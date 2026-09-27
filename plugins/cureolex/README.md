# Cureolex — Türkiye Sağlık Mevzuatı Reform Protokolü

En ileri düzey **sağlık mevzuatı üretim/reform** plugin'i: Türkiye'de sağlık-farmasötik regülasyonunun her düzleminde — **kanun · CBK · Cumhurbaşkanı kararı · yönetmelik · tebliğ · genelge** — yeni mevzuat üretir, mevcut mevzuatı değiştirir, gerektiğinde çerçeveyi yeniden yazar. **5210 sayılı Yönetmelik + AYM belirlilik içtihadı + OECD Better Regulation + Anayasa Md.17/56/90/5 + ICESCR Md.12** çerçevesinde, **G0-G11 kalite kapıları** ve **no-fabrication** disipliniyle. **4.0'dan itibaren** Türkiye davranışı yargı bölgesinden bağımsız bir çekirdeğin üstünde **bir paket** olarak durur; başka ülkeler aynı çekirdeğe paket olarak takılır.

Sürüm geçmişi: [CHANGELOG.md](CHANGELOG.md).

## Öne çıkanlar

- **12 mod:** DRAFT · AMEND · ANALYZE · COMPLY · OPINE · RIA · COMPARATIVE_LAW · TBMM_KANUN_TEKLIFI/PARLIAMENTARY_BILL · EX_POST_EVALUATION · REGULATORY_MATURITY · TRANSPOSITION · RELIANCE_FRAMEWORK.
- **Yargı bölgesi paketleri (4.0):** `jurisdictions/<kod>/jurisdiction_pack.yaml` — TR **active**; GB · DE · CH **draft** (çıktı en fazla LOW). Paket yetenek bayrakları güven tavanını belirler; wire'lı S1 bağlayıcısı + uzman paneli olmadan paket `active` olamaz. Ayrıntı: [`jurisdictions/README.md`](jurisdictions/README.md).
- **Tam-filo aktivasyonu:** wire edilmiş **20 hukuk/regülasyon MCP + 3 zorunlu companion** (Yargı · Open Law · Ansvar) her sorguda çalışır; her çıktı **kapsam manifestosu (G0)** taşır — hangi server çalıştı/boş/degrade/atlandı (sessiz atlama yasak; bağlam-dışı companion satırı dürüstçe `skipped: mod için N/A`).
- **Bağlam ekonomisi + büyük-veri:** tam-filo ham veriyi ana pencereye dökmez — **3-katmanlı ekonomi** (Tier 0 ana pencere · Tier 1 ≤4 paralel distiller alt-ajanı · Tier 2 **anamnesis** RAG/GraphRAG substratı, `collection=cureolex:sess:<id>`) + **kanonik cache** (bir-kez-getir, G0–G11 aynı sess) + **kör-getirme-yok chunking** + **devre-kesici/extract-then-evict**. Büyük kanun/statute/OCR → anamnesis ingest→bounded query (`doc_scope` yoktur; atıf `doc_id::idx`). Sözleşme: `skills/cureolex/shared/context-economy-contract.md`.
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
| `/lex-maturity <bölge + kapsam>` | WHO GBT düzenleyici olgunluk açığı (4.0) |
| `/lex-transpose <kaynak norm + bölge>` | Aktarım / uyum tablosu (4.0) |
| `/lex-reliance <bölge + işlev>` | Reliance çerçevesi taslağı (4.0) |
| `/lex-connectors` | Tam-filo bağlantı durumu |

Serbest metinle de tetiklenir (skill `cureolex` + `cureolex-start` router). Oryantasyon için `/lex-connectors` veya "cureolex nedir".

## Wire edilmiş MCP filosu (20 server + 3 companion)

Filo **tek bir kaynaktan** tanımlanır: [`fleet.yaml`](fleet.yaml). `.mcp.json`, `fleet.lock.json`, `/lex-connectors` anahtar tablosu, distiller ajanlarının `tools:` kısıtı ve mod×server matrisi **ondan üretilir** (`python3 tools/fleetkit/gen_fleet.py`); `tools/fleetkit/check_drift.py` türetilmiş≠commit'li hâlini ve düzyazıdaki yanlış filo sayılarını CI'da yakalar. **`tools/fleetkit/` KURULU PLUGIN'DE BULUNMAZ** — kaynak depoya (`CureoPrivate`) ait bir GELİŞTİRME aracıdır; kurulu pakette türetme/kapı komutları çalıştırılamaz, `fleet.yaml` ve türevleri salt-okunur kanıttır.

| Katman | Shard | Server'lar |
|---|---|---|
| TR primer/idari | S1 | mevzuat (primer) · resmi-gazete · titck · tbmm · saglikbakanligi · detsis |
| Karşılaştırmalı/uluslararası | S2 | health-policy (yabancı ülke) · german-law · **eurlex (G6 CELEX)** · **fedlex (CH birincil)** · **uk-legal (UK içtihat/Hansard)** · ich-guidelines · intl-treaty · eudamed · oecd |
| Doktrin | S3 | yok-akademik (künye) · **yoktez** (tez tam-metni + G7 atıf doğrulaması) · **literatur** (DergiPark makale tam-metni) |
| Tam-metin (tek katman) | S4 | **openathens** (Tier 3: `oa_fetch_fulltext` / `oa_fetch_pdf`, tek katman — erişilemezse `degraded: tam metin erişilemedi`) |
| Büyük-veri substratı | tümü | anamnesis (RAG/GraphRAG evidence_index — kaynak değil, bağlam-ekonomisi Tier 2) |
| **Companion** (wire edilemez — claude.ai connector) | — | Yargı içtihat · Open Law (UK çapraz/HUDOC; statute = `uk-legal` `legislation_*`) · Ansvar (58-yargı tarama) |

