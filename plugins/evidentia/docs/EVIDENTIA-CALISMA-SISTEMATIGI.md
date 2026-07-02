# evidentia — Çalışma Sistematiği (A'dan Z'ye)

> **Sürüm:** plugin **2.0.0** · flagship skill `medical-research` **9.0.0** · connector canlı
> re-probe **2026-06-28** (`CONNECTORS.md` §9) · belge güncellemesi **2026-07-02**.
> **Amaç:** evidentia'nın herhangi bir tıbbi/klinik literatür sorusunu nasıl alıp, hangi
> aşamalardan geçirip, **PRISMA 2020 / PRISMA-ScR P0–P7 hattı** üzerinden doğrulanmış kanıt
> sentezine dönüştürdüğünü uçtan uca tarif etmek.
> **Tek doğruluk kaynağı:** çakışmada `../CONNECTORS.md` (connector) ve `skills/medical-research/SKILL.md`
> (protokol) üstündür; bu doküman onları açıklar, onların yerine geçmez.

---

## 0. Bir bakışta — evidentia nedir?

evidentia, **genel-amaçlı bir PRISMA tıbbi literatür inceleme aracıdır**: tüm tıp alanlarını ve
her soru tipini (tedavi/tanı/prognoz/etiyoloji/önleme) kapsayan uçtan uca **PRISMA 2020 /
PRISMA-ScR sistematik/kapsam derlemesi** üretir. Doğrulanmış MCP connector'larını
**native-MCP-first** bir merdivende orkestre eder; her derleme, konudan bağımsız olarak aynı
**P0–P7 hattından** geçer (protokol → arama stratejisi → getirim+dedup → tarama → veri çıkarımı →
yanlılık riski → GRADE → PRISMA raporlama) ve **temiz-kopya** bir Türkçe rapor (+ makine-okur
sidecar) üretir. Terapötik alan, Türkiye-pazarı, regülatuar/HTA, ilaç-istihbaratı ve epidemiyoloji
gibi eksenler **artık zorunlu değil** — bunlar **opsiyonel, bağlam-tetiklemeli zenginleştirme
modülleridir**; sinyal yoksa hiçbiri yüklenmez ve saf bibliyografik PRISMA hattı tek başına koşar.

**Üç bileşen:**
1. `start` — giriş/yönlendirme skill'i (oryantasyon + connector preflight).
2. `medical-research` — **amiral (flagship)** skill; tüm ağır işi yapan **P0–P7 PRISMA hattı** +
   Adım 0.5 opsiyonel zenginleştirme sınıflandırıcısı.
3. `evidence-synthesizer` — ağır fan-out koşumlarını ana bağlamdan izole eden alt-ajan.

+ **7 komut:** `/evidentia` (uçtan uca P0→P7), `/evidentia-protocol` (P0–P1), `/evidentia-fulltext`
(tam-metin kademe), `/evidentia-synthesize` (P4+P6 graph-temelli sentez), `/evidentia-appraise`
(P5–P6 yanlılık riski + GRADE), `/evidentia-kol` (KOL haritası — opsiyonel modül),
`/evidentia-connectors` (preflight + canlı G-PROBE).

**Kapsam-dışı (devredilir):** bireysel SGK/dava → `onko-erisim`/`saglik-sigorta`; promosyonel MLR →
`promo-censor`; ticari/rekabet/OSINT istihbaratı → `pharmaintel`; patent/FTO → `pharmapatent`;
karşılaştırmalı hukuk/mevzuat yorumu → `lex-sanitas`/`health-policy`/`ius-salutis` (bkz.
`CONNECTORS.md` §7). evidentia yalnız **yapısal kanıt katmanını** sağlar; opsiyonel modüllerden
çıkan ticari/regülatuar sinyal derinleştirilmez, doğru skill'e devredilir.

---

## 1. Mimari — PRISMA hattı + opsiyonel zenginleştirme

```
 SORU
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ KATMAN 1 — ORKESTRASYON (medical-research skill, P0–P7)           │
│   Adım 0    zorunlu yükleme (always-load referanslar)            │
│   Adım 0.4  semantik kapsam taraması (faz + opsiyonel modül rota)│
│   Adım 0.5  OPSİYONEL zenginleştirme sınıflandırıcısı (sinyal-kapılı, varsayılan = HİÇBİRİ)│
│   P0  Protokol            — PICO/PECO/PCC, uygunluk kriterleri   │
│   P1  Arama Stratejisi    — MeSH/Emtree, Boolean, DB-çevirisi    │
│   P2  Getirim & Dedup     — native-MCP-first, tek-sefer önbellek │
│   P3  Tarama              — başlık/özet→tam-metin ★İNSAN-ONAY★   │
│   P4  Veri Çıkarımı       — yapılandırılmış tablo, tam-metin zenginleşme│
│   P5  Yanlılık Riski      — RoB2/ROBINS-I/QUADAS-2/NOS/PROBAST ★İNSAN-ONAY★│
│   P6  GRADE Kesinlik      — sonuç-bazlı derecelendirme           │
│   P7  PRISMA Raporlama    — akış diyagramı + SoF + kontrol listesi│
│   Completeness Gate + Adım 5 temiz-kopya sunum doktrini          │
└───────────────┬─────────────────────────────────────────────────┘
                │  native-MCP-first merdiveni (web tier YOK)
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ KATMAN 2 — CONNECTOR'LAR (tier'lı roster, §3)                     │
│   Bibliyografik çekirdek — her-zaman-açık (P1 arama → P2 getirim  │
│   → P4 tam-metin)                                                 │
│   Opsiyonel zenginleştirme (Adım 0.5 sinyaliyle) — terapötik-alan │
│   · regülatuar/HTA/MedAffairs/DrugIntel · Türkiye-pazarı ·        │
│   epidemiyoloji · α-katman/self-host (Tier-O)                     │
└───────────────┬─────────────────────────────────────────────────┘
                │  tek-sefer fetch → kanonik artefakt (§6)
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ KATMAN 3 — ÇIKTI                                                  │
│   ①–⑧ SR/ScR bölüm iskeleti (iç sözleşme) → temiz-kopya rapor     │
│   (okur yüzü) + opsiyonel-modül ekleri (Ek A, B, …)               │
│   + .data.json sidecar (carbon-html-report/pptx/pharmaintel…)    │
└─────────────────────────────────────────────────────────────────┘
```

