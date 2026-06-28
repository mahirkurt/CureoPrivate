---
description: Tam çok-kaynaklı kanıt sentezi koşumu — medical-research v8.4.0 flagship'ini kapsam→çoklu-kaynak→çapraz-doğrulama→sentez→temiz-kopya protokolüyle çalıştırır. Argüman = araştırma sorusu (molekül, hastalık, kılavuz/HTA, TR ruhsat/fiyat, pipeline).
argument-hint: <araştırma sorusu — molekül / hastalık / kılavuz / TR pazar>
---

# /evidentia — Tam Kanıt Sentezi Koşumu

Kullanıcı sorusu: **$ARGUMENTS**

`medical-research` v8.4.0 flagship skill'ini **eksiksiz** çalıştırın. Süit bağlamında
[`CONNECTORS.md`](../CONNECTORS.md) ve [`shared/canonical-cache-contract.md`](../shared/canonical-cache-contract.md)
**normatiftir**.

## Yürütme

1. **Pre-flight (kısa).** Soru kapsamına göre hangi connector gruplarının gerektiğini belirle;
   yüzey-bilinçli bağlanırlığı doğrula (claude.ai'de Tier-K/O manuel olabilir — CONNECTORS.md §6).
   Eksik connector → fallback merdivenini (CONNECTORS.md §2) kullan, durma.

2. **medical-research Adım 0–5'i çalıştır:**
   - **Adım 0/0.5** — zorunlu yükleme + 10-eksen sınıflandırıcı (Onko/Heme/Regülatuar/HTA/
     MedAffairs/İmmün/Nöro/Nadir/DrugIntel/Epidemiyoloji sinyali).
   - **Adım 1** — native-MCP-first paralel çağrı listesi (Akademik Çekirdek + Extended Tier +
     6-ülke AFF + Türkiye Dörtlüsü + Kılavuz/HTA + aktif eksen paketleri). **Genişletme
     connector'ları** (`med-terminologies`, `nih-clinicaltables`, `nlm-rxnorm`, `iuphar-gtopdb`)
     Extended Tier'de **opsiyonel native-first** kaynaktır → topluluk-yayıncı: **sandbox-first,
     least-privilege**.
   - **Adım 2** — cömertlik ilkesi (uncapped getirme).
   - **Adım 3** — çıktı sözleşmesi (numaralı bölümler 1–21; aktif eksene göre).
   - **Adım 4/5** — kullanıcı etkileşimi + **temiz-kopya doktrini** (VIZ/OPS yorum izolasyonu;
     araç-sızıntısı yok).

3. **Tek-sefer disiplini.** TİTCK barcode bir kez çözülür; openfda tekil+retry+skippable.
   Kanonik artefaktlar (`evidence_corpus`, `titck_record`,
   `regulatory_snapshot`, `terminology_map`) paylaşılır (canonical-cache-contract.md).

4. **Çapraz-doğrulama (bağlayıcı).** Hasta-etkili her iddia (doz, DDI, terminoloji, endikasyon)
   **iki bağımsız kaynakla** doğrulanır; topluluk-MCP çıktısı otoriter kaynak (KÜB/SPL/kılavuz)
   olmadan klinik karar olarak sunulmaz (CONNECTORS.md §5). DDI **"etkileşim verisi"** olarak
   sunulMAZ (substance-overlap ayrımı).

5. **Boşluk dürüstlüğü.** Bulunamayan veri "VERİ BULUNAMADI" + denenen sorgularla raporlanır;
   sessiz atlama yok.

## Ağır koşum

Geniş fan-out (çok eksen + çok ülke + tam-metin) bekleniyorsa `evidence-synthesizer` alt-ajanını
tetikle: ham connector gürültüsünü izole eder, yalnız damıtılmış kanonik artefaktları döndürür.

## Devir (Scope Guard)

Bireysel SGK/dava → `ius-salutis`/`onko-erisim`; MLR → `promo-censor`; ticari/IP →
`pharmaintel`/`pharmapatent`; yayın render → `carbon-html-report`/`carbon-pptx`.
