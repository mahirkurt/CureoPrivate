#!/usr/bin/env python3
"""evidentia Anamnesis lifecycle hook — mint exclusive run scope and forget it.

Events (Claude plugin names; Cursor hosts that fire the same hooks.json keys):
  SessionStart  startup|clear  → forget leftover from a crashed prior run, mint new
  SessionStart  resume|compact → keep the run; re-inject the prefix (compact amnesia)
  UserPromptSubmit             → new `/evidentia` / `/evidentia-synthesize` remints
                                 after forgetting the previous working set
  SessionEnd                   → forget this run's doc_ids (success, abort, close)

Does NOT forget on Stop: P3/P5 human-approval checkpoints end a turn but not
the run. Mid-run wipe would recreate the empty-corpus failure.

Cleanup prefers forget_collection (stubbed in tests via EVIDENTIA_ANAMNESIS_FORGET_LOG),
falling back to ledger forget_document. Unprefixed ids are never sent. No Stop-hook forget.
Fail-open: I/O or parse errors exit 0.
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
    is_new_evidentia_run,
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
            if not is_new_evidentia_run(prompt_of(data)):
                return 0
            led = rotate_run(forget_previous=True)
            emit("UserPromptSubmit", context_message(led))
            return 0

        # Compact/resume MUST keep the working set (P3/P5 checkpoints live
        # across compact). Missing `source` is treated as keep — wiping on an
        # unidentified SessionStart would recreate the empty-corpus failure.
        # startup/clear: forget leftover from a crashed prior session, then mint.
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
