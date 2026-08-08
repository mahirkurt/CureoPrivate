#!/usr/bin/env python3
"""Section-chunk SKILL.md + references/*.md and upsert into the evidentia-kb index
via the Worker's Bearer-gated kb_upsert tool (setup / refresh).

Usage:
  export EVIDENTIA_KB_MCP_API_KEY=$(doppler secrets get EVIDENTIA_KB_MCP_API_KEY -p cureohub -c dev_personal --plain)
  python3 scripts/kb_ingest.py
"""
import os, re, json, glob, hashlib, urllib.request

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(PLUGIN_ROOT, "skills", "medical-research")
URL = os.environ.get("EVIDENTIA_KB_URL", "https://evidentia-kb-mcp.cureonics.workers.dev/mcp")
KEY = os.environ["EVIDENTIA_KB_MCP_API_KEY"]
SID = {"v": None}


def call(method, params=None, notif=False):
    body = {"jsonrpc": "2.0", "method": method}
    if not notif:
        body["id"] = 1
    if params is not None:
        body["params"] = params
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST")
    for k, v in {
        "authorization": "Bearer " + KEY,
        "user-agent": "Mozilla/5.0 (kb-ingest)",  # CF bot-filter blocks default Python-urllib UA
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
    }.items():
        req.add_header(k, v)
    if SID["v"]:
        req.add_header("mcp-session-id", SID["v"])
    resp = urllib.request.urlopen(req, timeout=60)
    if resp.headers.get("mcp-session-id"):
        SID["v"] = resp.headers["mcp-session-id"]
    raw = resp.read().decode()
    if not raw.strip():
        return None  # e.g. 202 Accepted for a notification — empty body
    if "text/event-stream" in (resp.headers.get("content-type") or ""):
        for ln in raw.splitlines():
            if ln.startswith("data:"):
                try:
                    return json.loads(ln[5:].strip())
                except Exception:
                    pass
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def chunks():
    """Yield {id,file,section,ord,text} by splitting each file on ##/### headings."""
    files = [os.path.join(SKILL_DIR, "SKILL.md")] + sorted(
        f for f in glob.glob(os.path.join(SKILL_DIR, "references", "*.md"))
        # knowledge-map.md is the routing index, not knowledge content — its concept-dense
        # chunks match every query and crowd out the real layer files in kb_search. Exclude it.
        if os.path.basename(f) != "knowledge-map.md"
    )
    head_re = re.compile(r"(?m)^(#{2,3}\s+.*)$")
    for fp in files:
        fname = os.path.basename(fp)
        txt = open(fp, encoding="utf-8").read()
        parts = head_re.split(txt)  # [pre, head1, body1, head2, body2, ...]
        segments = []
        if parts[0].strip():
            segments.append((fname, parts[0]))  # preamble before first heading
        for i in range(1, len(parts) - 1, 2):
            head = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            segments.append((head, body))
        ord_ = 0
        for head, body in segments:
            text = (head + "\n" + body).strip()
            if len(text) < 30:
                continue
            section = head.lstrip("# ").strip()[:120] or fname
            cid = f"{fname}#{ord_}:" + hashlib.md5((fname + head).encode()).hexdigest()[:8]
            yield {"id": cid, "file": fname, "section": section, "ord": ord_, "text": text[:4000]}
            ord_ += 1


def main():
    call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                        "clientInfo": {"name": "kb-ingest", "version": "1"}})
    call("notifications/initialized", notif=True)
    # FORGET-THEN-UPSERT, per file (2026-08-08). kb_upsert is INSERT OR REPLACE and the chunk id
    # embeds md5(file + heading), so a RENAMED or DELETED section is never overwritten — it orphans
    # a row that kb_search keeps returning. This was not theoretical: on 2026-08-08 the live index
    # still served `connector-registry.md § 3.5 annas-mcp` with the retired `article_download`
    # API, and `fulltext-retrieval.md § Tier 3 — annas-mcp`, a heading that no longer exists.
    # Dropping each file's chunks immediately before re-adding them makes the index a faithful
    # mirror of the corpus instead of an append-only pile.
    by_file = {}
    for c in chunks():
        by_file.setdefault(c["file"], []).append(c)

    n, errs, purged = 0, 0, 0
    for fname, cs in by_file.items():
        res = call("tools/call", {"name": "kb_forget", "arguments": {"file": fname}})
        body = (res or {}).get("result", {})
        if body.get("isError"):
            # A failed purge would silently leave stale rows behind the fresh ones — say so loudly
            # rather than printing a clean DONE over a half-updated index.
            errs += 1
            print(f"  PURGE-ERR {fname}: {body}")
        else:
            try:
                deleted = json.loads(body["content"][0]["text"])["deleted"]["chunks"]
            except Exception:
                deleted = 0
            purged += deleted
            print(f"  {fname}: dropped {deleted} existing row(s)", flush=True)
        for c in cs:
            res = call("tools/call", {"name": "kb_upsert", "arguments": c})
            if isinstance(res, dict) and res.get("result", {}).get("isError"):
                errs += 1
                print("  ERR", c["id"], res.get("result"))
            n += 1
            if n % 25 == 0:
                print(f"  upserted {n}…", flush=True)
    # `purged` counts EVERY pre-existing row for these files, not only the stale ones — the rebuild
    # is drop-then-add, so it cannot distinguish them. The stale subset is whatever no longer has a
    # matching heading in the corpus; the point is that after this run the index mirrors the corpus.
    print(f"DONE — {len(by_file)} files · {purged} pre-existing rows dropped · {n} current chunks "
          f"ingested ({errs} errors)")


if __name__ == "__main__":
    main()
