/**
 * collection.ts — tenant / working-set identity for anamnesis-mcp.
 *
 * Contract (do not invent other names):
 *   collection = "{plugin}:{kind}:{id}"
 *   kind ∈ { run, sess, lib }
 *   Evidentia scratch: collection = "evidentia:run:<12hex>"
 *
 * Missing collection on write → `_legacy` (compat). `_legacy` is NOT a client-minted
 * collection; it is the bucket for pre-namespace rows and old clients.
 */

export const LEGACY_COLLECTION = "_legacy";
export const COLLECTION_KINDS = ["run", "sess", "lib"] as const;
export type CollectionKind = (typeof COLLECTION_KINDS)[number];

const KIND_SET = new Set<string>(COLLECTION_KINDS);
const PLUGIN_RE = /^[a-z0-9][a-z0-9_-]*$/i;
const ID_RE = /^[a-z0-9][a-z0-9._:-]*$/i;

export class CollectionRequiredError extends Error {
  readonly tool: string;
  constructor(tool: string) {
    super(`${tool} requires collection (unscoped access is an MCP error)`);
    this.name = "CollectionRequiredError";
    this.tool = tool;
  }
}

export class InvalidCollectionError extends Error {
  constructor(raw: string) {
    super(
      `invalid collection '${raw}': expected {plugin}:{run|sess|lib}:{id} ` +
        `(e.g. evidentia:run:<12hex>)`,
    );
    this.name = "InvalidCollectionError";
  }
}

/** True for a client-minted collection. `_legacy` is the internal compat bucket. */
export function isValidCollection(raw: string): boolean {
  const s = (raw || "").trim();
  if (!s || s === LEGACY_COLLECTION) return false;
  const parts = s.split(":");
  if (parts.length < 3) return false;
  const plugin = parts[0];
  const kind = parts[1];
  const id = parts.slice(2).join(":");
  return Boolean(plugin && id && KIND_SET.has(kind) && PLUGIN_RE.test(plugin) && ID_RE.test(id));
}

/**
 * Resolve a write-side collection. Empty/missing → `_legacy`.
 * A present but invalid value is an error (never silently bucket it).
 */
export function resolveWriteCollection(raw?: string | null): string {
  const s = (raw ?? "").trim();
  if (!s) return LEGACY_COLLECTION;
  if (s === LEGACY_COLLECTION) return LEGACY_COLLECTION;
  if (!isValidCollection(s)) throw new InvalidCollectionError(s);
  return s;
}

/**
 * Resolve a read/delete collection. Empty is a caller policy (error vs unscoped);
 * invalid is always an error. `_legacy` is accepted so operators can observe/forget it.
 */
export function resolveScopedCollection(raw?: string | null): string | undefined {
  const s = (raw ?? "").trim();
  if (!s) return undefined;
  if (s === LEGACY_COLLECTION) return LEGACY_COLLECTION;
  if (!isValidCollection(s)) throw new InvalidCollectionError(s);
  return s;
}

export function requireCollection(raw: string | undefined | null, tool: string): string {
  const scoped = resolveScopedCollection(raw);
  if (!scoped) throw new CollectionRequiredError(tool);
  return scoped;
}

/** Scratch collections (run/sess) may carry ttl_hours. `lib` is durable. */
export function isScratchCollection(collection: string): boolean {
  if (collection === LEGACY_COLLECTION) return false;
  const kind = collection.split(":")[1];
  return kind === "run" || kind === "sess";
}

export const __testing = {
  KIND_SET,
  PLUGIN_RE,
  ID_RE,
};
