import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface KbEnv {
  AI: { run: (model: string, opts: any) => Promise<any> };
  KB_VECTORIZE: {
    query: (vec: number[], opts: any) => Promise<any>;
    upsert: (vectors: Array<{ id: string; values: number[]; metadata?: Record<string, unknown> }>) => Promise<unknown>;
    // Optional so a binding without it degrades to a D1-only delete rather than throwing.
    deleteByIds?: (ids: string[]) => Promise<unknown>;
  };
  DB: { prepare: (q: string) => any; batch?: (s: any[]) => Promise<any> };
}

const EMBED_MODEL = "@cf/baai/bge-m3";

/** Max characters of chunk body returned per hit. This IS the retrieve-don't-dump boundary:
 *  kb_search hands back section POINTERS, and the reader loads `file#section` for full detail. */
const SNIPPET_CHARS = 500;

/** `?,?,?` for a bound IN(...) clause. Pure. Ids are BOUND, never interpolated -- keeping this
 *  a placeholder generator (not a value joiner) is what keeps the query injection-safe. */
function placeholders(n: number): string {
  return new Array(n).fill("?").join(",");
}

/** Project Vectorize matches + D1 rows into hits. Pure -- split out of kb_search so the
 *  fallback ladder (D1 row -> vector metadata -> null) and the snippet cap are pinned. */
function shapeHits(matches: any[], textById: Record<string, any>): any[] {
  return matches.map((m) => {
    const row = textById[m.id] ?? m.metadata ?? {};
    return {
      file: row.file ?? m.metadata?.file ?? null,
      section: row.section ?? m.metadata?.section ?? null,
      score: m.score,
      snippet: String(row.text ?? "").slice(0, SNIPPET_CHARS),
    };
  });
}

/** Build the WHERE clause + bindings for a forget request. Pure, so the id/file XOR contract and
 *  the "never delete everything" guard are testable without a D1 binding.
 *
 *  WHY THIS EXISTS (measured 2026-08-08). Chunk ids are `{file}#{ord}:{md5(file+heading)[:8]}`
 *  (scripts/kb_ingest.py), i.e. derived from the HEADING TEXT. `kb_upsert` is INSERT OR REPLACE,
 *  so re-ingesting after a heading is renamed or removed writes a NEW id and orphans the old row
 *  forever — vector and D1 alike. The index therefore had no invalidation path at all, and it was
 *  not hypothetical: on 2026-08-08 `kb_search` still served `connector-registry.md § 3.5
 *  annas-mcp` with the retired `article_download(doi=…)` text, plus `fulltext-retrieval.md
 *  § Tier 3 — annas-mcp`, a heading that no longer exists. kb_search is the skill's Adım 0.4
 *  recall booster, so the stale rows were being handed back as current guidance. */
function forgetTarget(args: { id?: string; file?: string }): { sql: string; bind: string[] } {
  const id = (args.id ?? "").trim();
  const file = (args.file ?? "").trim();
  if (id && file) throw new Error("give either `id` or `file`, not both");
  if (!id && !file) throw new Error("one of `id` or `file` is required — kb_forget never deletes the whole index");
  return id
    ? { sql: "SELECT id FROM kb_chunks WHERE id = ?", bind: [id] }
    : { sql: "SELECT id FROM kb_chunks WHERE file = ?", bind: [file] };
}

async function embed(env: KbEnv, text: string): Promise<number[]> {
  const r: any = await env.AI.run(EMBED_MODEL, { text: [text] });
  const v = r?.data?.[0] ?? r?.[0];
  if (!Array.isArray(v)) throw new Error("embed: unexpected AI response shape");
  return v as number[];
}

