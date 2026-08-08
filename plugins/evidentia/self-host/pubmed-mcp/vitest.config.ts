import { cloudflareTest } from "@cloudflare/vitest-pool-workers";
import { defineConfig } from "vitest/config";

// Migrated 2026-08-07 for @cloudflare/vitest-pool-workers v0.20 (vitest 4): the pool is now a
// VITE PLUGIN, not a `test.poolOptions.workers` entry, and the `/config` subpath export
// (defineWorkersConfig) was removed. Shape taken from the package's own
// `codemods/vitest-v3-to-v4` transform, not guessed.
//
// KNOWN NOISE (upstream, not ours): each run prints ~26 lines of
//   Sourcemap for ".../@modelcontextprotocol/sdk/dist/esm/**.js" points to missing source files
// The SDK publishes .js.map files referencing sources it does not ship. MEASURED: a Vite
// `customLogger` intercepting warn/warnOnce/info/error does NOT suppress them -- the message is
// emitted from inside the workerd/miniflare isolate, below the Vite logger. Rather than ship a
// no-op that looks like a fix, the noise is left visible and documented. It does not affect
// results (exit 0, all suites pass) and disappears when the SDK fixes its packaging.
export default defineConfig({
  plugins: [
    cloudflareTest({
      wrangler: { configPath: "./wrangler.jsonc" },
      miniflare: {
        // test-only: provide non-prod secret values + allow-no-auth where a test needs it.
        // Real secrets are NEVER committed; these exist only inside the test sandbox.
        bindings: {
          MCP_API_KEY: "test-mcp-api-key-000000000000000000000000000000000000000000000000000000000000",
          AUTH_HMAC_SECRET: "test-hmac-secret-0000000000000000000000000000000000000000000000000000000000",
          MCP_ALLOW_NO_AUTH: "0",
          OAUTH_ALLOWED_REDIRECT_ORIGINS: "",
        },
      },
    }),
  ],
});
