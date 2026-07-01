# Risk of Bias Assessment (P5)

**Loaded:** Phase P5 — P4'ün kesinleşmiş `evidence_table`'ını (`data-extraction.md` §5)
ve her çalışmanın **tasarımını** girdi alır; üretir `rob_assessments` (P6 GRADE
"risk of bias" düşürme alanı + P7 raporlama girdisi).

**Authority basis:** RoB 2 (Sterne et al., *BMJ* 2019) · ROBINS-I (Sterne et al., *BMJ*
2016) · QUADAS-2 (Whiting et al., *Ann Intern Med* 2011) · Newcastle-Ottawa Scale
(Wells et al., Ottawa Hospital) · PROBAST (Wolff et al., *Ann Intern Med* 2019) ·
AMSTAR-2 (Shea et al., *BMJ* 2017) · Cochrane Handbook v6.x ch. 8 (RoB assessment).

---

## 1. Araç seçim matrisi — tasarım → araç

Yanlılık riski aracı, çalışmanın **tasarımına** göre belirlenir (`data-extraction.md`
§1 künye bloğundaki `design` alanından okunur) — yanlış araç seçimi geçersiz
değerlendirme üretir, bu yüzden eşleme aşağıdaki tabloya **birebir** sadıktır:

| Çalışma tasarımı | Araç | Alan sayısı |
|---|---|---|
| **RKÇ** (randomize kontrollü çalışma) | **RoB 2** | 5 alan |
| **Randomize-olmayan müdahale** (NRSI/kohort-müdahale) | **ROBINS-I** | 7 alan |
| **Tanısal-doğruluk** | **QUADAS-2** | 4 alan (+ uygulanabilirlik) |
| **Gözlemsel kohort / olgu-kontrol** | **Newcastle-Ottawa Scale (NOS)** | 3 blok (yıldız) |
| **Tahmin modeli** (prognostik/tanısal model geliştirme-doğrulama) | **PROBAST** | 4 alan |
| **Dahil edilen sistematik derlemeler** (derleme-içinde-derleme) | **AMSTAR-2** | 16 madde |

Eşleme kaynakta belirsizse (ör. tek-kollu prospektif seri) en yakın gözlemsel
tasarım aracı seçilir ve gerekçe not edilir; **asla** RKÇ aracı (RoB 2)
randomize-olmayan bir çalışmaya uygulanmaz ve tersi de geçerli değildir.

---

## 2. Araç-başına alan-alan sorular + yargı seviyeleri

**RoB 2 (5 alan)** — her alan ayrı yargılanır: (1) randomizasyon sürecinden kaynaklanan
yanlılık, (2) amaçlanan müdahaleden sapmalar (deviations), (3) eksik sonuç verisi
(missing outcome data), (4) sonuç ölçümü (outcome measurement), (5) raporlanan
sonucun seçimi (selective reporting). Yargı: **low / some concerns / high**;
genel yargı = alanların en kötüsü (tek "high" → genel "high").

**ROBINS-I (7 alan)** — (1) confounding, (2) katılımcı seçimi, (3) müdahale
sınıflaması, (4) amaçlanan müdahaleden sapmalar, (5) eksik veri, (6) sonuç ölçümü,
(7) raporlanan sonucun seçimi. Yargı: **low / moderate / serious / critical /
no information**; genel yargı = en kötü alan.

**QUADAS-2 (4 alan + uygulanabilirlik)** — (1) hasta seçimi, (2) indeks test,
(3) referans standart, (4) akış ve zamanlama; ilk 3 alan ayrıca **uygulanabilirlik
kaygısı** (applicability concern) taşır. Yargı: **low / unclear / high** (hem
yanlılık riski hem uygulanabilirlik ekseni için ayrı ayrı).

**Newcastle-Ottawa Scale (3 blok, yıldız)** — kohort: seçim (4 madde, max 4★) +
karşılaştırılabilirlik (1 madde, max 2★) + sonuç (3 madde, max 3★) = **max 9★**;
olgu-kontrol: seçim (4 madde, max 4★) + karşılaştırılabilirlik (max 2★) + maruziyet
(3 madde, max 3★) = **max 9★**. Genel eşik (yaygın kullanım): ≥7★ düşük risk,
5–6★ orta, ≤4★ yüksek risk — eşik kullanılıyorsa raporda açıkça belirtilir.

