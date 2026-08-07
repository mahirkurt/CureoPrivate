# socius-vigil plugin — nitelikli pazar araştırması süiti

**Tarih:** 2026-08-06
**Durum:** onaylandı (kullanıcı, beş bölümlük tasarım sunumu üzerine)
**Kapsam:** `CureoPrivate/plugins/socius-vigil/` (yeni) + `plugins/brand-ecosystem-core` stub'ı + marketplace kaydı
**Öncül (bloklayıcı):** `CureoHub/docs/superpowers/specs/2026-08-06-socius-vigil-mcp-v040-design.md` — Faz B'nin dört yeni aracı **deploy edilmiş** ve şemaları donmuş olmalı.

---

## 1. Neden bu spec var

`socius-vigil.skill` (v2.3.0) tek dosyalık bir beceri paketi: 456 satır SKILL.md, 13 mod,
16 kalite kapısı, 16 referans, 12 stdlib script, 4 JSON şema, evals. Bu hâliyle üç sorunu var:

1. **Kurulu kopya bayat.** `~/.claude/skills/socius-vigil` v1.2.0'da donmuş; v2.3.0 hiç kurulmamış.
   Sürüm yönetimi yok, dağıtım yolu yok.
2. **Modlar keşfedilemez.** 13 mod tek dosyanın içinde düz yazı; kullanıcı hangi modu nasıl
   çağıracağını bilmiyor ve her mod 456 satırın tamamını bağlama yüklüyor.
3. **Kapılar uygulanmıyor.** G1–G16 "protokol-düzeyi gözden geçirme" olarak tanımlı — yani
   modelin kendi disiplinine bırakılmış. Rapor uzadıkça atlanma olasılığı artar; özellikle **G16
   temiz-kopya** kapısı (okuyucu metninde teknik jargon sızıntısı) tam olarak bir modelin
   kendi kendine yakalamakta en kötü olduğu türden bir ihlal.

Plugin bu üçünü sırasıyla dağıtım, dekompozisyon ve **hook-uygulaması** ile çözer.

---

## 2. Değişmezler

Faz-B spec'inin I1–I7'si burada da geçerlidir; ek olarak:

| # | Değişmez |
|---|---|
| **P1** | **Tek doğruluk kaynağı.** `references/`, `schemas/`, `scripts/`, `evals/` **yalnız** flagship skill dizininde bulunur. Mod skill'leri bunları çoğaltmaz; göreli yolla atıf verir. |
| **P2** | **Hook'lar fail-open.** Hiçbir hook MCP çağrısını bloklamaz, hiçbir turu reddetmez. `Stop` hook'ları `decision:"block"` + gerekçe ile turu **tamamlatır**, iptal etmez. `stop_hook_active` döngüyü kırar. |
| **P3** | **Meta-tur baskılaması.** Hook'lar, plugin'in *kendi kodu* üzerinde çalışılan oturumlarda ateşlenmez (vekayinüvis F9 dersi). Tetikleme yalnız gerçek artefakt imzasıyla. |
| **P4** | **Degrade beyanı.** Bir connector bağlı değilse ilgili katman atlanır **ve manifestoda gerekçesiyle beyan edilir** — sessiz atlama yasak, uydurma yasak. |

---

## 3. Dizin yapısı

