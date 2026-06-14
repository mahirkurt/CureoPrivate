#!/usr/bin/env python3
"""
domain_recon.py — Brand-Maker Domain Availability Heuristic + Verification Tool

⚠️ FALLBACK SCRIPT: This script is the SECONDARY path. The PRIMARY domain
verification path in brand-maker v1.2+ is the GoDaddy MCP integration
(see references/godaddy-mcp-integration.md). Use this script ONLY when:
  - GoDaddy MCP is not enabled in the user's chat connectors
  - GoDaddy API is rate-limited / unavailable
  - User explicitly requests heuristic estimation only

Simulates the methodology of `veliovgroup/uniq.site` for predicting
domain availability without making live API calls (sandbox-safe).

Generates:
  - Heuristic availability score (0-100) per TLD
  - Modern alternative pattern suggestions (get-, try-, -hq, -app)
  - Manual verification URLs (Namecheap, Domainr, Instant Domain Search)
  - Trademark pre-screening URLs (USPTO, EUIPO, WIPO, TÜRKPATENT)

USAGE:
    python domain_recon.py "Lumio" "Verzo" "Stripe"

DEPENDENCIES: Pure Python 3.8+, no network access required.

LIMITATIONS: Heuristic only. Final domain availability MUST be
verified via GoDaddy MCP (preferred) or the printed manual URLs.
"""

import sys
import re
from typing import Dict, List
from urllib.parse import quote_plus

# ============================================================
# Common English Dictionary Words (subset for in-dictionary detection)
# ============================================================
# This is a tiny representative subset; in production, use NLTK or
# /usr/share/dict/words. For brand-maker purposes, this catches the
# obvious cases.

COMMON_WORDS = {
    "stripe", "linear", "notion", "stripe", "notion", "apple", "amazon",
    "google", "uber", "lift", "snap", "zoom", "slack", "box", "square",
    "cash", "tesla", "nike", "atlas", "phoenix", "sony", "sky", "drop",
    "face", "book", "pin", "interest", "youtube", "tube", "chat", "snap",
    "drop", "post", "tweet", "ping", "boom", "pop", "vroom", "claim",
    "cloud", "data", "code", "edge", "core", "node", "rocket", "moon",
    "star", "sun", "fire", "water", "earth", "ocean", "river", "mountain",
    "tree", "flower", "leaf", "love", "happy", "smart", "quick", "fast",
    "slow", "best", "great", "good", "bad", "new", "old", "young", "fresh",
    "the", "and", "for", "with", "from", "into", "onto", "upon", "over",
    "credit", "debit", "pay", "money", "bank", "fund", "stock", "trade",
    "buy", "sell", "shop", "store", "market", "deal", "save", "spend",
}

# ============================================================
# TLD Strategy Tiers
# ============================================================

TLD_STRATEGY = {
    "primary": [
        (".com", "Gold standard — first priority always", 1.0),
    ],
    "secondary": [
        (".io", "Tech/dev classic — second priority for born-global tech", 0.85),
        (".ai", "AI startup standard since 2023 — required for AI/ML", 0.80),
        (".co", "Fast .com alternative — third priority", 0.75),
    ],
    "tertiary": [
        (".app", "Google-backed TLD (2018+) — mobile app focus", 0.65),
        (".dev", "Developer tools niche", 0.60),
        (".xyz", "Web3/crypto classic — normalized", 0.65),
        (".tech", "Generic tech — marginal", 0.40),
    ],
    "regional": [
        (".com.tr", "Turkish market", 0.70),
        (".co.uk", "UK market", 0.70),
        (".de", "Germany / DACH", 0.70),
        (".fr", "France", 0.65),
        (".es", "Spain / Latin America gateway", 0.65),
    ]
}

# ============================================================
# Heuristic Availability Scoring
# ============================================================

def count_syllables_quick(name: str) -> int:
    """Quick syllable counter (mirrors phonetic_analyzer.py)."""
    word = re.sub(r"[^a-zA-Z]", "", name.lower())
    if not word:
        return 0
    word = re.sub(r"e$", "", word) if len(word) > 3 else word
    return max(1, len(re.findall(r"[aeiouy]+", word)))


