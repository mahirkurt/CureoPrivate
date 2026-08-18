---
name: lex-draft
description: Mod 1 DRAFT — sıfırdan sağlık mevzuatı taslağı üretimi (yönetmelik/tebliğ/CBK). 5210 Md.15 madde sırası + üst-norm zinciri + AB/uluslararası benchmark + içtihat/doktrin + genel/madde gerekçesi. Argüman = üretilecek düzenlemenin konusu ve türü.
argument-hint: <konu ve mevzuat türü — örn. "ATMP ileri tedavi tıbbi ürünleri yönetmeliği">
---

# /lex-draft — Mod 1 DRAFT (yeni mevzuat üretimi)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 1 DRAFT** olarak çalıştır. Süit sözleşmeleri normatiftir: [`shared/composition-contract.md`](../skills/cureolex/shared/composition-contract.md), [`shared/coverage-manifest.md`](../skills/cureolex/shared/coverage-manifest.md).

## Yürütme

1. **Scope Guard (§6).** Reform-dışıysa (bireysel dava/promosyon) → yönlendir, dur.
2. **Tam-filo (G0, zorunlu).** Belirsiz manzara varsa önce kısa ANALYZE landscape distillate. Sonra `references/00-mod-pipelines.md` Mod 1 listesini `legal-distiller` + `comparative-law-researcher` shard'larına ver; **tools_used semantik sırası eksiksiz** (kalıcı alt küme yok).
3. **Klinik boyut varsa → evidentia'ya delege et** (§5; zenginleştirilmiş sorgu, `epistemic_dual_label:true`).
4. **DRAFT pipeline** (`00-mod-pipelines` Mod 1): üst-norm + **Md.90/5** → semantik tarama → mülga → AB/uluslararası (german **resolve→EU**; ich **M4/M8** dosya-yapısıysa; cihaz→eudamed) → içtihat+doktrin → Md.15 iskelet → yazım → yan belgeler → kaynakça → R9 QC.
5. **Template:** [`templates/yonetmelik-taslagi.md`](../skills/cureolex/templates/yonetmelik-taslagi.md) veya [`templates/teblig-taslagi.md`](../skills/cureolex/templates/teblig-taslagi.md). Gerekçe: [`templates/genel-gerekce.md`](../skills/cureolex/templates/genel-gerekce.md) + [`templates/madde-gerekce.md`](../skills/cureolex/templates/madde-gerekce.md).
6. **Kapılar G0-G7.** `evidence_ledger` tut; her atıf MCP-doğrulanmış (no-fabrication).
7. **sci-audit'e delege et** (§5 — `/verify-citations` + `/check-turkish`).
8. **Kapsam manifestosu (G0) + confidence_label** ile bitir. İnsan denetimi zorunlu.
