# `titck-cache-mcp` — AI Ajanı için Adım Adım İnşa Talimatı (rxpraxis v1.1)

> **Bu belge bir yürütme talimatıdır.** Bir AI kodlama ajanına (Claude Code, Cursor, Windsurf vb.)
> doğrudan verilmek üzere yazılmıştır. **Adımları SIRAYLA uygula.** Her adımın sonundaki
> **`✅ Kabul kontrolü`** komutunu çalıştır; geçmeden bir sonraki adıma **GEÇME**. Bir kontrol
> başarısız olursa, o adımı düzelt ve kontrolü yeniden çalıştır. Tüm kod tam ve kopyalanabilir
> biçimde verilmiştir; tahmin etme, verilen içeriği birebir oluştur. Dil: kod İngilizce, açıklama
> Türkçe. Hedef ortam: **Cloudflare Workers (TypeScript)**.

---

## 0. Amaç ve Bağlam (ajanın bilmesi gereken)

Bu Worker, rxpraxis süitinin **R1 riskini** (BUILD.md §4) sözleşme-disiplininden **kod-düzeyi
deterministik garantiye** taşır. rxpraxis'in üç skill'i (medical-research, pharmaintel,
pharmapatent) aynı upstream **TİTCK MCP** sunucusunu bağımsızca çağırır; "tek-sefer TİTCK"
kuralı bugün yalnızca prompt-düzeyi bir disiplindir. Bu Worker, TİTCK MCP'nin önüne **şeffaf,
önbellekleyen bir MCP proxy** olarak girer ve aynı sorgunun upstream'e ikinci kez gitmesini
**fiziksel olarak** engeller.

**İki seviyeli önbellek ilişkisi (önemli):**

| Seviye | Nerede | Anahtar | Garanti |
|---|---|---|---|
| Sözleşme (mevcut) | `shared/canonical-cache-contract.md` | artefakt `scope_hash` | "tüm çıkarım dizisi bir kez" — *prompt disiplini* |
| **Kod (bu Worker)** | `titck-cache-mcp` | her `(tool, args)` için `scope_key` | "her benzersiz çağrı upstream'e ≤1" — *deterministik* |

Worker, her **tekil araç çağrısını** içerik-adresli anahtarla önbelleğe alır. Böylece model
`get_drug(barcode=X)`'i iki skill'de iki kez çağırsa bile upstream **bir kez** vurulur; tüm
kanonik çıkarım dizisi ikinci kez istenirse upstream maliyeti **sıfırdır**. Bu, R1'in talep
ettiği deterministik davranıştır.

**`midas-mcp` ile simetri.** Mevcut `midas-mcp.cureonics.workers.dev` Worker'ı ThoughtSpot REST
`searchdata` ucunu sarıp MCP olarak sunar. Bu Worker da aynı yığını (Cloudflare Workers +
Wrangler + TypeScript) ve aynı `*.cureonics.workers.dev` desenini kullanır; fark, upstream'in
**zaten bir MCP sunucusu** olması ve bizim bir **önbellekleyen proxy** kurmamızdır.

### 0.1 Mimari

```
                          ┌─────────────────────────────────────────────┐
   Claude (rxpraxis)      │            titck-cache-mcp (Worker)          │
   ───────────────►  POST │                                             │
   /mcp (JSON-RPC)        │  index.ts  ─ method yönlendirme              │
                          │     │                                       │
                          │     ├─ tools/call & cacheable?              │
                          │     │     1) KV.get(scope_key) ──HIT──► dön  │
                          │     │     2) MISS → SingleFlight DO          │
                          │     │            (scope_key başına tekil)    │
                          │     │              └─ upstream'e BİR kez ───────────►  TİTCK MCP
                          │     │              └─ KV.put(ttl) + dön               (Cloud Run)
                          │     ├─ initialize / tools/list / diğer       │
                          │     │     → şeffaf relay (gerekirse cache'li  │
                          │     │       tools/list)                      │
                          │     └─ her cacheable çağrı → Ledger DO        │
                          │            (Mcp-Session-Id başına sayaç)      │
                          │  KV: TITCK_CACHE   DO: SINGLEFLIGHT, LEDGER   │
                          └─────────────────────────────────────────────┘
   GET /health · GET /ledger?session=… · POST /purge  (gözlemlenebilirlik)
```

**Bileşenler:** (a) **KV** `TITCK_CACHE` — kenar önbelleği, TTL'li; (b) **SingleFlight DO** —
`scope_key` başına tek-uçuş (cache stampede önleme: eşzamanlı özdeş çağrılar tek upstream'e
birleşir); (c) **Ledger DO** — `Mcp-Session-Id` başına çağrı sayaçları (`single_shot_enforced`
kanıtı); (d) **proxy çekirdeği** — JSON-RPC yönlendirme + SSE→JSON çözümleme.

---

## 1. Ön Koşullar

```bash
node --version    # >= 20
npm --version
npx wrangler --version   # >= 4 ; yoksa: npm i -g wrangler
npx wrangler login       # Cloudflare hesabına giriş (cureonics hesabı)
```

Ajan ayrıca şu iki bilgiyi hazır tutmalı:

