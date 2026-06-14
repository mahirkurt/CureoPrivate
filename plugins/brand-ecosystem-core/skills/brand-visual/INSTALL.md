# INSTALL.md — brand-visual

**Version**: 1.3.0
**Release Date**: 2026-04-24
**Release Name**: Genesis — 2026 Adaptive Era

**Changelog Özeti (v1.2 → v1.3)**:

v1.3 Genesis, 2026'nın "Adaptive Era" paradigma değişimine yanıt veren büyük bir yeniden yapılandırmadır. Markalar artık tek statik logo değil, AI agent'larla konuşan + adaptif bağlamlara evrilen + voice-first UI'larda duyulan + regulatuar provenance içeren **çok katmanlı kimlik sistemleri**.

**Yeni Route**:
- **Route 4 — Adaptive / Living Identity**: Nike dynamic logo pairings, Adobe Substance 3D cube states, Coca-Cola contextual variants, Google Doodle doktrini. Core spine (immutable DNA) + Variable shell (context-responsive) mimarisi.

**Yeni Prompt Mimarisi — UMMP (Unified Multi-Model Prompt)**:
- Eski 5-variant (A-E) model-spesifik prompt architecture → **TEK UMMP + model execution notes**
- Nano Banana 2 (Gemini 3.1 Flash Image, 26 Şubat 2026, $0.067/2K) ve Grok Imagine Aurora-2 (3 Nisan 2026 Speed/Quality/Pro modes) aynı prompt grammar'ına converge etti
- 7-element UMMP grammar: subject framing / form construction / style anchor / technical spec / composition / semantic positive-constraint color / 2026 trend anchor
- Parameter flag yok; narrative paragraph + semantic positive-constraint

**Yeni Referans Dosyaları**:
- `references/2026-trends.md` — 14 curated trend library (Adım 0 zorunlu yükleme)
- `references/adaptive-identity.md` — Route 4 dayanak, core spine + variable shell architecture
- `references/ai-discoverability.md` — Agent-era branding (Adım 5.10)
- `references/c2pa-provenance.md` — EU AI Act + C2PA Content Credentials (Adım 5.11)
- `references/sonic-identity.md` — Voice-first era sonic logo brief (Adım 5.9 opsiyonel)

**Yeni Output Tipleri**:
- `adaptive_identity_spec` (Route 4 brief)
- `ai_discoverability_spec` (20-word brand description + Schema.org JSON-LD + manifesto)
- `c2pa_provenance_spec` (provenance chain + EU AI Act disclosure + trademark package)
- `sonic_identity_brief` (sonic logo + earcon library + voice persona)

**Yeni Quality Gates**:
- G11: Adaptive Identity compliance (Route 4)
- G12: UMMP grammar compliance (mandatory)
- G13: AI Discoverability layer (mandatory)
- G14: C2PA Content Credentials (mandatory)
- G15: Neuro-Inclusive Design audit
- G16: Sonic Identity Brief

**2026 Trend Library Integration**:
14 trend: Adaptive Fluid Identity · Warm Neo-Minimalism · Hyperfunctional Editorial Overlay · Kinetic Typography Wordmarks · Earthmark Organic · Subtle Disruption Signature · Gothic/Folklore Revival · Tactile Dimensional Refinement · Surreal Collage · Pantone Cloud Dancer 2026 COY · Generative Morphing · Neuro-Inclusive Design · Coauthored Open Canvas · AI Discoverability.

**SKILL.md Güncellemeleri**:
- 3-route → 4-route sistem
- 4-test karar çerçevesi (Timelessness × Adaptability eklendi)
- 6 red lines (AI Provenance violation eklendi)
- Adım 4 UMMP output
- Adım 5.8-5.11 yeni alt bölümler

**Upgrade Path**: v1.0/1.1/1.2 kullanıcıları kırılma yaşamaz. Yeni adımlar (Route 4, 5.8, 5.9, 5.10, 5.11) opsiyonel olarak entegre — skill brief'e ve tercihe göre hangi adımları aktif edeceğine karar verir. UMMP eski 5-variant'ı **deprecate** ediyor (breaking change), ama kalite çok daha yüksek ve paralel dual-model native 2026 workflow'u.

