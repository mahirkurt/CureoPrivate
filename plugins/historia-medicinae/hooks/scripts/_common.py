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


def _turn_records(payload, window=400):
    """Son TURUN kayıtlarını (eskiden yeniye) döndür.

    TUR SINIRI: geriye yürürken gerçek bir KULLANICI METNİ mesajında durulur.
    ⚠️ Araç sonuçları da `role: "user"` olarak kaydedilir — sınır için role tek
    başına YETMEZ; yalnız `type: "text"` bloğu taşıyan user mesajı gerçek sınırdır.
    (Bu ayrım ölçüldü: canlı transkriptte 43 `user/tool_result`'a karşı 2 `user/text`.)
    """
    path = payload.get("transcript_path")
    if not path:
        return []
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    recs = []
    for line in reversed(lines[-window:]):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        msg = rec.get("message") or {}
        role, content = msg.get("role"), msg.get("content")
        if role == "user":
            blocks = content if isinstance(content, list) else []
            is_text = isinstance(content, str) or any(
                isinstance(b, dict) and b.get("type") == "text" for b in blocks)
            if is_text:
                break                      # GERÇEK tur sınırı
            continue                        # tool_result — sınır değil
        recs.append(rec)
    return list(reversed(recs))


def transcript_text(payload, limit=200_000):
    """SON TURDA üretilen asistan metni. Yoksa boş string."""
    out = []
    for rec in _turn_records(payload):
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
    return "\n".join(out)


def turn_called_mcp(payload):
    """Bu turda GERÇEK bir MCP connector çağrısı yapıldı mı.

    META-TUR BASKILAYICI: filo/mod adlarını ANAN ama connector ÇAĞIRMAYAN turlar
    (dokümantasyon, hook öz-kodu, mimari tartışma) araştırma çıktısı DEĞİLDİR —
    raporlanacak kapsam yoktur. Kapı bunlarda susar. Aksi hâlde 'MORBUS' kelimesini
    yazmak, o modda araştırma yapmakla aynı sayılır (canlı oturumda gözlendi).
    """
    for rec in _turn_records(payload):
        msg = rec.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        for block in msg.get("content") or []:
            if (isinstance(block, dict) and block.get("type") == "tool_use"
                    and str(block.get("name", "")).startswith("mcp__")):
                return True
    return False
