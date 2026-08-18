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


def run_hook_raw(
    script_name: str,
    raw: str,
    env_extra: dict | None = None,
) -> tuple[int, dict | None]:
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    res = subprocess.run(
        [sys.executable, str(SCRIPTS / script_name)],
        input=raw,
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


def run_hook(script_name: str, payload: dict, env_extra: dict | None = None) -> tuple[int, dict | None]:
    return run_hook_raw(script_name, json.dumps(payload), env_extra)


def cursor_common(event: str, workspace: Path) -> dict:
    """Cursor'ın her hook zarfında gönderdiği ortak alanların test örneği."""
    return {
        "conversation_id": "conv-edupedia-test",
        "generation_id": "gen-edupedia-test",
        "model": "gpt-test",
        "hook_event_name": event,
        "cursor_version": "test",
        "workspace_roots": [str(workspace)],
    }


def claude_common(event: str, workspace: Path) -> dict:
    """Claude Code'un PostToolUse ortak alanlarının test örneği."""
    return {
        "session_id": "claude-session-test",
        "transcript_path": str(workspace / "transcript.jsonl"),
        "cwd": str(workspace),
        "permission_mode": "default",
        "hook_event_name": event,
        "workspace_roots": [str(workspace)],
    }


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

    print("\n== 2. session_start.py (SessionStart Hook) ==")
    code, out = run_hook("session_start.py", {"source": "test"}, env_extra={"EDUPEDIA_PREFLIGHT_NO_PROBE": "1"})
    check("SessionStart sıfır çıkış kodu döner", code == 0)
    check("SessionStart structured output döner", bool(out and "hookSpecificOutput" in out))
    ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "") if out else ""
    check("SessionStart konvansiyonları içerir", "[edupedia]" in ctx and "16 KALİTE KAPISI" in ctx and "maarif-mufredat" in ctx)

    print("\n== 3. validate_module_hook.py (PostToolUse Hook) ==")
    # non-html file -> no-op
    code, out = run_hook(
        "validate_module_hook.py",
        {
            **claude_common("PostToolUse", ROOT),
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/test.py"},
        },
    )
    check("HTML olmayan dosyada sessiz kalır", code == 0 and out is None)

    # valid template html -> runs and succeeds silently
    template_path = str(ROOT / "skills" / "carbon-edupedia" / "assets" / "module-template.html")
    code, out = run_hook(
        "validate_module_hook.py",
        {
            **claude_common("PostToolUse", ROOT),
            "tool_name": "Write",
            "tool_input": {"file_path": template_path},
        },
    )
    check("Geçerli şablonda sıfır çıkış kodu ve sessiz/advisory dönüş", code == 0)

    # fail fixture -> surfaces advisory context
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8") as tf:
        tf.write("""<!DOCTYPE html><html lang="tr"><head><title>Test</title></head><body>
<script>const MODULE_DATA = { title: "Test 😀" };</script>
</body></html>""")
        tf.flush()
        workspace = Path(tf.name).parent
        code, out = run_hook(
            "validate_module_hook.py",
            {
                **claude_common("PostToolUse", workspace),
                "tool_name": "Write",
                "tool_input": {"file_path": tf.name},
            },
        )
        check("İhlal içeren HTML'de advisory bağlam döner", code == 0 and out is not None and "G-EMOJI" in str(out))

    print("\n== 4. Cursor-native hook zarfları ==")
    session_payload = {
        **cursor_common("sessionStart", ROOT),
        "session_id": "cursor-session-test",
        "is_background_agent": False,
        "composer_mode": "agent",
    }
    code, out = run_hook(
        "cursor_session_start.py",
        session_payload,
        env_extra={
            "CURSOR_PLUGIN_ROOT": str(ROOT),
            "EDUPEDIA_PREFLIGHT_NO_PROBE": "1",
        },
    )
    check("Cursor sessionStart sıfır çıkış kodu döner", code == 0)
    check(
        "Cursor sessionStart additional_context döner",
        bool(out and isinstance(out.get("additional_context"), str) and "[edupedia]" in out["additional_context"]),
    )
    check(
        "Cursor sessionStart Claude wrapper döndürmez",
        bool(out is not None and "hookSpecificOutput" not in out),
    )

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        workspace = base / "workspace"
        workspace.mkdir()
        bad_module = workspace / "module.html"
        bad_module.write_text(
            """<!DOCTYPE html><html lang="tr"><head><title>Test</title></head><body>
<script>const MODULE_DATA = { title: "Test 😀" };</script>
</body></html>""",
            encoding="utf-8",
        )
        post_payload = {
            **cursor_common("postToolUse", workspace),
            "tool_name": "Write",
            "tool_input": {"file_path": str(bad_module)},
            "tool_output": {"path": str(bad_module)},
            "tool_use_id": "write-test-1",
            "cwd": str(workspace),
            "duration": 12,
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            post_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor postToolUse sıfır çıkış kodu döner", code == 0)
        check(
            "Cursor postToolUse additional_context döner",
            bool(out and "G-EMOJI" in out.get("additional_context", "")),
        )
        check(
            "Cursor postToolUse Claude wrapper döndürmez",
            bool(out is not None and "hookSpecificOutput" not in out),
        )

        print("\n== 5. Host-bazlı araç adı sözleşmesi ==")
        for tool_name in ("Write", "Edit", "StrReplace"):
            claude_payload = {
                **claude_common("PostToolUse", workspace),
                "tool_name": tool_name,
                "tool_input": {"file_path": str(bad_module)},
                "tool_response": {"filePath": str(bad_module)},
                "tool_use_id": f"claude-{tool_name}",
            }
            code, out = run_hook("validate_module_hook.py", claude_payload)
            check(
                f"Claude {tool_name} aracını kabul eder",
                code == 0 and bool(out and "G-EMOJI" in str(out)),
            )

        claude_unknown = {
            **claude_common("PostToolUse", workspace),
            "tool_name": "Shell",
            "tool_input": {"file_path": str(bad_module)},
            "tool_use_id": "claude-unknown",
        }
        code, out = run_hook("validate_module_hook.py", claude_unknown)
        check("Claude bilinmeyen aracı reddeder", code == 0 and out is None)

        for tool_name in ("Edit", "Shell"):
            cursor_unknown = {
                **post_payload,
                "tool_name": tool_name,
                "tool_use_id": f"cursor-{tool_name}",
            }
            code, out = run_hook(
                "cursor_validate_module_hook.py",
                cursor_unknown,
                env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
            )
            check(
                f"Cursor {tool_name} aracını reddeder",
                code == 0 and out == {},
            )

        nested_payload = {
            **post_payload,
            "tool_input": {"arguments": {"target_path": str(bad_module)}},
            "tool_use_id": "write-test-2",
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            nested_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check(
            "Cursor nested Write yolu savunmacı ayrıştırılır",
            code == 0 and bool(out and "additional_context" in out),
        )

        no_path_payload = {
            **post_payload,
            "tool_input": {"content": "<html></html>"},
            "tool_use_id": "write-test-3",
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            no_path_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor yol yoksa tam `{}` döner", code == 0 and out == {})

        non_html = workspace / "module.py"
        non_html.write_text("MODULE_DATA = {}", encoding="utf-8")
        non_html_payload = {
            **post_payload,
            "tool_input": {"target_file": str(non_html)},
            "tool_use_id": "write-test-4",
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            non_html_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor HTML olmayan dosyada tam `{}` döner", code == 0 and out == {})

        plain_html = workspace / "plain.html"
        plain_html.write_text("<!doctype html><title>Sıradan sayfa</title>", encoding="utf-8")
        no_marker_payload = {
            **post_payload,
            "tool_input": {"target_path": str(plain_html)},
            "tool_use_id": "write-test-5",
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            no_marker_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor MODULE_DATA yoksa tam `{}` döner", code == 0 and out == {})

        code, out = run_hook_raw(
            "cursor_validate_module_hook.py",
            "{bozuk-json",
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor bozuk girdide fail-open `{}` döner", code == 0 and out == {})

        print("\n== 6. Kanonik yol ve boyut güvenliği ==")
        sibling = base / "workspace-sibling"
        sibling.mkdir()
        outside = sibling / "outside.html"
        outside.write_text(
            "<html><script>const MODULE_DATA = {title: 'Dışarı 😀'};</script></html>",
            encoding="utf-8",
        )
        traversal_payload = {
            **post_payload,
            "tool_input": {"path": str(outside)},
            "tool_use_id": "write-test-6",
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            traversal_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor sibling-prefix yolunu reddeder", code == 0 and out == {})

        symlink_path = workspace / "linked.html"
        symlink_path.symlink_to(outside)
        symlink_payload = {
            **post_payload,
            "tool_input": {"path": "linked.html"},
            "tool_use_id": "write-test-7",
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            symlink_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor symlink kaçışını reddeder", code == 0 and out == {})

        root_only = workspace / "root-only.html"
        root_only.write_text(
            "<html><script>const MODULE_DATA = {title: 'Kök 😀'};</script></html>",
            encoding="utf-8",
        )
        workspace_root_payload = {
            **post_payload,
            "workspace_roots": [str(workspace)],
            "tool_input": {"path": root_only.name},
            "tool_use_id": "write-test-8",
        }
        workspace_root_payload.pop("cwd")
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            workspace_root_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check(
            "Cursor workspace_roots ile göreli yolu kabul eder",
            code == 0 and bool(out and "additional_context" in out),
        )

        no_roots_payload = {
            **post_payload,
            "workspace_roots": [],
            "tool_input": {"path": str(outside)},
            "tool_use_id": "write-test-9",
        }
        no_roots_payload.pop("cwd")
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            no_roots_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor güvenilir kök yoksa mutlak yolu okumaz", code == 0 and out == {})

        claude_no_roots = {
            "session_id": "claude-no-root",
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(outside)},
            "tool_use_id": "claude-write-no-root",
        }
        code, out = run_hook("validate_module_hook.py", claude_no_roots)
        check("Claude güvenilir kök yoksa mutlak yolu okumaz", code == 0 and out is None)

        oversized = workspace / "oversized.html"
        with oversized.open("wb") as handle:
            handle.write(b"<script>const MODULE_DATA = {title: 'oversized'};</script>")
            handle.seek(9 * 1024 * 1024)
            handle.write(b"x")
        oversized_payload = {
            **post_payload,
            "tool_input": {"path": str(oversized)},
            "tool_use_id": "write-test-10",
        }
        code, out = run_hook(
            "cursor_validate_module_hook.py",
            oversized_payload,
            env_extra={"CURSOR_PLUGIN_ROOT": str(ROOT)},
        )
        check("Cursor büyük HTML'i okumadan fail-open döner", code == 0 and out == {})

    print("\n== 7. Host-nötr SessionStart remediation ==")
    with tempfile.TemporaryDirectory() as td:
        cache_root = Path(td)
        cache_path = cache_root / "cureonics-fleet" / "edupedia.json"
        stamp = fleet_probe.roster_fingerprint(lock)
        cache_results = {
            "maarif-mufredat": {
                "name": "maarif-mufredat",
                "status": "auth_missing",
                "auth_env": "MUFREDAT_MCP_API_KEY",
            }
        }
        cache_env = {
            "MUFREDAT_MCP_API_KEY": "",
            "EGITIM_KAYNAK_MCP_API_KEY": "",
        }
        has_cache_identity = hasattr(fleet_probe, "cache_identity")
        check("credential-sensitive cache identity API mevcut", has_cache_identity)
        if has_cache_identity:
            salt = fleet_probe._load_or_create_salt(cache_path.parent)
            identity = fleet_probe.cache_identity(lock, cache_env, salt)
            fleet_probe.write_cache(
                cache_path,
                cache_results,
                stamp,
                identity=identity,
            )
        else:
            fleet_probe.write_cache(cache_path, cache_results, stamp)
        code, out = run_hook(
            "cursor_session_start.py",
            session_payload,
            env_extra={
                "CURSOR_PLUGIN_ROOT": str(ROOT),
                "EDUPEDIA_PREFLIGHT_NO_PROBE": "",
                "XDG_CACHE_HOME": str(cache_root),
                **cache_env,
            },
        )
        cursor_context = out.get("additional_context", "") if out else ""
        check(
            "Cursor remediation Claude-only komut içermez",
            code == 0 and "MUFREDAT_MCP_API_KEY" in cursor_context and "-- claude" not in cursor_context,
        )

    print(f"\nSonuç: {PASS} passed, {FAIL} failed")
    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