- **Upstream MCP URL:** `https://titck-origin.cureonics.com/mcp`
- **Upstream auth:** Bilinmiyor. **Varsayılan: kimliksiz dene.** Smoke testte 401/403 alınırsa
  (S13) `UPSTREAM_AUTH_HEADER` secret'ı eklenir. Kullanıcıdan teyit iste.

---

## 2. Adım S0 — Proje iskeleti

**Amaç:** Boş bir TypeScript Worker projesi.

```bash
mkdir titck-cache-mcp && cd titck-cache-mcp
npm init -y
npm i -D wrangler typescript @cloudflare/vitest-pool-workers vitest @cloudflare/workers-types
mkdir -p src test
```

`package.json` içine script'leri ekle:

```json
{
  "name": "titck-cache-mcp",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "test": "vitest run",
    "types": "wrangler types"
  }
}
```

**✅ Kabul kontrolü:** `ls package.json src test` üç yolu da listeler; `npm ls wrangler` sürüm gösterir.

---

## 3. Adım S1 — `tsconfig.json`

`tsconfig.json` oluştur:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "lib": ["ES2022"],
    "types": ["@cloudflare/workers-types", "@cloudflare/vitest-pool-workers"],
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "isolatedModules": true
  },
  "include": ["src/**/*.ts", "test/**/*.ts", "worker-configuration.d.ts"]
}
```

**✅ Kabul kontrolü:** `npx tsc --noEmit` hatasız döner (henüz kaynak yok; yalnız config geçerliliği).

---

## 4. Adım S2 — `wrangler.jsonc` (binding'ler)

`wrangler.jsonc` oluştur. **`<KV_ID>` bir sonraki adımda doldurulacak** — şimdilik bırak.

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "titck-cache-mcp",
  "main": "src/index.ts",
  "compatibility_date": "2025-06-01",
  "compatibility_flags": ["nodejs_compat"],
  "observability": { "enabled": true },

  "vars": {
    "UPSTREAM_MCP_URL": "https://titck-origin.cureonics.com/mcp",
    "CACHE_NAMESPACE": "tc:v1",
    "DEFAULT_TTL_SECONDS": "86400"
  },

  "kv_namespaces": [
    { "binding": "TITCK_CACHE", "id": "<KV_ID>" }
  ],

  "durable_objects": {
    "bindings": [
      { "name": "SINGLEFLIGHT", "class_name": "SingleFlight" },
      { "name": "LEDGER", "class_name": "Ledger" }
    ]
  },

  "migrations": [
    { "tag": "v1", "new_sqlite_classes": ["SingleFlight", "Ledger"] }
  ]
}
```

> **Not (`.toml` tercih edenler için):** Aynı yapı `wrangler.toml` ile de ifade edilebilir;
> `[[kv_namespaces]]`, `[[durable_objects.bindings]]`, `[[migrations]]` blokları. Yeni DO'lar
> için `new_sqlite_classes` zorunlu (SQLite-destekli depolama; Free planda kullanılabilir).

**✅ Kabul kontrolü:** Dosya geçerli JSONC; `node -e "JSON.parse(require('fs').readFileSync('wrangler.jsonc','utf8').replace(/\/\/.*$/gm,''))"` hatasız.

---

## 5. Adım S3 — KV namespace oluştur ve `id` yaz

```bash
npx wrangler kv namespace create TITCK_CACHE
```

Komutun döndürdüğü `id` değerini `wrangler.jsonc` içindeki `<KV_ID>` yerine yapıştır.

**✅ Kabul kontrolü:** `npx wrangler kv namespace list` çıktısında `TITCK_CACHE` görünür; `wrangler.jsonc`'de `<KV_ID>` kalmadı (`grep -c '<KV_ID>' wrangler.jsonc` = 0).

---

## 6. Adım S4 — Tip üretimi

```bash
npx wrangler types
```

Bu, `worker-configuration.d.ts` üretir (Env arayüzü: `TITCK_CACHE`, `SINGLEFLIGHT`, `LEDGER`,
`UPSTREAM_MCP_URL`, `CACHE_NAMESPACE`, `DEFAULT_TTL_SECONDS`, opsiyonel `UPSTREAM_AUTH_HEADER`).

**✅ Kabul kontrolü:** `worker-configuration.d.ts` mevcut ve içinde `TITCK_CACHE` + `SINGLEFLIGHT` + `LEDGER` geçiyor.

---

## 7. Adım S5 — `src/hash.ts` (kanonikleştirme + `scope_key`)

**Amaç:** Aynı semantik çağrının aynı anahtara eşlendiği, deterministik, içerik-adresli anahtar.
Bu, `canonical-cache-contract.md §2` ile hizalıdır.

`src/hash.ts`:

