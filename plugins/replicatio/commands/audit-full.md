---
description: A→F tüm katmanları (veri sözleşmesi · varsayım · raporlama tutarlılığı · yeniden-üretilebilirlik · bağımsız tekrar) bir analiz dizininde sırayla çalıştırır ve konsolide IBM Carbon HTML rapor üretir. Argüman = analiz dizini.
argument-hint: "[analiz-dizini] (varsayılan: çalışılan dizin)"
allowed-tools: Bash, Read, Glob, Grep
---

# /replicatio:audit-full — Tam Denetim (A→F)

Hedef analiz dizini: **$ARGUMENTS** (boşsa çalışılan dizin).

Tüm katmanları sırayla yürütün; ham istatistiği R betikleri yapar, siz orkestrasyon + yorum
yaparsınız. [`CONNECTORS.md`](../CONNECTORS.md) normatiftir. Bulgular tek dizine yazılır:
`<analiz-dizini>/.replicatio/findings`. **No-fabrication:** yalnız betiklerin ürettiği bulguları
raporlayın.

## Yürütme

1. **Preflight.** `Rscript --version` ve toolchain kontrolü (`start` skill Adım 2). Paket eksikse
   `Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.R"` önerin/çalıştırın. `OUT="<dir>/.replicatio/findings"`.

2. **Girdi keşfi.** Glob/Grep ile dizinde belirle: `.csv` (A), modeli `model` atayan `.R` (B),
   APA-stili metin / `mean,sd,n` CSV (C), `renv.lock`/`_targets.R`/`tests/` (D), karşılaştırılacak
   sonuç çiftleri (F). Bulunmayan katmanı **atla** ve raporda "girdi yok → atlandı" diye işaretle.

3. **Katmanları sür** (mevcut girdiler için):
   - **D (önce, ortam):** `Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/00_session.R" --project "<dir>" --out "$OUT"` → `repro-audit` skill.
   - **A:** `Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/01_data_contract.R" --csv "<csv>" --out "$OUT"` → `data-contract` skill.
   - **B:** `Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/02_assumptions.R" --model "<model.R>" --out "$OUT"` → `assumption-audit` skill.
   - **C:** `Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/03_numeric_consistency.R" --text "<metin>" --stats "<stats.csv>" --out "$OUT"` → `numeric-consistency` skill.
   - **F:** iki bağımsız sonuç varsa `04_crossvalidate.R` → `cross-validate` skill.
   Her katman için ilgili skill'in yorum kurallarını uygulayın (şiddet eşikleri, çerçeve, çaprazlar).

4. **Konsolide rapor:**
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/lib/report.R" --out "$OUT" --html "<dir>/.replicatio/replicatio-report.html"
   ```

5. **Özet.** Şiddet sayımlarını (CRITICAL/MAJOR/MINOR/OBSERVATION) ve en kritik bulguları
   provenance damgasıyla özetleyin; HTML rapor yolunu verin.

## Çıktı sözleşmesi
Son satır deterministik:
`STATUS=<OK|FAIL>  CRITICAL=<n> MAJOR=<n> MINOR=<n> OBSERVATION=<n>  REPORT=<html-yolu>`
(`FAIL` = en az bir CRITICAL veya betik/Rscript hatası.)
