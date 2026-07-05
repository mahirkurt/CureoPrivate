---
description: Yalnız A katmanı — ham CSV girdisinin veri sözleşmesi denetimi (parse tanıları, eksiklik/tekrar/tip/sabit-sütun, opsiyonel pointblank/validate). Argüman = CSV yolu.
argument-hint: "<csv-yolu> [--rules <rules.R>]"
allowed-tools: Bash, Read, Glob
---

# /replicatio:audit-data — A Katmanı: Veri Sözleşmesi

Girdi: **$ARGUMENTS**

`data-contract` skill'ini çalıştırın. **No-fabrication:** veri içeriğini uydurmayın.

## Yürütme

1. CSV yolunu ayrıştırın (ilk argüman). Opsiyonel `--rules <rules.R>` (pointblank `agent` veya
   validate `rules`) varsa iletin. `OUT="$PWD/.replicatio/findings"`.
2. Toolchain preflight (readr/pointblank yoksa `bootstrap.R` önerin).
3. Sür:
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/01_data_contract.R" --csv "<csv>" [--rules "<rules.R>"] --out "$OUT"
   ```
4. `Read` → `$OUT/01_data_contract.json`; `data-contract` skill'inin şiddet-yorum kurallarını
   uygulayın (CRITICAL parse/≥%50-NA, MAJOR yüksek eksik/tekrar/all-NA, vb.), her bulguyu `tool`
   damgasıyla aktarın.

## Çıktı sözleşmesi
Son satır: `STATUS=<OK|FAIL>  CRITICAL=<n> MAJOR=<n> MINOR=<n> OBSERVATION=<n>`
(`FAIL` = en az bir CRITICAL veya betik hatası.)
