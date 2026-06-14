#!/usr/bin/env python3
"""
llm_namespace_probe.py — LLM Namespace Cleanliness Probe

Finalist ismin 4 LLM proxy (ChatGPT/Claude/Gemini/Perplexity) tarafından
hangi entity'ye bağlandığını ölçer. Post-Digital Validation Axis 1.

NOTE: This script provides the INTERFACE and CLASSIFICATION LOGIC for probe
results. Actual LLM surface queries must be executed via claude.ai's
`web_search` tool at runtime (outside this script). This script accepts
either:
  (a) Manual probe results via --probe-results JSON input
  (b) Fallback heuristic mode via --heuristic (no live queries)
  (c) Cached probe dataset via --cache-dir

Usage:
    python llm_namespace_probe.py "BrandName"
    python llm_namespace_probe.py --heuristic "BrandName"
    python llm_namespace_probe.py --probe-results probe.json "BrandName"
    python llm_namespace_probe.py --json "BrandName"

Scoring (Axis 1 — 0-2 points):
    2 = Clean (no prominent entity found across 4 LLM surfaces)
    1 = Ambiguous (low-prominence entity OR inconsistent surface responses)
    0 = Collision (prominent existing entity) OR Hallucination magnet (4/4 inconsistent)
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Hardcoded well-known entities for heuristic fallback
KNOWN_FAMOUS_NAMES = {
    "apple", "google", "microsoft", "amazon", "meta", "facebook", "twitter", "x",
    "tesla", "nike", "adidas", "coca-cola", "pepsi", "netflix", "disney", "pixar",
    "youtube", "instagram", "linkedin", "slack", "zoom", "spotify", "uber", "airbnb",
    "openai", "anthropic", "claude", "gpt", "chatgpt", "gemini", "bard", "perplexity",
    "mistral", "groq", "arc", "vercel", "stripe", "notion", "figma", "canva",
    "roche", "pfizer", "novartis", "merck", "astrazeneca", "sanofi", "gsk",
    "keytruda", "opdivo", "herceptin", "humira", "ozempic", "wegovy", "mounjaro"
}


def classify_probe_response(response_text, name):
    """
    Classify a single LLM probe response into one of four categories:
    clean, ambiguous, collision, hallucination.
    """
    if not response_text:
        return "clean", []
    
    text_lower = response_text.lower()
    name_lower = name.lower()
    
    # Detection heuristics
    clean_signals = [
        "i don't have information", "not familiar with", "don't recognize",
        "no established", "no notable", "i'm not aware", "cannot find",
        "no significant entity", "tanımadığım", "hakkında bilgim yok"
    ]
    
    if any(signal in text_lower for signal in clean_signals):
        return "clean", []
    
    # Extract named entities (very rough heuristic: capitalized words)
    entities = extract_entities(response_text)
    relevant_entities = [e for e in entities if e.lower() != name_lower]
    
    if len(relevant_entities) == 0:
        return "clean", []
    elif len(relevant_entities) == 1:
        # Single entity found - check prominence
        if relevant_entities[0].lower() in KNOWN_FAMOUS_NAMES:
            return "collision", relevant_entities
        else:
            return "ambiguous", relevant_entities
    elif len(relevant_entities) >= 3:
        return "hallucination", relevant_entities
    else:
        # 2 entities — ambiguous territory
        any_famous = any(e.lower() in KNOWN_FAMOUS_NAMES for e in relevant_entities)
        return ("collision" if any_famous else "ambiguous"), relevant_entities


def extract_entities(text):
    """
    Rough named-entity extraction: capitalized multi-word phrases.
    Returns list of unique entities.
    """
    # Pattern: proper nouns (capitalized words, possibly multi-word)
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    matches = re.findall(pattern, text)
    
    # Filter common English non-entity capitalized words
    stopwords = {
        "The", "A", "An", "This", "That", "These", "Those", "It", "I",
        "Is", "Are", "Was", "Were", "Has", "Have", "Had", "Do", "Does", "Did",
        "And", "Or", "But", "So", "Then", "However", "Therefore"
    }
    
    entities = [m for m in matches if m not in stopwords]
    return list(dict.fromkeys(entities))  # dedup preserving order


def heuristic_mode(name):
    """
    Fallback heuristic mode — no live LLM queries.
    Uses known famous marks list + name characteristics.
    """
    name_lower = name.lower()
    
    # Is the name itself a famous mark?
    if name_lower in KNOWN_FAMOUS_NAMES:
        return {
            "classification": "collision",
            "entities_detected": [name],
            "confidence": 0.95,
            "rationale": f"'{name}' is a well-known global brand. High collision risk."
        }
    
    # Is it a substring/superstring of a famous mark?
    adjacent = [m for m in KNOWN_FAMOUS_NAMES if m in name_lower or name_lower in m]
    if adjacent:
        return {
            "classification": "ambiguous",
            "entities_detected": adjacent[:3],
            "confidence": 0.65,
            "rationale": f"'{name}' is adjacent to known famous marks: {adjacent[:3]}"
        }
    
    # Is the name a common English word?
    common_word_pattern = re.match(r'^[a-z]{4,10}$', name_lower)
    if common_word_pattern:
        return {
            "classification": "ambiguous",
            "entities_detected": [],
            "confidence": 0.40,
            "rationale": f"'{name}' resembles a common word. Manual LLM probe recommended."
        }
    
    # Likely coined / clean
    return {
        "classification": "clean",
        "entities_detected": [],
        "confidence": 0.55,
        "rationale": f"'{name}' appears to be a coined or distinctive name. Heuristic-only assessment."
    }


def aggregate_score(probe_results):
    """
    Combine 4 LLM probe classifications into single Axis 1 score.
    
    Input: dict with 4 LLM entries, each having "classification" field.
    Output: (score 0-2, rationale string)
    """
    classifications = [r.get("classification", "unknown") for r in probe_results.values()]
    
    collision_count = classifications.count("collision")
    ambiguous_count = classifications.count("ambiguous")
    hallucination_count = classifications.count("hallucination")
    clean_count = classifications.count("clean")
    
    # Hallucination magnet: inconsistent responses
    if hallucination_count >= 2 or len(set(classifications)) >= 3:
        return (0, f"HALLUCINATION MAGNET — inconsistent LLM responses across {len(classifications)} surfaces. Brand-to-entity mapping unreliable.")
    
    # High collision: ≥2 LLMs link to established entity
    if collision_count >= 2:
        return (0, f"COLLISION — {collision_count}/{len(classifications)} LLM surfaces link to established entity(ies). Namespace occupied.")
    
    # Moderate collision or ambiguous
    if collision_count == 1 or ambiguous_count >= 2:
        return (1, f"AMBIGUOUS — {collision_count} collision + {ambiguous_count} ambiguous responses. Soft-flag for namespace planning.")
    
    # Mostly clean
    if clean_count >= 3:
        return (2, f"CLEAN NAMESPACE — {clean_count}/{len(classifications)} LLM surfaces return no established entity. Excellent LLM discoverability potential.")
    
    # Fallback for mixed
    return (1, "ACCEPTABLE WITH NOTE — Mixed probe signals; manual review recommended.")


def probe_llm_namespace(name, mode="heuristic", probe_results_json=None, depth="standard"):
    """
    Main probe function.
    
    mode: "heuristic" (no live queries) | "manual" (use provided probe_results_json)
    depth: "standard" (1 prompt per LLM) | "deep" (3 prompts per LLM)
    """
    result = {
        "name": name,
        "mode": mode,
        "depth": depth,
        "probes": {},
        "aggregate_score": None,
        "rationale": None
    }
    
    if mode == "heuristic":
        h = heuristic_mode(name)
        # Simulate 4 identical heuristic responses
        for llm in ["chatgpt_proxy", "claude_proxy", "gemini_proxy", "perplexity_proxy"]:
            result["probes"][llm] = {
                "classification": h["classification"],
                "entities_detected": h["entities_detected"],
                "confidence": h["confidence"],
                "rationale": h["rationale"]
            }
        score, rationale = aggregate_score(result["probes"])
        result["aggregate_score"] = score
        result["rationale"] = f"[HEURISTIC MODE — no live LLM queries] {rationale}"
        result["note"] = "For production use, invoke this script with actual web_search results via --probe-results JSON file."
    
    elif mode == "manual" and probe_results_json:
        try:
            with open(probe_results_json, "r", encoding="utf-8") as f:
                manual_results = json.load(f)
            for llm in ["chatgpt_proxy", "claude_proxy", "gemini_proxy", "perplexity_proxy"]:
                if llm in manual_results:
                    response_text = manual_results[llm].get("response", "")
                    cls, entities = classify_probe_response(response_text, name)
                    result["probes"][llm] = {
                        "classification": cls,
                        "entities_detected": entities,
                        "raw_response_preview": response_text[:200]
                    }
            score, rationale = aggregate_score(result["probes"])
            result["aggregate_score"] = score
            result["rationale"] = rationale
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"ERROR loading probe results: {e}", file=sys.stderr)
            # Fallback to heuristic
            return probe_llm_namespace(name, mode="heuristic")
    
    return result


def format_human_output(result):
    """Human-readable formatter."""
    lines = []
    lines.append(f"=== LLM Namespace Probe — \"{result['name']}\" ===\n")
    lines.append(f"Mode: {result['mode']}")
    lines.append(f"Depth: {result['depth']}\n")
    
    for llm, probe in result["probes"].items():
        lines.append(f"{llm}: {probe['classification'].upper()}")
        if probe.get("entities_detected"):
            lines.append(f"  Detected entities: {probe['entities_detected']}")
        if "confidence" in probe:
            lines.append(f"  Confidence: {probe['confidence']:.2f}")
        if probe.get("rationale"):
            lines.append(f"  Rationale: {probe['rationale']}")
        lines.append("")
    
    lines.append(f"AGGREGATE SCORE: {result['aggregate_score']}/2")
    lines.append(f"Rationale: {result['rationale']}")
    
    if result.get("note"):
        lines.append("")
        lines.append(f"Note: {result['note']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="LLM Namespace Probe for brand-maker Axis 1"
    )
    parser.add_argument("names", nargs="+", help="Brand name(s) to probe")
    parser.add_argument("--heuristic", action="store_true", help="Heuristic mode (no live queries)")
    parser.add_argument("--probe-results", default=None, help="JSON file with manual probe results")
    parser.add_argument("--deep", action="store_true", help="Deep probe (3 prompts per LLM)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    mode = "manual" if args.probe_results else "heuristic"
    depth = "deep" if args.deep else "standard"
    
    results = []
    for name in args.names:
        result = probe_llm_namespace(name, mode=mode, probe_results_json=args.probe_results, depth=depth)
        results.append(result)
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(format_human_output(result))
            print()


if __name__ == "__main__":
    main()
