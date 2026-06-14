#!/usr/bin/env python3
"""
morpheme_saturation_check.py — Morpheme Saturation & AI-Fingerprint Detection

Post-Digital Validation Axis 2. Tests finalist against YC + ProductHunt
last-24-month morpheme frequency corpus to detect algorithmic genericism.

Usage:
    python morpheme_saturation_check.py "BrandName1" "BrandName2"
    python morpheme_saturation_check.py --corpus data/yc_ph_morpheme_corpus.json "Mealogram"
    python morpheme_saturation_check.py --json "Spotify"

Scoring (Axis 2 — 0-2 points):
    2 = Distinctive (pattern frequency <5)
    1 = Common but ownable (5-50)
    0 = Algorithmic generic (>50)
"""

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_CORPUS = Path(__file__).parent.parent / "data" / "yc_ph_morpheme_corpus.json"


# Known prefix/suffix candidates (heuristic morpheme segmentation)
COMMON_PREFIXES = [
    "medi", "derma", "gluco", "diabe", "neuro", "bio", "smart", "auto",
    "tech", "cyber", "eco", "green", "earth", "ai", "meta", "super",
    "hyper", "quick", "swift", "rapid", "pro", "ultra", "max", "mega",
    "micro", "nano", "pico", "poly", "multi", "omni"
]

COMMON_SUFFIXES = [
    "ify", "io", "ly", "os", "ai", "gpt", "y", "gram", "ic", "hub",
    "box", "kit", "lab", "app", "base", "core", "flow", "flex", "fi",
    "tech", "ware", "logy", "ous", "ify", "ize", "ease", "ise"
]


def load_corpus(path=None):
    """Load the morpheme frequency corpus."""
    if path is None:
        path = DEFAULT_CORPUS
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"WARNING: Corpus not found at {path}. Using empty defaults.", file=sys.stderr)
        return {
            "metadata": {"total_names_analyzed": 0},
            "prefixes": {},
            "suffixes": {},
            "patterns": {},
            "saturation_alerts": []
        }
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in corpus: {e}", file=sys.stderr)
        sys.exit(1)


def extract_morphemes(name):
    """
    Heuristic morpheme segmentation.
    Returns: {"prefix": str|None, "root": str, "suffix": str|None}
    """
    name_lower = name.lower()
    
    # Find longest prefix match
    prefix = None
    for p in sorted(COMMON_PREFIXES, key=lambda x: -len(x)):
        if name_lower.startswith(p) and len(name_lower) > len(p) + 1:
            prefix = p
            break
    
    # Find longest suffix match
    suffix = None
    for s in sorted(COMMON_SUFFIXES, key=lambda x: -len(x)):
        if name_lower.endswith(s) and len(name_lower) > len(s) + 1:
            suffix = s
            break
    
    # Extract root
    start = len(prefix) if prefix else 0
    end = len(name_lower) - len(suffix) if suffix else len(name_lower)
    root = name_lower[start:end]
    
    return {
        "prefix": prefix,
        "root": root,
        "suffix": suffix
    }


def detect_pattern(name):
    """
    Detect morphological pattern (CVC-ify, CVCV-io, etc.)
    Returns pattern string.
    """
    name_lower = name.lower()
    morphemes = extract_morphemes(name_lower)
    
    if morphemes["suffix"]:
        # Analyze root syllable structure
        root = morphemes["root"]
        vowels = re.findall(r'[aeiouy]+', root)
        syllable_count = len(vowels) if vowels else 1
        
        if syllable_count == 1:
            return f"1-syllable-{morphemes['suffix']}"
        elif syllable_count == 2:
            return f"2-syllable-{morphemes['suffix']}"
        else:
            return f"{syllable_count}-syllable-{morphemes['suffix']}"
    
    if morphemes["prefix"]:
        return f"{morphemes['prefix']}-X"
    
    # Fallback CVC pattern
    if re.match(r'^[bcdfghjklmnpqrstvwxz][aeiouy][bcdfghjklmnpqrstvwxz]$', name_lower):
        return "CVC-pure"
    
    return "coined-novel"


