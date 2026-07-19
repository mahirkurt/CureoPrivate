#!/usr/bin/env python3
"""
phonetic_analyzer.py — Brand-Maker Phonetic Analysis Tool

Simulates the methodology of `aparrish/pronouncingpy` (CMU Pronouncing Dictionary)
and applies global phonetic laws (Bouba-Kiki, Frequency Code, Sound Symbolism)
to candidate brand names.

USAGE:
    python phonetic_analyzer.py "Lumio" "Verzo" "Clarity"

DEPENDENCIES: Pure Python 3.8+, no external libraries required.

OUTPUT: Per-name structured analysis covering:
  - Syllable count + estimated stress pattern
  - Vowel-consonant ratio
  - Universal phoneme inventory check
  - Bouba-Kiki classification (round vs spiky)
  - Frequency code (small-fast vs big-strong)
  - 5x repeat test heuristic
  - Overall phonetic readiness score (0-100)
"""

import re
import sys
from typing import Dict, List, Tuple

# ============================================================
# Phonetic Constants (Universal Phoneme Inventory + Sound Symbolism)
# ============================================================

VOWELS = set("aeiouAEIOU")
VOWELS_FRONT = set("ieIE")  # high frequency → small/fast/light
VOWELS_BACK = set("ouOU")   # low frequency → big/heavy/strong
VOWELS_MID = set("aA")      # neutral

# Bouba (round/warm): liquid + nasal + back vowels
BOUBA_CONSONANTS = set("lmnrwLMNRW")
# Kiki (spiky/sharp): hard stops + voiceless fricatives + front vowels
KIKI_CONSONANTS = set("kptxzKPTXZ")

# Universal Phoneme Inventory — sounds present in 30+ major world languages
UNIVERSAL_CONSONANTS = set("pbtdkgfsmnlrPBTDKGFSMNLR")
RISKY_CONSONANTS = set("qwxyQWXY")  # not universal; require care
# Note: 'h' is widely understood; 'v' is missing in Mandarin/Spanish but tolerated

# Hard cluster patterns that break in Mandarin/Japanese transliteration
HARD_CLUSTERS = [
    "sch", "str", "spl", "shr", "thr", "phl", "kn", "ps", "pt",
    "rkst", "rgst", "ngst", "tch", "dge", "rkst", "ngth"
]

# ============================================================
# v2.1 — score-discrimination constants (expert-audit remediation C)
# ============================================================
# The 2026 audit found phonetic scores piling at 95-100 for most candidates:
# the scale conflated "easy to pronounce" with "strong corporate brand". Those
# are DIFFERENT axes. A smooth -anza coined word is easy to say (high ease) yet
# weak as an ownable corporate mark (template genericness, me-too register). We
# now compute TWO axes and a spread composite.

import re as _re  # already imported below; alias kept for clarity in this block

# Saturated terminal morpheme family the audit flagged (-anza/-anta/-onta/…):
# a vowel + n + (z|t) + vowel. Template genericness → brand-strength penalty.
SATURATED_FAMILY_RE = re.compile(r"[aeiou]n[zt][aeiou]$")

# Overused algorithmic-coined suffixes (me-too register).
GENERIC_SUFFIXES = ["ify", "ly", "io", "ai", "sy", "zy", "ora", "era", "ara"]

# Distinctive consonants that aid ownability when used with intent.
DISTINCTIVE_LETTERS = set("kxzqjv")

# ============================================================
# Heuristic Syllable Counter (English-leaning, language-agnostic)
# ============================================================

def count_syllables(name: str) -> int:
    """
    Heuristic syllable counter. Counts vowel groups; adjusts for
    common English patterns (silent e, diphthongs).

    Not perfect for coined/foreign names but agency-grade reliable
    for 90%+ of brand candidates.
    """
    name_lower = name.lower()
    # Remove common silent endings before counting
    word = re.sub(r"e$", "", name_lower) if len(name_lower) > 3 and name_lower.endswith("e") else name_lower
    # Remove non-letters
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    # Count vowel groups (consecutive vowels = 1 syllable)
    syllables = len(re.findall(r"[aeiouy]+", word))
    # Minimum 1 if word has any letters
    return max(1, syllables)


