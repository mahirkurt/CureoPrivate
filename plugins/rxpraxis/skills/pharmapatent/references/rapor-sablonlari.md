# references/rapor-sablonlari.md — Çıktı Şablonları (6 Mod)

> Her modun çıktı formatı önceden tanımlıdır; bu şablonlar Carbon HTML ve docx uyumludur. Şablon dışına çıkma ancak bilimsel/hukuki gerekçe halinde ve açık beyanla yapılır.

## İlişkili Protokoller

- **`fto-invalidity-protokol.md`** — §1 FTO Raporu ve §2 Invalidity Briefing şablonlarını besleyen 9-adım + 11-adım iş akışları
- **`ictihat-emsal.md`** — §6 Litigation Briefing için Yargıtay 11. HD eğilimleri, FSHHM pratiği ve EPO G-kararları
- **`ruhsat-veri-imtiyazi.md`** — §5 Pazara Giriş Takvimi için 6 yıllık veri imtiyazı formülü (Gümrük Birliği MAX hesabı)
- **`smk-6769-ilac.md`** — Tüm şablonlarda SMK madde atıflarının (m.85, m.138, m.159 vb.) hukuki çerçevesi
- **`gorsel-standartlari.md`** [v1.3.0] — Her şablon için zorunlu görsel seti (Gantt, heatmap, choropleth, citation network)
- **`visualize-widget-kutuphanesi.md`** [v1.5.0] — 33 hazır SVG/Mermaid/HTML şablonu, IBM Carbon + IBM Plex uyumlu, inline görseller için `visualize:show_widget`
- **`compliance-beyanlari.md`** [v1.3.0] — Her rapor tipi için zorunlu compliance footer (GPP3/MDR-IVDR/KVKK/avukat-müvekkil)

## Filled Examples (Doldurulmuş Örnekler)

Aşağıdaki doldurulmuş örnekler bu şablonların nasıl kullanılacağını somutlaştırır:

- **§1 FTO Raporu** → `examples/fto-ornek-atorvastatin.md` (hipotetik atorvastatin 40mg tablet için tam FTO)
- **§2 Invalidity Briefing** → `examples/invalidity-ornek-trastuzumab.md` (hipotetik trastuzumab formülasyon patenti çürütme)
- **§5 Pazara Giriş Takvimi** → `examples/regulatory-ornek-semaglutide.md` (hipotetik semaglutide biyobenzer pazara giriş)

Claude, yeni bir rapor üretirken önce ilgili filled example'ı okumalı; içerik + yapı + ton kalıbını oradan çapalayıp hedef vakaya uyarlamalıdır.

## Hedef Kitle Varyasyonları

Aynı rapor üç farklı hedef kitleye üç farklı varyantta hazırlanabilir. Varyant seçimi açıkça belirtilmelidir (rapor kapağında "Hedef kitle: Technical | Executive | Legal").

### Varyant 1 — Technical (R&D, patent vekili, bilirkişi)

**Hedef uzunluk**: 15-30 sayfa
**Ton**: Teknik jargon serbest, kimyasal yapı/XRPD/SMILES detaylı, deneysel data tam
**Odak**: Her argümanın teknik delilleri; özellik-özellik matrisleri tam; mozaik tablosu; prior art derinliği

**Zorunlu bileşenler**:
- Tam bibliyografi
- Ham prior art pasajları (alıntılı)
- Kimyasal yapı görselleri (SMILES + 2D structure)
- Deneysel protokoller (XRPD, DSC, biyoeşdeğerlik)
- Markush topoloji analizi (varsa)
- Peer review checklist sonucu

**Atlanabilir**: Yönetici özeti BLUF kısa tutulur; glossary gereksiz.

### Varyant 2 — Executive (CEO, CFO, Board, Strategic Committee)

**Hedef uzunluk**: 1-2 sayfa (executive dashboard formatı)
**Ton**: BLUF (Bottom Line Up Front), nicel, aksiyon odaklı
**Odak**: Karar noktası + finansal etki + risk skoru + önerilen aksiyon

**Zorunlu bileşenler**:
- BLUF (ilk 3 satır: sonuç + öneri + risk)
- Nicel etkiler: maliyet tahmini (USD), zaman (ay), pazar payı (%)
- Risk skoru (Strong/Moderate/Weak yerine 1-5 ölçekli)
- Karar matrisi (2-3 alternatif × 3-4 kriter)
- İmza blokları (hazırlayan, onaylayan, CFO sign-off)
- Sonraki adım tablosu (30/60/90 gün)

**Zorunlu atlanır**: Teknik jargon, SMK madde atıfları (ayrı ek olarak), kimyasal yapılar, tam prior art listesi (ek olarak).

**Tipik bölüm yapısı**:
1. BLUF (3 satır)
2. Karar alternatifleri (tablo)
3. Finansal etki (USD, NPV)
4. Risk özeti (1-5 skor)
5. Tavsiye + imza

### Varyant 3 — Legal (Hukuk Departmanı, Dış Vekil, Dava Ekibi)

**Hedef uzunluk**: 8-15 sayfa
**Ton**: Hukuki terminoloji, SMK + içtihat atıfları, savunulabilir dil
**Odak**: Argüman hattı + forum stratejisi + süreç + maliyet

**Zorunlu bileşenler**:
- SMK madde atıfları tam (m.82, 83, 85, 92, 138, 141, 149, 151, 159)
- Yargıtay emsal numaraları (Yargıtay 11. HD, tarih + esas numarası)
- EPO G-kararları (yorumsal kaynak olarak)
- Forum stratejisi detayı (hangi FSHHM, neden)
- Süreç ve takvim Gantt
- Maliyet tahmini kalem bazlı
- Karar ağacı (olası sonuçlar + ihtimaller)
- Hukuki sorumluluk + vekillik notu
- Çıkar çatışması beyanı (gerekiyorsa)

**Atlanabilir**: Tam teknik deliller (Technical varyant ekinde), çok detaylı kimya (gerekmedikçe).

### Varyant seçim kılavuzu

