# references/tibbi-cihaz-uts.md — Tıbbi Cihaz Yönetmeliği, ÜTS, CE ve ISO 13485 Entegrasyonu

> Farmasötik ve tıbbi cihaz hukuku ayrı rejimlerdir, ancak modern **kombinasyon ürünler** (prefilled syringe, inhaler, auto-injector, transdermal sistem, akıllı pompa) bu iki rejimi iç içe geçirir. Bu protokol, patent + ruhsat + cihaz onay zincirini entegre yönetmek için kurulmuştur.

## İlişkili Protokoller

- **`cpc-ipc-kodlari.md`** — A61M (cihaz), A61B (teşhis/cerrahi), G16H (sağlık informatiği), A61F (implantlar) CPC taksonomisi
- **`ruhsat-veri-imtiyazi.md`** — Kombinasyon ürünlerde birincil amaç testi — ilaç rejimi ile cihaz rejimi ayrımı
- **`ictihat-emsal.md`** — Cihaz patent tecavüzü, kombinasyon ürün davaları ve FSHHM pratiği
- **`smk-6769-ilac.md`** — SMK'nın cihaz patentlerine uygulanması: m.82 (patent edilebilirlik), m.92 (koruma kapsamı), m.141 (tecavüz)

## İçindekiler

1. Tıbbi Cihaz Yönetmeliği — genel çerçeve
2. Cihaz sınıflandırması (I / IIa / IIb / III)
3. CE işaretleme süreci
4. ÜTS — Ürün Takip Sistemi
5. ISO 13485 — Kalite Yönetim Sistemi
6. Kombinasyon ürünler (ilaç + cihaz)
7. TÜRKPATENT 2024 Nice güncellemesi
8. Cihaz patenti stratejik boyutları
9. Yapay zekâ teşhis cihazları
10. Tipik ihtilaf senaryoları

---

## 1. Tıbbi Cihaz Yönetmeliği — genel çerçeve

### Temel dokümanlar

**Ana yönetmelik**: Tıbbi Cihaz Yönetmeliği
- Resmi Gazete 02.06.2021, 31499
- AB'nin MDR (Medical Device Regulation (EU) 2017/745) ile uyumlu
- 2021 öncesi yürürlükteki TCY (2011) tamamen yenilendi

**İn Vitro Tanı Amaçlı Tıbbi Cihaz Yönetmeliği**: AB'nin IVDR (Regulation (EU) 2017/746) uyumlu.

**Kapsam**:
- Cerrahi aletler ve protezler
- İmplantlar
- Diagnostik cihazlar
- Kombinasyon ürünler (cihaz-ilaç-biyolojik)
- Yazılım ve yapay zeka uygulamaları (SaMD — Software as a Medical Device)
- Akıllı giyilebilir cihazlar

**Kapsam dışı**:
- Salt kozmetik ürünler
- Gıda takviyeleri
- Kişisel koruyucu donanım (biyosidal ve koruyucu ekipman ayrı mevzuatta)

### Yetkili otorite

**TİTCK — Tıbbi Cihaz Dairesi Başkanlığı**:
- Ulusal onay ve kayıt
- ÜTS sistemi
- Piyasa gözetim ve denetim
- Uygunsuzluk ve geri çağırma

**Onaylanmış Kuruluşlar** (Notified Bodies):
- TÜRKAK akreditasyonlu kuruluşlar
- Türkiye'de: TSE, TÜRKLOYDU, URS, SZUTEST ve diğerleri
- AB onaylanmış kuruluşları (TÜV SÜD, BSI, DEKRA, DQS vb.) Türkiye'de de geçerli CE ile

---

## 2. Cihaz sınıflandırması (I / IIa / IIb / III)

### Sınıf I — Düşük risk

- Kısa süreli temas, invaziv olmayan
- Örnekler: muayene lastik eldivenleri, bandajlar, pamuk, stetoskop, reflex çekici

**Onay süreci**: Üretici kendi kendine uygunluk beyanı (self-certification) yeterlidir. Onaylanmış kuruluş denetimi gerekmez (Sınıf Is ve Im hariç — steril veya ölçme fonksiyonlu cihazlar).

