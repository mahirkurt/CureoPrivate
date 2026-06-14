#!/usr/bin/env python3
"""
disaster_checker.py — Brand-Maker Multi-Language Disaster Check

Simulates the methodology of `snguyenthanh/better_profanity` extended
internationally. Cross-checks candidate brand names against curated
profanity / taboo / false-friend dictionaries in 9 languages:

  English, Mandarin (pinyin), Hindi (transliterated), Spanish,
  Arabic (transliterated), French, Russian (transliterated),
  German, Turkish.

USAGE:
    python disaster_checker.py "AdayIsim1" "AdayIsim2" "AdayIsim3"

DEPENDENCIES: Pure Python 3.8+, no external libraries.

OUTPUT: GREEN / YELLOW / ORANGE / RED verdict per name with
specific language-flag detail.

LIMITATIONS: Heuristic substring + Levenshtein-2 matching.
NOT a substitute for native-speaker verification in critical markets.
"""

import sys
import re
from typing import Dict, List, Tuple

# ============================================================
# Multi-Language Profanity & Taboo Blocklists
# ============================================================
# Format: language → list of (pattern, severity, gloss)
# Severity: "hard" (RED), "soft" (YELLOW)
# These are HEURISTIC LISTS — not exhaustive, not perfect.
# Native-speaker review remains mandatory for critical markets.

BLOCKLISTS: Dict[str, List[Tuple[str, str, str]]] = {
    "english": [
        ("ass", "soft", "vulgar (buttocks/donkey)"),
        ("butt", "soft", "vulgar (buttocks)"),
        ("tit", "soft", "vulgar (breast)"),
        ("cock", "hard", "vulgar (penis)"),
        ("dick", "hard", "vulgar (penis)"),
        ("fag", "hard", "slur"),
        ("fuck", "hard", "vulgar"),
        ("shit", "hard", "vulgar"),
        ("crap", "soft", "vulgar (excrement)"),
        ("bitch", "hard", "slur"),
        ("damn", "soft", "mild profanity"),
        ("hell", "soft", "mild profanity"),
        ("rape", "hard", "violent term"),
        ("nazi", "hard", "extremist reference"),
        ("kill", "soft", "violent term"),
    ],
    "spanish": [
        ("puta", "hard", "vulgar (whore)"),
        ("polla", "hard", "vulgar (penis, Spain)"),
        ("coger", "soft", "vulgar in LatAm (to f**k); neutral in Spain"),
        ("pene", "soft", "anatomical (penis)"),
        ("culo", "soft", "vulgar (buttocks)"),
        ("mierda", "hard", "vulgar (sh*t)"),
        ("pinche", "soft", "Mexican vulgar intensifier"),
        ("cabron", "hard", "vulgar"),
        ("nova", "soft", "phrase 'no va' = doesn't go (urban legend but cautious)"),
        ("pajero", "hard", "vulgar (masturbator) — see Mitsubishi Pajero case"),
        ("fitta", "hard", "Swedish/Italian-Spanish overlap, vulgar (vagina)"),
        ("concha", "soft", "vulgar in Argentina/Uruguay (vagina); neutral elsewhere"),
    ],
    "arabic_translit": [
        ("khara", "hard", "vulgar (excrement)"),
        ("kara", "soft", "near-vulgar (excrement near-homophone)"),
        ("zubb", "hard", "vulgar (penis)"),
        ("kus", "hard", "vulgar (vagina, Egyptian dialect)"),
        ("tiz", "hard", "vulgar (buttocks)"),
        ("kelb", "soft", "literal 'dog' but used as insult"),
    ],
    "russian_translit": [
        ("blyat", "hard", "vulgar"),
        ("bliad", "hard", "vulgar"),
        ("pizda", "hard", "vulgar (vagina)"),
        ("pizdets", "hard", "vulgar"),
        ("xuy", "hard", "vulgar (penis); note Turkish 'huy' = habit, false friend"),
        ("huy", "hard", "vulgar (penis) — Turkish 'huy' = habit, FALSE FRIEND"),
        ("pidor", "hard", "slur"),
        ("ebat", "hard", "vulgar"),
    ],
    "mandarin_pinyin": [
        ("shi", "soft", "homophone of '死' (death)"),
        ("si", "soft", "homophone of '死' (death)"),
        ("ku", "soft", "homophone of '哭' (cry)"),
        ("kun", "soft", "homophone of certain Cantonese vulgar terms"),
        ("cao", "hard", "vulgar (f**k) — pinyin 'cào' 操"),
        ("ji", "soft", "polysemous; can be 'chicken' (鸡) — slang for prostitute in some contexts"),
        ("4", "soft", "number 4 — taboo (death)"),
    ],
    "hindi_translit": [
        ("bhen", "hard", "vulgar (sister + sexual)"),
        ("bhain", "hard", "vulgar"),
        ("lund", "hard", "vulgar (penis)"),
        ("chod", "hard", "vulgar (f**k)"),
        ("chut", "hard", "vulgar (vagina)"),
        ("madarchod", "hard", "vulgar"),
        ("kutta", "soft", "literal 'dog' but used as insult"),
        ("haram", "soft", "Arabic-origin 'forbidden' — religious sensitivity"),
    ],
    "french": [
        ("con", "hard", "vulgar (vagina/idiot)"),
        ("merde", "hard", "vulgar (sh*t)"),
        ("putain", "hard", "vulgar (whore/expletive)"),
        ("baise", "hard", "vulgar (f**k)"),
        ("cul", "soft", "vulgar (buttocks)"),
        ("salope", "hard", "slur"),
        ("connard", "hard", "vulgar (a**hole)"),
    ],
    "german": [
        ("fick", "hard", "vulgar (f**k)"),
        ("ficken", "hard", "vulgar"),
        ("scheiss", "hard", "vulgar (sh*t)"),
        ("scheisse", "hard", "vulgar"),
        ("arsch", "hard", "vulgar"),
        ("gift", "soft", "false friend: German 'Gift' = poison, not present"),
        ("vicks", "soft", "homophone of 'ficken' — see Vicks/Wick case"),
        ("mist", "soft", "literal 'manure' / mild expletive"),
    ],
    "turkish": [
        ("amk", "hard", "vulgar abbreviation"),
        ("am", "soft", "vulgar root (vagina) — must check ending"),
        ("bok", "hard", "vulgar (sh*t/excrement)"),
        ("got", "soft", "vulgar (buttocks) — 'göt'"),
        ("gotver", "hard", "vulgar"),
        ("siktir", "hard", "vulgar"),
        ("sik", "hard", "vulgar (penis)"),
        ("orospu", "hard", "vulgar"),
        ("piç", "hard", "vulgar"),
        ("pic", "hard", "vulgar (transliterated)"),
    ],
}

