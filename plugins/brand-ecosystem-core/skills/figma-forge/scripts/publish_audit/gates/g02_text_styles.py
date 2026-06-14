"""Gate 2 — Every TEXT node must reference a text style."""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult, iter_text_nodes
from ..gates_registry import get_gate, register_gate


@register_gate(2)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Detached typography (text without a style) is a publish blocker."""
    res = GateResult(gate=get_gate(2))
    for role, f in ctx.iter_publishable_files():
        for node, page in iter_text_nodes(f.document):
            res.checked_count += 1
            if not (node.get("styles") or {}).get("text"):
                res.add(f"[{role}] {page} → {node.get('name', '<unnamed>')}", role=role)
    res.mark_fail()
    return res
