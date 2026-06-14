"""orchestration.json manifest parser.

The manifest schema (v1.0, frozen in v0.3.0 GA) declares a pipeline as
an ordered list of stage objects. Each stage carries: ``stage`` (1-indexed
integer), ``mode`` (canonical executor name), ``description``,
``command`` (informational string), and optional fields ``outputs``,
``estimated_time``, ``pass_criteria``.

The parser validates required fields, normalizes the stage list into
:class:`StageSpec` instances, and surfaces field-level errors with the
JSONPath that triggered the failure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import StageSpec


class ManifestError(ValueError):
    """Raised when the manifest fails validation."""


REQUIRED_STAGE_FIELDS = {"stage", "mode"}
ALLOWED_MODES = {
    "SCAFFOLD",
    "TOKENS_IMPORT",
    "FOUNDATIONS_BUILD",
    "COMPONENTS_BUILD",
    "ICONS_BUILD",
    "PATTERNS_BUILD",
    "CODE_CONNECT",
    "PUBLISH_AUDIT",
    "PUBLISH",
    "AUTO_REMEDIATE",
}


def parse_manifest(path: Path) -> tuple[dict, list[StageSpec]]:
    """Parse ``orchestration.json`` and return ``(top_level, [StageSpec])``.

    The returned tuple's first element preserves manifest-level metadata
    (``library``, ``version``, ``channel_preference``, etc.) for the
    runner's logging. The second element is the validated, ordered
    stage list.
    """
    if not path.exists():
        raise ManifestError(f"Manifest not found: {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ManifestError(f"Invalid JSON in {path}: {e}") from e

    if not isinstance(raw, dict):
        raise ManifestError("Manifest top-level must be an object")

    pipeline = raw.get("pipeline")
    if not isinstance(pipeline, list) or not pipeline:
        raise ManifestError("Manifest must contain a non-empty 'pipeline' array")

    specs: list[StageSpec] = []
    for i, stage_raw in enumerate(pipeline):
        if not isinstance(stage_raw, dict):
            raise ManifestError(f"pipeline[{i}] must be an object")

        missing = REQUIRED_STAGE_FIELDS - set(stage_raw.keys())
        if missing:
            raise ManifestError(
                f"pipeline[{i}] missing required field(s): {sorted(missing)}"
            )

        mode = stage_raw["mode"]
        if mode not in ALLOWED_MODES:
            raise ManifestError(
                f"pipeline[{i}].mode = {mode!r} is not one of "
                f"{sorted(ALLOWED_MODES)}"
            )

        try:
            stage_index = int(stage_raw["stage"])
        except (TypeError, ValueError) as e:
            raise ManifestError(
                f"pipeline[{i}].stage must be an integer (got {stage_raw['stage']!r})"
            ) from e

        outputs = stage_raw.get("outputs", [])
        if outputs and not isinstance(outputs, list):
            raise ManifestError(f"pipeline[{i}].outputs must be a list")

        specs.append(StageSpec(
            index=stage_index,
            mode=mode,
            description=stage_raw.get("description", ""),
            command=stage_raw.get("command"),
            outputs=list(outputs),
            estimated_time=stage_raw.get("estimated_time"),
            pass_criteria=stage_raw.get("pass_criteria"),
            raw=stage_raw,
        ))

    # Reject duplicate stage indices
    indices = [s.index for s in specs]
    if len(indices) != len(set(indices)):
        raise ManifestError(
            f"Duplicate stage indices in pipeline: {indices}"
        )

    # Sort by declared index (manifest order should already match,
    # but enforce determinism in case of human typos)
    specs.sort(key=lambda s: s.index)

    return raw, specs
