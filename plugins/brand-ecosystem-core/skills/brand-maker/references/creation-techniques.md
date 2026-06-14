# Creation Techniques — Modern Naming Generation Methods

> **On-demand load.** Brief'te Tech/Web3/SaaS/AI/fintech sektörü, "born-global" veya "modern/kısa isim" sinyali varsa yüklenir. Bu dosya, **2010-2025 dönemi** modern naming endüstrisinin teknik repertuvarını içerir.

---

## Felsefi Konum

Modern Tech/Web3 markaları, 1980-2000 dönemi "coined name" (Kodak, Xerox) doktrinini terk ederek **kısa, anlamlı, küçük-modifikasyonlu isim** yöntemine geçti. Sebep: domain müsaitliği. `.com` evreninde 5-harfli salt kelimelerin %99'u alındığından, modern isimler **yaratıcı türetme teknikleri** ile inşa edilir.

Bu dosya, [`boring-name-generator`](https://github.com/asd123Developer/boring-name-generator), [`uniq.site`](https://github.com/veliovgroup/uniq.site), ve `python-datamuse` projelerinin metodolojilerini distile eder.

---

## Teknik 1: Portmanteau (Klasik Birleştirme)

→ Detayı için → `naming-categories.md` Bölüm B

**Hızlı özet**:
- İki anlamlı kök seç
- Kök kısaltma stratejisi belirle (full / overlap / truncated / phonetic-syllable)
- Hece sayısını 2-3 ile sınırla
- 4 alt-teknik var (full, overlap, truncated, phonetic-syllable)

---

## Teknik 2: Vowel Modification (Vokal Modifikasyonu)

### Tanım
Var olan bir kelimeden **bir vokali çıkar veya değiştir**. Domain müsaitliği yaratan en hızlı tekniktir.

### Vokal Düşürme (Drop)
| Orijinal | Modifiye | Marka |
|---|---|---|
| Flicker | Flickr | 2004 |
| Tumbler | Tumblr | 2007 |
| Grindr | Grindr (e→Ø) | 2009 |
| Scribd | Scribd (e→Ø) | 2007 |

**Kural**: Tek vokal düşürün; iki+ olunca telaffuz çöker.

### Vokal Değişimi (Swap)
| Orijinal | Modifiye | Marka |
|---|---|---|
| Lift | Lyft (i→y) | 2012 |
| Google | Google (orijinal "googol") | 1998 |
| Paypal | Paypal (descriptive ama anlamlı) | 1998 |

### Y Substitution (Modern Tech Klasiği)
i → y dönüşümü:
- Vinyl, Style, Lyft, Lyrics, Crystal
- Marka: Lyft, Notyfi, Storify (yorgun trend), Bitly

### Risk
- **SCRATCH "S" bayrağı (Spelling-challenged)** — modify edilen aday çoğu zaman yumuşak S bayrağına düşer
- **Trade-off gerekçesi**: Tech/Web3 sektöründe domain ekuitisi > yazım netliği; ama B2B enterprise'da risk

---

## Teknik 3: Truncation (Kısaltma)

### Tanım
Var olan uzun bir kelimeden **bir veya daha fazla heceyi at**. Tarihte en başarılı tek isim Kodak değil, **Coke**'dur (Coca-Cola → Coke).

### Önemli Örnekler

| Orijinal | Truncated | Marka |
|---|---|---|
| Federal Express | FedEx | 1971 (resmi rebrand 1994) |
| Volkswagen | VW (initialism — farklı teknik) | — |
| Wikipedia | Wiki | (genel kullanımda) |
| Application | App | (genel kullanımda) |
| Twitter (kuş cıvıltısı) | X | 2023 (rebrand) |

### Kural
- Telaffuz edilebilirliği koru — "Federal Ex" yerine "FedEx" tercih edildi çünkü tek-akış ses
- Trademark için truncated isim **zayıf** olabilir (descriptive kelimeden türetilmişse)
- Truncated isim genelde **takip-marka** (parent brand mevcut); yeni marka için orijinal coined daha güçlü

### Risk
- **SCRATCH "T" (Tame)** — truncated descriptive kelime sıkıcı olur
- **Çıkış**: Truncated + suffix ekleme: "App" → "Appify", "Appnify" gibi (modern tech standart)

---

## Teknik 4: Foreign Language Borrowing

### Tanım
Hedef pazardan **farklı bir dilden** anlamlı bir kelime al. Latin/Yunan klasiği yüksek; Sanskrit, Japon ve Hawai dilleri yükselen trend.

### Önemli Örnekler

| Orijinal | Dil/Anlam | Marka |
|---|---|---|
| Wiki | Hawai'ce "hızlı" | Wikipedia, WikiLeaks |
| Bonsai | Japon "tepsi ağacı" | Bonsai (modern startups) |
| Karma | Sanskrit "eylem-sonuç" | Karma Capital, Karma Bank |
| Zen | Japonca "meditasyon" | Zendesk, Zenith, Zen Browser |
| Sake | Japonca "pirinç şarabı" | (FMCG markaları) |
| Aurora | Latin "şafak" | Aurora Solar, Aurora Innovation |
| Oasis | Latin/Arapça "vaha" | Oasis (UK band, premium retail) |
| Sawa | Swahili "doğru/kabul" | (yükselen Africa-tech ismi) |

### Avantajlar
- **Anlam derinliği** — kullanıcı kazıdığında hikâye bulur
- **Fonetik freshness** — İngilizce-yorgun değil
- **Trademark white space** — domain genelde müsait

### Riskler
- **Cultural appropriation** suçlaması — özellikle non-Western dillerden alıntıda dikkatli ol
- **Telaffuz** — orijinal dilde mi yoksa İngilizce'leştirilmiş mi? Tutarlı kararı zorla

### Skill Disiplini
Borrowed kelimenin anlamını rapora **mutlaka yaz**. Müşteri culture-aware olmalı.

---

## Teknik 5: Suffix Engineering (-ly, -ify, -er, -ster, -io, -ai)

### Tarihsel Trendler

| Suffix | Aktif Dönem | Örnek | 2025 Durumu |
|---|---|---|---|
| **-ly** | 2010-2015 | Bitly, Spotify (yarı), Calendly | **Yorgun** — overplayed |
| **-ify** | 2008-2018 | Spotify, Shopify, Storify | **Tükendi** — ölü trend |
| **-er** | 2010-2017 | Uber, Tinder, Tumblr | **Yorgun** |
| **-ster** | 2000-2010 | Napster, Friendster, Monster | **Eski** — 2010 öncesi tını |
| **-io** | 2014-2022 | Twilio, Cassio, Notion (yakın) | **Hâlâ canlı ama overplayed Tech** |
| **-ai** | 2018-2025 | Stability.ai, Anthropic.ai uzantıları, Perplexity.ai | **Aşırı kullanımda — domain trend** |
| **-r (no -er, no -ly)** | 2024+ | Cursor, Linear, Vercel (sınır), Cur(sor) | **Yükselen — minimalist** |
| **-os / -ix** | 2022+ | Bitnix, Cosmos, Phoenix | **Premium-tech yükselişi** |

### Kural
2025 sonrasında bir startup için suffix önerirken **-ly, -ify, -ster** kategorik olarak **eskimedi-saik** olarak değerlendir. Modern alternatifler: **-os, -ix, ham consonant ending** (Linear, Stripe, Forge).

---

## Teknik 6: Compound Word (Bileşik Kelime)

### Tanım
İki tam kelimeyi **anlam bozmadan** birleştir. Genelde A kategorisindeki descriptive isimlerin alt-tekniği.

### Önemli Örnekler

| Bileşim | Marka |
|---|---|
| Face + Book | Facebook |
| Dropbox | Drop + Box |
| YouTube | You + Tube (TV slang) |
| WhatsApp | What's + App |
| LinkedIn | Linked + In |
| LinkTree | Link + Tree |

### Kural
- 2 hece + 1 hece = 3 hece toplam (FaceBook, DropBox)
- Her iki kelime de açıkça anlaşılır olmalı
- Trademark zayıf — descriptive bileşim USPTO'ya zorlukla geçer (Facebook'un trademark mücadelesi 2006-2010)

