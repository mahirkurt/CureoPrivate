#!/usr/bin/env python3
"""Yapıştırılmış araç listesinden yüzey anlık görüntüsü üret.

Kullanım (worktree kökünden):
  python3 tools/fleetkit/snapshot_prefixes.py cureolex cowork --observed "2026-10-01 Cowork" < araclar.txt
  ... --write   → plugins/<plugin>/tests/surface_snapshots/<yüzey>.yaml (önek anahtarlı birleştirme)

Girdi: satır başına bir tam araç adı (mcp__<önek>__<araç>); diğer satırlar yok sayılır.
Eşleme: önekin araçlarının bir sunucunun `tools_used ∪ tools_fallback` kümesiyle kesişimi
en büyük olan sunucu. Yalnız genel adlarla (search/fetch) eşleşme sayılmaz. Kesişim yoksa
`server: null` — eşleme UYDURULMAZ.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
TOOL_RE = re.compile(r"^(mcp__.+?__)([A-Za-z0-9_]+)$")
GENERIC = {"search", "fetch"}


def map_prefixes(tool_names, fleet):
    by_prefix = {}
    for line in tool_names:
        m = TOOL_RE.match(line.strip())
        if m:
            by_prefix.setdefault(m.group(1), set()).add(m.group(2))
    rows = []
    for prefix in sorted(by_prefix):
        tools = by_prefix[prefix]
        best, best_n = None, 0
        for s in fleet.get("servers", []):
            known = set(s.get("tools_used", [])) | set(s.get("tools_fallback", []))
            n = len((tools & known) - GENERIC)
            if n > best_n:
                best, best_n = s["name"], n
        rows.append({"prefix": prefix, "server": best, "evidence": sorted(tools)[:5]})
    return rows


def merge(old, new_rows, surface, observed):
    """Spec A1.3: her satırın KENDİ `observed`'ı olur. Bu koşuda taze görülen
    (`new_rows`) satırlar CLI `--observed` değerini alır — aynı prefix daha önce
    var olsa bile (yeniden gözlemlendi, stale kalmamalı). Bu koşuda dokunulmayan
    eski satırlar KENDİ `observed`'larını korur; dosya-düzeyi `observed` yalnız
    'son güncelleme' bilgisidir, satırların kendi `observed`'ını EZMEZ."""
    entries = {e["prefix"]: e for e in (old or {}).get("entries", [])}
    for r in new_rows:
        row = dict(r)
        row["observed"] = observed
        entries[row["prefix"]] = row
    return {"surface": surface, "observed": observed, "entries": list(entries.values())}


def main(argv=None):
    ap = argparse.ArgumentParser(description="yüzey anlık görüntüsü")
    ap.add_argument("plugin")
    ap.add_argument("surface")
    ap.add_argument("--observed", required=True)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    root = REPO / "plugins" / a.plugin
    fleet = yaml.safe_load((root / "fleet.yaml").read_text(encoding="utf-8"))
    rows = map_prefixes(sys.stdin.read().splitlines(), fleet)
    path = root / "tests" / "surface_snapshots" / f"{a.surface}.yaml"
    old = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None
    doc = merge(old, rows, a.surface, a.observed)
    text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    if a.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"{path.relative_to(REPO)} — {len(rows)} önek işlendi, "
              f"{sum(1 for r in rows if r['server'] is None)} eşlenmedi")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
