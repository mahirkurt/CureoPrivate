# edupedia — Çok Platformlu Kurulum ve Entegrasyon Kılavuzu

Bu belge `edupedia` eklentisinin tüm desteklenen LLM platformlarında (**Claude Code**, **claude.ai**, **Cursor IDE**, **ChatGPT / OpenAI Codex**, **Google Gemini / AI Studio**, **VS Code / Roo Code / Cline / Windsurf / Claude Desktop**) kurulumunu, MCP bağlayıcılarının yapılandırmasını ve kimlik doğrulama modellerini açıklar.

---

## 1. Mimari ve Konnektör Envanteri

Edupedia süiti, iki tamamlayıcı MCP sunucusu üzerinde çalışır:

| Konnektör Adı | Sunucu URL | Araç Sayısı | Rol / Görev | Kimlik Doğrulama | Doppler Değişkeni |
|---|---|:---:|---|---|---|
| **`maarif-mufredat`** | `https://mufredat.cureonics.com/mcp` | 21 | **OTORİTE KAYNAĞI** — 105 MEB ders kitabı tam metni, 10.855 kazanım, 22.414 ders kitabı figürü, 13 çerçeve (266 madde). | OAuth 2.1 / Bearer | `MUFREDAT_MCP_API_KEY` |
| **`egitim-kaynak`** | `https://egitim-kaynak.cureonics.com/mcp` | 6 | **OER RAG ZENGİNLEŞTİRME** — 124 doğrulanmış müfredat kategorisi (3.828 sayfa), PhET 175 Türkçe simülasyon (CC BY-NC 4.0). Display: *"Eğitim Kaynakları"*. | OAuth 2.1 / Bearer | `EGITIM_KAYNAK_MCP_API_KEY` |

> 🔒 **GÜVENLİK İLKESİ:** Canlı anahtar değerleri hiçbir dokümantasyonda veya repoda düz metin olarak saklanmaz. Değerlerin tek merkezi kaynağı Doppler'dır (`cureohub` / `dev_personal`).

---

## 2. Platform Bazında Kurulum Yolları

### Platform A · Claude Code (CLI / Terminal)

Claude Code ortamında plugin ve konnektörler `.mcp.json` ve `.claude-plugin/plugin.json` üzerinden otomatik devreye girer.

1. **Doppler ile Başlatma (Önerilen)**:
   ```bash
   doppler run -p cureohub -c dev_personal -- claude
   ```
   *Doppler tüm `${MUFREDAT_MCP_API_KEY}` ve `${EGITIM_KAYNAK_MCP_API_KEY}` değişkenlerini süreç ortamına enjekte eder; `.mcp.json` bunları otomatik çözer.*

2. **Manuel Ortam Değişkeni ile Başlatma**:
   ```bash
   export MUFREDAT_MCP_API_KEY="<anahtar>"
   export EGITIM_KAYNAK_MCP_API_KEY="<anahtar>"
   claude
   ```

3. **Mevcut Yetenekler**:
   - Komutlar: `/edupedia:modul`, `/edupedia:mufredat`, `/edupedia:soru`, `/edupedia:kazanim-bul`, `/edupedia:durum`
   - Kancalar (Hooks): `SessionStart` (oturum açılışında 24h önbellekli canlı MCP probu + konvansiyon enjeksiyonu) ve `PostToolUse` (HTML modül yazıldığında 16 kalite kapısı denetimi).
   - Alt-Ajan: `module-auditor` (4 eksenli QA denetimi).

---

### Platform B · claude.ai (Web & Desktop)

claude.ai ortamında tek uzantı noktası **Skill** ve **Custom Connectors** arayüzüdür (hook, alt-ajan ve slash-komutlar bu arayüzde bulunmaz).

1. **Custom Connectors Ekleme**:
   - **Settings → Customize → Connectors → "+"**:
     - 1. Konnektör: `https://mufredat.cureonics.com/mcp` (OAuth / Bearer)
     - 2. Konnektör: `https://egitim-kaynak.cureonics.com/mcp` (OAuth / Bearer)
   - *Not: Açılan yetkilendirme ekranında ilgili anahtarları girin. Sohbete asla anahtar yapıştırmayın.*

