# Uluslararası Karşılaştırmalı Sağlık Mevzuatı Kaynak Kataloğu

Bu dosya, Lex-Sanitas protokolünün **Bölüm 5.4 (Uluslararası Kaynak Katmanı)** reçetesinin operasyonel sözlüğüdür. Her kaynak için **(a) kurum/ veri tabanı tanımı, (b) URL örüntüsü, (c) erişim modalitesi, (d) Lex-Sanitas modu eşlemesi, (e) tipik sorgu reçetesi** verilmiştir.

> **Genel kural:** Türkiye dışındaki sağlık mevzuatı için **hesap havuzunuzda dedicated MCP bulunmamaktadır.** Tüm çağrılar üç genel-amaçlı MCP üzerinden orkestre edilir: **Tavily** (gezinme + sentez), **Exa** (neural search), **Fetch** (sabit URL ham erişim). Bilgi sınırı sonrası güncel sürümler için Fetch ile resmi sayfa doğrulaması zorunludur.

---

## 0. Cross-Reference Index — Lex-Sanitas v2.0

Bu dosya **AB + ABD + ICH/PIC/S/IMDRF + HTA** boyutlarında **hızlı erişim** kataloğudur. Daha **derinleşmiş** referans için:

| Konu Alanı | Derinleşmiş Referans Dosyası |
|------------|------------------------------|
| **BM Sistemi + İnsan Hakları Sözleşmeleri (ICESCR, CRC, CEDAW, CRPD)** | `references/10-bm-uluslararasi-saglik-hukuku.md` |
| **Avrupa Konseyi (Oviedo) + AİHS Sağlık Maddeleri** | `references/10-bm-uluslararasi-saglik-hukuku.md` (Bölüm 4) |
| **Helsinki Bildirgesi 2024 + CIOMS Rehberleri** | `references/10-bm-uluslararasi-saglik-hukuku.md` (Bölüm 5-6) |
| **BM Narkotik Üçlü Sözleşmesi + INCB** | `references/10-bm-uluslararasi-saglik-hukuku.md` (Bölüm 3) |
| **WHO derinlemesine — IHR 2005, Pandemic Agreement, FCTC, EML, ICD-11, PQ, WLA, ATC/DDD, Guidelines, Position Papers, BTS, EURO, Codex** | `references/11-who-derinlemesine-rejim.md` |
| **Japonya (PMDA), Kore (MFDS), Singapur (HSA + ACCESS Consortium), Çin (NMPA), Hindistan (CDSCO), Avustralya (TGA + PBAC), Yeni Zelanda (PHARMAC), İskandinav (DKMA/MPA/DMP/Fimea + FINOSE), İrlanda (HPRA), Belçika (KCE), Hollanda (ZIN), İspanya (AEMPS), İtalya (AIFA), Brezilya (ANVISA), Meksika (COFEPRIS), İsrail (MOH + Sal Briut), UAE/Suudi (DOH + SFDA), Endonezya (BPOM), Pakistan (DRAP)** | `references/12-gelismis-ulke-rejimleri-derin.md` |
| **Reliance + Hızlı Onay Programları karşılaştırma matrisi** | `references/12-gelismis-ulke-rejimleri-derin.md` (Bölüm 6) |
| **HTA + Geri Ödeme Modelleri karşılaştırma** | `references/12-gelismis-ulke-rejimleri-derin.md` (Bölüm 7) |
| **Türk Yüksek Yargı + AİHM + ABAD içtihat erişimi (Hukuki Veritabanları MCP) ve Türk akademik doktrin (YokTez MCP)** | `references/13-icthat-doktrin-akademik-katman.md` |
| **Uluslararası antlaşma + yargı kararı atıf formatları** | `references/03-atif-teknigi.md` (Bölüm 11-12) |
| **Türk hukuk dili + üslubu + tabaka seçimi** | `references/09-turk-hukuk-dili-ve-uslubu.md` |

**Operasyonel akış:** Türk taslağı için **uluslararası karşılaştırma** gerektiğinde, **birinci durakla** bu dosya (R8) — AB/FDA/ICH; **derinleşme** gerektiğinde yukarıdaki tablodaki ilgili dosyaya geçilir. Yargı içtihat + doktrinal temellendirme gerektiğinde **R13** zorunlu.

---

## 1. Süpranasyonal / Bölgesel Düzlem — AB Müktesebatı

### 1.1. EUR-Lex (eur-lex.europa.eu)

**Tanım:** AB'nin tek resmi mevzuat veri tabanı. CELEX numarası sistemiyle (örn. `32017R0745` = 2017 yılı, R = Regulation, 0745 = numarası) her belge benzersiz adreslenir.

**URL örüntüleri:**

| Senaryo | URL Şablonu |
|---------|-------------|
| Düzenleme tam metni (orijinal) | `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:[CELEX]` |
| Konsolide sürüm | `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:0[CELEX]-[YYYYMMDD]` |
| HTML görünüm | `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:[CELEX]` |
| PDF | `https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:[CELEX]` |
| Çok dilli (Türkçe çeviri çoğu zaman yok) | `?uri=CELEX:[CELEX]&from=EN` parametresi |
| SPARQL endpoint | `https://publications.europa.eu/webapi/rdf/sparql` |
| Web Service API (kayıtla) | `https://eur-lex.europa.eu/EURLexWebService` |

