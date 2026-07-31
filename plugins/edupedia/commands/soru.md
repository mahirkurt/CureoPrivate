---
description: Fotoğrafı çekilen veya yapıştırılan bir sınav sorusunu pedagojik ilkelerle çözen + gerektirdiği kavram zincirini öğreten etkileşimli modül üretir
argument-hint: "<soru fotoğrafı veya soru metni> [+ opsiyonel ders/sınıf]"
---

`edupedia:carbon-edupedia` skill'ini **EXAM modunda** çağır. Mantığı burada tekrarlama —
skill'in modları, kalite kapıları ve pedagojik davranışı olduğu gibi geçerlidir; bu komut
yalnız soru → modül giriş noktasını kanonikleştirir.

**Girdi:** $ARGUMENTS *(soru fotoğrafı veya yapıştırılmış soru metni)*

## Yürütme protokolü

**Normatif kaynak: skill `references/exam-solving.md` — akışın TAMAMI oradadır.**
Bu komut kuralı **tekrarlamaz**; aşağıdaki liste yalnız bir haritadır.

1. **Referansı oku:** `references/exam-solving.md` (EXAM modunda zorunlu) +
   `references/adhd-pedagogy.md` (her modülden önce zorunlu).
2. **Transkripsiyon** (§2 Adım 1): soruyu birebir metne çevir; şekil varsa yazar-SVG
   olarak yeniden çiz. **Belirsizlik varsa SOR** — neyin okunmadığını tam söyle.
3. **KAPI** (§2 Adım 2): ders + sınıf kesinleşmeden üretim başlamaz. Kural tek yerde:
   `references/curriculum-integration.md` §3 Adım 0. Yoksa `AskUserQuestion` ile sor.
4. **Geriye çözümleme** (§2 Adım 3): "bunu çözmek için önce neyi bilmek gerekiyor?"
   → 2-4 halkalı kavram zinciri.
5. **Kazanım + çerçeve** (§2 Adım 4-5): her halkayı `search_learning_outcomes` ile
   kazanıma bağla; `list_textbooks` → `get_document_text` ile ders kitabını aç.
   Bağlanamıyorsa **D2**, kitap yoksa **D3** (§5).
6. **Çöz** (§2 Adım 6): her adımın dayanağı kitap sayfası. Soru bozuksa **D1**,
   çerçeve üstüyse **D4**.
7. **Kur + doğrula** (§2 Adım 7-8): `exam` bloğu (§3) + 11 segmentlik kurgu (§4);
   `scripts/validate_module.py` ile G-EXAM dahil kapıları geçir;
   `/mnt/user-data/outputs/` altına kebab-case adla kaydet + yan yana `.manifest.json`.

## Yayın

**Bu modda yayın TEKLİF EDİLMEZ** (`exam-solving.md` K2 — telif). `/edupedia:modul` ve
`/edupedia:mufredat`'ın aksine "yayınlamamı ister misin?" sorusu **sorulmaz**.

Kullanıcı kendisi isterse: telif uyarısını ver ("bu soru size ait değilse
edupedia.cureonics.com'da yayınlamak telif ihlali olabilir"), sonra karar kullanıcınındır —
engelleme.

## Sınırlılık

- Fotoğrafta **birden çok soru** varsa hangisini istediğini **sor** — bu komut tek soru
  işler (§7).
- Kazanım kodundan modül isteniyorsa → `/edupedia:modul`; ders+sınıf+konudan →
  `/edupedia:mufredat`; yalnız "hangi kazanımlar" keşfi → `/edupedia:kazanim-bul`.
- MEB dışı müfredat (IB/Cambridge) kapsam dışıdır; çerçeve kurulamaz, dürüstçe söylenir.
