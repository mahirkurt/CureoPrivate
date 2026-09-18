#!/usr/bin/env python3
"""edupedia SessionStart preflight (1.0.0 ince istemci) — tedy orkestratörü prob'u + akış kuralları.

Filo fleet.lock.json'dan gelir (tools/fleetkit/gen_fleet.py üretir). Vendor'lı fleet_probe kimliksiz
`initialize` gönderir (24 saat önbellekli); yalnız `tedy` sonucu yorumlanır: 401 sağlıklı (interaktif
OAuth), 200 güvenlik uyarısı, 403 erişim reddi, diğerleri erişilemedi. Fail-open: prob ya da lock çökerse
yalnız akış kuralları gider, oturum durmaz.
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

from hook_core import session_context  # noqa: E402


def main() -> int:
    try:
        sys.stdin.read()  # drain stdin payload if any
    except Exception:
        pass
    try:
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": session_context(ROOT, os.environ, fleet_probe),
            }
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    except Exception:
        pass  # fail-open
    return 0


if __name__ == "__main__":
    sys.exit(main())
