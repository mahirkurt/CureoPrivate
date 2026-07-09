# Vekayinüvis Plugin

> *Vekāyi'-nüvîs* (وقايع نويس): Osmanlı Devleti'nin resmî tarih yazıcısı —
> arşivlere doğrudan erişimi olan akademik-bürokratik makam. Bu plugin, modern
> araştırmacıya o makamın çağdaş dijital eş değerini sunar: çok-arşivli erişim,
> kaynak hiyerarşisine sadakat, akademik yayın disiplini.

Birincil-kaynak-öncelikli **Osmanlı/Türk tarih araştırma orkestrasyon** Claude
Code plugin'i. Ottoman Archives, resmî Devlet Arşivleri kataloğu, YÖK Tez,
DergiPark tam-metin, YÖK Akademik ve akademik triangülasyon katmanını
OpenAthens/Anna's Reader tam-metin şelalesi ve anamnesis RAG/GraphRAG
substratıyla birleştirir; IJMES/TDV İslâm Ansiklopedisi çeviriyazı standardı
ve Chicago atıf disipliniyle **9 çalışma modu** sunar.

## İçindekiler

| Bileşen | Yol | Açıklama |
|---------|-----|----------|
| Flagship skill | `skills/vekayinuvis/SKILL.md` | 9-modlu tarih araştırma protokolü (v2.4.0) + 9 referans dosyası |
| Oryantasyon skill | `skills/start/SKILL.md` | Connector preflight + mod yönlendirme |
| Slash komutları | `commands/*.md` | 9 komut: `/vekayinuvis-kaynak-avi`, `-arsiv-dalis`, `-boa-katalog`, `-literatur`, `-transkripsiyon`, `-prosopografi`, `-kronoloji`, `-rapor`, `-kanun-gerekce` |
| Connector envanteri | `CONNECTORS.md` | Tek doğruluk kaynağı — tam-filo, auth modeli, degrade kuralları |
| Transport | `.mcp.json` | 13 MCP sunucusu: çekirdek, akademik, tam-metin ve RAG substratı |

## Çalışma Modları

`SOURCE_HUNT` · `ARCHIVE_DEEP_DIVE` · `MANUSCRIPT_TRANSCRIBE` · `PROSOPOGRAPHY`
· `EVENT_RECONSTRUCTION` · `HISTORIOGRAPHY` · `CHRONOLOGY_CONVERSION` ·
`ACADEMIC_REPORT` · `KANUN_GEREKÇESİ`

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

`.mcp.json` 13 sunucuyu bundle eder: `ottoman-archives`, `devlet-arsivleri`,
`yoktez`, `literatur`, `yok-akademik`, `consensus`, `scholar-gateway`, `exa`,
`tavily`, `paper-search`, `openathens`, `annas-reader`, `anamnesis`.
Auth'lu endpoint'ler bearer env var bekler; eksik anahtar veya kapalı oturum
SessionStart preflight'ta görünür ve ilgili katman manifestoda gerekçeli
degrade edilir. Ayrıntı için **CONNECTORS.md § 6**'ya bakın.

## Önemli Sınırlar

- **Restricted-kaynak disiplini**: erişim-kısıtlı arşivlerde plugin katalog
  bilgisi, kayıt numarası, fond yapısı ve erişim prosedürü verir; içerik ancak
  gerçek tarama/OCR/HTR çıktısı veya kullanıcı doğrulaması varsa yazılır.
  Satın alınmış Devlet Arşivleri belgelerinde çok-sayfa OCR/HTR desteklenir;
  satın alınmamış belgelerde önizleme sınırı dürüstçe raporlanır.
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
```

## Sürüm

- Plugin paketi: `v2.4.0`
- Flagship skill: `v2.4.0` (bkz. `CHANGELOG.md`)
