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

## Motor seçimi — ÖLÇÜLDÜ (2026-07-17)

Uzman ground-truth'a karşı kıyaslandı: **OpenITI MAKHZAN** (Zenodo `10.5281/zenodo.19861912`),
elle ALTO satır transkripsiyonu taşıyan **6 Osmanlıca rik'a/divanî yazma sayfası**. Normalize CER,
aynı Katman-0 girdisi:

| Motor | CER (ort.) | rik'a sayfası | Not |
| --- | ---: | ---: | --- |
| **Transleyt** | **0.230** | **0.130** | **Osmanlı VARSAYILANI** — en iyi otomatik okuyucu |
| **Asistan görüsü** | — | **0.154** | Transleyt'e **denk** (satır 4–18); bağımsız ikinci okuyucu |
| eScriptorium | 0.479 | 0.255 | bedava/self-host → **keşif taraması** için |
| Transkribus 429513 | 0.782 | 0.663 | katalogdaki tek Arap-harfli TK modeli — **kullanılamaz** |
| tesseract | — | — | Osmanlıca gövdeye katkısı **sıfır**; yalnız basılı damga + referans kodu |

**Osmanlı varsayılanı artık `transleyt`** (eski varsayılan `both` ölçümden önceki bir tahmindi;
gerekçesi de tutmuyordu — `both` zaten Transkribus'u çağırıyor, o da kredi ölçümlü, yani sayfa
başına ~1 kredi harcanıyordu. Takas maliyeti değiştirmiyor, doğruluğu ~2 katına çıkarıyor).
`engine=` parametresi her zaman geçersiz kılar; `DEVARSIV_OTTOMAN_ENGINE` ile pinlenebilir.

**Kredi kuralı (değişmedi, sadece motoru değişti):** keşif/tarama taramasında
`engine="escriptorium"` (bedava, self-host) veya `engine="tesseract"`; **değerli sayfada**
varsayılan `transleyt`.

**En doğru okuma = Transleyt + asistan görüsü.** İkisi **karşılaştırılabilir** (%13 vs %15) ve
**bağımsız** — iki çıktıyı uzlaştırmak her ikisinden de iyidir. Zayıf motorları (ES %48,
TK-429513 %78) oya katmak doğruluğu **düşürür**; tesseract Osmanlıca gövdede oy veremez.
Transleyt güven skoru döndürmez (`mean_confidence: null`) → ağırlıklı birleştirme mümkün değil;
uzlaştırma asistanın görüyle yaptığı iştir. **MCP tek-birleşik-metin ÜRETMEZ.**

Transleyt kimlik/kredi yoksa dürüstçe `unavailable` döner (uydurma yok). Boş kâğıt testinde
metin üretmediği (dürüst degrade) ve iki koşumda **birebir aynı** çıktı verdiği (deterministik,
konfabüle etmiyor) ölçüldü — ama **%13–23 hata payı**, isim/tarih/yer/meblağ hatası demektir;
transkripsiyon insan doğrulamasına tabidir.

## K3 — Transkribus model seçim tablosu

| Belge türü | Model | Alfabe | CER | Not |
| --- | --- | --- | --- | --- |
| El yazması genel (divani/rika) | **56496** OttomanTurkish_generic | **Latin çeviriyazı** | ~%12 | Üretimdeki varsayılan (`DEVARSIV_TRANSKRIBUS_HTR_ID`) |
| Fetva / ilmiye el yazması | **169801** Ottoman Fatwa Manuscript | **Latin çeviriyazı** | %5.94 | Fetva/kadı-sicili tipi eller |
| El yazması — Arap-harfli çıktı | **429513** | **Arap harfli** | %9.36 | Katalogdaki TEK Arap-harfli Osmanlıca model; yalnız 1.054 satır eğitim |
| Matbu (salname/gazete/nizamname) | **52502** OttomanTurkish_Print_1 | **Latin çeviriyazı** | %7.2 | TTK "yarım-transkripsiyon" latinizasyon şeması |
| Matbu — daha geniş veri | **57485** OttomanTurkish_Print_v2 | Latin (ölçülmedi; 52502 soylu) | %7.6 | 52502 verisi + ek veri, 37.866 satır |

Alfabe sütunu 2026-07-16'da canlı ölçüldü (429513 arap=69/latin=0; 56496 ve 169801 arap=0);
52502 kendi belgesinde latinizasyon şemasını beyan eder. 57485 ölçülmedi — dürüstçe işaretli.

