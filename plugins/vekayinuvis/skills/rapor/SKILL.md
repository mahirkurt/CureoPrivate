---
name: rapor
description: Bir konuda tam-uzunlukta, atıflı, 10-bölümlü akademik tarih raporu üretir (ACADEMIC_REPORT modu).
disable-model-invocation: true
context: fork
---

`vekayinuvis` skill'ini **ACADEMIC_REPORT** modunda çalıştır.

Hedef: kullanıcının belirttiği konu (+ opsiyonel dönem/coğrafya) üzerine § 7'deki 10-bölümlü
resmî akademik tarih raporu şablonuna uygun, tam-uzunlukta atıflı belge. Tüm connector
katmanlarını birleştir; G0–G6 kalite kapılarından geçir (kapsam, kaynak çeşitliliği,
triangülasyon, tarih disiplini, çeviriyazı tutarlılığı, atıf bütünlüğü, dürüst
belirsizlik).

${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/citation-and-transliteration.md ve ${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/report-template.md
yükle. Çıktı carbon-html-report (A4 print) veya carbon-pptx ile downstream
işlenebilir.

**Geniş tarama, `arsiv-tarama-distilleri` alt-ajanına devredilir.** Bu skill tüm katmanların
(devlet-arsivleri + ottoman-archives + yoktez + literatur + akademik companion + tam-metin
şelalesi) birleşimini gerektirdiğinden `context: fork` ile çalışır: ham çok-connector çıktısı
ajanın kendi penceresinde tüketilir; ana pencereye yalnız kompakt `arsiv_distillate` + `coverage`
döner (bkz. ${CLAUDE_PLUGIN_ROOT}/shared/context-economy-contract.md).
