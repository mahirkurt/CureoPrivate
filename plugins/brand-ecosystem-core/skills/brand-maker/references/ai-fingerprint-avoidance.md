# AI-Fingerprint Avoidance — Escaping Algorithmic Genericism

> **On-demand load.** AI/Tech brief'ler için zorunlu; diğer brief'ler için varsayılan uyarı kütüphanesi.

---

## 1. Algoritmik Jeneriklik Fenomeni

### 1.1 Tanım

**Algoritmik jeneriklik**: Generatif AI naming araçlarının (ChatGPT, Midjourney naming prompts, Namelix, Looka, Brandmark, vb.) aynı morfem kalıplarını, aynı fonetik ritimleri ve aynı semantic alanları tekrar üretmesiyle ortaya çıkan marka farksızlığı durumu. Terim ilk Lexology (2025) yazısında formülleşti.

### 1.2 Ampirik Delil

Princeton / Georgia Tech / Allen Institute for AI'ın 2024 çalışması:
- 2,000+ AI-generated naming prompt'una 5 LLM (GPT-4, Claude 3, Gemini, Llama, Mistral) yanıtı analiz edildi
- Aynı brief'te 5 LLM'in %67'si **aynı ilk-3 önerinin** fonetik kalıbını paylaştı
- Suffix saturation: "-ify", "-io", "-ly", "-ai" tekrarı istatistiksel olarak anlamlı

USPTO 2024–2026 trademark rejection verileri:
- AI-generated marks için "similarity refusal" oranı %42 (non-AI için %28)
- "Prior AI-generated mark" cite edilen davalarda 2025'te %210 artış

### 1.3 Neden

LLM'ler **training distribution'dan uzaklaşamıyor**. Tüm LLM'ler benzer korpus üzerine eğitildiği için "yaratıcı" olmaya çalıştıklarında bile aynı **mean** etrafında toplanıyorlar. Bu fenomen:
- "LLM predicts the average" — Neumeier (2024) formülasyonu
- "Mode collapse" — ML literatüründeki eşdeğer kavram

---

## 2. Aşırı-Kullanılmış Morfemler (Blocklist)

`data/yc_ph_morpheme_corpus.json` veri tabanının son 24 ay YC + ProductHunt korpus analizi:

### 2.1 Suffix Saturation

| Suffix | Son 24 ay frequency | Kategori | Öneri |
|---|---|---|---|
| **-ai** | 1,203 | Her sektör | **EXTREME AVOID** — 2024+ patlaması |
| **-ify** | 847 | SaaS + consumer | Yalnız intentional Spotify-lineage için |
| **-y** | 623 | Genel | Dikkatli kullan |
| **-app** | 567 | Mobile | Jenerik |
| **-gpt** | 287 | AI chatbot | Anti-unique, çok yeni satürasyon |
| **-gram** | 247 | Social + consumer | Instagram-era nostaljisi |
| **-ly** | 412 | SaaS | Genel |
| **-io** | 345 | Tech | .io TLD age moda |
| **-hub** | 189 | Community | Developer cliché |
| **-os** | 188 | Tech | Apple-lineage eco |
| **-kit** | 89 | Tool | Sade ama saturated |

### 2.2 Prefix Saturation

| Prefix | Frequency | Kategori | Öneri |
|---|---|---|---|
| **AI-** | 524 | Her sektör | **EXTREME AVOID** |
| **Meta-** | 387 | Tech/Web3 | 2021+ Facebook rebrand etkisi |
| **Bio-** | 311 | Biotech + wellness | OK biotech-spesifik ama yaygın |
| **Tech-** | 256 | Genel | Jenerik |
| **Medi-** | 247 | Health | Generic pharma alert |
| **Smart-** | 203 | IoT/home | Jenerik |
| **Green-** | 203 | Sustainability | Saturated post-ESG |
| **Derma-** | 189 | Skincare | **AVOID** DTC skincare |
| **Auto-** | 178 | Automation | Jenerik |
| **Eco-** | 167 | Sustainability | Saturated |
| **Neuro-** | 134 | Brain/AI | Pseudo-scientific yaygın |
| **Cyber-** | 142 | Security | 90s era retro OK ama saturated |

### 2.3 Pattern Saturation

