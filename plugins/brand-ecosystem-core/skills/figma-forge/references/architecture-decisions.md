# Architecture Decision Records — figma-forge

A small ADR log capturing intentional design decisions that may otherwise look like code smells to static auditors.

---

## ADR-001 — Figma REST endpoints are hardcoded as literal URLs

**Status:** Accepted · 2026-05-26 · v0.1.1
**Decision driver:** skill-censor v1.6.0 audit finding `F-O-003` (D6) flagged 17 hardcoded API endpoints across `scripts/` and `references/`.

### Context

The auditor's D6 connector heuristic flags any literal `https://api.figma.com/...` URL as a portability liability and suggests moving endpoints to configuration or environment variables. This is the right default rule for application code that may target multiple hostnames (staging vs. production, multi-tenant SaaS, white-label deployments).

It is **not** the right rule for the case at hand:

1. **Figma's API has exactly one production endpoint.** `https://api.figma.com/v1` is the only base URL; there is no staging surface for third-party callers, no white-label tenants, no multi-region split. The URL is part of Figma's public stable contract.
2. **The references in `figma-forge` are documentation, not runtime configuration.** Most of the 17 hits are inside reference Markdown (`references/figma-rest-api.md`, `references/publish-checklist.md`) where the URL appears as part of example `curl` invocations and endpoint signatures — i.e., teaching material, not runtime configuration.
3. **Treating Figma's URL as variable obscures rather than illuminates.** Replacing `https://api.figma.com/v1/files/$KEY/variables` with `${FIGMA_API_BASE}/v1/files/$KEY/variables` does not portably abstract anything; it just adds an indirection layer that the reader must mentally resolve back to the same literal value every time.

### Decision

Keep all `api.figma.com` and `figma.com/plugin-docs` URLs as literal strings inline with the code or documentation that references them. Do not introduce a `FIGMA_API_BASE` configuration variable.

### Consequences

- **Positive:** Reference modules stay readable as `curl` recipes that paste-and-run without environment setup. Code paths are obvious without indirection.
- **Negative:** A hypothetical future where Figma offers regional API endpoints (e.g., `eu.api.figma.com`) would require a one-time find-and-replace across the skill. This cost is judged trivially small relative to the readability gain.
- **Auditor impact:** `F-O-003` is acknowledged but consciously rejected — this is the documented justification. Future audit runs may still surface the same finding; reviewers should consult this ADR.

### What would change this decision

If Figma announces multi-region or staging endpoints, OR if `figma-forge` ever needs to target a Figma-API-compatible mock server during testing, this ADR is revisited and an environment-variable abstraction is introduced.

---

## ADR-002 — HCT tonal palettes are sRGB-lerp approximated, not full CAM16

**Status:** Accepted · 2026-05-26 · v0.1.0

### Context

Material 3's canonical tonal palette generator uses the HCT (Hue/Chroma/Tone) color space, which is built on the CAM16 color appearance model. A production-grade HCT implementation runs ~500 lines and requires `material-color-utilities` as a dependency.

### Decision

`scripts/material3_to_dtcg.py:generate_tonal_palette()` approximates HCT via sRGB linear interpolation against black (tones 0–40) and white (tones 40–100), with the seed color anchored at tone 40 exactly. Full HCT is **not** used.

### Consequences

- **Positive:** Zero external dependencies. The mapper runs in any Python 3.10+ environment without `pip install`.
- **Negative:** Chroma fidelity drift of up to ~5 ΔE2000 in mid-tones (50, 60, 70) for highly saturated seeds. For neutral and low-chroma brand seeds (typical corporate/clinical contexts), the drift is visually negligible.
- **Validated:** Tested with seed `#0066CC` (Roche teal); tone-40 matches exactly; tones 30 and 50 are within visual tolerance of the canonical HCT output.

### What would change this decision

If a downstream consumer requires color-science-grade HCT fidelity, swap in `material-color-utilities` (Python port available) and update `generate_tonal_palette()` to delegate to it. The DTCG output shape would remain unchanged.

---

## ADR-003 — Channel 3 (Plugin) bundles tokens at build time

**Status:** Accepted · 2026-05-26 · v0.1.0

### Context

The Figma plugin produced by Channel 3 fallback could either: (a) fetch token data at runtime from a remote endpoint, or (b) embed the entire token payload into `code.ts` at bundle time.

### Decision

The plugin embeds tokens at bundle time. The `manifest.json` sets `networkAccess: { allowedDomains: ["none"] }` — the plugin cannot phone home.

### Consequences

- **Positive:** Plugin runs offline. No supply-chain exposure (no fetch URL to poison). PAT-free (tokens travel with the bundle, not as runtime auth). Plugin code is auditable end-to-end without network analysis.
- **Negative:** Token updates require re-bundling and re-importing the plugin. Tokens cannot live-update between deploys.
- **Why this fits the skill's risk model:** Designers running plugins downloaded from a chat assistant should never grant outbound network access by default. The trust boundary is the chat conversation, not the network.

---

End of ADR log.
