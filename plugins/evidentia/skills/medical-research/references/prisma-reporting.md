# PRISMA Reporting (P7)

**Loaded:** Phase P7 (son faz) — `screening_log` (`screening.md` §5), `evidence_table`
(`data-extraction.md` §5), `rob_assessments` (`risk-of-bias.md` §4) ve GRADE
sertainty/SoF girdisini (`evidence-grading.md` §2) tüketir; okur-yüzü PRISMA
artefaktlarını üretir (`output-templates.md` rapor iskeletine, `report-presentation.md`
temiz kopyasına yerleşir).

**Authority basis:** PRISMA 2020 (Page et al., *BMJ* 2021, 27 madde + akış diyagramı) ·
PRISMA-ScR (Tricco et al., *Ann Intern Med* 2018, 22 madde) · GRADE Working Group
(Summary-of-Findings tablosu, Guyatt et al.).

---

## 1. PRISMA 2020 akış diyagramı (+ PRISMA-ScR varyantı)

Kutu-kutu şablon, `screening_log`'un (`screening.md` §5) alanlarına **birebir** eşlenir
— sayı uydurulmaz, eksik alan `null`/"raporlanmadı" kalır:

```
Identification
  ├─ kayıt tanımlandı (veritabanı): screening_log.identified
  ├─ kayıt tanımlandı (diğer kaynaklar: el-taraması/atıf/gri lit.): ayrı sayaç, yoksa "raporlanmadı"
  └─ tekilleştirme sonrası taranan kayıt: screening_log.deduplicated
Screening
  ├─ başlık/özet taranan: screening_log.title_abstract_screened
  └─ hariç (başlık/özet): screening_log.excluded_title_abstract[] (reason_category × count)
Eligibility (tam-metin)
  ├─ tam-metin için aranan/değerlendirilen: screening_log.full_text_assessed
  └─ hariç (tam-metin, gerekçeli): screening_log.excluded_full_text[] (reason_category × count)
Included
  └─ nihai dahil çalışma: screening_log.included
```

`maybe_resolved_to_include`/`maybe_resolved_to_exclude` diyagramda ayrı kutu **değildir**
— Aşama-1 `maybe` kararlarının Aşama-2'de nasıl çözüldüğünü açıklayan dipnot olarak
akışın altına eklenir (PRISMA kutu şemasını bozmadan şeffaflık). Reconciliation
zorunlu: `included + Σexcluded_title_abstract + Σexcluded_full_text == identified`
tutmuyorsa akış **tutarsız** işaretlenir, sessizce düzeltilmez (`screening.md` §5
no-fabrication notuyla aynı norm).

