# BIST Analist Kopilotu — Temel Analiz Metodolojisi (Sektör-Normalize)

Bu belge, `bist-analist-kopilotu` becerisinin **temel (fundamental) analiz** katmanını tanımlar. Amaç, finansal oranları **sektöre göre normalize ederek** değer ve finansal sağlık zemini kurmak ve bunu `scripts/financial_quality_score.py` ile yeniden-üretilebilir bir kalite kompozitine indirgemektir.

> **Sınır (değişmez):** Temel analiz, bir hissenin "ucuz/pahalı" veya "kaliteli/zayıf" olduğuna dair **gözlem** üretir; **al/sat tavsiyesi veya hedef fiyat üretmez.** Üçüncü-taraf analist verileri (`get_analyst_data`) **doğrulanmamış bağlamdır.**

---

## 1. Hangi oranlar önemli (get_financial_ratios)

Finansal oranlar dört kümede okunur. Her oran **mutlak değer** olarak değil, sektör emsaline ve şirketin kendi geçmişine **göreli** yorumlanır.

| Küme | Oranlar | Okuma |
|---|---|---|
| **Değerleme** | F/K (pe_ratio), PD/DD (pb), FD/FAVÖK (EV/EBITDA) | Şirket kazancı/öz kaynağı/işletme değeri başına ne ödendiği. Negatif F/K = zarar; "ucuz" demek değildir. |
| **Kârlılık** | ROE (roe), ROA (roa), net marj (net_margin), FAVÖK marjı | Sermayenin ve varlığın ne kadar verimli kâra dönüştüğü. |
| **Finansal sağlık** | Kaldıraç (borç/öz kaynak), cari oran, net borç/FAVÖK | Borç yükü ve kısa vadeli ödeme gücü; iflas/likidite riski. |
| **Büyüme** | Satış YoY, net kâr YoY | Üst ve alt satır büyümesi (yıldan yıla). |

Uyarılar:

- **Negatif/anlamsız oran:** Zarar eden şirkette F/K ve FD/FAVÖK yanıltıcıdır; "veri anlamlı değil" notu düşülür, düşük değer "ucuzluk" sayılmaz.
- **Tek dönem yanılgısı:** Tek çeyreklik sıçrama (tek seferlik gelir/gider) trend gibi sunulmaz; mümkünse yıllık/normalize bakılır.

---

## 2. Sektör-normalizasyon (get_sector_comparison)

Oranlar **sektör merceğiyle** okunmadan yorumlanamaz. Bankanın PD/DD'si ile sanayi şirketinin PD/DD'si aynı eşikle değerlendirilemez. `get_sector_comparison` ile şirketin emsal sektör dağılımındaki konumu (medyan/çeyreklik) çıkarılır.

| Sektör tipi | Birincil mercek | İkincil | Dikkat |
|---|---|---|---|
| **Bankalar (XBANK/XUMAL)** | PD/DD, ROE, net faiz marjı | Sermaye yeterliliği, takipteki kredi | F/K bankalarda daha az bilgilendirici; FD/FAVÖK **anlamsızdır** (finansal kuruluş). |
| **Sanayi (XUSIN/XGIDA/XELKT)** | FD/FAVÖK, FAVÖK marjı, net borç/FAVÖK | F/K, ROIC | Sermaye yoğun; kaldıraç ve marj döngüselliği kritik. |
| **Holdingler (XHOLD)** | PD/DD, NAV iskontosu | İştirak kompozisyonu | Konsolide F/K yanıltıcı; parça-toplam (sum-of-parts) mantığı. |
| **Hizmet/Teknoloji/İletişim (XUHIZ/XUTEK/XILTM)** | Büyüme, FD/Satış, FD/FAVÖK | Marj genişlemesi | Yüksek büyüme beklentisi yüksek çarpanı "haklı" kılabilir; sürdürülebilirlik sorgulanır. |

Kural: Bir oranı "yüksek/düşük" diye nitelemeden önce **emsal medyanı** belirtilir. Örnek: "PD/DD 1,2; banka sektör medyanı ~0,8 — emsalin üzerinde."

Endeks bağlamı için ilgili sektör endeksleri kullanılır: XU030, XU100, XBANK, XUSIN, XUMAL, XUHIZ, XUTEK, XHOLD, XGIDA, XELKT, XILTM.

Fundamental tarama ön ayarları (screener), emsal kümeyi hızlı kurmaya yarar: `small/mid/large_cap`, `high_dividend`, `low_pe`, `high_roe`, `high_net_margin`, `high_upside`, `high_return`, `high_foreign_ownership`, `buy/sell_recommendation`. Bunlar **filtre/karşılaştırma aracıdır**, tavsiye üretmez (ör. `buy_recommendation` ön ayarı doğrulanmamış üçüncü-taraf etiketidir).

---

## 3. Finansal kalite kompoziti (scripts/financial_quality_score.py)

Beceri, temel görünümü **0–100 bandında** deterministik bir kalite skoruna indirger. Skor, `get_financial_ratios` ve `get_sector_comparison` çıktılarını girdi alır; **sektör-normalize** edilmiş alt-skorların ağırlıklı birleşimidir. Bu belge ile betik **aynı tanımı** paylaşır.

