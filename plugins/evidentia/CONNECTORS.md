# CONNECTORS.md — evidentia Connector Tek Doğruluk Kaynağı

> **Normatif.** Bu dosya, `evidentia` plugin'inin connector envanteri, native-first
> fallback zincirleri, güven sınıflandırması ve claude.ai uyumluluk yargıları için **tek
> doğruluk kaynağıdır**. `.mcp.json` bundled roster'ı bu dosyayla **çapraz-doğrulanır**
> (G-BUNDLE kapısı). Skill içi `skills/medical-research/references/connector-registry.md`
> standalone kullanım için korunur; süit bağlamında çakışmada **bu dosya üstündür**.
>
> Orkestrasyon disiplini (tek-sefer fetch, kanonik önbellek):
> [shared/canonical-cache-contract.md](./shared/canonical-cache-contract.md).
>
> **PRISMA araç sırası (bağlayıcı):**
> [skills/medical-research/references/execution-map.md](./skills/medical-research/references/execution-map.md)
> — 20 bundled sunucu + 13 companion için MUST/SHOULD/MAY/OUT + `SKIP-REASON`.
> Bu dosya envanterdir; playbook sıradır. Sessiz atlama Completeness Gate ihlalidir.

---

## 1. Connector Envanteri (beş grup + güven katmanı)

claude.ai yargısı: 🟢 Directory-Verified / Remote-Ready · 🟡 Hostable-Remote · 🔴 Local-Only.
Güven: **resmi-ns** (com.x / ai.x ters-DNS) · **topluluk** (io.github.x) · **operatör**
(Cureonics Worker) · **Anthropic HCLS** (hcls.mcp.claude.com / pubmed.mcp.claude.com dizini).

**Katmanlama (v9.1 — bibliyografik çekirdek birincil, alan-connector'ları opsiyonel):** §1.1
**Bibliyografik Çekirdek** her PRISMA taramasının konudan bağımsız yüklediği **her-zaman-açık**
settir (P1 arama → P2 getirim → P4 tam-metin). §1.2/§1.3 (curated intelligence + mekanizma;
regülatuar/epidemiyoloji/Türkiye/IP) yalnız Adım 0.5 ilgili bağlamı işaretlediğinde yüklenen
**opsiyonel, zenginleştirme-modülü-kapılı** katmanlardır. §1.5 (Genişletme Katmanı) ve self-host
Tier-O (§1.6) da aynı şekilde opsiyonel/sinyal-kapılıdır. Çekirdek hiçbir opsiyonel connector'ın
bağlı olmasına bağımlı değildir; bir opsiyonel modülün yokluğu yalnız o modülü bozar, temel PRISMA
hattını değil.

### 1.0 Directory Connector Tier (claude.ai hesap-düzeyi; `.mcp.json`'da bildirilMEZ)

**Bu connector'lar tıbbi çekirdeğin bir bölümünü sağlar (PubMed/EPMC, ClinicalTrials, Consensus,
Elicit…) ama `.mcp.json` bundled roster'ında STATİK URL ile bildirilMEZ.** Nedeni yapısaldır:
directory/OAuth connector'lardır — bağlanmaları hesap-düzeyinde, interaktif OAuth tarayıcı-dansı
gerektirir; statik `type:http` + statik Bearer ile plugin roster'ına gömülemezler. Plugin bunları
**referansla** entegre eder: `medical-research` skill araçları **ad'la** çağırır (§2 merdivenleri),
fiili bağlanma aşağıdaki yüzey-adımıyla yapılır. Preflight (`start` Adım 2) hangilerinin bağlı
olduğunu raporlar; `.claude/evidentia.local.md` `known_connected:` ile bağlı-kabul edilip tekrar
probe'lanmaları önlenir (`docs/evidentia.local.md.example`).

| Connector | Yüzey & bağlama adımı | Auth | Skill'in çağırdığı araçlar | Katman |
|---|---|---|---|---|
| **PubMed / Europe PMC** | claude.ai: **Directory'den etkinleştir** · Claude Code: `claude mcp add --transport http pubmed <hcls-url>` + tek-sefer OAuth | Anthropic HCLS OAuth | `search_articles`, `get_full_text_article`, `get_copyright_status`, `convert_article_ids` | A (çekirdek §1.1) |
| **ClinicalTrials v2** | claude.ai: **Directory'den etkinleştir** | none / HCLS | `search_trials`, `get_trial_details`, `search_by_sponsor`, `analyze_endpoints` | K* (çekirdek §1.1) |
| **Consensus** | claude.ai: **Directory** (`bio-research:consensus`) | API / OAuth | `search` (kullanım-mesajı **birebir** reprodüksiyon; ≤3/batch; filtre yalnız kullanıcı isterse) | A (çekirdek §1.1) |
| **Scholar Gateway** | claude.ai: **Directory / workspace** | API | `semanticSearch` | A (çekirdek §1.1) |
| **bioRxiv / medRxiv** | claude.ai: **Directory'den etkinleştir** · Claude Code: Hub stdio `biorxiv-mcp` (rxpraxis) | none / HCLS | `search_preprints` (preprint flag zorunlu) | K (çekirdek §1.1) |
| **Scite** | claude.ai: **Directory'den etkinleştir** | API / OAuth | Oturum schema'sı — smart citations / evidence sentences (P1.9 SHOULD) | A (çekirdek §1.1) |
| **Elicit** | claude.ai: **Settings → Connectors → OAuth** (`elicit.com/api/mcp`); §9 "WIRE secondary" | OAuth | `search_papers`, `search_trials`, `list_reports`, `get_report` | secondary (OAuth) |
| **AdisInsight** | claude.ai: **Settings → Connectors → OAuth** (Springer) | OAuth (API) | `search_drugs`, `get_drug`(HyDE), `generate_chart` — yalnız 0.5.I sinyali | A (opsiyonel §1.2) |
| **SNOMED CT Terminology** | claude.ai: **Directory'den etkinleştir** | HCLS / API | SNOMED search / validate / expand (P4 coding MAY) | K* (terminology) |
| **BioRender** | claude.ai: **Directory / OAuth** | OAuth | Figure library / template / generation — **P7 görsel ONLY** | visual (kanıt değil) |
| **NPI Registry** | claude.ai: **Directory'den etkinleştir** | none / HCLS | `npi_search`, `npi_lookup`, `npi_validate` — yalnız ABD-KOL sinyali | K* (opsiyonel §1.3) |

> **Claude vs self-host (Evidentia):** Bundled `pubmed-epmc`, `openalex`, `semantic-scholar`,
> `marmara-ebsco`, `openathens` filoda **birincil** — Bearer/OAuth ile Claude Code'da otomatik.
> Directory companion'lar (PubMed HCLS, Clinical Trials, bioRxiv, Consensus, Elicit, Scite,
> AdisInsight, SNOMED, BioRender, Paper Search, YÖK Tez, Wiley, Literatür) hesap düzeyinde
> bağlanır; yüklü değilse `SKIP-REASON companion_unloaded` + fleet degrade (execution-map).
> bioRxiv: HCLS boş-gövde bug'ında Hub stdio `mcp-servers/biorxiv-mcp` tercih edilir.
>
> **Kural:** Bu satırlar `.mcp.json`'a **eklenmez** (G-BUNDLE kapısı bunu bekler). Yüklü değilse
> `SKIP-REASON companion_unloaded`. **Yüzey ayrımı §6'da normatiftir**; Tier-K/Tier-O statik-URL
> connector'ları (who-gho, openfda, anamnesis, med-terminologies, marmara-ebsco…) `.mcp.json`'da
> bildirilir ve Claude Code'da otomatik bağlanır.

