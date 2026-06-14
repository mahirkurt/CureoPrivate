# references/yeni-modaliteler.md — Yeni Modaliteler İçin Modalite-Spesifik Patent Protokolü

> Farmasötik IP'nin klasik (küçük molekül + biyolojik) analitik çerçevesi, son 15 yılın **yeni modaliteleri** (ADC, CAR-T, mRNA-LNP, gene therapy, siRNA, xenotransplantation, cell-based vaccines) için yetersizdir. Her modalitenin patent kuvveti profili, Markush yapısı, freedom-to-operate stratejisi ve regülatör yolu farklıdır. Bu protokol, modalite-bazlı derin daldırmalar sunar.

## İlişkili Protokoller

- **`cpc-ipc-kodlari.md`** — Her modalitenin CPC taksonomisi: ADC (C07K 16/00 + A61K 47/68), CAR-T (C12N 5/0783), mRNA (C07H 21/02 + C12N 15/11), gene therapy (C12N 15/85)
- **`markush-protokol.md`** — Payload + linker + toxin Markush stratejisi; siRNA sekans Markush analizi
- **`biyobenzer-yol.md`** — Yeni modaliteler için biyobenzer regülatör çerçevesi henüz olgunlaşmamış durumdadır
- **`patent-degerleme.md`** — Modalite-spesifik royalty stack + NPV çarpanları
- **`fto-invalidity-protokol.md`** — Her modalite için FTO'nun modifiye iş akışı
- **`tibbi-cihaz-uts.md`** — Gene therapy viral vektör üretim cihazı + CAR-T prodüksiyon cihazları

## İçindekiler

1. Yeni modaliteler genel kıyaslama
2. ADC (Antibody-Drug Conjugate)
3. CAR-T (Chimeric Antigen Receptor T-cell therapy)
4. mRNA-LNP (mRNA ile Lipid Nanoparticle)
5. siRNA / ASO (antisense oligonucleotide)
6. Gene Therapy (AAV, lentiviral vektörler)
7. Xenotransplantation ve cell-based therapies
8. Yapay zekâ + dijital terapötikler
9. Modalite-spesifik regülatör kesişim
10. Modalite-spesifik değerleme çarpanları

---

## 1. Yeni modaliteler genel kıyaslama

### Modalite × IP Profili matrisi

| Modalite | Temel birim | IP karmaşıklığı | Patent kuvveti | Biyobenzer zorluğu | Pazar $ (2024) |
|---|---|---|---|---|---|
| ADC | mAb + linker + payload | **Yüksek** (3 patent ailesi + conjugation) | Yüksek | Zor — proses çeşitliliği | $13B (2024) |
| CAR-T | T-hücre + CAR receptor | **Çok Yüksek** (manufacturing + construct) | Orta-Yüksek | Çok zor — kişiselleştirme | $5B (2024) |
| mRNA-LNP | mRNA + LNP formülasyon | **Çok Yüksek** (Acuitas LNP royalty stack) | Orta | Zor — LNP patent duvarı | $60B (COVID ile zirve 2022) |
| siRNA | Oligonükleotit | Yüksek (sekans + konjugasyon) | Yüksek | Zor (sekans patenti) | $3B (2024) |
| AAV gene therapy | AAV + transgen | **Yüksek** (serotype + payload) | Yüksek | Çok zor — kişiselleştirme | $3B (2024) |
| Lentiviral | Lentivirus + transgen | Yüksek | Orta | Zor | — |
| Xenotransplantation | Modifikasyonlu domuz organı | **Çok Yüksek** (gene editing + immune) | Yüksek | Yok (bireysel) | Preklinik |
| AI diagnostics | Software + training data | Yüksek (algoritma + veri) | Orta-düşük | Yok (yazılım) | $5B (2024) |

## 2. ADC (Antibody-Drug Conjugate)

### Teknoloji anatomisi

ADC üç bileşenden oluşur:
- **Antikor** (targeting)
- **Linker** (cleavable veya non-cleavable)
- **Payload** (sitotoksik ilaç)

Her bileşen **ayrı patent ailesi** oluşturabilir → ADC için tipik 3-5 patent kaynak lisansı.

### Örnek kompozisyon — trastuzumab deruxtecan (T-DXd, Enhertu)

- Antikor: trastuzumab (HER2) — Genentech, originalde Roche
- Linker: GGFG tetrapeptid + maleimide — Daiichi Sankyo
- Payload: exatecan türevi deruxtecan — Daiichi Sankyo
- Conjugation teknoloji: random lizin konjugasyonu — Daiichi Sankyo

