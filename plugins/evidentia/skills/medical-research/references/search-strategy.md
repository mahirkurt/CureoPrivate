# Search Strategy (P1)

**Loaded:** Phase P1 — consumes P0 `protocol` (`prisma-protocol.md` §5), produces the
per-database search strategy P2 retrieval executes. Feeds P3 (`screening.md`, dedupe/
flow counts) and P7 (`prisma-reporting.md` item 7 — reproducible search string).

**Authority basis:** PRISMA 2020 item 7 · Cochrane Handbook ch. 4 (search methods) ·
PubMed Clinical Queries filters · Cochrane HSSS · PRISMA-S extension.

---

## 1. Kavram→kontrollü sözcük eşleme

Her P0 PICO/PECO/PCC bileşeni (population, intervention_or_exposure, comparator,
outcome_primary) bağımsız bir arama kavramı olur, üç katmanda doldurulur:

| Katman | Kaynak | Kural |
|---|---|---|
| MeSH (PubMed) | `pubmed-epmc:pubmed_lookup_mesh` | Descriptor'a çöz; explode varsayılan |
| Emtree (Embase) | — | **Native API yok** → dürüst boşluk (§6); yalnız serbest-metin katmanı Embase-tarzı simüle eder |
| Serbest-metin | Türetim | Eşanlamlı + yazım varyantı (`tumour`/`tumor`) + kısaltma (`RA`↔`rheumatoid arthritis`) |

Wildcard: PubMed `[tiab]`'de `*` (`therap*`, ≥4 karakter kök). Europe PMC/OpenAlex
serbest-metin `*` desteklemez → eşanlamlı listesi genişletilerek telafi edilir.

---

## 2. Boole yapısı

- **Kavram-içi:** eşanlamlı + MeSH + serbest-metin **OR**.
- **Kavramlar-arası:** Population **AND** Intervention/Exposure **AND** (varsa)
  Comparator **AND** Outcome; PCC'de Comparator/Outcome zorlanmaz (`prisma-protocol.md` §2).
- **Alan etiketleri (PubMed):** `[tiab]` (serbest-metin), `[mesh]` (explode),
  `[mh:noexp]` (explode kapalı), `[majr]` (major topic, yüksek-özgüllük).
  Formül: `("term"[tiab] OR "syn"[tiab] OR "MeSH"[mesh]) AND (...)`.
- **Eşdeğerleri:** Europe PMC `TITLE_ABS:`/`MESH:`; OpenAlex `filter=` (alan
  etiketi yok, tür/tarih daraltma); CT.gov `query.cond`/`query.intr` (örtük AND).

---

## 3. Veritabanı-başına sorgu çevirisi

| Veritabanı | Araç (Sunucu:arac) | DSL notu |
|---|---|---|
| PubMed | `pubmed-epmc:pubmed_search_articles` (birincil) / `PubMed:search_articles` | Tam Boole + `[tiab]`/`[mesh]`; `date_from`/`date_to` = protokol `year` |
| Europe PMC | `pubmed-epmc:pubmed_europepmc_search` | PubMed sıfır-sonuçta genişletme (preprint+PMC-only OA); `TITLE_ABS:`/`MESH:` |
| ClinicalTrials | `Clinical Trials:search_trials` | `query.cond`/`query.intr`/`query.spons`; kayıt/gri-literatür kapsamı (§4) |
| OpenAlex | `openalex:openalex_search_entities` | Önce `openalex_resolve_name`; `filter=type,publication_year,has_fulltext` |
| Semantic Scholar | `semantic-scholar:search_papers` | Doğal-dil, alan etiketi yok; **ikincil** teyit (Consensus zaten S2 sentezliyor) |
| Consensus | `Consensus:search` | Doğal-dil; filtre yalnız kullanıcı isterse; azami 3 çağrı/parti |
| bioRxiv/medRxiv | `bioRxiv:search_preprints` | Tarih+kategori (anahtar-kelime yok); ⚠️ hakemsiz bayrağı zorunlu |
| Paper Search | `Paper Search:search` / `search_pubmed` / `search_semantic` / `search_biorxiv` | Çoklu-kaynak fan-out + tam-metin okuma (full-text cascade tier 2) |
| YÖK Tez | `YokTez MCP:search_yok_tez_detailed` | Türkçe **ve** İngilizce ayrı denenir; `search_yok_tez_by_anabilim_dali` ile daraltma |

