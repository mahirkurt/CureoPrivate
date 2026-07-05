# replicatio — Connector Sözleşmesi (P0–P3)

Bu dosya, `replicatio`'nun denetim motoru olarak kullandığı R-MCP sunucularının **tek doğruluk
kaynağıdır**. `.mcp.json` yalnız geçerli MCP server objelerini içerir (JSON yorum kabul etmez);
katman yapısı, ön koşullar, güvenlik notları ve "yoksa ne olur" davranışı burada belgelenir.

**Tasarım ilkesi — yerel/stdio öncelikli.** `.mcp.json` *yalnızca* yerel/stdio sunucu bağlar.
Barındırılan (HTTP/uzak) sunucular bilinçli olarak **opt-in**'dir ve `.mcp.json`'a konmaz —
Roche-gizli ham veriyle çalışıldığı varsayımıyla "Lethal Trifecta" (özel veri + güvenilmeyen
içerik + dışa-aktarım kanalı) riskini sıfırlamak için.

> **Yüzey notu.** **Claude Code**'da plugin etkinleşince `.mcp.json` roster'ı (P0/P1) otomatik
> bağlanır. **claude.ai web**'de stdio yerel sunucular bağlanamaz; orada R betikleri yine
> `Rscript` ile çalışır, canlı-introspeksiyon MCP'leri olmadan (tüm katmanlar betik yoluyla
> işlevseldir). Proje-kapsamlı kurulumda her MCP, sunucu-başına güven kapısından geçer.

---

## Özet tablo

| Tier | Sunucu | Taşıma | Bağlı? | Rol |
|---|---|---|---|---|
| **P0** | `r-mcptools` | stdio (Rscript) | `.mcp.json` (oto) | Canlı R introspeksiyonu (paket dokümanı, ortam, oturum) |
| **P1** | `rstudio-r` | stdio (node) | `.mcp.json` (koşullu) | testthat / R CMD check otomasyonu (D katmanı) |
| **P2** | `rmcp` | http (uzak) | **opt-in, ASLA gizli veri** | Bağımsız istatistiksel oracle (yalnız sentetik/anonim) |
| **P3** | akademik MCP'ler | (ortamda) | bağlanmaz | Metodolojik gerekçe / birincil-kaynak (fırsatçı) |

---

## P0 — `r-mcptools` (zorunlu, yerel)

- **Amaç.** R oturumunu bir MCP sunucusuna çevirir; `btw` araç seti ile paket dokümantasyonu,
  global ortam nesneleri ve oturum meta-verisi üzerinde canlı introspeksiyon sağlar. B/D
  katmanlarında model/ortam nesnelerini canlı incelemek için.
- **Taşıma.** stdio (`Rscript -e "btw::btw_mcp_server()"`).
- **Ön koşul.** R ≥ 4.3 + `mcptools` + `btw` paketleri. `scripts/bootstrap.R` her ikisini kurar.
- **Kurulum.** `.mcp.json`'da tanımlı; plugin etkinleşince otomatik başlar. Manuel test:
  `Rscript -e "btw::btw_mcp_server()"` (stdio bekler).
