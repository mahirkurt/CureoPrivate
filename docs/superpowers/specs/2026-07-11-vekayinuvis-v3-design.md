# Vekayinüvis v3.0.0 — devarsiv tam-entegrasyon + filo genişlemesi + mimari göç

**Tarih:** 2026-07-11 · **Durum:** Onaylandı (kullanıcı; kapsam=core+high, sepet=yumuşak kapı,
komut adları=kır-temizle, userConfig=6 anahtar)
**Kapsam:** `CureoPrivate/plugins/vekayinuvis/` (v2.5.0-uncommitted → v3.0.0)
**Girdi:** 10-ajanlık keşif/araştırma workflow'u (wf_3d113e0c) — plugin haritası, 29 maddelik
upgrade kataloğu (7 core / 12 high / 10 nice), 4 iş-akışı tasarımı, dijital-Osmanlı araştırması.

## 1. Amaç

Vekayinüvis'i devlet-arsivleri-mcp'nin yeni 22-araç yüzeyiyle (eSatış sepeti → Access-kapılı
noVNC insan-ödemesi → BOA-kodlu yerel PDF arşivi → çift-motor OCR/HTR → async job katmanı)
tam entegre etmek; araştırmadan çıkan yeni işlevleri (filo genişlemesi, HTR model seçimi,
kanıt-disiplini kalıpları) eklemek; plugin mimarisini 2026 şemasına taşımak.

## 2. Zemin (keşif bulguları — özet)

- Plugin v2.5.0 TAMAMEN uncommitted (son commit v2.4.0); devarsiv bilgisi 10-araç döneminde
  donmuş. Canlı sunucu **22 araç** servis ediyor (bu oturumda deploy+doğrulandı); claude.ai
  connector listesi yeniden bağlanınca tazelenir.
- Bilinen BUG: `hooks.json` SessionStart matcher'ında `clear` eksik → `/clear` sonrası
  preflight hiç koşmuyor.
- `references/htr-workflow.md` devarsiv'den tamamen habersiz; `report-template.md` bayat
  "BOA tam metin taraması mevcut değildir / on-site erişim" örneklemi taşıyor (rapora sızar).
- `.codex-plugin/plugin.json` mcpServers bloğunu `.mcp.json`'dan INLINE kopyalıyor
  (çift-bakım tuzağı — her .mcp.json değişikliği iki yerde yapılır).
- Kök `hooks.json` inert duplicate; `agents/openai.yaml` yabancı dosya.
- Doğrulanmış kamu Transkribus modelleri: 56496 OttomanTurkish_generic (~CER %12, üretimde),
  **169801 Ottoman Fatwa Manuscript (CER %5.94)**, **52502 OttomanTurkish_Print_1 (CER %7.2)**.
- Transkribus 56496 taşra-kâtibi ellerinde gürültülü (2026-07-09 canlı gözlem) → görü-birincil
  protokol şart. eScriptorium motoru BASILI-Osmanlıca (OpenITI print, seg pk2/rec pk1).

## 3. Kararlar

| Karar | Seçim |
| --- | --- |
| Kapsam | **core+high tek v3.0.0**; nice yalnız kısa referans-notu (Wikilala manual_required, Qalamos probu, safety-degrade, DUDU teyit notu); gazetteer/NER + MAKHZAN + deneysel hook'lar → v3.1 |
| Sepet güvenliği | **Yumuşak kapı** — PreToolUse hook YOK; skill/komut metni `list_cart` doğrula → açık kullanıcı onayı → `checkout_cart`. Bütçe rehberi komut metninde (ops. `.claude/vekayinuvis.local.md` konvansiyonu) |
| Komut adları | **Kır-temizle** — commands→skills göçünde önek düşer (`/vekayinuvis:durum`); README/CHANGELOG migration notu |
| userConfig | **6 anahtar** (devarsiv/ottoman/yok-akademik/openathens/annas/anamnesis; sensitive+optional); toplam-uzunluk 2KB keychain kontrolü — sığmazsa öncelik devarsiv/ottoman/anamnesis + env-fallback notu |
| Deploy sırası | Plugin, branch'in 22-araç yüzeyini hedefler (sunucu zaten canlı); CureoHub branch merge'ü ayrı iş |

## 4. Tasarım

### §4.1 Mimari göç: commands → skills (H3)

- 10 legacy komut → öneksiz `skills/<ad>/SKILL.md`: `durum`, `arsiv-dalis`, `boa-katalog`,
  `kanun-gerekce`, `kaynak-avi`, `kronoloji`, `literatur`, `prosopografi`, `rapor`,
  `transkripsiyon`. `commands/` dizini kalkar; plugin.json `commands` alanı silinir.
