# brand-ecosystem-core

The strategic, verbal and visual layers of the **Brand Ecosystem v1.0**, packaged
as one Claude Code plugin. It bundles ten skills under a single `skills/`
directory and composes with the separate **brand-voice** plugin for the voice &
tone layer.

## What's inside

| Skill | Role |
|---|---|
| `brand-audit` | Diagnostic audit (rebrand / refresh / M&A / post-launch) |
| `brand-platform` | Strategic bedrock: vision, mission, values, personality, persona, positioning, promise |
| `brand-story` | SB7 BrandScript + three-layer problem analysis |
| `brand-maker` | Verbal identity / naming (SMILE+M, v2.1 two-source domain + diversity gate + naive-perception + pharma brand collision) |
| `brand-maker-ecosystem` | Naming companion: platform/story-aware bias, sector + luxury constraints |
| `brand-verify` | Live-verification discipline: multi-source domain/TM/INN/handle via brand-verify-mcp, provenance-stamped, with offline script fallback |
| `brand-visual` | 2026 visual identity system (routes, color, type, tokens) |
| `brand-visual-ecosystem` | Visual companion: touchpoint atmosphere, corporate signature, sensory layer |
| `figma-forge` | Design-system → Figma library (variables, styles, components, Code Connect) |
| `brand-touchpoint` | Per-surface application specs (stationery → packaging → retail → digital) |
| `brand-launch` | Internal-first launch, brand center, guidelines, IP/handle checklist, KPI dashboard |

A pipeline command, `/brand-ecosystem-core:pipeline`, runs the canonical
build order end to end and hands off to the voice layer. Each skill is also
invocable on its own (e.g. `brand-ecosystem-core:brand-platform`).

> **Supersedes the standalone skills.** These ten skills also exist as
> standalone library skills. Once this plugin is installed they load as plugin
> components (`brand-ecosystem-core:<name>`); to avoid double-listing, remove or
> disable the standalone copies under your skills directory. The cross-skill
> handoff references (`../brand-audit/references/…`) resolve inside the plugin
> because the skills remain siblings under `skills/`.

## Verification layer (v2.1)

Following an independent brand-expert audit, the naming pipeline is hardened by a
three-primitive verification layer (see `ARCHITECTURE.md`):

- **Hooks (`hooks/`) — guarantees.** `SessionStart` injects the no-fabrication
  verification doctrine; `UserPromptSubmit` routes regulated-sector and
  "final/lock" intent; `Stop` runs a provenance self-check that blocks a finish
  presenting a domain/mark as *available/clean* without a status label.
- **Subagents (`agents/`) — isolated critique.** `diversity-auditor` (blocks
  single-morpheme-family shortlists), `naive-reader` (perceived vs intended
  meaning), `brand-skeptic` (red-team the shortlist), `trademark-examiner`
  (opposition + brand collision), `etymology-verifier` (are claimed roots real
  *and* perceived).
- **MCP fleet — live data.** `brand-verify-mcp` (multi-source domain + TM + INN +
  handle, provenance-stamped) and the P1/P2 connectors are user-bound Cloudflare
  connectors registered in `mcp.optional.json`; the `brand-verify` skill teaches
  their use, and `brand-maker`'s scripts are the offline fallback.

## Composition with brand-voice

The voice & tone identity is owned by the **brand-voice** plugin, not this one.
The pipeline hands the platform/story off to `brand-voice:guideline-generation`
(which includes the mandatory Turkish sen/siz/biz register decision) and uses
`brand-voice:brand-voice-enforcement` for launch-surface copy. Install both
from the same `cureonics` marketplace.

## Install

```bash
claude plugin marketplace add https://<gitea-host>/<owner>/cureonics-marketplace.git
claude plugin install brand-ecosystem-core@cureonics
# optional, for the voice layer:
claude plugin install brand-voice@cureonics
```

## Optional connectors

Every bundled skill is Claude.ai-native and declares `mcp_servers_required: []`,
so no connector is needed. `mcp.optional.json` documents three enhancers you can
opt into: **Figma** (figma-forge, brand-visual), **GoDaddy** (brand-maker domain
checks), **Exa** (brand-audit competitive research). To activate, merge the
chosen entries into a plugin `.mcp.json` or connect them in Claude.ai.

## Output rendering

This ecosystem produces strategy and specification text. It defers all
HTML/print/deck rendering to `carbon-html-report` (A4 brand book), `carbon-pptx`
(deck) and `docx`. For any regulated-sector brand (pharma, health, finance,
legal), route promotional-claim review to `promo-censor` / `lex-sanitas`.

## Manifests (SMP dual-compatibility)

Each skill keeps a canonical SMP `skill-manifest.yaml`. The seven brand-* skills
carry manifests migrated to canonical list-form by `smp migrate`; brand-maker,
brand-visual and figma-forge ship their existing canonical manifests. Built over
the full ecosystem (these ten + the three brand-voice skills) the composition
graph resolves **180/180 edges with zero dangling**.

## Validate

```bash
claude plugin validate ./plugins/brand-ecosystem-core --strict
```

## License

Internal skill assets (`LicenseRef-Internal`). See LICENSE.
