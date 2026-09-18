---
description: Bir konuya denk gelen doğrulanmış MEB kazanımlarını TEDY orkestratörüyle listeler (modül üretmez)
argument-hint: "<konu> [sınıf] [ders] (örn. kesirler 5. sınıf matematik)"
---

Girdi: $ARGUMENTS

1. Ders ya da sınıf eksikse kullanıcıya sor; ikisi de `edupedia_kapsam` için zorunludur.
2. `edupedia_kapsam(ders, sinif, konu)` çağır; kazanım kodlarını ve metinlerini, ders kitabı çerçevesini (belge ve sayfalar) ve coverage manifestosunu raporla.
3. Modül üretme, MODULE_DATA yazma. Kullanıcı modül isterse `/edupedia:mufredat` ya da `/edupedia:modul` öner.

Boş sonuç yokluk kanıtı değildir; kazanım uydurma.
