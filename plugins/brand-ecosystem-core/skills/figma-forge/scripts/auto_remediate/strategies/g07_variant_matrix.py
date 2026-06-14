"""G07 — Variant matrix Cartesian product auto-calculator strategy.

When the publish_audit G07 gate reports a mismatch between the
``variants.expected_count`` value declared in a component spec and the
actual Cartesian product of the spec's variant axes, this strategy:

1. Loads every component spec under ``components/``
2. Computes ``expected = product(len(axis_values) for axis_values in axes.values())``
3. Subtracts any ``disabled_combinations`` length declared on the spec
4. Compares against the spec's stored ``expected_count`` (if any)
5. Proposes a patch to align the stored value with the computed one,
   or to add the field when missing

Empirically derived from the Düstur build experience where 17 component
specs were validated via ad-hoc Python loop. Düstur's Yüzey Badge had
7 tier × 3 variant × 3 size = 63 variants — exactly the value the
strategy now computes deterministically.

The strategy is purely arithmetic and runs entirely on static specs;
it does not depend on a live Figma file.
"""

from __future__ import annotations

import json
import re
from functools import reduce
from operator import mul
from pathlib import Path
from typing import Sequence

from ..base import (
    Channel,
    GateFailure,
    RemediationAction,
    RemediationContext,
    RemediationStrategy,
    UnsupportedChannelError,
    register_strategy,
)


@register_strategy(gate_id=7)
class VariantMatrixCalculatorStrategy(RemediationStrategy):
    """Compute and write the correct ``expected_count`` for every component spec."""

    title = "Variant matrix Cartesian product calculator"
    output_channels = ("pr",)

    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        components_dir = ctx.library_dir / "components"
        if not components_dir.exists():
            return []

        actions: list[RemediationAction] = []
        for spec_path in sorted(components_dir.glob("*.json")):
            rel = str(spec_path.relative_to(ctx.library_dir))
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue  # Invalid JSON is G04 / pre-publish-lint territory

            variants_block = spec.get("variants")
            if not isinstance(variants_block, dict):
                continue

            axes = variants_block.get("axes")
            if not isinstance(axes, dict) or not axes:
                continue

            computed = self._compute_expected_count(axes, variants_block)
            stored = variants_block.get("expected_count")

            if stored == computed:
                continue  # Already correct

            # Patch the spec's expected_count
            new_spec = self._patch_expected_count(spec, computed)
            new_json = json.dumps(new_spec, indent=2, ensure_ascii=False) + "\n"
            original = spec_path.read_text(encoding="utf-8")

            comp_name = spec.get("component", {}).get("name", spec_path.stem)
            axes_summary = " × ".join(
                f"{len(v)} {axis_name.lower()}" for axis_name, v in axes.items() if isinstance(v, list)
            )
            disabled_n = len(variants_block.get("disabled_combinations") or [])
            adj = f" − {disabled_n} disabled" if disabled_n else ""

            rationale = (
                f"Auto-compute variants.expected_count for component {comp_name!r}: "
                f"{axes_summary}{adj} = {computed}. "
                f"Previous stored value: {stored!r} (was {'absent' if stored is None else 'stale'}). "
                f"This patch keeps the spec a single source of truth — publish_audit G07 verifies "
                f"the live Figma component set count against this value, and a mismatch fails the gate."
            )

            actions.append(
                RemediationAction(
                    strategy_id=7,
                    action_type="patch_file",
                    target_path=rel,
                    rationale=rationale,
                    old_content=original,
                    new_content=new_json,
                    confidence="high",
                )
            )

        return actions

    def render(self, action: RemediationAction, channel: Channel) -> str:
        if channel != "pr":
            raise UnsupportedChannelError(
                f"G07 strategy only supports PR channel (requested: {channel!r})"
            )
        return _render_unified_diff(
            target=action.target_path,
            old=action.old_content or "",
            new=action.new_content or "",
            rationale=action.rationale,
        )

    # ------------------------------------------------------------------
    # Arithmetic helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_expected_count(axes: dict, variants_block: dict) -> int:
        """Cartesian product of axis lengths, minus disabled combinations."""
        axis_lengths = []
        for axis_name, axis_values in axes.items():
            if isinstance(axis_values, list):
                axis_lengths.append(max(1, len(axis_values)))
        if not axis_lengths:
            return 0
        product = reduce(mul, axis_lengths, 1)
        disabled = variants_block.get("disabled_combinations") or []
        return product - len(disabled)

    @staticmethod
    def _patch_expected_count(spec: dict, computed: int) -> dict:
        """Return a deep-copy of the spec with ``variants.expected_count`` set
        to ``computed``. Preserves dict ordering and other fields."""
        import copy

        new_spec = copy.deepcopy(spec)
        variants_block = new_spec.setdefault("variants", {})
        variants_block["expected_count"] = computed
        return new_spec


def _render_unified_diff(*, target: str, old: str, new: str, rationale: str) -> str:
    import difflib
    diff_lines = list(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{target}",
            tofile=f"b/{target}",
            n=3,
        )
    )
    rationale_block = "\n".join(f"# {line}" for line in rationale.splitlines())
    return f"{rationale_block}\n{''.join(diff_lines)}"