# ============================================================
# Cultural Number Taboo (separate check)
# ============================================================
NUMBER_TABOOS = {
    "4": ("China/Japan/Korea", "homophone of death (sì 死, shi 死)"),
    "9": ("Japan", "homophone of suffering (ku 苦)"),
    "13": ("Western", "Christian taboo (Last Supper)"),
    "666": ("Christian world", "Number of the Beast"),
}

# ============================================================
# Levenshtein Distance for Fuzzy Matching
# ============================================================

def levenshtein(a: str, b: str) -> int:
    """Standard Levenshtein distance."""
    if len(a) < len(b):
        return levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    previous_row = range(len(b) + 1)
    for i, ca in enumerate(a):
        current_row = [i + 1]
        for j, cb in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (ca != cb)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


# ============================================================
# Core Check Function
# ============================================================

def check_name_in_language(name: str, lang: str, blocklist: List[Tuple[str, str, str]]) -> List[Dict]:
    """Check a single name against a single language's blocklist.

    Matching policy:
    - Patterns of 4+ chars: simple substring match (e.g., 'pajero' inside 'mitsubishipajero')
    - Patterns of ≤3 chars: only match if pattern is at name start, name end, or
      the entire name (avoids false positives like 'pic' inside 'anthroPIC')
    - Patterns of ≤4 chars also get Levenshtein-1 fuzzy match against full name
    """
    name_lower = name.lower()
    findings = []

    for pattern, severity, gloss in blocklist:
        plen = len(pattern)
        matched = False
        match_type = None

        if plen >= 4:
            # Long pattern: simple substring is meaningful
            if pattern in name_lower:
                matched = True
                match_type = "substring"
        else:
            # Short pattern (≤3 chars): require word-boundary placement
            # to avoid false positives (e.g., 'pic' in 'anthropic')
            if name_lower == pattern:
                matched = True
                match_type = "exact"
            elif name_lower.startswith(pattern) and len(name_lower) <= plen + 2:
                matched = True
                match_type = "prefix (short name)"
            elif name_lower.endswith(pattern) and len(name_lower) <= plen + 2:
                matched = True
                match_type = "suffix (short name)"

        if matched:
            findings.append({
                "language": lang,
                "pattern": pattern,
                "severity": severity,
                "gloss": gloss,
                "match_type": match_type
            })
            continue

        # Levenshtein-1 fuzzy match for short patterns + short names
        if plen <= 4 and len(name_lower) <= plen + 2:
            if levenshtein(name_lower, pattern) <= 1:
                findings.append({
                    "language": lang,
                    "pattern": pattern,
                    "severity": severity,
                    "gloss": gloss,
                    "match_type": "fuzzy (Levenshtein-1)"
                })
    return findings


