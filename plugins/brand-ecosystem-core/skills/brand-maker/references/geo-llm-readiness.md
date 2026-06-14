# GEO-LLM Readiness — Brand Naming in the Age of Agentic AI

> **On-demand load.** AI/SaaS/Tech/Web3 briefs, born-global rebrands, ve LLM-mediated search içinde gelecek keşfedilebilirliğin önemli olduğu her brief için.

---

## 1. Paradigma: Keşif Katmanının LLM'e Kayması

2025 Gartner raporuna göre çevrimiçi aramaların **%58'i AI-üretimli özet** veya doğrudan cevap içeriyor. Bu, markanın keşfedilme mekaniğini temelden değiştirir:

- **Eski dünya (1998–2023)**: SEO → Google 1. sayfa → click-through → conversion
- **Yeni dünya (2024+)**: GEO → LLM cevap içinde cite → direct recommendation → conversion (genelde zero-click)

Princeton, Georgia Tech ve Allen Institute for AI'ın 2024 çalışması, GEO-optimize edilmiş içeriğin AI-üretimli cevaplarda **%40'a kadar daha yüksek görünürlük** elde ettiğini belgeledi. Bu, markanın keşfedilebilirliğinin yeni zemini.

### LLM as Stakeholder

Hootsuite Kıdemli Pazarlama Direktörü Ryan Smith'in 2026 formülasyonu: *"LLM'leri markanın yeni bir paydaşı gibi düşünmeliyiz — markanın görünürlüğünü, itibarını, değerlendirilmesini ve satın alma kararlarını giderek daha fazla yönlendiren son derece etkili bir paydaş."*

Bu, `brand-maker` için şu demektir: **bir isim, insan zihninde pozisyon kazanmanın yanında LLM'in knowledge graph'ında temiz bir slot işgal etmek zorundadır.**

---

## 2. Taksonomi: GEO vs SEO vs AEO vs LLMO

Endüstri henüz tek terim üzerinde anlaşamadı. Aynı konsepti 4 farklı şekilde adlandırıyor:

| Terim | Açılım | Vurgu |
|---|---|---|
| **GEO** | Generative Engine Optimization | İçerik AI-üretimli cevaplarda **cite** edilmek |
| **AEO** | Answer Engine Optimization | Cevap motorunda **seçilmek** |
| **LLMO** | Large Language Model Optimization | LLM çıktılarında **görünmek** |
| **AI SEO** | AI Search Engine Optimization | AI search içinde **sıralamak** |

`brand-maker` skill'i GEO terminolojisini benimser — en yaygın ve academically desteklenmiş.

---

## 3. Query Fan-Out Mekaniği

AI-üretimli cevap üretimi **tek sorgu → birden çok sub-query** mantığıyla çalışır:

```
Kullanıcı: "En iyi B2B AI agent platformu?"
       ↓
LLM internal fan-out:
    - "B2B AI agent platform 2026"
    - "AI agent platform enterprise features"
    - "developer-friendly agent platform"
    - "AI agent platform pricing comparison"
       ↓
Her sub-query için RAG retrieval
       ↓
Multi-source synthesis + brand citations
       ↓
Kullanıcıya tek cevap
```

Bu mekanik, **marka ismi**nin her sub-query'de **semantic clarity** sağlaması gerekliliğini doğurur. İsim belirsizse, LLM "acaba X mi Y mi?" ikilemi yaşar ve **atlar**.

---

## 4. İsim Düzeyinde LLM-Discoverability — 4 Kriter

### 4.1 Entity Clarity

İsim tek bir entity'ye mi işaret ediyor?

- **Kötü**: "Arc" (browser vs Arc hotel chain vs Arc Teryx outdoor brand) — LLM ambiguity
- **İyi**: "Perplexity" (tek yüksek-tanınırlık entity — AI search company)
- **Mükemmel**: "Anthropic" (coined, benzersiz)

### 4.2 Knowledge Graph Presence

