# cureolex — sürüm geçmişi

## 4.0.0

**Sürüm 4.0.0 (2026-09-24) — çekirdek / yargı bölgesi paketi ayrımı.** "Diğer ülkelere taşımak bir çeviri işi değil, yeniden mimarlama işidir" planının kod olarak uygulanabilen kısmı. (1) `jurisdictions/`: paket şeması + **TR paketi (active — 3.9.0 davranışının birebir tanımı, gerileme yok)** + **GB · DE · CH taslak paketleri** (bayraklar 2026-09-24'te birincil kaynağa karşı ölçüldü; DE kaynağı bu makineden erişilemediği için temkinli). (2) Kimlik modeli: `jurisdiction` ISO 3166-1/2 + `ORG:` ulusüstü ad alanı (`ORG:AU` Afrika Birliği ≠ `AU` Avustralya; `UK`→`GB` eski takma ad), `id_kind` += akn · ecli · urn-lex · `x-<ad>`. (3) Bağlayıcı sözleşmesi (9 soyut yetenek; düzey A/B/C). (4) Beş yetenek bayrağı → **güven tavanı** (CC-1…CC-8; `confidence_label.confidence_ceiling`). (5) Yeni kapılar **G10 güncellik / belirli-tarihte-yürürlük** ve **G11 yargı bölgesi tutarlılığı** (plan G10'u var sanıyordu ve G12 diyordu — cureolex'te yalnız G0–G9 vardı; G10–G16 socius-vigil'e aittir). (6) Evrensel legistik rubrik: 12 aile, R6b'nin 21 kontrolü eşlendi — TR'de **geçiş hükümleri ailesinin kontrolü yok** (uydurma K-22 eklenmedi, kapsama boşluğu olarak beyan edilir). (7) Yeni modlar **REGULATORY_MATURITY** (WHO GBT: RS + MA/VL/MC/LI/RI/LT/CT/LR) · **TRANSPOSITION** · **RELIANCE_FRAMEWORK**; Mod 8'in kanonik adı `PARLIAMENTARY_BILL` (`TBMM_KANUN_TEKLIFI` takma ad olarak çalışmaya devam eder). (8) HTA kurum haritası evidentia'ya bağlamla aktarılır + karşılaştırmalı bağlam-uygunluk kontrolü. (9) `tests/validate_packs.py` (yayım kuralı · tam-bir-kez dosya sahipliği · parça aynası · tavan hesabı · G11 statik denetimi) + 12 TR altın/adversarial vaka (mülga hüküm · uydurma RG sayısı · yanlış mahkeme hiyerarşisi · yargı karışması · bağlayıcı uygunluğu). Önceden kırmızı olan hook testi (sabit yazılmış sunucu sayısı, kilit bir bağlayıcı kaldırılınca bayatlamıştı) artık kilitten türetiliyor. **Kod olmayan kalemler ertelendi** (uzman paneli, yerel hukuk ortağı, AKN dönüştürücü, yeni ülke adaptörleri, GBT gösterge veri seti): `docs/superpowers/specs/2026-09-24-cureolex-yargi-paketleri-tasarim.md` (kaynak depo).

## 3.9.0

**Sürüm 3.9.0 (2026-09-07):** Stop hook kapsam daraltması — G0 manifesto kapısı artık metin sezgisiyle değil DAVRANIŞLA tetiklenir (`_turn_tools.fleet_data_tool_invoked`); mühendislik/inceleme turları ("gerekçe", "madde 4.3") ve sıradan İngilizce kelimeler ("draft/analyze/comply/amend") artık reform çıktısı sanılmıyor. Bölüşüm vekayinuvis + historia-medicinae ile hizalandı.

## 3.8.7

Cursor native MCP Bearer `${env:VAR}` process-env interpolasyonu (`.cursor-plugin/mcp.json`).

## 3.8.6

