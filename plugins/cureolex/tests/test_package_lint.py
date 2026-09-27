#!/usr/bin/env python3
"""package_lint birim testleri — run_suites.py [9] tarafından da koşulur."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import package_lint as pl  # noqa: E402

FLEET = {
    "servers": [
        {"name": "mevzuat", "tools_used": ["get_mevzuat_content", "search_within_mevzuat"]},
        {"name": "literatur", "tools_used": ["tr_literatur_read_article"]},
    ],
    "companions": [{"name": "De Jure", "tools": ["search_decisions"]}],
}


def make_root(files: dict) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, txt in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
    return root


class ToolReferenceTests(unittest.TestCase):
    def test_call_form_is_a_reference(self):
        self.assertIn("madde_acikla", pl.tool_references("`madde_acikla(madde_no)` drill-down"))

    def test_chain_members_are_references(self):
        refs = pl.tool_references("`search_articles` → `pdf_to_html` → `get_article_references`")
        self.assertEqual(refs, {"search_articles", "pdf_to_html", "get_article_references"})

    def test_unbackticked_chain(self):
        self.assertIn("pdf_to_html", pl.tool_references("search_articles → pdf_to_html ile tam metin"))

    def test_mcp_call_key_is_a_reference(self):
        refs = pl.tool_references("mcp_call: search_aym_norm_denetimi\n   query: x")
        self.assertIn("search_aym_norm_denetimi", refs)

    def test_plain_backticked_field_is_not_a_reference(self):
        self.assertEqual(pl.tool_references("alan `as_of_date` zorunlu"), set())

    def test_file_names_are_not_references(self):
        self.assertEqual(pl.tool_references("`scope_guard.py` → hook"), set())


class CheckToolNamesTests(unittest.TestCase):
    def test_ghost_is_reported_known_is_not(self):
        root = make_root({"skills/cureolex/SKILL.md":
                          "önce `get_mevzuat_content(madde_no)` sonra `madde_acikla(madde_no)`"})
        errors, _ = pl.check_tool_names(root, FLEET)
        msgs = " ".join(m for _, m in errors)
        self.assertIn("madde_acikla", msgs)
        self.assertNotIn("get_mevzuat_content", msgs)

    def test_prefixed_tool_name_is_checked(self):
        root = make_root({"agents/a.md": "`mcp__mevzuat__ilga_zinciri(x)`"})
        errors, _ = pl.check_tool_names(root, FLEET)
        self.assertTrue(any("ilga_zinciri" in m for _, m in errors))

    def test_schema_field_in_chain_is_not_a_ghost(self):
        root = make_root({
            "skills/cureolex/schemas/x.schema.json":
                '{"properties": {"as_of_date": {}, "in_force_status": {}}}',
            "skills/cureolex/SKILL.md": "`as_of_date` → `in_force_status`",
        })
        errors, _ = pl.check_tool_names(root, FLEET)
        self.assertEqual(errors, [])

    def test_companion_tool_is_known(self):
        root = make_root({"commands/c.md": "`search_decisions(q)`"})
        self.assertEqual(pl.check_tool_names(root, FLEET)[0], [])


class SurfaceSnapshotTests(unittest.TestCase):
    def test_pattern_covers_exact_prefix(self):
        self.assertTrue(pl.pattern_covers("mcp__T_TCK__*", "mcp__T_TCK__"))
        self.assertFalse(pl.pattern_covers("mcp__T_TCK_Data__*", "mcp__T_TCK__"))

    def test_case_and_separator_sensitive(self):
        self.assertFalse(pl.pattern_covers("mcp__health-policy__*", "mcp__Health_Policy__"))
        self.assertFalse(pl.pattern_covers("mcp__mevzuat__*", "mcp__Mevzuat__"))

    def _fixture(self, tools_line, entries):
        fleet = {"servers": [{"name": "titck", "shard": "S1"}, {"name": "oecd", "shard": "S2"}],
                 "generated_blocks": [{"file": "agents/a.md", "name": "agent-tools",
                                       "generator": "agent_tools", "config": {"shards": ["S1"]}}]}
        root = make_root({
            "agents/a.md": f"---\n# GEN:agent-tools BEGIN\n{tools_line}\n# GEN:agent-tools END\n---\n",
            "tests/surface_snapshots/cowork.yaml":
                "surface: cowork\nobserved: test\nentries:\n" + entries,
        })
        return root, fleet

    def test_uncovered_prefix_is_an_error(self):
        root, fleet = self._fixture("tools: Read, mcp__titck__*",
                                    "  - {prefix: mcp__T_TCK__, server: titck, evidence: [search_drugs]}\n")
        errors, _ = pl.check_surface_snapshots(root, fleet)
        self.assertTrue(any("mcp__T_TCK__" in m and "agents/a.md" in m for _, m in errors))

    def test_covered_prefix_passes_and_other_shard_ignored(self):
        root, fleet = self._fixture(
            "tools: Read, mcp__T_TCK__*",
            "  - {prefix: mcp__T_TCK__, server: titck, evidence: [search_drugs]}\n"
            "  - {prefix: mcp__claude_ai_oecd__, server: oecd, evidence: [query_data]}\n")
        errors, _ = pl.check_surface_snapshots(root, fleet)
        self.assertEqual(errors, [])

    def test_unmapped_prefix_is_a_warning_not_error(self):
        root, fleet = self._fixture("tools: Read",
                                    "  - {prefix: mcp__TR_Dizin__, server: null, evidence: rapor}\n")
        errors, warnings = pl.check_surface_snapshots(root, fleet)
        self.assertEqual(errors, [])
        self.assertTrue(any("mcp__TR_Dizin__" in m for _, m in warnings))

    def test_unknown_server_is_an_error(self):
        root, fleet = self._fixture("tools: Read",
                                    "  - {prefix: mcp__X__, server: yok-boyle, evidence: [a_b]}\n")
        self.assertTrue(pl.check_surface_snapshots(root, fleet)[0])


class ForbiddenNamesTests(unittest.TestCase):
    def test_forbidden_name_is_reported(self):
        root = make_root({"skills/cureolex/SKILL.md": "Bireysel dava → saglik-sigorta"})
        errors, _ = pl.check_forbidden_names(root, FLEET)
        self.assertTrue(any("saglik-sigorta" in m for _, m in errors))

    def test_case_insensitive(self):
        root = make_root({"README.md": "PROMO-CENSOR"})
        self.assertTrue(pl.check_forbidden_names(root, FLEET)[0])

    def test_exempt_files_are_skipped(self):
        root = make_root({"CHANGELOG.md": "3.x: onko-erisim yönlendirmesi vardı"})
        self.assertEqual(pl.check_forbidden_names(root, FLEET)[0], [])

    def test_binary_like_files_are_skipped(self):
        root = make_root({"docs/logo.png": "onko-erisim"})
        self.assertEqual(pl.check_forbidden_names(root, FLEET)[0], [])


if __name__ == "__main__":
    unittest.main()
