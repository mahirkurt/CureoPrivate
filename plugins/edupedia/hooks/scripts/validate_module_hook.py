#!/usr/bin/env python3
"""edupedia PostToolUse advisory — MODULE_DATA taşıyan HTML dosyalarını otomatik 16 kalite kapısıyla doğrular.

Fail-open: hiçbir koşulda araç sonucunu bloklamaz (daima exit 0).
Kapı otoritesi yerel `skills/carbon-edupedia/scripts/validate_module.py`'dir.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR = ROOT / "skills" / "carbon-edupedia" / "scripts" / "validate_module.py"


def extract_filepath(data: dict) -> str:
    """Stdin JSON payload'ından dosya yolunu çıkarır."""
    tool_input = data.get("tool_input") or {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "path", "target_file", "filePath", "filename"):
            val = tool_input.get(key)
            if val and isinstance(val, str):
                return val
    return ""


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        data = json.loads(raw)
    except Exception:
        return 0

    try:
        file_path = extract_filepath(data)
        if not file_path or not file_path.endswith(".html"):
            return 0

        p = Path(file_path)
        if not p.is_file():
            return 0

        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return 0

        if "MODULE_DATA" not in content:
            return 0

        if not VALIDATOR.is_file():
            return 0

        res = subprocess.run(
            [sys.executable, str(VALIDATOR), str(p), "--json"],
            capture_output=True,
            text=True,
            timeout=25,
        )

        gates_json = {}
        if res.stdout.strip():
            try:
                gates_json = json.loads(res.stdout)
            except Exception:
                pass

        failed = [g for g, v in gates_json.items() if v.get("status") == "FAIL"]
        warned = [g for g, v in gates_json.items() if v.get("status") == "WARN"]

        if failed or warned:
            parts = []
            if failed:
                parts.append(f"FAIL Kapıları: {', '.join(failed)}")
            if warned:
                parts.append(f"WARN Kapıları: {', '.join(warned)}")
            msg = (
                f"[edupedia modül kalite denetimi] {p.name}: "
                + " · ".join(parts)
                + ". scripts/validate_module.py ile ayrıntıları inceleyin (advisory, bloklamaz)."
            )
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
