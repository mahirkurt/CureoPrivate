# edupedia — claude.ai kurulumu

claude.ai, edupedia'nın **asıl üretim yüzeyidir**: modül HTML'i dosyaya yazılmadan doğrudan
`edupedia_publish`'e üretilir ve tek adımda yayınlanır. Bu belge kurulumun tamamıdır.

> **Claude Code ile aynı şey değildir.** claude.ai'da **tek uzantı noktası Skill**'dir —
> hook, alt-ajan ve slash-komut YOKTUR (bkz. §4). Bu yüzden paket ayrı üretilir.

## 1. Ön koşul: plan

| Plan | Custom connector | edupedia çalışır mı |
|---|---|---|
| Free | **1 adet** | ✘ — edupedia **üç** connector ister |
| Pro / Max / Team / Enterprise | Çoklu | ✔ |

Skill yükleme her planda var; sınır **connector** tarafındadır. Team/Enterprise'da yönetici
connector'ları kurum genelinde açmalıdır.

## 2. Üç connector'ı ekle

**Settings → Customize → Connectors → "+"** (Skills'ten **ayrı** bir bölümdür).

| Sıra | Ad | URL | Kimlik doğrulama |
|---|---|---|---|
| 1 | `maarif-mufredat` | `https://mufredat.cureonics.com/mcp` | **Yok** (public read-only) |
| 2 | `egitim-kaynak` | `https://egitim-kaynak.cureonics.com/mcp` | **OAuth** (bağlan → izin ver; 2026-07-19 keyless→keyed) |
| 3 | `modul-yayin` | `https://edupedia.cureonics.com/mcp` | **OAuth** (bağlan → izin ver) |

**Sıra 2 ve 3 kimlik gerektirir** (OAuth) — Sıra 1 `maarif-mufredat` public'tir. Anahtarlar
OAuth akışında verilir; **sohbete asla yapıştırmayın** — connector ayarlarında kalır.
(`egitim-kaynak` 2026-07-19'da keyless→keyed geçti; plugin-dışı Gemini/ChatGPT standalone için.)

> **Connector listesinde görünen adlar:** `egitim-kaynak` → **"Eğitim Kaynakları"**,
> `modul-yayin` → **"Modül Yayını"** (sunucunun `serverInfo.name`'i). `.mcp.json`'daki iç
> anahtarlar (`egitim-kaynak`/`modul-yayin`) değişmedi — komut/skill referansları aynı.

> Adlar `CONNECTORS.md` (normatif envanter) ile aynıdır. Sıra 3'ün **eski adı `edupedia`
> idi**; plugin adıyla çakışmasın diye `modul-yayin`'e alındı — endpoint ve token aynı.

> **Bir Skill connector talep EDEMEZ.** claude.ai'da Skill↔Connector bağımlılık mekanizması
> yoktur; üçünü de elle eklemek zorundasınız. Eksik connector üretimi **bloke etmez** —
> skill dürüstçe degrade eder (asla uydurma kaynak), ama yeteneği düşer:
> - `maarif-mufredat` yoksa → müfredat/ders kitabı/figür **yok**; yalnız serbest-kaynak modu
> - `egitim-kaynak` yoksa → PhET simülasyonu ve ek örnek yok (zenginleştirme atlanır)
> - `modul-yayin` yoksa → yayın yok; modül sohbette artefakt olarak kalır

## 3. Skill'i yükle

```bash
python3 plugins/edupedia/scripts/build_claude_ai_skill.py
# → plugins/edupedia/dist/carbon-edupedia-claude-ai.zip  (279 KB)
```

**Settings → Customize → Skills → Upload** → zip'i seç.

Script paketi üretmeden önce claude.ai spec'ini **ölçer** (name ≤64 + küçük-harf/tire +
rezerve-kelime yok; description ≤1024 + XML yok; zip klasör-kökte; ≤30 MB) ve ihlalde
**durur** — bozuk paket üretmez.

**Vendor + kırık-bağlantı kapısı (2026-07-17).** Skill, plugin düzeninde `../../../CONNECTORS.md`
gibi **paket-dışı** yollara referans verir. Bu yollar Claude Code'da doğrudur (plugin ağacı
oradadır) ama zip'in kökü `carbon-edupedia/` olduğu için claude.ai'da hepsi **kırık bağlantıya**
dönüşürdü — üstelik biri connector envanterinin "tek doğruluk kaynağı" ilan edilen
`CONNECTORS.md`'ydi. Kaynak yanlış değildi, **paketleyici eksikti.** Artık script dört normatif
belgeyi `plugin-context/`e taşır ve bağlantıları derinlik-duyarlı yeniden yazar:

| Kaynak (plugin) | Pakette |
|---|---|
| `CONNECTORS.md` | `plugin-context/CONNECTORS.md` |
| `shared/canonical-cache-contract.md` | `plugin-context/canonical-cache-contract.md` |
| `shared/run-manifest-schema.json` | `plugin-context/run-manifest-schema.json` |
| `docs/mcp-introspection-2026-07-06.json` | `plugin-context/…` (denetlenebilirlik kanıtı) |

`commands/*.md` **vendor'lanmaz** — claude.ai'da komut yoktur; o bağlantılar taşıdıkları tek
anlam olan komut **adına** indirgenir (`../commands/yayinla.md` → `/edupedia:yayinla`). Kapı
paketi kurduktan sonra **zip'in içinden** ölçer: kaçan her bağlantı zip üyesi olmak zorundadır,
değilse build **durur**. Niyeti değil artefaktı ölçtüğü için yeni bir paket-dışı referans
sessizce sızamaz.

Paket `tests/`, `docs/`, `evals/` ve cache'leri **dışlar** (~670 KB geliştirme yükü).
`scripts/` dâhildir: kod-çalıştırma açıksa `validate_module.py` yerel ön-kontrol olarak
koşar. Koşmasa da üretim çalışır — **kapıların otoritesi zaten sunucudur**.

## 4. Ne geçer, ne geçmez (dürüst harita)

| Plugin bileşeni | claude.ai'da | Nasıl karşılanıyor |
|---|---|---|
| `carbon-edupedia` skill | ✔ Skill | Paketin kendisi; **kendi başına yeterli** |
| `CONNECTORS.md` + `shared/*` | ✔ vendor | `plugin-context/`e taşınır, bağlantılar yeniden yazılır (§3) — eskiden kırık bağlantıydı |
| 3 MCP connector | ✔ Connector | §2'de elle eklenir |
| `commands/modul`·`mufredat` | ✘ komut yok | Akış **skill'in içinde**: `references/curriculum-integration.md §3` (sözleşmenin tek kaynağı) |
| `commands/yayinla` | ✘ komut yok | SKILL.md §8 Adım 6: HTML doğrudan `edupedia_publish`'e |
| `commands/durum` | ✘ komut yok | **Karşılığı yok — bilerek.** Bağlı connector'ları claude.ai'ın kendisi gösterir (Settings → Connectors); skill `server_info`'yu yalnız **provenans/korpus sürümü** için çağırır, sağlık yoklaması için değil |
| `commands/kazanim-bul` | ✘ komut yok | "Bu konuya hangi kazanımlar denk geliyor?" diye sorun |
| `agents/module-auditor` | ✘ alt-ajan yok | Denetim skill'in kendi akışında (§3 Adım 5.5 + G-VERIFY) |
| `hooks/preflight` | ✘ hook yok | **Büyük ölçüde gereksiz:** hook'un asıl işi çözülmeyen `${EDUPEDIA_PUBLISH_TOKEN}` uyarısıydı — claude.ai'da token OAuth'tan gelir, o arıza **sınıfı yok**. Connector eksikliği üretimi bloke etmez: skill MCP'ye ulaşamayınca dürüstçe degrade eder (SKILL.md §8 Adım 0.5). Envanterin normatif metni pakette: `plugin-context/CONNECTORS.md` |
| `hooks/validate-module` | ✘ hook yok | **Gerek yok** — yayında kapıları sunucu ölçer (14 kapı, 422) |
| `start` skill | ✘ paketlenmez | Görevi komutlara yönlendirmekti; claude.ai'da komut yok → anlamsız, üstelik "start" adı yanlış-tetikleme mıknatısı |

## 5. Skill nasıl tetiklenir

claude.ai'da **`/skill-adı` çağrısı YOKTUR.** Claude skill'i **yalnız `description`
alanından** seçer. Yani şöyle konuşun:

- "5. sınıf fen, elektrik devresi konusunda etkileşimli bir modül hazırla"
- "FB.5.6.1.1 kazanımından DEHB-dostu bir öğrenim modülü üret"
- "Bu konuya hangi MEB kazanımları denk geliyor?"

Tetiklenmezse sorun büyük olasılıkla description'dadır — skill'i yeniden yükleyin.

## 6. Sözleşme claude.ai'da da geçerlidir

Üretim şu kapılara tabidir (kullanıcı sözleşmesi, 2026-07-17):

1. **Sınıf + ders kesinleşmeden üretim başlamaz** — koddan çıkarılmaz, MCP'den doğrulanır;
   yoksa **sorulur**.
2. **Çerçeveyi ders kitabı çizer** — `get_document_text` ile açılır (105 kitabın 103'ü tam
   metin). Çerçeve dışı içerik üretilmez; doğru olması yetmez.
3. **Kitabın kendi figürleri önceliklidir**; yazar-üretimi SVG yedektir.
4. **Denetimsiz yayın yok** — her olgusal iddia `verification` bloğunda dayanağıyla kayıtlı.

Son kapı **sunucudadır ve pazarlığa kapalıdır**: `edupedia_publish` HTML'i kendisi ölçer
(14 kapı), istemcinin beyanını **yok sayar**, düşerse **422** döner ve hangi kapıların
düştüğünü söyler. `force=true` bir kaçış değil, işaretli bir istisnadır.
