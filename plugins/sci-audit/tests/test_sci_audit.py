"""sci-audit deterministic test suite (stdlib-only).

Run:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/sci-audit/tests

Core tests must pass with no third-party packages. The Zemberek provider test
is skipped when the package is absent (skipUnless).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(PLUGIN_ROOT, "hooks", "scripts")
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load(module_name: str, rel_path: str):
    path = os.path.join(PLUGIN_ROOT, rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # dataclass field resolution needs this
    spec.loader.exec_module(mod)
    return mod


stats = _load("stats_forensics", "skills/stats-forensics/scripts/stats_forensics.py")
claim = _load("claim_grounding", "skills/claim-grounding/scripts/claim_grounding.py")
halluc = _load("hallucination_signals", "skills/hallucination-signals/scripts/hallucination_signals.py")
trsci = _load("tr_sciaudit", "skills/turkish-sci-style/scripts/tr_sciaudit.py")
sement = _load("semantic_entropy", "skills/hallucination-signals/scripts/semantic_entropy.py")


def _run_hook(script: str, event: dict, env_extra: dict | None = None):
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = PLUGIN_ROOT
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, script)],
        input=json.dumps(event), text=True, capture_output=True, env=env,
    )
    return proc


# --- Axis C: stats forensics ----------------------------------------------

class TestStatcheck(unittest.TestCase):
    def test_t_pvalue_recomputation(self):
        p = stats.p_from_t(2.50, 38)
        self.assertAlmostEqual(p, 0.0169, places=3)

    def test_f_pvalue(self):
        p = stats.p_from_f(5.00, 2, 40)
        self.assertAlmostEqual(p, 0.0114, places=3)

    def test_chi2_pvalue(self):
        p = stats.p_from_chi2(10.0, 1)
        self.assertAlmostEqual(p, 0.00157, places=4)

    def test_z_pvalue(self):
        self.assertAlmostEqual(stats.p_from_z(1.96), 0.05, places=2)

    def test_decision_changing_flagged(self):
        r = stats.audit_text("t(38) = 2.50, p = 0.20.")
        codes = [f["code"] for f in r["findings"]]
        self.assertIn("statcheck-inconsistent-decision", codes)
        self.assertEqual(r["counts"]["error"], 1)

    def test_consistent_is_clean(self):
        r = stats.audit_text("t(38) = 2.50, p = 0.017.")
        self.assertEqual(r["counts"]["error"], 0)
        self.assertEqual(r["counts"]["warning"], 0)

    def test_grim_impossible(self):
        r = stats.audit_text("Mean = 3.15, N = 4.")
        self.assertIn("grim-inconsistent", [f["code"] for f in r["findings"]])

    def test_impossible_correlation(self):
        r = stats.audit_text("The correlation was r = 1.7 overall.")
        self.assertIn("impossible-correlation", [f["code"] for f in r["findings"]])


# --- Axis B: claim grounding ----------------------------------------------

class TestClaimGrounding(unittest.TestCase):
    def test_unsourced_claim_flagged(self):
        r = claim.audit_text("The prevalence was 34% in 2019.")
        self.assertEqual(r["counts"]["error"], 1)
        self.assertEqual(r["claims_grounded"], 0)

    def test_grounded_claim_passes(self):
        r = claim.audit_text("Mortality fell by 5% [3].")
        self.assertEqual(r["counts"]["error"], 0)
        self.assertEqual(r["claims_grounded"], 1)

    def test_ragas_probe_is_bool(self):
        self.assertIsInstance(claim.ragas_available(), bool)


# --- Axis D: hallucination signals ----------------------------------------

class TestHallucination(unittest.TestCase):
    def test_malformed_doi_is_error(self):
        r = halluc.audit_text("See doi: not-a-real-doi for details.")
        self.assertIn("malformed-doi", [f["code"] for f in r["findings"]])
        self.assertEqual(r["counts"]["error"], 1)

    def test_suspicious_pmid(self):
        r = halluc.audit_text("Reported in PMID: 1234567890.")
        self.assertIn("suspicious-pmid", [f["code"] for f in r["findings"]])

    def test_overcertainty(self):
        r = halluc.audit_text("This proves definitively that it works.")
        self.assertIn("over-certainty", [f["code"] for f in r["findings"]])

    def test_universal_quantifier(self):
        r = halluc.audit_text("All studies show the same benefit.")
        self.assertIn("universal-quantifier", [f["code"] for f in r["findings"]])


class TestSemanticEntropy(unittest.TestCase):
    def test_clustering_math(self):
        demo = ["Paris", "The capital is Paris", "Lyon", "Paris.", "It is Lyon"]
        same = lambda a, b: a.strip(". ").lower().replace("the capital is ", "").replace("it is ", "") \
            == b.strip(". ").lower().replace("the capital is ", "").replace("it is ", "")
        out = sement.semantic_entropy("q", n=len(demo), generate=lambda p, k: demo, entails=same)
        self.assertEqual(out["n_clusters"], 2)
        self.assertGreater(out["entropy"], 0)


# --- Axis G: Turkish scientific writing ------------------------------------

class TestTurkishAudit(unittest.TestCase):
    def _issues(self, text, strictness="certification"):
        lines = trsci.strip_qmd_noise(text)
        paras = trsci.build_paragraphs(lines)
        return trsci.detect_issues(lines, paras, strictness, set(trsci.COMMON_ABBREVIATIONS))

    def test_decimal_dot_pvalue_is_error(self):
        issues = self._issues("Sonuç anlamlıydı (p < 0.05).")
        codes = [i.severity + ":" + i.code for i in issues]
        self.assertIn("error:decimal-dot-p-value", codes)

    def test_first_person_register(self):
        issues = self._issues("Bu çalışmada ilişkiyi inceledik.")
        self.assertIn("first-person-register", [i.code for i in issues])

    def test_missing_diacritic(self):
        issues = self._issues("Bu calisma önemlidir.")
        self.assertIn("missing-diacritic", [i.code for i in issues])

    def test_causal_overclaim(self):
        issues = self._issues("Ebeveyn tutumu depresyona neden olur.")
        self.assertIn("causal-overclaim", [i.code for i in issues])

    def test_atesman_score_present(self):
        lines = trsci.strip_qmd_noise("Bu bir örnek cümledir. İkinci cümle de vardır.")
        paras = trsci.build_paragraphs(lines)
        m = trsci.calculate_metrics(paras)
        self.assertIsNotNone(m.atesman_score)

    def test_providers_skip_by_default(self):
        report = trsci.audit_text("Bir örnek metin.", "quick")
        statuses = {p.provider: p.status for p in report.providers}
        self.assertEqual(statuses["tdk"], "skipped")
        self.assertEqual(statuses["gecturk"], "skipped")
        # llm judge stub must never send text
        self.assertEqual(statuses["llm-judge"], "skipped")

    def test_grok_flag_sends_no_text(self):
        cfg = trsci.ExternalConfig(enable_grok=True)
        report = trsci.audit_text("Metin.", "quick", external_config=cfg)
        judge = [p for p in report.providers if p.provider == "llm-judge"][0]
        self.assertEqual(judge.status, "unavailable")
        self.assertEqual(judge.findings, [])

    def test_extra_abbreviations_whitelist(self):
        # A project abbreviation added via whitelist should not be flagged.
        text = "EMBU ölçeği kullanıldı."
        without = self._issues(text)
        lines = trsci.strip_qmd_noise(text)
        paras = trsci.build_paragraphs(lines)
        with_wl = trsci.detect_issues(lines, paras, "certification",
                                      set(trsci.COMMON_ABBREVIATIONS) | {"EMBU"})
        codes_without = [i.evidence for i in without if i.code == "abbreviation-review"]
        codes_with = [i.evidence for i in with_wl if i.code == "abbreviation-review"]
        self.assertIn("EMBU", codes_without)
        self.assertNotIn("EMBU", codes_with)

    @unittest.skipUnless(
        importlib.util.find_spec("zemberek") is not None,
        "zemberek-python not installed (optional provider)",
    )
    def test_zemberek_runs_when_available(self):
        lines = [(1, "Bu bir örnek cümledir.")]
        paras = trsci.build_paragraphs(lines)
        result = trsci.run_zemberek_layer(paras, True)
        self.assertEqual(result.status, "ok")


# --- Hooks (subprocess, stdin JSON contract) -------------------------------

class TestHooks(unittest.TestCase):
    def test_user_prompt_submit_blocks_secret(self):
        proc = _run_hook("user_prompt_submit.py",
                         {"prompt": "my key is sk-ant-api03-" + "A" * 40})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("secret", proc.stderr.lower())

    def test_user_prompt_submit_allows_clean(self):
        proc = _run_hook("user_prompt_submit.py", {"prompt": "audit this paragraph"})
        self.assertEqual(proc.returncode, 0)

    def test_pre_tool_use_denies_rm_rf_root(self):
        proc = _run_hook("pre_tool_use_policy.py",
                         {"tool_input": {"command": "rm -rf /"}})
        out = json.loads(proc.stdout)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_pre_tool_use_denies_env_read(self):
        proc = _run_hook("pre_tool_use_policy.py",
                         {"tool_input": {"command": "cat .env"}})
        out = json.loads(proc.stdout)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_pre_tool_use_allows_normal(self):
        proc = _run_hook("pre_tool_use_policy.py",
                         {"tool_input": {"command": "python3 audit.py file.md"}})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "")

    def test_session_start_injects_context(self):
        proc = _run_hook("session_start.py", {"hook_event_name": "SessionStart"})
        out = json.loads(proc.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("no-fabrication", ctx.lower())

    def test_post_tool_use_flags_secret(self):
        proc = _run_hook("post_tool_use_review.py",
                         {"tool_response": "token=ghp_" + "b" * 40})
        out = json.loads(proc.stdout)
        self.assertIn("secret", out["hookSpecificOutput"]["additionalContext"].lower())

    def test_stop_blocks_turkish_pvalue_dot(self):
        proc = _run_hook("stop_verify.py",
                         {"last_assistant_message": "Sonuç şu şekildeydi: p < 0.05 bulundu ve anlamlıydı."})
        out = json.loads(proc.stdout)
        self.assertEqual(out.get("decision"), "block")
        self.assertIn("G5", out["reason"])

    def test_stop_blocks_unsourced_numeric(self):
        proc = _run_hook("stop_verify.py",
                         {"last_assistant_message": "The mortality rate was 34% across cohorts."})
        out = json.loads(proc.stdout)
        self.assertEqual(out.get("decision"), "block")

    def test_stop_allows_sourced(self):
        proc = _run_hook("stop_verify.py",
                         {"last_assistant_message": "The rate was 34% in 2019 (Smith et al., 2019) [3]."})
        out = json.loads(proc.stdout)
        self.assertTrue(out.get("continue"))

    def test_stop_loop_guard(self):
        proc = _run_hook("stop_verify.py",
                         {"stop_hook_active": True, "last_assistant_message": "34% unsourced"})
        out = json.loads(proc.stdout)
        self.assertTrue(out.get("continue"))


class TestFleetIdentity(unittest.TestCase):
    """Bibliographic trio must share Evidentia's CureoHub HP self-host URLs (2026-08-17)."""

    def test_lock_points_at_cureonics_hub_not_third_party(self):
        lock_path = os.path.join(PLUGIN_ROOT, "fleet.lock.json")
        with open(lock_path, encoding="utf-8") as fh:
            lock = json.load(fh)
        blob = json.dumps(lock)
        self.assertNotIn("caseyjhand.com", blob)
        self.assertNotIn("pipeworx.io", blob)
        self.assertNotIn("workers.dev", blob)
        by_name = {s["name"]: s for s in lock["servers"]}
        self.assertEqual(by_name["pubmed"]["url"], "https://pubmed.mcp.claude.com/mcp")
        self.assertIsNone(by_name["pubmed"]["auth_env"])
        self.assertEqual(
            by_name["pubmed-epmc"]["url"],
            "https://pubmed.cureonics.com/mcp",
        )
        self.assertEqual(by_name["pubmed-epmc"]["auth_env"], "PUBMED_MCP_API_KEY")
        self.assertEqual(
            by_name["openalex"]["url"],
            "https://openalex.cureonics.com/mcp",
        )
        self.assertEqual(by_name["openalex"]["auth_env"], "OPENALEX_MCP_API_KEY")
        self.assertEqual(
            by_name["semantic-scholar"]["url"],
            "https://semanticscholar.cureonics.com/mcp",
        )
        self.assertEqual(
            by_name["semantic-scholar"]["auth_env"],
            "SEMANTICSCHOLAR_MCP_API_KEY",
        )


if __name__ == "__main__":
    unittest.main()
