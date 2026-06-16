# `borsa` MCP Araç Şeması ve Çağrı Kalıpları — `bist-analist-kopilotu`

Bu belge, `borsa` MCP sunucusunun araçlarını mod-bazlı kullanım için referans
tablosu olarak verir; ardından `scan_stocks` ve `screen_securities` filtre
gramerini tam metin olarak ve dört çalışma modu için örnek çağrı sıralamasını
içerir.

> **Sembol kuralı:** Her analize **önce `search_symbol` ile** doğru BIST sembolü
> teyit edilerek başlanır.
>
> **Filtre belirsizliği:** Bir filtre alanının/preset adının kesin yazımı
> belirsizse, varsayım yapmadan **`get_scanner_help()` / `get_screener_help(market)`**
> çağrılarak canlı gramer alınır.

---

## 1. Araç referans tablosu

| Araç | Ne döner | Hangi modda | Notlar |
|---|---|---|---|
| `search_symbol(query, market)` | Ticker → resmi sembol (market ∈ bist/us/crypto_tr/crypto_global/fund/fx) | 1,2,3,4 | **İlk çağrı**; BIST için `market='bist'` |
| `get_quick_info` | Son kapanış, değişim %, hacim, piyasa değeri | 1,3,4 | EOD anlık görünüm |
| `get_profile` | Şirket profili / sektör / açıklama | 1,3 | Düşük frekanslı |
| `get_historical_data` | EOD OHLCV zaman serisi | 1,4 | Intraday yok |
| `get_technical_analysis` | RSI, MACD, hareketli ort., Bollinger, Supertrend, T3, ATR | 1,4 | EOD bazlı |
| `get_pivot_points` | Klasik/Fibonacci pivot (destek/direnç) | 1,4 | Günlük/haftalık seviye |
| `get_financial_statements` | Gelir tablosu / bilanço / nakit akışı | 1 | Çeyreklik damga |
| `get_financial_ratios` | F/K, PD/DD, ROE, ROA, net marj, kaldıraç, cari oran | 1,2 | Değerleme + kalite |
| `get_analyst_data` | Üçüncü-taraf tahmin/hedef/öneri | 1,3 | **Doğrulanmamış**; yönlendirme değil |
| `get_dividends` | Temettü geçmişi/verimi | 1 | Olay bazlı |
| `get_earnings` | Kâr geçmişi/takvimi | 1,3 | Kâr sürprizi bağlamı |
| `get_corporate_actions` | Bölünme, bedelli/bedelsiz, birleşme | 1,3 | Olay yorumu |
| `get_news` | Haber **+ KAP açıklamaları** akışı | 1,3,4 | KAP birincil etiketi |
| `get_sector_comparison` | Akran/sektör göreli metrikleri | 1,2 | Temel normalizasyon |
| `get_index_data` | XU030, XU100, XBANK, sektör endeksleri | 1,2,4 | Rejim/beta bağlamı |
| `scan_stocks` | Teknik tarayıcı sonuçları | 2,4 | Bkz. §2 gramer |
| `screen_securities` | Temel ekran sonuçları | 2 | Bkz. §3 gramer |
| `get_fx_data` | USDTRY, EURTRY | 1,2,3,4 | Makro bağlam |
| `get_macro_data` / `get_evds_data` | TCMB EVDS makro serileri | 1,2 | Anahtar sunucu tarafında |
| `get_economic_calendar` | Makro olay takvimi | 2,3,4 | Yaklaşan olay riski |
| `get_bond_yields` | TR tahvil faizleri | 1,2 | Risk-free / iskonto bağlamı |
| `get_regulations` | Düzenleyici referanslar | 3 | Olay/uyum yorumu |
| `get_scanner_help()` | Canlı tarayıcı gramer/preset listesi | 2,4 | Alan adı belirsizse çağır |
| `get_screener_help(market)` | Canlı ekran gramer/preset listesi | 2 | Alan adı belirsizse çağır |
| `screen_funds` / `get_fund_data` | TEFAS fonları | — | **Kapsam dışı** (hisse) |
| `get_crypto_market` | Kripto | — | **Kapsam dışı** |

Modlar: **1** = tek-hisse derin analiz · **2** = haftalık tarama/izleme listesi
üretimi · **3** = KAP açıklaması/olay yorumu · **4** = izleme listesi gözetimi.

---

## 2. `scan_stocks` grameri (teknik tarayıcı)

**Göstergeler:** `RSI` (0–100), `macd` (histogram), `close`, `change` (günlük %),
`volume`, `market_cap`, `SMA` (`sma_5`, `sma_20`, `sma_50`, `sma_200`),
`EMA` (`ema_20`), `bb_upper`, `bb_lower`, `supertrend_direction`
(`1` yükseliş / `-1` düşüş), `t3` (Tillson T3).

**Operatörler:** `>` `<` `>=` `<=` `==` `and` `or`

**Zaman dilimleri:** `1d`, `1h`, `4h`, `1W`

**Taranabilir endeksler:** `XU030`, `XU100`, `XBANK`, `XUSIN`, `XUMAL`, `XUHIZ`,
`XUTEK`, `XHOLD`, `XGIDA`, `XELKT`, `XILTM`, `XK100`, `XK050`, `XK030`

