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
 * SOURCE SPANS ARE THREADED, NOT RECONSTRUCTED (audit 2026-09-07, findings A1+A4).
 * Every block / sentence / window / chunk carries an EXACT `[start,end)` offset into the
 * ORIGINAL text. Previously rag.ts recovered offsets afterwards with `text.indexOf(chunkText)`,
 * which misses on any source with wrapped lines (i.e. nearly every PDF/OCR extract, the primary
 * input) because block and window assembly joins with " ". The old fallback then emitted a
 * SYNTHETIC offset indistinguishable from a real one. Threading positions makes the offsets
 * true by construction and, as a side effect, lets `charsIndexed` report exactly how far the
 * window cap got — so truncation is measurable instead of silent.
 *
 * Consequences for the implementation below: the source is never rewritten before scanning.
 * Paragraph/heading detection walks the original string, and abbreviation protection is a
 * lookbehind TEST at a candidate boundary rather than a `<DOT>` substitution (which would
 * shift every subsequent offset by +4 per match).
 *
 * Honest cost note: real semantic chunking costs N window-embeddings (boundary detection) +
 * M chunk-embeddings (stored vectors) per document. We bound N by grouping sentences into
 * windows and capping windows/doc; over-long inputs stop at the cap and report `charsIndexed`
 * so the caller can resume with `offset` instead of losing the tail.
 */

export interface SemanticChunk {
  idx: number;
  text: string;
  tokenEst: number;
  vector?: number[];
  /** Exact start offset of this chunk in the ORIGINAL text (inclusive). */
  charStart: number;
  /** Exact end offset of this chunk in the ORIGINAL text (exclusive). */
  charEnd: number;
}

export interface ChunkOpts {
  /** cosine below this between adjacent windows => semantic boundary. Default 0.55. */
  breakThreshold?: number;
  /** hard token cap per chunk. Default 512. */
  maxTokens?: number;
  /** sentences grouped per embedding window (bounds embed calls). Default 2. */
  windowSentences?: number;
  /** safety cap on windows per document (over-long inputs stop here and report charsIndexed). */
  maxWindows?: number;
  /** resume position: start scanning the source at this offset. Default 0. */
  offset?: number;
}

export type EmbedFn = (texts: string[]) => Promise<number[][]>;

const DEFAULTS: Required<ChunkOpts> = {
  breakThreshold: 0.55,
  maxTokens: 512,
  windowSentences: 2,
  maxWindows: 400,
  offset: 0,
};

/** A slice of the source with its exact offsets. `text` is whitespace-normalised. */
export interface Span {
  text: string;
  start: number;
  end: number;
}

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

const WS = /\s/;

/** Tighten [s,e) onto non-whitespace and emit a normalised span (dropped when empty). */
function pushSpan(out: Span[], text: string, s: number, e: number): void {
  while (s < e && WS.test(text[s])) s++;
  while (e > s && WS.test(text[e - 1])) e--;
  if (e > s) out.push({ text: text.slice(s, e).replace(/\s+/g, " "), start: s, end: e });
}

const HEADING_MARKER = /^#{1,6}\s+/;
/** Short ALL-CAPS section markers ("METHODS", "2. RESULTS") with no terminal punctuation. */
const CAPS_HEADING = /^[A-ZÇĞİÖŞÜ0-9][A-ZÇĞİÖŞÜ0-9 .,:()/-]{2,60}$/;

/** Emit blocks for one paragraph: a heading line becomes its own block, other lines merge. */
function paragraphBlocks(text: string, start: number, end: number, out: Span[]): void {
  let bufStart = -1;
  let bufEnd = -1;
  const flush = (): void => {
    if (bufStart >= 0) pushSpan(out, text, bufStart, bufEnd);
    bufStart = -1;
    bufEnd = -1;
  };
  let lineStart = start;
  while (lineStart < end) {
    let lineEnd = text.indexOf("\n", lineStart);
    if (lineEnd < 0 || lineEnd > end) lineEnd = end;
    let s = lineStart;
    let e = lineEnd;
    while (s < e && WS.test(text[s])) s++;
    while (e > s && WS.test(text[e - 1])) e--;
    const line = text.slice(s, e);
    if (line) {
      const marker = HEADING_MARKER.exec(line);
      const isHeading = marker !== null ||
        (CAPS_HEADING.test(line) && line.length < 64 && !/[.!?]$/.test(line));
      if (isHeading) {
        flush();
        // Span starts AFTER the markdown marker so slice(start,end) === the emitted text.
        pushSpan(out, text, s + (marker ? marker[0].length : 0), e);
      } else {
        if (bufStart < 0) bufStart = s;
        bufEnd = e;
      }
    }
    lineStart = lineEnd + 1;
  }
  flush();
}

/** Structural blocks (blank-line paragraphs + promoted headings) with exact source spans. */
export function blockSpans(text: string, from = 0): Span[] {
  const out: Span[] = [];
  const n = text.length;
  let i = Math.max(0, Math.min(from, n));
  const para = /\n[ \t\r]*\n/g;
  while (i < n) {
    while (i < n && WS.test(text[i])) i++;
    if (i >= n) break;
    para.lastIndex = i;
    const hit = para.exec(text);
    const paraEnd = hit ? hit.index : n;
    paragraphBlocks(text, i, paraEnd, out);
    i = hit ? hit.index + hit[0].length : n;
  }
  return out;
}

/** Abbreviations that must not end a sentence. Tested as a LOOKBEHIND on the source, so no
 *  substitution shifts the offsets (the old `<DOT>` trick added +4 chars per match). */
