# Bütçe Etki Formu (BEF) — EK-3 Şablonu

5210 sayılı Yönetmelik **Md. 27** ve **EK-3** uyarınca; **kamu gelirlerini azaltacak**, **kamu giderlerini artıracak** veya **kamu idarelerini yükümlülük altına sokacak** her taslak için doldurulması zorunlu olan formdur.

> **Md. 27/3:** Görüş süreci sonrası taslak değişirse, BEF de **güncellenerek nihaî hâli** verilir. Cumhurbaşkanlığına gönderilen pakette yer alacak BEF, taslağın son hâline uygun olmalıdır.

> **Not:** BEF, DEA'dan **dar kapsamlıdır** — yalnızca **doğrudan mali etki** üzerine odaklanır. DEA ise tüm etki kategorilerini içerir; sağlık taslaklarında genellikle BEF, DEA'nın mali etki bölümünden türetilir.

---

## BEF — EK-3 Standart Formu

```
T.C.
{{KURUM ADI}}
{{BİRİM ADI}}

BÜTÇE ETKİ FORMU (BEF)

1. TASLAĞIN KÜNYESİ
   Adı            : {{...}}
   Türü           : {{Kanun / CBK / Yönetmelik / Tebliğ / Karar}}
   Hazırlık Tarihi: {{gün/ay/yıl}}
   Sorumlu Birim  : {{...}}
   İletişim       : {{Ad-soyad, e-posta, telefon}}

2. DÜZENLEMENİN HEDEFLERİ
   {{2-3 cümle ile düzenlemenin amacı}}

3. ETKİLENECEK TARAFLAR
   3.1 Kamu İdareleri
       □ Genel Bütçe Kapsamındaki İdareler — {{liste}}
       □ Özel Bütçeli İdareler — {{liste}}
       □ Düzenleyici ve Denetleyici Kurumlar — {{TİTCK, SEDDK, vb.}}
       □ Sosyal Güvenlik Kurumları — SGK
       □ Mahalli İdareler — {{varsa}}
       □ Diğer — {{...}}
   3.2 Özel Sektör — {{...}}
   3.3 Vatandaş/Hastalar — {{...}}
```

### 4. Mali Etki Detayı

**4.1 İlave Kamu Gideri**

| Gider Kalemi | Yıl 1 (TRY) | Yıl 2 | Yıl 3 | Yıl 4 | Yıl 5 | 5-Yıl Toplam |
|---|---|---|---|---|---|---|
| Personel | | | | | | |
| Yatırım (donanım/yazılım) | | | | | | |
| Cari (kira, kırtasiye, vb.) | | | | | | |
| Transfer (geri ödeme, sübvansiyon) | | | | | | |
| Hizmet alımı | | | | | | |
| Diğer | | | | | | |
| **TOPLAM İLAVE GİDER** | | | | | | |

**4.2 İlave Kamu Geliri**

| Gelir Kalemi | Yıl 1 (TRY) | Yıl 2 | Yıl 3 | Yıl 4 | Yıl 5 | 5-Yıl Toplam |
|---|---|---|---|---|---|---|
| Vergi geliri | | | | | | |
| Ruhsat/lisans ücretleri | | | | | | |
| Para cezaları | | | | | | |
| Hizmet bedelleri | | | | | | |
| Diğer | | | | | | |
| **TOPLAM İLAVE GELİR** | | | | | | |

**4.3 Vazgeçilen Gelir / Yapılan Tasarruf**

| Kalem | Yıl 1 | Yıl 2 | Yıl 3 | Yıl 4 | Yıl 5 | 5-Yıl Toplam |
|---|---|---|---|---|---|---|
| Vergi muafiyeti/istisnası | | | | | | |
| Gümrük muafiyeti | | | | | | |
| Diğer vazgeçilen gelir | | | | | | |
| **Toplam vazgeçilen gelir** | | | | | | |
| Tasarruf (gider azaltıcı etki) | | | | | | |

**4.4 Net Bütçe Etkisi**

