---
name: brand-maker
description: >
  Sector-agnostic verbal identity protocol generating 3–5 globally pronounceable,
  trademark-defensible, LLM-discoverable, voice-first brand name finalists for
  any category — B2B SaaS, consumer DTC, fintech, automotive, luxury, FMCG,
  pharma. Five-step methodology: Strategic Decoding → Five-Category Brainstorm
  (A/B/C/D/E) → SMILE+M Lab → Live Domain → Post-Digital Validation (6-axis
  LLM/voice/entity/dilution/morpheme + opt-in regulated-sector checks) →
  Report. Each candidate ships with EN+TR rationale, domain + WIPO trademark
  guidance. Opt-in pharma INN check when pharma signals detected. USE for:
  brand naming, marka ismi, isim önerisi, isim öner, naming brief, startup/
  company/product name, sub-brand, rebrand, "yeni ürün için isim", "şirket
  ismi öner", "marka ismi bul", verbal identity, sözel kimlik, portmanteau,
  coined name, name validation — tech/SaaS/AI/fintech/pharma/DTC/FMCG/luxury/
  automotive/media/fashion naming. Trigger when user describes a venture
  without asking for a name.
---

# brand-maker v2.0 — Global Verbal Identity Protocol (Post-Digital Era)

## Raison d'être

Marka ismi, küresel pazarda zihinde işgal edilen tek ve evrensel bir kelimenin çivisidir. Bu skill, **dünya standartlarında bir isimlendirme ajansı** zekâsını, bilişsel dilbilim disiplini, objektif filtrasyon teknikleri ve **2026 post-dijital gerçekliğine** adapte olmuş doğrulama katmanı ile birleştirir. Yapay zekâ "isim jeneratörlerinin" rastgele ürettiği önerilerden köklü farkı şudur: her isim, **stratejik konumlandırma → fonetik analiz → SCRATCH filtresi → küresel disaster check → Türkçe semantic katman → GoDaddy MCP canlı .com doğrulaması → 6-eksen post-dijital doğrulama → sunum** zincirinden geçirilir.

v2.0 itibariyle skill, markanın **dört ayrı alıcıya** aynı anda hitap ettiğini kabul eder: insan tüketici, Büyük Dil Modeli (LLM), ses asistanı ve bilgi grafiği (knowledge graph). Her alıcı, farklı kriterlerle isim değerlendirir; `brand-maker` bunların tümünü **ölçülebilir** tek bir çıktıda birleştirir.

Bu skill **claude.ai-native** ve **free-tier** çalışır: ücretli API'lere veya ticari trademark veritabanlarına bağımlı değildir. Trademark tarama ve domain müsaitlik kontrolleri için **stratejik tavsiye + manuel doğrulama URL'leri** sunar (USPTO TESS, EUIPO eSearch+, WIPO Global Brand Database, TÜRKPATENT, GoDaddy, Namecheap, Domainr).

### Sektör-Agnostik Mimari Prensibi

`brand-maker`, **herhangi bir sektör** için aynı temel disiplini uygular: B2B SaaS, tüketici DTC, fintech, otomotiv, lüks moda, FMCG, medya, eğitim teknolojisi, gastronomi, konaklama, e-ticaret, oyun, kripto, sanat platformu, içerik markası, hukuk bürosu, danışmanlık, mimarlık, sağlık hizmetleri, pharma — ayırt etmeksizin. Beş-adımlı metodoloji, SMILE+M filtresi, 6-eksen Post-Digital Validation ve bilingual rapor çıktısı **evrensel çekirdek**tir.

Regüle sektörler (pharma, fintech, tütün, alkol, oyun, sağlık hizmetleri) için skill **brief-triggered opt-in modüller** aktif eder. Şu anda canlı olan sektör-spesifik modül:

| Regüle Sektör | Opt-in Modül | Trigger Sinyali | Aktif Olduğunda |
|---|---|---|---|
| **Pharma / Biotech / Medtech** | `pharma-naming-constraints.md` + `inn_stem_collision.py` | "pharma", "ilaç", "FDA", "EMA", "TİTCK", "INN", "molecule" | WHO INN/USAN stem collision check, FDA DMEPA Layer 2 pre-screen, TİTCK Türkçe filtre, Section 4A rapor bölümü |

