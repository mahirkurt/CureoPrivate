/**
 * chunk.ts — Semantic chunking for anamnesis-mcp.
 *
 * WHY: naive fixed-size chunking splits claims mid-thought and wrecks retrieval precision,
 * which is exactly what produces the "incomplete / inconsistent" answers the operator wants
 * to eliminate. We chunk on SEMANTIC boundaries (Greg Kamradt "level 4" / LlamaIndex
 * SemanticSplitter pattern): structural pre-split → sentence windows → embed → merge adjacent
 * windows while embedding cosine similarity stays above a threshold, capped by a token budget.
 *
 * The embedding function is INJECTED (not imported) so this module is unit-testable with a
 * deterministic fake embedder — no Workers AI needed in CI.
 *
 * Honest cost note: real semantic chunking costs N window-embeddings (boundary detection) +
 * M chunk-embeddings (stored vectors) per document. We bound N by grouping sentences into
 * windows and capping windows/doc; very long inputs are pre-segmented. This is the deliberate
 * accuracy/cost trade — documented, not hidden.
 */

export interface SemanticChunk {
  idx: number;
  text: string;
  tokenEst: number;
  vector?: number[];
}

export interface ChunkOpts {
  /** cosine below this between adjacent windows => semantic boundary. Default 0.55. */
  breakThreshold?: number;
  /** hard token cap per chunk. Default 512. */
  maxTokens?: number;
  /** sentences grouped per embedding window (bounds embed calls). Default 2. */
  windowSentences?: number;
  /** safety cap on windows per document (very long inputs are truncated with a flag). */
  maxWindows?: number;
}

export type EmbedFn = (texts: string[]) => Promise<number[][]>;

const DEFAULTS: Required<ChunkOpts> = {
  breakThreshold: 0.55,
  maxTokens: 512,
  windowSentences: 2,
  maxWindows: 400,
};

/** Rough token estimate: max(words×1.3, chars/4); no tokenizer in-Worker. */
export function estimateTokens(text: string): number {
  // Word heuristic undercounts space-starved PDF/OCR text; char/4 is the usual
  // fallback so the maxTokens cap still fires on dense extracts.
  const trimmed = text.trim();
  const words = trimmed.split(/\s+/).filter(Boolean).length;
  const byWords = Math.round(words * 1.3);
  const byChars = Math.ceil(trimmed.length / 4);
  return Math.max(1, byWords, byChars);
}