### Kritik CPC kodları

- **C07K 16/00** — immünoglobulinler
- **A61K 47/68** — antikor ilacı konjugatları (özel alt-sınıf)
- **A61K 47/69** — taşıyıcılar
- **A61P 35/00** — antineoplastik aktivite

### Patent portföyü stratejisi

**Orijinatör cephesi**:
- Payload patentleri: en değerli (20+ yıl koruma)
- Linker patentleri: orta (kritik tercih)
- Conjugation teknoloji patentleri: yüksek (proses kontrolü)
- Kombinasyon ürün patenti: antikor + linker + payload birlikte

**Jenerik/biyobenzer cephesi** (ADC biosimilar henüz zor):
- ADC biyobenzeri için FDA/EMA çerçeve YOK (2025 itibarıyla)
- Biyobenzerlik kanıtı: analitik × 3 + klinik × 1 ancak payload-specific challenges
- İlk ADC biyobenzer onayı beklenmesi: 2027-2030

### FTO stratejisi (ADC için)

Yeni bir ADC geliştirmek isteyen firma:
1. **Antikor FTO** — hedef antijen (HER2, TROP2, CD22, BCMA vs) için antikor patenti
2. **Linker FTO** — cleavable (valine-citrulline) vs non-cleavable; her biri için patent haritası
3. **Payload FTO** — auristatin (MMAE, MMAF) vs maytansine (DM1, DM4) vs camptothecin (exatecan, SN-38)
4. **Conjugation FTO** — random vs site-specific; her yaklaşım için patent

**Pratik örnek**: Yeni bir anti-HER2 ADC geliştiren firma, Daiichi Sankyo (deruxtecan), Genentech (T-DM1), Seagen (GGFG linker) ile karşılaşır — royalty stack tipik %15-25.

### Invalidity fırsatları

Birçok ADC patenti **geniş Markush formülleriyle** yazılmıştır. Zayıf noktalar:
- Konjugasyon stokiyometrisi (2, 4, 8 payload/antikor) — dar spesifik örnekler yeterli midi?
- Linker peptid spesifitesi — bireysel aa sekansı vs genel sınıf
- Payload varyantları — binlerce benzer molekül + eski prior art

## 3. CAR-T (Chimeric Antigen Receptor T-cell therapy)

### Teknoloji anatomisi

CAR-T süreci:
1. Hastadan T-hücre alınır (leukapheresis)
2. Viral vektör (lentiviral veya retroviral) ile CAR konstrüktü inserte
3. Hücreler ex vivo genişletilir
4. Hastaya infüzyon
5. Lenfodeplesyon preparatifi (fludarabin + siklofosfamid)

### Patent kategorileri

- **CAR konstrüktü patenti** — hedef bağlayıcı (scFv) + transmembran + sinyal domainleri
- **Vektör patenti** — lentiviral/retroviral paketleme
- **Kültür proses patenti** — ex vivo genişletme koşulları
- **Formülasyon patenti** — infüzyon için donma/çözme protokolü
- **Dozaj rejim patenti** — spesifik hasta popülasyonu + preparatif rejim
- **Kombinasyon tedavi patenti** — CAR-T + immün checkpoint inhibitörü

### Kritik platform patentler

**Genel platform patentleri** (lisans gerekli):
- **St. Jude patent (Penn/Novartis)** — CD19 CAR-T genel konstrüktü (4-1BB + CD3ζ)
- **Juno/Kite (Gilead)** — CD28 + CD3ζ konstrüktü + 1BB kombinasyon
- **Cellectis (Fransa)** — TALEN gene editing for allogeneic CAR-T

### FTO haritası (yeni CAR-T geliştirmek)

Yeni bir CD19 CAR-T geliştirmek için zorunlu lisanslar:
- Penn/Novartis CAR patenti (tisa-cel için kullanılır)
- 4-1BB patent (Cellectis)
- Viral vektör patent (Fred Hutchinson, MPB)
- Manufacturing proses (Lonza veya Vineti)

**Toplam royalty stack: %20-35** (net gelir bazlı) — bu CAR-T marjlarının neden düşük olduğunu açıklar.

### Biyobenzer / jenerik yaklaşımı

CAR-T'nin biyobenzeri nedir? Henüz regülatör tanımı yok:
- Her parti kişiselleştirilmiş (hasta-spesifik T-hücre)
- Lot-to-lot aynılık yok
- "Biobetter" kavramı (iyileştirilmiş versiyon) CAR-T için daha uygulanabilir