| Soru | Öneri |
|---|---|
| Kim okuyacak? | CEO/Board → Executive; Vekil → Legal; Bilirkişi → Technical |
| Ne kararı için? | Go/no-go → Executive; Dava açacak → Legal; İtiraz yazacak → Technical + Legal |
| Dokümanın ömrü? | 1 celse → Legal; 1 yönetim kurulu → Executive; 10 yıl portföy → Technical |
| Varsayılan? | **Technical** (en kapsamlı, diğerleri bundan türeyebilir) |

**İpucu**: Bir Technical rapor hazırlandıktan sonra Executive + Legal varyantlar ondan 2-3 saat içinde türetilebilir. Ters yön çok daha zordur.

## İçindekiler

- §1. FTO Raporu
- §2. Invalidity Briefing
- §3. Landscape Raporu
- §4. Lifecycle Yol Haritası
- §5. Pazara Giriş Takvimi
- §6. Litigation Briefing
- §7. Due Diligence Report (v1.2.0)
- §8. Opposition Briefing — EPO + TÜRKPATENT 3. Kişi Görüşü (v1.2.0)
- §9. Biosimilar Pathway Briefing (v1.2.0)
- §10. Expert Witness Report — FSHHM Bilirkişi Rapor Taslağı (v1.4.0)
- §3. Landscape Raporu
- §4. Lifecycle Yol Haritası
- §5. Pazara Giriş Takvimi
- §6. Litigation Briefing

---

## §1. FTO Raporu

### Kapak

- **Başlık**: "Faaliyet Serbestisi (FTO) Raporu — [Ürün adı]"
- **Versiyon / tarih**
- **Hazırlayan** (kurumsal rol)
- **Dağıtım kısıtı** (gizli / gizli-hukuki çalışma ürünü)

### 1. Yönetici Özeti

- Analiz konusu (1-2 cümle)
- Genel sonuç (Temiz / Kısmen riskli / Kritik risk)
- Ana bulgular (3-5 madde)
- Kritik öneri (varsa)

### 2. Ürün Teknik Özeti

- INN / CAS / SMILES / InChI
- Eksipiyanlar listesi
- Dozaj formu, konsantrasyon, doz, uygulama yolu
- Endikasyon(lar)
- Uygulama cihazı (varsa)
- Hedef pazar(lar) ve pazara giriş tarihi

### 3. Araştırma Metodolojisi

- Kullanılan veri tabanları
- Boolean sorgu örnekleri
- CPC kilit kodları
- Tarih aralığı
- Kimyasal yapısal arama (varsa)
- Epistemik sınırlar (ne tarandı, ne taranamadı)

### 4. Tespit Edilen Aktif Patentler

| Patent No | Başvuru Sahibi | Başlık | Öncelik | Expiry | TR Durum | Risk |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

### 5. İstem-Bazlı Analiz (her patent için)

**Patent [X]**:
- Bağımsız istem: [metin özeti]
- Özellik-özellik eşleştirme tablosu
- Literal ihlal analizi
- Doktrinel eşdeğer analizi
- Risk seviyesi: [Kritik/Yüksek/Orta/Düşük/Temiz]
- Yorum: [gerekçe]

### 6. Design-Around Önerileri (varsa)

- Tespit edilen engel
- Teknik alternatif(ler)
- Biyoeşdeğerlik / etkinlik etkisi
- Yeni FTO sorunu çıkarıp çıkarmadığı
- Tahmini süreç (CE / ruhsat revizyon süresi)

### 7. Rezidüel Risk Beyanı

- Pending başvurular (henüz yayımlanmamış)
- Terk edilmiş ama kamu malı olmayan başvurular
- Dil sınırı nedeniyle taranmayan kaynaklar
- Markush analizinin profesyonel araç kısıtı
- Diğer epistemik sınırlar

### 8. Genel Sonuç ve Öneriler

- Stratejik değerlendirme
- Sonraki adımlar (pazara giriş / müzakere / dava / çekilme)
- Öngörülen zaman çizelgesi
- Maliyet tahminleri (varsa)

### 9. Ek: Tam Kaynak Listesi

- Tüm patent referansları (tam numara + ofis)
- NPL referansları
- Kaynak erişim tarihleri
- Kullanılan veri tabanlarının versiyonları

### 10. Hukuki Sorumluluk Notu

> Bu rapor bilgilendirme amaçlıdır. Ticari karar için yetkili patent vekili ve hukuk müşaviri ile koordinasyon zorunludur. Raporda yer alan bulgular hazırlandığı tarihte geçerli veri tabanı sonuçlarına dayanır; patent durumları zamanla değişebilir.

---

## §2. Invalidity Briefing

### Kapak

- **Başlık**: "Hükümsüzlük Analizi — Patent [X]"
- **Versiyon / tarih**
- **Hazırlayan**
- **Dağıtım kısıtı**

### 1. Yönetici Özeti

- Hedef patent (numara + başvuru sahibi)
- Hükümsüzlük gerekçe özeti (3-5 madde)
- Güvenilirlik derecelendirmesi (Strong / Moderate / Weak)
- Önerilen forum stratejisi
- Öngörülen süreç ve maliyet

### 2. Hedef Patent Profili

- Patent numarası (TR + EP + US + WO varsa)
- Başvuru sahibi, mucit(ler)
- Öncelik tarihi, başvuru tarihi, yayın tarihi, granted tarihi
- Mevcut status (aktif / itiraz altında / kısmen iptal edilmiş)
- Bağımsız ve bağımlı istemler
- Patent ailesi (INPADOC family)

### 3. Saldırılacak İstemler

Hangi istemler pazar giriş engelidir? Öncelik sırası.

### 4. Özellik-Özellik Ayrıştırma

Her hedef istem için özellikler listesi.

### 5. Prior Art Taraması

**5.1. Patent prior art**:
Liste — her biri için yayın tarihi + özet + hangi özellikleri kapsadığı.

**5.2. NPL prior art**:
Hakemli makaleler, preprintler, tezler, klinik kayıtlar — aynı format.

**5.3. Kimyasal Markush prior art** (küçük moleküller için):
Daha önceki Markush formüllerinin kapsam analizi.

### 6. Mozaik Tablosu