const ABBREV_TAIL = /\b(e\.g|i\.e|et al|vs|Dr|Prof|Fig|No|cf|approx|ca)$/i;
const SENTENCE_START = /[A-ZÇĞİÖŞÜ0-9"'(]/;

/** Sentence spans inside one block, with exact source offsets. */
export function sentenceSpans(text: string, block: Span): Span[] {
  const out: Span[] = [];
  const { start, end } = block;
  let s = start;
  let i = start;
  while (i < end) {
    const ch = text[i];
    if (ch === "." || ch === "!" || ch === "?") {
      let j = i + 1;
      let sawGap = false;
      while (j < end && WS.test(text[j])) {
        j++;
        sawGap = true;
      }
      const isBoundary = sawGap && j < end && SENTENCE_START.test(text[j]) &&
        !(ch === "." && ABBREV_TAIL.test(text.slice(start, i)));
      if (isBoundary) {
        pushSpan(out, text, s, i + 1);
        s = j;
        i = j;
        continue;
      }
    }
    i++;
  }
  pushSpan(out, text, s, end);
  return out;
}

export interface ChunkResult {
  chunks: SemanticChunk[];
  truncated: boolean;
  windowCount: number;
  /** Absolute offset in the ORIGINAL text up to which this call indexed. When `truncated`,
   *  pass this back as `offset` to ingest the remainder — nothing is lost silently. */
  charsIndexed: number;
}

/** Group sentences into embedding windows, stopping at the window cap. */
function buildWindows(
  text: string, from: number, windowSentences: number, maxWindows: number,
): { units: Span[]; truncated: boolean } {
  const units: Span[] = [];
  for (const block of blockSpans(text, from)) {
    const sents = sentenceSpans(text, block);
    for (let i = 0; i < sents.length; i += windowSentences) {
      const group = sents.slice(i, i + windowSentences);
      units.push({
        text: group.map((g) => g.text).join(" "),
        start: group[0].start,
        end: group[group.length - 1].end,
      });
      if (units.length >= maxWindows) return { units, truncated: true };
    }
  }
  return { units, truncated: false };
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
  if (opts.offset !== undefined) out.offset = opts.offset;
  return out;
}

/**
 * Produce semantic chunks. Stored chunk vectors are the MEAN of their window embeddings
 * (avoids a second embedding pass per chunk; mean-pooling of bge-m3 windows is a faithful
 * representation for cosine retrieval). Returns chunk vectors so the caller upserts directly.
 */
export async function semanticChunk(text: string, embed: EmbedFn, opts: ChunkOpts = {}): Promise<ChunkResult> {
  const o = resolveOpts(opts);
  const from = Math.max(0, Math.min(o.offset, text.length));
  const capped = buildWindows(text, from, o.windowSentences, o.maxWindows);
  const units = capped.units;
  // Stopped at the last window's end when the cap fired; otherwise the whole source is consumed.
  const stoppedAt = capped.truncated && units.length ? units[units.length - 1].end : text.length;
  // The cap fires the moment units.length reaches maxWindows — which can be the LAST window, with
  // nothing after it. Reporting `truncated` there sends the caller back for an empty continuation
  // and, worse, tells them content is missing when none is. `truncated` therefore means "content
  // REMAINS unindexed", not "the cap was reached". Measured live 2026-09-07 on a 126 KB document.
  const remainder = text.slice(stoppedAt).trim();
  const truncated = capped.truncated && remainder.length > 0;
  const charsIndexed = truncated ? stoppedAt : text.length;
  if (units.length === 0) return { chunks: [], truncated, windowCount: 0, charsIndexed };
  if (units.length === 1) {
    const [v] = await embed([units[0].text]);
    return {
      chunks: [{
        idx: 0, text: units[0].text, tokenEst: estimateTokens(units[0].text), vector: v,
        charStart: units[0].start, charEnd: units[0].end,
      }],
      truncated, windowCount: 1, charsIndexed,
    };
  }

  const vectors = await embed(units.map((u) => u.text));

  // greedy merge with cosine boundary + token cap
  const chunks: SemanticChunk[] = [];
  let curUnits: Span[] = [units[0]];
  let curVecs: number[][] = [vectors[0]];
  let curTokens = estimateTokens(units[0].text);

  const pushChunk = (): void => {
    const body = curUnits.map((u) => u.text).join(" ").trim();
    chunks.push({
      idx: chunks.length, text: body, tokenEst: estimateTokens(body), vector: meanVector(curVecs),
      charStart: curUnits[0].start, charEnd: curUnits[curUnits.length - 1].end,
    });
  };

  for (let i = 1; i < units.length; i++) {
    const sim = cosineLocal(vectors[i - 1], vectors[i]);
    const nextTokens = estimateTokens(units[i].text);
    const boundary = sim < o.breakThreshold || curTokens + nextTokens > o.maxTokens;
    if (boundary) {
      pushChunk();
      curUnits = [units[i]];
      curVecs = [vectors[i]];
      curTokens = nextTokens;
    } else {
      curUnits.push(units[i]);
      curVecs.push(vectors[i]);
      curTokens += nextTokens;
    }
  }
  pushChunk();
  return { chunks, truncated, windowCount: units.length, charsIndexed };
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

/** Text-only views kept for the existing unit suite and for callers that do not need spans. */
function splitBlocks(text: string): string[] {
  return blockSpans(text, 0).map((b) => b.text);
}
function splitSentences(block: string): string[] {
  return sentenceSpans(block, { text: block, start: 0, end: block.length }).map((s) => s.text);
}

export const __testing = { splitBlocks, splitSentences, estimateTokens, meanVector, resolveOpts };