```
plugins/socius-vigil/
├── .claude-plugin/plugin.json          v1.0.0
├── .codex-plugin/{plugin.json,openai.yaml}
├── .mcp.json                           çekirdek filo
├── .mcp.optional.json                  sektör/sağlık genişletme (belgelenir, otomatik yüklenmez)
├── CONNECTORS.md · README.md · CHANGELOG.md
├── shared/
│   ├── context-economy-contract.md     Tier 0/1/2 + sharding
│   └── coverage-manifest.md            G0 kapsam manifestosu grameri
├── skills/                             13 skill = 13 slash komut
│   ├── socius-vigil/                   ◆ FLAGSHIP — protokol gövdesi
│   │   ├── SKILL.md                    v2.4.0 (§0–§14, G1–G16)
│   │   ├── references/01..16.md        16 referans (P1: tek kopya)
│   │   ├── schemas/*.json              4 şema
│   │   ├── scripts/*.py                12 stdlib script (native düşüş)
│   │   └── evals/                      regresyon vakaları
│   ├── start/ · durum/
│   ├── pazar-raporu/ · hizli-tarama/
│   ├── voc/ · rakip/ · fiyat/ · trend/ · kol/ · perakende/ · vijilans/
│   └── yayin/
├── agents/
│   ├── pazar-tarama-distilleri.md
│   ├── vijilans-triyaj.md
│   └── rapor-denetcisi.md
├── hooks/
│   ├── hooks.json
│   ├── scripts/{session_start,retrieve_dont_dump,sv_ledger,stop_gates,clean_copy_guard}.py
│   ├── scripts/{_signals,_turn_tools}.py
│   └── tests/test_*.py                 pytest
└── scripts/socius_doctor.py
```

---

## 4. Skill dekompozisyonu

**Kural:** flagship protokol gövdesini taşır; her mod skill'i **≤120 satır** ve şu altı başlıktan
oluşur — *ne zaman tetiklenir · hangi `sv_*` sırası · hangi çerçeve · hangi rapor bölümü · hangi
kapılar · degrade yolu*.

| Skill (`/socius-vigil:<ad>`) | Mod | Araç sırası | Çerçeve → Bölüm | Kapılar |
|---|---|---|---|---|
| `socius-vigil` | **flagship protokol** — gövde, §0–§14, G1–G16, referans/şema/script sahibi | — | tümü | G1–G16 |
| `start` | oryantasyon | `sv_source_inventory` opsiyonel | filo kadrosu + mod seçim ağacı | — |
| `durum` | teşhis | `tools/list` + `socius_doctor.py` | connector canlılığı, araç yüzeyi (18), SECTION_MAP tutarlılığı | — |
| `pazar-raporu` | `MARKET_INTELLIGENCE_REPORT` **(amiral gemisi)** | `sv_build_query_library` → `sv_source_inventory` → `sv_search`/`sv_fetch` → `sv_retail_review_scan` → `sv_retail_filter` → `sv_extract_reviews` → `sv_sentiment` → `sv_market_synthesis` → `sv_admiralty_score`/`sv_triangulate` | tam çerçeve seti | G1–G16 |
| `hizli-tarama` | `QUICK_SCAN` | `sv_collect_pipeline` (tek çağrı) → `sv_sentiment` | net sentiment + tema → §0, §3–§4 özet | G2, G9, G12 |
| `voc` | `VOICE_OF_CUSTOMER` | `sv_retail_review_scan` → `sv_retail_filter` → `sv_extract_reviews` | VoC/Kano → §5 (+§3.5) | G9, G11, G13 |
| `rakip` | `COMPETITIVE_POSITIONING` | `sv_build_query_library` (rakip seti) → `sv_search` → `sv_sentiment` → `sv_market_synthesis` | SoV→ESOV, STP, beyaz alan → §3, §7 | G2, G3, G13, G14 |
| `fiyat` | `PRICING_PERCEPTION` | `sv_extract_rating` → `sv_extract_reviews` (fiyat faseti) | değer-fiyat algısı → §3.5, §5 fiyat kesiti | G9, G11 |
| `trend` | `TREND_SCAN` | `sv_search` (zaman pencereli) → `sv_extract_reviews` (hız/burst) | kategori yörüngesi + talep → §6 | G2, G3, G9 |
| `kol` | `KOL_STANCE_AND_VALUATION` | `sv_search` (KOL keşfi) → **`sv_kol_stance`** → `sv_admiralty_score`/`sv_triangulate` | profil×duruş + değerleme → §8 | **G15**, G3, G4 |
| `perakende` | `RETAIL_REVIEW_MINING` | `sv_retail_review_scan` → **`sv_retail_filter`** → `sv_extract_reviews` → `sv_extract_rating` | puan dağılımı, doğrulanmış satın alma, sahte-yorum sezgisi → §3.5 | **G11**, G9, G10 |
| `vijilans` | `VIGILANCE_SWEEP` + `ESCALATION_TRIAGE` + pediatrik overlay | `sv_extract_reviews` → `sv_icsr_check` → `sv_admiralty_score` → `sv_ach_matrix` | ICSR 4-kriter, Admiralty, ACH, eskalasyon → §10 | **G4, G5, G8**, I3 |
| `yayin` | §11.5 **temiz-kopya geçişi** | **`sv_quality_gate --profile clean --annex`** | iki-artefakt ayrıştırma → Okuyucu Raporu + TSE | **G16**, G7, G12 |

