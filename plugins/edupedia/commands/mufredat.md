---
description: Bir ders + sınıf + konudan MEB kazanımlarını keşfeder ve kazanım-izlenebilir etkileşimli öğrenim modülü üretir
argument-hint: "<ders> <sınıf> <konu> (örn. Fen 5 hücre)"
---

`edupedia:carbon-edupedia` skill'ini **CURRICULUM modunda** çağır. Mantığı tekrarlama — bu komut
ders+sınıf+konu girdisini kanonik kazanım keşfine ve `/edupedia:modul` üretim akışına bağlar.

**Hedef:** $ARGUMENTS  *(ders + sınıf + konu)*

## Yürütme protokolü

1. **Niyeti çöz:** $ARGUMENTS'tan ders, sınıf ve konuyu ayır (örn. "Fen 5 hücre" → ders=Fen,
   sınıf=5, konu=hücre).

2. **Ders slug'ını çöz** (`maarif-mufredat`; `../CONNECTORS.md §1-A` + §2 kimlik uyarıları):
   `list_subjects(q=<ders>)` → doğru `slug` (asla isimden uydurma; örn. "Fen" → `fen-bilimleri-dersi`).
   `subject_registry` artefaktına yaz (tek-sefer). Gerekirse `get_subject(slug)` ile geçerli sınıf
   etiketini doğrula (`5.Sınıf` biçimi — nokta sonrası boşluksuz).

3. **Hedef kazanımları keşfet:** `search_learning_outcomes(q=<konu>, subject=<slug>, grade=<sınıf>,
   distinct_codes=true)` → konuya denk gelen kazanım kodlarını seç → kanonik `outcomes_extract`
   artefaktı (tek-sefer). Boş dönerse sorguyu genişlet (eş anlamlı/kısa terim) veya
   `list_learning_outcomes(distinct_codes=true)` ile üniteyi tara; hâlâ yoksa doğru ders/sınıf/konu sor.

4. **`/edupedia:modul` akışının 2–5. adımlarını uygula:** beceri → etkileşim haritalama
   (`framework_map`, skill §4) · **§3 görüntü-dayanak politikası** (Tier-1 varsayılan, Tier-2
   yetenek-probuyla) · modülü üret + `scripts/validate_module.py` 11 kapı (G-CURRICULUM + G-SVG) +
   `meta.sourceCitation` damgası + `/mnt/user-data/outputs/`'a kaydet · HTML ile **aynı ad +
   `.manifest.json`** run-manifest'i yaz (şema `../shared/run-manifest-schema.json`; dosya adı
   sözleşmesi `../shared/canonical-cache-contract.md §1`; `quality_gates` yalnız
   `validate_module.py` çıktısından, uydurma yok — koşulmayan kapı `SKIPPED`). `run_id`
   **NORMATİF KALIP** ile (verbatim, başka biçim KULLANMA): `Edupedia-YYYYMMDD-<ders>-<konu>-v<N>`
   — ör. `Edupedia-20260712-fen5-hucre-v1` (`<ders>`/`<konu>` yalnız küçük harf/rakam/tire, `<N>`
   sürüm tamsayısı; şema kısıtı `run-manifest-schema.json` `properties.run_id.pattern`).
   Manifest'siz `/edupedia:yayinla` çalışamaz.

## Sınırlılık

Tek bir kazanım kodu verildiyse → `/edupedia:modul` (doğrulama+çekme kısayolu). Yalnız keşif
(üretim yok) isteniyorsa → `/edupedia:kazanim-bul`. Ders Türkiye MEB dışıysa (IB/Cambridge) →
kapsam dışı, connector çağrılmaz.

## Yayın teklifi

Modül üretildikten ve kalite kapıları koştuktan sonra kullanıcıya sor:
"Bu modülü edupedia.cureonics.com'da yayınlamamı ister misin?" Onaylarsa
`/edupedia:yayinla <üretilen-html-yolu>` akışını izle. Reddederse dosya yerel kalır —
ısrar etme.
