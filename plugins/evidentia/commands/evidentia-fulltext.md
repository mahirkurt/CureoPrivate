---
description: Copyright-kapılı tam-metin getirme kademesi. Bir referans (DOI/PMID/PMCID/başlık) için EPMC→Paper Search→annas-mcp→Wiley→Unpaywall merdivenini yürütür; her adımda lisans/copyright durumunu doğrular; CC-BY dışı içerikte verbatim toplu reprodüksiyon yapmaz.
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
5. **Annas Reader** (operatör-bağlı Cloud Run; `article_search`/`article_download`, tier 3) —
   **copyright kapısı**: CC-BY dışı verbatim toplu metin **çıkarılMAZ**; künye + bağlam + ≤kısa
   alıntı. ⚠️ İndirme **kullanıcının makinesine** iner → analiz için metin yapıştırılır veya
   (uzunsa) doğrudan anamnesis'e ingest edilir (Adım 8).
6. **Wiley** (koşullu OAuth `authenticate`) — yayıncı tam-metin (tier 4).
7. **Unpaywall** (son çare) — yasal açık-erişim PDF lokasyonu (pubmed-epmc Unpaywall entegrasyonu; yalnız legal-OA, verbatim toplu reprodüksiyon yok).
8. **anamnesis ingest (uzun metin → indeks, ham metin DEĞİL).** Getirilen tam metin **kısa**
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
