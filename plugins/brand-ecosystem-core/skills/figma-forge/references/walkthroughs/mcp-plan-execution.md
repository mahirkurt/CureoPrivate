# MCP Plan Execution — Operator & Agent Walkthrough

> `validate_mcp_plan` + agent execution semantics · figma-forge v1.3.0-alpha.1

This walkthrough covers two parts of the MCP plan lifecycle that
`mcp-transport.md` didn't address: how to **statically validate** a
plan before any agent touches Figma, and what **execution semantics**
an agent should follow when consuming the plan.

It assumes you have read `mcp-transport.md` for the plan envelope
format and the `McpCursorTransport` model.

---

## 1. The plan lifecycle, end-to-end

```
figma-forge                                    agent + Figma MCP host
─────────────                                  ─────────────────────────

run_pipeline(transport=mcp_router)
    └─→ mcp.render_mcp_plan() ──── plan.json ───→  validate_mcp_plan(plan.json)
                                                      └─→ PlanValidationReport
                                                            ├─ schema_errors
                                                            ├─ argument_errors
                                                            └─ ordering_warnings

                                                  if report.is_executable:
                                                      for step in plan.steps:
                                                          if step.mechanism == "native":
                                                              call MCP tool step.mcp_tool
                                                                   with step.arguments
                                                          else:  # use_figma_nl
                                                              call Figma:use_figma
                                                                   with step.instruction
```

Validation is **cheap** (pure Python, no I/O) and **fast** (linear in
step count). Run it on every plan before execution — the cost is
milliseconds, the value is catching schema breaks before they reach
Figma.

---

## 2. Validating a plan

```python
import figma_forge as ff
import json

# Either from a live build:
plan_json = mcp.render_mcp_plan()

# Or from a saved file:
plan_json = open("dustur-plan.json").read()

report = ff.validate_mcp_plan(plan_json)

if not report.is_executable:
    for e in report.schema_errors:
        print(f"SCHEMA: {e}")
    for e in report.argument_errors:
        print(f"ARGUMENT (step {e['step']}): {e['detail']}")
    raise SystemExit(1)

for w in report.ordering_warnings:
    print(f"WARNING: {w}")

# Plan is executable — pass to the agent
```

### What the validator checks

| Check | Severity | Blocks execution |
|---|---|---|
| Envelope is a JSON object | schema | yes |
| Envelope has `plan_format_version`, `adapter`, `step_count`, `steps` | schema | yes |
| `step_count == len(steps)` | schema | yes |
| `step_count` is an integer | schema | yes |
| Each step has `step`, `operation`, `mcp_tool`, `mechanism`, `arguments` | schema | yes |
| `mechanism` ∈ {"native", "use_figma_nl"} | schema | yes |
| Step numbers monotonically increment | schema | yes |
| Native step has no `instruction` field | schema | yes |
| `use_figma_nl` step has a non-empty `instruction` | schema | yes |
| Native step's `arguments` carries every key the MCP tool expects | argument | yes |
| Dependency: `create_variable.collection_id` references prior `create_variable_collection` | ordering | no (warning) |
| Dependency: `place_instance.parent_name` references prior `create_component` | ordering | no (warning) |
| Dependency: `create_component.page_name` references prior `create_page` | ordering | no (warning) |

### Why ordering is soft

The ordering checks are heuristic. They produce false positives in
two legitimate cases:

1. **Cross-session plans**. A plan that only adds new variables to a
   collection created in an earlier plan correctly omits the
   `create_variable_collection` step. The validator can't see the
   prior plan, so it warns — but the plan is fine.
2. **Operator pre-creates the file**. The operator may pre-create
   pages or top-level components in Figma's UI before running a
   build. Subsequent `create_component` steps then have no
   `create_page` in this plan — but they're valid against the live
   file.

Ordering warnings are advisory: review them, satisfy the dependency
in your environment, and proceed. They never block.

### Suppressing cross-session false positives — `PriorState` (v1.4.0)

