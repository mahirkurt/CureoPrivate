# rxpraxis — Paylaşılan Connector Sözleşmesi (CONNECTORS.md)

**Belge sınıfı:** Normatif connector envanteri — plugin-düzeyi tek doğruluk kaynağı
**Sürüm:** 1.2.0 *(v1.2 — §9 devre-kesici + approval-gate raw failover; L1 tool-manifest pin-load → shared/tool-manifest.json)*
**Kapsam:** rxpraxis süitinin beş skill'inin (rxos · medical-research · pharmaintel · pharmapatent · thoughtspot-roche) tükettiği TÜM MCP connector'ları ve REST kaynakları.

> **Neden bu dosya var.** Süit öncesi, aynı connector envanteri beş ayrı `SKILL.md`
> içinde tekrarlanıyordu; aynı TİTCK MCP üç skill tarafından (medical-research Türkiye
> Dörtlüsü + pharmaintel Channel A + pharmapatent Mod 13) ayrı ayrı çağrılıyordu. Bu
> dosya, connector tanımını tek noktaya çeker; her skill buraya **referans verir**,
> kendi içinde yeniden tanımlamaz. Connector adı/parametre değişikliği yalnızca burada
> güncellenir.

---

## 0. Connector Çözümleme Merdiveni (Native-First Doktrini)

Her veri ihtiyacı şu öncelik sırasıyla çözülür (medical-research v8.0 "Native-MCP-First"
ve pharmaintel v3.0 "API-Integrations" doktrinlerinin birleşimi):

1. **Native MCP** — bağlı connector'da doğrulanmış araç varsa, web aramadan önce o kullanılır.
2. **Genel REST API** — native MCP yoksa kamuya açık REST (openFDA, ClinicalTrials.gov v2, ThoughtSpot REST `searchdata`, SEC EDGAR).
3. **web_fetch** — birincil kaynağın bilinen URL'i üzerinde (FDA belgeleri, EMA EPAR, Resmi Gazete).
4. **web_search / Exa / Tavily** — yalnızca **URL keşfi** için; doğrulanabilir bir olgunun birincil alıntısı için **değil**.

Tier-0 güven gerektiren her iddia 1-3 yoluyla birincil kaynağa çözülmelidir.

---

## 1. Connector Envanteri ve Skill-Eşleme Matrisi

Sütunlar: **MR** = medical-research · **PI** = pharmaintel · **PP** = pharmapatent ·
**TS** = thoughtspot-roche · **RX** = rxos (orkestratör; doğrudan değil, alt-skill üzerinden tüketir).
Hücre: ● birincil/zorunlu · ○ koşullu/opsiyonel · — kullanılmaz.

### 1.A Türkiye Yerel Katmanı (kanonik — süitin omurgası)

| Connector | Endpoint / Kaynak | Araç sayısı | MR | PI | PP | TS | RX | Notlar |
|---|---|---|---|---|---|---|---|---|
| **TİTCK Cache MCP** *(birincil — kanonik public uç)* | `titck.cureonics.com/mcp` | 56 (proxy) | ● | ● | ● | — | ● | **v1.1 — kod-düzeyi tek-sefer (§3).** Ham TİTCK MCP'yi saran şeffaf önbellek proxy'si; `scope_key` başına upstream çağrısı ≤1 (SingleFlight DO + KV TTL). Araç yüzeyi upstream ile **aynı**. rxpraxis'te **kanonik TİTCK yolu budur.** |
| **TİTCK MCP** *(upstream / fallback)* | `titck-mcp-to7lqjgdkq-ew.a.run.app/mcp` | 56 | ○ | ○ | ○ | — | ○ | Cache Worker'ın upstream'i. Doğrudan yalnız Cache erişilemezse (§6 fallback) veya cache-bypass tazeleme için çağrılır. Master record + holder + ATC/SNOMED + fiyat + eşdeğer/biyobenzer grup + Madde 23 + withdrawal + batch release + off-label. |
| **Mevzuat MCP** | `mevzuat-mcp-…run.app/mcp` | 19 | ○ | ○ | ● | — | ● | SMK + yönetmelik + tebliğ + genelge + Resmi Gazete tam metin. 5 fonksiyonel kategori. İçtihat (Yargıtay/Danıştay/AYM) **kapsam dışı**. |
| **Türk Patent MCP** | `markapatent-mcp.fastmcp.app/mcp` | 6 | ○ | — | ● | — | ● | Patent + marka (Nice) + endüstriyel tasarım (Locarno). CPC/IPC + applicant + abstract. EP→TR validation. |
| **YÖK Tez MCP** | `yoktezmcp.fastmcp.app/mcp` | 6 | ● | — | ○ | — | ● | TR + EN tez araması; TR-spesifik epidemiyoloji/prevalans için ikincil kaynak. |

