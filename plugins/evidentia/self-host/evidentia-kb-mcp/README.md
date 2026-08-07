# evidentia-kb-mcp

Bearer-gated Cloudflare Worker MCP exposing a **semantic index of the `medical-research` knowledge
base itself** (`SKILL.md` + `references/*.md`) to the `evidentia` plugin. It is a **recall booster**,
not an evidence source: it answers "which part of my own protocol covers this?" so Adım 0.4 /
Completeness Gate can find the right layer instead of guessing. Clinical evidence still comes from
the bibliographic core (PubMed/EuropePMC, ClinicalTrials, OpenAlex, …) — never from here.

Embeddings are Workers AI **bge-m3**; vectors live in Vectorize (`evidentia-kb`) and the chunk text
in D1 (`evidentia-kb-db`, table `kb_chunks`), so a hit returns real provenance rather than a bare id.

## Tools

| Tool | Purpose |
|---|---|
| `kb_search(query, k?)` | **Read-only.** Semantic search over the KB. Returns the top-k sections as `{file, section, score, snippet}` (snippet capped at 500 chars). `k` 1–25, default 8. |
| `kb_upsert(id, file, section, ord, text)` | **SETUP-ONLY · WRITE.** Embeds and upserts one KB chunk (Vectorize + D1). Driven by `scripts/kb_ingest.py` to (re)build the index; not for general use. |

`kb_search` returns section **pointers**, deliberately: load the named `file#section` for the full
text. That is the retrieve-don't-dump contract — the index exists to aim the reader, not to replace it.

## Why this Worker is gated

`MCP_ALLOW_NO_AUTH="0"` in `wrangler.jsonc`, unlike the keyless siblings (`who-gho`, `globocan`,
`ema`, `drugddx`). Two independent reasons, either sufficient:

1. **`kb_upsert` writes.** An open endpoint would let anyone poison the index that steers evidentia's
   own coverage decisions.
2. **Paid bindings.** Workers AI + Vectorize + D1 all bill per call; an open endpoint is a quota
   liability.

Bearer key = `EVIDENTIA_KB_MCP_API_KEY` (Doppler `cureohub`/`dev_personal`; see `docs/KURULUM.md`).
The hardened OAuth 2.1 surface (S256 PKCE, redirect allowlist, RFC 9728) is additive for
claude.ai / ChatGPT / grok connector flows.

## Develop / verify

```bash
npm install && npm run typecheck && npm test   # vitest — auth.test + routing.test
npm run dev                                    # wrangler dev
npm run deploy                                 # wrangler deploy
```

Post-deploy smoke (checks `/health`, S256-only metadata, the 401 gate, and — with a key — an
authenticated `initialize`):

```bash
BASE=https://evidentia-kb-mcp.cureonics.workers.dev \
MCP_API_KEY="$(doppler secrets get EVIDENTIA_KB_MCP_API_KEY --plain -p cureohub -c dev_personal)" \
  ./scripts/smoke_oauth_public.sh
```

Fleet-wide identity consistency (this Worker's `REALM` / `package.json` / `wrangler.jsonc` name must
all agree) is enforced by `python3 ../../scripts/g_identity.py`.

## Rebuilding the index

`scripts/kb_ingest.py` (plugin root) chunks the KB by section, calls `kb_upsert` per chunk and is
idempotent — chunk ids are `"<file>#<ord>:<hash>"`, so re-running replaces rather than duplicates.
Re-run it after any substantive edit to `SKILL.md` or `references/*.md`; otherwise `kb_search`
silently points at stale sections.

## Secrets

`MCP_API_KEY`, `AUTH_HMAC_SECRET` — set with `wrangler secret put`, never declared in
`wrangler.jsonc` (fleet invariant 6). No upstream credential exists: the only data source is this
Worker's own Vectorize/D1, so there is no confused-deputy surface to protect beyond the gate itself.
