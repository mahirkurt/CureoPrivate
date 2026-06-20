---
name: bist-analist-kopilotu
version: 1.1.1
changelog: |
  1.1.1 (2026-06-20) — RSI eğim penceresi ve RS lookback enrich_snapshot imzasına
  opsiyonel parametre olarak açıldı (kalibrasyon için; varsayılanlar 3/13 korunur,
  davranış değişmez).
  1.1.0 (2026-06-20) — Teknik-duruş motoru yükseltmesi; geriye-dönük backtest
  bulgularına dayalı, look-ahead'siz öz-denetimle (scripts/backtest_posture.py)
  önce/sonra doğrulandı. (B/CRITICAL) RSI/fiyat ayrışması artık duruş puanına
  GİRİYOR — önceki sürümde hesaplanıp atılıyordu; methodology.md §2.4 ile kod
  tutarsızlığı (spec-drift) giderildi. (C/MAJOR) RSI okuması eğim-duyarlı:
  aşırı-satımdan yukarı dönüşün haksız cezalandırılması (trend-takipçi kör nokta)
  düzeltildi. (E/MAJOR) Göreli güç (relative_strength) katmanı — "yükselen dalga"
  etkisini hisse-seçim sinyalinden ayırır; Mod 1/2'ye endeks serisi çekimi ve
  göreli-güç sütunu eklendi. (D/MAJOR) Çok-zaman-dilimli veri çekimi netleştirildi:
  günlük (~4 ay) + haftalık (~12 ay) AYRI aralıklarla; çözünürlük-aralık
  bağımlılığı belgelendi. (A/MAJOR) Yeni betik backtest_posture.py — duruşun
  sızıntısız öz-denetimi (Spearman ρ/IC/isabet/benchmark-göreli/boşluk ayrıştırma).
  (F/MINOR) Boşluk (gap) maruziyeti göstergesi: EOD kör-noktası şeffaflığı.
  (G/OBSERVATION) Ufuk-koşullu güven kalibrasyonu (methodology.md §4). (H/OBSERVATION)
  Düşük-kapsam → güven düşürme bayrağı. Davranış geriye-uyumlu; tüm uyum/feragat
  sınırları korundu.
  1.0.1 (2026-06-16) — Bakım/kalite: yüksek-CC betik fonksiyonları davranış
  korunarak parçalandı, kullanılmayan import'lar temizlendi, gövdeye Scope Guard +
  Tetikleyiciler H2'leri eklendi.
  1.0.0 (2026-06-16) — İlk yayın. 4 mod (tek hisse / haftalık tarama / KAP-olay /
  izleme listesi), 9 referans, 9 deterministik betik, asset + eval seti. Borsa MCP
  omurgalı; karar-destek sınırı ve kanonik feragat gömülü.
description: >-
  Borsa İstanbul (BIST) hisseleri için tek, gerekçeli karar-destek brifingi üretir:
  çok zaman dilimli teknik + sektör-normalize temel + KAP açıklama/duygu + TCMB makro
  rejimini bir belgede sentezler. Dört mod: (1) tek hisse derin analizi, (2) haftalık
  tarama, (3) KAP/olay yorumu, (4) izleme listesi gözetimi. Borsa veri bağlayıcısını
  kullanır (gün sonu/EOD veri). Çıktı karar-destektir, yatırım tavsiyesi DEĞİLDİR.
  Tetikler — "GARAN analiz et", "THYAO yorumla", "bu hafta hangi hisseler", "haftalık
  tarama", "şu KAP açıklaması ne anlama geliyor", "bedelsiz/temettü kararını yorumla",
  "izleme listemi gözden geçir", BIST hisse adı + analiz/yorum/teknik/temel.
  EN — analyze a BIST stock, weekly BIST scan, interpret a KAP disclosure, review a
  BIST watchlist. Kapsam dışı: ABD hisseleri, kripto, TEFAS fonları, gün-içi scalping,
  kişiye özel al/sat tavsiyesi.
