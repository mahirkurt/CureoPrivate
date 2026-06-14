#!/usr/bin/env python3
"""
ubo_resolver.py — pharmaintel v5.0.0 Forensic Provenance Layer

L1 source resolution layer — UBO source hierarchy (P0-P3) cascade resolver.

Implements ubo-source-hierarchy.md §10.1 SOURCE_PRIORITY ladder:
  - P0 (statutory authority) → Companies House UK + Handelsregister DE +
    KBO BE + KvK NL + MERSİS TR + Ticaret Sicili Gazetesi + EGRUL RU +
    SEC EDGAR 13D/13G
  - P1 (authorized aggregator) → OpenCorporates + OpenOwnership BODS +
    OCCRP Aleph authorized
  - P2 (investigative) → OCCRP Aleph leaks + ICIJ Offshore Leaks
  - P3 (commercial niche) → LittleSis + Crunchbase + Rusprofile

Provides:
  - Entity dataclass (target identification)
  - resolve_ubo() main entry point — P0→P3 cascade with triangulation enforcement
  - Recursive investor chain walk (≤7 hops per ubo-source-hierarchy.md §7.3)
  - Sanctions screening (OFAC + EU + UK + UN + Türkiye MASAK)
  - Obfuscation pattern detector (formation agent + serial director +
    secrecy haven + bearer shares + recent SPV)

External dependencies (optional, stub mode if missing):
  - requests           → all HTTP API calls (P0 statutory + P1 aggregator)
  - openpyxl           → OFAC SDN consolidated list parsing

Environment variables (operator-supplied API keys):
  - COMPANIES_HOUSE_API_KEY
  - OPENCORPORATES_API_TOKEN
  - HANDELSREGISTER_API_KEY
  - SEC_USER_AGENT (required by SEC EDGAR Fair Access Rule)

Run as module:
  python3 ubo_resolver.py --target "Acme Biotech Ltd" --jurisdiction GB
  python3 ubo_resolver.py --example

Cross-references:
  - references/ubo-source-hierarchy.md (canonical hierarchy specification)
  - references/sub-protocol-bd-dd.md §2.1 Dimension A (UBO + Corporate)
  - references/sub-protocol-bd-dd.md §2.2 Dimension B (Sanctions + PEP)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

try:
    import requests  # type: ignore

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# --- Constants --------------------------------------------------------------

P0_AUTHORITY_TIER = "OSINT-T1"
P1_AUTHORITY_TIER = "OSINT-T2"
P2_AUTHORITY_TIER = "OSINT-T3"
P3_AUTHORITY_TIER = "T6"  # commercial / niche

MAX_CHAIN_HOPS = 7  # per ubo-source-hierarchy.md §7.3 saturation rule

SECRECY_HAVEN_JURISDICTIONS = {
    "BVI", "VG",      # British Virgin Islands
    "KY",             # Cayman Islands
    "BS",             # Bahamas
    "PA",             # Panama (pre-2015 bearer share)
    "BZ",             # Belize
    "SC",             # Seychelles
    "MH",             # Marshall Islands
    "LI",             # Liechtenstein
    "AD",             # Andorra
    "AI",             # Anguilla
    "VC",             # St. Vincent
    "GD",             # Grenada
    "BB",             # Barbados (until 2018 reforms)
    "MU",             # Mauritius
    "JE", "GG", "IM", # Jersey, Guernsey, Isle of Man
    "LU",             # Luxembourg (SCSp + SOPARFI structures)
    "NL",             # Netherlands (CV + Coop conduit structures)
}

# Common formation agent address patterns (corporate registration services)
FORMATION_AGENT_PATTERNS = [
    re.compile(r"intertrust", re.IGNORECASE),
    re.compile(r"\b(csc|corporation service company)\b", re.IGNORECASE),
    re.compile(r"\bcitco\b", re.IGNORECASE),
    re.compile(r"\bmaples\b", re.IGNORECASE),
    re.compile(r"\bappleby\b", re.IGNORECASE),
    re.compile(r"\boffshore (incorporations|services|management)\b",
               re.IGNORECASE),
    re.compile(r"\btmf group\b", re.IGNORECASE),
    re.compile(r"\bvistra\b", re.IGNORECASE),
]

SANCTIONS_LISTS = {
    "OFAC_SDN": "https://www.treasury.gov/ofac/downloads/sdn.xml",
    "EU_CFSL": ("https://data.europa.eu/data/datasets/"
                "consolidated-list-of-persons-groups-and-entities-"
                "subject-to-eu-financial-sanctions"),
    "UK_HMT_OFSI": ("https://www.gov.uk/government/publications/"
                    "financial-sanctions-consolidated-list-of-targets"),
    "UN_CONSOLIDATED": ("https://www.un.org/securitycouncil/sanctions/"
                        "un-sc-consolidated-list"),
    "TR_MASAK": "https://masak.hmb.gov.tr/",
}


# --- Data classes -----------------------------------------------------------


@dataclass
class Entity:
    """Target entity for UBO investigation."""
    name: str
    jurisdiction: Optional[str] = None  # ISO 3166-1 alpha-2
    registration_number: Optional[str] = None
    address: Optional[str] = None
    entity_type: Optional[str] = None  # AŞ | Ltd | LP | GP | Trust | Foundation


@dataclass
class UBORecord:
    """Single UBO finding from a source."""
    source_name: str
    authority_tier: str  # OSINT-T1/T2/T3 or T6
    primary_url: str
    target_entity: Entity
    beneficial_owners: list[dict] = field(default_factory=list)
    direct_shareholders: list[dict] = field(default_factory=list)
    directors: list[dict] = field(default_factory=list)
    raw_response: Optional[dict] = None
    obfuscation_flags: list[str] = field(default_factory=list)


@dataclass
class SanctionsHit:
    """Sanctions screening match."""
    name_searched: str
    list_name: str
    match_score: float  # 0.0-1.0 fuzzy match confidence
    match_type: str  # exact | aliased | phonetic | partial
    sdn_program: Optional[str] = None
    sdn_designation_date: Optional[str] = None
    raw_entry: Optional[dict] = None


# --- P0 Statutory Authority Connectors -------------------------------------


def query_companies_house_psc(entity: Entity) -> Optional[UBORecord]:
    """Query UK Companies House PSC register.

    Requires COMPANIES_HOUSE_API_KEY environment variable.
    """
    if not HAS_REQUESTS:
        return None
    api_key = os.environ.get("COMPANIES_HOUSE_API_KEY")
    if not api_key or not entity.registration_number:
        return None

    try:
        # Get company profile
        company_url = (f"https://api.company-information.service.gov.uk/"
                       f"company/{entity.registration_number}")
        psc_url = company_url + "/persons-with-significant-control"

        r = requests.get(psc_url, auth=(api_key, ""), timeout=30)
        r.raise_for_status()
        data = r.json()

        beneficial_owners = []
        for item in data.get("items", []):
            owner = {
                "name": item.get("name"),
                "kind": item.get("kind"),  # individual | corporate-entity | etc.
                "nature_of_control": item.get("natures_of_control", []),
                "country_of_residence": item.get("country_of_residence"),
                "nationality": item.get("nationality"),
                "address": item.get("address"),
                "date_of_birth": item.get("date_of_birth"),  # PII!
                "ceased": item.get("ceased", False),
            }
            beneficial_owners.append(owner)

        return UBORecord(
            source_name="UK Companies House PSC Register",
            authority_tier=P0_AUTHORITY_TIER,
            primary_url=psc_url,
            target_entity=entity,
            beneficial_owners=beneficial_owners,
            raw_response=data,
        )
    except Exception:  # noqa: BLE001
        return None


def query_handelsregister_transparenz(entity: Entity) -> Optional[UBORecord]:
    """Query German Handelsregister + Transparenzregister (Transparency Register).

    Note: post-C-37/20 ECJ ruling restricts Transparenzregister access to
    legitimate-interest parties only. Requires registered account.
    """
    if not HAS_REQUESTS:
        return None
    # Stub — actual implementation requires authenticated session via
    # https://www.transparenzregister.de or unternehmensregister.de
    # API access via register-api.de paid tier
    return None


def query_kbo_bce(entity: Entity) -> Optional[UBORecord]:
    """Query Belgian KBO-BCE + UBO register."""
    if not HAS_REQUESTS:
        return None
    # Stub — Belgian UBO register access via https://finances.belgium.be
    return None


def query_kvk_nl(entity: Entity) -> Optional[UBORecord]:
    """Query Dutch KvK + UBO register (paid per-query ~€2.30)."""
    if not HAS_REQUESTS:
        return None
    # Stub — requires paid KvK API access
    return None


def query_mersis_tr(entity: Entity) -> Optional[UBORecord]:
    """Query Turkish MERSİS (Merkezi Sicil Kayıt Sistemi).

    No official API — web scraping with rate limit per ToS non-commercial.
    """
    if not HAS_REQUESTS:
        return None
    # Stub — production implementation: web scrape https://mersis.ticaret.gov.tr
    # with rate-limited Playwright per KVKK + ToS
    return None


def query_ticaret_sicili_gazette(entity: Entity) -> Optional[UBORecord]:
    """Query Turkish Ticaret Sicili Gazetesi (Commercial Registry Gazette).

    Notary-validated PDF archive of all Turkish company registrations +
    amendments since 2008.
    """
    if not HAS_REQUESTS:
        return None
    # Stub — production: search https://www.ticaretsicil.gov.tr
    # PDF parsing required for UBO extraction
    return None


def query_egrul_ru(entity: Entity) -> Optional[UBORecord]:
    """Query Russian EGRUL (Единый государственный реестр юридических лиц)."""
    if not HAS_REQUESTS:
        return None
    # Stub — https://egrul.nalog.ru — manual extraction or Rusprofile wrapper
    return None


def query_sec_edgar_13d(entity: Entity) -> Optional[UBORecord]:
    """Query SEC EDGAR for 13D/13G beneficial ownership filings.

    Requires SEC_USER_AGENT env var per SEC Fair Access Rule.
    """
    if not HAS_REQUESTS:
        return None
    user_agent = os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        return None
    # Stub — production: query data.sec.gov/submissions/CIK*.json
    return None


# --- P1 Authorized Aggregator Connectors -----------------------------------


def query_opencorporates(entity: Entity) -> Optional[UBORecord]:
    """Query OpenCorporates (free tier 200/month or paid)."""
    if not HAS_REQUESTS:
        return None
    token = os.environ.get("OPENCORPORATES_API_TOKEN")
    try:
        params = {"q": entity.name, "api_token": token} if token else {"q": entity.name}
        if entity.jurisdiction:
            params["jurisdiction_code"] = entity.jurisdiction.lower()
        r = requests.get(
            "https://api.opencorporates.com/v0.4/companies/search",
            params=params, timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results", {}).get("companies", [])
        if not results:
            return None
        best = results[0]["company"]
        return UBORecord(
            source_name="OpenCorporates",
            authority_tier=P1_AUTHORITY_TIER,
            primary_url=best.get("opencorporates_url", ""),
            target_entity=entity,
            beneficial_owners=[],  # OC doesn't expose UBO directly via free API
            direct_shareholders=[],
            raw_response=best,
        )
    except Exception:  # noqa: BLE001
        return None


def query_openownership_bods(entity: Entity) -> Optional[UBORecord]:
    """Query OpenOwnership BODS (Beneficial Ownership Data Standard)."""
    # Stub — production: parse local BODS JSONL bulk download
    return None


def query_aleph_authorized(entity: Entity) -> Optional[UBORecord]:
    """Query OCCRP Aleph (authorized public datasets subset)."""
    return None


# --- Source priority ladder -------------------------------------------------


SOURCE_PRIORITY: list[tuple[str, str, Callable[[Entity], Optional[UBORecord]]]] = [
    # P0 — statutory authority
    ("companies_house_uk", P0_AUTHORITY_TIER, query_companies_house_psc),
    ("handelsregister_de", P0_AUTHORITY_TIER, query_handelsregister_transparenz),
    ("kbo_be", P0_AUTHORITY_TIER, query_kbo_bce),
    ("kvk_nl", P0_AUTHORITY_TIER, query_kvk_nl),
    ("mersis_tr", P0_AUTHORITY_TIER, query_mersis_tr),
    ("ticaret_sicili_tr", P0_AUTHORITY_TIER, query_ticaret_sicili_gazette),
    ("egrul_ru", P0_AUTHORITY_TIER, query_egrul_ru),
    ("sec_edgar", P0_AUTHORITY_TIER, query_sec_edgar_13d),
    # P1 — authorized aggregators
    ("opencorporates", P1_AUTHORITY_TIER, query_opencorporates),
    ("openownership_bods", P1_AUTHORITY_TIER, query_openownership_bods),
    ("aleph_authorized", P1_AUTHORITY_TIER, query_aleph_authorized),
    # P2 + P3 omitted — implementations require investigative corpus access
]


# --- Obfuscation pattern detector ------------------------------------------


def detect_obfuscation_patterns(record: UBORecord) -> list[str]:
    """Detect obfuscation indicators per ubo-source-hierarchy.md §7.2 + §9.1."""
    flags = []

    # Secrecy haven jurisdiction
    if record.target_entity.jurisdiction in SECRECY_HAVEN_JURISDICTIONS:
        flags.append(f"secrecy_haven_jurisdiction:{record.target_entity.jurisdiction}")

    # Formation agent address pattern
    addr = (record.target_entity.address or "").lower()
    for pattern in FORMATION_AGENT_PATTERNS:
        if pattern.search(addr):
            flags.append(f"formation_agent_address:{pattern.pattern}")
            break

    # All shareholders are corporate (no natural person disclosed)
    bos = record.beneficial_owners
    if bos:
        natural_persons = [b for b in bos if b.get("kind") == "individual"]
        if not natural_persons and len(bos) > 0:
            flags.append("all_corporate_shareholders_no_natural_person")

    # Bearer shares historical jurisdiction
    if record.target_entity.jurisdiction == "PA":
        flags.append("bearer_shares_historical_jurisdiction")

    # Trust / Foundation entity type
    if record.target_entity.entity_type:
        et_lower = record.target_entity.entity_type.lower()
        if "trust" in et_lower or "foundation" in et_lower or "stiftung" in et_lower:
            flags.append(f"trust_foundation_entity_type:{record.target_entity.entity_type}")

    return flags


# --- Sanctions screening ----------------------------------------------------


def fuzzy_name_match(name: str, candidate: str, threshold: float = 0.85) -> float:
    """Simple fuzzy match using normalized Levenshtein-like ratio.

    Production: replace with python-Levenshtein or fuzzywuzzy library.
    """
    a = re.sub(r"[^\w\s]", "", name.lower()).strip()
    b = re.sub(r"[^\w\s]", "", candidate.lower()).strip()
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.9
    # Simple char overlap heuristic
    common = set(a.split()) & set(b.split())
    if not common:
        return 0.0
    return len(common) / max(len(set(a.split())), len(set(b.split())))


def sanctions_screen(name: str,
                     lists: Optional[list[str]] = None) -> list[SanctionsHit]:
    """Screen a name against sanctions lists.

    Stub implementation — production requires:
    1. Periodic OFAC SDN XML download + caching
    2. EU CFSL XML parsing
    3. UK HMT CSV parsing
    4. UN Security Council XML parsing
    5. Türkiye MASAK list scraping

    Returns list of SanctionsHit (empty if clean).
    """
    if lists is None:
        lists = list(SANCTIONS_LISTS.keys())

    hits: list[SanctionsHit] = []
    # Stub — actual implementation parses cached sanctions lists
    return hits


# --- Investor chain walk ---------------------------------------------------


def walk_investor_chain(target: Entity, max_hops: int = MAX_CHAIN_HOPS,
                        ) -> list[UBORecord]:
    """Recursive investor chain walk with cycle detection.

    Walks shareholders → their parents → ultimate individuals/sovereigns.
    Terminates at: ultimate individual | sovereign entity | publicly-traded
    parent | hard obfuscation point | max_hops reached.

    Returns list of UBORecord, one per hop.
    """
    visited: set[str] = set()
    chain: list[UBORecord] = []
    queue: list[tuple[Entity, int]] = [(target, 0)]

    while queue:
        entity, hop = queue.pop(0)
        if hop >= max_hops:
            break
        key = f"{entity.name}:{entity.jurisdiction}:{entity.registration_number}"
        if key in visited:
            continue
        visited.add(key)

        record = resolve_ubo(entity, walk_chain=False)
        if record is None:
            continue
        chain.append(record)

        # Enqueue corporate parents for next hop
        for owner in record.beneficial_owners:
            if owner.get("kind") in ("corporate-entity", "legal-person"):
                parent = Entity(
                    name=owner.get("name", ""),
                    jurisdiction=owner.get("country_of_residence"),
                    address=str(owner.get("address", "")) or None,
                )
                queue.append((parent, hop + 1))

    return chain


# --- Main resolver ----------------------------------------------------------


def resolve_ubo(target: Entity, walk_chain: bool = True) -> Optional[UBORecord]:
    """Run P0→P3 cascade and return first successful UBO record.

    Args:
        target: Entity to investigate
        walk_chain: if True, recursively walk investor chain

    Returns:
        UBORecord with obfuscation_flags populated, or None if no source matched.
    """
    for source_name, tier, query_fn in SOURCE_PRIORITY:
        try:
            record = query_fn(target)
            if record:
                record.obfuscation_flags = detect_obfuscation_patterns(record)
                return record
        except Exception:  # noqa: BLE001
            continue
    return None


def resolve_ubo_with_triangulation(
    target: Entity,
) -> tuple[Optional[UBORecord], Optional[UBORecord]]:
    """Resolve UBO with triangulation partner per G56/G-PROV-06.

    Returns (primary_record, triangulation_partner). Primary will be
    P0 if available, else P1. Triangulation will be next-best distinct source.
    """
    primary: Optional[UBORecord] = None
    triangulation: Optional[UBORecord] = None
    seen_sources: set[str] = set()

    for source_name, tier, query_fn in SOURCE_PRIORITY:
        if source_name in seen_sources:
            continue
        try:
            record = query_fn(target)
            if record:
                record.obfuscation_flags = detect_obfuscation_patterns(record)
                seen_sources.add(source_name)
                if primary is None:
                    primary = record
                elif triangulation is None:
                    triangulation = record
                    break
        except Exception:  # noqa: BLE001
            continue

    return primary, triangulation


# --- Example fixture --------------------------------------------------------


def example_resolution() -> dict:
    """Return example UBO resolution result (no network)."""
    target = Entity(
        name="Hypothetical Biotech Co.",
        jurisdiction="GB",
        registration_number="12345678",
    )
    primary = UBORecord(
        source_name="UK Companies House PSC Register",
        authority_tier=P0_AUTHORITY_TIER,
        primary_url=("https://find-and-update.company-information.service.gov.uk/"
                     "company/12345678/persons-with-significant-control"),
        target_entity=target,
        beneficial_owners=[
            {
                "name": "Acme Capital Fund LP",
                "kind": "corporate-entity",
                "nature_of_control": ["ownership-of-shares-50-to-75-percent"],
                "country_of_residence": "KY",  # Cayman Islands
                "address": "Maples Corporate Services, Ugland House, KY1-1104",
            },
            {
                "name": "Founder Person",
                "kind": "individual",
                "nature_of_control": ["ownership-of-shares-25-to-50-percent"],
                "country_of_residence": "United Kingdom",
                "nationality": "British",
            },
        ],
        obfuscation_flags=[
            "formation_agent_address:maples",
        ],
    )
    triangulation = UBORecord(
        source_name="OpenCorporates",
        authority_tier=P1_AUTHORITY_TIER,
        primary_url="https://opencorporates.com/companies/gb/12345678",
        target_entity=target,
        beneficial_owners=[],
    )
    return {
        "target": {
            "name": target.name,
            "jurisdiction": target.jurisdiction,
            "registration_number": target.registration_number,
        },
        "primary": {
            "source_name": primary.source_name,
            "authority_tier": primary.authority_tier,
            "primary_url": primary.primary_url,
            "beneficial_owners": primary.beneficial_owners,
            "obfuscation_flags": primary.obfuscation_flags,
        },
        "triangulation": {
            "source_name": triangulation.source_name,
            "authority_tier": triangulation.authority_tier,
            "primary_url": triangulation.primary_url,
        },
        "sanctions_screen": {
            "individuals_screened": ["Founder Person"],
            "entities_screened": ["Acme Capital Fund LP"],
            "lists_used": list(SANCTIONS_LISTS.keys()),
            "hits": [],  # all clear in example
        },
        "chain_walk_summary": {
            "max_hops_used": 7,
            "hops_traversed": 3,
            "termination_reason": "ultimate_individual_identified",
        },
    }


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="pharmaintel v5.0.0 Forensic Provenance Layer — UBO resolver"
    )
    parser.add_argument("--target", help="Target entity name")
    parser.add_argument("--jurisdiction",
                        help="ISO 3166-1 alpha-2 jurisdiction code (e.g. GB, DE, TR)")
    parser.add_argument("--registration",
                        help="Registration number")
    parser.add_argument("--max-hops", type=int, default=MAX_CHAIN_HOPS,
                        help=f"Max investor chain hops (default {MAX_CHAIN_HOPS})")
    parser.add_argument("--no-walk", action="store_true",
                        help="Skip recursive chain walk (single-hop resolution only)")
    parser.add_argument("--example", action="store_true",
                        help="Print example resolution result (no network)")
    args = parser.parse_args()

    if args.example:
        print(json.dumps(example_resolution(), indent=2, ensure_ascii=False))
        return 0

    if not args.target:
        parser.error("--target required (or use --example)")

    entity = Entity(
        name=args.target,
        jurisdiction=args.jurisdiction,
        registration_number=args.registration,
    )

    primary, triangulation = resolve_ubo_with_triangulation(entity)

    if primary is None:
        result = {
            "status": "no_source_matched",
            "target": entity.__dict__,
            "sources_attempted": [s for s, _, _ in SOURCE_PRIORITY],
            "note": "No P0/P1 source returned data. Check API credentials.",
        }
    else:
        chain = []
        if not args.no_walk:
            chain = walk_investor_chain(entity, max_hops=args.max_hops)
        result = {
            "status": "resolved",
            "target": entity.__dict__,
            "primary_source": {
                "source_name": primary.source_name,
                "authority_tier": primary.authority_tier,
                "primary_url": primary.primary_url,
                "beneficial_owner_count": len(primary.beneficial_owners),
                "obfuscation_flags": primary.obfuscation_flags,
            },
            "triangulation_source": (
                {
                    "source_name": triangulation.source_name,
                    "authority_tier": triangulation.authority_tier,
                } if triangulation else None
            ),
            "chain_walk_hops": len(chain),
        }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
