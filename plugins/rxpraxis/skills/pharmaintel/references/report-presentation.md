# pharmaintel — Nihai Rapor Sunum Standardı (Reader-Facing Clean-Copy Standard)

> **Bu dosyanın amacı:** pharmaintel'in Faz 5 (Synthesis) çıktısının *sunulan* hâlini yönetir. Skill'in kanıt toplama, triangülasyon ve provenans disiplini (sources-catalog.md, triangulation.md, provenance-engine.md) **değişmeden** korunur; bu referans yalnızca **toplanan istihbaratın okuyucuya nasıl sunulacağını** standartlaştırır. v8.1.0 ile eklenmiştir.
>
> **Yükleme disiplini (lazy-load):** Bu dosya **Faz 5'e girerken** (rapor taslağı oluşturulurken) yüklenir. Faz 1–4 (scope, discovery, deep-dive, triangulation) sırasında yüklenmesine gerek yoktur. Görev yönlendirmesi (Step 1) ve kanıt toplama tamamlandıktan sonra, raporu kaleme almadan **hemen önce** okunur.
>
> **Bağlayıcılık:** Bu standardın §1, §4, §5 ve §6 bölümleri **zorunludur** (manifest kapıları G66 + G67 + G68). §2, §3, §7 ileri-kalite yönergeleridir ve her raporda uygulanması beklenir.

---

## Tasarım felsefesi — neden iki katman?

Bir pharmaintel raporu iki birbirinden farklı işlevi aynı anda yerine getirmek zorundadır:

1. **Okunabilirlik:** Karar verici (Medical Affairs, Ticari, Market Access, akademik okuyucu) raporu, hakemli bir dergide okuduğu bir makale gibi akıcı, eksiksiz ve anlaşılır bulmalıdır. Bu okuyucu, skill'in iç çalışma mekaniğiyle (validator çağrıları, kapı kimlikleri, hiyerarşi rütbeleri, override anotasyonları) ilgilenmez — bunlar onun için **gürültüdür** ve metnin niteliğini düşürür.

2. **Denetlenebilirlik:** Skill'in bütünlük kapıları (G3 triangülasyon, G4 provenans damgası, G13 güven dağılımı, G22 generic-by-default, G17 katman ifşası) çıktının iç katmanında **eksiksiz** bulunmak zorundadır; aksi hâlde rapor savunulamaz hâle gelir ve validator başarısız olur.

Bu iki işlev **çelişir gibi görünür** ama aslında ayrıştırılabilir. Çözüm, çıktıyı iki katmana bölmektir:

| Katman | Adı | İçerik | Render'da görünür mü? | Kimin için? |
|---|---|---|---|---|
| **A** | Okur-yüzlü temiz kopya (clean copy) | Dergi-niteliğinde Türkçe metin, bilgi kutuları, tablolar, şekiller, numaralı atıflar, Kaynaklar | **Evet** (birincil teslimat) | Karar verici / okuyucu |
| **B** | İç denetim ve sağlama kaydı (audit ledger) | Provenans damgaları, güven dağılım tablosu, triangülasyon notları, G22 denetim satırı, katman ifşaları | **Hayır** (render dışı) | Validator / denetçi / kayıt |

**Temel ilke:** Birincil teslimat **Katman A'dır.** Katman B, raporun bütünlüğü ve validator'ın çalışması için ham markdown'da bulunur ama render edilen nihai üründe **görünmez**. Görselleştirme talimatları da aynı render-dışı kanalı kullanır.

---

## §1 — İki-Katmanlı Çıktı Modeli (ZORUNLU — Gate G66)

### §1.1 Katman A — Okur-yüzlü temiz kopya

Bu, raporun **varsayılan teslim edilen hâlidir.** Şu özellikleri taşır:

- **Yalnızca okuyucunun ihtiyaç duyduğu içerik:** arka plan, bulgular, sentez, sınırlılıklar, kaynaklar. İç çalışma mekaniğine dair **tek bir teknik kotasyon bulunmaz.**
- **Atıflar dergi biçimindedir:** metin içinde üst-simge/köşeli-parantez atıf işaretleri (`[1]`, `[2]`); tam künyeler sondaki **Kaynaklar** bölümünde (bkz. §7). Gövdede `> — Source: ... — Confidence: High` biçiminde blok-alıntı provenans damgası **kullanılmaz** — bu damgalar Katman B'ye taşınır.
- **Tanımlar ve kısaltmalar bilgi kutularıyla ve bir dizinle** karşılanır (bkz. §4); okuyucunun anlamadığı terim kalmaz.
- **Yöntem, okuyucu-dostu düzyazıyla** anlatılır (bkz. §6.2) — "validator", "G22", "gate", "hiyerarşi rütbesi" gibi iç terimler **geçmez**.

