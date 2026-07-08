# CONNECTORS.md — Vekayinüvis Plugin Connector Envanteri

> **Tek doğruluk kaynağı.** Bu dosya, `vekayinuvis` plugin süitinin tüm MCP
> connector bağımlılıklarını, kimlik doğrulama modelini, fallback zincirlerini
> ve mod → connector eşlemesini tanımlar. Skill'ler ve `start` oryantasyonu bu
> dosyaya referans verir. Transport (uzak MCP URL) tanımı için kanonik dosya
> `../.mcp.json`'dur.

---

## 1. Connector Katmanları

Vekayinüvis **tam-filo** çalışır: aşağıdaki katmanların **tamamı** artık
`.mcp.json`'da bundled'dır (13 server) ve kurulduğunda otomatik başlar — amaç,
bağlama uygun **her aracın her koşumda tam çalışması** (kullanıcı gereksinimi).
Katman etiketleri artık aktivasyon kapısı değil, sentezde **rol/otorite** ayrımıdır:

- **Çekirdek (core)** — `ottoman-archives` · `devlet-arsivleri` · `yoktez`:
  alana-özgü, plugin'in varlık sebebi olan arşiv/tez omurgası.
- **Akademik (academic)** — `literatur` · `consensus` · `scholar-gateway` ·
  `exa` · `tavily` · `paper-search`: tarihyazımı/kanıt triangülasyonu.
- **Tam-metin (fulltext)** — `openathens` (lisanslı, Tier 3) · `annas-reader`
  (son-çare, Tier 4): kitap+makale tam-metin şelalesi (paywall'lı monograf/makale).
- **Destekleyici (support)** — `yok-akademik`: modern akademisyen/ekol haritası.
- **Substrat** — `anamnesis`: büyük-veri RAG/GraphRAG bağlam-ekonomisi altyapısı
  (bir kaynak değil; `shared/context-economy-contract.md` Tier 2).

Bir server'ın anahtarı yoksa / oturumu düşükse **graceful degrade** eder ve
**G0 kapsam manifestosunda** dürüstçe beyan edilir (`skipped`/`degraded`) —
asla uydurma, asla sessiz atlama. § 4 tarihsel "opsiyonel snippet" artık
varsayılanın kendisidir (tam roster bundled).

---

## 2. Çekirdek Katman (`.mcp.json`'da bundled)

| Sunucu adı | Transport | URL | Rol | Kimlik doğrulama |
|---|---|---|---|---|
| `ottoman-archives` | http | `https://ottoman.cureonics.com/mcp` | 33-kaynaklı Osmanlı arşiv keşfi + IIIF tam-metin + Hicri/Rumî/Miladi çevirici + ebced + eScriptorium HTR + TDV İslâm Ansiklopedisi | HP self-host — `/mcp` Bearer (`${OTTOMAN_ARCHIVES_MCP_API_KEY}`) |
| `devlet-arsivleri` | http | `https://devarsiv.cureonics.com/mcp` | **Resmî Devlet Arşivleri kataloğu** (Osmanlı/BOA · Cumhuriyet/BCA · Dışişleri Diplomatik · Askeri Tarih) — doğrudan **fon/kutu/gömlek katalog araması** + belge künyesi; `katalog.devletarsivleri.gov.tr`'yi sarar | HP self-host, `/mcp` Bearer (`${DEVARSIV_MCP_API_KEY}`) — **tek-cihaz oturum kilitli** (HP'de kalıcı authenticated tarayıcı) |
| `yoktez` | http | `https://yoktezmcp.fastmcp.app/mcp` | YÖK Ulusal Tez Merkezi — tahrir/mühimme/şer'iye sicili transkripsiyon tezleri, anabilim dalı bazlı arama | FastMCP host — gerekirse `/mcp` OAuth akışı |

**Ottoman Archives yetenek katmanları** (skill § 3.1): A. Kaynak Keşfi ·
B. Tam-Metin Arama · C. Belge/Metin Çekme · D. Hesaplama/Yardımcı (tarih, ebced,
defter şeması) · E. HTR Pipeline (opt-in eScriptorium).

