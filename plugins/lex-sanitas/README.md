# Lex Sanitas — Türkiye Sağlık Mevzuatı Reform Protokolü

En ileri düzey **sağlık mevzuatı üretim/reform** plugin'i: Türkiye'de sağlık-farmasötik regülasyonunun her düzleminde — **kanun · CBK · Cumhurbaşkanı kararı · yönetmelik · tebliğ · genelge** — yeni mevzuat üretir, mevcut mevzuatı değiştirir, gerektiğinde çerçeveyi yeniden yazar. **5210 sayılı Yönetmelik + AYM belirlilik içtihadı + OECD Better Regulation + Anayasa Md.17/56/90/5 + ICESCR Md.12** çerçevesinde, **G0-G9 kalite kapıları** ve **no-fabrication** disipliniyle.

> Eski `lex-sanitas` skill'inin (v2.9.0) mirasçısı. Yabancı-ülke mevzuat tarama işlevi ayrı bir MCP'ye (**health-policy**) taşındı; bu plugin onu *bir kaynak katmanı* olarak wire eder. Sürüm 3.0.0 = plugin mimarisi + tam-filo aktivasyonu. Sürüm 3.1.0 = bağlam-tetiklemeli ZORUNLU entegrasyon: evidentia/sci-audit kuruluysa atlanamaz; companion'lar (Yargı↔G5, Open Law↔G6, Ansvar↔Mod7) tam-filonun zorunlu üyeleri. Sürüm 3.2.0 = health-policy **semantic_search** doğal-dil giriş kapısı (çok-dilli keşif US/JP/AU/CN → fetch ile doğrulama), in-plugin **legal-distiller** ajanı, `start`→`lex-sanitas-start` skill yeniden adlandırması, hook test harness'ı + PostToolUse devre-kesicinin `additionalContext` kanalına taşınması. Sürüm 3.3.0 = **koşullu companion katmanı**: Fedlex Swiss (Mod7 CH birincil metin — Ansvar CH satırı çerçeve-teyide düşer) + YokTez (tez doktrini + G7 YÖK-Tez atıf doğrulama) + Türk Patent (ilaç IP/SPC/veri imtiyazı) — bağlıyken ilgili bağlam tetiklenince zorunlu; connector önek-eşleştirme notu (`mcp__<Ad>__*` / `mcp__claude_ai_<Ad>__*`). Sürüm 3.5.0 = **türetilmiş filo**: `fleet.yaml` tek kaynak → `.mcp.json`/codex/lock/komut/ajan türetilir + `tools/check_drift.py` sürüklenme kapısı; **canlı MCP prob'lu preflight** (`auth_missing` ≠ `unauthorized`); **titck Bearer gate onarımı** (2026-08-02 kapılanması kaçırılmıştı → katman 401 alıyordu); filo **15→19** (yoktez + literatur + openathens + annas-reader wire), companion **6→5** (yoktez first-class'a terfi → **G7 hard PASS**); distiller ajanlarına shard-tabanlı araç kısıtı; kök `hooks.json` kopyası kaldırıldı. Sürüm 3.4.0 = Fedlex Swiss/YokTez/Türk Patent **zorunlu companion kategorisine terfi**: manifesto satırları her çıktıda zorunlu (bağlam yoksa `skipped: mod için N/A`), Stop-hook `MANDATORY_ROWS` 5→8 satır.

## Öne çıkanlar

- **9 mod:** DRAFT · AMEND · ANALYZE · COMPLY · OPINE · RIA · COMPARATIVE_LAW · TBMM_KANUN_TEKLIFI · EX_POST_EVALUATION.
- **Tam-filo aktivasyonu:** wire edilmiş **19 hukuk/regülasyon MCP + 5 zorunlu companion** (Yargı · Open Law · Ansvar · Fedlex Swiss ↔ Mod7 CH birincil metin · Türk Patent ↔ IP-boyutlu reform) her sorguda çalışır; her çıktı **kapsam manifestosu (G0)** taşır — hangi server çalıştı/boş/degrade/atlandı (sessiz atlama yasak; bağlam-dışı companion satırı dürüstçe `skipped: mod için N/A`).
- **Bağlam ekonomisi + büyük-veri:** tam-filo ham veriyi ana pencereye dökmez — **3-katmanlı ekonomi** (Tier 0 ana pencere · Tier 1 ≤4 paralel distiller alt-ajanı · Tier 2 **anamnesis** RAG/GraphRAG substratı) + **kanonik cache** (bir-kez-getir) + **kör-getirme-yok chunking** + **devre-kesici/extract-then-evict**. Büyük kanun/statute/OCR → anamnesis ingest→bounded query. Sözleşme: `skills/lex-sanitas/shared/context-economy-contract.md`.
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

