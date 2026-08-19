#!/usr/bin/env python3
"""PostToolUse ledger — record ingest_document ids, drop forget_document ids.

Matcher: mcp__.*anamnesis.*  Advisory additionalContext on ingest so the model
sees the exclusive prefix after a successful write. Fail-open.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anamnesis_run import (
    collection_for,
    collection_of,
    context_message,
    drop_doc_id,
    extract_doc_id,
    has_run_prefix,
    is_anamnesis_tool,
    load_ledger,
    record_doc_id,
    save_ledger,
    tool_base,
    tool_input_of,
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
    if not led or not doc:
        return 0
    if not has_run_prefix(doc, led["run_id"]):
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
    elif base == "forget_collection":
        if collection_of(tool_input_of(data)) == collection_for(led["run_id"]):
            led["doc_ids"] = []
            led["pending_forget"] = []
            led["status"] = "empty"
            save_ledger(led)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
