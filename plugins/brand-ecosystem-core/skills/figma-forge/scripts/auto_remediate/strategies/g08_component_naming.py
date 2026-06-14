"""G08 — Component naming PascalCase rewriter strategy.

When the publish_audit G08 gate reports a component whose ``name_carbon``
field violates the PascalCase canonical convention (snake_case,
kebab-case, camelCase, ALL_CAPS, etc.), this strategy:

1. Loads every component spec
2. Detects non-PascalCase ``name_carbon`` values via regex
3. Proposes the canonical PascalCase rewrite (preserves Turkish chars)
4. Patches both the spec's ``name_carbon`` field and any matching
   ``code-connect/<id>.json`` carbon_class_name field for consistency

The Carbon Design System canonical convention is PascalCase
("YuzeyBadge", "MaddeCard"), matching React component naming. The Düstur
build's 17 component specs all complied on first pass, but the strategy
guards against the common drift where contributors add components in
non-canonical naming during PR review cycles.

Diacritics are preserved: "yüzey-badge" → "YüzeyBadge" (NOT "YuzeyBadge")
unless the spec explicitly declares an ``_ascii_class_name`` override.
This matches the Düstur convention of keeping authoritative Turkish
names while exposing ASCII-safe aliases for npm scopes via G17.
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

# Matches a properly PascalCased identifier (incl. Turkish letters)
_PASCAL_RE = re.compile(r"^[A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğıöşü0-9]*$")


@register_strategy(gate_id=8)
class ComponentNamingRewriterStrategy(RemediationStrategy):
    """Rewrite non-canonical component class names to PascalCase."""

    title = "Component naming PascalCase rewriter"
    output_channels = ("pr",)

    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        components_dir = ctx.library_dir / "components"
        if not components_dir.exists():
            return []

        actions: list[RemediationAction] = []
        rename_map: dict[str, str] = {}  # old_name → new_name (for Code Connect sync)

        for spec_path in sorted(components_dir.glob("*.json")):
            rel = str(spec_path.relative_to(ctx.library_dir))
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue

            comp = spec.get("component", {})
            current = comp.get("name_carbon")
            if not current or not isinstance(current, str):
                continue

            if _PASCAL_RE.match(current):
                continue  # Already canonical

            new_name = _to_pascal_case(current)
            if new_name == current:
                continue  # Cannot derive a valid PascalCase form

            rename_map[current] = new_name
            comp["name_carbon"] = new_name

            new_json = json.dumps(spec, indent=2, ensure_ascii=False) + "\n"
            original = spec_path.read_text(encoding="utf-8")

            actions.append(
                RemediationAction(
                    strategy_id=8,
                    action_type="patch_file",
                    target_path=rel,
                    rationale=(
                        f"Rewrite component class name {current!r} → {new_name!r} (PascalCase). "
                        f"Carbon DS canonical convention; React component naming standard. "
                        f"Turkish diacritics preserved (use _ascii_class_name override for ASCII-safe "
                        f"npm scope aliases)."
                    ),
                    old_content=original,
                    new_content=new_json,
                    confidence="high",
                )
            )

        # Cascade renames to Code Connect mappings (G17's output)
        actions.extend(self._sync_code_connect(ctx, rename_map))

        return actions

    def render(self, action: RemediationAction, channel: Channel) -> str:
        if channel != "pr":
            raise UnsupportedChannelError(
                f"G08 strategy only supports PR channel (requested: {channel!r})"
            )
        return _render_unified_diff(
            target=action.target_path,
            old=action.old_content or "",
            new=action.new_content or "",
            rationale=action.rationale,
        )

    # ------------------------------------------------------------------
    # Cascade helpers
    # ------------------------------------------------------------------

    def _sync_code_connect(
        self, ctx: RemediationContext, rename_map: dict[str, str]
    ) -> list[RemediationAction]:
        """For each renamed component, propagate the rename to any matching
        Code Connect mapping JSON."""
        if not rename_map:
            return []
        code_connect_dir = ctx.library_dir / "code-connect"
        if not code_connect_dir.exists():
            return []

        actions: list[RemediationAction] = []
        for cc_path in sorted(code_connect_dir.glob("*.json")):
            rel = str(cc_path.relative_to(ctx.library_dir))
            try:
                mapping = json.loads(cc_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue

            current_cls = mapping.get("carbon_class_name")
            if current_cls not in rename_map:
                continue
            new_cls = rename_map[current_cls]
            mapping["carbon_class_name"] = new_cls

            # Update React import + JSX example
            react = mapping.get("react", {})
            if isinstance(react, dict):
                if isinstance(react.get("import_statement"), str):
                    react["import_statement"] = react["import_statement"].replace(current_cls, new_cls)
                if isinstance(react.get("code_example"), str):
                    react["code_example"] = react["code_example"].replace(current_cls, new_cls)

            new_json = json.dumps(mapping, indent=2, ensure_ascii=False) + "\n"
            original = cc_path.read_text(encoding="utf-8")
            if original == new_json:
                continue

            actions.append(
                RemediationAction(
                    strategy_id=8,
                    action_type="patch_file",
                    target_path=rel,
                    rationale=(
                        f"Cascade rename {current_cls!r} → {new_cls!r} into Code Connect mapping. "
                        f"Keeps spec + mapping in lockstep so G17 stays passing."
                    ),
                    old_content=original,
                    new_content=new_json,
                    confidence="high",
                )
            )

        return actions


def _to_pascal_case(s: str) -> str:
    """Convert any common identifier convention to PascalCase, preserving
    Turkish diacritics on letter positions."""
    if not s:
        return s
    # Split on any non-letter delimiter (underscore, hyphen, space, dot)
    parts = re.split(r"[-_\s.]+", s)
    if len(parts) == 1:
        # No delimiters — handle camelCase / ALL_CAPS / single word
        single = parts[0]
        if single.isupper() and len(single) > 1:
            # ALL_CAPS → titlecase
            return single.capitalize()
        if single[0].islower():
            return single[0].upper() + single[1:]
        return single
    return "".join(p[:1].upper() + p[1:] if p else "" for p in parts)


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