### 1.B Ticari / IQVIA MIDAS Katmanı (cross-country kalibrasyon)

| Connector | Endpoint / Kaynak | MR | PI | PP | TS | RX | Notlar |
|---|---|---|---|---|---|---|---|
| **ThoughtSpot Spotter MCP** | `agent.thoughtspot.app/mcp` | — | ● | — | ● | ● | Oturum-tabanlı beşli: `check_connectivity` · `create_analysis_session` · `send_session_message` · `get_session_updates` · `create_dashboard`. **Ham hücre döndürmez** (§4). |
| **MIDAS REST (`midas-mcp`)** | `midas-mcp.cureonics.workers.dev/mcp` (Cloudflare Worker → ThoughtSpot REST `searchdata`) | — | ○ | — | ● | ● | Ham sayısal değer yolu (Path B). `searchdata` zarfı: `contents[0].column_names` + `data_rows`. Auth → GUID çözümü → veri çekimi. **G9 no-fabrication.** |
| **MIDAS Spotter (agent)** | `agent.thoughtspot.app/mcp` | — | — | — | ● | ● | NLG + yapı doğrulaması; rakam için REST zorunlu. |

> **MIDAS küp envanteri:** MIDAS Monthly · MIDAS Disease Monthly · MIDAS Quarterly.
> Doğrulanmış attribute yüzeyi: **ATC1 Description · Product · Country** (ATC2/3/4 + molecule
> + manufacturer/corporation kırılımı). Değer birimi: **Total Swiss Franc + Standard Units**.
> Kümülatif-CHF **annualize edilir** (§5 + canonical-cache-contract §MIDAS).

### 1.C Regülatuar + Epidemiyoloji Katmanı

| Connector | Kapsam | MR | PI | PP | TS | RX | Notlar |
|---|---|---|---|---|---|---|---|
| **RegulatoryMCP (openFDA)** | openFDA drugsfda + label + FAERS | ● | ● | ○ | — | ● | **Native** çağrı (Python requests değil). Latency-prone: tekil çağrı + retry + skippable. |
| **RegulatoryMCP (ICD-11)** | WHO ICD-11 MMS kodlama | ● | — | — | — | ● | İndikasyon kodlama; TA-adaptif epidemiyoloji. |
| **RegulatoryMCP (WHO GHO)** | Global Health Observatory | ● | — | — | — | ● | Hastalık yükü/insidans/mortalite; onkoloji-dışı epidemiyoloji çapası. |
| **EMA EPAR (web_fetch)** | EPAR PDF | ● | ● | ● | — | ● | Birincil URL üzerinden; native MCP yok. |
| **FDA Orange/Purple Book** | Patent + exclusivity listingi | — | ● | ● | — | ● | NCE/data exclusivity; patent typology girişi. |

### 1.D Akademik Çekirdek (kanıt sentezi)

