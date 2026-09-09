import { describe, it, expect } from "vitest";
import worker from "../src/index.js";
import type { Env } from "../src/index.js";
import { ingestDocument, listDocs } from "../src/rag.js";
import { evalEnv, MockVectorize } from "./harness.js";

const KEY = "key-cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc";
const ctx = { waitUntil() {}, passThroughOnException() {} } as unknown as ExecutionContext;
const SCRATCH = "evidentia:run:0f0f0f0f0f0f";

function opsEnv(vec = new MockVectorize()): Env {
  return {
    ...evalEnv(vec),
    MCP_API_KEY: KEY,
    AUTH_HMAC_SECRET: "hmac-dddddddddddddddddddddddddddddddddddddddddddddddd",
    OAUTH_ALLOWED_REDIRECT_ORIGINS: "",
    MCP_ALLOW_NO_AUTH: "0",
    MCP_OBJECT: {} as DurableObjectNamespace,
  } as unknown as Env;
}

describe("scheduled reaper is wired to the cron trigger (A2)", () => {
  it("collects expired scratch when the schedule fires", async () => {
    const env = opsEnv();
    await ingestDocument(env, {
      text: "Alpha expiring body.", doc_id: "cron:a", collection: SCRATCH, ttl_hours: 1,
    });
    // Pretend the nightly trigger fires two hours later.
    const event = { scheduledTime: Date.now() + 2 * 3600_000, cron: "0 4 * * *" } as ScheduledController;
    await worker.scheduled!(event, env, ctx);
    expect((await listDocs(env, SCRATCH)).docs.filter((d) => d["id"] === "cron:a")).toEqual([]);
  });
});

describe("deep health check", () => {
  it("keeps the public liveness probe unauthenticated and cheap", async () => {
    const res = await worker.fetch(new Request("https://w.example/health"), opsEnv(), ctx);
    expect(res.status).toBe(200);
    expect(await res.text()).toBe("ok");
  });

  it("requires the bearer for the deep probe", async () => {
    const res = await worker.fetch(new Request("https://w.example/health?deep=1"), opsEnv(), ctx);
    expect(res.status).toBe(401);
  });

  it("reports per-dependency reachability to an authenticated operator", async () => {
    const res = await worker.fetch(new Request("https://w.example/health?deep=1", {
      headers: { Authorization: `Bearer ${KEY}` },
    }), opsEnv(), ctx);
    expect(res.status).toBe(200);
    const body = await res.json() as Record<string, unknown>;
    expect(body["d1"]).toBe("ok");
    expect(body["vectorize"]).toBe("ok");
    expect(body["ai"]).toBe("ok");
  });

  it("reports a failing dependency instead of a blanket ok", async () => {
    const env = opsEnv();
    const broken = { ...env, AI: { run: async () => { throw new Error("Workers AI down"); } } } as Env;
    const res = await worker.fetch(new Request("https://w.example/health?deep=1", {
      headers: { Authorization: `Bearer ${KEY}` },
    }), broken, ctx);
    const body = await res.json() as Record<string, unknown>;
    expect(body["ai"]).not.toBe("ok");
    expect(body["status"]).toBe("degraded");
  });
});