**Sürüm 3.8.6 (2026-08-18):** İkinci semantik geçiş — canlı yeteneklerin sıraya emilmesi: uk-legal `legislation_*` (httpx fix), UHRI HP indexer (`uhri_search`/`uhri_fetch_document` Md.90 sonrası zorunlu), fedlex Vernehmlassung RIA-only, mevzuat 0.15.1 `phrase`/`search_within`/bedesten gerekçe (ikincile gövde yok), german free-tier EU korunur. Stale skip'ler (UHRI exclude, `legislation_* yok`, Open Law-only UK) temizlendi.

## 3.8.5

**Sürüm 3.8.5 (2026-08-17):** Tam-filo araç ince ayarı — `tools_used` genişletildi (mevzuat list_*/detail/kurumlar, RG pdf/info, sb birimler/taslaklar, health-policy keşif araçları, oecd 9/9 + GOV_REG, yok/detsis omurga); distiller semantik sıra (ANALYZE→DRAFT, german resolve→EU, TBMM sira_no→gerekçe gövdesi, ich M4/M8, eudamed≠ÜTS); `conscious_excludes` tek yerde. **2026-08-18:** fedlex Vernehmlassung RIA'ya alındı.

## 3.8.4

Claude Code `plugin.json` agents dosya listesi; Türk Patent emekli → 21 server.

## 3.8.3