Serbest metinle de tetiklenir (skill `lex-sanitas` + `lex-sanitas-start` router). Oryantasyon için `/lex-connectors` veya "lex-sanitas nedir".

## Wire edilmiş MCP filosu (19 server + 5 companion)

Filo **tek bir kaynaktan** tanımlanır: [`fleet.yaml`](fleet.yaml). `.mcp.json`, `fleet.lock.json`, `/lex-connectors` anahtar tablosu, distiller ajanlarının `tools:` kısıtı ve mod×server matrisi **ondan üretilir** (`python3 tools/gen_fleet.py`); [`tools/check_drift.py`](tools/check_drift.py) türetilmiş≠commit'li hâlini ve düzyazıdaki yanlış filo sayılarını CI'da yakalar.

| Katman | Shard | Server'lar |
|---|---|---|
| TR primer/idari | S1 | mevzuat (primer) · mevzuat-bilgisi (ikincil çapraz-kontrol) · resmi-gazete · titck · tbmm · saglikbakanligi · detsis |
| Karşılaştırmalı/uluslararası | S2 | health-policy (yabancı ülke) · german-law · ich-guidelines · intl-treaty · eudamed · oecd |
| Doktrin | S3 | yok-akademik (künye) · **yoktez** (tez tam-metni + G7 atıf doğrulaması) · **literatur** (DergiPark makale tam-metni) |
| Tam-metin şelalesi | S4 | **openathens** (Tier 3 lisanslı) → **annas-reader** (Tier 4 son çare, yalnız analiz) |
| Büyük-veri substratı | tümü | anamnesis (RAG/GraphRAG evidence_index — kaynak değil, bağlam-ekonomisi Tier 2) |
| **Companion** (wire edilemez — claude.ai connector) | — | Yargı içtihat · Open Law (UK+EU) · Ansvar (300+ reg korpus) · Fedlex Swiss (CH) · Türk Patent (IP/SPC) |

16'sı Bearer-gated, 3'ü public (`mevzuat-bilgisi`, `yoktez`, `literatur`).

## Kurulum ve kimlik doğrulama

Auth'lu server'lar Bearer anahtarını süreç ortamından çözer (Doppler-injected). Oturumu şöyle başlat:

```bash
doppler run -p cureohub -c dev_personal -- claude
```

Bir anahtar yoksa o katman **graceful degrade** eder (kapsam manifestosunda `skipped: anahtar yok`) — çıktı durmaz, asla uydurma yapılmaz. Anahtar env-var haritası: `/lex-connectors`. Companion connector'lar (Yargı/Open Law/Ansvar/Fedlex Swiss/Türk Patent) claude.ai connector ayarlarından eklenir. Canlı filo sağlığı: `/lex-connectors` veya `python3 hooks/scripts/fleet_probe.py --fresh`.

## Mimari

```
lex-sanitas/
├── .claude-plugin/plugin.json      # manifest (v3.5.0)
├── fleet.yaml                      # ★ FİLONUN TEK GERÇEK KAYNAĞI (19 server + 5 companion)
├── fleet.lock.json                 # üretilir — hook'ların okuduğu stdlib türev
├── .mcp.json                       # üretilir — 19 MCP + tam-filo rol notları
├── tools/                          # gen_fleet.py (üretici) · check_drift.py (CI kapısı)
├── skills/
│   ├── lex-sanitas/                # flagship (9 mod, G0-G9) + 19 referans + 12 template + 4 şema
│   └── lex-sanitas-start/          # router / oryantasyon
├── commands/                       # 10 komut (9 mod + connectors)
├── agents/                         # comparative-law-researcher · compliance-auditor · gerekce-drafter · legal-distiller
├── hooks/                          # SessionStart canlı-prob preflight · fleet_probe.py · UserPromptSubmit scope-guard · PostToolUse retrieve-don't-dump · Stop G0-kapsam kapısı
├── shared/                         # composition-contract · coverage-manifest · context-economy-contract
└── tests/                          # routing · scope-boundary · citation-hallucination · mod9
```

## Çekirdek doktrin

- **İnsan denetimi her çıktıda zorunludur.** Bu plugin karar-destek üretir, resmî hukuki mütalaa değil.
- **Tam-filo + temiz-kopya:** tüm araçlar çalışır ama ham getirim `legal-distiller` alt-ajanında toplanır; ana bağlama yalnız damıtılmış sonuç + kapsam kanıtı gelir.
- **Kapsam:** reform/norm-üretim. Bireysel hak-arama (SGK red, AYM başvuru, malpraktis) → `saglik-sigorta`/`onko-erisim`; promosyon denetimi → `promo-censor`.

## Lisans

Internal skill asset — harici dağıtım için değildir.
