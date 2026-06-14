# pharmaintel — Label & Post-Marketing Safety Sub-Protocol

## Scope

Onaylı her tedavi için **FDA label / EMA Summary of Product Characteristics (SmPC) / PMDA tenpu bunsho** fetch edilir ve strukturel olarak ekstrakte edilir. Post-marketing güvenlik için **FAERS disproportionality** kontrolü yapılır. Bu sub-protocol, pharmaintel'in "approval date yakalandı" seviyesinden "label semantic'i ve post-marketing safety picture'ı eksiksiz" seviyesine çıkarır.

**Neden bu sub-protocol (v1.3.0 gap):** Önceki sürümlerde FDA/EMA onay tarihi ve indikasyon özeti captured ediliyordu, ancak label'in operasyonel detayları (dozaj, kontrendikasyon, boxed warning, restrictive population, REMS gereksinimleri, co-admin uyarıları, DRG/mitochondrial toxicity monitorizasyon gereksinimleri) protokolün parçası değildi. Medical affairs bağlamında bu detaylar günlük kullanım sorularının cevabıdır — kliniyenlerin "kime, nasıl, ne zaman yazılır" diye sorduklarının tam karşılığı.

## Trigger rules (yüklenme koşulları)

Aşağıdaki durumlarda bu sub-protocol otomatik yüklenir:

1. **T2 Asset Profile** — onaylı bir asset için zorunlu
2. **T3 Modality Landscape** — landscape'te en az bir onaylı tedavi varsa zorunlu (pipeline-only landscape'lerde opsiyonel)
3. **T5 Catalyst Watch** — yeni onaylı ajan veya onaylı ajana post-marketing güvenlik olayı geldiyse
4. **T6 Head-to-Head Comparison** — karşılaştırılan her onaylı ajan için zorunlu
5. **T7 Regulatory Status Snapshot** — zaten label query'si
6. **Medical affairs use case flagged** — clinician briefing / KOL engagement materyali hazırlanıyorsa

**Tetiklenmez:** Pre-approval asset'ler için label bölümü doldurulamaz; bu asset'ler "label pending approval" stamp'i alır.

---

## Free-tier access hierarchy

| Kaynak | URL pattern | İçerik tipi | Confidence anchor |
|---|---|---|---|
| **FDA DailyMed** | dailymed.nlm.nih.gov/dailymed/search.cfm?query=[INN] | Structured Product Labeling (SPL) XML + renderred text; her label revizyonu | Primary regulatory |
| **FDA Drugs@FDA** | accessdata.fda.gov/scripts/cder/daf | Originator label + Summary Review + Medical Review + Action Package | Primary regulatory |
| **FDA Orange Book + Purple Book** | accessdata.fda.gov/scripts/cder/ob + purplebooksearch.fda.gov | Patent + exclusivity + biosimilar status | Primary regulatory |
| **EMA EPAR** | ema.europa.eu/en/medicines | SmPC + Assessment Report + PRAC minutes | Primary regulatory |
| **PMDA 添付文書** | pmda.go.jp/PmdaSearch/iyakuSearch | Japanese label (requires sub-protocol-pmda.md) | Primary regulatory |
| **FAERS Public Dashboard** | fis.fda.gov/sense/app/95239e26-e0be-42d9-a960-9a5f7f1c25ee | Adverse event reports + disproportionality signals | Primary post-marketing |
| **OpenFDA API** | api.fda.gov/drug/event.json | Programmatic FAERS access | Primary post-marketing |
| **VigiBase summary** | vigiaccess.org | WHO global pharmacovigilance | Secondary (aggregate) |

**Hierarchy principle:** Bir iddiada çelişki varsa — örneğin sponsor web sitesinde belirtilen indication ile DailyMed'deki label arasında fark varsa — **her zaman label primary'dir**. Sponsor site guidance'ları max Medium confidence ile cap'lenir; label tam metin High confidence sağlar.

