#!/usr/bin/env python3
"""SessionStart hook — inject the brand-maker v2.1 verification doctrine.

Makes the no-fabrication + two-source-verification discipline active from the
first turn, so a naming run never silently falls back to optimistic
"available/clean" assertions.

Output contract: hookSpecificOutput.additionalContext.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import hooks_enabled, inject_context, read_event  # noqa: E402

DOCTRINE = (
    "brand-ecosystem-core v2.1 doğrulama doktrini (aktif): "
    "(1) DOMAIN — hiçbir alan adı iki uyuşan canlı kaynak (GoDaddy MCP ya da "
    "RDAP+WHOIS) olmadan 'müsait' YAZILMAZ; tek kaynak=provisional, kaynak "
    "yok=unverified — asla varsayımsal 'müsait'. (2) MARKA — pharma finalisti "
    "için marka çakışması 'yok/temiz' tek yüzeysel aramadan verilemez; "
    "provenance + 'resmî TM araştırması gerekli' zorunlu (scripts/"
    "pharma_brand_collision.py). (3) ÇEŞİTLİLİK — finalist kümesi tek morfem "
    "ailesiyse (ör. hep -anza/-anta) shortlist_diversity_check.py FAIL verir → "
    "ikinci tur zorunlu, aynı aile yeniden karıştırılmaz. (4) ALGI — her "
    "finalist için naif ilk-okuma (niyet-kök≠algı-kök, ör. Ortanza→'orta'=vasat) "
    "FIRST-CLASS yüzeye çıkar. (5) SKOR — telaffuz-kolaylığı ile marka-gücü AYRI "
    "eksenler; 95-100 yığını bir ayrım hatasıdır. Her 'müsait/temiz/anlam' "
    "iddiası kaynak + confirmed|provisional|unverified etiketi taşır."
)


def main() -> None:
    if not hooks_enabled():
        sys.exit(0)
    _ = read_event()
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    context = DOCTRINE
    # Prefer the canonical doctrine file if present (single source of truth).
    doc = os.path.join(root, "skills", "brand-verify", "references",
                       "verification-doctrine.md")
    if doc and os.path.exists(doc):
        try:
            with open(doc, "r", encoding="utf-8") as fh:
                loaded = fh.read().strip()
                if loaded:
                    context = loaded
        except Exception:
            pass
    inject_context("SessionStart", context)


if __name__ == "__main__":
    main()