**Fold edilen utility modlar:** `SOURCE_INVENTORY` ve `QUERY_BUILD` ayrı skill olmaz — tek araç
çağrısıdırlar; `start` tanıtır, `pazar-raporu` adım 3–4'te kullanır. `PEDIATRIC_SAFETY_OVERLAY`
bir *modifiye edici*dir → `vijilans` içinde `references/14` ile.

**Tetikleyici çakışması:** 13 skill'in `description` alanları **ayrık** anahtar kelime kümeleri
taşımalı; flagship en genel ("pazar araştırması", "sosyal dinleme") olur, mod skill'leri dar
("ses payı", "yorum analizi", "advers etki sinyali"). `durum` skill'i bu ayrıklığı denetler.

---

## 5. SKILL.md v2.3.0 → v2.4.0 değişiklikleri

Zorunlu (aksi hâlde protokol gövdesi gerçeklikten sapar):

1. **§2 araç tablosu 14 → 18.** Dört yeni satır; native-düşüş sütunu dolu
   (`kol_stance.py`, `market_synthesis.py`, `retail_filter.py`, `quality_gate_check.py`).
2. **§2.1'deki "bilinen artık MCP bulguları"** (SV-FIX-01b / 02b) bloğu **kaldırılır** — ampirik
   olarak kapalı (v0.3.1, `test/core/sv_fixes.test.ts`). Yerine Faz-A denetiminin verdikti + kalan
   P2 backlog'u yazılır. Defense-in-depth çapraz-doğrulama **korunur** (kusur-telafisi değil,
   ilke olarak).
3. **§12 kapı tablosuna "uygulama" sütunu:** her kapı için `hook` · `sv_quality_gate` ·
   `protokol-düzeyi` etiketi. Hangi kapının makineyle yakalandığı okuyucuya açık olur.
4. **§13 Composability:** `brand-market-signal` artık downstream değil — emekli; `brand-audit`
   upstream olarak kalır.
5. **§14 script kataloğu:** dört script'in artık **hem** MCP aracı **hem** native düşüş olduğu.
6. `skill-manifest.yaml`: `skill.version: 2.4.0`, `runtime.mcp_servers` Social Listening satırı
   18 araç, `verification.gates` değişmez (G1–G16 aynı), `build.release_name` güncellenir.

---

## 6. Alt-ajanlar

Üçü de izole bağlam penceresinde koşar; ana pencereye **yalnız damıtılmış** sonuç döner.

### 6.1 `pazar-tarama-distilleri`
- **Ne zaman:** `pazar-raporu` · `rakip` · `trend` gibi onlarca `sv_*` çağrısı gereken modlar.
- **Sharding:** ≤4 paralel çağrı; bölme ekseni **pazar × dil** (platform değil — aynı platformun
  farklı dilleri farklı sinyal taşır, aynı dilin farklı platformları örtüşür).
- **Döner:** tek `sv_distillate` zarfı — ≤20 bulgu (her biri: kaynak · dil · platform · URL ·
  tarih · özet ≤2 cümle · Admiralty ön-notu) + `coverage` (server × `hit|empty|degraded|skipped:<gerekçe>`).
- **Yasak:** ham JSON, tam-metin blok, tam URL listesi ana pencereye sızmaz.
- **Araçlar:** tümü; `disallowedTools: Write, Edit`.

### 6.2 `vijilans-triyaj`
- **Ne zaman:** sağlık rejimi açık **ve** yorum korpusunda AE adayı var.
- **Gerekçe:** WEB-RADR — ürün terimiyle eşleşen gönderilerin <%2'si kişisel AE, aday AE'lerin
  ~%40'ı gerçek. Yüzlerce adayı ana pencereye dökmek hem taşırır hem yanlış-pozitifle sentezi bozar.
