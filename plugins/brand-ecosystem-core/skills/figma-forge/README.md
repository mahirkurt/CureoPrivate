# figma-forge

> SMP v1.0 operationalization layer between design system specifications and production-ready Figma libraries.

**Version:** 0.1.0
**License:** Internal
**Position in skill ecosystem:** Downstream of `brand-platform` / `brand-visual` / `roche-design` (DS spec authors). Upstream of `frontend-design` (consumes published Figma libraries).

---

## What this skill does

Given a design system specification — Carbon v11, Material 3, Tailwind, W3C DTCG token JSON, or Style Dictionary export — `figma-forge` produces a complete, publish-ready Figma library ecosystem comprising:

- **Variables** organised into typed collections (Color, Dimension, Typography, Misc).
- **Modes** (Light/Dark or any brand-defined set, including Carbon's 4 themes).
- **Paint, Text, and Effect styles** bound to variables.
- **Components** with variant axes (size, state, hierarchy) and instance-swap slots.
- **Code Connect mappings** linking Figma components to React or Web Components code.
- **Multi-file architecture** — typically Foundations / Components / Patterns / Icons — with proper publish ordering.
- **Audit reports** covering 19 publish-readiness gates.

The skill operates across three transport channels and falls back automatically when a higher-priority channel is unavailable.

## Modes

| # | Mode | Purpose |
|---|------|---------|
| 1 | `SCAFFOLD` | Create the empty multi-file Figma library skeleton (cover pages, navigation, sections). |
| 2 | `TOKENS_IMPORT` | Read tokens from DTCG / Style Dictionary / built-in mappers; emit Figma Variables. |
| 3 | `FOUNDATIONS_BUILD` | Build paint/text/effect styles bound to variables; populate the Foundations file. |
| 4 | `COMPONENTS_BUILD` | Generate component sets with variant axes; populate the Components file. |
| 5 | `MIGRATE` | Take an existing Figma file and migrate it to a new token system; produce a delta report. |
| 6 | `CODE_CONNECT` | Generate Code Connect `.figma.tsx` (React) or `.figma.ts` (WC) stub files per component. |
| 7 | `PUBLISH_AUDIT` | Run the 19-gate publish readiness check against a library file. |

See `SKILL.md` for the full protocol — preconditions, workflow steps, and postconditions per mode.

## Channels

| Channel | Mechanism | Default for |
|---------|-----------|-------------|
| 1 — MCP | Figma MCP tools (`use_figma`, `create_new_file`, `get_design_context`, `get_variable_defs`, `search_design_system`, `add_code_connect_map`, `send_code_connect_mappings`) | Any Figma plan. Default when the MCP is connected. |
| 2 — REST | Figma REST API with PAT, including the Variables API (Enterprise only for write) | Enterprise plans, large bulk imports, CI flows. |
| 3 — Plugin | Generated TypeScript Figma plugin written to user's local filesystem; user imports via Plugins menu | Non-Enterprise plans, full deterministic control, offline use. |

## Built-in mappers

| Mapper | Output | Smoke-test result |
|--------|--------|-------------------|
| `scripts/carbon_to_dtcg.py` | Carbon v11 all-theme DTCG | 158 tokens · 92 primitive colors · 27 semantic colors · 16 typography · 13 spacing |
| `scripts/material3_to_dtcg.py` | M3 baseline or seeded DTCG | 15-stop tonal palette · 33 semantic roles · 15 type ramp tokens |
| `scripts/tailwind_to_dtcg.py` | Tailwind v3 default DTCG | 16 hues × 11 stops + 36 spacing + 13 type scale |
| `scripts/style_dict_to_dtcg.py` | Generic Style Dictionary → DTCG | Type-inferred conversion |
| `scripts/dtcg_to_variables.py` | DTCG → Figma Variables REST payload | Topological alias resolution + multi-mode detection |
| `scripts/publish_audit.py` | 19-gate REST-based audit | 4 gates implemented in v0.1.0; remainder stubbed |

## Quick start

### Scenario 1 — Forge a Carbon library

```bash
# Step 1: emit DTCG from Carbon canonical tables
python3 scripts/carbon_to_dtcg.py --all-themes --output build/carbon.dtcg.json

# Step 2: convert DTCG to Figma Variables REST payload
python3 scripts/dtcg_to_variables.py \
    --input build/carbon.dtcg.json \
    --output build/carbon-variables-payload.json

# Step 3: POST the payload (Enterprise plans only)
curl -X POST "https://api.figma.com/v1/files/$FILE_KEY/variables" \
    -H "X-Figma-Token: $FIGMA_PAT" \
    -H "Content-Type: application/json" \
    -d @build/carbon-variables-payload.json
```

### Scenario 2 — Forge a Material 3 library with custom brand seed

```bash
python3 scripts/material3_to_dtcg.py \
    --seed "#0066CC" \
    --font-family "Roche Sans" \
    --output build/roche-m3.dtcg.json
```

The resulting DTCG contains a 15-stop tonal palette generated from your seed, neutrals from the M3 baseline (unchanged), and the type ramp anchored to your specified font family.

### Scenario 3 — Forge a custom DTCG library (non-Enterprise)

When Channel 2 is not available, the skill writes a Figma plugin bundle to your workspace:

```
figma-forge-plugin/
├── manifest.json
├── code.ts          ← embedded DTCG payload + variable creation logic
└── ui.html
```

You import the plugin via **Figma desktop app → Plugins → Development → Import plugin from manifest** and run it. The plugin populates Variables, paint styles, text styles, and effect styles into the current file.

### Scenario 4 — Audit before publishing

```bash
python3 scripts/publish_audit.py \
    --file-key "$FILE_KEY" \
    --figma-pat "$FIGMA_PAT" \
    --output build/publish-audit.md \
    --strict
```

The audit produces a Markdown report enumerating pass/fail status per gate, with remediation guidance for each failure.

## File layout

```
figma-forge/
├── SKILL.md                     # Protocol authority
├── skill-manifest.yaml          # SMP v1.0 manifest
├── README.md                    # This file
├── references/                  # 14 reference modules
│   ├── figma-mcp-cookbook.md
│   ├── figma-rest-api.md
│   ├── figma-plugin-fallback.md
│   ├── w3c-dtcg-tokens.md
│   ├── style-dictionary.md
│   ├── carbon-mapping.md
│   ├── material3-mapping.md
│   ├── tailwind-mapping.md
│   ├── library-architecture.md
│   ├── component-spec-templates.md
│   ├── code-connect-patterns.md
│   ├── naming-conventions.md
│   └── publish-checklist.md
├── templates/
│   ├── dtcg-tokens.template.json
│   ├── figma-plugin/
│   │   ├── manifest.json
│   │   ├── code.ts
│   │   └── ui.html
│   └── code-connect/
│       ├── react.figma.tsx.template
│       └── web-components.figma.ts.template
├── scripts/                     # Mappers + audit + converters
│   ├── dtcg_to_variables.py
│   ├── style_dict_to_dtcg.py
│   ├── carbon_to_dtcg.py
│   ├── material3_to_dtcg.py
│   ├── tailwind_to_dtcg.py
│   └── publish_audit.py
├── evals/
│   └── evals.json               # 3-test-case evaluation suite
└── tests/
    └── run_tests.py             # 8-gate skill self-validation runner
```

## Composability

`figma-forge` is SMP v1.0 compliant and composes with:

- **Upstream:** `brand-platform`, `brand-visual`, `brand-story`, `roche-design`
- **Downstream:** `frontend-design`, `brand-touchpoint`, `brand-launch`, `carbon-html-report` (for documenting the published DS)

Example pipeline: `brand-visual` → DTCG → `figma-forge` → published Figma library → `frontend-design` consumes via `get_design_context`.

## Quality gates

The skill itself ships with 8 self-validation gates (run via `tests/run_tests.py`):

| Gate | Check |
|------|-------|
| G1-INT | File integrity (all required files present) |
| G2-CONT | Content validation (modes documented, DTCG keywords present) |
| G3-TPL | Template validation (JSON parses, plugin code API references present) |
| G4-CONS | Cross-file consistency (modes referenced across references/) |
| G5-PROC | Procedural completeness (Precondition / Workflow / Postcondition per mode) |
| G6-ANTI | Anti-pattern detection (no hard-coded file_keys or PAT leaks) |
| G7-DESC | Description ≤1024 chars (SMP v1.0 hard limit) |
| G8-MAPPER | Built-in mapper coverage (Carbon + M3 + Tailwind present + Carbon smoke test) |

Additionally, library output is audited against the 19 publish-readiness gates documented in `references/publish-checklist.md`.

## Honest limitations

1. **Variables API write is Enterprise-only.** Channel 2 cannot create variables on non-Enterprise plans. The skill automatically falls back to Channel 3 (Plugin).
2. **HCT palette generation is sRGB-lerp approximated** in `material3_to_dtcg.py`. For pixel-perfect HCT/CAM16 fidelity, integrate Google's `material-color-utilities` library; for most brand seeds, the approximation is visually acceptable (validated against M3 baseline at tone 40).
3. **256-variant practical Figma limit.** The skill warns at 64 variants per component; Figma editor performance degrades past 256 combinations.
4. **PAT handling.** Tokens are accepted via `FIGMA_PAT` env var or `--figma-pat` flag only. The skill never persists them and never logs them. The G6-ANTI gate scans for accidental PAT leakage in skill files.
5. **Channel 3 plugins use `networkAccess: none`.** All token data is bundled at build time. Plugins cannot phone home; this is by design.
6. **Audit script v0.1.0** implements 4 of 19 gates (G1, G2, G5, G16). The remaining 15 are stubbed and will be implemented in v0.2.0 based on user feedback.

## Reference

Authoritative external sources:

- **W3C DTCG:** [tr.designtokens.org/format](https://tr.designtokens.org/format/) (working draft)
- **Figma Variables API:** [figma.com/developers/api](https://www.figma.com/developers/api#variables)
- **Figma Plugin API:** [figma.com/plugin-docs](https://www.figma.com/plugin-docs/)
- **Code Connect:** [github.com/figma/code-connect](https://github.com/figma/code-connect)
- **IBM Carbon v11:** [carbondesignsystem.com](https://carbondesignsystem.com/)
- **Material 3:** [m3.material.io](https://m3.material.io/)
- **Tailwind:** [tailwindcss.com](https://tailwindcss.com/docs/customizing-colors)
- **Amazon Style Dictionary:** [amzn.github.io/style-dictionary](https://amzn.github.io/style-dictionary/)

---

End of README.