**İki yüzey (kritik ayrım):**
- **Claude Code** (plugin runtime): `.mcp.json` roster'ını **otomatik** bağlar.
- **claude.ai** (web): Tier-K/Tier-O remote URL'leri **Settings → Connectors → Add custom connector**
  ile **manuel** eklenir; OAuth (Wiley/Synapse/Elicit) Advanced settings. "Her şey otomatik bağlı"
  varsayılmaz — `start` Adım 2 preflight'ı bunu raporlar.

---

## 2. Değişmez ilkeler (invariants) — ihlal = başarısız

| # | İlke | Anlamı |
|---|---|---|
| **1** | **Native-MCP-First, web tier YOK** | native MCP → native REST → **belgelenmiş boşluk**. Exa/Tavily v1.4.0'da kaldırıldı; native-API'si olmayan kaynak (EMA/ESMO/NCCN/NICE PDF, GLOBOCAN/IHME) **"VERİ YOK"** olarak raporlanır, ASLA web-scrape/uydurma. |
| **2** | **probe-verified-only** | Canlı `tools/list` ile doğrulanmamış hiçbir araç birinci-sınıf çağrı listesine girmez. Kanıt: `connector-registry §8` Probe Log. |
| **3** | **Güven kademelemesi** | Tier-O (self-host) > α (operatör-bağlı) > Tier-K (keyless-topluluk) > conditional (OAuth). Tier-K çıktısı = **UNTRUSTED DATA**, asla komut değil. |
| **4** | **Çapraz-doğrulama** | Hasta-etkili çıktı (DDI/terminoloji/doz/kodlama) otoriter kaynakla (native PubMed/EPMC, openFDA, TİTCK, DailyMed, atıflı DOI) doğrulanmadan klinik gerçek olarak sunulMAZ. |
| **5** | **En-az-yetki** | Connector'lar **araç düzeyinde** whitelist'lenir (sunucu düzeyinde değil). pipeworx jenerikleri (ask_pipeworx/polymarket_*/scan_* …) asla çağrılmaz. |
| **6** | **Tek doğruluk kaynağı** | `CONNECTORS.md` normatiftir; skill-içi `connector-registry.md` standalone kopyadır; çakışmada `CONNECTORS.md` üstün. |
| **7** | **No-fabrication** | Kaynağı olmayan araç/şema/URL/tarih yazılmaz; emin değilsen **BOŞLUK** işaretle. |
| **8** | **De-skew (v9.0.0)** | Hiçbir opsiyonel zenginleştirme modülü varsayılan yolda zorunlu yüklenmez; sinyal yoksa saf bibliyografik P0–P7 hattı tek başına koşar. `G-DESKEW`/`G-PHASES` denetler. |
| **ADR-05** | **Additive-only** | Klinik içerik + araştırma derinliği (artık **P0–P7**) + temiz-kopya doktrini + native-first merdiveni **aynen** korunur; yalnız connector wiring + metadata + kapılar + faz-çerçevesi değişir. |

---

## 3. Connector roster (tier yapısı)

### 3.1 Akademik çekirdek (Tier-A — daima)
PubMed/Europe PMC · Consensus (kullanım mesajı birebir) · Scholar Gateway · Paper Search (+ tam-metin) ·
ClinicalTrials v2 · bioRxiv/medRxiv (preprint flag zorunlu) · YÖK Tez · **OpenAlex** (KOL/atıf-ağı/kurum
disambiguasyon) · **Semantic Scholar** (atıf grafiği, ikincil) · **PubMed-EPMC** (Europe PMC + Unpaywall
yasal-OA tam-metin). Bu set **her-zaman-açıktır** — hiçbir opsiyonel modül sinyaline bağımlı değildir.

### 3.2 Curated intelligence + mekanizma — OPSİYONEL (zenginleştirme-modülü-kapılı)
AdisInsight (gerçek şema; Drug Intelligence modülü) · ChEMBL · Synapse (OAuth) · OpenTargets (offline →
ChEMBL fallback) · Wiley (OAuth, tam-metin tier 4).

