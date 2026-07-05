---
description: Yalnız D katmanı — bir projenin yeniden-üretilebilirlik + sürüm sabitliği denetimi (renv lock/sync, targets güncelliği, testthat/covr, sessioninfo, seed/RNG disiplini). Argüman = proje dizini.
argument-hint: "[proje-dizini] (varsayılan: çalışılan dizin)"
allowed-tools: Bash, Read, Glob, Grep
---

# /replicatio:audit-repro — D Katmanı: Yeniden-Üretilebilirlik

Proje: **$ARGUMENTS** (boşsa çalışılan dizin).

`repro-audit` skill'ini çalıştırın. **No-fabrication:** test/lock durumunu uydurmayın.

## Yürütme

1. `OUT="<proje>/.replicatio/findings"`. Toolchain preflight.
2. Ortam & sürüm:
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/00_session.R" --project "<proje>" --out "$OUT"
   ```
   (renv.lock yok / senkron değil → MAJOR.)
3. **targets** (varsa `_targets.R`): `Rscript -e 'targets::tar_outdated()'` → boş değilse MAJOR.
4. **Testler:** rstudio-r MCP'si bağlıysa `r_test_package`/`r_check_package` araçlarını çağırın;
   değilse `Rscript -e 'testthat::test_dir("tests/testthat")'` + `covr::percent_coverage(...)`.
   Test yoksa → MAJOR-OBSERVATION sınır bulgusu.
5. **Seed disiplini:** Grep ile stokastik adım (boot/MI/MCMC/sample/rf) ara; `set.seed` yoksa MAJOR.
6. `Read` → `$OUT/00_session.json` + eklediğiniz gözlemler; `repro-audit` skill kurallarıyla yorumlayın.

## Çıktı sözleşmesi
Son satır: `STATUS=<OK|FAIL>  CRITICAL=<n> MAJOR=<n> MINOR=<n> OBSERVATION=<n>`
(`FAIL` = test FAIL veya en az bir CRITICAL.)
