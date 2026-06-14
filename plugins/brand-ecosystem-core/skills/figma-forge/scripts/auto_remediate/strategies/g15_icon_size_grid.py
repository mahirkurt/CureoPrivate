"""G15 — Icon size grid normalizer strategy.

When the publish_audit G15 gate (or static-lint L6) reports SVG icons
whose dimensions deviate from the canonical size grid declared in
``library-registry.icon_size_grid``, this strategy:

1. Loads each ``icons/svg/<tier>/*.svg`` file
2. Parses its ``viewBox`` attribute and any ``width`` / ``height``
   attributes
3. Determines the canonical target size by category:
   - ``icons/svg/`` (generic UI) — canonical sizes: {16, 20, 24}
   - ``icons/svg/tier/`` — canonical sizes: {24, 48}
   - ``icons/svg/selcuklu-motif/`` — canonical sizes: {48, 96, 192}
   - ``icons/svg/document/`` (legal symbols) — canonical sizes: {32, 48}
4. Snaps the icon to the nearest canonical size by:
   - Computing the natural aspect-preserving viewBox cube
   - Setting ``width=height=<target>``
   - Preserving the original ``viewBox`` so the rendered geometry is
     untouched — only the grid alignment changes
5. Emits a unified-diff patch per affected SVG file

Empirically derived from the Düstur build experience where 14 tier icons
needed a 24px adapter while 6 Selçuklu motifs were locked to 192px. The
heuristic gracefully handles cases where the icon's original cube is
non-square (e.g. 16×24 banner-tier marks) — it preserves the original
aspect ratio and snaps the dominant axis only.
"""

from __future__ import annotations

import json
import re
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

# Default canonical grids by tier — override via library-registry.icon_size_grid
DEFAULT_GRID_BY_DIR = {
    "icons/svg/tier/":           [24, 48],
    "icons/svg/selcuklu-motif/": [48, 96, 192],
    "icons/svg/document/":       [32, 48],
    "icons/svg/":                [16, 20, 24],  # Generic UI fallback (most specific later)
}

_VIEWBOX_RE = re.compile(r"viewBox=[\"']([^\"']+)[\"']")
_WIDTH_RE = re.compile(r"\swidth=[\"']([^\"']+)[\"']")
_HEIGHT_RE = re.compile(r"\sheight=[\"']([^\"']+)[\"']")