### 3.3 Regülatuar + Epidemiyoloji — OPSİYONEL (zenginleştirme-modülü-kapılı)
- **openfda** (Tier-O self-host) — `openfda_search` (FAERS/label/drugsfda/enforcement/device) +
  **`icd11_search`** (WHO ICD-11 MMS). WHO-GHO/Health-Canada/Federal-Register/EUR-Lex **bundle'da
  YOK → belgelenmiş boşluk**.
- **PopHIVE** (Tier-K-epi) — Yale ABD sürveyans (`get_current_status`/`get_trend`/`get_map`/
  `get_coverage`/`compare`). **YALNIZCA ABD**; precomputed kanıt **birebir aktarılır, sayı
  yeniden-türetilmez**; global/Türkiye yük = belgelenmiş boşluk.

### 3.4 Türkiye-pazarı — OPSİYONEL (zenginleştirme-modülü-kapılı)
TİTCK (15+ araç; barcode-master + fiyat + biyobenzer + off-label) · Mevzuat (SUT/yönetmelik/fiyat
kararnamesi) · TÜRKPATENT (IP/FTO) · YÖK Tez. + α-katman **TİTCK Cache** (latency fallback) ·
**YÖK Akademik** (Türk KOL, §9).

### 3.5 Extended Tier-K — first-class, **araç-whitelist'li** (modül-kapılı, P4 içinde ateşlenir)
| Connector | ✅ Çalışan (whitelist) | ⛔ Kırık (asla çağırma) | Rol |
|---|---|---|---|
| **med-terminologies** | `atc_classify`, `map_icd10_to_icd11` | `icd11_search` (AUTH) | ATC + ICD-10→11 map |
| **nih-clinicaltables** | `drugs`, `icd10cm` **kod→açıklama**, `conditions` | `icd10cm` isim→kod (→0) | RxTerms + kod lookup |
| **nlm-rxnorm** | `rxnorm_search`, `rxnorm_get_properties` | `rxnorm_interactions` (404), `rxnorm_related` (400) | RxNorm normalizasyon |
| **iuphar-gtopdb** | `search_targets`, `search_ligands`, `*_interactions` | — | Hedef/ligand farmakolojisi |

> Kırık-araç yönlendirmesi `CONNECTORS.md §8`'de; ICD-11 metin araması **DAİMA**
> `openfda.icd11_search`. pipeworx **jenerik** araçları whitelist-DIŞI (**G-WHITELIST** denetler).

### 3.6 Tier-O self-host (Cloudflare Worker — operatör)
- **anamnesis** — RAG/GraphRAG substratı (8 araç; bge-m3 Vectorize + D1 graph + FTS5). `evidence_index`.
- **drugddx** — klinik-DDI boşluk-kapatıcı (`normalize_drug`/`interaction_label`; pairwise motor DEĞİL).
- **openfda** — yukarıda §3.3.
- **evidentia-kb** — `kb_search` semantik-recall takviyesi (opsiyonel, graceful-degrade).

