---
name: rapor
description: Bir konuda tam-uzunlukta, atıflı, 10-bölümlü akademik tarih raporu üretir (ACADEMIC_REPORT modu).
disable-model-invocation: true
---

`vekayinuvis` skill'ini **ACADEMIC_REPORT** modunda çalıştır.

Hedef: kullanıcının belirttiği konu (+ opsiyonel dönem/coğrafya) üzerine § 7'deki 10-bölümlü
resmî akademik tarih raporu şablonuna uygun, tam-uzunlukta atıflı belge. Tüm connector
katmanlarını birleştir; G0–G6 kalite kapılarından geçir (kapsam, kaynak çeşitliliği,
triangülasyon, tarih disiplini, çeviriyazı tutarlılığı, atıf bütünlüğü, dürüst
belirsizlik).

${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/citation-and-transliteration.md ve ${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/report-template.md
yükle. Çıktı carbon-html-report (A4 print, sunum-hazır) veya carbon-quarto-scientific
(Quarto/R bilimsel format) ile downstream işlenebilir.

**Geniş tarama `arsiv-tarama-distilleri` alt-ajanına DELEGE EDİLİR.** Bu mod tüm katmanların
(devlet-arsivleri + ottoman-archives + yoktez + literatur + akademik companion + tam-metin
şelalesi) birleşimini gerektirdiğinden ham çok-connector çıktısını Task/Agent aracıyla bu ajana
devret: çıktı ajanın kendi penceresinde tüketilir, ana pencereye yalnız kompakt `arsiv_distillate`
+ `coverage` döner. Bu delegasyon **Claude Code'da** mevcuttur; **claude.ai'de plugin alt-ajanı
yoksa** doğrudan Tier-2 anamnesis'e ingest→bounded query ile daralt
(bkz. ${CLAUDE_PLUGIN_ROOT}/shared/context-economy-contract.md).
