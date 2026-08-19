#!/usr/bin/env python3
"""vekayinuvis PreToolUse — DENY unscoped Anamnesis hybrid/graph/search.

Matcher: mcp__.*  Fail-open. Disable: <project>/.claude/vekayinuvis-anamnesis.off
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anamnesis_run import (  # noqa: E402
    GUARD_OFF,
    deny_reason,
    ensure_ledger,
    is_anamnesis_tool,
    tool_base,
    tool_input_of,
)


def deny(reason: str) -> None:
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "[vekayinuvis anamnesis] " + reason,
        }
    }))
    sys.exit(0)


def main() -> int:
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj and os.path.isfile(os.path.join(proj, ".claude", GUARD_OFF)):
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = str(data.get("tool_name", ""))
    if not is_anamnesis_tool(tool):
        return 0
    try:
        reason = deny_reason(tool_base(tool), tool_input_of(data), ensure_ledger())
        if reason:
            deny(reason)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
