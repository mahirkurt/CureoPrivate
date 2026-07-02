# evidentia

**Genel-amaçlı PRISMA tıbbi literatür inceleme aracı** — bir Claude Code / claude.ai
marketplace plugin'i. Tüm tıp alanlarını ve her soru tipini (tedavi/tanı/prognoz/etiyoloji/
önleme) kapsayan uçtan uca **PRISMA 2020 / PRISMA-ScR sistematik/kapsam derlemesi** motoru.
`medical-research` v9.0.0 flagship skill'ini, her-zaman-açık bibliyografik çekirdek
connector'ları, opsiyonel bağlam-tetiklemeli zenginleştirme modüllerini ve `mcp-scout` ile
canlı-doğrulanmış klinik genişletme MCP'lerini tek kurulabilir pakette toplar.

---

## Ne sağlar

- **Flagship skill:** `medical-research` v9.0.0 — omurga **P0–P7 PRISMA hattı**, soru
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
  - `/evidentia-fulltext` — copyright-kapılı tam-metin kademesi (EPMC→Paper Search→annas-mcp→
    Wiley→Unpaywall).
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
  Nöro/Nadir), Regülatuar/HTA/MedAffairs/Drug-Intelligence, Türkiye-pazarı (TİTCK/Mevzuat/
  TÜRKPATENT), Epidemiyoloji (openfda ICD-11 + PopHIVE ABD). Sinyal yoksa çekirdek bibliyografik
  PRISMA hattı tek başına koşar — bu **de-skew** değişmezi `G-DESKEW`/`G-PHASES` kapılarıyla
  denetlenir.
- **Tam-metin connector'ı:** **Annas Reader** (operatör-bağlı Cloud Run, OAuth-gated) — makale/kitap
  tam-metin erişimi (`article_search`/`download`, `book_search`/`download`).
- **RAG/GraphRAG substratı:** **anamnesis** self-host Worker — semantik chunking (bge-m3 1024-d) +
  Vectorize + D1 bilgi grafiği. Tam-metin/büyük araç çıktılarını **bağlama dökmeden** indeksler;
  `hybrid_query` ile context-window'a sığan, provenance-damgalı kanıt paketi sunar
  (**`evidence_index`** kanonik artefaktı — context-window taşma koruması).
- **Bundled connector roster** (`.mcp.json`) — 16 server (bibliyografik çekirdek + opsiyonel
  curated-intelligence/regülatuar/α-katman/self-host); tek doğruluk kaynağı
  [`CONNECTORS.md`](./CONNECTORS.md).
- **Dört self-host bileşeni** — sertleştirilmiş OAuth 2.1 Cloudflare Worker'ları (`self-host/`):
  [`drugddx-mcp`](./self-host/drugddx-mcp/BUILD-BRIEF.md) (klinik DDI boşluğu) ·
  [`anamnesis-mcp`](./self-host/anamnesis-mcp/BUILD-BRIEF.md) (RAG/GraphRAG substratı) ·
  [`openfda-mcp`](./self-host/openfda-mcp/) (FDA openFDA + WHO ICD-11; deploy talimatı §3.3) ·
  [`evidentia-kb-mcp`](./self-host/evidentia-kb-mcp/) (KB semantik-kapsam takviyesi, opsiyonel; §3.4).

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
| **Tier-O** operatör Worker'ları | TİTCK Cache, YÖK Akademik, **Annas Reader** (tam-metin), **openfda** (FDA/WHO ICD-11), **evidentia-kb** (KB takviyesi, opsiyonel) | ✅ |
| **Tier-A** auth-gerekli | PubMed/EPMC, Consensus, AdisInsight, TİTCK, Mevzuat, Türk Patent, … | env / Settings |
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
  her `self-host/<worker>/` altında. Tüm dört Worker `auth.ts` birebir aynı 6 invariant paylaşır.
  openfda WHO ICD-11 erişimi sunucu-tarafı OAuth ile (`ICD11_CLIENT_ID`/`SECRET` secrets) — istemci
  kimlik bilgisi açığa çıkmaz.
- **anamnesis RAG dürüstlüğü:** varlık/ilişki çıkarımı orchestrator (Claude) tarafından yapılır
  (LLM-in-the-loop GraphRAG); Worker yalnız depolar+gezer. Microsoft-GraphRAG global community
  özetleri Cloud Run indeksleyiciye ertelendi — sahte in-Worker yaklaşımla taklit edilmez. Annas
  tam metni yalnız analiz içindir; chunk'lar sınırlı/provenance'lı, toplu birebir çoğaltma yok.

---

## Doğrulama kapıları

**Skill-düzeyi (12 kapı, `check_integrity.py`):** `G-REF` · `G-CONN` · `G-ALWAYS` · `G-VERSION` ·
`G-COVERAGE` · `G-PROBE` · `G-XVAL` · `G-WHITELIST` · `G-SIZE` · `G-DESC` · **`G-PHASES`** (P0–P7
hepsi tanımlı + her faz kendi referans dosyasına işaret ediyor) · **`G-DESKEW`** (varsayılan yolda
hiçbir zenginleştirme modülü zorunlu yüklenmiyor). + **`G-RAG`** (çıktı faithfulness,
`rag_quality.py`, §7.2.1). **Plugin-düzeyi:** canlı `G-PROBE` (`.mcp.json` URL'lerinde initialize
handshake) + `G-BUNDLE` (`.mcp.json` ↔ `CONNECTORS.md` tutarlılığı) + nitel `G-TRUST` / `G-SURFACE`
/ `G-REGRESSION` / `G-COPYRIGHT`. Koşum:
```bash
python scripts/g_probe.py        # .mcp.json URL'lerinde canlı initialize
python scripts/g_bundle.py       # .mcp.json ↔ CONNECTORS.md tutarlılık
python skills/medical-research/evals/check_integrity.py        # yapısal: G-REF/G-CONN/G-ALWAYS/G-VERSION/G-COVERAGE/G-PROBE/G-XVAL/G-WHITELIST/G-SIZE/G-DESC/G-PHASES/G-DESKEW
python skills/medical-research/evals/rag_quality.py            # G-RAG: çıktı faithfulness (§7.2.1) — yapısal taban; --judge ile LLM-judge (EVIDENTIA_JUDGE_KEY)
```

---

## İlişkili skill'ler

- **Upstream:** `mcp-scout` (connector roster bakımı — bundle edilmez, dış araçtır).
- **Downstream composable:** `pharmaintel` / `pharmapatent` (ticari/IP), `onko-erisim` /
  `ius-salutis` (bireysel erişim/dava), `carbon-html-report` / `carbon-pptx` (yayın render'ı).

---

*AS IS; no warranty. Internal-use grant. **Plugin v2.0.0 / flagship skill `medical-research`
v9.0.0** — v9.0.0'da omurga, zorunlu 10-eksen domain matrisinden uçtan uca **PRISMA 2020 /
PRISMA-ScR P0–P7 hattına** yeniden yazıldı; eski eksenler silinmedi, **opsiyonel, bağlam-tetiklemeli
zenginleştirme modülleri**ne dönüştü (Adım 0.5, de-skew invariant). Native-MCP-first, temiz-kopya,
retrieve-don't-dump, no-fabrication, cömertlik ve tek-sefer/kanonik-önbellek doktrinleri ADR-05-safe
korunur. Bundled roster: 16 server.*
