# edupedia — Çoklu Sınav Sorusu (EXAM genişlemesi) · Tasarım

- **Tarih:** 2026-08-16
- **Durum:** Uygulandı (2026-08-16)
- **Kapsam:** `plugins/edupedia` — mevcut EXAM modunun çoklu-soru hali
- **Önceki tasarım:** `docs/superpowers/specs/2026-07-31-edupedia-sinav-asistani-design.md` (tek soru; K1–K4 yürürlükte)
- **Motor durumu:** `assets/module-template.html` **değişmez** (`exam` / `exams` / `topics` motor tarafından çizilmez; provenans + G-EXAM)

---

## 1. Problem

`/edupedia:soru` bugün **tek** soru kabul eder. Fotoğraf veya yapıştırmada birden fazla
soru varsa hangisini istediğini sorar (`exam-solving.md` §7.2). Öğrenci bir yazılı /
deneme sayfası getirdiğinde bu sürtünme üretimi böler; konular ve yöntem aynı oturumda
öğretilmez.

İstenen: yapıştırılan veya fotoğrafı çekilen **bir veya birden fazla** soruyu analiz
eden, ilgili konuları kısaca anlatan, her soruyu demonstratif çözen **tek HTML modül**.

Tek-soru pedagojisi (kavram zinciri + `worked`/`fadeFrom` + telif/paylaşmama) korunur.

---

## 2. Kararlar

Önceki K1–K4 aynen geçerli. Ekler:

| # | Karar | Gerekçe |
|---|---|---|
| K5 | Teslim = **tek HTML** (konu farklı olsa bile) | Kullanıcı onayı: ortak/ardışık konu anlatımı + her sorunun çözümü aynı dosyada |
| K6 | Konu zinciri **soru başına değil konu başına** | Aynı konudaki sorular anlatımı tekrarlamaz; “kısaca anlat” ile uyumlu |
| K7 | Yumuşak tavan **~4 soru** | DEHB kısa oturum; 5+ için uyarı, üretim yine de aynı HTML’de (FAIL değil) |
| K8 | Yeni komut yok | `/edupedia:soru` genişler; `exams.length === 1` eski tek-soru davranışı |

G-FLOW soru sayısını **sınırlamaz** (o kapı gamification değişmezleridir: merak-boşluğu,
gain-only streak, kaygısız disk). Tempo: `module-architecture.md` ≥6 segmentte
`brainbreak` + konu sonu `checkpoint`. Önceki taslakta “G-FLOW tavanı” denmişti — **yanlış;
bu spec onu düzeltir.**

---

## 3. Yerleşim

| Dosya | Değişiklik |
|---|---|
| `commands/soru.md` | Çoklu girdi; “hangisini istiyorsun?” kalkar; konu kümeleme + yumuşak tavan uyarısı |
| `skills/carbon-edupedia/references/exam-solving.md` | `topics` + `exams[]` şema; sıkıştırılmış çoklu kurgu; §7.2 tek-soru sınırı kalkar |
| `skills/carbon-edupedia/SKILL.md` | EXAM satırı: bir veya birden fazla soru |
| `skills/carbon-edupedia/skill-manifest.yaml` | G-EXAM tanımı çoklu; sürüm **3.9.0 → 3.10.0** |
| `skills/carbon-edupedia/scripts/validate_module.py` | G-EXAM: `exams[]` dolaşımı; öğe başına `workedId`+`fadeFrom`; `topicId`; n>4 WARN |
| `skills/carbon-edupedia/tests/test_gates.py` | Eski `exam:{}` PASS; çoklu PASS/FAIL/WARN |
| `skills/start/SKILL.md`, `README.md`, plugin.json | Komut açıklaması |
| CureoHub `services/edupedia_site/app/gates/` | Validator lockstep (site emekli; sapma yasağı durur) |
| `assets/module-template.html` | **DEĞİŞMEZ** |

Plugin sürümü **0.8.0 → 0.9.0**.

