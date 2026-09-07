#!/usr/bin/env python3
"""Anamnesis helpers — exclusive collection + prefixed doc_id. CANONICAL, VENDORED.

DO NOT EDIT THE COPY INSIDE A PLUGIN. The canonical source is
`tools/fleetkit/vendor/anamnesis/anamnesis_run.py`; `tools/fleetkit/vendor.py`
copies it byte-identically into each consuming plugin and `check_drift.py`
fails CI if a copy diverges.

WHY VENDORED AND NOT IMPORTED: plugins install from the marketplace as ONE
DIRECTORY, so shared code at the repo root never reaches the installed copy.
Runtime components must live inside the plugin — the same constraint that
already governs `fleet_probe.py`.

Everything plugin-specific lives in a sibling `anamnesis_config.py`; this file
derives the rest, so the two consumers stay byte-identical here.

Contract:
  collection = "{PLUGIN_ID}:{KIND}:<12hex>"
  doc_id     = "{PREFIX_HEAD}<12hex>:<canonical>"
  kind ∈ {run, sess, lib} — a plugin picks one, never lib.

Guard DENY unscoped hybrid_query / graph_* / search. ALLOW when collection
matches this run. Cleanup: forget_collection (fallback N× forget_document)
on SessionEnd + next flagship command + startup leftover. No Stop forget.

CI: <ENV_PREFIX>_FORGET_LOG stubs HTTP; <ENV_PREFIX>_NO_NETWORK skips live
calls. Secrets are never logged. Fail-open on I/O.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from anamnesis_config import (  # noqa: E402  — per-plugin identity, vendored core stays generic
    DOC_ID_EXAMPLE,
    ENV_PREFIX,
    GUARD_OFF,
    KIND,
    LEDGER_NAME,
    NEW_RUN_RE,
    PLUGIN_ID,
    PLUGIN_LABEL,
    PREFIX_HEAD,
)

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
RUN_ID_RE = re.compile(r"^[0-9a-f]{12}$")
PREFIX_RE = re.compile(rf"^{re.escape(PREFIX_HEAD)}([0-9a-f]{{12}}):")
COLLECTION_RE = re.compile(rf"^{re.escape(PLUGIN_ID)}:{re.escape(KIND)}:([0-9a-f]{{12}})$")

HYBRID_GRAPH = {"hybrid_query", "graph_neighbors", "subgraph"}
OBSERVE = {"corpus_stats"}

# Fleet-wide Anamnesis collection / doc_id prefixes. Own prefixes are excluded
# below so wrong own-run still DENYs; peer prefixes pass through (the owning
# plugin's guard enforces exclusivity). Copied per plugin — no shared package.
ANAMNESIS_FLEET_SCOPE_PREFIXES = (
    "evidentia:run:",
    "evrun:",
    "cureolex:sess:",
    "cureolex:run:",
    "cureolex:lib:",
    "vekayinuvis:run:",
    "vkrun:",
    "histmed:run:",
    "hmrun:",
    "openathens:run:",
    "marmara:run:",
    "marmara:ebsco",
)
COLLECTION_HEAD = f"{PLUGIN_ID}:{KIND}:"
OWN_SCOPE_PREFIXES = (COLLECTION_HEAD, PREFIX_HEAD)
_UA = f"Mozilla/5.0 ({PLUGIN_ID}-anamnesis-cleanup)"
_INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": f"{PLUGIN_ID}-anamnesis", "version": "1"},
    },
}


def _env(name: str, default: str = "") -> str:
    return os.environ.get(f"{ENV_PREFIX}_{name}", default).strip()


def is_anamnesis_tool(tool: str) -> bool:
    t = (tool or "").lower()
    return t.startswith("mcp__") and "anamnesis" in t


def tool_base(tool: str) -> str:
    return str(tool or "").split("__")[-1]


def tool_input_of(data: dict) -> dict:
    for key in ("tool_input", "tool_arguments", "arguments", "input"):
        v = data.get(key)
        if isinstance(v, dict):
            return v
    return {}


def mint_run_id() -> str:
    return os.urandom(6).hex()


def prefix_for(run_id: str) -> str:
    return f"{PREFIX_HEAD}{run_id}:"


def collection_for(run_id: str) -> str:
    return f"{PLUGIN_ID}:{KIND}:{run_id}"


def has_run_prefix(doc_id: str, run_id: str) -> bool:
    return str(doc_id or "").startswith(prefix_for(run_id))


def collection_matches(value: str, run_id: str) -> bool:
    return str(value or "").strip() == collection_for(run_id)


def scoped_doc_id(run_id: str, raw: str) -> str:
    raw = str(raw or "").strip()
    want = prefix_for(run_id)
    if raw.startswith(want):
        return raw
    m = PREFIX_RE.match(raw)
    if m:
        return want + raw[m.end():]
    if raw.startswith(COLLECTION_HEAD):
        rest = raw.split(":", 2)[-1]
        # {PLUGIN_ID}:{KIND}:<id>:<canonical> from another run
        if ":" in rest:
            rest = rest.split(":", 1)[1]
        return want + rest
    if raw.startswith(f"{PLUGIN_ID}:"):
        return want + raw[len(PLUGIN_ID) + 1:]
    return want + raw


def ids_of(inp: dict) -> list[str]:
    out = []
    d = inp.get("doc_id") or inp.get("docId")
    if d:
        out.append(str(d).strip())
    ids = inp.get("doc_ids") or inp.get("docIds")
    if isinstance(ids, list):
        out.extend(str(x).strip() for x in ids if x)
    return [x for x in out if x]


def ledger_path() -> Path:
    override = _env("LEDGER")
    if override:
        return Path(override)
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if proj:
        return Path(proj) / ".claude" / LEDGER_NAME
    uid = str(os.getuid()) if hasattr(os, "getuid") else "user"
    return Path(tempfile.gettempdir()) / f"anamnesis-{PLUGIN_ID}-{uid}" / LEDGER_NAME


def empty_ledger(run_id: str | None = None) -> dict:
    rid = run_id or mint_run_id()
    return {
        "run_id": rid,
        "collection": collection_for(rid),
        "prefix": prefix_for(rid),
        "doc_ids": [],
        "pending_forget": [],
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "active",
    }


def _clean_ids(raw, run_id: str) -> list[str]:
    out, seen = [], set()
    if not isinstance(raw, list):
        return out
    for item in raw:
        s = str(item or "").strip()
        if not s or s in seen or not has_run_prefix(s, run_id):
            continue
        seen.add(s)
        out.append(s)
    return out


def load_ledger() -> dict | None:
    path = ledger_path()
    try:
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    rid = str(data.get("run_id") or "")
    if not RUN_ID_RE.match(rid):
        coll = str(data.get("collection") or "")
        m = COLLECTION_RE.match(coll)
        if m:
            rid = m.group(1)
        else:
            return None
    data["run_id"] = rid
    data["collection"] = collection_for(rid)
    data["prefix"] = prefix_for(rid)
    data["doc_ids"] = _clean_ids(data.get("doc_ids"), rid)
    data["pending_forget"] = _clean_ids(data.get("pending_forget"), rid)
    data.setdefault("status", "active")
    return data


def save_ledger(ledger: dict) -> None:
    path = ledger_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        tmp.replace(path)
    except Exception:
        pass


def ensure_ledger() -> dict:
    led = load_ledger()
    if led:
        return led
    led = empty_ledger()
    save_ledger(led)
    return led


def record_doc_id(doc_id: str) -> dict:
    led = ensure_ledger()
    rid = led["run_id"]
    if not has_run_prefix(doc_id, rid):
        return led
    if doc_id not in led["doc_ids"]:
        led["doc_ids"].append(doc_id)
        save_ledger(led)
    return led


def drop_doc_id(doc_id: str) -> dict:
    led = load_ledger() or empty_ledger()
    led["doc_ids"] = [d for d in led.get("doc_ids", []) if d != doc_id]
    led["pending_forget"] = [d for d in led.get("pending_forget", []) if d != doc_id]
    save_ledger(led)
    return led


def extract_doc_id(payload: dict) -> str:
    inp = tool_input_of(payload)
    for key in ("doc_id", "docId"):
        v = inp.get(key)
        if v:
            return str(v).strip()
    result = payload.get("tool_result", payload.get("tool_response", ""))
    text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
    try:
        obj = json.loads(text) if isinstance(result, str) else result
    except Exception:
        obj = None
    if isinstance(obj, dict) and obj.get("doc_id"):
        return str(obj["doc_id"]).strip()
    m = re.search(r'"doc_id"\s*:\s*"([^"]+)"', text)
    return m.group(1).strip() if m else ""


def is_new_run(prompt: str) -> bool:
    return bool(NEW_RUN_RE.search(prompt or ""))


def session_source(data: dict) -> str:
    for key in ("source", "reason", "matcher"):
        v = str(data.get(key) or "").strip().lower()
        if v:
            return v
    return ""


def event_name(data: dict) -> str:
    return str(data.get("hook_event_name") or data.get("hookEventName") or "").strip()


def prompt_of(data: dict) -> str:
    for key in ("prompt", "user_prompt", "content", "text"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def context_message(ledger: dict) -> str:
    rid = ledger["run_id"]
    coll = collection_for(rid)
    prefix = prefix_for(rid)
    n = len(ledger.get("doc_ids") or [])
    return (
        f"[{PLUGIN_LABEL}] Anamnesis münhasır çalışma seti — "
        f"collection=`{coll}` · doc_id öneki `{prefix}` ({n} kayıtlı belge). "
        f"Her ingest: collection + `{PREFIX_HEAD}<id>:<kanonik>` ({DOC_ID_EXAMPLE}). "
        "hybrid_query / graph_neighbors / subgraph YALNIZ bu collection ile. "
        "Kapsamsız çağrı DENY (paylaşılan korpus sızıntısı). "
        "Cevap yalnız dönen chunk'lardan; atıf `doc_id::idx`. "
        "corpus_stats küresel gözlemdir, bu koşunun çalışma seti değildir. "
        f"Stop'ta silinmez. SessionEnd / sonraki `/{PLUGIN_LABEL}` / startup "
        "yalnız bu collection'ı forget_collection (yoksa ledger id'leri) ile temizler."
    )


def peer_scope_prefixes() -> tuple[str, ...]:
    own = set(OWN_SCOPE_PREFIXES)
    return tuple(p for p in ANAMNESIS_FLEET_SCOPE_PREFIXES if p not in own)


def _matches_scope_prefix(value: str, prefixes: tuple[str, ...]) -> bool:
    s = str(value or "").strip()
    return bool(s) and any(s.startswith(p) for p in prefixes)


def is_peer_plugin_scope(inp: dict) -> bool:
    """True when collection / doc_id belongs to another known plugin namespace."""
    peers = peer_scope_prefixes()
    coll = str((inp or {}).get("collection") or "").strip()
    if coll:
        return _matches_scope_prefix(coll, peers)
    ids = ids_of(inp or {})
    if ids:
        return all(_matches_scope_prefix(i, peers) for i in ids)
    triples = (inp or {}).get("triples") or []
    if isinstance(triples, list) and triples:
        for t in triples:
            if not isinstance(t, dict):
                return False
            tcoll = str(t.get("collection") or "").strip()
            doc = str(t.get("doc_id") or t.get("docId") or "").strip()
            if tcoll:
                if not _matches_scope_prefix(tcoll, peers):
                    return False
            elif not _matches_scope_prefix(doc, peers):
                return False
        return True
    return False


def deny_reason(base: str, inp: dict, ledger: dict) -> str | None:
    rid = ledger["run_id"]
    coll = collection_for(rid)
    prefix = prefix_for(rid)
    got = str(inp.get("collection") or "").strip()

    if base in OBSERVE:
        return None

    if is_peer_plugin_scope(inp):
        return None

    if base in HYBRID_GRAPH:
        if collection_matches(got, rid):
            return None
        return (
            f"anamnesis münhasır: '{base}' collection='{coll}' ister "
            "(kapsamsız hybrid/graph paylaşılan indeksi tarar veya Worker MCP error "
            "döner). doc_scope YOKTUR — collection / doc_ids[] kullan. "
            f"Atıf `doc_id::idx`."
        )

    if base == "list_docs":
        if collection_matches(got, rid):
            return None
        return f"anamnesis münhasır: list_docs collection='{coll}' ister."

    if base == "forget_collection":
        if collection_matches(got, rid):
            return None
        return (
            "anamnesis münhasır: forget_collection yalnız bu koşunun "
            f"koleksiyonunu siler (`{coll}`). Başka kiracıya kör wipe yok."
        )

    if base == "ingest_document":
        doc = str(inp.get("doc_id") or inp.get("docId") or "").strip()
        if not collection_matches(got, rid):
            return (
                f"anamnesis münhasır: ingest_document collection='{coll}' "
                f"zorunlu (eksik → Worker `_legacy` torbasına düşer)."
            )
        if not doc:
            return (
                f"anamnesis münhasır: ingest_document doc_id zorunlu — "
                f"`{prefix}<kanonik>` (ör. `{prefix}{DOC_ID_EXAMPLE}`)."
            )
        if not has_run_prefix(doc, rid):
            return (
                f"anamnesis münhasır: doc_id öneksiz. Tekrar dene: "
                f"doc_id='{scoped_doc_id(rid, doc)}' + collection='{coll}'."
            )
        return None

    if base == "forget_document":
        doc = str(inp.get("doc_id") or inp.get("docId") or "").strip()
        if not doc or not has_run_prefix(doc, rid):
            return (
                "anamnesis münhasır: forget_document yalnız bu koşunun "
                f"önekli id'sini siler (`{prefix}…`). Çalışma seti için "
                f"forget_collection(collection='{coll}') tercih edilir."
            )
        return None

    if base == "semantic_search":
        if collection_matches(got, rid):
            return None
        docs = ids_of(inp)
        if docs and all(has_run_prefix(d, rid) for d in docs):
            return None
        return (
            "anamnesis münhasır: semantic_search collection veya önekli "
            f"doc_id/doc_ids[] ister. collection='{coll}' veya "
            f"doc_id='{prefix}<kanonik>'. Kapsamsız arama paylaşılan korpusu tarar."
        )

    if base == "upsert_triples":
        if not collection_matches(got, rid):
            return (
                f"anamnesis münhasır: upsert_triples collection='{coll}' "
                "zorunlu (düğüm anahtarı koleksiyonu taşır)."
            )
        triples = inp.get("triples") or []
        if not isinstance(triples, list):
            return "anamnesis münhasır: upsert_triples.triples bir liste olmalı."
        for i, t in enumerate(triples):
            if not isinstance(t, dict):
                continue
            doc = str(t.get("doc_id") or t.get("docId") or "").strip()
            if doc and not has_run_prefix(doc, rid):
                return (
                    f"anamnesis münhasır: triples[{i}].doc_id bu koşunun "
                    f"önekiyle başlamalı (`{prefix}…`)."
                )
        return None

    return None


def anamnesis_url() -> str:
    override = _env("URL")
    if override:
        return override.rstrip("/")
    try:
        lock = json.loads((PLUGIN_ROOT / "fleet.lock.json").read_text(encoding="utf-8"))
        for s in lock.get("servers", []):
            if s.get("name") == "anamnesis" and s.get("url"):
                return str(s["url"]).rstrip("/")
    except Exception:
        pass
    return "https://anamnesis-mcp.cureonics.workers.dev/mcp"


def _forget_stub(doc_ids: list[str], collection: str) -> list[dict]:
    log = _env("FORGET_LOG")
    out = []
    if not log:
        return out
    try:
        Path(log).parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as fh:
            row = {"collection": collection, "ok": True, "stub": True}
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.append(row)
            for doc_id in doc_ids:
                row = {"doc_id": doc_id, "ok": True, "stub": True}
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.append(row)
    except Exception:
        return [{"collection": collection, "ok": False, "stub": True}]
    return out


def _rpc_parse(content_type: str, body: str) -> dict | None:
    if not (body or "").strip():
        return None
    if "text/event-stream" in (content_type or ""):
        for line in body.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except Exception:
                    return None
        return None
    try:
        return json.loads(body)
    except Exception:
        return None


def _http_session():
    """Best-effort MCP session. Never prints the bearer value."""
    if _env("NO_NETWORK") or os.environ.get("HISTMED_ANAMNESIS_NO_NETWORK"):
        return None
    key = os.environ.get("ANAMNESIS_MCP_API_KEY", "").strip()
    if not key:
        return None
    url = anamnesis_url()
    sid = None

    def post(payload, timeout=20, notify=False):
        nonlocal sid
        headers = {
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": _UA,
        }
        if sid:
            headers["mcp-session-id"] = sid
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers=headers, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                sid = resp.headers.get("mcp-session-id") or sid
                if notify:
                    return {"ok": True, "json": None}
                return {"ok": True, "json": _rpc_parse(resp.headers.get("content-type", ""), raw)}
        except urllib.error.HTTPError as e:
            return {"ok": False, "err": f"HTTP {e.code}"}
        except Exception as e:
            return {"ok": False, "err": type(e).__name__}

    init = post(_INIT)
    if not init.get("ok"):
        return None
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, notify=True)
    return post


def _call_ok(body: dict | None) -> bool:
    if not body:
        return False
    if body.get("error"):
        return False
    if (body.get("result") or {}).get("isError"):
        return False
    return True


def _http_forget(doc_ids: list[str], collection: str) -> list[dict]:
    post = _http_session()
    if post is None:
        reason = "no_network" if (_env("NO_NETWORK") or os.environ.get("HISTMED_ANAMNESIS_NO_NETWORK")) else "no_key"
        return [{"doc_id": d, "ok": False, "skipped": reason} for d in doc_ids] or [
            {"collection": collection, "ok": False, "skipped": reason}
        ]
    r = post({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "forget_collection", "arguments": {"collection": collection}},
    })
    if r.get("ok") and _call_ok(r.get("json")):
        return [{"collection": collection, "ok": True}] + [
            {"doc_id": d, "ok": True} for d in doc_ids
        ]
    results = [{"collection": collection, "ok": False, "fallback": "forget_document"}]
    for doc_id in doc_ids:
        r = post({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "forget_document", "arguments": {"doc_id": doc_id}},
        })
        ok = bool(r.get("ok")) and _call_ok(r.get("json"))
        results.append({"doc_id": doc_id, "ok": ok, "err": None if ok else r.get("err") or "rpc"})
    return results


def forget_run_docs(ledger: dict | None = None) -> dict:
    """Forget this run's collection (and ledger ids). Never touches other tenants."""
    led = ledger or load_ledger()
    if not led:
        return {"forgotten": 0, "failed": 0, "skipped": True}
    rid = led["run_id"]
    collection = collection_for(rid)
    ids, seen = [], set()
    for d in list(led.get("doc_ids") or []) + list(led.get("pending_forget") or []):
        if d in seen or not has_run_prefix(d, rid):
            continue
        seen.add(d)
        ids.append(d)

    if not ids and _env("FORGET_LOG"):
        led["doc_ids"] = []
        led["pending_forget"] = []
        led["status"] = "empty"
        save_ledger(led)
        return {"forgotten": 0, "failed": 0, "skipped": False}

    if _env("FORGET_LOG"):
        rows = _forget_stub(ids, collection)
        ok = all(r.get("ok") for r in rows) if rows else True
        led["doc_ids"] = []
        led["pending_forget"] = [] if ok else ids
        led["status"] = "empty" if ok else "cleanup_failed"
        save_ledger(led)
        return {"forgotten": len(ids) if ok else 0, "failed": 0 if ok else len(ids), "skipped": False}

    rows = _http_forget(ids, collection)
    coll_ok = any(r.get("collection") == collection and r.get("ok") for r in rows)
    pending = []
    if not coll_ok:
        for row in rows:
            if row.get("doc_id") and not row.get("ok"):
                pending.append(row["doc_id"])
    led["doc_ids"] = []
    led["pending_forget"] = pending
    led["status"] = "empty" if not pending else "cleanup_failed"
    save_ledger(led)
    return {"forgotten": len(ids) - len(pending), "failed": len(pending), "skipped": False}


def rotate_run(forget_previous: bool = True) -> dict:
    old = load_ledger()
    if forget_previous and old:
        forget_run_docs(old)
    fresh = empty_ledger()
    save_ledger(fresh)
    return fresh