```ts
// Deterministik kanonik JSON: nesne anahtarlarını özyinelemeli sırala,
// string'leri Unicode NFC ile normalize et + trim. Sayı/boolean/null aynen.
// DİKKAT: Güvenli tarafta kal — büyük/küçük harf DÖNÜŞTÜRME yapma (TİTCK alanları
// büyük/küçük harfe duyarlı olabilir). Yalnız boşluk + Unicode normalizasyonu.
export function canonicalize(value: unknown): unknown {
  if (value === null || typeof value !== "object") {
    if (typeof value === "string") return value.normalize("NFC").trim();
    return value;
  }
  if (Array.isArray(value)) return value.map(canonicalize);
  const obj = value as Record<string, unknown>;
  const out: Record<string, unknown> = {};
  for (const k of Object.keys(obj).sort()) out[k] = canonicalize(obj[k]);
  return out;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(canonicalize(value));
}

async function sha256Hex(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// scope_key = <namespace>:<sha256(tool + '\u0000' + canonicalJson(args))>
export async function scopeKey(
  namespace: string,
  tool: string,
  args: unknown,
): Promise<string> {
  const material = `${tool}\u0000${canonicalJson(args ?? {})}`;
  return `${namespace}:${await sha256Hex(material)}`;
}
```

`test/hash.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { canonicalJson, scopeKey } from "../src/hash";

describe("kanonikleştirme", () => {
  it("anahtar sırasından bağımsızdır", () => {
    expect(canonicalJson({ b: 1, a: 2 })).toBe(canonicalJson({ a: 2, b: 1 }));
  });
  it("aynı çağrı aynı scope_key üretir", async () => {
    const k1 = await scopeKey("tc:v1", "get_drug", { barcode: "8699", lang: "tr" });
    const k2 = await scopeKey("tc:v1", "get_drug", { lang: "tr", barcode: "8699" });
    expect(k1).toBe(k2);
  });
  it("farklı argüman farklı anahtar üretir", async () => {
    const k1 = await scopeKey("tc:v1", "get_drug", { barcode: "8699" });
    const k2 = await scopeKey("tc:v1", "get_drug", { barcode: "8700" });
    expect(k1).not.toBe(k2);
  });
});
```

**✅ Kabul kontrolü:** `npx vitest run test/hash.test.ts` → 3 test geçer.

---

## 8. Adım S6 — `src/policy.ts` (önbelleklenebilir araçlar + TTL)

**Amaç:** TİTCK araçlarının tümü salt-okunur/idempotenttir (`idempotentHint: true`). Hepsini
önbellekle; tazelik-kritik sınıflara daha kısa TTL ver.

`src/policy.ts`:

```ts
// TİTCK MCP tüm araçları read-only. Prefiks → TTL (saniye) politikası.
// Fiyat ve geri-çekme verisi daha sık değişir → kısa TTL.
const TTL_OVERRIDES: { match: (t: string) => boolean; ttl: number }[] = [
  // Geri çekme / satış blokajı — güvenlik-kritik tazelik
  { match: (t) => t.includes("recall") || t.includes("cancellation"), ttl: 3600 },          // 1 saat
  // Fiyat verisi — periyodik tebliğlerle değişir
  { match: (t) => t.includes("price"), ttl: 6 * 3600 },                                      // 6 saat
  // Takvimlendirme / ek izleme — orta tazelik
  { match: (t) => t.includes("scheduling") || t.includes("monitoring"), ttl: 12 * 3600 },    // 12 saat
];

// Önbelleklenmeyecek araçlar (TİTCK'te yok; gelecekte non-idempotent araç eklenirse buraya).
const NON_CACHEABLE = new Set<string>([]);

export function isCacheable(tool: string): boolean {
  if (NON_CACHEABLE.has(tool)) return false;
  // TİTCK araç adları search_/get_/find_/list_/compare_/summarize_/server_info ile başlar.
  return /^(search_|get_|find_|list_|compare_|summarize_|server_info)/.test(tool);
}

export function ttlFor(tool: string, defaultTtl: number): number {
  for (const o of TTL_OVERRIDES) if (o.match(tool)) return o.ttl;
  return defaultTtl;
}
```

`test/policy.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { isCacheable, ttlFor } from "../src/policy";

describe("önbellek politikası", () => {
  it("okuma araçlarını önbellekler", () => {
    expect(isCacheable("get_drug")).toBe(true);
    expect(isCacheable("search_drugs")).toBe(true);
    expect(isCacheable("find_equivalent_products_by_substance")).toBe(true);
  });
  it("fiyat araçlarına kısa TTL verir", () => {
    expect(ttlFor("get_price_history", 86400)).toBe(6 * 3600);
    expect(ttlFor("search_recalls", 86400)).toBe(3600);
    expect(ttlFor("get_drug", 86400)).toBe(86400);
  });
});
```

**✅ Kabul kontrolü:** `npx vitest run test/policy.test.ts` → tüm testler geçer.

---

## 9. Adım S7 — `src/mcp.ts` (JSON-RPC + SSE yardımcıları)

**Amaç:** Upstream cevabı JSON ya da SSE (`text/event-stream`) olabilir. Önbelleklenecek araç
çağrısında JSON-RPC `result`'ını güvenilir biçimde çıkar.

`src/mcp.ts`:

```ts
export interface JsonRpcMsg {
  jsonrpc: "2.0";
  id?: string | number | null;
  method?: string;
  params?: { name?: string; arguments?: unknown; [k: string]: unknown };
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

// Upstream gövdesinden JSON-RPC mesajını çıkar (JSON veya SSE).
export function parseRpcFromBody(text: string, contentType: string): JsonRpcMsg | null {
  const ct = (contentType || "").toLowerCase();
  if (ct.includes("text/event-stream")) {
    // SSE: 'data:' satırlarını topla; sonuncu geçerli JSON-RPC nesnesini al.
    let last: JsonRpcMsg | null = null;
    for (const line of text.split(/\r?\n/)) {
      const m = line.match(/^data:\s?(.*)$/);
      if (!m) continue;
      try {
        const obj = JSON.parse(m[1]) as JsonRpcMsg;
        if (obj && (("result" in obj) || ("error" in obj))) last = obj;
      } catch { /* yoksay */ }
    }
    return last;
  }
  try { return JSON.parse(text) as JsonRpcMsg; } catch { return null; }
}

// Önbellekten dönerken: result'ı çağrının KENDİ id'siyle yeniden zarfla.
export function buildResultResponse(
  result: unknown,
  id: JsonRpcMsg["id"],
  cacheOutcome: "HIT" | "MISS" | "COALESCED",
  scopeKeyVal: string,
): Response {
  const body = JSON.stringify({ jsonrpc: "2.0", id: id ?? null, result });
  return new Response(body, {
    status: 200,
    headers: {
      "content-type": "application/json",
      "x-titck-cache": cacheOutcome,
      "x-titck-scope-key": scopeKeyVal,
      ...corsHeaders(),
    },
  });
}

export function corsHeaders(): Record<string, string> {
  return {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, POST, DELETE, OPTIONS",
    "access-control-allow-headers": "content-type, mcp-session-id, mcp-protocol-version, authorization",
    "access-control-expose-headers": "mcp-session-id, x-titck-cache, x-titck-scope-key",
  };
}

// İstemciden upstream'e iletilecek başlıklar (cacheable çağrı için JSON tercih et ama SSE'yi kabul et).
export function forwardHeaders(req: Request, authHeader?: string): Headers {
  const h = new Headers();
  h.set("content-type", "application/json");
  h.set("accept", "application/json, text/event-stream");
  const proto = req.headers.get("mcp-protocol-version");
  if (proto) h.set("mcp-protocol-version", proto);
  const sess = req.headers.get("mcp-session-id");
  if (sess) h.set("mcp-session-id", sess);
  if (authHeader) h.set("authorization", authHeader);
  return h;
}
```

**✅ Kabul kontrolü:** `npx tsc --noEmit` hatasız.

---

## 10. Adım S8 — `src/singleflight.ts` (SingleFlight Durable Object)

**Amaç:** `scope_key` başına **tek upstream çağrısı** — eşzamanlı özdeş istekler tek fetch'e
birleşir (cache stampede önleme). DO tek-iş-parçacıklı olduğundan aynı anahtara gelen istekler
seri işlenir; ilki upstream'i vurur, sonrakiler taze sonucu görür.

`src/singleflight.ts`:

```ts
import { DurableObject } from "cloudflare:workers";
import { parseRpcFromBody, type JsonRpcMsg } from "./mcp";

interface FetchOnceArgs {
  upstreamUrl: string;
  headers: Record<string, string>;
  body: string;
  key: string;
  ttl: number;
}
type FetchOnceResult =
  | { outcome: "MISS" | "COALESCED"; kind: "result"; result: unknown }
  | { outcome: "MISS"; kind: "error"; error: JsonRpcMsg["error"] }
  | { outcome: "MISS"; kind: "unparseable"; raw: string; contentType: string };

export class SingleFlight extends DurableObject<Env> {
  // RPC: Worker MISS'te çağırır. Aynı DO id'sine eşzamanlı çağrılar seri işlenir.
  async fetchOnce(a: FetchOnceArgs): Promise<FetchOnceResult> {
    // 1) DO içi taze giriş var mı? (eşzamanlı çağrı birleşmesi)
    const cached = await this.ctx.storage.get<{ result: unknown; exp: number }>("r");
    if (cached && cached.exp > Date.now()) {
      return { outcome: "COALESCED", kind: "result", result: cached.result };
    }
    // 2) Upstream'i BİR kez vur.
    const resp = await fetch(a.upstreamUrl, { method: "POST", headers: a.headers, body: a.body });
    const text = await resp.text();
    const rpc = parseRpcFromBody(text, resp.headers.get("content-type") || "");

    if (rpc && "result" in rpc && rpc.result !== undefined) {
      // Başarılı sonucu hem DO'da (kısa) hem KV'de (TTL) sakla.
      const exp = Date.now() + a.ttl * 1000;
      await this.ctx.storage.put("r", { result: rpc.result, exp });
      await this.ctx.storage.setAlarm(exp); // süre dolunca DO girdisini temizle
      await this.env.TITCK_CACHE.put(a.key, JSON.stringify(rpc.result), { expirationTtl: a.ttl });
      return { outcome: "MISS", kind: "result", result: rpc.result };
    }
    if (rpc && rpc.error) {
      // Hataları ÖNBELLEKLEME (geçici olabilir).
      return { outcome: "MISS", kind: "error", error: rpc.error };
    }
    return { outcome: "MISS", kind: "unparseable", raw: text, contentType: resp.headers.get("content-type") || "" };
  }

  // Süre dolunca DO içi girdiyi temizle (KV kendi TTL'i ile düşer).
  async alarm() {
    await this.ctx.storage.delete("r");
  }
}
```

