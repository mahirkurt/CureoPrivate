# drugddx-mcp

Sertleştirilmiş OAuth 2.1 Cloudflare Worker MCP — **RxNorm normalizasyonu + DailyMed etiket
etkileşim-bölümü**. `evidentia` plugin'inin klinik-DDI boşluğu için kontrollü, dürüst fallback'i.

> ⚠️ **Klinik ikili-DDI motoru DEĞİLDİR.** NLM RxNav etkileşim API'si Ocak 2024'te kapandı; bu
> Worker normalizasyon + FDA-etiketi (DailyMed SPL) etkileşim-bölümü metni sağlar. İkili klinik
> etkileşim için lisanslı kaynak (Lexicomp/UpToDate/DrugBank) şarttır.

## Neden var
Registry connector `io.github.guptaprakhariitr/drug-interaction-mcp` canlı probe'da **HTTP 500**
(deployment kırık) verdi. evidentia yeteneği sertleştirilmiş-OAuth Worker olarak fork'lar.

## Hızlı kurulum
```bash
npm install
npx tsc --noEmit          # DoD kapısı 1
npx vitest run            # DoD kapısı 2 (6 güvenlik değişmezi + router)
wrangler secret put MCP_API_KEY        # 64-hex
wrangler secret put AUTH_HMAC_SECRET   # 32-hex
wrangler deploy
BASE=https://drugddx-mcp.<subdomain>.workers.dev MCP_API_KEY=<key> ./scripts/smoke_oauth_public.sh
```
Tam adımlar + güvenlik yüzeyi + DoD: **[BUILD-BRIEF.md](./BUILD-BRIEF.md)**.

## Araçlar (read-only)
- `normalize_drug(name)` → RxNorm RxCUI (RxNav `/rxcui`).
- `interaction_label(name)` → FDA etiketi "Drug Interactions" bölümü (DailyMed SPL, LOINC 34073-7) işaretçisi.

## Güvenlik (6 değişmez)
redirect-origin allowlist · PKCE S256-only · escHtml · HMAC+TTL auth code · constant-time secret
karşılaştırma · secret'lar yalnız `wrangler secret put`. Detay: BUILD-BRIEF.md §4.

## Yapı
```
src/index.ts    router + Durable Object (DrugDdx) + Bearer gate
src/server.ts   araç katmanı (RxNav + DailyMed)
src/auth.ts     OAuth 2.1 yüzeyi (6 değişmez)
test/           auth.test.ts (değişmezler) · routing.test.ts
scripts/        smoke_oauth_public.sh
wrangler.jsonc  DO binding + migration + nodejs_compat
```

*AS IS; no warranty. Cureonics internal-use.*