| Özellik | PA1 | PA2 | PA3 | ... |
|---|---|---|---|---|
| F1 | ✓ | — | ✓ |  |
| F2 | — | ✓ | — |  |
| ... |  |  |  |  |

### 7. Hükümsüzlük Argümanları (atak vektörleri)

**7.1. Yenilik yoksunluğu (Novelty attack)**:
- Argüman detayı
- Delil: prior art [X]
- Güvenilirlik: [Strong / Moderate / Weak]

**7.2. Buluş basamağı yoksunluğu (Obviousness attack)**:
- Problem-solution yaklaşımı
- En yakın prior art + ikincil referanslar
- Kombinasyonun motivasyonu
- Güvenilirlik

**7.3. Yeterli açıklama yoksunluğu**:
- Undue burden argümanı
- Geniş Markush + az örnek
- Güvenilirlik

**7.4. Patent verilemeyecek konu**:
- Tedavi usulü vs. kullanım istemi yorumu
- Güvenilirlik

**7.5. Diğer gerekçeler**:
- Hak sahipliği
- Çift patent
- Güvenilirlik

### 8. Atak Vektörü Önceliklendirmesi

| Vektör | Güvenilirlik | Süreç | Tahmini maliyet | Öneri |
|---|---|---|---|---|
| Yenilik | Strong | Hızlı | Düşük | Birincil saldırı |
| Buluş basamağı | Moderate | Orta | Orta | İkincil destek |
| ... |  |  |  |  |

### 9. Forum Stratejisi

- FSHHM hükümsüzlük davası (TR)
- TÜRKPATENT YİDK itirazı (ret kararı için)
- EPO opposition (EP patenti + 9 ay içinde)
- Üçüncü kişi görüşü
- ABD PTAB IPR (varsa)
- Çok-forum kombinasyonu

### 10. Öngörülen Süreç ve Takvim

- İlk derece dava süresi
- İstinaf + temyiz
- EPO opposition süreci
- Tedbir olasılığı

### 11. Hukuki Sorumluluk Notu

Aynı §1.10 gibi.

---

## §3. Landscape Raporu

### Kapak

- **Başlık**: "Patent Peyzajı Raporu — [Modalite / Hedef / Endikasyon]"

### 1. Yönetici Özeti

- Araştırma kapsamı
- Öne çıkan bulgular
- Stratejik implikasyonlar

### 2. Araştırma Kapsamı

- Teknoloji alanı tanımı
- CPC hiyerarşisi
- Coğrafi kapsam
- Zaman ufku

### 3. Patent Hacmi — Zaman Serisi

- Yıllık başvuru sayısı (grafik)
- Coğrafi yayılım (harita / tablo)
- Pending / granted / lapsed dağılımı

### 4. Portföy Kümeleme

**4.1. En aktif başvuru sahipleri (Assignee Top 20)**:

| Sıra | Assignee | Patent sayısı | Ana teknoloji |
|---|---|---|---|
| 1 | ... | ... | ... |

**4.2. En aktif mucitler**:

Benzer tablo.

**4.3. Kurumsal-akademik işbirlikçiler**:

Üniversite-sanayi ortak başvuruları.

### 5. Atıf Ağı Analizi

- **Foundational patents** (temel patentler) — en çok atıf alanlar
- **Peripheral patents** — etrafındaki gelişmeler
- **Citation graph** (görsel — visualize tool ile)

### 6. Kritik Patent Aileleri

Her önemli aile için kısa özet:
- Ebeveyn patent
- Devam / bölünmüş başvurular
- Bitiş tarihleri
- Teknik konusu
- Pazar implikasyonu

### 7. Evergreening Haritası

Spesifik moleküller için:
- Birincil madde patenti
- Polimorf patentleri
- Formülasyon patentleri
- İkinci tıbbi kullanım
- Cihaz patentleri
- Toplam koruma ömrü

### 8. BERT/NLP Öngörü Katmanı (varsa)

Henüz onay almamış ancak patent peyzajında görünen adaylar.

### 9. Stratejik İmplikasyonlar

- Pazar fırsatları
- Yatırım önerileri
- Lisans fırsatları
- Rekabet uyarıları

### 10. Ek: Tam Patent Listesi

---

## §4. Lifecycle Yol Haritası

### Kapak

- **Başlık**: "Ürün Yaşam Döngüsü Yol Haritası — [Ürün]"

### 1. Yönetici Özeti

- Mevcut portföy pozisyonu
- Öngörülen jenerik / biyobenzer giriş penceresi
- Stratejik öneriler

### 2. Portföy Mevcut Durum

**2.1. Aktif patentler**:

| Patent | Öncelik | TR Expiry | Teknik konusu |
|---|---|---|---|
| ... | ... | ... | birincil madde / polimorf / formülasyon / ... |

**2.2. Pending başvurular**:
Liste.

**2.3. Coğrafi kapsam**:
Hangi ülkelerde aktif.

### 3. Evergreening Fırsat Analizi

Yeni koruma katmanları için ürünün boyutları:
- Fizikokimyasal (polimorf, hidrat, co-crystal)
- Farmakokinetik (uzatılmış salınım, hedefleme)
- Kombinasyon (sabit kombinasyon, fixed-dose)
- İletim sistemi (yeni cihaz, yeni yol)
- Pediatrik
- İkinci tıbbi kullanım

### 4. Veri İmtiyazı Haritası

- Türkiye veri imtiyazı bitişi
- AB veri imtiyazı (8+2+1)
- ABD NCE/ODE/PED exclusivities
- Ortalama LOE penceresi

### 5. Cihaz Entegrasyonu

- Mevcut cihaz patentleri (A61M)
- CE / ÜTS uyumu
- Kombinasyon ürün patent potansiyeli

### 6. Gantt Zaman Çizelgesi

```
  2024   2025   2026   2027   2028   2029   2030   2031   2032
   |      |      |      |      |      |      |      |      |
P1 =========================>                       [birincil madde expiry]
P2       =====================>                     [formülasyon]
P3            ===============================>      [cihaz]
VI =================>                                [veri imtiyazı]
PED    =====>                                       [pediatrik uzatma]
JG                          X                       [jenerik teorik giriş]
```

