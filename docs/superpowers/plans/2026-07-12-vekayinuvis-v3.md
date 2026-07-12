# Vekayinüvis v3.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vekayinüvis plugin'ini devarsiv 22-araç yüzeyiyle (sepet→noVNC→arşiv→çift-motor OCR→async job) tam entegre etmek, filoyu 13→17(+1) server'a genişletmek ve commands→skills mimari göçünü tamamlamak (v3.0.0).

**Architecture:** Salt içerik/konfig katmanı — plugin markdown skill'leri + JSON konfigler + 5 Python hook/doctor script'i. Kod değişiklikleri TDD (pytest yok; py_compile + örnek-payload çalıştırma); markdown görevleri içerik-sözleşmesi + grep-doğrulama döngüsüyle test edilir. Her görev bağımsız commit.

**Tech Stack:** Claude Code plugin şeması (skills/agents/hooks/mcpServers/userConfig), Python 3 (stdlib-only hook'lar), JSON, zip paketleme.

**Spec:** `docs/superpowers/specs/2026-07-11-vekayinuvis-v3-design.md` (bu repoda). Her görev spec'in ilgili §'ünü uygular.

## Global Constraints

- Çalışma dizini: `/mnt/thunderbolt/workspaces/CureoPrivate` (git repo kökü); plugin: `plugins/vekayinuvis/`.
- Sürüm damgası HER YERDE `3.0.0` (plugin.json ×2, doctor clientInfo, CHANGELOG, zip adı).
- `.mcp.json`'a yapılan HER değişiklik `.codex-plugin/plugin.json` inline `mcpServers` kopyasına da aynen yapılır (çift-bakım kuralı).
- Türkçe prose, mevcut dosyaların üslubunu koru; araç adları/parametreler İngilizce kod-font.
- No-fabrication değişmezleri her yeni/güncellenen metinde korunur: ödeme asla otonom değil; görü birincil/HTR yardımcı; yokluk kanıt değildir; degrade zarfları aynen aktarılır.
- noVNC URL sabiti: `https://devarsiv-vnc.cureonics.com/vnc.html`. Tek-cihaz uyarısı cümlesi (değişmez, her satın-alma bağlamında): "Kendi cihazınızdan kataloğa GİRMEYİN — tek-cihaz kilidi HP oturumunu düşürür."
- Fiyat dili: "~0,50 TL/sayfa TAHMİNDİR; bağlayıcı tutar `devarsiv_list_cart` çıktısındaki Tutar sütunudur."
- Commit mesajları `feat(vekayinuvis): …` / `fix(vekayinuvis): …` + `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Her görev sonunda: `python3 -c "import json; json.load(open('plugins/vekayinuvis/.mcp.json'))"` benzeri JSON-parse kontrolü (dokunulan her JSON için) + görev-özel grep doğrulaması.

## Kanonik içerik blokları (görevlerde aynen kullanılacak)

### K1 — Devarsiv 22-araç envanteri (SKILL/CONNECTORS/katalog.md tablolarının kaynağı)

| Grup | Araç | Not |
| --- | --- | --- |
| Arama | `devarsiv_search(query, arsiv?, limit?)` | Basit Arama; `capped:true`→enumerasyon, çok geniş→`refine_required` |
| Arama | `devarsiv_semantic_search(query, arsiv?, limit?, rerank?)` | Diyakronik genişletme (karantina→tahaffuzhane) + bge-m3 rerank |
| Arama | `devarsiv_detailed_search(arsiv, ozet?, ust_fon?, kutu?, gomlek?, sira?, tarih_turu?, yil_bas?, yil_bit?, limit?)` | OzelArama — 1000-cap altına daraltma/enumerasyon |
| Arama | `devarsiv_list_fon_categories(arsiv)` | Üst-fon listesi (enumerasyon ekseni) |
| Arama | `devarsiv_detailed_search_fields(arsiv)` | Form-alan introspeksiyonu |
| Belge | `devarsiv_get_belge(item_id, hash, arsiv)` | Künye + `access` (purchased/purchasable) |
| Belge | `devarsiv_get_belge_image(item_id, hash, arsiv)` | Önizleme taraması ImageContent — **görüyle okuma** |
| Belge | `devarsiv_ocr_belge(item_id, hash, arsiv, lang?, engine?)` | OCR/HTR; Osmanlı varsayılanı `engine="both"` |
| Sepet | `devarsiv_add_to_cart(item_id, hash, arsiv, pages?)` `[_RW]` | 1-tabanlı cbk sayfa seçimi ("1,3-5"; boş=tümü) |
| Sepet | `devarsiv_list_cart()` `[_RO]` | Kalemler + **bağlayıcı Tutar** |
| Sepet | `devarsiv_remove_from_cart(rows?, contains?, clear?)` `[_DESTRUCTIVE]` | Satır sil / boşalt |
| Sepet | `devarsiv_checkout_cart()` `[_RO]` | Ödeme YAPMAZ; yalnız noVNC URL + sepet döner |
| Arşiv | `devarsiv_list_purchased()` | SatinAldiklarim t/hash listesi |
| Arşiv | `devarsiv_ocr_belge_pages(t, hash, arsiv?, pages?, lang?, engine?)` | Viewer temsilî-sayfa sınırlı; TAM yol = yerel arşiv |
| Arşiv | `devarsiv_list_archive(query?)` | BOA-kodlu yerel PDF arşivi (code/yer/tarih/özet/sayfa) |
| Arşiv | `devarsiv_get_archive_page(code, page)` | **300 DPI ImageContent — satın-alınmış belgede birincil okuma** |
| Arşiv | `devarsiv_ocr_archive_pages(code, pages?, arsiv?, lang?, engine?)` | Sync OCR, ≤5 sayfa (MULTIPAGE_MAX_PAGES) |
| Arşiv | `devarsiv_get_archive_pdf(code, include_base64?, max_bytes?)` | Künye + sınırlı base64 PDF |
| Async | `devarsiv_ocr_submit(code, pages?, engine?, lang?, arsiv?)` `[_RW]` | İdempotent; job_id döner |
| Async | `devarsiv_ocr_result(job_id, include_text?)` `[_RO]` | queued/running/done/error/**stale** |
| Durum | `devarsiv_session_status()` | HP oturumu canlı mı |
| Durum | `devarsiv_server_info()` | Araç envanteri + `ocr.engines` + `purchase_cart.manual_checkout_url` |

### K2 — Motor konvansiyonu (tüm okuma anlatılarında)

`engine`: `auto` (Osmanlı→both, diğerleri→tesseract) | `both` | `transkribus` | `escriptorium` | `tesseract`.
`both` → Transkribus (el yazması PyLaia) + eScriptorium (basılı Kraken) PARALEL; iki transkripsiyon `transcriptions` altında yan yana + tesseract damga katmanı. Düşen motor dürüst `unavailable` nedeni taşır. Latin arşivler (1/3/4) daima tesseract. **Görü birincil, HTR yardımcı** — Transkribus taşra-kâtibi ellerinde gürültülü olabilir (2026-07-09 canlı gözlem).

### K3 — Transkribus model seçim tablosu

| Belge türü | Model | CER | Not |
| --- | --- | --- | --- |
| El yazması genel (divani/rika) | **56496** OttomanTurkish_generic | ~%12 | Üretimdeki varsayılan (`DEVARSIV_TRANSKRIBUS_HTR_ID`) |
| Fetva / ilmiye el yazması | **169801** Ottoman Fatwa Manuscript | %5.94 | Fetva/kadı-sicili tipi eller için alternatif |
| Matbu (salname/gazete/nizamname) | **52502** OttomanTurkish_Print_1 | %7.2 | Matbu Osmanlıca; eScriptorium OpenITI print ile çapraz-kontrol |

Model değişimi deploy-notu: HP `~/devarsiv-mcp/runtime.env` → `DEVARSIV_TRANSKRIBUS_HTR_ID=<id>` + `systemctl restart devarsiv-mcp`.

### K4 — Sync/async karar kuralı

≤5 sayfa VE tek motor → `devarsiv_ocr_archive_pages` (sync). >5 sayfa VEYA `both` tam belge → `devarsiv_ocr_submit` → `devarsiv_ocr_result(include_text=false)` ile poll → `done`'da **tek sefer** `include_text=true` → anamnesis `ingest_document(doc_id="devarsiv:<code>", …)` → sonraki sorgular `hybrid_query`. `stale` → aynı parametrelerle resubmit (arşiv PDF yerel; maliyet tekrarlanmaz).

### K5 — Re-login runbook (katalog.md §3 + PostToolUseFailure enjeksiyonu)

```text
Oturum düştü (session_required / Runtime Error 500 ≈ expired oturum → BEKLEME değil RE-LOGIN):
1. HP: sudo systemctl restart devarsiv-chrome
2. HP: x11vnc -display :99 -rfbauth ~/devarsiv/vncpass -rfbport 5900 -localhost -forever -bg
       (kalıcı devarsiv-x11vnc.service zaten aktifse bu adım atlanır)
3. noVNC: https://devarsiv-vnc.cureonics.com/vnc.html (Cloudflare Access, @cureonics.com OTP)
4. Tarayıcıda reCAPTCHA çöz + T.C. Kimlik ile giriş (Doppler DEVLET_ARSIVLERI_*)
5. devarsiv_session_status → alive:true doğrula
Degrade-devam: katalog düşükken yerel arşiv (list_archive/get_archive_page) + anamnesis +
akademik katman ÇALIŞMAYA DEVAM EDER — rapor akışını durdurma, "katalog doğrulaması bekliyor" şerhi düş.
```

### K6 — Murzi kanıt-disiplini kalıpları (6)

1. İki-seviye kanıt: toponim/bağlam eşleşmesi ≠ soyad/kişi belgesi — iddia seviyesini ayır.
2. Katalog arama token'i ≠ doğrulanmış içerik — görüntüsü açılmamış kayda "görüntü teyidi bekliyor" etiketi.
3. Çift-tarih: her Hicri/Rumi→Miladi çevirisine `ottoman_convert_date` ile yeniden-teyit şerhi.
4. Tarihsiz katalog kaydı kronolojik kanıt olarak kullanılamaz.
5. Ham HTR metni rapora alıntılanmaz — görüyle doğrulanmış okuma alıntılanır, HTR dipnotta.
6. Katalog yazımı (özgün imlâ) ile toponimik/tarihsel yorum ayrı sütunlarda tutulur.

---

### Task 0: v2.5.0 baseline commit (tarih koruma)

**Files:** hiçbiri yaratılmaz — mevcut uncommitted çalışma ağacı OLDUĞU GİBİ commit'lenir.

**Interfaces:** Produces: temiz working tree; v3 görevleri bunun üstüne izole diff'ler üretir.

- [ ] **Step 1: Durumu doğrula** — `cd /mnt/thunderbolt/workspaces/CureoPrivate && git status --short` → yalnız `plugins/vekayinuvis/*`, `README.md`, `.claude-plugin/marketplace.json` değişiklikleri beklenir. Başka dosya varsa DURDUR ve raporla.
- [ ] **Step 2: Commit** —
```bash
git add plugins/vekayinuvis README.md .claude-plugin/marketplace.json
git commit -m "feat(vekayinuvis): v2.5.0 — marketplace-portable doctor, G0 sıkılaştırma, provenance denetimi (baseline)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
- [ ] **Step 3: Doğrula** — `git status --short` boş; `git log --oneline -1` v2.5.0 mesajını gösterir.

### Task 1: Devarsiv senkronu — .mcp.json + .codex-plugin + CONNECTORS.md

**Files:**
- Modify: `plugins/vekayinuvis/.mcp.json` (devlet-arsivleri `_role`)
- Modify: `plugins/vekayinuvis/.codex-plugin/plugin.json` (inline mcpServers kopyası)
- Modify: `plugins/vekayinuvis/CONNECTORS.md` (§2 envanter, §7 mod-map, §8 preflight)

**Interfaces:** Consumes: K1/K2/K4. Produces: CONNECTORS §7 mod-map satır adları (`SEPET/SATIN-ALMA`, `ARŞİV OKUMA`, `ASYNC OCR`) — Task 4/5 skill'leri bu adlara atıf yapar.

- [ ] **Step 1:** `.mcp.json`'daki `devlet-arsivleri` girdisinin `_role` (veya eşdeğer açıklama) metnini K1'in tek-cümlelik özetiyle değiştir: "Resmî Devlet Arşivleri kataloğu — arama 5'lisi + belge 3'lüsü (engine paramlı çift-motor OCR) + eSatış sepeti 4'lüsü (ödeme YALNIZ insan/noVNC) + satın-alınmış/yerel-arşiv 6'lısı (300 DPI, arşiv-öncelikli okuma) + async OCR 2'lisi + durum 2'lisi = 22 araç; tek-cihaz oturum kilidi (HP)."
- [ ] **Step 2:** Aynı metni `.codex-plugin/plugin.json` inline kopyasına uygula. İki dosyayı da JSON-parse ile doğrula.
- [ ] **Step 3:** `CONNECTORS.md` §2: devlet-arsivleri başlığındaki "8 araç"/10-ad tutarsızlığını K1 tablosunun kompakt hâliyle değiştir (22 araç, 6 grup). §8 preflight'a ekle: `devarsiv_server_info` çağrısının `tools` uzunluğu **22** değilse "connector'ı claude.ai'da yeniden bağla (araç listesi cache'lenmiş olabilir)" uyarısı.
- [ ] **Step 4:** §7 mod-map tablosuna üç yeni satır: `SEPET/SATIN-ALMA → devarsiv sepet 4'lüsü (skills/satinalma)`, `ARŞİV OKUMA → list_archive/get_archive_page/ocr_archive_pages/get_archive_pdf (skills/arsiv-oku)`, `ASYNC OCR → ocr_submit/ocr_result + anamnesis ingest (skills/toplu-okuma)`.
- [ ] **Step 5: Doğrula + commit** — `grep -c "devarsiv_" plugins/vekayinuvis/CONNECTORS.md` artmış olmalı; `grep -n "8 araç" CONNECTORS.md` boş dönmeli.
```bash
git add plugins/vekayinuvis/.mcp.json plugins/vekayinuvis/.codex-plugin/plugin.json plugins/vekayinuvis/CONNECTORS.md
git commit -m "feat(vekayinuvis): devarsiv 22-araç senkronu — connector rol + CONNECTORS envanter/mod-map/preflight"
```

### Task 2: skills/vekayinuvis/SKILL.md — çekirdek orkestratör güncellemesi

**Files:**
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/SKILL.md`

**Interfaces:** Consumes: K1, K2, K4, K6. Produces: §3.1.b kanonik 22-araç tablosu; "arşivde-varsa-arşivden-oku" kural cümlesi (Task 3/4/5 atıf yapar): **"Belge satın alınmışsa okuma DAİMA yerel arşivden başlar: devarsiv_list_archive → devarsiv_get_archive_page (300 DPI + görü); katalog önizlemesi (sample) yalnız satın-alınmamış belgeler içindir."**

- [ ] **Step 1:** §3.1.b devarsiv araç tablosunu K1 ile TAMAMEN değiştir (22 satır, anotasyonlar dahil). `ocr_belge_pages` artık tabloda (tutarsızlık kapanır).
- [ ] **Step 2:** No-fabrication/güvenlik bölümüne "state-changing araçlar" paragrafı: sepet mutasyonları `_RW`/`_DESTRUCTIVE`; `checkout_cart` ödeme YAPMAZ; ödeme-öncesi metin-onay kapısı zorunlu (Global Constraints'teki uyarı cümlesi verbatim); alt-ajan sepete dokunmaz.
- [ ] **Step 3:** Okuma anlatısına K2 motor konvansiyonu + K4 sync/async kuralı + yukarıdaki "arşivde-varsa-arşivden-oku" kural cümlesini ekle (Tier-0/1 bağlam-ekonomisi bölümüne çapraz-atıf).
- [ ] **Step 4:** EVENT_RECONSTRUCTION moduna devarsiv wire et: mod tarifine "devarsiv_semantic_search (dönem terimleriyle) + detailed_search (tarih-aralığı) birincil katman" cümlesi + araç listesine devarsiv araçları.
- [ ] **Step 5:** K6 Murzi kalıplarını "Kanıt disiplini" alt-bölümü olarak ekle (6 madde verbatim).
- [ ] **Step 6:** Sürüm/başlık satırındaki `v2.5.0` → `v3.0.0`; 9 mod sayımı korunur, mod-map'te üç yeni akış skill'ine işaret.
- [ ] **Step 7: Doğrula + commit** — `grep -c "devarsiv_" SKILL.md` ≥ 30; `grep -n "ocr_submit\|get_archive_page\|checkout_cart" SKILL.md` üçü de bulunur.
```bash
git add plugins/vekayinuvis/skills/vekayinuvis/SKILL.md
git commit -m "feat(vekayinuvis): SKILL çekirdeği — 22-araç tablosu, motor/async konvansiyonu, arşiv-öncelik, Murzi kanıt disiplini"
```

### Task 3: references/ dalgası — 9 dosya güncellemesi

**Files:**
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/references/devlet-arsivleri-katalog.md`
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/references/archive-landscape.md`
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/references/htr-workflow.md`
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/references/medical-history.md`
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/references/kanun-gerekcesi-workflow.md`
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/references/report-template.md`
- Modify (dokunma-gerekirse): `citation-and-transliteration.md` (yalnız K6 çapraz-atıf)

**Interfaces:** Consumes: K1–K6, Task 2 kural cümlesi. Produces: katalog.md §8 akış adımları (Task 5 skill'leri bunlara atıf yapar); §3 runbook (Task 7 hook'u aynı metni enjekte eder).

- [ ] **Step 1 — devlet-arsivleri-katalog.md (büyük revizyon):** ":28 '10 araç'" → K1 22-araç envanteri; `ocr_belge` satırlarına `engine` paramı; `server_info` çıktısına `ocr.engines` + `purchase_cart` alanları; §3'e K5 runbook'u verbatim; "eSatış kapısında / satın alma gerekli → talimat" cümlelerini AKSIYONLU akışla değiştir ("→ skills/satinalma akışını başlat"); §7 motor tablosunu K2+K3 ile değiştir; §8'e dört akış özeti (satın-alma / arşiv-okuma / üç-sütun transkripsiyon / async) + güvenlik anotasyonları.
- [ ] **Step 2 — archive-landscape.md:** §8.1/§8.4'teki "eSatış satın-alma TALİMATI" pasajlarını `add_to_cart→list_cart→ONAY→checkout_cart→noVNC` akışına çevir. Dosya sonuna "Diğer dijital yüzeyler" notları: **Wikilala** (~8M sayfa matbu Osmanlıca tam-metin arama 1729-1928; API yüzeyi DOĞRULANMADI → yalnız manuel deep-link + sorgu-yankısı kalıbı) ve **Qalamos** (147k+ Doğu yazması; IIIF uçları teyitsiz → önce canlı probe notu).
- [ ] **Step 3 — htr-workflow.md (devarsiv farkındalığı sıfırdan):** Adım 0 keşif bölümüne `devarsiv_search→get_belge_image` girişi; §6'ya K4 async kalıbı; §7 fallback + §10 karar akışına "BOA/BCA belgesi → devarsiv çift-motor (K2)" dalı; model tablosuna K3; dosya sonuna LLM safety-degrade notu: "Tarihî şiddet/esaret anlatılarında görü-okuma/çeviri güvenlik-reddi verebilir (arXiv 2503.11898, likely) → parça-böl + yeniden dene + olmadıysa dürüst 'okunamadı' işareti — içerik asla atlanmış gibi gösterilmez." + DUDU teyit notu ("UD_Ottoman_Turkish-DUDU treebank'i UD deposunda teyit edilmeli — SPECULATIVE").
- [ ] **Step 4 — medical-history.md:** §7'deki 5 arşiv reçetesinde `web_search("BOA HAT …")` çağrılarını `devarsiv_search(query, arsiv="2")` / `devarsiv_semantic_search` ile değiştir (sorgu terimleri aynı kalır).
- [ ] **Step 5 — kanun-gerekcesi-workflow.md:** TUR 1 paralel setine devarsiv ekle: `devarsiv_search(arsiv="2")` İrade/HAT/DH grubu + `devarsiv_search(arsiv="1")` BCA kararnameler; §5.4 örnek komuta aynı ekleme. (Yeni filo server'ları Task 6'da eklenir — burada yalnız devarsiv.)
- [ ] **Step 6 — report-template.md:** :73-75/:108-111/:300-301 bayat "BOA tam metin taraması mevcut değildir / on-site erişim" örneklem cümlelerini kaldır; yerine süreç-notu: "Erişim durumu `devarsiv_get_belge.access` ile raporlanır; satın-alınmış belgeler yerel arşiv PDF'inden (300 DPI) okunmuştur." §8 süreç-notuna devarsiv araç adları.
- [ ] **Step 7 — citation-and-transliteration.md:** §6.3'e tek cümle çapraz-atıf: "Kanıt-seviyesi etiketleri (görüntü teyidi bekliyor / görüyle doğrulandı / HTR-yalnız) için SKILL §Kanıt-disiplini (Murzi kalıpları)."
- [ ] **Step 8: Doğrula + commit** — `grep -rn "10 araç\|mevcut değildir\|on-site" references/` bayat kalıntı döndürmez; `grep -c "devarsiv_" references/htr-workflow.md` ≥ 5.
```bash
git add plugins/vekayinuvis/skills/vekayinuvis/references/
git commit -m "feat(vekayinuvis): references dalgası — katalog 22-araç+runbook, HTR devarsiv+model tablosu, bayat-anlatı temizliği"
```

### Task 4: commands→skills göçü (10 komut)

**Files:**
- Create: `plugins/vekayinuvis/skills/{durum,arsiv-dalis,boa-katalog,kanun-gerekce,kaynak-avi,kronoloji,literatur,prosopografi,rapor,transkripsiyon}/SKILL.md`
- Delete: `plugins/vekayinuvis/commands/` (10 dosya)
- Modify: `plugins/vekayinuvis/.claude-plugin/plugin.json` (`commands` alanı kaldır)

**Interfaces:** Consumes: mevcut komut gövdeleri (içerik taşınır+güncellenir), K1-K4, Task 2/3 çıktıları. Produces: skill adları `/vekayinuvis:<ad>` (README/CHANGELOG migration tablosu Task 10 bunları listeler).

- [ ] **Step 1:** Her komut için `skills/<öneksiz-ad>/SKILL.md` oluştur. Frontmatter şablonu:
```markdown
---
name: <ad>
description: <mevcut komutun description'ı — tetikleyiciler korunur>
---
```
Gövde = mevcut komut gövdesi + şu güncellemeler: (a) `arsiv-dalis` ve `boa-katalog`: `get_belge.access=="purchasable"` dalına "→ `/vekayinuvis:satinalma` akışına yönlendir" adımı; çok-sayfa okumada K4 kuralı; (b) `transkripsiyon`: üç girdi tipi (katalog önizleme `get_belge_image` / satın-alınmış arşiv `get_archive_page(code,page)` / harici görüntü) + **üç-sütun protokol**: "Sütun 1 Görü (birincil — çelişkide kazanır) | Sütun 2 Transkribus | Sütun 3 eScriptorium; gürültülü HTR sütunu 'kullanılmadı (gürültülü)' olarak işaretlenir, boş bırakılmaz" + K3 model tablosu + kredi kuralı ("`both` yalnız görünün değerli bulduğu sayfada; keşif taramasında `engine=tesseract` veya `escriptorium`"); (c) `durum`: doctor çağrısına yeni bölümler (Task 8'in çıktı formatı); (d) `kanun-gerekce`: Task 3 Step 5 devarsiv seti.
- [ ] **Step 2:** Manuel-only skill'lere `disable-model-invocation: true` frontmatter'ı ekle: `durum`, `rapor`, (Task 5'te `satinalma`). Ağır fan-out'lara (`arsiv-dalis`, `kaynak-avi`, `rapor`) frontmatter'a `context: fork` ekle ve gövdeye "geniş tarama arsiv-tarama-distilleri alt-ajanına devredilir" notu (zaten varsa koru).
- [ ] **Step 3:** `git rm -r plugins/vekayinuvis/commands/`; `.claude-plugin/plugin.json`'dan `"commands": "./commands"` satırını sil (JSON-parse doğrula).
- [ ] **Step 4: Doğrula + commit** — `ls plugins/vekayinuvis/skills/ | wc -l` = 14 (vekayinuvis + start + 10 göç + 0 yeni-henüz); her yeni SKILL.md frontmatter'ı `name:` + `description:` içerir (`grep -L "^description:" skills/*/SKILL.md` boş).
```bash
git add -A plugins/vekayinuvis
git commit -m "feat(vekayinuvis)!: commands→skills göçü — /vekayinuvis:<ad> öneksiz adlar (BREAKING), transkripsiyon üç-sütun protokolü"
```

### Task 5: 3 yeni akış skill'i + start/context-economy güncellemeleri

**Files:**
- Create: `plugins/vekayinuvis/skills/satinalma/SKILL.md`
- Create: `plugins/vekayinuvis/skills/arsiv-oku/SKILL.md`
- Create: `plugins/vekayinuvis/skills/toplu-okuma/SKILL.md`
- Modify: `plugins/vekayinuvis/skills/start/SKILL.md`
- Modify: `plugins/vekayinuvis/shared/context-economy-contract.md`

**Interfaces:** Consumes: K1-K5, Task 2 kural cümlesi, CONNECTORS §7 satır adları (Task 1). Produces: `/vekayinuvis:satinalma`, `/vekayinuvis:arsiv-oku`, `/vekayinuvis:toplu-okuma`.

- [ ] **Step 1 — satinalma/SKILL.md** (frontmatter: `disable-model-invocation: true`; description: "eSatış sepet + noVNC satın-alma akışı — karar matrisi, metin-onay kapısı, ödeme daima insan"). Gövde iki faz:
```markdown
## Faz 1 — KARAR (ücretsiz)
1. devarsiv_get_belge → künye + goruntu_sayisi + access ("purchased" ise DUR: /vekayinuvis:arsiv-oku)
2. devarsiv_get_belge_image → önizlemeyi GÖRÜyle değerlendir (içerik gerçekten hedefle ilgili mi?)
3. Karar matrisi (4 eksen): ilgi (görü teyidi) × derinlik (goruntu_sayisi) × kaynak-değeri
   (özet+fon) × bütçe (~0,50 TL/sayfa TAHMİN; bağlayıcı tutar list_cart Tutar sütunu)
4. Karar tablosunu kullanıcıya sun: aday belgeler | sayfa | tahmini maliyet | gerekçe
## Faz 2 — SEPET (yumuşak kapı)
5. Onaylanan adaylar: devarsiv_add_to_cart(item_id, hash, arsiv, pages) — sayfa alt-kümesi
   destekli ("1,3-5")
6. devarsiv_list_cart → kalemleri + BAĞLAYICI toplamı doğrula
7. METİN-ONAY KAPISI: "Sepette N kalem, toplam X TL. Ödemeye geçilsin mi?" — açık onay
   olmadan checkout_cart ÇAĞRILMAZ; remove_from_cart(clear=true) da açık onay ister
8. devarsiv_checkout_cart → YALNIZ noVNC URL döner: https://devarsiv-vnc.cureonics.com/vnc.html
   + uyarı: "Kendi cihazınızdan kataloğa GİRMEYİN — tek-cihaz kilidi HP oturumunu düşürür."
   Ödeme (kart+3DS) DAİMA insan; Access girişi @cureonics.com OTP.
## Faz 3 — ÖDEME SONRASI (operatör adımı)
9. Kullanıcı ödemeyi bitirdiğinde: HP'de scripts/build_archive.py koşulmalı —
   Claude Code host: ssh hp-ai-node '~/devarsiv/.venv-arc/bin/python ~/devarsiv/build-archive.py'
   (yol yoksa: CureoHub mcp-servers/devlet-arsivleri-mcp/scripts/build_archive.py kopyası)
   claude.ai host: komutu kullanıcıya kutu içinde ver (operatör adımı)
10. devarsiv_list_archive ile yeni code'u doğrula → /vekayinuvis:arsiv-oku
```
- [ ] **Step 2 — arsiv-oku/SKILL.md** (description: "Satın-alınmış belgeleri yerel BOA-kodlu arşivden okuma — 300 DPI görü birincil"). Gövde: `list_archive(query)` → code seçimi → sayfa-sayfa `get_archive_page(code, page)` görüyle okuma (Task 2 kural cümlesi verbatim) → deterministik katman gerekiyorsa `ocr_archive_pages` (≤5, K2 engine rehberi) → künye/PDF `get_archive_pdf` → >5 sayfa → `/vekayinuvis:toplu-okuma`. Atıf biçimi: "BOA <code>, s.<page> (yerel arşiv 300 DPI, görüyle okundu)".
- [ ] **Step 3 — toplu-okuma/SKILL.md** (description: "Çok-sayfalı satın-alınmış belgede async çift-motor OCR + anamnesis ingest"). Gövde: K4 verbatim + poll disiplini ("`ocr_result(include_text=false)` ile ilerleme; kullanıcıya '3/15 sayfa' raporla; done'da TEK SEFER tam metin → anamnesis ingest → ham metni pencereden düşür") + `stale` davranışı + iş bitince özet tablo (sayfa | motor | kelime | görü-teyit gereken mi).
- [ ] **Step 4 — start/SKILL.md:** "Önemli sınır" paragrafını güncelle: çok-sayfa erişimin artık sepet→satın-alma→arşiv zinciriyle araç-içi olduğu; preflight'a `devarsiv_server_info` 22-araç kontrolü; yeni üç akışın tek-satır tanıtımı.
- [ ] **Step 5 — context-economy-contract.md:** §6 olarak ekle: "Async OCR sonucu: `ocr_result(include_text=true)` TEK SEFER okunur → anamnesis `ingest_document(doc_id='devarsiv:<code>')` → ham metin ana pencereden düşürülür; izleyen erişim `hybrid_query`. `get_archive_page` görüntüleri ana pencerede sayfa-sayfa tüketilir (distiller'a gönderilmez — görü ana asistanda)."
- [ ] **Step 6: Doğrula + commit** — üç yeni skill frontmatter'lı; `grep -n "checkout_cart" skills/satinalma/SKILL.md` onay-kapısı adımından SONRA gelir.
```bash
git add plugins/vekayinuvis/skills plugins/vekayinuvis/shared
git commit -m "feat(vekayinuvis): satinalma/arsiv-oku/toplu-okuma akış skill'leri + start/context-economy güncellemesi"
```

### Task 6: Filo genişlemesi — 4(+1) yeni MCP server

**Files:**
- Modify: `plugins/vekayinuvis/.mcp.json` + `.codex-plugin/plugin.json` (birlikte)
- Modify: `plugins/vekayinuvis/CONNECTORS.md`, `plugins/vekayinuvis/shared/coverage-manifest.md`
- Modify: `plugins/vekayinuvis/hooks/scripts/stop_coverage.py`, `hooks/scripts/session_start.py`
- Modify: `plugins/vekayinuvis/skills/vekayinuvis/SKILL.md` (mod-katman eşlemesi), `skills/kanun-gerekce/SKILL.md`, `skills/prosopografi/SKILL.md`

**Interfaces:** Consumes: mevcut .mcp.json girdi biçimi (header/env deseni AYNEN kopyalanır). Produces: server anahtar adları — `resmigazete`, `mevzuat`, `tbmm`, `marmara`(, `detsis`).

- [ ] **Step 1 — canlı probe (detsis + URL teyitleri):**
```bash
for u in resmi-gazete-mcp.cureonics.workers.dev mevzuat.cureonics.com tbmm.cureonics.com marmara.cureonics.com detsis.cureonics.com; do
  printf "%s: " "$u"; curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 "https://$u/mcp"; done
```
Beklenen: 401/406 (auth/Accept gate = canlı). `detsis` 404/530/timeout dönerse detsis'i ATLA ve CHANGELOG'a "detsis v3.1'e ertelendi (URL doğrulanamadı)" notu düş.
- [ ] **Step 2:** `.mcp.json`'a mevcut girdilerin biçimini birebir kopyalayarak ekle (URL + `Authorization: Bearer ${VAR}`): `resmigazete`→`https://resmi-gazete-mcp.cureonics.workers.dev/mcp`/`${RESMI_GAZETE_MCP_API_KEY}`; `mevzuat`→`https://mevzuat.cureonics.com/mcp`/`${MEVZUAT_MCP_API_KEY}`; `tbmm`→`https://tbmm.cureonics.com/mcp`/`${TBMM_MCP_API_KEY}`; `marmara`→`https://marmara.cureonics.com/mcp`/`${MARMARA_MCP_API_KEY}`; (probe geçtiyse) `detsis`→`https://detsis.cureonics.com/mcp`/`${DETSIS_MCP_API_KEY}`. Her girdiye `_role` tek-cümle (spec §4.4 tablosundan). `.codex-plugin` kopyası + iki JSON-parse.
- [ ] **Step 3:** `CONNECTORS.md`: katman tablosuna 4(+1) satır (rol + mod eşlemesi + auth env adı); §4 snippet 13→17(+1); §7 mod-map: KANUN_GEREKÇESİ+=resmigazete/mevzuat/tbmm; HISTORIOGRAPHY tam-metin şelalesi `openathens→marmara→annas-reader`; PROSOPOGRAPHY+=detsis (girdiyse, "Cumhuriyet-sınırlı: Osmanlı teşkilatına inmez" kapsam notuyla); SOURCE_HUNT+=tbmm DSpace.
- [ ] **Step 4:** `coverage-manifest.md` G0 listesi + `stop_coverage.py` içindeki server listesi/sayısı + `session_start.py` preflight listesi yeni server'larla güncellenir (üçünde de aynı adlar). `python3 -m py_compile` iki script'e.
- [ ] **Step 5:** SKILL.md mod-katman eşlemesine, `kanun-gerekce` TUR-1 setine (rg_resolve_date→rg_get_item; search_mulga_mevzuat+get_mevzuat_gerekce; tbmm_search_kanun_teklifi→tbmm_get_kanun_teklifi) ve `prosopografi`ye (detsis_resolve_birim→detsis_get_gecmis_birim→detsis_list_milestones→detsis_get_mevzuatlar zinciri, girdiyse) yeni katman satırları.
- [ ] **Step 6: Doğrula + commit** — `python3 - <<'EOF'` ile .mcp.json server sayısını yazdır (17 veya 18); `grep -c "cureonics" .mcp.json` tutarlı.
```bash
git add plugins/vekayinuvis
git commit -m "feat(vekayinuvis): filo genişlemesi — resmigazete/mevzuat/tbmm/marmara(+detsis?) → G0/preflight/mod-map senkron"
```

### Task 7: Hook katmanı — BUG fix + PostToolUseFailure + iki script güncellemesi

**Files:**
- Modify: `plugins/vekayinuvis/hooks/hooks.json`
- Create: `plugins/vekayinuvis/hooks/scripts/devarsiv_degrade.py`
- Modify: `plugins/vekayinuvis/hooks/scripts/retrieve_dont_dump.py`, `hooks/scripts/citation_discipline.py`, `hooks/scripts/session_start.py`
- Delete: `plugins/vekayinuvis/hooks.json` (kök inert kopya)

**Interfaces:** Consumes: K5 runbook metni (katalog.md §3 ile AYNI). Produces: hooks.json event yapısı (Task 9 validator'ı parse eder).

- [ ] **Step 1 — BUG fix:** `hooks/hooks.json` SessionStart matcher `"startup|resume|compact"` → `"startup|resume|clear|compact"`.
- [ ] **Step 2 — devarsiv_degrade.py (yeni):** Mevcut `retrieve_dont_dump.py`'nin stdin-JSON okuma/çıktı desenini AYNEN izleyerek yaz: `tool_name` `devarsiv_` ile başlıyor VE tool yanıtında (`tool_response` string'inde) `"session_required"` ya da `"viewer_runtime_error"` geçiyorsa, `hookSpecificOutput.additionalContext` olarak K5 runbook'unun kompakt hâlini (6 satır) döndür; aksi hâlde sessiz `{}`. Script hem `PostToolUse` hem `PostToolUseFailure` payload'ıyla çalışacak şekilde alan-yokluğuna toleranslı olsun (`.get` zinciri; asla exception fırlatmaz — `except Exception: print("{}")`).
- [ ] **Step 3 — hooks.json'a kayıt:** `PostToolUse` altına matcher `"^mcp__.*devarsiv.*"` (mevcut hook'ların matcher üslubuyla) → `devarsiv_degrade.py`; ayrıca `PostToolUseFailure` event'i altına aynı kayıt — kurulu CC sürümü event'i tanımıyorsa girdi yoksayılır (zararsız), bu davranış hooks.json içi `_comment` alanıyla not edilir.
- [ ] **Step 4 — retrieve_dont_dump.py:** `BIG_OUTPUT_TOOLS` kümesine ekle: `devarsiv_ocr_belge_pages`, `devarsiv_ocr_archive_pages`, `devarsiv_get_archive_pdf`, `devarsiv_ocr_result`. Hemen üstüne yorum: `# devarsiv_get_archive_page BİLİNÇLİ İSTİSNA: görüntü ana pencerede görüyle okunur (get_belge_image gibi)`.
- [ ] **Step 5 — citation_discipline.py:** provenance regex'ine alternatifler ekle: `ocr_archive_pages|ocr_submit|ocr_result|job_id|get_archive_page|get_archive_pdf`; "both" modu kuralı için denetim mesajına ek satır: "Çift-motor kullanıldıysa iki motorun çıktısı ayrı raporlanmalı (tek birleşik metin YASAK)."
- [ ] **Step 6 — session_start.py:** Bayat "Çok-sayfalı tam satın-alma seti hâlâ erişim-kapısında" cümlesini kaldır; yerine 4 konvansiyon satırı: sepet=state-changing-ama-ödemesiz; checkout=yalnız-noVNC-URL (+tek-cihaz uyarısı); arşiv-öncelikli okuma kuralı; K4 sync/async tek-cümle özeti.
- [ ] **Step 7 — kök hooks.json:** `git rm plugins/vekayinuvis/hooks.json` (inert duplicate).
- [ ] **Step 8 — Test:** `python3 -m py_compile hooks/scripts/*.py` temiz. Örnek-payload testi:
```bash
echo '{"tool_name":"mcp__devlet-arsivleri__devarsiv_search","tool_response":"{\"status\": \"session_required\"}"}' \
 | python3 plugins/vekayinuvis/hooks/scripts/devarsiv_degrade.py
# Beklenen: additionalContext içinde "re-login" ve "devarsiv-vnc.cureonics.com" geçen JSON
echo '{"tool_name":"mcp__devlet-arsivleri__devarsiv_search","tool_response":"{\"status\": \"ok\"}"}' \
 | python3 plugins/vekayinuvis/hooks/scripts/devarsiv_degrade.py
# Beklenen: {}
```
- [ ] **Step 9: Commit**
```bash
git add -A plugins/vekayinuvis/hooks plugins/vekayinuvis/hooks.json
git commit -m "fix(vekayinuvis): SessionStart 'clear' BUG + devarsiv degrade hook'u + retrieve/citation yeni-araç uyumu"
```

