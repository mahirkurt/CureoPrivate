# CONNECTORS.md — evidentia Connector Tek Doğruluk Kaynağı

> **Normatif.** Bu dosya, `evidentia` plugin'inin connector envanteri, native-first
> fallback zincirleri, güven sınıflandırması ve claude.ai uyumluluk yargıları için **tek
> doğruluk kaynağıdır**. `.mcp.json` bundled roster'ı bu dosyayla **çapraz-doğrulanır**
> (G-BUNDLE kapısı). Skill içi `skills/medical-research/references/connector-registry.md`
> standalone kullanım için korunur; süit bağlamında çakışmada **bu dosya üstündür**.
>
> Orkestrasyon disiplini (tek-sefer fetch, kanonik önbellek):
> [shared/canonical-cache-contract.md](./shared/canonical-cache-contract.md).

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

### 1.1 Bibliyografik Çekirdek (her-zaman-açık getirim seti)
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| PubMed / Europe PMC | 🟢 | API | search_articles · get_full_text_article · get_copyright_status · convert_article_ids (+3) | Anthropic HCLS | A |
| Clinical Trials v2 | 🟢 | none | search_trials · get_trial_details · search_by_sponsor · analyze_endpoints (+2) | Anthropic HCLS | K* |
| Consensus | 🟢 | API | search (kullanım mesajı birebir reprodüksiyon; ≤3/batch) | resmi | A |
| Scholar Gateway | 🟢 | API | semanticSearch | operatör/resmi | A |
| Paper Search | 🟢 | API | search · read_pubmed_paper · download_* (tam-metin tier 2) | topluluk | A |
| bioRxiv / medRxiv | 🟢 | none | search_preprints (preprint flag zorunlu) | Anthropic HCLS | K |
| YÖK Tez | 🟢 | none | search_yok_tez_detailed · get_yok_tez_document_markdown (+2) | operatör | A |

