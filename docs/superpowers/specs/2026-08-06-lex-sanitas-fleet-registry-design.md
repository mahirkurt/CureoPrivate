# lex-sanitas v3.5.0 — Türetilmiş Filo (Fleet Registry) Tasarımı

**Tarih:** 2026-08-06
**Plugin:** `plugins/lex-sanitas` (3.4.0 → 3.5.0)
**Kapsam:** MCP filosu bütünlüğü, tek-kaynak-of-truth registry, canlı prob'lu preflight, doktrin/tam-metin genişletmesi, alt-ajan araç kısıtı.

---

## 1. Problem

lex-sanitas 3.4.0 olgun bir protokol (9 mod, G0–G9 kapıları, 19 referans, 12 şablon) ama **filo tanımı 8 ayrı yerde elle** tutuluyor ve hiçbiri diğerinden türemiyor:

1. `.mcp.json` — `mcpServers` (kanonik olması beklenen)
2. `.codex-plugin/plugin.json` — aynı bloğun **birebir kopyası**
3. `hooks/scripts/session_start.py` — `GATED` sözlüğü (anahtar haritası)
4. `commands/lex-connectors.md` — anahtar env-var tablosu
5. `skills/lex-sanitas/SKILL.md` §3 + §4 (G0) — düzyazı sayı ve rol listeleri
6. `README.md` — düzyazı
7. `references/00-mod-pipelines.md` — mod×server listeleri
8. `tests/*.yaml` — filo sayısına dayanan iddialar

Bu yapı iki somut arızaya yol açtı (2026-08-06 canlı doğrulandı):

### 1.1 Kritik: TİTCK katmanı ölü

TİTCK 2026-08-02'de kapılandı (`titck-cache` Worker'ı emekli, önbellek sunucuya taşındı, `titck.cureonics.com` artık Bearer ister). `rxpraxis` v1.2.2'de düzeltildi; **lex-sanitas atlandı.**

```
titck (anahtarsız, mevcut hâl)   → HTTP 401  {"error":"unauthorized"}
titck (Bearer TITCK_MCP_API_KEY) → HTTP 200  66 araç
```

Arıza **dört yerde birden** saklandı: `.mcp.json` header'sız + `_role` "gate yok" diyor; `.codex-plugin` kopyası aynı; `session_start.py` titck'i `GATED`'e almadığı için preflight uyarmıyor, üstelik "Public server'lar — titck, mevzuat-bilgisi — etkilenmez" diye **aktif olarak yanlış** bilgi enjekte ediyor; `/lex-connectors` tablosu "public — anahtar yok" diyor.

Yani plugin'in ilaç/cihaz regülasyon katmanı (TİTCK yönetmelik/SUT/ruhsat reformlarının mevcut-durum kaynağı) her çağrıda sessizce 401 alıyor ve G0 manifestosunda "degraded" olarak görünüyor — ama **düzeltilebilir bir yapılandırma hatası** olduğu hiçbir yerden anlaşılmıyor.

### 1.2 Sayı sürüklenmesi

`.mcp.json` **15** server tanımlıyor (14 kaynak + `anamnesis` substratı). Plugin 10 dosyada, 15+ yerde **"14"** diyor. Sayı iddiası G0 kapısının ölçütü olduğu için bu kozmetik değil: G0 "wire edilmiş 14 MCP … tamamı ateşlenmiş" diyor, gerçekte 15 var.

### 1.3 Kök neden

**Preflight gerçek prob yapmıyor.** `session_start.py` yalnız `os.environ.get(var)` bakıyor → "anahtar var ama server 401" ve "anahtar hiç beklenmiyor ama server artık istiyor" hallerini **yapısal olarak göremez**. titck arızası tam bu kör noktada yaşadı.

---

## 2. Çözüm mimarisi

**İlke:** filo tek yerde tanımlanır, geri kalan her şey ya türetilir ya da bir kapıyla doğrulanır.