**Hazır presetler (22 adet, seçme):**

| Preset | Tanım |
|---|---|
| `oversold` | `RSI<30` |
| `overbought` | `RSI>70` |
| `bullish_momentum` | `RSI>50 and macd>0` |
| `bearish_momentum` | düşüş momentumu |
| `macd_positive` | macd histogram pozitif |
| `high_volume` | `volume>10000000` |
| `big_gainers` | `change>3` |
| `big_losers` | `change<-3` |
| `momentum_breakout` | `change>2 and volume>5000000` |
| `bb_oversold_buy` | `close<bb_lower and RSI>30` |
| `bb_overbought_sell` | Bollinger üst aşırı |
| `ma_squeeze_momentum` | hareketli ort. sıkışma çıkışı |
| `supertrend_bullish` | `supertrend_direction==1` |
| `supertrend_bearish` | `supertrend_direction==-1` |
| `supertrend_bullish_oversold` | supertrend yükseliş + aşırı satım |
| `t3_bullish` | `close>t3` |
| `t3_bearish` | `close<t3` |
| `t3_bullish_momentum` | `close>t3 and RSI>50` |

> Tüm preset adlarının ve özel filtre alanlarının kesin yazımı için
> **`get_scanner_help()`** çağrılır.

---

## 3. `screen_securities` grameri (temel ekran)

**Presetler:** `small_cap` (<5B TL), `mid_cap` (5–25B TL), `large_cap` (>25B TL),
`high_dividend` (>%3), `low_pe` (<10), `high_roe` (>%15), `high_net_margin`
(>%15), `high_upside` (>%20), `low_upside`, `high_return` (>%50 yıllık),
`high_volume`, `low_volume`, `high_foreign_ownership` (>%40),
`buy_recommendation`, `sell_recommendation`.

**Operatörler:** `eq`, `gt`, `lt`, `btwn`

**Örnek filtre sorguları:**

```
sector == 'Bankacilik'
market_cap > 10000000000
pe_ratio < 15
```

> `buy_recommendation` / `sell_recommendation` presetleri üçüncü-taraf öneri
> tabanlıdır; çıktıda **doğrulanmamış** olarak etiketlenir, yönlendirmeye
> dönüştürülmez. Alan adı belirsizse **`get_screener_help('bist')`** çağrılır.

---

## 4. Mod-bazlı örnek çağrı sıralamaları

### Mod 1 — Tek-hisse derin analiz

1. `search_symbol(query, market='bist')` — sembolü teyit et.
2. `get_quick_info` + `get_profile` — anlık görünüm ve sektör.
3. `get_historical_data` → `get_technical_analysis` → `get_pivot_points` — fiyat
   yapısı ve seviyeler (EOD).
4. `get_financial_statements` + `get_financial_ratios` — temel görünüm.
5. `get_sector_comparison` — akran normalizasyonu.
6. `get_dividends`, `get_earnings`, `get_corporate_actions`, `get_news` — olay/akış.
7. `get_analyst_data` — **doğrulanmamış** bağlam.
8. `get_index_data` + `get_fx_data` + `get_bond_yields` — rejim/iskonto bağlamı.

### Mod 2 — Haftalık tarama / izleme listesi üretimi

1. `get_index_data` (XU100/XU030) + makro/`get_fx_data` — rejim çerçevesi.
2. `scan_stocks` (örn. `bullish_momentum` veya özel filtre, endeks=XU100,
   timeframe `1W`/`1d`) — teknik aday havuzu.
3. `screen_securities` (örn. `low_pe` + `high_roe` veya filtre sorgusu) — temel
   eleme.
4. İki listenin kesişimi → her aday için kısa `get_financial_ratios` /
   `get_sector_comparison` teyidi.
5. Gramer belirsizse `get_scanner_help()` / `get_screener_help('bist')`.

### Mod 3 — KAP açıklaması / olay yorumu

1. `search_symbol` — ilgili sembol.
2. `get_news` — KAP açıklamasını/haberi getir (birincil kaynak).
3. Olay türüne göre: `get_corporate_actions` (sermaye/birleşme), `get_earnings`
   (kâr), `get_dividends` (temettü), `get_regulations` (uyum).
4. `get_quick_info` — açıklama öncesi/sonrası bağlam (EOD).
5. Gerekirse `get_financial_ratios` — etkinin temel bağlamı.

### Mod 4 — İzleme listesi gözetimi

1. Liste sembolleri için toplu `get_quick_info` — değişim/hacim taraması.
2. `scan_stocks` (özel filtre, ilgili endeks) — tetiklenen teknik koşullar.
3. `get_technical_analysis` / `get_pivot_points` — tetiklenen isimlerde teyit.
4. `get_news` — listedeki isimlerde yeni KAP/haber.
5. `get_economic_calendar` — yaklaşan makro olay riski.

---

> Bu araç şemasıyla üretilen çıktılar **karar-destek** amaçlıdır; **yatırım
> tavsiyesi değildir.**