**⚠ Alfabe uyarısı.** TK'nin Osmanlıca modelleri Arap-harfli görüntüyü okur ama **Latin
çeviriyazı yazar**; eScriptorium/OpenITI **Arap harfli** yazar. İki çıktı bu yüzden
**karşılaştırılamaz**: `arbitrate=true` hakemliğinde ayrı alfabelerde aday üretirler →
`agreement_rate` tanım gereği 0 çıkar (bug değil, dürüst sinyal). İki motoru aynı alfabede
toplamak tek seçenekle mümkün: **429513**. Detay: references/htr-workflow.md.

Model değişimi deploy-notu: HP `~/devarsiv-mcp/runtime.env` → `DEVARSIV_TRANSKRIBUS_HTR_ID=<id>` +
`systemctl restart devarsiv-mcp`.

## Katman 3 — kanıt-temelli satır hakemliği (`arbitrate=true`) — **yalnız MATBU sayfada**

**Kapsam (2026-07-16 ölçümüyle daraltıldı).** Hakemlik yalnız **matbu** Osmanlıca sayfalarda
(salname/gazete/nizamname) anlam taşır. **El yazması BOA belgesinde `arbitrate=true` KULLANMA** —
orada `agreement_rate` düşük değil, **daima 0.0**'dır ve hakemlik hiçbir şey katmaz. İki bağımsız
ölçülmüş neden: (1) iki motor **ayrı alfabelerde** yazar (TK → Latin çeviriyazı, ES → Arap harfli;
yukarıdaki alfabe uyarısı) → metin uzlaşması tanım gereği imkânsız; (2) eScriptorium **diyagonal
kançılarya düzeninde** tam satır bulamaz, parça bulur (ölçüm: 4 koşulun hiçbirinde tam-genişlik
satır yok; TK 4 tam satır buluyor). *Düzeltme (2026-07-17): bu, "ES el yazmasında satır bulamaz"
demek DEĞİL — MAKHZAN ölçümü ES'in **kitap yazmalarını** 6'da 4 isabetle segmentlediğini gösterdi
(17/18, 17/17, 17/17, 17/16). Sorun el yazısı değil, **diyagonal layout**.* El yazmasında geçerli
yol: **Transleyt (%13–23) + asistan görüsü (%15) uzlaştırması** — ikisi denk ve bağımsız.

`engine="both"` + `arbitrate=true` (OCR araçlarında opsiyonel bayrak) çıktıya bir `arbitration`
zarfı ekler: motor satırları koordinatla (dikey bbox örtüşmesi) hizalanır, her satır uzlaşma
durumuna göre sınıflanır (`IDENTICAL`/`MINOR`/`CONFLICT`/`SINGLE`), ve **çelişki satırlarının
kırpılmış görüntüsü** (`crop_image`, gerçek PNG) motor adaylarıyla (`candidates: {motor: metin}`)
birlikte sunulur. Transleyt tam-metni `block_reference` olarak eklenir (koordinatsız).

**Asistan rolü = hakem.** Sadece `CONFLICT`/`SINGLE` satırların `crop_image`'ını görüyle oku,
adaylarla karşılaştır, **en olası okumayı seç**; hiçbir aday doğru değilse görüden oku. Uzlaşan
(`IDENTICAL`/`MINOR`) satırlar zaten kırpılmaz — onlara güven. **MCP tek-birleşik-metin ÜRETMEZ**
(adaylar ayrı; birleştirme asistanın insan-denetimli işidir). Matbu sayfada `agreement_rate`
düşükse (zor baskı/soluk mürekkep) bu normaldir — hakemlik tam da bunun için; ama **0.0 görüyorsan
belge muhtemelen el yazmasıdır → yukarıdaki kapsam notu, hakemliği bırak, görüyle oku.** Degrade dürüst
(`degrade[]`; opencv yoksa `crop_image` yok, metin-only; <2 koordinatlı motor →
`insufficient_engines`). Durum: `devarsiv_server_info` → `ocr.arbitration`.

Çıktı: HTR/transkripsiyon ham metni (üç-sütun) + insan-revizyon önerileri + paleografik notlar.
**Tarama gerçektir, transkripsiyon uydurulmaz**; HTR/OCR hata payını ve düşük-güveni açıkça
belirt; transkripsiyon insan doğrulamasına tabi. Detaylı prosedür için references/htr-workflow.md
yükle.
