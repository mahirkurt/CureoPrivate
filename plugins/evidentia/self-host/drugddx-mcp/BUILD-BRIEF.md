# drugddx-mcp — Kurulum Talimatnamesi (Build Brief)

> **Aile A** (Cloudflare Worker + Durable Object + sertleştirilmiş OAuth 2.1). Bu talimatname,
> `mcp-scout` `self-host-build.md` §12 şablonunu izler. Kod iskeleti `src/`, `test/`,
> `wrangler.jsonc` içinde hazırdır; bu belge **deploy adımlarını** ve **kabul kriterlerini**
> (DoD) tanımlar.

---

## §0 — Doldurulacaklar

| Alan | Değer |
|---|---|
| slug | `drugddx-mcp` |
| URL (deploy sonrası) | `https://drugddx-mcp.<subdomain>.workers.dev/mcp` (operatör tercihi: `https://drugddx-mcp.cureonics.workers.dev/mcp`) |
| DO sınıfı / binding | `DrugDdx` / `MCP_OBJECT` |
| Secret 1 | `MCP_API_KEY` (64-hex) — gerçek Bearer kapısı |
| Secret 2 | `AUTH_HMAC_SECRET` (32-hex) — auth-code imzası |
| Non-secret var | `MCP_ALLOW_NO_AUTH="0"`, `OAUTH_ALLOWED_REDIRECT_ORIGINS=""` |

---

## §1 — Aile Gerekçesi

`workerd` alt-süreç başlatamaz (stdio MCP doğrudan koşamaz) → **Aile A**: upstream çağrılar
TypeScript'te yeniden ifade edilir (RxNav + DailyMed keyless REST), durum Durable Object'te
tutulur, remote MCP HTTP/SSE olarak sunulur. Kaynak β-aday `drug-interaction-mcp` canlı probe'da
**HTTP 500** verdi (deployment kırık) → bu Worker o yeteneği kontrollü ve dürüst biçimde ikame eder.

### Ön koşullar
- Node ≥ 18, `npm`.
- Cloudflare hesabı + `wrangler login`.
- (Opsiyonel) `*.cureonics.workers.dev` subdomain'i.

---

## §2 — Kurulum Adımları (S0–S13)

**S0. Bağımlılıklar.**
```bash
cd self-host/drugddx-mcp
npm install
```

**S1. Tip kontrolü (DoD kapısı 1).**
```bash
npx tsc --noEmit
```
Sıfır hata beklenir.

**S2. Testler (DoD kapısı 2).**
```bash
npx vitest run
```
`test/auth.test.ts` (6 değişmez) + `test/routing.test.ts` (router) **yeşil** olmalı.

**S3–S6. Worker iskeleti.** Hazır: `src/index.ts` (router + DO), `src/server.ts` (araç katmanı),
`src/auth.ts` (OAuth 2.1), `wrangler.jsonc` (DO binding + migration + `nodejs_compat`).

**S7. Secret'ları yükle (invariant 6 — koda yazma).**
```bash
# 64-hex ve 32-hex üret (örnek):
openssl rand -hex 32   # -> MCP_API_KEY
openssl rand -hex 16   # -> AUTH_HMAC_SECRET
wrangler secret put MCP_API_KEY
wrangler secret put AUTH_HMAC_SECRET
```

**S8. Deploy.**
```bash
wrangler deploy
```

**S9. Public smoke.**
```bash
BASE=https://drugddx-mcp.<subdomain>.workers.dev MCP_API_KEY=<key> ./scripts/smoke_oauth_public.sh
```
Beklenen: `/health` 200 · AS metadata **S256** (plain YOK) · `/mcp` Bearer'sız **401** ·
Bearer'lı `initialize` **200**.

**S10. claude.ai'ye bağla.** Settings → Connectors → Add custom connector →
`https://drugddx-mcp.<subdomain>.workers.dev/mcp`. OAuth akışı authorize formuna yönlendirir;
MCP API key girilir; PKCE S256 round-trip tamamlanır.

