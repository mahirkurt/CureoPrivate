---
name: start
description: >-
  replicatio denetim süitine giriş ve yönlendirme. R + CSV istatistiksel analizlerin doğruluk
  ve yeniden-üretilebilirlik denetiminde hangi katmanın gerektiğini belirler, R-MCP
  connector'larının (r-mcptools P0, rstudio-r P1) ve R toolchain'inin kurulu/erişilebilir
  olduğunu kontrol eder, eksikse bootstrap'a yönlendirir, beş denetim modunu tanıtır ve
  kullanıcının niyetine göre doğru komuta/katmana yönlendirir. İlk kez süitle çalışırken, "neyi
  denetlemeliyim / nereden başlamalıyım / connector'larım bağlı mı / R paketleri kurulu mu" türü
  oryantasyon sorularında kullanın. Tetikleyiciler — replicatio başlat, denetim nereden, audit
  start, reproducibility audit, statistical audit, "analizimi denetle", connector kontrolü,
  R toolchain kurulumu.
metadata:
  version: "0.1.0"
---

# replicatio — Başlangıç & Yönlendirme

Bu skill, `replicatio` denetim süitinin **giriş kapısıdır**. R + CSV istatistiksel analizlerin
**doğruluğunu** (yöntem/varsayım/raporlama) ve **yeniden-üretilebilirliğini** (sürüm/kod-veri/
bağımsız tekrar) denetler. Ağır işi beş katman skill'i ve onların sürdüğü R betikleri yapar; bu
skill yalnızca preflight + yönlendirme yapar. Beş adımı sırayla yürütün.

Tüm denetim **severity-graded** (CRITICAL/MAJOR/MINOR/OBSERVATION), **provenance-stamped**
(her bulgu kaynak araç damgalı) ve **no-fabrication**'dır: çalışmayan bir denetim asla sahte
geçti/kaldı üretmez — nedenini açıklayan bir OBSERVATION yazar.

---

## Adım 1 — Karşılama

Kullanıcıya kısaca: replicatio, R betikleriyle ham CSV üzerinde yürütülen analizleri **altı
katmanda** denetler:

| Katman | Skill | Ne denetler |
|---|---|---|
| A | `data-contract` | Girdi validasyonu (tip/aralık/eksiklik/tekillik/parse) |
| B | `assumption-audit` | Yöntem seçimi + model varsayımları (normallik, homoskedastisite, VIF, aşırı yayılım) |
| C | `numeric-consistency` | Raporlama tutarlılığı (statcheck, GRIM/GRIMMER/SPRITE) |
| D | `repro-audit` | Yeniden-üretilebilirlik (renv, targets, testthat, sürüm/seed) |
| F | `cross-validate` | Bağımsız yeniden-uygulama (waldo karşılaştırma, specr robustluk) |

Tam denetim için `/replicatio:audit-full`, tek katman için ilgili komut kullanılır; konsolide
IBM Carbon HTML rapor `/replicatio:audit-report` ile üretilir.

---

## Adım 2 — Toolchain & Connector Preflight

Denetime başlamadan **bağlanırlığı ve toolchain'i raporlayın**. [`CONNECTORS.md`](../../CONNECTORS.md)
**normatiftir** (P0–P3 sözleşmesi).

1. **R + Rscript var mı?** `Rscript --version`. Yoksa: kullanıcıya R ≥ 4.3 kurmasını söyleyin;
   süit çalışamaz.
2. **R paketleri kurulu mu?** Hızlı kontrol:
   `Rscript -e 'cat(all(c("pointblank","performance","statcheck","scrutiny","renv","waldo","jsonlite") %in% rownames(installed.packages())))'`
   `FALSE` ise: bir kez `Rscript ${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.R` (opsiyonel `--renv`)
   çalıştırmaya yönlendirin. Bu, dış-ağ (CRAN) erişimi gerektirir — yalnız kurulum anında.