### 7. Stratejik Karar Noktaları

- 2025 Q2: Divisional başvuru go/no-go
- 2026: İkinci tıbbi kullanım patent başvuru
- 2027: Yeni cihaz patent başvuru
- 2028: Rakip FTO temizlemesi için lisans stratejisi

### 8. Öngörülen Gelir Erozyonu Modeli

- LOE öncesi baseline
- Yıl 1 sonrası % erozyon (küçük molekül ~%40-60, biyobenzer ~%20-40)
- 5 yıl projeksiyon

### 9. Öneriler

- Patent başvuru önceliklendirmesi
- Ülke seçimi (hangi pazarlar)
- Ülke terkleri (maliyeti gider seyredenler)
- Çapraz lisans / ortak savunma imkânları

---

## §5. Pazara Giriş Takvimi

### Kapak

- **Başlık**: "Pazara Giriş Takvimi — [Ürün]"

### 1. Yönetici Özeti

- En erken yasal pazara arz tarihi
- Kritik engeller
- Önerilen zaman çizelgesi

### 2. Ürün Profili ve Ruhsat Stratejisi

- Ürün tanımı
- Başvuru tipi (tam / kısaltılmış / hibrid / biyobenzer)
- Hedef pazar(lar)

### 3. Patent Durumu Özeti

- Referans ürünün patent portföyü
- En geç biten aktif patentin tarihi
- Patent hükümsüzlük olasılığı (varsa)

### 4. Veri İmtiyazı Hesabı

**Temel formül**:

```
Erişim tarihi = MAX(
    Gümrük Birliği alanında ilk ruhsat tarihi + 6 yıl,
    Türkiye patent süresi (varsa)
)
```

- Gümrük Birliği alanında ilk ruhsat tarihi: [tarih] (referans: [TİTCK/EMA belgesi])
- Türkiye patent süresi: [tarih]
- Hesaplanan erişim tarihi: [tarih]

### 5. Bolar İstisnası Takvimi

- Biyoeşdeğerlik başlama tarihi (erken — Bolar kapsamı)
- Ruhsat başvuru tarihi (veri imtiyazı sonrası)
- Beklenen ruhsat karar tarihi
- Fiyat onay tarihi
- Geri ödeme müzakere tarihi

### 6. Pediatrik / Orphan Etkileşimi

Türkiye'de uzatmasız; AB'de etkiler (çıkış pazarları için).

### 7. Cihaz Entegrasyonu (varsa)

- ÜTS kayıt süresi
- CE değerlendirme süresi
- Kombinasyon ürün onay süresi

### 8. Risk Değerlendirmesi

- İhtiyati tedbir ihtimali (orijinatörün dava açması)
- Tedbir teminatı tahmini
- Tedbir kaldırma stratejisi

### 9. Zaman Çizelgesi

```
                                         Aktif patent bitişi
                                         ↓
Jenerik  [Biyoeşdeğerlik] [Ruhsat] [Fiyat] [SGK] [Arz]
   |     |                |        |       |     |
   2025  2026             2028     2029    2029  2030
```

### 10. Öneriler

- En erken başlama tarihi
- Kritik milestonelar
- Acil durum senaryoları

---

## §6. Litigation Briefing

### Kapak

- **Başlık**: "Dava Briefingi — [Dava konusu]"

### 1. Yönetici Özeti

- İhtilafın niteliği
- Hedef
- Stratejik öneri

### 2. Tarafların Pozisyonu

- Davacı / davalı
- Hakların tanımı (patent, veri imtiyazı, ruhsat)
- Pazar pozisyonları

### 3. Hukuki Vaka Analizi

- Vakanın özeti
- İlgili SMK maddeleri
- İlgili Yargıtay emsalleri
- EPO paralel içtihadı

### 4. Argüman Hattı (tecavüz davası için)

**4.1. Davacı argümanları**:
- Patentin geçerliliği + kapsamı
- Tecavüz fiilinin tespiti (literal + doktrinel eşdeğer)
- Tazminat hesabı

**4.2. Muhtemel davalı argümanları**:
- Literal ihlalin bulunmaması
- Doktrinel eşdeğer red
- Bolar istisnası
- Hükümsüzlük karşı davası

### 5. Argüman Hattı (hükümsüzlük davası için)

Invalidity Briefing §7-8 özetlenir.

### 6. İhtiyati Tedbir Stratejisi

**Talep için**:
- Prima facie delil
- Teminat hesabı
- Acil durum gerekçesi (pazar erozyonu)

**Kaldırma için**:
- Hükümsüzlük karşı dava
- Teminat yüksekliği
- Pazar gerçekliği

### 7. Delil Stratejisi

- Teknik deliller (patent metinleri, bilirkişi gerekliliği)
- Ticari deliller (ürün örnekleri, satış verileri)
- Tanıklar (mucitler, sektör uzmanları)
- Bilirkişi profili önerisi

### 8. Forum Seçimi

- Ana forum (FSHHM — hangi il?)
- Yan forumlar (TÜRKPATENT YİDK / EPO / ABD PTAB)
- Çok-forum koordinasyonu

### 9. Süreç ve Takvim

- İlk derece süresi
- İstinaf süresi
- Temyiz süresi
- Olası tedbir süreleri

### 10. Maliyet Tahmini

- Mahkeme harçları
- Vekalet ücreti
- Bilirkişi masrafları
- Tedbir teminatı

### 11. Karar Ağacı

```
                [Dava açılır]
                     │
                     ▼
             [Tedbir talebi?]
               Evet/Hayır
             ┌───┴───┐
             ▼       ▼
         [Tedbir   [Esas inceleme]
           verildi?]    │
           Evet/Hayır   ▼
         ┌─┴─┐      [Bilirkişi]
         ▼   ▼          │
      [İtiraz [Esas]    ▼
       kaldırma          [Karar]
       stratejisi]          │
                            ▼
                       [İstinaf]
                            │
                            ▼
                       [Temyiz]
```

### 12. Öneriler

- Önerilen ilk aksiyon
- Alternatif (uzlaşma) yolları
- Stratejik kırmızı çizgiler

### 13. Hukuki Sorumluluk Notu

