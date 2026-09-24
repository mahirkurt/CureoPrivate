# Düzenleyici Olgunluk Açığı Raporu — WHO Global Benchmarking Tool (GBT) iskeleti

**Mod:** REGULATORY_MATURITY · **Kapılar:** G0, G2, G5, G6, G7, G10, G11 · **Paket:** aktif yargı bölgesi paketi (`jurisdictions/<kod>/`)

> **Ne üretir:** bir ulusal düzenleyici sistemin mevzuat tabanını WHO GBT işlev yapısına göre
> haritalar ve **mevzuattan okunabilen** açıkları gösterir. GBT'nin kendisi bir **denetim**
> aracıdır (resmî değerlendirme WHO ekibi + ulusal otorite ile yapılır); bu rapor o
> değerlendirmenin **yerine geçmez**, onun mevzuat hazırlığıdır.
>
> **Doğrulanmış çerçeve (2026-09-24):** RS (ulusal düzenleyici sistem) + sekiz işlev —
> **MA** (kayıt ve pazarlama izni), **VL** (vijilans), **MC** (piyasa gözetimi ve kontrolü),
> **LI** (tesis ruhsatlandırma), **RI** (düzenleyici denetim), **LT** (laboratuvar testi),
> **CT** (klinik araştırma denetimi), **LR** (seri serbest bırakma). Olgunluk düzeyi 1–4;
> **düzey 3** = "istikrarlı, iyi işleyen ve bütünleşik düzenleyici sistem" (asgari hedef).
> Rev VI incelemesinde **268 alt gösterge** raporlanmıştır (Frontiers in Medicine 2020;7:457);
> PAHO "yaklaşık 300" der — sayı revizyona bağlıdır.
>
> **Uydurma yasağı:** gösterge KİMLİKLERİ (ör. "RS01.02") ve gösterge METİNLERİ bu şablonda
> YOKTUR ve modelin belleğinden YAZILMAZ. Gösterge düzeyinde satır yalnız WHO'nun güncel GBT
> belgesinden (birincil kaynak, sürüm + tarih ile) alıntılanarak doldurulur; kaynak yoksa
> satır `manual_required` kalır.

---

## 0. Künye

| Alan | Değer |
|---|---|
| Yargı bölgesi | {{paket kodu + adı}} · paket sürümü {{pack_version}} · durum {{active/draft}} |
| Kapsam | {{ilaç / aşı / tıbbi cihaz / kan ürünleri — hangi ürün sınıfı}} |
| GBT sürümü | {{WHO GBT revizyonu + yayım tarihi — birincil kaynaktan; yoksa "belirlenemedi"}} |
| Referans tarihi (G10) | {{mevzuatın hangi tarihteki yürürlük hâline göre okunduğu}} |
| Resmî GBT değerlendirmesi var mı? | {{evet: tarih + yayımlanmış olgunluk düzeyi + kaynak · hayır · bilinmiyor}} — **uydurulmaz** |

## 1. Yönetici özeti

- Mevzuattan okunabilen en büyük üç açık (işlev + dayanak eksikliği).
- Düzey 3 hedefi için **mevzuat** tarafında gereken değişiklikler (kurumsal kapasite, bütçe, insan kaynağı bu raporun dışında — ayrıca beyan edilir).
- Güven etiketi: paket tavanı {{ceiling}} ({{uygulanan CC kuralları}}).

## 2. Norm envanteri — işlev başına yasal dayanak

Her satır: işlev → dayanak norm(lar) → norm hiyerarşisindeki yeri (paketin `norm_hierarchy`) → yürürlük durumu (G10) → kanıt defteri kimliği.

| İşlev | Dayanak norm (künye) | Hiyerarşi | Yürürlük (as-of) | Kanıt |
|---|---|---|---|---|
| RS — ulusal düzenleyici sistem | | | | E… |
| MA — kayıt ve pazarlama izni | | | | |
| VL — vijilans | | | | |
| MC — piyasa gözetimi ve kontrolü | | | | |
| LI — tesis ruhsatlandırma | | | | |
| RI — düzenleyici denetim | | | | |
| LT — laboratuvar testi | | | | |
| CT — klinik araştırma denetimi | | | | |
| LR — seri serbest bırakma | | | | |

> Bir işlev için dayanak bulunamadıysa "bulunamadı" yazılır ve **aranan bağlayıcılar** listelenir.
> Boş sonuç yokluk kanıtı değildir: "dayanak yok" ancak paketin S1 bağlayıcısı süpürmeyi
> tamamladıysa ve bu, kapsam manifestosunda görünüyorsa söylenebilir.

## 3. Açık analizi — mevzuatın yapabildiği / yapamadığı

| İşlev | Mevzuat açığı | Açığın türü | Kaynak |
|---|---|---|---|
| | {{ör. yetki devri var, usul düzenlemesi yok}} | yetki · usul · yaptırım · şeffaflık · bağımsızlık · kaynak | E… |

Açık türleri, rapor boyunca aynı sözlükle kullanılır. Kurumsal kapasite açığı (personel, laboratuvar akreditasyonu, bilgi sistemi) mevzuat açığı DEĞİLDİR — ayrı sütunda "mevzuat dışı" olarak işaretlenir.

## 4. Reliance ve uluslararası bağlantılar

- İşlev başına reliance kullanımı (MA ve LR'de tipik): mevzuat reliance'a **izin veriyor mu**, hangi referans otoriteleri anıyor, kararın egemenliği nasıl korunuyor → ayrıntı için `templates/reliance-framework.md`.
- Bölgesel uyum girişimleri (paketin `gate_params.G11` notu): üyelik / gözlemcilik — **doğrulanmış kaynakla**.

## 5. Öneri — mevzuat yol haritası

| Öncelik | İşlev | Önerilen düzenleme | Norm düzeyi | Gerekçe | Bağımlılık |
|---|---|---|---|---|---|
| 1 | | | {{paketin hiyerarşisinden}} | | |

Öneriler paketin legistik profiline göre biçimlenir (`legistic_profile`); profil `verified: false` ise şekil önerileri **CONDITIONAL** olarak işaretlenir (CC-8).

## 6. Sınırlar ve insan denetimi

- Bu rapor resmî GBT değerlendirmesi değildir; olgunluk DÜZEYİ ataması yapmaz.
- Paket `draft` ise çıktı en fazla LOW güvenlidir ve bu satır raporun başında da yer alır (CC-6).
- Kapsam manifestosu (G0) + `confidence_label` (paket + tavan alanlarıyla) zorunludur.
