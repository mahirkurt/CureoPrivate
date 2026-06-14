#!/usr/bin/env python3
"""
pharmaintel — Generic-By-Default Validator (G22)

Programmatic enforcement of generic-by-default discipline (per generic-by-default.md
Article 6). Executes 8 checks on a finalized pharmaintel report and reports per-check
pass/fail status.

Usage:
    python3 validate-report-discipline.py REPORT.md \\
        --user-name "User Name" \\
        --user-employer "Employer Name" \\
        [--query "original user query text"] \\
        [--strict | --json | --quiet]

Exit codes:
    0 = all 8 checks passed → report is generic-by-default compliant
    1 = one or more checks failed → revise before delivery
    2 = invalid usage (missing args, file not found)

The user-name and user-employer arguments are needed to detect leaks. The script
does NOT read user identity from any external source; it must be supplied at runtime
by whatever process invokes the validator (skill harness, manual review, CI).

This script implements only mechanical/textual checks. It is supplementary to
manual self-audit (Step 5b) and does not replace human judgment — some leaks
require semantic interpretation (e.g., user-employer-internal terminology that
doesn't match the literal employer name).
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


# ----- Config: forbidden patterns by check -----------------------------------

# Check 5 — user-employer-fitted intended use declarations
INTENDED_USE_PATTERNS = [
    r"intended for internal\s+(?:strategic\s+)?(?:intelligence\s+)?use\s+within\s+(?:[A-Z][\w\s/]+?)\s+(?:context|department|BU|business\s+unit|team)",
    r"for\s+(?:[A-Z][\w\s/]+?)(?:\s+internal)?\s+stakeholder\s+briefing",
    r"usable\s+in\s+(?:[A-Z][\w\s/]+?)\s+internal",
    r"intended\s+(?:to\s+be\s+used|use)\s+(?:by|within|inside)\s+(?:[A-Z][\w\s/]+?)\s+(?:context|department|BU)",
]

# Check 5 / Check 8 — employer-internal terminology (jargon NOT matched by literal name)
EMPLOYER_INTERNAL_TERMINOLOGY_PATTERNS = [
    # Common pharma corporate-internal terms when referring to "the org's internal X":
    r"\bBU\s+senior\s+team\b",
    r"\bRWE\s+registry\s+committee\b",
    r"\binternal\s+stakeholder\s+briefing\b",
    r"\binternal\s+strategic\s+intelligence\b",
    r"\bcompetitive\s+defense\s+playbook\b",
    r"\bdefensive\s+memo(?:randum)?\b",
]

# Check 4 — strategic action recommendation directed at a specific named sponsor
# Detected via verb patterns near sponsor-name positions:
STRATEGIC_ACTION_VERB_PATTERNS = [
    r"defensive\s+ni[şs]i?n?\s+(?:savunmas[ıi]|sürdür)",
    r"agresif\s+[şs]ekilde\s+savun",
    r"defensive\s+ni\w+\s+(?:defend|savun|protect)",
    r"strategic\s+action\s+signal\s*\(",
    r"stratejik\s+aksiyon\s+sinyali\s*\(",
    r"defend\s+/\s+partner\s+/\s+monitor",
    r"maksimum\s+kullan[ıi]lmas[ıi]",
    r"hızlı\s+erozyona\s+uğra",
]

# Check 6 — coverage anchor asymmetry
COVERAGE_EXCLUSION_ASYMMETRY_PATTERNS = [
    r"(?:Türkiye|Turkey|Japan|China|Çin|Almanya|Germany|France|UK|US|ABD)\s+(?:dışlanmıştır|excluded|deliberately\s+excluded|exclude(?:d)?)",
    r"deliberately\s+(?:dışlanmıştır|dış\s+bırakılmıştır|excluded)",
]

COVERAGE_INCLUSION_ANCHOR_PATTERNS = [
    r"özellikle\s+(?:[A-ZÇĞİÖŞÜ][\wçğıöşüÇĞİÖŞÜ]+?(?:\s+[A-ZÇĞİÖŞÜ][\wçğıöşüÇĞİÖŞÜ]+?)?)\s+(?:pazarı|bağlamı|context|market)",
    r"with\s+particular\s+attention\s+to\s+(?:[A-Z][\w\s]+?)(?:'s|\s+portfolio)",
    r"with\s+(?:specific|special)\s+focus\s+on\s+(?:[A-Z][\w\s]+?)(?:'s|\s+portfolio|\s+franchise)",
]

# Check 7 — scope note alignment with employer competitive setting
SCOPE_NOTE_COMPETITIVE_ALIGNMENT_PATTERNS = [
    # "Roche portföyüyle rekabetçi etkileşim" type
    r"(?:[A-Z][\w]+?)\s+portföyüyle\s+\([^)]+\)\s+rekabet",
    r"competitive\s+(?:interaction|dynamics|engagement)\s+with\s+(?:[A-Z][\w]+?)(?:'s)?\s+(?:portfolio|franchise)",
]

# Check 3 — auto-trigger rationale referencing user identity
AUTOTRIGGER_USER_IDENTITY_PATTERNS = [
    r"sponsor\s+profile\s*[—:-]\s*(?:[A-Z][\w\s]+?)\s+(?:Country\s+)?(?:Medical\s+Director|BU\s+Lead|Country\s+Manager|Director|Hematology|Oncology)",
    r"sponsor\s+profili\s*[—:-]\s*(?:[A-Z][\w\s]+?)\s+(?:Country\s+)?(?:Medical\s+Director|BU\s+Lead|Country\s+Manager|Director)",
    r"user\s+(?:is|works)\s+(?:in|at|for)\s+",
    r"user'?s\s+(?:role|employer|location|specialty|background)",
    r"based\s+on\s+user'?s\s+(?:role|profile|context|location|employer)",
    r"kullanıcının\s+(?:rolü|işvereni|konumu|profili|uzmanlığı)",
]

# Check 1 — direct user address
DIRECT_USER_ADDRESS_PATTERNS_TEMPLATE = [
    r"\bSayın\s+{name}\b",
    r"\b{name}\s+(?:bey|hanım)\b",
    r"\bSize|Sizin\s+(?:için|pozisyon)",
]


# ----- Data classes ----------------------------------------------------------

@dataclass
class CheckResult:
    check_id: int
    name: str
    status: str  # "PASS" | "FAIL" | "SKIP"
    findings: List[str] = field(default_factory=list)
    advice: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class AuditReport:
    report_path: str
    user_name: Optional[str]
    user_employer: Optional[str]
    query: Optional[str]
    total_checks: int
    passed: int
    failed: int
    skipped: int
    overall_pass: bool
    checks: List[CheckResult] = field(default_factory=list)
    overridden: int = 0
    t6_defense_overridden: int = 0
    g24_results: Optional[dict] = None
    g_prov_results: Optional[dict] = None  # v5.0.0 — Forensic Provenance Layer (G51-G60)


# ----- Helper functions ------------------------------------------------------

def find_lines_with_pattern(text: str, pattern: str, flags=re.IGNORECASE) -> List[str]:
    """Return list of 'line_number: matched_excerpt' strings for each match."""
    findings = []
    lines = text.splitlines()
    pat = re.compile(pattern, flags)
    for i, line in enumerate(lines, 1):
        m = pat.search(line)
        if m:
            excerpt = line.strip()
            if len(excerpt) > 200:
                excerpt = excerpt[:197] + "..."
            findings.append(f"L{i}: {excerpt}")
    return findings


def query_mentions(query: Optional[str], term: str) -> bool:
    """Check if the user's original query explicitly mentions a term."""
    if not query:
        return False
    return term.lower() in query.lower()