> Bu briefing bilgilendirme amaçlıdır. Dava stratejisi ve dilekçe hazırlığı için yetkili vekil ile koordinasyon zorunludur.

---

## §7. Due Diligence Report

### Kapak

- **Başlık**: "Patent Due Diligence Raporu — [Target firma / asset]"
- **Amaç**: M&A, licensing, in-licensing due diligence
- **Hedef kitle**: Executive + Legal (M&A deal team)

### 1. Yönetici Özeti (BLUF)

- Deal structure özeti (1 cümle)
- Target portföy değer aralığı (P20-P80, USD)
- En kritik 3 red flag
- Go / no-go / conditional öneri

### 2. Deal Scope

- Target firma / asset tanımı
- Deal yapısı (asset purchase / equity / exclusive license / non-exclusive)
- Hedef coğrafi kapsam
- Hedef endikasyonlar

### 3. Target Patent Portföyü — Envanter

**Kritik patentler** (genellikle 5-50):

| Patent No | Asset | Öncelik | Expiry | Aktif ülkeler | Yıllık harç durumu | Kuvvet |
|---|---|---|---|---|---|---|

**Pending başvurular**: ayrı tablo.
**Terk edilmiş / sona eren**: ayrı tablo (geçmiş için).

### 4. Patent Geçerlilik Analizi

Her kritik patent için:
- Prior art taraması (kısa)
- Hükümsüzlük olasılığı (Strong / Moderate / Weak)
- Yıllık harç ödeme geçmişi
- Third-party opposition / hükümsüzlük davaları
- Forum shopping riski

### 5. Coverage Haritası

- Her patent + ülke kombinasyonu → yeşil/sarı/kırmızı
- Toplam coverage skoru
- Boşluklar (gap analysis) — hangi pazarlarda koruma zayıf?

### 6. FTO Durumu — Target ürünleri için

- Üçüncü taraf patentler target'ı bloke ediyor mu?
- In-license gerekliliği var mı?
- Royalty stack (varsa)

### 7. Değerleme

- Cost Approach (historical R&D)
- Market Approach (comparable transactions)
- Income Approach (DCF + relief-from-royalty)
- Monte Carlo P10/P50/P90
- **Değer aralığı** (USD)

Detaylar için `references/patent-degerleme.md`.

### 8. Red Flags (Kırmızı Bayraklar)

- Devam eden veya muhtemel dava
- Patent tercümesi hataları
- Yıllık harç gecikmeleri
- Terk edilen kritik ülkeler
- Hak sahipliği anlaşmazlıkları
- Sınırlı patent süresi kalmış

### 9. Yeşil Bayraklar

- Portföy derinliği
- Coğrafi genişlik
- Kritik pazarlarda güçlü koruma
- Pending başvurular ile devamlılık
- Patent dava zaferleri

### 10. Risk Azaltma Önerileri

- Reps & warranties deal yapısında
- Escrow rakamları
- Hangi asset'ler deal scope'dan çıkarılabilir

### 11. Sonraki Adımlar

- Ek DD istekleri
- Sözlü görüşmeler (target IP ekip)
- Dış patent vekili incelemesi
- Değerleme revizyonu (2. tur data sonrası)

### 12. Hukuki Sorumluluk Notu

> Bu DD raporu M&A kararına temel oluşturur; nihai deal kararı için bağımsız hukuki görüş + değerleme danışmanı onayı + deal attorney incelemesi zorunludur.

---

## §8. Opposition Briefing (EPO + TÜRKPATENT 3. Kişi Görüşü)

### Kapak

- **Başlık**: "Opposition / 3. Kişi Görüşü Briefing — Patent [X]"
- **Forum**: EPO Opposition Division / TÜRKPATENT YİDK
- **Hedef kitle**: Technical + Legal (opposition team)

### 1. Yönetici Özeti

- Hedef patent + başvuru sahibi
- Opposition forumu + süre
- Argüman özeti (3-5 satır)
- Önerilen aksiyon + zaman

### 2. Forum ve Süre Analizi

**EPO Opposition**:
- 9 aylık pencere — granted tarihinden itibaren
- Geç başvuru kabul edilmez
- Maliyet: €880 (2024) + patent vekili ücreti

**TÜRKPATENT 3. Kişi Görüşü**:
- Yayımlanmış başvuruya (granted öncesi) herhangi bir zamanda
- Taraf olmaya gerek yok
- Maliyet düşük (resmi harç + vekil ücreti)

**Hangi forum seçilsin?**:
- EP patent + 9 ay içinde → EPO opposition (merkezi iptal etkisi)
- Yayımlanmış TR başvurusu → 3. kişi görüşü
- Granted TR patent → FSHHM hükümsüzlük davası (farklı rapor — §2)

### 3. Hedef Patent Profili

- Patent numarası (EP / TR / equivalents)
- Başvuru sahibi + mucit
- Öncelik tarihi, başvuru tarihi, granted tarihi
- Opposition süresi durumu
- Yıllık harç + pending status

### 4. Hedeflenen İstemler

Hangi istemler öncelikli? Genellikle:
- İstem 1 (bağımsız) — tam iptal önceliği
- Spesifik bağımlı istemler (formülasyon, kombinasyon) — pazar engelleri

### 5. Opposition Gerekçeleri

EPO opposition, EPC Article 100 uyarınca üç kategoride:

**Article 100(a)** — patent edilebilirlik:
- 100(a)(i): Yenilik yoksunluğu (EPC Art. 54)
- 100(a)(ii): Buluş basamağı yoksunluğu (EPC Art. 56)
- 100(a)(iii): Sanayiye uygulanamazlık (EPC Art. 57)
- 100(a)(iv): Patent edilemeyecek konu (EPC Art. 52-53)

**Article 100(b)** — yeterli açıklama (EPC Art. 83):
- Undue burden
- Plausibility (T 1329/04)

**Article 100(c)** — tarifname değişikliği (EPC Art. 123(2)):
- "Added matter" — başvuru sonrası eklenen kapsam

### 6. Prior Art Delilleri

