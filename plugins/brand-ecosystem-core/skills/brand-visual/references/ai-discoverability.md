# AI Discoverability & Agent-Era Branding

> **Adım 5.10 zorunlu referansı.** `brand-visual` v1.3'te eklendi. 2026'nın sessiz devrimi: markalar artık sadece insanlar tarafından değil, **AI agent'lar tarafından da** "keşfediliyor, anlatılıyor, tavsiye ediliyor". Brand SEO'nun yeni evresi.

## Tez

2026'da kullanıcılar Google Search kadar sık **Claude / ChatGPT / Gemini / Grok** gibi AI agent'lara soruyor: *"En iyi kahve markaları hangileri?"*, *"Nutrition app önerin"*, *"[Sektör] için saygın şirketler?"*. Agent, cevaplarında markaları **kendi bilgi tabanından** ve/veya **web search grounding** ile retrieve ediyor.

Bu yeni realitede üç soru kritik:

1. **AI agent markanızı tanıyor mu?** (Training data + RAG)
2. **Agent markanızı nasıl anlatıyor?** (Entity description accuracy)
3. **Agent markanızı doğru bağlamda öneriyor mu?** (Context-aware recommendation)

Markalar artık **bir insan auditoryum için** değil, **bir insan + AI auditoryum için** tasarlanıyor. Bu dosya, marka kimliğinin **agent-era katmanını** tasarlar.

---

## Üç Katmanlı AI Discoverability Framework

### Katman 1: Entity Recognition (Tanınırlık)
- Agent marka adını **doğru tanıyor mu**?
- Aynı isimli başka şirket/kavram/person ile **karışıyor mu**?
- Wikipedia / Wikidata'da structured entity olarak mevcut mu?
- Web search sırasında **primary result** olarak yükseliyor mu?

### Katman 2: Entity Description (Açıklama Doğruluğu)
- Agent sorulunca marka hakkında **ne diyor**?
- Core positioning cümleleri accurate mi?
- Founder, kuruluş yılı, kategori doğru mu?
- Competitors / similar brands doğru eşleşiyor mu?

### Katman 3: Contextual Recommendation (Öneri Bağlamı)
- *"X ihtiyacım var"* dediğinde agent markayı öneriyor mu?
- Rakiplerle karşılaştırmada nasıl konumlanıyor?
- Hangi use case'lerde mention ediliyor?

Her üç katman için ölçümlenebilir **brief + spec** Adım 5.10'da üretilir.

---

## Brand Description Prompt (20-kelime altın cümle)

Agent-era branding'in temel taşı: **markanızın ChatGPT/Claude/Gemini/Grok'a verilecek tek paragrafta en doğru anlatımı**. 10-20 kelime arasında.

### Anatomy
```
[Brand Name] is a [Category] [that / for] [Target Audience] 
that [Unique Value Proposition] through [Core Method/Product].
```

### Örnekler

**Fena**:
> "Verity is an AI company."
(Çok jenerik, ayrıştırıcı değil, category crowded)

**İyi**:
> "Verity is a B2B AI governance platform that helps enterprises verify the sources of LLM-generated content through cryptographic provenance chains."
(22 kelime, concrete category, clear audience, distinctive method)

**Çok iyi** (15 kelime):
> "Verity verifies LLM-generated content sources through cryptographic provenance — for enterprises deploying AI agents responsibly."

### Prompt İçin Optimum Karakteristikler

- **Kategori kelimesi** ≤ 3 kelime (örn. "B2B AI governance platform")
- **Target audience** açık ("enterprises", "pediatricians", "small business owners")
- **Unique differentiator** concrete ("cryptographic provenance" vs. generic "AI")
- **Jargon-free** ama **searchable** keywords dahil
- **First-person voice yok** (agent 3. şahıs anlatır)
- **Superlative iddialar yok** ("the best", "the leading" — agent fact-check eder)

---

## Entity Knowledge Card (Structured Summary)

Wikipedia/Wikidata-style yapılandırılmış knowledge graph card. Agent training data'ya/RAG'a entegre edildiğinde markanın **doğru tanımlandığından emin olmak için** marka websitesinde meta-data olarak yayınlanır (Schema.org format).