```
fleet.yaml                        ← ELLE YAZILAN TEK KAYNAK
  │
  ├─ tools/gen_fleet.py ──┬─► .mcp.json                      (tam üretim)
  │                       ├─► .codex-plugin/plugin.json      (mcpServers bloğu yerinde değiştirilir)
  │                       ├─► fleet.lock.json                (stdlib-okunur; hook'lar bunu okur)
  │                       ├─► commands/lex-connectors.md     (⟨GEN⟩ işaretli anahtar tablosu)
  │                       └─► agents/*.md                    (⟨GEN⟩ işaretli tools: satırı)
  │
  └─ tools/check_drift.py ─► CI kapısı
        · yeniden üret + diff  → türetilmiş ≠ commit'li ise FAIL
        · düzyazı sayı taraması → elle yazılmış filo sayısı ≠ len(fleet) ise FAIL
        · auth_env kapsam denetimi → auth_env'li her server hook GATED'inde görünmeli
```

`fleet.yaml` insan-yazımı için YAML; **hook'lar `fleet.lock.json` okur** (stdlib `json`) — kullanıcı sisteminde PyYAML olmasa da preflight çalışır. Lock dosyası commit'lenir.

### 2.1 `fleet.yaml` şeması

```yaml
version: 1
plugin: lex-sanitas
plugin_version: "3.5.0"

servers:                       # wire edilebilen (.mcp.json'a giren) sunucular
  - name: mevzuat
    url: https://mevzuat.cureonics.com/mcp
    tier: primary              # primary|secondary|comparative|support|doctrine|fulltext|substrate
    auth_env: MEVZUAT_MCP_API_KEY    # null ⇒ public (anahtarsız 200 beklenir)
    shard: S1                        # S1 TR-çekirdek · S2 karşılaştırmalı · S3 doktrin · S4 tam-metin
    modes: [ALL]                     # veya [DRAFT, AMEND, COMPARATIVE_LAW, …]
    gate: null                       # bağlı olduğu kalite kapısı (G5/G6/G7) veya null
    tools_used: [search_mevzuat, get_mevzuat_madde_tree, get_mevzuat_timeline, …]
    role: >-                         # .mcp.json _role notu
      PRİMER TR mevzuat — …
    degrade: >-                      # erişilemezse ne olur
      Anahtar yoksa manifestoda 'skipped: anahtar yok'; TR-mevzuat omurgası düşer …

companions:                    # wire EDİLEMEYEN dış connector'lar (claude.ai)
  - name: Yargı
    tool_prefixes: ["mcp__Yarg__", "mcp__claude_ai_Yarg__"]
    gate: G5
    modes: [ALL]
    manifest_row: "Yargı (companion — G5 içtihat)"
    degrade: "G5 en fazla CONDITIONAL — içtihat zinciri doğrulanamaz"

delegations:                   # zorunlu plugin delegasyonları
  - name: evidentia
    plugin_id_prefix: "evidentia@"
    trigger: "klinik boyut"
    manifest_row: "evidentia (klinik delegasyon)"
  - name: sci-audit
    plugin_id_prefix: "sci-audit@"
    trigger: "her reform-modu çıktısı"
    manifest_row: "sci-audit (çıktı-QA delegasyonu)"
```

### 2.2 Üretilen `fleet.lock.json`

Hook'ların ihtiyaç duyduğu minimum, stdlib-okunur:

```json
{
  "generated_from": "fleet.yaml",
  "plugin_version": "3.5.0",
  "counts": { "servers": 19, "gated": 16, "public": 3, "companions": 5, "delegations": 2 },
  "servers": [ {"name","url","tier","auth_env","shard","modes","gate"} ],
  "companions": [ {"name","tool_prefixes","gate","modes","manifest_row","degrade"} ],
  "delegations": [ {"name","plugin_id_prefix","manifest_row"} ]
}
```

`role`/`tools_used`/`degrade` düzyazısı lock'a **girmez** (hook'lar kullanmaz; dosyayı şişirir).

---

## 3. Filo bileşimi: 15 → 19 wire, 6 → 5 companion

Dört yeni aday 2026-08-06'da canlı `initialize` + `tools/list` ile doğrulandı.