**Sınıf Is** (sterile): Sterilite için onaylanmış kuruluş gerekir.
**Sınıf Im** (measuring): Ölçüm fonksiyonunun doğruluğu için onaylanmış kuruluş gerekir.
**Sınıf Ir** (reusable surgical instruments): Yeniden kullanım için denetim gerekir.

### Sınıf IIa — Orta-düşük risk

- Kısa/orta süreli invaziv, düşük risk tıbbi yazılım
- Örnekler: İşitme cihazları, dental implantasyon aksesuarları, ultrason tanı sistemleri, kalp atış hızı monitörleri

**Onay süreci**: Onaylanmış kuruluş denetimi + CE işaret.

### Sınıf IIb — Orta-yüksek risk

- Uzun süreli invaziv, enerji uygulayan cihazlar, kan ile temas
- Örnekler: İnfüzyon pompaları, solunum cihazları, anestezi cihazları, radyolojik cihazlar, bazı yazılım uygulamaları

**Onay süreci**: Onaylanmış kuruluş denetimi + klinik veri + CE işaret.

### Sınıf III — Yüksek risk

- Kalp, merkezi sinir sistemi, merkezi dolaşım ile temas
- İmplant edilebilir cihazlar (cerrahi önce)
- Örnekler: Kalp kapakçıkları, koroner stentler, pacemaker'lar, kemik/eklem protezleri, CAR-T ile ilişkili cihazlar, beyin stimülatörleri

**Onay süreci**: Onaylanmış kuruluş tam denetim + tam teknik dosya + klinik çalışma + CE işaret + tasarım incelemesi.

### MDR sınıflandırma kuralları

MDR'ın 22 sınıflandırma kuralı (Annex VIII):
- Kural 1-4: İnvaziv olmayan cihazlar
- Kural 5-8: İnvaziv cihazlar
- Kural 9-13: Aktif cihazlar
- Kural 14-22: Özel kurallar (nanomalzemeler, implantlar, kombinasyon)

**Pratik**: Yanlış sınıflandırma pazar erişimini geciktirir; başlangıçta doğru sınıf tespit edilmelidir.

---

## 3. CE işaretleme süreci

### Süreç adımları

1. **Cihaz sınıfının belirlenmesi** (MDR Annex VIII)
2. **Temel gereklilikler analizi** (MDR Annex I) — performans, güvenlik
3. **Uygunluk değerlendirme prosedürünün seçilmesi** (MDR Annex IX-XI)
4. **Teknik dosya hazırlanması** (MDR Annex II)
5. **Kalite yönetim sistemi (ISO 13485) uygulaması**
6. **Klinik değerlendirme / klinik çalışma** (MDR Annex XIV)
7. **Risk yönetimi (ISO 14971)**
8. **Onaylanmış kuruluş denetimi** (Sınıf IIa, IIb, III için)
9. **Uygunluk beyannamesi (DoC)**
10. **CE işaretinin yapıştırılması**
11. **EUDAMED veri tabanına kayıt** (AB)
12. **Türkiye'de ÜTS kayıt**
13. **Piyasaya arz**

### Klinik değerlendirme

**Sınıf III** ve çoğu **Sınıf IIb** cihazlar için klinik çalışma gerekir:
- Pre-market klinik araştırma (IDE benzeri süreç)
- TİTCK izni + etik kurul onayı (ICH GCP uyumlu)
- ISO 14155 uyumlu çalışma

**Klinik değerlendirme raporu (CER)**:
- Literatür analizi
- Eşdeğer cihaz kıyaslaması (varsa)
- Post-market klinik takip planı (PMCF — Post-Market Clinical Follow-up)

### Piyasa sonrası gözetim (PMS)

MDR ile zorunlu hale getirildi:
- **PMSR**: Post-Market Surveillance Report (Sınıf I için yıllık)
- **PSUR**: Periodic Safety Update Report (Sınıf IIa için 2 yılda bir, IIb+III için yıllık)
- **Vijilans raporlama**: ciddi olaylar, trend raporları, FSCA (Field Safety Corrective Action)

