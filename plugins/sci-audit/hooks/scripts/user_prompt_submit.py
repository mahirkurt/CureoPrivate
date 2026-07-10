#!/usr/bin/env python3
"""UserPromptSubmit hook (Layer 1: deterministic gate).

Scans the prompt about to be sent for high-confidence secret patterns (API
keys, private keys, tokens). If found, BLOCKS the prompt so the secret never
reaches the model or any logging backend.

Block contract: exit code 2 + reason on stderr.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import SECRET_PATTERNS, allow, block, hooks_enabled, read_event  # noqa: E402


def main() -> None:
    if not hooks_enabled():
        allow()  # project master switch: skip secret scan
    event = read_event()
    prompt = event.get("prompt", "") or ""
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, prompt):
            block(
                f"Blocked: prompt appears to contain a secret ({label}). "
                "Remove the credential before sending. Rotate it if it was real."
            )
    allow()


if __name__ == "__main__":
    main()
