---
description: Mod 9 EX_POST_EVALUATION — yürürlükteki reformun geriye dönük etki değerlendirmesi (12-36 ay sonra). 5 OECD kriteri (Etkililik/Verimlilik/Tutarlılık/İlgililik/AB-değeri) + ex-ante↔ex-post karşılaştırma + karar (K-1 Koru / K-2 Revize→AMEND / K-3 Sunset/İlga). evidentia ex_post_metrics zorunlu. Argüman = değerlendirilecek yürürlükteki mevzuat + dönem.
argument-hint: <mevzuat + dönem — örn. "Endikasyon-dışı ilaç kullanımı yönetmeliği, 24 ay">
---

# /lex-expost — Mod 9 EX_POST_EVALUATION (geriye dönük değerlendirme)

Talep: **$ARGUMENTS**

`lex-sanitas` flagship skill'ini **Mod 9 EX_POST_EVALUATION** olarak çalıştır. Template: [[`templates/ex-post-evaluation.md`](../skills/lex-sanitas/templates/ex-post-evaluation.md)](../skills/lex-sanitas/templates/ex-post-evaluation.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Tam-filo (G0).** `legal-distiller` ile Mod 9 server-listesi. Load-bearing: mevzuat (yürürlük tarihçesi) + resmi-gazete + titck + saglikbakanligi + oecd + Yarg + health-policy (programatik zaman-serisi).
3. **evidentia ◆ zorunlu:** §5,7,13.c,14.d,19 + **`ex_post_metrics` bloğu** (sidecar 2.3.1: elapsed_months + ≥1 veri bloğu).
4. **EX_POST 10-adım:** kapsam+dönem+değerlendirme-tipi → ex-ante varsayımları derle (Mod 6 DEA/BEF) → gerçek uygulama verisi (ÜTS/MIDAS/MEDULA/RWE/paydaş + programatik zaman-serisi) → **5 OECD kriteri** karşısında ölç → yargısal-denetim derlemesi → paydaş-geri-bildirim → mukayeseli ex-post → bütüncül hüküm → **karar K-1/K-2/K-3** → düzeltici yol haritası → EDR.
5. **Kapılar tümü + G9.** `evidence_ledger`, no-fabrication.
6. **sci-audit'e delege et.**
7. **Kapsam manifestosu + confidence_label** ile bitir. K-2 kararı → `/lex-amend`'e köprü.