### 3.7 Tam-metin + ikincil/koşullu
annas-reader (tam-metin tier 3, copyright-kapılı; çekirdeğin parçası, enrichment-kapılı DEĞİL) ·
PDF Viewer · NPI Registry (ABD PI/KOL) · **Mevzuat Bilgisi** (ikincil TR-mevzuat çapraz-kontrol;
kanun-no + bedesten) · **Elicit** (OAuth, ikincil sistematik-derleme/ekstraksiyon;
`search_papers`/`search_trials`/`create_report` — Consensus'a secondary).

---

## 4. Native-First merdiveni (her veri ihtiyacı için)

```
1) Native MCP tool        → varsa DAİMA bu (TİTCK, openfda, EPMC, AdisInsight, CT.gov…)
2) Native REST (bash+req) → native MCP yoksa (PubChem, DailyMed, DOAJ, J-STAGE, DrugBank)
3) BELGELENMİŞ BOŞLUK     → ikisi de yoksa "VERİ BULUNAMADI" + denenen sorgular
                            (web tier YOK → ASLA scrape/uydurma)
```

**Örnek merdivenler (`CONNECTORS.md §2`):**
- **ICD/kodlama:** `openfda.icd11_search` (ICD-11 birincil) → `nih-clinicaltables` (ICD-10) → boşluk.
- **İlaç normalizasyon:** `nlm-rxnorm` → `med-terminologies` → DailyMed REST.
- **Klinik DDI:** `drugddx` → DailyMed label DDI-bölümü (⚠️ "etkileşim verisi" olarak sunulMAZ).
- **Mekanizma/hedef:** ChEMBL → `iuphar-gtopdb` → OpenTargets(offline) → EPMC.
- **Epidemiyoloji:** **ABD:** PopHIVE + ICD-11. **TR:** TİTCK + EPMC `AFF:"Turkey"` + YÖK Tez.
  **Global yük:** native-API YOK → boşluk.

---

## 5. ÇALIŞMA AKIŞI — P0 → P7 (kalp)

### Adım 0 — Zorunlu yükleme
Her çağrıda ÖNCE şu **always-load** referanslar yüklenir (progressive disclosure bunlar için kapalı):
`knowledge-map.md` · `connector-registry.md` · `evidence-grading.md` · `output-templates.md` ·
`report-presentation.md` · `prisma-reporting.md`. Faz dosyaları (`prisma-protocol.md` [P0],
`search-strategy.md` [P1], `screening.md` [P3], `data-extraction.md` [P4], `risk-of-bias.md` [P5])
**faz-bazında** (progressive disclosure) yüklenir. Opsiyonel zenginleştirme modülleri yalnız
Adım 0.5 sinyaliyle.

### Adım 0.1 — Proje ayarları (varsa)
`.claude/evidentia.local.md` varsa okunur; frontmatter `known_connected`/`default_modules`/
`fulltext_tier`/`completeness_gate`/`auto_ingest_rag` alanları çalıştırmayı yönlendirir (hiçbiri
zorunlu-modül yapmaz — yalnız ipucu). Yoksa varsayılan: hiçbir zenginleştirme modülü aktif değil.

### Adım 0.4 — Semantic Scope Scan (zorunlu, 0.5'ten önce)
`knowledge-map.md` üzerinden soru **anlamca** taranır (anahtar-kelime değil):
1. Soru kavram kümesine ayrıştırılır (popülasyon/hastalık · müdahale/maruziyet · karşılaştırıcı ·
   sonuç · çalışma-tasarımı · coğrafya · kanıt-türü · tam-metin/KOL ihtiyacı).
2. Önce **FAZ dosyalarına** rota çizilir — her derleme aşağıdaki P0–P7 omurgasına eşlenir.
3. Sonra **opsiyonel zenginleştirme modülleri** haritalanır — knowledge-map Inverted Map'i ile;
   bunlar Adım 0.5 için **aday**dır, otomatik yükleme değil.
4. *(Opsiyonel booster)* `kb_search` erişilebilirse çağrılır, dönen bölümler kümeye eklenir.
5. `coverage_set` (fazlar + aday modüller) görünmez Ops sidecar'a yazılır — **denetlenebilir
   kapsam izi**.

### Adım 0.5 — Opsiyonel zenginleştirme sınıflandırıcısı (ZORUNLU DEĞİL)
> **Hiçbir zenginleştirme modülü zorunlu ya da her-zaman-açık değildir; çekirdek PRISMA hattı
> (P0–P7) konudan bağımsız her durumda çalışır.** Bu adım yalnız bağlam gerçekten gerektirdiğinde
> modül aktive eden bir tarama adımıdır. **Varsayılan inceleme yolu hiçbir alan katmanı
> yüklemez.**

Soru metni modül sözlüklerine karşı taranır (tam-kelime + kök). Bir sinyal **danışmandır**: modülü
aday olarak işaretler ve P2 çağrı listesine ek getirim **yalnızca inceleyici bağlamın gerçekten
gerektirdiğini onaylarsa** enjekte eder. Modüller bağımsızdır; birkaçı ya da hiçbiri ateşlenebilir.

| Opsiyonel modül | Temsili bağlam tetikleyicisi | Modül dosyası |
|---|---|---|
| Onkoloji | tümöre-özgü evreleme/yanıt kriterleri | `oncology-layer.md` |
| Hematoloji | heme malignite sınıflama/risk-stratifikasyonu | `hematology-layer.md` |
| Regülatuar | onay/etiket/regülatuar-kilometre taşı soruları | `regulatory-science-layer.md` (+`regulatory-intelligence.md`) |
| HTA / erişim | maliyet-etkinlik, ICER/QALY, geri-ödeme | `hta-layer.md` (+`regulatory-intelligence.md`) |
| Medical Affairs | MSL/KOL/danışma-kurulu/uyum çerçevesi | `medaffairs-ops-layer.md` |
| İmmünoloji | immün-aracılı hastalık sonuç/hedef özellikleri | `immunology-layer.md` |
| Nöroloji | nöro hastalık-modifiye edici/sonuç özellikleri | `neurology-layer.md` |
| Nadir Hastalık | orphan/doğal-seyir/registry-sonuç özellikleri | `rare-disease-layer.md` |
| Drug Intelligence | ilaç/MoA/hedef/pipeline/deal manzarası | `drug-intelligence-layer.md` |
| Türkiye-pazarı | TR geri-ödeme/SUT/native-registry bağlamı | `turkiye-layer.md` |
| Epidemiyoloji/Yük | insidans/prevalans/mortalite/hastalık yükü, ABD sürveyansı | `regulatory-intelligence.md` (ICD-11 via openfda; ABD via PopHIVE; global/TR = boşluk) |

**Sinyal yoksa:** saf PRISMA hattı yalnız akademik çekirdekle koşar — hiçbir modül yüklenmez.

### P0 — Protokol & PICO/PECO
Soruyu PICO/PECO (veya kapsam derlemesi için PCC) çerçevesine oturtur, derleme tipini
(sistematik/kapsam) belirler, uygunluk kriterlerini sabitler, protokol niyetini ön-kaydeder.
`references/prisma-protocol.md`.

### P1 — Arama Stratejisi
MeSH/Emtree + serbest-metin, Boolean yapı, veritabanı-başına çeviri, tarih/dil sınırları,
gri-literatür planı ile kapsamlı, tekrarlanabilir bir arama inşa eder. `references/search-strategy.md`.

### P2 — Getirim & Dedup
P1 stratejisini bibliyografik çekirdek üzerinden (native-MCP-first) yürütür, kayıtları
kimlikleriyle (PMID/DOI/NCT/…) yakalar, yinelenenleri temizler, PRISMA akış sayaçlarını kaydeder.
**Tek-sefer/kanonik-önbellek** sözleşmesine tabi. Opsiyonel zenginleştirme getirimi (Adım 0.5)
yalnız bir modül aktifse burada enjekte edilir.

### P3 — Tarama (Başlık/Özet → Tam-Metin)
Uygunluk kriterlerine karşı iki-aşamalı tarama; dahil/hariç gerekçeleriyle kaydedilir; çakışmalar
çözülür. `references/screening.md`. **İnsan-onay kapısı:** dahil/hariç seti ve dışlama
gerekçeleri, P4'e geçmeden önce inceleyici onayına sunulur.

### P4 — Veri Çıkarımı
Çalışma özellikleri + sayısal sonuçları (etki tahmini, GA, p, alt-grup, yan-etki) yapılandırılmış
çıkarım tablosuna işler; özet yetersizse copyright-kapılı tam-metin kademesiyle zenginleştirir.
`references/data-extraction.md`. Opsiyonel ilaç/terminoloji modülü aktifse Extended-Tier
reçeteleri (§3.5) burada ateşlenir — her biri bir çapraz-doğrulama kapısıyla biter.

### P5 — Yanlılık Riski
Tasarıma uygun aracı uygular: **RoB2** (RKÇ), **ROBINS-I** (randomize-olmayan), **QUADAS-2**
(tanısal doğruluk), **Newcastle-Ottawa** (gözlemsel), **PROBAST** (prediksiyon modeli).
`references/risk-of-bias.md`. **İnsan-onay kapısı:** çalışma-bazlı RoB yargıları (+ alan
gerekçesi), GRADE'e geçmeden önce inceleyici onayına sunulur.

### P6 — GRADE Kesinlik
Sonuç-bazlı kanıt kesinliğini derecelendirir (GRADE / Tier 0–6), gerekçeli düşür/yükseltme
uygular. `references/evidence-grading.md`.

### P7 — PRISMA Raporlama
PRISMA 2020 akış diyagramını, Summary-of-Findings tablosunu ve PRISMA/PRISMA-ScR kontrol
listesini derler; temiz-kopya Türkçe raporu üretir. `references/prisma-reporting.md`
(+ `output-templates.md`, `report-presentation.md`).

### Çoklu-Kaynak Getirim (P2 native-first merdiveni)
Her ihtiyaç **Native-First merdiveniyle** çözülür (native MCP → Python REST → belgelenmiş boşluk;
**web tier yok**). **A. Akademik Çekirdek** (PubMed/EPMC, bioRxiv, CT.gov, Consensus, Scholar
Gateway, Paper Search, YÖK Tez, OpenAlex, Semantic Scholar, PubMed-EPMC). **B. Extended** (ChEMBL,
EPMC SR-filtresi, REST fallback, native openFDA + Extended Tier-K reçeteleri — modül-kapılı,
her biri çapraz-doğrulama kapısıyla biter). **C. Multi-Country AFF** — `for ülke in [Turkey,
China, Japan, Germany, Brazil, Korea]: EPMC AFF:"{ülke}"` (coğrafi genişlik önemliyse). **D.
Türkiye-pazarı** (TR bağlamı/modülü aktifken) — TİTCK + Mevzuat + YÖK Tez + EPMC AFF:"Turkey".
**E. Kılavuzlar & HTA/Epidemiyoloji** — native-API'siz kaynak = belgelenmiş boşluk (web-scrape
yok); ICD-11 openfda ile, ABD sürveyansı PopHIVE ile. **Tam-metin** (özet yetersizse) — EPMC
`get_full_text_article` → `get_copyright_status` → Paper Search → annas-reader → Wiley →
pubmed-epmc Unpaywall (son çare).