> **Yöntem Notu · Katman A'nın testi**
>
> Katman A'nın doğru kurulup kurulmadığını anlamanın pratik testi şudur: *Bu metni, skill'in varlığından habersiz bir hakemli dergi editörüne gösterseniz, herhangi bir "iç süreç sızıntısı" fark eder mi?* Cevap "hayır" olmalıdır. Editör yalnızca bir bilimsel/ticari istihbarat makalesi görmelidir.

### §1.2 Katman B — İç denetim ve sağlama kaydı

Skill'in kapı-zorunlu makinesi şu öğeleri içerir ve bunların tamamı Katman B'ye yerleştirilir:

- Madde-bazlı 4-parçalı provenans damgaları (kaynak türü + kimlik/URL + erişim tarihi + güven) — G4
- Güven Dağılım Tablosu (Confidence Disclosure) — G13
- Triangülasyon Notları (hiyerarşi rütbeleriyle çatışma çözümü) — G3
- G22 generic-by-default denetim sonucu satırı + validator çağrısı — G22 / G61
- Auto-Trigger Disclosure, Sponsor Sweep Disclosure — G17
- Varsa `# G22-OVERRIDE` anotasyonları + gerekçeleri

**Yalıtım mekaniği (bkz. §6.3):** Katman B, ham markdown'da **render-dışı sentinel çiftiyle** sarmalanmış bir ek olarak (`<!-- RENDER:EXCLUDE-FROM-HERE -->` … `<!-- RENDER:EXCLUDE-TO-HERE -->`) bulunur **veya** ayrı bir refakat dosyası olarak üretilir. Her iki durumda da render edilen okur-yüzlü üründe görünmez.

**Validator uyumu — kritik:** Katman B'deki açıklama bloklarının başlıkları (`## Provenance Disclosure`, `## Confidence Disclosure`, `## Triangulation Notes`, `## Auto-Trigger Disclosure`) **gerçek `##` markdown başlıkları olarak korunur** — çünkü `scripts/validate-report-discipline.py` tüm dosyayı ham metin olarak tarar ve bu blokları başlık regex'iyle bulur. Başlıkları HTML yorumuna gömmeyin veya `###`/`####` seviyesine indirmeyin; aksi hâlde validator'ın Check 8 ve Check 9'u bu blokları bulamaz. (`##?\s*Provenance\s+Disclosure` deseni yalnızca `#` veya `##` ile eşleşir.)

### §1.3 Çıktı sırası (kanonik)

Birleşik markdown dosyasının kanonik sırası:

```
[Meta-blok (YAML front-matter)]
[Katman A — okur-yüzlü temiz kopya: başlık → özet → gövde → kaynaklar]
<!-- RENDER:EXCLUDE-FROM-HERE -->
[Katman B — iç denetim ve sağlama kaydı: ## Provenance Disclosure, ## Confidence Disclosure, ## Triangulation Notes, ## Auto-Trigger Disclosure, G22 satırı]
<!-- RENDER:EXCLUDE-TO-HERE -->
```

Görselleştirme talimatları (HTML yorumları), Katman A'nın **içinde**, ilgili oldukları verinin hemen yanında bulunur (bkz. §5).

---

## §2 — Türkçe Bilimsel Yazım Standardı

Okur-yüzlü temiz kopya, yüksek nitelikli bir bilimsel rapor diliyle yazılır.

**Cümle ve dil:**
- **Eksiksiz cümle yapısı.** Eksiltili/parçalı ifadelerden kaçının (tablolar ve madde listeleri bunun istisnasıdır; ancak madde listelerinde de en az bir tam cümle kurun).
- **Nesnel, edilgen bilimsel ses.** "Biz inanıyoruz / bize göre" yerine "veriler ... göstermektedir", "kanıtlar ... işaret etmektedir". Aşırı kesinlik iddialarından kaçının; güven düzeyi belirsiz olan bulgular için temkinli kiplik kullanın ("... olabileceği", "ön bulgular ... düşündürmektedir").
- **Anlaşılırlık önceliği.** Karmaşık veri ilişkilerini önce sözel olarak açıklayın, ardından tabloyla/şekille destekleyin.
- **Anglikizm dengesi.** Yerleşik Türkçe karşılığı olan terimlerde Türkçeyi tercih edin. Sektörde yerleşik teknik terimler (örn. "endpoint", "readout", "label", "biowaiver") ilk geçişlerinde Türkçe karşılığıyla birlikte verilir; özgün terim parantez içinde korunabilir: "birincil sonlanım noktası (primary endpoint)".

