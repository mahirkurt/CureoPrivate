# CureoPrivate

**Cureonics özel Claude Code plugin kataloğu** — Mahir Kurt tarafından geliştirilen Claude
plugin'lerinin private yayın deposu. Bu repo (`mahirkurt/CureoPrivate`), **on kurulabilir
Claude Code plugin'ini** tek bir katalog altında barındırır; yeni plugin'ler eklendikçe genişler.

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

Sürümler her plugin'in `.claude-plugin/plugin.json` dosyasından gelir; `marketplace.json`
bunlarla senkron tutulur (tek doğruluk kaynağı = plugin.json).

| Plugin | Sürüm | Alan | Açıklama |
|---|---|---|---|
| **evidentia** (Evidentia) | 2.7.2 | araştırma | Genel-amaçlı **PRISMA 2020 / PRISMA-ScR** tıbbi literatür inceleme motoru — her soru tipi (tedavi/tanı/prognoz/etiyoloji/önleme). `medical-research` v9.0.1 flagship: P0 protokol/PICO → P1 arama → P2 getirim+dedup → P3 tarama → P4 çıkarım → P5 yanlılık riski (RoB2/ROBINS-I/QUADAS-2/NOS/PROBAST) → P6 GRADE → P7 PRISMA akış + SoF. Bibliyografik çekirdek her-zaman-açık; legal-first tam-metin şelalesi (OpenAthens/Millet Kütüphanesi Tier 3 lisanslı → Wiley → Anna's Reader son çare → Unpaywall); anamnesis RAG/GraphRAG. Tedavi-alanı/HTA/KOL/Türkiye-pazarı/epidemiyoloji katmanları **opsiyonel** (de-skew invariantı). On bir self-host connector. |
| **cureolex** (Cureolex) | 3.8.6 | regülasyon | Türkiye **sağlık mevzuatı norm-üretim** protokolü (kanun · CBK · CB kararı · yönetmelik · tebliğ · genelge). Dokuz mod: DRAFT · AMEND · ANALYZE · COMPLY (5210 uyum) · OPINE · RIA · COMPARATIVE_LAW · TBMM_KANUN_TEKLIFI · EX_POST_EVALUATION. 5210 sayılı Yönetmelik + AYM belirlilik içtihadı + OECD Better Regulation çerçevesi; G0–G9 kalite kapıları + `evidence_ledger` no-fabrication disiplini. Tam-filo: 22 wire'lı MCP + 3 companion. Bireysel dava/malpraktis **kapsam dışı** (Scope Guard). |
| **vekayinuvis** (Vekayinüvis) | 3.4.12 | araştırma | Birincil-kaynak-öncelikli **Osmanlı/Türk tarih** araştırma orkestratörü. Devlet Arşivleri resmî kataloğu + Ottoman Archives + YÖK Tez + DergiPark + yasama/mevzuat katmanı + lisanslı tam-metin şelalesi (OpenAthens → Anna's Reader son çare) + anamnesis RAG/GraphRAG. 17-server filo; IJMES/TDV İA çeviriyazı, Chicago atıf; 9 çalışma modu. **`defaultEnabled: false`** (opt-in). |
| **historia-medicinae** (Historia Medicinae) | 0.1.2 | araştırma | Küresel **tıp tarihi** araştırma orkestratörü — Avrupa-merkezli olmayan, Mezopotamya/Mısır'dan çağdaş küresel sağlığa. 11 araştırma modu (SOURCE_HUNT · MORBUS · INSTITUTIO · CONCEPTUS · ETHICA · PROSOPOGRAPHIA · THERAPEUTICA · SANITAS_PUBLICA · HISTORIOGRAPHIA · EDITIO · RELATIO) + metodoloji skill'leri. 25-server filo; Wellcome sayfa-düzeyi tam-metin + lisanslı OpenAthens → Anna's son çare. Osmanlıca paleografi/HTR → vekayinuvis; çağdaş klinik geçerlilik → evidentia. **`defaultEnabled: false`** (opt-in). |
| **rxpraxis** (Rx Analyzer) | 1.2.3 | farma | Türkiye-merkezli **jenerik/biyobenzer fırsat tarama** süiti. `rxos` orkestratörü (7-aşamalı deterministik boru hattı, G0–G6 kapıları) + medical-research · pharmaintel · pharmapatent · thoughtspot-roche kaynak skill'leri. Retail/topluluk-eczanesi, oral+topikal küçük molekül, tüm TA. Hospital/IV **kapsam dışı**. |
| **fon-uzmani** (Fon Uzmanı) | 1.3.1 | finans | Türkiye yatırım (YAT) + emeklilik (EMK) fonları **karar-destek** süiti: 8-aşamalı `fon-analiz-orkestratoru` (G0–G7) + 6 kaynak skill + 12-modül saf-Python kuant kütüphanesi (Sharpe…HRP). Borsa MCP + fon-mcp omurgası; beş mod. SPK yatırım tavsiyesi **değildir**. |
| **bist-analyst** (BIST Uzmanı) | 1.1.9 | finans | **Borsa İstanbul** analist kopilotu — çok zaman dilimli teknik + sektör-normalize temel + KAP açıklama/duygu + TCMB makro rejimini tek gerekçeli brifingde sentezler (tek hisse, haftalık tarama, KAP olayı, izleme listesi modları). Borsa MCP omurgası paket içinde. Yatırım tavsiyesi **değildir**. |
| **sci-audit** (Scientific Audit) | 0.2.4 | bilimsel bütünlük | LLM-üretimi bilimsel metinler için **alan-bağımsız adli + dilsel denetçi**. Yedi eksen: (A) referans bütünlüğü · (B) iddia temellendirme + tam-metin doğrulama · (C) belge-içi istatistik tutarlılığı (statcheck/GRIM/GRIMMER/SPRITE) · (D) halüsinasyon sinyalleri + varlık doğrulama · (E) 14 raporlama kılavuzu (PRISMA/CONSORT/STROBE/TRIPOD…) · (F) AI-şeffaflığı (ICMJE/COPE) · (G) Türkçe bilimsel dil. Deterministik çekirdek **saf Python stdlib**. Çözülemeyen kaynak `unverified` olur, asla "geçti" olmaz. |
| **edupedia** (Edupedia) | 0.10.0 | eğitim | MEB **Türkiye Yüzyılı Maarif Modeli** (2024) kazanımlarından kazanım-izlenebilir, WCAG 2.1 AA erişilebilir, tek-dosya etkileşimli **HTML öğrenim modülleri** üretir (DEHB-odaklı, IBM Carbon v11). `carbon-edupedia` flagship 9 mod (MODULE · QUIZ · FLASHCARDS · GAME · EXPLAINER · ASSESSMENT · SERIES · CURRICULUM · EXAM) ve 16 kalite kapısı sunar; `start` yönlendirir. İki anahtarlı MCP: `maarif-mufredat` · `egitim-kaynak`. Teslim yerel HTML; plugin yayınlamaz. `/edupedia:soru` bir veya birden fazla soruyu tek HTML'de çözer. Kapsam yalnız Türkiye MEB. |
| **brand-ecosystem-core** (Brand Ecosystem) | 1.1.3 | marka | Brand Ecosystem'in stratejik + sözel + görsel katmanları: 12 skill (brand-audit · brand-platform · brand-story · brand-maker · brand-visual · figma-forge · brand-touchpoint · brand-launch · brand-verify · brand-market-signal …) + `/brand-ecosystem-core:pipeline` komutu. Claude.ai-native; Figma/GoDaddy/Exa **opsiyonel**. Ses katmanı ayrı `brand-voice` plugin'ine aittir. |

### Bileşen envanteri

Sayılar diskteki `commands/` dosyaları, `skills/` alt dizinleri, `agents/` alt-ajan dosyaları (`openai.yaml` hariç), `hooks/` varlığı ve `.mcp.json` → `mcpServers` anahtarlarıdır. `marketplace.json` / `plugin.json` sürümleriyle hizalıdır.

| Plugin | Komut | Skill | Alt-ajan | Hook | Paketli MCP |
|---|---:|---:|---:|:---:|---:|
| evidentia | 7 | 2 | 1 | ✅ | 20 |
| cureolex | 10 | 2 | 4 | ✅ | 22 |
| vekayinuvis | — | 16 | 1 | ✅ | 17 |
| historia-medicinae | — | 17 | 2 | ✅ | 25 |
| rxpraxis | 6 | 6 | — | — | 6 |
| fon-uzmani | 5 | 8 | — | — | 2 |
| bist-analyst | — | 2 | — | — | 1 |
| sci-audit | 7 | 7 | 8 | ✅ | 4 |
| edupedia | 5 | 2 | 1 | ✅ | 2 |
| brand-ecosystem-core | 1 | 12 | 5 | ✅ | 7 |

**Komutu olmayan plugin'ler** (vekayinuvis, historia-medicinae, bist-analyst) önek-siz **skill mimarisi** kullanır:
`/<plugin>:<ad>` biçiminde skill olarak çağrılırlar. **Paketli MCP** sütunu plugin'in
`.mcp.json` dosyasındaki server sayısıdır; auth gerektiren connector'lar kullanıcının kendi
Claude.ai/Claude Code bağlantılarından tüketilir ve eksiklerse **degrade mod** ile bildirilir.
`brand-ecosystem-core` ayrıca `mcp.optional.json` ile Figma / GoDaddy / Exa taşır — bunlar
paketli sayıya dahil değildir.

## Yapı

```
CureoPrivate/                             ← repo kökü (Claude Code'a EKLENECEK)
├── .claude-plugin/
│   └── marketplace.json                  ← katalog (plugin → ./plugins/<plugin>)
├── docs/superpowers/                     ← tasarım spec'leri + uygulama planları
└── plugins/
    ├── evidentia/                        ← PRISMA kanıt-sentezi motoru
    │   ├── .claude-plugin/plugin.json · .mcp.json · hooks/
    │   ├── commands/ (7)   skills/ (start · medical-research)   agents/   shared/
    │   ├── self-host/ (anamnesis · drugddx · openfda · evidentia-kb · who-gho · globocan · ema · pubmed-epmc · openalex · semantic-scholar)
    │   └── CONNECTORS.md · README.md
    ├── cureolex/                      ← sağlık mevzuatı norm-üretimi
    │   ├── .claude-plugin/plugin.json · .mcp.json · hooks/
    │   ├── commands/ (10: lex-draft … lex-expost)   skills/   agents/ (4)
    │   └── README.md
    ├── vekayinuvis/                      ← Osmanlı/Türk tarih araştırması
    │   ├── .claude-plugin/plugin.json · .codex-plugin/plugin.json · .mcp.json · hooks/
    │   ├── skills/ (16: start · vekayinuvis flagship · mod + akış-skill'leri)
    │   └── CONNECTORS.md · README.md · CHANGELOG.md
    ├── historia-medicinae/               ← küresel tıp tarihi araştırması
    │   ├── .claude-plugin/plugin.json · .mcp.json · hooks/
    │   ├── skills/ (17: start · durum · historia-medicinae flagship · 11 mod + metodoloji)
    │   ├── agents/ (tarih-tarama-distilleri · anakronizm-denetcisi)
    │   └── CONNECTORS.md · README.md · CHANGELOG.md
    ├── rxpraxis/                         ← farmasötik fırsat-tarama
    │   ├── commands/ (6)   skills/ (6)   shared/   evals/
    │   └── CONNECTORS.md · BUILD.md · README.md
    ├── fon-uzmani/ · bist-analyst/       ← finans plugin'leri (Borsa MCP / fon-mcp)
    ├── sci-audit/                        ← bilimsel metin denetçisi
    │   ├── commands/ (7)   skills/ (7)   agents/ (8)   hooks/   scripts/
    │   └── README.md
    ├── edupedia/                         ← Maarif Modeli öğrenim modülü üreticisi
    │   ├── commands/ (6)   skills/ (carbon-edupedia · start)   agents/   hooks/
    │   └── CONNECTORS.md · README.md
    └── brand-ecosystem-core/             ← marka ekosistemi
        ├── commands/pipeline.md   skills/ (12)   agents/ (5)   hooks/
        └── .mcp.json · mcp.optional.json · README.md · CHANGELOG.md
```

## Hızlı başlangıç

Her plugin kurulduktan sonra **Claude Code'u yeniden başlatın** (yeni skill/agent/MCP
kayıtları ancak restart'ta görünür), sonra `/help` ile komutları doğrulayın.

**evidentia** — PRISMA sistematik/kapsam derlemesi

```
/plugin install evidentia@cureonics-marketplace
/evidentia                                 # 7 komut: -protocol -fulltext -synthesize -appraise -kol -connectors
```

On bir self-host connector (anamnesis · drugddx · openfda · evidentia-kb · who-gho ·
globocan · ema · pubmed-epmc · openalex · semantic-scholar · openathens) paketli
`.mcp.json` ile gelir; akademik/klinik connector'lar sizin bağlantılarınızdan
tüketilir. Anahtarlar için (operatöre özel, repo dışı) `EVIDENTIA-KURULUM-VE-KEYLER.md`.

**cureolex** — sağlık mevzuatı taslak/reform

```
/plugin install cureolex@cureonics-marketplace
/lex-connectors                            # tam-filo sağlık kontrolü
/lex-draft <konu>                          # · /lex-amend · /lex-comply · /lex-ria · /lex-bill …
```

**vekayinuvis** — Osmanlı/Türk tarih araştırması (opt-in)

```
/plugin install vekayinuvis@cureonics-marketplace
/plugin enable vekayinuvis                 # defaultEnabled:false — açıkça etkinleştirin
/vekayinuvis:start                         # filo durumu + mod seçimi
```

Devlet Arşivleri kataloğu **tek-cihaz oturum** kilidiyle çalışır: HP'deki authenticated
tarayıcı oturumu canlı olmalıdır (`devarsiv_session_status`). Ödeme **daima insanda**.

**historia-medicinae** — küresel tıp tarihi (opt-in)

```
/plugin install historia-medicinae@cureonics-marketplace
/plugin enable historia-medicinae          # defaultEnabled:false — açıkça etkinleştirin
/historia-medicinae:start                  # filo durumu + mod seçimi
```

Osmanlıca paleografi/HTR vekayinuvis'e, çağdaş klinik geçerlilik evidentia'ya, çıktı-QA
sci-audit'e delege edilir. Birincil kaynak IIIF motorudur (Wellcome sayfa-düzeyi tam-metin
ölçülmüş biçimde çalışır; LoC/NLM ölçülmüş blok).

**sci-audit** — bilimsel metin denetimi

```
/plugin install sci-audit@cureonics-marketplace
/audit <metin>                             # · /verify-citations · /check-stats · /check-turkish
```

**edupedia** — Maarif kazanımından etkileşimli modül

```
/plugin install edupedia@cureonics-marketplace
/edupedia:kazanim-bul <konu>               # kazanım keşfi
/edupedia:modul <kazanım-kodu>             # yerel tek-dosya HTML modül üret
```

**rxpraxis** — jenerik/biyobenzer fırsat taraması

```
/plugin install rxpraxis@cureonics-marketplace
/rxpraxis-scan                             # · -validate · -regulatory · -patent · -midas · -evidence
```

**fon-uzmani** / **bist-analyst** — finans

```
/plugin install fon-uzmani@cureonics-marketplace
/fon-analiz <fon-kodu>                     # · /fon-tara · /fon-karsilastir · /fon-portfoy · /fon-izle

/plugin install bist-analyst@cureonics-marketplace   # skill mimarisi — komut yok, doğal dille çağrılır
```

**brand-ecosystem-core** — marka ekosistemi

```
/plugin install brand-ecosystem-core@cureonics-marketplace
/brand-ecosystem-core:pipeline             # uçtan uca kanonik kurulum sırası
```

## Ortak sözleşmeler

Katalogdaki araştırma/regülasyon plugin'leri (evidentia · cureolex · vekayinuvis ·
historia-medicinae · rxpraxis · sci-audit) aynı invariantları paylaşır:

- **No-fabrication.** Native kaynakta veri yoksa çıktı "VERİ YOK"/`unverified` olur; asla
  uydurulmaz. Erişilemeyen yüzeyler deterministik `manual_required` zarfı döner.
- **Kapsam manifestosu (G0).** Her substantif çıktı, hangi connector'ın çalıştığını /
  boş döndüğünü / degrade ettiğini gerekçesiyle beyan eder — sessiz atlama yok.
- **Retrieve-don't-dump.** Ağır çok-connector süpürmeler alt-ajanlara (evidence-synthesizer,
  arsiv-tarama-distilleri, tarih-tarama-distilleri, legal/medical distiller) izole edilir; ana bağlama yalnız
  damıtılmış zarf döner. Büyük tam-metinler anamnesis'e ingest edilip sınırlı sorgulanır.
- **İnsan denetimi.** Hepsi karar-destek niteliğindedir — klinik tavsiye, resmî hukuki
  mütalaa veya yatırım danışmanlığı **değildir**.
- **Degrade, çökme değil.** Eksik connector/anahtar çalışmayı durdurmaz; ilgili katman
  degrade eder ve bunu manifestoda beyan eder.

## Yeni plugin ekleme

1. `plugins/<yeni-plugin>/.claude-plugin/plugin.json` + bileşenleri ekle (`commands/`,
   `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json` — anahtarlar `plugin.json`'da
   belirtilmezse konvansiyonel yollardan otomatik keşfedilir).