### 1.1 Bibliyografik Çekirdek (her-zaman-açık getirim seti)
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| PubMed / Europe PMC | 🟢 | API | search_articles · get_full_text_article · get_copyright_status · convert_article_ids (+3) | Anthropic HCLS | A |
| Clinical Trials v2 | 🟢 | none | search_trials · get_trial_details · search_by_sponsor · analyze_endpoints (+2) | Anthropic HCLS | K* |
| Consensus | 🟢 | API | search (kullanım mesajı birebir reprodüksiyon; ≤3/batch) | resmi | A |
| Scholar Gateway | 🟢 | API | semanticSearch | operatör/resmi | A |
| Paper Search | 🟢 | API | search · read_pubmed_paper · download_* (tam-metin tier 2) | topluluk | A |
| bioRxiv / medRxiv | 🟢 | none | search_preprints (preprint flag zorunlu) | Anthropic HCLS / Hub stdio | K |
| Scite | 🟢 | API | smart citations / evidence sentences (schema oturumdan) | resmi | A |
| Elicit | 🟢 | OAuth | search_papers · list_reports (SR-aid; cross-validate) | resmi | A |
| BioRender | 🟡 | OAuth | figure templates / generation (P7 only — not evidence) | resmi | visual |
| SNOMED CT Terminology | 🟢 | HCLS | SNOMED search/validate/expand (companion; ICD-11 primary elsewhere) | Anthropic HCLS | K* |
| YÖK Tez | 🟢 | none | search_yok_tez_detailed · get_yok_tez_document_markdown (+2) | operatör | A |

