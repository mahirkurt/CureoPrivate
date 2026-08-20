#!/usr/bin/env python3
"""evidentia Completeness Gate v2 + hybrid multi-query advisory (context-economy P1/P2).

Events:
  * PreToolUse  — hybrid_query single-query advisory; fulltext collection pass-through
                  advisory; optional soft DENY when EVIDENTIA_COVERAGE_ENFORCE=1 and
                  coverage < floor (include_set empty → never DENY).
  * UserPromptSubmit — /evidentia-synthesize or P6–P7 finalize language → coverage
                       systemMessage listing uncovered IDs (advisory by default).
  * PostToolUse — synthesizer-related hybrid_query / list_docs reminder path is
                  handled by working_set_ledger reconcile; this hook stays quiet.

Default is advisory so CI/hosts without a ledger never hard-break.
Soft DENY only when ``EVIDENTIA_COVERAGE_ENFORCE=1``.
Fail-open. Preserves Anamnesis exclusivity (no Stop forget; no unscoped hybrid).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anamnesis_run import (  # noqa: E402
    ensure_ledger,
    event_name,
    is_anamnesis_tool,
    load_ledger,
    prompt_of,
    tool_base,
    tool_input_of,
)
from working_set_ledger import (  # noqa: E402
    coverage_block,
    load_working_set,
    reconcile_advisory,
    reconcile_anamnesis_ledger,
)

# Fulltext Hub tools that accept collection/doc_id pass-through.
COLLECTION_PASS_TOOLS = {
    "oa_fetch_fulltext",
    "ebsco_get",
}
# annas read_*/download_* — NO collection/doc_id API (gap → ingest_document after).

FINALIZE_RE = re.compile(
    r"(?:/evidentia-synthesize|"
    r"\bP(?:6|7)\b|"
    r"completeness\s*gate|"
    r"finalize|finali[sz]e|"
    r"sentez(?:le|i|ini)?|"
    r"(?:raporu?\s*)?(?:bitir|yaz|tamamla)|"
    r"GRADE\s*(?:SoF|özet|summary)?)",
    re.IGNORECASE,
)

SYNTH_HYBRID_HINT = (
    "[evidentia] hybrid multi-query (P1): sentez için `queries[]` ZORUNLU "
    "(≥2 alt-yön/eşanlamlı). Tek `query` yasak — recall düşer, kaynak atlanır. "
    "Örnek: hybrid_query(collection=evidentia:run:<id>, query=<ana>, "
    "queries=[\"etki boyutu\",\"yan etki\",\"popülasyon\"]). "
    "canonical-cache-contract RECALL kuralı."
)

COLLECTION_HINT = (
    "[evidentia] fulltext collection pass-through (P1): '{base}' çağrısında "
    "`collection=evidentia:run:<run_id>` + `doc_id=evrun:<run_id>:<DOI>` geçir "
    "(OpenAthens/EBSCO Hub auto-ingest). Eksikse mint `openathens:fetch:` / "
    "`marmara:fetch:` olur → koşu scratch'ine düşmez. "
    "Gap: annas `read_article`/`download_document` collection KABUL ETMEZ — "
    "sonra anamnesis.ingest_document(dual-write) zorunlu."
)


def _enforce() -> bool:
    return os.environ.get("EVIDENTIA_COVERAGE_ENFORCE", "").strip() in {
        "1", "true", "TRUE", "yes", "YES",
    }


def _gate_name() -> str:
    return (os.environ.get("EVIDENTIA_COVERAGE_GATE") or "standard").strip().lower()


def _coverage_message(block: dict, *, enforce: bool) -> str:
    unc = block.get("uncovered") or []
    ids = ", ".join(
        (u.get("key") or str(u.get("id") or "?")) for u in unc[:12]
    ) or "(yok)"
    more = f" +{len(unc) - 12}" if len(unc) > 12 else ""
    verb = "DENY" if enforce and not block.get("pass") and block.get("n_include") else "advisory"
    return (
        "[evidentia] Completeness Gate v2 ({verb}): "
        "coverage={cov} floor={floor} (n_include={ni}, n_cited={nc}, "
        "n_skipped_reasoned={ns}, pass={ok}). uncovered[{n}]={ids}{more}. "
        "pass:false → finalize etme — cite / skip_reason / extract. "
        "include_set boşsa yalnız bilgilendirme (hard-break yok). "
        "Env: EVIDENTIA_COVERAGE_ENFORCE=1 soft-DENY."
    ).format(
        verb=verb,
        cov=block.get("coverage"),
        floor=block.get("floor"),
        ni=block.get("n_include"),
        nc=block.get("n_cited"),
        ns=block.get("n_skipped_reasoned"),
        ok=block.get("pass"),
        n=len(unc),
        ids=ids,
        more=more,
    )


def _emit_advisory(msg: str, *, event: str = "PreToolUse") -> None:
    sys.stdout.write(json.dumps({
        "systemMessage": msg,
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": msg,
        },
    }))


def _emit_deny(msg: str) -> None:
    sys.stdout.write(json.dumps({
        "systemMessage": msg,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        },
    }))


def _queries_ok(inp: dict) -> bool:
    qs = inp.get("queries")
    if not isinstance(qs, list):
        return False
    return len([q for q in qs if str(q or "").strip()]) >= 2


def handle_pretool(data: dict) -> int:
    tool = str(data.get("tool_name", ""))
    if not tool.startswith("mcp__"):
        return 0
    base = tool_base(tool)
    inp = tool_input_of(data)
    msgs: list[str] = []

    # --- multi-query hybrid (synthesis contract) ---
    if is_anamnesis_tool(tool) and base == "hybrid_query":
        if not _queries_ok(inp):
            msgs.append(SYNTH_HYBRID_HINT)

    # --- collection/doc_id pass-through on Hub fulltext ---
    if base in COLLECTION_PASS_TOOLS:
        coll = str(inp.get("collection") or "").strip()
        doc = str(inp.get("doc_id") or inp.get("docId") or "").strip()
        if not coll or not doc:
            msgs.append(COLLECTION_HINT.format(base=base))

    # --- coverage soft-DENY / advisory before hybrid synthesis ---
    if is_anamnesis_tool(tool) and base == "hybrid_query":
        try:
            led = load_ledger() or ensure_ledger()
            ws = load_working_set(led["run_id"])
            # Reconcile against Anamnesis doc_id ledger (proxy when list_docs not fresh).
            report = reconcile_anamnesis_ledger(
                ws, list(led.get("doc_ids") or []), run_id=led["run_id"], phase="P6",
            )
            if report.get("changed"):
                from working_set_ledger import save_working_set
                save_working_set(ws)
            if report.get("missing_extractions") or report.get("orphans"):
                msgs.append(reconcile_advisory(report, ws))
            block = coverage_block(ws, gate=_gate_name())
            if block["n_include"] == 0:
                # Empty include_set → advisory only (never DENY).
                pass
            elif not block["pass"]:
                msg = _coverage_message(block, enforce=_enforce())
                if _enforce():
                    _emit_deny(msg)
                    return 0
                msgs.append(msg)
        except Exception:
            pass

    if msgs:
        _emit_advisory("\n".join(msgs), event="PreToolUse")
    return 0


def handle_user_prompt(data: dict) -> int:
    prompt = prompt_of(data)
    if not prompt or not FINALIZE_RE.search(prompt):
        return 0
    try:
        led = load_ledger() or ensure_ledger()
        ws = load_working_set(led["run_id"])
        report = reconcile_anamnesis_ledger(
            ws, list(led.get("doc_ids") or []), run_id=led["run_id"], phase="P6",
        )
        if report.get("changed"):
            from working_set_ledger import save_working_set
            save_working_set(ws)
        block = coverage_block(ws, gate=_gate_name())
        parts = []
        if report.get("missing_extractions") or report.get("orphans"):
            parts.append(reconcile_advisory(report, ws))
        # include_set empty → advisory-only note (no hard-break).
        if block["n_include"] == 0:
            parts.append(
                "[evidentia] Completeness Gate v2 (advisory): include_set=0 — "
                "ledger'da henüz included/extracted/cited/skipped yok; coverage "
                "hesabı bilgilendirme. Finalize engellenmez."
            )
        else:
            parts.append(_coverage_message(block, enforce=_enforce()))
            if _enforce() and not block["pass"]:
                # UserPromptSubmit: surface as systemMessage + additionalContext;
                # hosts without deny support still see the block. Soft DENY is
                # enforced on the next hybrid_query PreToolUse path above.
                parts.append(
                    "[evidentia] EVIDENTIA_COVERAGE_ENFORCE=1 — coverage floor "
                    "altında; hybrid_query / finalize soft-DENY aktif."
                )
        _emit_advisory("\n".join(parts), event="UserPromptSubmit")
    except Exception:
        return 0
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    # Disable flag mirrors the tool guard.
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj and os.path.isfile(os.path.join(proj, ".claude", "evidentia-guard.off")):
        return 0

    ev = event_name(data).lower().replace("_", "")
    try:
        if ev in {"userpromptsubmit"}:
            return handle_user_prompt(data)
        # PreToolUse (default when event absent — Claude often omits on matcher hooks)
        if ev in {"", "pretooluse"} or data.get("tool_name"):
            return handle_pretool(data)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