| Connector | Endpoint / Kaynak | MR | PI | PP | TS | RX | Notlar |
|---|---|---|---|---|---|---|---|
| **PubMed / EuropePMC MCP** | `pubmed.mcp.claude.com/mcp` | ● | ● | ○ | — | ● | ≥2 sorgu × 25; çok-ülke AFF döngüsü (6 ülke) atlanamaz. |
| **ClinicalTrials MCP** | `hcls.mcp.claude.com/clinical_trials/mcp` | ● | ● | — | — | ● | v2 yapılı sorgu; pivotal RCT NCT eşleme. |
| **bioRxiv MCP** | `hcls.mcp.claude.com/biorxiv/mcp` | ● | ● | — | — | ● | Preprint sinyali; PubMed timeout fallback'i. |
| **Consensus MCP** | `mcp.consensus.app/mcp` | ● | ● | — | — | ○ | Kanıt sentezi evet/hayır verdiktleri. |
| **Scholar Gateway MCP** | `connector.scholargateway.ai/mcp` | ● | ● | — | — | ○ | Semantik akademik korpus; PubMed fallback. |
| **Paper Search MCP** | `server.smithery.ai/@adamamer20/paper-search-mcp-openai` | ● | ● | — | — | ○ | Çok-kaynak akademik agregasyon + full-text indirme. |
| **AdisInsight MCP** | `adisinsight-mcp.springer.com/mcp` | ● | ● | — | — | ● | **REAL şema** (`search_drugs`/`get_drug` HyDE/`search_drug_companies`/`generate_chart`). Pipeline + originatör çapası. medical-research §1.O yalnız 0.5.I sinyalinde gate. |
| **Exa MCP** | `mcp.exa.ai/mcp` | ● | ● | ● | — | ● | Semantik web + full-text; kılavuz/HTA PDF (NICE/ESMO/NCCN). URL keşif önceliği. |
| **Tavily MCP** | `mcp.tavily.com/mcp` | ● | ● | — | — | ○ | Gerçek-zamanlı haber/finans; 432/error → Exa fallback. |
| **NPI Registry MCP** | `hcls.mcp.claude.com/npi_registry/mcp` | ● | — | — | — | — | ABD PI/KOL doğrulaması. |

### 1.E Tam Metin Geri Çağırma (copyright-disiplinli)

| Connector | Kapsam | MR | PI | PP | TS | RX | Notlar |
|---|---|---|---|---|---|---|---|
| **EuropePMC PMC** | OA tam metin + `get_copyright_status` | ● | ○ | ○ | — | ○ | Yalnız analiz; verbatim toplu çoğaltma yasak; CC-BY alıntılanabilir. |
| **Paper Download** | DOI tam metin | ● | ○ | — | — | — | Cascade son halkası. |

---

## 2. Connector→Skill Sorumluluk Sınırı (kim neyi çağırır)

Süit içinde connector çağrı sorumluluğu **tek skill'e** atanır; orkestratör çift çağrıyı
engeller. Bu, hem token tasarrufu hem provenance tutarlılığı içindir.

| Veri alanı | Kanonik sahip skill | rxos aşaması | Diğer skill'ler nasıl erişir |
|---|---|---|---|
| Global tedavi peyzajı (literatür + trial + pipeline) | **medical-research** | Aşama 1 | `treatment_landscape.json` artefaktından okur |
| Üç-otorite regülatuar matris (FDA/EMA/MHRA/PMDA) | **pharmaintel** (Regulatory) | Aşama 2 | `regulatory_matrix.json` |
| TİTCK kanonik dosya (master+holder+ATC+SNOMED+fiyat+eşdeğer) | **pharmapatent** (Mod 13) | Aşama 2 (bir kez) | `regulatory_matrix.titck_canonical` — Aşama 4 **tekrar sormaz** |
| Eşdeğer grup doygunluğu + withdrawal trend | **pharmaintel** (M4/M6) | Aşama 2 | `regulatory_matrix.{equivalent_group,withdrawal_trend}` |
| Patent ekosistemi + FTO + LOE + Bolar + SPC | **pharmapatent** (Mod 13→1→5→9) | Aşama 4 | `feasibility_matrix.json` |
| Biowaiver/BCS + Reliance hedefi | **pharmaintel** (M5/M7) | Aşama 4 | `feasibility_matrix.{biowaiver_bcs,reliance_target}` |
| 36-ülke MIDAS cross-country sizing | **thoughtspot-roche** | Aşama 5b | `commercial_opportunity.cross_country_sizing` |
| TR commercial sizing + fiyat tavanı + scorecard | **pharmaintel** (M1/M2/M3) | Aşama 5a/c | `commercial_opportunity.{pricing_formula,m1_scorecard}` |

