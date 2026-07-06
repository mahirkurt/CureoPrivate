#!/usr/bin/env python3
"""lex-sanitas hook harness — 4 hook'un davranış matrisi (bağımlılıksız, stdlib).

Çalıştırma: python3 hooks/test_hooks.py  (plugin kökünden)
Her vaka hook'u gerçek subprocess olarak, gerçek stdin sözleşmesiyle çağırır.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")
PASS, FAIL = 0, 0


def run(script, payload, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30, env=env,
    )
    out = None
    if r.stdout.strip():
        try:
            out = json.loads(r.stdout)
        except Exception:
            out = {"_raw": r.stdout}
    return r.returncode, out


def check(name, cond, detail=""):
    global PASS, FAIL
    status = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not cond else ""))


print("== session_start.py ==")
rc, out = run("session_start.py", {})
ctx = (out or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
check("çıkış 0 + geçerli hook JSON", rc == 0 and bool(ctx))
check("konvansiyon enjeksiyonu (TAM-FİLO + NO-FABRICATION + companion zorunluluğu)",
      all(s in ctx for s in ("TAM-FİLO", "NO-FABRICATION", "ZORUNLU üyeleridir")))
check("delegasyon kurulum algısı satırı", "[preflight/delegasyon]" in ctx or "KURULU" in ctx)
rc, out = run("session_start.py", {}, env_extra={"MEVZUAT_MCP_API_KEY": ""})
ctx2 = (out or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
check("eksik anahtar preflight uyarısı (mevzuat)", "MEVZUAT_MCP_API_KEY" in ctx2)

print("== scope_guard.py (UserPromptSubmit) ==")
rc, out = run("scope_guard.py", {"prompt": "SGK ödeme reddi davam için itiraz dilekçesi yaz"})
check("kapsam-dışı (bireysel dava) → uyarı/yönlendirme", out is not None and rc == 0,
      f"rc={rc} out={str(out)[:80]}")
rc, out = run("scope_guard.py", {"prompt": "ATMP yönetmelik taslağı hazırla"})
check("kapsam-içi (reform) → sessiz geçiş", rc == 0 and (out is None or not (out or {}).get("decision")))

print("== retrieve_dont_dump.py (PostToolUse) ==")
small = {"tool_name": "mcp__mevzuat__search_mevzuat", "tool_response": {"content": [{"type": "text", "text": "kısa sonuç"}]}}
rc, out = run("retrieve_dont_dump.py", small)
check("küçük çıktı → sessiz", rc == 0 and (out is None or not out))
big = {"tool_name": "mcp__mevzuat__get_mevzuat_text", "tool_response": {"content": [{"type": "text", "text": "X" * 8000}]}}
rc, out = run("retrieve_dont_dump.py", big)
check("6KB+ çıktı → devre-kesici uyarısı", rc == 0 and out is not None and bool(str(out)),
      f"rc={rc} out={str(out)[:80]}")
huge = {"tool_name": "mcp__mevzuat__get_mevzuat_text", "tool_response": {"content": [{"type": "text", "text": "X" * 40000}]}}
rc, out = run("retrieve_dont_dump.py", huge)
check("30KB+ çıktı → anamnesis/Tier-2 yönlendirmesi", rc == 0 and "anamnesis" in str(out).lower())

print("== stop_coverage.py (Stop) ==")
rc, out = run("stop_coverage.py", {"last_assistant_message": "Bugün hava güzel.", "stop_hook_active": False})
check("lex-dışı tur → sessiz", rc == 0 and not out)
rc, out = run("stop_coverage.py", {"last_assistant_message": "MADDE 1 - ... gerekçe ... 5210 uyumlu yönetmelik taslağı", "stop_hook_active": False})
check("mod-çıktısı, manifesto+label YOK → block", (out or {}).get("decision") == "block")
partial = ("MADDE 1 - ... gerekçe ... Kapsam Manifestosu (G0): mevzuat → hit 3; titck → hit 1; "
           "confidence_label: combined_confidence MODERATE human_review_required:true")
rc, out = run("stop_coverage.py", {"last_assistant_message": partial, "stop_hook_active": False})
reason = (out or {}).get("reason", "")
check("manifesto var ama companion/delegasyon satırları eksik → block + isim listesi",
      (out or {}).get("decision") == "block" and all(x in reason for x in ("Yargı", "Open Law", "Ansvar", "evidentia", "sci-audit")))
full = ("MADDE 1 - ... gerekçe ... Kapsam Manifestosu (G0): mevzuat → hit 3; Yarg → hit 2; "
        "Open_Law → skipped: companion bağlı değil ⇒ G6 CONDITIONAL; Ansvar → empty; evidentia → hit; "
        "sci-audit → hit; confidence_label: combined_confidence MODERATE human_review_required:true")
rc, out = run("stop_coverage.py", {"last_assistant_message": full, "stop_hook_active": False})
check("tam çıktı-sözleşmesi → sessiz PASS", rc == 0 and not out)
rc, out = run("stop_coverage.py", {"last_assistant_message": "MADDE 1 gerekçe 5210", "stop_hook_active": True})
check("stop_hook_active döngü koruması → sessiz", rc == 0 and not out)

print(f"\nTOPLAM: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