| # | Server | Tier | Auth | Araç | Değişiklik |
|---|---|---|---|---|---|
| 1 | mevzuat | primary | `MEVZUAT_MCP_API_KEY` | 21 | — |
| 2 | mevzuat-bilgisi | secondary | public | 26 | — |
| 3 | resmi-gazete | primary | `RESMI_GAZETE_MCP_API_KEY` | 11 | — |
| 4 | **titck** | primary | **`TITCK_MCP_API_KEY`** | 66 | **🔴 auth eklenir (401→200)** |
| 5 | tbmm | primary | `TBMM_MCP_API_KEY` | 13 | — |
| 6 | saglikbakanligi | primary | `SAGLIK_BAKANLIGI_MCP_API_KEY` | 11 | — |
| 7 | detsis | support | `DETSIS_MCP_API_KEY` | 16 | — |
| 8 | health-policy | comparative | **`HEALTH_POLICY_MCP_API_KEY`** | 20 | 🟠 kanonik ada geçiş |
| 9 | german-law | comparative | `GERMAN_LAW_MCP_API_KEY` | 21 | — |
| 10 | ich-guidelines | comparative | `ICH_MCP_API_KEY` | 7 | — |
| 11 | intl-treaty | comparative | `INTL_TREATY_MCP_API_KEY` | 6 | — |
| 12 | eudamed | comparative | `EUDAMED_MCP_MCP_API_KEY` | 6 | — |
| 13 | oecd | support | `OECD_MCP_API_KEY` | 9 | — |
| 14 | yok-akademik | doctrine | `YOK_AKADEMIK_MCP_API_KEY` | 16 | — |
| 15 | **yoktez** | doctrine | public | 6 | ✨ companion → first-class |
| 16 | **literatur** | doctrine | public | 3 | ✨ yeni (DergiPark tam-metin) |
| 17 | **openathens** | fulltext | `OPENATHENS_MCP_API_KEY` | 10 | ✨ yeni (Tier 3 lisanslı) |
| 18 | **annas-reader** | fulltext | `ANNAS_MCP_API_KEY` | 8 | ✨ yeni (Tier 4 son çare) |
| 19 | anamnesis | substrate | `ANAMNESIS_MCP_API_KEY` | 8 | — |

**Companion (dış, wire edilemez): 5** — Yargı (G5) · Open Law (G6) · Ansvar (Mod 7) · Fedlex Swiss (Mod 7 CH) · Türk Patent (IP). `yoktez` bu listeden **çıkar**.

### 3.1 Yeni katmanların gerekçesi

- **yoktez** (`yoktezmcp.fastmcp.app/mcp`, authless): bugün "claude.ai connector olarak ekleyin" deniyor, dolayısıyla **G7 YÖK-Tez atıf doğrulaması kullanıcı aksiyonuna bağlı ve pratikte hiç yapılmıyor**. Wire edilince G7 CONDITIONAL→**hard PASS** olur: uydurma tez atfı (tez no/başlık/yazar) deterministik yakalanır.
- **literatur** (`literatur-mcp.surucu.dev/mcp`, authless): doktrin katmanı bugün yalnız `yok-akademik` **metadata**'sı — akademisyen profili, yayın başlığı. Gerekçe yazımında *okunabilir* Türk doktrini yok. DergiPark tam-metin (`search_articles` → `pdf_to_html`) bu boşluğu kapatır.
- **openathens** (Tier 3) + **annas-reader** (Tier 4): yabancı hukuk doktrini (monograf, hakemli makale) için lisanslı→son-çare şelalesi. vekayinuvis'te kanıtlanmış desen; Mod 7 COMPARATIVE_LAW ve G6 uluslararası kaynak teyidini besler. **Şelale disiplini:** openathens denenmeden annas-reader çağrılmaz; annas-reader çıktısı yalnız analiz içindir, tam-metin yeniden yayımlanmaz.

### 3.2 Kapı etkisi

| Kapı | Önce | Sonra |
|---|---|---|
| G5 içtihat | Yargı companion'a bağlı → CONDITIONAL | değişmez (Yargı hâlâ dış) |
| G6 uluslararası | Open Law companion'a bağlı → CONDITIONAL | değişmez; openathens/annas doktrin **desteği** ekler (birincil teyit değil) |
| **G7 epistemik dürüstlük** | YÖK-Tez doğrulaması companion'a bağlı | **wire'lı yoktez ile hard PASS** |

---

## 4. Canlı prob'lu preflight

### 4.1 `hooks/scripts/fleet_probe.py` (yeni)

Hem kütüphane hem CLI.

- `fleet.lock.json`'u okur; her server için sınıflandırma:

| Durum | Anlamı |
|---|---|
| `ok` | HTTP 200 + geçerli JSON-RPC `result` |
| `auth_missing` | `auth_env` tanımlı ama süreç ortamında yok → **istek atılmaz** |
| `unauthorized` | 401/403 — anahtar var/yok ama sunucu reddetti (**titck sınıfı arıza**) |
| `unreachable` | timeout, bağlantı hatası, 5xx |
| `error` | 200 ama JSON-RPC hata/ayrıştırılamaz gövde |

- **Eşzamanlılık:** `ThreadPoolExecutor(max_workers=10)`, uç başına 4 sn, toplam bütçe 8 sn. Bütçe dolarsa kalanlar `unknown` yazılır (asla asılı kalmaz).
- **Cache:** `${XDG_CACHE_HOME:-~/.cache}/lex-sanitas/fleet_probe.json`, TTL **24 saat**. Her oturumda ağ trafiği yok.
- **CLI:** `--fresh` (cache bypass), `--json`, `--quiet`.
- **Fail-open:** her istisna → boş sonuç + exit 0. Prob asla oturumu bloklamaz.
- **Bağımlılık yok:** yalnız stdlib (`urllib.request`, `json`, `concurrent.futures`).

### 4.2 `session_start.py` (yeniden yazılır)

- Anahtar haritası **`fleet.lock.json`'dan gelir** (hardcoded `GATED` sözlüğü silinir).
- Konvansiyon metnindeki sayılar lock'un `counts`'undan enterpole edilir ("14" hardcode'u ölür).
- `fleet_probe`'u kütüphane olarak çağırır (cache'li). **Yalnız sağlıksız satırları** enjekte eder — her şey yeşilse preflight bölümü sessizdir.
- `unauthorized` için ayrı ve keskin bir mesaj üretir: *"anahtar var ama sunucu reddetti — bu bir yapılandırma arızasıdır, degrade değil"*. Bu, titck sınıfı hatanın bir daha sessizce yaşamasını imkânsız kılar.
- Prob kullanılamazsa (import/cache/ağ hatası) **env-only moda düşer** — bugünkü davranış, fail-open.

### 4.3 `stop_coverage.py`

`MANDATORY_ROWS` lock'tan türetilir: `companions` (5) + `delegations` (2) = **7 satır** (bugün 8; `yoktez` companion olmaktan çıktığı için düşer). Wire'lı 19 server için satır-satır regex denetimi **eklenmez** — kırılgan olur; G0 manifesto varlığı ve companion/delegasyon satırları denetlenmeye devam eder.

### 4.4 `/lex-connectors`

Canlı prob raporuna dönüşür: her satır `ok / auth_missing / unauthorized / unreachable` + kapı etkisi. Anahtar env-var tablosu `⟨GEN⟩` işaretli blok olarak üretilir. `--fresh` argümanı desteklenir.

---

## 5. Alt-ajan araç kısıtı

`mcp__<server>__*` wildcard'ı agent frontmatter `tools:` alanında desteklenir (resmî `sonarqube` plugin'inde kullanımda doğrulandı). `fleet.yaml`'deki `shard` alanından türetilir:

| Ajan | Shard | Gördüğü server'lar |
|---|---|---|
| `legal-distiller` | S1 + S3 | mevzuat, mevzuat-bilgisi, resmi-gazete, titck, tbmm, saglikbakanligi, detsis, yok-akademik, yoktez, literatur, anamnesis |
| `comparative-law-researcher` | S2 + S4 | health-policy, german-law, ich-guidelines, intl-treaty, eudamed, oecd, openathens, annas-reader, anamnesis |
| `compliance-auditor` | denetim | mevzuat, mevzuat-bilgisi, resmi-gazete |
| `gerekce-drafter` | gerekçe | mevzuat, tbmm, resmi-gazete, yoktez, literatur |

Companion araç önekleri (`mcp__Yarg__*` vb.) ilgili ajanlara **eklenir** — bağlı değillerse zaten görünmezler, zarar yok.

`tools:` satırı `⟨GEN⟩` işaretli tek satır olarak üretilir; ajanın düzyazı gövdesine dokunulmaz.

---

## 6. Temizlik

