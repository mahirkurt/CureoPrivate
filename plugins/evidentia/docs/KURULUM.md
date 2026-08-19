# Evidentia — Kurulum Kılavuzu (kamuya açık)

> **Bu dosya plugin ile birlikte DAĞITILIR.** Operatörün sır taşıyan kopyası
> (`EVIDENTIA-KURULUM-VE-KEYLER.md`) `.gitignore`'ludur ve hiçbir kuruluma gelmez —
> 2026-08-07 denetimi (MINOR-2) `skills/start/SKILL.md` ile `CONNECTORS.md`'nin
> kullanıcıyı o dağıtılmayan dosyaya yönlendirdiğini buldu. Buradaki metin o dosyanın
> sır İÇERMEYEN bölümünden birebir türetilmiştir; **anahtar DEĞERLERİ yalnız Doppler'da**
> yaşar (aşağıda §Anahtar değerlerini alma).


> **Güncel:** 2026-08-18 · evidentia plugin **v2.7.2** / flagship skill `medical-research` **v9.0.2**
> · CureoPrivate `plugins/evidentia`
> · **ChatGPT custom-connector uyumu** (orijinal **4 CF self-host Worker**, 2026-06-30 canlı doğrulandı; bkz. Kurulum yolu **C**)
> · **openathens (HP self-host) full-text Tier-3**: 11 araç; metin + sağlayıcı-nötr orijinal PDF
> (`oa_fetch_fulltext`/`oa_fetch_pdf`). **annas-reader Tier-5 son çare**: 9 araç; okuma +
> PDF/EPUB ve desteklenen diğer formatlar (`download_document`).
>
> 🔒 **GÜVENLİK.** Bu kamuya açık dosya hiçbir canlı MCP anahtar değeri içermez. Anahtarların tek
> doğruluk kaynağı **Doppler** (`cureohub` / `dev_personal`); değerleri belgeye, sohbete veya Git'e
> yapıştırma. Yetkili operatörün yerel oturumunda bir değeri tazelemesi gerekirse:
> ```bash
> doppler secrets get <VAR> --plain -p cureohub -c dev_personal
> ```
> Claude Code plugin'i çalıştırırken `doppler run -- claude` ile tüm `${VAR}`'lar süreç
> ortamına otomatik enjekte olur (`.mcp.json` bunları genişletir) — elle yapıştırmaya gerek yok.

## Connector roster — anahtar gerekliliği

