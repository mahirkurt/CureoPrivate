# Edupedia 3.0.0 — Derin Motor + Şema Yükseltmesi (Tasarım Spec'i)

**Tarih:** 2026-07-06
**Durum:** Onaylandı (brainstorming) → writing-plans'e hazır
**Kapsam:** `paideia` plugin'inin `edupedia`'ya yeniden adlandırılması + flagship skill `carbon-paideia`'nın (2.8.0) `carbon-edupedia`'ya (3.0.0) derin motor/şema yükseltmesi; üç araştırma-temelli zenginleştirme ekseni (içerik zenginliği · Carbon estetik mükemmelliği · ADHD oyunlaştırma), bir QA agent'ı ve iki hook.

> **Not:** Bu spec, üç paralel web-araştırma koşumunun (kaynak-atıflı) bulgularını somut bir yapı sözleşmesine dönüştürür. Araştırma bulguları §10'da özetlenir. `carbon-edupedia` skill'inin **pedagojik davranışı korunur ve genişletilir** — mevcut 8 mod ve mevcut 11 kalite kapısı kaldırılmaz; yeni segment tipleri, iki yeni kapı ve marka yeniden adlandırması eklenir.

---

## 1. Hedefler ve hedef-olmayanlar

**Hedefler:**
1. Plugin'i `edupedia` markasına taşı (dizin, manifest, marketplace, namespace, prose); flagship skill'i `carbon-edupedia`'ya taşı.
2. Üç araştırma eksenini somut, uygulanabilir çözümlere dönüştür: (a) içerik zenginliği, (b) Carbon estetik mükemmelliği, (c) ADHD oyunlaştırma/akış.
3. Motoru (`assets/module-template.html`) ve `MODULE_DATA` şemasını dört yetenek kümesiyle (A oyunlaştırma omurgası · B derin öğretim · C etkileşimli manipülatifler · D erişilebilirlik+tekrar) genişlet.
4. İki yeni validator kapısı (G-FLOW, G-CARBON-GRID) → toplam 13 kapı.
5. Bir modül-denetçisi (QA) agent'ı ve iki hook (SessionStart preflight + PostToolUse otomatik doğrulama) ekle.
6. Geriye uyumluluğu koru: mevcut MODULE_DATA modülleri kırılmadan çalışsın.

**Hedef-olmayanlar (YAGNI):**
- Canlı PhET/GeoGebra/Desmos/Khan embed veya EBA/MEB içerik gömme — lisans/runtime kısıtı; yalnız `content-enrichment.md`'de "yapılamaz" olarak belgelenir.
- İçerik-zenginleştirme agent'ı (Wikidata/Commons çekimi) — auditor agent seçildi; zenginleştirme yazar-yönergesi olarak kalır.
- Cross-session streak, liderlik tablosu, değişken-oran ödül, geri-sayım timer — atıflı YAPMA listesine girer, motora girmez.
- Türkiye dışı müfredat, genel React UI, statik baskı raporu (→ `carbon-html-report`), slayt (→ `carbon-pptx`).

---

## 2. Mevcut durum (temel alınacak gerçek)

**Motor (`assets/module-template.html`, ~1925 satır):** `render()` dispatch'i şu handler'lara dağıtır: `renderTeach`, `renderMCQ`, `renderMatch`, `renderFillblank`, `renderBreak`, `renderCheckpoint`, `renderChart`, `renderTable`, `renderNumberline`, `renderFlashcards`, `renderOrder`, `renderSorting`, `renderHotspot`, `renderTimeline`, `renderSummary`. **Zaten mevcut:** `renderStreak` (streak-chip), `renderStepper` (progress rayı), `renderBadges`, XP sayacı, productive/expressive motion token'ları (`--ease-expr/entrance/exit`), `prefers-reduced-motion` blokları. Bu yüzden A kümesi mevcut altyapıyı **genişletir**, sıfırdan kurmaz.

**Şema (`references/module-architecture.md`):** `MODULE_DATA = { meta, learner, objectives, rewards, segments[] }`. Segment tipleri: teach, mcq, match, flashcards, fillblank, order, sorting, hotspot, brainbreak, checkpoint (+ chart/table/numberline/timeline görselleri). `meta.sourceCitation` zorunlu.

