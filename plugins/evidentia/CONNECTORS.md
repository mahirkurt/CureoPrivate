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

### 1.1 Akademik Çekirdek
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| PubMed / Europe PMC | 🟢 | API | search_articles · get_full_text_article · get_copyright_status · convert_article_ids (+3) | Anthropic HCLS | A |
| Clinical Trials v2 | 🟢 | none | search_trials · get_trial_details · search_by_sponsor · analyze_endpoints (+2) | Anthropic HCLS | K* |
| Consensus | 🟢 | API | search (kullanım mesajı birebir reprodüksiyon; ≤3/batch) | resmi | A |
| Scholar Gateway | 🟢 | API | semanticSearch | operatör/resmi | A |
| Paper Search | 🟢 | API | search · read_pubmed_paper · download_* (tam-metin tier 2) | topluluk | A |
| bioRxiv / medRxiv | 🟢 | none | search_preprints (preprint flag zorunlu) | Anthropic HCLS | K |
| YÖK Tez | 🟢 | none | search_yok_tez_detailed · get_yok_tez_document_markdown (+2) | operatör | A |
| Exa | 🟢 | API | web_search_exa · web_fetch_exa (gap-filler, en son) | resmi | A |
| Tavily | 🟢 | API | tavily_search/research/extract — **kota 432 → Exa-fallback** | resmi | A |

> **Bundled Tier-A statik URL'leri (`.mcp.json`):** Tavily `https://mcp.tavily.com/mcp`
> (Bearer `${TAVILY_API_KEY}`). **(RegulatoryMCP/Lex-Sanitas Tier-A girdisi KALDIRILDI** —
> karşılaştırmalı-hukuk araçları medikal kanıtta gürültüydü; yerine self-host **`openfda`** Tier-O
> + ICD-11 için aynı `openfda` Worker'ın `icd11_search`'ü (WHO ICD-11 MMS API, server-side OAuth); bkz §1.6.) Diğer Tier-A connector'lar (PubMed/EPMC, Consensus, AdisInsight,
> TİTCK, Mevzuat, Türk Patent, …) operatör workspace / claude.ai dizin connector'larıdır →
> roster'da statik URL ile **bildirilmez**; CONNECTORS.md envanteri + Settings ile bağlanır (§6).

