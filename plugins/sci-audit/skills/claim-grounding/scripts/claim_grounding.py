#!/usr/bin/env python3
"""Deterministic claim-grounding core (sci-audit axis B).

Stdlib-only. Extracts quantitative/factual claims from text and checks whether
each carries a nearby source marker (citation, DOI/PMID, URL, or repo file
path). An unsourced quantitative claim is a violation — the same contract the
Stop hook enforces at end-of-turn, exposed here for whole-document auditing.

Optional escalation: if `ragas` is installed AND contexts are supplied, a
faithfulness score can be computed by the caller — this module keeps a thin
`ragas_available()` probe and never hard-depends on it (graceful skip).

The LLM claim-matching step (mapping a claim to a specific evidence span) is
performed by the `claim-extractor` and `claim-refuter` Claude subagents, not
here; this module is the deterministic floor.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# A quantitative/factual claim signal (domain-agnostic, scientific).
CLAIM = re.compile(
    r"\b\d+(?:[.,]\d+)?\s?%|\b\d{4}\b|\$\s?\d|"
    r"\b(?:n|N)\s?=\s?\d|\b(?:OR|HR|RR|CI|SD|SE|IQR|p)\b\s?[:=<>]?\s?\d|"
    r"\b\d+(?:[.,]\d+)?\s?(mg|ml|kg|µg|mcg|mmol|nmol|patients|subjects|participants|cases|"
    r"fold|times|percent|hasta|katılımcı|olgu|denek|kat)\b",
    re.IGNORECASE,
)
SOURCE_MARKER = re.compile(
    r"https?://|doi\.org|\bdoi:|arxiv|\bPMID\b|\bPMCID\b|\[\d+\]|\(20\d\d\)|\(19\d\d\)|"
    r"et al\.|\bTable \d|\bFigure \d|\bTablo \d|\bŞekil \d|"
    r"[\w./~-]+\.(?:md|csv|tsv|py|R|qmd|Rmd|bib|ya?ml|json|toml|pdf|docx|tex)\b|"
    r"`[^`]*[/.][^`]*`",
    re.IGNORECASE,
)


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    evidence: str


def ragas_available() -> bool:
    try:
        import ragas  # type: ignore  # noqa: F401
        return True
    except Exception:
        return False


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def audit_text(text: str) -> dict:
    findings: list[Finding] = []
    grounded = 0
    total_claims = 0
    for sentence in split_sentences(text):
        if CLAIM.search(sentence):
            total_claims += 1
            if SOURCE_MARKER.search(sentence):
                grounded += 1
            else:
                findings.append(Finding(
                    "error", "unsourced-claim",
                    "Quantitative/factual claim has no nearby source marker "
                    "(citation, DOI/PMID, URL, table/figure, or file path).",
                    sentence.strip()[:180],
                ))
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return {
        "axis": "B-claim-grounding",
        "counts": counts,
        "claims_total": total_claims,
        "claims_grounded": grounded,
        "grounding_rate": round(grounded / total_claims, 3) if total_claims else None,
        "ragas_available": ragas_available(),
        "findings": [asdict(f) for f in findings],
        "scope_note": (
            "Deterministic grounding floor: presence of a source marker, not "
            "verification that the source supports the claim. Use the "
            "claim-extractor + claim-refuter subagents and MCP resolution for "
            "true evidence matching."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Claim-grounding audit (sci-audit axis B).")
    parser.add_argument("path", type=Path, nargs="?", help="File to audit. Omit to read stdin.")
    parser.add_argument("--fail-on", choices=["error", "warning", "none"], default="error")
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
