# Connector Kaydı — doğrulanmış araçlar ve ÖLÇÜLMÜŞ yetenekler

> Bu dosya **ölçüm** kaydıdır, iddia kaydı değil. Bir satırda "çalışır" yazıyorsa canlı bir
> çağrıyla doğrulanmıştır ve tarihi verilmiştir. Ölçülmemiş yetenek **ölçülmemiş** yazar.
> Çakışmada `../../../CONNECTORS.md` ve `../../../.mcp.json` üstündür.

Son ölçüm turu: **2026-08-11**.

---

## 1. Akademik çekirdek — her substantif sorguda ateşlenir

| Server | Kilit araçlar | Ölçülmüş not |
|---|---|---|
| `openalex` | `openalex_search_entities`, `openalex_resolve_name`, `openalex_get_citation_graph`, `openalex_analyze_trends` | **Tıp tarihi topic'leri ölçüldü:** T12324 History of Medicine Studies (123.520 eser), T12990 Medical History and Innovations (288.100), T14475 History of Science and Medicine (117.643), T12778 History of Medicine and Tropical Health (25.224). Beşeri bilimler literatürünü taşıyan tek geniş graf |
| `pubmed-epmc` | `pubmed_search_articles`, `pubmed_lookup_mesh`, `pubmed_fetch_fulltext`, `pubmed_europepmc_search` | **MeSH tarih ağacı ölçüldü:** kök `K01.400`; D006666 History of Medicine (K01.400.552); Ancient .470 · Medieval .500 · Early Modern 1451-1600 .475 · Modern 1601- .504 · 19th .937 · 20th .968 · 21st .984. `Historical Article` yayın tipiyle birlikte dönem kilitleme sağlar |
| `semantic-scholar` | `search_papers`, `get_paper`, `get_paper_citations` | Bağımsız ikinci indeks. ⚠️ Kitap/kitap-bölümü kapsamı zayıf: ölçümde "Transforming plague / Cunningham" **0 sonuç** döndü |
| `paper-search` | `search_google_scholar`, `search_crossref`, `read_crossref_paper` | Monograf ve kitap-bölümü katmanının tek geniş yüzeyi. Smithery anahtarı yoksa degrade |
| `consensus` | `search` | Ücretsiz katman **3 sonuç gösterir** (ölçümde 20 bulundu, 3 gösterildi). Kullanım mesajını birebir aktar |
| `scholar-gateway` | `semanticSearch` | Pasaj-düzeyi atıf. OAuth gerekir; etkileşimsiz oturumda erişilemez |

**Yapısal kör nokta (ölçüldü):** pre-DOI monograflar bu filoda çözülmez — Rosenberg *Framing
Disease* (1992), Arnold *Colonizing the Body* (1993), Porter "The Patient's View" (1985),
Cunningham "Transforming plague" (1992, CUP kitap bölümü). Bunlar **bibliyografik künyeyle**
atıflanır; tanımlayıcı **uydurulmaz**.

---

## 2. Birincil kaynak — IIIF ve arşiv

| Server | Kilit araçlar | Ölçülmüş not |
|---|---|---|
| `ottoman-archives` | `ottoman_search_iiif`, `ottoman_fetch_iiif_manifest`, `ottoman_search_within_manifest`, `ottoman_browse_iiif_collection`, `ottoman_convert_date` | **Osmanlı-dışı çalışır:** "anatomy Vesalius" → 29 sonuç; "plague treatise" → 28. Gerçek isabetler: Fuchs *De humani corporis fabrica* 1551, Vesalius *Fabrica* 1555, *A treatise of the plague* 1603/1721/1799. Kaynak-başına yetenek EŞİT DEĞİL → `iiif-capability-matrix.md` |
| `devlet-arsivleri` | `devarsiv_session_status`, `devarsiv_search`, `devarsiv_semantic_search`, `devarsiv_get_belge`, `devarsiv_coverage` | Tek-cihaz oturum kilidi; sorgudan ÖNCE `session_status`. Derin zanaat → `vekayinuvis` delegasyonu |

---

## 3. Tam-metin şelalesi

| Tier | Server | Kural |
|---|---|---|
| 3 | `openathens` | Lisanslı band — **önce burası**. `oa_fetch_fulltext` = metin/RAG; `oa_fetch_pdf(doi\|url)` = provider-nötr orijinal PDF, kısa-ömürlü resource link + SHA-256/provenance |
| 4 | `annas-reader` | Son çare; reader akışı bounded analiz için. `download_document(id=DOI\|32-hex MD5)` = PDF/EPUB/MOBI/AZW/DjVu/FB2/CBZ/CBR/XPS, kısa-ömürlü resource link + checksum. Yalnız ANALİZ; gövde kopyalanmaz; > eşik → anamnesis |

Dosya linkleri kalıcı kaynak değildir: derhal tüketilir; atıf/provenance kaydında DOI veya
MD5 ile dönen SHA-256 tutulur. `oa_fetch_pdf` HTML-only sayfayı PDF diye uydurmaz;
`pdf_unavailable` dürüst degrade'dir.

---

## 4. Tarihsel yasama

