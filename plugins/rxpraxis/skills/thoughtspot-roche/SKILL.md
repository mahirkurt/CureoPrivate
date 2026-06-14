---
name: thoughtspot-roche
description: >
  Roche EMEA ThoughtSpot MCP (Spotter) üzerinden IQVIA MIDAS küplerine (MIDAS
  Monthly, MIDAS Disease Monthly, MIDAS Quarterly) oturum-tabanlı sorgu
  protokolü. Roche internal pharma sales, ATC2/3/4 hiyerarşisi,
  molecule/manufacturer/corporation kırılımı, cross-country pazar büyüklüğü,
  fiyat tavanı, eşdeğer grup, jenerik/biyobenzer fizibilite, Türkiye Ürün
  Geliştirme cross-country layer, indikasyon-bazlı pazar payı için USE THIS
  SKILL. Tetikleyiciler: ThoughtSpot, Spotter, MIDAS, IQVIA, Swiss Franc sales,
  ATC breakdown, disease landscape, manufacturer share, molecule trend, audited
  sales, dashboard, küpten çek, MIDAS'tan al, global satış, eşdeğer grup pazar,
  n_countries, ülke kırılımı, ham değer çıkarımı, CSV export. pharmaintel ve
  medical-research upstream; pharmaintel, pharmapatent, carbon-html-report,
  carbon-pptx downstream composable. Oturum-tabanlı Spotter akışı, ham-hücre
  sınırlılığı, REST getAnswer-first çıkarımı, no-fabrication, Roche confidential
  handling içerir. When in doubt, USE this skill.
---

# thoughtspot-roche — Roche EMEA ThoughtSpot MCP Operasyonel Protokolü

> **Plugin entegrasyon notu (rxpraxis).** Bu skill rxpraxis süiti altında çalışırken connector envanteri, fallback zincirleri ve tek-sefer TİTCK/MIDAS disiplini için [../../CONNECTORS.md](../../CONNECTORS.md) ve [../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md) **NORMATİFTİR**. Aşağıdaki Path A / Path B MIDAS çıkarımı ve ham-hücre asimetrisi disiplini, standalone kullanım için korunmuştur; süit bağlamında çakışma hâlinde plugin sözleşmesi üstündür.


**Skill type:** Data orchestration (MCP-first + REST-extraction fallback)
**Version:** 2.0.0
**Tenant:** `emea.thoughtspot.roche.com`
**Authenticated user:** `Mahir Kurt (kurtm1)`
**Data classification:** Roche confidential — internal use only

> **v2.0.0 — Breaking change uyarısı.** Canlı MCP araç yüzeyi v1.0.0'da
> varsayılan `ping / getRelevantQuestions / getAnswer / createLiveboard`
> dörtlüsünden, **oturum-tabanlı Spotter beşlisine** (`check_connectivity`,
> `create_analysis_session`, `send_session_message`, `get_session_updates`,
> `create_dashboard`) geçmiştir. Ayrıca **MCP ham hücre değeri döndürmez** —
> ham sayısal veri yalnızca render edilen yanıtta yaşar veya MCP-dışı REST
> `searchdata` ile çekilir. Bu sürüm her iki gerçeği de kodlar.

---

## 1. What This Skill Does

ThoughtSpot Roche EMEA tenant'ına bağlanan oturum-tabanlı Spotter MCP üzerinden, IQVIA MIDAS-sınıfı küplere doğal-dil analitik sorgu çevirir; sonucu Türkçe profesyonel rapor formatına dönüştürür. Birincil kullanım vektörleri:

- **Pazar büyüklüğü ve trend sorgulamaları** — ATC2/3/4, disease, molecule, manufacturer/corporation ekseninde CHF/Standard Units bazında satış kırılımı
- **Cross-country pazar kalibrasyonu** — pharmaintel'in Türkiye Ürün Geliştirme akışına global benchmark sağlar
- **Fiyat tavanı / eşdeğer grup analitiği** — TİTCK fiyat tavanı kararnameleri için MIDAS referans pazarlardan dış kalibrasyon
- **Therapeutic area landscape** — onkoloji, hematoloji, immünoloji indikasyon-bazlı pazar haritalama
- **Coğrafi ayak izi analitiği** — molekül başına `n_countries`, top-country yoğunlaşması, Herfindahl-Hirschman (HHI) coğrafi dağılım
- **Manufacturer competitive intelligence** — portföylerin global trend kıyaslaması

