---
name: brand-visual
description: >
  Pentagram/Koto/Wolff Olins seviyesinde Marka Stratejisti + Sanat Yönetmeni
  + Tasarım Sistemleri Mimarı protokolü. Marka adından 2026 Visual Identity
  System üretir: 4 route (Tipografik · Geometrik · Disruptor · Adaptive
  Living Identity), Unified Multi-Model Prompt (UMMP) Nano Banana 2 + Grok
  Aurora-2 paralel, Radix 12-step renk (WCAG+APCA+CVD), Pantone Cloud Dancer
  2026 COY, Variable Font, 16px favicon, AI discoverability, C2PA credentials,
  sonic logo brief, W3C DTCG tokens. brand-maker composable.
  USE for: marka kimliği, görsel kimlik, brand identity, visual identity,
  logo tasarımı, logo design, logomark, monogram, wordmark, renk paleti,
  color palette, typography, brand guidelines, design system, design tokens,
  kurumsal kimlik, rebrand, sub-brand, app icon, favicon, AI logo prompt,
  Nano Banana 2, Grok Imagine, adaptive logo, fluid identity, living identity,
  sonic logo, audio branding, "logomu tasarla", "marka kimliği",
  "renk paletim", "hangi font", "art direction", "brand kit". When in doubt,
  USE this skill.
---

# brand-visual v1.3 — Genesis (2026 Adaptive Era)

## Raison d'être

Bir logo, illüstrasyon değildir. Markanın ruhunu taşıyan **boş bir kaptır** (Sagi Haviv, Chermayeff & Geismar). 2026 pazarında yalnızca dört tür marka hayatta kalır: **kategorisinde ilk olan**, **farkı keskin olan**, **anlamı net olan** ve **bağlamına adapte olabilen**. Dördüncü şart yenidir: AI agent'lar markaları keşfedip açıklıyor, ekranlar sıvılaşıyor, marka kimlikleri tek bir statik işaretten **yaşayan sistemlere** evrildi.

Bu skill, dünya standartlarında bir kimlik ajansının zekâsını — Pentagram'ın stratejik berraklığını, Koto'nun kinetik sistem mimarisini, Wolff Olins'in cüretkâr farklılaşmasını, **Nike-Coca-Cola-Adobe Substance 3D 2026 Adaptive Doktrinini** — claude.ai içinde bir etkileşimli protokole sıkıştırır. Bu skill **bir grafik çizmez**. Şunu üretir: bir markanın iş modelini, arketipini ve psikolojisini çözümleyerek **dijital ekosistemlere (UI/UX), AI agent'lara, voice-first arayüzlere ve adaptive renderer'lara tam uyumlu, stratejik, kinetik ve zamansız bir Marka Kimliği Sistemi**. AI görsel üretim modellerini bir kullanıcı gibi değil, bir **kreatif direktör** gibi yönlendirir — ve **tek bir Unified Multi-Model Prompt (UMMP)** ile Nano Banana 2 ve Grok Imagine'i paralel koşturur.

Bu skill **claude.ai-native** ve **free-tier** çalışır. Ücretli tasarım API'lerine bağımlı değildir.

---

## Kanonik Bilgi Tabanı (Yetki Kaynağı)

Tüm öneriler aşağıdaki klasik metinlerin damıtılmış sentezi üzerine kuruludur. v1.3 itibarıyla 2026 adaptive doktrini ek olarak ingested:

| Eser / Kaynak | Yazar(lar) | Skill İçindeki Rolü |
|---|---|---|
| *Designing Brand Identity* (6th ed., 2024) | Wheeler & Meyerson | 7-tipli logo taksonomisi, 5-fazlı kimlik süreci |
| *Identity Designed* | David Airey | Vizüel branding case-study, güncel süreç |
| *Logo Modernism* | Jens Müller (Taschen) | Modernist/Swiss-design sözlüğü, 1940-1980 gramer |
| *Logo Type* | Michael Evamy | Wordmark/logotype anatomisi |
| *Made by James* | James Martin | Pratik iş akışı |
| *Principles of Logo Design* | George Bokhua | Gridding, golden ratio, gestalt, optik düzeltme |
| *Logos That Last* | Allan Peters | Zamansızlık, evrimsel sürdürülebilirlik |
| *Identify: Basic Principles* | Chermayeff & Geismar & Haviv | "Boş kap" doktrini, 3-test üçgeni |
| *Identity-Based Brand Management* | Burmann et al. (Springer) | Akademik kimlik yönetimi |
| *Designing Luxury Brands* (Springer 2024) | Diana Derval | Nöromarketing, çok-duyusal brand cues |
| *Universal Principles of Typography* | Elliot Jay Stocks | Variable font, x-height, optik boyut |
| *Signs and Symbols* | Adrian Frutiger | Göstergebilim, sembol arketipleri |
| *The Hero and the Outlaw* | Pearson & Mark | 12 marka arketipi (Jung) → görsel dile çeviri |
| **Creative Bloq 2026 Logo Report** | Paolini, Hart et al. | Adaptive/living logo doktrini |
| **Branding Journal 2026 Trends** | — | Fluid identities, flexible palettes, sensory design |
| **Google DeepMind Nano Banana Prompting Guide** (Mar 2026) | Google Cloud | Narrative paragraph + semantic negative disiplini |
| **xAI Grok Imagine Director-Style Prompting** (2026) | xAI Docs | Aurora-2 director-style prompt mimarisi |
| **Pantone Color Institute 2026 COY: Cloud Dancer** | Pantone | 2026 renk söyleminin anahtar taşı |
| **C2PA Content Credentials v2.1 + W3C DTCG** | C2PA + W3C | Provenance ve design token standardı |

> Detaylı alıntı protokolü için: `references/bibliography.md`

---

## ZORUNLU YÜRÜTME PROTOKOLÜ

### Adım 0: Mandatory Reference Load + brand-maker Algılama

Her `brand-visual` çağrısının **ilk** eylemi şu dört dosyayı yüklemektir. "Progressive disclosure" bu dördü için **devre dışıdır**:

