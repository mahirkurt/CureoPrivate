"""figma-forge ``RestTransport`` — v1.1.0-alpha skeleton.

Adapter for the Figma REST API. v1.1.0-alpha ships **structural
support**: the adapter loads credentials, knows which operations the
REST API supports (Variables endpoints; Code Connect endpoints; file
metadata reads), and stages each call in an in-memory queue.

**Live HTTP execution is staged for v1.1.0 GA** — the alpha-grade
adapter exists so the router and capability matrix tests can verify
correct behavior, and so downstream code can be written against the
final Protocol shape. Operations that would require an HTTP call are
captured in :attr:`pending_calls` instead.

When v1.1.0 GA ships, the ``_dispatch_http`` helper at the bottom will
be enabled and the adapter will issue real PATCH/POST requests
against ``https://api.figma.com``.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .capability_matrix import ADAPTER_REST, supported_operations
from .backoff import BackoffPolicy
from .batch_policy import BatchPolicy
from .errors import (
    AuthenticationError,
    CapabilityUnsupportedError,
    NotFoundError,
)
from .protocol import (
    AuthRequirement,
    CodeConnectMapping,
    CodeConnectRef,
    CollectionRef,
    ComponentGeometry,
    ComponentRef,
    ComponentSetRef,
    InstanceRef,
    Effect,
    FileKind,
    FileRef,
    PageRef,
    Paint,
    PublishRef,
    SessionResult,
    SessionToken,
    StyleRef,
    TextStyleProperties,
    VariableRef,
    VariableType,
    VariableValue,
    VariantSpec,
)


@dataclass
class RestTransport:
    """Figma REST API adapter — alpha skeleton (operations queued, not yet sent).

    Parameters
    ----------
    pat:
        The Figma Personal Access Token. When ``None``, the adapter
        reads it from the ``FIGMA_PERSONAL_ACCESS_TOKEN`` environment
        variable at construction time.
    base_url:
        The Figma REST API base URL. Defaults to the public endpoint;
        override for testing against staging or a local mock.
    dry_run:
        When ``True`` (v1.1.0-alpha **default**), operations are
        queued in :attr:`pending_calls` rather than dispatched over
        HTTP. The v1.1.0 GA release will default to ``False``.
    """

    pat: str | None = None
    base_url: str = "https://api.figma.com"
    dry_run: bool = True  # v1.1.0-alpha; GA flips to False
    backoff: "BackoffPolicy | None" = None
    batch: "BatchPolicy | None" = None
    #: Optional cross-build observation log (v1.5.0-beta.1). When set
    #: together with an AdaptiveConcurrency policy, the transport
    #: seeds its observation history from the log at construction and
    #: appends each new observation on commit_session — extending
    #: multi-batch smoothing across process boundaries.
    observation_log: "ObservationLog | None" = None
    pending_calls: list[dict[str, Any]] = field(default_factory=list)
    _current_session: SessionToken | None = None
    _resolved_pat: str | None = field(default=None, init=False, repr=False)
    #: Injectable sleep function (default time.sleep); tests pass a
    #: no-op to avoid real waits. Not part of the public API.
    _sleep_fn: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        # Resolve PAT once at construction; never re-read mid-pipeline
        # to avoid surprising behavior if the env var mutates.
        if self.pat is not None:
            self._resolved_pat = self.pat
        else:
            self._resolved_pat = os.environ.get("FIGMA_PERSONAL_ACCESS_TOKEN")
        # Default sleep is the real one; tests inject a no-op.
        if self._sleep_fn is None:
            import time
            self._sleep_fn = time.sleep
        # Per-batch telemetry — populated by _dispatch_with_retry under
        # the lock, reset at the start of _dispatch_batch, harvested
        # at its end. v1.4.0-beta.1 adaptive concurrency.
        import threading
        from collections import deque
        self._batch_telemetry_lock = threading.Lock()
        self._batch_telemetry = self._fresh_telemetry()
        # v1.5.0-alpha.2: bounded ring of recent observations for
        # multi-batch smoothing. maxlen tracks AdaptiveConcurrency.window
        # when adaptive is set; for no-adaptive runs the deque exists
        # but stays empty (zero overhead).
        window = (self.batch.adaptive.window
                  if (self.batch is not None and self.batch.adaptive is not None)
                  else 1)
        self._observation_history: deque = deque(maxlen=window)
        # v1.5.0-beta.1: seed history from the cross-build log so
        # smoothing spans process boundaries. Only meaningful when an
        # adaptive policy is set (otherwise history is never consulted).
        if (self.observation_log is not None
                and self.batch is not None
                and self.batch.adaptive is not None):
            for obs in self.observation_log.read_recent(window):
                self._observation_history.append(obs)

    @staticmethod
    def _fresh_telemetry() -> dict[str, float]:
        return {
            "requests_total": 0,
            "requests_429": 0,
            "requests_5xx": 0,
            "retry_after_seconds_max": 0.0,
        }

    # ------------------------------------------------------------------
    # Identity & capability
    # ------------------------------------------------------------------

    def adapter_id(self) -> str:
        return ADAPTER_REST

    def supports(self, operation_name: str) -> bool:
        return operation_name in supported_operations(ADAPTER_REST)

    def authentication_required(self) -> AuthRequirement:
        return AuthRequirement(
            needs_credentials=True,
            credential_kind="figma-pat",
            environment_variable="FIGMA_PERSONAL_ACCESS_TOKEN",
        )

    def has_credentials(self) -> bool:
        return bool(self._resolved_pat)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def begin_session(self) -> SessionToken:
        if not self.has_credentials():
            raise AuthenticationError(
                "Figma PAT not set; export FIGMA_PERSONAL_ACCESS_TOKEN "
                "or pass pat=... to RestTransport constructor.",
                operation="begin_session", adapter_id=self.adapter_id(),
            )
        token = SessionToken(
            adapter_id=ADAPTER_REST,
            started_at=self._now(),
            token=f"rest-{uuid.uuid4().hex[:12]}",
        )
        self._current_session = token
        return token

    def commit_session(self, token: SessionToken) -> SessionResult:
        # Run any deferred (batched) dispatches in parallel.
        deferred = [c for c in self.pending_calls if c.get("_deferred")]
        failed = 0
        observation: "ConcurrencyObservation | None" = None
        if deferred and self.batch is not None and not self.dry_run:
            # Reset telemetry for this batch
            with self._batch_telemetry_lock:
                self._batch_telemetry = self._fresh_telemetry()
            failed = self._dispatch_batch(deferred)
            # Harvest telemetry → ConcurrencyObservation (if adaptive)
            if self.batch.adaptive is not None:
                observation = self._build_observation()
                # v1.5.0-beta.1: persist to cross-build log if attached.
                if self.observation_log is not None:
                    self.observation_log.append(observation)
            # Clear the deferred flag once handled
            for c in deferred:
                c.pop("_deferred", None)

        # In dry-run, we don't actually dispatch; the queue is the result.
        applied = 0 if self.dry_run else len(self.pending_calls)
        return SessionResult(
            token=token,
            operations_applied=applied,
            operations_failed=failed,
            artifacts={
                "pending_calls": str(len(self.pending_calls)),
                "dry_run": str(self.dry_run),
                "batch_dispatched": str(len(deferred)),
                "max_concurrency": str(
                    self.batch.max_concurrency if self.batch else 1
                ),
            },
            adaptive_observation=observation,
        )

    def _build_observation(self) -> "ConcurrencyObservation":
        """Harvest the per-batch counters into a ConcurrencyObservation.

        Reads the counters under the lock, appends the raw single-batch
        observation to ``_observation_history`` (bounded by
        ``adaptive.window``), then computes the aggregate recommendation
        across the deque's contents. Called by :meth:`commit_session`
        only when an :class:`AdaptiveConcurrency` policy is attached.

        v1.5.0-alpha.2: when ``window > 1``, the recommendation is
        smoothed across consecutive batches; ``window == 1`` reduces
        to v1.4 behavior (deque of size 1 → aggregate equals the single
        latest observation).
        """
        from .adaptive_concurrency import ConcurrencyObservation
        assert self.batch is not None and self.batch.adaptive is not None
        with self._batch_telemetry_lock:
            t = dict(self._batch_telemetry)  # snapshot

        # Build the raw single-batch observation. Its
        # ``recommended_max_concurrency`` is the standalone
        # recommendation (computed without history). This is what
        # gets stored in history; the *returned* observation may
        # carry a different aggregate recommendation.
        single_new, single_rationale = self.batch.adaptive.recommend(
            current=self.batch.max_concurrency,
            requests_total=int(t["requests_total"]),
            requests_429=int(t["requests_429"]),
        )
        raw = ConcurrencyObservation(
            requests_total=int(t["requests_total"]),
            requests_429=int(t["requests_429"]),
            requests_5xx=int(t["requests_5xx"]),
            retry_after_seconds_max=float(t["retry_after_seconds_max"]),
            current_max_concurrency=self.batch.max_concurrency,
            recommended_max_concurrency=single_new,
            rationale=single_rationale,
        )
        # Append to bounded history (deque auto-drops oldest).
        self._observation_history.append(raw)

        # Aggregate over history (which now includes this batch).
        # For window==1, this is identical to the single-batch path.
        agg_new, agg_rationale = self.batch.adaptive.recommend_aggregate(
            current=self.batch.max_concurrency,
            observations=self._observation_history,
        )
        return ConcurrencyObservation(
            requests_total=raw.requests_total,
            requests_429=raw.requests_429,
            requests_5xx=raw.requests_5xx,
            retry_after_seconds_max=raw.retry_after_seconds_max,
            current_max_concurrency=self.batch.max_concurrency,
            recommended_max_concurrency=agg_new,
            rationale=agg_rationale,
        )

    def _dispatch_batch(self, deferred: list[dict[str, Any]]) -> int:
        """Dispatch all deferred calls in parallel via ThreadPoolExecutor.

        Each worker runs its own BackoffPolicy retry schedule
        independently (the policy is pure arithmetic — no shared
        state). Per-call exceptions are recorded on the call dict's
        ``error`` key and counted toward ``operations_failed``; the
        batch completes all scheduled work regardless of individual
        failures (best-effort semantics, matching the v1.x
        precedent).
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        assert self.batch is not None  # narrowed by caller
        max_workers = max(1, self.batch.max_concurrency)
        failed = 0
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(self._dispatch_one_safe, c): c
                       for c in deferred}
            for fut in as_completed(futures):
                # _dispatch_one_safe records errors on the call dict
                # and never raises. Count failures.
                if futures[fut].get("error"):
                    failed += 1
        return failed

    def _dispatch_one_safe(self, call: dict[str, Any]) -> None:
        """Run ``_dispatch_with_retry`` and capture any exception on
        the call dict — never raise. Workers use this to keep the
        thread pool healthy across per-call failures."""
        try:
            self._dispatch_with_retry(call)
        except Exception as e:  # noqa: BLE001 — caller wants opaque capture
            call["error"] = repr(e)

    def rollback_session(self, token: SessionToken) -> None:
        self.pending_calls.clear()
        self._current_session = None

    # ------------------------------------------------------------------
    # File-level — partial REST support
    # ------------------------------------------------------------------

    def create_file(self, *, name: str, file_kind: FileKind) -> FileRef:
        # POST /v1/files (Enterprise only)
        self._queue("POST", "/v1/files", body={
            "name": name, "file_kind": file_kind,
        })
        # In alpha: return a placeholder FileRef
        return FileRef(key=f"pending-{uuid.uuid4().hex[:8]}",
                       name=name, kind=file_kind)

    def get_file(self, *, key: str) -> FileRef:
        call: dict[str, Any] = {
            "method": "GET", "path": f"/v1/files/{key}",
            "body": None, "queued_at": self._now(),
        }
        last_modified = ""
        name = ""
        if not self.dry_run:
            self._dispatch_with_retry(call)
            payload = call.get("response_json") or {}
            last_modified = str(payload.get("lastModified", ""))
            name = str(payload.get("name", ""))
        self.pending_calls.append(call)
        return FileRef(key=key, name=name, kind="generic",
                       last_modified=last_modified)

    def publish_library(
        self, *, file_key: str, changelog: str
    ) -> PublishRef:
        raise CapabilityUnsupportedError(
            "Library publishing has no REST endpoint; manual UI action only.",
            operation="publish_library", adapter_id=self.adapter_id(),
        )

    # ------------------------------------------------------------------
    # Variables — the REST adapter's primary surface
    # ------------------------------------------------------------------

    def create_variable_collection(
        self, *, file_key: str, name: str, modes: list[str]
    ) -> CollectionRef:
        # POST /v1/files/{file_key}/variables (Enterprise)
        cid = f"VariableCollectionId:pending-{uuid.uuid4().hex[:8]}"
        self._queue("POST", f"/v1/files/{file_key}/variables", body={
            "variableCollections": [{
                "action": "CREATE",
                "id": cid,
                "name": name,
                "modes": [{"action": "CREATE", "modeId": f"mode-{i}",
                            "name": m} for i, m in enumerate(modes)],
            }],
        })
        return CollectionRef(file_key=file_key, collection_id=cid,
                             name=name, modes=tuple(modes))

    def get_variable_collection(
        self, *, file_key: str, name: str
    ) -> CollectionRef | None:
        # GET /v1/files/{file_key}/variables/local
        self._queue("GET", f"/v1/files/{file_key}/variables/local")
        # In dry-run, return None to exercise the create path
        return None

    def create_variable(
        self, *, collection_ref: CollectionRef, name: str,
        type: VariableType, values_per_mode: dict[str, VariableValue],
    ) -> VariableRef:
        vid = f"VariableId:pending-{uuid.uuid4().hex[:8]}"
        self._queue("POST",
                    f"/v1/files/{collection_ref.file_key}/variables",
                    body={
                        "variables": [{
                            "action": "CREATE",
                            "id": vid,
                            "name": name,
                            "variableCollectionId": collection_ref.collection_id,
                            "resolvedType": type,
                        }],
                        "variableModeValues": [
                            {"variableId": vid,
                             "modeId": mode_id,
                             "value": value}
                            for mode_id, value in values_per_mode.items()
                        ],
                    })
        return VariableRef(
            collection_id=collection_ref.collection_id,
            variable_id=vid, name=name, type=type,
        )

    def update_variable(
        self, *, variable_ref: VariableRef,
        values_per_mode: dict[str, VariableValue],
    ) -> None:
        self._queue("POST",
                    "/v1/files/{file_key}/variables",
                    body={
                        "variableModeValues": [
                            {"variableId": variable_ref.variable_id,
                             "modeId": mode_id,
                             "value": value}
                            for mode_id, value in values_per_mode.items()
                        ],
                    })

    def create_alias_reference(
        self, *, source_var: VariableRef, target_var: VariableRef,
        mode_id: str,
    ) -> None:
        self._queue("POST",
                    "/v1/files/{file_key}/variables",
                    body={
                        "variableModeValues": [{
                            "variableId": source_var.variable_id,
                            "modeId": mode_id,
                            "value": {"type": "VARIABLE_ALIAS",
                                      "id": target_var.variable_id},
                        }],
                    })

    # ------------------------------------------------------------------
    # Styles — REST does NOT support paint/text/effect styles
    # ------------------------------------------------------------------

    def create_paint_style(
        self, *, file_key: str, name: str, paints: list[Paint]
    ) -> StyleRef:
        raise CapabilityUnsupportedError(
            "Figma styles are not exposed in REST API.",
            operation="create_paint_style", adapter_id=self.adapter_id(),
        )

    def create_text_style(
        self, *, file_key: str, name: str, properties: TextStyleProperties
    ) -> StyleRef:
        raise CapabilityUnsupportedError(
            operation="create_text_style", adapter_id=self.adapter_id(),
            message="Figma styles are not exposed in REST API.",
        )

    def create_effect_style(
        self, *, file_key: str, name: str, effects: list[Effect]
    ) -> StyleRef:
        raise CapabilityUnsupportedError(
            operation="create_effect_style", adapter_id=self.adapter_id(),
            message="Figma styles are not exposed in REST API.",
        )

    # ------------------------------------------------------------------
    # Components / pages — REST cannot create
    # ------------------------------------------------------------------

    def create_page(self, *, file_key: str, name: str) -> PageRef:
        raise CapabilityUnsupportedError(
            operation="create_page", adapter_id=self.adapter_id(),
            message="REST API has no endpoint for page creation.",
        )

    def create_component(
        self, *, page_ref: PageRef, name: str,
        geometry: ComponentGeometry,
    ) -> ComponentRef:
        raise CapabilityUnsupportedError(
            operation="create_component", adapter_id=self.adapter_id(),
            message="REST API has no endpoint for component creation.",
        )

    def create_component_set(
        self, *, page_ref: PageRef, name: str,
        variants: list[VariantSpec],
    ) -> ComponentSetRef:
        raise CapabilityUnsupportedError(
            operation="create_component_set", adapter_id=self.adapter_id(),
            message="REST API has no endpoint for ComponentSet creation.",
        )

    def set_component_property(
        self, *, component_ref: ComponentRef, key: str, value: Any,
    ) -> None:
        raise CapabilityUnsupportedError(
            operation="set_component_property", adapter_id=self.adapter_id(),
            message="REST API does not expose component property writes.",
        )

    def import_svg_as_component(
        self, *, page_ref: PageRef, name: str,
        svg_source: str, canonical_size: tuple[int, int],
    ) -> ComponentRef:
        raise CapabilityUnsupportedError(
            operation="import_svg_as_component", adapter_id=self.adapter_id(),
            message="SVG import requires the Figma plugin runtime.",
        )

    def update_component_description(
        self, *, component_ref: ComponentRef,
        description: str, doc_links: list[str],
    ) -> None:
        raise CapabilityUnsupportedError(
            operation="update_component_description",
            adapter_id=self.adapter_id(),
            message="REST API does not expose component description writes.",
        )

    # ------------------------------------------------------------------
    # Instance composition — unsupported through REST
    # ------------------------------------------------------------------

    def place_instance(
        self, *, parent_ref: ComponentRef, component_ref: ComponentRef,
        position: tuple[int, int],
    ) -> InstanceRef:
        raise CapabilityUnsupportedError(
            operation="place_instance", adapter_id=self.adapter_id(),
            message="Figma REST API has no write endpoint for creating "
                    "instances; use the plugin or MCP channel.",
        )

    def set_instance_property(
        self, *, instance_ref: InstanceRef, key: str, value: str,
    ) -> None:
        raise CapabilityUnsupportedError(
            operation="set_instance_property", adapter_id=self.adapter_id(),
            message="Figma REST API cannot set instance properties; "
                    "use the plugin or MCP channel.",
        )

    # ------------------------------------------------------------------
    # Code Connect — REST supports
    # ------------------------------------------------------------------

    def attach_code_connect(
        self, *, component_ref: ComponentRef,
        mapping: CodeConnectMapping,
    ) -> CodeConnectRef:
        mid = f"ccm-{uuid.uuid4().hex[:8]}"
        self._queue("POST",
                    f"/v1/code_connect",
                    body={
                        "componentId": component_ref.node_id,
                        "framework": mapping.framework,
                        "importStatement": mapping.import_statement,
                        "codeExample": mapping.code_example,
                        "propsMapping": mapping.props_mapping,
                    })
        return CodeConnectRef(component_node_id=component_ref.node_id,
                              mapping_id=mid, framework=mapping.framework)

    def list_code_connect(
        self, *, file_key: str
    ) -> list[CodeConnectRef]:
        self._queue("GET", f"/v1/code_connect?file_key={file_key}")
        # Alpha: return empty
        return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _queue(
        self, method: str, path: str,
        *, body: dict[str, Any] | None = None,
    ) -> None:
        """Stage one HTTP request for later dispatch (or for inspection in alpha).

        With ``batch=None`` (default), write-side calls dispatch
        immediately on queue — the v1.1 behavior. With a
        :class:`BatchPolicy`, write-side calls (POST/PUT/PATCH/DELETE)
        are deferred and the call dict is tagged ``_deferred=True``;
        :meth:`commit_session` later dispatches all deferred calls
        in parallel through a thread pool. GET calls remain immediate
        regardless of the policy, because callers depend on their
        response data synchronously.
        """
        call = {
            "method": method,
            "path": path,
            "body": body,
            "queued_at": self._now(),
        }
        if not self.dry_run:
            if self._should_defer(call):
                call["_deferred"] = True
            else:
                self._dispatch_with_retry(call)
        self.pending_calls.append(call)

    def _should_defer(self, call: dict[str, Any]) -> bool:
        """Return True when ``call`` should be deferred for batch
        dispatch in :meth:`commit_session`. False (immediate) when no
        batch policy is set, the policy is disabled, or the call is a
        GET (caller needs the response synchronously)."""
        if self.batch is None or not self.batch.enabled:
            return False
        return call.get("method", "").upper() != "GET"

    def _dispatch_with_retry(self, call: dict[str, Any]) -> None:
        """Dispatch ``call``, retrying transient failures per the policy.

        When no :attr:`backoff` policy is configured, this is a plain
        single-shot dispatch (the v1.1 behavior). With a policy,
        :class:`RateLimitError` (429) and
        :class:`UpstreamUnavailableError` (5xx / network) are retried
        up to ``max_retries`` times, sleeping ``compute_delay`` before
        each retry. A 429's ``retry_after_seconds`` (parsed from the
        ``Retry-After`` header) is honored as the delay when present.
        Non-transient errors (4xx other than 429) are never retried.
        The ``call`` dict accumulates a ``retry_attempts`` count and a
        ``retry_delays`` list for introspection.
        """
        if self.backoff is None:
            self._dispatch_http(call)
            self._record_telemetry(success=True)
            return

        from .errors import RateLimitError, UpstreamUnavailableError

        attempt = 0
        delays: list[float] = []
        while True:
            try:
                self._dispatch_http(call)
                self._record_telemetry(success=True)
                call["retry_attempts"] = attempt
                call["retry_delays"] = delays
                return
            except RateLimitError as e:
                retry_after = getattr(e, "retry_after_seconds", None)
                self._record_telemetry(
                    success=False, status=429,
                    retry_after_seconds=retry_after,
                )
                if not self.backoff.should_retry(attempt):
                    call["retry_attempts"] = attempt
                    call["retry_delays"] = delays
                    raise
                delay = self.backoff.compute_delay(attempt, retry_after)
                delays.append(delay)
                self._sleep_fn(delay)
                attempt += 1
            except UpstreamUnavailableError:
                self._record_telemetry(success=False, status=500)
                if not self.backoff.should_retry(attempt):
                    call["retry_attempts"] = attempt
                    call["retry_delays"] = delays
                    raise
                delay = self.backoff.compute_delay(attempt, None)
                delays.append(delay)
                self._sleep_fn(delay)
                attempt += 1

    def _record_telemetry(
        self, *, success: bool, status: int = 200,
        retry_after_seconds: float | None = None,
    ) -> None:
        """Update per-batch telemetry counters under the lock.

        Called from :meth:`_dispatch_with_retry` after every HTTP
        attempt (success, 429, or 5xx). Each attempt counts as one
        request — retries inflate the total because each retry adds
        observable load on Figma. Thread-safe; works correctly under
        the :class:`BatchPolicy` thread pool.
        """
        with self._batch_telemetry_lock:
            self._batch_telemetry["requests_total"] += 1
            if not success:
                if status == 429:
                    self._batch_telemetry["requests_429"] += 1
                    if retry_after_seconds is not None:
                        self._batch_telemetry["retry_after_seconds_max"] = max(
                            self._batch_telemetry["retry_after_seconds_max"],
                            float(retry_after_seconds),
                        )
                elif 500 <= status < 600:
                    self._batch_telemetry["requests_5xx"] += 1

    def _dispatch_http(self, call: dict[str, Any]) -> None:
        """Issue the staged HTTP call via stdlib urllib.

        Translates the queued ``call`` dict into a real HTTPS request
        against ``self.base_url + call['path']``, sending the JSON
        body when present, and mapping channel-specific HTTP errors
        onto the normalized :mod:`figma_forge.transport.errors`
        hierarchy:

        - ``400`` → :class:`ValidationError`
        - ``401`` → :class:`AuthenticationError`
        - ``403`` → :class:`AuthorizationError`
        - ``404`` → :class:`NotFoundError`
        - ``409`` → :class:`ConflictError`
        - ``429`` → :class:`RateLimitError` (with ``retry_after_seconds`` parsed
          from the ``Retry-After`` header)
        - ``5xx`` → :class:`UpstreamUnavailableError`

        The response body is parsed as JSON when the
        ``Content-Type`` header advertises ``application/json``;
        non-JSON responses are kept verbatim. The mutated ``call``
        dict carries ``response_code``, ``response_body``, and
        ``response_headers`` for the caller's introspection.
        """
        import urllib.error
        import urllib.request

        req = urllib.request.Request(
            url=f"{self.base_url}{call['path']}",
            method=call["method"],
            headers={
                "X-Figma-Token": self._resolved_pat or "",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "figma-forge/1.1.0",
            },
            data=(
                json.dumps(call["body"]).encode("utf-8")
                if call["body"] is not None else None
            ),
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                call["response_code"] = resp.status
                call["response_headers"] = dict(resp.headers.items())
                call["response_body"] = body
                ctype = resp.headers.get("Content-Type", "")
                if "application/json" in ctype and body:
                    try:
                        call["response_json"] = json.loads(body)
                    except json.JSONDecodeError:
                        pass
        except urllib.error.HTTPError as e:
            # Map HTTP error code → normalized TransportError subclass
            self._translate_http_error(e, call)
        except urllib.error.URLError as e:
            # DNS failure, connection refused, timeout
            from .errors import UpstreamUnavailableError
            raise UpstreamUnavailableError(
                f"Network error contacting {self.base_url}: {e.reason}",
                operation=self._infer_operation_from_path(call["path"]),
                adapter_id=self.adapter_id(),
                cause=e,
            ) from e

    def _translate_http_error(
        self, err: "urllib.error.HTTPError", call: dict[str, Any]
    ) -> None:
        """Map an HTTPError onto the appropriate TransportError subclass."""
        from .errors import (
            AuthenticationError,
            AuthorizationError,
            ConflictError,
            NotFoundError,
            RateLimitError,
            UpstreamUnavailableError,
            ValidationError,
        )

        # Try to read the response body for a useful error message
        try:
            err_body = err.read().decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover
            err_body = ""
        call["response_code"] = err.code
        call["response_body"] = err_body

        op = self._infer_operation_from_path(call["path"])
        message = f"HTTP {err.code}: {err.reason}"
        if err_body:
            # Trim long bodies but keep enough detail for debugging
            preview = err_body[:200].replace("\n", " ")
            message += f" — {preview}"

        common_kwargs = {
            "operation": op,
            "adapter_id": self.adapter_id(),
            "cause": err,
        }

        code = err.code
        if code == 400:
            raise ValidationError(message, **common_kwargs)
        if code == 401:
            raise AuthenticationError(message, **common_kwargs)
        if code == 403:
            raise AuthorizationError(message, **common_kwargs)
        if code == 404:
            raise NotFoundError(message, **common_kwargs)
        if code == 409:
            raise ConflictError(message, **common_kwargs)
        if code == 429:
            retry_after = err.headers.get("Retry-After") if err.headers else None
            try:
                retry_after_seconds = float(retry_after) if retry_after else None
            except ValueError:
                retry_after_seconds = None
            raise RateLimitError(
                message,
                retry_after_seconds=retry_after_seconds,
                **common_kwargs,
            )
        if 500 <= code < 600:
            raise UpstreamUnavailableError(message, **common_kwargs)
        # Anything else — surface as generic TransportError
        from .errors import TransportError
        raise TransportError(message, **common_kwargs)

    def _infer_operation_from_path(self, path: str) -> str:
        """Best-effort: derive the operation name from the REST path.

        Used purely for diagnostic enrichment of error messages — the
        exception's ``operation`` field. Not authoritative.
        """
        if "/variables" in path:
            return "variables_endpoint"
        if "/code_connect" in path:
            return "code_connect_endpoint"
        if "/files/" in path and path.endswith(tuple(("/v1/files",))):
            return "create_file"
        if "/files/" in path:
            return "get_file"
        return "unknown"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


__all__ = ["RestTransport"]