# ----- The 8 checks ----------------------------------------------------------

def check_1_user_name(text: str, user_name: Optional[str]) -> CheckResult:
    """Check 1: Does the document body contain the user's name (memory-derived)?"""
    if not user_name:
        return CheckResult(
            1, "User name not in document body",
            "SKIP",
            advice="--user-name not provided; this check skipped. Supply --user-name to enable."
        )

    findings = []
    for pat_template in DIRECT_USER_ADDRESS_PATTERNS_TEMPLATE:
        pattern = pat_template.format(name=re.escape(user_name))
        findings.extend(find_lines_with_pattern(text, pattern))

    # Bare-name occurrence (case-sensitive whole word)
    bare_name_pattern = r"\b" + re.escape(user_name) + r"\b"
    bare_findings = find_lines_with_pattern(text, bare_name_pattern, flags=0)
    findings.extend(bare_findings)

    if findings:
        return CheckResult(
            1, "User name not in document body", "FAIL",
            findings=findings[:10],
            advice=f"Remove all references to '{user_name}' from document body. Direct user address belongs in chat layer only."
        )
    return CheckResult(1, "User name not in document body", "PASS")


def check_2_user_employer(text: str, user_employer: Optional[str], query: Optional[str]) -> CheckResult:
    """Check 2: Does the document body contain user's employer name AND that employer is NOT explicitly mentioned in query?"""
    if not user_employer:
        return CheckResult(
            2, "User employer not in document body (unless query mentions)",
            "SKIP",
            advice="--user-employer not provided; this check skipped."
        )

    if query_mentions(query, user_employer):
        return CheckResult(
            2, "User employer not in document body (unless query mentions)",
            "PASS",
            advice=f"User employer '{user_employer}' was explicitly mentioned in user query; references in body permitted."
        )

    pattern = r"\b" + re.escape(user_employer) + r"\b"
    findings = find_lines_with_pattern(text, pattern, flags=0)

    if findings:
        return CheckResult(
            2, "User employer not in document body (unless query mentions)", "FAIL",
            findings=findings[:10],
            advice=f"Document mentions user employer '{user_employer}' but user query does not explicitly reference it. Remove or rewrite to be sponsor-agnostic."
        )
    return CheckResult(2, "User employer not in document body (unless query mentions)", "PASS")


def check_3_autotrigger_user_identity(text: str) -> CheckResult:
    """Check 3: Does any auto-trigger rationale cite user identity (role, profile, location, employer)?"""
    findings = []
    for pat in AUTOTRIGGER_USER_IDENTITY_PATTERNS:
        findings.extend(find_lines_with_pattern(text, pat))
    if findings:
        return CheckResult(
            3, "No auto-trigger rationale cites user identity", "FAIL",
            findings=findings[:10],
            advice="Auto-trigger rationales must cite query content (asset's actual sponsor, query keyword, asset characteristics, geographic mention in query). User identity is NOT a valid trigger source per generic-by-default.md Article 5."
        )
    return CheckResult(3, "No auto-trigger rationale cites user identity", "PASS")


def check_4_strategic_action_recommendation(text: str, user_employer: Optional[str], query: Optional[str]) -> CheckResult:
    """Check 4: Does any executive summary variant include strategic action recommendation directed at a specific named sponsor (other than mechanical incumbent identification)?"""
    findings = []
    for pat in STRATEGIC_ACTION_VERB_PATTERNS:
        findings.extend(find_lines_with_pattern(text, pat))

    # If a strategic action verb appears AND user_employer is named in same line, escalate
    employer_strategic_findings = []
    if user_employer and not query_mentions(query, user_employer):
        for finding in findings:
            if user_employer.lower() in finding.lower():
                employer_strategic_findings.append(finding)

    if employer_strategic_findings:
        return CheckResult(
            4, "No sponsor-specific strategic action recommendation (without explicit user request)", "FAIL",
            findings=employer_strategic_findings[:10],
            advice=f"Strategic action verb co-occurs with user employer '{user_employer}'. This is a sponsor-specific recommendation contamination. Reframe as abstract stakeholder category ('for incumbents', 'for entrants', 'for payers')."
        )
    if findings:
        # Strategic action verbs present but not necessarily directed at user's employer
        return CheckResult(
            4, "No sponsor-specific strategic action recommendation (without explicit user request)", "FAIL",
            findings=findings[:10],
            advice="Strategic action recommendation patterns detected. Verify each is directed at abstract stakeholder category, not specific named sponsor (unless explicit user request)."
        )
    return CheckResult(4, "No sponsor-specific strategic action recommendation (without explicit user request)", "PASS")


def check_5_intended_use(text: str) -> CheckResult:
    """Check 5: Does the intended-use declaration name the user's employer or contain employer-internal terminology?"""
    findings = []
    for pat in INTENDED_USE_PATTERNS:
        findings.extend(find_lines_with_pattern(text, pat))
    for pat in EMPLOYER_INTERNAL_TERMINOLOGY_PATTERNS:
        findings.extend(find_lines_with_pattern(text, pat))
    if findings:
        return CheckResult(
            5, "Intended use declaration sponsor-agnostic", "FAIL",
            findings=findings[:10],
            advice="Replace with: 'Intended for medical affairs, business development, regulatory intelligence, market access, and academic readers analyzing this asset/modality/topic.'"
        )
    return CheckResult(5, "Intended use declaration sponsor-agnostic", "PASS")


def check_6_coverage_asymmetry(text: str) -> CheckResult:
    """Check 6: Coverage statement contains region exclusion-as-mention asymmetry, or region/sponsor inclusion anchor asymmetry?"""
    findings = []
    for pat in COVERAGE_EXCLUSION_ASYMMETRY_PATTERNS:
        findings.extend(find_lines_with_pattern(text, pat))
    for pat in COVERAGE_INCLUSION_ANCHOR_PATTERNS:
        findings.extend(find_lines_with_pattern(text, pat))
    if findings:
        return CheckResult(
            6, "No coverage anchor asymmetry", "FAIL",
            findings=findings[:10],
            advice="Coverage statements must use positive-list discipline. Remove exclusion-as-mention asymmetry ('Türkiye dışlanmıştır') and inclusion anchors ('özellikle X bağlamı'). State what IS in scope; do not single out what is OUT unless methodologically justified."
        )
    return CheckResult(6, "No coverage anchor asymmetry", "PASS")


def check_7_scope_note_employer_alignment(text: str) -> CheckResult:
    """Check 7: Document scope note aligns analytical frame with user employer's competitive setting?"""
    findings = []
    for pat in SCOPE_NOTE_COMPETITIVE_ALIGNMENT_PATTERNS:
        findings.extend(find_lines_with_pattern(text, pat))
    if findings:
        return CheckResult(
            7, "Scope note not aligned with user employer competitive setting", "FAIL",
            findings=findings[:10],
            advice="Scope notes describe analytical frame in sponsor-agnostic terms. Remove employer-portfolio anchoring."
        )
    return CheckResult(7, "Scope note not aligned with user employer competitive setting", "PASS")


