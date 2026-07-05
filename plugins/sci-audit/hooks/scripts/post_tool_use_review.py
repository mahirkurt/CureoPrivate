#!/usr/bin/env python3
"""PostToolUse hook (Layer 1: deterministic gate).

Runs AFTER a Bash command executes. It cannot undo the side effect, but it:
  1. Flags high-confidence secret leaks in the output (redaction warning).
  2. Feeds obvious error signatures (Traceback, FATAL, segfault) back to the model.

Feedback contract: hookSpecificOutput.additionalContext.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import SECRET_PATTERNS, read_event  # noqa: E402

ERROR_SIGNATURES = ("Traceback (most recent call last)", "FATAL:", "segfault")


def extract_response_text(event: dict) -> str:
    parts: list[str] = []

    def add(value: object) -> None:
        if value is None:
            return
        if isinstance(value, str):
            parts.append(value)
            return
        parts.append(json.dumps(value))

    for key in ("tool_response", "tool_output", "output", "response"):
        add(event.get(key))

    for key in ("result", "tool_result"):
        value = event.get(key)
        if isinstance(value, dict):
            for nested_key in ("output", "stdout", "stderr", "text"):
                add(value.get(nested_key))

    return "\n".join(parts)


def main() -> None:
    event = read_event()
    text = extract_response_text(event)

    leaked_labels = sorted({label for pattern, label in SECRET_PATTERNS if re.search(pattern, text)})
    if leaked_labels:
        sys.stdout.write(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": (
                            "The command output contains high-confidence secret-like value(s): "
                            + ", ".join(leaked_labels)
                            + ". Treat the previous output as sensitive; avoid repeating it, "
                            "redact summaries, and rotate the credential if it was real."
                        ),
                    }
                }
            )
        )
        sys.exit(0)

    for sig in ERROR_SIGNATURES:
        if sig in text:
            sys.stdout.write(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PostToolUse",
                            "additionalContext": (
                                f"The command output contains an error signature "
                                f"('{sig}'). Diagnose and fix before proceeding."
                            ),
                        }
                    }
                )
            )
            sys.exit(0)

    sys.exit(0)  # nothing to flag


if __name__ == "__main__":
    main()