**Changelog Özeti (v1.1 → v1.2)**:
- `references/ai-prompt-engineering.md` genişletildi: 541 → 810 satır (+269)
- **Nano Banana Pro** (Gemini 3 Pro Image) entegrasyonu — wordmark + mockup composition için yeni primary model (narrative paragraph prompt disiplini)
- **Grok Imagine 1.0** (xAI) entegrasyonu — Route 3 Disruptor + rapid moodboarding için yeni primary (contextual typography gücü)
- Route-based variant allocation matrisi: her route'un kendi primary modeli var
- Model-aware prompt quality checklist — her model için ayrı kontrol listesi
- Semantic negative prompting disiplini (Nano Banana Pro için "no gradient" yerine pozitif karşıt tarif)
- Legacy variants (Midjourney V7, Niji 7, Ideogram, DALL-E 3, Flux) geriye uyumlu korundu

**Upgrade Path (v1.1 → v1.2)**: Mevcut brand-visual çağrıları eski şekilde çalışmaya devam eder; Adım 4'te sadece variant seçenekleri genişlemiş olur.

---

## Genel Bakış

`brand-visual`, claude.ai-native bir interaktif protokol skill'idir. Pentagram / Koto / Wolff Olins seviyesinde bir Marka Stratejisti + Sanat Yönetmeni + Tasarım Sistemleri Mimarı zekâsını, 4 etkileşimli adımda bir marka kimliği sistemine dönüştürür.

**Composability**: `brand-maker` skill'inin verbal identity (marka adı + arketip + stratejik çıpa) çıktısını **doğrudan girdi olarak kabul eder**. brand-maker → brand-visual canonical pipeline.

---

## Dosya Yapısı

```
brand-visual/
├── SKILL.md                                  (Ana protokol — etkileşimli 4 adım)
├── INSTALL.md                                (Bu dosya)
├── skill-manifest.yaml                       (SMP v1.0 composability sözleşmesi)
│
├── references/
│   ├── route-strategies.md                   (Mandatory — 3+1 route metodolojisi, v1.3 Route 4 eklendi)
│   ├── red-lines.md                          (Mandatory — sektör klişe matrisi)
│   ├── output-template.md                    (Mandatory — final rapor şablonu)
│   ├── archetypes.md                         (12 Jung arketipi → görsel dile çeviri)
│   ├── logo-taxonomy.md                      (Wheeler 7-tipli + Evamy wordmark)
│   ├── ai-prompt-engineering.md              (v1.3 UMMP + Nano Banana 2 + Grok Aurora-2 + MJ fallback)
│   ├── color-system.md                       (Radix 12-step + WCAG/APCA + Cloud Dancer 2026 COY)
│   ├── typography-system.md                  (Variable font + type pairing)
│   ├── gestalt-principles.md                 (Closure, continuity, figure-ground)
│   ├── design-system-tokens.md               (W3C tokens, Tailwind, multi-brand)
│   ├── vector-conversion.md                  (v1.1 — vtracer production SVG)
│   ├── print-production.md                   (v1.1 — Pantone + paper + finishing)
│   ├── motion-language.md                    (v1.1 — Brand motion + Lottie)
│   ├── 2026-trends.md                        (v1.3 — Mandatory Adım 0 yükleme, 14 trend library)
│   ├── adaptive-identity.md                  (v1.3 — Route 4 dayanak, core spine + variable shell)
│   ├── ai-discoverability.md                 (v1.3 — Adım 5.10 agent-era branding zorunlu)
│   ├── c2pa-provenance.md                    (v1.3 — Adım 5.11 EU AI Act + C2PA zorunlu)
│   ├── sonic-identity.md                     (v1.3 — Adım 5.9 voice-first era opsiyonel)
│   └── bibliography.md                       (Kanonik kaynak atıf protokolü)
│
├── scripts/
│   ├── palette_generator.py                  (Base color → 12-step Radix scale)
│   ├── wcag_contrast.py                      (WCAG 2.x + APCA Lc kontrast hesabı)
│   ├── prompt_composer.py                    (7-element formül → multi-model prompt)
│   └── favicon_simulator.py                  (Logo → 16/32/64/192/512 + checklist)
│
└── assets/
    └── archetype-wheel.svg                   (12 arketip görsel referans tekerleği)
```

