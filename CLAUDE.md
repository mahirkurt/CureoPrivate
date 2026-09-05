# CLAUDE.md

Bu dosya, bu depoda çalışan Claude Code'a (claude.ai/code) rehberlik eder.

## Depo Ne İşe Yarar

**CureoPrivate**, Claude Code plugin'lerinin **yayın kataloğudur** — `cureonics-marketplace`.
Kullanıcılar `/plugin marketplace add mahirkurt/CureoPrivate` ile bu depoyu doğrudan
GitHub'dan klonlar.

> **main'e giren her commit, ara aşama olmadan kullanıcıların kurduğu artefakttır.**
> Build adımı, staging ortamı, yayın etiketi yoktur. `git push` = release.
> Bu yüzden aşağıdaki iki kapı danışma niteliğinde değildir.

Kaynak dil Markdown (skill/komut/agent) + JSON (manifest); dokümantasyon **Türkçe**.

## Ortak Çalışma Alanı — CureoHub ile Çift Repo

Bu depo tek başına anlamlı değildir. Plugin'lerin `.mcp.json` dosyalarındaki
`*.cureonics.com` / `*.cureonics.workers.dev` uçlarının **kaynak kodu ve dağıtımı**
kardeş `CureoHub` deposunda yaşar.

| | **CureoHub** | **CureoPrivate** (bu depo) |
|---|---|---|
| Rol | MCP sunucu **kaynağı** + dağıtım (HP/Pi systemd, Cloudflare Worker) | Plugin **tüketimi** ve yayını |
| Yol | `/mnt/thunderbolt/workspaces/CureoHub` | `/mnt/thunderbolt/workspaces/CureoPrivate` |
| Remote | `github.com/mahirkurt/CureoHub` | `github.com/mahirkurt/CureoPrivate` |
| Yayın | systemd/`wrangler deploy` | `git push` → `/plugin marketplace update` |