**Sürüm 3.8.3 (2026-08-16):** marketplace yüzey wiring — `.claude-plugin/plugin.json` artık `mcpServers` / `hooks` / `skills` / `commands` / `agents` bildirir; native `.cursor-plugin/plugin.json`; Codex `openai.yaml` `.codex-plugin/` altına taşındı; `CONNECTORS.md` Claude Code / Cursor / claude.ai / ChatGPT ayrımını sabitledi (web'de hook yok, MCP elle connector). Distiller `tools:` allowlist'ine Cursor tireli önek (`mcp__plugin-cureolex-<server>__*`) eklendi.

## 3.8.2

**Sürüm 3.8.2 (2026-08-14):** OpenAthens `oa_fetch_pdf(doi|url)` ve Anna's Reader `download_document(id=DOI|MD5)` S4 tam-metin shard'ına eklendi; kısa-ömürlü resource link, SHA-256/provenance ve anamnesis bounded-analysis disipliniyle. Legal-first sıra ve Anna's yalnız-analiz kapısı değişmedi.

## 3.8.1

2026-08-08 ölçümü: **german-law free-tier haritası düzeltildi** (AB ailesinin 5'i de ÇALIŞIYOR; yalnız case-law/preparatory/version-tracking kapalı) + çözücü tuzakları belgelendi (`get_provision` yalnız `{id}` biçimiyle, `validate_citation` AMG'yi doğrulayamıyor); **DÖRDÜNCÜ arıza katmanı** (boş gövde `null`/`{}`/`[]` = arıza) + `check_drift` companion **ad-listesi** kapısı ve kök marketplace açıklamasının taranması.

## 3.8.0

**fedlex + uk-legal wire'landı** (aynı desen; `mcp-oauth-gateway` genelleştirildi), Fedlex Swiss + Türk Patent companion'dan emekli → filo o kesitte 23-sunucu / 3 companion; SSE yanıt çerçevesi artık JSON-RPC `id` ile seçilir (yanlış-yeşil onarımı) + fleet.yaml yinelenen-anahtar kapısı.

## 3.7.0

**eurlex wire'landı** (HP self-host, upstream pinli, önünde OAuth kapısı) → **G6 companion'dan kurtuldu, hard PASS**.

## 3.6.0

Open Law + Fedlex için **programatik yedek** (ep.legislation_uk / ep.fedlex_sparql) — companion'a bağımlılık kırıldı.

## 3.5.9

**Türk Patent companion'dan wire'a**; ÜÇÜNCÜ arıza katmanı (`isError:false` ama GÖVDEDE `error` → sessiz yanlış-negatif).

## 3.5.8

**araç-düzeyi canlı kapı** (`check_tools.py`: `tools_used` beyanı ↔ canlı `tools/list`, + `--call` duman testi) — 3 fantom araç düzeltildi.

## 3.5.6

2026-08-07 denetimi: **connector ad-eşleme katmanı** (`tool_prefixes` — aynı sunucu Claude Code'da `mcp__<ad>__`, claude.ai'de `mcp__claude_ai_<Görünen_Ad>__` yüklenir; ajan `tools:` allowlist'i sert olduğu için eşleşmezse sunucu ajan için YOKTUR), 2 komutun geçersiz YAML frontmatter'ı, `tests/run_suites.py` (70 vaka), shard/kapsam/companion sözleşme tablolarının fleet'e bağlanması.

## 3.5.5

`shared/` skill'in içine alındı (claude.ai düzleştirilmiş paketinde `../../shared/` çözülmüyordu).

## 3.5.4

2026-08-06 denetimi: ölü `lex-sanitas-mcp` adı registry/healthcheck/testlerden ayrıldı (uç 404), `mevzuat-bilgisi` devralma kuralı yazıldı, `check_drift` [6] sunucu-kimliği kapısı eklendi.

## 3.5.0

**türetilmiş filo**: `fleet.yaml` tek kaynak → `.mcp.json`/codex/lock/komut/ajan türetilir + `tools/fleetkit/check_drift.py` sürüklenme kapısı; **canlı MCP prob'lu preflight** (`auth_missing` ≠ `unauthorized`); **titck Bearer gate onarımı** (2026-08-02 kapılanması kaçırılmıştı → katman 401 alıyordu); filo **15→19** (yoktez + literatur + openathens + annas-reader wire), companion **6→5** (yoktez first-class'a terfi → **G7 hard PASS**); distiller ajanlarına shard-tabanlı araç kısıtı; kök `hooks.json` kopyası kaldırıldı.

## 3.4.0

Fedlex Swiss/YokTez/Türk Patent **zorunlu companion kategorisine terfi**: manifesto satırları her çıktıda zorunlu (bağlam yoksa `skipped: mod için N/A`); Stop-hook zorunlu satır sayısı **sabit olmaktan çıkıp `fleet.lock.json`'dan türer** (companions + delegations = **7**; eski düzyazıdaki “5→8” yanlıştı).

## 3.3.0

**koşullu companion katmanı**: Fedlex Swiss (Mod7 CH birincil metin — Ansvar CH satırı çerçeve-teyide düşer) + YokTez (tez doktrini + G7 YÖK-Tez atıf doğrulama) — bağlıyken ilgili bağlam tetiklenince zorunlu; connector önek-eşleştirme notu (`mcp__<Ad>__*` / `mcp__claude_ai_<Ad>__*`).

## 3.2.0

health-policy **semantic_search** doğal-dil giriş kapısı (çok-dilli keşif US/JP/AU/CN → fetch ile doğrulama), in-plugin **legal-distiller** ajanı, `start`→`cureolex-start` skill yeniden adlandırması, hook test harness'ı + PostToolUse devre-kesicinin `additionalContext` kanalına taşınması.

## 3.1.0

bağlam-tetiklemeli ZORUNLU entegrasyon: evidentia/sci-audit kuruluysa atlanamaz; companion'lar (Yargı↔G5, Open Law↔G6, Ansvar↔Mod7) tam-filonun zorunlu üyeleri.

## 3.0.0

Formerly **Lex Sanitas**. Eski `lex-sanitas` skill'inin (v2.9.0) mirasçısı. Yabancı-ülke mevzuat tarama işlevi ayrı bir MCP'ye (**health-policy**) taşındı; bu plugin onu *bir kaynak katmanı* olarak wire eder. plugin mimarisi + tam-filo aktivasyonu.
