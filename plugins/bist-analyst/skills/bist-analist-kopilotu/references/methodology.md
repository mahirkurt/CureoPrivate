# BIST Analist Kopilotu — Analitik Metodoloji

Bu belge, `bist-analist-kopilotu` becerisinin temel akıl yürütme yöntemini tanımlar. Beceri, dört çalışma kipinde (tek-hisse derin analiz, haftalık tarama, KAP olay yorumu, izleme listesi gözetimi) **tek bir gerekçelendirilmiş brifing** üretir. Bu metodoloji, brifingin nasıl kurulduğunu, kanıtların nasıl zincirlendiğini ve sonuçların güven düzeyiyle nasıl çerçevelendiğini düzenler.

> **Sınır (değişmez):** Bu beceri **karar-destek** üretir, **yatırım tavsiyesi vermez.** Kişiselleştirilmiş al/sat yönlendirmesi, kişiye özel hedef fiyat veya portföy tahsisi önerisi üretilmez. Her sonuç bir **güven düzeyi** ve bir **karşıt senaryo** ile birlikte sunulur.

---

## 1. Kanıt-zinciri disiplini (evidence-chain discipline)

Brifingteki her vargı, izlenebilir bir kanıt zincirine dayanmalıdır. Hiçbir sayısal iddia, kaynağı ve zamanı belirtilmeden metne girmez.

### 1.1 Zincir kuralı

Her sonuç şu üçlüye geri izlenebilir olmalıdır:

| Bileşen | Açıklama |
|---|---|
| **Veri çağrısı** | Değerin alındığı `borsa` veri kaynağı / fonksiyon (ör. teknik tarayıcı, finansal oranlar, sektör karşılaştırması, KAP/haber akışı). |
| **Değer** | Alınan ham büyüklük; birimiyle birlikte (TL, %, kat, adet). |
| **Zaman damgası** | Verinin geçerlilik anı (*as-of* tarihi). Fiyat verisi **gün-sonu (EOD)/gecikmeli** olduğundan ilgili işlem gününü taşır. |

Bir iddiayı destekleyecek kanıt yoksa, iddia brifinge **girmez**; bunun yerine "veri mevcut değil / doğrulanamadı" notu düşülür.

### 1.2 Üçüncü-taraf hedefleri

`get_analyst_data` üzerinden gelen üçüncü-taraf analist hedef fiyatları ve tavsiyeleri **"doğrulanmamış bağlam"** statüsündedir. Bunlar:

- Becerinin kendi vargısı olarak sunulamaz,
- Hedef fiyat türetmek için kullanılamaz,
- Yalnızca "piyasa beklentisi/konsensüs şu yönde, doğrulanmadı" çerçevesiyle aktarılabilir.

### 1.3 Determinist yardımcılar

Sayısal türetmelerin yeniden-üretilebilir olması için beceri, paketlenmiş Python yardımcılarını çağırır. Bu betikler, ham veriyi deterministik biçimde işler; serbest yorum yapmaz:

| Betik | Görev |
|---|---|
| `scripts/technical_helpers.py` | RSI, MACD, hareketli ortalamalar (SMA/EMA), Bollinger bantları, Supertrend, T3, ATR. |
| `scripts/technical_plus.py` | Teknik duruş puanı, RSI/fiyat **ayrışması** (puanlanır), **göreli güç**, **boşluk (gap) maruziyeti**, çok-zaman-dilimli teyit (confluence), pivot seviyeleri. |
| `scripts/backtest_posture.py` | Teknik-duruş motorunun **look-ahead'siz öz-denetimi**: Spearman ρ / bilgi katsayısı (IC) / isabet / benchmark-göreli / boşluk ayrıştırması. |
| `scripts/financial_quality_score.py` | Temel kalite kompoziti (bkz. fundamental-methodology.md). |
| `scripts/macro_context.py` | Makro rejim sınıflandırması. |
| `scripts/sentiment_score.py` | KAP/haber duyarlılık skoru. |
| `scripts/kap_materiality.py` | KAP bildiriminin önemlilik (materiality) derecesi. |
| `scripts/brief_lint.py` | Nihai brifingin uyumluluk ve biçim denetimi. |
| `scripts/watchlist_diff.py` | İzleme listesi değişim çıkarımı (4. kip). |

---

## 2. Çok-zaman-dilimli teknik okuma

Teknik görünüm tek bir grafikten değil, **zaman dilimleri hiyerarşisinden** okunur. Mevcut veri **gün-sonu/gecikmeli** olduğundan, gün-içi mikro-yapı (emir defteri, tik-tik akış) **kapsam dışıdır**; ufuk günlük/haftalıktır.

### 2.1 Hiyerarşik okuma sırası

