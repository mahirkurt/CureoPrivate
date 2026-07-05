---
name: assumption-audit
description: >-
  replicatio B katmanı — istatistiksel yöntem seçimi + model varsayımı denetimi. Fitli bir model
  nesnesi üzerinde easystats performance suite'ini çalıştırır (check_normality,
  check_heteroscedasticity, check_collinearity/VIF, check_autocorrelation, check_outliers ve
  GLM/GLMM için check_overdispersion + DHARMa simulate_residuals); p-değerlerini şiddete haritalar.
  Kullanıcı model varsayımlarını, doğru test seçimini, normallik/homoskedastisite/çoklu-bağlantı/
  aşırı yayılım/residual diagnostiği sorduğunda kullanın. Tetikleyiciler — model varsayımı,
  assumption check, normallik, normality, homoskedastisite, heteroscedasticity, çoklu bağlantı,
  collinearity VIF, aşırı yayılım, overdispersion, doğru test seçimi, residual diagnostic, DHARMa.
metadata:
  version: "0.1.0"
allowed-tools: Bash, Read, Glob
---

# replicatio — B Katmanı: Yöntem & Varsayım Denetimi

Seçilen istatistiksel yöntemin veriye uygunluğunu ve model varsayımlarının tutup tutmadığını
denetler. **No-fabrication:** test sonuçlarını uydurmayın; sayısal p çıkartılamazsa betik bunu
OBSERVATION olarak metinle raporlar — onu aynen aktarın.

## Yürütme

1. **Model girdisini hazırla.** Kullanıcının fitli modeli `model` değişkenine atayan bir `.R`
   betiği olmalı (örn. `model <- lm(y ~ x, data = d)`). Yoksa, kullanıcıdan analiz betiğindeki
   model satırlarını izole eden küçük bir `.R` dosyası isteyin (veri yükleme + tek `model <- ...`).
   Farklı değişken adı varsa `--object <ad>` kullanılır.

2. **Yöntem-uygunluğu ön-muhakemesi (siz).** Betiği çalıştırmadan önce, sonuç değişkeninin tipine
   ↔ seçilen teste bakın: sürekli→OLS/t; sayım→Poisson/NB; oran/ikili→lojistik; tekrarlı/kümeli→
   karışık model. Açık bir uyumsuzluk varsa bunu bir MAJOR muhakeme-notu olarak ekleyin (betik
   bunu otomatik bilmez; sizin katkınız).

3. **Betiği sür:**
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/02_assumptions.R" --model "<model.R>" --out "$PWD/.replicatio/findings"
   ```

4. **Bulguları oku** (`Read` → `.replicatio/findings/02_assumptions.json`) ve yorumla:
   - p < 0.001 → **MAJOR**, p < 0.01 → **MINOR**, p < 0.05 → **OBSERVATION** ihlal (severity.R).
   - VIF ≥ 10 → MAJOR, ≥ 5 → MINOR çoklu-bağlantı.
   - Sayım/oran modelinde aşırı yayılım veya DHARMa uniformity/dispersion ihlali → varyans yapısı
     yanlış belirlenmiş olabilir.
   - `assumptions-check_model.png` üretildiyse kullanıcıya görsel tanıyı işaret edin.

5. **Düzeltici öneri (yorum, uygulama değil).** İhlal varsa uygun rota: robust SE, dönüşüm,
   NB/quasi-Poisson, karışık model, GLS. Öneriyi gerekçeli verin; uygulamayı kullanıcıya bırakın.

## Kapsam Dışı
- Modeli **yeniden kurmak/düzeltmek** — replicatio denetler, model yazmaz.
- Raporlanan sayıların tutarlılığı (p↔stat) → `numeric-consistency` (C).
- Veri kalitesi → `data-contract` (A).

## Notlar
- Doğru raporlama için `parameters`/`effectsize`/`gtsummary` önerilebilir (betik kurar) ama bu
  skill bunları zorunlu kılmaz.
- Canlı R introspeksiyonu gerekiyorsa (model nesnesini incelemek) P0 `r-mcptools` connector'ı
  kullanılabilir; yoksa `Rscript` yolu yeterlidir.
