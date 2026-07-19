#!/usr/bin/env python3
"""Stop hook — provenance self-check (no-fabrication GUARANTEE).

At end of turn, inspects the assistant's last message. If it presents a domain
as AVAILABLE ("müsait"/"available") or a name/mark as CLEAN ("temiz"/"no
collision"/"çakışma yok") WITHOUT a nearby verification-status/provenance marker
(confirmed/provisional/unverified/RDAP/WHOIS/GoDaddy/source/kaynak/"resmî TM
araştırması gerekli"), it CONTINUES the turn and asks the model to add the
provenance or downgrade the claim. This turns the v2.1 output-contract
(A + E + F) from an aspiration into a guarantee.

Stop contract: {"decision":"block","reason":...} does NOT reject the turn — it
continues it with the reason. stop_hook_active breaks the loop (prevents an
infinite continuation).
"""
from __future__ import annotations

import os
import re
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import emit_json, hooks_enabled, last_assistant_message, read_event  # noqa: E402

# A positive availability / cleanliness claim.
AVAILABLE_CLAIM = re.compile(
    r"\b(müsait|musait|available|boşta|bosta)\b", re.IGNORECASE)
CLEAN_CLAIM = re.compile(
    r"\b(temiz|clean|çakışma\s*yok|cakisma\s*yok|no\s*collision|collision[- ]free|"
    r"conflict[- ]free)\b", re.IGNORECASE)

# Nearby verification-status / provenance markers that make the claim legitimate.
PROVENANCE = re.compile(
    r"\b(confirmed|provisional|unverified|doğrulan|dogrulan|RDAP|WHOIS|GoDaddy|"
    r"kaynak|source|provenance|zaman\s*damgas|timestamp|resmî\s*TM|resmi\s*TM|"
    r"formal\s*TM|araştırması\s*gerekli|arastirmasi\s*gerekli|live_tm_checked|"
    r"ön-tarama|on-tarama|iki[- ]kaynak|two[- ]source)\b", re.IGNORECASE)

# Domain / brand context words that indicate the claim is about availability.
DOMAIN_BRAND = re.compile(
    r"\.(com|io|ai|co|net|org|dev|app)\b|\bdomain\b|\balan\s*ad|\bmarka\b|"
    r"\btrademark\b|\bfinalist\b", re.IGNORECASE)

WINDOW = 240  # chars around a claim to search for a provenance marker


def find_unverified_claims(text: str) -> List[str]:
    """Return snippets of positive availability/clean claims lacking provenance.

    Pure function (unit-testable). A claim is flagged only when:
      • it is an availability/clean assertion, AND
      • it appears in a domain/brand context, AND
      • no provenance/status marker occurs within WINDOW chars.
    """
    if not text:
        return []
    flagged = []
    for pat in (AVAILABLE_CLAIM, CLEAN_CLAIM):
        for m in pat.finditer(text):
            start = max(0, m.start() - WINDOW)
            end = min(len(text), m.end() + WINDOW)
            window = text[start:end]
            if not DOMAIN_BRAND.search(window):
                continue  # not an availability-of-a-name claim
            if PROVENANCE.search(window):
                continue  # legitimately sourced/labelled
            snippet = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            flagged.append(snippet.strip())
    return flagged


REASON = (
    "PROVENANCE SELF-CHECK (v2.1 no-fabrication guarantee): the reply presents a "
    "domain/mark as available or clean WITHOUT a verification-status marker. "
    "Fix before finishing: for each such claim add its source + status "
    "(confirmed | provisional | unverified) — domains need two agreeing live "
    "sources (GoDaddy MCP or RDAP+WHOIS) to be called 'müsait'; a single source "
    "is 'provisional'; no source is 'unverified' (never 'müsait'). Pharma-brand "
    "'no collision' must carry provenance + 'resmî TM araştırması gerekli'. "
    "Unverifiable claims: downgrade the wording, do not drop the caveat.\n\n"
    "Offending snippet(s):\n"
)


def main() -> None:
    if not hooks_enabled():
        sys.exit(0)
    event = read_event()
    if event.get("stop_hook_active"):
        sys.exit(0)  # already continued once — don't loop
    text = last_assistant_message(event)
    claims = find_unverified_claims(text)
    if claims:
        bullets = "\n".join(f"  • …{c}…" for c in claims[:6])
        emit_json({"decision": "block", "reason": REASON + bullets})
    sys.exit(0)


if __name__ == "__main__":
    main()