---

## 3. Tek-Sefer TİTCK Kuralı (kritik connector disiplini)

TİTCK MCP, süitte **üç skill** tarafından çağrılabilir (medical-research Türkiye Dörtlüsü,
pharmaintel Channel A, pharmapatent Mod 13). rxos orkestrasyonunda bu çağrılar **tek bir
çağrı kümesinde** toplanır:

1. Aşama 2'de pharmapatent **Mod 13** TİTCK kanonik dosyasını **bir kez** çıkarır:
   `search_drugs` (FTS5 smart) + `get_drug` + `get_drug_snomed_profile` + `get_holder_portfolio`
   + `get_atc_class_summary` + `find_first_in_class`.
2. Çıktı `regulatory_matrix.titck_canonical` alanına yazılır.
3. Aşama 4 (pharmapatent FTO) ve diğer TİTCK-bağımlı modüller bu artefaktı **okur**, yeniden
   sorgulamaz. **Çift sorgu yasaktır.**

Bu kural canonical-cache-contract.md §TİTCK ile birlikte normatiftir.

**v1.1 (kod-düzeyi zorlama — dağıtıldı).** Tek-sefer TİTCK kuralı artık `titck-cache-mcp`
Worker'ı (`titck.cureonics.com`) tarafından **deterministik** uygulanır:
`scope_key = sha256(tool + canonical(args))` başına upstream çağrısı ≤ 1 — **SingleFlight
Durable Object** eşzamanlı özdeş çağrıları tek-uçuşa birleştirir (cache stampede önleme), **KV
TTL** ikinci-kat kenar önbellektir. Üç skill artık ham TİTCK yerine **TİTCK Cache** connector'ını
çağırır; aynı `(tool, args)` ikinci kez istense de upstream **vurulmaz**. `single_shot_enforced`
artık model beyanı değil, Worker `/ledger` ucundan **ölçülebilir** bir değişmezdir:
`upstream_calls ≤ distinct_scopes`. Cache erişilemezse §6 fallback ile ham TİTCK MCP'ye düşülür
(caveat damgası). İnşa ayrıntısı: `titck-cache-mcp-build-playbook.md`.

---

## 4. ThoughtSpot Ham-Hücre Asimetrisi (kritik MIDAS disiplini)

Oturum-tabanlı Spotter MCP (`get_session_updates`) **ham sayısal hücre döndürmez** — yalnız
NLG + şema + sıralama döner. Niceliksel rapor (gerçek rakamlı tablo) için **Path B**
zorunludur:

- **Path B (önerilen):** MCP-dışı REST `searchdata` (midas-mcp Worker veya doğrudan
  ThoughtSpot REST v2.0). Yanıt zarfı: `contents[0].column_names` + `data_rows`. Header
  preamble **yoktur**.
- **Native export:** Render edilen yanıttan CSV; ilk üç satır Roche extract preamble'ıdır
  (atlanır). Bilimsel notasyon (`2.82E12`) → `2,82 trilyon CHF`.

**G9 — No fabrication:** Görselden okunamayan rakam **asla** uydurulmaz; ham değer REST
veya native export ile alınır; erişim yoksa açıkça beyan edilir.

---

## 5. MIDAS Annualizasyon Sözleşmesi (zorunlu)

Tüm MIDAS-türevi değerler kümülatif-CHF olarak gelir ve **annualize edilmeden** penetrasyon
hesabına sokulamaz:

```
annualized_chf = raw_chf × (12 / time_span_months)
```

Tüm dalgalar **aynı sabit explicit pencereyi** paylaşır (örn. `between 2024-01 and 2025-12`).
Her MIDAS-türevi alan şu damgaları taşır: `time_basis` + `annualization` +
`(datasource_guid, session_identifier, generation_number, frame_url, extract_timestamp_utc)`
+ `roche_confidential: true`.

---

## 6. Fallback Zincirleri (MCP hata/timeout protokolü)

