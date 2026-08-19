#!/usr/bin/env python3
"""historia-medicinae Anamnesis lifecycle — mint exclusive collection, forget own only.

  SessionStart  startup|clear  → forget leftover, mint new
  SessionStart  resume|compact → keep collection (canonical cache across modes)
  UserPromptSubmit             → `/historia-medicinae` / `:start` remints after forget
  SessionEnd                   → forget_collection (fallback ledger ids)

Does NOT forget on Stop (G0/anachronism checkpoints end a turn, not the run).
Fail-open.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anamnesis_run import (  # noqa: E402
    context_message,
    ensure_ledger,
    event_name,
    is_new_run,
    prompt_of,
    rotate_run,
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
            from anamnesis_run import forget_run_docs
            forget_run_docs()
            return 0
        if ev in {"userpromptsubmit"}:
            if not is_new_run(prompt_of(data)):
                return 0
            led = rotate_run(forget_previous=True)
            emit("UserPromptSubmit", context_message(led))
            return 0
        if src in {"startup", "clear"}:
            led = rotate_run(forget_previous=True)
        else:
            led = ensure_ledger()
        emit("SessionStart", context_message(led))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