/** Split into structural blocks: blank-line paragraphs + heading/section boundaries. */
export function splitBlocks(text: string): string[] {
  const normalized = text.replace(/\r\n/g, "\n").replace(/\n{3,}/g, "\n\n");
  const rawParas = normalized.split(/\n\s*\n/);
  const blocks: string[] = [];
  for (const para of rawParas) {
    const trimmed = para.trim();
    if (!trimmed) continue;
    // promote markdown headings / ALL-CAPS short section markers to their own block
    const lines = trimmed.split("\n");
    let buf: string[] = [];
    const flush = () => { if (buf.length) { blocks.push(buf.join(" ").trim()); buf = []; } };
    for (const line of lines) {
      const l = line.trim();
      const isHeading = /^#{1,6}\s/.test(l) ||
        (/^[A-ZÇĞİÖŞÜ0-9][A-ZÇĞİÖŞÜ0-9 .,:()/-]{2,60}$/.test(l) && l.length < 64 && !/[.!?]$/.test(l));
      if (isHeading) { flush(); blocks.push(l.replace(/^#{1,6}\s/, "")); }
      else buf.push(l);
    }
    flush();
  }
  return blocks.filter(Boolean);
}

/** Sentence splitter (abbreviation-light; medical text tolerant). */
export function splitSentences(block: string): string[] {
  // protect common abbreviations from false breaks
  const protectedText = block
    .replace(/\b(e\.g|i\.e|et al|vs|Dr|Prof|Fig|No|cf|approx|ca)\./gi, "$1<DOT>");
  const parts = protectedText.split(/(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ0-9"'(])/);
  return parts.map((s) => s.replace(/<DOT>/g, ".").trim()).filter(Boolean);
}

/** Build sentence windows (units) across all blocks, preserving order. */
function buildWindows(text: string, windowSentences: number, maxWindows: number): { units: string[]; truncated: boolean } {
  const units: string[] = [];
  for (const block of splitBlocks(text)) {
    const sents = splitSentences(block);
    for (let i = 0; i < sents.length; i += windowSentences) {
      units.push(sents.slice(i, i + windowSentences).join(" "));
      if (units.length >= maxWindows) return { units, truncated: true };
    }
  }
  return { units, truncated: false };
}

export interface ChunkResult {
  chunks: SemanticChunk[];
  truncated: boolean;
  windowCount: number;
}

/**
 * Merge caller opts over defaults WITHOUT letting explicit `undefined` clobber.
 * MCP tool handlers often pass `{ maxTokens: a.max_tokens }` where the field is
 * omitted → `undefined`; a naïve `{ ...DEFAULTS, ...opts }` then sets
 * `maxTokens`/`breakThreshold` to undefined, disabling BOTH the token cap and
 * the cosine boundary (`n > undefined` / `sim < undefined` are always false) and
 * collapsing every multi-window document into a single chunk (n_chunks=1 with
 * window_count ≫ 1). Measured live 2026-08-20.
 */
function resolveOpts(opts: ChunkOpts): Required<ChunkOpts> {
  const out: Required<ChunkOpts> = { ...DEFAULTS };
  if (opts.breakThreshold !== undefined) out.breakThreshold = opts.breakThreshold;
  if (opts.maxTokens !== undefined) out.maxTokens = opts.maxTokens;
  if (opts.windowSentences !== undefined) out.windowSentences = opts.windowSentences;
  if (opts.maxWindows !== undefined) out.maxWindows = opts.maxWindows;
  return out;
}

/**
 * Produce semantic chunks. Stored chunk vectors are the MEAN of their window embeddings
 * (avoids a second embedding pass per chunk; mean-pooling of bge-m3 windows is a faithful
 * representation for cosine retrieval). Returns chunk vectors so the caller upserts directly.
 */
export async function semanticChunk(text: string, embed: EmbedFn, opts: ChunkOpts = {}): Promise<ChunkResult> {
  const o = resolveOpts(opts);
  const { units, truncated } = buildWindows(text, o.windowSentences, o.maxWindows);
  if (units.length === 0) return { chunks: [], truncated, windowCount: 0 };
  if (units.length === 1) {
    const [v] = await embed(units);
    return { chunks: [{ idx: 0, text: units[0], tokenEst: estimateTokens(units[0]), vector: v }], truncated, windowCount: 1 };
  }

  const vectors = await embed(units);

  // greedy merge with cosine boundary + token cap
  const chunks: SemanticChunk[] = [];
  let curText: string[] = [units[0]];
  let curVecs: number[][] = [vectors[0]];
  let curTokens = estimateTokens(units[0]);

  const pushChunk = () => {
    const text = curText.join(" ").trim();
    chunks.push({ idx: chunks.length, text, tokenEst: estimateTokens(text), vector: meanVector(curVecs) });
  };

  for (let i = 1; i < units.length; i++) {
    const sim = cosineLocal(vectors[i - 1], vectors[i]);
    const nextTokens = estimateTokens(units[i]);
    const boundary = sim < o.breakThreshold || curTokens + nextTokens > o.maxTokens;
    if (boundary) {
      pushChunk();
      curText = [units[i]];
      curVecs = [vectors[i]];
      curTokens = nextTokens;
    } else {
      curText.push(units[i]);
      curVecs.push(vectors[i]);
      curTokens += nextTokens;
    }
  }
  pushChunk();
  return { chunks, truncated, windowCount: units.length };
}

function meanVector(vs: number[][]): number[] {
  if (vs.length === 1) return vs[0];
  const n = vs[0].length;
  const out = new Array(n).fill(0);
  for (const v of vs) for (let i = 0; i < n; i++) out[i] += v[i];
  for (let i = 0; i < n; i++) out[i] /= vs.length;
  return out;
}

function cosineLocal(a: number[], b: number[]): number {
  let dot = 0, na = 0, nb = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  return na && nb ? dot / (Math.sqrt(na) * Math.sqrt(nb)) : 0;
}

export const __testing = { splitBlocks, splitSentences, estimateTokens, meanVector, resolveOpts };