Skill **veri üretmez**; var olan Roche internal MIDAS verisini sorgulayıp normalize eder. **Erişilemeyen veride asla rakam uydurmaz** (bkz. G9). Kullanım tüm Roche compliance kurallarına tabidir.

---

## 2. MCP Architecture

### 2.1 Connection Profile

| Parametre | Değer |
|---|---|
| Endpoint | `https://agent.thoughtspot.app/mcp` |
| Tenant | `emea.thoughtspot.roche.com` |
| Auth | Kullanıcı kimliği üzerinden hidratlı; ek API key yok |
| İmza | Render edilen yanıtın `iframe_url`'i authenticated session'a bağlıdır |

### 2.2 Tool Inventory — Oturum-Tabanlı Spotter (DOĞRULANMIŞ, v2.0.0)

Canlı MCP **beş** araç sunar (2026-06 itibarıyla doğrulandı):

| Araç | Rol | Operasyonel Statü |
|---|---|---|
| `check_connectivity` | Sağlık/kimlik kontrolü (`{"success": true}`) | **Pre-flight zorunlu** |
| `create_analysis_session` | Analitik oturum açar; `analytical_session_id` döner. `data_source_id` opsiyonel — verilmezse ajan otomatik seçer | **Birincil — her akışın başı** |
| `send_session_message` | Oturuma doğal-dil sorgu/follow-up gönderir; `additional_context` ile arka plan bilgisi iletilir | **Birincil iş yükü** |
| `get_session_updates` | Ajan yanıtını poll eder; `text_chunk` + `answer` blokları döner. `is_done:false` iken tekrar çağrılır | **Birincil — sonuç toplama** |
| `create_dashboard` | Biriken `answer_id`'lerden kalıcı dashboard | İleri kullanım — opsiyonel |

### 2.3 v1.0.0 → v2.0.0 Araç Eşlemesi (Migration Map)

| v1.0.0 (kullanımdan kalktı) | v2.0.0 karşılığı |
|---|---|
| `ping` | `check_connectivity` |
| `getRelevantQuestions` | **Karşılığı yok** — oturum modeline gömülü; ayrı keşif aracı sunulmuyor |
| `getAnswer` (tek-call, CSV döndürür varsayımı) | `create_analysis_session` → `send_session_message` → `get_session_updates` (poll) — **ham CSV döndürmez**, bkz. §2.4 |
| `createLiveboard` | `create_dashboard` |

### 2.4 KRİTİK SINIRLILIK — MCP Ham Hücre Döndürmez

Doğrulanmış davranış: `get_session_updates` yalnızca **doğal-dil özet** (`text_chunk`) ve bir **`answer` meta nesnesi** (`answer_id`, `answer_query` arama ifadesi, `iframe_url`) döndürür. **Tablo hücre değerleri (gerçek CHF rakamları) bu akışta YER ALMAZ.** Ajanın kendisi dahi altta yatan hücreleri görmediğini açıkça beyan eder.

**Operasyonel sonuç:**
- Niceliksel rapor (gerçek rakamlı tablo) gerektiğinde, ham değerler **ya** render edilen yanıttan native export ile **ya da** MCP-dışı REST `searchdata` ile çekilir (bkz. §5).
- Bu skill **hiçbir koşulda görselden okunamayan rakamı uydurmaz** (G9). MCP yanıtı yalnız yapı/şema/sıralama doğrulaması için yeterlidir; sayı için REST yolu zorunludur.

---

## 3. Datasource Registry

`assets/datasource-registry.yaml` merkezi GUID + boyut kataloğunu tutar. Doğrulanmış envanter (2026-06):

