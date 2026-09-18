---
description: Bir MEB kazanım kodundan TEDY orkestratörüyle etkileşimli öğrenim modülü üretir, derler ve tedy.online'da yayınlar
argument-hint: "<kazanım-kodu> (örn. FB.5.4.1.1) [mod QUIZ | MODULE | FLASHCARDS | GAME | EXPLAINER]"
---

`edupedia` skill'indeki kuralları `tedy` orkestratörüyle uygula. Girdi: $ARGUMENTS

1. `edupedia_rehber` → `bolum: "akis"`.
2. Kazanım kodundan ders ve sınıfı çıkar (örn. `FB.5.…` → Fen Bilimleri, 5. sınıf); emin değilsen kullanıcıya sor. `edupedia_kapsam(ders, sinif, kazanim_kodu)`.
3. Mod verilmediyse QUIZ öner. MODULE_DATA'yı rehbere göre yaz → `edupedia_derle` → FAIL kalmayana dek düzelt.
4. Kullanıcı onaylarsa `edupedia_yayinla`; dönen `url`'yi aynen ver. Coverage manifestosunu ve kapı raporunu özetle.

HTML'i kendin yazma; `edupedia_yayinla` sonucu olmadan "yayınlandı" deme.