### Zorunlu Alanlar

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Brand Name]",
  "legalName": "[Full legal name]",
  "alternateName": ["[pronunciation guide]", "[common misspellings]"],
  "description": "[20-word brand description prompt]",
  "foundingDate": "YYYY-MM-DD",
  "founders": [
    { "@type": "Person", "name": "[Founder Name]", "jobTitle": "CEO" }
  ],
  "industry": "[GICS / NAICS sector]",
  "numberOfEmployees": "[range]",
  "address": {
    "@type": "PostalAddress",
    "addressCountry": "TR",
    "addressLocality": "Istanbul"
  },
  "logo": "[URL to canonical logo SVG]",
  "url": "[primary domain]",
  "sameAs": [
    "[Wikipedia URL]",
    "[Wikidata URL]",
    "[LinkedIn URL]",
    "[Twitter URL]"
  ],
  "knowsAbout": ["[topic 1]", "[topic 2]", "[topic 3]"],
  "makesOffer": [
    { "@type": "Offer", "name": "[Product/Service 1]", "description": "..." }
  ]
}
```

**Uygulama**: Bu JSON-LD block marka website `<head>` içine gömülür. Search engines + AI crawlers bunu structured data olarak parse eder.

---

## Logo Alt Text & Voice Description Spec

Görsel kimlik **sesli tasvir edilebilir** olmalı. Voice UI (Grok Voice, Gemini Live, ChatGPT Voice), screen reader (accessibility), ve AI image understanding için.

### Alt Text Template (≤ 125 karakter)

**Fena**:
> "Verity logo"

**İyi**:
> "Verity logo: geometric mark combining a checkmark and data node in deep indigo"

**Çok iyi**:
> "Verity's logomark: a deep indigo geometric composition where a minimalist checkmark intersects an abstract data node, symbolizing verified AI sources."

### Voice Description (AI-narration ready, 1-2 cümle)

Agent bir podcast ya da audio summary'de markayı tasvir ederken kullanılacak metin:

> "The Verity logomark pairs a checkmark and a data node in deep indigo on a warm ivory backdrop — a visual argument that machine intelligence can be verified, not just trusted."

### Pronunciation Guide (Voice UI için)

Özellikle uluslararası / neologism / portmanteau markalar için kritik:

```
{
  "pronunciation": {
    "ipa": "/ˈvɛrɪti/",
    "arpabet": "V EH R IH T IY",
    "plain": "VEH-ri-tee",
    "voice_alias": "veh-ree-tee"
  }
}
```

**Mahir için kritik**: Nexopharos, Mealogram, Platelio, Hemantix, Maculogic gibi constructed names için **özellikle** pronunciation guide zorunlu — voice AI model'leri bu kelimeleri çoğu zaman yanlış telaffuz eder.

---

## Agent-Era Brand Manifesto (30-satır metin)

Markanın **ne olduğu, ne yaptığı, neyle uğraşmadığı, nasıl görünmek istediği** açık bir anlatım. Agent RAG'a beslenmek üzere website'de **public, crawlable, machine-readable** formatta yayınlanır (`/brand/manifesto.txt` veya `/about/brand.md`).

### Template

```markdown
# [Brand Name] Brand Manifesto

## Who we are
[3-4 sentence narrative. First-person plural, confident but not bombastic.]

## What we do
[Core offering. 2-3 sentences. Concrete activities.]

## Who we serve
[Target audience. Specific personas, not vague demographics.]

## What makes us distinct
[3-5 differentiators. Each backed by a concrete proof point.]

