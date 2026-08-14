---
description: Copyright-kapılı tam-metin getirme kademesi. Bir referans (DOI/PMID/PMCID/başlık) için EPMC→Paper Search→OpenAthens→Wiley→Anna's Reader→Unpaywall merdivenini yürütür; metin veya orijinal PDF/EPUB teslim yolunu seçer, lisans/copyright durumunu doğrular ve CC-BY dışı içerikte verbatim toplu reprodüksiyon yapmaz.
argument-hint: <DOI / PMID / PMCID / makale başlığı>
---

# /evidentia-fulltext — Tam-Metin Kademe (P4, Copyright-Kapılı)

Hedef referans: **$ARGUMENTS**

`medical-research` **P4 çıkarım** fazının tam-metin kademesi: `references/fulltext-retrieval.md`
merdivenini yürüt; getirilen tam metin `references/data-extraction.md` çıkarımını (kanıt tablosu)
besler. **Copyright kapısı her adımda bağlayıcıdır** (G-COPYRIGHT).

## Kademe

1. **Kimlik çöz.** DOI↔PMID↔PMCID dönüşümü (EPMC `convert_article_ids`). PMCID varsa açık-erişim
   olasılığı yüksek.
2. **Lisans kontrolü (önce).** EPMC `get_copyright_status` → **CC-BY/CC0** ise tam metin
   getirilebilir; aksi halde **yalnız** künye + özet + bölüm-başlıkları + kısa alıntı.
3. **EPMC tam metin.** `get_full_text_article` (PMC açık-erişim) — lisans elverdiğince.
4. **Paper Search.** `read_pubmed_paper` / `download_*` (tier 2).
5. **OpenAthens / Millet Kütüphanesi** (Tier 3 — **lisanslı kurumsal, legal-öncelikli; annas'ın
   ÖNÜNDE**). `openathens` connector (HP self-host, `openathens.cureonics.com/mcp` — **CANLI**;
   bağlı değilse bu adımı atla, Tier 4/5'e düş). `oa_resolve(doi/pmid/title)` → kapsayan DB +
   OpenAthens redirector; metin/arama/RAG için `oa_fetch_fulltext(doi, ingest=true)`, orijinal
   sağlayıcı PDF'i gerektiğinde provider-nötr `oa_fetch_pdf(doi|url)` kullan. PDF aracı
   kısa-ömürlü opaque `resource_link` + filename/MIME/size/SHA-256/acquired_via döndürür;
   linki derhal tüket, kalıcı URL diye saklama. `oa_fetch_fulltext` copyright-gated teslimdir (uzun metin
   **HP'de** iner → anamnesis manifest; verbatim bağlama dökülmez; hangi DB'nin verdiği raporlanır).
   **Kapsam gerçeği (anti-bot v2, 2026-07-13):** getirme, Xvfb altında **headed** kalıcı-profilli
   Chromium ile sürer (gerçek tarayıcı parmak-izi + `cf_clearance` profilde saklı). Anti-bot duvarı
   OLMAYAN yayıncılar (Springer, Nature) doğrudan; Cloudflare/JS anti-bot'lu yayıncılar (Wiley,
   Elsevier, OUP, Sage, T&F) → **non-interactive** managed challenge kendiliğinden temizlenene kadar
   beklenir (çoğu artık **tam metin verir**). Yalnız **interactive** challenge (reCAPTCHA/Turnstile)
   çözülemezse → yeni `challenge_required` zarfı (host + operatör noVNC ipucu; `manual_required`'dan
   AYRI, **gövdesiz** — uydurma yok): operatör HP'de `deploy/oa-vnc.sh up` ile challenge'ı çözer,
   `cf_clearance` profilde kalır → sonraki getirmeler insan müdahalesiz geçer. Sentez akışında
   `challenge_required` → kullanıcıya "operatör noVNC gerekiyor" bildir + Tier 4/5'e degrade et (asla
   sessiz atlama). Oturum sıcaklığı/bekleyen-challenge için `oa_session_status` (`validated` /
   `session_age_s` / `pending_challenge`). Referans-listesi için `oa_batch_submit`/`oa_batch_result`
   (**savunmacı pacing:** sıralı, 20–60 s jitter, per-run 25 / günlük 100 cap — kurum hesabını koru).
   Başarısız → `manual_required` (redirector deep-link + echoed identifier); uydurma yok.
6. **Wiley** (koşullu OAuth `authenticate`) — Tier 4, OpenAthens'in kapsamadığı yayıncılar için
   (lisanslı band'ın parçası).
7. **Annas Reader** (Tier 5 — **SON ÇARE**; yalnız lisanslı band [OpenAthens + Wiley] getiremeyince).
   Bounded analiz için `article_search`→`read_article` (DOI),
   `book_search`→`get_document_info`→`search_in_document`→`read_document` (kitabı ASLA
   bütün çekme). Orijinal PDF/EPUB veya diğer desteklenen dosya gerektiğinde
   `download_document(id=<DOI|32-hex MD5>)`; dönen opaque `resource_link` kısa ömürlüdür,
   derhal tüketilir ve DOI/MD5 + format + SHA-256 kaydedilir. ⚠️ Eski
   `article_download`/`book_download` adları YOKTUR. **Copyright kapısı**: CC-BY dışı
   verbatim toplu metin **çıkarılMAZ**; künye + bağlam + ≤kısa alıntı. Uzun dosya
   anamnesis'e ingest edilir (Adım 9).
8. **Unpaywall** (Tier 6 — son legal-OA süpürmesi) — yasal açık-erişim PDF lokasyonu (pubmed-epmc
   Unpaywall entegrasyonu; yalnız legal-OA, verbatim toplu reprodüksiyon yok).
9. **anamnesis ingest (uzun metin → indeks, ham metin DEĞİL).** Getirilen tam metin **kısa**
   değilse (≳1-2 sayfa) bağlama dökme: anamnesis `ingest_document(text=…, doc_id=<DOI>,
   source=…)` → **manifest** döner. Sonra `semantic_search` / **`hybrid_query`** ile sorguya
   sınırlı, provenance-damgalı (`doc_id::idx`) dilim çek. Bir `doc_id` **bir kez** ingest edilir
   (`evidence_index` kanonik artefaktı, `../shared/canonical-cache-contract.md`). Bu adım
   context-window taşmasını önler; anamnesis deploy edilmemişse (BUILD-BRIEF) bu adım atlanır ve
   metin **özetlenerek** (verbatim değil) işlenir.

## Copyright disiplini (bağlayıcı)

- **Verbatim toplu reprodüksiyon yok** (lisans CC-BY/CC0 değilse). Çıktı: künye, DOI, özet
  (yeniden ifade), bölüm-başlıkları, gerekçeli **kısa** alıntı.
- Lisans **belirsiz** ise → açık-erişim muamelesi **yapma**; künye + "tam metin lisans-kapalı,
  şu kaynaktan erişilebilir" yönlendirmesi.
- Tek kaynaktan yeniden-ifade ≤2-3 cümle; ötesi → kaynağa yönlendir.

## Boşluk

Hiçbir kademe lisanslı tam metni veremezse: künye + nerede erişilebileceği (kurumsal erişim/
yayıncı) + denenen kademeler. Uydurma DOI/erişim **yok**.