2. **Skill Paketini Yükleme**:
   ```bash
   # Skill paketini derleyin:
   python3 plugins/edupedia/scripts/build_claude_ai_skill.py
   # Çıktı: plugins/edupedia/dist/carbon-edupedia-claude-ai.zip
   ```
   - **Settings → Customize → Skills → Upload** adımlarını izleyerek `carbon-edupedia-claude-ai.zip` dosyasını yükleyin.

3. **Kullanım & Tetikleme**:
   - Doğal dille talimat verin (örn: *"5. sınıf fen, elektrik devresi konusunda etkileşimli bir modül hazırla"* veya *"FB.5.3.1.1 kazanımından DEHB-dostu bir modül üret"*).
   - Çıktı doğrudan sohbet içi interaktif HTML artefaktı olarak teslim edilir.

---

### Platform C · Cursor IDE (Composer & Agent Mode)

Cursor IDE içinde Edupedia hem plugin mimarisiyle (`.cursor-plugin/`) hem de MCP entegrasyonuyla tam uyumludur.

1. **Cursor MCP Yapılandırması**:
   - **Cursor Settings → Features → MCP Servers** altına ekleyin veya workspace kökünüzdeki `.cursor/mcp.json` dosyasına ekleyin:

```json
{
  "mcpServers": {
    "maarif-mufredat": {
      "url": "https://mufredat.cureonics.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MUFREDAT_MCP_API_KEY"
      }
    },
    "egitim-kaynak": {
      "url": "https://egitim-kaynak.cureonics.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_EGITIM_KAYNAK_MCP_API_KEY"
      }
    }
  }
}
```

2. **Kullanım**:
   - Cursor Agent / Composer modunda `@edupedia` veya ilgili komut ve skill yönergeleriyle tam etkileşimli çalışır.

---

### Platform D · ChatGPT / OpenAI Codex / Custom GPTs

ChatGPT (Plus, Team, Enterprise, Edu) ve OpenAI Codex ortamlarında MCP konnektörleri **Developer Mode** ve OAuth 2.1 RFC 9728 uyumuyla doğrudan bağlanabilir.

1. **ChatGPT Developer Mode Custom Connector Bağlantısı**:
   - **Settings → Connectors → Add Custom Connector**:
     - `maarif-mufredat`: `https://mufredat.cureonics.com/mcp`
     - `egitim-kaynak`: `https://egitim-kaynak.cureonics.com/mcp`
   - Kimlik doğrulama türü olarak **OAuth** seçin. Sunucular RFC 9728 Protected Resource Metadata (PRM) ve PKCE S256 ile tam uyumludur; açılan login formuna Doppler'dan aldığınız anahtarı girin.

2. **Custom GPT Yapılandırması**:
   - **Name**: Edupedia MEB Öğrenim Modülü Üreticisi
   - **Instructions**: `skills/carbon-edupedia/SKILL.md` ve `.codex-plugin/openai.yaml` içeriğini talimat olarak ekleyin.

---

### Platform E · Google Gemini / Google AI Studio / Spark

Google ekosistemi Streamable HTTP MCP protokolünü ve OAuth 2.1 akışını destekler.

1. **OAuth İzin Listesi Doğrulaması**:
   - Her iki MCP sunucusu da Google'ın resmî OAuth redirect broker'ı olan `https://oauth-redirect.googleusercontent.com` adresini varsayılan olarak destekler.
2. **Konnektör Tanımı**:
   - Endpoint URL'leri: `https://mufredat.cureonics.com/mcp` ve `https://egitim-kaynak.cureonics.com/mcp`.

---

### Platform F · VS Code / Roo Code / Cline / Windsurf / Claude Desktop

Standart MCP istemcisi barındıran tüm editör ve araçlar için evrensel JSON yapılandırması:

