# Pharma Naming Constraints — FDA/EMA/WHO/USAN/TİTCK Regulatory Screening

> **On-demand load.** Pharma, biotech, medtech, medical device brief'leri için **zorunlu yüklenir**. Mahir'in domain'i (oncology/hematology medical affairs, Roche Türkiye) dikkate alınarak onkoloji ve hematoloji sınıflarında derinleştirilmiştir.

---

## 1. Pharmaceutical Nomenclature Hiyerarşisi

Her ilaç üç adlandırma katmanına sahiptir:

```
Chemical name        →   Generic name (INN)      →   Brand (proprietary) name
   (IUPAC, CAS)           (WHO INN / USAN)            (FDA / EMA / TİTCK onaylı)
```

**Örnek (trastuzumab → Herceptin)**:
- **Chemical**: Immunoglobulin G1, anti-(human p185c-erbB2 receptor); recombinant humanized γ1-chain
- **Generic (INN)**: trastuzumab (`-mab` stem = monoclonal antibody)
- **Brand**: Herceptin (Roche proprietary)

**Örnek (pembrolizumab → Keytruda)**:
- **Chemical**: IgG4 kappa humanized anti-PD-1 monoclonal antibody
- **Generic (INN)**: pembrolizumab
- **Brand**: Keytruda (Merck & Co.)

Her katmanın dünya otoritesi:
- **Chemical**: IUPAC (teorik nomenclature) + CAS Registry (pratik identifier)
- **Generic**: **WHO INN Programme** (global) + **USAN Council** (ABD paralel)
- **Brand**: **FDA DMEPA** (ABD), **EMA NRG** (AB), **TİTCK** (Türkiye)

`brand-maker` skill'i yalnızca **üçüncü katman** (brand/proprietary name) için isim üretir, ancak **INN/USAN stem çakışması** brand isminin FDA/EMA tarafından otomatik reddedilmesine yol açar. Bu yüzden WHO INN stem sistemi **hayati önem** taşır.

---

## 2. WHO INN Stem Sistemi — Tam Kapsam

WHO INN sistemi, farmakolojik sınıfları **belirli son ekler ile** işaretler. Marka adı bu stem'lerle karışamaz. Aşağıdaki liste WHO INN Programme'nin son güncellemeleri (2022–2025) ile USAN Council stem listesinin sentezidir.

### 2.1 Onkoloji — Mahir Alanı (Detaylı)

| Stem | Sınıf | Örnek İlaçlar | Notlar |
|---|---|---|---|
| **`-mab`** | Monoclonal antibody | trastuzumab, pembrolizumab, rituximab, daratumumab, nivolumab, atezolizumab, obinutuzumab | Core onc/heme stem. Brand name sonu `-mab` = FDA DMEPA otomatik red. **Sub-stems**: `-omab` (mouse), `-ximab` (chimeric), `-zumab` (humanized), `-mumab` (fully human) |
| **`-tinib`** | Tyrosine kinase inhibitor (TKI) | imatinib, osimertinib, ibrutinib, lorlatinib, dasatinib, nilotinib, alectinib, brigatinib | Small-molecule onc class. `-tinib` ending kullanılamaz |
| **`-parib`** | PARP inhibitor | olaparib, niraparib, rucaparib, talazoparib | DNA damage response class |
| **`-ciclib`** | CDK4/6 inhibitor | palbociclib, ribociclib, abemaciclib | Breast cancer class marker |
| **`-rafenib`** | RAF kinase inhibitor | vemurafenib, dabrafenib, encorafenib, sorafenib | Melanoma BRAF V600 class |
| **`-degib`** | Hedgehog signaling inhibitor | vismodegib, sonidegib | BCC/medulloblastoma |
| **`-rasib`** | KRAS inhibitor | sotorasib, adagrasib | 2021+ yeni sınıf (KRAS G12C) |
| **`-nisib` / `-disib`** | PI3K/AKT/mTOR inhibitors | alpelisib, copanlisib, idelalisib | PI3K class |
| **`-dustat`** | HIF prolyl hydroxylase inhibitor | roxadustat, vadadustat | Anemia of CKD |
| **`-zomib`** | Proteasome inhibitor | bortezomib, carfilzomib, ixazomib | Multiple myeloma |
| **`-lisib`** (non-PI3K contexts) | Varied kinase | duvelisib | Dikkat — `-lisib` birden fazla class'a yayılmıştır |
| **`-mogulin`** / **`-vedin`** | ADC payload markers | — | Antibody-drug conjugate payload indicator |
| **`-deruxtecan`** | Topoisomerase I inhibitor payload | trastuzumab deruxtecan, datopotamab deruxtecan | ADC payload suffix |
| **`-govitecan`** | SN-38 (irinotecan metabolite) payload | sacituzumab govitecan | ADC payload suffix |
| **`-vedotin`** | MMAE payload | brentuximab vedotin, enfortumab vedotin | ADC payload suffix |
| **`-emtansine`** | DM1 payload | trastuzumab emtansine (T-DM1) | ADC payload suffix |

