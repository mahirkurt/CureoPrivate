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
5. **OpenAthens / Millet Kütüphanesi** (Tier 4 — **lisanslı kurumsal BİRİNCİ deneme**; annas'ın
   **ÖNÜNDE**).
   `openathens` (HP, `openathens.cureonics.com/mcp` — **CANLI**). Bağlı değilse Tier 5/6.
   `oa_verify_access` → `oa_resolve` → metin için `oa_fetch_fulltext(doi, ingest=true,
   collection=…, doc_id=…)`, orijinal PDF için `oa_fetch_pdf`. `challenge_required` →
   operatör noVNC + Tier 5/6 (sessiz atlama yok). Batch pacing: `oa_batch_*`.
6. **Wiley** (koşullu OAuth `authenticate`) — Tier 5, OpenAthens kapsamı dışı yayıncılar
   (lisanslı band; OA→Annas omurgasını tersine çevirmez).
7. **Annas Reader** (Tier 6 — **SON ÇARE**; yalnız lisanslı band [OpenAthens + Wiley]
   getiremeyince). Bounded analiz: `article_search`→`read_article`; kitap: `get_document_info`→
   `search_in_document`→`read_document`. Dosya: `download_document(id=DOI|MD5)`. Copyright:
   CC-BY dışı verbatim toplu metin yok.
8. **Unpaywall** (Tier 7 — son legal-OA süpürmesi) — pubmed-epmc `pubmed_fetch_fulltext`.
9. **anamnesis ingest (uzun metin → indeks; münhasır set).** Kısa değilse:
    `ingest_document(collection=evidentia:run:<run_id>, doc_id=evrun:<run_id>:<DOI>, source=…)`
    veya Hub aracına `collection`/`doc_id` geçir (OpenAthens kabul eder). Sonra scoped
    `hybrid_query` / `semantic_search`. Kademe atlanırsa `SKIP-REASON` yaz.

## Copyright disiplini (bağlayıcı)

- **Verbatim toplu reprodüksiyon yok** (lisans CC-BY/CC0 değilse).
- Lisans **belirsiz** ise → açık-erişim muamelesi **yapma**.
- Tek kaynaktan yeniden-ifade ≤2-3 cümle; ötesi → kaynağa yönlendir.

## Boşluk

Hiçbir kademe lisanslı tam metni veremezse: künye + nerede erişilebileceği + denenen kademeler
(OpenAthens dahil). Uydurma DOI/erişim **yok**.