### 3.1 Alt-skorlar

| Alt-skor | Girdi oranlar | Mantık |
|---|---|---|
| **Kârlılık** | ROE, ROA, net/FAVÖK marjı | Emsal medyanına göre z-benzeri konum → 0–100. |
| **Kaldıraç / ödeme gücü (solvency)** | Borç/öz kaynak, net borç/FAVÖK, cari oran | Düşük borç + yeterli likidite yüksek puan; aşırı kaldıraç cezalandırılır. |
| **Büyüme** | Satış YoY, net kâr YoY | Pozitif ve sürdürülebilir büyüme yüksek puan; enflasyon-düzeltmeli okuma (bkz. §5). |
| **Değerleme makullüğü** | F/K, PD/DD, FD/FAVÖK (sektör-normalize) | "Ucuz = yüksek puan" değil; emsale göre **makul** olan yüksek puan. Aşırı pahalı ve dayanaksız ucuz uçları cezalandırılır. |

### 3.2 Bantlama (0–100)

| Band | Etiket | Yorum |
|---|---|---|
| 80–100 | Güçlü | Çoğu alt-boyutta emsal üstü; sağlam zemin. |
| 60–79 | İyi | Genel olarak sağlam, sınırlı zayıflık. |
| 40–59 | Orta | Karışık; en az bir alt-boyutta belirgin zayıflık. |
| 20–39 | Zayıf | Birden çok boyutta zayıflık. |
| 0–19 | Kırılgan | Yapısal sorunlar (zarar, aşırı kaldıraç, daralma). |

Kurallar:

- Veri eksikse ilgili alt-skor **boş bırakılır** ve kompozit "kısmi" olarak işaretlenir; uydurma değerle doldurulmaz.
- Kompozit bir **özet işarettir**, tek başına vargı değildir; methodology.md'deki katman uzlaştırmasına girdi olur.
- Değerleme makullüğü alt-skoru, "ucuz" ile "kalitesiz ucuz"u ayırt eder; düşük çarpan tek başına olumlu sayılmaz.

---

## 4. Kazanç, temettü ve sermaye işlemi bağlamı

Temel görünüm, oranların ötesinde **olay bağlamıyla** zenginleştirilir.

| Kaynak | Ne sağlar | Dikkat |
|---|---|---|
| `get_earnings` | Kazanç açıklama takvimi/geçmişi, sürpriz | Yaklaşan bilanço, oran tazeliğini etkiler; eski döneme dayalı vargı işaretlenir. |
| `get_dividends` | Temettü geçmişi/verimi | Yüksek temettü verimi sürdürülebilir mi; tek seferlik mi sorgulanır. |
| `get_corporate_actions` | Bedelli/bedelsiz, bölünme, birleşme | **Seyrelme (dilution) uyarısı**; tarihsel fiyat/oran serileri düzeltilmemişse kıyas bozulur. |

**Bedelli/bedelsiz uyarısı:** Bedelli sermaye artırımı mevcut payı seyreltir; "fiyat düştü" gözlemi düzeltme kaynaklı olabilir. Bedelsiz, pay sayısını artırır, değer yaratmaz. Sermaye işlemi varsa, YoY büyüme ve hisse-başı oranlar bu etki belirtilerek okunur.

---

## 5. TL-enflasyon bozulması (nominal büyüme uyarısı)

Türk Lirası bazlı nominal büyüme, yüksek enflasyon ortamında **gerçek büyümeyi abartır.**

- **Nominal satış/kâr YoY** yüksek görünebilir; bunun bir kısmı yalnızca fiyat artışıdır. Brifing, güçlü nominal büyümeyi "enflasyon etkisi düşülmeden" notuyla sunar.
- Mümkün olduğunda **reel** bağlam (enflasyona göre) veya **marj** trendi (enflasyondan daha az etkilenir) vurgulanır.
- **Enflasyon muhasebesi (TMS 29)** uygulanan dönemlerde, düzeltilmiş ve düzeltilmemiş finansallar karıştırılmaz; hangi temelde olduğu belirtilir.
- Yabancı para borçlu/gelirli şirketlerde kur etkisi, nominal büyümeyi ayrıca çarpıtabilir; bu da işaretlenir.

> Kural: Yüksek nominal büyüme tek başına "güçlü temel" sayılmaz; reel/marj teyidi olmadan büyüme alt-skoru ihtiyatlı puanlanır.

---

## 6. Üçüncü-taraf verisi (get_analyst_data)

`get_analyst_data` çıktısı (hedef fiyat, konsensüs tavsiye, tahminler) **doğrulanmamış bağlam** olarak ele alınır:

- Becerinin kendi temel vargısı yerine geçemez.
- Hedef fiyat türetmek için kullanılamaz.
- Yalnızca "piyasa konsensüsü şu yönde — doğrulanmadı" çerçevesiyle, kaynak ve tarih belirtilerek aktarılır.

---

*Karar-destek hatırlatması: Temel analiz, finansal kaliteye dair gözlem üretir; yatırım tavsiyesi veya hedef fiyat vermez. Her oran sektör emsali ve güven düzeyiyle okunmalıdır.*
