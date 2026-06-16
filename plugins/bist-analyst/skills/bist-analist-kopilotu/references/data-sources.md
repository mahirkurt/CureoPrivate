# Veri Omurgası ve Veri Güveni — `bist-analist-kopilotu`

Bu belge, BIST analist ko-pilotunun beslendiği veri kaynaklarını, her kaynağın
kapsamını, tazelik/gecikme özelliklerini ve bir **veri güveni (data-trust)
merdivenini** tanımlar. Amaç, üretilen brifingin her satırının izlenebilir bir
kaynağa dayanması ve kaynak güvenilirlik seviyesinin açıkça etiketlenmesidir.

> Tüm fiyat ve teknik veriler **gün sonu (EOD) / gecikmeli** karakterdedir.
> Intraday emir defteri, derinlik veya Level-2 verisi **yoktur**. Analiz ufku
> **günlük ve haftalık** ile sınırlıdır.

---

## 1. Veri omurgası: `borsa` MCP

Tüm birincil piyasa verisi, paketlenmiş uzak MCP sunucusu **`borsa`** (Borsa MCP,
FastMCP, `https://borsamcp.fastmcp.app/mcp`) üzerinden gelir. Sunucu, TCMB EVDS
gibi anahtar gerektiren kaynaklar için anahtarı **sunucu tarafında** tutar;
kullanıcının hiçbir API anahtarı kurulumu yapması gerekmez.

### 1.1 Kaynak katmanları ve kapsamları

| Katman | Sağlayan araç(lar) | Kapsam | Tazelik |
|---|---|---|---|
| Sembol çözümleme | `search_symbol` | Ticker → resmi sembol eşleme (bist/us/fx/...) | Anlık (statik liste) |
| Anlık görünüm | `get_quick_info` | Son kapanış, günlük değişim %, hacim, piyasa değeri | EOD / gecikmeli |
| Şirket profili | `get_profile` | Sektör, faaliyet alanı, açıklama | Düşük frekanslı |
| Fiyat serisi | `get_historical_data` | EOD OHLCV zaman serisi | Gün sonu kapanış |
| Teknik göstergeler | `get_technical_analysis`, `get_pivot_points` | RSI, MACD, hareketli ortalamalar, Bollinger, Supertrend, T3, ATR; pivot/destek-direnç | EOD bazlı |
| Temel mali tablolar | `get_financial_statements`, `get_financial_ratios` | Gelir tablosu, bilanço, nakit akışı; F/K, PD/DD, ROE, ROA, net marj, kaldıraç, cari oran | Çeyreklik raporlama |
| Sektör/akran | `get_sector_comparison` | Akran/sektör göreli metrikleri (temel normalizasyon) | Çeyreklik bazlı |
| Endeks | `get_index_data` | XU030, XU100, XBANK ve sektör endeks serileri | EOD |
| Temettü / kâr | `get_dividends`, `get_earnings` | Temettü geçmişi/verimi, kâr geçmişi/takvimi | Olay bazlı |
| Şirket olayları | `get_corporate_actions` | Bölünme, bedelli/bedelsiz sermaye artırımı, birleşme | Olay bazlı |
| Haber / KAP | `get_news` | Haber akışı **ve KAP açıklamaları** | Olay bazlı, gün içi yayım |
| Tarama | `scan_stocks`, `screen_securities` | Teknik tarayıcı; temel ekran | EOD bazlı |
| Döviz | `get_fx_data` | USDTRY, EURTRY (makro bağlam) | EOD / gecikmeli |
| Makro | `get_macro_data`, `get_evds_data`, `get_economic_calendar`, `get_bond_yields` | TCMB EVDS serileri, makro takvim, TR tahvil faizleri (risk-free/iskonto bağlamı) | EVDS yayım takvimi |
| Mevzuat | `get_regulations` | Düzenleyici referanslar | Düşük frekanslı |
| Üçüncü-taraf tahmin | `get_analyst_data` | Analist tahmin/hedef/öneri | **Doğrulanmamış** |

### 1.2 Kapsam dışı kaynaklar

