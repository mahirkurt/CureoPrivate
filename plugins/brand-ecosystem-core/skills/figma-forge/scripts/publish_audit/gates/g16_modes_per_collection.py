"""Gate 16 — Every variable collection must declare at least one mode."""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate


@register_gate(16)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """A collection without modes can't resolve any variable value."""
    res = GateResult(gate=get_gate(16))
    for role, f in ctx.iter_publishable_files():
        if not f.variable_collections:
            res.notes.append(
                f"[{role}] No variable collections (Variables API may be unavailable on this plan)."
            )
            continue
        for cid, coll in f.variable_collections.items():
            res.checked_count += 1
            if not coll.get("modes"):
                res.add(f"[{role}] {coll.get('name', cid)} — no modes defined", role=role)
    res.mark_fail()
    return res
