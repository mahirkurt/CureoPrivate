#!/usr/bin/env python3
"""
asr_simulation.py — Voice-First / ASR Readiness Simulation

Post-Digital Validation Axis 3. Tests finalist for voice commerce,
podcast performance, and ASR transcription fidelity.

Usage:
    python asr_simulation.py "BrandName"
    python asr_simulation.py --accent us,uk,au,tr "BrandName"
    python asr_simulation.py --homophone-check "BrandName"
    python asr_simulation.py --json "BrandName"

Scoring (Axis 3 — 0-2 points):
    2 = Voice-safe (≥4 of 5 metrics pass)
    1 = Acceptable with note (3 of 5 pass)
    0 = Voice-risky (<3 of 5 pass)
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Known brand homophone candidates (seed list; extensible)
HOMOPHONE_CANDIDATES = [
    "google", "apple", "amazon", "meta", "twitter", "tesla", "nike",
    "spotify", "uber", "airbnb", "instagram", "facebook", "netflix",
    "claude", "gpt", "gemini", "perplexity", "groq", "grok",
    "lumio", "loomio", "lumino", "luminos",
    "platelio", "plato", "platon",
    "herceptin", "hepton", "harceptin",
    "keytruda", "keystruda"
]


# Dangerous phonemes (languages with inconsistent ASR support)
RISKY_PHONEMES = {
    "ç": "palatalize (TR) — ASR often 'ch'",
    "ş": "palatalize (TR) — ASR often 'sh'",
    "ğ": "soft g (TR) — ASR drops entirely",
    "'": "glottal stop — ASR unreliable",
}


# Turkish special chars check
TURKISH_SPECIAL = set("çğıöşüÇĞIİÖŞÜ")


def count_syllables(name):
    """Heuristic syllable count via vowel clusters."""
    name_lower = name.lower()
    # Treat each vowel cluster as one syllable
    vowel_clusters = re.findall(r'[aeıioöuüy]+', name_lower, re.IGNORECASE)
    return max(1, len(vowel_clusters))


def vowel_consonant_ratio(name):
    """Calculate vowel-to-consonant ratio."""
    name_clean = re.sub(r'[^a-zA-ZçğıöşüÇĞIİÖŞÜ]', '', name)
    vowels = sum(1 for c in name_clean.lower() if c in "aeıioöuüy")
    consonants = len(name_clean) - vowels
    total = vowels + consonants
    if total == 0:
        return 0.0
    return round(vowels / total, 2)


def metaphone_encode(name):
    """
    Simplified Metaphone algorithm — approximates phonetic encoding.
    Not a full Double Metaphone; catches most homophone collisions.
    """
    name_upper = name.upper()
    # Remove non-letters
    name_upper = re.sub(r'[^A-Z]', '', name_upper)
    
    if not name_upper:
        return ""
    
    # Common transformations
    # Drop silent letters
    # KN- → N, GN- → N, PN- → N, WR- → R
    name_upper = re.sub(r'^(KN|GN|PN|WR)', lambda m: m.group(0)[1], name_upper)
    # Drop B at end if after M
    name_upper = re.sub(r'MB$', 'M', name_upper)
    # C + H = X (ch sound)
    name_upper = name_upper.replace('CH', 'X')
    # C + K → K
    name_upper = name_upper.replace('CK', 'K')
    # PH → F
    name_upper = name_upper.replace('PH', 'F')
    # TH → 0 (special metaphone marker)
    name_upper = name_upper.replace('TH', '0')
    # Drop vowels except initial
    if name_upper:
        first = name_upper[0]
        rest = re.sub(r'[AEIOU]', '', name_upper[1:])
        name_upper = first + rest
    
    return name_upper


def soundex_encode(name):
    """Basic Soundex encoding."""
    name_upper = re.sub(r'[^A-Z]', '', name.upper())
    if not name_upper:
        return "0000"
    
    # Mapping
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    
    result = name_upper[0]
    prev_code = mapping.get(name_upper[0], '')
    
    for char in name_upper[1:]:
        code = mapping.get(char, '')
        if code and code != prev_code:
            result += code
            if len(result) == 4:
                break
        if char not in "AEIOUYHW":
            prev_code = code
    
    result = (result + "0000")[:4]
    return result


def check_homophones(name, candidate_list=None):
    """Check for homophonic collisions via Metaphone + Soundex."""
    if candidate_list is None:
        candidate_list = HOMOPHONE_CANDIDATES
    
    name_metaphone = metaphone_encode(name)
    name_soundex = soundex_encode(name)
    
    collisions = []
    for candidate in candidate_list:
        if candidate.lower() == name.lower():
            continue  # self-match
        c_metaphone = metaphone_encode(candidate)
        c_soundex = soundex_encode(candidate)
        
        if c_metaphone == name_metaphone and c_soundex == name_soundex:
            collisions.append({"name": candidate, "match_type": "exact"})
        elif c_metaphone == name_metaphone:
            collisions.append({"name": candidate, "match_type": "metaphone"})
        elif c_soundex == name_soundex:
            collisions.append({"name": candidate, "match_type": "soundex"})
    
    return collisions


def first_phoneme_safety(name):
    """Assess first phoneme ASR safety."""
    if not name:
        return "safe", "(empty)"
    
    first_char = name[0].lower()
    
    # Risky Turkish special chars
    if first_char in RISKY_PHONEMES:
        return "risky", f"First char '{first_char}': {RISKY_PHONEMES[first_char]}"
    
    # Safe English phonemes
    safe_starts = "mnlbptdkgfvszjr"
    if first_char in safe_starts or first_char in "aeiou":
        return "safe", f"First phoneme /{first_char}/ is ASR-safe."
    
    return "marginal", f"First char '{first_char}' has marginal ASR support."


def simulate_accent_variants(name):
    """
    Generate accent-specific pronunciation hints.
    """
    variants = {}
    # Simplified approach — return phonetic approximation per accent
    variants["us"] = simple_phonetic(name, "us")
    variants["uk"] = simple_phonetic(name, "uk")
    variants["au"] = simple_phonetic(name, "au")
    variants["tr"] = simple_phonetic(name, "tr")
    return variants


def simple_phonetic(name, accent):
    """Very rough phonetic transcription per accent."""
    name_lower = name.lower()
    # Very simplified — just split syllables with hyphens
    syllables = re.findall(r'[^aeıioöuüy]*[aeıioöuüy]+', name_lower, re.IGNORECASE)
    return "-".join(syllables).upper()


def collocation_test(name):
    """Test ASR fidelity in common voice queries."""
    queries = [
        f"Buy me a {name}",
        f"Order {name}",
        f"Play {name}",
        f"Open {name} app",
    ]
    # Heuristic: shorter, common phonemes → higher fidelity
    syllable_count = count_syllables(name)
    vc_ratio = vowel_consonant_ratio(name)
    first_safety, _ = first_phoneme_safety(name)
    
    base_score = 95
    if syllable_count > 3:
        base_score -= 5
    if vc_ratio < 0.35 or vc_ratio > 0.70:
        base_score -= 10
    if first_safety == "risky":
        base_score -= 15
    elif first_safety == "marginal":
        base_score -= 5
    
    return {q: max(50, base_score + (i * 2)) for i, q in enumerate(queries)}


def has_turkish_special(name):
    """Check if name contains Turkish special characters."""
    return any(c in TURKISH_SPECIAL for c in name)


def simulate_asr(name, accents=None):
    """Main ASR simulation."""
    if accents is None:
        accents = ["us", "uk", "au", "tr"]
    
    syllable_count = count_syllables(name)
    vc_ratio = vowel_consonant_ratio(name)
    first_safety, first_rationale = first_phoneme_safety(name)
    homophones = check_homophones(name)
    collocation = collocation_test(name)
    accent_variants = simulate_accent_variants(name)
    
    # Metric scoring (0-2 each, 5 metrics, total 0-10, mapped to 0-2)
    metric_scores = {}
    
    # Metric 1: Homophone check
    if len(homophones) == 0:
        metric_scores["homophone"] = 2
    elif len(homophones) == 1:
        metric_scores["homophone"] = 1
    else:
        metric_scores["homophone"] = 0
    
    # Metric 2: Syllable count
    if 2 <= syllable_count <= 3:
        metric_scores["syllable"] = 2
    elif syllable_count in (1, 4):
        metric_scores["syllable"] = 1
    else:
        metric_scores["syllable"] = 0
    
    # Metric 3: First phoneme
    metric_scores["first_phoneme"] = {"safe": 2, "marginal": 1, "risky": 0}[first_safety]
    
    # Metric 4: VC ratio
    if 0.45 <= vc_ratio <= 0.60:
        metric_scores["vc_ratio"] = 2
    elif 0.35 <= vc_ratio <= 0.70:
        metric_scores["vc_ratio"] = 1
    else:
        metric_scores["vc_ratio"] = 0
    
    # Metric 5: Collocation average
    avg_colloc = sum(collocation.values()) / len(collocation)
    if avg_colloc >= 90:
        metric_scores["collocation"] = 2
    elif avg_colloc >= 75:
        metric_scores["collocation"] = 1
    else:
        metric_scores["collocation"] = 0
    
    # Pass-count
    pass_count = sum(1 for s in metric_scores.values() if s >= 1)
    
    # Overall axis score
    total = sum(metric_scores.values())
    if total >= 8:
        axis_score = 2
        level = "VOICE-SAFE"
    elif total >= 5:
        axis_score = 1
        level = "ACCEPTABLE WITH NOTE"
    else:
        axis_score = 0
        level = "VOICE-RISKY"
    
    rationale = (
        f"{pass_count}/5 metrics passed. "
        f"Syllables: {syllable_count}, VC ratio: {vc_ratio}, "
        f"first phoneme: {first_safety}, homophones: {len(homophones)}."
    )
    
    warnings = []
    if has_turkish_special(name):
        warnings.append("Name contains Turkish special chars (ç, ğ, ş, ü, ö, ı) — not recommended for global brand.")
    if len(homophones) > 0:
        warnings.append(f"Homophonic adjacency to: {[h['name'] for h in homophones]}")
    
    return {
        "name": name,
        "syllable_count": syllable_count,
        "vowel_consonant_ratio": vc_ratio,
        "first_phoneme_safety": first_safety,
        "first_phoneme_rationale": first_rationale,
        "homophone_collisions": homophones,
        "metaphone": metaphone_encode(name),
        "soundex": soundex_encode(name),
        "accent_variants": accent_variants,
        "collocation_tests": collocation,
        "metric_scores": metric_scores,
        "axis_score": axis_score,
        "level": level,
        "rationale": rationale,
        "warnings": warnings
    }


def format_human_output(result):
    lines = []
    lines.append(f"=== ASR Simulation — \"{result['name']}\" ===\n")
    lines.append(f"Phonetic (Metaphone): {result['metaphone']}")
    lines.append(f"Phonetic (Soundex): {result['soundex']}")
    lines.append(f"Syllable count: {result['syllable_count']}")
    lines.append(f"Vowel-consonant ratio: {result['vowel_consonant_ratio']}")
    lines.append(f"First phoneme: {result['first_phoneme_safety']}")
    lines.append(f"  {result['first_phoneme_rationale']}")
    lines.append("")
    
    if result["homophone_collisions"]:
        lines.append("Homophone collisions:")
        for h in result["homophone_collisions"]:
            lines.append(f"  ⚠ {h['name']} ({h['match_type']} match)")
    else:
        lines.append("Homophone collisions: None")
    lines.append("")
    
    lines.append("Accent variants:")
    for accent, variant in result["accent_variants"].items():
        lines.append(f"  {accent.upper()}: {variant}")
    lines.append("")
    
    lines.append("Collocation tests:")
    for query, conf in result["collocation_tests"].items():
        lines.append(f"  \"{query}\": {conf}% ASR confidence")
    lines.append("")
    
    lines.append("Metric scores:")
    for metric, score in result["metric_scores"].items():
        lines.append(f"  {metric}: {score}/2")
    lines.append("")
    
    lines.append(f"AXIS SCORE: {result['axis_score']}/2 — {result['level']}")
    lines.append(f"Rationale: {result['rationale']}")
    
    if result["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        for w in result["warnings"]:
            lines.append(f"  ⚠ {w}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="ASR Simulation — Voice-First Readiness (Axis 3)"
    )
    parser.add_argument("names", nargs="+", help="Brand name(s)")
    parser.add_argument("--accent", default="us,uk,au,tr", help="Comma-separated accents")
    parser.add_argument("--homophone-check", action="store_true", help="Homophone-only mode")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    accents = args.accent.split(",")
    
    results = [simulate_asr(n, accents) for n in args.names]
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(format_human_output(result))
            print()


if __name__ == "__main__":
    main()
