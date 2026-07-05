# 5210 Uyum Denetimi — 21 Noktalı Kontrol Listesi (v2.0)

Bu liste, **COMPLY** modunda kullanılır. Her madde için **PASS / FAIL / N/A** + kısa gerekçe verilir.

v2.0 ile **iki yeni grup** eklendi:
- **Grup F (Kontrol 20):** AB Müktesebatı + Uluslararası Karşılaştırmalı Uyum
- **Grup G (Kontrol 21):** Türk Hukuk Dili + İçtihat-Doktrin Süzgeci (G-DİL)

## A. Maddi Uygunluk (Md. 4) — 8 Kontrol

### Kontrol 1: Üst Hukuk Normuna Uygunluk (Md. 4/a)
- [ ] **Taslak Anayasa'ya aykırı hüküm içeriyor mu?**
  - Sağlık için kontrol: Md. 13 (temel hak sınırlama), Md. 17 (yaşam hakkı), Md. 56 (sağlık hakkı), Md. 73 (vergi kanuniliği), Md. 124 (yönetmelik altlığı).
- [ ] **Taslak dayanak kanuna aykırı hüküm içeriyor mu?**
  - Mevzuat MCP doğrulaması: `get_mevzuat_content` ile dayanak kanun çekilir; yetki sınırı taranır.
- [ ] **Taslak CBK'ya aykırı hüküm içeriyor mu?**
  - 1 sayılı CBK md. 508 vd. (TİTCK görev alanı) taraması.

**FAIL örnekleri:**
- Yönetmelikte kanunda olmayan yeni ceza türü
- Tebliğde anayasal bir hakka kanuna dayanmadan sınırlama
- TİTCK Genelgesinde 1262 SK'da olmayan ürün kategorisi tanımı

### Kontrol 2: Düzenleme Amacına Uygunluk (Md. 4/b)
- [ ] **Taslak, kendi amaç maddesinin dışına çıkıyor mu?** (*ultra vires* testi)

**FAIL örneği:** Ruhsatlandırma yönetmeliği amaç maddesinde "ruhsat verme şartlarını düzenlemek" diyorsa, **fiyat belirleme hükmü** ultra vires'dir.

### Kontrol 3: Çoklu Kaynak Gözetimi (Md. 4/c)
- [ ] **Yargı kararları gözetildi mi?** Özellikle:
  - AYM içtihadı
  - Danıştay 10. Daire (sağlık), 13. Daire (idari yargı)
  - Yargıtay 13. HD (tüketici), 4. HD ve HGK (tıbbi malpraktis)
- [ ] **AB müktesebatı incelendi mi?**
  - Tıbbi cihaz: MDR (2017/745), IVDR (2017/746)
  - Klinik araştırma: CTR (536/2014)
  - İlaç: 2001/83/EC
- [ ] **Türkiye'nin taraf olduğu andlaşmalar gözetildi mi?**
  - AİHS, Oviedo, TRIPS

### Kontrol 4: Mevzuat Enflasyonu Temizliği (Md. 4/ç)
- [ ] **Çakışan/mükerrer hüküm var mı?**
  - `search_mevzuat` ile aynı konuda başka mevzuat var mı?
  - Varsa, eskileri yürürlükten kaldırılıyor mu?

**FAIL örneği:** SGK SUT'ta zaten yer alan bir geri ödeme kuralının ayrıca bir Genelgede daha düzenlenmesi.

### Kontrol 5: Tek Metin Bütünlüğü (Md. 4/d)
- [ ] **Çerçeve taslaklarda ana mevzuata işlenemeyecek "ekstra" madde var mı?**
- [ ] **Geçici madde sayılmayan ama esasa ilişkin "tek metin dışı" hüküm var mı?**

### Kontrol 6: Kapsam Maddesi Netliği (Md. 4/e)
- [ ] **Kapsam maddesi amaç maddesini tekrar ediyor mu?** (yasak)
- [ ] **Kapsam tereddütsüz mü?**