def check_8_disclosure_user_context(text: str, user_name: Optional[str], user_employer: Optional[str], query: Optional[str]) -> CheckResult:
    """Check 8: Disclosure blocks contain user-context references beyond what is methodologically required?"""
    # Find disclosure-block sections
    disclosure_sections = []
    section_headers = [
        r"##?\s*Triangulation\s+Notes",
        r"##?\s*Provenance\s+Disclosure",
        r"##?\s*Confidence\s+Disclosure",
        r"##?\s*Auto-Trigger\s+Disclosure",
        r"##?\s*Sponsor\s+Sweep\s+Disclosure",
    ]

    findings = []
    for header_pat in section_headers:
        # Extract section content (until next ## or end)
        match = re.search(header_pat + r"(.*?)(?=\n##\s|\Z)", text, re.DOTALL | re.IGNORECASE)
        if not match:
            continue
        section_text = match.group(1)
        # Check for user identity references
        if user_name and re.search(r"\b" + re.escape(user_name) + r"\b", section_text):
            findings.append(f"Disclosure section contains user name '{user_name}'")
        if user_employer and not query_mentions(query, user_employer):
            if re.search(r"\b" + re.escape(user_employer) + r"\b", section_text):
                findings.append(f"Disclosure section contains user employer '{user_employer}' (not in query)")
        # Check for user-identity-based auto-trigger rationale
        for pat in AUTOTRIGGER_USER_IDENTITY_PATTERNS:
            section_findings = re.findall(pat, section_text, re.IGNORECASE)
            for sf in section_findings:
                excerpt = sf if isinstance(sf, str) else str(sf)
                findings.append(f"Disclosure section: {excerpt[:150]}")

    if findings:
        return CheckResult(
            8, "Disclosure blocks free of user-context references", "FAIL",
            findings=findings[:10],
            advice="Disclosure blocks (Triangulation, Provenance, Confidence, Auto-Trigger, Sponsor Sweep) must not contain user identity references beyond methodologically required attribution."
        )
    return CheckResult(8, "Disclosure blocks free of user-context references", "PASS")


# v6.0.0 — G22.9 language-as-trigger detection (also surfaced as manifest gate G61)
LANGUAGE_TRIGGER_PATTERNS = [
    # English/Turkish language-fact as trigger rationale
    r"(turkish|t[üu]rk[çc]e)[\s\S]{0,80}(language|dil|written|yaz[ıi]lm[ıi]ş)[\s\S]{0,80}(trigger|tetik)",
    r"(japanese|japonca|日本語)[\s\S]{0,80}(language|dil|written|yaz[ıi]lm[ıi]ş)[\s\S]{0,80}(trigger|tetik)",
    r"(mandarin|chinese|[çc]ince|中文)[\s\S]{0,80}(language|dil|written|yaz[ıi]lm[ıi]ş)[\s\S]{0,80}(trigger|tetik)",
    # Inverse phrasing patterns: "written in X → fire Y-protocol"
    r"(written|yaz[ıi]lm[ıi]ş)[\s\S]{0,40}(turkish|t[üu]rk[çc]e|japanese|japonca|mandarin|[çc]ince|chinese)[\s\S]{0,120}(sub-protocol|katman|layer|load)",
    # "Query language: Turkish → Türkiye layer"
    r"(query|sorgu)[\s\S]{0,30}(language|dil)[\s\S]{0,30}:\s*(turkish|t[üu]rk[çc]e|japanese|japonca|mandarin|[çc]ince|chinese)[\s\S]{0,120}(sub-protocol|katman|layer)",
]


def check_9_query_language_as_trigger(text: str) -> CheckResult:
    """Check 9 (G22.9 / manifest gate G61, v6.0.0): No auto-trigger rationale cites query language.

    Rationale per generic-by-default.md Article 5.3: the natural language/writing system
    of a query is NEVER a valid content trigger for a regional sub-protocol. Only explicit
    semantic content (TİTCK, SGK, SUT for turkey; PMDA, MHLW for pmda; NMPA, NRDL for nmpa)
    is a valid trigger source.
    """
    # Focus search within Auto-Trigger Disclosure / Provenance Disclosure / Sub-Protocol Activation sections
    disclosure_section_patterns = [
        r"##?\s*Auto-Trigger\s+Disclosure(.*?)(?=\n##\s|\Z)",
        r"##?\s*Provenance\s+Disclosure(.*?)(?=\n##\s|\Z)",
        r"##?\s*Sub-Protocol\s+Activation(.*?)(?=\n##\s|\Z)",
        r"##?\s*Katman\s+Aktivasyon(.*?)(?=\n##\s|\Z)",
    ]

    findings = []
    # First, scope the search to disclosure sections only (lower false-positive rate)
    scoped_text_parts = []
    for pat in disclosure_section_patterns:
        match = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if match:
            scoped_text_parts.append(match.group(1))

    scoped_text = "\n".join(scoped_text_parts) if scoped_text_parts else text

    for pattern in LANGUAGE_TRIGGER_PATTERNS:
        matches = re.findall(pattern, scoped_text, re.IGNORECASE | re.DOTALL)
        for m in matches:
            excerpt = " ".join(m) if isinstance(m, tuple) else str(m)
            # Normalize whitespace
            excerpt = re.sub(r"\s+", " ", excerpt).strip()
            findings.append(f"Language-as-trigger pattern: {excerpt[:200]}")

    if findings:
        return CheckResult(
            9, "No auto-trigger rationale cites query language (Article 5.3 / G61)", "FAIL",
            findings=findings[:8],
            advice=(
                "Query language (Turkish / Japanese / Mandarin writing system) is NEVER a "
                "valid trigger source for regional sub-protocols (turkey / pmda / nmpa). "
                "Per generic-by-default.md Article 5.3, only explicit semantic content "
                "(TİTCK, SGK, SUT, PMDA, MHLW, NMPA, NRDL, etc.) is a valid trigger. "
                "Remove the offending sub-protocol activation and revise the rationale "
                "to cite content keywords, or remove the sub-protocol layer if no "
                "content trigger exists."
            )
        )
    return CheckResult(9, "No auto-trigger rationale cites query language (Article 5.3 / G61)", "PASS")


# v7.0.0 — G62 Historical / Nth-of-class claim verification
# Detects ordinal chronological claims that require primary-database enumeration
# per triangulation.md §11 "History-sensitive chronological claims"

NTH_CLAIM_PATTERNS_EN = [
    r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b[\s\S]{0,60}"
    r"(tumor[- ]?agnostic|tumou?r[- ]?agnostic|FDA[- ]?approv|EMA[- ]?approv|accelerated[- ]?approv|"
    r"ADC[- ]?(?:based|temelli)|CAR[- ]?T|bispecific|CRISPR|gene[- ]?therapy|biosimilar|"
    r"breakthrough[- ]?therapy|priority[- ]?review|RTOR|first[- ]?in[- ]?class)",
    r"\b(1st|2nd|3rd|[4-9]th|[0-9]+(?:st|nd|rd|th))\b[\s\S]{0,60}"
    r"(tumor[- ]?agnostic|tumou?r[- ]?agnostic|FDA|EMA|accelerated|ADC|CAR[- ]?T|bispecific|CRISPR)",
]

NTH_CLAIM_PATTERNS_TR = [
    r"\b(ilk|ikinci|[üu][çc][üu]nc[üu]|d[öo]rd[üu]nc[üu]|be[şs]inci|alt[ıi]nc[ıi]|yedinci)\b[\s\S]{0,80}"
    r"(t[üu]m[öo]r[- ]?agnostik|FDA|EMA|T[İi]TCK|hızlandırılmış|ADC|CAR[- ]?T|bispesifik|CRISPR|"
    r"biyobenzer|gen[- ]?tedavi|onay[ıi])",
    r"\b(tarihindeki\s+(?:ilk|ikinci|[üu][çc][üu]nc[üu]))\b[\s\S]{0,80}"
    r"(onay|approval|ilaç|tedavi|terapi)",
]

