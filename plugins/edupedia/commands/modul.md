---
description: Bir MEB kazanım kodundan DEHB-dostu, kazanım-izlenebilir, erişilebilir etkileşimli öğrenim modülü üretir
argument-hint: "<kazanım-kodu> (örn. FB.5.3.1.1) [+ opsiyonel öğrenci profili]"
---

`edupedia:carbon-edupedia` skill'ini **CURRICULUM modunda** çağır. Mantığı burada tekrarlama —
skill'in 8 modu, 14 kalite kapısı ve pedagojik davranışı olduğu gibi geçerlidir; bu komut yalnız
kazanım-kodu → modül giriş noktasını kanonikleştirir.

**Hedef kazanım:** $ARGUMENTS

## Yürütme protokolü

0. **KAPI — sınıf + ders kesinleşmeden ÜRETİM BAŞLAMAZ.** (Kullanıcı sözleşmesi, 2026-07-17.)
   Sınıf ve ders, modülün derinliğini ve kapsamını belirleyen şeydir; tahminle üretilen modül
   yanlış sınıfa hitap eder ve bu, sessiz bir hatadır.
   - **Kod verildiyse:** koddan sınıf/ders **çıkarma — DOĞRULA.** `FB.5.3.1.1` → "Fen·5" bir
     string tahminidir; otorite `search_learning_outcomes`'un döndürdüğü kaydın `subject` +
     `grade` alanlarıdır. Kod çözülmezse **uydurma**: kullanıcıya bildir ve sor.
   - **Kod YOKSA** (örn. "hücre hakkında modül") veya çözülen ders/sınıf belirsizse:
     **`AskUserQuestion` ile SOR** — sınıf ve ders. Varsayma, "muhtemelen 5. sınıftır" deme.
   - Doğrulanan ders+sınıf, `verification.frame_source` ve `curriculum` bloklarına yazılır.

1. **Kazanımı doğrula + çek** (`maarif-mufredat` connector'ı; `../CONNECTORS.md` §1-B +
   `../shared/canonical-cache-contract.md` normatif):
   - Kodun üst-fiilini ayrıştır; ders/sınıf Adım 0'da MCP'den **doğrulanmış** olarak gelir.
   - `list_subjects` ile ders slug'ını çöz (asla uydurma → `subject_registry` artefaktı).
   - `search_learning_outcomes(q=<kod veya konu>, subject=<slug>, grade=<sınıf>, distinct_codes=true)`
     ile kodu **doğrula ve tam metnini** çek → kanonik `outcomes_extract` artefaktı (tek-sefer).
   - PDF-türevi metni temizle (CONNECTORS.md §2: tireli birleştir, içerik-çerçevesi kuyruğunu
     ayrıştır, yarım cümleyi tamamlama).

2. **Beceri → etkileşim haritalama:** Kazanımın üst-fiilini `framework_map` üzerinden KB2.x
   becerisine ve birincil etkileşim desenine eşle (skill `references/curriculum-integration.md §4`).
   Resmî beceri modülde gösterilecekse `get_framework("beceriler/kavramsal-beceriler")` — bir kez.

2.5. **ÇERÇEVEYİ ÇİZ — ders kitabını AÇ (ZORUNLU).** `references/curriculum-integration.md` Adım 3.
   **"Ders kitapları metin döndürmez" eski iddiası YANLIŞTI** — ölçüldü: 105 kitabın 103'ü tam
   metin indeksli. `list_textbooks(subject, grade)` → `search_figures`/`search` ile konunun
   sayfasını bul → `get_document_text(document_id, page_range=…)`. **Modülün çerçevesini bu metin
   çizer**: hangi kavramlar, hangi derinlikte, hangi örneklerle. Kitap yoksa/`page_count=0` ise
   öğretim programına düş ve `verification.frame_source.kind:"program"` yaz — asla "kitaba
   dayandım" deme.

