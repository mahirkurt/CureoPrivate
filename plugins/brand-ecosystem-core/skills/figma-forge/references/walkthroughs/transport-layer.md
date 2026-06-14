# Transport Layer (v1.1.0-alpha)

> Status: v1.1.0-alpha.1 · RFC merged · alpha implementation · live REST execution staged for v1.1.0 GA

`figma-forge` v1.1 introduces a **transport abstraction layer** that
separates _what_ the pipeline wants to do (`create_variable_collection`,
`import_svg_as_component`, …) from _how_ each operation reaches Figma
(REST, plugin runtime, MCP server, or a no-op stub).

This walkthrough explains the architecture, the four adapters that
ship in alpha, the preference-ordered router, the new
`ff.run_pipeline()` API, and the path to v1.1.0 GA.

## Why a transport layer?

Each of the seven "live" orchestrate modes (`SCAFFOLD`,
`FOUNDATIONS_BUILD`, `COMPONENTS_BUILD`, `ICONS_BUILD`,
`PATTERNS_BUILD`, `CODE_CONNECT`, `PUBLISH`) reaches Figma through a
channel with different authentication, capabilities, latency, and
error shapes. Without abstraction, every mode would either be locked
to one channel (sacrificing reachability) or carry channel-branching
logic throughout (sacrificing maintainability).

The transport layer is the single seam where channel selection
happens. Pipeline code calls one method, e.g.

```python
adapter.create_variable_collection(
    file_key="...", name="Renkler", modes=["Aydınlık", "Karanlık"]
)
```

and the adapter — selected at routing time — issues whatever channel
operation actually performs the work, or queues it, or captures it
into a TypeScript script, or logs it.

## Four adapters in v1.1.0-alpha

| Adapter                  | Identifier         | Channel                                    | Auth needed       |
|--------------------------|--------------------|---------------------------------------------|-------------------|
| `StubTransport`          | `stub`             | none (always-success no-op + log)          | none              |
| `PluginCaptureTransport` | `plugin-capture`   | accumulates → emits TypeScript script       | none              |
| `RestTransport`          | `rest-v1`          | Figma REST API (HTTP)                       | Figma PAT         |
| _McpCursorTransport_     | `mcp-cursor`       | _placeholder — implementation in v1.2_      | ambient OIDC      |

### `StubTransport`

The always-available fallback. Every operation succeeds and is
recorded as a structured log entry on
`stub.operations_log`. Use cases:

- Unit tests — every other adapter is mocked through Stub
- CI dry-runs — see what the pipeline would do without touching Figma
- Router fallback — when no preferred adapter handles an op

### `PluginCaptureTransport`

A buffering adapter that accumulates operations and, on
`commit_session`, renders a single Figma plugin TypeScript script the
operator pastes into Figma → Plugins → Development → Open Console.

This is the continuation of the v0.3.1 plugin channel — every
template-literal escape, idempotent guard (find by name → update or
create), and locale-aware header is inherited from G02 / G13 / G14
strategies.

**Locale**: pass `locale="tr-TR"` for a Turkish header, default is
`"en-US"`. Both produce identical operational behavior.

**Idempotency**: re-running the captured script does **not** produce
duplicates. Each `create_*` operation in the script first checks for
an existing node with the same name; updates in place if found,
creates otherwise.

```python
import figma_forge as ff

plug = ff.PluginCaptureTransport(locale="tr-TR")
token = plug.begin_session()

# Capture some operations
plug.create_variable_collection(
    file_key="x", name="Renkler", modes=["Aydınlık", "Karanlık"]
)
plug.create_variable(
    collection_ref=collection_ref, name="color.tbk.9",
    type="COLOR",
    values_per_mode={"Aydınlık": "#E30A17", "Karanlık": "#FF1F2D"},
)

# Materialize the script
result = plug.commit_session(token)
script = result.artifacts["typescript_script"]
print(script)  # paste this into Figma plugin console
```

### `RestTransport` (alpha skeleton)

The Figma REST API adapter. v1.1.0-alpha **stages** the operations
(queue them in `pending_calls`) without dispatching real HTTP — this
gives the router something to choose against and the test suite
something to verify. **Live HTTP dispatch is staged for v1.1.0 GA**
(the `_dispatch_http` method body is intentionally
`NotImplementedError` until then).

**Authentication**: reads `FIGMA_PERSONAL_ACCESS_TOKEN` from the
environment at construction, or accepts `pat="..."` directly. Once
constructed, the PAT is frozen — mid-pipeline env mutation has no
effect.

