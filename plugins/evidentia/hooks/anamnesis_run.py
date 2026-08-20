#!/usr/bin/env python3
"""evidentia Anamnesis run-scope helpers — exclusive working set + targeted forget.

Worker 1.2.0 adds collection isolation. Dual-write (keep the prefix working):

  * collection = ``evidentia:run:<12hex>``  (kind ∈ {run, sess, lib})
  * every ingest still prefixes ``doc_id`` ``evrun:<run_id>:``
  * hybrid_query / semantic_search / graph_* are ALLOWED when scoped to this run
  * unscoped hybrid/graph/global search stays DENY
  * cleanup prefers ``forget_collection``; falls back to ledger ``forget_document``
  * HTTP is skipped when EVIDENTIA_ANAMNESIS_FORGET_LOG is set (CI stub)

Secrets are never logged. Fail-open on I/O so a helper bug cannot brick a session.
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

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
LEDGER_NAME = "evidentia-anamnesis-run.json"
PREFIX_HEAD = "evrun:"
RUN_ID_RE = re.compile(r"^[0-9a-f]{12}$")
PREFIX_RE = re.compile(r"^evrun:([0-9a-f]{12}):")
# Slash commands that START a new PRISMA working set. Subcommands
# (fulltext/appraise/kol/connectors/protocol) continue the current run.
NEW_RUN_RE = re.compile(
    r"(?:^|\s)/evidentia(?:-synthesize)?(?:\s|$)",
    re.IGNORECASE,
)
GLOBAL_READ = {"hybrid_query", "graph_neighbors", "subgraph"}
SCOPED_MUTATE = {"ingest_document", "forget_document", "forget_collection"}
SCOPED_SEARCH = {"semantic_search", "list_docs"}
TRIPLE_WRITE = {"upsert_triples"}
OBSERVE = {"corpus_stats"}
PLUGIN_NAME = "evidentia"

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
    "openathens:fetch:",
    "marmara:fetch:",
    "marmara:ebsco",
)
OWN_SCOPE_PREFIXES = ("evidentia:run:", "evrun:")

# User-Agent: Cloudflare bot-filter blocks default Python-urllib (D10).
_UA = "Mozilla/5.0 (evidentia-anamnesis-cleanup)"
_INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "evidentia-anamnesis", "version": "1"},
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


def mint_run_id() -> str:
    return os.urandom(6).hex()


def prefix_for(run_id: str) -> str:
    return f"{PREFIX_HEAD}{run_id}:"


def collection_for(run_id: str) -> str:
    return f"{PLUGIN_NAME}:run:{run_id}"


def collection_matches(collection: str, run_id: str) -> bool:
    return str(collection or "").strip() == collection_for(run_id)


def collection_of(inp: dict) -> str:
    return str((inp or {}).get("collection") or "").strip()


def listed_doc_ids(inp: dict) -> list[str]:
    out, seen = [], set()
    raw = []
    if (inp or {}).get("doc_id") or (inp or {}).get("docId"):
        raw.append((inp.get("doc_id") or inp.get("docId")))
    extra = (inp or {}).get("doc_ids") or (inp or {}).get("docIds") or []
    if isinstance(extra, list):
        raw.extend(extra)
    for item in raw:
        s = str(item or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def all_ids_prefixed(ids: list[str], run_id: str) -> bool:
    return bool(ids) and all(has_run_prefix(s, run_id) for s in ids)


def scoped_doc_id(run_id: str, raw: str) -> str:
    raw = str(raw or "").strip()
    want = prefix_for(run_id)
    if raw.startswith(want):
        return raw
    m = PREFIX_RE.match(raw)
    if m:
        return want + raw[m.end():]
    return want + raw


def has_run_prefix(doc_id: str, run_id: str) -> bool:
    return str(doc_id or "").startswith(prefix_for(run_id))


def ledger_path() -> Path:
    override = os.environ.get("EVIDENTIA_ANAMNESIS_LEDGER", "").strip()
    if override:
        return Path(override)
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if proj:
        return Path(proj) / ".claude" / LEDGER_NAME
    uid = str(os.getuid()) if hasattr(os, "getuid") else "user"
    return Path(tempfile.gettempdir()) / f"evidentia-anamnesis-{uid}" / LEDGER_NAME


def project_claude_dir() -> Path:
    """Project ``.claude/`` root (or temp fallback). Shared by anamnesis + working-set."""
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if proj:
        return Path(proj) / ".claude"
    uid = str(os.getuid()) if hasattr(os, "getuid") else "user"
    return Path(tempfile.gettempdir()) / f"evidentia-claude-{uid}"


def run_dir(run_id: str | None = None) -> Path:
    """Scratch dir for bibliographic working-set artefacts.

    Path: ``.claude/evidentia-run/<run_id>/`` (ledger.json, hits.jsonl,
    screening_table.jsonl). Separate from ``evidentia-anamnesis-run.json``
    (Anamnesis doc_id exclusivity ledger — do not merge).
    """
    override = os.environ.get("EVIDENTIA_WORKING_SET_DIR", "").strip()
    if override:
        return Path(override)
    rid = (run_id or "").strip()
    if not rid:
        led = load_ledger()
        rid = str((led or {}).get("run_id") or "")
    if not RUN_ID_RE.match(rid):
        rid = mint_run_id()
    return project_claude_dir() / "evidentia-run" / rid


def empty_ledger(run_id: str | None = None) -> dict:
    rid = run_id or mint_run_id()
    return {
        "run_id": rid,
        "prefix": prefix_for(rid),
        "collection": collection_for(rid),
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
    rid = str(data.get("run_id") or "")
    if not RUN_ID_RE.match(rid):
        return None
    data["run_id"] = rid
    data["prefix"] = prefix_for(rid)
    data["collection"] = collection_for(rid)
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


def is_new_evidentia_run(prompt: str) -> bool:
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
    prefix = ledger.get("prefix") or prefix_for(rid)
    coll = ledger.get("collection") or collection_for(rid)
    n = len(ledger.get("doc_ids") or [])
    return (
        "[evidentia] Anamnesis münhasır çalışma seti — dual-write: "
        f"`collection={coll}` VE `doc_id` öneki `{prefix}` ({n} kayıtlı id). "
        "ingest_document her ikisini birden gönderir (önek kalkmaz). "
        "hybrid_query / semantic_search / graph_neighbors / subgraph / list_docs "
        f"yalnız `collection={coll}` (ve/veya bu önekli doc_id / doc_ids[]) ile "
        "ALLOWED. Kapsamsız hybrid/graph/global search DENY (NSCLC↔emicizumab "
        "sızıntı sınıfı). corpus_stats küresel gözlemdir, bu koşunun çalışma "
        "seti değildir — list_docs(collection=…) kullan. Koşu bitince hook "
        "forget_collection tercih eder; yoksa ledger forget_document. "
        "Başka kiracının belgesine dokunulmaz. Stop-hook forget YOK."
    )


def peer_scope_prefixes() -> tuple[str, ...]:
    own = set(OWN_SCOPE_PREFIXES)
    return tuple(p for p in ANAMNESIS_FLEET_SCOPE_PREFIXES if p not in own)


def _matches_scope_prefix(value: str, prefixes: tuple[str, ...]) -> bool:
    s = str(value or "").strip()
    return bool(s) and any(s.startswith(p) for p in prefixes)


def is_peer_plugin_scope(inp: dict) -> bool:
    """True when collection / doc_id belongs to another known plugin namespace.

    Pass-through ALLOW so co-installed plugin guards do not mutually DENY.
    Wrong own-run / unscoped / unknown still follow this plugin's DENY rules.
    """
    peers = peer_scope_prefixes()
    coll = collection_of(inp)
    if coll:
        return _matches_scope_prefix(coll, peers)
    ids = listed_doc_ids(inp)
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
    rid = ledger["run_id"]
    prefix = prefix_for(rid)
    want = collection_for(rid)
    coll = collection_of(inp)
    ids = listed_doc_ids(inp)

    if base in OBSERVE:
        return None

    # Another plugin's valid namespace — skip this guard (do not mutual-DENY).
    if is_peer_plugin_scope(inp):
        return None

    if coll and not collection_matches(coll, rid):
        return (
            f"anamnesis münhasır: collection bu koşunun seti değil "
            f"(`{coll}` ≠ `{want}`). Başka kiracı/koşu koleksiyonuna "
            "erişim yok."
        )

    scoped = collection_matches(coll, rid) or all_ids_prefixed(ids, rid)

    if base in GLOBAL_READ:
        if scoped:
            return None
        return (
            "anamnesis münhasır: '{base}' kapsamsız paylaşılan korpusu okur. "
            f"collection='{want}' ve/veya önekli doc_id / doc_ids[] zorunlu "
            f"(`{prefix}<DOI>`). Unscoped hybrid/graph DENY "
            "(NSCLC↔emicizumab sızıntı sınıfı)."
        ).format(base=base)

    if base == "ingest_document":
        doc = str(inp.get("doc_id") or inp.get("docId") or "").strip()
        if not doc:
            return (
                f"anamnesis münhasır: ingest_document doc_id zorunlu; dual-write "
                f"`collection='{want}'` + `doc_id='{prefix}<PMID|DOI>'`."
            )
        if collection_matches(coll, rid) or has_run_prefix(doc, rid):
            return None
        return (
            f"anamnesis münhasır: dual-write — collection='{want}' VE/VEYA "
            f"doc_id='{scoped_doc_id(rid, doc)}'. Öneksiz + koleksiyonsuz "
            "ingest paylaşılmış indekste çakışır / sızdırır."
        )

    if base == "forget_document":
        doc = str(inp.get("doc_id") or inp.get("docId") or "").strip()
        if not doc or not has_run_prefix(doc, rid):
            return (
                "anamnesis münhasır: forget_document yalnız bu koşunun "
                f"önekli id'sini siler (`{prefix}…`). Paylaşılan korpusa "
                "kör wipe yok; başka plugin/koşu belgesi silinmez."
            )
        return None

    if base == "forget_collection":
        if collection_matches(coll, rid):
            return None
        return (
            "anamnesis münhasır: forget_collection yalnız "
            f"`{want}` siler. Küresel wipe yok; başka koleksiyon DENY."
        )

    if base == "list_docs":
        if collection_matches(coll, rid):
            return None
        return (
            f"anamnesis münhasır: list_docs collection='{want}' ister. "
            "corpus_stats çalışma seti değildir."
        )

    if base == "semantic_search":
        if scoped:
            return None
        return (
            "anamnesis münhasır: semantic_search kapsamsız tüm paylaşılan "
            f"indeksi tarar. collection='{want}' ve/veya "
            f"doc_id='{prefix}<PMID|DOI>' / doc_ids[] zorunlu."
        )

    if base == "upsert_triples":
        if collection_matches(coll, rid):
            return None
        triples = inp.get("triples") or []
        if not isinstance(triples, list):
            return "anamnesis münhasır: upsert_triples.triples bir liste olmalı."
        for i, t in enumerate(triples):
            if not isinstance(t, dict):
                return f"anamnesis münhasır: triples[{i}] nesne değil."
            doc = str(t.get("doc_id") or t.get("docId") or "").strip()
            tcoll = str(t.get("collection") or "").strip()
            if collection_matches(tcoll, rid) or has_run_prefix(doc, rid):
                continue
            return (
                "anamnesis münhasır: upsert_triples collection="
                f"'{want}' veya her triple.doc_id `{prefix}…` olmalı."
            )
        return None

    return None


def anamnesis_url() -> str:
    override = os.environ.get("EVIDENTIA_ANAMNESIS_URL", "").strip()
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


def _forget_stub(doc_ids: list[str], collection: str | None = None) -> list[dict]:
    log = os.environ.get("EVIDENTIA_ANAMNESIS_FORGET_LOG", "").strip()
    out = []
    if not log:
        return out
    try:
        Path(log).parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as fh:
            if collection:
                crow = {
                    "collection": collection,
                    "tool": "forget_collection",
                    "ok": True,
                    "stub": True,
                }
                fh.write(json.dumps(crow, ensure_ascii=False) + "\n")
                out.append(crow)
            for doc_id in doc_ids:
                row = {
                    "doc_id": doc_id, "ok": True, "stub": True,
                    "via": "forget_collection" if collection else "forget_document",
                }
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


def _http_forget(doc_ids: list[str]) -> list[dict]:
    """Best-effort MCP forget_document. Never prints the bearer value."""
    if os.environ.get("EVIDENTIA_ANAMNESIS_NO_NETWORK"):
        return [{"doc_id": d, "ok": False, "skipped": "no_network"} for d in doc_ids]
    key = os.environ.get("ANAMNESIS_MCP_API_KEY", "").strip()
    if not key:
        return [{"doc_id": d, "ok": False, "skipped": "no_key"} for d in doc_ids]
    url = anamnesis_url()
    sid = None
    results = []

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
        return [{"doc_id": d, "ok": False, "err": init.get("err", "init")} for d in doc_ids]
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, notify=True)
    for doc_id in doc_ids:
        r = post({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "forget_document", "arguments": {"doc_id": doc_id}},
        })
        ok = bool(r.get("ok"))
        body = r.get("json") or {}
        if body.get("error") or (body.get("result") or {}).get("isError"):
            ok = False
        results.append({"doc_id": doc_id, "ok": ok, "err": None if ok else r.get("err") or "rpc"})
    return results


def _rpc_is_error(body: dict | None) -> bool:
    if not body:
        return True
    if body.get("error"):
        return True
    result = body.get("result") or {}
    return bool(result.get("isError"))


def _http_forget_collection(collection: str) -> dict:
    """Best-effort MCP forget_collection. Never prints the bearer value."""
    if os.environ.get("EVIDENTIA_ANAMNESIS_NO_NETWORK"):
        return {"ok": False, "skipped": "no_network"}
    key = os.environ.get("ANAMNESIS_MCP_API_KEY", "").strip()
    if not key:
        return {"ok": False, "skipped": "no_key"}
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
        return {"ok": False, "err": init.get("err", "init")}
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, notify=True)
    r = post({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "forget_collection", "arguments": {"collection": collection}},
    })
    if not r.get("ok") or _rpc_is_error(r.get("json")):
        return {"ok": False, "err": r.get("err") or "rpc"}
    return {"ok": True}


def forget_run_docs(ledger: dict | None = None) -> dict:
    """Forget this run's working set. Prefers forget_collection; falls back to ledger ids."""
    led = ledger or load_ledger()
    if not led:
        return {"forgotten": 0, "failed": 0, "skipped": True}
    rid = led["run_id"]
    coll = led.get("collection") or collection_for(rid)
    ids = []
    seen = set()
    for d in list(led.get("doc_ids") or []) + list(led.get("pending_forget") or []):
        if d in seen or not has_run_prefix(d, rid):
            continue
        seen.add(d)
        ids.append(d)
    if not ids:
        led["doc_ids"] = []
        led["pending_forget"] = []
        led["status"] = "empty"
        save_ledger(led)
        return {"forgotten": 0, "failed": 0, "skipped": False, "collection": coll}

    if os.environ.get("EVIDENTIA_ANAMNESIS_FORGET_LOG", "").strip():
        rows = _forget_stub(ids, collection=coll)
        pending = []
        forgotten = ids
    else:
        coll_res = _http_forget_collection(coll)
        if coll_res.get("ok"):
            rows = [{"doc_id": d, "ok": True, "via": "forget_collection"} for d in ids]
            forgotten, pending = list(ids), []
        else:
            rows = _http_forget(ids)
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
    return {
        "forgotten": len(forgotten),
        "failed": len(pending),
        "skipped": False,
        "collection": coll,
        "via": "forget_collection" if not pending else "forget_document",
    }


def rotate_run(forget_previous: bool = True) -> dict:
    """End the current working set (optional forget) and mint a new run_id."""
    old = load_ledger()
    if forget_previous and old and (old.get("doc_ids") or old.get("pending_forget")):
        forget_run_docs(old)
    fresh = empty_ledger()
    save_ledger(fresh)
    return fresh
