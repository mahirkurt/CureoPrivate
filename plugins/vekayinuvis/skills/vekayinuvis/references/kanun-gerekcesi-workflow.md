# KANUN_GEREKÇESİ Mod — Tam İş Akışı (v1.1)

> `vekayinuvis` skill'inin **§ 5.9 KANUN_GEREKÇESİ** modunda etkinleşen ek
> referans. Türk anayasası ve TBMM İçtüzüğü m. 73-74 uyarınca her kanun
> teklifi/tasarısının gerekçe metninde **tarihsel arka plan** ve
> **antecedant mevzuat zinciri** bulundurma yükümlülüğünü, akademik bir
> tarihçi titizliğiyle yerine getirmek için tasarlanmıştır.
>
> Bu dosya beş bölümden oluşur: (1) girdi spektrumu, (2) beş-katmanlı
> zincir mantığı, (3) paralel-çağrı seti, (4) TBMM-uyumlu çıktı şablonu,
> (5) `lex-sanitas` ile composable akış + ek kalite kapıları (G7-G8).

---

## 1. Girdi Spektrumu

KANUN_GEREKÇESİ modu **üç farklı tipte girdi** ile tetiklenebilir. Her
girdi tipi farklı bir paralel-çağrı stratejisi gerektirir.

### 1.1 Tip A — Yürürlükteki bir kanunun reform/ilga süreci

**Örnek**: *"1219 sayılı Kanun'u modernize ediyoruz; mevcut yapısının
tarihî genealojisini üret."* (Mahir Bey'in Türkiye Sağlık Mevzuatı Reformu
çalışması)

Bu tipte skill:
- Yürürlükteki kanunun **tam Resmî Gazete metnini** (Düstûr/RG arşivinden)
- Kanunun **tüm değişiklik tarihçesini** (her değiştirici kanun + RG sayısı)
- Kanunun **antecedant Osmanlı mevzuatını** (Tanzimat'tan 1928'e)
- Kanunla ilgili **AYM/Danıştay içtihatını** (varsa)
- AB **karşılaştırmalı uyum süreci**ni
çıkarır.

### 1.2 Tip B — Yeni bir kanun teklifi için tarihî gerekçe

**Örnek**: *"Türkiye'de Sağlık Verisi Mahremiyeti Kanunu için tarihî
çerçeve."*

Bu tipte skill, kanunun **konusu** üzerinden geriye doğru çalışır:
- Konunun **Osmanlı klasik düzenindeki yeri** (varsa)
- **Tanzimat-Islahat döneminde** ilk modernleşme girişimleri
- **II. Meşrutiyet** yasaması
- **Erken Cumhuriyet** ve sonrası
- **Modern Türkiye** mevzuat haritası (KVKK, mevcut sağlık mevzuatı)

### 1.3 Tip C — TBMM müzakere kayıtlarının arşiv-temelli yorumlanması

**Örnek**: *"1928'de 1219'un müzakeresinde Adnan Adıvar'ın konuşmaları."*

Bu tipte skill, doğrudan **TBMM Zabıt Ceridesi**ne odaklanır:
- `acikerisim.tbmm.gov.tr` üzerinden müzakere tutanağı (Devre/İçtima/B./S.)
- Konuşmacıların biyografik tanıtımı (`PROSOPOGRAPHY` modu ile composable)
- Müzakere tarihinin Hicrî/Rumî karşılığı (`CHRONOLOGY_CONVERSION`)
- Dönem basınında müzakerenin yansıması (Cumhuriyet, Akşam, Vakit gazeteleri)
- Müzakere sonrası ilan edilen Resmî Gazete numarası ve tarihi

---

## 2. Beş-Katmanlı Yasama Tarihçesi (L1–L5)

Her KANUN_GEREKÇESİ çıktısı bu beş katmanı **mutlaka** kurar. Bir
katmanda kanıt boşluğu varsa **şeffaf olarak** etiketlenir; varsayım
üretilmez.

### 2.1 Katman Tablosu — Detay

