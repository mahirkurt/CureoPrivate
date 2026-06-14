"""G02 — Composite typography → text styles routing strategy.

When the publish_audit G02 gate reports composite typography tokens
(``$type: typography``) that are mistakenly emitted into the Figma
Variables payload, this strategy:

1. Scans the merged DTCG document for composite typography tokens
2. Builds a separate ``text-styles.json`` payload (one entry per role)
3. Strips the composite tokens from the Variables payload
4. Generates two patches: amended Variables payload + new text-styles file

Empirically derived from the Düstur build experience where 12 composite
typography roles (display, section, body, code, eli-uri, ...) were
manually rerouted because Figma Variables API cannot hold composite
types — only atomic values (color, dimension, number, string, boolean).

The text-styles JSON is consumed by the v0.4.0 plugin channel which
calls ``figma.createTextStyle()`` for each entry; v0.3.0 emits the JSON
as a static artifact ready for any downstream Plugin TS writer.
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


@register_strategy(gate_id=2)
class CompositeTypographyRoutingStrategy(RemediationStrategy):
    """Route composite typography tokens out of Variables, into text-styles."""

    title = "Composite typography → text-styles router"
    output_channels = ("pr", "plugin")

    # DTCG composite type identifiers — Figma Variables cannot hold these
    COMPOSITE_TYPES = frozenset({"typography", "border", "shadow", "transition", "gradient"})

    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        merged_rel = failure.details.get("merged_dtcg", "tokens/dustur.tokens.json")
        merged_full = ctx.library_dir / merged_rel

        if not merged_full.exists():
            return []

        tokens = ctx.read_json(merged_rel)
        composites = list(_collect_composite_tokens(tokens, ctx))

        if not composites:
            return []

        # Build text-styles.json payload (Figma-plugin-friendly format)
        text_styles = self._build_text_styles_payload(composites)
        text_styles_rel = self._infer_text_styles_path(merged_rel)
        text_styles_full = ctx.library_dir / text_styles_rel
        text_styles_existed = text_styles_full.exists()

        # Strip composite tokens from the merged DTCG (they belong in text-styles, not Variables)
        amended_tokens = _strip_composites_from_tree(tokens, self.COMPOSITE_TYPES)
        amended_json = json.dumps(amended_tokens, indent=2, ensure_ascii=False) + "\n"
        original_json = merged_full.read_text(encoding="utf-8")

        # Use the same indent/newline conventions for the text-styles payload
        text_styles_json = json.dumps(text_styles, indent=2, ensure_ascii=False) + "\n"

        rationale_amend = (
            f"Strip {len(composites)} composite typography token(s) from the merged DTCG. "
            f"Figma Variables API only accepts atomic types (color/dimension/number/string/boolean); "
            f"composite typography roles must live in a separate Text Styles payload that is consumed "
            f"by the plugin channel (figma.createTextStyle). Without this split, dtcg_to_variables "
            f"silently drops the composites and the Variables import produces incomplete coverage."
        )

        rationale_create = (
            f"Create {text_styles_rel} from {len(composites)} composite typography role(s). "
            f"Each entry carries fontFamily / fontSize / lineHeight / letterSpacing / fontWeight "
            f"in Figma-plugin native shape. The companion patch removes these from the main "
            f"DTCG so the Variables import remains schema-valid."
        )

        actions = [
            RemediationAction(
                strategy_id=2,
                action_type="patch_file",
                target_path=merged_rel,
                rationale=rationale_amend,
                old_content=original_json,
                new_content=amended_json,
                confidence="high",
            ),
        ]

        if text_styles_existed:
            existing = text_styles_full.read_text(encoding="utf-8")
            if existing.strip() != text_styles_json.strip():
                actions.append(
                    RemediationAction(
                        strategy_id=2,
                        action_type="patch_file",
                        target_path=text_styles_rel,
                        rationale=(
                            "Update existing text-styles payload to reflect newly-extracted "
                            "composite roles. Operator should diff against any local modifications "
                            "before merging."
                        ),
                        old_content=existing,
                        new_content=text_styles_json,
                        confidence="medium",
                    )
                )
        else:
            actions.append(
                RemediationAction(
                    strategy_id=2,
                    action_type="create_file",
                    target_path=text_styles_rel,
                    rationale=rationale_create,
                    new_content=text_styles_json,
                    confidence="high",
                )
            )

        return actions

    def render(self, action: RemediationAction, channel: Channel) -> str:
        if channel not in self.output_channels:
            raise UnsupportedChannelError(
                f"G02 strategy does not support channel {channel!r} "
                f"(available: {self.output_channels})"
            )

        if channel == "pr":
            if action.action_type == "create_file":
                return _render_create_file_diff(
                    target=action.target_path,
                    content=action.new_content or "",
                    rationale=action.rationale,
                )
            return _render_unified_diff(
                target=action.target_path,
                old=action.old_content or "",
                new=action.new_content or "",
                rationale=action.rationale,
            )

        # plugin channel: emit a TypeScript snippet that creates Text Styles
        if action.action_type == "create_file" and action.target_path.endswith("text-styles.json"):
            return _render_plugin_text_styles(action)
        # Other actions don't have a meaningful plugin representation
        return _render_plugin_noop(action, reason="amend-only DTCG patch, no live Figma op")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _infer_text_styles_path(merged_rel: str) -> str:
        """Derive ``tokens/<ds-name>.text-styles.json`` from the merged DTCG path."""
        p = Path(merged_rel)
        # If the source is "tokens/dustur.tokens.json", produce "tokens/dustur.text-styles.json"
        if p.name.endswith(".tokens.json"):
            new_name = p.name.replace(".tokens.json", ".text-styles.json")
            return str(p.parent / new_name)
        # Fallback: drop the suffix and append .text-styles.json
        return str(p.parent / (p.stem + ".text-styles.json"))

    @staticmethod
    def _build_text_styles_payload(composites: list[dict]) -> dict:
        """Convert a list of composite typography tokens into a plugin-ready
        payload keyed by canonical role name (e.g. ``display``, ``body``)."""
        text_styles: dict[str, dict] = {}
        for entry in composites:
            role = entry["role"]
            value = entry["value"]
            text_styles[role] = {
                "role": role,
                "dtcg_path": entry["path"],
                "fontFamily": value.get("fontFamily"),
                "fontWeight": value.get("fontWeight"),
                "fontSize": value.get("fontSize"),
                "lineHeight": value.get("lineHeight"),
                "letterSpacing": value.get("letterSpacing"),
                "textCase": value.get("textCase"),
                "textDecoration": value.get("textDecoration"),
            }
        return {
            "$schema": "https://raw.githubusercontent.com/mahirkurt/figma-forge/main/schemas/text-styles.schema.json",
            "_generated_by": "figma-forge auto-remediate v0.3.0 (G02 strategy)",
            "text_styles": text_styles,
        }


def _collect_composite_tokens(tree, ctx: RemediationContext, prefix: str = ""):
    """Yield every leaf token whose ``$type`` is in the composite set."""
    if isinstance(tree, dict):
        if "$value" in tree:
            t = tree.get("$type")
            if t in CompositeTypographyRoutingStrategy.COMPOSITE_TYPES:
                yield {
                    "path": prefix,
                    "role": prefix.rsplit(".", 1)[-1],
                    "type": t,
                    "value": tree["$value"] if isinstance(tree["$value"], dict) else {"raw": tree["$value"]},
                }
        else:
            for k, v in tree.items():
                if k.startswith("$"):
                    continue
                p = f"{prefix}.{k}" if prefix else k
                yield from _collect_composite_tokens(v, ctx, p)


def _strip_composites_from_tree(tree, composite_types: frozenset):
    """Return a deep copy of ``tree`` with every composite-type leaf removed."""
    if isinstance(tree, dict):
        if "$value" in tree and tree.get("$type") in composite_types:
            return None
        out = {}
        for k, v in tree.items():
            stripped = _strip_composites_from_tree(v, composite_types) if not k.startswith("$") else v
            if stripped is not None:
                out[k] = stripped
        return out
    if isinstance(tree, list):
        return [x for x in (_strip_composites_from_tree(item, composite_types) for item in tree) if x is not None]
    return tree


# ---------------------------------------------------------------------------
# Channel renderers
# ---------------------------------------------------------------------------

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


def _render_create_file_diff(*, target: str, content: str, rationale: str) -> str:
    rationale_block = "\n".join(f"# {line}" for line in rationale.splitlines())
    lines = content.splitlines()
    diff_added = "\n".join(f"+{line}" for line in lines)
    diff_body = (
        f"--- /dev/null\n"
        f"+++ b/{target}\n"
        f"@@ -0,0 +1,{len(lines)} @@\n"
        f"{diff_added}\n"
    )
    return f"{rationale_block}\n{diff_body}"


def _render_plugin_text_styles(action: RemediationAction) -> str:
    """Emit a Figma plugin TypeScript snippet that creates Text Styles
    from the JSON payload."""
    payload = json.loads(action.new_content or "{}")
    styles = payload.get("text_styles", {})
    lines = [
        "// figma-forge auto-remediate v0.3.0 — G02 (Composite typography → Text Styles)",
        f"// Source DTCG: {payload.get('_generated_by', 'unknown')}",
        "// Run from Figma → Plugins → Development → Open Console → paste:",
        "",
        "(async () => {",
        f"  console.log('Creating {len(styles)} text style(s)...');",
    ]
    for role, spec in styles.items():
        safe_role = role.replace("'", "\\'")
        font_family = (spec.get("fontFamily") or "Inter").replace("'", "\\'")
        font_weight = spec.get("fontWeight") or "Regular"
        font_size = spec.get("fontSize") or 16
        line_height_raw = spec.get("lineHeight")
        letter_spacing = spec.get("letterSpacing") or 0

        lines.append(f"  // Role: {role}")
        lines.append("  {")
        lines.append(f"    const style = figma.createTextStyle();")
        lines.append(f"    style.name = '{safe_role}';")
        lines.append(f"    await figma.loadFontAsync({{ family: '{font_family}', style: '{font_weight}' }});")
        lines.append(f"    style.fontName = {{ family: '{font_family}', style: '{font_weight}' }};")
        lines.append(f"    style.fontSize = {_to_number(font_size)};")
        if line_height_raw:
            line_height_value = _coerce_line_height(line_height_raw)
            lines.append(f"    style.lineHeight = {line_height_value};")
        lines.append(f"    style.letterSpacing = {{ unit: 'PIXELS', value: {_to_number(letter_spacing)} }};")
        lines.append("  }")
    lines.append("  console.log('Text styles created.');")
    lines.append("})();")
    return "\n".join(lines) + "\n"


def _render_plugin_noop(action: RemediationAction, *, reason: str) -> str:
    rationale_block = "\n".join(f"// {line}" for line in action.rationale.splitlines())
    return (
        f"{rationale_block}\n"
        f"// NO-OP: {reason}\n"
        f"// Target path: {action.target_path}\n"
        f"// The PR channel patch handles this action; no Figma live mutation needed.\n"
    )


def _to_number(v) -> str:
    """Render a DTCG dimension/number value as a JS literal."""
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        # strip 'px' suffix; parse percentage as fraction
        s = v.strip().lower()
        if s.endswith("px"):
            return s[:-2]
        try:
            return str(float(s))
        except ValueError:
            return "16"
    return "16"


def _coerce_line_height(raw) -> str:
    """Render a DTCG line-height value (number, %, px) as Figma LineHeight JSON."""
    if isinstance(raw, (int, float)):
        # Unit-less ratio (e.g. 1.4) → percent of font-size
        return f"{{ unit: 'PERCENT', value: {raw * 100} }}"
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s.endswith("%"):
            try:
                return f"{{ unit: 'PERCENT', value: {float(s[:-1])} }}"
            except ValueError:
                pass
        if s.endswith("px"):
            return f"{{ unit: 'PIXELS', value: {s[:-2]} }}"
        try:
            return f"{{ unit: 'PERCENT', value: {float(s) * 100} }}"
        except ValueError:
            pass
    return "{ unit: 'AUTO' }"
