#!/usr/bin/env python3
"""Cureonics sürüklenme kapısı — AĞ ERİŞİMİ GEREKTİRMEZ, CI'da güvenle koşar.

Altı denetim (hepsi deterministik):
  [1] Türetilmiş dosyalar güncel mi        gen_fleet --check
  [2] Sürüm tutarlı mı                     plugin.json ↔ marketplace ↔ codex ↔ SKILL.md
  [3] Vendor'lı fleet_probe bayt-özdeş mi  kanonik kopyayla karşılaştırılır
  [4] Çift hooks.json var mı               kök + hooks/ aynı anda
  [5] Düzyazı filo sayısı doğru mu         (fleet.yaml `prose_count_check: true` derse)
  [6] Sunucu KİMLİĞİ filoda var mı         `mcp__<id>__*` / `mcp_server: <id>` ↔ fleet.yaml

NEDEN VAR: 2026-08-06 denetimi tek koşumda üç ölü katman, iki sapmış codex bloğu
ve beş sürüm sürüklenmesi buldu — hiçbiri bir teste takılmıyordu çünkü hiçbiri
türetilmiyordu. Bu kapı o üç sınıfı da yakalar.

[6] NEDEN EKLENDİ (2026-08-07): denetim [5] yalnız SAYI iddialarını tarıyordu
("19 server"), AD/uç sürüklenmesini görmüyordu. Bu yüzden `lex-sanitas-mcp`
2026-06-29'da `health-policy-mcp` olarak yeniden adlandırılıp kapsamı
daraltıldığı hâlde `source_registry.yaml` sekiz satırda ölü adı taşımaya devam
etti; sayı hep 19 kaldığı için kapı temiz raporladı. Ölü uç 2026-08-07'de HTTP
404 döndürdüğü doğrulandı — yani registry, doğrulanması imkânsız bir kaynağa
`verification` bağlıyordu. [6] tam da bu sınıfı yakalar: filoda OLMAYAN bir
sunucu kimliğine yapılan her atıf sürüklenmedir.

Kullanım:
  python3 tools/fleetkit/check_drift.py --all
  python3 tools/fleetkit/check_drift.py lex-sanitas edupedia
Çıkış: 0 temiz · 1 sürüklenme.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_fleet  # noqa: E402

REPO = gen_fleet.REPO
PLUGINS = gen_fleet.PLUGINS
CANONICAL_PROBE = Path(__file__).resolve().parent / "fleet_probe.py"

# Düzyazıda 'N MCP/server/companion' iddiası. Dışlananlar (regresyon testli):
#   tarih/madde-no (24/2/2022, Md.90/5) · '§4 server-side' · 'Mod 1 server-listesi'
#   · harf öneki ('G7 companion') · bileşik ad ('server-side')
SERVER_CLAIM = re.compile(
    r"(?<![\w.,/§-])(?<!Mod )(\d{1,3})\s+"
    r"(?:hukuk/regülasyon\s+|hukuk\s+|kaynak\s+|wire'?lı\s+)?"
    r"(?:MCP|server|sunucu)\b(?!-)", re.IGNORECASE)
COMPANION_CLAIM = re.compile(
    r"(?<![\w.,/§-])(?<!Mod )(\d{1,3})\s+(?:zorunlu\s+|wire'?lı\s+|bağlı\s+)?"
    r"companion\b(?!-)", re.IGNORECASE)

SCAN_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".json"}
SKIP_DIRS = {"__pycache__", ".git", "node_modules"}
SKIP_FILES = {"fleet.lock.json", ".mcp.json", "fleet.yaml"}
SKIP_PREFIXES = ("test_",)


def scan_text(text, expected, companions=None):
    hits = [m.group(0).strip() for m in SERVER_CLAIM.finditer(text)
            if int(m.group(1)) != expected]
    if companions is not None:
        hits += [m.group(0).strip() for m in COMPANION_CLAIM.finditer(text)
                 if int(m.group(1)) != companions]
    return hits


def scan_prose(root: Path, expected: int, companions: int):
    out = []
    for path in sorted(root.rglob("*")):
        if (not path.is_file() or path.suffix not in SCAN_SUFFIXES
                or path.name in SKIP_FILES or SKIP_DIRS & set(path.parts)
                or path.name.startswith(SKIP_PREFIXES)):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            for hit in scan_text(line, expected, companions):
                out.append((str(path.relative_to(root)), i, hit))
    return out


# [6] Sunucu kimliği sürüklenmesi.
#   `mcp__<id>__tool`  → araç-öneki biçimi (SKILL.md, ajan araç kısıtı, testler)
#   `mcp_server: <id>` → source_registry.yaml erişim bloğu
# Companion'lar `.mcp.json`'da DEĞİLDİR (claude.ai connector'ı) ama meşru
# kimliklerdir → normalize edilip beyaz listeye alınır (Yargı→Yarg/Yargi vb.).
SERVER_REF = re.compile(r"mcp__([A-Za-z0-9_-]+)__")
REGISTRY_REF = re.compile(r"^\s*.*\bmcp_server:\s*([A-Za-z0-9_-]+)", re.M)
# Filo dışı ama meşru ön ekler (başka plugin'lerin araçları).
REF_ALLOW = {"playwright", "cloudflaredocs", "cloudflareapi", "sequentialthinking"}
_FOLD = str.maketrans("ıüöçşğâîû", "uuocsgaiu")   # 'ı' fold'u aşağıda özel ele alınır


def _squash_ref(s: str) -> str:
    """Kimliği karşılaştırılabilir çekirdeğe indir: claude.ai öneki + ayraçlar atılır."""
    s = s.lower()
    for pre in ("mcp__", "claude_ai_", "plugin_"):
        if s.startswith(pre):
            s = s[len(pre):]
    return re.sub(r"[^a-z0-9]", "", s)


def _name_variants(name: str) -> set:
    """Connector adının yüzeyde alabileceği biçimler.

    claude.ai araç öneki ASCII-DIŞI harfleri ya karşılığına katlar ya da '_'
    yapar/düşürür: 'Türk Patent' → T_rk_Patent · 'Yargı' → Yarg. Bu yüzden
    her ada iki çekirdek üretilir: katlanmış ve ASCII-dışı-düşürülmüş.
    """
    low = name.lower()
    folded = low.replace("ı", "i").translate(_FOLD)
    dropped = re.sub(r"[^\x00-\x7f]", "", low)
    return {_squash_ref(folded), _squash_ref(dropped)}


def scan_server_ids(root: Path, fleet: dict):
    """Filoda bulunmayan sunucu kimliğine yapılan atıfları döndür."""
    known = set(REF_ALLOW)
    for s in fleet["servers"]:
        known |= _name_variants(s["name"])
    for c in fleet.get("companions", []):
        known |= _name_variants(c["name"])
    out = []
    for path in sorted(root.rglob("*")):
        if (not path.is_file() or path.suffix not in SCAN_SUFFIXES
                or path.name in SKIP_FILES or SKIP_DIRS & set(path.parts)
                or path.name.startswith(SKIP_PREFIXES)):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            for m in list(SERVER_REF.finditer(line)) + list(REGISTRY_REF.finditer(line)):
                ref = m.group(1)
                if _squash_ref(ref) in known:
                    continue
                out.append((str(path.relative_to(root)), i, ref))
    return out


def versions(d: Path, marketplace: dict):
    man = json.loads((d / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    name = man["name"]
    vs = {"plugin.json": man.get("version"), "marketplace": marketplace.get(name)}
    codex = d / ".codex-plugin" / "plugin.json"
    if codex.is_file():
        vs["codex"] = json.loads(codex.read_text(encoding="utf-8")).get("version")
    for sk in sorted((d / "skills").glob("*/SKILL.md")):
        if sk.parent.name != name:
            continue
        m = re.search(r"^version:\s*(\S+)\s*$", sk.read_text(encoding="utf-8"), re.M)
        if m:
            vs["SKILL.md"] = m.group(1)
    lock = d / "fleet.lock.json"
    if lock.is_file():
        vs["fleet.lock"] = json.loads(lock.read_text(encoding="utf-8")).get("plugin_version")
    return {k: v for k, v in vs.items() if v is not None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cureonics sürüklenme kapısı")
    ap.add_argument("plugins", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if not (a.plugins or a.all):
        ap.error("plugin adı ya da --all gerekli")

    marketplace = {p["name"]: p.get("version") for p in json.loads(
        (REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))["plugins"]}
    canonical = CANONICAL_PROBE.read_bytes()
    failed, checked = False, 0

    for d in gen_fleet.plugin_dirs(a.plugins or None):
        checked += 1
        fleet = gen_fleet.load_fleet(d)
        counts = gen_fleet.build_lock(fleet)["counts"]
        issues = []

        stale = gen_fleet.write_all(d, fleet, check=True)
        if stale:
            issues.append(("[1] türetilmiş dosya güncel değil", stale,
                           "python3 tools/fleetkit/gen_fleet.py"))

        vs = versions(d, marketplace)
        if len(set(vs.values())) > 1:
            issues.append(("[2] sürüm tutarsız", [f"{k}={v}" for k, v in vs.items()],
                           "hepsini plugin.json sürümüne eşitle"))

        vend = d / "hooks" / "scripts" / "fleet_probe.py"
        if vend.is_file() and vend.read_bytes() != canonical:
            issues.append(("[3] vendor'lı fleet_probe kanoniğinden sapmış",
                           [str(vend.relative_to(REPO))],
                           "python3 tools/fleetkit/vendor.py"))

        if (d / "hooks.json").is_file() and (d / "hooks" / "hooks.json").is_file():
            issues.append(("[4] çift hooks.json", ["hooks.json + hooks/hooks.json"],
                           "kök kopyayı sil (hooks/hooks.json kanonik)"))

        if fleet.get("prose_count_check"):
            prose = scan_prose(d, counts["servers"], counts["companions"])
            if prose:
                issues.append((f"[5] düzyazı sayı sürüklenmesi (gerçek "
                               f"{counts['servers']} server / {counts['companions']} companion)",
                               [f"{f}:{ln} → {h!r}" for f, ln, h in prose], ""))

        bad_ids = scan_server_ids(d, fleet)
        if bad_ids:
            issues.append(("[6] filoda OLMAYAN sunucu kimliğine atıf "
                           "(yeniden adlandırma/emeklilik sürüklenmesi)",
                           [f"{f}:{ln} → {r!r}" for f, ln, r in bad_ids],
                           "fleet.yaml'e ekle ya da atfı güncel sunucuya taşı"))

        if issues:
            failed = True
            if not a.quiet:
                print(f"\n⚠ {d.name}")
                for title, items, fix in issues:
                    print(f"  {title}:")
                    for it in items:
                        print(f"      · {it}")
                    if fix:
                        print(f"    → {fix}")
        elif not a.quiet:
            print(f"✓ {d.name:22s} {counts['servers']:>3d} server "
                  f"({counts['gated']} gated / {counts['public']} public)"
                  + (f", {counts['companions']} companion" if counts["companions"] else ""))

    if not a.quiet:
        print(f"\n{'SÜRÜKLENME VAR' if failed else 'FİLO TEMİZ'} — {checked} plugin denetlendi")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
