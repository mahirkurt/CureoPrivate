---
description: Mod 1 DRAFT — sıfırdan sağlık mevzuatı taslağı üretimi (yönetmelik/tebliğ/CBK). 5210 Md.15 madde sırası + üst-norm zinciri + AB/uluslararası benchmark + içtihat/doktrin + genel/madde gerekçesi. Argüman = üretilecek düzenlemenin konusu ve türü.
argument-hint: <konu ve mevzuat türü — örn. "ATMP ileri tedavi tıbbi ürünleri yönetmeliği">
---

# /lex-draft — Mod 1 DRAFT (yeni mevzuat üretimi)

Talep: **$ARGUMENTS**

`lex-sanitas` flagship skill'ini **Mod 1 DRAFT** olarak çalıştır. Süit sözleşmeleri normatiftir: [`shared/composition-contract.md`](../skills/lex-sanitas/shared/composition-contract.md), [`shared/coverage-manifest.md`](../skills/lex-sanitas/shared/coverage-manifest.md).

## Yürütme

1. **Scope Guard (§6).** Reform-dışıysa (bireysel dava/promosyon) → yönlendir, dur.
2. **Tam-filo (G0, zorunlu).** `references/00-mod-pipelines.md` Mod 1 server-listesini `legal-distiller` alt-ajanına tek görevde ver; wire'lı 19 MCP + bağlı companion **tamamı** süpürülsün, kompakt `retrieval_distillate` + `coverage` dönsün.
3. **Klinik boyut varsa → evidentia'ya delege et** (§5; zenginleştirilmiş sorgu, `epistemic_dual_label:true`).
4. **DRAFT 11-adım pipeline'ı** uygula (`references/00-mod-pipelines.md` → Mod 1): üst-norm zinciri → yatay semantik tarama → mülga taraması → AB/uluslararası benchmark → içtihat+doktrin → Md.15 iskelet → Md.4+10-22+25 yazım → yan belgeler → kaynakça → R9 15-nokta dil QC.
5. **Template:** [`templates/yonetmelik-taslagi.md`](../skills/lex-sanitas/templates/yonetmelik-taslagi.md) veya [`templates/teblig-taslagi.md`](../skills/lex-sanitas/templates/teblig-taslagi.md). Gerekçe: [`templates/genel-gerekce.md`](../skills/lex-sanitas/templates/genel-gerekce.md) + [`templates/madde-gerekce.md`](../skills/lex-sanitas/templates/madde-gerekce.md).
6. **Kapılar G0-G7.** `evidence_ledger` tut; her atıf MCP-doğrulanmış (no-fabrication).
7. **sci-audit'e delege et** (§5 — `/verify-citations` + `/check-turkish`).
8. **Kapsam manifestosu (G0) + confidence_label** ile bitir. İnsan denetimi zorunlu.