1. **Haftalık (1W) → ana eğilim (trend):** Birincil yön belirlenir. SMA200/SMA50 dizilimi ve Supertrend yönü haftalık çerçevede ana rejimi verir.
2. **Günlük (1d) → kurulum (setup):** Haftalık eğilim içinde günlük momentum, geri çekilme/kırılım ve oynaklık değerlendirilir.
3. **Teyit (confluence):** 4h/1h dilimler yalnızca **günlük kurulumu teyit** amacıyla okunur; bağımsız sinyal kaynağı değildir. Diller arası uyum arttıkça güven artar.

> Zaman dilimleri arasında **çelişki** varsa (ör. 1W yukarı, 1d aşağı), bu bir "ayrışma" notu olarak işaretlenir ve teknik duruş **nötr/zayıf** tarafına çekilir; uyum varmış gibi gösterilemez.

### 2.2 Dört teknik boyut

Mevcut tarayıcı göstergeleri (RSI, macd, close, change, volume, market_cap, sma_5/20/50/200, ema_20, bb_upper, bb_lower, supertrend_direction [1/-1], t3) dört boyuta eşlenir:

| Boyut | Göstergeler | Okuma |
|---|---|---|
| **Eğilim (trend)** | SMA dizilimi (5>20>50>200 = yukarı diziliş), Supertrend yönü, T3 eğimi | Fiyatın hangi yönde yapısal olduğunu verir. |
| **Momentum** | RSI, MACD | Hareketin gücü/hızı; aşırı alım-satım. |
| **Oynaklık (volatilite)** | Bollinger bant genişliği (bb_upper/bb_lower), ATR | Bant daralması = sıkışma; genişleme = hareket. |
| **Hacim (volume)** | volume, hacim-fiyat uyumu | Hareketin teyidi; düşük hacimli kırılım zayıftır. |

### 2.3 Göstergelerin "teknik duruşa" birleştirilmesi

Göstergeler tek tek değil, **istif (stack)** olarak okunur. `technical_plus.py` çoklu-dilim teyidini hesaplar; nihai etiket beş kademelidir:

| Teknik duruş | Tipik istif örüntüsü |
|---|---|
| **Güçlü yukarı** | SMA yukarı dizilişi + Supertrend +1 (1W ve 1d) + RSI sağlıklı (50–70) + MACD pozitif + hacim teyitli |
| **Zayıf yukarı** | Yukarı diziliş var fakat momentum yavaşlıyor (RSI düşüyor / MACD tepe yapıyor) veya hacim teyitsiz |
| **Nötr** | Karışık sinyaller; SMA'lar iç içe, Supertrend dilimler arası çelişkili, Bollinger sıkışması |
| **Zayıf aşağı** | Aşağı eğilim başlangıcı; SMA dizilişi bozuluyor, Supertrend −1'e dönüyor, RSI 50 altına sarkıyor |
| **Güçlü aşağı** | SMA aşağı dizilişi + Supertrend −1 (1W ve 1d) + MACD negatif + RSI zayıf + satış hacmi teyitli |

İstifteki göstergeler **çelişiyorsa**, duruş otomatik olarak orta kademeye (nötr veya zayıf) çekilir ve güven düzeyi düşürülür.

### 2.4 Ayrışma (divergence) ve yanlış sinyal tespiti — EOD sınırı

Gün-sonu veriyle çalışırken:

- **Ayrışma:** Fiyat yeni zirve/dip yaparken RSI veya MACD teyit etmiyorsa (negatif/pozitif uyumsuzluk) işaretlenir. **v1.1.0'dan itibaren ayrışma yalnız işaretlenmez, teknik duruş puanına da katkı verir** (`trend_posture`: bullish +1 / bearish −1; bkz. §2.5). EOD veride ayrışma yalnızca **kapanış serileri** üzerinden okunabilir; gün-içi salınımlar görülmez, bu açıkça belirtilir.
- **Yanlış kırılım (false breakout):** Bollinger bandı veya seviye kırılımı **hacim teyidi olmadan** gerçekleşmişse, "teyitsiz kırılım — tek günlük EOD kapanışıyla doğrulanmadı" notu eklenir.
- **Tek-bar riski:** EOD veride tek bir günün uç kapanışı yanıltıcı olabilir; çok-dilim teyidi olmadan tek bara dayalı vargı kurulmaz.

### 2.5 Duruş puanının bileşenleri ve sinyal entegrasyonu (v1.1.0)

Teknik duruş, `trend_posture` içinde **şeffaf, gerekçeli bir puan istifinden** üretilir; her bileşenin katkısı `contributions` altında döner (kara-kutu değil). Çekirdek referans ağırlığı **8.0**'dır:

| Bileşen | Ağırlık | Okuma |
|---|--:|---|
| MA dizilimi | 2 | close vs sma20/50/200 + dizilim sırası |
| RSI bölgesi (**eğim-duyarlı**) | 1 | aşırı-satımdan yukarı kıvrılma cezayı nötrler; aşırı-alımdan dönüş katkıyı kısar |
| MACD histogram | 1 | işaret |
| Supertrend yönü | 2 | +1/−1 |
| T3 konumu | 1 | close vs T3 |
| Bollinger %B | 1 | bant içi konum |
| **Ayrışma** | 1 | bullish +1 / bearish −1 (§2.4) — *v1.1.0'da puana bağlandı* |
| **Göreli güç** | 1 | endeks serisi verilmişse rs_score (−1..+1) |

İki **mean-reversion / rejim düzeltmesi** v1.1.0'da eklendi:

- **Eğim-duyarlı RSI:** Saf seviye okuması, aşırı-satımdan (RSI ≤ 30) yukarı dönen bir kurulumu *zayıflık* sayarak şiddetli ortalamaya-dönüşü yapısal olarak ıskalıyordu. Artık RSI eğimi yukarıysa bu ceza nötrlenir; trend-takipçi kör nokta kapanır. (Eğim bilinmiyorsa klasik davranış korunur.)
- **Göreli güç (relative strength):** Mutlak duruş, herkesin yükseldiği bir haftada hisse-seçim becerisini ölçemez. Göreli güç, hareketin ne kadarının endeksi GERÇEKTEN yendiğini ölçer (son ~13 bar, hisse getirisi − endeks getirisi) ve "yükselen dalga"yı sinyalden ayırır. Yalnız `enrich_snapshot`'a endeks serisi verildiğinde devreye girer.

**Boşluk (gap) maruziyeti — EOD kör noktası.** `gap_exposure`, son barların seans-arası boşluk istatistiğini üretir. EOD motoru bir önceki kapanış ile bu açılış arasındaki sıçramayı **öngöremez**; bir Cuma taramasının hafta sonu gap'ini göremeyeceği şeffaflaştırılır. Bir kurulumun getirisinin büyük kısmı boşluğa bağımlıysa, bu açıkça not edilir (öngörü iddiası değil, dürüstlük katmanı).

**Kapsam-güven bağı.** Etkin ağırlık çekirdek 8.0'ın belirgin altındaysa (ör. kısa seride MACD/T3 düşerse) duruş az göstergeye dayanır; `low_coverage` bayrağı kalkar ve **güven bir kademe düşürülür**. Bu yüzden Adım 0'daki uzun-aralık haftalık çekim (≈52 bar) önemlidir.

**Kalibrasyon erişimi (v1.1.1).** RSI eğim penceresi ve RS lookback `enrich_snapshot` imzasına opsiyonel parametre olarak açıldı (walk-forward kalibrasyonu için; varsayılanlar 3/13 korunur, davranış değişmez).

**Walk-forward kalibrasyon (v1.1.2).** `scripts/walkforward_calibrate.py`, bu iki parametreyi bir ızgarada ({2,3,5}×{8,13,21}) **sızıntısız** ve **çok-rejimli** tarar (her cell'i `backtest_posture`'a delege eder; tek pencere zayıf testtir). İlk çalıştırma — 14 BIST hissesi + XU100, 36 aylık (bölünme-düzeltmeli) bar, 12 rejim penceresi — varsayılan **3/13'ü değiştirmek için gerekçe bulamadı:** en iyi cell ile varsayılan arasındaki ortalama Spearman farkı (~0,04) rejim-içi gürültünün (σ≈0,29) ~0,15 katı ve SE-ortalamanın ~0,5 katıdır (z≈0,5, anlamsız); "en iyi" cell kesitler arası **kayar** (RS-açık çok-rejim → (2,8); tek-pencere → look=21; (2,8) tek-pencerede en kötü) — bu sinyal değil aşırı-uyum imzasıdır; ve hiçbir cell pozitif mutlak isabet taşımaz (tüm ρ<0, isabet 0,357<0,5). **Sonuç: varsayılan korunur (kanıta dayalı), değiştirilmez.** ÖNEMLİ sınır: aylık bar SMA50/200'ü tanımsız bırakır (kapsam-sınırlı duruş) ve 1-aylık ufuk motorun günlük/haftalık tasarımıyla uyumsuzdur; bu kalibrasyon motoru **eksik-test eder**.