- Wikipedia article olasılığı yüksek mi?
- Wikidata QID taşıyabilir mi?
- Crunchbase profile-friendly mi?

### 4.3 Citation-Friendliness

LLM'in isimden hangi metadata'yı hızla çıkarabildiği:
- Company founded (year)
- Primary category
- Headquarters / founders
- Product/service description
- Distinctive attributes

İsim bu metadata'ya **kancalanabilir** olmalı — rastgele karakter dizisi (ör. "Xyzqrtl") metadata taşımaz, dolayısıyla LLM citation yapamaz.

### 4.4 Hallucination Resistance

LLM'in isimden yanlış bilgi üretme olasılığı ne kadar düşük?

- Jenerik isimler (Arc, Claude, Cursor) yüksek hallucination riski taşır — LLM başka bir Arc/Claude/Cursor ile karıştırır
- Distinctive coined isimler (Anthropic, Perplexity, Vercel) düşük risk

---

## 5. 4-LLM Probe Protokolü

`llm_namespace_probe.py` scripti her finalist için aşağıdaki 3 prompt'u 4 LLM proxy'ye gönderir (web_search üzerinden public surface):

### 5.1 Prompt Templates

**Prompt 1**: `What is [NAME]?`
**Prompt 2**: `[NAME] company`
**Prompt 3**: `Tell me about [NAME] in [CATEGORY]`

### 5.2 4 Proxy LLM

1. **ChatGPT proxy** (OpenAI search surface)
2. **Claude proxy** (Anthropic search surface)
3. **Gemini proxy** (Google AI search)
4. **Perplexity proxy** (Perplexity search)

### 5.3 Response Classification

Her LLM yanıtı 4 sınıftan birine atanır:

- **Clean**: "I don't have information about a company/brand called [NAME]" — temiz namespace
- **Ambiguous**: Birkaç low-prominence entity'ye işaret eder
- **Collision**: Yüksek-tanınırlık tek entity (skill'e bağlı olarak iyi veya kötü)
- **Hallucination magnet**: 4 LLM tutarsız yanıt verir (aynı prompta farklı entity'ler)

### 5.4 Aggregate Skoru

- 2 puan: 4/4 Clean veya 3/4 Clean + 1 low-prominence
- 1 puan: 2/4 Collision/Ambiguous
- 0 puan: 3+/4 Collision veya Hallucination magnet

---

## 6. Karar Matrisi — Hangi Brief'te Hangi Eşik

| Brief Tipi | Minimum GEO Skor | Gerekçe |
|---|---|---|
| Greenfield startup | 1/2 | Marka ekuitisini sıfırdan inşa edebilir |
| B2B SaaS | 2/2 | Enterprise müşteri LLM aracılığıyla keşfedecek |
| Consumer DTC | 1-2/2 | Sosyal medya + LLM recommendation mix |
| **Pharma launch** | **2/2** | **FDA REMS + pharmacovigilance LLM-okur; hallucination yüksek maliyet** |
| Rebrand | 2/2 | Eski brand equity taşınmalı, yeni namespace sorunsuz olmalı |
| M&A / IPO öncesi | 2/2 | Due diligence LLM disinformation riski |

---

## 7. Örnek Vaka Analizleri

### 7.1 "Claude" naming retrospect — Anthropic namespace yönetimi

- **Challenge**: "Claude" = common French name (Claude Debussy, Claude Monet) + ambiguous
- **Strategy**: Anthropic, çok hızlı SEO + paid search + academic paper references yayarak LLM training data'sına "Claude = AI assistant" bağını yerleştirdi
- **Outcome**: 2024 itibariyle ChatGPT + Gemini + Perplexity, "Claude" sorgusunu doğru şekilde Anthropic'e bağlıyor
- **Ders**: Ambiguous namespace bile **aktif SEO+GEO discipline** ile fethedilebilir

### 7.2 "Groq" vs "Grok" — Homophonic LLM Collision

- Groq (AI inference chip company, kurulma 2016)
- Grok (Elon Musk / xAI chatbot, launch 2023)
- Homofonik, LLM'ler sık karıştırıyor
- **Ders**: Yakın fonetik rakip, LLM namespace'te disaster; probe test ile erken tespit

### 7.3 "Arc" Browser — Generic Kelime Zorluğu

- Arc (The Browser Company, 2022)
- "Arc" = common word (arc = yay/ark), ayrıca Arc Hotel, Arc'Teryx outdoor, Joan of Arc
- LLM yanıtları genelde "Which Arc?" gerilimi yaşıyor
- **Strategy**: The Browser Company, "Arc Browser" tam name + distinctive visual identity ile LLM disambiguation sağlıyor
- **Ders**: Generic kelime seçilirse **context signifier** (Browser, Search) ile pekiştirilmeli

### 7.4 "v0" by Vercel — Minimalist İsim Riski

- v0 (Vercel'in AI UI generator, 2023)
- "v0" = too minimal for LLM to treat as entity
- Wikipedia "v0" article yok; LLM'ler "Vercel v0" tam formla çağırıyor
- **Outcome**: Vercel brand gücü v0'ı taşıyor; ama standalone v0 LLM namespace zayıf
- **Ders**: Minimalist isim parent brand güçlüyse ok; greenfield'de risk

### 7.5 "Perplexity" — Semantic Disambiguation Mastery

- Perplexity (AI search, 2022)
- "Perplexity" = entelektüel kelime, 1 tam-tanınırlık entity
- LLM'ler doğrudan AI search context'ine bağlıyor
- **Ders**: Distinctive kelime + distinctive category = LLM namespace ideal

---

## 8. Skill Çağrısı Protokolü

```bash
# Basic probe (4 LLM × 1 prompt per finalist)
python /mnt/skills/user/brand-maker/scripts/llm_namespace_probe.py "Finalist1"

# Deep probe (4 LLM × 3 prompts per finalist) — pharma/rebrand brief için
python /mnt/skills/user/brand-maker/scripts/llm_namespace_probe.py --deep "Finalist1"

# Machine-readable JSON output
python /mnt/skills/user/brand-maker/scripts/llm_namespace_probe.py --json "Finalist1"
```

Script çıktısı Post-Digital Scorecard Eksen 1'e yazılır.

---

## 9. Brand-Discovery Checklist (v2.0)

Finalist seçildikten sonra, brand launch öncesi 6 aylık GEO hazırlığı:

1. **Wikipedia article** draft (notability kriterleri karşılandığında)
2. **Wikidata QID** assignment + interlanguage links
3. **Crunchbase profile** + structured company data
4. **LinkedIn company page** + founder profiles
5. **Industry publication coverage** (Techcrunch, Fiercepharma, Endpoints, etc.) — LLM training data source
6. **Structured data markup** (Schema.org Organization, Product)
7. **llms.txt** file (emergent standard 2025+)
8. **Knowledge graph consistency** across all sources (founding date, HQ, product description)

`brand-maker` raporunda Section 7 "Sonraki Adımlar" bu checklist'i Mahir'in hedef brief'ine göre uyarlayabilir.

---

## 10. Kaynaklar

- Liu, P., et al. (2024). "Generative Engine Optimization: A Study of Content Visibility in AI-Generated Responses." Princeton University / Georgia Tech / Allen Institute for AI joint publication.
- Gartner. (2025). *Generative AI in Search: Forecast and Strategic Implications*.
- Kenny, G. & Ramsey, K. (2026, March). "LLMs Are Overtaking Search: Here's How to Adjust Your Online Presence." *Harvard Business Review*.
- Smith, R. (Hootsuite). (2026). "LLM Visibility: What It Is and How to Track It in 2026." Hootsuite Blog.
- Adobe. (2026, April). "Adobe Introduces Brand Visibility Solution: LLM Optimizer at Adobe Summit 2026." Adobe News.
- Interbrand. (2026). *Best Global Brands 2026 Report — Agentic AI Era*.
