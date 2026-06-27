import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export interface KbEnv {
  AI: { run: (model: string, opts: any) => Promise<any> };
  KB_VECTORIZE: {
    query: (vec: number[], opts: any) => Promise<any>;
    upsert: (vectors: Array<{ id: string; values: number[]; metadata?: Record<string, unknown> }>) => Promise<unknown>;
  };
  DB: { prepare: (q: string) => any; batch?: (s: any[]) => Promise<any> };
}

const EMBED_MODEL = "@cf/baai/bge-m3";

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
          const ph = ids.map(() => "?").join(",");
          const rows = await env.DB.prepare(
            `SELECT id, file, section, text FROM kb_chunks WHERE id IN (${ph})`,
          ).bind(...ids).all();
          for (const r of (rows.results ?? [])) textById[String(r.id)] = r;
        }
        const hits = matches.map((m) => {
          const row = textById[m.id] ?? m.metadata ?? {};
          return { file: row.file ?? m.metadata?.file ?? null, section: row.section ?? m.metadata?.section ?? null, score: m.score, snippet: String(row.text ?? "").slice(0, 500) };
        });
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
}
