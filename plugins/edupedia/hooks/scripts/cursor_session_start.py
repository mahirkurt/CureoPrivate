#!/usr/bin/env python3
"""Cursor sessionStart wrapper — yalnız Cursor-native JSON üretir."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

try:
    import fleet_probe
except Exception:
    fleet_probe = None

from hook_core import resolve_plugin_root, session_context  # noqa: E402


def main() -> int:
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("hook input mapping değil")
        root = resolve_plugin_root("CURSOR_PLUGIN_ROOT", __file__)
        context = session_context(root, os.environ, fleet_probe)
        output = {"additional_context": context}
    except Exception:
        output = {}
    sys.stdout.write(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
