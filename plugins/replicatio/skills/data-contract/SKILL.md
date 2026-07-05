---
name: data-contract
description: >-
  replicatio A katmanı — ham CSV girdisinin veri sözleşmesi denetimi. CSV ayrıştırma tanıları
  (readr::problems), yapısal denetimler (boyut, tekrar satır, sütun-bazlı eksiklik, sabit/tamamen-NA
  sütun) ve opsiyonel pointblank ajan + validate kural seti çalıştırır; tip/aralık/eksiklik/
  tekillik/referansel ihlalleri CRITICAL/MAJOR/MINOR/OBSERVATION'a haritalar. Kullanıcı veri
  kalitesini, CSV doğrulamasını, eksik/aykırı değerleri, tip uyumunu veya bir "data contract"
  kurmayı sorduğunda kullanın. Tetikleyiciler — veri kalitesi, CSV doğrulama, data contract,
  eksik değer, missing data, aykırı değer, tip uyumu, duplicate rows, pointblank, validate.
metadata:
  version: "0.1.0"
allowed-tools: Bash, Read, Glob
---

# replicatio — A Katmanı: Veri Sözleşmesi (Data Contract)

Ham CSV'nin **analize girmeden önceki** bütünlüğünü denetler. Ham istatistiği R betiği yapar;
siz orkestrasyon + yorum yaparsınız. **No-fabrication:** veri içeriğini uydurmayın; yalnız betiğin
ürettiği bulguları raporlayın.

## Yürütme

1. **Girdiyi belirle.** Kullanıcıdan CSV yolunu alın. Birden çok CSV varsa Glob ile listeleyin ve
   her biri için ayrı koşum yapın.

2. **Betiği sür** (analiz dizininde):
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/01_data_contract.R" --csv "<path.csv>" --out "$PWD/.replicatio/findings"
   ```
   Kullanıcının bir kural dosyası (pointblank `agent` veya validate `rules` bırakan `.R`) varsa
   `--rules "<rules.R>"` ekleyin. Yoksa betik temel bir pointblank ajanı (rows_distinct +
   col_vals_not_null) ve yapısal denetimleri yine çalıştırır.

3. **Bulguları oku.** `Read` ile `.replicatio/findings/01_data_contract.json`. Şema:
   `{layer, check, severity, message, tool, value, expected}`.

4. **Yorumla ve raporla.** Bulguları şiddete göre grupla:
   - **CRITICAL** — CSV ayrıştırılamadı veya ≥%50 eksik bir sütun: analiz güvenilmez.
   - **MAJOR** — yüksek eksiklik/tekrar oranı, tamamen-NA sütun, parse tip-zorlamaları.
   - **MINOR** — düşük eksiklik/tekrar.
   - **OBSERVATION** — boyut, sabit sütun, geçen pointblank kontrolü.
   Her bulguyu `tool` damgasıyla aktarın (örn. `readr::problems`, `pointblank`, `validate::confront`).

5. **Boşluk dürüstlüğü.** Bir paket kurulu değilse (OBSERVATION + bootstrap önerisi gelir) bunu
   gizlemeyin. Veri hakkında betiğin ölçmediği bir iddiada bulunmayın.

## Kapsam Dışı

- Veriyi **düzeltmek/temizlemek** (imputation, dedup uygulama) — replicatio yalnız denetler,
  değiştirmez. Önerebilirsiniz; uygulamayı kullanıcıya/analiz akışına bırakın.
- Modelleme varsayımları → `assumption-audit` (B).
- Sürüm/yeniden-üretim → `repro-audit` (D).

## Notlar
- Eşik→şiddet haritası `scripts/lib/severity.R` içindedir (eksiklik için crit=0.50/major=0.20).
  Domain'e özgü eşikler için `--rules` ile pointblank/validate kuralı geçin.
- `--out` verilmezse bulgular `./.replicatio/findings` altına yazılır; rapor aynı dizinden okur.
