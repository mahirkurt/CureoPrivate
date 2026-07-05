#!/usr/bin/env python3
"""Repo-local GECTurk-compatible endpoint for local/CI Turkish audit runs.

Stdlib-only HTTP server (http.server) exposing the deterministic tr_sciaudit
core over a `/check` POST. Intended for LOCAL or CI use only — it is NOT a
public API and NEVER assumed by the plugin's remote (claude.ai-web) path. The
web path uses the deterministic core directly; this server exists so the
`--enable-gecturk --gecturk-url http://127.0.0.1:<port>/check` provider layer
has a real self-host endpoint to talk to when a developer wants it.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import tr_sciaudit

MAX_BODY_BYTES = 1_000_000


def audit_text_payload(text: str, strictness: str = "certification") -> dict[str, Any]:
    lines = [(lineno, line.rstrip("\n")) for lineno, line in enumerate(text.splitlines(), start=1)]
    if not lines and text:
        lines = [(1, text)]
    paragraphs = tr_sciaudit.build_paragraphs(lines)
    metrics = tr_sciaudit.calculate_metrics(paragraphs)
    whitelist = set(tr_sciaudit.COMMON_ABBREVIATIONS)
    issues = tr_sciaudit.detect_issues(lines, paragraphs, strictness, whitelist)
    counts = tr_sciaudit.issue_counts(issues)
    return {
        "service": "gecturk-selfhost",
        "engine": "sci-audit-deterministic-fallback",
        "strictness": strictness,
        "metrics": asdict(metrics),
        "issue_counts": counts,
        "issues": [asdict(issue) for issue in issues[:200]],
        "truncated": len(issues) > 200,
    }


class GECTurkSelfHostHandler(BaseHTTPRequestHandler):
    server_version = "SciAuditGECTurkSelfHost/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"ok": True, "service": "gecturk-selfhost"})
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/check":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length > MAX_BODY_BYTES:
            self._send_json(413, {"ok": False, "error": "payload_too_large"})
            return
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        text = payload.get("text")
        if not isinstance(text, str):
            self._send_json(400, {"ok": False, "error": "text_required"})
            return
        strictness = payload.get("strictness", "certification")
        if strictness not in {"quick", "certification"}:
            self._send_json(400, {"ok": False, "error": "invalid_strictness"})
            return
        self._send_json(200, audit_text_payload(text, strictness))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a repo-local GECTurk-compatible audit endpoint (local/CI only).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"gecturk-selfhost listening on http://{args.host}:{args.port}/check")
    server = ThreadingHTTPServer((args.host, args.port), GECTurkSelfHostHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