- **Güvenlik.** Tamamen yerel; ağ çıkışı yok. Yalnız yerel R oturumunu açar.
- **Doğrulama notu.** Kanonik btw→MCP yolu `btw::btw_mcp_server()`'dır (btw README/homepage).
  Spesifikasyonun ilk taslağındaki `mcptools::mcp_server(tools = btw::btw_tools())` çağrısı
  **doğrulanmadı** (btw_tools() ellmer `chat$register_tools()` içindir); bu yüzden doğrulanmış
  `btw::btw_mcp_server()` kullanıldı. Minimal alternatif: `mcptools::mcp_server()` (yalnız
  yerleşik oturum araçları — kaynak roxygen'de birebir doğrulanmış).
- **Yoksa ne olur.** Tüm denetim katmanları yine `Rscript` ile çalışır; yalnız *canlı*
  introspeksiyon araçları kullanılamaz. Akış durmaz.

---

## P1 — `rstudio-r` (önerilen, yerel)

- **Amaç.** D katmanı otomasyonu: `r_test_package` (testthat), `r_check_package` (R CMD check),
  `r_document_package` (roxygen2), `r_execute` ve ek araçlar (`r_test_file`, `r_build_package`,
  `r_load_all`, `r_install_package`, `r_list_packages`, `r_workspace_ls`).
- **Taşıma.** stdio (`node ${RSTUDIO_MCP_PATH}/build/index.js`).
- **Ön koşul.** Node 18+, R 3.6+ (`Rscript` PATH'te), R paketleri `devtools`/`testthat`/`roxygen2`.
  Repoyu klonlayıp derlemeniz ve `RSTUDIO_MCP_PATH` ayarlamanız gerekir.
- **Kurulum.**
  ```bash
  git clone https://github.com/lerlerchan/rstudio-mcp-server
  cd rstudio-mcp-server
  npm run setup          # ya da: npm install && npm run build
  export RSTUDIO_MCP_PATH="$PWD"   # build/index.js'in bulunduğu kök
  ```
  Sonra Claude Code'u bu env ile başlatın; `.mcp.json` `${RSTUDIO_MCP_PATH}/build/index.js`'i sürer.
- **Güvenlik.** Yerel; ağ çıkışı yok. Yerel R/araç komutları çalıştırır.
- **Doğrulama notu.** Tool adları + `build/index.js` giriş noktası + `npm run setup` build adımı
  `lerlerchan/rstudio-mcp-server` kaynağından doğrulandı. `setup` script'inin tam içeriği
  doğrulanmadı (TODO: `package.json`'ı kontrol edin) — bu yüzden hem `npm run setup` hem manuel
  `npm install && npm run build` belgelendi.
- **Yoksa ne olur (`${RSTUDIO_MCP_PATH}` ayarlı değilse).** Bu sunucu sessizce başlamayabilir;
  **plugin yine yüklenir** (zarif düşüş). D katmanı `Rscript -e 'testthat::test_dir(...)'` +
  `covr` yoluyla çalışmaya devam eder.

---

## P2 — `rmcp` (opt-in, UZAK — gizlilik riskli)

- **Amaç.** Bağımsız bir istatistiksel oracle (Python tabanlı, 52 araç, 429 CRAN paketi). F
  katmanında ikinci-yol doğrulaması için *yalnızca* sentetik/anonim veride.
- **Taşıma.** http (barındırılan) veya kendi self-host kopyanızda stdio (`rmcp start`).
- **⚠️ GÜVENLİK UYARISI.** **Gizli/Roche ham verisini barındırılan uca GÖNDERMEYİN.** Yalnız
  sentetik/anonimleştirilmiş veride veya kendi self-host kopyanızda kullanın. Bu yüzden
  `.mcp.json`'da **bağlı değildir**.
- **Kurulum (kullanıcı isterse, bilinçli).**
  ```bash
  # barındırılan (yalnız anonim veri):
  claude mcp add --transport http rmcp https://rmcp-server-394229601724.us-central1.run.app/mcp
  # ya da self-host: pip install rmcp && rmcp serve-http   (kendi makinenizde)
  ```
  Kaynak: `github.com/finite-sample/rmcp` (PyPI `rmcp`). URL canlılığı doğrulanmadı (TODO: probe).
- **Yoksa ne olur.** F katmanı, sizin/kullanıcının yazdığı bağımsız R yeniden-uygulaması +
  `waldo::compare()` ile tamamen çalışır; oracle opsiyoneldir.

---

## P3 — Akademik MCP'ler (fırsatçı, halihazırda bağlı)

- **Amaç.** Bir bulguyu literatürle gerekçelendirmek/birincil-kaynak doğrulamak (örn. bir
  varsayım-ihlali için uygun yöntem önerisini kaynakla desteklemek).
- **Kapsam.** Kullanıcının ortamında **zaten bağlı** olabilen Consensus, Elicit, Scholar Gateway,
  Paper Search gibi MCP'ler.
- **Bağlama.** replicatio bunları `.mcp.json` ile **bağlamaz** (tekrar bağlamak çakışma yaratır).
  Skiller bunları *varsa* fırsatçı kullanır.
- **Yoksa ne olur.** Zarifçe devam edilir; literatür-gerekçesi adımı atlanır, denetim etkilenmez.

---

## Sağlık kontrolü (preflight)

`start` skill Adım 2'yi izleyin:
```bash
Rscript --version
Rscript -e 'cat(all(c("pointblank","performance","statcheck","scrutiny","renv","waldo","jsonlite") %in% rownames(installed.packages())))'
```
`FALSE` → `Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.R"` (opsiyonel `--renv`).
