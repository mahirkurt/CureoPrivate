---
name: cross-validate
description: >-
  replicatio F katmanı — bağımsız yeniden-uygulama. Rapor edilen bir sonucu ikinci bir bağımsız
  yolla üretip waldo::compare() ile karşılaştırır (snapshot tutarlılığı), ve opsiyonel olarak
  specr ile spesifikasyon-eğrisi/çoklu-evren robustluk analizi yapar. Kullanıcı çapraz doğrulama,
  bağımsız tekrar, sonuç karşılaştırma, hassasiyet/robustluk veya çoklu-evren analizi istediğinde
  kullanın. Tetikleyiciler — çapraz doğrulama, cross-validate, bağımsız tekrar, independent
  replication, sonuç karşılaştırma, waldo compare, hassasiyet analizi, robustness, specification
  curve, multiverse, çoklu evren.
metadata:
  version: "0.1.0"
allowed-tools: Bash, Read, Glob
---

# replicatio — F Katmanı: Bağımsız Yeniden-Uygulama

Bir sonucun, orijinalden bağımsız bir hesap yoluyla yeniden üretilip üretilemediğini ve
spesifikasyon seçimlerine ne kadar dayanıklı olduğunu denetler. Bu katmanın **bağımsız yeniden
hesabı sizin (veya kullanıcının) ürettiği ikinci uygulamadır** — replicatio onu orijinalle
**karşılaştırır**, kendisi "doğru cevabı" uydurmaz.

## Yürütme

1. **İki sonucu hazırla.**
   - **A (rapor edilen):** orijinal analizin çıktısı — bir `.rds` (kaydedilmiş nesne) veya `result`
     değişkenini bırakan bir `.R`.
   - **B (bağımsız yeniden-hesap):** aynı niceliği farklı bir kod yoluyla (farklı paket/elle
     formül/temiz yeniden-yazım) hesaplayan ikinci uygulama, yine `.rds` veya `result` bırakan `.R`.
     Bu ikinci uygulamayı yazmanız gerekebilir; orijinal koddan KOPYALAMAYIN (bağımsızlık şarttır).

2. **Karşılaştır:**
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/04_crossvalidate.R" --a "<A.rds|A.R>" --b "<B.rds|B.R>" \
     --tol 1e-8 --out "$PWD/.replicatio/findings"
   ```
   `--tol` sayısal tolerans (varsayılan tam eşitlik). Bulgular `04_crossvalidate.json`.

3. **Yorumla:**
   - Özdeş (tol dahilinde) → OBSERVATION: sonuç bağımsızca doğrulandı.
   - Farklı → **MAJOR**: waldo fark bloklarını aktarın; farkın kaynağını (yuvarlama, farklı
     varsayılan, gerçek hata) birlikte araştırın.

4. **Opsiyonel robustluk (specr).** Spesifikasyon seçimlerinin (kovaryat seti, örneklem filtresi,
   model ailesi) sonucu ne kadar oynattığını görmek için `specr::setup()` çıktısını `spec_setup`
   olarak bırakan bir `.R` verin:
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/04_crossvalidate.R" --specs "<specs.R>" --out "$PWD/.replicatio/findings"
   ```
   Tahmin **işareti** spesifikasyonlar arası değişiyorsa → MAJOR (sonuç kırılgan).

5. **Boşluk dürüstlüğü.** İkinci bağımsız uygulama yapılamıyorsa bunu açıkça söyleyin; "doğrulandı"
   demeyin. specr kurulu değilse OBSERVATION + bootstrap önerisi gelir.

## Kapsam Dışı
- Orijinal analizi **düzeltmek**. Fark bulursanız raporlayın; düzeltmeyi kullanıcıya bırakın.
- Raporlanan-sayı iç tutarlılığı → `numeric-consistency` (C).

## Notlar
- Anonimleştirilmiş/sentetik veride, bağımsız bir istatistiksel oracle olarak P2 `rmcp`
  (barındırılan) kullanılabilir — **ama gizli/Roche verisi ASLA barındırılan uca gönderilmez**
  (CONNECTORS.md §P2). Varsayılan olarak `.mcp.json`'da bağlı değildir.
