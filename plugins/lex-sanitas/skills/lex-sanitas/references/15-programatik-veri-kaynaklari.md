# Reference 15 — Programatik Veri Kaynakları, API Uçları ve MCP Entegrasyon Kataloğu (YENİ — v2.5)

> **Amaç ve konum.** Bu dosya, Lex-Sanitas'ın **Katman 2 (Uluslararası Kaynak Katmanı)** ve **Katman 3 (Klinik/HTA Katmanı)** erişimini, mümkün olan her yerde **web-scraping'den makine-okunur programatik erişime (API/SPARQL/OData/bulk XML)** taşıyan kaynakları kataloglar. `references/08-uluslararasi-kaynaklar.md` (portal kayıt defteri — URL + ana kanun) ve `references/12-gelismis-ulke-rejimleri-derin.md` (derin rejim analizi) ile **tekil-doğruluk-kaynağı (single source of truth)** ilkesi gözetilerek tamamlayıcıdır: R8/R12 *ne* okunacağını, bu dosya *nasıl programatik olarak* okunacağını tanımlar. Mevzuat MCP (Katman 1) Türkiye iç hukuku için birincildir ve bu dosyanın kapsamı dışındadır.
>
> **Operasyonel ilke (v2.5 — Programatik Erişim Önceliği).** Bir kaynak için kararlı bir API/SPARQL/OData ucu mevcutsa, Fetch/Tavily ile HTML kazımak yerine **programatik uç tercih edilir**; çünkü programatik uçlar (a) madde/kayıt-düzeyinde yapılandırılmış veri, (b) sürüm/yürürlük damgası, (c) tekrarlanabilir doğrulama sağlar. Programatik uç yoksa veya yetkilendirme gerektiriyorsa, Fetch+parse geri-düşüş (fallback) kullanılır ve bu durum çıktıda epistemik dürüstlükle not edilir.

