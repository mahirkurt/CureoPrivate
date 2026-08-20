#!/usr/bin/env python3
"""cureolex Anamnesis sess-scope helpers — collection + prefixed doc_id.

The live Worker may still lack `collection` / `doc_ids[]` / `forget_collection`
(P0 client still sends them). Isolation that works today:

  * every ingest id is ``{collection}:{human}`` e.g.
    ``cureolex:sess:<12hex>:mevzuat:1219/1`` (human prefixes kept)
  * hybrid_query / graph_* are DENIED unless ``collection`` or a prefixed
    doc_id/doc_ids[] is present (unscoped hybrid is global contamination)
  * a plugin-private ledger (never Evidentia's) records ids THIS sess ingested
  * cleanup prefers forget_collection; falls back to N× forget_document
  * HTTP is skipped when CUREOLEX_ANAMNESIS_FORGET_LOG is set (CI stub)

kind ∈ {sess, run, lib}. Default is sess (G0–G9 share one legal-research
thread). lib is NOT default — mevzuat.gov.tr is never dumped into a forever
library. Secrets are never logged. Fail-open on I/O.
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

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
PLUGIN = "cureolex"
LEDGER_NAME = "anamnesis-cureolex.json"
KIND_DEFAULT = "sess"
KINDS = ("sess", "run", "lib")
SESSION_ID_RE = re.compile(r"^[0-9a-f]{12}$")
COLLECTION_RE = re.compile(
    rf"^{re.escape(PLUGIN)}:(sess|run|lib):([0-9a-f]{{12}})$"
)
# Slash commands that CONTINUE the same sess (G0–G9 canonical cache).
# /lex-connectors is status-only — no collection inject.
LEX_WORK_RE = re.compile(
    r"(?:^|\s)/lex-(?:draft|amend|analyze|comply|opine|ria|"
    r"comparative|bill|expost)(?:\s|$)",
    re.IGNORECASE,
)
GLOBAL_READ = {"hybrid_query", "graph_neighbors", "subgraph"}
SCOPED_MUTATE = {"ingest_document", "forget_document", "forget_collection"}
SCOPED_SEARCH = {"semantic_search"}
TRIPLE_WRITE = {"upsert_triples"}
OBSERVE = {"corpus_stats"}

# Fleet-wide Anamnesis collection / doc_id prefixes. Own prefixes are excluded
# below so wrong own-sess still DENYs; peer prefixes pass through (the owning
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
    "openathens:fetch:",
    "marmara:fetch:",
    "marmara:ebsco",
)
OWN_SCOPE_PREFIXES = ("cureolex:sess:", "cureolex:run:", "cureolex:lib:")

_UA = "Mozilla/5.0 (cureolex-anamnesis-cleanup)"
_INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "cureolex-anamnesis", "version": "1"},
    },
}


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


def mint_session_id() -> str:
    return os.urandom(6).hex()


def collection_for(session_id: str, kind: str = KIND_DEFAULT) -> str:
    k = kind if kind in KINDS else KIND_DEFAULT
    return f"{PLUGIN}:{k}:{session_id}"


def parse_collection(value: str) -> tuple[str, str] | None:
    m = COLLECTION_RE.match(str(value or "").strip())
    if not m:
        return None
    return m.group(1), m.group(2)


def scoped_doc_id(collection: str, raw: str) -> str:
    raw = str(raw or "").strip()
    coll = str(collection or "").strip()
    if not coll:
        return raw
    prefix = coll + ":"
    if raw.startswith(prefix):
        return raw
    # Strip a foreign/stale cureolex:{kind}:{id}: prefix, keep the human tail.
    m = re.match(
        rf"^{re.escape(PLUGIN)}:(?:sess|run|lib):[0-9a-f]{{12}}:(.+)$", raw
    )
    if m:
        return prefix + m.group(1)
    return prefix + raw


def has_collection_prefix(doc_id: str, collection: str) -> bool:
    return str(doc_id or "").startswith(str(collection or "") + ":")


def collect_doc_ids(inp: dict) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    def add(val: object) -> None:
        s = str(val or "").strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)

    for key in ("doc_id", "docId"):
        if inp.get(key):
            add(inp.get(key))
    for key in ("doc_ids", "docIds"):
        v = inp.get(key)
        if isinstance(v, list):
            for item in v:
                add(item)
    for key in ("node", "seed", "entity"):
        if inp.get(key):
            add(inp.get(key))
    ents = inp.get("entities")
    if isinstance(ents, list):
        for item in ents:
            add(item)
    return out


def ledger_path() -> Path:
    override = os.environ.get("CUREOLEX_ANAMNESIS_LEDGER", "").strip()
    if override:
        return Path(override)
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if proj:
        return Path(proj) / ".claude" / LEDGER_NAME
    uid = str(os.getuid()) if hasattr(os, "getuid") else "user"
    return Path(tempfile.gettempdir()) / f"cureolex-anamnesis-{uid}" / LEDGER_NAME


def empty_ledger(session_id: str | None = None, kind: str = KIND_DEFAULT) -> dict:
    sid = session_id or mint_session_id()
    k = kind if kind in KINDS else KIND_DEFAULT
    coll = collection_for(sid, k)
    return {
        "plugin": PLUGIN,
        "kind": k,
        "session_id": sid,
        "collection": coll,
        "doc_ids": [],
        "pending_forget": [],
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "active",
    }


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
    sid = str(data.get("session_id") or "")
    if not SESSION_ID_RE.match(sid):
        return None
    kind = str(data.get("kind") or KIND_DEFAULT)
    if kind not in KINDS:
        kind = KIND_DEFAULT
    coll = str(data.get("collection") or collection_for(sid, kind))
    parsed = parse_collection(coll)
    if not parsed or parsed[1] != sid:
        coll = collection_for(sid, kind)
    data["plugin"] = PLUGIN
    data["kind"] = kind
    data["session_id"] = sid
    data["collection"] = coll
    data["doc_ids"] = _clean_ids(data.get("doc_ids"), coll)
    data["pending_forget"] = _clean_ids(data.get("pending_forget"), coll)
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


def _clean_ids(raw, collection: str) -> list[str]:
    out, seen = [], set()
    if not isinstance(raw, list):
        return out
    for item in raw:
        s = str(item or "").strip()
        if not s or s in seen or not has_collection_prefix(s, collection):
            continue
        seen.add(s)
        out.append(s)
    return out


def record_doc_id(doc_id: str) -> dict:
    led = ensure_ledger()
    coll = led["collection"]
    if not has_collection_prefix(doc_id, coll):
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


def is_lex_work_command(prompt: str) -> bool:
    return bool(LEX_WORK_RE.search(prompt or ""))


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
    coll = ledger.get("collection") or collection_for(ledger["session_id"])
    n = len(ledger.get("doc_ids") or [])
    example = scoped_doc_id(coll, "mevzuat:1219/1")
    return (
        "[cureolex] Anamnesis oturum koleksiyonu "
        f"`{coll}` ({n} kayıtlı doc_id; kind=sess, G0–G9 aynı cache). "
        "doc_scope YOKTUR — collection + önekli doc_id kullan. "
        f"ingest_document(collection='{coll}', "
        f"doc_id='{example}'). "
        "hybrid_query / semantic_search collection VE/VEYA doc_ids[] "
        "(önekli) olmadan YASAK (paylaşılan indeks sızıntısı). "
        "graph_* aynı kural. Cevaplar `doc_id::idx` ile atıflanır. "
        "corpus_stats küresel sayıdır, bu oturumun çalışma seti değildir. "
        "lib varsayılan DEĞİL — mevzuat.gov.tr sonsuz kütüphaneye dökülmez. "
        "Stop unutmaz; SessionEnd / yeni oturum (startup) önceki sess "
        "koleksiyonunu forget_collection (yoksa N× forget_document) ile siler."
    )


def _collection_matches(inp: dict, ledger: dict) -> bool:
    got = str(inp.get("collection") or "").strip()
    return bool(got) and got == ledger.get("collection")


def _ids_match(inp: dict, ledger: dict) -> bool:
    coll = ledger.get("collection") or ""
    ids = collect_doc_ids(inp)
    return bool(ids) and all(has_collection_prefix(i, coll) for i in ids)


def is_scoped(inp: dict, ledger: dict) -> bool:
    """True when collection matches or every listed id is prefixed."""
    return _collection_matches(inp, ledger) or _ids_match(inp, ledger)


def peer_scope_prefixes() -> tuple[str, ...]:
    own = set(OWN_SCOPE_PREFIXES)
    return tuple(p for p in ANAMNESIS_FLEET_SCOPE_PREFIXES if p not in own)


def _matches_scope_prefix(value: str, prefixes: tuple[str, ...]) -> bool:
    s = str(value or "").strip()
    return bool(s) and any(s.startswith(p) for p in prefixes)


def is_peer_plugin_scope(inp: dict) -> bool:
    """True when collection / doc_id belongs to another known plugin namespace.

    Pass-through ALLOW so co-installed plugin guards do not mutually DENY.
    Wrong own-sess / unscoped / unknown still follow this plugin's DENY rules.
    """
    peers = peer_scope_prefixes()
    coll = str((inp or {}).get("collection") or "").strip()
    if coll:
        return _matches_scope_prefix(coll, peers)
    ids: list[str] = []
    for key in ("doc_id", "docId"):
        v = (inp or {}).get(key)
        if v:
            ids.append(str(v).strip())
    extra = (inp or {}).get("doc_ids") or (inp or {}).get("docIds") or []
    if isinstance(extra, list):
        for item in extra:
            s = str(item or "").strip()
            if s:
                ids.append(s)
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
    """Return a deny string, or None to allow. corpus_stats always allowed."""
    coll = ledger["collection"]
    example = scoped_doc_id(coll, "mevzuat:1219/1")

    if base in OBSERVE:
        return None

    # Another plugin's valid namespace — skip this guard (do not mutual-DENY).
    if is_peer_plugin_scope(inp):
        return None

    if base in GLOBAL_READ:
        if is_scoped(inp, ledger):
            got = str(inp.get("collection") or "").strip()
            if got and parse_collection(got) and got.split(":")[1] == "lib" and (
                    ledger.get("kind") != "lib"):
                return (
                    "anamnesis: lib varsayılan değil. Bu oturum "
                    f"`{coll}` (sess). mevzuat.gov.tr sonsuz kütüphaneye "
                    f"dökülmez. collection='{coll}' kullan."
                )
            return None
        return (
            "anamnesis: '{base}' kapsam dışı — Worker'da doc_scope YOK; "
            "filtresiz hybrid/graph paylaşılan indeksi tarar. "
            f"collection='{coll}' ve/veya doc_ids=['{example}', …] zorunlu. "
            "Cevaplar doc_id::idx ile atıflanır."
        ).format(base=base)

    if base == "ingest_document":
        got = str(inp.get("collection") or "").strip()
        doc = str(inp.get("doc_id") or inp.get("docId") or "").strip()
        if got and got.split(":")[:2] == [PLUGIN, "lib"] and ledger.get("kind") != "lib":
            return (
                "anamnesis: lib varsayılan değil. "
                f"collection='{coll}' (sess) kullan; mevzuat.gov.tr "
                "forever-library'ye yazılmaz."
            )
        if got != coll:
            return (
                "anamnesis: ingest_document collection zorunlu ve bu "
                f"oturumun `{coll}` değeri olmalı (doc_scope yok)."
            )
        if not doc:
            return (
                f"anamnesis: ingest_document doc_id zorunlu — "
                f"`{example}` (insan-okunur mevzuat:/celex:/ecli:/rg: "
                f"kuyruğu korunur)."
            )
        if not has_collection_prefix(doc, coll):
            return (
                f"anamnesis: doc_id öneksiz. Tekrar dene: "
                f"doc_id='{scoped_doc_id(coll, doc)}'."
            )
        return None

    if base == "forget_document":
        doc = str(inp.get("doc_id") or inp.get("docId") or "").strip()
        if not doc or not has_collection_prefix(doc, coll):
            return (
                "anamnesis: forget_document yalnız bu oturumun önekli "
                f"id'sini siler (`{coll}:…`). Kör wipe yok."
            )
        return None

    if base == "forget_collection":
        got = str(inp.get("collection") or "").strip()
        if got != coll:
            return (
                "anamnesis: forget_collection yalnız bu oturumun "
                f"`{coll}` koleksiyonunu siler."
            )
        return None

    if base == "semantic_search":
        if is_scoped(inp, ledger):
            return None
        return (
            "anamnesis: semantic_search collection veya önekli "
            f"doc_id/doc_ids[] olmadan tüm paylaşılan indeksi tarar. "
            f"collection='{coll}' ve/veya doc_id='{example}'."
        )

    if base == "upsert_triples":
        triples = inp.get("triples") or []
        if not isinstance(triples, list):
            return "anamnesis: upsert_triples.triples bir liste olmalı."
        for i, t in enumerate(triples):
            if not isinstance(t, dict):
                return f"anamnesis: triples[{i}] nesne değil."
            doc = str(t.get("doc_id") or t.get("docId") or "").strip()
            if not has_collection_prefix(doc, coll):
                return (
                    "anamnesis: her triple.doc_id bu oturumun koleksiyon "
                    f"önekiyle başlamalı (`{coll}:…`)."
                )
        return None

    return None


def anamnesis_url() -> str:
    override = os.environ.get("CUREOLEX_ANAMNESIS_URL", "").strip()
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
    log = os.environ.get("CUREOLEX_ANAMNESIS_FORGET_LOG", "").strip()
    out = []
    if not log:
        return out
    try:
        Path(log).parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "op": "forget_collection",
                "collection": collection,
                "ok": False,
                "stub": True,
                "skipped": "fallback_forget_document",
            }, ensure_ascii=False) + "\n")
            for doc_id in doc_ids:
                row = {"doc_id": doc_id, "ok": True, "stub": True}
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.append(row)
    except Exception:
        return [{"doc_id": d, "ok": False, "stub": True} for d in doc_ids]
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


def _rpc_ok(body: dict | None) -> bool:
    if not body:
        return False
    if body.get("error"):
        return False
    result = body.get("result") or {}
    if isinstance(result, dict) and result.get("isError"):
        return False
    return True


def _http_session():
    key = os.environ.get("ANAMNESIS_MCP_API_KEY", "").strip()
    if os.environ.get("CUREOLEX_ANAMNESIS_NO_NETWORK"):
        return None, "no_network"
    if not key:
        return None, "no_key"
    url = anamnesis_url()
    sid = {"id": None}

    def post(payload, timeout=20, notify=False):
        headers = {
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": _UA,
        }
        if sid["id"]:
            headers["mcp-session-id"] = sid["id"]
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers=headers, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                sid["id"] = resp.headers.get("mcp-session-id") or sid["id"]
                if notify:
                    return {"ok": True, "json": None}
                return {
                    "ok": True,
                    "json": _rpc_parse(resp.headers.get("content-type", ""), raw),
                }
        except urllib.error.HTTPError as e:
            return {"ok": False, "err": f"HTTP {e.code}"}
        except Exception as e:
            return {"ok": False, "err": type(e).__name__}

    init = post(_INIT)
    if not init.get("ok"):
        return None, init.get("err", "init")
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, notify=True)
    return post, None


def _call_tool(post, name: str, arguments: dict) -> dict:
    r = post({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    })
    body = r.get("json") if r.get("ok") else None
    return {
        "ok": bool(r.get("ok")) and _rpc_ok(body),
        "err": None if r.get("ok") and _rpc_ok(body) else (
            r.get("err") or "rpc"
        ),
        "body": body,
    }


def _http_forget(doc_ids: list[str], collection: str) -> list[dict]:
    """forget_collection if deployed, else N× forget_document. Never prints the bearer."""
    post, err = _http_session()
    if err:
        return [{"doc_id": d, "ok": False, "skipped": err} for d in doc_ids]
    coll_r = _call_tool(post, "forget_collection", {"collection": collection})
    if coll_r["ok"]:
        return [{"doc_id": d, "ok": True, "via": "forget_collection"} for d in doc_ids]
    results = []
    for doc_id in doc_ids:
        r = _call_tool(post, "forget_document", {"doc_id": doc_id})
        results.append({
            "doc_id": doc_id,
            "ok": r["ok"],
            "err": None if r["ok"] else r.get("err") or "rpc",
        })
    return results


def forget_session_docs(ledger: dict | None = None) -> dict:
    """Forget this sess collection. Idempotent. Never forgets unprefixed ids."""
    led = ledger or load_ledger()
    if not led:
        return {"forgotten": 0, "failed": 0, "skipped": True}
    coll = led["collection"]
    ids = []
    seen = set()
    for d in list(led.get("doc_ids") or []) + list(led.get("pending_forget") or []):
        if d in seen or not has_collection_prefix(d, coll):
            continue
        seen.add(d)
        ids.append(d)
    if not ids:
        led["doc_ids"] = []
        led["pending_forget"] = []
        led["status"] = "empty"
        save_ledger(led)
        return {"forgotten": 0, "failed": 0, "skipped": False}

    if os.environ.get("CUREOLEX_ANAMNESIS_FORGET_LOG", "").strip():
        rows = _forget_stub(ids, coll)
    else:
        rows = _http_forget(ids, coll)

    forgotten, pending = [], []
    for row, doc_id in zip(rows, ids):
        if row.get("ok"):
            forgotten.append(doc_id)
        else:
            pending.append(doc_id)
    led["doc_ids"] = []
    led["pending_forget"] = pending
    led["status"] = "empty" if not pending else "cleanup_failed"
    save_ledger(led)
    return {"forgotten": len(forgotten), "failed": len(pending), "skipped": False}


def rotate_session(forget_previous: bool = True) -> dict:
    """End the current sess (optional forget) and mint a new sess collection."""
    old = load_ledger()
    if forget_previous and old and (old.get("doc_ids") or old.get("pending_forget")):
        forget_session_docs(old)
    fresh = empty_ledger()
    save_ledger(fresh)
    return fresh