def estimate_stress(name: str) -> str:
    """
    Estimate stress pattern. English default is trochaic for 2-syll
    (DA-da). For 3-syll, depends on suffix.

    Returns: "trochaic" | "iambic" | "dactyl" | "anapest" | "monosyllabic"
    """
    sylls = count_syllables(name)
    if sylls == 1:
        return "monosyllabic"
    if sylls == 2:
        # Default English: trochaic (apple, google, netflix)
        return "trochaic"
    if sylls == 3:
        # Names ending in -ly, -tion, -ic → typically trochaic on 1st
        # Names like "Patagonia" are amphibrach
        if re.search(r"(ic|ix|ek|ek|ex|us|um)$", name.lower()):
            return "trochaic"
        return "dactyl"  # DA-da-da default
    return "polysyllabic"


# ============================================================
# Sound Symbolism Classifiers
# ============================================================

def classify_bouba_kiki(name: str) -> Tuple[str, float]:
    """
    Classify name on Bouba-Kiki spectrum.

    Returns: (label, score 0.0–1.0 where 0=most Bouba/round, 1=most Kiki/spiky)
    """
    bouba_count = sum(1 for c in name if c in BOUBA_CONSONANTS)
    kiki_count = sum(1 for c in name if c in KIKI_CONSONANTS)
    back_v = sum(1 for c in name if c in VOWELS_BACK)
    front_v = sum(1 for c in name if c in VOWELS_FRONT)

    bouba_total = bouba_count + back_v
    kiki_total = kiki_count + front_v
    if bouba_total + kiki_total == 0:
        return ("neutral", 0.5)

    spikiness = kiki_total / (bouba_total + kiki_total)
    if spikiness < 0.35:
        label = "round/warm (Bouba)"
    elif spikiness > 0.65:
        label = "spiky/sharp (Kiki)"
    else:
        label = "neutral/balanced"
    return (label, round(spikiness, 2))


def classify_frequency_code(name: str) -> str:
    """
    Ohala's Frequency Code: front vowels = small/fast, back vowels = big/strong.
    """
    front = sum(1 for c in name if c in VOWELS_FRONT)
    back = sum(1 for c in name if c in VOWELS_BACK)
    if front > back * 1.5:
        return "small / fast / light"
    if back > front * 1.5:
        return "big / strong / heavy"
    return "balanced"


# ============================================================
# Universal Phoneme & Cluster Checks
# ============================================================

def check_universal_phonemes(name: str) -> Dict:
    """
    Verify name uses only universal-inventory consonants.
    Flag risky consonants (q, w, x, y).
    """
    risky_found = [c for c in name if c in RISKY_CONSONANTS]
    return {
        "has_risky": len(risky_found) > 0,
        "risky_chars": list(set(risky_found)),
    }


def check_hard_clusters(name: str) -> List[str]:
    """Return list of hard consonant clusters found in name."""
    name_lower = name.lower()
    found = []
    for cluster in HARD_CLUSTERS:
        if cluster in name_lower:
            found.append(cluster)
    return found


def vowel_consonant_ratio(name: str) -> float:
    """Ratio of vowels to total letters (0.0–1.0)."""
    letters = [c for c in name if c.isalpha()]
    if not letters:
        return 0.0
    vowels = [c for c in letters if c in VOWELS]
    return round(len(vowels) / len(letters), 2)


# ============================================================
# Turkish-Character Block (skill rule: no Turkish-only chars)
# ============================================================

TURKISH_LOCAL_CHARS = set("şŞğĞçÇüÜöÖıİ")

def has_turkish_local_chars(name: str) -> bool:
    return any(c in TURKISH_LOCAL_CHARS for c in name)


# ============================================================
# Composite Phonetic Readiness Score (0-100)
# ============================================================

def pronunciation_ease_score(analysis: Dict) -> int:
    """
    AXIS 1 — pronunciation ease (0-100). How easy the name is to SAY across
    languages. A smooth coined word legitimately scores high here; that is fine
    — ease is not the same as brand strength (see brand_strength_score).
    """
    score = 100

    sylls = analysis["syllables"]
    if sylls == 1:
        score -= 5
    elif sylls == 2:
        score -= 0
    elif sylls == 3:
        score -= 5
    elif sylls >= 4:
        score -= 25

    vc = analysis["vowel_consonant_ratio"]
    if 0.4 <= vc <= 0.6:
        score -= 0
    elif 0.3 <= vc < 0.4 or 0.6 < vc <= 0.7:
        score -= 10
    else:
        score -= 25

    if analysis["universal_check"]["has_risky"]:
        score -= len(analysis["universal_check"]["risky_chars"]) * 5

    score -= len(analysis["hard_clusters"]) * 15

    if analysis["has_turkish_local_chars"]:
        score -= 50

    if len(analysis["name"]) > 12:
        score -= 15
    elif len(analysis["name"]) < 3:
        score -= 25

    return max(0, min(100, score))


