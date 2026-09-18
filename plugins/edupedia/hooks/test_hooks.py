#!/usr/bin/env python3
"""edupedia hook harness — 1.0.0 SessionStart preflight testleri (stdlib, ağsız).

Çalıştırma: python3 plugins/edupedia/hooks/test_hooks.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE / "scripts"
ROOT = HERE.parent
PASS, FAIL = 0, 0
NO_PROBE = {"EDUPEDIA_PREFLIGHT_NO_PROBE": "1"}

sys.path.insert(0, str(SCRIPTS))
import fleet_probe  # noqa: E402
import hook_core  # noqa: E402


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def run_hook_raw(script_name: str, raw: str, env_extra: dict | None = None) -> tuple[int, dict | None]:
    env = dict(os.environ)
    env.update(env_extra or {})
    res = subprocess.run([sys.executable, str(SCRIPTS / script_name)], input=raw, capture_output=True,
                         text=True, timeout=30, env=env)
    out = None
    if res.stdout.strip():
        try:
            out = json.loads(res.stdout)
        except Exception:
            out = {"_raw": res.stdout}
    return res.returncode, out


def run_hook(script_name: str, payload: dict, env_extra: dict | None = None) -> tuple[int, dict | None]:
    return run_hook_raw(script_name, json.dumps(payload), env_extra)


def cursor_session_payload() -> dict:
    return {
        "conversation_id": "conv-edupedia-test",
        "generation_id": "gen-edupedia-test",
        "model": "gpt-test",
        "hook_event_name": "sessionStart",
        "cursor_version": "test",
        "workspace_roots": [str(ROOT)],
        "session_id": "cursor-session-test",
        "is_background_agent": False,
        "composer_mode": "agent",
    }


def main() -> None:
    print("== 1. fleet_probe.py (vendor'lı sınıflandırma, lock, önbellek) ==")
    check("401 → unauthorized", fleet_probe.classify(401, "") == "unauthorized")
    check("403 → unauthorized", fleet_probe.classify(403, "") == "unauthorized")
    check("200 + result → ok", fleet_probe.classify(200, '{"jsonrpc":"2.0","id":1,"result":{"x":1}}') == "ok")
    check("200 + error → error", fleet_probe.classify(200, '{"jsonrpc":"2.0","id":1,"error":{"code":-1}}') == "error")
    check("503 → unreachable", fleet_probe.classify(503, "") == "unreachable")
    check("None → unreachable", fleet_probe.classify(None, "") == "unreachable")

    lock = fleet_probe.load_lock(ROOT)
    check("fleet.lock.json 3 server barındırıyor", bool(lock) and lock["counts"]["servers"] == 3)
    tedy = next((s for s in (lock or {}).get("servers", []) if s.get("name") == "tedy"), {})
    check("tedy anahtarsız ve mcp.tedy.online'a işaret eder",
          tedy.get("auth_env") is None and tedy.get("url") == "https://mcp.tedy.online/mcp")

    with tempfile.TemporaryDirectory() as td:
        cp = Path(td) / "test_cache.json"
        fleet_probe.write_cache(cp, {"s1": {"status": "ok"}})
        check("taze cache okunur", fleet_probe.read_cache(cp, ttl=86400) == {"s1": {"status": "ok"}})
        check("bayat cache None döner", fleet_probe.read_cache(cp, ttl=-1) is None)

    with tempfile.TemporaryDirectory() as td:
        cp = Path(td) / "cureonics-fleet" / "edupedia.json"
        calls = []
        original_cache_path = fleet_probe._cache_path
        original_probe_fleet = fleet_probe.probe_fleet

        def fake_cache_path(_plugin=""):
            return cp

        def fake_probe_fleet(_lock, env):
            calls.append(env)
            return {"maarif-mufredat": {"name": "maarif-mufredat", "status": "ok"}}

        fleet_probe._cache_path = fake_cache_path
        fleet_probe.probe_fleet = fake_probe_fleet
        try:
            secret_one = "hook-cache-credential-one"
            secret_two = "hook-cache-credential-two"
            env_one = {"MUFREDAT_MCP_API_KEY": secret_one}
            fleet_probe.cached_probe(ROOT, env_one)
            fleet_probe.cached_probe(ROOT, env_one)
            check("aynı credential cache hit üretir", len(calls) == 1)

            fleet_probe.cached_probe(ROOT, {"MUFREDAT_MCP_API_KEY": secret_two})
            check("credential rotasyonu cache miss üretir", len(calls) == 2)

            fleet_probe.cached_probe(ROOT, {})
            fleet_probe.cached_probe(ROOT, {})
            check("missing credential durumu kendi içinde cache hit üretir", len(calls) == 3)

            raw_cache = cp.read_bytes() if cp.is_file() else b""
            check(
                "cache credential veya parçasını içermez",
                secret_one.encode() not in raw_cache
                and secret_two.encode() not in raw_cache
                and secret_two[:8].encode() not in raw_cache
                and secret_two[-8:].encode() not in raw_cache,
            )
            try:
                cache_doc = json.loads(raw_cache)
            except Exception:
                cache_doc = {}
            check(
                "cache schema + HMAC kimliği taşır",
                cache_doc.get("schema_version")
                == getattr(fleet_probe, "CACHE_SCHEMA_VERSION", None)
                and isinstance(cache_doc.get("auth_presence"), list)
                and len(cache_doc.get("credential_fingerprint", "")) == 64,
            )
        finally:
            fleet_probe._cache_path = original_cache_path
            fleet_probe.probe_fleet = original_probe_fleet

    print("\n== 2. hook_core — yalnız tedy yorumlanır ==")
    base = hook_core.build_context(lock, {})
    check("prob yoksa yalnız akış kuralları", base == hook_core.conventions(lock))
    check("kurallar orkestratör akışını taşır",
          all(w in base for w in ("[edupedia]", "tedy", "edupedia_rehber(bolum='akis')", "edupedia_derle",
                                  "edupedia_kapsam", "edupedia_yayinla", "kaynak_verisi")))
    check("kurallar yerel betiğe ve eski kapı sayısına işaret etmez",
          "scripts/" not in base and "16 KALİTE" not in base and "YEREL ÇIKTI" not in base)
    healthy = hook_core.build_context(lock, {
        "tedy": {"name": "tedy", "status": "unauthorized", "http": 401, "detail": ""},
        "maarif-mufredat": {"name": "maarif-mufredat", "status": "auth_missing", "http": None},
        "egitim-kaynak": {"name": "egitim-kaynak", "status": "unreachable", "http": None, "detail": "URLError"},
    })
    check("tedy 401 sağlıklı; isteğe bağlı bağlayıcılar raporlanmaz", healthy == base)
    open_gate = hook_core.build_context(lock, {"tedy": {"status": "ok", "http": 200}})
    check("kimliksiz 200 güvenlik uyarısı üretir", open_gate.startswith(base) and "GÜVENLİK" in open_gate)
    denied = hook_core.build_context(lock, {"tedy": {"status": "unauthorized", "http": 403}})
    check("403 erişim reddi olarak raporlanır", "HTTP 403" in denied and "GÜVENLİK" not in denied)
    down = hook_core.build_context(lock, {"tedy": {"status": "unreachable", "http": None, "detail": "URLError"}})
    check("erişilemeyen tedy dürüstçe raporlanır", "erişilemedi (URLError)" in down and "modül üretilemez" in down)
    unknown = hook_core.build_context(lock, {"tedy": {"status": "unknown", "http": None, "detail": "bütçe doldu"}})
    check("prob bütçesinin dolması erişilemedi sayılır", "erişilemedi (bütçe doldu)" in unknown)
    check("lock yoksa varsayılan uç yazılır", "https://mcp.tedy.online/mcp" in hook_core.conventions(None))

    print("\n== 3. session_start.py (Claude SessionStart) ==")
    code, out = run_hook("session_start.py", {"source": "test"}, env_extra=NO_PROBE)
    ctx = ((out or {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
    check("sıfır çıkış ve structured additionalContext", code == 0 and ctx.startswith("[edupedia]"))
    code, _ = run_hook_raw("session_start.py", "bozuk-json", env_extra=NO_PROBE)
    check("bozuk stdin'de fail-open sıfır çıkış", code == 0)

    print("\n== 4. cursor_session_start.py (Cursor sessionStart) ==")
    cursor_env = {"CURSOR_PLUGIN_ROOT": str(ROOT), **NO_PROBE}
    code, out = run_hook("cursor_session_start.py", cursor_session_payload(), env_extra=cursor_env)
    check("sıfır çıkış ve additional_context",
          code == 0 and bool(out) and str(out.get("additional_context", "")).startswith("[edupedia]"))
    check("Claude sarmalayıcısı döndürmez", out is not None and "hookSpecificOutput" not in out)
    code, out = run_hook_raw("cursor_session_start.py", "[]", env_extra=cursor_env)
    check("mapping olmayan girdide tam {} döner", code == 0 and out == {})

    print("\n== 5. önbellekteki tedy arızası bağlama girer (ağsız) ==")
    with tempfile.TemporaryDirectory() as td:
        cache_root = Path(td)
        cache_path = cache_root / "cureonics-fleet" / "edupedia.json"
        cred_env = {"MUFREDAT_MCP_API_KEY": "", "EGITIM_KAYNAK_MCP_API_KEY": ""}
        salt = fleet_probe._load_or_create_salt(cache_path.parent)
        fleet_probe.write_cache(
            cache_path,
            {"tedy": {"name": "tedy", "status": "unreachable", "http": None, "detail": "onbellek-kaniti"}},
            fleet_probe.roster_fingerprint(lock),
            identity=fleet_probe.cache_identity(lock, cred_env, salt),
        )
        code, out = run_hook("cursor_session_start.py", cursor_session_payload(), env_extra={
            "CURSOR_PLUGIN_ROOT": str(ROOT),
            "EDUPEDIA_PREFLIGHT_NO_PROBE": "",
            "XDG_CACHE_HOME": str(cache_root),
            **cred_env,
        })
        # "onbellek-kaniti" can only come from the cache: a live probe would carry a real HTTP detail.
        check("yalnız önbellekten gelebilecek ayrıntı bağlamda",
              code == 0 and "erişilemedi (onbellek-kaniti)" in str((out or {}).get("additional_context", "")))

    print(f"\nSonuç: {PASS} passed, {FAIL} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    main()
