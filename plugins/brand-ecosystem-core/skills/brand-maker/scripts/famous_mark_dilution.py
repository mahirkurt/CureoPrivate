#!/usr/bin/env python3
"""
famous_mark_dilution.py — Famous-Mark 3-Layer Dilution Screen

Post-Digital Validation Axis 6. Tests finalist against top 500 global brands
via 3-layer proximity screen:
    Layer A — Levenshtein-2 direct proximity
    Layer B — Phonetic-3 proximity (homophonic)
    Layer C — Conceptual-aura proximity (Pixar-style)

Usage:
    python famous_mark_dilution.py "BrandName"
    python famous_mark_dilution.py --conceptual-check "PixarStyle" --category animation
    python famous_mark_dilution.py --json "BrandName"

Scoring (Axis 6 — 0-2 points):
    2 = 3/3 layers clean
    1 = 2/3 layers clean
    0 = ≤1/3 layers clean (high dilution risk)
"""

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_DB = Path(__file__).parent.parent / "data" / "famous_marks_2026.json"


def load_famous_marks(path=None):
    """Load famous marks database."""
    if path is None:
        path = DEFAULT_DB
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"WARNING: Famous marks DB not found at {path}. Using minimal fallback.", file=sys.stderr)
        return get_fallback_marks()
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def get_fallback_marks():
    """Minimal fallback famous marks list."""
    return {
        "metadata": {"source": "fallback", "total_marks": 20},
        "marks": [
            {"name": "Apple", "category": "technology", "conceptual_territory": ["minimalist computing", "premium electronics"]},
            {"name": "Google", "category": "technology", "conceptual_territory": ["web search", "AI platform"]},
            {"name": "Microsoft", "category": "technology", "conceptual_territory": ["enterprise software", "Windows OS"]},
            {"name": "Amazon", "category": "retail", "conceptual_territory": ["e-commerce", "cloud infrastructure"]},
            {"name": "Meta", "category": "technology", "conceptual_territory": ["social media", "VR/AR"]},
            {"name": "Tesla", "category": "automotive", "conceptual_territory": ["electric vehicles", "clean energy"]},
            {"name": "Nike", "category": "apparel", "conceptual_territory": ["athletic performance", "sport culture"]},
            {"name": "Coca-Cola", "category": "beverage", "conceptual_territory": ["classic soda", "americana"]},
            {"name": "Netflix", "category": "entertainment", "conceptual_territory": ["streaming service", "original content"]},
            {"name": "Disney", "category": "entertainment", "conceptual_territory": ["family entertainment", "animation heritage"]},
            {"name": "Pixar", "category": "entertainment", "conceptual_territory": ["animated family entertainment", "heartwarming storytelling", "computer animation craft"]},
            {"name": "McDonalds", "category": "food", "conceptual_territory": ["fast food", "americana"]},
            {"name": "Starbucks", "category": "food", "conceptual_territory": ["premium coffee", "third place"]},
            {"name": "Instagram", "category": "technology", "conceptual_territory": ["photo sharing", "visual social media"]},
            {"name": "TikTok", "category": "technology", "conceptual_territory": ["short video", "gen-z culture"]},
            {"name": "YouTube", "category": "technology", "conceptual_territory": ["video platform", "creator economy"]},
            {"name": "Uber", "category": "services", "conceptual_territory": ["ride-sharing", "gig economy"]},
            {"name": "Airbnb", "category": "services", "conceptual_territory": ["home-sharing", "travel"]},
            {"name": "Spotify", "category": "entertainment", "conceptual_territory": ["music streaming", "audio platform"]},
            {"name": "OpenAI", "category": "technology", "conceptual_territory": ["AI research", "ChatGPT"]},
            {"name": "Anthropic", "category": "technology", "conceptual_territory": ["AI safety", "Claude LLM"]}
        ]
    }


