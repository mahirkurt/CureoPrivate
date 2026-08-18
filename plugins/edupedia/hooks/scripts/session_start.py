#!/usr/bin/env python3
"""edupedia SessionStart preflight — connector kadrosu prob'u + pedagojik konvansiyon enjeksiyonu.

v1.0.0: anahtar haritası hardcoded DEĞİL — `fleet.lock.json`'dan gelir (`tools/fleetkit/gen_fleet.py`
üretir, kaynak `fleet.yaml`). Preflight gerçek MCP `initialize` prob'u yapar (24 saat cache'li)
ve iki hâli AYIRIR:

  auth_missing → anahtar süreç ortamında yok  → MEŞRU DEGRADE
  unauthorized → sunucu 401/403 verdi         → YAPILANDIRMA ARIZASI

Sağlıklı filoda preflight bölümü SESSİZDİR (yalnız konvansiyonlar enjekte edilir).
Fail-open: prob veya lock çökerse yalnız konvansiyonlar gider, oturum durmaz.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS))
try:
    import fleet_probe
except Exception:
    fleet_probe = None

from hook_core import build_context, conventions, session_context  # noqa: E402,F401


def main() -> int:
    try:
        sys.stdin.read()  # drain stdin payload if any
    except Exception:
        pass

    try:
        ctx = session_context(ROOT, os.environ, fleet_probe)
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": ctx,
            }
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    except Exception:
        pass  # fail-open
    return 0


if __name__ == "__main__":
    sys.exit(main())
