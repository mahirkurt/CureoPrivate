#!/usr/bin/env python3
"""edupedia PostToolUse advisory — MODULE_DATA taşıyan HTML dosyalarını otomatik 16 kalite kapısıyla doğrular.

Fail-open: hiçbir koşulda araç sonucunu bloklamaz (daima exit 0).
Kapı otoritesi yerel `skills/carbon-edupedia/scripts/validate_module.py`'dir.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = Path(__file__).resolve().parent
ALLOWED_TOOL_NAMES = frozenset({"Write", "Edit", "StrReplace"})

sys.path.insert(0, str(SCRIPTS))
from hook_core import extract_write_path, module_advisory  # noqa: E402


extract_filepath = extract_write_path


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        data = json.loads(raw)
    except Exception:
        return 0

    try:
        msg = module_advisory(data, ROOT, ALLOWED_TOOL_NAMES)
        if msg:
            payload = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": msg,
                }
            }
            sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    except Exception:
        pass  # fail-open

    return 0


if __name__ == "__main__":
    sys.exit(main())