| Datasource | Granülarite | Kapsam | Tarihçe | Tür |
|---|---|---|---|---|
| **MIDAS Monthly** | Aylık | 36 ülke | 12 yıl | Audited sales |
| **MIDAS Disease Monthly** | Aylık (indikasyon) | 36 ülke | 6 yıl | Disease panel |
| **MIDAS Quarterly** | Çeyreklik | Yalnız Tayvan | 12 yıl | Audited sales |

### 3.1 MIDAS Monthly — Boyut/Metrik Envanteri (Doğrulanmış)

| Boyut Kategorisi | Alanlar |
|---|---|
| Coğrafya | Country (36 pazar) |
| **ATC Hiyerarşisi** | ATC2 → ATC3 → ATC4 (kod + Description, üç düzey) |
| Ürün | Product, International Product, International Brand, Pack, International Pack |
| Molekül | Molecule List, Molecule Count |
| Üretici | Manufacturer, International Manufacturer, Corporation |
| Zaman | Date, Month, Quarter, Year, Period |
| Sınıflandırma | Generic Product Classification, Product/Pack Launch Date |

**Ölçütler (7):** Swiss Franc (CHF, ex-manufacturer, cari kur), Local Currency Swiss Franc (sabit kur), Euros, US Dollars, Local Currency Dollar, Units/Standard Units/Counting Units (hacim), KG/International Units (etken madde).

> **ATC kod kuralı:** ATC kodları küçük harftir (ör. antineoplastik ajanlar = `l1`, değil `L01`). Filtre değeri buna göre yazılır.

> **GUID re-doğrulama notu:** v1.0.0 registry'sindeki GUID'ler (`210eb567…`, `7e0a9470…`) eski connector döneminden gelir; oturum-tabanlı Spotter `data_source_id` parametresini bu GUID formatında kabul eder ancak **REST yolu için GUID `metadata/search` ile yeniden çözülmelidir** (bkz. §5 Adım 1). Boş bırakılırsa ajan en uygun kaynağı otomatik seçer.

---

## 4. Mandatory Execution Protocol (Oturum-Tabanlı)

Her ThoughtSpot sorgu akışı bu adımları sırayla uygular:

### Step 1 — Pre-flight (`check_connectivity`)
Yeni oturumun ilk çağrısı her zaman `check_connectivity`. Yanıt `{"success": true}` olmalı; aksi halde akış durur ve kullanıcıya endpoint sağlık sorunu bildirilir. (Gate G1)

### Step 2 — Session Open (`create_analysis_session`)
Analitik oturum açılır. Hedef küp biliniyorsa `data_source_id` verilir; belirsizse boş bırakılır (ajan otomatik seçer). Dönen `analytical_session_id` tüm follow-up'larda yeniden kullanılır (aynı oturum = aynı kaynak seçimi). (Gate G2)

### Step 3 — Query Send (`send_session_message`)
Doğrulanmış prompt kalıbı (§4 pattern listesi, `references/query-templates.md`) ile İngilizce sorgu gönderilir. `additional_context` alanına küp ipucu, para birimi (CHF), istemcinin iframe göremediği gibi arka plan bilgisi yazılır. (Gate G3)

### Step 4 — Poll (`get_session_updates`)
`is_done:true` olana kadar tekrar çağrılır. Bloklar: `text_chunk` (NLG özeti — kullanıcıya akış/ilerleme gösterimi için), `answer` (`answer_id` + `answer_query` + `iframe_url`). **Ham hücre değeri beklenmez** (§2.4). (Gate G10)

### Step 5 — Veri Edinim Yolu Seçimi (DUAL-PATH)

| Çıktı ihtiyacı | Yol |
|---|---|
| Yalnız yapı/şema/sıralama doğrulaması, kalitatif yorum | **Path A** — MCP `answer` meta verisi yeterli |
| **Gerçek rakamlı tablo / CSV / niceliksel rapor** | **Path B** — MCP-dışı REST `searchdata` (bkz. §5) **VEYA** render edilen yanıttan native CSV export |

Path B seçildiğinde §5 REST getAnswer-first akışı çalıştırılır; rakamlar canlı API yanıtından gelir. (Gate G9 — no fabrication)