| Katman | Dönem | Birincil mevzuat kaynakları | Tipik atıf formatı |
|---|---|---|---|
| **L1. Klasik Osmanlı** | 16–19. yy başı | Kanun-ı Şâh, Kanunnâme-i Âl-i Osman (Fatih), Mecelle-i Ahkâm-ı Adliyye (1869-1876), şer'iyye sicilleri, fetvâ mecmuaları | *Kanunnâme-i Âl-i Osman*, [bölüm], h. [tarih] |
| **L2. Tanzimat-Islahat** | 1839–1876 | Düstûr I. Tertib (8 cilt), Takvîm-i Vekayi, ilk nizamnâmeler, Meclis-i Vâlâ kararları | *Düstûr* I. Tertib, c.[X], s.[Y], h.[tarih] |
| **L3. II. Meşrutiyet** | 1908–1922 | Düstûr II. Tertib (12 cilt), Meclis-i Mebusan Zabıt Ceridesi, Meclis-i Â'yân Zabıt Ceridesi, Cerîde-i İlmiye | *Düstûr* II. Tertib, c.[X], s.[Y], r.[tarih] |
| **L4. Erken Cumhuriyet** | 1923–1950 | TBMM Zabıt Ceridesi (Devre I-VIII), Düstûr III. Tertib, Resmî Gazete (1921'den itibaren) | *Resmî Gazete*, S.[sayı], [tarih]; TBMM ZC, D.[X], C.[Y], B.[Z], s.[N] |
| **L5. Modern Türkiye** | 1950–güncel | Resmî Gazete, AYM kararları (Kararlar Bilgi Bankası), Danıştay içtihatı, AB ilerleme raporları, AB direktifleri (CELEX), Venedik Komisyonu görüşleri | *Resmî Gazete*, S.[sayı], [tarih]; AYM E.[X]/K.[Y] sayılı karar |

### 2.2 Katman Bütünlüğü Kontrolü

Çıktı tamamlanmadan önce şu sorulara cevap aranır:

- **L1 boş mu?** → Konunun gerçekten klasik Osmanlı düzenleme alanı dışında
  olduğu mu, yoksa yetersiz tarama mı? Örn. *modern telekomünikasyon*
  → L1 doğal olarak boş; ama *aile/miras hukuku* → L1 boş olamaz.
- **L2 boş mu?** → Tanzimat döneminde meselenin doğrudan düzenlenmemiş
  olabileceği kabul edilebilir; ancak ilgili çevre nizamnâmeleri taranır.
- **L3 boş mu?** → II. Meşrutiyet, modern bürokratik mevzuatın temelidir;
  L3 boşluğu sıklıkla yetersiz aramayı işaret eder.
- **L4 boş mu?** → Erken Cumhuriyet'in temel kuruluş kanunları (1924
  Anayasa, 1926 Medenî Kanun, 1928 1219, 1930 1593 Umumi Hıfzıssıhha, 1936
  3017 Sıhhat Vekâleti, 1950 5847 vd.) L4'ün omurgasıdır.
- **L5 boş mu?** → Hemen hiç olmamalıdır; çağdaş Türk kanunlarının çoğunun
  son 20 yılda en az bir değişikliği vardır.

Bir katman gerçekten boşsa **çıktıda açıkça** belirtilir:

> *"L2 (Tanzimat-Islahat) için bu konuya doğrudan değinen bir nizamnâme
> tespit edilmemiştir. İlgili çevre düzenlemeler [...] hatlarında dolaylı
> olarak yer alır. Bu boşluk, Tanzimat reformlarının önceliklerini
> yansıtmaktadır."*

---

## 3. Paralel-Çağrı Seti

KANUN_GEREKÇESİ modu üç turda çalışır.

### 3.1 TUR 1 — Geniş Tarama (paralel)

