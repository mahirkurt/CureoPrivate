"""figma-forge batch dispatch policy — v1.3.0-beta.1.

Opt-in parallel dispatch for :class:`RestTransport`. When a
:class:`BatchPolicy` is attached, write-side HTTP calls (POST, PUT,
PATCH, DELETE) are **deferred** at queue time and dispatched in
parallel from :meth:`RestTransport.commit_session` using a thread
pool of ``max_concurrency`` workers. Read-side calls (GET) remain
immediate, because callers depend on their response data synchronously
(e.g. :meth:`RestTransport.get_file` returning a populated
``last_modified``).

The policy is purely about **concurrency** — no dependency-graph
analysis. Figma's REST API resources (variables, code_connect) are
self-versioned server-side, so concurrent writes to the same file are
safe; conflicting writes surface as 409 / 429, which the existing
:class:`BackoffPolicy` already retries. Each worker thread runs its
own backoff schedule, so a rate-limit storm is naturally
load-distributed by the policy's jitter.

Usage shape
-----------

.. code-block:: python

    rest = ff.RestTransport(
        pat="...", base_url="https://api.figma.com",
        backoff=ff.BackoffPolicy(max_retries=3, jitter=True),
        batch=ff.BatchPolicy(max_concurrency=4),
    )
    # write-side calls are queued; commit_session dispatches them in parallel
    router = ff.TransportRouter(...)
    result = ff.run_pipeline(bundle, transport=router, file_key="X")

Trade-offs
----------

- **Output ordering is non-deterministic** — workers complete in
  whatever order the network and Figma's response time permit. The
  per-call dict's ``response_json`` is still populated correctly;
  only the order of ``pending_calls`` after commit reflects
  completion order, not queue order.
- **First-error abort vs. continue**: this implementation runs all
  scheduled work to completion (no early abort on first failure),
  matching the v1.x precedent of "best-effort, never fail" for
  auxiliary mechanisms. Per-call exceptions are recorded on the call
  dict's ``error`` key; the caller's ``commit_session`` decides
  whether to surface them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BatchPolicy:
    """Parallel-dispatch policy for :class:`RestTransport`.

    Attributes
    ----------
    max_concurrency:
        Number of worker threads in the dispatch pool. Production
        defaults: 4 (matches Figma's published per-PAT concurrency
        guidance circa 2026). Setting ``1`` yields sequential
        dispatch through the pool — useful for reproducing batch
        behavior in tests without true concurrency.
    enabled:
        Master toggle. When ``False``, behavior matches
        ``batch=None`` (immediate dispatch on queue). Useful for
        flag-gating in production without removing the policy
        instance.
    adaptive:
        Optional :class:`AdaptiveConcurrency` policy. When set,
        :meth:`RestTransport.commit_session` records per-call
        rate-limit telemetry during batch dispatch and produces a
        :class:`ConcurrencyObservation` recommendation for the next
        build, attached to ``SessionResult.adaptive_observation``.
        The current build's concurrency is **not** mutated — the
        recommendation is for the operator to apply on a subsequent
        build by rebuilding the policy.
    """

    max_concurrency: int = 4
    enabled: bool = True
    adaptive: "AdaptiveConcurrency | None" = None

    def __post_init__(self) -> None:  # pragma: no cover - dataclass guard
        if self.max_concurrency < 1:
            raise ValueError(
                f"max_concurrency must be >= 1 (got {self.max_concurrency})"
            )


__all__ = ["BatchPolicy"]