| Öğe | İşlem |
|---|---|
| Kök `hooks.json` | **silinir** (`hooks/hooks.json` kanonik; tek fark trailing newline) |
| `.codex-plugin/plugin.json` `mcpServers` | üretilir; elle bakım biter |
| `agents/openai.yaml` | korunur (Codex yüzeyi), üretim kapsamına alınmaz — statik |
| Düzyazı "14" | tüm dosyalarda gerçek sayıyla değiştirilir; `check_drift.py` bundan sonra bekçilik eder |
| `references/00-mod-pipelines.md` | mod×server listeleri `⟨GEN⟩` bloğuna alınır |

---

## 7. Hata yönetimi ve degrade sözleşmesi

Değişmeyen invaryantlar (mevcut doktrin korunur):

- **Hiçbir MCP çağrısı bloklanmaz.** Tüm hook'lar fail-open.
- **Sessiz atlama yasak.** Her server manifestoda hit/empty/degraded/skipped-with-reason satırı taşır.
- **No-fabrication.** Erişilemeyen katman veri boşluğu olarak işaretlenir, doldurulmaz.

Yeni degrade kuralları:

- `fleet.lock.json` okunamazsa → hook'lar minimum gömülü listeye düşer + uyarı enjekte eder (asla çökmez).
- `fleet_probe` çalışmazsa → env-only preflight (bugünkü davranış).
- `openathens` erişilemezse → `annas-reader`'a düşme **meşru değildir**; şelale sırası korunur, satır `degraded` yazılır (lisanslı bandın yokluğu son çareyi otomatik açmaz).
- Yeni public server'lar (`yoktez`, `literatur`) 401 dönerse → `unauthorized` olarak raporlanır (upstream'in kapılanma ihtimali; titck dersinin genellemesi).

---

## 8. Test stratejisi

| Test | Tür | Yakaladığı |
|---|---|---|
| `tools/check_drift.py` | deterministik, CI kapısı | (a) türetilmiş dosya ≠ commit'li; (b) düzyazıdaki filo sayısı ≠ `len(servers)`; (c) `auth_env`'li server lock'ta eksik; (d) `tier`/`shard`/`modes` şema ihlali |
| `tests/fleet_registry_tests.yaml` | davranışsal | `public` işaretli server gerçekten anahtarsız 200 mü; `auth_env` adı Doppler'da var mı; companion listesi ≠ wire listesi (kesişim boş) |
| `hooks/test_hooks.py` (genişletilir) | birim | fleet_probe sınıflandırması (5 durum), cache TTL, bütçe aşımı → `unknown`, fail-open, `MANDATORY_ROWS` türetimi (7 satır) |
| Mevcut 6 test dosyası | güncellenir | 14→19, companion 6→5, G7 hard-PASS kuralı, yeni tam-metin şelalesi disiplini |

`check_drift.py` ağ erişimi **gerektirmez** (saf dosya karşılaştırması) — CI'da güvenle koşar. Ağ gerektiren `fleet_registry_tests.yaml` davranışsal katmandadır.

---

## 9. Sürümleme ve teslim

- `plugin.json` (×2) + `SKILL.md` frontmatter: **3.5.0**
- `.claude-plugin/marketplace.json`: lex-sanitas 3.4.0 → 3.5.0
- Commit'ler main üzerinde, mantıksal olarak ayrılmış; **push edilmez** (kullanıcı kararı).

## 10. Kapsam dışı

- Yargı / Open Law / Ansvar / Fedlex Swiss / Türk Patent için self-host MCP yazımı — bunlar dış connector kalır.
- 9 modun içerik/doktrin revizyonu (referanslar, şablonlar, kalite-kapı ölçütleri) — bu tasarım **filo bütünlüğü** işidir, norm-üretim doktrini değişmez.
- Diğer plugin'lerin marketplace sürüm sürüklenmesi (rxpraxis 1.2.1↔1.2.2, edupedia 0.6.5↔0.7.0) — ayrı iş.

## 11. Bilinen kullanıcı aksiyonu

`lex-sanitas@cureonics-marketplace` `~/.claude/settings.json` → `enabledPlugins` içinde **yok**; plugin kurulu değil. Bu iş kodu doğru hâle getirir, kurulumu kullanıcı `/plugin` ile yapar.
