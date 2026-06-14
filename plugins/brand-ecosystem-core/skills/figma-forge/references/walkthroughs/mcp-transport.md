# MCP Transport — Operator Walkthrough

> `McpCursorTransport` · figma-forge v1.2.0-alpha.1

This walkthrough explains how figma-forge drives a Figma library build
through the **Model Context Protocol (MCP)** channel, what the emitted
"MCP tool-call plan" is, and how an MCP-capable agent (Claude, Cursor,
or any MCP host) executes that plan against a live Figma file.

It assumes you have read `transport-layer.md` for the general
transport model (adapters, the router, `run_pipeline`).

---

## 1. The mental model: figma-forge emits a plan, an agent executes it

figma-forge is a **library / CLI**. It does not hold an MCP client
connection and cannot call Figma MCP tools itself — only an
MCP-capable agent can. So the MCP transport works exactly like the
plugin transport, one level removed:

```
PluginCaptureTransport  →  emits a TypeScript script
                        →  operator pastes it into Figma's plugin console
                        →  the plugin runtime executes it

McpCursorTransport      →  emits an MCP tool-call plan (JSON)
                        →  an MCP-capable agent reads the plan
                        →  the agent invokes the Figma MCP tools
```

In both cases figma-forge produces a **deterministic, reviewable
artifact** that something else executes. You can inspect, diff, sign,
and archive the plan before any change reaches Figma. This is the same
"capture, review, then apply" discipline that the plugin channel
established in v0.3.

---

## 2. Two dispatch mechanisms — `native` and `use_figma_nl`

The Figma MCP server exposes a mix of granular, dedicated tools and
one high-level natural-language tool (`Figma:use_figma`). figma-forge
maps each of its operations to one of two mechanisms, and records the
mechanism on every step of the plan:

### `native` — deterministic, dedicated MCP tool (5 operations)

| figma-forge operation       | Figma MCP tool                   |
|-----------------------------|----------------------------------|
| `create_file`               | `Figma:create_new_file`          |
| `get_file`                  | `Figma:get_metadata`             |
| `get_variable_collection`   | `Figma:get_variable_defs`        |
| `attach_code_connect`       | `Figma:send_code_connect_mappings` |
| `list_code_connect`         | `Figma:get_code_connect_map`     |

These are deterministic: the arguments map directly onto the tool's
parameters, and the agent calls the tool verbatim.

### `use_figma_nl` — natural-language via `Figma:use_figma` (13 operations)

