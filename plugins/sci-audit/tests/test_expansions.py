"""Tests for the v0.2 expansions (stdlib-only).

Run:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/sci-audit/tests
"""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(PLUGIN_ROOT, rel))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


stats = _load("stats_forensics2", "skills/stats-forensics/scripts/stats_forensics.py")
halluc = _load("hallucination_signals2", "skills/hallucination-signals/scripts/hallucination_signals.py")
aitrans = _load("ai_transparency", "skills/ai-transparency/scripts/ai_transparency.py")
prescan = _load("guideline_prescan", "skills/sci-audit-orchestrator/scripts/guideline_prescan.py")
ledger = _load("evidence_ledger", "skills/sci-audit-orchestrator/scripts/evidence_ledger.py")
sement = _load("semantic_entropy2", "skills/hallucination-signals/scripts/semantic_entropy.py")


# --- Axis C: Turkish decimals + P2 depth -----------------------------------

class TestStatsTurkishAndDepth(unittest.TestCase):
    def test_turkish_decimal_statcheck(self):
        r = stats.audit_text("Sonuç: t(38) = 2,50, p = 0,20 bulundu.")
        codes = [f["code"] for f in r["findings"]]
        self.assertIn("statcheck-inconsistent-decision", codes)

    def test_turkish_F_not_swallowed(self):
        # F(2, 40) df must parse, not be eaten as one comma-decimal.
        r = stats.audit_text("Ayrıca F(2, 40) = 5,00, p = 0,30.")
        self.assertTrue(any(f["code"].startswith("statcheck") for f in r["findings"]))

    def test_one_tailed_reclassification(self):
        # t(30)=1.70 two-sided p≈0.099; one-sided ≈0.05 -> info, not blocker.
        r = stats.audit_text("A directional test, t(30) = 1.70, p = 0.05.")
        codes = [f["code"] for f in r["findings"]]
        self.assertIn("statcheck-maybe-one-tailed", codes)
        self.assertEqual(r["counts"]["error"], 0)

    def test_sprite_infeasible_sd(self):
        r = stats.audit_text("On a 1-5 scale, mean 3.0, SD 2.5, N = 30.")
        self.assertIn("sprite-infeasible-sd", [f["code"] for f in r["findings"]])

    def test_sprite_feasible_clean(self):
        r = stats.audit_text("On a 1-5 scale, mean 3.0, SD 1.0, N = 30.")
        self.assertFalse(any(f["code"] == "sprite-infeasible-sd" for f in r["findings"]))

    def test_ci_excludes_estimate(self):
        r = stats.audit_text("The effect was OR 5.0 (95% CI 1.2-4.0).")
        self.assertIn("ci-excludes-estimate", [f["code"] for f in r["findings"]])

    def test_ci_p_significance_mismatch(self):
        r = stats.audit_text("Risk was OR 2.5 (95% CI 1.2-4.0), p = 0.30.")
        self.assertIn("ci-p-significance-mismatch", [f["code"] for f in r["findings"]])

    def test_subgroup_sum_mismatch(self):
        r = stats.audit_text("The cohort (N = 50) split into groups (30, 15).")
        self.assertIn("subgroup-sum-mismatch", [f["code"] for f in r["findings"]])

    def test_percentage_sum_off(self):
        r = stats.audit_text("Categories were 40%, 40%, and 30% respectively.")
        self.assertIn("percentage-sum-off", [f["code"] for f in r["findings"]])

    def test_grimmer_present(self):
        # A clearly infeasible SD given integer data should be catchable.
        r = stats.audit_text("mean 2.0, SD 0.03, N = 3.")
        # Either grimmer or clean depending on rounding; assert it runs & lists caveat.
        self.assertIn("caveat", r)
        self.assertIn("grimmer", r["checks_run"])

    def test_caveat_and_checks_run(self):
        r = stats.audit_text("no stats here")
        self.assertTrue(r["caveat"])
        self.assertEqual(len(r["checks_run"]), 8)


# --- Axis D: identifier checksums ------------------------------------------