**Günlük katman kalibrasyonu (v1.1.3).** `scripts/stitch_daily.py` (günlük-veri toplayıcı), Borsa'nın ≤30-günlük dilimlerini birleştirerek günlük frames üretir (Borsa çözünürlüğü aralık-uzunluğuyla ölçeklenir: ≤30g→günlük, ~3ay→haftalık, ~1yıl→aylık; uzun günlük seri **dilimlenip birleştirilmelidir**). Aylık katmanın kapsam sınırını gidermek için günlük katmanda yeniden koşuldu: 8 BIST hissesi + XU100, **101 günlük (bölünme-düzeltmeli) bar** (2026-01-21…06-19, SMA50 artık tanımlı; SMA200 hâlâ değil), motor-ufku (5 ve 10 işlem günü), 10 rejim. Sonuç **aylık kararı bozmadı:** varsayılan **3/13 hiçbir kesitte yenilmedi** (h=10'da eş-en-iyi, fark=0,000; h=5'te tek-en-iyi; RS-kapalı'da win=3 tüm rejimlerde rank-1). Aylık verinin (2,8) imâsı günlükte düzeldi. **Dürüst çerçeve (çekişmeli denetimli):** bu "doğrulama" değil **alt-sınır-altı-olmama (non-inferiority)** bulgusudur — cell başına SE (≈0,15) tüm ızgara açıklığından (≈0,09) büyüktür ve 10 pencere **örtüşür** (otokorelasyon → etkin N≪10), dolayısıyla hiçbir cell ayırt edilemez; "eş-en-iyi" = ayrımsızlık. Ayrıca **tüm ρ negatif** kalır (zayıf/ters kesitsel ilişki, 5–10 günde) — bu **parametre sorunu değil, motorun mutlak öngörü gücüne dair ayrı bir uyarıdır** ve bağımsız incelenmelidir. **Karar: varsayılan korunur** (değiştirmek için kanıt yok). Varsayılanı değiştirmeyi/motoru aklamayı gerekçelendirecek şey: **örtüşmeyen** pencereler, daha geniş kesit (N≫8), SMA200 kapsamı (≥250 günlük bar), gerçek out-of-sample bölme ve z≳2 ile pozitif-mutlak-IC.

**Motor-skill çalışması (v1.1.4) — duruşun MUTLAK öngörü gücü.** Negatif-ρ uyarısı parametre değil **motor** sorusudur; `scripts/skill_study.py` bunu istatistiksel güçle yanıtlar: **örtüşmeyen** (bağımsız) bloklar (t adımı = ufuk → ardışık ileri-getiri pencereleri çakışmaz), **SMA200 kapsamlı** veri, sabit varsayılan (3/13), ve **Student-t** (df=K−1; küçük-K kalın kuyruk doğru hesaplanır, normal-yaklaşım değil). Koşum: 12 BIST hissesi + XU100, **286 günlük (bölünme-düzeltmeli) bar**, ufuk 5/10/20 işlem günü. **Sonuç: hiçbir ufukta sıfırdan ayırt edilebilir skill yok** (ρ̄ = −0,12/−0,16/−0,02; tüm **p ≥ 0,20**); RS-açık ≈ RS-kapalı. **Dürüst çerçeve (çekişmeli kalibreli) — kanıt-yokluğu, yokluğun-kanıtı DEĞİL:** çalışma *güçlü* skili (|ρ|≳0,20, h=5'te; %95 GA ≈ [−0,32, +0,07]) **dışlar**, ama *zayıf* skili sıfırdan ayıramaz (h=10/h=20 saptama tabanı 0,43/0,78 — örtüşmeme bağımsızlığı K'yı/güçü düşürür). Hafif-negatif eğilim **gürültü içindedir** — sinyal değil hipotezdir (olası kısa-ufuk ortalamaya-dönüş / bid-ask sıçraması; bağımsız/daha büyük örneklemde test edilmeli). **Çıkarım:** duruş skoru kesitsel getiri-sıralama *kanıtlanmış* bir üstünlük değil; **betimsel/yapısal** (şeffaf, denetlenebilir teknik-durum + senaryo çerçevesi) olarak konumlanır — bu, eklentinin **karar-destek (tahmin değil)** ilkesini pekiştirir. Zayıf bir skilin VAR olup olmadığını saptamak için: N≫12, daha uzun/bağımsız tarih, gerçek OOS, daha çok bağımsız blok.