- `screen_funds`, `get_fund_data` — TEFAS fonları. Hisse analizinde **kapsam
  dışı**; yalnızca mevcudiyeti not edilir, hisse brifingine girmez.
- `get_crypto_market` — Kripto. **Kapsam dışı.**

---

## 2. Tazelik ve gecikme özellikleri

- **EOD/gecikme yanlılığı.** Fiyat, hacim, teknik ve pivot verilerinin tamamı
  gün sonu kapanışına dayanır. Gün içi hareket, açılış/kapanış mekanizması,
  seans-içi seviye veya emir derinliği **mevcut değildir**. Brifingde "son fiyat"
  her zaman **son kapanış** olarak ifade edilmelidir.
- **Intraday yokluğu.** Order book, bid/ask spread, derinlik ve Level-2 verisi
  sağlanmaz. Skalp/gün-içi kurguları üretilmez; çıktı ufku **günlük ve haftalık**
  ile sınırlıdır.
- **Çeyreklik temel veri.** Mali tablo ve oranlar çeyreklik raporlama
  takvimine bağlıdır; en güncel çeyrek henüz açıklanmamış olabilir. Tarih/çeyrek
  damgası daima belirtilmelidir.
- **EVDS sunucu tarafı anahtar.** TCMB EVDS makro serileri sunucu tarafında
  yetkilendirilir; kullanıcı kurulumu gerekmez. Yayım gecikmesi serinin TCMB
  yayım takvimine bağlıdır (örn. TÜFE aylık, faiz kararı PPK takvimine göre).
- **KAP gecikmesi.** KAP açıklamaları `get_news` üzerinden gelir; yayım anına
  yakın ancak akış tabanlıdır. Bir açıklamanın resmî metni için her zaman KAP'a
  atıf yapılır.

---

## 3. Veri güveni merdiveni (data-trust ladder)

Brifingdeki her ifade, dayandığı kaynağın güven seviyesine göre etiketlenir.
Yüksekten düşüğe:

| Seviye | Kaynak | Etiket | Kullanım kuralı |
|---|---|---|---|
| **1 — En yüksek** | KAP resmî açıklamaları, TCMB/EVDS resmî serileri, resmî mali tablolar | *resmî / birincil* | Doğrudan dayanak olarak kullanılabilir |
| **2 — Yüksek** | Borsa/endeks EOD piyasa verisi, hesaplanmış teknik/temel göstergeler | *piyasa verisi (EOD)* | Tazelik damgasıyla kullanılır |
| **3 — Orta** | Sektör/akran karşılaştırması, türev/hesaplanmış metrikler | *türetilmiş* | Yöntem ve normalizasyon açıkça belirtilir |
| **4 — Doğrulanmamış** | `get_analyst_data` üçüncü-taraf tahmin/hedef/öneri | *doğrulanmamış / üçüncü-taraf* | Yalnızca bağlam olarak; **asla yönlendirme/hedef olarak sunulmaz** |

**Kritik kural:** Üçüncü-taraf analist hedefleri yalnızca "doğrulanmamış /
üçüncü-taraf" notuyla aktarılır; hiçbir koşulda kişiselleştirilmiş al/sat veya
hedef fiyat çağrısına dönüştürülmez.

---

## 4. Zarif bozulma (graceful degradation)

`borsa` MCP'sine **erişilemezse**:

1. Yalnızca `web_search` / `web_fetch` ile devam edilir.
2. Her bilgi parçasının kaynağı (URL/yayıncı + tarih) açıkça etiketlenir ve
   veri güveni merdiveninde sınıflandırılır (resmî KAP/TCMB sayfası = Seviye 1;
   üçüncü-taraf haber/blog = düşük).
3. **Fiyat veya gösterge değerleri asla uydurulmaz.** Web'den teyit edilemeyen
   sayısal değer için "veri alınamadı" denir; tahmini değer üretilmez.
4. Brifingin başında, `borsa` erişilemediği ve sonuçların yalnızca açık-web
   kaynaklarına dayandığı not düşülür.

---

> Bu belgenin ürettiği çıktılar **karar-destek** amaçlıdır; **yatırım tavsiyesi
> değildir.**
