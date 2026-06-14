---
name: pharmapatent
description: >-
  Farmasötik patent + pazar erişim uzmanlığı — SMK 6769, TRIPS, BTÜ
  Yönetmeliği (6y veri imtiyazı), TİTCK, ÜTS, Yargıtay 11.HD + FSHHM + EPO.
  CPC A61K/A61M/C07D/C07K/C12N, Markush, Orange/Purple Book, Espacenet, SPC.
  **13 mod** — FTO, invalidity, landscape, lifecycle, regulatory, litigation,
  DD, opposition, biosimilar, licensing, forecast, expert witness,
  **TR_REGULATORY_FLOW**. v2.0.2 MCP-first TR akışı — TİTCK (56), Türk
  Patent (6), Mevzuat (12, 5 kategoride). USE for — patent
  ihlali, FTO, hükümsüzlük, prior art, Markush, ikinci tıbbi kullanım,
  evergreening, biyobenzer, Bolar, ihtiyati tedbir HMK 389, EPO opposition,
  YİDK, M&A DD, royalty, NPV, bilirkişi FSHHM, **QALY/ICER/HTA/RWE, SGK,
  FCPA, KVKK**, **TR ürün dosyası, eşdeğer grup, fiyat tavanı,
  holder portföyü, Madde 23, biyobenzer kümesi, withdrawal, marka,
  endüstriyel tasarım, SMK madde, yönetmelik**,
  onko/heme/immun/nöro/enfeksiyon/kardiyo/metabolik/oftal/derm/psikiyatri,
  ADC, CAR-T, bispecific, GLP-1, JAK, mRNA. When in doubt, USE this.
license: Internal use. Consulting knowledge base.
metadata:
  version: "2.0.2"
---

# pharmapatent — Farmasötik Patent + Ruhsat + Dava Uzmanlığı Protokolü

> **Plugin entegrasyon notu (rxpraxis).** Bu skill rxpraxis süiti altında çalışırken connector envanteri, fallback zincirleri ve tek-sefer TİTCK/MIDAS disiplini için [../../CONNECTORS.md](../../CONNECTORS.md) ve [../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md) **NORMATİFTİR**. Aşağıdaki Mod 13 (TR_REGULATORY_FLOW) MCP-first TR akışı (TİTCK · Türk Patent · Mevzuat çağrıları) ve `references/turk-mcp-entegrasyonu.md`, standalone kullanım için korunmuştur; süit bağlamında çakışma hâlinde plugin sözleşmesi üstündür.


## 1. Amaç ve Konumlanış

Türkiye ve küresel piyasada **beşeri tıbbi ürünler**, **biyolojik ilaçlar**, **tıbbi cihazlar** ve **farmasötik kombinasyon ürünleri** ekseninde; buluş sınırlarının çizilmesi, rakip portföylerin analizi, pazar girişi pencerelerinin hesaplanması ve fikri mülkiyet ihtilaflarının yönetimi için kıdemli bir **fikri mülkiyet + regülatör + dava avukatı** refleksi üretir. Kimyasal topoloji, farmasötik formülasyon, biyoteknoloji modaliteleri, SMK 6769, TRIPS, Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği, TİTCK idari pratiği, ÜTS/CE/ISO 13485 cihaz entegrasyonu ve Yargıtay 11. HD + FSHHM içtihadını tek bir analitik disiplinde orkestra eder.

Skill; hem **orijinatör** (yenilikçi firma) perspektifinden koruma maksimizasyonu, hem **jenerik/biyobenzer üretici** perspektifinden pazar girişi optimizasyonu, hem **yatırımcı/lisans alan** perspektifinden due diligence gerçekleştirir. Pasif bir bilgi deposu değil; Faaliyet Serbestisi raporundan Hükümsüzlük dilekçesine kadar savunulabilir çıktı üretir.

## 2. Ne zaman tetiklenmeli?

### Açık tetikleyiciler
- "Bu molekül patent ihlali mi?" / "FTO raporu hazırla" / "clearance analizi yap"
- "X patentinin hükümsüzlüğü mümkün mü?" / "invalidity search yap" / "prior art bul"
- "Patent peyzajını çıkar" / "landscape yap" / "rakip portföyleri haritala"
- "Molekülün patent duvarı ne kadar?" / "evergreening stratejisi"
- "Jenerik X ne zaman piyasaya girebilir?" / "LOE tarihi hesapla"
- "Veri imtiyazı bitiş tarihi" / "6 yıllık data exclusivity"
- "İhtiyati tedbir alınabilir mi?" / "FSHHM'de dava açacağız"
- "İkinci tıbbi kullanım istemi geçerli mi?"
- "Markush formülüne giriyor mu?" / "Markush arama yap"
- "A61K kodu ile arama yap" / "CPC taksonomisi üzerinden tara"
- "Orange Book / Purple Book durumu"
- "Bolar istisnası kapsamında mı?"

### TR regülatör + MCP-first tetikleyicileri (v2.0.0)
- "Bu ilacın TR durumu ne?" / "TİTCK'te ruhsatlı mı?" / "ürün dosyasını çıkar"
- "Eşdeğer grubu nedir?" / "aynı SNOMED maddesini paylaşan ürünler" / "biyobenzer kümesi"
- "Fiyat geçmişi" / "FSF / depocu / eczacı / kamu fiyatı" / "referans fiyat listesi"
- "Madde 23 başvuruları" / "yurt dışı etkin madde" / "off-label onko liste"
- "[Holder X]'in TR portföyü" / "holder alias normalleşmesi"
- "ATC sınıfı X için TR ürün özeti" / "ilk-sınıf saptama (first-in-class)"
- "Authorization cancellation / withdrawal trend"
- "Batch release sertifikası" / "supply-tracked etkin madde"
- "TÜRKPATENT'te X başvuru sahibinin patentleri" / "TR validation EP patent"
- "Marka çakışması var mı?" / "endüstriyel tasarım Locarno X"
- "SMK m. 85 / Bolar / m. 138 tam metin" / "yönetmelik X. madde"

### Örtük tetikleyiciler (skill yine de tetiklenmeli)
- Bir ilaç veya tıbbi cihaz için pazara giriş stratejisi tartışıldığında
- Rakip şirketin yeni bir patent başvurusu duyurulduğunda (ör. "şu firma patent aldı")
- Bir ilacın fiyatı / geri ödemesi tartışılırken tekel kökeni sorgulandığında
- Klinik araştırma denemesi sırasında Bolar kapsamı / FTO kaygısı belirdiğinde
- Formülasyon veya cihaz kombinasyonu değiştirileceğinde (reformulation, delivery device swap)
- Lisans / co-development / tech-transfer müzakerelerinde patent portföyünün değerlenmesi gerektiğinde
- Zorunlu lisans / paralel ithalat / kamu yararı tartışıldığında

