# Modül Mimarisi ve `MODULE_DATA` Şeması

> Bir `carbon-edupedia` modülü, `assets/module-template.html` içindeki **etkileşim
> motoru** (engine) + üstteki **`MODULE_DATA` veri nesnesi**nden oluşur. İçeriği
> üretmek = `MODULE_DATA`'yı doldurmak. Motoru değiştirmeyin; veriyi yerleştirin.

## İçindekiler
1. Üst düzey anatomi
2. Tam `MODULE_DATA` şeması
3. Segment akışı kuralları
4. İskeleden doldurmaya — adım adım
5. Kalite öz-kontrol listesi

---

## 1. Üst düzey anatomi

```
modul.html
├── <head>: IBM Plex CDN, satır-içi Carbon CSS (:root token'ları), reduced-motion
├── <body>
│   ├── SVG icon sprite (gizli, currentColor)
│   ├── Üst çubuk: modül başlığı + ilerleme rayı + XP sayacı + rozet kasası
│   ├── #stage: aktif segment buraya render edilir (tek-odak)
│   └── Alt: yönlendirme (Geri / Devam), erişilebilirlik kontrolleri
└── <script>
    ├── const MODULE_DATA = { ... }   ← İÇERİK BURADA (sen doldurursun)
    └── engine: segment render, etkileşim mantığı, XP/ilerleme, özet  ← DEĞİŞMEZ
```

**Tek-odak ilkesi:** Aynı anda yalnız bir segment görünür (ped İlke 5, dış yük).
Üst çubuk yürütücü dışsallaştırmadır (ped İlke 4): nerede olduğum, ne kadar
kaldığı, ne kazandığım hep görünür.

## 2. Tam `MODULE_DATA` şeması

```js
const MODULE_DATA = {
  meta: {
    title: "Hücre ve Organeller",        // modül başlığı (TR)
    subject: "Fen Bilimleri",            // ders
    gradeLevel: "7. Sınıf",              // sınıf düzeyi
    mode: "MODULE",                      // MODULE|QUIZ|FLASHCARDS|GAME|EXPLAINER|ASSESSMENT|SERIES
    accent: "#009d9a",                   // ders aksanı (carbon-child-system §3)
    estimatedMinutes: 18,                // tahmini süre (üst çubukta gösterilir)
    coverPictogram: "ic-idea",           // kapak piktogram/ikon anahtarı
    sourceCitation: "MEB Fen 7, Ünite 1 / kullanıcı ders notu" // KAYNAK (SKILL.md §7)
  },

  learner: {                             // opsiyonel kişiselleştirme
    name: "",                            // boşsa nötr; "Işık" gibi verilebilir
    showTimer: false                     // süre sayacı varsayılan KAPALI (ped §3)
  },

  objectives: [                          // başta gösterilir: "Bu modülde…"
    "Hücrenin temel kısımlarını tanıyacaksın.",
    "Bitki ve hayvan hücresini ayırt edeceksin.",
    "Organellerin görevlerini eşleştireceksin."
  ],

  rewards: {
    xpPerCorrect: 10,
    firstTryBonus: 5,
    badges: [                            // ustalık rozetleri (bilgilendirici, ped İlke 6)
      { id: "explorer", label: "Hücre Kâşifi", pictogram: "pic-rocket",
        condition: "module-complete" },
      { id: "sharp", label: "Keskin Göz", pictogram: "ic-trophy",
        condition: "no-mistakes-segment" }
    ]
  },

  segments: [
    // 1) öğretim
    { type: "teach", id: "t1", title: "Hücre nedir?", pictogram: "pic-idea",
      body: ["<p>...</p>", "<ul><li>...</li></ul>"],
      keyTerms: [{ term: "hücre", def: "canlının en küçük yapı birimi" }],
      visual: { kind: "svg", ref: "<svg ...>...</svg>" } },          // opsiyonel

    // 2) etkileşim (OTR — teach'ten sonra zorunlu)
    { type: "mcq", id: "q1", title: "Mini Yarışma", pictogram: "pic-rocket",
      instructions: "Doğru seçeneği işaretle.",
      questions: [
        { stem: "...", options: ["...","...","..."], correctIndex: 1,
          explanation: "...", sourceRef: "t1" }
      ] },

    // 3) öğretim
    { type: "teach", id: "t2", ... },

    // 4) mola (uzun modülde)
    { type: "brainbreak", id: "b1", title: "Kısa Mola", pictogram: "ic-pause",
      prompt: "30 saniye ayağa kalk, derin nefes al.", durationSec: 30 },

    // 5) eşleştirme
    { type: "match", id: "m1", title: "Organel Eşleştirme", pictogram: "pic-idea",
      mode: "text", pairs: [{ a: "Mitokondri", b: "enerji üretir" }, ...] },

    // 6) flashcard / fillblank / order / sorting / hotspot ... (interaction-patterns.md)

    // son) kontrol noktası (karma geri-getirme, ped İlke 8)
    { type: "checkpoint", id: "c1", title: "Kontrol Noktası", pictogram: "ic-trophy",
      recap: ["...", "..."],
      mixedQuestions: [ /* mcq şeması */ ],
      selfAssess: ["Bunu öğrendim", "Tekrar etmeliyim"] }
  ]
};
```