| Server | Kilit araçlar | Not |
|---|---|---|
| `uk-legal` | `hansard_search`, `hansard_get_debate`, `find_case_law_search` | Hansard 1803+ — en zengin programatik birincil yasama kaydı. ⚠️ `legislation_*` araçları **ölçülmüş biçimde bozuk** (upstream HTTP istemcisi; aynı URL'ler `curl` ile 200 döner) → mevzuat METNİ için `legislation.gov.uk` `/data.akn` yolu |
| `health-policy` | `govinfo_search`, `congress_search`, `federal_register_search`, `semantic_search` | Tarihsel ABD kaydı + JP/AU/ES/IE/CN/MX/CA |
| `intl-treaty` | `treaty_status`, `coe_treaty_signatories` | ⚠️ coe.int canlı yolu **inert** (TLS parmak izi bloğu) → küratörlü snapshot servis edilir, `snapshot_age_days` + `mcp_verified:false` taşır |
| `mevzuat` · `tbmm` · `resmigazete` | — | TR yasama kolu |

---

## 5. Terminoloji ve epidemiyoloji

| Server | Durum | **Ölçülmüş uyarı** |
|---|---|---|
| `med-terminologies` | canlı ama **güvenilmez** | `find_equivalent` skorlaması **TERS**: doğru ICD-11 isabetleri `match_score: 0`, yanlış sözlüksel isabetler `0.833`. `dropsy`→Oedema+Ascites ✅ · `apoplexy`→Stroke ✅ ama "Pituitary Apoplexy" da geliyor · **`consumption`→tüberküloz HİÇ dönmüyor** ("Oxygen Consumption" dönüyor). `match_score` sıralamada **KULLANILMAZ**. SNOMED lisanssız → devre dışı |
| `who-gho` | canlı | Yalnız WHO'nun yayımladığı dönem (≈1948+); öncesine projeksiyon yasak |
| `globocan` | canlı | Çağdaş kesit; tarihsel seri değil |

---

## 6. Bloklu / erişilemeyen yüzeyler — ölçülmüş

| Kaynak | Durum | Kanıt | Sonuç |
|---|---|---|---|
| **Library of Congress** manifest | ❌ 403 | Araç ve iki bağımsız ağdan `curl` (Chrome UA) → 403; blok **evrensel**, egress kaynaklı değil | Keşif ve TEK görsel (`tile.loc.gov` 200) çalışır; sayfa listesi alınamaz |
| **NLM Digital Collections** | ❌ bot kapısı | `curl` → HTTP 202, gövde 0 bayt (Akamai); IIIF manifest ucu da 202/0 | Tarayıcı-yetenekli relay gerekir |
| **Perseus / Scaife CTS** | ❌ ölü | `scaife-cts.perseus.org` DNS yok; `cts.perseids.org` 502; `scaife.perseus.org/api/cts` SPA kabuğu | Çalışan alternatif: Hopper `xmlchunk` (200) + GitHub `PerseusDL/canonical-greekLit` (tlg0627 Hipokrat, tlg0057 Galen) |
| **HathiTrust** tam-metin | ❌ 403 | Data API 403; **Bib API 200** (`oclc:424023` → JSON) | Metadata/holdings kullanılabilir, tam metin değil |
| **Europeana** | ❌ anahtarsız | `Invalid API key`; ottoman sunucusu da `OTTOMAN_EUROPEANA_API_KEY not configured` diyor | Ücretsiz anahtar + sunucu env'i (tek satırlık iş) |
| **BHL** (herbal/materia medica) | ❌ anahtarsız | `unauthorized ... invalid API key` | Ücretsiz anahtar alınmalı |
| **IndexCat** | ⚠️ yalnız HTML | Kök 200/119 KB; Vivisimo sorgu ucu 200/157 KB `text/html`; JSON/dump yok | Kazıma MCP'si gerekir |
| **DPLA** doğrudan | ❌ 403 | Doğrudan `curl` → `invalid_api_key`; **ama** `ottoman_search_iiif` dpla n=5 döndürdü | Yalnız `ottoman-archives` üzerinden |

**Kural:** bu yüzeylerden içerik **uydurulmaz**. Kullanıcıya erişim yol haritası verilir
(kurum, koleksiyon, raf numarası, alternatif dijital kopya).

---

## 7. Anahtarsız ve doğrudan çalışan yardımcı yüzeyler (ölçüldü)

| Kaynak | Uç | Durum |
|---|---|---|
| **Wellcome Collection API** | `api.wellcomecollection.org/catalogue/v2/works` | ✅ 200, authless. `include=items` → `locations[].locationType.id == "iiif-presentation"` → `.url` = manifest URI. Dijitalleşmemiş eserde bu location YOK → filtre şart |
| **Wikidata SPARQL** | `query.wikidata.org/sparql` | ✅ 200, authless. Prosopografi sorgusu doğrulandı (P106=Q39631 hekim + P569/P570) |
| **Wikimedia REST** | `api.wikimedia.org/core/v1/...` | ✅ 200, authless (Wikipedia + Wikisource) |
| **HathiTrust Bib** | `catalog.hathitrust.org/api/volumes/...` | ✅ 200 |
| **Gallica IIIF** | `gallica.bnf.fr/iiif/ark:/12148/<ark>/manifest.json` | ✅ 200 (`search_service` yok) |
| **Internet Archive IIIF** | `iiif.archive.org/iiif/<id>/manifest.json` | ✅ 200 |

Bu yüzeyler MCP değildir; `WebFetch` ile çağrılır ve sonuç **P1/P2 kanıt** sayılır (Wikidata ve
Wikipedia **P3**'tür — yalnız yönlendirme).