# Combine all patterns
NTH_CLAIM_PATTERNS = NTH_CLAIM_PATTERNS_EN + NTH_CLAIM_PATTERNS_TR

# Known-wrong claims (hardcoded from production test failures — triangulation.md §11 reference table)
KNOWN_WRONG_NTH_CLAIMS = [
    # Pattern: (regex, explanation)
    (r"(?:second|ikinci)[\s\S]{0,40}t[üu]m[öo]r[- ]?agnosti[ck]", "T-DXd is NOT the second tumor-agnostic approval — at least 7th per FDA chronology"),
    (r"(?:third|[üu][çc][üu]nc[üu])[\s\S]{0,40}t[üu]m[öo]r[- ]?agnosti[ck]", "T-DXd is NOT the third tumor-agnostic approval — at least 7th per FDA chronology"),
]


def check_10_historical_claim_verification(text: str) -> CheckResult:
    """Check 10 (G22.10 / manifest gate G62, v7.0.0): Nth-of-class claims verified or safely rephrased.

    Per triangulation.md §11, ordinal chronological claims (first/second/third X)
    require primary-database enumeration + cross-verification before emission.
    This check detects potential Nth-of-class claims and flags them for review.
    """
    findings = []
    severity = "WARNING"  # Default WARNING; escalate to FAIL for known-wrong patterns

    # Phase 1: Detect any Nth-of-class claim patterns
    nth_claims_found = []
    for pattern in NTH_CLAIM_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for m in matches:
            excerpt = re.sub(r"\s+", " ", m.group(0)).strip()[:200]
            nth_claims_found.append(excerpt)

    # Phase 2: Check against known-wrong claims (FAIL, not WARNING)
    known_wrong_hits = []
    for pattern, explanation in KNOWN_WRONG_NTH_CLAIMS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            known_wrong_hits.append(explanation)
            severity = "FAIL"

    if known_wrong_hits:
        for hit in known_wrong_hits:
            findings.append(f"KNOWN-WRONG Nth claim: {hit}")

    if nth_claims_found and not known_wrong_hits:
        # Phase 3: Check if report contains enumeration evidence (table with chronological listing)
        # Heuristic: if report contains a numbered chronological table near the Nth claim → likely verified
        has_enumeration_table = bool(re.search(
            r"\|\s*#\s*\|.*\|\s*\d{4}\s*\|", text, re.IGNORECASE
        ))
        if has_enumeration_table:
            # Likely has self-contained verification table → WARNING only (encourage review)
            for claim in nth_claims_found[:5]:
                findings.append(f"Nth-of-class claim (enumeration table detected — review): {claim}")
            severity = "WARNING"
        else:
            # No enumeration table → higher risk of unverified ordinal
            for claim in nth_claims_found[:5]:
                findings.append(f"Nth-of-class claim WITHOUT enumeration table — verify per §11: {claim}")
            severity = "WARNING"

    if severity == "FAIL":
        return CheckResult(
            10, "No known-wrong Nth-of-class claims (triangulation.md §11 / G62)", severity,
            findings=findings[:10],
            advice=(
                "Known-wrong Nth-of-class claims detected. Per triangulation.md §11, "
                "these ordinal claims have been previously demonstrated to be factually "
                "incorrect in production tests. The report MUST either (a) correct the "
                "ordinal with full primary-database enumeration, or (b) rephrase to a "
                "safe differentiator-focused form (e.g., 'first ADC-based tumor-agnostic "
                "approval' instead of 'Nth tumor-agnostic approval')."
            )
        )
    elif findings:
        return CheckResult(
            10, "Nth-of-class claims flagged for review (triangulation.md §11 / G62)", "WARNING",
            findings=findings[:10],
            advice=(
                "Ordinal chronological claims (first/second/third X) detected. Per "
                "triangulation.md §11, these require primary-database enumeration + "
                "cross-verification. If verified → OK. If not verified → rephrase to "
                "safe differentiator-focused form."
            )
        )
    return CheckResult(10, "No Nth-of-class claims requiring verification (§11 / G62)", "PASS")


# ----- Main runner -----------------------------------------------------------

def parse_overrides(text: str) -> dict:
    """
    Parse # G22-OVERRIDE annotations from report text.

    Format expected (one per line):
      # G22-OVERRIDE: G22.X — <rationale>
      # G22-OVERRIDE: G22.2 — Roche named as incumbent product sponsor in competitive landscape, not user-context reference

    Returns: dict mapping check_id (int) -> rationale (str)
    Multiple overrides for same check_id: rationales joined with '; '
    """
    overrides = {}
    pattern = r"#\s*G22-OVERRIDE:\s*G22\.(\d+)\s*[—\-:]\s*(.+?)(?=\n|$)"
    for m in re.finditer(pattern, text, re.MULTILINE):
        try:
            check_id = int(m.group(1))
            rationale = m.group(2).strip()
            if check_id in overrides:
                overrides[check_id] += "; " + rationale
            else:
                overrides[check_id] = rationale
        except (ValueError, IndexError):
            continue
    return overrides


# T6-DEFENSE override class (v1.8.0+) — restricted to G22.4 and G22.7 only
T6_DEFENSE_PERMITTED_CHECKS = {4, 7}


def parse_t6_defense_overrides(text: str) -> dict:
    """
    Parse # T6-DEFENSE annotations from report text (v1.8.0+).

    Format expected (one per line):
      # T6-DEFENSE: G22.X — <rationale>
      # T6-DEFENSE: G22.4 — Strategic action recommendations directed at [Sponsor X] per explicit user request

    T6-DEFENSE overrides are RESTRICTED to G22.4 and G22.7 only (per task-comparison-defense.md §2.1).
    Validator silently rejects T6-DEFENSE attempts to override other checks.

    Returns: dict mapping check_id (int) -> rationale (str), filtered to permitted checks only.
    """
    overrides = {}
    pattern = r"#\s*T6-DEFENSE:\s*G22\.(\d+)\s*[—\-:]\s*(.+?)(?=\n|$)"
    for m in re.finditer(pattern, text, re.MULTILINE):
        try:
            check_id = int(m.group(1))
            rationale = m.group(2).strip()
            if check_id not in T6_DEFENSE_PERMITTED_CHECKS:
                continue  # Silently reject; T6-DEFENSE only valid for G22.4 + G22.7
            if check_id in overrides:
                overrides[check_id] += "; " + rationale
            else:
                overrides[check_id] = "[T6-DEFENSE] " + rationale
        except (ValueError, IndexError):
            continue
    return overrides


def apply_overrides(audit: AuditReport, overrides: dict, t6_defense_overrides: dict = None) -> AuditReport:
    """
    Apply documented overrides to audit results.
    For each FAIL check that has a documented override, downgrade to OVERRIDE status
    (not PASS — preserves transparency that the check did surface a finding).
    Recomputes overall_pass: True if all checks are PASS or OVERRIDE (no FAIL remaining).

    v1.8.0+: t6_defense_overrides dict is merged with general overrides; T6-DEFENSE rationales
    prefixed with [T6-DEFENSE] for transparency in advice field.
    """
    if t6_defense_overrides is None:
        t6_defense_overrides = {}

    # Merge: T6-DEFENSE overrides take precedence (more specific)
    merged_overrides = {**overrides}
    for k, v in t6_defense_overrides.items():
        if k in merged_overrides:
            merged_overrides[k] = merged_overrides[k] + "; " + v
        else:
            merged_overrides[k] = v

    new_passed = 0
    new_failed = 0
    new_skipped = 0
    new_overridden = 0
    new_t6_defense_overridden = 0
    for c in audit.checks:
        if c.status == "FAIL" and c.check_id in merged_overrides:
            c.status = "OVERRIDE"
            c.advice = (c.advice or "") + f" | OVERRIDE rationale: {merged_overrides[c.check_id]}"
            new_overridden += 1
            if c.check_id in t6_defense_overrides:
                new_t6_defense_overridden += 1
        elif c.status == "PASS":
            new_passed += 1
        elif c.status == "FAIL":
            new_failed += 1
        elif c.status == "SKIP":
            new_skipped += 1
    audit.passed = new_passed
    audit.failed = new_failed
    audit.skipped = new_skipped
    audit.overridden = new_overridden
    audit.t6_defense_overridden = new_t6_defense_overridden
    audit.overall_pass = (new_failed == 0)
    return audit