When you know certain entities already exist (from an earlier plan
or hand-created in Figma's UI), pass a `PriorState` to suppress the
corresponding ordering warnings. This is the canonical way to use
the validator with multi-session pipelines:

```python
import figma_forge as ff

# Build N+1: only adding new variables to an existing collection.
prior = ff.PriorState(
    known_collection_ids=frozenset({"vc_renkler"}),
    known_component_names=frozenset({"Button", "Card"}),
    known_page_names=frozenset({"Foundations", "Components"}),
)
report = ff.validate_mcp_plan(plan, prior_state=prior)
# Orphan-collection / orphan-parent / orphan-page warnings for
# entities listed above are suppressed; warnings for any genuinely
# missing dependency remain.
```

`PriorState` is a frozen dataclass with four `frozenset[str]` fields
— hashable, cacheable, cheap to share across multiple validations
within a single build pipeline. A default `PriorState()` (all empty)
is equivalent to passing `None`. The hint set is purely additive: it
can only **suppress** warnings, never introduce schema or argument
errors. Genuinely orphan references (a `create_variable` against a
collection id that's neither in the plan nor in `PriorState`) still
warn correctly.

**Sourcing the hint set**. In practice operators populate
`PriorState` from one of three places:

1. **A previous build's audit trail** — record the IDs / names
   created and pass them to the next build's validator.
2. **A live Figma file query** — at the start of a build, ask the
   Figma MCP for the current file's collection IDs / page names
   and seed `PriorState` from the answer. (Requires a live MCP
   host; not available in dry-run validation.)
3. **A manifest checked into the bundle** — a JSON file in the
   library bundle listing the entities the operator expects to
   exist before the build runs. Simplest and most reproducible.

### Stale-hint detection — `last_verified_at` (v1.5.0-alpha.1)

`PriorState` accepts an optional timezone-aware `last_verified_at`
datetime recording when the hint set was last reconciled with the
live Figma state. When `validate_mcp_plan` is called with a
`freshness_window_seconds` argument, hints older than that window
add a `freshness_warnings` entry to the report.

```python
from datetime import datetime, timezone

prior = ff.PriorState(
    known_collection_ids=frozenset({"vc_renkler"}),
    last_verified_at=datetime.now(timezone.utc),  # tz-aware required
)

# Five-minute TTL: hint stale → warning, but is_executable stays True
report = ff.validate_mcp_plan(
    plan, prior_state=prior, freshness_window_seconds=300,
)
if report.freshness_warnings:
    log.warning(report.freshness_warnings[0])
```

Two semantic choices worth noting:

- **Freshness warnings never block execution.** Stale hints
  contribute to `freshness_warnings` but do not affect
  `is_executable` — the operator may legitimately validate with
  stale hints when live reconciliation is unavailable (offline
  build, CI without MCP credentials). Treating staleness as a
  hard error would force operators into one of two failure
  modes: either skip the freshness check (defeating the purpose)
  or block legitimate offline builds (defeating the workflow).
- **Naive datetimes are rejected at construction.** Passing
  `last_verified_at=datetime.now()` (no tzinfo) raises
  `ValueError` from `PriorState.__post_init__`. The policy is
  explicit: a hint with no timezone is ambiguous about which
  clock it refers to, and silently treating it as UTC can mask
  staleness across a team operating in multiple zones. The error
  surfaces at the call site rather than deep inside the
  validator.

`PlanRunner.run()` forwards the `freshness_window_seconds` parameter
to the validator, so the same freshness check applies in the
runner path:

```python
result = ff.PlanRunner().run(
    plan, prior_state=prior, freshness_window_seconds=300,
)
# result.validation_report.freshness_warnings is populated if stale.
# Dispatch still happens — freshness is advisory.
```

#### Per-entity-class freshness TTLs (v1.6.0-beta.1)

A single window treats all hints as aging at the same rate, but
they don't: a variable collection's ID is far more stable than a
component's name, which may be renamed between builds. Pass
`freshness_window_overrides` to give each entity class its own TTL:

```python
report = ff.validate_mcp_plan(
    plan, prior_state=prior,
    freshness_window_seconds=300,                 # fallback for unlisted classes
    freshness_window_overrides={"collection": 3600},  # collections: 1 hour
)
# A 600s-old PriorState now yields:
#   - no warning for collection hints (within 3600s)
#   - a warning for component and page hints (exceed 300s fallback)
```

The class keys are `"collection"`, `"component"`, and `"page"`.
Three rules govern the per-class mode:

- **A class is evaluated only if it has a hint.** An empty
  `known_component_names` means no component warning, regardless of
  TTL.
- **`freshness_window_seconds` is the fallback.** A class with no
  override uses the scalar window; a class with neither an override
  nor a scalar window is skipped entirely (so
  `freshness_window_overrides={"component": 300}` with no scalar
  evaluates *only* components).
- **Clock skew stays class-independent.** A future
  `last_verified_at` produces one skew warning, not one per class,
  because there is a single timestamp. Scalar mode
  (`overrides=None`) is byte-for-byte the v1.5.0-alpha.1 behavior.

`PlanRunner.run()` forwards `freshness_window_overrides` too.

#### ID-vs-name freshness split (v1.7.0-alpha.1)

The `"collection"` class covers both a collection's stable *ID* and
its mutable display *name* — but they age differently. A
variable-collection ID is fixed for the collection's lifetime, while
its name can be renamed between builds. Two new keys split them:

```python
report = ff.validate_mcp_plan(
    plan, prior_state=prior,
    freshness_window_overrides={
        "collection_id":   3600,   # stable → 1 hour
        "collection_name":  300,   # mutable → 5 minutes
    },
)
# A 600s-old PriorState now warns on collection_name (exceeds 300s)
# but not collection_id (within 3600s).
```

`"collection_id"` maps to `known_collection_ids`,
`"collection_name"` to `known_collection_names`. Two rules:

- **The split is opt-in.** It activates only when `"collection_id"`
  or `"collection_name"` is present. With only the legacy
  `"collection"` key (or none), `"collection"` stays the single
  combined class of v1.6 — one warning, never two. Operators who
  don't adopt the new keys are unaffected.
- **Most-specific wins.** For a sub-class, resolution is sub-key →
  `"collection"` alias → scalar → skip. So
  `{"collection_id": 3600, "collection": 300}` gives IDs a 3600s
  window and names the 300s `"collection"` fallback. The warning
  text names the sub-class (`"collection_id hints are …"`), so you
  see which refinement is stale.

### Native argument shapes

The validator enforces that native steps carry every key the named
MCP tool expects. The required key sets are recorded in the
validator and reflect the public Figma MCP surface as of v1.3.0:

| MCP tool                              | Required argument keys |
|---------------------------------------|------------------------|
| `Figma:create_new_file`               | `name`, `file_kind` |
| `Figma:get_metadata`                  | `key` |
| `Figma:get_variable_defs`             | `file_key`, `name` |
| `Figma:send_code_connect_mappings`    | `node_id`, `component_name`, `framework`, `import_statement`, `code_example`, `props_mapping` |
| `Figma:get_code_connect_map`          | `file_key` |

Extra keys in `arguments` are **allowed and ignored** — the schema is
forward-compatible. When Figma adds a new optional argument to one
of these tools, you don't need a figma-forge release to start passing it.

---

## 3. Executing a plan — agent runbook

> **v1.4.0-alpha.2 update**: this section's semantics are now
> available as **working code** in `figma_forge.PlanRunner`.
> Operators and agents should either use the runner directly or
> treat its source as the reference implementation. The prose
> below remains as the readable specification; the runner is the
> normative executable form. If the two ever drift, the runner
> wins.

```python
import figma_forge as ff

# Dry-run (no-op dispatch — validates and walks)
runner = ff.PlanRunner()
result = runner.run(plan, prior_state=prior)

# Live MCP host
runner = ff.PlanRunner(
    native_dispatch=lambda tool, args: my_mcp.call(tool, args),
    nl_dispatch=lambda instruction, args: my_mcp.call(
        "Figma:use_figma", {"instruction": instruction}),
    on_step=lambda s: print(f"step {s.step}: {s.status} ({s.duration_ms:.0f}ms)"),
    abort_on_failure=False,
)
result = runner.run(plan, prior_state=prior)
print(f"{result.steps_succeeded}/{result.steps_attempted} ok, "
      f"{result.steps_failed} failed")
```

The remainder of this section documents what the runner does — and
what your dispatch callables should do — for each step type.

The plan is an ordered list. An agent walks it sequentially. For each
step:

### Native step

```pseudocode
result = mcp.call(step.mcp_tool, step.arguments)
# result carries any IDs / metadata Figma returns; the agent may
# stash them for reference but figma-forge does not require them.
```

`step.arguments` is shaped to the MCP tool's signature. Pass it
straight through. `PlanRunner` calls `native_dispatch(step.mcp_tool,
step.arguments)`.

### `use_figma_nl` step

```pseudocode
result = mcp.call("Figma:use_figma", step.instruction)
# Then VERIFY: ask Figma metadata to confirm the intended entity
# now exists with the intended shape.
```

`step.arguments` carries the structured intent (the agent can use it
to phrase its own prompt if `step.instruction` is missing or to
cross-check the result). `step.instruction` is the ready-to-use
natural-language string. `PlanRunner` calls
`nl_dispatch(step.instruction, step.arguments)`.

### Structured dispatch returns — `DispatchResponse` (v1.6.0-alpha.1)

Dispatch callables may return **any** object; the runner captures it
opaquely in `StepResult.response`. Returning a `DispatchResponse`
instead is **opt-in** and gives the runner three things it can't
otherwise see:

```python
def native_dispatch(mcp_tool, args):
    resp = my_mcp.call(mcp_tool, args)
    if resp.status == "name_collision":
        return ff.DispatchResponse(
            ok=False,                       # → step marked "failure"
            raw=resp,
            warnings=("name collision: " + args["name"],),
        )
    return ff.DispatchResponse(
        ok=True,
        entity_id=resp.node_id,             # stash the created node ID
        raw=resp,
        retry_attempts=resp.attempts,       # surface retry telemetry
    )
```

- **`ok=False` is a soft failure.** The step is marked `"failure"`
  and `abort_on_failure` triggers, *without* the callable having to
  raise. Use it when the MCP host returned a 2xx but the operation
  was logically unsuccessful (entity already exists, name collision,
  validation rejection). The `warnings` become the `StepResult.error`
  string.
- **`entity_id`** lets you stash created node IDs without parsing
  `raw`.
- **`retry_attempts`** surfaces retry telemetry the runner cannot
  see — the runner does not retry; that is the callable's job.

A non-`DispatchResponse` return is always treated as success (the
v1.5 behavior), so existing dispatch callables need no changes. When
a `DispatchResponse` is returned, it appears both as
`StepResult.response` (the raw return) and `StepResult.dispatch_response`
(typed accessor).

### Concurrent execution — layered parallel dispatch (v1.6.0-alpha.2)

By default `PlanRunner.run` walks the plan sequentially in step
order. This is always safe: the plan emitter orders steps so every
dependency precedes its consumer (a `create_variable_collection`
before the `create_variable` steps that reference it; a `create_page`
before the `create_component` steps on it). But sequential
execution leaves throughput on the table — many steps have **no**
inter-dependencies and could run in parallel.

`run(..., concurrent=True, max_workers=N)` partitions the plan into
**dependency layers** and dispatches each layer's steps across a
thread pool:

```python
result = runner.run(plan, concurrent=True, max_workers=8)
```

The layering is computed by `plan_execution_layers(plan)`, which you
can also call directly to inspect parallelism:

```python
layers = ff.plan_execution_layers(plan)
# e.g. [[1, 2, 5], [3, 4], [6]]
#   layer 0: steps 1, 2, 5 — independent producers (collections, page)
#   layer 1: steps 3, 4    — variables that reference collections 1 & 2
#   layer 2: step 6        — an instance that references a component
```

Three guarantees make this safe to adopt:

- **Same dependency model as the validator.** Layering uses the
  identical producer/consumer edges the validator's ordering check
  uses (collection → variable; page → component; component →
  instance). A reference to an entity with no in-plan producer
  (created in a prior session or by hand) imposes no ordering — that
  step lands in layer 0.
- **Plan-ordered results regardless of completion order.**
  `step_results` is always assembled by ascending step number, so a
  concurrent run is indistinguishable from a sequential one in its
  output — only faster. The `on_step` callback also fires in plan
  order, after the run assembles results.
- **Layer-granular abort.** With `abort_on_failure=True`, a failure
  does not interrupt steps already in flight: the failing step's
  layer completes (every step in it finishes), then all later layers
  are marked `"skipped"`. `aborted_on_step` is the lowest-numbered
  failing step in the aborting layer. This differs from sequential
  abort (which halts at the exact failing step) because thread-pool
  tasks cannot be reliably cancelled once started — completing the
  layer is the honest, deterministic behavior.

**When to use it.** Concurrency helps most on wide, shallow plans —
many independent collections, pages, or icon imports. It helps least
on deep chains (a fully transitive plan expands to one step per
layer, i.e. no parallelism). The validation gate, `PriorState`, and
freshness checks all run exactly as in sequential mode. Pick
`max_workers` to match your MCP host's concurrency tolerance — the
runner does not rate-limit; that is the transport/host's job (see
`AdaptiveConcurrency`).

### Idempotency

Many figma-forge operations are naturally idempotent (creating a
variable that already exists by name returns the existing one). For
the rest, the agent should:

- For `native` steps, trust the MCP tool's idempotency semantics
- For `use_figma_nl` steps, **query before creating** when the
  operation is expensive — e.g. before `import_svg_as_component`,
  ask `Figma:get_metadata` whether a component with that name
  already exists on the target page

### Error recovery

An MCP call that fails should:

1. **Retry transient failures** (rate limit, 5xx) — the agent's MCP
   host should already do this; if not, sleep and retry up to a
   policy-defined limit.
2. **Surface non-transient failures** to the operator with the
   step number, operation, and the underlying error. The operator
   decides whether to fix the source bundle, skip the step, or
   abort the build.
3. **Never silently skip** — a "missing component" warning at
   execution time should propagate.

### Verification after `use_figma_nl` steps

Because `use_figma_nl` is non-deterministic, the agent should verify
the outcome of each such step against `step.arguments`. Concrete
patterns:

- After `create_variable_collection (name="Renkler", modes=[…])`,
  query `Figma:get_variable_defs` and confirm a collection with that
  name and those modes exists.
- After `create_component_set (name="Button", variant_count=57)`,
  query `Figma:get_metadata` for the page and confirm a ComponentSet
  with that name and ≥ that variant count exists.
- After `import_svg_as_component`, confirm the component exists and
  has the expected `size`.

A verification failure should surface as a warning, not a hard error
— Figma's generative layer may have produced an acceptable but
not-byte-identical result.

---

## 4. The `pytest -m live` convention

For operators who can run against a real Figma file with a live MCP
host, a `live` pytest marker is recommended:

```python
@pytest.mark.live
def test_plan_executes_against_live_figma():
    plan = build_plan_for("real-figma-file-key")
    report = ff.validate_mcp_plan(plan)
    assert report.is_executable
    # ... drive the MCP host ...
    # ... assert post-build state matches expectation ...
```

These tests are excluded from default `pytest` runs (`pytest -m "not
live"`) so the sandbox CI stays green; operators with credentials run
`pytest -m live` from their environment. This is the same convention
the v1.1.0 GA accepted for the deferred "real-Figma integration"
acceptance criterion.

---

## 5. Limitations

- **No semantic argument validation for `use_figma_nl` steps**. The
  validator only enforces native-tool argument shapes; the
  natural-language instruction is opaque to the validator. A
  malformed instruction surfaces only at execution.
- **Heuristic ordering**. The validator does not build a full
  dependency graph; it tracks "known" collections / components /
  pages from creation steps and warns on references it hasn't seen.
  False positives are possible (see §2 "Why ordering is soft").
- **No batch / parallel validation**. v1.3's batch dispatch
  (roadmap) will add operation-grouping; the validator currently
  treats all steps as sequential. Batch metadata will be additive
  to the plan format when shipped.