#### `claude_desktop_config.json` / `cline_mcp_settings.json` / `roo_code_mcp_settings.json`:

```json
{
  "mcpServers": {
    "maarif-mufredat": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mufredat.cureonics.com/mcp",
        "--header",
        "Authorization: Bearer ${MUFREDAT_MCP_API_KEY}"
      ]
    },
    "egitim-kaynak": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://egitim-kaynak.cureonics.com/mcp",
        "--header",
        "Authorization: Bearer ${EGITIM_KAYNAK_MCP_API_KEY}"
      ]
    }
  }
}
```

*Veya doğrudan Streamable HTTP destekleyen istemciler için (`Windsurf` / `Cursor` / `VS Code Native MCP`):*

```json
{
  "mcpServers": {
    "maarif-mufredat": {
      "type": "http",
      "url": "https://mufredat.cureonics.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MUFREDAT_MCP_API_KEY"
      }
    },
    "egitim-kaynak": {
      "type": "http",
      "url": "https://egitim-kaynak.cureonics.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_EGITIM_KAYNAK_MCP_API_KEY"
      }
    }
  }
}
```

---

## 3. Platformlar Arası Yetenek ve Uyumluluk Matrisi

| Yetenek / Bileşen | Claude Code (CLI) | claude.ai (Web) | Cursor IDE | ChatGPT / OpenAI | Gemini | VS Code / Roo / Cline |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **carbon-edupedia (Flagship Skill)** | ✅ Tam | ✅ Tam | ✅ Tam | ✅ Tam | ✅ Tam | ✅ Tam |
| **16 Kalite Kapısı (`validate_module.py`)** | ✅ Otomatik (Hook) | ⚠️ Kod Çalıştırma ile | ✅ Terminal / Python | ⚠️ Sandboxed | ⚠️ Manuel | ✅ Terminal / Task |
| **Müfredat MCP (`maarif-mufredat` - 21 Araç)** | ✅ Paketli | ✅ Connector | ✅ MCP Server | ✅ OAuth Conn | ✅ MCP | ✅ Remote MCP |
| **Eğitim Kaynak MCP (`egitim-kaynak` - 6 Araç)** | ✅ Paketli | ✅ Connector | ✅ MCP Server | ✅ OAuth Conn | ✅ MCP | ✅ Remote MCP |
| **module-auditor QA Alt-Ajanı** | ✅ Alt-Ajan | ❌ (Skill içi denetim) | ✅ Agent Modu | ❌ (Prompt içi) | ❌ | ✅ Sub-agent |
| **Kancalar (SessionStart & PostToolUse)** | ✅ Aktif | ❌ Desteklenmez | ❌ (Terminal script) | ❌ | ❌ | ❌ |
| **Komutlar (`/edupedia:*`)** | ✅ Slash Komut | ❌ (Doğal Dil) | ✅ Slash / Prompt | ❌ (Doğal Dil) | ❌ | ❌ (Custom prompt) |
| **Tier-1 SVG Üretimi** | ✅ Garantili | ✅ Garantili | ✅ Garantili | ✅ Garantili | ✅ Garantili | ✅ Garantili |
| **Tier-2 Görsel Gömme (`fetch_figure.py`)** | ✅ Tam | ⚠️ Metadata / SVG | ✅ Tam | ⚠️ Metadata | ⚠️ | ✅ Tam |

---

## 4. Sorun Giderme ve Teşhis

- **401 Unauthorized Hatası**: Anahtarın eksik veya süresinin dolduğunu gösterir. Claude Code için Doppler üzerinden oturum açın; web platformlarında (claude.ai, ChatGPT) connector OAuth formuna anahtarı yeniden girin.
- **Konnektör Sağlık Kontrolü**:
  - Claude Code: `/edupedia:durum`
  - CLI Testi: `python3 hooks/scripts/fleet_probe.py --fresh`
  - Unit Testleri: `python3 hooks/test_hooks.py`
