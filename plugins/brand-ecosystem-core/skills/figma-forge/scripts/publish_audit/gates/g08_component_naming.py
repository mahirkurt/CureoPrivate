"""Gate 8 — Component and component-set names must match the declared naming
convention.

Reads the convention from the LibraryRegistry; in single-file mode without
a registry, the gate skips with a note (we have no way to know which
convention to enforce).
"""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate
from ..naming import get_validator


@register_gate(8)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Validate component names against the registry's selected naming convention."""
    res = GateResult(gate=get_gate(8))
    if ctx.registry is None:
        res.status = "n_a"
        res.notes.append(
            "No library-registry: cannot determine naming convention; "
            "G8 skipped. Provide --library-registry to enable."
        )
        return res
    validator = get_validator(ctx.registry.naming_convention)
    res.notes.append(f"Convention: {validator.convention_name}")
    for role, f in ctx.iter_publishable_files():
        for cid, comp in f.components.items():
            # Children of a ComponentSet have variant-encoded names
            # ("Type=Primary, Size=Md") that don't follow the component
            # naming convention — skip them.
            if comp.get("componentSetId"):
                continue
            res.checked_count += 1
            name = comp.get("name", "")
            result = validator.validate_component(name)
            if not result.ok:
                res.add(f"[{role}] component {name!r}: {result.reason}", role=role)
        for sid, cset in f.component_sets.items():
            res.checked_count += 1
            name = cset.get("name", "")
            result = validator.validate_component(name)
            if not result.ok:
                res.add(f"[{role}] component-set {name!r}: {result.reason}",
                        role=role)
    res.mark_fail()
    return res
