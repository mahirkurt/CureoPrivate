# Bağlam Ekonomisi Sözleşmesi — historia-medicinae

**Sorun.** Tam-filo (25 server) tek turda ateşlendiğinde ham getirim ana bağlam penceresini
boğar. Tıp tarihinde bu sorun diğer alanlardan **daha ağırdır**: alanın taşıyıcı birimi makale
değil **monograf**tır (300–600 sayfa), birincil kaynak **sayfa görüntüsüdür** (bir IIIF manifesti
180–972 canvas), ve yasama kaydı **zabıt serisidir** (Hansard tek bir müzakerede on binlerce
kelime).

**Çözüm.** Üç katmanlı ekonomi. Hiçbir katman detayı atmaz; her katman detayın **nerede
akıl yürütüleceğini** değiştirir.

---

## §1 Üç katman

| Katman | Araç | Ne zaman | Ne döner |
|---|---|---|---|
| **Tier 0 — doğrudan** | MCP aracı ana bağlamda | Getirim küçük (< ~6 KB), tek server, tek sonuç | Ham sonuç |
| **Tier 1 — distiller** | `agents/tarih-tarama-distilleri.md` | Çok-server fan-out; ham gövde > 6 KB; kaynak matrisi taraması | Tek `retrieval_distillate` zarfı + `coverage` bloğu |
| **Tier 2 — RAG substratı** | `anamnesis` MCP | Tek belge > ~30 KB (monograf, tez PDF, manifest-içi blok, zabıt serisi) | `ingest_document(collection=histmed:run:…)` → `hybrid_query(collection=…)` dilimleri |

**Kural:** büyük bir belge **kör getirilmez**. Önce yapısal navigasyon (manifest canvas listesi,
madde ağacı, içindekiler, MeSH/anahtar kelime konumu) → hedef parça → gerekirse Tier 2.

---

## §2 Sharding — tam-filo, paralel, ≤4 alt-ajan

Fan-out gerektiğinde filo **shard**'lara bölünür ve her shard'a **araç kümesi kısıtlı** bir
distiller verilir. Aynı anda **en fazla 4** distiller çalışır.

| Shard | Bant | Server'lar |
|---|---|---|
| **S1** | Akademik çekirdek | openalex · pubmed-epmc · semantic-scholar · paper-search · consensus · scholar-gateway |
| **S2** | Birincil kaynak | ottoman-archives (IIIF) · devlet-arsivleri |
| **S3** | Tam-metin şelalesi | openathens (`oa_fetch_fulltext` / `oa_fetch_pdf`) → annas-reader (reader / `download_document`) |
| **S4** | Tarihsel yasama | uk-legal · health-policy · intl-treaty · mevzuat · tbmm · resmigazete |
| **S5** | Terminoloji/epi | med-terminologies · who-gho · globocan |
| **S6** | Türkiye kolu | yoktez · literatur · yok-akademik |
| **S7** | Web (üçüncül) | exa · tavily |
| **S8** | Substrat | anamnesis (shard değil — her katmanın çıktısını yutabilir) |

Shard **kapsamı daraltmaz**: her shard kendi bandını TAM tarar ve `coverage` satırlarını döndürür.
Sharding yalnız *nerede akıl yürütüldüğünü* değiştirir. Bir shard'ın atlanması G0 ihlalidir.

---

## §3 Kanonik önbellek — bir-kez-getir

Her getirilen artefakt **kanonik bir kimlikle** anılır ve **aynı koşumda ikinci kez
getirilmez**:

| Artefakt | Kanonik sonek (`doc_id = hmrun:<12hex>:<sonek>`) |
|---|---|
| Makale | `doi/<doi>` veya `pmid/<pmid>` |
| IIIF belgesi | `<kaynak>/<id>` (ör. `wellcome/b3135631x`) |
| Monograf (tam-metin) | `openathens/<doi-veya-yazar-yıl>` veya `annas/<md5>`; dosya linki değil DOI/MD5 + SHA-256 provenance |
| Arşiv belgesi | `devarsiv/<arşiv>/<fon>/<kutu>-<gömlek>` |
| Zabıt | `hansard/<tarih>/<debate-id>` · `tbmm/<dönem>/<birleşim>` |
| Tez | `yoktez/<tez-no>` |

**Her ingest `collection=histmed:run:<12hex>` + önekli `doc_id` ister.** Tenancy collection'dadır;
eski çıplak `histmed:doi/…` (koşu-id'siz) `_legacy` torbasına düşer ve diğer plugin sorgularına sızar.
`doc_scope` **yoktur**. Cevap yalnız dönen chunk'lardan; atıf `doc_id::idx`.

---

## §4 Chunking disiplini — kör getirme yok

1. **IIIF:** `ottoman_fetch_iiif_manifest` önce canvas listesini verir; **tüm sayfaları çekme**.
   Wellcome'da `search_service` varsa `ottoman_search_within_manifest` ile hedef canvas'ı bul,
   yalnız onu oku. Diğer kaynaklarda metadata + hedef aralık.
2. **Monograf:** reader varsa `search_in_document` (BM25) ile konum bul → yalnız o bölümü
   oku. Orijinal dosya gerekiyorsa `oa_fetch_pdf` veya `download_document`; kısa-ömürlü
   resource link'i derhal tüket, SHA-256/provenance kaydet → > 30 KB ise Tier 2.
3. **Zabıt:** tarih + konuşmacı ile daralt; tüm oturumu çekme.
4. **Tez:** `get_yok_tez_document_markdown` sayfa-bazlıdır; içindekilerden hedef sayfaya git.

---

## §5 Bağlam bütçesi ve devre kesici

- Tek turda ham MCP getirimi **~60 KB**'ı aşarsa: kalan getirim Tier 1'e, > 30 KB tek belge
  Tier 2'ye taşınır.
- Aynı server'a aynı sorguyla **ikinci çağrı yasaktır** (kanonik önbellek).
- Distiller'ın döndürdüğü zarf ana bağlamda **yeniden özetlenmez** — olduğu gibi kullanılır.

---

## §6 anamnesis çağrı disiplini

```
ingest_document(collection="histmed:run:<12hex>", doc_id="hmrun:<12hex>:doi/<doi>", …)
hybrid_query(collection="histmed:run:<12hex>", queries=[…])   # kapsamsız = DENY / MCP error
upsert_triples(collection="histmed:run:<12hex>", …)
graph_neighbors / subgraph  # collection zorunlu
# atıf: doc_id::idx
```

**Anahtar yoksa:** sınırlı-parça getirime düşülür (manifest-içi arama + sayfa-bazlı okuma).
**Ham tam-metin dökümü hiçbir koşulda yapılmaz.**

---

## §7 Beş değişmez

1. **Detay atlanmaz, yeri değişir.** Distiller'a giden bir bulgu kaybolmaz; zarfta döner.
2. **Kör getirme yok.** Büyük belge önce yapısal olarak navige edilir.
3. **Bir-kez-getir.** Kanonik doc_id ile önbellek; `collection=histmed:run:` + `hmrun:` öneki zorunlu.
4. **Sessiz atlama yok.** Her shard `coverage` satırı üretir; eksik satır G0 FAIL.
5. **Ham döküm yok.** Ne ana bağlama, ne çıktıya. Getirilen tam metin **analiz içindir**;
   telif kapısı (annas-reader Tier 4) gövde kopyalamayı yasaklar.
