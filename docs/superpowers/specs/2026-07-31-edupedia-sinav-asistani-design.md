# edupedia — Sınav Sorusu Asistanı (EXAM modu) · Tasarım

- **Tarih:** 2026-07-31
- **Durum:** Onaylandı (tasarım); uygulama planı bekliyor
- **Kapsam:** `plugins/edupedia` — yeni mod + komut + referans + kalite kapısı
- **Motor durumu:** `assets/module-template.html` **değişmez**

---

## 1. Problem

Öğrencinin önüne gelmiş bir sınav sorusu (fotoğraf veya kopyala-yapıştır) edupedia'nın
pedagojik ilkeleriyle çözülsün; çözülürken sorunun gerektirdiği kavramlar da öğretilsin.

Mevcut plugin **kazanımdan modül üretir** (`/edupedia:modul`, `/edupedia:mufredat`).
Girdi olarak *soru* alan bir yol yok. Ayrıca sınav sorusu üç yeni gerilim getiriyor:

1. **Çerçeve tersine döner.** Mevcut akışta çerçeveyi ders kitabı çizer ve üretimin
   sınırıdır. Sınav sorusu ise dışarıdan gelir (LGS denemesi, yayınevi föyü, okul yazılısı)
   ve çerçeveye *sonradan* bağlanmalıdır.
2. **Telif.** Modüller `edupedia.cureonics.com`'da public okunur. Telifli bir soru
   birebir gömülüp yayınlanırsa ihlal olur.
3. **Ödev-çözme riski.** Cevabı doğrudan veren bir asistan öğrenme aracı değil, kopya
   aracıdır. Bu, yapısal olarak engellenmelidir — iyi niyete bırakılamaz.

---

## 2. Kararlar

| # | Karar | Gerekçe |
|---|---|---|
| K1 | Çıktı = **etkileşimli tek-dosya HTML modül** (yeni bir çıktı türü değil) | Motor, 13 kapı, `worked`/`selfExplain` segmentleri ve yayın hattı olduğu gibi yeniden kullanılır |
| K2 | Soru modülde **içerikçe birebir** yer alır (aynı sayılar, aynı ifade, aynı şıklar — piksel değil, K4); modül **varsayılan olarak yayınlanmaz** | Öğrenci kendi sorusunu tanımalı; telif riski yayın teklifini kaldırarak kapatılır |
| K3 | Anlatım genişliği = **geriye doğru kavram zinciri** (kazanımın tamamı değil) | Soruyu çözmek için gereken halkalar öğretilir → ~10-12 dk, DEHB kısa-oturum ilkesiyle uyumlu; her segment soruya bağlı olduğu için "neden bunu öğreniyorum" hep açık |
| K4 | Soru **transkribe + yeniden inşa** edilir; fotoğraf gömülmez | Motorda raster taşıyıcı yok (§8); ayrıca yeniden inşa tema-duyarlı, ekran-okuyucu erişilebilir ve Tier-1 yazar-SVG doktriniyle tutarlı |

K4'ün bedeli transkripsiyon hatasıdır (yanlış okunan üs, karışan `6`/`b`). Karşılığı
modülün 2. segmentindeki **transkripsiyon doğrulama kapısı**dır (§5).

---

## 3. Yerleşim

| Dosya | Değişiklik |
|---|---|
| `commands/soru.md` | **YENİ** — `/edupedia:soru` giriş noktası |
| `skills/carbon-edupedia/references/exam-solving.md` | **YENİ** — soru anatomisi · geriye çözümleme · çeldirici pedagojisi · bozuk-soru protokolü · transkripsiyon disiplini |
| `skills/carbon-edupedia/SKILL.md` | 9. mod `EXAM` (§6 mod tablosu) + §5 referans tablosuna satır + §12'ye `G-EXAM` |
| `skills/carbon-edupedia/skill-manifest.yaml` | mod · referans · trigger · `G-EXAM` kapısı · sürüm |
| `skills/carbon-edupedia/scripts/validate_module.py` | **YENİ koşullu kapı `G-EXAM`** |
| `skills/carbon-edupedia/tests/test_gates.py` + `tests/fixtures/` | `G-EXAM` testleri (pass + her FAIL dalı için birer fixture) |
| `plugin.json` | komut 5→6, açıklama |
| `skills/start/SKILL.md` | Adım 4 komut tablosu + Adım 5 niyet yönlendirme |
| `assets/module-template.html` | **DEĞİŞMEZ** |
| `agents/module-auditor.md` | **DEĞİŞMEZ** (mevcut 4 eksen EXAM modülünde de geçerli) |

