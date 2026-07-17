# edupedia

**MEB Türkiye Yüzyılı Maarif Modeli kazanımlarından DEHB-dostu, erişilebilir, kazanım-izlenebilir
etkileşimli öğrenim modülü üreticisi.**

`edupedia`, flagship `carbon-edupedia` skill'ini (IBM Carbon Design System v11 · WCAG 2.1 AA ·
8 mod · 14 kalite kapısı) **Maarif Modeli MCP** (`maarif-mufredat`) connector'ıyla paketleyen,
kurulur-kurulmaz connector'ı devreye alan, komut-yüzeyli bir Claude plugin'idir. Modüller
tek-dosya, bağımsız (offline çalışır), emojisiz ama ikon/piktogram/SVG zengindir; her olgusal
iddia bir MEB kazanım koduna izlenebilir (G-CURRICULUM provenansı).

## Kurulum

Plugin yüklendiğinde `maarif-mufredat` connector'ı (`.mcp.json`) otomatik devreye girer — ayrı
bir kurulum adımı gerekmez, auth yoktur (public read-only). Doğrulamak için `/edupedia:durum`.

## Komutlar

| Komut | Ne Yapar | Argüman |
|---|---|---|
| `/edupedia:modul` | Bir MEB kazanım kodundan kazanım-izlenebilir etkileşimli modül üretir | `<kazanım-kodu>` (örn. `FB.5.3.1.1`) |
| `/edupedia:mufredat` | Ders + sınıf + konudan kazanım keşfi → modül üretir | `<ders> <sınıf> <konu>` (örn. `Fen 5 hücre`) |
| `/edupedia:kazanim-bul` | Konuya denk gelen kazanımları KB becerisi ↔ etkileşim desenine haritalar (**üretim yok**) | `<konu> [sınıf] [ders]` |
| `/edupedia:yayinla` | Üretilen modülü `edupedia.cureonics.com`'da yayınlar, public bağlantı verir | `<modul.html yolu>` |
| `/edupedia:durum` | `maarif-mufredat` connector sağlığı + Tier-2 (`get_figure`) yeteneği + önbellek durumu | — |

İlk kez mi? `edupedia:start` skill'i oryantasyon + connector kontrolü + niyet→komut yönlendirmesi yapar.

## Skill'ler

- **carbon-edupedia** (flagship, v3.3.0) — kaynaktan/kazanımdan tek-dosya etkileşimli HTML öğrenim
  modülü. 8 mod (MODULE/QUIZ/FLASHCARDS/GAME/EXPLAINER/ASSESSMENT/SERIES/CURRICULUM), 13 kalite
  kapısı (G-EMOJI/G-CARBON/G-A11Y/G-INTERACT/G-SELFCONTAINED/G-CONTRAST/G-SVG/G-WELLBEING/G-AUDIO/
  G-CURRICULUM/G-TOKEN/G-FLOW/G-CARBON-GRID). Token otoritesi `@carbon/*` npm.
- **start** (yönlendirici, v1.0.0) — süit girişi ve yönlendirme.

## Connector

İki connector paketlenmiştir:

- **Maarif Modeli MCP** — `maarif-mufredat` · `https://mufredat.cureonics.com/mcp` ·
  **yalnız Türkiye MEB / Türkiye Yüzyılı Maarif Modeli (2024)** · 21 araç (dört küme: Keşif ·
  Kazanım · Beceri çerçevesi · Belge+medya). Auth yok (public read-only).
- **egitim-kaynak** — `egitim-kaynak` · `https://egitim-kaynak.cureonics.com/mcp` · açık
  eğitsel kaynak (OER) RAG · 6 araç (`kb_search`, `kb_for_outcome`, `kb_get`, `kb_patterns`,
  `kb_sources`, `kb_server_info`). Kazanımı Maarif verir, İÇERİĞİ bu zenginleştirir
  (kaynaklandırılmış, lisans-etiketli pasaj). **Anahtarsız — secret gerekmez** (salt-okunur,
  korpus tamamen açık lisanslı; `titck-cache-mcp` emsali).

  > **OTORİTE:** modülün olgusal dayanağı **`maarif-mufredat`**'tır — 105 MEB ders kitabı
  > **tam metin**. `egitim-kaynak` onun yerine geçmez, üstüne ekler. Çelişkide **ders kitabı
  > kazanır**.

  **Kaynaklar:** **PhET** (CC BY-NC 4.0, **atıf zorunlu**; korpusta **175 sim**, tamamı Türkçe
  — etkileşimli modülde en değerlisi; fizik/kimya/matematik güçlü, biyoloji ince) ·
  **Vikipedi-TR** (CC BY-SA 4.0 — **arka plan/örnek, otorite değil**). *Vikikitap düşürüldü:
  9 aktif editör.* Getirme: **BM25 önce, vektör YEDEK** (`bge-m3`/Workers AI) — RRF füzyonu
  2026-07-17'de kaldırıldı: ölçüm hibridi 3/8, saf BM25'i 6/8 verdi.