def find_similar_names(name, corpus, top_n=5):
    """Find N most similar names in corpus based on suffix/prefix sharing."""
    morphemes = extract_morphemes(name)
    similar = []
    
    catalog = corpus.get("full_name_catalog", [])
    
    # If catalog provided, use it; otherwise skip
    for existing_name in catalog:
        existing_lower = existing_name.lower()
        existing_morphemes = extract_morphemes(existing_lower)
        
        # Score similarity
        score = 0
        if morphemes["suffix"] and existing_morphemes["suffix"] == morphemes["suffix"]:
            score += 2
        if morphemes["prefix"] and existing_morphemes["prefix"] == morphemes["prefix"]:
            score += 2
        if len(existing_lower) == len(name.lower()):
            score += 1
        
        if score >= 2:
            similar.append((existing_name, score))
    
    similar.sort(key=lambda x: -x[1])
    return [n for n, _ in similar[:top_n]]


def compute_saturation(name, corpus):
    """
    Main saturation computation.
    Returns full analysis dict.
    """
    morphemes = extract_morphemes(name)
    pattern = detect_pattern(name)
    
    prefixes_freq = corpus.get("prefixes", {})
    suffixes_freq = corpus.get("suffixes", {})
    patterns_freq = corpus.get("patterns", {})
    
    prefix_frequency = prefixes_freq.get(morphemes["prefix"], 0) if morphemes["prefix"] else 0
    suffix_frequency = suffixes_freq.get(morphemes["suffix"], 0) if morphemes["suffix"] else 0
    pattern_frequency = patterns_freq.get(pattern, 0)
    
    # Aggregate saturation = max of the three (dominant signal)
    max_freq = max(prefix_frequency, suffix_frequency, pattern_frequency)
    
    # Scoring logic
    if max_freq >= 50:
        score = 0
        level = "ALGORITHMIC GENERIC"
        rationale = (
            f"Maximum morpheme frequency {max_freq} in last-24-month YC+PH corpus. "
            f"Pattern saturation HIGH — finalist likely to blend with AI-generated names. "
            f"Recommend rejecting or selecting distinctive alternative (E category)."
        )
    elif max_freq >= 5:
        score = 1
        level = "COMMON BUT OWNABLE"
        rationale = (
            f"Maximum morpheme frequency {max_freq}. Pattern common but not saturated. "
            f"Acceptable with documented strategic trade-off."
        )
    else:
        score = 2
        level = "DISTINCTIVE"
        rationale = f"Maximum morpheme frequency {max_freq}. Pattern distinctive — excellent AI-escape."
    
    similar = find_similar_names(name, corpus)
    
    return {
        "name": name,
        "morphemes": morphemes,
        "pattern": pattern,
        "prefix_frequency": prefix_frequency,
        "suffix_frequency": suffix_frequency,
        "pattern_frequency": pattern_frequency,
        "max_frequency": max_freq,
        "similar_names_in_corpus": similar,
        "level": level,
        "score": score,
        "rationale": rationale,
        "corpus_metadata": corpus.get("metadata", {})
    }


def format_human_output(result):
    """Format as human-readable text."""
    lines = []
    lines.append(f"=== Morpheme Saturation Check — \"{result['name']}\" ===\n")
    
    m = result["morphemes"]
    lines.append("Morpheme breakdown:")
    lines.append(f"  Prefix: {m['prefix'] or '(none)'} (frequency: {result['prefix_frequency']})")
    lines.append(f"  Root: '{m['root']}'")
    lines.append(f"  Suffix: {m['suffix'] or '(none)'} (frequency: {result['suffix_frequency']})")
    lines.append("")
    
    lines.append(f"Pattern: {result['pattern']}")
    lines.append(f"Pattern frequency: {result['pattern_frequency']}")
    lines.append(f"Max frequency: {result['max_frequency']}")
    lines.append("")
    
    if result["similar_names_in_corpus"]:
        lines.append(f"Similar names in corpus: {', '.join(result['similar_names_in_corpus'])}")
        lines.append("")
    
    lines.append(f"Level: {result['level']}")
    lines.append(f"Score: {result['score']}/2")
    lines.append(f"Rationale: {result['rationale']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Morpheme Saturation Check — AI-Fingerprint Avoidance (Axis 2)"
    )
    parser.add_argument("names", nargs="+", help="Brand name(s) to check")
    parser.add_argument("--corpus", default=None, help="Path to corpus JSON")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    corpus = load_corpus(args.corpus)
    
    results = [compute_saturation(name, corpus) for name in args.names]
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(format_human_output(result))
            print()


if __name__ == "__main__":
    main()