Her fallback rapora caveat olarak kaydedilir (run_manifest + §Limitations).

| Connector | Tetikleyici | Fallback zinciri | Caveat etiketi |
|---|---|---|---|
| **Türk Patent MCP** | service balance / timeout | Espacenet → Patentscope WIPO → USPTO → Google Patents | `"Türk Patent MCP hata; TR sicil web proxy"` |
| **TİTCK Cache MCP** | Worker 5xx / timeout | Ham **TİTCK MCP** (doğrudan, önbeleksiz) → cached registry → tekil barcode → manuel web fetch | `"TİTCK Cache hata; ham upstream <ISO>"` |
| **ThoughtSpot** | `$0.00` / boş veri | Attribute swap (Product→International Brand) → country swap → ATC4 proxy → cube swap → 36-ülke dekompozisyon | `"ThoughtSpot empty; attribute swap"` veya `"N/36 data-redacted"` |
| **PubMed/Consensus** | ratelimit / timeout | Exa academic → Scholar Gateway → bioRxiv → Paper Search | `"PubMed rate-limit; <alt> triangulate"` |
| **RegulatoryMCP (openFDA)** | latency stall | Tekil çağrı + 1 retry → skippable | `"Regulatory MCP gecikme; tekil+retry"` |
| **Tavily** | 432 / error | Exa fallback | `"Tavily kotası; Exa-fallback"` |

---

## 7. Provenance Damgası Standardı (özet — tam metin shared/provenance-standard.md)

Her veri noktası kaynağına göre damgalanır:

- **MCP:** `[<MCP adı> / <tool> / <erişim ISO>]` — örn. `[TİTCK MCP / get_price_history / 2026-06-14]`
- **Mevzuat:** `[Mevzuat MCP / search_mevzuat / SMK 6769 / 2026-06-14]`
- **MIDAS:** `(datasource_guid, session_identifier, generation_number, frame_url, extract_timestamp_utc)` + `roche_confidential: true`
- **Akademik:** Vancouver (PMID/DOI/NCT + erişim tarihi)
- **Web:** kaynak + erişim tarihi (yalnız URL keşfi sonrası birincil doğrulama ile)

---

## 8. Connector Sağlık-Kontrolü (start skill tarafından çalıştırılır)

`rxpraxis:start` skill'i her oturum başında bağlı connector'ları gruplar ve hangilerinin
canlı olduğunu raporlar. Pre-flight zorunluları:

- **ThoughtSpot:** `check_connectivity` → `{"success": true}` gelmezse Aşama 5 Bölüm B atlanır (degrade mod).
- **TİTCK MCP:** `server_info` veya `list_datasets` → 20 modül yanıtı.
- **Türk Patent MCP:** servis bakiyesi kontrolü.
- **RegulatoryMCP:** latency-prone; skippable olarak işaretle.

---

## 9. Devre-Kesici Protokolü (Circuit Breaker — kritik dayanıklılık disiplini)

§6 fallback zincirleri *hangi* alternatife düşüleceğini tanımlar; **§9** ise *ne zaman*
bir connector'ın "açık" (devre dışı) sayılacağını, kaç deneme yapılacağını ve durumun nereye
yazılacağını tanımlar. Komutların **Adım 0** pin-load'ı ve **Pre-flight (§8 + §9)** adımı bu
protokolü uygular. Her devre durumu `scan-ledger.circuit_breakers` (bkz. `shared/scan-ledger-schema.json`)
ve karar kartının **Katman B İç Denetim Kaydı**'na yazılır.

### 9.1 Devre durumları

| Durum | Anlam | Geçiş |
|---|---|---|
| **CLOSED** | Connector sağlıklı; çağrılar normal akar. | 2 ardışık başarısızlık → OPEN |
| **HALF_OPEN** | Soğuk-başlangıç şüphesi; **1 retry** denenir. | retry OK → CLOSED · retry FAIL → OPEN |
| **OPEN** | Connector devre dışı; çağrı yapılmaz, fallback (§6) veya degrade. | Sonraki çağrı kümesinde tek HALF_OPEN prob ile sınanabilir |

