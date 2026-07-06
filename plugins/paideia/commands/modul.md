---
description: Bir MEB kazanım kodundan DEHB-dostu, kazanım-izlenebilir, erişilebilir etkileşimli öğrenim modülü üretir
argument-hint: "<kazanım-kodu> (örn. FB.5.3.1.1) [+ opsiyonel öğrenci profili]"
---

`paideia:carbon-paideia` skill'ini **CURRICULUM modunda** çağır. Mantığı burada tekrarlama —
skill'in 8 modu, 11 kalite kapısı ve pedagojik davranışı olduğu gibi geçerlidir; bu komut yalnız
kazanım-kodu → modül giriş noktasını kanonikleştirir.

**Hedef kazanım:** $ARGUMENTS

## Yürütme protokolü

1. **Kazanımı doğrula + çek** (`maarif-mufredat` connector'ı; `../CONNECTORS.md` §1-B +
   `../shared/canonical-cache-contract.md` normatif):
   - $ARGUMENTS içindeki kazanım kodunun üst-fiilini ayrıştır → ders/sınıf/ünite (kod anatomisi:
     `FB.5.3.1.1` = Fen·5·Ünite3·Bölüm1·Çıktı1).
   - `list_subjects` ile ders slug'ını çöz (asla uydurma → `subject_registry` artefaktı).
   - `search_learning_outcomes(q=<kod veya konu>, subject=<slug>, grade=<sınıf>, distinct_codes=true)`
     ile kodu **doğrula ve tam metnini** çek → kanonik `outcomes_extract` artefaktı (tek-sefer).
   - PDF-türevi metni temizle (CONNECTORS.md §2: tireli birleştir, içerik-çerçevesi kuyruğunu
     ayrıştır, yarım cümleyi tamamlama).

2. **Beceri → etkileşim haritalama:** Kazanımın üst-fiilini `framework_map` üzerinden KB2.x
   becerisine ve birincil etkileşim desenine eşle (skill `references/curriculum-integration.md §4`).
   Resmî beceri modülde gösterilecekse `get_framework("beceriler/kavramsal-beceriler")` — bir kez.

3. **Görsel — §3 görüntü-dayanak politikası** (`../CONNECTORS.md §3`): **Tier-1 varsayılan**
   (yazar-üretimli tema-duyarlı SVG). **Tier-2** (`get_figure include_image=true` → resmî görsel
   gömme) yalnız yetenek-probuyla; herhangi bir hatada sessizce Tier-1'e düş, `tier2_status` raporla.

4. **Üret + doğrula + damgala:** Modülü kur (segmentleri hedef kazanıma göre kurgula), 
   `scripts/validate_module.py` ile **11 kalite kapısını** (G-CURRICULUM + G-SVG dahil) geçir,
   `meta.sourceCitation`'ı kazanım kodu + korpus sürümüyle (`server_info.corpus_version`) damgala,
   `/mnt/user-data/outputs/` altına kebab-case adla kaydet.

## Belirsiz / hatalı kod

Kod belirsiz veya geçersizse `search_learning_outcomes` ile en yakın kanonik kazanımı öner ve
onay iste — uydurma kodla üretme.

## Sınırlılık

Girdi bir kazanım kodu değil, ders+sınıf+konu ise → bu komut yerine `/paideia:mufredat`; yalnız
"hangi kazanımlar" keşfi isteniyorsa → `/paideia:kazanim-bul`. Kaynak metin yapıştırıldıysa MCP'siz
doğrudan skill yeterlidir.
