# Changelog — Vekayinüvis Plugin

Bu plugin [Semantic Versioning](https://semver.org/lang/tr/) kullanır.
Flagship skill kendi sürüm geçmişini `skills/vekayinuvis/SKILL.md` frontmatter
`changelog` alanında tutar.

## [2.2.2] — 2026-07-08

### Değiştirildi
- **`upstream_error` ≠ `session_required` ayrımı** (references §3): katalog backend'i sunucu-tarafı
  "Runtime Error" (Server Error in '/' Application) verirse `upstream_error` döner — oturum değil,
  upstream kesinti; **noVNC re-login çözmez**, bir süre sonra tekrar denenir. (MCP-tarafı tespit
  CureoHub `a8f80a8c`'de; önceden yanlışlıkla alive:true + boş/timeout dönüyordu.)

## [2.2.1] — 2026-07-08

### Değiştirildi (OCR sonrası ince ayar)
- **retrieve-don't-dump hook** artık `devarsiv_ocr_belge`'yi de tanıyor (büyük OCR/HTR metni →
  Tier-1 distiller / Tier-2 anamnesis'e yönlendirilir). `devarsiv_get_belge_image` **kasıtlı
  olarak hariç** — o bir görüntüdür, asistan görüsüyle okunur, dump edilmez.
- **Transkribus HTR durumu netleştirildi** (`devlet-arsivleri-katalog.md` §7): model
  `OttomanTurkish_generic` sunucuda yapılandırıldı ama **kredi-kapılı** (READ Coop kredisi
  gerekir); kredisizken el yazması Osmanlıca için **birincil yol `devarsiv_get_belge_image` +
  asistan görüsü**; kredi eklendiğinde `ocr_belge` gerçek HTR döner.

## [2.2.0] — 2026-07-08

### Eklendi (belge okuma — OCR/HTR + görsel)
- **devlet-arsivleri MCP artık belge sayfa taramasını okuyor** (5→8→**10 araç**). BelgeGoster
  full-res sayfa taramasını `<img id="sample_picture">`'da sunar — **satın-alma durumundan
  BAĞIMSIZ** (satın alınmamış önizlemeler de okunur; ampirik doğrulandı 2026-07-08).
  - **`devarsiv_get_belge_image`** — sayfa taraması ImageContent olarak → asistan **el yazması
    Osmanlıca'yı doğrudan görüsüyle okur** (BOA el yazması için pratikteki en iyi tam-okuma).
  - **`devarsiv_ocr_belge`** — deterministik OCR/HTR: Latin/Cumhuriyet tam-metin · Osmanlı basılı
    damga+arşiv referans kodu (tesseract `tur+eng+ara`) · el yazması Arap-harfli gövde → Transkribus
    HTR (creds-gated, SOTA) veya görsel-okuma. `mean_confidence`+`note`; no-fabrication.

### Değiştirildi
- **No-fabrication güncellendi:** belge görüntüsü artık **çekilir (gerçek tarama, uydurulmaz)** ve
  OCR/görü ile okunur; OCR düşük-güvende dürüstçe raporlanır; el yazması transkripsiyon insan
  doğrulamasına tabi; yalnız çok-sayfalı tam satın-alma seti (eSatış *SatinAldiklarim*) + diğer
  kısıtlı arşivler erişim-kapısında kalır. SKILL §3.1.b (10 araç) + §1.2, ARCHIVE_DEEP_DIVE /
  MANUSCRIPT_TRANSCRIBE / PROSOPOGRAPHY belge-okuma adımı, references/devlet-arsivleri-katalog.md §7
  (motor tablosu + kanonik akış), CONNECTORS §2, boa-katalog + transkripsiyon komutları,
  session_start hook konvansiyonu güncellendi.
- Osmanlıca en iyi okuma iki yol: **asistan görüsü** (self-contained, hesap gerektirmez) +
  **Transkribus HTR** (READ Coop hesabıyla deterministik SOTA); tesseract el yazmasını okumaz
  (basılı+Latin okur) — bu sınır dürüstçe belgelenir.
- Flagship skill **v2.1.0 → v2.2.0**. Davranış/mod sayısı (9) korundu.

## [2.1.0] — 2026-07-08

### Eklendi (devlet-arsivleri derin araç wire)
- **`devarsiv_semantic_search`** — diakronik/semantik katalog araması wire edildi: modern
  sorguyu Osmanlıca eşdeğerlerine genişletir (karantina→tahaffuzhane/sıhhiye/kordon;
  göçmen→muhacir/mülteci) + Workers AI **bge-m3** rerank; `matched_variants` şeffaflığı.
  SOURCE_HUNT/ARCHIVE_DEEP_DIVE modlarında modern-terim **birincil** arama aracı.
- **`devarsiv_detailed_search`** + **`devarsiv_list_fon_categories`** — **1000-tavan aşan
  kapsamlı erişim**: `list_fon_categories` (üst-fon ekseni) → her fon için `detailed_search`
  (arşiv × üst-fon × tarih-penceresi × özet) → `item_id` union. Katalog sayfalama-yok 1000
  satır render ettiği için `capped:true` = *daha fazlası var*; bu enumerasyon her belgeye
  ulaşmanın tek yolu. Ağır fan-out `arsiv-tarama-distilleri` ajanına delege edilir.

### Değiştirildi
- Bu 3 araç şuralara işlendi: SKILL §3.1.b tablosu (5→8 araç) + §5.1/§5.2 mod akışları +
  araç-seçim rehberi; `references/devlet-arsivleri-katalog.md` §2 (8 araç) + yeni §2b (kapsamlı
  erişim enumerasyonu) + §2c (semantik/diakronik); `agents/arsiv-tarama-distilleri.md` (araç
  seçimi + enumerasyon + `kapsam` çıktı alanı); `CONNECTORS.md` §2 + §7; `commands/vekayinuvis-
  boa-katalog.md` + `vekayinuvis-arsiv-dalis.md`; `hooks/scripts/retrieve_dont_dump.py`
  (semantic/detailed büyük-çıktı yönlendirmesi).
- **11→13 server sayım kayması düzeltildi**: `openathens`+`annas-reader` v2.0.0'da eklendiği hâlde
  bazı sayaçlar 11'de kalmıştı → SKILL §3.5/§10, `skills/start`, `session_start.py`,
  `stop_coverage.py` (gerekçe listesine iki tam-metin server'ı eklendi), `hooks.json`, `CONNECTORS.md`
  hepsi 13'e hizalandı; `context-economy-contract.md` sharding tablosuna **fulltext katmanı** (S3) eklendi.
- Flagship skill **v2.0.0 → v2.1.0**. Davranış/mod sayısı (9) korundu.

## [2.0.0] — 2026-07-07

### Eklendi
- **`devlet-arsivleri` çekirdek connector** (`https://devarsiv.cureonics.com/mcp`):
  resmî Devlet Arşivleri kataloğunda (Osmanlı/BOA · Cumhuriyet/BCA · Diplomatik ·
  Askeri) doğrudan **fon/kutu/gömlek araması** + belge künyesi. `archive-landscape.md`
  §1.1/§8.1/§8.4'teki "BETSİS sorgu önerisi / BCA için kayıt yok" boşluğunu kapatır.
  Yeni referans: `references/devlet-arsivleri-katalog.md`.
- **`literatur` (DergiPark) companion**: tam-metin (PDF→HTML) makale + referans;
  ottoman `search_dergipark`'ı tamamlar. Hazır remote (`literatur-mcp.surucu.dev`, authless).
- **`yok-akademik` destekleyici companion**: YÖK Akademik profilleri (modern prosopografi + ekol haritası).
- **Kitap+makale tam-metin şelalesi**: `openathens` (Tier 3 lisanslı — Millet Kütüphanesi /
  OpenAthens SAML, 309 DB; paywall'lı monograf/makale) → `annas-reader` (Tier 4 son-çare —
  Anna's Archive efemer-RAG; out-of-print Osmanlı çalışmaları; yalnız analiz). Getirilen tam-metin
  → anamnesis'e ingest. Böylece kitap ve makaleye tam-metin erişim tamamlandı.
- **`anamnesis` substrat**: büyük-veri RAG/GraphRAG bağlam-ekonomisi altyapısı
  (ingest→bounded query; kişi↔görev↔belge / olay↔tarih↔kaynak grafiği).
- **`arsiv-tarama-distilleri` alt-ajanı** (`agents/`): ağır çok-connector arşiv
  taramasını izole eder → tek `arsiv_distillate` zarfı (retrieve-don't-dump).
- **4 hook** (`hooks/hooks.json` + `hooks/scripts/`): SessionStart connector-preflight
  + tam-filo/bağlam-ekonomisi konvansiyonları; PostToolUse retrieve-don't-dump
  (büyük gövde → Tier-1 distiller / Tier-2 anamnesis); Stop stop_coverage (G0 kapsam
  manifestosu) + Stop citation_discipline (fon/kutu/gömlek + Hicrî/Miladî çift-tarih + katalog URL).
- **Bağlam ekonomisi + tam-filo sözleşmeleri** (`shared/`): `context-economy-contract.md`
  (Tier 0/1/2, sharding, kanonik cache, kör-getirme-yok chunking, devre-kesici) +
  `coverage-manifest.md` (G0 manifesto biçimi + örnek).
- **2 yeni komut**: `vekayinuvis-boa-katalog` (resmî katalog araması+künye) +
  `vekayinuvis-literatur` (DergiPark tam-metin derin literatür).
- **`userConfig`** (`plugin.json`): paper-search Smithery key'i enable-time'da (opsiyonel; girilmezse degrade).

### Değiştirildi
- **TAM-FİLO**: `.mcp.json` artık **11 server** bundle eder (çekirdek + akademik companion +
  yok-akademik + anamnesis, `_tier`/`_role` annotasyonlu) — bağlama uygun her araç her koşumda
  çalışır; iki-katmanlı "companion bundle edilmez" tasarımı full-fleet'e terfi etti.
- Flagship skill **v1.3.0 → v2.0.0**: §1.2 restricted-kaynak notu (katalog araması artık doğrudan;
  belge görüntüleri hâlâ kısıtlı), §3.1.b F. Resmî Katalog katmanı, §3.2 literatur+yok-akademik,
  §3.5 Tam-Filo ve Bağlam Ekonomisi, §5 mod güncellemeleri (SOURCE_HUNT/ARCHIVE_DEEP_DIVE/
  PROSOPOGRAPHY/HISTORIOGRAPHY/KANUN_GEREKÇESİ), §6.3 katalog URL atfı, §8 G0 kapsam manifestosu,
  §10 shared referanslar.
- CONNECTORS.md: §1 full-fleet, §2 devlet-arsivleri çekirdek + F. Resmî Katalog, §3 literatur/
  yok-akademik/anamnesis + tam-filo notu, §6 auth, §7 mod-map, §8 preflight + güncellenmiş
  restricted-kaynak kuralı. start/SKILL.md: connector kadrosu + tam-filo + anamnesis + degrade notları.

### Not
- **No-fabrication korunur**: resmî katalog kaydı (fon/kutu/gömlek + künye) doğrudan; belge
  **görüntüleri/tam-metni** hâlâ eSatış/on-site/transkripsiyon-tezi kapısında — asla uydurma.
  `devlet-arsivleri` **tek-cihaz oturum kilitli** (HP kalıcı authenticated tarayıcı); oturum düşükse
  `session_required` → re-login yol haritası + degrade.

## [1.0.0] — 2026-06-17

### Eklendi
- **Plugin paketlemesi**: standalone `vekayinuvis` user-skill'i, Claude Code
  plugin formatına (`.claude-plugin/plugin.json`) dönüştürüldü.
- **Çekirdek MCP transport** (`.mcp.json`): `ottoman-archives` (Cloud Run) +
  `yoktez` (FastMCP) uzak HTTP sunucuları bundle edildi.
- **Oryantasyon skill'i** (`skills/start/SKILL.md`): connector preflight +
  9-mod yönlendirme + scope guard.
- **7 slash komutu** (`commands/`): kaynak-avi, arsiv-dalis, transkripsiyon,
  prosopografi, kronoloji, rapor, kanun-gerekce.
- **CONNECTORS.md**: connector envanteri için tek doğruluk kaynağı — çekirdek
  vs. tamamlayıcı katman ayrımı, kimlik doğrulama modeli (OAuth vs. userConfig),
  mod → connector eşlemesi, fallback zincirleri, restricted-kaynak disiplini.
- **Tam orkestrasyon `.mcp.json` snippet'i + `userConfig` bloğu**: tamamlayıcı
  akademik katmanı (paper-search/consensus/scholar-gateway/exa/tavily) bundle
  etmek isteyenler için CONNECTORS.md § 4–5'te dokümante edildi.

### Değiştirildi
- Flagship skill **v1.2 → v1.3.0**: connector envanteri ve transport için
  plugin-düzeyi `../../CONNECTORS.md` + `../../.mcp.json` normatif kaynak olarak
  işaretlendi; § 3 connector tabloları pedagojik referans olarak korundu (skill
  standalone da çalışır). **Davranış / mod sayıları / kalite kapıları
  DEĞİŞMEDİ.**

### Korundu (v1.2 davranışı)
- 9 çalışma modu, G0–G6 kalite kapıları, IJMES/TDV İA çeviriyazı disiplini,
  çift/üçlü tarih notasyonu, restricted-kaynak içerik-üretmeme kuralı, 8
  referans dosyası (archive-landscape, source-typology, citation-and-
  transliteration, chronology, htr-workflow, kanun-gerekcesi-workflow,
  medical-history, report-template).
