---
description: Bir konuya denk gelen MEB kazanımlarını keşfeder ve her birini KB becerisine ile önerilen etkileşime haritalar (modül ÜRETMEZ)
argument-hint: "<konu> [sınıf] [ders] (örn. kesirler 5. sınıf matematik)"
---

`edupedia:carbon-edupedia` skill'inin **yalnız keşif/haritalama** katmanını çalıştır. **Bu komut
modül ÜRETMEZ** — "bu konuya hangi kazanımlar denk geliyor?" sinyaline karşılık verir; bir kazanım
↔ KB becerisi ↔ önerilen etkileşim tablosu döndürür.

**Konu:** $ARGUMENTS

## Yürütme protokolü

1. **Ders slug'ını çöz** (verildiyse): `list_subjects(q=<ders>)` → `subject_registry`
   (`../CONNECTORS.md §2`; slug'ı uydurma).

2. **Kazanımları listele:** `search_learning_outcomes(q=<konu>, subject=<slug>, grade=<sınıf>,
   distinct_codes=true)` → konuya denk gelen kanonik kazanımlar (`outcomes_extract`, tek-sefer).
   Ders/sınıf verilmediyse `subject`/`grade` filtresi olmadan aranır; PDF-türevi metni temizle (§2).

3. **Beceri + etkileşim haritala:** Her kazanımın üst-fiilini çıkar → KB2.x/KB3.x/KB1.x becerisine
   eşle → skill `references/curriculum-integration.md §4` tablosundan **birincil etkileşim desenini**
   ve **destek görselini** öner. Resmî beceri tanımı gerekiyorsa `get_framework("beceriler/kavramsal-beceriler")`
   — bir kez (`framework_map`).

## Çıktı (tablo)

| Kazanım kodu | Kazanım (üst-fiil) | Maarif beceri (KB) | Önerilen etkileşim | Destek görseli |
|---|---|---|---|---|

Kaynak damgasını ekle (`server_info.corpus_version`). Kullanıcı bir kazanımdan modül üretmek isterse
`/edupedia:modul <kod>`'a yönlendir. Hiçbir olgu uydurulmaz; kazanım metni izlenebilir olmalıdır.
