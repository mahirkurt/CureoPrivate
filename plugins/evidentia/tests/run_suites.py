#!/usr/bin/env python3
"""evidentia gate runner — the CI entry point for this plugin.

WHY THIS FILE EXISTS
--------------------
The repo's CI behaviour step globs `plugins/*/tests/run_suites.py` (.github/workflows/ci.yml).
Until 2026-08-08 only lex-sanitas shipped one, so evidentia's ENTIRE gate layer — 13 skill gates,
the hook regression pack, G-BUNDLE, G-IDENTITY, G-RAG — ran only when a human typed the commands.
Gates exist to catch drift; a gate nobody runs catches nothing. That is precisely how the five
documentation drifts found in the 2026-08-07 audit accumulated while every gate was "green".

WHAT IT RUNS (offline, deterministic, no secrets, no network)
  check_integrity.py   13 structural gates (G-REF/G-CONN/G-ALWAYS/G-VERSION/G-COVERAGE/G-PROBE/
                       G-XVAL/G-WHITELIST/G-SIZE/G-DESC/G-PHASES/G-DESKEW/G-AGENT)
  hooks/test_hooks.py  guard + retrieve-don't-dump + preflight regression pack
  scripts/g_bundle.py  .mcp.json <-> CONNECTORS.md consistency (pure static — the URLs it
                       compares are string literals, it opens no socket)
  scripts/g_identity.py  each self-host Worker carries its own realm/package/wrangler name
  rag_quality.py       G-RAG output faithfulness, STRUCTURAL layer only (the LLM-judge path is
                       opt-in behind --judge + EVIDENTIA_JUDGE_KEY and is deliberately not used)

WHAT IT DELIBERATELY DOES NOT RUN — and why it says so out loud
  g_probe.py  / g_tools.py     need live network AND Bearer credentials for the 7 gated
                               connectors. CI has neither, and a gate that silently skips the
                               gated half of the fleet while printing green is the exact failure
                               this plugin already fixed once. They stay MANUAL, under
                               `doppler run`, and this runner names them so their absence from
                               CI is visible rather than assumed.
                               (Same reasoning the repo already applies to check_tools.py.)

Usage:
  python3 tests/run_suites.py            # from the plugin root or from tests/
  python3 tests/run_suites.py --quiet
Exit: 0 = every offline gate passed · 1 = one or more failed · 2 = a gate script is missing.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                   # plugin root

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"

# (label, path relative to the plugin root, extra argv)
GATES = [
    ("skill integrity (13 kapı)", "skills/medical-research/evals/check_integrity.py", []),
    ("hook regresyon paketi", "hooks/test_hooks.py", []),
    ("G-BUNDLE", "scripts/g_bundle.py", []),
    ("G-IDENTITY", "scripts/g_identity.py", []),
    ("G-RAG (yapısal)", "skills/medical-research/evals/rag_quality.py", []),
]

# Named so a reader can never mistake CI-green for full coverage.
MANUAL_ONLY = [
    ("G-PROBE", "scripts/g_probe.py", "canlı initialize — ağ + 7 kapılı connector Bearer'ı"),
    ("G-TOOLS", "scripts/g_tools.py --smoke --surface",
     "canlı tools/list sözleşmesi + işlevsel smoke + Worker HTTP yüzeyi — ağ + Bearer"),
]


def run_gate(label, rel, extra, quiet):
    script = ROOT / rel
    if not script.exists():
        print(f"  {RED}EKSİK{RESET}  {label:26} {rel}")
        return None
    p = subprocess.run([sys.executable, str(script), *extra],
                       cwd=ROOT, capture_output=True, text=True)
    ok = p.returncode == 0
    tag = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
    print(f"  {tag}   {label:26} {rel}")
    if not ok or not quiet:
        tail = [ln for ln in (p.stdout + p.stderr).splitlines() if ln.strip()]
        # On failure show enough to diagnose; on success just the gate's own verdict line.
        for ln in (tail[-14:] if not ok else tail[-1:]):
            print(f"         {DIM}{ln}{RESET}")
    return ok


def main():
    ap = argparse.ArgumentParser(description="evidentia offline gate runner (CI entry point)")
    ap.add_argument("--quiet", action="store_true", help="only print each gate's verdict line")
    args = ap.parse_args()

    print(f"evidentia kapı koşucusu — {len(GATES)} çevrimdışı kapı (ağ yok, secret yok)\n")
    results = [run_gate(*g, args.quiet) for g in GATES]

    if any(r is None for r in results):
        print(f"\n{RED}SETUP HATASI: bir kapı betiği bulunamadı{RESET}")
        return 2

    failed = [g[0] for g, r in zip(GATES, results) if not r]

    print(f"\n{DIM}  CI'da KOŞMAYANLAR (ağ + Bearer ister; elle, `doppler run` altında):{RESET}")
    for label, cmd, why in MANUAL_ONLY:
        print(f"{DIM}    {label:10} python3 {cmd}{RESET}")
        print(f"{DIM}               → {why}{RESET}")

    if failed:
        print(f"\n{RED}KAPI DÜŞTÜ: {', '.join(failed)}{RESET}")
        return 1
    print(f"\n{GREEN}{len(GATES)}/{len(GATES)} ÇEVRİMDIŞI KAPI TEMİZ{RESET} "
          f"{DIM}(canlı kapsam için yukarıdaki iki elle-kapıyı koş){RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