| Connector | Endpoint | Key? | Doppler var | Not |
|---|---|:---:|---|---|
| **anamnesis** (self-host) | `anamnesis-mcp.cureonics.workers.dev/mcp` | ✅ | `ANAMNESIS_MCP_API_KEY` | Bearer-gated — RAG/GraphRAG; yazma + **yıkıcı `forget_document`** + ücretli Workers-AI/Vectorize/D1 → public açılmaz |
| **evidentia-kb** (self-host) | `evidentia-kb-mcp.cureonics.workers.dev/mcp` | ✅ | `EVIDENTIA_KB_MCP_API_KEY` | Bearer-gated — `kb_upsert` (yazma) + Vectorize → public açılmaz |
| **openfda** (self-host) | `openfda-mcp.cureonics.workers.dev/mcp` | ✅ | `OPENFDA_MCP_API_KEY` | **RE-GATED 2026-06-28** — `icd11_search` server-side WHO ICD-11 OAuth cred'i (`ICD11_CLIENT_ID/SECRET`) taşır → açık olsa confused-deputy/kota-suistimali; Bearer zorunlu |
| **drugddx** (self-host) | `drugddx-mcp.cureonics.workers.dev/mcp` | ❌ | — (`MCP_ALLOW_NO_AUTH=1`) | **AÇIK/keyless** — salt-okunur NIH RxNav/DailyMed proxy, **server-side upstream cred YOK** → confused-deputy yok; maliyet yalnız Worker invocation |
| **who-gho** (self-host) | `who-gho-mcp.cureonics.workers.dev/mcp` | ❌ | — (`MCP_ALLOW_NO_AUTH=1`) | **AÇIK/keyless** — WHO GHO OData proxy (`ghoapi.azureedge.net` authless), **server-side sır YOK** → confused-deputy yok. Küresel/ülke hastalık yükü (Türkiye dahil); PopHIVE'ın ABD-only boşluğunu kapatır. ✅ CANLI 2026-07-05 (Version 30df2ff2, E2E doğrulandı) |
| **globocan** (self-host) | `globocan-mcp.cureonics.workers.dev/mcp` | ❌ | — (`MCP_ALLOW_NO_AUTH=1`) | **AÇIK/keyless** — IARC GLOBOCAN 2022 proxy (`gco-api.iarc.fr` authless+headerless), **server-side sır YOK**. Küresel/ülke kanser insidans+mortalite (Türkiye dahil); who-gho'yu kanser-özelinde tamamlar. ✅ CANLI 2026-07-05 (Version 74cfb636, E2E doğrulandı) |
| **ema** (self-host) | `ema-mcp.cureonics.workers.dev/mcp` | ❌ | — (`MCP_ALLOW_NO_AUTH=1`) | **AÇIK/keyless** — EMA Medicines/EPAR **baked korpus** (authless XLSX'ten build; runtime upstream/sır YOK). AB ruhsat + CHMP/EPAR (openFDA'nın AB muadili). Yenile: `npm run build:corpus`+redeploy. ✅ CANLI 2026-07-05 (Version ff226c89, 2712 ilaç, E2E doğrulandı) |
| **titck** | `titck.cureonics.com/mcp` | ✅ | `TITCK_MCP_API_KEY` | **KAPILI** (Bearer). ⚠️ 2026-07-31'de `titck-cache-mcp` Worker'ı emekli edildi, önbellek sunucunun içine taşındı ve uç KAPATILDI — bu satır 2026-08-07'ye kadar "anahtarsız/açık tasarım" diyordu, o yönergeyi izleyen kurulum 401 alır. Kanonik Türkiye ilaç indeksi, 66 araç, v0.5.8 |
| **med-terminologies** | `medical.sidneybissoli.com/mcp` | ❌ | — | Üçüncü-taraf keyless (topluluk) |
| **nih-clinicaltables** | `gateway.pipeworx.io/clinicaltables/mcp` | ❌ | — | Üçüncü-taraf keyless |
| **nlm-rxnorm** | pipeworx gateway | ❌ | — | Üçüncü-taraf keyless |
| **iuphar-gtopdb** | pipeworx gateway | ❌ | — | Üçüncü-taraf keyless |
| **openalex** | `openalex.cureonics.com/mcp` | ✅ | `OPENALEX_MCP_API_KEY` | CureoHub HP self-host `:8324` (Worker undeploy 2026-08-17) |
| **pubmed-epmc** | `pubmed.cureonics.com/mcp` | ✅ | `PUBMED_MCP_API_KEY` | CureoHub HP self-host `:8325` (Worker undeploy 2026-08-17) |
| **semantic-scholar** | `semanticscholar.cureonics.com/mcp` | ✅ | `SEMANTICSCHOLAR_MCP_API_KEY` | CureoHub HP self-host `:8323` (Worker undeploy 2026-08-17) |
| **annas-reader** | `annas.cureonics.com/mcp` | ✅ | `ANNAS_MCP_API_KEY` | Operatör-bağlı HP self-host (Docker); static-Bearer veya OAuth. 9 araç: Tier-5 son çare okuma + `download_document(id=<DOI\|MD5>)`; PDF/EPUB/MOBI/AZW/DjVu/FB2/CBZ/CBR/XPS kısa-ömürlü opaque link + SHA-256, yalnız analiz. |
| **yok-akademik** | `yok-akademik.cureonics.com/mcp` | ✅ | `YOK_AKADEMIK_MCP_API_KEY` | Operatör-bağlı HP self-host; OAuth 2.1 + Bearer |
| **openathens** (self-host) | `openathens.cureonics.com/mcp` | ✅ | `OPENATHENS_MCP_API_KEY` | Operatör-bağlı HP self-host (systemd); OAuth 2.1 + Bearer. 11 araç: tam-metin **Tier 3 LİSANSLI**; `oa_fetch_fulltext` + sağlayıcı-nötr `oa_fetch_pdf(doi\|url)` (kısa-ömürlü opaque link + PDF doğrulama/SHA-256; 100 MiB tavanı). annas'ın önünde, legal-öncelikli. |