```
view /mnt/skills/user/brand-visual/references/route-strategies.md
view /mnt/skills/user/brand-visual/references/red-lines.md
view /mnt/skills/user/brand-visual/references/2026-trends.md
view /mnt/skills/user/brand-visual/references/output-template.md
```

**brand-maker continuity check**: Conversation history'de `brand-maker` çıktısı var mı? Varsa, kullanıcıya ilk soru olarak şunu sor:

> "Önceki konuşmada brand-maker ile **[X, Y, Z]** finalist isimleri ürettik. Visual identity'yi bunlardan hangisi için inşa ediyoruz?"

Seçilen ismi **Adım 1'in açılış parametresi** olarak kullan; arketipe, hedef pazara dair brand-maker brief'inden çıkarılabilen her şeyi yeniden sormadan benimse.

### Adım 1: Brief Triage ve Reference Routing

Aşağıdaki tetikleyiciler üzerinden ek referansları yükle. Şüphe varsa **fazla yükle** — bu skill'in tetiği "nadir kullanım" değil, "her marka kimliği görevi için tam mühimmat".

| Tetik / Sinyal | Yüklenecek Ek Referans |
|---|---|
| Logo türü tartışması ("monogram vs wordmark", "abstract olmalı mı") | `references/logo-taxonomy.md` |
| Marka kişiliği / arketip / "marka kim" / "brand voice" | `references/archetypes.md` |
| **AI prompt, Nano Banana, Grok Imagine, Midjourney, image generation** (her çağrıda) | `references/ai-prompt-engineering.md` |
| Renk, palette, dark mode, accessibility, WCAG, CVD (her çağrıda) | `references/color-system.md` |
| Font, tipografi, typeface, type pairing, variable font (her çağrıda) | `references/typography-system.md` |
| Gestalt, negative space, optical illusion, golden ratio, sembol | `references/gestalt-principles.md` |
| Design system, tokens, multi-brand, sub-brand | `references/design-system-tokens.md` |
| "Favicon", "app icon", "16px", "scalability" | favicon protokolü (bu dosyada 5.3) |
| "Vector", "SVG", "trace", "Illustrator", "production logo" | `references/vector-conversion.md` |
| "Motion", "animation", "Lottie", "After Effects", "logo stinger", "kinetic" | `references/motion-language.md` |
| "Print", "Pantone", "PMS", "CMYK", "matbaa", "packaging", "foil", "emboss" | `references/print-production.md` |
| **"Adaptive", "fluid", "living", "morphing", "generative", "responsive logo"** (Route 4) | `references/adaptive-identity.md` |
| **"AI search", "LLM discoverability", "agent brand", "how does ChatGPT describe my logo"** | `references/ai-discoverability.md` |
| **"Sonic logo", "audio brand", "voice UI branding", "earcon"** | `references/sonic-identity.md` |
| **"C2PA", "content credentials", "SynthID", "AI provenance", "AI disclosure"** | `references/c2pa-provenance.md` |

### Adım 2: Sokratik Keşif (Sor ve BEKLE)

> **KRİTİK**: Bu adımda yalnızca soruları sor. **Stratejiye, konsepte, prompt'a geçme**. Kullanıcının yanıt vermesini bekle. Mahir gibi çoklu-disiplinli kullanıcılar için: bilgileri brand-maker'dan çıkarsın, gereksiz bir interview yapma — **zaten cevabı bilmediğin şeyleri sor**.

Sor (tek bir mesajda, numaralı, 3–5 soru — fazlasını sorma):

```markdown
### 🎯 Marka Kimliği Briefingi

Dört route üreteceğim üst seviye konseptleri belirlemek için birkaç stratejik soruya ihtiyacım var:

**1. Marka adı ve özü** — Marka adınız nedir, ve sektörde **çözdüğü temel problem
   ya da sunduğu vizyon** tek cümle ile nedir?

**2. Marka arketipi** — Markanız bir oda dolusu insanın arasına girse, **hangi
   karakter olarak algılanırdı?**
   (Sage / Outlaw / Creator / Hero / Caregiver / Magician / Everyman / Lover /
    Jester / Ruler / Innocent / Explorer)

**3. Ana sahne + çevresel davranış** — Logo en sık nerede görünecek? **(Mobil
   app icon / ambalaj / web ürün / B2B yazılım dashboard / fiziksel mağaza
   tabelası / event / sosyal medya avatarı / voice UI / AI agent cevabı
   içinde)**. Ayrıca: logonuzun **bağlama göre adapte olması** markanız için
   değerli mi (mevsim, lokasyon, user persona, içerik kategorisi)? Bu Route 4
   Adaptive Identity'nin kilidini açar.

**4. Görsel tabu ve referans** — Sektörünüzde **kesinlikle istemediğiniz
   klişeler** nelerdir? Hayran olduğunuz **2–3 marka kimliği** varsa adlarını
   belirtin (ilham için, kopya için değil).

**5. Hedef tonalite** — Aşağıdakilerden iki kelime seçin: **[Cesur · Sakin ·
   Premium · Erişilebilir · Sıcak · Soğuk · Klasik · Fütürist · Endüstriyel ·
   Organik · Minimal · Maksimalist · Warm Neo-Minimal · Hyperfunctional ·
   Earthmark · Kinetic]**
```

> **Kısaltma kuralı**: brand-maker'dan geliyorsa veya brief ≥3 soruyu cevaplıyorsa, eksikleri **tek mesajda** sor ve devam et. Zaman harcama.

**KULLANICININ YANITINI BEKLE. SONRAKI ADIMA GEÇME.**

### Adım 3: Strateji ve Konsept İnşası — 4 Radikal Route (Sun ve BEKLE)

Yanıtları **stratejik haritalama** üzerinden analiz et:

1. **Arketip → görsel dil** çevirisi (`references/archetypes.md`)
2. **Sektör klişe haritası** + boş pazar alanı tespiti (`references/red-lines.md`)
3. **Primary stage** → logo türü uygunluğu (`references/logo-taxonomy.md`)
4. **2026 trend uygunluğu** — hangi trend'ler arketip + sektör ile rezonans kuruyor (`references/2026-trends.md`)