### Step 6 — (Opsiyonel) Coğrafi Genişletme — `n_countries`
Molekül/ürün liderboard'u alındıktan sonra coğrafi ayak izi isteniyorsa, her satır için ülke-düzeyi sorgu çalıştırılıp `n_countries`, `top_country`, `top_country_share_pct`, `hhi_country` türetilir. Programmatik uygulama: `scripts/ts_getanswer_country_extractor.py`. (Bkz. §6)

### Step 7 — CSV Normalization
İki kaynak biçimi vardır:
- **REST `searchdata` (Path B, önerilen):** Yanıt `contents[0].column_names` + `data_rows` taşır; doğrudan tabloya/CSV'ye eşlenir. Header preamble **yoktur**.
- **Native export / eski getAnswer indirme biçimi:** İlk üç satır Roche extract preamble'ıdır (extract notu + confidential etiket + boş satır) → atlanır. Bilimsel notasyon (`2.82E12`) → Türkçe `2,82 trilyon CHF` formatına dönüştürülür.

Programmatik normalizer: `scripts/normalize_csv.py`. (Gate G5)

### Step 8 — Output Synthesis
Kullanıcı yanıtı: **(a)** Türkçe başlıklı, milyar/trilyon formatlı tablo; **(b)** veri kaynağı yorumu (hangi küp, hangi attribute, mertebe yorumu); **(c)** limitations/caveats (Unclassified payları, time-span belirsizlikleri, CHF mertebe uyarıları, ham-hücre erişim notu); **(d)** provenance (`analytical_session_id` + `answer_id` + `answer_query` + extract timestamp + Roche confidential etiketi). (Gate G6, G8)

### Step 9 — Dashboard Materialization (Opsiyonel, `create_dashboard`)
Biriken `answer_id`'ler ve başlıklar `create_dashboard`'a iletilir; `note_tile` HTML özet taşır. Kalıcı dashboard döner.

---

## 5. REST getAnswer-First Çıkarımı (MCP-Dışı — Ham Değer Yolu)

MCP ham hücre döndürmediğinden (§2.4), niceliksel çıkarım ThoughtSpot **REST API v2.0** ile yapılır. Tüm istek gövdeleri resmî ThoughtSpot Developer dokümanına dayanır (2026-06 doğrulaması).

### Adım 0 — Kimlik (`/api/rest/2.0/auth/token/full`)
`username` + `secret_key` ile tam erişim token'ı alınır (`validity_time_in_sec`). SSO-only tenant'ta trusted authentication etkinleştirilmeli; satır-düzeyi entitlement için `auth/token/custom` kullanılabilir. Dönen `token` Bearer olarak kullanılır.

### Adım 1 — GUID Çözümü (`/api/rest/2.0/metadata/search`)
GUID bilinmiyorsa `metadata` dizisinde `type: LOGICAL_TABLE`, `name_pattern: "<küp adı>"` ile sorgulanır; yanıttan `metadata_id` alınır.

### Adım 2 — Veri Çekimi (`/api/rest/2.0/searchdata`)
Gövde:
```json
{
  "query_string": "[Swiss Franc] [Molecule List] [ATC2] = 'l1' [Date] = 'last 12 months' sort by [Swiss Franc] descending top 10",
  "logical_table_identifier": "<WORKSHEET_GUID>",
  "data_format": "COMPACT",
  "record_offset": 0,
  "record_size": -1
}
```
- Varsayılanlar: `data_format=COMPACT`, `record_offset=0`, `record_size=10`. Tam set için `record_size=-1`.
- Çağrı başına ≤100.000 satır. Kod tabanlı çağrıda `User-Agent` başlığı zorunludur.
- Yanıt zarfı: `data.contents[0].column_names` + `data.contents[0].data_rows`.
- ThoughtSpot Sorgu Dili: sütunlar köşeli parantez `[ ]`, literal değerler tek tırnak; UI seçimi yerine açık token'larla disambiguasyon.
- v1 fallback (tenant v2 kapalıysa): `/callosum/v1/tspublic/v1/searchdata?query_string=...&data_source_guid=...&formattype=COMPACT` + `X-Requested-By: ThoughtSpot` başlığı.