### 2.2 Hematoloji — Mahir Alanı (Detaylı)

| Stem | Sınıf | Örnek İlaçlar | Notlar |
|---|---|---|---|
| **`-cel`** | Cell therapy (CAR-T, TIL) | axicabtagene ciloleucel (axi-cel), tisagenlecleucel (tisa-cel), idecabtagene vicleucel (ide-cel), brexucabtagene autoleucel, ciltacabtagene autoleucel (cilta-cel), lisocabtagene maraleucel (liso-cel) | CAR-T + cell therapy stem |
| **`-tamab`** (BsAb) | Bispecific T-cell engager | teclistamab, epcoritamab, elranatamab, glofitamab, talquetamab, mosunetuzumab | Multiple myeloma + lymphoma BsAb class |
| **`-gene`** | Gene therapy | onasemnogene abeparvovec, valoctocogene roxaparvovec, exagamglogene autotemcel (exa-cel) | AAV-based gene therapy + CRISPR therapies |
| **`-parin`** | Heparin analogs | enoxaparin, dalteparin, tinzaparin, fondaparinux | LMWH class |
| **`-xaban`** | Factor Xa inhibitor | apixaban, rivaroxaban, edoxaban, betrixaban | DOAC class |
| **`-rubin`** | Direct thrombin inhibitor | dabigatran (etexilate) | DTI class |
| **`-brutinib`** | BTK inhibitor (specific) | ibrutinib, acalabrutinib, zanubrutinib, pirtobrutinib | B-cell malignancy class |
| **`-zumab`** (heme-specific) | Humanized mAb | daratumumab, elotuzumab, inotuzumab ozogamicin, blinatumomab | Heme malignancy humanized antibody |

### 2.3 Kardiyovasküler

| Stem | Sınıf | Örnek İlaçlar |
|---|---|---|
| **`-olol`** | Beta blocker | metoprolol, atenolol, carvedilol, bisoprolol |
| **`-pril`** | ACE inhibitor | lisinopril, enalapril, ramipril, captopril |
| **`-sartan`** | Angiotensin II receptor blocker (ARB) | losartan, valsartan, telmisartan, irbesartan |
| **`-statin`** | HMG-CoA reductase inhibitor | atorvastatin, rosuvastatin, simvastatin, pravastatin |
| **`-dipine`** | Dihydropyridine CCB | amlodipine, nifedipine, felodipine |
| **`-afil`** | PDE5 inhibitor | sildenafil, tadalafil, vardenafil |
| **`-dralazine`** | Hydralazine derivatives | hydralazine |

### 2.4 Endokrinoloji

| Stem | Sınıf | Örnek İlaçlar |
|---|---|---|
| **`-gliptin`** | DPP-4 inhibitor | sitagliptin, linagliptin, saxagliptin |
| **`-gliflozin`** | SGLT2 inhibitor | empagliflozin, dapagliflozin, canagliflozin, ertugliflozin |
| **`-glitazone`** | Thiazolidinedione (TZD) | pioglitazone, rosiglitazone |
| **`-glutide`** | GLP-1 receptor agonist | semaglutide, dulaglutide, liraglutide, exenatide, **tirzepatide** (dual GIP/GLP-1, `-patide` stem variant) |
| **`-glinide`** | Meglitinide insulin secretagogue | repaglinide, nateglinide |

### 2.5 Antivirals