- **Yapar:** her aday için `sv_icsr_check` + `sv_admiralty_score`; ambigü olanlar için
  `sv_ach_matrix` (varsayılan 4 hipotez: gerçek UE / yanlış kullanım / astroturfing /
  ilgisiz-eşzamanlı).
- **Döner:** §10 tablosuna doğrudan girecek satırlar + elenenlerin **sayısı ve gerekçe dağılımı**
  (eleme şeffaflığı → §13). Her satır `requires_human_review:true` (I3).
- **Yasak:** vaka dosyalama önerisi, nedensellik iddiası. `disallowedTools: Write, Edit`.

### 6.3 `rapor-denetcisi`
- **Ne zaman:** `yayin` geçişinden **sonra**, teslimden **önce**.
- **Yapar:** `sv_quality_gate --profile clean --annex <TSE>` koşar, çıktısını **yorumlar**
  (heuristik denetleyicinin yakalayamadığı P2/P5 ihlallerini — eksiksiz cümle, anlatım akışı,
  çerçeveleyici metin — kendi okumasıyla ekler).
- **Döner:** ≤1 sayfa öncelikli düzeltme listesi (Kritik / Önemli / Küçük), her madde konum + tek
  cümlelik gerekçe.
- **Yasak:** düzeltmeyi kendisi yapmaz. `disallowedTools: Write, Edit` (edupedia:module-auditor deseni).

---

## 7. Hook katmanı

`hooks/hooks.json` — P2 gereği tamamı fail-open, P3 gereği meta-tur baskılamalı.

| Event / matcher | Script | Davranış |
|---|---|---|
| `SessionStart` `startup\|resume\|clear\|compact` | `session_start.py` | Connector preflight: `SOCIUS_VIGIL_MCP_API_KEY` + companion anahtarları. Doktrin enjeksiyonu: MCP-toplar/skill-yorumlar sınırı · **WEB-RADR invaryantı (I3)** · no-fabrication (I2/G9) · iki-artefakt çıktı (§11.5) · Tier 0/1/2 bağlam ekonomisi · mod seçim ağacı. Anahtar yoksa **degrade yolunu söyler**, oturumu kesmez. |
| `PostToolUse` `mcp__socius-vigil__.*` | `retrieve_dont_dump.py` | Gövde **>6 KB** → `pazar-tarama-distilleri`'ye yönlendir; **>30 KB** → `anamnesis` ingest→bounded query (bağlı değilse bounded-chunk + evidence_ledger'a çök). Advisory. |
| `PostToolUse` `mcp__socius-vigil__.*` | `sv_ledger.py` | **G7/G12'yi uygulanabilir kılan parça.** Her çağrıdan `tool · provider · degraded · gaps · enriched_by · enrichment_note · timestamp` çekip **tur-yerel deftere** yazar (`mcp_tool_ledger.schema.json` uyumlu). `ae_candidate` / `valid_icsr` görürse I3 invaryantını + eskalasyon eşiklerini (≥C3 / ≥B2; MDR ≤15 gün; kozmetovijilans SUE ≤20 takvim günü) hatırlatır. |
| `Stop` | `stop_gates.py` | Substantif rapor imzası varsa defteri okuyup denetler: **G12** (defter dolu; **18 kanonik ad dışı `sv_*` = uydurma araç → ihlal**), **G9** (no-fabrication beyanı), **G13** (minimum eksen: talep/SoV + sentiment + VoC + konumlandırma), **G14** (§12 RACI + kanıt çapası), **G10** (çok-SKU etiketleme). Eksikse tamamlatır. |
| `Stop` | `clean_copy_guard.py` | **G16 — doktrinin dişleri.** Okuyucu Raporu imzası varsa yasaklı jeton taraması: `sv_*` · "MCP" · parantezli `G\d+` · `SV-FIX` · script/şema dosya adı · **görünür** (HTML yorumu dışı) "VIZ" · doldurulmamış `[köşeli parantez]`. Sızıntı varsa konumuyla tamamlatır. |
| yardımcı | `_signals.py` · `_turn_tools.py` | Rapor/mod imza tespiti, transkript erişimi, tur-yerel defter I/O. |