**Allogeneic CAR-T** (Precision Biosciences, Allogene, Cellectis): donörden üretilen off-the-shelf CAR-T — jenerik benzeri yaklaşım. 2024-2026 itibarıyla Faz I/II.

## 4. mRNA-LNP (mRNA + Lipid Nanoparticle)

### Teknoloji anatomisi

- **mRNA sekans** (hedef antijen veya protein için kodlayan)
- **Modifiye nükleotitler** (N1-metilpsödoüridin — immünojenisite azaltma)
- **Lipid nanopartikül** (cationic + ionizable + PEG + cholesterol + helper)
- **Formülasyon buffer** (citrate / phosphate + pH + tonicity)

### Kritik CPC kodları

- **C07H 21/02** — nükleik asitler
- **C12N 15/11** — DNA/RNA
- **A61K 9/51** — nanopartiküller
- **A61K 48/00** — gen tedavisi bileşimleri

### Patent portföyü örüntüsü

**Moderna + BioNTech portföy örtüşmesi**:
- Her iki firma 2020-2024 arası 1000+ patent başvurusu
- ABD'de Moderna vs BioNTech/Pfizer patent davası devam etmektedir
- Patent zeminleri karmaşık — her iki firma farklı ülkelerde farklı patentlere dayanmaktadır

### Acuitas LNP patent duvarı

**Acuitas Therapeutics (Kanada)** — ionizable lipid (ALC-0315) patentleri lisans:
- Moderna: Acuitas patent → direkt lisans
- BioNTech/Pfizer: Acuitas → sublicense
- Yeni mRNA-LNP geliştirici: Acuitas ile lisans **zorunlu** (veya alternatif ionizable lipid geliştirme)

**Royalty stack tipik**: %12-20 (net gelir)

### Alnylam LNP patenti

**Alnylam Pharmaceuticals** — RNA therapeutics pioneer + LNP teknolojileri:
- DLin-MC3-DMA ionizable lipid (patensivran/Onpattro için kullanıldı)
- Patent süresi 2029-2032 aralığında
- Moderna + BioNTech Alnylam'dan sub-lisans aldı

### FTO stratejisi (yeni mRNA ürün)

1. **mRNA sekans FTO** — hedef protein için patentler (örn. SARS-CoV-2 spike için 50+ patent)
2. **Modifiye nükleotit patenti** — N1-metilpsödoüridin: Karikó & Weissman (Penn) patenti — Moderna + BioNTech'e lisanslandı
3. **LNP formülasyon FTO** — Acuitas + Alnylam zorunlu
4. **Manufacturing FTO** — IVT (in vitro transcription) + 5' capping + poli-A
5. **Formülasyon buffer** — spesifik pH + şeker (sucrose/trehalose) patentleri

### Invalidity fırsatları

mRNA-LNP patent peyzajı karmaşık ve çoğu genç (2020-2024 post-COVID aktivite):
- Obviousness argümanları güçlü (COVID aşısı aceleyle geliştirildi — novel olmayan prensipler)
- Inherent disclosure (Karikó 2005 makaleleri)
- Patent trolls saldırıları artıyor (Arbutus, Moderna davaları)

## 5. siRNA / ASO (antisense oligonucleotide)

### Teknoloji anatomisi

- **siRNA**: 21-23 nükleotit çift zincirli RNA, hedef mRNA'yı kesiyor (RISC complex)
- **ASO**: 15-25 nükleotit tek zincirli DNA/RNA, hedef mRNA'ya bağlanır (RNase H veya steric block)

### Önemli onaylı ürünler

- Patisiran (Onpattro, Alnylam) — hATTR amyloidosis (2018)
- Inclisiran (Leqvio, Novartis) — LDL-C düşürme (2021)
- Nusinersen (Spinraza, Biogen) — SMA (2016, ASO)
- Milasen — ilk kişiselleştirilmiş ASO

### Patent stratejisi

**Sekans patenti**: Her hedef mRNA için spesifik siRNA/ASO sekansı patenti. Ancak:
- Belirli 21mer için patent dar
- Aynı hedef için 100+ farklı sekans olabilir
- "Sekans genus" patentleri geniş ama invalidity'e açık

**Modifikasyon patentleri**:
- 2'-O-metil
- Fosforothioat linkage
- GalNAc conjugation (karaciğer hedefleme)

