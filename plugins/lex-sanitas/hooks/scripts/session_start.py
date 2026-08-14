#!/usr/bin/env python3
"""lex-sanitas SessionStart preflight — canlı filo prob'u + konvansiyon enjeksiyonu.

v3.5.0: anahtar haritası artık hardcoded DEĞİL — `fleet.lock.json`'dan gelir
(`tools/gen_fleet.py` üretir, kaynak `fleet.yaml`). Preflight gerçek MCP
`initialize` prob'u yapar (24 saat cache'li) ve iki hâli AYIRIR:

  auth_missing → anahtar süreç ortamında yok  → MEŞRU DEGRADE
  unauthorized → sunucu 401/403 verdi         → YAPILANDIRMA ARIZASI

Bu ayrım olmasaydı ikisi de "o katman çalışmıyor" diye görünürdü — 2026-08-02
TİTCK kapılanmasının aylarca sessizce yaşamasının sebebi tam olarak buydu.

Sağlıklı filoda preflight bölümü SESSİZDİR (yalnız konvansiyonlar enjekte edilir).
Fail-open: prob veya lock çökerse yalnız konvansiyonlar gider, oturum durmaz.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import fleet_probe
except Exception:  # prob modülü yoksa/bozuksa preflight yine çalışır
    fleet_probe = None

ROOT = Path(__file__).resolve().parent.parent.parent

# Lock okunamazsa kullanılacak asgari delegasyon haritası (fail-open).
DELEGATION_FALLBACK = {"evidentia": "evidentia@", "sci-audit": "sci-audit@"}


def conventions(lock) -> str:
    """Çekirdek invaryantlar — sayılar lock'tan enterpole edilir, hardcode YOK."""
    counts = (lock or {}).get("counts", {})
    n_srv = counts.get("servers", "?")
    comps = (lock or {}).get("companions", [])
    comp_desc = " / ".join(
        "{} {}*".format(c["name"], c["tool_prefixes"][0]) for c in comps
    ) or "companion listesi okunamadı"
    return (
        "[lex-sanitas] Türkiye sağlık mevzuatı reform protokolü aktif. "
        "Çekirdek invaryantlar: "
        "(1) TAM-FİLO — wire'lı {n} hukuk MCP + {nc} companion ({cd}) her sorguda "
        "çalışır; companion'lar tam-filonun ZORUNLU üyeleridir — bağlıyken "
        "tetiklenmiş bağlamda atlanmaları G0 ihlalidir; bağlı değillerse ilgili kapı "
        "CONDITIONAL + manifesto beyanı; bağlam-dışı companion satırı dürüstçe "
        "'skipped: mod için N/A' yazılır (satır hiç yazılmamazlık edilemez). "
        "Connector önekleri yüzeye göre mcp__<Ad>__* veya mcp__claude_ai_<Ad>__* "
        "görünebilir — ada göre eşleştir. Çıktı G0 kapsam manifestosu taşır "
        "(server → hit/empty/degraded/skipped-with-reason; sessiz atlama = FAIL). "
        "(2) NO-FABRICATION — kanun/CELEX/AYM/Yargıtay/PMID/YÖK-Tez asla uydurulmaz; "
        "her atıf MCP-doğrulanmış (evidence_ledger). YÖK-Tez atıfları artık wire'lı "
        "`mcp__yoktez__*` ile doğrulanır (tez no/başlık/yazar) → G7 companion'a bağlı "
        "değil, hard PASS. "
        "(3) SCOPE GUARD — yalnız mevzuat reformu; bireysel dava (SGK red/AYM "
        "başvuru), malpraktis → saglik-sigorta/onko-erisim; promosyon denetimi → "
        "promo-censor. "
        "(4) ZORUNLU DELEGASYON — klinik kanıt → evidentia (her klinik-boyutlu "
        "sorguda); atıf-adli + TR dil → sci-audit (her çıktıda). Bu plugin'ler "
        "KURULUYKEN atlanmaları G0 ihlalidir; degrade yalnız gerçek yoklukta meşrudur. "
        "(5) İNSAN DENETİMİ her çıktıda zorunlu. "
        "(6) BAĞLAM EKONOMİSİ — tam-filo ham verisi ana pencereye girmez: ≤4 paralel "
        "distiller alt-ajanı (Tier 1, shard-kısıtlı araç kümesiyle) + anamnesis RAG "
        "substratı (Tier 2, büyük tam-metin ingest→bounded query) + kanonik cache "
        "(bir-kez-getir) + kör-getirme-yok chunking. "
        "(7) TAM-METİN ŞELALESİ — doktrin tam metni için önce lisanslı band "
        "(openathens Tier 3): metin/RAG için oa_fetch_fulltext, orijinal provider PDF için "
        "oa_fetch_pdf(doi|url). annas-reader (Tier 4) YALNIZ o denendikten sonra, açık "
        "gerekçeyle ve YALNIZ ANALİZ için; bounded reader veya orijinal PDF/EPUB/etc. "
        "için download_document(id=DOI|MD5). Kısa-ömürlü resource_link derhal tüketilir, "
        "kalıcı kaynak diye cache'lenmez; DOI/MD5+SHA-256 evidence_ledger'a yazılır. "
        "Getirilen metin çıktıya gövde olarak kopyalanmaz. shared/context-economy-contract.md."
    ).format(n=n_srv, nc=len(comps), cd=comp_desc)


