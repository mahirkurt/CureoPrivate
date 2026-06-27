import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
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
      },
    },
  },
});
