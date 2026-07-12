# CureoPrivate

**Cureonics özel Claude Code plugin kataloğu** — Mahir Kurt tarafından geliştirilen Claude
plugin'lerinin private yayın deposu. Bu repo (`mahirkurt/CureoPrivate`), birden fazla
**kurulabilir Claude Code plugin'ini** tek bir katalog altında barındırır; yeni plugin'ler
eklendikçe genişler.

> **Adlandırma notu.** Repo ve dokümantasyon adı **CureoPrivate**'tir. Claude Code'un
> gördüğü **fonksiyonel katalog kimliği** ise `cureonics-marketplace` olarak korunur —
> `marketplace.json` `name` alanı ve tüm `@cureonics-marketplace` kurulum ekleri bu işlevsel
> kimliği kullanır (değiştirilmesi mevcut kurulumları kırar).

## Kataloğu ekleme

Claude Code oturumunda (REPL):

```
/plugin marketplace add mahirkurt/CureoPrivate
/plugin install <plugin>@cureonics-marketplace
```

> Bu repo **private**'tır; Claude Code, klonlama için sistemdeki GitHub kimlik bilgisini
> (`gh auth` / credential helper) kullanır. Katalog kaynağı taşınabilirdir (yerel yol
> içermez), bu yüzden çok-düğümlü `settings.json` senkronizasyonuyla uyumludur.

## Katalog

| Plugin | Sürüm | Açıklama |
|---|---|---|
| **evidentia** (Evidentia) | 1.6.0 | Çok-kaynaklı bilimsel/klinik kanıt sentezi + Türkiye-pazarı araştırma motoru — RAG/GraphRAG ile context-window-güvenli. Saf yapısal-otoriter kanıt (native kaynakta yoksa "VERİ YOK", web-scrape/uydurma yok). `medical-research` v8.4.0 flagship skill (semantik-kapsam: knowledge-map + Semantic Scope Scan + Completeness Gate + G-COVERAGE) + start skill + evidence-synthesizer alt-ajan + 5 komut + 14-server connector roster (PubMed/EuropePMC, ClinicalTrials, AdisInsight, ChEMBL, TİTCK, Mevzuat, Türk Patent, openFDA, WHO ICD-11, NPI, RxNorm/GtoPdb, OpenAlex, PubMed-EPMC, Semantic Scholar) + operatör-bağlı Annas Reader tam-metin + dört self-host Cloudflare Worker (anamnesis semantik-chunking/Vectorize-RAG/D1-GraphRAG + multi-query hybrid retrieval · drugddx klinik-DDI · openfda+ICD-11 · evidentia-kb recall booster). 12 doğrulama kapısı (G-RAG dahil). |
| **rxpraxis** (Rx Analyzer) | 1.2.1 | Türkiye-merkezli farmasötik jenerik/biyobenzer fırsat tarama süiti (`rxos` orkestratörü + medical-research, pharmaintel, pharmapatent, thoughtspot-roche kaynak skill'leri; 6 komut). v1.2: 7 no-auth çekirdek connector `.mcp.json` ile tanımlı (auth'lular kullanıcı bağlantılarından), L1 tool-manifest pin-load, §9 devre-kesici + extract-then-evict. Retail/topluluk-eczanesi, oral+topikal küçük molekül, tüm TA. Hospital/IV kapsam dışı. |
| **brand-ecosystem-core** | 1.0.0 | Brand Ecosystem v1.0'ın stratejik + sözel + görsel katmanları: 10 skill (brand-audit, brand-platform, brand-story, brand-maker(-ecosystem), brand-visual(-ecosystem), figma-forge, brand-touchpoint, brand-launch) + `/brand-ecosystem-core:pipeline` komutu. Claude.ai-native; Figma/GoDaddy/Exa opsiyonel. Ses katmanı için `brand-voice` plugin'i ile kompoze olur. |
| **bist-analyst** (BIST Uzmanı) | 1.1.8 | Borsa İstanbul analist kopilotu — çok zaman dilimli teknik + sektör-normalize temel + KAP açıklama/duygu + TCMB makro rejimini tek gerekçeli brifingde sentezler (tek hisse, haftalık tarama, KAP olayı, izleme listesi modları). Borsa MCP veri omurgası paket içinde. Karar destek; yatırım tavsiyesi değildir. |
| **fon-uzmani** (Fon Uzmanı) | 1.3.0 | Türkiye yatırım (YAT) + emeklilik (EMK) fonları için çok-skill karar-destek süiti: 8-aşamalı `fon-analiz-orkestratoru` + 6 kaynak skill + 12-modül saf-Python kuant kütüphanesi (Sharpe…HRP). Borsa MCP + fon-mcp omurgası; beş mod. SPK yatırım tavsiyesi değildir. |
| **vekayinuvis** (Vekayinüvis) | 2.5.0 | Birincil-kaynak-öncelikli Osmanlı/Türk tarih araştırma orkestratörü. Ottoman Archives + resmî Devlet Arşivleri kataloğu + YÖK Tez + DergiPark tam-metin + YÖK Akademik + akademik triangülasyon + OpenAthens/Anna's Reader tam-metin şelalesi + anamnesis RAG/GraphRAG. v2.5: `/vekayinuvis-durum` doctor komutu, 13-server G0 kapsam hook'u ve görüntü/OCR provenance atıf denetimi; IJMES/TDV İA çeviriyazı, Chicago atıf; 9 çalışma modu. `defaultEnabled:false` (opt-in). |