def in_dictionary(name: str) -> bool:
    """Check if name is a common dictionary word."""
    return name.lower() in COMMON_WORDS


def has_consonant_clusters(name: str) -> bool:
    """Check for 3+ consonant clusters."""
    return bool(re.search(r"[bcdfghjklmnpqrstvwxz]{3,}", name.lower()))


def domain_availability_score(name: str, tld: str) -> Dict:
    """
    Heuristic score for likelihood of domain being available.
    Returns dict with score (0-100) and reasoning.

    Mirrors the spirit of veliovgroup/uniq.site:
    - Short common words = unavailable
    - Coined unique strings = available
    - Length matters
    """
    score = 50  # baseline
    reasoning = []

    name_clean = re.sub(r"[^a-zA-Z]", "", name).lower()
    length = len(name_clean)

    # Length-based scoring
    if length <= 3:
        score -= 40
        reasoning.append(f"Very short ({length} chars) — most {tld} taken")
    elif length <= 5:
        score -= 25
        reasoning.append(f"Short ({length} chars) — competitive market")
    elif length <= 7:
        score += 5
        reasoning.append(f"Optimal length ({length} chars)")
    elif length <= 10:
        score += 15
        reasoning.append(f"Long enough ({length} chars) — good odds")
    else:
        score += 20
        reasoning.append(f"Very long ({length} chars) — likely available")

    # Dictionary check
    if in_dictionary(name_clean):
        score -= 30
        reasoning.append(f"Common dictionary word — likely taken in {tld}")
    else:
        score += 20
        reasoning.append("Not a common dictionary word — coined-style")

    # Consonant cluster (uniqueness signal)
    if has_consonant_clusters(name_clean):
        score += 10
        reasoning.append("Contains consonant cluster — distinctive")

    # TLD priority adjustment (.com is hardest, exotic TLDs easier)
    tld_modifier = {
        ".com": -10, ".io": +5, ".ai": +0, ".co": +5, ".app": +10,
        ".dev": +15, ".xyz": +15, ".tech": +20,
        ".com.tr": +10, ".co.uk": +5, ".de": +5, ".fr": +10, ".es": +10,
    }.get(tld, 0)
    score += tld_modifier
    reasoning.append(f"TLD modifier: {tld_modifier:+d} for {tld}")

    score = max(0, min(100, score))

    if score >= 75:
        verdict = "Likely available"
    elif score >= 50:
        verdict = "Possibly available — verify manually"
    elif score >= 25:
        verdict = "Likely taken — alternative pattern recommended"
    else:
        verdict = "Almost certainly taken — premium domain market or alternative"

    return {
        "tld": tld,
        "score": score,
        "verdict": verdict,
        "reasoning": reasoning,
    }


# ============================================================
# Modern Alternative Pattern Generator
# ============================================================

def alternative_patterns(name: str) -> List[str]:
    """Generate modern alternative URL patterns when .com is taken."""
    n = name.lower()
    return [
        f"get{n}.com",
        f"try{n}.com",
        f"use{n}.com",
        f"with{n}.com",
        f"{n}hq.com",
        f"{n}app.com",
        f"{n}.io",
        f"{n}.ai",
        f"{n}.co",
        f"hi{n}.com",
        f"join{n}.com",
        f"{n}labs.com",
    ]


# ============================================================
# Manual Verification URL Generator
# ============================================================