**Plan tier**: most write operations against Figma REST require an
**Enterprise plan** PAT. The capability matrix declares this with the
`supported-enterprise` level; non-Enterprise PATs will hit
`AuthorizationError` at dispatch time in v1.1.0 GA.

**Capability cliff**: REST exposes Variables, file metadata, and
Code Connect — but NOT paint/text/effect styles, NOT page creation,
NOT component creation, NOT SVG import. The router falls through to
PluginCapture for these.

```python
import figma_forge as ff

rest = ff.RestTransport(pat="figd_...your-token...")
rest.begin_session()  # raises AuthenticationError if PAT missing

# Queues a POST /v1/files/{key}/variables call
collection = rest.create_variable_collection(
    file_key="abc123", name="Colors", modes=["Light", "Dark"]
)

print(rest.pending_calls)  # in alpha; in GA the dispatch is live
```

### `McpCursorTransport` (v1.2 placeholder)

Declared in the capability matrix with `deferred-v1_2` level for all
operations. No concrete class ships in v1.1.0-alpha because Figma's
MCP server write surface is still in flux. The full Anthropic-MCP /
Cursor-MCP implementation will land in v1.2 once the resource model
stabilizes.

## Capability matrix

The `figma_forge.transport.capability_matrix` module declares, in
code, exactly which adapter implements which of the 19 transport
operations. Tests verify that each adapter's `supports()` method
matches the matrix declaration exactly — no silent drift.

```python
from figma_forge.transport.capability_matrix import (
    CAPABILITY_MATRIX, adapters_supporting, supported_operations,
)

# Which adapters can handle this op?
adapters_supporting("create_variable_collection")
# → ['plugin-capture', 'rest-v1', 'stub']

# Inverse: what operations does REST support?
supported_operations("rest-v1")
# → ['attach_code_connect', 'create_alias_reference',
#    'create_file', 'create_variable', 'create_variable_collection',
#    'get_file', 'get_variable_collection', 'list_code_connect',
#    'update_variable']

# What's the exact cell?
from figma_forge.transport.capability_matrix import capability
cell = capability("create_variable_collection", "rest-v1")
print(cell.level)  # 'supported-enterprise'
print(cell.notes)  # 'POST /v1/files/:key/variables — Enterprise only.'
```

## The router

`TransportRouter` selects, per operation, which adapter to dispatch
to. The selection rules are:

1. Iterate the preference list in order
2. Skip adapters that don't `supports(operation)`
3. Skip adapters that need credentials but don't have them
4. Return the first adapter that survives the filters
5. **Fallback** to the stub adapter as last resort; record a warning

The preference list is the operator's choice of channel ordering.
The default (when `preferences` is empty) is `["rest-v1",
"plugin-capture", "stub"]` — try the live REST first, fall back to a
TypeScript capture if REST can't handle it, fall back to stub if
neither can.

```python
import figma_forge as ff

router = ff.TransportRouter(
    adapters={
        "stub": ff.StubTransport(),
        "plugin-capture": ff.PluginCaptureTransport(locale="tr-TR"),
        "rest-v1": ff.RestTransport(pat="figd_..."),
    },
    preferences=["rest-v1", "plugin-capture", "stub"],
)

# Per-operation introspection
router.candidate_chain("create_variable_collection")
# → ['rest-v1', 'plugin-capture', 'stub']

router.candidate_chain("create_paint_style")
# → ['plugin-capture', 'stub']  (REST cannot create styles)

router.candidate_chain("publish_library")
# → ['stub']  (no live adapter supports library publishing)
```

## The high-level API: `ff.run_pipeline`

The transport layer's primary consumer is `ff.run_pipeline`, which
walks a library bundle and emits the appropriate transport operations
for each stage:

```python
import figma_forge as ff
from pathlib import Path

# Option 1: a single adapter (the simplest case)
result = ff.run_pipeline(
    Path("./dustur-figma-library"),
    transport=ff.PluginCaptureTransport(locale="tr-TR"),
    file_key="DUSTUR_FOUNDATIONS_FILE_KEY",
)

# Option 2: a router (for multi-channel strategies)
result = ff.run_pipeline(
    Path("./dustur-figma-library"),
    transport=ff.TransportRouter(
        adapters={...}, preferences=[...],
    ),
    file_key="DUSTUR_FOUNDATIONS_FILE_KEY",
)

# Option 3: None — uses the default router (REST → PluginCapture → Stub)
result = ff.run_pipeline(Path("./dustur-figma-library"))

# Inspect the outcome
print(result.is_success)              # True/False
print(result.stages_completed)        # ['FOUNDATIONS_BUILD']
print(result.operations_attempted)    # e.g. 73
print(result.operations_succeeded)    # e.g. 73
print(result.fallback_warnings)       # router fallback notes

# Capture-adapter session artifacts
sess = result.session_results["plugin-capture"]
script = sess.artifacts["typescript_script"]
Path("foundations-build.ts").write_text(script)
```