export function registerTools(server: McpServer, env: KbEnv): void {
  server.tool(
    "kb_search",
    "Semantic search over the medical-research knowledge base (SKILL.md + references/*.md), " +
      "bge-m3 vectors. Returns the top-k most relevant KB sections with {file, section, score} " +
      "provenance — a recall booster for Adım 0.4 / Completeness Gate. Read-only.",
    {
      query: z.string().describe("The research question or concept to find relevant KB sections for"),
      k: z.number().int().min(1).max(25).optional().describe("Max sections (default 8)"),
    },
    async ({ query, k }) => {
      try {
        const qv = await embed(env, query);
        const res: any = await env.KB_VECTORIZE.query(qv, { topK: k ?? 8, returnMetadata: "all" });
        const matches: any[] = res?.matches ?? [];
        const ids = matches.map((m) => m.id);
        let textById: Record<string, any> = {};
        if (ids.length) {
          const rows = await env.DB.prepare(
            `SELECT id, file, section, text FROM kb_chunks WHERE id IN (${placeholders(ids.length)})`,
          ).bind(...ids).all();
          for (const r of (rows.results ?? [])) textById[String(r.id)] = r;
        }
        const hits = shapeHits(matches, textById);
        return { content: [{ type: "text", text: JSON.stringify({ query, k: k ?? 8, hits, note: "KB section pointers for coverage; load the named file#section for full detail." }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `kb_search failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "kb_upsert",
    "SETUP-ONLY (Bearer-gated): embed + upsert one KB chunk into the evidentia-kb index. Used by scripts/kb_ingest.py to (re)build the index; not for general use.",
    {
      id: z.string().describe("Stable chunk id, e.g. 'oncology-layer.md#3:abcd1234'"),
      file: z.string().describe("Source file name"),
      section: z.string().describe("Section heading"),
      ord: z.number().int().describe("Section order index within the file"),
      text: z.string().describe("Section text (chunk body)"),
    },
    async ({ id, file, section, ord, text }) => {
      try {
        const v = await embed(env, text);
        await env.KB_VECTORIZE.upsert([{ id, values: v, metadata: { file, section } }]);
        await env.DB.prepare(
          "INSERT OR REPLACE INTO kb_chunks (id,file,section,ord,text) VALUES (?,?,?,?,?)",
        ).bind(id, file, section, ord, text).run();
        return { content: [{ type: "text", text: JSON.stringify({ upserted: id }) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `kb_upsert failed: ${e.message}` }] };
      }
    },
  );

  server.tool(
    "kb_forget",
    "SETUP-ONLY (Bearer-gated): hard-delete KB chunks from the index — the invalidation path " +
      "kb_upsert lacked. Give `file` (all chunks of one source file — the rebuild unit used by " +
      "scripts/kb_ingest.py) or `id` (one chunk). Removes the Vectorize vectors AND the D1 rows. " +
      "Necessary because chunk ids are derived from the HEADING text, so a renamed or deleted " +
      "section is never overwritten by re-ingest: it orphans a row that kb_search keeps serving " +
      "as current guidance. DESTRUCTIVE and irreversible. Idempotent — an unknown id/file deletes " +
      "nothing and reports existed:false. One of `id`/`file` is REQUIRED; there is deliberately no " +
      "delete-everything form.",
    {
      file: z.string().optional().describe("Source file name, e.g. 'fulltext-retrieval.md' — deletes ALL of its chunks"),
      id: z.string().optional().describe("A single chunk id, e.g. 'oncology-layer.md#3:abcd1234'"),
    },
    async ({ file, id }) => {
      try {
        const { sql, bind } = forgetTarget({ id, file });
        const rows = await env.DB.prepare(sql).bind(...bind).all();
        const ids = ((rows.results ?? []) as Array<{ id: string }>).map((r) => String(r.id));
        if (!ids.length) {
          return { content: [{ type: "text", text: JSON.stringify({ target: id ? { id } : { file }, existed: false, deleted: { chunks: 0, vectors: 0 } }, null, 2) }] };
        }
        // Vectorize first: if D1 succeeded and this then failed, the index would keep answering
        // from vectors whose provenance row is gone — a worse state than either side being stale.
        let vectors = 0;
        if (typeof env.KB_VECTORIZE.deleteByIds === "function") {
          for (let i = 0; i < ids.length; i += 1000) {
            await env.KB_VECTORIZE.deleteByIds(ids.slice(i, i + 1000));
          }
          vectors = ids.length;
        }
        await env.DB.prepare(
          `DELETE FROM kb_chunks WHERE id IN (${placeholders(ids.length)})`,
        ).bind(...ids).run();
        return { content: [{ type: "text", text: JSON.stringify({
          target: id ? { id } : { file }, existed: true,
          deleted: { chunks: ids.length, vectors },
          ...(vectors === 0 ? { warning: "Vectorize binding exposes no deleteByIds — D1 rows removed but VECTORS REMAIN; kb_search can still return them with null provenance." } : {}),
        }, null, 2) }] };
      } catch (e: any) {
        return { isError: true, content: [{ type: "text", text: `kb_forget failed: ${e.message}` }] };
      }
    },
  );
}

// Pure helpers surfaced for test/server.test.ts (house pattern: who-gho / globocan / ema /
// openfda / drugddx). Added 2026-08-07: this Worker had no server.test.ts, so the
// retrieve-don't-dump snippet cap and the bound-placeholder query path were unpinned.
export const __testing = { placeholders, shapeHits, forgetTarget, SNIPPET_CHARS, EMBED_MODEL };
