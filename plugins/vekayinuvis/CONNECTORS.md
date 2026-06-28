# CONNECTORS.md — Vekayinüvis Plugin Connector Envanteri

> **Tek doğruluk kaynağı.** Bu dosya, `vekayinuvis` plugin süitinin tüm MCP
> connector bağımlılıklarını, kimlik doğrulama modelini, fallback zincirlerini
> ve mod → connector eşlemesini tanımlar. Skill'ler ve `start` oryantasyonu bu
> dosyaya referans verir. Transport (uzak MCP URL) tanımı için kanonik dosya
> `../.mcp.json`'dur.

---

## 1. Connector Katmanları

Vekayinüvis iki katmanlı bir connector mimarisi kullanır:

- **Çekirdek katman (bundled)** — plugin `.mcp.json`'unda doğrudan bildirilir;
  kurulduğunda otomatik başlar. Bunlar alana-özgü, genel-amaçlı olmayan,
  plugin'in varlık sebebini tanımlayan sunuculardır.
- **Tamamlayıcı katman (companion)** — akademik triangülasyonu zenginleştiren
  genel-amaçlı connector'lar. `.mcp.json`'a varsayılan eklenmez (kullanıcının
  hesap düzeyinde zaten bağlı olabileceği ve isim çakışması riskini önlemek
  için). Tam-kapsayıcı kurulum isteyen kullanıcı için § 4'teki snippet ile
  bundle edilebilir.

---

## 2. Çekirdek Katman (`.mcp.json`'da bundled)

| Sunucu adı | Transport | URL | Rol | Kimlik doğrulama |
|---|---|---|---|---|
| `ottoman-archives` | http | `https://ottoman-archives-to7lqjgdkq-ew.a.run.app/mcp` | 33-kaynaklı Osmanlı arşiv keşfi + IIIF tam-metin + Hicri/Rumî/Miladi çevirici + ebced + eScriptorium HTR + TDV İslâm Ansiklopedisi | Cloud Run dağıtımı — endpoint'in auth modeline göre `/mcp` üzerinden doğrulama gerekebilir |
| `yoktez` | http | `https://yoktezmcp.fastmcp.app/mcp` | YÖK Ulusal Tez Merkezi — tahrir/mühimme/şer'iye sicili transkripsiyon tezleri, anabilim dalı bazlı arama | FastMCP host — gerekirse `/mcp` OAuth akışı |

**Ottoman Archives yetenek katmanları** (skill § 3.1): A. Kaynak Keşfi ·
B. Tam-Metin Arama · C. Belge/Metin Çekme · D. Hesaplama/Yardımcı (tarih, ebced,
defter şeması) · E. HTR Pipeline (opt-in eScriptorium).

---

## 3. Tamamlayıcı Katman (companion — opsiyonel bundle / hesap düzeyi)

Akademik triangülasyon katmanı (skill § 3.2). Bunlar **olmadan da** plugin
çalışır (çekirdek katman + Anthropic yerleşik `web_search`/`web_fetch` yeterli
asgari işlevi sağlar), ancak bağlı olduklarında kanıt sentezi belirgin
zenginleşir.

| Sunucu adı | Transport | URL | Rol | Kimlik doğrulama notu |
|---|---|---|---|---|
| `paper-search` | http | `https://server.smithery.ai/@adamamer20/paper-search-mcp-openai` | Google Scholar tam aralığı + Semantic Scholar + CrossRef + PubMed (tıp tarihi) + arXiv (DH) | **Smithery-host** — genelde URL query veya header'da `api_key` ister; § 4'te `userConfig` ile yönetilir |
| `consensus` | http | `https://mcp.consensus.app/mcp` | Hakemli makale sentezi | OAuth 2.0 → ilk kullanımda `/mcp` tarayıcı akışı |
| `scholar-gateway` | http | `https://connector.scholargateway.ai/mcp` | Tam-metin akademik korpus + pasaj-düzeyi atıf | OAuth / sağlayıcıya göre key |
| `exa` | http | `https://mcp.exa.ai/mcp` | Akademik blog, kurum sayfası, ansiklopedi entries | OAuth veya Exa API key |
| `tavily` | http | `https://mcp.tavily.com/mcp` | Geniş web tarama, çok-sayfa araştırma, crawl | OAuth veya Tavily API key |