---

## 4. Yürütme akışı

```
/edupedia:soru <fotoğraf | yapıştırılmış metin>
 │
 0  GİRDİ           fotoğrafı oku / metni al
 │
 1  TRANSKRİPSİYON  soruyu birebir metne çevir; şekil/grafik → yazar-SVG olarak
 │                  yeniden çiz (svg-authoring.md kuralları: token renk, role="img",
 │                  2px stroke, gradyansız)
 │                  ⚠ silik rakam, kesik kenar, belirsiz üs → SOR, tahmin etme (D5)
 │
 2  KAPI            ders + sınıf kesinleşmeden üretim başlamaz.
 │                  Fotoğrafta yazmıyorsa AskUserQuestion ile SOR.
 │                  → curriculum-integration.md §3 Adım 0 kuralının aynısı;
 │                    burada TEKRARLANMAZ, oraya referans verilir.
 │
 3  TEŞHİS          soruyu GERİYE çözümle: "bunu çözmek için önce neyi bilmek
 │                  gerekiyor?" → kavram/beceri zinciri (2-4 halka tipik)
 │
 4  KAZANIM         zincirin her halkasını search_learning_outcomes ile kazanıma
 │                  BAĞLA — doğrula, uydurma. Bağlanamayan halka için D2.
 │
 5  ÇERÇEVE         list_textbooks → get_document_text → zincirin kitaptaki yeri.
 │                  Çözümün ve anlatımın dayanağı burasıdır.
 │                  Kitap yoksa D3.
 │
 6  ÇÖZ             kendi çözümünü üret; her adımın dayanağı kitap sayfası.
 │                  Soru bozuksa D1, çerçeve üstüyse D4.
 │
 7  KURGU           MODULE_DATA + exam bloğu (§5, §6)
 │
 8  TESLİM          validate_module.py (G-EXAM dahil) → /mnt/user-data/outputs/
                    + <ad>.manifest.json
                    ✗ /edupedia:yayinla TEKLİF EDİLMEZ (K2)
```

