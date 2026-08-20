# evidentia

**Genel-amaçlı PRISMA tıbbi literatür inceleme aracı** — bir Claude Code / Cursor /
claude.ai marketplace plugin'i. Tüm tıp alanlarını ve her soru tipini (tedavi/tanı/prognoz/etiyoloji/
önleme) kapsayan uçtan uca **PRISMA 2020 / PRISMA-ScR sistematik/kapsam derlemesi** motoru.
`medical-research` v9.0.6 flagship skill'ini, her-zaman-açık bibliyografik çekirdek
connector'ları, opsiyonel bağlam-tetiklemeli zenginleştirme modüllerini ve `mcp-scout` ile
canlı-doğrulanmış klinik genişletme MCP'lerini tek kurulabilir pakette toplar.

---

## Ne sağlar

- **Flagship skill:** `medical-research` v9.0.6 — omurga **P0–P7 PRISMA hattı**, soru
  konusundan bağımsız her derlemede aynı sekiz fazı çalıştırır:
  - **P0 Protokol** — PICO/PECO/PCC çerçeveleme, derleme tipi (sistematik/kapsam), uygunluk
    kriterleri, protokol ön-kaydı.
  - **P1 Arama Stratejisi** — MeSH/Emtree + serbest-metin, Boolean yapı, veritabanı-başına
    çeviri, tarih/dil sınırları, gri-literatür planı.
  - **P2 Getirim & Dedup** — native-MCP-first merdivenle kapsamlı getirim, kayıt kimlikleri
    (PMID/DOI/NCT), yineleme temizliği, PRISMA akış sayaçları; tek-sefer/kanonik-önbellek
    sözleşmesine tabi.
  - **P3 Tarama** — başlık/özet → tam-metin iki-aşamalı tarama, dahil/hariç gerekçe kaydı,
    çakışma çözümü. **İnsan-onay kapısı.**
  - **P4 Veri Çıkarımı** — çalışma özellikleri + sayısal sonuçlar (etki tahmini, GA, p, alt-grup,
    yan-etki) yapılandırılmış çıkarım tablosuna; copyright-kapılı tam-metin zenginleştirmesi.
  - **P5 Yanlılık Riski** — tasarıma göre RoB2 (RKÇ) / ROBINS-I (randomize-olmayan) / QUADAS-2
    (tanısal doğruluk) / Newcastle-Ottawa (gözlemsel) / PROBAST (prediksiyon modeli).
    **İnsan-onay kapısı.**
  - **P6 GRADE Kesinlik** — sonuç-bazlı kanıt kesinliği derecelendirmesi (GRADE / Tier 0–6),
    gerekçeli düşür/yükselt.
  - **P7 PRISMA Raporlama** — PRISMA 2020 akış diyagramı + Summary-of-Findings tablosu +
    PRISMA/PRISMA-ScR kontrol listesi + dergi-düzeyi temiz-kopya Türkçe rapor.
  Korunan omurga doktrinleri: native-MCP-first çözümleme, temiz-kopya sunum, retrieve-don't-dump,
  no-fabrication, cömertlik (uncapped derinlik), tek-sefer/kanonik-önbellek.
