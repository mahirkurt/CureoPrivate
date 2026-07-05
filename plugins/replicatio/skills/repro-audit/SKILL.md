---
name: repro-audit
description: >-
  replicatio D katmanı — yeniden-üretilebilirlik + sürüm sabitliği denetimi. renv lockfile/sync
  durumu, targets boru hattı güncelliği (tar_outdated), testthat birim testleri (rstudio-r MCP'si
  varsa r_test_package, yoksa Rscript), covr kapsamı, sessioninfo ortam yakalama ve seed/parallel-RNG
  disiplinini denetler. Kullanıcı yeniden-üretilebilirliği, sürüm sabitliğini, renv/targets/testthat
  durumunu, seed disiplinini veya ortam yakalamayı sorduğunda kullanın. Tetikleyiciler — yeniden
  üretilebilirlik, reproducibility, renv, lockfile, targets, birim test, unit test, testthat,
  coverage, sürüm sabitliği, seed, set.seed, ortam yakalama, sessioninfo.
metadata:
  version: "0.1.0"
allowed-tools: Bash, Read, Glob
---

# replicatio — D Katmanı: Yeniden-Üretilebilirlik & Sürüm Sabitliği

Bir analizin bağımsız bir makinede/zamanda aynı sonucu vermesini sağlayan koşulları denetler.
**No-fabrication:** test/lock durumunu uydurmayın; betiğin ve (varsa) rstudio-r MCP'sinin gerçek
çıktısını raporlayın.

## Yürütme

1. **Ortam & sürüm yakalama:**
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/00_session.R" --project "<proje-dizini>" --out "$PWD/.replicatio/findings"
   ```
   Bu, `sessioninfo` + `renv::status()` çalıştırır; `session-info.txt` ve `00_session.json` üretir.
   - `renv.lock` yok → **MAJOR** (sürümler sabit değil).
   - renv kütüphanesi lockfile ile senkron değil → **MAJOR**.

2. **Boru hattı güncelliği (varsa).** Projede `_targets.R` varsa:
   ```bash
   Rscript -e 'if (requireNamespace("targets", quietly=TRUE)) print(targets::tar_outdated())'
   ```
   Boş değilse → güncel-olmayan hedefler var → MAJOR (kod-veri-çıktı uyumu kırık).

3. **Birim testleri.** Tercih sırası:
   - **rstudio-r MCP'si bağlıysa** (P1): `r_test_package` / `r_check_package` araçlarını çağırın
     (paket projeleri için R CMD check + testthat). Çıktıyı şiddete haritalayın (test FAIL →
     CRITICAL/MAJOR; NOTE/WARNING → MINOR).
   - **Bağlı değilse** (zarif düşüş): `tests/` varsa
     `Rscript -e 'testthat::test_dir("tests/testthat")'`; kapsam için
     `Rscript -e 'if (requireNamespace("covr", quietly=TRUE)) print(covr::percent_coverage(covr::package_coverage()))'`.
   - Test yoksa → MAJOR-OBSERVATION sınırı: "birim test yok; davranış regresyona açık".

4. **Seed / parallel-RNG disiplini.** `00_session.json`'daki `rng_kind` bulgusuna ek olarak,
   analiz kodunda `set.seed()` çağrısı arayın (Grep). Stokastik adım (bootstrap, MI, MCMC, RF) var
   ama `set.seed` yoksa → MAJOR. Paralel kod varsa `RNGkind("L'Ecuyer-CMRG")` beklenir.

5. **Bulguları oku & raporla** (`Read` → `.replicatio/findings/00_session.json` + eklediğiniz
   gözlemler). Eksik MCP/paket → zarifçe belirt, durma.

## Kapsam Dışı
- Testleri **yazmak** veya renv'i **başlatmak** — replicatio denetler; `bootstrap.R --renv` bir
  kurulum yardımıdır, denetim değil. Eksikleri rapor edip kullanıcıya bırakın.
- Sonuç sayılarının doğruluğu → `cross-validate` (F) / `numeric-consistency` (C).

## Notlar
- `r_test_package`/`r_check_package`/`r_document_package`/`r_execute` araçları rstudio-r
  (github.com/lerlerchan/rstudio-mcp-server) MCP'sinden gelir; `${RSTUDIO_MCP_PATH}` ayarlı ve
  derlenmiş olmalı (CONNECTORS.md P1).
