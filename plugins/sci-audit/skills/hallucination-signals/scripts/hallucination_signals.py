#!/usr/bin/env python3
"""Deterministic hallucination-signal detector (sci-audit axis D).

Stdlib-only, network-free. Surfaces textual signals that CORRELATE with LLM
confabulation; it does not decide truth. Signals:

  * Over-certainty / hedge-free absolutes on empirical claims
    ("proves", "definitively", "it is certain that", "kesin olarak kanıtlar").
  * Universal quantifiers on empirical claims ("all studies show", "no study
    has ever", "her zaman", "hiçbir çalışma").
  * Suspicious citation/identifier shapes that look fabricated: DOIs/PMIDs that
    are structurally malformed, "et al. (in press)" with no venue, round-number
    statistics with no source.
  * Method/tool-name shapes that are commonly confabulated (invented acronyms
    presented as established named methods without a citation).

The heavy consistency signal (semantic entropy) is in semantic_entropy.py and
needs a sampler+NLI backend (a Claude subagent in-plugin, or a CI backend).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    evidence: str


OVERCERTAINTY = {
    r"\b(?:this|these results?|the data|our findings?)\s+(?:prove[sd]?|definitively\s+show)": "Over-certainty: empirical data rarely 'proves'; prefer 'suggests/indicates/supports'.",
    r"\b(?:it is|this is)\s+(?:certain|undeniable|indisputable|beyond doubt)\b": "Over-certainty absolute; scientific claims carry uncertainty.",
    r"\b(?:kesin olarak|kesinlikle)\s+kanıtla": "Aşırı-kesinlik: 'kanıtlamak' yerine 'göstermektedir/desteklemektedir'.",
    r"\b(?:hiçbir kuşku|tartışmasız|kesin olarak doğru)\b": "Aşırı-kesinlik ifadesi; bilimsel iddia belirsizlik taşır.",
    r"\b100%\s+(?:accurate|certain|effective|reliable)\b": "Absolute 100% claim; verify or qualify.",
}

UNIVERSAL_QUANTIFIER = {
    r"\ball\s+(?:studies|research|experts|scientists)\s+(?:show|agree|confirm)": "Universal quantifier on empirical consensus; almost always an overclaim.",
    r"\bno\s+study\s+has\s+(?:ever\s+)?(?:shown|found|reported)": "Universal negative; hard to substantiate — verify or soften.",
    r"\b(?:her zaman|tüm çalışmalar|bütün araştırmalar)\s+\w+": "Evrensel niceleyici; genelleme aşımı olabilir.",
    r"\bhiçbir çalışma\b": "Evrensel olumsuz iddia; kanıtlanması güç — doğrula veya yumuşat.",
}

# Structurally malformed identifiers — a fabricated-citation smell.
MALFORMED_DOI = re.compile(r"\bdoi:\s*(?!10\.\d{4,9}/)\S+", re.IGNORECASE)
MALFORMED_PMID = re.compile(r"\bPMID:?\s*(\d{9,})\b", re.IGNORECASE)  # PMIDs are <= 8 digits today
INPRESS_NOVENUE = re.compile(r"\((?:in press|baskıda)\)", re.IGNORECASE)

# An ALL-CAPS acronym introduced as a named method/algorithm/framework with no
# adjacent citation marker is a common confabulation shape.
NAMED_METHOD = re.compile(
    r"\b(?:using|via|with|the)\s+(?P<name>[A-Z][A-Za-z]*(?:-[A-Z][A-Za-z]*)?)\s+"
    r"(?:algorithm|method|framework|technique|model|test|procedure)\b"
)
CITATION_NEARBY = re.compile(r"\[\d+\]|\(20\d\d\)|\(19\d\d\)|doi|PMID|et al", re.IGNORECASE)


def _add(findings: list[Finding], text: str, patterns: dict, code: str, severity: str) -> None:
    for pattern, message in patterns.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            findings.append(Finding(severity, code, message, m.group(0).strip()[:140]))


# --- Checksum / format validation for structured identifiers ---------------
# These are deterministic, offline validity checks. A checksum failure means the
# identifier is impossible (very likely fabricated); it is NOT existence proof —
# a valid checksum still needs axis-A resolution against a real source.

ISBN13 = re.compile(r"\bISBN(?:-13)?[:\s]*((?:97[89][-\s]?)(?:\d[-\s]?){9}\d)\b", re.IGNORECASE)
ISBN10 = re.compile(r"\bISBN(?:-10)?[:\s]*((?:\d[-\s]?){9}[\dXx])\b", re.IGNORECASE)
ORCID = re.compile(r"\b(?:ORCID[:\s]*)?(\d{4}-\d{4}-\d{4}-\d{3}[\dXx])\b")
ARXIV_NEW = re.compile(r"\barXiv[:\s]*(\d{4})\.(\d{4,5})(v\d+)?\b", re.IGNORECASE)
ARXIV_OLD = re.compile(r"\barXiv[:\s]*([a-z-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?\b", re.IGNORECASE)


def _isbn13_ok(digits: str) -> bool:
    d = [int(c) for c in digits]
    if len(d) != 13:
        return False
    s = sum(d[i] * (1 if i % 2 == 0 else 3) for i in range(12))
    return (10 - s % 10) % 10 == d[12]


def _isbn10_ok(chars: str) -> bool:
    if len(chars) != 10:
        return False
    s = 0
    for i, c in enumerate(chars):
        v = 10 if c in "Xx" and i == 9 else (int(c) if c.isdigit() else -1)
        if v < 0:
            return False
        s += v * (10 - i)
    return s % 11 == 0


def _orcid_ok(orcid: str) -> bool:
    body = orcid.replace("-", "")
    if len(body) != 16:
        return False
    total = 0
    for c in body[:15]:
        if not c.isdigit():
            return False
        total = (total + int(c)) * 2
    check = (12 - total % 11) % 11
    expected = "X" if check == 10 else str(check)
    return body[15].upper() == expected


def check_identifiers(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in ISBN13.finditer(text):
        digits = re.sub(r"[-\s]", "", m.group(1))
        if not _isbn13_ok(digits):
            findings.append(Finding("error", "invalid-isbn13",
                                    "ISBN-13 checksum fails; the identifier is impossible (likely fabricated).",
                                    m.group(0).strip()[:60]))
    for m in ISBN10.finditer(text):
        chars = re.sub(r"[-\s]", "", m.group(1))
        # skip if it was actually the tail of an ISBN-13 (already handled)
        if len(chars) == 10 and not _isbn10_ok(chars):
            findings.append(Finding("error", "invalid-isbn10",
                                    "ISBN-10 checksum fails; the identifier is impossible (likely fabricated).",
                                    m.group(0).strip()[:60]))
    for m in ORCID.finditer(text):
        if not _orcid_ok(m.group(1)):
            findings.append(Finding("error", "invalid-orcid",
                                    "ORCID checksum (ISO 7064 MOD 11-2) fails; impossible identifier.",
                                    m.group(0).strip()[:60]))
    for m in ARXIV_NEW.finditer(text):
        yy, mm = int(m.group(1)[:2]), int(m.group(1)[2:])
        if not (1 <= mm <= 12):
            findings.append(Finding("warning", "malformed-arxiv-id",
                                    "arXiv id month is out of range (YYMM.NNNNN); verify it.",
                                    m.group(0).strip()[:60]))
    return findings


def audit_text(text: str) -> dict:
    findings: list[Finding] = []
    _add(findings, text, OVERCERTAINTY, "over-certainty", "warning")
    _add(findings, text, UNIVERSAL_QUANTIFIER, "universal-quantifier", "warning")
    findings += check_identifiers(text)

    for m in MALFORMED_DOI.finditer(text):
        findings.append(Finding("error", "malformed-doi",
                                "DOI does not match the 10.NNNN/... structure; verify it exists.",
                                m.group(0).strip()[:140]))
    for m in MALFORMED_PMID.finditer(text):
        findings.append(Finding("warning", "suspicious-pmid",
                                "PMID has 9+ digits (current PMIDs are <= 8); verify it exists.",
                                m.group(0).strip()[:140]))
    for m in INPRESS_NOVENUE.finditer(text):
        # Flag only when there is no venue/journal word in the same sentence.
        start = text.rfind(".", 0, m.start()) + 1
        end = text.find(".", m.end())
        sentence = text[start: end if end != -1 else len(text)]
        if not re.search(r"journal|dergi|proceedings|conference|press\s+of|university", sentence, re.IGNORECASE):
            findings.append(Finding("info", "in-press-no-venue",
                                    "'in press' with no venue named; confirm the source is real.",
                                    m.group(0).strip()))

    for m in NAMED_METHOD.finditer(text):
        window = text[max(0, m.start() - 40): m.end() + 40]
        if not CITATION_NEARBY.search(window):
            findings.append(Finding("info", "uncited-named-method",
                                    f"Named method '{m.group('name')}' has no nearby citation; "
                                    "confirm it is an established method, not a confabulation.",
                                    m.group(0).strip()[:140]))

    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return {
        "axis": "D-hallucination-signals",
        "counts": counts,
        "findings": [asdict(f) for f in findings],
        "scope_note": (
            "Textual signals correlated with confabulation; NOT a truth verdict. "
            "For a consistency-based signal, run semantic_entropy.py with a "
            "sampler+NLI backend (a Claude subagent in-plugin)."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hallucination-signal audit (sci-audit axis D).")
    parser.add_argument("path", type=Path, nargs="?", help="File to audit. Omit to read stdin.")
    parser.add_argument("--fail-on", choices=["error", "warning", "none"], default="none")
    args = parser.parse_args(argv or sys.argv[1:])

    if args.path:
        if not args.path.exists():
            print(f"File not found: {args.path}", file=sys.stderr)
            return 2
        text = args.path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    result = audit_text(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    counts = result["counts"]
    if args.fail_on == "error" and counts["error"]:
        return 1
    if args.fail_on == "warning" and (counts["warning"] or counts["error"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