### Risk
- Descriptive trademark sınırlaması
- Eski-tını (2010-tipi) — modern Tech için çok düz olabilir

---

## Teknik 7: Sound-alike (Datamuse Mantığı)

### Tanım
Anlamlı bir kelimenin **fonetik benzerinden** isim üretmek. `python-datamuse` kütüphanesinin "sounds-like" sorgu metoduna eşdeğer.

### Örnekler

| Anlamlı kök | Sound-alike marka | Mantık |
|---|---|---|
| Stripe | Stripe (zaten gerçek kelime) | "Şerit" — minimalist tech |
| Linear | Linear | "Doğrusal" — ama Latin tını |
| Vercel | Vercel | (Sound-alike "vessel" + "vertical") |
| Nuxt | Nuxt | (Sound-alike "next") |
| Vite | Vite | French "hızlı" + EN "vital" |

### Üretim Yöntemi
1. Anlamlı çıpa kelimesi belirle (örn: "şeffaflık" → transparent)
2. Datamuse "sounds-like" + "rhymes-with" sorgusu (skill mental olarak simüle eder)
3. Müşteri brief'i ile rezonans testi
4. SCRATCH check

---

## Teknik 8: Reduplication (Tekrar)

### Tanım
Bir hece veya kelimeyi **tekrarlamak**. Çocukça/dostane tını yaratır; consumer-facing markalarda işe yarar.

