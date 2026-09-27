#!/usr/bin/env python3
"""check_drift [6]: `surface_snapshots` istisnası yalnız `tests/surface_snapshots/`
yoluna dar tutulmalı — herhangi bir `surface_snapshots` adlı dizine değil.

Fix round 1 bulgusu: eski koşul yalnız `path.parent.name == "surface_snapshots"`
bakıyordu; bu, `docs/surface_snapshots/` gibi alakasız bir dizini de sessizce
muaf tutardı (check_drift 10 plugin'in TAMAMINI tarayan paylaşılan bir CI
kapısıdır — gelecekte başka bir plugin'de aynı ada sahip alakasız bir dizin
sürüklenmeyi sessizce atlatabilirdi).
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_drift  # noqa: E402

FLEET = {"plugin": "testplug", "servers": [], "companions": []}
UNKNOWN_REF_LINE = "entries:\n  - {prefix: mcp__UnknownServer__, server: null}\n"


def _make_root(rel_path: str) -> Path:
    root = Path(tempfile.mkdtemp())
    p = root / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(UNKNOWN_REF_LINE, encoding="utf-8")
    return root


class SurfaceSnapshotExemptionScopeTests(unittest.TestCase):
    def test_tests_surface_snapshots_is_exempt(self):
        root = _make_root("tests/surface_snapshots/x.yaml")
        hits = check_drift.scan_server_ids(root, FLEET)
        self.assertEqual(hits, [], hits)

    def test_other_surface_snapshots_directory_is_not_exempt(self):
        """DAR eşleşme: yalnız `tests/surface_snapshots/`; `docs/surface_snapshots/`
        gibi bir yol bu istisnadan yararlanmamalı — sürüklenme kapıyı düşürmeli."""
        root = _make_root("docs/surface_snapshots/x.yaml")
        hits = check_drift.scan_server_ids(root, FLEET)
        self.assertTrue(
            any(ref == "UnknownServer" for _, _, ref in hits),
            f"beklenen: 'UnknownServer' filoda-yok olarak yakalanmalıydı, hits={hits}")


if __name__ == "__main__":
    unittest.main()
