"""figma-forge transport Protocol — v1.1.0-alpha.

The :class:`TransportAdapter` Protocol captures the **minimum
sufficient operation set** that the 7 currently-deferred orchestrate
modes need from a Figma transport. Concrete adapters
(``StubTransport``, ``PluginCaptureTransport``, ``RestTransport``)
implement this Protocol; the router selects per-operation.

The Protocol is intentionally **flat** — no inheritance hierarchy
between operation groups — so each adapter can implement only the
subset it supports and have the others raise
:class:`CapabilityUnsupportedError`.

Reference types (``FileRef``, ``CollectionRef``, etc.) are dataclasses
that carry the **opaque external id** plus a few channel-independent
descriptors. They are deliberately shallow so the wire format can
evolve without disturbing the Protocol surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Type aliases & enums (string-based for v1.x append-only stability)
# ---------------------------------------------------------------------------

FileKind = Literal["foundations", "components", "patterns", "icons", "generic"]

VariableType = Literal["COLOR", "FLOAT", "STRING", "BOOLEAN"]
"""Aligned with Figma's Variables API resolved type values."""

PaintType = Literal["SOLID", "GRADIENT_LINEAR", "GRADIENT_RADIAL", "IMAGE"]


# ---------------------------------------------------------------------------
# Reference dataclasses — opaque ids plus minimal descriptors
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FileRef:
    """Pointer to a Figma file.

    ``last_modified`` carries the file's last-modified timestamp
    (ISO 8601, as reported by the Figma REST API's ``lastModified``
    field or the MCP metadata) when the adapter can resolve it; it is
    empty for capture-mode adapters that cannot read live state. It is
    used by concurrency detection (v1.2.0) to spot edits made by
    another editor during a build.
    """
    key: str
    name: str = ""
    kind: FileKind = "generic"
    last_modified: str = ""


@dataclass(frozen=True)
class PageRef:
    """Pointer to a page within a file."""
    file_key: str
    page_id: str
    name: str = ""


@dataclass(frozen=True)
class CollectionRef:
    """Pointer to a Variables collection."""
    file_key: str
    collection_id: str
    name: str = ""
    modes: tuple[str, ...] = ()


@dataclass(frozen=True)
class VariableRef:
    """Pointer to a Figma Variable within a collection."""
    collection_id: str
    variable_id: str
    name: str = ""
    type: VariableType = "STRING"


@dataclass(frozen=True)
class StyleRef:
    """Pointer to a paint/text/effect style."""
    file_key: str
    style_id: str
    name: str = ""
    style_type: Literal["PAINT", "TEXT", "EFFECT"] = "PAINT"


@dataclass(frozen=True)
class ComponentRef:
    """Pointer to a Component or ComponentSet member."""
    file_key: str
    node_id: str
    name: str = ""
    is_set_member: bool = False


@dataclass(frozen=True)
class ComponentSetRef:
    """Pointer to a ComponentSet (variant component family)."""
    file_key: str
    node_id: str
    name: str = ""
    variant_count: int = 0


@dataclass(frozen=True)
class InstanceRef:
    """Pointer to a placed instance of a Component inside a parent.

    An instance is a live copy of a main Component (or a specific
    variant of a ComponentSet) nested within another node — typically
    a pattern frame. ``component_node_id`` records which main
    Component this instance derives from; ``parent_node_id`` records
    the containing node (the pattern frame). Setting variant/exposed
    properties on the instance is done via ``set_instance_property``.
    """
    file_key: str
    node_id: str
    component_node_id: str = ""
    parent_node_id: str = ""
    name: str = ""


@dataclass(frozen=True)
class CodeConnectRef:
    """Pointer to a Code Connect attachment on a Component."""
    component_node_id: str
    mapping_id: str
    framework: str = "react"


@dataclass(frozen=True)
class PublishRef:
    """Pointer to a library publish event."""
    file_key: str
    publish_id: str
    changelog: str = ""


# ---------------------------------------------------------------------------
# Value dataclasses — for arguments that are richer than a string
# ---------------------------------------------------------------------------

# A variable's resolved value for a given mode. Matches Figma's
# Variables API value shape; aliases use {"type": "VARIABLE_ALIAS",
# "id": variable_id}.
VariableValue = Any  # str | float | bool | dict for alias references