Tam parametre doğrulaması: `connector-registry.md` §2.1 — burada yalnız arama-DSL notu.

---

## 4. Duyarlılık/özgüllük filtreleri

| Filtre | Uygulama |
|---|---|
| RCT — yüksek duyarlılık | `("randomized controlled trial"[pt] OR "randomized"[tiab] OR "placebo"[tiab] OR "randomly"[tiab])` (Cochrane HSSS'e yakın) |
| RCT — yüksek özgüllük | `"randomized controlled trial"[pt]` tek başına (PubMed Clinical Queries eşdeğeri) |
| SR/meta-analiz | `("systematic review"[pt] OR "meta-analysis"[pt] OR "systematic review"[tiab])` — Tier 0 (`evidence-grading.md` §1) |
| Diğer connector eşdeğeri | Europe PMC `PUB_TYPE:"Randomized Controlled Trial"`; OpenAlex özel study-design filtresi yok → dürüst boşluk |
| Gri-literatür + kayıt | CT.gov taraması zorunlu (tamamlanmamış/yayınlanmamış sonuç); kongre özeti/tez gerekçeliyse YÖK Tez |

Filtre seçimi review tipine bağlıdır (`prisma-protocol.md` §4): scoping tasarım
filtresi **uygulamaz** (JBI ilkesi).

---

## 5. Raporlanabilir arama dizesi

PRISMA madde 7: her veritabanı için birebir sorgu + çalıştırma tarihi + ham sonuç
sayısı `.data.json` `search_strategy` alanına yazılır (`output-templates.md` §4):

```jsonc
{ "search_strategy": {
    "concepts": { "population": {"mesh": ["…"], "free_text": ["…"]}, "intervention_or_exposure": {"…":"…"} },
    "databases": [ { "name": "PubMed", "tool": "pubmed-epmc:pubmed_search_articles",
        "query_string": "(\"…\"[tiab] OR \"…\"[mesh]) AND (…)",
        "filters_applied": ["date_from:YYYY-MM-DD", "RCT high-sensitivity"],
        "run_date": "YYYY-MM-DD", "result_count": 0 } ],
    "gaps": ["Embase: no native API — Emtree layer not applied"] } }
```

Üçüncü bir taraf aynı sorguyu aynı veritabanında çalıştırıp benzer `result_count`
üretebilmeli (küçük sapma canlı-indeks güncellemesinden gelir, P7'de not edilir).

---

## 6. Sınır dürüstlüğü

- **Cochrane (CENTRAL):** native bağlayıcı yok → `search_strategy.gaps`'e "taranmadı"
  yazılır; PubMed sonucundan asla türetilmez.
- **Embase:** native API yok → Emtree katmanı boş (§1); serbest-metin katmanı yalnız
  benzetim — Embase kapsamının (Avrupa ilaç literatürü ağırlığı) yerine geçmez. P7
  akış diyagramında "veritabanı taranmadı" görünür, asla sıfır-sonuç gizlenmez.
- **Akış-sayısı sınırı:** connector toplam-sayı döndürmüyorsa `result_count: null` +
  P7'ye "toplam bilinmiyor, yalnız getirilen N kayıt" caveat'ı (`prisma-reporting.md`
  akış diyagramı kutu 1).
- Boşluk asla tahmini sayı/"yaklaşık" ile doldurulmaz — `null` + açık not yeterlidir.

---

## 7. Sonraki faz

`search_strategy` artefaktı P2 retrieval'ce çalıştırılır (`databases[]` satırı →
connector çağrısı 1:1); dedupe edilmiş sonuç P3 taramasına (`screening.md`) devredilir.
`gaps` listesi P7'ye (`prisma-reporting.md`) doğrudan taşınır.