| Stem | Sınıf | Örnek İlaçlar |
|---|---|---|
| **`-buvir`** | HCV polymerase inhibitor | sofosbuvir, dasabuvir |
| **`-previr`** | HCV protease inhibitor | glecaprevir, voxilaprevir, grazoprevir |
| **`-tegravir`** | HIV integrase inhibitor | dolutegravir, raltegravir, bictegravir, cabotegravir |
| **`-vir`** (genel) | Antiviral | acyclovir, ganciclovir, oseltamivir |

### 2.6 Antimikrobiyaller

| Stem | Sınıf | Örnek İlaçlar |
|---|---|---|
| **`-cillin`** | Penicillin | amoxicillin, ampicillin, penicillin V |
| **`-floxacin`** | Fluoroquinolone | ciprofloxacin, levofloxacin, moxifloxacin |
| **`-mycin`** | Aminoglycoside / macrolide | erythromycin, azithromycin, gentamicin, vancomycin |
| **`-azole`** | Antifungal / PPI crossover | fluconazole, voriconazole + omeprazole (PPI), pantoprazole |
| **`-conazole`** | Antifungal specific | itraconazole, posaconazole |

### 2.7 Diğer Kritik Sınıflar

| Stem | Sınıf | Örnek İlaçlar |
|---|---|---|
| **`-prazole`** | Proton pump inhibitor | omeprazole, pantoprazole, esomeprazole, lansoprazole |
| **`-setron`** | 5-HT3 receptor antagonist | ondansetron, granisetron, palonosetron |
| **`-giline`** | MAO-B inhibitor | selegiline, rasagiline, safinamide |
| **`-triptan`** | 5-HT1B/1D agonist (migraine) | sumatriptan, rizatriptan, eletriptan |
| **`-caftor`** | CFTR modulator (cystic fibrosis) | ivacaftor, lumacaftor, tezacaftor, elexacaftor |
| **`-tursen` / `-rsen`** | Antisense oligonucleotide | nusinersen, milasen, inotersen, tofersen |
| **`-mab (tursen)` edit** | Antisense + antibody chimera | — |
| **`-mer`** | Aptamer / oligonucleotide | pegaptanib |

**Toplam aktif stem sayısı**: ~250+ (WHO INN Programme 2024 liste + USAN Council yayını)

Tam programatik liste: `data/usan_stems.json`

---

## 3. FDA Brand Name Review Süreci (DMEPA)

### 3.1 DMEPA Rolü

**Division of Medication Error Prevention and Analysis** (DMEPA), FDA'nın Center for Drug Evaluation and Research (CDER) içinde konumlanan brand name review birimi. Her yeni pharma brand name submission **FDA Form 3331** ile başvurur.

### 3.2 Üç-Katmanlı İnceleme

**Katman 1: LASA (Look-Alike Sound-Alike)**
- Mevcut onaylı ilaç isimleriyle **karışma riski**
- Text similarity (Levenshtein) + phonetic similarity (Soundex/Metaphone) test edilir
- Yanlış reçeteleme riski yaratıyorsa red
- Örnek red: "Celexa" (citalopram, depression) vs "Celebrex" (celecoxib, NSAID) — onaylanıp sonra LASA sorunları

**Katman 2: USAN Stem Collision**
- Brand name bir INN/USAN stem ile bitiyor veya stem'i içeriyorsa red
- Örnek red: "Novamab" (sonu `-mab` — mAb sınıfını ima eder, gerçekte mAb değilse aldatıcı)

**Katman 3: Promotional Claim**
- İsim abartılı klinik vaat içeriyorsa red
- Örnek red: "Curit", "Heala", "Nopain", "Cureall", "Painaway"
- Uluslararası uyarı: "Super-", "Ultra-", "Max-" ön ekleri de risk

### 3.3 FDA DMEPA İstatistikleri

- **Yıllık ortalama ilk başvuru reddi**: %30–40
- **Revizyon döngüsü**: 3 rund'a kadar serbest; 4.'da formal hearing
- **Onay süresi**: 180 gün (standart), 90 gün (priority)
- **En sık red nedeni**: LASA (60%), USAN stem (20%), promotional claim (15%), diğer (5%)

### 3.4 brand-maker Integration

`inn_stem_collision.py` scripti FDA DMEPA Katman 2'yi simüle eder. Ancak Katman 1 (LASA) tam kapsam için **USP Medication Errors Database** erişimi gerektirir; skill bu katmanı heuristic olarak modellemez — raporda kullanıcıya "LASA formal doğrulama gerekli" uyarısı yazar.

