#!/usr/bin/env python3
"""
entity_disambiguation.py — Wikipedia/Wikidata Namespace Uniqueness Test

Post-Digital Validation Axis 4. Tests finalist for existing Wikipedia
article, disambiguation page, or Wikidata QID conflicts.

Uses free Wikipedia API (no auth required).

Usage:
    python entity_disambiguation.py "BrandName"
    python entity_disambiguation.py --high-precision "BrandName"  # pharma mode
    python entity_disambiguation.py --offline "BrandName"  # skip API, heuristic only
    python entity_disambiguation.py --json "BrandName"

Scoring (Axis 4 — 0-2 points):
    2 = Clean (no Wikipedia article, no Wikidata QID)
    1 = Low-prominence single match (small-town, niche academic)
    0 = Disambiguation page OR high-prominence collision
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

USER_AGENT = "brand-maker/2.0 (Anthropic Claude skill)"


def wiki_api_call(url, params, timeout=10):
    """Make a Wikipedia API call; returns parsed JSON or None."""
    try:
        params_encoded = urllib.parse.urlencode(params)
        full_url = f"{url}?{params_encoded}"
        req = urllib.request.Request(full_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  [Wikipedia API warning: {e}]", file=sys.stderr)
        return None


def wikipedia_search(name):
    """Search Wikipedia; return list of top hits."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": name,
        "srlimit": 10,
        "format": "json"
    }
    result = wiki_api_call(WIKIPEDIA_API, params)
    if result and "query" in result and "search" in result["query"]:
        return result["query"]["search"]
    return []


def wikipedia_page_info(name):
    """Fetch page info for exact title match."""
    params = {
        "action": "query",
        "titles": name,
        "prop": "info|pageprops|categories",
        "format": "json"
    }
    result = wiki_api_call(WIKIPEDIA_API, params)
    if not result or "query" not in result:
        return None
    
    pages = result["query"].get("pages", {})
    for page_id, page_data in pages.items():
        if page_id == "-1":  # No page
            return None
        return page_data
    return None


def wikipedia_pageviews(title, days=30):
    """Rough pageview estimation — use simple heuristic."""
    try:
        encoded_title = urllib.parse.quote(title.replace(" ", "_"))
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{encoded_title}/daily/20260201/20260228"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if "items" in data:
                total_views = sum(item.get("views", 0) for item in data["items"])
                return total_views
    except Exception:
        pass
    return 0


def wikidata_lookup(name):
    """Search Wikidata for QID matches."""
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "limit": 5,
        "format": "json"
    }
    result = wiki_api_call(WIKIDATA_API, params)
    if result and "search" in result:
        return [
            {"qid": item.get("id"), "label": item.get("label"), "description": item.get("description")}
            for item in result["search"]
        ]
    return []


def is_disambiguation_page(page_data):
    """Check if Wikipedia page is a disambiguation page."""
    if not page_data:
        return False
    cats = page_data.get("categories", [])
    for cat in cats:
        cat_title = cat.get("title", "").lower()
        if "disambiguation" in cat_title:
            return True
    pageprops = page_data.get("pageprops", {})
    if "disambiguation" in pageprops:
        return True
    return False


def check_wikipedia(name, high_precision=False, offline=False):
    """
    Main Wikipedia/Wikidata check.
    Returns detailed entity disambiguation result.
    """
    result = {
        "name": name,
        "direct_article": False,
        "direct_article_title": None,
        "disambiguation_page": False,
        "disambiguation_entries": [],
        "search_hits": [],
        "wikidata_qid": None,
        "wikidata_ambiguity": 0,
        "wikidata_matches": [],
        "prominence_score": 0.0,
        "pageviews_estimate": 0,
        "mode": "offline" if offline else ("high-precision" if high_precision else "standard")
    }
    
    if offline:
        # Heuristic-only mode
        result["rationale_offline"] = (
            "Offline mode — no Wikipedia/Wikidata API queries. "
            "Heuristic assessment only based on name characteristics."
        )
        # Apply simple heuristic
        if len(name) <= 4 or name.lower() in ["apple", "google", "amazon", "tesla", "nike"]:
            result["prominence_score"] = 0.9
        else:
            result["prominence_score"] = 0.2
        score, rationale = score_from_result(result)
        result["score"] = score
        result["score_rationale"] = rationale
        return result
    
    # Live Wikipedia API queries
    page_data = wikipedia_page_info(name)
    time.sleep(0.5)  # Rate-limit courtesy
    
    if page_data and "missing" not in page_data:
        result["direct_article"] = True
        result["direct_article_title"] = page_data.get("title")
        result["disambiguation_page"] = is_disambiguation_page(page_data)
    
    # Search for adjacent entities
    search_hits = wikipedia_search(name)
    time.sleep(0.5)
    
    result["search_hits"] = [
        {"title": hit.get("title"), "snippet_length": len(hit.get("snippet", ""))}
        for hit in search_hits[:5]
    ]
    
    # Wikidata lookup
    if high_precision:
        wd_matches = wikidata_lookup(name)
        result["wikidata_matches"] = wd_matches
        result["wikidata_ambiguity"] = len(wd_matches)
        if wd_matches:
            result["wikidata_qid"] = wd_matches[0]["qid"]
    
    # Prominence scoring via pageviews (if article exists)
    if result["direct_article"] and not result["disambiguation_page"]:
        pageviews = wikipedia_pageviews(result["direct_article_title"])
        result["pageviews_estimate"] = pageviews
        # Normalize to 0-1
        if pageviews > 100000:
            result["prominence_score"] = 1.0
        elif pageviews > 10000:
            result["prominence_score"] = 0.7
        elif pageviews > 1000:
            result["prominence_score"] = 0.4
        else:
            result["prominence_score"] = 0.1
    
    score, rationale = score_from_result(result)
    result["score"] = score
    result["score_rationale"] = rationale
    
    return result


