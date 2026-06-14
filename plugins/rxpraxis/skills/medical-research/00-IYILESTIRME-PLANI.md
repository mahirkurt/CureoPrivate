# medical-research Skill — Kapsamlı İyileştirme Planı (v7.1 → v8.0)

**Belge türü:** Mühendislik iyileştirme planı + konnektör entegrasyon mimarisi
**Hazırlanma tarihi:** 9 Haziran 2026
**Kapsam:** SKILL.md + 18 referans dosyasının uçtan uca yeniden mimarisi
**Yöntem:** Bağlı MCP konnektörlerinin canlı sondalanması (live probing) ile gerçeklik-temelli (ground-truth) doğrulama
**Karar:** Tam yeniden yazım · Markdown çıktı · En geniş kapsamlı konnektör entegrasyonu

---

## 0. Yönetici Özeti

medical-research v7.1, kâğıt üzerinde ~12 konnektörü orkestre eden, 13.466 satırlık (SKILL.md 108 KB + 18 referans) olgun bir araştırma motorudur. Ancak skill, **idealize edilmiş bir konnektör seti** varsayımıyla yazılmıştır; bu oturumda **fiilen bağlı olan MCP sunucularının** gerçek araç şemaları skill'in dokümante ettiğinden hem **daha zengin** (bazı eksenlerde), hem de **yapısal olarak farklıdır** (kritik bir eksende).

Bu planın dayandığı bulgular spekülatif değildir; **canlı çağrılarla doğrulanmıştır** (bkz. §2). Üç başlık:

1. **KRİTİK — AdisInsight şema uyuşmazlığı (v7.1'in amiral özelliğinde correctness hatası).** `drug-intelligence-layer.md` ve `connector-api.md §10`, AdisInsight için bir *Springer Pharma API Bundle* şeması (`organisations` / `phases` / `indications` / `moas` / `drugClass` / `locations` / `fromDate` / `toDate`) dokümante eder. **Fiilen bağlı AdisInsight MCP'si bu şemayı tanımaz.** Gerçek arayüz: `search_drugs` / `get_drug` (+HyDE `query_text`) / `search_trials` / `search_drug_companies` / `generate_chart`; parametreler `drug_name`, `developers`, `dev_phase`, `mechanism`, `targets`, `therapeutic_area`, `indication`. Skill, dokümante ettiği biçimde çağrı kursa **çağrı başarısız olur**.

2. **MAJOR — TİTCK native MCP'si kullanılmıyor.** Skill'in tüm "Türkiye Dörtlüsü", `Exa:web_search_exa site:titck.gov.tr` web-kazıma üzerine kuruludur. Oysa **50+ yapılandırılmış araç** sunan native bir TİTCK MCP'si bağlıdır: barkod-birincil ilaç arama, ATC sınıf özeti (fiyat dağılımı + ruhsat sahipleri), onkoloji off-label endikasyon listesi, biyobenzer/originator grubu, referans fiyat + fiyat geçmişi, eşdeğer ürün, Madde-23 başvuru geçmişi, SNOMED eşlemesi. Türkiye katmanının web-kazımadan **yapısal sorguya** terfisi, tek başına en büyük iyileştirmedir.

3. **MAJOR — Native regülatuvar + tam-metin + omics yığınları boşta.** Bağlı ama entegre edilmemiş: çok-yargı-alanlı **regülatuvar MCP** (native openFDA, WHO ICD-11, WHO GHO disease-burden, Health Canada DPD, Federal Register, EUR-Lex), **annas-mcp** (DOI ile tam-metin keşif + indirme — canlı doğrulandı), **paper-download MCP** (PMC/biorxiv/medrxiv/semantic/crossref tam-metin okuma), native **ChEMBL+ADMET**, native **EPMC** (`get_full_text_article` + `get_copyright_status`), **Tavily** (research/crawl/extract — kotası dolu, Exa-fallback olarak), **NPI registry** (KOL doğrulama), **TÜRKPATENT** MCP, native **Türk Mevzuat** MCP.

**v8.0 tezi:** Skill, soyut konnektör adlarından **doğrulanmış araç kayıt defterine (connector registry)** taşınır; "native-MCP-önce" ilkesi benimsenir; Türkiye native yığını, regülatuvar istihbarat yığını ve tam-metin alma kademesi (cascade) birinci sınıf hale getirilir; AdisInsight katmanı gerçek şemayla yeniden yazılır. Geriye dönük klinik içerik (uzmanlık katmanlarının tıbbi gövdesi) korunur — değişen yalnızca **konnektör tel bağlantısıdır (wiring)**.

---

## 1. Mevcut Durum Analizi (v7.1)

### 1.1 Mimari envanter

| Bileşen | Satır | Rol |
|---|---:|---|
| `SKILL.md` | ~2.300 | Zorunlu yürütme protokolü (Adım 0–4), 9-eksenli domain classifier, çıktı sözleşmesi |
| `connector-api.md` | 473 | 8 çekirdek konnektör + Exa orkestrasyon + AdisInsight/Synapse §10 |
| `extended-api.md` | 1.128 | Native REST şablonları (EuropePMC, OpenAlex, DailyMed, ChEMBL, PubChem, S2, Unpaywall, DOAJ, J-STAGE) — **Python `requests` tabanlı** |
| `drug-intelligence-layer.md` | 555 | AdisInsight katmanı — **hatalı şema** |
| `evidence-grading.md` | 255 | Tier 0–6 hiyerarşisi, GRADE, pragmatik derecelendirme, NER |
| `output-templates.md` | 888 | Format A–I + `.data.json` sidecar şeması (v7.0) |
| 8 uzmanlık katmanı | ~6.700 | onkoloji, hematoloji, regülatuvar, HTA, medical affairs, immunoloji, nöroloji, nadir hastalık |
| osint / execution-map / composition-runbook / benchmark ×2 | ~1.900 | Altyapı + OSINT + test |

### 1.2 v7.1 konnektör modeli ve zayıf noktaları

- **Exa-ağırlıklı.** Kılavuzlar, regülasyon, Türkiye verisi, full-text — hepsi Exa `web_search_exa` ile `site:` kazıması üzerine kurulu. Exa'nın `includeDomains`/`freshness` desteği yok; bu skill'de açıkça bir kısıt olarak belgelenmiş. Sonuç: **yapısal veri (fiyat, ATC, ruhsat tarihi, FAERS sayımı) serbest-metin aramayla elde edilmeye çalışılıyor.**
- **Python-requests tabanlı extended tier.** EuropePMC, OpenAlex, ChEMBL, DailyMed, PubChem, Unpaywall, DOAJ `bash_tool` + `requests` ile çağrılıyor. Bunların bir kısmının artık **native MCP** karşılığı var (daha hızlı, daha az kırılgan, kota/rate yönetimi sunucuda).
- **AdisInsight/Synapse soyut.** §10 ve `drug-intelligence-layer.md` gerçek MCP'ye değil, varsayımsal bir Springer API'sine göre yazılmış; "tool name discovery protocol" ile belirsizlik itiraf edilmiş.
- **Türkiye = web kazıma.** Kullanıcının uzmanlık alanı (TR pharma/onkoloji/regülasyon) tam da burada zayıf.

---

## 2. Yöntem — Canlı Konnektör Sondalaması (Ground-Truth)

İyileştirme önerileri, bağlı MCP'lerin **gerçek çağrılarıyla** doğrulanmıştır. Kanıt tablosu:

| # | Konnektör (sunucu) | Sonda | Sonuç (kanıt) |
|---|---|---|---|
| 1 | **AdisInsight** (`6a9fd4a4…`) | `search_drugs(drug_name="glofitamab")` | ✅ Tam profil tek çağrıda: Columvi markası, CD20×CD3 bispesifik, STARGLO Faz III, **FDA CRL Tem 2025**, **ODAC May 2025**, EU/Çin/Kanada ruhsat, Roche/Genentech/Chugai rolleri, `adis_insight_profile_url`. **Dokümante şema yanlış doğrulandı.** |
| 2 | **TİTCK** (`1a49b1bb…`) | `search_drugs(query="trastuzumab")` | ✅ Herceptin (referans) + Trazimera/Herzuma (biyobenzer) + Teruvia + Kadcyla (ADC); barkod, ATC (L01FD01), **GERİ ÖDEMELİ**, 2026 fiyatları (TRY + kaynak-ülke EUR), SNOMED concept_id, ruhsat tarihi. |
| 3 | **annas-mcp** | `article_search(GRADE DOI)` → `article_download` | ✅ GRADE 2008 (Guyatt) bulundu; **indirme başarılı** (`C:\Users\…\Downloads`). Cochrane Handbook 2. baskı (2019/2020) bulundu. Tam-metin kademesi **canlı doğrulandı**. |
| 4 | **Regülatuvar MCP** (`922d7cdc…`) | `who_gho_query(WHOSIS_000001, TUR)` | ✅ Türkiye yaşam beklentisi serisi (2001–2021, GBD-tipi CI). ⚠️ **Gecikme riski**: bir paralel çağrı 180 s'de timeout. |
| 5 | **AdisInsight** şema | `get_drug` şeması | ✅ HyDE iş akışı: `drug_name` + `query_text` (8–10× tekrar) + `resources` + `min_similarity`. `generate_chart` (Chart.js) mevcut. |
| 6 | **Tavily** (`30203133…`) | `tavily_search(...)` | ⚠️ HTTP 432 — **kota dolu**. Bağlı ama canlı değil → Exa-fallback olarak tasarlanmalı. |
| 7 | **EPMC** (`8f314cbe…`) | şema | ✅ `search_articles` (PubMed sözdizimi + tarih) · `get_full_text_article` (PMC) · `get_copyright_status` (açık-erişim/lisans tespiti). |
| 8 | **ChEMBL** (`bio-research:chembl`) | şema | ✅ `drug_search` · `get_mechanism` · `get_admet` (QED + Lipinski/Veber + hERG) · `target_search` (gen→UniProt). |
| 9 | **TİTCK** ek | şema | ✅ `compare_drug_to_alternatives` (eşdeğer peers + fiyat delta), `get_atc_class_summary`, `find_off_label_uses_for_drug`, `find_biosimilar_group`. |
| 10 | **OpenTargets** (`bio-research:ot`) | ToolSearch | ❌ Henüz yüzeye çıkmadı (bağlanıyor). Koşullu/opsiyonel tasarlanmalı. |

**Veri kalitesi notu (sondadan):** TİTCK kayıtlarında ATC kodu master kayıtta güncel (`L01FD01`) ama `detailed_price_list` alt-alanında eski (`L01XC03`) olabilir. v8.0 bu ikili-ATC nüansını açıkça belgeler ve master kaydı otorite kabul eder.

---

## 3. Bulgu — Konnektör Gerçeklik Açığı (Severity-Rated)

| Önem | Bulgu | Mevcut v7.1 davranışı | v8.0 düzeltmesi |
|---|---|---|---|
| 🔴 **CRITICAL** | AdisInsight şema uyuşmazlığı | Var olmayan `organisations/phases/moas` parametreleriyle çağrı → başarısızlık | `drug-intelligence-layer.md` tamamen yeniden yazılır; gerçek `search_drugs/get_drug/generate_chart` şeması + HyDE |
| 🟠 **MAJOR** | TİTCK native MCP boşta | `Exa site:titck.gov.tr` kazıma | Yeni `turkiye-layer.md`: 15+ TİTCK aracı yapısal sorgu |
| 🟠 **MAJOR** | Regülatuvar native MCP boşta | openFDA Python `requests`; ICD/WHO-GHO yok | Yeni `regulatory-intelligence.md`: native openFDA + ICD-11 + WHO GHO + Health Canada + Federal Register |
| 🟠 **MAJOR** | Tam-metin kademesi yok | Yalnız `Exa:web_fetch_exa` (paywall'da kör) | Yeni `fulltext-retrieval.md`: EPMC PMC → copyright → annas → paper-download → Wiley |
| 🟡 **MODERATE** | Python-requests vs native | EuropePMC/ChEMBL/openFDA `requests` | `extended-api.md`: native-MCP-önce, `requests` fallback |
| 🟡 **MODERATE** | Tavily entegre değil | — | `connector-registry.md`: Tavily research/crawl/extract; kota fallback Exa |
| 🟡 **MODERATE** | KOL doğrulama zayıf | OpenAlex + EPMC meta | NPI registry (ABD PI doğrulama) + OpenAlex |
| 🟡 **MODERATE** | TR patent / mevzuat boşta | Exa kazıma | TÜRKPATENT MCP + native Mevzuat MCP (SUT/yönetmelik) |
| 🟢 **MINOR** | Synapse/OpenTargets/Wiley/Owkin | Soyut referans | Koşullu + OAuth-gated; graceful skip |
| 🟢 **MINOR** | `generate_chart` kullanılmıyor | — | Inline pipeline/pazar grafikleri için AdisInsight `generate_chart` |

---

## 4. v8.0 Doğrulanmış Konnektör Kayıt Defteri (Connector Registry)

Aşağıdaki tablo, skill'in soyut "8 konnektör" modelini değiştiren **gerçeklik-temelli kayıt defteridir**. Tam, çağrılabilir araç adları `references/connector-registry.md`'de listelenir.

### 4.1 Akademik literatür çekirdeği
| Konnektör | Anahtar araçlar | Skill fazı |
|---|---|---|
| PubMed/EPMC (`8f314cbe` + `bio-research:pubmed`) | `search_articles`, `get_full_text_article`, `get_copyright_status`, `convert_article_ids`, `find_related_articles` | Phase 2.1 #1 |
| Consensus (`b2afd737` + `bio-research:consensus`) | `search` (zorunlu inline atıf) | Phase 2.1 #2 |
| Scholar Gateway (`0db119cc`) | `semanticSearch` (yıl filtresi, retracted toggle) | Phase 2.1 #3 |
| Paper Search/Download (`660e91bd`) | `search`, `search_pubmed`, `read_pubmed_paper`, `download_*` | Phase 2.1 #4 + full-text |
| Clinical Trials v2 (`4cc36ce0` + `bio-research:c-trials`) | `search_trials`, `get_trial_details`, `search_by_sponsor`, `search_investigators`, `analyze_endpoints` | Phase 2.1 #5 |
| bioRxiv/medRxiv (`4e673875` + `bio-research:biorxiv`) | `search_preprints`, `get_preprint`, `search_published_preprints` | Phase 2.1 #6 |
| YÖK Tez (`b2d46b46`) | `search_yok_tez_detailed`, `get_yok_tez_document_markdown` | Phase 2.1 #7 (TR) |
| Exa (`b2b8051d`) | `web_search_exa`, `web_fetch_exa` | Phase 2.1 #11 (gap-filling) |
| Tavily (`30203133`) | `tavily_search`, `tavily_research`, `tavily_extract`, `tavily_crawl`, `tavily_map` | Exa-tamamlayıcı (kota fallback) |

### 4.2 Kuratörlü istihbarat + mekanizma
| Konnektör | Anahtar araçlar | Not |
|---|---|---|
| **AdisInsight** (`6a9fd4a4`) | `search_drugs`, `get_drug`(HyDE), `search_trials`, `search_drug_companies`, `search_trial_companies`, `generate_chart` | **Gerçek şema** — drug intelligence ekseni |
| **ChEMBL** (`bio-research:chembl`) | `drug_search`, `compound_search`, `get_mechanism`, `get_admet`, `get_bioactivity`, `target_search` | Native — mekanizma/ADMET |
| Synapse (`bio-research:synapse`) | `authenticate` → multi-omics | OAuth-gated; koşullu |
| OpenTargets (`bio-research:ot`) | (henüz çevrimdışı) | Koşullu; target-disease association |
| Wiley (`bio-research:wiley`) | `authenticate` → publisher full-text | OAuth-gated; full-text kademesinde |

### 4.3 Regülatuvar + epidemiyoloji + Türkiye + IP
| Konnektör | Anahtar araçlar | Skill fazı |
|---|---|---|
| **Regülatuvar MCP** (`922d7cdc`) | `openfda_search` (FAERS/label/drugsfda/enforcement), `icd11_search`, `who_gho_query`, `health_canada_dpd`, `federal_register_search`, `eurlex_expert_search` | Phase 2.2 + reg/HTA katmanları |
| **TİTCK** (`1a49b1bb`) | `search_drugs`, `get_drug`, `get_atc_class_summary`, `find_off_label_uses_for_drug`, `find_biosimilar_group`, `find_reference_prices_for_drug`, `compare_drug_to_alternatives`, `search_regulation_article23`, `find_authorization_cancellations_for_drug` | Türkiye Dörtlüsü (native) |
| **Mevzuat** (`fbf16a1a`) | `search_mevzuat`, `get_mevzuat_text`, `get_anayasa`, `get_mevzuat_madde_tree` | SUT/yönetmelik/regülasyon |
| **TÜRKPATENT** (`ded65854`) | `search_patents`, `search_trademarks`, `search_designs` | pharmapatent kompozisyonu |
| **NPI Registry** (`64557ced`) | `npi_search`, `npi_lookup`, `npi_validate` | KOL/PI doğrulama (ABD) |
| **annas-mcp** | `article_search`, `book_search`, `article_download`, `book_download` | Tam-metin kademesi |

### 4.4 Yardımcı (compose/visualize)
`carbon-html-report`, `carbon-pptx` (sidecar tüketici); `mevzuat` + `TÜRKPATENT` (onko-erisim/saglik-sigorta/pharmapatent kompozisyonu); AdisInsight `generate_chart` (inline görsel).

---

## 5. v8.0 Mimari Değişiklikleri

### 5.1 İlke: "Native-MCP-Önce" (Native-First Resolution)
Her veri ihtiyacı için çözüm sırası: **(1) native MCP aracı → (2) Python `requests` native REST → (3) Exa/Tavily web kazıma → (4) belgelenmiş boşluk.** Bu, `extended-api.md`'nin Python-ağırlıklı yapısını tersine çevirir: native MCP varsa o kullanılır; `requests` yalnızca native MCP yoksa fallback'tir.

### 5.2 Yeni: Türkiye Native Yığını (`turkiye-layer.md`)
Türkiye Dörtlüsü yeniden tanımlanır:
1. **TİTCK native** (`search_drugs` + `get_atc_class_summary` + off-label + biyobenzer + referans fiyat) — web kazıma yerine yapısal sorgu.
2. **Mevzuat native** (`search_mevzuat` → SUT, beşeri tıbbi ürünler yönetmeliği, fiyat kararnameleri).
3. **YÖK Tez** (mevcut, korunur).
4. **EuropePMC `AFF:"Turkey"`** (mevcut, korunur).
5. **TÜRKPATENT** (jenerik/biyobenzer IP — pharmapatent kompozisyonu için).

Bu, kullanıcının çekirdek uzmanlık alanını (TR pharma/onkoloji/regülasyon, EctoCare/Erapharma bağlamı) doğrudan besler ve `onko-erisim` / `saglik-sigorta` / `pharmaintel` / `rxos` skill kompozisyonlarını güçlendirir.

### 5.3 Yeni: Regülatuvar İstihbarat Yığını (`regulatory-intelligence.md`)
- **openFDA native** (`openfda_search`): FAERS sinyal sayımı (count agregasyonu), drug/label, drugsfda (onay), enforcement (recall). Python `requests` openFDA kaldırılır.
- **WHO ICD-11** (`icd11_search`): endikasyon kodlama, regülatuvar/HTA dosyalarında ICD atfı.
- **WHO GHO** (`who_gho_query`): hastalık yükü / epidemiyoloji (insidans, mortalite, yaşam beklentisi) — HTA budget-impact ve nadir hastalık prevalansı için. ⚠️ gecikme-toleranslı çağrı (retry + uzun timeout).
- **Health Canada DPD + Federal Register + EUR-Lex**: çok-yargı-alanlı regülatuvar çapraz referans (regülatuvar katman §13).
- **EMA** (Exa `site:ema.europa.eu` korunur — native MCP yok).

### 5.4 Yeni: Tam-Metin Alma Kademesi (`fulltext-retrieval.md`)
Kademeli cascade (canlı doğrulandı):
1. **EPMC `get_full_text_article`** (PMC açık erişim) + `get_copyright_status` (lisans tespiti — Unpaywall/DOAJ'ı tamamlar).
2. **paper-download MCP** `read_pubmed_paper` (PMC tam-metin çıkarımı).
3. **annas-mcp `article_download`** (DOI ile paywall'lı makale — **çalıştığı doğrulandı**) / `book_search`+`book_download` (metodoloji kitapları: Cochrane Handbook, GRADE, ESMO-MCBS rehberleri).
4. **Wiley** (OAuth-gated publisher full-text).
5. **Exa `web_fetch_exa`** (son çare).

**Telif uyumu:** annas/Wiley tam-metni yalnızca **analiz/çıkarım** için kullanılır; çıktıda hiçbir zaman büyük bloklar verbatim çoğaltılmaz (Anthropic telif kuralları). `get_copyright_status` ile açık-erişim (CC-BY) tespit edilenler serbest alıntılanır.

### 5.5 Düzeltme: Drug Intelligence Layer (`drug-intelligence-layer.md` — tam yeniden yazım)
- Gerçek `search_drugs` parametreleri (`drug_name`, `developers`, `dev_phase`, `mechanism`, `targets`, `therapeutic_area`, `indication`, `dev_phase_any`, `mechanism_any`, boolean'lar: `orphan_drug_status`, `btt_status`, `fast_track_status`, `prime_status`, `new_molecular_entity`).
- `get_drug` HyDE iş akışı (`query_text` 8–10× tekrar + `resources` + `min_similarity=0.2` + `limit=10`).
- `doc_id` → derin alım deseni.
- `generate_chart` ile inline pipeline/faz dağılımı grafikleri.
- Çapraz-referans protokolü korunur (CT.gov + DailyMed + EMA + openFDA FAERS), ama `pipeline_payload` sidecar gerçek alanlarla güncellenir (`adis_insight_profile_url`, `history_events` regülatuvar milestone'ları, `development_phases` ülke-bazlı).
- Zero-result fallback: AdisInsight `search_drugs` boş → `search_drug_companies` → Exa `site:adisinsight.springer.com` → CT.gov+DailyMed sentezi.

### 5.6 Genişletme: Domain Classifier — Yeni Eksen 0.5.K (Epidemiyoloji/Disease Burden)
WHO GHO + ICD-11 + GLOBOCAN sinyalleri (insidans, prevalans, mortalite, hastalık yükü, DALY, epidemiyoloji, "kaç hasta", "Türkiye'de görülme sıklığı") yeni bir eksen tetikler → regülatuvar/HTA/nadir-hastalık katmanlarına epidemiyolojik temel sağlar. Mevcut 9 eksen (0.5.A–0.5.J) korunur.

### 5.7 generate_chart ile inline görselleştirme
AdisInsight `generate_chart` (Chart.js) ile faz dağılımı, rakip peyzajı, indikasyon-bazlı pipeline grafiklerinin sidecar'a + Carbon rapora aktarımı.

---

## 6. Zorluklar, Riskler ve Azaltım Stratejileri

| Risk | Etki | Azaltım |
|---|---|---|
| **Regülatuvar MCP gecikmesi** (180 s timeout gözlemlendi) | WHO GHO/openFDA çağrıları yavaş | Gecikme-toleranslı çağrı: tekil (paralel değil), retry + exponential backoff; kritik değilse atlanabilir-işaretli |
| **Tavily kota dolu** (HTTP 432) | Tavily canlı değil | Tavily her zaman Exa-fallback'li; kota dolarsa otomatik Exa'ya düşülür; çıktıda not |
| **OAuth-gated konnektörler** (Wiley, Synapse, Owkin, BioRender) | `authenticate` gerektirir | Koşullu; auth yoksa graceful skip + "auth gerekli" notu; çekirdek akış etkilenmez |
| **OpenTargets çevrimdışı** | Target-disease association yok | Koşullu yükleme; yoksa ChEMBL `target_search` + EPMC ile telafi |
| **AdisInsight rate/lisans** | Springer Nature kotası | `generate_chart`/`get_drug` cömert ama tekrar-dirençli; boş dönerse §5.5 fallback |
| **Telif (annas/Wiley full-text)** | Verbatim çoğaltma riski | Yalnız analiz; `get_copyright_status` ile CC-BY tespiti; büyük blok alıntı yasak |
| **TİTCK ATC ikiliği** (L01FD01 vs L01XC03) | Eski/yeni ATC karışıklığı | Master kayıt otorite; alt-alan farkı belgelenir |
| **TİTCK `find_drug_drug_interactions` yanıltıcı adı** | Klinik DDI sanılması | v8.0 açıkça uyarır: bu araç **madde-örtüşmesi** verir, klinik DDI değil → `find_shared_substance_peers` kullan |
| **Çift konnektör** (EPMC `8f314cbe` + `bio-research:pubmed`; CT.gov `4cc36ce0` + `c-trials`) | Hangisi? | Registry'de birincil seçilir; diğeri fallback |

---

## 7. Alternatif Yaklaşımlar (Değerlendirilen)

- **(A) Yalnız hata düzeltme (minimal):** Sadece AdisInsight şemasını düzelt, gerisini bırak. → Reddedildi: kullanıcı "en geniş kapsam" istedi; TİTCK/regülatuvar/full-text fırsatları kaçırılır.
- **(B) Tüm 18 dosyayı tek turda verbatim yeniden yaz:** → Pratik değil (13.5k satır; bağlam/kalite riski). Kullanıcının seçtiği "tam yeniden yazım" opsiyonu zaten "birden çok tur gerektirir" notunu içeriyordu.
- **(C) Seçilen — Çekirdek-önce, kademeli tam yeniden yazım:** Bu turda plan + SKILL.md + connector-critical referanslar tam yazılır; uzmanlık katmanları connector-wiring yamasıyla güncellenir (klinik gövde korunur); kalan dosyalar takip turlarında. → Hem kalite hem kapsam optimize edilir.

---

## 8. Migrasyon Yol Haritası (Dosya-Dosya)

### Faz P0 — Bu tur (çekirdek v8.0)
| Dosya | Aksiyon | Durum |
|---|---|---|
| `00-IYILESTIRME-PLANI.md` | Yeni — bu belge | ✅ |
| `SKILL.md` | Tam yeniden yazım (v8.0 protokol + registry + classifier + çıktı) | bu tur |
| `references/connector-registry.md` | **Yeni** — `connector-api.md`'yi değiştirir; doğrulanmış araç tablosu | bu tur |
| `references/drug-intelligence-layer.md` | Tam yeniden yazım — gerçek AdisInsight şeması | bu tur |
| `references/turkiye-layer.md` | **Yeni** — TİTCK + Mevzuat + YÖK + TÜRKPATENT native | bu tur |

### Faz P1 — Takip turu (genişletilmiş entegrasyon)
| Dosya | Aksiyon |
|---|---|
| `references/regulatory-intelligence.md` | **Yeni** — openFDA/ICD-11/WHO-GHO/Health Canada native |
| `references/fulltext-retrieval.md` | **Yeni** — EPMC PMC → copyright → annas → paper-download → Wiley kademesi |
| `references/extended-api.md` | Yeniden yazım — native-MCP-önce, `requests` fallback |
| `references/evidence-grading.md` | Güncelleme — full-text cascade + copyright + annas metodoloji grounding |
| `references/output-templates.md` | Güncelleme — sidecar v8.0, yeni konnektörler, `connectors_used` listesi |

### Faz P2 — Takip turu (uzmanlık katmanı wiring yaması)
8 uzmanlık katmanı (onko/heme/reg/HTA/MA/immun/nöro/rare) + osint/execution-map/composition-runbook/benchmark: **klinik içerik korunur**, yalnızca konnektör çağrıları v8.0 native araçlarına çevrilir (tek bir `v8-wiring-patch.md` find/replace spesifikasyonu + her dosyaya hedefli düzenleme).

### Faz P3 — Doğrulama
`benchmark-suite.md` güncellenir: her connector referansının gerçek araca çözümlendiği otomatik kontrol + 10 regresyon sorgusu (TR onkoloji, AdisInsight pipeline, full-text retrieval, WHO GHO epidemiyoloji).

---

## 9. Doğrulama / Test Stratejisi

v8.0 yayın-öncesi kapıları:
1. **Referans bütünlüğü:** SKILL.md + referanslardaki her MCP araç adı, §4 registry'deki gerçek bir araca çözümlenmeli (grep + manuel eşleme).
2. **Şema doğruluğu:** AdisInsight/TİTCK/regülatuvar çağrı şablonları, bu planda doğrulanmış parametre adlarını kullanmalı.
3. **Fallback zinciri:** Her birinci-seçenek konnektör için en az 1 fallback (Tavily→Exa, native→requests, AdisInsight→sentez).
4. **Telif kapısı:** Full-text bölümünde verbatim-çoğaltma yasağı + copyright-status kontrolü açıkça yazılı.
5. **Regresyon:** Benchmark sorguları (örn. "trastuzumab TR fiyat + biyobenzer peyzaj", "glofitamab pipeline + ODAC", "DLBCL ESMO + Cochrane full-text") beklenen katman aktivasyonu + konnektör seti ile eşleşmeli.

---

## 10. v8.0 Sürüm Özeti (changelog taslağı)

> **v8.0 — MAJOR: Ground-Truth Connector Integration.** Soyut konnektör modeli, canlı-doğrulanmış **connector registry**'ye taşındı. **KRİTİK DÜZELTME:** AdisInsight katmanı gerçek MCP şemasıyla (`search_drugs`/`get_drug` HyDE/`generate_chart`) yeniden yazıldı (v7.1 hatalı Springer-API şeması kaldırıldı). **Yeni native yığınlar:** Türkiye (TİTCK 15+ araç + Mevzuat + TÜRKPATENT), Regülatuvar İstihbarat (native openFDA + ICD-11 + WHO GHO + Health Canada + Federal Register), Tam-Metin Alma Kademesi (EPMC PMC + copyright-status + annas-mcp + paper-download + Wiley). **Yeni ilke:** Native-MCP-Önce çözümleme. **Yeni eksen:** 0.5.K Epidemiyoloji/Disease Burden (WHO GHO + ICD-11). **Tavily** research/crawl/extract eklendi (Exa-fallback'li, kota-dirençli). **NPI registry** KOL doğrulama. **generate_chart** inline görselleştirme. Geriye dönük: uzmanlık katmanlarının klinik içeriği korundu; yalnız konnektör wiring değişti. Tüm araç adları bu oturumda canlı sondalarla doğrulandı.

---

*Bu plan, bağlı MCP konnektörlerinin 9 Haziran 2026'da yapılan canlı çağrılarıyla doğrulanmış bulgulara dayanır. Araç şemaları ve örnek çıktılar gerçektir; spekülatif değildir.*