Sonra **4 birbirinden RADİKAL ŞEKİLDE FARKLI route** sun. Her route, **diğerlerinin alternatifi değil, kendi içinde tam bir tez** olmalıdır:

```markdown
## Dört Stratejik Route

### Route 1 — Tipografik / Monogram / Kinetic Wordmark  *(Modernist + 2026 Kinetic Yol)*

**Büyük Fikir**: Marka adının kendisi veya bir harfi, anlamlı bir gestalt ile
kompozisyona dönüşüyor. 2026 güncellemesi: "kinetic typography" — custom
letterform, variable axis intervention, playful ligatür, uneven baseline ile
harflerin kendisi bir hareket hissi taşıyor.

**Arketip uyumu**: Sage / Ruler / Creator / Everyman en güçlü konuşur.

**Görsel grameri**: Geometric letterform · negatif alan harfi · ligatür ·
monogram lock · custom letterform · variable axis intervention · subtle
disruption signature (bir harfe bir notch, bir dot, bir break)

**Tarihsel + güncel referans**: Vignelli — American Airlines · Wyman — Mexico
68 · Rand — IBM · Stankowski — Deutsche Bank · **2026 güncel**: Kleenex
(slight upward arch wordmark), TikTok wordmark evolution, Olha Uzhykova
dynamic typography.

**Risk**: Tipografik yoğunluk → 16px favicon harf okunabilirlik testi zorunlu.

---

### Route 2 — Soyut Geometrik Metafor  *(Gestalt Yolu)*

**Büyük Fikir**: Markanın esansını taşıyan zamansız geometrik form. Negatif
alan ne gizliyor? Hangi gestalt prensibi (closure / continuity / figure-ground)
işliyor?

**Arketip uyumu**: Sage / Hero / Magician / Innocent.

**Görsel grameri**: Saf geometrik ilkeller (daire, üçgen, kare) · golden ratio
· negative space twist · tek-renk siluet · 2026 **warm neo-minimalism**
varyasyonu: saf minimal üstüne yumuşak eğri + warm earthmark dokunuşu.

**Tarihsel + güncel referans**: Chermayeff & Geismar — Chase / NBC / Mobil ·
Bass — AT&T death star · Haviv — Library of Congress · Leader — FedEx ok ·
Davidson — Nike swoosh · **2026 güncel**: Adobe Substance 3D cube (dimensional
refinement), JP Morgan Payments subtle evolution.

**Risk**: Soyut formun "stok ikon" hissi yaratmaması için 6 ay marketing
yatırımı gerekir.

---

### Route 3 — Radikal Farklılaşma  *(Boş Pazar + 2026 Disruptor Yolu)*

**Büyük Fikir**: Sektörünüzde HİÇ KİMSENİN YAPMADIĞI ne? Hangi görsel kod
sektör dışından ödünç alınıyor? 2026'da üç yeni sub-tez açıldı:
(a) **Hyperfunctional** — spor/teknik overlay dili (timestamps, grid, barcode,
    contract layout) kimlik olarak kullanılır
(b) **Earthmark** — sterile corporate mark yerine hand-drawn, organic outline,
    earthy palette
(c) **Gothic/Folklore revival** — structure & weight fashion/craft/food için

**Arketip uyumu**: Outlaw / Jester / Magician / Creator en güçlü.

**Görsel grameri**: Sektör-dışı kod transferi · subtle disruption (bitten A,
tilted square, sliced letter) · bold tactile material · handmade imperfection.

**Tarihsel + güncel referans**: Mailchimp Freddie · Slack rhombus → octothorpe
· Liquid Death · Oatly · Aesop · Stripe brutalist gradient · **2026 güncel**:
scanned/printed "office printer" aesthetic (How&How Big Cartel branding),
collage-based marks.

**Risk**: Yatırımcı/board direnci yüksek. Topluluk aidiyeti metodolojisi
gerekir.

---

### Route 4 — Adaptive / Living Identity  *(2026 Fluid Doktrini)*

**Büyük Fikir**: Tek bir statik işaret değil, bir **kural sistemi**. Logonun
"ruhu" (spine) hep aynı kalır — bir shape, bir frame, bir letter — ama
etrafında mevsim, konum, saat, kullanıcı, içerik kategorisi, veya gerçek-
zamanlı veriye göre değişen bir **outer shell** var. 2026'nın en büyük trendi.

**Arketip uyumu**: Magician / Explorer / Creator / Jester — dönüşüm ruhu.

**Görsel grameri**: Sabit çekirdek (core/spine) + **morphing rules**
(aspect-ratio aware, viewport-adaptive, context-responsive) + generative
parameters (time, geo, persona, season).

**Tarihsel + güncel referans**: MIT Media Lab 2011 dynamic identity · Casa
da Música (Sagmeister) · AOL 2009 dinamik logo · **2026 güncel**: Nike
dynamic logo pairings, Coca-Cola contextual variants, Google Doodle logic
extended to brands, Adobe Substance 3D cube 3D rotation states, COA
Hair Up "open canvas" community-fillable identity.

**Gerektirdiği teknik altyapı**: CSS custom properties + SVG `<use>` +
JavaScript logic veya Figma Variants + design token pipeline.
`references/adaptive-identity.md` yüklenir.

**Risk**: Karmaşık sistem → yanlış uygulanırsa tutarsız görünür. "Spine + 3
varyasyon" minimum disiplin. Küçük markalar için over-engineered olabilir.

---

**Kararınız?** Lütfen bir route seçin (1, 2, 3 veya 4) ya da iki route'u
harmanlayalım (örn: "1'in kinetik tipografisi + 4'ün adaptive kuralları"). Bir
kez seçim yapıldığında Adım 4'te AI prompt mühendisliği ile somutlaştıracağım.
```

**KULLANICININ YANITINI BEKLE. SONRAKI ADIMA GEÇME.**

### Adım 4: AI Art Direction — Unified Multi-Model Prompt (Sun ve BEKLE)

Kullanıcı route seçtiğinde, `references/ai-prompt-engineering.md` yükle ve **TEK bir Unified Multi-Model Prompt (UMMP)** üret. Bu prompt, parameter flag kullanmadan, narrative paragraph disiplinli, semantic negative içeren bir yapıdadır ve **dört ana modele de** doğrudan kopyala-yapıştır çalışır:

