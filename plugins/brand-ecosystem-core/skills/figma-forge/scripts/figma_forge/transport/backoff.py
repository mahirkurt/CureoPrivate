"""figma-forge ``BackoffPolicy`` — v1.2.0-alpha.

A small, deterministic-testable retry policy for transient transport
failures — primarily HTTP 429 (rate limit) and 5xx / network errors
(upstream unavailable). The policy computes a delay before each retry
attempt, honoring a server-supplied ``Retry-After`` hint when present
and otherwise falling back to exponential backoff with optional
jitter.

The policy is pure data + arithmetic — it does **not** sleep. The
caller (e.g. :class:`RestTransport`) is responsible for sleeping the
returned delay, which keeps the policy unit-testable without real
time passing and lets the caller inject a no-op sleep in tests.

Example
-------

.. code-block:: python

    policy = BackoffPolicy(max_retries=3, base_delay=0.5, jitter=False)
    # attempt 0 failed → wait policy.compute_delay(0) before attempt 1
    if policy.should_retry(attempt):
        time.sleep(policy.compute_delay(attempt, retry_after_seconds))
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BackoffPolicy:
    """Exponential backoff with optional jitter and Retry-After honor.

    Parameters
    ----------
    max_retries:
        Maximum number of *retries* after the initial attempt. A value
        of 3 means up to 4 total attempts (1 initial + 3 retries).
    base_delay:
        The base delay in seconds. The exponential schedule is
        ``base_delay * 2**attempt`` (attempt is 0-indexed).
    max_delay:
        Upper clamp for any computed delay, in seconds. Protects
        against unbounded waits on high attempt counts or a
        pathological ``Retry-After`` value.
    jitter:
        When ``True``, the computed delay is multiplied by a random
        factor in ``[1 - jitter_ratio, 1 + jitter_ratio]`` to avoid
        thundering-herd synchronization across parallel clients.
        Disable for deterministic tests.
    jitter_ratio:
        The magnitude of jitter (default 0.25 → ±25%).
    honor_retry_after:
        When ``True`` (default), a server-supplied ``Retry-After``
        value (passed to :meth:`compute_delay`) takes precedence over
        the exponential schedule, still clamped to ``max_delay``.
    seed:
        Optional RNG seed for reproducible jitter in tests. ``None``
        uses the module's shared RNG.
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    jitter: bool = True
    jitter_ratio: float = 0.25
    honor_retry_after: bool = True
    seed: int | None = None

    def should_retry(self, attempt: int) -> bool:
        """Return True if another attempt is permitted after ``attempt``.

        ``attempt`` is the 0-indexed number of the attempt that just
        failed. With ``max_retries=3``, attempts 0, 1, 2 may retry;
        attempt 3 (the 4th) may not.
        """
        return attempt < self.max_retries

    def compute_delay(
        self, attempt: int, retry_after_seconds: float | None = None
    ) -> float:
        """Compute the delay (seconds) to wait before the next attempt.

        If ``retry_after_seconds`` is provided and
        ``honor_retry_after`` is set, it is used as the base delay
        (clamped to ``max_delay``); jitter is **not** applied to a
        server-supplied hint, since the server has already told us the
        exact time to wait. Otherwise, an exponential delay
        ``base_delay * 2**attempt`` is computed, optionally jittered,
        and clamped to ``max_delay``.
        """
        if self.honor_retry_after and retry_after_seconds is not None:
            return min(max(0.0, retry_after_seconds), self.max_delay)

        raw = self.base_delay * (2 ** max(0, attempt))
        if self.jitter:
            rng = random.Random(self.seed) if self.seed is not None else random
            low = 1.0 - self.jitter_ratio
            high = 1.0 + self.jitter_ratio
            raw *= rng.uniform(low, high)
        return min(raw, self.max_delay)

    def schedule(self, retry_after_seconds: float | None = None) -> list[float]:
        """Return the full delay schedule for all permitted retries.

        Useful for diagnostics / logging: ``policy.schedule()`` returns
        ``[compute_delay(0), compute_delay(1), …]`` for each retry the
        policy would permit. With ``jitter=True`` the values are a
        single random realization.
        """
        return [
            self.compute_delay(attempt, retry_after_seconds)
            for attempt in range(self.max_retries)
        ]


__all__ = ["BackoffPolicy"]