def verification_urls(name: str) -> Dict[str, str]:
    """Generate clickable URLs for manual domain & trademark verification."""
    n_url = quote_plus(name)
    n_lower = name.lower()

    return {
        # Domain checks
        "Namecheap WHOIS": f"https://www.namecheap.com/domains/whois/?domain={n_lower}.com",
        "Domainr (multi-TLD)": f"https://domainr.com/?q={n_url}",
        "Instant Domain Search": f"https://instantdomainsearch.com/search?q={n_url}",
        "GoDaddy Bulk": f"https://www.godaddy.com/domainsearch/find?domainToCheck={n_lower}",

        # Trademark checks
        "USPTO TESS": f"https://tmsearch.uspto.gov/bin/showfield?f=toc&state=4810%3Atmtb1.1.1&p_search=searchss&p_L=50&BackReference=&p_plural=yes&p_s_PARA1=&p_tagrepl%7E%3A=PARA1%24LD&expr=PARA1+AND+PARA2&p_s_PARA2={n_url}&p_tagrepl%7E%3A=PARA2%24FT&p_op_ALL=AND&a_default=search&a_search=Submit+Query&a_search=Submit+Query",
        "EUIPO TMview": f"https://www.tmdn.org/tmview/#/tmview/results?text={n_url}",
        "WIPO Global Brand DB": f"https://www3.wipo.int/branddb/en/index.jsp#?text={n_url}",
        "TÜRKPATENT Marka": f"https://www.turkpatent.gov.tr/arastirma-yap?form=trademark",

        # Etymology / cultural cross-check
        "Wiktionary (multi-lang)": f"https://en.wiktionary.org/wiki/{n_url}",
        "Forvo (pronunciation)": f"https://forvo.com/word/{n_url}/",
    }


# ============================================================
# Pretty Printer
# ============================================================

def format_report(name: str) -> str:
    out = f"""
═══════════════════════════════════════════════════════
DOMAIN & TRADEMARK RECONNAISSANCE: {name}
═══════════════════════════════════════════════════════

▌ HEURISTIC AVAILABILITY SCORES (0-100, sandbox estimate)
"""
    # Primary TLDs first
    all_tlds = (
        TLD_STRATEGY["primary"] +
        TLD_STRATEGY["secondary"] +
        TLD_STRATEGY["tertiary"]
    )
    for tld_info in all_tlds:
        tld, desc, base_priority = tld_info
        result = domain_availability_score(name, tld)
        out += (
            f"\n  {name}{tld:7s}  Score: {result['score']:3d}/100  → {result['verdict']}\n"
            f"    Description: {desc}\n"
        )

    # Regional TLDs
    out += "\n▌ REGIONAL TLDs (consider for target markets)\n"
    for tld_info in TLD_STRATEGY["regional"]:
        tld, desc, base_priority = tld_info
        result = domain_availability_score(name, tld)
        out += f"  {name}{tld:9s}  Score: {result['score']:3d}/100  → {result['verdict']}  ({desc})\n"

    # Modern alternative patterns (if .com is likely taken)
    com_score = domain_availability_score(name, ".com")["score"]
    if com_score < 60:
        out += "\n▌ MODERN ALTERNATIVE PATTERNS (since .com appears competitive)\n"
        for pattern in alternative_patterns(name):
            out += f"  • {pattern}\n"

    # Manual verification URLs
    out += "\n▌ MANUAL VERIFICATION (mandatory — sandbox cannot live-check)\n"
    urls = verification_urls(name)
    for label, url in urls.items():
        out += f"  • {label}:\n    {url}\n"

    out += """
▌ NOTES
  • Heuristic scores are PREDICTIVE, not authoritative.
  • Final domain reservations: register within 24 hours of name approval
    to prevent cybersquatting.
  • Trademark searches above are PRE-SCREENING only.
    Comprehensive search via legal counsel (Compumark, Corsearch) required.

═══════════════════════════════════════════════════════
"""
    return out


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python domain_recon.py <Name1> [Name2] ...")
        print('Example: python domain_recon.py "Lumio" "Verzo" "Stripe"')
        sys.exit(1)

    names = sys.argv[1:]
    print(f"\n# Domain & Trademark Reconnaissance — {len(names)} candidate(s)")
    print(f"# Brand-Maker v1.0 — domain_recon.py\n")
    print("# DISCLAIMER: Heuristic estimates. Manual verification URLs provided below.\n")

    for name in names:
        print(format_report(name))


if __name__ == "__main__":
    main()
