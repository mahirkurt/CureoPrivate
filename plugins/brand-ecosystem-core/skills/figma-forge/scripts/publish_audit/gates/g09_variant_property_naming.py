"""Gate 9 — Variant property keys and values must match the declared
naming convention.

Property keys (axis names like ``size``, ``state``) should be camelCase
or BEM lowercase-kebab; values (``md``, ``hover``, ``primary``) should be
lowercase short tokens.

The gate reuses :func:`analyze_component_set` from the variants module —
the same axes dictionary that G7 uses for matrix coverage analysis is
used here for the naming check, avoiding duplicate parsing.
"""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate
from ..naming import get_validator
from ..variants import analyze_component_set


@register_gate(9)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Validate variant axis keys and values against the registry's naming convention."""
    res = GateResult(gate=get_gate(9))
    if ctx.registry is None:
        res.status = "n_a"
        res.notes.append("No registry → no convention → G9 skipped.")
        return res
    validator = get_validator(ctx.registry.naming_convention)
    res.notes.append(f"Convention: {validator.convention_name}")
    for role, f in ctx.iter_publishable_files():
        children_by_set: dict[str, list[dict]] = {}
        for cid, comp in f.components.items():
            set_id = comp.get("componentSetId")
            if set_id:
                children_by_set.setdefault(set_id, []).append(comp)
        for set_id, set_meta in f.component_sets.items():
            children = children_by_set.get(set_id, [])
            matrix = analyze_component_set(set_id, set_meta, children)
            set_name = matrix.component_set_name
            # Validate axis keys
            for axis_key in matrix.axes:
                res.checked_count += 1
                result = validator.validate_variant_property_key(axis_key)
                if not result.ok:
                    res.add(
                        f"[{role}] {set_name}: axis key {axis_key!r} — {result.reason}",
                        role=role
                    )
                # Validate values within the axis
                for value in matrix.axes[axis_key]:
                    res.checked_count += 1
                    vresult = validator.validate_variant_property_value(value)
                    if not vresult.ok:
                        res.add(
                            f"[{role}] {set_name}: {axis_key}={value!r} — {vresult.reason}",
                            role=role
                        )
    res.mark_fail()
    return res
