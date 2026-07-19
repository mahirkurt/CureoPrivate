---
name: brand-verify
description: >
  Live-verification discipline for brand naming — teaches how to confirm a name's
  domain availability, trademark clearance, INN/USAN status, and social-handle
  availability using the brand-verify-mcp connector (multi-source, provenance-
  stamped), with a graceful offline fallback to brand-maker's local scripts.
  Enforces the v2.1 no-fabrication contract: no domain called "available" without
  two agreeing live sources; no mark called "clean" without provenance; every
  claim labelled confirmed | provisional | unverified. USE for: domain
  verification, "is this available", trademark check, marka doğrulama, "bu isim
  müsait mi", ".com kontrol", handle availability, INN check, verification of a
  naming shortlist before it is locked. Companion to brand-maker.
---

# brand-verify — Live Verification Discipline for Brand Naming

`brand-maker` generates and filters names; **brand-verify** confirms them against
the live world and stamps every claim with provenance. It exists because the 2026
expert audit found the pipeline reporting registered domains as "available" and
pharma marks as "clean" from a single weak signal. This skill makes verification
a **sourced, labelled, two-source** step — never an optimistic guess.

## The one rule

> **No positive claim without provenance and a status label.**
> - **Domain** is "MÜSAİT" only when **two agreeing live sources** confirm it
>   free (GoDaddy MCP, or RDAP + WHOIS). One source = `provisional`. No source =
>   `unverified`. Never a bare "available".
> - **Trademark / brand** is never "clean/temiz" from one search. Every result
>   carries the sources checked and, if no live registry was queried, the caveat
>   *"resmî çok-yargı-bölgeli TM araştırması gerekli — ön-tarama yeterli değil."*
> - Every claim is labelled **confirmed | provisional | unverified** with a
>   timestamp.

## Primary path — brand-verify-mcp (user-bound connector)

When the `brand-verify-mcp` connector is connected (a user-bound Cloudflare Worker
in the Cureonics fleet — see the plugin-root `ARCHITECTURE.md`), prefer it. It is
one MCP with several tools, each returning `{value, source, checked_at,
status: confirmed|provisional}`:

| Tool | Returns |
|---|---|
| `domain_multi` | RDAP + WHOIS + registrar for a name across TLDs |
| `trademark_multi` | TÜRKPATENT + EUIPO eSearch + WIPO Global Brand DB + USPTO |
| `inn_usan_live` | live WHO INN / USAN stem status |
| `social_handles` | X / Instagram / LinkedIn / YouTube handle availability |
| `llm_namespace` | LLM-namespace collision probe |

Interpreting results: require **two agreeing sources** before writing "available";
carry the `source` and `checked_at` fields into the report; if a tool returns
`provisional` or errors, downgrade the wording — do not upgrade it to "available".

## Fallback path — brand-maker local scripts (offline-safe)

If `brand-verify-mcp` (and GoDaddy MCP) are not connected, use the local scripts.
They are genuine live verifiers where the network allows, and degrade honestly
when it does not:

```bash
# Domain — RDAP (primary) + WHOIS (secondary). Offline → 'unverified', never 'available'.
python3 "${CLAUDE_PLUGIN_ROOT}/skills/brand-maker/scripts/domain_recon.py" NAME --json
python3 "${CLAUDE_PLUGIN_ROOT}/skills/brand-maker/scripts/domain_recon.py" NAME --offline

# Pharma brand collision (beyond INN stems) — always provenance + caveat.
python3 "${CLAUDE_PLUGIN_ROOT}/skills/brand-maker/scripts/pharma_brand_collision.py" NAME --json
python3 "${CLAUDE_PLUGIN_ROOT}/skills/brand-maker/scripts/inn_stem_collision.py" NAME --json
```

Read `verification_status` / `provenance` from the JSON and carry them verbatim
into the report. Never translate `provisional`/`unverified` into "available".

## Handing verification to subagents

For an isolated, adversarial pass, delegate:
- **trademark-examiner** — "would this survive opposition?" + brand collision.
- **naive-reader** — perceived meaning independent of intent.
- **etymology-verifier** — is the claimed root real AND perceived?
- **diversity-auditor** — is the shortlist one morpheme family?

Each returns a compact, provenance-carrying verdict — not a raw dump.

## Output contract

Every verified line in the final report shows: **value · status
(confirmed|provisional|unverified) · source(s) · timestamp**, and preserves the
"pre-screen (done) ≠ formal research (not done)" distinction. See
`references/verification-doctrine.md` (the canonical doctrine, also injected at
session start).