### Adım 2 — Cömertlik İlkesi (UNCAPPED — tüm fazlarda)
Çağrı sayısı/derinlik sınırlanmaz; varsayılan = **maksimum derinlik**, P0'dan P7'ye kadar tüm
fazlara yayılır. Minimum getirim derinlikleri korunur (PubMed ≥2 sorgu×25, EPMC ×2, 6-ülke AFF,
CT.gov ×2, Türkiye native aktifken). Aktif zenginleştirme modülleri derinliği **artırır**, asla
azaltmaz. Telemetri (Cömertlik Garantisi) görünmez Ops annex'ine yazılır.

### Adım 3 — Çıktı Sözleşmesi
Okur-yüzü yapı ve bölüm iskeleti `references/output-templates.md`'de yaşar (SR/ScR **①–⑧**
yapısı, adaptif formatlar, `.data.json` sidecar) — artık dokümanda satır-içi §1–21 iskeleti YOK.
Kural: derleme tipinin gerektirdiği her eleman mevcuttur; eksik veri = "VERİ BULUNAMADI" (asla
sessizce atlanmaz). Detay: §8.

### Adım 5 — Temiz-Kopya Sunum Doktrini
Araştırma derinliği (P0–P7) değişmez; bu, **okurun aldığı formu** yönetir. Her dosya-tabanlı
rapor **dergi-düzeyi Türkçe temiz kopya**ya dönüşür: tam cümleler + akademik üslup + açık
Vancouver atıfları (PMID/DOI/NCT + erişim tarihi) + yönetici özeti + kanıt-düzeyi etiketleri +
kısaltma dizini + okur-yüzü Yöntem/Kısıtlar + PRISMA akış diyagramı + Summary-of-Findings.
**Anti-leakage:** connector/araç adları, fonksiyon imzaları, faz/modül kodları (`0.5.I`/`P4`),
çağrı sayıları → okur gövdesinden YASAK; tümü `<!-- OPS: … -->` annex'ine taşınır.
Görselleştirme yönergeleri yalnız `<!-- VIZ: … -->` yorumlarında. Bitiriş kapısı **G1–G7**
(`report-presentation.md`).