Brief'te bu sinyal sözcüklerden **hiçbiri** yoksa, pharma modülü **sessizdir**. Örneğin bir tech startup brief'i, consumer DTC brief'i veya lüks moda brief'i için rapor pharma-bilgisi içermez; Post-Digital Scorecard yalnızca 5 eksen (0–10) üzerinden hesaplanır. Gelecekte fintech-constraints, food-beverage-constraints, cosmetics-constraints gibi ek opt-in modüller aynı mimariyle eklenebilir.

Kısaca: **skill sektör-agnostiktir; regülasyon-bilinçlidir.**

---

## Kanonik Kaynaklar (Yetki Tabanı) — v2.0 Genişletildi

Bu skill aşağıdaki klasik + modern metinlerin damıtılmış sentezi üzerine kuruludur. 13 kaynaklı havuz, 1981–2026 döneminin otoriter sesidir:

| Eser | Yazar(lar) | Yıl | Skill İçindeki Rolü |
|---|---|---|---|
| *Positioning: The Battle for Your Mind* | Al Ries & Jack Trout | 1981 | "Power of the Name" doktrini, kategori merdivenleri, anti-paternler |
| *Brand Thinking and Other Noble Pursuits* | Debbie Millman (ed.) | 2011 | Disiplin filozofisi, çok-boyutlu "iyi isim" tanımı |
| *Designing Brand Identity* | Alina Wheeler | 2013 | 7 nitelik filtresi, naming process disiplini |
| *Hello, My Name is Awesome* | Alexandra Watkins | 2014 | SMILE/SCRATCH filtrasyon framework'ü (v2.0: SMILE+M) |
| *Identity-Based Brand Management* | Burmann, Riley, Halaszovich, Schade | 2017 | Sistemik kimlik bileşeni entegrasyonu |
| *Building a StoryBrand* | Donald Miller | 2017 | Rehber–kahraman asimetrisi |
| *Decoding Branding* (1st, 2nd eds.) | Royce Yuen | 2021 / 2024 | Global/Asya pazar perspektifi, kültürel uyarlama |
| *The Ultimate Naming Book* | Cher Murphy | 2023 | 200+ isim tipolojisi katalog derinliği |
| *Brand Naming: The Complete Guide* | Rob Meyerson (Heirloom) | 2024 | AI-integrated naming workflow, human-AI co-pilot doktrini |
| *Scratch: The Contrarian Branding Book* (rev.) | Marty Neumeier | 2024 | Contrarian/gut-feeling damarı (5. kategori E için tez) |
| *Best Global Brands — Annual Trend Reports* | Interbrand | 2024–2026 | Agentic AI shift, credibility-over-visibility tezi |
| *AI + Brand Craft Whitepaper* | Pentagram | 2025 | Human-craft backlash, AI co-pilot metodolojisi |
| *Fluid Identity: Adaptive Brand Systems* | Wolff Olins | 2025 | Kinetic identity, isim modülerliği, SMILE+M tezinin zemini |

---

## ZORUNLU YÜRÜTME PROTOKOLÜ

### Adım 0: Mandatory Reference Load

Her `brand-maker` çağrısının **ilk** eylemi aşağıdaki üç dosyayı yüklemektir. "Progressive disclosure" bu üç dosya için **devre dışıdır**:

```
view /mnt/skills/user/brand-maker/references/positioning-foundation.md
view /mnt/skills/user/brand-maker/references/smile-scratch-filter.md
view /mnt/skills/user/brand-maker/references/output-template.md
```

İlave referanslar **brief'in karakterine göre on-demand** yüklenir (aşağıdaki Routing tablosu).

### Adım 1: Brief Triage ve Reference Routing (v2.0 Genişletildi)

Kullanıcının brief'ini okuyup aşağıdaki tetikleyiciler üzerinden ek referansları yükleyin:

| # | Tetik / Sinyal | Yüklenecek Ek Referans |
|---|---|---|
| 1 | Global/Tech/Web3/SaaS/AI/fintech sektörü, "born-global", "modern", "kısa isim" | `creation-techniques.md` |
| 2 | "Fonetik", "telaffuz", "akıcı", "ritmik", "soft-sounding"; veya çoklu dil hedef pazar | `phonetic-laws.md` |
| 3 | 3+ hedef pazar veya non-Latin alfabe ülkesi (Çin, Japonya, Arap dünyası, Rusya) | `disaster-check.md` |
| 4 | Trademark, hukuki güvence, "tescil", "WIPO", "domain", "URL", ".com", ".io", ".ai" | `domain-trademark-strategy.md` + `godaddy-mcp-integration.md` |
| 5 | "Domain müsait mi", ".com kontrol", "live check" | `godaddy-mcp-integration.md` |
| 6 | Belirsiz / iki+ kategoride benzer isim arıyor | `naming-categories.md` |
| 7 | Somut örnek/"X gibi bir isim" | `exemplar-catalog.md` |
| 8 | Türkiye, Türk pazarı, TR/EU çift lansman, Türk tüketici | `turkish_semantic_check.py` + `disaster-check.md` TR bölümü |
| **9** | **AI/SaaS/Tech/Web3/LLM/chatbot** | **`geo-llm-readiness.md` + `ai-fingerprint-avoidance.md` + `llm_namespace_probe.py` + `morpheme_saturation_check.py`** |
| **10** | **Voice assistant/smart speaker/podcast/voice commerce/Alexa/Siri/DTC audio** | **`voice-first-naming.md` + `asr_simulation.py`** |
| **11** | **Pharma/biotech/medtech/ilaç/FDA/EMA/TİTCK/INN/generic/molecule** | **`pharma-naming-constraints.md` + `inn_stem_collision.py` + `entity_disambiguation.py` (high-precision)** |
| **12** | **Motion/kinetic/animated/dynamic brand/adaptive identity** | **`motion-kinetic-readiness.md`** |
| **13** | **Purpose/sustainability/ESG/impact/değer-odaklı/manifesto** | **`purpose-axis-matrix.md` + `category-creator-protocol.md`** |
| **14** | **Rebrand/renaming/refresh/existing brand** | **Tüm 6 eksen + `morpheme_saturation_check.py` (high precision mode)** |
| **15** | **Contrarian/disruptive/anti-algorithmic/cesur/bold/rebellion** | **`modern-canon-2022-2026.md` (Neumeier Contrarian bölümü)** |
| **Default** | **Herhangi bir brief** | **Eksen 1 (LLM probe) + Eksen 2 (morpheme) + Eksen 4 (entity) otomatik** |

> **Kural**: Şüphe varsa fazla yükle. Regüle sektör tetikleyicileri (Kural 11 pharma, gelecekte fintech/food/tütün vb.) **aktifleştiğinde** karşılık gelen constraint modülü otomatik yüklenir; aksi halde sessiz kalırlar. Pharma kuralı (11) aktifse, brief yüksek regulatory riski gereken bir alan olduğundan ilgili script çağrıları sıkılaştırılır.

### Adım 2: Brief Eksiklerini Tamamla (yalnızca gerekirse)

Brief aşağıdaki **dört zorunlu girdiyi** içermiyorsa, devam etmeden önce **tek bir mesajda** topluca sor:

1. **Sektör / Kategori**
2. **Hedef pazar coğrafyası**
3. **Marka kişiliği / Konumlandırma çıpası**
4. **Tabu / Kısıt**

Brief zaten yeterince zenginse **doğrudan Adım 3'e geç**.

### Adım 3: Beş-Adımlı Ajans Metodolojisini Yürüt (v2.0: 4→5 adım)

Bu, skill'in özüdür. Her adım rapora ayrı bir bölüm olarak yazılır.

#### ADIM 3.1 — Global Stratejik Deşifre

Brief'i global pazar dinamiklerine göre analiz et:

* **Kategori manzarası**: Hangi global kategoride yarışıyor? En büyük 3–5 uluslararası rakip kim?
* **Rakip kelime haritası**: Her rakip zihinde hangi kelimeyi sahiplenmiş?
* **Beyaz alan tespiti**: Rakip kelime havuzunda **boş kalan**, sahiplenilebilir evrensel kavram nedir?
* **Stratejik çıpa**: Önerilecek tüm isimlerin sahiplenmeye çalışacağı **tek kelime / tek duygu**?
* **[v2.0] Purpose-axis coordinate**: (purpose-driven brief'lerde) Utility × Heritage × Rebellion × Craft eksenlerinden hangisi?

> **Ries & Trout doktrini**: "Bir isim, prospect'in zihninde markayı kategori merdiveninin bir basamağına asan kancadır."

#### ADIM 3.2 — Beş-Kategori Bazlı Global Beyin Fırtınası (v2.0: 4→5 kategori)

İsim adaylarını **rastgele üretme**. Onları **beş stratejik kategoriye** ayrılmış olarak üret. Her kategoride **2–3 ismi** öner; toplamda 10–15 aday.

| Kategori | Tanım | Klasik Örnek | Üretim Tekniği |
|---|---|---|---|
| **A. Tanımlayıcı & Metaforik** | Ürünün ne yaptığını veya çağrıştırdığı evrensel metaforu kullanır | Salesforce, Patagonia, Apple, Amazon, Shell, Oracle | Doğa/mit/coğrafya metafor + ürün esansı |
| **B. Sentez & Türetilmiş (Portmanteau)** | İki anlamlı kökü birleştirip yeni kelime üretir | Microsoft, Pinterest, Instagram, Netflix | Kök seçimi → çatı → kısaltma |
| **C. Soyut & Fonetik (Coined)** | Hiçbir dilde anlamı olmayan, saf sesle yaşayan icat-kelime | Kodak, Xerox, Rolex, Sony, Häagen-Dazs | CV-CV-CV ritmi + sert ünsüz çıpa |
| **D. Çağrışımsal & Mitolojik** | Mitoloji, edebiyat, tarih veya doğadan güçlü referans | Nike, Hermes, Tesla, Pandora, Atlas | Arketipsel referans → modern okuma |
| **E. Sezgisel/Kontraryen (YENİ — v2.0)** | Kategori konvansiyonunu bilerek kıran, LLM-öngörüsüzlüğüne dayanan cesur isim | Arc (browser), v0 (Vercel), Granola, Cursor, Claude, Groq, Liquid Death | Category convention → anti-thesis → fonetik cesaret |

> **Neumeier (2024) Scratch doctrine**: "LLM'in öngördüğü ortalamadan kaç. Tuhaf olmak için değil — unutulmaz olmak için."

> **Watkins kuralı (korundu)**: Her aday için kafanda **görsel** oluşmalı.

#### ADIM 3.3 — Dilbilimsel Laboratuvar ve Küresel SCRATCH Testi (v2.0: SMILE+M)

10–15 adaydan **en güçlü 3–5 finalisti** seç. Her finalist için aşağıdaki tablo:

```markdown
### Finalist: [İSİM]

**Hece yapısı**: [örn: Nai-ke, 2 hece, trochaic]
**Fonetik profil**: [açık vokal sonu / sert ünsüz açılış / Bouba-Kiki: round]
**SMILE+M skoru**: S [✓] M [✓] I [✓] L [✓] E [✓] +M [✓] = 6/6
**SCRATCH bayrakları**: [hiçbiri / X kategorisinde uyarı]
**3-katmanlı dilution**: L-A Levenshtein [temiz] / L-B Phonetic [temiz] / L-C Aura [temiz]
**Telaffuz test (6 dil)**: EN [✓] ES [✓] DE [✓] FR [✓] TR [✓] JP [✓]
**Disaster check (9 dil)**: EN/ES/AR/RU/ZH/TR/FR/DE/PT — temiz
**Stratejik karşılığı (EN)**: [tek cümle]
**Stratejik karşılığı (TR)**: [tek cümle]
```

**SCRATCH testine takılan hiçbir ismi finalist olarak sunma.** Soft-flag (S-Spelling veya C-Curse-of-knowledge) durumunda bunu **bilinçli stratejik tercih** olarak gerekçelendir.

**+M (Morphable) kriteri**: Aşağıdaki 4 sorudan en az 3'üne evet:
1. Kinetik wordmark için harfler arası nefes alma kapasitesi var mı?
2. Sub-brand üretimi için morfolojik açık kapı var mı?
3. Prefix/suffix ekleme ile semantik erozyon olmadan genişleyebilir mi?
4. Motion-first animasyonda heceler bağımsız canlanabilir mi?

İlgili scriptleri çağırabilirsin:

```bash
# Fonetik profil (her finalist için)
python /mnt/skills/user/brand-maker/scripts/phonetic_analyzer.py "AdayIsim1" "AdayIsim2" "AdayIsim3"

# 9-dilli disaster check
python /mnt/skills/user/brand-maker/scripts/disaster_checker.py "AdayIsim1" "AdayIsim2" "AdayIsim3"

# Türkçe semantic katman
python /mnt/skills/user/brand-maker/scripts/turkish_semantic_check.py "AdayIsim1" "AdayIsim2" "AdayIsim3"
```

#### ADIM 3.4 — Live Domain Verification (GoDaddy MCP-First)

> **Bağlayıcı kural**: Domain doğrulaması bu adımda yapılır ve `.com` mutlak önceliklidir.

v1.2'den aynen korundu. Detaylı protokol için → `references/godaddy-mcp-integration.md`

#### ADIM 3.5 — Post-Digital Validation (YENİ — v2.0)

> **Bağlayıcı kural**: Step 3.4 tamamlandıktan sonra ve Step 3.6 öncesinde **her finalist için** yürütülür. Her finalist altı eksen üzerinden 0–2 puan; toplam 0–12.

**Skorlama rubric'i (her eksen)**:
- **0 puan** = kritik başarısızlık, finalist **elenir** veya raporda bold uyarı
- **1 puan** = dikkat notu ile kabul
- **2 puan** = temiz

**Toplam skor yorumu**:
- **10–12 / Digital-Safe** — birinci tercih adaylığı için güçlü
- **7–9 / Acceptable with notes** — stratejik trade-off raporlanır
- **<7 / Demote** — alternatif finalist aranır

**Altı Eksen**:

| Eksen | Script | Test |
|---|---|---|
| **1. LLM Namespace** | `llm_namespace_probe.py` | 4 LLM proxy'de "What is [NAME]?" sorgusu — entity collision tespiti |
| **2. Morpheme Saturation** | `morpheme_saturation_check.py` | YC+PH son 24 ay korpusunda kalıp sıklığı (algoritmik jeneriklik) |
| **3. Voice-First ASR** | `asr_simulation.py` | Homofonik rakip, ASR fidelity, voice commerce optimality (trigger: consumer/voice) |
| **4. Entity Disambiguation** | `entity_disambiguation.py` | Wikipedia/Wikidata namespace uniqueness |
| **5. INN/USAN Collision** | `inn_stem_collision.py` | WHO INN + USAN stem çakışması (trigger: pharma only) |
| **6. Famous-Mark Dilution** | `famous_mark_dilution.py` | 3-katmanlı: Levenshtein-2 + Phonetic-3 + Conceptual-aura |

Non-pharma brief'lerde Eksen 5 **N/A**; toplam skor 10 üzerinden değerlendirilir.

Script çağrıları:

```bash
python /mnt/skills/user/brand-maker/scripts/llm_namespace_probe.py "Finalist1"
python /mnt/skills/user/brand-maker/scripts/morpheme_saturation_check.py "Finalist1"
python /mnt/skills/user/brand-maker/scripts/asr_simulation.py "Finalist1"
python /mnt/skills/user/brand-maker/scripts/entity_disambiguation.py "Finalist1"
python /mnt/skills/user/brand-maker/scripts/inn_stem_collision.py "Finalist1"   # pharma only
python /mnt/skills/user/brand-maker/scripts/famous_mark_dilution.py "Finalist1"
```

#### ADIM 3.6 — Ajans Kalitesinde Sunum (v1.2 → v2.0 kaydırıldı)

Final 3–5 şampiyon ismi, **`output-template.md`'de tanımlı format** ile sun. Her isim için:

* **Tek cümle EN rasyonel** (uluslararası investor pitch tonu)
* **Tek cümle TR karşılığı** (yönetim kuruluna sunum tonu)
* **Domain durumu** (GoDaddy MCP canlı sonucu)
* **Trademark stratejisi** (WIPO Madrid sınıfları + ön-tarama URL'leri)
* **[v2.0] Post-Digital Readiness Scorecard** (6-eksen skorları + rationale)
* **[v2.0] Pharma-regulatory pre-screen** (pharma-only)
* **Genişleme alanı (Legs)** — alt-marka / ürün hattı projeksiyonu

Raporun sonuna **stratejik tavsiye matrisi** ekle. `.com` müsait + Post-Digital 10+/12 finalistler **birinci tavsiye** olarak öner.

---

## Karar Çerçevesi: SMILE+M / SCRATCH (özet)

Tam detay için → `references/smile-scratch-filter.md`

**SMILE+M — Kazananın 6 niteliği** (Watkins 2014 + v2.0 uzantısı):
- **S**uggestive — marka deneyimini ima eder
- **M**eaningful — müşteri "anlar"
- **I**magery — görsel olarak çağrışım yaratır
- **L**egs — tema / genişleme imkânı
- **E**motional — duygu uyandırır
- **+M**orphable (v2.0) — kinetik / modüler genişleme toleransı

**SCRATCH — Kaybedenin 7 ölümcül günahı**:
- **S**pelling-challenged
- **C**opycat (v2.0: 3-katmanlı dilution — Levenshtein + Phonetic + Conceptual-aura)
- **R**estrictive
- **A**nnoying
- **T**ame
- **C**urse of knowledge
- **H**ard to pronounce

---

## Çıktı Sözleşmesi (v2.0)

1. **Format**: Markdown.
2. **Dil**: Brief diline birincil, rationale'ler EN+TR çift.
3. **Uzunluk**: 2.000–4.500 kelime.
4. **Ton**: Otoriter, entelektüel, cesur, analitik, global vizyoner.
5. **Yasaklar**:
   - [v1.2] Türkçe lokal karakter (ş, ğ, ç, ü, ö, ı) içeren global isim önerme
   - [v1.2] SCRATCH testine takılan hiçbir ismi finalist olarak listeleme
   - [v1.2] Ünlü trademark'ları (Apple, Tesla, Google) "öneri" olarak sunma
   - [v1.2] Tek heceli generic kelimeler (Run, Box, Up, Go)
   - [v1.2] Numerik karakterler — yalnızca müşteri özellikle isterse
   - **[v2.0] Algoritmik jenerik kalıplar** — `morpheme_saturation_check.py`'den >50 frequency dönen hiçbir finalist sunulmaz
   - **[v2.0] INN/USAN suffix collision** — pharma brief'lerde INN stem ile çakışan isim finalist olamaz
   - **[v2.0] Famous-mark conceptual-aura exploitation** — Layer C'de pozitif dönen finalist elenir
   - **[v2.0] LLM hallucination magnet** — Axis 1'de ≥2 LLM başka entity'ye bağlıyorsa finalist olamaz

---

## GitHub Repo Mantığının Uygulanması

Kullanıcı, skill'in tasarımında aşağıdaki açık-kaynak metodolojilerden esinlenilmesini istedi:

| Repo | Skill İçinde Karşılığı |
|---|---|
| [veliovgroup/uniq.site](https://github.com/veliovgroup/uniq.site) | **Birincil**: GoDaddy MCP. **Fallback**: `scripts/domain_recon.py` |
| [dcurtis/open-brand](https://github.com/dcurtis/open-brand) | `references/exemplar-catalog.md` |
| [starlangsoftware/turkishwordnet-py](https://github.com/starlangsoftware/turkishwordnet-py) | `scripts/turkish_semantic_check.py` |
| [aparrish/pronouncingpy](https://github.com/aparrish/pronouncingpy) | `scripts/phonetic_analyzer.py` |
| [snguyenthanh/better_profanity](https://github.com/snguyenthanh/better_profanity) | `scripts/disaster_checker.py` |
| [gmarmstrong/python-datamuse](https://github.com/gmarmstrong/python-datamuse) | `references/creation-techniques.md` |

---

## Tipik Çağrı Örnekleri (v2.0) — Sektör Çeşitliliği

Aşağıdaki üç örnek, skill'in **sektör-agnostik** karakterini ve **opt-in regüle sektör modüllerini** gösterir.

### Örnek 1 — B2B SaaS / AI Platform (Tech, Regülasyon-Hafif)

**Kullanıcı brief'i:**
> "Yeni bir B2B AI agent platformu için isim arıyorum. Geliştiriciler hedef. Stripe ve Vercel'in birleşimi gibi konumlanmak istiyorum — geliştirici-dostu ama enterprise-ready. Born-global çıkıyoruz, ABD ve EMEA pazarı."

**Skill yanıt akışı:**
1. **Adım 0**: 3 zorunlu referans yüklenir.
2. **Adım 1**: "AI", "developer", "born-global" → **Kural 9 tetiklenir**: `geo-llm-readiness.md` + `ai-fingerprint-avoidance.md` + `creation-techniques.md` + `naming-categories.md` yüklenir. Pharma modülü sessizdir.
3. **Adım 3.1–3.6**: 5-kategoriden 12 aday → 4 finalist. Post-Digital Validation 5 eksen üzerinden 0–10 (Eksen 5 INN N/A). Çıktı ~3.200 kelime.

### Örnek 2 — Tüketici DTC / Premium İçecek (Regülasyon-Hafif)

**Kullanıcı brief'i:**
> "Yeni bir fermente çay markası lansmanı planlıyorum. Gen-Z hedef, Kombucha'dan daha cesur bir pozisyonda — Liquid Death estetiği, premium doğal. TR+EU pazarı."

**Skill yanıt akışı:**
1. **Adım 0**: 3 zorunlu referans yüklenir.
2. **Adım 1**: "Liquid Death", "cesur", "Gen-Z" → **Kural 15 tetiklenir**: `modern-canon-2022-2026.md` (Neumeier Contrarian) + `voice-first-naming.md` (DTC voice commerce) + `disaster-check.md` TR+EU. Ayrıca `turkish_semantic_check.py` TR-market sinyaliyle. Pharma modülü sessizdir.
3. **Adım 3.2**: **E kategorisi ağırlıklı** üretim — contrarian brief. 5-kategoriden 14 aday, 4 finalist. 
4. **Adım 3.5**: Voice-first ASR Eksen 3 yüksek ağırlık. Post-Digital 5-eksen (0–10).

### Örnek 3 — Pharma Brand (Opt-in Regüle Sektör Aktif)

**Kullanıcı brief'i:**
> "Roche TR için yeni HER2-low ADC ürününün Türkiye brand ismi. Onkolog hedef, hastane kanalı ana. TİTCK onay süreciyle uyumlu olmalı."

**Skill yanıt akışı:**
1. **Adım 0**: 3 zorunlu referans yüklenir.
2. **Adım 1**: "Roche", "HER2-low", "ADC", "TİTCK" → **Kural 11 dominant tetiklenir**: `pharma-naming-constraints.md` + `inn_stem_collision.py` + `entity_disambiguation.py --high-precision`. Ayrıca `turkish_semantic_check.py` TR-market + `disaster-check.md`.
3. **Adım 3.5**: Post-Digital 6-eksen (0–12). Eksen 5 (INN/USAN) **aktif** — `-deruxtecan`, `-mab`, `-tinib` stem kontrolleri.
4. **Rapor ek bölümü**: Section 4A "Pharma-Specific Regulatory Screening" (USAN stem, LASA riski, TİTCK Türkçe filtre).
5. Çıktı ~4.500 kelime, finalistler FDA DMEPA Layer 2 pre-screen temiz.

---

**Üç örneğin ortak noktası**: Aynı 5-adımlı çekirdek metodoloji, aynı SMILE+M filtresi, aynı 3-katmanlı SCRATCH dilution, aynı bilingual rapor formatı. Fark yalnızca **tetiklenen referans dosyaları**, **aktif Post-Digital eksenleri** ve **opsiyonel rapor bölümleri**.

---

## Versiyon ve Limitler

* **v1.0** — İlk sürüm. 4 stratejik kategori, SMILE/SCRATCH filtre, 8-dilli disaster check, 4-adımlı metodoloji.
* **v1.1** — GoDaddy MCP entegrasyonu.
* **v1.2** — Türkçe semantic katman (5-layer + `--suggest` mode).
* **v2.0** — Post-Digital Era upgrade. 5. kategori (Contrarian), SMILE+M, 6-axis Post-Digital Validation, pharma-regulatory module, SMP v1.0 manifest, 2022–2026 canon integration.

* **Bilinen limitler**:
  - Trademark "kesin" temizlik garantisi verilmez — manuel USPTO/EUIPO/WIPO doğrulaması zorunlu
  - Domain müsaitliği yalnızca GoDaddy MCP etkin ise canlı; aksi halde heuristic
  - Mandarin tonal nüansı heuristic seviyede
  - Arapça kök analizi yüzeysel
  - **[v2.0] LLM namespace probe**, özel API'lere erişmez; `web_search` ile public surface proxy kullanır
  - **[v2.0] Morpheme saturation corpus** sabit snapshot; periyodik güncelleme gerekir
  - **[v2.0] INN/USAN stem listesi**, 2026 Q1 snapshot'ıdır
  - **[v2.0] Famous-mark Layer C (conceptual-aura)** heuristic + LLM-yardımlı
* **Tasarım kararı**: Bu skill **isim üretir + filtreler + sunar**. Logo tasarımı, vizüel kimlik → `brand-visual` skill'ine yönlendir.
