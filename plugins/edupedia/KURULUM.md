# edupedia 1.0.0 — Kurulum

Her yüzey aynı başlangıç talimatını (`surfaces/bootstrap.md`'den üretilir) ve aynı `tedy` bağlayıcısını kullanır: `https://mcp.tedy.online/mcp`. Bağlanabilen hesaplar TEDY aile listesindeki tam yetkili Google hesaplarıdır. OAuth sırasında Google girişinden sonra açılan onay sayfası istemci adını ve tam geri-çağırma adresini gösterir; adres [`CONNECTORS.md`](CONNECTORS.md)'deki beklenen adresle aynıysa "Onayla", değilse "Reddet".

## Claude Code

1. `/plugin marketplace add mahirkurt/CureoPrivate` (bir kez) → `/plugin install edupedia@cureonics-marketplace` → Claude Code'u yeniden başlatın.
2. `/mcp` → `tedy` → **Authenticate** → tarayıcıda Google girişi → onay sayfası (geri-çağırma `http://localhost:<port>/…`) → Onayla.
3. `/edupedia:durum`.

Güncelleme: `/plugin marketplace update cureonics-marketplace` ve `/plugin update edupedia@cureonics-marketplace`. Kurulu kopya sürüm anahtarlıdır; sürüm değişmeden güncellenmez.

## claude.ai

[`CLAUDE-AI-KURULUM.md`](CLAUDE-AI-KURULUM.md).

## Codex

1. Talimat: `surfaces/codex/skills/edupedia/SKILL.md` → `~/.codex/skills/edupedia/SKILL.md`. Codex'iniz yoldan plugin kurulumunu destekliyorsa `surfaces/codex/` dizinini plugin olarak da kurabilirsiniz; `.codex-plugin/plugin.json` aynı bağlayıcıyı taşır.
2. Bağlayıcı — `~/.codex/config.toml`:

   ```toml
   [mcp_servers.tedy]
   enabled = true
   url = "https://mcp.tedy.online/mcp"
   ```

3. OAuth: `codex mcp login tedy` (sürümünüzde farklıysa `codex mcp --help`). Geri-çağırma yerel loopback'tir; Codex'i tarayıcının açıldığı makinede çalıştırın (uzak makinede VS Code masaüstünün port yönlendirmesi gerekir).

## Grok (özel bağlayıcı ücretli plan ister)

1. Bir proje/workspace oluşturun; talimat alanına `surfaces/grok/grok-workspace.md` içeriğini yapıştırın (≤ 4.000 karakter).
2. grok.com → Connectors → Custom → URL `https://mcp.tedy.online/mcp` → bağlan → Google girişi → onay sayfasında `https://grok.com/…` geri-çağırması → Onayla.

## Gemini Spark

1. Gemini → Gems → yeni Gem "TEDY edupedia" → talimat: `surfaces/gemini/gemini-gem.md`.
2. Spark → Connected Apps → custom app → MCP URL `https://mcp.tedy.online/mcp` → Google girişi → onay sayfasında `https://oauth-redirect.googleusercontent.com/r/user_bound_custom-mcp-…-mcp_tedy_online` geri-çağırması → Onayla.

## Cursor

Marketplace ya da GitHub plugin'i olarak kurulur; `tedy` bağlayıcısı `.cursor-plugin/mcp.json`'dan gelir, OAuth Cursor'ın MCP ayarlarından tamamlanır.

## Sorun giderme

| Belirti | Neden ve çözüm |
|---|---|
| `tedy` araçları görünmüyor | OAuth tamamlanmadı; bağlayıcıyı yeniden bağlayın. |
| Google girişinden sonra "onaylayamaz" | Hesap aile listesinde tam yetkili değil. |
| Bağlantı geri-çağırma hatasıyla düşüyor | Yüzeyin geri-çağırma adresi izin listesinde yok; operatöre bildirin (sunucu kaydı `oauth_redirect_reddedildi`). |
| "Onayla"dan sonra sayfa ilerlemiyor | Tarayıcı Console'da `form-action` CSP ihlali varsa operatöre bildirin (geri-çağırma sayfası başka bir origin'e yönleniyor). |
| `/edupedia:durum` erişilemedi diyor | `https://mcp.tedy.online/health` yanıt vermiyor; operatöre bildirin. |
