---
description: Osmanlıca yazma/baskı bir sayfayı eScriptorium HTR pipeline ile dijitalleştirir (MANUSCRIPT_TRANSCRIBE modu).
argument-hint: <IIIF manifest URL veya yüklenen görüntü>
---

`vekayinuvis` skill'ini **MANUSCRIPT_TRANSCRIBE** modunda çalıştır.

Girdi: "$ARGUMENTS" (IIIF manifest URL'i veya kullanıcının yüklediği görüntü).
ottoman-archives eScriptorium pipeline'ını (CONNECTORS.md E katmanı) uygula:
list_models → create_document → import_iiif → segment → transcribe →
get_transcription.

Çıktı: HTR ham metni + insan-revizyon önerileri + paleografik notlar. HTR hata
payı tahminini açıkça belirt. Detaylı prosedür için references/htr-workflow.md
yükle.
