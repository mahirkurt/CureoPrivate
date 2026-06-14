# figma-forge API Stability Contract

> Effective from **v1.0.0** · last updated for **v1.4.0** · 2026-05-28 · binds all v1.x releases

This document is the **canonical agreement** between figma-forge and
its downstream consumers (skill bundle users, CI pipelines, library
embedders) about what identifiers, behaviors, and file formats are
covered by Semantic Versioning guarantees.

The public API surface grew from **22 symbols (v1.0.0)** to **32
symbols (v1.1.0)** to **36 symbols (v1.2.0)** to **39 symbols
(v1.3.0)** to **45 symbols (v1.4.0)** to **46 symbols
(v1.5.0)** to **48 symbols (v1.6.0)** — all additions are
append-only; every prior symbol retains its signature and semantics.
`API_VERSION` remains `"1.0"` because the v1.x contract is unchanged
by additive minor releases.

## 1. Public API Surface

The **single** stable import surface is the top-level package:

```python
import figma_forge as ff
```

Every identifier reachable through `ff.<name>` and listed in
`figma_forge.__all__` is **stable**. The full list at v1.0.0:

### 1.1 Version / contract

| Identifier      | Kind     | Purpose                                |
|-----------------|----------|----------------------------------------|
| `__version__`   | `str`    | The figma-forge release version        |
| `API_VERSION`   | `str`    | The public API contract version (`"1.0"`) |

### 1.2 Audit comparison (Mode 11 — AUDIT_DIFF)

| Identifier            | Kind        | Stability  |
|-----------------------|-------------|------------|
| `AuditSnapshot`       | dataclass   | stable     |
| `DiffReport`          | dataclass   | stable     |
| `GateTransition`      | dataclass   | stable     |
| `load_audit_snapshot` | function    | stable     |
| `compare_audits`      | function    | stable     |
| `format_diff_json`    | function    | stable     |
| `format_diff_markdown`| function    | stable     |

### 1.3 Audit trend (Mode 12 — AUDIT_TREND)

| Identifier              | Kind        | Stability  |
|-------------------------|-------------|------------|
| `GateTimeSeries`        | dataclass   | stable     |
| `TimePoint`             | dataclass   | stable     |
| `TrendReport`           | dataclass   | stable     |
| `load_audit_points`     | function    | stable     |
| `analyze_trend`         | function    | stable     |
| `format_trend_json`     | function    | stable     |
| `format_trend_markdown` | function    | stable     |
| `format_trend_html`     | function    | stable     |

### 1.4 Static lint (Mode 7 — PUBLISH_AUDIT static-only)

| Identifier         | Kind     | Stability  |
|--------------------|----------|------------|
| `run_static_lint`  | function | stable     |

### 1.5 Auto-remediate (Mode 8 — AUTO_REMEDIATE)

| Identifier            | Kind        | Stability  |
|-----------------------|-------------|------------|
| `RemediationAction`   | dataclass   | stable     |
| `RemediationContext`  | dataclass   | stable     |
| `RemediationOptions`  | dataclass   | stable     |
| `run_remediation`     | function    | stable     |

### 1.6 Supply-chain (v1.0 new)

Lazy-loaded — first access triggers `sigstore` / `pyOpenSSL` import.

| Identifier              | Kind        | Stability  |
|-------------------------|-------------|------------|
| `BundleManifest`        | dataclass   | stable     |
| `ProvenanceAttestation` | dataclass   | stable     |
| `build_bundle_manifest` | function    | stable     |
| `sign_manifest`         | function    | stable     |
| `verify_manifest`       | function    | stable     |

### 1.7 Transport layer (v1.1.0 new)

The transport layer abstracts how build operations reach Figma
(REST, plugin runtime, MCP, or no-op stub). See RFC v1.1 in
`docs/rfc/v1.1-transport-layer.md` for the full design.

