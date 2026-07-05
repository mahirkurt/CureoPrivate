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
    "(1) TAM-FİLO — wire'lı 14 hukuk MCP + 3 companion (Yargı mcp__Yarg__* / Open Law mcp__Open_Law__* / "
    "Ansvar mcp__Ansvar__*) her sorguda çalışır; companion'lar tam-filonun ZORUNLU üyeleridir "
    "(Yargı↔G5 içtihat, Open Law↔G6 CELEX doğrulama, Ansvar↔Mod7 58-yargı) — bağlıyken tetiklenmiş "
    "bağlamda atlanmaları G0 ihlalidir; bağlı değillerse ilgili kapı CONDITIONAL + manifesto beyanı. "
    "Çıktı G0 kapsam manifestosu taşır (server → hit/empty/degraded/skipped-with-reason; sessiz "
    "atlama = FAIL). "
    "(2) NO-FABRICATION — kanun/CELEX/AYM/Yargıtay/PMID asla uydurulmaz; her atıf MCP-doğrulanmış "
    "(evidence_ledger). (3) SCOPE GUARD — yalnız mevzuat reformu; bireysel dava (SGK red/AYM başvuru), "
    "malpraktis → saglik-sigorta/onko-erisim; promosyon denetimi → promo-censor. (4) ZORUNLU DELEGASYON — "
    "klinik kanıt → evidentia (her klinik-boyutlu sorguda); atıf-adli + TR dil → sci-audit (her çıktıda). "
    "Bu plugin'ler KURULUYKEN atlanmaları G0 ihlalidir; degrade yalnız gerçek yoklukta meşrudur. "
    "(5) İNSAN DENETİMİ her çıktıda zorunlu. (6) BAĞLAM EKONOMİSİ — tam-filo ham veri ana pencereye "
    "girmez: ≤4 paralel distiller alt-ajanı (Tier 1) + anamnesis RAG substratı (Tier 2, büyük tam-metin "
    "ingest→bounded query) + kanonik cache (bir-kez-getir) + kör-getirme-yok chunking. "
    "shared/context-economy-contract.md."
)

# Delegasyon plugin'leri — kurulum algılama (deterministik, fail-open).
DELEGATION_PLUGINS = {"evidentia": "evidentia@", "sci-audit": "sci-audit@"}


def detect_installed_plugins():
    """~/.claude/settings.json enabledPlugins içinden evidentia/sci-audit kurulumunu algılar.

    Amaç: 'kurulu → çağrı ZORUNLU / kurulu değil → graceful degrade' ayrımını oturum başında
    kanıta bağlamak. Okuma başarısızlığı = bilinmiyor (boş dict) — fail-open.
    """
    try:
        path = os.path.expanduser("~/.claude/settings.json")
        with open(path, encoding="utf-8") as fh:
            enabled = json.load(fh).get("enabledPlugins", {})
        return {
            name: any(k.startswith(prefix) and v for k, v in enabled.items())
            for name, prefix in DELEGATION_PLUGINS.items()
        }
    except Exception:
        return {}


def main():
    try:
        sys.stdin.read()  # SessionStart payload'ını boşalt (kullanılmıyor)
    except Exception:
        pass

    missing = [f"{c} (${v})" for c, v in GATED.items() if not os.environ.get(v)]
    ctx = CONVENTIONS

    plugins = detect_installed_plugins()
    if plugins:
        installed = [n for n, ok in plugins.items() if ok]
        absent = [n for n, ok in plugins.items() if not ok]
        if installed:
            ctx += (
                "\n[preflight/delegasyon] KURULU: " + ", ".join(installed)
                + " → bağlam tetiklendiğinde çağrılmaları ZORUNLU (evidentia: her klinik-boyutlu "
                "sorgu; sci-audit: her reform-modu çıktısı). Atlanmaları G0 ihlalidir; manifesto "
                "satırları 'skipped: plugin kurulu değil' YAZILAMAZ."
            )
        if absent:
            ctx += (
                "\n[preflight/delegasyon] KURULU DEĞİL: " + ", ".join(absent)
                + " → graceful degrade meşru; manifestoda 'skipped: plugin kurulu değil' beyan et, "
                "eksik katmanı uydurma."
            )

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