**Tam-metin rung'u (P4, çekirdeğin parçası — enrichment-kapılı DEĞİL):**
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| **marmara-ebsco** (self-host, `https://ebsco.cureonics.com/mcp`) | 🟡 | OAuth/Bearer | 4 araç: `ebsco_server_info` · `ebsco_list_databases` · `ebsco_search` · `ebsco_get(record_id, prefer, collection?, doc_id?)`. **Tam-metin Tier 3: LİSANSLI BİRİNCİ deneme** (Marmara VETİS→EBSCOhost; OpenAthens'in önünde). Miss → SKIP-REASON + Tier 4. Kod hazır; HP deploy/tunnel operatör kapısı | operatör self-host | O |
| **openathens** (self-host, `https://openathens.cureonics.com/mcp`) | 🟢 | OAuth/Bearer | 11 araç, ölçüm 2026-08-14: `oa_resolve` · `oa_fetch_fulltext`(metin/ingest; collection?) · **`oa_fetch_pdf(doi\|url)`** · `oa_verify_access` · `oa_list_databases` · `oa_session_status` · `oa_batch_submit`/`oa_batch_result` · `search`/`fetch`. **Tam-metin Tier 4: LİSANSLI İKİNCİ deneme**, annas'ın önünde | operatör self-host | O |
| annas-reader | 🟡 | Bearer | 9 araç, ölçüm 2026-08-14: reader + **`download_document(id=DOI\|32-hex MD5)`**. (**Tier 6 SON ÇARE**, lisanslı band'dan sonra; yalnız analiz) | operatör self-host | O |
| Unpaywall (pubmed-epmc üzerinden) | 🟢 | none | pubmed_fetch_fulltext (EuropePMC + Unpaywall yasal-OA çözümü; Tier 7 son legal-OA süpürmesi) | topluluk (cyanheads) | K |

**RAG substratı (retrieve-don't-dump, çekirdeğin parçası — enrichment-kapılı DEĞİL):**
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| anamnesis (self-host) | — | OAuth/Bearer | ingest_document · semantic_search · hybrid_query · graph_neighbors · list_docs · corpus_stats · forget_document · forget_collection | operatör self-host | O |
| evidentia-kb (self-host) | — | OAuth/Bearer | kb_search — Adım 0.4 semantik yönlendirme takviyesi (bağlı değilse map-only degrade) | operatör self-host | O **`kb_forget(file=…|id=…)`** (SADECE-KURULUM, yıkıcı) 2026-08-08'de eklenen geçersizleştirme yolu: chunk id'si `md5(dosya+başlık)` taşıdığı için `kb_upsert`'ün INSERT OR REPLACE'i DEĞİŞEN/SİLİNEN başlığı asla üzerine yazmaz — satır yetim kalır ve `kb_search` onu güncel rehber diye döndürür (ölçüldü: canlı indeks emekli `article_download` API'sini hâlâ veriyordu). `scripts/kb_ingest.py` artık her dosyayı yeniden eklemeden önce temizliyor. |

> **WEB TIER KALDIRILDI (v1.4.0):** Exa ve Tavily — ve OSINT ekseni — **tamamen çıkarıldı**.
> evidentia artık **saf yapısal-otoriter kanıt motorudur**: hiçbir web-arama/scraping fallback'i yoktur.
> Bir veri yapısal connector'larda (PubMed/EPMC, OpenAlex, S2, CT.gov, openFDA, TİTCK, NPI …)
> bulunamıyorsa sonuç dürüstçe **"VERİ YOK / bulunamadı"** olarak raporlanır — ASLA uydurulmaz.
> Native-API'si olmayan kaynaklar (ESMO/NCCN/NICE kılavuz PDF'leri, IHME/GBD) bu nedenle
> **erişilemez bir boşluk** olarak işaretlenir. **(WHO GHO, GLOBOCAN ve EMA artık boşluk DEĞİL** —
> küresel/ülke yük için `who-gho`, küresel kanser insidans/mortalite için `globocan`, AB ruhsat +
> CHMP/EPAR için `ema` native connector'ları eklendi, §1.3/§1.6. **IHME/GBD** (kamuya açık API yok,
> hesap+ToS+satır-limiti) ve **toplum-kılavuz PDF'leri** boşluk olarak kalır.)
>
> **Bundled Tier-A statik URL'leri (`.mcp.json`):** YOK. **(RegulatoryMCP/Cureolex Tier-A girdisi
> KALDIRILDI** — karşılaştırmalı-hukuk araçları medikal kanıtta gürültüydü; yerine self-host **`openfda`**
> Tier-O + ICD-11 için aynı `openfda` Worker'ın `icd11_search`'ü; bkz §1.6.) Tier-A connector'lar
> (PubMed/EPMC, Consensus, AdisInsight, TİTCK, Türk Patent, …) operatör workspace / claude.ai
> dizin connector'larıdır → roster'da statik URL ile **bildirilmez**; envanter + Settings ile bağlanır (§6).

### 1.2 Curated Intelligence + Mekanizma — OPSİYONEL (zenginleştirme-modülü-kapılı)
**Yalnız Adım 0.5 Drug Intelligence (0.5.I) veya mekanizma/hedef sinyali işaretlediğinde yüklenir.**
Yokluğu yalnız ilaç-zekası/mekanizma modülünü bozar — bibliyografik çekirdek (§1.1) etkilenmez.

| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| AdisInsight | 🟢 | API | search_drugs · get_drug(HyDE) · generate_chart (+3) — **gerçek şema** (drug-intelligence-layer.md); eksen 0.5.I | resmi (Springer) | A |
| ChEMBL | 🟢 | none | drug_search · get_mechanism · get_admet · target_search | bio-research | A |
| Synapse | 🟡 | OAuth | authenticate → multi-omics (0.5.J) | bio-research | A (conditional) |
| OpenTargets | 🔴 | — | (offline son probe'da) → ChEMBL target_search fallback | bio-research | A (offline) |
| Wiley | 🟡 | OAuth | authenticate → publisher tam-metin (tier 5). **Companion** — statik `.mcp.json` URL'si yok; claude.ai / Cursor Settings → Connectors. Operatör sırrı fleet.yaml'da tutulmaz; bağlanmamışsa graceful skip. | bio-research | A (conditional) |

### 1.3 Regülatuar + Epidemiyoloji + Türkiye + IP — OPSİYONEL (zenginleştirme-modülü-kapılı)
**Yalnız Adım 0.5 Regulatory (0.5.C), HTA (0.5.D), Epidemiyoloji (0.5.K) veya Türkiye pazarı
bağlamı işaretlendiğinde yüklenir.** Bu **kanıt-bağlamı zenginleştirmesidir**, kendi başına
ticari/regülasyon istihbaratı DEĞİLDİR — ticari strateji `pharmaintel`'e, MLR `promo-censor`'a,
bireysel SGK/geri-ödeme `onko-erisim`'e, patent-özel iş `pharmapatent`'e, karşılaştırmalı-hukuk
soruları `cureolex`/`health-policy`'ye yönlendirilir. Yokluğu yalnız işaretlenen modülü bozar —
bibliyografik çekirdek (§1.1) etkilenmez.

| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| **openfda** (self-host) | — | OAuth/Bearer | `openfda_search` (drug/event·label·drugsfda·enforcement·device/*, api.fda.gov keyless) + `icd11_search` (WHO ICD-11 MMS, server-side OAuth) — hızlı. **(RegulatoryMCP/Cureolex yerine; ICD-11 buradan; WHO GHO/Health Canada/EUR-Lex çıkarıldı)** | operatör self-host | O |
| **PopHIVE** (US epi · v8.5) | 🟢 | none | `get_current_status` · `get_trend` · `get_map` · `get_coverage` · `compare` · `get_data` — Yale harmonize **ABD** sürveyans (ED/hastane/atıksu/lab + çocukluk aşı kapsamı). **YALNIZCA ABD** (global/Türkiye yük için **who-gho**, aşağıda); precomputed kanıtı **birebir aktar, sayıyı yeniden-türetme**. Eksen 0.5.K → §1.P/§21 | Yale (kamusal, DOI 10.5281/zenodo.17345935) | K-epi |
| **who-gho** (self-host · global epi) | 🟢 | none (keyless) | `who_gho_search_indicators` (topic→GHO kodu) · `who_gho_query` (indicator_code + `country` ISO3/`GLOBAL`/region + `year` + `dim1`) · `who_gho_dimensions` (COUNTRY/SEX/AGEGROUP/REGION çözümü) — WHO **Global Health Observatory** OData: **küresel/ülke hastalık yükü·mortalite·risk-faktörü·kapsam** (Türkiye `TUR` dahil). **PopHIVE'ın ABD-only boşluğunu native KAPATIR** (kanser için globocan, IHME hâlâ boşluk). Değerler **modellenmiş+raporlanan** karışımı, nokta-zaman → her satır `caveat`; ülke/yıl yoksa boşluk (uydurma yok). `https://who-gho-mcp.cureonics.workers.dev/mcp` (keyless — upstream `ghoapi.azureedge.net` authless, server-side sır yok). Eksen 0.5.K | operatör self-host (WHO GHO upstream) | K-epi |
| **globocan** (self-host · global kanser) | 🟢 | none (keyless) | `gco_list_cancers` (41 site + ICD-10, ölçüm 2026-08-07) · `gco_resolve_population` (ISO3/ad→GLOBOCAN kodu; `TUR`=792) · `gco_query` (`population` + `cancer` + `sex` + `type` insidans/mortalite → total/ASR/crude/cum_risk_74/rank/UI) — IARC **Global Cancer Observatory GLOBOCAN 2022**: **küresel/ülke kanser insidans+mortalite** (185+ ülke, Türkiye dahil). **who-gho'nun genel GHO'sunu kanser-özelinde tamamlar**; IHME/GBD hâlâ boşluk. Değerler **MODELLENMİŞ TAHMİN** (ref. yıl 2022, ülke veri-yoğunluğuna göre metodoloji) → her satır `ui` belirsizlik aralığı + zorunlu `caveat`; kombinasyon yoksa boşluk (uydurma yok). `https://globocan-mcp.cureonics.workers.dev/mcp` (keyless — upstream `gco-api.iarc.fr` authless+headerless). Eksen 0.5.K / Onko | operatör self-host (IARC GLOBOCAN upstream) | K-epi |
| **ema** (self-host · AB regülatuar) | 🟢 | none (keyless) | `ema_search_medicines` · `ema_get_medicine` · `ema_filter` (ATC prefix+status+bayraklar) · `ema_stats` — EMA **Medicines/EPAR** baked korpus (2712 ilaç): AB merkezi **ruhsat durumu + CHMP opinion/decision tarihi** + orphan/conditional/accelerated/PRIME/advanced-therapy/biosimilar bayrakları + ATC/INN/MAH/endikasyon + **EPAR URL**. **RegulatoryMCP kaldırıldığında kalan EMA/CHMP boşluğunu kapatır** (openFDA'nın AB muadili). Nokta-zaman snapshot → `generated_at` + `caveat`; yoksa yokluk-kanıtı değil. Tam metin EPAR url'inde (talep üzerine anamnesis'e ingest). `https://ema-mcp.cureonics.workers.dev/mcp` (keyless — baked public XLSX, runtime upstream/sır yok). Eksen 0.5.C Regülatuar | operatör self-host (EMA XLSX baked) | O |
| TİTCK | 🟢 | none | search_drugs · get_drug · find_biosimilar_group · get_price_history · find_off_label_uses_for_drug (+11) | operatör | A |
| Türk Patent | 🟢 | API | search_patents · search_trademarks · get_patent_details (+1) | operatör | A |
| NPI Registry | 🟢 | none | npi_search · npi_lookup · npi_validate (ABD PI/KOL) | Anthropic HCLS | K* |

### 1.4 α-katman (operatör-bağlı, yüksek-güven · Tier-O) — OPSİYONEL (modülüne bağlı yükleme)
**Yalnız desteklediği opsiyonel modülle birlikte yüklenir** — TİTCK Türkiye-pazarı
merdiveninin (§1.3) fallback basamağıdır, YÖK Akademik opsiyonel Türk-KOL modülüdür; **Annas
Reader ise çekirdek tam-metin rung'unun (§1.1) parçasıdır**, opsiyonel değildir. Yokluğu yalnız
bağlı olduğu modülü/rung'u bozar.

| Connector | URL | Rol |
|---|---|---|
| **TİTCK** (kapılı) | `https://titck.cureonics.com/mcp` | **Kanonik** Türkiye ilaç indeksi — 66 araç, v0.5.8. ⚠️ Önbellek Worker'ı 2026-07-31'de emekli edildi → bu bir "yedek basamak" DEĞİL, bundle'daki TEK TİTCK; doğrudan çağrılır |
| YÖK Akademik | `https://yok-akademik.cureonics.com/mcp` | Türk KOL kimliklendirme (§8 TR katmanı; YÖK Tez'den FARKLI) |
| **Annas Reader** | `https://annas.cureonics.com/mcp` | **Tam-metin geri-çağırma** (HP self-host Docker, Bearer/OAuth-gated; 9 araç, 2026-08-14) — **full-text cascade Tier 6 (SON ÇARE)**, lisanslı band (Marmara EBSCO + OpenAthens + Wiley) getiremeyince. Reader akışı bounded metin verir; `download_document(id=DOI|MD5)` orijinal PDF/EPUB ve desteklenen diğer formatları kısa-ömürlü opaque resource link + checksum/provenance ile teslim eder. Link derhal tüketilir; uzun dosya anamnesis'e ingest edilir. **Telif:** yalnız analiz, toplu birebir çoğaltma YOK. |

### 1.5 Genişletme Katmanı (mcp-scout canlı-doğrulanmış · Tier-K · §6)
**Karışık katman — dikkat:** `openalex` / `pubmed-epmc` / `semantic-scholar` **bibliyografik
çekirdeğin** (§1.1) bundled tool yüzeyleridir, her-zaman-açıktır. `med-terminologies` /
`nih-clinicaltables` / `nlm-rxnorm` / `iuphar-gtopdb` ise **OPSİYONEL** Extended Tier-K'dır —
yalnız drug/terminology zenginleştirme sinyali (Adım 0.5) ateşlendiğinde çağrılır
(`connector-registry.md §2.6` tool-whitelist).

| Connector | URL | Probe (2026-06-25) | Rol | Güven |
|---|---|---|---|---|
| **med-terminologies** | `https://medical.sidneybissoli.com/mcp` | ✅ 200 · v1.5.7 · 31 araç (ölçüm 2026-08-07) | SNOMED/LOINC/RxNorm/MeSH/ATC çapraz-yürüyüş (⚠️ `icd11_search` sunucuda WHO creds yok → AUTH_CONFIG_ERROR; **ICD-11 için `openfda`**) | **topluluk-UNVERIFIED** |
| **nih-clinicaltables** | `https://gateway.pipeworx.io/clinicaltables/mcp` | ✅ 200 · keyless | NIH Clinical Tables (ICD/LOINC/NPI/condition) | topluluk · NIH upstream |
| **nlm-rxnorm** | `https://gateway.pipeworx.io/rxnorm/mcp` | ✅ 200 · keyless | RxNorm normalizasyonu (INN↔RxCUI) | topluluk · NLM upstream |
| **iuphar-gtopdb** | `https://gateway.pipeworx.io/guidetopharmacology/mcp` | ✅ 200 · keyless | GtoPdb hedef/ligand | topluluk · IUPHAR upstream |
| **openalex** | `https://openalex.cureonics.com/mcp` | ✅ HP self-host 2026-08-17 · 5 araç · SQLite cache · Worker undeploy | CureoHub HP systemd `:8324`. Bearer `OPENALEX_MCP_API_KEY`; opsiyonel `OPENALEX_API_KEY` günlük bütçeyi anahtara taşır. Eski `*.workers.dev` / caseyjhand uçları emekli | operatör HP self-host | K |
| **pubmed-epmc** | `https://pubmed.cureonics.com/mcp` | ✅ HP self-host 2026-08-17 · 11 araç · SQLite cache · Worker undeploy | CureoHub HP systemd `:8325`. Bearer `PUBMED_MCP_API_KEY`; opsiyonel `PUBMED_API_KEY` NCBI 429 bütçesini anahtara taşır. Eski `*.workers.dev` / caseyjhand uçları emekli | operatör HP self-host | K |
| **semantic-scholar** | `https://semanticscholar.cureonics.com/mcp` | ✅ HP self-host 2026-08-17 · 4 araç · SQLite cache · Worker undeploy | CureoHub HP systemd `:8323`. Yalnız 4 araç (en-az-yetki sunucu şeklinde). Bearer `SEMANTICSCHOLAR_MCP_API_KEY`; upstream `SEMANTIC_SCHOLAR_API_KEY`. Eski Worker / pipeworx gateway emekli | operatör HP self-host | K |

### 1.6 Self-Host (klinik DDI boşluğu + RAG/GraphRAG substratı + openFDA + WHO GHO + GLOBOCAN + EMA)
**Karışık katman — dikkat:** `anamnesis` ve `evidentia-kb` **bibliyografik çekirdeğin RAG
substratıdır** (§1.1) — her-zaman-açık, retrieve-don't-dump + Adım 0.4 yönlendirme için. `drugddx`,
`openfda`, `who-gho`, `globocan` ve `ema` ise **OPSİYONEL** — yalnız klinik-DDI / regülatuar / ICD-11 /
epidemiyoloji-yük / kanser-yükü / AB-ruhsat zenginleştirme sinyali ateşlendiğinde çağrılır (§1.3).
`who-gho`/`globocan`/`ema` üçü de **keyless** (drugddx gibi — authless upstream veya baked public veri,
server-side sır yok).

| Connector | URL | Durum |
|---|---|---|
| **drugddx** | `https://drugddx-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25) | β-aday `drug-interaction-mcp` HTTP 500 (CF 1101) → **self-host fork** (`self-host/drugddx-mcp/BUILD-BRIEF.md`). **Deployed + Tier-O roster'da** (2026-06-28 AÇIK/keyless — MCP_ALLOW_NO_AUTH=1, salt-okunur public-API proxy; no-auth initialize 200 · serverInfo drugddx-mcp v1.0.0). |
| **openfda** | `https://openfda-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25) | **openFDA tipli erişim** (`self-host/openfda-mcp/`) — `openfda_search`: drug/event (FAERS), drug/label, drugsfda, enforcement, device/*; upstream api.fda.gov (keyless), endpoint allowlist (SSRF-safe). **Deployed + Tier-O** (2026-06-28 Bearer-gated — RE-GATED: `icd11_search` WHO ICD-11 server-side OAuth cred confused-deputy/resource-abuse önlemi; authenticated initialize 200 · canlı FAERS count + drug/label doğrulandı). **RegulatoryMCP/Cureolex'ın YERİNE**: karşılaştırmalı-hukuk araçları medikal kanıtta gürültü olduğu için roster'dan çıkarıldı; **ICD-11 = bu Worker'ın `icd11_search`'ü** (WHO ICD-11 MMS API, server-side OAuth = ICD11_CLIENT_ID/SECRET; canlı 3B10.0 doğrulandı — `med-terminologies` icd11'i WHO creds yokluğundan çalışmıyor). ⚠️ FAERS sayımları spontan rapor, insidans değil. |
| **evidentia-kb** | `https://evidentia-kb-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-26) | **KB semantik recall takviyesi** (`self-host/evidentia-kb-mcp/`) — `kb_search(query,k)` SKILL.md+references/*.md'yi (knowledge-map.md HARİÇ) bge-m3 Vectorize ile arar (244 chunk/24 dosya). medical-research **Adım 0.4 + Completeness Gate** için OPSİYONEL; bağlı değilse map-only degrade. **Deployed + Tier-O** (401 SECURED · kb_search canlı, layer-file recall doğrulandı). `kb_upsert` = setup-only (`scripts/kb_ingest.py`). **`kb_forget(file=…|id=…)`** (SADECE-KURULUM, yıkıcı) 2026-08-08'de eklenen geçersizleştirme yolu: chunk id'si `md5(dosya+başlık)` taşıdığı için `kb_upsert`'ün INSERT OR REPLACE'i DEĞİŞEN/SİLİNEN başlığı asla üzerine yazmaz — satır yetim kalır ve `kb_search` onu güncel rehber diye döndürür (ölçüldü: canlı indeks emekli `article_download` API'sini hâlâ veriyordu). `scripts/kb_ingest.py` artık her dosyayı yeniden eklemeden önce temizliyor. |
| **who-gho** | `https://who-gho-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-07-05 · Version 30df2ff2 · E2E doğrulandı) | **WHO GHO OData tipli erişim** (`self-host/who-gho-mcp/`) — `who_gho_search_indicators`/`who_gho_query`/`who_gho_dimensions`; upstream `ghoapi.azureedge.net` (authless OData v4), SSRF-safe indicator-code allowlist. **KEYLESS by design** (`MCP_ALLOW_NO_AUTH=1`, drugddx precedent — server-side sır YOK, confused-deputy yok); hardened OAuth additive korunur (web connector). **Küresel/ülke hastalık yükü** — PopHIVE'ın ABD-only boşluğunu native kapatır; kanser için `globocan`, AB ruhsat için `ema`; IHME/GBD hâlâ boşluk. Değer WHO-otoriter ama modellenmiş+raporlanan → zorunlu `caveat`; ülke/yıl yoksa boşluk. Canlı doğrulama: WHOSIS_000001 SpatialDim='TUR' TimeDim=2019→77.6 [77.2-78.1]. Unit: server.test 12 + auth.test 15 yeşil (routing.test ajv-shim ortam sorunu, openfda ile aynı). |
| **globocan** | `https://globocan-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-07-05 · Version 74cfb636 · E2E doğrulandı) | **IARC GLOBOCAN 2022 live-proxy** (`self-host/globocan-mcp/`) — `gco_list_cancers`/`gco_resolve_population`/`gco_query`; upstream `gco-api.iarc.fr/api/globocan/v3/2022` (authless+headerless JSON; endpoint Playwright ile Cancer Today XHR'inden **ampirik yakalandı** 2026-07-05), SSRF-safe pop-code/cancer-id allowlist. **KEYLESS** (who-gho precedent). **Küresel/ülke kanser insidans+mortalite+prevalans** — who-gho'yu kanser-özelinde tamamlar; IHME/GBD hâlâ boşluk. Değer MODELLENMİŞ TAHMİN → `ui` + zorunlu caveat. **Path {type}/{sex}** (sex/type sırası bilinen-değerle doğrulandı; ilk sürümdeki swap düzeltildi). Canlı: Türkiye(792) female breast mortalite 7360/insidans 25249 (yayınlanan değerlerle birebir), male lung insidans 33039/mortalite 32119; all-cancers female 34 satır Meme rank 1, sessiz-kesme yok. Unit: server.test 13 + auth.test 15 yeşil (routing.test ajv-shim ortam sorunu). |
| **ema** | `https://ema-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-07-05 · Version ff226c89 · E2E doğrulandı) | **EMA Medicines/EPAR baked-corpus** (`self-host/ema-mcp/`) — `ema_search_medicines`/`ema_get_medicine`/`ema_filter`/`ema_stats`; `scripts/build_corpus.mjs` authless EMA XLSX'ini (`medicines-output-medicines-report_en.xlsx`, overnight yenilenir) SheetJS ile `src/data.gen.ts`'e bake eder (2712 ilaç; runtime XLSX-parse YOK — mufredat deseni). **KEYLESS** (baked public, sır yok). **AB ruhsat + CHMP/EPAR** boşluğunu kapatır (openFDA'nın AB muadili). Nokta-zaman → `generated_at`+caveat. Canlı: Keytruda→Authorised/L01FF02/opinion 2015-05-20; ema_filter(L01,authorised,orphan)→5 onkoloji; 1863 authorised. Unit: server.test 8 + auth.test 15 yeşil (routing.test ajv-shim). Yenile: `npm run build:corpus`+redeploy. |
| **anamnesis** | `https://anamnesis-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25 · RAG+GraphRAG E2E doğrulandı; **1.2.0 collection API kodda, canlı cutover HP wrangler + D1 migrate bekler**) | **RAG/GraphRAG retrieval substratı** — registry'de hosted GraphRAG MCP yok (`rag-knowledge-graph-mcp` yalnız yerel stdio) → **self-host** (`self-host/anamnesis-mcp/BUILD-BRIEF.md`). Semantik chunking (bge-m3 1024-d) + Vectorize + D1 bilgi grafiği + FTS5 lexical. **10 araç (v1.2.0):** `ingest_document` (collection yeni istemcide zorunlu, yoksa `_legacy`; re-ingest önce forget) · `semantic_search` (collection ve/veya `doc_id` / `doc_ids[]`) · `upsert_triples` · `graph_neighbors` · `subgraph` · **`hybrid_query`** (collection zorunlu; kapsamsız → MCP error) · `list_docs` · `corpus_stats` (collection yok = küresel gözlem, çalışma seti değil) · `forget_document` · **`forget_collection`** (SQL + Vectorize `deleteByIds`; başka koleksiyona dokunmaz). `collection={plugin}:{run\|sess\|lib}:{id}`; Evidentia scratch `evidentia:run:<12hex>`. `forget_by_prefix` API değildir. **ÇOK-SORGULU HİBRİT GETİRİM (özellik revizyonu v1.6.0 — ⚠️ bu bir ÖZELLİK etiketidir, dağıtım sürümü değil: `serverInfo` paket sürümünü yansıtır). Tam §4.1.1:** `queries[]` → vektör ∥ BM25 → RRF → rerank. §8 retrieval telemetri CF-log'da. **Bağlam-penceresi taşma koruması** (§3 → `evidence_index`). |

### 1.7 REST Fallback (Tier-R · bundle DIŞI)
Native MCP olmayan, `medical-research`'ün Python `requests` ile çağırdığı uçlar
(`references/extended-api.md`): **OpenAlex · PubChem · Semantic Scholar Graph · DailyMed ·
Unpaywall · DOAJ · J-STAGE · DrugBank**. `.mcp.json`'da **bildirilmez**.

---

## 2. Native-First Fallback Zincirleri (PRISMA faz bazında çözümleme merdivenleri)

Her veri ihtiyacı şu sırayla çözülür: **native MCP → REST → belgelenmiş boşluk**
("VERİ BULUNAMADI" + denenen sorgular). **Web tier (Exa/Tavily) v1.4.0'da kaldırıldı** —
yapısal kaynaklarda yoksa dürüstçe boşluk raporlanır, ASLA web-scraping/uydurma yapılmaz.
Merdivenler artık **PRISMA fazına göre** gruplanır: **P1 (arama stratejisi)** → **P2 (getirim/
dedup)** → **P4 (tam-metin zenginleştirme)**. P1/P2/P4 çekirdek merdivenleri (§1.1) her taramada
çalışır; Adım 0.5 etiketli satırlar yalnız ilgili opsiyonel modül ateşlendiğinde devreye girer.

### P1 — Arama stratejisi (çekirdek, her-zaman-açık)

| İhtiyaç | Merdiven |
|---|---|
| Bibliyografik arama (MeSH/Emtree + serbest metin) | `openalex` → `pubmed-epmc` → `semantic-scholar` → PubMed companion → Clinical Trials companion → bioRxiv companion → Consensus → Paper Search → Elicit companion → Scite companion → AdisInsight (0.5.I) → YÖK Tez |
| KOL / atıf-ağı / kurum-yazar | `openalex` (`openalex_resolve_name`→`search_entities`/`get_citation_graph`) → `semantic-scholar` → EPMC → NPI (US, **opsiyonel**) → YÖK Akademik (TR, **opsiyonel**) |

### P2 — Getirim & dedup (çekirdek, her-zaman-açık)

| İhtiyaç | Merdiven |
|---|---|
| Çekirdek akademik getirim | PubMed/EPMC → Clinical Trials v2 `search_trials` → bioRxiv/medRxiv `search_preprints` → Paper Search → `openalex`/`semantic-scholar`/`pubmed-epmc` (Tier-K bundled, çekirdeğin parçası) |
| Semantik KB takviyesi (Adım 0.4) | `evidentia-kb` `kb_search` — bağlı değilse map-only degrade (opsiyonel booster, çekirdek akışı bloklamaz) |

### P4 — Tam-metin zenginleştirme (çekirdek, her-zaman-açık)

| İhtiyaç | Merdiven |
|---|---|
| Tam-metin (legal-first) | EPMC `get_copyright_status` → EPMC `get_full_text_article` (PMC OA, Tier 1) → Paper Search `read_pubmed_paper` (Tier 2) → **Marmara EBSCO** `ebsco_search` + `ebsco_get` (**Tier 3 LİSANSLI BİRİNCİ**) → **OpenAthens/Millet** `oa_verify_access`/`oa_resolve` + `oa_fetch_fulltext`/`oa_fetch_pdf` (**Tier 4 LİSANSLI İKİNCİ**) → Wiley (Tier 5) → **Annas Reader** (**Tier 6 SON ÇARE**) → **pubmed-epmc** `pubmed_fetch_fulltext` (Tier 7 legal-OA) → anamnesis ingest/bounded query (`collection=evidentia:run:<id>`). EBSCO miss → SKIP-REASON, sessiz atlama yok |

### Opsiyonel modül merdivenleri (yalnız Adım 0.5 sinyaliyle)

| İhtiyaç | Merdiven |
|---|---|
| ICD/condition kodlama | `openfda` `icd11_search` (WHO ICD-11 MMS, ICD-11 birincil) → `nih-clinicaltables` (ICD-10/9) → bulunamazsa boşluk |
| İlaç normalizasyonu (INN↔RxCUI) | `nlm-rxnorm` → `med-terminologies` (RxNorm) → DailyMed REST |
| Terminoloji çapraz-yürüyüş (SNOMED/MeSH/LOINC/ATC) | ICD-11: `openfda` `icd11_search` → `med-terminologies` · MeSH/ATC: `med-terminologies` · SNOMED validate/expand: SNOMED CT Terminology companion (MAY) → `med-terminologies` (Snowstorm creds varsa) → TİTCK SNOMED ids (TR ilaç) |
| Mekanizma / hedef | ChEMBL `get_mechanism`/`target_search` → `iuphar-gtopdb` → OpenTargets (offline) → EPMC |
| TR ruhsat/fiyat/biyobenzer | **TİTCK** (`titck.cureonics.com`, kapılı — bundle'daki tek TİTCK, doğrudan) → bulunamazsa boşluk. SUT/mevzuat metni bu plugin'de yok → `cureolex` |
| Epidemiyoloji/yük | **ABD:** `PopHIVE` (`get_current_status`/`get_trend`/`get_map`/`get_coverage`/`compare` — precomputed, birebir aktar) + ICD-11 kodlama (`openfda`). **Global/ülke yük (Türkiye dahil):** `who-gho` (`who_gho_search_indicators`→`who_gho_query` `country="TUR"`/`"GLOBAL"`/region — WHO GHO OData, native) + EPMC `AFF:"Turkey"` + TİTCK + YÖK Tez. **Kanser insidans/mortalite (global/ülke):** `globocan` (`gco_resolve_population`→`gco_query` — IARC GLOBOCAN 2022, native; MODELLENMİŞ TAHMİN → `ui`+caveat). **IHME/GBD:** native-API YOK (hesap+ToS+satır-limiti) → hâlâ erişilemez boşluk (uydurma yok). PopHIVE'ı ABD-dışına genelleme; who-gho/globocan caveat'larını taşı. |
| Klinik DDI | **drugddx** (✅ canlı) → `nlm-rxnorm` etkileşim + DailyMed label DDI-bölümü (⚠️ "etkileşim verisi" olarak sunulMAZ) |
| Regülatuvar (FDA) | **openfda** `openfda_search` (drug/event FAERS · drug/label · drugsfda · enforcement) → DailyMed REST (label) → bulunamazsa boşluk |
| Regülatuvar (AB / EMA) | **ema** `ema_search_medicines`/`ema_get_medicine`/`ema_filter` (AB merkezi ruhsat durumu + CHMP opinion/decision + orphan/conditional/accelerated/PRIME bayrakları + ATC/INN/MAH/EPAR URL — baked EMA Medicines korpusu, native) → tam metin EPAR url → anamnesis ingest → bulunamazsa boşluk |
| Kılavuz/HTA PDF (ESMO/NCCN/NICE) | native-API YOK → **erişilemez boşluk** (VERİ YOK; uydurma yok). Operatör kılavuz PDF'ini yüklerse anamnesis'e ingest edilebilir |

---

## 3. Tek-Sefer Disiplini (kanonik önbellek)

TİTCK, MIDAS gibi pahalı/latency'li connector'lardan çekilen veri **tek sefer**
çekilir; sonraki adımlar `shared/canonical-cache-contract.md`'deki kanonik artefakttan okur.
Çift connector sorgusu engellenir. Özellikle: **TİTCK tek-sefer kuralı** (barcode çözümü bir
kez). (Eski RegulatoryMCP'nin 180 s latency'si self-host **openfda** ile ortadan kalktı — hızlı,
yine de tek-sefer cache disiplinine tabidir.)

**`evidence_index` (RAG/GraphRAG) — retrieve-don't-dump + münhasır çalışma seti:** Tam-metin
makale/kitap ve büyük araç çıktıları **asla ham olarak bağlam penceresine dökülmez**. Dual-write:
`collection=evidentia:run:<run_id>` **ve** `doc_id=evrun:<run_id>:<PMID|DOI>` (önek kalkmaz).
Flagship sorgu: `hybrid_query(collection=aynı, queries[])`. `semantic_search` collection ve/veya
önekli `doc_id` / `doc_ids[]` ile de ALLOW. Kapsamsız hybrid/graph/global search **PreToolUse
DENY** (NSCLC↔emicizumab sızıntı sınıfı). `corpus_stats` küresel gözlemdir, çalışma seti değildir
→ `list_docs(collection=…)`. Koşu bitince hook `forget_collection` tercih eder; yoksa ledger
`forget_document`. Küresel wipe yok; `forget_by_prefix` API değildir. Unscoped `semantic_search`
canlıda compat için durur — guard yine DENY eder. (Kanonik artefakt:
`shared/canonical-cache-contract.md` → `evidence_index`.) Aynı önekli `doc_id` iki kez ingest edilmez.

---

## 4. Pre-Flight Zorunluları

| Connector | Çağrı öncesi |
|---|---|
| openfda (FDA/ICD-11) | Latency-aware: tekil (paralel değil) çağrı; 1 retry; stall → skippable işaretle |
| Synapse / Wiley | `authenticate`; başarısız → graceful skip + not |
| OpenTargets | Offline olabilir → ChEMBL `target_search` fallback hazır |
| Self-host Worker'lar (openfda/drugddx/anamnesis/evidentia-kb) | **User-Agent zorunlu (D10):** boş/şüpheli UA → Cloudflare Error 1010 / 403. MCP istemcisi gerçek UA gönderir (sorun yok); doğrudan curl/script testinde `-H "User-Agent: Mozilla/5.0"` ekle. |
| Tier-K genişletme (×4) | İlk kullanımda liveness; topluluk-yayıncı → **least-privilege, sandbox-first** |
| drugddx (self-host) | Deploy + `/health` ok + Bearer `initialize` 200 (BUILD-BRIEF.md DoD) |

---

## 5. Güven & Güvenlik (mcp-scout Trust & Safety)

- **Doğrulanmamış connector uyarısı.** Özel konnektörler Anthropic'çe doğrulanmamış
  servislere bağlanır. **Tier-K genişletme (#1–#4) topluluk-yayıncıdır** (`io.github.*`);
  bunlara **least-privilege** kimlik verilir, önce **sandbox**'ta denenir.
- **Ekosistem istatistiği.** Kamuya açık MCP taramalarında kayda değer oranlarda SSRF (~%37),
  güvensiz komut yürütme (~%43), sıfır-auth (~%41) saptanmıştır → güven sinyalleri
  dekorasyon değil, karar girdisidir.
- **Klinik çapraz-doğrulama (bağlayıcı).** DDI, terminoloji, doz gibi **hasta-etkili**
  alanlarda topluluk-MCP çıktısı **bağımsız otoriter kaynakla** (TİTCK KÜB, DailyMed SPL,
  yayınlanmış kılavuz) çapraz-doğrulanmadan klinik karar olarak sunulMAZ.
- **DDI sunum disiplini.** TİTCK `find_drug_drug_interactions` substance-overlap'tir, klinik
  DDI **değildir** → "etkileşim verisi" olarak sunulMAZ; `find_shared_substance_peers`
  kullanılır. Aynı disiplin self-host `drugddx`'in label-bölümü çıktısına da uygulanır.
- **Honesty.** Bir connector'ın güvenliği/canlılığı doğrulanamıyorsa **söylenir**; "güvenli"
  damgalanmaz. `drug-interaction-mcp`'in HTTP 500'ü gizlenmemiş, self-host'a yönlendirilmiştir.

---

## 6. claude.ai ⇄ Claude Code Yüzey Ayrımı (KRİTİK)

| Yüzey | `.mcp.json` auto-wire? | Eylem |
|---|---|---|
| **Claude Code** (plugin runtime) | ✅ Tam — `mcpServers` doğrudan bağlanır | Plugin kurulumu connector'ları yükler |
| **claude.ai** (web) | ⚠️ Kısmî | Tier-K/Tier-O remote URL'leri **Settings → Connectors → Add custom connector**; Tier-A OAuth'u Advanced settings |
| **ChatGPT** (web · Developer Mode) | ❌ Yok — elle | **Settings → Connectors** (Plus/Pro/Business/Enterprise/Edu + **Developer Mode**). Self-host Worker URL'leri (`…/mcp`) elle eklenir; gated olanlarda OAuth, drugddx + keyless'larda "No authentication". Detay: `docs/KURULUM.md` Kurulum yolu **C**. |

**ChatGPT uyumu (4 self-host Worker, 2026-06-30 canlı doğrulandı):** anamnesis · evidentia-kb ·
openfda · drugddx **ChatGPT custom-connector ile çalışır**. Redirect allowlist `https://chatgpt.com`
içerir; OAuth keşfi **RFC 9728**'e göre sağlamlaştırıldı (401 `WWW-Authenticate` →
`resource_metadata`; PRM **path-insertion** `…/oauth-protected-resource/mcp`). Tümü **additive** —
claude.ai/grok yüzeyleri bozulmaz. ChatGPT istemcisi `/mcp`'yi sunucu tarafından çağırır → CORS
gerekmez. Üçüncü-taraf keyless connector'ların (med-terminologies, pipeworx gateway'leri; ⚠️ caseyjhand ikilisi 2026-08-08'de self-host'a taşındı)
ChatGPT-uyumu **upstream operatöre** bağlıdır. **openathens (HP self-host, 2026-07-03)** aynı
OAuth 2.1 + Bearer desenini kullanan **5.** self-host connector'dur — ChatGPT bağımsız doğrulaması
2026-06-30 batch'inin parçası DEĞİLDİR (yukarıdaki tarihli iddia orijinal 4 CF Worker'a özgüdür).

**Yanılgı önleme:** "Plugin her yerde her şeyi otomatik bağlar" **yanlıştır**. claude.ai/ChatGPT
web tarafında OAuth/operatör connector'ları manuel eklenir (mcp-scout
`claude-ai-compatibility.md`). `start` skill'inin Adım 2 preflight'ı bunu raporlar.

**Tier-O Worker taşınabilirliği:** `*.cureonics.workers.dev` / `yok-akademik.cureonics.com`
URL'leri **operatöre özeldir**. Başka bir operatör kurarsa kendi instance'larını ayağa
kaldırıp (TİTCK / YÖK Akademik fork'ları) `.mcp.json`'ı kendi
domain'leriyle güncellemelidir.

**Annas Reader + anamnesis (RAG/GraphRAG) yüzey notu:** **Annas Reader** operatörün bağlı
Cloud Run connector'ıdır (`*.a.run.app`, OAuth-gated, 401 SECURED) — claude.ai web tarafında
zaten bağlıdır; Claude Code tarafında OAuth handshake ile çalışır. **anamnesis** ise artık
**deploy EDİLDİ** (`self-host/anamnesis-mcp/BUILD-BRIEF.md`; Vectorize 1024-d cosine + D1 provizyonu
yapıldı, secret'lar set, 2026-06-25 RAG+GraphRAG E2E doğrulandı) ve Tier-O canlı girdisi olarak
roster'dadır. Her ikisi de **operatöre
özeldir**; başka operatör kendi Annas instance'ını bağlamalı ve anamnesis'i kendi Cloudflare
hesabına deploy etmelidir. Tam-metin + RAG akışı yalnız bu iki connector birlikte hazır
olduğunda uçtan uca çalışır (retrieve-don't-dump → `evidence_index`, §3).

---

## 7. Kapsam Notu

`medical-research` evrenseldir (hastane/IV dahil tüm alanlar) ve **çekirdeği bibliyografik
PRISMA hattıdır** (§1.1 — PubMed/EPMC, Europe PMC, OpenAlex, Semantic Scholar, Consensus,
ClinicalTrials, bioRxiv/medRxiv, Paper Search, YÖK Tez + tam-metin/RAG substratı). **TİTCK/
TÜRKPATENT, openFDA/ICD-11, AdisInsight/ChEMBL/GtoPdb, PopHIVE, med-terminologies/
RxNorm/nih-clinicaltables, drugddx, NPI/YÖK-Akademik gibi opsiyonel Türkiye/regülatuar/ilaç
modülleri, çekirdek taramaya bağlam veren KANIT-ZENGİNLEŞTİRMESİDİR — kendi başına ticari
istihbarat, regülasyon-işleri veya pazar-erişim danışmanlığı DEĞİLDİR.** Bu opsiyonel
modüllerden çıkan sinyal ticari/regülatuar bir soruya dönüşürse **doğru skill'e devredilir,
medical-research'te derinleştirilmez:**
- Ticari strateji / rekabet / pipeline istihbaratı (OSINT dahil) → `pharmaintel`
- Promosyonel materyal / MLR incelemesi → `promo-censor`
- Bireysel SGK/geri-ödeme itirazı, dava dosyası → `onko-erisim`
- Patent-özel araştırma (TÜRKPATENT'in salt patent-hukuku boyutu) → `pharmapatent`
- Karşılaştırmalı hukuk / mevzuat yorumu (TR dışı) → `cureolex` / `health-policy`

Ayrıca: **DDI çıktısı** otoriter kaynak olmadan "etkileşim verisi" olarak sunulMAZ; **FAERS**
sayıları raporlamadır, insidans değildir; **β-aday** connector'lar probe-verified olmadan
bağlanmaz; **web tier yok** (Exa/Tavily/OSINT v1.4.0'da kaldırıldı) → yapısal kaynakta yoksa
"VERİ YOK", uydurma yok. `medical-research` yalnız yapısal kanıt katmanını sağlar; opsiyonel
modüllerin yokluğu çekirdek bibliyografik hattı asla bozmaz.

---

## 8. Bilinen upstream araç kusurları (2026-06-27 canlı denetim)

Bu araçlar **upstream/üçüncü-taraf** kaynaklı kusurludur — plugin tarafından doğrudan
düzeltilemez. Hepsi `pipeworx_feedback`/operatöre raporlandı; skill bunlardan **kaçınıp
çalışan alternatife yönlenir** (no-fabrication: kusur gizlenmez).

| # | Araç (pack) | Kusur | Yönlendirme (kullan) |
|---|---|---|---|
| D1 | `nlm-rxnorm.rxnorm_interactions` (rxnorm) | **HTTP 404** — RxNav Drug Interaction API NLM tarafından Oca-2024'te kaldırıldı | Klinik-DDI: **`drugddx`** (`interaction_label`/`normalize_drug`) + DailyMed label DDI-bölümü. `rxnorm_interactions` ASLA çağrılmaz (deprecated/removed-upstream). |
| D2 | `nlm-rxnorm.rxnorm_related` (rxnorm) | **HTTP 400** (tty'li ve tty'siz, dokümante örnekle bile); gateway tty'yi virgülle iletiyor olabilir | Brand↔generic eşleme: **`med-terminologies.atc_classify`** veya **TİTCK `find_equivalent_products_by_substance`**. |
| D3 | `nih-clinicaltables.icd10cm` (clinicaltables) | İsim→kod araması **0 döner** (`diabetes`→0); yalnız kod→açıklama çalışır | Tanı→kod: **`med-terminologies.map_icd10_to_icd11`** veya **`openfda.icd11_search`**. `icd10cm` YALNIZ kod→açıklama doğrulaması için. |
| D4 | `nlm-rxnorm.rxnorm_search` (rxnorm) | Yalnız **SBD/SCD** döner (IN/BN/PIN yok) → ingredient RxCUI doğrudan alınamaz | Ingredient RxCUI: **`med-terminologies.atc_classify`** veya `resolve_entity(drug)`. |
| D5 | `*.validate_claim` (pipeworx) | **Dönem-hizalama zayıf** — doğru "FY2024" iddiası en güncel FY2025 ile kıyaslanıp "%6 sapma" denir | Kullanımda **asserted fiscal-year** açıkça verilir; sonucu dönem-uyumu için elle teyit et. |
| D6 | `med-terminologies.icd11_search` (med-terminologies) | **EMEKLI 2026-08-17** — canlı çağrı ICD-11 **3B10.0** döndü; guard artık DENY etmez. `openfda.icd11_search` operatör-sahipli yedek yol olarak durur. | Her iki `icd11_search` de meşru; operator-owned path = `openfda`. |

> D1–D5 upstream **pipeworx** (io.github.pipeworx-io) kaynaklıdır; D6 (sidneybissoli AUTH) 2026-08-17
> canlı doğrulamayla kapatıldı. evidentia salt-okunur tüketicidir. Bu satırlar `connector-registry.md`
> §3.3/§5 yönlendirmeleriyle tutarlıdır.
> **Canlı yeniden-doğrulama 2026-06-28** (`connector-registry.md §8` Probe Log): D1 (404), D2 (400),
> D3 (icd10cm isim→0) **birebir teyit edildi**; D6 2026-08-17'de geçersiz kılındı. Çalışan whitelist
> (atc_classify, map_icd10_to_icd11, drugs, icd10cm-kod, rxnorm_search/get_properties,
> search_targets/ligands, icd11_search) doğrulandı.

---

## 9. Adjudication Log — v8.5 (çakışan/yeni yüzeyler · canlı probe 2026-06-28)

Yeni aday connector'lar **probe-verified-only** (DEĞİŞMEZ 2) ilkesiyle yargılandı. Tam kanıt:
`connector-registry.md §8` Probe Log.

| Aday | Probe (2026-06-28) | Karar | Gerekçe |
|---|---|---|---|
| **PopHIVE** (`https://mcp.pophive.org/mcp`) | 200 · `get_current_status(rsv,CT)` canlı | **WIRE** (Tier-K-epi, §1.3) | ABD epidemiyoloji boşluğunu kapatır (native). **YALNIZCA ABD** → global/TR yük için who-gho (aşağıda); precomputed kanıt birebir aktarılır. |
| **who-gho** (`https://who-gho-mcp.cureonics.workers.dev/mcp`) | 2026-07-05 CANLI (Version 30df2ff2): keyless initialize 200 · tools/list 3 araç · `who_gho_query(WHOSIS_000001,TUR,2019)`→77.6/75.1/80.1 (BTSX/MLE/FMLE) E2E | **WIRE** (Tier-K-epi, self-host §1.6; ✅ DEPLOYED) | **Global/ülke hastalık yükü boşluğunu native kapatır** (PopHIVE ABD-only'nin tamamlayıcısı). Keyless (drugddx precedent — authless GHO OData, server-side sır yok). Değer WHO-otoriter ama modellenmiş+raporlanan → zorunlu caveat; ülke/yıl yoksa boşluk. Whitelist: `who_gho_search_indicators`, `who_gho_query`, `who_gho_dimensions`. |
| **globocan** (`https://globocan-mcp.cureonics.workers.dev/mcp`) | 2026-07-05 CANLI (Version 8825e031): endpoint Playwright ile yakalandı, path `{type}/{sex}` bilinen-değerle DOĞRULANDI (ilk swap düzeltildi); E2E Türkiye(792) female breast mortalite 7360/insidans 25249 (yayınlanan birebir), male lung insidans 33039/mortalite 32119, all-cancers female 34 satır Meme rank 1 (sessiz-kesme yok), prevalence prev_time 1/3/5, 41 kanser sitesi | **WIRE** (Tier-K-epi, self-host §1.6; ✅ DEPLOYED) | **Küresel/ülke KANSER yükü boşluğunu native kapatır** (who-gho'yu kanser-özelinde tamamlar; IHME/GBD hâlâ boşluk). Keyless (authless+headerless gco-api). Değer IARC-otoriter ama MODELLENMİŞ TAHMİN (ref 2022) → `ui`+zorunlu caveat; kombinasyon yoksa boşluk. Whitelist: `gco_list_cancers`, `gco_resolve_population`, `gco_query`. |
| **ema** (`https://ema-mcp.cureonics.workers.dev/mcp`) | 2026-07-05 CANLI (Version ff226c89): baked corpus 2712 ilaç (generated_at 05/07/2026); E2E Keytruda→Authorised/L01FF02/opinion 2015-05-20, ema_filter(L01,authorised,orphan)→5 onkoloji, ema_stats 2712 | **WIRE** (Tier-O regülatuar, self-host §1.6; ✅ DEPLOYED) | **AB ruhsat + CHMP/EPAR boşluğunu native kapatır** (RegulatoryMCP kaldırıldığında kalan EMA; openFDA'nın AB muadili). Keyless (baked public EMA XLSX, runtime upstream/sır yok). Değer EMA-otoriter, nokta-zaman → generated_at+caveat; snapshot'ta yoksa yokluk-kanıtı değil. Whitelist: `ema_search_medicines`, `ema_get_medicine`, `ema_filter`, `ema_stats`. |
| **drugddx** (`drugddx-mcp…`) | 200 · `normalize_drug`/`interaction_label` canlı | **WIRE** (Tier-O, D-β) | Klinik-DDI boşluk-kapatıcı (pairwise motor DEĞİL); self_host bloğundan runtime'a terfi. |
| **Mevzuat Bilgisi** (eski `mevzuat.surucu.dev` / Hub `mevzuat-mcp`) | — | **UNWIRE** (2026-08-17) | Evidentia ile mevzuat ilişkisi yok. TR mevzuat metni / SUT / kanun lookup → `cureolex`. Filodan, ajan `tools:` listesinden ve D7 `page_size` guard'ından çıkarıldı. |
| **Elicit** (`elicit.com/api/mcp`) | **OAuth bağlandı → 2026-06-28 CANLI** (`search_papers`→JULIET NEJM PMID 30501490; `list_reports` canlı) | **WIRE secondary** (conditional/OAuth) | Sistematik-derleme/ekstraksiyon katmanı, **Consensus'a secondary**. Doğrulanmış araçlar: `search_papers`/`search_trials` (corpus arama — typeTags RCT/Meta/SR + quartile/yıl filtreleri), `list_reports`/`get_report`, `create_report` (SR-rapor üreteci — kota-yükü, ölçülü kullan). **Statik `elk_live_` anahtarı Elicit REST-API anahtarıdır, MCP-JWS DEĞİL** (MCP OAuth ile bağlanır). Wiley/Synapse gibi: claude.ai Settings ile bağlanır, statik `.mcp.json` URL'si YOK; zorunlu Adım 1 listesinde DEĞİL; çıkarılan iddialar çapraz-doğrulanır (DEĞİŞMEZ 4). Anahtar → Doppler `ELICIT_API_KEY` (rotate önerilir). |
| **Yargı** (TR mahkeme) | (bağlı) | **WIRE ETME** | Hukuk içtihadı evidentia kapsamı dışı → **`cureolex` / `ius-salutis`**'e devredilir (start Scope Guard + §7). |
| **pipeworx generic** (`ask_pipeworx`/`discover_tools`/`remember`/`recall`/`polymarket_*`/`scan_*`/`subscribe`/`validate_claim` + gateway'in ~binlerce dinamik aracı) | — | **WHITELIST-DIŞI** | En-az-yetki (DEĞİŞMEZ 5): yalnız tıbbi pack araçları çağrılır. `.mcp.json` `includeTools` allowlist'i (nih-clinicaltables / nlm-rxnorm / iuphar-gtopdb) + PreToolUse guard §2.6 allowlist. **G-WHITELIST** statik denetler. |

> **Tool-düzeyi en-az-yetki (DEĞİŞMEZ 5):** `.mcp.json` sunucu düzeyinde bağlar; araç-düzeyi whitelist
> `connector-registry.md §2.6`'da normatiftir ve skill yalnız o araçları çağırır. **G-WHITELIST** §2.6
> whitelist'inde hiçbir pipeworx-jenerik araç adı bulunmadığını doğrular.
