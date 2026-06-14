"""Mock Figma API server for sandbox-friendly RestTransport integration tests.

Lightweight in-process HTTP server built on stdlib ``http.server``.
Implements just enough of the Figma REST API surface to exercise the
``RestTransport._dispatch_http`` path: variables CRUD, file get,
canned error responses for each HTTP code we map.

Usage::

    from tests.fixtures.mock_figma_server import MockFigmaServer

    with MockFigmaServer() as server:
        rest = ff.RestTransport(pat="test-pat", base_url=server.url,
                                dry_run=False)
        rest.begin_session()
        rest.create_variable_collection(...)
        # → live HTTP roundtrip through urllib → mock server → response

The server records every received request on ``server.request_log``
so tests can assert exactly which HTTP calls were made.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable


class MockFigmaServer:
    """In-process HTTP server emulating a subset of the Figma REST API.

    Default behavior: every endpoint returns a successful canned
    response that the test can override via :meth:`set_response`. The
    server runs on an OS-assigned port (``localhost:<random>``); the
    public URL is exposed at :attr:`url`.

    Thread-safe: the server runs in a background thread; tests
    interact with it from the main thread.

    Use as a context manager (preferred) or call :meth:`start` /
    :meth:`stop` explicitly.
    """

    def __init__(self) -> None:
        self.request_log: list[dict[str, Any]] = []
        self._log_lock = threading.Lock()  # v1.3 batch dispatch: thread-safe log
        self._handlers: dict[tuple[str, str], Callable[[], tuple[int, dict, dict]]] = {}
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port: int = 0
        self._install_defaults()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def url(self) -> str:
        return f"http://localhost:{self.port}"

    def start(self) -> None:
        handler_class = _make_handler(self)
        self._server = HTTPServer(("localhost", 0), handler_class)
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

    def __enter__(self) -> "MockFigmaServer":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def set_response(
        self,
        method: str,
        path_pattern: str,
        *,
        status: int = 200,
        body: dict | str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Override the canned response for one (method, path) pair.

        ``path_pattern`` may include literal path-prefix matching
        (e.g. ``"/v1/files/"`` matches every file fetch). The most
        specific (longest) registered pattern wins.

        For canned error responses, pass any 4xx/5xx ``status`` and
        a ``body`` describing the error.
        """
        def handler() -> tuple[int, dict, dict]:
            return (
                status,
                headers or {"Content-Type": "application/json"},
                body or {},
            )

        self._handlers[(method, path_pattern)] = handler

    def set_response_sequence(
        self,
        method: str,
        path_pattern: str,
        sequence: list[tuple[int, dict, dict]],
    ) -> None:
        """Override responses with an ordered queue.

        Each request to ``(method, path_pattern)`` pops the next tuple
        ``(status, headers, body)``; once exhausted, the last entry is
        replayed. Thread-safe via the same lock that guards
        ``request_log``. v1.3.0-beta.1 — enables 429-then-200 retry
        scenarios in batch dispatch tests.
        """
        seq = list(sequence)
        idx = {"n": 0}

        def handler() -> tuple[int, dict, dict]:
            with self._log_lock:
                i = min(idx["n"], len(seq) - 1)
                idx["n"] += 1
            status, hdrs, body = seq[i]
            return (status,
                    {"Content-Type": "application/json", **hdrs},
                    body)

        self._handlers[(method, path_pattern)] = handler

    def reset_log(self) -> None:
        self.request_log.clear()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _install_defaults(self) -> None:
        """Register default 200-OK handlers for common Figma endpoints."""
        self.set_response("POST", "/v1/files/", body={
            "meta": {"variableCollections": {}, "variables": {}},
        })
        self.set_response("GET", "/v1/files/", body={
            "name": "Mock Figma File",
            "lastModified": "2026-05-27T05:00:00Z",
        })
        self.set_response("GET", "/v1/files/local-variables", body={
            "meta": {
                "variableCollections": {},
                "variables": {},
            },
        })
        self.set_response("POST", "/v1/code_connect", body={
            "id": "mock-ccm-abc123",
        })

    def _resolve_handler(
        self, method: str, path: str
    ) -> Callable[[], tuple[int, dict, dict]] | None:
        """Find the longest-prefix handler for (method, path)."""
        candidates = [
            (m, p) for (m, p) in self._handlers
            if m == method and (path.startswith(p) or path == p)
        ]
        if not candidates:
            return None
        # Longest pattern wins
        candidates.sort(key=lambda mp: len(mp[1]), reverse=True)
        return self._handlers[candidates[0]]


def _make_handler(server_ref: MockFigmaServer):
    """Build a BaseHTTPRequestHandler subclass closed over ``server_ref``."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A003
            # Silence default stderr noise
            return

        def _record(self, body: bytes | None) -> None:
            entry = {
                "method": self.command,
                "path": self.path,
                "headers": dict(self.headers.items()),
                "body": body.decode("utf-8") if body else None,
            }
            with server_ref._log_lock:
                server_ref.request_log.append(entry)

        def _serve(self, method: str) -> None:
            length = int(self.headers.get("Content-Length", 0) or 0)
            body = self.rfile.read(length) if length > 0 else None
            self._record(body)

            handler = server_ref._resolve_handler(method, self.path)
            if handler is None:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "no mock handler registered"}')
                return

            status, headers, response_body = handler()
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()
            if isinstance(response_body, dict):
                self.wfile.write(json.dumps(response_body).encode("utf-8"))
            elif isinstance(response_body, str):
                self.wfile.write(response_body.encode("utf-8"))

        def do_GET(self):     return self._serve("GET")
        def do_POST(self):    return self._serve("POST")
        def do_PATCH(self):   return self._serve("PATCH")
        def do_DELETE(self):  return self._serve("DELETE")
        def do_PUT(self):     return self._serve("PUT")

    return Handler


__all__ = ["MockFigmaServer"]
