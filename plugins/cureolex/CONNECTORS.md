# CONNECTORS.md — cureolex yüzey ve connector sözleşmesi

> **Normatif.** Wire edilmiş 22 hukuk/regülasyon MCP + 3 companion (Yargı · Open
> Law · Ansvar) için uç listesi, auth modeli ve **hangi ajan yüzeyinin neyi
> otomatik bağladığı** burada sabittir. `.mcp.json` bu dosyadaki roster'dan
> üretilir (`fleet.yaml` → `python3 tools/fleetkit/gen_fleet.py`). Anahtar
> **değerleri** yazılmaz; yalnız env **adları** vardır.

**Yanılgı önleme:** "Plugin her yerde her şeyi otomatik bağlar" **yanlıştır**.
Skill, komut ve ajan paketi marketplace kurulumuyla gelir; MCP ve hook katmanı
yüzeye göre ayrı bağlanır.

---

## 1. Yüzey matrisi

| Yüzey | Skill / komut / ajan | 22 wire'lı MCP | Python hook (SessionStart / Stop G0) | Ne yapmalısın |
|---|---|---|---|---|
| **Claude Code** | marketplace kurulumu | `.mcp.json` auto-wire | çalışır | `doppler run -p cureohub -c dev_personal -- claude` |
| **Cursor** | marketplace / GitHub plugin | `.cursor-plugin/mcp.json` auto-wire (`plugin-cureolex-<server>`) | çalışır (`python3`) | Süreç ortamında Doppler adları (`${env:VAR}`). `doppler run … -- cursor` veya `dotfiles-ai/scripts/sync-doppler-env.sh` sonra Cursor restart. `${VAR}` plugin-variable paste formu **kullanılmaz**. |
| **claude.ai** | plugin skills/komutlar yüklenebilir | **elle** Settings → Connectors | **koşmaz** | her gated URL için custom connector + Bearer/OAuth; G0 manifestosunu model yazar |
| **ChatGPT** (Developer Mode) | Codex skill / `interface` | **elle** Settings → Connectors | **koşmaz** | Plus/Pro/… + Developer Mode; gated uçlarda OAuth veya Bearer; public uçlarda "No authentication" |

Hook'un olmadığı yüzeyde SessionStart preflight ve Stop G0 **yoktur**. Flagship
skill yine G0 kapsam manifestosunu **çıktıya yazmak zorundadır** — hook yokluğu
kapsam kapısını kapatmaz, yalnız otomatik hatırlatmayı kaldırır. Scope Guard
skill metninde kalır (`§6`); UserPromptSubmit hook'u web'de sessizdir.

`/lex-connectors` canlı `fleet_probe.py` koşturur. Web yüzeyinde `python3` /
`CLAUDE_PLUGIN_ROOT` yoksa probe **atlanır**: aşağıdaki roster + kullanıcının
eklediği connector listesi raporlanır; canlı `ok` iddia edilmez.

---

## 2. Marketplace kurulum

```text
/plugin marketplace add mahirkurt/CureoPrivate
/plugin install cureolex@cureonics-marketplace
```

Cursor aynı GitHub marketplace kaynağını Claude plugin olarak da yükler. Native
Cursor manifesti `.cursor-plugin/plugin.json` + `.cursor-plugin/mcp.json`
(`${env:VAR}` — process env; plugin-variable paste formu değil). Codex/ChatGPT
yüzeyi `.codex-plugin/plugin.json` + `.codex-plugin/openai.yaml`.

Claude Code `userConfig` alanları Settings UI'da görünür **ama** `.mcp.json`
header'ı `${ENV}` okur. Yalnız UI'ya yapıştırılan değer header'ı **beslemez**;
aynı adı süreç ortamına da vermek gerekir (Doppler). Bu, host'un
userConfig→env fallback sözdiziminin belgelenmemiş olmasından gelir.

---

## 3. Wire edilmiş roster