### 7.1 Tetikleme imzaları (P3 — yanlış-pozitif kontrolü)

`clean_copy_guard` ve `stop_gates`, plugin'in kendi kaynak dosyaları üzerinde çalışılırken
**ateşlenmemelidir**. vekayinüvis'in F9 dersi doğrudan uygulanır:

- **Güçlü imza (gerekli):** son asistan mesajında `# Pazar Zekâsı Raporu` başlığı **ve** en az üç
  `## <n>.` numaralı bölüm başlığı.
- **Baskılayıcı:** mesaj birden çok mod adını anıyor **veya** plugin-iç dosya adı (`hooks/`,
  `SKILL.md`, `*.tool.ts`) taşıyor **ve** hiçbir kaynak künyesi yoksa → meta-tur, sessiz kal.
- **Transkript varsa** `sv_*` aracının gerçekten çağrıldığı doğrulanır (kesin sinyal); transkript
  yoksa yukarıdaki metin-yedeği kullanılır.

Bu üç kural **pytest ile mutasyon-denetimli** test edilir (§10).

---

## 8. MCP kablolaması

### `.mcp.json` — çekirdek (otomatik yüklenir)

| Server | Tier | Rol |
|---|---|---|
| `socius-vigil` — `https://socius-vigil-mcp.cureonics.workers.dev/mcp`, Bearer `${SOCIUS_VIGIL_MCP_API_KEY}` | **core** | 18 araç: toplama + deterministik skorlama omurgası |
| `exa` | support | Yorum keşfi + temiz tam-içerik; `sv_search`/`sv_fetch` düşüşü |
| `tavily` | support | Geniş web tarama + extract; kaynak keşfi |
| `anamnesis` — Bearer `${ANAMNESIS_MCP_API_KEY}` | **substrate** | Tier-2 bağlam ekonomisi; anahtar yoksa bounded-chunk'a degrade |

### `.mcp.optional.json` — sektör/sağlık genişletmesi (belgelenir, elle etkinleştirilir)

`tripadvisor` (otel/seyahat/F&B — claude.ai connector, kullanıcı-bağlı) · `pubmed-epmc` ·
`consensus` · `clinical-trials` (AE klinik plausibility) · `titck` (TR ruhsat bağlamı) ·
`thoughtspot` (IQVIA MIDAS → **SoM**, ESOV hesabının tek gerçek girdisi).

**CONNECTORS.md** her satır için: rol · gerekli anahtar · **bağlı değilse ne olur** (hangi kapı
N/A'ya düşer, hangi metrik `not_provided` olur). Ayrıca `sv_quality_gate`'in rapor gövdesini
kullanıcının kendi worker'ına gönderdiği açıkça yazılır.

### `plugin.json` `userConfig`
`socius_vigil_api_key` · `exa_api_key` · `tavily_api_key` · `anamnesis_api_key` — hepsi
`required:false`, `sensitive:true`. **Vekayinüvis'teki belgelenmiş tuzak tekrar yazılır:**
`.mcp.json` header'ı `${ENV_VAR}` okur; `userConfig`→env fallback sözdizimi belgelenmemiştir, yani
alanı doldurmak tek başına header'ı beslemez — değer ayrıca ortam değişkeni olarak dışa aktarılmalı.

---

## 9. `brand-market-signal` emekliye ayırma

`plugins/brand-ecosystem-core/skills/brand-market-signal/SKILL.md` ≤30 satırlık yönlendirme
stub'ına indirgenir.

**Korunacaklar (kırılmasın diye):**
- `name: brand-market-signal` ve frontmatter'daki **tüm tetikleyici anahtar kelimeler** — mevcut
  kullanıcı alışkanlığı ve brand-audit'in iç atıfları çalışmaya devam eder.
- **Marka-özel handoff sözleşmesi:** beyaz alan → `brand-maker` naming brief'i. Bu bilgi
  socius-vigil'de **yok**; stub'da kalır.

**Gövde:** "Bu iş artık `/socius-vigil:rakip` (SoV + konumlandırma + beyaz alan) ve
`/socius-vigil:pazar-raporu` (tam rapor) tarafından yapılır. socius-vigil plugin'i kurulu değilse
… (kurulum satırı)." Fabrikasyon yasağı cümlesi korunur.

`brand-ecosystem-core/.mcp.optional.json`'daki `socius-vigil` girdisi **kalır** (stub yoksa bile
brand-audit opportunistik kullanabilir), `_role` metni yeni sınırı anlatacak şekilde güncellenir.

