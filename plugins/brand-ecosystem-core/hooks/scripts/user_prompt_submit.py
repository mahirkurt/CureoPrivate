#!/usr/bin/env python3
"""UserPromptSubmit hook — regulated-sector + final-lock intent routing.

Deterministically injects constraint reminders BEFORE the model sees the prompt:
  • Regulated-sector signals (pharma / medical device / cosmetic) → remind to
    load pharma-naming-constraints + run the brand-collision scan.
  • "Final / lock / present / publish" intent → require the verification
    package (two-source domain, diversity gate, naive perception, TM pre-scan)
    before any name is presented as final.

Pure additive context. Never blocks. Output: hookSpecificOutput.additionalContext.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import hooks_enabled, inject_context, read_event  # noqa: E402

REGULATED = re.compile(
    r"\b(pharma|ilaç|ilac|biotech|biyotek|medtech|medical\s*device|tıbbi\s*cihaz|"
    r"tibbi\s*cihaz|kozmetik|cosmetic|FDA|EMA|TİTCK|TITCK|INN|molecule|molekül|"
    r"oncology|onkoloj|hematolog|klinik|clinical)\b", re.IGNORECASE)

FINAL_LOCK = re.compile(
    r"\b(final|finalize|kilitle|lock|kesinleş|sun|present|yayınla|yayinla|"
    r"publish|onayla|approve|seç(?:tim)?|karar\s*ver)\b", re.IGNORECASE)

REG_NOTE = (
    "[brand-hook] Regüle-sektör sinyali algılandı → pharma modülü ZORUNLU: "
    "references/pharma-naming-constraints.md yükle; her finalist için "
    "inn_stem_collision.py + pharma_brand_collision.py (INN stem ÖTESİ marka "
    "çakışması) çalıştır; 'çakışma yok' tek aramadan verilmez, provenance + "
    "'resmî TM araştırması gerekli' zorunlu."
)

LOCK_NOTE = (
    "[brand-hook] Final/kilitle niyeti algılandı → doğrulama-paketi ŞART: bir "
    "isim ancak (a) domain iki-kaynak confirmed (RDAP+WHOIS/GoDaddy MCP; asla "
    "tek-sinyal 'müsait'), (b) çeşitlilik kapısı PASS, (c) naif ilk-okuma "
    "koşuldu, (d) TM ön-tarama koşuldu — tümü tamamlanınca 'final' sunulur. "
    "Eksikse önce doğrulamayı tamamla."
)


def main() -> None:
    if not hooks_enabled():
        sys.exit(0)
    event = read_event()
    prompt = (event.get("prompt") or "").strip()
    if not prompt:
        sys.exit(0)
    notes = []
    if REGULATED.search(prompt):
        notes.append(REG_NOTE)
    if FINAL_LOCK.search(prompt):
        notes.append(LOCK_NOTE)
    if notes:
        inject_context("UserPromptSubmit", "\n".join(notes))
    sys.exit(0)


if __name__ == "__main__":
    main()
