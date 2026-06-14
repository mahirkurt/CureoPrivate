"""Gate 11 — Each page in publishable files (except Cover/Candidates/etc.)
must have a heading frame at the top.

A heading frame is a top-level child of the page CANVAS that:
  * is a FRAME (or COMPONENT) type, AND
  * contains a TEXT child whose text matches the page name, OR
  * has a name suggesting it's a header (e.g. "Section Header", "Title",
    or matches the page name)

Without section headers, designers landing on a page see raw component
spreads with no editorial framing — discoverability suffers.
"""

from __future__ import annotations

from typing import Iterable

from ..context import MultiFileFigmaContext
from ..models import GateResult, iter_pages, collect_text_content
from ..gates_registry import get_gate, register_gate


SKIP_PAGES = {"Cover", "Overview", "Welcome", "Candidates", "Deprecated"}

HEADER_NAME_HINTS = ("header", "title", "section")


def _is_header_frame(child: dict, page_name: str) -> bool:
    """Heuristic: a top-level FRAME/COMPONENT is a header if its name or
    contained text reflects the page identity."""
    if child.get("type") not in {"FRAME", "COMPONENT", "GROUP"}:
        return False
    child_name = (child.get("name") or "").lower()
    if any(hint in child_name for hint in HEADER_NAME_HINTS):
        return True
    if page_name.lower() in child_name:
        return True
    # Fallback: scan visible text in the child for the page name
    text = collect_text_content(child)
    if page_name.lower() in (text or "").lower():
        return True
    return False


def _has_heading(page: dict) -> bool:
    """Inspect ``page.children[:3]`` for a header frame."""
    page_name = page.get("name", "")
    for child in (page.get("children") or [])[:3]:
        if _is_header_frame(child, page_name):
            return True
    return False


def _publishable_pages(file_doc: dict) -> Iterable[dict]:
    """Yield pages that should have a section header — skips Cover and
    other special pages."""
    for page in iter_pages(file_doc):
        if page.get("name") in SKIP_PAGES:
            continue
        if not (page.get("children") or []):
            continue  # empty pages are out of scope
        yield page


@register_gate(11)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    res = GateResult(gate=get_gate(11))
    for role, f in ctx.iter_publishable_files():
        for page in _publishable_pages(f.document):
            res.checked_count += 1
            if not _has_heading(page):
                res.add(
                    f"[{role}] page {page.get('name', '<unnamed>')!r} "
                    f"has no section header at top",
                    role=role
                )
    res.mark_fail()
    return res