## İçindekiler
- [§1. Avrupa Birliği — CELLAR / EUR-Lex / EMA](#1)
- [§2. ABD Federal Düzenleyici Katman](#2)
- [§3. Birleşik Krallık — legislation.gov.uk (Akoma Ntoso)](#3)
- [§3b. İsviçre — Fedlex SPARQL (CH birincil metin)](#3b)
- [§4. Avrupa İçtihat ve Çok-Ülke Portalları](#4)
- [§5. Asya-Pasifik (Mevcut Yargı Bölgeleri) Programatik Uçlar](#5)
- [§6. Yeni Yargı Bölgeleri — Kanada, Brezilya, Suudi Arabistan, BAE](#6)
- [§7. Model Bağlam Protokolü (MCP) Sunucuları](#7)
- [§8. Klinik Kanıt ve Sağlık Teknolojisi Değerlendirme (HTA) Kaynakları](#8)
- [§9. Hukukî Tanımlayıcı Standartları (ELI / ECLI / Akoma Ntoso / FRBR)](#9)
- [§10. Erişim Disiplini, Lisans ve Bilgi Sınırı Uyarıları](#10)
- [§11. Mod × Kaynak Entegrasyon Matrisi](#11)

---

<a id="1"></a>
## §1. Avrupa Birliği — CELLAR / EUR-Lex / EMA

AB katmanı, birinci sınıf bir **Bağlı Açık Veri (Linked Open Data)** altyapısı sunar; Lex-Sanitas'ın AB erişimini kazımadan otomatik-doğrulanabilir sorgulara taşır.

| Kaynak | Erişim biçimi | Kimlik/anahtar | Standart | Not |
|---|---|---|---|---|
| **CELLAR SPARQL endpoint** (`http://publications.europa.eu/webapi/rdf/sparql`) | SPARQL 1.1 | Gerekmez | CDM (OWL/RDF), FRBR, ELI, ECLI, CELEX | Publications Office ortak metadata+içerik deposu; 2,7 milyon+ "work", ~720 milyon triple. Triple store Mart 2026'da Virtuoso 8'e yükseltildi — sorgu davranışı yeniden doğrulanmalı. |
| **CELLAR REST API** | REST (içerik + metadata) | Gerekmez | Formex XML / Akoma Ntoso / XHTML / PDF | Madde-düzeyi ayrıştırma (recital, madde, ek). Pre-2014 belgeler Formex XML olabilir — ayrıştırıcı her iki şemayı işlemeli. |
| **data.europa.eu SPARQL** (`https://data.europa.eu/data/sparql`) | SPARQL | Gerekmez | DCAT, EuroVoc | Veri seti metadatası + Resmî Gazete listeleri (CSV + Formex linkleri). |
| **EU Vocabularies / EuroVoc** | İndirme + SPARQL | Gerekmez | SKOS, NAL | 24 dilli thesaurus. **Dil filtresi (`cdm:expression_uses_language`) atlanırsa 24× fazla sonuç döner** — sorgularda dil daraltması zorunlu. Otorite tablolarını yerel cache'leyin (URI'ler ara sıra değişir). |
| **EUR-Lex data dump** (`datadump.publications.europa.eu`) | Bulk indirme | EU Login | — | Sektör 3 / yürürlükteki yasal işlemler; toplu işleme için. |
| **RSS/Atom feed (Pillar IV)** | Atom | Gerekmez | — | **Değişiklik bildirimi** — yeni/değişen mevzuatı izleme (15-30 dk aralık önerilir). |

**EMA (Avrupa İlaç Ajansı):** EPAR/medicine data indirilebilir tablolar (`ema.europa.eu/en/medicines/download-medicine-data`) + data.europa.eu "EPAR human medicines" veri seti; **Clinical Data Publication** (`clinicaldata.ema.europa.eu`, EMA hesabı + giriş gerekir, kullanım koşulları); **SPOR master data** (SMS/PMS/OMS/RMS, ISO IDMP uyumlu, on-boarding gerekir; PMS, CTIS'i besler); **DARWIN EU** dağıtık gerçek-dünya-kanıtı ağı (regülatör kullanımı).

**Erişim ekosistemi notu:** Olgun `eurlex` R paketi (CRAN — `elx_make_query`, `elx_run_query`, `elx_fetch_data`) SPARQL+REST'i sarmalar; sorgu kalıbı tasarımında referans alınabilir.

<a id="2"></a>
## §2. ABD Federal Düzenleyici Katman

Olağanüstü zengin ve büyük ölçüde **anahtarsız** bir katman; özellikle RIA (Mod 6) ve EX_POST (Mod 9) için ABD emsali sağlar.

| Kaynak | Uç | Anahtar | Not |
|---|---|---|---|
| **eCFR API** | `ecfr.gov/developers/documentation/api/v1` | Gerekmez | Günlük güncel CFR; başlık/bölüm hiyerarşisi, **point-in-time sürümler**, tam XML, ajans listeleri. GPO bulk XML'den türetilir. |
| **Federal Register API** | `federalregister.gov/developers/documentation/api/v1` | **Gerekmez** | CSV/JSON; NPRM/Final Rule, Public Inspection; 1994'ten. RIA için kural-yapım gerekçesi kaynağı. |
| **GovInfo** | `govinfo.gov` (Data.gov) | GovInfo anahtarı | CFR yıllık baskı + bulk XML repo. Güncel takip için eCFR tercih edilir. |
| **Regulations.gov API** | `regulations.gov` | Anahtar (api.data.gov) | Kamu yorumları (docket) — RIA paydaş analizi için. |
| **openFDA** | `api.fda.gov` | Anahtarsız 240/dk; anahtarla 240/dk + 120.000/gün | Elasticsearch tabanlı. Endpoint'ler aşağıda. `limit` max 1000; `skip`+`limit` ≤ 25.000. |

**openFDA endpoint envanteri:** `drug/event` (FAERS — 21M+ advers olay, 2004'ten, çeyreklik 3+ ay gecikmeli); `drug/label` (SPL/HL7 XML); `drug/ndc`; `drug/enforcement` (recall); `drug/drugsfda`; `device/*` (510(k), PMA, MAUDE 24M+, recall, classification, UDI); `food/event`, `food/enforcement`; `other/*` (NSDE, substance). **Orange Book / Purple Book** kısmen openFDA + ayrı indirme.

> **Uyarı:** openFDA verisi "klinik/üretim kullanımı için doğrulanmamıştır"; karşılaştırma/farmakovijilans sinyali için kullanılır, resmî klinik karar için değil.

<a id="3"></a>
## §3. Birleşik Krallık — legislation.gov.uk (Akoma Ntoso)

Akoma Ntoso'yu resmî olarak destekleyen az sayıdaki ulusal sistemden biri; **karşılaştırmalı hukukta yapısal kıyas için altın standart**.

- **RESTful içerik müzakeresi:** herhangi bir mevzuat URL'sine ek-uzantı: `/data.xml` (CLML — Crown Legislation Markup Language), **`/data.akn`** (Akoma Ntoso, OASIS LegalDocML), `/data.html` (AKN'nin HTML5 serileştirmesi), `/data.rdf` (metadata), **`/data.feed`** (Atom — zengin metadata, ~20 sonuç/sayfa, sayfalama), `/data.pdf`, `/data.xht`.
- **FRBR tabanlı** (Work/Expression/Manifestation). **`<ukm:UnappliedEffects>`** metadatası uygulanmamış değişiklikleri işaretler — yürürlük takibi için kritik.
- Lisans: Open Government Licence v3.0. XSLT dönüşümleri GitHub'da açık.

<a id="3b"></a>
## §3b. İsviçre — Fedlex SPARQL (CH birincil metin)

**Neden burada:** CH birincil metni bu filoda yalnız `Fedlex Swiss` **companion**'ına bağlıydı; o yetkilendirme beklerken tanımlı degrade yolu Ansvar **çerçeve** taramasıydı — çerçeve taraması birincil metin DEĞİLDİR. Uç anahtarsız ve canlı olduğu için programatik yedek yazıldı (2026-08-08 ölçümü).

- **Uç:** `https://fedlex.data.admin.ch/sparqlendpoint` — anahtarsız, `GET` + `query` parametresi, `Accept: application/sparql-results+json`.
- **Ontoloji:** jolux (`http://data.legilux.public.lu/resource/ontology/jolux#`) + SKOS. SR numarası `classifiedByTaxonomyEntry/skos:notation` üzerinden gelir.
- **Kimlik:** ELI. Konsolide derleme `eli/cc/…`, Bundesblatt/taslak `eli/fga/…`.

### ⚠️ İki ölçülmüş tuzak

**1. Taslak tuzağı.** SR numarasını yalnız `skos:notation` ile aramak **Bundesblatt taslağını** döndürebilir. Ölçüm: SR `812.21` sorgusunun İLK sonucu `eli/fga/2025/3018` — başlığı `… (Entwurf)`. "Yürürlükteki birincil metin" istiyorsanız `a jolux:ConsolidationAbstract` (ya da URI'de `eli/cc/`) filtresi **zorunludur**.

**2. İfade çoğaltması.** Bir eser dil/ifade başına tekrarlandığı için filtresiz sorgu özdeş satırlar üretir (ölçüm: 5 özdeş satır). **`DISTINCT` şarttır.**

### Doğrulanmış sorgu

```sparql
PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?act ?srn ?title WHERE {
  ?act a jolux:ConsolidationAbstract ;
       jolux:classifiedByTaxonomyEntry/skos:notation ?srn ;
       jolux:isRealizedBy ?expr .
  ?expr jolux:language <http://publications.europa.eu/resource/authority/language/DEU> ;
        jolux:title ?title .
  FILTER(str(?srn) = "812.21")
}
```

Koşum sonucu: `https://fedlex.data.admin.ch/eli/cc/2001/422` · SR `812.21` · *"Bundesgesetz vom 15. Dezember 2000 über Arzneimittel und Medizinprodukte (Heilmittelgesetz, HMG)"* — İsviçre'nin beşeri tıbbi ürün ve tıbbi cihaz temel kanunu, yani sağlık mevzuatı mukayesesinin CH ayağı.

Dil URI'si değiştirilerek FRA/ITA ifadeleri alınır (`…/authority/language/FRA`, `…/ITA`).

**Degrade:** Fedlex Swiss companion bağlıysa o birincildir; bağlı değilse bu uç kullanılır ve çıktı `mcp_verified=false` + `confidence_label.mcp_unavailability` taşır. İkisi de erişilemezse CH satırı `manual_required` (Fedlex portal deep-link) — asla uydurma.

---

<a id="4"></a>
## §4. Avrupa İçtihat ve Çok-Ülke Portalları

| Kaynak | Erişim | Not |
|---|---|---|
| **CURIA / InfoCuria** (`curia.europa.eu`) | Web + yapılandırılmış arama | ABAD içtihatı; 24 dil, full-text + metadata, Boolean/yaklaşık arama. |
| **HUDOC** (`echr.coe.int`) | Web (HTML/PDF/Word) | AİHM kararları. **ECHR-OD** projesi 2010-2023 standart açık veri + API sağlar (resmî değil, akademik). |
| **N-Lex** | Web portal | AB üye devletlerinin ulusal mevzuat veritabanlarına tek-durak köprü. |

ELI/ECLI çoğu üye devlette kısmen benimsenmiştir (örn. Avusturya tam knowledge-graph uygulaması yapmıştır — bkz. §9 Türkiye önerisi).

<a id="5"></a>
## §5. Asya-Pasifik (Mevcut Yargı Bölgeleri) Programatik Uçlar

| Ülke | Mevzuat açık veri | İlaç/cihaz regülatörü | Not |
|---|---|---|---|
| **Japonya** | e-Gov Data Portal (`data.e-gov.go.jp`), Digital Agency (`digital.go.jp`) | PMDA (İngilizce DB, çoğunlukla web) | e-LAWS yasa/yönetmelik açık veri. |
| **Güney Kore** | `data.go.kr` (ulusal açık veri portalı) | MFDS açık veri (data.go.kr üzerinden) | — |
| **Singapur** | `sso.agc.gov.sg` (Singapore Statutes Online; "gayri resmî metin, otoritatif değil" uyarısı), `data.gov.sg` + `developer.tech.gov.sg` | HSA (web) | data.gov.sg açık API + APEX Cloud API yönetimi. |
| **Avustralya** | `legislation.gov.au` (Federal Register of Legislation), `api.gov.au` katalogu, `data.gov.au` (CKAN) | TGA (ARTG arama) | Mevzuatta yürürlük tarihi açık verilir. PBS için bkz. §8. |
| **Yeni Zelanda** | `legislation.govt.nz`, `data.govt.nz` API katalogu | Medsafe/CARM, PHARMAC | digital.govt.nz API rehberi. |

<a id="6"></a>
## §6. Yeni Yargı Bölgeleri — Kanada, Brezilya, Suudi Arabistan, BAE

### 6.1. Kanada (en olgun yeni eklenti)
| Kaynak | Uç | Anahtar | Not |
|---|---|---|---|
| **Health Canada Drug Product Database (DPD) API** | `https://health-products.canada.ca/api/drug/` | Gerekmez | JSON + XML; ~47.000 ürün (onaylı/pazarlanan/dormant/iptal; human/veterinary/radiopharmaceutical/disinfectant). Parametreler: id, ingredientname, lang, type; endpoint'ler aktif madde/marka/DIN/firma/form/yol/ATC. Gece güncellenen ZIP ekstre (open.canada.ca). |
| **Canadian Clinical Drug Data Set (CCDD)** | open.canada.ca / Infoway | Gerekmez | DPD'den standart terminoloji modeli. |
| **Justice Laws Website** | `laws-lois.justice.gc.ca` | — | Federal kanun/yönetmelik, XML erişimi. |
| **open.canada.ca (CKAN)** | CKAN REST | Okuma anahtarsız | OpenAPI spec mevcut. |
| **CDA-AMC (eski CADTH)** | `cda-amc.ca` (web/PDF) | — | 1 Mayıs 2024'te isim değişti; HTA raporları PDF, özel API yok. |

### 6.2. Brezilya
| Kaynak | Uç | Not |
|---|---|---|
| **LexML Brasil** | `lexml.gov.br/apidata`, `/open-data` (JSON) | Norm/teklif/içtihat/doktrin; **URN-LEX** tanımlayıcıları (`urn:lex:br:federal:...`), schema.org Legislation, CC BY 4.0. Senato dados-abertos API (norma detay: tip/numara/yıl). |
| **ANVISA dados abertos** | `gov.br/anvisa` + `api.anvisa.gov.br` | İlaç regülatörü; PDA (Decreto 8.777/2016). |
| **dados.gov.br** + **apidadosabertos.saude.gov.br** | Federal + Sağlık Bakanlığı (DEMAS) API | — |
| **Diário Oficial da União** + **CONITEC** | Web | Resmî gazete + HTA (birincil). |

### 6.3. Suudi Arabistan
| Kaynak | Uç | Not |
|---|---|---|
| **Saudi Open Data Platform** | `open.data.gov.sa` | 2025 itibarıyla **11.439+ veri seti, 172 kuruluş**; CSV/JSON/XML + API; okuma kayıtsız; Open Data Commons Attribution License; SDAIA/NDMO yönetimi. Developers + Publishers API kılavuzları. İlke: open by default, machine-readable, free. |
| **SFDA** (Saudi Food and Drug Authority) | `sfda.gov.sa` | Açık veri; çoğunlukla web/indirme. |
| **Bureau of Experts at the Council of Ministers** | `boe.gov.sa` | Mevzuat (birincil, web). |

### 6.4. Birleşik Arap Emirlikleri
| Kaynak | Uç | Erişim | Not |
|---|---|---|---|
| **UAE Legislation Portal** | `uaelegislation.gov.ae` | **WEB-ONLY** | Cabinet Genel Sekreterliği; public API/bulk yok; tekil PDF (`/legislations/{id}/download`); AR+EN; 1971'den 1.000+ yasa. (moj.gov.ae + Resmî Gazete paralel, web.) |
| **MOHAP Open Data API** | `mohap.gov.ae/en/open-data/open-data-api` | API + statik dosyalar | UAE'nin en makine-okunur sağlık kaynağı; kayıtlı ilaç listesi; şirketler için onboarding (src.opendata@mohap.gov.ae). |
| **DoH Abu Dhabi** | `doh.gov.ae/resources/opendata` | Web panolar | FCSC portalında kuruluş olarak görünür. Shafafiya/Malaffi klinik sistem (açık veri değil). |
| **DHA (Dubai)** | `dha.gov.ae` | Web + kimlik-gated | NABIDH (HL7 API, lisanslı tesis), Sheryan (lisanslama). |
| **Bayanat.ae / FCSC** | `admin.bayanat.ae/api/opendata/GetDatasetResourceData?resourceID={id}&query={q}&limit={n}` | CKAN REST | 2.600+ veri seti, EN/AR; public okuma; UAE Open Data Policy. |

> **Kritik geçiş uyarısı (2025-26):** UAE'de ilaç ruhsatlandırma işlevi yeni **Emirates Drug Establishment (EDE)**'ye taşınmaktadır — UAE ilaç verisinin yeni birincil otoritesi. MOHAP kaynağına atıf öncesi güncel otorite yeniden doğrulanmalı.

<a id="7"></a>
## §7. Model Bağlam Protokolü (MCP) Sunucuları

MCP ekosistemi olgunlaşmıştır; aşağıdaki sunucular Lex-Sanitas'ın araç katmanını hızlandırabilir. **Benimseme kuralı:** Bir kaynak için API kararlıysa MCP sarmalayıcısı tercih edilir; web-only ise Fetch+parse fallback kullanılır.

| MCP sunucusu | Kapsam | Anahtar | Lex-Sanitas kullanımı |
|---|---|---|---|
| **open-legal-compliance-mcp** (GitHub: TCoder920x) | ABD USC/CFR (GovInfo), ABD içtihat (CourtListener), AB (EUR-Lex) | GOVINFO_API_KEY zorunlu; CONGRESS/COURTLISTENER/OPENSTATES/CANLII opsiyonel | COMPARATIVE_LAW (ABD/AB emsal), ANALYZE |
| **BioMCP** (GenomOncology) | PubMed/PubTator3, bioRxiv/medRxiv, Europe PMC, ClinicalTrials.gov, NCI Trials, OncoKB | Bazı uçlar anahtarsız | Klinik kanıt — DRAFT/RIA/COMPARATIVE klinik bölümleri |
| **ClinicalTrials.gov MCP** (cyanheads/aafjes) | API v2, ~485.000 çalışma, 221 ülke | Anahtarsız | EX_POST (klinik etkinlik), DRAFT |
| **healthcare-mcp-public** (Cicatriiz) | openFDA, PubMed, Health.gov, ClinicalTrials, ICD-10, medRxiv | Smithery kurulumu | Çok-amaçlı klinik destek |
| **openFDA MCP** (taru0208) | FAERS, recall, MAUDE | Anahtarsız | Farmakovijilans karşılaştırması |
| **Akademik MCP'ler** | PubMed, arXiv, Semantic Scholar, Web of Science | Bazıları anahtar ister | Bilimsel temellendirme (yardımcı) |
| **health-policy-mcp** (Cloudflare Worker — Cureonics; **20 araç canlı, 2026-08-07 probe**) | ABD eCFR/FedReg/GovInfo/Congress, Kanada Justice Laws (XML, yalnız fetch), Japonya e-LAWS, Avustralya FRL (OData), İspanya BOE, İrlanda eISB, Çin NPC, Meksika DOF (best-effort), `semantic_search` (Workers AI), `legal_distill_start`/`_result` | Anahtarlar Worker secret'ında; OAuth 2.1 connector | Katman-2 programatik erişim (Türkiye-dışı + Ansvar-dışı). **KAPSAM DIŞI:** AB/UK→Open Law · DE→german-law · CH/FR/IT/NL/SE/DK/FI/AT/PL→Ansvar/Fedlex Swiss · TR→mevzuat/titck · EuroVoc+data.europa.eu→SARMALANMADI |

> **Mimari not (v1.1 — 2026-08-07 DÜZELTMESİ).** Katman-2 sarmalayıcısı **canlıdır ama adı ve kapsamı değişmiştir**: `lex-sanitas-mcp` → **`health-policy-mcp`** (2026-06-29 yeniden adlandırma + yeniden kapsamlandırma). Eski uç `https://lex-sanitas-mcp.cureonics.workers.dev/mcp` 2026-08-07 probe'unda **HTTP 404 — ÖLÜDÜR**; canonical uç `https://health-policy-mcp.cureonics.workers.dev/mcp` (aynı probe: 401 = auth kapısı çalışıyor). Türkiye iç hukuku eskisi gibi Mevzuat/Yargı/YokTez/TİTCK MCP'lerinde kalır.
>
> **Yeniden kapsamlandırmada KALDIRILAN araçlar — bunlar artık ÇAĞRILAMAZ, atıf kaynağı gösterilemez:**
> - `cellar_sparql` · `cellar_fetch_document` · `eurlex_expert_search` · `uk_legislation_fetch` → **AB + UK artık `Open Law` companion'ın işidir.**
> - `germany_law_search` / `germany_law_get` (NeuRIS beta) → **`german-law` MCP** (wire'lı, :8307; ücretsiz korpus: 8 statü aracı işlevsel, 11 araç dürüst "ücretsiz katmanda yok" döner).
> - `fedlex_sparql` / `fedlex_fetch_document` → **`Fedlex Swiss` / `Ansvar` companion** (wire'lı DEĞİL).
> - `eurovoc_concept_lookup` · `dataeuropa_dataset_search` → **hiçbir sunucu sarmıyor** → web-birincil; EuroVoc URI'si programatik teyit EDİLEMEZ, dolayısıyla ÜRETİLEMEZ (registry `eu.eurovoc`: `open_primary_source`).
> - `health_canada_dpd` · `openfda` · WHO ICD-11/GHO · Légifrance → klinik/regülatuar konnektörlere taşındı.
>
> **Sarılı KALAN (2026-08-07 canlı araç listesiyle doğrulandı, 20 araç):** ABD `ecfr_get`/`ecfr_versions`/`federal_register_search`/`govinfo_search`/`congress_search` · `canada_justicelaws_fetch` (**yalnız fetch — arama ucu yok**) · `japan_elaws_search`/`_fetch` · `australia_legislation_search`/`_fetch` · `spain_boe_fetch` · `ireland_eisb_fetch` · `china_law_recent`/`china_law_detail` · `mexico_dof_nota` · `semantic_search` · `legal_distill_start`/`legal_distill_result` · genel `search`/`fetch`.
>
> ⚠️ **Bu bölümün altındaki v2.7.0 "Sarılan (W)" listesi TARİHSELDİR** — 2026-06-07 tarihli o probe'un sonucudur ve yukarıdaki düzeltmeyle geçersiz kılınmıştır. Araç adı için tek doğruluk kaynağı canlı `tools/list`'tir.
>
> **D-sınıfı (web-only — SARMALANMADI; `web_primary` kalır; canlı probe gerekçesi):**
> - **Brezilya LexML** — `/apidata` ve `/busca/SRU` uçları **404**; resmî programatik uç doğrulanamadı.
> - **Suudi Open Data** (`open.data.gov.sa`) — **erişilemedi/timeout**; CKAN sözleşmesi doğrulanamadı.
> - **Yeni Zelanda legislation** — API yalnızca **`202` async-generate/poll** döndürür; temiz senkron uç yok.
> - **Singapur SSO** — statute metni için API **yok** (data.gov.sg yalnızca dataset; SSO "gayri resmî metin").
> - **UAE Legislation Portal / Saudi BoE / Brezilya Diário Oficial-CONITEC** — public API yok.
>
> **Ertelendi:** **Kore** (data.go.kr, `KR_DATA_GO_KR_KEY` — anahtarlı; bu sürümün anahtarsız kapsamı dışı) ve **Dalga 3** (EUR-Lex bulk, UAE MOHAP/Bayanat — secret/onboarding lead-time).

<a id="8"></a>
## §8. Klinik Kanıt ve Sağlık Teknolojisi Değerlendirme (HTA) Kaynakları

### 8.1. Programatik (yüksek öncelik)
| Kaynak | Uç | Anahtar | Not |
|---|---|---|---|
| **WHO GHO OData API** | `https://ghoapi.azureedge.net/api` | Gerekmez | Boyut/gösterge sorgulama (XML/JSON); `$filter=contains(IndicatorName,'...')`, `/api/DIMENSION/COUNTRY/DimensionValues`. Hastalık yükü/sonuç verisi. |
| **WHO ICD-11 API** | `icd.who.int/icdapi` | Anahtar (sitede) | ICD-10/11 sınıflandırma. |
| **Epistemonikos API** | `api.epistemonikos.org` | — | Sistematik derleme + ilgili belgeler; 30 veritabanı (Cochrane/PubMed/EMBASE/CINAHL); 9 dil; PICO; 115.000+ belge. Kanıt-sentezi modunun çekirdeği. |
| **openFDA FAERS** | `api.fda.gov/drug/event` | bkz. §2 | Farmakovijilans, JSON. |
| **PBS API (Avustralya)** | `data.pbs.gov.au` (`info.data.pbs.gov.au/api/open-api-v1-0-0`) | Embargo uçları giriş ister | REST + CSV, aylık güncel. **Legacy XML/Text 1 Mayıs 2026'da kaldırılıyor, PBS Offline 1 Mart 2026** — API/CSV tek kaynak olur. |
| **Fransa HAS** | `data.gouv.fr` ("Haute Autorité de santé") | — | **HTA kuruluşları arasında en makine-okunur**: Commission de la Transparence SMR/ASMR (ilaç), CNEDiMTS (cihaz), sertifikasyon, IQSS göstergeleri; CSV/XLSX + API; Licence Ouverte v2. |

### 8.2. Web-only / kısıtlı (Fetch+parse gerekir)
| Kaynak | Durum |
|---|---|
| **EUnetHTA / EU HTA Regulation (HTAR, (EU) 2021/2282)** | JCA 12 Ocak 2025'ten; ilk onkoloji JCA 27 Mart 2025; raporlar **şablon-PDF** (makine-okunur akış değil); HTA IT Platform EU Login-gated; EC belgeleri genel CC BY 4.0; 2025 ortasında hacim minimal. |
| **Almanya IQWiG + G-BA** | PDF/web; API yok. G-BA AMNOG §35a kararları 3 ay içinde. |
| **Kanada CDA-AMC, Quebec INESSS** | Web/PDF; INESSS kararları Quebec'te bağlayıcı (Fransızca birincil). |
| **INAHTA International HTA Database** (`database.inahta.org`) | Web-only bibliyografik indeks, ~16.000 kayıt; **bulk/API yok**; 2023 çalışmasında kapsam eksik bulundu (NICE TA örneğinin %75'i bulunamadı) — **keşif aracı, kapsamlı değil**. |

### 8.3. İlaç bilgi / terminoloji / fiyat / epidemiyoloji
- **DrugBank**: akademik indirme (v5.1.12); ticari Clinical API (bölgeli, JSON); DDI + ADMET.
- **RxNorm / DailyMed / MedlinePlus** (NLM): RxNorm REST API, DailyMed SPL.
- **WHO INN, MedDRA**: standart isimlendirme / advers olay terminolojisi.
- **OECD Health Statistics** (OECD.Stat SDMX API), **PPRI**, **WHO MedNet**, **MSH Price Guide**: fiyat/erişim.
- **IHME GBD** (`vizhub.healthdata.org/gbd-results`): GBD 2023, 204 ülke; **genel veri API'si YOK** ("no data APIs available"); query tool + GHDx CSV; tek istekte max 100.000 satır; ticari kullanım lisans gerektirir.
- **GLOBOCAN** (IARC) kanser insidans/mortalite; **Our World in Data** indirilebilir CSV.

<a id="9"></a>
## §9. Hukukî Tanımlayıcı Standartları (ELI / ECLI / Akoma Ntoso / FRBR)

| Standart | Tanım | Lex-Sanitas için anlam |
|---|---|---|
| **ELI** (European Legislation Identifier) | HTTP URI + RDFa ile mevzuata kalıcı, makine-okunur kimlik; FRBR uyumlu | AB + üye devlet mevzuatına deterministik atıf; konsolide sürüm çözümleme |
| **ECLI** (European Case Law Identifier) | Mahkeme kararlarına standart Avrupa kimliği | İçtihat atfında uydurma numara riskini ortadan kaldırır |
| **Akoma Ntoso (OASIS LegalDocML)** | Yasal belgeler için XML şeması (madde/recital/ek yapısı) | Madde-düzeyi diff, karşılaştırma, değişiklik tekniği |
| **CELEX** | AB belgelerine benzersiz numara | EUR-Lex/CELLAR erişiminin anahtarı |
| **URN-LEX** | Mevzuat için URN şeması (Brezilya LexML kullanır) | Çok-ülke tanımlayıcı uyumu |
| **FRBR** | Work/Expression/Manifestation katmanlaması | Sürüm (orijinal vs konsolide) ayrımının temeli |

> **Türkiye mimari önerisi.** Lex-Sanitas, Türkiye mevzuatını **ELI/ECLI ve Akoma Ntoso ile modellemeyi** öneren çıktılar üretebilir (Avusturya'nın tam knowledge-graph uygulaması emsal). Bu, hem iç tutarlılık (madde-düzeyi sürüm yönetimi) hem AB karşılaştırması için en yüksek otomasyon kaldıracını sağlar; DRAFT ve COMPARATIVE_LAW modlarında bir reform önerisi unsuru olarak değerlendirilebilir.

<a id="10"></a>
## §10. Erişim Disiplini, Lisans ve Bilgi Sınırı Uyarıları

**Yetkilendirme/limit özeti:** Anahtarsız ve serbest: CELLAR (SPARQL+REST), data.europa.eu, eCFR, Federal Register, legislation.gov.uk, openFDA (limitli), DPD, open.canada.ca (okuma), WHO GHO, LexML, open.data.gov.sa (okuma), Bayanat (okuma). Anahtar/giriş gerektiren: GovInfo, Regulations.gov, openFDA yüksek limit, WHO ICD-11, EMA Clinical Data + SPOR, EUR-Lex data dump, PBS embargo uçları, MOHAP onboarding.

**Lisans çeşitliliği:** Open Government Licence v3.0 (UK), CC BY 4.0 (EC belgeleri, LexML), Licence Ouverte v2 (Fransa), Open Data Commons Attribution (Suudi), UAE Open Data Policy. **Her kaynağın koşulu ticari/otomatik kullanım öncesi doğrulanmalıdır.**

**Bağlayıcı uyarılar:**
1. **"Klinik kullanım için doğrulanmamış"** — openFDA ve benzeri kaynaklar resmî klinik karar için değil, karşılaştırma/sinyal içindir.
2. **IHME GBD'nin genel API'si yoktur** ve ticari kullanım lisans gerektirir (100.000 satır/istek sınırı) — GHDx dosya indirmesiyle entegre edilir.
3. **INAHTA HTA Database kapsamı eksiktir** (bağımsız doğrulama) — tek kaynak olarak güvenilmez.
4. **EU JCA raporları henüz makine-okunur akış değildir** (şablon-PDF); kararlı veri hacmi beklenmelidir.
5. **UAE/Suudi mevzuat portalları çoğunlukla web-only**; UAE ilaç otoritesi MOHAP→EDE geçişinde — birincil otorite yeniden doğrulanmalı.
6. **"Gayri resmî metin" damgaları** (Singapur SSO, bazı çeviriler) — otoritatif metin için resmî kaynak teyidi şarttır.
7. **Üçüncü-taraf aggregator'lar** (Apify, Microsoft connectors) birincil değildir; resmî endpoint tercih edilir.
8. R8 §5.5'teki **üç doğrulama kuralı** (sürüm/yürürlük/çeviri) bu katmanda da bağlayıcıdır; v2.5'te buna **programatik erişim önceliği** dördüncü kural olarak eklenir (bkz. SKILL.md §5.5).

<a id="11"></a>
## §11. Mod × Kaynak Entegrasyon Matrisi

Programatik (API/SPARQL) erişimi olan kaynaklara öncelik verilir; bunlar otomatik doğrulama için en değerlidir.

| Mod | Birincil programatik kaynaklar | İkincil/web-only |
|---|---|---|
| **DRAFT (Mod 1)** | CELLAR (AB direktif/regülasyon şablonu + ELI), legislation.gov.uk (Akoma Ntoso emsal), DPD/LexML (ürün/norm), WHO ICD-11/GHO | EU JCA, IQWiG/G-BA |
| **AMEND (Mod 2)** | CELLAR REST (madde-düzeyi konsolide), legislation.gov.uk UnappliedEffects, eCFR point-in-time | — |
| **ANALYZE (Mod 3)** | CELLAR SPARQL, eCFR, openFDA, CURIA/HUDOC (ECLI) | INAHTA (keşif) |
| **COMPLY (Mod 4)** | CELLAR (ELI/ECLI doğrulama), legislation.gov.uk versiyonlama | — |
| **OPINE (Mod 5)** | Epistemonikos, BioMCP, PubMed MCP | HAS, NICE |
| **RIA (Mod 6)** | Federal Register + Regulations.gov (yorum), openFDA/FAERS, IHME GBD (GHDx), WHO GHO, **HAS (data.gouv.fr)**, **PBS API** | EU JCA, OECD.Stat |
| **COMPARATIVE_LAW (Mod 7)** | CELLAR, legislation.gov.uk, eCFR, LexML, DPD, SSO, legislation.gov.au, ECLI içtihat | EUnetHTA, INESSS, CDA-AMC |
| **TBMM_KANUN_TEKLIFI (Mod 8)** | Akoma Ntoso emsalleri (UK/LexML/Avusturya), CELLAR (ELI), tam klinik kanıt MCP'leri | tüm HTA web-only |
| **EX_POST_EVALUATION (Mod 9)** | openFDA recall/FAERS zaman serisi, **PBS API tarihsel**, WHO GHO OData trend, point-in-time eCFR/CELLAR, EU JCA çıktıları | INAHTA, MEDULA (web) |

---

*Bu dosya v2.5'te eklenmiştir. Buradaki endpoint URL'leri ve erişim koşulları erişim anına bağlıdır; sürekli değiştiklerinden, kritik bir görevde kullanılmadan önce ilgili resmî dokümantasyon (developer/API sayfası) üzerinden yeniden doğrulanmalıdır. Endpoint davranışı değişen kaynaklar (örn. CELLAR Virtuoso 8 geçişi, PBS legacy kaldırma, UAE EDE geçişi) için §10 uyarıları bağlayıcıdır.*
