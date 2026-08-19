---
name: start
description: Vekayinüvis süitine giriş ve yönlendirme. Bağlı MCP connector'larını (Ottoman Archives, Devlet Arşivleri, YÖK Tez + tamamlayıcı akademik katman) kontrol eder, flagship vekayinuvis skill'ini, dokuz çalışma modunu ve sepet→satın-alma→arşiv-okuma→async-OCR akış üçlüsünü tanıtır, kullanıcının niyetine göre doğru moda/akışa veya slash komutuna yönlendirir. İlk kez süitle çalışırken, hangi connector'ların bağlı olduğunu görmek için, ya da "vekayinuvis nedir / nereden başlamalıyım / hangi modu kullanmalıyım" türü oryantasyon sorularında kullanın. Tetikleyiciler — vekayinuvis başlat, süit oryantasyonu, connector kontrolü, Osmanlı arşivi bağlı mı, "ne yapabilirsin", "nereden başlayayım", "hangi mod".
version: 3.4.12
last_updated: 2026-08-14
---

# Vekayinüvis — Başlangıç ve Yönlendirme

Vekayinüvis, **birincil-kaynak-öncelikli Osmanlı/Türk tarih araştırma**
orkestrasyon süitidir. Kullanıcıyı süitle tanıştırıp doğru moda yönlendirin.
Aşağıdaki adımları sırayla izleyin.

> Connector envanteri, kimlik doğrulama modeli ve fallback zincirleri için tek
> doğruluk kaynağı: [../../CONNECTORS.md](../../CONNECTORS.md). Transport (uzak
> MCP) tanımı: [../../.mcp.json](../../.mcp.json).

## Adım 1 — Karşılama

Şu mesajı gösterin:

```
Vekayinüvis — Osmanlı/Türk Tarih Araştırma Protokolü

Dağınık arşiv, yazma, akademik tez, hakemli literatür ve yasama zekâsını tek bir
atıflı, çeviriyazısı tutarlı, kaynağı şeffaf tarih çıktısına dönüştürür. TAM-FİLO
(17 server): Ottoman Archives (33 kaynak) + resmî Devlet Arşivleri kataloğu (BOA/
BCA/Diplomatik/Askeri) + YÖK Tez çekirdeğini şu katmanlarla birleştirir —
akademik triangülasyon (DergiPark tam-metin Literatür, YÖK Akademik, Paper Search,
Consensus, Scholar Gateway, Exa, Tavily); **yasama/mevzuat** (Resmî Gazete erken-
Cumhuriyet arşivi, mevzuat.gov.tr mülga/gerekçe, TBMM yasama soyağacı, DETSİS
kurumsal prosopografi); **tam-metin şelalesi** (OpenAthens lisanslı Millet
Kütüphanesi → Anna's Reader son-çare) → getirilen tam-metin **anamnesis** RAG/
GraphRAG substratına ingest edilir. IJMES/TDV İA çeviriyazı ve Chicago atıf
disipliniyle, her çıktıda G0 kapsam manifestosuyla çalışır.

Kapsam: Osmanlı dönemi (~1299–1922) + erken Cumhuriyet (1923–1950) öncelikli.
Önemli sınır: BOA/BCA/Diplomatik/Askeri arşivlerin resmî KATALOG araması artık
doğrudan yapılır (devlet-arsivleri: fon/kutu/gömlek + künye). Belge sayfa
taraması/OCR/HTR yalnız gerçek `devarsiv_get_belge_image` / `devarsiv_ocr_belge`
çıktısı ve provenance ile aktarılır; çekilmediyse katalog düzeyinde kalınır.
Osmanlı el yazması gövdesinde varsayılan okuyucu **Transleyt** (ölçülen en iyi,
CER 0.130–0.230); en doğru okuma **Transleyt + asistan görüsü iki-okuyucu
uzlaştırması**dır (ikisi denk ve bağımsız). Çok-sayfalı TAM erişim artık eSatış'a
çıkmadan araç-içi çözülür: sepet→satın-alma (`/vekayinuvis:satinalma` — karar
matrisi, metin-onay kapısı, ödeme DAİMA insan/noVNC) → yerel BOA-kodlu arşivden
300 DPI görüyle okuma (`/vekayinuvis:arsiv-oku`) → gerekirse çok-sayfalı belgede
async OCR + anamnesis ingest (`/vekayinuvis:toplu-okuma`) zinciriyle. Diğer
kısıtlı kaynaklar (TKGM, ATASE, İSAM, Süleymaniye…) için içerik uydurulmaz;
yalnız erişim yol haritası sağlanır.
```

## Adım 2 — Bağlı MCP Connector'larını Kontrol Et

