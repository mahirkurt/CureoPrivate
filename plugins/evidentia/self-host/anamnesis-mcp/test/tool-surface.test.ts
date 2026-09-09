import { describe, it, expect } from "vitest";
import worker from "../src/index.js";
import type { Env } from "../src/index.js";
import { evalEnv, MockVectorize } from "./harness.js";

const KEY = "key-cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc";
const ctx = { waitUntil() {}, passThroughOnException() {} } as unknown as ExecutionContext;

function mcpEnv(): Env {
  return {
    ...evalEnv(new MockVectorize()),
    MCP_API_KEY: KEY,
    AUTH_HMAC_SECRET: "hmac-dddddddddddddddddddddddddddddddddddddddddddddddd",
    OAUTH_ALLOWED_REDIRECT_ORIGINS: "",
    MCP_ALLOW_NO_AUTH: "0",
    MCP_OBJECT: {} as DurableObjectNamespace,
  } as unknown as Env;
}

async function rpc(env: Env, body: unknown): Promise<any> {
  const res = await worker.fetch(new Request("https://w.example/mcp", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${KEY}`,
      "Content-Type": "application/json",
      "Accept": "application/json, text/event-stream",
    },
    body: JSON.stringify(body),
  }), env, ctx);
  const text = await res.text();
  const line = text.split("\n").find((l) => l.startsWith("data: "));
  return JSON.parse(line ? line.slice(6) : text);
}

const INIT = {
  jsonrpc: "2.0", id: 1, method: "initialize",
  params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "t", version: "0" } },
};

/** Unwrap a tools/call result: the payload is a JSON text block. */
function payload(r: any): any {
  expect(r.result?.isError, JSON.stringify(r.result)).toBeFalsy();
  return JSON.parse(r.result.content[0].text);
}

describe("MCP tool surface carries the coverage contract", () => {
  it("advertises offset on ingest_document so a capped document can be continued", async () => {
    const env = mcpEnv();
    await rpc(env, INIT);
    const list = await rpc(env, { jsonrpc: "2.0", id: 2, method: "tools/list" });
    const ingest = list.result.tools.find((t: any) => t.name === "ingest_document");
    expect(ingest).toBeDefined();
    expect(Object.keys(ingest.inputSchema.properties)).toContain("offset");
  });

  it("returns chars_indexed / chars_total / next_offset from a real ingest call", async () => {
    const env = mcpEnv();
    await rpc(env, INIT);
    const text = "Alpha opens the record. Beta closes the record.";
    const r = await rpc(env, {
      jsonrpc: "2.0", id: 3, method: "tools/call",
      params: {
        name: "ingest_document",
        arguments: { text, doc_id: "e2e:a", collection: "evidentia:run:9999888877ff" },
      },
    });
    const out = payload(r);
    expect(out.chars_total).toBe(text.length);
    expect(out.chars_indexed).toBe(text.length);
    expect(out.next_offset).toBeNull();
    expect(out.truncated).toBe(false);
  });

  it("rejects an over-long doc_id with an actionable error", async () => {
    const env = mcpEnv();
    await rpc(env, INIT);
    const r = await rpc(env, {
      jsonrpc: "2.0", id: 4, method: "tools/call",
      params: {
        name: "ingest_document",
        arguments: { text: "Alpha one.", doc_id: "z".repeat(80), collection: "evidentia:run:9999888877ff" },
      },
    });
    expect(r.result.isError).toBe(true);
    expect(r.result.content[0].text).toMatch(/doc_id too long/i);
  });
});
