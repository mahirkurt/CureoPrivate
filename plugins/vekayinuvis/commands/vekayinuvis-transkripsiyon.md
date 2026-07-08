---
description: Osmanlıca yazma/baskı bir sayfayı eScriptorium HTR pipeline ile dijitalleştirir (MANUSCRIPT_TRANSCRIBE modu).
argument-hint: <IIIF manifest URL veya yüklenen görüntü>
---

`vekayinuvis` skill'ini **MANUSCRIPT_TRANSCRIBE** modunda çalıştır.

Girdi: "$ARGUMENTS" — IIIF manifest URL'i, kullanıcının yüklediği görüntü, **veya bir
resmî katalog belgesi** (`devarsiv_search` → `item_id`/`hash`).

Kaynak → yöntem:
- **Resmî katalog belgesi:** `devarsiv_get_belge_image(item_id, hash, arsiv)` ile sayfa
  taramasını çek → **Osmanlı el yazması için taramayı DOĞRUDAN görünle transkribe et**
  (pratikteki en iyi yol) veya `devarsiv_ocr_belge` (Transkribus HTR creds'liyse deterministik;
  Latin belgede tam-metin). Bkz. references/devlet-arsivleri-katalog.md §7.
- **IIIF/yüklenen görüntü:** ottoman-archives eScriptorium pipeline (CONNECTORS.md E katmanı):
  list_models → create_document → import_iiif → segment → transcribe → get_transcription.

Çıktı: HTR/transkripsiyon ham metni + insan-revizyon önerileri + paleografik notlar. **Tarama
gerçektir, transkripsiyon uydurulmaz**; HTR/OCR hata payını ve düşük-güveni açıkça belirt;
transkripsiyon insan doğrulamasına tabi. Detaylı prosedür için references/htr-workflow.md yükle.
