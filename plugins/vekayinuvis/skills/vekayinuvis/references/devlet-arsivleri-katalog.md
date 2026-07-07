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

## 2. Araçlar ve akış

1. **`devarsiv_search(query, arsiv?, limit?)`** — resmî katalog serbest-metin araması.
   - Sonuç satırı: `arsiv · fon · kutu · gömlek · yer_sira · ozet · tarih (Hicri) ·
     item_id · hash · belge_url`.
   - Header **fon facet'leri** döner (sonucu daraltmak için).
2. **`devarsiv_get_belge(item_id, hash, arsiv)`** — tek kaydın künyesi
   (yer bilgisi = kutu-gömlek, belge tarihi, kurum=fon, dil, **görüntü sayısı**)
   + **erişim durumu** (`purchased` / `purchasable`).
3. **`devarsiv_detailed_search_fields(arsiv)`** — Detaylı Arama'nın arşive-özel
   alanları (fon-üst, tarih türü, özel kod, özet).
4. **`devarsiv_session_status()`** — oturum canlı mı (pre-flight).
5. **`devarsiv_server_info()`** — kapsam + caveat.

**Kanonik akış:** `devarsiv_session_status` → `devarsiv_search` (dar sorgu) →
ilgili satırın `item_id`+`hash`'i ile `devarsiv_get_belge`.

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
