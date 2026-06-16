# Changelog — BIST Uzmanı

Bu eklenti [Semantic Versioning](https://semver.org) (MAJOR.MINOR.PATCH) izler.

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