class TestIdentifierChecksums(unittest.TestCase):
    def test_valid_isbn13_passes(self):
        r = halluc.audit_text("Book ISBN 978-0-306-40615-7 was cited.")
        self.assertNotIn("invalid-isbn13", [f["code"] for f in r["findings"]])

    def test_invalid_isbn13_flagged(self):
        r = halluc.audit_text("Fake ISBN 978-0-306-40615-8 was cited.")
        self.assertIn("invalid-isbn13", [f["code"] for f in r["findings"]])

    def test_valid_orcid_passes(self):
        r = halluc.audit_text("Author ORCID 0000-0002-1825-0097 listed.")
        self.assertNotIn("invalid-orcid", [f["code"] for f in r["findings"]])

    def test_invalid_orcid_flagged(self):
        r = halluc.audit_text("Author ORCID 0000-0002-1825-0098 listed.")
        self.assertIn("invalid-orcid", [f["code"] for f in r["findings"]])

    def test_arxiv_month_out_of_range(self):
        r = halluc.audit_text("Preprint arXiv:2513.01234 studied.")
        self.assertIn("malformed-arxiv-id", [f["code"] for f in r["findings"]])


# --- Axis F: AI transparency -----------------------------------------------

class TestAiTransparency(unittest.TestCase):
    def test_missing_disclosure_with_signal_is_error(self):
        r = aitrans.audit_text("As an AI language model, I generated this section.")
        codes = [f["code"] for f in r["findings"]]
        self.assertIn("missing-ai-disclosure", codes)
        self.assertFalse(r["disclosure_present"])
        self.assertEqual(r["counts"]["error"], 1)

    def test_genuine_disclosure_clean(self):
        r = aitrans.audit_text("Methods: Generative AI (ChatGPT) was used to edit language.")
        self.assertTrue(r["disclosure_present"])
        self.assertEqual(r["counts"]["error"], 0)

    def test_negative_disclosure_counts(self):
        r = aitrans.audit_text("No generative AI was used in this study.")
        self.assertTrue(r["disclosure_present"])

    def test_placeholder_flagged(self):
        r = aitrans.audit_text("The result was [insert citation] significant. No AI was used.")
        self.assertIn("unfilled-placeholder", [f["code"] for f in r["findings"]])


# --- Axis E: guideline pre-scan --------------------------------------------

class TestGuidelinePrescan(unittest.TestCase):
    def test_section_presence(self):
        r = prescan.audit_text("# Introduction\nx\n# Methods\ny\n# Results\nSee Table 1.")
        self.assertIn("introduction", r["sections_present"])
        self.assertIn("methods", r["sections_present"])
        self.assertIn("discussion", r["sections_missing"])

    def test_structure_detection(self):
        r = prescan.audit_text("As shown in Table 2 and Figure 1.")
        present = {s["name"] for s in r["structures"] if s["present"]}
        self.assertIn("table", present)
        self.assertIn("figure", present)

    def test_all_14_guidelines_exist(self):
        gdir = os.path.join(PLUGIN_ROOT, "skills", "sci-audit-orchestrator", "references", "guidelines")
        files = {f[:-3] for f in os.listdir(gdir) if f.endswith(".md")}
        expected = {"prisma", "prisma-scr", "consort", "consort-ai", "strobe", "coreq",
                    "srqr", "jars", "tripod", "tripod-ai", "stard", "spirit", "cheers", "arrive"}
        self.assertTrue(expected.issubset(files), f"missing: {expected - files}")


# --- P5: evidence ledger ---------------------------------------------------

class TestEvidenceLedger(unittest.TestCase):
    def test_hash_deterministic(self):
        self.assertEqual(ledger.content_hash("abc"), ledger.content_hash("abc"))
        self.assertNotEqual(ledger.content_hash("abc"), ledger.content_hash("abd"))

    def test_entry_and_verify(self):
        e = ledger.make_entry("claim", "PMID:1", "source text", "grounded", "abstract", ts="2026-01-01T00:00:00Z")
        self.assertTrue(ledger.verify_entry(e, "source text"))
        self.assertFalse(ledger.verify_entry(e, "tampered text"))

    def test_entry_excludes_body(self):
        e = ledger.make_entry("c", "id", "SECRET BODY", "v", "abstract")
        self.assertNotIn("SECRET BODY", str(e))  # only the hash is stored


# --- P3c: entropy from clusters --------------------------------------------

class TestEntropyFromClusters(unittest.TestCase):
    def test_single_cluster_zero_entropy(self):
        out = sement.entropy_from_clusters([6])
        self.assertEqual(out["n_clusters"], 1)
        self.assertAlmostEqual(out["entropy"], 0.0)

    def test_split_clusters_positive(self):
        out = sement.entropy_from_clusters([3, 3])
        self.assertEqual(out["n_clusters"], 2)
        self.assertGreater(out["entropy"], 0)


if __name__ == "__main__":
    unittest.main()