- **modul-yayin** — `modul-yayin` · `https://edupedia.cureonics.com/mcp` · yayın connector'ı · 4
  araç (`edupedia_publish`, `edupedia_list`, `edupedia_unpublish`, `edupedia_server_info`).
  Tek-kiracılı OAuth 2.1; Claude Code'da `.mcp.json` üzerinden `EDUPEDIA_PUBLISH_TOKEN`
  bearer'ı, claude.ai'de connector ayarlarında OAuth ile bağlanır. *(Eski adı `edupedia`;
  MCP connector'ı plugin adıyla çakışmasın diye yeniden adlandırıldı — endpoint/token aynı.)*

Tam envanter, kimlik/PDF uyarıları, provenans standardı ve Tier-1/Tier-2 görüntü-dayanak
politikası (Maarif MCP): **[CONNECTORS.md](./CONNECTORS.md)** (tek doğruluk kaynağı — yayın
connector'ı `modul-yayin` ve RAG connector'ı `egitim-kaynak` de burada tanımlıdır). Tek-sefer disiplini ve `get_figure`
yetenek-probu: **[shared/canonical-cache-contract.md](./shared/canonical-cache-contract.md)**.

### Görüntü-dayanak (Tier-1 / Tier-2)

- **Tier-1 (garanti):** kazanım koduna izlenebilir olgular + yazar-üretimli tema-duyarlı SVG.
  Varsayılan ve zorunlu yol; `validate_module.py` G-CURRICULUM + G-SVG kapılarıyla denetlenir.
- **Tier-2 (best-effort):** `get_figure(include_image=true)` → resmî ders-kitabı görselinin base64
  gömülmesi. Yalnız yetenek-probu geçerse; herhangi bir hata/timeout/boş dönüşte **sessizce Tier-1'e
  düşülür**, üretim asla bloke olmaz. (Introspeksiyon 2026-07-06: `get_figure` connector'da **mevcut**.)

## Kapsam

**Yalnız Türkiye MEB.** Yabancı müfredat (IB/Cambridge), üniversite içeriği, genel React UI, statik
baskı raporu (→ `carbon-html-report`) veya slayt (→ `carbon-pptx`) kapsam dışıdır. Erişilebilirlik
(WCAG 2.1 AA) ve emojisizlik skill sözleşmesi gereği korunur.

## Yayınlama

Üretilen modüller `/edupedia:yayinla` ile **edupedia.cureonics.com**'a yayınlanır
(Pi'de host edilen Carbon kataloglu site; okuma public, yayın token'lı). İki yol vardır —
komut hangisinin bağlı olduğuna göre otomatik seçer:

- **MCP yolu (tercih edilen):** `modul-yayin` connector'ı (`.mcp.json`, OAuth'lu) bağlıysa
  `edupedia_publish` aracı doğrudan çağrılır. Manifest dosyası istemci tarafında
  kurulmaz — sunucu manifesti `run_id`/`requested_scope` düz alanlarından (html, run_id,
  subject_slug, grade, topic, mode, outcome_codes) kendisi kurar ve kalite kapılarını
  kendisi ölçer. claude.ai'de bu yol tek başına yeterlidir: HTML dosyaya hiç yazılmadan
  doğrudan `edupedia_publish`'in `html` argümanına üretilip yayınlanabilir.
- **REST yolu (yedek):** `edupedia_publish` aracı yoksa (tipik salt Claude Code oturumu),
  `/edupedia:modul` / `/edupedia:mufredat` üretim akışlarının son adımında yazılan
  HTML + aynı ad + `.manifest.json` run-manifest ikilisi `POST /api/publish` ile
  `EDUPEDIA_PUBLISH_TOKEN` bearer'ıyla gönderilir (bkz. `shared/canonical-cache-contract.md §1`).

Her iki yolda da kalite kapılarının OTORİTESİ sunucudur — istemcinin beyanı yok sayılır.

- Modül kalıcı bir adres alır: `edupedia.cureonics.com/m/<slug>` — link asla değişmez.
- Yeniden yayın sürümü artırır; eski sürüm `/m/<slug>/v<N>` altında kalır.
- Bir kalite kapısı `FAIL` ise yayın reddedilir (`force` ile geçilebilir) —
  siteye emojili, erişilemez veya kazanım-izlenemez modül düşmez.
- Her iki yolda da: sunucudan `url` dönmediyse "yayınlandı" denmez.

Yayın token'ı Doppler'da (`cureohub` / `dev_personal` / `EDUPEDIA_PUBLISH_TOKEN`); Claude
Code'da REST yolu için oturumu `doppler run -p cureohub -c dev_personal -- claude` ile
başlatın. claude.ai'de aynı token, connector ayarlarında OAuth ile bağlanır — sohbete
hiç girmez.

## Genişleme

Bu plugin ileride `carbon-html-report` (statik rapor) ve `carbon-pptx` (slayt) sibling skill'leriyle
genişleyebilir; bunlar aynı `maarif-mufredat` connector sözleşmesini (CONNECTORS.md §7) paylaşır. Bu
sürümde yalnız `carbon-edupedia` + `start` paketlenmiştir.
