# Vekayinüvis Plugin

> *Vekāyi'-nüvîs* (وقايع نويس): Osmanlı Devleti'nin resmî tarih yazıcısı —
> arşivlere doğrudan erişimi olan akademik-bürokratik makam. Bu plugin, modern
> araştırmacıya o makamın çağdaş dijital eş değerini sunar: çok-arşivli erişim,
> kaynak hiyerarşisine sadakat, akademik yayın disiplini.

Birincil-kaynak-öncelikli **Osmanlı/Türk tarih araştırma orkestrasyon** Claude
Code plugin'i. Ottoman Archives, resmî Devlet Arşivleri kataloğu (22 araç —
eSatış sepeti, noVNC satın-alma, yerel BOA-kodlu arşiv, çift-motor OCR/HTR,
async job kuyruğu), YÖK Tez, DergiPark tam-metin, YÖK Akademik, akademik
triangülasyon katmanı, yasama/mevzuat katmanı (Resmî Gazete, mevzuat.gov.tr,
TBMM, DETSİS) ve OpenAthens/Anna's Reader tam-metin şelalesini anamnesis
RAG/GraphRAG substratıyla birleştirir; IJMES/TDV İslâm Ansiklopedisi
çeviriyazı standardı ve Chicago atıf disipliniyle **9 çalışma modu** + **3
sepet/arşiv/OCR akış-skill'i** sunar.

## İçindekiler

| Bileşen | Yol | Açıklama |
|---------|-----|----------|
| Flagship skill | `skills/vekayinuvis/SKILL.md` | 9-modlu tarih araştırma protokolü (v3.0.0) + 9 referans dosyası |
| Oryantasyon skill | `skills/start/SKILL.md` | Connector preflight + mod/akış yönlendirme |
| Mod skill'leri | `skills/{durum,kaynak-avi,arsiv-dalis,boa-katalog,literatur,transkripsiyon,prosopografi,kronoloji,rapor,kanun-gerekce}/SKILL.md` | 10 önek-siz skill (eski `commands/vekayinuvis-*.md`'den göçtü, bkz. **Sürüm 2.x → 3.0 Geçişi**) |
| Akış skill'leri (yeni v3.0) | `skills/{satinalma,arsiv-oku,toplu-okuma}/SKILL.md` | eSatış sepeti + noVNC satın-alma → yerel arşiv okuma → async çift-motor OCR zinciri (bkz. **Yeni Akışlar**) |
| Doctor script | `scripts/vekayinuvis_doctor.py` | Marketplace-portable tam-filo preflight + G0 kapsam manifestosu; `--live` ile `devlet-arsivleri` oturum + `[envanter]`/`[engines]`/`[vnc]` probeları |
| Connector envanteri | `CONNECTORS.md` | Tek doğruluk kaynağı — tam-filo, auth modeli, degrade kuralları |
| Transport | `.mcp.json` | 17 MCP sunucusu: çekirdek, akademik, tam-metin, yasama/mevzuat, destekleyici ve RAG substratı |

## Çalışma Modları

`SOURCE_HUNT` · `ARCHIVE_DEEP_DIVE` · `MANUSCRIPT_TRANSCRIBE` · `PROSOPOGRAPHY`
· `EVENT_RECONSTRUCTION` · `HISTORIOGRAPHY` · `CHRONOLOGY_CONVERSION` ·
`ACADEMIC_REPORT` · `KANUN_GEREKÇESİ`

Mod sayısı v3.0'da da **9** olarak korundu. Bunlara ek olarak, resmî
Devlet Arşivleri satın-alma/okuma zincirine özel **3 akış-skill'i**
(`satinalma` · `arsiv-oku` · `toplu-okuma`) eklendi — bkz. **Yeni Akışlar
(v3.0)** aşağıda.

## Kurulum

Marketplace deposu eklendikten sonra:

```bash
# Marketplace'i ekle (private GitHub deposu)
/plugin marketplace add mahirkurt/CureoPrivate

# Plugin'i kur
/plugin install vekayinuvis@cureonics-marketplace
```

Plugin `defaultEnabled: false` ile gelir (dış servislere bağlandığı için
opt-in). Etkinleştirme:

```bash
/plugin enable vekayinuvis@cureonics-marketplace
```

## MCP Connector Kurulumu

`.mcp.json` **17 sunucuyu** bundle eder (kategoriler `CONNECTORS.md § 1`'deki
katman tanımlarıyla birebir):

- **Çekirdek arşiv** (3): `ottoman-archives`, `devlet-arsivleri` (22 araç —
  arama/belge/eSatış sepeti/satın-alınmış-arşiv/async-OCR/durum), `yoktez`.
- **Akademik triangülasyon** (6): `literatur`, `consensus`, `scholar-gateway`,
  `exa`, `tavily`, `paper-search`.
- **Tam-metin şelalesi** (2): `openathens`, `annas-reader`.
- **Yasama/mevzuat** (3, yeni v3.0): `resmigazete`, `mevzuat`, `tbmm`.
- **Destekleyici** (2, `detsis` yeni v3.0): `yok-akademik` (modern
  akademisyen/ekol haritası), `detsis` (kurumsal prosopografi,
  Cumhuriyet-sınırlı).
- **Substrat** (1): `anamnesis` (RAG/GraphRAG bağlam ekonomisi).

(3+6+2+3+2+1 = 17. Tam liste, rol açıklamaları ve auth modeli için
**CONNECTORS.md § 1-3**.)

`marmara-mcp` (Turcademy/hukuk tam-metin) v3.0'da **tasarlanmıştı ama
kurulmadı** — `marmara.cureonics.com` DNS'i henüz yayınlanmamış (NXDOMAIN,
2026-07-12 üç bağımsız çözümleyiciyle doğrulandı); v3.1 adayı olarak
ertelendi (bkz. `CHANGELOG.md` [3.0.0]).

Auth'lu endpoint'ler bearer env var bekler; eksik anahtar veya kapalı oturum
SessionStart preflight'ta görünür ve ilgili katman manifestoda gerekçeli
degrade edilir. Ayrıntı için **CONNECTORS.md § 6**'ya bakın.

Kurulum sonrası hızlı sağlık kontrolü:

```bash
/vekayinuvis:durum
```

Komut, `scripts/vekayinuvis_doctor.py --live --write-manifest` ile 17 server
satırlı G0 preflight manifestosu üretir; `devlet-arsivleri` için
`devarsiv_session_status` canlılığını ve (v3.0 doctor) `[envanter]`
(`devarsiv_server_info` araç sayısının 22'ye göre drift'i), `[engines]`
(Transkribus/eScriptorium motor durumu) ve `[vnc]` (noVNC Access-gate probu)
bölümlerini kontrol eder. Bu bir araştırma koşusu değildir; belge görüntüsü,
OCR/HTR veya tam metin çekmez.

## userConfig Kurulumu

`plugin.json` `userConfig` bloğunda **6 hassas API-key alanı** tanımlıdır:
`devarsiv_api_key`, `ottoman_api_key`, `yok_akademik_api_key`,
`openathens_api_key`, `annas_api_key`, `anamnesis_api_key` (+ önceden var
olan `smithery_api_key`/`smithery_profile`). Tümü `sensitive: true`,
`required: false`; girilen değerler host'un sistem keychain'ine yazılır
(`settings.json`'a değil; toplam 6 anahtar ölçülen boyutu ~374 bayt).

**Önemli sınır — tek-mekanizma değil, çift-adım:** host'ta `userConfig`
alanından `.mcp.json` `Authorization` header'ına otomatik enjeksiyon
fallback sözdizimi (`${user_config.field:-${ENV}}` gibi) **belgelenmemiş**
(code.claude.com/docs doğrulandı). `.mcp.json` header'ları düz
`Bearer ${DEVARSIV_MCP_API_KEY}` vb. ortam-değişkeni biçiminde kalır. Bu
yüzden bu 6 alana `/plugin` enable-time'da bir değer girmek **tek başına
header'ı beslemez** — aynı anda ilgili ortam değişkenini de (Doppler /
`~/.dotfiles-ai/secrets/secrets.env`) dışa aktarmanız gerekir. `userConfig`
alanı girilmezse mevcut ortam değişkeni davranışı olduğu gibi kullanılmaya
devam eder (hiçbir mevcut kurulum kırılmaz).

