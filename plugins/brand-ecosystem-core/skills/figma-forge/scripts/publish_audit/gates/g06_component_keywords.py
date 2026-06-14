"""Gate 6 — Component descriptions must declare keywords.

Figma's component search is keyword-driven. Without keywords, designers
can only find a component by its exact name — breaking discoverability
for the entire library.

Detection format (convention-driven):

  Description block must contain a line matching ``Keywords:`` followed
  by ≥4 comma-separated keyword tokens. The line may appear anywhere in
  the description. Token examples:

      Keywords: button, action, cta, submit, primary

  Alternative accepted format (Figma's own pluginData convention):
  ``tags: ...`` or ``Tags:`` — recognized as a synonym.

Minimum threshold: ``MIN_KEYWORDS = 4`` per component. Tunable via the
constant for future ``--config`` integration.

Like G5, this gate iterates every component AND every component-set; for
component children of a set we skip (the set inherits keywords from
itself).
"""

from __future__ import annotations

import re

from ..context import MultiFileFigmaContext
from ..models import GateResult
from ..gates_registry import get_gate, register_gate


MIN_KEYWORDS = 4
KEYWORDS_RE = re.compile(
    r"^\s*(?:keywords?|tags?|etiketler?|anahtar\s*kelimeler?)\s*[:：]\s*(.+)$",
    re.IGNORECASE | re.MULTILINE
)


def _extract_keywords(description: str) -> list[str]:
    """Return the list of keyword tokens declared in ``description``.

    Searches for a ``Keywords:``-style line and splits the trailing text
    on commas. Empty tokens and whitespace are trimmed. Returns [] when
    no keyword line is present.
    """
    if not description:
        return []
    match = KEYWORDS_RE.search(description)
    if not match:
        return []
    raw = match.group(1)
    return [tok.strip() for tok in raw.split(",") if tok.strip()]


@register_gate(6)
def check(ctx: MultiFileFigmaContext) -> GateResult:
    """Verify every component's description contains a `Keywords:` line with ≥4 tokens."""
    res = GateResult(gate=get_gate(6))
    for role, f in ctx.iter_publishable_files():
        # ComponentSets first — the canonical unit
        for sid, cset in f.component_sets.items():
            res.checked_count += 1
            keywords = _extract_keywords(cset.get("description") or "")
            if len(keywords) < MIN_KEYWORDS:
                res.add(
                    f"[{role}] {cset.get('name', sid)} (set) — "
                    f"{len(keywords)} keyword(s), expected ≥{MIN_KEYWORDS}",
                    role=role
                )
        # Standalone components (not children of a set)
        for cid, comp in f.components.items():
            if comp.get("componentSetId"):
                continue
            res.checked_count += 1
            keywords = _extract_keywords(comp.get("description") or "")
            if len(keywords) < MIN_KEYWORDS:
                res.add(
                    f"[{role}] {comp.get('name', cid)} — "
                    f"{len(keywords)} keyword(s), expected ≥{MIN_KEYWORDS}",
                    role=role
                )
    res.mark_fail()
    return res
