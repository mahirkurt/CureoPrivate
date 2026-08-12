#!/usr/bin/env python3
"""historia-medicinae hook testleri — stdlib unittest, ağ yok.

    python3 hooks/test_hooks.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent / "scripts"


def run(script, payload):
    """Hook'u çalıştır ve İNSAN-OKUNUR metni döndür.

    Hook'lar JSON basar ve Türkçe karakterler kaçırılmış olabilir; assertion'ların
    ham \\u0130 dizgesi üzerinde çalışmaması için burada çözülür.
    """
    p = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30,
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


def transcript(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    f.write(json.dumps({"message": {"role": "assistant",
                                    "content": [{"type": "text", "text": text}]}}) + "\n")
    f.close()
    return f.name


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
                  {"tool_name": "mcp__literatur__search_articles", "tool_response": "A" * 8000})
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
                  "stop_coverage.py", "anachronism_guard.py"):
            p = subprocess.run([sys.executable, str(SCRIPTS / s)],
                               input="}{bozuk", capture_output=True, text=True, timeout=30)
            self.assertEqual(p.returncode, 0, f"{s} bozuk girdide patladı")


if __name__ == "__main__":
    unittest.main(verbosity=2)
