# references/markush-protokol.md — Markush Yapıları ve Kimyasal Topoloji Protokolü

> **Farmasötik patent araştırmasının en tehlikeli tuzağı**, spesifik bir molekülün rakip patentin **jenerik Markush formülünün** kapsamında olduğunu fark etmemektir. Anahtar kelime aramaları ve klasik alt-yapı sorguları bu tuzağı büyük ölçüde kaçırır. Bu protokol, Markush risk analizini sistemleştirir.

## İlişkili Protokoller

- **`cpc-ipc-kodlari.md`** — C07D (heterosiklik), C07K (peptid), A61K31/* (organik aktif) Markush yoğun CPC dalları
- **`veritabani-stratejileri.md`** — SureChEMBL (ücretsiz), SciFinder/STN IP Suite, Derwent Markush, SureChEMBL-Patents yapısal arama araçları
- **`fto-invalidity-protokol.md` §1 Adım 6 + §2 Adım 6** — Kimyasal yapısal arama adımı ve Markush prior art analizi
- **`ictihat-emsal.md` §6 + §7.2** — EPO G 2/88 (seçim buluşu doktrini) ve Türkiye'de Markush yorumu

## İçindekiler

1. Tarihsel bağlam ve yasal temel
2. Markush formülünün anatomisi
3. Dört varyasyon tipi
4. Jenerik düğümler sözlüğü
5. Kimyasal patent ihlali nasıl doğar
6. Araştırma araçları ve sınırlılıkları
7. Markush sorgu metodolojisi
8. Örnek vaka çalışmaları
9. Sık-düşülen hatalar

---

## 1. Tarihsel bağlam ve yasal temel

**1924** — Eugene Markush, "Pirazolon Boyası ve Yapım Usulü" başvurusunda aktif bileşeni tek bir kimyasal formül yerine **jenerik varyasyon listesi** olarak tanımladı. Başvuru USPTO tarafından kabul edildi; İKİNCİL Commissioner Decision ile "Markush claim" doktrini resmileşti.

**1940'lar sonrası** — Tüm büyük patent ofisleri (USPTO, EPO, JPO, SIPO, TÜRKPATENT) Markush istemlerini kabul etti. EPO G 2/88 ve G 1/03 kararları Markush kapsamının yorumuna dair çerçeveyi çizdi.

**Yasal gerekçe**: Bir kimyasal keşif genellikle tek bir molekül değil, **ortak çekirdek + değişken periferi** şeklinde bir "ailedir". Her üyeyi tek tek isimlendirerek başvuru yapmak pratikte imkânsızdır (milyonlarca varyasyon). Markush formülasyonu bu aileyi tek istemde tanımlar.

**Türkiye**: SMK 6769 m. 92/1 koruma kapsamı istem metni üzerinden belirlenir; Markush formülü içeren istemler, formülde ifade edilen tüm spesifik bileşikleri kapsar. Yargıtay 11. HD, 2017/4518 E. kararında bir Markush formülünün kapsamına giren spesifik bileşiğin izinsiz üretiminin patent tecavüzü oluşturduğunu teyit etmiştir.

---

## 2. Markush formülünün anatomisi

Tipik bir Markush istemi şu yapıyı taşır:

```
Formula (I):

        R1
        |
    Ar—X—Y—N—R2
        |
        R3

wherein:
- Ar is selected from phenyl, naphthyl, or 5- or 6-membered heteroaryl;
- X is O, S, NH, or a bond;
- Y is C1-C6 alkyl, optionally substituted with halogen;
- R1, R2, R3 are independently H, C1-C4 alkyl, or together with the nitrogen form a 5- or 6-membered ring;
- n is an integer from 1 to 4.
```

### Bileşenler

1. **Çekirdek yapı (scaffold)** — Ar—X—Y—N üçgeni; tüm varyantların paylaştığı iskelet.
2. **Yer tutucular (R groups)** — R1, R2, R3, X, Y; her biri ayrı bir varyasyon ekseni.
3. **Substituent seçenekleri** — her yer tutucu için izin verilen kimyasal grupların listesi.
4. **Kısıtlamalar (provisos)** — bazı kombinasyonların dışlanması (ör. "with the proviso that when X is O, R1 is not hydrogen").

### Yorum kuralı

Formül içindeki **her olası kombinasyon** açıkça isimlendirilmiş kabul edilir. Yukarıdaki örnekte teorik olarak milyonlarca spesifik molekül kapsanır; başvuru sahibi bunları örnek olarak vermese dahi hepsi korunur (ancak "yeterli açıklama" ve "destekleme" gereklilikleri bu kapsamı sınırlayabilir — bkz. invalidity protokolü).

---

## 3. Dört varyasyon tipi

### 3.1. Sübstitüsyon (Değiştirme) Varyasyonu — en yaygın

Belirli bir yer tutucu için izin verilen alternatif substituent grupları listesi.

**Örnek**: 
```
R1 is hydrogen, halogen, C1-C4 alkyl, C1-C4 alkoxy, hydroxy, nitro, or amino
```

**Araştırma implikasyonu**: Hedef molekülünüzdeki R1 pozisyonunda bir "—OCH3" varsa, yukarıdaki formülün C1-C4 alkoxy kapsamında olur ve patent ihlali oluşur.

### 3.2. Pozisyonel Varyasyon

Değişken grubun çekirdek üzerindeki **pozisyonu** sabit değildir; birden fazla aromatic pozisyonda bulunabilir.

**Örnek**:
```
"a substituent R4 at position 3, 4, or 5 of the phenyl ring"
```
Ya da daha geniş:
```
"R4 substituent at any position on the aromatic ring"
```

**Araştırma implikasyonu**: Orto, meta, para izomerlerin hepsi kapsanır. Hedef molekülünüzdeki substituent'in **hangi pozisyonda** olduğu çoğu zaman önemlidir, ama Markush yer tutucusu "any position" derse hepsi korunur.

### 3.3. Frekans Varyasyonu

Belirli bir grubun **tekrar sayısı** değişkendir.

**Örnek**:
```
"—(CH2)n— wherein n is an integer from 1 to 10"

"a polyethylene glycol chain containing 4 to 40 repeating units"
```

**Araştırma implikasyonu**: Zincir uzunluğu, PEGilasyon derecesi gibi özellikler. n=7 bir zincir, n=1-10 Markush'unun tam içine girer.

### 3.4. Homoloji Varyasyonu — en aldatıcı olan

Yer tutucu **spesifik bir atom veya grup yerine geniş bir kimyasal aileyi** temsil eden jenerik düğüm ile ifade edilir.

**Örnek**:
```
"Ar represents any 5- or 6-membered aromatic ring containing 0-3 heteroatoms selected from N, O, or S"
```

Bu tek ifade şunları kapsar:
- Fenil (0 hetero atom)
- Piridin, pirimidin, triazin (N)
- Furan, pirol, tiyofen (diğer heteroatomlar)
- İmidazol, pirazol, oksazol, tiyazol, izoksazol, izotiyazol
- 1,2,3-triazol, 1,2,4-triazol, 1,3,5-triazin, tetrazol
- Yüzlerce kombinasyon

**Araştırma implikasyonu**: Molekülünüzde "benzotiyazol" varsa ve patent "Ar represents any 5- or 6-membered aromatic ring containing 0-3 heteroatoms" diyorsa, tiyazol kısmı kapsamda kalır (halka füzyonuyla ilgili başka bir istem de varsa tam ihlal doğrulanır).

---

## 4. Jenerik düğümler sözlüğü

Patent ofislerinin resmi Markush araçlarında (özellikle STN IP Protection Suite ve CAS SciFinder) kullanılan **jenerik düğüm** terimleri — bu kodlar istem metninde geçer ve kimyasal çizim araçlarında yorumlanır:

| Düğüm | Anlamı | Örnek kapsadıkları |
|---|---|---|
| **A** | Any atom (hidrojen hariç) | C, N, O, S, F, Cl, Br, I, P, B vs. |
| **Q** | Any heteroatom | N, O, S, P, F, Cl, Br, I |
| **M** | Any metal atom | Na, K, Ca, Mg, Fe, Zn, Cu, Pt vb. |
| **X** | Any halogen | F, Cl, Br, I |
| **Ak** | Any alkyl chain | —CH3, —C2H5, —C3H7, ... |
| **Cb** | Any carbocyclic (halkalı karbon) | Siklopentan, sikloheksan, benzen |
| **Cy** | Any cyclic group | Karbosiklik + heterosiklik hepsi |
| **Hy** | Any heterocyclic | Piridin, pirazin, pirol, furan |
| **Ar** / **ARY** | Any aromatic group | Benzen, naftalen, indol, piridin vs. |
| **HET** | Any heterocycle (ARY'nin non-aromatik versiyonu) | Piperidin, morfolin, piperazin |
| **CHK** | Any hydrocarbon chain | Doymuş ve doymamış karbon zincirleri |

**Pratik**: Bir patent metninde "R is selected from alkyl, cycloalkyl, or heteroaryl" ifadesi, özünde **Ak ∪ Cb ∪ ARY** birleşimini temsil eder. STN sistemlerinde bu birleşim topolojik olarak eşleştirilir.

---

## 5. Kimyasal patent ihlali nasıl doğar?

**Temel mantık**: Spesifik bir bileşik, Markush formülünün "her olası kombinasyonu" açıkça isimlendirilmiş sayılacağı için, kimyasal topolojik olarak o formüle uyuyorsa patent kapsamındadır.

### Değerlendirme adımları

1. **Hedef molekülün standardize kimyasal gösterimi** — SMILES, InChI, IUPAC ismi oluşturulur.
2. **Patent formülünün parse edilmesi** — çekirdek ve her yer tutucunun olası grupları bir set olarak çıkarılır.
3. **Eşleştirme (matching)** — Hedef molekülün her yapısal özelliği (çekirdek + her bağlantı noktasındaki grup) patent formülünün ilgili yer tutucusuna düşer mi diye kontrol edilir.
4. **Provisos kontrolü** — Patent metnindeki "with the proviso that..." kısıtlamaları uygulanır.
5. **Örneklendirmeyle doğrulama** — Patent açıklamasındaki örnekler (Examples) hedef molekülün uygulanan sınıfta olduğunu gösteriyor mu?

### Örnek

Patent Formula (I):
```
Ar—CH2—C(O)—NH—R1
wherein Ar is phenyl optionally substituted with 1-3 halogen atoms;
R1 is C1-C6 alkyl or cycloalkyl.
```

Hedef molekül: **2-(4-klorofenil)-N-sikloheksil-asetamid** (SMILES: `ClC1=CC=C(C=C1)CC(=O)NC2CCCCC2`)

Analiz:
- Ar = 4-klorofenil (fenil + 1 klor = fenil optionally substituted with 1-3 halogen → **KAPSANIR**)
- —CH2—C(O)—NH— = çekirdek aynen eşleşiyor → **KAPSANIR**
- R1 = sikloheksil (C6 siklik = cycloalkyl → **KAPSANIR**)

**Sonuç**: Hedef molekül patent istemi kapsamındadır. Satış/üretim patent ihlali oluşturur (aksi iddia edilmedikçe).

---

## 6. Araştırma araçları ve sınırlılıkları

### 6.1. Profesyonel (ücretli) araçlar

**CAS SciFinder / STN IP Protection Suite**
- Dünyanın en kapsamlı kimyasal patent veri tabanı (CAS, 230+ milyon bileşik)
- **Markush DART** algoritması — çizilen spesifik bir bileşiğin, veri tabanındaki Markush formüllerinden hangilerinin kapsamında olduğunu topolojik olarak test eder
- Jenerik düğüm (A/Q/M/Ak/Cb/ARY/HET) destekli çizim arayüzü
- 1988 sonrası tam global patent kapsamı; 1961 sonrası INPI (Fransa)
- **Maliyet**: Yıllık $10.000-$100.000+ (kullanıcı bazlı)

**Derwent Innovation / Clarivate**
- Merck Index + Derwent World Patents Index (DWPI) abstract'ları ile zenginleştirilmiş
- Kimyasal yapı çizimi destekli Markush eşleştirme (Derwent Chemistry Resource)
- **Maliyet**: Kuruma göre $15.000+

**Orbit Intelligence / Questel**
- FamPat veritabanı üzerinden global patent aileleri
- Chemical search modülü (CASrn + InChI eşleştirme)

### 6.2. Ücretsiz (limitli) alternatifler

**Espacenet (EPO)** — 140+ milyon yayın, metin-tabanlı arama + "smart search". Kimyasal yapı çizimi **YOK**. Markush eşleştirme **YOK**. Ancak:
- Kimyasal ad veya CAS numarası ile arama yapılabilir
- IPC/CPC kodları üzerinden yapısal sınıfa erişim
- Örneğin C07D 487 altındaki tüm patentleri listelemek mümkün

**USPTO Patent Public Search** — ABD patent metinleri tam erişim, Boolean + saha kodu gelişmiş arama. Kimyasal yapı çizimi **YOK**.

**Google Patents** — Metin arama, semantic search (beta), indirilebilir PDF. Kimyasal yapı çizimi **YOK**, ancak metindeki SMILES/InChI referansları yakalanabilir.

**PubChem (NIH)** — 100+ milyon bileşik, yapısal benzerlik araması mevcut; ancak patent veri tabanı ile entegrasyon sınırlı. Bir bileşiğin CID'sini bulup patent atıflarını takip etmek için kullanılır.

**ChemSpider (Royal Society of Chemistry)** — Benzer şekilde yapısal arama, patent bağlantıları sınırlı.

**SureChEMBL (EMBL-EBI)** — Patent tam metinlerinden otomatik çıkarılmış 16+ milyon kimyasal bileşik. Ücretsiz. SMILES eşleştirme mümkün. **Markush desteği KISITLI** (tam topolojik eşleştirme yok), ancak spesifik bileşik metin eşleştirmesi güçlüdür.

### 6.3. Ücretsiz alternatiflerin sınırı

Tek başına ücretsiz araçlarla tam Markush kapsam analizi **yapılamaz**. Riski azaltmak için:

1. Espacenet + CPC kodu → ilgili teknoloji alanının tam patent listesi
2. SureChEMBL → yapısal benzerlik raporu (spesifik bileşikler bazında)
3. Patent tam metinlerini okuyarak Markush istemlerinin sınırlarını manuel yorum
4. Kritik FTO kararları için profesyonel bir araçla doğrulama **zorunludur**

---

## 7. Markush sorgu metodolojisi

### 7.1. "Önce çevre, sonra merkez" yaklaşımı

Markush formülünün tam eşleştirilmesi maliyetlidir. Etkin strateji:

1. **Faz 1 — CPC filtreleme**: İlgili teknoloji alanının tam CPC alt-ağacı (örn. C07D 487 + A61K 31/519) ile sorgu → 5.000-50.000 belge.
2. **Faz 2 — Çekirdek yapı kimyasal arama**: SureChEMBL veya PubChem üzerinden hedef molekülün çekirdek yapısı benzerliği ≥80% → 100-1.000 belge.
3. **Faz 3 — Manuel istem okuması**: İlk 50-100 en-alakalı belgenin bağımsız istemleri okunur; Markush içerenler işaretlenir.
4. **Faz 4 — Topolojik eşleştirme**: Profesyonel araçla kapsam testi (veya manuel yorum).
5. **Faz 5 — Provisos kontrolü**: İsteme giren ama kısıtlamayla dışlanan bileşik olup olmadığı teyit edilir.

### 7.2. "Geniş çerçeveden daralt" yaklaşımı

Patent ailesi sorgulaması şu genişlikten dar: 
- **Tüm ilgili patentler** (IPC sınıfı) → binlerce
- **Aynı şirketin patentleri** (assignee) → yüzlerce
- **Aynı mucit grubu** (inventor) → onlar
- **Patent ailesindeki üye ülkeler** (INPADOC) → ulus-bazlı filtre

Her daralma aşamasında Markush istemleri incelenir; en tehlikeli genellikle ilk başvuruda yer alan ve sonra devam/bölünmüş başvurularla dar istemlere ayrılan "ebeveyn" patenttir.

### 7.3. "Öncelik tarihini kilitle" prensibi

Her Markush eşleştirme sorusu **belirli bir zaman noktasında** sorulur. Örnek:
- Hedef molekülüm **2024'te sentezlendi** → Sadece 2024'ten **önce** başvurulan Markush patentleri ihlal yaratabilir.
- Eğer patent başvurusu 2024'ten sonra yapıldıysa, invalidity açısından hedef molekül **prior art** olabilir (başvurunun yenilik sorununu doğurur).

---

## 8. Örnek vaka çalışmaları

### Vaka 1: Seçim buluşu (Selection invention)

**Durum**: 1995'te X şirketi bir Markush formülü patenti aldı: 
> "C1-C4 alkyl substituted imidazoles having anti-inflammatory activity"

(Bu, **binlerce** teorik alkyl-imidazol varyantını kapsar.)

**2005'te** Y şirketi, bu Markush içindeki spesifik bir bileşiği — **2-etil-4-metil-imidazol** — izole edip özel bir in vivo potens gösterdi. Y, "bu spesifik bileşik özel teknik etki sağlar" argümanıyla yeni (seçim) patent almaya çalıştı.

**EPO doktrini (G 2/88)**: Seçim buluşu geçerlidir ancak dört şart sağlanmalı:
1. Seçilen bileşik, jenerik formülün spesifik bir örneği olarak daha önce **açıklanmamış** olmalı.
2. Seçilen dar grup, jenerik formülün diğer üyelerine göre **beklenmedik bir teknik avantaj** sağlamalı.
3. Seçilen dar grup, öncekinin "özel olarak kastedildiği" bir aralıkta olmamalı.
4. Tüm seçilen grup için teknik etkinin varlığı deneysel olarak kanıtlanmalı.

**Pratik implikasyon**: Y'nin patenti geçerli olabilir, ancak mahkemede X Markush patentinin **kapsamında** olup olmadığı ayrı bir tecavüz sorusudur. Seçim buluşu **patent edilebilirlik** sağlar ama **ihlal kalkanı değildir** — Y, kendi bileşiğini üretmek için X'in Markush patentinin süresi bitene kadar lisans almak zorunda kalabilir.

### Vaka 2: Mozaik anticipation

**Durum**: Z şirketi 2020'de bir pirimidin-kinaz inhibitörü patenti başvurdu. 

**Jenerik prior art araştırması**: 2010'da W şirketinin Markush patentinde pirimidin + piperidin kombinasyonu açıklanmış. 2015'te V şirketinin başka bir patentinde aynı pirimidin çekirdeği + kinaz inhibitör aktivitesi yayımlanmış. 

Z'nin spesifik bileşiği, W ve V'nin birleştirilmiş açıklamaları kapsamında olabilir → Z'nin patenti "buluş basamağı yoksunluğu" (obviousness) nedeniyle geçersiz iddia edilebilir.

### Vaka 3: Homoloji tuzağı

**Durum**: A şirketi 1998'de bir patent aldı: 
> "Ar—O—CH2—COOH compounds, wherein Ar is any 5- or 6-membered aromatic ring optionally substituted."

**2015'te** B şirketi spesifik olarak **1-metil-pirazol-3-il-oksiasetik asit** sentezledi ve ticarileştirmeye hazırlandı. 

**Analiz**: 1-metil-pirazol-3-il bir 5-üyeli aromatik halka (pirazol) üzerinde metil substituenti taşıyor → A'nın Markush formülündeki "Ar is any 5- or 6-membered aromatic ring optionally substituted" kapsamına giriyor.

**Sonuç**: B, kendi ürünü için A'nın 1998 patentinden lisans almak zorunda. A'nın patenti 1998+20=2018'e kadar geçerli; B bu tarihten önce satamaz (Bolar istisnası dışında üretim denemeleri yapabilir).

---

## 9. Sık-düşülen hatalar

**Hata 1**: Sadece tam eşleşme arıyorum. Markush formülleri **jenerik** kapsamlıdır; tam eşleşme gerekmez, alt-set olarak düşmesi yeterlidir.

**Hata 2**: "Patent 20 yıllık, muhtemelen süresi doldu." Öncelik tarihinden (priority date) 20 yıldır, başvuru tarihi değil. Ayrıca SPC (supplementary protection certificate, Türkiye'de yok ama EP/US'ta var) 5 yıla kadar uzatabilir.

**Hata 3**: Sadece tek bir patenti analiz etmek. Markush patentleri aileler oluşturur; ebeveyn + devam + bölünmüş + terminal disclaimer zincirleri bütün olarak incelenmelidir.

**Hata 4**: Provisos'u görmemek. Patent istemi "except compounds of formula X, Y, Z" tarzı kısıtlamalar içerebilir. Hedef bileşik kısıtlanan sete giriyorsa patentin kapsamında DEĞİLDİR.

**Hata 5**: Kimyasal eşdeğeri (bioisosteres) gözden kaçırmak. —OH yerine —NH2, —O— yerine —S—, fenil yerine piridin — bu tür küçük değişimler Markush formülünün homoloji düğümlerine düşer ve patent ihlali yaratabilir.

**Hata 6**: Yeterli açıklama (sufficiency of disclosure) argümanıyla Markush'u geçersiz saymak. Teorik olarak geniş bir Markush, eğer başvuru sahibi sadece birkaç örnek verdiyse, "undue burden" argumentumu ile kısmen geçersiz kılınabilir. Ancak bu **mahkeme kararıyla** olur; FTO raporunda patent **geçerli varsayılır**.

**Hata 7**: Patent tarandığında istemleri değil özeti (abstract) okumak. Özet, hukuki kapsamı bağlamaz; istem (claim) metni esastır. Özette dar anlatılan bir patent, istemlerde çok geniş kapsamlı olabilir.

**Hata 8**: İstem bağımlılık zincirini takip etmemek. "Claim 5 depends on claim 1" → bağımsız istem 1'in tüm şartları ve bağımlı istem 5'in ek şartları birlikte kapsanır. Bağımlı istemler tek başına değerlendirilemez.

---

*Kritik FTO kararlarında Markush analizinin ücretli bir araçla (STN SciFinder, Derwent, Orbit) doğrulanması profesyonel standarttır. Ücretsiz alternatifler ön-triyaj amaçlıdır; kesin yasal görüşe yeterli değildir.*