- **3 yeni akış skill'i:** `satinalma`, `arsiv-oku`, `toplu-okuma` (aşağıda §4.3).
- Manuel-only akışlara `disable-model-invocation: true` (durum, rapor, satinalma);
  ağır fan-out akışlarına (arsiv-dalis, kaynak-avi, rapor) `context: fork` +
  `agent: arsiv-tarama-distilleri` yönlendirme notu.
- Frontmatter: `description` tetikleyicileri korunur; adlar kısa-kebap.

### §4.2 Devarsiv 22-araç senkronu (C1)

Normatif+pedagojik TÜM katmanlar branch yüzeyine eşitlenir:

- `skills/vekayinuvis/SKILL.md` §3.1.b: 10→22 araç tablosu — arama 5'lisi, belge 3'lüsü
  (`ocr_belge` `engine` paramıyla), sepet 4'lüsü (anotasyonlarıyla: `add_to_cart`=_RW,
  `remove_from_cart`=_DESTRUCTIVE, `list_cart`/`checkout_cart`=_RO), satın-alınmış/arşiv
  6'lısı, async 2'lisi, durum 2'lisi; `ocr_belge_pages` tablo tutarsızlığı giderilir.
- EVENT_RECONSTRUCTION moduna devarsiv wire edilir (tek devarsiv'siz mod kalmaz).
- `.mcp.json` `_role` metni + `.codex-plugin/plugin.json` inline kopyası BİRLİKTE.
- `CONNECTORS.md`: §2 "8 araç"→22; §4 snippet 13→17 server; §7 mod-map'e
  sepet/arşiv/async satırları; §8 preflight'a yeni araç probları.
- 9 references dosyasında bayat anlatı temizliği: `devlet-arsivleri-katalog.md`
  (envanter+akış+§7 motor tablosu+§8), `archive-landscape.md` (§8.1/§8.4 talimat→aksiyon),
  `htr-workflow.md` (devarsiv farkındalığı sıfırdan), `medical-history.md` (§7 reçeteler
  web_search→devarsiv_search/semantic_search), `kanun-gerekcesi-workflow.md` (TUR 1'e
  devarsiv), `report-template.md` (bayat erişim-notu örneklemi çıkar).

### §4.3 Dört yeni akış (C2–C5 + araştırma Akış A–F)

**`skills/satinalma/SKILL.md` (yumuşak kapı):**

1. **KARAR fazı (ücretsiz):** `get_belge` künye + `get_belge_image` görü + damga-OCR;
   karar matrisi: ilgi × derinlik (goruntu_sayisi) × kaynak-değeri × bütçe
   (~0,50 TL/sayfa TAHMİN; bağlayıcı tutar = `list_cart` Tutar sütunu).
2. **SEPET fazı:** `add_to_cart(item_id, hash, arsiv, pages)` (1-tabanlı cbk seçimi) →
   `list_cart` doğrulama → **metin-onay kapısı** ("şu N kalem, toplam ~X TL — onaylıyor
   musunuz?") → `checkout_cart` → YALNIZ noVNC URL'si
   (`https://devarsiv-vnc.cureonics.com/vnc.html`) + **"kendi cihazından kataloğa girme —
   tek-cihaz kilidi HP oturumunu düşürür"** uyarısı. Ödeme DAİMA insan.
3. **Ödeme-sonrası operatör adımı:** HP'de `scripts/build_archive.py` (Claude Code host'ta
   Bash ile; claude.ai host'ta kullanıcıya komut kutusu) → arşiv güncellenir.

**`skills/arsiv-oku/SKILL.md`:** `list_archive(query)` → code → `get_archive_page(code,
page)` 300 DPI + **asistan görüsü = birincil okuma** → `ocr_archive_pages` (≤5 sayfa sync)
→ `get_archive_pdf` künye. "Arşivde-varsa-arşivden-oku" önceliği tüm modlara işlenir
(önizleme sample yerine tam sayfa).

**`skills/transkripsiyon/SKILL.md` (göç + güçlendirme):** üç girdi tipi (katalog önizleme /
satın-alınmış arşiv sayfası / harici görüntü); **üç-sütun protokol**: Görü (birincil) |
Transkribus | eScriptorium — çelişkide görü kazanır, HTR alternatifi dipnot, gürültülü HTR
açıkça "kullanılmadı"; kredi ekonomisi (both yalnız değerli sayfada; keşifte
engine=tesseract/escriptorium); **model seçim tablosu**: el yazması→56496 (fetva/ilmiye→
169801), matbu→52502 (`DEVARSIV_TRANSKRIBUS_HTR_ID` alternatifi deploy notu).

**`skills/toplu-okuma/SKILL.md`:** sync/async karar kuralı (≤5 sayfa tek motor→
`ocr_archive_pages`; >5 veya both tam belge→`ocr_submit`); idempotent submit; poll
disiplini `ocr_result(include_text=false)`; done'da **tek-sefer** `include_text=true` →
anamnesis `ingest_document(doc_id="devarsiv:<code>")` → sonraki sorgular `hybrid_query`;
`stale`→resubmit (yeniden-indirme maliyeti yok). `shared/context-economy-contract.md`'ye
§6 async→ingest kuralı.

**Re-login runbook (C7):** `references/devlet-arsivleri-katalog.md` §3'e tam komut bloklu
runbook (chrome restart → geçici x11vnc/websockify → Tailscale noVNC → reCAPTCHA login →
`session_status` doğrula → kanal kapat); "Runtime Error 500 = çoğunlukla expired oturum →
re-login (bekleme değil)" kuralı; degrade-devam (katalog düşükken arşiv+anamnesis+akademik
katman çalışmaya devam eder).

### §4.4 Filo genişlemesi: 13 → 17 (+1 koşullu) (H2, H10, H11)

| Yeni server | Rol | Mod |
| --- | --- | --- |
| resmigazete-mcp | Erken-Cumhuriyet `/eskiler/` (1920+) + rg_resolve_date→rg_get_item + rg-ocr | KANUN_GEREKÇESİ, EVENT_RECONSTRUCTION |
| mevzuat-mcp | `search_mulga_mevzuat` + `get_mevzuat_gerekce` + `resolve_resmi_gazete` | KANUN_GEREKÇESİ |
| tbmm-mcp | Teklif→komisyon→kanun soyağacı; acikerisim DSpace geç-Osmanlı zabıtları | KANUN_GEREKÇESİ, SOURCE_HUNT |
| marmara-mcp | Tam-metin şelalesi Tier-3b: Turcademy Türkçe monograf + hukuk DB'leri (openathens→marmara→annas sırası) | HISTORIOGRAPHY, LITERATÜR |
| detsis (koşullu) | Kurumsal prosopografi: teşkilat soyağacı (resolve_birim→gecmis_birim→milestones→mevzuatlar); Cumhuriyet-sınırlı | PROSOPOGRAPHY |

detsis URL'si CLAUDE.md'de doğrulanmamış → implementasyonda canlı probe; geçmezse v3.1'e
düşer (spec bunu kabul eder). G0 kapsam manifestosu (`shared/coverage-manifest.md`),
`stop_coverage.py`, `session_start.py` preflight, doctor ve CONNECTORS yeni server sayısına
güncellenir. Auth: mevzuat SUITE_MCP_API_KEY-dostu; her yeni server `${ENV}` bearer
(userConfig'e girmez — 6-anahtar bütçesi mevcut çekirdek içindir).

### §4.5 Hook + doctor katmanı (C6, C7, H1, H7, H12)

- **BUG fix:** SessionStart matcher `startup|resume|clear|compact`.
- `session_start.py`: bayat "çok-sayfa hâlâ erişim-kapısında" metni çıkar; yeni
  konvansiyonlar (sepet=state-changing-ama-ödemesiz; checkout=yalnız-noVNC-URL; async çifti;
  engine konvansiyonu; arşiv-öncelikli okuma).
- `retrieve_dont_dump.py`: BIG_OUTPUT_TOOLS += `devarsiv_ocr_belge_pages`,
  `devarsiv_ocr_archive_pages`, `devarsiv_get_archive_pdf`, `devarsiv_ocr_result`
  (`devarsiv_get_archive_page` bilinçli istisna — görü ana pencerede okunur; yorumla).
- `citation_discipline.py`: provenance desenleri += `ocr_archive_pages|ocr_submit|
  ocr_result|job_id|get_archive_page|get_archive_pdf`; "both modunda iki motor ayrı
  raporlanır" kuralı (yanlış-pozitif önlenir).
- **Yeni hook — `PostToolUseFailure`** (matcher devarsiv araçları): `session_required` /
  `viewer_runtime_error` yanıtında re-login runbook'unu additionalContext olarak enjekte
  (Akış F'nin hook karşılığı). Deneysel `type:agent` atıf-verifier v3.1'e ertelendi.
- **Doctor** (`scripts/vekayinuvis_doctor.py`): `devarsiv_server_info` araç-envanter drift
  raporu (22 bekler; eksikse "connector'ı yeniden bağla" önerisi), `engines` durumu,
  `vnc_url` erişilebilirlik probu (Access 302 = sağlıklı), yeni 4-5 server probu,
  `--write-manifest` + hook cache evi `${CLAUDE_PLUGIN_DATA}` (sürüm-bağımsız state),
  clientInfo sürüm damgası 3.0.0.

### §4.6 Taşınabilirlik + hijyen (H4, H5, H6, H9 + nice-notlar)

- **userConfig:** 6 anahtar (devarsiv, ottoman-archives, yok-akademik, openathens,
  annas-reader, anamnesis) `sensitive: true, required: false`; `.mcp.json` header'ları
  `Bearer ${user_config.X:-${ENV_VAR}}` biçiminde env-fallback'li (destekleniyorsa; yoksa
  userConfig-öncelikli iki ayrı giriş REDDEDİLİR — tek mekanizma seçilir ve README'de
  belgelenir). Implementasyonda toplam-uzunluk ölçülür; 2KB keychain bütçesini aşarsa
  öncelik devarsiv/ottoman/anamnesis + kalanlara env notu.
- **Hijyen:** kök `hooks.json` silinir; plugin.json redundant default-path alanları
  (`commands`/`agents`/`skills` default'la aynıysa) sadeleştirilir; `agents/openai.yaml` →
  `.codex-plugin/`; dosya izinleri 644/755 normalize; marketplace entry `strict:false`
  kaldırılır; zip/doctor sürüm damgaları eşitlenir.
- **Distiller ajan modernizasyonu:** frontmatter'a `disallowedTools` (Write, Edit,
  `devarsiv_add_to_cart`, `devarsiv_remove_from_cart`, `devarsiv_checkout_cart`) — **alt-ajan
  sepete DOKUNMAZ** invariantı açık yazılır; zarfa `access`/`purchased` zenginleştirmesi
  ("zaten satın alınmış → arşivden oku" vs "sepet adayı: N sayfa").
- **Murzi kanıt-disiplini (H9):** 6 kalıp SKILL + citation referansına genellenir:
  iki-seviye kanıt (toponim ≠ soyad belgesi); katalog token'i ≠ doğrulanmış içerik
  ("görüntü teyidi bekliyor"); çift-tarih `ottoman_convert_date` re-teyit şerhi; tarihsiz
  kayıt kronolojik kanıt olamaz; ham HTR rapora alıntılanmaz; katalog yazımı ≠ toponimik yorum.
- **Nice-notlar (yalnız referans):** Wikilala (~8M sayfa matbu tam-metin arama,
  manual_required deep-link kalıbı) → `archive-landscape.md`; Qalamos IIIF probu notu;
  LLM safety-degrade notu (parça-böl/yeniden-dene/dürüst "okunamadı") → `htr-workflow.md`;
  DUDU treebank teyit notu.

### §4.7 Sürümleme + yayın (§8)

1. Önce mevcut uncommitted v2.5.0 çalışması OLDUĞU GİBİ ayrı commit'lenir (tarih korunur).
2. v3.0.0 implementasyonu → `plugin-validator` ajanı + doctor koşusu + hook `py_compile` +
   zip paket (`vekayinuvis-plugin-3.0.0.zip` + sha256).
3. CureoPrivate commit + `marketplace.json` sürüm; kurulum + `enabledPlugins` doğrulaması
   (bilinen gotcha: kurulum sessiz düşebilir) + `/vekayinuvis:durum` canlı smoke.
4. CHANGELOG v3.0.0: kırılan komut adları migration tablosu; README güncellemesi.

## 5. Değişmezler

- **Ödeme asla otonom değil**; sepet mutasyonları ana asistanda, metin-onaylı; alt-ajan
  sepete dokunmaz.
- **No-fabrication**: session_required/upstream degrade zarfları aynen aktarılır; görü
  birincil, HTR yardımcı; gürültülü HTR dürüstçe işaretlenir; yokluk kanıt değildir.
- **Bağlam ekonomisi**: Tier sözleşmesi korunur; async sonuç tek-sefer okunur → anamnesis;
  büyük çıktılar distiller üzerinden.

## 6. Başarı ölçütleri

- Doctor: 17 (+detsis?) server probu + devarsiv 22-araç envanteri yeşil.
- `/vekayinuvis:durum` ve en az bir uçtan-uca akış (arsiv-oku: gerçek arşiv belgesinde
  sayfa görüntüsü + sync OCR) canlı doğrulanır.
- plugin-validator temiz; zip kurulup enable edildiği `enabledPlugins`'te görülür.
