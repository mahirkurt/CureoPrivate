---
name: lex-comply
description: Mod 4 COMPLY — bir reform metninin 5210 uyum denetimi (R6b 21-nokta yürütülebilir rubrik; her kontrol PASS/FAIL/CONDITIONAL/N/A + test + düzeltme + risk ağırlığı). Yalnız YENİ reform metnini denetler; promosyon materyali DEĞİL (→ promo-censor). Argüman = denetlenecek taslak metin.
argument-hint: <denetlenecek taslak — dosya yolu veya yapıştırılan metin>
---

# /lex-comply — Mod 4 COMPLY (5210 uyum denetimi)

Hedef metin: **$ARGUMENTS**

`lex-sanitas` flagship skill'ini **Mod 4 COMPLY** olarak çalıştır. Rubrik: [`references/06b-compliance-executable-rubric.md`](../skills/lex-sanitas/references/06b-compliance-executable-rubric.md).

## Yürütme

1. **Scope Guard (§6).** Promosyonel/MLR denetimi → `promo-censor`.
2. **Tam-filo (G0).** `legal-distiller` ile Mod 4 server-listesi (mevzuat load-bearing; resmi-gazete/titck/saglikbakanligi/Yarg/karşılaştırmalı çapraz).
3. **R6b 21-nokta rubriği uygula** — her kontrol (K-1…K-21) test prosedürü + PASS/FAIL/CONDITIONAL/N/A + düzeltme + risk ağırlığı. **K-1 (üst-norm) önce**; FAIL ise dur → kapsamlı revizyon.
4. **Eşikler:** tümü PASS/N-A & CONDITIONAL≤3, FAIL=0 → YAYINA HAZIR; 1 yüksek-risk FAIL → düzeltme zorunlu; FAIL≥2 → kapsamlı revizyon; FAIL≥5 veya K-1/K-17 FAIL → tasarımı yeniden gözden geçir.
5. **Çıktı:** 21-nokta rapor + R6b skor-kartı + verdict.
6. **Kapılar G0-G7.** `compliance-auditor` alt-ajanına düşman-doğrulama (adversarial) yaptır.
7. **sci-audit'e delege et.**
8. **Kapsam manifestosu + confidence_label** ile bitir.
