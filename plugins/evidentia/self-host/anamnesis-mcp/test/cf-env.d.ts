/** Miniflare bindings for P3 eval. Runtime comes from @cloudflare/vitest-pool-workers. */
declare module "cloudflare:workers" {
  export const env: {
    DB: {
      prepare: (sql: string) => {
        bind: (...args: unknown[]) => {
          run: () => Promise<unknown>;
          all: () => Promise<{ results?: unknown[] }>;
          first: <T = unknown>() => Promise<T | null>;
        };
        run: () => Promise<unknown>;
        all: () => Promise<{ results?: unknown[] }>;
        first: <T = unknown>() => Promise<T | null>;
      };
    };
  };
}
