"""Shared helpers for brand-ecosystem-core Claude Code hooks.

Claude Code passes one JSON object on stdin to every command hook. Common
fields: session_id, transcript_path, cwd, hook_event_name. Event-specific:
tool_name/tool_input/tool_response (Pre/PostToolUse), prompt (UserPromptSubmit),
stop_hook_active (Stop).

Output conventions:
  - JSON on stdout with hookSpecificOutput.additionalContext → inject context
  - {"decision":"block","reason":...} on a Stop hook → CONTINUE the turn with
    the reason (does not reject; forces the model to keep going)
  - exit(0) with no output → no-op

Domain-agnostic, stdlib-only (no PyYAML). A master switch env var
BRAND_HOOKS_DISABLED=1 turns every hook into a silent no-op.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict


def hooks_enabled() -> bool:
    return os.environ.get("BRAND_HOOKS_DISABLED", "").strip() not in ("1", "true", "yes")


def read_event() -> Dict[str, Any]:
    """Parse the single JSON object on stdin. Fail-open (never hard-crash)."""
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def emit_json(obj: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj))
    sys.exit(0)


def inject_context(event_name: str, context: str) -> None:
    emit_json({"hookSpecificOutput": {"hookEventName": event_name,
                                       "additionalContext": context}})


def last_assistant_message(event: Dict[str, Any]) -> str:
    """Return the assistant's last message text, from the event or transcript."""
    msg = event.get("last_assistant_message")
    if isinstance(msg, str) and msg.strip():
        return msg
    transcript = event.get("transcript_path") or ""
    if not transcript or not os.path.exists(transcript):
        return ""
    try:
        last = ""
        with open(transcript, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("type") == "assistant" or rec.get("role") == "assistant":
                    content = rec.get("message", {}).get("content") or rec.get("content")
                    if isinstance(content, list):
                        parts = [c.get("text", "") for c in content
                                 if isinstance(c, dict) and c.get("type") == "text"]
                        text = "\n".join(p for p in parts if p)
                    elif isinstance(content, str):
                        text = content
                    else:
                        text = ""
                    if text.strip():
                        last = text
        return last
    except Exception:
        return ""
