#!/usr/bin/env python3
"""Cursor postToolUse wrapper — Write sonrası advisory kalite bağlamı."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
ALLOWED_TOOL_NAMES = frozenset({"Write"})

from hook_core import module_advisory, resolve_plugin_root  # noqa: E402


def main() -> int:
    output = {}
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("hook input mapping değil")
        root = resolve_plugin_root("CURSOR_PLUGIN_ROOT", __file__)
        context = module_advisory(data, root, ALLOWED_TOOL_NAMES)
        if context:
            output = {"additional_context": context}
    except Exception:
        pass
    sys.stdout.write(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