---

# BIST Analist Kopilotu

BIST hisseleri için **yayına hazır, kendine yeten bir karar-destek brifingi**
üretir. Teknik, temel, KAP-duygu ve makro katmanlarını **tek bir gerekçeli
belgede** birleştirir; her sonucu güven düzeyi ve karşıt senaryoyla sunar; sonda
zorunlu feragatle kapatır.

> **Sınır (asla ihlal etme):** Çıktılar **karar destek** niteliğindedir;
> **yatırım danışmanlığı/tavsiyesi değildir.** Kişiye özel "al/sat/topla"
> yönlendirmesi yapılmaz. Ayrıntı için `references/compliance.md`.

---

## Kapsam / Sınır (Scope Guard)

- **Kapsam:** Yalnızca **BIST hisseleri** ve gerektiğinde BIST endeksleri / TCMB makro bağlamı.
- **Kapsam dışı:** ABD hisseleri, kripto varlıklar, TEFAS fonları, gün-içi scalping/emir defteri/derinlik. Bunlar sorulursa kapsam dışı olduğu kibarca bildirilir.
- **Veri sınırı:** Fiyat verisi gün sonu (EOD) ve gecikmelidir; gün-içi mikro-yapı iddiası üretilmez.
- **Uyum sınırı:** Karar-destek; yatırım danışmanlığı/tavsiyesi değil. Kişiye özel "al/sat/topla" yönlendirmesi yapılmaz; üçüncü-taraf analist hedefleri yalnız "doğrulanmamış" bağlam olarak anılır. Tam ilke: `references/compliance.md`.

## Tetikleyiciler

- **TR:** "GARAN analiz et", "THYAO yorumla", "ASELS teknik+temel durum"; "bu hafta hangi hisseler", "haftalık tarama"; "şu KAP açıklaması ne anlama geliyor", "bedelsiz/temettü kararını yorumla"; "izleme listemi gözden geçir".
- **EN:** analyze a BIST stock · weekly BIST scan · interpret a KAP disclosure · review a BIST watchlist.
- **Yönlendirme detayları ve kapsam-dışı sapmalar:** `evals/triggers.md` (mod yönlendirme tablosu + disambiguasyon + 22 örnek vaka).

---

## Adım 0 — Bağlayıcı sağlık kontrolü (zorunlu)

Her analizden önce **Borsa** veri bağlayıcısının erişilebilir olduğunu küçük bir
probla doğrula (`search_symbol(query, market="bist")`). Erişilemiyorsa canlı fiyat
**varsayma**; yalnızca `web_search`/`web_fetch` ile, kaynak ve kısıtı açıkça
belirterek sınırlı bağlam ver. **Uydurma fiyat/rakam üretme.** (Detay:
`evals/mcp_smoke_test.md`.)

Veri sınırı: fiyat verisi büyük ölçüde **gün sonu (EOD)** ve gecikmelidir; **gün
içi emir defteri/derinlik içermez.** Günlük ve haftalık ufuk için yeterli;
gün-içi mikro-yapı iddiası üretme.

### Çok-zaman-dilimli veri çekimi (çözünürlük-aralık bağımlılığı)

> **Kritik:** Borsa `get_historical_data` çözünürlüğü, talep edilen **aralık
> uzunluğuyla** ölçeklenir: kısa aralık (≤~30 gün) günlük, orta aralık (~3 ay)
> haftalık, uzun aralık (~1 yıl) aylık bar döndürür. Bu yüzden 1W çapa ile 1d
> kurulum **tek bir çağrıdan elde edilemez** — aksi hâlde `confluence` tek dilime
> çöker ve "çapa" tek başına karar verir (ampirik olarak zayıf sinyal).

İki dilim için **iki ayrı çağrı** yap:
- **Haftalık çapa (1W):** ~**12 aylık** aralık (≈52 hafta bar). Uzun seri,
  SMA200/MACD/T3 gibi göstergelerin tanımlı olmasını ve duruşun düşük-kapsama
  düşmemesini sağlar.