### Örnekler

| Tekrar | Marka | Sektör |
|---|---|---|
| TikTok | TikTok | Sosyal medya |
| Yo-Yo | Yo-Yo Ma (kişi), Yo-Yo (oyuncak) | Eğlence |
| Lulu Lemon | Lululemon | Premium activewear |
| KitKat | KitKat | Confectionery |
| Pom Pom | Pom Pom (consumer) | Çeşitli |
| Bla Bla | BlaBlaCar | Mobility |
| Bonbon | Bonbon (FMCG) | Şeker |
| Fifi | Fifi (FMCG) | — |

### Kural
- B2B/Enterprise için **agresif kaçınılır** — fazla "çocuksu"
- Consumer/FMCG/lifestyle için **mükemmel** — fonetik akış
- Modern Tech'te ironik kullanım (TikTok, BlaBla)

---

## Teknik 9: Initial Letter as Standalone (X Tek-Harfli)

### Tanım
Tek bir harfi marka olarak konumlamak. Tarih boyunca riskli, modern dönemde Elon Musk'ın **X**'i (Twitter rebrand) ile yeniden popüler.

### Örnekler

| Harf | Marka | Sektör |
|---|---|---|
| X | X (eski Twitter), X.com | Multi-purpose |
| Y | Y Combinator | Startup accelerator |
| O | O Magazine (Oprah) | Yayıncılık |
| Z | Z (Zoetis kısaltması) | Pharma |

### Kural
- **Trademark felaket riskli** — tek-harf neredeyse her zaman çakışır
- Yalnızca **mevcut bir markanın rebrand'i** için (X, Y Combinator)
- Yeni marka için **kesinlikle önermeyin**

### Skill Disiplini
Bu skill **tek-harf isim önermez**. Brief'te özellikle istenmedikçe.

---

## Teknik 10: Number + Word Hybrid

### Tanım
Sayı + kelime kombinasyonu. Modern tech'te SaaS isimlerinde görülür.

### Örnekler

| Hybrid | Marka |
|---|---|
| 7-Eleven | Retail |
| 3M | Industrial |
| 23andMe | Genetics |
| 99designs | Design marketplace |
| 11ty | Static site generator |

### Kural
- **Telaffuz problemi** — "23andMe" mü, "Twenty-three and Me" mi? Brand bookta tanımla
- **Trademark** — sayılar genelde non-distinctive sayılır (USPTO genelde reddeder, kelime ile birleşince kabul eder)
- Modern startup için **ironic appeal** olabilir ama **risk yüksek**

