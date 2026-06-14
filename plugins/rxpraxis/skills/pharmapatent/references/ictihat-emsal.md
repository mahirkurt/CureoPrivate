# references/ictihat-emsal.md — Yargıtay, FSHHM, Danıştay, AYM İçtihadı ve EPO Paralel Yorumları

> Türk ilaç patent davalarının seyri Yargıtay 11. HD eğilimleri ile belirlenir; ancak EPO Genişletilmiş Temyiz Kurulu kararları (G-kararları) yorumsal kaynak olarak standart alınır. Bu protokol, **emsal çıkarma metodolojisini** ve **tipik karar örüntülerini** özetler.

## İlişkili Protokoller

- **`smk-6769-ilac.md`** — Yargıtay yorumlarının dayandığı SMK maddeleri (m.82, 83, 85, 92, 138, 159) ve TRIPS/Doha çerçevesi
- **`fto-invalidity-protokol.md` §2 Adım 7-11** — Kısmi hükümsüzlük, buluş basamağı ve mozaik argüman inşasında Yargıtay eğilimleri
- **`markush-protokol.md`** — EPO G 2/88 (seçim buluşu) doktrininin Türkiye'de uygulanması
- **`rapor-sablonlari.md` §6** — Litigation Briefing şablonu — içtihat bulgularının dava strateji dokümanına aktarımı

## İçindekiler

1. UYAP ve karar arama metodolojisi
2. Yargıtay 11. Hukuk Dairesi — ilaç patent eğilimleri
3. FSHHM (Fikri ve Sınai Haklar Hukuk Mahkemesi) pratiği
4. Danıştay — TÜRKPATENT YİDK iptal davaları
5. Anayasa Mahkemesi — sağlık hakkı ve mülkiyet dengesi
6. EPO Board of Appeal — paralel yorumsal kaynaklar
7. Konu bazlı içtihat haritası
8. Karar bağlayıcılığı ve öncelikler hiyerarşisi

---

## 1. UYAP ve karar arama metodolojisi

### Kaynaklar

> **MCP-FIRST [v2.0.1] — Mevzuat MCP**: SMK 6769 + yönetmelik + tebliğ + genelge tam metni için **Mevzuat MCP aktif (12 araç, revision `mevzuat-mcp-00017-668`, MCP SDK 1.27.0, protocolVersion 2024-11-05)**. Detay ve araç envanteri için `references/turk-mcp-entegrasyonu.md §4`. **Önemli ayrım**: Mevzuat MCP yalnız kanun/yönetmelik/tebliğ/genelge/Resmi Gazete kapsamındadır — **Yargıtay/Danıştay/AYM içtihadı MCP kapsamı dışıdır**. İçtihat aramaları için aşağıdaki UYAP / karararama.yargitay.gov.tr / danistay.gov.tr / kararlarbilgibankasi.anayasa.gov.tr web protokolleri uygulanır (hem v2.0.1 sonrası da geçerli birincil yöntem).

**UYAP Mevzuat Bilgi Sistemi**: https://www.mevzuat.gov.tr/
- Kanunlar, KHK'lar, yönetmelikler, tebliğler — **artık Mevzuat MCP üzerinden kanonik erişim**
- Mülga versiyonlar dahil
- SMK 6769 tam + önceki 551 KHK karşılaştırma
- **Provenance damgası** (v2.0.1): `[Mevzuat MCP / <tool> / mevzuat_id / erişim_tarihi]`. Web fetch yedeği yalnız MCP timeout audit-trail için.

**Yargıtay Karar Arama**: https://karararama.yargitay.gov.tr/
- 9.8 milyon karar
- Daire bazlı filtre
- Tarih + anahtar kelime filtresi
- PDF indirme

**Danıştay Karar Arama**: https://www.danistay.gov.tr/
- 385+ bin karar
- Daire + konu bazlı filtre

**Anayasa Mahkemesi**: https://kararlarbilgibankasi.anayasa.gov.tr/
- Bireysel başvuru + iptal + itiraz kararları

**UYAP Avukat Portalı**: Sadece avukatların erişimine açık; dava dosyalarına erişim, e-duruşma.

### Sorgu teknikleri

**Yargıtay arama örneği**:

```
Daire: 11. Hukuk Dairesi
Tarih aralığı: 2017-2024 (SMK dönemi)
Kelime: "patent" AND ("ilaç" OR "ecza")
```

```
Daire: Hukuk Genel Kurulu
Kelime: "ikinci tıbbi kullanım"
```

### Kritik arama terimleri