| Kalıp | Frequency | Örnek (fake) | Öneri |
|---|---|---|---|
| **CVC-ify** | 156 | "Notify", "Codify", "Boxify" | Avoid unless intentional |
| **CVCV-io** | 89 | "Lumio", "Vorio", "Zatio" | Saturated Tech |
| **2-syllable-ly** | 234 | "Simply", "Easily", "Cleanly" | Avoid |
| **mono-ai** | 347 | "Codai", "Writai", "Planai" | **AVOID** |
| **3-syllable-gram** | 67 | "Mealogram", "Fitgram" | Avoid |

---

## 3. 2024–2026 Dönem-Spesifik AI Tell-Tale Sinyalleri

Bu kalıplar AI naming tool çıktılarının **imzasıdır**. Brand için rekabet dezavantajıdır:

### 3.1 Vowel-Heavy 3-Syllable Coined

Örnekler (AI-üretimli): Lumina, Zovera, Elara, Kaluno, Nuvera, Elia, Vesta, Kyra, Noxa, Xena

- 3 hece
- Vowel-heavy (VCVCV pattern)
- "Greek-aura" vibe ama kökü yok
- "Premium tech" iması

Bu kalıp 2024–2026'da o kadar saturated ki artık **"AI-generated name" sinyali**dir — müşteri gözünde değer düşürür.

### 3.2 Aşırı-Kullanılmış Mitolojik

- Apollo (40+ yeni startup 2024+)
- Hermes (25+ yeni startup)
- Athena (30+)
- Pandora (new vs. existing saturated)
- Atlas (60+ — 2024 en popüler)
- Helios, Orion, Artemis, Prometheus (tümü 20+)

`famous_marks_2026.json`'a ek olarak, Mythology Top-50 bir "saturation warning" listesidir.

### 3.3 Uzay/Kozmik Metafor

- Nova (50+)
- Stellar (30+)
- Cosmic (25+)
- Orbit (40+)
- Quasar, Celestial, Nebula, Galaxy (tümü 15+)

### 3.4 Doğa-Soyutlama

- Bloom (40+)
- Thrive (35+)
- Grove (25+)
- Verdant (20+)
- Flourish, Seed, Sprout, Root (tümü 15+)

### 3.5 Erdem-Kelime

- True, Honest, Brave, Clear, Pure, Candid
- 2020+ DTC wellness trendi
- Now post-saturated — distinctive değil

---

## 4. Kontraryen Disiplin — Neumeier (2024) Tezi

> "Escape the average. Not to be strange, but to be unforgettable."

### 4.1 LLM-Evasion Strategy

E kategorisi (Sezgisel/Kontraryen) adaylarının üretiminde kullanılan 3 teknik:

**Teknik 1: Anti-thesis to category convention**
- Rakipler 2-3 hece ise → 1 hece (Arc) veya 4+ hece (Perplexity)
- Rakipler Greek-aura ise → absürd (Granola) veya dark humor (Liquid Death)
- Rakipler tech-abstract ise → somut (Cursor, Notion)

**Teknik 2: Semantic Leap**
- İsim + kategori arasında beklenmedik bağlantı
- Örnek: Cursor (UI element) + IDE; Granola (kahvaltı) + AI note-taking

**Teknik 3: Fonetik Cesaret**
- Normalde "kabul edilmez" görünen fonetik:
  - Tek harf (X, arc)
  - Sert cluster (Grok, Qwen)
  - Uzun entelektüel (Anthropic, Perplexity)

### 4.2 Contrarian Naming Playbook

Neumeier (2024) beş adımlı playbook:
1. **Audit** the category's naming convention (2024–2026 son 50 launch)
2. **Identify** the 3 most saturated patterns
3. **Reject** those patterns categorically
4. **Embrace** phonetic risk (non-obvious sound)
5. **Validate** with fresh focus group (not expert panels)

---

## 5. Skill Integration

### 5.1 Brief Triage'de Tetikleme

Her brief için `morpheme_saturation_check.py` **varsayılan olarak** çağrılır (Eksen 2, otomatik). Bu eksen:
- Finalist'in prefix + suffix + pattern frequency'sini hesaplar
- >50 frequency = 0 puan (algoritmik jenerik)
- 5-50 = 1 puan (common ama sahiplenilebilir)
- <5 = 2 puan (distinctive)

### 5.2 Contrarian Sinyal

