#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import snapshot_prefixes as sp  # noqa: E402

FLEET = {"servers": [
    {"name": "titck", "tools_used": ["search_drugs", "get_drug"]},
    {"name": "mevzuat", "tools_used": ["search_mevzuat"], "tools_fallback": ["search", "fetch"]},
]}


class MapPrefixTests(unittest.TestCase):
    def test_maps_by_tool_intersection(self):
        rows = sp.map_prefixes(["mcp__T_TCK__search_drugs", "mcp__T_TCK__get_drug"], FLEET)
        self.assertEqual(rows, [{"prefix": "mcp__T_TCK__", "server": "titck",
                                 "evidence": ["get_drug", "search_drugs"]}])

    def test_unknown_tools_map_to_null(self):
        rows = sp.map_prefixes(["mcp__TR_Dizin__trdizin_ara"], FLEET)
        self.assertIsNone(rows[0]["server"])

    def test_generic_names_alone_do_not_map(self):
        rows = sp.map_prefixes(["mcp__X__search", "mcp__X__fetch"], FLEET)
        self.assertIsNone(rows[0]["server"])

    def test_non_tool_lines_ignored(self):
        self.assertEqual(sp.map_prefixes(["Read", "", "# başlık"], FLEET), [])

    def test_merge_keeps_old_entries(self):
        old = {"entries": [{"prefix": "mcp__A__", "server": "titck", "evidence": ["get_drug"]}]}
        new = [{"prefix": "mcp__B__", "server": None, "evidence": ["x_y"]}]
        merged = sp.merge(old, new, surface="s", observed="o")
        self.assertEqual([e["prefix"] for e in merged["entries"]], ["mcp__A__", "mcp__B__"])


if __name__ == "__main__":
    unittest.main()
