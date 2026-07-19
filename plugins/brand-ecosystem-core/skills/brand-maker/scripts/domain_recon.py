#!/usr/bin/env python3
"""
domain_recon.py — Brand-Maker Domain Availability Verification Tool (v2.1)

⚠️ TWO-SOURCE VERIFICATION MANDATE (v2.1 — expert-audit remediation A):
No domain is EVER reported "available / müsait" from a single signal. The
2026-audit found the heuristic pathway happily reported `auronza.com` and
`nortanza.com` as "available (standard)" when both are in fact REGISTERED.
Root cause: a coined 7-letter string scores high on the availability
heuristic, and the heuristic was treated as a verdict rather than an estimate.

Fix: the heuristic is now an ESTIMATE only. The AVAILABILITY VERDICT requires
live second-source confirmation (RDAP primary → WHOIS fallback). A name is
called AVAILABLE only when a live registry source confirms it is unregistered;
"available" is NEVER emitted from the heuristic alone. Every domain result
carries verification_status (confirmed | provisional | unverified), the
source(s) consulted, and a UTC timestamp.

Verification states:
  - confirmed_taken      — a live source returned registration data (DOLU)
  - confirmed_available  — TWO independent live sources agree it is free
  - provisional_available— exactly ONE live source says free (needs 2nd source)
  - unverified           — no live source reachable (sandbox/offline) → NEVER
                           "available"; heuristic estimate shown for context only

GoDaddy MCP (references/godaddy-mcp-integration.md) remains the PRIMARY live
path at skill-execution time. This script is the fallback/second-source layer
and is now a genuine live verifier (RDAP over HTTPS), not a pure heuristic.

USAGE:
    python domain_recon.py "Lumio" "Verzo" "Auronza"
    python domain_recon.py --json "Auronza" "Nortanza"
    python domain_recon.py --offline "Auronza"     # skip network (deterministic)
    python domain_recon.py --tlds .com,.io "Verzo"

DEPENDENCIES: Pure Python 3.8+ stdlib (urllib, socket). Network optional —
graceful degrade to "unverified" when offline.
"""

import argparse
import json
import re
import socket
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ============================================================
# Common English Dictionary Words (subset for in-dictionary detection)
# ============================================================

