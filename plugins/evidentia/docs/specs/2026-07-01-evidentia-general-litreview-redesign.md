# evidentia — Genel-Amaçlı Tıbbi Literatür İnceleme Aracına Yeniden Yapılandırma (Tasarım Spesifikasyonu)

> **Tarih:** 2026-07-01 · **Durum:** onaylı tasarım (brainstorming çıktısı) · **Uygulayıcı:** kodlama ajanı
> **Kapsam:** `CureoPrivate/plugins/evidentia` — flagship skill `medical-research`, komutlar, agent, connector roster, plugin metadata, dokümanlar
> **Hedef sürüm:** plugin `1.7.1 → 2.0.0` · skill `medical-research 8.5.0 → 9.0.0`
> **Yöneten standart:** `EKLENTI-GELISTIRME-GENEL-TALIMATI.md` — **kardeş CureoHub deposunun kökünde** (`/mnt/thunderbolt/workspaces/CureoHub/EKLENTI-GELISTIRME-GENEL-TALIMATI.md`; çapraz-repo, göreli link verilmez). Bu refactor onun ZORUNLU ilkelerine uyar (§9 Uyum Haritası).

---

## 1. Bağlam ve problem

evidentia şu an "çok-kaynaklı **istihbarat** + Türkiye-**pazarı** araştırma motoru"dur. Kimliği ve varsayılan davranışı belirli tedavi alanlarına ve ilaçlara **eğiktir (skewed)**:

- `SKILL.md` **Adım 0.5** her koşumda **10-eksen sinyal taraması** yapar; tedavi-alanı katmanları (onkoloji/hematoloji/immünoloji/nöroloji/nadir-hastalık) ve ticari eksenler (drug-intelligence/HTA/medaffairs/regülatuar/Türkiye) **zorunlu/varsayılan** olarak yüklenir.
- `plugin.json` keyword'leri (`oncology`, `hematology`) ve skill `description` tetikleyicileri (`CAR-T, myeloma, JAK, MS, SMA…`) bu eğilimi pekiştirir.
- Çıktı sözleşmesi (§1–21) bir **istihbarat raporu**dur (pipeline snapshot, KOL haritası, TR erişim), sistematik bir literatür incelemesi değil.

**Hedef:** evidentia'yı **genel-amaçlı, tüm-tıp, PRISMA-temelli sistematik/kapsam derleme (systematic/scoping review) aracı**na dönüştürmek. Herhangi bir uzmanlık ve soru tipi (tedavi, tanı, prognoz, etiyoloji, önleme) için eşit çalışsın.

---

## 2. Onaylı kararlar (brainstorming)

| # | Karar | Sonuç |
|---|---|---|
| K1 | De-skewing ilkesi | **Yeteneği silme; opsiyonel + bağlam-tetiklemeli yap.** Hiçbir katman/connector silinmez. Eğilim, *varsayılan/kimliğin* genel PRISMA olmasıyla kalkar. |
| K2 | Birincil iş akışı | **PRISMA 2020 / PRISMA-ScR sistematik/kapsam derleme.** |
| K3 | Pipeline derinliği | **Uçtan uca operasyonel** (arama→dedup→tarama→çıkarım→RoB→GRADE→PRISMA akış), insan-onay kapılarıyla. |
| K4 | Yaklaşım | **A — yerinde refactor**: `medical-research` evrimleştirilir; sıfırdan yazılmaz. |
| K5 | Tüm domain katmanları | 5 tedavi-alanı + ticari/regülatuar/TR/HTA/drug-intel/KOL/epi → **opsiyonel, bağlam-tetiklemeli zenginleştirme modülleri**. |
| K6 | Adlandırma | Plugin `evidentia`, skill `medical-research` **korunur** (ADR-05; dış referanslar kırılmaz). Yalnız `description`/tetikleyici/kimlik yeniden yazılır. |
| K7 | Faz-komutları | 2 yeni opsiyonel komut eklenir: `/evidentia-protocol`, `/evidentia-appraise`. |
| K8 | Uyum | EKLENTİ-GELİŞTİRME-GENEL-TALİMATI ZORUNLU ilkelerine uyum (§9). |

---

## 3. Hedef mimari