### Completeness Gate (ZORUNLU — bitirmeden hemen önce)
`knowledge-map.md` soruya ve yapılan işe karşı yeniden taranır: "Bu soruyla ilgili danışılmamış
bir faz/bölüm/connector var mı?" Boşluk listesi Ops sidecar'a yazılır; boş değilse her boşluk
yüklenip giderilir, yeniden kontrol edilir. Yalnız boşluk listesi boşken bitirilir — kapsamı
deterministik ve tekrarlanabilir kılar.

---

## 6. Tek-Sefer / Kanonik Önbellek Disiplini
`shared/canonical-cache-contract.md`: bir veri **bir kez** çekilir, bir **kanonik artefakta** yazılır,
sonraki adımlar oradan **okur**. Çift connector sorgusu engellenir.

| Kanonik artefakt | İlk çeken | Okuyanlar |
|---|---|---|
| `evidence_corpus` | İlk akademik tarama (P2) | P4 çıkarım, P6 sentez, tam-metin |
| `titck_record` | İlk TİTCK get_drug | fiyat, biyobenzer, off-label, regülatuar modülü |
| `regulatory_snapshot` | İlk openfda + **PopHIVE** | epidemiyoloji modülü, güvenlik, kodlama |
| `terminology_map` | İlk Extended Tier-K | normalizasyon, cross-country eşleme |
| `kol_graph` | İlk OpenAlex/S2/EPMC yazar | KOL haritası (`/evidentia-kol`), ağ |
| `evidence_index` | İlk anamnesis ingest | P4/P6 sentez, tam-metin — **indeks, ham metin değil** |

**Tekil kurallar:** TİTCK tek-sefer (barcode bir kez) · openfda tekil+1retry+skippable · PopHIVE
US-only + birebir-aktar · Tier-K ilk-liveness-sonrası yeniden-probe yok.

---

## 7. RAG/GraphRAG — retrieve-don't-dump (anamnesis)
Tam-metin makale/kitap veya büyük araç çıktısı **ASLA ham olarak bağlam penceresine dökülmez**.
Bir `doc_id` (DOI) **bir kez** `ingest_document` ile indekslenir (semantik chunk + bge-m3 embed + D1
graph). Sonraki sorgular `semantic_search`/`hybrid_query` ile **sınırlı, provenance-damgalı** dilim
çeker. Karmaşık soru alt-yönlere bölünür → `queries[]` → vektör∥BM25 → RRF füzyon → cross-encoder
rerank → top-k (recall-maks, "hiçbir detayı atlamama"). **Boş-korpus guard'ı:** `semantic_search`
öncesi `corpus_stats` zorunlu; 0 hit "kanıt yok" DEĞİLDİR (önce ingest et). `/evidentia-synthesize`
komutu bu substratı P4+P6 sentezi için kullanır. Bağlam-penceresi taşmasını önleyen çekirdek
disiplin.

---

## 8. Çıktı — ①–⑧ SR/ScR iskeleti + sidecar + temiz-kopya
- **İç iskele (①–⑧, `output-templates.md` §1):** ① Arka Plan · ② Amaç + PICO/PECO + Derleme Tipi ·
  ③ Yöntem (③.1 uygunluk … ③.9 veri kesim tarihi) · ④ PRISMA Akış Diyagramı · ⑤ Bulgular (⑤.1
  çalışma özellikleri, ⑤.2 RoB özeti, ⑤.3 sonuç-bazlı bulgular) · ⑥ Summary-of-Findings/GRADE ·
  ⑦ Tartışma/Kısıtlılıklar/Sonuç · ⑧ Kaynaklar + Dahil/Dışlanan Listeleri. Numaralı alt-etiketler
  (③.1…, ⑤.1…) yazar-içi navigasyon yardımıdır; okur temiz-kopyada doğal-dil başlıkları görür.
- **Opsiyonel-modül ekleri:** bir zenginleştirme modülü ateşlenirse, çıktısı ⑧'den **sonra**
  ayrı-başlıklı bir ek olarak eklenir (ör. "Ek A — İlaç İstihbaratı ve Ticari Görünüm"); çekirdek
  ①–⑧ hiçbir zaman opsiyonel içerikle karıştırılmaz — PRISMA-uygunluk korunur.