### 1.2 Curated Intelligence + Mekanizma
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| AdisInsight | 🟢 | API | search_drugs · get_drug(HyDE) · generate_chart (+3) — **gerçek şema** (drug-intelligence-layer.md); eksen 0.5.I | resmi (Springer) | A |
| ChEMBL | 🟢 | none | drug_search · get_mechanism · get_admet · target_search | bio-research | A |
| Synapse | 🟡 | OAuth | authenticate → multi-omics (0.5.J) | bio-research | A (conditional) |
| OpenTargets | 🔴 | — | (offline son probe'da) → ChEMBL target_search fallback | bio-research | A (offline) |
| Wiley | 🟡 | OAuth | authenticate → publisher tam-metin (tier 4) | bio-research | A (conditional) |

### 1.3 Regülatuar + Epidemiyoloji + Türkiye + IP
| Connector | claude.ai | Auth | Anahtar araçlar | Güven | Katman |
|---|---|---|---|---|---|
| **openfda** (self-host) | — | OAuth/Bearer | `openfda_search` (drug/event·label·drugsfda·enforcement·device/*, api.fda.gov keyless) + `icd11_search` (WHO ICD-11 MMS, server-side OAuth) — hızlı. **(RegulatoryMCP/Lex-Sanitas yerine; ICD-11 buradan; WHO GHO/Health Canada/EUR-Lex çıkarıldı)** | operatör self-host | O |
| TİTCK | 🟢 | none | search_drugs · get_drug · find_biosimilar_group · get_price_history · find_off_label_uses_for_drug (+11) | operatör | A |
| Mevzuat | 🟢 | none | search_mevzuat · get_mevzuat_text · get_anayasa (+3) | operatör | A |
| Türk Patent | 🟢 | API | search_patents · search_trademarks · get_patent_details (+1) | operatör | A |
| NPI Registry | 🟢 | none | npi_search · npi_lookup · npi_validate (ABD PI/KOL) | Anthropic HCLS | K* |
| annas-mcp | 🟡 | — | article_search · article_download · book_search (tam-metin tier 3; **copyright kapısı**) | topluluk | A |

### 1.4 α-katman (operatör-bağlı, yüksek-güven · Tier-O)
| Connector | URL | Rol |
|---|---|---|
| TİTCK Cache | `https://titck-cache-mcp.cureonics.workers.dev` | Türkiye Dörtlüsü latency fallback rung |
| YÖK Akademik | `https://yok-akademik.cureonics.com/mcp` | Türk KOL kimliklendirme (§8 TR katmanı; YÖK Tez'den FARKLI) |
| **Annas Reader** | `https://annas-mcp-to7lqjgdkq-ew.a.run.app/mcp` | **Tam-metin geri-çağırma** (operatör-bağlı Cloud Run, OAuth-gated; 2026-06-25 401 SECURED). §1.3 generic `annas-mcp` satırını gerçekler/yerine geçer. Araçlar: `article_search`/`article_download` (DOI), `book_search`/`book_download` (MD5+format). ⚠️ İndirmeler **kullanıcının makinesine** iner (sandbox'a değil) → analiz için **anamnesis ingest** veya yapıştırma gerekir. **Telif:** yalnız analiz, toplu birebir çoğaltma YOK. |

### 1.5 Genişletme Katmanı (mcp-scout canlı-doğrulanmış · Tier-K · §6)
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
| Connector | URL | Durum |
|---|---|---|
| **drugddx** | `https://drugddx-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25) | β-aday `drug-interaction-mcp` HTTP 500 (CF 1101) → **self-host fork** (`self-host/drugddx-mcp/BUILD-BRIEF.md`). **Deployed + Tier-O roster'da** (401 SECURED · authenticated initialize 200 · serverInfo drugddx-mcp v1.0.0). |
| **openfda** | `https://openfda-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25) | **openFDA tipli erişim** (`self-host/openfda-mcp/`) — `openfda_search`: drug/event (FAERS), drug/label, drugsfda, enforcement, device/*; upstream api.fda.gov (keyless), endpoint allowlist (SSRF-safe). **Deployed + Tier-O** (401 SECURED · authenticated initialize 200 · canlı FAERS count + drug/label doğrulandı). **RegulatoryMCP/Lex-Sanitas'ın YERİNE**: karşılaştırmalı-hukuk araçları medikal kanıtta gürültü olduğu için roster'dan çıkarıldı; **ICD-11 = bu Worker'ın `icd11_search`'ü** (WHO ICD-11 MMS API, server-side OAuth = ICD11_CLIENT_ID/SECRET; canlı 3B10.0 doğrulandı — `med-terminologies` icd11'i WHO creds yokluğundan çalışmıyor). ⚠️ FAERS sayımları spontan rapor, insidans değil. |
| **evidentia-kb** | `https://evidentia-kb-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-26) | **KB semantik recall takviyesi** (`self-host/evidentia-kb-mcp/`) — `kb_search(query,k)` SKILL.md+references/*.md'yi (knowledge-map.md HARİÇ) bge-m3 Vectorize ile arar (244 chunk/24 dosya). medical-research **Adım 0.4 + Completeness Gate** için OPSİYONEL; bağlı değilse map-only degrade. **Deployed + Tier-O** (401 SECURED · kb_search canlı, layer-file recall doğrulandı). `kb_upsert` = setup-only (`scripts/kb_ingest.py`). |
| **anamnesis** | `https://anamnesis-mcp.cureonics.workers.dev/mcp` (✅ CANLI 2026-06-25 · RAG+GraphRAG E2E doğrulandı, corpus temiz) | **RAG/GraphRAG retrieval substratı** — registry'de hosted GraphRAG MCP yok (`rag-knowledge-graph-mcp` yalnız yerel stdio) → **self-host** (`self-host/anamnesis-mcp/BUILD-BRIEF.md`). Semantik chunking (bge-m3 1024-d) + Vectorize + D1 bilgi grafiği. Araçlar: `ingest_document` (→ manifest, ham metin değil) · `semantic_search` · `upsert_triples` · `graph_neighbors` · `subgraph` · **`hybrid_query`** · `corpus_stats`. **Bağlam-penceresi taşma koruması** (§3 → `evidence_index`). Deploy: Vectorize 1024-d cosine + D1 provizyon. |

### 1.7 REST Fallback (Tier-R · bundle DIŞI)
Native MCP olmayan, `medical-research`'ün Python `requests` ile çağırdığı uçlar
(`references/extended-api.md`): **OpenAlex · PubChem · Semantic Scholar Graph · DailyMed ·
Unpaywall · DOAJ · J-STAGE · DrugBank**. `.mcp.json`'da **bildirilmez**.

---

## 2. Native-First Fallback Zincirleri (çözümleme merdivenleri)

Her veri ihtiyacı şu sırayla çözülür: **native MCP → REST → web (Exa/Tavily) → belgelenmiş
boşluk** ("VERİ BULUNAMADI" + denenen sorgular).

| İhtiyaç | Merdiven |
|---|---|
| ICD/condition kodlama | `openfda` `icd11_search` (WHO ICD-11 MMS, ICD-11 birincil) → `nih-clinicaltables` (ICD-10/9) → Exa |
| İlaç normalizasyonu (INN↔RxCUI) | `nlm-rxnorm` → `med-terminologies` (RxNorm) → DailyMed REST |
| Terminoloji çapraz-yürüyüş (SNOMED/MeSH/LOINC/ATC) | `med-terminologies` (SNOMED/MeSH/LOINC/RxNorm/ATC) + ICD-11 için `openfda` `icd11_search` → `nih-clinicaltables` |
| Mekanizma / hedef | ChEMBL `get_mechanism`/`target_search` → `iuphar-gtopdb` → OpenTargets (offline) → EPMC |
| TR ruhsat/fiyat/biyobenzer | TİTCK native → **TİTCK Cache** (stall'da) → Mevzuat → Exa (son çare) |
| Epidemiyoloji/yük | `nih-clinicaltables` (condition) → GLOBOCAN/IHME (Exa) → PubMed/EPMC. (WHO GHO `who_gho_query` bundle'dan çıkarıldı; gerekirse operatörün standalone Lex-Sanitas connector'ından.) |
| Klinik DDI | **drugddx** (✅ canlı) → `nlm-rxnorm` etkileşim + DailyMed label DDI-bölümü (⚠️ "etkileşim verisi" olarak sunulMAZ) |
| Regülatuvar (FDA) | **openfda** `openfda_search` (drug/event FAERS · drug/label · drugsfda · enforcement) → DailyMed REST (label) → Exa (accessdata.fda.gov) |
| Tam-metin | EPMC `get_full_text_article` → `get_copyright_status` → Paper Search `read_pubmed_paper` → **Annas Reader** (`article_download`/`book_download`) → Wiley → Exa **→ anamnesis `ingest_document` → `semantic_search`/`hybrid_query`** (uzun metin bağlama DÖKÜLMEZ; indekslenir, sınırlı paket çekilir) |
| Kılavuz/HTA PDF | Exa (esmo/nccn/nice…) → Tavily (kota varsa, domain-scoped) |

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
| Regulatory MCP | Latency-aware: tekil (paralel değil) çağrı; 1 retry; stall → skippable işaretle |
| Tavily | Kota kontrolü; 432 → Exa-fallback (sessizce değil, çıktıda not) |
| Synapse / Wiley | `authenticate`; başarısız → graceful skip + not |
| OpenTargets | Offline olabilir → ChEMBL `target_search` fallback hazır |
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

**Yanılgı önleme:** "Plugin her yerde her şeyi otomatik bağlar" **yanlıştır**. claude.ai
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

`medical-research` evrenseldir (hastane/IV dahil tüm alanlar). Ancak: **DDI çıktısı**
otoriter kaynak olmadan "etkileşim verisi" olarak sunulMAZ; **FAERS** sayıları raporlamadır,
insidans değildir; **OSINT** (Tier 6) bağlamdır, klinik kanıt değildir; **β-aday**
connector'lar probe-verified olmadan bağlanmaz. Bireysel SGK/dava → `onko-erisim`; MLR →
`promo-censor`; ticari strateji → `pharmaintel` (medical-research kanıt katmanını sağlar).