3. **R-MCP connector'ları (yüzey-bilinçli):**
   - **P0 `r-mcptools`** (stdio, `btw::btw_mcp_server()`) — Claude Code plugin'i `.mcp.json` ile
     otomatik bağlar; canlı R introspeksiyonu (paket dokümanı, ortam nesneleri, oturum meta).
     `btw`+`mcptools` kurulu olmalı (bootstrap kurar).
   - **P1 `rstudio-r`** (stdio, node) — yalnız `${RSTUDIO_MCP_PATH}` ayarlı + derlenmişse başlar
     (testthat/R CMD check otomasyonu, D katmanı). Ayarlı değilse **zarif düşüş**: D katmanı
     `Rscript` ile çalışmaya devam eder.

> **Yüzey ayrımı:** **Claude Code**'da plugin `.mcp.json` roster'ını otomatik bağlar. **claude.ai
> web**'de stdio yerel sunucular bağlanamaz; orada R betikleri yine `Rscript` ile çalışır,
> canlı-introspeksiyon MCP'leri olmadan. "Her şey otomatik bağlı" varsaymayın.

Eksik connector/paket → durmayın; ilgili katmanın `Rscript` yolu yine çalışır.

---

## Adım 3 — Denetim Hedefini Belirle

Kullanıcıdan denetlenecek **analiz dizinini** ve girdileri toplayın:
- Ham veri: bir `.csv` (A katmanı).
- Fitli model: modeli `model` değişkenine atayan bir `.R` betiği (B katmanı).
- Rapor edilen sayılar: APA-stili metin (`.txt/.md/.pdf`) ve/veya `mean,sd,n[,min,max]` sütunlu
  bir CSV (C katmanı).
- Proje: `renv.lock`/`_targets.R`/`tests/` içeren dizin (D katmanı).
- İki sonuç dosyası (rapor edilen vs bağımsız yeniden-hesap; `.rds` veya `result` bırakan `.R`)
  (F katmanı).

Bulgular `./.replicatio/findings/<katman>.json` altına yazılır (veya `--out <dizin>`).

---

## Adım 4 — Komut Tanıtımı

| Komut | Ne yapar |
|---|---|
| `/replicatio:audit-full [analiz-dizini]` | **A→F tüm katmanlar** + konsolide Carbon HTML rapor |
| `/replicatio:audit-data [csv-yolu]` | Yalnız **A** — veri sözleşmesi |
| `/replicatio:audit-assumptions [model-betiği]` | Yalnız **B** — yöntem/varsayım |
| `/replicatio:audit-repro [proje-dizini]` | Yalnız **D** — yeniden-üretilebilirlik |
| `/replicatio:audit-report [bulgular-dizini]` | Toplanan bulgulardan **Carbon HTML rapor** |

C ve F katmanları doğrudan `numeric-consistency` ve `cross-validate` skill'leriyle ya da
`audit-full` içinden çalışır.

---

## Adım 5 — Niyet Yönlendirme + Scope Guard

| Kullanıcı niyeti | Yönlendir |
|---|---|
| "Tüm analizi baştan sona denetle" | `/replicatio:audit-full` |
| "Veri/CSV kalitesi, eksik/aykırı değer" | `audit-data` → `data-contract` |
| "Doğru test mi, varsayımlar tutuyor mu" | `audit-assumptions` → `assumption-audit` |
| "Rapor edilen p/ortalama tutarlı mı (GRIM/statcheck)" | `numeric-consistency` |
| "Bu tekrar üretilebilir mi (renv/seed/test)" | `audit-repro` → `repro-audit` |
| "İki bağımsız sonuç aynı mı / robust mu" | `cross-validate` |
| Belirsiz / çok-katmanlı | `/replicatio:audit-full` |

**Scope Guard (devir):**
- İstatistiksel analizi **yapmak/yazmak** (yeni model kurmak) → bu süit değil; ilgili analiz
  rehberi/skill'i (örn. tez/biyoistatistik skill'leri). replicatio yalnız **mevcut** analizi
  **denetler**.
- Yayın-kalite render → `carbon-html-report` / `carbon-quarto-scientific`.
- Literatürle metodolojik gerekçelendirme gerekiyorsa, ortamda **varsa** akademik MCP'leri
  (Consensus/Elicit/Scholar/Paper Search) **fırsatçı** kullanın (P3); yoksa zarifçe devam edin —
  replicatio bunları bağlamaz.

Şüphede: `/replicatio:audit-full` evrenseldir → katman katman ilerler, eksik girdileri atlar.
