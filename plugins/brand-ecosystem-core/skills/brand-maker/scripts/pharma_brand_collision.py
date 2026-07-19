#!/usr/bin/env python3
"""
pharma_brand_collision.py — Pharmaceutical BRAND-name collision pre-screen (v2.1)

⚠️ NEW in v2.1 — expert-audit remediation E.
inn_stem_collision.py checks only INN/USAN STEM suffixes (-mab, -tinib …). The
2026 audit found 'Claranta' sailing through that check while it is, in reality,
a REGISTERED Class 5 pharmaceutical mark (India) AND collides with the
clarithromycin / Claritin brand family — a pure BRAND-level collision an INN
stem scan structurally cannot see. This script adds the missing layer:
structured checks against real marketed drug BRAND names and high-collision INN
generics, plus a LASA (Look-Alike Sound-Alike) heuristic.

HARD DISCIPLINE (no-fabrication):
  • "No collision" is NEVER asserted from a single shallow pass. Every result
    carries provenance (which sources were consulted) and, because no LIVE
    trademark registry is queried here, a MANDATORY caveat that formal
    multi-jurisdiction TM research is still required. A clean seed result reads
    "resmî TM araştırması gerekli — ön-tarama yeterli değil", never "temiz".
  • Absence of a hit against the seed is not proof of clearance.

Detection layers:
  1. Substring / containment  — a real brand appears inside the candidate (or
     vice-versa) → HIGH.
  2. Distinctive shared prefix (≥4 leading chars) vs a brand or INN generic →
     MEDIUM (query risk). Catches 'Claranta' via the 'clar-' family.
  3. LASA — normalized Levenshtein similarity ≥0.60 or edit distance ≤2 vs a
     brand → HIGH/MEDIUM by strength.

USAGE:
    python pharma_brand_collision.py "Claranta" "Ozemvia"
    python pharma_brand_collision.py --json "Claranta"
    python pharma_brand_collision.py --data data/pharma_brand_names.json "Claranta"

Scoring (Axis 5b — 0-2):
    0 = strong brand collision (substring or LASA ≤1) — reject
    1 = query risk (shared distinctive prefix or moderate LASA) — flag
    2 = no seed hit — BUT formal TM research still mandatory (never "clean")

DEPENDENCIES: Pure Python 3.8+ stdlib.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_DATA = Path(__file__).parent.parent / "data" / "pharma_brand_names.json"

PREFIX_MIN = 4          # distinctive shared-prefix length
LASA_SIM_THRESHOLD = 0.60
LASA_EDIT_STRONG = 1    # edit distance ≤1 → strong LASA
LASA_EDIT_MEDIUM = 2    # edit distance ≤2 → medium LASA


def load_data(path: Optional[str]) -> Dict:
    p = Path(path) if path else DEFAULT_DATA
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: pharma brand seed not found at {p}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {p}: {e}", file=sys.stderr)
        sys.exit(1)


def clean(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def norm_sim(a: str, b: str) -> float:
    m = max(len(a), len(b)) or 1
    return 1.0 - levenshtein(a, b) / m


def shared_prefix_len(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def scan(name: str, data: Dict) -> Dict:
    cand = clean(name)
    brands = data.get("brand_names", [])
    inns = data.get("inn_generics_high_collision", [])
    sources = data.get("sources_catalogued", [])

    findings = []

    # Layer 1: substring / containment vs brand
    for b in brands:
        bc = clean(b["brand"])
        if len(bc) < 4:
            continue
        if bc in cand or cand in bc:
            findings.append({
                "type": "substring",
                "severity": "high",
                "match": b["brand"], "inn": b.get("inn"),
                "class": b.get("class"), "jurisdiction": b.get("jurisdiction"),
                "detail": f"'{b['brand']}' overlaps as substring with '{name}'",
            })

    # Layer 3: LASA vs brand
    for b in brands:
        bc = clean(b["brand"])
        d = levenshtein(cand, bc)
        sim = norm_sim(cand, bc)
        if d <= LASA_EDIT_STRONG:
            sev = "high"
        elif d <= LASA_EDIT_MEDIUM or sim >= LASA_SIM_THRESHOLD:
            sev = "medium"
        else:
            continue
        findings.append({
            "type": "LASA", "severity": sev,
            "match": b["brand"], "inn": b.get("inn"),
            "class": b.get("class"), "jurisdiction": b.get("jurisdiction"),
            "edit_distance": d, "similarity": round(sim, 2),
            "detail": f"Look-alike/sound-alike to '{b['brand']}' "
                      f"(edit {d}, sim {sim:.2f})",
        })

    # Layer 2: distinctive shared prefix vs brand or INN generic
    prefix_hits = []
    for b in brands:
        bc = clean(b["brand"])
        pl = shared_prefix_len(cand, bc)
        if pl >= PREFIX_MIN:
            prefix_hits.append({
                "type": "distinctive_prefix", "severity": "medium",
                "match": b["brand"], "inn": b.get("inn"),
                "class": b.get("class"), "jurisdiction": b.get("jurisdiction"),
                "shared_prefix": cand[:pl],
                "detail": f"Shares distinctive prefix '{cand[:pl]}-' with brand "
                          f"'{b['brand']}' ({b.get('inn')})",
            })
    for g in inns:
        gc = clean(g)
        pl = shared_prefix_len(cand, gc)
        if pl >= PREFIX_MIN:
            prefix_hits.append({
                "type": "distinctive_prefix_inn", "severity": "medium",
                "match": g, "inn": g, "class": "INN generic",
                "jurisdiction": "global",
                "shared_prefix": cand[:pl],
                "detail": f"Shares distinctive prefix '{cand[:pl]}-' with INN "
                          f"generic '{g}'",
            })
    findings.extend(prefix_hits)

    # De-dup findings by (type, match)
    seen = set()
    deduped = []
    for f in findings:
        key = (f["type"], clean(f["match"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(f)
    # Order: high first
    order = {"high": 0, "medium": 1, "low": 2}
    deduped.sort(key=lambda f: order.get(f["severity"], 3))

    has_high = any(f["severity"] == "high" for f in deduped)
    has_medium = any(f["severity"] == "medium" for f in deduped)

    if has_high:
        score = 0
        level = "STRONG BRAND COLLISION"
        verdict = ("REJECT — collides with an existing drug brand (substring/"
                   "LASA). FDA DMEPA Layer-1 + TİTCK Türkçe-LASA reject risk.")
    elif has_medium:
        score = 1
        level = "BRAND QUERY RISK"
        verdict = ("FLAG — shares a distinctive prefix / moderate LASA with an "
                   "existing pharmaceutical mark or INN family. Not clearable "
                   "without live TM search.")
    else:
        score = 2
        level = "NO SEED HIT"
        verdict = ("NO HIT against the seed brand list — BUT this is NOT a "
                   "clearance. Resmî çok-yargı-bölgeli TM araştırması gerekli — "
                   "ön-tarama yeterli değil.")

    # MANDATORY provenance + caveat (no live TM registry was queried here).
    caveat = ("Ön-tarama yalnızca kürasyonlu tohum listesine karşı yapıldı; "
              "CANLI trademark kaydı SORGULANMADI. 'Çakışma yok' bir temizlik "
              "belgesi DEĞİLDİR. WIPO Global Brand DB + USPTO + EUIPO/TMview + "
              "TÜRKPATENT + ilgili ulusal (ör. Hindistan) IP sicili zorunludur.")

    return {
        "name": name,
        "score": score,
        "level": level,
        "verdict": verdict,
        "findings": deduped,
        "collision_found": bool(deduped),
        "provenance": {
            "sources_catalogued": sources,
            "seed_brand_count": len(brands),
            "seed_inn_count": len(inns),
            "live_tm_checked": False,
        },
        "mandatory_caveat": caveat,
    }


def format_human(result: Dict) -> str:
    lines = [f"=== Pharma BRAND collision pre-screen — \"{result['name']}\" ==="]
    lines.append(f"Score: {result['score']}/2 — {result['level']}")
    lines.append(f"Verdict: {result['verdict']}")
    lines.append("")
    if result["findings"]:
        lines.append("Findings:")
        for f in result["findings"]:
            lines.append(f"  [{f['severity'].upper()}] {f['type']}: {f['detail']}")
            if f.get("class"):
                lines.append(f"        class: {f['class']}  jurisdiction: "
                             f"{f.get('jurisdiction')}")
    else:
        lines.append("No hit against the seed brand/INN list.")
    lines.append("")
    lines.append("Provenance:")
    for s in result["provenance"]["sources_catalogued"]:
        lines.append(f"  • {s}")
    lines.append(f"  live_tm_checked: {result['provenance']['live_tm_checked']}")
    lines.append("")
    lines.append("⚠ MANDATORY CAVEAT: " + result["mandatory_caveat"])
    lines.append("─" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Pharmaceutical brand-name collision pre-screen (Axis 5b)")
    parser.add_argument("names", nargs="+")
    parser.add_argument("--data", default=None, help="Path to brand seed JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = load_data(args.data)
    results = [scan(n, data) for n in args.names]

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            print(format_human(r))
            print()


if __name__ == "__main__":
    main()
