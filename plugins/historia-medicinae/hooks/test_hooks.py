#!/usr/bin/env python3
"""historia-medicinae hook testleri — stdlib unittest, ağ yok.

    python3 hooks/test_hooks.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent / "scripts"


def run(script, payload, env=None):
    """Hook'u çalıştır ve İNSAN-OKUNUR metni döndür.

    Hook'lar JSON basar ve Türkçe karakterler kaçırılmış olabilir; assertion'ların
    ham \\u0130 dizgesi üzerinde çalışmaması için burada çözülür.
    """
    e = os.environ.copy()
    if env:
        e.update(env)
    p = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        env=e,
    )
    out = p.stdout.strip()
    if not out:
        return ""
    try:
        obj = json.loads(out)
    except json.JSONDecodeError:
        return out          # düz metin hook'u (retrieve_dont_dump)
    if isinstance(obj, dict):
        if "reason" in obj:
            return obj["reason"]
        hso = obj.get("hookSpecificOutput") or {}
        if "additionalContext" in hso:
            return hso["additionalContext"]
    return out


def run_json(script, payload, env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    p = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        env=e,
    )
    out = p.stdout.strip()
    parsed = None
    if out:
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            parsed = {"_raw": out}
    return p.returncode, parsed


def decision(j):
    if not j:
        return "ALLOW"
    hso = j.get("hookSpecificOutput") or {}
    if hso.get("permissionDecision") == "deny":
        return "DENY"
    if j.get("systemMessage") or hso.get("additionalContext"):
        return "MSG"
    return "ALLOW"


def _asst(text=None, mcp_tool=None):
    blocks = []
    if mcp_tool:
        blocks.append({"type": "tool_use", "name": mcp_tool, "input": {}})
    if text is not None:
        blocks.append({"type": "text", "text": text})
    return {"message": {"role": "assistant", "content": blocks}}


def _tool_result():
    """Araç sonucu — GERÇEK transkriptte role='user' olarak kaydedilir.
    Tur sınırı SAYILMAZ; fixture'lar bunu içermezse sınır mantığı test edilmemiş olur."""
    return {"message": {"role": "user",
                        "content": [{"type": "tool_result", "content": "ok"}]}}


def _user(text):
    return {"message": {"role": "user", "content": [{"type": "text", "text": text}]}}


def _write(records):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for r in records:
        f.write(json.dumps(r) + "\n")
    f.close()
    return f.name


def transcript(text, mcp=True):
    """Tek turluk transkript. mcp=True → connector çağrısı yapılmış sayılır
    (meta-tur baskılayıcısı susturmasın diye); mcp=False → meta-tur."""
    return _write([_user("soru"),
                   _asst(mcp_tool="mcp__openalex__openalex_search_entities" if mcp else None),
                   _tool_result(),
                   _asst(text=text)])


class SessionStart(unittest.TestCase):
    def test_emits_context(self):
        ctx = run("session_start.py", {})
        self.assertIn("historia-medicinae", ctx)

    def test_names_the_three_traps(self):
        ctx = run("session_start.py", {})
        for trap in ("RETROSPEKTİF TANI", "PRESENTİZM", "DİFÜZYONİZM"):
            self.assertIn(trap, ctx)

    def test_declares_permanent_blocks(self):
        ctx = run("session_start.py", {})
        self.assertIn("Library of Congress", ctx)
        self.assertIn("histmed:", ctx)  # doc_id ön-eki


