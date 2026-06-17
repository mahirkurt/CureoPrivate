---
name: start
description: Vekayinüvis süitine giriş ve yönlendirme. Bağlı MCP connector'larını (Ottoman Archives, YÖK Tez + tamamlayıcı akademik katman) kontrol eder, flagship vekayinuvis skill'ini ve dokuz çalışma modunu tanıtır, kullanıcının niyetine göre doğru moda veya slash komutuna yönlendirir. İlk kez süitle çalışırken, hangi connector'ların bağlı olduğunu görmek için, ya da "vekayinuvis nedir / nereden başlamalıyım / hangi modu kullanmalıyım" türü oryantasyon sorularında kullanın. Tetikleyiciler — vekayinuvis başlat, süit oryantasyonu, connector kontrolü, Osmanlı arşivi bağlı mı, "ne yapabilirsin", "nereden başlayayım", "hangi mod".
version: 1.0.0
last_updated: 2026-06-17
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

Dağınık arşiv, yazma, akademik tez ve hakemli literatür zekâsını tek bir
atıflı, çeviriyazısı tutarlı, kaynağı şeffaf tarih çıktısına dönüştürür.
Ottoman Archives (33 kaynak) + YÖK Tez çekirdek katmanını akademik
triangülasyon katmanıyla (Paper Search, Consensus, Scholar Gateway, Exa,
Tavily) birleştirir; IJMES/TDV İA çeviriyazı ve Chicago atıf disipliniyle
çalışır.