**PRISMA-ScR varyantı (kapsam derlemesi, `prisma-protocol.md` §4):** kutu adları
"screening"/"eligibility" yerine PCC diline döner — RoB değerlendirmesi genelde
atlanır (§4/§5 bu derleme tipinde boş bırakılır, "kapsam derlemesi — RoB
uygulanmadı" notuyla); Included kutusu "haritalanan kaynak sayısı" olarak etiketlenir.

---

## 2. Kontrol listesi — PRISMA 2020 (27 madde) / PRISMA-ScR (22 madde)

Her madde, raporun **hangi bölümünde** karşılandığı belirtilerek eşlenir (madde
numaraları PRISMA 2020/ScR resmi checklist'iyle birebir):

| Madde grubu | Örnek maddeler | Karşılandığı bölüm |
|---|---|---|
| Başlık/Özet (1–2) | Başlık PRISMA tanımlı; yapılandırılmış özet | Rapor başlığı + özet |
| Giriş (3–4) | Gerekçe; amaç/PICO-PCC | `prisma-protocol.md` §2 → Giriş |
| Yöntem (5–15/16 ScR) | Uygunluk kriterleri, bilgi kaynağı, arama stratejisi, seçim/veri-çıkarım süreci, RoB aracı, sentez yöntemi | `prisma-protocol.md` §3, `search-strategy.md`, `screening.md` §1–3, `data-extraction.md` §1–4, `risk-of-bias.md` §1–3 → Yöntemler |
| Bulgular (16–22/20 ScR) | Seçim akışı, çalışma özellikleri, RoB sonucu, bireysel/sentez sonuçları | §1 akış diyagramı, §3 çalışma-özellikleri tablosu, §4 RoB özeti, §5 SoF tablosu → Bulgular |
| Tartışma (23) | Kanıt sınırlılığı, yöntem sınırlılığı, sonuç | §6 sınır dürüstlüğü + `screening.md` §4 tekil-eleştirmen notu → Tartışma |
| Diğer (24–27) | Kayıt/protokol, fon, çıkar çatışması, veri erişilebilirliği | Protokol referansı (`prisma-protocol.md`), fon/COI alanları (`data-extraction.md` §1 künye bloğu) |

PRISMA-ScR 22 maddesi aynı iskeleti izler; farklılık yalnız RoB maddesinin (PRISMA 2020
madde 12–13/19) **isteğe bağlı** olması ve sentezin niceliksel meta-analiz yerine
haritalama/anlatı olmasıdır (`prisma-protocol.md` §4).

---

## 3. Çalışma-özellikleri tablosu

`evidence_table` (`data-extraction.md` §5) satırlarından okur-yüzü tabloya dönüştürülür
— sütunlar: Çalışma (yazar/yıl/PMID), Tasarım, N (toplam+kol), Popülasyon, Müdahale/
Karşılaştırıcı, Birincil sonuç, İzlem süresi, Fon/COI. Yalnız `human_approved:true`
satırlar tabloya girer; taslak (`human_approved:false`) satır varsa tablo altına
"N çalışma onay bekliyor — tabloya dahil edilmedi" notu eklenir. `"VERİ BULUNAMADI"`
alanlar tabloda aynen korunur (boş hücre veya tahmini değerle doldurulmaz).

---

## 4. RoB özet figürü (trafik-ışığı)

`rob_assessments` (`risk-of-bias.md` §4) satır=çalışma × sütun=araç-alanı ısı-tablosuna
dönüştürülür; hücre = yargı seviyesi (yeşil/sarı/kırmızı + NOS için yıldız sayısı, aynı
şema `risk-of-bias.md` §4 ile birebir). Genel yargı sütunu korunur. Yalnız
`human_approved:true` değerlendirmeler figüre girer; onaysız satır "taslak — figüre
dahil edilmedi" olarak ayrıca not edilir. PRISMA-ScR'de bu bölüm, RoB atlanmışsa
tamamen düşer (§1 notu).

---

## 5. Summary-of-Findings (GRADE) tablosu

Sonuç (outcome) satır bazlı, `evidence-grading.md` §2 GRADE şemasına göre doldurulur:

```jsonc
{ "grade_sof": [
    { "outcome_name": "",
      "n_studies": 0, "n_participants": 0,
      "effect_measure": "HR|OR|RR|MD|...", "effect_size": null, "ci_95": [null, null],
      "certainty": "⊕⊕⊕⊕ High|⊕⊕⊕◯ Moderate|⊕⊕◯◯ Low|⊕◯◯◯ Very low",
      "downgrade_reasons": ["risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias"],
      "importance": "critical|important|not_important",
      "plain_language_summary": "" }
  ] }
```

`n_studies`/`n_participants` doğrudan onaylı `evidence_table` satırlarından toplanır;
`certainty` ve `downgrade_reasons`, onaylı `rob_assessments` (RoB payı) + tutarlılık/
dolaylılık/kesinlik/yayın-yanlılığı değerlendirmesinden (`evidence-grading.md` §2)
gelir — GRADE derecelendirmesi burada **yeniden hesaplanmaz**, yalnız P6 çıktısı
tabloya aktarılır. Boş/`null` alan asla varsayılan sertaintyle ("Moderate" gibi)
doldurulmaz; girdi eksikse `"raporlanmadı"` yazılır.

---

## 6. Sınır dürüstlüğü (no-fabrication)

Herhangi bir connector toplam-kayıt sayısı döndürmüyorsa (ör. bir veritabanı toplam
sonuç sayısını raporlamıyor, yalnız sayfalanmış sonuç listesi veriyor), akış
diyagramındaki ilgili kutu **gerçek elde edilen sayıyla** doldurulur ve kutunun altına
"yalnız alınabilen X kayıt; connector toplam sayı raporlamıyor" notu eklenir — sayı
enterpole edilmez, üst sınır tahmin edilmez. Aynı disiplin `excluded_*` sayaçlarına ve
SoF `n_studies`/`n_participants` alanlarına da uygulanır: eksik/işlenmemiş bir aşama
`null` bırakılır, tahmini sayıyla doldurulmaz (`screening.md` §5 ile aynı norm).

---

## 7. Sonraki faz

Bu, pipeline'ın son fazıdır (P7). Üretilen dört artefakt — akış diyagramı, kontrol
listesi eşlemesi, çalışma-özellikleri tablosu, RoB özeti ve SoF tablosu — bütünüyle
okur-yüzü rapora (`output-templates.md` iskeleti) yerleşir ve `report-presentation.md`
temiz-kopya doktrinine tabi olarak sunulur.
