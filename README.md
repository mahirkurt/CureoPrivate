# cureonics-marketplace

**Cureonics Claude Code plugin marketplace** — Mahir Kurt tarafından geliştirilen Claude
plugin'lerinin yayın deposu. Bu repo, bir veya daha fazla **kurulabilir Claude Code plugin'ini**
tek bir katalog altında barındırır; yeni plugin'ler eklendikçe genişler.

## Marketplace'i ekleme

Claude Code oturumunda (REPL):

```
/plugin marketplace add mahirkurt/marketplace
/plugin install <plugin>@cureonics-marketplace
```

> Bu repo **private**'tır; Claude Code, klonlama için sistemdeki GitHub kimlik bilgisini
> (`gh auth` / credential helper) kullanır. Marketplace kaynağı taşınabilirdir (yerel yol
> içermez), bu yüzden çok-düğümlü `settings.json` senkronizasyonuyla uyumludur.

## Katalog

| Plugin | Sürüm | Açıklama |
|---|---|---|
| **rxpraxis** (Rx Analyzer) | 1.2.1 | Türkiye-merkezli farmasötik jenerik/biyobenzer fırsat tarama süiti (`rxos` orkestratörü + medical-research, pharmaintel, pharmapatent, thoughtspot-roche kaynak skill'leri; 6 komut). v1.2: 7 no-auth çekirdek connector `.mcp.json` ile tanımlı (auth'lular kullanıcı bağlantılarından), L1 tool-manifest pin-load, §9 devre-kesici + extract-then-evict. Retail/topluluk-eczanesi, oral+topikal küçük molekül, tüm TA. Hospital/IV kapsam dışı. |
| **brand-ecosystem-core** | 1.0.0 | Brand Ecosystem v1.0'ın stratejik + sözel + görsel katmanları: 10 skill (brand-audit, brand-platform, brand-story, brand-maker(-ecosystem), brand-visual(-ecosystem), figma-forge, brand-touchpoint, brand-launch) + `/brand-ecosystem-core:pipeline` komutu. Claude.ai-native; Figma/GoDaddy/Exa opsiyonel. Ses katmanı için `brand-voice` plugin'i ile kompoze olur. |

## Yapı

```
marketplace/                              ← marketplace kökü (Claude Code'a EKLENECEK)
├── .claude-plugin/
│   └── marketplace.json                  ← katalog (plugin → ./plugins/<plugin>)
└── plugins/
    ├── rxpraxis/                         ← ilk plugin
    │   ├── .claude-plugin/plugin.json
    │   ├── commands/   skills/   shared/   evals/
    │   └── CONNECTORS.md · BUILD.md · README.md
    └── brand-ecosystem-core/             ← marka ekosistemi plugin'i
        ├── .claude-plugin/plugin.json
        ├── commands/pipeline.md
        ├── skills/   (10 skill: brand-audit … figma-forge)
        └── mcp.optional.json · README.md · CHANGELOG.md
```

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
