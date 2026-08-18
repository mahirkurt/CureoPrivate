#!/usr/bin/env python3
"""cureolex PreToolUse guard — Anamnesis collection scope (smallest hook).

DENY unscoped hybrid_query / graph_* / semantic_search / ingest / forget.
ALLOW when collection matches this sess or every doc_id is prefixed.
Fail-open. Disable: <project>/.claude/cureolex-anamnesis-guard.off
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def deny(reason: str) -> None:
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "[cureolex anamnesis] " + reason,
        }
    }))
    sys.exit(0)


def main() -> int:
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj and os.path.isfile(
            os.path.join(proj, ".claude", "cureolex-anamnesis-guard.off")):
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        from anamnesis_run import (
            deny_reason, ensure_ledger, is_anamnesis_tool, tool_base,
            tool_input_of,
        )
        tool = str(data.get("tool_name", ""))
        if not is_anamnesis_tool(tool):
            return 0
        reason = deny_reason(tool_base(tool), tool_input_of(data), ensure_ledger())
        if reason:
            deny(reason)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