<!-- GEN:connector-roster BEGIN -->
| Server | Endpoint | Auth | Doppler var | Tier |
|---|---|:---:|---|---|
| `mevzuat` | `https://mevzuat.cureonics.com/mcp` | Bearer | `MEVZUAT_MCP_API_KEY` | primary |
| `mevzuat-bilgisi` | `https://mevzuat.surucu.dev/mcp` | public | — | secondary |
| `resmi-gazete` | `https://resmi-gazete-mcp.cureonics.workers.dev/mcp` | Bearer | `RESMI_GAZETE_MCP_API_KEY` | primary |
| `titck` | `https://titck.cureonics.com/mcp` | Bearer | `TITCK_MCP_API_KEY` | primary |
| `tbmm` | `https://tbmm.cureonics.com/mcp` | Bearer | `TBMM_MCP_API_KEY` | primary |
| `saglikbakanligi` | `https://saglik-mcp.cureonics.com/mcp` | Bearer | `SAGLIK_BAKANLIGI_MCP_API_KEY` | primary |
| `detsis` | `https://detsis.cureonics.com/mcp` | Bearer | `DETSIS_MCP_API_KEY` | support |
| `health-policy` | `https://health-policy-mcp.cureonics.workers.dev/mcp` | Bearer | `HEALTH_POLICY_MCP_API_KEY` | comparative |
| `german-law` | `https://german-law.cureonics.com/mcp` | Bearer | `GERMAN_LAW_MCP_API_KEY` | comparative |
| `ich-guidelines` | `https://ich.cureonics.com/mcp` | Bearer | `ICH_MCP_API_KEY` | comparative |
| `intl-treaty` | `https://intl-treaty-mcp.cureonics.workers.dev/mcp` | Bearer | `INTL_TREATY_MCP_API_KEY` | comparative |
| `eudamed` | `https://eudamed-mcp.cureonics.workers.dev/mcp` | Bearer | `EUDAMED_MCP_MCP_API_KEY` | comparative |
| `oecd` | `https://oecd.cureonics.com/mcp` | Bearer | `OECD_MCP_API_KEY` | support |
| `yok-akademik` | `https://yok-akademik.cureonics.com/mcp` | Bearer | `YOK_AKADEMIK_MCP_API_KEY` | doctrine |
| `yoktez` | `https://yoktezmcp.fastmcp.app/mcp` | public | — | doctrine |
| `literatur` | `https://literatur-mcp.surucu.dev/mcp` | public | — | doctrine |
| `openathens` | `https://openathens.cureonics.com/mcp` | Bearer | `OPENATHENS_MCP_API_KEY` | fulltext |
| `annas-reader` | `https://annas.cureonics.com/mcp` | Bearer | `ANNAS_MCP_API_KEY` | fulltext |
| `eurlex` | `https://eurlex.cureonics.com/mcp` | Bearer | `EURLEX_MCP_API_KEY` | comparative |
| `fedlex` | `https://fedlex.cureonics.com/mcp` | Bearer | `FEDLEX_MCP_API_KEY` | comparative |
| `uk-legal` | `https://uk-law.cureonics.com/mcp` | Bearer | `UK_LEGAL_MCP_API_KEY` | comparative |
| `anamnesis` | `https://anamnesis-mcp.cureonics.workers.dev/mcp` | Bearer | `ANAMNESIS_MCP_API_KEY` | substrate |
| **Yargı** | _(kararlı self-host URL yok)_ | OAuth | claude.ai / ChatGPT / Cursor **Settings → Connectors** | companion |
| **Open Law** | _(kararlı self-host URL yok)_ | OAuth | claude.ai / ChatGPT / Cursor **Settings → Connectors** | companion |
| **Ansvar** | _(kararlı self-host URL yok)_ | OAuth | claude.ai / ChatGPT / Cursor **Settings → Connectors** | companion |
<!-- GEN:connector-roster END -->

`anamnesis` (Tier 2): `collection=cureolex:sess:<12hex>` + önekli `doc_id`
(`cureolex:sess:<id>:mevzuat:…` / `celex:` / `ecli:` / `rg:`). **`doc_scope`
yoktur.** Kapsamsız `hybrid_query`/`graph_*` PreToolUse DENY. Ledger
`.claude/anamnesis-cureolex.json`. `lib` varsayılan değil. Cevaplar
`doc_id::idx`. `corpus_stats` çalışma seti değildir. SessionEnd/startup
`forget_collection` (yoksa N× `forget_document`); Stop unutmaz.