---

## Adım adım protokol

### Step L1 — Label semantic extraction

Her onaylı ajan için DailyMed veya EMA EPAR fetch'i sonrası aşağıdaki strukturel şema doldurulur:

```markdown
#### [Brand] ([INN]) — [Sponsor]

**Onay ve sürümler:**
- FDA first approval: YYYY-MM-DD (indication)
- FDA latest label revision: YYYY-MM-DD (revision rationale)
- EMA first approval: YYYY-MM-DD (indication)
- EMA latest SmPC revision: YYYY-MM-DD

**Indication scope:**
> [label'den tam indication paragrafı, kısaltılmış değil]
> **Subpopulation restrictions:** [varsa biomarker / yaş / prior treatment kriterleri]
> **Line of therapy:** [first-line / second-line / refractory]

**Dosing & administration:**
- Standard dose: [...]
- Dose adjustments: [renal / hepatic / age / weight]
- Administration route: [IV / SC / oral / IT / IM]
- Infusion duration + premedication (if applicable): [...]

**Boxed warning (if present):**
> [tam metin]

**Contraindications:**
- [...]

**Warnings & precautions (key items):**
- [...]

**Monitoring requirements:**
- Baseline: [tests to perform before treatment]
- On-treatment: [frequency and parameters]
- Special populations: [pediatric / pregnancy / lactation / geriatric]

**Drug-drug interactions (clinically significant):**
- [...]

**REMS program (if present):**
- [...]

**Adverse reactions (≥10% incidence in pivotal trial, or Grade 3-4 rates):**
- [...]

**Pregnancy category + reproductive toxicity:**
- [...]

**Stamp:** Source: DailyMed SPL + EMA SmPC · Accessed: YYYY-MM-DD · Confidence: High
```

### Step L2 — Label delta analysis (eğer birden fazla onaylı ajan veya birden fazla onay sürümü varsa)

Onaylı tedaviler arasında (T3 Modality Landscape, T6 Head-to-Head) veya bir ajanın label revizyonları arasında delta yapılır:

```markdown
**Label comparison / evolution:**

| Parameter | [Agent A] | [Agent B] | [Agent C] |
|---|---|---|---|
| Indication scope (breadth) | ... | ... | ... |
| Age restriction | ... | ... | ... |
| Prior therapy requirement | ... | ... | ... |
| Boxed warning | ... | ... | ... |
| Route | ... | ... | ... |
| Dosing frequency | ... | ... | ... |
| REMS required | Y/N | Y/N | Y/N |
| Key monitoring | ... | ... | ... |
```

Bu tablo, kliniyenlerin pragmatic seçim sorularını (hangi hasta için hangi ajan?) doğrudan destekler.

### Step L3 — FAERS disproportionality check (post-marketing sinyal)

Her onaylı ajan için **OpenFDA API** veya FAERS Public Dashboard üzerinden post-marketing safety kontrol:

1. **Çalışma sırasındaki AE profil vs post-marketing FAERS sinyal** farkını tespit et
2. **Disproportionality signals** (ROR, PRR, EBGM skoru) için known databases'e başvur:
   - FDA FAERS Public Dashboard (signal mining yapılabilir)
   - VigiAccess (aggregate signal retrieval)
3. Sinyaller varsa **label'de reflect edilmiş mi** kontrol et:
   - Varsa: label update tarihi ve bölümü belirt
   - Yoksa: "emerging signal, not yet labeled" stamp'i ile flag

**Çıktı formatı:**

```markdown
**Post-marketing safety signals (FAERS/VigiBase, [accessed date]):**
- Top 5 reported reactions (FAERS, rank): [...]
- Disproportionality signals not fully captured in label:
  - [Reaction 1]: ROR [value], [label reflection status]
  - [Reaction 2]: [...]
- Regulatory actions triggered post-approval (safety communications, REMS modifications, label updates for safety):
  - [YYYY-MM-DD]: [action type + link]

**Stamp:** FAERS Public Dashboard · Accessed: YYYY-MM-DD · Confidence: Medium-High (aggregate signals reliable; individual case causality inference not made)
```

