# references/turk-mcp-entegrasyonu.md — Türk Regülatör MCP-First Birleşik Rehberi

**Skill**: pharmapatent v2.0.0
**Bağlam**: Mod 13 (TR_REGULATORY_FLOW) zorunlu okuması. Diğer modlar (Mod 1 FTO, Mod 4 Lifecycle, Mod 5 Regulatory, Mod 6 Litigation, Mod 7 DD, Mod 9 Biosimilar, Mod 10 Licensing, Mod 12 Expert Witness) Türkiye-tarafı veriye dokunduğunda bu dosya çağrılır.

## İlişkili Protokoller

- `SKILL.md §3.5 / §5.5` — MCP-first doktrini
- `SKILL.md §4 Mod 13` — TR_REGULATORY_FLOW akışı
- `references/veritabani-stratejileri.md §1.4 / §2.3` — TİTCK + TÜRKPATENT klasik kaynak bilgisi (web tabanlı, MCP yedeği)
- `references/ictihat-emsal.md §1` — Mevzuat sorgulama
- `references/ruhsat-veri-imtiyazi.md` — TİTCK ruhsat süreci kavramsal çerçeve
- `references/smk-6769-ilac.md` — SMK madde haritası

## İçindekiler

1. Üçlü mimari ve doktrin
2. TİTCK MCP — 56 araç envanteri ve kullanım örüntüleri
3. Türk Patent MCP — 6 araç envanteri ve kullanım örüntüleri
4. Mevzuat MCP — mevzuat.gov.tr + KAYSİS sözleşmesi
5. Mod 13 akış diyagramı ve örüntüler
6. Provenance damgası ve audit trail
7. Bilinen sınırlamalar ve düşülen tuzaklar
8. Örnek end-to-end vaka

---

## 1. Üçlü mimari ve doktrin

### 1.1. MCP üçgeni

| MCP | Sunucu URL | Araç sayısı | Kapsam | Durum |
|---|---|---|---|---|
| **TİTCK MCP** | `titck.cureonics.com` | 66 | TR beşeri tıbbi ürün master dataset + bağlı 19 dinamik modül (active ingredients, foreign ingredients, off-label, Madde 23, batch release, supply tracking, additional monitoring, withdrawal, reference prices, institutional fees, scheduling, regulation art.23) + 4 derived dataset (holders kanonik + SNOMED ingredient map + ICD-10 maps + drug-substance profile) | ✅ Aktif |
| **Türk Patent MCP** | `markapatent-mcp.fastmcp.app` | 6 | TÜRKPATENT — patent + endüstriyel tasarım + ticari marka. Search + get_details her üç varlık için | ✅ Aktif |
| **Mevzuat MCP** | `mevzuat.cureonics.com/mcp` | 29 | mevzuat.gov.tr + KAYSİS kurum belgeleri; arama, künye, madde/sürüm ve sınırlı PDF okuma | §4 kaynak/kimlik/kapsam sözleşmesi |

### 1.2. MCP-First doktrin (5 zorunlu kural)

**K1 — Kanonik kaynak**: Türkiye verisi için **MCP > resmi kurum web sitesi (kazıma) > akademik literatür > sektör basını**. Web kazıma yalnız MCP envanteri yetersiz olduğunda yedek.

**K2 — Provenance damgası**: Her TR veri noktasına `[Kaynak MCP / Tool / Erişim tarihi]` formatında ek; örneğin `[TİTCK MCP / get_price_history / 2026-05-01]`. Damgasız veri rapora girmez.

**K3 — Holder normalizasyonu**: Holder string'i ham geçirilmez. Önce `find_holder_by_alias` veya `search_holders` ile kanonik `holder::id`'ye çözülür; sonra `get_holder_portfolio` ile alias listesi + GLN + VAT + ürün sayısı çıkarılır. "DEVA HOLDİNG A.Ş." ve "Deva Holding" aynı kanonik kayıttır — alias normalizasyonu olmadan portföy analizi hatalıdır.

**K4 — SNOMED CT atomu**: Etkin madde tabanlı analiz (eşdeğerlik, biyobenzer küme, off-label genişleme, foreign drug eşleştirme) **`master::barcode → SNOMED concept`** bağı üzerinden yapılır. INN string match ("trastuzumab" vs "Trastuzumab Emtansin") ayrı SNOMED kavramlarıdır; string benzerliği bağlayıcı değil.

**K5 — FTS5 query mode**: TİTCK arama araçlarının çoğunda `query_mode='smart'` (varsayılan) Boolean operatörlerini otomatik algılar (`"Ozempic" OR "semaglutide"`, `glofitamab NOT mosunetuzumab`). Yalnız özel/karmaşık FTS5 ifadesi geçirmek için `query_mode='raw'` kullanılır. Tek-kelime sorgu için fark yoktur.

### 1.3. MCP-first ne zaman bypass edilir?

| Durum | Çözüm |
|---|---|
| TİTCK MCP timeout / 5xx | İkinci deneme; iki kez başarısızsa `https://www.titck.gov.tr/` web fetch + audit notu |
| Türk Patent MCP'de aranan başvuru numarası bulunamıyor | EPAAT (https://online.turkpatent.gov.tr/EPATT/) web fetch + audit notu |
| Mevzuat kaynağı erişilemiyor | Başarılı diğer kaynak korunur; eksik kol `coverage` / tanı ile kaydedilir. Resmî URL’den doğrulama gerekiyorsa kaynak bazında audit notu; yokluk hükmü verilmez |
| İçtihat metni gerek (Yargıtay/Danıştay/AYM) — Mevzuat MCP kapsamı dışı | UYAP / `karararama.yargitay.gov.tr` / `kararlarbilgibankasi.anayasa.gov.tr` web fetch + audit notu |
| Gerçek-zamanlı haber/duyuru gerek (örn. yeni geri ödeme tebliği yayımlandı) | Web search + zaman damgası; kaynaklar TİTCK Resmî Duyurular + Resmî Gazete |
| Audit trail için dış kaynak doğrulaması | Web fetch + provenance ile ek satır |

---

## 2. TİTCK MCP — 56 araç envanteri ve kullanım örüntüleri

### 2.1. Araçlar — fonksiyonel sınıflandırma

