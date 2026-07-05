---
description: Toplanan bulgu JSON'larından konsolide IBM Carbon v11 + IBM Plex tek-dosya HTML rapor üretir (özet tablo + katman bölümleri + severity rozetleri + provenance). Argüman = bulgular dizini.
argument-hint: "[bulgular-dizini] (varsayılan: ./.replicatio/findings)"
allowed-tools: Bash, Read
---

# /replicatio:audit-report — Konsolide Carbon HTML Rapor

Bulgular dizini: **$ARGUMENTS** (boşsa `./.replicatio/findings`).

Daha önce çalıştırılan denetim katmanlarının (`00`–`04`) ürettiği `*.json` bulgularını tek bir
self-contained HTML rapora dönüştürün. **No-fabrication:** rapor yalnız mevcut bulgu dosyalarını
yansıtır; eksik katman "girdi yok" olarak görünür.

## Yürütme

1. Bulgular dizinini belirleyin: `FIND="${ARGUMENTS:-$PWD/.replicatio/findings}"`. Boşsa, önce bir
   denetim komutu (`/replicatio:audit-data` vb.) çalıştırılması gerektiğini söyleyin.
2. Üretin:
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/lib/report.R" --out "$FIND" --html "$FIND/replicatio-report.html"
   ```
3. Rapor yolunu ve betiğin bastığı şiddet sayımlarını kullanıcıya verin. Gerekirse `Read` ile
   bulgu JSON'larını okuyup kısa bir metin özeti de ekleyin.

## Çıktı sözleşmesi
Son satır: `STATUS=<OK|FAIL>  REPORT=<html-yolu>`
(`FAIL` = jsonlite yok / hiç bulgu dosyası yok / render hatası.)