**FAIL örneği:**
- Amaç: "Beşeri tıbbi ürünlerin ruhsat şartlarını düzenlemek."
- Kapsam: "Bu Yönetmelik beşeri tıbbi ürünlerin ruhsat şartlarını kapsar." → **YASAK** (tekrar)
- DOĞRU kapsam: "Bu Yönetmelik beşeri tıbbi ürünlerin tam ruhsat, şartlı ruhsat ve acil kullanım ruhsatı başvuru sürecini kapsar; ileri tedavi tıbbi ürünleri (ATMP) hariçtir."

### Kontrol 7: Madde Kısalığı ve Sadeliği (Md. 4/f)
- [ ] **Madde metinleri kısa ve anlaşılır mı?**
- [ ] **Gereksiz ayraç içi açıklama var mı?**

**FAIL örneği:** "Ruhsat başvurusu (başvuru sahibi tarafından elektronik ortamda yapılır, ancak teknik aksaklık halinde fiziksel olarak da kabul edilebilir, bu durumda Kurum tarafından değerlendirilir, vb.) gerçekleştirilir."
- DOĞRU: Bu uzun ayraç → ayrı bir fıkra veya bent yapın.

### Kontrol 8: Çoklu Görev Alanında Mutabakat (Md. 4/g)
- [ ] **Birden fazla kurum etkileniyorsa mutabakat sağlandı mı?**
- [ ] **Görüş alma yazıları (Md. 6) eklendi mi?**

**FAIL örneği:** Yeni bir biyobenzer yönetmelik taslağı (TİTCK + SGK + SB ortak alan); sadece TİTCK hazırlamış, mutabakat yok.

## B. Şekli Uygunluk (Md. 10-22) — 6 Kontrol

### Kontrol 9: Gerekçeler Mevcut mu (Md. 10 + 23)?
- [ ] **Genel gerekçe var mı?**
- [ ] **(Kanun/CBK ise) madde gerekçeleri var mı?**
- [ ] **Madde gerekçesi madde metninin tekrarı şeklinde mi?** (yasak)

**FAIL örneği:**
- Madde 5/1 metni: "Ruhsat başvurusu elektronik ortamda yapılır."
- Madde 5 gerekçesi: "Bu madde, ruhsat başvurusunun elektronik ortamda yapılması esasını düzenlemektedir."
→ **FAIL** (tekrar). 
- DOĞRU gerekçe: "Madde, ÜTS entegrasyonu nedeniyle elektronik başvuru esasını getirmektedir. Eski paragraf düzeyinde fiziksel başvuru kalkmakta, fiziksel olarak başvurunun yalnızca teknik aksaklık halinde kabul edileceği hüküm altına alınmaktadır."

### Kontrol 10: Madde Sıralaması Md. 15'e Uygun mu?
- [ ] **Amaç → Kapsam → Dayanak → Tanımlar** ilk dört madde mi?
- [ ] **Yürürlük + Yürütme** son maddeler mi?
- [ ] **Geçici maddeler** yürürlük öncesi mi?

### Kontrol 11: MADDE Numaraları ve Tipografi (Md. 13)
- [ ] **MADDE kalın + büyük + bitişik kısa çizgi** formatında mı?
- [ ] **Madde altı çizilmemiş mi?**
- [ ] **Tanımlar maddesi alfabetik sırada mı?**
- [ ] **Fıkra `(1)`, bent `a)`, alt bent `1)` hiyerarşisi doğru mu?**

### Kontrol 12: Atıf Formatı (Md. 21)
- [ ] **İlk atıfta tarih + sayı + ad var mı?**
- [ ] **Tarihler `gün/ay/yıl` formatında ve soldaki sıfır YOK mu?**
- [ ] **Madde numaralarında kesme işareti yok mu?**
- [ ] **Türkçe ses uyumlu ek (`inci/ıncı/üncü`)?**
- [ ] **Fıkra atfı rakam yerine YAZI ile mi?**
- [ ] **Bent ve alt bent ayraç içinde mi?**
- [ ] **Geçmiş değişiklik bilgisi atıfta YOK mu?**

