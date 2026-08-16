---
name: lex-analyze
description: Mod 3 ANALYZE — mevcut sağlık mevzuatının reform-öncesi analizi (7-boyut uyum denetimi + AB/uluslararası sapma + Türk yargı/doktrin filtresi + iptal-riski). "Neyi değiştireceğiz?" sorusunu yanıtlar. Argüman = incelenecek mevzuat.
argument-hint: <incelenecek mevzuat — örn. "1219 sayılı Tababet Kanunu belirlilik denetimi">
---

# /lex-analyze — Mod 3 ANALYZE (reform-öncesi analiz)

Talep: **$ARGUMENTS**

`lex-sanitas` flagship skill'ini **Mod 3 ANALYZE** olarak çalıştır.

## Yürütme

1. **Scope Guard (§6).** (Bireysel dava değil — mevzuatın kendisinin analizi.)
2. **Tam-filo (G0).** `legal-distiller` ile Mod 3 server-listesi. Load-bearing: mevzuat + Yarg + yok-akademik + karşılaştırmalı (health-policy/german-law/eudamed).
3. **Klinik boyut → evidentia.**
4. **ANALYZE 8-adım:** hedef + paralel üst-norm zinciri → **7-boyut uyum denetimi** (üst-norm Md.4/a · amaç-içerik Md.4/b · belirlilik Md.4/e+AYM · atıf Md.21 · madde yapısı Md.10-16 · yükümlülük kanuniliği Md.24 · dil Md.25) → benchmark sapma analizi → Türk yargı+doktrin filtresi (AYM/Danıştay/Yargıtay/AİHM/ABAD) → iptal-riski değerlendirmesi → mukayeseli zayıflık haritası → rapor.
5. **Çıktı:** hiyerarşik bulgu + risk ısı-haritası + düzeltme önerileri.
6. **Kapılar G0-G7**, `evidence_ledger`, no-fabrication.
7. **sci-audit'e delege et.**
8. **Kapsam manifestosu + confidence_label** ile bitir.
