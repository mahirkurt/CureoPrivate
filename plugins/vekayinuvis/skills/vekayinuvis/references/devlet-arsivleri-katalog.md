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

## 2. Araçlar ve akış (8 araç)

1. **`devarsiv_search(query, arsiv?, limit?)`** — resmî katalog serbest-metin (Basit Arama).
   - Sonuç satırı: `arsiv · fon · kutu · gömlek · yer_sira · ozet · tarih (Hicri) ·
     item_id · hash · belge_url`.
   - Header **fon facet'leri** + `total_rendered` + **`capped`** döner. `capped:true`
     (tam 1000 satır) = *daha fazlası var* → §2b enumerasyonuna geç.
2. **`devarsiv_semantic_search(query, arsiv?, limit?, rerank?)`** — **diakronik/semantik**
   arama (§2c). Modern sorguyu Osmanlıca eşdeğerlerine genişletir (karantina →
   tahaffuzhane/sıhhiye/kordon; göçmen → muhacir/mülteci), her varyantı çalıştırır,
   `item_id` ile birleştirir, sonra özet-benzerliğine göre **bge-m3** ile yeniden sıralar.
   Terim-belirsiz / modern-terimli konularda `devarsiv_search` yerine **bunu** kullan.
3. **`devarsiv_detailed_search(arsiv, ozet?, ust_fon?, kutu?, gomlek?, sira?, tarih_turu?,
   yil_bas?, yil_bit?, limit?)`** — **hassas/enumerasyon** aracı (OzelArama). Herhangi bir
   konuyu 1000-tavanının altına daraltır (arşiv × üst-fon × tarih-aralığı × özet) → §2b
   kapsamlı erişim omurgası.
4. **`devarsiv_list_fon_categories(arsiv)`** — arşivin **üst-fon** (fon grubu) listesi
   (Osmanlı 49 grup: A.} / BEO / C.. / DH.. / HAT / İ.. / Y.. …; Cumhuriyet 16…). Bir
   >1000 konuyu tüketici biçimde bölmek için **enumerasyon ekseni** (§2b).
5. **`devarsiv_get_belge(item_id, hash, arsiv)`** — tek kaydın künyesi
   (yer bilgisi = kutu-gömlek, belge tarihi, kurum=fon, dil, **görüntü sayısı**)
   + **erişim durumu** (`purchased` / `purchasable`).
6. **`devarsiv_detailed_search_fields(arsiv)`** — Detaylı Arama'nın arşive-özel
   alanları (fon-üst, tarih türü, özel kod, özet) — introspeksiyon.
7. **`devarsiv_session_status()`** — oturum canlı mı (pre-flight).
8. **`devarsiv_server_info()`** — kapsam + caveat.

**Kanonik akış (tekil kayıt):** `devarsiv_session_status` → `devarsiv_search` *veya*
`devarsiv_semantic_search` (dar/diakronik sorgu) → ilgili satırın `item_id`+`hash`'i ile
`devarsiv_get_belge`.

**Araç seçim rehberi:**
- Tam-eşleşen bilinen terim/fon → `devarsiv_search`.
- Modern terim / dönem-değişken sözcük / "hangi karşılıklar var" → `devarsiv_semantic_search`.
- Belirli fon+tarih+özet ile hassas daraltma → `devarsiv_detailed_search`.
- Konu >1000 kayıt (kapsamlı/tam tarama) → `devarsiv_list_fon_categories` + `devarsiv_detailed_search` (§2b).

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
- **Belge görüntüsü üretilmez.** `get_belge` yalnız künye + erişim/satın-alma
  durumu verir; belge fotokopisi/tam-metni eSatış satın-alma veya on-site
  akreditasyon kapısındadır. Görüntü içeriğini asla uydurma (§ kısıtlı-kaynak).
- **Oturum yoksa `session_required`.** Tek-cihaz oturum kilidi (HP'de kalıcı
  authenticated tarayıcı) düştüğünde araçlar `session_required` döner
  (portal deep-link + yankılanan sorgu). Bu durumda kullanıcıya bildir:
  *"Resmî katalog oturumu düştü; HP noVNC re-login gerekiyor"* — ve
  `ottoman-archives`/`yoktez`/`literatur` ile degrade araştırmaya devam et.
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
URL'iyle** dipnotlanır. Görüntünün kendisi hâlâ erişim-kısıtlıdır.

---

## 6. Prosopografi notu (DH.SAİD / Sicill-i Ahval)

`PROSOPOGRAPHY` modunda bir Osmanlı memurunun hizmet kaydı için:
`devarsiv_search("<ad> sicill-i ahval", arsiv=2)` veya doğrudan `DH.SAİD` fonunu
tara → aday kayıtların `item_id`/künyesini al → hizmet çizelgesini kur. Modern
akademisyen prosopografisi için `yok-akademik` (destekleyici) ile birleştir.