- **Okur yüzü:** temiz-kopya rapor (Adım 5; sızıntı yok).
- **`.data.json` sidecar (v9 PRISMA union şeması):** `prisma_flow_counts` + `eligibility_criteria`
  + `search_strategy` + `screening_log` + `evidence_table` + `rob_assessments` + GRADE/SoF +
  opsiyonel-modül payload'ları (`turkey_access_summary`, `epidemiology_payload`,
  `pipeline_payload`, …) + `sources_summary`. Tüketiciler: carbon-html-report / carbon-pptx /
  pharmaintel / pharmapatent / onko-erisim / saglik-sigorta.

---

## 9. Komutlar + alt-ajan + start
| Yüzey | Ne yapar |
|---|---|
| `/evidentia` | Uçtan uca P0→P7 koşumu (herhangi bir tıbbi araştırma sorusu; kanonik artefaktları üretir). |
| `/evidentia-protocol` | P0–P1: soru-tipi sınıflama, PICO/PECO + uygunluk kriterleri, veritabanı-başına MeSH/Emtree arama stratejisi. |
| `/evidentia-fulltext` | Copyright-kapılı tam-metin kademesi (EPMC→Paper Search→annas-mcp→Wiley→Unpaywall). |
| `/evidentia-synthesize` | P4+P6: `evidence-synthesizer` alt-ajanını çağırır (anamnesis RAG/GraphRAG, ağır fan-out izolasyonu). |
| `/evidentia-appraise` | P5–P6: verilen çalışma setine tasarıma-göre RoB2/ROBINS-I/QUADAS-2/Newcastle-Ottawa/PROBAST uygular, sonuç-bazlı GRADE + SoF üretir. |
| `/evidentia-kol` | KOL haritası — **opsiyonel zenginleştirme modülü**; yalnız KOL/uzman-ağı bağlamlı sorularda (OpenAlex → S2 → EPMC → NPI → YÖK Akademik). |
| `/evidentia-connectors` | Preflight + roster tazeleme + **canlı G-PROBE** (initialize handshake; hatırlamaz). |
| `start` skill | Oryantasyon + connector preflight (yüzey-bilinçli) + doğru komuta yönlendirme. |

**Alt-ajan (`evidence-synthesizer`):** ≥3 opsiyonel modül **veya** 6-ülke AFF **veya** tam-metin
korpus **veya** KOL ağı içeren koşumlarda; onlarca connector çağrısının ham gürültüsünü **kendi**
bağlamında tüketir, ana pencereye **yalnız damıtılmış kanonik artefaktları + numaralı sentezi**
döner.

---

## 10. Doğrulama Kapıları

**Skill-düzeyi (12 otomatik kapı — `skills/medical-research/evals/check_integrity.py`):**

| Gate | Ne denetler |
|---|---|
| **G-REF** | SKILL.md'nin andığı her `references/*.md` diskte var (mount-toleranslı) |
| **G-CONN** | connector-registry'deki her connector manifest runtime'da çözülür |
| **G-ALWAYS** | 6 always-load dosyası mevcut |
| **G-VERSION** | Sürüm üçlüsü hizalı (SKILL fm + H1 + manifest skill/build = 9.0.0) |
| **G-COVERAGE** | knowledge-map tüm korpusu + fazları + opsiyonel modülleri kapsıyor, dangling yok |
| **G-PROBE** | Her first-class Extended Tier-K/O connector'ın §8 Probe Log'da **WIRE tablo-satırı** var |
| **G-XVAL** | Her Extended-Tier reçetesi bir çapraz-doğrulama kapısı taşıyor |
| **G-WHITELIST** | §2.6 whitelist'inde hiç pipeworx-jenerik araç yok (en-az-yetki) |
| **G-SIZE** | SKILL.md gövdesi < 500 satır |
| **G-DESC** | Skill açıklaması genel PRISMA tetikleyicileri taşıyor, ticari-önyargı yok |
| **G-PHASES** | SKILL.md P0…P7'nin tamamını tanımlıyor, her faz kendi referans dosyasına işaret ediyor |
| **G-DESKEW** | Varsayılan yolda hiçbir alan/zenginleştirme modülü zorunlu yüklenmiyor (de-skew değişmezi) |