**Terimler ve kısaltmalar:**
- **Her kısaltma ilk geçtiği yerde açılır:** "Avrupa İlaç Ajansı (EMA)". Sonraki geçişlerde kısaltma kullanılabilir.
- Açılan terim ek tanım gerektiriyorsa bir **Bilgi Kutusu** ile desteklenir (bkz. §4).
- Tüm kısaltmalar ayrıca rapor başındaki **Kısaltmalar Dizini'nde** toplanır.

**Biçim tutarlılığı:**
- Tarihler ISO 8601 (YYYY-AA-GG).
- Para birimleri açık belirtilir (USD, EUR, GBP, TRY); birim ve büyüklük net (örn. "1,18 milyar USD").
- Etki büyüklükleri, %95 GA, p-değerleri ve örneklem büyüklükleri standart gösterimle (örn. "HR 0,64; %95 GA 0,54–0,76; p<0,001; n=412").
- Sayısal değerlerde Türkçe ondalık ayracı (virgül) tutarlı kullanılır.

**Referans açıklığı (kullanıcı önceliği):** Her maddi iddia, kaynağına izlenebilir olmalıdır. Gövdede numaralı atıf işareti, sonda tam künye (§7). Kaynağa ulaşılamayan veya yalnızca ikincil kaynaktan teyit edilen iddialar, metinde açıkça bu sınırlılıkla birlikte sunulur ("birincil düzenleyici kaynaktan teyit edilememiştir; ikincil sektör basınına dayanmaktadır").

---

## §3 — Anlatı Akışı ve Makro Yapı

Rapor, okuyucunun rahat takip edebileceği, mantıksal olarak ilerleyen bir yapı kurar.

**Önerilen makro yapı (göreve göre uyarlanır):**

1. **Yönetici Özeti** — Yalnızca bu bölümü okuyan biri konuyu, mevcut durumu, en kritik 2–3 bulguyu ve en önemli belirsizliği öğrenmelidir.
2. **Arka Plan / Bağlam** — Konunun çerçevesi; okuyucuyu bulgulara hazırlar (terminoloji, endikasyon/modalite tanımı, pazar bağlamı).
3. **Göreve özgü bulgu bölümleri** — Mantıksal sırada (örn. düzenleyici durum → klinik kanıt → ticari konum → katalizörler). Her bölüm bir önceki bulguya köprülenir.
4. **Sentez / Çıkarımlar** — Bulgular bir araya getirilir; paydaş-agnostik çıkarımlar (generic-by-default disiplini korunur).
5. **Sınırlılıklar** — Açık erişim kaynak boşlukları, konuya özgü boşluklar, veri kesim tarihi.
6. **Kaynaklar** — Numaralı, tam künyeli (§7).

**Akış teknikleri:**
- **Bölüm açılışı (lede):** Her bölüm, o bölümün ana bulgusunu özetleyen bir cümleyle açılır; ardından kanıt, ardından bağlam gelir.
- **Tablo çerçeveleme:** Her tablodan **önce** onu tanıtan bir yönlendirme cümlesi ("Aşağıdaki tablo, ... karşılaştırmaktadır"); her tablodan **sonra** bulguyu yorumlayan bir cümle ("Tablodan görüldüğü üzere ...").
- **Köprü cümleleri:** Bölümler arası geçişlerde bağlantı kurulur ("Düzenleyici durum bu şekilde netleştikten sonra, klinik kanıt tabanına geçilebilir").
- **Paragraf hijyeni:** Bölüm düzyazısı ~8 paragrafı aşarsa alt başlıklara bölünür. Okuma yükünü azaltmak için uzun listeler tablolaştırılır.
- **Zenginleştirme:** Anlatım, bulguların **anlamını** açıklayacak şekilde detaylandırılır — yalın veri dökümü değil, bağlamlı yorum. Ancak zenginleştirme, doğrulanmamış spekülasyona dönüşmemelidir; her yorum kanıta bağlı kalır.

---

## §4 — Bilgi Kutuları ve Kısaltmalar Dizini (ZORUNLU — Gate G68)

Okuyucunun anlamadığı bir detay kalmaması için iki tamamlayıcı mekanizma kullanılır.

### §4.1 Kısaltmalar ve Tanımlar Dizini (rapor başında)

Raporun başında, Yönetici Özeti'nden hemen önce veya sonra, raporda geçen tüm kısaltmaları ve anahtar terimleri toplayan bir dizin bulunur:

