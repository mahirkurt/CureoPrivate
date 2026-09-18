# edupedia

**TEDY edupedia ince istemcisi (1.0.0).** Türkiye Yüzyılı Maarif Modeli'ne hizalı, etkileşimli, tek dosyalık öğrenim modüllerini `tedy` MCP orkestratörüyle (https://mcp.tedy.online/mcp) üretir; modüller 18 kalite kapısından geçip tedy.online aile kataloğunda yayınlanır. Derin rehber, derleyici, kapılar ve katalog TED deposundaki `ted-mcp`'dedir.

## 1.0.0 — kırıcı değişiklik

- Yayın yolu değişti: çıktı yerel bir HTML dosyası değil, tedy.online kataloğundaki yayındır.
- Kaldırılanlar: yerel doğrulayıcı ve testleri, kalite denetçisi alt-ajanı, yazma sonrası doğrulama hook'u, yazım rehberi dosyaları, modül şablonu ve bunları taşıyan yerel skill. Tek kaynak artık TED `src/mcp_server/vendor/`.
- Eklenenler: `tedy` bağlayıcısı (interaktif OAuth), `edupedia` başlangıç skill'i, dört web yüzeyi paketi (`surfaces/`).
- Kalanlar: SessionStart preflight (yalnız `tedy`), beş komut, `start` skill'i; isteğe bağlı doğrudan `maarif-mufredat` ve `egitim-kaynak`.

## Kurulum

| Yüzey | Paket | Kurulum |
|---|---|---|
| Claude Code | bu plugin | `/plugin install edupedia@cureonics-marketplace` → `/mcp` → `tedy` → Authenticate |
| claude.ai | `surfaces/claude-ai/` (zip: `python3 plugins/edupedia/scripts/build_surfaces.py --zip`) | Skill yükle + custom connector |
| Codex | `surfaces/codex/` | skill + `tedy` MCP + OAuth girişi |
| Grok | `surfaces/grok/grok-workspace.md` | Workspace talimatı + Custom connector (ücretli plan) |
| Gemini Spark | `surfaces/gemini/gemini-gem.md` | Gem talimatı + Spark Connected Apps custom app |

Adım adım: [`KURULUM.md`](KURULUM.md) · claude.ai: [`CLAUDE-AI-KURULUM.md`](CLAUDE-AI-KURULUM.md) · bağlayıcılar ve geri-çağırma adresleri: [`CONNECTORS.md`](CONNECTORS.md).

## Komutlar

`/edupedia:modul` · `/edupedia:mufredat` · `/edupedia:kazanim-bul` · `/edupedia:soru` (EXAM, yayınlanmaz) · `/edupedia:durum`

## Yüzey paketleri nasıl güncellenir

`surfaces/bootstrap.md` tek kaynaktır (≤ 3.500 karakter). Düzenle → `python3 plugins/edupedia/scripts/build_surfaces.py` → türetilmiş dosyalar aynı commit'te. `python3 tools/fleetkit/check_drift.py --all` bayatlığı yakalar (`[7]`). Sürüm `fleet.yaml`'dan gelir; yayın için sürüm zinciri birlikte artırılır.

## Erişim

Yalnız TEDY aile listesindeki tam yetkili hesaplar. OAuth desteklemeyen bir istemci için kişi başı `tdyM_` anahtarı operatör tarafından TED'de üretilir; anahtar depoya ya da paylaşılan ortama yazılmaz.