| Identifier                  | Kind             | Stability  |
|-----------------------------|------------------|------------|
| `TransportAdapter`          | Protocol         | stable     |
| `TransportError`            | exception (base) | stable     |
| `AuthenticationError`       | exception        | stable     |
| `CapabilityUnsupportedError`| exception        | stable     |
| `StubTransport`             | class            | stable     |
| `PluginCaptureTransport`    | class            | stable     |
| `RestTransport`             | class            | stable     |
| `McpCursorTransport`        | class            | stable (v1.2.0) |
| `BackoffPolicy`             | dataclass        | stable (v1.2.0) |
| `ConcurrencyReport`         | dataclass        | stable (v1.2.0) |
| `check_concurrency`         | function         | stable (v1.2.0) |
| `PlanValidationReport`      | dataclass        | stable (v1.3.0) |
| `validate_mcp_plan`         | function         | stable (v1.3.0) |
| `plan_execution_layers`     | function         | stable (v1.6.0) |
| `PriorState`                | dataclass        | stable (v1.4.0) |
| `PlanRunner`                | class            | stable (v1.4.0) |
| `PlanRunResult`             | dataclass        | stable (v1.4.0) |
| `StepResult`                | dataclass        | stable (v1.4.0) |
| `DispatchResponse`          | dataclass        | stable (v1.6.0) |
| `AdaptiveConcurrency`       | dataclass        | stable (v1.4.0) |
| `ConcurrencyObservation`    | dataclass        | stable (v1.4.0) |
| `ObservationLog`            | class            | stable (v1.5.0) |
| `BatchPolicy`               | dataclass        | stable (v1.3.0) |
| `TransportRouter`           | class            | stable     |
| `PipelineResult`            | dataclass        | stable     |
| `run_pipeline`              | function         | stable     |

**Notes on transport stability:**

- The `TransportAdapter` Protocol's operation set is **append-only**:
  new operations may be added in minor releases; existing operation
  signatures remain stable. Adapters implementing the Protocol via
  structural typing (no inheritance) continue to satisfy
  `isinstance(x, TransportAdapter)` as long as they implement the
  existing operations.
- `run_pipeline`'s `stages` parameter accepts new stage names in
  minor releases (additive). The default stage list may grow in
  minor releases (it grew from 2 to 5 stages between v1.1.0-alpha.1
  and v1.1.0-beta.1); callers who depend on an exact stage set should
  pass `stages=[...]` explicitly.
- `RestTransport`'s `dry_run` parameter defaults to `True` through
  the v1.1.x series. A future minor release may flip the default to
  `False`; callers who depend on dry-run behavior should pass
  `dry_run=True` explicitly.
- The capability matrix (`figma_forge.transport.capability_matrix`)
  is **internal** — accessible but not part of the stable contract.
  Query it only through `TransportAdapter.supports()`.
- `McpCursorTransport` (v1.2.0) emits an **MCP tool-call plan** rather
  than executing operations directly. Its `render_mcp_plan()` JSON
  envelope carries a `plan_format_version` (currently `"1.0"`);
  the plan format is versioned independently of `API_VERSION` and
  follows the same additive-compatibility rule. The `supported-nl`
  capability level (natural-language dispatch via `Figma:use_figma`)
  is stable from v1.2.0. Which operations are `native` vs
  `supported-nl` may shift toward `native` in future minor releases
  as Figma's MCP write surface matures — this is a non-breaking
  improvement (a `supported-nl` operation becoming `native` only
  increases determinism; both remain "supported" for routing).
- **Instance composition** (v1.2.0): the operations `place_instance`
  and `set_instance_property`, and the `InstanceRef` reference type,
  are stable from v1.2.0. They are additive to the `TransportAdapter`
  Protocol's operation set (19 → 21). Adapters that cannot place
  instances (e.g. `RestTransport`) declare `unsupported` and raise
  `CapabilityUnsupportedError`; this is a stable, documented behavior.
- **`BackoffPolicy`** (v1.2.0) is a frozen dataclass; its fields
  (`max_retries`, `base_delay`, `max_delay`, `jitter`, `jitter_ratio`,
  `honor_retry_after`, `seed`) and methods (`should_retry`,
  `compute_delay`, `schedule`) are stable. `RestTransport`'s `backoff`
  parameter defaults to `None` (no retry) for backward compatibility;
  passing a policy is opt-in. The policy is pure arithmetic and does
  not sleep — callers sleep the returned delay.