**Delivery**:
- LNP (siRNA için)
- GalNAc conjugation (Alnylam + Ionis)

### Platform patent duvarı

- **Alnylam** — siRNA therapeutics genel platform
- **Ionis** — ASO platform
- **Arrowhead** — TRiM platform

## 6. Gene Therapy (AAV, lentiviral)

### Teknoloji

**AAV** (Adeno-Associated Virus) — replikasyon-bozulmuş virüs; transgen için vektör:
- Kapsid serotipleri: AAV2, AAV5, AAV8, AAV9, AAVrh.10 (her biri farklı doku tropizmi)
- ITR (Inverted Terminal Repeats) — paketleme için zorunlu
- Promoter seçimi — doku-spesifik ekspresyon

**Lentiviral vektörler** — HIV-derived; stabil integrasyon → uzun süreli ekspresyon.

### Onaylı gene therapies

- Luxturna (Spark/Roche) — kalıtsal retinal distrofi, 2017
- Zolgensma (Novartis) — SMA, 2019, en pahalı ilaç ($2.1M/dose)
- Casgevy + Lyfgenia (Vertex + bluebird) — orak hücreli anemi, 2023
- Elevidys (Sarepta) — Duchenne muscular dystrophy, 2023

### Patent portföyü

**Kapsid serotipleri** — REGENXBIO, Voyager, Stride Bio portföyleri değerli
**Manufacturing (plasmid + upstream + downstream)** — Lonza, Catalent platform patentleri
**Kişiselleştirilmiş gene therapy manufacturing** — Orchard, bluebird proses patentleri

### FTO (yeni AAV gene therapy)

1. Hedef gen (transgen) için FTO
2. Kapsid serotipi FTO — istenen dokuda ekspresyon için
3. Promoter FTO — doku-spesifik veya ubiquitous
4. Manufacturing FTO — HEK293 veya Sf9 üretim sistemi

**Pratik örnek**: Yeni bir AAV9 gene therapy için:
- REGENXBIO AAV9 platform (NAV Technology): sublicense $$
- Spark/Roche dozaj rejim patentleri (varsa)
- Novartis kapsid modifikasyon patentleri

### Çok yüksek CapEx — finansal etki

AAV gene therapy üretim tesisi: $200M-500M CapEx. Patent süresi tek bir hedef için 20 yıl = terminal değeri yüksek ama ROI analizi hassas.

## 7. Xenotransplantation ve cell-based therapies

### Tanım

**Xenotransplantation**: Domuz veya diğer hayvan organlarının insana transplantasyonu. 2022-2024'te ilk başarılı genetik modifikasyonlu domuz kalbi + böbrek transplantları.

### Gen modifikasyonlu domuz

**10+ genetik modifikasyon** (gene knockout + knockin):
- α-1,3-galactosyltransferase knockout (hyperakut rejeksiyon)
- β4GalNT2, CMAH knockouts
- HLA class I knockout
- CD47, CD55, CD59 knockin (komplement düzenleyici)

### Patent stratejisi

**Revivicor** (UTHC grubu) — ilk patentler, şimdi United Therapeutics
**eGenesis** — yeni patentler, 10-genelik modifikasyon platformu

### Regülatör — henüz yok

- FDA + EMA xenotransplantation için özel rejim geliştiriyor
- Türkiye'de bunun için hiç çerçeve yok
- ilk onay 2030'lu yılların başı beklenmekte

### Patent süresi dikkat

Xenotransplantation patentleri 2015-2023 arası çoğunluk. Onay 2030+'sa, patent süresinin çoğu harcanmış olacak → uzatma mekanizmaları (continuations, new indications) kritik.

## 8. Yapay zekâ + dijital terapötikler

### Kategoriler

**AI diagnostics / SaMD**:
- Software as a Medical Device (FDA, EMA MDR sınıf IIb)
- Algorithm patents (CPC G16H 50/20)
- Training data rights
- Clinical validation

**Digital therapeutics (DTx)**:
- Uygulama tabanlı tedavi (Pear Therapeutics, Akili)
- Veri toplama + yapay zeka + geri besleme
- Hem yazılım hem davranışsal müdahale

### Patent stratejisi (DTx için zor)

- Yazılım patentleri dar yorumlanır (Alice Corp v. CLS Bank, 2014)
- Algoritma patentlenemez — spesifik uygulama patentlenebilir
- Veri seti patentlenemez — veri işleme yöntemi patentlenebilir
- "Abstract idea" istisnası (ABD)