## Yapı

```
CureoPrivate/                             ← repo kökü (Claude Code'a EKLENECEK)
├── .claude-plugin/
│   └── marketplace.json                  ← katalog (plugin → ./plugins/<plugin>)
└── plugins/
    ├── evidentia/                        ← kanıt-sentezi motoru
    │   ├── .claude-plugin/plugin.json · .mcp.json
    │   ├── commands/   skills/ (start + medical-research)   shared/
    │   ├── self-host/ (anamnesis · drugddx · openfda · evidentia-kb Worker'ları)
    │   └── CONNECTORS.md · README.md
    ├── rxpraxis/                         ← farmasötik fırsat-tarama
    │   ├── .claude-plugin/plugin.json
    │   ├── commands/   skills/   shared/   evals/
    │   └── CONNECTORS.md · BUILD.md · README.md
    ├── brand-ecosystem-core/             ← marka ekosistemi
    │   ├── .claude-plugin/plugin.json
    │   ├── commands/pipeline.md
    │   ├── skills/   (10 skill: brand-audit … figma-forge)
    │   └── mcp.optional.json · README.md · CHANGELOG.md
    ├── bist-analyst/ · fon-uzmani/        ← finans plugin'leri (Borsa/fon-mcp)
    └── vekayinuvis/                      ← Osmanlı/Türk tarih araştırma plugin'i
        ├── .claude-plugin/plugin.json · .mcp.json
        ├── commands/   (9 slash komutu: kaynak-avi … literatur)
        ├── skills/   (start + vekayinuvis flagship + 9 referans)
        └── CONNECTORS.md · README.md · CHANGELOG.md
```

## evidentia — hızlı başlangıç

```
/plugin install evidentia@cureonics-marketplace
/help                                      # /evidentia komutları görünmeli
```

evidentia, dört self-host Cloudflare Worker'ı (anamnesis · drugddx · openfda · evidentia-kb)
paketli `.mcp.json` ile static-Bearer kimlikli getirir; akademik/klinik connector'lar (PubMed,
ClinicalTrials, TİTCK, OpenAlex, …) Claude.ai/Claude Code bağlantılarınızdan tüketilir. Anahtar
kurulumu için (operatöre özel, repo dışı) `EVIDENTIA-KURULUM-VE-KEYLER.md` notuna bakın.

## brand-ecosystem-core — hızlı başlangıç

```
/plugin install brand-ecosystem-core@cureonics-marketplace
/help                                      # /brand-ecosystem-core:pipeline görünmeli
```

Uçtan uca kanonik kurulum sırası için `/brand-ecosystem-core:pipeline`; her skill tek
başına da çağrılabilir (örn. `brand-ecosystem-core:brand-platform`). Skill'ler
Claude.ai-native (`mcp_servers_required: []`); Figma / GoDaddy / Exa zenginleştiricileri
opsiyoneldir (`plugins/brand-ecosystem-core/mcp.optional.json`). Ses & ton katmanı ayrı
`brand-voice` plugin'ine aittir.

## rxpraxis — hızlı başlangıç

Kurulumdan sonra Claude Code'u yeniden başlatın, sonra:

```
/plugin install rxpraxis@cureonics-marketplace
/help                                      # 6 rxpraxis komutu görünmeli
```

Beklenen **6 komut**: `/rxpraxis-scan` · `/rxpraxis-validate` · `/rxpraxis-regulatory` ·
`/rxpraxis-patent` · `/rxpraxis-midas` · `/rxpraxis-evidence`.

**Duman testi:** yeni sohbet → `rxpraxis nedir, nereden başlayayım?` → `start` skill'i bağlı
connector'ları ve komutları raporlar. Tek-asset:
`/rxpraxis-validate dapagliflozin 10 mg film tablet`.

rxpraxis canlı MCP **paketlemez**; connector'ları Claude.ai/Claude Code bağlantılarınız
üzerinden tüketir (eşleme: `plugins/rxpraxis/CONNECTORS.md`). Eksik connector tarama-zamanı
**degrade mod** ile bildirilir.

## Yeni plugin ekleme

1. `plugins/<yeni-plugin>/.claude-plugin/plugin.json` + bileşenleri (commands/skills) ekle.
2. `.claude-plugin/marketplace.json` → `plugins[]` dizisine girdi ekle
   (`name`, `source: ./plugins/<yeni-plugin>`, `version`, `description`).
3. Commit + push → `/plugin marketplace update cureonics-marketplace`.

## Güncelleme / kaldırma

```
/plugin marketplace update cureonics-marketplace
/plugin update <plugin>@cureonics-marketplace
/plugin uninstall <plugin>@cureonics-marketplace
```
