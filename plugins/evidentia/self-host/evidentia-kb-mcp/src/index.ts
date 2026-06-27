import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools, type KbEnv } from "./server.js";
import { handleOAuth, requireBearer, type AuthEnv } from "./auth.js";

export interface Env extends AuthEnv, KbEnv { MCP_OBJECT: DurableObjectNamespace; }

export class EvidentiaKb extends McpAgent<Env> {
  server = new McpServer({ name: "evidentia-kb-mcp", version: "1.0.0" });
  async init(): Promise<void> { registerTools(this.server, this.env as unknown as KbEnv); }
}

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const p = new URL(req.url).pathname;
    if (p === "/health") return new Response("ok", { status: 200, headers: { "content-type": "text/plain" } });
    if (p.startsWith("/.well-known/oauth") || p.startsWith("/oauth/")) return handleOAuth(req, env);
    if (p === "/mcp" || p === "/sse") {
      const denied = requireBearer(req, env); if (denied) return denied;
      return p === "/sse" ? EvidentiaKb.serveSSE("/sse").fetch(req, env, ctx) : EvidentiaKb.serve("/mcp").fetch(req, env, ctx);
    }
    return new Response("not found", { status: 404, headers: { "content-type": "text/plain" } });
  },
};