`ich-guidelines` M4 (CTD) / M8 (eCTD) **spesifikasyon** yüzeyi IN'dir (modül,
granularity, bölgesel M1 vs ICH M2–M5, spesifikasyon sürümü, Q&A). COMPARATIVE
ve DRAFT dosya-yapısı atıfı yapabilir; şirket sequence / otorite gönderimi
`pharmaintel` ops'tur — ICH MCP bu soruları reddetmez.

Public (Bearer yok): `mevzuat-bilgisi`, `yoktez`, `literatur`.

Gated Bearer: süreç ortamındaki Doppler adı. Claude Code `${VAR}` okur. Cursor
native wire (`.cursor-plugin/mcp.json`) **`${env:VAR}`** okur — IDE bunu plugin
variable sanıp yapıştırma formu açmasın diye. Üç kapı adı `EURLEX_MCP_API_KEY` /
`FEDLEX_MCP_API_KEY` / `UK_LEGAL_MCP_API_KEY` (Doppler `cureohub/dev_personal`).
Yerel `~/.dotfiles-ai/secrets/secrets.env` geride kaldıysa
`dotfiles-ai/scripts/sync-doppler-env.sh` sonra Cursor'ı yeniden başlat. Env'de
yoksa Cursor "enter key" sorar; env varsa sormaz. Anahtar yoksa o katman
`auth_missing` (meşru degrade) — plugin paketi bu boşluğu dolduramaz.

---

## 4. Companion (wire edilemez)

Kararlı self-host URL'leri yoktur. claude.ai / ChatGPT / Cursor **Settings →
Connectors** üzerinden bağlanır. Bağlıyken tetiklenen bağlamda atlanamazlar.

| Companion | Kapı / rol | Yoksa |
|---|---|---|
| **Yargı** | G5 içtihat zinciri | G5 en fazla CONDITIONAL |
| **Open Law** | UK çapraz/HUDOC (statute birincil = wire `uk-legal` `legislation_*`) | Wire fail → `ep.legislation_uk`; **G6'yı düşürmez** (G6 = wire'lı `eurlex`) |
| **Ansvar** | Mod 7, 58-yargı tarama | ilgili yargı satırı `manual_required` |

---

## 5. claude.ai / ChatGPT elle connector

Her satır için: **Add custom connector** → Remote MCP URL = tablodaki Endpoint
→ gated ise Authentication = Bearer (veya sunucunun OAuth 2.1 dansı) ve Doppler
adındaki anahtar. Public satırlarda authentication yok.

OAuth redirect allowlist sunucu tarafında `claude.ai` / `claude.com` /
`chatgpt.com` / `grok.com` taşır (RFC 9728). Bu, ChatGPT'nin plugin'i **otomatik
yüklediği** anlamına gelmez — Developer Mode'da URL hâlâ elle eklenir.

Görünen connector adı insan tercihidir. Distiller ajanlarının `tools:`
allowlist'i hem `mcp__<server>__*` hem ölçülmüş `mcp__claude_ai_<Görünen>__*`
öneğini taşır. Yeni bir görünen ad ölçülmeden allowlist'e eklenmez
(`fleet.yaml` `tool_prefixes`).

Cursor distiller öneği ayrıca `mcp__plugin-cureolex-<server>__*` (tireli)
taşır; Claude Code biçimi `mcp__plugin_cureolex_<server>__*` kalır.

---

## 6. Auth özeti

```bash
doppler run -p cureohub -c dev_personal -- claude
doppler run -p cureohub -c dev_personal -- cursor
```

Anahtar yok → o katman graceful degrade (`skipped: anahtar yok`), çıktı durmaz,
uydurma yok. Anahtar var ama uç 401 → **yapılandırma arızası**, degrade değil.

Canlı sağlık (yalnız Python'lu host): `/lex-connectors` veya
`python3 hooks/scripts/fleet_probe.py --fresh`.