def build_context(lock, probe: dict, plugins: dict) -> str:
    """Konvansiyonlar + delegasyon durumu + YALNIZ sağlıksız prob satırları."""
    ctx = conventions(lock)

    if plugins:
        installed = [n for n, ok in plugins.items() if ok]
        absent = [n for n, ok in plugins.items() if not ok]
        if installed:
            ctx += ("\n[preflight/delegasyon] KURULU: " + ", ".join(installed)
                    + " → bağlam tetiklendiğinde çağrılmaları ZORUNLU (evidentia: her "
                      "klinik-boyutlu sorgu; sci-audit: her reform-modu çıktısı). "
                      "Atlanmaları G0 ihlalidir; manifesto satırları 'skipped: plugin "
                      "kurulu değil' YAZILAMAZ.")
        if absent:
            ctx += ("\n[preflight/delegasyon] KURULU DEĞİL: " + ", ".join(absent)
                    + " → graceful degrade meşru; manifestoda 'skipped: plugin kurulu "
                      "değil' beyan et, eksik katmanı uydurma.")

    broken = [r for r in probe.values() if r.get("status") == "unauthorized"]
    missing = [r for r in probe.values() if r.get("status") == "auth_missing"]
    down = [r for r in probe.values() if r.get("status") in ("unreachable", "error")]

    if broken:
        ctx += ("\n[preflight] ⚠ YAPILANDIRMA ARIZASI — şu server(lar) canlı prob'da "
                "401/403 verdi: "
                + ", ".join("{} (HTTP {})".format(r["name"], r.get("http"))
                            for r in broken)
                + ". Bu bir degrade DEĞİL, düzeltilebilir bir wiring hatasıdır: ya "
                  ".mcp.json'daki Authorization header'ı eksik/yanlış, ya anahtar "
                  "geçersiz/emekli. Çözüm: fleet.yaml'i düzelt → "
                  "`python3 tools/gen_fleet.py`. Bu tur ilgili katman manifestoda "
                  "'degraded: 401' olarak beyan edilir; ASLA uydurma.")
    if missing:
        ctx += ("\n[preflight] Şu connector anahtar(lar)ı süreç ortamında YOK: "
                + ", ".join("{} ({})".format(r["name"], r.get("detail", ""))
                            for r in missing)
                + ". Manifestoda 'skipped: anahtar yok' beyan edilir (tam-filo degrade "
                  "— çıktı durmaz). Çözüm: oturumu "
                  "`doppler run -p cureohub -c dev_personal -- claude` ile başlat.")
    if down:
        ctx += ("\n[preflight] Şu server(lar) erişilemedi: "
                + ", ".join("{} ({})".format(r["name"],
                                             r.get("detail") or r.get("http"))
                            for r in down)
                + ". Manifestoda 'degraded: erişilemedi' beyan et; yokluk kanıt "
                  "DEĞİLDİR, veri boşluğu doldurulmaz.")
    return ctx


def detect_installed_plugins():
    """~/.claude/settings.json enabledPlugins'ten delegasyon plugin'lerini algılar.

    Amaç: 'kurulu → çağrı ZORUNLU / kurulu değil → graceful degrade' ayrımını
    oturum başında kanıta bağlamak. Okuma başarısızlığı = bilinmiyor — fail-open.
    """
    try:
        lock = fleet_probe.load_lock(ROOT) if fleet_probe else None
        prefixes = ({d["name"]: d["plugin_id_prefix"] for d in lock["delegations"]}
                    if lock and lock.get("delegations") else DELEGATION_FALLBACK)
        path = os.path.expanduser("~/.claude/settings.json")
        with open(path, encoding="utf-8") as fh:
            enabled = json.load(fh).get("enabledPlugins", {})
        return {name: any(k.startswith(p) and v for k, v in enabled.items())
                for name, p in prefixes.items()}
    except Exception:
        return {}


def main():
    try:
        sys.stdin.read()  # SessionStart payload'ını boşalt (kullanılmıyor)
    except Exception:
        pass

    lock, probe = None, {}
    try:
        if fleet_probe:
            lock = fleet_probe.load_lock(ROOT)
            probe = fleet_probe.cached_probe(ROOT, os.environ)
    except Exception:
        pass  # fail-open: prob olmadan da konvansiyonlar gider

    ctx = build_context(lock, probe, detect_installed_plugins())
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart",
                               "additionalContext": ctx}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
