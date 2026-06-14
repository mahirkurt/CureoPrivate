"""figma-forge adaptive concurrency policy — v1.4.0-beta.1.

Observed-rate-limit-driven recommendations for ``BatchPolicy.max_concurrency``.
After each batch dispatch, the policy aggregates per-call telemetry
(429 count, 5xx count, ``Retry-After`` distribution) into a
:class:`ConcurrencyObservation`. The observation carries a
**recommendation** for the next build's ``max_concurrency`` — the
runner does not mutate the running policy mid-batch (that would
require a pool rebuild and break the v1.3 "concurrency is set by
construction, not runtime" invariant).

This is intentionally **tuning recommendation, not self-tuning**.
The operator inspects ``SessionResult.adaptive_observation`` after
the build, decides whether to apply the recommendation, and either
rebuilds the policy or ignores the hint. This keeps control with
the operator and avoids feedback-loop instability where a bad
recommendation could ratchet concurrency into a degenerate state.

Algorithm
---------

Given an observed 429 ratio ``r = requests_429 / requests_total``
and current ``max_concurrency = c``:

- ``r > target_429_ratio`` → scale down by 1 (capped at ``min_concurrency``).
  Rate limiting is active; back off.
- ``r == 0.0`` → scale up by 1 (capped at ``max_concurrency``). Zero
  pressure means we have headroom. With ``aggressive_scale_up=True``
  the step is 2 instead of 1.
- ``0 < r <= target_429_ratio`` → hold. Within budget; don't perturb.

Below a minimum sample size (``min_sample_size``, default 10), no
recommendation is made and ``recommended_max_concurrency`` equals
the current value — a 0/3 zero-429-ratio is not statistically
distinguishable from headroom and a 1/3 33% ratio is not
distinguishable from noise.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptiveConcurrency:
    """Policy controlling rate-limit-driven concurrency tuning.

    Attached to a :class:`BatchPolicy` via its ``adaptive`` field.
    After each batch dispatch, the REST transport produces a
    :class:`ConcurrencyObservation` using this policy's bounds and
    target.

    Attributes
    ----------
    min_concurrency:
        Lower bound for the recommended ``max_concurrency``.
        Recommendations never fall below this value, even under
        sustained rate limiting.
    max_concurrency:
        Upper bound for the recommended value. Recommendations
        never exceed this, even when zero 429s are observed.
    target_429_ratio:
        Acceptable 429-to-total ratio. Default 0.05 (5%). Above
        this, the policy recommends scaling down; at or below,
        scale up or hold.
    aggressive_scale_up:
        When ``True``, zero-429 observations scale up by 2 instead
        of 1. Default ``False`` — incremental scale-up is safer in
        unfamiliar environments.
    min_sample_size:
        Minimum number of total requests before any recommendation
        is made. Below this, ``recommended_max_concurrency`` equals
        the current value (no signal). Default 10.
    window:
        Number of consecutive batches to aggregate over for
        recommendation. Default ``1`` matches v1.4 behavior — each
        batch's recommendation is computed solely from that batch's
        telemetry. With ``window > 1``, the REST transport keeps the
        last ``window`` observations in a bounded deque and
        :meth:`recommend_aggregate` is called over the deque's
        contents; aggregate ``requests_total`` and ``requests_429``
        are summed across the window, then fed through
        :meth:`recommend`. The aggregate sample size dilutes single-
        batch noise (a 1/3 spike is much weaker against a 200-
        request total than against a 3-request one). v1.5.0-alpha.2.
    """

    min_concurrency: int = 1
    max_concurrency: int = 16
    target_429_ratio: float = 0.05
    aggressive_scale_up: bool = False
    min_sample_size: int = 10
    window: int = 1

    def __post_init__(self) -> None:  # pragma: no cover — dataclass guard
        if self.min_concurrency < 1:
            raise ValueError(
                f"min_concurrency must be >= 1 (got {self.min_concurrency})"
            )
        if self.max_concurrency < self.min_concurrency:
            raise ValueError(
                f"max_concurrency ({self.max_concurrency}) must be >= "
                f"min_concurrency ({self.min_concurrency})"
            )
        if not 0.0 <= self.target_429_ratio <= 1.0:
            raise ValueError(
                f"target_429_ratio must be in [0.0, 1.0] "
                f"(got {self.target_429_ratio})"
            )
        if self.min_sample_size < 1:
            raise ValueError(
                f"min_sample_size must be >= 1 (got {self.min_sample_size})"
            )
        if self.window < 1:
            raise ValueError(
                f"window must be >= 1 (got {self.window})"
            )

    def recommend(
        self, *, current: int, requests_total: int, requests_429: int,
    ) -> tuple[int, str]:
        """Return ``(recommended_max_concurrency, rationale)``.

        Pure arithmetic — no side effects. The rationale is a
        human-readable string suitable for logs and diagnostics.

        This is the **single-batch** recommendation. For
        multi-batch smoothing across a ``window`` of consecutive
        observations, call :meth:`recommend_aggregate` instead.
        """
        # Below sample threshold: no recommendation
        if requests_total < self.min_sample_size:
            return current, (
                f"sample size {requests_total} < min {self.min_sample_size} "
                f"→ hold at {current}"
            )

        ratio = requests_429 / requests_total if requests_total else 0.0

        # Above target: scale down (always step 1)
        if ratio > self.target_429_ratio:
            new = max(self.min_concurrency, current - 1)
            return new, (
                f"429 ratio {ratio:.1%} > {self.target_429_ratio:.1%} "
                f"target → scale down {current}→{new}"
            )

        # Zero pressure: scale up (step 1 or 2 if aggressive)
        if ratio == 0.0:
            step = 2 if self.aggressive_scale_up else 1
            new = min(self.max_concurrency, current + step)
            label = "aggressive" if self.aggressive_scale_up else "incremental"
            return new, (
                f"0% 429 → {label} scale up {current}→{new}"
            )

        # Within budget: hold
        return current, (
            f"429 ratio {ratio:.1%} ≤ {self.target_429_ratio:.1%} "
            f"target → hold at {current}"
        )

    def recommend_aggregate(
        self, *, current: int,
        observations: "Iterable[ConcurrencyObservation]",
    ) -> tuple[int, str]:
        """Recommend based on the aggregate counters of multiple batches.

        Sums ``requests_total`` and ``requests_429`` across the
        supplied observations and feeds the aggregate through
        :meth:`recommend`. The recommendation is therefore identical
        to what a single batch with the combined counters would
        produce — but driven from a larger sample, which dilutes
        single-batch noise.

        Empty observation iterable → hold at current with a
        no-observations rationale. ``window > 1`` callers see the
        batch count surface in the returned rationale.

        v1.5.0-alpha.2.
        """
        obs_list = list(observations)
        if not obs_list:
            return current, "no observations → hold at " + str(current)
        agg_total = sum(o.requests_total for o in obs_list)
        agg_429 = sum(o.requests_429 for o in obs_list)
        new, rationale = self.recommend(
            current=current, requests_total=agg_total, requests_429=agg_429,
        )
        # Prefix rationale with batch count for operator-visible context.
        # Note: rationale strings are explicitly non-parseable per the
        # v1.4 stability contract; this prefix is purely for human reading.
        n = len(obs_list)
        suffix = "batch" if n == 1 else "batches"
        return new, f"[aggregate over {n} {suffix}] {rationale}"

    def suggest_window(
        self,
        observations: "Iterable[ConcurrencyObservation]",
        *,
        max_suggested: int = 10,
    ) -> tuple[int, str]:
        """Suggest a ``window`` size from observed batch telemetry.

        A **recommendation, not an action** — like :meth:`recommend`
        and :meth:`recommend_aggregate`, this never mutates the
        policy. The operator reads the suggestion and decides whether
        to reconstruct the policy with a new ``window`` (the field is
        frozen). It answers: *"given how my batches actually behaved,
        how many should I smooth over?"*

        The heuristic combines two orthogonal signals and takes the
        larger:

        1. **Sample sufficiency.** If the average batch dispatched
           fewer than ``min_sample_size`` requests, a single batch is
           too small to recommend from reliably; enough batches must
           be aggregated to clear the threshold. This term is
           ``ceil(min_sample_size / avg_batch_total)``.
        2. **Volatility.** If the per-batch 429 ratio swings widely,
           more smoothing dampens the noise. This term scales with
           the coefficient of variation (``stdev / mean``) of the
           per-batch ratios: roughly ``1 + round(cv)``.

        The result is clamped to ``[1, max_suggested]``. An empty
        observation iterable yields ``1`` (nothing to smooth). The
        rationale names the dominant signal.

        Parameters
        ----------
        observations:
            The batch telemetry to analyze — typically the contents
            of an :class:`ObservationLog` or a transport's recent
            observation history.
        max_suggested:
            Upper bound on the suggested window. Default 10 — windows
            larger than this rarely help and risk clinging to stale
            signal.

        Returns
        -------
        tuple[int, str]:
            ``(suggested_window, rationale)``. The rationale is a
            human-readable, explicitly non-parseable string.
        """
        obs = list(observations)
        if not obs:
            return 1, "no observations → suggest window=1 (nothing to smooth)"

        n = len(obs)
        totals = [o.requests_total for o in obs]
        avg_total = sum(totals) / n

        # Signal 1: sample sufficiency.
        if avg_total >= self.min_sample_size:
            sample_window = 1
        else:
            sample_window = math.ceil(self.min_sample_size / max(avg_total, 1.0))

        # Signal 2: volatility (coefficient of variation of 429 ratios).
        ratios = [
            (o.requests_429 / o.requests_total if o.requests_total else 0.0)
            for o in obs
        ]
        mean_ratio = sum(ratios) / n
        if mean_ratio > 0.0 and n >= 2:
            variance = sum((r - mean_ratio) ** 2 for r in ratios) / n
            cv = (variance ** 0.5) / mean_ratio
            volatility_window = 1 + round(cv)
        else:
            volatility_window = 1

        suggested = max(sample_window, volatility_window)
        suggested = max(1, min(max_suggested, suggested))

        if sample_window >= volatility_window and sample_window > 1:
            reason = (
                f"avg batch {avg_total:.0f} req < min sample "
                f"{self.min_sample_size} → aggregate {suggested} batches"
            )
        elif volatility_window > 1:
            reason = (
                f"429-ratio volatility (cv={cv:.2f}) over {n} batches "
                f"→ smooth {suggested}"
            )
        else:
            reason = (
                f"batches are large and stable over {n} samples "
                f"→ window=1 suffices"
            )
        return suggested, f"[from {n} observations] {reason}"


@dataclass(frozen=True)
class ConcurrencyObservation:
    """Per-batch rate-limit telemetry + recommendation.

    Produced by :class:`RestTransport`'s batch dispatch and attached
    to :attr:`SessionResult.adaptive_observation` when both
    :class:`BatchPolicy` and its ``adaptive`` field are set.

    Attributes
    ----------
    requests_total:
        Total HTTP requests dispatched in this batch (including
        retries — each retry counts as a separate request because
        each adds load on Figma).
    requests_429:
        Subset that returned HTTP 429 (rate-limited).
    requests_5xx:
        Subset that returned 5xx (server error). Tracked
        separately because 5xx ratio above ~1% may indicate Figma
        side issues, not client over-concurrency.
    retry_after_seconds_max:
        Largest ``Retry-After`` header value observed across all
        429 responses in this batch. A high value means Figma
        wants meaningful backoff; the operator may want to drop
        concurrency more aggressively than the default step.
    current_max_concurrency:
        The ``max_concurrency`` setting that produced these
        observations.
    recommended_max_concurrency:
        What the adaptive policy suggests for the next build.
    rationale:
        Human-readable explanation of the recommendation. Suitable
        for log output and operator review.
    """

    requests_total: int
    requests_429: int
    requests_5xx: int
    retry_after_seconds_max: float
    current_max_concurrency: int
    recommended_max_concurrency: int
    rationale: str

    @property
    def ratio_429(self) -> float:
        """The observed 429-to-total ratio (0.0 when total is 0)."""
        return self.requests_429 / self.requests_total if self.requests_total else 0.0


__all__ = ["AdaptiveConcurrency", "ConcurrencyObservation"]
