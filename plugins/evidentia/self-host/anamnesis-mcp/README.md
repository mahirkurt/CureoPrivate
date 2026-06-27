# anamnesis-mcp

> **ἀνάμνησις** — *recollection / retrieval* (Plato); klinikte *anamnez* = hastanın öyküsünün
> hatırlanması. evidentia eklentisinin **bilgi-geri-çağırma** substratı için iki anlamlı isim.

Sertleştirilmiş-OAuth Cloudflare Worker MCP'si. Tam-metin makale/kitap ve büyük araç çıktılarını
**semantik chunk + vektör (Vectorize/bge-m3) + varlık-ilişki grafiği (D1)** olarak indeksler ve
sorguya yalnız **bağlam-penceresine sığacak**, provenance-damgalı, graph-temelli bir kanıt paketi
sunar. Amaç: araç çıktılarının bağlam taşması nedeniyle eksik/tutarsız değerlendirilmesini önlemek.

## Araçlar
| Araç | İşlev | Tip |
|---|---|---|
| `ingest_document` | Semantik chunk + embed + sakla → **manifest** döner (ham metin değil) | mutation |
| `semantic_search` | Vektör top-k chunk + provenance (doc_id, idx, score) | read-only |
| `upsert_triples` | Claude'un çıkardığı varlık/ilişki triple'larını D1 grafiğine yaz | mutation |
| `graph_neighbors` | Bir varlıktan n-hop yerel GraphRAG genişletme | read-only |
| `subgraph` | Verilen varlık kümesi içindeki induced kenarlar (çapraz-belge bağ) | read-only |
| **`hybrid_query`** | **Vektör top-k ∪ graph genişletme → sınırlı kanıt paketi** | read-only |
| `corpus_stats` | docs/chunks/nodes/edges sayımı | read-only |

## Mimari
`bge-m3` (1024-d, çok-dilli — TR sorgu / EN korpus) embeddings → **Vectorize** (vektörler) +
**D1** (chunk metni + bilgi grafiği). Çıkarım **orchestrator (Claude) tarafından** yapılır
(LLM-in-the-loop GraphRAG); Worker depolar+gezer. Microsoft-GraphRAG global community özetleri
bir Cloud Run indeksleyiciye ertelenir (BUILD-BRIEF §5).

## Güvenlik
Cureonics Family A — `auth.ts` drugddx ile birebir aynı 6 invariant (redirect tam-origin
allowlist · PKCE S256-only · escHtml · HMAC+10dk TTL auth-code · sabit-zaman karşılaştırma ·
secret yalnız secret store).

## Deploy
`BUILD-BRIEF.md` (S0–S13 + Vectorize/D1 provizyon + DoD). Özet:
```bash
npm install && npm run typecheck && npm test
npx wrangler vectorize create anamnesis-index --dimensions=1024 --metric=cosine
npx wrangler d1 create anamnesis-graph            # database_id → wrangler.jsonc
wrangler secret put MCP_API_KEY && wrangler secret put AUTH_HMAC_SECRET
wrangler deploy
```

**Telif:** tam metin yalnız analiz içindir; chunk'lar sınırlı/provenance'lı, toplu çoğaltma yok.
