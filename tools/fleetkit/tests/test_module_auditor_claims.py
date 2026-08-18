#!/usr/bin/env python3
"""module-auditor tetiklenme iddialarının gerçek hook davranışıyla hizası."""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
AUDITOR = REPO / "plugins" / "edupedia" / "agents" / "module-auditor.md"


class ModuleAuditorClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = AUDITOR.read_text(encoding="utf-8")

    def test_auditor_is_explicit_qualitative_second_eye(self) -> None:
        self.assertIn("açıkça çağrılan niteliksel ikinci göz", self.text)

    def test_hooks_run_only_deterministic_gates(self) -> None:
        self.assertIn("yalnız 16 deterministik kalite kapısını", self.text)
        self.assertIn("module-auditor'ı otomatik çağırmaz", self.text)

    def test_old_auto_dispatch_claims_are_removed(self) -> None:
        self.assertNotIn("Hook tetiklemesi.", self.text)
        self.assertNotIn("otomatik QA döngüsü tetiklediğinde", self.text)

    def test_claude_ai_no_subagent_note_is_preserved(self) -> None:
        self.assertIn("Claude.ai'da hook ve alt-ajan yoktur", self.text)


if __name__ == "__main__":
    unittest.main()
