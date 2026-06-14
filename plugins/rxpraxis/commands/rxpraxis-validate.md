---
description: Tek bir molekül/ürün için hızlı fizibilite doğrulaması — tam 7-aşamalı taramanın değil, yalnız karar-kritik alt-kümenin (TİTCK kanonik dosya + eşdeğer grup doygunluğu + patent/veri imtiyazı engeli + fiyat tavanı) çalıştırılması. rxos boru hattının "fast-path" kısayolu.
argument-hint: "[tek INN / barkod / ürün — örn. 'dapagliflozin 10 mg film tablet']"
---

`rxpraxis:rxos` orkestratörünü **hızlı doğrulama (fast-path)** modunda çalıştır — tam G0-G6
boru hattını değil, bir tek aday için "yapılabilir mi / engel var mı" sorusunu yanıtlayan
karar-kritik alt-kümeyi.

**Aday:** $ARGUMENTS

## Ne zaman bu komut, ne zaman `/rxpraxis-scan`

| Kullanın | Bu komut (`-validate`) | Tam tarama (`-scan`) |
|---|---|---|
| Girdi | **Tek, adlandırılmış** molekül/ürün | TA / indikasyon / portföy briefi |
| Soru | "Bu aday yapılabilir mi, açık engel var mı?" | "Bu alanda hangi fırsatlar var?" |
| Kapsam | Aşama 2 + 4 alt-kümesi | Aşama 0-6 tümü |
| Çıktı | Tek sayfa GO / NO-GO / KOŞULLU kartı | 10-12 bölümlük konsolide rapor |

Girdi tek bir adlandırılmış aday değilse (TA taraması, "fırsatları bul" tipi) → bu komutu
çalıştırma, kullanıcıyı `/rxpraxis-scan`'a yönlendir.

## Yürütme protokolü (rxos fast-path)

1. **Pre-flight (CONNECTORS.md §8):** TİTCK MCP + Türk Patent MCP canlılığını doğrula.
   ThoughtSpot bu komutta zorunlu değildir (fiyat tavanı TİTCK referans fiyatından türetilir;
   MIDAS cross-country yalnız opsiyonel zenginleştirme).

2. **G0 — mini brief:** Adayı `skills/rxos/assets/brief-schema.json`'ın asgari alanlarına
   oturt (molekül + form + kanal). Kanal hospital/IV ise → reddet (scope guard). Form
   topikal/oral değilse uyar.

3. **TİTCK kanonik dosya (pharmapatent Mod 13 — TİTCK MCP BİR KEZ):** `titck_canonical`
   artefaktını üret (canonical-cache-contract.md §3.1): `search_drugs` → `get_drug` →
   `get_drug_snomed_profile` → `get_holder_portfolio` → `find_equivalent_products_by_substance`
   → `get_atc_class_summary`. **İki kez sorgulama** (single_shot_enforced).

4. **Doygunluk + fiyat (pharmaintel Türkiye Ürün Geliştirme M2/M4 alt-kümesi):**
   eşdeğer-grup doygunluk skoru (kaç ruhsatlı eşdeğer + holder yoğunlaşması) ve referans
   fiyat tavanı / eşdeğer grup fiyatı. "Kalabalık mı / fiyat tabanı çökmüş mü?" yargısı.

5. **Patent + veri imtiyazı engeli (pharmapatent Mod 1 + 5 alt-kümesi):** Türk Patent MCP
   (`search_patents`) + Orange/Purple Book + 6 yıllık veri imtiyazı + (varsa) ikinci tıbbi
   kullanım / formülasyon patenti taraması. **Bolar istisnası** notu. LoE/SPC ufku.

6. **Karar kartı:** GO / NO-GO / KOŞULLU (koşul listesiyle) — tek sayfa.

## Çıktı

`titck_canonical` JSON + tek sayfa **GO/NO-GO/KOŞULLU karar kartı**:
ruhsat durumu · eşdeğer-grup doygunluğu · fiyat tavanı · patent/veri imtiyazı engeli (tarih
ufkuyla) · net yargı + gerekçe. Her veri noktası provenance damgalı
(provenance-standard.md §1). İki katmanlı çıktı (Katman A karar kartı + Katman B İç Denetim
Kaydı).

`titck_canonical` artefaktı önbelleğe yazılır; kullanıcı ardından `/rxpraxis-scan` çalıştırırsa
Aşama 2 bu dosyayı **yeniden çıkarmaz**, okur (canonical-cache-contract.md §3.2).

## Sınırlılık beyanı (zorunlu)

Bu hızlı yol **tam fizibilite kararı değildir**: epidemiyoloji/funnel boyutlandırma (Aşama 1),
36-ülke MIDAS cross-country kanıtı (Aşama 5b) ve biowaiver/BCS değerlendirmesi
**çalıştırılmaz**. KOŞULLU/GO çıkan adaylar için tam `/rxpraxis-scan` önerilir. Bu sınır
çıktıda açıkça belirtilmelidir.

## Fallback
TİTCK MCP timeout → CONNECTORS.md §6 zinciri, caveat damgası. Türk Patent MCP erişilemezse
patent engeli "doğrulanamadı" olarak işaretlenir — sessizce "engel yok" varsayma.