**Çok-örnek havuz (v1.1.5) — çapraz-piyasa + metodolojik ders.** `skill_study.py --pool` birden çok örneğin örtüşmeyen bloklarını havuzlar (güç ↑). Çapraz-piyasa koşum: 9 BIST + 9 ABD hissesi, ~286-288 günlük bar, aynı ~14-ay penceresi → **hiçbir ufukta pozitif kesitsel skill kanıtı yok** (h=5 ρ̄=−0,11, p=0,09 — anlamlı DEĞİL; isabet 0,493 = yazı-tura → yönsel içerik yok; h=10/20 işaret hakkında bilgisiz). **Önemli ders (çekişmeli denetimle):** aynı takvim penceresindeki farklı piyasaları havuzlamak bağımsızlık VERMEZ — ortak küresel risk faktörü blokları çağdaş ilişkilendirir, **etkin K≈17 (34 değil)**, SE küçümsenir, gerçek p daha büyüktür (çoklu-ufuk multiplisitesiyle ≈0,25). Yani hafif-negatif eğilim "çapraz-piyasa tekrarlanmış sinyal" DEĞİL, gürültüdür; pozitif skill "dışlanmış" da denemez (h=5 CI üst ucu ~sıfırda, h=10/20'de açık). **Net konum: duruşun kısa-ufuk getiriyle ilişkisi istatistiksel olarak sıfırdan ayırt edilemez → betimsel/yapısal.** Gerçek güç için doğru yol **çağdaş-olmayan** (farklı dönem) bağımsız örnekler + multiplisite düzeltmesi; çapraz-piyasa aynı-pencere değil. (`--pool` docstring'i bu bağımsızlık tuzağını uyarır.)

**Çok-dönem (zaman-bağımsız) BIST — kesin koşum (v1.1.6).** Metodolojik olarak doğru güç tasarımı: tek, sürekli ve **derin** günlük seri → bloklar farklı takvim zamanlarında olduğundan **gerçekten bağımsız** (çapraz-piyasa aynı-pencere tuzağı yok). 8 BIST hissesi + XU100, **615 günlük (bölünme-düzeltmeli) bar** (2024-01…2026-06, ~2,5 yıl), SMA200 tam kapsamlı, h=5'te **K=83 örtüşmeyen bağımsız blok**. Sonuç: **hiçbir ufukta skill yok** (tüm p≥0,38; Šidák×3 ≥0,76); isabet ~0,49–0,50 (yazı-tura). **Kritik:** önceki kısa/çapraz koşumlardaki hafif-negatif eğilim **kayboldu** (h=5 artık ρ̄=+0,02; işaret ufuklar arası değişiyor) → gürültü olduğu doğrulandı (gerçek güç altında yok oluyor). **En sıkı sınır, sıfırda merkezli:** h=5 %95 GA **[−0,07, +0,11]** → artık bu *yokluğun-kanıtı*na yakın: anlamlı |ρ|>~0,11 hem POZİTİF hem NEGATİF yönde dışlanır, nokta tahmini ~0. **Net (kesin): duruşun kısa-ufuk kesitsel getiriyle ilişkisi sıfırdan ayırt edilemez ve küçük bir banta (|ρ|<~0,11) sınırlıdır → kesinlikle betimsel/yapısal.** Kalan tek artık: çok-zayıf |ρ|<~0,1 kesin dışlanmaz ve bu tek bir ~2,5-yıllık BIST dönemidir (tek piyasa/çağ); daha da daraltmak için daha çok yıl/piyasa-çağı gerekir — ama pratik sonuç (pozitif öngörü üstünlüğü yok) sağlamdır.

