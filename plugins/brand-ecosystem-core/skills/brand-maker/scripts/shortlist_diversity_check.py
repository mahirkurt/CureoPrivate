#!/usr/bin/env python3
"""
shortlist_diversity_check.py — Portfolio-level Diversity & Confusability Gate (v2.1)

⚠️ NEW in v2.1 — expert-audit remediation B.
The 2026 audit found a 14-finalist shortlist where EVERY name ended in
-onta/-anta/-anza/-venta/-vanza. That is not "four or five naming territories"
— it is a single algorithm's variations, with heavy intra-portfolio auditory
confusion (Faronta / Fidonta / Nortanza / Ortanza / Ortanta). The existing
morpheme_saturation_check.py scores names ONE AT A TIME and cannot see this:
homogeneity is a property of the SET, not of any single name.

This script is a SET-level gate. It blocks a shortlist that fails diversity and
tells the skill which territories are missing so Adım 3.2/3.3 can trigger a
complementary generation round from DIFFERENT phonetic/morphological families
(and away from the -anza family).

Metrics:
  1. Terminal-rhyme saturation — largest cluster of names sharing the same
     terminal rhyme (last-3 phonogram), as a share of the shortlist.
  2. Saturated-family share — share matching the Vn[zt]V / -anza-family regex.
  3. Intra-shortlist confusability — pairs that are auditorily confusable
     (shared terminal rhyme AND small normalized Levenshtein distance).
  4. Phonetic-family spread — distinct (ending-class, syllable-bucket,
     initial-consonant-class) signatures represented.
  5. (optional) Category spread — when --categories A,B,C… is given, no single
     naming category (A/B/C/D/E) may dominate.

USAGE:
    python shortlist_diversity_check.py "Auronza" "Nortanza" "Ortanza" ...
    python shortlist_diversity_check.py --json Name1 Name2 ...
    python shortlist_diversity_check.py --categories A,A,B,C,E Name1 ...

Scoring: prints PASS/FAIL. Exit code 0 = PASS, 1 = FAIL (CI-friendly).
DEPENDENCIES: Pure Python 3.8+ stdlib.
"""

import argparse
import json
import re
import sys
from itertools import combinations
from typing import Dict, List

VOWELS = set("aeiouy")
FRONT_CONS = set("bfpvmw")       # labial-ish
DENTAL_CONS = set("tdnszlr")     # coronal-ish
BACK_CONS = set("kgqxhcj")       # dorsal/other

# The specific saturated family the audit caught: a vowel + n + (z|t) + vowel.
# -anza, -onta, -enta, -anta, -inza, -unza, -venta(→enta), -vanza(→anza)…
SATURATED_FAMILY_RE = re.compile(r"[aeiou]n[zt][aeiou]$")

# Gate thresholds (documented; tune per audit evidence).
TERMINAL_CLUSTER_CEILING = 0.40   # >40% sharing one terminal rhyme → fail
FAMILY_SHARE_CEILING = 0.40       # >40% in one morpheme family → fail
CONFUSABLE_PAIR_CEILING = 0.20    # >20% of all pairs confusable → fail
MIN_ENDING_FAMILIES = 3           # need ≥3 distinct ending classes (if n≥5)
CATEGORY_DOMINANCE_CEILING = 0.60 # no single category > 60% of shortlist