```markdown
## Kısaltmalar ve Tanımlar

| Kısaltma / Terim | Açılım / Tanım |
|---|---|
| ADC | Antikor-ilaç konjugatı (antibody-drug conjugate) — bir monoklonal antikorun, bağlayıcı (linker) aracılığıyla sitotoksik bir yüke (payload) bağlandığı hedefe yönelik tedavi sınıfı. |
| HR | Tehlike oranı (hazard ratio) — olay hızlarının zaman içindeki oranı; <1 değeri lehte etkiyi gösterir. |
| PDUFA | ABD FDA'nın bir başvuru için kendisine belirlediği karar hedef tarihi (Prescription Drug User Fee Act goal date). |
```

### §4.2 Bilgi Kutuları (metin içinde, ilgili yerde)

Okuyucunun akışı bozulmadan, bir terimin veya kavramın ilk geçtiği yerde **satır içi bilgi kutusu** ile derinlemesine açıklama sağlanır. Kanonik biçim — **bold etiketli blok-alıntı**:

```markdown
> **Bilgi Kutusu · Birincil sonlanım noktası (primary endpoint)**
>
> Bir klinik çalışmanın başarısını ölçmek için önceden belirlenen ana ölçüt. Düzenleyici onay kararları büyük ölçüde birincil sonlanım noktasındaki istatistiksel anlamlılığa dayanır; ikincil sonlanım noktaları destekleyici kanıt sağlar.
```

**Bilgi kutusu türleri:**

| Etiket | Kullanım |
|---|---|
| `Bilgi Kutusu · [Terim]` | Terim/kısaltma/kavram tanımı — okuyucunun anlaması için (birincil, en sık kullanılan tür). |
| `Yöntem Notu · [Başlık]` | Genel ve anlaşılır metodolojik açıklama (örn. "iki bağımsız kaynakla teyit ilkesi"). **İç makine terimleri içermez** (validator, gate, rütbe). |
| `Dikkat · [Başlık]` | Önemli bir uyarı, kısıtlama veya yanlış yorumlanmaya açık nokta vurgusu. |

**Disiplin kuralları:**
- Bilgi kutuları **okuyucu için** vardır; iç süreç ifşası **değildir**. `Yöntem Notu` kutuları yalnızca okuyucu-dostu, genel metodolojik açıklamalar içerir.
- Aynı terim için kutu yalnızca **ilk geçişte** açılır; tekrar açılmaz.
- Bir bilgi kutusu, atıf gerektiren maddi bir iddia içeriyorsa o iddia da numaralı atıfla desteklenir.

> **Yöntem Notu · Render boru hattı bilgi kutularını nasıl ele alır**
>
> Render aşaması (carbon-html-report), `Bilgi Kutusu`, `Yöntem Notu` ve `Dikkat` etiketli blok-alıntıları algılayıp Carbon "aside" / "notification" bileşenlerine yükseltebilir. Bu nedenle etiket biçimi (`**Bilgi Kutusu · ...**` bold lead) tutarlı tutulmalıdır.

---

## §5 — Görselleştirme Talimatları Yönergesi (ZORUNLU — Gate G67)

Markdown rapor daha sonra görselleştirilerek render edileceğinden, metin içinde tasarım aşamasına yönelik görselleştirme talimatları bulunur. **Kritik kısıt:** bu talimatlar yalnızca tasarımcıya yönlendirmedir ve **nihai rapor metnine girmez.**

### §5.1 Mekanik — HTML yorumu zorunluluğu

Tüm görselleştirme talimatları **HTML yorumu** olarak yazılır. HTML yorumları:
- Markdown HTML'e render edildiğinde **görünmez** (tarayıcıda gösterilmez) — yani nihai okur-yüzlü ürüne **hiçbir koşulda girmez**.
- Tasarım/render boru hattı tarafından ham markdown okunarak **okunabilir**.
- Önemsizce ayıklanabilir.

Bu, "talimatların nihai metne girmemesi" gereksinimini **savunma-derinliğiyle** karşılar: yorum ayıklanmasa bile render'da görünmez; ayrıca render boru hattı (§8) tüm `<!-- VIZ... -->` bloklarını üretimden önce siler.

### §5.2 Kanonik biçim

**Tek satırlık talimat:**

```markdown
<!-- VIZ: tip=<grafik-türü>; veri=<hangi tablo/paragraf/değerler>; eksen=<x: ..., y: ...>; vurgu=<...>; not=<tasarımcıya kısa yönlendirme> -->
```

**Blok talimat (uzun yönlendirmeler için):**