---

## Kurulum

### claude.ai (web/desktop/mobile) — Önerilen
1. Bu skill folder'ını download veya clone edin.
2. claude.ai > Settings > Capabilities > Skills (or Features > Skills) → "Upload custom skill"
3. `brand-visual` folder'ını upload edin.
4. Skill otomatik olarak ilgili konuşmalarda devreye girer (description tetikleyicileri ile).

### Claude Code (CLI)
```bash
# Skill'i ~/.claude/skills/ altına kopyalayın
cp -r brand-visual/ ~/.claude/skills/

# Doğrulama:
ls ~/.claude/skills/brand-visual/SKILL.md
```

### Programatik (Anthropic API)
Skill içeriği context'e load edilebilir:
```python
import anthropic, pathlib

skill_md = pathlib.Path("brand-visual/SKILL.md").read_text()
# system message'a embed et:
system_prompt = f"<available_skill>\n{skill_md}\n</available_skill>\n\n[other system context]"
```

---

## Bağımlılıklar

### Skill Çekirdeği
**Sıfır external dependency** — pure markdown protokolü ve Python stdlib scripts.

### Opsiyonel Script Dependencies
`scripts/favicon_simulator.py` SVG/PNG render için:

```bash
# Pillow (raster işleme — PNG/JPG input + monochrome conversion)
pip install Pillow

# CairoSVG (SVG → PNG rasterization)
pip install cairosvg
```

**Veya** sistem alternatifleri (CairoSVG yerine):
```bash
# Linux
apt install librsvg2-bin   # rsvg-convert
apt install imagemagick     # magick / convert

# macOS
brew install librsvg
brew install imagemagick
```

Eğer hiçbir dependency yoksa, `favicon_simulator.py` otomatik olarak **mental simulation checklist** moduna düşer (dependency-free).

### External AI Tools (kullanıcı tarafından)
brand-visual prompt üretir, AI generation'ı kullanıcı dış araçlarda yapar:

| Tool | Kullanım | Erişim |
|------|----------|--------|
| **Midjourney V7/V8** | Primary logo concept generation | https://www.midjourney.com (subscription) |
| **Niji 7** | Illustrated/character logos (Route 3) | Midjourney içinde `/imagine --niji 7` |
| **Flux.1 dev/schnell** | Open-source alternative | fal.ai, Replicate, ComfyUI local |
| **DALL-E 3** | Text rendering specialty | ChatGPT Plus / Azure OpenAI |
| **Ideogram 2.0** | Typography-heavy posters | https://ideogram.ai |

---

## brand-maker ile Composability

Eğer brand-maker da kuruluysa, doğal pipeline:

```
1. Kullanıcı: "Yeni bir B2B AI agent platformu için isim ve görsel kimlik istiyorum"
   ↓
2. brand-maker tetiklenir → 5 finalist isim + verbal identity raporu
   ↓
3. Kullanıcı: "Lumora ismiyle devam edelim, görsel kimliği inşa et"
   ↓
4. brand-visual tetiklenir → brand-maker raporundan çekiyor
   - Stratejik çıpa, arketip, sektör otomatik anlaşılıyor
   - Sokratik Adım 2 yalnızca primary stage + 1-2 eksik bilgiyi sorar
   ↓
5. Adım 3-4-5 standart akış → Visual Identity System raporu
```

`skill-manifest.yaml` içinde `composition.pipe_from` brand-maker'ı declare eder.

---

## SMP v1.0 Validation

Skill manifest'i `smp-orchestrator` ile doğrulanmış, ekosistem grafına entegre:

```bash
python smp-orchestrator/scripts/smp.py validate brand-visual/skill-manifest.yaml
# [PASS] brand-visual v1.0.0 — All checks passed.

python smp-orchestrator/scripts/smp.py describe <ecosystem-dir> brand-visual
# Inputs: 3 (1 required) | Outputs: 4 | pipe_from: 1 (brand-maker)
# pipe_to: 4 (carbon-pptx, carbon-html-report, medmarketing, alegria-prompt-engine)
```

---

## Quick Test (Doğru Kurulu mu?)

Bu prompt'la skill'i test edin:

> "Yeni bir DTC kahve markası için marka kimliği oluşturmak istiyorum. Adı 'Curio'. Kahveyi bir keşif aracı olarak konumluyoruz."

Beklenen davranış:
1. **Adım 0**: Skill `route-strategies.md`, `red-lines.md`, `output-template.md` dosyalarını yükler.
2. **Adım 2**: Sokratik 4-5 soru sorar (arketip, primary stage, tabular, tonalite). **Sonra durur, yanıtınızı bekler**.
3. Yanıtlar geldikten sonra **Adım 3**: 3 stratejik route sunar. **Yine durur**.
4. Route seçildikten sonra **Adım 4**: 3 AI prompt variant. **Durur**.
5. AI çıktıları onaylandıktan sonra **Adım 5**: Tam Visual Identity System raporu.

Eğer skill **tüm adımları tek seferde dökerse** veya **yanıtınızı beklemezse**, SKILL.md adım disiplini açısından doğru yüklenmemiş demektir.

---

## Script Test Örnekleri

### palette_generator.py
```bash
# Base color → 12-step light + dark palette (markdown table)
python scripts/palette_generator.py "#5B5BD6" --name indigo

# CSS custom properties output
python scripts/palette_generator.py "#5B5BD6" --name brand --format css

# W3C Design Tokens JSON
python scripts/palette_generator.py "#5B5BD6" --name brand --format json
```

### wcag_contrast.py
```bash
# Quick check
python scripts/wcag_contrast.py "#5B5BD6" "#FFFFFF"

# Detailed compliance breakdown
python scripts/wcag_contrast.py "#4747B5" "#FCFCFD" --verbose

# Markdown output (rapor için)
python scripts/wcag_contrast.py "#2E2E80" "#F9F9FB" --format markdown
```

### prompt_composer.py
```bash
# Tek model prompt
python scripts/prompt_composer.py \
  --subject "letter C formed by two nested arcs suggesting curiosity" \
  --logo-type "minimalist monogram" \
  --style-anchor "Paul Rand,Sagi Haviv" \
  --color "deep indigo on pure white" \
  --sector coffee \
  --model midjourney

# 5 model varyantı (paralel exploration için)
python scripts/prompt_composer.py [args] --model all

# Interactive mode
python scripts/prompt_composer.py --interactive
```

### favicon_simulator.py
```bash
# Logo dosyasından favicon paketi + report.md
python scripts/favicon_simulator.py logo.svg --output-dir ./favicon-test/

# Sadece checklist (dependency-free)
python scripts/favicon_simulator.py --checklist-only

# Custom sizes
python scripts/favicon_simulator.py logo.svg --sizes 16,32,64,192,512
```

---

## Tasarım Karar Kayıtları

### Neden Etkileşimli (Non-Monolithic)?
Bir ajans toplantısında brief → konsept → revize → karar 1 dakikada olmaz. brand-visual'ı **tek-shot output** olarak yapsaydık, kullanıcının *gerçekten istediği* şeyle uzaklaşma riski yüksekti. Etkileşimli protokol, **müşteri-ajans diyaloğunun** disiplinini taşır. Pentagram'da Michael Bierut müşteriyle masada otururdu — biz de o ritmi simüle ediyoruz.