**Şema notları:**
- `meta.sourceCitation` **zorunlu** (kaynak izlenebilirliği). Kaynak yoksa
  SKILL.md §7'ye göre işaretle.
- `mcq` sorularında `sourceRef` doğrulanabilirlik kancası (validate_module.py).
- `body` sade HTML; `<script>`/satır-içi olay yok (motor olayları bağlar).
- `visual.ref` ya bir sprite ikon anahtarı (`"ic-idea"`) ya satır-içi `<svg>`.
- Pictogram anahtarları sprite'taki `id`'ler veya gömülü Carbon piktogramı.

## 3. Segment akışı kuralları (motor + planlama)

1. **Parçalama:** Hiçbir `teach` ekranda 4–6 kısa birimi aşmaz (ped İlke 1).
2. **OTR:** İki `teach` arasında ≥1 etkileşim (ped İlke 2). Saf okuma zinciri yok.
3. **Erken başarı:** İlk etkileşim kolay; zorluk kademeli (ped İlke 6).
4. **Mola:** ≥6 segmentlik modülde ≥1 `brainbreak` (ped §4).
5. **Anında ödül:** Her etkileşim sonrası anında geri bildirim + XP (ped İlke 3).
6. **Geri-getirme:** Modül `checkpoint` ile biter (ped İlke 8) — motor ayrıca
   otomatik **özet** ekranı (XP, ustalık, rozet, öz-değerlendirme) üretir.
7. **Tek-odak:** Aynı anda tek segment (ped İlke 5).

## 4. İskeleden doldurmaya — adım adım

1. Kaynağı **kazanımlara** ayır (her kazanım → bir öğretim segmenti).
2. Her kazanım için: `teach` yaz (kaynağa sadık, sadeleştirilmiş, görselli) →
   ardından uygun etkileşim seç (interaction-patterns.md) ve **kaynaktan** soru/
   çift/cevap üret.
3. Akışı kur: teach→etkileşim→(mola)→teach→... → checkpoint.
4. `meta.accent`'i derse göre seç (carbon-child-system §3); piktogramları seç
   (icon-pictogram-svg); gereken kavram için özgün SVG çiz.
5. `MODULE_DATA`'yı şablona yerleştir; motoru değiştirme.
6. `validate_module.py` ile doğrula; ihlalleri gider.

## 5. Kalite öz-kontrol listesi (emisyon öncesi)

- [ ] Her `teach` kısa ve tek-kazanım; uzun olan bölünmüş (İlke 1).
- [ ] İki teach arası ≥1 etkileşim (İlke 2); saf okuma zinciri yok.
- [ ] Her `mcq` sorusunda `correctIndex` + `explanation` + `sourceRef` var.
- [ ] Quiz cevapları kaynaktan izlenebilir; kaynak-dışı olgu yok (SKILL.md §7).
- [ ] ≥6 segmentte ≥1 `brainbreak`; modül `checkpoint` ile biter.
- [ ] Aksan derse uygun; metin rengi daima `--cds-text-primary` (aksan değil).
- [ ] Görseller satır içi; emoji yok; durum çift-kanal (renk+ikon+metin).
- [ ] `meta.sourceCitation` dolu; süre varsayılan kapalı.
- [ ] Ton teşvik edici; ceza mekaniği yok (§3 etik).
