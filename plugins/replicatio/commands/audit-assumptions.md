---
description: Yalnız B katmanı — fitli bir model üzerinde yöntem-uygunluğu + varsayım denetimi (easystats performance + GLM için DHARMa). Argüman = modeli `model` değişkenine atayan bir R betiği.
argument-hint: "<model.R> [--object <ad>]"
allowed-tools: Bash, Read, Glob
---

# /replicatio:audit-assumptions — B Katmanı: Yöntem & Varsayım

Girdi: **$ARGUMENTS**

`assumption-audit` skill'ini çalıştırın. **No-fabrication:** test sonuçlarını uydurmayın;
sayısal p çıkartılamazsa betiğin metin sonucunu aynen aktarın.

## Yürütme

1. Model betiğini ayrıştırın (modeli `model` — ya da `--object <ad>` — değişkenine atamalı).
   `OUT="$PWD/.replicatio/findings"`.
2. **Yöntem-uygunluğu ön-muhakemesi:** sonuç tipi ↔ test uyumunu siz değerlendirin (sürekli/
   sayım/ikili/kümeli → uygun aile). Açık uyumsuzluk = MAJOR muhakeme-notu.
3. Toolchain preflight (performance yoksa `bootstrap.R`).
4. Sür:
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/02_assumptions.R" --model "<model.R>" [--object "<ad>"] --out "$OUT"
   ```
5. `Read` → `$OUT/02_assumptions.json`; `assumption-audit` skill'inin eşiklerini uygulayın
   (p<0.001→MAJOR, VIF≥10→MAJOR, overdispersion/DHARMa ihlalleri). `assumptions-check_model.png`
   üretildiyse işaret edin. Düzeltici öneriyi gerekçeli verin (uygulamayı kullanıcıya bırakın).

## Çıktı sözleşmesi
Son satır: `STATUS=<OK|FAIL>  CRITICAL=<n> MAJOR=<n> MINOR=<n> OBSERVATION=<n>`
(`FAIL` = model nesnesi alınamadı veya en az bir CRITICAL.)