> **Anthropic yerleşik araçları** (her zaman mevcut, MCP gerektirmez):
> `web_search`, `web_fetch`, `google_drive_search`, `google_drive_fetch`.
> Tamamlayıcı connector'lar bağlı değilse bunlar fallback olarak devreye girer.

---

## 4. Tam Orkestrasyon `.mcp.json` Snippet'i (opsiyonel)

Plugin'i tamamen kendi-içine-kapalı (self-contained) hale getirmek isteyen
kullanıcı, `.mcp.json`'u aşağıdaki **genişletilmiş** sürümle değiştirebilir.
API-key gerektiren sunucular `userConfig` ile parametrelenir; bu durumda
`plugin.json`'a karşılık gelen `userConfig` bloğu eklenmelidir (§ 5).

```json
{
  "mcpServers": {
    "ottoman-archives": {
      "type": "http",
      "url": "https://ottoman-archives-to7lqjgdkq-ew.a.run.app/mcp"
    },
    "yoktez": {
      "type": "http",
      "url": "https://yoktezmcp.fastmcp.app/mcp"
    },
    "consensus": {
      "type": "http",
      "url": "https://mcp.consensus.app/mcp"
    },
    "scholar-gateway": {
      "type": "http",
      "url": "https://connector.scholargateway.ai/mcp"
    },
    "exa": {
      "type": "http",
      "url": "https://mcp.exa.ai/mcp"
    },
    "tavily": {
      "type": "http",
      "url": "https://mcp.tavily.com/mcp"
    },
    "paper-search": {
      "type": "http",
      "url": "https://server.smithery.ai/@adamamer20/paper-search-mcp-openai/mcp?api_key=${user_config.smithery_api_key}&profile=${user_config.smithery_profile}"
    }
  }
}
```

> **Uyarı.** `consensus`, `scholar-gateway`, `exa`, `tavily` sunucularının
> OAuth mu yoksa statik API-key mi istediği endpoint'e göre değişir. OAuth
> destekleyenler için yalnız `url` yeterlidir (kimlik doğrulama `/mcp`
> üzerinden). Statik key isteyen bir endpoint varsa, ilgili sunucuyu da
> `paper-search` gibi `userConfig` substitüsyonuna taşıyın. Yayınlamadan önce
> her endpoint'i **MCP server tester** ile (`tools/list` + auth) doğrulayın.

---

## 5. `userConfig` Bloğu (key-gerektiren sunucular için)

§ 4'teki genişletilmiş `.mcp.json` kullanılıyorsa, `plugin.json`'a şu blok
eklenir. Değerler enable-time'da sorulur ve `sensitive: true` olanlar sistem
keychain'ine yazılır (settings.json'a değil).

```json
{
  "userConfig": {
    "smithery_api_key": {
      "type": "string",
      "title": "Smithery API key",
      "description": "Paper Search (Smithery host) için API anahtarı",
      "sensitive": true,
      "required": false
    },
    "smithery_profile": {
      "type": "string",
      "title": "Smithery profile",
      "description": "Smithery profil tanımlayıcısı (opsiyonel)",
      "required": false
    }
  }
}
```

---

## 6. Kimlik Doğrulama Modeli — Özet

1. **Kendi altyapın (ottoman-archives, yoktez)** — Cureonics filo deseni
   (Cloud Run / FastMCP). Auth, dağıtımının yapılandırmasına bağlıdır; public
   ise doğrudan, korumalı ise `/mcp` OAuth.