`.claude/settings.json` → `permissions.additionalDirectories` her iki repoyu karşılıklı
erişilebilir kılar: bu depoda açılan bir oturum `CureoHub`'ı okuyabilir, tersi de geçerlidir.
Editör tarafında kanonik giriş noktası `../Cureonics_Marketplace.code-workspace`
(multi-root; üçüncü klasör: özel süit bundle'ı `CureoSuite`). Yapı ve hijyen kuralları:
`../CureoHub/docs/reference/WORKSPACE.md`.

**Bir connector'ı değiştirirken hangi repo?**
- Tool davranışı, endpoint, auth, deploy → **CureoHub/mcp-servers/**
- Plugin'in o connector'ı hangi skill'de nasıl çağırdığı, `.mcp.json` wiring'i → **burası**
- `evidentia/self-host/` altındaki paketler istisnadır: bunlar bu depodan `wrangler deploy`
  edilen Worker'lardır. `RETIRED.md` taşıyan dizin **arşivdir** — canlı uç CureoHub'a
  taşınmıştır (`openalex-mcp`, `pubmed-mcp`, `semanticscholar-mcp`; 2026-08-17).

## Kalite Kapıları

Her push/PR'da CI'da koşar ([`.github/workflows/ci.yml`](.github/workflows/ci.yml));
commit öncesi elle koşun:

```bash
python3 tools/fleetkit/check_drift.py --all     # türetilmişlik · sürüm zinciri · sunucu kimliği
python3 tools/fleetkit/check_marketplace.py     # katalog ↔ disk bileşen sözleşmesi
```

| Kapı | Yakaladığı sınıf |
|---|---|
| `check_drift` | bayat türetilmiş dosya · sürüm zinciri tutarsızlığı · sapmış vendor'lı `fleet_probe` · çift `hooks.json` · düzyazıdaki filo sayısının yanlışlığı · filoda olmayan sunucu kimliğine atıf |
| `check_marketplace` | katalog ↔ disk uyuşmazlığı · skill/agent `name` ≠ dizin · eksik `description` · bilinmeyen hook olayı · var olmayan hook betiği · `CLAUDE_PLUGIN_ROOT` kullanmayan komut · `timeout` yok · hook betiğinde sözdizimi hatası |

İkisi ayrıdır çünkü `check_drift` yalnız *türetilen* şeyleri denetler; skill frontmatter'ı,
agent adı, hook betiği yolu **türetilmez** ve bozulduklarında hata da vermezler —
skill sessizce keşfedilemez, hook her oturumda sessizce düşer. `check_marketplace`
tam olarak bu *sessiz* sınıf içindir. CI kapılara kasıtlı kusur enjekte edip
yakaladıklarını da doğrular.

Canlı MCP sağlığı (`tools/fleetkit/audit_plugins.py`, gerçek `initialize` çağrıları)
**CI'da koşmaz** — Bearer anahtarı ister ve bir upstream arızası PR'ları bloke ederdi.
Elle koşulur.

## Katalog

10 plugin, `plugins/<ad>/` altında; katalog manifesti `.claude-plugin/marketplace.json`.

| Plugin | Alan |
|---|---|
| `evidentia` | PRISMA kanıt sentezi; 10 self-host connector `self-host/` altında |
| `cureolex` | Türkiye sağlık mevzuatı norm-üretimi (taslak · uyum · RIA · ex-post) |
| `vekayinuvis` | Osmanlı/Türk tarihi birincil-kaynak araştırması (BOA/BCA katalog + HTR) |
| `historia-medicinae` | Küresel tıp tarihi; anakronizm/presentizm/difüzyonizm denetimi |
| `rxpraxis` | Farmasötik pazar zekâsı ve jenerik/biyobenzer fırsat taraması |
| `sci-audit` | Bilimsel metin denetçisi (atıf-adli, yedi eksen) |
| `edupedia` | Maarif Modeli öğrenim modülü üreticisi |
| `brand-ecosystem-core` | Marka ekosistemi (isim · renk · tipografi · kültürel tarama) |
| `fon-uzmani` · `bist-analyst` | Finans (fon-mcp / Borsa MCP) |

Bileşen sayıları, dizin ağacı ve hızlı başlangıç için [`README.md`](README.md) —
sayılar diskten türetilir ve `marketplace.json` ile hizalı tutulur.

## Ortak Sözleşmeler

Araştırma/regülasyon plugin'leri (evidentia · cureolex · vekayinuvis ·
historia-medicinae · rxpraxis · sci-audit) aynı invariantları paylaşır. Yeni bir
skill yazarken bunları koru:

- **No-fabrication.** Native kaynakta veri yoksa çıktı "VERİ YOK"/`unverified` olur.
  Erişilemeyen yüzey deterministik `manual_required` zarfı döner — asla uydurulmaz.
  Boş sonuç yokluk kanıtı değildir.
- **Kapsam manifestosu (G0).** Her substantif çıktı hangi connector'ın çalıştığını /
  boş döndüğünü / degrade ettiğini **gerekçesiyle** beyan eder. Sessiz atlama = ihlal.
- **Retrieve-don't-dump.** Ağır çok-connector süpürmeler alt-ajanlara izole edilir;
  ana bağlama yalnız damıtılmış zarf döner. Büyük tam-metinler anamnesis'e ingest
  edilip sınırlı sorgulanır.
- **Degrade, çökme değil.** Eksik connector/anahtar çalışmayı durdurmaz; katman
  degrade eder ve bunu manifestoda beyan eder.
- **İnsan denetimi.** Hepsi karar-destektir — klinik tavsiye, resmî hukuki mütalaa
  veya yatırım danışmanlığı değildir.

## Konvansiyonlar

- Plugin bileşenleri konvansiyonel yollardan otomatik keşfedilir: `commands/`,
  `skills/<ad>/SKILL.md`, `agents/`, `hooks/hooks.json`, `.mcp.json`.
  `plugin.json`'da yol belirtmek yalnız istisna içindir.
- Komut ve hook betikleri **`${CLAUDE_PLUGIN_ROOT}`** ile adreslenir — mutlak yol
  taşınabilirliği bozar ve `check_marketplace` bunu reddeder. Her hook'a `timeout` verin.
- Skill/agent `name` frontmatter'ı dizin/dosya adıyla **birebir** eşleşmelidir.
- Sürüm üç yerde senkron: `plugins/<p>/.claude-plugin/plugin.json` ·
  `.claude-plugin/marketplace.json` · README tabloları. Aynı commit'te hizalayın.
- Yeni plugin eklerken README'deki katalog tablosu, bileşen envanteri, dizin ağacı ve
  hızlı başlangıç aynı commit'te güncellenir (sayılar diskten, sürüm plugin.json'dan).
- `shared/` ve `.claude/settings.local.json` gitignore'dadır — commit etmeyin.
- Kurulu plugin'ler `<plugin>@cureonics-marketplace` ile referanslanır; katalog **adı**
  repo adından (`CureoPrivate`) ayrıdır ve değişmez.
