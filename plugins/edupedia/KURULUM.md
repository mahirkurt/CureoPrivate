# edupedia — Çok Platformlu Kurulum ve Entegrasyon Kılavuzu

Bu belge `edupedia` eklentisinin **Claude Code**, **claude.ai**, **Cursor IDE**,
**ChatGPT / OpenAI Codex**, **Google Gemini / AI Studio** ve
**VS Code / Roo Code / Cline / Windsurf / Claude Desktop** üzerindeki farklı destek
düzeylerini, MCP bağlayıcılarının yapılandırmasını ve kimlik doğrulama modellerini açıklar.
Bir hostun skill metnini veya MCP'yi kullanabilmesi, native plugin otomasyonuna sahip olduğu
anlamına gelmez.

---

## 1. Mimari ve Konnektör Envanteri

Edupedia süiti, iki tamamlayıcı MCP sunucusu üzerinde çalışır:

| Konnektör Adı | Sunucu URL | Araç Sayısı | Rol / Görev | Kimlik Doğrulama | Doppler Değişkeni |
|---|---|:---:|---|---|---|
| **`maarif-mufredat`** | `https://mufredat.cureonics.com/mcp` | 21 | **OTORİTE KAYNAĞI** — 105 MEB ders kitabı tam metni, 10.855 kazanım, 22.414 ders kitabı figürü, 13 çerçeve (266 madde). | OAuth 2.1 / Bearer | `MUFREDAT_MCP_API_KEY` |
| **`egitim-kaynak`** | `https://egitim-kaynak.cureonics.com/mcp` | 6 | **OER RAG ZENGİNLEŞTİRME** — 124 doğrulanmış müfredat kategorisi (3.828 sayfa), PhET 175 Türkçe simülasyon (CC BY-NC 4.0). Display: *"Eğitim Kaynakları"*. | OAuth 2.1 / Bearer | `EGITIM_KAYNAK_MCP_API_KEY` |

> 🔒 **GÜVENLİK İLKESİ:** Canlı anahtar değerleri hiçbir dokümantasyonda veya repoda düz
> metin olarak saklanmaz. Değerlerin tek merkezi kaynağı Doppler'dır
> (`cureohub` / `dev_personal`). Statik Bearer bağlantısı API anahtarını doğrudan
> kullanabilir; OAuth authorization code ve access token opaque değerlerdir, API anahtarının
> kendisi değildir.

---

## 2. Platform Bazında Kurulum Yolları

Üç destek düzeyi kullanılır:

1. **Native plugin otomasyonu:** Claude Code ve Cursor — komut, platforma özgü hook,
   `module-auditor`, yerel `validate_module.py` ve `fetch_figure.py`.
2. **Authenticated MCP:** Host Streamable HTTP MCP/Custom Connector destekliyorsa
   `maarif-mufredat` + anahtarlı `egitim-kaynak` OAuth/Bearer bağlantısı.
3. **Prompt uyarlaması:** `SKILL.md`/skill metni talimat olarak verilir; komut, hook,
   alt-ajan ve otomatik Tier-2b paritesi yoktur.

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

Cursor IDE, Claude Code ile birlikte **native plugin otomasyonu** sunan ikinci yüzeydir.
`.cursor-plugin/plugin.json`, Claude hook manifestini değil Cursor'a özgü
`hooks/hooks-cursor.json` dosyasını bildirir. Komutlar, `module-auditor`, Cursor
`sessionStart`/`postToolUse` hook'ları ve yerel Python scriptleri bu yüzeyde kullanılabilir.

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
   - Cursor Agent / Composer modunda `@edupedia` veya ilgili komut ve skill yönergelerini
     kullanın. Native otomasyon yalnız plugin yüklüyse geçerlidir; yalnız MCP kaydı eklemek
     komut/hook/alt-ajan kurmaz.

---

### Platform D · ChatGPT / OpenAI Codex / Custom GPTs

Bu yüzeylerde Edupedia **prompt uyarlaması** olarak kullanılır. Host/hesap gerçekten
Developer Mode Custom Connector sunuyorsa iki MCP ayrıca OAuth ile bağlanabilir; bu bağlantı
Claude Code/Cursor komut, hook, alt-ajan veya yerel script otomasyonunu taşımaz.

1. **ChatGPT Developer Mode Custom Connector Bağlantısı**:
   - **Settings → Connectors → Add Custom Connector**:
     - `maarif-mufredat`: `https://mufredat.cureonics.com/mcp`
     - `egitim-kaynak`: `https://egitim-kaynak.cureonics.com/mcp`
   - Kimlik doğrulama türü olarak **OAuth** seçin. Sunucular RFC 9728 Protected Resource
     Metadata (PRM) ve PKCE S256 akışını sunar; açılan login formuna Doppler'dan aldığınız
     anahtarı girin. Dönen authorization code/access token opaque'dır ve API anahtarının
     kendisi değildir.