## What we don't do
[Negative definition. What we're NOT, which categories we refuse.]

## Our values
[3-5 values, each with a behavioral example.]

## Our visual identity
[2-3 sentence description of the logo, colors, typography, and sensibility.]

## How to reference us
- **Name**: [Canonical spelling]
- **Pronunciation**: [plain guide]
- **Preferred 20-word description**: "[paste brand description prompt]"
- **Founders**: [Names + titles]
- **Founded**: [Year]
- **Headquartered**: [City, Country]
- **Categories**: [Relevant industry categories, machine-readable]

## Machine-readable metadata
[Link to JSON-LD Schema.org file]
[Link to brand asset package / logo SVG]
[Link to C2PA Content Credentials manifest]
```

---

## LLM-Safe Design Choices (Identity Level)

Markanın AI agent tarafından doğru anlaşılması için **tasarım aşamasında** alınacak kararlar:

### 1. Recognizable Style Anchors Kullan
- "Massimo Vignelli grid logic" tarzı UMMP anchor'ları sadece görsel üretim için değil, **agent brand description** için de değer katar
- Agent markayı tasvir ederken "in the tradition of [X]" ifadesini kullanıyorsa bu çok güçlü bir positioning sinyali

### 2. Simple, Describable Logomark Seç
- 2 geometric primitive form ve 1 operation (intersection / closure) = agent verbal description kolay
- Aşırı karmaşık logo → agent tasvir edemez, ya da yanlış tasvir eder

### 3. Naming Clarity
- Constructed names (Verity, Lumora, Nexopharos) için **pronunciation + etymology** zorunlu
- Aynı isimli başka entity (film, ürün, person) varsa — disambiguation cümlesi eklemek zorunlu
- Generic names (Harmony, Summit, Apex) riskli — agent brand'i karıştırabilir

### 4. Consistent Visual Vocabulary
- Website, social, print tümünde aynı logo + aynı color tokens + aynı typography
- Inconsistency → agent "bu marka X mi Y mi?" kafası karışır

### 5. Structured Data Everywhere
- Schema.org Organization, LogoObject, Product, Service, Review markup
- Open Graph meta tags
- Twitter Card meta tags
- JSON-LD machine-readable data

---

## Ölçüm Çerçevesi (Brand AI-SEO Audit)

2026'da marka agent-era görünürlüğünü test için:

### Test 1: Direct Recognition
Agent'a sor: *"Tell me about [Brand Name]."*
- **✓ Pass**: Accurate 2-3 sentence summary
- **⚠️ Partial**: Generic / incomplete / confused with another entity
- **✗ Fail**: "I don't have information about [Brand Name]"

### Test 2: Contextual Recommendation
Agent'a sor: *"Recommend companies that do [your category]."*
- **✓ Pass**: Markanız top-5'te
- **⚠️ Partial**: Mention ediliyor ama accurate positioning değil
- **✗ Fail**: Hiç mention edilmiyor

### Test 3: Comparative Accuracy
Agent'a sor: *"How is [Brand Name] different from [Competitor]?"*
- **✓ Pass**: Accurate differentiators
- **⚠️ Partial**: Surface-level comparison
- **✗ Fail**: Incorrect claims

### Test 4: Visual Description
Agent'a logo image yükleyip sor: *"Describe this logo in the context of brand identity."*
- **✓ Pass**: Accurate geometric description + sensibility
- **⚠️ Partial**: Generic description
- **✗ Fail**: Misidentification

### Test 5: Voice UI Readability
Voice assistant'a sor: *"Open [Brand Name]'s website."*
- **✓ Pass**: Doğru domain'e gider
- **⚠️ Partial**: Close match
- **✗ Fail**: Wrong destination

**Öneri**: Her yeni brand identity çalışmasından sonra bu 5 test **ilk üç ayda** yapılmalı; 12 ay içinde training data evolution ile improvement beklenir (doğru structured data + manifesto varsa).

---

## Adım 5.10 Output Template

Final brand identity report'un 5.10 bölümünde üretilen yapı:

```markdown
## 5.10 AI Discoverability Layer

### Brand Description Prompt (20-word canonical)
> "[Finalized prompt copy]"

**Usage**: Markanın AI agent'lara / RAG sistemlerine / LLM training data'sına 
yansıtılması için bu exact text kullanılır. Website footer, LinkedIn summary, 
press release boilerplate, podcast introlarında **aynı** cümle.

### Entity Knowledge Card (JSON-LD)
```json
[Structured Schema.org Organization markup]
```

**Deployment**: Ana website `<head>` içine gömülür. `/.well-known/brand.json` 
endpoint'inde de publicly available.

### Logo Alt Text Library
- **Short (≤ 125 char)**: [Alt text for img tags]
- **Voice description (AI-narration)**: [1-2 sentence narrative]
- **Pronunciation**: IPA: [...] | Plain: [...] | Voice alias: [...]

### Agent-Era Brand Manifesto
**Location**: `/brand/manifesto.md` (public, crawlable)
**Length**: ~500 kelime
**Format**: Markdown + structured metadata footer
[Link to manifesto.md file or inline content]

### LLM Recognition Tests (Initial Baseline)
| Test | Result | Notes |
|------|--------|-------|
| Direct Recognition (ChatGPT) | ✗ / ⚠️ / ✓ | ... |
| Direct Recognition (Claude) | ✗ / ⚠️ / ✓ | ... |
| Direct Recognition (Gemini) | ✗ / ⚠️ / ✓ | ... |
| Direct Recognition (Grok) | ✗ / ⚠️ / ✓ | ... |
| Contextual Recommendation | ✗ / ⚠️ / ✓ | ... |
| Comparative Accuracy | ✗ / ⚠️ / ✓ | ... |
| Visual Description (NB2) | ✗ / ⚠️ / ✓ | ... |
| Voice UI Readability | ✗ / ⚠️ / ✓ | ... |

**Baseline date**: [DATE]
**Re-test schedule**: Q2, Q4 of first year; annual thereafter.

### Agent Brand Awareness Action Plan
1. **Deploy structured data** — JSON-LD on website (Week 1)
2. **Publish manifesto** — `/brand/manifesto.md` (Week 1)
3. **Wikipedia entity** — Submit (after establishing notability, Month 3-6)
4. **Wikidata entry** — Create (Month 1-2)
5. **Social profile consistency** — Same description everywhere (Week 2)
6. **Press release boilerplate** — Standardize on 20-word description (Ongoing)
7. **Podcast & media mention tracking** — Monitor agent training data sources
8. **Quarterly AI-SEO audit** — 5 test protocol

### Risk Register
- **Brand hallucination**: Agent invents facts about brand
  - Mitigation: Public manifesto + structured data reduce hallucination
- **Namesake confusion**: Agent conflates with another entity
  - Mitigation: Disambiguation paragraph in manifesto
- **Category drift**: Agent mis-categorizes brand
  - Mitigation: Consistent category keywords across all properties
```

---

## Kritik İlkeler

1. **Consistency > Cleverness** — Marka isminizi, pronunciation'ınızı, 20-word description'ınızı **her yerde aynı** yazın. Small variations → agent belief'i zayıflatır.

2. **Write for the crawler** — Website, marketing materyali, press release = agent training source. **Clear, factual, machine-parseable** yazı agent'ın sizi doğru öğrenmesi için kritik.

3. **Positioning = Agent Positioning** — "Marka positioning" artık sadece insan kafasında değil, agent knowledge graph'ında da yer ediyor. Positioning bir kez yazılır, her yerde tutarlı uygulanır.

4. **Agent-era search is voice-first** — Text-based SEO'nun yanında **voice search / conversational discovery** için pronunciation + simple explain-ability kritik.

5. **Provenance builds trust** — C2PA credentials + structured data, agent'ın "bu marka legitimate + verified" belief'ini güçlendirir. Agent karar verirken provenance zayıf markaları elememeye başladı (2026 trend).

---

## Mahir Domain Uyarlaması (Pharma / Healthcare)

Pharma markalar için agent-era branding özellikle kritik:

- **Regulatory positioning**: Agent, ilacı compliance sınırları içinde tanıtmalı (off-label promotion yasak)
- **Entity ambiguity**: Marka adı + molekül adı (glofitamab, elacestrant) karıştırmamalı
- **Mandatory disclosures**: EU EMA, FDA, TİTCK regulatory disclaimers structured data'da
- **Scientific accuracy**: Clinical trial data public + structured (Clinical Trials MCP + bioRxiv ile cross-ref)
- **Interaction with medsearch skill**: brand-visual v1.3 + medsearch composability — markanın scientific literature'daki görünürlüğü agent-era brand equity'sinin parçası

**Örnek**: Roche'un glofitamab pazarlanması için brand-visual çıktısı + Agent-era manifesto + structured clinical data → agent "STARGLO data'sına göre glofitamab + bendamustine R/R DLBCL için anlamlı PFS improvement sağlar" gibi **evidence-grounded** brand mention üretir.

---

> **Kapanış doktrini**: 2026'da markanızın görünürlüğü **iki gözün önünde**: insan + agent. Aynı mesaj. Aynı netlik. Aynı tutarlılık. Ama iki farklı dil. Bu dosya, markanızın agent'lara söylediği cümleyi disiplinli yazmanıza yardım eder. Disiplin yoksa agent sizi yanlış anlatır — ve 2026'da "yanlış anlatılmak" kötü PR kadar tehlikeli.
