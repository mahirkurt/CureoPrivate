# Data Extraction (P4)

**Loaded:** Phase P4 — P3'ün kesinleşmiş `include` kayıtlarını (`screening.md` §3/§6)
ve `fulltext-retrieval.md` tam-metin merdivenini girdi alır; üretir `evidence_table`
(P6 sentez, P7 raporlama girdisi).

**Authority basis:** PRISMA 2020 item 10 (data items / data collection process) ·
Cochrane Handbook v6.x ch. 5 (data collection) · CHARMS (prediction-model çıkarımı,
uygulanabilirse) · GRADE handbook (per-outcome giriş şeması `evidence-grading.md`'ye).

---

## 1. Çıkarım şablonu — çalışma tipine göre

Her dahil çalışma için tek bir **temel künye bloğu** + tasarıma özgü ek alanlar
doldurulur. Temel blok (her tip için zorunlu): yazar/yıl, PMID, DOI, (varsa) NCT
numarası, tasarım, N (toplam + kol bazlı), popülasyon (yaş/tanı/evre özeti),
müdahale/karşılaştırıcı, birincil+ikincil sonuç ölçütleri, etki büyüklüğü + **%95
GA**, izlem süresi, fon kaynağı/çıkar çatışması beyanı.

| Tasarım | Ek zorunlu alanlar |
|---|---|
| **RKÇ** | randomizasyon yöntemi, körleme, ITT/PP analiz seti, kayıp/izlem-dışı oranı |
| **Kohort** | yön (prospektif/retrospektif), karşılaştırma kolu tanımı, ayarlanan kovaryatlar, izlem-süresi heterojenliği |
| **Olgu-kontrol** | olgu/kontrol tanım kriteri, eşleştirme değişkenleri, maruziyet ölçüm yöntemi |
| **Tanısal-doğruluk** | referans standart, duyarlılık/özgüllük + %95 GA, ROC-AUC, prevalans (verilmişse) |
| **Kesitsel** | örnekleme yöntemi, yanıt oranı, zamanlama (tek kesit tarihi) |

Alan boşsa veya kaynakta yoksa **"VERİ BULUNAMADI"** yazılır — tahmini/enterpole
değer asla üretilmez (bkz. §4).

---

## 2. Tam-metin akışı — retrieve-don't-dump

1. **Cascade** — `fulltext-retrieval.md` §2 (Tier 1–5) ile tam metin edinilir
   (EPMC OA → Paper Search → annas-mcp → Wiley → pubmed-epmc Unpaywall).
2. **Ingest** — edinilen tam metin (veya operatörün sağladığı PDF metni)
   `anamnesis: ingest_document(text=..., doc_id="<PMID|DOI>", source="<Tier adı>",
   title=...)` ile semantik-parçalanıp indekslenir. Bu adım metnin **ham hâlde
   bağlama dökülmesini** engeller — dönen MANIFEST yalnız parça sayısı + önizleme.
3. **Retrieve** — çıkarım alanı başına hedefli sorguyla dilim çekilir:
   `anamnesis: semantic_search(query="<sonuç ölçütü / alan>", doc_id="<PMID|DOI>",
   k=5–8)` tek-belge hassas arama için; çok-yönlü/karma çıkarımlarda
   `anamnesis: hybrid_query(query="<birincil sonuç>", queries=["<alt-yönler>"],
   seed_entities=["<ilaç/gen>"])` daha geniş bağlam + graf genişletmesi için.
4. Her dönen parça `{doc_id, idx, score}` provenance taşır — çıkarılan her sayısal
   değer bu parça kimliğine **iğnelenir** (aşağıdaki sidecar `source_chunk` alanı).
5. Copyright kapısı (`fulltext-retrieval.md` §3) burada da geçerlidir: sayı/olgu
   çıkarımı serbest, geniş **verbatim** blok asla kopyalanmaz.

---

## 3. Sonuç-bazlı toplama

Çıkarım çalışma-satırı bazlı değil **sonuç (outcome) bazlı** gruplanır: aynı
sonuç ölçütünü raporlayan tüm çalışmalar tek bir toplama birimine yazılır, böylece
P6 sentezi doğrudan meta-analiz/anlatı sentezine geçebilir. Toplama öncesi **birim
ve tanım uyumu** zorunlu kontrol: aynı sonuç farklı ölçek/birimle raporlanmışsa
(ör. mmol/L vs mg/dL, farklı yanıt-tanımı eşiği) ham değer dönüştürülmeden yan yana
konmaz — dönüşüm yapılırsa yöntemi ve kaynağı not edilir; dönüştürülemiyorsa
"birim uyumsuz — sentezlenemez" olarak işaretlenir (uydurma harmonizasyon yok).

---

## 4. İnsan-onay + doğrulama (ZORUNLU)

- Her çıkarılan sayısal/kategorik değer, kaynağa (tam-metin parçası veya özet)
  karşı **tek tek doğrulanır** — tool çıktısı nihai kabul edilmez.
- Kullanıcı, parti hâlinde sunulan çıkarım satırlarını (çalışma + alan + değer +
  `source_chunk`) onaylamak zorundadır; onay öncesi hiçbir satır kesin
  `evidence_table`'a yazılmaz (`screening.md` §3 insan-onay kapısıyla aynı norm).
- Kaynakta bulunmayan/belirsiz her alan **"VERİ BULUNAMADI"** — asla enterpolasyon,
  ortalama tahmini veya "muhtemelen" değeri uydurulmaz.
- Kullanıcı bir çıkarımı reddedip düzeltebilir (`override` — orijinal tool çıktısı
  ile birlikte saklanır, sessizce üzerine yazılmaz).

---

## 5. Sidecar — `evidence_table` şeması (`.data.json`)

```jsonc
{ "evidence_table": [
    { "study_id": "author_year_pmid",
      "citation": { "author": "", "year": 0, "pmid": "", "doi": "", "nct": null },
      "design": "RCT|cohort|case-control|diagnostic-accuracy|cross-sectional",
      "n_total": 0, "n_arms": [],
      "population": "",
      "intervention": "", "comparator": "",
      "outcomes": [
        { "outcome_name": "", "effect_measure": "HR|OR|RR|MD|sensitivity|...",
          "effect_size": null, "ci_95": [null, null],
          "unit": "", "source_chunk": { "doc_id": "", "idx": 0, "score": 0.0 },
          "verified": false, "note": "VERİ BULUNAMADI | ..." }
      ],
      "follow_up": "", "funding": "", "coi": "",
      "human_approved": false }
  ] }
```

**No-fabrication notu:** `verified:false` veya boş alan asla varsayılan değerle
doldurulmaz; `human_approved:false` satırı P6/P7'ye **taslak** olarak geçer, kesin
sayılmaz. Onaylanmış satırlar bütünüyle P6 sentezine (`evidence-grading.md` GRADE
girdisi) ve P7 kanıt tablosuna aktarılır.

---

## 6. Sonraki faz

Onaylanmış `evidence_table` satırları GRADE derecelendirmesine (`evidence-grading.md`,
per-outcome sertainty) ve çalışma-bazlı yanlılık riski değerlendirmesine
(`risk-of-bias.md`) devredilir; ikisi birlikte P7 raporlamasına
(`prisma-reporting.md` kanıt tablosu + özet bulgular tablosu) aktarılır.