@dataclass(frozen=True)
class Paint:
    """A single paint applied to a paint style."""
    paint_type: PaintType
    # SOLID: {"r": 0..1, "g": 0..1, "b": 0..1, "a": 0..1}
    # GRADIENT_*: stops + transform; structurally the same as Figma API
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TextStyleProperties:
    """Properties of a text style."""
    font_family: str
    font_size: float
    font_weight: int = 400
    line_height_pct: float | None = None
    letter_spacing: float | None = None
    text_decoration: Literal["NONE", "UNDERLINE", "STRIKETHROUGH"] = "NONE"


@dataclass(frozen=True)
class Effect:
    """A single effect (shadow, blur, etc.)."""
    effect_type: Literal["DROP_SHADOW", "INNER_SHADOW", "LAYER_BLUR", "BACKGROUND_BLUR"]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComponentGeometry:
    """Bounding box + content for an empty component frame."""
    width: float = 100.0
    height: float = 100.0
    background_color: str | None = None


@dataclass(frozen=True)
class VariantSpec:
    """A single variant within a ComponentSet."""
    name: str
    properties: dict[str, str]
    geometry: ComponentGeometry = field(default_factory=ComponentGeometry)


@dataclass(frozen=True)
class CodeConnectMapping:
    """Code Connect attachment payload."""
    framework: Literal["react", "vue", "swift", "kotlin", "html"]
    import_statement: str
    code_example: str
    props_mapping: dict[str, dict[str, str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SessionToken:
    """Opaque identifier for a transport session."""
    adapter_id: str
    started_at: str
    token: str


@dataclass(frozen=True)
class SessionResult:
    """Outcome of committing a transport session.

    ``adaptive_observation`` (v1.4.0-beta.1) carries the rate-limit
    telemetry + concurrency recommendation when the REST transport
    ran with an :class:`AdaptiveConcurrency` policy attached to its
    :class:`BatchPolicy`. ``None`` for all other adapters and for
    REST runs without an adaptive policy (backward compatible).
    """
    token: SessionToken
    operations_applied: int
    operations_failed: int
    artifacts: dict[str, str] = field(default_factory=dict)
    adaptive_observation: "ConcurrencyObservation | None" = None


# ---------------------------------------------------------------------------
# Capability declaration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AuthRequirement:
    """What credentials does an adapter need?"""
    needs_credentials: bool
    credential_kind: Literal["none", "figma-pat", "oidc", "ambient-mcp"] = "none"
    environment_variable: str | None = None


# ---------------------------------------------------------------------------
# The Protocol itself
# ---------------------------------------------------------------------------

@runtime_checkable
class TransportAdapter(Protocol):
    """The contract every transport adapter implements.

    Implementations may raise :class:`CapabilityUnsupportedError` from
    any method they don't support. The router consults
    :meth:`supports` before dispatch to avoid round-trips on
    operations that are known unreachable through this channel.

    All operations are **session-scoped**: call :meth:`begin_session`,
    then operations, then :meth:`commit_session` (or
    :meth:`rollback_session`). A stub adapter may make sessions a
    no-op; a buffered adapter (REST) ships the batch on commit;
    a capture adapter (PluginCapture) emits the consolidated script
    on commit.
    """

    # --- Identity & capability -------------------------------------------

    def adapter_id(self) -> str:
        """Stable adapter identifier (e.g. ``'rest-v1'``)."""
        ...

    def supports(self, operation_name: str) -> bool:
        """Does this adapter implement the named operation?

        ``operation_name`` is the method name as a string (e.g.
        ``"create_variable_collection"``).
        """
        ...

    def authentication_required(self) -> AuthRequirement:
        """Declare credential requirements."""
        ...

    # --- Lifecycle --------------------------------------------------------

    def begin_session(self) -> SessionToken: ...
    def commit_session(self, token: SessionToken) -> SessionResult: ...
    def rollback_session(self, token: SessionToken) -> None: ...

    # --- File operations --------------------------------------------------

    def create_file(self, *, name: str, file_kind: FileKind) -> FileRef: ...
    def get_file(self, *, key: str) -> FileRef: ...
    def publish_library(self, *, file_key: str, changelog: str) -> PublishRef: ...

    # --- Variable operations ----------------------------------------------

    def create_variable_collection(
        self, *, file_key: str, name: str, modes: list[str]
    ) -> CollectionRef: ...

    def get_variable_collection(
        self, *, file_key: str, name: str
    ) -> CollectionRef | None: ...

    def create_variable(
        self, *,
        collection_ref: CollectionRef,
        name: str,
        type: VariableType,
        values_per_mode: dict[str, VariableValue],
    ) -> VariableRef: ...

    def update_variable(
        self, *,
        variable_ref: VariableRef,
        values_per_mode: dict[str, VariableValue],
    ) -> None: ...

    def create_alias_reference(
        self, *,
        source_var: VariableRef,
        target_var: VariableRef,
        mode_id: str,
    ) -> None: ...

    # --- Style operations -------------------------------------------------

    def create_paint_style(
        self, *, file_key: str, name: str, paints: list[Paint]
    ) -> StyleRef: ...

    def create_text_style(
        self, *, file_key: str, name: str, properties: TextStyleProperties
    ) -> StyleRef: ...

    def create_effect_style(
        self, *, file_key: str, name: str, effects: list[Effect]
    ) -> StyleRef: ...

    # --- Component operations ---------------------------------------------

    def create_page(self, *, file_key: str, name: str) -> PageRef: ...

    def create_component(
        self, *, page_ref: PageRef, name: str,
        geometry: ComponentGeometry,
    ) -> ComponentRef: ...

    def create_component_set(
        self, *, page_ref: PageRef, name: str,
        variants: list[VariantSpec],
    ) -> ComponentSetRef: ...

    def set_component_property(
        self, *, component_ref: ComponentRef, key: str, value: Any,
    ) -> None: ...

    def import_svg_as_component(
        self, *, page_ref: PageRef, name: str,
        svg_source: str, canonical_size: tuple[int, int],
    ) -> ComponentRef: ...

    def update_component_description(
        self, *, component_ref: ComponentRef,
        description: str, doc_links: list[str],
    ) -> None: ...

    # --- Instance composition (v1.2.0) ------------------------------------

    def place_instance(
        self, *, parent_ref: ComponentRef, component_ref: ComponentRef,
        position: tuple[int, int],
    ) -> InstanceRef: ...

    def set_instance_property(
        self, *, instance_ref: InstanceRef, key: str, value: str,
    ) -> None: ...

    # --- Code Connect -----------------------------------------------------

    def attach_code_connect(
        self, *, component_ref: ComponentRef,
        mapping: CodeConnectMapping,
    ) -> CodeConnectRef: ...

    def list_code_connect(
        self, *, file_key: str
    ) -> list[CodeConnectRef]: ...


# ---------------------------------------------------------------------------
# Helper: operation registry (used by router + capability matrix tests)
# ---------------------------------------------------------------------------

#: All transport operation names. Stable from v1.1.0; the list is
#: append-only.
TRANSPORT_OPERATIONS: tuple[str, ...] = (
    # File-level
    "create_file",
    "get_file",
    "publish_library",
    # Variables
    "create_variable_collection",
    "get_variable_collection",
    "create_variable",
    "update_variable",
    "create_alias_reference",
    # Styles
    "create_paint_style",
    "create_text_style",
    "create_effect_style",
    # Components
    "create_page",
    "create_component",
    "create_component_set",
    "set_component_property",
    "import_svg_as_component",
    "update_component_description",
    # Instance composition (v1.2.0)
    "place_instance",
    "set_instance_property",
    # Code Connect
    "attach_code_connect",
    "list_code_connect",
)


__all__ = [
    # Protocol
    "TransportAdapter",
    "TRANSPORT_OPERATIONS",
    # Reference types
    "FileRef", "PageRef", "CollectionRef", "VariableRef",
    "StyleRef", "ComponentRef", "ComponentSetRef", "InstanceRef",
    "CodeConnectRef", "PublishRef",
    # Value types
    "Paint", "TextStyleProperties", "Effect",
    "ComponentGeometry", "VariantSpec", "CodeConnectMapping",
    # Lifecycle
    "SessionToken", "SessionResult", "AuthRequirement",
    # Enums
    "FileKind", "VariableType", "PaintType",
]
