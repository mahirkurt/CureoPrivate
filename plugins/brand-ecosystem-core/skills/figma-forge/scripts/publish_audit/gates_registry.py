"""
Gate catalog and dispatch.

The 19 publish-readiness gates are registered here. Each gate has a stable
ID and a checker function that consumes a ``MultiFileFigmaContext`` and
returns a ``GateResult``.

Gate implementations live in ``gates/g<NN>_<name>.py`` modules and register
themselves via the ``@register_gate`` decorator. This keeps each gate's
logic isolated and individually testable.

v0.2.0 expansion notes:
  * v0.1.x: 4 implemented (G1, G2, G5, G16), 15 stubbed.
  * v0.2.0 Sprint 1: +6 gates (G3, G4, G10, G12, G17, G18) → 10 active.
  * v0.2.0 Sprint 2: +5 gates (G7, G8, G9, G11, G19) → 15 active.
  * v0.2.0 Sprint 3: +4 gates (G6, G13, G14, G15) → 19 active. Release.
"""

from __future__ import annotations

from typing import Callable

from .models import Gate, GateResult
from .context import MultiFileFigmaContext


GateChecker = Callable[[MultiFileFigmaContext], GateResult]


# ----------------------------------------------------------------------------
# Catalog — single source of truth for gate definitions
# ----------------------------------------------------------------------------

GATE_CATALOG: list[Gate] = [
    Gate(1, "All paints come from a variable", "error",
         "Every solid fill must reference a variable; no hard-coded hex.",
         "Iterate failing nodes; rebind to the appropriate variable."),
    Gate(2, "All text uses a text style", "error",
         "Every text node must reference a text style (no detached typography).",
         "Apply the appropriate text style; create one in Foundations if missing."),
    Gate(3, "No orphan styles", "warn",
         "Published styles must be referenced at least once.",
         "Delete unused styles, or apply them to relevant nodes."),
    Gate(4, "No missing variable references", "error",
         "Every variable alias must resolve to an existing target.",
         "Restore the missing target, or rebind to an existing variable."),
    Gate(5, "All components have descriptions", "warn",
         "Component descriptions must be ≥30 characters.",
         "Author a 1–2 sentence description per component."),
    Gate(6, "All components have keywords", "warn",
         "Component keyword list must be non-empty.",
         "Add 4–8 keywords per component."),
    Gate(7, "Every variant axis is fully populated", "error",
         "No gaps in the variant Cartesian product.",
         "Add missing variant instances; document disabled combinations explicitly."),
    Gate(8, "Component naming follows convention", "warn",
         "Names match the selected convention (Carbon/Material/BEM/Custom).",
         "Rename non-conforming components via batch."),
    Gate(9, "Variant property naming follows convention", "warn",
         "Property keys camelCase; values lowercase short.",
         "Rename via Figma variant editor or plugin."),
    Gate(10, "Foundations file has cover page", "warn",
         "Foundations file has a 'Cover' page with DS name + version.",
         "Auto-generate via skill or hand-craft."),
    Gate(11, "Each component family has a section header", "warn",
         "Every page in Components/Patterns has a heading frame at top.",
         "Add a heading frame using the H2 text style."),
    Gate(12, "No unpublished local styles in a publishable file", "warn",
         "Every style is published, except those in Candidates page.",
         "Publish the style, or move it to Candidates."),
    Gate(13, "Effect styles are bound to elevation tokens", "warn",
         "Effect styles used on Surfaces match elevation tokens.",
         "Rebind to the proper elevation effect style."),
    Gate(14, "All icons are components", "error",
         "Icon-like nodes must be COMPONENT or INSTANCE, never raw vectors.",
         "Wrap each icon as a Figma component."),
    Gate(15, "All icons follow size/grid convention", "warn",
         "Icons have square bounding boxes at {16,20,24,32,48}.",
         "Resize and align icons to the convention."),
    Gate(16, "Library has at least one mode per collection", "error",
         "Every variable collection has at least one mode named Light/Default.",
         "Add the missing mode and populate values."),
    Gate(17, "Component descriptions reference Code Connect status", "info",
         "Optional: descriptions include 🟢/🟡/⚪ Code Connect badge.",
         "Run CODE_CONNECT mode or add badges manually."),
    Gate(18, "License/version/contact metadata in cover page", "warn",
         "Cover contains DS version, license, contact.",
         "Add metadata block to cover."),
    Gate(19, "No detached instance overrides outside Candidates", "warn",
         "Component instances in published pages have clean overrides.",
         "Add missing variant, or revert override."),
]


# ----------------------------------------------------------------------------
# Registration — gates self-register at module-import time
# ----------------------------------------------------------------------------

_CHECKERS: dict[int, GateChecker] = {}


def register_gate(gate_id: int) -> Callable[[GateChecker], GateChecker]:
    """Decorator to register a gate checker function under its numeric ID."""
    def decorator(fn: GateChecker) -> GateChecker:
        """Register ``fn`` as the checker for the enclosing gate_id."""
        if gate_id in _CHECKERS:
            raise RuntimeError(f"gate {gate_id} already registered")
        _CHECKERS[gate_id] = fn
        return fn
    return decorator


def get_gate(gate_id: int) -> Gate:
    """Return the static Gate definition for ``gate_id`` (1..19)."""
    for g in GATE_CATALOG:
        if g.id == gate_id:
            return g
    raise KeyError(f"unknown gate id: {gate_id}")


def has_checker(gate_id: int) -> bool:
    """Return True iff a checker function has been registered for ``gate_id``."""
    return gate_id in _CHECKERS


def run_gate(gate_id: int, ctx: MultiFileFigmaContext) -> GateResult:
    """Execute the registered checker for ``gate_id``, or return a skip result."""
    if gate_id not in _CHECKERS:
        return GateResult(gate=get_gate(gate_id), status="skip",
                          notes=["Gate not implemented in this build."])
    return _CHECKERS[gate_id](ctx)


def run_all_gates(ctx: MultiFileFigmaContext) -> list[GateResult]:
    """Execute every gate in the catalog, in numeric order."""
    return [run_gate(g.id, ctx) for g in GATE_CATALOG]


def implemented_gate_count() -> int:
    """How many gates have registered checkers."""
    return len(_CHECKERS)


# ----------------------------------------------------------------------------
# Side-effect imports — each gate module registers itself on import.
# Order matches the gate IDs; new gates added in v0.2.0 Sprint 1.
# ----------------------------------------------------------------------------

from .gates import (  # noqa: E402, F401  — imported for side effects
    g01_paint_bindings,
    g02_text_styles,
    g03_orphan_styles,
    g04_missing_variable_refs,
    g05_component_descriptions,
    g06_component_keywords,
    g07_variant_matrix,
    g08_component_naming,
    g09_variant_property_naming,
    g10_foundations_cover,
    g11_section_headers,
    g12_published_styles,
    g13_effect_elevation,
    g14_icons_are_components,
    g15_icon_size_grid,
    g16_modes_per_collection,
    g17_code_connect_badges,
    g18_cover_metadata,
    g19_instance_overrides,
)