**Devlet Arşivleri yetenek katmanı** (skill § 3.1 · **F. Resmî Katalog** — 8 araç):
`devarsiv_search` (fon/kutu/gömlek + özet + tarih + item_id/hash + `capped`),
**`devarsiv_semantic_search`** (diakronik/semantik — Osmanlıca eşdeğer genişletme +
bge-m3 rerank), **`devarsiv_detailed_search`** (hassas/enumerasyon — arşiv × üst-fon ×
tarih × özet), **`devarsiv_list_fon_categories`** (üst-fon ekseni — 1000-tavan aşımı),
`devarsiv_get_belge` (künye + erişim durumu; hash zinciri aramadan gelir),
**`devarsiv_get_belge_image`** (sayfa taraması ImageContent — satın-almadan bağımsız; asistan
el yazması Osmanlıca'yı görüsüyle okur), **`devarsiv_ocr_belge`** (deterministik OCR/HTR —
Latin tam · Osmanlı damga+referans kodu · el yazması→Transkribus/görü),
`devarsiv_detailed_search_fields`, `devarsiv_session_status`, `devarsiv_server_info`.
**Kapsamlı erişim:** katalog en çok 1000 satır render eder (sayfalama yok) → tam 1000
(`capped:true`) = *daha fazlası var*; her belgeye ulaşmak için `list_fon_categories` +
`detailed_search` üst-fon × tarih-penceresi enumerasyonu + `item_id` union (skill
`devlet-arsivleri-katalog.md` §2b). **No-fabrication:** geniş sorgu → `refine_required`;
canlı oturum yoksa → `session_required` (asla uydurma). ottoman-archives'ın **yapmadığı**
resmî BOA/BCA katalog aramasını doldurur; belge görüntüleri hâlâ eSatış/on-site kapısında (§ 8).

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
| `literatur` | http | `https://literatur-mcp.surucu.dev/mcp` | **DergiPark tam-metin** — Türk akademik dergi makalesi arama (yıl/tür/dizin/sıralama filtreli) + **PDF→HTML tam metin** + referans çekme. ottoman-archives `search_dergipark`'ı (curated OAI-PMH metadata) tam-metin ve tüm-dergi kapsamıyla tamamlar | Hazır remote (surucu.dev), **authless** — CapSolver/Mistral yazar tarafında; kurulumsuz |
| `yok-akademik` | http | `https://yok-akademik.cureonics.com/mcp` | **YÖK Akademik profilleri** (15 salt-okunur araç) — akademisyen arama, yayın/proje/tez danışmanlığı, eş-yazar ego-ağı. **Destekleyici unsur**: modern prosopografi + ekol/uzman haritası; birincil arşiv işlevine gerekli değil | HP self-host, `/mcp` Bearer (`${YOK_AKADEMIK_MCP_API_KEY}`) |
| `openathens` *(tam-metin)* | http | `https://openathens.cureonics.com/mcp` | **Lisanslı kurumsal tam-metin** (kitap+makale) — Millet Kütüphanesi / OpenAthens SAML üzerinden 309 lisanslı DB'den tam metin; paywall'lı monograf/makale/ansiklopedi maddesine yasal erişim. Tam-metin şelalesi **Tier 3** (literatur/paper-search sonrası, annas öncesi). 6 araç (`oa_*`) | HP self-host, `/mcp` Bearer (`${OPENATHENS_MCP_API_KEY}`); SAML creds sunucu-taraflı |
| `annas-reader` *(tam-metin)* | http | `https://annas.cureonics.com/mcp` | **Son-çare kitap+makale tam-metin** (Anna's Archive efemer-RAG) — lisanslı band getiremeyince. Out-of-print Osmanlı çalışmaları, nadir monograf, paywall-dışı makale. `book_search`/`article_search`/`read_document`/`search_in_document` (BM25). Telif: yalnız analiz | HP self-host (Docker), `/mcp` Bearer (`${ANNAS_MCP_API_KEY}`) |
| `anamnesis` *(substrat)* | http | `https://anamnesis-mcp.cureonics.workers.dev/mcp` | **Büyük-veri RAG/GraphRAG substratı** (bir kaynak DEĞİL, bağlam-ekonomisi altyapısı) — büyük tam-metin (belge transkripsiyonu, tez PDF, DergiPark tam-metin, İА maddesi) ingest → bounded query; kişi↔görev↔belge / olay↔tarih↔kaynak grafiği. Detayların atlanmadan, pencere taşmadan kapsanmasını sağlar | CF Worker, `/mcp` Bearer (`${ANAMNESIS_MCP_API_KEY}`) |

> **TAM-FİLO + bağlam ekonomisi (bkz. `shared/context-economy-contract.md`).** Bağlama uygun
> tüm server'lar **her sorguda** çalışır ve **G0 kapsam manifestosu**yla (`shared/coverage-manifest.md`)
> kanıtlanır — sessiz atlama yasak. Ağır çok-connector getirim `arsiv-tarama-distilleri` alt-ajanında
> toplanır (retrieve-don't-dump); büyük tam-metin `anamnesis`'e ingest edilir → bounded query. Ana
> pencereye yalnız damıtılmış `arsiv_distillate` + coverage döner. Böylece **hiçbir araç atlanmaz,
> hiçbir detay kaybolmaz, pencere taşmaz.** Full-fleet artık `.mcp.json`'da bundled (companion'lar
> dâhil); paper-search Smithery key'i `userConfig` ile enable-time'da sorulur (§ 5).

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
      "url": "https://ottoman.cureonics.com/mcp",
      "headers": { "Authorization": "Bearer ${OTTOMAN_ARCHIVES_MCP_API_KEY}" }
    },
    "devlet-arsivleri": {
      "type": "http",
      "url": "https://devarsiv.cureonics.com/mcp",
      "headers": { "Authorization": "Bearer ${DEVARSIV_MCP_API_KEY}" }
    },
    "yoktez": {
      "type": "http",
      "url": "https://yoktezmcp.fastmcp.app/mcp"
    },
    "literatur": {
      "type": "http",
      "url": "https://literatur-mcp.surucu.dev/mcp"
    },
    "yok-akademik": {
      "type": "http",
      "url": "https://yok-akademik.cureonics.com/mcp",
      "headers": { "Authorization": "Bearer ${YOK_AKADEMIK_MCP_API_KEY}" }
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

1. **Kendi altyapın (ottoman-archives, devlet-arsivleri, yok-akademik, yoktez)** —
   Cureonics filo deseni (HP/Pi self-host FastMCP + hardened OAuth 2.1). `/mcp`
   Bearer = ilgili `${*_MCP_API_KEY}` (Doppler `cureohub/dev_personal`; Claude
   Code/Desktop'ta statik Bearer, claude.ai/grok'ta OAuth akışı). `devlet-arsivleri`
   ayrıca **tek-cihaz oturum kilitli** — connector auth'undan bağımsız olarak, upstream
   katalog oturumu HP'deki kalıcı authenticated tarayıcıda yaşar (bkz. § 8).
   `literatur` hazır remote (surucu.dev), authless.
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
| `SOURCE_HUNT` | **devlet-arsivleri** (search / **semantic_search** modern terimde — kanıt-yoğunluğu; `capped` ise **list_fon_categories** kapsam-haritası) + ottoman-archives (list_sources, search_iiif, search_dergipark, search_dspace) + yoktez + literatur | tavily/exa akademik filtre → web_search |
| `ARCHIVE_DEEP_DIVE` | **devlet-arsivleri** (search/semantic_search + get_belge; konu >1000 → **list_fon_categories + detailed_search** üst-fon×tarih enumerasyonu, item_id union) + ottoman-archives (get_source, search_literature, get_islam_ansiklopedisi) + yoktez | web_fetch (İSAM e-baskı) |
| `MANUSCRIPT_TRANSCRIBE` | ottoman-archives eScriptorium pipeline (E katmanı) | — (HTR yerel; fallback yok) |
| `PROSOPOGRAPHY` | **devlet-arsivleri** (DH.SAİD Sicill-i Ahval katalog kaydı) + ottoman-archives (get_islam_ansiklopedisi) + yoktez + **yok-akademik** (modern akademisyen) + **openathens/annas-reader** (biyografik monograf/Sicill-i Osmânî tam-metin) + web_fetch | consensus/paper-search |
| `EVENT_RECONSTRUCTION` | ottoman-archives (IIIF gazete) + **devlet-arsivleri** (dönem belge kayıtları) + literatur + paper-search + tavily | web_search |
| `HISTORIOGRAPHY` | **literatur** (DergiPark tam-metin) + **openathens** (lisanslı kitap/makale tam-metin) + **annas-reader** (son-çare monograf/makale) + paper-search + consensus + scholar-gateway + ottoman-archives (search_dergipark) + **yok-akademik** (ekol/uzman haritası) | exa |
| `CHRONOLOGY_CONVERSION` | ottoman-archives (convert_date, parse_ottoman_date, calc_ebced, tarih_dusur) | — |
| `ACADEMIC_REPORT` | tüm katmanların birleşimi (devlet-arsivleri + ottoman-archives + yoktez + literatur + akademik companion) | katman degrade |
| `KANUN_GEREKÇESİ` | **devlet-arsivleri** (BCA lâyiha/BOA İrade katalog kayıtları — L1–L4) + ottoman-archives (Düstûr/İA) + yoktez + literatur/paper-search (L5); sağlık alanında medical-history.md | web_search/web_fetch (Resmî Gazete, TBMM zabıt) |

---

## 8. Pre-flight Zorunluları

`start` skill'i her oturum açılışında şunları kontrol eder:

1. `ottoman-archives` **canlı mı?** — değilse plugin'in çekirdek işlevi
   (arşiv keşfi, IIIF, tarih çevirici, HTR) devre dışı; kullanıcıya `/mcp`
   ile bağlanması bildirilir.
2. `devlet-arsivleri` **oturumu canlı mı?** — `devarsiv_session_status` ile
   kontrol edilir. **Tek-cihaz oturum kilidi** nedeniyle oturum HP'de yaşayan
   kalıcı tarayıcıya bağlıdır; `alive:false` ise resmî katalog araması
   `session_required` döner → kullanıcıya HP noVNC re-login yol haritası
   bildirilir (ottoman-archives/yoktez ile degrade çalışma sürer).
3. `yoktez` **canlı mı?** — değilse Türkçe tez triangülasyonu atlanır
   (degrade çalışma; web_search fallback).
4. Tamamlayıcı katman durumu raporlanır; eksiklerin etkisi belirtilir (örn.
   `consensus` yoksa hakemli sentez zayıflar → `web_search` fallback;
   `literatur` yoksa DergiPark tam-metin atlanır → ottoman `search_dergipark`
   metadata fallback; `yok-akademik` yoksa modern uzman/ekol haritası atlanır).

> **Restricted-kaynak kuralı (güncellenmiş, değişmez çekirdek).** Erişim-kısıtlı
> arşivlerde (BOA, BCA, TKGM, ATASE, topkapi-arsiv, IRCICA, İSAM, Millet Yazma,
> Süleymaniye, Müteferriqa) plugin **belge görüntüsü/tam-metin içeriği üretmez**.
> **YENİ (`devlet-arsivleri` ile):** BOA/BCA/Diplomatik/Askeri **katalog araması,
> kayıt-numarası (fon/kutu/gömlek), künye ve özet artık DOĞRUDAN canlı çekilir**
> (`devarsiv_search`/`devarsiv_get_belge`) — "BETSİS sorgu önerisi" adımı gerçek
> katalog sorgusuna terfi etti. Ancak **belge görüntüleri** hâlâ eSatış satın-alma
> / on-site akreditasyon kapısındadır; bu görüntüler uydurulmaz, `get_belge` yalnız
> erişim/satın-alma durumunu bildirir. No-fabrication invariant'ı korunur; bu, skill
> § 1.2'deki disiplinin connector-düzeyi yansımasıdır.
