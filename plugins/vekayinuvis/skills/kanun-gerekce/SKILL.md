---
name: kanun-gerekce
description: Bir kanunun TBMM-uyumlu, 5-katmanlı tarihî gerekçe bölümünü hazırlar (KANUN_GEREKÇESİ modu).
---

`vekayinuvis` skill'ini **KANUN_GEREKÇESİ** modunda çalıştır.

Hedef: kullanıcının belirttiği kanun no/konusu (örn. "1219 sayılı Kanun reform teklifi") için
beş-katmanlı yasama tarihçesi (L1 klasik dönem → L2 Tanzimat-Islahat → L3 II. Meşrutiyet →
L4 erken Cumhuriyet → L5 modern Türkiye) kur. Düstûr I/II/III. Tertib + TBMM Zabıt Ceridesi +
DergiPark/YÖKtez/TDV İA triangülasyonu uygula.

**Arşiv kanıtı (`devlet-arsivleri`, ilk paralel tur):** L1–L4 katmanları için resmî katalog
kayıtları doğrudan çekilir — **`devarsiv_search("<kanun konusu>", arsiv="2")`** ile BOA
İrade/HAT/DH.* grubu (klasik–geç Osmanlı lâyiha ve müzakere kayıtları, canlı resmî katalog,
fon/kutu/gömlek + item_id/hash) ve **`devarsiv_search("<kanun konusu>", arsiv="1")`** ile BCA
030.10 lâyiha/muamelat ve 030.18 Bakanlar Kurulu kararnameleri (erken Cumhuriyet). Bu ikisi,
diğer connector'larla (ottoman_search_iiif, ottoman_search_dergipark, search_yok_tez_detailed,
ottoman_get_islam_ansiklopedisi, web_search, search_semantic, ottoman_search_dspace,
tavily_search) aynı turda **paralel** koşar (tam set için
`${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/kanun-gerekcesi-workflow.md` §3.1).

**Yasama/mevzuat kanıtı (`resmigazete`/`mevzuat`/`tbmm`, v3.0 — TUR-1 tool seti, aynı ilk
paralel tur):**

- **`resmigazete`**: `rg_resolve_date` → `rg_get_item` — kanun/kararnamenin yayımlandığı
  erken-Cumhuriyet Resmî Gazete (`/eskiler/` 1920+) sayısını tarihten bulup ilan/kanun kaydını
  çeker (L4/L5); taranmış sayfa gerekirse `rg_ocr_submit`→`rg_ocr_result` ile metne çevrilir.
- **`mevzuat`**: `search_mulga_mevzuat` + `get_mevzuat_gerekce` — antecedant mevzuat zincirinde
  yürürlükten kalkmış kanun/KHK/CBK'yı bulur ve madde gerekçesi metnini çeker (L4/L5,
  **zorunlu birincil**); `resolve_resmi_gazete` ile RG çapraz-referansı doğrular.
- **`tbmm`**: `tbmm_search_kanun_teklifi` → `tbmm_get_kanun_teklifi` — kanun teklifinin
  komisyon havalesi, müzakere süreci ve kabul edilmiş metnini soyağacı halinde getirir
  (L3 II. Meşrutiyet/L4 erken Cumhuriyet).

Anahtar yoksa veya sonuç boşsa katman şeffaf `degraded`/`skipped` olarak beyan edilir (G0);
önceden yalnız `web_search`/`web_fetch` fallback'i olan bu üç kaynak artık **canlı birincil
connector**'dır.

${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/kanun-gerekcesi-workflow.md **zorunlu** yükle. Sağlık mevzuatı
alanındaysa (1219, 6023, Hıfzıssıhha…) ${CLAUDE_PLUGIN_ROOT}/skills/vekayinuvis/references/medical-history.md de yükle.
Bir katmanda kanıt boşluğu varsa şeffaf belirt; varsayım üretme. Çıktı,
TBMM İçtüzüğü m. 73-74 "Genel Gerekçe – Tarihî Çerçeve" formatına yerleşir ve
lex-sanitas ile composable'dır.