**✅ Kabul kontrolü:** `npx tsc --noEmit` hatasız; `SingleFlight` sınıfı dışa aktarılıyor.

---

## 11. Adım S9 — `src/ledger.ts` (Ledger Durable Object)

**Amaç:** `Mcp-Session-Id` başına çağrı sayaçları — `single_shot_enforced` kanıtı. Değişmez:
**her benzersiz scope için upstream çağrısı ≤ 1.** Ledger, oturumda görülen *benzersiz scope*
sayısı ile *upstream MISS* sayısını izler; `single_shot_enforced = (upstream_calls ≤ distinct_scopes)`.

`src/ledger.ts`:

```ts
import { DurableObject } from "cloudflare:workers";

type Outcome = "HIT" | "MISS" | "COALESCED";

export class Ledger extends DurableObject<Env> {
  async record(tool: string, outcome: Outcome, scopeKeyVal: string): Promise<void> {
    const tools = (await this.ctx.storage.get<Record<string, { hit: number; miss: number; coalesced: number }>>("tools")) ?? {};
    const scopes = (await this.ctx.storage.get<Record<string, number>>("scopes")) ?? {};
    const t = tools[tool] ?? { hit: 0, miss: 0, coalesced: 0 };
    if (outcome === "HIT") t.hit++;
    else if (outcome === "MISS") t.miss++;
    else t.coalesced++;
    tools[tool] = t;
    scopes[scopeKeyVal] = (scopes[scopeKeyVal] ?? 0) + 1;
    await this.ctx.storage.put("tools", tools);
    await this.ctx.storage.put("scopes", scopes);
  }

  async report(): Promise<unknown> {
    const tools = (await this.ctx.storage.get<Record<string, { hit: number; miss: number; coalesced: number }>>("tools")) ?? {};
    const scopes = (await this.ctx.storage.get<Record<string, number>>("scopes")) ?? {};
    const distinctScopes = Object.keys(scopes).length;
    const upstreamCalls = Object.values(tools).reduce((s, t) => s + t.miss, 0);
    return {
      tools,
      distinct_scopes: distinctScopes,
      upstream_calls: upstreamCalls,
      // R1 değişmezi: hiçbir benzersiz scope ikinci kez upstream'e gitmedi.
      single_shot_enforced: upstreamCalls <= distinctScopes,
    };
  }
}
```

**✅ Kabul kontrolü:** `npx tsc --noEmit` hatasız; `Ledger` sınıfı dışa aktarılıyor.

---

## 12. Adım S10 — `src/index.ts` (proxy çekirdeği)

**Amaç:** MCP isteklerini yönlendir. Cacheable `tools/call` → KV → SingleFlight DO; diğer her şey
→ şeffaf relay. Gözlemlenebilirlik uçları: `/health`, `/ledger`, `/purge`.

`src/index.ts`:

```ts
import { SingleFlight } from "./singleflight";
import { Ledger } from "./ledger";
import { scopeKey } from "./hash";
import { isCacheable, ttlFor } from "./policy";
import {
  buildResultResponse, corsHeaders, forwardHeaders, parseRpcFromBody, type JsonRpcMsg,
} from "./mcp";

export { SingleFlight, Ledger };

async function recordLedger(env: Env, sessionId: string, tool: string, outcome: "HIT" | "MISS" | "COALESCED", key: string) {
  const id = env.LEDGER.idFromName(sessionId);
  await env.LEDGER.get(id).record(tool, outcome, key);
}

// Şeffaf relay: gövdeyi ve başlıkları upstream'e ilet, cevabı aynen döndür (SSE dahil).
async function relay(req: Request, env: Env, rawBody?: string): Promise<Response> {
  const headers = new Headers(req.headers);
  headers.delete("host");
  if (env.UPSTREAM_AUTH_HEADER) headers.set("authorization", env.UPSTREAM_AUTH_HEADER);
  const init: RequestInit = { method: req.method, headers };
  if (req.method !== "GET" && req.method !== "HEAD") init.body = rawBody ?? (await req.text());
  const up = await fetch(env.UPSTREAM_MCP_URL, init);
  const outHeaders = new Headers(up.headers);
  for (const [k, v] of Object.entries(corsHeaders())) outHeaders.set(k, v);
  return new Response(up.body, { status: up.status, headers: outHeaders });
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);

    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders() });

    if (url.pathname === "/health") {
      return Response.json({ ok: true, upstream: env.UPSTREAM_MCP_URL, ns: env.CACHE_NAMESPACE });
    }
    if (url.pathname === "/ledger") {
      const session = url.searchParams.get("session") ?? "no-session";
      const rep = await env.LEDGER.get(env.LEDGER.idFromName(session)).report();
      return Response.json({ session, ...(rep as object) });
    }
    if (url.pathname === "/purge" && req.method === "POST") {
      // Korumalı: PURGE_TOKEN secret'ı ile. Tek bir scope_key veya tüm namespace temizliği.
      if (!env.PURGE_TOKEN || req.headers.get("x-purge-token") !== env.PURGE_TOKEN)
        return new Response("forbidden", { status: 403 });
      const key = url.searchParams.get("key");
      if (key) { await env.TITCK_CACHE.delete(key); return Response.json({ purged: key }); }
      return Response.json({ note: "tüm-namespace temizliği için CACHE_NAMESPACE sürümünü artırın (tc:v2)" });
    }

    // MCP uç noktası — yalnız POST gövdesini denetle; GET/DELETE şeffaf relay.
    if (req.method !== "POST") return relay(req, env);

    const rawBody = await req.text();
    let msg: JsonRpcMsg | JsonRpcMsg[];
    try { msg = JSON.parse(rawBody); } catch { return relay(req, env, rawBody); }

    // Batch (dizi) → önbelleksiz şeffaf relay.
    if (Array.isArray(msg)) return relay(req, env, rawBody);

    const sessionId = req.headers.get("mcp-session-id") ?? "no-session";

    if (msg.method === "tools/call" && msg.params?.name) {
      const tool = msg.params.name;
      const args = msg.params.arguments ?? {};
      if (isCacheable(tool)) {
        const key = await scopeKey(env.CACHE_NAMESPACE, tool, args);

        // 1) KV kenar önbelleği
        const cached = await env.TITCK_CACHE.get(key, "text");
        if (cached !== null) {
          await recordLedger(env, sessionId, tool, "HIT", key);
          return buildResultResponse(JSON.parse(cached), msg.id, "HIT", key);
        }

        // 2) MISS → SingleFlight DO (scope_key başına tekil)
        const ttl = ttlFor(tool, Number(env.DEFAULT_TTL_SECONDS || "86400"));
        const headers = Object.fromEntries(forwardHeaders(req, env.UPSTREAM_AUTH_HEADER).entries());
        const stub = env.SINGLEFLIGHT.get(env.SINGLEFLIGHT.idFromName(key));
        const r = await stub.fetchOnce({ upstreamUrl: env.UPSTREAM_MCP_URL, headers, body: rawBody, key, ttl });

        if (r.kind === "result") {
          await recordLedger(env, sessionId, tool, r.outcome, key);
          return buildResultResponse(r.result, msg.id, r.outcome, key);
        }
        if (r.kind === "error") {
          await recordLedger(env, sessionId, tool, "MISS", key);
          return Response.json({ jsonrpc: "2.0", id: msg.id ?? null, error: r.error }, { headers: { "x-titck-cache": "MISS-ERROR", ...corsHeaders() } });
        }
        // Çözümlenemeyen upstream cevabı → ham relay (önbelleklenmedi).
        await recordLedger(env, sessionId, tool, "MISS", key);
        return new Response(r.raw, { status: 200, headers: { "content-type": r.contentType || "application/json", "x-titck-cache": "MISS-PASSTHROUGH", ...corsHeaders() } });
      }
    }

    // initialize / tools/list / notifications / diğer → şeffaf relay
    return relay(req, env, rawBody);
  },
} satisfies ExportedHandler<Env>;
```

> **`tools/list` notu (opsiyonel iyileştirme):** Üst düzey araç listesi nadiren değişir.
> İstenirse `tools/list` cevabı da KV'de uzun TTL ile önbelleklenebilir; ancak `initialize`
> oturum başlığı (`Mcp-Session-Id`) relay'inin bozulmaması için ilk sürümde `tools/list`'i
> **şeffaf relay** bırak. Determinizm hedefi yalnız `tools/call` önb1eklemesiyle karşılanır.

**✅ Kabul kontrolü:** `npx tsc --noEmit` hatasız; `src/index.ts` `SingleFlight` ve `Ledger`'ı yeniden dışa aktarıyor (DO sınıfları Worker girişinden export edilmeli).

---

## 13. Adım S11 — Yerel test: **kabul senaryosu** (iki özdeş çağrı → tek upstream)

**Amaç:** R1'in deterministik kanıtı. `@cloudflare/vitest-pool-workers` + `fetchMock` ile
upstream'i taklit et; iki özdeş `tools/call` gönder; upstream'in **tam bir kez** çağrıldığını ve
ikinci cevabın `x-titck-cache: HIT` taşıdığını doğrula.

`vitest.config.ts`:

```ts
import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";
export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: { wrangler: { configPath: "./wrangler.jsonc" } },
    },
  },
});
```

`test/proxy.test.ts`:

```ts
import { env, fetchMock } from "cloudflare:test";
import { beforeAll, afterEach, describe, it, expect } from "vitest";
import worker from "../src/index";

const UP = new URL(env.UPSTREAM_MCP_URL);

function call(id: number) {
  return new Request("https://x/mcp", {
    method: "POST",
    headers: { "content-type": "application/json", "mcp-session-id": "S1" },
    body: JSON.stringify({
      jsonrpc: "2.0", id, method: "tools/call",
      params: { name: "get_drug", arguments: { barcode: "8699000000000" } },
    }),
  });
}

beforeAll(() => fetchMock.activate());
afterEach(() => fetchMock.assertNoPendingInterceptors());

describe("tek-sefer TİTCK (R1)", () => {
  it("iki özdeş çağrıda upstream BİR kez vurulur; ikinci HIT döner", async () => {
    // Upstream yalnız BİR kez yanıtlamaya hazır (times: 1). İkinci kez vurulursa test patlar.
    fetchMock.get(UP.origin).intercept({ path: UP.pathname, method: "POST" }).reply(
      200,
      JSON.stringify({ jsonrpc: "2.0", id: 1, result: { drug: { barcode: "8699000000000", name: "TEST" } } }),
      { headers: { "content-type": "application/json" } },
    ).times(1);

    const r1 = await worker.fetch(call(1), env);
    const j1 = await r1.json();
    expect(r1.headers.get("x-titck-cache")).toBe("MISS");
    expect((j1 as any).result.drug.name).toBe("TEST");

    const r2 = await worker.fetch(call(2), env);
    const j2 = await r2.json();
    expect(r2.headers.get("x-titck-cache")).toBe("HIT");      // upstream'e GİTMEDİ
    expect((j2 as any).id).toBe(2);                            // id yeniden zarflandı
    expect((j2 as any).result.drug.name).toBe("TEST");
  });

  it("ledger single_shot_enforced=true raporlar", async () => {
    const rep = await env.LEDGER.get(env.LEDGER.idFromName("S1")).report();
    expect((rep as any).single_shot_enforced).toBe(true);
    expect((rep as any).upstream_calls).toBeLessThanOrEqual((rep as any).distinct_scopes);
  });
});
```

```bash
npx vitest run
```

**✅ Kabul kontrolü:** Tüm testler geçer. Özellikle: (a) `fetchMock` interceptor `times(1)` ile
tanımlı olduğundan ikinci çağrı upstream'i vursaydı `assertNoPendingInterceptors`/eşleşme hatası
verirdi → **upstream tam bir kez** vuruldu; (b) ikinci cevap `x-titck-cache: HIT`; (c)
`single_shot_enforced=true`.

---

## 14. Adım S12 — MCP Inspector ile elle doğrulama (yerel)

```bash
npx wrangler dev        # http://localhost:8787 (ayrı terminal)
npx @modelcontextprotocol/inspector    # tarayıcı arayüzü
```

Inspector'da Transport = **Streamable HTTP**, URL = `http://localhost:8787` (ya da `/mcp`).
`initialize` → `tools/list` (TİTCK araçları görünmeli, relay çalışıyor) → bir `tools/call`
(`get_drug`) iki kez çalıştır; ikinci yanıtın başlıklarında `x-titck-cache: HIT` olmalı.

**✅ Kabul kontrolü:** `tools/list` upstream araçlarını döndürür; aynı `get_drug` çağrısı ikinci
seferde `HIT`; `GET http://localhost:8787/ledger?session=...` `single_shot_enforced: true` döner.

---

## 15. Adım S13 — Secrets ve dağıtım

```bash
# Upstream kimliksiz çalışmıyorsa (S14 smoke'ta 401/403 alınırsa):
# echo "Bearer <token>" | npx wrangler secret put UPSTREAM_AUTH_HEADER
# Purge ucu koruması:
npx wrangler secret put PURGE_TOKEN          # rastgele güçlü değer

npx wrangler deploy
```

**✅ Kabul kontrolü:** Dağıtım URL'i basılır (ör. `https://titck.cureonics.com`).
`npx wrangler deployments list` son dağıtımı gösterir.

---

## 16. Adım S14 — Canlı smoke test

```bash
BASE=https://titck.cureonics.com

# 1) sağlık
curl -s $BASE/health | jq .

# 2) initialize (oturum başlat) — Mcp-Session-Id cevabı relay edilmeli
curl -si -X POST $BASE/mcp \
  -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"1"}}}' | sed -n '1,15p'

# 3) aynı tools/call'u iki kez — ikinci HIT olmalı
REQ='{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_drug","arguments":{"barcode":"8699000000000"}}}'
curl -s -X POST $BASE/mcp -H 'content-type: application/json' -H 'mcp-session-id: SMOKE' -H 'accept: application/json, text/event-stream' -d "$REQ" -D - -o /dev/null | grep -i x-titck-cache   # → MISS
curl -s -X POST $BASE/mcp -H 'content-type: application/json' -H 'mcp-session-id: SMOKE' -H 'accept: application/json, text/event-stream' -d "$REQ" -D - -o /dev/null | grep -i x-titck-cache   # → HIT

# 4) ledger kanıtı
curl -s "$BASE/ledger?session=SMOKE" | jq .
```