3. **Görsel — ders kitabının KENDİ figürleri ÖNCELİKLİ** (`../CONNECTORS.md §3`).
   `search_figures(query=<konu>, subject=<slug>, grade=<sınıf>)` → 22.414 figür ders+sınıf
   filtreli, her biri caption + `page_no` taşır (sayfa bulucu olarak da kullanılır).
   `get_figure(figure_id, include_image=true)` ile resmî görseli **modüle göm** — öğrencinin
   kitabındaki görselle aynı olması öğrenme transferini güçlendirir.
   **Tier-1 (yazar-üretimli tema-duyarlı SVG) artık yedektir:** uygun resmî figür yoksa veya
   `get_figure` hata verirse ona düş ve `tier2_status` raporla — sessizce atlama.

3.5. **KAPSAM + DOĞRULUK DENETİMİ — canlıya çıkmadan ÖNCE (ZORUNLU).**
   `references/curriculum-integration.md §6.1`. Kullanıcı sözleşmesi: içerik denetlenmeden
   yayınlanmaz. **Denetimi sen (model) yaparsın — ama dayanakla, sezgiyle değil.** İki eksen:
   - **(a) Kapsam:** üretilen her şey Adım 2.5'te açtığın çerçevenin İÇİNDE mi? Çerçeve dışı
     kalan her şeyi **çıkar** ve `verification.scope.excluded[]`'a yaz. Doğru olması yetmez —
     o sınıfın çerçevesinde yoksa yeri yok.
   - **(b) Doğruluk + tutarlılık:** her olgusal iddiayı ders kitabı metnine karşı sına; modül
     kendi içinde çelişmesin (bir segmentte söylediğin şeyi başka segmentte bozma).
   Sonucu `verification` bloğuna yaz: her iddia için `claim` + `grounding` (document_id + page)
   + `verdict`. **Dayanağını gösteremediğin iddiayı ya kaynağına bağla ya modülden çıkar** —
   `verdict:"general_knowledge"` bir kaçış deliği değil, bir borçtur (kapı WARN verir; çoğunluk
   öyleyse FAIL). `scope.in_frame:false` ise **üretme**.

4. **Üret + doğrula + damgala:** Modülü kur (segmentleri hedef kazanıma göre kurgula),
   `scripts/validate_module.py` ile kalite kapılarını (G-CURRICULUM + G-VERIFY + G-SVG dahil) geçir,
   `meta.sourceCitation`'ı kazanım kodu + korpus sürümüyle (`server_info.corpus_version`) damgala,
   `/mnt/user-data/outputs/` altına kebab-case adla kaydet.

5. **Manifest'i yaz (yayın için zorunlu ön koşul):** HTML ile **aynı dizine**, aynı ad +
   `.manifest.json` uzantısıyla (örn. `hucre-modul.html` → `hucre-modul.manifest.json`) bir
   run-manifest yaz — şema `../shared/run-manifest-schema.json`, dosya adı sözleşmesi
   `../shared/canonical-cache-contract.md §1`. **`python scripts/validate_module.py --json
   <html>` çıktısını manifeste yazmak İSTEĞE BAĞLI bir yerel ön-kontroldür.** Kalite
   kapılarının OTORİTESİ yayın sunucusudur: yayın sırasında sunucu HTML'i kendisi ölçer ve
   istemcinin `quality_gates` beyanını yok sayar; kapı düşerse yayın 422 ile reddedilir
   (bkz. `../commands/yayinla.md`). Manifeste yine de yazılıyorsa kapı sonuçlarını elle
   yazma, konsol raporundan transkribe etme, hiçbir kapıyı PASS'a yükseltme —
   koşturulmayan/uygulanamayan kapı `--json` çıktısında kendiliğinden `SKIPPED` gelir
   (asla `PASS`). `connector_call_ledger`/`canonical_artifacts` bu komutun Adım 1'inde yapılan Müfredat MCP
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

**claude.ai'de:** modülü dosyaya yazmak yerine, HTML'i doğrudan `edupedia_publish`
aracının `html` argümanına üret. Böylece modül tek seferde üretilir ve yayınlanır;
ikinci kez emit edilmesi gerekmez. Kullanıcı modülü siteden indirebilir.
**Claude Code'da:** mevcut akış korunur (dosyaya yaz, sonra `/edupedia:yayinla`).
