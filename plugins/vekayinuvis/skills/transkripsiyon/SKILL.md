---
name: transkripsiyon
description: Osmanlıca yazma/baskı bir sayfayı görü + Transkribus + eScriptorium üç-sütun protokolüyle dijitalleştirir (MANUSCRIPT_TRANSCRIBE modu).
---

`vekayinuvis` skill'ini **MANUSCRIPT_TRANSCRIBE** modunda çalıştır.

Girdi: kullanıcının belirttiği IIIF manifest URL'i, yüklediği görüntü, veya bir resmî katalog
belgesi (`devarsiv_search` → `item_id`/`hash`). **Üç girdi tipi** ve her biri için yöntem:

1. **Katalog önizlemesi (satın-alınmamış belge):** `devarsiv_get_belge_image(item_id, hash, arsiv)`
   — sample_picture'ı önizleme taraması olarak çeker; satın-alma durumundan bağımsız, ama yalnız
   **1 temsilî sayfa**. Deterministik metin katmanı için `devarsiv_ocr_belge(item_id, hash, arsiv,
   lang?, engine?)`: **Latin/Cumhuriyet belgeler (arsiv 1/3/4)** → tam-metin OCR (varsayılan
   `engine="tesseract"`; `mean_confidence` raporlanır; basılı damga + arşiv referans kodu da bu
   katmanla doğrulanır); **Osmanlı** → aşağıdaki üç-sütun protokol (varsayılan `engine="both"`).
   Bkz. references/devlet-arsivleri-katalog.md §7 (motor tablosu ve engine parametresi). Çok-sayfa
   gerekiyorsa önce `/vekayinuvis:satinalma` akışı başlatılır.
2. **Satın-alınmış belge (yerel arşiv):** `devarsiv_get_archive_page(code, page)` — 300 DPI
   ImageContent, **birincil okuma** kalitesi.
   Belge satın alınmışsa okuma DAİMA yerel arşivden başlar: devarsiv_list_archive → devarsiv_get_archive_page (300 DPI + görü); katalog önizlemesi (sample) yalnız satın-alınmamış belgeler içindir.
   Çok-sayfa toplu iş → `/vekayinuvis:toplu-okuma` (K4 sync/async kararı).
3. **Harici görüntü:** IIIF manifest URL'i veya kullanıcının doğrudan yüklediği görüntü —
   ottoman-archives eScriptorium pipeline (CONNECTORS.md E katmanı): list_models →
   create_document → import_iiif → segment → transcribe → get_transcription.

## Katman 0 — görüntü kalitesi (otomatik)

Motorlara giden her sayfa artık **arşiv çözünürlüğünde (300 DPI)** raster'lanır ve deterministik
bir OpenCV ön-işlemeden (deskew + CLAHE kontrast + denoise) geçer — kredi harcamaz, dört motoru
birden yükseltir. Asistan-görü sütunu **ham 300 DPI** alır (VLM ham yüksek-çözünürlüğü en iyi
okur). Uygulanan filtreler her OCR çıktısının `preprocess` alanında raporlanır; opencv yoksa
dürüst passthrough (ham görüntü, uydurma yok). Durum: `devarsiv_server_info` → `ocr.preprocess`.

## Üç-sütun protokol

Osmanlı el yazması sayfalarda varsayılan `engine="both"`:
Sütun 1 Görü (birincil — çelişkide kazanır) | Sütun 2 Transkribus | Sütun 3 eScriptorium; gürültülü HTR sütunu "kullanılmadı (gürültülü)" olarak işaretlenir, boş bırakılmaz.
Düşen motor dürüst `unavailable` nedeni taşır; çıktı her hâlde **insan doğrulamasına** tabidir.

**Kredi kuralı:** `both` yalnız görünün değerli bulduğu sayfada çağrılır; keşif taramasında
`engine=tesseract` veya `escriptorium` kullanılır (Transkribus kredi tüketimini gereksiz
sayfalarda harcamamak için).

**4. motor — Transleyt (`engine="transleyt"`):** transleyt.com AI/LLM tabanlı Osmanlıca+Arapça
OCR; Transkribus'a bir alternatif/çapraz-kontrol katmanı. **Kredi ölçümlü** (~1 kredi/sayfa) →
aynı kredi disiplini: yalnız görünün değerli bulduğu sayfada, keşif taramasında değil. Osmanlı
varsayılanı `both` (Transkribus+eScriptorium) **değişmez** — Transleyt opt-in'dir. Çıktısı da
insan doğrulamasına tabidir; taşra-kâtibi/gürültülü ellerde Transkribus veya görü ile
çapraz-kontrol önerilir. Kimlik/kredi yoksa dürüstçe `unavailable` döner (uydurma yok).

## K3 — Transkribus model seçim tablosu

| Belge türü | Model | CER | Not |
| --- | --- | --- | --- |
| El yazması genel (divani/rika) | **56496** OttomanTurkish_generic | ~%12 | Üretimdeki varsayılan (`DEVARSIV_TRANSKRIBUS_HTR_ID`) |
| Fetva / ilmiye el yazması | **169801** Ottoman Fatwa Manuscript | %5.94 | Fetva/kadı-sicili tipi eller için alternatif |
| Matbu (salname/gazete/nizamname) | **52502** OttomanTurkish_Print_1 | %7.2 | Matbu Osmanlıca; eScriptorium OpenITI print ile çapraz-kontrol |

Model değişimi deploy-notu: HP `~/devarsiv-mcp/runtime.env` → `DEVARSIV_TRANSKRIBUS_HTR_ID=<id>` +
`systemctl restart devarsiv-mcp`.

Çıktı: HTR/transkripsiyon ham metni (üç-sütun) + insan-revizyon önerileri + paleografik notlar.
**Tarama gerçektir, transkripsiyon uydurulmaz**; HTR/OCR hata payını ve düşük-güveni açıkça
belirt; transkripsiyon insan doğrulamasına tabi. Detaylı prosedür için references/htr-workflow.md
yükle.
