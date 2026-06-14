# references/fto-invalidity-protokol.md — FTO ve Invalidity İş Akışı Protokolü

> FTO ve Invalidity, pharmapatent skill'inin **operasyonel çekirdeğidir**. Her iki iş akışı aynı arama araçlarını kullanır ancak farklı sorular sorar: FTO "serbest miyim?", Invalidity "bu patenti çürütebilir miyim?". Her ikisi de **sistematik** olmalı; atlanan tek adım dava önünde eksik çıkan kanıt demektir.

## İlişkili Protokoller

- **`cpc-ipc-kodlari.md`** — §1 Adım 4'te CPC kilit listesi çıkarma ve Adım 5'te sınıf tabanlı patent genişletmesi için hiyerarşi
- **`markush-protokol.md`** — §1 Adım 6 + §2 Adım 6'da kimyasal yapısal arama ve Markush kapsam analizi metodolojisi
- **`veritabani-stratejileri.md`** — Tüm adımlarda çoklu veri tabanı triangülasyonu (Orange Book + Espacenet + USPTO + EPAAT + WIPO)
- **`ictihat-emsal.md`** — §2 Adım 11'de argüman güvenilirliği derecelendirmesinde Yargıtay 11. HD eğilimleri ve EPO G-kararları
- **`smk-6769-ilac.md`** — Hükümsüzlük gerekçelerinin (m.138) hukuki çerçevesi + Bolar istisnası (m.85/3)
- **`rapor-sablonlari.md` §1-§2 + §8`** — FTO Raporu, Invalidity Briefing ve Opposition Briefing çıktı şablonları
- **`yeni-modaliteler.md`** [v1.2.0] — ADC, CAR-T, mRNA-LNP, gene therapy için FTO iş akışının modalite-spesifik uyarlaması
- **`patent-degerleme.md`** [v1.2.0] — Hükümsüzlük olasılığının değerleme üzerindeki discount etkisi
- **`../domains/onkoloji-ip.md`** [v1.4.0] — Onkoloji-spesifik FTO + invalidity senaryoları (ICI + ADC + CAR-T + bispecific)
- **`../domains/hematoloji-ip.md`** [v1.4.0] — Hematoloji-spesifik FTO + invalidity (Roche malignant hematology alanı)
- **`../domains/immunoloji-ip.md`** [v1.5.0] — İmmunoloji-spesifik FTO + invalidity (TNF-α biyobenzer, IL ailesi, JAK/TYK2)
- **`../domains/noroloji-ip.md`** [v1.5.0] — Nöroloji-spesifik FTO + invalidity (MS, Alzheimer anti-amiloid, CGRP)
- **`../domains/enfeksiyon-ip.md`** [v1.5.0] — Enfeksiyon-spesifik FTO + invalidity (antibiyotik, HIV, HCV, mRNA)
- **`../domains/kardiyoloji-ip.md`** [v1.6.0] — Kardiyoloji-spesifik FTO + invalidity (PCSK9, Factor XI, SGLT-2, Lp(a), ATTR)
- **`../domains/metabolik-ip.md`** [v1.6.0] — Metabolik-spesifik FTO + invalidity (GLP-1, MASH, KOAH, obezite)
- **`../domains/oftalmoloji-ip.md`** [v1.6.0] — Oftalmoloji-spesifik FTO + invalidity (anti-VEGF, retinal gene therapy, GA)
- **`../domains/dermatoloji-ip.md`** [v1.6.0] — Dermatoloji-spesifik FTO + invalidity (psöriazis, AD, JAK alopesi, vitiligo)
- **`../domains/psikiyatri-ip.md`** [v1.7.0] — Psikiyatri-spesifik FTO + invalidity (M1/M4 muskarinik Cobenfy, psikedelik, hızlı etki MDD)

## İçindekiler

1. FTO (Faaliyet Serbestisi) — 9 adım iş akışı
2. Invalidity (Hükümsüzlük) — 11 adım iş akışı
3. Ortak araçlar ve kaynaklar matrisi
4. Özellik-özellik analiz matrisi şablonu
5. Mozaik tablosu şablonu
6. Karar ağacı
7. Sık düşülen tuzaklar ve bunlardan kaçınma
8. Raporun kalite denetimi (peer review checklist)

---

## 1. FTO (Faaliyet Serbestisi) — 9 adım iş akışı

### Adım 1 — Ürün profilini kilitle

**Girdiler**:
- INN, CAS numarası, SMILES, InChI (küçük molekül için)
- Amino asit sekansı, glikozilasyon paterni (biyolojikler için)
- Aktif madde + eksipiyanlar tam listesi
- Dozaj formu (tablet, kapsül, enjeksiyon, inhaler, vb.)
- Konsantrasyon, doz, uygulama yolu
- Hedef endikasyon (ler)
- Uygulama cihazı (varsa)
- Üretim süreci (kritik adımlar)
- Hedef pazar (TR, AB, ABD, ROW)
- Planlanan pazara arz tarihi

**Çıktı**: 1-2 sayfalık **Ürün Teknik Özeti**; her özellik "anahtar kelime" havuzunun parçası olur.

### Adım 2 — Kavramsal haritalama (eşanlamlı havuzu)

Her teknik özelliği için alternatif terimleri listele:
- Aktif madde: INN + ticari marka + CAS + eşanlamlılar + kimyasal ad + SMILES
- Dozaj formu: "tablet, tablete, tableta, formülasyon..."
- Mekanizma: reseptör, enzim, sinyal yolu
- Endikasyon: hastalık adları (TR/EN/ICD kodu/MeSH)

**Çıktı**: **Eşanlamlı Matrisi** (Excel veya markdown tablo).

### Adım 3 — Öncül Boolean sorgusu (çekirdek set)

**Hedef**: 50-200 yüksek alaka belgesi.

**Sorgu örnekleri**:

USPTO:
```
(atorvastatin OR "4-fluorophenyl-hydroxy-calcium").CLM. AND CPC/A61K9/20.CPC.
```

Espacenet:
```
ta="atorvastatin" AND cpc=A61K9/20 AND pd>20050101
```

**Sınırlama**: Yayın tarihi filtresi — pazar giriş tarihinizden 20-25 yıl öncesi başlayabilir (en eski potansiyel aktif patent için yeterli).

### Adım 4 — Kod çıkarımı

Çekirdek setin her belgesinin:
- CPC kodları (tüm atanmışlar)
- IPC kodları
- Başvuru sahibi (assignee)
- İlk başvuru tarihi
listelenir. En sık görülen CPC kodları **radar sınıfı** olur.

**Çıktı**: **CPC Kilit Listesi** — bu kodlar Adım 5'te kullanılacak.

### Adım 5 — Sınıf tabanlı genişletme

Adım 4'te tespit edilen CPC kodları için anahtar kelime olmaksızın sorgu:

```
USPTO:
CPC/A61K9/20.CPC. AND CPC/A61K31/40.CPC.

