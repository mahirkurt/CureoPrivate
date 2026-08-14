# CONNECTORS — historia-medicinae bağlayıcı envanteri

> **Normatif kaynak.** Çakışmada bu dosya ve `.mcp.json` üstündür; skill içi tablolar
> pedagojik referanstır. `.mcp.json` ve `fleet.lock.json` **üretilmiş** dosyalardır —
> tek gerçek kaynak `fleet.yaml`.

25 wire'lı server · 3 companion · 3 delegasyon. Ölçüm turu: **2026-08-11**.

---

## 1. Bantlar ve rolleri

### A. Akademik çekirdek (6) — HER substantif sorguda ateşlenir

| Server | Anahtar | Rol |
|---|---|---|
| `openalex` | `OPENALEX_MCP_API_KEY` | **Taşıyıcı graf.** Tıp tarihi literatürünün büyük kısmı beşeri bilimler dergilerindedir ve PubMed'de görünmez. Topic'ler: T12324 · T12990 · T14475 · T12778 |
| `pubmed-epmc` | `PUBMED_MCP_API_KEY` | **Dönem kilidi.** MeSH `K01.400` tarih ağacı + `Historical Article` yayın tipi |
| `semantic-scholar` | `SEMANTICSCHOLAR_MCP_API_KEY` | Bağımsız ikinci indeks (çapraz doğrulama) |
| `paper-search` | — (Smithery userConfig) | **Monograf katmanı** — Google Scholar + CrossRef |
| `consensus` | — (OAuth) | Tartışmalı tarihyazımı iddialarında sentez |
| `scholar-gateway` | — (OAuth) | Pasaj-düzeyi atıf doğrulaması |

### B. Birincil kaynak (2)

| Server | Anahtar | Rol |
|---|---|---|
| `ottoman-archives` | `OTTOMAN_ARCHIVES_MCP_API_KEY` | **Jenerik IIIF motoru** — Wellcome/Gallica/IA/Princeton/DPLA + herhangi bir v2/v3 manifest + çok-takvimli tarih çevirisi |
| `devlet-arsivleri` | `DEVARSIV_MCP_API_KEY` | TR resmî katalog. **Tek-cihaz oturum kilidi** — sorgudan önce `devarsiv_session_status` |

### C. Tam-metin şelalesi (2) — yasal-öncelikli

| Tier | Server | Anahtar | Dosya teslim sözleşmesi |
|---|---|---|---|
| 3 | `openathens` | `OPENATHENS_MCP_API_KEY` | 11 araç (2026-08-14): metin/RAG `oa_fetch_fulltext`; provider-nötr orijinal PDF `oa_fetch_pdf(doi\|url)` |
| 4 (son çare) | `annas-reader` | `ANNAS_MCP_API_KEY` | 9 araç (2026-08-14): bounded reader akışı; orijinal PDF/EPUB/etc. `download_document(id=DOI\|MD5)` |

Her iki dosya aracı kısa-ömürlü opaque `resource_link` + checksum/provenance döndürür.
Link derhal tüketilir, kalıcı URL diye saklanmaz; uzun belge `histmed:` doc_id ile
anamnesis'e ingest edilir. Anna's yalnız lisanslı bant başarısız olduktan sonra ve analiz
amacıyla kullanılır.

### D. Tarihsel yasama (6)

| Server | Anahtar | Rol |
|---|---|---|
| `uk-legal` | `UK_LEGAL_MCP_API_KEY` | **Hansard 1803+** — en zengin programatik birincil yasama kaydı |
| `health-policy` | `HEALTH_POLICY_MCP_API_KEY` | GovInfo/Congress tarihsel ABD + JP/AU/ES/IE/CN/MX/CA |
| `intl-treaty` | `INTL_TREATY_MCP_API_KEY` | Oviedo CETS 164 · MEDICRIME 211 · BM sözleşmeleri |
| `mevzuat` | `MEVZUAT_MCP_API_KEY` | TR mülga sağlık mevzuatı + gerekçe |
| `tbmm` | `TBMM_MCP_API_KEY` | TBMM zabıtları (1219/1593 müzakereleri) |
| `resmigazete` | `RESMI_GAZETE_MCP_API_KEY` | Erken-Cumhuriyet yayın kaydı (1920+) |