**Betimsel-değer çalışması (v1.1.7) — duruş ↔ ileri OYNAKLIK + TREND/YATAY rejim.** Önceki üç katman duruşun ileri **getiri-yönü** sorusunu kapattı (skill yok). Bu çalışma (`scripts/regime_study.py`) FARKLI bir ekseni sınar: duruş kategorilerinin **betimsel/yapısal** değeri — getirinin yönü değil **karakteri**. İki birincil test: **vol_extreme** (duruş aşırılığı |score_norm| ↔ ileri gerçekleşmiş oynaklık, **mevcut-vol kontrollü kısmi Spearman** — oynaklık otokorele olduğundan kontrolsüz test sahte-pozitif verir) ve **regime_trend** (|score_norm| ↔ ileri **efficiency-ratio**: trendli mi yatay/çalkantılı mı). İki ikincil: vol_asimetri (işaretli skor ↔ ileri-vol; kaldıraç etkisi) ve vol-kovan η² (varsayımsız çapraz-kontrol). `skill_study`'nin örtüşmeyen-blok + Student-t makinesi ve `backtest_posture` skorlama yolu **yeniden kullanılır; motor değişmez**. Koşum: 8 BIST hissesi + XU100, **573 hizalanmış günlük bar** (ortak-tarih kesişimi → blok t = tüm isimler için AYNI takvim günü; 2024-01…2026-04), SMA200 tam, ufuk 5/10/20 (K=74/37/18). **Bulgular (çekişmeli denetimli, dürüst): (1) Vol büyüklüğü — BETİMSEL DEĞER YOK.** vol_extreme tüm ufuklarda sıfırdan ayırt edilemez (p≥0,36; nokta tahmini ~0); vol-kovan η²≈0 bunu doğrular → duruş aşırılığı, **mevcut-vol temelinin ötesinde** ileri-vol bilgisi taşımıyor (motorun getiri-eksenindeki betimsel-değil-tahmin konumu **vol ekseninde de** doğrulanır). **(2) Trend/yatay rejim — çoğunlukla null, tek Šidák-aşan sinyal.** regime_trend h=5/h=10'da null (p=0,38/0,94); h=20'de **anlamlı NEGATİF** (ρ̄=−0,24; p=0,004; **p_Šidák=0,024** — 6-test ailesinde bile hayatta kalır): aşırı aylık duruşlar daha **çalkantılı/ortalamaya-dönen** (trendli DEĞİL) bir ileri-pencere önceler. **Temkinli yorum:** en düşük-güç ufku (K=18), kısa ufuklarda yok → **mütevazı bir ~1-aylık ortalamaya-dönüş tellisi**; bağımsız dönemde tekrar (replikasyon) gerektiren *geçici* bir betimsel gözlem, alım-satım sinyali DEĞİL. **(3) Vol asimetrisi (ikincil, düzeltilmemiş):** h=5/h=10'da tutarlı yönde zayıf POZİTİF (ρ̄≈+0,13/+0,18; ham p≈0,02) → yukarı-duruşlar hafifçe daha çok ileri-vol önceler (klasik kaldıraç etkisinin TERSİ); çoklu-karşılaştırma ile doğrulanmadı, betimsel ipucu. **Net:** duruşun ileri-vol büyüklüğüyle ilişkisi (mevcut-vol kontrollü) sıfırdan ayırt edilemez; tek sağlam (Šidák-aşan) sinyal aylık ufukta mütevazı bir ortalamaya-dönüş eğilimidir → motor **betimsel/yapısal** konumunu korur, **karar-destek (tahmin değil)** ilkesi pekişir. h=20 bulgusu için doğru sonraki adım: bağımsız dönem/piyasa-çağında `--pool` replikasyonu.