### Neden 3 Route?
- **1 route**: Müşteriye "tek seçenek" sunmak ajans işi değil — düşünme tembelliği sinyali.
- **2 route**: Genelde "iyi vs daha iyi" diyalektiği yaratır — kullanıcı eleyemez.
- **3 route**: Klasik design school yöntemi — biri konservatif, biri dengeli, biri cesur. Kullanıcı **strategy aralığında** karar verir.
- **4+ route**: Karar yorgunluğu (decision fatigue), zayıf brief sinyali.

### Neden AI'da Vector Output Üretmiyor?
2026 itibariyle hiçbir AI model **production-grade clean SVG** üretmez. Vtracer, LogicAI gibi araçlar emerging ama tutarlılık yok. brand-visual'ın felsefesi: **AI = brief, designer = production**. Konsep referansı için MJ/Niji/Flux raster çıktısı yeterli; final logo Adobe Illustrator/Figma'da manuel rebuild edilir. Bu, telif sorunu da çözer (insan-modifiye = telif altında).

### Neden Radix Colors?
Tasarım sistemleri için 2026'nın **fiilen standardı**. 12-step semantic scale + matematiksel tutarlılık + light/dark mode otomatik mapping + APCA Lc 60/90 garantisi. Tailwind v4, Figma Variables, shadcn/ui hepsi Radix patterns'a uyuyor. Ad-hoc HEX scale önermek 2017 mentalitesi.

### Neden Variable Fonts?
2024+ markaların standardı. Tek dosyada tüm ağırlıklar (HTTP request azalır), runtime'da axes interpolation (logotype lock-up custom weight), system font fallback uyumlu. Static font set önermek (Bold, Regular, Light dosyalar) eski-mantık.

---

## Bilinen Limitler

1. **Vector output yok** — AI raster (PNG) verir; SVG conversion designer işidir (Adobe Illustrator Image Trace, Vector Magic, Inkscape, ya da manual redraw).

2. **Trademark clearance kapsam dışı** — brand-maker'dan WIPO/USPTO/TÜRKPATENT URL'leri kullanılır; brand-visual marka tescili yapmaz.

3. **Live brand mockup üretmez** — output-template.md "Application Mockup Briefs" bölümü tasarımcıya brief verir; web hero, app icon, business card vb. designer Figma'da üretir.

4. **Motion brand language minimal** — kinetic identity (logo animation, transitions) bu skill'in kapsamı dışında. After Effects / Lottie animation tasarım stüdyosu işidir.

5. **Print production spec vermez** — pantone color matching, paper stock, embossing/foil specs tasarımcı + matbaa diyaloğunda netleşir.

6. **Multi-language wordmark testi yok** — wordmark Latin alphabet için optimize edilir; Çince/Japonca/Arapça/Kiril için ayrı script ve typography uzmanı gerekir.

---

## Changelog

### v1.1.0 — 2026-04-15 — Production-Grade Edition

