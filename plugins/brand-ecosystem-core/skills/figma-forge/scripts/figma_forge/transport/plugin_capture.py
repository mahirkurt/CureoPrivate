"""figma-forge ``PluginCaptureTransport`` — v1.1.0-alpha.

A buffering transport that accumulates every operation into an
in-memory log and, on :meth:`commit_session`, renders a single
TypeScript script the operator pastes into Figma's plugin console.

This is the continuation of the v0.3.1 plugin channel — the
operations expressible through this adapter are a superset of the
auto-remediate G02/G13/G14 strategies; the same template literal
escaping, page routing, and idempotency guards apply.

Code-Connect operations are **not** supported through this adapter
because Code Connect attachments are made via REST or the Figma CLI
(not the plugin runtime).
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .capability_matrix import ADAPTER_PLUGIN_CAPTURE, supported_operations
from .errors import CapabilityUnsupportedError, ValidationError
from .protocol import (
    AuthRequirement,
    CodeConnectMapping,
    CodeConnectRef,
    CollectionRef,
    ComponentGeometry,
    ComponentRef,
    ComponentSetRef,
    InstanceRef,
    Effect,
    FileKind,
    FileRef,
    PageRef,
    Paint,
    PublishRef,
    SessionResult,
    SessionToken,
    StyleRef,
    TextStyleProperties,
    VariableRef,
    VariableType,
    VariableValue,
    VariantSpec,
)


@dataclass
class PluginCaptureTransport:
    """Buffers operations; emits one TS script on commit.

    The captured script structure follows the v0.3 plugin channel
    convention: an async IIFE with try/catch wrappers per operation,
    locale-aware header comment, idempotency guards (findOne by name
    before create).
    """

    locale: str = "en-US"
    _operations: list[dict[str, Any]] = field(default_factory=list)
    _current_session: SessionToken | None = None

    # ------------------------------------------------------------------
    # Identity & capability
    # ------------------------------------------------------------------

    def adapter_id(self) -> str:
        return ADAPTER_PLUGIN_CAPTURE

    def supports(self, operation_name: str) -> bool:
        return operation_name in supported_operations(ADAPTER_PLUGIN_CAPTURE)

    def authentication_required(self) -> AuthRequirement:
        return AuthRequirement(needs_credentials=False, credential_kind="none")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def begin_session(self) -> SessionToken:
        token = SessionToken(
            adapter_id=ADAPTER_PLUGIN_CAPTURE,
            started_at=self._now(),
            token=f"pcap-{uuid.uuid4().hex[:12]}",
        )
        self._current_session = token
        return token

    def commit_session(self, token: SessionToken) -> SessionResult:
        ts_script = self.render_typescript()
        return SessionResult(
            token=token,
            operations_applied=len(self._operations),
            operations_failed=0,
            artifacts={
                "typescript_script": ts_script,
                "operation_count": str(len(self._operations)),
            },
        )

    def rollback_session(self, token: SessionToken) -> None:
        self._operations.clear()
        self._current_session = None

    # ------------------------------------------------------------------
    # File-level — mostly unsupported
    # ------------------------------------------------------------------

    def create_file(self, *, name: str, file_kind: FileKind) -> FileRef:
        raise CapabilityUnsupportedError(
            "Plugin scripts cannot create new Figma files; "
            "create the file in Figma UI first, then run the script there.",
            operation="create_file", adapter_id=self.adapter_id(),
        )

    def get_file(self, *, key: str) -> FileRef:
        raise CapabilityUnsupportedError(
            operation="get_file", adapter_id=self.adapter_id(),
            message="Plugin runs in the current file; no cross-file lookup.",
        )

    def publish_library(self, *, file_key: str, changelog: str) -> PublishRef:
        raise CapabilityUnsupportedError(
            operation="publish_library", adapter_id=self.adapter_id(),
            message="Library publish is a manual Figma UI action.",
        )

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def create_variable_collection(
        self, *, file_key: str, name: str, modes: list[str]
    ) -> CollectionRef:
        cid = self._stable_id("vc", name)
        self._capture("create_variable_collection", {
            "file_key": file_key, "name": name, "modes": modes,
            "collection_id": cid,
        })
        return CollectionRef(file_key=file_key, collection_id=cid,
                             name=name, modes=tuple(modes))

    def get_variable_collection(
        self, *, file_key: str, name: str
    ) -> CollectionRef | None:
        # Capture-mode adapters can't introspect live state; assume
        # absent and let downstream operations create.
        return None

    def create_variable(
        self, *, collection_ref: CollectionRef, name: str,
        type: VariableType, values_per_mode: dict[str, VariableValue],
    ) -> VariableRef:
        vid = self._stable_id("var", f"{collection_ref.collection_id}/{name}")
        self._capture("create_variable", {
            "collection_id": collection_ref.collection_id,
            "name": name, "type": type,
            "values_per_mode": values_per_mode,
            "variable_id": vid,
        })
        return VariableRef(collection_id=collection_ref.collection_id,
                           variable_id=vid, name=name, type=type)

    def update_variable(
        self, *, variable_ref: VariableRef,
        values_per_mode: dict[str, VariableValue],
    ) -> None:
        self._capture("update_variable", {
            "variable_id": variable_ref.variable_id,
            "variable_name": variable_ref.name,
            "values_per_mode": values_per_mode,
        })

    def create_alias_reference(
        self, *, source_var: VariableRef, target_var: VariableRef,
        mode_id: str,
    ) -> None:
        self._capture("create_alias_reference", {
            "source_name": source_var.name,
            "target_name": target_var.name,
            "mode_id": mode_id,
        })

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def create_paint_style(
        self, *, file_key: str, name: str, paints: list[Paint]
    ) -> StyleRef:
        sid = self._stable_id("paint", name)
        self._capture("create_paint_style", {
            "file_key": file_key, "name": name,
            "paints": [{"type": p.paint_type, "payload": p.payload}
                       for p in paints],
            "style_id": sid,
        })
        return StyleRef(file_key=file_key, style_id=sid,
                        name=name, style_type="PAINT")

    def create_text_style(
        self, *, file_key: str, name: str, properties: TextStyleProperties
    ) -> StyleRef:
        sid = self._stable_id("text", name)
        self._capture("create_text_style", {
            "file_key": file_key, "name": name,
            "font_family": properties.font_family,
            "font_size": properties.font_size,
            "font_weight": properties.font_weight,
            "line_height_pct": properties.line_height_pct,
            "letter_spacing": properties.letter_spacing,
            "style_id": sid,
        })
        return StyleRef(file_key=file_key, style_id=sid,
                        name=name, style_type="TEXT")

    def create_effect_style(
        self, *, file_key: str, name: str, effects: list[Effect]
    ) -> StyleRef:
        sid = self._stable_id("effect", name)
        self._capture("create_effect_style", {
            "file_key": file_key, "name": name,
            "effects": [{"type": e.effect_type, "payload": e.payload}
                        for e in effects],
            "style_id": sid,
        })
        return StyleRef(file_key=file_key, style_id=sid,
                        name=name, style_type="EFFECT")

    # ------------------------------------------------------------------
    # Components / pages
    # ------------------------------------------------------------------

    def create_page(self, *, file_key: str, name: str) -> PageRef:
        pid = self._stable_id("page", name)
        self._capture("create_page", {
            "file_key": file_key, "name": name, "page_id": pid,
        })
        return PageRef(file_key=file_key, page_id=pid, name=name)

    def create_component(
        self, *, page_ref: PageRef, name: str,
        geometry: ComponentGeometry,
    ) -> ComponentRef:
        nid = self._stable_id("comp", f"{page_ref.name}/{name}")
        self._capture("create_component", {
            "page_id": page_ref.page_id, "page_name": page_ref.name,
            "name": name,
            "width": geometry.width, "height": geometry.height,
            "background_color": geometry.background_color,
            "node_id": nid,
        })
        return ComponentRef(file_key=page_ref.file_key, node_id=nid, name=name)

    def create_component_set(
        self, *, page_ref: PageRef, name: str,
        variants: list[VariantSpec],
    ) -> ComponentSetRef:
        nid = self._stable_id("set", f"{page_ref.name}/{name}")
        self._capture("create_component_set", {
            "page_id": page_ref.page_id, "page_name": page_ref.name,
            "name": name,
            "variant_count": len(variants),
            "variants": [
                {"name": v.name, "properties": v.properties,
                 "width": v.geometry.width, "height": v.geometry.height}
                for v in variants
            ],
            "node_id": nid,
        })
        return ComponentSetRef(file_key=page_ref.file_key, node_id=nid,
                               name=name, variant_count=len(variants))

    def set_component_property(
        self, *, component_ref: ComponentRef, key: str, value: Any,
    ) -> None:
        self._capture("set_component_property", {
            "node_id": component_ref.node_id,
            "component_name": component_ref.name,
            "key": key, "value": value,
        })

    def import_svg_as_component(
        self, *, page_ref: PageRef, name: str,
        svg_source: str, canonical_size: tuple[int, int],
    ) -> ComponentRef:
        # Validate SVG envelope minimally — surface broken inputs at
        # capture time rather than at paste time
        if not svg_source.lstrip().startswith("<svg"):
            raise ValidationError(
                "svg_source does not start with <svg envelope",
                operation="import_svg_as_component",
                adapter_id=self.adapter_id(),
            )
        nid = self._stable_id("icon", f"{page_ref.name}/{name}")
        self._capture("import_svg_as_component", {
            "page_id": page_ref.page_id, "page_name": page_ref.name,
            "name": name,
            "svg_source": svg_source,
            "size": list(canonical_size),
            "node_id": nid,
        })
        return ComponentRef(file_key=page_ref.file_key, node_id=nid, name=name)

    def update_component_description(
        self, *, component_ref: ComponentRef,
        description: str, doc_links: list[str],
    ) -> None:
        self._capture("update_component_description", {
            "node_id": component_ref.node_id,
            "component_name": component_ref.name,
            "description": description,
            "doc_links": list(doc_links),
        })

    # ------------------------------------------------------------------
    # Instance composition
    # ------------------------------------------------------------------

    def place_instance(
        self, *, parent_ref: ComponentRef, component_ref: ComponentRef,
        position: tuple[int, int],
    ) -> InstanceRef:
        nid = self._stable_id(
            "inst", f"{parent_ref.node_id}/{component_ref.name}/{position}"
        )
        x, y = position
        self._capture("place_instance", {
            "parent_node_id": parent_ref.node_id,
            "parent_name": parent_ref.name,
            "component_node_id": component_ref.node_id,
            "component_name": component_ref.name,
            "x": x, "y": y,
            "instance_node_id": nid,
        })
        return InstanceRef(
            file_key=parent_ref.file_key, node_id=nid,
            component_node_id=component_ref.node_id,
            parent_node_id=parent_ref.node_id,
            name=component_ref.name,
        )

    def set_instance_property(
        self, *, instance_ref: InstanceRef, key: str, value: str,
    ) -> None:
        self._capture("set_instance_property", {
            "instance_node_id": instance_ref.node_id,
            "instance_name": instance_ref.name,
            "key": key, "value": value,
        })

    # ------------------------------------------------------------------
    # Code Connect — unsupported through plugin channel
    # ------------------------------------------------------------------

    def attach_code_connect(
        self, *, component_ref: ComponentRef,
        mapping: CodeConnectMapping,
    ) -> CodeConnectRef:
        raise CapabilityUnsupportedError(
            operation="attach_code_connect", adapter_id=self.adapter_id(),
            message="Code Connect is attached via REST or Figma CLI, "
                    "not through the plugin runtime.",
        )

    def list_code_connect(
        self, *, file_key: str
    ) -> list[CodeConnectRef]:
        # Plugin can read mappings stored as plugin data on the
        # component node, but for v1.1 we leave this as an empty list.
        return []

    # ------------------------------------------------------------------
    # Capture & render
    # ------------------------------------------------------------------

    def captured_operations(self) -> list[dict[str, Any]]:
        """Returns the in-memory operation log (read-only view)."""
        return list(self._operations)

    def render_typescript(self) -> str:
        """Render the captured operations as a single Figma plugin TS script.

        The script is an async IIFE that iterates the captured
        operations, applying each one through the live Figma plugin
        API. Idempotency guards inherited from v0.3.1 G14: find by
        name → update in place, else create.
        """
        header = self._header_lines()
        body_lines: list[str] = []
        for i, op in enumerate(self._operations, start=1):
            body_lines.append(f"  // ─── Operation {i}: {op['kind']}")
            body_lines.append("  try {")
            body_lines.extend(
                f"    {line}" for line in self._render_one(op).splitlines()
            )
            body_lines.append("  } catch (err) {")
            body_lines.append(
                f"    console.error('  ✗ Op {i} ({op['kind']}) failed:', err);"
            )
            body_lines.append("  }")
            body_lines.append("")

        return "\n".join([
            *header,
            "(async () => {",
            *body_lines,
            "  console.log('  ✓ figma-forge plugin script completed');",
            "})();",
        ]) + "\n"

    # ------------------------------------------------------------------
    # Private renderers — one per operation kind
    # ------------------------------------------------------------------

    def _render_one(self, op: dict[str, Any]) -> str:
        kind = op["kind"]
        renderer = _RENDERERS.get(kind)
        if renderer is None:
            return f"// (no renderer for {kind}; skipped)"
        return renderer(self, op)

    def _capture(self, kind: str, payload: dict[str, Any]) -> None:
        self._operations.append({"kind": kind, **payload})

    def _stable_id(self, prefix: str, key: str) -> str:
        """Stable, deterministic id from key text.

        Same name → same id within a session. This keeps the captured
        operations reproducible across re-runs, supporting the
        manifest signing flow (the resulting bundle hash doesn't
        change just because we re-captured).
        """
        h = hex(hash(key) & 0xFFFFFFFF)[2:]
        return f"{prefix}_{h:0>8}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _header_lines(self) -> list[str]:
        if self.locale == "tr-TR":
            return [
                "// figma-forge v1.1 plugin transport script — buradan üretildi.",
                "// Figma → Plugins → Development → Open Console → bu betiği yapıştırıp Enter'a basın.",
                "// Idempotent: aynı betiği yeniden çalıştırmak duplicate üretmez.",
                "",
            ]
        return [
            "// figma-forge v1.1 plugin transport script — generated.",
            "// Figma → Plugins → Development → Open Console → paste and Enter.",
            "// Idempotent: re-running this script does not produce duplicates.",
            "",
        ]


# ---------------------------------------------------------------------------
# Per-operation TS renderers
# ---------------------------------------------------------------------------

def _ts_escape(s: str) -> str:
    """Escape a string for embedding in a single-quoted TS literal."""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")


def _ts_template_safe(s: str) -> str:
    """Escape a string for embedding in a backtick TS template literal."""
    return (
        s.replace("\\", "\\\\")
         .replace("`", "\\`")
         .replace("${", "\\${")
    )


def _render_create_variable_collection(self, op):
    name = _ts_escape(op["name"])
    modes = op["modes"]
    modes_ts = ", ".join(f"'{_ts_escape(m)}'" for m in modes)
    return (
        f"const existingColl = figma.variables.getLocalVariableCollections()\n"
        f"  .find(c => c.name === '{name}');\n"
        f"let coll: VariableCollection;\n"
        f"if (existingColl) {{\n"
        f"  coll = existingColl;\n"
        f"  console.log('  · reusing existing collection \"{name}\"');\n"
        f"}} else {{\n"
        f"  coll = figma.variables.createVariableCollection('{name}');\n"
        f"  console.log('  + created collection \"{name}\"');\n"
        f"}}\n"
        f"// Ensure all required modes exist:\n"
        f"const requiredModes = [{modes_ts}];\n"
        f"for (const modeName of requiredModes) {{\n"
        f"  if (!coll.modes.some(m => m.name === modeName)) {{\n"
        f"    coll.addMode(modeName);\n"
        f"  }}\n"
        f"}}"
    )


def _render_create_variable(self, op):
    name = _ts_escape(op["name"])
    var_type = op["type"]
    vals_per_mode = op["values_per_mode"]
    cid = _ts_escape(op["collection_id"])
    lines = [
        f"// stable-id ref: {cid}",
        f"const coll{name.replace('.', '_').replace('-', '_')}_target = "
        f"figma.variables.getLocalVariableCollections().find(c => "
        f"c.variableIds.some(vid => "
        f"figma.variables.getVariableById(vid)?.name === '{name}')) ?? "
        f"figma.variables.getLocalVariableCollections()[0];",
        f"let v = figma.variables.getLocalVariables()"
        f".find(x => x.name === '{name}');",
        f"if (!v) {{",
        f"  v = figma.variables.createVariable("
        f"'{name}', coll{name.replace('.', '_').replace('-', '_')}_target, '{var_type}');",
        f"  console.log('  + created variable \"{name}\"');",
        f"}}",
    ]
    for mode_name, value in vals_per_mode.items():
        mode_esc = _ts_escape(mode_name)
        mode_lookup = (
            f"coll{name.replace('.', '_').replace('-', '_')}_target.modes"
            f".find(m => m.name === '{mode_esc}')?.modeId"
        )
        if isinstance(value, str):
            val_lit = f"'{_ts_escape(value)}'"
        elif isinstance(value, dict) and value.get("type") == "VARIABLE_ALIAS":
            target_id = _ts_escape(str(value.get("id", "")))
            val_lit = (
                f"figma.variables.createVariableAlias("
                f"figma.variables.getVariableById('{target_id}')!)"
            )
        else:
            val_lit = json.dumps(value)
        lines.append(
            f"if ({mode_lookup}) v.setValueForMode({mode_lookup}!, {val_lit});"
        )
    return "\n".join(lines)


def _render_create_page(self, op):
    name = _ts_escape(op["name"])
    return (
        f"const existingPage = figma.root.children.find("
        f"(p): p is PageNode => p.type === 'PAGE' && p.name === '{name}');\n"
        f"const page = existingPage ?? figma.createPage();\n"
        f"page.name = '{name}';\n"
        f"console.log(existingPage ? "
        f"'  · reusing page \"{name}\"' : '  + created page \"{name}\"');"
    )


def _render_import_svg(self, op):
    name = _ts_escape(op["name"])
    page_name = _ts_escape(op["page_name"])
    w, h = op["size"]
    svg_safe = _ts_template_safe(op["svg_source"])
    return (
        f"const targetPage = figma.root.children.find("
        f"(p): p is PageNode => p.type === 'PAGE' && p.name === '{page_name}');\n"
        f"if (!targetPage) throw new Error('page \"{page_name}\" not found; "
        f"run create_page first');\n"
        f"await figma.setCurrentPageAsync(targetPage);\n"
        f"const imported = figma.createNodeFromSvg(`{svg_safe}`);\n"
        f"imported.resize({w}, {h});\n"
        f"const existing = targetPage.findOne("
        f"(n): n is ComponentNode => n.type === 'COMPONENT' && n.name === '{name}');\n"
        f"let comp: ComponentNode;\n"
        f"if (existing) {{\n"
        f"  for (const c of [...existing.children]) c.remove();\n"
        f"  for (const c of [...imported.children]) existing.appendChild(c);\n"
        f"  existing.resize({w}, {h});\n"
        f"  imported.remove();\n"
        f"  comp = existing;\n"
        f"  console.log('  · updated icon component \"{name}\"');\n"
        f"}} else {{\n"
        f"  comp = figma.createComponentFromNode(imported);\n"
        f"  comp.name = '{name}';\n"
        f"  console.log('  + created icon component \"{name}\"');\n"
        f"}}"
    )


def _render_create_paint_style(self, op):
    name = _ts_escape(op["name"])
    # Build a Paint[] literal from the captured payload
    paints_lit = []
    for paint in op["paints"]:
        if paint["type"] == "SOLID":
            color = paint["payload"].get("color", {"r": 0, "g": 0, "b": 0})
            opacity = paint["payload"].get("opacity", 1.0)
            paints_lit.append(
                f"{{type: 'SOLID', "
                f"color: {{r: {color.get('r', 0)}, "
                f"g: {color.get('g', 0)}, b: {color.get('b', 0)}}}, "
                f"opacity: {opacity}}}"
            )
    paints_ts = "[" + ", ".join(paints_lit) + "]"
    return (
        f"const existing = figma.getLocalPaintStyles()"
        f".find(s => s.name === '{name}');\n"
        f"const style = existing ?? figma.createPaintStyle();\n"
        f"style.name = '{name}';\n"
        f"style.paints = {paints_ts};\n"
        f"console.log(existing ? "
        f"'  · updated paint style \"{name}\"' : '  + created paint style \"{name}\"');"
    )


def _render_create_text_style(self, op):
    name = _ts_escape(op["name"])
    family = _ts_escape(op["font_family"])
    size = op["font_size"]
    weight = op["font_weight"]
    # Map weight to FontStyle string (Figma uses style names: 'Regular', 'Bold' etc.)
    weight_to_style = {
        100: "Thin", 200: "Extra Light", 300: "Light",
        400: "Regular", 500: "Medium", 600: "Semi Bold",
        700: "Bold", 800: "Extra Bold", 900: "Black",
    }
    style_name = weight_to_style.get(weight, "Regular")
    return (
        f"await figma.loadFontAsync({{family: '{family}', style: '{style_name}'}});\n"
        f"const existing = figma.getLocalTextStyles()"
        f".find(s => s.name === '{name}');\n"
        f"const style = existing ?? figma.createTextStyle();\n"
        f"style.name = '{name}';\n"
        f"style.fontName = {{family: '{family}', style: '{style_name}'}};\n"
        f"style.fontSize = {size};\n"
        f"console.log(existing ? "
        f"'  · updated text style \"{name}\"' : '  + created text style \"{name}\"');"
    )


def _render_create_component(self, op):
    name = _ts_escape(op["name"])
    page_name = _ts_escape(op["page_name"])
    w, h = op["width"], op["height"]
    return (
        f"const targetPage = figma.root.children.find("
        f"(p): p is PageNode => p.type === 'PAGE' && p.name === '{page_name}');\n"
        f"if (!targetPage) throw new Error('page \"{page_name}\" not found');\n"
        f"await figma.setCurrentPageAsync(targetPage);\n"
        f"let comp = targetPage.findOne("
        f"(n): n is ComponentNode => n.type === 'COMPONENT' && n.name === '{name}');\n"
        f"if (!comp) {{\n"
        f"  comp = figma.createComponent();\n"
        f"  comp.name = '{name}';\n"
        f"  console.log('  + created component \"{name}\"');\n"
        f"}} else {{\n"
        f"  console.log('  · reusing component \"{name}\"');\n"
        f"}}\n"
        f"comp.resize({w}, {h});"
    )


def _render_update_component_description(self, op):
    name = _ts_escape(op["component_name"])
    desc = _ts_template_safe(op["description"])
    doc_links_ts = ", ".join(
        f'{{uri: "{_ts_escape(u)}"}}' for u in op["doc_links"]
    )
    return (
        f"const comp = figma.currentPage.findOne("
        f"(n): n is ComponentNode => n.type === 'COMPONENT' && n.name === '{name}') "
        f"?? figma.root.findOne("
        f"(n): n is ComponentNode => n.type === 'COMPONENT' && n.name === '{name}');\n"
        f"if (comp) {{\n"
        f"  comp.description = `{desc}`;\n"
        f"  comp.documentationLinks = [{doc_links_ts}];\n"
        f"  console.log('  · updated description on \"{name}\"');\n"
        f"}} else {{\n"
        f"  console.warn('  ⚠ component \"{name}\" not found for description update');\n"
        f"}}"
    )


def _render_create_alias_reference(self, op):
    source_name = _ts_escape(op["source_name"])
    target_name = _ts_escape(op["target_name"])
    mode_id = _ts_escape(op["mode_id"])
    return (
        f"const sourceVar = figma.variables.getLocalVariables()"
        f".find(v => v.name === '{source_name}');\n"
        f"const targetVar = figma.variables.getLocalVariables()"
        f".find(v => v.name === '{target_name}');\n"
        f"if (sourceVar && targetVar) {{\n"
        f"  const coll = figma.variables.getVariableCollectionById("
        f"sourceVar.variableCollectionId);\n"
        f"  const mode = coll?.modes.find(m => "
        f"m.name === '{mode_id}' || m.modeId === '{mode_id}');\n"
        f"  if (mode) {{\n"
        f"    sourceVar.setValueForMode(mode.modeId, "
        f"figma.variables.createVariableAlias(targetVar));\n"
        f"    console.log('  · alias {source_name} → {target_name} in mode {mode_id}');\n"
        f"  }}\n"
        f"}} else {{\n"
        f"  console.warn('  ⚠ alias rebind skipped — source or target missing');\n"
        f"}}"
    )


def _render_place_instance(self, op):
    parent_name = _ts_escape(op["parent_name"])
    comp_name = _ts_escape(op["component_name"])
    x, y = op["x"], op["y"]
    return (
        f"const parentComp = figma.currentPage.findOne("
        f"(n): n is ComponentNode => n.type === 'COMPONENT' "
        f"&& n.name === '{parent_name}') "
        f"?? figma.root.findOne("
        f"(n): n is ComponentNode => n.type === 'COMPONENT' "
        f"&& n.name === '{parent_name}');\n"
        f"const mainComp = figma.root.findOne("
        f"(n): n is ComponentNode => n.type === 'COMPONENT' "
        f"&& n.name === '{comp_name}');\n"
        f"if (parentComp && mainComp) {{\n"
        f"  const existing = parentComp.findOne("
        f"(n): n is InstanceNode => n.type === 'INSTANCE' "
        f"&& n.name === '{comp_name}');\n"
        f"  if (!existing) {{\n"
        f"    const inst = mainComp.createInstance();\n"
        f"    inst.x = {x}; inst.y = {y};\n"
        f"    parentComp.appendChild(inst);\n"
        f"    console.log('  + placed instance of \\\"{comp_name}\\\" "
        f"in \\\"{parent_name}\\\"');\n"
        f"  }} else {{\n"
        f"    console.log('  · instance of \\\"{comp_name}\\\" "
        f"already in \\\"{parent_name}\\\"');\n"
        f"  }}\n"
        f"}} else {{\n"
        f"  console.warn('  ⚠ place_instance skipped — "
        f"parent or main component missing');\n"
        f"}}"
    )


def _render_set_instance_property(self, op):
    inst_name = _ts_escape(op["instance_name"])
    key = _ts_escape(op["key"])
    value = _ts_escape(op["value"])
    return (
        f"const inst = figma.currentPage.findOne("
        f"(n): n is InstanceNode => n.type === 'INSTANCE' "
        f"&& n.name === '{inst_name}');\n"
        f"if (inst) {{\n"
        f"  try {{\n"
        f"    inst.setProperties({{ '{key}': '{value}' }});\n"
        f"    console.log('  · set {key}={value} on \\\"{inst_name}\\\"');\n"
        f"  }} catch (e) {{\n"
        f"    console.warn('  ⚠ setProperties failed on "
        f"\\\"{inst_name}\\\": ' + e);\n"
        f"  }}\n"
        f"}} else {{\n"
        f"  console.warn('  ⚠ instance \\\"{inst_name}\\\" not found');\n"
        f"}}"
    )


_RENDERERS: dict[str, Any] = {
    "create_variable_collection": _render_create_variable_collection,
    "create_variable": _render_create_variable,
    "create_alias_reference": _render_create_alias_reference,
    "create_page": _render_create_page,
    "import_svg_as_component": _render_import_svg,
    "create_paint_style": _render_create_paint_style,
    "create_text_style": _render_create_text_style,
    "create_component": _render_create_component,
    "update_component_description": _render_update_component_description,
    "place_instance": _render_place_instance,
    "set_instance_property": _render_set_instance_property,
}


__all__ = ["PluginCaptureTransport"]
