# Changelog — BIST Uzmanı

Bu eklenti [Semantic Versioning](https://semver.org) (MAJOR.MINOR.PATCH) izler.

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