**Yeni özellikler — production gap kapatma**:
- **Vector conversion**: `scripts/vector_trace.py` — vtracer/inkscape/potrace backend wrapper, 6 logo preset (logo-color/logo-mono/bw-clean/pixel-art/sketch/high-detail), automatic backend detection, post-processing recommendations. AI raster (PNG) → production-grade SVG geçişini sistematize eder.
- **Pantone PMS matching**: `scripts/pantone_matcher.py` — HEX → en yakın Pantone PMS C/U via ΔE CIEDE2000 algoritması. ~250 curated PMS spot color database (Pantone Formula Guide v6, 2024 edition'dan), CMYK approximation (GRACoL profile), tolerance interpretation (Pantone resmi ≤2.0 ΔE00 hedefi).
- **Brand motion language**: `scripts/motion_spec_generator.py` — 12 arketip × motion personality mapping (durations + easing curves + animation primitives + no-go zones), 10 tonality modifier (premium/luxury/fast/snappy/calm/minimal/bold/cesur/sıcak/soğuk), Lottie Specification v1.0 compliant JSON skeleton emission for After Effects designer hand-off.
- **3 yeni reference dosyası**: `vector-conversion.md` (~520 satır), `print-production.md` (~520 satır), `motion-language.md` (~480 satır)
- **Output template expansion**: 10 → **14 bölüm** (8. Vector Spec, 9. Print Spec, 10. Motion Spec eklendi; mevcut bölümler renumber)
- **3 yeni quality gate**: G8 (Vector conversion production-readiness, mandatory), G9 (Pantone PMS matching coverage, mandatory), G10 (Motion language specification, optional)
- **5 yeni manifest output**: `production_vector_svg`, `pantone_matching_report`, `print_production_spec`, `motion_language_spec`, `lottie_skeleton`
- **Yeni external tool integrations**: vtracer 0.6.x, Adobe Illustrator (manuel cleanup), Adobe AE + Bodymovin/LottieFiles plugin, Pantone Connect

**Backward compatibility**:
- v1.0.0 ile **tam uyumlu** — tüm yeni outputs `optional: true`
- Mevcut interactive 4-adım protokol değişmedi (Adım 5 internal expansion: 5.5 Vector / 5.6 Print / 5.7 Motion / 5.8 Final)
- v1.0 raporları v1.1 skill ile re-generate edilebilir; ek bölümler otomatik üretilir

**Bilinen ek limitler (v1.1 itibarıyla)**:
- Vector trace **assist eder**, designer manuel cleanup şart (telif + production-grade için)
- Pantone matching **yaklaşıktır** — production'da fiziksel fan deck + D50 lighting doğrulama şart
- Motion spec **brief üretir**, animasyonu üretmez — designer After Effects'te detaylandırır

### v1.0.0 — 2026-04-15 — Initial Release

**Yeni özellikler**:
- 4-adım etkileşimli protokol (Sokratik Discovery → 3 Route → AI Prompt → Design System)
- Radix 12-step renk sistemi (palette_generator.py, OKLCH-based)
- WCAG 2.x + APCA contrast checker (wcag_contrast.py)
- Multi-model AI prompt composer (Midjourney V7/V8, Niji 7, Flux, DALL-E 3, Ideogram)
- Favicon scalability simulator (16/32/64/192/512 + monochrome)
- 12 Jung arketipi → görsel dile çeviri matrisi (archetypes.md)
- Wheeler 7-tipli logo taksonomisi + Evamy wordmark anatomisi (logo-taxonomy.md)
- 13 sektör için klişe matrisi + alternatif metafor önerileri (red-lines.md)
- W3C Design Tokens Format Module uyumlu JSON export
- Tailwind v4 + shadcn/ui integration patterns (design-system-tokens.md)
- brand-maker ile composability (skill-manifest.yaml SMP v1.0)
- Pipe_to: carbon-pptx, carbon-html-report, medmarketing, alegria-prompt-engine
- 16 kanonik kaynak akademik bibliography

**Tasarım kararları**:
- Vector trace post-processing kullanıcıya bırakıldı (Adobe Illustrator / Vector Magic önerildi)
- AI promptlar her zaman İngilizce; rasyoneller TR + EN bilingual
- Etkileşimli ritim (Pentagram brief flow simulation)
- Sektör-spesifik negative listeleri (red-lines.md → prompt_composer.py)

---

## Katkı ve Geri Bildirim

Bu skill bir **living document**'tir. Aşağıdaki konularda öneri/iyileştirme:

- Yeni sektör klişe entrieleri (red-lines.md genişletme)
- Modern designer/agency style anchor ekleme (ai-prompt-engineering.md)
- Yeni AI model entegrasyonu (Imagen 4, Stable Diffusion 4 vb.)
- Yeni token formatı (Style Dictionary export, Figma plugin sync)
- Multi-language typography rehberleri (Çin, Japon, Arap dünyası)

Versiyon bumps:
- **Patch (1.0.x)**: Bug fix, küçük doc düzeltmeleri
- **Minor (1.x.0)**: Yeni reference dosyası, yeni script, yeni AI model entegrasyonu
- **Major (x.0.0)**: Protokol akışı değişikliği, breaking schema değişikliği