### 3.1. Kimlik ve sınır
- **Kimlik:** genel-amaçlı PRISMA-temelli tıbbi literatür inceleme aracı. Varsayılan koşum = saf genel sistematik/kapsam derleme; hiçbir domain modülü zorunlu değil.
- **CureoSuite sınırı pekişir** (`CONNECTORS.md §7` korunur): ticari strateji → `pharmaintel`; MLR → `promo-censor`; bireysel geri-ödeme → `onko-erisim`; patent/FTO → `pharmapatent`; hukuk → `cureolex`/`ius-salutis`. Opsiyonel TR/regülatuar/drug modülleri **kanıt-bağlamı zenginleştirmesi** içindir; ticari istihbarat değildir.

### 3.2. Çekirdek protokol: 10-eksen koşumu → PRISMA yaşam döngüsü

`SKILL.md` çekirdeği **P0–P7** fazlarına yeniden yazılır. Fazlar "doğru irtifada" (right altitude) doktrin/kontrol-listesi olarak ifade edilir — kırılgan hard-coded script değil (Talimatname §12.5).

| Faz | Ne yapar | Kaynak dosya |
|---|---|---|
| **P0 Protokol** | Soru tipi sınıflaması (tedavi/tanı/prognoz/etiyoloji/önleme); **PICO/PECO**; uygunluk (dahil/hariç) kriterleri; derleme tipi (sistematik/kapsam/hızlı) | **YENİ** `prisma-protocol.md` |
| **P1 Arama stratejisi** | Kavram → **MeSH/Emtree** + serbest metin; veritabanı-başına sorgu çevirisi; duyarlılık/özgüllük filtreleri; raporlanabilir arama dizesi | **YENİ** `search-strategy.md` |
| **P2 Getirim + dedup** | Bibliyografik connector'larda kapsamlı arama → tekilleştirilmiş kayıt seti + kaynak-bazlı sayılar | mevcut Adım 1 orkestrasyonu (de-skewed) |
| **P3 Tarama** | Başlık/özet parti parti **dahil/hariç + gerekçe** → tam-metin tarama; insan-onay kapısı | **YENİ** `screening.md` |
| **P4 Çıkarım** | Dahil edilenlerden yapılandırılmış veri çıkarımı (tam-metin + **anamnesis RAG**) → kanıt tabloları | **YENİ** `data-extraction.md` + mevcut `fulltext-retrieval.md` |
| **P5 Yanlılık riski** | **RoB2** (RKÇ) · **ROBINS-I** (randomize-olmayan) · **QUADAS-2** (tanısal) · **Newcastle-Ottawa** (gözlemsel) · **PROBAST** (tahmin modeli) · **AMSTAR-2** (dahil edilen derlemeler); insan-onay kapısı | **YENİ** `risk-of-bias.md` |
| **P6 Sentez + GRADE** | Anlatısal (+ uygun yerde yapılandırılmış) sentez; sonuç-bazlı **GRADE** kesinlik | mevcut `evidence-grading.md` (merkezîleşir) |
| **P7 Raporlama** | **PRISMA 2020 akış diyagramı** (gerçek sayı) + PRISMA/PRISMA-ScR kontrol listesi + çalışma-özellikleri tablosu + RoB özeti + **Summary-of-Findings (GRADE)** tablosu | **YENİ** `prisma-reporting.md` + mevcut `output-templates.md`/`report-presentation.md` |

**Korunan omurga doktrinleri (yeniden çerçevelenir, silinmez):** native-MCP-first çözümleme, clean-copy doktrini, retrieve-don't-dump (anamnesis `evidence_index`), no-fabrication ("VERİ YOK" dürüstlüğü), Cömertlik ilkesi (uncapped derinlik), tek-sefer/kanonik-önbellek sözleşmesi.

**İnsan-onay kapıları:** P3 (dahil/hariç) ve P5 (RoB yargısı) tool-önerir/insan-onaylar. "Uçtan uca operasyonel" = tool tarama/çıkarımı doldurur; nihai yargı kullanıcı onayıyla ilerler (savunulabilir derleme normu).

### 3.3. Opsiyonel zenginleştirme modülleri (bağlam-tetiklemeli)

Eski **Adım 0.5 zorunlu 10-eksen** → **opsiyonel zenginleştirme sınıflandırıcı**ya dönüşür. P0 protokolü soruyu netleştirdikten sonra bir semantik tarama, yalnız soru gerçekten o bağlama girerse ilgili modülü **ilerleyici açımlama** ile yükler (Talimatname §3.1). Hiçbiri varsayılan/zorunlu değildir.