## Yeni Akışlar (v3.0)

Resmî Devlet Arşivleri eSatış sepetini uçtan uca kapsayan üç yeni akış
skill'i (mod değil — `skills/vekayinuvis/SKILL.md`'in 9 modundan bağımsız,
`devlet-arsivleri` connector'ının sepet/arşiv/async araç gruplarına özel):

1. **`/vekayinuvis:satinalma`** — eSatış sepet + noVNC satın-alma. Karar
   matrisi (kaç sayfa, tahminî maliyet) → `devarsiv_add_to_cart` (1-tabanlı
   sayfa seçimi) → `devarsiv_list_cart` ile **metin-onay kapısı** (kullanıcı
   sepeti Tutar sütunuyla birlikte onaylamadan ödemeye geçilmez) → noVNC
   (`https://devarsiv-vnc.cureonics.com/vnc.html`) ile insan ödemesi.
   **Ödeme HER ZAMAN insan tarafından, noVNC üzerinden yapılır — asistan
   asla otonom ödeme yapmaz.** Tek-cihaz uyarısı: "Kendi cihazınızdan
   kataloğa GİRMEYİN — tek-cihaz kilidi HP oturumunu düşürür." Fiyat dili:
   "~0,50 TL/sayfa TAHMİNDİR; bağlayıcı tutar `devarsiv_list_cart`
   çıktısındaki Tutar sütunudur."
2. **`/vekayinuvis:arsiv-oku`** — satın-alınmış belgeyi yerel BOA-kodlu
   arşivden **300 DPI görüyle**, sayfa-sayfa okur (`devarsiv_list_archive` →
   `devarsiv_get_archive_page`). Arşiv-öncelikli okuma kuralı: satın-alınmış
   belgede okuma DAİMA yerel arşivden başlar; katalog önizlemesi yalnız
   satın-alınmamış belgeler içindir.
3. **`/vekayinuvis:toplu-okuma`** — çok-sayfalı satın-alınmış belgede async
   çift-motor OCR + anamnesis ingest. Sync/async karar kuralı (K4): ≤5
   sayfa VE tek motor → sync `devarsiv_ocr_archive_pages`; >5 sayfa VEYA
   `engine="both"` tam belge → async `devarsiv_ocr_submit` →
   `devarsiv_ocr_result` poll → `done`'da tek-sefer tam metin →
   `anamnesis.ingest_document` → sonraki sorgular `hybrid_query`. `stale`
   durumunda aynı parametrelerle resubmit edilir (yerel PDF; maliyet
   tekrarlanmaz).

Motor konvansiyonu (`engine=auto|both|transkribus|escriptorium|tesseract`,
Osmanlı varsayılanı `both` — Transkribus PyLaia el yazması + eScriptorium
Kraken basılı PARALEL, görü birincil/HTR yardımcı) tüm üç akışta ve
`/vekayinuvis:transkripsiyon` skill'inde ortaktır.

## Sürüm 2.x → 3.0 Geçişi (Migration)

**BREAKING:** `commands/` dizini kaldırıldı; 10 slash komutu önek almadan
skill adıyla çağrılan `skills/<ad>/SKILL.md`'e taşındı:

| Eski (v2.x) | Yeni (v3.0) |
|---|---|
| `/vekayinuvis:vekayinuvis-durum` | `/vekayinuvis:durum` |
| `/vekayinuvis:vekayinuvis-kaynak-avi` | `/vekayinuvis:kaynak-avi` |
| `/vekayinuvis:vekayinuvis-arsiv-dalis` | `/vekayinuvis:arsiv-dalis` |
| `/vekayinuvis:vekayinuvis-boa-katalog` | `/vekayinuvis:boa-katalog` |
| `/vekayinuvis:vekayinuvis-literatur` | `/vekayinuvis:literatur` |
| `/vekayinuvis:vekayinuvis-transkripsiyon` | `/vekayinuvis:transkripsiyon` |
| `/vekayinuvis:vekayinuvis-prosopografi` | `/vekayinuvis:prosopografi` |
| `/vekayinuvis:vekayinuvis-kronoloji` | `/vekayinuvis:kronoloji` |
| `/vekayinuvis:vekayinuvis-rapor` | `/vekayinuvis:rapor` |
| `/vekayinuvis:vekayinuvis-kanun-gerekce` | `/vekayinuvis:kanun-gerekce` |

Ayrıca: `devlet-arsivleri` 10→22 araca genişledi (eSatış sepeti + satın-
alınmış/yerel-arşiv + async OCR); filo 13→17 server'a genişledi
(`resmigazete`/`mevzuat`/`tbmm`/`detsis`); `userConfig`'e 6 yeni alan
eklendi (yukarıya bakın). Tam ayrıntı için `CHANGELOG.md` `[3.0.0]`
girdisine bakın. Eski `2.x` kurulumlarda bir güncelleme sonrası eski komut
adlarını kullanan otomasyon/döküman varsa yeni `/vekayinuvis:<ad>` biçimine
güncellenmelidir.

## Önemli Sınırlar

- **Restricted-kaynak disiplini**: erişim-kısıtlı arşivlerde plugin katalog
  bilgisi, kayıt numarası, fond yapısı ve erişim prosedürü verir; içerik ancak
  gerçek tarama/OCR/HTR çıktısı veya kullanıcı doğrulaması varsa yazılır.
  Satın alınmış Devlet Arşivleri belgelerinde çok-sayfa OCR/HTR desteklenir;
  satın alınmamış belgelerde önizleme sınırı dürüstçe raporlanır.
- **Ödeme asla otonom değil**: eSatış sepeti state-changing'dir (sepete
  ekleme/çıkarma) ama `devarsiv_checkout_cart` ödeme YAPMAZ — yalnız noVNC
  URL'i döner; fiilî ödeme HER ZAMAN insan tarafından noVNC üzerinden
  yapılır (bkz. **Yeni Akışlar (v3.0)**).
- **Güvenlik**: public bir depoda `.mcp.json` URL'leri görünür olur; gizli
  değerler env var veya userConfig üzerinden gelir, pakete secret gömülmez.
- Plugin, gerçek arşiv çalışmasının yerini almaz; o çalışmanın **ön
  araştırması, kaynak haritalandırması ve raporlama altyapısını** sağlar.

## Composability

- **Upstream**: `medical-research` (tıp tarihi modern literatür), `lex-sanitas`
  (mevzuat tarih bölümü kapsamı), `lex-mercator`, `psychdev`.
- **Downstream**: `carbon-html-report` (A4 print PDF), `carbon-pptx` (komite
  sunumu), `lex-sanitas` (kanun gerekçesi tarihî bölümü geri beslemesi).

## Doğrulama

```bash
claude plugin validate ./plugins/vekayinuvis --strict
python3 ./plugins/vekayinuvis/scripts/vekayinuvis_doctor.py --topic preflight --live
```

## Sürüm

- Plugin paketi: `v3.0.0`
- Flagship skill: `v3.0.0` (bkz. `CHANGELOG.md`)