**Patent prior art** — her biri için tam alıntı + öncelik tarihi + ilgili pasajlar.
**NPL prior art** — tam atıf + yayım tarihi + ilgili bölümler.
**Kimyasal Markush** — prior formüller (gerekirse).

### 7. Argüman Hattı

Her argüman için:
- Hangi opposition gerekçesine dayanır (EPC Art. 100)
- Prior art delilleri
- Problem-solution analizi (obviousness için)
- Güvenilirlik (Strong / Moderate / Weak)

### 8. EPO Özel Doktrin Uygulamaları

- **Problem-Solution Approach** — obviousness için
- **Plausibility** — T 1329/04, Warner-Lambert etkisi
- **Technical effect** — teknik etki iddiasının desteklenmesi
- **Intermediate generalisation** — istem değişikliklerinde sınır

### 9. Muhtemel Karşı Argümanlar

Patent sahibi ne diyebilir?
- Surprising technical effect
- Plausibility reply
- Claim amendment önerisi (partial maintenance)

### 10. Süreç ve Takvim

- Notice of opposition (yazı)
- Başvuru sahibinin cevabı (4 ay)
- Oral proceedings (genellikle 18-30 ay sonra)
- Opposition Division kararı
- Temyiz (Board of Appeal) — gerekirse

### 11. Strateji: Çok-opposition koordinasyonu

Birden fazla şirket aynı patente opposition açabilir. Strateji:
- Argüman paylaşımı (gizlilik anlaşması ile)
- Farklı prior art odağı (overlap + complementary)
- Oral proceedings koordinasyonu

### 12. Maliyet Tahmini

- EPO harcı: €880
- Patent vekili: €15,000-50,000 (karmaşıklığa göre)
- Oral proceedings: +€10,000
- Bilirkişi raporu (gerekirse): +€5,000-20,000
- Temyiz (gerekirse): +€30,000-80,000
- **Toplam**: €30,000-150,000

### 13. Hukuki Sorumluluk Notu

> Opposition dilekçesi taslağı EPO-akredite patent vekili tarafından final kontrol edilmelidir. Bu briefing yönlendirme amaçlıdır; nihai sorumluluk vekilde.

---

## §9. Biosimilar Pathway Briefing

### Kapak

- **Başlık**: "Biyobenzer Yol Haritası — [Referans ürün adı]"
- **Hedef kitle**: Executive (strateji) + Legal (IP + regulatory)

### 1. Yönetici Özeti

- Referans ürün + pazar büyüklüğü
- En erken yasal pazara giriş tarihi (TR + AB + ABD ayrı)
- Toplam yatırım gerekliliği
- NPV aralığı
- Go / no-go / wait öneri

### 2. Referans Ürün Profili

- INN + marka (ör. trastuzumab / Herceptin)
- Modalite (mAb / ADC / peptid / hormon)
- Molekül karmaşıklığı
- Endikasyonlar
- 2024 pazar büyüklüğü (ABD + AB + TR + global)
- Tipik doz + fiyat

### 3. Patent Duvarı Haritası

Tam patent portföyü haritası:

| Patent No | Konu | Expiry | TR / AB / ABD durum | Aşma stratejisi |
|---|---|---|---|---|

Üç kategori:
- **Molekül patenti** (birincil — genellikle sona ermiş)
- **Formülasyon patenti** (aşılabilir farklı buffer/pH ile)
- **Cihaz patenti** (kendi cihaz veya üçüncü taraf)

Detaylı patent analizi için ayrı FTO raporu gerekir (§1 şablonu).

### 4. Veri İmtiyazı Hesabı

Her üç jurisdiction için:

**Türkiye**: 6 yıl (Gümrük Birliği alanında ilk ruhsat bazlı)
**AB**: 8+2+1 yıl (toplam 11 yıl max)
**ABD**: 12 yıl (BPCIA biologics exclusivity)

**Erişim tarihi formülü**:
```
Erişim = MAX(patent expiry, data exclusivity end)
```

### 5. Karşılaştırılabilirlik Paketi

Detaylar için `references/biyobenzer-yol.md §2`.

**CQA (Critical Quality Attributes)**:
- Primer yapı (LC-MS peptid haritalama)
- Glikan paterni
- Yükler (cIEF, CE-SDS)
- Biyolojik aktivite (cell-based potency)
- İmmünojenisite potansiyeli

**Analitik karşılaştırma** — 15+ ortogonal metod.

**Nonklinik karşılaştırma** — in vitro + in vivo.

**Klinik karşılaştırma**:
- Faz I PK (~30-60 gönüllü): equivalence limit ±20%
- Faz III: en duyarlı endikasyonda, 200-900 hasta

### 6. Extrapolation Stratejisi

Bilimsel gerekçe ile hangi endikasyonlara uzatılabilir?
- Primary endikasyon (pivotal trial)
- Extrapolation eligible (aynı mekanizma, aynı popülasyon)
- Extrapolation zor (farklı mekanizma)

### 7. Cihaz Stratejisi

Biyobenzer genellikle enjektabl → cihaz gerekli:

- Seçenek A: Kendi cihaz geliştir (18-24 ay + CE IIb + ÜTS)
- Seçenek B: Üçüncü taraf tedarikçi (Ypsomed / SHL / BD) — 12-18 ay
- Seçenek C: Önce prefilled syringe ile gir, oto-enjektöre geçiş sonra

### 8. Üretim Gerekliliği

- Biyolojik üretim tesisi CapEx: USD 50-200M
- GMP validation: 18-24 ay
- Proses development: 18-30 ay
- Kapasite planlaması

### 9. Ruhsat Takvimi (Türkiye + AB + ABD)

| Aşama | TR | AB | ABD |
|---|---|---|---|
| Scientific advice | Opsiyonel | Önerilen | BPD Type II meetings |
| Karşılaştırılabilirlik | TİTCK BB | EMA CHMP | FDA 351(k) |
| Pivotal klinik | Başlat | Başlat | Başlat |
| Ruhsat başvuru | 18-30 ay | 12-18 ay | 10-16 ay |
| Onay sonrası | Fiyat + SGK | EC + ülke bazlı | Launch readiness |

### 10. Pazara Giriş Stratejisi