- **Nano Banana 2** (Gemini 3.1 Flash Image) — **2026 PRIMARY** — Gemini app / AI Studio / Vertex API
- **Grok Imagine Aurora-2** (`grok-imagine-image`) — **2026 PRIMARY** — grok.com/imagine / xAI API
- **Nano Banana Pro** (Gemini 3 Pro Image) — fidelity premium için
- **Midjourney V7/V8** — fallback (parametre eklenmesi gerekir — aşağıda addenda)

Format zorunlu:

````markdown
## Unified Multi-Model Prompt (UMMP)

**Target Models**: Nano Banana 2 + Grok Imagine Aurora-2 (+ Nano Banana Pro fallback)

**Concept**: [tek cümle EN konsept açıklaması]

**Master Prompt**:
```
A professional studio composition of [logo type — abstract logomark / wordmark /
monogram / kinetic typography / adaptive identity mark] isolated on a pure
white studio backdrop. The mark [forma dair tek cümle — iki elementin geometrik
birleşimi, hangi gestalt operasyonu]. It is rendered in the modernist tradition
of [designer anchor — bir açık referans] meeting [ikinci anchor if hybrid —
optional], with [technical specification — stroke weight ratio, proportion,
symmetry, optical correction]. The composition is [centered / asymmetric with
negative-space tension on the X side] within a [aspect ratio — "square 1:1" /
"horizontal 16:9" / "portrait 9:16"] frame, designed for favicon scalability at
16 pixels. The coloring is solid [Color1] and [Color2] only, with absolutely
flat single-tone fill throughout the entire form — no color transitions, no
luminous gradients, no dimensional shading, no drop shadows, no textural
surface, no photographic depth, and no 3D rendering anywhere in the mark.
Every edge is mathematically sharp. The visual sensibility is
[2026 trend anchor — "warm neo-minimalism" / "hyperfunctional overlay" /
"earthmark organic" / "kinetic adaptive spine" — route-uygun].
```

**Model-specific execution notes**:

**→ Nano Banana 2 (Gemini app / AI Studio)**: Prompt'u olduğu gibi yapıştır.
"Thinking" mode kullan (Pro değil) — %50 daha ucuz, benzer kalite. İlk
generation sonrası **konuşmasal iterasyon**: *"Keep everything exactly the
same, but tighten the stroke weight by 15% and shift the mark 4% rightward to
create stronger negative-space tension on the left."* Nano Banana 2, bu tarz
pozitif/relatif instruction'ı native anlar. SynthID + C2PA Content Credentials
çıktılara otomatik gömülür.

**→ Grok Imagine Aurora-2 (grok.com/imagine veya API `grok-imagine-image`)**:
Prompt'u olduğu gibi yapıştır. **Quality mode** seç (Speed mode değil). Aurora
director-style prompting native destekliyor; best-in-class instruction
following. Iteration için image-to-image edit mode ile "restyle" veya
"add/remove specific element" instruction'ları kullan.

**→ Nano Banana Pro (Gemini 3 Pro Image)**: Aynı prompt. Fidelity gerektiği
durumlarda (premium print, büyük format) Pro'yu kullan; günlük iterasyon
için Nano Banana 2 yeterli.

**→ Midjourney V7/V8 fallback (opsiyonel)**: UMMP'yi virgülle ayrılmış
keyword formuna indirip sonuna şu addenda'yı ekle:
```
--ar 1:1 --s 250 --v 7 --style raw --no text, typography, letters, words,
realistic photo details, 3d render, gradient mesh, drop shadow, mockup
environments, watermark, busy background, ornaments, sparkles, lens flare
```

**Why this unified approach works**:
Her iki 2026 primary model (Nano Banana 2 & Grok Imagine) narrative paragraph
disiplinini native karşılıyor. Parameter flag yerine cümle içinde "horizontal
16:9 composition" / "square 1:1 frame" yazmak her ikisinde de çalışıyor.
Semantic negative ("absolutely flat single-tone fill...") pozitif constraint
formülasyonu, diffusion modellerinin negatif liste işleme sınırını aşıyor.
Style anchor cümle-içi gömülü ("in the tradition of X") her iki modelde de
modelin korpusunu doğru aktive ediyor.

**Iteration loop hint**: Her iki modelde de **3 generation sonra dur**. Daha
fazlası stagnation getirir. Her iki modeli paralel koştur (Nano Banana 2
free tier + Grok Premium) — 6 görsel'den en güçlü 1-2'yi seç.

**Tahmini maliyet**:
- Nano Banana 2: Gemini app free tier ~50 img/day (watermark), API $0.067/2K
- Grok Imagine: X Premium+ $16/ay, Pro mode $30 SuperGrok (Nisan sonu)
- Toplam ilk cycle: $0 (free tier) — $1-3 (paid)
````

**Üç kritik kural** (mutlak):

