# anamnesis-mcp — Kurulum Talimatnamesi (Build Brief)

> Bu Worker, evidentia eklentisinin **bağlam-penceresi taşması** sorununu çözen retrieval
> substratıdır: tam-metin makale/kitap çıktıları (Annas/EuropePMC OA/Paper Search) ham olarak
> bağlama dökülmek yerine **semantik chunk + embed + graph** olarak indekslenir; sorguya yalnız
> sınırlı, provenance-damgalı, graph-temelli kanıt paketi sunulur. Kaynaklar hazır; bu belge
> operatörün **deploy** adımlarını ve Tamamlanma Tanımını (DoD) belirler.

---

## §0 — Doldurulacaklar

| Alan | Değer |
|---|---|
| slug | `anamnesis-mcp` |
| URL (deploy sonrası) | `https://anamnesis-mcp.<subdomain>.workers.dev/mcp` (operatör tercihi: `https://anamnesis-mcp.cureonics.workers.dev/mcp`) |
| DO sınıfı / binding | `Anamnesis` / `MCP_OBJECT` |
| **Vectorize index** | `anamnesis-index` — **1024-d, cosine** (bge-m3 boyutu) |
| **D1 database** | `anamnesis-graph` → `database_id` `wrangler.jsonc`'a yapıştırılır |
| Workers AI binding | `AI` (model `@cf/baai/bge-m3`) |
| Secret 1 | `MCP_API_KEY` (64-hex) — gerçek Bearer kapısı |
| Secret 2 | `AUTH_HMAC_SECRET` (32-hex) — auth-code imzası |
| Non-secret var | `MCP_ALLOW_NO_AUTH="0"`, `OAUTH_ALLOWED_REDIRECT_ORIGINS=""` |

---

## §1 — Aile Gerekçesi & Bu Worker Neden Var

Cureonics Family A (sertleştirilmiş OAuth 2.1 + McpAgent DO + Bearer-gated `/mcp`). `auth.ts`
drugddx ile **birebir aynı 6 invariant**i taşır (REALM dışında değişmez).

**Neden:** `mcp-scout` registry taraması (2026-06-25) hosted, uzak-erişilebilir, sertleştirilmiş
GraphRAG MCP'si bulamadı (`io.github.CSOAI-ORG/rag-knowledge-graph-mcp` yalnız yerel stdio,
üçüncü-taraf). Klinik araştırma verisi için güvenilir bir substrat gerektiğinden — drugddx ile
aynı disiplinle — **self-host** edilir. Araç tasarımı (`index_document`/`rag_query`/
`add_graph_edge`) o registry kaydının şeklini doğrular.

### Ön koşullar
- Node ≥ 18, `npm i`, Cloudflare hesabı + `wrangler login`.
- **Workers AI** (hesapta etkin), **Vectorize** (etkin), **D1** (etkin).

---

## §2 — Kurulum Adımları (S0–S13)

**S0. Bağımlılıklar.**
```bash
cd self-host/anamnesis-mcp && npm install
```

**S1. Tip kontrolü (DoD kapısı 1).**
```bash
npm run typecheck     # tsc --noEmit → 0 hata
```

**S2. Altyapıyı provizyonla (Vectorize + D1) — deploy ÖNCESİ ZORUNLU.**
```bash
# Vectorize index — bge-m3 = 1024 boyut, cosine
npx wrangler vectorize create anamnesis-index --dimensions=1024 --metric=cosine

# D1 graph database — dönen database_id'yi wrangler.jsonc'taki REPLACE_WITH_D1_DATABASE_ID'e yapıştır
npx wrangler d1 create anamnesis-graph
```
> Şema (docs/chunks/nodes/edges tabloları) ilk araç çağrısında `ensureSchema()` ile
> otomatik kurulur — ayrı migration SQL gerekmez. (İsteğe bağlı: `wrangler d1 execute
> anamnesis-graph --command "..."` ile önceden de kurulabilir.)

