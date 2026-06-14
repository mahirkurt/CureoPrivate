"""Gate 10 — The Foundations file must have a 'Cover' page.

A cover page is the canonical landing zone for designers opening the
library. Without it, the file opens into raw variable lists, which is
hostile to discovery.

This gate is registry-aware:
  * If the registry declares a ``foundations`` role, check that specific
    file for a Cover page.
  * In single-file mode, treat the primary file as the foundations target
    if its name contains "Foundations" (case-insensitive); otherwise
    skip with a note.

The gate only checks that *a page named Cover exists*. G18 separately
verifies the cover's content (DS name, version, contact).
"""

from __future__ import annotations

from ..context import FigmaFile, MultiFileFigmaContext
from ..models import GateResult, find_page
from ..gates_registry import get_gate, register_gate


COVER_PAGE_NAMES = ("Cover", "Overview", "Welcome")  # accepted synonyms


def _has_cover(f: FigmaFile) -> bool:
    """True if the file declares any of the accepted cover-page names."""
    return any(find_page(f.document, name) is not None for name in COVER_PAGE_NAMES)


def _foundations_target(ctx: MultiFileFigmaContext) -> tuple[str, FigmaFile] | None:
    """Locate the file that should carry the Cover page.

    Registry mode: returns the file at ``foundations`` role.
    Single-file mode: returns the primary file iff its name suggests it
    is the foundations file; otherwise returns None.
    """
    if ctx.registry is not None:
        f = ctx.get("foundations")
        return ("foundations", f) if f is not None else None
    primary = ctx.primary
    if "foundation" in (primary.name or "").lower():
        return ("primary", primary)
    return None


@register_gate(10)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Confirm the Foundations file declares a Cover/Overview/Welcome page."""
    res = GateResult(gate=get_gate(10))
    target = _foundations_target(ctx)
    if target is None:
        res.status = "n_a"
        res.notes.append(
            "No 'foundations' role declared in registry, and primary file "
            "name does not suggest a foundations file — gate skipped."
        )
        return res
    role, f = target
    res.checked_count = 1
    if not _has_cover(f):
        accepted = ", ".join(COVER_PAGE_NAMES)
        res.add(
            f"[{role}] file {f.name!r} has no cover page "
            f"(accepted names: {accepted})",
            role=role
        )
    res.mark_fail()
    return res