**+ `G-RAG`** (çıktı faithfulness, `evals/rag_quality.py`, ayrı betik) **+ nitel** `G-COPYRIGHT`
(tam-metin no-verbatim-bulk) / `G-REGRESSION` (regresyon sorguları doğru faz+modüle eşliyor) —
`skill-manifest.yaml verification` içinde deklare edilir. **Plugin-düzeyinde** ayrıca: canlı
`G-PROBE` (`.mcp.json` URL'lerinde `scripts/g_probe.py` initialize handshake), `G-BUNDLE`
(`.mcp.json` ↔ `CONNECTORS.md` tutarlılığı, `scripts/g_bundle.py`), `G-TRUST` (3P-untrusted güven
duruşu), `G-SURFACE` (claude.ai ⇄ Claude Code yüzey ayrımı).

Koşum: `python3 skills/medical-research/evals/check_integrity.py` (12 skill-gate; `ALL RUN GATES
PASSED` beklenir) + `rag_quality.py` (G-RAG) + `scripts/g_probe.py`/`scripts/g_bundle.py`
(plugin-gate).

---

## 11. Uçtan uca örnek koşum
**Soru:** *"Tisagenlecleucel 3L DLBCL — global kanıt + NICE maliyet-etkinliği + Türkiye erişim + ABD epidemiyoloji."*

1. **Adım 0/0.4:** always-load yüklenir; kavramlar {CAR-T, DLBCL, HTA/ICER, TR-erişim, ABD-epi} →
   `coverage_set` = {P0–P7 omurgası} + aday opsiyonel modüller {Hematoloji, HTA, Epidemiyoloji,
   Türkiye-pazarı}.
2. **Adım 0.5:** heme + HTA + epidemiyoloji + Türkiye-pazarı modülleri sinyalle ateşlenir; ilgili
   katman dosyaları yüklenir, P2 çağrı listesine ek getirim enjekte edilir.
3. **P0–P1:** PICO çerçevesi (P: 3L DLBCL, I: tisagenlecleucel, C: standart bakım, O: yanıt/OS) +
   MeSH/Emtree arama stratejisi.
4. **P2 Getirim:** PubMed/EPMC/CT.gov/Consensus/OpenAlex… → JULIET çalışması (NEJM,
   NCT02445248); 6-ülke AFF döngüsü; TİTCK (TR ruhsat/fiyat) + Mevzuat (SUT) — `titck_record` bir
   kez; HTA modülü: NICE/ICER PDF = **belgelenmiş boşluk** (web-scrape yok) → AdisInsight history +
   EPMC HTA literatürü; epidemiyoloji modülü: **PopHIVE** ABD lenfoma aktivitesi (varsa) — birebir
   aktar; global/TR yük = boşluk (TR → EPMC AFF:Turkey + YÖK Tez).
5. **P3 Tarama:** başlık/özet → tam-metin iki-aşamalı tarama; dahil/hariç seti **inceleyici
   onayına** sunulur.
6. **P4 Veri Çıkarımı:** JULIET → anamnesis ingest → `hybrid_query` (recall-maks); yapılandırılmış
   çıkarım tablosu.
7. **P5 Yanlılık Riski:** RoB2/ROBINS-I (tasarıma göre) uygulanır; RoB yargıları **inceleyici
   onayına** sunulur.
8. **P6 GRADE:** sonuç-bazlı kesinlik derecelendirmesi.
9. **P7 + Adım 5:** PRISMA akış diyagramı + SoF; dergi-düzeyi Türkçe temiz kopya; Vancouver
   atıfları; HTA boşluğu **görünür** (sessiz atlama yok); faz/modül kodları `<!-- OPS -->`'a.
10. **①–⑧ + Ek'ler:** çekirdek ①–⑧ + "Ek A — Türkiye Erişim Özeti (native TİTCK)" + "Ek B — HTA/
    Maliyet-Etkinlik (ICER boşluk-notlu)" + "Ek C — ABD Epidemiyolojisi (PopHIVE)".
11. **Sidecar:** `evidence_table`/`rob_assessments`/GRADE-SoF + `epidemiology_payload` (PopHIVE
    US + ICD-11; TR boşluk) + `turkey_access_summary` (native TİTCK) + `hta_table` (ICER
    boşluk-notlu).

---

## 12. Sürümleme + iki-kopya senkron (operasyonel)
- **Sürüm:** plugin (`2.x`) ≠ flagship skill (`9.x`). Şu an plugin **2.0.0** / skill **9.0.0** /
  12 skill-gate + G-RAG + plugin-düzeyi G-BUNDLE/G-TRUST/G-SURFACE. G-VERSION üçlüsü: SKILL fm +
  H1 + manifest skill/build.
- **v9.0.0 headline:** zorunlu 10-eksen alan matrisi, uçtan uca **PRISMA 2020/PRISMA-ScR P0–P7
  hattı** ile değiştirildi; eski eksenler silinmedi — **opsiyonel, bağlam-tetiklemeli
  zenginleştirme modüllerine** dönüştürüldü (Adım 0.5, de-skew invariant, ADR-05-safe).
- **İki kopya:** `evidentia-cc/` (git'siz build/deploy workspace) ↔ `CureoPrivate/plugins/evidentia/`
  (kanonik, git-izli katalog). Düzenle cc → aynala CP → commit **yalnız CP** (main). Self-host
  worker'ları `evidentia-cc/self-host/`'tan wrangler ile ayrı deploy edilir.

---

*Kaynaklar: `skills/medical-research/SKILL.md` (Adım 0/0.4/0.5 + P0–P7 + Version History) ·
`../CONNECTORS.md` (roster + §2 merdivenler + §8 D-kayıtları + §9 adjudication) ·
`skills/medical-research/references/connector-registry.md` (§2.6 Extended Tier-K + §8 Probe Log) ·
`skills/medical-research/references/output-templates.md` (①–⑧ iskelet + sidecar) ·
`skills/medical-research/references/prisma-reporting.md` (PRISMA akış + SoF) ·
`shared/canonical-cache-contract.md` (tek-sefer) · `evals/check_integrity.py` (kapılar). Çakışmada bu
otoriter dosyalar üstündür.*