**Eşik:** **2 ardışık başarısızlık → OPEN** (tek geçici hata devreyi açmaz). **Soğuk-başlangıç
istisnası:** serverless/Worker tabanlı connector'larda (MIDAS, TİTCK Cache, ThoughtSpot) ilk
çağrıda araç-keşfedilemezlik/`tools-list` boşluğu genelde cold-start'tır → doğrudan OPEN değil,
**HALF_OPEN + 1 retry** (deploy/soğuk başlangıç toparlanır).

### 9.2 Connector-özel devre davranışı

| Connector | OPEN tetikleyici | Açıkken davranış | Karar etkisi |
|---|---|---|---|
| **TİTCK Cache** | `"No approval received"` (per-call approval-gate) **veya** 5xx | **Anında** ham `TİTCK:*` raw'a failover (veri **bayt-aynı**); devre "approval-gated", bug değil. Worker tamamen erişilemezse §6 zinciri. | Karar **etkilenmez** (failover şeffaf); `single_shot_enforced` raw modda caveat-damgalı. |
| **Türk Patent** | service balance / Capsolver / timeout, 2 başarısızlık | Espacenet → Patentscope WIPO → USPTO → Google Patents + (ABD) Orange/Purple Book **dokümante-public-fact**. Patent **yön-yalnız** (sayısal LOE tarihi YOK). | `feasibility_matrix.patent_section = VIABLE_WITH_CAVEAT`; net karar **CONDITIONAL** caveat taşır. **Sessizce "engel yok/var" VARSAYMA.** |
| **MIDAS / ThoughtSpot** | `midas_health` ≠ `{"ok":true}` / `check_connectivity` Pong yok | Önce **HALF_OPEN + 1 retry** (cold-start). Kalıcıysa OPEN → Aşama 5b degrade; §6 attribute/country/cube swap. | Rapor `"N/36 data-redacted"` caveat'ı; TR-iç katman ile degrade. |
| **PubMed / akademik** | ratelimit / timeout, 2 başarısızlık | §6: Exa → Scholar Gateway → bioRxiv → Paper Search cascade. | Kanıt sentezi degrade; caveat damgası. |
| **openFDA / Regulatory** | latency stall | tekil çağrı + 1 retry → skippable (zaten §8). | Atlanabilir; üç-otorite matrisi eksik-alanlı. |

### 9.3 Approval-gate ↔ raw failover (TİTCK'e özgü)

TİTCK Cache Worker'ı **per-call approval-gate** uygular; `"No approval received"` **beklenen**
bir durumdur (hata değil). Doğru davranış: ham `TİTCK:search_drugs` / `TİTCK:get_drug` raw'a
**anında** geç — veri bayt-aynıdır, karar değişmez. Bu, `tool-manifest.json` `collision_resolution`
ile uyumludur: `search_drugs` kanonik bağlamda TİTCK Cache; approval-gate'te raw TİTCK. Bu
failover bir caveat olarak (`"TİTCK Cache approval-gate; ham upstream <ISO>"`) raporlanır ama
**devreyi kalıcı OPEN saymaz**.

### 9.4 Ledger entegrasyonu (zorunlu)

Her devre olayı şuraya yazılır:

```yaml
scan-ledger.circuit_breakers:
  - connector: "Türk Patent"
    state: OPEN
    opened_at: "<ISO>"
    trigger: "service_balance"
    failover: "Espacenet+OrangeBook (direction-only)"
    decision_impact: "patent_section=VIABLE_WITH_CAVEAT"
```

ve karar kartının **Katman B (İç Denetim Kaydı)**'na özetlenir. Açık devre içeren hiçbir koşum
"temiz" işaretlenmez; etkilenen karar bölümü ilgili caveat'ı taşır.

> **Altın kural:** Bir connector OPEN olduğunda **sessiz varsayım yasaktır.** Patent için
> "engel yok" varsayma; MIDAS için "pazar küçük" varsayma; eksik veriyi açıkça caveat olarak
> beyan et ve kararı `CONDITIONAL`/`degraded` damgalar.