| Konu | Anahtar kelimeler |
|---|---|
| Patent tecavüzü | "patent", "tecavüz", "ihlal", "ilaç" |
| Hükümsüzlük | "patent hükümsüzlüğü", "geçersizlik", "kısmi hükümsüzlük" |
| İkinci tıbbi kullanım | "ikinci tıbbi kullanım", "Swiss-type", "purpose-limited" |
| İhtiyati tedbir | "ihtiyati tedbir", "tedbir kararı", "patent tedbiri" |
| Bolar istisnası | "Bolar", "deney amaçlı", "ruhsatlandırma istisnası" |
| Markush | "Markush", "kimyasal formül", "kapsam" |
| Buluş basamağı | "buluş basamağı", "aşikârlık", "uzman kimse" |
| TÜRKPATENT YİDK | "YİDK", "Yeniden İnceleme", "idari iptal" |
| Zorunlu lisans | "zorunlu lisans", "kamu yararı", "ilaç erişimi" |
| Bilirkişi | "bilirkişi raporu", "teknik uzman" |

---

## 2. Yargıtay 11. Hukuk Dairesi — ilaç patent eğilimleri

### Dairenin yetkisi

Yargıtay 11. Hukuk Dairesi, FSHHM kararları Yargıtay'a geldiğinde fikri mülkiyet uyuşmazlıklarını inceler. İlaç + patent + hükümsüzlük davaları 11. HD'ye gelir.

### Temel eğilimler (2017 SMK sonrası)

**Eğilim 1 — Kısmi hükümsüzlük sık uygulanır**

Yargıtay, ilaç patentlerinde "all or nothing" yaklaşımı yerine istem-bazlı analiz yapar. Spesifik bağımlı istemler (örneğin belirli formülasyon kısıtlamaları) iptal edilirken, genel istem (molekül) geçerli kalabilir.

**Örnek akıl yürütmesi** (anonimleştirilmiş):
> "İstem 1 ana bileşiğin yeniliği sorunu taşımaktadır ve hükümsüz ilan edilir. Ancak istem 4'te yer alan spesifik formülasyon özgün olup kısmen geçerli sayılır. Bu durum kısmi hükümsüzlük niteliğindedir."

**Eğilim 2 — İhtiyati tedbir kararları daha tereddütlü**

2010'lara kadar ilaç patent davalarında ilk bakışta tedbir kararı sıkça veriliyordu. Günümüzde mahkemeler:
- Patentin prima facie geçerliliğini
- Kısmi hükümsüzlük ihtimalini
- Jenerik tarafın ekonomik zararını
- Kamu sağlığı dengesini
birlikte değerlendirir; salt patentin varlığı artık yeterli görülmez.

**Eğilim 3 — İkinci tıbbi kullanım kabul edilir ama dar yorumlanır**

