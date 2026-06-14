# Migration Guide: brand-maker v1.2.x → v2.0.0

> **Hedef okur**: `brand-maker` v1.2'yi aktif kullanan herkes. Bu rehber, v2.0'a geçişin işlevsel etkisini ve geçiş prosedürünü açıklar.

---

## 1. Özet Değerlendirme

| Boyut | v1.2 | v2.0 |
|---|---|---|
| **Çağrı API'si** | Natural-language brief | Natural-language brief (değişmedi) |
| **Zorunlu adım sayısı** | 4 | 5 |
| **Naming kategorisi** | 4 (A/B/C/D) | 5 (A/B/C/D/E) |
| **SMILE kriteri** | 5 | 5 (+ opsiyonel M = 6) |
| **SCRATCH dilution** | 1-layer (Levenshtein) | 3-layer (L-A + L-B + L-C) |
| **Validation eksen sayısı** | - | 6 (post-digital) |
| **Pharma modülü** | Yok | Var (`inn_stem_collision.py` + derin referans) |
| **Kanonik kaynak** | 7 (1981-2021) | 13 (1981-2026) |
| **Referans dosyası** | 10 | 18 |
| **Python scripti** | 4 | 10 |
| **Data asseti** | 0 | 3 |

### Backward Compatibility Temeli

**v1.2 kullanıcıları için en önemli haber**: Dış kullanıcı arayüzü (natural-language brief) tamamen aynı kaldı. Bir v1.2 brief'iniz varsa, v2.0'da aynı brief ile **daha zengin çıktı** alırsınız; yeniden brief yazmanıza gerek yok.

Sessiz değişim: Raporun iç yapısı zenginleşti. Section 5 (Post-Digital Readiness Scorecard) her yeni raporda görünecek. Section 4A yalnızca pharma brief'lerinde görünür.

---

## 2. Dosya Sistemi Geçişi

### 2.1 Mevcut v1.2 Kurulumu Yedekle

```bash
# Önce v1.2'yi yedekle
cp -r /mnt/skills/user/brand-maker /mnt/skills/user/brand-maker-v1.2-backup

# v2.0 zip'ini çıkar
unzip brand-maker-v2.0.zip -d /mnt/skills/user/

# Dizin yapısı:
# /mnt/skills/user/brand-maker/
#   SKILL.md                    (v2.0 rewrite)
#   skill-manifest.yaml         (YENİ)
#   CHANGELOG.md                (YENİ)
#   MIGRATION_v1.2_to_v2.0.md   (bu dosya)
#   references/                 (18 dosya — 6 preserved, 4 updated, 8 new)
#   scripts/                    (10 dosya — 4 preserved, 6 new)
#   data/                       (3 dosya — tümü YENİ)
```

### 2.2 Dosya-by-Dosya Migration Tablosu

| Dosya | v1.2 → v2.0 Statüsü | Not |
|---|---|---|
| `SKILL.md` | **Updated** (major rewrite) | 5-adım metodoloji, 15 routing, 2026 canon |
| `references/positioning-foundation.md` | **Preserved** | Değişmedi |
| `references/smile-scratch-filter.md` | **Updated** | SMILE+M + 3-layer dilution |
| `references/output-template.md` | **Updated** | Section 5, 4A eklendi |
| `references/creation-techniques.md` | **Updated** | AI-fingerprint bölümü append edildi |
| `references/phonetic-laws.md` | **Preserved** | Değişmedi |
| `references/disaster-check.md` | **Preserved** | Değişmedi |
| `references/domain-trademark-strategy.md` | **Preserved** | Değişmedi |
| `references/godaddy-mcp-integration.md` | **Preserved** | Değişmedi |
| `references/naming-categories.md` | **Updated** | 5. kategori E eklendi |
| `references/exemplar-catalog.md` | **Preserved** (minör update) | 2022–26 exemplar append |
| `references/geo-llm-readiness.md` | **YENİ** | |
| `references/voice-first-naming.md` | **YENİ** | |
| `references/pharma-naming-constraints.md` | **YENİ** | Mahir profili için detay |
| `references/motion-kinetic-readiness.md` | **YENİ** | |
| `references/ai-fingerprint-avoidance.md` | **YENİ** | |
| `references/purpose-axis-matrix.md` | **YENİ** | |
| `references/modern-canon-2022-2026.md` | **YENİ** | |
| `references/category-creator-protocol.md` | **YENİ** | |
| `scripts/phonetic_analyzer.py` | **Preserved** | |
| `scripts/disaster_checker.py` | **Preserved** | |
| `scripts/turkish_semantic_check.py` | **Preserved** | |
| `scripts/domain_recon.py` | **Preserved** | |
| `scripts/llm_namespace_probe.py` | **YENİ** | |
| `scripts/morpheme_saturation_check.py` | **YENİ** | |
| `scripts/asr_simulation.py` | **YENİ** | |
| `scripts/entity_disambiguation.py` | **YENİ** | |
| `scripts/inn_stem_collision.py` | **YENİ** | |
| `scripts/famous_mark_dilution.py` | **YENİ** | |
| `data/usan_stems.json` | **YENİ** | |
| `data/yc_ph_morpheme_corpus.json` | **YENİ** | |
| `data/famous_marks_2026.json` | **YENİ** | |

