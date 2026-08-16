---
description: Bir MEB kazanım kodundan DEHB-dostu, kazanım-izlenebilir, erişilebilir etkileşimli öğrenim modülü üretir
argument-hint: "<kazanım-kodu> (örn. FB.5.3.1.1) [+ opsiyonel öğrenci profili]"
---

`edupedia:carbon-edupedia` skill'ini **CURRICULUM modunda** çağır. Mantığı burada tekrarlama —
skill'in 8 modu, 16 kalite kapısı ve pedagojik davranışı olduğu gibi geçerlidir; bu komut yalnız
kazanım-kodu → modül giriş noktasını kanonikleştirir.

**Hedef kazanım:** $ARGUMENTS

## Yürütme protokolü

0. **KAPI — sınıf + ders kesinleşmeden ÜRETİM BAŞLAMAZ.** Kural ve gerekçesi **tek yerde**:
   skill `references/curriculum-integration.md` **§3 Adım 0** (kullanıcı sözleşmesi,
   2026-07-17). Özet: koddan **ÇIKARMA — DOĞRULA** (otorite `search_learning_outcomes`'un
   `subject`+`grade` alanları); kod yoksa/belirsizse **`AskUserQuestion` ile SOR**.
   > Bu komut kuralı **tekrarlamaz**. Sözleşme metnini burada çoğaltmak, iki kopyanın
   > sapmasına yol açtı (referans "koddan çıkarılabilir" derken komut "çıkarma" diyordu) —
   > ve claude.ai yalnız referansı gördüğü için orada YANLIŞ kural geçerliydi. Tek kaynak.

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

2.5. **ÇERÇEVEYİ ÇİZ — ders kitabını AÇ (ZORUNLU).** Normatif: `curriculum-integration.md`
   **§3 Adım 3**. Özet: `list_textbooks` → sayfayı bul → `get_document_text`; **çerçeveyi o
   metin çizer ve üretimin sınırıdır**. Kitap yoksa/`page_count=0` → programa düş ve
   `frame_source.kind:"program"` yaz.

3. **Görsel — ders kitabının KENDİ figürleri ÖNCELİKLİ.** Normatif: `curriculum-integration.md`
   **§2.1** (+ `../CONNECTORS.md §3`). Özet: `search_figures(query, subject, grade)` →
   `get_figure(..., include_image=true)` ile **göm**; yazar-SVG (Tier-1) **yedektir**;
   düşerse `tier2_status` **raporla** — sessizce atlama.

3.5. **KAPSAM + DOĞRULUK DENETİMİ — canlıya çıkmadan ÖNCE (ZORUNLU).** Normatif:
   `curriculum-integration.md` **§3 Adım 5.5 + §6.1**. Özet: (a) kapsam — çerçeve dışını
   **çıkar**, `scope.excluded[]`'a yaz, `in_frame:false` ise **üretme**; (b) doğruluk +
   tutarlılık — her iddiayı kitap metnine karşı sına. Sonuç `verification` bloğuna:
   `claim` + `grounding` (`document_id` + `page`) + `verdict`. Dayanaksız iddia ya kaynağına
   bağlanır ya çıkarılır.

4. **Üret + doğrula + damgala:** Modülü kur (segmentleri hedef kazanıma göre kurgula),
   `scripts/validate_module.py` ile kalite kapılarını (G-CURRICULUM + G-VERIFY + G-VOICE + G-SVG dahil) geçir,
   `meta.sourceCitation`'ı kazanım kodu + korpus sürümüyle (`server_info.corpus_version`) damgala,
   `/mnt/user-data/outputs/` altına kebab-case adla kaydet.

5. **Manifest'i yaz:** HTML ile **aynı dizine**, aynı ad + `.manifest.json` uzantısıyla
   (örn. `hucre-modul.html` → `hucre-modul.manifest.json`) bir run-manifest yaz — şema
   `../shared/run-manifest-schema.json`, dosya adı sözleşmesi
   `../shared/canonical-cache-contract.md §1`. Kalite kapılarının OTORİTESİ yerel
   `scripts/validate_module.py`'dir. `quality_gates` yazılacaksa `python
   scripts/validate_module.py --json <html>` çıktısının BİREBİR kendisi olmalı —
   elle yazma, konsol raporundan transkribe, hiçbir kapıyı PASS'a yükseltme yok.
   Koşturulmayan kapı `--json` çıktısında kendiliğinden `SKIPPED` gelir (asla `PASS`).
   `connector_call_ledger`/`canonical_artifacts` bu komutun Adım 1'inde yapılan Müfredat MCP
   çağrılarından gelir. `run_id` **NORMATİF KALIP** ile (verbatim, başka biçim KULLANMA):
   `Edupedia-YYYYMMDD-<ders>-<konu>-v<N>` — ör. `Edupedia-20260712-fen5-hucre-v1` (`<ders>`/`<konu>`
   yalnız küçük harf/rakam/tire, `<N>` sürüm tamsayısı; şema kısıtı `run-manifest-schema.json`
   `properties.run_id.pattern`).

## Belirsiz / hatalı kod

Kod belirsiz veya geçersizse `search_learning_outcomes` ile en yakın kanonik kazanımı öner ve
onay iste — uydurma kodla üretme.

## Sınırlılık

Girdi bir kazanım kodu değil, ders+sınıf+konu ise → bu komut yerine `/edupedia:mufredat`; yalnız
"hangi kazanımlar" keşfi isteniyorsa → `/edupedia:kazanim-bul`. Kaynak metin yapıştırıldıysa MCP'siz
doğrudan skill yeterlidir.

## Teslim

Modül yerel tek-dosya HTML'dir. Yayınlama, siteye yükleme veya `edupedia_publish` **yok**.
claude.ai'de HTML'i sohbet artefaktı olarak sun; Claude Code'da dosyaya yaz.