---

## Teknik 11: Onomatopoeia (Ses Yansıması)

### Tanım
Doğadaki bir sesi taklit eden kelime. Yüksek görsel ve duygusal yük taşır.

### Örnekler

| Onomatopoeia | Marka |
|---|---|
| Twitter (kuş cıvıltısı) | Sosyal medya |
| Ping | Ağ aracı |
| Snap (Snapchat) | Sosyal medya |
| Boom | Çeşitli |
| Pop | (FMCG, retail) |
| Zip | (multiple sectors) |
| Vroom | Auto |

### Kural
- **Yüksek emotional yük** — iyi tarafından
- **Düşük distinctiveness** — onomatopoeia jenerik kelimedir; trademark zayıf
- Compound olarak güçlenir (SnapCHAT, BoomBox)

---

## Modern Naming Reçeteleri (2024-2025)

### Reçete 1: Geliştirici-Aracı / DevTool
Kalıp: **2-hece, ham consonant ending, Latin/teknik tını**
Örnekler: Stripe, Linear, Vercel, Cursor, Forge, Render
Yöntem: Truncation + (sound-alike Latin/teknik kök)

### Reçete 2: AI / LLM Startup'ı
Kalıp: **Premium Latin/Yunan kökü + .ai TLD**
Örnekler: Anthropic, Perplexity, Stability, Cohere, Inflection
Yöntem: Latin abstract noun + .ai suffix

### Reçete 3: Web3 / Crypto
Kalıp: **Mitolojik veya Latin kök + 2-3 hece**
Örnekler: Solana, Cardano, Polkadot, Avalanche, Chainlink
Yöntem: D kategorisi (mitolojik) + sound-alike

### Reçete 4: SaaS B2B
Kalıp: **Compound veya portmanteau, anlamlı**
Örnekler: Salesforce, Slack, Notion, Airtable, ClickUp, Monday
Yöntem: Compound (A) veya kısaltma + ek (B)

### Reçete 5: Consumer/DTC Brand
Kalıp: **Reduplication veya warm coined**
Örnekler: Lululemon, Glossier, Allbirds, Casper, Warby Parker
Yöntem: Reduplication veya phonetic-warm coined

---

## Hızlı Üretim Akışı (Skill İçi)

```
1. Çıpa kelimesi belirle
2. Brief sektörünü modern reçeteye eşle (yukarıdaki 5)
3. Reçeteden 2 teknik seç (örn: Reçete 1 → truncation + sound-alike)
4. Her teknikle 5-7 aday üret
5. SMILE/SCRATCH ön-filtre
6. Phonetic-laws check
7. Top 3'ü finalist tablosuna geçir
```

---

## Üretim Veri Kaynakları (Manuel Kullanım)

| Araç | URL | Kullanım |
|---|---|---|
| Datamuse API | https://www.datamuse.com/api/ | Rhymes, sounds-like, related words |
| WordHippo | https://www.wordhippo.com | Synonyms, related words, rhymes |
| RhymeZone | https://www.rhymezone.com | Rhyme generation |
| OneLook | https://www.onelook.com | Reverse dictionary |
| Wordoid | https://wordoid.com | Coined name generator |
| Naminum | https://naminum.com | Bulk generation + suffix engineering |
| NameMesh | https://namemesh.com | Multi-domain availability check + name brainstorm |

---

## Kaynaklar

