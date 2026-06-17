# Vekayinüvis Plugin

> *Vekāyi'-nüvîs* (وقايع نويس): Osmanlı Devleti'nin resmî tarih yazıcısı —
> arşivlere doğrudan erişimi olan akademik-bürokratik makam. Bu plugin, modern
> araştırmacıya o makamın çağdaş dijital eş değerini sunar: çok-arşivli erişim,
> kaynak hiyerarşisine sadakat, akademik yayın disiplini.

Birincil-kaynak-öncelikli **Osmanlı/Türk tarih araştırma orkestrasyon** Claude
Code plugin'i. Ottoman Archives (33 kaynak) + YÖK Tez çekirdek MCP katmanını
akademik triangülasyon katmanıyla birleştirir; IJMES/TDV İslâm Ansiklopedisi
çeviriyazı standardı ve Chicago atıf disipliniyle **9 çalışma modu** sunar.

## İçindekiler

| Bileşen | Yol | Açıklama |
|---------|-----|----------|
| Flagship skill | `skills/vekayinuvis/SKILL.md` | 9-modlu tarih araştırma protokolü (v1.3) + 8 referans dosyası |
| Oryantasyon skill | `skills/start/SKILL.md` | Connector preflight + mod yönlendirme |
| Slash komutları | `commands/*.md` | `/vekayinuvis-kaynak-avi`, `-arsiv-dalis`, `-transkripsiyon`, `-prosopografi`, `-kronoloji`, `-rapor`, `-kanun-gerekce` |
| Connector envanteri | `CONNECTORS.md` | Tek doğruluk kaynağı — çekirdek + tamamlayıcı katman, auth modeli |
| Transport | `.mcp.json` | Çekirdek MCP sunucuları (ottoman-archives, yoktez) |

## Çalışma Modları

`SOURCE_HUNT` · `ARCHIVE_DEEP_DIVE` · `MANUSCRIPT_TRANSCRIBE` · `PROSOPOGRAPHY`
· `EVENT_RECONSTRUCTION` · `HISTORIOGRAPHY` · `CHRONOLOGY_CONVERSION` ·
`ACADEMIC_REPORT` · `KANUN_GEREKÇESİ`

## Kurulum

Marketplace deposu eklendikten sonra:

```bash
# Marketplace'i ekle (private GitHub deposu)
/plugin marketplace add mahirkurt/marketplace

# Plugin'i kur
/plugin install vekayinuvis@cureonics-marketplace
```

Plugin `defaultEnabled: false` ile gelir (dış servislere bağlandığı için
opt-in). Etkinleştirme:

```bash
/plugin enable vekayinuvis@cureonics-marketplace
```

## MCP Connector Kurulumu

**Çekirdek katman** (`.mcp.json`'da bundled — plugin etkinleşince otomatik
başlar):
- `ottoman-archives` — Cloud Run (kendi altyapın)
- `yoktez` — FastMCP host

İlk kullanımda kimlik doğrulama gerekiyorsa `/mcp` ile tarayıcı akışını
tamamlayın. Endpoint'lerin auth modeli için **CONNECTORS.md § 6**'ya bakın.

**Tamamlayıcı katman** (opsiyonel — akademik triangülasyonu zenginleştirir):
`paper-search`, `consensus`, `scholar-gateway`, `exa`, `tavily`. Bunları
plugin'e bundle etmek için CONNECTORS.md § 4'teki genişletilmiş `.mcp.json`
snippet'ini ve § 5'teki `userConfig` bloğunu kullanın; ya da hesap düzeyinde
zaten bağlıysanız olduğu gibi bırakın.

## Önemli Sınırlar

- **Restricted-kaynak disiplini**: erişim-kısıtlı arşivlerde (BOA, TKGM, ATASE,
  İSAM, Süleymaniye, Millet Yazma, Topkapı, IRCICA, Müteferriqa) plugin **belge
  içeriği üretmez** — yalnız katalog-bilgisi, kayıt-numarası, fond-yapısı ve
  erişim prosedürü sağlar. Atıfta bulunulan içerik, kullanıcının kendi arşiv
  çalışmasından doğrulanmalıdır.
- **Güvenlik**: public bir depoda `.mcp.json` URL'leri herkese görünür olur;
  `ottoman-archives` Cloud Run endpoint'i için **private Gitea** önerilir.
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
```

## Sürüm

- Plugin paketi: `v1.0.0`
- Flagship skill: `v1.3.0` (bkz. `CHANGELOG.md`)