def check_number_taboos(name: str) -> List[Dict]:
    """Check for taboo numbers in name."""
    findings = []
    for num, (region, reason) in NUMBER_TABOOS.items():
        if num in name:
            findings.append({
                "language": "numerical",
                "pattern": num,
                "severity": "soft",
                "gloss": f"taboo in {region} — {reason}",
                "match_type": "number"
            })
    return findings


# ============================================================
# Verdict Computation
# ============================================================

def compute_verdict(findings: List[Dict]) -> Tuple[str, str]:
    """
    Aggregate findings into final verdict.
    Returns (verdict_label, color_code).
    """
    if not findings:
        return ("GREEN", "✓ Clean across 8 languages — finalist-ready")

    hard_count = sum(1 for f in findings if f["severity"] == "hard")
    soft_count = sum(1 for f in findings if f["severity"] == "soft")
    languages_flagged = set(f["language"] for f in findings)

    if hard_count >= 1:
        return ("RED", f"✗ Hard taboo flagged ({hard_count} severe in {len(languages_flagged)} language(s)) — REJECT")
    if soft_count >= 2 or len(languages_flagged) >= 2:
        return ("ORANGE", f"⚠ Multiple soft flags ({soft_count} in {len(languages_flagged)} language(s)) — reconsider")
    return ("YELLOW", f"⚠ One soft flag ({soft_count}) — finalist with documented trade-off")


# ============================================================
# Main Analysis
# ============================================================

def analyze(name: str) -> Dict:
    name_clean = name.strip()
    all_findings = []

    for lang, blocklist in BLOCKLISTS.items():
        findings = check_name_in_language(name_clean, lang, blocklist)
        all_findings.extend(findings)

    # Number taboos
    all_findings.extend(check_number_taboos(name_clean))

    verdict, msg = compute_verdict(all_findings)

    return {
        "name": name_clean,
        "verdict": verdict,
        "message": msg,
        "findings": all_findings,
    }


# ============================================================
# Pretty Printer
# ============================================================

def format_report(analysis: Dict) -> str:
    n = analysis
    color_marker = {
        "GREEN": "🟢",
        "YELLOW": "🟡",
        "ORANGE": "🟠",
        "RED": "🔴",
    }.get(n["verdict"], "?")

    out = f"""
═══════════════════════════════════════════════════════
NAME: {n['name']}
═══════════════════════════════════════════════════════
VERDICT: {color_marker} {n['verdict']}
{n['message']}
"""

    if n["findings"]:
        out += "\nFlags found:\n"
        for f in n["findings"]:
            out += (
                f"  • [{f['language']}] '{f['pattern']}' ({f['severity']}, {f['match_type']})\n"
                f"    → {f['gloss']}\n"
            )
    else:
        out += "\nNo flags detected in any of the 9 language blocklists.\n"

    out += """
RECOMMENDATION:
"""
    if n["verdict"] == "GREEN":
        out += "  ✓ Proceed to finalist tier. Native-speaker verification still recommended for Mandarin/Arabic if those are critical target markets.\n"
    elif n["verdict"] == "YELLOW":
        out += "  ⚠ Document the trade-off in the report. Consider native-speaker review for the flagged language.\n"
    elif n["verdict"] == "ORANGE":
        out += "  ⚠ Reconsider this candidate. Multiple soft flags suggest cross-cultural risk.\n"
    elif n["verdict"] == "RED":
        out += "  ✗ Reject this candidate. Hard taboo flag in target market would damage brand.\n"

    out += "═══════════════════════════════════════════════════════\n"
    return out


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python disaster_checker.py <Name1> [Name2] ...")
        print('Example: python disaster_checker.py "Lumio" "Pajero" "Verzo"')
        sys.exit(1)

    names = sys.argv[1:]
    print(f"\n# Multi-Language Disaster Check Report — {len(names)} candidate(s)")
    print(f"# Brand-Maker v1.0 — disaster_checker.py")
    print(f"# Languages checked: EN, ES, AR, RU, ZH, HI, FR, DE, TR + numerical taboos\n")
    print(f"# DISCLAIMER: Heuristic check. Native-speaker verification mandatory for critical markets.\n")

    for name in names:
        print(format_report(analyze(name)))


if __name__ == "__main__":
    main()
