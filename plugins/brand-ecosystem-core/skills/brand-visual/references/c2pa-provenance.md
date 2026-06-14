# C2PA Content Credentials & AI Provenance

> **Adım 5.11 zorunlu referansı.** `brand-visual` v1.3'te eklendi. 2026'da AI ile üretilmiş brand assets için **provenance disclosure** regulatory gereklilik (EU AI Act 2024). Nano Banana 2 bu metadata'yı otomatik gömüyor — bu dosya, o metadata'nın **brand identity pipeline boyunca korunması** için protokol sunar.

## Tez

2026'da iki regulatory kuvvet markaların AI-generated asset workflow'unu değiştirdi:

1. **EU AI Act** (Aralık 2024 fully in effect) — AI-generated content için **disclosure zorunlu**. Markalar AI ile üretilmiş reklam / identity / marketing asset'lerinde bunu **public olarak** belirtmeli.

2. **C2PA (Coalition for Content Provenance and Authenticity)** — Adobe, Microsoft, Google, Nikon, Sony, BBC, Intel tarafından başlatılan açık standart. Görüntü/video/audio dosyalarına **cryptographically signed metadata** gömerek "bu içerik ne, nasıl üretildi, kim tarafından" bilgisini taşır.

Bu ikisi birleşti: **C2PA = EU AI Act compliance'ın de facto teknik implementasyonu**. Markalar artık:
- AI-generated brand asset yayınlarken C2PA manifest **ekleyeceğini** bilir
- Vector conversion, post-processing, retouching sırasında provenance'ı **korumanın** yolunu bulur
- Trademark başvurusu + copyright claim için provenance + human authorship **ikisini birlikte** dokümante eder

## Üç Katmanlı Provenance Framework

