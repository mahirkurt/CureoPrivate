# PRISMA Protocol (P0)

**Loaded:** Phase P0 (Protocol) — the entry phase of the P0→P7 systematic/scoping literature-review
pipeline. Output feeds P1 (`search-strategy.md`), P3 (`screening.md`), and P7 (`prisma-reporting.md`).

**Authority basis:** PRISMA 2020 (Page et al., *BMJ* 2021) · PRISMA-ScR (Tricco et al., *Ann Intern
Med* 2018) · Cochrane Handbook v6.x (question formulation, ch. 2–3) · PRISMA-P (protocol
pre-specification, Moher et al. 2015) · JBI Scoping Review Methodology.

---

## 1. Soru-tipi sınıflaması

Her araştırma sorusu, ilk adımda aşağıdaki altı tipten birine sınıflanır. Tip seçimi, hem uygun
çalışma tasarımı hiyerarşisini hem de PICO değişkenlerinin hangi eksende dolduracağını belirler.

| Soru tipi | Odak | Uygun tasarım hiyerarşisi (yüksek→düşük) |
|---|---|---|
| **Tedavi (therapy)** | Girişimin etkinliği/güvenliği | Sistematik derleme+meta-analiz → RKÇ → kontrollü olmayan deneysel → kohort |
| **Tanı (diagnostic accuracy)** | Testin doğruluğu | SR of accuracy studies → cross-sectional accuracy (index test vs. referans standart) → vaka-kontrol |
| **Prognoz** | Hastalık seyri/risk tahmini | SR of prognostic studies → prospektif kohort → retrospektif kohort |
| **Etiyoloji / zarar** | Neden-sonuç, yan etki | SR/meta-analiz → kohort → vaka-kontrol → kesitsel (RKÇ nadiren etik/uygun) |
| **Önleme** | Girişimin insidansı azaltması | RKÇ (community/individual) → kohort → kesitsel |
| **Kapsam (scoping)** | Alanın haritalanması, kavram netleştirme | Tasarım hiyerarşisi **uygulanmaz** — tüm kanıt tipleri (dahil gri literatür) kapsam dahilinde olabilir |

Sınıflama tekildir ama soru birden çok tipi kapsıyorsa (ör. "tedavi + prognoz alt grubu") baskın
tipi birincil al, ikincili alt-soru olarak not et. Yanlış tip seçimi P1 arama stratejisini ve P5
risk-of-bias aracı seçimini (RoB 2 vs. QUADAS-2 vs. QUIPS vs. ROBINS-I) doğrudan bozar.

---

## 2. PICO/PECO/PICOTS şablonu

Soru tipine göre çerçeve seçilir; alanlar **birincil ve ikincil çıktıyı** ayrı ayrı doldurur.

- **PICO** (tedavi/önleme): Population, **I**ntervention, Comparator, Outcome.
- **PECO** (etiyoloji/zarar — girişim yoksa): Population, **E**xposure, Comparator, Outcome.
- **PICOTS**: PICO/PECO + **T**imeframe (izlem süresi/veri aralığı) + **S**etting (bakım basamağı,
  ülke/sağlık sistemi bağlamı).
- **PCC** (kapsam derlemeleri, PRISMA-ScR): **P**opulation, **C**oncept, **C**ontext — Comparator ve
  Outcome zorunlu değildir; kapsam sorusu "ne var" sorusudur, "ne kadar etkili" değil.

Zorunlu alt-alanlar:
- **Outcome (primary)** — tek, önceden-belirtilmiş birincil sonlanım; GRADE Kanıt Özeti bu sonlanım
  etrafında kurulur (bkz. `evidence-grading.md` §2).
- **Outcome (secondary)** — sınırlı sayıda (aşırı-sonlanım sürüklenmesini önlemek için).
- **Timeframe** — hem izlem süresi (klinik anlamlılık için minimum eşik) hem de yayın tarihi aralığı.
- **Setting** — birinci/ikinci/üçüncü basamak, ülke/bölge kısıtı varsa gerekçesiyle.

---

## 3. Uygunluk kriterleri (eligibility)

Dahil/hariç matrisi, en az şu beş eksende **önceden belirtilir** (pre-specification) — tarama
(P3) başladıktan sonra kriter değişikliği yalnız gerekçeli protokol sapması olarak kaydedilir,
sonuç odaklı post-hoc daraltma yasaktır.