- **First mover** pozisyonu — patent settlement veya ilk onay
- **Fast follower** pozisyonu — düşük risk + kanıtlanmış yol
- **Fiyat stratejisi** — referansın %60-70'i (ilk giriş), %40-50'si (sonraki)

### 11. Finansal Projeksiyonu

- Revenue ramp-up (3 yıl)
- COGS projeksiyonu (%15-30)
- R&D payback period
- NPV (10 yıl)
- IRR

### 12. Risk Faktörleri

- Patent dava (ihtiyati tedbir ihtimali)
- Karşılaştırılabilirlik başarısızlığı (ör. glikan paterni ayrışır)
- İmmünojenisite artışı
- Referans ürün fiyat indirimi (protect market share)
- Orijinal üreticinin geliştirilmiş "biobetter" versiyonu

### 13. Öneriler ve Karar Ağacı

Go / wait / no-go karar matrisi kriter bazlı:

| Kriter | Go eşiği |
|---|---|
| Pazar büyüklüğü | >USD 500M küresel |
| Patent duvarı aşılabilir | Maks 3 kritik patent |
| Veri imtiyazı takvimi | 5 yıl içinde ulaşılabilir |
| Üretim CapEx ROI | <4 yıl payback |
| Klinik geliştirme maliyeti | <$100M |
| Rekabet (biyobenzer sayısı) | <3 beklenir |

### 14. Hukuki Sorumluluk Notu

> Biyobenzer stratejisi çok-disiplinli karar gerektirir: IP + regulatory + klinik + üretim + ticari. Bu briefing çerçeve sunar; nihai karar için uzman regülatör danışmanı + patent vekili + klinik geliştirme ekibi koordinasyon zorunludur.

---

## §10. Expert Witness Report (FSHHM Bilirkişi Rapor Taslağı) [v1.4.0]

### Kapak

- **Başlık**: "Bilirkişi Raporu — [Dosya No] / [Mahkeme]"
- **Dava No**: FSHHM / Dosya Numarası
- **Taraflar**: [Davacı] v. [Davalı]
- **Konu**: Patent tecavüzü / hükümsüzlük / karşı dava
- **Bilirkişi**: [Uzman İsim], [Unvan], [Kurum]
- **Tarih**: YYYY-MM-DD

### 1. Bilirkişi Kimliği ve Uzmanlık Alanı

**Önemli**: FSHHM bilirkişi raporunun geçerliliği, bilirkişinin uzmanlık alanının dava konusuyla uyumuna bağlıdır. Yargıtay 11. HD tutarlı olarak "uzmanlık dışı" alanda verilen raporları reddetmiştir.

- Ad-soyad, akademik unvan
- Üniversite + bölüm + kürsü
- Uzmanlık alanı (farmasötik kimya / farmakoloji / biyoteknoloji / tıbbi kimya / klinik araştırma / patent hukuku)
- Mevcut rol (Öğretim üyesi / Bölüm başkanı / Emekli öğretim üyesi / Patent vekili)
- Bilirkişilik deneyimi (FSHHM / diğer mahkemelerde yıllar + yaklaşık dava sayısı)
- Yayınlar (konu ilgili seçme bibliyografya)
- Çıkar çatışması beyanı (davada taraflarla profesyonel ilişki yok)

### 2. Görev Tanımı

Mahkeme tarafından sorulan soruların **birebir listesi**:

Örnek yapıda:
> "Bilirkişi heyeti aşağıdaki sorulara cevap vermeye yetkilidir:
> 
> 1. Davalı tarafından pazarlanan [ürün] ürünü, davacının TR/EP[xxxx] numaralı patentinin kapsamına girmekte midir?
> 2. Davacının patentinin istem 1'i yenilik ve buluş basamağı şartlarını taşımakta mıdır?
> 3. Söz konusu patent Türkiye Cumhuriyeti'nde geçerli midir?
> 4. Davalının fiili, SMK 6769 sayılı Kanun'un 141. maddesi kapsamında patent tecavüzü oluşturmakta mıdır?
> 5. Tecavüz tespiti halinde, zararın miktarı ve hesaplama yöntemi ne olmalıdır?"

### 3. Metodoloji

Bu bölümde, bilirkişinin **savunulabilir, bilimsel ve hukuki olarak geçerli metodolojisi** açıklanır:

#### 3.1. Kullanılan kaynaklar

- Patent dokümanları: [liste — TR/EP/US tam metin]
- Prior art referansları: [liste]
- Mevzuat: SMK 6769, TRIPS, Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği, ilgili maddeler
- İçtihat: Yargıtay 11. HD kararları (varsa, atıflı)
- Bilimsel literatür: [PubMed atıfları]
- Uzman kitaplar: [referanslar]

#### 3.2. Analiz metodu

- **İstem yorumu (claim construction)**: Hangi yorumsal yaklaşım kullanıldı — "ordinary meaning", "broadest reasonable interpretation", "Phillips standard"
- **Özellik ayrıştırması**: Patent istem özelliklerinin F1, F2, ..., Fn olarak ayrıştırılması (`../references/fto-invalidity-protokol.md §4`)
- **Karşılaştırma testi**: Literal ihlal + doktrinel eşdeğer testi
- **Buluş basamağı**: EPO problem-solution yaklaşımı (`../references/fto-invalidity-protokol.md §7.2`)

### 4. Patent Analizi

#### 4.1. Davacı patenti özeti

- Patent numarası (TR/EP/equivalents)
- Başvuru sahibi, mucit
- Öncelik tarihi, başvuru tarihi, tescil tarihi
- Patent süresi, yıllık harç durumu (EPAAT teyitli)
- Temel teknik konu

#### 4.2. İstemlerin teknik ayrıştırması

**İstem 1** (bağımsız):
> [İstem tam metni — orijinal dilde + Türkçe tercüme]

Özellik ayrıştırması:

| F# | Teknik özellik | Açıklama |
|---|---|---|
| F1 | [özellik] | [teknik açıklama] |
| F2 | [özellik] | [teknik açıklama] |
| ... | ... | ... |

**Bağımlı istemler**: Aynı ayrıştırma F(n+1), F(n+2), ... olarak.