### Çalıştırılabilir Çıkarıcılar (vendor-neutral, env-driven)
| Script | İşlev |
|---|---|
| `scripts/ts_getanswer_extractor.py` | auth → GUID → searchdata → normalize CSV (`rank,molecule,total_chf,share_of_class_pct`) |
| `scripts/ts_getanswer_country_extractor.py` | + molekül başına ülke kırılımı, `n_countries` + top-country + HHI türevleri; iki CSV (özet + uzun-format) üretir |

Kapsamlı REST referansı: `references/rest-getanswer-guide.md`.

---

## 6. Coğrafi Türev Metrikler — `n_countries` ve Yoğunlaşma

Molekül başına ülke satırlarından (pozitif satış = varlık) türetilir:

| Türev Sütun | Tanım |
|---|---|
| `n_countries` | Pozitif denetlenmiş satışı olan ülke sayısı (coğrafi ayak izi) |
| `top_country` / `top_country_share_pct` | En yüksek cirolu ülke ve molekül-içi payı |
| `hhi_country` | Ülke paylarının Herfindahl-Hirschman İndeksi (0 = tam dağınık → 1 = tek ülke) |

Eşik kuralı: "varlık" `> 0` satış olarak tanımlanır; iade/düzeltme kaynaklı negatif/sıfır satırlar ayak izine sayılmaz. Uzun-format çıktı: `molecule,country,chf,pct_of_molecule_total`.

---

## 7. Verification Gates (G1–G10)

| Gate | Ad | Mandatory |
|---|---|---|
| G1 | Pre-flight `check_connectivity` başarılı (`success:true`) | ✅ |
| G2 | Oturum açıldı; datasource registry'de bilinen veya kullanıcı-doğrulanmış/otomatik | ✅ |
| G3 | Sorgu prompt kalıbı doğrulanmış pattern listesinden | ✅ |
| G4 | Sage NLG asimetri fallback disiplini (zayıf NLG → doğrudan sorgu) | ✅ |
| G5 | CSV normalization (REST envelope eşleme veya preamble skip + notasyon dönüşümü) | ✅ |
| G6 | Confidential handling — Roche internal etiketi yansıtıldı; dış-paylaşım uyarısı | ✅ |
| G7 | Cross-cube triangulation (≥2 küp sorgulandığında mantıksal tutarlılık) | Conditional |
| G8 | Currency unit verification — CHF mertebesi sponsor cirosu/pazar boyu mantığıyla kontrol | ✅ |
| **G9** | **No fabrication — görselden okunamayan rakam asla uydurulmaz; ham değer REST `searchdata` veya native export ile alınır; erişim yoksa açıkça beyan edilir** | ✅ |
| **G10** | **MCP raw-cell asimetrisi tanındı — `get_session_updates` ham hücre döndürmez; niceliksel ihtiyaçta Path B (REST) zorunlu** | ✅ |

---

## 8. Composability — Pipe Compatibility

### 8.1 Upstream (`pipe_from`)
| Skill | Tetikleyici akış |
|---|---|
| `pharmaintel` v8+ | Türkiye Ürün Geliştirme cross-country sizing adımı |
| `medical-research` | Disease prevalence + market reality cross-validation |

### 8.2 Downstream (`pipe_to`)
| Skill | Çıktı kullanımı |
|---|---|
| `pharmaintel` v8+ | Commercial & Payer Context empirical foundation |
| `pharmapatent` | Eşdeğer grup pazar boyutu, biyobenzer fırsat, jenerik fizibilite niceliksel ayağı |
| `carbon-html-report` v6+ | Publication-grade HTML/PDF (ülke ısı haritası, liderboard, HHI göstergesi) |
| `carbon-pptx` v1.9+ | Senior leadership/BU review deck'leri |

---

## 9. Bilinen Sınırlılıklar