| Eksen | Dahil örneği | Hariç örneği |
|---|---|---|
| **Tasarım** | §1 hiyerarşisinde belirlenen minimum tasarım seviyesi ve üstü | Vaka sunumu (aksi belirtilmedikçe), yorum/editöryal |
| **Popülasyon** | PICO/PECO/PCC'de tanımlı yaş/tanı/evre kriterleri | Örtüşmeyen tanı, yanlış yaş grubu |
| **Dil** | Tam-metin erişimi olan diller (çeviri kapasitesine göre genişletilebilir) | Çeviri imkânı olmayan dil + özet yetersizliği |
| **Yıl** | Belirlenen tarih aralığı (klinik pratikteki kırılma noktası gerekçeli) | Aralık dışı, güncelliğini yitirmiş kılavuz-öncesi dönem |
| **Yayın tipi** | Hakemli makale, tez (gerekçeliyse), kayıtlı ön-baskı (etiketli) | Konferans özeti (tek başına), basın bülteni |

Kapsam derlemelerinde (scoping) tasarım ekseni gevşetilir — JBI metodolojisi gri literatürü ve
tasarım-tipinden bağımsız dahil etmeyi teşvik eder; bu durumda hariç tutma yalnız Popülasyon/
Concept/Context uyumsuzluğuna dayanır.

---

## 4. Derleme tipi seçimi

| Tip | Ne zaman | Ayırt edici özellik |
|---|---|---|
| **Sistematik derleme** | Odaklanmış PICO/PECO sorusu, etkinlik/etki büyüklüğü sorusu | Tam PRISMA 2020 akışı; RoB değerlendirmesi zorunlu; genelde meta-analiz hedefler |
| **Kapsam derlemesi (scoping, PRISMA-ScR)** | Alan az çalışılmış, kavram/terminoloji net değil, kanıt tipi heterojen, "ne tür kanıt var" sorusu | PCC çerçevesi; RoB değerlendirmesi genelde **atlanır**; sonuç niceliksel değil haritalama/sentezdir |
| **Hızlı derleme (rapid)** | Zaman kısıtı (politika/kılavuz acili), kaynak kısıtı | Sistematik derlemenin daraltılmış versiyonu — tek gözden geçiren tarama, sınırlı veritabanı, kısıtlar **açıkça raporlanır** (PRISMA'nın rapid-review uzantısı önerisi) |

Seçim, soru tipinden (§1) ve mevcut kaynak/zaman kısıtından türetilir; seçilen tip P7 raporlama
şablonunu (`prisma-reporting.md`) belirler — sistematik/hızlı PRISMA 2020 akış diyagramı kullanır,
kapsam PRISMA-ScR akış diyagramı ve terimlerini kullanır.

---

## 5. Protokol çıktısı

P0'ın çıktısı, insan onayına sunulan okunabilir protokol metninin yanı sıra makine-okur bir
`protocol` bloğudur. Bu blok `.data.json` sidecar'ının `eligibility_criteria` alanını besler
(bkz. `output-templates.md` §4) ve P1/P3/P7'nin girdisidir.

```jsonc
{
  "protocol": {
    "question_type": "therapy | diagnosis | prognosis | etiology | prevention | scoping",
    "framework": "PICO | PECO | PICOTS | PCC",
    "population": "…",
    "intervention_or_exposure": "…",
    "comparator": "…",
    "outcome_primary": "…",
    "outcome_secondary": ["…"],
    "timeframe": "…",
    "setting": "…",
    "concept": "…",          // yalnız PCC (scoping) doldurulur
    "context": "…",          // yalnız PCC (scoping) doldurulur
    "eligibility_criteria": {
      "design":       { "include": ["…"], "exclude": ["…"] },
      "population":   { "include": ["…"], "exclude": ["…"] },
      "language":     { "include": ["…"], "exclude": ["…"] },
      "year":         { "include": "YYYY-YYYY", "exclude": "…" },
      "publication_type": { "include": ["…"], "exclude": ["…"] }
    },
    "review_type": "systematic | scoping | rapid",
    "pre_specified": true
  }
}
```

**No-fabrication notu:** protokol alanları yalnız kullanıcı sorusundan ve netleştirme
diyaloğundan türetilir; hiçbir alan varsayım veya eğitim-verisi bilgisiyle doldurulmaz. Eksik/
belirsiz bir alan `null` bırakılır ve P4/P7'ye "protocol gap" olarak taşınır — asla tahmini bir
değerle doldurulmaz.

---

## 6. Sonraki faz

Protokol onaylandıktan sonra devir **P1 arama stratejisine** (`search-strategy.md`) yapılır: PICO/
PECO/PCC alanları veritabanı-başına MeSH/Emtree/anahtar-kelime dizelerine çevrilir, `eligibility_criteria`
ise arama filtrelerine (dil/yıl/yayın tipi) ve sonrasında P3 tarama kriterlerine doğrudan
aktarılır.
