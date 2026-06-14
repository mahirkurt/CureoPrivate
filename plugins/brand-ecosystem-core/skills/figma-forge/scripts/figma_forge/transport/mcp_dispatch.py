"""figma-forge MCP dispatch registry — v1.3.0-alpha.2.

The **single source of truth** for how each transport operation
dispatches through the Figma MCP server. Three downstream consumers
derive their behavior from this registry at import time:

1. :mod:`figma_forge.transport.mcp_cursor` — emits the per-operation
   tool-call descriptor using ``REGISTRY[operation].mcp_tool`` and
   ``REGISTRY[operation].mechanism``.
2. :mod:`figma_forge.transport.capability_matrix` — derives the
   MCP-Cursor column's capability level from
   ``REGISTRY[operation].mechanism`` (``native`` → ``supported``,
   ``use_figma_nl`` → ``supported-nl``).
3. :mod:`figma_forge.transport.plan_validation` — derives the per-tool
   required-argument set from
   ``REGISTRY[operation].required_args`` for native entries.

Promoting an operation from ``use_figma_nl`` to ``native`` is a
**one-line registry edit** here; the three consumers pick up the
change automatically at the next import. This eliminates the
three-place drift that the v1.2 code had baked in.

This module is **internal**. It is not exported on
``figma_forge.__all__``; operators should not mutate the registry at
runtime. The contract is: figma-forge maintainers update this file
when Figma's MCP write surface evolves, and ship a new release.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DispatchMechanism = Literal["native", "use_figma_nl"]


@dataclass(frozen=True)
class McpDispatchSpec:
    """A single operation's MCP dispatch specification.

    Attributes
    ----------
    operation:
        The figma-forge transport operation name (e.g.
        ``"create_variable"``).
    mcp_tool:
        The Figma MCP tool to call. For ``native`` mechanism this is
        a dedicated tool (e.g. ``"Figma:create_new_file"``); for
        ``use_figma_nl`` this is the natural-language fallback
        (``"Figma:use_figma"``).
    mechanism:
        ``"native"`` when a deterministic dedicated tool exists,
        ``"use_figma_nl"`` otherwise.
    required_args:
        For ``native`` entries: the argument keys the MCP tool
        requires. Used by :func:`validate_mcp_plan` to enforce
        argument shape. For ``use_figma_nl`` entries: empty
        (instruction string carries the intent).
    capability_note:
        The human-readable note attached to the capability matrix
        cell — surfaced in coverage diagnostics.
    """

    operation: str
    mcp_tool: str
    mechanism: DispatchMechanism
    required_args: tuple[str, ...] = ()
    capability_note: str = ""


# ---------------------------------------------------------------------------
# The registry — single source of truth.
# ---------------------------------------------------------------------------
#
# To promote an operation from ``use_figma_nl`` to ``native`` when Figma
# ships a new granular MCP tool:
#
#   1. Change ``mechanism`` from ``"use_figma_nl"`` to ``"native"``.
#   2. Change ``mcp_tool`` from ``"Figma:use_figma"`` to the new
#      tool's name.
#   3. Fill ``required_args`` with the tool's argument keys.
#   4. Update ``capability_note`` to describe the new behavior.
#
# No other file needs to change. The three downstream consumers
# (mcp_cursor, capability_matrix, plan_validation) derive their
# behavior from this single record.

REGISTRY: dict[str, McpDispatchSpec] = {

    # --- Native dispatch (5 entries) -----------------------------------
    "create_file": McpDispatchSpec(
        operation="create_file", mcp_tool="Figma:create_new_file",
        mechanism="native", required_args=("name", "file_kind"),
        capability_note="create_new_file native",
    ),
    "get_file": McpDispatchSpec(
        operation="get_file", mcp_tool="Figma:get_metadata",
        mechanism="native", required_args=("key",),
        capability_note="get_metadata native",
    ),
    "get_variable_collection": McpDispatchSpec(
        operation="get_variable_collection",
        mcp_tool="Figma:get_variable_defs",
        mechanism="native", required_args=("file_key", "name"),
        capability_note="get_variable_defs native",
    ),
    "attach_code_connect": McpDispatchSpec(
        operation="attach_code_connect",
        mcp_tool="Figma:send_code_connect_mappings",
        mechanism="native",
        required_args=("node_id", "component_name", "framework",
                       "import_statement", "code_example",
                       "props_mapping"),
        capability_note="send_code_connect_mappings native",
    ),
    "list_code_connect": McpDispatchSpec(
        operation="list_code_connect",
        mcp_tool="Figma:get_code_connect_map",
        mechanism="native", required_args=("file_key",),
        capability_note="get_code_connect_map native",
    ),

    # --- Natural-language dispatch (16 entries) ------------------------
    "create_variable_collection": McpDispatchSpec(
        operation="create_variable_collection",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (collection name + modes)",
    ),
    "create_variable": McpDispatchSpec(
        operation="create_variable",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (variable name + values)",
    ),
    "update_variable": McpDispatchSpec(
        operation="update_variable",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL",
    ),
    "create_alias_reference": McpDispatchSpec(
        operation="create_alias_reference",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (alias reference)",
    ),
    "create_paint_style": McpDispatchSpec(
        operation="create_paint_style",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (paint style)",
    ),
    "create_text_style": McpDispatchSpec(
        operation="create_text_style",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (text style)",
    ),
    "create_effect_style": McpDispatchSpec(
        operation="create_effect_style",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (effect style)",
    ),
    "create_page": McpDispatchSpec(
        operation="create_page",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (page creation)",
    ),
    "create_component": McpDispatchSpec(
        operation="create_component",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (component frame)",
    ),
    "create_component_set": McpDispatchSpec(
        operation="create_component_set",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (ComponentSet + variants)",
    ),
    "set_component_property": McpDispatchSpec(
        operation="set_component_property",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (component property)",
    ),
    "import_svg_as_component": McpDispatchSpec(
        operation="import_svg_as_component",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (SVG import)",
    ),
    "update_component_description": McpDispatchSpec(
        operation="update_component_description",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (description)",
    ),
    "place_instance": McpDispatchSpec(
        operation="place_instance",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (instance placement)",
    ),
    "set_instance_property": McpDispatchSpec(
        operation="set_instance_property",
        mcp_tool="Figma:use_figma", mechanism="use_figma_nl",
        capability_note="via use_figma NL (instance property)",
    ),
}


# ---------------------------------------------------------------------------
# Derived views — consumed by mcp_cursor, capability_matrix, plan_validation
# ---------------------------------------------------------------------------

def mcp_tool_for_operation(operation: str) -> tuple[str, str] | None:
    """Return ``(mcp_tool, mechanism)`` for an operation, or None."""
    spec = REGISTRY.get(operation)
    if spec is None:
        return None
    return spec.mcp_tool, spec.mechanism


def native_required_args() -> dict[str, tuple[str, ...]]:
    """Build the ``mcp_tool → required_args`` view used by the plan
    validator. Native entries only."""
    return {
        spec.mcp_tool: spec.required_args
        for spec in REGISTRY.values()
        if spec.mechanism == "native"
    }


def capability_level_for_operation(operation: str) -> str | None:
    """Return the capability matrix level for an operation, or None
    when the operation is not handled by MCP-Cursor."""
    spec = REGISTRY.get(operation)
    if spec is None:
        return None
    return "supported" if spec.mechanism == "native" else "supported-nl"


__all__ = [
    "DispatchMechanism", "McpDispatchSpec", "REGISTRY",
    "mcp_tool_for_operation", "native_required_args",
    "capability_level_for_operation",
]
