"""Gate 12 — Styles in publishable files must be published.

An unpublished style is invisible to library consumers but still bloats the
file. Common cause: the style was created in a Candidates page during
exploration but never moved out.

We allow unpublished styles iff the underlying style is located on a page
explicitly named "Candidates" (which by convention is a sandbox for
work-in-progress styles).

The Figma REST API exposes a ``remote`` flag (True = imported from another
library, so not our concern) and the consumer's local styles arrive without
a ``remote: true`` field. The ``Style.published`` boolean is only set when
the local style has been published. Absent means unpublished.
"""

from __future__ import annotations

from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, walk_nodes
from ..gates_registry import get_gate, register_gate


def _style_node_pages(f: FigmaFile) -> dict[str, str]:
    """Map style_id → page_name where the style was first defined.

    Walks the document tree; whenever a node's ``styles`` map references a
    style_id we haven't seen yet, we associate that style with the current
    page. This is heuristic — style definitions don't have an explicit
    "lives on page X" field in the REST payload — but works for the common
    case where styles are defined in the file they're applied in.
    """
    location: dict[str, str] = {}
    for node, page in walk_nodes(f.document):
        node_styles = node.get("styles") or {}
        if not isinstance(node_styles, dict):
            continue
        for sid in node_styles.values():
            if isinstance(sid, str) and sid and sid not in location:
                location[sid] = page or ""
    return location


@register_gate(12)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Flag local styles that are not marked published, outside the Candidates exemption page."""
    res = GateResult(gate=get_gate(12))
    for role, f in ctx.iter_publishable_files():
        if not f.styles:
            continue
        page_of = _style_node_pages(f)
        for sid, style_meta in f.styles.items():
            res.checked_count += 1
            # Imported styles from other libraries are out of scope.
            if style_meta.get("remote"):
                continue
            # The Figma payload sets `published: True` for published local
            # styles. Treat missing or False as unpublished.
            if style_meta.get("published"):
                continue
            # Styles on the Candidates page are explicitly exempt.
            if page_of.get(sid) == "Candidates":
                continue
            name = style_meta.get("name", sid)
            style_type = style_meta.get("styleType", "?")
            res.add(f"[{role}] {name} ({style_type}) — local style is unpublished",
                    role=role)
    res.mark_fail()
    return res