### Alternatif IP koruması

- **Trade secret** — algoritma gizlenir
- **Copyright** — yazılım kodu
- **Trademark** — marka ve kullanıcı deneyimi
- **Veri tekeli** — birebir eşsiz eğitim veri seti

### Türkiye AI sağlık regülatörü

- TİTCK AI/ML tabanlı cihazlar için kılavuz hazırlıyor (2024-2026)
- AB AI Act (Regulation (EU) 2024/1689) Türkiye'ye yansıma bekleniyor
- KVKK + sağlık verisi entegrasyon karmaşık

## 9. Modalite-spesifik regülatör kesişim

| Modalite | FDA yolu | EMA yolu | TİTCK yolu |
|---|---|---|---|
| Small molecule | NDA (505(b)(1)) | MAA | Tam başvuru |
| Biyolojik | BLA | MAA | Tam başvuru |
| ADC | BLA | MAA | Tam başvuru |
| CAR-T | BLA + ATMP (AB) | MAA-ATMP | İleri Tedavi Tıbbi Ürünleri Yönetmeliği |
| Gene therapy | BLA + RMAT | MAA-ATMP | İleri Tedavi Tıbbi Ürünleri Yönetmeliği |
| mRNA | BLA (COVID için EUA) | MAA | Aşı için özel fast-track |
| siRNA/ASO | NDA veya BLA | MAA | Tam başvuru |
| Digital (SaMD) | 510(k) veya De Novo | CE IIa/IIb (MDR) | Tıbbi Cihaz Yönetmeliği |

### Fast-track mekanizmalar

- **FDA Breakthrough Designation** — hızlı inceleme
- **EMA PRIME** — öncelik ilaç inceleme
- **TİTCK koşullu ruhsat** — sınırlı kanıt ile acil ihtiyaç

### ATMP (İleri Tedavi Tıbbi Ürünleri)

AB'de CAR-T, gene therapy, tissue-engineered için özel kategori:
- Hastane muafiyeti (hospital exemption) — 1 merkez, akademik kullanım
- Non-commercial ATMP — GMP gerekliliği hafif
- Ticari ATMP — tam MAA

Türkiye'de İleri Tedavi Tıbbi Ürünleri Yönetmeliği (2023) AB ATMP ile büyük oranda uyumlu.

## 10. Modalite-spesifik değerleme çarpanları

### Peak sales büyüklükleri (tipik)

| Modalite | Tipik peak sales |
|---|---|
| Küçük molekül onkoloji | $500M - $3B |
| mAb onkoloji | $1B - $10B |
| ADC | $500M - $5B |
| CAR-T | $300M - $2B (patient-bazlı düşük hacim) |
| mRNA vaccine | COVID dönemi $20-30B (normalize $1-5B) |
| Gene therapy (rare disease) | $200M - $1B (one-shot) |
| Digital therapeutic | $50M - $500M |

### Royalty stack (net gelir bazlı)

| Modalite | Tipik royalty stack |
|---|---|
| Küçük molekül | %5-12 |
| mAb | %8-15 |
| ADC | %15-25 (3 patent aile) |
| CAR-T | %20-35 (çok platform lisans) |
| mRNA-LNP | %15-25 (Acuitas + Alnylam stack) |
| Gene therapy | %15-30 (vektör + manufacturing) |
| Digital | %5-15 (veri + algoritma) |

### NPV çarpanları

Standart DCF üzerine modalite düzeltmesi:

| Modalite | Risk adjustment factor |
|---|---|
| Küçük molekül | 1.0x (baseline) |
| mAb | 1.2x (daha uzun LOE, daha az erozyon) |
| ADC | 1.1x (karmaşık ama düşük biosimilar tehdidi) |
| CAR-T | 0.7x (manufacturing risk + limited scale) |
| mRNA | 0.8-1.3x (dalgalanma yüksek — COVID etkisi) |
| Gene therapy | 0.6-0.9x (one-shot revenue ani) |
| Digital | 0.5-0.8x (reimbursement belirsiz) |

---

*Yeni modaliteler, klasik farmasötik IP kurallarını zorlar ve her birisi ayrı bir disiplin haline gelmiştir. Bu protokol giriş seviyesi haritayı sunar; spesifik modalite için uzman patent vekili + regülatör danışmanı ile koordinasyon zorunludur. Modalite-spesifik referanslar ve güncel patent dava hakkında EvaluatePharma, Endpoints, FiercePharma günlük takip edilmesi önerilir.*