class RetrieveDontDump(unittest.TestCase):
    def test_small_payload_silent(self):
        self.assertEqual(run("retrieve_dont_dump.py",
                             {"tool_name": "mcp__openalex__x", "tool_response": "kısa"}), "")

    def test_tier1_threshold(self):
        out = run("retrieve_dont_dump.py",
                  {"tool_name": "mcp__literatur__tr_literatur_search_articles", "tool_response": "A" * 8000})
        self.assertIn("tarih-tarama-distilleri", out)

    def test_tier2_threshold_and_prefix(self):
        out = run("retrieve_dont_dump.py",
                  {"tool_name": "mcp__openathens__oa_fetch_fulltext",
                   "tool_response": "A" * 40000})
        self.assertIn("anamnesis", out)
        self.assertIn("histmed:", out)

    def test_measured_trap_find_equivalent(self):
        out = run("retrieve_dont_dump.py",
                  {"tool_name": "mcp__med-terminologies__find_equivalent",
                   "tool_response": {"a": 1}})
        self.assertIn("match_score", out)

    def test_measured_trap_iiif_ordering(self):
        out = run("retrieve_dont_dump.py",
                  {"tool_name": "mcp__ottoman-archives__ottoman_search_iiif",
                   "tool_response": {"a": 1}})
        self.assertIn("Osmanlı-öncelikli", out)


class StopCoverage(unittest.TestCase):
    def test_short_answer_silent(self):
        self.assertEqual(run("stop_coverage.py",
                             {"transcript_path": transcript("kısa yanıt")}), "")

    def test_substantive_without_manifest_blocks(self):
        t = transcript("MORBUS modu tıp tarihi birincil kaynak taraması. " * 40)
        out = run("stop_coverage.py", {"transcript_path": t})
        self.assertIn("G0", out)

    def test_manifest_present_passes(self):
        body = ("MORBUS modu tıp tarihi birincil kaynak. " * 40 +
                "Kapsam Manifestosu (G0) " +
                " ".join(f"server{i} hit {i}" for i in range(1, 10)))
        self.assertEqual(run("stop_coverage.py", {"transcript_path": transcript(body)}), "")

    def test_loop_guard(self):
        t = transcript("MORBUS modu tıp tarihi birincil kaynak taraması. " * 40)
        self.assertEqual(run("stop_coverage.py",
                             {"transcript_path": t, "stop_hook_active": True}), "")


class AnachronismGuard(unittest.TestCase):
    def test_teleology_flagged(self):
        t = transcript("Tıp tarihi 19. yüzyıl salgın arşiv incelemesi. "
                       "Hekimler henüz mikrop teorisini bulamamışlardı. " * 20)
        self.assertIn("TELEOLOJİ", run("anachronism_guard.py", {"transcript_path": t}))

    def test_unhedged_modern_dx_flagged(self):
        t = transcript("Tıp tarihi 19. yüzyıl salgın arşiv incelemesi. "
                       "Hastalık tüberküloz idi ve yayıldı. " * 20)
        self.assertIn("RETROSPEKTİF", run("anachronism_guard.py", {"transcript_path": t}))

    def test_hedged_dx_passes(self):
        t = transcript("Tıp tarihi 19. yüzyıl salgın arşiv incelemesi. Kaynak consumption der; "
                       "tüberküloz okuması bir hipotezdir, ayırıcı tanı yazılmıştır. " * 20)
        self.assertEqual(run("anachronism_guard.py", {"transcript_path": t}), "")

    def test_missing_dual_date_flagged(self):
        t = transcript("Tıp tarihi arşiv incelemesi 19. yüzyıl dönem salgın. "
                       "Belge H. 1265 tarihlidir ve kayıt böyle geçer. " * 20)
        self.assertIn("ÇİFT TARİH", run("anachronism_guard.py", {"transcript_path": t}))

    def test_non_history_output_silent(self):
        t = transcript("Bu bir yazılım mimarisi tartışmasıdır. " * 60)
        self.assertEqual(run("anachronism_guard.py", {"transcript_path": t}), "")

    def test_malformed_input_fail_open(self):
        for s in ("session_start.py", "retrieve_dont_dump.py",
                  "stop_coverage.py", "anachronism_guard.py",
                  "anamnesis_guard.py", "anamnesis_ledger.py",
                  "anamnesis_lifecycle.py"):
            p = subprocess.run([sys.executable, str(SCRIPTS / s)],
                               input="}{bozuk", capture_output=True, text=True, timeout=30)
            self.assertEqual(p.returncode, 0, f"{s} bozuk girdide patladı")


