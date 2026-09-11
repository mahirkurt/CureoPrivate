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

## 2. Araçlar ve akış (27 araç, 7 grup — K1)

Devarsiv artık yalnız katalog aramasıyla sınırlı değil: **kapsamlı async süpürme +
yerel store** (deep_search→deep_result + coverage), eSatış sepeti (state-changing,
**ödemesiz**), satın-alınmış belgelerin **yerel arşivi** (300 DPI + Transleyt OCR) ve bir
**async OCR kuyruğu** dahil **27 araç, 7 grup**tur. (Kesin sayı deploy'a göre değişir —
grup-kapsamı ölçülür, bkz. `/vekayinuvis:durum`.)

| Grup | Araç | Not |
| --- | --- | --- |
| Arama | `devarsiv_search(query, arsiv?, limit?)` | Basit Arama; `capped:true`→enumerasyon (§2b), çok geniş→`refine_required` |
| Arama | `devarsiv_semantic_search(query, arsiv?, limit?, rerank?)` | Diyakronik genişletme (karantina→tahaffuzhane) + bge-m3 rerank (§2c) |
| Arama | `devarsiv_detailed_search(arsiv, ozet?, ust_fon?, kutu?, gomlek?, sira?, tarih_turu?, yil_bas?, yil_bit?, limit?)` | OzelArama — 1000-cap altına daraltma/enumerasyon (§2b) |
| Arama | `devarsiv_list_fon_categories(arsiv)` | Üst-fon listesi (enumerasyon ekseni, §2b) |
| Arama | `devarsiv_detailed_search_fields(arsiv)` | Form-alan introspeksiyonu |
| Süpürme | `devarsiv_deep_search(query, arsiv?, ust_fon?)` `[_RW]` | **Kapsamlı async süpürme** (§2b) — arşiv×üst-fon×tarih kovaları, store'a yazar, `job_id`; `arsiv` boş→dört arşiv; `ust_fon` `arsiv` gerektirir; store yoksa `store_required` |
| Süpürme | `devarsiv_deep_result(job_id)` `[_RO]` | Süpürme durumu + **kapsam manifestosu** (`coverage.archives[]`); `complete=true` yalnız 6 koşul+tüm arşiv `completed`; `complete=false`→boş ≠ "yok" (§2b/§3) |
| Süpürme | `devarsiv_coverage(arsiv?, ust_fon?)` `[_RO]` | **Store hasat defteri** — "yok" mu "hasat edilmedi" mi ayrımı (§3 no-fabrication); yokluk sonucundan ÖNCE bak; `capped:true` kova tam değil |
| Belge | `devarsiv_get_belge(item_id, hash, arsiv)` | Künye + **`access`** (`purchased`=**SatinAldiklarim ledger-otoriter** · `preview`=önizleme ibaresi var ama ledger'da yok → sahip DEĞİL · `purchasable`) + `purchased` bool — hangi §8 akışına gidileceğini belirler |
| Belge | `devarsiv_get_belge_image(item_id, hash, arsiv, region?, zoom?, contrast?)` | Önizleme taraması ImageContent — **görüyle okuma**, satın-alma durumundan bağımsız. **v3.4:** `region`/`zoom`/`contrast` ile bölge-kırpma+büyütme (önizleme = interpolasyon) |
| Belge | `devarsiv_ocr_belge(item_id, hash, arsiv, lang?, engine?)` | Deterministik OCR/HTR; Osmanlı varsayılanı `engine="transleyt"` (bkz. §7 K2). Önizleme taramasındaki "…görüntülenmiştir" filigranı **Katman-0'da bastırılır** (`watermark_suppressed`); belge satın-alınmışsa `purchased_hint` temiz arşiv sayfalarına yönlendirir |
| Belge | `devarsiv_ocr_image(image_url, engine?, lang?)` | Harici IIIF/görüntü OCR; aynı motor beyni; SSRF allowlist'li (`DEVARSIV_OCR_IMAGE_HOSTS`, boş=kapalı) |
| Sepet | `devarsiv_add_to_cart(item_id, hash?, arsiv, pages?)` `[_RW]` | 1-tabanlı cbk sayfa seçimi ("1,3-5"; boş=tümü); ödeme yapmaz. **`hash` opsiyonel** — verilmezse sunucu çözer (yerel store → canlı hedefli arama; **asla uydurulmaz**). Belge zaten satın-alınmışsa `already_purchased`+`next_steps` döner. Yanıt slim (<20 KB, ASPX artığı yok) |
| Sepet | `devarsiv_list_cart()` `[_RO]` | Kalemler + **bağlayıcı Tutar** |
| Sepet | `devarsiv_remove_from_cart(rows?, contains?, clear?)` `[_DESTRUCTIVE]` | Satır sil / boşalt |
| Sepet | `devarsiv_checkout_cart()` `[_RO]` | Ödeme YAPMAZ; yalnız noVNC URL + güncel sepet döner |
| Arşiv | `devarsiv_list_purchased()` | SatinAldiklarim t/hash listesi |
| Arşiv | `devarsiv_rebuild_archive(incremental?, limit?)` `[_RW]` | Satın-alınanları yerel 300 DPI PDF arşivine kurar/günceller (eSatış ZIP→kayıpsız PDF); **TAM-belge tek yolu**; `session_required` korumalı, ödeme YAPMAZ (§8.2). **Her talep BENZERSİZ blok** (sayfa-aralığından deterministik kod → çakışma/kopya/eksik yok; front talepleri sayfalanmış listeden). `status:integrity_error` → kapsam-deliği/kopya (rapor `integrity`'de), o belge OCR'ı güvenilmez |
| Arşiv | `devarsiv_ocr_belge_pages(t, hash, arsiv?, pages?, lang?, engine?)` | Viewer üzerinden çok-sayfa OCR — **temsilî-sayfa sınırlı**; TAM/güvenilir yol yerel arşivdir (§8.2) |
| Arşiv | `devarsiv_list_archive(query?)` | BOA-kodlu yerel PDF arşivi (code/yer/tarih/özet/sayfa) |
| Arşiv | `devarsiv_get_archive_page(code, page, region?, zoom?, contrast?)` | **300 DPI ImageContent — satın-alınmış belgede BİRİNCİL okuma.** **v3.4:** `region=[x0,y0,x1,y1]` (0..1) + `zoom` (6–10×) + `contrast` → marjinal detayı (kenar yılı/derkenar/mühür) GERÇEK yüksek-res render (pdftoppm crop, upscale değil) |
| Arşiv | `devarsiv_ocr_archive_pages(code, pages?, arsiv?, lang?, engine?)` | Sync OCR, ≤5 sayfa (MULTIPAGE_MAX_PAGES) |
| Arşiv | `devarsiv_get_archive_pdf(code, include_base64?, max_bytes?)` | Künye + sınırlı base64 PDF |
| Async | `devarsiv_ocr_submit(code, pages?, engine?, lang?, arsiv?)` `[_RW]` | İdempotent; `job_id` döner |
| Async | `devarsiv_ocr_result(job_id, include_text?)` `[_RO]` | `queued`/`running`/`done`/`error`/**`stale`** |
| Durum | `devarsiv_session_status()` | HP oturumu canlı mı (pre-flight) |
| Durum | `devarsiv_server_info()` | Araç envanteri + caveat + **`ocr.engines`** (mevcut motorlar) + **`purchase_cart.manual_checkout_url`** (noVNC) |

**Kanonik akış (tekil kayıt):** `devarsiv_session_status` → `devarsiv_search` *veya*
`devarsiv_semantic_search` (dar/diakronik sorgu) → ilgili satırın `item_id`+`hash`'i ile
`devarsiv_get_belge` → dönen `access` alanına göre **§8'deki dört akıştan biri**
(satın-alma / arşiv-okuma / iki-okuyucu transkripsiyon / async).

**Araç seçim rehberi:**
- Tam-eşleşen bilinen terim/fon → `devarsiv_search`.
- Modern terim / dönem-değişken sözcük / "hangi karşılıklar var" → `devarsiv_semantic_search`.
- Belirli fon+tarih+özet ile hassas daraltma → `devarsiv_detailed_search`.
- Konu >1000 kayıt (kapsamlı/tam tarama) → **`devarsiv_deep_search`** (otomatik async süpürme →
  `devarsiv_deep_result` poll; store gerektirir) — manuel `list_fon_categories`+`detailed_search`
  enumerasyonu yalnız store kapalıyken/dar hedefte (§2b).
- Boş sonuçtan "arşivde yok" sonucuna varmadan ÖNCE → **`devarsiv_coverage`** (hasat defteri; §3).
- **Belgeyi OKUMAK** (metin/içerik): `access=purchased` (**SatinAldiklarim ledger-otoriter** — künye
  ibaresi değil; "purchased görünen ama alınamayan/okunamayan" sahte-owned tuzağı 2026-07-20'de
  sunucuda kalktı) → doğrudan **§8.2 arşiv-okuma akışı** (`devarsiv_list_archive`→
  `devarsiv_get_archive_page`, → `skills/arsiv-oku`); `access=purchasable` **veya `preview`**
  (ikincisi: künyede "daha önce satın aldınız" ibaresi VAR ama ledger'da YOK → **sahip DEĞİL**) ve
  önizleme yeterliyse `devarsiv_get_belge_image`+`devarsiv_ocr_belge`; tüm sayfalar gerekiyorsa önce
  **§8.1 satın-alma akışı** (→ `skills/satinalma`) başlatılır (artık sahte-`already_purchased` engeli yok).

---

## 2b. Kapsamlı erişim (1000-tavan aşımı — süpürme + store)

Katalog **en çok 1000 satır sayfalama olmadan** render eder; çok büyük sorgu
`refine_required` ile reddedilir. Bu yüzden **tam 1000** (`capped:true`) = *daha fazlası
var* demektir.

### 2b.1 Birincil yol — `devarsiv_deep_search` (otomatik async süpürme)

Kapsamlı erişimin **birincil** yolu artık otomatiktir: `devarsiv_deep_search(query, arsiv?,
ust_fon?)` konuyu **arşiv × üst-fon × tarih** kovalarına böler, `capped` her kovayı tarih
ekseninde ikiye bölerek tavanın altına indirir, sonuçları **yerel store'a** yazar ve bir
**kapsam defterine** işler. `arsiv` verilmezse **dört arşiv birden** (her biri kendi üst-fon
listesi ve tarih açıklığıyla, biri diğerine sızmadan). `ust_fon` `arsiv` gerektirir (fon kodları
arşive özeldir). Store KAPALIYSA süpürme başlatılmaz → `store_required`.

**Async sözleşmesi (OCR K4 ile aynı):**
```
job = deep_search(query="tahaffuzhane")           # arsiv boş → dört arşiv; job_id + created
# poll (idempotent — created:false canlı işi döner, tekrar süpürmez):
res = deep_result(job.job_id)                      # coverage manifestosu
#   res.coverage.complete == true  → YALNIZCA 6 koşul + tüm archives[] "completed"
#   res.coverage.complete == false → KISMİ; boş sonuç 'yok' değildir
#   res.coverage.archives[] → arşiv-başına status: completed/partial/aborted/not_started
```
`complete=true` bile **iki eksende koşulludur**: yalnız süpürülen `year_bounds` (bu açıklığın
DIŞI + tarihsiz kayıtlar taranmadı) ve `fon_bounds` (yalnız listelenen üst-fonlar; `ust_fon`
verildiyse kapsam O TEK FON) içinde okunur. Tamlık iddiası asla "bu arşivin tamamı tarandı"
demek değildir. Hiç başlanmamış arşiv manifestoda `not_started` olarak **görünür** (tahmine
bırakılmaz). Süpürme tarayıcı kilidini paylaşır → uzun sürer, diğer devarsiv araçlarını yavaşlatır.

### 2b.2 Yedek yol — manuel enumerasyon (store kapalıyken / dar hedefte)

Store kapalıysa veya çok-dar hedefli bir koşumda **üst-fon × tarih-aralığı** ekseninde elle
daralt ve `item_id` ile birleştir:

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

Her iki yol da **ağır** olduğundan ana pencerede değil, **`arsiv-tarama-distilleri`
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
- **STORE-FIRST: boş sonuç yokluk kanıtı DEĞİLDİR.** Bir konuda boş sonuç aldığında "arşivde
  yok" SONUCUNA VARMADAN ÖNCE `devarsiv_coverage(arsiv?, ust_fon?)` ile hasat defterine bak:
  ilgili kova defterde yoksa doğru cevap **"bilmiyoruz / bu kova henüz hasat edilmedi"**dir,
  "yok" değil → `devarsiv_deep_search` ile süpür. `deep_result.coverage.complete=false` iken de
  boş sonuç yokluk kanıtı değildir; tamlık iddiası yalnız süpürülen `year_bounds`/`fon_bounds`
  içinde geçerlidir. `capped:true` kova 1000 tavanına vurmuş → o kova TAM DEĞİLDİR.
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
  2. (İsteğe bağlı) `sudo systemctl restart devarsiv-chrome` — yalnız Chrome şişmiş/form render etmiyorsa; restart oturumu düşürür (zaten ölüyse bedelsiz). Kalıcı devarsiv-x11vnc/noVNC unit'leri zaten aktif (vncpass YOK).
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

`engine`: `auto` (Osmanlı→`transleyt`, diğerleri→`tesseract`) | `both` | `transkribus` |
`escriptorium` | `tesseract`.

**Osmanlı varsayılanı `transleyt`** (ölçülen en iyi okuyucu; en doğru okuma Transleyt +
asistan görüsü uzlaştırması — kanonik doktrin: `/vekayinuvis:transkripsiyon` §İki-okuyucu
uzlaştırma). `both` açıkça istenirse **Transkribus** + **eScriptorium** paralel koşar
(matbu/çapraz-kontrol); iki transkripsiyon `transcriptions` altında yan yana + tesseract
damga katmanı döner (§8.3). Düşen motor dürüst `unavailable` taşır. Latin arşivler (1/3/4)
daima `tesseract`. Zayıf motorları (ES 0.479, TK 0.782) oya katmak doğruluğu düşürür.

| İçerik | En iyi motor | Nasıl |
|---|---|---|
| **Latin / Cumhuriyet (BCA) + modern** | `tesseract` (`tur+eng`) | `devarsiv_ocr_belge(…, engine="tesseract")` → tam makine metni + güven |
| **Osmanlı taramasındaki basılı damga + arşiv referans kodu** | `tesseract` (`tur+eng+ara`) | Transleyt çıktısıyla birlikte tesseract damga katmanı → ör. `İ.SH.00001,00001.001` güvenilir okunur (~60 conf) |
| **El yazması Osmanlıca Arap-harfli gövde** | **Transleyt** (0.130) + asistan görüsü (0.154) uzlaştırması | `devarsiv_ocr_belge(…)` varsayılanı Transleyt metnini döndürür; asistan `devarsiv_get_belge_image` taramasını görüsüyle okuyup uzlaştırır (ikisi denk ve bağımsız) |

### 7.2 Transkribus model tablosu — neden TK bir transkripsiyon rakibi DEĞİL

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
karşılaştırılamaz — TK ayrı bir çıktıdır (Latin çeviriyazı), iki-okuyucu uzlaştırmasının rakibi
değildir. Aynı alfabe tek seçenekle mümkündü (**429513**) ama ölçüm onu da eledi (aşağı bak).

**⚠ Osmanlı varsayılanı artık `transleyt` (2026-07-17 ölçümü).** OpenITI MAKHZAN uzman
ground-truth'una karşı 6 rik'a/divanî yazma sayfasında normalize CER: **Transleyt 0.230 ort. /
0.130 rik'a** · asistan görüsü 0.154 · eScriptorium 0.479 · **TK-429513 0.782 (kullanılamaz)** ·
tesseract Osmanlıca gövdede sıfır. Eski varsayılan `both` ölçümden önceki tahmindi ve gerekçesi
tutmuyordu (`both` zaten kredi ölçümlü Transkribus'u çağırıyordu). Keşif taramasında hâlâ
`engine="escriptorium"` (bedava). En doğru okuma = **Transleyt + asistan görüsü uzlaştırması**
(denk ve bağımsız); zayıf motorları oya katmak doğruluğu düşürür. Detay: htr-workflow.md
"Motor doğrulukları".

Model değişimi deploy-notu: HP `~/devarsiv-mcp/runtime.env` →
`DEVARSIV_TRANSKRIBUS_HTR_ID=<id>` + `systemctl restart devarsiv-mcp`.

**Kanonik okuma akışı:**
```
devarsiv_search / semantic_search → item_id + hash
  ├─ devarsiv_ocr_belge(item_id, hash, arsiv, engine=…)   → deterministik metin (Latin tam; Osmanlı damga+kod; el yazması → transleyt)
  └─ devarsiv_get_belge_image(item_id, hash, arsiv) → tarama görüntüsü:
        · Cumhuriyet/Latin: OCR metnini görsel doğrula
        · Osmanlı EL YAZMASI: **Transleyt (varsayılan) + asistan görüsü uzlaştırması** (ikisi denk ve bağımsız)
```

**Değişmezler (no-fabrication):**
- Görüntü **gerçek taramadır, uydurulmaz**; OCR düşük-güvende `mean_confidence` + `note` ile
  dürüstçe raporlanır — asla uydurma transkripsiyon.
- tesseract **basılı/dizgi** metni okur; **el yazması Osmanlıca'yı OKUMAZ** (deterministik OCR sınırı).
  El yazması için varsayılan **Transleyt** (0.130) + asistan görüsü (0.154) uzlaştırması: MCP
  Transleyt metnini döndürür, asistan aynı sayfayı görüsüyle okuyup uzlaştırır (ikisi denk ve
  bağımsız — ölçüm 0.231→0.162). Transkribus Latin çeviriyazı yazar (transkripsiyon rakibi değil).
  Çıktı ölçülü %13-23 CER taşır (özel ad/tarih/yer/meblağda hata beklenir; hata payı çıktıda beyan
  edilir; birincil-kaynak yorumu araştırmacıya aittir). Durum: `devarsiv_server_info` → `ocr.engines`.
- Önizleme = **temsilî tek sayfa**; `goruntu_sayisi` gerçek sayfa sayısını verir. Çok-sayfalı
  tam satın-alınmış set artık **yerel arşivden** okunur (§8.2, → `skills/arsiv-oku`).
- Getirilen tarama/transkripsiyon > eşik → **anamnesis'e ingest** (bağlam ekonomisi §3.5);
  büyük görüntü ana pencerede kör tutulmaz.

---

## 8. Dört kanonik akış (satın-alma / arşiv-okuma / iki-okuyucu transkripsiyon / async)

BelgeGoster yalnız **1 temsilî önizleme** (sample_picture) verir. Bir belgenin tüm
sayfalarına ulaşmak ve onu çok-motorlu okumak için aşağıdaki dört akıştan biri devreye
girer; hangisinin seçileceği `devarsiv_get_belge`'nin döndürdüğü `access` alanına
(`purchased`/`purchasable`) ve sayfa/motor ihtiyacına bağlıdır.

### 8.1 Satın-alma akışı (→ `skills/satinalma`)

```
devarsiv_get_belge(item_id, hash, arsiv) → access=purchasable
  → devarsiv_add_to_cart(item_id, hash?, arsiv, pages?)     [_RW, ödemesiz; hash ops.—store/canlı çözer]
       (access=purchased ise already_purchased+next_steps döner → §8.2)
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

### 8.3 İki-okuyucu transkripsiyon akışı (`engine="transleyt"`, → `skills/arsiv-oku`)

Osmanlı el yazması sayfalarda varsayılan `engine="transleyt"`: MCP Transleyt metnini
(0.130) döndürür, asistan aynı sayfayı görüsüyle (0.154) okuyup uzlaştırır — ikisi denk ve
bağımsız (ölçüm 0.231→0.162). Kanonik doktrin: `/vekayinuvis:transkripsiyon` §İki-okuyucu
uzlaştırma. `both` açıkça istenirse Transkribus + eScriptorium paralel koşar (matbu/çapraz-
kontrol). Adaylar **ayrı** raporlanır (tek birleşik metin YASAK); çıktı ölçülü %13-23 CER
taşır (özel ad/tarih/yer/meblağda hata beklenir, çıktıda beyan edilir).

### 8.4 Async OCR akışı (K4, → `skills/toplu-okuma`)

Sync/async kararı: **≤5 sayfa** → `devarsiv_ocr_archive_pages` (sync,
MULTIPAGE_MAX_PAGES). **>5 sayfa VEYA çok-motorlu (`both`) tam belge** → async kuyruk:

```
devarsiv_ocr_submit(code, pages?, engine?, lang?, arsiv?)     [_RW, idempotent, job_id döner]
  → devarsiv_ocr_result(job_id, include_text=false)            [_RO, poll: queued/running/done/error/stale]
  → done'da TEK SEFER devarsiv_ocr_result(job_id, include_text=true)
  → anamnesis ingest_document(collection=vekayinuvis:run:<12hex>, doc_id="vkrun:<12hex>:devarsiv:<code>", …)
  → sonraki sorgular anamnesis hybrid_query(collection=…) (bağlam ekonomisi §3.5; atıf doc_id::idx)
```

`stale` dönerse **aynı parametrelerle resubmit** (arşiv PDF yerel; maliyet tekrarlanmaz —
yalnız OCR işi yeniden kuyruklanır).

**Değişmez (no-fabrication, dört akışın tamamı için):** Çok-sayfa TAM erişim **yalnız
satın-alınmış** belgelerde; satın-alınmamışta katalog 2..N sayfayı sunmaz → o sayfalar
**uydurulmaz**, yalnız 1 önizleme + §8.1 satın-alma akışına yönlendirme yapılır.

### 2026-09-11 — devarsiv v0.2.0 sözleşme ekleri (ADDITIVE; eski alanlar değişmedi)

- **Oturum telemetrisi:** `devarsiv_session_status.session` artık `state` (`alive|dead|unknown`),
  `kind` (`session_dead|upstream_outage|unknown` — kesinti ile oturum ölümünü ayırır),
  `last_alive_at`, `dead_for_s`, `death_count`, `novnc_url`, `runbook[]` (kanonik, sunucudan) taşır.
  `session_required`/`upstream_error` zarfları da aynı alanları taşır → hook `runbook`'u sunucudan basar.
  Sunucu ölümü kendi tespit eder (süreç-içi probe, 8 dk; HTTP 500 = oturum yok) ve ntfy push atar.
- **`filter_unapplied`** (`devarsiv_detailed_search`): filtre uygulanamadı → arama YÜRÜTÜLMEDİ
  (`field`, `control_id`, `requested_value`, `reason ∈ control_missing|option_missing:N|readback_mismatch`).
  Bu bir SONUÇ değildir; `option_missing` = o değer bu arşivin listesinde yok (ör. `SH.`) →
  `devarsiv_list_fon_categories`. deep_search kovası bu durumda `filter_unapplied` (terminal), `complete:false`.
  Başarılı detaylı aramada `filters_applied[]` (`verified`, `verified_after_submit`).
- **`membership_expired`**: üyelik bitimi (1 yıl + uzatma) ≠ oturum ölümü; `needs_relogin:false` →
  DAB/e-Devlet yenileme.
- **`devarsiv_relogin_prepare()`** `[_RW]`: oturum ölüyken tarayıcıyı e-Devlet kapısına götürür,
  kimlik formunda DURUR (sır yok, otomatik giriş yok); reCAPTCHA kota hatasında yedek yol.
- **`devarsiv_fon_info(code|query)`** `[_RO]`: Osmanlı Arşivi Rehberi 2017 EK III (941 fon kodu) —
  kod/ön-ek/ad; **`devarsiv_yer_adi(query)`** `[_RO]`: resmî Yer Adları Sözlüğü (66.466 madde) —
  Osmanlıcası, nam-ı diğer, kaza/liva/vilayet, `search_variants[]` (arama adayları). Her ikisi
  ≤50 satır, `source` + `license_note` (atıf zorunlu, RG 31616 Md. 12/1).
- **`semantic_search.fon_hints[]`** (olası üst-fonlar); `deep_search` fon sırasını buna göre öne
  alır (`fon_bounds.order_source`). Gazetteer genişletme katmanı **varsayılan kapalı** (ablasyon önce).
- **Sepet:** `cart.cost_estimate_try` (0,50 TL/görüntü) + `cost_estimate_matches_total`; BAĞLAYICI
  tutar yine `toplam_tutar`. **`usage_terms`** arşiv/OCR çıktılarında (Md. 11/2 ticari yasak, 12/1 atıf).
- **Store v2:** `detailed_search` ölü oturumda da store fallback'li (`filter_fidelity`); satırlar
  `yil_norm/takvim/hash_verified_at` taşır. `server_info.tools` registry'den (30 araç).