#### A. Temel arama ve detay (master drug records)
- **`search_drugs(query, limit, offset, query_mode)`** — Tam metin sorgu (FTS5). Ürün adı, INN, barkod, holder, ATC. Birinci giriş kapısı.
- **`get_drug(identifier)`** — Tek ürün detayı; barkod (örn. `8699XXXXXXXXX`) veya `master::barcode` id.
- **`get_drug_snomed_profile(barcode)`** — Master record + SNOMED + ATC bağı tek çağrıda.
- **`search_by_atc(atc_code, ...)`** — ATC kodu ile arama (prefix match destekler — "L01" → tüm onkoloji).
- **`search_by_substance(snomed_concept_id, ...)`** — SNOMED CT concept üzerinden ürün listesi.

#### B. Holder (firma) normalizasyonu
- **`search_holders(query, has_in_market, min_products, ...)`** — Holder kanonik araması; spelling varyantları otomatik birleşir.
- **`get_holder(identifier)`** — `holder::id` veya alias text ile detay; alias listesi + GLN + VAT + product_count.
- **`find_holder_by_alias(alias_text)`** — Bir spelling varyantını kanonik holder'a çözer.
- **`list_holder_aliases(holder_id, ...)`** — Bir holder'ın tüm gözlemlenmiş yazımları.
- **`get_holder_portfolio(holder_id)`** — Roll-up: holder + alias varyantları + total + in-market product sayısı + ATC class dağılımı.
- **`compare_holders(holder_id_a, holder_id_b)`** — İki holder'ın TR portföyü side-by-side.

#### C. Eşdeğerlik ve biyobenzer
- **`find_shared_substance_peers(barcode, ...)`** — Aynı SNOMED substance'ı paylaşan diğer ürünler (canonical anti-INN-string-match aracı).
- **`find_equivalent_products_by_substance(barcode, ...)`** — Eşdeğerlik (jenerik) listesi.
- **`find_biosimilar_group(snomed_concept_id, ...)`** — Same-SNOMED-substance peers, **oldest-first sıralı**; en eski authorization referans ürün olarak işaretlenir (8 yıl AB / 6 yıl TR veri imtiyazı çapası).
- **`compare_drug_to_alternatives(barcode)`** — Same-substance + same-ATC peerlere karşı side-by-side.
- **`find_first_in_class(atc_code)`** — Bir ATC sınıfı (prefix-match) içindeki en eski authorization + class summary.
- **`get_atc_class_summary(atc_code)`** — Bir ATC sınıfının agregate snapshot'ı (ürün sayısı, holder sayısı, withdrawal trend).
- **`get_atc_hierarchy(atc_code)`** — WHO-ATC parent/sibling/child dağılımı.

#### D. Etkin madde (substance) — kayıt ve haritalama
- **`search_active_ingredients(query, ...)`** — TİTCK "Etkin Madde Listesi" (REGISTRATION PIPELINE — open dossier signal).
- **`find_active_ingredients_for_drug(barcode)`** — Bir ürünün ingredient'ı open pipeline'da mı?
- **`get_ingredient_snomed_map(ingredient_name)`** — TİTCK ingredient adından kanonik SNOMED concept(ler)i.
- **`list_unmapped_ingredients(...)`** — SNOMED bağı çözülmemiş canonical ingredient'lar (audit / data-quality rapor için).
- **`summarize_substance(snomed_concept_id)`** — SNOMED FSN + preferred name + ürün listesi + ATC + ICD-10 indikasyonlar tek çağrıda.
- **`get_icd10_maps_for_substance(snomed_concept_id)`** — SNOMED CT International ICD-10 map satırları.

#### E. Foreign / import
- **`search_foreign_active_ingredients(query, ...)`** — Yurt Dışı Etkin Madde Listesi (TİTCK named-patient programı).
- **`find_foreign_active_ingredients_for_drug(barcode)`** — Bir TR ürün ile foreign listedeki kayıtların bağı.
- **`find_foreign_drugs_for_icd10(icd10_code)`** — ICD-10 kodu ile foreign ingredient reverse lookup.

#### F. Fiyat
- **`get_price_history(barcode)`** — Tam fiyat zinciri: FSF / depocu / pharmacy / retail + İŞLEM GEÇMİŞİ tarih + nedenleri.
- **`find_reference_prices_for_drug(barcode)`** — Referans Bazlı İlaç Fiyat Listesi bağı.
- **`search_reference_prices(query, ...)`** — Referans-fiyat tam metni.
- **`search_institutional_fees(query, ...)`** — Kurum Hizmetleri Fiyat Tarifesi.

#### G. Pipeline ve istisnalar
- **`find_regulation_article23_for_drug(barcode)`** — Madde 23 muafiyet başvuruları.
- **`search_regulation_article23(query, publication_date_from, publication_date_to, sheet_name, ...)`** — Madde 23 multi-year history.
- **`find_off_label_uses_for_drug(barcode)`** — Endikasyon Dışı Kullanım Listesi (oncology + organ category) bağı.
- **`search_off_label_uses(query, sheet_name, ...)`** — Off-label tam metin (organ category sheet filter).
- **`find_supply_tracked_ingredients_for_drug(barcode)`** — Supply-tracked ingredient bağı.
- **`search_supply_tracked_ingredients(query, ...)`** — Supply tracking tam liste.
- **`find_additional_monitoring_for_drug(barcode)`** — Additional monitoring (siyah üçgen) bağı.
- **`search_additional_monitoring(query, ...)`** — Additional monitoring tam liste.

#### H. Çıkış / iptal / batch release
- **`find_authorization_cancellations_for_drug(barcode)`** — İptal kayıtları.
- **`search_authorization_cancellations(query, ...)`** — İptal listesi tam metin.
- **`get_withdrawal_trend(year_from, year_to, ...)`** — Yıl-yıl iptal eğilimi aggregate.
- **`find_batch_release_certificates_for_drug(barcode)`** — Seri Serbest Bırakma Sertifikası bağı (biyolojikler için kritik).
- **`search_batch_release_certificates(query, ...)`** — Batch release tam metin.

#### I. Belge tarama
- **`list_document_datasets(...)`** — İndekslenmiş PDF/DOCX dataset listesi (doctor information, label changes).
- **`search_documents(query, dataset_id, ...)`** — Indekslenmiş belge full-text search.
- **`get_document(document_id)`** — Belge tam metin.
- **`find_documents_for_drug(barcode)`** — Bir ürünle ilişkili belgeler.
- **`find_documents_by_substance(snomed_concept_id)`** — SNOMED bazlı belge tarama.

#### J. Scheduling
- **`find_scheduling_records_for_drug(barcode)`** — Aylık takvimlendirme listesi bağı.
- **`search_scheduling_records(query, ...)`** — Takvimlendirme tam metin.

