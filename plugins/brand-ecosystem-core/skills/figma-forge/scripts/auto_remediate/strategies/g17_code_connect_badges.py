"""G17 — Code Connect mapping generator strategy.

When the publish_audit G17 gate reports components without a Code
Connect mapping, this strategy generates JSON template files in the
``code-connect/`` directory by reading the corresponding component spec
and synthesizing React + Web Components + CSS class snippets.

The generated templates follow the Düstur convention:

* React: ``import { <Carbon> } from '<pkg>/react';`` + JSX example with
  full prop schema derived from ``variants.axes``
* Web Components: ``tcm-<id>`` custom-tag pattern + attribute schema
* CSS: class-name pattern integrated with the design-system stylesheet

Empirically derived from the Düstur build experience where 17 Code
Connect mappings were authored manually in a Python loop.
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


@register_strategy(gate_id=17)
class CodeConnectMappingStrategy(RemediationStrategy):
    """Generate missing Code Connect mapping JSON files from component specs."""

    title = "Code Connect mapping generator"
    output_channels = ("pr",)

    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        components_dir = ctx.library_dir / "components"
        code_connect_dir = ctx.library_dir / "code-connect"

        if not components_dir.exists():
            return []

        # Read library-registry to determine the npm package name (Düstur default: @dustur)
        registry = self._safe_load_registry(ctx)
        ds_name = registry.get("ds_name", "Design System") if registry else "Design System"
        pkg_root = self._infer_package_root(ds_name)

        existing_mappings = {p.stem for p in code_connect_dir.glob("*.json")} if code_connect_dir.exists() else set()

        actions: list[RemediationAction] = []
        for spec_path in sorted(components_dir.glob("*.json")):
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            comp = spec.get("component", {})
            comp_id = self._component_id(spec_path.stem)
            if comp_id in existing_mappings:
                continue  # Mapping already present; do not overwrite

            mapping_json = self._synthesize_mapping(comp, comp_id, pkg_root, spec)
            rel_target = f"code-connect/{comp_id}.json"

            actions.append(
                RemediationAction(
                    strategy_id=17,
                    action_type="create_file",
                    target_path=rel_target,
                    rationale=(
                        f"Generate Code Connect mapping for component {comp.get('name', comp_id)!r}. "
                        f"Derived from {spec_path.name}; produces React + Web Components + CSS class "
                        f"snippet templates. Operator should review prop types and example JSX before merging."
                    ),
                    new_content=json.dumps(mapping_json, indent=2, ensure_ascii=False) + "\n",
                    confidence="high",
                )
            )

        return actions

    def render(self, action: RemediationAction, channel: Channel) -> str:
        if channel != "pr":
            raise UnsupportedChannelError(
                f"G17 strategy only supports PR channel (requested: {channel!r})"
            )
        # For create_file actions we synthesize an "all-add" unified diff
        # so it applies cleanly via `git apply`.
        return _render_create_file_diff(
            target=action.target_path,
            content=action.new_content or "",
            rationale=action.rationale,
        )

    # ------------------------------------------------------------------
    # Synthesis helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _component_id(spec_stem: str) -> str:
        # "01-yuzey-badge" → "yuzey-badge"
        return re.sub(r"^\d+-", "", spec_stem)

    @staticmethod
    def _safe_load_registry(ctx: RemediationContext) -> dict | None:
        reg = ctx.library_dir / "library-registry.json"
        if reg.exists():
            return json.loads(reg.read_text(encoding="utf-8"))
        return None

    @staticmethod
    def _infer_package_root(ds_name: str) -> str:
        # "Düstur Tasarım Sistemi" → "@dustur"
        first = ds_name.split()[0].lower()
        # Strip Turkish diacritics for npm scope (npm scopes are ASCII)
        translation = str.maketrans({"ü": "u", "ö": "o", "ı": "i", "ş": "s", "ğ": "g", "ç": "c"})
        return "@" + first.translate(translation)

    @staticmethod
    def _synthesize_mapping(comp: dict, comp_id: str, pkg_root: str, spec: dict) -> dict:
        carbon = comp.get("name_carbon") or _to_pascal(comp_id)
        axes = spec.get("variants", {}).get("axes", {})

        # Synthesize React prop schema
        react_props: dict = {}
        for axis_name, axis_values in axes.items():
            if isinstance(axis_values, list) and axis_values:
                key = axis_name.lower()
                react_props[key] = {
                    "type": "enum",
                    "values": [str(v).lower() for v in axis_values],
                    "figma_axis": axis_name,
                }

        # Render JSX example using lowercase axis values
        jsx_props = " ".join(f"{k}={{ {k} }}" for k in react_props)
        react_example = f"<{carbon} {jsx_props}>{{children}}</{carbon}>" if react_props else f"<{carbon} />"

        # Web Components
        wc_tag = f"tcm-{comp_id}"
        attrs = {k: f"{' | '.join(v['values'])}" for k, v in react_props.items()}
        attr_str = " ".join(f'{k}="{v["values"][0]}"' for k, v in react_props.items())
        wc_example = f'<{wc_tag} {attr_str}></{wc_tag}>' if react_props else f"<{wc_tag}></{wc_tag}>"

        return {
            "$schema": "https://raw.githubusercontent.com/mahirkurt/figma-forge/main/schemas/code-connect.schema.json",
            "component_id": comp_id,
            "figma_component_name": comp.get("name", carbon),
            "carbon_class_name": carbon,
            "_generated_by": "figma-forge auto-remediate v0.3.0 (G17 strategy)",
            "_review_required": True,
            "react": {
                "import_statement": f"import {{ {carbon} }} from '{pkg_root}/react';",
                "code_example": react_example,
                "props": react_props,
            },
            "web_components": {
                "tag_name": wc_tag,
                "import_statement": f"import '{pkg_root}/web-components/{comp_id}';",
                "code_example": wc_example,
                "attributes": attrs,
            },
            "css_class_pattern": f".{comp_id} (uses CSS Custom Properties from {pkg_root}/tasarim-sistemi)",
        }


def _to_pascal(s: str) -> str:
    return "".join(w.capitalize() for w in re.split(r"[-_\s]+", s))


def _render_create_file_diff(*, target: str, content: str, rationale: str) -> str:
    """Format a unified diff for a brand-new file."""
    rationale_block = "\n".join(f"# {line}" for line in rationale.splitlines())
    lines = content.splitlines()
    # Each content line becomes "+<line>" in the diff
    diff_added = "\n".join(f"+{line}" for line in lines)
    diff_body = (
        f"--- /dev/null\n"
        f"+++ b/{target}\n"
        f"@@ -0,0 +1,{len(lines)} @@\n"
        f"{diff_added}\n"
    )
    return f"{rationale_block}\n{diff_body}"