## End-to-end empirical validation (Düstur Tasarım Sistemi)

`ff.run_pipeline(Path("dustur-figma-library"),
transport=PluginCaptureTransport(locale="tr-TR"))` on the canonical
103-file Düstur bundle produces:

```
operations_succeeded: 73

Operation breakdown:
  create_variable_collection         1
  create_variable                   72  (6 families × 12 steps)

TypeScript script: 76,419 chars, 1,110 lines
  → ready to paste into Figma → Plugins → Development → Console
```

The 6 Düstur families — `tbk`, `lacivert`, `bordo`, `turkuvaz`,
`amber`, `neutral` — are each scaled across 12 steps (0..11), giving
the 72 primitive variables. The single collection (`Renkler`) holds
all of them across two modes (`Aydınlık`, `Karanlık`).

### Two color_families shapes coexist

The Düstur bundle uses **dict-keyed** `color_families` (each key is
the token-tree prefix; the value carries human-readable
documentation):

```json
{
  "color_families": {
    "tbk":      {"name": "TBK (Türk Bayrağı Kırmızısı)", ...},
    "lacivert": {"name": "Cumhuriyet Lacivert", ...}
  }
}
```

The Material 3 and IBM Carbon stubs use **list-of-dicts**:

```json
{
  "color_families": [
    {"name": "primary", "expected_steps": 10},
    {"name": "neutral", "expected_steps": 10}
  ]
}
```

The pipeline's `_color_families_for()` helper tolerates both shapes
transparently — see the docstring for the resolution logic.

## What's NOT in v1.1.0-alpha

The RFC explicitly defers these to v1.1.0 GA and later:

- **Live REST dispatch** (`RestTransport._dispatch_http`): staged but
  body is `NotImplementedError`. v1.1.0 GA will enable it.
- **Component / icon / pattern / code-connect stages** in
  `run_pipeline`: the Foundations stage is implemented end-to-end;
  the others are recognized and marked `(deferred-v1.1-GA)` in the
  result.
- **MCP transport** (`McpCursorTransport`): declared in the
  capability matrix but no concrete class ships. v1.2.
- **Concurrency awareness**: v1.1 does not detect or coordinate with
  active Figma editing sessions on the target file.
- **Backoff / rate-limit policy**: REST API has per-PAT rate limits;
  v1.1 logs them but doesn't queue or back off. `BackoffPolicy` is a
  v1.2 abstraction.

## Migration from v1.0

**Zero breaking changes.** Every v1.0 public API symbol retains its
signature and behavior:

```python
import figma_forge as ff

# All v1.0 code keeps working:
audit = ff.run_static_lint(library_dir)
diff  = ff.compare_audits(baseline, current)
trend = ff.analyze_trend(points)

# v1.1 adds new optional kwargs and new high-level APIs:
result = ff.run_pipeline(
    library_dir,
    transport=ff.PluginCaptureTransport(),  # new in v1.1
    file_key="...",                          # new in v1.1
)
```

The public API surface grew from 22 symbols (v1.0) to 32 (v1.1) —
all additive. `API_VERSION` remains `"1.0"` because the v1.x contract
is unchanged.

## Authoring an integration test

For a v1.1.0 GA contributor wanting to add a live REST integration
test against a real Figma file:

1. Create a dedicated test Figma file (Enterprise plan account)
2. Generate a scoped Personal Access Token with `files:write`
3. Export `FIGMA_PERSONAL_ACCESS_TOKEN=figd_...`
4. Add a `pytest.mark.live` marker to the test
5. Configure pytest to skip live tests by default; opt in with
   `pytest -m live`

```python
@pytest.mark.live
def test_rest_creates_real_variable_collection():
    rest = ff.RestTransport()  # picks PAT from env
    rest.begin_session()
    collection = rest.create_variable_collection(
        file_key=os.environ["TEST_FIGMA_FILE_KEY"],
        name="figma-forge-test-coll",
        modes=["m1"],
    )
    # In v1.1.0 GA, _dispatch_http actually issues the POST
    assert collection.file_key
```

In v1.1.0-alpha this test would have `pending_calls` populated but
the file wouldn't change. In v1.1.0 GA, dispatch is live.

---

## Design System Migration Recipe (worked example)

