# references/veritabani-stratejileri.md — Farmasötik Patent Veri Tabanları ve Arama Sözdizimi

> Hiçbir tek veri tabanı tam resmi veremez. Orange Book regülatör entegrasyonu verirken, Espacenet aile ağacını, STN kimyasal topolojiyi, TÜRKPATENT Türkiye hukuki geçerliliği verir. Profesyonel patent araştırması **çok-veri tabanlı triyanglasyondur**.

## İlişkili Protokoller

- **`cpc-ipc-kodlari.md`** — Boolean sorguların CPC hiyerarşisi ile kesişimi (A61K, A61M, C07D, G16H)
- **`markush-protokol.md`** — Kimyasal yapı tabanlı arama (SureChEMBL, SciFinder, Derwent Markush) için araç seçim rehberi
- **`fto-invalidity-protokol.md` §1 Adım 3-5, §2 Adım 4-5** — Arama adımlarının FTO/Invalidity iş akışına entegrasyonu
- **`ruhsat-veri-imtiyazi.md`** — Orange Book / Purple Book ile referans ürün patent + veri imtiyazı bağı

## İçindekiler

1. Resmi regülatör veri tabanları
2. Ulusal ve bölgesel patent ofisi platformları
3. Uluslararası / uluslar-ötesi platformlar
4. Ücretli profesyonel platformlar
5. Türkiye-spesifik kaynaklar
6. Bilimsel literatür entegrasyonu
7. Boolean sözdizimi farkları — karşılaştırmalı tablo
8. Çok-veritabanı triyanglasyon protokolü
9. Sık-yapılan-hatalar

---

## 1. Resmi regülatör veri tabanları

### 1.1. FDA Orange Book (ABD — küçük moleküller)

**Tam adı**: *Approved Drug Products with Therapeutic Equivalence Evaluations*

**URL**: https://www.accessdata.fda.gov/scripts/cder/ob/

**Kapsam**:
- FDA onaylı **küçük molekül** ilaçların tam listesi
- Her ilaç için aktif patentler ve bitiş tarihleri
- Pediatrik uzatma durumu
- Terapötik eşdeğerlik kodları (AB, BX, vs. — jenerik değiştirilebilirlik)
- Veri imtiyazı bilgisi

**Önemli sekmeler**:
- **Appendix A** — Ürün ismi → aktif patentler eşleştirmesi
- **Appendix B** — Patent listesi (numara + bitiş tarihi + "drug substance", "drug product", "method of use" etiketleri)
- **Appendix C** — Veri imtiyazı eşleştirmeleri (NCE = 5 yıl, orphan = 7 yıl, pediatric extension = +6 ay vs.)

