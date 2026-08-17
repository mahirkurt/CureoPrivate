#!/usr/bin/env python3
"""edupedia hook harness — SessionStart ve PostToolUse hook testleri (stdlib).

Çalıştırma: python3 hooks/test_hooks.py (plugin kökünden)
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE / "scripts"
ROOT = HERE.parent
PASS, FAIL = 0, 0

sys.path.insert(0, str(SCRIPTS))
import fleet_probe  # noqa: E402
import session_start  # noqa: E402
import validate_module_hook  # noqa: E402


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    status = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not cond else ""))


def run_hook(script_name: str, payload: dict, env_extra: dict | None = None) -> tuple[int, dict | None]:
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    res = subprocess.run(
        [sys.executable, str(SCRIPTS / script_name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    out = None
    if res.stdout.strip():
        try:
            out = json.loads(res.stdout)
        except Exception:
            out = {"_raw": res.stdout}
    return res.returncode, out


def main() -> None:
    print("== 1. fleet_probe.py (canlı prob sınıflandırması ve cache) ==")
    check("401 → unauthorized", fleet_probe.classify(401, "") == "unauthorized")
    check("403 → unauthorized", fleet_probe.classify(403, "") == "unauthorized")
    check("200 + result → ok", fleet_probe.classify(200, '{"jsonrpc":"2.0","id":1,"result":{"x":1}}') == "ok")
    check("200 + error → error", fleet_probe.classify(200, '{"jsonrpc":"2.0","id":1,"error":{"code":-1}}') == "error")
    check("503 → unreachable", fleet_probe.classify(503, "") == "unreachable")
    check("None → unreachable", fleet_probe.classify(None, "") == "unreachable")

    lock = fleet_probe.load_lock(ROOT)
    check("fleet.lock.json 2 server barındırıyor", bool(lock) and lock["counts"]["servers"] == 2)

    with tempfile.TemporaryDirectory() as td:
        cp = Path(td) / "test_cache.json"
        fleet_probe.write_cache(cp, {"s1": {"status": "ok"}})
        check("taze cache okunur", fleet_probe.read_cache(cp, ttl=86400) == {"s1": {"status": "ok"}})
        check("bayat cache None döner", fleet_probe.read_cache(cp, ttl=-1) is None)

    print("\n== 2. session_start.py (SessionStart Hook) ==")
    code, out = run_hook("session_start.py", {"source": "test"}, env_extra={"EDUPEDIA_PREFLIGHT_NO_PROBE": "1"})
    check("SessionStart sıfır çıkış kodu döner", code == 0)
    check("SessionStart structured output döner", bool(out and "hookSpecificOutput" in out))
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") if out else ""
    check("SessionStart konvansiyonları içerir", "[edupedia]" in ctx and "16 KALİTE KAPISI" in ctx and "maarif-mufredat" in ctx)

    print("\n== 3. validate_module_hook.py (PostToolUse Hook) ==")
    # non-html file -> no-op
    code, out = run_hook("validate_module_hook.py", {"tool_input": {"file_path": "/tmp/test.py"}})
    check("HTML olmayan dosyada sessiz kalır", code == 0 and out is None)

    # valid template html -> runs and succeeds silently
    template_path = str(ROOT / "skills" / "carbon-edupedia" / "assets" / "module-template.html")
    code, out = run_hook("validate_module_hook.py", {"tool_input": {"file_path": template_path}})
    check("Geçerli şablonda sıfır çıkış kodu ve sessiz/advisory dönüş", code == 0)

    # fail fixture -> surfaces advisory context
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8") as tf:
        tf.write("""<!DOCTYPE html><html lang="tr"><head><title>Test</title></head><body>
<script>const MODULE_DATA = { title: "Test 😀" };</script>
</body></html>""")
        tf.flush()
        code, out = run_hook("validate_module_hook.py", {"tool_input": {"file_path": tf.name}})
        check("İhlal içeren HTML'de advisory bağlam döner", code == 0 and out is not None and "G-EMOJI" in str(out))

    print(f"\nSonuç: {PASS} passed, {FAIL} failed")
    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
