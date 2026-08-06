#!/usr/bin/env python3
"""gen_fleet üretici birim testleri — stdlib unittest, AĞ ERİŞİMİ YOK.

Koşum:  cd plugins/lex-sanitas && python3 tools/test_gen_fleet.py -v
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_fleet  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class TestFleetRegistry(unittest.TestCase):
    def setUp(self):
        self.fleet = gen_fleet.load_fleet(ROOT)

    def test_fleet_sunucu_sayisi(self):
        self.assertEqual(len(self.fleet["servers"]), 19)
        self.assertEqual(len(self.fleet["companions"]), 5)
        self.assertEqual(len(self.fleet["delegations"]), 2)

    def test_titck_auth_zorunlu(self):
        """2026-08-02 kapılanması: titck ARTIK public değil."""
        titck = next(s for s in self.fleet["servers"] if s["name"] == "titck")
        self.assertEqual(titck["auth_env"], "TITCK_MCP_API_KEY")

    def test_health_policy_kanonik_env(self):
        hp = next(s for s in self.fleet["servers"] if s["name"] == "health-policy")
        self.assertEqual(hp["auth_env"], "HEALTH_POLICY_MCP_API_KEY")

    def test_yoktez_companion_degil(self):
        """yoktez v3.5.0'da first-class wire; companion listesinde OLMAMALI."""
        names = {s["name"] for s in self.fleet["servers"]}
        comp = {c["name"] for c in self.fleet["companions"]}
        self.assertIn("yoktez", names)
        self.assertFalse(names & comp, "wire'lı server companion olamaz")

    def test_lock_sayilari(self):
        lock = gen_fleet.build_lock(self.fleet)
        self.assertEqual(lock["counts"]["servers"], 19)
        self.assertEqual(lock["counts"]["gated"], 16)
        self.assertEqual(lock["counts"]["public"], 3)
        self.assertEqual(lock["counts"]["companions"], 5)

    def test_lock_role_metnini_tasimaz(self):
        """Lock hook'lar içindir; düzyazı şişirmez."""
        lock = gen_fleet.build_lock(self.fleet)
        for s in lock["servers"]:
            self.assertNotIn("role", s)
            self.assertNotIn("tools_used", s)

    def test_mcp_json_auth_header_uretimi(self):
        mcp = gen_fleet.build_mcp_servers(self.fleet)
        self.assertEqual(
            mcp["titck"]["headers"]["Authorization"], "Bearer ${TITCK_MCP_API_KEY}"
        )
        self.assertNotIn("headers", mcp["yoktez"], "public server header taşımaz")

    def test_sema_dogrulama_bozuk_tier_reddeder(self):
        bad = {
            "version": 1, "plugin": "x", "plugin_version": "1",
            "servers": [{"name": "a", "url": "https://a/mcp", "tier": "UYDURMA",
                         "auth_env": None, "shard": "S1", "modes": ["ALL"],
                         "gate": None, "tools_used": [], "role": "r", "degrade": "d"}],
            "companions": [], "delegations": [],
        }
        with self.assertRaises(ValueError):
            gen_fleet.validate_fleet(bad)

    def test_sema_dogrulama_companion_cakismasi_reddeder(self):
        bad = {
            "version": 1, "plugin": "x", "plugin_version": "1",
            "servers": [{"name": "yoktez", "url": "https://a/mcp", "tier": "doctrine",
                         "auth_env": None, "shard": "S3", "modes": ["ALL"],
                         "gate": None, "tools_used": [], "role": "r", "degrade": "d"}],
            "companions": [{"name": "yoktez", "tool_prefixes": ["x"], "gate": None,
                            "modes": ["ALL"], "manifest_row": "y", "degrade": "d"}],
            "delegations": [],
        }
        with self.assertRaises(ValueError):
            gen_fleet.validate_fleet(bad)

    # ── Task 2: türetilmiş artefaktlar ────────────────────────────────────
    def test_mcp_json_uretilen_ile_commitli_ayni(self):
        """CI kapısının çekirdeği: diskteki .mcp.json üretilenle birebir olmalı."""
        expected = gen_fleet.build_mcp_json(self.fleet)
        actual = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_codex_mcpservers_ayni(self):
        codex = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(codex["mcpServers"], gen_fleet.build_mcp_servers(self.fleet))

    def test_codex_diger_alanlar_korunur(self):
        codex = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertIn("interface", codex)
        self.assertEqual(codex["interface"]["displayName"], "Lex Sanitas")

    # ── Task 7: ajan shard kısıtları ──────────────────────────────────────
    def test_legal_distiller_S2_gormez(self):
        """S1+S3 ajanı karşılaştırmalı server'ları görmemeli."""
        line = gen_fleet.agent_tools_line(
            self.fleet, ["S1", "S3"], ["Read"], companions=True)
        self.assertIn("mcp__mevzuat__*", line)
        self.assertIn("mcp__yoktez__*", line)
        self.assertNotIn("mcp__health-policy__*", line)
        self.assertNotIn("mcp__eudamed__*", line)

    def test_comparative_S1_gormez(self):
        line = gen_fleet.agent_tools_line(
            self.fleet, ["S2", "S4"], ["Read"], companions=True)
        self.assertIn("mcp__health-policy__*", line)
        self.assertIn("mcp__openathens__*", line)
        self.assertNotIn("mcp__tbmm__*", line)

    def test_anamnesis_her_ajanda(self):
        """shard=ALL olan substrat her shard'a girer."""
        for shards in (["S1", "S3"], ["S2", "S4"]):
            self.assertIn(
                "mcp__anamnesis__*",
                gen_fleet.agent_tools_line(self.fleet, shards, [], companions=False),
            )

    def test_ajan_dosyalari_gen_blogu_tasiyor(self):
        for agent, *_ in gen_fleet.AGENT_SHARDS:
            text = (ROOT / "agents" / agent).read_text(encoding="utf-8")
            self.assertIn("# GEN:agent-tools BEGIN", text, agent)
            self.assertIn("tools:", text, agent)


if __name__ == "__main__":
    unittest.main()
