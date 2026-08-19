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
| `ingest_document` | Semantik chunk + embed + sakla; re-ingest önce forget (kuyruk vektörü kalmaz); isteğe bağlı `ttl_hours` (run/sess) → **manifest** | mutation |
| `semantic_search` | Hibrit getirim; `collection` ve/veya `doc_id` / `doc_ids[]` | read-only |
| `upsert_triples` | Collection-scoped graph yazımı (`nodeKey`/`edgeId` collection içerir) | mutation |
| `graph_neighbors` | n-hop; **collection zorunlu** | read-only |
| `subgraph` | Induced kenarlar; **collection zorunlu** | read-only |
| **`hybrid_query`** | **FLAGSHIP; collection zorunlu**; vektör∥BM25→RRF→rerank ∪ graph → sınırlı paket | read-only |
| `list_docs` | Bir koleksiyonun belgeleri | read-only |
| `corpus_stats` | collection yok = küresel gözlem (çalışma seti değil) | read-only |
| `forget_document` | Tek `doc_id` temiz silme | **mutation (destructive)** |
| **`forget_collection`** | Bir koleksiyon: SQL + Vectorize `deleteByIds`; başka koleksiyona dokunmaz | **mutation (destructive)** |

Sentez kılavuzu: *Synthesize ONLY from these chunks; cite doc_id::idx*.

## Mimari
`bge-m3` (1024-d, çok-dilli — TR sorgu / EN korpus) embeddings → **Vectorize** (vektörler;
metadata `collection` + `doc_id`) + **D1** (chunk metni + bilgi grafiği). Çıkarım **orchestrator
(Claude) tarafından** yapılır (LLM-in-the-loop GraphRAG); Worker depolar+gezer. In-Worker LLM
çıkarımı ve sahte GraphRAG community özeti **yoktur** (BUILD-BRIEF §5).

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
wrangler secret put MCP_API_KEY && wrangler secret put AUTH_HMAC_SECRET
wrangler deploy
```

`ensureSchema()` ilk araç çağrısında `ALTER TABLE` ile collection sütunlarını da ekler;
migration dosyası HP'de bir kez çalıştırılacak tek-seferlik yoldur.

**Telif:** tam metin yalnız analiz içindir; chunk'lar sınırlı/provenance'lı, toplu çoğaltma yok.
