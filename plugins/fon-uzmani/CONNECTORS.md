# fon-uzmani — Paylaşılan Connector Sözleşmesi (CONNECTORS.md)

**Belge sınıfı:** Normatif connector envanteri — plugin-düzeyi tek doğruluk kaynağı.
**Sürüm:** 1.1.0 (2026-06-20 — fon-mcp canlı tool yüzeyiyle hizalandı)

> **Neden bu dosya var.** Connector tanımı altı SKILL.md içinde tekrarlanmasın; aynı
> TEFAS/Borsa çağrısı iki skill tarafından ayrı ayrı yapılmasın diye connector
> envanteri, skill-eşlemesi, fallback ve provenance tek noktaya çekilir. Her skill
> buraya **referans verir**.

---

## 0. Connector Çözümleme Merdiveni (Native-First Doktrini)

1. **Native MCP** — bağlı connector'da doğrulanmış araç varsa, web aramadan önce o kullanılır.
2. **Genel REST API** — native MCP yoksa kamuya açık REST (örn. doğrudan TEFAS).
3. **web_fetch** — birincil kaynağın bilinen URL'i üzerinde (KAP fon sayfası vb.).
4. **web_search / Exa** — yalnızca **URL keşfi** için.

Tier-0 güven gerektiren her sayısal iddia (NAV, getiri, TER, ağırlık) 1–3 yoluyla
**birincil kaynağa** çözülmelidir. Asla uydurulmaz.

---

## 1. Connector Envanteri ve Skill-Eşleme Matrisi

Sütunlar: **FH** = fon-haritalama · **QA** = quant-analiz · **PM** = piyasa-makro ·
**RU** = regulasyon-uyum · **PI** = portfoy-insa · **IZ** = izleme · **ORK** = orchestrator.
● = birincil/zorunlu · ○ = koşullu/opsiyonel · — = kullanılmaz.

### 1.A fon-mcp (TEFAS/KAP detay sunucusu — `https://fon-mcp.cureonics.workers.dev/mcp`)

> **Yeni TEFAS resmî API** (2026 Next.js göçü sonrası — `fonGnlBlgSiraliGetir` /
> `dagilimSiraliGetirT` / `fonBilgiGetir` / `fonYonetimBazliBilgiGetir`). Eski
> `/api/DB/Bind*` rotaları küresel devre dışı (`Method not found`); doğrudan TEFAS
> kazıma yapan herhangi bir akış BU sunucuya geçirilir. Auth/anahtar YOK.