```
TUR 1 (paralel, 6-8 connector):

  ├─ devarsiv_search("<kanun konusu>", arsiv="2")
  │     → BOA İrade/HAT/DH.* grubu — klasik–geç Osmanlı lâyiha ve müzakere
  │       kayıtları (canlı resmî katalog, fon/kutu/gömlek + item_id/hash)
  │
  ├─ devarsiv_search("<kanun konusu>", arsiv="1")
  │     → BCA 030.10 lâyiha/muamelat ve 030.18 Bakanlar Kurulu kararnameleri
  │       (erken Cumhuriyet; ottoman-archives'ta kayıt yoktu, boşluk kapandı)
  │
  ├─ ottoman_search_iiif(
  │     query="<kanun konusu> nizamname",
  │     sources=["internet_archive","gallica"],
  │     limit=10)
  │     → Düstûr I. ve II. Tertib taraması (IA dijital kopyaları)
  │     → Fransızca dönemin paralel mevzuatı (Gallica)
  │
  ├─ ottoman_search_dergipark(
  │     query="<kanun konusu> tarihçe",
  │     limit=15)
  │     → DergiPark + TR Dizin: konunun yasama tarihçesini
  │       ele alan TR akademik makaleleri
  │
  ├─ search_yok_tez_detailed(
  │     keyword="<kanun konusu> mevzuat tarihi",
  │     limit=10)
  │     → YÖKtez: doktora/yüksek lisans tezleri
  │       (özellikle Tıp Tarihi AD, Kamu Hukuku AD)
  │
  ├─ ottoman_get_islam_ansiklopedisi("<kanun konusu>")
  │     → TDV İA: konunun kurumsal/kavramsal tanımı
  │
  ├─ web_search("TBMM Zabıt Ceridesi <kanun no> müzakere")
  │     → acikerisim.tbmm.gov.tr üzerinden müzakere zaptı
  │     → resmigazete.gov.tr arşivi
  │
  ├─ search_semantic(
  │     query="<kanun konusu> Ottoman regulation history",
  │     limit=10)
  │     → İngilizce karşılaştırmalı literatür (IJMES, Studies on Ottoman
  │       Society and Culture, Comparative Legal History)
  │
  ├─ ottoman_search_dspace(query="<kanun konusu>", limit=10)
  │     → DSpace açık erişim arşivleri (TBMM Kütüphanesi, üniversiteler)
  │
  └─ tavily_search(query="<kanun konusu> Düstûr nizamname")
        → açık web: TBMM, Resmî Gazete, akademik blog, vd.
```

### 3.2 TUR 2 — Triangülasyon ve Katmanlama

Her bulgu beş katmandan (L1-L5) birine yerleştirilir. Her belge için:

1. **Tarih dönüşümü**: `ottoman_convert_date` ile Hicrî/Rumî/Miladî
   üçlü-doğrulama
2. **Quellenkritik**: birincil mi, ikincil mi, üçüncül mü; resmî mi,
   yarı-resmî mi, akademik mi
3. **Boşluk analizi**: hangi katmanda hangi belge eksik kalıyor?

### 3.3 TUR 3 — Drafting