### Ne zaman TETİKLENMEMELİ
- Salt klinik kanıt sentezi veya tedavi kılavuzu soruları → `medsearch` tetiklenmeli
- Salt pazarlama/ticari istihbarat (IQVIA pazar payı, launch trayektorisi) → `pharmaintel`
- Salt distribütörlük / lisans sözleşmesi taslağı → `lex-mercator` (ancak patent due diligence bu skill'de)
- Salt SGK / SUT geri ödeme dilekçesi → `onko-erisim` (ancak LOE sonrası fiyatlandırma etkileşimi bu skill'de yorumlanabilir)
- Salt özel sağlık sigortası teminat analizi → `saglik-sigorta`

## 3. Mantıksal Temel: "Kendi Başına Arama Yapanın İkilemi"

Farmasötik patent araştırmasında **salt anahtar kelime sorgusu sistematik bir başarısızlıktır**. Tek başına kullanıldığında eşzamanlı olarak hem **çok dar** (patent vekilinin kasıtlı standart dışı isimlendirmesi, jenerik Markush formülleri nedeniyle asıl tehdit gözden kaçar) hem **çok geniş** (hastalık adları, mekanizma terimleri binlerce teğetsel sonuç üretir) çıktı üretir. Bu nedenle bu skill **beş-katmanlı ardışık strateji** uygular:

1. **Kavramsal haritalama** — INN (Uluslararası Tescilli Olmayan İsim), ticari marka, CAS numarası, kimyasal eşanlamlı, mekanizma, terapötik sınıf ve hastalık MeSH terimleri eşanlamlı havuzu kurulur.
2. **Öncül Boolean sorgusu** — Bu havuzdan yüksek-alaka çekirdek belge seti (core set) elde edilir.
3. **Kod çıkarımı** — Çekirdek setin IPC/CPC kodları çıkarılır; taksonomik kilitler belirlenir.
4. **Sınıf tabanlı genişletme** — CPC kodu üzerinden anahtar kelime sınırı olmaksızın tam peyzaj taranır.
5. **Atıf + Markush + portföy analizi** — Forward/backward citation, jenerik Markush eşleştirme, en aktif assignee portföyleri.

Kısa yoldan çözülmesi talep edilse dahi bu akış kısaltılmaz; yalnız hangi adımda durulduğu çıktıda açıkça bildirilir.

## 4. Çalışma Modları (13 Mod)

Kullanıcının talebine göre **on üç moddan** biri devreye girer. Mod açıkça belirtilmemişse talebin semantiğinden çıkarım yapılır ve kullanıcıya kısaca bildirilir. Modlar birleştirilebilir (örn. FTO + Regulatory pazar-giriş takvimi için; Invalidity + Litigation dava dosyası için; DD + Licensing M&A için; Landscape Forecast + Licensing in-license stratejisi için; **TR_REGULATORY_FLOW + FTO + Regulatory** TR ürün dosyası + pazara giriş takvimi için).

### Mod 1 — FTO (Faaliyet Serbestisi / Freedom to Operate)

Müvekkilin planlanan ürününün (API, formülasyon, cihaz kombinasyonu, üretim süreci) üçüncü kişilerin aktif patent hakları nedeniyle piyasaya arzında engel bulunup bulunmadığını saptar.

**Girdiler**: Ürün tarifi · aktif farmasötik bileşen (INN/CAS/SMILES) · formülasyon karakteristikleri (doz, dozaj formu, salım profili, eksipiyanlar) · hedef pazar (TR, AB, ABD, ROW) · beklenen pazara arz tarihi · temsil edilen taraf (orijinatör / jenerik / biyobenzer / tıbbi cihaz).

**Adımlar**:
1. `references/markush-protokol.md` — Kimyasal çekirdeği haritala; Markush varyasyon tipleri ile potansiyel jenerik formüllere dahiliyet testi.
2. `references/cpc-ipc-kodlari.md` — A61K (preparatlar), A61M (uygulama cihazları), A61B (teşhis/cerrahi), B01D (saflaştırma), C07D (heterosiklik bileşikler) eksenli sınıf seçimi.
3. `references/veritabani-stratejileri.md` — Orange Book (referans ilaç patentleri + pediatrik uzatma), Purple Book (biyolojikler), Espacenet (aileler + INPADOC), USPTO Public Search (.CPC. saha kodu ile), TÜRKPATENT EPAAT (Türkiye geçerlilik), WIPO PATENTSCOPE (PCT ulusal fazlar), STN SciFinder (kimyasal alt-yapı).
4. Tespit edilen her aktif patent için **İstem Analizi Matrisi**: (a) bağımsız istem kapsamı, (b) bağımlı istem tuzakları, (c) doktrinel eşdeğer (doctrine of equivalents) riski, (d) istemin SMK m. 92 kapsamında yorum marjı, (e) ulusal faz durumu.
5. `references/smk-6769-ilac.md` — SMK m. 85 (sahip hakları), m. 92 (koruma kapsamı), m. 85/3 Bolar istisnası, m. 129 zorunlu lisans ekseninde yasal filtreleme.
6. `references/ruhsat-veri-imtiyazi.md` — Patent bitişi ile 6 yıllık veri imtiyazı bitişinin çakıştırılması (Gümrük Birliği alanında ilk ruhsat tarihi referans); en geç pazara giriş tarihi.
7. **Tasarım etrafından dolaşma (design-around) simülasyonu** — İhlal riski tespit edilirse farmasötik olarak eşdeğer, istem kapsamı dışında formülasyon/cihaz alternatifleri önerilir.
8. Çıktı: **FTO Raporu** (Carbon HTML veya docx) — `references/rapor-sablonlari.md §1` formatında. Her patent için "Temiz / Riskli / Kritik" renk kodu; her bulguda savunulabilir rasyonel.

**Kural**: FTO raporu mutlaka **"Rezidüel Risk Beyanı"** içerir — tespit edilemeyen, terk edilmiş, pending durumdaki başvuruların yaratabileceği geleceğe dönük riskler; ticari karar için epistemik sınırlar açıkça çizilir.

### Mod 2 — INVALIDITY (Hükümsüzlük / Geçersizlik Araştırması)

Rakibin aktif patentinin istemlerini, **yenilik** (novelty — SMK m. 83), **buluş basamağı** (inventive step — SMK m. 83/4), **yeterli açıklama** (sufficiency of disclosure — SMK m. 92/1), **çıkarılabilirlik** (extractability) ve **buluşa konu olabilirlik** (patentable subject matter) kriterlerinde çürütmek için sistematik prior art (önceki teknik) taraması.

**Girdiler**: Hedef patent numarası (TR/EP/US/WO) · saldırılacak spesifik istemler · temsil edilen taraf (saldırgan jenerik) · kritik pazara giriş tarihi.

**Adımlar**:
1. Patent aile ağacını (INPADOC family) Espacenet üzerinden tam çıkar; öncelik tarihini (priority date) kilitle — tüm prior art aramaları bu tarihten **önce** yayımlanmış olmalıdır.
2. Hedef istemlerin teknik özelliklerini **özellik-özellik** (feature-by-feature) listele.
3. `references/veritabani-stratejileri.md` — Her özellik için bağımsız Boolean sorgu + non-patent literature (NPL) taraması; `medsearch` composability ile PubMed, Google Scholar, YÖK Tez, bioRxiv.
4. `references/markush-protokol.md` — Önceki Markush açıklamalarında hedef spesifik bileşiğin örtülü kapsamında olup olmadığı (anticipation by genus disclosure) testi.
5. Her prior art belgesi için **Mozaik Tablosu** oluştur: hangi özellik hangi belge ile karşılanıyor; buluş basamağı için tek belge mi yoksa ikili kombinasyon mu gerekiyor (Türk hukukunda "ortalama uzman için aşikâr olma" testi).
6. `references/smk-6769-ilac.md` — SMK m. 99 kısmi hükümsüzlük, m. 138 geçersizlik davası, ex tunc etki ekseninde hukuki yorum.
7. `references/ictihat-emsal.md` — Yargıtay 11. HD'nin özellikle **ikinci tıbbi kullanım** ve **seçim buluşu** (selection invention) içtihatlarının hedef istem tipine uygulanabilirliği.
8. Çıktı: **Invalidity Briefing** (`references/rapor-sablonlari.md §2`) — istem-istem hükümsüzlük argümanı, mozaik haritası, güvenilirlik derecelendirmesi (strong / moderate / weak), mahkeme stratejisi seçenekleri (FSHHM hükümsüzlük davası vs. TÜRKPATENT YİDK itirazı vs. EPO opposition vs. üçüncü kişi görüşü).

**Kural**: Invalidity çıktısı **"Atak Vektörü Önceliklendirmesi"** içerir — farklı argüman aileleri (yenilik vs. buluş basamağı vs. yeterli açıklama) ayrı ayrı puanlandırılır; müvekkile hangi kombinasyonun mahkemede en yüksek başarı şansı verdiği gerekçelendirilir.

### Mod 3 — LANDSCAPE (Patent Peyzajı / Teknoloji Haritalaması)

Bir moleküler hedef, modalite (ADC, CAR-T, bispesifik, RNA, GLP-1, PROTAC), endikasyon veya teknoloji sahası için tam patent coğrafyasını çıkarır. Yalnız aktif patentleri değil; süresi dolmuş, pending, terk edilmiş, ret edilmiş başvuruları da kapsar.

**Girdiler**: Araştırılan alan tanımı (hedef/modalite/endikasyon/teknoloji) · coğrafi kapsam · zaman ufku · analitik derinlik (stratejik özet vs. tam atıf ağı).

**Adımlar**:
1. **Kavramsal parametrik haritalama** — INN listesi, mekanizma sınıfı, hedef reseptör/protein, endikasyon sınıflandırma kodları (ICD-10, MeSH).
2. **CPC hiyerarşik tarama** — ilgili A61K alt grupları + C07D (heterosiklik), C07K (peptid/protein), C12N (genetik mühendislik) sınıflarında tam sorgulama.
3. **Portföy kümeleme** — En aktif başvuru sahipleri (assignee), mucitler, kurumsal akademik işbirlikçiler; ilk-başvuru coğrafyası (USPTO → EP → JP → CN → WO eğilimleri).
4. **Atıf ağı analizi** — forward (kim bu patenti referans aldı) + backward (bu patent hangilerini referans aldı) citation network; "temel patent" (foundational patent) vs "çevre patenti" (peripheral patent) ayrımı.
5. **Zaman serisi** — yıllık başvuru hacmi, coğrafi yayılım, yaşam döngüsü (pending → granted → maintained → lapsed/expired).
6. **Evergreening haritası** — aynı moleküle ilişkin birincil madde patenti, polimorf, tuz, formülasyon, ikinci tıbbi kullanım, devam (continuation), bölünmüş (divisional), terminal disclaimer ilişkileri; toplam koruma ömrü modeli.
7. **BERT / NLP tabanlı öngörü** — Spesifikleşmiş kimyasal ilaç patent sınıflayıcıları ile henüz regülatör onayı almamış ancak patent peyzajında görünen molekülleri saptama; erken uyarı katmanı.
8. Çıktı: **Landscape Raporu** (`references/rapor-sablonlari.md §3`) — görsel atıf ağı (mümkünse visualize tool ile), assignee tablosu, zaman serisi çizelgesi, kritik patent ailesi özetleri, stratejik implikasyonlar (yatırım / lisans / girişim fırsatları).

### Mod 4 — LIFECYCLE (Portföy Yaşam Döngüsü Yönetimi)

Orijinatör firma perspektifinden bir ürünün ticari korunma ömrünü **yasal sınırlar içinde** maksimize etmek veya jenerik rakip için bu stratejiyi sökmek.

**Girdiler**: Ürün profili · mevcut patent portföyü · pazar pozisyonu · Ar-Ge pipeline'ı · 10 yıllık ticari hedef.

**Adımlar**:
1. **Portföy ilk denetimi** — birincil madde patenti, polimorf/tuz/hidrat patentleri, formülasyon patentleri (uzatılmış salınım, kombinasyon, kötüye kullanım engelleyici), ikinci tıbbi kullanım, üretim usul patentleri, cihaz/uygulama sistemi patentleri, pediatrik formülasyon, salt eksipiyan patentleri.
2. **Evergreening fırsat analizi** — ürünün hangi fizikokimyasal, farmakokinetik, kombinasyon, iletim, pediatrik veya cihaz boyutunda yeni istem üretilebilir olduğu; Türkiye'de Yargıtay'ın evergreening karşı-argümanlarına dayanıklılık değerlendirmesi.
3. **Veri imtiyazı kalkanı** — patent süresinden bağımsız 6 yıllık veri imtiyazı (Gümrük Birliği alanı ilk ruhsat tarihi bazlı), pediatrik ruhsat uzatması etkileşimi.
4. **Cihaz entegrasyonu** — inhaler, prefilled syringe, auto-injector, otonom pompalar gibi kombinasyon ürünleri üzerinden CPC A61M kapsamında ikincil patent duvarı inşası; `references/tibbi-cihaz-uts.md` üzerinden ÜTS + CE + ISO 13485 uyumluluğu.
5. **Coğrafi başvuru stratejisi** — PCT ulusal fazları, EPO validation, öncelikli pazar seçimi (Türkiye pazarı için TR başvurusu + EPO yolu kıyaslaması); küçük pazarlarda tescil maliyeti optimizasyonu.
6. **Bölünmüş başvuru (divisional) ve devam (continuation)** — SMK m. 91 ve EPO Rule 36 kapsamında bekletilmiş istem korumaları; stratejik pending havuzu.
7. **Çapraz-lisans simülasyonu** — rakiplerin portföylerine karşı savunma lisansları, pool anlaşmaları.
8. **Patent iptal / hakedişten vazgeçme kararları** — yıllık harç vs. getiri optimizasyonu.
9. Çıktı: **Lifecycle Yol Haritası** (`references/rapor-sablonlari.md §4`) — Gantt-benzeri takvim (birincil patent bitişi, her ikincil patentin bitişi, veri imtiyazı, pediatrik uzatma, jenerik erişim penceresi), stratejik karar noktaları (go/no-go), öngörülen gelir erozyonu modeli.

### Mod 5 — REGULATORY (Ruhsat-Patent Entegrasyonu)

Patent hakkı ile idari ruhsat rejiminin birbirini kestiği gri alanda karar verir; pazara giriş takvimini saniyesi saniyesine hesaplar.

**Girdiler**: İlaç / cihaz profili · referans ilacın ilk ruhsat tarihi (Türkiye ve Gümrük Birliği alanı) · patent durumu · ruhsat stratejisi (tam dosya / kısaltılmış / literatür tabanlı).

**Adımlar**:
1. `references/ruhsat-veri-imtiyazi.md` — **6 yıllık veri imtiyazı hesabı**: imtiyaz, Gümrük Birliği alanında (AB + TR) ilk ruhsatlandırma tarihinden başlar; Türkiye patent süresinden kısa ise patent süresi ile sınırlıdır. Pediatrik uzatma ve orphan drug istisnaları değerlendirilir.
2. **Bolar istisnası yorumu** — Ruhsat hazırlığı amaçlı Ar-Ge, biyoeşdeğerlik, biyoyararlanım denemeleri tecavüz sayılmaz (SMK m. 85/3). Ancak ticari stoklama, deneme ötesi üretim, ihracata yönelik faaliyet Bolar dışıdır. Sınır çiziminde `references/ictihat-emsal.md` Yargıtay 11. HD kararları.
3. **Kısaltılmış başvuru stratejisi** — jenerik/biyobenzer ruhsat dosyasında referans verilen orijinal dosyaya atıf; veri imtiyazı penceresi dışında atıf serbest.
4. **Tıbbi cihaz entegrasyonu** — `references/tibbi-cihaz-uts.md` ÜTS kayıt, CE sınıflandırması (I/IIa/IIb/III), ISO 13485 kalite sistemi, kombinasyon ürün ikili rejimi (ilaç+cihaz).
5. **TÜRKPATENT 2024 Nice güncellemesi** — 44. sınıf (diş hekimliği, psikolog hizmetleri), 39. sınıf (sağlık turizmi), 09. sınıf (yapay zeka teşhis robotları) koruma kapsamları.
6. **Zorunlu lisans ve kamu yararı** — SMK m. 129 ekseninde Cumhurbaşkanlığı kararı ihtimali; Doha deklarasyonu ve 6471 sayılı TRIPS protokolü ile ihracat amaçlı zorunlu lisans; paralel ithalat simülasyonu (referans fiyatlandırma etkisi).
7. Çıktı: **Pazara Giriş Takvimi** (`references/rapor-sablonlari.md §5`) — patent bitişi, veri imtiyazı bitişi, pediatrik uzatma, SPC (Türkiye'de uygulanmayan ancak ihracat pazarları için), en erken ruhsat başvuru tarihi, en erken piyasaya arz tarihi; riskler (ihtiyati tedbir ihtimali, itiraz prosedürleri).

### Mod 6 — LITIGATION (Dava Savunusu / İhtilaf Yönetimi)

FSHHM nezdinde patent tecavüzü, hükümsüzlük, delil tespiti, ihtiyati tedbir davalarında taraf argümanını kurar.

**Girdiler**: İhtilafın niteliği (tecavüz / hükümsüzlük / tespit / tedbir) · taraflar · mevcut delil · süreç aşaması · acillik.

**Adımlar**:
1. `references/ictihat-emsal.md` — Yargıtay 11. HD, FSHHM, Danıştay, AYM emsal taraması; UYAP Mevzuat + Karar Arama + Yargıtay Bilgi Sistemi (9.8 milyon karar) üzerinden spesifik emsal çıkarma.
2. **Tecavüz argümanı (orijinatör)** — istem yorumu (claim construction), doğrudan tecavüz + dolaylı tecavüz + eşdeğer doktrini; SMK m. 141-142 tecavüz tanımı, m. 149 haklar.
3. **Hükümsüzlük savunması (jenerik)** — Mod 2 Invalidity çıktısının dava formatına aktarımı; istem bazında yenilik/buluş basamağı/yeterli açıklama/hak sahipliği saldırı hattı; kısmi hükümsüzlük talebi (SMK m. 138/3) — ex tunc etki.
4. **İhtiyati tedbir kararı / kaldırılması** — HMK m. 389-390 + SMK m. 159 teminatlı tedbir prosedürü; "yaklaşık ispat" (prima facie) eşiği; jenerik tarafın teminatlı tedbir kaldırma prosedürü; Yargıtay'ın ilaç davalarında tedbir eşiği içtihadı.
5. **Delil tespiti (HMK m. 400)** — rakip üretim tesisinde numune alma, üretim süreci gözlemi.
6. **İkinci tıbbi kullanım özel analiz** — Swiss-type claim vs EPC-2000 purpose-limited claim formatı; Türkiye'de eczane pratiğinde "off-label" / "cross-labeling" zemininde tecavüz isnadı zorluğu; Yargıtay Hukuk Genel Kurulu kararları.
7. **TÜRKPATENT YİDK süreci** — idari itiraz, YİDK kararına karşı Danıştay iptal davası.
8. **EPO Opposition** — 9 ay içinde itiraz, Opposition Division + Board of Appeal; Türkiye tescili üzerindeki dolaylı etki.
9. **Üçüncü kişi görüşü (third party observation)** — inceleme aşamasındaki başvuruya dava açmaksızın argüman sunma.
10. Çıktı: **Litigation Briefing** (`references/rapor-sablonlari.md §6`) — hukuki vaka analizi, emsal listesi, argüman hattı, karşı argüman risk haritası, önerilen işlem sırası (çok-forum stratejisi: FSHHM + TÜRKPATENT YİDK + EPO + WIPO PATENTSCOPE üçüncü kişi görüşü).

**Kural**: Litigation çıktısı **"karar ağacı"** formatında sunulur — her işlem adımının olası sonucu ve bir sonraki karar noktası.

### Mod 7 — DUE DILIGENCE (M&A + Licensing Due Diligence) [v1.2.0]

Bir target firma veya asset için IP portföy due diligence: portföy envanteri, geçerlilik analizi, coğrafi kapsam, FTO durumu, değerleme, red flag tespiti.

**Girdiler**: Target firma/asset tanımı · deal yapısı (iktisap / lisans / opsiyon) · hedef coğrafi kapsam · data room erişimi · deal timeline.

**Adımlar**:
1. `references/patent-degerleme.md` — Üç değerleme yaklaşımı çerçevesi (cost / market / income) + Monte Carlo metodolojisi.
2. **Portföy envanteri** — her patent ailesi için INPADOC genişletmesi, coğrafi yayılım haritası, yıllık harç durumu, patent-ürün bağlantı matrisi.
3. **Geçerlilik analizi** — her kritik patent için prior art taraması (Mod 2 Invalidity iş akışının hızlandırılmış versiyonu), hükümsüzlük olasılığı derecelendirmesi.
4. **Coverage haritası** — patent × ülke × ürün grid; boşluklar (gap analysis) tespit edilir.
5. **FTO analizi** — target ürünlerin 3. taraf patentler karşısındaki durumu (Mod 1 FTO'nun portföy-ölçekli versiyonu).
6. **Değerleme** — income approach (rNPV + Monte Carlo), relief-from-royalty, comparable transactions.
7. **Red flag haritası** — devam eden davalar, tercüme hataları, yıllık harç gecikmeleri, terk edilen ülkeler, hak sahipliği anlaşmazlıkları.
8. **Reps & warranties önerileri** — deal dokumentasyonunda garanti edilmesi gereken patent klausları.
9. Çıktı: **Due Diligence Report** (`references/rapor-sablonlari.md §7`) — target portföy değer aralığı, red flag tablosu, go/no-go önerisi, risk azaltma önerileri.

**Kural**: DD raporu **her assertion için audit trail** içermelidir — hangi data room dokümanı, hangi EPAAT / Espacenet sorgu, hangi tarih. Buyer bu audit trail'i kendi bağımsız DD'sinde doğrulayacaktır.

### Mod 8 — OPPOSITION (EPO 9 Aylık Opposition + TÜRKPATENT 3. Kişi Görüşü) [v1.2.0]

Pre-grant (3. kişi görüşü) veya post-grant (9 ay EPO opposition) formal idari/yarı-yargısal itiraz süreçlerinin yönetimi. FSHHM hükümsüzlük davasından (Mod 6) daha hızlı, düşük maliyetli alternatif.

**Girdiler**: Hedef patent (EP veya TR başvuru) · süre durumu (granted tarihi / yayım tarihi) · hedeflenen istemler · mevcut prior art.

**Adımlar**:
1. **Forum belirleme** — granted EP + 9 ay içinde → EPO Opposition; yayımlanmış TR başvuru → TÜRKPATENT 3. kişi görüşü; granted TR patent → FSHHM (Mod 6'ya yönlendir).
2. `references/fto-invalidity-protokol.md §2` — Invalidity iş akışının EPO/TÜRKPATENT formatına uyarlanması.
3. **EPC Article 100 bazında gerekçe haritası** — 100(a) patentability + 100(b) insufficient disclosure + 100(c) added matter.
4. **Problem-Solution Approach uygulaması** — EPO buluş basamağı analizi için zorunlu çerçeve.
5. **Plausibility argümanı** — EPO T 1329/04 doktrini; broad genus + dar örnek endişesi.
6. **Added matter analizi** — EPC Art. 123(2); başvuru sonrası kapsam genişletme iddiası.
7. **Oral proceedings hazırlık** — EPO sözlü duruşma stratejisi; patent sahibinin olası amendment argümanları.
8. **Çok-opposition koordinasyonu** — birden fazla opposant paralel çalışırsa argüman paylaşımı + forum koordinasyonu.
9. Çıktı: **Opposition Briefing** (`references/rapor-sablonlari.md §8`) — EPC madde bazında argüman hattı, prior art delilleri, oral proceedings strateji, maliyet projeksiyonu.

**Kural**: EPO opposition notice dilekçesi EPO-akredite patent vekili onayı olmaksızın gönderilmez. TÜRKPATENT 3. kişi görüşü için vekil gerekli değil ama kalite için önerilir.

### Mod 9 — BIOSIMILAR PATHWAY (Biyobenzer Yol Haritası) [v1.2.0]

Referans biyolojik ürün için biyobenzer geliştirme stratejisi: karşılaştırılabilirlik paketi, patent duvarı aşma, regülatör rejim, extrapolation, cihaz stratejisi, pazar pozisyonlaması.

**Girdiler**: Referans ürün (INN + marka) · modalite (mAb / ADC / peptid / fusion protein / hormon) · hedef pazar (TR + AB + ABD) · aday başlangıç yılı · üretim kapasitesi durumu.

**Adımlar**:
1. `references/biyobenzer-yol.md` — EMA/FDA/TİTCK biyobenzer rejim detayı + karşılaştırılabilirlik paketi + extrapolation + interchangeability.
2. **Patent duvarı haritası** — molekül + formülasyon + cihaz + ikinci tıbbi kullanım patentleri için tam portföy analizi (Mod 1 FTO + `tibbi-cihaz-uts.md` entegrasyonu).
3. **Veri imtiyazı hesabı** — TR (6 yıl) + AB (8+2+1) + ABD (12 yıl) üç ayrı formül uygulanır.
4. **CQA (Critical Quality Attributes) tanımlama** — referans ürünün kritik kalite özelliklerinin lot-to-lot varyasyon aralığı → biyobenzer hedef pencere.
5. **Klinik geliştirme stratejisi** — en duyarlı endikasyon seçimi; Faz I PK (sağlıklı gönüllü) + Faz III etkinlik (200-900 hasta); immünojenisite izlemi + switching study.
6. **Extrapolation planı** — hangi endikasyonlar bilimsel gerekçe ile tek pivotal çalışmadan uzatılabilir; mekanizma-bazlı değerlendirme.
7. **Cihaz stratejisi** — kendi cihaz geliştirme vs üçüncü taraf tedarikçi (Ypsomed, SHL, BD); ÜTS + CE + ISO 13485 entegrasyonu (`tibbi-cihaz-uts.md`).
8. **Pazara giriş zamanlaması** — Bolar takvimi; "first mover" vs "fast follower" pozisyon analizi.
9. **Finansal model** — yatırım (CapEx + OpEx) + revenue ramp-up + COGS + NPV + IRR.
10. Çıktı: **Biosimilar Pathway Briefing** (`references/rapor-sablonlari.md §9`) — patent + regulatory + klinik + üretim + ticari entegre strateji.

**Kural**: Yeni modaliteler (ADC biosimilar, CAR-T biobetter, gene therapy biosimilar) için `references/yeni-modaliteler.md` ayrıca okunmalıdır — klasik biyobenzer çerçevesi yeterli değildir.

### Mod 10 — LICENSING (Lisans Müzakere) [v1.4.0]

Bir patent/asset için lisans anlaşmasının finansal modellemesi + hukuki çerçevenin inşası. In-licensing veya out-licensing stratejisi için entegre yaklaşım.

**Girdiler**: Asset tanımı (molekül/endikasyon/aşama) · müzakere tarafı (licensor vs licensee) · hedef pazar · müzakere pozisyonu (güçlü/zayıf) · karşılaştırılabilir transaksiyon verisi · hedef royalty + upfront + milestone yapısı.

**Adımlar**:
1. `references/patent-degerleme.md` — Üç değerleme yaklaşımı + Monte Carlo + RFR metodolojisi.
2. **Karşılaştırılabilir transaksiyon taraması** — SEC EDGAR + EvaluatePharma + Cortellis deals + GlobalData Pharma kaynakları.
3. **Deal yapısı tasarımı** — upfront + development milestones + sales milestones + tiered royalty (örneğin %10-12-15 tier'ları).
4. **PTRS ayarlaması** — klinik geliştirme aşamasına göre risk ayarlaması (Faz I-II-III farklı olasılıklar).
5. **Vergi optimizasyonu** — Türkiye patent box rejimi (KVK m. 32/B) + Ar-Ge teşviki entegrasyonu; transfer pricing (BEPS 8-10) uyumu.
6. `scripts/royalty-calculator.py` — NPV + IRR + discount rate sensitivity + sektörel benchmark karşılaştırması.
7. **Comparable transactions raporu** — son 3-5 yılın benzer deal'ları tablolanır.
8. **`lex-mercator` skill'i ile entegrasyon** — sözleşme drafting + redline + klaus bank (downstream composability).
9. **Negotiation rehberi** — BATNA (best alternative to negotiated agreement), ZOPA (zone of possible agreement), anchor fiyatlama.
10. Çıktı: **License Negotiation Memo** — deal yapısı + finansal model + müzakere stratejisi + hukuki çerçeve.

**Kural**: Licensing çıktısı **müzakere kırmızı çizgileri** içermelidir — kabul edilmeyecek koşullar açıkça belirtilir. Exit stratejisi + alternatif senaryolar sunulmalıdır.

### Mod 11 — LANDSCAPE FORECAST (BERT/NLP Öngörü) [v1.4.0]

Mevcut patent + başvuru trendleri ile **ortaya çıkan** (henüz kritik olmamış) alanları tahmin eden ileri landscape analizi. Rakibin gelecek 2-5 yıl patent portföyünü öngörmeye çalışır.

**Girdiler**: Teknoloji alanı (modalite + hedef) · coğrafi kapsam · zaman penceresi (geçmiş için 5-10 yıl retrospektif) · rakip şirket listesi (opsiyonel) · odak sektörler.

**Adımlar**:
1. `references/veritabani-stratejileri.md` — Tam landscape verisi toplama (Espacenet + USPTO + PATENTSCOPE + Google Patents).
2. **NLP özellik çıkarımı** — istem metinlerinden BERT/transformer-tabanlı özellik ayrıştırması (hedef, modalite, mekanizma, endikasyon).
3. **Trend analizi** — yıllık başvuru sayısı + assignee konsantrasyonu + CPC evolüsyonu.
4. **Yükselen sinyaller** — henüz az sayıda patent başvurusu olan ama hızla büyüyen niche alanlar (emerging signals).
5. **Rakip portföy öngörüsü** — son 2-3 yıl başvuru hızına dayalı, önümüzdeki 2-3 yılda gelecek başvurular.
6. **Semantic similarity clustering** — istemlerin benzer gruplanması (BERT embedding + k-means veya DBSCAN).
7. **Patent "boşlukları"** — belirli hedef × modalite kombinasyonlarında patent yoksunluğu (white space) — opportunity.
8. `scripts/cpc-recommender.py` — Hedef molekül için uygun CPC kodları.
9. **Citation network analizi** — foundational patentlerden gelişim yolunun haritalanması.
10. Çıktı: **Landscape Forecast Report** — mevcut peyzaj + 2-5 yıl öngörü + boşluklar + rakip sinyalleri + yatırım önerileri.

**Kural**: Forecast çıktısı **belirsizlik aralıkları** içermelidir — noktasal tahmin yerine senaryo bazlı (konservatif / baseline / agresif) öngörüler. BERT/NLP tabanlı tahminlerde **false positive** riski açıkça belirtilir.

### Mod 12 — EXPERT WITNESS (Bilirkişi Rapor Hazırlığı) [v1.4.0]

FSHHM veya TÜRKPATENT YİDK için bilirkişi rapor taslağının hazırlanması. Mahkeme önünde savunulabilir, bilimsel + hukuki standartlara uyumlu bilirkişi raporu.

**Girdiler**: Dava dosya bilgisi · mahkeme soruları · dava tarafları · taraf iddialarının özeti · mevcut teknik deliller · bilirkişinin uzmanlık alanı.

**Adımlar**:
1. `references/ictihat-emsal.md` — Yargıtay 11. HD bilirkişi raporu eğilimleri + FSHHM pratiği + HMK m. 266 bilirkişi bağımsızlığı.
2. **Mahkeme sorularının ayrıştırılması** — her soru için spesifik yanıt yapısı.
3. **Uzmanlık alanı doğrulaması** — bilirkişinin dava konusuyla uyum testi (Yargıtay'ın "uzmanlık dışı" reddini önleme).
4. **Çıkar çatışması beyanı** — bilirkişi bağımsızlığının açık beyanı.
5. **Metodoloji beyanı** — kullanılan analitik çerçeve (claim construction, özellik ayrıştırması, problem-solution) açıkça belirtilir.
6. **Tecavüz analizi** (tecavüz davasında) — literal + doktrinel eşdeğer testi; `fto-invalidity-protokol.md §1`.
7. **Hükümsüzlük analizi** (hükümsüzlük davasında) — yenilik + buluş basamağı + yeterli açıklama; `fto-invalidity-protokol.md §2`.
8. **Zarar hesaplama** (SMK m. 151) — üç yöntem + en uygun seçim; `patent-degerleme.md`.
9. **Savunulabilirlik testi** — sözlü duruşmada taraflara cevap verecek kadar güçlü argümanlar.
10. Çıktı: **Expert Witness Report** (`rapor-sablonlari.md §10`) — bilimsel + hukuki savunulabilir bilirkişi raporu taslağı.

**Kural**: Expert Witness Report **final metin** değil, **taslak**tır. Gerçek bilirkişi raporu atanan kurul bilirkişileri tarafından onaylanır. Bu mod, tarafların davanın teknik hazırlığı için bilirkişiye sunabilecekleri nitelikli materyal üretir.

### Mod 13 — TR_REGULATORY_FLOW (Türk Regülatör + IP Akış Otomasyonu) [v2.0.0]

Türk regülatör ekosisteminin programatik kabuğu. Tek bir ilaç barkodu, INN, ATC kodu, holder adı veya patent başvurusundan başlayarak — **TİTCK MCP** (56 araç), **Türk Patent MCP** (6 araç) ve **Mevzuat MCP** (12 araç, v2.0.1 aktif) üçgenini yürütür; web tarayıcısı kabuk önündedir, MCP arkadaki kanonik kaynaktır. Diğer 12 modun **TR-girdi katmanı**dır: FTO (Mod 1), Lifecycle (Mod 4), Regulatory (Mod 5), Litigation (Mod 6), DD (Mod 7), Biosimilar (Mod 9) modları için zorunlu önişleme adımı haline gelir.

**Girdiler**: Aşağıdakilerden en az biri — TİTCK barkodu (8479xxxxxxxxx) · INN/etkin madde · ATC kodu (örn. L01XC03) · ICD-10 (off-label / yurt dışı etkin madde için) · holder adı (alias varyantları dahil) · TR patent/başvuru numarası · marka adı · SMK madde numarası.

**MCP-first protokol** (`references/turk-mcp-entegrasyonu.md` zorunlu okuma):

1. **Discovery (TİTCK)** — `search_drugs` (FTS5 smart query), `search_active_ingredients`, `search_holders` ile kanonik kayıt id (`master::barcode`, `holder::id`) elde edilir. Web sitesi kazınmaz.

2. **Identity dosyası (TİTCK)** — `get_drug` + `get_drug_snomed_profile` + `get_holder_portfolio` ile ürün + sahip + ATC + SNOMED CT substance bağı kurulur. SNOMED bağı, eşdeğerlik ve **biyobenzer grup** tespitinin atomu.

3. **Eşdeğerlik + biyobenzer kümesi (TİTCK)** — `find_shared_substance_peers` + `find_biosimilar_group` + `find_equivalent_products_by_substance` üçlüsü. Mod 9 Biosimilar Pathway'in TR-tarafı ön-işlemesi; en eski referans ürün otomatik işaretlenir (8 yıl AB / 6 yıl TR veri imtiyazı çapası).

4. **ATC peyzajı (TİTCK)** — `get_atc_class_summary` + `get_atc_hierarchy` + `find_first_in_class` ile sınıf-bazlı ilk-pazara-girene-ait koruma + rekabet haritası. Mod 3 Landscape ve Mod 11 Forecast için TR çapası.

5. **Fiyat + erişim (TİTCK)** — `get_price_history` (FSF / depocu / eczacı / kamu zinciri + İŞLEM GEÇMİŞİ) + `find_reference_prices_for_drug` (Referans Bazlı Fiyat Listesi) + `search_institutional_fees` (Kurum Hizmet Fiyatları). Fiyat tavanı + LOE sonrası erozyon modeli için canlı veri.

6. **Pipeline ve istisnalar (TİTCK)** — `find_regulation_article23_for_drug` (Madde 23 muafiyet başvuruları) + `find_off_label_uses_for_drug` (Endikasyon Dışı Kullanım Listesi — onkoloji organ kategorileri) + `find_supply_tracked_ingredients_for_drug` + `find_additional_monitoring_for_drug`.

7. **Çıkış + uyarılar (TİTCK)** — `find_authorization_cancellations_for_drug` + `get_withdrawal_trend` (yıl-yıl iptal eğilimi) + `find_batch_release_certificates_for_drug` (Seri Serbest Bırakma — biyolojikler için kritik).

8. **Belge tarama (TİTCK)** — `search_documents` + `find_documents_for_drug` + `find_documents_by_substance` ile indekslenmiş PDF/DOCX dokümanlar (doktor bilgilendirme yazıları, KÜB değişiklikleri) tam metin sorgusu.

9. **Patent katmanı (Türk Patent MCP)** — `search_patents` (applicant + IPC/CPC + abstract anahtar kelime + attorney) → eşleşen patentler için `get_patent_details`. EP→TR validation, ulusal başvuru, jenerik firma savunmaları, akademik/kurumsal ortaklık tespiti. Mod 1 FTO'nun TR-tarafı kanonik araması.

10. **Marka + tasarım (Türk Patent MCP)** — `search_trademarks` (Nice 5/10/35/44 sınıfları farmasötik için kritik) + `search_designs` (Locarno 28-03 medikal cihaz, 24-01 terapötik). Lifecycle Mod 4'te kombinasyon ürün cihaz patenti + endüstriyel tasarım çakışması; ticari marka çatışmaları (örn. jenerik benzeri marka).

11. **Mevzuat tam metni (Mevzuat MCP — v2.0.2 envanter kategorize)** — 12 araçlı envanter 5 kategoride orkestre edilir:
    - **A. Arama** (3): "mevzuat.gov.tr'de ara" full-text · "Mevzuat fihristinde ara" yapısal/hiyerarşik · "Mülga mevzuatta ara" yürürlükten kalkmış mevzuat
    - **B. Detay erişim** (4): "Ham mevzuat dosyası indir" · "Mevzuat HTML içeriği" · "Mevzuat meta bilgisi" · "Mevzuat metni (PDF → text)" — madde-bazlı tam metin alıntısı için
    - **C. Tarih** (1): "Önceki mevzuat metinleri" — versiyon karşılaştırma (551 KHK ↔ SMK 6769 geçişi)
    - **D. Listeleme/Referans** (2): "Mevzuatı türe göre listele" · "Mevzuat tür kodları" — kategori tarama
    - **E. Kompozit/Özel** (2): "Kapsamlı mevzuat semantik kanıt paketi" — agregat akıllı bağlam · "1982 Anayasası" — özel domain
    
    Tipik kullanım: SMK 6769 m. 85/3 Bolar metni için → **A→B** (search → get_text); 551 KHK ↔ SMK karşılaştırması için → **C** (önceki versiyonlar); BTÜ Yönetmeliği güncel hali için → **A→B**; karmaşık çapraz-mevzuat bağlamı için → **E** (semantik kanıt paketi).

12. **Çapraz-doğrulama** — Aynı barkoda hem `search_drugs` hem `search_authorization_cancellations` çakışması mı? Holder alias farklı yazımları aynı kanonik holder'a mı çözülüyor (`find_holder_by_alias` + `list_holder_aliases`)? Etkin madde SNOMED bağı çözülemiyorsa (`list_unmapped_ingredients`'te mi?) — kanonik substance haritası eksikliği belirtilir.

13. Çıktı: **TR Regülatör + IP Dosyası** (`references/rapor-sablonlari.md §11` — v2.0.0 ile eklenecek). Yapı: (a) Ürün kartı (TİTCK kanonik), (b) Holder portföy özeti, (c) Eşdeğer / biyobenzer kümesi, (d) ATC peyzajı + first-in-class çapası, (e) Fiyat zinciri tablosu, (f) Pipeline + istisna kayıtları, (g) Patent + marka + tasarım eklentileri, (h) Mevzuat alıntıları, (i) Çapraz-doğrulama notları, (j) Diğer modlara (FTO, Regulatory, Biosimilar) bağlama vektörleri.

**Kural — MCP-first**: Bu mod aktifken TR ekosisteminden **hiçbir veri web kazımayla** çekilmez. Kanonik kaynak MCP'dir. Web fetch yalnızca (i) MCP envanteri eksik olduğunda (Mevzuat geçici), (ii) gerçek-zamanlı haber/duyuru için, (iii) MCP tool failure'unda audit-trail amaçlı kullanılır. Her veri noktası için provenance: `[TİTCK MCP / search_drugs / 2026-05-01]` formatında ek konur.

**Kural — composability**: Mod 13 **bağımsız çalıştırılabilir** (sade TR ürün dosyası talebi için), ancak çoğu vakada **diğer modların önişleme katmanı** olarak çağrılır. Örneğin "jenerik semaglutide TR'de ne zaman piyasaya girebilir?" → Mod 13 (referans ürün TİTCK kartı + biyobenzer kümesi + fiyat) → Mod 5 Regulatory (LOE + veri imtiyazı + Bolar) → Mod 1 FTO (Türk Patent MCP ile cihaz patenti araması) → Mod 9 Biosimilar Pathway.

**Kural — Mevzuat MCP entegrasyonu (v2.0.1)**: Mevzuat MCP envanteri teyit edildi (12 araç aktif). Bu mod aktifken SMK / yönetmelik / tebliğ / genelge / Resmi Gazete alıntıları doğrudan Mevzuat MCP'den `[Mevzuat MCP / <tool> / <mevzuat_id> / <erişim>]` provenance damgası ile çekilir. İçtihat (Yargıtay/Danıştay/AYM kararları) Mevzuat MCP kapsamı dışıdır; bu katman için `references/ictihat-emsal.md §1`'deki UYAP karar arama protokolü uygulanır.

## 5. Teknik Derinlik Protokolü

### 5.1. Bilimsel okuryazarlık zorunluluğu

Her analiz, buluşun kimyasal-biyolojik-farmakolojik-biyoteknolojik **özünü** anlamadan başlamaz. Asgari derinlik:
- **Küçük molekül**: SMILES/InChI okuryazarlığı, stereokimyasal isomerizm (enantiyomer, diastereomer, atropisomer), polimorfizm, tuz formu, hidrat/solvat, formülasyon eksipiyanlarının işlevsel gerekçesi.
- **Biyolojikler**: protein sekansı (primer), domain organizasyonu, glikozilasyon paterni, Fc-fragman modifikasyonları (ADCC/CDC artışı, efektörsüzleştirme), ADC yük-linker-antikor üçlüsü, bispesifik formatlar (BiTE, DuoBody, CrossMab).
- **Gen/hücre tedavi**: vektör tipi (AAV serotipleri, lentiviral, retroviral), transgen, promotör, CAR tasarımı (scFv-hinge-transmembran-sinyal domenleri), HLA eşleştirme.
- **Cihaz**: iletim mekanizması (dozaj, tetikleyici, biyouyumluluk), sensör/aktüatör mimarisi, yazılım katmanı (IEC 62304).

Bilimsel dili hatalı yorumlayan her IP argümanı mahkeme önünde çürür. Gerekirse `medsearch` composability çağrılarak hakemli literatür üzerinden bilimsel zemin sağlamlaştırılır.

### 5.2. Markush topolojisi

Farmasötik patentlerin belkemiği 1924'ten bu yana Markush jenerik formülleridir. Klasik alt-yapı (substructure) araması yetersiz kalır; spesifik hedef bileşiğin jenerik açıklama kapsamında olup olmadığı matematiksel/topolojik olarak test edilmelidir. Dört varyasyon tipi — **sübstitüsyon**, **pozisyonel**, **frekans**, **homoloji** — ve jenerik düğümler (A, Q, M, X, Ak, Cb, Cy, Hy, ARY, HET, CHK) için `references/markush-protokol.md` zorunlu okumadır. STN IP Protection Suite ve CAS SciFinder Markush eşleştirme motorları ile ücretsiz alternatiflerin limitleri bu referansta karşılaştırılır.

### 5.3. IPC / CPC taksonomisi

İşbirlikçi Patent Sınıflandırması (CPC) 260.000+ kod ile IPC'nin granüler halefi; bir patente birden çok kod atanabildiğinden araştırma radarını genişletir. Farmasötik / tıbbi cihaz alanında kritik alt-bölümler için `references/cpc-ipc-kodlari.md`.

### 5.4. Veri tabanı çokluğu

Tek bir veri tabanı üzerinden karar yetersizdir. Orange Book (ABD referans ilaç), Purple Book (biyolojikler), Espacenet (140M+ yayın, INPADOC aileleri), USPTO Patent Public Search (.CPC. saha kodu), TÜRKPATENT EPAAT (Türkiye geçerlilik + yıllık harç durumu), WIPO PATENTSCOPE (PCT ulusal fazlar), STN SciFinder (kimyasal topoloji). Detaylı Boolean sözdizimleri ve sınırlılıkları için `references/veritabani-stratejileri.md`.

### 5.5. Türk Regülatör MCP-First Doktrini [v2.0.2]

Türkiye ekosistemi için skill v2.0.2 itibarıyla **MCP-first** kanonik doktrini tam aktive edilmiştir. Üç MCP de canlı; 12 Mevzuat MCP aracı 5 fonksiyonel kategoride envanterlenmiş:

| MCP | Kapsam | Araç sayısı | Durum |
|---|---|---|---|
| **TİTCK MCP** | TR beşeri tıbbi ürün kanonik dataset (master records, holders, ATC/SNOMED, fiyat, biyobenzer grup, off-label, Madde 23, withdrawal, batch release, supply tracking, additional monitoring, foreign ingredients) | 56 | ✅ Aktif |
| **Türk Patent MCP** | TÜRKPATENT — patent + marka + endüstriyel tasarım | 6 | ✅ Aktif |
| **Mevzuat MCP** | mevzuat.gov.tr — A. Arama (3 araç: full-text + fihrist + mülga), B. Detay erişim (4 araç: ham dosya + HTML + meta + PDF→text), C. Tarih (1 araç: önceki versiyonlar), D. Listeleme/Referans (2 araç: tür listesi + tür kodları), E. Kompozit/Özel (2 araç: semantik kanıt paketi + 1982 Anayasası) | 12 | ✅ Aktif (v2.0.2) |

**Doktrin** (zorunlu okuma `references/turk-mcp-entegrasyonu.md`):

1. **Kanonik kaynak öncelik sırası**: MCP > resmi kurum web sitesi (kazıma yerine) > akademik literatür > sektör basını.
2. **Web fetch ne zaman**: (a) MCP timeout/5xx audit-trail yedeği, (b) gerçek-zamanlı haber/duyuru, (c) MCP envanteri kapsamı dışı içerik. Türkiye veri akışı v2.0.1 itibarıyla **tam MCP-first**; web fetch artık birincil değil.
3. **Provenance damgası**: Her TR veri noktası için `[Kaynak MCP / Tool / Erişim tarihi]` formatında ek; örneğin `[TİTCK MCP / get_price_history / 2026-05-01]` veya `[Mevzuat MCP / search_legislation / SMK 6769 / 2026-05-01]`.
4. **Holder normalizasyonu zorunlu**: Holder adı verildiğinde önce `find_holder_by_alias` + `list_holder_aliases` ile kanonik `holder::id`'ye çözümle; ham string ile karşılaştırma yapma.
5. **SNOMED CT atomu**: Etkin madde tabanlı analizler (eşdeğerlik, biyobenzer küme, off-label genişlemesi) **sadece `master::barcode → SNOMED concept`** bağı üzerinden yapılır; INN string match'i yetersiz.
6. **FTS5 smart-mode varsayılan**: TİTCK arama araçlarında `query_mode='smart'` kullan (FTS5 sözdizimini otomatik algılar). Yalnız özel bir Boolean ifadeyi ham geçirmek istiyorsan `query_mode='raw'`.

### 5.6. AI / NLP katmanı

Son dönem çalışmalar BERT tabanlı sınıflayıcıların USPTO verisinde kimyasal ilaç patentlerini %94.4 doğrulukla ayırt edebildiğini ve regülatör onayından **on yıl öncesine varan erken saptama** sağladığını göstermiştir. Bu tür sistemler landscape modunda erken uyarı aracı olarak kullanılır; ancak saptama ≠ hukuki değerlendirme, her öngörü insan eliyle doğrulanır.

## 6. Composability — Diğer Skill'lerle ve MCP'lerle Entegrasyon

### 6.1. Diğer skill'ler ile

Bu skill izole değil; Mahir'in skill ekosistemiyle aşağıdaki akışlarda eşleşir:

| Upstream (önce çalışır) | pharmapatent (bu skill) | Downstream (sonra çalışır) |
|---|---|---|
| `medsearch` — prior art için hakemli literatür, klinik kanıt sentezi | Mod 2 Invalidity, Mod 3 Landscape | `carbon-html-report` — FTO/Landscape raporu |
| `pharmaintel` — Orange/Purple Book, SEC 10-K, pipeline, katalizör takvimi | Mod 1 FTO, Mod 3 Landscape, Mod 4 Lifecycle | `carbon-pptx` — yönetim kurulu briefing'i |
| `lex-mercator` — lisans / JV / tech-transfer sözleşmesi çerçevesi | Mod 4 Lifecycle, Mod 6 Litigation, Mod 10 Licensing | `docx` — dilekçe, savunma, delil tespiti talebi |
| — | Mod 5 Regulatory, **Mod 13 TR_REGULATORY_FLOW** | `onko-erisim` — LOE sonrası SUT/SGK geri ödeme dilekçesi |
| — | Mod 6 Litigation | `carbon-html-report` — mahkeme brifingi |

Composability zincirleri için gerektiğinde açıkça belirtin: "Bu FTO raporu için önce `pharmaintel` ile Orange Book tarayacağım, sonra `pharmapatent` Mod 13 ile TİTCK MCP üzerinden TR ürün kartını çıkaracağım, sonra Mod 1 FTO'yu çalıştıracağım."

### 6.2. MCP konnektörleri ile (v2.0.0)

Skill, üç Türk regülatör MCP'sini doğrudan tüketir. Detaylar `references/turk-mcp-entegrasyonu.md`:

| MCP | Hangi modlarda zorunlu | Hangi modlarda opsiyonel | Notlar |
|---|---|---|---|
| **TİTCK MCP** | Mod 5 Regulatory · Mod 9 Biosimilar · **Mod 13 TR_REGULATORY_FLOW** | Mod 1 FTO · Mod 4 Lifecycle · Mod 7 DD · Mod 10 Licensing · Mod 12 Expert Witness | 56 araç. Holder normalizasyonu + SNOMED bağı zorunlu kullanım kuralı |
| **Türk Patent MCP** | Mod 1 FTO · Mod 4 Lifecycle · **Mod 13 TR_REGULATORY_FLOW** | Mod 2 Invalidity · Mod 3 Landscape · Mod 6 Litigation · Mod 7 DD · Mod 12 Expert Witness | 6 araç. CPC/IPC + applicant + abstract anahtar kelime arama |
| **Mevzuat MCP** | Mod 5 Regulatory · Mod 6 Litigation · **Mod 13 TR_REGULATORY_FLOW** | Mod 2 Invalidity · Mod 7 DD · Mod 12 Expert Witness | 12 araç (v2.0.1 aktif). SMK + yönetmelik + tebliğ + genelge + Resmi Gazete tam metin. İçtihat (Yargıtay/Danıştay/AYM) MCP kapsamı dışı; o katman için `karararama.yargitay.gov.tr` web fetch yedeği kalır |

**Üst-düzey orkestrasyon**: TR-merkezli her sorgu **Mod 13'ten başlar** (TİTCK + Türk Patent kanonik dosya), **sonra ilgili modlara genişler** (FTO için Mod 1, Pazara giriş için Mod 5, biyobenzer için Mod 9, dava için Mod 6). Skill, kullanıcı açıkça başka mod istemediği sürece bu varsayılan zinciri uygular.

## 7. Çıktı Disiplini

Tüm çıktılarda uygulanır:

1. **Kaynak provenansı** — Her iddia için (patent numarası + paragraf/istem, mevzuat maddesi, Yargıtay karar numarası + tarih, veri tabanı + erişim tarihi) tam atıf.
2. **Epistemik sınırlar** — Ulaşılamayan veri, dil sınırı, paywall engeli, terk edilmiş başvuru statüsü belirsizliği açıkça beyan edilir.
3. **Güvenilirlik derecesi** — Her argümana Strong / Moderate / Weak / Speculative etiketi.
4. **Tarih hassasiyeti** — Öncelik tarihi, başvuru tarihi, yayın tarihi, granted tarihi, expiry tarihi ayırt edilir; "patent bitti" gibi muğlak ifadeler kullanılmaz.
5. **Coğrafi netlik** — Patent ulusaldır; "TR'de bitti, ABD'de aktif, EP'de muhalefet sürüyor" tarzı ülke-bazlı çözünürlük.
6. **Türkçe-İngilizce paralel terminoloji** — "istem (claim)", "önceki teknik (prior art)", "buluş basamağı (inventive step)", "ex tunc etki (geçmişe dönük iptal)" şeklinde çift-dilli anahtar terimler.
7. **Hukuki sorumluluk notu** — Rapor bilgilendirme amaçlıdır, spesifik dava için vekillik ilişkisi kurulmadan nihai görüş oluşturulamaz.

## 8. Reference Dosyaları

Progressive disclosure yapısında, talebin modu ve derinliğine göre yüklenir:

- **`references/cpc-ipc-kodlari.md`** — Farmasötik ve tıbbi cihaz CPC/IPC taksonomisi; A61K (preparatlar) tam alt-ağacı, A61M/A61B, B01D, C07D/C07K, C12N hiyerarşileri; sınıf bazlı Boolean sorgu örnekleri; TÜRKPATENT 2024 Nice güncellemesi 09./39./44. sınıf etkileşimi.

- **`references/markush-protokol.md`** — Markush yapısı tarihçesi (Eugene Markush 1924), dört varyasyon tipi (sübstitüsyon / pozisyonel / frekans / homoloji) detayı, jenerik düğüm sözlüğü (A/Q/M/X/Ak/Cb/Cy/Hy/ARY/HET/CHK), CAS IP Finder & STN IP Protection Suite Markush sorgu protokolü, ücretsiz alternatiflerin (Espacenet smart search, USPTO Patent Public Search) sınırlılığı, örnek case study'ler.

- **`references/veritabani-stratejileri.md`** — Orange Book (FDA referans listeleri, pediatrik uzatma, patent delisting), Purple Book (biyolojikler, BsUFA), Espacenet (akıllı arama + INPADOC family), USPTO Patent Public Search (.CPC. saha sintaksı), TÜRKPATENT EPAAT (başvuru/tescil/yıllık harç sorgu), WIPO PATENTSCOPE (PCT ulusal faz), STN SciFinder (kimyasal alt-yapı), Boolean operatör farkları, sık-yapılan-hatalar listesi.

- **`references/smk-6769-ilac.md`** — SMK 6769'un ilaç-ilgili maddeleri (m. 82 patent verilebilirlik, m. 83 yenilik/buluş basamağı, m. 85 hak, m. 85/3 Bolar istisnası, m. 91 bölünmüş başvuru, m. 92 koruma kapsamı, m. 99 kısmi hükümsüzlük, m. 129 zorunlu lisans, m. 138 geçersizlik davası, m. 141-149 tecavüz ve yaptırımlar, m. 159 ihtiyati tedbir), 566 KHK tarihsel geçişi, Gümrük Birliği 1/95, TRIPS m. 27 + m. 31, Doha Deklarasyonu, 6471 sayılı TRIPS protokolü.

- **`references/ruhsat-veri-imtiyazi.md`** — Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği (2005 + 2022 revizyonu), TİTCK prosedürleri, kısaltılmış başvuru, 6 yıllık veri imtiyazı hesap metodolojisi (Gümrük Birliği alanı ilk ruhsat tarihi referansı), pediatrik uzatma, orphan drug rejimi, referans fiyatlandırma (Fransa/İtalya/İspanya/Portekiz/Yunanistan en düşük depocu satış fiyatı), SGK Geri Ödeme Komisyonu, Bolar istisnası içtihadı.

- **`references/tibbi-cihaz-uts.md`** — Tıbbi Cihaz Yönetmeliği (MDR uyumlu), Ürün Takip Sistemi (ÜTS), CE sınıflandırması (I/IIa/IIb/III), ISO 13485 kalite yönetim sistemi, kombinasyon ürünler ikili rejim, TÜRKPATENT 2024 Nice 09./39./44. sınıf güncellemesi (yapay zeka teşhis robotları, sağlık turizmi, diş hekimliği, psikolog hizmetleri).

- **`references/ictihat-emsal.md`** — Yargıtay 11. HD ilaç patenti kararları, Yargıtay HGK ikinci tıbbi kullanım içtihadı, FSHHM ihtiyati tedbir pratiği, Danıştay TÜRKPATENT YİDK iptal kararları, AYM sağlık hakkı + mülkiyet hakkı dengesi, EPO Board of Appeal paralel içtihadı; UYAP Mevzuat ve Yargıtay Bilgi Sistemi üzerinde verimli sorgu teknikleri.

- **`references/fto-invalidity-protokol.md`** — FTO araştırma tam iş akışı (9-adım), Invalidity araştırma tam iş akışı (11-adım), her adımda kullanılacak veri tabanı + sorgu örneği; özellik-özellik analiz matrisi; mozaik tablosu şablonu; karar ağacı; sık-düşülen-tuzaklar listesi.

- **`references/rapor-sablonlari.md`** — 9 çalışma modu için çıktı şablonları: §1 FTO Raporu, §2 Invalidity Briefing, §3 Landscape Raporu, §4 Lifecycle Yol Haritası, §5 Pazara Giriş Takvimi, §6 Litigation Briefing, **§7 Due Diligence Report (v1.2.0)**, **§8 Opposition Briefing (v1.2.0)**, **§9 Biosimilar Pathway Briefing (v1.2.0)**. Her şablon Carbon HTML ve docx uyumlu yapıdadır. **v1.1.0**: Hedef Kitle Varyasyonları (Technical / Executive / Legal) ve Filled Examples bölümleri eklendi.

- **`references/patent-degerleme.md`** [v1.2.0] — Farmasötik patent değerleme metodolojileri: Cost / Market / Income yaklaşımları, DCF + rNPV + Monte Carlo uygulaması, Relief-from-Royalty (RFR), comparable transactions, modalite-spesifik royalty stack, biyolojikler vs küçük molekül farklılıkları, portföy sinerjisi, vergi + Türkiye Ar-Ge teşvikleri + patent box rejimi, dava tazminat hesaplama (SMK m. 151), IVS 210 raporlama standardı.

- **`references/biyobenzer-yol.md`** [v1.2.0] — Biyobenzer geliştirme tam rehberi: jenerik vs biyobenzer yapısal fark, Critical Quality Attributes (CQA), analitik + nonklinik + klinik karşılaştırılabilirlik paketi, AB EMA (Article 10(4)) + ABD FDA (BPCIA 351(k)) + Türkiye TİTCK düzenleyici rejimleri, veri imtiyazı (AB 8+2+1, ABD 12 yıl, TR 6 yıl), extrapolation doktrini, interchangeability (ABD vs AB vs TR), patent dance (BPCIA §262(l)), pazar dinamikleri + fiyat erozyonu, biyobenzer-spesifik IP stratejileri.

- **`references/yeni-modaliteler.md`** [v1.2.0] — Yeni modaliteler için modalite-spesifik patent protokolü: ADC (antikor + linker + payload üç patent ailesi), CAR-T (T-hücre + CAR konstrüktü + platform patentleri), mRNA-LNP (Acuitas + Alnylam LNP royalty stack), siRNA / ASO (sekans + konjugasyon), gene therapy (AAV serotipi + lentiviral), xenotransplantation, AI diagnostics / SaMD. Her modalite için CPC kodları, FTO stratejisi, invalidity fırsatları, regülatör kesişim, değerleme çarpanları.

- **`references/gorsel-standartlari.md`** [v1.3.0] — Rapor şablonları için zorunlu görsel setleri: 9 şablonun her biri için spesifik görseller (Gantt, heatmap, choropleth, citation network, karar ağacı, Monte Carlo dağılımı, tornado chart), IBM Carbon uyumlu renk paleti + tipografi, SVG standart boyutları (inline/HTML/PPTX/docx), Mermaid + visualize:show_widget + D3.js üretim araçları seçim rehberi, accessibility (WCAG AA) + print-safe kurallar.

- **`references/compliance-beyanlari.md`** [v1.3.0] — Farmasötik raporlarda zorunlu compliance beyanları: GPP3 (Good Publication Practice), MDR/IVDR (tıbbi cihaz bağlantılı), KVKK (6698 sayılı Kanun) + GDPR (EU 2016/679) veri koruma, avukat-müvekkil ayrıcalığı (Av.K m.36 + HMK m.219/3) + work product doctrine, GCP (ICH E6), FCPA/UK Bribery Act/5607 anti-bribery, çıkar çatışması beyanları. Her rapor tipi için compliance beyan matrisi + hazır şablon metinler.

- **`references/turk-mcp-entegrasyonu.md`** [v2.0.1] — **Türk Regülatör MCP-First birleşik rehberi**. Üç MCP envanteri (TİTCK 56 araç + Türk Patent 6 araç + Mevzuat 12 araç — üçü de aktif), her aracın çağrı imzası, parametre sözleşmeleri, dönüş şekilleri, Mod 13 TR_REGULATORY_FLOW akış diyagramı, holder normalizasyon paterni, SNOMED CT atomu kullanımı, FTS5 smart-mode/raw-mode kararı, fiyat zinciri çıkarımı, biyobenzer grup tespiti, off-label katmanı, Madde 23 takibi, Türk Patent + TİTCK + Mevzuat çapraz-doğrulama tarifi, MCP başarısızlık durumlarında audit trail kurma, content-negotiation post-mortem (v2.0.0 → v2.0.1 lessons learned), provenance damgası standardı.

- **`references/visualize-widget-kutuphanesi.md`** [v1.5.0] — `visualize:show_widget` tool'u için IBM Carbon Design System renk paleti + IBM Plex tipografi uyumlu 33 hazır SVG/Mermaid/HTML şablonu: §1 FTO (patent×ülke heatmap, özellik matrisi, design-around tree, LOE Gantt) · §2 Invalidity (mozaik, radar, citation network, forum tree) · §3 Landscape (filing trend, assignee bar, choropleth, evergreening timeline) · §4 Lifecycle (Gantt, erosion curve, quadrant) · §5 Pazara giriş (LOE Gantt, MAX formula viz) · §6 Litigation (decision tree, cost curve, forum matrix) · §7 DD (coverage heatmap, radar, Monte Carlo, tornado) · §8 Opposition (EPC Art.100 map, problem-solution, Gantt) · §9 Biosimilar (multi-Gantt, sankey, market share, launch calendar) · §10 Expert Witness (feature matrix, verdict summary). Her şablon placeholder sözleşmesi ile hazır.

### 8.0. Domain Derinlikleri (v1.4.0)

Terapötik alan-spesifik IP rehberleri — Mahir'in uzmanlık alanlarına odaklıdır. Mod seçimi sonrası (FTO / Invalidity / Landscape / Licensing / DD) ilgili domain dosyası okunmalı; terapötik alana özgü hedef, modalite, pazar dinamikleri, Türkiye erişim özellikleri ve KOL ağı haritası buradadır.

- **`domains/onkoloji-ip.md`** [v1.4.0] — Onkoloji IP derinlik: ICI (pembrolizumab, nivolumab, atezolizumab, LAG-3), targeted therapy (TKI + mAb), ADC (T-DXd, Enhertu, Trodelvy, Padcev, Elahere), CAR-T otologous + allogeneic, bispecifics (CD20×CD3, BCMA×CD3, GPRC5D×CD3, EGFR×MET, PD-1×CTLA-4, PD-1×VEGF), radioligand therapy (Lutathera, Pluvicto, Xofigo), biyobenzer onkoloji dalgası (trastuzumab/rituksimab/bevacizumab 2024), Türkiye SGK onkoloji erişim hiyerarşisi, Yargıtay + AYM onkoloji davaları, ctDNA + liquid biopsy + neoantigen vaccines + AI-driven discovery.

- **`domains/hematoloji-ip.md`** [v1.4.0] — Hematoloji IP derinlik (Mahir'in doğrudan rol alanı): malign hematoloji (AML/ALL/KML/KLL/DLBCL/FL/MCL/HL/MM/MDS/MF), CAR-T hematoloji (Kymriah/Yescarta/Tecartus/Breyanzi/Abecma/Carvykti), bispecific detay (blinatumomab, mosunetuzumab, **glofitamab**, epcoritamab, teclistamab, elranatamab, talquetamab), hemofili (emicizumab + gene therapy Roctavian/Hemgenix/Beqvez), SCD + β-talasemi (Casgevy CRISPR + Lyfgenia lentiviral), nadir hematoloji (PNH + aHUS + ITP + TTP), DOAC + Factor XI inhibitörleri, Türkiye hematoloji erişim + SGK + AYM davaları, Roche Türkiye malignant hematology entegrasyonu.

- **`domains/immunoloji-ip.md`** [v1.5.0] — İmmunoloji / otoimmün IP derinlik: TNF-α inhibitörleri + adalimumab biyobenzer dalgası (Humira citrate-free 2023 sonrası), IL-17 (secukinumab/bimekizumab), IL-23 (ustekinumab + Wezlana biyobenzer 2024, risankizumab, guselkumab), IL-4/13 (dupilumab blockbuster), IL-6 (tocilizumab + biyobenzer), JAK inhibitörleri (tofacitinib/baricitinib/upadacitinib) + FDA Box Warning etkisi, **TYK2 allosterik (deucravacitinib)** yeni sınıf, B-cell (ocrelizumab MS), S1P modülatörleri, atopik hastalıklar, transplantasyon immünolojisi, Türkiye immunoloji erişim + step therapy, emerging TL1A + oral bispecifics (JNJ-2113).

- **`domains/noroloji-ip.md`** [v1.5.0] — Nöroloji IP derinlik: MS biyolojik devrim (**ocrelizumab Roche blockbuster** + BTK inhibitörleri), **Alzheimer anti-amiloid dalgası (Leqembi 2023 + Kisunla 2024)** + ARIA güvenlik + Türkiye erişim belirsizliği, Parkinson gene therapy (PR001/AAV-GBA1) + α-synuclein başarısızlık kümesi, ALS/SMA (Zolgensma $2.1M + Spinraza + Risdiplam) + DMD Elevidys, migren CGRP mAb + gepant pazarı, epilepsi + nöropati yeni mekanizmalar, nöropsikiyatri M1/M4 (Cobenfy), nadir CNS (NMOSD + MG), Türkiye AYM SMA davaları, emerging tau + BBB delivery platforms (Denali TV, JCR J-Brain Cargo).

- **`domains/enfeksiyon-ip.md`** [v1.5.0] — Enfeksiyon hastalıkları IP derinlik: antibiyotik krizi (PASTEUR Act + AMR Action Fund + GARDP), yeni nesil antibiyotikler (cefiderocol + tebipenem + zoliflodacin), HIV (Gilead Biktarvy + **lenacapavir PURPOSE-1 PrEP**), HCV post-Sovaldi konsolidasyon + Türkiye HCV eliminasyon, HBV kür pipeline (bepirovirsen + VIR-2218 + siRNA), COVID antivirallar (Paxlovid + molnupiravir) + RSV yeni dalgası (Beyfortus + Arexvy + Abrysvo + mRESVIA), antifungal Candida auris yeni sınıflar (olorofim + fosmanogepix), **mRNA aşı platformu devrimi** + LNP IP thicket (Acuitas + Alnylam), tropikal (malaria R21/Matrix-M + TB BPaL), emerging faj tedavi + ABC + pandemic preparedness.

- **`domains/kardiyoloji-ip.md`** [v1.6.0] — Kardiyoloji IP derinlik: post-statin era + PCSK9 mAb (evolocumab + alirocumab) + **inclisiran siRNA (Leqvio)** + Lp(a) pipeline (pelacarsen + olpasiran), **Factor XI antikoagülan devrimi** (abelacimab AZALEA-TIMI 71 pozitif + asundexian OCEANIC-AF başarısız 2023 + milvexian), DOAC cross-ref, SGLT-2 CVD outcome genişleme (dapagliflozin + empagliflozin HFrEF/HFpEF/CKD), GLP-1 RA CVD (SELECT semaglutide), ARNI (Entresto jenerik yakın), **ATTR amiloidoz** (tafamidis + patisiran + vutrisiran + acoramidis + NTLA-2001 CRISPR MAGNITUDE), PAH (sotatercept 2024 Winrevair), Türkiye SGK kardiyoloji, emerging **VERVE-102 PCSK9 in vivo base editing** + ziltivekimab anti-IL-6 CVD.

- **`domains/metabolik-ip.md`** [v1.6.0] — Metabolik IP derinlik: T2DM (SGLT-2 + DPP-4 + insülin biyobenzer + metformin), **GLP-1 RA blockbuster pazarı** ($50B+ 2024 — Ozempic/Wegovy semaglutide Novo + Mounjaro/Zepbound tirzepatide Lilly), obezite (orforglipron oral küçük molekül + retatrutide triple agonist GIP/GLP-1/glucagon + CagriSema + bimagrumab muscle-sparing), **MASH ilk onay (Rezdiffra resmetirom 2024)** + FGF21 + lanifibranor Faz III, KOAH (dupilumab 2024 FDA + ensifentrine), T1D (teplizumab Tzield Sanofi), semaglutide patent 2032 + tirzepatide 2036 + cihaz patentleri, Türkiye metabolik erişim + off-label Ozempic obezite, emerging oral GLP-1 + siRNA metabolik (zilebesiran).

- **`domains/oftalmoloji-ip.md`** [v1.6.0] — Oftalmoloji IP derinlik: AMD anti-VEGF devrimi + **Roche Vabysmo (faricimab) bispesifik anti-VEGF + anti-Ang2 blockbuster ($3.5B 2024)**, ranibizumab biyobenzer dalgası (Byooviz + Cimerli + Ximluci + Yesafili + Pavblu), aflibercept biyobenzer 2024 başladı, **Eylea HD (8mg)** + high-dose formülasyon paradigma, **GA (Geographic Atrophy)** pazarı yeni (pegcetacoplan Syfovre + avacincaptad Izervay 2023 FDA + güvenlik sinyalleri), retinal gene therapy (Luxturna RPE65 + ADVM-022 + RGX-314 + 4D-150), kuru göz (Miebo + Tyrvaya), glokom (netarsudil + latanoprostene bunod), Türkiye SGK anti-VEGF tam geri ödeme, emerging tek-doz AAV anti-VEGF + complement inhibitörleri.

- **`domains/dermatoloji-ip.md`** [v1.6.0] — Dermatoloji IP derinlik: psöriazis + AD cross-ref to `immunoloji-ip.md`, topikal yeni sınıflar (tapinarof Vtama AhR + roflumilast Zoryve PDE4 + ruxolitinib Opzelura JAK), akne + rosacea (jenerik dominant + clascoterone Winlevi ilk topikal anti-androjen + Mahir'in ADACLIN Era Pharma regülatör defans bağlantısı), **alopesi areata JAK devrimi** (Olumiant + Litfulo + Leqselvi), **vitiligo (Opzelura 2022 ilk FDA)**, AK + BCC + SCC (tirbanibulin + hedgehog inhibitörleri vismodegib/sonidegib + cemiplimab), melanom cross-ref to `onkoloji-ip.md`, HS (adalimumab + secukinumab 2023 + bimekizumab 2024), CSU (remibrutinib BTK Faz III 2024 pozitif), onikomikoz, estetik (Botox + Daxxify uzun etkili).

- **`domains/psikiyatri-ip.md`** [v1.7.0] — Psikiyatri IP derinlik: **60 yıl sonra ilk yeni mekanizma — Cobenfy (xanomelin/trospium M1/M4 muskarinik, BMS/Karuna $14B akuisisyon)**, Caplyta (lumateperone, J&J $14.6B), emraclidine Cerevel AbbVie $8.7B — toplam $37B psikiyatri konsolidasyon 2023-2024. MDD hızlı etki devrimi (Spravato esketamine + Zurzuvae zuranolone + AXS-05 Auvelity + psilocybin Faz III), bipolar (Caplyta + Vraylar), **Alzheimer ajitasyonu ilk onay Rexulti 2023**, LAI 6-aylık aralık (Invega Hafyera), ADHD non-stimulant, **psikedelik rönesans** (MDMA-PTSD Lykos Faz III FDA CRL 2024 + psilocybin Compass Faz III TRD + 5-MeO-DMT), bağımlılık (GLP-1 RA off-label araştırma), Türkiye SGK + REMS + Schedule I.



### 8.1. Örnek Raporlar (v1.1.0)

Doldurulmuş referans raporlar — Claude, yeni bir rapor hazırlarken önce ilgili örneği okumalı; içerik + yapı + ton + derinlik kalıbını oradan çapalayıp hedef vakaya uyarlamalıdır:

- **`examples/fto-ornek-atorvastatin.md`** — Hipotetik atorvastatin 40mg tablet için tam FTO raporu; 18 aktif patent değerlendirmesi, Form IV kristal polimorfuna design-around önerisi, rezidüel risk beyanı.

- **`examples/invalidity-ornek-trastuzumab.md`** — Hipotetik trastuzumab liyofilize formülasyon patenti (EP2987654) için tam Invalidity Briefing; 3 atak vektörü (yenilik, buluş basamağı, yeterli açıklama), mozaik tablosu, FSHHM forum stratejisi.

- **`examples/regulatory-ornek-semaglutide.md`** — Hipotetik semaglutide biyobenzer için tam Pazara Giriş Takvimi; LOE formül uygulaması, cihaz patenti stratejisi (FlexTouch EP3456789), Bolar takvimi, üç ürün (Ozempic/Rybelsus/Wegovy) için ayrı hesap.

- **`examples/licensing-ornek-adc.md`** [v1.5.0] — Mod 10 Licensing için: Hipotetik anti-TROP2 ADC "BRX-202" Faz I in-licensing deal; 6 karşılaştırılabilir transaksiyon analizi, upfront $120M + milestone $1.5B + tiered royalty %10-12-14, NPV $1.1B licensee / $380M licensor, BATNA + ZOPA + anchor fiyatlama stratejisi, lex-mercator entegrasyon, Çin option müzakere hedefi.

- **`examples/opposition-ornek-epo.md`** [v1.5.0] — Mod 8 Opposition için: Hipotetik EP3456789 "Stabilized Concentrated Pembrolizumab Formulation" EPO opposition; 3 atak vektörü (yenilik — WO2017/054XX self-prior art STRONG, buluş basamağı problem-solution MOD-STRONG, added matter intermediate generalisation MOD), 9 aylık pencere hesabı (kalan 52 gün, filing deadline 2026-06-15), €75-225K maliyet projeksyonu, oral proceedings hazırlık.

- **`examples/landscape-ornek-adc-2030.md`** [v1.6.0] — Mod 11 Landscape Forecast için: ADC (Antibody-Drug Conjugates) solid tumor 2015-2024 retrospektif + 2025-2030 öngörü; CAGR %21.3, 8,450 patent kümülatif, BERT-tabanlı trend modeli (konservatif/baseline/agresif projeksyon), top 15 assignee (Daiichi Sankyo #1), **Çin %34 vs ABD %32** 2024'te ilk defa ön plana geçti, $30B+ Çin-Batı deal flow 2023-2024, **white space matrix** (hedef × payload): CLDN18.2 + CEACAM5 + CDH6 + MET yüksek fırsat, Roche ADC stratejisi + 3 öncelikli yatırım önerisi (CLDN18.2 in-license + Çin partnership + dual-payload platform).

- **`examples/ddreport-ornek-ma.md`** [v1.6.0] — Mod 7 M&A DD için: Hipotetik OncoGenesis Biotech anti-PSMA ADC (OG-PSMA-777) Faz II akuistisyon değerlendirmesi; $650M upfront + $400M CVR, NPV +$850M probability-weighted, 6 patent ailesi (expiry 2039-2043) + Seagen ADC platform lisans zorunluluğu, Faz II veri (PSA50 %48 + Grade 3+ neuropati %22 kırmızı bayrak), **Monte Carlo 10,000 sim** (P10 -$200M / P50 +$750M / P90 +$1.8B), **tornado duyarlılık** (peak sales dominant), 7 stratejik kırmızı çizgi + 24 haftalık müzakere takvimi, Pluvicto + 4 aktif anti-PSMA ADC Faz III rekabet.

- **`examples/showcase/pharmapatent-showcase.jsx`** [v1.6.0] — React interactive showcase artifact. IBM Carbon Design System + IBM Plex tipografi ile 6 sekmeli etkileşimli gösterge paneli: Genel Bakış (8 stat + 4-katmanlı mimari) · 12 Operasyonel Mod (detay paneli ile) · 9 Terapötik Alan · 10 Python Script · 33 Görsel Şablonu · Bilgi Grafı Centrality. Bağımsız React .jsx dosyası, lucide-react bağımlılığı, Claude artifact olarak veya standalone React projesinde kullanılabilir. Skill ekosisteminin canlı dokümantasyonu + iç eğitim aracı.

- **`examples/litigation-ornek-fshhm.md`** [v1.7.0] — Mod 6 Litigation için: Hipotetik Novo Nordisk vs [Jenerik Firma] **SEMARA® 1mg** semaglutide patent ihlali davası (İstanbul 2. FSHHM 2026/XXX E.). EP2059533 T3 İstem 1 analizi + İstem-özellik matrisi (F1-F5 literal/doktrinel eşdeğer), **HMK m. 389 ihtiyati tedbir %55-65 başarı**, paralel YİDK hükümsüzlük, İstanbul vs Ankara FSHHM forum karşılaştırması, **SMK m. 151 tazminat hesabı 3 alternatif** (davacı kâr kaybı ₺37.5M/yıl × 5 yıl = ₺187M / davalı kâr ₺60-80M / makul royalty %10 ₺30M), 4 settlement seçeneği (lisans / gecikmeli giriş / pazar paylaşımı / patent challenge anlaşması), 45 aylık takvim + ₺12-22M maliyet her iki taraf için.

- **`examples/showcase/monte-carlo-widget.md`** [v1.7.0] — Interactive HTML Monte Carlo NPV simulator widget. M&A DD + Licensing toplantılarında müvekkil ile canlı NPV dağılımı tartışması için. 6 slider (peak sales $500M-$5B, Faz II/III PTRS 20-95%, discount rate 8-20%, launch gecikme 0-4 yıl, patent challenge 0-50%). Real-time histogram (kırmızı negatif / mavi pozitif NPV) + P10/P50/P90 + Expected NPV + Pozitif NPV %. 10,000 simülasyon canvas rendering. `royalty-calculator.py --montecarlo` modunun web-interactive sürümü, `visualize:show_widget` HTML mode ile render edilir.

### 8.2. Yürütülebilir Araçlar (v1.1.0 / v1.3.0 / v1.4.0)

Python CLI tools — hızlı hesaplamalar ve tekrarlanabilir analizler için:

- **`scripts/loe-calculator.py`** [v1.1.0] — Patent + veri imtiyazı MAX formülü ile LOE tarihi hesaplar. Patent/veri imtiyazı engeli birbirinden ayırır; Bolar istisnası kapsamında biyoeşdeğerlik başlama önerisi verir; praktik pazara arz tarihi (ruhsat + fiyat + SGK) hesaplar.

- **`scripts/claim-parser.py`** [v1.1.0] — Bağımsız istem metnini otomatik olarak özelliklere ayrıştırır (F1, F2, ...). Her özelliğin kategorisini tahmin eder (aktif madde / eksipiyan / fiziksel form / konsantrasyon aralığı / pH / proses / kullanım / cihaz / stabilite). FTO veya Invalidity özellik-özellik matris şablonu üretir.

- **`scripts/royalty-calculator.py`** [v1.3.0] — Lisans anlaşması finansal modelleme: upfront + milestone + tiered royalty üzerinden NPV, IRR (Newton-Raphson bisection), Relief-from-Royalty (RFR), discount rate duyarlılık analizi, sektörel benchmark karşılaştırması. 7 modalite-spesifik benchmark kategorisi (small_molecule_onco_P3, mab_P3, adc_P2, car_t_P2, mrna_lnp_preclinical, gene_therapy_P1, platform_preclinical). SMK m. 151 dava tazminat için RFR modu.

- **`scripts/patent-expiry-monitor.py`** [v1.3.0] — Portföy takip monitörü: yıllık harç + expiry için otomatik uyarı üretir. 4-seviye öncelik (critical 7/30 gün, high 30/90, medium 60/180, low 90/365). Kaçırılmış harçlar için 180 günlük recovery penceresi uyarısı. CSV/JSON import + markdown/JSON export. Büyük portföyler (50+ patent) için uygun.

- **`scripts/cpc-recommender.py`** [v1.4.0] — Molekül/cihaz profilinden CPC (Cooperative Patent Classification) ve IPC kodu önerisi. Modalite (small_molecule / antibody / ADC / CAR-T / mRNA / gene_therapy / radioligand / device) + endikasyon + hedef + dozaj formu + cihaz komponenti + özel özellikler (bispecific, nanoparticle, AI) girdisine göre primary + secondary CPC kodları üretir; USPTO ve Espacenet formatında Boolean sorgu örnekleri hazırlar.

- **`scripts/family-tracer.py`** [v1.4.0] — INPADOC-style patent ailesi haritalama + coverage analizi. Priority date bazlı aile birleştirme; jurisdiction başına granted/pending/abandoned/lapsed/revoked durum takibi; hedef ülke listesine karşı coverage gap tespiti; Mermaid flowchart diyagramı + markdown coverage matrisi + JSON yapısal çıktı üretimi. CSV import destekler.

- **`scripts/priority-date-matrix.py`** [v1.4.0] — Portföy priority date uyumluluk analizi. Paris Convention 12 aylık priority period testi, PCT 30 aylık ulusal faz deadline testi, aile priority date tutarlılık testi, prior art arama kesim tarihi matrisi. 4-kategori check (pass / warning / fail / skip) sonuçlar. Invalidity araştırmasının tarihsel sınırlarını belirler.

- **`scripts/spc-calculator.py`** [v1.5.0] — AB Supplementary Protection Certificate (SPC) süre hesaplayıcı. Regulation (EC) No 469/2009 Art. 13 formülüne göre SPC süresi (max 5 yıl + 6 ay pediatric extension), SPC eligibility testi, market exclusivity tavanı (ilk ruhsat + 15 yıl), Türkiye karşılaştırması (SPC TR'de YOK — sadece 20 yıl patent + 6 yıl veri imtiyazı). 6 hipotetik örnek (Keytruda, Sovaldi, Ozempic, Enhertu, Xtandi, fast approval). `--compare-tr` modu tüm ürünlerin AB vs TR koruma farkı tablosu.

- **`scripts/report-builder.py`** [v1.6.0] — Rapor otomasyon orkestratörü: `rapor-sablonlari.md` (11 rapor tipi) + `visualize-widget-kutuphanesi.md` (33 görsel şablonu) + `carbon-html-report` skill entegrasyonu. Her rapor tipi için: iskelet bölümler + zorunlu görsel yer tutucular + compliance bloğu + hedef kitle varyantı + ilgili script işaretleyicileri. 11 rapor tipi: fto, invalidity, landscape, lifecycle, regulatory, litigation, dd, opposition, biosimilar, licensing, expert_witness. `--list-types` ile mevcut rapor tipleri tablosu; `--type X --asset Y --out Z.md` ile iskelet üretim.

- **`scripts/biosimilar-comparator.py`** [v1.6.0] — Biyobenzer CQA (Critical Quality Attributes) benzerlik skorlama — ICH Q5E + FDA + EMA Biosimilar Guidance uyumlu. 3 tier sistemi (Critical ≥0.85, Important ≥0.70, Minor ≥0.50) + 4 similarity band (Highly Similar / Similar / Trend / Not Similar). 5 CQA kategorisi (structural, functional, process, product, PK/PD). Tier-ağırlıklı overall skor + verdict (PASS/CONDITIONAL/FAIL). 3 hipotetik örnek: trastuzumab (PASS), adalimumab (PASS), ranibizumab_fail (FAIL demo).

- **`scripts/fto-grid.py`** [v1.7.0] — Çoklu patent × çoklu ülke × çoklu ürün FTO risk matrisi otomasyonu. 5 statü (Clean / Caution / Blocker / N/A / Expired) + her hücre için gerekçe. Özet tablo (statü dağılım + ülke blocker yoğunluk + ürün bazlı blocker listesi). Markdown + JSON çıktı. 3 örnek: HCV DAA (Sofosbuvir + kombi, 30 değerlendirme), obezite (Semaglutide + Tirzepatide 50 değerlendirme), Humira biyobenzer (12 değerlendirme). Mod 1 FTO raporu iskeleti için birincil veri kaynağı.

- **`scripts/regulatory-timeline.py`** [v1.7.0] — Ruhsat + SGK + Bolar tam takvim otomasyonu. 3 ürün tipi (innovative 12 yıl / biosimilar 8 yıl / generic 2 yıl). 11-aşama inovatif TR yol haritası (CMC → Faz I/II/III → TİTCK başvuru 6ay → TİTCK değerlendirme 10ay → Ruhsat → SGK Ödeme Komisyonu 8ay → SUT listesi → satışa arz → hastane ihale). Bolar overlap hesabı (SMK m.85/3). 4 format: ASCII Gantt + Markdown table + Mermaid Gantt + JSON.

- **`scripts/kol-graph.py`** [v1.7.0] — KOL + klinik araştırmacı network grafiği. Düğümler (KOL + merkez + şehir + uzmanlık + aktif trial + yayın sayısı), kenarlar (co_author / co_pi / steering_committee / advisory_board / same_center) ağırlıklı. Weighted centrality (kenar tipi ağırlığı + trial bonus + yayın bonus). 3 örnek: Türkiye MS KOL (8 düğüm, 14 kenar), Türkiye Onkoloji KOL (8+14), Global GLP-1 investigators (6+8). Mermaid flowchart + Markdown centrality tablosu + JSON. Nexopharos OSINT sürecinin otomasyonu.

- **`scripts/evidence-ranker.py`** [v1.7.0] — GRADE + Oxford CEBM 2011 kanıt seviyesi otomatik sınıflandırma. 15 çalışma tasarımı enum + baseline GRADE (RCT=HIGH, cohort=LOW, case series=VERY LOW). 5 downgrade (RoB, inconsistency, indirectness, imprecision, publication bias) + 3 upgrade (large effect, dose-response, plausible confounders reduce — sadece observasyonel için). Otomatik final GRADE hesabı. 6 hipotetik örnek: KEYNOTE-189 (HIGH), CheckMate-067 (MODERATE), dapagliflozin kohort (LOW→MODERATE), lecanemab case series (VERY LOW), Cochrane CAR-T (MODERATE), AZALEA-TIMI 71 Factor XI (MODERATE).

- **`scripts/patent-language-translator.py`** [v1.8.0] — Patent istem teknik-legal dilinin operasyonel dile çevrimi. Kural-tabanlı NLP (regex + lemma + farmasötik terim sözlüğü 40+ kısaltma). Preamble / transition / body ayrıştırması; open/closed/intermediate transition scope; Markush grup üyesi çıkarımı; 9 özellik kategorisi (aktif madde / eksipiyan / fiziksel form / konsantrasyon / pH / proses / kullanım / cihaz / stabilite); her özellik için **3 çıktı: (1) sade Türkçe plain**, **(2) ihlal testi sorusu**, **(3) design-around ipucu**. 4 örnek: pembrolizumab formülasyon, semaglutide peptid+cihaz, statin Markush, ADC DAR+Markush payload.

- **`scripts/health-economics-qaly.py`** [v1.8.0] — QALY + ICER + HTA threshold değerlendirme. Intervention (cost_per_cycle × cycles + additional_costs) + HealthState (utility + duration) modeli. Incremental cost/QALY/LY + ICER + dominance analizi (dominant/dominated/trade-off/cost-saving/equivalent). **12 HTA threshold tablosu**: NICE standard £20-30K (+severity +EoL modifier), ICER $100-150K (+ultra-rare), WHO 1-3× GDP, Türkiye informal ₺500K, Germany IQWiG (relative benefit), France HAS (ASMR), China CDE ¥150-250K, Japan MHLW ¥5-7.5M. 3 örnek: pembrolizumab NSCLC (ICER $203K/QALY — NOT COST-EFFECTIVE), CAR-T DLBCL (ICER $53K — HIGHLY COST-EFFECTIVE), resmetirom MASH.

- **`scripts/realworld-evidence-harvester.py`** [v1.8.0] — RWE konsolidasyon orkestratörü. 13 kaynak kayıt (TR: SGK Medula + TİTCK Ruhsat + TR Kanser Kayıt + IMS Turkey; Global: FDA FAERS + EMA EudraVigilance + ClinicalTrials.gov + FiercePharma + Endpoints + Evaluate Pharma + PubMed + SEER + GARDP). RWEDataPoint yapısı (source/metric/value/date/note). Her paket için source directory + dağılım + gap analizi + şablon üretimi. 3 örnek: pembrolizumab-tr (15 veri noktası), **glofitamab-tr (Mahir'in Roche portföy bağlantısı, 9 veri noktası)**, semaglutide-global (14 veri noktası). `--template --product X --indication Y` ile yeni ürün için boş paket.

- **`scripts/compliance-checker.py`** [v1.8.0] — 7 compliance framework (**FCPA + UK Bribery Act 2010 + TR MASAK + KVKK/GDPR + EFPIA Code + IFPMA Code + Roche Group Audit internal**) otomatik uyum kontrolü. 4 senaryo evaluator (hcp_honorarium, advisory_board, clinical_investigator, patient_data_processing). Her senaryo için: framework-bazlı flag listesi (critical/high/medium/low/info) + bulgu + öneri + required approvals + applicable SOPs. Overall risk score 0-100 ağırlıklı. 6 örnek senaryo (risky + clean karşılaştırma): HCP honorarium risky (71/100 CRITICAL) vs clean (0/100 LOW), advisory board Bodrum resort vs İstanbul conference center, clinical investigator FMV benchmarking, patient data AB→TR transferi.

- **`scripts/README.md`** — Scripts kullanım kılavuzu, programatik kullanım örnekleri, roadmap.

## 9. Operasyonel Disiplin

- **Türkçe formel "siz" hitabı** — profesyonel ve akademik kayıt.
- **Multidisipliner derinlik** — salt hukuki değil; kimya, biyoteknoloji, farmakoloji, ruhsat mevzuatı, ticari strateji entegrasyonu.
- **Öncelik: birincil kaynak** — TÜRKPATENT, USPTO, EPO, FDA, EMA, resmi TİTCK belgeleri, Yargıtay Bilgi Sistemi. Sekonder kaynak (blog, IP yorum siteleri) ancak birincil desteği olmadığında ve bu açıkça beyan edilerek kullanılır.
- **TR-ekosistemde MCP-first (v2.0.1)** — Türkiye verilerinde **TİTCK MCP > Türk Patent MCP > Mevzuat MCP** üçlüsü web kazımanın yerine geçer ve üçü de aktiftir. Web fetch yalnızca (i) MCP timeout/5xx audit-trail yedeği, (ii) gerçek-zamanlı haber/duyuru, (iii) MCP envanteri kapsamı dışı içerik (örneğin Yargıtay/Danıştay içtihatı) için. Her TR veri noktasına `[Kaynak MCP / Tool / Erişim tarihi]` provenance damgası eklenir. Detay: `references/turk-mcp-entegrasyonu.md`.
- **Güncel mevzuat doğrulaması** — SMK ve yönetmeliklerin güncel metinleri her raporda Mevzuat MCP üzerinden teyit edilir (12 araç aktif). "Tarihte X'ti, güncel Y'dir" ayrımı mülga-versiyon karşılaştırma araçlarıyla netleştirilir.
- **Holder normalizasyonu (v2.0.0)** — Holder adı her raporda `find_holder_by_alias` + `list_holder_aliases` ile kanonik `holder::id`'ye çözülür; ham string ile rapor yazılmaz.
- **SNOMED CT atomu (v2.0.0)** — Etkin madde tabanlı analizler `master::barcode → SNOMED concept` bağı üzerinden yapılır; INN string match yetersiz, eşdeğerlik analizinde reddedilir.
- **Dava savunusu dili** — argümanlar mahkeme diline uyarlanabilir yoğunlukta ve hassasiyette üretilir.
- **Hiçbir nihai görüş uzman avukat onayı olmaksızın ticari karara bağlanmaz** — bu skill karar-destek sunar; nihai hukuki sorumluluk yetkili vekildedir.
- **Filled example öncelik kuralı (v1.1.0)** — Yeni bir rapor üretmeden önce `examples/` altında ilgili örnek okunmalıdır. Örnek, içerik + yapı + ton + derinlik için çapa işlevi görür.
- **Hedef kitle seçimi (v1.1.0)** — Her rapor hazırlığında Technical / Executive / Legal varyant açıkça seçilmeli; kapakta belirtilmeli.

## 10. Protokol Versiyonu

**v2.0.2** — 1 Mayıs 2026. **Patch — Mevzuat MCP envanteri tam tablolandı**:
- v2.0.1'de "PENDING discovery placeholder" olarak bırakılan 12 Mevzuat MCP aracı, kullanıcı tarafından sağlanan envanter ile **5 fonksiyonel kategoride** kesinleştirildi: A. Arama (mevzuat.gov.tr full-text + fihrist + mülga — 3 araç), B. Detay erişim (ham dosya + HTML + meta + PDF→text — 4 araç), C. Tarih (önceki versiyonlar — 1 araç), D. Listeleme/Referans (tür listele + tür kodları — 2 araç), E. Kompozit/Özel (semantik kanıt paketi + 1982 Anayasası — 2 araç).
- references/turk-mcp-entegrasyonu.md §4 tam yenilendi: §4.2 PENDING discovery placeholder kaldırıldı, **12-araç tam tablo** + 5 kullanım örüntüsü (madde getir / mülga karşılaştır / tebliğ ara / 1982 Anayasası özel sorgular / semantik agregat) yazıldı; §4.4 boş placeholder yerine canlı kategori-bazlı kullanım rehberi.
- SKILL.md §4 Mod 13 step 11 detaylandırıldı: 5 kategori + tipik kullanım kombinasyonları (A→B madde alıntısı, C versiyon karşılaştırma, A→B yönetmelik, E kompozit).
- SKILL.md §5.5 status tablosu Mevzuat satırı 5-kategori özeti ile zenginleştirildi.
- skill-manifest.yaml `mcp_connectors[mevzuat-mcp]` bölümüne `tools_inventory` alt-bloğu eklendi (12 araç, kategori, beklenen function name placeholder, açıklama).
- v2.0.1'in `inventory_discovery_pending` alanı kaldırıldı; envanter artık tam.
- **Açık ufak iş**: 12 aracın **kanonik snake_case function isimleri** (örn. `search_mevzuat`, `get_legislation_text`) Claude.ai connector index re-sync sonrası tool_search ile teyit edilince §4.2 tablosunda placeholder → kesin atom değişimi (kozmetik, davranış değişmeyecek).

**v2.0.1** — 1 Mayıs 2026. **Patch — Mevzuat MCP envanter teyidi**:
- Mevzuat MCP (`mevzuat-mcp-00017-668` Cloud Run revision) tam aktif: **12 araç** kullanıma hazır, `protocolVersion: 2024-11-05`.
- Kök sorun istemci uyumluluğuydu — tool registry değil. Public endpoint yetkisiz çağrılarda 401 dönüyordu (beklenen davranış); ancak Claude.ai gibi JSON-only `Accept: application/json` istemcilerine FastMCP varsayılan olarak 406 döndürüyordu (`Accept: text/event-stream` zorunluluğu). Sunucuya **JSON response modu** eklendi (`server.py:107`); regresyon testi (taze app helper + JSON-only initialize/tools/list testi) eklendi, **22 test passed**. MCP SDK sürümü 1.27.0 doğrulandı; stdio (`__main__.py:18`) vs HTTP (`http_app.py:545,547`) entrypoint ayrımı doğruydu, transport stdio değil streamable-http; Pydantic schema veya decorator düzeltmesi gerekmedi.
- Deploy sonrası public smoke testler net: OAuth discovery 200, yetkisiz mcp 401 challenge (doğru), JSON-only initialize 200 + tools/list 200 + tools_count 12 + tools_empty=false. `claude mcp list` çıktısında konnektör bağlı.
- SKILL.md güncellemeleri: §5.5 status tablosu Mevzuat ⏳→✅ + 12 araç; §6.2 composability matrisi Mevzuat optional→required (Mod 5/6/13); §4 Mod 13 step 11 PENDING dili kaldırıldı, kanonik MCP çağrıları yazıldı; §9 Operasyonel Disiplin geçici web yedeği kaldırıldı; frontmatter description Mevzuat (PENDING) → Mevzuat (12).
- references/turk-mcp-entegrasyonu.md §1.1 status, §4 Mevzuat MCP bölümü (PENDING blok yerine 12-araç envanter çerçevesi + content negotiation post-mortem), §5 akış diyagramı, §6 provenance, §7 tuzaklar (T-12 PENDING → T-12 content negotiation tuzağı/lessons learned), §8 end-to-end vaka Mevzuat çağrıları aktif yazıldı.
- references/ictihat-emsal.md §1 Mevzuat MCP bloku PENDING'den aktif duruma yükseltildi; UYAP içtihat aramasının Mevzuat MCP kapsamı dışı olduğu açıklığa kavuşturuldu.
- skill-manifest.yaml: version 2.0.0 → 2.0.1; mcp_connectors[mevzuat-mcp] status pending→active, tool_count 0→12, required_in_modes eklendi (Mod 5/6/13), fallback_protocol + inventory_completion_actions kaldırıldı; version_history v2.0.1 entry eklendi.
- **Açık iş**: 12 Mevzuat MCP aracının spesifik isimleri ve parametre şemaları, Claude.ai connector index re-sync sonrası `tool_search` ile keşfedilip `references/turk-mcp-entegrasyonu.md §4`'te tablolanacak (v2.0.2 patch). İçerikten bağımsız olarak doktrin ve mod-bazlı zorunluluklar bu sürümle kesinleşti.

**v2.0.0** — 1 Mayıs 2026. **Major sürüm — Türk Regülatör MCP-first içselleştirilmesi**:
- Yeni Mod 13: **TR_REGULATORY_FLOW** (Türk Regülatör + IP Akış Otomasyonu) — TİTCK MCP (56 araç) + Türk Patent MCP (6 araç) + Mevzuat MCP (PENDING) üçgenini orkestra eden 13-adımlı protokol. Diğer 12 modun TR-girdi katmanı; bağımsız da çalıştırılabilir.
- Yeni reference: `references/turk-mcp-entegrasyonu.md` — Üç MCP'nin birleşik rehberi: tool envanteri (TİTCK 56, Türk Patent 6, Mevzuat PENDING), parametre sözleşmeleri, dönüş şekilleri, holder normalizasyon paterni, SNOMED CT atomu, FTS5 smart-mode/raw-mode kararı, fiyat zinciri çıkarımı, biyobenzer grup tespiti, off-label katmanı, Madde 23 takibi, çapraz-doğrulama, Mevzuat geçici yedeği, audit-trail kurma.
- §5'e yeni alt-bölüm **§5.5 Türk Regülatör MCP-First Doktrini** eklendi (önceki §5.5 → §5.6 olarak kaymıştır).
- §6 Composability ikiye ayrıldı: §6.1 skill ekosistemi + §6.2 MCP konnektörleri; her MCP için zorunlu/opsiyonel mod matrisi tablolandı.
- Frontmatter description: 13 mod + MCP-first sinyalleri + TR ürün dosyası/eşdeğer grup/fiyat tavanı/holder portföyü/Madde 23 anahtar kelimeleri.
- §2 örtük tetikleyiciler: 11 yeni TR regülatör + MCP-first tetikleyici eklendi.
- §9 Operasyonel Disiplin: MCP-first kuralı + Holder normalizasyonu + SNOMED CT atomu zorunlu kuralları eklendi.
- skill-manifest.yaml: yeni `mcp_connectors` deklarasyonu (TİTCK + Türk Patent + Mevzuat); composability_chain TR-akış zinciri eklendi.
- Mevzuat MCP envanteri PENDING — Cloud Run deployment'da `tools/list` boş dönüyor (büyük olasılıkla `transport='streamable-http'` parametresi eksik veya FastMCP decorator'ları kayıt dışı). Envanter teyit edildiğinde `references/turk-mcp-entegrasyonu.md §4` doldurulacak; geçici yedek: `mevzuat.gov.tr` web fetch + tarih damgası.

**v1.8.0** — 24 Nisan 2026. Script ekosistemi zirvesi — 4 yeni çapraz-fonksiyonel araç:
- `scripts/patent-language-translator.py` — Patent istem teknik dilinin sade Türkçe + ihlal testi + design-around çıktısı (kural-tabanlı NLP, 40+ pharma terim sözlüğü, Markush çıkarımı, 9 kategori)
- `scripts/health-economics-qaly.py` — QALY + ICER + 12 HTA threshold (NICE + ICER + WHO + Türkiye informal + IQWiG + HAS + CDE + MHLW). 3 vaka (pembro NSCLC, CAR-T DLBCL, resmetirom MASH)
- `scripts/realworld-evidence-harvester.py` — 13 RWE kaynak (SGK Medula + IMS + FAERS + EudraVigilance + FiercePharma + Endpoints + Evaluate + PubMed vb.). 3 örnek paket — **glofitamab-tr Mahir Roche portföyüne doğrudan hitap**
- `scripts/compliance-checker.py` — **7 framework (FCPA + UKBA + MASAK + KVKK/GDPR + EFPIA + IFPMA + Roche Group Audit)** × 4 senaryo tipi. Risk skoru 0-100 + kırmızı bayrak listesi + required approvals + SOP referansları. Mahir'in Roche Türkiye Group Audit bağlamı
- Description güncellendi: QALY, ICER, HTA, RWE, FCPA, UKBA, MASAK, compliance anahtar kelimeleri
- Graph: hiçbir yeni domain/reference yok — sadece scripts ekosistemi genişledi

**v1.7.0** — 24 Nisan 2026. Büyük sürüm — domain + script ekosistemi tam olgunluk:
- 1 yeni domain derinlik dosyası: `domains/psikiyatri-ip.md` (**Cobenfy M1/M4 muskarinik 60 yıl sonra ilk yeni mekanizma**, Caplyta + emraclidine — toplam $37B psikiyatri konsolidasyon 2023-2024, hızlı etki MDD Spravato/Zurzuvae/AXS-05, **psikedelik rönesans MDMA-PTSD + psilocybin Faz III**, Alzheimer ajitasyonu Rexulti 2023, LAI 6-aylık, pediatrik ADHD + otizm, geriatrik, digital therapeutics, gene therapy CNS, neurosteroidler, TAAR1)
- 4 yeni operasyonel script:
  - `scripts/fto-grid.py` — Patent × ülke × ürün FTO risk matrisi (3 örnek: HCV, obezite, Humira biyobenzer)
  - `scripts/regulatory-timeline.py` — Ruhsat + SGK + Bolar Gantt (3 ürün tipi: innovative/biosimilar/generic)
  - `scripts/kol-graph.py` — KOL network + weighted centrality (3 örnek: TR MS, TR onkoloji, global GLP-1)
  - `scripts/evidence-ranker.py` — GRADE + Oxford CEBM otomatik sınıflandırma (6 örnek)
- 1 yeni filled example: `examples/litigation-ornek-fshhm.md` (Mod 6 — hipotetik Novo vs Jenerik semaglutide FSHHM davası + SMK m.151 tazminat hesabı + 4 settlement seçeneği)
- 1 yeni showcase artifact: `examples/showcase/monte-carlo-widget.md` (interactive HTML NPV simulator — 6 slider + real-time histogram + 10K simülasyon)
- Description güncellendi: litigation, FSHHM, GRADE, KOL, psikiyatri, Cobenfy anahtar kelimeleri

**v1.6.0** — 24 Nisan 2026. Büyük sürüm — tam ekosistem olgunlaşma:
- 4 yeni domain derinlik dosyası: `domains/kardiyoloji-ip.md` (PCSK9 + Factor XI + SGLT-2 + Lp(a) + ATTR + VERVE), `domains/metabolik-ip.md` (GLP-1 blockbuster pazarı + obezite + MASH + KOAH + T1D teplizumab), `domains/oftalmoloji-ip.md` (anti-VEGF + **Roche Vabysmo blockbuster** + retinal gene therapy + GA), `domains/dermatoloji-ip.md` (psöriazis cross-ref + JAK alopesi devrimi + vitiligo + HS + ADACLIN Era Pharma bağlantısı)
- 2 yeni operasyonel script: `scripts/report-builder.py` (11 rapor tipi orkestratörü + visualize entegrasyonu) + `scripts/biosimilar-comparator.py` (CQA benzerlik skorlama — ICH Q5E + FDA/EMA guidance uyumlu)
- 2 yeni filled example: `examples/landscape-ornek-adc-2030.md` (Mod 11 Landscape Forecast — ADC 2015-2030 öngörüsü + white space matrisi + Roche stratejik önerileri) + `examples/ddreport-ornek-ma.md` (Mod 7 M&A DD — OncoGenesis Biotech hipotetik akuistisyon + Monte Carlo 10K sim + tornado sensitivity)
- 1 React interactive artifact: `examples/showcase/pharmapatent-showcase.jsx` — IBM Carbon Design System + 6 sekmeli etkileşimli ekosistem gösterge paneli
- Description güncellendi: kardiyoloji, metabolik, oftalmoloji, dermatoloji + PCSK9, GLP-1, anti-VEGF, JAK anahtar kelimeleri
- Roche Türkiye için Vabysmo (oftalmoloji blockbuster) + Ocrevus (nöroloji) + glofitamab (hematoloji) + Actemra (immunoloji) stratejik vurgu genişletildi
- Mahir'in regülatör çalışmalarına bağlantılar: ADACLIN Era Pharma (dermatoloji), Glofitamab STARGLO defans (hematoloji)

**v1.5.0** — 24 Nisan 2026. Domain + şablon kütüphanesi + SPC genişlemesi:
- 3 yeni domain derinlik dosyası: `domains/immunoloji-ip.md` (TNF-α + IL ailesi + JAK/TYK2 + otoimmün), `domains/noroloji-ip.md` (MS + Alzheimer anti-amiloid + CGRP + nadir CNS), `domains/enfeksiyon-ip.md` (antibiyotik krizi + HIV + HCV + mRNA aşılar + antifungal)
- 1 yeni operasyonel script: `scripts/spc-calculator.py` — AB Supplementary Protection Certificate (Reg. EC 469/2009 Art. 13 formülü, max 5 yıl + 6 ay pediatric, TR karşılaştırması)
- 2 yeni filled example: `examples/licensing-ornek-adc.md` (Mod 10 için anti-TROP2 ADC deal), `examples/opposition-ornek-epo.md` (Mod 8 için pembrolizumab formülasyon EPO opposition)
- 1 yeni referans: `references/visualize-widget-kutuphanesi.md` — 33 hazır SVG/Mermaid/HTML şablonu, IBM Carbon + IBM Plex uyumlu, tüm 10 rapor tipinin zorunlu görsellerini kapsar
- Türkiye'de SPC olmaması kuralı vurgulandı (sadece 20 yıl patent + 6 yıl veri imtiyazı)
- Roche ürünleri immunoloji + nöroloji domain'lerinde özellikle vurgulandı (ocrelizumab, tocilizumab, crovalimab, glofitamab)
- HIV PURPOSE-1 lenacapavir PrEP pozitif klinik verisi entegre edildi

**v1.4.0** — 24 Nisan 2026. Domain + mod + bilirkişi + script genişlemesi:
- 2 yeni domain derinlik dosyası: `domains/onkoloji-ip.md`, `domains/hematoloji-ip.md` — terapötik alan-spesifik IP rehberi (Mahir'in uzmanlık alanları)
- 3 yeni operasyonel mod: Mod 10 Licensing, Mod 11 Landscape Forecast, Mod 12 Expert Witness
- 3 yeni yürütülebilir script: `cpc-recommender.py`, `family-tracer.py`, `priority-date-matrix.py`
- Yeni rapor şablonu: §10 Expert Witness Report (FSHHM bilirkişi rapor taslağı)
- Licensing modu ile `lex-mercator` sözleşme drafting entegrasyonu
- Landscape Forecast modu ile BERT/NLP tabanlı rakip portföy öngörüsü
- Expert Witness modu ile HMK m. 266 bilirkişi bağımsızlığı çerçevesi
- Paris Convention (12 ay) + PCT (30 ay) uyumluluk testi scripti
- INPADOC-style patent ailesi coverage + Mermaid diyagram
- Onkoloji: ICI + ADC + CAR-T + bispecific + RLT detay
- Hematoloji: Roche malignant hematology entegrasyon (glofitamab, emicizumab, bispecifics, CAR-T)

**v1.3.0** — 24 Nisan 2026. Compliance + görsel + araç genişlemesi:
- 2 yeni referans dosyası: `gorsel-standartlari.md` (her şablon için zorunlu görsel seti), `compliance-beyanlari.md` (GPP3/MDR-IVDR/KVKK/GDPR/avukat-müvekkil ayrıcalığı)
- 2 yeni yürütülebilir script: `royalty-calculator.py` (NPV+IRR+RFR+benchmark), `patent-expiry-monitor.py` (portföy takip + uyarı)
- 9 rapor şablonu için standart görsel seti tanımlandı (Gantt, heatmap, choropleth, citation network, radar, Monte Carlo)
- Compliance beyan matrisi her rapor tipi için tanımlandı
- IBM Carbon renk paleti + tipografi + SVG boyut standartları
- Rapor footer'ı için hazır şablon compliance blok'u (avukat-müvekkil + KVKK + çıkar çatışması + anti-bribery)
- Sektörel lisans benchmark kategorileri (7 kategori)
- Gecikmiş yıllık harç recovery penceresi (180 gün) takibi

**v1.2.0** — 23 Nisan 2026. Genişletme sürümü:
- 3 yeni operasyonel mod: Mod 7 Due Diligence, Mod 8 Opposition, Mod 9 Biosimilar Pathway
- 3 yeni referans dosyası: `patent-degerleme.md`, `biyobenzer-yol.md`, `yeni-modaliteler.md`
- 3 yeni rapor şablonu: §7 Due Diligence Report, §8 Opposition Briefing, §9 Biosimilar Pathway Briefing
- ADC, CAR-T, mRNA-LNP, gene therapy, siRNA, xenotransplantation modalite-spesifik protokolleri
- Patent değerleme metodolojisi (DCF, rNPV, Monte Carlo, RFR, comparable transactions)
- Biyobenzer karşılaştırılabilirlik paketi + AB/ABD/TR üçgeni regülatör kesişim
- M&A + licensing due diligence + red flag haritalama

**v1.1.0** — 23 Nisan 2026. Zenginleştirme sürümü:
- 3 filled example eklendi: atorvastatin FTO, trastuzumab invalidity, semaglutide regulatory
- Hedef kitle varyasyonları tanımlandı (Technical / Executive / Legal)
- 2 yürütülebilir script: `loe-calculator.py` + `claim-parser.py`
- Referans dosyaları arası çapraz atıf yoğunluğu 38 kenara çıkarıldı
- `scripts/` ve `examples/` SMP manifest'e eklendi

**v1.0.0** — 23 Nisan 2026. İlk tam sürüm. SMK 6769 + TRIPS + Doha + TÜRKPATENT 2024 Nice güncellemesi + Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği 2022 revizyonu entegre. BERT tabanlı landscape öngörü katmanı eklendi. Composability zincirleri: `medsearch` + `pharmaintel` (upstream); `carbon-html-report` + `carbon-pptx` + `docx` + `lex-mercator` + `onko-erisim` (downstream).

---

*Son söz: İlaç patenti hukuku, kimyasal formüllerin istem metnine, klinik verilerin ruhsat dosyasına, tıbbi gereklilik iddiasının zorunlu lisansa dönüştüğü çok katmanlı bir stratejik arenadır. Her savunma, bilimsel gerçekliğin hukuki mimariyle kusursuz örtüşmesine bağlıdır. Bu skill'in amacı, o örtüşmeyi mümkün kılmaktır.*
