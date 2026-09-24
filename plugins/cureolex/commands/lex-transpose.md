---
name: lex-transpose
description: "Mod 11 TRANSPOSITION — ulusüstü normun (AB direktifi/tüzüğü, andlaşma, model kanun) ev yargı bölgesinde madde-madde karşılanmasını tablolar: Tam · Kısmi · Yok · Aşan (gold-plating) · Uygulanmaz. Önce G11: normun ev bölgesindeki hukuki rolü (binding / transposition_source / comparative_benchmark / treaty_obligation) paketten belirlenir. Argüman = kaynak norm + ev yargı bölgesi."
argument-hint: '<kaynak norm + ev bölgesi — örn. "Direktif 2001/83/EC farmakovijilans hükümleri → TR">'
---

# /lex-transpose — Mod 11 TRANSPOSITION (aktarım / uyum tablosu)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 11 TRANSPOSITION** olarak çalıştır. Template: [`templates/transposition-table.md`](../skills/cureolex/templates/transposition-table.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Paketi yükle (§1.5)** — ev yargı bölgesi. `gate_params.G11` AB üyeliği / ikili anlaşma / alt birim notunu taşır.
3. **G11 — rol tespiti ÖNCE.** Kaynak normun ev bölgesindeki rolü kanıt defterine `jurisdiction` + `jurisdiction_role` olarak yazılır. AB üyesi olmayan bölgede AB normu `comparative_benchmark`'tır: tablo başlığı "Uyum Analizi" olur, "aktarım yükümlülüğü" dili KULLANILMAZ.
4. **Kaynak norm (G6 + G10):** CELEX/ELI `mcp__eurlex__eurlex_lookup_celex` ile doğrulanır; güncel konsolide hâl ve değişiklik zinciri `eurlex_get_relations` ile. Üye devlet uygulama emsali: german-law `get_german_implementations`, fedlex (CH özerk uyum), Ansvar (bağlıysa).
5. **Ulusal karşılık:** paketin S1 bağlayıcısıyla madde-madde; referans tarihine göre yürürlükteki metin (G10).
6. **Kapılar:** G0, G1, G2, G6, G7, G10, G11. `evidence_ledger` + `home_jurisdiction`.
7. **sci-audit'e delege et** · **kapsam manifestosu + confidence_label** ile bitir.