| Hesap | Yıl 1 | Yıl 2 | Yıl 3 | Yıl 4 | Yıl 5 | 5-Yıl Toplam |
|---|---|---|---|---|---|---|
| İlave gelir – İlave gider | | | | | | |
| – Vazgeçilen gelir | | | | | | |
| + Tasarruf | | | | | | |
| **NET ETKİ** | | | | | | |

> **Renk kodu:** Negatif rakamlar (bütçe yükü) **(-)** ile, pozitif rakamlar (+) olarak gösterilir.

---

### 5. Hesaplama Varsayımları

```
Bu BEF'in dayandığı temel varsayımlar:

V1. Enflasyon oranı : %{{...}} (TCMB Beklenti Anketi {{ay/yıl}}
                                ortalaması)
V2. Döviz kuru       : {{USD/EUR/TRY oranı + tarih}}
V3. Pazar büyüklüğü  : {{baz}} (Kaynak: IQVIA / TİTCK / SGK)
V4. Etkilenen birim sayısı: {{adet}} (Kaynak: {{...}})
V5. Birim maliyet     : {{TRY}} (Kaynak: {{...}})
V6. Adoption hızı     : %{{Yıl 1}}, %{{Yıl 2}}, %{{Yıl 3}}
                       (varsayım dayanağı: {{...}})
V7. Geri ödeme oranı  : %{{...}} (SUT EK-4/A bazında)
```

### 6. Senaryo Analizi (Sensitivity Analysis)

| Parametre | Baz Değer | Düşük | Yüksek | 5-yıl etki aralığı |
|---|---|---|---|---|
| Adoption hızı | %{{x}} | %{{x-10}} | %{{x+10}} | {{TRY aralık}} |
| Birim maliyet | {{TRY}} | -%15 | +%15 | {{TRY aralık}} |
| Pazar büyümesi | %{{y}} | %{{y-2}} | %{{y+2}} | {{TRY aralık}} |

---

### 7. Karşılama Kaynağı

```
Bu düzenlemeden kaynaklanan ilave bütçe yükünün karşılanması:

□ Mevcut bütçe ödeneklerinden — {{tertip + tutar}}
□ Yeni ödenek ihtiyacı — {{tertip + tutar}} → {{kaynağı}}
□ Yeni gelir yaratıcı önlem — {{...}}
□ Tasarruf öngörüsü — {{kalemde + tutar}}

Hazine ve Maliye Bakanlığı görüşü: {{tarih/sayı + öz}}
Strateji ve Bütçe Başkanlığı görüşü: {{tarih/sayı + öz}}
```

---

### 8. İmzalar

```
Hazırlayan:        {{Ad-soyad, unvan, imza, tarih}}
Birim Amiri:       {{Ad-soyad, unvan, imza, tarih}}
Mali Hizmetler:    {{Ad-soyad, unvan, imza, tarih}}
Kurum Yetkilisi:   {{Ad-soyad, unvan, imza, tarih}}
```

---

## Sağlık Mevzuatında Tipik BEF Senaryoları

### Senaryo 1 — Yeni İlacın SUT EK-4/A'ya Eklenmesi

Bu en sık karşılaşılan senaryodur. Hesaplama temel mantığı:

```
İlave SGK gideri =
  (Yıllık hasta sayısı) × (Yıllık tedavi maliyeti) ×
  (Reçete edilebilme uyum oranı) × (Geri ödeme oranı)

Örnek (Trastuzumab deruxtecan, HER2+ metastatik meme):
  Hasta sayısı (yıllık, eligible)    : ~3,500
  Yıllık tedavi maliyeti (KDV dahil) : 850,000 TRY
  Reçete uyumu                       : %70
  Geri ödeme oranı                   : %80
  → Yıllık SGK gideri = 3,500 × 850,000 × 0,70 × 0,80
                     = ~1,666,000,000 TRY
```