**S3. Testler (DoD kapısı 2).**
```bash
npm test   # auth (6 invariant) + router + semantik-chunking sınır tespiti + graph helper
```
> Not: `chunk.test.ts` sahte deterministik embedder ile **tam offline** çalışır; D1 graph
> SQL + Vectorize + AI entegrasyonu deploy-sonrası smoke ile doğrulanır (Workers AI/Vectorize
> miniflare'de emüle edilmez). İsteğe bağlı: miniflare D1 ile bir entegrasyon testi eklenebilir.

**S4–S6. Worker iskeleti (hazır).** `src/index.ts` (router + `Anamnesis` DO), `src/server.ts`
(7 araç), `src/embed.ts` (bge-m3 + defansif yanıt normalizasyonu), `src/chunk.ts` (semantik
chunking), `src/rag.ts` (Vectorize + D1 metin deposu), `src/graph.ts` (D1 bilgi grafiği),
`src/auth.ts` (OAuth).

**S7. Secret'ları yükle (invariant 6 — koda yazma).**
```bash
# 64-hex ve 32-hex üret (örnek):
openssl rand -hex 32   # → MCP_API_KEY
openssl rand -hex 16   # → AUTH_HMAC_SECRET
wrangler secret put MCP_API_KEY
wrangler secret put AUTH_HMAC_SECRET
```

**S8. Deploy.**
```bash
wrangler deploy
```

**S9. Public smoke.**
```bash
bash scripts/smoke_oauth_public.sh https://anamnesis-mcp.<subdomain>.workers.dev
```
Beklenen: `/health` 200 · AS metadata **S256** (plain YOK) · `/mcp` Bearer'sız **401** ·
geçerli Bearer ile **200**.

**S10. claude.ai'ye bağla.** Settings → Connectors → Add custom connector →
`https://anamnesis-mcp.<subdomain>.workers.dev/mcp`; MCP API key girilir; PKCE S256 round-trip.

**S11. evidentia roster'ına ekle.** `.mcp.json`'da `__SELF_HOST__anamnesis` placeholder'ını canlı
Tier-O girdisiyle değiştir:
```jsonc
"anamnesis": {
  "type": "http",
  "url": "https://anamnesis-mcp.cureonics.workers.dev/mcp",
  "_tier": "O",
  "_role": "RAG/GraphRAG retrieval substratı — tam-metin ingest + semantic_search + hybrid_query; bağlam-penceresi koruması (shared/canonical-cache-contract.md evidence_index)"
}
```
CONNECTORS.md'deki anamnesis satırının `_probe`'unu da güncelle.

**S12. G-PROBE doğrula.** `python scripts/g_probe.py` — anamnesis `🔒401` (auth kapısı aktif)
beklenir; bu **başarı**dır (güvenli).

**S13. İzleme.** `wrangler tail` ile canlı log; `observability.enabled=true`. İlk gerçek
ingest sonrası `corpus_stats` ile docs/chunks/nodes/edges sayımını teyit et.

---

## §3 — Akış (operatörün ilk doğrulama senaryosu)
1. `ingest_document(text=<EuropePMC OA tam metin>, doc_id=<DOI>, source="EuropePMC OA")` → manifest döner (ham metin DÖNMEZ).
2. `semantic_search(query="emicizumab inhibitor-free efficacy", k=8)` → provenance'lı chunk'lar.
3. (Claude chunk'lardan triple çıkarır →) `upsert_triples([...])` → grafiğe yazılır.
4. `hybrid_query(query=..., seed_entities=["emicizumab"])` → sınırlı, graph-temelli kanıt paketi.

---

## §4 — OAuth Güvenlik Yüzeyi (copy-safe özet)
1. **redirect_uri tam-origin allowlist** (varsayılan `https://claude.ai`, `https://claude.com`).
2. **PKCE S256-only** — `plain` reddedilir; metadata yalnız S256 ilan eder.
3. **escHtml** her yansıtılan parametrede (reflected-XSS kapalı).
4. **Auth code HMAC-imzalı + 10 dk TTL.**
5. **Tüm secret karşılaştırmaları sabit-zaman.**
6. **Secret'lar yalnız secret store'da** (`wrangler secret put`) — kodda/vars'ta asla.

Yüzey: `/.well-known/oauth-protected-resource` (RFC 9728), `/.well-known/oauth-authorization-server`
(RFC 8414, S256), `/oauth/register` (RFC 7591 stub, `none`), `GET+POST /oauth/authorize`,
`POST /oauth/token`.

---

## §5 — Dürüst RAG/GraphRAG Sınırı (KRİTİK — güvenmeden önce oku)

**v1'de SEVK EDİLEN:**
- **Semantik chunking** (bge-m3 embedding cosine sınır tespiti + token-cap; sahte-embedder ile test edilmiş).
- **Vektör RAG** (Vectorize 1024-d cosine; metin D1'de, vektör Vectorize'da — metadata boyut tavanı yenmez).
- **Yerel (entity-merkezli) GraphRAG** — `upsert_triples` + n-hop `graph_neighbors` + induced `subgraph` + `hybrid_query` birleşimi.

**KASITLI OLARAK SEVK EDİLMEYEN (sahte yaklaşımla taklit edilmez):**
- **Varlık/ilişki çıkarımı in-Worker zayıf 8B modelle YAPILMAZ** — çıkarımı **orchestrator (Claude)**
  yapar (`upsert_triples`); Worker yalnız depolar+gezer. Bu "LLM-in-the-loop GraphRAG"tir; grafik
  kalitesi konusunda dürüsttür.
- **Microsoft-GraphRAG global arama** (Leiden community detection + hiyerarşik community özetleri) —
  istek-kapsamlı bir Worker'a değil, **batch bir Cloud Run indeksleyiciye** aittir. `community_summary`/
  `global_query` yol haritasıdır; zayıf bir in-Worker yaklaşımı olarak SEVK EDİLMEZ. (Eklemek isteyen:
  `anamnesis-indexer` Cloud Run job → Leiden → community summaries → D1 `communities` tablosu → yeni
  `global_query` aracı; aynı OAuth arkasında.)

**Telif:** Annas/Wiley tam metni yalnız **analiz** içindir; chunk'lar sınırlı ve provenance'lıdır,
toplu birebir çoğaltma yapılmaz (CONNECTORS.md telif notu).

**Alternatif depo (belgelenmiş):** Operatörün Supabase connector'ı varsa pgvector + (Apache AGE)
alternatif substrat olabilir; birincil seçim, fleet desenini korumak için Cloudflare (Vectorize+D1+
Workers AI). Embedding yine Workers AI ile üretildiğinden harici embedding API anahtarı gerekmez.

---

## DoD (Definition of Done)
- [ ] `npm run typecheck` → 0 hata.
- [ ] `npm test` → auth (6 invariant) + router + chunk-boundary + graph-helper yeşil.
- [ ] `wrangler vectorize create anamnesis-index --dimensions=1024 --metric=cosine` çalıştırıldı.
- [ ] `wrangler d1 create anamnesis-graph` çalıştırıldı, `database_id` `wrangler.jsonc`'a yapıştırıldı.
- [ ] `MCP_API_KEY` + `AUTH_HMAC_SECRET` secret store'da (kodda/vars'ta DEĞİL).
- [ ] `wrangler deploy` başarılı.
- [ ] `smoke_oauth_public.sh`: health 200 · S256-only · 401-without-Bearer · 200-authenticated.
- [ ] `ingest_document` → manifest (ham metin DÖNMÜYOR) · `corpus_stats` doc/chunk artışını gösteriyor.
- [ ] claude.ai custom connector eklendi; PKCE round-trip tamam.
- [ ] `.mcp.json` + CONNECTORS.md anamnesis Tier-O girdisi canlı URL ile güncellendi; G-PROBE 🔒401.