---

## 4. ÜTS — Ürün Takip Sistemi

### Yasal dayanak

- Tıbbi Cihaz Yönetmeliği + TİTCK Kılavuzları
- AB EUDAMED ile uyumlu (ancak ayrı sistem)

### İşleyiş

**ÜTS** (urunturkiye.gov.tr), Türkiye'de tıbbi cihaz, kozmetik, biyosidal ürün, beşeri tıbbi ürünlerin dijital takibini sağlar.

**Tüm üreticilerin / ithalatçıların yapması gerekenler**:

1. Firma kaydı (TİTCK sistemine)
2. Ürün kaydı (her model için)
3. UDI kodu atama (Unique Device Identifier — Amerika FDA ve AB MDR uyumlu)
4. Barkodlama
5. Üretim / ithalat partileri bildirimi
6. Ecza deposu dağıtımı kaydı
7. Sağlık kurumu teslim kaydı
8. Hastaya teslim kaydı (bazı kategorilerde)

### UDI sistemi

**Kapsam**: Tüm tıbbi cihazlar, kombinasyon ürünler (ilaç kısmı dahil değil — o ayrı kimlikle).

**Elementler**:
- DI (Device Identifier) — sabit
- PI (Production Identifier) — batch, expiry, serial

**Format**: GS1 DataMatrix barkod, RFID.

### ÜTS ile patent hakkı etkileşimi

**Tecavüz ispatı**: ÜTS kayıtları — kim, ne zaman, hangi miktarda ithalat / üretim / satış yaptı — patent ihlali davasında delil niteliğindedir.

**Gümrük itirazı**: Patent sahibi gümrükte tecavüz eden ürünün yakalanmasını talep edebilir (4458 sayılı Gümrük Kanunu + SMK m. 159 ile bağlantılı). ÜTS kaydı olmayan veya sahte UDI içeren cihazlar için gümrük aksiyonu daha güçlüdür.

---

## 5. ISO 13485 — Kalite Yönetim Sistemi

### Zorunluluk

ISO 13485:2016 — Tıbbi cihaz üreticileri için kalite yönetim sistemi standardı.

**Kapsam**:
- Tüm CE işareti almak isteyen üreticiler
- Onaylanmış kuruluş denetiminin temeli
- MDR Annex IX uygunluk değerlendirme prosedürünün temel bileşeni

### Temel gereklilikler

1. **Kalite yönetim sistemi dokümantasyonu** — kalite el kitabı, prosedürler
2. **Yönetim sorumluluğu** — üst yönetim sorumluluğu, kalite politikası
3. **Kaynak yönetimi** — insan kaynakları, altyapı, iş ortamı
4. **Ürün gerçekleştirme** — tasarım, satın alma, üretim, muayene
5. **Ölçme, analiz ve iyileştirme** — denetim, iç tetkik, sürekli iyileştirme

### ISO 13485 ile ISO 9001 farkı

ISO 13485 **tıbbi cihaz spesifiktir**; ISO 9001 genel kalite yönetim standardıdır. Tıbbi cihaz üreticileri için ISO 9001 yeterli değildir; ISO 13485 zorunludur.

---

## 6. Kombinasyon ürünler (ilaç + cihaz)

### Tanım

İlaç + cihaz kombinasyonu; iki bileşenin **tek bir ambalajda / tek bir kullanımda** birleştiği ürünler.

### Türleri

**Tip A — Entegre kombinasyon**: İlaç ve cihaz ayrılamaz şekilde birleşmiş.
- Prefilled syringe (insülin kalemleri, trastuzumab enjeksiyon pompası)
- Otomatik enjektörler (EpiPen benzerleri)
- İlaç salan stentler (drug-eluting stents)
- İlaç salan implantlar (kontraseptif implantlar)

**Tip B — Kit kombinasyon**: İlaç ve cihaz ayrı ancak paket içinde birlikte.
- İnhalerler (salbutamol inhalör)
- Transdermal yamalar (fentanyl TTS)
- Radyasyon kiti (radyoiyot kitleri)

### Regülatör yaklaşımı

