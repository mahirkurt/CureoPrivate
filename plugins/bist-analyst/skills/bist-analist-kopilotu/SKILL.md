---
name: bist-analist-kopilotu
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

## Adım 0 — Bağlayıcı sağlık kontrolü (zorunlu)

Her analizden önce **Borsa** veri bağlayıcısının erişilebilir olduğunu küçük bir
probla doğrula (`search_symbol(query, market="bist")`). Erişilemiyorsa canlı fiyat
**varsayma**; yalnızca `web_search`/`web_fetch` ile, kaynak ve kısıtı açıkça
belirterek sınırlı bağlam ver. **Uydurma fiyat/rakam üretme.** (Detay:
`evals/mcp_smoke_test.md`.)

Veri sınırı: fiyat verisi büyük ölçüde **gün sonu (EOD)** ve gecikmelidir; **gün
içi emir defteri/derinlik içermez.** Günlük ve haftalık ufuk için yeterli;
gün-içi mikro-yapı iddiası üretme.

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
3. **Teknik (çok zaman dilimli):** `get_historical_data` (1W ve 1d) + `get_technical_analysis` + `get_pivot_points`. Yerel çapraz kontrol ve duruş için `scripts/technical_helpers.py` ve `scripts/technical_plus.py` (RSI/MACD/MA/Bollinger/Supertrend/T3, `trend_posture`, `confluence`). Yöntem: `references/methodology.md`.
4. **Temel (sektör-normalize):** `get_financial_ratios`, `get_financial_statements`, `get_sector_comparison`, `get_earnings`, `get_dividends`, `get_corporate_actions`. Kalite skoru: `scripts/financial_quality_score.py`. Yöntem: `references/fundamental-methodology.md`. Analist hedefleri yalnız "doğrulanmamış/üçüncü-taraf" bağlam.
5. **KAP & duygu:** `get_news` → `scripts/kap_fetch.py` (normalize) → `scripts/sentiment_score.py` + `scripts/kap_materiality.py`. Taksonomi: `references/kap-taxonomy.md`.
6. **Makro:** `get_evds_data`/`get_macro_data`/`get_fx_data`/`get_bond_yields` → `scripts/macro_context.py` (rejim). Yöntem: `references/evds-macro.md`.
7. **Brifingi yaz:** `assets/brief-template.md` (8 bölüm) + `assets/scenario-matrix-template.md`. Stil: `references/report-style.md`. Örnek: `evals/golden_outputs/garan-mod1-ornek.md`.

## Mod 2 — Haftalık tarama

1. Teknik tarama: `scan_stocks` (göstergeler/preset'ler; gramer için `get_scanner_help`). Temel süzme: `screen_securities` (`get_screener_help`).
2. Adayları teknik duruş + temel kalite + KAP duygu ile **gerekçelendir**; bu bir **araştırma gündemidir, alım listesi değildir.**
3. Çıktı: gerekçeli aday tablosu; her aday için 1–2 satır neden + izlenecek seviye/tetik. Kapanışta feragat.

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