---

## 4. Girdi ve akış

```
/edupedia:soru  <fotoğraf(lar) ve/veya yapıştırılmış metin>
 │
 0  GİRDİ            bir veya birden fazla soru; belirsiz rakam/şık → SOR (D5), tahmin yok
 │
 1  TRANSKRİPSİYON   her soru birebir metin; şekil → yazar-SVG; fotoğraf gömülmez (K4)
 │
 2  KÜMELE           soruları konuya göre grupla (farklı konular → ardışık kümeler, hâlâ tek HTML)
 │
 3  KAPI             ders + sınıf kesinleşmeden üretim yok (curriculum-integration.md §3 Adım 0)
 │
 4  TAVAN            n > 4 → kullanıcıya “oturum uzayacak” uyarısı; üretim durmaz
 │
 5  KONU ZİNCİRİ     küme başına 2–4 halka; search_learning_outcomes ile bağla (D2); kitap (D3)
 │
 6  ÇÖZ              her soru kendi demonstratif çözümü (D1/D4 soru bazında)
 │
 7  KUR              topics[] + exams[] (tek soruda geriye dönük exam:{} da geçerli)
 │
 8  TESLİM           validate_module.py (G-EXAM dahil) → yerel HTML + .manifest.json
                     paylaşım teklifi yok (K2)
```

Tek soru: bugünkü 11 segmentlik kurgu (`exam-solving.md` §4) **aynen**.

---

## 5. Veri modeli

Motor bu blokları okumaz. G-EXAM regex ile biçim ölçer.

### 5.1 Geriye dönük (tek soru)

Mevcut `exam: { stem, options?, figure?, source?, integrity, integrityNote?,
transcriptionCheck, distractorAnalysis?, chain[] }` şeması **geçerli kalır**.
`workedId` yoksa bugünkü kural: HTML’de `fadeFrom < adım` olan bir `worked` yeter.

### 5.2 Çoklu

```js
topics: [
  { id: "t-kesir", title: "Kesirle çarpma",
    chain: [
      { concept: "birim fiyat", outcomeCode: "MAT.6.1.4.1", mappedTo: ["t1"] }
    ] }
],
exams: [
  { id: "q1", topicId: "t-kesir",
    stem: "…",
    options: ["…"],          // opsiyonel
    figure: { kind: "svg", ref: "<svg …>" },
    source: "öğrenci fotoğrafı",
    integrity: "sound",      // sound | flawed | out_of_frame
    integrityNote: "",
    transcriptionCheck: "tc-q1",
    distractorAnalysis: "d-q1",
    workedId: "w-q1" }       // ZORUNLU (çokluda); bu id'li worked fadeFrom taşımalı
]
```

- Her `exams[]` öğesi bir `topicId` çözer.
- Zincir **konuda** yaşar; soru öğesinde `chain` yok.
- Doğru cevap blokta tutulmaz (`worked.steps[].answer` + varsa çeldirici `mcq`).
- `mode: "EXAM"` kalır.

Tek soru yazarı isterse `exams: [{…}]` + `topics: [{…}]` de yazabilir; G-EXAM her iki
şekli kabul eder. `exams` yalnız `length ≥ 1` ise kullanılır; boş `exams: []` yok
hükmündedir ve varsa `exam:{}` legacy yolu işler.

---

## 6. Segment kurgusu (çoklu, sıkıştırılmış)

```
  hook            "Bunlar hangi bilgiyi istiyor?"          // bir kez
  ── konu kümeleri (sırayla) ──
    teach+etkileşim   zincir halkaları (2–4; chain.mappedTo)
    ── kümenin her sorusu ──
      teach           transkribe kök + şıklar + yazar-SVG
      selfExplain     "Böyle okudum"   ← transcriptionCheck
      worked          bu soru, fadeFrom zorunlu
      selfExplain     "Neden bu adım?"
      mcq             çeldirici (yalnız şıklıysa)
    checkpoint        konu sonu
    brainbreak        ≥6 segment kuralı; kümeler arası
  mcq             transfer — konu başına EN FAZLA bir, soru başına değil
  checkpoint      kapanış; wellbeing: sınav/ödev anı aracı değil
```