- **Günlük kurulum (1d):** ~**3–4 aylık** aralık (günlük bar). Aşırı-satım dönüşü,
  kırılım ve oynaklık bu dilimde çok daha erken/belirgin görünür; haftalık çapanın
  yapısal olarak geç yakaladığı keskin mean-reversion'ı bu dilim yakalar.

Her iki seriyi `scripts/technical_plus.py` → `enrich_snapshot` ile zenginleştirip
`confluence({"1W": haftalık, "1d": günlük})` ile birleştir.

### Göreli güç için endeks serisi (zorunlu, "yükselen dalga" düzeltmesi)

Mutlak teknik duruş, herkesin yükseldiği bir haftada hisse-seçim becerisini
ölçemez. Benchmark (XU100) ve ilgili sektör endeksi (ör. XBANK) için de haftalık
seri çek (`get_historical_data`/`get_index_data`); `enrich_snapshot(ohlc,
index_closes=...)` çağrısıyla **göreli güç** duruşa dahil edilir.

---

## Mod seçimi

| Niyet | Mod |
| :-- | :-- |
| Tek sembol + "analiz/yorum/teknik+temel" | **1 — Tek hisse derin analizi** |
| Haftalık aday evreni / "öne çıkanlar" / tarama | **2 — Haftalık tarama** |
| Tek bir KAP açıklaması / olay / sert hareket | **3 — KAP / olay yorumu** |
| Verili sembol listesinin gözetimi / "ne değişti" | **4 — İzleme listesi gözetimi** |

Belirsizse tek soruyla netleştir. Kapsam dışı talepleri (`evals/triggers.md`)
kibarca reddet veya karar-destek diline çevir.

---

## Kanıt zinciri disiplini

Her sonuç bir araç çağrısı + değer + as-of tarihine kadar izlenebilir olmalı.
Brifingin **gövdesinde** ham JSON, araç adı veya "MCP" gibi makine-dili
**sızıntısı olmaz** (her şey düzyazı/tabloya çevrilir). Bitirmeden önce çıktıyı
`scripts/brief_lint.py` ile denetle.

---

## Mod 1 — Tek hisse derin analizi

1. **Sembol çöz:** `search_symbol` → doğru BIST sembolü.
2. **Anlık + profil:** `get_quick_info`, `get_profile`.
3. **Teknik (çok zaman dilimli):** `get_historical_data` **iki ayrı çağrı** — haftalık çapa için ~12 ay, günlük kurulum için ~3–4 ay (çözünürlük-aralık bağımlılığı: bkz. Adım 0) — + `get_technical_analysis` + `get_pivot_points`. Benchmark (XU100) ve sektör endeksi serisini de çek. Yerel çapraz kontrol ve duruş için `scripts/technical_helpers.py` ve `scripts/technical_plus.py` (RSI/MACD/MA/Bollinger/Supertrend/T3, RSI/fiyat **ayrışması**, **göreli güç**, `trend_posture`, `confluence`); `enrich_snapshot(ohlc, index_closes=...)` ile göreli gücü duruşa kat. Yöntem: `references/methodology.md`.
4. **Temel (sektör-normalize):** `get_financial_ratios`, `get_financial_statements`, `get_sector_comparison`, `get_earnings`, `get_dividends`, `get_corporate_actions`. Kalite skoru: `scripts/financial_quality_score.py`. Yöntem: `references/fundamental-methodology.md`. Analist hedefleri yalnız "doğrulanmamış/üçüncü-taraf" bağlam.
5. **KAP & duygu:** `get_news` → `scripts/kap_fetch.py` (normalize) → `scripts/sentiment_score.py` + `scripts/kap_materiality.py`. Taksonomi: `references/kap-taxonomy.md`.
6. **Makro:** `get_evds_data`/`get_macro_data`/`get_fx_data`/`get_bond_yields` → `scripts/macro_context.py` (rejim). Yöntem: `references/evds-macro.md`.
7. **Brifingi yaz:** `assets/brief-template.md` (8 bölüm) + `assets/scenario-matrix-template.md`. Stil: `references/report-style.md`. Örnek: `evals/golden_outputs/garan-mod1-ornek.md`.