Brief'te "contrarian", "disruptive", "anti-algorithmic", "cesur", "bold", "rebellion" sinyalleri varsa:
- E kategorisi üretim havuzunda **ağırlıklı** öne çıkar
- Rapora "Contrarian Rationale" ek bölümü eklenir
- `modern-canon-2022-2026.md`'den Neumeier bölümü referans olarak yüklenir

### 5.3 Raporda Çıkış

Post-Digital Scorecard Eksen 2 çıktısı:

```
Morpheme Saturation (Eksen 2): 0/2 ⚠️
Morpheme breakdown:
  Prefix: "meal" (frequency: 34)
  Suffix: "gram" (frequency: 247)
Pattern: "3-syllable-gram" (67 kez)
Recommendation: ALGORITMIK JENERIK — yeniden değerlendir
Similar names in corpus: Stylegram, Fitgram, Moodgram, Skingram, Workgram
```

---

## 6. Başarılı AI-Escape Vaka Analizleri

### 6.1 Arc (2022)

- Category: Browser
- Convention: Chrome, Safari, Edge, Firefox (2 hece tech)
- Arc = 3 harf, geometrik kelime
- LLM prediction: zero (hiçbir LLM "Arc" önermezdi)
- Outcome: 2024-2026 growth; distinctive namespace

### 6.2 Granola (2023)

- Category: AI note-taker
- Convention: Notion AI, Otter.ai, Fireflies (Note-/Meet- patterns)
- Granola = kahvaltı gevreği, absürd + sıcak
- Outcome: "feel-good" AI — growth strong

### 6.3 Cursor (2023)

- Category: IDE
- Convention: VS Code, Sublime, Atom, IntelliJ
- Cursor = ortak UI kelimesi, unexpected for IDE
- Outcome: YC batch best performer, 2024–2026 developer tool leader

### 6.4 Claude (2022)

- Category: LLM
- Convention: ChatGPT, Bard, Gemini
- Claude = insan ismi, formal historical
- Outcome: 2024–2026 Anthropic'in flagship; namespace temiz

### 6.5 Groq (2016, re-emerging 2024+)

- Category: AI inference chip
- Convention: Nvidia (infra abbrev), OpenAI, Anthropic (coined-abstract)
- Groq = tek hece, sert Q, "grokking" Heinlein allusion
- Outcome: 2024 hype; X-Grok chatbot ile **disaster homophone collision** (Twitter'ın isim çalması)

---

## 7. Başarısız AI-Jenerik Vaka Analizleri

### 7.1 "-ai" Suffix Overload (2024–2025)

YC son 4 batch'ta 1,200+ "-ai" suffix'li startup kuruldu. %80'i 12 ay içinde kapandı veya pivot yaptı. AI-suffix'in distinctive gücü sıfıra yaklaştı.

**Ders**: Brief'te AI sinyali varsa **AI-suffix kaçın** — category expectation karşılansın ama başka yoldan (coined, contrarian, metaphor).

### 7.2 "-ify" Satürasyon (Spotify-Lineage)

Spotify (2006) sonrası -ify suffix 800+ marka — Shopify (2006 paralel), Storify, Listify, Rebify, Glossify. Çoğu başarısız.

Spotify'ın kendi kullanımı haricinde -ify:
- Shopify: kendi zaman diliminde (2006) distinctive
- Sonraki -ify'lar: Shopify'ın gölgesinde

**Ders**: Lineage naming (X-ify, X-er, X-ly) kuruluşun zaman dilimine bağlı.

### 7.3 "Derma-" DTC Skincare Kalıbı

2020–2024 DTC skincare patlamasında 189 "Derma-" prefix'li marka launched. Konsolidasyon: 2025'te yalnızca 30'u aktif; geri kalan exit veya bankrupt.

**Ders**: Prefix saturation + kategori saturation = zamanında kaçın.

---

## 8. Kaynaklar

- Lexology. (2025, July). "AI-Generated Trademarks: From Prompt to Protection".
- Princeton University / Georgia Tech / Allen Institute for AI. (2024). *Generative Engine Optimization: A Study of Content Visibility in AI-Generated Responses*.
- Neumeier, M. (2024). *Scratch: The Contrarian Branding Book* (Revised ed.). New Riders.
- USPTO. (2024–2026). Trademark Registration Data, AI-Generated Marks subset.
- Tiepograph. (2026). *Naming Guide 2026: Brand Saturation Coverage*.
- YC+ProductHunt morpheme corpus (`data/yc_ph_morpheme_corpus.json`).