**Ana unsur tespiti** — Ürünün **birincil amacı ilaç mı cihaz mı** sorusuna göre ana rejim belirlenir:

**Birincil ilaç** → Ruhsatlandırma Yönetmeliği (ilaç rejimi), cihaz kısmı tıbbi cihaz olarak da ayrıca değerlendirilir.

**Birincil cihaz** → Tıbbi Cihaz Yönetmeliği (cihaz rejimi), ilaç kısmı için farmasötik veri sunulur.

**AB'de**: MDR Article 1(9) — entegre kombinasyon için ana unsur testi; "devices incorporating a medicinal product" için özel prosedür.

### Pratik örnekler

- **Prefilled syringe — biyolojik ilaç**: Birincil amaç ilaç → Ruhsatlandırma Yönetmeliği. Syringe (cihaz) için ayrıca ISO standartları ve patent korunabilir.

- **İlaç salan stent (everolimus eluting)**: Birincil amaç mekanik (damar açıklığı) → Tıbbi Cihaz (Sınıf III). İlaç kısmı için ruhsat dosyasında ek bölüm.

- **Akıllı insülin pompası**: Birincil amaç cihaz (pompa) → Sınıf IIb. İnsülin ayrıca ruhsatlı.

### Patent stratejisi

Orijinatör firma kombinasyon ürünü için **çoklu patent duvarı** inşa edebilir:

1. **İlaç patenti** — aktif madde, formülasyon
2. **Cihaz patenti** — syringe/pump/inhaler mekanizması (A61M)
3. **Kombinasyon patenti** — ilaç + cihaz birlikte kullanım istemi
4. **Yazılım patenti** (akıllı cihazlar için) — kontrol algoritmaları
5. **Tıbbi kullanım patenti** — spesifik hasta popülasyonunda kullanım

Bu çoklu korunma, ilaç patent süresinin sonrasında dahi ürünün (cihaz ile birlikte) pazar tekelinin devamını sağlar — jenerik rakip ya cihaz için ayrı lisans alır ya da ilacı ayrı bir cihazla pazarlar.

---

## 7. TÜRKPATENT 2024 Nice güncellemesi

### Genel bilgi

2024 yılında TÜRKPATENT, marka başvurularında kullanılan Nice sınıflandırma listesini güncelledi. Bu, **marka** sınıflandırmasıdır (patent değil); ancak sağlık ürünleri için entegre fikri mülkiyet portföyü içinde önemlidir.

### Kritik yeni alt sınıflar

**09. sınıf — yeni alt sınıf**: *Yapay zekalı insansı robotlar, güvenlik robotları ve laboratuvar robotları*.

- Cerrahi robotlar (da Vinci benzeri)
- Yapay zekalı teşhis robotları
- Otomatik ilaç hazırlama / dispens etme robotları
- Laboratuvar otomasyon sistemleri

**Pratik**: Yapay zekalı bir teşhis cihazı üreticisi; cihaz patenti (A61B 34/00, G16H 50/20 CPC) + marka (09. sınıf) + ÜTS kaydı entegre yaklaşır.

**39. sınıf — eklenen hizmetler**: *Sağlık turizmi ulaşım ve konaklama ayarlanması, vize işlemleri düzenlenmesi*.

- Sağlık turizmi aracılık şirketleri
- Ulaşım + konaklama paketleri
- Uluslararası hasta yönetimi

**44. sınıf — ayrıştırılan hizmetler**: *Diş hekimliği hizmetleri* ve *psikologlara ait hizmetler* 44/01 alt sınıfına spesifik olarak eklendi.

### Önemi

Bir ilaç şirketi hem patent (CPC) hem marka (Nice) tescili alır:
- Patent → ürünün teknik korunması
- Marka → ürünün ticari isim / logo korunması

**Örnek**: Yapay zekalı kanser teşhis yazılımı üreten bir şirket:
- Patent: G16H 50/20 + A61B 34/00
- Marka: 09. sınıf yeni alt sınıf (yapay zekalı robotlar)
- ÜTS: Tıbbi cihaz sınıfında kayıt
- CE: Sınıf IIa / IIb (risk bazlı)