## Mod 2 — Haftalık tarama

1. Teknik tarama: `scan_stocks` (göstergeler/preset'ler; gramer için `get_scanner_help`). Temel süzme: `screen_securities` (`get_screener_help`). Benchmark bağlamı için XU100 (ve ilgili sektör endeksi) haftalık serisini de çek.
2. Adayları teknik duruş + temel kalite + KAP duygu ile **gerekçelendir**; bu bir **araştırma gündemidir, alım listesi değildir.** Her adayın duruşunu `enrich_snapshot(ohlc, index_closes=XU100)` ile üret — böylece **göreli güç** (endeksi geçiyor mu) ve **ayrışma** sinyalleri duruşa girer; mutlak güç tek başına "yükselen dalga"da yanıltır.
3. Çıktı: gerekçeli aday tablosu — sütunlar **duruş · endekse göreli güç · izlenecek seviye/tetik · 1–2 satır neden**. Tek-hafta ufkunda güven tavanını düşük tut (bkz. `references/methodology.md §4`: haftalık duruş çok-haftalık eğilim için anlamlıdır, tek-hafta yön tahmini için zayıf sinyaldir). Kapanışta feragat.

> **Öz-denetim (opsiyonel ama önerilir):** Tarama mantığının ampirik isabetini periyodik doğrulamak için `scripts/backtest_posture.py` (look-ahead'siz Spearman ρ / IC / isabet / benchmark-göreli / boşluk ayrıştırması). Bu, duruş motorunun belirli bir ufukta gerçekten sinyal taşıyıp taşımadığını ölçer; sonuç güven kalibrasyonunu besler.

## Mod 3 — KAP / olay yorumu

1. Olayı al: `get_news` (+ ilgili sembolde `get_quick_info`/`get_historical_data` ile fiyat/hacim bağlamı).
2. Sınıflandır + materyalite: `scripts/kap_materiality.py` (`references/kap-taxonomy.md`). Duygu: `scripts/sentiment_score.py`.
3. Olası yön + reaksiyon penceresi: `references/kap-reaction.md` (EOD; "haber alımı/satışı" uyarısı, hacim teyidi). Sonuç güven + karşıt senaryoyla; **emir değil.**

## Mod 4 — İzleme listesi gözetimi

1. Her sembol için güncel durum anlık görüntüsünü `assets/watchlist-state-schema.json` biçiminde üret.
2. Önceki anlık görüntü varsa `scripts/watchlist_diff.py` ile **deterministik** karşılaştır.
3. Çıktı: önceliğe göre sıralı değişim listesi (duruş değişti, seviye kırıldı, yeni KAP, RSI bölge değişimi). Yalnız değişen boyutları yaz.

---

## Çıktı kalite kapısı

Brifingi vermeden önce `scripts/brief_lint.py` ile doğrula:
- Kanonik feragat var; kişiselleştirilmiş al/sat emri yok; makine/araç sızıntısı yok;
  sayılar as-of tarihiyle; fiyat varsa EOD kaydı; senaryo matrisi + güven göstergesi var.

Stil ilkeleri (`references/report-style.md`): bilimsel Türkçe, kendine yeten belge,
kaynaklar resmî ad + tarih, her sonuç güven + karşıt senaryo, makine-dili yok.

---

## Composability

Brifingi belgeye/sunuma dökmek için `carbon-html-report` / `carbon-pptx` (ayrı
kurulur, paketlenmez). Tamamlayıcı pazar/sektör istatistiği için Finmap MCP
(opsiyonel). Gerçek-zaman/gün-içi (IBKR vb.) **tasarım gereği kapsam dışıdır.**

> Tüm modların çıktısı karar-destektir; yatırım danışmanlığı/tavsiyesi değildir.
