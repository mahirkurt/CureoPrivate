"""figma-forge reference MCP plan executor — v1.4.0-alpha.2.

A reference interpreter for MCP tool-call plans. Walks a validated
plan envelope and invokes injectable dispatch callables for each
step. The runner is the canonical execution semantics from
``references/walkthroughs/mcp-plan-execution.md`` expressed as code
— agents and operators should either use this directly or treat its
source as the reference implementation.

Why a reference runner
----------------------

v1.3.0-alpha.1 introduced the MCP plan envelope + a static validator
+ a walkthrough describing execution semantics (lifecycle, native vs
``use_figma_nl`` dispatch, idempotency, error recovery, verification).
But the walkthrough was *prose*. Each operator/agent re-implemented
the execution loop from scratch, which is a semantic drift hazard:
two agents reading the same walkthrough may write subtly different
loops, and the walkthrough may drift from any working implementation.

This module makes the walkthrough's agent runbook **executable**.
Default dispatch callables are no-ops returning a recognizable
sentinel ``{"_noop": True, ...}`` — so a fresh ``PlanRunner()``
runs a plan dry, verifying schema and walking step-by-step without
any side effects. Operators with a live MCP host inject their own
``native_dispatch`` / ``nl_dispatch`` callables; the rest of the
runner is identical between dry and live modes.

Design
------

- **Frozen ``StepResult`` per step**: outcome, response, error,
  duration. Frozen so callers can stash them safely.
- **``PlanRunResult`` aggregates**: attempt/success/failure counts,
  ``step_results`` list, optional ``aborted_on_step``, and the
  ``validation_report`` if validation ran.
- **``abort_on_failure`` flag**: when ``False`` (default), the
  runner attempts every step regardless of per-step failures —
  matching ``BatchPolicy``'s "best-effort, never fail" precedent.
  When ``True``, the first failure halts the run and remaining
  steps are *not* counted as attempts.
- **``on_step`` callback**: invoked after every step (success or
  failure) with the freshly-constructed ``StepResult``. Lets a
  caller stream progress, log to telemetry, or implement a custom
  abort policy via exception in the callback.

Usage
-----

.. code-block:: python

    import figma_forge as ff

    # Dry-run — default no-op dispatch, just validates and walks
    runner = ff.PlanRunner()
    result = runner.run(plan)
    print(f"{result.steps_succeeded}/{result.steps_attempted} steps OK")

    # Live MCP host — inject real dispatchers
    runner = ff.PlanRunner(
        native_dispatch=lambda tool, args: my_mcp.call(tool, args),
        nl_dispatch=lambda instruction, args: my_mcp.call(
            "Figma:use_figma", {"instruction": instruction}),
        on_step=lambda s: print(f"{s.step}: {s.status}"),
        abort_on_failure=False,
    )
    result = runner.run(plan, prior_state=prior)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from .plan_validation import (
    PlanValidationReport, PriorState, validate_mcp_plan,
)

#: Dispatch callable signatures, exposed for type-hint use by
#: callers. ``native_dispatch`` receives the Figma MCP tool name
#: (e.g. ``"Figma:create_new_file"``) and the descriptor's
#: ``arguments`` dict; ``nl_dispatch`` receives the instruction
#: string and the descriptor's ``arguments`` dict (the latter is
#: structured intent the agent may use for verification or for
#: phrasing its own prompt).
NativeDispatch = Callable[[str, dict], Any]
NlDispatch = Callable[[str, dict], Any]
StepCallback = Callable[["StepResult"], None]

StepStatus = Literal["success", "failure", "skipped"]
StepMechanism = Literal["native", "use_figma_nl"]


@dataclass(frozen=True)
class DispatchResponse:
    """A standardized return shape for ``PlanRunner`` dispatch callables.

    Dispatch callables (``native_dispatch`` / ``nl_dispatch``) may
    return **any** object — the runner captures it opaquely in
    :attr:`StepResult.response`. Returning a ``DispatchResponse``
    instead is **opt-in**: the runner recognizes it, surfaces it as
    a typed :attr:`StepResult.dispatch_response`, and lets the
    callable signal a *soft failure* (``ok=False``) without raising
    an exception.

    Two ways to signal failure
    --------------------------

    A dispatch callable can signal failure in two ways, both of
    which mark the step ``"failure"`` and trigger ``abort_on_failure``:

    1. **Raise an exception** — a hard failure. The runner captures
       ``repr(exc)`` in ``StepResult.error``.
    2. **Return ``DispatchResponse(ok=False)``** — a soft failure.
       Useful when the MCP host returned a 2xx but the operation was
       logically unsuccessful (e.g. Figma reported "entity already
       exists" or "name collision"). The callable can attach a
       human-readable reason via ``warnings`` and still hand back
       structured data.

    Returning a non-``DispatchResponse`` value (the v1.5 behavior)
    is always treated as success — the runner does not inspect
    opaque returns for failure signals.

    Attributes
    ----------
    ok:
        ``True`` (default) → the step is ``"success"``. ``False`` →
        the step is ``"failure"`` even though no exception was
        raised.
    entity_id:
        The Figma node / entity ID the operation created or
        affected, if the host returned one. Lets the operator stash
        IDs for later reference without parsing ``raw``.
    raw:
        The underlying MCP host response, unmodified. ``StepResult.response``
        holds the ``DispatchResponse`` itself; ``raw`` holds what the
        host actually returned beneath it.
    retry_attempts:
        How many times the callable retried internally before
        succeeding (or giving up). ``0`` means first-try success.
        Surfaces retry telemetry the runner cannot otherwise see
        (the runner does not retry — that is the callable's job).
    warnings:
        Non-fatal messages from the dispatch (e.g. a deprecation
        notice from the host, or the reason for ``ok=False``).
        Immutable tuple.
    """

    ok: bool = True
    entity_id: str | None = None
    raw: Any = None
    retry_attempts: int = 0
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class StepResult:
    """Outcome of a single plan step.

    Frozen so step results can be safely captured into logs,
    telemetry, or further analysis without risk of mutation.

    Attributes
    ----------
    step:
        The 1-indexed step number from the plan envelope.
    operation:
        The figma-forge transport operation name
        (``"create_variable"``, ``"place_instance"``, …).
    mcp_tool:
        The Figma MCP tool that was (or would have been) called.
    mechanism:
        ``"native"`` or ``"use_figma_nl"``.
    status:
        ``"success"`` when the dispatch returned without raising;
        ``"failure"`` when an exception was caught; ``"skipped"``
        when ``abort_on_failure`` halted the run before this step.
    response:
        Whatever the dispatch callable returned (opaque to the
        runner). ``None`` for skipped steps.
    error:
        ``repr(exception)`` when ``status == "failure"``; empty
        string otherwise.
    duration_ms:
        Wall-clock time spent in dispatch, in milliseconds. ``0.0``
        for skipped steps.
    dispatch_response:
        The :class:`DispatchResponse` the callable returned, if it
        returned one; otherwise ``None``. When present, ``status``
        reflects its ``ok`` flag. v1.6.0-alpha.1.
    """

    step: int
    operation: str
    mcp_tool: str
    mechanism: StepMechanism
    status: StepStatus
    response: Any = None
    error: str = ""
    duration_ms: float = 0.0
    dispatch_response: "DispatchResponse | None" = None


@dataclass
class PlanRunResult:
    """Aggregate outcome of a plan run.

    Not frozen because ``step_results`` grows during execution.
    After ``run()`` returns the result is effectively complete; the
    caller may treat it as immutable.

    Attributes
    ----------
    steps_attempted:
        Count of steps the runner actually tried to dispatch.
        Excludes skipped steps under ``abort_on_failure=True``.
    steps_succeeded:
        Subset of ``steps_attempted`` that succeeded.
    steps_failed:
        Subset of ``steps_attempted`` that failed.
    steps_skipped:
        Count of steps not attempted because an earlier failure
        triggered abort (``abort_on_failure=True``). ``0`` when
        ``abort_on_failure=False`` or no failure occurred.
    step_results:
        The :class:`StepResult` for every step in plan order
        (including skipped ones).
    aborted_on_step:
        The 1-indexed step number on which the run aborted, or
        ``None`` if no abort occurred.
    validation_report:
        The :class:`PlanValidationReport` produced before dispatch
        when ``validate=True``, otherwise ``None``. When validation
        fails (``is_executable=False``), no dispatch is attempted
        and this field tells the caller why.
    """

    steps_attempted: int = 0
    steps_succeeded: int = 0
    steps_failed: int = 0
    steps_skipped: int = 0
    step_results: list[StepResult] = field(default_factory=list)
    aborted_on_step: int | None = None
    validation_report: PlanValidationReport | None = None

    @property
    def is_success(self) -> bool:
        """True when no failures, no abort, and (if validation ran)
        the plan was executable.

        A run that aborted at the validation gate
        (``validation_report.is_executable is False``) is **not**
        success, even though it recorded zero failed dispatches —
        because no dispatches were attempted. The property captures
        operator intent: "did this plan execute cleanly end-to-end?"
        """
        if (self.validation_report is not None
                and not self.validation_report.is_executable):
            return False
        return self.steps_failed == 0 and self.aborted_on_step is None


def _default_native_dispatch(mcp_tool: str, arguments: dict) -> dict:
    """Default no-op native dispatch — returns a sentinel."""
    return {"_noop": True, "mcp_tool": mcp_tool}


def _default_nl_dispatch(instruction: str, arguments: dict) -> dict:
    """Default no-op use_figma_nl dispatch — returns a sentinel."""
    return {"_noop": True, "instruction_len": len(instruction)}


class PlanRunner:
    """Reference interpreter for MCP tool-call plans.

    Construct with the dispatch hooks appropriate to your
    environment (or rely on the no-op defaults for dry-run), then
    call :meth:`run` with a plan envelope.

    Parameters
    ----------
    native_dispatch:
        Callable invoked for each ``mechanism="native"`` step.
        Receives ``(mcp_tool: str, arguments: dict)``; returns
        whatever your MCP host returned. ``None`` (default) uses an
        internal no-op that returns a sentinel — useful for
        dry-run.
    nl_dispatch:
        Callable invoked for each ``mechanism="use_figma_nl"``
        step. Receives ``(instruction: str, arguments: dict)``;
        returns the MCP host response. ``None`` (default) uses an
        internal no-op.
    on_step:
        Callback invoked after every step (success, failure, or
        skipped) with the freshly-constructed ``StepResult``. Use
        for streaming progress, telemetry, or a custom abort
        policy (raise from the callback to halt).
    abort_on_failure:
        When ``False`` (default), the runner attempts every step
        regardless of per-step failures. When ``True``, the first
        failure halts the run; remaining steps are marked
        ``"skipped"`` in ``step_results`` and ``aborted_on_step``
        is set.

    Notes
    -----
    The runner does **not** retry. Per-step retries are the
    responsibility of the dispatch callables — if the operator's
    MCP host implements its own retry semantics, the runner
    inherits them transparently. This mirrors the v1.2/v1.3
    decision to keep ``BackoffPolicy`` inside ``RestTransport``
    rather than at the dispatch boundary.
    """

    def __init__(
        self,
        *,
        native_dispatch: NativeDispatch | None = None,
        nl_dispatch: NlDispatch | None = None,
        on_step: StepCallback | None = None,
        abort_on_failure: bool = False,
    ) -> None:
        self.native_dispatch = native_dispatch or _default_native_dispatch
        self.nl_dispatch = nl_dispatch or _default_nl_dispatch
        self.on_step = on_step
        self.abort_on_failure = abort_on_failure

    def run(
        self,
        plan: str | dict[str, Any],
        *,
        validate: bool = True,
        prior_state: PriorState | None = None,
        freshness_window_seconds: float | None = None,
        freshness_window_overrides: dict[str, float] | None = None,
        concurrent: bool = False,
        max_workers: int = 4,
    ) -> PlanRunResult:
        """Execute the plan, returning a :class:`PlanRunResult`.

        Parameters
        ----------
        plan:
            The MCP plan envelope as JSON string or pre-parsed dict.
        validate:
            When ``True`` (default), the plan is statically validated
            before any dispatch. If validation fails
            (``is_executable=False``), the runner returns immediately
            with no attempted steps and the validation report
            attached. When ``False``, validation is skipped and the
            runner walks the plan as given — useful for replaying
            plans that have already been validated.
        prior_state:
            Forwarded to :func:`validate_mcp_plan` when ``validate=True``.
            Ignored otherwise.
        freshness_window_seconds:
            Forwarded to :func:`validate_mcp_plan` when ``validate=True``.
            Ignored otherwise. v1.5.0-alpha.1.
        freshness_window_overrides:
            Per-entity-class freshness TTLs (``{"collection": 3600,
            "component": 300}``) forwarded to :func:`validate_mcp_plan`
            when ``validate=True``. Ignored otherwise. v1.6.0-beta.1.
        concurrent:
            When ``False`` (default), steps run sequentially in plan
            order — exactly the v1.4–v1.6.0-alpha.1 behavior. When
            ``True``, the plan is partitioned into dependency layers
            via :func:`plan_execution_layers` and each layer's steps
            are dispatched in parallel across a thread pool; layers
            run in order. ``step_results`` is always assembled in
            plan order regardless of completion order. v1.6.0-alpha.2.
        max_workers:
            Thread-pool size for ``concurrent=True``. Ignored when
            ``concurrent=False``. v1.6.0-alpha.2.
        """
        import json
        if isinstance(plan, str):
            plan_obj = json.loads(plan)
        else:
            plan_obj = plan

        result = PlanRunResult()

        # Validation gate
        if validate:
            report = validate_mcp_plan(
                plan_obj, prior_state=prior_state,
                freshness_window_seconds=freshness_window_seconds,
                freshness_window_overrides=freshness_window_overrides,
            )
            result.validation_report = report
            if not report.is_executable:
                return result  # No dispatch attempted

        steps = plan_obj.get("steps", []) if isinstance(plan_obj, dict) else []

        if concurrent:
            self._run_concurrent(plan_obj, steps, result, max_workers)
            return result

        aborted = False

        for step in steps:
            step_num = step.get("step", 0) if isinstance(step, dict) else 0
            operation = step.get("operation", "") if isinstance(step, dict) else ""
            mcp_tool = step.get("mcp_tool", "") if isinstance(step, dict) else ""
            mechanism = step.get("mechanism", "native") if isinstance(step, dict) else "native"
            args = step.get("arguments", {}) if isinstance(step, dict) else {}
            instruction = step.get("instruction", "") if isinstance(step, dict) else ""

            # Skip remaining steps if we aborted
            if aborted:
                sr = StepResult(
                    step=step_num, operation=operation, mcp_tool=mcp_tool,
                    mechanism=mechanism, status="skipped",
                )
                result.step_results.append(sr)
                result.steps_skipped += 1
                if self.on_step is not None:
                    self.on_step(sr)
                continue

            # Dispatch via the shared per-step executor.
            sr = self._execute_step(step)
            if sr.status == "success":
                result.steps_succeeded += 1
            else:  # failure
                result.steps_failed += 1
                if self.abort_on_failure:
                    result.aborted_on_step = sr.step
                    aborted = True

            result.steps_attempted += 1
            result.step_results.append(sr)
            if self.on_step is not None:
                self.on_step(sr)

        return result

    def _execute_step(self, step: dict[str, Any]) -> StepResult:
        """Dispatch a single step and return its :class:`StepResult`.

        Shared by the sequential and concurrent execution paths so
        both produce identical StepResult semantics (success /
        soft-failure / hard-failure detection, ``DispatchResponse``
        recognition, duration timing). Does **not** mutate the
        aggregate result or apply abort policy — that is the
        caller's responsibility.
        """
        step_num = step.get("step", 0) if isinstance(step, dict) else 0
        operation = step.get("operation", "") if isinstance(step, dict) else ""
        mcp_tool = step.get("mcp_tool", "") if isinstance(step, dict) else ""
        mechanism = step.get("mechanism", "native") if isinstance(step, dict) else "native"
        args = step.get("arguments", {}) if isinstance(step, dict) else {}
        instruction = step.get("instruction", "") if isinstance(step, dict) else ""

        t0 = time.perf_counter()
        try:
            if mechanism == "native":
                response = self.native_dispatch(mcp_tool, args)
            else:
                response = self.nl_dispatch(instruction, args)
            duration_ms = (time.perf_counter() - t0) * 1000.0
            # Recognize an opt-in DispatchResponse. A non-DispatchResponse
            # return is always success (v1.5 behavior); a
            # DispatchResponse(ok=False) is a soft failure.
            if isinstance(response, DispatchResponse):
                dispatch_resp = response
                succeeded = response.ok
            else:
                dispatch_resp = None
                succeeded = True
            if succeeded:
                return StepResult(
                    step=step_num, operation=operation, mcp_tool=mcp_tool,
                    mechanism=mechanism, status="success",
                    response=response, duration_ms=duration_ms,
                    dispatch_response=dispatch_resp,
                )
            soft_error = (
                "; ".join(dispatch_resp.warnings)
                if dispatch_resp.warnings
                else "DispatchResponse(ok=False)"
            )
            return StepResult(
                step=step_num, operation=operation, mcp_tool=mcp_tool,
                mechanism=mechanism, status="failure",
                response=response, error=soft_error,
                duration_ms=duration_ms, dispatch_response=dispatch_resp,
            )
        except Exception as e:  # noqa: BLE001 — opaque per-step capture
            duration_ms = (time.perf_counter() - t0) * 1000.0
            return StepResult(
                step=step_num, operation=operation, mcp_tool=mcp_tool,
                mechanism=mechanism, status="failure",
                error=repr(e), duration_ms=duration_ms,
            )

    def _run_concurrent(
        self, plan_obj: dict[str, Any], steps: list,
        result: PlanRunResult, max_workers: int,
    ) -> None:
        """Layered parallel execution. Mutates ``result`` in place.

        Partitions the plan into dependency layers, dispatches each
        layer's steps across a thread pool, and assembles results in
        plan order. ``abort_on_failure`` halts at layer granularity:
        the failing layer always completes (its steps were already
        in flight), then remaining layers are marked ``"skipped"``.
        ``aborted_on_step`` is the lowest-numbered failing step in
        the layer that triggered the abort.
        """
        from concurrent.futures import ThreadPoolExecutor
        from .plan_graph import plan_execution_layers

        step_by_num: dict[int, dict] = {}
        for idx, s in enumerate(steps, start=1):
            if isinstance(s, dict):
                num = s.get("step") if isinstance(s.get("step"), int) else idx
                step_by_num[num] = s

        layers = plan_execution_layers(plan_obj)
        results_by_num: dict[int, StepResult] = {}
        aborted = False

        for layer in layers:
            if aborted:
                for snum in layer:
                    step = step_by_num.get(snum, {})
                    results_by_num[snum] = StepResult(
                        step=snum,
                        operation=step.get("operation", ""),
                        mcp_tool=step.get("mcp_tool", ""),
                        mechanism=step.get("mechanism", "native"),
                        status="skipped",
                    )
                continue

            # Dispatch this layer. A singleton layer runs inline (no
            # pool overhead); a wider layer fans out across the pool.
            if len(layer) == 1:
                snum = layer[0]
                results_by_num[snum] = self._execute_step(step_by_num[snum])
            else:
                with ThreadPoolExecutor(max_workers=max_workers) as ex:
                    future_to_num = {
                        ex.submit(self._execute_step, step_by_num[snum]): snum
                        for snum in layer
                    }
                    for fut in future_to_num:
                        snum = future_to_num[fut]
                        results_by_num[snum] = fut.result()

            # After the layer completes, check for failures.
            layer_failures = [
                snum for snum in layer
                if results_by_num[snum].status == "failure"
            ]
            if layer_failures and self.abort_on_failure:
                aborted = True
                result.aborted_on_step = min(layer_failures)

        # Assemble step_results in plan order (ascending step number).
        for snum in sorted(results_by_num):
            sr = results_by_num[snum]
            result.step_results.append(sr)
            if sr.status == "success":
                result.steps_succeeded += 1
                result.steps_attempted += 1
            elif sr.status == "failure":
                result.steps_failed += 1
                result.steps_attempted += 1
            else:  # skipped
                result.steps_skipped += 1
            if self.on_step is not None:
                self.on_step(sr)


__all__ = [
    "NativeDispatch", "NlDispatch", "StepCallback",
    "StepStatus", "StepMechanism",
    "DispatchResponse",
    "StepResult", "PlanRunResult", "PlanRunner",
]