def clean(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


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
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def norm_similarity(a: str, b: str) -> float:
    m = max(len(a), len(b)) or 1
    return 1.0 - levenshtein(a, b) / m


def terminal_rhyme(name: str, n: int = 3) -> str:
    c = clean(name)
    return c[-n:] if len(c) >= n else c


def syllable_bucket(name: str) -> str:
    c = clean(name)
    syl = max(1, len(re.findall(r"[aeiouy]+", c)))
    if syl <= 1:
        return "1"
    if syl == 2:
        return "2"
    if syl == 3:
        return "3"
    return "4+"


def initial_consonant_class(name: str) -> str:
    c = clean(name)
    if not c:
        return "none"
    first = c[0]
    if first in VOWELS:
        return "vowel-initial"
    if first in FRONT_CONS:
        return "labial"
    if first in DENTAL_CONS:
        return "coronal"
    if first in BACK_CONS:
        return "dorsal"
    return "other"


def ending_class(name: str) -> str:
    """Coarse ending class = last vowel-consonant shape of the last 2 chars."""
    c = clean(name)
    if len(c) < 2:
        return c or "none"
    tail = c[-2:]
    shape = "".join("V" if ch in VOWELS else "C" for ch in tail)
    return f"{shape}:{c[-1]}"  # e.g. "CV:a", "VC:n"


def cluster_by(items: List[str], keyfn) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for it in items:
        out.setdefault(keyfn(it), []).append(it)
    return out


def analyze(names: List[str], categories: List[str] = None) -> Dict:
    names = [n for n in names if clean(n)]
    n = len(names)
    reasons_fail = []
    reasons_note = []

    # 1. Terminal-rhyme clustering
    rhyme_clusters = cluster_by(names, terminal_rhyme)
    largest_rhyme = max(rhyme_clusters.items(), key=lambda kv: len(kv[1]),
                        default=("", []))
    largest_rhyme_share = len(largest_rhyme[1]) / n if n else 0.0

    # 2. Saturated-family share
    family_hits = [x for x in names if SATURATED_FAMILY_RE.search(clean(x))]
    family_share = len(family_hits) / n if n else 0.0

    # 3. Confusable pairs (shared terminal rhyme + high similarity)
    confusable = []
    for a, b in combinations(names, 2):
        ca, cb = clean(a), clean(b)
        share_rhyme = terminal_rhyme(a) == terminal_rhyme(b)
        sim = norm_similarity(ca, cb)
        if (share_rhyme and sim >= 0.5) or sim >= 0.7:
            confusable.append({"pair": [a, b], "similarity": round(sim, 2),
                               "shared_rhyme": terminal_rhyme(a) if share_rhyme else None})
    total_pairs = n * (n - 1) // 2 if n > 1 else 1
    confusable_share = len(confusable) / total_pairs

    # 4. Phonetic-family spread
    ending_families = cluster_by(names, ending_class)
    syllable_spread = cluster_by(names, syllable_bucket)
    initial_spread = cluster_by(names, initial_consonant_class)

    # 5. Category spread (optional)
    category_stats = None
    if categories:
        cat_clusters: Dict[str, int] = {}
        for c in categories[:n]:
            cat_clusters[c.strip().upper()] = cat_clusters.get(c.strip().upper(), 0) + 1
        dominant = max(cat_clusters.values()) / n if cat_clusters else 0.0
        distinct = len(cat_clusters)
        category_stats = {"distribution": cat_clusters,
                          "dominant_share": round(dominant, 2),
                          "distinct_categories": distinct}

    # --- Gate decision ---
    if largest_rhyme_share > TERMINAL_CLUSTER_CEILING:
        reasons_fail.append(
            f"Terminal-rhyme saturation: {len(largest_rhyme[1])}/{n} names share "
            f"the '-{largest_rhyme[0]}' rhyme ({largest_rhyme_share:.0%} > "
            f"{TERMINAL_CLUSTER_CEILING:.0%} ceiling).")
    if family_share > FAMILY_SHARE_CEILING:
        reasons_fail.append(
            f"Single-morpheme-family saturation: {len(family_hits)}/{n} names "
            f"match the -anza/-anta/-onta/-venta family ({family_share:.0%} > "
            f"{FAMILY_SHARE_CEILING:.0%} ceiling). This is one algorithm's "
            f"variations, not distinct naming territories.")
    if confusable_share > CONFUSABLE_PAIR_CEILING:
        reasons_fail.append(
            f"Intra-portfolio confusability: {len(confusable)}/{total_pairs} name "
            f"pairs are auditorily confusable ({confusable_share:.0%} > "
            f"{CONFUSABLE_PAIR_CEILING:.0%} ceiling).")
    if n >= 5 and len(ending_families) < MIN_ENDING_FAMILIES:
        reasons_fail.append(
            f"Phonetic monotony: only {len(ending_families)} distinct ending "
            f"class(es) across {n} names (need ≥{MIN_ENDING_FAMILIES}).")
    if category_stats and category_stats["dominant_share"] > CATEGORY_DOMINANCE_CEILING:
        reasons_fail.append(
            f"Category dominance: one naming category holds "
            f"{category_stats['dominant_share']:.0%} of the shortlist "
            f"(> {CATEGORY_DOMINANCE_CEILING:.0%}).")

    if len(syllable_spread) < 2 and n >= 5:
        reasons_note.append("All finalists share the same syllable count — "
                            "consider varying syllable length.")
    if len(initial_spread) < 2 and n >= 5:
        reasons_note.append("All finalists share the same initial-consonant "
                            "class — vary the onset.")

    passed = len(reasons_fail) == 0

    # Missing-territory guidance for the second round
    missing = []
    if not passed:
        if family_share > FAMILY_SHARE_CEILING:
            missing.append("Generate a round OUTSIDE the -anza/-anta/-onta/"
                           "-venta family (hard vowel-final coined, monosyllabic "
                           "contrarian, real-word metaphor, mythological).")
        present_endings = set(ending_families.keys())
        for want in ["CV:o", "CV:i", "VC:n", "CV:e", "CC:x"]:
            if want not in present_endings:
                missing.append(f"No name with ending class '{want}' — add one.")

    return {
        "shortlist_size": n,
        "gate": "PASS" if passed else "FAIL",
        "passed": passed,
        "trigger_second_round": not passed,
        "metrics": {
            "largest_terminal_rhyme": {"rhyme": largest_rhyme[0],
                                       "members": largest_rhyme[1],
                                       "share": round(largest_rhyme_share, 2)},
            "saturated_family_share": round(family_share, 2),
            "saturated_family_members": family_hits,
            "confusable_pair_share": round(confusable_share, 2),
            "distinct_ending_classes": len(ending_families),
            "distinct_syllable_buckets": len(syllable_spread),
            "distinct_initial_classes": len(initial_spread),
        },
        "terminal_rhyme_clusters": {k: v for k, v in rhyme_clusters.items()
                                    if len(v) > 1},
        "confusable_pairs": confusable[:25],
        "ending_class_distribution": {k: v for k, v in ending_families.items()},
        "category_stats": category_stats,
        "fail_reasons": reasons_fail,
        "notes": reasons_note,
        "missing_territories": missing[:8],
    }


def format_report(a: Dict) -> str:
    out = []
    out.append("═" * 60)
    out.append(f"SHORTLIST DIVERSITY GATE — {a['shortlist_size']} finalists → "
               f"{a['gate']}")
    out.append("═" * 60)
    m = a["metrics"]
    lr = m["largest_terminal_rhyme"]
    out.append(f"Largest terminal-rhyme cluster: '-{lr['rhyme']}' × "
               f"{len(lr['members'])} ({lr['share']:.0%})  {lr['members']}")
    out.append(f"Saturated -anza-family share:   {m['saturated_family_share']:.0%}  "
               f"{m['saturated_family_members']}")
    out.append(f"Confusable pair share:          {m['confusable_pair_share']:.0%}")
    out.append(f"Distinct ending classes:        {m['distinct_ending_classes']}")
    out.append(f"Distinct syllable buckets:      {m['distinct_syllable_buckets']}")
    out.append(f"Distinct initial-cons classes:  {m['distinct_initial_classes']}")
    if a["confusable_pairs"]:
        out.append("\nConfusable pairs (top):")
        for p in a["confusable_pairs"][:10]:
            out.append(f"  • {p['pair'][0]} ↔ {p['pair'][1]}  "
                       f"(sim {p['similarity']}, rhyme -{p['shared_rhyme']})")
    if a["fail_reasons"]:
        out.append("\n✗ GATE FAILED:")
        for r in a["fail_reasons"]:
            out.append(f"  • {r}")
    if a["notes"]:
        out.append("\nNotes:")
        for r in a["notes"]:
            out.append(f"  • {r}")
    if a["missing_territories"]:
        out.append("\n→ SECOND-ROUND GUIDANCE (feed to Adım 3.2/3.3):")
        for r in a["missing_territories"]:
            out.append(f"  • {r}")
    if a["passed"]:
        out.append("\n✓ Shortlist shows genuine cross-territory diversity.")
    out.append("═" * 60)
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Portfolio-level diversity & confusability gate")
    parser.add_argument("names", nargs="+", help="Shortlist names")
    parser.add_argument("--categories", default=None,
                        help="Comma-separated naming categories (A/B/C/D/E) "
                             "aligned to names by position")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cats = args.categories.split(",") if args.categories else None
    result = analyze(args.names, cats)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_report(result))

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