### Katman 1: Üretim (Generation)
- Nano Banana 2 çıktısı: **SynthID watermark** (invisible) + **C2PA Content Credentials manifest** otomatik gömülü
- Grok Imagine çıktısı: xAI provenance metadata (C2PA uyumu gelişen — 2026 Q2 expected)
- Midjourney çıktısı: C2PA optional (Pro/Mega plan'de available)
- Stable Diffusion / lokal modeller: **manuel** C2PA tooling (c2patool CLI)

### Katman 2: Dönüşüm (Transformation)
- Vector conversion (vtracer / Illustrator) sırasında **metadata korunmalı**
- Photoshop / Figma edits için **C2PA-compatible software** zorunlu (Adobe full C2PA support 2026)
- Upscaling / cropping / color adjustment bir **transformation chain** olarak logged
- Her transformation **ayrı bir assertion** olarak manifest'e eklenir

### Katman 3: Yayın (Publication)
- Brand identity PDF, web assets, social media post = tümünde C2PA manifest korunur
- Website: `<img src="logo.svg">` yanında Content Credentials viewer UI
- Press release: AI disclosure statement
- Trademark başvurusu: human authorship documentation + provenance chain

Adım 5.11 output'u bu üç katmanın her biri için konkret spec üretir.

## Teknik Implementasyon

### C2PA Manifest Yapısı (Örnek)

```json
{
  "claim_generator": "Gemini 3.1 Flash Image (Nano Banana 2)",
  "claim_generator_info": [
    { "name": "Google DeepMind", "version": "3.1.preview" }
  ],
  "assertions": [
    {
      "label": "c2pa.actions",
      "data": {
        "actions": [
          {
            "action": "c2pa.created",
            "when": "2026-04-24T10:30:00Z",
            "softwareAgent": "Gemini 3.1 Flash Image"
          },
          {
            "action": "c2pa.ai_generated",
            "digitalSourceType": "trainedAlgorithmicMedia",
            "parameters": {
              "description": "[UMMP prompt text]"
            }
          }
        ]
      }
    },
    {
      "label": "c2pa.training-mining",
      "data": {
        "entries": {
          "c2pa.ai_inference": { "use": "allowed" },
          "c2pa.ai_training": { "use": "notAllowed" },
          "c2pa.data_mining": { "use": "notAllowed" }
        }
      }
    },
    {
      "label": "stds.schema-org.CreativeWork",
      "data": {
        "@type": "CreativeWork",
        "author": {
          "@type": "Organization",
          "name": "[Brand Name]"
        },
        "creator": "AI-generated with human creative direction"
      }
    }
  ],
  "signature": { /* cryptographic signature */ }
}
```

### Vector Conversion'da Metadata Korumak

AI-generated raster (PNG) → SVG conversion sırasında metadata'yı kaybetmemek için:

```bash
# 1. Raster'ın C2PA manifest'ini extract et
c2patool logo_nb2.png --output logo_manifest.json

# 2. Vector conversion yap (vtracer)
python scripts/vector_trace.py logo_nb2.png --output logo.svg --preset logo-color

# 3. SVG <metadata> bloğuna C2PA reference ekle
# (scripts/vector_trace.py v1.3'te --preserve-c2pa flag ile otomatik)
python scripts/vector_trace.py logo_nb2.png --output logo.svg \
    --preset logo-color --preserve-c2pa logo_manifest.json
```

SVG'de sonuç:
```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <metadata>
    <c2pa:manifest href="./logo_manifest.json" 
                   version="2.1" 
                   xmlns:c2pa="https://c2pa.org/manifest"/>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:dc="http://purl.org/dc/elements/1.1/">
      <rdf:Description>
        <dc:creator>[Brand Name] creative direction + Nano Banana 2 (Gemini 3.1 Flash Image)</dc:creator>
        <dc:date>2026-04-24</dc:date>
        <dc:rights>Human-directed AI output + significant manual vector refinement</dc:rights>
      </rdf:Description>
    </rdf:RDF>
  </metadata>
  <!-- SVG path data -->
</svg>
```

### Adobe Workflow (C2PA Native Support 2026)

Adobe Illustrator / Photoshop 2026 sürümleri **native C2PA support** içeriyor. Workflow:

1. **Open**: AI-generated raster açıldığında C2PA manifest otomatik detect
2. **Edit**: Her edit (retouching, cleanup) **yeni assertion** olarak manifest'e eklenir
3. **Export**: Export dialog'unda "Include Content Credentials" checkbox default-on
4. **Publish**: Content Credentials Cloud'a upload (opsiyonel public verification)

## EU AI Act Uyumu: Disclosure Template

EU AI Act Article 50'ye göre, AI-generated veya AI-manipulated content public yayında **disclosure** zorunludur. Brand identity contexte'inde bu nasıl uygulanır?

### Disclosure Hierarchy

**Tier 1 — Core Identity Assets (Logomark, Wordmark)**
- Core identity **genelde human-authored + AI-assisted** konumlanır (vector rebuild + significant manual work)
- Disclosure: **opsiyonel** ama **best practice**
- Template (website footer):
  > "Our logomark was developed through creative direction with AI image generation (Nano Banana 2) and refined through manual vector design. [Content Credentials →]"

**Tier 2 — Marketing / Campaign Visuals**
- Campaign visuals typically **AI-generated + light editing**
- Disclosure: **zorunlu** (EU AI Act Article 50)
- Template (asset caption):
  > "This visual was generated with the assistance of AI (Nano Banana 2) and curated by [Brand Name]'s creative team. [Content Credentials verification →]"

**Tier 3 — Product Mockups / Presentation**
- Nano Banana 2 multi-reference mockup = hybrid
- Disclosure: **zorunlu** (transparency)
- Template: Similar to Tier 2

### Public-Facing Disclosure Examples

**Website footer (persistent)**:
```html
<footer>
  <p>Our brand identity was created with human creative direction and AI image 
  generation. Full provenance:
    <a href="/brand/content-credentials">Content Credentials →</a>
  </p>
</footer>
```

**Social media post caption**:
```
[Post content]

—
Created with AI (Nano Banana 2) under creative direction by [Brand].
C2PA Content Credentials available: [link]
```

**Press release boilerplate**:
```
[Brand Name] identity note: Brand visual assets developed through hybrid 
workflow — human creative direction with AI image generation tools 
(Nano Banana 2, Grok Imagine) and manual vector refinement. Full content 
provenance available at [URL].
```

## Copyright & Trademark Strategy

### USA: Thaler v. Perlmutter (2023) + USPTO 2025 Guidance

**Mevcut durum**:
- Pure AI-generated output **telif korumasız** (Thaler v. Perlmutter)
- **Significant human modification + documented creative direction** → telif eligible
- USPTO 2025 revised guidance: process documentation zorunlu

**Brand-visual workflow karşılığı**:

1. **AI generation** (Nano Banana 2 / Grok Imagine) → raster, **copyright-safe değil** tek başına
2. **Vector rebuild** (manuel cleanup, Illustrator Pen Tool, node reduction) → **significant human modification**
3. **Design refinement** (color calibration, optical correction, kerning) → **human creative direction**
4. **Documentation** (process record, iteration logs, UMMP prompt history) → **legal defense**

**Sonuç**: Vector-converted + manually refined logomark = **copyright eligible**. AI raster standalone = **değil**.

### EU: Copyright + AI Act

EU copyright doktrini benzer: human authorship eşiği var, ama **daha permissive** (transformative use + AI tool kullanımı olarak yorumlanabilir).

AI Act ek yükümlülük: **disclosure + provenance track**. Bu, telif başvurusuna zarar vermez; aksine **transparency** trademark/IP office'lerinde olumlu etki eder.

### Türkiye: SMK 6769 + 5846 (FSEK)

- **Trademark (marka)**: SMK Md. 83 — ayrıştırıcı logo tescili mümkün. AI-üretim origin trademark tesciline engel değil (trademark = commercial use sign, authorship değil).
- **Telif (FSEK)**: Md. 1/B "eser sahibinin hususiyeti" şartı. Pure AI = human hususiyet yok → eser değil. Manual refinement + creative direction varsa → eser sahipliği kurulabilir.

**Pratik implikasyon** (Mahir için):
- Era Pharma + Roche + ozlemmurzoglu.com gibi Türkiye projelerinde:
  1. AI ile ilk konsept üret
  2. Vector rebuild + significant manual work yap
  3. Process dokümante et (UMMP prompt history + iteration log)
  4. TÜRKPATENT trademark başvurusunda dosyala
  5. FSEK telif için "human-directed" argümanı

## Trademark Application Package (C2PA Era)

Trademark başvurusunda 2026 itibariyle best practice package:

```
trademark-submission/
├── logo.svg                                  # Production SVG
├── logo_manifest.json                        # C2PA Content Credentials
├── AI_disclosure_statement.md                # Transparent disclosure
├── human_authorship_record.md                # Process documentation
├── iteration_log.md                          # Each iteration + decision
├── prompt_history.md                         # UMMP evolution
├── vector_process_screenshots/               # Pen tool work
├── color_calibration_notes.md                # Human creative direction
└── final_brand_identity_report.pdf           # Full deliverable
```

### AI Disclosure Statement Template

```markdown
# AI Disclosure Statement for Trademark Application

**Brand**: [Name]
**Filing Jurisdiction**: [USPTO / EUIPO / TÜRKPATENT / WIPO]
**Filing Class**: [Nice Classification]

## Creation Workflow

This brand identity was developed through a hybrid human-AI workflow:

1. **Creative Direction**: [Human designer/team name]
   - Brand strategy, route selection, concept direction, 
     style anchor selection, color palette decisions
     
2. **Initial Concept Generation**: AI image generation tools
   - Primary models: Nano Banana 2 (Gemini 3.1 Flash Image), 
     Grok Imagine Aurora-2
   - Generation count: [X iterations across Y generations]
   - Human-authored prompt (UMMP): [brief description]

3. **Human Refinement**: 
   - Vector rebuild in Adobe Illustrator / Inkscape
   - Pen Tool manual curve restoration
   - Node optimization
   - Optical correction (specific calibrations noted in process log)
   - Color harmonization
   - [Estimated Z hours of human work]

4. **Final Human Decisions**: 
   - Color palette locked: [HEX values + Pantone references]
   - Typography locked: [Font family + weights]
   - Grid system locked: [Dimensional specification]
   - Adaptive rules (if Route 4): [Core spine definition]

## Content Credentials (C2PA)

Full provenance available at:
- Manifest JSON: [URL or attached file]
- Chain: [List of transformations with timestamps]

## Copyright Position

The submitted logomark represents **significant human creative authorship** 
with AI as a tool for initial concept generation. Per USPTO 2025 guidance 
/ EU AI Act provisions / SMK 6769, copyright eligibility is claimed based 
on human selection, arrangement, and transformation of AI-generated 
elements into a final work bearing original human creative choices.

**Signed**: [Brand representative + date]
```

## Adım 5.11 Output Template

Final brand identity report'un 5.11 bölümünde üretilen yapı:

```markdown
## 5.11 C2PA Content Credentials & AI Provenance

### Provenance Chain Dokümantasyonu

**Üretim Katmanı**:
- Model: Nano Banana 2 (Gemini 3.1 Flash Image, preview)
- Generation date: [YYYY-MM-DD]
- UMMP prompt (canonical): "[quoted]"
- Iterations: [N rounds of conversational refinement]
- SynthID watermark: ✓ (invisible, embedded)
- C2PA manifest: ✓ (auto-generated by model)

**Dönüşüm Katmanı**:
- Vector conversion: [vtracer / Illustrator / manual Pen Tool hybrid]
- Manual cleanup time: [approx. hours]
- Node count: [pre-cleanup X → post-cleanup Y]
- Metadata preservation: ✓ (C2PA manifest transferred to SVG <metadata>)

**Yayın Katmanı**:
- Primary asset: logo.svg (canonical, with embedded C2PA)
- Secondary assets: logo.png (various sizes, manifest retained)
- Public Content Credentials viewer URL: [brand.com/content-credentials]

### EU AI Act Disclosure Statement
[Tier 1 / Tier 2 / Tier 3 template uygulanmış]

### Trademark Strategy Package
- **Jurisdiction**: [USPTO / EUIPO / TÜRKPATENT / WIPO Madrid]
- **Nice Class**: [X]
- **Package contents**: [liste, bu dosyadaki template'e göre]
- **Filing date target**: [YYYY-MM-DD]
- **Human authorship evidence**: [summary]

### AI Disclosure in Brand Book
Yer: Brand book appendix + website footer + press release boilerplate
Content: [20-50 kelime clean disclosure text]

### C2PA Tooling Recommendations
- **Adobe Creative Suite 2026**: Native support, default on
- **c2patool (CLI)**: Open-source, available for CI/CD pipelines
- **Content Credentials Cloud**: Public verification URL (optional but recommended)
- **Figma C2PA plugin**: [status — beta 2026]

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|:-:|:-:|---|
| Metadata strip during export | Medium | High | Use C2PA-native tools; avoid legacy image editors |
| Third-party asset reuse without credentials | High | Medium | Partner/vendor contracts require C2PA preservation |
| Trademark challenge citing AI authorship | Low | High | Comprehensive human authorship record |
| EU AI Act non-compliance | Medium | High | Tier 2/3 disclosures on all public campaign assets |
| Brand assets stripped of provenance in social reposts | High | Low | Original assets on brand.com with full credentials |

### Governance
- **Provenance Manager** (role): [Designated person / team]
- **Quarterly provenance audit**: [Process]
- **New asset onboarding**: [C2PA checklist before any brand asset publishes]
```

## Kritik Uyarılar

### 1. Metadata Stripping
Sosyal medya platformları (Instagram, Twitter, Facebook) tarihi olarak **EXIF + metadata strip** ediyor. 2026 itibariyle:
- **Instagram / Meta**: C2PA preservation **pilot** (genişleme bekleniyor)
- **Twitter / X**: C2PA desteği **sınırlı**
- **LinkedIn**: C2PA desteği **yok** (2026 itibariyle)
- **TikTok**: C2PA desteği **sınırlı**

**Mitigation**: Original assets **brand.com'da tam credentials** ile. Social posts **ikincil** kopyalar. Link-back to verified original.

### 2. Transformation Chain Fragility
Her dönüşüm (crop, resize, color adjust) **manifest'e eklenmeli**. C2PA-uncompliant tool kullanımı zinciri kırar. **Disiplin**: Adobe 2026+ tools + c2patool CLI sadece.

### 3. Client Education Gap
Pek çok marketing/design partner C2PA'yı bilmiyor. Brand guideline'a **"C2PA preservation mandatory"** clause'u ekle. Vendor onboarding'de training yap.

### 4. Public Verification UI
Content Credentials Cloud'a upload edilmezse kullanıcılar metadata'yı inspecte edemez. Public verification URL best practice.

## Mahir Domain Özel: Pharma C2PA

Pharma markalar için C2PA özellikle kritik (regulatory overlay):

- **EMA / FDA / TİTCK görsel materyal submissions**: Provenance dokümantasyon zorunlu (bazı jurisdiction'larda 2026)
- **Promotional materials** (GPP3 uyumu): AI-assisted visuals için tam disclosure
- **Clinical trial materials** (investigator brochures, patient-facing content): C2PA preservation zorunlu — "bu data-visualization AI ile üretildi, hastaya gösteriliyor" = trust layer
- **Regulatory compliance layer**: TİTCK, SGK, MEDULA submissions — AI-assisted materyal disclosure template'i Türkiye bağlamında henüz kodifiye değil ama AB uyumu öngörülüyor

**Pratik tavsiye**: Roche / Era Pharma / ozlemmurzoglu.com gibi Mahir projelerinde **tüm** brand identity deliverables C2PA manifest ile — hem EU AI Act compliance hem de 2026-2028 arası beklenen Türkiye regulatory harmonization için proaktif hazırlık.

---

> **Kapanış doktrini**: C2PA, markanızın **görünürdeki imzası** olmaktan çıkıp **görünmez ama doğrulanabilir omurgası** hâline geldi. 2026'da markalar "biz AI kullandık" demenin utanacağı bir şey değil — aksine **şeffaflığın, etik duruşun, professional disiplinin** işareti. Brand identity sadece bir logo üretmek değil, **bu logonun nereden geldiğini** belgelemek artık işin parçası.
