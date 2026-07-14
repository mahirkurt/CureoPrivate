# edupedia

**MEB Türkiye Yüzyılı Maarif Modeli kazanımlarından DEHB-dostu, erişilebilir, kazanım-izlenebilir
etkileşimli öğrenim modülü üreticisi.**

`edupedia`, flagship `carbon-edupedia` skill'ini (IBM Carbon Design System v11 · WCAG 2.1 AA ·
8 mod · 13 kalite kapısı) **Maarif Modeli MCP** (`maarif-mufredat`) connector'ıyla paketleyen,
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

Tek connector: **Maarif Modeli MCP** — `maarif-mufredat` · `https://mufredat.cureonics.com/mcp` ·
**yalnız Türkiye MEB / Türkiye Yüzyılı Maarif Modeli (2024)** · 21 araç (dört küme: Keşif · Kazanım ·
Beceri çerçevesi · Belge+medya). Tam envanter, kimlik/PDF uyarıları, provenans standardı ve
Tier-1/Tier-2 görüntü-dayanak politikası: **[CONNECTORS.md](./CONNECTORS.md)** (tek doğruluk kaynağı).
Tek-sefer disiplini ve `get_figure` yetenek-probu: **[shared/canonical-cache-contract.md](./shared/canonical-cache-contract.md)**.

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
(Pi'de host edilen Carbon kataloglu site; okuma public, yayın token'lı). `/edupedia:modul` ve
`/edupedia:mufredat` üretim akışlarının son adımı, HTML ile aynı dizine aynı ad +
`.manifest.json` ile bir run-manifest yazar (gerçek `validate_module.py` kalite-kapısı
sonuçlarıyla); `/edupedia:yayinla` yalnız bu manifesti okur (bkz. `shared/canonical-cache-contract.md §1`).

- Modül kalıcı bir adres alır: `edupedia.cureonics.com/m/<slug>` — link asla değişmez.
- Yeniden yayın sürümü artırır; eski sürüm `/m/<slug>/v<N>` altında kalır.
- Manifest'te bir kalite kapısı `FAIL` ise yayın reddedilir (`force` ile geçilebilir) —
  siteye emojili, erişilemez veya kazanım-izlenemez modül düşmez.

Yayın token'ı Doppler'da (`cureohub` / `dev_personal` / `EDUPEDIA_PUBLISH_TOKEN`);
oturumu `doppler run -p cureohub -c dev_personal -- claude` ile başlatın.

## Genişleme

Bu plugin ileride `carbon-html-report` (statik rapor) ve `carbon-pptx` (slayt) sibling skill'leriyle
genişleyebilir; bunlar aynı `maarif-mufredat` connector sözleşmesini (CONNECTORS.md §7) paylaşır. Bu
sürümde yalnız `carbon-edupedia` + `start` paketlenmiştir.