### Step L4 — Label-based HEOR / access considerations

Label'den çıkan HEOR-relevant öğeler:

- **Restrictive population** → specialty market channel sinyalidir, broad market değil
- **Boxed warning** → payer gatekeeping mekanizması tetikleyebilir (prior authorization, REMS-like monitoring requirement)
- **REMS program** → maliyet-artırıcı program gerekir (eğitim, monitorizasyon, distribution restriction)
- **Long infusion / monitoring period** → site-of-care (hospital vs ambulatory vs home) kararını etkiler
- **Pediatric-only indication** → specialty pediatric clinic + infusion center altyapısı gerektirir

Bu öğeler task-hta.md ve task-modality.md §Commercial & Payer Context bölümlerine beslenir.

---

## Confidence caps

| Claim type | Max confidence from label-only source |
|---|---|
| Approved indication verbatim | High (label primary) |
| Boxed warning text | High |
| Dosing | High |
| AE rates (as stated in label) | High |
| Disproportionality signal from FAERS aggregate | Medium-High (aggregate stable; individual causality not inferable) |
| Regulatory action history | High (FDA docket / EMA PRAC minutes direct) |
| Real-world effectiveness inference from label AE profile | Low (label AE rate ≠ real-world incidence) |

---

## Known gaps

1. **FAERS underreporting bias** — passive surveillance sistemlerinde underreporting yaygındır; özellikle hafif/non-serious AE'ler için. FAERS ratios yorumlanırken dikkatli olunmalı.
2. **Label lag vs emerging evidence** — label revizyonları PMR/PMC çalışmalarının sonuçlarıyla yıllar sonra güncellenir. Güncel peer-reviewed literatür label'den sapabilir.
3. **Pediatric label extrapolation** — bazı ajanlar erişkin kanıtıyla pediatrik yaş genişletmesi aldı (extrapolation based); bu durumlarda label efikasi kanıt-bazı uyuşmaz.
4. **Gene therapy lifetime safety** — AAV-based gen terapileri için post-marketing izlem (>5 yıl) datası sınırlıdır; FAERS erken-dönem güvenliği yakalar ama uzun-dönem immunogenicity ve durability için yetersiz.
5. **Country-specific label divergence** — aynı ajanın FDA/EMA/PMDA label'leri indikasyon scope'u ve restriction'larında farklılık gösterebilir; her biri ayrı fetch gerekir.
6. **Biosimilar / follow-on label inheritance** — Purple Book / Orange Book'ta biosimilar için reference ajan label'i inherited; bu aşağı akış nüansları yakalanmalı.

---

## Output integration

Bu sub-protocol'ün çıktısı **task report içinde ayrı §Label & Post-Marketing Context bölümü** olarak yer alır. Pre-approval asset'ler için bu bölüm "label pending; anticipated [INN] indication based on pivotal trial: [...]" formatında placeholder taşır.

## Cross-reference

- `sources-catalog.md §FDA DailyMed + FDA Drugs@FDA + EMA EPAR + FAERS` — URL kataloğu
- `triangulation.md §3` — label primary, sponsor secondary conflict resolution
- `task-asset.md §Regulatory history + safety profile` — asset-level integration point
- `task-modality.md §Commercial & Payer Context` (v1.4.0 yeni bölüm) — label delta tablosu buraya feed eder
- `task-hta.md §NICE / HAS / CADTH — clinical evaluation layer` — label indication + restriction tetikçileri
- `sub-protocol-pmda.md` — Japanese label fetch için paralel workflow

**Invocation:** SKILL.md Step 1b/1c/1d/1e paralelinde, onaylı ajan içeren her task'ta Phase 3 (Deep Dive) sırasında otomatik tetikli.
