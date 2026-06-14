---
description: Tam 7-aşamalı Türkiye jenerik/biyobenzer fırsat taraması başlatır — brief standardizasyonundan (G0) konsolide karar raporuna (G6) kadar rxos orkestratörünü çalıştırır.
argument-hint: "[terapötik alan / molekül / indikasyon briefi]"
---

`rxpraxis:rxos` orkestratör skill'ini tam boru hattı modunda çalıştır.

**Kullanıcı briefi:** $ARGUMENTS

## Yürütme protokolü

1. **Pre-flight (CONNECTORS.md §8):** Bağlı connector'ları doğrula. ThoughtSpot
   `check_connectivity` → Pong yoksa Aşama 5 Bölüm B'nin atlanacağını (degrade mod) kullanıcıya
   bildir. TİTCK MCP + Türk Patent MCP canlılığını kontrol et.

2. **Aşama 0 (G0):** Kullanıcı briefini `skills/rxos/assets/brief-schema.json` şemasına oturt.
   8 kontrolü uygula. Eksik zorunlu alan varsa kullanıcıdan iste; uydurma. TA-kalibrasyonu
   (§0.C) üret.

3. **Aşama 1-5:** rxos §3 protokolünü sırayla çalıştır. **Kanonik önbellek disiplinini
   uygula** (canonical-cache-contract.md): `adis_pipeline` (Aşama 1) · `titck_canonical`
   (Aşama 2, TİTCK MCP **bir kez**) · `midas_extract` (Aşama 5b, annualize). Her aşama kalite
   kapısını geçmeden sonrakine **geçme** (BLOKER kapılar).

4. **Aşama 6 (G6):** Konsolide Markdown raporu üret (10-12 bölüm). İki katmanlı çıktı:
   okuyucu-yüzlü temiz kopya (Katman A) + render-dışı İç Denetim Kaydı (Katman B,
   provenance-standard.md §3).

5. **run_manifest.json:** `run-manifest-schema.json`'a uygun üret. `connector_call_ledger.titck_mcp.single_shot_enforced`
   alanını doğru işaretle (çift-sorgu yasağı kanıtı).

## Çıktı
`<RUN_ID>/` dizini: 6 JSON artefakt + `pilot_report.md` + `run_manifest.json`.
Run ID: `RxOS-YYYYMMDD-<TA>-<SUBTOPIC>-v<N>`.

## Scope guard
Hastane/IV ürün → reddet, kapsam dışı bildir. Bireysel SGK/dava → onko-erisim'e yönlendir.
