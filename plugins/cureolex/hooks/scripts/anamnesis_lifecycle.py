#!/usr/bin/env python3
"""cureolex Anamnesis lifecycle — mint sess collection and forget it.

Events:
  SessionStart  startup|clear  → forget leftover (crash residue), mint new sess
  SessionStart  resume|compact → keep sess (G0–G11 canonical cache)
  UserPromptSubmit /lex-*      → keep sess, re-inject collection (no remint)
  SessionEnd                   → forget this sess collection

Does NOT forget on Stop: G0–G11 gates and human review end a turn, not the
legal-research thread. Mid-pipeline wipe would drop the canonical cache.

Cleanup: forget_collection if the Worker has it, else N× forget_document from
the ledger (stubbed in tests via CUREOLEX_ANAMNESIS_FORGET_LOG). Unprefixed
ids are never sent. Fail-open.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anamnesis_run import (
    context_message,
    ensure_ledger,
    event_name,
    is_lex_work_command,
    prompt_of,
    rotate_session,
    session_source,
)


def emit(event: str, ctx: str) -> None:
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": ctx,
        }
    }))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    ev = event_name(data).lower().replace("_", "")
    src = session_source(data)

    try:
        if ev in {"sessionend"}:
            from anamnesis_run import forget_session_docs
            forget_session_docs()
            return 0

        if ev in {"userpromptsubmit"}:
            if not is_lex_work_command(prompt_of(data)):
                return 0
            led = ensure_ledger()
            emit("UserPromptSubmit", context_message(led))
            return 0

        # Compact/resume MUST keep the working set (G0–G11 live across compact).
        # Missing `source` is treated as keep — wiping on an unidentified
        # SessionStart would drop the canonical cache.
        if src in {"startup", "clear"}:
            led = rotate_session(forget_previous=True)
        else:
            led = ensure_ledger()
        emit("SessionStart", context_message(led))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
