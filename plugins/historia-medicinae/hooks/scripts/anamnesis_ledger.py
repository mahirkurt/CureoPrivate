#!/usr/bin/env python3
"""PostToolUse ledger — record ingest_document ids, drop forget ids.

Matcher: mcp__.*anamnesis.*  Advisory additionalContext on ingest. Fail-open.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anamnesis_run import (  # noqa: E402
    context_message,
    drop_doc_id,
    extract_doc_id,
    has_run_prefix,
    is_anamnesis_tool,
    load_ledger,
    record_doc_id,
    save_ledger,
    tool_base,
)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = str(data.get("tool_name", ""))
    if not is_anamnesis_tool(tool):
        return 0
    base = tool_base(tool)
    doc = extract_doc_id(data)
    led = load_ledger()
    if not led:
        return 0
    if base == "forget_collection":
        led["doc_ids"] = []
        led["pending_forget"] = []
        led["status"] = "empty"
        save_ledger(led)
        return 0
    if not doc or not has_run_prefix(doc, led["run_id"]):
        return 0
    if base == "ingest_document":
        led = record_doc_id(doc)
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context_message(led),
            }
        }))
    elif base == "forget_document":
        drop_doc_id(doc)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