---

## 3. Davranış Değişiklikleri

### 3.1 Yeni Zorunlu Adım — Step 3.5

v1.2'de 4-adımlı metodoloji (3.1 Deşifre → 3.2 4-Kategori → 3.3 Dilbilimsel Lab → 3.4 Ajans Sunumu) idi.

v2.0'da bu sıra yeniden düzenlendi:
- 3.1 Stratejik Deşifre (aynı)
- 3.2 **5-Kategori** Bazlı Brainstorm (E eklendi)
- 3.3 Dilbilimsel Lab — SMILE+M ve 3-layer SCRATCH
- 3.4 **Live Domain Verification** (v1.2'de adım 3.4 idi — önceden ajans sunumundu)
- 3.5 **Post-Digital Validation** (YENİ — 6-eksen)
- 3.6 Ajans Sunumu (v1.2'deki 3.4)

**Kullanıcı için anlam**: Her raporda artık 6-eksenli scorecard var. Bu, ek bir tablo ve 200-400 kelimelik rationale eklenmesi demek.

### 3.2 E Kategorisi — "Neumeier Boşluğu"

v1.2 naming-categories.md 4 kategori tanımlıyordu:
- A. Tanımlayıcı & Metaforik
- B. Sentez & Türetilmiş (Portmanteau)
- C. Soyut & Fonetik (Coined)
- D. Çağrışımsal & Mitolojik

v2.0'da eklendi:
- E. Sezgisel / Kontraryen

**Kullanıcı için anlam**: Her beyin fırtınası havuzunda artık 5 kategoriden aday görünür. "Cesur", "disruptive", "contrarian" sinyali olan brief'lerde E kategorisi finalist ağırlığı artar.

### 3.3 SMILE → SMILE+M

v1.2'de 5 kriter (Suggestive, Meaningful, Imagery, Legs, Emotional). v2.0'da opsiyonel 6. kriter:
- +M (Morphable) — kinetik/motion-first deformation toleransı

**Kullanıcı için anlam**:
- Motion-first brief'lerde 6/6 skor hedeflenir
- Diğer brief'lerde 5/5 yeterli, +M bilgi amaçlı raporlanır
- Geri uyumlu: v1.2 raporlarında 5/5 alınan isimler hâlâ geçer

### 3.4 SCRATCH C Kriteri — 3-Layer Dilution

v1.2'de SCRATCH'in C (Copycat) kriteri tek-katmanlı (Levenshtein-2) idi.

v2.0'da 3-katmanlı:
- **Layer A** — Levenshtein-2 (v1.2 ile aynı)
- **Layer B** — Phonetic-3 (Metaphone + Soundex homophonic)
- **Layer C** — Conceptual-aura (Pixar-style exploitation)

**Kullanıcı için anlam**: v1.2'de "clean" geçen bazı isimler v2.0'da Layer B veya C'de flag alabilir. Bu flag'ler rapora yazılır ama finalist'i otomatik elemez; raporlanır.

### 3.5 Pharma Zorunlu Modül

v1.2'de pharma brief'ler genel naming framework'ü ile işleniyordu. v2.0'da **ayrı modül**:
- `pharma-naming-constraints.md` otomatik yüklenir
- `inn_stem_collision.py` + `entity_disambiguation.py --high-precision` çalışır
- Rapor Section 4A oluşturulur

**Kullanıcı için anlam**: Pharma brief'lerde artık rapor 3.500–5.000 kelime range'de. Regulatory pre-screen derinliği kullanıcının yüküne ek olarak skill tarafından otomatik.

---

## 4. Rapor Şablonu Geçişi

### 4.1 v1.2 Rapor Yapısı (6-bölüm)

1. Stratejik Deşifre
2. 4-Kategori Aday Havuzu
3. Dilbilimsel Lab
4. Domain & Trademark Stratejisi
5. Stratejik Tavsiye Matrisi
6. Sonraki Adımlar

### 4.2 v2.0 Rapor Yapısı (7-bölüm)

1. Stratejik Deşifre (1.6 eklenebilir: Purpose-axis)
2. **5-Kategori** Aday Havuzu (E eklendi)
3. Dilbilimsel Lab (SMILE+M, 3-layer dilution)
3A. (opsiyonel) Proposed Category Name (category-creator brief için)
4. Domain & Trademark Stratejisi
4A. (opsiyonel) Pharma-Specific Regulatory Screening
**5. Post-Digital Readiness Scorecard** ← YENİ ZORUNLU
6. Stratejik Tavsiye Matrisi (Post-Digital + Pharma-Reg sütunları eklendi)
7. Sonraki Adımlar + Yöntemsel Notlar (13 kaynak)

### 4.3 Stratejik Tavsiye Matrisi — Sütun Artımı

**v1.2**:
```
| Finalist | Kategori | SMILE | SCRATCH | Domain | Trademark | Genel Öncelik |
```

**v2.0**:
```
| Finalist | Kategori | SMILE+M | SCRATCH | Domain | Trademark | Post-Digital | Pharma-Reg | Genel Öncelik |
```

---

## 5. Çıktı Uzunluğu Beklentisi

| Brief Tipi | v1.2 hedef | v2.0 hedef |
|---|---|---|
| Küçük brief | 1,500–2,000 kelime | 2,000–2,500 kelime |
| Standart kurumsal | 2,000–3,000 | 2,500–3,500 |
| Born-global startup | 2,500–3,500 | 3,500–4,500 |
| **Pharma launch** | 2,500–3,500 | **3,500–5,000** |

Artış sebebi: Section 5 + (pharma'da) Section 4A eklenmesi.

---

## 6. Composability Değişikliği

v2.0 **SMP v1.0 uyumludur**. Bu:

- `smp-orchestrator` skill'i brand-maker'ı discover edebilir
- Otomatik pipeline önerileri alır: medsearch → brand-maker → brand-visual → carbon-html-report gibi
- Manifest içindeki `pipe_from` / `pipe_to` deklarasyonları **yanlışa dirençli**

**v1.2'de manuel çağrı**:
```
Kullanıcı: "medsearch'te semaglutide için literatür yap"
[medsearch çıktısı]
Kullanıcı: "brand-maker'da bunu kullanarak semaglutide sub-brand'i için isim öner"
```

**v2.0'da (pragmatik)**:
```
Kullanıcı: "semaglutide için sub-brand isim önerisi — medsearch + pharmaintel ile"
[Skill'ler SMP uyumlu olduğundan chain öneri otomatik]
```

---

## 7. Geri Dönüş Senaryoları

Eğer v2.0'da istemediğiniz bir davranış varsa:

### 7.1 "Section 5'i istemiyorum"
Brief'te açıkça belirtin: "Post-Digital validation atlasın, klasik raporu istiyorum." Skill bunu saygı gösterir ve Section 5'i boş bırakır.

### 7.2 "E kategorisi istemiyorum"
"Kontraryen kategori önerme, konservatif kalalım." Skill havuzda E kategorisi üretmez.

### 7.3 "SCRATCH 3-layer istemiyorum"
"Klasik Levenshtein-2 Copycat testi yeter." Skill Layer B ve C'yi atlar.

### 7.4 "v1.2 tam fallback"
Brief'e: "v1.2 moduyla çalış — 4-kategori, 5-kriter SMILE, 1-layer SCRATCH, 4-adım." Skill bu emri saygı göstererek eski davranışa döner.

---

## 8. Test Senaryoları

Migration doğrulaması için aşağıdaki test brief'leri v1.2 → v2.0 geçiş öncesi ve sonrası karşılaştırılabilir:

### 8.1 Standart SaaS Brief
```
"B2B AI agent platformu — Stripe + Vercel intersection. Developer-friendly, enterprise-ready. EMEA + US."
```

**Beklenti**: v2.0'da raporda Section 5 (LLM namespace probe + morpheme saturation + entity disambiguation + voice test + dilution) görünür.

### 8.2 Pharma Brief
```
"Roche Turkey için yeni HER2-low ADC ürün (trastuzumab deruxtecan sonrası NGS-positive). Hastane-odaklı, onkolog hedef."
```

**Beklenti**: v2.0'da Section 4A (USAN stem çakışması, LASA riski, TİTCK Türkçe filtre) görünür.

### 8.3 Consumer DTC Brief
```
"Yeni yiyecek takviyeli probiyotik içecek. Gen-Z hedef. Liquid Death + Olipop estetiği."
```

**Beklenti**: v2.0'da E kategorisi (kontraryen) finalist ağırlığı artar; voice-first namespace probe çıkar.

---

## 9. Desteklenen Süre

- **v1.2**: 2026-12-31 tarihine kadar paralel destek. Kritik bug-fix'ler için `1.2.x` patch serisi sürdürülür.
- **v2.0**: Ana geliştirme hattı. Yeni özellikler v2.x üzerine inşa edilir.

---

## 10. Sorular ve Destek

Migration sırasında karşılaşılan bir sorun varsa:
- SKILL.md "Versiyon ve Limitler" bölümüne bakın
- CHANGELOG.md v2.0.0 section'ındaki "Known Limitations"
- Brief'inizi "v1.2 moduyla çalış" kısıtıyla tekrar deneyin; fark tespiti için

Upgrade tamamlandı. Hayırlı olsun.
