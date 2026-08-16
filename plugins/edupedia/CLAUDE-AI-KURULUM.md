# edupedia — claude.ai kurulumu

claude.ai, edupedia'nın üretim yüzeylerinden biridir: modül HTML'i sohbet artefaktı olarak
sunulur. Plugin yayınlamaz. Bu belge kurulumun tamamıdır.

> **Claude Code ile aynı şey değildir.** claude.ai'da **tek uzantı noktası Skill**'dir —
> hook, alt-ajan ve slash-komut YOKTUR (bkz. §4). Bu yüzden paket ayrı üretilir.

## 1. Ön koşul: plan

| Plan | Custom connector | edupedia çalışır mı |
|---|---|---|
| Free | **1 adet** | ✘ — edupedia **iki** connector ister |
| Pro / Max / Team / Enterprise | Çoklu | ✔ |

Skill yükleme her planda var; sınır **connector** tarafındadır. Team/Enterprise'da yönetici
connector'ları kurum genelinde açmalıdır.

## 2. İki connector'ı ekle

**Settings → Customize → Connectors → "+"** (Skills'ten **ayrı** bir bölümdür).

| Sıra | Ad | URL | Kimlik doğrulama |
|---|---|---|---|
| 1 | `maarif-mufredat` | `https://mufredat.cureonics.com/mcp` | **OAuth / Bearer** |
| 2 | `egitim-kaynak` | `https://egitim-kaynak.cureonics.com/mcp` | **OAuth** (bağlan → izin ver) |

Anahtarlar OAuth akışında verilir; **sohbete asla yapıştırmayın** — connector ayarlarında kalır.

> **Connector listesinde görünen ad:** `egitim-kaynak` → **"Eğitim Kaynakları"**
> (sunucunun `serverInfo.name`'i).

> **Bir Skill connector talep EDEMEZ.** claude.ai'da Skill↔Connector bağımlılık mekanizması
> yoktur; ikisini de elle eklemek zorundasınız. Eksik connector üretimi **bloke etmez** —
> skill dürüstçe degrade eder (asla uydurma kaynak), ama yeteneği düşer:
> - `maarif-mufredat` yoksa → müfredat/ders kitabı/figür **yok**; yalnız serbest-kaynak modu
> - `egitim-kaynak` yoksa → PhET simülasyonu ve ek örnek yok (zenginleştirme atlanır)

## 3. Skill'i yükle

```bash
python3 plugins/edupedia/scripts/build_claude_ai_skill.py
# → plugins/edupedia/dist/carbon-edupedia-claude-ai.zip
```

**Settings → Customize → Skills → Upload** → zip'i seç.

Script paketi üretmeden önce claude.ai spec'ini **ölçer** (name ≤64 + küçük-harf/tire +
rezerve-kelime yok; description ≤1024 + XML yok; zip klasör-kökte; ≤30 MB) ve ihlalde
**durur** — bozuk paket üretmez.

**Vendor + kırık-bağlantı kapısı.** Skill, plugin düzeninde `../../../CONNECTORS.md`
gibi **paket-dışı** yollara referans verir. Bu yollar Claude Code'da doğrudur (plugin ağacı
oradadır) ama zip'in kökü `carbon-edupedia/` olduğu için claude.ai'da hepsi **kırık bağlantıya**
dönüşürdü. Artık script dört normatif belgeyi `plugin-context/`e taşır ve bağlantıları
derinlik-duyarlı yeniden yazar:

| Kaynak (plugin) | Pakette |
|---|---|
| `CONNECTORS.md` | `plugin-context/CONNECTORS.md` |
| `shared/canonical-cache-contract.md` | `plugin-context/canonical-cache-contract.md` |
| `shared/run-manifest-schema.json` | `plugin-context/run-manifest-schema.json` |
| `docs/mcp-introspection-2026-07-06.json` | `plugin-context/…` (denetlenebilirlik kanıtı) |

`commands/*.md` **vendor'lanmaz** — claude.ai'da komut yoktur. Kapı paketi kurduktan sonra
**zip'in içinden** ölçer: kaçan her bağlantı zip üyesi olmak zorundadır, değilse build **durur**.

Paket `tests/`, `docs/`, `evals/` ve cache'leri **dışlar**. `scripts/` dâhildir: kod-çalıştırma
açıksa `validate_module.py` kalite kapısı olarak koşar. Koşmuyorsa kapıları "PASS" diye
beyan etmeyin — ölçülmemiş kapı ölçülmemiştir.

## 4. Ne geçer, ne geçmez (dürüst harita)

| Plugin bileşeni | claude.ai'da | Nasıl karşılanıyor |
|---|---|---|
| `carbon-edupedia` skill | ✔ Skill | Paketin kendisi; **kendi başına yeterli** |
| `CONNECTORS.md` + `shared/*` | ✔ vendor | `plugin-context/`e taşınır, bağlantılar yeniden yazılır (§3) |
| 2 MCP connector | ✔ Connector | §2'de elle eklenir |
| `commands/modul`·`mufredat` | ✘ komut yok | Akış **skill'in içinde**: `references/curriculum-integration.md §3` |
| `commands/durum` | ✘ komut yok | Bağlı connector'ları claude.ai'ın kendisi gösterir (Settings → Connectors) |
| `commands/kazanim-bul` | ✘ komut yok | "Bu konuya hangi MEB kazanımları denk geliyor?" diye sorun |
| `agents/module-auditor` | ✘ alt-ajan yok | Denetim skill'in kendi akışında (§3 Adım 5.5 + G-VERIFY) |
| `hooks/*` | ✘ hook yok | Connector eksikliği üretimi bloke etmez (SKILL.md §8 Adım 0.5) |
| `start` skill | ✘ paketlenmez | Görevi komutlara yönlendirmekti; claude.ai'da komut yok |

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
4. **Her olgusal iddia `verification` bloğunda dayanağıyla kayıtlıdır.**

Teslim sohbet artefaktıdır. Plugin siteye yayınlamaz. Kalite kapısı yerel
`validate_module.py`'dir (kod-çalıştırma açıksa).