### Task 8: Doctor v3

**Files:**
- Modify: `plugins/vekayinuvis/scripts/vekayinuvis_doctor.py`
- Modify: `plugins/vekayinuvis/skills/durum/SKILL.md` (çıktı-format bölümü)

**Interfaces:** Consumes: Task 6 server listesi. Produces: doctor çıktı bölümleri `[envanter]`, `[engines]`, `[vnc]` (durum skill'i bunları okur).

- [ ] **Step 1:** Server listesine Task 6'da eklenenleri işle (offline sınıflamada 17/18). clientInfo sürümü `3.0.0`.
- [ ] **Step 2:** `--live` moduna üç kontrol ekle (mevcut devarsiv_session_status probunun HTTP/JSON-RPC desenini aynen kullanarak): (a) `devarsiv_server_info` çağır → `tools` uzunluğu ≠22 ise `[envanter] DRIFT: N/22 — claude.ai connector'ını yeniden bağlayın` yaz; (b) aynı yanıttan `ocr.engines.transkribus/escriptorium` durum stringlerini `[engines]` bölümünde bas; (c) `https://devarsiv-vnc.cureonics.com/vnc.html` HEAD isteği → 302 (Access yönlendirmesi) = `[vnc] OK (Access-gated)`; timeout/5xx = `[vnc] SORUN`.
- [ ] **Step 3:** `--write-manifest` çıktı evi: `os.environ.get("CLAUDE_PLUGIN_DATA")` doluysa onun altına, yoksa mevcut davranış (geriye-uyumlu) — tek `out_dir` yardımcı fonksiyonu.
- [ ] **Step 4 — Test:** `python3 -m py_compile` + `python3 scripts/vekayinuvis_doctor.py --help` çalışır; offline modda 17/18 server listelenir (ağ gerekmez).
- [ ] **Step 5: Commit** — `git add … && git commit -m "feat(vekayinuvis): doctor v3 — 22-araç drift raporu, engines, vnc probu, CLAUDE_PLUGIN_DATA"`

### Task 9: userConfig + hijyen + distiller modernizasyonu

**Files:**
- Modify: `plugins/vekayinuvis/.claude-plugin/plugin.json` (userConfig + redundant path temizliği)
- Modify: `plugins/vekayinuvis/.mcp.json` + `.codex-plugin/plugin.json` (header interpolasyonu)
- Modify: `plugins/vekayinuvis/agents/arsiv-tarama-distilleri.md`
- Move: `plugins/vekayinuvis/agents/openai.yaml` → `plugins/vekayinuvis/.codex-plugin/openai.yaml`
- Modify: `/mnt/thunderbolt/workspaces/CureoPrivate/.claude-plugin/marketplace.json` (strict:false kaldır — varsa)

**Interfaces:** Consumes: Task 1/6 .mcp.json hali. Produces: userConfig anahtar adları (README Task 10 belgeler): `devarsiv_api_key`, `ottoman_api_key`, `yok_akademik_api_key`, `openathens_api_key`, `annas_api_key`, `anamnesis_api_key`.

- [ ] **Step 1:** plugin.json `userConfig`'e 6 alan ekle (mevcut `smithery_api_key` biçimini kopyala; hepsi `"sensitive": true, "required": false`; description'da "girilmezse ortam değişkeni ${<ENV_ADI>} kullanılır" yazar).
- [ ] **Step 2:** `.mcp.json`'da 6 server'ın Authorization header'larını `Bearer ${user_config.<alan>:-${<MEVCUT_ENV>}}` biçimine çevir. ÖNCE tek server'da dene ve `claude` host'ta fallback sözdiziminin desteklenip desteklenmediğini yerinde doğrula (plugin'i geçici kur veya belge kontrolü); desteklenmiyorsa karar: header `${<MEVCUT_ENV>}` (env) KALIR ve userConfig alanlarının description'ı "değer girilirse ortam değişkenine dışarıdan yazılmalı" yönergesine çevrilir — hangisi seçildiyse README'ye tek-mekanizma olarak yazılır. Keychain bütçesi: 6 anahtarın gerçek uzunluk toplamını `wc -c` ile ölç (Doppler'dan), >1800 bayt ise yalnız devarsiv/ottoman/anamnesis userConfig'te kalır (README'ye not).
- [ ] **Step 3 — hijyen:** plugin.json'dan default'u tekrarlayan `"agents": "./agents"`, `"skills": "./skills"` alanlarını sil (hooks/mcpServers özel yolda — kalır); `git mv agents/openai.yaml .codex-plugin/`; `find plugins/vekayinuvis -type f -exec chmod 644 {} +` ve `chmod 755` script/hook .py'ler; marketplace.json'da vekayinuvis girdisinde `"strict": false` varsa kaldır.
- [ ] **Step 4 — distiller:** `agents/arsiv-tarama-distilleri.md` frontmatter'ına `disallowedTools: Write, Edit, mcp__devlet-arsivleri__devarsiv_add_to_cart, mcp__devlet-arsivleri__devarsiv_remove_from_cart, mcp__devlet-arsivleri__devarsiv_checkout_cart` ekle (mevcut frontmatter alan-adı üslubunu koru); gövdeye iki ek: (a) zarf zenginleştirme — her kayda `access` alanı ("purchased→/vekayinuvis:arsiv-oku ile okunur" / "purchasable: N sayfa ≈ X TL sepet adayı"); (b) AÇIK invariant: "Bu alt-ajan SEPETE DOKUNMAZ — add_to_cart/remove_from_cart/checkout_cart çağırmaz; satın-alma kararı ve mutasyonu ana asistanda, kullanıcı onayıyla."
- [ ] **Step 5: Doğrula + commit** — plugin.json + marketplace.json JSON-parse; `grep -n "openai.yaml" plugins/vekayinuvis/agents/` boş.
```bash
git add -A plugins/vekayinuvis .claude-plugin/marketplace.json
git commit -m "feat(vekayinuvis): userConfig 6 anahtar + hijyen paketi + distiller 'sepete dokunmaz' invariantı"
```

### Task 10: Sürümleme — plugin.json 3.0.0 + CHANGELOG + README + marketplace

**Files:**
- Modify: `plugins/vekayinuvis/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` (version+description)
- Modify: `plugins/vekayinuvis/CHANGELOG.md`, `plugins/vekayinuvis/README.md`, repo `README.md`, `.claude-plugin/marketplace.json` (sürüm alanı varsa)

- [ ] **Step 1:** İki plugin.json'da `"version": "3.0.0"`; description'ı v3 içeriğiyle güncelle (22-araç devarsiv, satın-alma→arşiv→çift-motor OCR→async zinciri, 17(+1) server, skills mimarisi). Keywords'e ekle: `esatis-sepet`, `novnc-satinalma`, `cift-motor-ocr`, `escriptorium-kraken`, `async-ocr`, `resmigazete`, `mulga-mevzuat`.
- [ ] **Step 2:** CHANGELOG v3.0.0 girdisi: BREAKING komut-ad tablosu (10 satır: `/vekayinuvis:vekayinuvis-durum` → `/vekayinuvis:durum` …), yeni 3 akış, 22-araç senkronu, filo 13→17(+1), hook fix'leri (clear BUG), userConfig, hijyen.
- [ ] **Step 3:** Plugin README: yeni akış bölümleri + userConfig kurulum + migration notu; repo README'de vekayinuvis satırı v3.0.0.
- [ ] **Step 4: Commit** — `git add -A && git commit -m "feat(vekayinuvis): v3.0.0 sürümleme — CHANGELOG migration tablosu + README"`

### Task 11: Validasyon + paket + kurulum smoke

**Files:**
- Create: `/mnt/thunderbolt/workspaces/CureoHub/vekayinuvis-plugin-3.0.0.zip` (+ `.sha256`)

- [ ] **Step 1 — plugin-validator:** `plugin-dev:plugin-validator` ajanını `plugins/vekayinuvis` üzerinde koştur; bulguları düzelt (yeniden koşarak temiz olduğunu doğrula).
- [ ] **Step 2 — statik gate:** tüm JSON'lar parse; `python3 -m py_compile plugins/vekayinuvis/hooks/scripts/*.py plugins/vekayinuvis/scripts/*.py`; `grep -rn "vekayinuvis-durum\|commands/" plugins/vekayinuvis --include="*.md" --include="*.json"` bayat referans döndürmez (CHANGELOG migration tablosu hariç).
- [ ] **Step 3 — zip paket:**
```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins
zip -r /mnt/thunderbolt/workspaces/CureoHub/vekayinuvis-plugin-3.0.0.zip vekayinuvis \
  -x "vekayinuvis/.codex-plugin/openai.yaml" # codex-yan dosyası pakete girer mi: plugin.json ile TUTARLI karar ver ve README'ye yaz
cd /mnt/thunderbolt/workspaces/CureoHub && sha256sum vekayinuvis-plugin-3.0.0.zip > vekayinuvis-plugin-3.0.0.zip.sha256
```
- [ ] **Step 4 — CureoPrivate push:** `git push` (GitHub `mahirkurt/CureoPrivate`) — marketplace dağıtımı bu repo üzerinden.
- [ ] **Step 5 — kurulum smoke (bilinen gotcha: kurulum sessiz düşebilir):** kullanıcının kurulu kopyasını güncelle; `claude plugin list 2>/dev/null | grep vekayinuvis` veya `grep -o '"vekayinuvis[^"]*"' ~/.claude/settings.json` ile `enabledPlugins` doğrula; yeni oturumda `/vekayinuvis:durum` çalıştırılabilirliğini raporla (etkileşimli adım kullanıcıya bırakılabilir — açıkça söyle).
- [ ] **Step 6 — final commit/rapor:** kalan değişiklikler commit; özet rapor (sürüm, komut kırılımı, doctor çıktısı, bilinen sınırlar: detsis durumu, connector yeniden-bağlama gereği).

## Self-review notları

- Spec kapsama: §4.1→T4/T5, §4.2→T1/T2/T3, §4.3→T3/T5, §4.4→T6, §4.5→T7/T8, §4.6→T9, §4.7→T0/T10/T11. Nice-notlar T3 Step 2/3 içinde. Boşluk yok.
- Tip/ad tutarlılığı: skill adları (satinalma/arsiv-oku/toplu-okuma), userConfig alan adları, doctor bölüm adları görevler arası tek biçimde tanımlandı.
- Placeholder taraması: karar-gerektiren iki nokta (userConfig fallback sözdizimi T9-S2; openai.yaml paketleme T11-S3) plan-içi karar prosedürüyle verildi — "TBD" yok.