**Araştırma stratejisi**:
1. Ürün ismi veya INN ile Appendix A'dan patent listesi çıkarılır
2. Appendix B'den her patentin tipi ve bitiş tarihi teyit edilir
3. Çapraz-doğrulama: her patenti USPTO Patent Public Search'te istem metinleri için aç
4. Paragraph IV Certification durumu: **Paragraph IV Patent Certifications** ayrı listesinden takip edilir — bir patentin hükümsüzlüğüne karşı jenerik başvurunun olup olmadığını gösterir
5. Patent delisting (Orange Book'tan çıkarma) kararları — orijinatörün patentten vazgeçme stratejisi göstergesi

**Sınırlılık**: Orange Book ABD-spesifiktir; Avrupa / Türkiye / diğer pazarlar için doğrudan kullanılmaz. Ancak aktif madde ve patent ailesi buradan başlatılabilir.

### 1.2. FDA Purple Book (ABD — biyolojikler)

**Tam adı**: *Database of Licensed Biological Products*

**URL**: https://purplebooksearch.fda.gov/

**Kapsam**:
- FDA onaylı **biyolojik ürünler** (BLA — Biologic License Application)
- Biyobenzer ve değiştirilebilir (interchangeable) statü
- Ruhsat numarası (STN — Submission Tracking Number)
- Referans ürün ile biyobenzer eşleştirmesi

**Özel not**: Orange Book'un aksine Purple Book, patentleri **listelemez**. Biyolojikler için patent bilgisi ayrıca USPTO veya Lex Machina / IPWatchdog tipi hizmetlerden takip edilir. Ancak BPCIA (Biologics Price Competition and Innovation Act, 351(k) yolu) kapsamındaki patent dance (Patent Dance) sürecinde taraflar patent listelerini mübadele eder; bu kamuya açık değildir.

### 1.3. EMA (Avrupa İlaç Ajansı) — EPAR

**URL**: https://www.ema.europa.eu/

**Kapsam**: AB merkezi ruhsat ürünleri için European Public Assessment Report; ilacın klinik dosyası, ruhsat tarihi, endikasyon.

**Araştırma önemi**: 
- Gümrük Birliği alanında **ilk ruhsat tarihi** için AB merkezi ruhsat tarihi referanstır (Türkiye veri imtiyazı hesabı için kritik)
- Orphan ve pediatrik uzatma durumları burada

### 1.4. TİTCK (Türkiye) — Beşeri Tıbbi Ürün Listesi

> **MCP-FIRST [v2.0.0]** — TR ürün dosyası, holder portföyü, fiyat geçmişi, Madde 23, off-label, biyobenzer kümesi, withdrawal, batch release ve 19 dinamik modül için **TİTCK MCP (56 araç) kanonik kaynaktır**. Detaylı tool envanteri ve kullanım örüntüleri için `references/turk-mcp-entegrasyonu.md §2`. Bu bölüm yalnız MCP timeout / failure durumunda audit-trail web fallback için referanstır.

**URL**: https://www.titck.gov.tr/ / https://kdb.titck.gov.tr/

**Kapsam**: Türkiye'de ruhsatlı beşeri tıbbi ürünler; ruhsat tarihi, kısa ürün bilgisi (KÜB), endikasyonlar, fiyat (Farklı Teşhis ve Tedavi Kapsamı) tarafından tutulur.

**Araştırma önemi (web yedek katmanı)**: 
- Türkiye'deki ilk ruhsat tarihi (6 yıllık veri imtiyazı hesabı için) → MCP'de `get_drug.authorization_date`
- Endikasyon listesi (ikinci tıbbi kullanım patenti analizi için) → MCP'de `find_off_label_uses_for_drug` + `summarize_substance`
- Jenerik ruhsat durumları → MCP'de `find_shared_substance_peers` + `find_equivalent_products_by_substance`

---

## 2. Ulusal ve bölgesel patent ofisi platformları

### 2.1. USPTO Patent Public Search (ABD)

**URL**: https://ppubs.uspto.gov/

**Özellikler**:
- ABD patentleri (granted + published applications) tam metin arama
- 80+ saha kodu (field code) destekli sorgu
- CPC, USPC (eski), MPEP referansları ile sorgu
- Patent Image ve Markush structure görüntüleme
- Indirme: PDF tam metin, XML, CSV

**Temel saha kodları**:
| Saha kodu | Anlamı |
|---|---|
| `.CPC.` | CPC sınıflandırması |
| `.ICL.` | IPC sınıflandırması |
| `.AANM.` | Applicant name (başvuru sahibi) |
| `.AN.` | Assignee name (devralan) |
| `.INV.` | Inventor name (mucit) |
| `.PN.` | Patent number |
| `.APD.` | Application date |
| `.IPD.` | Issue (granted) date |
| `.ABST.` | Abstract text |
| `.CLM.` | Claim text |
| `.SPEC.` | Specification (full body) |
| `.TTL.` | Title |
| `.AB.` | Abstract (alternative) |

**Örnek sorgular**:
```
# Atorvastatin içeren formülasyon patentleri
(atorvastatin).CLM. AND CPC/A61K9/20.CPC.

# 2020 sonrası mRNA aşı patentleri
("messenger RNA" OR mRNA).ABST. AND CPC/A61K9/5123.CPC. AND .APD.>20200101

# Roche tarafından başvurulan anti-HER2 antikor patentleri
(HER2 OR ErbB2).TTL. AND ("F. Hoffmann-La Roche" OR Genentech).AN.

# Belirli bir patentin devam ve bölünmüş başvuruları
US10123456.PN. (patent numarasını aile ile birlikte aramak için Espacenet tercih edilir)
```

**Sınırlılık**: Yalnız ABD patentlerini gösterir. Küresel görünüm için Espacenet ile birlikte kullanın.

### 2.2. Espacenet (EPO)

**URL**: https://worldwide.espacenet.com/

**Özellikler**:
- 140+ milyon yayın — küresel kapsam (100+ ülke)
- **INPADOC family** — bir patentin dünya genelinde ilgili tüm başvuruları
- **Global Dossier** — aynı patentin farklı ülkelerdeki inceleme dosyaları
- Smart Search — doğal dil ile sorgu
- Advanced Search — saha kodu destekli
- Classification Search — IPC/CPC doğrudan hiyerarşi gezinme

**Temel saha kodları (Advanced Search)**:
| Saha kodu | Anlamı |
|---|---|
| `cpc` | CPC sınıflandırması |
| `ipc` | IPC sınıflandırması |
| `pa` | Patent applicant (başvuru sahibi) |
| `in` | Inventor |
| `pd` | Publication date |
| `ad` | Application date |
| `ta` | Title, abstract |
| `desc` | Description |
| `cl` | Claims |

**Örnek sorgular**:
```
# Türkiye'de geçerli enhertu patentleri
cpc=A61K39/3955 AND cpc=C07K16/32 AND (ta=trastuzumab AND ta=deruxtecan)

# Novartis CAR-T portföyü
cpc=C12N5/0783 AND pa=Novartis

# Belirli bir patentin tam ailesi
# (patent numarasını girip "Patent family" sekmesinden görülür)
```

**Özel güç**: INPADOC Family — bir ABD patentinin Türkiye'de muadili var mı? → Espacenet bunu tek tıkla gösterir.

### 2.3. TÜRKPATENT EPAAT (Türkiye)

> **MCP-FIRST [v2.0.0]** — TR ulusal patent + endüstriyel tasarım + ticari marka aramaları için **Türk Patent MCP (6 araç) kanonik kaynaktır**: `search_patents`, `get_patent_details`, `search_designs`, `get_design_details`, `search_trademarks`, `get_trademark_details`. Detay ve kullanım örüntüleri: `references/turk-mcp-entegrasyonu.md §3`. **Sınırlama**: MCP istem tam metnini vermez (sadece bibliografik); FER (First Examination Report) içeriği yoktur. Bu iki katman için EPAAT web fetch hâlâ zorunlu. Aşağıdaki bölüm hem yedek hem de MCP-üstü ham veri için referanstır.

**URL**: https://online.turkpatent.gov.tr/EPATT/

**Özellikler**:
- Türkiye ulusal başvurular + EPO validation başvuruları
- Başvuru/tescil/ret durumu
- Yıllık harç ödeme durumu (geçerlilik için kritik!)
- Hak sahibi değişiklikleri (assignment kayıtları)
- TÜRKPATENT YİDK kararları
- Araştırma ve inceleme raporları (FER, ER) — inceleme aşamasındaki başvurular için

**Araştırma stratejisi**:
1. Patent numarası veya başvuru numarası ile detay sayfa
2. "Yıllık harç durumu" kontrolü — ödenmediği yıl patent **sona erer**
3. Hak sahibi hanesinde değişiklik — lisans / devir göstergesi
4. FER (First Examination Report) içinde itiraz ve gerekçeler

**Kritik not**: TÜRKPATENT arayüzü sık güncellenir. Bazı sayfalarda CPC/IPC arama varsayılan olarak IPC'ye ayarlanmıştır; CPC sorgusu için manuel seçim gerekebilir.

### 2.4. Diğer büyük ulusal patent ofisleri

- **DPMA (Almanya)** — https://depatisnet.dpma.de/
- **INPI (Fransa)** — https://bases-brevets.inpi.fr/
- **JPO (Japonya)** — https://www.j-platpat.inpit.go.jp/
- **CNIPA (Çin)** — http://cpquery.cnipa.gov.cn/
- **CIPO (Kanada)** — https://www.ic.gc.ca/opic-cipo/cpd/eng/

Bu ofislerin ulusal platformları genellikle Espacenet ile senkronize; ancak dosya tarihçesi (file history, prosecution history) için **ulusal ofise** gitmek gerekir. Örneğin bir EP başvurusunun inceleme yazışmaları için EPO Register, bir DE-spesifik için DPMA'nın kendi register'ı.

---

## 3. Uluslararası / uluslar-ötesi platformlar

### 3.1. WIPO PATENTSCOPE

**URL**: https://patentscope.wipo.int/

**Kapsam**:
- PCT (Patent Cooperation Treaty) başvuruları
- 100+ ülkenin ulusal patent koleksiyonları
- Chemical Compound Search (SMILES destekli!)
- CLIR (Cross-Lingual Information Retrieval) — Japonca/Çince gibi dillerdeki başvuruları İngilizce arayıp bulmak

**PCT süreci ve önemi**: Bir buluş sahibi ilk başvurusunu yaptıktan sonra 12 ay içinde PCT başvurusu yapabilir; sonra 30 ay (bazı ülkelerde 31) içinde ulusal fazlara (ülke bazlı başvurular) girer. PATENTSCOPE bu "uluslararası" aşamayı ve ulusal faz girişlerini takip etmenin merkezi platformudur.

**Araştırma önemi**: Rakibin hangi ülkelerde patent koruması istediğini ulusal faz girişlerinden okuyun — örneğin yalnız US + EP + JP girdi, TR girmediyse → Türkiye pazarı için koruma yok.

### 3.2. SureChEMBL (EMBL-EBI)

**URL**: https://www.surechembl.org/

**Kapsam**:
- Patent tam metinlerinden **otomatik olarak çıkarılmış** kimyasal bileşikler
- 16+ milyon bileşik, 4+ milyon patent
- SMILES / InChI ile yapısal benzerlik arama
- Ücretsiz

**Kullanım**: Bir bileşik yapısı çizerek hangi patentlerde bahsedildiğini bulmak. **Markush tam eşleştirme yok**, ancak spesifik bileşik için metin madenciliği gücü yüksek.

### 3.3. Google Patents

**URL**: https://patents.google.com/

**Özellikler**:
- 120M+ patent ve başvuru
- Semantic search (AI tabanlı benzerlik — beta)
- Prior art öneri motoru (bir patent sayfasında "most relevant prior art")
- Citation graph görselleştirme
- Full-text PDF indirme
- Google Scholar entegrasyonu (NPL — non-patent literature)

**Sınırlılık**: Resmi ofis veri tabanları kadar güncel olmayabilir; legal status bilgisi bazen eskidir.

---

## 4. Ücretli profesyonel platformlar

### 4.1. CAS SciFinder / STN IP Protection Suite

**Satıcı**: American Chemical Society (CAS)

**Üstün özellikler**:
- 230+ milyon kimyasal bileşik
- Markush DART algoritması (jenerik formül eşleştirme)
- Reaction search (reaksiyon sorgusu)
- 1988 sonrası tam global patent kapsamı; 1961 sonrası INPI

**Kullanım alanları**: Kritik FTO, Invalidity prior art kimyasal yapısal arama, reaksiyon patentleri.

**Maliyet**: Kuruma göre yıllık $10.000–$100.000+.

### 4.2. Derwent Innovation (Clarivate)

**Satıcı**: Clarivate Analytics

**Özellikler**:
- Derwent World Patents Index (DWPI) abstract'ları — uzman editörler tarafından yeniden yazılmış özetler
- Kimyasal yapı araması (Derwent Chemistry Resource)
- Patent aileleri
- Analiz ve görselleştirme araçları

**Kullanım alanı**: Geniş landscape çalışmaları, rekabet istihbaratı.

### 4.3. Orbit Intelligence (Questel)

**Satıcı**: Questel

**Özellikler**:
- FamPat (patent aileleri veri tabanı)
- Legal status tracking
- Citation analysis
- Geostrategic mapping

### 4.4. PatBase (Minesoft)

**Satıcı**: Minesoft

**Özellikler**:
- 50M+ patent ailesi
- Gelişmiş filtreleme
- Citation & family explorer

### 4.5. PatSnap

**Satıcı**: PatSnap

**Özellikler**:
- AI tabanlı patent analitiği
- Teknoloji trendi görselleştirmeleri
- M&A ve portföy due diligence

### 4.6. Lex Machina / Docket Navigator

**Satıcılar**: LexisNexis / Docket Navigator

**Özellikler**:
- ABD federal mahkeme patent davaları
- Hakimlerin kararları, aldıkları kararların ortalama süresi
- Dava geçmişi, uzlaşma desenleri

**Kullanım alanı**: Litigation stratejisi, mahkeme seçimi (forum selection).

---

## 5. Türkiye-spesifik kaynaklar

### 5.1. TÜRKPATENT EPAAT (bkz. 2.3)

### 5.2. UYAP Mevzuat Bilgi Sistemi

**URL**: https://www.mevzuat.gov.tr/

**Kapsam**: Türkiye'nin tüm kanunları, yönetmelikleri, mülga ve güncel metinleri.

**Araştırma önemi**:
- SMK 6769 güncel metin + tadillere tam erişim
- Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği (güncel + önceki versiyonlar)
- Tıbbi Cihaz Yönetmeliği
- TÜRKPATENT Uygulama Yönetmeliği

### 5.3. Yargıtay Bilgi Sistemi

**URL**: https://karararama.yargitay.gov.tr/

**Kapsam**: 9.8+ milyon Yargıtay kararı, yerel mahkeme kararları, HGK kararları.

**Araştırma stratejisi**:
- Daire bazlı filtre: 11. HD (Hukuk Dairesi) — fikri mülkiyet, rekabet, şirketler hukuku
- Anahtar kelime: "patent tecavüzü", "hükümsüzlük", "ikinci tıbbi kullanım", "Bolar", "ihtiyati tedbir"
- Tarih bazlı filtre: 2017 sonrası SMK 6769 dönemini işaret eder

### 5.4. Danıştay Bilgi Sistemi

**URL**: https://www.danistay.gov.tr/

**Kapsam**: TÜRKPATENT YİDK kararlarına karşı idari iptal davaları. 10. Daire (Vergi) ve 15. Daire (fikri mülkiyet) özellikle ilgili.

### 5.5. Anayasa Mahkemesi (AYM)

**URL**: https://www.anayasa.gov.tr/

**Kapsam**: Bireysel başvuru kararları. Sağlık hakkı (Anayasa m. 17/56) ile mülkiyet hakkı (m. 35) dengesi; özellikle zorunlu lisans ve kamu yararı tartışmalarında.

### 5.6. TİTCK Mevzuat Portalı

**URL**: https://titck.gov.tr/mevzuat

**Kapsam**: Sadece sağlık mevzuatı; TİTCK Kılavuzları, kararları, izin süreçleri.

### 5.7. Resmi Gazete arşivi

**URL**: https://www.resmigazete.gov.tr/

**Araştırma**: Yeni yönetmelik ve kanun değişikliklerinin ilk yayımı; aksi belirtilmedikçe yürürlük tarihi yayım tarihinden itibaren hesaplanır.

---

## 6. Bilimsel literatür entegrasyonu (NPL — non-patent literature)

Patent davalarında prior art patent dışı kaynaklardan da gelebilir:

- **PubMed** — https://pubmed.ncbi.nlm.nih.gov/ (36M+ hakemli makale)
- **Google Scholar** — https://scholar.google.com/ (semi-peer-reviewed + patent + tez)
- **YÖK Tez** — https://tez.yok.gov.tr/ (Türkiye doktora ve yüksek lisans tezleri; FTO için kritik çünkü Türkçe tezler uluslararası aramalarda gözden kaçar)
- **bioRxiv / medRxiv** — https://www.biorxiv.org/ (preprintler; priority date delili olarak kabul edilir)
- **ClinicalTrials.gov** — https://clinicaltrials.gov/ (klinik çalışma kayıtları, prior art olarak alınabilir)
- **WHO ICTRP** — https://trialsearch.who.int/ (küresel klinik çalışma kayıtları)

Bu kaynaklar `medsearch` skill composability ile tetiklenebilir.

---

## 7. Boolean sözdizimi farkları — karşılaştırmalı tablo

| Operatör | USPTO | Espacenet | WIPO | TÜRKPATENT EPAAT |
|---|---|---|---|---|
| AND | `AND` | `AND` | `AND` | `AND` |
| OR | `OR` | `OR` | `OR` | `OR` |
| NOT | `ANDNOT` | `NOT` | `NOT` | `NOT` |
| Truncation (kesme) | `$` veya `*` | `*` | `*` | `*` |
| Phrase | `"..."` | `"..."` | `"..."` | `"..."` |
| Yakınlık | `ADJ` | — (yok) | `NEAR5` | — (yok) |
| Same paragraph | `SAME` | — | — | — |
| Field prefix | `.CPC.` (çevre nokta) | `cpc=` | `CPC:` | `cpc:` veya form seçimi |

**Pratik**: USPTO sorgularını Espacenet'e kopyalarken operatörler yeniden yazılmalıdır; otomatik çeviri yoktur.

---

## 8. Çok-veritabanı triyanglasyon protokolü

### Adım 1 — Kavramsal haritalama (tüm araştırmalar için zorunlu)
- INN, ticari marka, CAS numarası, SMILES, InChI, kimyasal eşanlamlı, mekanizma, terapötik sınıf, endikasyon MeSH, IPC/CPC kodları bir **konsept tablosuna** yazılır.
- En az 3 farklı isimlendirme/varyasyon her konsept için listelenir.

### Adım 2 — Regülatör referansları
- Orange Book (ABD küçük molekül) veya Purple Book (biyolojikler) → Aktif patentler + bitiş tarihleri
- EMA EPAR (AB) → ilk ruhsat tarihi
- TİTCK (Türkiye) → yerel ruhsat durumu

### Adım 3 — Ulusal patent ofislerinde çekirdek sorgu
- USPTO Patent Public Search → ABD patentleri tam metin
- Espacenet → Küresel görünüm + INPADOC aileleri
- TÜRKPATENT EPAAT → Türkiye geçerlilik + yıllık harç durumu

### Adım 4 — Kimyasal yapısal arama
- SureChEMBL (ücretsiz) veya SciFinder (ücretli) → hedef molekül / çekirdek yapı üzerinden
- Markush eşleştirme yalnızca ücretli platformlarda güvenilir

### Adım 5 — NPL (bilimsel literatür)
- PubMed + Google Scholar + bioRxiv → prior art destekleyici yayınlar
- YÖK Tez → Türkçe akademik literatür

### Adım 6 — Legal ve dava arka planı
- UYAP Mevzuat → güncel mevzuat
- Yargıtay Bilgi Sistemi → emsal kararlar
- Lex Machina / Docket Navigator → ABD dava geçmişi (varsa)

### Adım 7 — Çapraz doğrulama
- Her bulgu en az **2 ayrı kaynaktan** teyit edilmelidir
- Çelişki çıkarsa birincil kaynak (patent ofisi resmi kaydı) tercih edilir

### Adım 8 — Raporlama
- Her iddiaya kaynak numarası + erişim tarihi
- "Bilgi eksikliği" olan alanlar açıkça belirtilir (ör. "TÜRKPATENT EPAAT'ta yıllık harç durumu son ödeme tarihi netleştirilemedi")

---

## 9. Sık-yapılan-hatalar

**Hata 1**: Orange Book'u "küresel patent listesi" zannetmek. Orange Book yalnız ABD FDA onaylı ürünlerin **ABD** patentlerini listeler.

**Hata 2**: Espacenet family = tam patent ailesi sanmak. Espacenet **INPADOC** ailesini gösterir; bu çoğu zaman tam aile ile aynı olsa da bazen daha geniş (paten örnekleri zincirini gösterir) veya daha dar (sadece formal priority bağlantılı) olabilir. Tam aile için "Extended family" sekmesine bakın.

**Hata 3**: TÜRKPATENT EPAAT'ta yıllık harcın ödenmiş olmasını patent geçerliliği sanmak. Harç ödenmiş olabilir ancak patent TÜRKPATENT YİDK tarafından ret edilmiş olabilir veya FSHHM tarafından hükümsüz kılınmış olabilir. Status bilgisi ayrıca kontrol edilmelidir.

**Hata 4**: USPTO'da `.CPC.` ve `.ICL.` ayrımını atlamak. `.CPC.` CPC koduna, `.ICL.` IPC koduna karşılık gelir; karıştırmak boş sonuç verir.

**Hata 5**: Google Patents'ı resmi kaynak sanmak. Google Patents hızlı öntaramada çok faydalı, ancak legal status ve tam dosya geçmişi için resmi ofise (USPTO, EPO, TÜRKPATENT) gitmek gerekir.

**Hata 6**: SureChEMBL'in Markush kapsamını analiz ettiğini sanmak. SureChEMBL spesifik bileşik metin madenciliği yapar; Markush jenerik formülünün kapsam kontrolü STN sistemlerinde yapılır.

**Hata 7**: Türkiye araştırmasında yalnız Espacenet'e güvenmek. Espacenet TR başvuruları için kısmi kapsama sahiptir (bazen gecikmeli); Türkiye-spesifik için **mutlaka TÜRKPATENT EPAAT** kullanılmalıdır.

**Hata 8**: Ücretli platform sonuçlarını tek kaynakla sunmak. SciFinder veya Derwent tek başına kullanıldığında metadata kaydı eksik olabilir; resmi ofis kaydı ile çapraz doğrulama zorunludur.

**Hata 9**: Prior art tarihlerinin "öncelik tarihi"ne göre değerlendirilmediğini unutmak. Invalidity için **saldırılan patentin öncelik tarihinden önce** yayımlanmış prior art arar — yayın tarihi, yapım/icat tarihi değil.

**Hata 10**: Paywall engellerinin araştırmayı sınırlamasına izin vermek. PubMed Central (PMC) açık erişim alternatifi, Sci-Hub etik/hukuki olarak kaçınılır ancak açık-erişim versiyon her zaman aranmalıdır; yazarın kurumsal sayfası veya ResearchGate faydalı olabilir.

---

*Veri tabanı peyzajı hızla değişir. Yeni platformlar (ör. lens.org, dimensions.ai, PatSeer) ortaya çıkarken mevcutlar güncellenir. Yıllık veri tabanı denetimi önerilir.*