ANAM_RUN = "aabbccddeeff"
ANAM_PREFIX = f"hmrun:{ANAM_RUN}:"
ANAM_COLL = f"histmed:run:{ANAM_RUN}"


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _anam_env(docs=None):
    tmp = tempfile.mkdtemp()
    ledger = os.path.join(tmp, "ledger.json")
    log = os.path.join(tmp, "forget.jsonl")
    payload = {
        "run_id": ANAM_RUN,
        "collection": ANAM_COLL,
        "prefix": ANAM_PREFIX,
        "doc_ids": list(docs or []),
        "pending_forget": [],
        "status": "active",
    }
    with open(ledger, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    env = {
        "HISTMED_ANAMNESIS_LEDGER": ledger,
        "HISTMED_ANAMNESIS_FORGET_LOG": log,
        "HISTMED_ANAMNESIS_NO_NETWORK": "1",
        "CLAUDE_PROJECT_DIR": tmp,
    }
    return env, ledger, log


class Anamnesis(unittest.TestCase):
    def setUp(self):
        self.env, self.ledger, self.log = _anam_env()
        self.scoped = ANAM_PREFIX + "doi/10.1234/arnold"
        self.foreign = "doi:10.9999/foreign-chunk"

    def _g(self, tool, inp=None, env=None):
        payload = {"tool_name": tool}
        if inp is not None:
            payload["tool_input"] = inp
        _, j = run_json("anamnesis_guard.py", payload, env or self.env)
        return decision(j), j

    def test_guard_matrix(self):
        cases = [
            ("mcp__anamnesis__ingest_document", None, "DENY"),
            ("mcp__anamnesis__ingest_document",
             {"doc_id": "histmed:doi/10.1234/arnold"}, "DENY"),
            ("mcp__anamnesis__ingest_document",
             {"collection": ANAM_COLL, "doc_id": self.scoped}, "ALLOW"),
            ("mcp__anamnesis__hybrid_query", {"query": "cholera"}, "DENY"),
            ("mcp__anamnesis__hybrid_query",
             {"query": "cholera", "collection": ANAM_COLL}, "ALLOW"),
            ("mcp__anamnesis__hybrid_query",
             {"query": "x", "collection": "histmed:run:ffffffffffff"}, "DENY"),
            ("mcp__anamnesis__hybrid_query",
             {"query": "x", "collection": "evidentia:run:ffffffffffff"}, "ALLOW"),
            ("mcp__anamnesis__hybrid_query",
             {"query": "x", "collection": "cureolex:sess:aabbccddeeff"}, "ALLOW"),
            ("mcp__anamnesis__graph_neighbors", {"node": "hekim:x"}, "DENY"),
            ("mcp__anamnesis__graph_neighbors",
             {"node": "hekim:x", "collection": ANAM_COLL}, "ALLOW"),
            ("mcp__anamnesis__subgraph", {"entities": ["x"]}, "DENY"),
            ("mcp__anamnesis__subgraph",
             {"entities": ["x"], "collection": ANAM_COLL}, "ALLOW"),
            ("mcp__anamnesis__semantic_search", {"query": "x"}, "DENY"),
            ("mcp__anamnesis__semantic_search",
             {"query": "x", "collection": ANAM_COLL}, "ALLOW"),
            ("mcp__anamnesis__semantic_search",
             {"query": "x", "doc_ids": [self.scoped]}, "ALLOW"),
            ("mcp__anamnesis__forget_document", {"doc_id": self.foreign}, "DENY"),
            ("mcp__anamnesis__forget_document", {"doc_id": self.scoped}, "ALLOW"),
            ("mcp__anamnesis__forget_collection",
             {"collection": "histmed:run:ffffffffffff"}, "DENY"),
            ("mcp__anamnesis__forget_collection",
             {"collection": "evidentia:run:ffffffffffff"}, "ALLOW"),
            ("mcp__anamnesis__forget_collection",
             {"collection": ANAM_COLL}, "ALLOW"),
            ("mcp__anamnesis__corpus_stats", {}, "ALLOW"),
            ("mcp__anamnesis__list_docs", {"collection": ANAM_COLL}, "ALLOW"),
            ("mcp__claude_ai_PubMed__search_articles", None, "ALLOW"),
        ]
        for tool, inp, want in cases:
            got, j = self._g(tool, inp)
            self.assertEqual(got, want, f"{tool} {inp} → {got} != {want}")
            if want == "DENY":
                reason = ((j or {}).get("hookSpecificOutput") or {}).get(
                    "permissionDecisionReason", "")
                self.assertTrue(
                    "anamnesis" in reason.lower() or "münhasır" in reason,
                    f"deny reason missing münhasır: {reason!r}",
                )

    def test_disable_flag(self):
        off = tempfile.mkdtemp()
        os.makedirs(os.path.join(off, ".claude"))
        open(os.path.join(off, ".claude", "histmed-anamnesis.off"), "w").close()
        got, _ = self._g("mcp__anamnesis__hybrid_query", {"query": "x"},
                         {**self.env, "CLAUDE_PROJECT_DIR": off})
        self.assertEqual(got, "ALLOW")

    def test_ledger_records_own_drops_foreign(self):
        env, ledger, _ = _anam_env()
        _, j = run_json("anamnesis_ledger.py", {
            "tool_name": "mcp__plugin-historia-medicinae-anamnesis__ingest_document",
            "tool_input": {
                "doc_id": self.scoped, "collection": ANAM_COLL, "text": "body",
            },
            "tool_result": json.dumps({"doc_id": self.scoped, "chunks": 3}),
        }, env)
        self.assertIn(self.scoped, _read_json(ledger).get("doc_ids") or [])
        self.assertEqual(decision(j), "MSG")
        run_json("anamnesis_ledger.py", {
            "tool_name": "mcp__anamnesis__ingest_document",
            "tool_input": {"doc_id": self.foreign, "text": "nsclc"},
            "tool_result": "{}",
        }, env)
        self.assertNotIn(self.foreign, _read_json(ledger).get("doc_ids") or [])
        run_json("anamnesis_ledger.py", {
            "tool_name": "mcp__anamnesis__forget_document",
            "tool_input": {"doc_id": self.scoped},
            "tool_result": json.dumps({"existed": True}),
        }, env)
        self.assertNotIn(self.scoped, _read_json(ledger).get("doc_ids") or [])

    def test_startup_rotates_and_stub_forgets(self):
        env, ledger, log = _anam_env(docs=[self.scoped])
        _, j = run_json("anamnesis_lifecycle.py", {
            "hook_event_name": "SessionStart",
            "source": "startup",
        }, env)
        after = _read_json(ledger)
        self.assertNotEqual(after.get("run_id"), ANAM_RUN)
        self.assertNotIn(self.scoped, after.get("doc_ids") or [])
        self.assertIn(self.scoped, Path(log).read_text(encoding="utf-8"))
        ctx = ((j or {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
        self.assertIn(after.get("prefix", ""), ctx)

    def test_resume_and_compact_keep(self):
        env, ledger, log = _anam_env(docs=[self.scoped])
        run_json("anamnesis_lifecycle.py", {
            "hook_event_name": "SessionStart", "source": "resume",
        }, env)
        self.assertEqual(_read_json(ledger).get("run_id"), ANAM_RUN)
        self.assertFalse(os.path.isfile(log) and open(log, encoding="utf-8").read().strip())

        env2, ledger2, _ = _anam_env(docs=[self.scoped])
        run_json("anamnesis_lifecycle.py", {
            "hook_event_name": "SessionStart", "source": "compact",
        }, env2)
        led = _read_json(ledger2)
        self.assertEqual(led.get("run_id"), ANAM_RUN)
        self.assertIn(self.scoped, led.get("doc_ids") or [])

    def test_session_end_forgets_own_only(self):
        env, ledger, log = _anam_env(docs=[self.scoped])
        poisoned = _read_json(ledger)
        poisoned["doc_ids"] = [self.scoped, self.foreign]
        with open(ledger, "w", encoding="utf-8") as fh:
            json.dump(poisoned, fh)
        run_json("anamnesis_lifecycle.py", {"hook_event_name": "SessionEnd"}, env)
        logged = Path(log).read_text(encoding="utf-8") if os.path.isfile(log) else ""
        self.assertIn(self.scoped, logged)
        self.assertNotIn(self.foreign, logged)
        self.assertFalse(_read_json(ledger).get("doc_ids"))

    def test_empty_session_end_no_stub(self):
        env, _, log = _anam_env(docs=[])
        rc, _ = run_json("anamnesis_lifecycle.py",
                         {"hook_event_name": "SessionEnd"}, env)
        self.assertEqual(rc, 0)
        self.assertFalse(os.path.isfile(log) and open(log, encoding="utf-8").read().strip())

    def test_flagship_remints_subcommand_does_not(self):
        env, ledger, log = _anam_env(docs=[self.scoped])
        run_json("anamnesis_lifecycle.py", {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "/historia-medicinae:kaynak-avi cholera",
        }, env)
        self.assertEqual(_read_json(ledger).get("run_id"), ANAM_RUN)
        _, j = run_json("anamnesis_lifecycle.py", {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "/historia-medicinae cholera 1817",
        }, env)
        after = _read_json(ledger)
        self.assertNotEqual(after.get("run_id"), ANAM_RUN)
        self.assertIn(self.scoped, Path(log).read_text(encoding="utf-8"))
        ctx = ((j or {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
        self.assertIn(after.get("prefix", ""), ctx)

    def test_stop_does_not_forget(self):
        env, _, log = _anam_env(docs=[self.scoped])
        run_json("anamnesis_lifecycle.py", {"hook_event_name": "Stop"}, env)
        self.assertFalse(os.path.isfile(log) and open(log, encoding="utf-8").read().strip())
        hooks = json.loads(
            (Path(__file__).resolve().parent / "hooks.json").read_text(encoding="utf-8")
        )
        stop_cmds = [
            h.get("command") or ""
            for block in hooks.get("hooks", {}).get("Stop", [])
            for h in block.get("hooks", [])
        ]
        self.assertFalse(any("anamnesis" in c for c in stop_cmds))



def multi_turn(*turns, mcp_last=True):
    """turns: ('assistant'|'user', metin). Son asistan turuna mcp çağrısı eklenir."""
    recs = []
    for k, (role, text) in enumerate(turns):
        if role == "user":
            recs.append(_user(text))
        else:
            last = k == len(turns) - 1
            recs.append(_asst(mcp_tool=("mcp__openalex__openalex_search_entities"
                                        if (last and mcp_last) else None)))
            recs.append(_tool_result())
            recs.append(_asst(text=text))
    return _write(recs)


class TurnBoundary(unittest.TestCase):
    """REGRESYON: kapılar YALNIZ son turu yargılar.

    Kusur (2026-08-13): transcript_text kullanıcı mesajında durmuyordu; uzun bir
    oturumda depo-bakımı turu, önceki tıp tarihi turlarından alan sinyali miras
    alıp G0/anakronizm kapılarını yanlış-pozitif ateşliyordu.
    """

    RESEARCH = ("MORBUS modu tıp tarihi birincil kaynak taraması retrospektif tanı. " * 40)
    MAINT = ("Marketplace kayıtlarını ve README dosyalarını güncelledim; sürüm "
             "referansları ve displayName alanları düzeltildi. " * 25)

    def test_coverage_gate_ignores_previous_research_turn(self):
        t = multi_turn(("assistant", self.RESEARCH),
                       ("user", "marketplace kayıtlarını güncelle"),
                       ("assistant", self.MAINT))
        self.assertEqual(run("stop_coverage.py", {"transcript_path": t}), "",
                         "önceki turun alan sinyali bakım turuna sızdı")

    def test_anachronism_gate_ignores_previous_research_turn(self):
        bad_prev = ("Tıp tarihi 19. yüzyıl salgın arşiv. Hastalık tüberküloz idi. "
                    "Hekimler henüz mikrop teorisini bulamamışlardı. " * 20)
        t = multi_turn(("assistant", bad_prev),
                       ("user", "readme güncelle"),
                       ("assistant", self.MAINT))
        self.assertEqual(run("anachronism_guard.py", {"transcript_path": t}), "",
                         "önceki turun ihlali bakım turuna sızdı")

    def test_still_fires_on_current_research_turn(self):
        """Sınır daraltması kapıyı KÖRLEŞTİRMEMELİ."""
        t = multi_turn(("user", "kolera pandemisini araştır"),
                       ("assistant", self.RESEARCH))
        self.assertIn("G0", run("stop_coverage.py", {"transcript_path": t}))


class MetaTurnSuppressor(unittest.TestCase):
    """Filo/mod adlarını ANAN ama connector ÇAĞIRMAYAN tur araştırma değildir."""

    META = ("MORBUS modu için tıp tarihi birincil kaynak taramasını anlatan CHANGELOG "
            "maddesini yazdım; retrospektif tanı kapısı da belgelendi. " * 25)

    def test_meta_turn_silent_in_coverage_gate(self):
        self.assertEqual(run("stop_coverage.py",
                             {"transcript_path": transcript(self.META, mcp=False)}), "",
                         "connector çağırmayan dokümantasyon turu G0 istedi")

    def test_meta_turn_silent_in_anachronism_gate(self):
        t = transcript("Tıp tarihi salgın arşiv 19. yüzyıl; hastalık tüberküloz idi ve "
                       "hekimler henüz mikrop teorisini bulamamışlardı. " * 20, mcp=False)
        self.assertEqual(run("anachronism_guard.py", {"transcript_path": t}), "",
                         "connector çağırmayan tur anakronizm kapısını tetikledi")

    def test_same_text_WITH_connector_calls_still_fires(self):
        """Baskılayıcı yalnız çağrısızlığa bakar — metne değil."""
        self.assertIn("G0", run("stop_coverage.py",
                                {"transcript_path": transcript(self.META, mcp=True)}))


class ToolResultIsNotTurnBoundary(unittest.TestCase):
    """REGRESYON: araç sonuçları role='user' taşır ama TUR SINIRI DEĞİLDİR.

    İlk onarım 'ilk user kaydında dur' diyordu; araç çağrısı olan turda bu, asistan
    metni toplanmadan durmak demekti — kapıyı kapsamak yerine KÖRLEŞTİRİRDİ.
    """

    def test_text_after_tool_results_is_still_collected(self):
        body = "MORBUS tıp tarihi birincil kaynak retrospektif tanı taraması. " * 40
        recs = [_user("kolera araştır"),
                _asst(mcp_tool="mcp__openalex__openalex_search_entities"), _tool_result(),
                _asst(mcp_tool="mcp__pubmed-epmc__pubmed_search_articles"), _tool_result(),
                _asst(text=body)]
        out = run("stop_coverage.py", {"transcript_path": _write(recs)})
        self.assertIn("G0", out, "tool_result tur sınırı sanıldı; metin toplanmadı")

if __name__ == "__main__":
    unittest.main(verbosity=2)
