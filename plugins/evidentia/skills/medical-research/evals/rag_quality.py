#!/usr/bin/env python3
"""
rag_quality.py — RAG-quality evaluation harness (EKLENTI-GELISTIRME-GENEL-TALIMATI §7.2.1).

Closes evidentia's MEASURED-accuracy gap: check_integrity.py gates are STRUCTURAL ("do files
resolve / is the map consistent"); this harness scores the *output* — does the synthesis stay
FAITHFUL to the retrieved evidence (no fabricated/uncited claims), per the no-fabrication
invariant + the Vancouver claim-level-grounding convention (report-presentation.md).

Two layers (code-first + local, §7.1.1):

  1. STRUCTURAL faithfulness (deterministic, stdlib-only, no API — the CI floor). Per item:
       C1 citations_resolve   every body [n] has a numbered sources entry
       C2 sources_have_ids    every sources entry carries a stable id (PMID/NCT/DOI)
       C3 ids_grounded        every cited id appears in the retrieved evidence (no fabrication)
       C4 no_vague_citation   no forbidden vague attribution ("bir çalışmaya göre" / "literatürde"
                              / "according to a study") — convention forbids these
       C5 quant_claims_cited  every quantitative claim sentence (%, mg, /kg, $, QALY, oran) carries [n]
     faithful_pred = C1∧C2∧C3∧C4∧C5.
     The gold set (rag-eval-set.jsonl) carries `expected.faithful`, including planted NEGATIVE
     controls (fabricated citation / vague / uncited number). The gate is SELF-VALIDATING: it
     PASSES iff the detector classifies every gold item correctly (predicted == expected). This
     proves the no-fabrication detector actually catches the failure modes it claims to.

  2. SEMANTIC faithfulness via LLM-judge (optional, --judge). When EVIDENTIA_JUDGE_KEY is set,
     an OpenAI-compatible endpoint scores faithfulness / answer_relevance / context_relevance
     (0..1) against a rubric (§7.2.1 RAG eval + §7.2.1 LLM-as-judge). Honest skip if no key —
     never fabricates a judge score.

Exit: 0 = gate passed; 1 = a blocking check failed; 2 = setup error.
CI usage:  python rag_quality.py                 # structural floor (no API)
           python rag_quality.py --judge          # + LLM-judge (needs EVIDENTIA_JUDGE_KEY)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

EVAL_SET = Path(__file__).resolve().parent / "rag-eval-set.jsonl"

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"

VAGUE = [
    "bir çalışmaya göre", "bir araştırmaya göre", "literatürde belirtildiği",
    "literatürde", "araştırmalar gösteriyor", "according to a study", "studies show",
]
QUANT_CUE = re.compile(r"(\d+\s?%|%\s?\d+|yüzde\s?\d+|\$\s?\d|\bmg\b|/kg|QALY|\bdolar\b|oran[ıi]\b)", re.IGNORECASE)
CITE = re.compile(r"\[(\d+)\]")
# stable identifiers: PMID, ClinicalTrials NCT, DOI (10.x/...)
ID_PATTERNS = [
    re.compile(r"PMID:?\s*(\d+)", re.IGNORECASE),
    re.compile(r"(NCT\d{8})", re.IGNORECASE),
    re.compile(r"(10\.\d{4,9}/[^\s\]]+)"),
]


def canon_ids(text: str) -> set[str]:
    out: set[str] = set()
    for pat in ID_PATTERNS:
        for m in pat.findall(text or ""):
            out.add(m.lower().rstrip(".,;)"))
    return out


def split_body_sources(synthesis: str) -> tuple[str, dict[int, str]]:
    """Split a synthesis into (body, {n: source_line}) on the Kaynaklar/Sources header."""
    parts = re.split(r"\n\s*(?:Kaynaklar|Sources|References)\s*:\s*\n", synthesis, maxsplit=1, flags=re.IGNORECASE)
    body = parts[0]
    sources: dict[int, str] = {}
    if len(parts) > 1:
        for line in parts[1].splitlines():
            m = re.match(r"\s*(\d+)[.)]\s*(.+)", line)
            if m:
                sources[int(m.group(1))] = m.group(2).strip()
    return body, sources


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def structural_faithfulness(item: dict) -> dict:
    body, sources = split_body_sources(item["synthesis"])
    evidence_ids = set()
    for e in item.get("evidence", []):
        evidence_ids |= canon_ids(e.get("ref", "")) | canon_ids(e.get("text", ""))

    body_cites = {int(n) for n in CITE.findall(body)}

    # C1 citations resolve
    c1 = all(n in sources for n in body_cites)
    c1_bad = sorted(n for n in body_cites if n not in sources)

    # C2 sources have stable ids
    c2 = all(canon_ids(v) for v in sources.values()) if sources else (not body_cites)
    c2_bad = sorted(n for n, v in sources.items() if not canon_ids(v))

    # C3 every CITED source id appears in the evidence (no fabrication)
    cited_ids: set[str] = set()
    for n in body_cites:
        cited_ids |= canon_ids(sources.get(n, ""))
    c3_bad = sorted(i for i in cited_ids if i not in evidence_ids)
    c3 = not c3_bad

    # C4 no vague attribution
    low = body.lower()
    c4_bad = [v for v in VAGUE if v in low]
    c4 = not c4_bad

    # C5 quantitative claim sentences carry a citation
    c5_bad = [s[:80] for s in sentences(body) if QUANT_CUE.search(s) and not CITE.search(s)]
    c5 = not c5_bad

    checks = {"C1_cites_resolve": c1, "C2_sources_have_ids": c2, "C3_ids_grounded": c3,
              "C4_no_vague": c4, "C5_quant_cited": c5}
    faithful = all(checks.values())
    fails = []
    if not c1: fails.append(f"C1 unresolved body cites {c1_bad}")
    if not c2: fails.append(f"C2 sources w/o id {c2_bad}")
    if not c3: fails.append(f"C3 fabricated/ungrounded ids {c3_bad}")
    if not c4: fails.append(f"C4 vague attribution {c4_bad}")
    if not c5: fails.append(f"C5 uncited quantitative claim(s) {c5_bad}")
    score = sum(checks.values()) / len(checks)
    return {"faithful": faithful, "score": round(score, 3), "checks": checks, "fails": fails}


# --------------------------------------------------------------------------- LLM judge (optional)
JUDGE_RUBRIC = (
    "You are a strict RAG faithfulness judge. Given a QUERY, the retrieved EVIDENCE, and a "
    "SYNTHESIS answer, score 0.0-1.0:\n"
    "- faithfulness: every substantive claim in SYNTHESIS is supported by EVIDENCE (penalize "
    "any claim/number not grounded in EVIDENCE, and any cited source absent from EVIDENCE).\n"
    "- answer_relevance: SYNTHESIS addresses QUERY.\n"
    "- context_relevance: EVIDENCE is relevant to QUERY.\n"
    'Reply ONLY with compact JSON: {"faithfulness":x,"answer_relevance":x,"context_relevance":x}'
)


def llm_judge(item: dict) -> dict | None:
    key = os.environ.get("EVIDENTIA_JUDGE_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    base = os.environ.get("EVIDENTIA_JUDGE_BASE", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("EVIDENTIA_JUDGE_MODEL", "gpt-4o-mini")
    ev = "\n".join(f"- [{e.get('ref','')}] {e.get('text','')}" for e in item.get("evidence", []))
    user = f"QUERY:\n{item['query']}\n\nEVIDENCE:\n{ev}\n\nSYNTHESIS:\n{item['synthesis']}"
    payload = json.dumps({
        "model": model, "temperature": 0,
        "messages": [{"role": "system", "content": JUDGE_RUBRIC}, {"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(f"{base}/chat/completions", data=payload, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "User-Agent": "evidentia-rag-eval/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        content = data["choices"][0]["message"]["content"]
        m = re.search(r"\{.*\}", content, re.DOTALL)
        return json.loads(m.group(0)) if m else None
    except Exception as e:  # honest: judge unavailable, never fabricate a score
        return {"_error": str(e)[:120]}


# --------------------------------------------------------------------------- runner
def main() -> int:
    ap = argparse.ArgumentParser(description="evidentia RAG-quality eval (§7.2.1)")
    ap.add_argument("--judge", action="store_true", help="also run the LLM-judge (needs EVIDENTIA_JUDGE_KEY)")
    ap.add_argument("--threshold", type=float, default=0.80, help="min mean judge faithfulness (judge mode)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON summary")
    args = ap.parse_args()

    if not EVAL_SET.exists():
        print(f"{RED}SETUP ERROR{RESET}: {EVAL_SET} missing")
        return 2
    items = [json.loads(l) for l in EVAL_SET.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not items:
        print(f"{RED}SETUP ERROR{RESET}: eval set empty")
        return 2

    print("G-RAG  RAG-quality eval (§7.2.1) — structural faithfulness floor\n")
    mismatches, pos_scores, results = [], [], []
    for it in items:
        s = structural_faithfulness(it)
        exp = bool(it.get("expected", {}).get("faithful", True))
        ok = s["faithful"] == exp
        if not ok:
            mismatches.append(it["id"])
        if exp:
            pos_scores.append(s["score"])
        mark = f"{GREEN}OK  {RESET}" if ok else f"{RED}MISS{RESET}"
        verdict = "faithful" if s["faithful"] else "UNFAITHFUL"
        print(f"  {mark} {it['id']:28s} pred={verdict:10s} expect={'faithful' if exp else 'UNFAITHFUL':10s}"
              + ("" if ok else f"  {YELLOW}<- detector misclassified{RESET}"))
        if s["fails"]:
            for f in s["fails"]:
                print(f"          · {f}")
        results.append({"id": it["id"], "structural": s, "expected_faithful": exp, "match": ok})

    pos_rate = sum(pos_scores) / len(pos_scores) if pos_scores else 0.0
    classify_ok = not mismatches
    print(f"\n  positives mean structural-faithfulness: {pos_rate:.3f}")
    print(f"  self-validation (detector matches planted controls): "
          f"{GREEN}PASS{RESET}" if classify_ok else f"{RED}FAIL ({mismatches}){RESET}")

    judge_ok = True
    judge_summary = None
    if args.judge:
        print("\nG-RAG  LLM-judge (semantic faithfulness / relevance)")
        jf = []
        ran = False
        for it in items:
            j = llm_judge(it)
            if j is None:
                print(f"  {YELLOW}SKIP{RESET} no EVIDENTIA_JUDGE_KEY — judge layer not run (honest skip)")
                break
            if "_error" in j:
                print(f"  {YELLOW}WARN{RESET} {it['id']}: judge error {j['_error']}")
                continue
            ran = True
            exp = bool(it.get("expected", {}).get("faithful", True))
            f = float(j.get("faithfulness", 0))
            if exp:
                jf.append(f)
            print(f"  {it['id']:28s} faithfulness={f:.2f} answer_rel={float(j.get('answer_relevance',0)):.2f} "
                  f"context_rel={float(j.get('context_relevance',0)):.2f}")
        if ran and jf:
            mean_jf = sum(jf) / len(jf)
            judge_ok = mean_jf >= args.threshold
            judge_summary = round(mean_jf, 3)
            print(f"  positives mean judge-faithfulness: {mean_jf:.3f} (threshold {args.threshold}) "
                  + (f"{GREEN}PASS{RESET}" if judge_ok else f"{RED}FAIL{RESET}"))

    passed = classify_ok and judge_ok
    if args.json:
        print(json.dumps({"classify_ok": classify_ok, "positives_structural_rate": round(pos_rate, 3),
                          "judge_faithfulness": judge_summary, "mismatches": mismatches,
                          "results": results}, ensure_ascii=False))
    print()
    if passed:
        print(f"{GREEN}G-RAG PASSED{RESET}")
        return 0
    print(f"{RED}G-RAG FAILED{RESET} — faithfulness detector or judge below threshold")
    return 1


if __name__ == "__main__":
    sys.exit(main())