#### K. New entries / yeni-kayıt takibi
- **`find_new_authorizations_since(date_iso)`** — Belirli tarihten itibaren ruhsatlanan ürünler.

#### L. Meta
- **`list_datasets(...)`** — 20 dinamik modül + auth metadata + son güncelleme.
- **`get_dataset_overlap(dataset_a, dataset_b)`** — İki dataset arasında Jaccard / coverage.
- **`server_info()`** — Sunucu version + config.

### 2.2. Standart kullanım örüntüleri

#### Örüntü 1 — Tek ürünün tam dosyası (Mod 13 ana akış)

```
1. search_drugs(query="MABTHERA")         # Discovery
2. get_drug_snomed_profile(barcode)        # Master + SNOMED + ATC
3. get_holder_portfolio(holder_id)         # Sahip portföyü
4. find_shared_substance_peers(barcode)    # Eşdeğer/biyobenzer adayları
5. find_biosimilar_group(snomed_concept)   # Biyobenzer kümesi (oldest-first)
6. get_atc_class_summary(atc_code)         # Sınıf rekabeti
7. find_first_in_class(atc_code)           # First-in-class çapası
8. get_price_history(barcode)              # Fiyat zinciri
9. find_reference_prices_for_drug(barcode) # Referans fiyat
10. find_regulation_article23_for_drug(barcode)
11. find_off_label_uses_for_drug(barcode)
12. find_authorization_cancellations_for_drug(barcode)
13. find_batch_release_certificates_for_drug(barcode)  # biyolojiklerse
```

#### Örüntü 2 — Biyobenzer fizibilitesi (Mod 9)

```
1. search_drugs(query="<innovator brand>") → barcode
2. get_drug_snomed_profile(barcode) → SNOMED concept_id
3. find_biosimilar_group(concept_id) → en eski authorization tarihi (referans çapası)
4. summarize_substance(concept_id) → ATC + ICD-10 + tüm ürünler
5. find_first_in_class(ATC) → veri imtiyazı + 6 yıl çapası
6. get_atc_class_summary(ATC) → mevcut biyobenzer sayısı
7. (paralel) Türk Patent MCP search_patents(applicant=<innovator firma TR>)
   → cihaz patenti + formülasyon patenti TR durumu
```

#### Örüntü 3 — Holder portföy karşılaştırması (Mod 4 Lifecycle)

```
1. find_holder_by_alias("<spelling A>") → holder_id_A
2. find_holder_by_alias("<spelling B>") → holder_id_B
3. compare_holders(holder_id_A, holder_id_B)
4. (her iki holder için) get_holder_portfolio → ATC class dağılımı
5. (her iki holder için) get_withdrawal_trend → portföy sağlığı
```

#### Örüntü 4 — Off-label haritası (onkoloji)

```
1. search_off_label_uses(query="meme kanseri", sheet_name="Meme")
   → her satır: ilaç + diagnosis + organ
2. her ilaç için search_drugs → barcode
3. get_price_history(barcode) → erişim baskısı
4. find_off_label_uses_for_drug(barcode) → diğer organ kategorileri
5. (Mod 5 entegrasyonu) Mevzuat MCP / SUT eki sorgusu (aktif v2.0.1)
```

#### Örüntü 5 — Madde 23 muafiyet trendi (Mod 5)

```
1. search_regulation_article23(query="<INN>", 
     publication_date_from="2024-01-01")
2. her başvuru için ilgili barkod → search_drugs
3. find_regulation_article23_for_drug(barcode) → tüm Madde 23 başvuruları
4. yıl-bazlı agregasyon (skill içi)
```

#### Örüntü 6 — Pediatric / yetim ilaç audit (Mod 12 Expert Witness destek)

```
1. find_new_authorizations_since("2024-01-01")
2. (filter) is_orphan = true (varsa) veya etkin madde foreign listede mi?
3. find_foreign_active_ingredients_for_drug(barcode)
4. find_additional_monitoring_for_drug(barcode) → siyah üçgen
5. summarize_substance → klinik bağlam
```

### 2.3. Performans ve sayfalama

- Listeleme araçları varsayılan `limit=20`, max `100`. Pagination için `next_offset` field'ı response'tan alınır ve sonraki çağrıya `offset` olarak geçirilir.
- FTS5 smart-mode tek-kelime + multi-kelime + Boolean'ı otomatik ayırt eder; özel sözdizimi gerekmedikçe `raw` kullanmaktan kaçının.
- `get_holder_portfolio` ve `get_atc_class_summary` ağır roll-up'lar — paralel ürün analizinde tekrar çağırmak yerine sonucu skill içinde önbelleğe alın.

---

## 3. Türk Patent MCP — 6 araç envanteri ve kullanım örüntüleri

### 3.1. Araçlar

#### Patent
- **`search_patents(title, applicant, abstract, ipc_class, cpc_class, owner, attorney, application_number, limit, offset)`** — TR ulusal başvurular + EP validations. Aynı anda birden fazla parametre kombine edilebilir.
- **`get_patent_details(application_number)`** — Tam detay: başvuru/yayın/tescil tarihleri, mucitler, applicant, attorney, IPC/CPC tam, durum, yıllık harç durumu.

#### Endüstriyel tasarım
- **`search_designs(design_name, applicant, designer, attorney, locarno_class, registration_no, limit, offset)`** — Locarno sınıflandırması ile.
- **`get_design_details(registration_no)`** — Tam detay.

#### Ticari marka
- **`search_trademarks(trademark_name, holder_name, nice_classes, name_operator, holder_name_operator, limit, offset)`** — Nice 5 (farmasötik), Nice 10 (medikal cihaz), Nice 35 (hizmet), Nice 44 (sağlık hizmetleri) farmasötik için kritik sınıflar.
- **`get_trademark_details(application_number)`** — Tam detay.

### 3.2. Standart kullanım örüntüleri

#### Örüntü 1 — Innovator firma TR portföyü (Mod 4 Lifecycle)

```
1. search_patents(applicant="Roche", limit=100, offset=0)
   → portföy sayfaları
2. get_patent_details(<her başvuru numarası>)
   → IPC/CPC, durum, yıllık harç
3. (paralel) search_trademarks(holder_name="Roche", nice_classes="5,10")
   → marka envanteri
4. (paralel) search_designs(applicant="Roche", locarno_class="28-03")
   → cihaz endüstriyel tasarım
```

#### Örüntü 2 — FTO başvuru sahibi araması (Mod 1 FTO TR-tarafı)