- **Tedavi-alanı** (soru o hastalık alanındaysa): oncology / hematology / immunology / neurology / rare-disease → alan-özgü kılavuz derinliği (NCCN/ESMO/ELN vb.).
- **İlaç/mekanizma** (soru bir molekül/hedefse): drug-intelligence (AdisInsight) · ChEMBL/GtoPdb mekanizma · drugddx DDI.
- **Regülatuar/epidemiyoloji** (ruhsat/insidans/prevalans bağlamında): regulatory-intelligence · openFDA+ICD-11 · PopHIVE.
- **HTA/erişim** (maliyet-etkililik/geri-ödeme bağlamında): hta-layer.
- **Türkiye** (TR-özgü soruda): turkiye-layer (TİTCK/Mevzuat/TÜRKPATENT).
- **KOL** (yazar-ağı/uzman haritası bağlamında): medaffairs-ops + `/evidentia-kol`.

Modül tetiklendiğinde çıktıya **açıkça işaretli bir ek (appendix)** olarak girer; çekirdek SR raporunun kimliğini belirlemez.

### 3.4. Referans dosyaları planı (hiçbiri silinmez)

- **YENİ (6):** `prisma-protocol.md` · `search-strategy.md` · `screening.md` · `data-extraction.md` · `risk-of-bias.md` · `prisma-reporting.md`.
- **YENİDEN ÇERÇEVELENİR:** `SKILL.md` (P0–P7 + opsiyonel-sınıflandırıcı; **< 500 satır ZORUNLU**) · `knowledge-map.md` (eksen-indeksi → *modül-indeksi* + soru-tipi/PICO taksonomisi) · `connector-registry.md` (roster yeniden çerçeve) · `output-templates.md` + `report-presentation.md` (SR raporu + PRISMA artefaktları) · `evidence-grading.md` (GRADE + SoF merkezî) · `skill-manifest.yaml`.
- **"OPSİYONEL ZENGİNLEŞTİRME MODÜLÜ" olarak yeniden etiketlenir** (içerik korunur, "zorunlu/her zaman" → "bağlam-tetiklemeli"): `oncology-layer` · `hematology-layer` · `immunology-layer` · `neurology-layer` · `rare-disease-layer` · `drug-intelligence-layer` · `regulatory-intelligence` · `regulatory-science-layer` · `hta-layer` · `medaffairs-ops-layer` · `turkiye-layer`.

### 3.5. Connector roster yeniden çerçeve (`CONNECTORS.md` tek doğruluk kaynağı güncellenir)