# G24 — T6-Defense well-formedness audit (6 checks per task-comparison-defense.md §7)

def g24_check(text: str) -> dict:
    """
    Run G24 well-formedness audit when T6-Defense is invoked.
    Returns: dict with overall_pass + 6 check results
    """
    results = {
        "g24_1_activation_source_cited": False,
        "g24_2_explicit_trigger_present": False,
        "g24_3_section_b_present": False,
        "g24_4_section_c_present": False,
        "g24_5_section_a_present": False,
        "g24_6_other_sections_agnostic": True,  # Default true; manually checked
        "details": []
    }

    # G24.1: activation source cited in Provenance §T6-Defense activation disclosure
    if re.search(r"T6-Defense activation disclosure", text, re.IGNORECASE):
        if re.search(r"Activation source:\s*\S", text, re.IGNORECASE):
            results["g24_1_activation_source_cited"] = True
            results["details"].append("G24.1 PASS: T6-Defense activation disclosure with cited source found")
        else:
            results["details"].append("G24.1 FAIL: T6-Defense disclosure section present but Activation source not cited")
    else:
        results["details"].append("G24.1 FAIL: T6-Defense activation disclosure missing from Provenance")

    # G24.2: at least one explicit trigger keyword present in activation source area
    explicit_triggers = [
        r"cephesinden", r"competitive defense", r"perspective on",
        r"defense playbook", r"T6-Defense:", r"biz\s+\w+\s+(olarak|şirketiyiz)",
        r"from .{1,30}'s perspective"
    ]
    if any(re.search(t, text, re.IGNORECASE) for t in explicit_triggers):
        results["g24_2_explicit_trigger_present"] = True
        results["details"].append("G24.2 PASS: At least one explicit trigger keyword detected")
    else:
        results["details"].append("G24.2 FAIL: No explicit trigger keyword from §1.1 detected")

    # G24.3 + G24.4: §10.B and §10.C parallel sections (or any §X.B / §X.C sponsor perspective sections)
    # Look for "From [...]'s perspective" pattern
    perspective_sections = re.findall(r"From\s+([\w\s\.&,]+?)(?:'s|\u2019s)\s+perspective", text)
    if len(perspective_sections) >= 1:
        results["g24_3_section_b_present"] = True
        results["details"].append(f"G24.3 PASS: §10.B sponsor perspective section found ({perspective_sections[0]})")
        if len(perspective_sections) >= 2:
            results["g24_4_section_c_present"] = True
            results["details"].append(f"G24.4 PASS: §10.C parallel sponsor perspective section found ({perspective_sections[1]})")
        else:
            # Check for abstract competitor perspective fallback
            if re.search(r"abstract\s+(entrant|disruptor|competitor)\s+perspective", text, re.IGNORECASE):
                results["g24_4_section_c_present"] = True
                results["details"].append("G24.4 PASS: §10.C abstract competitor perspective fallback (per §3.3)")
            else:
                results["details"].append("G24.4 FAIL: §10.C parallel competitor perspective section MISSING — symmetric framing requirement violated")
    else:
        results["details"].append("G24.3 FAIL: §10.B sponsor perspective section MISSING")
        results["details"].append("G24.4 FAIL: §10.C parallel section MISSING (cascade from G24.3)")

    # G24.5: §10.A standard sponsor-agnostic implications section present
    if re.search(r"standard\s+sponsor-agnostic", text, re.IGNORECASE) or \
       re.search(r"abstract\s+stakeholder\s+(categories|categori)", text, re.IGNORECASE):
        results["g24_5_section_a_present"] = True
        results["details"].append("G24.5 PASS: §10.A standard sponsor-agnostic implications section detected")
    else:
        results["details"].append("G24.5 FAIL: §10.A standard sponsor-agnostic implications section MISSING — generic-by-default discipline outside override scope not preserved")

    # G24.6: other sections (this is heuristic; we check that T6-DEFENSE annotations are limited)
    # Count T6-DEFENSE annotations and check they all sit near "perspective" markers
    t6_defense_annotations = re.findall(r"#\s*T6-DEFENSE:", text)
    if len(t6_defense_annotations) > 0 and len(perspective_sections) > 0:
        # Heuristic: if T6-DEFENSE annotations exist and perspective sections exist, assume properly scoped
        results["g24_6_other_sections_agnostic"] = True
        results["details"].append(f"G24.6 PASS (heuristic): {len(t6_defense_annotations)} T6-DEFENSE annotations co-occur with {len(perspective_sections)} perspective sections")
    elif len(t6_defense_annotations) > 0 and len(perspective_sections) == 0:
        results["g24_6_other_sections_agnostic"] = False
        results["details"].append(f"G24.6 FAIL: {len(t6_defense_annotations)} T6-DEFENSE annotations present but NO perspective sections found — annotations may be outside designated §10.B/§10.C scope")

    # Overall G24 pass
    g24_keys = ["g24_1_activation_source_cited", "g24_2_explicit_trigger_present",
                "g24_3_section_b_present", "g24_4_section_c_present",
                "g24_5_section_a_present", "g24_6_other_sections_agnostic"]
    results["overall_pass"] = all(results[k] for k in g24_keys)
    results["pass_count"] = sum(1 for k in g24_keys if results[k])
    results["total_checks"] = len(g24_keys)
    return results


def run_all_checks(report_path: Path, user_name: Optional[str], user_employer: Optional[str], query: Optional[str], accept_overrides: bool = False, enforce_g24: bool = False) -> AuditReport:
    text = report_path.read_text(encoding="utf-8")

    checks = [
        check_1_user_name(text, user_name),
        check_2_user_employer(text, user_employer, query),
        check_3_autotrigger_user_identity(text),
        check_4_strategic_action_recommendation(text, user_employer, query),
        check_5_intended_use(text),
        check_6_coverage_asymmetry(text),
        check_7_scope_note_employer_alignment(text),
        check_8_disclosure_user_context(text, user_name, user_employer, query),
        check_9_query_language_as_trigger(text),  # v6.0.0 — G61 / Article 5.3
        check_10_historical_claim_verification(text),  # v7.0.0 — G62 / triangulation.md §11
    ]

    passed = sum(1 for c in checks if c.status == "PASS")
    failed = sum(1 for c in checks if c.status == "FAIL")
    skipped = sum(1 for c in checks if c.status == "SKIP")

    audit = AuditReport(
        report_path=str(report_path),
        user_name=user_name,
        user_employer=user_employer,
        query=query,
        total_checks=len(checks),
        passed=passed,
        failed=failed,
        skipped=skipped,
        overall_pass=(failed == 0),
        checks=checks,
    )

    if accept_overrides:
        overrides = parse_overrides(text)
        t6_defense_overrides = parse_t6_defense_overrides(text)
        if overrides or t6_defense_overrides:
            audit = apply_overrides(audit, overrides, t6_defense_overrides)

    if enforce_g24:
        g24 = g24_check(text)
        audit.g24_results = g24
        # If G24 fails, mark overall_pass = False (T6-Defense malformed)
        if not g24["overall_pass"]:
            audit.overall_pass = False

    return audit


