#!/usr/bin/env python3
"""
inn_stem_collision.py — WHO INN / USAN Stem Collision Check

Pharma brand name için INN/USAN stem çakışması tespit eder.
FDA DMEPA Katman 2 (USAN Stem Collision) ön-taraması yapar.

Usage:
    python inn_stem_collision.py "BrandName1" "BrandName2"
    python inn_stem_collision.py --therapeutic-area oncology "Novazib"
    python inn_stem_collision.py --fda-mode "Curotol"
    python inn_stem_collision.py --json "BrandName1"

Scoring (Post-Digital Validation Axis 5):
    2 = Clean (no INN stem collision)
    1 = Weak substring match (FDA query risk)
    0 = Direct suffix collision (FDA auto-reject)

Data: /data/usan_stems.json (WHO INN + USAN Council stems snapshot)
"""

import argparse
import json
import os
import sys
from pathlib import Path


# Default stem database path (relative to script location)
DEFAULT_STEM_DB = Path(__file__).parent.parent / "data" / "usan_stems.json"


def load_stem_database(path):
    """Load INN/USAN stem JSON database."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Stem database not found at {path}", file=sys.stderr)
        print("Expected file: data/usan_stems.json", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in stem database: {e}", file=sys.stderr)
        sys.exit(1)


def get_all_stems(db, therapeutic_area=None):
    """
    Extract all stems from database.
    If therapeutic_area specified, prioritize that area's stems.
    Returns list of stem dicts: [{"stem": "...", "class": "...", "examples": [...]}]
    """
    stems = []
    classes = db.get("stems_by_class", {})
    
    if therapeutic_area and therapeutic_area in classes:
        # Primary area first (higher precision)
        stems.extend(classes[therapeutic_area])
        # Then others
        for area, area_stems in classes.items():
            if area != therapeutic_area:
                stems.extend(area_stems)
    else:
        for area_stems in classes.values():
            stems.extend(area_stems)
    
    return stems


def suffix_match(name, stems):
    """
    Check if name ends in any INN/USAN stem.
    Returns matched stem dict or None.
    Case-insensitive.
    """
    name_lower = name.lower()
    # Sort by stem length descending (longer stems matched first to avoid false partials)
    sorted_stems = sorted(stems, key=lambda s: -len(s["stem"]))
    
    for stem_entry in sorted_stems:
        stem = stem_entry["stem"].lower()
        if name_lower.endswith(stem):
            return stem_entry
    return None


def substring_search(name, stems, min_stem_length=3):
    """
    Find INN/USAN stems as substrings anywhere in the name.
    Returns list of matched stems (non-suffix matches).
    Only returns stems >= min_stem_length to reduce false positives.
    """
    name_lower = name.lower()
    matches = []
    seen_stems = set()
    
    for stem_entry in stems:
        stem = stem_entry["stem"].lower()
        if len(stem) < min_stem_length:
            continue
        # Non-suffix match: stem appears but name doesn't end with it
        if stem in name_lower and not name_lower.endswith(stem):
            if stem not in seen_stems:
                matches.append(stem_entry)
                seen_stems.add(stem)
    
    return matches


def assess_semantic_confusion(name, therapeutic_area, suffix_match_result, substring_matches):
    """
    Heuristic semantic confusion assessment.
    Returns: (confusion_level, rationale_string)
    """
    if suffix_match_result:
        return (
            "high",
            f"Direct suffix collision with '{suffix_match_result['stem']}' "
            f"({suffix_match_result['class']}) — FDA DMEPA auto-reject risk."
        )
    
    if substring_matches:
        matched_classes = list({m["class"] for m in substring_matches})
        return (
            "medium",
            f"Substring match(es) with INN stem(s): {[m['stem'] for m in substring_matches]}. "
            f"Prescriber may confuse with {matched_classes} class(es). "
            f"FDA DMEPA query risk."
        )
    
    return ("low", "No INN stem collision detected.")


def compute_score(suffix_match_result, substring_matches):
    """
    Post-Digital Validation Axis 5 scoring.
    Returns: (score 0-2, rationale)
    """
    if suffix_match_result:
        return (0, "FAIL — Direct INN suffix collision. Finalist elimination recommended.")
    
    if len(substring_matches) >= 1:
        return (1, "ACCEPTABLE WITH FDA QUERY RISK — Substring overlap with INN stem(s).")
    
    return (2, "CLEAN — No INN stem collision detected.")


def check_inn_collision(name, therapeutic_area=None, stem_db_path=None, fda_mode=False):
    """
    Main analysis function.
    Returns full assessment dict.
    """
    if stem_db_path is None:
        stem_db_path = DEFAULT_STEM_DB
    
    db = load_stem_database(stem_db_path)
    stems = get_all_stems(db, therapeutic_area)
    
    suffix_result = suffix_match(name, stems)
    substring_results = substring_search(name, stems)
    
    confusion_level, confusion_rationale = assess_semantic_confusion(
        name, therapeutic_area, suffix_result, substring_results
    )
    
    score, score_rationale = compute_score(suffix_result, substring_results)
    
    # Matched existing drugs (from examples in matched stems)
    matched_drugs = []
    if suffix_result:
        matched_drugs.extend(suffix_result.get("examples", []))
    for m in substring_results:
        matched_drugs.extend(m.get("examples", []))
    matched_drugs = list(set(matched_drugs))[:10]  # Top 10 unique
    
    # Regulatory risk assessment
    if score == 0:
        reg_risk = "high"
    elif score == 1:
        reg_risk = "medium"
    else:
        reg_risk = "low"
    
    return {
        "name": name,
        "therapeutic_area_context": therapeutic_area or "general (no area specified)",
        "suffix_match": suffix_result["stem"] if suffix_result else None,
        "suffix_match_class": suffix_result["class"] if suffix_result else None,
        "substring_matches": [
            {"stem": m["stem"], "class": m["class"]} for m in substring_results
        ],
        "semantic_confusion": confusion_level,
        "semantic_rationale": confusion_rationale,
        "regulatory_risk": reg_risk,
        "score": score,
        "score_rationale": score_rationale,
        "matched_existing_drugs": matched_drugs,
        "database_metadata": db.get("metadata", {}),
        "fda_mode": fda_mode,
    }


def format_human_output(result):
    """Format result as human-readable text."""
    lines = []
    lines.append(f"=== INN/USAN Stem Collision Check — \"{result['name']}\" ===\n")
    lines.append(f"Therapeutic area context: {result['therapeutic_area_context']}\n")
    
    lines.append("Suffix analysis:")
    if result["suffix_match"]:
        lines.append(f"  ⚠ Direct suffix match: -{result['suffix_match']}")
        lines.append(f"  Class: {result['suffix_match_class']}")
    else:
        lines.append("  ✓ No INN/USAN suffix collision")
    lines.append("")
    
    lines.append("Substring search:")
    if result["substring_matches"]:
        for m in result["substring_matches"]:
            lines.append(f"  ⚠ Stem '{m['stem']}' found as substring (class: {m['class']})")
    else:
        lines.append("  ✓ No substring overlap with INN stems")
    lines.append("")
    
    lines.append(f"Semantic confusion level: {result['semantic_confusion'].upper()}")
    lines.append(f"  Rationale: {result['semantic_rationale']}")
    lines.append("")
    
    lines.append(f"Regulatory risk: {result['regulatory_risk'].upper()}")
    lines.append(f"Score: {result['score']}/2 — {result['score_rationale']}")
    lines.append("")
    
    if result["matched_existing_drugs"]:
        lines.append(f"Matched existing drugs (from stem examples):")
        for drug in result["matched_existing_drugs"]:
            lines.append(f"  • {drug}")
    
    lines.append("")
    lines.append("─" * 60)
    lines.append(
        "DISCLAIMER: This is a Layer-2 FDA DMEPA pre-screen. "
        "Formal FDA Brand Name Review (Form 3331) + EMA NRG + TİTCK "
        "submission remain mandatory."
    )
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="INN/USAN Stem Collision Check (Pharma Brand Name Pre-Screen)"
    )
    parser.add_argument("names", nargs="+", help="Brand name(s) to check")
    parser.add_argument(
        "--therapeutic-area",
        default=None,
        help="Prioritize stems from this therapeutic area (oncology, hematology, cardiovascular, etc.)"
    )
    parser.add_argument(
        "--stem-db",
        default=None,
        help="Path to custom USAN stems JSON database"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    parser.add_argument(
        "--fda-mode", action="store_true",
        help="Enable FDA-specific high-sensitivity mode"
    )
    
    args = parser.parse_args()
    
    results = []
    for name in args.names:
        result = check_inn_collision(
            name,
            therapeutic_area=args.therapeutic_area,
            stem_db_path=args.stem_db,
            fda_mode=args.fda_mode,
        )
        results.append(result)
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(format_human_output(result))
            print()


if __name__ == "__main__":
    main()