---

## 10. Doğrulama

| Kapı | Komut / eylem | Geçme ölçütü |
|---|---|---|
| Hook birim testleri | `pytest plugins/socius-vigil/hooks/tests` | tümü yeşil; en az: imza tespiti, **meta-tur baskılaması**, defter parse, G16 jeton taraması, fail-open (script çökerse tur devam eder) |
| Plugin yapısı | `plugin-dev:plugin-validator` | temiz |
| Araç adı senkronu | `socius_doctor.py` → canlı `tools/list` ↔ hook'un kanonik listesi ↔ `.mcp.json` `_role` | **18** ve birebir aynı ad kümesi |
| Skill tetikleyici ayrıklığı | `socius_doctor.py --skills` | 13 skill'in `description` anahtar kelime kümeleri arasında beklenmeyen çakışma yok |
| SECTION_MAP tutarlılığı | `socius_doctor.py --sections` | mod skill'lerinin bölüm atıfları `references/13` ile uyumlu |
| Kurulum | plugin kur → `enabledPlugins` teyidi | **sessiz düşme tuzağı** — kurulum sonrası mutlaka doğrula |
| Canlı oryantasyon | `/socius-vigil:durum` | connector'lar + 18 araç + degrade yolları doğru raporlanıyor |
| Uçtan uca | `evals/bioderma_atoderm_creme_fr.md` referans vakası: `pazar-raporu` → `yayin` → `rapor-denetcisi` | Okuyucu Raporu + TSE ayrık üretiliyor; `sv_quality_gate --profile clean` **blocking_failures boş** |
| Bayat kopya | `~/.claude/skills/socius-vigil` (v1.2.0) kaldırılır | plugin onu ikame eder; iki kopya çakışmaz |

---

## 11. Riskler

| Risk | Azaltım |
|---|---|
| **G16 hook'u kendi geliştirme oturumlarını bloklar** | §7.1 sıkı imza + meta-tur baskılayıcı, baştan teste bağlı; P2 gereği zaten bloklamaz, tamamlatır |
| 13 skill protokolden sürüklenir | P1 (tek kopya) + `durum` skill'inin SECTION_MAP denetimi |
| Araç sayısı 6 yerde ayrışır | Kardeş spec §6: `TOOL_NAMES` tek kaynak; burada `socius_doctor.py` canlı `tools/list` ile karşılaştırır |
| `brand-market-signal` stub'ı mevcut kurulumları kırar | Aynı `name` + aynı tetikleyiciler; yalnız gövde değişir |
| Tetikleyici çakışması yanlış skill'i açar | Ayrık anahtar kelime kümeleri + `durum` denetimi; flagship en genel, modlar dar |
| Anahtarsız kullanıcı sessiz boş rapor alır | P4 — `session_start.py` preflight uyarısı + her çıktıda G0 kapsam manifestosu |
| Python↔TS parite kayması (script değişir, TS kalır) | Kardeş spec §7 parite testi; script değişikliği fixture yenilemeyi zorunlu kılar — bu spec'e de kayıtlı |

## 12. Kapsam dışı

- MCP sunucu kodu — kardeş spec.
- Yeni pazar-araştırması çerçevesi icat etmek; `references/11`'deki set korunur.
- `carbon-html-report` / `carbon-pptx` render entegrasyonu — opsiyonel downstream, varsayılan çıktı inline Markdown.
- Firecrawl/Nimble derin-scrape connector'ı — opsiyonel harici eskalasyon olarak belgede kalır.
- Public marketplace yayını — CureoPrivate özel deposunda kalır.