> **Mahsuplaştırma:** Yeni ilaç bir önceki tedavi standardını ikame ediyorsa, **vazgeçilen mevcut tedavi gideri** mahsup edilmelidir. Net gider artışı bu mahsuplaşmadan sonra hesaplanır.

### Senaryo 2 — Yeni Ruhsat Ücreti İhdası

```
İlave TİTCK geliri =
  (Yıllık yeni ruhsat başvuru sayısı) × (Ücret) +
  (Yıllık ruhsat yenileme sayısı) × (Yenileme ücreti) +
  (Yıllık varyasyon sayısı) × (Varyasyon ücreti)
```

> **Md. 24 Uyarısı:** Yönetmelikte yeni ücret kalemi ihdas edilemez. Ancak yönetmelikle ücret miktarı dayanak kanun çerçevesinde belirlenebilir veya değiştirilebilir. Yeni ücret kalemi için **kanun değişikliği** gereklidir.

### Senaryo 3 — Sağlık Hizmeti Bedeli Değişikliği

```
SGK gider değişimi =
  Σ (Hizmet kodu hacmi × (Yeni bedel - Eski bedel))

Örnek: Belirli bir CPT/SUT kodunun bedelinin artırılması:
  Hizmet kodu     : XXX.YYY (örn. genetik test)
  Yıllık hacim    : 50,000
  Eski bedel      : 2,000 TRY
  Yeni bedel      : 3,500 TRY
  Artış per işlem : 1,500 TRY
  Yıllık ek yük   : 75,000,000 TRY
```

### Senaryo 4 — Mali Etki "Sıfır" Durumu

Bazı düzenlemeler **doğrudan mali etki yaratmaz** (örn. tanım maddesi güncellemesi, atıf düzeltmesi). Bu durumda BEF basitleştirilmiş şekilde hazırlanır:

```
3. ETKİLENECEK TARAFLAR: Yok (idari bildirim/güncelleme)
4.1 İlave Gider     : 0 TRY
4.2 İlave Gelir     : 0 TRY
4.4 Net Bütçe Etkisi: 0 TRY

Bu düzenleme yalnızca {{idari düzeltme/tanım güncelleme}} amacı
taşımakta olup doğrudan mali etki içermemektedir. Yönetmelik
Md. 27 anlamında BEF hazırlanması zorunluluğu doğmadığından bu
form bilgi amaçlı sunulmaktadır.
```

---

## BEF Doğrulama Listesi

- [ ] Form **EK-3 standart başlığı** ile mi sunuldu?
- [ ] 5 yıllık projeksiyon tamamlandı mı?
- [ ] Tüm rakam hücreleri **doldurulu mu** (boş kalan varsa "—" işareti konuldu mu)?
- [ ] Varsayımlar **kaynak gösterilerek** belirtildi mi?
- [ ] Senaryo analizi yapıldı mı?
- [ ] **Mahsup kalemleri** (vazgeçilen mevcut tedavi/hizmet) dikkate alındı mı?
- [ ] Karşılama kaynağı belirtildi mi?
- [ ] Hazine + SBB görüşü alındı mı? (Md. 6/2)
- [ ] **Md. 27/3** uyarınca taslak güncellenince BEF de güncellendi mi?
- [ ] BEF imzaları **tam ve doğru hiyerarşi**de mi?

---

## BEF ve DEA İlişkisi

BEF, DEA'nın **dar bir alt kümesidir**. İlişki:

| Belge | Kapsam | Ne Zaman Zorunlu? |
|---|---|---|
| DEA (Md. 26) | Tüm etkiler (ekonomik + sosyal + çevresel + idari + AB uyumu + KPI + risk) | Kanun ve CBK için |
| BEF (Md. 27) | Sadece doğrudan mali etki | Kamu geliri azaltıcı / gider artırıcı / yükümlülük getirici her taslak için |

Pratik öneri: Önce **DEA'nın mali etki bölümünü** doldurun; oradaki tabloları BEF'e taşıyın. Bu yaklaşım iki belge arasında tutarlılığı garanti eder.