Espacenet:
cpc=A61K9/20 AND cpc=A61K31/40
```

Bu sorgu **binlerce** belge döndürebilir. Bu belgeler:
- Başvuru sahibine göre gruplandırılır
- Assignee Top 20'si ayrıca incelenir
- Her major assignee için Markush istemleri aranır

**Çıktı**: **Genişletilmiş Belge Seti** (500-5000 belge).

### Adım 6 — Kimyasal yapısal arama (küçük moleküller için)

**SureChEMBL** veya profesyonel (SciFinder/Derwent) ile:
- Hedef molekülün çekirdek yapısı ≥80% benzerlik arar
- Markush formülü kapsam analizi yapar (profesyonel araç gerekir)
- Tuz, ester, izomer, polimorf varyantları ayrıca aranır

**Çıktı**: **Kimyasal Risk Haritası** — spesifik patent referansları ile.

### Adım 7 — İstem-bazlı FTO analizi

Adım 3-6'da biriken aktif patentlerin her biri için:

1. Bağımsız istemleri oku
2. Özellik-özellik eşleştirme (bkz. Bölüm 4)
3. Hedef ürünün her özelliği istem kapsamına giriyor mu?
4. Doktrinel eşdeğer (aynı işlevi başka yöntemle) risk analizi
5. Patent geçerlilik durumunu doğrula (yıllık harç ödeme, yeniden tescil)
6. Coğrafi kapsam (Türkiye'de aktif mi?)

**Risk seviyeleri**:
- **Kritik**: Doğrudan ihlal, kaçınılamaz
- **Yüksek**: Doktrinel eşdeğer ile ihlal
- **Orta**: Bazı özelliklerde eşleşme, diğerlerinde değil; tarafsız yorum olası
- **Düşük**: Teorik risk var ama pratikte kapsam dışı
- **Temiz**: Kapsam net dışı

**Çıktı**: **Patent-Risk Tablosu**.

### Adım 8 — Design-around simülasyonu (kritik/yüksek risk için)

İhlal riski tespit edilen her patent için:

1. İstemdeki hangi spesifik element engel yaratıyor?
2. Bu element nasıl değiştirilebilir?
   - Farklı eksipiyan kombinasyonu
   - Farklı dozaj formu (tabletten kapsüle)
   - Farklı uygulama cihazı
   - Farklı üretim süreci
3. Değişiklik FDA/EMA/TİTCK bioeşdeğerlik için kabul edilebilir mi?
4. Değişiklik kendi FTO sorunu yaratır mı?

**Çıktı**: **Design-Around Önerileri**.

### Adım 9 — Rezidüel risk beyanı ve rapor

Son rapor:
1. Tespit edilen aktif patentler + risk seviyeleri
2. Design-around önerileri
3. **Rezidüel risk beyanı** — tespit edilemeyen riskler:
   - Pending başvurular (henüz yayımlanmamış olanlar)
   - Terk edilmiş ancak kamu malı olmamış başvurular
   - Dil sınırı nedeniyle taranmayan ülkeler
   - Markush analizinin profesyonel araçsız eksikliği
4. Epistemik sınırlar (ne bilmiyoruz)
5. Öneriler (sonraki adımlar)

**Çıktı**: **FTO Raporu** (Carbon HTML veya docx formatında — `rapor-sablonlari.md §1`).

---

## 2. Invalidity (Hükümsüzlük) — 11 adım iş akışı

### Adım 1 — Hedef patent profilini çıkar

**Girdiler**:
- Patent numarası (TR, EP, US, WO)
- Başvuru tarihi + öncelik tarihi (kritik!)
- Yayın tarihi
- Granted tarihi
- Tescil durumu (aktif/yıllık harç)
- Başvuru sahibi ve mucit listesi

**Öncelik tarihi** kilit veri: Prior art araması bu tarihten **öncesine** odaklanacaktır.

### Adım 2 — Saldırılacak istemleri belirle

Müvekkilin öncelikli pazar giriş engeli hangi istemlerdir? Genellikle:
- Bağımsız istem 1 (ana koruma kapsamı)
- Spesifik formülasyon istemleri (jenerik rakip için)
- İkinci tıbbi kullanım istemleri (endikasyon çakışması için)

**Çıktı**: **Hedef İstem Listesi** — önceliklendirmeli.

### Adım 3 — Özellik-özellik çıkarma

Her hedef istemin teknik özelliklerini ayrıştır:

Örnek istem:
> "Bir farmasötik formülasyon, X aktif maddesi (%30-50 ağırlık), mikrokristalin selüloz (%20-40), kolloidal silika (%1-5) içeren ve tablet formunda olan."

Özellik listesi:
- F1: Tablet formu
- F2: X aktif maddesi
- F3: X konsantrasyonu %30-50
- F4: Mikrokristalin selüloz (%20-40)
- F5: Kolloidal silika (%1-5)

**Çıktı**: **Özellik Matrisi** — her istem için.

### Adım 4 — Öncelik tarihi öncesi patent prior art

Öncelik tarihinden önceki **patent** yayınlarını tara:
- Aynı veya benzer molekülü tanımlayan patentler
- Aynı formülasyon bileşenlerini tanımlayan patentler
- Aynı dozaj formunu tanımlayan patentler

**Araçlar**: USPTO, Espacenet, WIPO PATENTSCOPE, TÜRKPATENT EPAAT, SciFinder.

**Çıktı**: **Patent Prior Art Seti** — her özellik için adaylar.

### Adım 5 — NPL (non-patent literature) prior art

**PubMed + Google Scholar + bioRxiv + medRxiv + YÖK Tez + ClinicalTrials.gov**:
- Hakemli makaleler
- Konferans bildirileri (abstract)
- Tezler
- Klinik çalışma kayıtları (tarih bilgisi delil)
- Patent başvuru sahibinin kendi önceki yayınları

`medsearch` skill composability: PubMed sistematik araması + Scholar Gateway + Consensus + Paper Search entegre.

**Çıktı**: **NPL Prior Art Seti**.

### Adım 6 — Kimyasal Markush prior art

**Kritik soru**: Hedef patentin bileşiği daha önce geniş bir Markush formülü içinde **örtülü olarak açıklanmış** mı?

**Araç**: SciFinder / STN IP Protection Suite (ücretli). SureChEMBL kısmi.

**Ana doktrin**: EPO G 2/88 — "bilinen bir genus, spesifik türü de açıklar" ya da açıklamaz? EPO'nun son içtihadına göre, jenerik Markush formülü **o formül içindeki her spesifik bileşiği** önceden açıklanmış saymak için yeterli **değildir** (unless formül içindeki spesifik örnekler veriliyor veya dar bir grup açıklanıyorsa).

**Çıktı**: **Markush-Based Prior Art Analizi**.

### Adım 7 — Yenilik analizi (novelty attack)

**Tek bir prior art belgesi** hedef istemin **tüm özelliklerini** ortaya koyuyorsa → yenilik yoktur.

**Test**:
- F1, F2, F3, F4, F5 hepsi tek bir prior art belgesinde (yayım tarihi < öncelik tarihi) var mı?

**Sonuç**: Tam eşleşme → güçlü yenilik hükümsüzlüğü argümanı.

**Kısmi eşleşme** → yenilik yok ama buluş basamağı değerlendirmeye devam.

### Adım 8 — Buluş basamağı analizi (inventive step / obviousness attack)

Türkiye ve EPO "Problem-Solution Approach":
1. **En yakın prior art** (closest prior art) tespit edilir — hedef patent ile en benzer olan
2. **Teknik farklılık** saptanır — hedef patent ile en yakın prior art arasındaki farklar
3. **Objektif teknik problem** tanımlanır — farkın çözdüğü problem
4. **Ortalama uzman** problem çözümüne sahip önceki tekniği (closest prior art + ikincil referanslar + genel bilgi) kullanarak çözüme ulaşabilir miydi?
5. Evet ise → buluş basamağı yoktur (aşikâr).

**Mozaik**: Birden fazla prior art belgesinin kombinasyonu ile yapılan argüman. Ancak "hindsight" (geriye dönük akıl yürütme) tuzağına düşmemek için:
- Kombinasyonun *motivasyonu* (neden iki belgeyi birleştireyim?) gösterilmeli
- Kombinasyonun *olası sonucu* hedef patente varmalı

**Çıktı**: **Mozaik Tablosu** — hangi prior art belgesi hangi özelliği karşılıyor.

### Adım 9 — Yeterli açıklama (sufficiency of disclosure) analizi

SMK m. 92/1 — istemler tarifname tarafından desteklenmelidir.

**Test**:
- Patent tarifnamesi tüm istem kapsamını destekliyor mu?
- Örnek sayısı yeterli mi? (Çok geniş Markush + az örnek → yetersiz destek)
- Ortalama uzman, tarifname ile buluşu tekrar edebilir mi?
- "Gereksiz deneme yükü" (undue burden) var mı?

### Adım 10 — Diğer hükümsüzlük gerekçeleri

- **Sanayiye uygulanabilirlik** — pratik uygulanabilirlik gösterilmiş mi?
- **Patent verilemeyecek konu** — tedavi usulü gibi yasaklı konulara mı giriyor?
- **Hak sahipliği** — doğru mucit ve başvuru sahibi mi?
- **Çift patent** — aynı mucitin aynı konuda başka patenti var mı (Terminal Disclaimer gerekliliği)?

### Adım 11 — Strateji ve atak vektörü önceliklendirmesi

Her argüman ailesi için güvenilirlik derecelendirmesi:
- **Strong**: Açık delil + net doktrin desteği
- **Moderate**: Delil var ama yoruma açık
- **Weak**: Çürüğe meyilli argüman
- **Speculative**: Sadece olasılık

**Forum seçimi**:
- **FSHHM hükümsüzlük davası** — Türkiye için en güçlü argümanlar
- **TÜRKPATENT YİDK itirazı** — 2 ay süresi varsa (ret kararına karşı)
- **EPO opposition** — EP patenti için 9 ay içinde
- **Üçüncü kişi görüşü** — yayımlanmış başvuru için süre sınırsız
- **Çok-forum strateji** — aynı anda birden fazla forum

**Çıktı**: **Invalidity Briefing** (`rapor-sablonlari.md §2`) — argüman aileleri, atak vektörü önceliklendirmesi, forum stratejisi.

---

## 3. Ortak araçlar ve kaynaklar matrisi

### FTO ve Invalidity için ortak araçlar

| Araç | FTO | Invalidity | Notlar |
|---|---|---|---|
| USPTO Patent Public Search | ✓ | ✓ | ABD patentleri tam metin |
| Espacenet | ✓ | ✓ | Küresel + INPADOC family |
| WIPO PATENTSCOPE | ✓ | ✓ | PCT + ulusal fazlar |
| TÜRKPATENT EPAAT | ✓ (TR) | ✓ (TR) | Türkiye'de geçerlilik |
| Orange Book | ✓ | ✓ | ABD referans patentleri |
| Purple Book | ✓ | — | ABD biyolojikler |
| SureChEMBL | ✓ | ✓ | Ücretsiz kimyasal arama |
| SciFinder / STN | ✓ | ✓ | Kritik; ücretli |
| PubMed | — | ✓ | NPL prior art için kritik |
| Google Scholar | — | ✓ | NPL — akademik + teknik |
| bioRxiv / medRxiv | — | ✓ | Preprint NPL |
| YÖK Tez | — | ✓ (TR) | Türk akademik tezler |
| ClinicalTrials.gov | — | ✓ | Klinik kayıt delili |

### Composability — diğer skill'lerle

- `pharmaintel` → Orange/Purple Book hızlı sorgu, şirket pipeline, 10-K dosyaları
- `medsearch` → NPL sistematik literatür taraması (Invalidity için kritik)
- `carbon-html-report` → FTO/Invalidity raporu üretimi
- `carbon-pptx` → yönetim briefing slaytları
- `docx` → dava dilekçesi (hükümsüzlük davası talep metni)

---

## 4. Özellik-özellik analiz matrisi şablonu

Örnek matris (bir patent istemi için):

| Özellik | Patent İstemi | Hedef Ürün | Eşleşme | Not |
|---|---|---|---|---|
| F1 | Tablet formu | Kapsül formu | HAYIR | Farklı dozaj formu |
| F2 | Atorvastatin | Atorvastatin | EVET | Aynı aktif madde |
| F3 | %30-50 (a/a) | %40 (a/a) | EVET | Aralık içinde |
| F4 | Mikrokristalin selüloz | Laktoz monohidrat | HAYIR | Farklı eksipiyan |
| F5 | Kolloidal silika | Magnezyum stearat | HAYIR | Farklı yardımcı |

**Yorum**: Tüm istem özelliklerinden sadece F2 ve F3 eşleşiyor; F1, F4, F5 eşleşmiyor → **Literal ihlal yok**. Doktrinel eşdeğer analizi: Kapsül ile tablet teknik eşdeğer sayılır mı? (Genelde hayır; farklı formülasyon süreci + farklı biyoyararlanım). **Sonuç: Bu patentten temiz.**

---

## 5. Mozaik tablosu şablonu

**Senaryo**: Hedef patent "İstem 1" (F1-F5 özellikleri) için hükümsüzlük argümanı.

| Özellik | Prior Art 1 (WO2010/001234, 2010) | Prior Art 2 (Smith et al., JACS 2012) | Prior Art 3 (US8123456, 2011) |
|---|---|---|---|
| F1 (Tablet formu) | ✓ (istem 5) | — | ✓ (ör. 3) |
| F2 (Atorvastatin) | ✓ (istem 1) | ✓ (Figure 2) | — |
| F3 (%30-50 konsantrasyon) | — | ✓ (Table 1) | — |
| F4 (Mikrokristalin selüloz) | ✓ (Ex. 2) | — | ✓ (ör. 3) |
| F5 (Kolloidal silika) | — | — | ✓ (ör. 3) |

**Analiz**:
- **Yenilik**: Hiçbir tek belge F1-F5 hepsini içermiyor → yenilik **var** (sıkı anlamda)
- **Buluş basamağı**: PA1 + PA3 kombinasyonu tüm özellikleri kapsıyor. PA1 bir sanat adamı için PA3 ile neden birleştirilsin? Motivasyon: her ikisi de tablet formülasyonlarını aynı problemi (biyoyararlanım) çözmeye çalışıyor → mozaik argümanı kabul edilebilir
- **Sonuç**: Buluş basamağı yoksunluğu (obviousness) argümanı mümkün. Strong-Moderate güvenilirlik.

---

## 6. Karar ağacı

```
                    [FTO/Invalidity sorusu]
                            │
                            ▼
                 [Müvekkil hangi taraf?]
                    ┌──────┴──────┐
                    ▼             ▼
              [Orijinatör]    [Jenerik/Biyobenzer]
                    │             │
                    ▼             ▼
         [Portföy maksimize]  [Pazar giriş]
                    │             │
          ┌─────────┼─────────┐   ├─────────────┐
          ▼         ▼         ▼   ▼             ▼
    [Mode 4      [Mode 6   [Mode 3]  [Mode 1    [Mode 2
    Lifecycle]   Litigation] Landscape] FTO]    Invalidity]
                                        │         │
                                        ▼         ▼
                             [Temiz? ] [Çürütülebilir?]
                              Evet/Hayır    Strong/Moderate/Weak
                              │        │         │
                              ▼        ▼         ▼
                          [Pazara gir] [Design-around] [Dava açmak]
                                            │             │
                                            ▼             ▼
                                  [Yeni FTO]     [Mode 5 Regulatory]
                                                  + [Mode 6 Litigation]
