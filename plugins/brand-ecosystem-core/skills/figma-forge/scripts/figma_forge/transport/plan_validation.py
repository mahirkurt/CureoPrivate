"""figma-forge MCP plan static validator — v1.3.0-alpha.1.

A pure-Python static validator for the JSON envelope produced by
:meth:`McpCursorTransport.render_mcp_plan`. Validates the plan before
an agent executes it against a live Figma file, catching schema
violations, native-argument shape mismatches, and dependency-ordering
anomalies that would otherwise surface only at execution time.

The validator is **strict on schema, soft on ordering**. Schema and
argument violations make the plan non-executable
(``is_executable=False``); ordering anomalies are reported as
warnings — the plan remains executable, since the heuristic that
detects them can produce false positives on edge cases (e.g.
cross-session plans where dependencies were satisfied in an earlier
plan).

Usage
-----

.. code-block:: python

    import json
    plan_json = mcp.render_mcp_plan()
    report = validate_mcp_plan(plan_json)
    if not report.is_executable:
        for e in report.schema_errors:
            print(f"SCHEMA: {e}")
        for e in report.argument_errors:
            print(f"ARGUMENT: step {e['step']} — {e['detail']}")
    for w in report.ordering_warnings:
        print(f"WARNING: {w}")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .mcp_dispatch import native_required_args as _native_required_args


@dataclass(frozen=True)
class PriorState:
    """Known-existing entities from prior plans or pre-existing Figma
    UI state, used to suppress ordering warnings that would otherwise
    be false positives in cross-session validation.

    A typical use: a build that only adds new variables to an existing
    collection legitimately omits the ``create_variable_collection``
    step (the collection was created in an earlier plan or by hand
    in the Figma UI). Without ``PriorState``, the validator emits an
    orphan-collection ordering warning; with the collection's name or
    id listed here, the warning is suppressed.

    The four frozenset fields correspond to the four entity types the
    validator's heuristic ordering checks track. All fields default
    to empty — passing a default ``PriorState()`` is equivalent to
    passing ``None`` (no suppression).

    The dataclass is frozen so an instance can be cheaply shared
    across multiple validations within a single build pipeline.

    Attributes
    ----------
    known_collection_ids:
        Collection IDs that already exist (referenced by
        ``create_variable.collection_id`` in this plan but never
        created here).
    known_collection_names:
        Collection names that already exist. Not currently used by
        the validator's checks (kept for forward compatibility — the
        ordering heuristic tracks ids); accepted in the API today.
    known_component_names:
        Component / component-set names that already exist
        (referenced by ``place_instance.parent_name`` in this plan).
    known_page_names:
        Page names that already exist (referenced by
        ``create_component.page_name`` in this plan).
    last_verified_at:
        Optional timezone-aware :class:`datetime.datetime` recording
        when the hint set was last reconciled with the live Figma
        state. Used by :func:`validate_mcp_plan` when called with a
        ``freshness_window_seconds`` argument: hints older than that
        window contribute a ``freshness_warnings`` entry to the
        report. ``None`` (default) preserves v1.4 behavior — no
        freshness checking. **Must be timezone-aware**; passing a
        naive datetime raises :class:`ValueError` at construction.
        v1.5.0-alpha.1.
    """

    known_collection_ids: frozenset[str] = frozenset()
    known_collection_names: frozenset[str] = frozenset()
    known_component_names: frozenset[str] = frozenset()
    known_page_names: frozenset[str] = frozenset()
    last_verified_at: "datetime | None" = None

    def __post_init__(self) -> None:
        # tz-aware enforcement — explicit policy: a hint with no
        # timezone is ambiguous about which clock it refers to and
        # silently treating it as UTC can mask staleness across a
        # team operating in multiple zones. Reject at construction
        # so the error surfaces at the call site of PriorState(),
        # not deep inside validate_mcp_plan().
        if self.last_verified_at is not None:
            if self.last_verified_at.tzinfo is None:
                raise ValueError(
                    "last_verified_at must be timezone-aware "
                    "(got a naive datetime). Use "
                    "`datetime.now(timezone.utc)` or attach a tzinfo "
                    "with `.replace(tzinfo=timezone.utc)`."
                )


#: Required envelope fields (top-level keys of the plan JSON).
_REQUIRED_ENVELOPE_FIELDS = (
    "plan_format_version", "adapter", "step_count", "steps",
)

#: Required per-step fields, regardless of mechanism.
_REQUIRED_STEP_FIELDS = ("step", "operation", "mcp_tool", "mechanism",
                         "arguments")

#: Native MCP tool → required argument keys. **Derived from**
#: :data:`figma_forge.transport.mcp_dispatch.REGISTRY` — the single
#: source of truth. When a new native MCP tool is registered, its
#: required-arg shape is picked up here automatically at import time.
#: Extra keys in a descriptor's ``arguments`` are allowed
#: (forward-compatible).
_NATIVE_TOOL_REQUIRED_ARGS: dict[str, tuple[str, ...]] = _native_required_args()

#: Operations whose `arguments.collection_id` must reference an earlier
#: `create_variable_collection`. Heuristic dependency check.
_NEEDS_COLLECTION = ("create_variable", "update_variable",
                     "create_alias_reference")

#: Operations whose `arguments.parent_name` should reference an earlier
#: `create_component` / `create_component_set` (component frame).
_NEEDS_PARENT_COMPONENT = ("place_instance",)

#: Operations whose `arguments.page_name` should reference an earlier
#: `create_page` on the same file. Soft dependency.
_NEEDS_PAGE = ("create_component", "create_component_set",
               "import_svg_as_component")


@dataclass(frozen=True)
class PlanValidationReport:
    """The outcome of a static plan validation.

    Attributes
    ----------
    plan_format_version:
        Plan format version reported in the envelope.
    step_count:
        Number of steps in the plan, as reported by the envelope.
    schema_errors:
        Critical envelope or per-step shape violations. Any entry
        here makes the plan non-executable.
    argument_errors:
        Native-step argument shape mismatches (each carries the
        step number and a human-readable detail). Critical.
    ordering_warnings:
        Heuristic dependency-ordering anomalies — a step references
        an entity (collection, parent component, page) for which no
        prior creation step was found in this plan. Soft — does not
        block execution, since cross-session plans may legitimately
        omit prior creations.
    freshness_warnings:
        Stale-hint warnings produced when
        :func:`validate_mcp_plan` is called with a
        ``freshness_window_seconds`` argument and the supplied
        :class:`PriorState` has a ``last_verified_at`` older than
        that window. Soft — does not block execution, since the
        operator may legitimately choose to validate with a stale
        hint set (e.g. when the live Figma query is unavailable).
        v1.5.0-alpha.1.
    is_executable:
        ``True`` when no schema or argument errors are present.
        Ordering and freshness warnings do not affect executability.
    """

    plan_format_version: str
    step_count: int
    schema_errors: list[str]
    argument_errors: list[dict[str, Any]]
    ordering_warnings: list[str]
    is_executable: bool
    freshness_warnings: list[str] = field(default_factory=list)


def validate_mcp_plan(
    plan: str | dict[str, Any],
    *,
    prior_state: PriorState | None = None,
    freshness_window_seconds: float | None = None,
    freshness_window_overrides: dict[str, float] | None = None,
) -> PlanValidationReport:
    """Statically validate an MCP tool-call plan JSON envelope.

    Accepts either the JSON string returned by
    :meth:`McpCursorTransport.render_mcp_plan` or a pre-parsed dict.
    Returns a :class:`PlanValidationReport` describing any schema
    violations, argument-shape mismatches, and dependency-ordering
    anomalies. Never raises for plan-content problems — those are
    captured in the report. Raises ``json.JSONDecodeError`` only if
    the input string is not valid JSON.

    Parameters
    ----------
    plan:
        The MCP plan envelope as JSON string or pre-parsed dict.
    prior_state:
        Optional :class:`PriorState` seeding the cross-step ordering
        check with entities known to exist before this plan runs
        (from earlier plans or pre-existing Figma UI state).
        Default ``None`` (no seeding — the v1.3.0 behavior). When
        given, the ordering heuristic treats listed collection ids,
        component names, and page names as already-satisfied
        dependencies, suppressing what would otherwise be
        false-positive ordering warnings on cross-session plans.
    freshness_window_seconds:
        Optional scalar staleness window in seconds (v1.5.0-alpha.1).
        When given together with ``prior_state.last_verified_at``, a
        single class-agnostic warning is emitted if the hint age
        exceeds it. Advisory only — never affects ``is_executable``.
    freshness_window_overrides:
        Optional per-entity-class staleness windows (v1.6.0-beta.1).
        Keys are ``"collection"``, ``"component"``, ``"page"``;
        ``freshness_window_seconds`` is the fallback for unlisted
        classes. A class is evaluated only if ``prior_state`` carries
        a hint for it. **ID-vs-name split (v1.7.0-alpha.1):** the
        ``"collection"`` class may be refined into ``"collection_id"``
        (stable IDs) and ``"collection_name"`` (mutable names)
        sub-classes with distinct TTLs. The split is opt-in — it
        activates only when ``"collection_id"`` or
        ``"collection_name"`` is present; otherwise ``"collection"``
        behaves exactly as in v1.6 (one combined class). Resolution
        is most-specific-wins: sub-key → ``"collection"`` → scalar →
        skip. Scalar mode (``overrides=None``) is byte-for-byte the
        v1.5.0-alpha.1 behavior. Advisory only.
    """
    if isinstance(plan, str):
        plan_obj = json.loads(plan)
    else:
        plan_obj = plan

    schema_errors: list[str] = []
    argument_errors: list[dict[str, Any]] = []
    ordering_warnings: list[str] = []
    freshness_warnings: list[str] = []

    # ---- Freshness check (v1.5.0-alpha.1; per-class v1.6.0-beta.1) -----
    # Triggers when a hint timestamp is present together with either a
    # scalar window or a per-class override map. Stale hints never
    # affect is_executable — they're advisory.
    if (prior_state is not None
            and prior_state.last_verified_at is not None
            and (freshness_window_seconds is not None
                 or freshness_window_overrides is not None)):
        now = datetime.now(timezone.utc)
        age_seconds = (now - prior_state.last_verified_at).total_seconds()
        if age_seconds < 0:
            # Negative age (timestamp in the future) is suspicious and
            # class-independent (one timestamp) — surface it once, do
            # not block, and skip per-class staleness (age is invalid).
            freshness_warnings.append(
                f"PriorState last_verified_at is "
                f"{abs(age_seconds):.0f}s in the future "
                f"(clock skew or operator error?)."
            )
        elif freshness_window_overrides is not None:
            # Per-class mode: evaluate each entity class that has a
            # hint against its own TTL (override → scalar fallback →
            # skipped if neither is defined for that class).
            #
            # ID-vs-name split (v1.7.0-alpha.1): the "collection"
            # class can be refined into "collection_id" (stable) and
            # "collection_name" (mutable) sub-classes with distinct
            # TTLs. The split is *opt-in* — it activates only when a
            # sub-key is present in the overrides. Without a sub-key,
            # "collection" behaves exactly as in v1.6.0-beta.1 (one
            # combined class → at most one collection warning), so an
            # operator using only the legacy "collection" key sees
            # identical v1.6 behavior. Resolution is most-specific-wins
            # (RFC v1.7 §5.5): sub-key → "collection" → scalar → skip.
            overrides = freshness_window_overrides
            _split = ("collection_id" in overrides
                      or "collection_name" in overrides)
            if _split:
                _collection_alias = overrides.get(
                    "collection", freshness_window_seconds
                )
                _checks = [
                    ("collection_id",
                     bool(prior_state.known_collection_ids),
                     overrides.get("collection_id", _collection_alias)),
                    ("collection_name",
                     bool(prior_state.known_collection_names),
                     overrides.get("collection_name", _collection_alias)),
                ]
            else:
                _checks = [
                    ("collection",
                     bool(prior_state.known_collection_ids
                          or prior_state.known_collection_names),
                     overrides.get("collection", freshness_window_seconds)),
                ]
            _checks += [
                ("component", bool(prior_state.known_component_names),
                 overrides.get("component", freshness_window_seconds)),
                ("page", bool(prior_state.known_page_names),
                 overrides.get("page", freshness_window_seconds)),
            ]
            for cls, has_hint, ttl in _checks:
                if not has_hint or ttl is None:
                    continue
                if age_seconds > ttl:
                    freshness_warnings.append(
                        f"PriorState {cls} hints are {age_seconds:.0f}s "
                        f"old, exceed their {ttl:.0f}s freshness window "
                        f"— {cls} hints may be stale (last_verified_at="
                        f"{prior_state.last_verified_at.isoformat()})."
                    )
        elif freshness_window_seconds is not None:
            # Scalar mode (v1.5.0-alpha.1 behavior, unchanged): one
            # class-agnostic window for all hints.
            if age_seconds > freshness_window_seconds:
                freshness_warnings.append(
                    f"PriorState hint is {age_seconds:.0f}s old, exceeds "
                    f"freshness window of {freshness_window_seconds:.0f}s — "
                    f"hints may be stale (last_verified_at="
                    f"{prior_state.last_verified_at.isoformat()})."
                )

    # ---- Envelope schema -----------------------------------------------
    if not isinstance(plan_obj, dict):
        schema_errors.append(
            f"Envelope is not a JSON object (got {type(plan_obj).__name__})."
        )
        return PlanValidationReport(
            plan_format_version="", step_count=0,
            schema_errors=schema_errors,
            argument_errors=[], ordering_warnings=[],
            is_executable=False,
            freshness_warnings=freshness_warnings,
        )

    for field_name in _REQUIRED_ENVELOPE_FIELDS:
        if field_name not in plan_obj:
            schema_errors.append(f"Envelope missing required field: {field_name!r}.")

    plan_format_version = str(plan_obj.get("plan_format_version", ""))
    declared_step_count = plan_obj.get("step_count", 0)
    if not isinstance(declared_step_count, int):
        schema_errors.append(
            f"step_count must be an integer (got {type(declared_step_count).__name__})."
        )
        declared_step_count = 0

    steps = plan_obj.get("steps", [])
    if not isinstance(steps, list):
        schema_errors.append(
            f"steps must be a list (got {type(steps).__name__})."
        )
        steps = []

    if declared_step_count != len(steps):
        schema_errors.append(
            f"step_count={declared_step_count} disagrees with "
            f"len(steps)={len(steps)}."
        )

    # ---- Per-step schema + arguments + monotonic step numbering --------
    prior_step_num = 0
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            schema_errors.append(
                f"Step #{idx} is not a JSON object."
            )
            continue
        for field_name in _REQUIRED_STEP_FIELDS:
            if field_name not in step:
                schema_errors.append(
                    f"Step #{idx} missing required field: {field_name!r}."
                )

        step_num = step.get("step")
        if isinstance(step_num, int):
            if step_num != prior_step_num + 1:
                schema_errors.append(
                    f"Step #{idx}: step number {step_num} is not "
                    f"monotonically incrementing (expected {prior_step_num + 1})."
                )
            prior_step_num = step_num

        mechanism = step.get("mechanism")
        if mechanism not in ("native", "use_figma_nl"):
            schema_errors.append(
                f"Step #{idx}: invalid mechanism {mechanism!r} "
                f"(must be 'native' or 'use_figma_nl')."
            )

        instruction_present = "instruction" in step
        if mechanism == "native" and instruction_present:
            schema_errors.append(
                f"Step #{idx}: native descriptors must not carry an "
                f"'instruction' field."
            )
        if mechanism == "use_figma_nl" and not step.get("instruction"):
            schema_errors.append(
                f"Step #{idx}: use_figma_nl descriptors require a "
                f"non-empty 'instruction'."
            )

        # Native argument shape
        if mechanism == "native":
            mcp_tool = step.get("mcp_tool", "")
            required = _NATIVE_TOOL_REQUIRED_ARGS.get(mcp_tool, ())
            args = step.get("arguments") if isinstance(
                step.get("arguments"), dict
            ) else {}
            missing = [k for k in required if k not in args]
            if missing:
                argument_errors.append({
                    "step": step_num if isinstance(step_num, int) else idx,
                    "mcp_tool": mcp_tool,
                    "missing": missing,
                    "detail": (
                        f"native step calling {mcp_tool} is missing required "
                        f"argument(s): {', '.join(missing)}"
                    ),
                })

    # ---- Cross-step dependency ordering (heuristic, soft warnings) -----
    # Seed the "known" sets from prior_state so cross-session plans
    # don't trigger false-positive ordering warnings for entities
    # created in earlier plans / by the operator in the Figma UI.
    known_collection_ids: set[str] = set()
    known_collection_names: set[str] = set()
    known_component_names: set[str] = set()
    known_page_names: set[str] = set()
    if prior_state is not None:
        known_collection_ids.update(prior_state.known_collection_ids)
        known_collection_names.update(prior_state.known_collection_names)
        known_component_names.update(prior_state.known_component_names)
        known_page_names.update(prior_state.known_page_names)

    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            continue
        op = step.get("operation", "")
        args = step.get("arguments") if isinstance(
            step.get("arguments"), dict
        ) else {}
        step_num = step.get("step") if isinstance(
            step.get("step"), int
        ) else idx

        # Record creations
        if op == "create_variable_collection":
            cid = args.get("collection_id")
            if cid:
                known_collection_ids.add(str(cid))
            name = args.get("name")
            if name:
                known_collection_names.add(str(name))
        elif op == "create_page":
            page_name = args.get("name")
            if page_name:
                known_page_names.add(str(page_name))
        elif op in ("create_component", "create_component_set"):
            comp_name = args.get("name")
            if comp_name:
                known_component_names.add(str(comp_name))

        # Check dependencies
        if op in _NEEDS_COLLECTION:
            cid = args.get("collection_id")
            if cid and str(cid) not in known_collection_ids:
                ordering_warnings.append(
                    f"Step {step_num} ({op}) references collection_id "
                    f"{cid!r} not seen in an earlier "
                    f"create_variable_collection step."
                )

        if op in _NEEDS_PARENT_COMPONENT:
            parent = args.get("parent_name")
            if parent and str(parent) not in known_component_names:
                ordering_warnings.append(
                    f"Step {step_num} ({op}) references parent "
                    f"{parent!r} not seen in an earlier "
                    f"create_component / create_component_set step."
                )

        if op in _NEEDS_PAGE:
            page = args.get("page_name")
            if page and str(page) not in known_page_names:
                ordering_warnings.append(
                    f"Step {step_num} ({op}) references page "
                    f"{page!r} not seen in an earlier create_page step."
                )

    is_executable = (not schema_errors) and (not argument_errors)
    return PlanValidationReport(
        plan_format_version=plan_format_version,
        step_count=len(steps),
        schema_errors=schema_errors,
        argument_errors=argument_errors,
        ordering_warnings=ordering_warnings,
        is_executable=is_executable,
        freshness_warnings=freshness_warnings,
    )


__all__ = ["PlanValidationReport", "PriorState", "validate_mcp_plan"]