---

## 4. EMA Invented Name Review (NRG — Name Review Group)

### 4.1 EMA NRG Rolü

**Name Review Group**, EMA'nın Committee for Medicinal Products for Human Use (CHMP) bünyesinde brand name review yapar. Centralized procedure'deki tüm ilaçlar için zorunlu.

### 4.2 AB 27 Üye Devlet Filtresi

- Her üye devletin resmi dilinde olumsuz çağrışım kontrolü
- Özellikle Almanca, Fransızca, İtalyanca, İspanyolca, Lehçe, Hollandaca, Yunanca, Romence kritik
- Örnek red: İngilizce temiz bir isim, Fransızcada müstehcen duyabilir

### 4.3 "Invented" Gerekliliği

- EMA, brand name'in **icat edilmiş** (invented) olmasını bekler
- Gerçek kelime = descriptive = red olasılığı
- Jenerik-bitişli coined isimler (Opdivo, Keytruda, Lynparza, Trodelvy) tipik kabul

### 4.4 Revision Timeline

- İlk submission: CHMP opinion ile paralel (Day 120)
- Revizyon döngüsü: 180 gün içinde 2 revision
- Red durumunda appeal procedure mümkün

---

## 5. TİTCK Türkiye Kuralları

### 5.1 Paralel Süreç

TİTCK (Türkiye İlaç ve Tıbbi Cihaz Kurumu) FDA + EMA standartlarının üstüne ek filtreler uygular. Türkiye'de her pharma brand name TİTCK onayından geçmek zorundadır — centralized EMA prosedürü burada **yeterli değildir**.

### 5.2 TİTCK-Spesifik Red Nedenleri

**Türkçe olumsuz çağrışım**:
- "Keytruda" → Türkçede sorun yok (onaylı)
- Hayali örnek: "Kefarim" → Türkçe "kefaret" (paying penalty) — reddedilebilir
- Hayali örnek: "Malinol" → Türkçe "malın olma" negatif çağrışım

**Dini/etnik hassasiyet**:
- Kur'an-ı Kerim kelimeleri veya İslami mübarek isimler — red
- Etnik/ırksal çağrışım — red
- Devlet sembollerine yakın isimler — red

**Türkçe eczane LASA**:
- TİTCK Türkçe telaffuz LASA testi yapar
- Türkçe alfabede var olan sesler üzerinden rekontrol
- Örnek: "Taxol" (paclitaxel, Bristol Myers Squibb) + "Taxotere" (docetaxel, Sanofi) Türkçede LASA uyarı alır

### 5.3 Türkiye'de Onaylı Örnekler

- **Keytruda** (pembrolizumab, MSD)
- **Opdivo** (nivolumab, BMS)
- **Herceptin** (trastuzumab, Roche)
- **Mabthera** (rituximab, Roche)
- **Enhertu** (trastuzumab deruxtecan, DS/AZ)
- **Lynparza** (olaparib, AstraZeneca)
- **Tagrisso** (osimertinib, AstraZeneca)
- **Tecentriq** (atezolizumab, Roche)

---

## 6. WIPO Madrid Class 5 Pharma Özellikleri

### 6.1 Pharma için Öncelikli Nice Sınıfları

**Class 5** — Pharmaceutical preparations (ana sınıf):
- Pharmaceutical and veterinary preparations
- Sanitary preparations for medical purposes
- Dietetic substances adapted for medical use
- Food for babies
- Plasters, materials for dressings
- Disinfectants

**Class 10** — Medical apparatus and instruments:
- Tıbbi cihazlar, implantlar, CAR-T için gerekli ek sınıf

**Class 44** — Medical services:
- Klinik hizmetler, medical information services

Pharma launch için minimum Class 5 + Class 10 (medical device componenti varsa) + Class 44 (support services) kombinasyonu önerilir.

### 6.2 Opposition Proceedings — Pharma Yüksek Oranı

Pharma'da trademark opposition oranı diğer sektörlere göre ~3–5 kat yüksektir. Sebep:
- Sınırlı "ownable" namespace (stem kuralları kısıt)
- Büyük ilaç şirketlerinin defensive portfolio stratejisi
- LASA concern ile birleşen legal vigilance

Pharma brand için **erken coğrafi filing** kritik.

---

## 7. Modern Pharma Brand Archetypes (2023–2026)