> **Suite bağlamı (evidentia dışı):** `CUREONICS_SUITE_MCP_KEY` — fon-mcp/titck-mcp/mevzuat-mcp'nin
> additive suite kapısı (CureoSuite bundle). evidentia self-host worker'larıyla ilgisizdir; burada
> yalnız tamlık için anılır.

## Kurulum yolları

### A. Claude Code plugin (`evidentia@cureonics-marketplace`)
`.mcp.json` gated connector'lar için `Bearer ${VAR}` kullanır → değerler süreç ortamından gelir:
```bash
doppler run -p cureohub -c dev_personal -- claude     # tüm ${VAR}'lar otomatik enjekte
# veya elle: export ANAMNESIS_MCP_API_KEY=...  EVIDENTIA_KB_MCP_API_KEY=...  OPENFDA_MCP_API_KEY=...
```
`drugddx` + üçüncü-taraf keyless'lar **hiçbir env gerektirmez** (⚠️ `titck` bu listeden 2026-08-07'de, `openalex` ve `pubmed-epmc` ise 2026-08-08'de ÇIKTI — ikincisi operatör API anahtarı (OpenAlex bütçesi / NCBI rate-limit) tuttukları için yeniden kapılandı: açık uç, operatörün kotasını herkese harcatırdı (confused deputy).)

### B. claude.ai / Claude Desktop custom connector
URL'yi ekle; **yalnız Bearer-gated** olanlara anahtar yapıştır:

| Anahtar gerektiren | Anahtarsız (URL yeter) |
|---|---|
| anamnesis · evidentia-kb · openfda · annas-reader · yok-akademik · **openathens** · **titck** · **pubmed-epmc** · **openalex** · **semantic-scholar** | **drugddx** · **who-gho** · **globocan** · **ema** · med-terminologies · nih-clinicaltables · nlm-rxnorm · iuphar-gtopdb · openalex · pubmed-epmc · semantic-scholar |

Değeri çek: `doppler secrets get OPENFDA_MCP_API_KEY --plain -p cureohub -c dev_personal`

### C. ChatGPT custom connector (Developer Mode)
ChatGPT (Plus/Pro/Business/Enterprise/Edu) **Settings → Connectors**'tan MCP custom connector
ekler; bu Worker'ların **rastgele araçları** (search/fetch değil — `semantic_search`,
`openfda_search`, `kb_search` …) tam çalışsın diye **Developer Mode** açık olmalıdır.