---

## 8. Cihaz patenti stratejik boyutları

### İstem tipleri

Tıbbi cihaz patentlerinde:

**Yapısal istem**:
> "Bir enjektör cihazı, aşağıdakileri içerir:
> - bir hazne,
> - bir iğne,
> - bir piston,
> - bir güvenlik kilidi..."

**Fonksiyonel istem**:
> "İlacın kontrollü salınımını sağlayan bir mekanizma..."

**Kullanım istemi**:
> "A ilacının B hastalığında kullanılması için C cihazı..."

**Yöntem istemi**:
> "Aşağıdaki adımları içeren bir ilaç uygulama yöntemi..." (SMK m. 82/2 kapsamı — tedavi yöntemi ise patent edilmez; üretim yöntemi ise edilir)

### İhlal testi

Cihaz patentinde ihlal testi:
1. **Literal ihlal** — cihaz istemdeki tüm elementleri içeriyor mu?
2. **Doktrinel eşdeğer** — farklı bir element kullanılmış ancak aynı işlevi görüyor mu?
3. **Değişken elementler** — Markush benzeri genişletmeler ilaçta olduğu gibi cihazda da geçerlidir

### Tipik dava senaryoları

**Senaryo 1**: Jenerik ilaç firması, orijinal ilaca atıfla Bolar kapsamında ruhsat alıyor; ancak orijinal ilaç önceden dolu bir otomatik enjektör (Sınıf IIb cihaz) ile geliyor. Jenerik firma bu enjektörün patentini çürütememişse, kendi ürününü **ayrı bir enjektörle** pazarlamak zorunda — ki bu farklı cihaz için CE onay süreci 6-18 ay ek süre gerektirir.

**Senaryo 2**: Tıbbi cihaz üreticisi, ISO 13485 uyumluluk denetiminde tasarımda bir patent ihlali fark ediyor; tasarım değişikliği için etki analizi ve onaylanmış kuruluş onayı gerekir.

**Senaryo 3**: Yapay zeka teşhis yazılımı güncellemesi — yazılım güncellemesi patent ihlali yaratabilir (yeni bir algoritma başka bir patentte korunuyorsa). MDR altında yazılım güncellemeleri **significant change** olarak değerlendiriliyorsa yeniden CE onay gerekir.

---

## 9. Yapay zekâ teşhis cihazları

### MDR kapsamında SaMD

**Software as a Medical Device (SaMD)** MDR altında tam cihaz statüsündedir:
- Sınıflandırma: IMDRF (International Medical Device Regulators Forum) çerçevesi + MDR Kural 11
- Risk bazlı sınıflama: I, IIa, IIb, III
- Klinik değerlendirme gerekli
- Yazılım yaşam döngüsü IEC 62304 uyumlu olmalı
- Siber güvenlik IEC 81001-5-1 uyumlu
- Kullanılabilirlik IEC 62366 uyumlu

### Yapay zeka / makine öğrenmesi özel

**Adaptive AI / Continuous Learning** — yazılım "kullanım sırasında kendi kendine öğrenen" AI modelleri için özel düzenleme:
- FDA'nın Predetermined Change Control Plan (PCCP) yaklaşımı
- AB AI Act (Regulation (EU) 2024/1689) — yüksek riskli AI sistemleri için ek gereklilikler
- Türkiye'de TİTCK kılavuzları geliştirilmekte

### Patent stratejisi

**CPC kodları**:
- G16H 50/20 — makine öğrenmesi tabanlı teşhis
- G16H 30/00 — teşhis için görüntü analizi
- G06N 3/00 — nöral ağlar, derin öğrenme
- A61B 5/00 — teşhis ölçüm (yapay zeka entegre)

**Patent ile açık kaynak gerilimi**: AI modelleri bazen açık kaynaklı (MIT, GPL) lisanslarla yayımlanır. Bu durumda patent koruması sınırlı olabilir — spesifik kullanım, veri hazırlama, inference mimarisi patent edilebilir; model mimarisi açık kaynak ise değil.