**Validator (`scripts/validate_module.py`):** 11 kapı — gate_emoji, gate_carbon, gate_a11y, gate_interact, gate_selfcontained, gate_contrast, gate_wellbeing, gate_svg (+figür-svg), gate_audio (earcon+TTS-farkında), gate_token_authority, gate_curriculum (koşullu).

**Pedagojik değişmezler (korunur):** fixed-ratio ödül (değişken-oran reddedilir), no-punitive/no-time-pressure (G-WELLBEING), tek-odak, OTR, mola dozu, emojisiz, WCAG 2.1 AA, @carbon/* token otoritesi.

---

## 3. Yeniden adlandırma

| Öğe | Eski | Yeni |
|---|---|---|
| Plugin dizini | `plugins/paideia/` | `plugins/edupedia/` |
| plugin.json `name`/`displayName` | paideia / Paideia | edupedia / Edupedia |
| Flagship skill dizini | `skills/carbon-paideia/` | `skills/carbon-edupedia/` |
| Skill `name` (SKILL.md + manifest) | carbon-paideia | carbon-edupedia |
| Skill sürümü | 2.8.0 | 3.0.0 |
| Namespace | `paideia:carbon-paideia` / `paideia:start` | `edupedia:carbon-edupedia` / `edupedia:start` |
| Komutlar | `/paideia:*` | `/edupedia:*` |
| marketplace.json kaydı | name paideia, source ./plugins/paideia | name edupedia, source ./plugins/edupedia |
| Prose markası (README, CONNECTORS, start, durum vb.) | paideia | Edupedia |

**Yol referansları:** komut dosyaları `commands/` (1 seviye) → `../CONNECTORS.md`; skill dosyaları `skills/x/` (2 seviye) → `../../CONNECTORS.md` (mevcut kural korunur). Git `git mv` ile dizin taşınır (tarih korunur).

---

## 4. Üç yeni reference dosyası (progressive disclosure)

Skill'in `references/` deseni: her dosya `skill-manifest.yaml`'da `read_when` ile indekslenir; SKILL.md aşamalı açığa çıkarma ile yönlendirir.

### 4.1 `references/content-enrichment.md`
- **Entegre edilebilir (build-zamanı, self-contained):** Wikidata **CC0** olgu-çipleri (QID + retrieval tarihi provenansı; **Maarif kazanım metnine karşı uzlaştırma + no-fabrication zorunlu**); Wikimedia **PD/CC-BY** görsel (CC BY-SA **kaçınılır** — viral SA modülü kirletir; seyrek, Tier-1 yazar-SVG doktrini korunur; zorunlu atıf satırı); native **MathML** (sıfır JS/font/yük); çapraz-oturum aralıklı-tekrar veri modeli.
- **Dürüst "entegre EDİLEMEZ" listesi (over-promise engeli):** canlı PhET (kaynak OSS değil, ~200MB, iframe runtime), GeoGebra (NC + runtime), Desmos (API-key + runtime), Khan (CC BY-NC-SA), **EBA/MEB (FSEK kapalı)**, TÜBİTAK Açık Ders (CC BY-NC-ND — ND remiks yasak). Yalnız statik SVG/PNG export lisans-uyumluysa gömülebilir.
- **Kaynak:** araştırma §10.1 (lisanslar doğrulanmış URL'lerle).

### 4.2 `references/carbon-excellence.md`
15-madde "uzman vs jenerik Carbon" checklist'i (her madde ikili-denetlenebilir): 2x grid yerleşimi, Carbon en-boy oranları (1:1/2:1/2:3/3:2/4:3/16:9), layer-elevation (gölge yalnız yüzen yüzey), contextual layer token'ları, okuma-ölçüsü (sütun-alt-kümesi), bölümler-arası nefes, koreografi grameri (entrance/exit/standard easing), stagger ~20ms/<500ms, expressive akışkan başlık / productive gövde (bileşende karışmaz), aksan-anlam (birincil eylem Blue 60), veri-viz kategorik sabit sıra + ilişkiye-göre palet + içgörü-başlığı, ikon-boyut eşleme, piktogram disiplini. **G-CARBON-GRID kapısının normatif kaynağı.** Kaynak: araştırma §10.2 (carbondesignsystem.com URL'leri).

### 4.3 `references/gamified-flows.md`
- **4 akış şablonu:** A "Keşif Döngüsü" (hook→teach→interaction→micro-win), B "Sefer" (mission + avatar + SVG mini-harita + N istasyon + kamp molası + checkpoint + sağlıklı-kapanış), C "Antrenman" (warm-up + uyarlanır item merdiveni + gain-only streak + öz-rekabet), D "Birlikte Odak" (opsiyonel co-play sarmalayıcı, sıra-tabanlı).
- **Mekanikler:** merak-boşluğu (segment içinde kapanır), hedef-gradyanı + bahşedilmiş ilerleme, görünmez taban-korumalı uyarlanır zorluk, kaygısız tempo diski.
- **Atıflı YAPMA listesi:** cross-session streak, liderlik tablosu, değişken-oran/loot-box, geri-sayım/sert-süre, aşırı-juicing, mastery'den-kopuk ödül, hyperfocus-sömürüsü, açık merak-boşluğu. **G-FLOW kapısının normatif kaynağı.** Kaynak: araştırma §10.3 (RCT/peer-review URL'leri).

---

## 5. Motor + şema yükseltmesi

Tüm yeni segment tipleri ve alanlar **opsiyoneldir**; motor render-dispatch'ine yeni handler eklenir, mevcut handler'lar korunur.

### 5.1 Küme A — Oyunlaştırma omurgası
| Ekleme | Tür | Motor değişikliği | Şema |
|---|---|---|---|
| Merak-boşluğu kancası | Yeni `hook` segment | `renderHook(stage,s)` — merak kartı + opsiyonel notsuz `predict`; **segment içinde kapanır** | `{type:"hook", id, question, predict?:{options[]}, resolvesIn:"<teachId>"}` |
| Hedef-gradyanı rayı | Mevcut `renderStepper` genişletme | milestone düğümleri + "son iki durak" yakın-hedef etiketi; `objectives` ekranı istasyon-1 (bahşedilmiş ilerleme) | `meta.milestones?` (yoksa mevcut davranış) |
| Gain-only streak | Mevcut `renderStreak` teyit/genişletme | yanlışta **tutar** (nötr "korundu"), asla boşalmaz/kayıp-dili yok | (mevcut streak; loss-dili kaldırılır) |
| Tempo diski | Yeni opsiyonel `pacingDisk` | SVG tükenen disk, **sayısız, kesintisiz, hard-stop yok**, varsayılan KAPALI | `learner.pacingDisk?:false` |
| Sefer mini-harita | Yeni `meta.quest` | SVG istasyon-haritası, tamamlanınca düğüm yanar | `meta.quest?:{stations[]}` |

### 5.2 Küme B — Derin öğretim
| Ekleme | Tür | Motor | Şema |
|---|---|---|---|
| Soluk-çözümlü örnek | Yeni `worked` segment | `renderWorked` — tam çözüm → adımlar `fadeFrom`'dan itibaren boşalır, öğrenci tamamlar | `{type:"worked", steps[], fadeFrom:int}` |
| Öz-açıklama | Yeni `selfExplain` segment | `renderSelfExplain` — istem + model açıklama reveal; **notsuz, düşük-baskı** | `{type:"selfExplain", prompt, modelExplanation}` |
| Uyarlanır zorluk | `mcq`/`fillblank` genişletme | opsiyonel `tier`; yuvarlanan-pencere sonraki tier'ı seçer (2 yanlış→ipucu-önce; 2 doğru→opsiyonel "meydan okuma"); **taban hep kolay, asla etiketleme** | soru şemasına `tier?:1|2|3` |

### 5.3 Küme C — Etkileşimli manipülatifler
| Ekleme | Tür | Motor | Şema |
|---|---|---|---|
| Parametrik simülasyon | Yeni `sim` segment | `renderSim` — 1–2 slider → canlı SVG yeniden çizim; **reduced-motion + klavye-adımlı slider** | `{type:"sim", simType:"<preset>", params[], labels}` — **preset kütüphanesi** (§5.3.1); MODULE_DATA yalnız veri taşır, render kodu taşımaz |
| Kavram-haritası kurucu | Yeni `conceptMap` segment | `renderConceptMap` — düğüm sürükle-bağla; **klavye fallback ZORUNLU** (kaynak-seç→hedef-seç); hedef yapıya karşı doğrula | `{type:"conceptMap", nodes[], targetEdges[]}` |
| Etkileşimli geometri/say-doğrusu | Mevcut `renderNumberline`/geometri genişletme | opsiyonel sürüklenebilir nokta + klavye-adım + canlı ölçüm | `{interactive?:true}` |

**§5.3.1 `sim` preset kütüphanesi (kod-güvenli tasarım kararı).** `MODULE_DATA` veri taşır, kod taşımaz (şema değişmezi: "motor olayları bağlar"). Bu yüzden `sim` keyfi render fonksiyonu **taşımaz**; motor sabit bir **preset kütüphanesi** gönderir ve `simType` ile seçilir, `params[]` ile yapılandırılır. Başlangıç presetleri (math/fen'i kapsayan küçük küme): `pendulum`, `projectile`, `wave`, `numberScale` (sayı-doğrusu/ölçek), `functionPlot` (parametrik y=f(x)). Yeni preset = **motor genişletmesi** (yeni `renderSim` dalı + G-SVG erişilebilirlik), MODULE_DATA yeteneği değil. Bu, self-contained + no-arbitrary-code değişmezini korur. `conceptMap` de aynı ilkeyle veri-güdümlüdür (`nodes`/`targetEdges`), motor kurma/doğrulama mantığını sağlar.

### 5.4 Küme D — Erişilebilirlik + tekrar
| Ekleme | Motor | Degrade |
|---|---|---|
| Sesli okuma (TTS) | teach/soru metnine "Sesli dinle" (`SpeechSynthesis`, `tr-TR` **localService** voice filtresi) | `tr-TR` yerel ses yoksa buton gizlenir; G-AUDIO zaten TTS-farkında |
| Çapraz-oturum aralıklı tekrar | `flashcards` → Leitner/kutu durumu `localStorage` (modül başına anahtar) | `localStorage` yok/bloklu → in-session tekrara degrade (IndexedDB kullanılmaz — `file://`'da bloklu) |
| İleri notasyon | `mathExpr` yetersizse inline `<math>` (MathML) | MathML render kalitesi tarayıcıya bağlı; `mathExpr` varsayılan kalır |

---

## 6. İki yeni validator kapısı → 13 kapı

Mevcut 11 kapı **değişmez**. Yeni segmentler için G-INTERACT/G-A11Y/G-SVG denetimleri genişletilir (yeni tipler tanınır).

### 6.1 G-FLOW (koşullu — yeni gamification alanları varsa)
- `hook` segmenti `resolvesIn` ile bir `teach`/segmente bağlı ve **aynı akışta kapanıyor** (açık merak-boşluğu = FAIL).
- Streak dili gain-only (loss/ceza/"kaybettin" dili = FAIL — G-WELLBEING'i tamamlar).
- `pacingDisk` sayısız + kesintisiz (geri-sayım/hard-stop = FAIL).
- Uyarlanır zorluk kullanıcıyı etiketlemiyor ("zorlanıyorsun" vb. = FAIL).
- İlgili alan yoksa → kapı **atlanır** (geriye uyum).

### 6.2 G-CARBON-GRID (WARN→FAIL — carbon-excellence makine-denetlenebilir alt-kümesi)
- 2x grid konteyneri mevcut (ad-hoc %-genişlik uyarısı).
- Media/figür/tile kutuları Carbon en-boy oranı kullanıyor.
- Statik kartlarda drop-shadow yok (layer-elevation); gölge yalnız floating (tooltip/menu/modal).
- Koreografi toplamı <500ms; tek geçiş 100–300ms.
- Bir bileşen iki tip-setini (expressive+productive) karıştırmıyor.
- Sapma = WARN; ağır ihlal (statik kart gölgesi, edge-to-edge gövde metni) = FAIL.

Runner çıktısı 13 kapı; `run-manifest-schema.json` `quality_gates` blokuna `G-FLOW` + `G-CARBON-GRID` eklenir.

---

## 7. Agent: `agents/module-auditor.md`

- **Rol:** üretilmiş modülü (veya modül spec'ini) **izole bağlamda** denetler → öncelikli düzeltme listesi.
- **Denetim eksenleri:** (1) `validate_module.py` 13-kapı; (2) `carbon-excellence.md` 15-madde checklist; (3) `gamified-flows.md` akış-şablonu uyumu (A/B/C/D) + atıflı YAPMA ihlalleri; (4) wellbeing/no-punitive + kaynak-sadakati (provenans).
- **Neden agent:** büyük modül HTML'i (100KB+) ana bağlamı taşırmadan tüketilir (rxpraxis/evidentia sub-agent izolasyon deseni). Ana bağlama yalnız ≤1-sayfa öncelikli-fix listesi döner.
- **Araçlar:** Read, Bash (validate_module.py çalıştırma), Grep, Glob. `${CLAUDE_PLUGIN_ROOT}` yolları.
- **Frontmatter:** `description` "when to use" örnekleriyle (plugin-dev agent-development deseni); model/tools alanları sibling agent'larla uyumlu.

---

## 8. Hook'lar: `hooks/hooks.json` (+ 2 script)

Tüm script'ler `${CLAUDE_PLUGIN_ROOT}/hooks/` altında; portable.

### 8.1 SessionStart — connector preflight
- `maarif-mufredat` canlılığı (`server_info`/`list_subjects`) + `get_figure`/Tier-2 mevcudiyeti → kısa durum notu.
- **Fail-open, deterministik:** connector yoksa üretim bloke olmaz; not bilgilendirici (evidentia deseni).

### 8.2 PostToolUse: Write|Edit — otomatik modül doğrulama
- Yazılan dosya `*.html` **ve** `MODULE_DATA` imzası taşıyorsa → `validate_module.py <dosya>` çalıştır, 13-kapı özetini (PASS/FAIL) yüzeyle.
- **Gate:** dosya path/imza eşleşmezse → sessiz no-op (herhangi bir HTML'de çalışmaz).
- Hook çıktısı kullanıcı geri-bildirimi olarak gösterilir (bloke etmez; WARN/FAIL bilgilendirir).

---

## 9. Geriye uyumluluk + doğrulama (kabul kriterleri)

**Geriye uyumluluk:**
- Tüm yeni segment tipleri/alanlar **opsiyonel**; yeni kapılar **koşullu**. Mevcut MODULE_DATA modülleri değişmeden çalışır. Major-bump (3.0.0) *marka + motor genişlemesi* içindir, kırılım için değil.

**Kabul kriterleri (hepsi geçmeli):**
- [ ] **E1.** Plugin `edupedia` olarak keşfedilir; `edupedia:carbon-edupedia` + `edupedia:start` skill'leri; 4 komut `/edupedia:*`. plugin-validator PASS.
- [ ] **E2.** `git mv` ile dizin taşındı; hiçbir kırık iç-referans yok (grep temiz); marketplace.json `edupedia` kaydı sibling'lerle biçim-uyumlu.
- [ ] **E3.** 3 yeni reference dosyası mevcut + `skill-manifest.yaml` `read_when` ile indeksli + SKILL.md wire.
- [ ] **E4.** Her yeni segment tipi (`hook`, `worked`, `selfExplain`, `sim`, `conceptMap`) için template'e **canlı örnek** eklendi; `node --check` geçer; motor render eder.
- [ ] **E5.** `validate_module.py` 13 kapı döndürür; mevcut template üstünde 13/13 (yeni koşullu kapılar skip veya PASS).
- [ ] **E6.** Yeni gamification örneği olan bir modül G-FLOW PASS; Carbon-grid örneği G-CARBON-GRID PASS.
- [ ] **E7.** `module-auditor` agent'ı keşfedilir; bir örnek modülde 13-kapı + checklist denetimi döndürür.
- [ ] **E8.** `hooks.json` geçerli; SessionStart preflight + PostToolUse validate script'leri kuru-çalıştırmada beklendiği gibi (modül→rapor, modül-olmayan→no-op).
- [ ] **E9.** TTS/spaced-rep/MathML degrade yolları: `tr-TR` ses yok / `localStorage` bloklu / MathML zayıf senaryolarında modül kırılmaz.
- [ ] **E10.** CHANGELOG 3.0.0 girişi; SKILL.md + manifest sürüm 3.0.0; geriye-uyum notu.

**Doğrulama yöntemi:** `validate_module.py` template üstünde; `node --check` her yeni segment örneği için; plugin-validator; hook script kuru-çalıştırma; yeni segment tipleri için manuel render smoke (mümkünse headless).

---

## 10. Araştırma bulguları (kaynak-atıflı özet)

### 10.1 İçerik zenginliği
En yüksek değer/düşük sürtünme: çapraz-oturum aralıklı tekrar (localStorage Leitner), TTS (SpeechSynthesis, sıfır yük), soluk-çözümlü örnek (math g=0.48, fading en güçlü alt-özellik — Barbieri 2023), öz-açıklama, parametrik SVG simülasyon (manipülatif d=0.83 — iJOE PhET meta). Wikidata **CC0** (wikidata.org/wiki/Wikidata:Licensing), native MathML (sıfır yük). Entegre edilemez: PhET (phet.colorado.edu/en/licensing/html — kaynak OSS değil), GeoGebra/Desmos/Khan (NC/SA/runtime), EBA/MEB (FSEK), Açık Ders (CC BY-NC-ND). Dyslexia-fontu miti: OpenDyslexic kanıtlı fayda YOK (PMC5629233) → ispatlı kaldıraçlar (satır-aralığı, ölçü, kullanıcı-seçimi).

### 10.2 Carbon estetik
Boşluk "token değil kompozisyon grameri": 2x grid + en-boy oranı (carbondesignsystem.com/elements/2x-grid), layer-elevation (gölge yalnız floating — /elements/color/usage), koreografi grameri + 20ms/<500ms (/elements/motion/choreography), expressive akışkan başlık/productive gövde (/elements/typography/type-sets), veri-viz sabit kategorik sıra + ilişkiye-göre palet + içgörü-başlığı (/data-visualization/color-palettes, /chart-anatomy). → 15-madde checklist.

### 10.3 ADHD oyunlaştırma
Merak-boşluğu (Loewenstein 1994; Kao CHI 2024 — curiosity en güçlü yol; **segment içinde kapanmalı**, açık boşluk→frustrasyon), hedef-gradyanı + bahşedilmiş ilerleme (Kivetz 2006), Sefer/level-progression (Dai 2025 RCT d≈0.92–1.25, 8-hafta kalıcı), görünmez uyarlanır zorluk (Dai 2025; Zohaib 2018 caveat), kaygısız tempo diski (Hallez & Vallier 2025 — kaygı↓+dikkatsizlik↓, performans değişmez). YAPMA: cross-session streak (loss-aversion→kaygı), liderlik tablosu (Hanus & Fox 2015), değişken-oran/loot-box, geri-sayım, aşırı-juicing, overjustification (Deci 1999), hyperfocus-sömürüsü. Hepsi mevcut G-WELLBEING/fixed-reward değişmezlerine **eklenir**, gevşetmez.

---

## 11. Uygulama sırası (writing-plans için ham girdi)

1. **Rename** (git mv + manifest/marketplace/prose + iç-referans onarımı) — izole, erken; testi kolay.
2. **3 reference dosyası** (araştırma §10 → normatif metin) — motor-bağımsız.
3. **Motor + şema** (küme A→B→D→C sırası; A mevcut altyapıyı genişletir en düşük risk; C en yüksek risk en son) — her segment tipi + canlı örnek + node --check.
4. **Validator** G-FLOW + G-CARBON-GRID — reference dosyaları normatif kaynak.
5. **Agent** module-auditor.
6. **Hook'lar** hooks.json + 2 script.
7. **Sürüm/CHANGELOG/manifest** 3.0.0 + geriye-uyum notu.
8. **Doğrulama** E1–E10.