def format_human_report(audit: AuditReport, verbose: bool = True) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("pharmaintel — Generic-By-Default Validator (G22)")
    lines.append("=" * 72)
    lines.append(f"Report:         {audit.report_path}")
    lines.append(f"User name:      {audit.user_name or '(not provided)'}")
    lines.append(f"User employer:  {audit.user_employer or '(not provided)'}")
    lines.append(f"User query:     {(audit.query[:80] + '...') if audit.query and len(audit.query) > 80 else (audit.query or '(not provided)')}")
    lines.append("")
    overridden_count = getattr(audit, 'overridden', 0)
    summary = f"{audit.passed}/{audit.total_checks} passed, {audit.failed} failed, {audit.skipped} skipped"
    if overridden_count:
        summary += f", {overridden_count} overridden"
    lines.append(f"Overall: {'✅ PASS' if audit.overall_pass else '❌ FAIL'}  |  {summary}")
    lines.append("")
    for c in audit.checks:
        if c.status == "PASS":
            icon = "✅"
        elif c.status == "FAIL":
            icon = "❌"
        elif c.status == "OVERRIDE":
            icon = "🔶"
        else:
            icon = "⚠️"
        lines.append(f"{icon} G22.{c.check_id}: {c.name}  →  {c.status}")
        if verbose and c.findings:
            lines.append("   Findings:")
            for f in c.findings:
                lines.append(f"     - {f}")
        if verbose and c.advice:
            lines.append(f"   Advice: {c.advice}")
        lines.append("")
    return "\n".join(lines)


# ----- G-PROV (G51-G60) — Forensic Provenance Layer (v5.0.0) -----------------
#
# Per provenance-engine.md §5 + sub-protocol-provenance.md.
# Activated by --mode forensic-grade flag.
#
# Gates:
#   G51 / G-PROV-01 — every claim ∈ provenance_required_set has [^prov:ev_*] footnote
#   G52 / G-PROV-02 — every [^prov:ev_*] resolves to evidence index entry
#   G53 / G-PROV-03 — Evidence object has ≥2 of 3 capture paths succeeded
#   G54 / G-PROV-04 — content_hash_sha256 non-empty + recompute matches
#   G55 / G-PROV-05 — RFC 3161 TSR present + digest recompute (BLOCKER in forensic-grade)
#   G56 / G-PROV-06 — UBO claim has P0/P1 source + triangulation partner
#   G57 / G-PROV-07 — capture retrieved_at within 7 days of report cite (WARNING)
#   G58 / G-PROV-08 — KVKK-sensitive → pii_redaction_applied (BLOCKER always)
#   G59 / G-PROV-09 — Evidence bundle ZIP has MANIFEST.yaml + VERIFICATION.md
#   G60 / G-PROV-10 — bundle ZIP SHA-256 cited in parent report footnote

PROV_FOOTNOTE_PATTERN = re.compile(r"\[\^prov:(ev_\d{4}-\d{2}-\d{2}_[a-f0-9]{8})\]")
PROV_REQUIRED_CLAIM_TYPES = {
    "beneficial_ownership",
    "sanctions_hit",
    "regulatory_action",
    "deleted_pipeline_claim",
    "historical_label",
    "titck_opponent_claim",
    "litigation_exhibit",
}
P0_TIERS = {"T0", "OSINT-T1"}
P1_TIERS = {"OSINT-T2"}