Figma's MCP server does not (yet) expose granular write tools for
Variables, styles, pages, components, component sets, or SVG import.
For these, figma-forge emits a **well-structured natural-language
instruction** for `Figma:use_figma` ("Create, edit, generate, or sync
any design in Figma"). Covered operations: `create_variable_collection`,
`create_variable`, `update_variable`, `create_alias_reference`,
`create_paint_style`, `create_text_style`, `create_effect_style`,
`create_page`, `create_component`, `create_component_set`,
`set_component_property`, `import_svg_as_component`,
`update_component_description`.

These are **best-effort and non-deterministic** — the agent and
Figma's generative layer interpret the instruction. The plan carries
both a structured `arguments` object (so the agent can cross-check or
render its own phrasing) and a ready-to-use `instruction` string.

The capability matrix records this split as `supported` (native) vs
`supported-nl` (natural-language). `publish_library` is `unsupported`
— library publish is a manual Figma UI action with no MCP tool.

---

## 3. Building a plan

```python
import figma_forge as ff
from pathlib import Path

# Build a router with McpCursor. It's opt-in — NOT in the default
# router — because it assumes an MCP-capable agent will execute the
# plan. In a non-agent environment the plan would be emitted but
# never run.
mcp = ff.McpCursorTransport(locale="tr-TR")   # or "en-US"
router = ff.TransportRouter(
    adapters={"stub": ff.StubTransport(), "mcp-cursor": mcp},
    preferences=["mcp-cursor", "stub"],
)

result = ff.run_pipeline(
    Path("./my-design-system-bundle"),
    transport=router,
    file_key="FIGMA_FILE_KEY",
    # default stages: Foundations, Icons, Components, Patterns, Code Connect
)

print(result.operations_succeeded, "operations planned")

# The plan itself:
plan_json = mcp.render_mcp_plan()
Path("mcp-plan.json").write_text(plan_json, encoding="utf-8")
```

### The plan envelope

```json
{
  "plan_format_version": "1.0",
  "adapter": "mcp-cursor",
  "locale": "tr-TR",
  "generated_at": "2026-05-28T...Z",
  "step_count": 189,
  "native_steps": 17,
  "use_figma_nl_steps": 172,
  "steps": [
    {
      "step": 1,
      "operation": "create_variable_collection",
      "mcp_tool": "Figma:use_figma",
      "mechanism": "use_figma_nl",
      "arguments": {
        "file_key": "FIGMA_FILE_KEY",
        "name": "Renkler",
        "modes": ["Aydınlık", "Karanlık"],
        "collection_id": "vc_xxxxxxxx"
      },
      "instruction": "FIGMA_FILE_KEY dosyasında “Renkler” adında bir değişken koleksiyonu oluştur; modlar: Aydınlık, Karanlık."
    },
    {
      "step": 173,
      "operation": "attach_code_connect",
      "mcp_tool": "Figma:send_code_connect_mappings",
      "mechanism": "native",
      "arguments": {
        "node_id": "...",
        "component_name": "Button",
        "framework": "react",
        "import_statement": "import { Button } from '@dustur/react';",
        "code_example": "<Button .../>",
        "props_mapping": { ... },
        "code_connect_id": "cc_xxxxxxxx"
      }
    }
  ]
}
```

Note the native step (Code Connect) carries no `instruction` — the
agent calls the MCP tool directly with `arguments`. The natural-
language step carries an `instruction` the agent can pass to
`Figma:use_figma`.

---

## 4. Executing the plan (the agent side)

An MCP-capable agent loads `mcp-plan.json` and walks `steps` in order.
For each step:

```
if step.mechanism == "native":
    call MCP tool step.mcp_tool with step.arguments
else:  # use_figma_nl
    call Figma:use_figma with the prompt step.instruction
        (cross-checking against step.arguments)
```

Because the plan is ordered and each step is self-describing, the
agent needs no figma-forge runtime — only the Figma MCP connection.
The agent is responsible for:

- **Ordering** — steps are emitted in dependency order (collections
  before variables, pages before components, components before their
  Code Connect mappings).
- **Reconciliation** — `native` read steps (`get_file`,
  `get_variable_collection`, `list_code_connect`) return live data the
  agent can use to skip already-present entities (idempotency).
- **Verification** — after `use_figma_nl` steps, the agent should
  verify the generated result matches the structured `arguments`
  (e.g. confirm the variable count, the variant matrix size).

---

## 5. Why McpCursor is opt-in

`McpCursorTransport.authentication_required()` reports
`credential_kind="ambient-mcp"` and `needs_credentials=False`: it
needs no PAT because the agent's MCP host owns the Figma connection.
That makes McpCursor a tempting default — but it is **deliberately
excluded from `_default_router`**:

- In a plain CLI or CI environment with no agent, McpCursor would
  silently emit a plan that nothing executes — a confusing no-op.
- The default chain (`REST → PluginCapture → Stub`) always produces
  an artifact someone can act on without an agent (a real API call,
  a paste-able script, or a logged stub).

To use MCP, opt in explicitly. A useful pattern is to place McpCursor
**after** REST so it becomes the credential-free fallback for Code
Connect when no Enterprise PAT is present:

```python
router = ff.TransportRouter(
    adapters={
        "stub": ff.StubTransport(),
        "rest-v1": ff.RestTransport(),          # uses PAT if present
        "mcp-cursor": ff.McpCursorTransport(),  # ambient agent context
    },
    preferences=["rest-v1", "mcp-cursor", "stub"],
)
```

Here, when `FIGMA_PERSONAL_ACCESS_TOKEN` is set, REST handles Variables
and Code Connect directly; when it isn't, REST is skipped for
credentialed operations and McpCursor picks up Code Connect natively
via `Figma:send_code_connect_mappings`, while Variables/components fall
to `use_figma_nl`.

---

## 6. Worked example — full design-system build via MCP

A complete five-stage build of a representative bundle (the Düstur
validation fixture) through McpCursor emits a **189-step plan**:

| Stage              | Steps | Mechanism breakdown                    |
|--------------------|-------|----------------------------------------|
| FOUNDATIONS_BUILD  | 73    | 1 collection + 72 variables — all `use_figma_nl` |
| ICONS_BUILD        | 29    | 3 pages + 26 SVG imports — all `use_figma_nl` |
| COMPONENTS_BUILD   | 35    | 1 page + 17 sets + 17 descriptions — all `use_figma_nl` |
| PATTERNS_BUILD     | 35    | 1 page + 17 patterns + 17 descriptions — all `use_figma_nl` |
| CODE_CONNECT       | 17    | 17 mappings — all **`native`** (`send_code_connect_mappings`) |
| **Total**          | **189** | **17 native + 172 use_figma_nl** |

The 17 Code Connect steps are the only native ones because Code
Connect is the single write surface Figma exposes as a granular MCP
tool. Everything else routes through `Figma:use_figma`. As Figma's MCP
server grows granular write tools, figma-forge will promote those
operations from `supported-nl` to `supported` (native) with no change
to the public API or the plan format.

---

## 7. Limitations & roadmap

- **Non-determinism of `use_figma_nl`**: most of a build's steps depend
  on `Figma:use_figma` interpreting a natural-language instruction.
  This is inherently less reliable than REST or the plugin channel for
  bulk Variable creation. For large token sets, the REST channel
  (Enterprise) or the plugin channel remains the deterministic choice;
  MCP is most valuable for Code Connect and for agent-driven,
  interactive building.
- **No live execution in this skill's sandbox**: McpCursor emits the
  plan; executing it requires an MCP host with a Figma connection. The
  plan format is verified end-to-end by tests, but a real round-trip
  against `Figma:use_figma` happens in the agent's environment.
- **Nested-instance composition (shipped v1.2.0-alpha.2)**: patterns
  now place real nested instances of their `uses_components` via
  `place_instance` / `set_instance_property`. Over MCP these are
  `use_figma_nl` steps; over the plugin channel they emit real
  `createInstance()` + `appendChild` TypeScript. The Düstur build's
  MCP plan grew from 189 to 265 steps accordingly.
- **Rate-limit backoff (shipped v1.2.0-alpha.2)**: `BackoffPolicy`
  wires 429 `Retry-After`-honoring exponential retry into
  `RestTransport`. McpCursor itself does not retry (the agent's MCP
  host manages rate limits), but a mixed router (REST + MCP) benefits
  from REST-side backoff.
- **Roadmap (v1.2.0+)**: concurrency detection (warn on active editor),
  and promotion of `use_figma_nl` operations to `native` as Figma's MCP
  write surface matures.