`brand-maker` pharma brief'lerinde aşağıdaki 5 archetype'tan biri üzerine inşa eder:

### 7.1 Scientific Authority
**Örnekler**: Keytruda, Opdivo, Tagrisso, Tecentriq
**Özellikler**: Latin/Greek kök + hafif coined. Güven ve klinik ağırlık taşır.

### 7.2 Patient-Emotional
**Örnekler**: Lyrica (fibromyalgia — "lyric/music/healing"), Abilify (schizophrenia — "ability")
**Özellikler**: Duygu çağrıştıran İngilizce kök. DTC marketplace'e uygun.

### 7.3 Mechanism-Evocative
**Örnekler**: Xarelto (factor Xa rivaroxaban — "Xa + reto"), Eliquis (apixaban)
**Özellikler**: İlacın mekanizmasına ince atıf — ama generic isme değil.

### 7.4 Coined-Global-Neutral
**Örnekler**: Ozempic, Wegovy, Mounjaro, Zepbound (hepsi semaglutide/tirzepatide), Trodelvy
**Özellikler**: Tamamen icat kelime, hiçbir dilde bağlantı yok. Modern standart.

### 7.5 Heritage-Institutional
**Örnekler**: Pfizer (kurucu), Roche (kurucu), Merck (kurucu), AstraZeneca (merge)
**Özellikler**: Şirket ismi olarak ürün markası — yeni launch için **önerilmez**.

---

## 8. brand-maker Pharma Brief Flow

### 8.1 Triyaj Tetiği

Aşağıdaki sinyallerin herhangi biri pharma-naming-constraints.md'yi tetikler:
- "pharma", "ilaç", "biotech", "medtech", "medical device"
- "FDA", "EMA", "TİTCK", "centralized procedure"
- "INN", "generic name", "drug name", "molecule"
- Onkoloji/hematoloji/kardiyoloji/endokrinoloji/enfeksiyon terminolojisi

### 8.2 Otomatik Script Çağrıları

```bash
# INN/USAN stem collision check (Eksen 5)
python /mnt/skills/user/brand-maker/scripts/inn_stem_collision.py "Finalist1"

# Entity disambiguation — high-precision pharma mode
python /mnt/skills/user/brand-maker/scripts/entity_disambiguation.py --high-precision "Finalist1"
```

### 8.3 Raporda Yazılan Bölüm

Output template Section **4A. Pharma-Specific Regulatory Screening** eklenir:

```markdown
## 4A. Pharma-Specific Regulatory Screening

| Finalist | USAN Stem Çakışması | LASA Riski | Promosyonel Yüklü | TİTCK TR Riski |
|---|---|---|---|---|
| [İsim] | ✗/✓ (stem) | [top 3 LASA adayı] | ✗/✓ | ✗/✓ |

**Per-finalist rationale**:
- [İsim 1]: INN stem taraması temiz. LASA `-axel` suffixli ilaçlara adjacent (Taxol, Taxotere) ama edit distance 3+. Promosyonel yüklü değil. Türkçe temiz.
```

---

## 9. Oncology/Hematology Spesifik Strateji (Mahir Profili)

### 9.1 ADC (Antibody-Drug Conjugate) İsimlendirme

ADC'ler **iki isim parçası**ndan oluşur: antibody (mAb) + payload.
- **trastuzumab deruxtecan** → Enhertu (brand)
- **sacituzumab govitecan** → Trodelvy
- **datopotamab deruxtecan** → (henüz brand yok 2026 Q1)

