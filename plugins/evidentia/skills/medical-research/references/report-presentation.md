# report-presentation.md — Nihai Sunum Sözleşmesi (Clean-Copy Doctrine) · v9.0

> **Ne zaman yüklenir:** HER çağrıda (Adım 0 zorunlu yükleme listesi). Bu dosya P7 — PRISMA
> Reporting / Output Generation'ın *biçim* ve *sunum* katmanını yönetir. `output-templates.md`
> "hangi bölümler / hangi format" sorusunu (①–⑧ SR rapor iskeleti — kapsam) yönetir; bu dosya
> "okuyucunun eline geçen nihai metin nasıl okunur" sorusunu (sunum) yönetir; `prisma-reporting.md`
> PRISMA artefaktlarının (akış diyagramı, kontrol listesi, SoF tablosu) mekaniğini yönetir. Üçü
> tamamlayıcıdır; çelişki hâlinde **clean-copy ilkeleri sunum açısından önceliklidir**.
>
> **v9.0 (Task 13, PRISMA refactor):** İç scaffold→clean-copy başlık eşlemesi, eski §1–21
> istihbarat-raporu iskeletinden **①–⑧ SR (sistematik derleme) başlık haritasına** geçirildi.
> Altı bağlayıcı temiz-kopya ilkesi (İlke 1–6+), VIZ/OPS HTML-yorum izolasyonu ve nihai
> doğrulama kapısı **korunmuştur**; kapı, PRISMA-kontrol-listesi tamamlık taramasını (G8)
> içerecek şekilde genişletilmiştir.

Bu sözleşmenin amacı tektir: araştırma sürecinin tüm derinliğini koruyarak, okuyucunun
eline **hakemli bir dergide okunan makale niteliğinde, temiz ve nihai bir kopya** vermek.
Operasyonel iz (çağrı sayısı, konnektör adı, iç süreç) rapor metnine **girmez**; ayrı,
render edilmeyen bir katmanda taşınır.

---

## 0. İki-Çıktı Modeli — Temiz Kopya + Render Edilmeyen Açıklama Katmanı

Her dosya-temelli rapor (`.md`) iki mantıksal katmandan oluşur:

| Katman | İçerik | Görünürlük | Sözdizimi |
|---|---|---|---|
| **A — Temiz Kopya** | Okuyucuya yönelik makale: özet, bulgular, tartışma, kaynaklar, bilgi kutuları, görünür şekil/tablo başlıkları | **Görünür** (render edilir) | Normal Markdown |
| **B — Görselleştirme Direktifleri** | Tasarım/render sürecine yönlendirme ("şu veriyi şu grafiğe dönüştür") | **Görünmez** (render'da gizli, kaynakta mevcut) | `<!-- VIZ: ... -->` HTML yorumu |
| **C — Operasyonel Ek** | Çağrı sayısı, native-first notu, konnektör boşlukları, Cömertlik Garantisi telemetrisi | **Görünmez** | `<!-- OPS: ... -->` HTML yorumu |

**Temel kural:** Bir `<!-- VIZ -->` veya `<!-- OPS -->` yorum bloğunun içindeki her şey
görünmezdir ve nihai render'da silinebilir. Yorum bloğunun dışındaki her şey **bitmiş,
yayına hazır okuyucu metnidir**. Bu ikili ayrım, "direktifler yalnızca tasarım sürecine
yönlendirmedir ve nihai rapor metnine girmez" gereksinimini yapısal olarak garanti eder.

**Neden HTML yorumu?** Standart Markdown→HTML hattının tamamında (carbon-html-report dâhil)
`<!-- ... -->` yorumları okuyucuya **render edilmez**; ancak `.md` kaynağında durdukları
için tasarımcı/renderleyici onları görüp işleyebilir. `:::viz` türü özel konteyner
sözdizimi, renderleyici onu tanımazsa **görünür düz metin** olarak sızar — bu nedenle
kullanılmaz. Görünmezlik garantisi yalnızca HTML yorumu ile koşulsuzdur.

---

## İlke 1 — Temiz Türkçe ve Bilimsel Üslup

**1.1 Tam cümle zorunluluğu.** Anlatı bölümleri (Giriş, Yöntem, Bulgular tartışmalı
kısımları, Tartışma, Sonuç) **eksiksiz, dilbilgisel olarak tam cümlelerle** yazılır.
Telgraf üslubu, yüklemsiz başlık-altı parçaları ve "veri dökümü" niteliğindeki kopuk
ibareler anlatı içinde kullanılmaz. Sayısal sonuç listeleri ve karşılaştırmalar tablo
veya — gerçekten sıralanabilir içerik için — madde imine alınabilir; ancak her tablo/madde
bloğu, kendisini bağlama oturtan en az bir tam cümleyle açılır ve bir sentez cümlesiyle
kapanır.

**1.2 Akademik kayıt (register).** Rapor gövdesi **nesnel, üçüncü tekil, kişiliksiz
bilimsel Türkçe** ile yazılır ("…gösterilmiştir", "…bildirilmektedir", "bu bulgu …
ile uyumludur"). Birinci tekil/çoğul anlatıcı sesi ("biz taradık", "ben buldum") ve
sohbet tonu kullanılmaz. Kesinlik dili kanıt düzeyine kalibre edilir: güçlü kanıt için
"göstermektedir", zayıf/ön kanıt için "düşündürmektedir / ön verilere göre" tercih edilir.

**1.3 Terminoloji.** Türkçe terim esastır; **ilk geçişte** İngilizce/özgün terim ve
kısaltma parantez içinde verilir: "genel sağkalım (overall survival, OS)". Sonraki
geçişlerde kısaltma kullanılır. İlaç adları, gen/protein sembolleri ve onaylı kısaltmalar
özgün biçimde korunur.

**1.4 Referans açıklığı (zorunlu).** Her özgün/sayısal iddia **açık bir kaynak işaretçisi**
taşır. "Bir çalışmaya göre", "literatürde belirtildiği üzere" gibi belirsiz atıflar
yasaktır. Varsayılan atıf biçimi **Vancouver** (numaralı, [1], [2]); talep hâlinde APA/AMA.
Kaynaklar listesinde her künye **kararlı tanımlayıcı** (PMID / DOI / NCT / ruhsat barkodu /
URL) ve **erişim tarihi** ile verilir. Bir iddiayı tek bir kaynağa dayandırmak mümkün
değilse, bu sınırlılık Bulgular/Tartışma içinde açıkça belirtilir; uydurma atıf yapılmaz.

---

## İlke 2 — Teknik/İşletme Sızıntısı Yasağı (Methods journal-style)

**2.1 Okuyucuya yönelik metinde YASAK olan unsurlar.** Aşağıdakiler temiz kopyanın
görünür gövdesinde **hiçbir biçimde** yer almaz (yalnızca `<!-- OPS -->` ekinde taşınabilir):

- Konnektör/araç adları ve fonksiyon imzaları: `search_articles`, `search_drugs`,
  `get_drug`, `who_gho_query`, `icd11_search`, `openfda_search` vb.
- "MCP", "connector", "native-first ladder", "HyDE", konnektör kimlikleri/hash'leri
  (`8f314cbe…`).
- İç süreç etiketleri: "Adım 0.5", "0.5.I", "§1.O", "specialty layer", "Türkiye Dörtlüsü",
  eksen adları.
- Çağrı telemetrisi: API çağrı sayısı, retry/backoff, pagination, "Cömertlik Garantisi"
  çağrı-sayım dipnotu, sidecar/JSON payload atıfları, sorgu DSL dizgeleri (`AFF:"Turkey"`).

**2.2 Okuyucuya yönelik metinde KABUL EDİLEN metodolojik ayrıntı.** "Genel ve anlaşılabilir
metodolojik ayrıntı" ilkesi, hakemli bir makalenin *Yöntem* bölümünde standart olan
açıklamayı **içerir** ve teşvik eder. Şunlar serbesttir ve beklenir:

- Taranan **kamu veri tabanlarının genel adları** (PubMed/Europe PMC, ClinicalTrials.gov,
  Cochrane, ulusal düzenleyici/geri ödeme kaynakları) — bunlar bir araç dökümü değil,
  bilimsel şeffaflığın gereğidir.
- Arama stratejisinin **kavramsal** özeti, dâhil etme/dışlama ölçütleri, dil ve **veri
  kesim (son güncelleme) tarihi**.
- Kanıt değerlendirme çerçevesi (örn. GRADE) ve kanıt hiyerarşisi mantığı — sade dille.

> Ayrım ölçütü: Bir bilgi, **okuyucunun çalışmayı değerlendirmesine** yarıyorsa Yöntem'e
> girer (kabul). Yalnızca **aracın nasıl çalıştığını** anlatıyorsa operasyonel ektedir
> (yasak). "PubMed tarandı" kabul; "`PubMed:search_articles` 2 sorgu × 25 sonuç ile
> çağrıldı" yasak.

**2.3 Telemetrinin yeniden konumlandırılması (Cömertlik Garantisi uzlaşımı).** v8.0'ın
zorunlu kıldığı Cömertlik Garantisi dipnotu ve tüm işletme izi, dosya-temelli temiz
kopyada görünür gövdeden çıkarılıp **`<!-- OPS -->` ekine** taşınır. Böylece şeffaflık
(çağrı sayısı, native-first çözümleme, konnektör boşlukları kaynakta erişilebilir kalır)
korunur, ancak makale niteliğindeki okuma deneyimi bozulmaz. Yalnızca kısa, etkileşimli
(dosya olmayan) yanıtlarda telemetri görünür kalabilir.

---

## İlke 3 — Anlatı Akışı ve Okunabilirlik

**3.1 IMRaD-temelli akış.** Temiz kopya, okuyucunun aşina olduğu bir mantıkla ilerler:
Yönetici Özeti → Giriş/Arka Plan → Yöntem → Bulgular (tematik alt-bölümler) → Tartışma →
Sınırlılıklar → Sonuç/Çıkarımlar → Kaynaklar. Bölümler arası **geçiş cümleleriyle**
bağlanır; her bölüm bir konu cümlesiyle açılır, bir sentez cümlesiyle kapanır. Ani sıçrama
ve bağlamsız tablo yığını yapılmaz.

**3.2 Düzyazı ↔ tablo/madde dengesi.** Çözümleme, yorum ve sentez **akıcı düzyazıyla**
verilir. Tablo ve madde imi yalnızca **gerçekten numaralandırılabilir/karşılaştırmalı**
içerik için (çalışma karakteristikleri, sonlanım değerleri, fiyat/geri ödeme satırları)
kullanılır. Ham bulgu listeleri, mümkün olduğunda çözümleyici düzyazıya dönüştürülür.

**3.3 Yön levhaları (signposting).** Uzun raporlarda kısa bir "okuma rehberi" cümlesi,
bölüm başlarında ne anlatılacağını işaret eder. Çapraz atıflar ("bkz. Tablo 2", "Şekil 1'de
özetlendiği üzere") okuyucuyu yönlendirir.

**3.4 Zenginleştirme.** Akış, içeriği seyreltmeden zenginleştirilir: mekanizma için kısa
bir kavramsal köprü, bir sonlanımın klinik anlamına dair bir yorum cümlesi, çelişen
bulguların neden çeliştiğine dair bir açıklama. Zenginleştirme **kanıttan kopmaz**; her
yorum cümlesi atıf veya açık bir mantıkla desteklenir.

---

## İlke 4 — Bilgi Kutuları (Definitions & Abbreviations)

Okuyucunun anlamadığı hiçbir terim/kısaltma kalmaması için iki mekanizma birlikte kullanılır.

**4.1 Kısaltmalar Dizini.** Yönetici Özeti'nin hemen ardından, raporda geçen tüm
kısaltmaları açan tek bir tablo yer alır.

```markdown
### Kısaltmalar Dizini
| Kısaltma | Açılım (özgün) | Türkçe karşılık |
|---|---|---|
| OS | Overall Survival | Genel sağkalım |
| PFS | Progression-Free Survival | İlerlemesiz sağkalım |
| HR | Hazard Ratio | Tehlike oranı |
```

**4.2 Bilgi Kutusu (info box) sözdizimi.** Bir terimin/kavramın yerinde açıklanması için,
**etiketli alıntı bloğu** kullanılır. Bu desen her Markdown renderleyicisinde okunur ve
carbon-html-report tarafından Carbon "callout/notification" bileşenine eşlenebilir:

```markdown
> **TANIM — Minimal Rezidüel Hastalık (Minimal Residual Disease, MRD):** Tedavi sonrası,
> standart yöntemlerle saptanamayan ancak yüksek duyarlıklı testlerle ölçülebilen düşük
> düzeyli hastalık varlığıdır. MRD negatifliği birçok hematolojik kanserde derin yanıtın
> göstergesi kabul edilmektedir.
```

**Etiket → Carbon callout türü eşlemesi** (renderleyiciye devir notunda kullanılır):

| Etiket öneki | Amaç | Carbon callout türü |
|---|---|---|
| `TANIM —` | Terim/kavram tanımı | `info` |
| `KLİNİK BAĞLAM —` | Bulgunun klinik anlamı/önemi | `info` (vurgulu) |
| `METODOLOJİK NOT —` | Okuyucuya yönelik yöntem açıklaması | `info` |
| `VERİ NOTU —` | Veri kaynağı/dönem/locale uyarısı | `info` |
| `SINIRLILIK —` / `DİKKAT —` | Yorum sınırı, dikkat | `warning` |

> Profesyonel/akademik ve düzenleyici (pharma) raporlarda **dekoratif emoji kullanılmaz**;
> anlam, metin etiketi ve render'da Carbon'un anlamsal renk/ikon sistemiyle taşınır.

**4.3 İlk-geçiş kuralı ile bütünlük.** Bilgi kutusu, İlke 1.3'teki "ilk geçişte parantez
içi açılım" kuralını **tamamlar**: kısa açılım metin içinde, ayrıntılı açıklama bilgi
kutusunda verilir. Her özgün/uzman terim en az bir kez tanımlanır.

---

## İlke 5 — Görselleştirme Direktifleri (Render'a Yönlendirme)

Rapor Markdown'ı sonradan görselleştirilerek render edileceğinden, "hangi veri hangi
grafiğe/diyagrama dönüşmeli" yönergeleri metne **gömülür** — ancak **yalnızca görünmez
`<!-- VIZ -->` yorumları içinde**.

**5.1 VIZ direktifi grameri.** Direktif, ilgili verinin **hemen yanına** yerleştirilir
(örn. ilgili tablodan sonra). Önerilen alanlar:

```markdown
<!-- VIZ:
type: <bar | grouped-bar | stacked-bar | line | area | scatter | forest-plot |
       kaplan-meier | funnel | swimlane | timeline | flow | prisma | consort |
       heatmap | pie | donut | choropleth | table-as-figure | callout>
title: "<şekil başlığı — render edilen şeklin başlığı için öneri>"
data: "<hangi veri: örn. Tablo 3'teki OS ve PFS için HR ve %95 GA değerleri>"
encoding: "<x=…, y=…, series=…, renk=…, sıralama=…>"
note: "<tasarımcı için ek talimat: eksen ölçeği, log/lineer, vurgulanacak nokta, eşik çizgisi>"
-->
```

**5.2 Görünmezlik garantisinin kuralları.**
- Görselleştirme/"şu grafiğe dönüştür / diyagrama dök / görselleştir" türü her yönerge
  **yalnızca** `<!-- VIZ -->` içinde bulunur; görünür gövdede asla cümle olarak yer almaz.
- VIZ yorumu **cümle içine gömülmez**; ilgili bloğun (paragraf/tablo) hemen altına ayrı
  satır olarak konur.
- **Görünür şekil başlığı isteniyorsa** (örn. "**Şekil 3.** Genel sağkalım için tehlike
  oranlarının karşılaştırması"), bu başlık **normal görünür Markdown** olarak yazılır ve
  VIZ yorumu onun hemen altına konur. Görünür başlık temiz kopyanın parçasıdır; tasarım
  talimatı değildir. Böylece "görünür caption" ile "görünmez direktif" karışmaz.

**5.3 Örnek (doğru kullanım).**

```markdown
**Tablo 3.** Faz 3 çalışmalarında genel sağkalım ve ilerlemesiz sağkalım sonuçları.

| Çalışma | Kol | OS HR (%95 GA) | PFS HR (%95 GA) |
|---|---|---|---|
| AAA-301 | A vs kontrol | 0,62 (0,48–0,80) | 0,55 (0,44–0,69) |
| BBB-204 | A vs kontrol | 0,71 (0,55–0,92) | 0,60 (0,47–0,77) |

**Şekil 1.** İki çalışmada genel sağkalım ve ilerlemesiz sağkalım için tehlike oranları.

<!-- VIZ:
type: forest-plot
title: "OS ve PFS tehlike oranları (HR), %95 güven aralıklarıyla"
data: "Tablo 3'teki OS HR / PFS HR ve %95 GA değerleri (AAA-301, BBB-204)"
encoding: "y=çalışma+sonlanım, x=HR (log ölçek), nokta=HR, çubuk=%95 GA"
note: "x=1 referans çizgisi kesikli; HR<1 lehte tarafı sol; OS ve PFS'i renkle ayır"
-->
```

Yukarıda okuyucu yalnızca Tablo 3'ü ve "Şekil 1." başlığını görür; forest-plot talimatı
kaynakta tasarımcı için durur, render'da görünmez.

---

## İlke 6+ — Hizalı Diğer İyileştirmeler

Bu öneriler 1–5'in ruhuna uygun, ek nitelik kazandıran unsurlardır:

- **Yönetici Özeti + Anahtar Bulgular.** Raporun başında 150–300 sözcüklük, düzyazı bir
  yönetici özeti; ardından her biri kanıt düzeyi etiketi taşıyan kısa "Anahtar Bulgular".
- **Kanıt düzeyi etiketleri.** Anahtar iddialar, GRADE'in sade Türkçe karşılığıyla
  etiketlenir: "Kanıt düzeyi: Yüksek / Orta / Düşük / Çok düşük". Etiket, iç jargona
  ("Tier 0") değil, okuyucuya yönelik dile dayanır.
- **Veri kesim tarihi.** Başlık bloğunda ve Yöntem'de "Veri kesim tarihi: GG Ay YYYY"
  ifadesi; güncellik notu (hızla değişen alanlarda son 12–24 ay vurgusu).
- **Sınırlılıklar (okuyucuya yönelik).** Konnektör boşluğu telemetrisinden **ayrı**, sade
  bilimsel dille yazılmış bir Sınırlılıklar bölümü (örn. "Türkiye'ye özgü insidans verisi
  sınırlıdır", "kanıtın çoğu tek-kollu çalışmalara dayanmaktadır").
- **Şekil/Tablo numaralandırma.** "Tablo N" / "Şekil N" sıralı; her tablo başlık + kaynak +
  gerektiğinde dipnot taşır; metinde çapraz atıf yapılır.
- **Sayı ve locale biçimi.** Türkçe metinde ondalık ayırıcı **virgül** (0,62); büyük
  sayılarda binlik ayırıcı nokta. İstatistiksel gösterim (HR, %95 GA, p) uluslararası
  kurala uygun ve tutarlı tutulur; birimler daima belirtilir.
- **Telif uyumu.** Tam metin yalnızca çözümleme için kullanılır; toplu birebir alıntı
  yapılmaz; alıntılar 15 sözcüğün altında ve kaynak başına en çok bir kez; CC-BY içerik
  serbestçe alıntılanabilir.
- **Başlık bloğu.** Başlık, alt başlık, veri kesim tarihi ve araştırma sorusu/kapsamı
  verilir; **yazar kimliği iddiası, kurum logosu uydurması veya araç/sürüm bilgisi konmaz**.

---

## Clean-Copy İskeleti (okuyucuya yönelik bölüm sırası — SR/PRISMA ①–⑧)

Bu iskelet `output-templates.md` §1'in ①–⑧ SR rapor sözleşmesinin **okuyucuya görünen**
biçimidir; numaralı dairelerin (①…⑧) kendisi başlık metnine girmez — doğal Türkçe akademik
başlıklar kullanılır (aşağıdaki eşleme tablosunda birebir karşılıkları verilmiştir).

```markdown
# [Başlık]
## [Alt başlık — kapsam, derleme tipi: sistematik derleme | kapsam derlemesi | hızlı derleme]
*Veri kesim tarihi: GG Ay YYYY · Araştırma sorusu: … · PICO/PECO: P … I/E … C … O …*

## Yönetici Özeti
(150–300 sözcük, düzyazı — PRISMA'nın yapılandırılmış özet ilkesiyle uyumlu: amaç, yöntem
özeti, ana bulgu, ana kısıtlılık, sonuç tek paragrafta)

## Anahtar Bulgular
- … (Kanıt düzeyi: …) — GRADE sertaintysinin sade Türkçe karşılığı

### Kısaltmalar Dizini
| Kısaltma | Açılım | Türkçe |

## ① Arka Plan
(klinik/bilimsel gerekçe — neden bu soru, mevcut kanıt boşluğu)

## ② Amaç ve Kapsam
(PICO/PECO/PCC düzyazı biçiminde; derleme tipi — sistematik/kapsam/hızlı — ve gerekçesi)

## ③ Yöntem
(uygunluk kriterleri, bilgi kaynakları/veri tabanları, arama stratejisi özeti, seçim süreci,
veri çıkarım süreci, yanlılık riski aracı, sentez yöntemi, GRADE, veri kesim tarihi —
genel veri tabanı adları serbest, araç/fonksiyon adı yok — bkz. İlke 2.2)

## ④ PRISMA Akış Diyagramı
(kutu-kutu şema + görünür "Şekil N." başlığı; VIZ direktifi hemen altında — bkz. İlke 5)

## ⑤ Bulgular
### Çalışma Özellikleri
(dahil çalışmaların tablo hâlinde özeti — bkz. ⑤.1)
### Yanlılık Riski Özeti
(trafik-ışığı/ısı-tablosu görünür başlığı + VIZ direktifi — bkz. ⑤.2)
### Sonuç Bazlı Bulgular
(her kritik/önemli sonlanım için ayrı alt-başlık; anlatı + tablo — bkz. ⑤.3)
### Küresel Literatür ve Kanıt Tabanı            ← her derlemede
### Klinik Geliştirme Hattı                       ← ilgiliyse
### Mekanizma ve Farmakoloji                      ← ilaç bağlamında
### Ruhsat, Etiket ve Düzenleyici Durum            ← ilaç bağlamında
### Türkiye'de Ruhsat, Fiyat ve Geri Ödeme         ← TR bağlamında
### Epidemiyoloji ve Hastalık Yükü                 ← 0.5.K aktifse
### Kılavuz Önerileri ve Klinik Yerleşim           ← ilgiliyse
(+ uzmanlık alanı alt-başlıkları, gerektiğinde)

## ⑥ Summary-of-Findings (Kanıt Özeti) Tablosu
(GRADE sertainty + etki büyüklüğü + görünür "Tablo N." başlığı — bkz. `evidence-grading.md` §8)

## ⑦ Tartışma
(yakınsama/ıraksama, zamansal anlatı, kılavuz uyumu — sentez düzyazısı)
### Kısıtlılıklar
(kanıt kısıtlılığı + yöntem kısıtlılığı — tekil-eleştirmen notu dâhil, `screening.md` §4)
### Sonuç ve Çıkarımlar

## ⑧ Kaynaklar
1. … PMID/DOI/NCT — Erişim: GG Ay YYYY

### Ek — Dahil Edilen Çalışmalar
### Ek — Tam Metinde Dışlanan Çalışmalar (gerekçeli)

<!-- Opsiyonel zenginleştirme ekleri (yalnız ilgili modül tetiklendiyse; ①–⑧'in bir parçası
     DEĞİL, ayrı ve etiketli) -->
## Ek A — İlaç İstihbaratı ve Ticari Görünüm      ← 0.5.I aktifse
## Ek B — Düzenleyici Kilometre Taşları           ← 0.5.C aktifse
## Ek C — HTA / Erişim Modeli                     ← 0.5.D aktifse
## Ek D — Bilimsel Görüş Liderleri ve Araştırma Ağı ← KOL modülü aktifse
## Ek E — Epidemiyolojik Ek Tablo                 ← 0.5.K genişletilmiş veri gerektiriyorsa

<!-- OPS:
Üretim notu (okuyucuya render edilmez). Çağrı sayısı: N. Aktif fazlar: P0–P7. Aktif
zenginleştirme modülleri: […]. Native-first çözümleme uygulandı. Konnektör boşlukları: […].
Cömertlik Garantisi: […].
-->
```

---

## İç SR Bölüm → Clean-Copy Başlık Eşlemesi (①–⑧)

`output-templates.md` §1'deki ①–⑧ SR rapor sözleşmesi araştırmanın **kapsamını ve sırasını**
garanti eder; ancak o sözleşmedeki numaralı-daire etiketleri ve alt-madde tool-provenance
okları (`← prisma-protocol.md §3` gibi) temiz kopyaya **olduğu gibi girmez** — doğal Türkçe
akademik başlıklara çevrilir. Aşağıdaki eşleme uygulanır (bu tablo, eski §1–21 istihbarat-
raporu iskeletinin yerini alır — Task 13, PRISMA refactor):

| İç SR bölümü (kapsam, `output-templates.md` §1) | Temiz kopya başlığı (okuyucu) |
|---|---|
| ① Arka Plan | Arka Plan |
| ② Amaç + PICO/PECO + derleme tipi | Amaç ve Kapsam |
| ③.1 Uygunluk kriterleri | Yöntem → "dahil edilen çalışmalar şu kriterlere göre belirlendi" cümlesi |
| ③.2 Kaynaklar / bilgi kaynakları | Yöntem → "taranan kamu veri tabanlarının genel adları" (İlke 2.2) |
| ③.3 Arama stratejisi | Yöntem → arama stratejisinin kavramsal özeti + veri kesim tarihi |
| ③.4 Seçim süreci | Yöntem → seçim/tarama süreci özeti |
| ③.5 Veri çıkarım süreci | Yöntem → çıkarım süreci özeti |
| ③.6 Yanlılık riski değerlendirmesi | Yöntem → uygulanan RoB aracı adı (RoB 2/ROBINS-I/QUADAS-2/NOS) |
| ③.7 Sentez yöntemleri | Yöntem → sentez yaklaşımı (anlatı/meta-analiz) |
| ③.8 GRADE | Yöntem → "kanıt değerlendirme çerçevesi" sade dille |
| ③.9 Veri kesim tarihi | Başlık bloğu + Yöntem |
| ④ PRISMA akış diyagramı | PRISMA Akış Diyagramı (görünür "Şekil N." + VIZ direktifi) |
| ⑤.1 Çalışma özellikleri tablosu | Bulgular → Çalışma Özellikleri |
| ⑤.2 RoB özeti | Bulgular → Yanlılık Riski Özeti |
| ⑤.3 Sonuç-bazlı bulgular | Bulgular → Sonuç Bazlı Bulgular + konu-özel alt-başlıklar (Küresel Literatür, Klinik Geliştirme Hattı, Mekanizma/Farmakoloji ilaç bağlamında, Ruhsat/Düzenleyici Durum ilaç bağlamında, Türkiye'de Ruhsat/Fiyat/Geri Ödeme, Epidemiyoloji 0.5.K aktifse, Kılavuz Önerileri) |
| ⑥ Summary-of-Findings/GRADE tablosu | Summary-of-Findings (Kanıt Özeti) Tablosu |
| ⑦ Tartışma · kısıtlılıklar · sonuç | Tartışma / Kısıtlılıklar / Sonuç ve Çıkarımlar |
| ⑧ Kaynaklar + dahil/dışlanan listeleri | Kaynaklar + Ek — Dahil Edilen Çalışmalar + Ek — Tam Metinde Dışlanan Çalışmalar |
| Opsiyonel zenginleştirme ekleri (0.5.A–K, KOL) | Ayrı, etiketli "Ek A/B/C/D/E — …" bölümleri; ①–⑧'in bir parçası değildir, ①–⑧'den SONRA gelir |

---

## Nihai Doğrulama Kapısı (emit'ten önce çalıştırılır — G1–G8)

Aşağıdaki kontroller temiz kopya yayımlanmadan **önce** uygulanır. Herhangi biri başarısızsa
metin düzeltilir. **v9.0 (Task 13):** kapı, G8 — PRISMA-kontrol-listesi tamamlık taraması —
eklenerek genişletilmiştir; bu, `SKILL.md`'nin "Completeness Gate"iyle aynı değildir (o,
konnektör/bölüm kapsamasını denetler; G8 burada **rapor metninin** PRISMA 2020/ScR madde
madde karşılığını denetler).

**G1 — Tam cümle.** Anlatı bölümlerinde yüklemsiz/telgraf parça yok; her tablo/madde bloğu
tam cümleyle çerçevelenmiş.

**G2 — Sızıntı taraması (görünür gövde).** Görünür metinde (yorumlar hariç) aşağıdaki
örüntülerin **hiçbiri** bulunmamalı:

```bash
# Yasak araç/işletme jetonları — yalnızca <!-- ... --> dışındaki görünür metinde aranır
grep -nE '(:search_|:get_|MCP|connector|native-first|HyDE|Adım 0\.5|0\.5\.[A-Z]|P[0-7] \(faz\)|screening_log|evidence_table|rob_assessments|grade_sof|AFF:"|Cömertlik Garantisi|sidecar|payload|search_drugs|who_gho_query|icd11_search|openfda_search)' rapor.md
# Görünür görselleştirme DİREKTİFİ sızıntısı (komut kipinde, yorum dışında)
grep -nE '(grafiğe (dönüştür|çevir)|diyagrama (dök|çevir)|görselleştir:|bir tabloya dönüştür)' rapor.md
```
Not: Bu taramalar `<!-- VIZ -->` / `<!-- OPS -->` içeriğini hariç tutacak biçimde
yorumlanır (yorum blokları kasıtlı olarak bu jetonları taşıyabilir). "PubMed/CT.gov tarandı",
"RoB 2 uygulandı", "GRADE ile derecelendirildi" gibi **veri tabanı adları ve yöntemsel
çerçeve adları kabul** edilir; yasak olan, fonksiyon imzaları, sidecar alan adları
(`screening_log` vb.) ve iç süreç/faz etiketleridir.

**G3 — Direktif izolasyonu.** Tüm görselleştirme yönergeleri `<!-- VIZ -->` içinde; görünür
gövdede yalnızca "**Şekil N.**" görünür başlıkları var.

**G4 — Referans bütünlüğü.** Her özgün/sayısal iddianın bir kaynak işaretçisi var; Kaynaklar
listesindeki her künye PMID/DOI/NCT/URL + erişim tarihi taşıyor; "bir çalışmaya göre" türü
belirsiz atıf yok.

**G5 — Tanım kapsaması.** Raporda geçen her kısaltma Kısaltmalar Dizini'nde açılmış; her
uzman terim en az bir kez (parantez açılımı veya bilgi kutusu) tanımlanmış.

**G6 — Telemetri konumu.** Cömertlik Garantisi ve tüm işletme izi `<!-- OPS -->` ekinde;
görünür gövdede çağrı sayısı/konnektör adı yok.

**G7 — Akış.** Bölümler geçiş cümleleriyle bağlı; her bölüm konu cümlesiyle açılıp sentez
cümlesiyle kapanıyor; Yönetici Özeti ve Sonuç mevcut.

**G8 — PRISMA-kontrol-listesi tamamlık taraması.** Rapor, `prisma-reporting.md` §2'deki madde
grubu → bölüm eşlemesine karşı denetlenir; sistematik/hızlı derlemede PRISMA 2020 27 maddesinin,
kapsam derlemesinde PRISMA-ScR 22 maddesinin **her biri** raporda karşılığını buluyor mu diye
tek tek işaretlenir:
- ① Arka Plan madde 3–4'ü (gerekçe, amaç/PICO) karşılıyor mu?
- ③ Yöntem, madde 5–15/16'yı (uygunluk, bilgi kaynağı, arama, seçim, çıkarım, RoB aracı, sentez
  yöntemi) tek tek karşılıyor mu — hiçbiri sessizce atlanmamış mı?
- ④ PRISMA akış diyagramı, `screening_log` sayaçlarıyla **birebir** tutarlı mı (madde 8–9,
  reconciliation: `included + Σexcluded_title_abstract + Σexcluded_full_text == identified`)?
- ⑤ Bulgular, madde 16–22/20'yi (seçim akışı, çalışma özellikleri, RoB sonucu, sonuç sentezi)
  karşılıyor mu; yalnızca `human_approved:true` satırlar tabloya/figüre girmiş mi
  (`prisma-reporting.md` §3–§4)?
- ⑥ SoF tablosu madde 20 kapsamındaki sentez sonuçlarını GRADE sertaintysiyle birlikte taşıyor mu?
- ⑦ Tartışma madde 23'ü (kanıt + yöntem kısıtlılığı, tekil-eleştirmen notu) karşılıyor mu?
- ⑧ Kaynaklar/protokol/fon/COI madde 24–27'yi karşılıyor mu?
- **Kapsam derlemesinde** (PRISMA-ScR): RoB atlanmışsa ⑤.2/⑥ bunu **açıkça** "kapsam
  derlemesi — RoB uygulanmadı" notuyla belirtiyor mu (gizlenmiyor mu)?

Eksik bir madde varsa rapor **tamamlanmamış** sayılır; eksiklik doldurulur veya (gerçekten
uygulanamıyorsa) raporda açık bir "uygulanamaz" notuyla işaretlenir — sessizce atlanmaz. Bu
tarama SKILL.md'nin Adım 0.4/Completeness Gate'inin (konnektör/bölüm kapsaması) yerini almaz;
onu **rapor-metni düzeyinde** tamamlar.

---

## Renderleyiciye Devir Notu (carbon-html-report ve diğer renderleyiciler için)

Bu raporu render eden katman aşağıdaki sözleşmeye uyar:

1. **`<!-- VIZ -->` ve `<!-- OPS -->` yorumları tüketilir ve render çıktısında temizlenir.**
   Hiçbir koşulda görünür içeriğe dönüştürülmez. (Renderleyici bunları tanımıyorsa bile, HTML
   yorumu olduklarından zaten okuyucuya görünmezler; tam temizlik için final adımda silinmeleri
   önerilir.)
2. **VIZ direktifleri**, belirtilen `type/title/data/encoding/note` ile ilgili verinin yerine
   bir şekil üretmek için kullanılır. carbon-html-report'un bu sözdizimini işlemesi için
   companion bir güncelleme önerilir; bu güncelleme yoksa garanti yine de bozulmaz (direktif
   görünmez kalır).
3. **Bilgi kutusu etiketleri** (`TANIM —`, `KLİNİK BAĞLAM —`, `METODOLOJİK NOT —`, `VERİ NOTU —`,
   `SINIRLILIK —`/`DİKKAT —`) İlke 4.2'deki eşlemeye göre Carbon callout/notification türlerine
   bağlanır.
4. **Sıralı şekil/tablo numaraları** ve çapraz atıflar korunur.

---

*v9.0 — Bu dosya P7 (PRISMA Reporting)'in sunum katmanını yönetir. Temiz kopya = okuyucunun
gördüğü ①–⑧ SR makale; VIZ/OPS = yalnızca tasarım/şeffaflık için görünmez katman. "Direktifler
nihai metne girmez" gereksinimi, HTML-yorumu izolasyonu + G2/G3 doğrulama kapısı ile; "rapor
PRISMA'nın tüm maddelerini karşılıyor" gereksinimi G8 ile yapısal olarak güvence altındadır.*