Bağlı araçları listeleyip aşağıdaki gruplara göre raporlayın. Her grupta hangi
connector'ın **canlı**, hangisinin **bağlı değil** olduğunu açıkça belirtin.

**Çekirdek katman (süitin omurgası — `.mcp.json`'da bundled):**
- `ottoman-archives` — 33-kaynaklı arşiv keşfi + IIIF tam-metin + Hicri/Rumî/
  Miladi çevirici + ebced + eScriptorium matbu-korpus HTR + TDV İslâm Ansiklopedisi ·
  *pre-flight zorunlu* (yoksa çekirdek işlev devre dışı)
- `devlet-arsivleri` — **resmî Devlet Arşivleri kataloğu** (Osmanlı/BOA · Cumhuriyet/
  BCA · Diplomatik · Askeri) doğrudan fon/kutu/gömlek araması + belge künyesi +
  eSatış sepet/satın-alma + yerel BOA-kodlu arşiv/async OCR + kapsamlı süpürme/store
  (**7 araç grubu** — arama · süpürme · belge · sepet · arşiv · OCR · durum;
  `/vekayinuvis:satinalma` ·
  `/vekayinuvis:arsiv-oku` · `/vekayinuvis:toplu-okuma`) · *tek-cihaz oturum kilitli* →
  `devarsiv_session_status` ile canlılığı kontrol edin; **preflight'ta**
  `devarsiv_server_info` çağrısının `tools` dizisinde **7 grubun her birinden en az bir
  araç** bulunduğunu doğrulayın (kesin sayı deploy'a göre değişir — `devarsiv_ocr_image`
  gibi eklemeler büyütür; magic-number beklemeyin). Bir grup **tümüyle yoksa** (ör. hiç
  `*_ocr_*` yok) connector'ı claude.ai'da yeniden bağlama uyarısı verin — araç listesi
  cache'lenmiş olabilir
- `yoktez` — YÖK Ulusal Tez Merkezi (tahrir/mühimme/şer'iye sicili tezleri)

**Tamamlayıcı katman (akademik triangülasyon — full-fleet bundled):**
- `literatur` (DergiPark **tam-metin** makale + PDF→HTML + referans) ·
  `yok-akademik` (**destekleyici** — YÖK Akademik profilleri, uzman/ekol haritası) ·
  `paper-search` (Google Scholar/Semantic Scholar/CrossRef/PubMed/arXiv) ·
  `consensus` (hakemli sentez) · `scholar-gateway` (pasaj-düzeyi atıf) ·
  `exa` (akademik web) · `tavily` (geniş web tarama)

**Tam-metin şelalesi (kitap+makale):**
- `openathens` (Tier 3 **lisanslı** — metin/RAG `oa_fetch_fulltext`, orijinal provider PDF
  `oa_fetch_pdf(doi|url)`) → `annas-reader` (Tier 4 **son çare** — bounded reader,
  orijinal PDF/EPUB/etc. `download_document(id=DOI|MD5)`; yalnız analiz). Dosya araçları
  kısa-ömürlü resource link + SHA-256/provenance döndürür; link derhal tüketilir,
  uzun tam-metin anamnesis'e ingest edilir.

**Substrat (bağlam ekonomisi altyapısı):**
- `anamnesis` — büyük-veri RAG/GraphRAG; büyük tam-metin (belge transkripsiyonu,
  tez PDF, DergiPark tam-metin) ingest→bounded query. Detayların atlanmadan,
  pencere taşmadan kapsanması için (bkz. `${CLAUDE_PLUGIN_ROOT}/shared/context-economy-contract.md`).

> **TAM-FİLO.** Bu 17 server `.mcp.json`'da bundled'dır ve bağlama uygun olanı
> **her substantif sorguda çalışır**; her çıktı **G0 kapsam manifestosu** taşır
> (`${CLAUDE_PLUGIN_ROOT}/shared/coverage-manifest.md`) — sessiz atlama yok. Ağır getirim
> `arsiv-tarama-distilleri` alt-ajanına delege edilir (retrieve-don't-dump).

**Web katmanı (host-bağımlı):**
- Filonun **bundled** web araçları `exa` (akademik web) + `tavily` (geniş tarama) —
  her iki host'ta (Claude Code + claude.ai) `.mcp.json` üzerinden mevcut, birincil web yüzeyi.
- Host-sağlamalı `web_search`/`web_fetch` + `google_drive_search`/`google_drive_fetch`
  **yalnız host sağlıyorsa** çalışır (Claude Code'da genelde var; claude.ai custom
  connector oturumunda bulunmayabilir) → bunlara güvenme, `exa`/`tavily`'yi tercih et.

Bağlı olmayan connector'lar için kullanıcıya, `/mcp` ile (veya claude.ai'de
Settings → Connectors) etkinleştirebileceğini bildirin. Kritik eksiklerin
etkisini söyleyin:
- `ottoman-archives` yoksa → arşiv keşfi, IIIF tam-metin, tarih çevirici ve
  HTR **devre dışı**; süit yalnız akademik-literatür modunda degrade çalışır.
- `devlet-arsivleri` oturumu düşükse (`session_required`) → resmî BOA/BCA katalog
  araması atlanır; kullanıcıya HP noVNC re-login yol haritası bildirilir,
  ottoman-archives/yoktez ile degrade devam edilir (asla uydurma).
- `yoktez` yoksa → Türkçe tez triangülasyonu atlanır (`exa`/`tavily` fallback).
- `literatur` yoksa → DergiPark **tam-metin** atlanır; ottoman `search_dergipark`
  (metadata) fallback. `yok-akademik` yoksa → modern uzman/ekol haritası atlanır
  (destekleyici; birincil işleve gerekli değil).
- `openathens` yoksa → lisanslı kitap/makale tam-metni atlanır (paywall aşılamaz);
  `annas-reader` son-çare fallback. `annas-reader` de yoksa → tam-metin yerine
  yalnız metadata/atıf + kullanıcıya kütüphane erişim yol haritası (uydurma yok).
- diğer tamamlayıcılar yoksa → hakemli kanıt sentezi zayıflar; `exa`/`tavily`
  fallback devreye girer.

## Adım 3 — Flagship Skill'i ve Modları Tanıt

Tek flagship skill: **`vekayinuvis`** (9 çalışma modu). Mod, sorgudan otomatik
seçilir; belirsizlikte kullanıcıya tek soru sorulur.

| Mod | Ne yapar | Tipik soru |
|-----|----------|-----------|
| **SOURCE_HUNT** | Kaynak avı — hangi arşivler/kaynaklar var | "X hakkında hangi arşivler var?" |
| **ARCHIVE_DEEP_DIVE** | Arşiv derin dalış + fond yol haritası | "BOA'da II. Mahmud dönemi tıbbiye HAT kayıtları?" |
| **MANUSCRIPT_TRANSCRIBE** | Yazma transkripsiyon (Transleyt + asistan görüsü uzlaştırması) | "Bu yazma sayfanın transkripsiyonu mümkün mü?" |
| **PROSOPOGRAPHY** | Biyografi + hizmet kaydı | "Mustafa Behçet Efendi'nin biyografisi" |
| **EVENT_RECONSTRUCTION** | Olay kurgulaması (gün-gün) | "31 Mart Vakası'nın kronolojisi" |
| **HISTORIOGRAPHY** | Tarih yazımı / literatür eleştirisi | "Tanzimat iktisadı üzerine literatürün durumu" |
| **CHRONOLOGY_CONVERSION** | Hicri/Rumî/Miladi + ebced/kronogram | "15 Receb 1287 Miladî karşılığı?" |
| **ACADEMIC_REPORT** | 10-bölümlü atıflı akademik rapor | "X üzerine akademik tarih raporu hazırla" |
| **KANUN_GEREKÇESİ** | Kanunun 5-katmanlı tarihî gerekçesi | "1219 sayılı Kanun'un tarihî gerekçesi" |

## Adım 4 — Slash Komutlarını Tanıt

> **İsimlendirme.** Komutlar önek almadan doğrudan skill adıyla çağrılır:
> `/vekayinuvis:<ad>` (dash-önekli eski `/vekayinuvis-<ad>` biçimi terk edildi —
> `commands/` dizini `skills/`'e göçtü). 14 satır: 11 mod-skill (9 çalışma modu +
> durum preflight + boa-katalog ARCHIVE_DEEP_DIVE varyantı) + 3 sepet/arşiv/OCR akış-skill'i.

| Komut | Mod/Akış | Ne yapar |
|-------|-----|----------|
| `/vekayinuvis:durum` | PREFLIGHT | Tam-filo MCP wiring/env/userConfig preflight + G0 manifest + `devlet-arsivleri` canlı session probe + araç-grubu kapsam kontrolü |
| `/vekayinuvis:kaynak-avi` | SOURCE_HUNT | Kaynak matrisi (tür × erişim × dil × kanıt-yoğunluğu) |
| `/vekayinuvis:arsiv-dalis` | ARCHIVE_DEEP_DIVE | Fond/tasnif yol haritası + erişim talimatı |
| `/vekayinuvis:boa-katalog` | ARCHIVE_DEEP_DIVE | Resmî katalogda (BOA/BCA/Diplomatik/Askeri) doğrudan fon/kutu/gömlek araması + künye (`devlet-arsivleri` odaklı) |
| `/vekayinuvis:transkripsiyon` | MANUSCRIPT_TRANSCRIBE | Transleyt + asistan görüsü iki-okuyucu uzlaştırması (harici IIIF → devarsiv_ocr_image) |
| `/vekayinuvis:prosopografi` | PROSOPOGRAPHY | Yaşam çizelgesi + atama-azil zinciri + eser listesi |
| `/vekayinuvis:olay` | EVENT_RECONSTRUCTION | Bir tarihî olayın gün-gün birincil-kaynak kronolojisi + olay örgüsü |
| `/vekayinuvis:kronoloji` | CHRONOLOGY_CONVERSION | Üç-takvim tablosu + ebced/kronogram |
| `/vekayinuvis:literatur` | HISTORIOGRAPHY | DergiPark tam-metin literatür taraması + tarihyazımı sentezi |
| `/vekayinuvis:rapor` | ACADEMIC_REPORT | Tam-uzunlukta atıflı akademik rapor |
| `/vekayinuvis:kanun-gerekce` | KANUN_GEREKÇESİ | TBMM-uyumlu 5-katmanlı tarihî gerekçe |
| `/vekayinuvis:satinalma` | SEPET/SATIN-ALMA | eSatış sepet + noVNC satın-alma — karar matrisi, metin-onay kapısı, ödeme daima insan |
| `/vekayinuvis:arsiv-oku` | ARŞİV OKUMA | Satın-alınmış belgeyi yerel BOA-kodlu arşivden 300 DPI görüyle okuma |
| `/vekayinuvis:toplu-okuma` | ASYNC OCR | Çok-sayfalı satın-alınmış belgede async OCR + anamnesis ingest |

## Adım 5 — Niyete Göre Yönlendir

Kullanıcının ne üzerinde çalıştığını sorun. Yaygın iş akışları:

1. **"X konusunda hangi kaynaklar var?"** → `/vekayinuvis:kaynak-avi`.
2. **"Belirli bir arşivde/fonda ne var?"** → `/vekayinuvis:arsiv-dalis`
   (veya doğrudan resmî katalog odağı için `/vekayinuvis:boa-katalog`).
3. **"Bir kişinin biyografisi/hizmet kaydı?"** → `/vekayinuvis:prosopografi`.
4. **"Bir olayın gün-gün kronolojisi / olay örgüsü?"** → `/vekayinuvis:olay`
   (birincil-kaynak temelli olay kurgulaması; çift-tarih + fon/kutu/gömlek künyeli).
5. **"Bir tarihin takvim karşılığı / kronogram çözümü?"** → `/vekayinuvis:kronoloji`.
6. **"Tam bir akademik tarih raporu?"** → `/vekayinuvis:rapor`.
7. **"Bir kanunun tarihî gerekçe bölümü?"** → `/vekayinuvis:kanun-gerekce`
   (sağlık alanında `medical-history.md` otomatik yüklenir; `cureolex` ile
   composable).
8. **"Bu belgenin tüm sayfalarını satın almak istiyorum."** → `/vekayinuvis:satinalma`
   (karar matrisi + metin-onay kapısı; ödeme daima insan/noVNC).
9. **"Satın aldığım belgeyi okumak istiyorum."** → `/vekayinuvis:arsiv-oku`
   (yerel BOA-kodlu arşivden 300 DPI görüyle, sayfa-sayfa).
10. **"Çok-sayfalı satın-alınmış belgenin tam metnini/OCR'ını istiyorum."** →
   `/vekayinuvis:toplu-okuma` (async OCR + anamnesis ingest, K4 kararı
   >5 sayfa veya çok-motorlu (`both`) tam belgede devreye girer).

**Ayrım rehberi (scope guard):**
- Mevzuat reformu/taslak yazımı → `cureolex` (vekayinuvis yalnız tarihî
  gerekçe bölümünü besler).
- Modern tıp literatürü / pipeline → `medical-research` / `pharmaintel`.
- Basılı/sunum çıktısı → `carbon-html-report` (A4 baskı/sunum-hazır) veya bilimsel
  format için `carbon-quarto-scientific` (downstream).

Kullanıcının yanıtını bekleyin ve uygun moda/komuta yönlendirin. Her çıktıda,
erişim-kısıtlı kaynaklarda gerçek arşiv çalışmasının **insan-araştırmacının
fiilî katılımını** gerektirdiğini; bu süitin o çalışmanın ön araştırması,
kaynak haritalandırması ve raporlama altyapısını sağladığını hatırlatın.
