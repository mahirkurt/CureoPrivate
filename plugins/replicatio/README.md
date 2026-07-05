# replicatio

**R + CSV istatistiksel analizlerin doğruluk & yeniden-üretilebilirlik denetim süiti.**

`replicatio`, R betikleriyle ham CSV üzerinde yürütülen istatistiksel analizlerin
**doğruluğunu** (yöntem seçimi, varsayım denetimi, hesap/raporlama tutarlılığı) ve
**yeniden-üretilebilirliğini** (sürüm sabitliği, kod-veri uyumu, bağımsız yeniden-uygulama)
denetler. Ham istatistiği olgun R paketlerine bırakır, muhakemeyi/sentezi skill'lerde tutar ve
denetim motoru olarak R-MCP sunucularını `.mcp.json` ile bağlar.

Tüm bulgular **severity-graded** (`CRITICAL` / `MAJOR` / `MINOR` / `OBSERVATION`),
**provenance-stamped** (her bulgu kaynak araç damgalı) ve **no-fabrication**'dır: çalıştırılamayan
bir denetim asla sahte geçti/kaldı üretmez — nedenini açıklayan bir `OBSERVATION` yazar.

> Bu süit **karar-destek** niteliğindedir; istatistiksel/klinik tavsiye değildir. Metabilim
> araçları (statcheck/GRIM/GRIMMER/SPRITE) **tetikleyici sinyallerdir**, nihai hakem değildir.

---

## Bileşenler

| Tür | Adet | İçerik |
|---|---|---|
| Skill | 6 | `start` (router) + `data-contract` (A) · `assumption-audit` (B) · `numeric-consistency` (C) · `repro-audit` (D) · `cross-validate` (F) |
| Komut | 5 | `/replicatio:audit-full` · `audit-data` · `audit-assumptions` · `audit-repro` · `audit-report` |
| MCP | 2 | `r-mcptools` (P0, stdio) · `rstudio-r` (P1, stdio, koşullu) — bkz. [CONNECTORS.md](./CONNECTORS.md) |
| R betiği | 8 | `bootstrap.R` · `00_session.R` · `01_data_contract.R` · `02_assumptions.R` · `03_numeric_consistency.R` · `04_crossvalidate.R` · `lib/severity.R` · `lib/report.R` |

### Denetim katmanları

| Katman | Skill | R betiği | Başlıca araçlar |
|---|---|---|---|
| A — Veri sözleşmesi | `data-contract` | `01_data_contract.R` | `readr::problems`, `pointblank`, `validate` |
| B — Yöntem & varsayım | `assumption-audit` | `02_assumptions.R` | `performance` (easystats), `DHARMa` |
| C — Raporlama tutarlılığı | `numeric-consistency` | `03_numeric_consistency.R` | `statcheck`, `scrutiny` (GRIM/GRIMMER), `rsprite2` (SPRITE) |
| D — Yeniden-üretilebilirlik | `repro-audit` | `00_session.R` | `renv`, `targets`, `testthat`, `covr`, `sessioninfo` |
| F — Bağımsız tekrar | `cross-validate` | `04_crossvalidate.R` | `waldo`, `specr` |

---

## Ön koşullar

- **Zorunlu:** R ≥ 4.3, `Rscript` PATH'te.
- **Önerilen (P1 `rstudio-r`):** Node 18+, ve `github.com/lerlerchan/rstudio-mcp-server`
  klonlanıp derlenmiş (`RSTUDIO_MCP_PATH` ortam değişkeni). Ayarlı değilse plugin yine yüklenir;
  D katmanı `Rscript` ile çalışır.
- **Opsiyonel (P2 `rmcp` self-host):** Python 3.10+ + `pip` (`pip install rmcp`). Yalnız
  sentetik/anonim veride; **gizli veri barındırılan uca gönderilmez** (bkz. Güvenlik).

R paket toolchain'i tek komutla kurulur:
```bash
Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.R"          # aktif kütüphaneye kur
Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.R" --renv   # proje-yerel renv ile sabitle
```
> `bootstrap.R` CRAN'a erişir (yalnız kurulum anında ağ gerektiren TEK adım). Kurulamayan paketleri
> dürüstçe raporlar; `mcptools`/`btw` CRAN'da bulunamazsa GitHub kurulum ipucu verir.

---

## Kurulum (CureoPrivate / cureonics-marketplace)

`replicatio`, `cureonics-marketplace` kataloğunun bir parçasıdır.
```text
/plugin marketplace add /mnt/thunderbolt/workspaces/CureoPrivate
/plugin install replicatio@cureonics-marketplace
```
Etkinleşince `.mcp.json` (P0/P1) otomatik bağlanır. İlk kullanımda bir kez `bootstrap.R` çalıştırın.