Transfer’in soru başına tekrarı yasak: uzunluk + ödev-makinesi riski.

---

## 7. G-EXAM

Tetik: `mode:"EXAM"` **veya** `exam:{` **veya** `exams:[`.

| Durum | Sonuç |
|---|---|
| Eski `exam:{}` | Bugünkü `_exam_eval` (stem, integrity, transcriptionCheck, tek fadeFrom-worked, chain) |
| `exams[]` | Her öğe: dolu stem; geçerli integrity (+ note); var olan transcriptionCheck; **kendi** `workedId` üzerinde fadeFrom < adım; `topicId` topics[]’te; konu chain dolu ve mappedTo gerçek id |
| `exams.length > 4` | **WARN** (yumuşak tavan) |
| Öğede source yok | WARN |
| Şık var, distractorAnalysis yok | WARN (öğe bazında) |
| Bir öğe D1/D4 | O öğe `flawed` / `out_of_frame`; diğer öğeler FAIL etmez |
| mode EXAM ama ne exam ne exams | FAIL |

**Hâlâ ölçemez:** transkripsiyon sadakati, çözüm doğruluğu, zincir eksiksizliği,
`outcomeCode` gerçekliği (salt-metin / MCP yok).

**Kırılma düzeltmesi:** bugün `_exam_worked_ok(html)` modüldeki **herhangi** bir
`worked` ile geçer. Çokluda bu yasak — öğrenci bir sorunun cevabını açık görüp
diğerinde fadeFrom varmış gibi sayılmamalı.

---

## 8. Degrade (soru bazında)

D1–D5 (`exam-solving.md` §5) **öğenin** `integrity`’sine yazılır. Bozuk bir soru
modülü iptal etmez: o slotta tanı segmenti + uydurma cevap yok; diğer sorular devam.

D5 (okunmayan fotoğraf) üretimden önce sorulur; tahmin yok.

MEB dışı (IB/Cambridge) çerçeve kurulamaz; dürüstçe söylenir — tüm girdi MEB dışıysa
üretim durur; karışıksa MEB olanlar üretilir, diğerleri `out_of_frame` notu.

---

## 9. Test

| Vaka | Beklenen |
|---|---|
| Mevcut tek `exam:{}` fixture | G-EXAM PASS (regresyon) |
| İki konu, üç `exams[]`, her birinde fadeFrom worked | PASS |
| Üç sorudan birinde `workedId` fadeFrom’suz | FAIL (yalnız o öğe mesajı) |
| Kırık `topicId` | FAIL |
| Beş `exams[]`, yapı sağlam | WARN (`> 4`), FAIL değil |
| Boş `exams: []` + `exam:{}` var | Legacy PASS (boş dizi yok hükmünde) |
| Boş `exams: []` + `exam:{}` yok + mode EXAM | FAIL |

---

## 10. Bilinçli olarak kapsam dışı

- Yeni slash komut (`/edupedia:sorular`)
- Motor/`MODULE_DATA`’da `exam` render’ı
- Public katalog / paylaşım teklifi
- Çoklu-soru hata örüntüsü istatistiği (eski §7.2’nin analitik kısmı hâlâ yok)
- Sert 4 tavan (ikinci HTML’e bölme)
- Fotoğrafı HTML’e gömmek

---

## 11. Başarı ölçütü

1. Yapıştırılmış iki soru + bir fotoğraf → tek HTML, konu anlatımı tekrar etmez.
2. Her sorunun `worked`’inde son adım öğrenciye bırakılır; G-EXAM öğe bazında bunu zorlar.
3. Eski tek-soru modülleri ve testleri yeşil kalır.
4. 5 soruluk girdi uyarır, üretir, FAIL etmez.
