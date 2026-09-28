#!/usr/bin/env python3
"""Yetenek bayrağı değerlendirmesi ve güven tavanı (4.1: conditional + yoklama)."""
import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validate_packs as vp  # noqa: E402

PACKS = vp.load_packs()
TR = PACKS["TR"][1]


class CapabilityValueTests(unittest.TestCase):
    def test_tr_case_law_is_conditional(self):
        cap = TR["capabilities"]["has_case_law_api"]
        self.assertEqual(cap["value"], "conditional")
        self.assertEqual(set(cap["requires_any_of"]), {"Yargı", "De Jure"})

    def test_conditional_without_probe_is_false(self):
        self.assertFalse(vp.capability_value(TR["capabilities"], "has_case_law_api"))

    def test_conditional_with_probe(self):
        self.assertTrue(vp.capability_value(TR["capabilities"], "has_case_law_api",
                                            {"has_case_law_api": True}))

    def test_plain_true_ignores_probes(self):
        self.assertTrue(vp.capability_value(TR["capabilities"], "has_consolidated_text", {}))


class CeilingTests(unittest.TestCase):
    def test_conditional_without_probe_is_pessimistic(self):
        ceiling, applied = vp.tavan_hesapla(TR, mode="ANALYZE")
        self.assertIn("CC-3", applied)
        self.assertEqual(ceiling, "MODERATE")

    def test_probe_true_lifts_cc3(self):
        ceiling, applied = vp.tavan_hesapla(TR, mode="ANALYZE", probes={"has_case_law_api": True})
        self.assertNotIn("CC-3", applied)


class OptimisticFlagTests(unittest.TestCase):
    def _issues(self, pack):
        return vp.capability_issues(pack, servers={"mevzuat", "uk-legal"},
                                    companions={"Yargı", "De Jure", "Open Law"})

    def test_true_on_companion_basis_is_rejected(self):
        pack = copy.deepcopy(TR)
        pack["capabilities"]["has_case_law_api"] = {
            "value": True, "basis": "Yargı companion (mcp__Yarg__*) — wire'lı değil."}
        self.assertTrue(any("has_case_law_api" in m for m in self._issues(pack)))

    def test_true_on_wired_basis_passes(self):
        pack = {"capabilities": {"has_case_law_api": {
            "value": True, "basis": "uk-legal case_law_search wire'lı; Open Law çapraz."}}}
        self.assertEqual(self._issues(pack), [])

    def test_requires_unknown_companion_is_rejected(self):
        pack = {"capabilities": {"has_case_law_api": {
            "value": "conditional", "requires_any_of": ["Yok"], "basis": "deneme dayanak metni"}}}
        self.assertTrue(self._issues(pack))

    def test_turkish_inflection_is_not_a_false_wired_match(self):
        # "mevzuatı" (mevzuat + Turkish suffix) must NOT count as naming the
        # wired 'mevzuat' server — the dotless-ı is a Unicode word char, not a
        # boundary. Regression for the ASCII-only boundary false-negative.
        pack = {"capabilities": {"has_authentic_translation": {
            "value": True,
            "basis": "Senedd (Galler) mevzuatı İngilizce + Galce eşit geçerlidir."}}}
        self.assertTrue(any("has_authentic_translation" in m for m in self._issues(pack)))

    def test_true_on_mcp_prefix_basis_passes(self):
        pack = {"capabilities": {"has_consolidated_text": {
            "value": True,
            "basis": "mcp__mevzuat__get_mevzuat_content — konsolide metin"}}}
        self.assertEqual(self._issues(pack), [])

    def test_true_on_hyphenated_server_name_passes(self):
        pack = {"capabilities": {"has_case_law_api": {
            "value": True, "basis": "uk-legal case_law_search wire'lı"}}}
        self.assertEqual(self._issues(pack), [])


if __name__ == "__main__":
    unittest.main()