@register_strategy(gate_id=15)
class IconSizeGridStrategy(RemediationStrategy):
    """Snap SVG icon dimensions to the nearest canonical size grid value."""

    title = "Icon size grid normalizer"
    output_channels = ("pr",)

    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        svg_dir = ctx.library_dir / "icons" / "svg"
        if not svg_dir.exists():
            return []

        # Load registry-level grid overrides if present
        grid_by_dir = dict(DEFAULT_GRID_BY_DIR)
        reg_path = ctx.library_dir / "library-registry.json"
        if reg_path.exists():
            try:
                reg = json.loads(reg_path.read_text(encoding="utf-8"))
                overrides = reg.get("icon_size_grid", {})
                if isinstance(overrides, dict):
                    for prefix, sizes in overrides.items():
                        if isinstance(sizes, list) and all(isinstance(n, int) for n in sizes):
                            grid_by_dir[prefix] = sorted(sizes)
            except json.JSONDecodeError:
                pass

        actions: list[RemediationAction] = []
        for svg_path in sorted(svg_dir.rglob("*.svg")):
            rel = str(svg_path.relative_to(ctx.library_dir))
            original = svg_path.read_text(encoding="utf-8")

            grid = self._resolve_grid_for(rel, grid_by_dir)
            if grid is None:
                continue

            patched = self._normalize_svg(original, grid=grid)
            if patched is None or patched == original:
                continue  # Already on grid, or unparseable

            comment = self._derive_comment(rel, original, patched, grid)
            actions.append(
                RemediationAction(
                    strategy_id=15,
                    action_type="patch_file",
                    target_path=rel,
                    rationale=comment,
                    old_content=original,
                    new_content=patched,
                    confidence="high",
                )
            )

        return actions

    def render(self, action: RemediationAction, channel: Channel) -> str:
        if channel != "pr":
            raise UnsupportedChannelError(
                f"G15 strategy only supports PR channel (requested: {channel!r})"
            )
        return _render_unified_diff(
            target=action.target_path,
            old=action.old_content or "",
            new=action.new_content or "",
            rationale=action.rationale,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_grid_for(rel_path: str, grid_by_dir: dict[str, list[int]]) -> list[int] | None:
        """Return the most-specific grid match for ``rel_path``.

        Most specific = longest matching prefix. ``icons/svg/tier/`` wins
        over ``icons/svg/`` when both match.
        """
        best_prefix = None
        best_grid: list[int] | None = None
        for prefix, sizes in grid_by_dir.items():
            if rel_path.startswith(prefix):
                if best_prefix is None or len(prefix) > len(best_prefix):
                    best_prefix = prefix
                    best_grid = sizes
        return best_grid

    @staticmethod
    def _normalize_svg(svg_text: str, *, grid: list[int]) -> str | None:
        """Snap the svg's width/height to the nearest grid value.

        Returns the patched SVG text, or ``None`` if no parse succeeded.
        Preserves the original viewBox geometry; only width/height
        attributes are touched.
        """
        vb_match = _VIEWBOX_RE.search(svg_text)
        if not vb_match:
            return None
        try:
            parts = vb_match.group(1).split()
            if len(parts) != 4:
                return None
            vb_w = float(parts[2])
            vb_h = float(parts[3])
        except (ValueError, IndexError):
            return None

        # Pick the natural size as max(viewBox dimensions); snap to nearest grid value
        natural = max(vb_w, vb_h)
        target = _nearest_grid_value(natural, grid)
        if target is None:
            return None

        # Compute the aspect-preserving width/height
        if vb_w >= vb_h:
            new_w = target
            new_h = round(target * vb_h / vb_w)
        else:
            new_h = target
            new_w = round(target * vb_w / vb_h)

        # Replace or insert width/height attrs
        out = svg_text
        if _WIDTH_RE.search(out):
            out = _WIDTH_RE.sub(f' width="{new_w}"', out, count=1)
        else:
            out = out.replace("<svg ", f'<svg width="{new_w}" ', 1)

        if _HEIGHT_RE.search(out):
            out = _HEIGHT_RE.sub(f' height="{new_h}"', out, count=1)
        else:
            out = out.replace("<svg ", f'<svg height="{new_h}" ', 1)

        return out

    @staticmethod
    def _derive_comment(rel_path: str, old: str, new: str, grid: list[int]) -> str:
        m_old_w = _WIDTH_RE.search(old)
        m_old_h = _HEIGHT_RE.search(old)
        m_new_w = _WIDTH_RE.search(new)
        m_new_h = _HEIGHT_RE.search(new)
        old_dim = f"{m_old_w.group(1) if m_old_w else '?'}×{m_old_h.group(1) if m_old_h else '?'}"
        new_dim = f"{m_new_w.group(1) if m_new_w else '?'}×{m_new_h.group(1) if m_new_h else '?'}"
        return (
            f"Snap {rel_path} from {old_dim} to canonical grid {new_dim} "
            f"(grid: {grid}). viewBox preserved — only width/height attributes change, "
            f"so rendered geometry remains pixel-identical. Aligns the icon with the "
            f"declared library-registry.icon_size_grid for the icon's category, ensuring "
            f"consistent Figma component frame sizes across the tier."
        )


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def _nearest_grid_value(natural: float, grid: list[int]) -> int | None:
    """Return the grid value closest to ``natural``.

    Ties broken by **rounding up** — better to have a slightly larger
    icon container than to crop the icon when geometry is preserved.
    """
    if not grid:
        return None
    grid_sorted = sorted(grid)
    # Choose nearest; ties round up
    closest = grid_sorted[0]
    best_delta = abs(natural - closest)
    for g in grid_sorted[1:]:
        d = abs(natural - g)
        if d < best_delta or (d == best_delta and g > closest):
            best_delta = d
            closest = g
    return closest


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
