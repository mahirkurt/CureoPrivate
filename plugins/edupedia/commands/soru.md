---
description: Fotoğrafı çekilen veya yapıştırılan bir veya birden fazla sınav sorusunu pedagojik ilkelerle çözen + gerektirdiği kavram zincirini öğreten etkileşimli modül üretir
argument-hint: "<soru fotoğrafı veya soru metni> [+ opsiyonel ders/sınıf]"
---

`edupedia:carbon-edupedia` skill'ini **EXAM modunda** çağır. Mantığı burada tekrarlama —
skill'in modları, kalite kapıları ve pedagojik davranışı olduğu gibi geçerlidir; bu komut
yalnız soru → modül giriş noktasını kanonikleştirir.

**Girdi:** $ARGUMENTS *(bir veya birden fazla soru fotoğrafı ve/veya yapıştırılmış soru metni)*

## Yürütme protokolü

**Normatif kaynak: skill `references/exam-solving.md` — akışın TAMAMI oradadır.**
Bu komut kuralı **tekrarlamaz**; aşağıdaki liste yalnız bir haritadır.

1. **Referansı oku:** `references/exam-solving.md` (EXAM modunda zorunlu) +
   `references/adhd-pedagogy.md` (her modülden önce zorunlu).
2. **Transkripsiyon** (§2 Adım 1): her soruyu birebir metne çevir; şekil varsa yazar-SVG
   olarak yeniden çiz. **Belirsizlik varsa SOR** — neyin okunmadığını tam söyle.
   Fotoğraf gömülmez. Birden fazla soru varsa hangisini istediğini **sorma** — hepsi
   aynı HTML'de işlenir.
3. **Kümele** (§2 Adım 2b): soruları konuya göre grupla. Zincir konu başına, soru başına
   değil. n > 4 ise “oturum uzayacak” uyarısı ver; üretimi durdurma.
4. **KAPI** (§2 Adım 2): ders + sınıf kesinleşmeden üretim başlamaz. Kural tek yerde:
   `references/curriculum-integration.md` §3 Adım 0. Yoksa `AskUserQuestion` ile sor.
5. **Geriye çözümleme** (§2 Adım 3): her konu kümesi için "bunu çözmek için önce neyi
   bilmek gerekiyor?" → 2-4 halkalı kavram zinciri.
6. **Kazanım + çerçeve** (§2 Adım 4-5): her halkayı `search_learning_outcomes` ile
   kazanıma bağla; `list_textbooks` → `get_document_text` ile ders kitabını aç.
   Bağlanamıyorsa **D2**, kitap yoksa **D3** (§5).
7. **Çöz** (§2 Adım 6): her sorunun kendi demonstratif çözümü. Soru bozuksa **D1**,
   çerçeve üstüyse **D4** — öğe bazında; bir bozuk soru modülü iptal etmez.
8. **Kur + doğrula** (§2 Adım 7-8): tek soru `exam` bloğu + 11 segment; çoklu
   `topics[]` + `exams[]` + sıkıştırılmış kurgu (§4.4);
   `scripts/validate_module.py` ile G-EXAM dahil kapıları geçir;
   çıktı dizinine kebab-case adla kaydet + yan yana `.manifest.json`.

## Teslim

Sınav sorusu telifli olabilir; paylaşılmaz, siteye yüklenmez. Teslim yerel tek-dosya HTML'dir.

## Sınırlılık

- Kazanım kodundan modül isteniyorsa → `/edupedia:modul`; ders+sınıf+konudan →
  `/edupedia:mufredat`; yalnız "hangi kazanımlar" keşfi → `/edupedia:kazanim-bul`.
- MEB dışı müfredat (IB/Cambridge) kapsam dışıdır; çerçeve kurulamaz, dürüstçe söylenir.