def brand_strength_score(analysis: Dict) -> Dict:
    """
    AXIS 2 — corporate brand strength / distinctiveness / ownability (0-100).
    v2.1 (expert-audit remediation C): the OLD single score piled at 95-100
    because it measured only pronunciation ease. This axis measures whether the
    name is a STRONG, OWNABLE corporate mark — separating "easy to say" from
    "distinctive and defensible". Baseline is deliberately mid-scale (60), and
    it MOVES: template genericness, me-too register, and portfolio-confusable
    shapes pull it DOWN; intentional distinctiveness pulls it UP. This is what
    produces a real distribution instead of a ceiling.
    """
    name = analysis["name"]
    lower = re.sub(r"[^a-z]", "", name.lower())
    score = 60
    penalties = []
    credits = []

    # --- Template genericness: the -anza/-anta/-onta family the audit flagged.
    if SATURATED_FAMILY_RE.search(lower):
        score -= 28
        penalties.append("Saturated -anza/-anta/-onta template family "
                         "(algorithmic-coined register, weak ownability) -28")

    # --- Me-too algorithmic suffixes.
    for suf in GENERIC_SUFFIXES:
        if lower.endswith(suf) and not SATURATED_FAMILY_RE.search(lower):
            score -= 12
            penalties.append(f"Generic me-too suffix '-{suf}' -12")
            break

    # --- Register: purely soft vowel-final CV endings are common/low-effort;
    #     a hard-consonant or distinctive close reads more corporate/ownable.
    last = lower[-1] if lower else ""
    if last in "aeiou":
        # soft vowel-final: mild register penalty unless distinctiveness offsets
        score -= 6
        penalties.append("Soft vowel-final ending (product-register) -6")
    elif last in "kxztqcpg":
        score += 8
        credits.append("Hard-consonant close (corporate-register, memorable) +8")

    # --- Distinctiveness: intentional use of distinctive letters.
    distinctive = sum(1 for c in lower if c in DISTINCTIVE_LETTERS)
    if distinctive >= 1:
        bonus = min(14, distinctive * 7)
        score += bonus
        credits.append(f"{distinctive} distinctive letter(s) (k/x/z/q/j/v) +{bonus}")

    # --- Initial hard consonant aids recall/ownership (Kodak doctrine).
    if lower[:1] in "kxztqbdgp":
        score += 5
        credits.append("Strong initial consonant (recall/ownership) +5")

    # --- Length sweet spot for a corporate mark (5-9 chars).
    L = len(lower)
    if 5 <= L <= 9:
        score += 6
        credits.append("Corporate length sweet spot (5-9 chars) +6")
    elif L <= 3:
        score -= 12
        penalties.append("Too short — trademark-thin -12")
    elif L >= 12:
        score -= 10
        penalties.append("Too long for a corporate mark -10")

    # --- Dictionary-word / descriptive register would be weak; approximate via
    #     vowel/consonant balance extremes (over-vowel = soft/generic).
    vc = analysis["vowel_consonant_ratio"]
    if vc > 0.6:
        score -= 8
        penalties.append("Vowel-heavy (soft/generic, less distinctive) -8")

    score = max(0, min(100, score))
    if score >= 78:
        tier = "STRONG (Fanciful/Arbitrary register)"
    elif score >= 60:
        tier = "SOLID (Suggestive register)"
    elif score >= 42:
        tier = "WEAK (template/me-too register — reconsider)"
    else:
        tier = "POOR (generic/confusable — likely reject)"

    return {"score": score, "tier": tier, "penalties": penalties,
            "credits": credits}


def phonetic_readiness_score(analysis: Dict) -> int:
    """
    COMPOSITE readiness (0-100) — v2.1. Deliberately a BLEND of two distinct
    axes so it no longer saturates: pronunciation ease (weight 0.45) + brand
    strength (weight 0.55, the discriminating axis). Two names that are equally
    easy to say now separate on ownability, which is the whole point of the
    remediation. Backward-compatible field name preserved.
    """
    ease = analysis["pronunciation_ease"]
    strength = analysis["brand_strength"]["score"]
    composite = round(0.45 * ease + 0.55 * strength)
    return max(0, min(100, composite))


