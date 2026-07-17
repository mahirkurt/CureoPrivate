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
| 2 | `egitim-kaynak` | `https://egitim-kaynak.cureonics.com/mcp` | **Yok — anahtarsız** (salt-okunur, korpus açık lisanslı) |
| 3 | `edupedia` | `https://edupedia.cureonics.com/mcp` | **OAuth** (bağlan → izin ver) |

**Sıra 3 tek kimlik-gerektiren connector'dır.** Yayın token'ı OAuth akışında verilir;
**sohbete asla yapıştırmayın** — connector ayarlarında kalır.

> **Bir Skill connector talep EDEMEZ.** claude.ai'da Skill↔Connector bağımlılık mekanizması
> yoktur; üçünü de elle eklemek zorundasınız. Eksik connector üretimi **bloke etmez** —
> skill dürüstçe degrade eder (asla uydurma kaynak), ama yeteneği düşer:
> - `maarif-mufredat` yoksa → müfredat/ders kitabı/figür **yok**; yalnız serbest-kaynak modu
> - `egitim-kaynak` yoksa → PhET simülasyonu ve ek örnek yok (zenginleştirme atlanır)
> - `edupedia` yoksa → yayın yok; modül sohbette artefakt olarak kalır

## 3. Skill'i yükle

```bash
python3 plugins/edupedia/scripts/build_claude_ai_skill.py
# → plugins/edupedia/dist/carbon-edupedia-claude-ai.zip  (259 KB)
```

**Settings → Customize → Skills → Upload** → zip'i seç.

Script paketi üretmeden önce claude.ai spec'ini **ölçer** (name ≤64 + küçük-harf/tire +
rezerve-kelime yok; description ≤1024 + XML yok; zip klasör-kökte; ≤30 MB) ve ihlalde
**durur** — bozuk paket üretmez.

Paket `tests/`, `docs/`, `evals/` ve cache'leri **dışlar** (~670 KB geliştirme yükü).
`scripts/` dâhildir: kod-çalıştırma açıksa `validate_module.py` yerel ön-kontrol olarak
koşar. Koşmasa da üretim çalışır — **kapıların otoritesi zaten sunucudur**.

## 4. Ne geçer, ne geçmez (dürüst harita)

| Plugin bileşeni | claude.ai'da | Nasıl karşılanıyor |
|---|---|---|
| `carbon-edupedia` skill | ✔ Skill | Paketin kendisi; **kendi başına yeterli** |
| 3 MCP connector | ✔ Connector | §2'de elle eklenir |
| `commands/modul`·`mufredat` | ✘ komut yok | Akış **skill'in içinde**: `references/curriculum-integration.md §3` (sözleşmenin tek kaynağı) |
| `commands/yayinla` | ✘ komut yok | SKILL.md §8 Adım 6: HTML doğrudan `edupedia_publish`'e |
| `commands/durum` | ✘ komut yok | "Connector'larım bağlı mı?" diye sorun; skill `server_info`/`kb_server_info` çağırır |
| `commands/kazanim-bul` | ✘ komut yok | "Bu konuya hangi kazanımlar denk geliyor?" diye sorun |
| `agents/module-auditor` | ✘ alt-ajan yok | Denetim skill'in kendi akışında (§3 Adım 5.5 + G-VERIFY) |
| `hooks/preflight` | ✘ hook yok | Connector envanteri skill'in Adım 0'ında |
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