**Replikasyon — bağımsız era + havuz (v1.1.8).** v1.1.7'nin tek Šidák-aşan bulgusu (h=20 regime_trend ρ̄=−0,24, p_Šidák=0,024) **doğru yöntemle** sınandı: non-contemporaneous bağımsız ERA (çapraz-piyasa aynı-pencere DEĞİL — kendi dersimiz). İkinci era: aynı 8 BIST + XU100, **565 hizalanmış günlük bar (2021-08…2023-11)** — v1.1.7 penceresiyle (2024-01…2026-04) ÖRTÜŞMEZ → bloklar farklı takvim zamanlarında, **gerçek bağımsızlık**. **(1) h=20 sinyali REPLİKE OLMADI — yanlış-pozitifti.** era2 tek-başına regime_trend h=20 = **+0,13** (p=0,17; işaret TERS döndü); havuz (era1+era2, K=36) = **−0,05** (p=0,43; p_Šidák=0,97). → era1'deki −0,24, **tek-dönem gürültüsü / çoklu-karşılaştırma yanlış-pozitifi** (6 birincil hücreden biri tek bir dönemde Šidák'ı şans eseri geçebilir). Kesin: trend/yatay rejimde **betimsel ilişki YOK**. **(2) vol_extreme sağlam değil:** havuzda yalnız h=10 ham-anlamlı (+0,12, p=0,028) ama Šidák'ı geçmez (0,156) ve eralar arası tutarsız (era1 null, era2 +0,17) → mevcut-vol ötesinde **güvenilir** ileri-vol bilgisi yok (v1.1.7 doğrulanır). **(3) Tek REPLİKE OLAN düzenlilik — vol asimetrisi (ikincil):** h=5/h=10'da İKİ bağımsız erada da pozitif (era1 +0,13/+0,18; era2 +0,09/+0,09; havuz **+0,11 p=0,005 / +0,14 p=0,017**) → yukarı-duruşlar hafifçe daha çok ileri-vol önceler (klasik kaldıraç etkisinin TERSİ; "ralli oynaklığı" imzası). İkincil ve çoklu-karşılaştırma-düzeltilmemiş — ama **iki-era replikasyonu** bunu bulunan en güvenilir betimsel düzenlilik yapar; yine de küçük etki, alım-satım sinyali DEĞİL. **Havuz geçerliliği:** render'daki "aynı-pencere farklı-piyasa → bağımsız değil" uyarısı GENERIC'tir; BU havuz farklı ERALAR olduğundan ortak-küresel-faktör tuzağı YOK, bağımsızlık geçerli (uyarı bu koşumda uygulanmaz). **Net (replikasyonlu kesin):** motorun betimsel değeri hem trend/rejim hem vol-büyüklüğünde YOK; tek dayanıklı düzenlilik, duruş-yönü ile ileri-vol arasındaki zayıf (kaldıraç-tersi) asimetridir — küçük, ikincil, betimsel. **Bilimsel kazanım:** replikasyon, v1.1.7'nin tek "anlamlı" bulgusunu DOĞRU biçimde eledi → motor sağlam biçimde **betimsel/yapısal**, karar-destek ilkesi en yüksek-disiplinli ampirik temele oturdu.

> **Ufuk uyarısı (ampirik).** Look-ahead'siz öz-denetim (`backtest_posture.py`), haftalık duruşun **tek-haftalık** ufukta düşük sinyal taşıdığını (düşük IC) gösterebilir — özellikle getirinin çoğu seans-arası boşluktan geldiğinde. Haftalık duruş **çok-haftalık eğilim** için anlamlıdır; tek-hafta yön tahmininde güven tavanı düşük tutulmalıdır (bkz. §4).

---

## 3. Katmanların ağırlıklandırılması ve uzlaştırılması

Brifing dört kanıt katmanını **tek bir duruşa** indirger: teknik, temel, KAP-duyarlılık, makro. Bunlar **körlemesine ortalanmaz**; uzlaştırılır.

### 3.1 Katman rolleri

| Katman | Kaynak | Birincil rolü |
|---|---|---|
| **Teknik** | Tarayıcı + `technical_helpers/plus` | Zamanlama ve mevcut momentum/yapı. |
| **Temel** | Finansal oranlar + sektör karşılaştırması + `financial_quality_score` | Değer ve finansal sağlık zemini. |
| **KAP-duyarlılık** | KAP/haber akışı + `sentiment_score`/`kap_materiality` | Yeni bilgi şokları, önemli olaylar. |
| **Makro** | `macro_context` + endeks/sektör verisi | Rejim çerçevesi (risk-açık/risk-kapalı, faiz, kur). |

### 3.2 Uzlaştırma kuralları

- Katmanlar **aynı yönü** gösteriyorsa duruş güçlenir ve güven düzeyi yükselir.
- Katmanlar **çelişiyorsa**, çelişki **görünür kılınır**, ortalama alınmaz. Örnekler:
  - **Güçlü teknik + zayıf temel:** "Teknik momentum güçlü görünüyor ancak finansal kalite zayıf; bu, spekülatif/dayanaksız bir hareket olabilir" diye **işaretlenir.** İki sinyal aritmetik olarak ortalanıp "orta" denmez.
  - **Güçlü temel + zayıf teknik:** "Finansal zemin sağlam fakat fiyat yapısı zayıf; zamanlama elverişsiz olabilir" notu düşülür.
  - **Önemli KAP olayı, teknik/temelle uyumsuz:** KAP olayı taze ve önemliyse (yüksek materiality), diğer katmanları **geçersiz kılabilir** ve duruş yeniden değerlendirilir.
- **Makro**, çoğunlukla bir **çarpan/çerçeve** katmanıdır: risk-kapalı rejimde tekil hisse teknik gücü bağlamlandırılır, güven düzeyine dikkat çekilir.

### 3.3 Karar dışı çıktı

Uzlaştırma sonucu **yön içeren bir tavsiye değil**, gerekçelendirilmiş bir **gözlem ve senaryo setidir.** "Şu koşullar şu yönde; şu koşullar karşıt yönde" biçiminde sunulur.

---

## 4. Güven düzeyi puanlaması (Yüksek / Orta / Düşük)

Her vargı bir güven düzeyi taşır. Güven, üç eksenin birleşik değerlendirmesidir:

| Eksen | Yüksek güven | Düşük güven |
|---|---|---|
| **Veri uyumu (agreement)** | Katmanlar ve zaman dilimleri aynı yönü gösteriyor | Katmanlar/dilimler çelişiyor |
| **Tazelik (freshness)** | Veri güncel işlem gününe ait | Veri eski; bilanço dönemi geçmiş, fiyat birkaç gün gecikmeli |
| **Örneklem (sample)** | Yeterli geçmiş gözlem, dolu oran seti, çoklu teyit | Az gözlem, eksik oran, tek kaynak |

Bantlama:

- **Yüksek:** Üç eksende de güçlü; çoklu bağımsız teyit.
- **Orta:** Bir eksende zayıflık ya da kısmi çelişki.
- **Düşük:** Birden fazla eksende zayıflık; eksik/eski veri veya katmanlar arası belirgin çelişki.

> Tazelik kuralı: Fiyat verisi EOD/gecikmeli olduğundan, hiçbir vargı "gün-içi/anlık" güven seviyesine yükseltilemez. En yüksek geçerli ufuk günlük/haftalıktır.

### 4.1 Ufuk-koşullu güven kalibrasyonu (v1.1.0)

Güven düzeyi, vargının **ölçüldüğü ufukla** koşullanmalıdır. Teknik duruşun çözünürlüğü ile tahmin ufku eşleşmiyorsa güven tavanı düşürülür:

| Duruş çözünürlüğü | Anlamlı olduğu ufuk | Tek-hafta yön tahmini |
|---|---|---|
| Haftalık (1W) çapa | Çok-haftalık ana eğilim (≈ haftalar–aylar) | **Zayıf sinyal** — güven tavanı *Orta* |
| Günlük (1d) kurulum | Günler–birkaç hafta | Geri çekilme/kırılım zamanlaması |

Gerekçe (ampirik): look-ahead'siz öz-denetim (`backtest_posture.py`), haftalık duruş skoru ile **tek-haftalık** gerçekleşen getiri arasındaki sıra-korelasyonunun (Spearman ρ) düşük — hatta sıfır civarı — olabildiğini gösterir; özellikle haftalık getirinin büyük kısmı **seans-arası boşluktan** geldiğinde (bir EOD motorunun yapısal olarak öngöremeyeceği bileşen). Bu nedenle:

- Mod 2 (haftalık tarama) çıktısında **tek-hafta** öngörüsüne *Yüksek* güven atfedilmez; duruş "çok-haftalık eğilim bağlamı" olarak çerçevelenir.
- Çok-haftalık eğilim ifadeleri (1W çapa + 1d kurulum **uyumlu** olduğunda) daha yüksek güven taşıyabilir.
- Boşluk-maruziyeti yüksek bir kurulumda (bkz. §2.5) güven ek olarak bir kademe kısılır.

---

## 5. Zorunlu senaryo matrisi

Her brifing, üç senaryolu bir matris içerir. Bu, tek-noktalı tahmin yerine **koşullu akıl yürütme** dayatır.

| Senaryo | İçerik | Tetikleyici | Geçersizleşme (invalidation) |
|---|---|---|---|
| **Baz** | En olası temel patika | Mevcut katman dengesi sürerse | Hangi gözlem bu patikayı bozar |
| **Boğa** | Yukarı yönlü koşullu senaryo | Hangi teyit/seviye/olay yukarıyı açar | Yukarı tezi hangi seviye/veri altında geçersizdir |
| **Ayı** | Aşağı yönlü koşullu senaryo | Hangi kırılım/bozulma aşağıyı açar | Aşağı tezi hangi seviye/veri üstünde geçersizdir |

Kurallar:

- Her senaryonun **somut tetikleyicisi** ve **geçersizleşme seviyesi/koşulu** olmalıdır (ör. "günlük kapanış SMA50 altına sarkarsa", "RSI 70 üstünde teyitli kalırsa"). Seviyeler EOD kapanış bazlıdır.
- Senaryolar **olasılık dağılımı** olarak nitel sunulur ("baz daha olası, ayı kuyruk riski"); kesin yüzde atfı yapılmaz.
- Senaryolar **kişiye özel pozisyon önerisi değildir**; "şu olursa tez şuraya kayar" çerçevesindedir.

---

## 6. Belirsizlik ve EOD sınırlarının açık beyanı

Her brifing, sınırlarını açıkça beyan eder:

- **Veri ufku:** Fiyat verisi **gün-sonu/gecikmeli**dir. Gün-içi mikro-yapı, anlık emir defteri ve seans-içi hareketler **kapsam dışıdır.** Geçerli ufuk **günlük/haftalık**tır.
- **Gecikme etkisi:** En güncel fiyat işlem günü kapanışını yansıtabilir; çok hızlı gelişen olaylarda brifing geride kalabilir.
- **Veri boşlukları:** Eksik oran, eksik dönem veya alınamayan veri **gizlenmez**; ilgili vargı "veri yetersiz" notuyla düşürülür.
- **Üçüncü-taraf belirsizliği:** Analist hedefleri/tavsiyeleri doğrulanmamış bağlamdır.
- **Model değil, gözlem:** Üretilen çıktı bir fiyat tahmini modeli değil, mevcut kanıtın yorumudur.

Nihai brifing, yayımdan önce `scripts/brief_lint.py` ile denetlenir: yatırım tavsiyesi dili, kaynaksız sayı, eksik güven düzeyi veya eksik karşıt senaryo varsa işaretlenir.

---

*Karar-destek hatırlatması: Bu metodoloji gözlem ve senaryo üretir; yatırım tavsiyesi vermez. Her vargı güven düzeyi ve karşıt senaryo ile okunmalıdır.*