# ============================================================
# Main Analysis Function
# ============================================================

def analyze(name: str) -> Dict:
    """Perform complete phonetic analysis of a candidate name."""
    name = name.strip()
    analysis = {
        "name": name,
        "length": len(name),
        "syllables": count_syllables(name),
        "stress_pattern": estimate_stress(name),
        "vowel_consonant_ratio": vowel_consonant_ratio(name),
        "bouba_kiki": classify_bouba_kiki(name),
        "frequency_code": classify_frequency_code(name),
        "universal_check": check_universal_phonemes(name),
        "hard_clusters": check_hard_clusters(name),
        "has_turkish_local_chars": has_turkish_local_chars(name),
    }
    # v2.1 — two separate axes, then a discriminating composite.
    analysis["pronunciation_ease"] = pronunciation_ease_score(analysis)
    analysis["brand_strength"] = brand_strength_score(analysis)
    analysis["readiness_score"] = phonetic_readiness_score(analysis)
    return analysis


# ============================================================
# Pretty Printer
# ============================================================

def format_report(analysis: Dict) -> str:
    n = analysis
    bk_label, bk_score = n["bouba_kiki"]
    risky_warn = ""
    if n["universal_check"]["has_risky"]:
        risky_warn = f" — RISKY: {', '.join(n['universal_check']['risky_chars'])}"
    cluster_warn = ""
    if n["hard_clusters"]:
        cluster_warn = f" — HARD CLUSTERS: {', '.join(n['hard_clusters'])}"
    tr_warn = " — TURKISH LOCAL CHARS DETECTED (skill rule violation)" if n["has_turkish_local_chars"] else ""

    score = n["readiness_score"]
    ease = n["pronunciation_ease"]
    bs = n["brand_strength"]
    if score >= 82:
        verdict = "★★★★★ Agency-ready — strong & pronounceable"
    elif score >= 68:
        verdict = "★★★★☆ Strong; minor trade-offs"
    elif score >= 52:
        verdict = "★★★☆☆ Acceptable; document trade-offs"
    elif score >= 38:
        verdict = "★★☆☆☆ Weak; reconsider (often template/me-too register)"
    else:
        verdict = "★☆☆☆☆ Reject — fundamental problems"

    bs_lines = ""
    for c in bs["credits"]:
        bs_lines += f"                       + {c}\n"
    for p in bs["penalties"]:
        bs_lines += f"                       − {p}\n"

    return f"""
═══════════════════════════════════════════════════════
NAME: {n['name']}  (length: {n['length']})
═══════════════════════════════════════════════════════
Syllables:           {n['syllables']}
Stress pattern:      {n['stress_pattern']}
Vowel/Cons ratio:    {n['vowel_consonant_ratio']}  (target: 0.4–0.6)
Bouba-Kiki:          {bk_label}  (spikiness: {bk_score}/1.0)
Frequency code:      {n['frequency_code']}
Universal phonemes:  {'OK' if not n['universal_check']['has_risky'] else 'WARN'}{risky_warn}
Hard clusters:       {'none' if not n['hard_clusters'] else 'FLAGGED'}{cluster_warn}
Turkish local chars: {'OK' if not n['has_turkish_local_chars'] else 'VIOLATION'}{tr_warn}
───────────────────────────────────────────────────────
AXIS 1 — Pronunciation ease:  {ease}/100
AXIS 2 — Brand strength:      {bs['score']}/100  ({bs['tier']})
{bs_lines}───────────────────────────────────────────────────────
COMPOSITE READINESS:  {score}/100   (0.45·ease + 0.55·strength)
VERDICT:              {verdict}
═══════════════════════════════════════════════════════
"""


# ============================================================
# CLI Entry Point
# ============================================================

def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(
        description="Phonetic analysis with pronunciation/brand-strength axes (v2.1)")
    parser.add_argument("names", nargs="+", help="Brand name(s) to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    analyses = [analyze(name) for name in args.names]

    if args.json:
        print(json.dumps(analyses, indent=2, ensure_ascii=False))
        return

    print(f"\n# Phonetic Analysis Report — {len(args.names)} candidate(s)")
    print(f"# Brand-Maker v2.1 — phonetic_analyzer.py (2-axis: ease + strength)\n")
    for analysis in analyses:
        print(format_report(analysis))
    print("\n# Done. Use this analysis to fill the Linguistic Lab section of the report.\n")


if __name__ == "__main__":
    main()