19'u Bearer-gated, 1'i public (`yoktez`).

## Kurulum ve kimlik doğrulama

Üç ajan yüzeyi **aynı paketi** yükler ama MCP/hook bağlama yolu farklıdır. Tam sözleşme: [`CONNECTORS.md`](CONNECTORS.md).

```bash
# Claude Code
doppler run -p cureohub -c dev_personal -- claude

# Cursor — native wire `${env:VAR}` (process env). Paste formu değil.
# Üç kapı: EURLEX_MCP_API_KEY, FEDLEX_MCP_API_KEY, UK_LEGAL_MCP_API_KEY
# (Doppler cureohub/dev_personal). secrets.env gerideyse:
#   bash dotfiles-ai/scripts/sync-doppler-env.sh
# sonra Cursor'ı yeniden başlat; veya `doppler run … -- cursor`.
```

claude.ai ve ChatGPT (Developer Mode) `.mcp.json`'ı otomatik yüklemez: her uç `CONNECTORS.md` roster'ından **Settings → Connectors** ile eklenir. Python hook bu iki web yüzeyinde **koşmaz** — G0 kapsam manifestosunu model yazar.

Auth'lu server'lar Bearer anahtarını süreç ortamından çözer. Bir anahtar yoksa o katman **graceful degrade** eder (kapsam manifestosunda `skipped: anahtar yok`) — çıktı durmaz, asla uydurma yapılmaz. Anahtar env-var haritası: `/lex-connectors`. Companion connector'lar (Yargı/Open Law/Ansvar) connector ayarlarından eklenir. Fedlex wire'lıdır. Canlı filo sağlığı (Python'lu host): `/lex-connectors` veya `python3 hooks/scripts/fleet_probe.py --fresh`.

## Mimari

```
cureolex/
├── .claude-plugin/plugin.json      # Claude Code / claude.ai marketplace (mcpServers+hooks+userConfig)
├── .cursor-plugin/plugin.json      # Cursor native manifest
├── .cursor-plugin/mcp.json         # üretilir — Cursor ${env:VAR} Bearer interpolasyonu
├── .codex-plugin/plugin.json       # ChatGPT / Codex (inline mcpServers)
├── .codex-plugin/openai.yaml       # ChatGPT interface stub
├── CONNECTORS.md                   # yüzey matrisi + connector roster (üretilen tablo)
├── fleet.yaml                      # ★ FİLONUN TEK GERÇEK KAYNAĞI (20 server + 3 companion)
├── fleet.lock.json                 # üretilir — hook'ların okuduğu stdlib türev
├── .mcp.json                       # üretilir — 20 MCP + tam-filo rol notları
├── skills/
│   ├── cureolex/                # flagship (12 mod, G0-G11) + 19 referans + 15 template + 4 şema
│   │   └── shared/                 # composition · coverage-manifest · context-economy (v3.5.5'te skill içine alındı)
│   └── cureolex-start/          # router / oryantasyon
├── commands/                       # 13 komut (12 mod + connectors)
├── agents/                         # comparative-law-researcher · compliance-auditor · gerekce-drafter · legal-distiller
├── jurisdictions/                  # 4.0 — _schema/ (paket şeması · kodlar · tavan kuralları · rubrik aileleri · bağlayıcı sözleşmesi)
│                                   #   · core_files.yaml · tr/ (active + golden_cases) · gb/ de/ ch/ (draft)
├── hooks/                          # SessionStart canlı-prob preflight · fleet_probe.py · UserPromptSubmit scope-guard · PostToolUse retrieve-don't-dump · Stop G0-kapsam kapısı
└── tests/                          # 7 süit — routing · scope-boundary · citation-hallucination
                                    #   · context-economy · fleet-registry · full-fleet-coverage · mod9
                                    #   + paket altın vakaları (jurisdictions/*/golden_cases.yaml)
                                    #   + run_suites.py (koşucu; şema/referans/fixture + yüzey wiring)
                                    #   + validate_packs.py (paket doğrulayıcısı; run_suites'ten de çağrılır)
```

> `tools/fleetkit/` (üretici + kapılar) **kaynak depoda kalır, kurulu pakette bulunmaz.**

## Çekirdek doktrin

- **İnsan denetimi her çıktıda zorunludur.** Bu plugin karar-destek üretir, resmî hukuki mütalaa değil.
- **Tam-filo + temiz-kopya:** tüm araçlar çalışır ama ham getirim `legal-distiller` alt-ajanında toplanır; ana bağlama yalnız damıtılmış sonuç + kapsam kanıtı gelir.
- **Kapsam:** reform/norm-üretim. Bireysel hak-arama (SGK red, AYM başvuru, malpraktis) ve promosyon denetimi kapsam dışıdır — cureolex çıktısı üretmez, hiçbir skill'e yönlendirilmez.

## Lisans

Internal skill asset — harici dağıtım için değildir.