def levenshtein_distance(s1, s2):
    """Standard dynamic programming Levenshtein."""
    s1, s2 = s1.lower(), s2.lower()
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if not s2:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def metaphone_encode(name):
    """Simplified Metaphone."""
    name_upper = re.sub(r'[^A-Z]', '', name.upper())
    if not name_upper:
        return ""
    
    name_upper = re.sub(r'^(KN|GN|PN|WR)', lambda m: m.group(0)[1], name_upper)
    name_upper = re.sub(r'MB$', 'M', name_upper)
    name_upper = name_upper.replace('CH', 'X').replace('CK', 'K').replace('PH', 'F').replace('TH', '0')
    if name_upper:
        first = name_upper[0]
        rest = re.sub(r'[AEIOU]', '', name_upper[1:])
        name_upper = first + rest
    return name_upper


def soundex_encode(name):
    name_upper = re.sub(r'[^A-Z]', '', name.upper())
    if not name_upper:
        return "0000"
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3', 'L': '4', 'M': '5', 'N': '5', 'R': '6'
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
    return (result + "0000")[:4]


def layer_a_levenshtein(name, marks, threshold=2):
    """Layer A — Levenshtein-2 direct proximity."""
    matches = []
    for mark in marks:
        dist = levenshtein_distance(name, mark["name"])
        if dist <= threshold and name.lower() != mark["name"].lower():
            matches.append({"mark": mark["name"], "distance": dist, "category": mark.get("category")})
    # Sort by distance
    matches.sort(key=lambda m: m["distance"])
    return matches


def layer_b_phonetic(name, marks):
    """Layer B — Phonetic-3 proximity (Metaphone + Soundex)."""
    name_metaphone = metaphone_encode(name)
    name_soundex = soundex_encode(name)
    
    matches = []
    for mark in marks:
        m_metaphone = metaphone_encode(mark["name"])
        m_soundex = soundex_encode(mark["name"])
        
        # Check for match on either encoding
        if m_metaphone == name_metaphone and name.lower() != mark["name"].lower():
            matches.append({"mark": mark["name"], "match_type": "metaphone", "category": mark.get("category")})
        elif m_soundex == name_soundex and name.lower() != mark["name"].lower():
            matches.append({"mark": mark["name"], "match_type": "soundex", "category": mark.get("category")})
    return matches


def layer_c_conceptual_aura(name, marks, user_category=None):
    """
    Layer C — Conceptual-aura proximity.
    Heuristic: Does the name evoke any famous mark's conceptual territory?
    
    This is an approximation. Full evaluation requires LLM-assisted
    semantic reasoning. Heuristic flags possible exploitation for manual review.
    """
    name_lower = name.lower()
    
    # Look for explicit aura-flag keywords
    flags = []
    for mark in marks:
        territories = mark.get("conceptual_territory", [])
        for territory in territories:
            # Check if name contains territory keywords or substring of mark
            territory_keywords = re.findall(r'\w+', territory.lower())
            for kw in territory_keywords:
                if len(kw) >= 5 and kw in name_lower:
                    flags.append({
                        "mark": mark["name"],
                        "territory": territory,
                        "shared_keyword": kw
                    })
                    break
        # Also check if mark name is part of phrase
        if mark["name"].lower() in name_lower and mark["name"].lower() != name_lower:
            flags.append({
                "mark": mark["name"],
                "territory": "name-substring",
                "shared_keyword": mark["name"]
            })
    
    return flags