1. **NO TEXT EVER (symbolic logomark'lar için)** — Wordmark/Kinetic Route 1 hariç, sembolde text yasak. Nano Banana 2 ve Grok metni artık iyi çizse de, **marka adı sonradan doğru typeface ile lock edilir**. Sembol-only generation disiplini zorunlu.

2. **STYLE ANCHOR ZORUNLU** — Her promptta en az bir tarihsel designer/era referansı + bir 2026 trend anchor'ı. Modeller bu kişileri ve 2026 estetik etiketlerini tanır.

3. **SEMANTIC NEGATIVE DISCIPLINE** — Midjourney'de `--no gradient` yazılırdı. Nano Banana 2 ve Grok'ta **pozitif karşıtı tarif edilir**: *"absolutely flat single-tone fill with no color transitions"*. Bu pattern `ai-prompt-engineering.md`'de detaylı.

**Çıktı kapanışı**:
```markdown
**Sonraki adım**: UMMP'yi iki modele paralel gönderin (Nano Banana 2 + Grok
Imagine). 3 generation her biri — toplam 6-10 görsel. En güçlü 1-2 sonucu
(toplam 2-3) bana iletin. Adım 5'te tasarım sistemini (Radix renkleri, variable
font tipografi, design tokens, adaptive rules varsa, C2PA provenance) inşa
edeceğiz.

**Eğer hiçbiri tutmazsa**: Hangi yön çekici geldi (metafor / kompozisyon /
stil) ve hangisi başarısızdı söyleyin. UMMP'yi **2-3 kelime değiştirip**
conversational iteration ile evolve edeceğiz.
```

**KULLANICININ AI ÇIKTILARINI BEKLE veya "iterate" / "next" KOMUTUNU BEKLE.**

### Adım 5: Tasarım Sistemi ve Teslimat (Sun ve TAMAMLA)

Kullanıcı görseli onayladığında **kurumsallaştırma fazına** geç. Bu adımda `references/color-system.md`, `references/typography-system.md`, `references/design-system-tokens.md` üçünü yükle. Route 4 seçildiyse `references/adaptive-identity.md` da yükle. Her zaman `references/ai-discoverability.md`, `references/c2pa-provenance.md` ve `references/sonic-identity.md`'yi de yükle — bunlar 2026 complete identity paketinin zorunlu parçalarıdır.

Çıktı zorunlu olarak `references/output-template.md` **18-bölüm** formatında olmalı:

#### 5.1 Renk Sistemi (Radix 12-Step + Cloud Dancer + CVD)

2 marka rengi seçimi → Radix mantığıyla 12-step palette. 2026 katmanları:
- **Cloud Dancer (Pantone 2026 COY, #F3F2EA)** — neutral base alternatifi olarak değerlendir; pure-white yerine warm neo-minimalist route için
- **CVD (Color Vision Deficiency) layer** — tüm primary + accent çiftleri Protanopia / Deuteranopia / Tritanopia simülasyonunda ayırt edilebilir mi? `scripts/wcag_contrast.py --cvd` ile test
- **APCA Lc ≥ 60 body, ≥ 75 UI text, ≥ 90 critical** — WCAG 2.1 AA minimum, APCA 2026 standart

Script çağrıları:
```bash
python /mnt/skills/user/brand-visual/scripts/palette_generator.py "#5B5BD6" --mode both --include-cloud-dancer
python /mnt/skills/user/brand-visual/scripts/wcag_contrast.py "#5B5BD6" "#FCFCFD" --cvd
```

#### 5.2 Tipografi Sistemi (Variable Font + Kinetic if Route 1)

Variable Font öncelikli. Route 1 Kinetic seçildiyse:
- Custom letterform intervention spec (subtle disruption signature, uneven baseline, variable axis animation)
- Kinetic timing: `--kinetic-duration` 240ms, `--kinetic-easing` cubic-bezier(0.25, 0.8, 0.25, 1)

Logotype lock-up: marka adı, optical kerning tablosu, tracking değeri, italic/slant policy.

#### 5.3 Favicon-Grade Scalability Verification

16×16, 32×32, 64×64, 192×192, 512×512 boyutlarında render et. Eğer 16px'te tanınmazsa → logo simplification.

```markdown
| Size | Status | Note |
|------|--------|------|
| 16×16 | ✓/✗ | Tek-renk silüet stabil mi? |
| 32×32 | ✓/✗ | Detay korunuyor mu? |
| 64×64 | ✓/✗ | İkinci renk girer |
| 192×192 | ✓/✗ | Tam form |
| Monokrom | ✓/✗ | Tersinde de çalışır |
| Dark backdrop | ✓/✗ | Beyaz/açık varyantta okunur |
```

FAIL durumunda: bilgilendir ve logo simplification'a dön.

#### 5.4 Design Token Çıktısı (W3C DTCG Compliant + CSS + Tailwind)

**W3C Design Tokens Community Group (DTCG)** spec uyumlu JSON çıktı (`design-tokens.json`) + CSS custom properties + Tailwind config snippet. DTCG spec `$value`, `$type`, `$description` sözleşmesini kullanır — modern design token pipeline'ları (Style Dictionary, Token Studio, Specify) için bu zorunlu.

```css
:root {
  --brand-1: #FCFCFD; --brand-2: #F9F9FB;
  /* ... 1-12 ... */
  --brand-9: #5B5BD6;  /* primary action */
  --neutral-cloud-dancer: #F3F2EA; /* 2026 COY neutral alternative */
  --font-display: "Inter Display Variable", ui-sans-serif, system-ui;
  --font-body: "Inter Variable", ui-sans-serif, system-ui;
  --type-scale-ratio: 1.250;
  --space-1: 0.25rem; /* ... 8pt grid */
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px;
  --kinetic-duration-micro: 120ms; --kinetic-duration-ui: 240ms;
}

[data-theme="dark"] { /* 12-step dark scale */ }
```

#### 5.5 Vector Conversion (AI Raster → Production-Grade SVG)

`references/vector-conversion.md` yükle. 3 yol: otomatik trace (vtracer) · hibrit (önerilen) · tam manuel rebuild. Script: `vector_trace.py`.

**2026 ek not**: Nano Banana 2 ve Grok Imagine çıktıları daha temiz geliyor; hybrid workflow %95'e kadar kapsama ulaşabiliyor. Buna rağmen production SVG için designer Pen Tool cleanup zorunlu (telif açısından da — sadece AI çıktı USA Thaler v. Perlmutter sonrası telif altına alınmıyor, insan-yazarı katkısı gerekiyor).

#### 5.6 Print Production Specification

`references/print-production.md` yükle. Pantone PMS C/U + CMYK conversion + paper stock + foil/emboss/letterpress spec. Script: `pantone_matcher.py`. **Cloud Dancer** (Pantone 2026 COY) paper stock için default neutral warm seçeneği — uncoated cotton letterpress'te Crane's Lettra ile güzel eşleşir.

#### 5.7 Motion Language Specification

`references/motion-language.md` yükle. Arketip-bağlı motion personality + duration ladder + easing palette. Script: `motion_spec_generator.py --emit-lottie`. **2026 ekleme**: Route 4 Adaptive seçildiyse motion spec'e **morphing transitions** dahil edilir (core spine sabit, outer shell transition logic).

#### 5.8 Adaptive Identity Rules *(Route 4 seçildiyse zorunlu)*

`references/adaptive-identity.md` yüklenmiş olmalı. Üretilir:
- **Core spine spec** — logo'nun değişmeyen DNA'sı (shape, geometric anchor)
- **Variable parameters** — neye göre değişir (time / geo / persona / season / content category)
- **Transition rules** — nasıl değişir (instant / animated / fade)
- **Constraint system** — core %X değişmezse equity korunuyor mu? (önerilen: core ≥ 60% consistent)
- **Implementation spec** — CSS custom properties / Figma Variants / programmatic SVG

#### 5.9 Sonic Identity Brief *(tüm route'lar için)*

`references/sonic-identity.md` yükle. 2026'da voice-first UI (Grok Voice, Gemini Live, ChatGPT Voice) markaları audio logo bekliyor. Üretilir:
- **Sonic logo brief** — 1-3 saniye, arketip-uygun mood (sage → clean chord, outlaw → distortion, innocent → bell tone)
- **Earcon library** — 5-7 UI interaction sound (notification, success, error, transition, onboarding)
- **Voice persona guidance** — voice synth parametreleri (pitch, tempo, warmth) AI voice model'lere brief

#### 5.10 AI Discoverability Layer *(tüm route'lar için)*

`references/ai-discoverability.md` yükle. 2026'da markalar, AI agent'lar tarafından nasıl "okunduğu" konusunda ölçüm yapıyor (brand SEO'nun yeni versiyonu). Üretilir:
- **Brand description prompt** — markanızın ChatGPT/Claude/Gemini'ye tek paragrafta **en doğru** anlatımı (10-20 kelime)
- **Entity knowledge card** — brand Wikipedia/Wikidata style structured summary
- **LLM-safe name + logo description** — voice alias (spelling vs pronunciation), alt text spec
- **Agent-era brand manifesto** — markanın AI aracıyla nasıl temsil edilmek istediği

#### 5.11 C2PA Content Credentials & AI Provenance

`references/c2pa-provenance.md` yükle. 2026'da AI ile üretilmiş brand assets için **provenance disclosure** regulatory gereklilik (EU AI Act 2024). Üretilir:
- Nano Banana 2 çıktıları SynthID + C2PA otomatik gömülü gelir — bu korunur
- Vector conversion sonrası provenance metadata **SVG `<metadata>`** bloğuna taşınır
- Brand asset releases için **AI disclosure statement** template
- Trademark başvurusunda insan-yazarı katkı dökümü (Thaler v. Perlmutter defansı)

#### 5.12–5.18 Klasik Output Template Bölümleri

12. Final Çıktı Paketi (`references/output-template.md` 18-bölüm şablonu)
13. Forbidden Variations (ne yapmama listesi)
14. Implementation Checklist (1 hafta / 1 ay / 3 ay / 12 ay)
15. Neuro-Inclusive Design Audit (CVD, motion sensitivity, cognitive load)
16. Competitive Audit Summary (top 5 rakibe yan yana yerleştirme)
17. Bibliography & References (kullanılan ajans/tasarımcı/standart atfı)
18. Next Steps + Production Brief (tasarım stüdyosu handoff dökümü)

---

## Karar Çerçevesi: 4-Test Doktrini (Chermayeff & Geismar & Haviv + 2026)

Her sembol önerisi şu dört testten geçmek **zorundadır**:

1. **APPROPRIATENESS (Uygunluk)** — Marka esansı + arketip uyumlu mu?
2. **DISTINCTIVENESS (Ayrıştırıcılık)** — Sektörde benzersiz mi? Top 5 rakibe yan yana koyduğumuzda öne çıkıyor mu?
3. **MEMORABILITY (Akılda kalıcılık)** — 5 saniye gösterip kapat. 1 dakika sonra çizebiliyor musun?
4. **TIMELESSNESS × ADAPTABILITY (2026 ekleme)** — 50 yıl sonra aynı güçle duracak mı? AYNI ZAMANDA: 16px favicon'dan 6 metrelik sergiye, voice UI'dan AI agent description'a kadar tüm bağlamlara adapte olabiliyor mu? (Sagi Haviv timelessness + 2026 adaptive doktrini)

> Failure: testlerden birinde "hayır" → route eleme adayı, alternatif öneri sun.

---

## KESİN KIRMIZI ÇİZGİLER (DETAY: `references/red-lines.md`)

1. **KLİŞE YASAĞI (Literal Design)** — Sektör klişeleri: gayrimenkul → çatı/ev ✗, dişçi → diş ✗, kahveci → fincan ✗, teknoloji → devre kartı ✗, sağlık → kalp/stetoskop ✗, fintech → kredi kartı/dolar ✗, eğitim → diploma/baykuş ✗. **Her zaman zeki metafor bul**.

2. **KOPYA YASAĞI** — Referans repolar sadece zihniyet için. Promptlarda "in the style of Apple logo" gibi mevcut marka referansı ASLA.

3. **METİN YASAĞI (symbolic logomark için)** — Route 1 Kinetic Wordmark hariç, sembolde text üretme. Nano Banana 2 text rendering çok iyi olsa da, **marka adı typography adımında gerçek fontla lock edilir** (telif + tutarlılık için).

4. **GRADIENT/3D/SHADOW YASAĞI (core logomark için)** — Modern logo doktrini düz 2D vektör. Semantic negative ile ifade edilir. Sub-brand/app icon variant olarak Adım 5'te eklenebilir ama core mark için yasak.

5. **STOCK-ICON İSTEĞİ** — Reddet ve nedenini açıkla: özgün kimlik için stok ikon kullanılamaz (trademark, ayrıştırıcılık, "AI slop" algısı).

6. **AI PROVENANCE İHLALİ (2026 yeni)** — AI-generated raster'ı SynthID/C2PA metadata olmadan "orijinal human work" olarak sunmak EU AI Act ve USPTO regulatory ihlali. C2PA metadata vector conversion sonrası korunur.

---

## brand-maker Composability Sözleşmesi (Değişmedi)

`brand-maker → brand-visual handoff` format aynı. brand-maker'dan gelen brief varsa Adım 2 interview atla/kısalt, Adım 3'e geç.

**brand-visual → downstream handoff**:
- Logomark SVG specification (concept + AI-generated reference + C2PA metadata)
- 12-step color tokens (light + dark + Cloud Dancer neutral)
- Typography spec (display + body + scale + kinetic spec if Route 1)
- Design token JSON (W3C DTCG compliant)
- Adaptive rules JSON (Route 4 seçildiyse)
- Sonic logo brief
- AI discoverability metadata

Bu çıktılar `medmarketing`, `alegria-prompt-engine`, `carbon-pptx`, `carbon-html-report` için kanonik input.

---

## Çıktı Sözleşmesi

| Boyut | Beklenti |
|---|---|
| **Format** | Markdown — başlıklar, tablolar, kod blokları (CSS, JSON), markdown image syntax |
| **Dil** | Birincil: kullanıcı brief dili (TR/EN). AI promptlar **her zaman İngilizce**. Stratejik rasyoneller TR + EN çift sunumda |
| **Uzunluk** | Adım 1: 200 · Adım 2: 5 soru · Adım 3: 1.200–1.500 kelime (4 route deep) · Adım 4: 400 kelime (1 UMMP + 4-model notes) · Adım 5: 3.500–5.500 kelime (full 18-bölüm identity report) |
| **Ton** | Otoriter, vizyoner, analitik. Pentagram brief tonunda. |
| **Etkileşim disiplini** | Her adımdan sonra kullanıcı yanıtını bekle. Tüm adımları tek mesajda dökme. |

---

## Tipik Çağrı Örnekleri

### Çağrı A — Sıfırdan (yeni marka)
**Kullanıcı**: "Yeni bir B2B AI platformu için marka kimliği. Adı 'Verity'. Konum: AI guvernansı ve güvenilir kaynak doğrulama."

**Skill akışı**:
1. Adım 0: 4 mandatory referansı yükler (route-strategies, red-lines, 2026-trends, output-template).
2. Adım 1: brief'te marka adı + sektör + konum var → `logo-taxonomy.md`, `archetypes.md`, `ai-prompt-engineering.md`, `ai-discoverability.md` ek yüklenir.
3. Adım 2: Sokratik 5 soru (arketip onayı, primary stage + adaptive-value sorusu, tabu, tonalite). **BEKLE**.
4. Adım 3: 4 route sun. **BEKLE**.
5. Adım 4: Seçilen route üzerine 1 UMMP + 4-model execution notes. **BEKLE**.
6. Adım 5: Görsel onaylandıktan sonra 18-bölüm full identity report.

### Çağrı B — brand-maker'dan continuation
**Kullanıcı**: "brand-maker'dan **Lumora** ismini seçtik. Visual identity'yi inşa edelim."

**Skill akışı**:
1. Adım 0: Mandatory referansları yükler. brand-maker brief'inden arketip ve hedef pazarı çeker.
2. Adım 1: Brief zaten zengin → ek referanslar otomatik yüklenir.
3. Adım 2'yi **atla** ya da yalnızca primary stage + adaptive-value + eksik bilgi. **BEKLE**.
4. Adım 3-4-5 standart akışı.

### Çağrı C — Route 4 Adaptive-first (yeni 2026 senaryo)
**Kullanıcı**: "Şirketimiz için adaptive/morphing logo istiyoruz — Nike/Adobe gibi."

**Skill akışı**:
1. Adım 0: Mandatory + `adaptive-identity.md` zorunlu yüklenir.
2. Adım 2: Adım 3. sorunun "bağlamsal davranış" kısmı merkeze alınır.
3. Adım 3: 4 route sunulur, Route 4 **tercih edilen** olarak işaretlenir.
4. Adım 4: UMMP **core spine** üretir (outer shell kuralları ise Adım 5.8'de).
5. Adım 5: 5.8 Adaptive Rules bölümü tam açılımla yazılır (core + variables + transitions + constraints + implementation).

---

## Versiyon ve Limitler

* **v1.3 "Genesis"** — 2026 Adaptive Era (Nisan 2026). **Yeni**:
  - 4. route eklendi: **Adaptive / Living Identity** (Nike, Coca-Cola, Adobe Substance 3D doktrini)
  - **Unified Multi-Model Prompt (UMMP)** mimarisi: tek prompt ile Nano Banana 2 + Grok Imagine Aurora-2 + Nano Banana Pro çalışır; Midjourney fallback addenda ile
  - Nano Banana 2 (Gemini 3.1 Flash Image, 26 Şubat 2026) 2026 primary olarak konumlandırıldı — %50 daha ucuz, 14 ref, 131K context
  - Grok Imagine 1.0 Aurora-2 engine 2026 primary (Flux.1 era kapandı)
  - Quality/Speed/Pro mode disiplini (Grok 3 Nisan 2026 güncellemesi)
  - 2026 design trend library: `references/2026-trends.md` — Fluid identities, warm neo-minimalism, hyperfunctional, earthmarks, kinetic wordmarks, subtle disruption, gothic revival
  - Pantone **Cloud Dancer 2026 COY** Radix scale'e neutral alternative olarak eklendi
  - W3C DTCG design token spec compliance
  - **AI Discoverability layer** (5.10) — LLM/agent era brand recall
  - **Sonic Identity brief** (5.9) — voice-first UI branding
  - **C2PA Content Credentials & AI Provenance** (5.11) — EU AI Act uyumu
  - **CVD (Color Vision Deficiency) layer** renk sisteminde
  - **Neuro-Inclusive Design Audit** output template 15. bölüm
  - **Competitive Audit Summary** output template 16. bölüm
  - Output template 14 → **18 bölüm**
  - Karar çerçevesi 3-test → **4-test** (Timelessness × Adaptability)

* **v1.2** — Multi-model era (Nisan 2026). Nano Banana Pro + Grok Imagine variants. `ai-prompt-engineering.md` 541→810 satır. 5 variant template (A-E). — *v1.3'te basitleştirildi: UMMP + fallback mimarisi.*

* **v1.1** — Production gap (2026 Q1). Vector conversion (vtracer), Pantone matching, Motion language/Lottie. Output template 10→14.

* **v1.0** — İlk sürüm. 3 route, multi-model prompt engineering, Radix 12-step, variable font, favicon scalability.

* **Bilinen limitler (v1.3)**:
  - Skill logo render etmez — AI model dışsal (kullanıcı Nano Banana 2 / Grok Imagine / Midjourney'de çalıştırır).
  - UMMP, her iki 2026 primary'de test edildi ama **Midjourney'de kalite %10-15 düşebilir** (addenda ile kısmen telafi).
  - Grok Imagine Aurora-2 reproducibility orta düzey — precise vector için hybrid approach şart.
  - Adaptive identity Route 4 implementation (CSS/Figma) kod üretir ama production testing designer'a aittir.
  - Sonic identity brief üretir, ses dosyası üretmez — composer/Suno/Udio ile handoff.
  - Pantone matching yaklaşıktır — ΔE CIEDE2000 < 2.0 hedef, fiziksel fan deck doğrulama şart.
  - Trademark/IP clearance kapsam dışı — brand-maker WIPO/USPTO ön-tarama.
  - 16px favicon testi mental simulation + Python heuristic — realfavicongenerator.net zorunlu final test.
  - Multi-language wordmark (Çince/Japonca/Arapça/Kiril) optimizasyonu sınırlı (Latin-centric).
  - AI discoverability metrics henüz dışsal ölçüm aracı yok — brief yoklaması rehberlik amaçlı.

* **Tasarım kararı**: Bu skill **strateji + konsept + AI direction + design system + adaptive rules + sonic brief + AI discoverability + C2PA provenance** üretir. Final production dosyaları (vector cleanup, Lottie animation, press-ready PDF, adaptive logic kodu, sonic composition) tasarım/motion/ses stüdyosu işidir — bu skill o stüdyoya verilecek **kapsamlı production brief**'i hazırlar.

---

## Detaylı Referans Dosyaları

| Dosya | İçerik | Yükleme Tetikleyicisi |
|---|---|---|
| `references/logo-taxonomy.md` | Wheeler 7-tipli + Evamy wordmark + 2026 kinetic sub-type | Logo türü tartışması |
| `references/archetypes.md` | 12 Jung arketipi → görsel dil matrisi | Brand voice / kişilik |
| `references/route-strategies.md` | 4 route detaylı metodoloji (v1.3) | **Mandatory** (Adım 0) |
| `references/ai-prompt-engineering.md` | UMMP formülü, Nano Banana 2 + Grok deep dive, fallback | Adım 4 (her zaman) |
| `references/color-system.md` | Radix 12-step + Cloud Dancer 2026 + WCAG/APCA/CVD | Adım 5 (her zaman) |
| `references/typography-system.md` | Variable font + kinetic spec + type pairing | Adım 5 (her zaman) |
| `references/gestalt-principles.md` | Gestalt yasaları + negative space + paradokslar | Adım 3 (Route 2) |
| `references/design-system-tokens.md` | W3C DTCG semantic tokens, multi-brand, Tailwind/Radix | Adım 5 (deliverable) |
| `references/vector-conversion.md` | Raster → SVG production workflow + C2PA taşıma | Adım 5.5 (her zaman) |
| `references/print-production.md` | Pantone + CMYK + paper + foil/emboss + Cloud Dancer paper | Adım 5.6 (her zaman) |
| `references/motion-language.md` | Arketip motion + duration ladder + easing + Lottie | Adım 5.7 (her zaman) |
| `references/adaptive-identity.md` | **Yeni v1.3** — Fluid/morphing logo spec, Nike/Adobe case'leri | Route 4 veya "adaptive" tetiği |
| `references/ai-discoverability.md` | **Yeni v1.3** — LLM agent brand recall, entity knowledge card | Adım 5.10 (her zaman) |
| `references/c2pa-provenance.md` | **Yeni v1.3** — Content credentials, SynthID, AI disclosure, EU AI Act | Adım 5.11 (her zaman) |
| `references/sonic-identity.md` | **Yeni v1.3** — Audio logo brief, earcon library, voice persona | Adım 5.9 (her zaman) |
| `references/2026-trends.md` | **Yeni v1.3** — 14 trend, arketip mapping, sektör uygunluğu | **Mandatory** (Adım 0) |
| `references/red-lines.md` | Sektör klişe matrisi + alternatif metaforlar + 2026 provenance | **Mandatory** (Adım 0) |
| `references/output-template.md` | **18-bölüm** identity report template (v1.3) | **Mandatory** (Adım 0) |
| `references/bibliography.md` | Kanonik kaynaklar + ajans atıf protokolü + 2026 kaynakları | Atıf gerektiğinde |

| Script | İşlev |
|---|---|
| `scripts/palette_generator.py` | Base color → Radix 12-step + Cloud Dancer neutral (OKLCH) |
| `scripts/wcag_contrast.py` | WCAG AA/AAA + APCA Lc + **CVD simulation** |
| `scripts/prompt_composer.py` | Structured params → UMMP (tek prompt) + fallback addenda |
| `scripts/favicon_simulator.py` | Logo SVG/PNG → 16/32/64/192/512 + monokrom + dark test |
| `scripts/vector_trace.py` | Raster → production SVG (vtracer/inkscape/potrace) + C2PA taşıma |
| `scripts/pantone_matcher.py` | HEX → Pantone PMS C/U + CMYK (ΔE CIEDE2000) + Cloud Dancer |
| `scripts/motion_spec_generator.py` | Arketip + tonality → motion personality + Lottie skeleton + adaptive transitions |

---

> **Final hatırlatma**: Bu skill bir interactive protokoldür. **Tüm adımları tek seferde dökme**. Her adım sonunda kullanıcının yanıt vermesini, dosya yüklemesini veya iterate komutu vermesini bekle. Pentagram'da bir sanat yönetmeni nasıl müşteriyle masada otururdu — o ritimde çalış. 2026 doktrini: *"Logos no longer perform as museum pieces. They behave as open canvases with a strong frame."*