- **`start` skill'i:** süit oryantasyonu + connector preflight + niyet yönlendirme.
- **7 komut:**
  - `/evidentia` — uçtan uca P0→P7 koşumu (herhangi bir tıbbi araştırma sorusu, her uzmanlık).
  - `/evidentia-protocol` — P0–P1 (PICO/PECO + veritabanı-başına MeSH/Emtree arama stratejisi).
  - `/evidentia-fulltext` — copyright-kapılı tam-metin kademesi (EPMC→Paper Search→
    OpenAthens→Wiley→Anna's Reader→Unpaywall); metin/RAG veya orijinal PDF/EPUB teslimini seçer.
  - `/evidentia-synthesize` — P4+P6 graph-temelli derin sentez (anamnesis RAG/GraphRAG üzerinden
    `evidence-synthesizer` alt-ajanını çağırır).
  - `/evidentia-appraise` — P5–P6 (RoB2/ROBINS-I/QUADAS-2/Newcastle-Ottawa/PROBAST yanlılık riski
    + GRADE kesinlik/Summary-of-Findings).
  - `/evidentia-kol` — KOL haritası (**opsiyonel zenginleştirme modülü**; yalnız KOL/uzman-ağı
    bağlamlı sorularda çağrılır).
  - `/evidentia-connectors` — preflight + roster tazeleme + canlı G-PROBE (initialize handshake).
- **1 alt-ajan:** `evidence-synthesizer` — ağır fan-out araştırmayı izole eder; RAG/GraphRAG ile
  retrieve-don't-dump.
- **Opsiyonel, bağlam-tetiklemeli zenginleştirme modülleri** (Adım 0.5) — hiçbiri varsayılan
  yolda zorunlu **değildir**, **hiçbiri silinmedi**: terapötik-alan katmanları (Onko/Heme/İmmün/
  Nöro/Nadir), Regülatuar/HTA/MedAffairs/Drug-Intelligence, Türkiye-pazarı (TİTCK/
  TÜRKPATENT), Epidemiyoloji (openfda ICD-11 + PopHIVE ABD). Sinyal yoksa çekirdek bibliyografik
  PRISMA hattı tek başına koşar — bu **de-skew** değişmezi `G-DESKEW`/`G-PHASES` kapılarıyla
  denetlenir.
- **Tam-metin dosya teslimi:** **OpenAthens** `oa_fetch_pdf(doi|url)` ile hesaba açık
  sağlayıcılardan orijinal PDF; **Anna's Reader** `download_document(id=DOI|MD5)` ile
  PDF/EPUB ve desteklenen diğer formatları sunar. Her ikisi de kısa-ömürlü opaque
  `resource_link` + SHA-256/provenance döndürür; link derhal tüketilir.
- **RAG/GraphRAG substratı:** **anamnesis** self-host Worker — semantik chunking (bge-m3 1024-d) +
  Vectorize + D1. Tam-metin **bağlama dökülmeden** dual-write (`collection=evidentia:run:<run_id>`
  + `evrun:<run_id>:`) çalışma setine yazılır; scoped `hybrid_query` / `semantic_search` ile
  sınırlı dilim çekilir. Kapsamsız hybrid/graph → guard DENY. Koşu bitince hook
  `forget_collection` (yedek: ledger `forget_document`).
- **Bundled connector roster** (`.mcp.json`) — **20 server** (11 Bearer-gated, 9 public) +
  13 companion (`.mcp.json`'a girmez; Wiley + Claude Directory OAuth dahil). Tek doğruluk kaynağı
  [`fleet.yaml`](./fleet.yaml) → [`CONNECTORS.md`](./CONNECTORS.md).
- **Self-host yüzeyi** — CF Worker (`self-host/`: anamnesis · drugddx · openfda ·
  evidentia-kb · who-gho · globocan · ema) + CureoHub HP akademik üçlü
  (`openalex.cureonics.com` · `pubmed.cureonics.com` · `semanticscholar.cureonics.com`) +
  marmara-ebsco HP (`ebsco.cureonics.com`, Tier 3) + openathens HP (`openathens.cureonics.com`, Tier 4).

---

## Kurulum

**Claude Code (marketplace):**
```bash
/plugin marketplace add <marketplace-repo>
/plugin install evidentia
```
Kurulum `.mcp.json` roster'ını yükler; Claude Code restart sonrası `start` skill'i ve komutlar
aktif olur.

**claude.ai (web):** Tier-K/Tier-O remote connector'ları **Settings → Connectors → Add custom
connector** ile, Tier-A OAuth connector'ları Advanced settings ile eklenir. Yüzey ayrımı için
[`CONNECTORS.md` §6](./CONNECTORS.md).

---

## Hızlı başlangıç

```
/evidentia-connectors      # önce bağlanırlığı doğrula
/evidentia <araştırma sorusu>   # uçtan uca P0→P7 PRISMA koşumu
```
Örnekler: *"perioperatif beta-bloker kullanımı kardiyak-dışı cerrahide mortalite — sistematik
derleme"* (saf PRISMA, hiçbir zenginleştirme modülü tetiklenmez) · *"emicizumab inhibitörsüz
Hemofili A — kanıt + TR ruhsat/fiyat manzarası"* (Türkiye-pazarı modülü tetiklenir) ·
*"CAR-T DLBCL 3L — kılavuz + HTA + pipeline"* (heme + HTA + drug-intelligence modülleri).

---

## Connector katmanları (özet)

Bibliyografik çekirdek (PubMed/EPMC, ClinicalTrials, OpenAlex, Semantic Scholar, Consensus,
bioRxiv/medRxiv, Paper Search, YÖK Tez + tam-metin/RAG) **her zaman açıktır** ve P1–P4'ü
konudan bağımsız çalıştırır; aşağıdaki tabloda işaretlenen geri kalan katmanlar (curated
intelligence, Türkiye-pazarı, regülatuar/epidemiyoloji, α-katman) yalnız Adım 0.5 zenginleştirme
sinyali tetiklendiğinde devreye girer.

| Katman | Ne | Auto-wire |
|---|---|---|
| **Tier-K** keyless remote-ready | Clinical Trials, NPI, bioRxiv + **genişletme:** med-terminologies, NIH Clinical Tables, NLM RxNorm, IUPHAR GtoPdb, **OpenAlex** (KOL/atıf-ağı), **PubMed-EPMC** (Europe PMC + Unpaywall yasal-OA), **Semantic Scholar** | ✅ |
| **Tier-O** operatör Worker'ları | TİTCK (kanonik, kapılı), YÖK Akademik, **Annas Reader** (tam-metin), **openfda** (FDA/WHO ICD-11), **evidentia-kb** (KB takviyesi, opsiyonel) | ✅ |
| **Tier-A** auth-gerekli | PubMed/EPMC, Consensus, AdisInsight, TİTCK, Türk Patent, … | env / Settings |
| **Tier-R** REST fallback | PubChem, DailyMed, DOAJ, J-STAGE, … | (native MCP değil — bundle dışı; OpenAlex/Unpaywall/S2 artık native Tier-K) |

Tam envanter, fallback merdivenleri ve probe kanıtı: [`CONNECTORS.md`](./CONNECTORS.md).

---

## Güvenlik notu

- **Tier-K genişletme connector'ları topluluk-yayıncıdır** (`io.github.*`) → least-privilege,
  sandbox-first; **hasta-etkili** çıktı (DDI, terminoloji, doz) otoriter kaynakla
  çapraz-doğrulanmadan klinik karar olarak sunulmaz.
- **No-fabrication:** her connector URL'i registry + canlı `initialize` probe'una izlenebilir
  (probe tarihi 2026-06-25). `drug-interaction-mcp`'in HTTP 500'ü gizlenmemiş, self-host'a
  yönlendirilmiştir.
- **Self-host Worker'lar** sertleştirilmiş OAuth 2.1 değişmezlerini korur (redirect-origin
  allowlist, PKCE S256-only, HMAC+TTL kod, escHtml, constant-time, secret store). Detay: BUILD-BRIEF.md
  her `self-host/<worker>/` altında. Self-host Worker `auth.ts` aynı 6 invariant paylaşır.
  openfda WHO ICD-11 erişimi sunucu-tarafı OAuth ile (`ICD11_CLIENT_ID`/`SECRET` secrets) — istemci
  kimlik bilgisi açığa çıkmaz.
- **anamnesis RAG dürüstlüğü:** varlık/ilişki çıkarımı orchestrator (Claude) tarafından yapılır
  (LLM-in-the-loop GraphRAG); Worker yalnız depolar+gezer. Microsoft-GraphRAG global community
  özetleri Cloud Run indeksleyiciye ertelendi — sahte in-Worker yaklaşımla taklit edilmez. Annas
  tam metni yalnız analiz içindir; chunk'lar sınırlı/provenance'lı, toplu birebir çoğaltma yok.

---

## Doğrulama kapıları

**Skill-düzeyi (13 kapı, `check_integrity.py`):** `G-REF` · `G-CONN` · `G-ALWAYS` · `G-VERSION` ·
`G-COVERAGE` · `G-PROBE` · `G-XVAL` · `G-WHITELIST` · `G-SIZE` · `G-DESC` · **`G-PHASES`** (P0–P7
hepsi tanımlı + her faz kendi referans dosyasına işaret ediyor) · **`G-DESKEW`** (varsayılan yolda
hiçbir zenginleştirme modülü zorunlu yüklenmiyor) · **`G-AGENT`** (filoyu süren her alt-ajan o
sunucuları `tools:` izin listesinde taşıyor + kaldırılmış web tier'ı `WebSearch` hiçbirinde yok —
2026-08-07'de `evidence-synthesizer` SIFIR MCP aracıyla ama WebSearch'lü bulunduktan sonra eklendi). + **`G-RAG`** (çıktı faithfulness,
`rag_quality.py`, §7.2.1). **Plugin-düzeyi:** canlı `G-PROBE` (`.mcp.json` URL'lerinde initialize
handshake) + **`G-TOOLS`** (canlı `tools/list` **araç-yüzeyi sözleşmesi** + isteğe bağlı işlevsel
smoke) + **`G-IDENTITY`** (her self-host Worker kendi realm/paket/wrangler adını taşıyor) +
`G-BUNDLE` (`.mcp.json` ↔ `CONNECTORS.md` tutarlılığı) + nitel `G-TRUST` / `G-SURFACE`
/ `G-REGRESSION` / `G-COPYRIGHT`.

> **`--surface` (2026-08-07):** kapılı üç Worker `OPTIONS /mcp`'ye **401 ve hiç `Access-Control-*`
> başlığı olmadan** cevap veriyordu. Preflight tanım gereği kimlik-bilgisiz olduğu için (tarayıcı
> `OPTIONS`'a `Authorization` iliştirmez) bearer kapısının önüne konması, connector'ın hiçbir
> tarayıcı istemcisinden (claude.ai web · grok.com · ChatGPT web) EKLENEMEMESİ demekti. CORS
> katmanı artık kapının önünde; `WWW-Authenticate` expose ediliyor ki 401'in RFC 9728 işaretçisi
> tarayıcı JS'ine görünür olsun.
>
> **Neden `G-TOOLS` var (2026-08-07):** `G-PROBE` bir connector'ın *ulaşılabilir* olduğunu kanıtlar,
> hangi araçları sunduğunu değil. Filo ölçüldüğünde belgeler canlı yüzeyden sessizce ayrışmıştı —
> med-terminologies 37→31 araç, pubmed-epmc 10→11 (v2.9.7→v2.10.2), openathens 10→11, annas-reader 8→9, globocan 36→41
> kanser sitesi — ve her kapı yeşildi. `G-TOOLS` araç yüzeyini `fleet.tools.json` içinde **taahhüt
> edilmiş sözleşmeye** çevirir; sonraki sürüklenme keşif değil, kırmızı kapıdır.

**CI.** Depo CI'ı (`.github/workflows/ci.yml`) `plugins/*/tests/run_suites.py` glob'uyla plugin
kapılarını koşar. 2026-08-08'e dek evidentia'da o dosya YOKTU — yani yukarıdaki kapı katmanının
tamamı yalnız elle koşuyordu. Artık `tests/run_suites.py` beş **çevrimdışı** kapıyı (skill
integrity · hook paketi · G-BUNDLE · G-IDENTITY · G-RAG yapısal) CI'a bağlıyor; ağ + Bearer
isteyen `g_probe`/`g_tools` bilinçli olarak DIŞARIDA ve koşucu bunları adıyla listeliyor, ki
"yeşil CI" ile "tam kapsam" karıştırılmasın.

Koşum:
```bash
python tests/run_suites.py       # CI'ın koştuğu 5 çevrimdışı kapı (ağ yok, secret yok)
python scripts/g_probe.py        # .mcp.json URL'lerinde canlı initialize
python scripts/g_tools.py --smoke --surface  # canlı tools/list sözleşmesi + sunucu başına 1
                                 # salt-okunur çağrı + 10 self-host Worker'ın HTTP sözleşmesi
                                 # (CORS preflight 204 · RFC 9728 PRM ×2 · AS · health · 401 biçimi)
python scripts/g_identity.py     # 10 self-host Worker kimlik tutarlılığı
python scripts/g_bundle.py       # .mcp.json ↔ CONNECTORS.md tutarlılık
python skills/medical-research/evals/check_integrity.py        # yapısal: G-REF/G-CONN/G-ALWAYS/G-VERSION/G-COVERAGE/G-PROBE/G-XVAL/G-WHITELIST/G-SIZE/G-DESC/G-PHASES/G-DESKEW/G-AGENT
python skills/medical-research/evals/rag_quality.py            # G-RAG: çıktı faithfulness (§7.2.1) — yapısal taban; --judge ile LLM-judge (EVIDENTIA_JUDGE_KEY)
```

---

## Hook mimarisi (runtime enforcement)

Skill'in prose olarak anlattığı değişmezleri **çalışma anında** uygulayan deterministik komut
hook'ları (`hooks/hooks.json`). Hepsi **fail-open** (hook hatası asla araç çağrısını kırmaz) ve MCP
araçlarına özeldir.

| Hook | Olay | Ne yapar |
|---|---|---|
| **`guard_tool_call.py`** | `PreToolUse` (`mcp__.*`) | **En-az-yetki + kırık-araç + Anamnesis münhasır set.** Pipeworx gateway'lerinde §2.6 **allowlist dışı** her araç + **D1/D2** DENY. Anamnesis: `collection=evidentia:run:<run_id>` (ve/veya `evrun:` önek) scoped hybrid/search/graph **ALLOW**; kapsamsız hybrid/graph/global search **DENY**. D6 (`med-terminologies.icd11_search`) 2026-08-17 emekli. |
| **`retrieve_dont_dump.py`** | `PostToolUse` (`mcp__.*`) | Büyük tam-metin çıktısında **retrieve-don't-dump** hatırlatır: ham işleme, dual-write `ingest_document` → scoped `hybrid_query` / `semantic_search`. |
| **`anamnesis_ledger.py`** | `PostToolUse` (`mcp__.*anamnesis.*`) | Başarılı `ingest_document` id'sini koşu defterine yazar; `forget_document` / `forget_collection` id'sini düşürür. |
| **`session_preflight.py`** | `SessionStart` | Gated self-host connector key(ler)i ortamda eksikse `doppler run` hatırlatır; **hepsi mevcutsa sessiz**. |
| **`anamnesis_lifecycle.py`** | `SessionStart` / `UserPromptSubmit` / `SessionEnd` | startup: önceki koşunun `forget_collection` (yedek: ledger `forget_document`; stub'lanabilir) + yeni `run_id` / collection. `/evidentia` yeni koşu açar. Compact/resume aynı collection. **Stop'ta silmez** (P3/P5 insan-onay). |

**Devre dışı bırak:** `<proje>/.claude/evidentia-guard.off` dosyası oluştur → guard tümüyle
bypass eder. **Regresyon testi:** `python3 hooks/test_hooks.py`.
⚠️ Hook'lar oturum başında yüklenir → değişiklikten sonra Claude Code'u yeniden başlat (`claude`).

---

## İlişkili skill'ler

- **Upstream:** `mcp-scout` (connector roster bakımı — bundle edilmez, dış araçtır).
- **Downstream composable:** `pharmaintel` / `pharmapatent` (ticari/IP), `onko-erisim` /
  `ius-salutis` (bireysel erişim/dava), `carbon-html-report` / `carbon-pptx` (yayın render'ı).

---

*AS IS; no warranty. Internal-use grant. **Plugin v2.7.6 / flagship skill `medical-research`
v9.0.6** — v9.0.6 Marmara EBSCO-first cascade + v9.0.2 ordered tool playbook (`execution-map.md`) binds MUST/SHOULD/MAY/OUT +
`SKIP-REASON` for all 20 bundled servers. v9.0.0'da omurga, zorunlu 10-eksen domain matrisinden uçtan uca **PRISMA 2020 /
PRISMA-ScR P0–P7 hattına** yeniden yazıldı; eski eksenler silinmedi, **opsiyonel, bağlam-tetiklemeli
zenginleştirme modülleri**ne dönüştü (Adım 0.5, de-skew invariant). Native-MCP-first, temiz-kopya,
retrieve-don't-dump, no-fabrication, cömertlik ve tek-sefer/kanonik-önbellek doktrinleri ADR-05-safe
korunur. Bundled roster: 20 server + 13 companion.*
