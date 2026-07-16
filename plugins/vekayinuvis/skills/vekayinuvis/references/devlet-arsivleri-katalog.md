# Referans: Devlet Arşivleri Resmî Katalog Akışı (`devlet-arsivleri` connector)

> **Ne zaman yüklenir:** `ARCHIVE_DEEP_DIVE`, `SOURCE_HUNT`, `PROSOPOGRAPHY`,
> `KANUN_GEREKÇESİ` ve `ACADEMIC_REPORT` modlarında BOA/BCA/Diplomatik/Askeri
> resmî katalog kaydı gerektiğinde. Bu dosya, `katalog.devletarsivleri.gov.tr`
> resmî kataloğunu saran `devlet-arsivleri` MCP'sinin sorgu stratejisini,
> no-fabrication zincirini ve atıf disiplinini tanımlar.

Bu connector, `archive-landscape.md` §1.1/§1.2/§8.1/§8.4'te tarihsel olarak
"BETSİS sorgu önerisi / BCA için kayıt yok" biçiminde **kodlanmış boşluğu**
kapatır: resmî katalog araması artık **doğrudan canlı** yapılır.

---

## 1. Dört arşiv (arsiv kodu)

| Kod | Arşiv | Tipik fonlar |
|---|---|---|
| `1` | Cumhuriyet Arşivi (**BCA**) | 030.10, 030.18, 490.1, 180.9, 051.*, 272.* |
| `2` | Osmanlı Arşivi (**BOA**) | HAT, İ.*, Y.*, DH.*, A.MKT.*, MV, ML.*, EV.*, ŞD, BEO, MD/MHM, C.* |
| `3` | Dışişleri Türk Diplomatik Arşivi | — |
| `4` | Milli Savunma Askeri Tarih Arşivi (**ATASE**) | — |

`devarsiv_search(arsiv=...)` filtresi ad ("Osmanlı") veya kod ("2") kabul eder.

---

## 2. Araçlar ve akış (22 araç, 6 grup — K1)

Devarsiv artık yalnız katalog aramasıyla sınırlı değil: eSatış sepeti
(state-changing, **ödemesiz**), satın-alınmış belgelerin **yerel arşivi**
(300 DPI + çift-motor OCR) ve bir **async OCR kuyruğu** dahil **22 araç,
6 grup**tur.

