#!/usr/bin/env python3
"""lex-sanitas sürüklenme kapısı — AĞ ERİŞİMİ GEREKTİRMEZ, CI'da güvenle koşar.

Üç denetim:
  [1] Türetilmiş dosyalar güncel mi          (gen_fleet --check)
  [2] Düzyazıdaki filo sayısı gerçekle uyuşuyor mu
  [3] Hook'lar lock'u okuyor mu               (hardcoded GATED sözlüğü kalmadı mı)

NEDEN VAR: 2026-08-02 TİTCK kapılanması lex-sanitas'ta gözden kaçtı çünkü filo
sekiz ayrı yerde elle tarif ediliyordu. Aynı dönemde .mcp.json 15 server
tanımlarken plugin on dosyada "14" diyordu. Bu kapı iki sürüklenme sınıfını da
deterministik olarak yakalar.

Çıkış: 0 temiz · 1 sürüklenme.
Koşum: cd plugins/lex-sanitas && python3 tools/check_drift.py
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_fleet  # noqa: E402

# Filo sayısı iddiası kalıpları. YALNIZ 'N MCP/server/sunucu' bağlamında sayı arar.
# Dışlananlar (hepsi test_check_drift.py'de koruma altında):
#   · tarih/madde-no/oran      → önceki karakter [\d.,/-] ise eşleşmez (24/2/2022, Md.90/5)
#   · bölüm göndermesi         → '§' öneki ('§4 server-side', '§3 companion↔kapı')
#   · mod göndermesi           → 'Mod N server-listesi'
#   · bileşik ad               → noun'dan sonra '-' ('server-side', 'server-listesini')
SERVER_CLAIM = re.compile(
    r"(?<![\d.,/§-])(?<!Mod )(\d{1,3})\s+"
    r"(?:hukuk/regülasyon\s+|hukuk\s+|kaynak\s+|wire'?lı\s+)?"
    r"(?:MCP|server|sunucu)\b(?!-)",
    re.IGNORECASE,
)
COMPANION_CLAIM = re.compile(
    r"(?<![\d.,/§-])(?<!Mod )(\d{1,3})\s+companion\b(?!-)", re.IGNORECASE)

SCAN_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".json"}
SKIP_DIRS = {"__pycache__", ".git", "node_modules"}
# Üretilmiş dosyalar (sayıları zaten counts'tan gelir) ve kaynağın kendisi.
SKIP_FILES = {"fleet.lock.json", ".mcp.json", "fleet.yaml", "check_drift.py"}
# Test dosyaları kasten yanlış sayı içerir (regex'i sınamak için) — taranmaz.
SKIP_PREFIXES = ("test_",)


def scan_text(text: str, expected: int, companions=None) -> list:
    """Metindeki YANLIŞ filo-sayısı iddialarını döndürür."""
    hits = []
    for m in SERVER_CLAIM.finditer(text):
        if int(m.group(1)) != expected:
            hits.append(m.group(0).strip())
    if companions is not None:
        for m in COMPANION_CLAIM.finditer(text):
            if int(m.group(1)) != companions:
                hits.append(m.group(0).strip())
    return hits


def scan_prose_counts(root: Path, expected: int, companions: int) -> list:
    """Plugin ağacındaki düzyazıyı tarar; (dosya, satır_no, bulgu) listesi döner."""
    findings = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if path.name in SKIP_FILES or SKIP_DIRS & set(path.parts):
            continue
        if path.name.startswith(SKIP_PREFIXES):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            for hit in scan_text(line, expected, companions):
                findings.append((str(path.relative_to(root)), i, hit))
    return findings


def hook_coverage_gap(root: Path) -> str:
    """Hook'lar lock'u okumalı; hardcoded GATED sözlüğü kalmışsa yakala."""
    src_path = root / "hooks" / "scripts" / "session_start.py"
    try:
        src = src_path.read_text(encoding="utf-8")
    except OSError:
        return "session_start.py okunamadı"
    if re.search(r"^GATED\s*=\s*\{", src, re.MULTILINE):
        return ("session_start.py hâlâ hardcoded GATED sözlüğü taşıyor — "
                "fleet.lock.json okumalı (anahtar haritası türetilmeli)")
    if "fleet.lock.json" not in src and "load_lock" not in src:
        return "session_start.py fleet.lock.json okumuyor"
    return ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lex-sanitas sürüklenme kapısı")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parent.parent
    fleet = gen_fleet.load_fleet(root)
    counts = gen_fleet.build_lock(fleet)["counts"]
    failed = False

    stale = gen_fleet.write_all(root, fleet, check=True)
    if stale:
        failed = True
        if not args.quiet:
            print("[1/3] TÜRETİLMİŞ DOSYA SÜRÜKLENMESİ:", file=sys.stderr)
            for s in stale:
                print(f"      · {s}", file=sys.stderr)
            print("      Çözüm: python3 tools/gen_fleet.py", file=sys.stderr)

    prose = scan_prose_counts(root, counts["servers"], counts["companions"])
    if prose:
        failed = True
        if not args.quiet:
            print(f"[2/3] DÜZYAZI SAYI SÜRÜKLENMESİ (gerçek: {counts['servers']} "
                  f"server / {counts['companions']} companion):", file=sys.stderr)
            for f, line, hit in prose:
                print(f"      · {f}:{line}  →  {hit!r}", file=sys.stderr)

    gap = hook_coverage_gap(root)
    if gap:
        failed = True
        if not args.quiet:
            print(f"[3/3] HOOK KAPSAM AÇIĞI: {gap}", file=sys.stderr)

    if not failed and not args.quiet:
        print(f"filo temiz — {counts['servers']} server ({counts['gated']} gated / "
              f"{counts['public']} public), {counts['companions']} companion")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
