---
description: Ders, sınıf ve konudan doğrulanmış kazanımları bulup TEDY orkestratörüyle etkileşimli modül üretir
argument-hint: "<ders> <sınıf> <konu> (örn. Fen 5 maddenin hâlleri)"
---

`edupedia` skill'indeki kuralları uygula. Girdi: $ARGUMENTS

1. `edupedia_rehber` → `bolum: "akis"`; istek yaklaşan bir sınav ya da ödevle ilgiliyse `edupedia_baglam`.
2. `edupedia_kapsam(ders, sinif, konu)`; dönen kazanımları göster ve hangisine odaklanılacağını sor.
3. MODULE_DATA → `edupedia_derle` → FAIL kalmayana dek düzelt → isteğe bağlı `edupedia_onizle` → onayla `edupedia_yayinla` (sınava bağlıysa `ted_link`).
4. `url`'yi, coverage manifestosunu ve kapı raporunu bildir.
