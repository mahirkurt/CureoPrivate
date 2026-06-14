"""Gate 3 — Published styles must be referenced at least once.

Strategy: build the set of all declared style IDs from ``file.styles``, then
walk the entire node tree counting references. Any style ID not referenced
is reported as an orphan.

Styles appear on nodes in two shapes:
  1. ``node.styles`` map (text style, fill style, stroke style, effect style),
     which is a dict of role → style_id.
  2. ``node.fills[].boundStyleId``, ``node.strokes[].boundStyleId`` — less
     common but seen on overridden instance children.

We collect both shapes for completeness.
"""

from __future__ import annotations

from typing import Iterable

from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, walk_nodes
from ..gates_registry import get_gate, register_gate


def _node_style_dict_refs(node: dict) -> Iterable[str]:
    """Yield style IDs from a node's ``styles`` field (dict-of-purpose-to-id)."""
    node_styles = node.get("styles")
    if not isinstance(node_styles, dict):
        return
    for sid in node_styles.values():
        if isinstance(sid, str) and sid:
            yield sid


def _node_bound_style_refs(node: dict) -> Iterable[str]:
    """Yield ``boundStyleId`` values from a node's fill/stroke/effect entries."""
    for collection_key in ("fills", "strokes", "effects"):
        for item in node.get(collection_key) or []:
            bound = item.get("boundStyleId")
            if isinstance(bound, str) and bound:
                yield bound


def _collect_referenced_style_ids(f: FigmaFile) -> set[str]:
    """Return the set of style IDs that appear as a reference anywhere in the document."""
    refs: set[str] = set()
    for node, _page in walk_nodes(f.document):
        refs.update(_node_style_dict_refs(node))
        refs.update(_node_bound_style_refs(node))
    return refs


@register_gate(3)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """A published style with zero references bloats the library and confuses consumers."""
    res = GateResult(gate=get_gate(3))
    for role, f in ctx.iter_publishable_files():
        declared = set(f.styles.keys())
        if not declared:
            continue
        referenced = _collect_referenced_style_ids(f)
        # Styles in `f.styles` use node_id keys (e.g. "1:23"); the references
        # collected above use the same node_id form, so direct set diff works.
        orphans = declared - referenced
        for sid in sorted(orphans):
            res.checked_count += 1
            style_meta = f.styles[sid]
            style_name = style_meta.get("name", sid)
            style_type = style_meta.get("styleType", "?")
            res.add(f"[{role}] {style_name} ({style_type}) — no references found",
                    role=role)
        # Even passing styles count toward checked_count for transparency.
        res.checked_count += len(declared - orphans)
    res.mark_fail()
    return res