COMMON_WORDS = {
    "stripe", "linear", "notion", "apple", "amazon",
    "google", "uber", "lift", "snap", "zoom", "slack", "box", "square",
    "cash", "tesla", "nike", "atlas", "phoenix", "sony", "sky", "drop",
    "face", "book", "pin", "interest", "youtube", "tube", "chat",
    "post", "tweet", "ping", "boom", "pop", "vroom", "claim",
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

# WHOIS servers for the fallback second source (subset; TLD → host:43).
WHOIS_SERVERS = {
    "com": "whois.verisign-grs.com",
    "net": "whois.verisign-grs.com",
    "org": "whois.pir.org",
    "io": "whois.nic.io",
    "ai": "whois.nic.ai",
    "co": "whois.nic.co",
    "app": "whois.nic.google",
    "dev": "whois.nic.google",
    "xyz": "whois.nic.xyz",
    "tech": "whois.nic.tech",
}

# WHOIS "no match" signatures (domain is free). Compared case-insensitively.
WHOIS_FREE_SIGNATURES = [
    "no match", "not found", "no data found", "no object found",
    "domain not found", "status: available", "no entries found",
]

# ============================================================
# Heuristic Availability ESTIMATE (context only — never a verdict)
# ============================================================

def in_dictionary(name: str) -> bool:
    return name.lower() in COMMON_WORDS


def has_consonant_clusters(name: str) -> bool:
    return bool(re.search(r"[bcdfghjklmnpqrstvwxz]{3,}", name.lower()))


def heuristic_estimate(name: str, tld: str) -> Dict:
    """
    Heuristic LIKELIHOOD estimate (0-100). This is NOT an availability verdict
    — it only frames how competitive the string is. The verdict is decided by
    live verification. Kept because it usefully flags "this coined string is
    probably free, worth a live check" vs "this dictionary word is probably
    taken" — but it can never on its own emit "available".
    """
    score = 50
    reasoning = []

    name_clean = re.sub(r"[^a-zA-Z]", "", name).lower()
    length = len(name_clean)

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

    if in_dictionary(name_clean):
        score -= 30
        reasoning.append(f"Common dictionary word — likely taken in {tld}")
    else:
        score += 20
        reasoning.append("Not a common dictionary word — coined-style")

    if has_consonant_clusters(name_clean):
        score += 10
        reasoning.append("Contains consonant cluster — distinctive")

    tld_modifier = {
        ".com": -10, ".io": +5, ".ai": +0, ".co": +5, ".app": +10,
        ".dev": +15, ".xyz": +15, ".tech": +20,
        ".com.tr": +10, ".co.uk": +5, ".de": +5, ".fr": +10, ".es": +10,
    }.get(tld, 0)
    score += tld_modifier
    reasoning.append(f"TLD modifier: {tld_modifier:+d} for {tld}")

    score = max(0, min(100, score))

    # NOTE: the heuristic verdict deliberately AVOIDS the word "available".
    # It speaks only of market competitiveness, never registration status.
    if score >= 75:
        estimate = "low-competition string (verify live before claiming free)"
    elif score >= 50:
        estimate = "moderate-competition string (verify live)"
    elif score >= 25:
        estimate = "high-competition string (likely registered)"
    else:
        estimate = "premium/exhausted string (almost certainly registered)"

    return {"tld": tld, "heuristic_score": score, "estimate": estimate,
            "reasoning": reasoning}


# ============================================================
# Live second-source verification (RDAP primary → WHOIS fallback)
# ============================================================

def rdap_lookup(domain: str, timeout: float = 6.0) -> Dict:
    """
    RDAP (RFC 7482/9082) lookup via the rdap.org bootstrap resolver.
    HTTP 200 → registered; HTTP 404 → available; anything else → unreachable.
    Returns {"status": registered|available|unreachable, "detail": str}.
    """
    url = f"https://rdap.org/domain/{quote_plus(domain)}"
    req = Request(url, headers={
        "User-Agent": "brand-maker-domain-recon/2.1 (+skill)",
        "Accept": "application/rdap+json, application/json",
    })
    try:
        with urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if code == 200:
                return {"status": "registered",
                        "detail": "RDAP 200 — registration record exists"}
            return {"status": "unreachable",
                    "detail": f"RDAP unexpected HTTP {code}"}
    except HTTPError as e:
        if e.code == 404:
            return {"status": "available",
                    "detail": "RDAP 404 — no registration record"}
        if e.code == 429:
            return {"status": "unreachable", "detail": "RDAP 429 rate-limited"}
        return {"status": "unreachable", "detail": f"RDAP HTTP {e.code}"}
    except (URLError, socket.timeout, OSError) as e:
        return {"status": "unreachable", "detail": f"RDAP unreachable: {e}"}
    except Exception as e:  # pragma: no cover — defensive
        return {"status": "unreachable", "detail": f"RDAP error: {e}"}


def whois_lookup(domain: str, timeout: float = 6.0) -> Dict:
    """
    WHOIS (port 43) fallback second source. Best-effort — many sandboxes block
    outbound 43, in which case this returns "unreachable" and the verdict
    degrades honestly. Returns {"status": registered|available|unreachable}.
    """
    tld = domain.rsplit(".", 1)[-1].lower()
    server = WHOIS_SERVERS.get(tld)
    if not server:
        return {"status": "unreachable",
                "detail": f"No WHOIS server mapped for .{tld}"}
    try:
        with socket.create_connection((server, 43), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall((domain + "\r\n").encode("utf-8", "ignore"))
            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
                if sum(len(c) for c in chunks) > 65536:
                    break
        text = b"".join(chunks).decode("utf-8", "ignore").lower()
        if not text.strip():
            return {"status": "unreachable", "detail": "WHOIS empty response"}
        for sig in WHOIS_FREE_SIGNATURES:
            if sig in text:
                return {"status": "available",
                        "detail": f"WHOIS free signature: '{sig}'"}
        return {"status": "registered",
                "detail": "WHOIS returned a registration record"}
    except (socket.timeout, OSError) as e:
        return {"status": "unreachable", "detail": f"WHOIS unreachable: {e}"}
    except Exception as e:  # pragma: no cover — defensive
        return {"status": "unreachable", "detail": f"WHOIS error: {e}"}


def verify_domain(name: str, tld: str, offline: bool = False,
                  timeout: float = 6.0,
                  rdap_fn=rdap_lookup, whois_fn=whois_lookup) -> Dict:
    """
    Two-source availability verification. Returns a dict with:
      verification_status: confirmed_taken | confirmed_available |
                           provisional_available | unverified
      available:  True only for confirmed_available; False for confirmed_taken;
                  None (unknown) for provisional/unverified.
      verdict:    human string — NEVER says "müsait/available" unless
                  confirmed_available.
      sources, timestamp, heuristic (estimate only).

    rdap_fn / whois_fn are injectable for deterministic testing.
    """
    domain = f"{name.lower()}{tld}"
    heuristic = heuristic_estimate(name, tld)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if offline:
        rdap = {"status": "skipped", "detail": "offline mode"}
        whois = {"status": "skipped", "detail": "offline mode"}
    else:
        rdap = rdap_fn(domain, timeout)
        whois = {"status": "skipped", "detail": "not consulted (RDAP decisive)"}
        # Only spend a WHOIS round-trip when it can change the verdict:
        # RDAP says free (need a 2nd source to CONFIRM available), or RDAP
        # is unreachable (need any live source at all).
        if rdap["status"] in ("available", "unreachable"):
            whois = whois_fn(domain, timeout)

    sources = []
    if rdap["status"] not in ("skipped",):
        sources.append({"name": "RDAP (rdap.org)", "result": rdap["status"],
                        "detail": rdap["detail"]})
    if whois["status"] not in ("skipped",):
        sources.append({"name": "WHOIS (port 43)", "result": whois["status"],
                        "detail": whois["detail"]})

    live = {s["result"] for s in sources}

    # --- Decision logic. "registered" from ANY live source is decisive. ---
    if "registered" in live:
        status = "confirmed_taken"
        available = False
        verdict = "DOLU / kayıtlı (confirmed — canlı kayıt bulundu)"
    elif live == {"available"} and len(sources) >= 2:
        # BOTH live sources agree it is free.
        status = "confirmed_available"
        available = True
        verdict = "MÜSAİT (confirmed — 2 bağımsız canlı kaynak teyit etti)"
    elif "available" in live:
        # Exactly one live source says free (other unreachable/absent).
        status = "provisional_available"
        available = None
        verdict = ("PROVISIONAL — tek canlı kaynak boş gösterdi; ikinci kaynak "
                   "teyidi gerekli, 'müsait' DİYE RAPORLAMA")
    else:
        # No live source reachable (offline / all unreachable).
        status = "unverified"
        available = None
        verdict = ("BELİRSİZ — doğrulanamadı (canlı kaynak erişilemedi); "
                   "asla 'müsait' varsayma — GoDaddy MCP / manuel kontrol gerekli")

    return {
        "domain": domain,
        "tld": tld,
        "verification_status": status,
        "available": available,
        "verdict": verdict,
        "sources": sources,
        "timestamp": timestamp,
        "heuristic": heuristic,
    }


# ============================================================
# Modern Alternative Pattern Generator
# ============================================================

def alternative_patterns(name: str) -> List[str]:
    n = name.lower()
    return [
        f"get{n}.com", f"try{n}.com", f"use{n}.com", f"with{n}.com",
        f"{n}hq.com", f"{n}app.com", f"{n}.io", f"{n}.ai", f"{n}.co",
        f"hi{n}.com", f"join{n}.com", f"{n}labs.com",
    ]


def verification_urls(name: str) -> Dict[str, str]:
    n_url = quote_plus(name)
    n_lower = name.lower()
    return {
        "Namecheap WHOIS": f"https://www.namecheap.com/domains/whois/?domain={n_lower}.com",
        "Domainr (multi-TLD)": f"https://domainr.com/?q={n_url}",
        "Instant Domain Search": f"https://instantdomainsearch.com/search?q={n_url}",
        "GoDaddy Bulk": f"https://www.godaddy.com/domainsearch/find?domainToCheck={n_lower}",
        "RDAP (live, machine-readable)": f"https://rdap.org/domain/{n_lower}.com",
        "USPTO Trademark Search": f"https://tmsearch.uspto.gov/search/search-information?query={n_url}",
        "EUIPO TMview": f"https://www.tmdn.org/tmview/#/tmview/results?text={n_url}",
        "WIPO Global Brand DB": f"https://www3.wipo.int/branddb/en/index.jsp#?text={n_url}",
        "TÜRKPATENT Marka": f"https://www.turkpatent.gov.tr/arastirma-yap?form=trademark",
        "Wiktionary (multi-lang)": f"https://en.wiktionary.org/wiki/{n_url}",
    }


# ============================================================
# Report builder
# ============================================================

def analyze(name: str, tlds: List[str], offline: bool, timeout: float) -> Dict:
    results = [verify_domain(name, tld, offline=offline, timeout=timeout)
               for tld in tlds]
    com = next((r for r in results if r["tld"] == ".com"), results[0])
    return {
        "name": name,
        "results": results,
        "com_verification_status": com["verification_status"],
        "com_available": com["available"],
        "verification_urls": verification_urls(name),
    }


def format_report(analysis: Dict) -> str:
    name = analysis["name"]
    out = f"""
═══════════════════════════════════════════════════════
DOMAIN RECONNAISSANCE (2-source verified): {name}
═══════════════════════════════════════════════════════

▌ LIVE VERIFICATION (RDAP primary → WHOIS fallback)
  Rule: no domain is called MÜSAİT without 2 live sources.
"""
    for r in analysis["results"]:
        out += (
            f"\n  {r['domain']}\n"
            f"    Status:   {r['verification_status']}\n"
            f"    Verdict:  {r['verdict']}\n"
            f"    Sources:  {', '.join(s['name'] + '=' + s['result'] for s in r['sources']) or '(none reachable)'}\n"
            f"    Heuristic (estimate only): {r['heuristic']['heuristic_score']}/100 — {r['heuristic']['estimate']}\n"
            f"    Checked:  {r['timestamp']}\n"
        )

    com = next((r for r in analysis["results"] if r["tld"] == ".com"), None)
    if com and com["verification_status"] in ("confirmed_taken",
                                              "provisional_available",
                                              "unverified"):
        out += "\n▌ MODERN ALTERNATIVE PATTERNS (.com not confirmed free)\n"
        for pattern in alternative_patterns(name):
            out += f"  • {pattern}\n"

    out += "\n▌ MANUAL / SECOND-SOURCE VERIFICATION URLs\n"
    for label, url in analysis["verification_urls"].items():
        out += f"  • {label}:\n    {url}\n"

    out += """
▌ NOTES
  • "unverified" and "provisional" are NOT "available" — never report a domain
    as free without two agreeing live sources (or a GoDaddy MCP confirmation).
  • Register a confirmed-free .com within 24h of name approval (anti-squatting).
  • Trademark URLs above are PRE-SCREENING only — comprehensive counsel search
    (Compumark / Corsearch) remains mandatory.

═══════════════════════════════════════════════════════
"""
    return out


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Domain reconnaissance with mandatory two-source verification"
    )
    parser.add_argument("names", nargs="+", help="Brand name(s) to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--offline", action="store_true",
                        help="Skip network (deterministic; yields 'unverified')")
    parser.add_argument("--tlds", default=".com,.io,.ai,.co",
                        help="Comma-separated TLDs (default: .com,.io,.ai,.co)")
    parser.add_argument("--timeout", type=float, default=6.0,
                        help="Per-request network timeout seconds")
    args = parser.parse_args()

    tlds = [t if t.startswith(".") else "." + t
            for t in (x.strip() for x in args.tlds.split(",")) if t]

    analyses = [analyze(name, tlds, args.offline, args.timeout)
                for name in args.names]

    if args.json:
        print(json.dumps(analyses, indent=2, ensure_ascii=False))
    else:
        print(f"\n# Domain Reconnaissance — {len(args.names)} candidate(s)")
        print("# Brand-Maker v2.1 — domain_recon.py (2-source verified)")
        print("# NO domain reported 'müsait' without two agreeing live sources.\n")
        for a in analyses:
            print(format_report(a))


if __name__ == "__main__":
    main()
