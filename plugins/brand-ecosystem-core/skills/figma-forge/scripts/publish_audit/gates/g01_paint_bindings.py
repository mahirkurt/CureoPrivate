"""Gate 1 — All SOLID paints must be bound to a variable."""

from __future__ import annotations

from typing import Iterator

from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, walk_nodes
from ..gates_registry import get_gate, register_gate


def _iter_solid_fills(f: FigmaFile) -> Iterator[tuple[str, dict, dict]]:
    """Yield ``(page_name, node, fill_dict)`` for every SOLID fill outside Candidates."""
    for node, page in walk_nodes(f.document):
        if (page or "") == "Candidates":
            continue
        for fill in node.get("fills") or []:
            if fill.get("type") == "SOLID":
                yield page or "", node, fill


def _is_foundation_swatch(file_name: str, node: dict) -> bool:
    """Foundation-swatch nodes are allowed to carry literal (un-bound) colors."""
    return "Foundations" in (file_name or "") or "Swatches" in (node.get("name") or "")


@register_gate(1)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Every SOLID fill across every publishable file must bind to a variable."""
    res = GateResult(gate=get_gate(1))
    for role, f in ctx.iter_publishable_files():
        for page, node, fill in _iter_solid_fills(f):
            res.checked_count += 1
            if (fill.get("boundVariables") or {}).get("color"):
                continue
            if node.get("type") == "RECTANGLE" or _is_foundation_swatch(f.name, node):
                continue
            res.add(f"[{role}] {page} → {node.get('name', '<unnamed>')}", role=role)
    res.mark_fail()
    return res