**Tam-metin rung'u (P4, çekirdeğin parçası — enrichment-kapılı DEĞİL):**
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| **openathens** (self-host) | 🟢 | OAuth/Bearer | `oa_resolve` · `oa_fetch_fulltext`(ingest) · `oa_list_databases` · `oa_batch_submit`/`oa_batch_result` — **tam-metin Tier 3: LİSANSLI kurumsal** (Millet Kütüphanesi/OpenAthens → ProQuest/EBSCO/ScienceDirect/Wiley/Nature/JSTOR/Cochrane…; **annas'ın ÖNÜNDE**, legal-öncelikli). **CANLI** `https://openathens.cureonics.com/mcp` (`openathens-mcp`, 2026-07-03); anti-bot'suz yayıncılar (Springer/Nature) tam metin verir, anti-bot'lu (Wiley/Elsevier/OUP/Sage/T&F) → `manual_required` deep-link; bağlı değilse cascade Tier 4/5'e düşer | operatör self-host | O |
| annas-mcp | 🟡 | — | article_search · article_download · book_search (**tam-metin Tier 5 — SON ÇARE**, lisanslı band'dan [OpenAthens+Wiley] sonra; **copyright kapısı**) | topluluk | A |
| Unpaywall (pubmed-epmc üzerinden) | 🟢 | none | pubmed_fetch_fulltext (EuropePMC + Unpaywall yasal-OA çözümü; Tier 6 son legal-OA süpürmesi) | topluluk (cyanheads) | K |

**RAG substratı (retrieve-don't-dump, çekirdeğin parçası — enrichment-kapılı DEĞİL):**
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| anamnesis (self-host) | — | OAuth/Bearer | ingest_document · semantic_search · hybrid_query · graph_neighbors · corpus_stats · forget_document | operatör self-host | O |
| evidentia-kb (self-host) | — | OAuth/Bearer | kb_search — Adım 0.4 semantik yönlendirme takviyesi (bağlı değilse map-only degrade) | operatör self-host | O |

> **WEB TIER KALDIRILDI (v1.4.0):** Exa ve Tavily — ve OSINT ekseni — **tamamen çıkarıldı**.
> evidentia artık **saf yapısal-otoriter kanıt motorudur**: hiçbir web-arama/scraping fallback'i yoktur.
> Bir veri yapısal connector'larda (PubMed/EPMC, OpenAlex, S2, CT.gov, openFDA, TİTCK, Mevzuat, NPI …)
> bulunamıyorsa sonuç dürüstçe **"VERİ YOK / bulunamadı"** olarak raporlanır — ASLA uydurulmaz.
> Native-API'si olmayan kaynaklar (EMA CHMP/EPAR, ESMO/NCCN/NICE kılavuz PDF'leri, GLOBOCAN/IHME
> epidemiyoloji) bu nedenle **erişilemez bir boşluk** olarak işaretlenir.
>
> **Bundled Tier-A statik URL'leri (`.mcp.json`):** YOK. **(RegulatoryMCP/Lex-Sanitas Tier-A girdisi
> KALDIRILDI** — karşılaştırmalı-hukuk araçları medikal kanıtta gürültüydü; yerine self-host **`openfda`**
> Tier-O + ICD-11 için aynı `openfda` Worker'ın `icd11_search`'ü; bkz §1.6.) Tier-A connector'lar
> (PubMed/EPMC, Consensus, AdisInsight, TİTCK, Mevzuat, Türk Patent, …) operatör workspace / claude.ai
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
| Wiley | 🟡 | OAuth | authenticate → publisher tam-metin (tier 4) | bio-research | A (conditional) |

### 1.3 Regülatuar + Epidemiyoloji + Türkiye + IP — OPSİYONEL (zenginleştirme-modülü-kapılı)
**Yalnız Adım 0.5 Regulatory (0.5.C), HTA (0.5.D), Epidemiyoloji (0.5.K) veya Türkiye pazarı
bağlamı işaretlendiğinde yüklenir.** Bu **kanıt-bağlamı zenginleştirmesidir**, kendi başına
ticari/regülasyon istihbaratı DEĞİLDİR — ticari strateji `pharmaintel`'e, MLR `promo-censor`'a,
bireysel SGK/geri-ödeme `onko-erisim`'e, patent-özel iş `pharmapatent`'e, karşılaştırmalı-hukuk
soruları `lex-sanitas`/`health-policy`'ye yönlendirilir. Yokluğu yalnız işaretlenen modülü bozar —
bibliyografik çekirdek (§1.1) etkilenmez.

| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| **openfda** (self-host) | — | OAuth/Bearer | `openfda_search` (drug/event·label·drugsfda·enforcement·device/*, api.fda.gov keyless) + `icd11_search` (WHO ICD-11 MMS, server-side OAuth) — hızlı. **(RegulatoryMCP/Lex-Sanitas yerine; ICD-11 buradan; WHO GHO/Health Canada/EUR-Lex çıkarıldı)** | operatör self-host | O |
| **PopHIVE** (US epi · v8.5) | 🟢 | none | `get_current_status` · `get_trend` · `get_map` · `get_coverage` · `compare` · `get_data` — Yale harmonize **ABD** sürveyans (ED/hastane/atıksu/lab + çocukluk aşı kapsamı). **YALNIZCA ABD** (global/Türkiye yük = belgelenmiş boşluk); precomputed kanıtı **birebir aktar, sayıyı yeniden-türetme**. Eksen 0.5.K → §1.P/§21 | Yale (kamusal, DOI 10.5281/zenodo.17345935) | K-epi |
| TİTCK | 🟢 | none | search_drugs · get_drug · find_biosimilar_group · get_price_history · find_off_label_uses_for_drug (+11) | operatör | A |
| Mevzuat | 🟢 | none | search_mevzuat · get_mevzuat_text · get_anayasa (+3) | operatör | A |
| Türk Patent | 🟢 | API | search_patents · search_trademarks · get_patent_details (+1) | operatör | A |
| NPI Registry | 🟢 | none | npi_search · npi_lookup · npi_validate (ABD PI/KOL) | Anthropic HCLS | K* |

### 1.4 α-katman (operatör-bağlı, yüksek-güven · Tier-O) — OPSİYONEL (modülüne bağlı yükleme)
**Yalnız desteklediği opsiyonel modülle birlikte yüklenir** — TİTCK Cache Türkiye-pazarı
merdiveninin (§1.3) fallback basamağıdır, YÖK Akademik opsiyonel Türk-KOL modülüdür; **Annas
Reader ise çekirdek tam-metin rung'unun (§1.1) parçasıdır**, opsiyonel değildir. Yokluğu yalnız
bağlı olduğu modülü/rung'u bozar.

| Connector | URL | Rol |
|---|---|---|
| TİTCK Cache | `https://titck.cureonics.com/mcp` | Türkiye Dörtlüsü latency fallback rung |
| YÖK Akademik | `https://yok-akademik.cureonics.com/mcp` | Türk KOL kimliklendirme (§8 TR katmanı; YÖK Tez'den FARKLI) |
| **Annas Reader** | `https://annas.cureonics.com/mcp` | **Tam-metin geri-çağırma** (operatör-bağlı Cloud Run, OAuth-gated; 2026-06-25 401 SECURED) — **§1.1 çekirdek tam-metin rung'unun parçası; full-text cascade Tier 5 (SON ÇARE)** — lisanslı band (OpenAthens Tier 3 + Wiley Tier 4) getiremeyince devreye girer (legal-öncelikli), generic `annas-mcp` satırını gerçekler/yerine geçer. Araçlar: `article_search`/`article_download` (DOI), `book_search`/`book_download` (MD5+format). ⚠️ İndirmeler **kullanıcının makinesine** iner (sandbox'a değil) → analiz için **anamnesis ingest** veya yapıştırma gerekir. **Telif:** yalnız analiz, toplu birebir çoğaltma YOK. |

### 1.5 Genişletme Katmanı (mcp-scout canlı-doğrulanmış · Tier-K · §6)
**Karışık katman — dikkat:** `openalex` / `pubmed-epmc` / `semantic-scholar` **bibliyografik
çekirdeğin** (§1.1) bundled tool yüzeyleridir, her-zaman-açıktır. `med-terminologies` /
`nih-clinicaltables` / `nlm-rxnorm` / `iuphar-gtopdb` ise **OPSİYONEL** Extended Tier-K'dır —
yalnız drug/terminology zenginleştirme sinyali (Adım 0.5) ateşlendiğinde çağrılır
(`connector-registry.md §2.6` tool-whitelist).

| Connector | URL | Probe (2026-06-25) | Rol | Güven |
|---|---|---|---|---|
| **med-terminologies** | `https://medical.sidneybissoli.com/mcp` | ✅ 200 · v1.5.7 · 37 araç | SNOMED/LOINC/RxNorm/MeSH/ATC çapraz-yürüyüş (⚠️ `icd11_search` sunucuda WHO creds yok → AUTH_CONFIG_ERROR; **ICD-11 için `openfda`**) | **topluluk-UNVERIFIED** |
| **nih-clinicaltables** | `https://gateway.pipeworx.io/clinicaltables/mcp` | ✅ 200 · keyless | NIH Clinical Tables (ICD/LOINC/NPI/condition) | topluluk · NIH upstream |
| **nlm-rxnorm** | `https://gateway.pipeworx.io/rxnorm/mcp` | ✅ 200 · keyless | RxNorm normalizasyonu (INN↔RxCUI) | topluluk · NLM upstream |
| **iuphar-gtopdb** | `https://gateway.pipeworx.io/guidetopharmacology/mcp` | ✅ 200 · keyless | GtoPdb hedef/ligand | topluluk · IUPHAR upstream |
| **openalex** | `https://openalex.caseyjhand.com/mcp` | ✅ 200 (2026-06-27) · v0.7.2 · 5 araç | OpenAlex katalog (works/authors/institutions/topics/funders) — **KOL/atıf-ağı/kurum disambiguasyon** (§8); REST-fallback→native terfi | topluluk (cyanheads) · OpenAlex upstream |
| **pubmed-epmc** | `https://pubmed.caseyjhand.com/mcp` | ✅ 200 (2026-06-27) · v2.9.7 · 10 araç | PubMed/PMC + **Europe PMC** + **Unpaywall YASAL OA tam-metin** (annas gri-alanına alternatif) | topluluk (cyanheads) · NCBI/EPMC/Unpaywall upstream |
| **semantic-scholar** | `https://gateway.pipeworx.io/semanticscholar/mcp` | ✅ 200 (2026-06-27) · pipeworx gateway · S2 pack | Semantic Scholar atıf-grafiği/etki-atıfı (ikincil; Consensus+Scholar Gateway'i tamamlar) | topluluk · S2 upstream (aynı gateway) |

### 1.6 Self-Host (klinik DDI boşluğu + RAG/GraphRAG substratı + openFDA)
**Karışık katman — dikkat:** `anamnesis` ve `evidentia-kb` **bibliyografik çekirdeğin RAG
substratıdır** (§1.1) — her-zaman-açık, retrieve-don't-dump + Adım 0.4 yönlendirme için. `drugddx`
ve `openfda` ise **OPSİYONEL** — yalnız klinik-DDI / regülatuar / ICD-11 zenginleştirme sinyali
ateşlendiğinde çağrılır (§1.3).

| Connector | URL | Durum |
|---|---|---|
| **drugddx** | `https://drugddx-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25) | β-aday `drug-interaction-mcp` HTTP 500 (CF 1101) → **self-host fork** (`self-host/drugddx-mcp/BUILD-BRIEF.md`). **Deployed + Tier-O roster'da** (2026-06-28 AÇIK/keyless — MCP_ALLOW_NO_AUTH=1, salt-okunur public-API proxy; no-auth initialize 200 · serverInfo drugddx-mcp v1.0.0). |
| **openfda** | `https://openfda-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25) | **openFDA tipli erişim** (`self-host/openfda-mcp/`) — `openfda_search`: drug/event (FAERS), drug/label, drugsfda, enforcement, device/*; upstream api.fda.gov (keyless), endpoint allowlist (SSRF-safe). **Deployed + Tier-O** (2026-06-28 Bearer-gated — RE-GATED: `icd11_search` WHO ICD-11 server-side OAuth cred confused-deputy/resource-abuse önlemi; authenticated initialize 200 · canlı FAERS count + drug/label doğrulandı). **RegulatoryMCP/Lex-Sanitas'ın YERİNE**: karşılaştırmalı-hukuk araçları medikal kanıtta gürültü olduğu için roster'dan çıkarıldı; **ICD-11 = bu Worker'ın `icd11_search`'ü** (WHO ICD-11 MMS API, server-side OAuth = ICD11_CLIENT_ID/SECRET; canlı 3B10.0 doğrulandı — `med-terminologies` icd11'i WHO creds yokluğundan çalışmıyor). ⚠️ FAERS sayımları spontan rapor, insidans değil. |
| **evidentia-kb** | `https://evidentia-kb-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-26) | **KB semantik recall takviyesi** (`self-host/evidentia-kb-mcp/`) — `kb_search(query,k)` SKILL.md+references/*.md'yi (knowledge-map.md HARİÇ) bge-m3 Vectorize ile arar (244 chunk/24 dosya). medical-research **Adım 0.4 + Completeness Gate** için OPSİYONEL; bağlı değilse map-only degrade. **Deployed + Tier-O** (401 SECURED · kb_search canlı, layer-file recall doğrulandı). `kb_upsert` = setup-only (`scripts/kb_ingest.py`). |
| **anamnesis** | `https://anamnesis-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25 · RAG+GraphRAG E2E doğrulandı, corpus temiz) | **RAG/GraphRAG retrieval substratı** — registry'de hosted GraphRAG MCP yok (`rag-knowledge-graph-mcp` yalnız yerel stdio) → **self-host** (`self-host/anamnesis-mcp/BUILD-BRIEF.md`). Semantik chunking (bge-m3 1024-d) + Vectorize + D1 bilgi grafiği + FTS5 lexical. **8 araç:** `ingest_document` (→ manifest, ham metin değil) · `semantic_search` · `upsert_triples` · `graph_neighbors` · `subgraph` · **`hybrid_query`** · `corpus_stats` · **`forget_document`** (doc_id ile temiz silme — Vectorize + D1 chunks/manifest/edges/FTS + node-provenance küçültme/orphan-silme; idempotent, destructive; v1.4.1). **ÇOK-SORGULU HİBRİT GETİRİM (v1.6.0, tam §4.1.1):** `semantic_search` + `hybrid_query` artık **`queries[]` ayrıştırma → her sorgu için vektör (bge-m3) ∥ BM25 (FTS5) → RRF füzyon (tüm sorgu×arm) → cross-encoder rerank (bge-reranker) → top-k** çalıştırır. Orkestratör soruyu alt-yönlere/eşanlamlılara böler→`queries[]`; Worker hepsini füzyonlar→PRIMARY'ye rerank → **recall-maks ("hiçbir detayı atlamama") + precision**. Saf-vektörün bulanıklaştırdığı tam-terminolojiyi (ilaç/gen/kod) yakalar; her aşama graceful-degrade. §8 retrieval telemetri CF-log'da. **Bağlam-penceresi taşma koruması** (§3 → `evidence_index`). Deploy: Vectorize 1024-d cosine + D1 + FTS5. |

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
| Bibliyografik arama (MeSH/Emtree + serbest metin) | PubMed/EPMC `search_articles` → `pubmed-epmc` (`pubmed_search_articles`/`pubmed_europepmc_search`) → Scholar Gateway `semanticSearch` → Consensus `search` → Paper Search / bioRxiv-medRxiv / YÖK Tez |
| KOL / atıf-ağı / kurum-yazar | `openalex` (`openalex_resolve_name`→`search_entities`/`get_citation_graph`) → `semantic-scholar` → EPMC → NPI (US, **opsiyonel**) → YÖK Akademik (TR, **opsiyonel**) |

### P2 — Getirim & dedup (çekirdek, her-zaman-açık)

| İhtiyaç | Merdiven |
|---|---|
| Çekirdek akademik getirim | PubMed/EPMC → Clinical Trials v2 `search_trials` → bioRxiv/medRxiv `search_preprints` → Paper Search → `openalex`/`semantic-scholar`/`pubmed-epmc` (Tier-K bundled, çekirdeğin parçası) |
| Semantik KB takviyesi (Adım 0.4) | `evidentia-kb` `kb_search` — bağlı değilse map-only degrade (opsiyonel booster, çekirdek akışı bloklamaz) |

### P4 — Tam-metin zenginleştirme (çekirdek, her-zaman-açık)

| İhtiyaç | Merdiven |
|---|---|
| Tam-metin (legal-first) | EPMC `get_copyright_status` → EPMC `get_full_text_article` (PMC OA, Tier 1) → Paper Search `read_pubmed_paper` (Tier 2) → **OpenAthens/Millet Kütüphanesi** `oa_resolve`/`oa_fetch_fulltext` (**Tier 3 — LİSANSLI kurumsal, legal-öncelikli**; `openathens` HP self-host **CANLI** → bağlı değilse atla; anti-bot'lu yayıncı → `manual_required`) → Wiley (opsiyonel OAuth, Tier 4) → **Annas Reader** `article_download`/`book_download` (**Tier 5 — SON ÇARE**, lisanslı band [OpenAthens+Wiley] getiremeyince) → **pubmed-epmc** `pubmed_fetch_fulltext` (Unpaywall YASAL-OA, Tier 6 son süpürme) **→ anamnesis `ingest_document` → `semantic_search`/`hybrid_query`** (uzun metin bağlama DÖKÜLMEZ; indekslenir, sınırlı paket çekilir) |

### Opsiyonel modül merdivenleri (yalnız Adım 0.5 sinyaliyle)

| İhtiyaç | Merdiven |
|---|---|
| ICD/condition kodlama | `openfda` `icd11_search` (WHO ICD-11 MMS, ICD-11 birincil) → `nih-clinicaltables` (ICD-10/9) → bulunamazsa boşluk |
| İlaç normalizasyonu (INN↔RxCUI) | `nlm-rxnorm` → `med-terminologies` (RxNorm) → DailyMed REST |
| Terminoloji çapraz-yürüyüş (SNOMED/MeSH/LOINC/ATC) | `med-terminologies` (SNOMED/MeSH/LOINC/RxNorm/ATC) + ICD-11 için `openfda` `icd11_search` → `nih-clinicaltables` |
| Mekanizma / hedef | ChEMBL `get_mechanism`/`target_search` → `iuphar-gtopdb` → OpenTargets (offline) → EPMC |
| TR ruhsat/fiyat/biyobenzer | TİTCK native → **TİTCK Cache** (stall'da) → Mevzuat → bulunamazsa boşluk |
| Epidemiyoloji/yük | **ABD:** `PopHIVE` (`get_current_status`/`get_trend`/`get_map`/`get_coverage`/`compare` — precomputed, birebir aktar) + ICD-11 kodlama (`openfda`). **Türkiye:** TİTCK + EPMC `AFF:"Turkey"` + YÖK Tez. **Global/TR yük (GLOBOCAN/IHME/WHO-GHO):** native-API YOK → erişilemez boşluk (uydurma yok). PopHIVE'ı ABD-dışına genelleme. |
| Klinik DDI | **drugddx** (✅ canlı) → `nlm-rxnorm` etkileşim + DailyMed label DDI-bölümü (⚠️ "etkileşim verisi" olarak sunulMAZ) |
| Regülatuvar (FDA) | **openfda** `openfda_search` (drug/event FAERS · drug/label · drugsfda · enforcement) → DailyMed REST (label) → bulunamazsa boşluk |
| Kılavuz/HTA PDF (ESMO/NCCN/NICE) + EMA (CHMP/EPAR) | native-API YOK → **erişilemez boşluk** (VERİ YOK; uydurma yok). Operatör kılavuz PDF'ini yüklerse anamnesis'e ingest edilebilir |

---

## 3. Tek-Sefer Disiplini (kanonik önbellek)

TİTCK, MIDAS gibi pahalı/latency'li connector'lardan çekilen veri **tek sefer**
çekilir; sonraki adımlar `shared/canonical-cache-contract.md`'deki kanonik artefakttan okur.
Çift connector sorgusu engellenir. Özellikle: **TİTCK tek-sefer kuralı** (barcode çözümü bir
kez). (Eski RegulatoryMCP'nin 180 s latency'si self-host **openfda** ile ortadan kalktı — hızlı,
yine de tek-sefer cache disiplinine tabidir.)

**`evidence_index` (RAG/GraphRAG) — retrieve-don't-dump kuralı:** Tam-metin makale/kitap ve
büyük araç çıktıları **asla ham olarak bağlam penceresine dökülmez**. Onun yerine anamnesis
`ingest_document` ile indekslenir (semantik chunk + bge-m3 embed + D1 grafiği) ve sorguya yalnız
`semantic_search`/`hybrid_query` ile **sınırlı, provenance-damgalı, graph-temelli** dilim çekilir.
Bu, araç çıktılarının context-window taşması nedeniyle eksik/tutarsız değerlendirilmesini önleyen
çekirdek disiplindir (kanonik artefakt: `shared/canonical-cache-contract.md` → `evidence_index`).
Bir `doc_id` (DOI vb.) bir kez ingest edilir; sonraki sorgular indeksten okur — çift ingest yok.

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
| **ChatGPT** (web · Developer Mode) | ❌ Yok — elle | **Settings → Connectors** (Plus/Pro/Business/Enterprise/Edu + **Developer Mode**). Self-host Worker URL'leri (`…/mcp`) elle eklenir; gated olanlarda OAuth, drugddx + keyless'larda "No authentication". Detay: `docs/EVIDENTIA-KURULUM-VE-KEYLER.md` Kurulum yolu **C**. |

**ChatGPT uyumu (4 self-host Worker, 2026-06-30 canlı doğrulandı):** anamnesis · evidentia-kb ·
openfda · drugddx **ChatGPT custom-connector ile çalışır**. Redirect allowlist `https://chatgpt.com`
içerir; OAuth keşfi **RFC 9728**'e göre sağlamlaştırıldı (401 `WWW-Authenticate` →
`resource_metadata`; PRM **path-insertion** `…/oauth-protected-resource/mcp`). Tümü **additive** —
claude.ai/grok yüzeyleri bozulmaz. ChatGPT istemcisi `/mcp`'yi sunucu tarafından çağırır → CORS
gerekmez. Üçüncü-taraf keyless connector'ların (med-terminologies, pipeworx gateway'leri, caseyjhand)
ChatGPT-uyumu **upstream operatöre** bağlıdır. **openathens (HP self-host, 2026-07-03)** aynı
OAuth 2.1 + Bearer desenini kullanan **5.** self-host connector'dur — ChatGPT bağımsız doğrulaması
2026-06-30 batch'inin parçası DEĞİLDİR (yukarıdaki tarihli iddia orijinal 4 CF Worker'a özgüdür).

**Yanılgı önleme:** "Plugin her yerde her şeyi otomatik bağlar" **yanlıştır**. claude.ai/ChatGPT
web tarafında OAuth/operatör connector'ları manuel eklenir (mcp-scout
`claude-ai-compatibility.md`). `start` skill'inin Adım 2 preflight'ı bunu raporlar.

**Tier-O Worker taşınabilirliği:** `*.cureonics.workers.dev` / `yok-akademik.cureonics.com`
URL'leri **operatöre özeldir**. Başka bir operatör kurarsa kendi instance'larını ayağa
kaldırıp (TİTCK Cache / YÖK Akademik fork'ları) `.mcp.json`'ı kendi
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
Mevzuat/TÜRKPATENT, openFDA/ICD-11, AdisInsight/ChEMBL/GtoPdb, PopHIVE, med-terminologies/
RxNorm/nih-clinicaltables, drugddx, NPI/YÖK-Akademik gibi opsiyonel Türkiye/regülatuar/ilaç
modülleri, çekirdek taramaya bağlam veren KANIT-ZENGİNLEŞTİRMESİDİR — kendi başına ticari
istihbarat, regülasyon-işleri veya pazar-erişim danışmanlığı DEĞİLDİR.** Bu opsiyonel
modüllerden çıkan sinyal ticari/regülatuar bir soruya dönüşürse **doğru skill'e devredilir,
medical-research'te derinleştirilmez:**
- Ticari strateji / rekabet / pipeline istihbaratı (OSINT dahil) → `pharmaintel`
- Promosyonel materyal / MLR incelemesi → `promo-censor`
- Bireysel SGK/geri-ödeme itirazı, dava dosyası → `onko-erisim`
- Patent-özel araştırma (TÜRKPATENT'in salt patent-hukuku boyutu) → `pharmapatent`
- Karşılaştırmalı hukuk / mevzuat yorumu (TR dışı) → `lex-sanitas` / `health-policy`

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
| D6 | `med-terminologies.icd11_search` (med-terminologies) | **AUTH_CONFIG_ERROR** — sunucuda WHO_CLIENT_ID/SECRET yok | ICD-11 metin araması: **DAİMA `openfda.icd11_search`** (WHO ICD-11 MMS, server-side OAuth; canlı doğrulandı haemophilia A→3B10.0). |

> D1–D5 upstream **pipeworx** (io.github.pipeworx-io) / D6 **medical.sidneybissoli.com** kaynaklıdır;
> evidentia salt-okunur tüketicidir. Bu satırlar `connector-registry.md` §3.3/§5 yönlendirmeleriyle tutarlıdır.
> **Canlı yeniden-doğrulama 2026-06-28** (`connector-registry.md §8` Probe Log): D1 (404), D2 (400),
> D3 (icd10cm isim→0), D6 (AUTH_CONFIG_ERROR) **birebir teyit edildi**; çalışan whitelist (atc_classify,
> map_icd10_to_icd11, drugs, icd10cm-kod, rxnorm_search/get_properties, search_targets/ligands) doğrulandı.

---

## 9. Adjudication Log — v8.5 (çakışan/yeni yüzeyler · canlı probe 2026-06-28)

Yeni aday connector'lar **probe-verified-only** (DEĞİŞMEZ 2) ilkesiyle yargılandı. Tam kanıt:
`connector-registry.md §8` Probe Log.

| Aday | Probe (2026-06-28) | Karar | Gerekçe |
|---|---|---|---|
| **PopHIVE** (`https://mcp.pophive.org/mcp`) | 200 · `get_current_status(rsv,CT)` canlı | **WIRE** (Tier-K-epi, §1.3) | ABD epidemiyoloji boşluğunu kapatır (native). **YALNIZCA ABD** → global/TR yük hâlâ belgelenmiş boşluk; precomputed kanıt birebir aktarılır. |
| **drugddx** (`drugddx-mcp…`) | 200 · `normalize_drug`/`interaction_label` canlı | **WIRE** (Tier-O, D-β) | Klinik-DDI boşluk-kapatıcı (pairwise motor DEĞİL); self_host bloğundan runtime'a terfi. |
| **Mevzuat Bilgisi** (`https://mevzuat.surucu.dev/mcp`) | 200 · `search_kanun("ilaç")`→67 | **WIRE secondary** (opsiyonel, degradable) | Primer Mevzuat'a **çapraz-kontrol aynası** — kanun-NUMARASI lookup + bedesten.adalet.gov.tr ikinci kaynak ekler (primer keyword-aramasında yok). **Primacy primer Mevzuat'ta**; tek-sefer cache'e tabi; yalnız primer-miss veya numara/gerekçe lookup'ında çağrılır. Tool whitelist: `search_kanun`, `search_mevzuat`. |
| **Elicit** (`elicit.com/api/mcp`) | **OAuth bağlandı → 2026-06-28 CANLI** (`search_papers`→JULIET NEJM PMID 30501490; `list_reports` canlı) | **WIRE secondary** (conditional/OAuth) | Sistematik-derleme/ekstraksiyon katmanı, **Consensus'a secondary**. Doğrulanmış araçlar: `search_papers`/`search_trials` (corpus arama — typeTags RCT/Meta/SR + quartile/yıl filtreleri), `list_reports`/`get_report`, `create_report` (SR-rapor üreteci — kota-yükü, ölçülü kullan). **Statik `elk_live_` anahtarı Elicit REST-API anahtarıdır, MCP-JWS DEĞİL** (MCP OAuth ile bağlanır). Wiley/Synapse gibi: claude.ai Settings ile bağlanır, statik `.mcp.json` URL'si YOK; zorunlu Adım 1 listesinde DEĞİL; çıkarılan iddialar çapraz-doğrulanır (DEĞİŞMEZ 4). Anahtar → Doppler `ELICIT_API_KEY` (rotate önerilir). |
| **Yargı** (TR mahkeme) | (bağlı) | **WIRE ETME** | Hukuk içtihadı evidentia kapsamı dışı → **`lex-sanitas` / `ius-salutis`**'e devredilir (start Scope Guard + §7). |
| **pipeworx generic** (`ask_pipeworx`/`discover_tools`/`remember`/`recall`/`polymarket_*`/`scan_*`/`subscribe`/`validate_claim`) | — | **WHITELIST-DIŞI** | En-az-yetki (DEĞİŞMEZ 5): yalnız tıbbi pack araçları çağrılır; jenerik orchestration/finans araçları asla. **G-WHITELIST** statik denetler. |

> **Tool-düzeyi en-az-yetki (DEĞİŞMEZ 5):** `.mcp.json` sunucu düzeyinde bağlar; araç-düzeyi whitelist
> `connector-registry.md §2.6`'da normatiftir ve skill yalnız o araçları çağırır. **G-WHITELIST** §2.6
> whitelist'inde hiçbir pipeworx-jenerik araç adı bulunmadığını doğrular.