```
1. search_patents(cpc_class="A61K9/00", abstract="<INN>")
   → formülasyon patentleri
2. search_patents(cpc_class="A61M5/", applicant="<device firma>")
   → cihaz patentleri
3. search_patents(ipc_class="C07K16/", applicant="<biyolojik firma>")
   → mAb patentleri
4. her eşleşme için get_patent_details → istem analizi için ham metin
   (NOT: TR Patent MCP istem metnini doğrudan vermez; başvuru numarası ile 
    EPAAT web fetch yedeği gerekebilir)
```

#### Örüntü 3 — Marka çatışması (Mod 4 Lifecycle, jenerik benzeri marka)

```
1. search_trademarks(trademark_name="<innovator marka>", nice_classes="5",
     name_operator="contains")
2. search_trademarks(holder_name="<şüpheli jenerik firma>", nice_classes="5")
3. her benzer marka için get_trademark_details
   → başvuru tarihi, durum, kullanım bölgesi
```

#### Örüntü 4 — TR ulusal vs EP validation ayrımı

`search_patents` sonuçlarında başvuru numarası prefix'i:
- `TR YYYY/NNNNNN` → TR ulusal başvuru
- `EP NNNNNNNNN` ile başlayanlar TR'de validate edilmiş EP — ayrı bir sayfa

Mevcut MCP araçları bu ayrımı doğrudan filter parametresi olarak vermiyor; sonuçlar üzerinde post-filter gerekli.

### 3.3. Bilinen sınırlamalar