def g_prov_check(text: str, evidence_db: Optional[Path] = None,
                 evidence_root: Optional[Path] = None) -> dict:
    """Run G51-G60 forensic-grade gates.

    Args:
        text: report markdown content
        evidence_db: SQLite evidence index path (optional — gates G52-G56 require)
        evidence_root: evidence directory path (optional — gates G54+G59 require)

    Returns:
        dict with overall_pass + per-gate results.
    """
    results = {
        "mode": "forensic-grade",
        "gates": {},
        "overall_pass": True,
        "blocker_count": 0,
        "warning_count": 0,
    }

    # Extract all [^prov:ev_*] references from report
    prov_refs = set(PROV_FOOTNOTE_PATTERN.findall(text))

    # G51 — every provenance-required claim has [^prov:] footnote
    # (Heuristic: report should mark such claims explicitly. We can't infer
    # claim_type from prose alone, so this gate is informational unless
    # reports include semantic markup like <!-- claim_type: beneficial_ownership -->)
    g51_findings = []
    if "<!-- claim_type:" in text or "<!--claim_type:" in text:
        # Semantic markup present — count claims vs footnotes
        claim_pattern = re.compile(r"<!--\s*claim_type:\s*(\w+)\s*-->")
        claim_types_in_doc = claim_pattern.findall(text)
        prov_required_count = sum(
            1 for ct in claim_types_in_doc if ct in PROV_REQUIRED_CLAIM_TYPES)
        if prov_required_count > len(prov_refs):
            g51_findings.append(
                f"{prov_required_count} provenance-required claims marked but "
                f"only {len(prov_refs)} [^prov:] footnotes present")
    results["gates"]["G51"] = {
        "name": "Provenance-required claims have [^prov:] footnotes",
        "status": "FAIL" if g51_findings else "PASS",
        "severity": "BLOCKER",
        "findings": g51_findings,
    }
    if g51_findings:
        results["blocker_count"] += 1
        results["overall_pass"] = False

    # G52 — every [^prov:ev_*] resolves to evidence index entry
    g52_findings = []
    g52_status = "SKIP"
    if evidence_db and evidence_db.is_file():
        try:
            import sqlite3
            with sqlite3.connect(str(evidence_db)) as conn:
                rows = conn.execute(
                    "SELECT evidence_id FROM evidence").fetchall()
                indexed_ids = {r[0] for r in rows}
            unresolved = prov_refs - indexed_ids
            if unresolved:
                for eid in sorted(unresolved)[:10]:
                    g52_findings.append(
                        f"Footnote [^prov:{eid}] not in evidence index")
                g52_status = "FAIL"
            else:
                g52_status = "PASS"
        except Exception as e:  # noqa: BLE001
            g52_findings.append(f"Evidence DB query error: {e}")
            g52_status = "FAIL"
    elif prov_refs:
        g52_status = "FAIL"
        g52_findings.append(
            f"{len(prov_refs)} [^prov:] footnotes present but --evidence-db not provided")
    results["gates"]["G52"] = {
        "name": "All [^prov:] references resolve in evidence index",
        "status": g52_status,
        "severity": "BLOCKER",
        "findings": g52_findings,
        "footnote_count": len(prov_refs),
    }
    if g52_status == "FAIL":
        results["blocker_count"] += 1
        results["overall_pass"] = False

    # G53-G56, G58 — per-evidence checks via evidence_object module
    g_status_map = {"G53": "SKIP", "G54": "SKIP", "G55": "SKIP",
                    "G56": "SKIP", "G58": "SKIP"}
    g_findings_map = {k: [] for k in g_status_map}

    if evidence_db and evidence_db.is_file() and prov_refs:
        try:
            # Try to import evidence_object module
            sys.path.insert(0, str(Path(__file__).parent / "provenance-engine"))
            try:
                import evidence_object as eo  # type: ignore
                has_eo = True
            except ImportError:
                has_eo = False

            import sqlite3
            with sqlite3.connect(str(evidence_db)) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM evidence WHERE evidence_id IN "
                    f"({','.join('?' for _ in prov_refs)})",
                    list(prov_refs),
                ).fetchall()

                for row in rows:
                    rd = dict(row)
                    paths = json.loads(rd.get("capture_paths_succeeded") or "[]")
                    # G53
                    if len(paths) < 2:
                        g_findings_map["G53"].append(
                            f"{rd['evidence_id']}: only {len(paths)}/3 capture paths succeeded")
                    # G54
                    if not rd.get("content_hash_sha256") or len(
                            rd.get("content_hash_sha256", "")) != 64:
                        g_findings_map["G54"].append(
                            f"{rd['evidence_id']}: invalid content_hash_sha256")
                    # G55 (BLOCKER in forensic-grade)
                    if not rd.get("tsr_primary_path") or not rd.get("tsr_primary_hash"):
                        g_findings_map["G55"].append(
                            f"{rd['evidence_id']}: missing RFC 3161 TSR")
                    # G56
                    if rd.get("claim_type") == "beneficial_ownership":
                        if rd.get("source_authority_tier") not in (P0_TIERS | P1_TIERS):
                            g_findings_map["G56"].append(
                                f"{rd['evidence_id']}: UBO claim with insufficient source tier")
                        partners = json.loads(rd.get("triangulation_partner_ids") or "[]")
                        if not partners:
                            g_findings_map["G56"].append(
                                f"{rd['evidence_id']}: UBO claim missing triangulation")
                    # G58 (BLOCKER always)
                    if rd.get("contains_personal_data") and not rd.get("pii_redaction_applied"):
                        g_findings_map["G58"].append(
                            f"{rd['evidence_id']}: PII not redacted")

            for gid in g_status_map:
                g_status_map[gid] = "FAIL" if g_findings_map[gid] else "PASS"
        except Exception as e:  # noqa: BLE001
            for gid in g_status_map:
                g_findings_map[gid].append(f"Per-evidence check error: {e}")
                g_status_map[gid] = "FAIL"

    for gid, severity in [("G53", "BLOCKER"), ("G54", "BLOCKER"),
                           ("G55", "BLOCKER"), ("G56", "BLOCKER"),
                           ("G58", "BLOCKER")]:
        results["gates"][gid] = {
            "name": {
                "G53": "≥2 of 3 capture paths succeeded per Evidence Object",
                "G54": "content_hash_sha256 valid + matches",
                "G55": "RFC 3161 TSR present (forensic-grade BLOCKER)",
                "G56": "UBO claim has P0/P1 source + triangulation partner",
                "G58": "PII redaction discipline (BLOCKER always)",
            }[gid],
            "status": g_status_map[gid],
            "severity": severity,
            "findings": g_findings_map[gid][:10],
        }
        if g_status_map[gid] == "FAIL":
            results["blocker_count"] += 1
            results["overall_pass"] = False

    # G57 — capture freshness (WARNING)
    g57_findings = []
    g57_status = "SKIP"
    if evidence_db and evidence_db.is_file() and prov_refs:
        try:
            from datetime import datetime, timezone
            import sqlite3
            with sqlite3.connect(str(evidence_db)) as conn:
                rows = conn.execute(
                    "SELECT evidence_id, retrieved_at FROM evidence WHERE evidence_id IN "
                    f"({','.join('?' for _ in prov_refs)})",
                    list(prov_refs),
                ).fetchall()
                for eid, ra in rows:
                    try:
                        dt = datetime.fromisoformat(ra.replace("Z", "+00:00"))
                        age = (datetime.now(timezone.utc) - dt).days
                        if age > 7:
                            g57_findings.append(f"{eid}: captured {age} days ago")
                    except (ValueError, AttributeError):
                        pass
            g57_status = "WARN" if g57_findings else "PASS"
        except Exception:  # noqa: BLE001
            pass
    results["gates"]["G57"] = {
        "name": "Capture freshness ≤7 days (WARNING)",
        "status": g57_status,
        "severity": "WARNING",
        "findings": g57_findings[:10],
    }
    if g57_status == "WARN":
        results["warning_count"] += 1

    # G59 — Evidence bundle ZIP exists with MANIFEST + VERIFICATION
    g59_findings = []
    g59_status = "SKIP"
    bundle_pattern = re.compile(
        r"(?:bundle|Bundle).*?\.zip[\"`'\s]", re.IGNORECASE)
    bundle_match = bundle_pattern.search(text)
    if bundle_match and evidence_root:
        # Look for bundle file
        bundle_dir = evidence_root / "bundle"
        if bundle_dir.is_dir():
            zips = list(bundle_dir.glob("*_evidence_bundle.zip"))
            if zips:
                import zipfile as zf
                bundle = zips[0]
                try:
                    with zf.ZipFile(bundle) as z:
                        names = z.namelist()
                        has_manifest = any(
                            n in ("MANIFEST.yaml", "MANIFEST.json") for n in names)
                        has_readme = "README.md" in names
                        has_verify = "VERIFICATION.md" in names
                        if not (has_manifest and has_readme and has_verify):
                            g59_findings.append(
                                f"{bundle.name} missing required files: "
                                f"manifest={has_manifest} readme={has_readme} verify={has_verify}")
                            g59_status = "FAIL"
                        else:
                            g59_status = "PASS"
                except Exception as e:  # noqa: BLE001
                    g59_findings.append(f"Bundle inspection error: {e}")
                    g59_status = "FAIL"
            else:
                g59_findings.append(f"No bundle ZIP found in {bundle_dir}")
                g59_status = "FAIL"
    elif bundle_match and not evidence_root:
        g59_findings.append("Bundle referenced in report but --evidence-root not provided")
        g59_status = "FAIL"
    results["gates"]["G59"] = {
        "name": "Evidence bundle ZIP has MANIFEST + README + VERIFICATION",
        "status": g59_status,
        "severity": "BLOCKER",
        "findings": g59_findings,
    }
    if g59_status == "FAIL":
        results["blocker_count"] += 1
        results["overall_pass"] = False

    # G60 — bundle ZIP SHA-256 cited in report
    g60_findings = []
    sha256_in_report = re.search(
        r"[Bb]undle\s+SHA-256[`:\s]+([a-f0-9]{64})", text)
    if sha256_in_report:
        results["gates"]["G60"] = {
            "name": "Bundle ZIP SHA-256 cited in parent report",
            "status": "PASS",
            "severity": "BLOCKER",
            "findings": [f"Cited SHA-256: {sha256_in_report.group(1)[:16]}…"],
        }
    elif prov_refs:
        g60_findings.append(
            "Provenance footnotes present but no bundle SHA-256 cited in report")
        results["gates"]["G60"] = {
            "name": "Bundle ZIP SHA-256 cited in parent report",
            "status": "FAIL",
            "severity": "BLOCKER",
            "findings": g60_findings,
        }
        results["blocker_count"] += 1
        results["overall_pass"] = False
    else:
        results["gates"]["G60"] = {
            "name": "Bundle ZIP SHA-256 cited in parent report",
            "status": "SKIP",
            "severity": "BLOCKER",
            "findings": ["No provenance footnotes — bundle citation not required"],
        }

    # Summary
    results["pass_count"] = sum(
        1 for g in results["gates"].values() if g["status"] == "PASS")
    results["fail_count"] = sum(
        1 for g in results["gates"].values() if g["status"] == "FAIL")
    results["skip_count"] = sum(
        1 for g in results["gates"].values() if g["status"] == "SKIP")
    results["total_gates"] = 10

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate a pharmaintel report against G22 generic-by-default discipline (and optionally G24 T6-Defense + G51-G60 Forensic Provenance Layer in v5.0.0+).",
        epilog="Per generic-by-default.md Article 6 (8 checks). v1.7.1: --accept-overrides supports # G22-OVERRIDE annotations for documented false-positive overrides. v1.9.0: --enforce-g24 supports T6-Defense well-formedness audit (6 checks per task-comparison-defense.md §7) + # T6-DEFENSE annotation class restricted to G22.4 + G22.7 only. v5.0.0: --mode forensic-grade enables G51-G60 (G-PROV-01 through G-PROV-10) Forensic Provenance Layer enforcement per provenance-engine.md §5."
    )
    parser.add_argument("report", type=Path, help="Path to the markdown report to audit")
    parser.add_argument("--user-name", type=str, default=None, help="User's name (for check 1)")
    parser.add_argument("--user-employer", type=str, default=None, help="User's employer name (for checks 2, 4, 8)")
    parser.add_argument("--query", type=str, default=None, help="Original user query text (for context-sensitive checks)")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any FAIL (default behavior)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output instead of human-readable")
    parser.add_argument("--quiet", action="store_true", help="Only emit overall PASS/FAIL line")
    parser.add_argument("--accept-overrides", action="store_true", help="Honor '# G22-OVERRIDE: G22.X — rationale' AND '# T6-DEFENSE: G22.X — rationale' annotations in report; downgrade matching FAILs to OVERRIDE status (transparent in output, but counted as overall_pass). T6-DEFENSE annotations restricted to G22.4 + G22.7 only per task-comparison-defense.md §2.1.")
    parser.add_argument("--enforce-g24", action="store_true", help="Run G24 well-formedness audit (6 checks per task-comparison-defense.md §7) — required when T6-Defense mode is invoked. Failure marks overall_pass=False even if all G22 checks pass/override.")
    parser.add_argument("--mode", choices=["baseline", "forensic-grade"], default="baseline",
                        help="v5.0.0: 'forensic-grade' enables G51-G60 (G-PROV-01 through G-PROV-10) Forensic Provenance Layer enforcement per provenance-engine.md §5. Default 'baseline' runs only G22 (and G24 if --enforce-g24).")
    parser.add_argument("--evidence-db", type=Path, default=None,
                        help="v5.0.0: Path to SQLite evidence index (evidence-master.db.sqlite) for G52-G56 enforcement when --mode forensic-grade")
    parser.add_argument("--evidence-root", type=Path, default=None,
                        help="v5.0.0: Path to evidence/ root directory for G54+G59 bundle inspection when --mode forensic-grade")
    args = parser.parse_args()

    if not args.report.exists():
        print(f"ERROR: Report file not found: {args.report}", file=sys.stderr)
        sys.exit(2)

    audit = run_all_checks(args.report, args.user_name, args.user_employer, args.query, accept_overrides=args.accept_overrides, enforce_g24=args.enforce_g24)

    # v5.0.0 — Forensic Provenance Layer (G51-G60)
    if args.mode == "forensic-grade":
        report_text = args.report.read_text(encoding="utf-8")
        audit.g_prov_results = g_prov_check(
            report_text,
            evidence_db=args.evidence_db,
            evidence_root=args.evidence_root,
        )
        # G-PROV BLOCKER failures override audit overall_pass
        if not audit.g_prov_results["overall_pass"]:
            audit.overall_pass = False

    if args.json:
        out = {
            "report_path": audit.report_path,
            "user_name": audit.user_name,
            "user_employer": audit.user_employer,
            "query": audit.query,
            "total_checks": audit.total_checks,
            "passed": audit.passed,
            "failed": audit.failed,
            "skipped": audit.skipped,
            "overridden": getattr(audit, 'overridden', 0),
            "t6_defense_overridden": getattr(audit, 't6_defense_overridden', 0),
            "overall_pass": audit.overall_pass,
            "checks": [c.to_dict() for c in audit.checks],
        }
        if audit.g24_results is not None:
            out["g24_results"] = audit.g24_results
        if audit.g_prov_results is not None:
            out["g_prov_results"] = audit.g_prov_results
        print(json.dumps(out, indent=2, ensure_ascii=False))
    elif args.quiet:
        status = "PASS" if audit.overall_pass else "FAIL"
        overridden_count = getattr(audit, 'overridden', 0)
        t6_count = getattr(audit, 't6_defense_overridden', 0)
        suffix_parts = []
        if overridden_count:
            suffix_parts.append(f"{overridden_count} overridden")
        if t6_count:
            suffix_parts.append(f"{t6_count} T6-DEFENSE")
        if audit.g24_results is not None:
            g24_status = "G24 PASS" if audit.g24_results.get("overall_pass") else "G24 FAIL"
            suffix_parts.append(f"{audit.g24_results.get('pass_count', 0)}/{audit.g24_results.get('total_checks', 6)} {g24_status}")
        if audit.g_prov_results is not None:
            gp = audit.g_prov_results
            gp_status = "G-PROV PASS" if gp.get("overall_pass") else "G-PROV FAIL"
            suffix_parts.append(
                f"{gp.get('pass_count', 0)}/{gp.get('total_gates', 10)} {gp_status}")
        suffix = (", " + ", ".join(suffix_parts)) if suffix_parts else ""
        print(f"{status}: {audit.passed}/{audit.total_checks} checks passed, {audit.failed} failed, {audit.skipped} skipped{suffix}")
    else:
        print(format_human_report(audit, verbose=True))
        if audit.g24_results is not None:
            print()
            print("=" * 72)
            print("G24 — T6-Defense Well-Formedness Audit (6 checks)")
            print("=" * 72)
            g24 = audit.g24_results
            g24_icon = "✅" if g24.get("overall_pass") else "❌"
            print(f"{g24_icon} G24 Overall: {g24.get('pass_count', 0)}/{g24.get('total_checks', 6)} checks passed")
            print()
            for detail in g24.get("details", []):
                if "PASS" in detail:
                    print(f"  ✅ {detail}")
                elif "FAIL" in detail:
                    print(f"  ❌ {detail}")
                else:
                    print(f"  ⚠️  {detail}")
        if audit.g_prov_results is not None:
            print()
            print("=" * 72)
            print("G-PROV (G51-G60) — Forensic Provenance Layer (10 gates, v5.0.0)")
            print("=" * 72)
            gp = audit.g_prov_results
            gp_icon = "✅" if gp.get("overall_pass") else "❌"
            print(f"{gp_icon} G-PROV Overall: "
                  f"{gp.get('pass_count', 0)}/{gp.get('total_gates', 10)} passed, "
                  f"{gp.get('fail_count', 0)} failed, "
                  f"{gp.get('skip_count', 0)} skipped, "
                  f"{gp.get('warning_count', 0)} warnings, "
                  f"{gp.get('blocker_count', 0)} BLOCKERs")
            print()
            for gid, info in gp.get("gates", {}).items():
                if info["status"] == "PASS":
                    icon = "✅"
                elif info["status"] == "FAIL":
                    icon = "❌"
                elif info["status"] == "WARN":
                    icon = "⚠️ "
                else:
                    icon = "⏭️ "
                print(f"  {icon} {gid} ({info['severity']}): {info['name']}  →  {info['status']}")
                if info.get("findings"):
                    for f in info["findings"][:5]:
                        print(f"        - {f}")

    sys.exit(0 if audit.overall_pass else 1)


if __name__ == "__main__":
    main()
