"""historia-medicinae hook ortak yardımcıları — stdlib yalnız, fail-open."""
import json
import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent


def read_payload():
    """Hook stdin JSON'unu oku. Bozuksa boş dict — asla patlamaz."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def load_lock():
    """fleet.lock.json (gen_fleet.py türevi). Yoksa boş iskelet."""
    try:
        return json.loads((PLUGIN_ROOT / "fleet.lock.json").read_text(encoding="utf-8"))
    except Exception:
        return {"servers": [], "companions": [], "delegations": [], "counts": {}}


def emit_context(text):
    """SessionStart için additionalContext; diğer eventler için düz stdout."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        }
    }, ensure_ascii=False))


def emit_block(reason):
    """Stop hook'unda modeli devam ettirmek için."""
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def env_present(name):
    return bool(name and os.environ.get(name, "").strip())


def transcript_text(payload, limit=200_000):
    """Transkript dosyasından son asistan metnini topla. Yoksa boş string."""
    path = payload.get("transcript_path")
    if not path:
        return ""
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    out = []
    for line in reversed(lines[-400:]):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        msg = rec.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    out.append(block.get("text", ""))
        elif isinstance(content, str):
            out.append(content)
        if sum(len(x) for x in out) > limit:
            break
    return "\n".join(reversed(out))
