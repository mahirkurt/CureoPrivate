# edupedia

**MEB Türkiye Yüzyılı Maarif Modeli kazanımlarından DEHB-dostu, erişilebilir, kazanım-izlenebilir
etkileşimli öğrenim modülü üreticisi.**

`edupedia`, flagship `carbon-edupedia` skill'ini (IBM Carbon Design System v11 · WCAG 2.1 AA ·
8 mod · 16 kalite kapısı) **Maarif Modeli MCP** (`maarif-mufredat`) connector'ıyla paketleyen,
kurulur-kurulmaz connector'ı devreye alan, komut-yüzeyli bir Claude plugin'idir. Modüller
tek-dosya, bağımsız (offline çalışır), emojisiz ama ikon/piktogram/SVG zengindir; her olgusal
iddia bir MEB kazanım koduna izlenebilir (G-CURRICULUM provenansı).

## Kurulum ve Çoklu Platform Desteği

Plugin ve MCP konnektörleri tüm modern LLM ortamlarında tam uyumlulukla çalışır:
- **Claude Code (CLI)**: `doppler run -p cureohub -c dev_personal -- claude` (otomatik `.mcp.json` enjeksiyonu ve kancalar).
- **claude.ai (Web/Desktop)**: `python3 plugins/edupedia/scripts/build_claude_ai_skill.py` ile derlenen skill zip paketi + Custom Connectors.
- **Cursor IDE**: Composer & Agent Mode uyumlu `.cursor-plugin/` ve MCP Settings entegrasyonu.
- **ChatGPT / OpenAI Codex**: Developer Mode OAuth 2.1 RFC 9728 Custom Connector desteği.
- **Google Gemini / AI Studio**: Streamable HTTP MCP ve `oauth-redirect.googleusercontent.com` desteği.
- **VS Code / Roo Code / Cline / Windsurf / Claude Desktop**: Standart JSON MCP tanımları.

> Tüm platformlar için adım adım yapılandırma ve kopyalanabilir JSON blokları: **[KURULUM.md](./KURULUM.md)**.

## Komutlar

| Komut | Ne Yapar | Argüman |
|---|---|---|
| `/edupedia:modul` | Bir MEB kazanım kodundan kazanım-izlenebilir etkileşimli modül üretir | `<kazanım-kodu>` (örn. `FB.5.3.1.1`) |
| `/edupedia:mufredat` | Ders + sınıf + konudan kazanım keşfi → modül üretir | `<ders> <sınıf> <konu>` (örn. `Fen 5 hücre`) |
| `/edupedia:soru` | Bir veya birden fazla sınav sorusundan tek HTML üretir (fotoğraf veya metin) | `<soru fotoğrafı veya metni>` |
| `/edupedia:kazanim-bul` | Konuya denk gelen kazanımları KB becerisi ↔ etkileşim desenine haritalar (**üretim yok**) | `<konu> [sınıf] [ders]` |
| `/edupedia:durum` | `maarif-mufredat` + `egitim-kaynak` sağlığı + Tier-2 (`get_figure`) yeteneği | — |

İlk kez mi? `edupedia:start` skill'i oryantasyon + connector kontrolü + niyet→komut yönlendirmesi yapar.

## Skill'ler

- **carbon-edupedia** (flagship, v3.10.0) — kaynaktan/kazanımdan tek-dosya etkileşimli HTML öğrenim
  modülü. 8 mod (MODULE/QUIZ/FLASHCARDS/GAME/EXPLAINER/ASSESSMENT/SERIES/CURRICULUM), 16 kalite
  kapısı (G-EMOJI/G-CARBON/G-A11Y/G-INTERACT/G-SELFCONTAINED/G-CONTRAST/G-SVG/G-WELLBEING/G-VOICE/
  G-AUDIO/G-CURRICULUM/G-VERIFY/G-TOKEN/G-FLOW/G-CARBON-GRID/G-EXAM). Token otoritesi `@carbon/*` npm.
- **start** (yönlendirici, v1.2.0) — süit girişi ve yönlendirme.

## Connector

İki connector paketlenmiştir:

- **Maarif Modeli MCP** — `maarif-mufredat` · `https://mufredat.cureonics.com/mcp` ·
  **yalnız Türkiye MEB / Türkiye Yüzyılı Maarif Modeli (2024)** · 21 araç (dört küme: Keşif ·
  Kazanım · Beceri çerçevesi · Belge+medya). OAuth 2.1 / Bearer (`${MUFREDAT_MCP_API_KEY}`).
- **egitim-kaynak** — `egitim-kaynak` · `https://egitim-kaynak.cureonics.com/mcp` · açık
  eğitsel kaynak (OER) RAG · 6 araç (`kb_search`, `kb_for_outcome`, `kb_get`, `kb_patterns`,
  `kb_sources`, `kb_server_info`). Kazanımı Maarif verir, İÇERİĞİ bu zenginleştirir
  (kaynaklandırılmış, lisans-etiketli pasaj). **OAuth/Bearer — keyed** (2026-07-19 keyless→keyed;
  plugin-dışı Gemini/ChatGPT standalone için anahtarlandı). Claude Code'da `.mcp.json`
  `Bearer ${EGITIM_KAYNAK_MCP_API_KEY}` (Doppler `cureohub/dev_personal`); claude.ai'da OAuth.
  Connector display adı **"Eğitim Kaynakları"**.

  > **OTORİTE:** modülün olgusal dayanağı **`maarif-mufredat`**'tır — 105 MEB ders kitabı
  > **tam metin**. `egitim-kaynak` onun yerine geçmez, üstüne ekler. Çelişkide **ders kitabı
  > kazanır**.

  **Kaynaklar:** **PhET** (CC BY-NC 4.0, **atıf zorunlu**; korpusta **175 sim**, tamamı Türkçe
  — etkileşimli modülde en değerlisi; fizik/kimya/matematik güçlü, biyoloji ince) ·
  **Vikipedi-TR** (CC BY-SA 4.0 — 124 doğrulanmış müfredat kategorisi; fen, matematik, sosyal/tarih, coğrafya, Türkçe/edebiyat, felsefe, bilişim dalları — **arka plan/örnek, otorite değil**). *Vikikitap düşürüldü:
  9 aktif editör.* Getirme: **BM25 önce (Türkçe harf-katlama varyantlı), vektör YEDEK** (`bge-m3`/Workers AI) — RRF füzyonu
  2026-07-17'de kaldırıldı: ölçüm hibridi 3/8, saf BM25'i 6/8 verdi.

Tam envanter, kimlik/PDF uyarıları, provenans standardı ve Tier-1/Tier-2 görüntü-dayanak
politikası (Maarif MCP): **[CONNECTORS.md](./CONNECTORS.md)** (tek doğruluk kaynağı).
Tek-sefer disiplini ve `get_figure` yetenek-probu:
**[shared/canonical-cache-contract.md](./shared/canonical-cache-contract.md)**.

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

## Teslim

Üretilen modül **yerel tek-dosya HTML**'dir. Plugin yayınlamaz: `/edupedia:yayinla`,
`modul-yayin` ve `edupedia_publish` kaldırıldı (0.8.0). Kalite kapılarının otoritesi
yerel `scripts/validate_module.py`'dir.

## Genişleme

Bu plugin ileride `carbon-html-report` (statik rapor) ve `carbon-pptx` (slayt) sibling skill'leriyle
genişleyebilir; bunlar aynı `maarif-mufredat` connector sözleşmesini (CONNECTORS.md §7) paylaşır. Bu
sürümde yalnız `carbon-edupedia` + `start` paketlenmiştir.
