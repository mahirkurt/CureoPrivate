#!/usr/bin/env python3
"""gen_fleet.server_prefixes — Cowork biçimi (mcp__<Görünen_Ad>__)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gen_fleet  # noqa: E402


class CoworkPrefixTests(unittest.TestCase):
    def test_explicit_claude_ai_prefix_gets_cowork_form(self):
        s = {"name": "titck", "tool_prefixes": ["mcp__titck__", "mcp__claude_ai_T_TCK__"]}
        self.assertIn("mcp__T_TCK__", gen_fleet.server_prefixes(s, "cureolex"))

    def test_derived_claude_ai_prefix_gets_cowork_form(self):
        out = gen_fleet.server_prefixes({"name": "health-policy"}, "cureolex")
        self.assertIn("mcp__claude_ai_Health_Policy__", out)
        self.assertIn("mcp__Health_Policy__", out)

    def test_plugin_scoped_forms_stay_first(self):
        out = gen_fleet.server_prefixes({"name": "mevzuat"}, "cureolex")
        self.assertEqual(out[:2], ["mcp__plugin_cureolex_mevzuat__", "mcp__plugin-cureolex-mevzuat__"])

    def test_no_duplicates(self):
        s = {"name": "tbmm", "tool_prefixes": ["mcp__tbmm__", "mcp__claude_ai_tbmm__"]}
        out = gen_fleet.server_prefixes(s, "cureolex")
        self.assertEqual(len(out), len(set(out)))

    def test_companion_prefixes_get_cowork_form(self):
        fleet = {"plugin": "cureolex", "servers": [],
                 "companions": [{"name": "X", "tool_prefixes": ["mcp__claude_ai_De_Jure__"]}]}
        line = gen_fleet.gen_agent_tools(fleet, {"shards": ["S1"], "companions": True})
        self.assertIn("mcp__De_Jure__*", line)


if __name__ == "__main__":
    unittest.main()
