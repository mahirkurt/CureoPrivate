# anamnesis-mcp

> **ἀνάμνησις** — *recollection / retrieval* (Plato); klinikte *anamnez* = hastanın öyküsünün
> hatırlanması. evidentia eklentisinin **bilgi-geri-çağırma** substratı için iki anlamlı isim.

Sertleştirilmiş-OAuth Cloudflare Worker MCP'si. Tam-metin makale/kitap ve büyük araç çıktılarını
**semantik chunk + vektör (Vectorize/bge-m3) + varlık-ilişki grafiği (D1)** olarak indeksler ve
sorguya yalnız **bağlam-penceresine sığacak**, provenance-damgalı, graph-temelli bir kanıt paketi
sunar. Amaç: araç çıktılarının bağlam taşması nedeniyle eksik/tutarsız değerlendirilmesini önlemek.

## Koleksiyon sözleşmesi (v1.2.0)

```
collection = "{plugin}:{kind}:{id}"
kind ∈ { run, sess, lib }
Evidentia scratch: collection="evidentia:run:<12hex>"
```

Eksik `collection` yazıda `_legacy` kovasına düşer (eski istemci uyumu). `hybrid_query` /
`graph_neighbors` / `subgraph` kapsamsız çağrı **MCP error** döner (boş başarı değil).
`semantic_search` kapsamsız compat için durur ve `_legacy` + tüm kiracıları görebilir —
istemci guard'ı bunu DENY etmelidir. `forget_by_prefix` API değildir; çalışma seti
`forget_collection` ile silinir. Küresel wipe aracı yoktur.

## Araçlar
| Araç | İşlev | Tip |
|---|---|---|
| `ingest_document` | Semantik chunk + embed + sakla; isteğe bağlı `ttl_hours` (run/sess) → **manifest**. Manifest `chars_indexed`/`chars_total`/`next_offset` taşır: `next_offset` doluysa kuyruk **indekslenmedi**, `offset` ile devam et. `doc_id` ≤ 56 bayt | mutation |
| `semantic_search` | Hibrit getirim; `collection` ve/veya `doc_id` / `doc_ids[]` | read-only |
| `upsert_triples` | Collection-scoped graph yazımı (`nodeKey`/`edgeId` collection içerir) | mutation |
| `graph_neighbors` | n-hop; **collection zorunlu** | read-only |
| `subgraph` | Induced kenarlar; **collection zorunlu** | read-only |
| **`hybrid_query`** | **FLAGSHIP; collection zorunlu**; vektör∥BM25→RRF→rerank ∪ graph → sınırlı paket | read-only |
| `list_docs` | Bir koleksiyonun belgeleri | read-only |
| `corpus_stats` | collection yok = küresel gözlem (çalışma seti değil) | read-only |
| `forget_document` | Tek `doc_id` temiz silme; `collection` **sahiplik kontrolüdür** — başka koleksiyona ait belge reddedilir | **mutation (destructive)** |
| **`forget_collection`** | Bir koleksiyon: SQL + Vectorize `deleteByIds`; başka koleksiyona dokunmaz | **mutation (destructive)** |

Sentez kılavuzu: *Synthesize ONLY from these chunks; cite doc_id::idx*.

Her getirim sonucu `score_kind` (`rerank` \| `rrf`) taşır — iki ölçek kıyaslanamaz. Vektör kolu
düşerse arama **leksikal-only** devam eder ve `degraded: "vector_unavailable"` bildirir.

## Kiracılık geçişi — `STRICT_COLLECTION`
`collection` biçimi hep doğrulanıyordu ama **kapsamsız** çağrılar kabul ediliyordu: yazma sessizce
`_legacy`'ye düşüyor, kapsamsız arama `_legacy` + tüm kiracıları okuyordu. Tek engel, claude.ai web
connector'ının / ChatGPT'nin / Cursor'ın / curl'ün asla çalıştırmadığı fail-open Python hook'lardı.

`STRICT_COLLECTION` (`wrangler.jsonc` vars, varsayılan `"0"`):
- **`"0"`** — davranış aynı, her kapsamsız çağrı `anamnesis.scope_violation` satırı olarak loglanır.
- **`"1"`** — kapsamsız `ingest_document` / `semantic_search` / `forget_document` / `upsert_triples`
  hata döner.

Log'lar temizlenene kadar `"0"` kalır. Önce kanıt, sonra kırılma.

## Mimari
`bge-m3` (1024-d, çok-dilli — TR sorgu / EN korpus) embeddings → **Vectorize** (vektörler;
metadata `collection` + `doc_id`) + **D1** (chunk metni + bilgi grafiği). Çıkarım **orchestrator
(Claude) tarafından** yapılır (LLM-in-the-loop GraphRAG); Worker depolar+gezer. In-Worker LLM
çıkarımı ve sahte GraphRAG community özeti **yoktur** (BUILD-BRIEF §5).

## Bakım
Gecelik cron (`10 4 * * *`) → `src/reaper.ts`: süresi dolmuş belgelerin D1 satırlarını, FTS
satırlarını **ve Vectorize vektörlerini** siler. Vectorize hiçbir zaman TTL filtrelenmiyordu, bu
yüzden ölü vektörler aday havuzunda canlı sonuçlardan yer çalıyordu. Reaper ayrıca TTL'siz kalmış
scratch'i 14 gün sonra süpürür (hook temizliği fail-open olduğu için son savunma hattı);
`lib` asla süpürülmez.

`GET /health` public ve ucuzdur. `GET /health?deep=1` (Bearer) D1 / Vectorize / Workers AI'yı ayrı
yoklar ve düşen bileşeni adıyla bildirir.

## Güvenlik
Cureonics Family A — `auth.ts` drugddx ile birebir aynı 6 invariant (redirect tam-origin
allowlist · PKCE S256-only · escHtml · HMAC+10dk TTL auth-code · sabit-zaman karşılaştırma ·
secret yalnız secret store).

## Deploy
`BUILD-BRIEF.md` (S0–S13 + Vectorize/D1 provizyon + DoD). Özet:
```bash
npm install && npm run typecheck && npm test
npx wrangler vectorize create anamnesis-index --dimensions=1024 --metric=cosine
npx wrangler vectorize create-metadata-index anamnesis-index --property-name=collection --type=string
npx wrangler vectorize create-metadata-index anamnesis-index --property-name=doc_id --type=string
npx wrangler d1 create anamnesis-graph            # database_id → wrangler.jsonc
npx wrangler d1 execute anamnesis-graph --remote --file=migrations/0001_collection.sql
npx wrangler d1 execute anamnesis-graph --remote --file=migrations/0002_edge_evidence.sql
wrangler secret put MCP_API_KEY && wrangler secret put AUTH_HMAC_SECRET
wrangler deploy
```

`ensureSchema()` bootstrap'ı **isolate başına bir kez** koşar (eskiden her araç çağrısındaydı:
ölçülen 24 ifade/çağrı, `hybrid_query` iki kez ödüyordu) ve `ALTER TABLE` ile eksik sütunları da
ekler; migration dosyaları uzak D1'de bir kez çalıştırılacak tek-seferlik yoldur.

**Telif:** tam metin yalnız analiz içindir; chunk'lar sınırlı/provenance'lı, toplu çoğaltma yok.