**Sağlık alanı kritik CELEX referansları:**

| CELEX | Düzenleme |
|-------|-----------|
| `32004R0726` | Regulation (EC) No 726/2004 — EMA kuruluş ve merkezî ruhsat |
| `32001L0083` | Directive 2001/83/EC — Beşeri Tıbbi Ürünler Kodifikasyonu (Türk Ruhsatlandırma Yönetmeliği'nin AB referansı) |
| `32017R0745` | Regulation (EU) 2017/745 — MDR (Tıbbi Cihaz) |
| `32017R0746` | Regulation (EU) 2017/746 — IVDR (İn Vitro Tanı Cihazları) |
| `32014R0536` | Regulation (EU) 536/2014 — CTR (Klinik Araştırma) |
| `32016R0679` | Regulation (EU) 2016/679 — GDPR |
| `32011L0062` | Directive 2011/62/EU — Falsified Medicines (sahte ilaçlarla mücadele) |
| `32021R2282` | Regulation (EU) 2021/2282 — HTA Regulation (Joint Clinical Assessment) |
| `32019R0006` | Regulation (EU) 2019/6 — Veteriner Tıbbi Ürünler |
| `32021R0241` | Regulation (EU) 2021/241 — Recovery & Resilience Facility (sağlık yatırımları) |

**Lex-Sanitas modu eşlemesi:** DRAFT (Adım 5), ANALYZE (Adım 4), OPINE (Adım 3 — AB Başkanlığı), RIA (Adım 4).

**Tipik sorgu reçetesi:**
```
Fetch → https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0745
   → MDR tam metnini çek (konsolide sürüm için tarih damgalı versiyon)
Tavily → site:eur-lex.europa.eu "medical device" guidance
   → MDCG referanslarını topla
```

### 1.2. EMA — European Medicines Agency (ema.europa.eu)

**Tanım:** Avrupa İlaç Ajansı; merkezî ruhsat prosedürünü yürütür. Mevzuat-altı düzlemde son derece zengin açık veri sunar.

**Alt kaynaklar:**

| Kaynak | URL |
|--------|-----|
| EPAR (European Public Assessment Report) | `https://www.ema.europa.eu/en/medicines` |
| CTIS (Clinical Trials Information System) | `https://euclinicaltrials.eu` |
| EudraVigilance Public Data | `https://www.adrreports.eu` |
| EMA Scientific Guidelines (CHMP) | `https://www.ema.europa.eu/en/human-regulatory-overview/research-development/scientific-guidelines` |
| Open Data Portal | `https://www.ema.europa.eu/en/about-us/how-we-work/access-information/open-data` |
| Q&A and Reflection Papers | `https://www.ema.europa.eu/en/documents` |

**Lex-Sanitas modu eşlemesi:** DRAFT (bilimsel temellendirme), RIA (klinik benchmark), OPINE (TİTCK görüşünde EMA paralelinin gösterilmesi).

### 1.3. EUDAMED (ec.europa.eu/tools/eudamed)

**Tanım:** MDR ve IVDR kapsamında AB tıbbi cihaz veri tabanı. Türkiye'deki ÜTS'nin AB modelidir.

**Modüller:** Aktör kaydı, UDI-DI/UDI-PI, Sertifika ve Notified Body, Klinik Araştırma, Vigilance, Market Surveillance. Modüller kademeli olarak açılıyor.

**Lex-Sanitas modu eşlemesi:** DRAFT (cihaz yönetmeliği taslakları için), RIA (ÜTS karşılaştırması).

### 1.4. HMA — Heads of Medicines Agencies (hma.eu)

**Tanım:** Ulusal yetkili otoritelerin koordinasyon platformu. CMDh (Coordination Group for Mutual Recognition and Decentralised Procedures) ve CMDv (veteriner) kararları burada.

**Lex-Sanitas modu eşlemesi:** ANALYZE (ruhsat prosedürü uyumu), OPINE (TİTCK ruhsat süreçleri ile karşılaştırma).

### 1.5. N-Lex (eur-lex.europa.eu/n-lex)

**Tanım:** AB üye devletlerinin **ulusal** mevzuat veri tabanlarına tek pencereden erişim portalı.

**Kullanım:** Her ülke için ulusal Resmî Gazete benzeri kaynağa yönlendirir; karşılaştırmalı çalışmalarda başlangıç noktası.

### 1.6. EU HTA Coordination Group (hta.europa.eu)

**Tanım:** Regulation (EU) 2021/2282 (HTA Regulation) uyarınca Joint Clinical Assessment (JCA) sorumlu organ. Ocak 2025'ten itibaren onkoloji + ATMP, ileride yetim ilaçlar.

**Lex-Sanitas modu eşlemesi:** RIA (SUT geri ödeme tebliği taslaklarında JCA çıktısının doğrudan kullanımı), OPINE (SGK görüşünde JCA referansı).

> *Karşılaştırmalı HTA model analizi: R12 §7 (NICE/CADTH/PBAC/IQWiG/HAS/ICER + SGK SUT entegre karşılaştırma tablosu).*

---

## 2. Ulusal Düzlem — Karşılaştırma için Öncelikli Yedi Yargı Bölgesi

> **Cross-Reference:** Bu bölüm AB üye devletleri (Almanya, Fransa) + UK + İsviçre + ABD + Kanada + Avustralya için **hızlı erişim** sunar. **Asya-Pasifik (Japonya PMDA, Kore MFDS, Singapur HSA + ACCESS, Çin NMPA, Hindistan CDSCO)**, **diğer Avrupa (İskandinav, İrlanda, Belçika, Hollanda, İspanya, İtalya)**, **Latin Amerika (Brezilya ANVISA, Meksika COFEPRIS)**, **Orta Doğu (İsrail, Suudi SFDA, UAE)** için **`references/12-gelismis-ulke-rejimleri-derin.md`** açılır.

### 2.1. Almanya — Gesetze im Internet (gesetze-im-internet.de)

**Tanım:** Federal Adalet Bakanlığı işletimi; tüm federal kanun ve yönetmeliklere erişim.

**Erişim:** HTML + XML açık erişim; bulk indirme mümkün.

**Sağlık alanında kritik metinler:**

| Kısaltma | Açılım | URL |
|----------|--------|-----|
| AMG | Arzneimittelgesetz (İlaç Kanunu) | `https://www.gesetze-im-internet.de/amg_1976/` |
| MPDG | Medizinprodukterecht-Durchführungsgesetz (MDR Uygulama Kanunu) | `https://www.gesetze-im-internet.de/mpdg/` |
| MPG | Medizinproduktegesetz (eski; MPDG ile değişti) | `https://www.gesetze-im-internet.de/mpg/` |
| SGB V | Sozialgesetzbuch V (Sağlık sigortası — § 35a AMNOG değerlendirmesi) | `https://www.gesetze-im-internet.de/sgb_5/` |
| ApoG | Apothekengesetz (Eczacılık Kanunu) | `https://www.gesetze-im-internet.de/apog/` |
| TPG | Transplantationsgesetz (Organ Nakli Kanunu) | `https://www.gesetze-im-internet.de/tpg/` |

**Regülatörler:**
- **BfArM** (`bfarm.de`) — Federal İlaç ve Tıbbi Cihaz Enstitüsü
- **PEI** (`pei.de`) — Paul-Ehrlich-Institut (biyolojik ürünler, aşılar)
- **G-BA** (`g-ba.de`) — Gemeinsamer Bundesausschuss (HTA + reimbursement)
- **IQWiG** (`iqwig.de`) — Institut für Qualität und Wirtschaftlichkeit (HTA değerlendirme)

**Lex-Sanitas modu eşlemesi:** DRAFT, ANALYZE, RIA (AB üye devleti karşılaştırması için varsayılan ilk seçim).

### 2.2. Fransa — Légifrance (legifrance.gouv.fr)

**Tanım:** Fransız hukukunun tek resmi platformu. PISTE/DILA üzerinden Open API.

**Sağlık alanında kritik metin:**

| Kod | Açılım | URL örüntüsü |
|-----|--------|--------------|
| CSP | Code de la Santé Publique | `https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006072665` |
| CSS | Code de la Sécurité Sociale (geri ödeme) | `https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006073189` |
| Code de la Recherche | Araştırma Kanunu (insan deneyi) | (Légifrance kod arama) |

**Regülatörler:**
- **ANSM** (`ansm.sante.fr`) — Agence Nationale de Sécurité du Médicament
- **HAS** (`has-sante.fr`) — Haute Autorité de Santé (HTA — *avis de la Commission de la Transparence*)
- **CNIL** (`cnil.fr`) — KVKK eşdeğeri

**API:** Légifrance Open API (DILA) — kayıtla ücretsiz; programatik tam metin erişimi.

**Lex-Sanitas modu eşlemesi:** DRAFT, RIA (AB üye devleti karşılaştırması ikincil varsayılan).

### 2.3. Birleşik Krallık — legislation.gov.uk

**Tanım:** The National Archives işletimi. **Açık REST API** (anahtarsız) — sağlık mevzuatı için en kullanışlı API'lerden biri.

**Erişim örüntüsü:**
```
https://www.legislation.gov.uk/services/data.feed?type=ukpga&year=2014
   → Acts of Parliament listesi
https://www.legislation.gov.uk/[type]/[year]/[number]/data.xml
   → Yapısal XML
```

**Sağlık alanında kritik metinler:**

| Metin | URL örüntüsü |
|-------|--------------|
| Medicines Act 1968 | `/ukpga/1968/67` |
| Human Medicines Regulations 2012 | `/uksi/2012/1916` |
| Medical Devices Regulations 2002 (UK MDR — Brexit sonrası revize) | `/uksi/2002/618` |
| National Health Service Act 2006 | `/ukpga/2006/41` |
| Health and Care Act 2022 | `/ukpga/2022/31` |

**Regülatörler:**
- **MHRA** (`gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency`)
- **NICE** (`nice.org.uk`) — National Institute for Health and Care Excellence (HTA)
- **NHSE** (`england.nhs.uk`) — geri ödeme prosedürleri

**NICE Evidence Search:** `https://www.nice.org.uk/guidance` + arama API'si (rate-limited).

**Lex-Sanitas modu eşlemesi:** Tüm modlar; Brexit sonrası UK MDR Türkiye için kritik referans (AB-dışı ama gelişmiş, AB ile yapısal benzerlik).

### 2.4. İtalya — Normattiva (normattiva.it)

**Tanım:** Cumhurbaşkanlığı'na bağlı resmi mevzuat portalı. Tam metin arama + tarihsel sürüm karşılaştırması.

**Resmî Gazete eşdeğeri:** Gazzetta Ufficiale — `gazzettaufficiale.it`.

**Regülatör:** **AIFA** (`aifa.gov.it`) — Agenzia Italiana del Farmaco.

**Lex-Sanitas modu eşlemesi:** RIA üçüncü AB üye devleti karşılaştırması.

### 2.5. İspanya — BOE (boe.es)

**Tanım:** Boletín Oficial del Estado — İspanyol Resmî Gazetesi + mevzuat veri tabanı. **REST + SPARQL Linked Open Data** ile programatik erişim.

**Regülatör:** **AEMPS** (`aemps.gob.es`) — Agencia Española de Medicamentos y Productos Sanitarios.

**Lex-Sanitas modu eşlemesi:** Güney Avrupa karşılaştırması; pediatrik düzenleme ve generik politika için referans.

### 2.6. İsviçre — Fedlex (fedlex.admin.ch)

**Tanım:** Resmi konfederasyon mevzuatı. AB üyesi değildir ama EMA ile bilateral anlaşmalar üzerinden hizalanır. **Açık API + RDF/XML bulk** erişimi.

**Sağlık alanında kritik metinler:**

| Kısaltma | Açılım |
|----------|--------|
| HMG | Heilmittelgesetz / LPTh / LATer (İlaç ve Tıbbi Cihaz Kanunu) |
| KVG | Krankenversicherungsgesetz (Sağlık Sigortası) |
| BetmG | Betäubungsmittelgesetz (Narkotik Maddeler) |

**Regülatör:** **Swissmedic** (`swissmedic.ch`).

**Lex-Sanitas modu eşlemesi:** **Yapısal benchmark olarak özellikle önemli** — Türkiye'nin AB-dışı ama AB-uyumlu pozisyonuyla en yakın paraleli İsviçre'dir.

### 2.7. Hollanda — wetten.overheid.nl

**Regülatör:** **CBG-MEB** (`cbg-meb.nl`) — College ter Beoordeling van Geneesmiddelen. EMA'nın merkezi Amsterdam'da olduğu için Hollanda önemli karşılaştırma noktasıdır.

---

## 3. Amerika Birleşik Devletleri — Federal Düzey

### 3.1. eCFR — Electronic Code of Federal Regulations (ecfr.gov)

**Tanım:** Tüm federal regülasyonların güncel resmi sürümü. **Tam REST API**.

**API endpoint:**
```
https://www.ecfr.gov/api/versioner/v1/full/[date]/title-[N].xml
https://www.ecfr.gov/api/structure/v1/[date]/title-[N]
```

**Sağlık için kritik Title'lar:**

| Title | İçerik | URL |
|-------|--------|-----|
| Title 21 | Food and Drugs (FDA) | `https://www.ecfr.gov/current/title-21` |
| Title 42 | Public Health (CMS dahil) | `https://www.ecfr.gov/current/title-42` |
| Title 45 Part 46 | Common Rule (insan araştırmaları) | `https://www.ecfr.gov/current/title-45/part-46` |

**Lex-Sanitas modu eşlemesi:** DRAFT, ANALYZE, RIA.

### 3.2. Federal Register (federalregister.gov)

**Tanım:** Yayımlanmakta olan kural taslakları (Notice of Proposed Rulemaking), nihai kurallar (Final Rules), başkanlık emirleri.

**API:** `https://www.federalregister.gov/api/v1` — REST, anahtarsız, dökümante.

**Lex-Sanitas modu eşlemesi:** RIA (ABD'de etki analizi metodu — NPRM yorum dönemi + Final Rule).

### 3.3. Congress.gov

**Tanım:** Kanun ve tasarı seviyesi. **API** kayıtla ücretsiz.

**Sağlıkla ilgili kritik kanunlar:**
- 21st Century Cures Act (2016, P.L. 114-255)
- CARES Act (2020)
- Inflation Reduction Act (2022 — Medicare drug price negotiation)
- PREVENT Pandemics Act
- PASTEUR Act (antimikrobiyal teşvik)

### 3.4. openFDA (open.fda.gov)

**Tanım:** FDA'nın **resmi açık API ekosistemi**.

**Modüller:**

| Modül | Endpoint | İçerik |
|-------|----------|--------|
| Drug labels (FDALabel) | `/drug/label.json` | Onay etiketi |
| FAERS | `/drug/event.json` | Advers olay raporları |
| Enforcement | `/drug/enforcement.json` | Geri çekme |
| NDC Directory | `/drug/ndc.json` | Ulusal İlaç Kodu |
| 510(k) | `/device/510k.json` | Cihaz onayı |
| PMA | `/device/pma.json` | Pre-market Approval |
| Recall | `/device/recall.json` | Cihaz geri çekme |

**Lex-Sanitas modu eşlemesi:** RIA (etki analizi metriği — FAERS sinyali → mevzuat revizyon ihtiyacı), DRAFT (farmakovijilans yönetmelik benchmark).

### 3.5. CMS — Centers for Medicare & Medicaid Services (cms.gov)

**Tanım:** Geri ödeme regülasyonu. NCD/LCD (National/Local Coverage Determinations), Medicare Part D Formulary File.

**Lex-Sanitas modu eşlemesi:** SUT taslakları için yapısal benchmark.

### 3.6. AHRQ — Effective Health Care Program (effectivehealthcare.ahrq.gov)

**Tanım:** Sistematik derlemeler, karşılaştırmalı etkinlik araştırmaları.

**Lex-Sanitas modu eşlemesi:** RIA bilimsel temellendirme katmanında.

### 3.7. ICER — Institute for Clinical and Economic Review (icer.org)

**Tanım:** ABD'nin yarı-bağımsız HTA kuruluşu; karşılaştırmalı klinik etkinlik + cost-effectiveness raporları.

**Lex-Sanitas modu eşlemesi:** RIA (SUT geri ödeme tebliği maliyet etkililik tartışması).

> *Karşılaştırmalı HTA model analizi (ICER + NICE + CADTH + PBAC + G-BA/IQWiG + HAS): R12 §7. Ayrıca medical-research § 14.d ICER detaylı kapsama.*

---

## 4. Diğer Yüksek Gelişmişlik Düzeyindeki Yargı Bölgeleri

> **R8 ↔ R12 Tekil Source of Truth Politikası (v2.3):** Bu bölümdeki Asya-Pasifik + Kanada yargı bölgeleri (Japonya, Güney Kore, Singapur, Avustralya, Hong Kong, Çin, Tayvan, Hindistan, Yeni Zelanda) için **R8 = kanonik portal + ana kanun adı + kısa kayıt**; **R12 = derin rejim analizi** (regülatör mekaniği, HTA modeli, Reliance pathway, Türkiye için operasyonel anlam, karşılaştırmalı reçeteler). Her iki dosya birbirini **tekrarlamaz**; tamamlar. Detay aramada her zaman önce R8 portal referansı, sonra R12 derin analiz okunur.

### 4.1. Kanada — Justice Laws Website (laws-lois.justice.gc.ca)

**Tanım:** Federal kanun ve yönetmelikler. **XML açık erişim**.

**Sağlık için kritik metinler:**
- Food and Drugs Act
- Food and Drug Regulations
- Medical Devices Regulations

**Regülatörler:**
- **Health Canada** (`canada.ca/en/health-canada`)
- **CADTH** (`cadth.ca`) — HTA otoritesi (Common Drug Review, pCODR onkoloji)

### 4.2. Avustralya — Federal Register of Legislation (legislation.gov.au)

**Tanım:** **Tam REST API + XML bulk**.

**Regülatörler:**
- **TGA** (`tga.gov.au`) — Therapeutic Goods Administration
- **PBAC** (`pbs.gov.au`) — Pharmaceutical Benefits Advisory Committee (HTA; Public Summary Documents açık)

> *Derin analiz: R12 §1.8 (Therapeutic Goods Act 1989 + TGA + PBAC + PBS — TR Reliance hedef alan); HTA karşılaştırma için R12 §7.*

### 4.3. Japonya — e-Gov + Japanese Law Translation (japaneselawtranslation.go.jp)

**Tanım:** Ulusal mevzuat tabanı + resmi İngilizce çeviri portalı.

**Regülatör:** **PMDA** (`pmda.go.jp`) — Pharmaceuticals and Medical Devices Agency. ICH'ın üç asıl ülkesinden biri.

> *Derin analiz: R12 §1.1 (Yakuji Hou 薬機法 + PMDA + Sakigake + Yakka Seido + CHE HTA — sürekli reform örüntüsü).*

### 4.4. Güney Kore — KLIC (law.go.kr/eng)

**Tanım:** Korean Law Information Center; resmi İngilizce çevirilerle.

**Regülatör:** **MFDS** (`mfds.go.kr`) — Ministry of Food and Drug Safety.

> *Derin analiz: R12 §1.2 (Pharmaceutical Affairs Act + MFDS + KIMS + HIRA + NHIS — Türkiye TR Reliance kandidatı).*

### 4.5. Singapur — Singapore Statutes Online (sso.agc.gov.sg)

**Regülatör:** **HSA** (`hsa.gov.sg`) — Health Sciences Authority; Asya'da hızlı ruhsatlandırma rejimi olarak benchmark.

> *Derin analiz: R12 §1.3 (Health Products Act 2007 + HSA + ACCESS Consortium Reliance — Singapur modeli TR Reliance için altın standart referans).*

### 4.6. İsveç — TLV (tlv.se)

**Tanım:** Tandvårds- och läkemedelsförmånsverket — Dental and Pharmaceutical Benefits Agency. Geri ödeme + HTA.

> *Derin analiz: R12 §2.1.2 (İskandinav modeli beşli birlik; İsveç MPA + TLV bütünleşik HTA-fiyatlama modeli).*

---

## 5. Uluslararası Kuruluşlar ve Karşılaştırmalı Veri

### 5.1. WHO — Dünya Sağlık Örgütü (Özet — Derinleşme için R11)

| Kaynak | URL | İçerik |
|--------|-----|--------|
| IRIS | `iris.who.int` | WHO yayın deposu; rehber, model regülasyon, EML |
| GHO (Global Health Observatory) | `who.int/data/gho` | Sağlık göstergeleri + API |
| Global Health Law Database / MindBank | `extranet.who.int/mindbank` | Akıl sağlığı + genel sağlık politikası |
| WHO Listed Authority (WLA) | `who.int/teams/regulation-prequalification` | Reliance kanalları için Türkiye stratejik referans |

> **Tam derinleşme:** WHO'nun **IHR 2005 + 2024 değişiklikleri**, **WHO Pandemic Agreement 2025 + PABS sistemi**, **FCTC + 4207 SK paraleli**, **EML/EMLc 2025**, **ICD-11 geçiş**, **ATC/DDD sistemi**, **WHO Guidelines (HIV, AMR, TB, palyatif, mental sağlık)**, **WHO Position Papers (aşı politikası)**, **Biotherapeutic Standards + biyobenzer iskeleti**, **WHO PQ + CRP + WLA**, **Codex Alimentarius (FAO ortak)**, **WHO EURO programları**, **WHO Drug Information Bulletin**, **WHO Country Office Türkiye + CCS 2022-2026** için **`references/11-who-derinlemesine-rejim.md`** açılır.

### 5.1.bis. BM Çerçevesi — İnsan Hakları + Sağlık (Özet — Derinleşme için R10)

Türkiye'nin Anayasa Md. 90/5 hükmü uyarınca temel hak sözleşmeleri kanun hükmündedir. Sağlık alanında zorunlu okumalar:

| Sözleşme | Sağlık Maddesi | Türkiye Statü |
|----------|----------------|----------------|
| ICESCR | Md. 12 + Genel Yorum 14 (AAAQ) | Taraf (2003) |
| CRC | Md. 24 + Genel Yorum 15 | Taraf (1995) |
| CEDAW | Md. 12 + Genel Tavsiye 24 | Taraf (1985) |
| CRPD | Md. 25 | Taraf (2009) |
| BM Narkotik Üçlü (1961/1971/1988) | Tam metin | Taraf (1967/1981/1996) |
| AİHS | Md. 2, 3, 8, 14 (sağlık ekseni içtihat) | Taraf (1954) |
| Oviedo Sözleşmesi (CETS 164) | Tam metin | **İmzalamadı** — *soft law* |
| Helsinki Bildirgesi 2024 (WMA) | 37 paragraf | WMA üyesi olarak benimseme |
| CIOMS 2016 Rehberi | Tam metin | TİTCK referans olarak |
| WTO TRIPS Md. 31bis + 39 | Tam metin | Taraf (1995) |

> **Tam derinleşme:** BM özel kuruluşları (UNICEF, UNFPA, UNAIDS, UNODC, ILO, FAO), Avrupa Konseyi Sosyal Şartı, BM Sağlık Hakkı Özel Raportörü, biyo-güvenlik sözleşmeleri, **Anayasa Md. 90/5 operasyonel uygulaması** için **`references/10-bm-uluslararasi-saglik-hukuku.md`** açılır.

### 5.2. OECD

| Kaynak | URL |
|--------|-----|
| OECD.Stat | `stats.oecd.org` |
| OECD iLibrary | `oecd-ilibrary.org` |
| Health at a Glance (yıllık) | `oecd.org/health/health-at-a-glance.htm` |
| Better Regulation çalışmaları | `oecd.org/gov/regulatory-policy` |

**API:** SDMX (Statistical Data and Metadata Exchange) — sağlık harcaması, sağlık kapasitesi, ilaç pazar verileri için programatik erişim.

### 5.3. WIPO Lex (wipolex.wipo.int)

**Tanım:** Patent ve fikri mülkiyet hukuku — sağlık alanında veri imtiyazı, SPC, biyobenzer patent peyzajı için kritik.

**Lex-Sanitas modu eşlemesi:** Pharmapatent skill ile birlikte; veri imtiyazı veya SPC yönetmelik taslaklarında.

### 5.4. World Bank — Open Data (data.worldbank.org)

**Tanım:** Sağlık harcaması, OOP, kapsam göstergeleri.

**Lex-Sanitas modu eşlemesi:** RIA sosyo-ekonomik etki bölümünde.

### 5.5. ICH — International Council for Harmonisation (ich.org)

**Tanım:** Q (Kalite), S (Güvenlik), E (Etkililik), M (Çok-disiplinli) serileri rehber dokümanlar. **Resmi mevzuat değil ama düzenleyici otoriteler arasında zımni normatif değere sahip.**

**Kritik kılavuzlar (örnek):**
- ICH Q1A(R2) — Stabilite testleri
- ICH Q9(R1) — Kalite risk yönetimi
- ICH E6(R3) — İyi Klinik Uygulamaları (GCP)
- ICH E8(R1) — Klinik çalışmaların genel düşünceleri
- ICH M4 — CTD formatı
- ICH M11 — Klinik elektronik veri standartları

**Lex-Sanitas modu eşlemesi:** Türk Klinik Araştırma ve Ruhsatlandırma Yönetmeliklerinin bilimsel iskeleti büyük ölçüde ICH ile uyumludur — taslakta dolaylı/doğrudan referans gerekir.

### 5.6. PIC/S — Pharmaceutical Inspection Co-operation Scheme (picscheme.org)

**Tanım:** GMP karşılıklı tanıma. **Türkiye PIC/S üyesidir**; GMP yönetmelik revizyonlarında doğrudan referans.

### 5.7. IMDRF — International Medical Device Regulators Forum (imdrf.org)

**Tanım:** Tıbbi cihaz regülasyonu için global hizalanma. MDR ve Türk Tıbbi Cihaz Yönetmeliği'nin yapısal kaynağı.

**Kritik dokümanlar:** UDI rehberi, SaMD (Software as a Medical Device) çerçevesi, Personalized Medical Devices, Adverse Event Terminology.

### 5.8. The Commonwealth Fund (commonwealthfund.org)

**Tanım:** Uluslararası sağlık politikası karşılaştırma raporları. RIA sosyo-politik etki bölümünde değerli.

### 5.9. ABAD — Court of Justice of the European Union (curia.europa.eu)

**Tanım:** AB Adalet Divanı içtihatı. CELEX `6...` prefix'li dokümanlar burada.

**Lex-Sanitas modu eşlemesi:** ANALYZE (uyum analizi), OPINE (AB Başkanlığı görüşünde içtihat dayanağı), COMPARATIVE_LAW (yeni 7. mod) yargısal kanıt boyutunda.

> **ABAD sağlık alanı klasik kararları (C-148/15 Deutsche Parkinson, C-557/16 Astellas Pharma, C-688/19 Hexal/Glaxo biosimilar, C-528/19 EMA Refusal vb.) için R13 Bölüm 3 — ABAD CELEX yapısı + standart atıf formatı.**

### 5.10. AİHM — HUDOC (hudoc.echr.coe.int)

**Tanım:** AİHM içtihat veri tabanı. Sağlık alanında AİHS Md. 2 (yaşam hakkı), Md. 3 (işkence yasağı — sağlık hizmeti reddi bağlamında), Md. 8 (özel yaşam — sağlık verisi, üreme sağlığı) içtihatları.

**Lex-Sanitas modu eşlemesi:** ANALYZE iptal/ihlal risk değerlendirmesi, COMPARATIVE_LAW yargısal kanıt.

> **AİHM Türkiye aleyhine + lehine önemli sağlık kararları (Mehmet Şentürk, Asiye Genç, Yardımcı, Kavur, Sarısaltık) ve karşılaştırmalı emsaller (Vo c. France, Tysiąc c. Polonya) için R13 Bölüm 2 — AİHM operasyonel rehberi.**

> **Türk Anayasa Mahkemesi + Danıştay + Yargıtay içtihat erişimi (Hukuki Veritabanları MCP), Türk akademik doktrin (Hakeri, Aydın, Yıldız, Gökcan vd.), Türk hukuk fakültesi dergileri ve YokTez tez taraması için ZORUNLU REFERANS: `references/13-icthat-doktrin-akademik-katman.md`.**

---

## 6. HTA ve Geri Ödeme Düzleminde Karşılaştırma — SUT Benchmark İçin

| Yargı Bölgesi | HTA Kurumu | URL | Erişim |
|---|---|---|---|
| Birleşik Krallık | NICE | `nice.org.uk/guidance` | TA guidance açık; Evidence Search API (rate-limited) |
| Almanya | G-BA / IQWiG | `g-ba.de` / `iqwig.de` | PDF/HTML; AMNOG beneficial value değerlendirmeleri |
| Fransa | HAS | `has-sante.fr` | Açık; Commission de la Transparence *avis* |
| Kanada | CADTH | `cadth.ca` | Açık; Common Drug Review |
| Avustralya | PBAC | `pbs.gov.au` | Public Summary Documents açık |
| ABD | ICER | `icer.org` | Açık; Evidence Reports |
| İsveç | TLV | `tlv.se` | Açık |
| Hollanda | ZIN | `zorginstituutnederland.nl` | Açık |
| Belçika | KCE | `kce.fgov.be` | Açık |
| Norveç | DMP | `dmp.no` | Açık |
| AB-bütünleşik | JCA (EU HTA Reg.) | `hta.europa.eu` | 2025 itibarıyla onkoloji + ATMP |

**EUnetHTA mirası:** EU HTA Regulation öncesi ortak değerlendirme raporları — eski POP database `eunethta.eu`.

---

## 7. Standart Sorgu Reçeteleri — Tipik Senaryolar

### 7.1. Senaryo: "MDR uyum kontrolü için Türk Tıbbi Cihaz Yönetmeliği'ni AB MDR ile karşılaştır"

```
Fetch → https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02017R0745-[YYYYMMDD konsolide tarih]
   → MDR konsolide tam metin
Mevzuat MCP → search_mevzuat(query="tıbbi cihaz yönetmeliği")
   → 2/6/2021 tarih ve 31499 sayılı Yönetmelik
Mevzuat MCP → get_mevzuat_content(...)
   → Türk metni
Tavily → site:ec.europa.eu MDCG guidance
   → Konuya özel MDCG rehberi
[Sentez: madde-madde tabloda paralel okumayı şablona aktar]
```

### 7.2. Senaryo: "SUT'a yeni ilaç ekleme tebliği için RIA — Bedaquiline+Delamanid kombinasyonu"

```
Mevzuat MCP → SUT yürürlükteki son tebliğini çek
Tavily → "NICE TA bedaquiline"
   → NICE değerlendirme (varsa)
Fetch → has-sante.fr [bedaquiline avis]
   → HAS Commission de la Transparence avis
Fetch → iqwig.de [bedaquiline dossier]
   → IQWiG değerlendirmesi
openFDA → drug.label endpoint, bedaquiline NDC
   → FDA onay etiketi + REMS bilgisi
WHO IRIS → "WHO consolidated guidelines on drug-resistant TB"
   → Global standart
PubMed + Scholar Gateway + Consensus + Tavily → DRT-TB klinik kanıt güncellemesi
[Sentez: dörtlü HTA + WHO + FDA + klinik kanıt → SUT madde önerisi]
```

### 7.3. Senaryo: "Klinik araştırma yönetmeliğinde Sponsor-Investigator tanımının revizyonu için"

```
Fetch → CELEX:32014R0536 (CTR konsolide)
   → AB CTR tanımları
Fetch → ich.org [E6(R3) GCP]
   → ICH güncel GCP
Fetch → gesetze-im-internet.de AMG § 4 (Begriffsbestimmungen)
   → Alman tanımları
Fetch → legifrance CSP L1121-1
   → Fransız tanımları
Fetch → ecfr.gov title-21 part-312
   → FDA IND yönetmeliği
Mevzuat MCP → Türk klinik araştırma yönetmeliği
[Sentez: 5-yargı bölgesi karşılaştırması → Türk tanım revizyon önerisi]
```

### 7.4. Senaryo: "AB Başkanlığı için tıbbi cihaz müktesebat uyum görüşü"

```
Mevzuat MCP → 7223 SK + Tıbbi Cihaz Yönetmeliği + İVT Yönetmeliği
Fetch → MDR + IVDR konsolide
Fetch → MDCG en güncel rehberler (ec.europa.eu/health/md_sector)
Tavily → "Türkiye İlerleme Raporu 2025 Chapter 1 Free Movement of Goods"
   → AB Komisyonu son yıllık rapor
Fetch → EUDAMED modül durumu
Mevzuat MCP → ÜTS genelgeleri (paralel olarak)
[Sentez: madde-madde uyum tablosu + AB Komisyonu raporundaki uyum açığı paragrafları]
```

---

## 8. Pratik Uygulama Notları

### 8.1. Çeviri ve dil bariyeri

Almanca AMG ve Fransızca CSP'nin **İngilizce resmi çevirileri sınırlıdır**; otomatik çeviri sonuçları **terminolojik kesinlik açısından mevzuat amacıyla yetersizdir.** Lex-Sanitas çıktısında uluslararası referans verilirken **çift gösterim** kullanın:

```
Almanca AMG § 21 (Zulassung — "Ruhsatlandırma") uyarınca... 
[orijinal madde başlığı + Türkçe bağlamsal açıklama]
```

### 8.2. Rate limit ve cache stratejisi

EUR-Lex API çağrıları rate-limit'e takılabilir. Uzun-vadeli projelerde:
- Bulk indirme + lokal cache
- CELEX referanslarını projeye özel sözlük halinde tutma
- Tavily Research modunun çoklu kaynak senteziyle sayfa sayısını azaltma

### 8.3. Sürüm doğrulama protokolü

Her uluslararası referansta **üç doğrulama**:

1. **Sürüm tipi** — Original / Consolidated. AB regülasyonları için konsolide şart.
2. **Yürürlük tarihi** — Date stamp kayda alın.
3. **Çeviri durumu** — Resmi / gayri resmi.

### 8.4. Bilgi sınırı uyarısı

Modelin bilgi sınırı sonrası yayımlanan AB regülasyonları, MDCG rehberleri, FDA Guidance'lar, NICE TA'ları **mutlaka Fetch ile resmi sayfadan teyit edilir.** Bu skill ezberden uluslararası referans vermez.

### 8.5. Yapısal gelişim önerisi

İleride bir **`/lex-comparatio` veya `/eu-medlaw` özel skill veya MCP** geliştirilmesi, EUR-Lex + ulusal düzlemleri + HTA çıktılarını tek sorguyla sentezleyebilecek bir araç boşluğunu doldurabilir. Bu, mevcut Tavily + Fetch + Exa üçlüsünün manuel orkestrasyonunu otomatize eder.

---

## 9. Kaynakça notu

Bu dosyadaki URL örüntüleri ve API özellikleri, ilgili kuruluşların kamuya açık dokümantasyonuna dayalı olarak, modelin bilgi sınırı itibarıyla doğrulanmış genel teknik özelliklerdir. Belirli bir endpoint'in güncel yapısı veya kimlik doğrulama gereksinimi için, kullanım anında ilgili portalın "Developer" veya "Open Data" sayfasının Fetch MCP ile teyit edilmesi önerilir.

Türkiye-AB Mevzuat Karşılaştırma Cetveli formatı için **AB Başkanlığı (`ab.gov.tr`) "Müktesebata Uyum Mevzuat Tablosu"** standardı esas alınmalıdır. Bu dosyanın güncellemesi, yeni AB sağlık regülasyonları yürürlüğe girdikçe yapılmalıdır (örn. EU HTA Regulation'ın 2028 yetim ilaçlar genişlemesi).
