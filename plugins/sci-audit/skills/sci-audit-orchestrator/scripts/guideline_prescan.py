#!/usr/bin/env python3
"""Deterministic reporting-guideline section pre-scan (sci-audit axis E, cheap pass).

Stdlib-only, network-free. Before the `guideline-mapper` subagent does the
nuanced item-by-item mapping, this pre-scan cheaply reports which IMRaD /
required sections and structural elements are textually present, so the agent
(and the reader) sees the obvious gaps immediately.

It does NOT judge whether a section is adequate — only whether it appears. A
present heading is not proof of a complete section, and absence via a synonym
the scan missed is possible: this is a trigger, not a verdict.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# Section-name synonyms (EN + TR). A section counts as present if any synonym
# appears as (or within) a heading line, or as a bold lead-in.
SECTIONS = {
    "abstract": [r"abstract", r"özet", r"öz\b"],
    "introduction": [r"introduction", r"background", r"giriş", r"arka plan"],
    "methods": [r"methods?", r"materials?\s+and\s+methods?", r"yöntem", r"gereç\s+ve\s+yöntem", r"metod"],
    "results": [r"results?", r"findings?", r"bulgular?", r"sonuçlar?"],
    "discussion": [r"discussion", r"tartışma"],
    "conclusion": [r"conclusions?", r"sonuç", r"yargı"],
    "limitations": [r"limitations?", r"sınırl[ıi]l[ıi]k", r"kısıtl[ıi]l[ıi]k"],
    "references": [r"references?", r"bibliography", r"kaynak(?:ça|lar)", r"kaynaklar"],
    "funding": [r"funding", r"financial\s+support", r"finansman", r"destek"],
    "conflict_of_interest": [r"conflict\s+of\s+interest", r"competing\s+interests?", r"çıkar\s+çat[ıi]şmas[ıi]"],
    "ethics": [r"ethics?\s+(?:approval|statement|committee)", r"IRB", r"etik\s+(?:kurul|onay)"],
    "data_availability": [r"data\s+availability", r"veri\s+(?:erişilebilirl|payla)"],
    "registration": [r"registration", r"registered", r"PROSPERO", r"ClinicalTrials", r"kay[ıi]t\s+numaras[ıi]"],
}

# Structural elements often required and often faked/absent in LLM drafts.
STRUCTURES = {
    "flow_diagram": [r"flow\s*(?:chart|diagram)", r"PRISMA\s+flow", r"CONSORT\s+flow", r"ak[ıi][şs]\s+(?:diyagram|şema)"],
    "table": [r"\bTable\s+\d", r"\bTablo\s+\d"],
    "figure": [r"\bFig(?:ure)?\.?\s+\d", r"\bŞekil\s+\d"],
    "ai_use_statement": [r"use\s+of\s+(?:generative\s+)?AI", r"AI\s+(?:use|disclosure)\s+statement",
                         r"yapay\s+zek[âa]\s+(?:kullan|beyan)"],
}


@dataclass
class SectionResult:
    name: str
    present: bool
    evidence: str


def _heading_hits(text: str, synonyms: list[str]) -> str:
    for syn in synonyms:
        # As a markdown/numbered heading, a bold lead-in, or an all-caps line.
        pat = (rf"(?:^|\n)\s*(?:#{{1,6}}\s*|\d+[.)]\s*|\*\*)?\s*(?:{syn})\b"
               rf"|\*\*\s*(?:{syn})\b")
        m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(0).strip()[:60]
    return ""


def audit_text(text: str) -> dict:
    sections = []
    for name, syns in SECTIONS.items():
        ev = _heading_hits(text, syns)
        sections.append(SectionResult(name, bool(ev), ev))
    structures = []
    for name, syns in STRUCTURES.items():
        found = ""
        for syn in syns:
            m = re.search(syn, text, re.IGNORECASE)
            if m:
                found = m.group(0).strip()[:60]
                break
        structures.append(SectionResult(name, bool(found), found))

    missing = [s.name for s in sections if not s.present]
    return {
        "axis": "E-guideline-prescan",
        "sections": [asdict(s) for s in sections],
        "structures": [asdict(s) for s in structures],
        "sections_present": [s.name for s in sections if s.present],
        "sections_missing": missing,
        "caveat": (
            "A present heading is not proof of a complete or adequate section; an "
            "absent one may use a synonym this scan missed. This is a trigger for "
            "the guideline-mapper agent, not a conformance verdict."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reporting-guideline section pre-scan (sci-audit axis E).")
    parser.add_argument("path", type=Path, nargs="?", help="File to scan. Omit to read stdin.")
    args = parser.parse_args(argv or sys.argv[1:])
    if args.path:
        if not args.path.exists():
            print(f"File not found: {args.path}", file=sys.stderr)
            return 2
        text = args.path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    print(json.dumps(audit_text(text), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