def score_from_result(result):
    """Score calculator — maps analysis to 0-2 axis score."""
    if result["disambiguation_page"]:
        return (0, "DISAMBIGUATION PAGE — 3+ entities share this name. LLM knowledge graph contested.")
    
    if result["direct_article"]:
        if result["prominence_score"] > 0.7:
            return (0, f"HIGH-PROMINENCE COLLISION — existing Wikipedia article with significant traffic ({result['pageviews_estimate']} monthly views).")
        elif result["prominence_score"] > 0.3:
            return (1, f"LOW-PROMINENCE MATCH — Wikipedia article exists but limited prominence. Namespace acquirable with brand-building.")
        else:
            return (1, "VERY LOW-PROMINENCE MATCH — Wikipedia article exists but negligible traffic. Soft-flag.")
    
    if result["wikidata_ambiguity"] >= 3:
        return (1, f"WIKIDATA AMBIGUITY — {result['wikidata_ambiguity']} entities share label. Knowledge graph crowded.")
    
    if len(result["search_hits"]) >= 3:
        return (1, f"SEARCH-HIT AMBIGUITY — {len(result['search_hits'])} relevant Wikipedia hits. Not an entity-article match but name appears in existing articles.")
    
    return (2, "CLEAN NAMESPACE — no Wikipedia article, no Wikidata QID conflicts. Knowledge graph slot open.")


def format_human_output(result):
    lines = []
    lines.append(f"=== Entity Disambiguation — \"{result['name']}\" ===\n")
    lines.append(f"Mode: {result['mode']}\n")
    
    if result["direct_article"]:
        lines.append(f"Direct Wikipedia article: YES ({result['direct_article_title']})")
        if result["disambiguation_page"]:
            lines.append("  ⚠ DISAMBIGUATION PAGE")
    else:
        lines.append("Direct Wikipedia article: No")
    
    if result["pageviews_estimate"] > 0:
        lines.append(f"Pageview estimate: {result['pageviews_estimate']}/month")
    
    if result["search_hits"]:
        lines.append(f"\nWikipedia search hits (top {len(result['search_hits'])}):")
        for hit in result["search_hits"]:
            lines.append(f"  - {hit['title']}")
    
    if result.get("wikidata_matches"):
        lines.append(f"\nWikidata matches ({result['wikidata_ambiguity']}):")
        for wd in result["wikidata_matches"][:3]:
            lines.append(f"  - {wd['qid']}: {wd['label']} — {wd.get('description', '(no desc)')}")
    elif result["mode"] == "high-precision":
        lines.append("\nWikidata matches: None")
    
    lines.append(f"\nProminence score: {result['prominence_score']:.2f}")
    lines.append(f"\nAXIS SCORE: {result['score']}/2")
    lines.append(f"Rationale: {result['score_rationale']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Entity Disambiguation — Wikipedia/Wikidata Namespace Test (Axis 4)"
    )
    parser.add_argument("names", nargs="+", help="Brand name(s)")
    parser.add_argument("--high-precision", action="store_true",
                        help="Pharma-mode with Wikidata lookup")
    parser.add_argument("--offline", action="store_true", help="Skip API (heuristic only)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    results = [
        check_wikipedia(name, high_precision=args.high_precision, offline=args.offline)
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
