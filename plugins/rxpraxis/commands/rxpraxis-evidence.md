---
description: Saf bilimsel/klinik kanıt sentezi — global literatür + trial + kılavuz + Türkiye verisi + (gerekirse) epidemiyoloji. medical-research'ün 20+ connector'ını çalıştırır. rxos Aşama 1'in tek-skill kısayolu.
argument-hint: "[klinik soru / molekül / indikasyon]"
---

`rxpraxis:medical-research` çağır — maksimal derinlikte kanıt sentezi.

**Soru:** $ARGUMENTS

## Yürütme

0. **Araç yükleme (tool-manifest.json — L1):** `shared/tool-manifest.json`
   `commands.rxpraxis-evidence` bloğunu pin-yükle (akademik çekirdek + AdisInsight). Pre-flight
   §8 + §9 (PubMed ratelimit → Exa/Scholar Gateway/bioRxiv/Paper Search cascade). **Bağlam
   uyarısı (kritik):** bu komut en yüksek bağlam-riskli komuttur — akademik tam-metin dump'ları
   büyüktür. Her geri çağırma **extract-then-evict** (canonical-cache §9): özet/atıf çıkar →
   ham tam-metni düşür → diske yaz. Sub-agent ortamında (canonical-cache §8) bu skill izole
   context'te koşmalı, orkestratöre yalnız ≤1-sayfa sentez + Vancouver atıf listesi dönmeli.

1. **Domain classifier (10-axis):** sinyal taraması → ilgili specialty katmanı yükle.
2. **Paralel çağrı listesi (native-first):** PubMed/EPMC (≥2×25) + bioRxiv + ClinicalTrials
   + Consensus + Scholar Gateway + Paper Search + YÖK Tez + 6-ülke AFF döngüsü + Türkiye Dörtlüsü
   (TİTCK + Mevzuat + YÖK + AFF:"Turkey") + (0.5.I ise) AdisInsight + (0.5.K ise) WHO GHO + ICD-11.
3. **Kanonik:** drug/MoA sinyalinde `adis_pipeline` üret (canonical-cache §5) — aynı molekül için
   `scan-ledger` triyaj preludünden gelen bir `adis_pipeline` varsa **oku**, yeniden çekme
   (AdisInsight-erken / tek-sefer disiplini).
4. **Tam metin (gerekirse):** EPMC PMC → copyright_status → Paper Download cascade (copyright-disiplinli).

## Çıktı
İki katmanlı (medical-research v8.1): dergi-kalitesinde temiz kopya (Katman A) + render-dışı
İç Denetim Kaydı (Katman B). Vancouver atıf (PMID/DOI/NCT + erişim). VIZ direktifleri yalnız
HTML yorum içinde.

## Scope guard
Ticari/regülatuar frame gerekiyorsa → `/rxpraxis-scan` veya `rxpraxis:pharmaintel`.
