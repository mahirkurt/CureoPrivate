---
name: lex-amend
description: Mod 2 AMEND — mevcut sağlık mevzuatında değişiklik (madde/ibare değişikliği, ek madde, geçici madde, ilga). Md.18-21 değişiklik tekniği + kümülatif önceki metinler + karşılaştırma cetveli + madde gerekçesi. Argüman = değiştirilecek mevzuat ve değişikliğin niteliği.
argument-hint: <mevzuat + değişiklik — örn. "Beşeri Tıbbi Ürünler Ruhsat Yön. m.12 fıkra ekle">
---

# /lex-amend — Mod 2 AMEND (mevzuat değişikliği)

Talep: **$ARGUMENTS**

`lex-sanitas` flagship skill'ini **Mod 2 AMEND** olarak çalıştır.

## Yürütme

1. **Scope Guard (§6).**
2. **Tam-filo (G0).** `legal-distiller` ile Mod 2 server-listesini süpür (`references/00-mod-pipelines.md`). Load-bearing: `mcp__mevzuat__get_onceki_metinler` (kümülatif). Companion + karşılaştırmalı da ateşle, manifestoya gir.
3. **Klinik/bilimsel-temel değişikliği ise → evidentia** (koşullu).
4. **AMEND 8-adım:** hedefi çek → `get_onceki_metinler` → değişiklik tipini sınıfla (Md.19 madde / Md.20 ibare / Md.16 ek-geçici / Md.21-8 ilga) → çerçeve-madde (Md.18 eski→yeni) → atıf (Md.21 sıfırsız tarih) → karşılaştırma cetveli → madde gerekçesi → R9 QC.
5. **Template:** [`templates/karsilastirma-cetveli.md`](../skills/lex-sanitas/templates/karsilastirma-cetveli.md) + [`templates/madde-gerekce.md`](../skills/lex-sanitas/templates/madde-gerekce.md).
6. **Kapılar G0-G7**, `evidence_ledger`, no-fabrication.
7. **sci-audit'e delege et.**
8. **Kapsam manifestosu + confidence_label** ile bitir.