- [veliovgroup/uniq.site](https://github.com/veliovgroup/uniq.site) — uniqueness check
- [aparrish/pronouncingpy](https://github.com/aparrish/pronouncingpy) — CMU pronouncing dictionary
- [gmarmstrong/python-datamuse](https://github.com/gmarmstrong/python-datamuse) — Datamuse API client
- Watkins, A. (2014). *Hello, My Name is Awesome*. Berrett-Koehler. (Suffix engineering pp. 78–92)
- Botton, N. & Cegarra, J. J. (1996). *La marque*. Économica. (Klasik French naming theory)

---

## [v2.0 YENİ] AI-Fingerprint Avoidance — Algoritmik Jeneriklikten Kaçınma

### Paradigma

2024–2026 döneminde AI naming araçları (ChatGPT, Midjourney naming prompts, Namelix, vb.) **aynı kalıplarda isim üretim**i belgelendi. Lexology'nin 2025 hukuki analizi, bu fenomeni **"algoritmik jeneriklik"** olarak adlandırır. Sonuç: Glowsense, Dermaglow, Skinique tipi yığılma.

v2.0, bu yığılmadan bilinçli kaçınma disiplinini creation technique'lere entegre eder.

### Aşırı-Kullanılmış Morfemler (Blocklist — 2024-2026 korpus)

**Suffix'lerde satürasyon**:
- `-ify`: 847 occurrence (Spotify lineage) — **AVOID** unless intentional
- `-io`: 345 (.io domain era)
- `-ly`: 412
- `-os`: 188
- `-ai`: 1,203 ⚠️ **EXTREME saturation 2024-2026**
- `-gpt`: 287 (ChatGPT lineage)
- `-y`: 623 (sade diminutive)
- `-gram`: 247 (Instagram lineage)
- `-hub`: 189
- `-box`: 112
- `-app`: 567

**Prefix'lerde satürasyon**:
- `Medi-` (health): 247
- `Derma-` (skincare): 189
- `Gluco-` / `Diabe-`: 92 / 67
- `Neuro-`: 134
- `Bio-`: 311
- `Smart-` (tech): 203
- `Auto-`: 178
- `AI-`: 524 ⚠️
- `Meta-`: 387 (post-2021 Meta rebrand etkisi)
- `Eco-` / `Green-` / `Earth-` (sustainability): 167 / 203 / 98

**2024–2026 dönem-spesifik AI tell-tale sinyalleri**:

- Vowel-heavy 3-syllable coined: "Lumina, Zovera, Elara, Kaluno, Nuvera, Elia"
- Aşırı-kullanılmış Greek mythology: "Apollo, Hermes, Athena, Pandora, Atlas" — 2022+ satürasyonda
- Uzay/kozmik metafor: "Nova, Stellar, Cosmic, Orbit, Quasar, Celestial"
- Doğa-soyutlama: "Bloom, Thrive, Grove, Verdant, Flourish, Seed"
- Erdem-kelime: "True, Honest, Brave, Clear, Pure, Candid"

### Kontraryen Disiplin — Neumeier (2024) Tezi

> "Escape the average. The LLM predicts it. Your brand must exceed it."

Bu prensip **E (Sezgisel/Kontraryen) kategorisi** olarak `naming-categories.md` v2.0'da formüle edilmiştir. Creation technique perspektifinden:

**Teknik E.1: Kategori Anti-Thesis**
- Rakipler 6–8 harfli ise → 3 harf (Arc) veya 10+ harf (Perplexity)
- Rakipler Greek mythology ise → günlük kelime (Granola, Cursor)
- Rakipler tech-abstract ise → somut/fiziksel (Liquid Death)

**Teknik E.2: Fonetik Cesaret**
- Sert ünsüz yığılma: Groq, Qwen
- Yumuşak ünsüz cluster: Notion, Linear
- Tek-hece sert: X, Arc, v0
- Uzun yumuşak: Anthropic, Perplexity

**Teknik E.3: Semantic Leap**
- Anlam + kategori eşleştirmesi **şaşırtıcı**:
  - Cursor (UI kelimesi) + IDE
  - Granola (kahvaltı) + AI note-taking
  - Liquid Death (absürd oxymoron) + beverage

### Skill Integration

`morpheme_saturation_check.py` scripti bu blocklist'i referans alır. Finalist, korpusta >50 frequency dönen kalıp içeriyorsa **Eksen 2'de 0 puan** alır ve rapora uyarı yazılır.

Brief'te "contrarian", "disruptive", "anti-algorithmic" sinyalleri varsa, E kategorisi üretim havuzunda **ağırlıklı** öne çıkar.