**✅ Kabul kontrolü:** (2) 401/403 değil (alındıysa S13 auth secret'ını ekle, yeniden deploy);
(3) birinci `MISS`, ikinci `HIT`; (4) `single_shot_enforced: true`.

---

## 17. Adım S15 — Claude / rxpraxis'e bağlama ve sözleşme güncellemesi

**Amaç:** rxpraxis'i ham TİTCK MCP yerine bu önbellekleyen proxy'ye yönlendir.

1. **Claude.ai connector'ı:** TİTCK connector URL'ini
   `https://titck.cureonics.com/mcp` olarak değiştir (ham Cloud Run URL'i yerine).
   Araç yüzeyi aynıdır (şeffaf proxy), bu yüzden skill'lerde başka değişiklik gerekmez.

2. **`CONNECTORS.md §3` güncellemesi (rxpraxis):** "Tek-sefer TİTCK kuralı"nın artık **kod-düzeyi
   garanti** olduğunu yansıt. Şu cümleyi §3'e ekle:

   > **v1.1 (kod-düzeyi zorlama):** Tek-sefer TİTCK kuralı artık `titck-cache-mcp` Worker'ı
   > tarafından deterministik olarak uygulanır: `scope_key = sha256(tool + canonical(args))`
   > başına upstream çağrısı ≤ 1 (SingleFlight DO + KV TTL). `single_shot_enforced` artık model
   > beyanı değil, Worker `/ledger` ucundan **ölçülebilir** bir değişmezdir.

3. **`run-manifest-schema.json` (rxpraxis):** `connector_call_ledger.titck_mcp` altına
   `ledger_endpoint` ve `verified_by_worker: boolean` alanları ekle; rapor üretiminde
   `GET /ledger?session=<Mcp-Session-Id>` çıktısı buraya işlenir (gerçek kanıt).

4. **`BUILD.md §4 R1` güncellemesi:** R1 azaltımını "disiplin" → "kod-düzeyi deterministik
   garanti (v1.1 dağıtıldı)" olarak yükselt; §7 v1.1 maddesini "tamamlandı" işaretle.

**✅ Kabul kontrolü:** rxpraxis tam tarama (`/rxpraxis-scan`) sırasında, raporun
`connector_call_ledger` bölümü `verified_by_worker: true` ve `/ledger` çıktısıyla tutarlı
`single_shot_enforced: true` taşır; aynı molekül için ikinci skill çağrısı upstream'i vurmaz.

---

## 18. Tamamlanma Tanımı (Definition of Done)

Aşağıdakilerin **tümü** sağlanmalı:

- [ ] `npx tsc --noEmit` ve `npx vitest run` tamamen yeşil (hash, policy, proxy testleri).
- [ ] Kabul senaryosu (S11): iki özdeş `tools/call` → upstream **bir kez** + ikinci `HIT`.
- [ ] `/health`, `/ledger`, `/purge` uçları çalışır; `single_shot_enforced` ledger'dan okunur.
- [ ] Canlı smoke (S14): `initialize` relay, `tools/list` upstream araçlarını döndürür, fiyat
      araçları kısa TTL (politika) ile davranır.
- [ ] rxpraxis connector'ı proxy'ye yönlendirilmiş; `CONNECTORS.md §3`, `run-manifest-schema.json`,
      `BUILD.md §4/§7` güncellenmiş.
- [ ] `wrangler deploy` ile `titck.cureonics.com` yayında.

---

## 19. Sınırlılıklar ve Sonraki Sürüm Notları

- **KV tutarlılığı:** KV nihai-tutarlıdır (eventually consistent); kenarlar arası yazma yayılımı
  saniyeler alabilir. Eşzamanlı *farklı kenarlardan* gelen ilk iki istek nadiren iki upstream
  çağrısı üretebilir; **SingleFlight DO** bunu tek bir küresel noktada birleştirerek
  determinizmi güçlendirir (DO, anahtar başına tekil ve küreseldir). KV yalnız hızlı ikinci-kat
  önbellektir.
- **TTL eskimesi:** Fiyat/geri-çekme verisinde tazelik-kritik durumlar için TTL politikası
  (S6) ayarlanabilir; acil tazeleme için `POST /purge?key=<scope_key>`.
- **Batch & SSE araç çağrıları:** İlk sürüm batch (dizi) ve çözümlenemeyen SSE araç cevaplarını
  **önbeklemeden** şeffaf relay eder (güvenli varsayılan). TİTCK okuma araçları tekil JSON
  döndürdüğü için pratikte tüm hedef çağrılar önbeklenir.
- **Oturum eşlemesi:** `initialize`/`Mcp-Session-Id` şeffaf relay edilir; proxy oturum durumu
  tutmaz (stateless tasarım — mcp-builder önerisiyle uyumlu). Upstream katı oturum-bağlama
  uygularsa, gelecek sürümde istemci↔upstream oturum eşleme tablosu (KV/DO) eklenebilir.
- **`tools/list` önbeklemesi:** Opsiyonel; determinizm için gerekli değil (S12 notu).

---

## 20. AI Ajanına Özet Yürütme Talimatı

> Adımları **S0→S15** sırasıyla uygula. Her adımda verilen dosyaları birebir oluştur, komutları
> çalıştır, **`✅ Kabul kontrolü`**'nü doğrula. Bir kontrol başarısızsa o adımda kal, düzelt,
> yeniden dene. S13'te upstream 401/403 dönerse kullanıcıdan auth bilgisini iste. Bitince **§18
> Tamamlanma Tanımı**'ndaki tüm kutuları işaretle ve `/ledger` çıktısını (`single_shot_enforced:
> true`) kanıt olarak raporla. Mimari kararları değiştirme; yalnız eksik teknik ayrıntıları
> (ör. Cloudflare hesap kimliği, KV id) ortamdan/kullanıcıdan tamamla.
