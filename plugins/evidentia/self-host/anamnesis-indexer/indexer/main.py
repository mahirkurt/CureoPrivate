"""Nightly driver: export each configured collection's graph, partition it, write it back.

Scope is CONFIG-DRIVEN on purpose. There is no "list every collection" tool and this package does
not ask for one: enumerating other tenants' working sets is exactly the cross-collection leak the
2026-09-07 audit closed. The operator names the durable corpora worth indexing, and only those.

Scratch (`run`/`sess`) collections are deliberately not indexed — they live for one session and
are reaped, so a community partition of them would be obsolete before anyone could read it.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Protocol

from indexer.client import AnamnesisClient, AnamnesisError
from indexer.partition import partition_graph


class Client(Protocol):
    def graph_export(self, collection: str) -> dict[str, Any]: ...
    def upsert_communities(self, collection: str, communities: list[dict[str, Any]]) -> dict[str, Any]: ...


def parse_collections(raw: str) -> list[str]:
    seen, out = set(), []
    for part in (raw or "").split(","):
        c = part.strip()
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _log(event: str, **fields: Any) -> None:
    print(json.dumps({"evt": f"anamnesis-indexer.{event}", **fields}, ensure_ascii=False), flush=True)


def run(client: Client, collections: list[str], *, seed: int = 42) -> dict[str, Any]:
    """Index every collection. One failure never stops the rest — a nightly job that aborts on
    the first bad entry silently stops maintaining everything after it."""
    report: dict[str, Any] = {"ok": 0, "failed": 0, "skipped": 0, "errors": [], "collections": {}}
    for collection in collections:
        try:
            graph = client.graph_export(collection)
            nodes, edges = graph.get("nodes", []), graph.get("edges", [])
            if not nodes:
                _log("skip", collection=collection, reason="empty_graph")
                report["skipped"] += 1
                continue
            parts = partition_graph(nodes, edges, seed=seed)
            if not parts:
                _log("skip", collection=collection, reason="no_communities")
                report["skipped"] += 1
                continue
            res = client.upsert_communities(collection, parts)
            levels = sorted({p["level"] for p in parts})
            _log("indexed", collection=collection, nodes=len(nodes), edges=len(edges),
                 communities=len(parts), levels=levels, replaced=res.get("replaced"))
            report["ok"] += 1
            report["collections"][collection] = {"communities": len(parts), "levels": levels}
        except (AnamnesisError, ValueError, KeyError) as e:
            _log("error", collection=collection, error=str(e)[:300])
            report["failed"] += 1
            report["errors"].append({"collection": collection, "error": str(e)[:300]})
    return report


def cli() -> int:
    base = os.environ.get("ANAMNESIS_URL", "https://anamnesis-mcp.cureonics.workers.dev")
    key = os.environ.get("ANAMNESIS_MCP_API_KEY", "")
    collections = parse_collections(os.environ.get("ANAMNESIS_INDEX_COLLECTIONS", ""))
    if not key:
        _log("abort", reason="ANAMNESIS_MCP_API_KEY missing")
        return 2
    if not collections:
        # Nothing configured is a no-op, not an error: global search is opt-in per corpus.
        _log("noop", reason="ANAMNESIS_INDEX_COLLECTIONS empty")
        return 0
    client = AnamnesisClient(base, key)
    try:
        report = run(client, collections)
    finally:
        client.close()
    _log("done", **{k: v for k, v in report.items() if k != "collections"})
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    sys.exit(cli())