- **Birincil katman — Bibliyografik Çekirdek** (her derlemede): PubMed/EPMC · Europe PMC · OpenAlex · Semantic Scholar · Consensus · ClinicalTrials · bioRxiv/medRxiv · Paper Search · YÖK Tez. **Tam-metin:** annas-reader · Unpaywall (pubmed-epmc). **RAG çıkarım tabanı:** anamnesis (P4'te merkezî) · evidentia-kb. Cochrane/Epistemonikos native-API yok → dürüst "VERİ YOK".
- **Opsiyonel domain connector'ları** (yalnız zenginleştirme bağlamı tetiklerse): TİTCK/Mevzuat/TÜRKPATENT · openFDA+ICD-11 · AdisInsight/ChEMBL/GtoPdb · PopHIVE · med-terminologies/RxNorm/nih-clinicaltables · drugddx · NPI/YÖK-Akademik.
- **4 self-host worker DEĞİŞMEZ** (kod dokunulmaz; ChatGPT-uyum işi korunur; redeploy yok). anamnesis P4 çıkarım tabanı olarak daha merkezî.

### 3.6. Komutlar / agent / plugin metadata

- **5 mevcut komut PRISMA'ya yeniden çerçevelenir:** `/evidentia` (uçtan uca P0→P7, insan-onay kapılı) · `/evidentia-connectors` (preflight) · `/evidentia-fulltext` (P4 tam-metin) · `/evidentia-synthesize` (P4+P6 graph-temelli çıkarım+sentez, anamnesis) · `/evidentia-kol` (opsiyonel KOL zenginleştirme).
- **2 YENİ opsiyonel faz-komutu:** `/evidentia-protocol` (P0–P1: protokol + arama stratejisi yazımı) · `/evidentia-appraise` (P5 RoB + P6 GRADE, verilen çalışma seti üzerinde).
- **Agent `evidence-synthesizer`:** ağır P2–P6 fan-out'unu (arama→tarama→çıkarım→değerlendirme) izole eder; her subagent temiz bağlam penceresiyle çalışır, lider ajana damıtılmış özet döner (Talimatname §11 Aşama 4). Açıklaması güncellenir.
- **plugin.json:** sürüm **2.0.0**; `description` yeniden yazılır (istihbarat/pazar dili → PRISMA/genel-derleme; ≤ 1024 karakter, ne+ne-zaman+tetikleyici); keywords → `systematic-review, prisma, prisma-scr, literature-review, scoping-review, meta-analysis, risk-of-bias, grade, screening, evidence-synthesis` öne; domain keyword'ler (oncology…) **ikincil** kalır (modüller durduğu için).
- **README.md + `docs/EVIDENTIA-CALISMA-SISTEMATIGI.md`:** kimlik/mimari bölümleri PRISMA çekirdek + opsiyonel modül anlatısına yeniden yazılır.

### 3.7. Çıktı sözleşmesi (21-bölüm istihbarat → SR raporu)

**Yeni yapı (PRISMA 2020 hizalı, clean-copy):**
1. Arka plan / gerekçe
2. Amaç + PICO/PECO + derleme tipi
3. Yöntem (uygunluk · bilgi kaynakları · arama stratejisi · seçim süreci · veri çıkarımı · RoB · sentez · GRADE · **veri-kesim tarihi**)
4. **PRISMA akış diyagramı** (tanımlanan → tekilleştirilen → taranan → dışlanan[gerekçe] → dahil; gerçek sayılar)
5. Bulgular (çalışma-özellikleri tablosu · RoB özet figürü · sonuç-bazlı bulgular)
6. **Summary-of-Findings / GRADE tablosu**
7. Tartışma · kısıtlılıklar · sonuç
8. Kaynaklar (Vancouver + PMID/DOI/NCT + erişim tarihi) + dahil/dışlanan çalışma listeleri

**Opsiyonel zenginleştirme ekleri** (yalnız modül tetiklenince, işaretli **ek** olarak): TR-erişim / regülatuar / epidemiyoloji / KOL.

**Korunur:** clean-copy doktrini (Layer A temiz kopya; B/C viz/ops HTML yorumunda; connector/araç adları, çağrı sayıları görünür gövdede yok). **Sidecar `.data.json` şeması güncellenir:** `prisma_flow_counts · eligibility_criteria · search_strategy · screening_log · evidence_table · rob_assessments · grade_sof` + opsiyonel enrichment payload'ları (yalnız varsa) + `sources_summary`. PRISMA/PRISMA-ScR kontrol listesi artefakt olarak.

---

## 4. Uygulama fazları (uygulama-planına girdi)

1. **F1 — Referans iskeleti:** 6 yeni referans dosyasını yaz (prisma-protocol, search-strategy, screening, data-extraction, risk-of-bias, prisma-reporting).
2. **F2 — SKILL.md yeniden yazımı:** çekirdeği P0–P7'ye taşı; Adım 0.5 → opsiyonel zenginleştirme sınıflandırıcı; **< 500 satır**; `description` yeniden yaz; always-load listesini güncelle.
3. **F3 — Modül yeniden etiketleme:** 11 layer dosyasını "opsiyonel zenginleştirme modülü" diline çevir (zorunlu→bağlam-tetiklemeli); `knowledge-map.md`'yi modül-indeksine çevir.
4. **F4 — Çıktı & roster:** `output-templates.md`/`report-presentation.md`/`evidence-grading.md` SR+PRISMA'ya uyarla; `connector-registry.md` + `CONNECTORS.md` roster'ı yeniden çerçevele; sidecar şeması.
5. **F5 — Komut/agent/metadata:** 5 komutu yeniden çerçevele + 2 yeni faz-komutu; `evidence-synthesizer` güncelle; `plugin.json` 2.0.0 + keyword/description; `skill-manifest.yaml`.
6. **F6 — Doküman:** README + EVIDENTIA-CALISMA-SISTEMATIGI yeniden yaz.
7. **F7 — Eval/CI + doğrulama:** PRISMA iş-akışı eval sorguları ekle (`evals/`); G-BUNDLE (roster↔CONNECTORS.md) çapraz-doğrulama; skill `description`/satır-sayısı lint kapısı; canlı probe smoke.

---

## 5. Test ve kabul kriterleri

- **SKILL.md < 500 satır** (Talimatname §3.2.1 ZORUNLU) — CI/lint kapısı.
- **`description` ≤ 1024 karakter**, ne+ne-zaman+tetikleyici içerir, tedavi-alanı-eğilimli tetikleyiciler genel PRISMA tetikleyicileriyle değiştirilmiş (§3.2.2).
- **Tam-nitelikli MCP araç adları** korunur (§3.2.4).
- **G-BUNDLE:** `.mcp.json` roster'ı `CONNECTORS.md` ile çapraz-doğrulanır (mevcut kapı).
- **Eval:** `evals/benchmark-queries.json`'a PRISMA iş-akışı senaryoları (tedavi/tanı/prognoz + kapsam derleme); `evals/rag_quality.py` korunur; genel (domain-modülsüz) bir soru **domain modülü tetiklemeden** temiz genel SR üretmeli (de-skew regresyon testi).
- **No-fabrication:** kaynak yoksa "VERİ YOK"; iddia-düzeyi atıf (§4.3 ZORUNLU).
- **Self-host worker regresyonu yok:** kod değişmez; mevcut `auth.test.ts` yeşil kalır.

---

## 6. Migrasyon / uyum / risk

- **ADR-05:** skill adı `medical-research` korunur → agent'lar, diğer CureoSuite plugin'leri ve `evidence-synthesizer` referansları kırılmaz.
- **Geriye uyum:** eski "istihbarat raporu" davranışı opsiyonel modüllerle *erişilebilir* kalır; ancak varsayılan ve kimlik değişir (kasıtlı, breaking → 2.0.0).
- **Risk — büyük SKILL.md yazımı:** omurga doktrinleri korunarak *yeniden çerçevelenir*, sıfırdan yazılmaz; < 500 satır disiplini progressive disclosure ile sağlanır.
- **Risk — modül regresyonu:** 11 layer içeriği korunur; yalnız tetikleme dili değişir → domain derinliği kaybolmaz.
- **Sürüm:** plugin `2.0.0`; skill `9.0.0`.

---

## 7. Kapsam dışı (non-goals)

- Yeni MCP sunucusu yazımı yok (mevcut roster yeniden çerçevelenir).
- Self-host worker kod değişikliği / redeploy yok.
- Ticari/pazar istihbaratı, MLR, bireysel geri-ödeme, patent, hukuk — kapsam dışı (CureoSuite kardeş plugin'lerine devredilir).
- Otomatik meta-analiz istatistiği (havuzlanmış etki büyüklüğü hesabı) bu sürümde yok; sentez anlatısal + GRADE. (Gelecek sürüm adayı.)

---

## 8. Açık sorular

- **PRISMA akış sayıları:** connector'lar toplam-sonuç sayısı (dedup öncesi) döndürmüyorsa, "tanımlanan kayıt" sayısı getirilen sayfalanmış sonuçlarla sınırlı olabilir → akış diyagramında bu sınır dürüstçe not edilir (no-fabrication). Uygulama-planında ele alınacak.

---

## 9. EKLENTİ-GELİŞTİRME-GENEL-TALİMATI uyum haritası

| Talimatname ilkesi | Bu tasarımdaki karşılığı |
|---|---|
| §1.1 bağlam sonlu bütçe · §3.1 ilerleyici açımlama | Opsiyonel modüller yalnız bağlamda yüklenir; SKILL.md lean çekirdek + referans dosyaları |
| §1.2 üç-katmanlı bağlam · §11-A4 subagent izolasyonu | anamnesis = kalıcı getirim tabanı; `evidence-synthesizer` temiz-bağlam fan-out |
| §3.2.1 SKILL.md < 500 satır (ZORUNLU) | F2 hedefi + F7 lint kapısı |
| §3.2.2 description hijyeni (≤1024, ne+ne-zaman+tetik) | plugin.json + skill description yeniden yazımı |
| §3.2.3 dışlayan içerik ayrı dosyada · §3.2.4 tam-nitelikli araç adı | 6 yeni referans + 11 modül ayrı dosya; araç adları korunur |
| §3.3 doğrulama döngüsü | P3/P5 insan-onay kapıları; P7 PRISMA kontrol listesi validator'ı |
| §4.1 çok-aşamalı getirim (hibrit+rerank) | anamnesis bge-m3 + BM25 + RRF + reranker (mevcut); P4 çıkarım |
| §4.3 iddia-düzeyi topraklama + atıf + abstention (ZORUNLU) | Vancouver atıf + no-fabrication + "VERİ YOK" |
| §5 yapılandırılmış çıktı + önce-muhakeme-sonra-yapı | Clean-copy (muhakeme) → `.data.json` sidecar (yapı) |
| §7 eval/CI kapıları (ZORUNLU) | F7: PRISMA eval sorguları + G-BUNDLE + lint kapısı |
| §12.5 basitlik / doğru irtifa | P0–P7 doktrin/kontrol-listesi; kırılgan if-else yok |

---

*Bu spesifikasyon onaylı brainstorming çıktısıdır. Sonraki adım: `writing-plans` ile ayrıntılı uygulama planı.*