4 self-host Worker artık **ChatGPT-uyumludur** (canlı doğrulandı 2026-06-30, tam OAuth dansı →
`access_token`). Yapılan ayarlar:
- Redirect allowlist `https://chatgpt.com` içerir (`OAUTH_ALLOWED_REDIRECT_ORIGINS`, 4 Worker).
- OAuth keşfi **RFC 9728**'e göre sağlamlaştırıldı: 401 `WWW-Authenticate` artık
  `resource_metadata="…/.well-known/oauth-protected-resource/mcp"` taşır **ve** PRM
  **path-insertion** (`…/oauth-protected-resource/mcp`) hizmet eder — ChatGPT'nin keşif yolu
  bu iki yüzeyi kullanır (claude.ai çıplak path'i kullanır; ikisi de çalışır). DCR redirect_uris'i
  echo'lar; PKCE S256. **Tümü additive** → claude.ai/grok bozulmaz.

Her connector için **MCP Server URL = `…/mcp`**. ChatGPT'de Auth seçimi:

| ChatGPT Auth | Connector'lar | Anahtar nasıl verilir |
|---|---|---|
| **OAuth** | anamnesis · evidentia-kb · openfda (+ annas-reader · yok-akademik · openathens) | ChatGPT yetkilendirme sayfasını açar → sunucunun **authorize formuna MCP API key'i yapıştır** → ChatGPT token'ı kendisi alır. Anahtar **ChatGPT UI'ına değil, authorize formuna** girilir (claude.ai ile aynı tek-kiracılı model). |
| **No authentication** | **drugddx** · **who-gho** · **globocan** · **ema** · üçüncü-taraf keyless (med-terminologies · nih-clinicaltables · nlm-rxnorm · iuphar-gtopdb) | URL yeter |
| **OAuth** (2026-08-08'de eklendi) | **pubmed-epmc** · **openalex** · **semantic-scholar** | Self-host'a taşındıktan sonra operatör API anahtarı aldılar → kapılandı |

> Anahtar değerlerini Doppler'dan al (aşağıda §"Anahtar değerlerini alma") (ör. `OPENFDA_MCP_API_KEY`).
> ChatGPT MCP istemcisi `/mcp`'yi **sunucu tarafından** çağırır → CORS gerekmez; OAuth dansı kullanıcının
> tarayıcısında olur. **drugddx açık/keyless** olduğundan 401 dönmez (OAuth gerekmez, doğrudan bağlanır).
> Üçüncü-taraf keyless connector'ların ChatGPT-uyumu **upstream operatöre** bağlıdır (bizim ayarımızın dışı).

### D. Directory / OAuth connector'ları (claude.ai hesap-düzeyi — `.mcp.json` DIŞI)

Tıbbi çekirdeğin bir bölümü **directory/OAuth connector'larından** gelir (PubMed/EPMC, ClinicalTrials,
Consensus, Scholar Gateway, bioRxiv, Elicit, AdisInsight, NPI). Bunlar **`.mcp.json` bundled
roster'ında bildirilmez** — bağlanmaları interaktif OAuth tarayıcı-dansı + hesap-düzeyi izin
gerektirir; statik URL+Bearer ile gömülemezler. Plugin bunları **referansla** entegre eder
(`medical-research` araçları ad'la çağırır); bağlama **yüzeye göre elle** yapılır. Kanonik connector
tablosu: `CONNECTORS.md §1.0 Directory Connector Tier`.

| Connector | claude.ai (web) | Claude Code (CLI) | ChatGPT |
|---|---|---|---|
| PubMed / Europe PMC | Settings → Connectors → **Directory'den ekle** (Anthropic HCLS) | `claude mcp add --transport http pubmed <hcls-url>` → `/mcp` ile tek-sefer OAuth | Settings → Connectors (varsa directory) |
| ClinicalTrials v2 | Directory'den ekle | `claude mcp add --transport http clinicaltrials <url>` | — |
| Consensus | Directory'den ekle (`bio-research:consensus`) | `claude mcp add` + OAuth | — |
| Scholar Gateway / bioRxiv / NPI | Directory'den ekle | `claude mcp add` + (varsa) OAuth | — |
| Elicit | Settings → Connectors → **OAuth** (`https://elicit.com/api/mcp`) | `claude mcp add --transport http elicit https://elicit.com/api/mcp` + OAuth | Settings → Connectors → OAuth |
| AdisInsight | Settings → Connectors → **OAuth** (Springer) | `claude mcp add` + OAuth | — |

> **Preflight config:** Proje köküne `.claude/evidentia.local.md` koyup `known_connected:` altında bu
> connector'ları listeleyin (şablon: `docs/evidentia.local.md.example`). Böylece `start` Adım 2
> preflight'ı onları **bağlı kabul eder**, tekrar probe etmez, "neden veri yok" gürültüsü kalkar.
> Bir connector bağlı değilse akış onun fallback merdivenine düşer (`CONNECTORS.md §2`) — asla durmaz.

---

## Deploy-tarafı sırlar (connector anahtarı DEĞİL)
Self-host worker'ların kendi secret store'unda (`wrangler secret put`) tutulan, **çağırana
gitmeyen** sunucu sırları — yalnız operatör deploy'unda gerekir:

| Worker | Secret(ler) | Doppler ayna |
|---|---|---|
| anamnesis | `MCP_API_KEY`, `AUTH_HMAC_SECRET` | `ANAMNESIS_MCP_API_KEY`, `ANAMNESIS_AUTH_HMAC_SECRET` |
| evidentia-kb | `MCP_API_KEY`, `AUTH_HMAC_SECRET` | `EVIDENTIA_KB_MCP_API_KEY`, `EVIDENTIA_KB_AUTH_HMAC_SECRET` |
| openfda | `MCP_API_KEY`, `AUTH_HMAC_SECRET`, **`ICD11_CLIENT_ID`/`ICD11_CLIENT_SECRET`** (WHO), `OPENFDA_KEY` (opsiyonel openFDA app key) | `OPENFDA_MCP_API_KEY`, `OPENFDA_AUTH_HMAC_SECRET`, `OPENFDA_KEY` |
| drugddx | `MCP_API_KEY`, `AUTH_HMAC_SECRET` (gate `MCP_ALLOW_NO_AUTH=1` ile **bypass**) | `DRUGDDX_MCP_API_KEY`, `DRUGDDX_AUTH_HMAC_SECRET` |
| who-gho | **sır YOK** (keyless; upstream WHO GHO OData authless, `MCP_ALLOW_NO_AUTH=1`). Yalnız **re-gate** edilirse `MCP_API_KEY`+`AUTH_HMAC_SECRET` gerekir. | — (re-gate: `WHO_GHO_MCP_API_KEY`, `WHO_GHO_AUTH_HMAC_SECRET`) |
| globocan | **sır YOK** (keyless; upstream IARC GLOBOCAN API authless+headerless, `MCP_ALLOW_NO_AUTH=1`). Yalnız re-gate → `MCP_API_KEY`+`AUTH_HMAC_SECRET`. | — (re-gate: `GLOBOCAN_MCP_API_KEY`, `GLOBOCAN_AUTH_HMAC_SECRET`) |
| ema | **sır YOK** (keyless; baked public EMA XLSX, runtime upstream/sır yok, `MCP_ALLOW_NO_AUTH=1`). Yalnız re-gate → `MCP_API_KEY`+`AUTH_HMAC_SECRET`. Veri yenileme = `npm run build:corpus`+redeploy (sır değil). | — (re-gate: `EMA_MCP_API_KEY`, `EMA_AUTH_HMAC_SECRET`) |
| openathens (**HP systemd**, CF Worker değil) | `MCP_API_KEY`, `AUTH_HMAC_SECRET` + Millet Kütüphanesi SAML login: `OPENATHENS_USERNAME`/`OPENATHENS_PASSWORD`/`OPENATHENS_LOGIN_URL`/`OPENATHENS_INSTITUTION` | `OPENATHENS_MCP_API_KEY`, `OPENATHENS_AUTH_HMAC_SECRET`, `OPENATHENS_USERNAME`, `OPENATHENS_PASSWORD`, `OPENATHENS_LOGIN_URL`, `OPENATHENS_INSTITUTION` — **Doppler→HP `.env`** (`wrangler` değil) |

> ⚠️ `MCP_ALLOW_NO_AUTH` worker `wrangler.jsonc` `vars`'ında: **0 = Bearer-gated, 1 = açık.**
> Şu an: anamnesis/evidentia-kb/openfda = `0`; drugddx = `1`. Değiştirip `npm run deploy`.
> openfda'yı **açma** — WHO ICD-11 cred'i confused-deputy yapar (bu yüzden 2026-06-28 re-gate edildi).

---


## Anahtar değerlerini alma

Anahtar **değerleri** bu depoda hiçbir yerde yazılı değildir. Tek kaynak Doppler
(`cureohub` / `dev_personal`):

```bash
# Önerilen: oturumu Doppler ile başlat — tüm ${VAR}'lar otomatik enjekte olur.
doppler run -p cureohub -c dev_personal -- claude

# Tek bir değeri elle çekmek gerekirse (ör. claude.ai connector alanına yapıştırmak için):
doppler secrets get OPENFDA_MCP_API_KEY --plain -p cureohub -c dev_personal
```

Hangi connector'ın anahtar istediğini yukarıdaki roster tablosu gösterir; kanonik,
üretilmiş liste ise `fleet.lock.json`'daki `auth_env` alanlarıdır — SessionStart
preflight'ı ve `scripts/g_probe.py` haritalarını oradan türetir, elle yazmaz.

Bir anahtar eksikse ilgili katman **dürüstçe degrade eder** (401 → 'skipped: anahtar
yok'); veri asla uydurulmaz. Preflight bunu oturum başında bildirir.