**Veri koruma — KVKK**: Eğitim verisi olarak hasta verisi kullanıldıysa KVKK uyumlu anonimleştirme/rıza gerekir; ihlal iptal gerekçesidir.

---

## 10. Tipik ihtilaf senaryoları

### İhtilaf 1 — İnhaler formülasyon davası

**Durum**: Orijinatör firmanın salmeterol/flutikazon inhaler patent süresi biterken, firma yeni bir inhaler cihaz patenti aldı (aerosol karıştırma mekanizması). Jenerik firma salmeterol/flutikazon jenerik ürünü çıkardı ama kendi inhalerinde mekaniksel olarak farklı bir sistem kullandı.

**Soru**: Jenerik firmanın inhaleri orijinatörün yeni cihaz patentini ihlal ediyor mu?

**Analiz**:
1. Orijinatörün cihaz patentinin istemlerini oku (bağımsız + bağımlı)
2. Jenerik cihazda patent istemlerinin tüm yapısal elementleri var mı?
3. Yok ise doktrinel eşdeğer analizi
4. Jenerik cihazın başka bir CE dosyası ile onaylandığını belirle
5. İhlal yok ise FTO temizliği teyit edilir

### İhtilaf 2 — Yapay zeka teşhis yazılımı

**Durum**: Şirket A, meme kanseri mamografi görüntüsünden teşhis eden AI yazılımı için MDR altında Sınıf IIb ruhsat aldı. Şirket B'nin patenti "2D-to-3D conversion ile lezyon tespit algoritması" için var.

**Soru**: Şirket A'nın algoritması B'nin patentini ihlal ediyor mu?

**Analiz**:
1. B patentinin istem metni — 2D-to-3D conversion spesifik mi, algoritma mı, sinirsel ağ mimarisi mi?
2. A'nın yazılım mimarisi ters mühendislik ile çıkarılabilir mi (klinik değerlendirme dosyasından)?
3. İstem elementleri eşleşiyor mu?
4. AI modeli açık kaynaktan mı türetildi, özgün mü?
5. Eğitim verisi patent ihlali ile alakalı değil, model kullanımı alakalı

### İhtilaf 3 — Kombinasyon ürün (biyolojik + syringe)

**Durum**: Orijinatör biyolojik ilaç (mAb) + prefilled syringe kombinasyonu. Biyobenzer firma mAb biyobenzeri ruhsatı aldı. Ancak orijinatörün prefilled syringe için özel bir "tek tık otomatik" mekanizma patenti var.

**Soru**: Biyobenzer firma aynı syringe ile pazarlanabilir mi?

**Analiz**:
1. Syringe patenti ne kadar geniş? (tek tık mekanizması + özel iğne koruması + ölçüm göstergesi kombinasyonu)
2. Biyobenzer firma alternatif syringe kullanabilir mi?
3. Alternatif syringe kendi CE / ÜTS sürecinden geçmeli — 6-12 ay ek süre
4. Stratejik seçim: ya biyobenzer girişi gecikir (syringe için lisans müzakeresi) ya da farklı bir cihaz ile daha az rekabetçi ürün

### İhtilaf 4 — ÜTS kayıt dışı ithalat

**Durum**: Yetkili distribütör, orijinatörün bir tıbbi cihazını Türkiye'ye ithal etti ancak ÜTS'ye kayıt etmedi. Ürün hastanelerde kullanıldı.

**Soru**: Bu ÜTS ihlali mi, patent ihlali mi?

**Analiz**:
1. ÜTS ihlali: idari (TİTCK tarafından ceza, ürün çekme, ihracat izni iptal)
2. Patent ihlali (varsa): hukuki (FSHHM'de dava, tazminat)
3. İkisi **birbirinden bağımsız** rejimler; biri uygulansa diğeri etkilenmez
4. Orijinatör hem ÜTS şikâyeti hem patent davası açabilir (varsa)

---

*Tıbbi cihaz mevzuatı AB MDR uyum süreçleriyle birlikte hızla değişiyor. Yıllık güncelleme kontrolü önerilir. AB MDR'in tam uygulanması 2027 geçiş dönemi sonuna kadar aşamalı.*