2. **OAuth 2.0 sunucuları (consensus vb.)** — token `.mcp.json`'a **gömülmez**;
   her kullanıcı `/mcp` tarayıcı akışıyla bir kez doğrular. Bu, public bir
   marketplace deposu için güvenli yoldur.
3. **Statik key sunucuları (paper-search/Smithery)** — key `userConfig` ile
   sorulur, keychain'de saklanır, `${user_config.*}` ile URL'ye enjekte edilir.
   Asla repo'ya commit edilmez.

> **Güvenlik notu.** Bu plugin **private GitHub deposunda** (`mahirkurt/CureoPrivate`;
> fonksiyonel katalog kimliği `cureonics-marketplace`) barındırılır; `.mcp.json` içindeki URL'ler yalnız repo
> erişimi olanlara görünür. `ottoman-archives` Cloud Run endpoint'i ayrıca OAuth ile
> korunur — URL'in görünmesi tek başına erişim vermez. Statik token'lar yine de asla
> repo'ya commit edilmez (`userConfig` ile keychain'de tutulur).

---

## 7. Mod → Connector Eşlemesi (skill § 5)

| Mod | Birincil connector seti | Fallback |
|---|---|---|
| `SOURCE_HUNT` | ottoman-archives (list_sources, search_iiif, search_dergipark, search_dspace) + yoktez | tavily/exa akademik filtre → web_search |
| `ARCHIVE_DEEP_DIVE` | ottoman-archives (get_source, search_literature, get_islam_ansiklopedisi) + yoktez | web_fetch (İSAM e-baskı) |
| `MANUSCRIPT_TRANSCRIBE` | ottoman-archives eScriptorium pipeline (E katmanı) | — (HTR yerel; fallback yok) |
| `PROSOPOGRAPHY` | ottoman-archives (get_islam_ansiklopedisi) + yoktez + web_fetch (Sicill-i Osmânî) | consensus/paper-search |
| `EVENT_RECONSTRUCTION` | ottoman-archives (IIIF gazete) + paper-search + tavily | web_search |
| `HISTORIOGRAPHY` | paper-search (semantic/scholar/crossref) + consensus + scholar-gateway + ottoman-archives (search_dergipark) | exa |
| `CHRONOLOGY_CONVERSION` | ottoman-archives (convert_date, parse_ottoman_date, calc_ebced, tarih_dusur) | — |
| `ACADEMIC_REPORT` | tüm katmanların birleşimi | katman degrade |
| `KANUN_GEREKÇESİ` | ottoman-archives (Düstûr/İA) + yoktez + paper-search; sağlık alanında medical-history.md | web_search/web_fetch (Resmî Gazete, TBMM zabıt) |

---

## 8. Pre-flight Zorunluları

`start` skill'i her oturum açılışında şunları kontrol eder:

1. `ottoman-archives` **canlı mı?** — değilse plugin'in çekirdek işlevi
   (arşiv keşfi, IIIF, tarih çevirici, HTR) devre dışı; kullanıcıya `/mcp`
   ile bağlanması bildirilir.
2. `yoktez` **canlı mı?** — değilse Türkçe tez triangülasyonu atlanır
   (degrade çalışma; web_search fallback).
3. Tamamlayıcı katman durumu raporlanır; eksiklerin etkisi belirtilir (örn.
   `consensus` yoksa hakemli sentez zayıflar → `web_search` fallback).

> **Restricted-kaynak kuralı (değişmez).** `ottoman-archives` bağlı olsa bile,
> erişim-kısıtlı arşivlerde (BOA, TKGM, ATASE, topkapi-arsiv, IRCICA, İSAM,
> Millet Yazma, Süleymaniye, Müteferriqa) plugin **belge içeriği üretmez**;
> yalnız katalog-bilgisi, kayıt-numarası, fond-yapısı ve erişim prosedürü
> sağlar. Bu, skill § 1.2'deki disiplinin connector-düzeyi yansımasıdır.
