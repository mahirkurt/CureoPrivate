#!/usr/bin/env python3
"""evidentia SessionStart preflight — gated-connector integration check.

CONTRACT (unchanged): SILENT when the fleet is healthy, so this adds no noise to
non-evidentia sessions. It speaks only when something is actually wrong.

WHAT CHANGED (2026-08-07 audit findings MAJOR-2 + MINOR-1):

  * The gated-connector map is NO LONGER HARDCODED. It is derived from
    `fleet.lock.json` (generated from `fleet.yaml` by `tools/fleetkit/gen_fleet.py`,
    byte-verified by `tools/fleetkit/check_drift.py`). The old hardcoded dict listed
    SIX connectors while `.mcp.json` had SEVEN: the 2026-08-02 TİTCK gating was
    repaired in `.mcp.json` on 2026-08-06 but never reached this hook, so a missing
    `TITCK_MCP_API_KEY` produced NO warning — and the emitted message positively
    told the operator that `titck-cache` (renamed `titck` on 2026-08-07) was
    keyless and unaffected. Deriving the
    map from the lock makes that class of drift structurally impossible.

  * The hook now also consults the live fleet probe (`hooks/scripts/fleet_probe.py`,
    byte-identical vendor of the canonical copy) and DISTINGUISHES two states that
    an env-only check cannot tell apart:

        auth_missing  → key absent from the process env  → LEGITIMATE DEGRADE
        unauthorized  → the server answered 401/403      → CONFIGURATION FAULT

    Without that split, a real wiring fault lives forever disguised as a degrade.
    That is exactly how the TİTCK gating survived for months. The probe is
    24h-cached, so the normal session pays no network cost.

Fail-open everywhere: a missing lock, a broken probe module, or any exception
yields a silent exit 0 — this hook never blocks a session.

Offline/deterministic mode: set EVIDENTIA_PREFLIGHT_NO_PROBE=1 to run the env
layer only (used by hooks/test_hooks.py so the suite needs no network).
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "hooks" / "scripts"))
try:
    import fleet_probe  # vendored; canonical = tools/fleetkit/fleet_probe.py
except Exception:  # probe module absent/broken → env layer still runs
    fleet_probe = None

# Human-readable "why this connector matters" notes. Purely cosmetic: a connector
# missing from this map is still reported, just without an editorial aside.
WHY = {
    "openathens": "tam-metin Tier 3 lisanslı",
    "anamnesis": "RAG/GraphRAG substratı",
    "evidentia-kb": "kb_search recall booster",
    "openfda": "openFDA + WHO ICD-11",
    "annas-reader": "tam-metin Tier 5 son çare",
    "yok-akademik": "YÖK akademisyen profilleri",
    "titck-cache": "Türkiye Dörtlüsü latency fallback",
}

DOPPLER_FIX = ("Çözüm: oturumu `doppler run -p cureohub -c dev_personal -- claude` ile "
               "başlat → tüm ${VAR}'lar otomatik enjekte olur, ek credential girmeye "
               "gerek yok.")


def gated_map():
    """{connector: env_var} — fleet.lock.json'dan türetilir, ASLA hardcode değil."""
    try:
        lock = fleet_probe.load_lock(ROOT) if fleet_probe else json.loads(
            (ROOT / "fleet.lock.json").read_text(encoding="utf-8"))
        if not lock:
            return {}
        return {s["name"]: s["auth_env"] for s in lock.get("servers", [])
                if s.get("auth_env")}
    except Exception:
        return {}


def label(name, env_var):
    why = WHY.get(name)
    return f"{name} (${env_var}{'; ' + why if why else ''})"


def main():
    try:
        sys.stdin.read()  # drain the SessionStart payload (unused)
    except Exception:
        pass

    try:
        gated = gated_map()
        if not gated:
            sys.exit(0)  # lock unreadable → fail-open, stay silent

        # --- Layer 1: env (offline, deterministic) ---------------------------
        missing = [label(n, v) for n, v in sorted(gated.items())
                   if not os.environ.get(v)]

        # --- Layer 2: live probe (24h-cached; catches what env cannot) --------
        broken, down = [], []
        if fleet_probe and not os.environ.get("EVIDENTIA_PREFLIGHT_NO_PROBE"):
            try:
                for r in fleet_probe.cached_probe(ROOT, os.environ).values():
                    st = r.get("status")
                    if st == "unauthorized":
                        broken.append(f"{r['name']} (HTTP {r.get('http')})")
                    elif st in ("unreachable", "error"):
                        down.append(f"{r['name']} ({r.get('detail') or r.get('http')})")
            except Exception:
                pass  # probe failure must never turn into a false alarm

        if not (missing or broken or down):
            sys.exit(0)  # healthy fleet → SILENT (the contract)

        parts = []
        if broken:
            parts.append(
                "⚠ YAPILANDIRMA ARIZASI — şu connector(lar) canlı prob'da 401/403 verdi: "
                + ", ".join(broken)
                + ". Bu bir degrade DEĞİL, düzeltilebilir bir wiring hatasıdır: ya "
                  ".mcp.json'daki Authorization header'ı eksik/yanlış, ya anahtar "
                  "geçersiz/emekli. Onarım: fleet.yaml'i düzelt → "
                  "`python3 tools/fleetkit/gen_fleet.py`. Bu tur ilgili katman "
                  "manifestoda 'degraded: 401' beyan edilir; ASLA uydurma.")
        if missing:
            parts.append(
                "Gated connector key(ler)i süreç ortamında YOK: " + ", ".join(missing)
                + f". Bu connector'lar çağrı anında 401 döner. {DOPPLER_FIX} "
                  "Manifestoda 'skipped: anahtar yok' beyan edilir (meşru degrade — "
                  "çıktı durmaz, veri boşluğu doldurulmaz).")
        if down:
            parts.append(
                "Şu connector(lar)a erişilemedi: " + ", ".join(down)
                + ". Manifestoda 'degraded: erişilemedi' beyan et; yokluk kanıt "
                  "DEĞİLDİR.")

        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "[evidentia preflight] " + " ".join(parts),
            }
        }))
    except Exception:
        pass  # fail-open
    sys.exit(0)


if __name__ == "__main__":
    main()