| Grup | Araç | Not |
| --- | --- | --- |
| Arama | `devarsiv_search(query, arsiv?, limit?)` | Basit Arama; `capped:true`→enumerasyon (§2b), çok geniş→`refine_required` |
| Arama | `devarsiv_semantic_search(query, arsiv?, limit?, rerank?)` | Diyakronik genişletme (karantina→tahaffuzhane) + bge-m3 rerank (§2c) |
| Arama | `devarsiv_detailed_search(arsiv, ozet?, ust_fon?, kutu?, gomlek?, sira?, tarih_turu?, yil_bas?, yil_bit?, limit?)` | OzelArama — 1000-cap altına daraltma/enumerasyon (§2b) |
| Arama | `devarsiv_list_fon_categories(arsiv)` | Üst-fon listesi (enumerasyon ekseni, §2b) |
| Arama | `devarsiv_detailed_search_fields(arsiv)` | Form-alan introspeksiyonu |
| Belge | `devarsiv_get_belge(item_id, hash, arsiv)` | Künye + **`access`** (`purchased`/`purchasable`) — hangi §8 akışına gidileceğini belirler |
| Belge | `devarsiv_get_belge_image(item_id, hash, arsiv)` | Önizleme taraması ImageContent — **görüyle okuma**, satın-alma durumundan bağımsız |
| Belge | `devarsiv_ocr_belge(item_id, hash, arsiv, lang?, engine?)` | Deterministik OCR/HTR; Osmanlı varsayılanı `engine="both"` (bkz. §7 K2) |
| Sepet | `devarsiv_add_to_cart(item_id, hash, arsiv, pages?)` `[_RW]` | 1-tabanlı cbk sayfa seçimi ("1,3-5"; boş=tümü); ödeme yapmaz |
| Sepet | `devarsiv_list_cart()` `[_RO]` | Kalemler + **bağlayıcı Tutar** |
| Sepet | `devarsiv_remove_from_cart(rows?, contains?, clear?)` `[_DESTRUCTIVE]` | Satır sil / boşalt |
| Sepet | `devarsiv_checkout_cart()` `[_RO]` | Ödeme YAPMAZ; yalnız noVNC URL + güncel sepet döner |
| Arşiv | `devarsiv_list_purchased()` | SatinAldiklarim t/hash listesi |
| Arşiv | `devarsiv_ocr_belge_pages(t, hash, arsiv?, pages?, lang?, engine?)` | Viewer üzerinden çok-sayfa OCR — **temsilî-sayfa sınırlı**; TAM/güvenilir yol yerel arşivdir (§8.2) |
| Arşiv | `devarsiv_list_archive(query?)` | BOA-kodlu yerel PDF arşivi (code/yer/tarih/özet/sayfa) |
| Arşiv | `devarsiv_get_archive_page(code, page)` | **300 DPI ImageContent — satın-alınmış belgede BİRİNCİL okuma** |
| Arşiv | `devarsiv_ocr_archive_pages(code, pages?, arsiv?, lang?, engine?)` | Sync OCR, ≤5 sayfa (MULTIPAGE_MAX_PAGES) |
| Arşiv | `devarsiv_get_archive_pdf(code, include_base64?, max_bytes?)` | Künye + sınırlı base64 PDF |
| Async | `devarsiv_ocr_submit(code, pages?, engine?, lang?, arsiv?)` `[_RW]` | İdempotent; `job_id` döner |
| Async | `devarsiv_ocr_result(job_id, include_text?)` `[_RO]` | `queued`/`running`/`done`/`error`/**`stale`** |
| Durum | `devarsiv_session_status()` | HP oturumu canlı mı (pre-flight) |
| Durum | `devarsiv_server_info()` | Araç envanteri + caveat + **`ocr.engines`** (mevcut motorlar) + **`purchase_cart.manual_checkout_url`** (noVNC) |

**Kanonik akış (tekil kayıt):** `devarsiv_session_status` → `devarsiv_search` *veya*
`devarsiv_semantic_search` (dar/diakronik sorgu) → ilgili satırın `item_id`+`hash`'i ile
`devarsiv_get_belge` → dönen `access` alanına göre **§8'deki dört akıştan biri**
(satın-alma / arşiv-okuma / üç-sütun transkripsiyon / async).

**Araç seçim rehberi:**
- Tam-eşleşen bilinen terim/fon → `devarsiv_search`.
- Modern terim / dönem-değişken sözcük / "hangi karşılıklar var" → `devarsiv_semantic_search`.
- Belirli fon+tarih+özet ile hassas daraltma → `devarsiv_detailed_search`.
- Konu >1000 kayıt (kapsamlı/tam tarama) → `devarsiv_list_fon_categories` + `devarsiv_detailed_search` (§2b).
- **Belgeyi OKUMAK** (metin/içerik): `access=purchased` → doğrudan **§8.2 arşiv-okuma akışı**
  (`devarsiv_list_archive`→`devarsiv_get_archive_page`, → `skills/arsiv-oku`); `access=purchasable`
  ve önizleme yeterliyse `devarsiv_get_belge_image`+`devarsiv_ocr_belge`; tüm sayfalar
  gerekiyorsa önce **§8.1 satın-alma akışı** (→ `skills/satinalma`) başlatılır.

---

## 2b. Kapsamlı erişim (1000-tavan aşımı — enumerasyon)

Katalog **en çok 1000 satır sayfalama olmadan** render eder; çok büyük sorgu
`refine_required` ile reddedilir. Bu yüzden **tam 1000** (`capped:true`) = *daha fazlası
var* demektir. Bir konunun **her** eşleşen belgesine ulaşmak için **üst-fon × tarih-aralığı**
ekseninde daralt ve `item_id` ile birleştir:

```
list_fon_categories(arsiv=2)                     → 49 üst-fon grubu
for fon in gruplar:
    r = detailed_search(arsiv=2, ust_fon=fon, ozet="tahaffuzhane")
    if r.capped:                                  # hâlâ >1000 → tarihe böl
        for (y0,y1) in on-yıllık pencereler:
            detailed_search(arsiv=2, ust_fon=fon, tarih_turu="miladi",
                            yil_bas=y0, yil_bit=y1, ozet="tahaffuzhane")
    union_by(item_id)                             # mükerrerleri item_id ile at
```

Bu fan-out **ağır** olduğundan ana pencerede değil, **`arsiv-tarama-distilleri`
alt-ajanında** koştur (retrieve-don't-dump); ajan yalnız birleştirilmiş, atıf-hazır
`arsiv_distillate` döndürür. `detailed_search` bir tarih aralığı verildiğinde Osmanlı
formunda `tarih_turu` gerektirir (verilmezse Miladî varsayılır).

---

## 2c. Semantik / diakronik arama (`devarsiv_semantic_search`)

Katalog anahtar-kelime eşleşir; Osmanlıca–modern **diakronik uçurum** (aynı kavramın
dönemlere göre farklı adlandırılması) recall'ı düşürür. `semantic_search` iki katman ekler:
1. **Küratörlü modern↔Osmanlıca eş-anlam sözlüğü** + Türkçe/Osmanlıca ortografik
   normalizasyon → sorgu genişletme (karantina → tahaffuzhane · sıhhiye · kordon;
   göçmen iskânı → muhacir · mülteci · sığınmacı iskânı).
2. **Gömme (embedding) yeniden sıralama** — havuzlanan sonuçlar Workers AI **bge-m3**
   (çok-dilli) ile özet-benzerliğine göre sıralanır; anahtar yoksa yalnız genişletme
   (graceful degrade).

`rerank=false` ile yalnız genişletme (daha hızlı). Genişletilen varyantlar çıktıda
`matched_variants` olarak taşınır → hangi Osmanlıca karşılığın eşleştiği şeffaf. Modern
terimli (göç, salgın, eğitim, belediye) konularda **birincil** arama aracı budur; sonuçların
en umut vericisi için yine `get_belge` ile künye çekilir (hash zinciri korunur).

---

## 3. No-fabrication invariant'ları (ZORUNLU)

- **Dar sorgu şart.** Basit arama geniş sorguyu ("İstanbul") reddeder →
  `status: refine_required`. Sorguyu daralt (spesifik terim + arşiv/fon filtresi +
  tarih); asla "sonuç yok" diye yorumlama — bu bir *daraltma* sinyalidir.
- **`hash` uydurulamaz.** `get_belge` çağrısı için `item_id` **ve** `hash`
  daima bir `devarsiv_search` sonucundan gelmelidir; hash bir per-belge sunucu
  token'ıdır, kurgulanmaz.
- **Belge görüntüsü ÇEKİLİR (uydurulmaz), OCR/görü ile okunur.** `get_belge` künye +
  erişim durumu verir; **`devarsiv_get_belge_image` sayfa taramasını (önizleme) GERÇEK
  görüntü olarak çeker** (satın-alma durumundan bağımsız) ve `devarsiv_ocr_belge` metne
  çevirir (§7). Görüntü uydurulmaz — gerçek taramadır; OCR düşük-güvende dürüstçe raporlanır.
  Çok-sayfalı **satın-alınmış** tam set artık **yerel arşivden** okunur — okuma DAİMA
  yerel arşivden başlar: `devarsiv_list_archive` → `devarsiv_get_archive_page` (300 DPI +
  görü); katalog önizlemesi (sample) yalnız satın-alınmamış belgeler içindir (§8.2, →
  `skills/arsiv-oku`). Satın-alınmamışsa tüm sayfalar için **§8.1 satın-alma akışı**
  (→ `skills/satinalma`) başlatılır. El yazması Osmanlıca deterministik OCR'ın ötesindedir
  → asistan görüsü veya Transkribus HTR (§7).
- **Oturum yoksa `session_required`.** Tek-cihaz oturum kilidi (HP'de kalıcı
  authenticated tarayıcı) düştüğünde araçlar `session_required` döner
  (portal deep-link + yankılanan sorgu). Bu durumda kullanıcıya bildir:
  *"Resmî katalog oturumu düştü; HP noVNC re-login gerekiyor"* — ve
  `ottoman-archives`/`yoktez`/`literatur` ile degrade araştırmaya devam et.
- **Katalog "Runtime Error" (HTTP 500) = büyük olasılıkla OTURUM SÜRESİ DOLDU → re-login.**
  Katalog kimlik-korumalı sayfalarda geçersiz/expired oturuma temiz login-yönlendirmesi yerine
  bir ASP.NET "Runtime Error" (500) verir; araçlar bunu `status: session_required` +
  `reason: runtime_error` ile döner. **ÇÖZÜM: HP'de noVNC re-login** (2026-07-08 doğrulandı:
  başka hesap çalışırken bizim expired oturum bu 500'ü aldı, re-login çözdü). Kullanıcıya
  re-login yol haritasını ver + bu arada ottoman/yoktez/literatur ile degrade devam et. NADİR:
  taze login DE 500 verirse gerçek bir upstream kesinti olabilir → o durumda bekle.
- **Re-login runbook (sabit — hook enjeksiyonuyla aynı metin):**
  ```text
  Oturum düştü (session_required / Runtime Error 500 ≈ expired oturum → BEKLEME değil RE-LOGIN):
  1. HP: sudo systemctl restart devarsiv-chrome
  2. HP: x11vnc -display :99 -rfbauth ~/devarsiv/vncpass -rfbport 5900 -localhost -forever -bg
         (kalıcı devarsiv-x11vnc.service zaten aktifse bu adım atlanır)
  3. noVNC: https://devarsiv-vnc.cureonics.com/vnc.html (Cloudflare Access, @cureonics.com OTP)
  4. Tarayıcıda reCAPTCHA çöz + T.C. Kimlik ile giriş (Doppler DEVLET_ARSIVLERI_*)
  5. devarsiv_session_status → alive:true doğrula
  Degrade-devam: katalog düşükken yerel arşiv (list_archive/get_archive_page) + anamnesis +
  akademik katman ÇALIŞMAYA DEVAM EDER — rapor akışını durdurma, "katalog doğrulaması bekliyor" şerhi düş.
  ```
- Her çıktı `mcp_verified: false` + `_caveat` taşır: bir kaydın bulunmaması,
  o belgenin arşivde olmadığının kesin kanıtı değildir.

---

## 4. Kronoloji köprüsü

`devarsiv_search` sonuçlarındaki tarihler **Hicrî** biçimdedir (ör. `H-27-12-1337`).
Miladî karşılık ve dönem doğrulaması için `ottoman-archives`
`ottoman_convert_date` / `ottoman_parse_ottoman_date` ile eşle (bkz.
`chronology.md`). Rapor/atıf tarihini daima **orijinal takvim + Miladî** çifti
olarak ver (§ `citation-and-transliteration.md` §6).

---

## 5. Atıf formatı (fon/kutu/gömlek)

Resmî katalogdan doğrulanan bir kayıt, `citation-and-transliteration.md` §6.1
şablonuyla atıflanır ve — dijital erişildiği için — dipnota **katalog URL'i**
(`belge_url`) eklenir:

```
BOA, DH.İ.UM, 22/19, H-27-12-1337 (M. 1919).
  <https://katalog.devletarsivleri.gov.tr/…BelgeGoster.aspx?ItemId=…>  [devlet-arsivleri kataloğundan doğrulandı]
BCA, 030.10/57.376.4, 1932.
```

Böylece BOA/BCA belgeleri artık — önceki "belge fotokopisi için akreditasyon
gerekir; katalog URL'i verilemez" kısıtı yerine — **doğrulanabilir katalog
URL'iyle** dipnotlanır. Sayfa taraması `devarsiv_get_belge_image` ile çekilip okunabilir (§7);
çok-sayfalı tam satın-alınmış set artık **yerel arşivden** okunur (§8.2 arşiv-okuma
akışı, → `skills/arsiv-oku`); satın-alınmamışsa §8.1 satın-alma akışı (→ `skills/satinalma`)
başlatılır.

---

## 6. Prosopografi notu (DH.SAİD / Sicill-i Ahval)

`PROSOPOGRAPHY` modunda bir Osmanlı memurunun hizmet kaydı için:
`devarsiv_search("<ad> sicill-i ahval", arsiv=2)` veya doğrudan `DH.SAİD` fonunu
tara → aday kayıtların `item_id`/künyesini al → hizmet çizelgesini kur. Modern
akademisyen prosopografisi için `yok-akademik` (destekleyici) ile birleştir.
Sicill-i Ahval kaydının **taramasını** `devarsiv_get_belge_image` ile çekip okuyarak
görev/tarih zincirini doğrudan çıkar (§7).

---

## 7. Belge okuma — OCR / HTR + görsel okuma + motor konvansiyonu (K2/K3)

Katalog artık salt-metadata değil: **BelgeGoster sayfa taramasını full-res base64 JPEG
olarak sunar** (`<img id="sample_picture">`), **satın-alma durumundan bağımsız** → satın
alınmamış belgelerin önizlemeleri de okunabilir. Satın-alınmışsa okuma DAİMA §8.2'deki
yerel arşiv akışından yapılır (300 DPI, temsilî önizlemeden daha yüksek kalite).

### 7.1 Motor konvansiyonu (K2)

`devarsiv_ocr_belge` / `devarsiv_ocr_archive_pages` / `devarsiv_ocr_submit` aynı
`engine` parametresini paylaşır:

`engine`: `auto` (Osmanlı→`both`, diğerleri→`tesseract`) | `both` | `transkribus` |
`escriptorium` | `tesseract`.

`both` → **Transkribus** (el yazması, PyLaia) + **eScriptorium** (basılı, Kraken)
**PARALEL** çalışır; iki transkripsiyon `transcriptions` altında yan yana + tesseract
damga/referans-kodu katmanıyla birlikte **üç sütun** döner (§8.3). Düşen motor dürüst
`unavailable` nedeni taşır. Latin arşivler (1/3/4) daima `tesseract`. **Görü birincil,
HTR yardımcı** — Transkribus taşra-kâtibi ellerinde gürültülü olabilir (2026-07-09 canlı
gözlem); bu yüzden Osmanlı OCR varsayılanı `engine="both"` (görü birincil çapraz-kontrol,
HTR/Kraken yardımcı).

| İçerik | En iyi motor | Nasıl |
|---|---|---|
| **Latin / Cumhuriyet (BCA) + modern** | `tesseract` (`tur+eng`) | `devarsiv_ocr_belge(…, engine="tesseract")` → tam makine metni + güven |
| **Osmanlı taramasındaki basılı damga + arşiv referans kodu** | `tesseract` (`tur+eng+ara`) | `devarsiv_ocr_belge(…, engine="both")` içindeki tesseract katmanı → ör. `İ.SH.00001,00001.001` güvenilir okunur (~60 conf) |
| **El yazması Osmanlıca Arap-harfli gövde** | **Transkribus PyLaia HTR** (deterministik) *+ tamamlayıcı* asistan görüsü / eScriptorium Kraken | `devarsiv_ocr_belge(…, engine="both")` → §7.2 K3 model tablosuyla çeviriyazır + eScriptorium basılı çapraz-kontrol; düşük-kalite/çapraz-doğrulama için `devarsiv_get_belge_image` + asistan görüsü |

### 7.2 Transkribus model seçim tablosu (K3)

| Belge türü | Model | Alfabe | CER | Not |
| --- | --- | --- | --- | --- |
| El yazması genel (divani/rika) | **56496** OttomanTurkish_generic | **Latin çeviriyazı** | ~%12 | Üretimdeki varsayılan (`DEVARSIV_TRANSKRIBUS_HTR_ID`) |
| Fetva / ilmiye el yazması | **169801** Ottoman Fatwa Manuscript | **Latin çeviriyazı** | %5.94 | Fetva/kadı-sicili tipi eller |
| El yazması — Arap-harfli çıktı | **429513** | **Arap harfli** | %9.36 | Katalogdaki TEK Arap-harfli Osmanlıca model; yalnız 1.054 satır eğitim |
| Matbu (salname/gazete/nizamname) | **52502** OttomanTurkish_Print_1 | **Latin çeviriyazı** | %7.2 | TTK "yarım-transkripsiyon" latinizasyon şeması |
| Matbu — daha geniş veri | **57485** OttomanTurkish_Print_v2 | Latin (ölçülmedi; 52502 soylu) | %7.6 | 52502 verisi + ek veri, 37.866 satır |

**⚠ Alfabe (2026-07-16 canlı ölçümü).** TK'nin Osmanlıca modelleri Arap-harfli görüntüyü okur ama
**Latin çeviriyazı yazar** (52502 kendi belgesinde TTK latinizasyon şemasını beyan eder; 56496 onu
baz model alıp karakter setini miras alır). eScriptorium **Arap harfli** yazar → iki çıktı
karşılaştırılamaz; `arbitrate=true` hakemliğinde `agreement_rate` tanım gereği 0 çıkar (bug değil).
Aynı alfabe tek seçenekle mümkün: **429513**. Detay: htr-workflow.md "Alfabe uyarısı".

Model değişimi deploy-notu: HP `~/devarsiv-mcp/runtime.env` →
`DEVARSIV_TRANSKRIBUS_HTR_ID=<id>` + `systemctl restart devarsiv-mcp`.

**Kanonik okuma akışı:**
```
devarsiv_search / semantic_search → item_id + hash
  ├─ devarsiv_ocr_belge(item_id, hash, arsiv, engine=…)   → deterministik metin (Latin tam; Osmanlı damga+kod; el yazması → both)
  └─ devarsiv_get_belge_image(item_id, hash, arsiv) → tarama görüntüsü:
        · Cumhuriyet/Latin: OCR metnini görsel doğrula
        · Osmanlı EL YAZMASI: **asistan taramayı görüsüyle transkribe eder** (en iyi tam-okuma, HTR ile çapraz-kontrol)
```

**Değişmezler (no-fabrication):**
- Görüntü **gerçek taramadır, uydurulmaz**; OCR düşük-güvende `mean_confidence` + `note` ile
  dürüstçe raporlanır — asla uydurma transkripsiyon.
- tesseract **basılı/dizgi** metni okur; **el yazması Osmanlıca'yı OKUMAZ** (deterministik OCR sınırı).
  El yazması için görsel-okuma (asistan) veya Transkribus HTR; çıktı her hâlde **insan
  doğrulamasına** tabi (çift-tarih + fon/kutu/gömlek atıf disiplini).
  **Transkribus HTR AKTİF (2026-07-08):** `devarsiv_ocr_belge` arsiv=2'de el yazması Osmanlıca'yı
  **Transkribus PyLaia + model 56496 (`OttomanTurkish_generic`)** ile deterministik olarak
  çeviriyazır (legacy TrpServer REST: upload→HTR→export; ~50s, ~1 kredi/sayfa; IJMES-diakritikli
  transliterasyon). ⇒ **el yazması için birincil deterministik yol `devarsiv_ocr_belge`.**
  `devarsiv_get_belge_image` + asistan görüsü tamamlayıcı kalır (düşük-kalite/gürültülü tarama,
  çapraz-doğrulama). HTR çıktısı **insan doğrulamasına tabidir** (model CER ~%12; gürültülü
  taramada daha düşük). Durum: `devarsiv_server_info` → `ocr.engines` (aktif/degrade).
- Önizleme = **temsilî tek sayfa**; `goruntu_sayisi` gerçek sayfa sayısını verir. Çok-sayfalı
  tam satın-alınmış set artık **yerel arşivden** okunur (§8.2, → `skills/arsiv-oku`).
- Getirilen tarama/transkripsiyon > eşik → **anamnesis'e ingest** (bağlam ekonomisi §3.5);
  büyük görüntü ana pencerede kör tutulmaz.

---

## 8. Dört kanonik akış (satın-alma / arşiv-okuma / üç-sütun transkripsiyon / async)

BelgeGoster yalnız **1 temsilî önizleme** (sample_picture) verir. Bir belgenin tüm
sayfalarına ulaşmak ve onu çok-motorlu okumak için aşağıdaki dört akıştan biri devreye
girer; hangisinin seçileceği `devarsiv_get_belge`'nin döndürdüğü `access` alanına
(`purchased`/`purchasable`) ve sayfa/motor ihtiyacına bağlıdır.

### 8.1 Satın-alma akışı (→ `skills/satinalma`)

```
devarsiv_get_belge(item_id, hash, arsiv) → access=purchasable
  → devarsiv_add_to_cart(item_id, hash, arsiv, pages?)      [_RW, ödemesiz]
  → devarsiv_list_cart()                                     [_RO, bağlayıcı Tutar]
  → KULLANICI METİN-ONAYI (sepet özeti + Tutar gösterilip açık onay alınmadan devam edilmez)
  → devarsiv_checkout_cart()                                 [_RO, ödeme YAPMAZ — yalnız noVNC URL + sepet döner]
  → İNSAN, noVNC üzerinden tarayıcıda ödemeyi TAMAMLAR (asistan asla otonom ödeme yapmaz)
  → devarsiv_list_purchased() ile satın-almayı doğrula → §8.2'ye geç
```

**Güvenlik anotasyonları:** `add_to_cart` `[_RW]` ve `remove_from_cart` `[_DESTRUCTIVE]`
devlet-değiştiricidir ama **para harcamaz**; `checkout_cart` de **ödeme YAPMAZ**. Ödeme
**DAİMA insan** tarafından, tarayıcı üzerinden tamamlanır. Fiyat dili: "~0,50 TL/sayfa
TAHMİNDİR; bağlayıcı tutar `devarsiv_list_cart` çıktısındaki Tutar sütunudur." Tek-cihaz
uyarısı **daima verbatim** aktarılır:

Kendi cihazınızdan kataloğa GİRMEYİN — tek-cihaz kilidi HP oturumunu düşürür.

noVNC: <https://devarsiv-vnc.cureonics.com/vnc.html> (Cloudflare Access, @cureonics.com OTP).

### 8.2 Arşiv-okuma akışı (→ `skills/arsiv-oku`)

Belge satın alınmışsa okuma **DAİMA yerel arşivden başlar**: `devarsiv_list_archive` →
`devarsiv_get_archive_page` (300 DPI + görü); katalog önizlemesi (sample) yalnız
satın-alınmamış belgeler içindir.

```
devarsiv_list_purchased() → {t, hash, ozet, sayfa}
  → devarsiv_list_archive(query?)                → BOA-kodlu yerel PDF künyesi (code/yer/tarih/özet/sayfa)
  → devarsiv_get_archive_page(code, page)         → 300 DPI ImageContent — BİRİNCİL okuma (görü)
  → (opsiyonel) devarsiv_get_archive_pdf(code, include_base64?, max_bytes?) → künye + sınırlı base64 PDF
```

Not: `devarsiv_ocr_belge_pages(t, hash, arsiv?, pages?, lang?, engine?)` de eSatış
viewer'ı üzerinden çok-sayfa OCR sağlar ama **temsilî-sayfa sınırlıdır**; TAM/güvenilir
yol yukarıdaki yerel-arşiv akışıdır. Sayfa metnine de ihtiyaç varsa §8.3/§8.4'e geç
(motor seçimine göre sync/async).

### 8.3 Üç-sütun transkripsiyon akışı (`engine="both"`, → `skills/arsiv-oku`)

Osmanlı el yazması sayfalarda varsayılan `engine="both"`: **Transkribus** (PyLaia, el
yazması, §7.2 K3 model tablosu) + **eScriptorium** (Kraken, basılı) **PARALEL** koşar,
tesseract damga/referans-kodu katmanıyla birlikte `transcriptions` altında **üç sütun
yan yana** döner (görü birincil çapraz-kontrol, HTR/Kraken yardımcı — bkz. §7.1 K2).
Düşen motor dürüst `unavailable` nedeni taşır; çıktı her hâlde **insan doğrulamasına**
tabidir.

### 8.4 Async OCR akışı (K4, → `skills/toplu-okuma`)

Sync/async kararı: **≤5 sayfa VE tek motor** → `devarsiv_ocr_archive_pages` (sync,
MULTIPAGE_MAX_PAGES). **>5 sayfa VEYA `both` tam belge** → async kuyruk:

```
devarsiv_ocr_submit(code, pages?, engine?, lang?, arsiv?)     [_RW, idempotent, job_id döner]
  → devarsiv_ocr_result(job_id, include_text=false)            [_RO, poll: queued/running/done/error/stale]
  → done'da TEK SEFER devarsiv_ocr_result(job_id, include_text=true)
  → anamnesis ingest_document(doc_id="devarsiv:<code>", …)
  → sonraki sorgular anamnesis hybrid_query (bağlam ekonomisi §3.5)
```

`stale` dönerse **aynı parametrelerle resubmit** (arşiv PDF yerel; maliyet tekrarlanmaz —
yalnız OCR işi yeniden kuyruklanır).

**Değişmez (no-fabrication, dört akışın tamamı için):** Çok-sayfa TAM erişim **yalnız
satın-alınmış** belgelerde; satın-alınmamışta katalog 2..N sayfayı sunmaz → o sayfalar
**uydurulmaz**, yalnız 1 önizleme + §8.1 satın-alma akışına yönlendirme yapılır.
