---
name: start
description: rxpraxis süitine giriş ve yönlendirme. Bağlı MCP connector'larını kontrol eder, süitin beş skill'ini ve altı komutunu tanıtır, kullanıcının niyetine göre doğru skill'e veya tam fırsat-tarama boru hattına yönlendirir. İlk kez süitle çalışırken, hangi connector'ların bağlı olduğunu görmek için, ya da "rxpraxis nedir / nereden başlamalıyım / hangi skill'i kullanmalıyım" türü oryantasyon sorularında kullanın. Tetikleyiciler — rxpraxis başlat, süit oryantasyonu, connector kontrolü, "ne yapabilirsin", "nereden başlayayım", "hangi skill".
version: 1.0.0
last_updated: 2026-06-14
---

# rxpraxis — Başlangıç ve Yönlendirme

rxpraxis, **Türkiye-merkezli farmasötik pazar zekâsı ve jenerik/biyobenzer fırsat tarama**
süitidir. Kullanıcıyı süitle tanıştırıp doğru araca yönlendirin. Aşağıdaki adımları sırayla
izleyin.

> Connector envanteri, skill-eşlemesi ve fallback zincirleri için tek doğruluk kaynağı:
> [CONNECTORS.md](../../CONNECTORS.md). Kanonik önbellek ve orkestrasyon disiplini:
> [canonical-cache-contract.md](../../shared/canonical-cache-contract.md).

## Adım 1 — Karşılama

Şu mesajı gösterin:

```
rxpraxis — Türkiye Farmasötik Fırsat Tarama Süiti

Dağınık ticari, regülatuar, bilimsel ve patent zekâsını tek bir savunulabilir
"jenerik/biyobenzer fırsat" kararına dönüştürür. rxos orkestratörü dört kaynak-tipi
skill'i (medical-research · pharmaintel · pharmapatent · thoughtspot-roche) yedi
aşamalı deterministik bir boru hattıyla (G0-G6 kalite kapıları) çağırır; çift connector
sorgusunu paylaşılan kanonik önbellekle engeller.

Kapsam: retail/topluluk-eczanesi · oral + topikal küçük molekül · TÜM terapötik alanlar.
Kapsam dışı: hastane kanalı (IV/infüzyon).
```

## Adım 2 — Bağlı MCP Connector'larını Kontrol Et

Bağlı araçları listeleyip aşağıdaki gruplara göre raporlayın. Her grupta hangi connector'ın
**canlı**, hangisinin **bağlı değil** olduğunu açıkça belirtin. Pre-flight zorunluları
(CONNECTORS.md §8) işaretleyin.

**Türkiye Yerel Katmanı (süitin omurgası):**
- TİTCK MCP — TR beşeri tıbbi ürün kanonik dataset (56 araç) · *tek-sefer kuralı*
- Mevzuat MCP — SMK + yönetmelik + tebliğ + Resmi Gazete (19 araç)
- Türk Patent MCP — patent + marka + endüstriyel tasarım (6 araç)
- YÖK Tez MCP — TR/EN tez araması

**IQVIA MIDAS / Ticari Katman (cross-country):**
- ThoughtSpot Spotter MCP — oturum-tabanlı (5 araç) · *pre-flight `check_connectivity` zorunlu*
- MIDAS REST (`midas-mcp` Worker) — ham değer yolu (Path B)

**Regülatuar + Epidemiyoloji:**
- RegulatoryMCP — openFDA + ICD-11 + WHO GHO (latency-prone, skippable)

**Akademik Çekirdek:**
- PubMed/EuropePMC · ClinicalTrials · bioRxiv · Consensus · Scholar Gateway · Paper Search ·
  AdisInsight · Exa · Tavily · NPI Registry

Bağlı olmayan connector'lar için kullanıcıya, araç menüsünden (Settings → Connectors)
etkinleştirebileceğini bildirin. Kritik eksiklerin etkisini söyleyin (örn. ThoughtSpot yoksa
36-ülke MIDAS katmanı atlanır → Aşama 5 degrade çalışır).

## Adım 3 — Süitin Skill'lerini Tanıt

| Skill | Ne Yapar | rxos aşaması |
|-------|----------|--------------|
| **rxos** | 7-aşamalı orkestratör — brief'ten konsolide fırsat raporuna | tümü |
| **medical-research** | Global tedavi peyzajı + kanıt sentezi (20+ akademik connector) | Aşama 1 |
| **pharmaintel** | Ticari/regülatuar/pipeline zekâsı + Türkiye Ürün Geliştirme (M1-M7) | Aşama 2, 5 |
| **pharmapatent** | Patent FTO + LOE + Bolar + TİTCK kanonik dosya (Mod 13) | Aşama 2, 4 |
| **thoughtspot-roche** | IQVIA MIDAS 36-ülke cross-country sizing | Aşama 5b |

## Adım 4 — Komutları Tanıt

| Komut | Ne Yapar |
|-------|----------|
| `/rxpraxis-scan` | Tam 7-aşamalı fırsat taraması (brief → konsolide rapor) |
| `/rxpraxis-validate` | Tek-asset fizibilite doğrulaması (hızlı yol) |
| `/rxpraxis-regulatory` | Regülatuar snapshot + TİTCK kanonik dosya |
| `/rxpraxis-patent` | Patent FTO / LOE / Bolar penceresi |
| `/rxpraxis-midas` | IQVIA MIDAS cross-country pazar boyutu |
| `/rxpraxis-evidence` | Saf bilimsel kanıt sentezi |

## Adım 5 — Niyete Göre Yönlendir

Kullanıcının ne üzerinde çalıştığını sorun. Yaygın iş akışlarına göre başlangıç önerin:

1. **"X molekülünde TR'de jenerik fırsatı var mı?"** → `/rxpraxis-scan` (tam boru hattı) veya
   tek molekül için `/rxpraxis-validate`.
2. **"Bu ilacın TR ruhsat/fiyat/eşdeğer grup durumu ne?"** → `/rxpraxis-regulatory` (pharmapatent Mod 13).
3. **"Jenerik X ne zaman piyasaya girebilir? / patent duvarı?"** → `/rxpraxis-patent`.
4. **"36 ülkede bu ürünün pazar boyutu / fiyat koridoru?"** → `/rxpraxis-midas`.
5. **"Bu indikasyonda kanıt/kılavuz ne diyor?"** → `/rxpraxis-evidence` (medical-research).

**Ayrım rehberi (scope guard):**
- Bireysel SGK/dava → bu süit değil, `onko-erisim`.
- MLR/promosyon denetimi → `promo-censor`.
- Mevzuat reformu/taslak → `cureolex`.
- Hastane/IV ürün → kapsam dışı (CONNECTORS.md §scope).

Kullanıcının yanıtını bekleyin ve uygun skill/komuta yönlendirin. Tam tarama için her zaman
önce bir brief'in `rxos` Aşama 0 şemasına (G0 kapısı) oturtulması gerektiğini hatırlatın.