```

---

## 7. Sık düşülen tuzaklar ve bunlardan kaçınma

### Tuzak 1: Anahtar kelime tuzağı (the self-searcher's dilemma)

**Hata**: Sadece INN ile sorgu.
**Kaçınma**: Eşanlamlı havuzu kurmadan ve CPC koduna inmeden tarama yapma.

### Tuzak 2: Öncelik tarihi karışıklığı

**Hata**: Başvuru tarihini veya yayın tarihini öncelik tarihi sanmak.
**Kaçınma**: Öncelik tarihi (priority date) patent ailesinin en eski başvurusunun tarihidir — bu tarih prior art aramasının sınırıdır.

### Tuzak 3: Özet (abstract) üzerinden karar vermek

**Hata**: Patent özetini okuyup sonuca varmak.
**Kaçınma**: Hukuki kapsam **istem metniyle** belirlenir. Özet bağlayıcı değildir.

### Tuzak 4: Coğrafi körük

**Hata**: ABD veya AB patentini "küresel patent" sanmak.
**Kaçınma**: Patent ulusaldır. TR'de geçerli mi sorusu TÜRKPATENT EPAAT ile cevaplanır.

### Tuzak 5: Yıllık harç ödenmedi = patent aktif değil

**Hata**: Patent numarasının veri tabanında bulunmasına güvenmek.
**Kaçınma**: Yıllık harç ödenmemişse patent sona ermiştir; EPAAT status alanı kontrol edilmeli.

### Tuzak 6: Markush kapsamını hafife almak

**Hata**: "Bu patent eski, benim molekülüm daha yeni, nasıl ilişkili olabilir?"
**Kaçınma**: Eski bir Markush formülü, yeni spesifik bir molekülü kapsayabilir; topolojik test zorunludur.

### Tuzak 7: İkinci tıbbi kullanım ile tedavi usulü karıştırmak

**Hata**: "Hastalığı tedavi etmek için X ilacı" istemi patent edilmez zannetmek.
**Kaçınma**: Swiss-type ("Hastalık tedavisi için kullanılmak üzere X") ve EPC-2000 purpose-limited ("Hastalık tedavisinde kullanım için X") istemler **patent edilebilir** (SMK + EPO yorumu). Sadece salt "method of treatment" istemi yasaklı.

### Tuzak 8: Bolar'ın ihracatı kapsadığını sanmak

**Hata**: Jenerik firmanın Türkiye'de üretip başka bir ülkeye patent süresinden önce ihraç edebileceğini düşünmek.
**Kaçınma**: Bolar istisnası **ruhsatlandırma hazırlığı** içindir, ticari ihracat değil. İhracat hedef ülkenin patent rejimine bağlıdır.

### Tuzak 9: Tedbir kararı = dava kazanılmış

**Hata**: İhtiyati tedbir kararının esas davanın kazanılacağı anlamına geldiğini sanmak.
**Kaçınma**: Tedbir **geçici** bir önlemdir; esas dava farklı sonuçlanabilir. Tedbir sonrası hükümsüzlük gelirse tedbir tazminatı gündeme gelir.

### Tuzak 10: Patent süresi dolmuş = serbest

**Hata**: Patentin 20 yılı doldu, serbest pazara giriş zannetmek.
**Kaçınma**: Veri imtiyazı (6 yıl Gümrük Birliği ilk ruhsat bazlı) patent bitse de aktif olabilir. Ayrıca devam / bölünmüş patentler, ikinci tıbbi kullanım patentleri, cihaz patentleri ayrı koruma katmanlarıdır.

---

## 8. Raporun kalite denetimi (peer review checklist)

FTO veya Invalidity raporu çıktığında aşağıdakiler kontrol edilir:

☐ Her iddia kaynak atıflı mı? (patent numarası + istem numarası / mevzuat maddesi / Yargıtay karar numarası)
☐ Tarih netliği var mı? (öncelik, başvuru, yayın, granted, expiry ayırt edilmiş mi)
☐ Coğrafi netlik var mı? (hangi ülkelerde aktif, hangilerde değil)
☐ Risk seviyeleri tutarlı derecelendirilmiş mi? (Strong/Moderate/Weak)
☐ Doktrinel eşdeğer riski değerlendirilmiş mi?
☐ Yıllık harç / status teyidi var mı?
☐ Markush kapsam analizi yapıldı mı (küçük moleküller için)?
☐ Design-around önerileri FTO için dahil mi?
☐ Atak vektörü önceliklendirmesi Invalidity için var mı?
☐ Forum seçimi Invalidity için tartışılmış mı?
☐ Rezidüel risk beyanı açıkça verilmiş mi?
☐ Epistemik sınırlar belirtilmiş mi?
☐ Hukuki sorumluluk notu var mı (vekillik ilişkisi gerekliliği)?

Bu checklist, skill çıktısının **savunulabilirlik eşiğini** garanti eder.

---

*Bu protokol canlı bir dokümandır; her FTO/Invalidity çalışmasında uygulanır ve öğrenilen dersler eklenir. Spesifik bir dava için protokol adımlarına hakim bir patent vekili ve uzman ilaç hukuku avukatı ile koordinasyon zorunludur.*
