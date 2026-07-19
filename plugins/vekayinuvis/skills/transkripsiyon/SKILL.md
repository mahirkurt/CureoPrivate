---
name: transkripsiyon
description: Osmanlıca yazma/baskı bir sayfayı Transleyt + asistan görüsü uzlaştırmasıyla dijitalleştirir (ölçülen en doğru yol; MANUSCRIPT_TRANSCRIBE modu).
---

`vekayinuvis` skill'ini **MANUSCRIPT_TRANSCRIBE** modunda çalıştır.

Girdi: kullanıcının belirttiği IIIF manifest URL'i, yüklediği görüntü, veya bir resmî katalog
belgesi (`devarsiv_search` → `item_id`/`hash`). **Üç girdi tipi** ve her biri için yöntem:

1. **Katalog önizlemesi (satın-alınmamış belge):** `devarsiv_get_belge_image(item_id, hash, arsiv)`
   — sample_picture'ı önizleme taraması olarak çeker; satın-alma durumundan bağımsız, ama yalnız
   **1 temsilî sayfa**. Deterministik metin katmanı için `devarsiv_ocr_belge(item_id, hash, arsiv,
   lang?, engine?)`: **Latin/Cumhuriyet belgeler (arsiv 1/3/4)** → tam-metin OCR (varsayılan
   `engine="tesseract"`; `mean_confidence` raporlanır; basılı damga + arşiv referans kodu da bu
   katmanla doğrulanır); **Osmanlı** → aşağıdaki iki-okuyucu uzlaştırma (varsayılan
   `engine="transleyt"`). Bkz. ${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/devlet-arsivleri-katalog.md §7 (motor tablosu ve engine
   parametresi). Çok-sayfa gerekiyorsa önce `/vekayinuvis:satinalma` akışı başlatılır.
2. **Satın-alınmış belge (yerel arşiv):** `devarsiv_get_archive_page(code, page)` — 300 DPI
   ImageContent. Osmanlı el yazmasında bu sayfa görüntüsü **asistan görüsünün** okuduğu şeydir
   (iki-okuyucu uzlaştırmasının bir yarısı).
   Belge satın alınmışsa okuma DAİMA yerel arşivden başlar: devarsiv_list_archive → devarsiv_get_archive_page (300 DPI + görü); katalog önizlemesi (sample) yalnız satın-alınmamış belgeler içindir.
   Çok-sayfa toplu iş → `/vekayinuvis:toplu-okuma` (K4 sync/async kararı).
3. **Harici görüntü (IIIF vb.):** `devarsiv_ocr_image(image_url, engine?, lang?)` — BOA dışı
   yazmalar için (ottoman-archives'in keşfettiği IIIF görüntüleri gibi). BOA belgeleriyle **aynı
   motor beynine** gider (6 motor + Katman 0), Osmanlı varsayılanı `transleyt`. Güvenlik:
   `image_url` yalnız `DEVARSIV_OCR_IMAGE_HOSTS` allowlist'indeki https host'lardan getirilir
   (boş = kapalı); asla uydurma metin. ottoman-archives'in eScriptorium pipeline'ı **matbu korpus**
   içindir, el yazması transkripsiyon motoru değildir.

## Katman 0 — görüntü kalitesi (otomatik)

Motorlara giden her sayfa **arşiv çözünürlüğünde (300 DPI)** raster'lanır ve deterministik bir
OpenCV ön-işlemeden (deskew + CLAHE kontrast + denoise) geçer — kredi harcamaz, her motoru birden
yükseltir. Asistan-görü okuyucusu **ham 300 DPI** alır (VLM ham yüksek-çözünürlüğü en iyi okur;
ölçüm: belirleyici değişken çözünürlüktür — 4836px sayfada görü çok güçlü, ~1000px'te neredeyse
sıfır). Uygulanan filtreler her OCR çıktısının `preprocess` alanında raporlanır; opencv yoksa
dürüst passthrough (ham görüntü, uydurma yok). Durum: `devarsiv_server_info` → `ocr.preprocess`.

## İki-okuyucu uzlaştırma (KANONİK MOTOR DOKTRİNİ)

Osmanlı el yazması sayfalarda varsayılan `engine="transleyt"`. En doğru okuma **iki bağımsız
okuyucunun uzlaştırılmasıdır**:

| Okuyucu | CER (rik'a) | Rol |
| --- | ---: | --- |
| **Transleyt** | **0.130** | Varsayılan; MCP `text` olarak döndürür |
| **Asistan görüsü** | **0.154** | DENK ve bağımsız ikinci okuyucu; asistan sayfa görüntüsünü kendi okur |

İkisi **denktir** — hiçbiri "çelişkide otomatik kazanmaz". Uzlaştırma asistanın işidir ve iki
okumadan da iyidir çünkü kıyaslanabilir + bağımsızdırlar. **Ölçüldü (6 MAKHZAN sayfası):**
Transleyt tek başına 0.231, görü tek başına 0.229, uzlaştırma **0.162** — %30 göreli iyileşme,
**sıfır yeni makineyle** (MCP zaten Transleyt döndürüyor, asistan zaten sayfayı okuyor).

Uzlaştırma **sağlam**: bir okuyucu çökse bile (ör. düşük çözünürlüklü sayfada görü) diğeri
korunur — 6 sayfanın 5'inde uzlaştırma ≥ iyi okuyucu. Ayrıldıklarında sayfaya bakıp **kanıtla**
karar ver; emin olamadığında Transleyt'i koru (o taban). Transleyt güven skoru döndürmez
(`mean_confidence: null`) → ağırlıklı birleştirme kapalı, uzlaştırma görüyle yapılır.

**Zayıf motorları oya KATMA** — doğruluğu düşürür: eScriptorium 0.479, Transkribus-429513 0.782,
tesseract Osmanlıca gövdede sıfır. **MCP tek-birleşik-metin ÜRETMEZ** (adaylar ayrı döner).

**Kredi kuralı:** keşif/tarama taramasında `engine="escriptorium"` (bedava, self-host); **değerli
sayfada** varsayılan `transleyt`. `engine=` her zaman geçersiz kılar; `DEVARSIV_OTTOMAN_ENGINE`
ile pinlenebilir.

## Motor seçimi — ÖLÇÜLDÜ (2026-07-17)

Uzman ground-truth'a karşı kıyaslandı: **OpenITI MAKHZAN** (Zenodo `10.5281/zenodo.19861912`),
elle ALTO satır transkripsiyonu taşıyan **6 Osmanlıca rik'a/divanî yazma sayfası**. Normalize CER,
aynı Katman-0 girdisi:

| Motor | CER (ort.) | rik'a sayfası | Not |
| --- | ---: | ---: | --- |
| **Transleyt** | **0.230** | **0.130** | **Osmanlı VARSAYILANI** — en iyi otomatik okuyucu |
| **Asistan görüsü** | 0.229 | **0.154** | Transleyt'e **denk**; bağımsız ikinci okuyucu |
| eScriptorium | 0.479 | 0.255 | bedava/self-host → **keşif taraması** için |
| Transkribus 429513 | 0.782 | 0.663 | katalogdaki tek Arap-harfli TK modeli — **kullanılamaz** |
| tesseract | — | — | Osmanlıca gövdeye katkısı **sıfır**; yalnız basılı damga + referans kodu |

Transleyt kimlik/kredi yoksa dürüstçe `unavailable` döner (uydurma yok). Boş kâğıt testinde
metin üretmediği (dürüst degrade) ve iki koşumda **birebir aynı** çıktı verdiği (deterministik,
konfabüle etmiyor) ölçüldü — ama **%13–23 hata payı**, özel ad/tarih/yer/meblağda hata beklenir
demektir. Bu hata payı çıktının kendi güvenilirliğidir ve atıf yapılırken bilinir; boru hattı
zorunlu bir insan adımı beklemez (ama birincil-kaynak yorumu her hâlde araştırmacıya aittir).

## Transkribus model tablosu (neden TK bir transkripsiyon rakibi DEĞİL)

TK'nin Osmanlıca modelleri Arap-harfli görüntüyü okur ama **Latin çeviriyazı yazar** — asistan
Arap-harfli okumadan zaten çeviriyazı üretebildiği için TK ayrı bir çıktıdır, iki-okuyucu
uzlaştırmasının rakibi değildir. Katalogdaki tek Arap-harfli model (429513) CER 0.782 ile
kullanılamaz.

| Belge türü | Model | Alfabe | CER | Not |
| --- | --- | --- | --- | --- |
| El yazması genel (divani/rika) | **56496** OttomanTurkish_generic | **Latin çeviriyazı** | ~%12 | `DEVARSIV_TRANSKRIBUS_HTR_ID` varsayılanı |
| Fetva / ilmiye el yazması | **169801** Ottoman Fatwa Manuscript | **Latin çeviriyazı** | %5.94 | Fetva/kadı-sicili tipi eller |
| El yazması — Arap-harfli çıktı | **429513** | **Arap harfli** | %9.36* | Katalogdaki TEK Arap-harfli; yalnız 1.054 satır eğitim (*MAKHZAN'da 0.782) |
| Matbu (salname/gazete/nizamname) | **52502** OttomanTurkish_Print_1 | **Latin çeviriyazı** | %7.2 | TTK "yarım-transkripsiyon" latinizasyon şeması |
| Matbu — daha geniş veri | **57485** OttomanTurkish_Print_v2 | Latin (ölçülmedi; 52502 soylu) | %7.6 | 52502 verisi + ek veri, 37.866 satır |

Alfabe sütunu 2026-07-16'da canlı ölçüldü (429513 arap=69/latin=0; 56496 ve 169801 arap=0);
52502 kendi belgesinde latinizasyon şemasını beyan eder. 57485 ölçülmedi — dürüstçe işaretli.

Model değişimi deploy-notu: HP `~/devarsiv-mcp/runtime.env` → `DEVARSIV_TRANSKRIBUS_HTR_ID=<id>` +
`systemctl restart devarsiv-mcp`.

> **Katman 3 (satır hakemliği) EMEKLİYE AYRILDI (2026-07-17).** Öncülü iki kez ölçümle çürütüldü:
> (1) hizaladığı iki motor farklı alfabede yazıyordu (TK Latin, ES Arap) → `agreement_rate`
> daima 0; (2) yeniden amaçlanan satır-kırpımı yolu tam-sayfa okumadan **+0.038 CER kötü** çıktı.
> `arbitrate` parametresi artık yok. En doğru okuma yukarıdaki iki-okuyucu uzlaştırmasıdır ve
> yeni makine istemez.

## Çıktı

HTR/transkripsiyon ham metni (Transleyt + asistan görüsü, **ayrı** raporlanır — tek birleşik
metin YASAK) + paleografik notlar. **Tarama gerçektir, transkripsiyon uydurulmaz**; hata payını
(%13–23) ve düşük-güveni açıkça belirt. Detaylı prosedür için ${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/htr-workflow.md yükle.