→ Detay için `references/03-atif-teknigi.md`

### Kontrol 13: Yürürlükten Kaldırma Açıklığı (Md. 21/8)
- [ ] **"Aykırı hükümler yürürlükten kaldırılmıştır" gibi muğlak ifade VAR mı?** (yasak)
- [ ] **Yürürlükten kaldırılan her hüküm açıkça gösterilmiş mi?**

### Kontrol 14: Değişiklik Tekniği (Md. 18-19)
- [ ] **Bir çerçeve madde tek bir mevzuatta mı değişiklik yapıyor?** (birden fazla → konu bağlantısı testi)
- [ ] **Değiştirilen metin tırnak içinde mi?**
- [ ] **Tırnak içinde cümle değişiklik için satırbaşı YOK mu?**
- [ ] **Çoklu değişiklikte eski tarihliden yeniye sıra var mı?**
- [ ] **Mahkeme kararı ile iptal edilmiş hükmün yeniden düzenlenmesinde açıkça belirtilmiş mi?**

## C. Dil ve Gerekçe (Md. 23, 25) — 2 Kontrol

### Kontrol 15: Madde Gerekçesi Kalitesi (Md. 23)
- [ ] **Madde metni tekrarı YOK mu?**
- [ ] **Sorun + amaç + neden bu çözüm açıklanmış mı?**
- [ ] **Geçiş süresi mantığı (varsa) gerekçelendirilmiş mi?**

### Kontrol 16: Dil Kuralları (Md. 25)
- [ ] **Sade + açık + anlaşılır mı?**
- [ ] **Türkçe karşılığı olan yabancı kelime VAR mı?** (yasak)
  - Örn: "compliance" yerine "uyum", "implementation" yerine "uygulama"
- [ ] **Zorunlu olmayan kısaltma VAR mı?**
- [ ] **"Yasa" kelimesi YOK mu?** ("Kanun" tercih)
- [ ] **TDK Yazım Kılavuzu kurallarına uyum?**

## D. Yetki ve Kanunilik (Md. 24) — 2 Kontrol

### Kontrol 17: Yönetmelik / Tebliğ / Genelge Yetki Sınırı (Md. 24)
- [ ] **Yönetmelik / tebliğ / genelge taslağında, dayanağında belirtilmemiş yeni yükümlülük VAR mı?** (yasak)
- [ ] **Yeni cezaî yaptırım VAR mı?** (yasak — sadece kanunla)
- [ ] **Yeni ücret kalemi VAR mı?** (yasak — sadece kanunla)
- [ ] **Yeni teşkilat birimi kurma VAR mı?** (yasak)
- [ ] **Kadro ihdas/iptal VAR mı?** (yasak)

**KRİTİK:** Bu kontrol noktası, Türk idari yargısında **en sık iptal gerekçesidir**. Anayasa Mahkemesi'nin yetki devri içtihadıyla doğrudan bağlantılıdır.

### Kontrol 18: Mali Yük Kanuniliği (Md. 24 + Anayasa Md. 73)
- [ ] **Mali yük doğuran her hüküm kanunî dayanağa sahip mi?**
- [ ] **Katkı payı / katılım payı / fark ücreti gibi mali yükler kanunî mi?**

**Önemli:** Anayasa Mahkemesi içtihadına göre, vergi-benzeri yükümlülükler kanunla düzenlenir (Md. 73). Sağlık alanında bu özellikle **katkı payı** ve **fark ücreti** tartışmalarında öne çıkar.

## E. Kalite Güvence (Md. 26-27) — 1 Kontrol

### Kontrol 19: DEA + BEF Mevcut mu?
- [ ] **(Kanun / CBK ise) DEA var mı?** (Md. 26 zorunlu)
- [ ] **Kamu mali yükü doğuruyorsa BEF var mı?** (Md. 27 zorunlu)
- [ ] **DEA + BEF yeterli derinlikte mi?**
- [ ] **Hesaplama varsayımları açık mı?**
- [ ] **Senaryo analizi yapılmış mı?**