2. **Custom GPT Yapılandırması**:
   - **Name**: Edupedia MEB Öğrenim Modülü Üreticisi
   - **Instructions**: `skills/carbon-edupedia/SKILL.md` ve `.codex-plugin/openai.yaml` içeriğini talimat olarak ekleyin.

---

### Platform E · Google Gemini / Google AI Studio / Spark

Bu yüzeylerde Edupedia **prompt uyarlaması** olarak kullanılır. İlgili Google ürünü/hesabı
Streamable HTTP MCP connector'ı sunuyorsa OAuth 2.1 ile iki MCP bağlanabilir; native
Edupedia plugin/hook/alt-ajan paritesi yoktur.

1. **OAuth İzin Listesi Doğrulaması**:
   - Her iki MCP sunucusu da Google'ın resmî OAuth redirect broker'ı olan `https://oauth-redirect.googleusercontent.com` adresini varsayılan olarak destekler.
2. **Konnektör Tanımı**:
   - Endpoint URL'leri: `https://mufredat.cureonics.com/mcp` ve `https://egitim-kaynak.cureonics.com/mcp`.

---

### Platform F · VS Code / Roo Code / Cline / Windsurf / Claude Desktop

Bu ailede temel düzey **prompt uyarlaması**dır. İstemci gerçekten remote/Streamable HTTP MCP
destekliyorsa aşağıdaki örneklerden uygun olanıyla authenticated MCP eklenebilir. JSON kaydı
tek başına Edupedia komutlarını, hook'larını, `module-auditor`'ı veya Tier-2b script
otomasyonunu kurmaz.

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
| **Destek düzeyi** | **Native plugin** | Skill paketi + MCP | **Native plugin** | Prompt + koşullu MCP | Prompt + koşullu MCP | Prompt + istemciye bağlı MCP |
| **carbon-edupedia (9 mod)** | Native skill | Yüklenen skill | Native skill | Prompt uyarlaması | Prompt uyarlaması | Prompt uyarlaması |
| **16 kapı (`validate_module.py`)** | Otomatik Claude hook + yerel Python | Kod çalıştırma varsa manuel; hook yok | Otomatik Cursor hook + yerel Python | Host/sandbox'a bağlı manuel | Host/sandbox'a bağlı manuel | Yerel Python varsa manuel; otomatik hook yok |
| **Müfredat MCP (21 araç)** | Paketli Bearer | Custom Connector OAuth | MCP Settings Bearer/OAuth | Ürün/hesap destekliyorsa OAuth | Ürün/hesap destekliyorsa OAuth | İstemci destekliyorsa remote MCP |
| **Eğitim Kaynak MCP (6 araç, keyed)** | Paketli Bearer | Custom Connector OAuth | MCP Settings Bearer/OAuth | Ürün/hesap destekliyorsa OAuth | Ürün/hesap destekliyorsa OAuth | İstemci destekliyorsa remote MCP |
| **module-auditor** | Native alt-ajan | Yok; prompt içi denetim | Native alt-ajan | Yok | Yok | Yok |
| **Hook'lar** | `hooks/hooks.json` | Yok | `hooks/hooks-cursor.json` | Yok | Yok | Yok |
| **Komutlar (`/edupedia:*`)** | Native | Yok; doğal dil | Native | Yok; prompt | Yok; prompt | Yok; custom prompt |
| **Tier-1 SVG üretimi** | Skill + validator | Skill paketi; otomatik validator yok | Skill + validator | Prompt; otomatik doğrulama yok | Prompt; otomatik doğrulama yok | Prompt; manuel doğrulama |
| **Tier-2a gözlem (`get_figure`)** | Metadata + ImageContent | Connector ImageContent | Metadata + ImageContent | Host connector'ı ImageContent gösterirse | Host connector'ı ImageContent gösterirse | MCP istemcisi ImageContent gösterirse |
| **Tier-2b binary çıkarım (`fetch_figure.py`)** | Yerel FS+Python | Native yol yok | Yerel FS+Python | Native yol yok | Native yol yok | Yalnız script açıkça yerelde çalıştırılırsa; MCP JSON'u yeterli değil |

---

## 4. Sorun Giderme ve Teşhis

- **401 Unauthorized Hatası**: Anahtarın eksik veya süresinin dolduğunu gösterir. Claude Code için Doppler üzerinden oturum açın; web platformlarında (claude.ai, ChatGPT) connector OAuth formuna anahtarı yeniden girin.
- **Konnektör Sağlık Kontrolü**:
  - Claude Code: `/edupedia:durum`
  - CLI Testi: `python3 hooks/scripts/fleet_probe.py --fresh`
  - Unit Testleri: `python3 hooks/test_hooks.py`