A concrete, step-by-step walkthrough of migrating *any* multi-library
design system onto the figma-forge transport layer. figma-forge is
**design-system-agnostic** — it operates on whatever DTCG-compliant
bundle you hand it. The example below uses a hypothetical 5-library
enterprise system (the kind of structure you'd find in Material 3,
IBM Carbon, the Roche Design System, or any comparably-sized system)
to make the steps concrete; substitute your own bundle's paths,
file keys, and identity strings throughout.

Assumes you have:

- A canonical DTCG export of your tokens at `tokens/<ds>.tokens.merged.json`
- The five empty Figma files created in advance for the five libraries
  (their `file_key` strings collected as env vars)
- An Enterprise Figma PAT exported as `FIGMA_PERSONAL_ACCESS_TOKEN`
  (optional — without it, the pipeline falls through to PluginCapture)
- If the system is design-system-specific (e.g. you have a dedicated
  downstream skill like `roche-design` for the Roche Design System),
  that skill provides the tokens/fonts/governance; figma-forge handles
  the Figma plumbing regardless.

### Library inventory

A representative large enterprise design system ships **five libraries**.
The exact names and counts below are illustrative — your system's
inventory will differ, but the *structure* (a Foundations file plus
Components / Patterns / Icons / Data Viz) is the common pattern:

| # | Library          | Primary content                            |
|---|------------------|---------------------------------------------|
| 1 | Foundations      | Variables (color palettes, scales); typography styles |
| 2 | Components       | Button, Input, Card, Dialog, Menu, Tabs, …  |
| 3 | Patterns         | Form, List View, Page Header, Empty State   |
| 4 | Icons            | Outlined + filled SVG icon set              |
| 5 | Data Visualization | Chart components (bar, line, scatter, …)  |

Each library is a separate Figma file with its own `file_key`. The
migration scripts each library through its own `run_pipeline`
invocation with file-key-specific configuration.

### Step 1 — Verify the bundle

```bash
# Sanity check the bundle structure
python3 scripts/publish_audit.py \
    --library-registry ds-bundle/library-registry.json \
    --static-only \
    --output-format json \
    --output ds-audit.json

# Refuse to proceed if the audit score is below STRONG (8.0)
python3 -c "
import json, sys
d = json.load(open('ds-audit.json'))
print(f'Score: {d[\"score\"]} ({d[\"band\"]})')
if d['score'] < 8.0:
    sys.exit('Refusing to migrate; raise score first')
"
```

### Step 2 — Sign the bundle (v1.0 supply-chain)

Before any Figma writes happen, freeze the source bundle's content
hash. This is the manifest that downstream consumers will verify
against later.

```bash
python3 scripts/sign.py \
    --library-dir ds-bundle/ \
    --output-dir ds-signed/ \
    --identity "ds-release@your-org.example" \
    --source-repository "https://github.com/your-org/your-design-system" \
    --source-commit "$(git rev-parse HEAD)" \
    --builder-id "ds-migration-cli/1.0" \
    --sign-mode auto \
    --verbose
```

### Step 3 — Configure the transport router

```python
import figma_forge as ff
import os

router = ff.TransportRouter(
    adapters={
        "stub": ff.StubTransport(),
        "plugin-capture": ff.PluginCaptureTransport(locale="en-US"),
        "rest-v1": ff.RestTransport(
            pat=os.environ["FIGMA_PERSONAL_ACCESS_TOKEN"],
            dry_run=False,
        ),
    },
    preferences=["rest-v1", "plugin-capture", "stub"],
)

# Preview the routing decisions before any work happens
print(router.coverage_summary([
    "create_variable_collection",   # → rest-v1 (Variables Enterprise)
    "create_paint_style",            # → plugin-capture
    "create_component",              # → plugin-capture
    "import_svg_as_component",       # → plugin-capture
    "attach_code_connect",           # → rest-v1
    "publish_library",               # → stub (manual UI action)
]))
```

### Step 4 — Run the Foundations library

```python
from pathlib import Path

foundations_file_key = os.environ["DS_FOUNDATIONS_KEY"]

result = ff.run_pipeline(
    Path("ds-bundle/foundations/"),
    transport=router,
    file_key=foundations_file_key,
    stages=["FOUNDATIONS_BUILD"],
)

assert result.is_success, result.stages_failed
print(f"Foundations: {result.operations_succeeded} ops")
print(f"Adapters used: {list(result.session_results.keys())}")

# REST queue contains the Variables writes that went over HTTP;
# inspect for retry-after / rate-limit events
rest_calls = router.adapters["rest-v1"].pending_calls
print(f"REST calls dispatched: {len(rest_calls)}")
```

A typical large-system Foundations build emits a few hundred operations:

- 1 `Colors` collection × 2 modes (Light, Dark)
- ~240 color primitives (5 palettes × ~12 steps × 4 channel modes)
- ~40 paint/text style operations

Time budget on a healthy connection: tens of seconds, dominated by
the Variables POST batch.

### Step 5 — Run the Icons library

```python
icons_file_key = os.environ["DS_ICONS_KEY"]

result = ff.run_pipeline(
    Path("ds-bundle/icons/"),
    transport=router,
    file_key=icons_file_key,
    stages=["ICONS_BUILD"],
)

# Icons is the largest stage by SVG count — typically 400-600 icons
print(f"Icons imported: {result.operations_succeeded}")

# The TS script captured for component creation:
session = result.session_results["plugin-capture::icons"]
script = session.artifacts["typescript_script"]
Path("ds-icons-build.ts").write_text(script)
print(f"Plugin script: {len(script):,} chars → ds-icons-build.ts")
```

The icon SVGs are not REST-reachable (component creation is plugin-only),
so the entire stage routes to PluginCapture. The operator pastes
`ds-icons-build.ts` into the Icons file's plugin console once.

### Step 6 — Components, Patterns, Data Viz

```python
for lib_name, file_key_env, stages in [
    ("components",  "DS_COMPONENTS_KEY",  ["COMPONENTS_BUILD"]),
    ("patterns",    "DS_PATTERNS_KEY",    ["PATTERNS_BUILD"]),
    ("data-viz",    "DS_DATAVIZ_KEY",     ["COMPONENTS_BUILD"]),
]:
    result = ff.run_pipeline(
        Path(f"ds-bundle/{lib_name}/"),
        transport=router,
        file_key=os.environ[file_key_env],
        stages=stages,
    )
    # In v1.1.0-alpha, these stages log "(deferred-v1.1-GA)";
    # in v1.1.0 GA they materialize the Components/Patterns TS.
    print(f"{lib_name}: {result.stages_completed}")
```

### Step 7 — Attach Code Connect mappings

Code Connect requires REST (or the Figma CLI). The router will pick
the REST adapter automatically when `attach_code_connect` is invoked.

```python
mappings = json.loads(Path("ds-bundle/code-connect/manifest.json").read_text())
for mapping in mappings:
    router.select("attach_code_connect").attach_code_connect(
        component_ref=ff.ComponentRef(
            file_key=os.environ["DS_COMPONENTS_KEY"],
            node_id=mapping["component_node_id"],
            name=mapping["component_name"],
        ),
        mapping=ff.CodeConnectMapping(
            framework="react",
            import_statement=mapping["import_statement"],
            code_example=mapping["code_example"],
            props_mapping=mapping["props_mapping"],
        ),
    )
```

### Step 8 — Publish the libraries (manual)

Library publishing has no API. Each library's file in Figma must be
published manually via **Assets → Library settings → Publish**. The
pipeline records this as a stub op so the audit trail captures the
human gate.

### Step 9 — Verify post-deployment

After publishing, run the verifier against the signed manifest from
Step 2 to confirm the source bundle hasn't drifted:

```bash
python3 scripts/verify.py \
    --manifest ds-signed/manifest.json \
    --provenance ds-signed/provenance.json \
    --signature ds-signed/signature.sigstore \
    --library-dir ds-bundle/ \
    --expected-identity "ds-release@your-org.example" \
    --verbose
```

Output should read `✓ All checks passed (4 checks)`. If the bundle
was modified between Step 2 (sign) and Step 9 (verify), the verifier
fails fast with the offending file path.

### Operational notes

- **Enterprise PAT lifetime**: Figma PATs don't expire by default but
  can be revoked. Many enterprise IT departments rotate PATs per-quarter. The
  RestTransport reads the PAT once at construction; mid-pipeline
  rotation requires restarting the script.
- **Rate limits**: Figma's Variables endpoint allows roughly 300
  requests/minute per file_key. A typical Foundations build sits well
  under this. RateLimitError is raised with `retry_after_seconds`
  when the threshold is hit; v1.1.0-alpha does not auto-retry —
  v1.2's `BackoffPolicy` will.
- **Parallelism**: each library has its own `file_key`, so the five
  libraries can be migrated in parallel (separate `run_pipeline`
  invocations on separate threads/processes). This brings total
  migration time from ~5 minutes serial to ~90 seconds parallel.
- **Idempotency**: rerunning the pipeline against an already-populated
  Figma file does NOT duplicate. PluginCapture emits TS that checks
  for existing nodes by name; RestTransport's `get_variable_collection`
  call in the create path identifies and reuses existing collections.
