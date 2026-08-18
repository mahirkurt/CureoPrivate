# Cureolex — Türkiye Sağlık Mevzuatı Reform Protokolü

En ileri düzey **sağlık mevzuatı üretim/reform** plugin'i: Türkiye'de sağlık-farmasötik regülasyonunun her düzleminde — **kanun · CBK · Cumhurbaşkanı kararı · yönetmelik · tebliğ · genelge** — yeni mevzuat üretir, mevcut mevzuatı değiştirir, gerektiğinde çerçeveyi yeniden yazar. **5210 sayılı Yönetmelik + AYM belirlilik içtihadı + OECD Better Regulation + Anayasa Md.17/56/90/5 + ICESCR Md.12** çerçevesinde, **G0-G9 kalite kapıları** ve **no-fabrication** disipliniyle.

> Formerly **Lex Sanitas**. Eski `lex-sanitas` skill'inin (v2.9.0) mirasçısı. Yabancı-ülke mevzuat tarama işlevi ayrı bir MCP'ye (**health-policy**) taşındı; bu plugin onu *bir kaynak katmanı* olarak wire eder. Sürüm 3.0.0 = plugin mimarisi + tam-filo aktivasyonu. Sürüm 3.1.0 = bağlam-tetiklemeli ZORUNLU entegrasyon: evidentia/sci-audit kuruluysa atlanamaz; companion'lar (Yargı↔G5, Open Law↔G6, Ansvar↔Mod7) tam-filonun zorunlu üyeleri. Sürüm 3.2.0 = health-policy **semantic_search** doğal-dil giriş kapısı (çok-dilli keşif US/JP/AU/CN → fetch ile doğrulama), in-plugin **legal-distiller** ajanı, `start`→`cureolex-start` skill yeniden adlandırması, hook test harness'ı + PostToolUse devre-kesicinin `additionalContext` kanalına taşınması. Sürüm 3.3.0 = **koşullu companion katmanı**: Fedlex Swiss (Mod7 CH birincil metin — Ansvar CH satırı çerçeve-teyide düşer) + YokTez (tez doktrini + G7 YÖK-Tez atıf doğrulama) — bağlıyken ilgili bağlam tetiklenince zorunlu; connector önek-eşleştirme notu (`mcp__<Ad>__*` / `mcp__claude_ai_<Ad>__*`). Sürüm 3.5.0 = **türetilmiş filo**: `fleet.yaml` tek kaynak → `.mcp.json`/codex/lock/komut/ajan türetilir + `tools/fleetkit/check_drift.py` sürüklenme kapısı; **canlı MCP prob'lu preflight** (`auth_missing` ≠ `unauthorized`); **titck Bearer gate onarımı** (2026-08-02 kapılanması kaçırılmıştı → katman 401 alıyordu); filo **15→19** (yoktez + literatur + openathens + annas-reader wire), companion **6→5** (yoktez first-class'a terfi → **G7 hard PASS**); distiller ajanlarına shard-tabanlı araç kısıtı; kök `hooks.json` kopyası kaldırıldı. Sürüm 3.4.0 = Fedlex Swiss/YokTez/Türk Patent **zorunlu companion kategorisine terfi**: manifesto satırları her çıktıda zorunlu (bağlam yoksa `skipped: mod için N/A`); Stop-hook zorunlu satır sayısı **sabit olmaktan çıkıp `fleet.lock.json`'dan türer** (companions + delegations = **7**; eski düzyazıdaki “5→8” yanlıştı). Sürüm 3.5.4 = 2026-08-06 denetimi: ölü `lex-sanitas-mcp` adı registry/healthcheck/testlerden ayrıldı (uç 404), `mevzuat-bilgisi` devralma kuralı yazıldı, `check_drift` [6] sunucu-kimliği kapısı eklendi. Sürüm 3.5.5 = `shared/` skill'in içine alındı (claude.ai düzleştirilmiş paketinde `../../shared/` çözülmüyordu). Sürüm 3.5.6 = 2026-08-07 denetimi: **connector ad-eşleme katmanı** (`tool_prefixes` — aynı sunucu Claude Code'da `mcp__<ad>__`, claude.ai'de `mcp__claude_ai_<Görünen_Ad>__` yüklenir; ajan `tools:` allowlist'i sert olduğu için eşleşmezse sunucu ajan için YOKTUR), 2 komutun geçersiz YAML frontmatter'ı, `tests/run_suites.py` (70 vaka), shard/kapsam/companion sözleşme tablolarının fleet'e bağlanması. Sürüm 3.5.8 = **araç-düzeyi canlı kapı** (`check_tools.py`: `tools_used` beyanı ↔ canlı `tools/list`, + `--call` duman testi) — 3 fantom araç düzeltildi. Sürüm 3.5.9 = **Türk Patent companion'dan wire'a**; ÜÇÜNCÜ arıza katmanı (`isError:false` ama GÖVDEDE `error` → sessiz yanlış-negatif). Sürüm 3.6.0 = Open Law + Fedlex için **programatik yedek** (ep.legislation_uk / ep.fedlex_sparql) — companion'a bağımlılık kırıldı. Sürüm 3.7.0 = **eurlex wire'landı** (HP self-host, upstream pinli, önünde OAuth kapısı) → **G6 companion'dan kurtuldu, hard PASS**. Sürüm 3.8.0 = **fedlex + uk-legal wire'landı** (aynı desen; `mcp-oauth-gateway` genelleştirildi), Fedlex Swiss + Türk Patent companion'dan emekli → filo o kesitte 23-sunucu / 3 companion; SSE yanıt çerçevesi artık JSON-RPC `id` ile seçilir (yanlış-yeşil onarımı) + fleet.yaml yinelenen-anahtar kapısı. Sürüm 3.8.1 = 2026-08-08 ölçümü: **german-law free-tier haritası düzeltildi** (AB ailesinin 5'i de ÇALIŞIYOR; yalnız case-law/preparatory/version-tracking kapalı) + çözücü tuzakları belgelendi (`get_provision` yalnız `{id}` biçimiyle, `validate_citation` AMG'yi doğrulayamıyor); **DÖRDÜNCÜ arıza katmanı** (boş gövde `null`/`{}`/`[]` = arıza) + `check_drift` companion **ad-listesi** kapısı ve kök marketplace açıklamasının taranması.
>
> **Sürüm 3.8.6 (2026-08-18):** İkinci semantik geçiş — canlı yeteneklerin sıraya emilmesi: uk-legal `legislation_*` (httpx fix), UHRI HP indexer (`uhri_search`/`uhri_fetch_document` Md.90 sonrası zorunlu), fedlex Vernehmlassung RIA-only, mevzuat 0.15.1 `phrase`/`search_within`/bedesten gerekçe (ikincile gövde yok), german free-tier EU korunur. Stale skip'ler (UHRI exclude, `legislation_* yok`, Open Law-only UK) temizlendi. Önceki: **3.8.5** tools_used genişletme + conscious_excludes tek yer; fedlex danışma tools_used.
>
> **Sürüm 3.8.5 (2026-08-17):** Tam-filo araç ince ayarı — `tools_used` genişletildi (mevzuat list_*/detail/kurumlar, RG pdf/info, sb birimler/taslaklar, health-policy keşif araçları, oecd 9/9 + GOV_REG, yok/detsis omurga); distiller semantik sıra (ANALYZE→DRAFT, german resolve→EU, TBMM sira_no→gerekçe gövdesi, ich M4/M8, eudamed≠ÜTS); `conscious_excludes` tek yerde. **2026-08-18:** fedlex Vernehmlassung RIA'ya alındı. Önceki: **3.8.4** Claude Code `plugin.json` agents dosya listesi; Türk Patent emekli → 22 server.
>
> **Sürüm 3.8.3 (2026-08-16):** marketplace yüzey wiring — `.claude-plugin/plugin.json` artık `mcpServers` / `hooks` / `skills` / `commands` / `agents` bildirir; native `.cursor-plugin/plugin.json`; Codex `openai.yaml` `.codex-plugin/` altına taşındı; `CONNECTORS.md` Claude Code / Cursor / claude.ai / ChatGPT ayrımını sabitledi (web'de hook yok, MCP elle connector). Distiller `tools:` allowlist'ine Cursor tireli önek (`mcp__plugin-cureolex-<server>__*`) eklendi.
>
> **Sürüm 3.8.2 (2026-08-14):** OpenAthens `oa_fetch_pdf(doi|url)` ve Anna's Reader `download_document(id=DOI|MD5)` S4 tam-metin shard'ına eklendi; kısa-ömürlü resource link, SHA-256/provenance ve anamnesis bounded-analysis disipliniyle. Legal-first sıra ve Anna's yalnız-analiz kapısı değişmedi.

## Öne çıkanlar

- **9 mod:** DRAFT · AMEND · ANALYZE · COMPLY · OPINE · RIA · COMPARATIVE_LAW · TBMM_KANUN_TEKLIFI · EX_POST_EVALUATION.
- **Tam-filo aktivasyonu:** wire edilmiş **22 hukuk/regülasyon MCP + 3 zorunlu companion** (Yargı · Open Law · Ansvar) her sorguda çalışır; her çıktı **kapsam manifestosu (G0)** taşır — hangi server çalıştı/boş/degrade/atlandı (sessiz atlama yasak; bağlam-dışı companion satırı dürüstçe `skipped: mod için N/A`).
- **Bağlam ekonomisi + büyük-veri:** tam-filo ham veriyi ana pencereye dökmez — **3-katmanlı ekonomi** (Tier 0 ana pencere · Tier 1 ≤4 paralel distiller alt-ajanı · Tier 2 **anamnesis** RAG/GraphRAG substratı, `collection=cureolex:sess:<id>`) + **kanonik cache** (bir-kez-getir, G0–G9 aynı sess) + **kör-getirme-yok chunking** + **devre-kesici/extract-then-evict**. Büyük kanun/statute/OCR → anamnesis ingest→bounded query (`doc_scope` yoktur; atıf `doc_id::idx`). Sözleşme: `skills/cureolex/shared/context-economy-contract.md`.
- **No-fabrication:** kanun/CELEX/AYM/Yargıtay/PMID asla uydurulmaz; her atıf MCP-doğrulanmış (`evidence_ledger`).
- **Yumuşak delegasyon:** klinik kanıt → **evidentia**; atıf-adli + Türkçe dil → **sci-audit** (varsa; yoksa graceful degrade).
- **Scope Guard:** yalnız mevzuat reformu; bireysel dava/promosyon denetimi kapsam dışı.

## Komutlar

| Komut | Mod |
|---|---|
| `/lex-draft <konu>` | Yeni mevzuat taslağı (yönetmelik/tebliğ/CBK) |
| `/lex-amend <mevzuat + değişiklik>` | Mevcut mevzuat değişikliği |
| `/lex-analyze <mevzuat>` | Reform-öncesi analiz (7-boyut uyum + iptal-riski) |
| `/lex-comply <taslak>` | 5210 uyum denetimi (R6b 21-nokta rubrik) |
| `/lex-opine <taslak + kurum>` | Kurum/paydaş/bilirkişi görüşü |
| `/lex-ria <reform>` | Düzenleyici etki analizi (DEA/BEF) |
| `/lex-comparative <soru>` | Karşılaştırmalı hukuk (AB/US/JP/AU…) |
| `/lex-bill <konu>` | TBMM kanun teklifi (Anayasa Md.88) |
| `/lex-expost <mevzuat + dönem>` | Ex post değerlendirme (12-36 ay) |
| `/lex-connectors` | Tam-filo bağlantı durumu |

Serbest metinle de tetiklenir (skill `cureolex` + `cureolex-start` router). Oryantasyon için `/lex-connectors` veya "cureolex nedir".

## Wire edilmiş MCP filosu (22 server + 3 companion)

Filo **tek bir kaynaktan** tanımlanır: [`fleet.yaml`](fleet.yaml). `.mcp.json`, `fleet.lock.json`, `/lex-connectors` anahtar tablosu, distiller ajanlarının `tools:` kısıtı ve mod×server matrisi **ondan üretilir** (`python3 tools/fleetkit/gen_fleet.py`); `tools/fleetkit/check_drift.py` türetilmiş≠commit'li hâlini ve düzyazıdaki yanlış filo sayılarını CI'da yakalar. **`tools/fleetkit/` KURULU PLUGIN'DE BULUNMAZ** — kaynak depoya (`CureoPrivate`) ait bir GELİŞTİRME aracıdır; kurulu pakette türetme/kapı komutları çalıştırılamaz, `fleet.yaml` ve türevleri salt-okunur kanıttır.

| Katman | Shard | Server'lar |
|---|---|---|
| TR primer/idari | S1 | mevzuat (primer) · mevzuat-bilgisi (ikincil çapraz-kontrol) · resmi-gazete · titck · tbmm · saglikbakanligi · detsis |
| Karşılaştırmalı/uluslararası | S2 | health-policy (yabancı ülke) · german-law · **eurlex (G6 CELEX)** · **fedlex (CH birincil)** · **uk-legal (UK içtihat/Hansard)** · ich-guidelines · intl-treaty · eudamed · oecd |
| Doktrin | S3 | yok-akademik (künye) · **yoktez** (tez tam-metni + G7 atıf doğrulaması) · **literatur** (DergiPark makale tam-metni) |
| Tam-metin şelalesi | S4 | **openathens** (Tier 3: `oa_fetch_fulltext` / `oa_fetch_pdf`) → **annas-reader** (Tier 4: reader / `download_document`, son çare, yalnız analiz) |
| Büyük-veri substratı | tümü | anamnesis (RAG/GraphRAG evidence_index — kaynak değil, bağlam-ekonomisi Tier 2) |
| **Companion** (wire edilemez — claude.ai connector) | — | Yargı içtihat · Open Law (UK çapraz/HUDOC; statute = `uk-legal` `legislation_*`) · Ansvar (58-yargı tarama) |

19'u Bearer-gated, 3'ü public (`mevzuat-bilgisi`, `yoktez`, `literatur`).

## Kurulum ve kimlik doğrulama

Üç ajan yüzeyi **aynı paketi** yükler ama MCP/hook bağlama yolu farklıdır. Tam sözleşme: [`CONNECTORS.md`](CONNECTORS.md).

```bash
# Claude Code
doppler run -p cureohub -c dev_personal -- claude

# Cursor (süreç ortamı ${ENV} interpolasyonunu besler)
doppler run -p cureohub -c dev_personal -- cursor
```

claude.ai ve ChatGPT (Developer Mode) `.mcp.json`'ı otomatik yüklemez: her uç `CONNECTORS.md` roster'ından **Settings → Connectors** ile eklenir. Python hook bu iki web yüzeyinde **koşmaz** — G0 kapsam manifestosunu model yazar.

Auth'lu server'lar Bearer anahtarını süreç ortamından çözer. Bir anahtar yoksa o katman **graceful degrade** eder (kapsam manifestosunda `skipped: anahtar yok`) — çıktı durmaz, asla uydurma yapılmaz. Anahtar env-var haritası: `/lex-connectors`. Companion connector'lar (Yargı/Open Law/Ansvar) connector ayarlarından eklenir. Fedlex wire'lıdır. Canlı filo sağlığı (Python'lu host): `/lex-connectors` veya `python3 hooks/scripts/fleet_probe.py --fresh`.

## Mimari

```
cureolex/
├── .claude-plugin/plugin.json      # Claude Code / claude.ai marketplace (mcpServers+hooks+userConfig)
├── .cursor-plugin/plugin.json      # Cursor native manifest
├── .codex-plugin/plugin.json       # ChatGPT / Codex (inline mcpServers)
├── .codex-plugin/openai.yaml       # ChatGPT interface stub
├── CONNECTORS.md                   # yüzey matrisi + connector roster (üretilen tablo)
├── fleet.yaml                      # ★ FİLONUN TEK GERÇEK KAYNAĞI (22 server + 3 companion)
├── fleet.lock.json                 # üretilir — hook'ların okuduğu stdlib türev
├── .mcp.json                       # üretilir — 22 MCP + tam-filo rol notları
├── skills/
│   ├── cureolex/                # flagship (9 mod, G0-G9) + 19 referans + 12 template + 4 şema
│   │   └── shared/                 # composition · coverage-manifest · context-economy (v3.5.5'te skill içine alındı)
│   └── cureolex-start/          # router / oryantasyon
├── commands/                       # 10 komut (9 mod + connectors)
├── agents/                         # comparative-law-researcher · compliance-auditor · gerekce-drafter · legal-distiller
├── hooks/                          # SessionStart canlı-prob preflight · fleet_probe.py · UserPromptSubmit scope-guard · PostToolUse retrieve-don't-dump · Stop G0-kapsam kapısı
└── tests/                          # 7 süit — routing · scope-boundary · citation-hallucination
                                    #   · context-economy · fleet-registry · full-fleet-coverage · mod9
                                    #   + run_suites.py (koşucu; şema/referans/fixture + yüzey wiring)
```

> `tools/fleetkit/` (üretici + kapılar) **kaynak depoda kalır, kurulu pakette bulunmaz.**

## Çekirdek doktrin

- **İnsan denetimi her çıktıda zorunludur.** Bu plugin karar-destek üretir, resmî hukuki mütalaa değil.
- **Tam-filo + temiz-kopya:** tüm araçlar çalışır ama ham getirim `legal-distiller` alt-ajanında toplanır; ana bağlama yalnız damıtılmış sonuç + kapsam kanıtı gelir.
- **Kapsam:** reform/norm-üretim. Bireysel hak-arama (SGK red, AYM başvuru, malpraktis) → `saglik-sigorta`/`onko-erisim`; promosyon denetimi → `promo-censor`.

## Lisans

Internal skill asset — harici dağıtım için değildir.