**PROBAST (4 alan)** — (1) katılımcılar, (2) prediktörler, (3) sonuç (outcome),
(4) analiz; yanlılık riski **ve** uygulanabilirlik ayrı değerlendirilir. Yargı:
**low / high / unclear** (alan başına); genel = herhangi bir alan "high" ise genel
"high risk of bias".

**AMSTAR-2 (16 madde)** — 7 "kritik" madde (ör. protokol ön-kaydı, kapsamlı arama
stratejisi, dahil-hariç gerekçesi, yanlılık riski değerlendirmesi, sentez yöntemi
uygunluğu, yayın yanlılığı değerlendirmesi, çıkar çatışması beyanı) + 9 "kritik
olmayan" madde. Genel güven: **high / moderate / low / critically low**
(kritik zayıflık sayısına göre — tek kritik zayıflık → en fazla "low").

---

## 3. İnsan-onay kapısı (ZORUNLU)

- Tool, yukarıdaki araca göre **alan-alan taslak yargı** üretir (sinyalleştirme
  sorularına atıf + kaynak künyesi ile); bu taslak **kesin kabul edilmez**.
- Kullanıcı, çalışma × alan bazında sunulan taslak yargıları tek tek onaylamak
  zorundadır — onay öncesi hiçbir satır kesin `rob_assessments`'a yazılmaz
  (`screening.md` §3 ve `data-extraction.md` §4 insan-onay kapısıyla aynı norm).
- Kullanıcı bir alan yargısını reddedip düzeltebilir (`override` — tool'un
  orijinal taslağı ile birlikte saklanır, sessizce üzerine yazılmaz).
- Kaynakta yeterli bilgi yoksa yargı **"no information"/"unclear"** olarak
  işaretlenir — asla iyimser varsayılan (ör. "low risk") ile doldurulmaz.

---

## 4. Özet gösterim

**Trafik-ışığı / ısı-tablosu:** satır = çalışma, sütun = araç-spesifik alan;
hücre rengi/etiketi = yargı seviyesi (yeşil=low, sarı=some concerns/moderate/
unclear, kırmızı=high/serious/critical). Genel yargı sütunu tabloya eklenir.
NOS çalışmaları için hücreler yıldız sayısı olarak da gösterilebilir (renk +
sayısal yıldız birlikte).

**Sidecar — `rob_assessments` şeması (`.data.json`):**

```jsonc
{ "rob_assessments": [
    { "study_id": "author_year_pmid",
      "design": "RCT|NRSI|diagnostic-accuracy|cohort|case-control|prediction-model|SR",
      "tool": "RoB2|ROBINS-I|QUADAS-2|NOS|PROBAST|AMSTAR-2",
      "domains": [
        { "domain_name": "", "judgement": "low|some concerns|high|moderate|serious|critical|no information|unclear",
          "signalling_notes": "", "source_citation": "", "human_approved": false }
      ],
      "nos_stars": { "selection": 0, "comparability": 0, "outcome_exposure": 0, "total": 0 },
      "overall_judgement": "", "overall_rationale": "",
      "human_approved": false }
  ] }
```

**No-fabrication notu:** `human_approved:false` satır P6/P7'ye **taslak** olarak
geçer, kesin sayılmaz; boş/belirsiz alan asla "low risk" varsayımıyla doldurulmaz.

---

## 5. GRADE'e devir

Onaylanmış `rob_assessments`, P6 GRADE derecelendirmesinin (`evidence-grading.md`
§2) **"risk of bias" düşürme alanını** besler: bir sonuç ölçütüne katkıda bulunan
çalışmaların çoğunluğu "high"/"serious"/"critical" yargı taşıyorsa GRADE o sonuç
için bir kademe (ciddi sınırlama) veya iki kademe (çok ciddi sınırlama) düşürülür;
gerekçe GRADE Kanıt Özeti'nde (Summary-of-Findings) açıkça belirtilir. AMSTAR-2
çıktısı (dahil derlemeler için) ayrıca Tier 0 sentezinin (`evidence-grading.md`
§1) güvenilirlik notuna eklenir. Onaylanmış değerlendirmeler bütünüyle P7
raporlamasına (`prisma-reporting.md` RoB özet şekli/tablosu) aktarılır.
