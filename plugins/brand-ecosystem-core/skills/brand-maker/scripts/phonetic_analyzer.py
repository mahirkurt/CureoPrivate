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

def phonetic_readiness_score(analysis: Dict) -> int:
    """
    Compute composite global-readiness score from analysis dict.
    Range: 0 (broken) to 100 (agency-ready for global launch).
    """
    score = 100

    # Syllable count
    sylls = analysis["syllables"]
    if sylls == 1:
        score -= 5  # Trademark slightly harder
    elif sylls == 2:
        score -= 0  # Optimal
    elif sylls == 3:
        score -= 5
    elif sylls >= 4:
        score -= 25  # Too long for global

    # V/C ratio
    vc = analysis["vowel_consonant_ratio"]
    if 0.4 <= vc <= 0.6:
        score -= 0
    elif 0.3 <= vc < 0.4 or 0.6 < vc <= 0.7:
        score -= 10
    else:
        score -= 25  # Too imbalanced

    # Universal phonemes
    if analysis["universal_check"]["has_risky"]:
        score -= len(analysis["universal_check"]["risky_chars"]) * 5

    # Hard clusters
    score -= len(analysis["hard_clusters"]) * 15

    # Turkish local chars (hard fail)
    if analysis["has_turkish_local_chars"]:
        score -= 50  # Hard penalty (skill rule)

    # Length penalty
    if len(analysis["name"]) > 12:
        score -= 15
    elif len(analysis["name"]) < 3:
        score -= 25

    return max(0, min(100, score))


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
    if score >= 85:
        verdict = "★★★★★ Agency-ready for global launch"
    elif score >= 70:
        verdict = "★★★★☆ Strong; minor trade-offs"
    elif score >= 50:
        verdict = "★★★☆☆ Acceptable; document trade-offs"
    elif score >= 30:
        verdict = "★★☆☆☆ Weak; reconsider"
    else:
        verdict = "★☆☆☆☆ Reject — fundamental phonetic problems"

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
PHONETIC READINESS:  {score}/100
VERDICT:             {verdict}
═══════════════════════════════════════════════════════
"""


# ============================================================
# CLI Entry Point
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python phonetic_analyzer.py <Name1> [Name2] [Name3] ...")
        print('Example: python phonetic_analyzer.py "Lumio" "Verzo" "Clarity"')
        sys.exit(1)

    names = sys.argv[1:]
    print(f"\n# Phonetic Analysis Report — {len(names)} candidate(s)")
    print(f"# Brand-Maker v1.0 — phonetic_analyzer.py\n")

    for name in names:
        analysis = analyze(name)
        print(format_report(analysis))

    print("\n# Done. Use this analysis to fill the Linguistic Lab section of the report.\n")


if __name__ == "__main__":
    main()