### E. Terminoloji / epidemiyoloji (3)

| Server | Anahtar | Uyarı |
|---|---|---|
| `med-terminologies` | — | ⚠️ **`find_equivalent` skorlaması ters** — yalnız doğrulama için |
| `who-gho` | — | Yalnız ≈1948+ |
| `globocan` | — | Çağdaş kesit, tarihsel seri değil |

### F. Türkiye kolu (3)

`yoktez` (—) · `literatur` (—) · `yok-akademik` (`YOK_AKADEMIK_MCP_API_KEY`)

### G. Web — üçüncül (2)

`exa` (—) · `tavily` (`TAVILY_API_KEY`). **Kanıt hiyerarşisinin en altı**: tek başına akademik
iddia taşıyamaz.

### H. Substrat (1)

`anamnesis` (`ANAMNESIS_MCP_API_KEY`) — doc_id ön-eki **`histmed:`** zorunlu.

---

## 2. Companion'lar (claude.ai yüzeyi)

| Companion | Yokluğunda |
|---|---|
| PubMed | wire'lı `pubmed-epmc` taşır — kayıp yok |
| Paper Search | wire'lı `paper-search` taşır — kayıp yok |
| Elicit | tarama elle yürütülür, beyan edilir |

Companion satırı manifestoda **daima yazılır** (`skipped: bağlı değil` dahil).

---

## 3. Delegasyonlar

| Hedef | Tetikleyici | Yokluğunda |
|---|---|---|
| `vekayinuvis` | Osmanlıca el yazması paleografi/HTR, BOA derin süpürme, ebced | Transkripsiyon **yapılmaz**; katalog künyesi düzeyinde kalınır |
| `evidentia` | Çağdaş klinik etkililik/güvenlilik | Klinik iddia **UNVERIFIED** bırakılır |
| `sci-audit` | Her RELATIO çıktısı | "Bağımsız denetim yapılmadı" **beyan edilir** |

---

## 4. Kalıcı bloklar — anahtarla çözülmez

| Kaynak | Durum | Ölçüm |
|---|---|---|
| Library of Congress manifest | **403** | Araç + iki bağımsız ağdan `curl` (Chrome UA); blok evrensel, egress kaynaklı değil. `tile.loc.gov` tek görsel **200** |
| NLM Digital Collections | **bot kapısı** | HTTP 202, gövde 0 bayt (Akamai); IIIF ucu da 202/0 |
| Perseus / Scaife CTS | **ölü** | `scaife-cts` DNS yok · `cts.perseids.org` 502 · `/api/cts` SPA kabuğu. Alternatif: Hopper `xmlchunk` 200 + GitHub `PerseusDL/canonical-greekLit` |
| HathiTrust tam-metin | **403** | Data API 403; Bib API 200 (`oclc:424023` → JSON) |
| Europeana | anahtarsız | `Invalid API key`; ottoman sunucusu `OTTOMAN_EUROPEANA_API_KEY not configured` diyor |
| BHL | anahtarsız | `unauthorized` — herbal/materia medica katmanı kapalı |
| DPLA doğrudan | 403 | Yalnız `ottoman-archives` üzerinden erişilebilir |

**Kural:** bu yüzeylerden içerik **uydurulmaz** → erişim yol haritası verilir.

---

## 5. Anahtarsız yardımcı yüzeyler (WebFetch ile, ölçüldü)

| Kaynak | Uç | Durum |
|---|---|---|
| Wellcome katalog API | `api.wellcomecollection.org/catalogue/v2/works` | 200, authless. `include=items` → `locationType.id=="iiif-presentation"` → `.url` |
| Wikidata SPARQL | `query.wikidata.org/sparql` | 200, authless (prosopografi — **P3**) |
| Wikimedia REST | `api.wikimedia.org/core/v1/...` | 200, authless (**P3**) |
| HathiTrust Bib | `catalog.hathitrust.org/api/volumes/...` | 200 |
| Gallica IIIF | `gallica.bnf.fr/iiif/ark:/12148/<ark>/manifest.json` | 200 (`search_service` yok) |
| Internet Archive IIIF | `iiif.archive.org/iiif/<id>/manifest.json` | 200 |