### 5. Tecavüz Analizi (tecavüz davasında)

#### 5.1. Davalı ürününün teknik profili

Davalının pazarladığı ürün:
- Aktif madde, form, dozaj
- Formülasyon bileşenleri
- Üretim süreci (kamuya açık bilgiden)
- Ruhsat durumu

#### 5.2. Özellik-özellik karşılaştırma matrisi

| Özellik | İstem metni | Davalı ürünü | Eşleşme |
|---|---|---|---|
| F1 | [istem] | [davalı] | EVET / HAYIR |
| F2 | ... | ... | ... |

#### 5.3. Literal ihlal değerlendirmesi

**Sonuç**: İstem 1'in özellik listesinin tümü davalının ürününde yer alıyor mu?
- Tamamı var → Literal ihlal var
- Bir veya daha fazla özellik eksik → Literal ihlal yok

#### 5.4. Doktrinel eşdeğer değerlendirmesi

Literal ihlal yoksa:
- Eksik özellik(ler)in yerine davalı ürününde farklı bir element var mı?
- Bu element, istemdeki elementle **aynı işlevi** (function) + **aynı şekilde** (way) + **aynı sonucu** (result) sağlıyor mu?
- SMK m. 92/3 uyarınca doktrinel eşdeğer analizi — Yargıtay 11. HD uygulaması.

**Sonuç**: Doktrinel eşdeğer var / yok.

### 6. Hükümsüzlük Analizi (hükümsüzlük davasında / karşı davada)

#### 6.1. Prior art taraması

- Patent prior art: [liste, her biri için öncelik tarihi + ilgili pasajlar]
- NPL prior art: [liste]
- Markush analizi (varsa)

#### 6.2. Yenilik değerlendirmesi

**Test**: Tek bir prior art belgesi istem 1'in tüm özelliklerini kapsıyor mu?

Mozaik tablosu (`../references/fto-invalidity-protokol.md §5`).

**Sonuç**: 
- Yenilik var / yok
- SMK m. 83/1 uyumu

#### 6.3. Buluş basamağı değerlendirmesi

EPO Problem-Solution yaklaşımı:
1. En yakın prior art: [belge]
2. Teknik farklılık: [açıklama]
3. Objektif teknik problem: [tanım]
4. Prior art + ortalama uzman bilgisi problem çözümüne varır mı?

**Sonuç**:
- Aşikâr / aşikâr değil
- SMK m. 83/4 uyumu

#### 6.4. Yeterli açıklama değerlendirmesi

- Patent tarifnamesi istem kapsamını destekliyor mu?
- Ortalama uzman buluşu tekrar edebilir mi?
- "Undue burden" var mı?

### 7. Türkiye'de Patentin Geçerliliği

- TÜRKPATENT EPAAT kaydı: [tarih + status]
- Yıllık harç ödeme durumu
- Tercüme hataları (SMK m. 103)
- Üçüncü kişi görüşü / YİDK itirazı geçmişi

### 8. Zarar Hesaplama (tecavüz tespit edilirse)

SMK m. 151 uyarınca üç yöntem:

**Yöntem A — Fiili zarar + yoksun kalınan kâr**:
- Davacının zarar kanıtı
- Yoksun kalınan kâr hesabı

**Yöntem B — Tecavüz edenin net kârı (disgorgement)**:
- Davalının ciro + COGS + SG&A
- Net kâr hesabı

**Yöntem C — Lisans analojisi (reasonable royalty / RFR)**:
- Comparable transactions (`../references/patent-degerleme.md §3`)
- Royalty rate (sektörel benchmark)
- Revenue × royalty × geri ödeme süresi

**Önerilen**: Hangi yöntemin en yüksek sonuç verdiği + hesap tablosu.

### 9. Sonuç ve Görüş

Mahkeme sorularına tek tek cevap:

> **Soru 1**: Davalının ürünü patenti ihlal ediyor mu?
> **Cevap**: [EVET / HAYIR / KISMEN] — gerekçe: [kısa özet]
>
> **Soru 2**: Patent yenilik şartlarını taşıyor mu?
> **Cevap**: [EVET / HAYIR] — gerekçe: [kısa özet]
>
> **Soru 3**: ...

### 10. Savunulabilirlik Notları

- **Bu raporun dayandığı bilimsel veriler 2026-04-24 itibarıyla geçerlidir**
- **Prior art taraması [tarih] itibarıyla yapılmıştır; sonradan yeni belgeler çıkarsa değerlendirme yenilenmelidir**
- **Bilirkişi raporu, mahkeme önünde savunulabilmelidir — sözlü duruşma için hazırlık gerekebilir**

### 11. Çıkar Çatışması ve Bağımsızlık Beyanı

> "Ben [Bilirkişi adı], bu bilirkişi raporunda yer alan görüşlerin bağımsız ve objektif olduğunu; davanın taraflarıyla geçmişte veya halen finansal, akademik veya profesyonel bir çıkar ilişkim bulunmadığını; raporumun tarafsız ve bilimsel nitelik taşıdığını beyan ederim."

### 12. Referanslar

- Patent dokümanları: [tam liste]
- Bilimsel literatür: [atıflar]
- Mevzuat: SMK 6769 [ilgili maddeler]
- İçtihat: [Yargıtay karar numaraları]
- Diğer kaynaklar

---

*İmza*

**[Bilirkişi Adı]**
[Unvan]
[Kurum]
Tarih: [YYYY-MM-DD]

---

### Compliance Ek

Bu rapor, **mahkeme önünde sunulan bilirkişi raporudur**:
- Avukat-müvekkil ayrıcalığı: **HAYIR** (mahkeme kamusal dosyasında)
- KVKK: Davanın tarafları ile ilgili verileri içerebilir; mahkeme kararıyla gizlenebilir
- Bilirkişi bağımsızlığı beyanı zorunlu (HMK m. 266)

Detaylı compliance için: `../references/compliance-beyanlari.md`

---

*Şablonlar iskeletdir; her çalışmanın özgüllüğüne göre genişletilir veya daraltılır. Şablon dışına çıkma halinde açık beyan ve gerekçe zorunludur.*