## F. AB Müktesebatı ve Uluslararası Karşılaştırmalı Uyum — 1 Kontrol (v2.0)

### Kontrol 20: Karşılaştırmalı Uyum (Md. 4/c operasyonel yansıması)
- [ ] **AB müktesebatı uyum tablosu hazırlandı mı?** (alan harmonize ise — MDR/IVDR/CTR/GDPR/Falsified Medicines vb.)
- [ ] **EUR-Lex CELEX referansları konsolide sürümde mi?**
- [ ] **ABAD ilgili içtihatı kontrol edildi mi?** (curia.europa.eu)
- [ ] **ICH/PIC/S/IMDRF harmonize kılavuzları tutarlılığı belgelendi mi?**
- [ ] **En az iki AB üye devleti karşılaştırması yapıldı mı?** (varsayılan: Almanya + Fransa)
- [ ] **(Reliance konusu varsa) Singapur HSA + Avustralya TGA + İsviçre Swissmedic benchmark dahil mi?**
- [ ] **(HTA konusu varsa) NICE + G-BA/IQWiG + HAS + CADTH dörtlüsü dahil mi?**

## G. Türk Hukuk Dili ve İçtihat-Doktrin Süzgeci (G-DİL) — 1 Kontrol (v2.0)

### Kontrol 21: Dil + İçtihat + Uluslararası İnsan Hakları Süzgeci

**Türk hukuk dili (R9 Bölüm 9 — 15 noktalı kontrol):**
- [ ] **Tabaka seçimi tutarlı mı?** (modern alan → Tabaka C; klasik kanunda değişiklik → ana metin bütünlüğü)
- [ ] **5210 Md. 25 dil kuralları uygulanmış mı?** (yasa→kanun, yargıç→hâkim, yabancı kelime yasağı)
- [ ] **Md. 21 ses uyumu ekleri doğru mu?** (5 inci, 12 nci, 22 nci, 100 üncü)
- [ ] **"Olunur/edilir/yapılır" çekim seçimi anlamsal nüansa uygun mu?**
- [ ] **Anti-pattern cümleler temizlendi mi?** ("mümkün olabilir", "ilgili kişiler", "vs.", "online"...)
- [ ] **Tarih formatı 5210 Md. 21 uyumlu mu?** (sıfırsız, eğik çizgi)
- [ ] **Tanımlar maddesi Türkçe alfabe sırasında mı?** (a, b, c, ç, d...)
- [ ] **Latince terim minimumda mı?**
- [ ] **TDK + Resmî Mevzuat Bilgi Sistemi terim hiyerarşisi gözetildi mi?**

**Anayasa Md. 90/5 + Uluslararası İnsan Hakları Sözleşmeleri (R10):**
- [ ] **Sağlık hakkı boyutu varsa ICESCR Md. 12 + Genel Yorum 14 (AAAQ) kontrol edildi mi?**
- [ ] **Çocuk sağlığı boyutu varsa CRC Md. 24 + Genel Yorum 15 kontrol edildi mi?**
- [ ] **Engelli sağlığı boyutu varsa CRPD Md. 25 kontrol edildi mi?**
- [ ] **Kadın/üreme sağlığı boyutu varsa CEDAW Md. 12 + Genel Tavsiye 24 kontrol edildi mi?**
- [ ] **Klinik araştırma boyutu varsa Helsinki Bildirgesi 2024 + CIOMS 2016 + Oviedo Sözleşmesi kontrol edildi mi?**

**WHO Operasyonel Rejim (R11):**
- [ ] **Pandemi/halk sağlığı boyutu varsa IHR 2005 + 2024 değişiklikleri + Pandemic Agreement 2025 kontrol edildi mi?**
- [ ] **İlaç/cihaz boyutu varsa WHO Reliance/WLA/CRP framework kontrol edildi mi?**
- [ ] **Sınıflandırma boyutu varsa ICD-11 + ATC/DDD uyumu kontrol edildi mi?**
- [ ] **Tütün kontrolü boyutu varsa FCTC + 4207 SK paraleli kontrol edildi mi?**

