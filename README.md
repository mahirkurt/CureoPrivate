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
| **rxpraxis** | 1.1.0 | Türkiye-merkezli farmasötik jenerik/biyobenzer fırsat tarama süiti (`rxos` orkestratörü + medical-research, pharmaintel, pharmapatent, thoughtspot-roche kaynak skill'leri; 6 komut). Retail/topluluk-eczanesi, oral+topikal küçük molekül, tüm TA. Hospital/IV kapsam dışı. |

## Yapı

```
marketplace/                              ← marketplace kökü (Claude Code'a EKLENECEK)
├── .claude-plugin/
│   └── marketplace.json                  ← katalog (plugin → ./plugins/<plugin>)
└── plugins/
    └── rxpraxis/                         ← ilk plugin
        ├── .claude-plugin/plugin.json
        ├── commands/   skills/   shared/   evals/
        └── CONNECTORS.md · BUILD.md · README.md
```

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