Beş-katmanlı çıktı (§ 4'teki şablon) üretilir; her iddia için en az iki
bağımsız atıf hedeflenir.

---

## 4. TBMM-Uyumlu Çıktı Şablonu

TBMM İçtüzüğü m. 73 uyarınca her kanun teklifi/tasarısı şu üç bölümlü
gerekçe içermelidir: (a) Genel Gerekçe (madde adı), (b) Madde
Gerekçeleri, (c) eklerse: Karşılaştırma Cetveli, Etki Analizi. Bu
şablon, **(a) Genel Gerekçe**'nin "Tarihî Çerçeve" alt-bölümü için
tasarlanmıştır.

```markdown
# [Kanun adı] — Tarihî Gerekçe Çerçevesi

## Önsöz
[2 paragraflık açılış. Birinci paragraf: konunun modern Türk hukukundaki
yerini ve aciliyetini. İkinci paragraf: tarihî gerekçenin neden gerekli
olduğunu (mevzuat sürekliliği ilkesi, anlamlı yasama tarihi).]

## L1. Klasik Osmanlı Düzeninde Düzenleme (16.–19. yy başı)

[Konunun Osmanlı klasik hukuk düzenindeki yeri. Örf, kanun-ı kadim,
kanunnâme, Mecelle hükmü (varsa). Klasik dönemde tamamen düzenlenmemiş
olabilir; o durumda boşluk şeffaf belirtilir.]

**Atıflar**:
- Kanunnâme-i Âl-i Osman, [bölüm], h. [tarih].
- Mecelle-i Ahkâm-ı Adliyye, md. [X-Y], 1869-1876.
- [TDV İA ilgili madde].

## L2. Tanzimat ve Islahat Dönemi Reformları (1839–1876)

[İlk modernleşme dalgasında konunun düzenlenmesi. Düstûr I. Tertib
taraması; ilk modern nizamnâme/tüzük; varsa yabancı modellerden esin
(Fransız Code Civil, Avusturya Tıbbî Polis Nizamnâmesi, Alman
Sanitätsordnung). Tanzimat fermanının ilgili maddelerine atıf.]

**Atıflar**:
- *Düstûr* I. Tertib, c.[X], s.[Y], h. [tarih].
- *Takvîm-i Vekayi*, S.[sayı], h. [tarih].
- [İkincil: Engelhardt, Lewis, Findley, Heinzelmann, vd.]

## L3. II. Meşrutiyet Yasaması (1908–1922)

[Modern bürokratik mevzuatın olgunlaştığı dönem. Düstûr II. Tertib
nizamnâmeleri; varsa Meclis-i Mebusan müzakeresi. Bu dönem Türk
parlamenter hukukunun gerçek temelidir.]

**Atıflar**:
- *Düstûr* II. Tertib, c.[X], s.[Y], r. [tarih].
- Meclis-i Mebusan ZC, Devre [X], İçtima [Y], C.[Z], B.[N], s.[N].
- [İkincil: Hanioğlu, Akşin, Kayalı, vd.]

## L4. Erken Cumhuriyet ve İlk Modern Kanun (1923–1950)

[Bu, kanunun bugünkü hâlinin tarihî kökünü oluşturan ilk Cumhuriyet
kanunudur. TBMM müzakeresi (Devre/İçtima/B./S.), başlıca konuşmacılar
(Adnan Adıvar, Refik Saydam vd.), kabul oylama sonucu, Resmî Gazete
sayı ve tarihi.]

**Atıflar**:
- TBMM ZC, Devre [X], İçtima [Y], C.[Z], B.[N], [tarih], s.[N].
- *Resmî Gazete*, S.[sayı], [tarih].
- [İkincil: Behçet Cantürk, Sina Akşin, Erik J. Zürcher, vd.]

## L5. Cumhuriyet Sonrası Değişiklikler ve Modernleşme Baskıları (1950–[Bugün])

[Sonraki değişiklikler, ilgili AYM iptal kararları, Danıştay içtihatı,
AB uyum baskısı, Venedik Komisyonu görüşleri, OECD önerileri.]

**Atıflar**:
- *Resmî Gazete*, S.[sayı], [tarih]: [değişiklik kanunu].
- AYM, E.[X]/K.[Y] sayılı karar, [tarih].
- Danıştay [X]. Daire, E.[Y]/K.[Z], [tarih].
- AB [yıl] İlerleme Raporu, s.[X-Y].

## Sentez ve Reform Argümanı

[Önerilen reformun nasıl bir yasama-tarihî zinciri tamamladığı ya da
zincirden bir kopuş niteliği taşıdığı, akademik dürüstlükle. Reformun
hangi tarihsel ihtiyaçlara cevap verdiği, hangi tarihsel baskıları
modernize ettiği. Karşılaştırmalı hukuk: AB üye devletlerinin paralel
mevzuatı.]

## Boşluk ve Sınırlılık Notu

[Hangi katmanda hangi belgelere erişilemedi. Restricted BOA/TKGM
fondlarına yönlendirme. Hangi belgelerin fiilî tetkiki gereklidir.
Çağdaş belgelerden hangileri tam metin olarak ulaşıldı.]

## Kaynakça

### A. Birincil mevzuat metinleri (kronolojik)
[Mecelle, Düstûr cildi/sayfa, Resmî Gazete sayı/tarih]

### B. TBMM/Meclis-i Mebusan Tutanakları
[Devre/İçtima/Birleşim/Sayfa formatında]

### C. Arşiv belgeleri (varsa)
[BOA HAT/İrade/Y.PRK + dosya/gömlek no + tarih]

### D. İkincil literatür (Chicago N-B)
[Alfabetik]
```

---

## 5. lex-sanitas ile Composable Akış ve G7-G8 Kalite Kapıları

### 5.1 Composable Zincir

```
[vekayinuvis] KANUN_GEREKÇESİ modu (bu dosya)
   ↓
[Markdown gerekçe taslağı]
   - Önsöz
   - L1-L5 katmanları
   - Sentez
   - Kaynakça
   ↓
[lex-sanitas] kanun teklifi madde madde drafting
   - Madde 1, 2, 3... + her madde için ayrı gerekçe
   - Geçici maddeler
   - Yürürlük ve yürütme maddeleri
   ↓
[carbon-html-report] TBMM iç tüzüğüne uygun A4 PDF
   - IBM Plex Serif typeface
   - Resmî Gazete tarzı dipnot
   - Otomatik bibliyografya
   ↓ (paralel)
[carbon-pptx] Sağlık Komisyonu sunumu
   - Beş katman üzerine dayalı slayt yapısı
   - Reform argümanını destekleyen kronoloji görselleri
   ↓
[ms-converter] DOCX export (TBMM Kanunlar ve Kararlar Müdürlüğü için)
```

### 5.2 G7 — Yasama-Tarihî Bütünlük Kapısı

Çıktı şu kontrollerden geçmedikçe "draft" olarak işaretlenir:

- **G7.a**: Beş katmanın (L1-L5) hepsi denendi mi?
- **G7.b**: Her katmanda en az iki bağımsız kaynak triangüle edildi mi?
  (yalnızca birincil ya da yalnızca ikincil değil; ikisinin de
  kullanılmasına çalışıldı mı?)
- **G7.c**: Boşluk varsa, boşluğun nedeni şeffaf etiketlendi mi?
- **G7.d**: Her tarihsel iddia için Hicrî/Rumî/Miladî üçlü-doğrulama
  yapıldı mı? (`ottoman_convert_date` ile)
- **G7.e** (v1.2 — yeni): **Tek-kaynak kontrolü**. Hiçbir tarihsel iddia
  yalnızca skill'in kendi referans dosyalarından gelmemiştir; çıktıdaki
  her [D] etiketli iddia, en az bir **dış akademik kaynakla** (DergiPark
  makalesi, İSAM makalesi, basılı monograf, birincil arşiv) çapraz
  doğrulanmıştır. medical-history.md'deki [T] etiketli iddialar,
  çıktıya **yalnızca [T-doğrulanmamış] şerhi ile** girer; hiçbiri
  doğrudan iddia olarak sunulmaz.

### 5.3 G8 — TBMM Uygulanabilirliği Kapısı

- **G8.a**: Çıktı, TBMM İçtüzüğü m. 73-74 uyarınca "Genel Gerekçe –
  Tarihî Çerçeve" bölümüne doğrudan yerleştirilebilir formatta mı?
- **G8.b**: Her atıf, **TBMM atıf konvansiyonuna** uygun mu? (Resmî
  Gazete: *RG, S.[sayı], [gün/ay/yıl]*; TBMM ZC: *TBMM ZC, Devre,
  İçtima, Cilt, Birleşim, Sayfa*)
- **G8.c**: Modern hukuki belgeler (AYM kararı, Danıştay içtihatı) doğru
  formatta atıflandı mı? (*AYM, E.YYYY/SSS, K.YYYY/KKK*; *Danıştay [X].
  Daire, E.YYYY/SSS, K.YYYY/KKK*)
- **G8.d**: Çıktı, doğrudan kullanılabilir bir TBMM teklifi gerekçe
  bölümü mü? Yoksa hâlâ akademik bir tarih raporu mu? (Bu mod özellikle
  yasama-uygulanabilirlik üretmelidir.)

### 5.4 Mahir Bey'in Çalışma Vakası İçin Hazır Örnek (v1.2 — düzeltilmiş)

Mahir Bey'in **1219 sayılı Kanun reform teklifi** için tipik komut:

> *"KANUN_GEREKÇESİ modunda; konu: 1219 sayılı Tababet ve Şuabatı
> San'atlarının Tarz-ı İcrasına Dair Kanun'un modernleşme reform teklifi.
> L1'den L5'e tam zincir; L2'de 1861 Tabâbet-i Belediye Nizamnâmesi, L3'te
> 1871 İdâre-i Umûmiye-i Tıbbıye + Karantina Nizamnâmeleri, 1888 Memleket
> Etibbâsı Nizamnâmesi; L4'te 14 Nisan 1928 müzakere zaptı derinlemesine;
> 1908 sonrası dönem için [T-doğrulanmamış] etiketi ile boşluk; lex-sanitas
> için drafting altyapısı olarak kullanılabilir taslak."*

Bu komutta skill paralel olarak şu çağrıları yapar:

1. `devarsiv_search("tababet icrası", arsiv="2")`
   → BOA İrade/HAT/DH.* grubu — klasik–geç Osmanlı lâyiha/müzakere kayıtları
     (canlı resmî katalog, L1–L3 katmanlarının arşiv kanıtı)
2. `devarsiv_search("tababet icrası", arsiv="1")`
   → BCA 030.10 lâyiha/muamelat ve 030.18 Bakanlar Kurulu kararnameleri
     (erken Cumhuriyet, L4 katmanının arşiv kanıtı)
3. `ottoman_search_dspace("İcra-yı Tababet Şuabatı", repository="isam-makaleler")`
   → İSAM Makaleler Veri Tabanı (osmed, Belleten, OTAM)
4. `ottoman_search_iiif("Düstur Tertib Sani", sources=["loc","internet_archive"])`
   → LoC Hamid II Düstûr koleksiyonu (Birinci ve İkinci Tertib ciltleri
     IIIF erişimi)
5. `web_search("TBMM Zabıt Ceridesi 1219 müzakere Adnan Adıvar Refik Saydam")`
   → acikerisim.tbmm.gov.tr TBMM ZC Devre III, İçtima 1, C.6, B.65,
     14.4.1928 sayfaları
6. `web_fetch("https://www.mevzuat.gov.tr/mevzuatmetin/1.3.1219.pdf")`
   → 1219 sayılı Kanun konsolide metni (Madde 78 ilga zinciri verifikasyonu)
7. `search_yok_tez_detailed("1219 sayılı Kanun tıp hukuku tarihçe")`
   → Türk doktora tezleri
8. `${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/medical-history.md` paralel olarak yüklenir
   → [D] doğrulanmış zincir: 1861 → 1871 → 1888 → 1894 → 1928
   → [T] tartışmalı dönem: 1908–1922 (II. Meşrutiyet sonrası tababet
     yasaması)
9. `search_semantic("Ottoman medical regulation Tanzimat modernization comparative")`
   → uluslararası karşılaştırmalı literatür

Çıktı, doğrudan lex-sanitas'a beslenecek beş-katmanlı bir markdown
taslağıdır; **L3 (II. Meşrutiyet) katmanı için açık [T-boşluk] beyanı**
zorunlu olarak yer alır. G7 (G7.e dahil) ve G8 kapılarından geçtikten
sonra TBMM Sağlık, Aile, Çalışma ve Sosyal İşler Komisyonu'na
sunulabilir.
