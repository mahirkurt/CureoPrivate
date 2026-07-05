#!/usr/bin/env python3
"""lex-sanitas SessionStart preflight — tam-filo credential check + konvansiyon enjeksiyonu.

lex-sanitas'ın 12 gated hukuk/regülasyon connector'ı Bearer anahtarını süreç ortamından çözer
(Doppler-injected: `doppler run -- claude`). Bir anahtar yoksa o connector çağrı anında 401 döner
ve tam-filo (G0) kapsamı o katmanda `skipped: anahtar yok` olarak degrade eder — çıktı DURMAZ,
asla uydurma yapılmaz. Bu hook: (a) eksik anahtarları bir kez yüzeye çıkarır, (b) her oturumda
lex-sanitas çekirdek konvansiyonlarını (tam-filo · no-fabrication · Scope Guard · insan-denetimi)
kısa bir additionalContext olarak enjekte eder. Fail-open.
"""
import json
import os
import sys

# Gated hukuk/regülasyon connector → env var (bkz. commands/lex-connectors.md anahtar haritası).
GATED = {
    "mevzuat": "MEVZUAT_MCP_API_KEY",
    "resmi-gazete": "RESMI_GAZETE_MCP_API_KEY",
    "tbmm": "TBMM_MCP_API_KEY",
    "saglikbakanligi": "SAGLIK_MCP_API_KEY",
    "detsis": "DETSIS_MCP_API_KEY",
    "health-policy": "HEALTH_POLICY_MCP_API_KEY",
    "german-law": "GERMAN_LAW_MCP_API_KEY",
    "ich-guidelines": "ICH_MCP_API_KEY",
    "intl-treaty": "INTL_TREATY_MCP_API_KEY",
    "eudamed": "EUDAMED_MCP_API_KEY",
    "oecd": "OECD_MCP_API_KEY",
    "yok-akademik": "YOK_AKADEMIK_MCP_API_KEY",
    "anamnesis": "ANAMNESIS_MCP_API_KEY",
}

CONVENTIONS = (
    "[lex-sanitas] Türkiye sağlık mevzuatı reform protokolü aktif. Çekirdek invaryantlar: "
    "(1) TAM-FİLO — wire'lı 14 hukuk MCP + bağlı companion her sorguda çalışır; çıktı G0 kapsam "
    "manifestosu taşır (server → hit/empty/degraded/skipped-with-reason; sessiz atlama = FAIL). "
    "(2) NO-FABRICATION — kanun/CELEX/AYM/Yargıtay/PMID asla uydurulmaz; her atıf MCP-doğrulanmış "
    "(evidence_ledger). (3) SCOPE GUARD — yalnız mevzuat reformu; bireysel dava (SGK red/AYM başvuru), "
    "malpraktis → saglik-sigorta/onko-erisim; promosyon denetimi → promo-censor. (4) DELEGASYON — "
    "klinik kanıt → evidentia; atıf-adli + TR dil → sci-audit (varsa; yoksa graceful degrade). "
    "(5) İNSAN DENETİMİ her çıktıda zorunlu. (6) BAĞLAM EKONOMİSİ — tam-filo ham veri ana pencereye "
    "girmez: ≤4 paralel distiller alt-ajanı (Tier 1) + anamnesis RAG substratı (Tier 2, büyük tam-metin "
    "ingest→bounded query) + kanonik cache (bir-kez-getir) + kör-getirme-yok chunking. "
    "shared/context-economy-contract.md."
)


def main():
    try:
        sys.stdin.read()  # SessionStart payload'ını boşalt (kullanılmıyor)
    except Exception:
        pass

    missing = [f"{c} (${v})" for c, v in GATED.items() if not os.environ.get(v)]
    ctx = CONVENTIONS
    if missing:
        ctx += (
            "\n[preflight] Şu hukuk connector anahtar(lar)ı süreç ortamında YOK: "
            + ", ".join(missing)
            + ". Bunlar çağrı anında 401 döner ve kapsam manifestosunda 'skipped: anahtar yok' "
            "olarak beyan edilir (tam-filo degrade — çıktı durmaz). Çözüm: oturumu "
            "`doppler run -p cureohub -c dev_personal -- claude` ile başlat → tüm ${VAR}'lar "
            "otomatik enjekte olur. (Public server'lar — titck, mevzuat-bilgisi — etkilenmez.)"
        )

    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
