#!/usr/bin/env python3
"""check_drift [7]: yeniden üretilmemiş yüzey paketi kapıyı düşürür (edupedia 1.0.0)."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GATE = REPO / "tools" / "fleetkit" / "check_drift.py"
BOOTSTRAP = REPO / "plugins" / "edupedia" / "surfaces" / "bootstrap.md"


def run_gate() -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GATE), "edupedia"], capture_output=True, text=True, timeout=120)


class SurfaceDriftGateTests(unittest.TestCase):
    def test_clean_tree_passes(self) -> None:
        self.assertTrue(BOOTSTRAP.is_file())
        res = run_gate()
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_edited_bootstrap_without_regeneration_fails(self) -> None:
        original = BOOTSTRAP.read_bytes()
        mutated = original + "\n- mutasyon: yeniden üretilmemiş satır\n".encode("utf-8")
        self.assertNotEqual(mutated, original)
        try:
            BOOTSTRAP.write_bytes(mutated)
            res = run_gate()
        finally:
            BOOTSTRAP.write_bytes(original)
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("[7] yüzey paketleri bayat", res.stdout)
        self.assertIn("surfaces/grok/grok-workspace.md", res.stdout)


if __name__ == "__main__":
    unittest.main()
