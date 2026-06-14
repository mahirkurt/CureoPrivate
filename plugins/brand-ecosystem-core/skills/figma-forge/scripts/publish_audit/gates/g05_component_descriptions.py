"""Gate 5 — Components and component sets must have meaningful descriptions."""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate


MIN_DESCRIPTION_LEN = 30


@register_gate(5)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Walk components + component sets across all files; check description length."""
    res = GateResult(gate=get_gate(5))
    for role, f in ctx.iter_publishable_files():
        for cid, comp in f.components.items():
            res.checked_count += 1
            desc = comp.get("description") or ""
            if len(desc) < MIN_DESCRIPTION_LEN:
                res.add(
                    f"[{role}] {comp.get('name', cid)} — description too short "
                    f"({len(desc)}/{MIN_DESCRIPTION_LEN} chars)",
                    role=role
                )
        for sid, cset in f.component_sets.items():
            res.checked_count += 1
            desc = cset.get("description") or ""
            if len(desc) < MIN_DESCRIPTION_LEN:
                res.add(
                    f"[{role}] {cset.get('name', sid)} (set) — description too short "
                    f"({len(desc)}/{MIN_DESCRIPTION_LEN} chars)",
                    role=role
                )
    res.mark_fail()
    return res
