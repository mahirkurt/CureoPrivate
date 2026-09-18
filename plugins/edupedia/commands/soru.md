---
description: Fotoğrafı çekilen ya da yapıştırılan sınav sorularını TEDY orkestratörüyle EXAM modunda çözüp öğreten modül taslağı hazırlar
argument-hint: "<soru fotoğrafı veya metni> [+ ders ve sınıf]"
---

Girdi: $ARGUMENTS

1. `edupedia_rehber` → önce `bolum: "akis"`, sonra `bolum: "sinav"`.
2. Sorunun dersini ve sınıfını belirle (emin değilsen sor); `edupedia_kapsam(ders, sinif, konu)`.
3. EXAM modunda MODULE_DATA yaz → `edupedia_derle` → FAIL kalmayana dek düzelt → `edupedia_onizle`.
4. Önizleme bağlantısını ver. EXAM modu yayınlanmaz; `edupedia_yayinla` çağırma.

Soru görselini araç çağrısına bayt olarak koyma; soru metnini kendin yazıya dök.
