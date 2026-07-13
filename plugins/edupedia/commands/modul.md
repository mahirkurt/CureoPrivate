---
description: Bir MEB kazanım kodundan DEHB-dostu, kazanım-izlenebilir, erişilebilir etkileşimli öğrenim modülü üretir
argument-hint: "<kazanım-kodu> (örn. FB.5.3.1.1) [+ opsiyonel öğrenci profili]"
---

`edupedia:carbon-edupedia` skill'ini **CURRICULUM modunda** çağır. Mantığı burada tekrarlama —
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

5. **Manifest'i yaz (yayın için zorunlu ön koşul):** HTML ile **aynı dizine**, aynı ad +
   `.manifest.json` uzantısıyla (örn. `hucre-modul.html` → `hucre-modul.manifest.json`) bir
   run-manifest yaz — şema `../shared/run-manifest-schema.json`, dosya adı sözleşmesi
   `../shared/canonical-cache-contract.md §1`. **`quality_gates` alanı
   `python scripts/validate_module.py --json <html>` çıktısının BİREBİR kendisidir** — bu
   komutu çalıştır, JSON'unu manifeste olduğu gibi yerleştir; kapı sonuçlarını elle yazma,
   konsol raporundan transkribe etme, hiçbir kapıyı PASS'a yükseltme. Koşturulmayan/uygulanamayan
   kapı `--json` çıktısında kendiliğinden `SKIPPED` gelir (asla `PASS`).
   `connector_call_ledger`/`canonical_artifacts` bu komutun Adım 1'inde yapılan Müfredat MCP
   çağrılarından gelir. `run_id` **NORMATİF KALIP** ile (verbatim, başka biçim KULLANMA):
   `Edupedia-YYYYMMDD-<ders>-<konu>-v<N>` — ör. `Edupedia-20260712-fen5-hucre-v1` (`<ders>`/`<konu>`
   yalnız küçük harf/rakam/tire, `<N>` sürüm tamsayısı; şema kısıtı `run-manifest-schema.json`
   `properties.run_id.pattern`). Bu manifest olmadan `/edupedia:yayinla` çalışamaz.

## Belirsiz / hatalı kod

Kod belirsiz veya geçersizse `search_learning_outcomes` ile en yakın kanonik kazanımı öner ve
onay iste — uydurma kodla üretme.

## Sınırlılık

Girdi bir kazanım kodu değil, ders+sınıf+konu ise → bu komut yerine `/edupedia:mufredat`; yalnız
"hangi kazanımlar" keşfi isteniyorsa → `/edupedia:kazanim-bul`. Kaynak metin yapıştırıldıysa MCP'siz
doğrudan skill yeterlidir.

## Yayın teklifi

Modül üretildikten ve kalite kapıları koştuktan sonra kullanıcıya sor:
"Bu modülü edupedia.cureonics.com'da yayınlamamı ister misin?" Onaylarsa
`/edupedia:yayinla <üretilen-html-yolu>` akışını izle. Reddederse dosya yerel kalır —
ısrar etme.