def check_famous_mark_dilution(name, famous_marks_db=None, user_category=None):
    """
    3-layer dilution check. Main analysis function.
    """
    db = load_famous_marks(famous_marks_db)
    marks = db.get("marks", [])
    
    layer_a = layer_a_levenshtein(name, marks)
    layer_b = layer_b_phonetic(name, marks)
    layer_c = layer_c_conceptual_aura(name, marks, user_category)
    
    # Layer pass/fail
    layer_a_pass = len(layer_a) == 0
    layer_b_pass = len(layer_b) == 0
    layer_c_pass = len(layer_c) == 0
    
    layers_passed = sum([layer_a_pass, layer_b_pass, layer_c_pass])
    
    # Axis score
    if layers_passed == 3:
        score = 2
        level = "CLEAN — all 3 layers pass"
    elif layers_passed == 2:
        score = 1
        level = "MARGINAL — 2/3 layers clean"
    elif layers_passed <= 1:
        score = 0
        level = "FAIL DILUTION SCREEN"
    
    rationale_parts = []
    if not layer_a_pass:
        closest = layer_a[0]
        rationale_parts.append(f"Layer A FAIL — distance {closest['distance']} from '{closest['mark']}'.")
    if not layer_b_pass:
        rationale_parts.append(f"Layer B FAIL — phonetic match: {[m['mark'] for m in layer_b]}.")
    if not layer_c_pass:
        rationale_parts.append(f"Layer C FAIL — conceptual-aura overlap with: {[f['mark'] for f in layer_c]}. Manual review recommended.")
    
    if layers_passed == 3:
        rationale_parts.append("No dilution proximity detected across all 3 layers.")
    
    rationale = " ".join(rationale_parts)
    
    return {
        "name": name,
        "user_category": user_category,
        "layer_a_levenshtein": {
            "pass": layer_a_pass,
            "matches": layer_a,
            "threshold": 2
        },
        "layer_b_phonetic": {
            "pass": layer_b_pass,
            "matches": layer_b
        },
        "layer_c_conceptual": {
            "pass": layer_c_pass,
            "flags": layer_c,
            "note": "Heuristic detection; manual review may be needed."
        },
        "layers_passed": layers_passed,
        "score": score,
        "level": level,
        "rationale": rationale,
        "database_metadata": db.get("metadata", {})
    }


def format_human_output(result):
    lines = []
    lines.append(f"=== Famous Mark Dilution Check — \"{result['name']}\" ===\n")
    
    # Layer A
    la = result["layer_a_levenshtein"]
    if la["pass"]:
        lines.append(f"LAYER A — Levenshtein-{la['threshold']} direct proximity: ✓ PASS")
    else:
        lines.append(f"LAYER A — Levenshtein-{la['threshold']} direct proximity: ✗ FAIL")
        for m in la["matches"]:
            lines.append(f"  - '{m['mark']}' (distance {m['distance']})")
    lines.append("")
    
    # Layer B
    lb = result["layer_b_phonetic"]
    if lb["pass"]:
        lines.append("LAYER B — Phonetic-3 (Metaphone+Soundex) proximity: ✓ PASS")
    else:
        lines.append("LAYER B — Phonetic-3 (Metaphone+Soundex) proximity: ✗ FAIL")
        for m in lb["matches"]:
            lines.append(f"  - '{m['mark']}' ({m['match_type']} match)")
    lines.append("")
    
    # Layer C
    lc = result["layer_c_conceptual"]
    if lc["pass"]:
        lines.append("LAYER C — Conceptual-aura proximity: ✓ PASS")
    else:
        lines.append("LAYER C — Conceptual-aura proximity: ✗ FAIL (heuristic flag)")
        for f in lc["flags"]:
            lines.append(f"  - '{f['mark']}' territory: '{f['territory']}' via '{f['shared_keyword']}'")
    lines.append("")
    
    lines.append(f"Layers passed: {result['layers_passed']}/3")
    lines.append(f"AXIS SCORE: {result['score']}/2 — {result['level']}")
    lines.append(f"Rationale: {result['rationale']}")
    lines.append("")
    lines.append(
        "DISCLAIMER: Layer C is heuristic; full conceptual-aura assessment "
        "requires LLM-assisted semantic reasoning and IP attorney review."
    )
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Famous Mark 3-Layer Dilution Screen (Axis 6)"
    )
    parser.add_argument("names", nargs="+", help="Brand name(s) to check")
    parser.add_argument("--famous-marks-db", default=None, help="Path to famous marks JSON")
    parser.add_argument("--category", default=None, help="User category context")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--conceptual-check", action="store_true", help="Only Layer C")
    
    args = parser.parse_args()
    
    results = [
        check_famous_mark_dilution(name, args.famous_marks_db, args.category)
        for name in args.names
    ]
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(format_human_output(result))
            print()


if __name__ == "__main__":
    main()