2. `.claude-plugin/marketplace.json` → `plugins[]` dizisine girdi ekle
   (`name`, `displayName`, `source: ./plugins/<yeni-plugin>`, `version`,
   `description`, `author`, `category`, `keywords`, `strict`).
   **Sürüm ve açıklama plugin.json ile senkron olmalıdır.**
3. Bu README'deki katalog tablosu, bileşen envanteri, dizin ağacı ve hızlı başlangıcı
   aynı commit'te hizala (sürüm = plugin.json; sayılar = disk).
4. Kapıları koştur (aşağı bkz.) → commit + push →
   `/plugin marketplace update cureonics-marketplace`.

## Kalite kapıları

Bu depo GitHub üzerinden doğrudan marketplace olarak hizmet verir: **main'e giren
her commit, ara aşama olmadan kullanıcıların kurduğu artefakttır.** İki
deterministik, offline kapı bunu korur ve her push/PR'da CI'da koşar
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):

```
python3 tools/fleetkit/check_drift.py --all        # türetilmişlik + sürüm + sunucu kimliği
python3 tools/fleetkit/check_marketplace.py        # marketplace bileşen sözleşmesi
```

| Kapı | Neyi yakalar |
|---|---|
| `check_drift` | türetilmiş dosya bayat · sürüm zinciri tutarsız · vendor'lı `fleet_probe` sapmış · çift `hooks.json` · düzyazı filo sayısı yanlış · **filoda olmayan sunucu kimliğine atıf** (yeniden adlandırma/emeklilik sürüklenmesi) |
| `check_marketplace` | katalog ↔ disk uyuşmazlığı · eksik katalog alanı · skill/agent `name` ≠ dizin/dosya · eksik `description` · bilinmeyen hook olayı · **var olmayan hook betiği** · `CLAUDE_PLUGIN_ROOT` kullanmayan (taşınabilir olmayan) komut · `timeout` yok · hook betiğinde sözdizimi hatası |

**Neden iki ayrı kapı:** `check_drift` yalnız *türetilen* şeyleri denetler. Skill
frontmatter'ı, agent adı, hook betiği yolu ve komut açıklaması **türetilmez** —
bu yüzden görünmezlerdi. Bu katmanların bozulması hata da vermez: skill sessizce
keşfedilemez, hook her oturumda sessizce düşer, komut menüde boş görünür.
`check_marketplace` tam olarak bu *sessiz* sınıf içindir.

CI ayrıca kapılara kasıtlı kusur enjekte edip **yakaladıklarını** doğrular —
"yeşil CI" ile "gerçekten denetleyen CI"yı ayırmak için.

Canlı MCP sağlığı (`tools/fleetkit/audit_plugins.py`, 56 uca gerçek `initialize`)
**CI'da koşmaz**: Bearer anahtarı ister ve bir upstream arızası PR'ları bloke
ederdi. Elle koşulur.

## Güncelleme / kaldırma

```
/plugin marketplace update cureonics-marketplace
/plugin update <plugin>@cureonics-marketplace
/plugin uninstall <plugin>@cureonics-marketplace
```