Swiss-type claim ve EPC-2000 purpose-limited istemler Türkiye'de patent edilebilir. Ancak:
- Tecavüz isnadı için, jenerik ilacın o spesifik endikasyon için **satıldığı** kanıtlanmalı
- Eczane pratiğinde "off-label" kullanım, jenerik firma sorumluluğu doğurmaz
- Cross-labeling (jenerik label'ında yeni endikasyonun yer alması) tecavüz teşkil eder

**Eğilim 4 — EPO kararları yorumsal kaynak olarak kabul edilir**

Özellikle EPO Board of Appeal kararları (T-decisions) ve Genişletilmiş Temyiz Kurulu G-kararları (G 2/88, G 5/83, G 1/03 vb.) bilirkişi raporlarında ve mahkeme gerekçelerinde sıkça atıf alır. Bağlayıcı değil; **yorumsal güçlü ipucu**.

**Eğilim 5 — Bilirkişi görüşü belirleyici**

Nadiren bir ilaç patent davası bilirkişi raporu olmaksızın sonuçlanır. Bilirkişiler genellikle:
- Üniversite öğretim üyesi (farmasötik kimya, farmakoloji, farmasötik teknoloji)
- Patent vekili (teknik dosya için)
- Hekim uzmanı (endikasyon ve klinik uygulanabilirlik için)

Mahkeme çoğu zaman bilirkişi raporunu kabul eder; red durumunda ek inceleme talep eder.

**Eğilim 6 — Tercüme hataları lehte yorum**

EP validation patentlerinde Türkçe tercüme orijinalinden daha geniş kapsam belirtiyorsa, **üçüncü kişi lehine** (dar kapsam) yorumlanır. Bu ilkesi SMK m. 103'te yazılıdır.

---

## 3. FSHHM (Fikri ve Sınai Haklar Hukuk Mahkemesi) pratiği

### Yetki alanları

FSHHM şunları görür:
- Patent + faydalı model tecavüzü
- Hükümsüzlük davaları
- Tedbir ve delil tespiti
- Marka ve tasarım davaları
- Haksız rekabet (fikri mülkiyet ilişkili)
- TTK m. 55 vd. ticari haksız rekabet

### İhtisaslaşmış mahkemeler

- **İstanbul**: Bakırköy 1. ve 2. FSHHM, Beyoğlu 1. FSHHM
- **Ankara**: 1., 2., 3., 4. FSHHM
- **İzmir**: 1. ve 2. FSHHM
- **Adana**, **Antalya**: Uzmanlaşmış mahkemeler
- Diğer iller: Asliye Ticaret Mahkemesi FSHHM sıfatıyla

### Tipik süreç

1. **Dava açılır** — tecavüz veya hükümsüzlük (ya da karşılıkla ikisi)
2. **Tedbir talebi** — genellikle davayla birlikte veya öncesinde
3. **Davalı cevabı** — 2 hafta + ek süreler
4. **Delil listesi** — iddia delilleri
5. **Bilirkişi incelemesi** — mahkemenin seçtiği uzman heyeti
6. **Bilirkişi raporu** — yaklaşık 6-12 ay
7. **Taraf itirazları** — rapora itiraz, ek rapor talepleri
8. **Duruşmalar** — genellikle 3-5 celse
9. **Karar** — 2-4 yıl

**Süre**: İlk derece dava ortalama 2-4 yıl; istinaf ve temyiz ile 5-7 yıl.

### Önemli usul noktaları

**Yetki itirazı**: Davalı ikametgahı veya tecavüz fiili yerindeki FSHHM yetkilidir.

**Karşı dava**: Hükümsüzlük iddiası, tecavüz davasında karşı dava olarak öne sürülebilir (SMK m. 155).

**Uzlaşma**: Mahkeme taraflar arasında uzlaşma önerebilir; kabul halinde kısa sürede sonuçlanır.

---

## 4. Danıştay — TÜRKPATENT YİDK iptal davaları

### Rol

TÜRKPATENT YİDK (Yeniden İnceleme ve Değerlendirme Dairesi) idari bir birimdir. YİDK kararları idari işlemdir ve idari yargıda iptali istenebilir.

### Yetkili mahkeme

**2020 öncesi**: Danıştay 10. veya 15. Daire (marka + patent ayrı)

**2020 sonrası**: Ankara Fikri ve Sınai Haklar İdare Mahkemesi (AFSİM) — TÜRKPATENT kararlarının iptali için özel yetki. İstinaf: Ankara Bölge İdare Mahkemesi.

### Tipik iptal sebepleri

- Patent ret kararının usulsüzlüğü (hatalı yorum)
- Üçüncü kişi görüşünün (TPO'nun) değerlendirilmemesi
- Araştırma raporunun hatalı yorumu
- Bilirkişi raporunda hata

### Süreç

1. YİDK kararına karşı 2 ay içinde dava
2. Savunma alışverişi
3. Bilirkişi incelemesi (gerekirse)
4. Karar

**Süre**: 1-3 yıl.

---

## 5. Anayasa Mahkemesi — sağlık hakkı ve mülkiyet dengesi

### Hukuki çerçeve

**Anayasa m. 17** — Yaşam hakkı
**Anayasa m. 56** — Sağlıklı çevre ve sağlık hakkı
**Anayasa m. 35** — Mülkiyet hakkı

Patent hakkı mülkiyet hakkının bir türüdür; ilaç erişimi ise sağlık hakkının yansımasıdır. İkisi arasında potansiyel gerilim vardır.

### AYM bireysel başvuru içtihadı

**İlaç erişim davaları** AYM'nin son dönem içtihadında sıkça karşılaşılan konudur. Ancak bu kararlar genellikle **SGK geri ödemesi reddi + sağlık hakkı** bağlamında (onkoloji ilaçları dahil) verilmektedir — patent doğrudan konu değildir.

**İlgili içtihat**: AYM, ilaç erişimi reddinin sağlık hakkı ihlali oluşturabileceğini ancak bu hakkın mutlak olmadığını belirtir; ekonomik imkânlar, bilimsel yeterlilik, alternatif tedavi varlığı değerlendirilir. Patent tekel hakkı, kamu sağlığı ile dengelenirken zorunlu lisans bir çözüm mekanizmasıdır.

### Patent sahipleri için AYM başvurusu

Zorunlu lisans kararı veya patentin devletleştirilmesi durumunda patent sahibi, mülkiyet hakkının ihlali gerekçesiyle AYM'ye bireysel başvuru yapabilir. Ancak Türkiye'de zorunlu lisans fiilen nadir uygulandığından bu tür başvuru örneği sınırlıdır.

---

## 6. EPO Board of Appeal — paralel yorumsal kaynaklar

### Yapısı

**EPO (European Patent Office)** — Avrupa Patent Sözleşmesi (EPC) kapsamında merkezi patent verme. Türkiye 2000'den beri EPC üyesi; EP patentleri Türkiye'de validation ile geçerli olur.

**Board of Appeal (Temyiz Kurulu)**: İlk derece inceleme ve itiraz dairesinin kararlarına karşı itiraz mercii. Kararlar "T" numarasıyla (Technical Board) yayımlanır.

**Enlarged Board of Appeal (Genişletilmiş Temyiz Kurulu)**: Hukuki ilkelerin netleştirilmesi için. Kararlar "G" numarasıyla.

### Kritik G-kararları (ilaç patentleri)

**G 5/83** — Swiss-type claim kabul edildi. "İlaç X'in B hastalığı tedavisi için kullanılan ilaç üretimi" formatının patent edilebilirliği teyit edildi.

**G 2/88** — Seçim buluşu doktrini. Bilinen bir Markush formülü içinde dar bir grup, dört şart karşılarsa ayrı patent olabilir.

**G 1/03** — İstem kapsamı yorumu + disclaimers (feragat).

**G 2/08** — EPC-2000 purpose-limited claim (ikinci tıbbi kullanım modern formatı).

**G 1/07** — Tedavi usulü ve cihaz arayüzü.

**G 3/08** — Yazılım patentleri (tıbbi yazılım dahil).

### Türkiye'de yorumsal güç

Türk yargı pratiğinde EPO G-kararları **bilirkişi raporlarında** ve **taraf dilekçelerinde** sıkça atıf alır. Mahkemeler bu kararları bağlayıcı saymaz ancak yorumsal güçlü ipucu olarak kabul eder. Özellikle:
- SMK m. 82/2 tedavi usulü istisnası — G 1/04 ve G 2/08 ile birlikte
- SMK m. 83 buluş basamağı — EPO "problem-solution approach" ile birlikte
- SMK m. 92 koruma kapsamı — G 2/88 seçim buluşu ile

---

## 7. Konu bazlı içtihat haritası

### 7.1. İkinci tıbbi kullanım

**Temel kabul**: Yargıtay Swiss-type ve EPC-2000 purpose-limited istemleri kabul eder.

**Tecavüz ispatı zorluğu**: Jenerik ilaç, orijinal endikasyon için ruhsatlandırılmış olsa bile ikinci endikasyon için off-label olarak reçetelenebilir. Eczane ve hekim sorumluluğu ayrıdır; jenerik üretici, kendi label'ında o endikasyonu yazmadığı sürece tecavüz işlememiş sayılır (genel eğilim).

**Cross-labeling**: Jenerik firma label'ında ikinci tıbbi kullanım endikasyonunu yazdıysa bu açık tecavüz oluşturur.

**Carve-out (skinny label)**: Jenerik firma ikinci endikasyonu label'ından çıkarabilir (FDA'da "Section viii statement" benzeri mekanizma Türkiye'de formal olarak yok; pratikte TİTCK kabul edebilir).

### 7.2. Seçim buluşu

**Kabul**: Yargıtay EPO G 2/88 doktrinini uygular.

**Dört şart** (seçim buluşunun geçerli olması için):
1. Seçilen bileşik, jenerik formülün spesifik örneği olarak önceden açıklanmamış
2. Seçilen dar grup, beklenmedik teknik avantaj sağlamalı
3. Seçilen grup, öncekinin özel olarak kastedildiği aralıkta olmamalı
4. Teknik etkinin varlığı deneysel olarak kanıtlanmalı

**İhlal ayrımı**: Seçim patenti, önceki Markush patentinin **kapsamından çıkmak anlamına gelmez** — ancak ayrı bir yeni patent doğurur. İki patent birbirinden bağımsız olarak ayrı hak sağlar.

### 7.3. Buluş basamağı (obviousness)

**Yargıtay eğilimi**: EPO "problem-solution approach" analitik çerçevesi kabul edilir.

**Adımlar**:
1. En yakın önceki teknik (closest prior art) tespit edilir
2. Hedef patent ile en yakın önceki teknik arasındaki teknik farklılık saptanır
3. Objektif teknik problem tanımlanır (patent sahibi ne problemi çözüyor)
4. Önceki teknik + genel uzman bilgisi, problemi çözmek için tek başına veya kombine olarak yeterli miydi?
5. Eğer yeterliyse buluş basamağı yoktur (aşikârdır)

**Pratik**: Bilirkişi raporu çoğu zaman bu çerçeveyle kurulur.

### 7.4. Yeterli açıklama (sufficiency of disclosure)

**SMK m. 92/1** — İstemler tarifname tarafından desteklenmelidir; buluş, ilgili teknoloji alanındaki uzman tarafından tekrar edilebilecek şekilde açıklanmalıdır.

**Yargıtay uygulaması**: Çok geniş Markush formülleri yeterli açıklama testinden düşebilir — başvuru sahibinin yalnız birkaç örnek verdiği, spesifik kombinasyonların elde edilmesi için "gereksiz deneme yükü" (undue burden) gerekeceği bilirkişi tarafından saptandığında kısmi hükümsüzlük verilebilir.

### 7.5. Kısmi hükümsüzlük

**SMK m. 138/3** — istemler bazında kısmi hükümsüzlük mümkündür.

**Yargıtay**: İstemler ayrı ayrı değerlendirilir; hükümsüzlük gerekçeleri (yenilik, buluş basamağı, yeterli açıklama) her istem için ayrı uygulanır.

**Uygulama**: Bir patentin 50 istemi varsa, 30'u geçersiz + 20'si geçerli çıkabilir.

### 7.6. İhtiyati tedbir

**Yargıtay 11. HD eğilimi** (2015-2024):
- Tedbir için prima facie geçerlilik gerekli
- Kısmi hükümsüzlük ihtimali güçlüyse tedbir reddedilir veya kaldırılır
- Teminat miktarı yüksek (yıllık ciro bazında hesap)
- Jenerik firma zararı mahkeme tarafından ciddi değerlendirilir
- Kamu sağlığı etkisi (ilaç erişimi) bazen değerlendirilir

**Tedbir kaldırma stratejisi** (jenerik için):
1. Karşı dava (hükümsüzlük) hızlıca açılır
2. Prima facie olarak güçlü prior art delili sunulur
3. Teminatın yüksek tutulması talep edilir (orijinatör tedbirden vazgeçebilir)
4. HMK m. 394 itiraz süreci kullanılır

---

## 8. Karar bağlayıcılığı ve öncelikler hiyerarşisi

### Türkiye hukuk sisteminde bağlayıcılık

**Bağlayıcı**:
- Anayasa Mahkemesi iptal kararları (norm denetimi)
- Yargıtay Hukuk Genel Kurulu kararları (içtihadı birleştirme gerektiren durumlarda)

**Bağlayıcı olmayan ancak güçlü etkili**:
- Yargıtay daire kararları (FSHHM için emsal ama formal bağlayıcı değil)
- Danıştay daire kararları
- EPO Board of Appeal kararları (yorumsal)
- AYM bireysel başvuru kararları

**Yorumsal kaynak**:
- Öğreti (doktrin — akademik yayınlar)
- Karşılaştırmalı hukuk

### Karar hiyerarşisi bir davada

İlaç patent davasında karar zinciri:
1. **FSHHM** (ilk derece) — olgusal + hukuki değerlendirme
2. **Bölge Adliye Mahkemesi** (istinaf) — tekrar tam inceleme
3. **Yargıtay 11. HD** (temyiz) — sadece hukuki + usul hataları

**Bozma**: Yargıtay bozarsa, FSHHM ya bozma gerekçesine uyar ya da direnir. Direnme halinde Yargıtay Hukuk Genel Kurulu karar verir — bu karar bağlayıcıdır.

### Emsal çıkarma metodolojisi

Bir dava için emsal ararken:

1. **Konu benzerliği**: Aynı tür ilaç (küçük molekül, biyolojik, vs.) + aynı tür sorun (hükümsüzlük, tecavüz, tedbir)
2. **Tarih önemi**: SMK dönemi (2017 sonrası) kararları öncelikli; önceki 551 KHK kararları geçiş süreci için
3. **Yargıtay > yerel**: Yargıtay kararı varsa öncelik
4. **Daire uyumu**: 11. HD kararları fikri mülkiyet için
5. **HGK kararları**: İçtihadın netleştiği alanlar için

---

*Karar arama UYAP ve Yargıtay bilgi sistemi üzerinde gerçek zamanlı olarak yapılmalıdır; bu dosyadaki temalar yol gösterici olup spesifik karar numaraları canlı sorgulama ile elde edilir. Belirli bir dava için detaylı arama ve bilirkişi raporu desteği bu protokolün kapsamı içindedir.*
