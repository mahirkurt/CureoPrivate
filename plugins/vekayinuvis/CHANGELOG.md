# Changelog — Vekayinüvis Plugin

Bu plugin [Semantic Versioning](https://semver.org/lang/tr/) kullanır.
Flagship skill kendi sürüm geçmişini `skills/vekayinuvis/SKILL.md` frontmatter
`changelog` alanında tutar.

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
