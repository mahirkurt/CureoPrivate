# Figma MCP Cookbook (Channel 1)

The Figma MCP server exposes a set of agentic tools that let `figma-forge` create, edit, and inspect Figma files without leaving the Claude environment. This reference documents every tool used by `figma-forge`, with input shape, output shape, typical invocation patterns, and known limitations.

## Table of contents

1. Tool inventory
2. File creation flow
3. Variant-aware component flow
4. Auto-layout patterns
5. Token binding pattern
6. Code Connect tools
7. Inspection / audit tools
8. Known limitations and Channel 3 handoffs

---

## 1. Tool inventory

| Tool | Purpose | Used in mode |
|---|---|---|
| `Figma:create_new_file` | Create empty Figma file | `SCAFFOLD` |
| `Figma:use_figma` | Create, edit, or sync nodes/components/frames | `FOUNDATIONS_BUILD`, `COMPONENTS_BUILD`, `MIGRATE` |
| `Figma:upload_assets` | Upload images (icons, photos, illustrations) | `COMPONENTS_BUILD` (icon imports), `FOUNDATIONS_BUILD` (logo) |
| `Figma:get_design_context` | Read a node's structure as design context | `PUBLISH_AUDIT`, `MIGRATE` |
| `Figma:get_metadata` | Read file-level metadata | `PUBLISH_AUDIT`, `SCAFFOLD` |
| `Figma:get_variable_defs` | Enumerate variables in a node | `PUBLISH_AUDIT`, `TOKENS_IMPORT` (verification) |
| `Figma:get_libraries` | Discover team libraries linked to a file | `SCAFFOLD` (existing-team detection) |
| `Figma:search_design_system` | Search for components/styles by query | `MIGRATE`, `CODE_CONNECT` |
| `Figma:get_screenshot` | Render a node to PNG | `PUBLISH_AUDIT` (visual verification) |
| `Figma:add_code_connect_map` | Map one node to one code source | `CODE_CONNECT` |
| `Figma:get_code_connect_map` | Read existing node↔code map | `CODE_CONNECT` (refresh) |
| `Figma:send_code_connect_mappings` | Bulk-save many node↔code mappings | `CODE_CONNECT` |
| `Figma:get_code_connect_suggestions` | AI-suggested node↔code mappings | `CODE_CONNECT` (interactive) |
| `Figma:whoami` | Return authenticated user info | Diagnostic (rare) |

---

## 2. File creation flow (`SCAFFOLD` mode)

```
For each layer in [Foundations, Components, Patterns, Icons]:
    response = Figma:create_new_file(
        name = f"{ds_name} — {layer}",
        team_id = <optional, if user supplied>,
        folder_id = <optional, if user supplied>
    )
    record file_key + url in library_registry.json
```

`create_new_file` returns the new file's `file_key` and editor URL. Store these immediately — without the file_key you cannot later target the file for variable writes via REST or for `use_figma` operations.

**Note:** if the user does not specify a team, the file is created in the authenticated user's personal drafts. This is fine for prototyping but NOT for production libraries — only team files can be published as libraries. Always confirm team scope with the user during `SCAFFOLD`.

---

## 3. Variant-aware component flow (`COMPONENTS_BUILD` mode)

Variants in Figma are technically multiple component instances grouped under a common component set. `use_figma` can construct them, but you must specify the variant axes precisely.

**Pattern:** describe to `use_figma` what to build with the full axis matrix.

```
Figma:use_figma(
    file_key = <Components file_key>,
    prompt = """
    Create a component set named 'Button' on page 'Buttons'.

    Variant axes:
      - size: sm, md, lg
      - state: default, hover, pressed, disabled, focus
      - variant: primary, secondary, tertiary, ghost
      - iconLeading: true, false
      - iconTrailing: true, false

    Use auto-layout horizontal with padding 8/16/24 for sm/md/lg.
    Bind background to variable 'color/button/{variant}/{state}/bg'.
    Bind text color to variable 'color/button/{variant}/{state}/text'.
    Bind corner radius to variable 'radius/button'.
    Bind text to text style 'typography/body/medium'.

    Each variant should have a description matching its purpose.
    Add keywords: button, action, cta, primary, click.
    """
)
```

The skill template (`COMPONENTS_BUILD`) constructs prompts like this from the component spec JSON. See `references/component-spec-templates.md` for the spec format.

**Failure handling:** if `use_figma` reports it could not create some variants (typically: too many axes × values), the skill falls through to Channel 3 (plugin) and uses the Plugin API's full variant API which has no such limitation.

---

## 4. Auto-layout patterns

Every component should use auto-layout to be truly responsive in consumer files. The skill's `use_figma` prompts always specify:

- Layout direction (horizontal / vertical)
- Padding (use variables: `space/component-padding-{size}`)
- Item spacing (use variables: `space/gap-{size}`)
- Alignment (e.g., center-cross-axis, fill-container, hug-contents)
- Resizing behavior per child

For complex layouts (cards, modals), nested auto-layout frames are used. The skill's prompt template documents the parent→child resizing intent for each layer.

---

## 5. Token binding pattern

The single most important rule when using `use_figma`: **every paint, every typography setting, every spacing value should bind to a variable or style — never to a literal value.**

If `use_figma` cannot bind to a variable (because the variable doesn't exist yet, or because of a current MCP limitation), the skill:

1. Logs the binding failure in the run report.
2. Creates the construct with a literal placeholder value.
3. Notes the binding requirement so it can be fixed in a `PUBLISH_AUDIT` follow-up or via Channel 3.

---

## 6. Code Connect tools

`Figma:get_code_connect_suggestions` is the killer feature: it can propose mappings from Figma nodes to candidates in a repo when both are accessible. Workflow:

```
1. Figma:get_code_connect_suggestions(
       file_key = <Components file_key>,
       repo_path = <target_repo_path>
   )
   → list of suggested mappings

2. Review suggestions; reject/edit as needed.

3. Figma:send_code_connect_mappings(
       file_key = <Components file_key>,
       mappings = <validated list>
   )
   → confirmation
```

For systems where AI suggestions are not available or are insufficient, use `Figma:add_code_connect_map` per-node with manual source paths. Stub templates in `templates/code-connect/`.

---

## 7. Inspection / audit tools

`PUBLISH_AUDIT` mode uses Channel 1 read tools to enumerate file contents and check gate compliance:

- `Figma:get_metadata` → file-level checks (name, last-modified, page count)
- `Figma:get_design_context` → per-page node tree for orphan-style and unused-variant detection
- `Figma:get_variable_defs` → enumerate all variables for alias resolution checks
- `Figma:search_design_system` → check naming convention compliance via search

Read tools do not require Enterprise plan. They are also rate-limited; the audit script batches calls and respects 429s.

---

## 8. Known limitations and Channel 3 handoffs

`use_figma` is powerful but has real edge cases. As of the current Figma MCP version:

| Limitation | Handoff strategy |
|---|---|
| Cannot create Variables (only read) | Channel 3 plugin (Plugin API: `figma.variables.createVariable`) |
| Variant explosion >256 unreliable | Channel 3 plugin (`figma.createComponentSet` direct API) |
| Complex instance-swap properties | Channel 3 plugin |
| Effect styles with multi-shadow | Channel 3 plugin |
| Library publish operation | REST Channel 2 (`POST /v1/files/:file_key/library_publish`) |

When a handoff is needed, the skill produces a Channel 3 plugin bundle pre-loaded with the failed work, and walks the user through the import + run cycle.

---

## End of reference

For Channel 2 REST API: see `figma-rest-api.md`.
For Channel 3 Plugin: see `figma-plugin-fallback.md`.