```markdown
<!-- VIZ-BLOCK
tip: timeline
baslik: FDA/EMA onay kronolojisi
veri: §3 tablosundaki onay tarihleri (8 öğe)
eksen: yatay zaman ekseni 2017–2025
vurgu: ilk-sınıf onayları farklı renkle işaretle
stil: Carbon kategorik palet; yoğunluk yerine sıralama önemli
not: Tarih hassasiyeti tier'ı korunsun; yalnızca yıl bilinen öğelerde ay gösterme
VIZ-BLOCK -->
```

### §5.3 Yerleşim ve içerik kuralları

- **Bitişiklik:** Her VIZ talimatı, ilgili olduğu verinin (tablo, paragraf, değer kümesi) **hemen yanına** yerleştirilir; böylece tasarımcı bağlama sahip olur.
- **Okuyucu-bağımsızlık:** VIZ talimatı, okuyucunun ihtiyaç duyduğu **hiçbir bilgiyi içermez** — yalnızca bir üretim yönergesidir. Talimatta yer alan bir bilgi okuyucu için gerekliyse, o bilgi ayrıca düzyazıda/tabloda bulunmalıdır.
- **Görünür düzyazıda yankılanmama:** VIZ talimatlarının içeriği görünür metinde **özetlenmez veya tekrarlanmaz** ("aşağıda bir grafik göreceksiniz" gibi ifadeler kullanılmaz; grafiğin kendisi render'da oluşturulur).
- **Generic-by-default uyumu:** VIZ talimatları da tüm dosya gibi generic-by-default disiplinine tabidir; kullanıcı/işveren adı veya iç bağlam **içermez** (validator tüm metni, yorumlar dâhil tarar).

### §5.4 Grafik türü kataloğu (tasarımcıya öneri sözlüğü)

`tip=` alanında kullanılabilecek yaygın türler ve ne zaman uygun oldukları:

| `tip` | Ne zaman | Tipik pharmaintel verisi |
|---|---|---|
| `bar` / `horizontal-bar` | Kategoriler arası büyüklük karşılaştırması | Pazar payı, yıllık satış, örneklem büyüklükleri |
| `grouped-bar` | İki boyutlu kategorik karşılaştırma | Ülkeler × yıllar satış; ürünler × endikasyonlar |
| `stacked-bar` | Bütünün bileşenleri | Gelir kırılımı, faz dağılımı |
| `line` | Zaman içinde trend | Satış trajektörisi, erozyon eğrisi |
| `timeline` / `gantt` | Kronolojik olaylar / katalizör takvimi | Onay kronolojisi, PDUFA/CHMP takvimi |
| `flow` / `sankey` | Süreç/akış/dönüşüm | Tedavi sırası, hasta hunisi, klinik geliştirme akışı |
| `donut` / `pie` | Tek boyutlu pay (dikkatli kullanın) | Tek bir pazarın paydaş payı |
| `heatmap` | İki-boyutlu yoğunluk/eşleşme | Eşdeğer grup doygunluğu, ATC × üretici |
| `waterfall` | Kümülatif artış/azalış | Fiyat tavanı türetimi (innovator → jenerik → marj) |
| `comparison-table` | Yan-yana çok-öznitelikli karşılaştırma | Head-to-head ürün karşılaştırması |
| `map` / `choropleth` | Coğrafi dağılım | Cross-country pazar büyüklüğü (36 ülke) |
| `forest-plot` | Etki büyüklüğü + GA görselleştirmesi | Alt grup analizleri, meta-sentez |

> **Yöntem Notu · VIZ talimatları render'a bir öneridir, emir değil**
>
> VIZ talimatları sonraki tasarım sürecine yalnızca bir **yönlendirme** sağlar; nihai grafik seçimi ve estetiği tasarımcının/render boru hattının kararıdır. Bu nedenle talimatlar "öneri" dilinde yazılır ve aşırı kısıtlayıcı olmaktan kaçınılır.

---

## §6 — İç Denetim Kaydının Yalıtımı

Bu bölüm, Katman B'nin (iç makine) okur-yüzlü üründen nasıl yalıtıldığını detaylandırır.

### §6.1 Render-dışı sentinel sarmalama

Katman B, birleşik markdown dosyasının **sonunda**, şu sentinel çiftiyle sarmalanır:

```markdown
<!-- RENDER:EXCLUDE-FROM-HERE -->

## Ek — İç Denetim ve Sağlama Kaydı (render dışı)

> Bu ek, raporun bütünlük denetimi ve provenans kaydı içindir; okur-yüzlü nihai üründe yer almaz.

## Provenance Disclosure
... [4-parçalı madde damgaları, kaynak türleri] ...

## Confidence Disclosure
... [H/M/L/U güven dağılım tablosu] ...

## Triangulation Notes
... [çatışma çözümleri, hiyerarşi rütbeleri] ...

## Auto-Trigger Disclosure
... [yüklenen katmanlar + gerekçeler] ...

G22 Generic-By-Default audit (forward + backward) sonucu: Tüm 8 kontrol PASS
(validator: scripts/validate-report-discipline.py invocation YYYY-MM-DD).

<!-- RENDER:EXCLUDE-TO-HERE -->
```

Render boru hattı (§8), iki sentinel arasındaki her şeyi üretimden önce siler.

### §6.2 Okur-yüzlü "Yöntem ve Kapsam" — Katman A'daki temiz karşılık

Katman B'deki teknik makinenin okuyucu-değerli kısmı (kaynak kategorileri, iki-kaynak ilkesi, sınırlılıklar), Katman A'da **okuyucu-dostu düzyazıyla** sunulur. Bu, gövdedeki tek metodoloji ifadesidir ve **iç makine terimleri içermez**:

```markdown
## Yöntem ve Kapsam

Bu rapor, birincil ve açık erişimli kaynaklara dayanmaktadır: ABD FDA ve Avrupa İlaç Ajansı (EMA) düzenleyici kayıtları, ClinicalTrials.gov çalışma tescilleri, SEC EDGAR mali bildirimleri ve hakemli literatür. Her maddi bulgu, en az iki bağımsız kaynakla teyit edilmeye çalışılmış; teyit düzeyi farklılık gösteren bulgular metinde açıkça belirtilmiştir. Ticari analiz platformlarına (örneğin abonelik gerektiren küresel satış veri tabanları) erişilememiş; bunun yarattığı boşluklar Sınırlılıklar bölümünde belgelenmiştir.

**Veri kesim tarihi:** YYYY-AA-GG. Bu tarihten sonraki gelişmeler rapora yansıtılmamıştır.
```

**Yasak (Katman A'da):** "validator", "G22", "gate", "kontrol PASS", "hiyerarşi rütbesi", "scripts/validate-report-discipline.py", "G22-OVERRIDE", "forward/backward audit" gibi iç-makine terimleri okur-yüzlü gövdede **geçmez**. Bunlar yalnızca Katman B'dedir.

### §6.3 Tek-dosya mı, refakat dosyası mı?

İki yerleşim seçeneği geçerlidir:

- **Tek dosya (varsayılan):** Katman A + sentinel-sarmalı Katman B aynı `.md` dosyasında. Validator bu birleşik dosya üzerinde çalışır. Render boru hattı sentinel arası bölgeyi siler.
- **Refakat dosyası:** Kullanıcı yalnızca temiz teslimat isterse, Katman B ayrı bir `*-denetim-kaydi.md` dosyasına alınır; temiz kopya tek başına teslim edilir. Bu durumda validator, denetimi her iki dosyanın birleşimi üzerinde yürütür.

### §6.4 Validator'ın çalışması (değişmez)

Step 5b'deki zorunlu validator çağrısı **aynen korunur** — yalnızca taranan dosya artık Katman A + Katman B birleşimidir (veya refakat dosyasıysa ikisinin birleşimi). Validator:
- Tüm metni (HTML yorumları ve sentinel-sarmalı ek dâhil) generic-by-default sızıntıları için tarar — bu, VIZ talimatlarının ve denetim kaydının da leak-free olmasını güvence altına alır.
- Açıklama bloklarını (`## Provenance Disclosure` vb.) Katman B içinde bulur ve denetler.

---

## §7 — Atıf ve Kaynak Sunumu

Okur-yüzlü temiz kopya, dergi-biçimi atıf disiplini uygular.

**Metin içi atıf:**
- Her maddi iddiaya, kaynağına çözümlenen bir **üst-simge/köşeli-parantez atıf işareti** eklenir: "Çalışma, genel sağkalımda anlamlı uzama göstermiştir[3]."
- Kritik sayısal değer sınıfları için (etki büyüklükleri ve %95 GA, p-değerleri, örneklem büyüklükleri, düzenleyici tarihler, mali rakamlar, kutulu-uyarı güvenlik oranları) atıf işareti **sayının kendisine** iliştirilir; böylece bir okuyucu herhangi bir kritik sayıyı kaydırmadan birincil kaynağına izleyebilir (v1.0.1 inline citation discipline — korunur).

**Kaynaklar bölümü (sonda):**
- İlk göründükleri sırada numaralandırılır.
- Her künye tam atıf sağlar: kaynak adı/türü, kanonik kimlik (DOI, NCT ID, 8-K accession, EPAR URL, patent no), erişim tarihi.
- İsteğe bağlı olarak her künyede güven düzeyi parantezle belirtilebilir; ancak ayrıntılı H/M/L/U dağılımı Katman B'deki Güven Dağılım Tablosu'ndadır.

```markdown
## Kaynaklar

**[1]** FDA Drugs@FDA — BLA 761239, Enhertu (trastuzumab deruxtecan) onay mektubu.
- URL: https://www.accessdata.fda.gov/drugsatfda_docs/appletter/...
- Erişim: YYYY-AA-GG · Kullanıldığı bölümler: §2.1, §3.4

**[2]** Modi S ve ark. — "Trastuzumab Deruxtecan in HER2-Low Breast Cancer".
- Dergi: NEJM (2022) · DOI: 10.1056/NEJMoa2203690
- Erişim: YYYY-AA-GG · Kullanıldığı bölümler: §3.2
```

**İlke (kullanıcı önceliği — referans açıklığı):** Hiçbir maddi iddia, atıfsız bırakılmaz. Bir iddia yalnızca ikincil kaynağa veya tek kaynağa dayanıyorsa, bu durum metinde açıkça ifade edilir.

---

## §8 — Render Boru Hattı Sözleşmesi (Downstream Handoff)

Okur-yüzlü temiz kopya, görselleştirme/yayın için downstream skill'lere devredildiğinde aşağıdaki sözleşme geçerlidir.

**Devralan skill'lerin (carbon-html-report, carbon-pptx) yükümlülükleri:**
1. **VIZ yorumlarını işle ve sil:** Tüm `<!-- VIZ: ... -->` ve `<!-- VIZ-BLOCK ... VIZ-BLOCK -->` bloklarını oku, ilgili grafikleri/diyagramları üret, ardından bu yorumları **nihai çıktıdan çıkar**.
2. **Render-dışı eki sil:** `<!-- RENDER:EXCLUDE-FROM-HERE -->` ile `<!-- RENDER:EXCLUDE-TO-HERE -->` arasındaki Katman B'yi nihai üretimden **tamamen çıkar**.
3. **Bilgi kutularını yükselt:** `Bilgi Kutusu` / `Yöntem Notu` / `Dikkat` etiketli blok-alıntıları, tasarım sistemi callout bileşenlerine (Carbon aside/notification) dönüştür.
4. **Atıf işaretlerini ve Kaynaklar'ı koru:** Numaralı atıflar ve Kaynaklar bölümü nihai üründe **kalır**.

> **Dikkat · Savunma derinliği**
>
> Bir downstream skill, sentinel/VIZ sözleşmesini bilmiyorsa bile okur-yüzlü ürün bozulmaz: HTML yorumları zaten render'da görünmez. Sentinel sarmalama, yorumların ayıklanmasını **kolaylaştırır** ama görünürlüğü engellemenin **tek** mekanizması değildir. Bu, "iç talimatların ve denetim kaydının nihai metne girmemesi" gereksinimini iki bağımsız katmanla güvence altına alır.

**markdown önizlemesi notu:** Ham markdown bir düz-metin editöründe açıldığında VIZ yorumları ve sentinel-sarmalı ek görünür; ancak bu "çalışma kopyasıdır", "sunulan rapor" değildir. Sunulan (render edilmiş) rapor her zaman temizdir.

---

## §9 — Sunum Öncesi Kontrol Listesi (Gate G66 + G67 + G68 eşlemesi)

Raporu teslim etmeden önce Claude şu kontrolleri sessizce yürütür:

**Katman ayrımı (G66):**
- [ ] Okur-yüzlü gövdede (Katman A) hiçbir iç-makine terimi yok mu? ("validator", "G22", "gate", "rütbe", "kontrol PASS", "scripts/", "override", "audit")
- [ ] Madde-bazlı provenans damgaları, güven dağılım tablosu, triangülasyon notları ve G22 satırı Katman B'ye (render-dışı sentinel arası veya refakat dosyası) taşındı mı?
- [ ] Açıklama bloklarının başlıkları (`## Provenance Disclosure` vb.) gerçek `##` başlık olarak korundu mu? (validator uyumu)

**Görselleştirme talimatları (G67):**
- [ ] Tüm görselleştirme talimatları HTML yorumu (`<!-- VIZ... -->`) biçiminde mi?
- [ ] Talimatlar ilgili verinin yanında mı ve görünür düzyazıda yankılanmıyor mu?
- [ ] Talimatlar okuyucu-bağımsız mı (içerdikleri okuyucu-değerli bilgi ayrıca metinde de var mı)?

**Bilgi kutuları ve kısaltmalar (G68):**
- [ ] Kısaltmalar ve Tanımlar Dizini rapor başında mevcut mu?
- [ ] Anahtar terimler ilk geçişte açıldı/tanımlandı mı; gerekli yerlerde bilgi kutusu eklendi mi?
- [ ] `Yöntem Notu` kutuları iç-makine terimi içermiyor mu?

**Dil ve akış (G2/G3 yönergeleri):**
- [ ] Cümle yapıları eksiksiz mi; bilimsel, nesnel ses kullanıldı mı?
- [ ] Her maddi iddia numaralı atıfla destekleniyor mu; Kaynaklar bölümü tam mı?
- [ ] Bölümler köprü cümleleriyle bağlanıyor; tablolar çerçeveleme cümleleriyle sunuluyor mu?
- [ ] Yöntem ve Kapsam, okuyucu-dostu düzyazıyla yazıldı; veri kesim tarihi belirtildi mi?

Bu kontroller başarısızsa, ilgili içerik düzeltilir ve liste yeniden yürütülür. Hiçbir madde başarısızken rapor teslim edilmez.

---

## §10 — Çalışılmış mikro-örnek (önce/sonra)

**ÖNCE (v8.0.0 — makine gövdeye karışmış, okuyucu için gürültülü):**

```markdown
### Bulgu: Birincil endpoint anlamlı

T-DXd, DESTINY-Breast04'te PFS'de anlamlı iyileşme gösterdi (HR 0,50).

> — **Source:** Peer-Reviewed (NEJM) + Primary Regulatory (FDA label)
> — **ID/URL:** DOI: 10.1056/NEJMoa2203690 ; BLA 761139
> — **Accessed:** 2026-06-12
> — **Confidence:** High

G22 Generic-By-Default audit sonucu: 8/8 PASS (validator invocation 2026-06-12).
```

**SONRA (v8.1.0 — Katman A temiz + Katman B'ye taşınmış makine + VIZ talimatı):**

*Katman A (gövde — render edilir):*

```markdown
### HER2-düşük meme kanserinde birincil etkililik

DESTINY-Breast04 çalışması, trastuzumab deruxtecanın progresyonsuz sağkalımda
(progression-free survival, PFS) klinik olarak anlamlı bir iyileşme sağladığını
göstermiştir: tehlike oranı 0,50 (%95 GA 0,40–0,63; p<0,001)[1][2]. Bu bulgu,
hem hakemli yayında hem de düzenleyici etikette tutarlı biçimde yer almaktadır.

> **Bilgi Kutusu · Progresyonsuz sağkalım (PFS)**
>
> Tedavi başlangıcından, hastalığın ilerlemesine veya ölüme kadar geçen süre.
> Onkolojide sık kullanılan ve düzenleyici onaylara temel oluşturabilen bir
> ara sonlanım noktasıdır.

<!-- VIZ: tip=forest-plot; veri=DB-04 birincil ve anahtar alt grup HR'leri (HR 0,50; %95 GA 0,40–0,63); eksen=x: HR log ölçek 0,25–1,0; vurgu=birincil sonucu kalın işaretle; not=GA çizgileri ve referans çizgisi (HR=1) gösterilsin -->
```

*Katman B (render-dışı ek — render edilmez):*

```markdown
<!-- RENDER:EXCLUDE-FROM-HERE -->
## Provenance Disclosure
- Birincil etkililik (PFS HR 0,50): Source: Peer-Reviewed (NEJM) + Primary Regulatory (FDA label) · ID: DOI 10.1056/NEJMoa2203690 ; BLA 761139 · Accessed: 2026-06-12 · Confidence: High
...
G22 Generic-By-Default audit (forward + backward) sonucu: Tüm 8 kontrol PASS (validator: scripts/validate-report-discipline.py invocation 2026-06-12).
<!-- RENDER:EXCLUDE-TO-HERE -->
```

Okuyucu yalnızca temiz, atıflı, bilgi-kutusuyla desteklenmiş bilimsel metni görür; grafik render'da oluşturulur; tüm provenans ve denetim disiplini Katman B'de eksiksiz korunur.

---

> **Özet:** Bu standart, pharmaintel'in kanıt-toplama bütünlüğünü **azaltmadan**, çıktının *sunulan* hâlini bir hakemli dergi makalesi niteliğine yükseltir. İki katman (temiz kopya + render-dışı denetim kaydı), bilgi kutuları, HTML-yorumu görselleştirme talimatları ve dergi-biçimi atıf disiplini birlikte; hem okuyucu hem denetçi için en uygun çıktıyı üretir.
