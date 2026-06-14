"""figma-forge transport capability matrix — v1.1.0-alpha.

Machine-readable declaration of which adapter implements which
operation, plus the rationale text used in CLI help output and in
the RFC document. The router consults this matrix at routing time;
tests verify each adapter's declared :meth:`supports` output matches
the matrix exactly (no silent drift between declaration and
implementation).

The matrix is **stable from v1.1.0 onwards** in the additive sense:
new operations or new adapters can be added in minor releases;
existing rows/columns retain their meaning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CapabilityLevel = Literal[
    "supported",            # ✓ — deterministic native channel operation
    "supported-enterprise", # E — requires Figma Enterprise plan
    "supported-nl",         # N — via use_figma natural-language (best-effort,
                            #     non-deterministic; MCP-Cursor only)
    "unsupported",          # ✗ — channel physically can't do this
    "deferred-v1_2",        # ? — planned for v1.2
]


@dataclass(frozen=True)
class CapabilityCell:
    level: CapabilityLevel
    notes: str = ""


# Adapter identifiers — string-keyed for stability
ADAPTER_STUB = "stub"
ADAPTER_PLUGIN_CAPTURE = "plugin-capture"
ADAPTER_REST = "rest-v1"
ADAPTER_MCP_CURSOR = "mcp-cursor"  # v1.2 — emits MCP tool-call plans


#: The canonical matrix. Indexed by (operation, adapter).
#:
#: ``supported`` — adapter implements the operation deterministically
#: ``supported-enterprise`` — implemented but requires Enterprise plan
#: ``supported-nl`` — implemented via use_figma natural-language
#:   instruction (MCP-Cursor only; best-effort, non-deterministic)
#: ``unsupported`` — technically impossible through this channel
#: ``deferred-v1_2`` — adapter exists, operation deferred
CAPABILITY_MATRIX: dict[tuple[str, str], CapabilityCell] = {
    # ----------------------------------------------------------------
    # File-level
    # ----------------------------------------------------------------
    ("create_file", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_file", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("unsupported",
        "Plugin scripts only modify the current file; cannot create new."),
    ("create_file", ADAPTER_REST):           CapabilityCell("supported-enterprise",
        "POST /v1/files requires Enterprise plan + scoped PAT."),
    ("create_file", ADAPTER_MCP_CURSOR): CapabilityCell("supported",
        "Figma:create_new_file — native MCP tool."),

    ("get_file", ADAPTER_STUB):           CapabilityCell("supported"),
    ("get_file", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("unsupported"),
    ("get_file", ADAPTER_REST):           CapabilityCell("supported"),
    ("get_file", ADAPTER_MCP_CURSOR): CapabilityCell("supported",
        "Figma:get_metadata — native read."),

    ("publish_library", ADAPTER_STUB):           CapabilityCell("supported"),
    ("publish_library", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("unsupported",
        "Library publishing has no API; manual UI action only."),
    ("publish_library", ADAPTER_REST):           CapabilityCell("unsupported",
        "No REST endpoint for library publishing."),
    ("publish_library", ADAPTER_MCP_CURSOR):     CapabilityCell("unsupported"),

    # ----------------------------------------------------------------
    # Variables — Foundations core
    # ----------------------------------------------------------------
    ("create_variable_collection", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_variable_collection", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_variable_collection", ADAPTER_REST):           CapabilityCell("supported-enterprise",
        "POST /v1/files/:key/variables — Enterprise only."),
    ("create_variable_collection", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("get_variable_collection", ADAPTER_STUB):           CapabilityCell("supported"),
    ("get_variable_collection", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("get_variable_collection", ADAPTER_REST):           CapabilityCell("supported",
        "GET /v1/files/:key/variables/local — read-only, all plans."),
    ("get_variable_collection", ADAPTER_MCP_CURSOR): CapabilityCell("supported",
        "Figma:get_variable_defs — native read."),

    ("create_variable", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_variable", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_variable", ADAPTER_REST):           CapabilityCell("supported-enterprise"),
    ("create_variable", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("update_variable", ADAPTER_STUB):           CapabilityCell("supported"),
    ("update_variable", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("update_variable", ADAPTER_REST):           CapabilityCell("supported-enterprise"),
    ("update_variable", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("create_alias_reference", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_alias_reference", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported",
        "Inherits v0.3.1 G13 cross-collection rebind walker pattern."),
    ("create_alias_reference", ADAPTER_REST):           CapabilityCell("supported-enterprise"),
    ("create_alias_reference", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    # ----------------------------------------------------------------
    # Styles — Foundations secondary (Figma styles, not Variables)
    # ----------------------------------------------------------------
    ("create_paint_style", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_paint_style", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_paint_style", ADAPTER_REST):           CapabilityCell("unsupported",
        "Figma styles are not exposed in REST API."),
    ("create_paint_style", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("create_text_style", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_text_style", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_text_style", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("create_text_style", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("create_effect_style", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_effect_style", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_effect_style", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("create_effect_style", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    # ----------------------------------------------------------------
    # Components / pages
    # ----------------------------------------------------------------
    ("create_page", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_page", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_page", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("create_page", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("create_component", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_component", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_component", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("create_component", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("create_component_set", ADAPTER_STUB):           CapabilityCell("supported"),
    ("create_component_set", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("create_component_set", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("create_component_set", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("set_component_property", ADAPTER_STUB):           CapabilityCell("supported"),
    ("set_component_property", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("set_component_property", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("set_component_property", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("import_svg_as_component", ADAPTER_STUB):           CapabilityCell("supported"),
    ("import_svg_as_component", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported",
        "Inherits v0.3.1 G14 idempotent component creation pattern."),
    ("import_svg_as_component", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("import_svg_as_component", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Figma:upload_assets + use_figma natural-language."),

    ("update_component_description", ADAPTER_STUB):           CapabilityCell("supported"),
    ("update_component_description", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("update_component_description", ADAPTER_REST):           CapabilityCell("unsupported"),
    ("update_component_description", ADAPTER_MCP_CURSOR): CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    # ----------------------------------------------------------------
    # Instance composition (v1.2.0)
    # ----------------------------------------------------------------
    ("place_instance", ADAPTER_STUB):           CapabilityCell("supported"),
    ("place_instance", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported",
        "figma.createInstance(component) + appendChild into the parent frame."),
    ("place_instance", ADAPTER_REST):           CapabilityCell("unsupported",
        "Figma REST API has no write endpoint for creating instances."),
    ("place_instance", ADAPTER_MCP_CURSOR):     CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    ("set_instance_property", ADAPTER_STUB):           CapabilityCell("supported"),
    ("set_instance_property", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported",
        "instance.setProperties({...}) on the placed instance."),
    ("set_instance_property", ADAPTER_REST):           CapabilityCell("unsupported",
        "Figma REST API cannot set instance properties."),
    ("set_instance_property", ADAPTER_MCP_CURSOR):     CapabilityCell("supported-nl",
        "Via Figma:use_figma natural-language instruction."),

    # ----------------------------------------------------------------
    # Code Connect
    # ----------------------------------------------------------------
    ("attach_code_connect", ADAPTER_STUB):           CapabilityCell("supported"),
    ("attach_code_connect", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("unsupported",
        "Code Connect is attached via REST or Figma's CLI, not via plugin."),
    ("attach_code_connect", ADAPTER_REST):           CapabilityCell("supported"),
    ("attach_code_connect", ADAPTER_MCP_CURSOR): CapabilityCell("supported",
        "Figma:send_code_connect_mappings — native MCP tool."),

    ("list_code_connect", ADAPTER_STUB):           CapabilityCell("supported"),
    ("list_code_connect", ADAPTER_PLUGIN_CAPTURE): CapabilityCell("supported"),
    ("list_code_connect", ADAPTER_REST):           CapabilityCell("supported"),
    ("list_code_connect", ADAPTER_MCP_CURSOR): CapabilityCell("supported",
        "Figma:get_code_connect_map — native read."),
}


def adapters_supporting(operation: str) -> list[str]:
    """Return the list of adapters that claim to support ``operation``.

    "Support" includes ``supported``, ``supported-enterprise``, and
    ``supported-nl`` (natural-language via use_figma); excludes
    ``unsupported`` and ``deferred-v1_2``.

    Used by the router to enumerate candidate adapters in operator
    preference order.
    """
    return sorted(
        adapter
        for (op, adapter), cell in CAPABILITY_MATRIX.items()
        if op == operation and cell.level in (
            "supported", "supported-enterprise", "supported-nl"
        )
    )


def supported_operations(adapter_id: str) -> list[str]:
    """Inverse query: list operations an adapter supports."""
    return sorted(
        op
        for (op, adapter), cell in CAPABILITY_MATRIX.items()
        if adapter == adapter_id and cell.level in (
            "supported", "supported-enterprise", "supported-nl"
        )
    )


def capability(operation: str, adapter_id: str) -> CapabilityCell:
    """Look up the cell for one operation × adapter pair.

    Raises ``KeyError`` if the pair is not declared — callers should
    treat missing pairs as a programming error (matrix is the
    authoritative declaration).
    """
    return CAPABILITY_MATRIX[(operation, adapter_id)]


# ---------------------------------------------------------------------------
# Registry-driven derivation for the MCP-Cursor column.
#
# Every MCP-Cursor cell whose operation appears in mcp_dispatch.REGISTRY
# is **overridden** here from that single source of truth at import
# time. Cells absent from the registry (e.g. publish_library — MCP
# explicitly unsupported) are left as declared in the literal above.
#
# This makes promotion-from-NL-to-native a one-line registry edit:
# change the registry, and both ``mcp_cursor._MCP_TOOL_FOR_OPERATION``
# and this matrix's MCP column update automatically.
# ---------------------------------------------------------------------------

def _apply_registry_overrides() -> None:
    from .mcp_dispatch import REGISTRY as _REGISTRY
    for op, spec in _REGISTRY.items():
        level: CapabilityLevel = (
            "supported" if spec.mechanism == "native" else "supported-nl"
        )
        CAPABILITY_MATRIX[(op, ADAPTER_MCP_CURSOR)] = CapabilityCell(
            level, spec.capability_note,
        )


_apply_registry_overrides()


__all__ = [
    "CapabilityCell",
    "CapabilityLevel",
    "CAPABILITY_MATRIX",
    "ADAPTER_STUB",
    "ADAPTER_PLUGIN_CAPTURE",
    "ADAPTER_REST",
    "ADAPTER_MCP_CURSOR",
    "adapters_supporting",
    "supported_operations",
    "capability",
]
