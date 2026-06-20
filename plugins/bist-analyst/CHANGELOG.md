# Changelog — BIST Uzmanı

Bu eklenti [Semantic Versioning](https://semver.org) (MAJOR.MINOR.PATCH) izler.

## [1.1.3] — 2026-06-20

Günlük-veri toplayıcı + günlük katman kalibrasyonu. Davranış/varsayılanlar değişmedi.

### Eklendi
- **`scripts/stitch_daily.py`** — günlük-veri toplayıcı/birleştirici. Borsa
  `get_historical_data` çözünürlüğü aralık-uzunluğuyla ölçeklendiğinden (≤30g→günlük,
  ~3ay→haftalık, ~1yıl→aylık), uzun bir günlük seri ≤30-günlük dilimler halinde
  çekilip birleştirilmelidir. Bu betik dilimleri tarihe göre tekilleştirir+sıralar,
  `walkforward_calibrate`/`backtest_posture`'ın beklediği frames.json'a çevirir ve
  bir kapsam raporu (SMA50/200 tanımlı mı, bölünme-artefaktı şüphesi) üretir.

### Karar (günlük katman, kanıta dayalı)
- Kalibrasyon günlük katmanda yeniden koşuldu (8 BIST hissesi + XU100, 101 günlük
  bölünme-düzeltmeli bar, SMA50 tanımlı, motor-ufku 5 ve 10 işlem günü, 10 rejim) →
  **varsayılan 3/13 hiçbir kesitte yenilmedi** (h=10 eş-en-iyi fark=0,000; h=5 tek-en-iyi;
  RS-kapalı win=3 tüm rejimlerde rank-1). Aylık verinin (2,8) imâsı günlükte düzeldi.
- **Dürüst çerçeve (çekişmeli denetimli):** bu "doğrulama" DEĞİL **non-inferiority**
  bulgusudur — cell SE'si (≈0,15) ızgara açıklığından (≈0,09) büyük + pencereler örtüşür
  (etkin N≪10), hiçbir cell ayırt edilemez. Ayrıca **tüm ρ negatif** kalır → motorun
  mutlak öngörü gücüne dair **ayrı** bir uyarı (parametre sorunu değil), bağımsız
  incelenmeli. **Karar: varsayılan korunur** (değiştirmek için kanıt yok).

## [1.1.2] — 2026-06-20

Walk-forward kalibrasyon aracı + çok-rejim kanıtı. Davranış geriye-uyumlu; varsayılanlar değişmedi.

### Eklendi
- **`scripts/walkforward_calibrate.py`** — teknik-duruş motorunun iki kalibrasyon
  parametresini (RSI eğim penceresi × göreli güç lookback, ızgara {2,3,5}×{8,13,21})
  **sızıntısız** ve **çok-rejimli** tarayan araç. Her cell'i `backtest_posture`'a
  delege eder (skorlama mantığı çoğaltılmaz). Modlar: `--smoke` (hızlı errors=0
  doğrulaması), tek-rejim ızgara (`--file`), çok-rejim (`--multi` dosyalar / `--windows N`
  ile tek seriyi rejim pencerelerine dilimleme). Sıra-kararlılığı için min-competition
  (beraberlik-duyarlı) sıralama; rejimler arası ρ̄/medyan/σ + top-1/top-3.

### Değişti (geriye-uyumlu)
- `backtest_posture.backtest_posture` imzasına opsiyonel `rsi_slope_window=3`,
  `rs_lookback=13` pass-through (enrich_snapshot'a iletilir). Varsayılan çıktı
  **bit-özdeş** (öz-denetim ρ=0.949 korunur).

### Karar (kanıta dayalı)
- İlk çok-rejim kalibrasyon (14 BIST hissesi + XU100, 36 aylık bölünme-düzeltmeli bar,
  12 rejim) **varsayılan 3/13'ü değiştirmek için gerekçe bulamadı**: en-iyi↔varsayılan
  ortalama-ρ farkı (~0,04) rejim-içi gürültünün (σ≈0,29) çok altında (z≈0,5); en-iyi
  cell kesitler arası kayıyor (aşırı-uyum imzası); mutlak isabet her yerde ≤ yazı-tura.
  Çok-mercekli + çekişmeli sentez (3 mercek + reddiye) yüksek-güvenle "varsayılanı koru"
  dedi. **Sınır:** aylık bar/1-aylık ufuk motoru eksik-test eder; nihai kalibrasyon
  günlük/haftalık tam-kapsam veri + out-of-sample bölme gerektirir.

## [1.1.1] — 2026-06-20

### Değişti (geriye-uyumlu yama)
- `technical_plus.enrich_snapshot` imzasına iki opsiyonel parametre eklendi:
  `rsi_slope_window=3` (RSI eğim penceresi) ve `rs_lookback=13` (göreli güç lookback).
  Bunlar `_series_slope(window=...)` ve `relative_strength(lookback=...)` çağrılarına
  geçirilir. **Varsayılanlar gömülü sabitlerle birebir aynıdır (3/13)** → varsayılan
  `enrich_snapshot(ohlc)` ve `(ohlc, index_closes=...)` çıktısı v1.1.0 ile **bit
  düzeyinde özdeştir**. Skorlama mantığı, eşikler, varsayılan davranış veya alanlar
  değişmedi. Amaç: ayrı bir `walkforward_calibrate.py`'nin RSI eğim penceresini
  {2,3,5} ve RS lookback'ini {8,13,21} ızgarasında taramasını mümkün kılmak.

## [1.1.0] — 2026-06-20

Teknik-duruş motoru yükseltmesi. Look-ahead'siz geriye-dönük backtest ile önce/sonra
doğrulandı; davranış geriye-uyumlu, tüm uyum/feragat sınırları korundu.

### Eklendi
- **(A)** `scripts/backtest_posture.py` — teknik duruşun **sızıntısız (look-ahead-free)**
  öz-denetimi: Spearman ρ, bilgi katsayısı (IC), mutlak + benchmark-göreli isabet,
  boşluk (gap) ayrıştırması. Motorun kendi isabetini ölçen geri-besleme döngüsü.
- **(E)** `relative_strength` katmanı — hisseyi endekse (XU100/sektör) göre ölçer;
  "yükselen dalga" etkisini hisse-seçim sinyalinden ayırır. Mod 1/2'ye endeks serisi
  çekimi ve göreli-güç sütunu eklendi.
- **(F)** `gap_exposure` — seans-arası boşluk maruziyeti göstergesi (EOD kör-nokta şeffaflığı).

### Düzeltildi / Değişti
- **(B, CRITICAL)** RSI/fiyat **ayrışması artık duruş puanına giriyor** — önceki
  sürümde hesaplanıp atılıyordu (methodology.md §2.4 ile kod arasındaki spec-drift giderildi).
  Bullish ayrışma +1, bearish −1 katkı.
- **(C)** RSI okuması **eğim-duyarlı**: aşırı-satımdan yukarı dönüşün haksız
  cezalandırılması (trend-takipçi kör nokta) düzeltildi. Eğim bilinmiyorsa klasik
  davranış birebir korunur (geriye-uyumlu).
- **(D)** Çok-zaman-dilimli veri çekimi netleştirildi (günlük ~3–4 ay + haftalık ~12 ay
  **ayrı** çağrılarla); çözünürlük-aralık bağımlılığı `SKILL.md` ve `methodology.md`'de belgelendi.
- **(G/H)** Ufuk-koşullu güven kalibrasyonu (methodology.md §4) + düşük-kapsam → güven
  düşürme bayrağı (`low_coverage`, `coverage_ratio`).

### Notlar
- `technical_plus.py` 808 → 1055 satır; tüm 10 betik sözdizimi-temiz ve import-temiz.
- Değişmeyen 8 betiğin self-test çıktısı bayt-bayt korundu; golden brifing `brief_lint`'ten geçiyor.

## [1.0.1] — 2026-06-16

### Değişti (davranış korunarak — bakım/kalite)
- **Kod kalitesi (D5):** Yüksek siklomatik-karmaşıklıklı altı fonksiyon odaklı
  yardımcılara bölündü (`macro_context.classify_regime`, `technical_plus.trend_posture`
  + `confluence`, `financial_quality_score.quality_score`, `brief_lint.lint`,
  `watchlist_diff._compare_symbol`). Tüm script'ler için self-test çıktısı bayt-bayt
  korundu; harici davranış değişikliği yoktur.
- **Temizlik:** Kullanılmayan `import sys` üç script'ten kaldırıldı.
- **Dokümantasyon (D4):** `bist-analist-kopilotu` gövdesine açık "Kapsam / Sınır
  (Scope Guard)" ve "Tetikleyiciler" H2 bölümleri eklendi.
- **Sürümleme (D10):** Her iki beceri frontmatter'ına `version` + `changelog` eklendi.

## [1.0.0] — 2026-06-15

### Eklendi
- İlk yayın. `bist-analist-kopilotu` analist becerisi (4 mod) eklenti olarak paketlendi.
- **Borsa MCP** veri omurgası `.mcp.json` ile remote (HTTP) bağlayıcı olarak
  pakete dahil edildi (`https://borsamcp.fastmcp.app/mcp`).
- `start` oryantasyon/yönlendirme becerisi: Scope Guard, Borsa MCP sağlık
  kontrolü (Adım 0) ve dört moda yönlendirme.
- Deterministik yardımcı script'ler (duygu skoru, KAP materyalite, finansal
  kalite skoru, makro rejim, teknik yardımcılar, brief lint, watchlist diff).
- Referans dokümanları (veri kaynakları, MCP tool şeması, EVDS makro, metodoloji,
  rapor stili, temel analiz metodolojisi, KAP taksonomisi/reaksiyon, uyum).
- Eklenti dokümantasyonu (README), uyum/feragat ilkeleri ve composability haritası.

### Notlar
- Çıktılar karar destek niteliğindedir; yatırım danışmanlığı/tavsiyesi değildir.
- Fiyat verisi gün sonu (EOD) ağırlıklıdır; gün-içi mikro-yapı kapsam dışıdır.
- TCMB EVDS makro katmanı sunucu-tarafı anahtarla çalışır; kullanıcı kurulumu
  gerektirmez.
