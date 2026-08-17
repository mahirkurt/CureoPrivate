#!/usr/bin/env python3
"""edupedia SessionStart preflight — connector kadrosu prob'u + pedagojik konvansiyon enjeksiyonu.

v1.0.0: anahtar haritası hardcoded DEĞİL — `fleet.lock.json`'dan gelir (`tools/fleetkit/gen_fleet.py`
üretir, kaynak `fleet.yaml`). Preflight gerçek MCP `initialize` prob'u yapar (24 saat cache'li)
ve iki hâli AYIRIR:

  auth_missing → anahtar süreç ortamında yok  → MEŞRU DEGRADE
  unauthorized → sunucu 401/403 verdi         → YAPILANDIRMA ARIZASI

Sağlıklı filoda preflight bölümü SESSİZDİR (yalnız konvansiyonlar enjekte edilir).
Fail-open: prob veya lock çökerse yalnız konvansiyonlar gider, oturum durmaz.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))
try:
    import fleet_probe
except Exception:
    fleet_probe = None


def conventions(lock: dict | None) -> str:
    """Çekirdek invaryantlar — sayılar lock'tan türetilir."""
    counts = (lock or {}).get("counts", {})
    n_srv = counts.get("servers", 2)
    return (
        f"[edupedia] MEB Türkiye Yüzyılı Maarif Modeli Etkileşimli Öğrenim Modülü Süiti aktif. "
        f"Çekirdek invaryantlar: "
        f"(1) İKİ MCP CONNECTOR — {n_srv} sunucu: maarif-mufredat (OTORİTE — 105 MEB ders kitabı tam metni, "
        f"10.855 kazanım, 22.414 figür, 13 çerçeve; Bearer) · egitim-kaynak (tamamlayıcı OER RAG içerik-zenginleştirme, "
        f"124 doğrulanmış kategori, PhET 175 simülasyon, OAuth 2.1 / Bearer; display adı 'Eğitim Kaynakları'). "
        f"Olgusal çelişkide ders kitabı KAZANIR. "
        f"(2) YEREL ÇIKTI — teslim yerel bağımsız tek-dosya HTML'dir (IBM Carbon v11, IBM Plex, "
        f"WCAG 2.1 AA, EMOJİSİZ, offline çalışır). Plugin yayınlamaz (/edupedia:yayinla emekli). "
        f"(3) 16 KALİTE KAPISI — yerel `scripts/validate_module.py` otoritedir: G-EMOJI, G-CARBON, "
        f"G-A11Y, G-INTERACT, G-SELFCONTAINED, G-CONTRAST, G-WELLBEING, G-VOICE, G-SVG, G-AUDIO, "
        f"G-TOKEN, G-CURRICULUM, G-VERIFY, G-FLOW, G-CARBON-GRID, G-EXAM. "
        f"(4) GÖRÜNTÜ-DAYANAK — Tier-1 (yazar-üretimli tema-duyarlı SVG) GARANTİ; Tier-2 (get_figure "
        f"ders kitabı görseli) BEST-EFFORT. "
        f"(5) KANONİK ÖNBELLEK — Tek-sefer disiplini (subject_registry, outcomes_extract, framework_map, "
        f"figure_probe) ve run-manifest yazımı (canonical-cache-contract.md). "
        f"(6) ZARİF DEGRADE — MCP erişilemezse offline yola dönülür (asla uydurma kaynak)."
    )


def build_context(lock: dict | None, probe: dict) -> str:
    """Konvansiyonlar + YALNIZ sağlıksız prob satırları."""
    ctx = conventions(lock)

    broken = [r for r in probe.values() if r.get("status") == "unauthorized"]
    missing = [r for r in probe.values() if r.get("status") == "auth_missing"]
    down = [r for r in probe.values() if r.get("status") in ("unreachable", "error")]

    if broken:
        ctx += (
            "\n⚠ YAPILANDIRMA ARIZASI — şu connector(lar) canlı prob'da 401/403 verdi: "
            + ", ".join(f"{r['name']} (HTTP {r.get('http')})" for r in broken)
            + ". Bu bir degrade DEĞİL, düzeltilebilir bir wiring hatasıdır: .mcp.json "
              "Authorization header'ı eksik/yanlış veya anahtar geçersiz. "
              "Onarım: fleet.yaml'i düzelt → `python3 tools/fleetkit/gen_fleet.py`."
        )

    if missing:
        ctx += (
            "\nGated connector key(ler)i süreç ortamında YOK: "
            + ", ".join(
                f"{r['name']} (${r.get('auth_env') or (r.get('detail', '').split(' ')[0].strip('${}'))})"
                for r in missing
            )
            + " → ilgili connector çağrıları 401 döner. Çözüm: oturumu "
              "`doppler run -p cureohub -c dev_personal -- claude` ile başlat. "
              "Manifestoda 'skipped: anahtar yok' beyan edilir (meşru degrade — "
              "çıktı durmaz, veri boşluğu doldurulmaz)."
        )

    if down:
        ctx += (
            "\nŞu connector(lar)a erişilemedi: "
            + ", ".join(f"{r['name']} ({r.get('detail') or r.get('http')})" for r in down)
            + " → offline yola düşülür; konunun yokluk kanıtı DEĞİLDİR."
        )

    return ctx


def main() -> int:
    try:
        sys.stdin.read()  # drain stdin payload if any
    except Exception:
        pass

    try:
        lock = fleet_probe.load_lock(ROOT) if fleet_probe else None
        probe = {}
        if fleet_probe and not os.environ.get("EDUPEDIA_PREFLIGHT_NO_PROBE"):
            probe = fleet_probe.cached_probe(ROOT, os.environ)

        ctx = build_context(lock, probe)
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": ctx,
            }
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    except Exception:
        pass  # fail-open
    return 0


if __name__ == "__main__":
    sys.exit(main())