| Araç | Döndürdüğü (canlı şema) | FH | QA | PM | RU | PI | IZ | ORK | Not |
|---|---|---|---|---|---|---|---|---|---|
| `resolve_fund(query, fund_type?)` | `code/name/aum/kap_link` (kurucu/kategori dönmez) | ● | — | — | — | — | ○ | ● | Kimlik çözümleme |
| `get_fund_registry(code, fund_type?)` | `name/category/aum/investor_count/category_rank/category_fund_count/market_share/last_price/founder` (PYŞ kısa adı, ünvandan türetilmiş) + `isin=null` + `strategy=null` + `kap_link` | ● | — | — | ○ | — | — | ● | Snapshot kartı; ISIN/strateji için KAP |
| `get_fund_taxonomy(fund_type, code?)` | `code` verilirse → tek fonun `category`; verilmezse → **SPK kategori referans listesi** (sayım YOK; getiri-sıralı tarama için Borsa `screen_funds`) | ● | — | — | — | — | — | ● | Taksonomi |
| `get_allocation_snapshot(code, fund_type?)` | son `allocations[{asset_class, code, percent}]` (~30 kodlu kolon → TR etiket) | ● | ○ | — | — | ○ | ○ | ● | Anlık dağılım |
| `get_allocation_history(code, start_date, end_date, fund_type?)` | dağılım **zaman-serisi** + `note` (>100k satır kapağında uyarı) | ● | ○ | — | — | — | ○ | ● | Drift/stil için |
| `get_fund_holdings(code, fund_type?)` | `holdings[{instrument, code, weight_pct}]` (**varlık-sınıfı düzeyi**; menkul-bazlı line-item YOK — KAP portföy raporu PDF) | ● | ○ | — | — | ○ | — | ● | Yoğunlaşma/overlap |
| `get_fund_costs(code, fund_type?)` | `management_fee_pct` + **`ter_ceiling_pct` (azami toplam gider oranı — ÜST SINIR, gerçekleşen TER DEĞİL)** + `umbrella` + `founder_code` ([fon-mcp / fonYonetimBazliBilgiGetir]); gerçekleşen TER → KAP KIID | ● | ○ | — | ○ | ○ | ○ | ● | Maliyet (üst-sınır) |
| `compare_fund_costs(fund_type, category?, sort_by?, limit?)` | TER üst-sınır kesiti (`sort_by=ter_ceiling_pct` varsayılan; `aum`/`management_fee_pct` opsiyonel); kategori filtresi destekli | ● | — | — | — | ○ | — | ● | Maliyet tarama |
| `get_fund_flows(code, start_date, end_date, fund_type?)` | NAV/shares/investor/AUM zaman-serisi + Δshares×midNAV ile türetilmiş `net_flow_try` | ● | — | — | — | — | ○ | ● | Akış |
| `get_flow_leaders(fund_type, limit?)` | AUM proxy sıralı evren | ● | — | — | — | — | — | ● | Akış (proxy) |
| `list_emk_funds(founder?, limit?)` | EMK evreni; `founder` arg = fon ünvanı substring filtresi (alt-kategori/FİGO/FTGK yeni API'de YOK) | ● | — | — | — | ○ | — | ● | Emeklilik |
| `fon_mcp_health` | `tefas_reachable`, `tefas_status`, `cache_namespace`, `relay`, `api` damgası | — | — | — | — | — | — | ● | Sağlık-kontrolü |

### 1.B Borsa MCP (mevcut — `https://borsamcp.fastmcp.app/mcp`)

| Araç | Döndürdüğü | FH | QA | PM | RU | PI | IZ | ORK | Not |
|---|---|---|---|---|---|---|---|---|---|
| `get_fund_data` | getiri/NAV serisi/AUM/kategori sıralaması | ● | — | — | — | — | ○ | ● | NAV omurgası (include_performance/portfolio) |
| `screen_funds` | kategori/tür tarama (YAT/EMK) | ● | — | — | — | — | — | ● | Mod 2 keşif |
| `get_index_data` | benchmark endeks serisi (XU100 vb.) | — | — | ● | — | — | — | ● | Beta/aktif getiri |
| `get_bond_yields` | TR tahvil getirisi | — | ○ | ● | — | — | — | ● | Risksiz oran |
| `get_fx_data` | USDTRY/EURTRY | — | — | ● | — | — | — | ● | Kur bağlamı |
| `get_evds_data` / `get_macro_data` | TCMB makro (faiz/enflasyon) | — | — | ● | — | — | — | ● | Makro rejim |
| `get_news` / `get_regulations` | haber/düzenleme | — | — | — | ○ | — | ○ | ○ | KAP/duyuru sinyali |

---

## 2. Connector → Skill Sorumluluk Sınırı (kim neyi çağırır)

Süit içinde her veri alanının connector çağrı sorumluluğu **tek skill'e** atanır;
orchestrator çift çağrıyı engeller (kanonik-önbellek §3).

| Veri alanı | Kanonik sahip | Faz | Diğerleri nasıl erişir |
|---|---|---|---|
| Fon kimlik + holdings + TER + akış + NAV serisi | **fon-haritalama** | Aşama 1 (bir kez) | `fund_registry`/`holdings`/`nav_series` artefaktından **okur** |
| Benchmark + risksiz oran + makro rejim | **piyasa-makro** | Aşama 2 (bir kez) | `market_context` |
| Risk/getiri metrikleri | **quant-analiz** | Aşama 4 | `quant_metrics` |
| Optimize tahsis | **portfoy-insa** | Aşama 5 | `optimized_portfolio` |
| SPK/KAP uyum | **regulasyon-uyum** | Aşama 7 | feragat bloğu enjekte edilir |

---

## 3. Tek-Sefer fon-mcp/Borsa + Tek-Hesap Kuralı

- fon-mcp holdings/NAV/registry çağrısı süitte **fon-haritalama tarafından bir kez**
  yapılır (Aşama 1); Aşama 3/5/izleme bu artefaktı **okur, yeniden sormaz**.
- Aynı fon × metrik kombinasyonu için kuant betiği **bir kez** çalışır; `scope_hash` ile
  önbelleklenir (kanonik-önbellek §2).
- `run_manifest.connector_call_ledger` bunu denetler: `fon_mcp.single_shot_enforced`,
  `borsa_mcp.fund_data_calls`, `quant_engine.deterministic: true`.

---

## 5. EOD / Veri-Tazelik / Yıllıklama Sözleşmesi

- TEFAS NAV verisi **gün-sonu (EOD)**; her fiyat/metrik `as-of` tarihi taşır; gün-içi
  iddia yasaktır.
- Yıllıklama faktörü (252/52/12) tarih ekseninden çıkarılır ve her metrikte raporlanır
  (quant betikleri `ppy`/`ppy_basis` döner).
- TL nominal getiri yüksek-enflasyon döneminde şişer; reel getiri (EVDS TÜFE) varsa
  paralel raporlanır.

---

## 6. MCP Fallback Protokolü

| Birincil | Düşüş | Caveat etiketi |
|---|---|---|
| fon-mcp holdings/allocation timeout | Borsa `get_fund_data(include_portfolio)` (sınırlı: asset-class var, line-item yok) | "holdings doğrulanamadı (fon-mcp erişilemedi)" |
| fon-mcp `get_fund_costs` üst-sınır TER vermez (eksik kayıt) | KAP KIID (Yatırımcı Bilgi Formu) — fon-mcp `kap_link` zaten döner | "ter üst-sınırı alınamadı; KAP KIID gerekir" |
| Gerçekleşen TER gerekliyse | Her zaman KAP KIID (TER üst-sınır ≠ gerçekleşen) | "TER azami sınır; gerçekleşen için KAP KIID" |
| fon-mcp `get_fund_registry` ISIN/strateji vermez | Borsa `get_fund_data` (ISIN) + KAP fon sayfası (strateji) web_fetch | "profil kısmen KAP'tan, doğrulanmamış olabilir" |
| Borsa `get_fund_data` timeout | fon-mcp `get_fund_flows` (NAV/shares/AUM zaman-serisi YEDEKLİ omurga) | "NAV omurgası fon-mcp'den; getiri penceresi sınırlı" |
| Borsa `screen_funds` timeout | fon-mcp `compare_fund_costs(sort_by=ter_ceiling_pct)` / `get_flow_leaders` / `list_emk_funds` (evren) | "tarama degrade — TER/AUM bazlı" |

Her fallback `run_manifest.caveats[]`'a ve rapor §Sınırlar bölümüne yazılır.

---

## 7. Provenance Özeti

Damga grameri `shared/provenance-standard.md`'dedir. Özet: `[Borsa MCP / get_fund_data /
<as-of>]`, `[fon-mcp / get_fund_holdings / <as-of>]`, `[fon-mcp / fonYonetimBazliBilgiGetir
/ <as-of>]` (TER üst-sınır), `[KAP / KIID / <kod> / <tarih>]` (gerçekleşen TER), `[KAP /
duyuru / <kod> / <tarih>]`, `[quant-analiz / <script> / <formül-vN>]`; her NAV/metrik
`(EOD/gün-sonu, as-of <tarih>)`. TER raporlandığında **üst-sınır mı gerçekleşen mi**
açıkça etiketlenir.

---

## 8. Sağlık-Kontrolü (pre-flight)

`start` skili ve her komut çalışmadan önce:
1. Borsa MCP: `search_symbol(market='fund', query='<bilinen kod>')` veya `get_fund_data` prob.
2. fon-mcp: `fon_mcp_health` → `tefas_reachable: true` + `api: "fonBilgiGetir/fonGnlBlgSiraliGetir/dagilimSiraliGetirT (yeni resmî API)"` + `cache_namespace: "fon:v4"` (veya sonraki).
Erişilemeyen connector için ilgili modun degrade çalışacağı kullanıcıya bildirilir.

**Canlı tool envanteri:** 12 araç (yukarıdaki §1.A tablosuyla bire-bir). `tools/list`
beklentisini bozarsa süit sürümü atlanmış demektir — `evals/mcp_smoke_test.md` çalıştırın.
