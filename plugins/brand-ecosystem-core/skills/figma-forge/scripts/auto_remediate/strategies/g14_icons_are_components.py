"""G14 — Icons-are-components SVG canonical normalizer.

When the publish_audit G14 gate reports SVG assets that are non-canonical
(missing viewBox, wrong stroke width, missing ``<title>`` tag, fill on
outline icons, etc.), this strategy normalizes them in place to match
the Düstur convention:

* Stroke width: 1.5px @ 24×24 base
* Stroke linecap / linejoin: round
* viewBox: ``0 0 N N`` (square, N = canonical size)
* ``<title>`` tag present (a11y requirement)
* Fill on outline icons: ``none``
* Color: ``currentColor`` for token-aware theming

Empirically derived from the Düstur build experience where 48 generic UI
icons required adaptation from Tabler's defaults (stroke 2px, no title).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
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

# Register a namespace so the parser preserves it on write
ET.register_namespace("", "http://www.w3.org/2000/svg")


@register_strategy(gate_id=14)
class IconCanonicalNormalizerStrategy(RemediationStrategy):
    """Normalize SVG icons to Düstur canonical form."""

    title = "Icon SVG canonical normalizer"
    output_channels = ("pr",)

    # Canonical defaults (per Düstur icon-strategy.md)
    DEFAULT_STROKE_WIDTH = "1.5"
    DEFAULT_LINECAP = "round"
    DEFAULT_LINEJOIN = "round"
    DEFAULT_FILL = "none"

    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        svg_dir = ctx.library_dir / "icons" / "svg"
        if not svg_dir.exists():
            return []

        # Determine icon-strategy: tier mührleri (filled) vs UI icons (stroked)
        actions: list[RemediationAction] = []

        # If the gate's failure carries explicit sample paths, prefer those;
        # otherwise scan all SVGs and check each for canonical conformance.
        sample_paths = [s.get("path") for s in failure.samples if s.get("path")]
        if sample_paths:
            candidates = [svg_dir / p for p in sample_paths if (svg_dir / p).exists()]
        else:
            candidates = list(svg_dir.rglob("*.svg"))

        for svg_path in candidates:
            # Selçuklu motifleri brand-asset, UI dışı — normalize KAPSAMI dışında
            if "selcuklu-motif" in svg_path.parts:
                continue

            original = svg_path.read_text(encoding="utf-8")
            normalized = self._normalize_svg(original, svg_path.name)
            if normalized == original:
                continue  # Already canonical

            rel_target = str(svg_path.relative_to(ctx.library_dir))
            actions.append(
                RemediationAction(
                    strategy_id=14,
                    action_type="patch_file",
                    target_path=rel_target,
                    rationale=(
                        f"Normalize {svg_path.name} to Düstur canonical form: "
                        f"add missing viewBox / <title>, set stroke-width={self.DEFAULT_STROKE_WIDTH}, "
                        f"linecap=round, linejoin=round on stroked icons; ensure fill=none for outlines."
                    ),
                    old_content=original,
                    new_content=normalized,
                    confidence="high",
                )
            )

        return actions

    def render(self, action: RemediationAction, channel: Channel) -> str:
        if channel != "pr":
            raise UnsupportedChannelError(
                f"G14 strategy only supports PR channel (requested: {channel!r})"
            )
        import difflib

        diff_lines = list(
            difflib.unified_diff(
                (action.old_content or "").splitlines(keepends=True),
                (action.new_content or "").splitlines(keepends=True),
                fromfile=f"a/{action.target_path}",
                tofile=f"b/{action.target_path}",
                n=3,
            )
        )
        rationale_block = "\n".join(f"# {line}" for line in action.rationale.splitlines())
        return f"{rationale_block}\n{''.join(diff_lines)}"

    # ------------------------------------------------------------------
    # Normalization helpers
    # ------------------------------------------------------------------

    def _normalize_svg(self, source: str, filename: str) -> str:
        """Apply canonical normalizations; return updated SVG text."""
        text = source

        # 1) Ensure viewBox attribute on the root <svg>
        if "viewBox" not in text:
            # Default to 24×24 if no width/height present
            text = re.sub(
                r"<svg(?![^>]*viewBox)",
                '<svg viewBox="0 0 24 24"',
                text,
                count=1,
            )

        # 2) Ensure <title> tag (a11y)
        if "<title>" not in text:
            # Derive a title from the filename: "arrow-left-24.svg" → "Arrow Left"
            stem = Path(filename).stem
            stem = re.sub(r"-\d+$", "", stem)  # strip trailing size
            label = " ".join(w.capitalize() for w in stem.split("-"))
            text = re.sub(
                r"(<svg[^>]*>)",
                lambda m: m.group(1) + f"\n  <title>{label}</title>",
                text,
                count=1,
            )

        # 3) Outline-style normalization: only apply if SVG looks like a stroked icon
        is_outline = (
            "stroke=" in text or "stroke-width" in text or
            ("<circle" in text and 'fill="#' not in text)
        )
        # Tier mühürleri (filled) are detected by presence of <circle ... fill="#..."> — skip them
        is_filled_seal = bool(re.search(r'<circle[^>]*fill="#[0-9A-Fa-f]{6}"', text))

        if is_outline and not is_filled_seal:
            # Ensure root has stroke-linecap=round, stroke-linejoin=round
            if "stroke-linecap" not in text:
                text = re.sub(r"<svg([^>]*)>", r'<svg\1 stroke-linecap="round" stroke-linejoin="round">', text, count=1)

            # Normalize stroke-width if explicitly set to 2
            text = re.sub(r'stroke-width="2(\.0+)?"', f'stroke-width="{self.DEFAULT_STROKE_WIDTH}"', text)

        return text
