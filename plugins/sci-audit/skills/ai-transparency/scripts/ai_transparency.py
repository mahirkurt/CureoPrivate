#!/usr/bin/env python3
"""Deterministic AI-use transparency scan (sci-audit axis F).

Stdlib-only, network-free. Checks whether an LLM-generated scientific text
carries the AI-use disclosure that ICMJE / COPE / WAME and most publishers now
require, and flags signals of UNDISCLOSED AI assistance.

It cannot prove a text was or was not AI-assisted; it detects the presence /
absence of a disclosure statement and surfaces textual signals that warrant a
disclosure. The verdict is a prompt for the author, not an accusation.
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


# A present AI-use disclosure statement (EN + TR). Requires an AI term AND a
# use/assist verb nearby so a passing mention of "AI" in the content does not
# count as a disclosure.
AI_TERMS = (
    r"(?:generative\s+AI|artificial\s+intelligence|large\s+language\s+model|LLM|"
    r"ChatGPT|GPT-?\d|Claude|Gemini|Copilot|AI\s+(?:tool|chatbot|assistant|language\s+model)|"
    r"yapay\s+zek[âa]|üretken\s+yapay\s+zek[âa]|büyük\s+dil\s+model)"
)
USE_VERBS = (
    r"(?:was|were)\s+used|used\s+to|assisted|employed|utili[sz]ed|generated|"
    r"kullan[ıi]l|yararlan[ıi]l|destek\s+al[ıi]n|ile\s+üretil"
)
DISCLOSURE = re.compile(
    rf"{AI_TERMS}[^.\n]{{0,80}}?(?:{USE_VERBS})|"
    rf"(?:{USE_VERBS})[^.\n]{{0,40}}?{AI_TERMS}",
    re.IGNORECASE,
)
# A disclosure-section header that names AI use.
DISCLOSURE_SECTION = re.compile(
    r"(?:AI\s+(?:use|usage|disclosure|statement)|use\s+of\s+(?:AI|generative\s+AI|LLMs?)|"
    r"declaration\s+of\s+(?:generative\s+)?AI|yapay\s+zek[âa]\s+(?:kullan[ıi]m[ıi]|beyan))",
    re.IGNORECASE,
)
# Explicit "no AI was used" negative disclosure (also a valid statement).
NEGATIVE_DISCLOSURE = re.compile(
    r"no\s+(?:generative\s+)?AI[^.\n]{0,40}?(?:was|were)\s+used|"
    r"(?:did\s+not|didn't)\s+use[^.\n]{0,30}?(?:AI|LLM)|"
    r"yapay\s+zek[âa][^.\n]{0,30}?kullan[ıi]lma",
    re.IGNORECASE,
)

# Undisclosed-AI signals: giveaway boilerplate phrases LLMs emit.
UNDISCLOSED_SIGNALS = {
    r"\bas an AI language model\b": "Verbatim LLM boilerplate left in the text.",
    r"\bI (?:cannot|can't) (?:provide|browse|access)\b": "First-person LLM refusal boilerplate left in the text.",
    r"\bknowledge cutoff\b": "LLM 'knowledge cutoff' phrasing left in the text.",
    r"\bmy training data\b": "LLM self-reference left in the text.",
    r"\bcertainly!\s+here'?s\b": "LLM chat-preamble left in the text.",
    r"\bregenerate response\b": "LLM UI artefact left in the text.",
    r"\byapay zek[âa] (?:dil )?modeli olarak\b": "LLM Türkçe boilerplate metinde kalmış.",
}
# Placeholder / hallucinated-fill signals.
PLACEHOLDER_SIGNALS = {
    r"\[(?:insert|add|citation needed|ref|TODO|XX+)\b[^\]]*\]": "Unfilled placeholder left in the text.",
    r"\bLorem ipsum\b": "Lorem ipsum filler left in the text.",
}


def _find(text: str, patterns: dict, code: str, severity: str) -> list[Finding]:
    out: list[Finding] = []
    for pat, msg in patterns.items():
        for m in re.finditer(pat, text, re.IGNORECASE):
            out.append(Finding(severity, code, msg, m.group(0).strip()[:120]))
    return out


def audit_text(text: str, require_disclosure: bool = True) -> dict:
    findings: list[Finding] = []

    findings += _find(text, UNDISCLOSED_SIGNALS, "undisclosed-ai-signal", "warning")
    findings += _find(text, PLACEHOLDER_SIGNALS, "unfilled-placeholder", "warning")
    signals_present = any(f.code == "undisclosed-ai-signal" for f in findings)

    # Giveaway boilerplate must NOT count as a genuine disclosure. Blank those
    # spans before detecting an author's AI-use statement.
    cleaned = text
    for pat in UNDISCLOSED_SIGNALS:
        cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE)
    has_disclosure = bool(
        DISCLOSURE.search(cleaned) or DISCLOSURE_SECTION.search(cleaned) or NEGATIVE_DISCLOSURE.search(cleaned)
    )

    if not has_disclosure:
        # Missing disclosure is a major when the text carries AI giveaway signals;
        # otherwise it is a minor prompt (the text may simply be human-written).
        sev = "error" if signals_present else ("warning" if require_disclosure else "info")
        findings.append(Finding(
            sev, "missing-ai-disclosure",
            ("No AI-use disclosure statement was found. ICMJE/COPE/WAME and most "
             "publishers require authors to disclose whether and how generative AI "
             "was used (or state that none was). Add an explicit statement."
             + (" The text also contains LLM giveaway phrasing (see signals above)."
                if signals_present else "")),
            "(document-level: no AI-use statement detected)",
        ))
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return {
        "axis": "F-ai-transparency",
        "counts": counts,
        "disclosure_present": has_disclosure,
        "findings": [asdict(f) for f in findings],
        "caveat": (
            "Detects the PRESENCE/ABSENCE of an AI-use disclosure and LLM giveaway "
            "signals — it cannot prove a text was or was not AI-assisted. Absence of "
            "signals is not proof of no AI use; presence of a disclosure is not "
            "verification of its accuracy."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI-use transparency scan (sci-audit axis F).")
    parser.add_argument("path", type=Path, nargs="?", help="File to audit. Omit to read stdin.")
    parser.add_argument("--no-require-disclosure", action="store_true",
                        help="Treat a missing disclosure as info, not a warning (e.g. informal drafts).")
    parser.add_argument("--fail-on", choices=["error", "warning", "none"], default="none")
    args = parser.parse_args(argv or sys.argv[1:])

    if args.path:
        if not args.path.exists():
            print(f"File not found: {args.path}", file=sys.stderr)
            return 2
        text = args.path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    result = audit_text(text, require_disclosure=not args.no_require_disclosure)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    counts = result["counts"]
    if args.fail_on == "error" and counts["error"]:
        return 1
    if args.fail_on == "warning" and (counts["warning"] or counts["error"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