| Sınırlılık | Etki | Mitigasyon |
|---|---|---|
| **MCP ham hücre döndürmez** | `get_session_updates` yalnız NLG + meta; sayı yok | Path B REST `searchdata` veya native export (§5) |
| Schema discovery yok (ayrı araç) | Küp attribute envanteri keşif sorgularıyla haritalanır | §3.1 envanteri + registry güncellemesi |
| Datasource discovery (MCP) | Otomatik seçim ajana bırakılır; GUID manuel/REST | `metadata/search` ile GUID çözümü (§5 Adım 1) |
| Sage NLG küp-bazında olgun değil | Zayıf NLG küplerde keşif zayıf | Doğrudan-sorgu stratejisi (G4) |
| Türkçe sorgu davranışı | EMEA tenant İngilizce metadata | İngilizce sorgu; çıktı Türkçe |
| Filter/parameter syntax kısmi | Time window/where-clause kısmen haritalı | `last 12 months` + ATC2 filtre doğrulandı; gerisi `references/query-templates.md` |
| Multi-cube join yok | Tek call'da iki küp join yapılamaz | Sıralı sorgu + triangulation (G7) |

---

## 10. Compliance ve Veri Sınıflandırması

- Tüm çıktılar **"Roche confidential material"** bağlamındadır; etiket kullanıcı yanıtında yansıtılır (G6).
- Skill yalnız yetkili Roche internal kullanım içindir; çıktılar Roche data classification policy'sine tabidir.
- Dış paylaşım kullanıcı (Mahir Kurt) sorumluluğundadır; skill kendiliğinden dış-paylaşım onayı vermez.
- `iframe_url` yalnız authenticated session'da erişilir; standalone share link değildir.
- REST `secret_key` ve token'lar koda gömülmez; ortam değişkeni ile sağlanır (`scripts/*` env-driven).

---

## 11. Referans Dosyalar

- `assets/datasource-registry.yaml` — GUID + boyut/metrik kataloğu (3 küp)
- `references/query-templates.md` — Doğrulanmış prompt kalıpları, anti-pattern'ler, ATC2 kod kuralı
- `references/rest-getanswer-guide.md` — REST getAnswer-first akışı, istek gövdeleri, yanıt zarfı, `n_countries` türevleri
- `references/csv-normalization-guide.md` — Notasyon → Türkçe format dönüşümü, preamble skip
- `references/changelog.md` — Sürüm geçmişi
- `scripts/ts_getanswer_extractor.py` — REST top-N CHF çıkarıcı (vendor-neutral)
- `scripts/ts_getanswer_country_extractor.py` — REST ülke kırılımı + `n_countries` çıkarıcı
- `scripts/normalize_csv.py` — Native/preamble CSV normalizer

---

## 12. When Claude Should Invoke This Skill

- "ThoughtSpot'tan/Spotter'dan çek", "MIDAS'tan al", "Roche datadan bak"
- "X molekülü için global satış trendi / ülke kırılımı / `n_countries`"
- "Y ATC sınıfının pazar büyüklüğü", "Z hastalığında manufacturer share"
- "Cross-country pazar karşılaştırması", "fiyat tavanı için MIDAS referans"
- "Eşdeğer grup pazar boyutu", "biyobenzer fırsat niceliksel layer"
- "Gerçek rakamları CSV olarak çıkar", "ham değer çıkarımı"
- ThoughtSpot, IQVIA, MIDAS, Spotter, Sage, dashboard, "Swiss Franc sales" geçtiğinde

When in doubt, **USE this skill**.

---

## 13. Composability Note

SMP v1.0 içinde hem **source** (küplerden veri) hem **transform** (CSV → normalize Markdown) rolü. Tipik pipeline:

```
pharmaintel (Türkiye Ürün Geliştirme)
    → thoughtspot-roche (cross-country MIDAS pull + REST ham değer çıkarımı)
        → carbon-pptx (BU deck) | carbon-html-report (publication-grade rapor)
```

Çıktılar provenance-stamped (`analytical_session_id` + `answer_id` + extract timestamp) olduğundan downstream'de geriye izlenebilir.