**Connector kullanımı:** mevcut üçlü değişmez. `maarif-mufredat` otorite (adım 4-5),
`egitim-kaynak` tamamlayıcı (D3'te `supported_by_source` dayanağı), `modul-yayin`
bu modda **kullanılmaz**.

---

## 5. `exam` veri bloğu (MODULE_DATA uzantısı)

`curriculum` bloğuyla aynı desende: motoru değiştirmez, izlenebilirlik taşır,
`G-EXAM` tarafından okunur.

```js
const MODULE_DATA = {
  meta: { mode: "EXAM", /* … */ },

  exam: {
    stem: "3/4 kg elma 24 TL ise 2/3 kg elma kaç TL'dir?",   // ZORUNLU — transkribe soru
    options: ["12 TL", "14 TL", "16 TL", "18 TL"],            // opsiyonel — şıklıysa
    figure: { kind: "svg", ref: "<svg …>" },                  // opsiyonel — yeniden çizilen şekil
    source: "öğrenci fotoğrafı — okul yazılısı",              // opsiyonel (yoksa WARN)
    integrity: "sound",                     // ZORUNLU: "sound" | "flawed" | "out_of_frame"
    integrityNote: "",                      // flawed/out_of_frame ise ZORUNLU açıklama
    transcriptionCheck: "tc1",              // ZORUNLU — doğrulama segmentinin id'si (selfExplain)
    distractorAnalysis: "d1",               // opsiyonel — çeldirici analizi segmentinin id'si
                                            //   (exam.options varsa yokluğu WARN)
    chain: [                                // ZORUNLU, boş olamaz — geriye çözümleme
      { concept: "birim fiyat",
        outcomeCode: "MAT.6.1.4.1",         // opsiyonel (D2'de düşer)
        mappedTo: ["t1", "q1"] },           // ZORUNLU — segments[]'te var olmalı
      { concept: "kesirle bölme",
        outcomeCode: "MAT.6.1.4.2",
        mappedTo: ["t2", "w1"] }
    ]
  },

  curriculum: { /* … */ },   // EXAM modunda OPSİYONEL (CURRICULUM modundan farkı — D2)
  verification: { /* … */ }, // ders+sınıf varsa mevcut kural; §7'deki tek istisna ile
  segments: [ /* §6 */ ]
};
```

**Doğru cevap `exam` bloğunda tutulmaz.** Cevap iki yerde yaşar: `worked` segmentinin
son adımındaki `answer` ve çeldirici analizi `mcq`'sünün `correctIndex`'i. Tekrar
tutulmaması bilinçlidir — tek kaynak.

> **Bilinen sızıntı (yeni değil):** `MODULE_DATA` HTML kaynağındadır; kaynağı açan bir
> öğrenci `answer`/`correctIndex` görebilir. Bu mevcut tüm `mcq` modülleri için de
> geçerli, bu tasarımın getirdiği bir gerileme değil. Çözülmeyecek.

---

## 6. Modül iç kurgusu

```
 1  teach        "Soruyu birlikte okuyalım"
                  → exam.stem + exam.options + exam.figure (yazar-SVG)
 2  selfExplain  "Soruyu böyle okudum. Bir yeri farklıysa aşağıya yaz."
                  ← TRANSKRİPSİYON KAPISI (exam.transcriptionCheck bunu gösterir)
                    modelExplanation: farklıysa düzeltilmiş soruyla tekrar sorma yönergesi
 3  hook         "Sence bunu çözmek için hangi bilgi gerekli?"   resolvesIn → 4
 4  teach + etkileşim   zincir halkası 1  (kitaptan; KB2.x becerisine eşlenmiş)
 5  teach + etkileşim   zincir halkası 2
 6  brainbreak   (≥6 segment ise — mevcut kural, module-architecture.md §3)
 7  worked       SORUNUN KENDİSİ, adım adım
                  ← fadeFrom ile SON ADIM(LAR) ÖĞRENCİYE BIRAKILIR
 8  selfExplain  "Neden bu adımda böyle yaptık?"  (notsuz, cezasız)
 9  mcq          ÇELDİRİCİ ANALİZİ — "B şıkkı neden cazip ama yanlış?"
10  mcq          TRANSFER — aynı zincirle 2 izomorfik soru
11  checkpoint
```

**2. adım neden `mcq` değil `selfExplain`:** `G-INTERACT` her `stem:` için bir
`correctIndex:` şart koşar. "Soruyu doğru mu okudum?" sorusunun doğru cevabı yoktur —
`mcq` yapılırsa ya kapı düşer ya da "Hayır, şurası farklı" diyen öğrenci *yanlış*
sayılır (G-WELLBEING ihlali). `selfExplain` notsuz ve cezasızdır, "Devam" koşulsuz
etkindir; öğrenci farkı yazabilir de yazmayabilir de. Doğru taşıyıcı budur.

**7. adım bu tasarımın kalbidir.** `worked` segmenti `fadeFrom` ile kapatılır; cevap
hiçbir zaman doğrudan verilmez, öğrenci son adımı kendisi tamamlar. Bu bir üslup tercihi
değil, `G-EXAM`'ın zorladığı bir yapıdır (§7) — ödev-çözme makinesi olmayı yapısal
olarak imkânsızlaştırır.

**9. adımın gerekçesi:** yeni nesil sorularda çeldirici genellikle *doğru ama ilgisiz*
bilgidir ve DEHB'li öğrenci için en zorlayıcı noktadır; geri bildirim "yanlış" demekle
yetinmeyip **neden ilgisiz olduğunu** açıklamalıdır
(`newgen-question-design.md` §3, `adhd-pedagogy.md` Ö4).

---

## 7. `G-EXAM` kalite kapısı

Koşullu: yalnız `mode:"EXAM"` **veya** `exam` bloğu varsa tetiklenir; yoksa `SKIPPED`
(geriye dönük uyum — mevcut modüller etkilenmez).

### FAIL üretir

| # | Denetim | Neyi engeller |
|---|---|---|
| 1 | `exam` bloğu mevcut (EXAM modunda) | — |
| 2 | `exam.stem` boş değil | Soruyu göstermeden çözme |
| 3 | `exam.transcriptionCheck` → `segments[]`'te var olan bir id | Doğrulama adımının atlanması |
| 4 | **≥1 `worked` segmenti VE `fadeFrom < steps.length`** | **Cevabın doğrudan verilmesi** |
| 5 | `exam.chain[]` boş değil; her halkada `concept` + `mappedTo`; her `mappedTo` id'si `segments[]`'te var | Zincirin uydurulması ("anlattım" tiyatrosu) |
| 6 | `exam.integrity` ∈ {`sound`, `flawed`, `out_of_frame`}; `sound` değilse `integrityNote` dolu | Bozuk sorunun sessizce sağlam sayılması |

### WARN üretir

- `exam.source` beyanı yok
- `exam.options` var ama `exam.distractorAnalysis` yok (çeldirici analizi kurulmamış)

### Denetim yöntemi — salt-regex

`validate_module.py` **MODULE_DATA JS nesnesini parse etmez**; G-CURRICULUM ve
G-VERIFY gibi salt-metin (regex/heuristik) çalışır. G-EXAM aynı yönteme tabidir:

- 4 numaralı denetim `worked` bloğu içindeki `text:` sayısını sayıp `fadeFrom`
  değeriyle karşılaştırır — **heuristiktir**; iç içe yapılar veya alışılmadık
  biçimlendirme yanıltabilir.
- 3 ve 5 numaralı denetimler, `_curriculum_collect`'in `mappedTo` için kullandığı
  id-toplama desenini yeniden kullanır.

Bu, kapının değerini düşürmez ama sınırını belirler: **kapı beyanın biçimini ölçer,
içeriğini değil.**

### DENETLEYEMEZ — dürüst sınır

`validate_module.py` çevrimdışıdır ve MCP erişimi yoktur (G-VERIFY ile aynı sınır):

- Transkripsiyonun fotoğrafa sadık olduğunu,
- Çözümün doğru olduğunu,
- Zincirin gerçekten eksiksiz olduğunu (eksik halka regex'le görünmez),
- `outcomeCode`'un gerçek bir kazanım olduğunu.

**Kapı yalnız yapının kurulduğunu ölçer.** Doğruluk yargısı modelindir ve insan
denetimine tabidir. Değeri şudur: zinciri iddia etmek, her halkayı bir segmente
bağlamayı zorunlu kılar.

---

## 8. Degrade protokolleri

| # | Durum | Davranış |
|---|---|---|
| **D1** | **Soru bozuk** — iki doğru şık, eksik veri, çelişkili öncül | `integrity:"flawed"` + `integrityNote`. `worked` yerine **tanı segmenti**: sorunun nesinin bozuk olduğu açıklanır. Zincir anlatımı **yine yapılır** (konu öğrenilir), ama uydurma cevap üretilmez. Öğrenci "ben anlamadım" sanmasın diye bu açıkça söylenir. |
| **D2** | **Kazanım bulunamıyor** | `chain[].outcomeCode` düşer; `curriculum` bloğu EXAM modunda **opsiyoneldir** → G-CURRICULUM tetiklenmez. Kullanıcıya bildirilir: "Bu soruyu bir MEB kazanımına bağlayamadım; konuyu genel bilgiyle anlattım." |
| **D3** | **Ders kitabı yok** (3·4·7·8·11·12. sınıf — TYMM kademeli yürürlüğü) | `verification.frame_source.kind:"program"` + `verdict:"supported_by_source"` (egitim-kaynak; `license` zorunlu). **Yeni kural yok** — mevcut G-VERIFY dalı aynen geçerli. |
| **D4** | **Soru çerçeve üstü** — olimpiyat, ileri yayınevi sorusu | `integrity:"out_of_frame"` + `integrityNote`. Soru **yine çözülür**, açık not eklenir: "Bu soru 7. sınıf çerçevesinin üstünde; çözümü 9. sınıfta gelen X kavramını gerektiriyor." |
| **D5** | **Fotoğraf okunamıyor** | SOR, tahmin etme. Kısmi okunuyorsa neyin belirsiz olduğu söylenir: "üçüncü şıkkın son rakamı okunmuyor — 6 mı 8 mi?" |

### EXAM ile CURRICULUM modu farkları (normatif)

| Kural | CURRICULUM | EXAM |
|---|---|---|
| `curriculum` bloğu | **zorunlu** | **opsiyonel** (D2) |
| `verification.scope.in_frame:false` | **üretimi durdurur** | **durdurmaz** (D4) |
| Yayın teklifi | üretim sonrası sorulur | **teklif edilmez** (K2) |
| Çerçeve kaynağı | ders kitabı → program | ders kitabı → program → (D4'te açıkça çerçeve dışı) |
| `exam` bloğu | yok | **zorunlu** |

**D4 istisnasının gerekçesi:** öğrencinin önüne gelmiş bir soruyu "çerçeve dışı" diye
reddetmek işe yaramaz. CURRICULUM modunda `in_frame:false` üretimi durdurur çünkü orada
model *neyi üreteceğini kendi seçer* ve çerçeve dışına taşması bir hatadır. EXAM modunda
soru **verilidir** — seçim yoktur. Doğru davranış reddetmek değil, dürüstçe etiketleyip
çözmektir.

---

## 9. Sınırlar ve kapsam dışı

1. **Sınav/ödev sırasında kullanım için değil.** Öğrenme sonrası araçtır. Modül
   kapanışında wellbeing dilinde (suçlayıcı olmayan) bir not bulunur.
2. **Yayın varsayılan KAPALI.** `/edupedia:yayinla` teklif edilmez. Kullanıcı açıkça
   isterse telif uyarısı verilir; karar kullanıcınındır — engellenmez.
3. **Tek soru.** Fotoğrafta birden çok soru varsa hangisi olduğu sorulur. Çoklu-soru
   **hata örüntüsü analizi** ("3 yanlışın 3'ü de kesir↔ondalık dönüşümünde") bilinçli
   olarak kapsam dışıdır — ayrı bir yetenek, ayrı bir spec.
4. **MEB dışı müfredat kapsam dışı.** IB/Cambridge sorusunda çerçeve kurulamaz;
   dürüstçe söylenir.
5. **Transkripsiyon insan denetimine tabidir.** Modülün 2. segmenti tam da bunun için var.
6. **Fotoğraf gömme yok** (K4). İhtiyaç doğarsa §10'daki Tier-2 işiyle birlikte
   ele alınmalı — ikisi aynı motor dalını paylaşır.

---

## 10. Bu tasarımdan bağımsız bulgu — Tier-2 açığı

`CONNECTORS.md §3` ve `curriculum-integration.md §2.1`, Tier-2 için
*"`get_figure(include_image=true)` → base64 göm"* der ve bu yolu **öncelikli** ilan eder
(2026-07-17 kullanıcı sözleşmesi). Ancak `assets/module-template.html` içinde `<img>`,
`data:image` veya base64 taşıyıcısı **yoktur**; `visual.kind` yalnız vektörel/yapısal
türleri tanır (`svg` · `pictogram` · `chart` · `table` · `numberline` · `fraction` ·
`math` · `mathml` · `labeled` · `flow` · `cards` · `gloss`).

`G-SELFCONTAINED` `data:` URI'sine izin verdiği için engel yoktur — yalnızca motorda
hazır dal yoktur. Yani **dokümante edilmiş ve "öncelikli" ilan edilmiş bir yetenek
fiilen bağlı değildir**; ders kitabı figürleri bugün modüle gömülemiyor olabilir.

Bu spec K4 sayesinde o dala ihtiyaç duymaz, dolayısıyla bloklanmaz. Ayrı iş olarak
ele alınmalıdır: doğrulanmalı (gerçekten kırık mı, yoksa `svgFigure` içine
`<image href="data:…">` gömen dokümante edilmemiş bir yol mu var), sonra ya motor
dalı eklenmeli ya dokümantasyon düzeltilmeli.

---

## 11. Uygulama sırası (öneri)

1. `references/exam-solving.md` — normatif davranış tek yerde tanımlanır
2. `validate_module.py` → `G-EXAM` + testler (TDD: fixture'lar önce)
3. `SKILL.md` §5/§6/§12 + `skill-manifest.yaml`
4. `commands/soru.md` — referansa delege eder, kuralı **tekrarlamaz**
   (bkz. `commands/modul.md`'deki "tek kaynak" uyarısı — çoğaltma sapmaya yol açtı)
5. `plugin.json` + `skills/start/SKILL.md`
6. Uçtan uca deneme: bir gerçek soru fotoğrafıyla, `module-auditor` denetimiyle