Kapsam: Osmanlı dönemi (~1299–1922) + erken Cumhuriyet (1923–1950) öncelikli.
Önemli sınır: erişim-kısıtlı arşivlerde (BOA, TKGM, ATASE, İSAM, Süleymaniye…)
belge içeriği ÜRETİLMEZ — yalnız katalog, kayıt-no, fond-yapısı ve erişim
yol haritası sağlanır.
```

## Adım 2 — Bağlı MCP Connector'larını Kontrol Et

Bağlı araçları listeleyip aşağıdaki gruplara göre raporlayın. Her grupta hangi
connector'ın **canlı**, hangisinin **bağlı değil** olduğunu açıkça belirtin.

**Çekirdek katman (süitin omurgası — `.mcp.json`'da bundled):**
- `ottoman-archives` — 33-kaynaklı arşiv keşfi + IIIF tam-metin + Hicri/Rumî/
  Miladi çevirici + ebced + eScriptorium HTR + TDV İslâm Ansiklopedisi ·
  *pre-flight zorunlu* (yoksa çekirdek işlev devre dışı)
- `yoktez` — YÖK Ulusal Tez Merkezi (tahrir/mühimme/şer'iye sicili tezleri)

**Tamamlayıcı katman (akademik triangülasyon — opsiyonel):**
- `paper-search` (Google Scholar/Semantic Scholar/CrossRef/PubMed/arXiv) ·
  `consensus` (hakemli sentez) · `scholar-gateway` (pasaj-düzeyi atıf) ·
  `exa` (akademik web) · `tavily` (geniş web tarama)

**Anthropic yerleşik (her zaman mevcut):**
- `web_search` · `web_fetch` · `google_drive_search` / `google_drive_fetch`

Bağlı olmayan connector'lar için kullanıcıya, `/mcp` ile (veya claude.ai'de
Settings → Connectors) etkinleştirebileceğini bildirin. Kritik eksiklerin
etkisini söyleyin:
- `ottoman-archives` yoksa → arşiv keşfi, IIIF tam-metin, tarih çevirici ve
  HTR **devre dışı**; süit yalnız akademik-literatür modunda degrade çalışır.
- `yoktez` yoksa → Türkçe tez triangülasyonu atlanır (web_search fallback).
- tamamlayıcı katman yoksa → hakemli kanıt sentezi zayıflar; `web_search`
  fallback devreye girer.

## Adım 3 — Flagship Skill'i ve Modları Tanıt

Tek flagship skill: **`vekayinuvis`** (9 çalışma modu). Mod, sorgudan otomatik
seçilir; belirsizlikte kullanıcıya tek soru sorulur.

| Mod | Ne yapar | Tipik soru |
|-----|----------|-----------|
| **SOURCE_HUNT** | Kaynak avı — hangi arşivler/kaynaklar var | "X hakkında hangi arşivler var?" |
| **ARCHIVE_DEEP_DIVE** | Arşiv derin dalış + fond yol haritası | "BOA'da II. Mahmud dönemi tıbbiye HAT kayıtları?" |
| **MANUSCRIPT_TRANSCRIBE** | Yazma HTR (eScriptorium pipeline) | "Bu yazma sayfanın transkripsiyonu mümkün mü?" |
| **PROSOPOGRAPHY** | Biyografi + hizmet kaydı | "Mustafa Behçet Efendi'nin biyografisi" |
| **EVENT_RECONSTRUCTION** | Olay kurgulaması (gün-gün) | "31 Mart Vakası'nın kronolojisi" |
| **HISTORIOGRAPHY** | Tarih yazımı / literatür eleştirisi | "Tanzimat iktisadı üzerine literatürün durumu" |
| **CHRONOLOGY_CONVERSION** | Hicri/Rumî/Miladi + ebced/kronogram | "15 Receb 1287 Miladî karşılığı?" |
| **ACADEMIC_REPORT** | 10-bölümlü atıflı akademik rapor | "X üzerine akademik tarih raporu hazırla" |
| **KANUN_GEREKÇESİ** | Kanunun 5-katmanlı tarihî gerekçesi | "1219 sayılı Kanun'un tarihî gerekçesi" |

## Adım 4 — Slash Komutlarını Tanıt

| Komut | Mod | Ne yapar |
|-------|-----|----------|
| `/vekayinuvis-kaynak-avi` | SOURCE_HUNT | Kaynak matrisi (tür × erişim × dil × kanıt-yoğunluğu) |
| `/vekayinuvis-arsiv-dalis` | ARCHIVE_DEEP_DIVE | Fond/tasnif yol haritası + erişim talimatı |
| `/vekayinuvis-transkripsiyon` | MANUSCRIPT_TRANSCRIBE | IIIF → eScriptorium HTR pipeline |
| `/vekayinuvis-prosopografi` | PROSOPOGRAPHY | Yaşam çizelgesi + atama-azil zinciri + eser listesi |
| `/vekayinuvis-kronoloji` | CHRONOLOGY_CONVERSION | Üç-takvim tablosu + ebced/kronogram |
| `/vekayinuvis-rapor` | ACADEMIC_REPORT | Tam-uzunlukta atıflı akademik rapor |
| `/vekayinuvis-kanun-gerekce` | KANUN_GEREKÇESİ | TBMM-uyumlu 5-katmanlı tarihî gerekçe |

## Adım 5 — Niyete Göre Yönlendir

Kullanıcının ne üzerinde çalıştığını sorun. Yaygın iş akışları:

1. **"X konusunda hangi kaynaklar var?"** → `/vekayinuvis-kaynak-avi`.
2. **"Belirli bir arşivde/fonda ne var?"** → `/vekayinuvis-arsiv-dalis`.
3. **"Bir kişinin biyografisi/hizmet kaydı?"** → `/vekayinuvis-prosopografi`.
4. **"Bir tarihin takvim karşılığı / kronogram çözümü?"** → `/vekayinuvis-kronoloji`.
5. **"Tam bir akademik tarih raporu?"** → `/vekayinuvis-rapor`.
6. **"Bir kanunun tarihî gerekçe bölümü?"** → `/vekayinuvis-kanun-gerekce`
   (sağlık alanında `medical-history.md` otomatik yüklenir; `lex-sanitas` ile
   composable).

**Ayrım rehberi (scope guard):**
- Mevzuat reformu/taslak yazımı → `lex-sanitas` (vekayinuvis yalnız tarihî
  gerekçe bölümünü besler).
- Modern tıp literatürü / pipeline → `medical-research` / `pharmaintel`.
- Basılı/sunum çıktısı → `carbon-html-report` / `carbon-pptx` (downstream).

Kullanıcının yanıtını bekleyin ve uygun moda/komuta yönlendirin. Her çıktıda,
erişim-kısıtlı kaynaklarda gerçek arşiv çalışmasının **insan-araştırmacının
fiilî katılımını** gerektirdiğini; bu süitin o çalışmanın ön araştırması,
kaynak haritalandırması ve raporlama altyapısını sağladığını hatırlatın.
