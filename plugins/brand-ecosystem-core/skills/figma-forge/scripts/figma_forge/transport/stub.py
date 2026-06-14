"""figma-forge ``StubTransport`` — v1.1.0-alpha.

The stub adapter is the **always-available, never-failing** fallback.
It implements every operation in the :class:`TransportAdapter`
Protocol as a structured log emission; no Figma is contacted, no
credentials are required, no state is persisted beyond the in-memory
session log.

Use cases:

- **Tests** — every other adapter is mocked via Stub
- **CI dry-runs** — preview what the pipeline would do without touching real Figma
- **Router fallback** — when no preferred adapter can handle an operation
- **Documentation** — readable session logs document the orchestration outcome
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .capability_matrix import ADAPTER_STUB, supported_operations
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

logger = logging.getLogger("figma_forge.transport.stub")


@dataclass
class StubTransport:
    """Always-available no-op transport. Records every operation."""

    operations_log: list[dict[str, Any]] = field(default_factory=list)
    _next_id_counter: int = 0
    _current_session: SessionToken | None = None

    # ------------------------------------------------------------------
    # Identity & capability
    # ------------------------------------------------------------------

    def adapter_id(self) -> str:
        return ADAPTER_STUB

    def supports(self, operation_name: str) -> bool:
        return operation_name in supported_operations(ADAPTER_STUB)

    def authentication_required(self) -> AuthRequirement:
        return AuthRequirement(needs_credentials=False, credential_kind="none")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def begin_session(self) -> SessionToken:
        token = SessionToken(
            adapter_id=ADAPTER_STUB,
            started_at=self._now(),
            token=f"stub-{uuid.uuid4().hex[:12]}",
        )
        self._current_session = token
        self._log("begin_session", token=token.token)
        return token

    def commit_session(self, token: SessionToken) -> SessionResult:
        applied = len([
            op for op in self.operations_log
            if op.get("kind") not in {"begin_session", "commit_session",
                                      "rollback_session"}
        ])
        self._log("commit_session", token=token.token, applied=applied)
        self._current_session = None
        return SessionResult(
            token=token, operations_applied=applied,
            operations_failed=0,
            artifacts={"log_count": str(len(self.operations_log))},
        )

    def rollback_session(self, token: SessionToken) -> None:
        self._log("rollback_session", token=token.token)
        self._current_session = None

    # ------------------------------------------------------------------
    # File-level
    # ------------------------------------------------------------------

    def create_file(self, *, name: str, file_kind: FileKind) -> FileRef:
        key = self._fake_id("file")
        self._log("create_file", name=name, file_kind=file_kind, key=key)
        return FileRef(key=key, name=name, kind=file_kind)

    def get_file(self, *, key: str) -> FileRef:
        self._log("get_file", key=key)
        return FileRef(key=key, name=f"stub-file-{key}", kind="generic")

    def publish_library(
        self, *, file_key: str, changelog: str
    ) -> PublishRef:
        pid = self._fake_id("publish")
        self._log("publish_library", file_key=file_key,
                  changelog=changelog, publish_id=pid)
        return PublishRef(file_key=file_key, publish_id=pid, changelog=changelog)

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def create_variable_collection(
        self, *, file_key: str, name: str, modes: list[str]
    ) -> CollectionRef:
        cid = self._fake_id("vc")
        self._log("create_variable_collection",
                  file_key=file_key, name=name, modes=modes, collection_id=cid)
        return CollectionRef(file_key=file_key, collection_id=cid,
                             name=name, modes=tuple(modes))

    def get_variable_collection(
        self, *, file_key: str, name: str
    ) -> CollectionRef | None:
        self._log("get_variable_collection", file_key=file_key, name=name)
        # Stub: always reports "not found" so caller's create-if-missing
        # pattern exercises the create path consistently
        return None

    def create_variable(
        self, *, collection_ref: CollectionRef, name: str,
        type: VariableType, values_per_mode: dict[str, VariableValue],
    ) -> VariableRef:
        vid = self._fake_id("var")
        self._log("create_variable",
                  collection_id=collection_ref.collection_id,
                  name=name, type=type,
                  modes=list(values_per_mode.keys()),
                  variable_id=vid)
        return VariableRef(
            collection_id=collection_ref.collection_id,
            variable_id=vid, name=name, type=type,
        )

    def update_variable(
        self, *, variable_ref: VariableRef,
        values_per_mode: dict[str, VariableValue],
    ) -> None:
        self._log("update_variable",
                  variable_id=variable_ref.variable_id,
                  modes=list(values_per_mode.keys()))

    def create_alias_reference(
        self, *, source_var: VariableRef, target_var: VariableRef,
        mode_id: str,
    ) -> None:
        self._log("create_alias_reference",
                  source=source_var.name or source_var.variable_id,
                  target=target_var.name or target_var.variable_id,
                  mode_id=mode_id)

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def create_paint_style(
        self, *, file_key: str, name: str, paints: list[Paint]
    ) -> StyleRef:
        sid = self._fake_id("paint")
        self._log("create_paint_style", file_key=file_key,
                  name=name, paint_count=len(paints), style_id=sid)
        return StyleRef(file_key=file_key, style_id=sid,
                        name=name, style_type="PAINT")

    def create_text_style(
        self, *, file_key: str, name: str, properties: TextStyleProperties
    ) -> StyleRef:
        sid = self._fake_id("text")
        self._log("create_text_style", file_key=file_key, name=name,
                  font_family=properties.font_family,
                  font_size=properties.font_size, style_id=sid)
        return StyleRef(file_key=file_key, style_id=sid,
                        name=name, style_type="TEXT")

    def create_effect_style(
        self, *, file_key: str, name: str, effects: list[Effect]
    ) -> StyleRef:
        sid = self._fake_id("effect")
        self._log("create_effect_style", file_key=file_key, name=name,
                  effect_count=len(effects), style_id=sid)
        return StyleRef(file_key=file_key, style_id=sid,
                        name=name, style_type="EFFECT")

    # ------------------------------------------------------------------
    # Components / pages
    # ------------------------------------------------------------------

    def create_page(self, *, file_key: str, name: str) -> PageRef:
        pid = self._fake_id("page")
        self._log("create_page", file_key=file_key, name=name, page_id=pid)
        return PageRef(file_key=file_key, page_id=pid, name=name)

    def create_component(
        self, *, page_ref: PageRef, name: str,
        geometry: ComponentGeometry,
    ) -> ComponentRef:
        nid = self._fake_id("comp")
        self._log("create_component", page_id=page_ref.page_id, name=name,
                  width=geometry.width, height=geometry.height,
                  node_id=nid)
        return ComponentRef(file_key=page_ref.file_key,
                            node_id=nid, name=name)

    def create_component_set(
        self, *, page_ref: PageRef, name: str,
        variants: list[VariantSpec],
    ) -> ComponentSetRef:
        nid = self._fake_id("set")
        self._log("create_component_set", page_id=page_ref.page_id,
                  name=name, variant_count=len(variants), node_id=nid)
        return ComponentSetRef(file_key=page_ref.file_key,
                               node_id=nid, name=name,
                               variant_count=len(variants))

    def set_component_property(
        self, *, component_ref: ComponentRef, key: str, value: Any,
    ) -> None:
        self._log("set_component_property",
                  node_id=component_ref.node_id, key=key,
                  value=str(value)[:60])

    def import_svg_as_component(
        self, *, page_ref: PageRef, name: str,
        svg_source: str, canonical_size: tuple[int, int],
    ) -> ComponentRef:
        nid = self._fake_id("icon")
        self._log("import_svg_as_component",
                  page_id=page_ref.page_id, name=name,
                  svg_bytes=len(svg_source.encode("utf-8")),
                  size=list(canonical_size), node_id=nid)
        return ComponentRef(file_key=page_ref.file_key,
                            node_id=nid, name=name)

    def update_component_description(
        self, *, component_ref: ComponentRef,
        description: str, doc_links: list[str],
    ) -> None:
        self._log("update_component_description",
                  node_id=component_ref.node_id,
                  description_chars=len(description),
                  doc_link_count=len(doc_links))

    # ------------------------------------------------------------------
    # Instance composition
    # ------------------------------------------------------------------

    def place_instance(
        self, *, parent_ref: ComponentRef, component_ref: ComponentRef,
        position: tuple[int, int],
    ) -> InstanceRef:
        nid = self._fake_id("inst")
        self._log("place_instance",
                  parent_node_id=parent_ref.node_id,
                  component_node_id=component_ref.node_id,
                  position=list(position),
                  instance_node_id=nid)
        return InstanceRef(
            file_key=parent_ref.file_key, node_id=nid,
            component_node_id=component_ref.node_id,
            parent_node_id=parent_ref.node_id,
            name=component_ref.name,
        )

    def set_instance_property(
        self, *, instance_ref: InstanceRef, key: str, value: str,
    ) -> None:
        self._log("set_instance_property",
                  instance_node_id=instance_ref.node_id,
                  key=key, value=value)

    # ------------------------------------------------------------------
    # Code Connect
    # ------------------------------------------------------------------

    def attach_code_connect(
        self, *, component_ref: ComponentRef,
        mapping: CodeConnectMapping,
    ) -> CodeConnectRef:
        mid = self._fake_id("cc")
        self._log("attach_code_connect",
                  node_id=component_ref.node_id,
                  framework=mapping.framework,
                  mapping_id=mid)
        return CodeConnectRef(component_node_id=component_ref.node_id,
                              mapping_id=mid, framework=mapping.framework)

    def list_code_connect(self, *, file_key: str) -> list[CodeConnectRef]:
        self._log("list_code_connect", file_key=file_key)
        return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fake_id(self, prefix: str) -> str:
        self._next_id_counter += 1
        return f"{prefix}_{self._next_id_counter:04d}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _log(self, kind: str, **fields: Any) -> None:
        entry = {"kind": kind, "ts": self._now(), **fields}
        self.operations_log.append(entry)
        logger.debug("stub-op %s", json.dumps(entry, ensure_ascii=False))


__all__ = ["StubTransport"]