| Sınırlama | İmpakt | Yedek |
|---|---|---|
| İstem tam metni `get_patent_details` ile gelmiyor (sadece bibliografik) | Detaylı istem analizi (Mod 1 FTO matrisleri, Mod 2 Invalidity feature-by-feature) için yetersiz | EPAAT web fetch (https://online.turkpatent.gov.tr/EPATT/) + audit notu |
| Yıllık harç ödeme tam tarihçesi sınırlı | Lifecycle (Mod 4) detaylı maintenance audit için yetersiz | EPAAT detay sayfası + scripts/patent-expiry-monitor.py |
| FER (First Examination Report) içeriği yok | Invalidity argümanı için kullanışlı önceki itirazlar görülmez | EPAAT FER PDF download |
| Citation network (forward/backward) yok | Mod 3 Landscape için Espacenet zorunlu | Espacenet INPADOC |

---

## 4. Mevzuat MCP — iki resmî kaynak ve doğrulanmış araç adları

### 4.1. Kaynak ve kimlik sözleşmesi

Sunucu `https://mevzuat.cureonics.com/mcp` üzerinde mevzuat.gov.tr ile KAYSİS'i birlikte
sunar. Buradaki araç adları 1 Ekim 2026 CureoHub kaynak sözleşmesini izler; istemcinin
`tools/list` şemasıyla doğrula. Eski Cloud Run revision'ı ve tahminî İngilizce fonksiyon
adları geçerli çağrı sözleşmesi değildir. Plugin'in
[CONNECTORS.md §1.A.1](../../../CONNECTORS.md) metni normatiftir.

- mevzuat.gov.tr: `{tertip}_{tur}_{no}`; detay/metin araçlarına sonuçtaki
  `mevzuat_no`, `mevzuat_tur`, `mevzuat_tertip` alanları geçirilir.
- KAYSİS: `kaysis:<belge_id>`; `belge_id` kanun numarası değildir. Tür ve kurum kodlarını
  kendi keşif araçlarından al; diğer kaynağın kodunu dönüştürme.
- Aynı başlık veya numara, kayıtların aynı hukukî belge olduğunu kanıtlamaz; iki kaynak
  otomatik tekilleştirilmez. Künye tarihi, yürürlük durumu ve sürüm resmî belgeyle doğrulanır.

### 4.2. Kullanılan araçlar

| Amaç | Gerçek araç adı / giriş |
|---|---|
| Birleşik keşif | `search_all_mevzuat(query, page=1, limit_per_source=10)` |
| KAYSİS tür / kurum keşfi | `list_kaysis_types()`; `search_kaysis_institutions(query)` |
| KAYSİS filtreli arama | `search_kaysis(query, kurum_id?, turler?, mevzuat_no?, yururluk, page)` |
| KAYSİS künye / PDF | `get_kaysis_detail(belge_id)`; `get_kaysis_text(belge_id, start_page, end_page, max_chars)` |
| mevzuat.gov.tr arama | `search_mevzuat(query, ...)`; `search_mulga_mevzuat(query, ...)`; `search_mevzuat_fihristi(fihrist_turu, ...)` |
| mevzuat.gov.tr detay / madde / PDF | `get_mevzuat_detail(...)`; `get_mevzuat_content(..., madde_no, max_chars)`; `get_mevzuat_text(...)` |
| Tarih / sürüm | `get_onceki_metinler(...)`; `get_mevzuat_timeline(...)`; `get_mevzuat_madde_diff(...)` |
| Tür / kurum / dosya | `list_mevzuat_types()`; `list_kurumlar()`; `list_mevzuat_by_type(tur, ...)`; `download_mevzuat_document(...)` |
| mevzuat.gov.tr kanıt paketi | `build_mevzuat_semantic_context(query, ...)` — KAYSİS'i taramaz; tamlık iddiası taşımaz |
| Anayasa / madde ağacı | `get_anayasa(...)`; `get_mevzuat_madde_tree(...)` — KAYSİS kaydına uygulanmaz |
| ChatGPT yüzeyi | `Mevzuat:search(query, limit)` → `Mevzuat:fetch(id=<dönen id>)`; `search` adını connector önekiyle kullan |

`shared/tool-manifest.json` içindeki regulatory/patent blokları yeni altı aracı ve
kaynak okuma araçlarını başlangıçta yükler. Tarih/sürüm gibi ilave araç gerektiren işte
ilgili gerçek şemaları da iş başlamadan yükle; fonksiyon adı veya parametre uydurma.

### 4.3. Standart kullanım örüntüleri

**M1 — Bilinen kanun maddesi:** `search_mevzuat(query="6769")` sonucundaki no/tür/tertip
ile `get_mevzuat_detail` → `get_mevzuat_content(..., madde_no="85", max_chars=20000)`.
Dönen maddenin içinden gerekli fıkrayı oku; arama başlığından hüküm üretme.

**M2 — Tarihsel karşılaştırma:** `search_mulga_mevzuat(query="551")` ile kaydı keşfet;
tarihî kimliği koru. `get_onceki_metinler` / `get_mevzuat_timeline` ile belgelenmiş
sürümleri belirle; `get_mevzuat_content(..., as_of_date=<tarih>)` veya
`get_mevzuat_madde_diff` kullan. Tarihî snapshot eksikse güncel metni tarihî diye sunma.

**M3 — Kurum yönergesi / genelgesi / rehberi:**

```text
1. search_all_mevzuat(query="ruhsatlandırma", limit_per_source=10)
2. list_kaysis_types()
3. search_kaysis_institutions(query="sağlık")
4. search_kaysis(query="ruhsatlandırma", kurum_id=<dönen id>, turler=<dönen tür kodları>)
5. get_kaysis_detail(belge_id=<seçilen sonuç>)
6. get_kaysis_text(belge_id=<aynı belge>, start_page=1, end_page=3, max_chars=20000)
```

**M4 — Anayasa:** `get_anayasa` sayfa/karakter sınırlarıyla PDF okur; `article_no` veya
`topic` parametresi yoktur. Belirli madde için `search_mevzuat(query="2709")` sonucundaki
kimlikle `get_mevzuat_content(..., madde_no="17")` kullan.

**M5 — Geniş araştırma:** önce `search_all_mevzuat` ile iki kaynağı keşfet. Mevzuat.gov.tr
kolunda `build_mevzuat_semantic_context` kullanılabilir; KAYSİS kolunda M3 uygulanır.
Kaynakların kanıtları ayrı tutulur, hiçbiri tek çağrıyla bütün mevzuatı kapsamaz.

### 4.4. Kapsam, eksik belge ve sınırlı okuma

`coverage` kayıtlarında `status`, `total`, `has_more`, `retrieved`, `returned`,
`page_truncated` ve `diagnostics` korunur. Bir kaynak başarısızsa diğerinin sonuçları
kullanılır, eksik kol raporlanır. `degraded` / `manual_required` / `error` veya bilinmeyen
toplam "mevzuat yok" anlamına gelmez. Sağlıklı boş yanıt yalnız sorgulanan kapsamı anlatır.

KAYSİS kaynak sayfası 50 kayıttır. `page_truncated=true` ise aynı `page` ile
`search_kaysis` kullanarak sayfanın kalan adaylarını al; `has_more` sonraki sayfayı
belirtir. Ortak arama 1–500 karakterdir; KAYSİS metni 3–160 karakter ve sayfa en fazla
10000 olabilir. Aşımda yalnız bu kol gerekçeli `manual_required` olur. Sayısal ortak
sorgu KAYSİS'te mevzuat numarası filtresine gider.

PDF için `max_chars` 500–100000; önce dar sayfa aralığı seç. `selected_pages` ile
`total_pages` birlikte okunur: `truncated=false` yalnız istenen aralığın sınır nedeniyle
kesilmediğini söyler; okunabilirlik ve tüm belge kapsamı ayrıca doğrulanır. `missing_text_pages` / `ocr_required` varsa okunmayan sayfalardan hüküm üretme;
otomatik OCR yapılmış sayma. Kaynak URL'si, erişim zamanı, PDF `sha256` değeri, hata
zarfı ve okunan kapsam kanıt dosyasında saklanır. Erişim tarihi yürürlük tarihi değildir.

### 4.5. Sağlık ve şema doğrulaması

`initialize` başarısı araçların veya iki resmî kaynağın çalıştığını tek başına kanıtlamaz.
Başlangıçtaki `tools/list` yeni altı aracı içermiyorsa eski istemci yüzeyini raporla;
eksik araç çağrısını tahminî alias ile maskeleme. 401 erişim/yapılandırma sorunudur;
başarılı HTTP yanıtında da `isError`, kaynak `status` ve `diagnostics` incelenir.

### 4.6. Tarihsel content negotiation kaydı

Bu tarihsel doğrulama güncel endpoint, araç sayısı veya deploy talimatı değildir;
güncel sözleşme §4.1–4.5'tedir. Eski olay kaydı aşağıda korunmuştur.

Bu blok skill'in v2.0.0 → v2.0.1 patch öyküsünü kayıt altına alır; benzer FastMCP/Claude.ai entegrasyon vakalarında referans olarak kullanılabilir.

**Semptom**: v2.0.0 sürümünde Mevzuat MCP'nin `tools/list` çağrısı boş görünüyor, ancak server kodu 12 `@mcp.tool` decorator'lı fonksiyonun tamamı doğru kayıtlı, return annotation + docstring tam.

**Hatalı varsayım hipotezleri (tümü reddedildi)**:
- ❌ FastMCP decorator eksikliği — kontrol: 12 fonksiyon kayıtlı.
- ❌ Pydantic schema bozukluğu — kontrol: tüm modeller geçerli.
- ❌ stdio transport ile yanlış deploy — kontrol: HTTP entrypoint `http_app.py` doğru, Dockerfile entrypoint doğru.
- ❌ Tool registry sorunu — kontrol: lokal MCP Inspector ile araçlar görünüyor.

**Gerçek kök neden**: **Content negotiation uyumsuzluğu**. FastMCP varsayılan ayarında HTTP yanıt için `text/event-stream` Accept header'ı bekliyor (SSE streaming için). Claude.ai gibi `Accept: application/json` (JSON-only) gönderen istemcilere sunucu **406 Not Acceptable** dönüyor; istemci tarafı bunu sessizce yorumlayıp tools/list boş gibi gösteriyor.

**Düzeltme**: FastMCP sunucusunda **JSON response modu** açıldı (`server.py:107`).

**Doğrulama**:
- Regresyon testleri eklendi: taze app helper (`test_http_app.py:48`) + JSON-only initialize/tools/list testi (`test_http_app.py:173`)
- Lokal: 22 test passed
- Deploy: Cloud Run yeni revision `mevzuat-mcp-00017-668`
- Public smoke: OAuth discovery 200 · yetkisiz mcp 401 (beklenen) · JSON-only initialize 200 application/json + protocolVersion 2024-11-05 · tools/list 200 application/json + tools_count=12 + tools_empty=false

**Side-quest bulgu**: `gcloud` context başlangıçta yanlış projedeydi; doğru deploy projesi `gcp-deploy.mjs:16` içindeki `cureonics-ai-hub`. Çoklu-proje GCP organizasyonlarında bu klasik bir tuzak.

**Genel ders (skill ekosistemine entegrasyon kuralı)**: Yeni bir MCP'yi `claude.ai`'ye bağlarken FastMCP-bazlı sunucularda **JSON response modu açık olmalı**; aksi halde streaming-yetenekli istemciler haricinde tool listesi sessizce boş görünür. SMP skill manifest'lerinde MCP konnektörlerinin sağlık kontrolü `tools_count > 0` doğrulamasını içermeli.

---

## 5. Mod 13 akış diyagramı ve örüntüler

### 5.1. Üst-düzey akış

```
┌─────────────────────────────────────────────────────────┐
│ Kullanıcı girdisi (1+):                                 │
│   barkod | INN | ATC | ICD-10 | holder | patent | marka │
└────────────────────────┬────────────────────────────────┘
                         ↓
        ┌────────────────┴──────────────┐
        ↓                               ↓
┌───────────────┐              ┌────────────────┐
│ TİTCK MCP     │              │ Türk Patent    │
│ (1) Discovery │              │ MCP            │
│ (2) Identity  │              │ (search +      │
│ (3) Eşdeğer   │              │  get_details)  │
│ (4) ATC       │              └────────┬───────┘
│ (5) Fiyat     │                       │
│ (6) Pipeline  │                       │
│ (7) Çıkış     │                       │
│ (8) Belge     │                       │
└───────┬───────┘                       │
        │                               │
        └────────────┬──────────────────┘
                     ↓
        ┌────────────────────────┐
        │ Mevzuat MCP (2 kaynak) │
        │ — kanun + yönetmelik   │
        │ + KAYSİS kurum belgesi │
        └────────────┬───────────┘
                     ↓
        ┌────────────────────────────────┐
        │ Çapraz-doğrulama + provenance  │
        │ Çıktı: TR Regülatör + IP Dosya │
        └────────────────────────────────┘
```

### 5.2. Mod 13 + diğer modlar bileşim örüntüleri

#### Bileşim A — "Jenerik X TR'de ne zaman piyasaya girebilir?" (Mod 13 → Mod 5 → Mod 1 → Mod 9)

```
Mod 13 (TR ürün dosyası):
  TİTCK: search_drugs → barcode → get_drug_snomed_profile
  TİTCK: find_biosimilar_group → en eski authorization (referans çapası)
  TİTCK: get_price_history → mevcut fiyat tavanı
  Türk Patent: search_patents(applicant=<innovator>) → cihaz + formülasyon patentleri
  
Mod 5 (Pazara giriş takvimi):
  scripts/loe-calculator.py → MAX(patent expiry, veri imtiyazı bitişi)
  scripts/regulatory-timeline.py → 8-yıl biosimilar yolu
  
Mod 1 (FTO):
  Türk Patent get_patent_details → cihaz patenti istem analizi
  references/markush-protokol.md → API formül kapsam testi
  
Mod 9 (Biosimilar Pathway):
  references/biyobenzer-yol.md → CQA çerçeve
  scripts/biosimilar-comparator.py
```

#### Bileşim B — "Holder X'in TR portföyünü değerle" (Mod 13 → Mod 4 → Mod 7)

```
Mod 13:
  TİTCK find_holder_by_alias → kanonik holder_id
  TİTCK get_holder_portfolio → ATC dağılımı + product_count
  TİTCK get_withdrawal_trend → portföy sağlığı
  Türk Patent search_patents(applicant=...) → IP envanteri
  
Mod 4 (Lifecycle):
  her ürün için patent expiry haritası
  scripts/patent-expiry-monitor.py
  
Mod 7 (DD):
  references/patent-degerleme.md → income approach
  scripts/royalty-calculator.py → portföy NPV
```

#### Bileşim C — "Bu ilaç off-label kullanılabilir mi?" (Mod 13 → Mod 5 → onko-erisim downstream)

```
Mod 13:
  TİTCK search_drugs → barcode
  TİTCK find_off_label_uses_for_drug → mevcut SUT off-label izinleri
  TİTCK find_regulation_article23_for_drug → Madde 23 başvuru tarihçesi
  Mevzuat MCP → SUT eki güncel hali + ilgili Sağlık Bakanlığı genelgesi
  
Mod 5:
  Bolar değerlendirmesi (uygulanmaz; off-label klinik kullanım)
  
onko-erisim (downstream skill):
  Yargıtay 3'lü kümülatif kriter + AYM BB 73 + dilekçe inşası
```

---

## 6. Provenance damgası ve audit trail

### 6.1. Damga formatı

Her TR veri noktası için:

```
[Kaynak / Tool / Erişim tarihi / Ek parametreler]
```

Örnekler:

- `[TİTCK MCP / get_drug / 2026-05-01]`
- `[TİTCK MCP / search_off_label_uses / sheet=Meme / 2026-05-01]`
- `[TİTCK MCP / get_price_history / 8699XXXXXXXXX / 2026-05-01]`
- `[Türk Patent MCP / search_patents / applicant=Roche, cpc=A61K9 / 2026-05-01]`
- `[Türk Patent MCP / get_patent_details / TR2018/12345 / 2026-05-01]`
- `[Mevzuat MCP / search_mevzuat / SMK 6769 / 2026-05-01]`
- `[Mevzuat MCP / get_mevzuat_content / SMK 6769 m.85 / 2026-05-01]`
- `[Mevzuat MCP timeout fallback / mevzuat.gov.tr web fetch / 2026-05-01]`
- `[TİTCK MCP timeout fallback / titck.gov.tr web fetch / 2026-05-01]`

### 6.2. Audit trail formatı (rapor sonu)

Her rapor `## Audit Trail` bölümü ile biter. Format:

```markdown
## Audit Trail

| # | Veri Noktası | Kaynak | Tool / URL | Erişim |
|---|---|---|---|---|
| 1 | MABTHERA 500mg/50ml fiyat geçmişi | TİTCK MCP | get_price_history(8699XXX) | 2026-05-01 |
| 2 | Roche TR holder canonical id | TİTCK MCP | find_holder_by_alias("Roche") | 2026-05-01 |
| 3 | rituximab biyobenzer kümesi | TİTCK MCP | find_biosimilar_group(SCT-...) | 2026-05-01 |
| 4 | TR2018/12345 cihaz patenti | Türk Patent MCP | get_patent_details | 2026-05-01 |
| 5 | SMK m. 85/3 Bolar metni | Mevzuat MCP | get_mevzuat_content(mevzuat_no="6769", mevzuat_tur=1, mevzuat_tertip=<arama sonucu>, madde_no="85") | 2026-05-01 |

**MCP üçgeni notu:** Mevzuat MCP iki kaynağı ayrı kimlik/kapsamla işler (§4). Erişilemeyen kaynak veya dosya için açık boşluk kaydı gerekir; içtihat bu connector kapsamı dışındadır.
```

---

## 7. Bilinen sınırlamalar ve düşülen tuzaklar

### 7.1. TİTCK MCP

- **Tuzak T-1 — INN string match**: "Trastuzumab" ve "Trastuzumab emtansin" ayrı SNOMED kavramlarıdır. INN substring araması (örn. `search_drugs(query="trastuzumab")`) iki ürünü birden döner — eşdeğerlik analizi için **mutlaka SNOMED concept_id** üzerinden ilerleyin.

- **Tuzak T-2 — Holder ham string**: "F. HOFFMANN-LA ROCHE LTD" ve "ROCHE MÜSTAHZARLARI" aynı kanonik Roche'a çözülür ama farklı string'lerdir. **Önce `find_holder_by_alias`**.

- **Tuzak T-3 — Yurt dışı etkin madde ≠ TR ruhsatlı**: `search_foreign_active_ingredients` sonuçları TR'de **ruhsatsız** named-patient programı ürünlerdir; `search_drugs` (TR ruhsatlı master) ile karıştırılmamalı. Foreign liste genelde rare disease + onkoloji.

- **Tuzak T-4 — Active ingredient PIPELINE ≠ approved**: `search_active_ingredients` (Etkin Madde Listesi) **registration pipeline** sinyalidir — ingredient'ın açık dossier'i var demektir, ürün ruhsatlı **değildir**. Approval için `search_drugs` kullanın.

- **Tuzak T-5 — Madde 23 ≠ ruhsat**: Madde 23 muafiyet başvurusu olan ürün ruhsatlı **olmayabilir**; yalnız muafiyet başvurusu yapılmıştır. Çapraz `search_drugs` ile teyit edin.

- **Tuzak T-6 — Withdrawn ≠ never authorized**: `search_authorization_cancellations` sonuçları **eskiden ruhsatlıydı, şimdi iptal**. Hiç ruhsatlanmamış ürün için bu listede yok. Cross-check `search_drugs` (mevcut) + `search_authorization_cancellations` (iptal).

- **Tuzak T-7 — Fiyat zinciri yorumu**: `get_price_history` 4-katmanlı fiyat zinciri verir (FSF / depocu / pharmacy / retail). LOE sonrası erozyon analizi için **FSF (Fabrika Satış Fiyatı)** baz alınır; retail tüketici fiyatıdır ve KDV + dağıtım marjı içerir.

- **Tuzak T-8 — sheet_name parametresi**: Bazı arama araçları (örn. `search_off_label_uses`, `search_regulation_article23`) `sheet_name` parametresi alır — bu, kaynaktaki Excel sayfa filtresidir. Off-label için organ kategorisi (`Akciğer`, `Meme`, `Kolorektal`), Madde 23 için yıl (`2024`).

### 7.2. Türk Patent MCP

- **Tuzak T-9 — İstem metni yok**: `get_patent_details` bibliografik veri verir; istem tam metni için EPAAT web fetch zorunlu. Mod 1/2/12 için bu kritiktir.

- **Tuzak T-10 — TR ulusal vs EP validation karışımı**: `search_patents` her ikisini birlikte döner; başvuru numarası prefix'i (TR YYYY/... vs EP...) ile post-filter gerekli.

- **Tuzak T-11 — Yıllık harç durumu sınırlı**: Patent geçerliliği için yıllık harç ödenmiş mi? MCP detaylı tarihçeyi vermez — `scripts/patent-expiry-monitor.py` ve EPAAT web detayı paralel kullanılır.

### 7.3. Mevzuat MCP

- **Tuzak T-12 — Sağlık ≠ kaynak kapsamı:** `initialize` / `tools/list` başarılı olsa da içerik çağrısının `isError`, `coverage`, `status`, `diagnostics` alanları denetlenir. Tek kaynak hatası, boş sonuç veya tarama tamamlandı diye yorumlanmaz (§4.4–4.5).

- **Tuzak T-12b — İçtihat ≠ Mevzuat MCP**: Yargıtay/Danıştay/AYM kararları **Mevzuat MCP kapsamı dışı**. Bu katman için `references/ictihat-emsal.md §1`'deki UYAP karar arama protokolü uygulanır (web fetch + tarih damgası). MCP envanteri sadece kanun/yönetmelik/tebliğ/genelge/Resmi Gazete üzerinedir.

### 7.4. Genel

- **Tuzak T-13 — MCP timeout**: Cloud Run cold start 5-10 saniye olabilir. İlk çağrıda timeout almak normal; ikinci deneme öneriyoruz. İki kez başarısızsa web fetch yedeği + audit notu.

- **Tuzak T-14 — provenance unutma**: Damga olmadan rapora veri girmez. Skill içinde her tool çağrı sonucunu damgalamayı disipline edin.

---

## 8. Örnek end-to-end vaka

**Senaryo**: Mahir, Roche Türkiye Malign Hematoloji BU Lead olarak, **glofitamab (COLUMVI®)** için TR pazara giriş + IP durumunun Mod 13 ile çıkarılmasını talep ediyor.

### 8.1. Adımlar

```
[Adım 1 — Discovery]
TİTCK MCP / search_drugs(query="glofitamab")
→ 2 sonuç: COLUMVI 2.5mg/0.5ml (master::8699XXXXXXXXX),
            COLUMVI 10mg/2ml (master::8699YYYYYYYYY)

[Adım 2 — Identity]
TİTCK MCP / get_drug_snomed_profile("master::8699XXXXXXXXX")
→ {
    barcode: "8699XXXXXXXXX",
    title: "COLUMVI 2.5mg/0.5ml IV ENJEKSİYONLUK ÇÖZELTİ İÇİN KONSANTRE",
    holder: "ROCHE MÜSTAHZARLARI SANAYİ A.Ş.",
    holder_id: "holder::abc123",
    snomed_concept: "SCT-glofitamab",
    atc: "L01FX36",
    authorization_date: "2024-XX-XX",
    in_market: true
  }

[Adım 3 — Holder normalizasyonu]
TİTCK MCP / find_holder_by_alias("ROCHE MÜSTAHZARLARI")
→ holder_id: "holder::abc123"
TİTCK MCP / list_holder_aliases("holder::abc123")
→ ["ROCHE MÜSTAHZARLARI SANAYİ A.Ş.", "ROCHE MÜSTAHZARLARI", 
    "F. HOFFMANN-LA ROCHE LTD", "ROCHE A.Ş."]

[Adım 4 — Eşdeğerlik kontrol]
TİTCK MCP / find_shared_substance_peers("8699XXXXXXXXX")
→ [] (boş — first-in-class glofitamab, henüz biyobenzer yok)
TİTCK MCP / find_biosimilar_group("SCT-glofitamab")
→ sadece COLUMVI 2 doz formu — referans çapası 2024 (8 yıl AB veri imtiyazı 
  → 2032 EU; 6 yıl TR → 2030 TR)

[Adım 5 — ATC peyzajı]
TİTCK MCP / get_atc_class_summary("L01FX")
→ {product_count: 47, holder_count: 23, withdrawal_5y_trend: "stable"}
TİTCK MCP / find_first_in_class("L01FX")
→ blinatumomab (BLINCYTO, Amgen) 2017 — ilk T-cell engager
   glofitamab → first-in-class CD20×CD3 IgG-like 2024

[Adım 6 — Fiyat]
TİTCK MCP / get_price_history("8699XXXXXXXXX")
→ FSF: ₺XX,XXX, Depocu: ₺XX,XXX, Eczacı: ₺XX,XXX, Retail: ₺XX,XXX
   İŞLEM: 2024-Q4 ilk satış fiyatı
TİTCK MCP / find_reference_prices_for_drug("8699XXXXXXXXX")
→ Referans Bazlı Liste'de mevcut, EUR-bazlı tavan

[Adım 7 — Pipeline]
TİTCK MCP / find_regulation_article23_for_drug → boş (yeni ürün)
TİTCK MCP / find_off_label_uses_for_drug → boş (henüz off-label izin yok)
TİTCK MCP / find_supply_tracked_ingredients_for_drug → boş
TİTCK MCP / find_additional_monitoring_for_drug
→ ✅ Siyah üçgen — additional monitoring 5 yıl boyunca

[Adım 8 — Çıkış]
TİTCK MCP / find_authorization_cancellations_for_drug → boş
TİTCK MCP / find_batch_release_certificates_for_drug
→ Her serisi için TR batch release sertifikası gerekli (biyolojik)

[Adım 9 — Patent katmanı]
Türk Patent MCP / search_patents(applicant="ROCHE", abstract="bispecific CD20 CD3")
→ 4 sonuç: TR2019/XXXXX (anti-CD20×CD3 formülasyon), 
            TR2020/YYYYY (cihaz prefilled syringe — N/A glofitamab IV),
            EP-validated EP3XXX...
Türk Patent MCP / get_patent_details("TR2019/XXXXX")
→ Başvuru 2019, tescil 2022, IPC C07K16, durum AKTİF, yıllık harç güncel

[Adım 10 — Marka]
Türk Patent MCP / search_trademarks(holder_name="Roche", 
   trademark_name="COLUMVI", nice_classes="5")
→ 1 sonuç: COLUMVI® başvuru 2023, tescil 2024

[Adım 11 — Mevzuat MCP (aktif v2.0.1)]
Mevzuat MCP / get_mevzuat_content(mevzuat_no="6769", mevzuat_tur=1, mevzuat_tertip=<arama sonucu>, madde_no="83")
→ "Buluş basamağı: ..." [tam metin alıntı]
Mevzuat MCP / get_mevzuat_content(mevzuat_no="6769", mevzuat_tur=1, mevzuat_tertip=<arama sonucu>, madde_no="85")
→ "Bolar istisnası: ..." [tam metin alıntı]
Provenance: [Mevzuat MCP / get_mevzuat_content / SMK 6769 m.85/3 / 2026-05-01]

[Adım 12 — Çapraz-doğrulama]
- Holder normalizasyonu: ✅ 4 alias → 1 kanonik
- SNOMED bağı: ✅ glofitamab tek concept
- Patent ↔ ürün bağı: TR2019/XXXXX formülasyon, COLUMVI'ye direkt bağlı
- Eşdeğer/biyobenzer: yok (first-in-class)

[Adım 13 — Çıktı]
TR Regülatör + IP Dosyası rapor şablonuna geçiş
```

### 8.2. Çıktıdan kritik bulgular

- **Veri imtiyazı çapası**: 2024-XX-XX TR ruhsat → 2030-XX-XX TR data exclusivity bitişi (6 yıl). EU 2024 → 2032/2034 (8+2+1).
- **Patent duvarı**: TR2019/XXXXX formülasyon patenti 2022 tescilli, 20 yıl → ~2039. Innovator dominant.
- **Biyobenzer fizibilitesi**: Henüz yok; en erken giriş ~2034 (TR data exclusivity sonrası + cihaz/formül patent expiry beklenir).
- **Ek izleme**: Siyah üçgen → 5 yıl pharmakovijilans yoğun.
- **Off-label baskısı**: Şu an liste yok; gelecekte CLL / FL endikasyon genişlemesi sonrası SUT-dışı kullanım baskısı beklenir → onko-erisim skill ile downstream.

### 8.3. Audit trail (yukarıdan)

| # | Veri | Kaynak | Tool | Erişim |
|---|---|---|---|---|
| 1 | COLUMVI barkod | TİTCK MCP | search_drugs | 2026-05-01 |
| 2 | SNOMED + ATC profili | TİTCK MCP | get_drug_snomed_profile | 2026-05-01 |
| 3 | Roche kanonik holder + 4 alias | TİTCK MCP | find_holder_by_alias + list_holder_aliases | 2026-05-01 |
| 4 | Biyobenzer kümesi (boş) | TİTCK MCP | find_biosimilar_group | 2026-05-01 |
| 5 | L01FX sınıf özeti | TİTCK MCP | get_atc_class_summary | 2026-05-01 |
| 6 | Fiyat zinciri | TİTCK MCP | get_price_history | 2026-05-01 |
| 7 | Additional monitoring | TİTCK MCP | find_additional_monitoring_for_drug | 2026-05-01 |
| 8 | TR2019/XXXXX bispesifik patent | Türk Patent MCP | search_patents + get_patent_details | 2026-05-01 |
| 9 | COLUMVI® marka | Türk Patent MCP | search_trademarks | 2026-05-01 |
| 10 | SMK m. 83/4, m. 85/3 metni | Mevzuat MCP | get_mevzuat_content (kimlik arama sonucundan) | 2026-05-01 |

---

*Mevzuat sözleşmesi 1 Ekim 2026 CureoHub araç adları ve KAYSİS entegrasyonuyla güncellendi. Diğer connector örneklerinin tarihleri kendi ölçümlerine aittir; bu belge yeni bir canlı sağlık ölçümü sayılmaz.*
