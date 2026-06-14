"""figma-forge ``McpCursorTransport`` — v1.2.0-alpha.

A buffering transport that accumulates every operation into an
in-memory log and, on :meth:`commit_session`, renders an **MCP
tool-call plan** — a structured, machine-readable descriptor of which
Figma MCP tools to invoke with which arguments, in order.

Design rationale (the architectural symmetry with PluginCapture)
================================================================

figma-forge is a library / CLI. It does **not** itself hold an MCP
client connection and cannot invoke MCP tools directly — only an LLM
agent (Claude, Cursor, or any MCP-capable host) can. So, exactly as
``PluginCaptureTransport`` emits a TypeScript script that an operator
pastes into the Figma plugin console, ``McpCursorTransport`` emits an
**MCP tool-call plan** that an agent executes by making the actual
Figma MCP calls.

    PluginCapture  →  TypeScript script   →  operator pastes into console
    McpCursor      →  MCP tool-call plan  →  agent invokes Figma MCP tools

Two dispatch mechanisms
=======================

The Figma MCP server exposes a mix of granular native tools and one
high-level natural-language tool (``Figma:use_figma`` — "Create, edit,
generate, or sync any design"). Each figma-forge operation maps to one
of two mechanisms, recorded on every emitted descriptor:

- ``"native"`` — a dedicated Figma MCP tool exists and the operation
  is deterministic. Five operations: ``create_file``
  (``Figma:create_new_file``), ``get_file`` (``Figma:get_metadata``),
  ``get_variable_collection`` (``Figma:get_variable_defs``),
  ``attach_code_connect`` (``Figma:send_code_connect_mappings``),
  ``list_code_connect`` (``Figma:get_code_connect_map``).

- ``"use_figma_nl"`` — no granular native tool exists, so the
  operation is expressed as a well-structured natural-language
  instruction for ``Figma:use_figma``. Best-effort and
  non-deterministic — the agent and Figma's generative layer
  interpret the instruction. Thirteen operations (Variables, styles,
  pages, components, component sets, SVG import, descriptions).

The capability matrix records this distinction as ``supported`` vs
``supported-nl``; this adapter's :meth:`emit_mechanism` reads it back.

``publish_library`` is ``unsupported`` — library publish is a manual
Figma UI action with no MCP tool.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .capability_matrix import (
    ADAPTER_MCP_CURSOR,
    capability,
    supported_operations,
)
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
from .mcp_dispatch import REGISTRY as _REGISTRY

#: Operation → (mcp_tool, mechanism). **Derived from**
#: :data:`figma_forge.transport.mcp_dispatch.REGISTRY` — the single
#: source of truth for MCP dispatch. To add or promote an operation,
#: edit ``mcp_dispatch.REGISTRY``; this map updates automatically.
_MCP_TOOL_FOR_OPERATION: dict[str, tuple[str, str]] = {
    op: (spec.mcp_tool, spec.mechanism)
    for op, spec in _REGISTRY.items()
}

#: Plan-format version, embedded in the rendered plan envelope so
#: downstream agents can detect schema changes.
MCP_PLAN_FORMAT_VERSION = "1.0"


@dataclass
class McpCursorTransport:
    """Buffers operations; emits an MCP tool-call plan on commit.

    The plan is a list of descriptors, each shaped:

    .. code-block:: json

        {
          "step": 1,
          "operation": "create_variable_collection",
          "mcp_tool": "Figma:use_figma",
          "mechanism": "use_figma_nl",
          "arguments": { ... },
          "instruction": "Create a variable collection named ..."
        }

    For ``native`` descriptors, ``arguments`` is the literal argument
    object to pass to the MCP tool. For ``use_figma_nl`` descriptors,
    ``instruction`` carries the natural-language prompt and
    ``arguments`` carries the structured intent (for the agent to
    cross-check or render its own phrasing).

    The optional ``locale`` controls the language of generated
    natural-language instructions (``"en-US"`` or ``"tr-TR"``).
    """

    locale: str = "en-US"
    _operations: list[dict[str, Any]] = field(default_factory=list)
    _current_session: SessionToken | None = None

    # ------------------------------------------------------------------
    # Identity & capability
    # ------------------------------------------------------------------

    def adapter_id(self) -> str:
        return ADAPTER_MCP_CURSOR

    def supports(self, operation_name: str) -> bool:
        return operation_name in supported_operations(ADAPTER_MCP_CURSOR)

    def authentication_required(self) -> AuthRequirement:
        # MCP tools are exposed in the agent's ambient context; no
        # separate PAT is read by this adapter. The agent's MCP host
        # owns the Figma connection / OAuth.
        return AuthRequirement(
            needs_credentials=False, credential_kind="ambient-mcp"
        )

    def emit_mechanism(self, operation_name: str) -> str:
        """Return ``"native"`` or ``"use_figma_nl"`` for an operation.

        Raises :class:`CapabilityUnsupportedError` if the operation is
        not supported by this adapter (e.g. ``publish_library``).
        """
        entry = _MCP_TOOL_FOR_OPERATION.get(operation_name)
        if entry is None:
            raise CapabilityUnsupportedError(
                operation=operation_name, adapter_id=self.adapter_id(),
                message=f"{operation_name} has no MCP dispatch mapping.",
            )
        return entry[1]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def begin_session(self) -> SessionToken:
        token = SessionToken(
            adapter_id=ADAPTER_MCP_CURSOR,
            started_at=self._now(),
            token=f"mcp-{uuid.uuid4().hex[:12]}",
        )
        self._current_session = token
        return token

    def commit_session(self, token: SessionToken) -> SessionResult:
        plan = self.render_mcp_plan()
        return SessionResult(
            token=token,
            operations_applied=len(self._operations),
            operations_failed=0,
            artifacts={
                "mcp_plan_json": plan,
                "operation_count": str(len(self._operations)),
                "plan_format_version": MCP_PLAN_FORMAT_VERSION,
            },
        )

    def rollback_session(self, token: SessionToken) -> None:
        self._operations.clear()
        self._current_session = None

    # ------------------------------------------------------------------
    # File-level
    # ------------------------------------------------------------------

    def create_file(self, *, name: str, file_kind: FileKind) -> FileRef:
        key = self._stable_id("file", name)
        self._emit("create_file", {
            "name": name, "file_kind": file_kind,
        }, instruction=self._nl(
            f"Create a new Figma {file_kind} file named “{name}”.",
            f"“{name}” adında yeni bir Figma {file_kind} dosyası oluştur.",
        ))
        return FileRef(key=key, name=name, kind=file_kind)

    def get_file(self, *, key: str) -> FileRef:
        # Native read — emit a descriptor; the agent fills the result.
        # We return a best-effort placeholder ref so the pipeline can
        # proceed; the agent reconciles real metadata at execution.
        self._emit("get_file", {"key": key})
        return FileRef(key=key, name=f"<file:{key}>", kind="design")

    def publish_library(self, *, file_key: str, changelog: str) -> PublishRef:
        raise CapabilityUnsupportedError(
            operation="publish_library", adapter_id=self.adapter_id(),
            message="Library publish is a manual Figma UI action; "
                    "no MCP tool exposes it.",
        )

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def create_variable_collection(
        self, *, file_key: str, name: str, modes: list[str]
    ) -> CollectionRef:
        cid = self._stable_id("vc", name)
        modes_txt = ", ".join(modes)
        self._emit("create_variable_collection", {
            "file_key": file_key, "name": name, "modes": modes,
            "collection_id": cid,
        }, instruction=self._nl(
            f"In file {file_key}, create a variable collection named "
            f"“{name}” with modes: {modes_txt}.",
            f"{file_key} dosyasında “{name}” adında bir değişken "
            f"koleksiyonu oluştur; modlar: {modes_txt}.",
        ))
        return CollectionRef(file_key=file_key, collection_id=cid,
                             name=name, modes=tuple(modes))

    def get_variable_collection(
        self, *, file_key: str, name: str
    ) -> CollectionRef | None:
        # Native read — emit a get_variable_defs descriptor. Plan-mode
        # cannot resolve live state, so return None and let downstream
        # operations create (the agent dedupes at execution).
        self._emit("get_variable_collection", {
            "file_key": file_key, "name": name,
        })
        return None

    def create_variable(
        self, *, collection_ref: CollectionRef, name: str,
        type: VariableType, values_per_mode: dict[str, VariableValue],
    ) -> VariableRef:
        vid = self._stable_id("var", f"{collection_ref.collection_id}/{name}")
        vals = ", ".join(f"{m}={v}" for m, v in values_per_mode.items())
        self._emit("create_variable", {
            "collection_id": collection_ref.collection_id,
            "name": name, "type": type,
            "values_per_mode": values_per_mode,
            "variable_id": vid,
        }, instruction=self._nl(
            f"In collection “{collection_ref.name}”, create a {type} "
            f"variable named “{name}” with values: {vals}.",
            f"“{collection_ref.name}” koleksiyonunda “{name}” adında "
            f"bir {type} değişkeni oluştur; değerler: {vals}.",
        ))
        return VariableRef(collection_id=collection_ref.collection_id,
                           variable_id=vid, name=name, type=type)

    def update_variable(
        self, *, variable_ref: VariableRef,
        values_per_mode: dict[str, VariableValue],
    ) -> None:
        vals = ", ".join(f"{m}={v}" for m, v in values_per_mode.items())
        self._emit("update_variable", {
            "variable_id": variable_ref.variable_id,
            "variable_name": variable_ref.name,
            "values_per_mode": values_per_mode,
        }, instruction=self._nl(
            f"Update variable “{variable_ref.name}” to values: {vals}.",
            f"“{variable_ref.name}” değişkenini şu değerlere güncelle: {vals}.",
        ))

    def create_alias_reference(
        self, *, source_var: VariableRef, target_var: VariableRef,
        mode_id: str,
    ) -> None:
        self._emit("create_alias_reference", {
            "source_variable_id": source_var.variable_id,
            "source_name": source_var.name,
            "target_variable_id": target_var.variable_id,
            "target_name": target_var.name,
            "mode_id": mode_id,
        }, instruction=self._nl(
            f"Bind variable “{source_var.name}” (mode {mode_id}) as an "
            f"alias to “{target_var.name}”.",
            f"“{source_var.name}” değişkenini (mod {mode_id}) "
            f"“{target_var.name}” değişkenine alias olarak bağla.",
        ))

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def create_paint_style(
        self, *, file_key: str, name: str, paints: list[Paint]
    ) -> StyleRef:
        sid = self._stable_id("paint", name)
        self._emit("create_paint_style", {
            "file_key": file_key, "name": name,
            "paints": [self._paint_dict(p) for p in paints],
            "style_id": sid,
        }, instruction=self._nl(
            f"Create a paint style named “{name}”.",
            f"“{name}” adında bir boya stili oluştur.",
        ))
        return StyleRef(file_key=file_key, style_id=sid, name=name,
                        style_type="paint")

    def create_text_style(
        self, *, file_key: str, name: str,
        properties: TextStyleProperties,
    ) -> StyleRef:
        sid = self._stable_id("text", name)
        self._emit("create_text_style", {
            "file_key": file_key, "name": name,
            "properties": self._text_props_dict(properties),
            "style_id": sid,
        }, instruction=self._nl(
            f"Create a text style named “{name}”.",
            f"“{name}” adında bir metin stili oluştur.",
        ))
        return StyleRef(file_key=file_key, style_id=sid, name=name,
                        style_type="text")

    def create_effect_style(
        self, *, file_key: str, name: str, effects: list[Effect]
    ) -> StyleRef:
        sid = self._stable_id("effect", name)
        self._emit("create_effect_style", {
            "file_key": file_key, "name": name,
            "effects": [self._effect_dict(e) for e in effects],
            "style_id": sid,
        }, instruction=self._nl(
            f"Create an effect style named “{name}”.",
            f"“{name}” adında bir efekt stili oluştur.",
        ))
        return StyleRef(file_key=file_key, style_id=sid, name=name,
                        style_type="effect")

    # ------------------------------------------------------------------
    # Pages & components
    # ------------------------------------------------------------------

    def create_page(self, *, file_key: str, name: str) -> PageRef:
        pid = self._stable_id("page", name)
        self._emit("create_page", {
            "file_key": file_key, "name": name, "page_id": pid,
        }, instruction=self._nl(
            f"Create a page named “{name}”.",
            f"“{name}” adında bir sayfa oluştur.",
        ))
        return PageRef(file_key=file_key, page_id=pid, name=name)

    def create_component(
        self, *, page_ref: PageRef, name: str,
        geometry: ComponentGeometry,
    ) -> ComponentRef:
        nid = self._stable_id("comp", f"{page_ref.name}/{name}")
        self._emit("create_component", {
            "page_id": page_ref.page_id, "page_name": page_ref.name,
            "name": name,
            "geometry": {"width": geometry.width, "height": geometry.height},
            "node_id": nid,
        }, instruction=self._nl(
            f"On page “{page_ref.name}”, create a component named "
            f"“{name}” ({geometry.width}×{geometry.height}).",
            f"“{page_ref.name}” sayfasında “{name}” adında bir "
            f"bileşen oluştur ({geometry.width}×{geometry.height}).",
        ))
        return ComponentRef(file_key=page_ref.file_key, node_id=nid, name=name)

    def create_component_set(
        self, *, page_ref: PageRef, name: str,
        variants: list[VariantSpec],
    ) -> ComponentSetRef:
        nid = self._stable_id("set", f"{page_ref.name}/{name}")
        self._emit("create_component_set", {
            "page_id": page_ref.page_id, "page_name": page_ref.name,
            "name": name,
            "variant_count": len(variants),
            "variants": [
                {"name": v.name, "properties": v.properties}
                for v in variants
            ],
            "node_id": nid,
        }, instruction=self._nl(
            f"On page “{page_ref.name}”, create a component set named "
            f"“{name}” with {len(variants)} variants.",
            f"“{page_ref.name}” sayfasında “{name}” adında "
            f"{len(variants)} varyantlı bir bileşen seti oluştur.",
        ))
        return ComponentSetRef(file_key=page_ref.file_key, node_id=nid,
                               name=name, variant_count=len(variants))

    def set_component_property(
        self, *, component_ref: ComponentRef,
        property_name: str, property_value: str,
    ) -> None:
        self._emit("set_component_property", {
            "node_id": component_ref.node_id,
            "component_name": component_ref.name,
            "property_name": property_name,
            "property_value": property_value,
        }, instruction=self._nl(
            f"Set property “{property_name}”=“{property_value}” on "
            f"component “{component_ref.name}”.",
            f"“{component_ref.name}” bileşeninde "
            f"“{property_name}”=“{property_value}” özelliğini ayarla.",
        ))

    def import_svg_as_component(
        self, *, page_ref: PageRef, name: str,
        svg_source: str, canonical_size: tuple[int, int],
    ) -> ComponentRef:
        if not svg_source.lstrip().startswith("<svg"):
            raise ValidationError(
                "svg_source does not start with <svg envelope",
                operation="import_svg_as_component",
                adapter_id=self.adapter_id(),
            )
        nid = self._stable_id("icon", f"{page_ref.name}/{name}")
        w, h = canonical_size
        self._emit("import_svg_as_component", {
            "page_id": page_ref.page_id, "page_name": page_ref.name,
            "name": name,
            "svg_source": svg_source,
            "size": [w, h],
            "node_id": nid,
        }, instruction=self._nl(
            f"Upload the SVG and place it as a {w}×{h} component named "
            f"“{name}” on page “{page_ref.name}”.",
            f"SVG'yi yükle ve “{page_ref.name}” sayfasında “{name}” "
            f"adında {w}×{h} bir bileşen olarak yerleştir.",
        ))
        return ComponentRef(file_key=page_ref.file_key, node_id=nid, name=name)

    def update_component_description(
        self, *, component_ref: ComponentRef,
        description: str, doc_links: list[str],
    ) -> None:
        self._emit("update_component_description", {
            "node_id": component_ref.node_id,
            "component_name": component_ref.name,
            "description": description,
            "doc_links": list(doc_links),
        }, instruction=self._nl(
            f"Set the description of component “{component_ref.name}”.",
            f"“{component_ref.name}” bileşeninin açıklamasını ayarla.",
        ))

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
        self._emit("place_instance", {
            "parent_node_id": parent_ref.node_id,
            "parent_name": parent_ref.name,
            "component_node_id": component_ref.node_id,
            "component_name": component_ref.name,
            "position": [x, y],
            "instance_node_id": nid,
        }, instruction=self._nl(
            f"Inside component “{parent_ref.name}”, place an instance of "
            f"“{component_ref.name}” at ({x}, {y}).",
            f"“{parent_ref.name}” bileşeninin içine “{component_ref.name}” "
            f"bileşeninin bir örneğini ({x}, {y}) konumuna yerleştir.",
        ))
        return InstanceRef(
            file_key=parent_ref.file_key, node_id=nid,
            component_node_id=component_ref.node_id,
            parent_node_id=parent_ref.node_id,
            name=component_ref.name,
        )

    def set_instance_property(
        self, *, instance_ref: InstanceRef, key: str, value: str,
    ) -> None:
        self._emit("set_instance_property", {
            "instance_node_id": instance_ref.node_id,
            "instance_name": instance_ref.name,
            "key": key, "value": value,
        }, instruction=self._nl(
            f"On instance “{instance_ref.name}”, set property "
            f"“{key}”=“{value}”.",
            f"“{instance_ref.name}” örneğinde “{key}”=“{value}” "
            f"özelliğini ayarla.",
        ))

    # ------------------------------------------------------------------
    # Code Connect — native MCP tools
    # ------------------------------------------------------------------

    def attach_code_connect(
        self, *, component_ref: ComponentRef,
        mapping: CodeConnectMapping,
    ) -> CodeConnectRef:
        ref_id = self._stable_id("cc", component_ref.name)
        self._emit("attach_code_connect", {
            "node_id": component_ref.node_id,
            "component_name": component_ref.name,
            "framework": mapping.framework,
            "import_statement": mapping.import_statement,
            "code_example": mapping.code_example,
            "props_mapping": mapping.props_mapping,
            "code_connect_id": ref_id,
        })
        return CodeConnectRef(
            component_node_id=component_ref.node_id,
            framework=mapping.framework, mapping_id=ref_id,
        )

    def list_code_connect(self, *, file_key: str) -> list[CodeConnectRef]:
        # Native read — emit a get_code_connect_map descriptor. Plan
        # mode returns an empty list; the agent fills real mappings.
        self._emit("list_code_connect", {"file_key": file_key})
        return []

    # ------------------------------------------------------------------
    # Plan emission & rendering
    # ------------------------------------------------------------------

    def captured_operations(self) -> list[dict[str, Any]]:
        """Read-only view of the in-memory descriptor log."""
        return list(self._operations)

    def render_mcp_plan(self) -> str:
        """Render the accumulated descriptors as a JSON plan envelope.

        The plan is the artifact an MCP-capable agent consumes to
        replay the build against a live Figma file. The envelope
        carries the format version, a step count, and an ordered list
        of tool-call descriptors.
        """
        steps = []
        for i, op in enumerate(self._operations, start=1):
            step = {
                "step": i,
                "operation": op["operation"],
                "mcp_tool": op["mcp_tool"],
                "mechanism": op["mechanism"],
                "arguments": op["arguments"],
            }
            if op.get("instruction"):
                step["instruction"] = op["instruction"]
            steps.append(step)

        envelope = {
            "plan_format_version": MCP_PLAN_FORMAT_VERSION,
            "adapter": ADAPTER_MCP_CURSOR,
            "locale": self.locale,
            "generated_at": self._now(),
            "step_count": len(steps),
            "native_steps": sum(
                1 for s in steps if s["mechanism"] == "native"
            ),
            "use_figma_nl_steps": sum(
                1 for s in steps if s["mechanism"] == "use_figma_nl"
            ),
            "steps": steps,
        }
        return json.dumps(envelope, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(
        self, operation: str, arguments: dict[str, Any],
        *, instruction: str = "",
    ) -> None:
        """Append one MCP tool-call descriptor to the buffer.

        Looks up the MCP tool + mechanism from the single-source map;
        raises if the operation has no mapping (programming error —
        every supported operation must be registered).
        """
        entry = _MCP_TOOL_FOR_OPERATION.get(operation)
        if entry is None:
            raise CapabilityUnsupportedError(
                operation=operation, adapter_id=self.adapter_id(),
                message=f"{operation} has no MCP dispatch mapping.",
            )
        mcp_tool, mechanism = entry
        descriptor: dict[str, Any] = {
            "operation": operation,
            "mcp_tool": mcp_tool,
            "mechanism": mechanism,
            "arguments": arguments,
        }
        # Native descriptors don't need a natural-language instruction;
        # use_figma_nl descriptors require one.
        if mechanism == "use_figma_nl":
            descriptor["instruction"] = instruction
        self._operations.append(descriptor)

    def _nl(self, en: str, tr: str) -> str:
        """Pick the natural-language instruction for the active locale."""
        return tr if self.locale == "tr-TR" else en

    def _stable_id(self, prefix: str, key: str) -> str:
        """Deterministic id from key text (same as PluginCapture)."""
        h = hex(hash(key) & 0xFFFFFFFF)[2:]
        return f"{prefix}_{h:0>8}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # --- value serializers (mirror PluginCapture's payload shapes) ---

    @staticmethod
    def _paint_dict(p: Paint) -> dict[str, Any]:
        return {"paint_type": p.paint_type, "payload": p.payload}

    @staticmethod
    def _text_props_dict(t: TextStyleProperties) -> dict[str, Any]:
        return {
            "font_family": t.font_family, "font_size": t.font_size,
            "font_weight": t.font_weight,
            "line_height_pct": t.line_height_pct,
            "letter_spacing": t.letter_spacing,
            "text_decoration": t.text_decoration,
        }

    @staticmethod
    def _effect_dict(e: Effect) -> dict[str, Any]:
        return {"effect_type": e.effect_type, "payload": e.payload}