- **Concurrency detection** (v1.2.0): `check_concurrency` and the
  frozen `ConcurrencyReport` dataclass are stable. `FileRef` gained an
  append-only `last_modified` field (default `""`). `run_pipeline`'s
  `detect_concurrency` keyword defaults to `False` (no check) for
  backward compatibility; `PipelineResult.concurrency_report` is
  `None` unless the check runs. The check is best-effort: adapters
  that can't read live state report `checked=False` and never raise.
- **MCP plan validation** (v1.3.0): `validate_mcp_plan` and the
  frozen `PlanValidationReport` dataclass are stable. The validator's
  **schema rules** (required envelope/step fields, `step_count`
  consistency, monotonic step numbers, mechanism-instruction
  coupling) are part of the stable contract — they may **gain** new
  rules in minor releases (additive), but existing rules will not be
  loosened. **Native argument-shape rules** track Figma's MCP tool
  signatures and may **expand** as new required arguments are added
  upstream; this is intentionally tracking, not contract — operators
  pinning to a specific behavior should pin a figma-forge version.
  **Ordering warnings** are heuristic and explicitly soft — their
  exact wording and detection rules are **not** part of the stable
  contract; never branch on warning text in CI.
- **MCP dispatch registry** (v1.3.0-alpha.2): the
  `figma_forge.transport.mcp_dispatch` module — including
  `McpDispatchSpec`, `REGISTRY`, and the helper accessors
  (`mcp_tool_for_operation`, `native_required_args`,
  `capability_level_for_operation`) — is **internal**. It is not
  exported on `figma_forge.__all__`. The registry's contents may
  change in any minor release (operations promoted from
  `use_figma_nl` to `native` as Figma's MCP write surface evolves).
  Consumers MUST NOT import or mutate it directly; the supported
  surface for affected behavior is the existing public API
  (`McpCursorTransport`, `CAPABILITY_MATRIX`, `validate_mcp_plan`).
- **`BatchPolicy`** (v1.3.0-beta.1) is a frozen dataclass; its fields
  (`max_concurrency`, `enabled`) are stable. `RestTransport`'s
  `batch` parameter defaults to `None` (sequential dispatch, v1.x
  behavior) for backward compatibility; passing a policy is opt-in.
  When enabled, write-side calls (non-GET) are deferred until
  `commit_session()` and dispatched in parallel via a thread pool.
  Per-call failures are recorded on the call dict's `error` key and
  counted in `SessionResult.operations_failed` rather than raised;
  the batch always completes all scheduled work (best-effort
  semantics). GET calls bypass deferral and dispatch immediately.
- **`PriorState`** (v1.4.0-alpha.1, extended in v1.5.0-alpha.1) is
  a frozen dataclass with four `frozenset[str]` hint fields plus
  the v1.5 freshness metadata field. Its semantics are stable: it
  can only **suppress** ordering warnings for entities listed in
  its hint sets — never introduce schema or argument errors, never
  affect `is_executable`. `validate_mcp_plan`'s `prior_state`
  keyword defaults to `None` (the v1.3 behavior); an empty
  `PriorState()` is equivalent to `None`. Frozen + frozenset →
  hashable for use as dict keys / cache keys. The four hint sets
  correspond to the validator's four ordering-check axes
  (collection ids, collection names, component names, page names) —
  new validator rules in future minor releases may consult the
  existing hint sets but will not require new fields without a
  major release.
  - **`last_verified_at: datetime | None = None`**
    (v1.5.0-alpha.1) — optional timezone-aware timestamp recording
    when the hint set was last reconciled with live Figma state.
    **Naive datetimes are rejected at construction with
    `ValueError`** (stable policy — silent UTC assumption is not
    forward-compatible across teams in multiple zones). Used by
    the `freshness_window_seconds` parameter of
    `validate_mcp_plan` and `PlanRunner.run`; ignored when neither
    side opts in. The field is append-only — v1.4 `PriorState()`
    callers see exact v1.4 behavior.
- **`validate_mcp_plan(..., freshness_window_seconds=None)`**
  (v1.5.0-alpha.1) — optional keyword parameter activating
  stale-hint detection. When set together with
  `prior_state.last_verified_at`, the validator computes the
  hint's age and appends to
  `PlanValidationReport.freshness_warnings` (new field, default
  empty list) when the age exceeds the window. **Stable contract:
  freshness warnings never affect `is_executable`** — the
  validator's executability semantics are determined only by
  schema and argument errors. Operators may legitimately validate
  offline with stale hints when live reconciliation is
  unavailable. Clock-skew detection (future `last_verified_at`)
  produces a distinct warning kept stable across releases.
  `PlanRunner.run(..., freshness_window_seconds=None)` forwards
  this parameter to the validator when `validate=True`.
  - **`freshness_window_overrides: dict[str, float] | None = None`**
    (v1.6.0-beta.1) — append-only keyword parameter for per-class
    TTLs. Keys are `"collection"`, `"component"`, `"page"`;
    `freshness_window_seconds` is the fallback for unlisted
    classes. A class is evaluated only if `prior_state` carries a
    hint for it; a class with neither override nor scalar fallback
    is skipped. Clock skew stays class-independent (one timestamp →
    one warning). **Scalar mode (`overrides=None`) is byte-for-byte
    the v1.5.0-alpha.1 behavior**, and per-class warnings, like all
    freshness signals, never affect `is_executable`.
    `PlanRunner.run(..., freshness_window_overrides=None)` forwards
    it.
    - **ID-vs-name split** (v1.7.0-alpha.1) — the key vocabulary
      gained `"collection_id"` and `"collection_name"`, refining the
      `"collection"` class into ID/name sub-classes (mapping to
      `known_collection_ids` / `known_collection_names`). The split
      is **opt-in**: it activates only when a sub-key is present;
      otherwise `"collection"` is the v1.6 combined class (one
      warning). Resolution is most-specific-wins (sub-key →
      `"collection"` → scalar → skip). Operators using only the
      legacy `"collection"` key see identical v1.6 behavior. This is
      a key-vocabulary extension of an existing parameter — **+0
      symbols**.
- **`AdaptiveConcurrency` + `ConcurrencyObservation`**
  (v1.4.0-beta.1, extended in v1.5.0-alpha.2): observed-rate-limit-
  driven recommendations for ``BatchPolicy.max_concurrency``. Both
  are frozen dataclasses; the ``AdaptiveConcurrency.recommend(
  current, requests_total, requests_429)`` method signature is
  stable. The algorithm
  - **`window: int = 1`** (v1.5.0-alpha.2) — append-only field for
    multi-batch smoothing. Default `1` is exactly v1.4 behavior;
    `window > 1` activates aggregation across the last `window`
    batch observations via the new ``recommend_aggregate()`` method.
    ``window`` is validated at construction (``window >= 1``).
    Operators who increase the window must accept the latency cost
    (recommendation requires up to `window` batches before
    converging to the new policy).
  - **`recommend_aggregate(*, current, observations)`**
    (v1.5.0-alpha.2) — stable method signature. Reuses
    ``recommend()`` under the hood, so the algorithm
    (scale-down above ``target_429_ratio``, scale-up at zero, hold
  within budget, hold under ``min_sample_size``) is the v1 contract.
  - **`suggest_window(observations, *, max_suggested=10)`**
    (v1.6.0-beta.1) — stable method signature. Recommends a
    ``window`` size from observed batch telemetry by taking the
    larger of two signals (sample sufficiency
    ``ceil(min_sample_size / avg_batch_total)`` and 429-ratio
    coefficient of variation), clamped to ``[1, max_suggested]``.
    Empty observations → ``1``. Like ``recommend``, it is **pure**:
    the frozen ``window`` field is never mutated — the operator
    rebuilds the policy with the suggested value. The exact
    heuristic weighting may evolve; the contract is only that the
    result lies in ``[1, max_suggested]`` and that the method never
    mutates. The returned rationale string MUST NOT be parsed.
  Refinements such as multi-batch smoothing or 5xx-aware policy may
  appear in future minor releases as new optional fields on
  ``AdaptiveConcurrency``, never as semantic changes to existing
  ones. The recommendation is advisory: the running policy is
  **never** mutated mid-batch — operators apply the recommendation
  on the next build by rebuilding ``BatchPolicy``. Rationale strings
  are human-readable and may evolve; operators MUST NOT parse them
  programmatically (use the numeric ``recommended_max_concurrency``
  and ``ratio_429`` fields instead). ``BatchPolicy.adaptive`` and
  ``SessionResult.adaptive_observation`` are both optional with
  default ``None`` (append-only fields; v1.3 callers see identical
  behavior). The ``ratio_429`` property on
  ``ConcurrencyObservation`` is zero-division safe.
- **`ObservationLog`** (v1.5.0-beta.1): a file-backed JSONL append
  log for ``ConcurrencyObservation`` records. Its constructor
  (``path``, ``max_records``) and public methods (``append``,
  ``read_recent``, ``clear``, ``__len__``, ``compact``) are stable. The on-disk
  wrapper format ``{"logged_at": ..., "observation": {...}}`` is a
  stable contract — the reader tolerates both the wrapper and a
  bare observation dict, filters unknown keys (forward
  compatibility), and skips records missing required fields. The
  log never raises on read (corrupted lines are silently dropped).
  ``compact(keep=None)`` (v1.6.0-beta.1) is the operator-triggered
  counterpart to the automatic amortized trim: it runs
  unconditionally, drops corrupted/blank lines and overflow records
  (keeping the most recent ``keep`` valid records; default
  ``max_records``), is atomic under the same exclusive lock as
  ``append``, returns the count of removed lines, performs no
  rewrite when already clean and within budget (returns ``0``),
  returns ``0`` for a missing file, and raises ``ValueError`` for
  ``keep < 1`` (use ``clear`` to drop all).
  - **`shard_per_process: bool = False`** (v1.7.0-alpha.2) —
    append-only field. When ``True``, each writer process appends to
    its own shard file (``{stem}.{shard-id}{suffix}``) **without an
    exclusive lock**, sidestepping network-FS lock contention.
    ``read_recent`` globs all shards (plus a bare single-file path,
    for mode cross-compatibility) and merges by ``logged_at``;
    ``compact`` compacts each shard independently; ``clear`` removes
    all shards. Shard identity (``pid-host_token-start_token``) is
    unique per concurrent writer and stable for its lifetime.
    Default ``False`` is byte-for-byte the v1.6 single-file behavior.
    This is a field on the existing class — **+0 symbols** (RFC v1.7
    §5.1: parameter, not subclass).
  - **`compact(reap_after_seconds=...)`** (v1.7.0-beta.1) —
    keyword-only parameter. In sharded mode, ``compact`` reaps dead
    shards (files whose mtime is older than ``reap_after_seconds``);
    **on by default** at a conservative one week, ``None`` disables
    it. This process's own shard and a bare single-file path are
    **never** reaped (alive / legacy). A reaped shard's records count
    toward the returned removed total. Ignored in single-file mode.
    Keyword parameter on the existing ``compact`` — **+0 symbols**.
  ``max_records`` is a soft cap: the file may transiently hold up
  to ``2 × max_records`` lines between amortized trims, but
  ``read_recent`` always returns at most the requested count.
  ``RestTransport.observation_log`` is an optional field (default
  ``None``; append-only — v1.5-alpha.2 callers see identical
  behavior); when set with an ``AdaptiveConcurrency`` policy it
  seeds the observation history at construction and appends on
  ``commit_session``, extending multi-batch smoothing across
  process boundaries.

- **`PlanRunner` + `PlanRunResult` + `StepResult`**
  (v1.4.0-alpha.2): the reference MCP plan interpreter. The class
  constructor parameters (`native_dispatch`, `nl_dispatch`,
  `on_step`, `abort_on_failure`) and the `run()` method's keyword
  arguments (`validate`, `prior_state`) are stable. Default
  dispatch callables are internal no-ops returning a sentinel
  shape `{"_noop": True, ...}` — operators MUST NOT depend on the
  exact sentinel keys, which may grow additively (e.g. for
  diagnostic fields). `StepResult` is frozen; its fields are
  stable. `PlanRunResult.is_success` semantics: True iff
  `steps_failed == 0` and `aborted_on_step is None` and (when
  validation ran) `validation_report.is_executable is True`. The
  runner does **not** retry; per-step retry is the dispatch
  callable's responsibility.
  - **`run(..., freshness_window_seconds=None)`** (v1.5.0-alpha.1)
    — forwards to `validate_mcp_plan` when `validate=True`.
  - **`StepResult.dispatch_response`** (v1.6.0-alpha.1) — optional
    typed accessor (default `None`; append-only field) holding the
    `DispatchResponse` the callable returned, if any.
- **`DispatchResponse`** (v1.6.0-alpha.1): an opt-in frozen
  dataclass a `PlanRunner` dispatch callable may return. Its five
  fields (`ok`, `entity_id`, `raw`, `retry_attempts`, `warnings`)
  are stable. The contract: returning a `DispatchResponse` is
  **optional** — a non-`DispatchResponse` return is always treated
  as success (the v1.5 behavior), so existing callables need no
  changes. `ok=False` is a soft failure that marks the step
  `"failure"` and triggers `abort_on_failure` without the callable
  raising; the `warnings` become the `StepResult.error` string.
  The runner never inspects opaque (non-`DispatchResponse`) returns
  for failure signals.
- **`plan_execution_layers(plan)`** (v1.6.0-alpha.2): computes a
  topological layering of plan steps for concurrent execution.
  Returns `list[list[int]]`; each inner list is a set of step
  numbers with no inter-dependencies, sorted ascending; the outer
  list is dependency-ordered. The dependency model mirrors the
  validator's ordering heuristic exactly. The function is pure and
  validator-independent (it does not raise on ordering anomalies;
  cycles degrade to singleton layers). The result is a partition of
  the plan's step set — every step appears in exactly one layer.
- **`PlanRunner.run(..., concurrent=False, max_workers=4)`**
  (v1.6.0-alpha.2): append-only keyword parameters. `concurrent=False`
  is the exact sequential behavior. `concurrent=True` dispatches each
  dependency layer across a thread pool. Stable contract:
  `step_results` is always assembled in plan order regardless of
  completion order; `on_step` fires in plan order; `abort_on_failure`
  is layer-granular (the failing layer completes, later layers are
  skipped, `aborted_on_step` = lowest failing step in that layer).
  Both paths share the internal `_execute_step` helper, so StepResult
  semantics (including `DispatchResponse` recognition) are identical
  across modes.

## 2. Stability Tiers

### 2.1 Stable

All identifiers re-exported by `figma_forge.__all__`.

**v1.x guarantee** — within the v1.x series:

- Function signatures are append-only (new optional kwargs may be
  added at the end; existing positional and keyword arguments retain
  their meaning).
- Dataclass fields are append-only (new optional fields may be added;
  existing fields retain their meaning and type).
- Return types are append-only (new attributes may be added; existing
  attributes retain their meaning and type).
- Exit codes for CLI tools (`scripts/*.py`) retain their meaning.
- JSON schema versions retain backward compatibility (existing fields
  retain their meaning; new optional fields may be added).

Breaking changes to any of the above require a major version bump
(v2.0.0).

### 2.2 Experimental

Identifiers in submodules `_*` or marked with `# EXPERIMENTAL` comment.
**No stability guarantee** — these may change in any minor version
(v1.1, v1.2, …) and disappear without deprecation period.

At v1.0.0 there are no experimental public identifiers.

### 2.3 Internal

Anything not re-exported via `figma_forge.__all__`. This includes:

- Direct submodule paths (`audit_diff.base`, `auto_remediate.runner`,
  `publish_audit.gates`, etc.)
- Helper functions prefixed with `_`
- Module-level constants prefixed with `_`

**No stability guarantee whatsoever**. Internal identifiers may
change shape, name, or location in any release — including patch
releases (v1.0.1).

## 3. Deprecation Policy

When a stable identifier needs to be removed or have its semantics
changed, the lifecycle is:

1. **Deprecation announcement** — the identifier is marked
   deprecated in CHANGELOG.md and emits a `DeprecationWarning` at
   runtime. The deprecation entry includes:
   - The replacement identifier (if any)
   - The earliest version in which the identifier will be removed
   - A migration example

2. **Soft removal** — the identifier remains available but warning
   message is upgraded to `FutureWarning` (visible by default).
   Minimum **one minor version** at this stage.

3. **Hard removal** — in a major version bump only (v2.0.0).

## 4. JSON Schema Versioning

| Schema              | Version | First shipped in | Stability for v1.x |
|---------------------|---------|------------------|---------------------|
| Audit report        | 1.0     | v0.2.0           | additive only       |
| Audit diff          | 1.0     | v0.3.1-alpha.1   | additive only       |
| Audit trend         | 1.0     | v0.3.1           | additive only       |
| Bundle manifest     | 1.0     | v0.3.0-rc.1      | additive only       |
| SLSA provenance     | 1.0     | v1.0.0           | additive only       |

"Additive only" means: new optional fields may appear in v1.x
patch and minor releases. Existing fields retain their location,
name, type, and meaning. Consumers should ignore unknown fields.

Breaking schema changes (renaming a field, changing its semantics,
removing it) require a schema version bump and at least one minor
version of grace period during which both schema versions are
emitted in parallel.

## 5. CLI Stability

The CLI flags of these scripts are **stable**:

| CLI                          | Public flags                                              |
|------------------------------|-----------------------------------------------------------|
| `scripts/publish_audit.py`   | `--library-registry`, `--static-only`, `--output-format`, `--output`, `--strict` |
| `scripts/auto_remediate.py`  | `--audit-report`, `--library-dir`, `--output-channel`, `--output-dir`, `--locale` |
| `scripts/orchestrate.py`     | `--manifest`, `--library-dir`, `--dry-run`, `--resume`, `--only`, `--continue-on-failure`, `--validate-only` |
| `scripts/bundle_manifest.py` | `--library-dir`, `--output`, `--verify`, `--quiet` |
| `scripts/audit_diff.py`      | `--baseline`, `--current`, `--output`, `--output-format`, `--fail-on` |
| `scripts/audit_trend.py`     | `--glob`, `--inputs`, `--output`, `--output-format`, `--since`, `--until`, `--fail-on-high-drift` |
| `scripts/sign.py`            | `--library-dir`, `--output-dir`, `--identity`, `--sign-mode`, `--source-repository`, `--source-commit`, `--builder-id` |
| `scripts/verify.py`          | `--manifest`, `--provenance`, `--signature`, `--library-dir`, `--expected-identity`, `--expected-oidc-issuer` |

Flag **defaults** are stable. Flag **behavior** is stable. New
optional flags may be added in minor releases. Flag removal or
behavioral change requires a major version bump.

## 6. Python Version Support

| Python version | Status at v1.0.0 |
|----------------|--------------------|
| 3.10           | supported          |
| 3.11           | supported          |
| 3.12           | supported (CI default) |
| 3.13           | supported          |

The minimum supported Python version may be raised in a major
version bump (v2.0.0) with at least one minor version of advance
notice.

## 7. Optional Dependencies

| Dependency  | Used by          | Required?   |
|-------------|------------------|-------------|
| `sigstore`  | supply-chain     | optional (graceful fallback to sha256-only) |
| `pytest`    | test harness     | development only |

`sigstore` is the only optional runtime dependency. When absent,
`figma_forge.sign_manifest(..., sign_mode="auto")` falls back to
the sha256-only mode without raising. Verification of a sigstore
signature without `sigstore` installed raises a clear error.

## 8. What This Document Does Not Cover

- **The Düstur Tasarım Sistemi bundle** — this is a sample/reference
  bundle and may evolve independently.
- **Mapper modules** (`scripts/mapper_*.py`) — these are
  contributions to the ecosystem and follow their own versioning.
- **Skill manifest** (`SKILL.md` frontmatter) — covered by the
  SMP v1.0 contract, not by this document.

## 9. Reporting API Drift

If you encounter behavior that contradicts this document, that is a
**bug**. File an issue with:

- The figma-forge version (`python3 -c "import figma_forge; print(figma_forge.__version__)"`)
- The Python version
- A minimal reproduction
- The expected vs. observed behavior
