"""Minimal MCP streamable-HTTP client for the two tools this indexer needs.

Deliberately not an MCP SDK dependency: two tool calls, one bearer, easy to mock. Mirrors the
client already used by marmara-mcp / openathens-mcp, including its lesson that the worker may
answer with either a plain JSON body or an SSE frame.
"""
from __future__ import annotations

import json
from typing import Any

import httpx

INIT = {
    "jsonrpc": "2.0", "id": 0, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "anamnesis-indexer", "version": "0.1.0"}},
}


class AnamnesisError(RuntimeError):
    """The worker answered, and the answer was a refusal. Never swallowed."""


def _unwrap(response: httpx.Response) -> dict[str, Any]:
    response.raise_for_status()
    text = response.text
    if "text/event-stream" in response.headers.get("content-type", ""):
        text = next((ln[6:] for ln in text.splitlines() if ln.startswith("data: ")), text)
    data = json.loads(text)
    if "error" in data:
        raise AnamnesisError(f"rpc error: {data['error']}")
    result = data.get("result", data)
    if result.get("isError"):
        raise AnamnesisError(result["content"][0]["text"])
    return json.loads(result["content"][0]["text"])


class AnamnesisClient:
    def __init__(self, base: str, key: str, *, timeout: float = 120.0,
                 transport: httpx.BaseTransport | None = None) -> None:
        self._base = base.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            # Cloudflare's edge rejects the default python-httpx/urllib agent with a 403 on this
            # zone; measured 2026-09-07 while verifying the deploy.
            "User-Agent": "anamnesis-indexer/0.1.0 (+cureonics)",
        }
        self._client = httpx.Client(timeout=timeout, transport=transport)

    def _call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base}/mcp"
        # The worker is stateless, but initialize is cheap and keeps this working if it ever
        # goes back to a session-bearing transport.
        self._client.post(url, json=INIT, headers=self._headers)
        return _unwrap(self._client.post(
            url, headers=self._headers,
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                  "params": {"name": name, "arguments": arguments}},
        ))

    def graph_export(self, collection: str) -> dict[str, Any]:
        return self._call("graph_export", {"collection": collection})

    def upsert_communities(self, collection: str, communities: list[dict[str, Any]]) -> dict[str, Any]:
        return self._call("upsert_communities",
                          {"collection": collection, "communities": communities})

    def close(self) -> None:
        self._client.close()
