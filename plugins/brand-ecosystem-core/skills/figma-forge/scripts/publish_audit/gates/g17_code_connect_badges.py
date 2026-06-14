"""Gate 17 — Component descriptions should reference Code Connect status.

This is an **informational** gate, not a publish blocker. It surfaces which
components have a Code Connect badge in their description and which don't,
so the team can prioritize CC mapping work.

Accepted badge tokens (in description text):
    🟢 / GREEN / linked         — Code Connect mapping live
    🟡 / YELLOW / partial       — Mapping in progress / partial
    ⚪ / WHITE / unlinked        — No mapping
    🔵 / BLUE / N/A             — Component intentionally code-less

A component is considered "badged" if any of these tokens appears in its
description. The gate reports the percentage badged across the audit
target, and lists individual unbadged components as findings (severity:
info, not blocking).
"""

from __future__ import annotations

from ..context import MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate


BADGE_TOKENS = ("🟢", "🟡", "⚪", "🔵", "GREEN", "YELLOW", "WHITE", "BLUE", "N/A", "linked")


def _has_cc_badge(description: str) -> bool:
    """Return True iff ``text`` contains a Code Connect badge token or status synonym."""
    if not description:
        return False
    haystack = description.upper()
    return any(tok.upper() in haystack for tok in BADGE_TOKENS)


@register_gate(17)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Surface components that lack a Code Connect status badge in their description."""
    res = GateResult(gate=get_gate(17))
    total = 0
    badged = 0
    for role, f in ctx.iter_publishable_files():
        # Component sets are the canonical unit; only count standalone
        # components (those not inside a set) to avoid double-counting.
        for sid, cset in f.component_sets.items():
            total += 1
            desc = cset.get("description") or ""
            if _has_cc_badge(desc):
                badged += 1
            else:
                res.add(f"[{role}] {cset.get('name', sid)} — no Code Connect status badge",
                        role=role)
        for cid, comp in f.components.items():
            # Skip components that belong to a set we already counted.
            if comp.get("componentSetId"):
                continue
            total += 1
            desc = comp.get("description") or ""
            if _has_cc_badge(desc):
                badged += 1
            else:
                res.add(f"[{role}] {comp.get('name', cid)} — no Code Connect status badge",
                        role=role)
    res.checked_count = total
    if total > 0:
        pct = 100.0 * badged / total
        res.notes.append(f"Code Connect badge coverage: {badged}/{total} ({pct:.1f}%)")
    # G17 is info-severity — failures do not block release.
    # We still flip status to 'fail' so it appears in the audit summary,
    # but the auditor's strict-mode logic does not act on info-severity fails.
    res.mark_fail()
    return res