**S11. evidentia roster'ına ekle.** `.mcp.json`'a Tier-O girdisi olarak ekle:
```jsonc
"drugddx": {
  "_tier": "O", "_role": "clinical DDI gap fallback (RxNorm + DailyMed label section)",
  "_trust": "self-host hardened OAuth 2.1",
  "type": "http",
  "url": "https://drugddx-mcp.<subdomain>.workers.dev/mcp",
  "headers": { "Authorization": "Bearer ${DRUGDDX_API_KEY}" }
}
```
Sonra `CONNECTORS.md` §1'e satır ekle ve `python scripts/g_bundle.py` (G-BUNDLE) tekrar koş.

**S12. G-PROBE doğrula.** `python scripts/g_probe.py` — drugddx `🔒401` (auth kapısı aktif) ya da
Bearer ile `200` görünmeli.

**S13. İzleme.** `wrangler tail` ile canlı log; `observability.enabled=true`.

---

## §4 — OAuth Güvenlik Yüzeyi (copy-safe özet)

`src/auth.ts` **altı değişmezi** korur — **gevşetme**:
1. **redirect_uri tam-origin allowlist** (varsayılan `https://claude.ai`, `https://claude.com`).
   Alt-string hilesi (`claude.ai.evil.com`) reddedilir.
2. **PKCE S256-only** — `plain` reddedilir; metadata yalnız S256 ilan eder.
3. **escHtml** — authorize formundaki her yansıtılan parametre kaçışlanır (reflected-XSS kapalı).
4. **HMAC-imzalı auth code + 10 dk TTL** — kurcalama/expired reddedilir.
5. **Sabit-zamanlı secret karşılaştırma** — tüm Bearer/api_key kıyasları.
6. **Secret'lar yalnız secret store'da** — `wrangler secret put`; koda/vars'a asla.

Endpoint'ler: `/.well-known/oauth-protected-resource` (RFC 9728), `/.well-known/oauth-authorization-server`
(RFC 8414, S256), `/oauth/register` (RFC 7591 stub, `none`), `GET+POST /oauth/authorize`,
`POST /oauth/token`.

---

## §5 — Dürüst DDI Sınırı (KRİTİK)

Bu Worker **klinik ikili-DDI motoru DEĞİLDİR**:
- **NLM RxNav Drug Interaction API Ocak 2024'te kapatıldı** — ücretsiz otoriter ikili-etkileşim
  uç noktası artık yok.
- Worker yalnız: (a) `normalize_drug` — INN/marka → RxNorm RxCUI (RxNav `/rxcui`, canlı);
  (b) `interaction_label` — tek ilacın FDA etiketi "Drug Interactions" bölümü (DailyMed SPL,
  LOINC 34073-7) işaretçisi.
- Çıktı **"etiket-türevli etkileşim metni + normalizasyon"** olarak sunulur; **asla** hesaplanmış
  klinik etkileşim hükmü olarak değil. İkili klinik DDI için **lisanslı kaynak** (Lexicomp/
  UpToDate/DrugBank) şarttır. Araç açıklamaları ve her sonuç bu uyarıyı taşır.
- Tüm araçlar **read-only** (`readOnlyHint: true`); upstream keyless public NIH/FDA REST.

---

## DoD (Definition of Done)

- [ ] `npx tsc --noEmit` sıfır hata
- [ ] `npx vitest run` yeşil (auth 6-değişmez + routing)
- [ ] `wrangler deploy` başarılı
- [ ] secret'lar `wrangler secret put` ile yüklendi (kodda YOK)
- [ ] `smoke_oauth_public.sh`: health 200 · S256-only · 401-without-Bearer · 200-authenticated
- [ ] claude.ai custom connector bağlandı, PKCE round-trip tamam
- [ ] `.mcp.json` + `CONNECTORS.md` güncellendi, `g_bundle.py` + `g_probe.py` yeşil

---

*AS IS; no warranty. Cureonics internal-use. Sağlık verisi: araç çıktısı klinik karar değildir;
otoriter kaynakla çapraz-doğrulanır.*