---

## Kullanım

```text
/replicatio:start                        # oryantasyon + preflight + yönlendirme
/replicatio:audit-full ./analiz          # A→F tüm katmanlar + konsolide Carbon HTML rapor
/replicatio:audit-data ./veri.csv        # yalnız A
/replicatio:audit-assumptions ./model.R  # yalnız B (model.R, modeli `model`e atamalı)
/replicatio:audit-repro ./proje          # yalnız D
/replicatio:audit-report ./.replicatio/findings   # toplanan bulgulardan HTML rapor
```
Bulgular `<analiz>/.replicatio/findings/<katman>.json` altına yazılır (şema:
`{layer, check, severity, message, tool, value, expected}`); rapor aynı dizinden okur ve
`replicatio-report.html` (IBM Carbon v11 + IBM Plex, emojisiz) üretir.

---

## Güvenlik (zorunlu — "Lethal Trifecta")

Roche-gizli ham veri varsayımıyla tasarlanmıştır:

- R-MCP sunucuları **yerel/stdio** çalışır; veri **salt-okunur** ele alınır (replicatio veriyi
  denetler, değiştirmez).
- İstatistik araçlarına/MCP'lerine **ağ çıkışı yoktur** (özel veri + güvenilmeyen içerik + dışa
  aktarım üçlüsü engellenir). TEK ağ-gerektiren adım `bootstrap.R`'nin CRAN kurulumudur.
- Sırlar `.mcp.json`'a gömülmez; `RSTUDIO_MCP_PATH` gibi değerler **ortam değişkeni** ile referans
  edilir.
- **P2 `rmcp` (barındırılan): gizli/Roche verisi gönderilmez** — yalnız sentetik/anonim veri veya
  self-host kopya. Bu yüzden `.mcp.json`'da bağlı değildir; opt-in'dir.
- Proje-kapsamlı kurulumda her MCP, sunucu-başına güven kapısından geçer.

---

## Token-maliyet notu

Bileşen envanterini ve projeksiyon token-maliyetini görmek için:
```bash
claude plugin details replicatio
```

---

## Yerel test akışı

```bash
# 1) Tek-oturum yükleme (marketplace olmadan)
claude --plugin-dir /mnt/thunderbolt/workspaces/CureoPrivate/plugins/replicatio
# 2) ya da katalogtan
#    /plugin marketplace add /mnt/thunderbolt/workspaces/CureoPrivate
#    /plugin install replicatio@cureonics-marketplace
# 3) toolchain
Rscript ./scripts/bootstrap.R
# 4) çalıştır
/replicatio:start
/replicatio:audit-full ./ornek-analiz
# 5) sıkı doğrulama (CI)
claude plugin validate /mnt/thunderbolt/workspaces/CureoPrivate/plugins/replicatio --strict
```

---

## Doğrulanmış sapmalar & açık TODO'lar

İnşa sırasında, "no-fabrication" gereği aşağıdaki noktalar resmî/paket dokümanlarına göre
**doğrulanıp** spesifikasyondan saptırıldı veya TODO bırakıldı:

- **SPRITE `scrutiny`'de yok.** Spesifikasyondaki `scrutiny::sprite()` mevcut değil; SPRITE ayrı
  `rsprite2` paketindedir (`set_parameters()` + `find_possible_distributions()`). `03` betiği
  rsprite2 kullanır; `min`/`max` ölçek sınırları verilmezse SPRITE dürüstçe atlanır.
- **btw→MCP yolu.** Spesifikasyondaki `mcptools::mcp_server(tools = btw::btw_tools())` doğrulanmadı;
  kanonik yol `btw::btw_mcp_server()` kullanıldı (`.mcp.json`). Minimal alternatif
  `mcptools::mcp_server()`.
- **plugin.json `components` alanı yok.** Resmî şemada böyle bir alan yoktur; bileşenler üst-düzey
  `commands`/`skills`/`mcpServers` yolları ile bildirilir (uygulanan biçim).
- **rstudio-r `setup` script içeriği** doğrulanmadı (TODO: `package.json`); hem `npm run setup` hem
  `npm install && npm run build` belgelendi. Repo: `lerlerchan/rstudio-mcp-server`.
- **`rmcp` Cloud Run URL canlılığı** probe edilmedi (TODO); URL `finite-sample/rmcp` README'sinden.
- **easystats p-çıkarımı.** `02` betiği `performance` check_* sonuçlarından p'yi savunmacı çıkarır
  (`attr(x,"p")` → metin yedeği); çıkarılamazsa sahte verdict yerine metinli `OBSERVATION` yazar.

Detay sözleşme: [CONNECTORS.md](./CONNECTORS.md).