Brand strategy: Payload-adjacent kelimelere dikkat (-deruxtecan'ı ima edebilir).

### 9.2 CAR-T İsimlendirme

CAR-T ürünleri `-cel` suffix (cel = cells).
- axicabtagene ciloleucel → Yescarta
- tisagenlecleucel → Kymriah
- idecabtagene vicleucel → Abecma
- lisocabtagene maraleucel → Breyanzi
- ciltacabtagene autoleucel → Carvykti

Brand strategy: Tek-hece sert cesaret (Kymriah, Yescarta).

### 9.3 Bispecific Antibody İsimlendirme

`-tamab` suffix (teclistamab, epcoritamab, glofitamab, talquetamab).

Brand örnekleri 2023–2026:
- teclistamab → Tecvayli
- epcoritamab → Epkinly
- talquetamab → Talvey
- glofitamab → Columvi (Roche)
- mosunetuzumab → Lunsumio (Roche)

### 9.4 Modern Oncology Naming Trends 2023–2026

Gözlemler:
1. **Kısa isim baskın**: 2-3 hece (Enhertu, Trodelvy, Tagrisso)
2. **Sert ünsüz açılış**: T, K, E, X başlangıç (Tecentriq, Keytruda, Xarelto)
3. **`-a` / `-i` açık sonlanış**: Abdominal-friendly, EU+TR pronunciation rahat
4. **Greek/Latin kök yerine coined**: Eski era (Paclitaxel → Taxol) vs yeni era (nivolumab → Opdivo)

---

## 10. Vaka Analizleri (Success + Failure)

### 10.1 Başarı: Keytruda (pembrolizumab)

- Merck Research Labs + Brand Institute birlikte çalıştı
- Fonetik: **key** (açar/kritik) + **truda** (coined, Greek "strongly" mı ima ediyor?)
- INN stem `-mab` tamamen kaçınıldı
- 5+ yıl hakimiyet: checkpoint inhibitor class leader

### 10.2 Başarı: Ozempic (semaglutide)

- Novo Nordisk blockbuster
- Fonetik: İcat-kelime, Latin aura
- GLP-1 `-glutide` stem'inden uzak durdu
- DTC ve TikTok era'da viral — "Ozempic face" kültürel fenomen

### 10.3 Başarısızlık: "Cureall"

- Hipotetik brand önerisi (gerçek değil)
- FDA DMEPA otomatik red: promotional claim (Katman 3)
- "Cure" kelimesi clinical endpoint vaadi olarak okunur
- Benzer red örnekleri: "Heala", "Nopain", "Painaway", "Forever Young"

### 10.4 Post-Launch Problem: "Rocephin → Rofecoxib LASA"

- Rocephin (ceftriaxone antibiotic, Roche)
- Rofecoxib (Vioxx NSAID, Merck — 2004 çekildi)
- Yıllar sonra post-market LASA analizi riski tespit etti
- Lesson: Brand name launch sonrası da surveillance gerekli

---

## 11. Kaynaklar

- World Health Organization. (2022). *Guidelines on the Use of International Nonproprietary Names (INNs) for Pharmaceutical Substances*. WHO Programme on INN.
- FDA Center for Drug Evaluation and Research. (2024). *Best Practices in Developing Proprietary Names for Human Prescription Drug Products: Guidance for Industry* (Final version).
- FDA. (2016). *Safety Considerations for Product Design to Minimize Medication Errors: Guidance for Industry*.
- European Medicines Agency. (2024). *CHMP Guideline on the Acceptability of Invented Names for Human Medicinal Products*. EMA/CHMP/287710/2014 Rev. 7.
- Türkiye İlaç ve Tıbbi Cihaz Kurumu (TİTCK). (2025). *Beşeri Tıbbi Ürünler İsimlendirme Rehberi* (güncellenmiş).
- USAN Council. (2024). *Statement of Principles: United States Adopted Names Council*.
- Brand Institute. (2024). Pharmaceutical naming case studies portfolio.
- Lexicon Branding (David Placek). (2026, January). *Brand Naming in 2026: AI, Trademarks & Emerging Trends* [Podcast]. Focus Lab.

---

## 12. Yasal Uyarı

**Bu dosya klinik, regulatuar veya hukuki tavsiye değildir.** `brand-maker` skill'i pharma brand name için **ön-tarama** yapar; **FDA Brand Name Review / EMA Invented Name Group / TİTCK formal submission** zorunludur ve bu skill onların yerini alamaz.

Skill'in pharma-naming-constraints.md ve `inn_stem_collision.py` kombinasyonu:
- FDA DMEPA Katman 2 (USAN stem) ön-tarama → **yüksek doğruluk**
- FDA DMEPA Katman 1 (LASA) heuristic → **orta doğruluk** (formal USP LASA database gereklidir)
- FDA DMEPA Katman 3 (promotional claim) semantic → **heuristic uyarı**
- TİTCK Türkçe filtre → `turkish_semantic_check.py` ile yüksek doğruluk

Final pharma brand launch için Brand Institute, Addison Whitney, Lexicon Branding gibi uzman ajanslarla + formal regulatory submission zorunludur.