**Türk Yargı İçtihatı + Akademik Doktrin (R13):**
- [ ] **AYM bireysel başvuru içtihatı tarandı mı?** (Hukuki Veritabanları MCP)
- [ ] **AYM norm denetimi içtihatı tarandı mı?** (varsa benzer iptal kararları)
- [ ] **Danıştay 10. / 13. / 15. D. içtihatı tarandı mı?**
- [ ] **Yargıtay 11. / 13. HD içtihatı tarandı mı?** (konu özel hukuk boyutu varsa)
- [ ] **AİHM Türkiye kararları kontrol edildi mi?** (Mehmet Şentürk, Asiye Genç, vd. — varsa benzer emsaller)
- [ ] **ABAD paralel kararları kontrol edildi mi?** (AB uyumu boyutu varsa)
- [ ] **YokTez tarama yapıldı mı?** (son 5 yıl DOKTORA + YÜKSEK LİSANS)
- [ ] **Türk hukuk doktrini atfı yapıldı mı?** (Hakeri, Aydın, Yıldız, Gökcan, Demir vd. — konu kapsamında)

**Karşılaştırmalı Yargı Yetkisi (R12 + COMPARATIVE_LAW modu):**
- [ ] **Karşılaştırılan ülke seçim gerekçesi açık mı?** (R12 Bölüm 9 kriterleri)
- [ ] **Yargı bölgesi seçimi konu tipine uygun mu?** (yeni etken madde → EMA+FDA; biyobenzer → EMA+WHO BTS; klinik araştırma → EU CTR+ICH; HTA → NICE+G-BA+HAS; vd.)

## Skor ve Risk Değerlendirmesi (v2.0)

| FAIL sayısı | Risk düzeyi | Aksiyon |
|-------------|-------------|---------|
| 0 | YEŞİL | Cumhurbaşkanlığına sunulabilir |
| 1-3 | SARI | Şekli düzeltmelerle hazır |
| 4-8 | TURUNCU | Önemli revizyon gerekli |
| 9+ | KIRMIZI | Esastan yeniden hazırlanmalı |

**KRİTİK ÇIKARSAMA (v2.0):**
- Kontrol **1, 2, 17, 18** FAIL ise → **kırmızı bayrak** (Danıştay iptal riski yüksek).
- Kontrol **12, 13** FAIL ise → şekli FAIL, kolayca düzeltilir.
- Kontrol **19** FAIL ise → Cumhurbaşkanlığı iadesi (Md. 9/5).
- Kontrol **20** FAIL ise (AB müktesebatı uyumsuzluğu) → AB Başkanlığı görüşünde **olumsuz** geri dönüş riski; aday ülke statüsü açısından politik risk.
- Kontrol **21 (G-DİL)** FAIL ise → metin **Lex-Sanitas kalite eşiğinin altında**; yeniden yazım gerekir. Özellikle Anayasa Md. 90/5 uyumu (ICESCR/CRC/CRPD) FAIL ise **AYM bireysel başvuru zafiyeti**; AİHM ihlal riski.

## Rapor Formatı (COMPLY çıktısı)

```markdown
# [Taslak Adı] — 5210 Uyum Denetimi Raporu

## Yönetici Özeti
- Toplam kontrol noktası: 19
- PASS: X
- FAIL: Y
- N/A: Z
- Risk düzeyi: [YEŞİL/SARI/TURUNCU/KIRMIZI]

## A. Maddi Uygunluk
### Kontrol 1: ... [PASS/FAIL/N/A]
**Bulgu:** ...
**Gerekçe:** ...
**Düzeltme önerisi (FAIL ise):** ...

[devamı...]

## Öncelikli Düzeltme Listesi
1. (Kontrol N) ...
2. ...

## Tavsiye
Bu taslağın Cumhurbaşkanlığına sunulmadan önce [şu] revizyonların yapılması gerekmektedir.
```
