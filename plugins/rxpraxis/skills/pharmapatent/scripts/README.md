# scripts/ — pharmapatent Yürütülebilir Araçlar

pharmapatent skill'ine eşlik eden yürütülebilir Python araçları. Bu scripts Claude'un yorumlarına ek olarak hızlı, tekrarlanabilir hesaplamalar için kullanılır.

## Araçlar

### `loe-calculator.py` — Loss of Exclusivity hesaplayıcı

Türkiye'de bir jenerik/biyobenzer ürünün en erken pazara giriş tarihini hesaplar. Patent + veri imtiyazı MAX formülünü uygular.

**Kullanım**:
```bash
python3 scripts/loe-calculator.py
```

Interaktif promptlar: ürün adı, biyobenzer mi, ilk AB/TR ruhsat tarihi, en geç biten aktif patent tarihi.

**Çıktı**:
- Veri imtiyazı bitiş tarihi
- Patent bitiş tarihi
- LOE tarihi (en erken yasal pazara giriş)
- Belirleyici faktör (PATENT vs DATA_EXCLUSIVITY)
- Bolar kapsamında biyoeşdeğerlik başlama önerisi
- Praktik pazara arz tarihi (ruhsat + fiyat + SGK süreci dahil)
- Uyarılar (invalidity feasibility, Bolar fırsatları)

**Bağımlılık**: `python-dateutil`
```bash
pip install python-dateutil
```

**Programatik kullanım**:
```python
from datetime import date
import importlib.util
spec = importlib.util.spec_from_file_location("loe_calc", "scripts/loe-calculator.py")
loe_calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loe_calc)

result = loe_calc.calculate_loe(
    first_registration=date(2018, 2, 8),
    latest_patent_expiry=date(2030, 2, 12),
)
print(result['loe_date'], result['determining_factor'])
# 2030-02-12 PATENT
```

---

### `claim-parser.py` — Patent istemi özellik ayrıştırıcı

Bağımsız istem metnini otomatik olarak teknik özelliklere (F1, F2, F3 ...) ayrıştırır. FTO ve Invalidity özellik-özellik matrisinin ilk iskeletini üretir.

**Kullanım**:
```bash
# Interaktif mod
python3 scripts/claim-parser.py

# Demo modu (trastuzumab hipotetik istemi)
python3 scripts/claim-parser.py --example
```

**Kategori tespiti**:
- `active_ingredient` — aktif madde (INN, antikor, peptid)
- `excipient` — yardımcı madde (trehalose, histidin, polisorbat vb.)
- `physical_form` — fiziksel form (tablet, liyofilize, kristalin vb.)
- `concentration_range` — konsantrasyon aralığı (%, mg/mL)
- `ph_range` — pH aralığı
- `process_step` — üretim adımı
- `use_or_treatment` — tedavi endikasyonu
- `device` — cihaz bileşeni
- `stability_criterion` — stabilite kriteri
- `other` — sınıflandırılamayan

**Çıktılar**:
1. Özet özellik tablosu (ID, kategori, kısaltılmış açıklama)
2. FTO özellik-özellik matrisi şablonu (markdown, direkt rapora yapıştırılabilir)
3. Her özelliğin tam metni (detaylı inceleme için)

**Bağımlılık**: Hiçbiri (yalnız Python 3 standart kütüphane).

---

### `royalty-calculator.py` [v1.3.0] — Lisans NPV/IRR Calculator

Lisans anlaşması finansal modellemesi: upfront + milestone payments + tiered royalty stream üzerinden NPV, IRR, Relief-from-Royalty (RFR) hesabı ve sektörel benchmark karşılaştırması.

**Kullanım**:
```bash
# Interaktif mod (basit deal input)
python3 scripts/royalty-calculator.py

# ADC lisans örneği (hipotetik Anti-HER2 ADC Faz II)
python3 scripts/royalty-calculator.py --example

# Relief-from-Royalty modu (vergi + dava tazminat değerlemesi)
python3 scripts/royalty-calculator.py --rfr
```

**Hesaplar**:
- Toplam nominal değerler (upfront + milestones + royalty)
- NPV (licensor + licensee perspektifleri, after-tax)
- IRR (Newton-Raphson bisection)
- Discount rate duyarlılık analizi (8%, 10%, 12%, 15%, 18%, 25%)
- Yıl-yıl cash flow tablosu
- Sektörel benchmark karşılaştırması (comparable transactions)

**Benchmark kategorileri**:
- `small_molecule_onco_P3`, `mab_P3`, `adc_P2`, `car_t_P2`, `mrna_lnp_preclinical`, `gene_therapy_P1`, `platform_preclinical`

**Kullanım senaryoları**:
- Lisans müzakeresi öncesi deal structure modelleme
- M&A due diligence değerleme
- SMK m. 151 dava tazminat hesaplaması (RFR metodolojisi)
- Transfer pricing intercompany lisans

**Programatik kullanım**:
```python
from royalty_calculator import LicenseDeal, Milestone, RevenueTier, build_deal_cash_flows, calculate_npv

deal = LicenseDeal(
    name="My Deal",
    upfront_usd=100_000_000,
    milestones=[Milestone("Phase 3", 2, 50_000_000, 0.7)],
    royalty_tiers=[RevenueTier(0, None, 0.10)],
    annual_revenue_projection=[0, 0, 100_000_000, 500_000_000, ...],
)
cfs = build_deal_cash_flows(deal)
npv = calculate_npv(cfs, discount_rate=0.12)
```

**Bağımlılık**: `python-dateutil` (opsiyonel, temel fonksiyonlar standart kütüphane ile çalışır).

---

### `patent-expiry-monitor.py` [v1.3.0] — Portföy Takip Monitörü

Patent portföyünüz için otomatik yıllık harç + expiry uyarıları. CSV/JSON import + markdown/JSON export.

**Kullanım**:
```bash
# Örnek portföyle demo (6 hipotetik patent)
python3 scripts/patent-expiry-monitor.py --example

# CSV import
python3 scripts/patent-expiry-monitor.py --import portfolio.csv

# Uyarı penceresi ayarı (default 365 gün)
python3 scripts/patent-expiry-monitor.py --example --days 180
```

**CSV formatı**:
```csv
patent_no,baslik,basvuru_sahibi,basvuru_tarihi,yil_harci_tarihi,expiry_tarihi,status,jurisdiction
EP1235764,Atorvastatin Form I,Pfizer,1997-07-17,2026-07-17,2024-07-17,active,TR
EP2876108,Stabilized formulation,Teva,2009-03-12,2026-09-12,2029-03-12,active,TR
```

**Uyarı kategorileri**:

| Kategori | Tetikleyici | Aksiyon |
|---|---|---|
| Annual fee — CRITICAL | ≤7 gün | DERHAL ödeme |
| Annual fee — HIGH | ≤30 gün | 30 gün içinde planla |
| Annual fee — MEDIUM | ≤60 gün | Bütçe takvimine ekle |
| Annual fee — LOW | ≤90 gün | Not et |
| Annual fee OVERDUE | 0 ile -180 gün | Gecikme harcı ile hâlâ mümkün |
| Expiry — CRITICAL | ≤30 gün | LOE + jenerik hazırlık |
| Expiry — HIGH | ≤90 gün | Lifecycle extension |
| Expiry — MEDIUM | ≤180 gün | Evergreening |
| Expiry — LOW | ≤365 gün | Portföy strateji notu |

**Çıktılar**:
- Konsol: öncelik-bazlı sıralı uyarı listesi
- Markdown: `/tmp/patent-alerts-YYYYMMDD.md`
- JSON: `/tmp/patent-alerts-YYYYMMDD.json`

**Programatik kullanım**:
```python
from patent_expiry_monitor import Patent, generate_alerts
from datetime import date

patents = [
    Patent(patent_no="EP123", baslik="Test", basvuru_sahibi="X",
           yil_harci_tarihi=date(2026, 5, 15), expiry_tarihi=date(2030, 1, 1)),
]
alerts = generate_alerts(patents, window_days=365)
for a in alerts:
    print(f"[{a.urgency}] {a.message}")
```

**Önemli not**: Bu script manuel girilen / CSV import edilen portföy üzerinde çalışır. TÜRKPATENT EPAAT resmi API'si public değildir; canlı sorgu için TÜRKPATENT ile entegrasyon gereklidir. Script web scraping yapmaz (robots.txt + ToS sebebiyle).

**Bağımlılık**: `python-dateutil`.

---

### `cpc-recommender.py` [v1.4.0] — CPC/IPC Code Önerici

Molekül/cihaz profilinden uygun CPC (Cooperative Patent Classification) ve IPC kodlarını öneren script. Küçük molekül + biyolojik + ADC + CAR-T + mRNA + gene therapy + radioligand + cihaz profillerini destekler.

**Kullanım**:
```bash
# Interactive mod
python3 scripts/cpc-recommender.py

# Demo örnekler
python3 scripts/cpc-recommender.py --example small_molecule
python3 scripts/cpc-recommender.py --example biologic
python3 scripts/cpc-recommender.py --example adc
python3 scripts/cpc-recommender.py --example car_t
python3 scripts/cpc-recommender.py --example mrna
python3 scripts/cpc-recommender.py --example gene_therapy
python3 scripts/cpc-recommender.py --example device

# JSON çıktı (otomasyon için)
python3 scripts/cpc-recommender.py --example adc --json
```

**Girdi parametreleri**:
- Modalite (small_molecule / antibody / adc / car_t / mrna / gene_therapy / radioligand / device)
- Endikasyon (oncology / hematology_malignancy / hemophilia / cardiovascular / neurology / antiviral / immunology)
- Spesifik hedef (HER2 / CD20 / PD-1 / BCMA / FVIII / VEGF / EGFR)
- Molekül sınıfı (pyrimidine / pyrrole / indole / piperidine)
- Dozaj formu (tablet / capsule / injection / lyophilized / inhaler / nanoparticle / liposome)
- Cihaz bileşeni (syringe / auto_injector / pen / inhaler / pump / stent)
- Özel özellikler (bispecific / combination_therapy / AAV / lentiviral / AI_diagnostic)

**Çıktı**:
- Primary CPC kodları (öncelikli) — modalite + endikasyon + spesifik hedef
- Secondary CPC kodları — dozaj formu + cihaz bileşeni + özellikler
- USPTO + Espacenet Boolean sorgu örnekleri

**Bağımlılık**: Yok (yalnız Python standart kütüphane).

---

### `family-tracer.py` [v1.4.0] — Patent Ailesi Takipçisi (INPADOC-style)

Patent ailelerini haritalayan, coverage gap analizi yapan ve Mermaid flowchart diyagramı üreten script. Espacenet INPADOC veri modeline benzer mantıkla çalışır.

**Kullanım**:
```bash
# Örnek portföy ile demo (3 aile, 14 üye)
python3 scripts/family-tracer.py --example

# CSV import
python3 scripts/family-tracer.py --import portfolio.csv

# Mermaid flowchart çıktısı (her aile priority → üyeleri)
python3 scripts/family-tracer.py --example --mermaid

# JSON yapısal çıktı
python3 scripts/family-tracer.py --example --json
```

**CSV formatı**:
```csv
family_id,patent_no,jurisdiction,priority_date,filing_date,grant_date,status
FAM-1,US9999999,US,2010-01-15,2011-01-10,2013-06-01,granted
FAM-1,EP2123456,EP,2010-01-15,2011-01-10,2014-03-15,granted
FAM-1,TR/EP2123456,TR,2010-01-15,2011-01-10,2014-06-20,granted
```

**Status kategorileri**: `granted`, `active`, `pending`, `abandoned`, `lapsed`, `revoked`, `unknown`.

**Çıktı fonksiyonları**:
- Her aile için priority date + expiry (20 yıl) + jurisdiction listesi
- Coverage gap analizi (hedef ülkeler vs aktif jurisdictions)
- Coverage matrix markdown tablosu (aile × ülke)
- Mermaid flowchart (renk kodlu: yeşil=granted, sarı=pending, kırmızı=abandoned/revoked)
- JSON serialize (API/otomasyon için)

**Bağımlılık**: Yok (csv + json standart kütüphane).

---

### `priority-date-matrix.py` [v1.4.0] — Priority Date Uyumluluk Analizörü

Patent portföyünde priority date uyumluluk check'leri + prior art kesim tarihi matrisi. Özellikle M&A DD ve portföy audit için kritik.

**Kullanım**:
```bash
# Örnek portföyle demo (6 patent, 2 fail case dahil)
python3 scripts/priority-date-matrix.py --example

# CSV import
python3 scripts/priority-date-matrix.py --import data.csv

# Uyumluluk check zorunlu (example zaten çalıştırır)
python3 scripts/priority-date-matrix.py --import data.csv --check
```

**CSV formatı**:
```csv
family_id,patent_no,jurisdiction,priority_date,filing_date,pct_filing_date,national_phase_date
FAM-1,US99999,US,2015-03-01,2016-02-28,2016-02-28,2017-09-01
```

**Check kategorileri**:
| Check | Tetikleyici | Hukuki Temel |
|---|---|---|
| Paris Convention priority | Priority → filing ≤365 gün | Paris Convention Art. 4 |
| PCT national phase | PCT filing + 30 ay ≥ national phase | PCT Art. 22, 39 |
| Family priority consistency | Aynı aile → aynı priority date | Genel tutarlılık |

**Check sonuçları**: `pass` ✓ / `warning` ⚠ / `fail` ✗ / `skip` ○

**Çıktı**:
- Priority date matrisi tablosu
- Her aile için prior art kesim tarihi (invalidity araştırması tarihsel sınır)
- Uyumluluk check özeti (pass/warning/fail sayıları)

**Kullanım senaryoları**:
- Yeni iktisap edilen portföyde hukuki uyum audit
- Invalidity araştırmasından önce prior art arama penceresini belirleme
- Bölünmüş başvuru (divisional) zinciri analizi
- Portföy tutarsızlıklarının tespiti

**Bağımlılık**: Yok (standart kütüphane).

---

### `spc-calculator.py` [v1.5.0] — AB SPC Süre Hesaplayıcı

AB Supplementary Protection Certificate (SPC) süresini Regulation (EC) No 469/2009 Art. 13 formülüne göre hesaplar. **ÖNEMLİ**: SPC Türkiye'de geçerli değildir — sadece AB + bazı Avrupa ülkeleri için. Bu script Türkiye LOE hesabında AB portföy karşılaştırması için kullanılır.

**Formül (Art. 13)**:
```
SPC süresi = (İlk AB ruhsat tarihi - Patent başvuru tarihi) - 5 yıl
Max SPC süresi = 60 ay (5 yıl)
Pediatric extension = +6 ay ek (Reg 1901/2006)
Toplam koruma ≤ ilk ruhsat tarihi + 15 yıl (+ 6 ay pediatric)
```

**Kullanım**:
```bash
# Interactive mod
python3 scripts/spc-calculator.py

# Hipotetik örnekler
python3 scripts/spc-calculator.py --example keytruda
python3 scripts/spc-calculator.py --example sovaldi
python3 scripts/spc-calculator.py --example ozempic
python3 scripts/spc-calculator.py --example enhertu
python3 scripts/spc-calculator.py --example xtandi
python3 scripts/spc-calculator.py --example fast_approval

# Tüm örnekleri TR karşılaştırma tablosu olarak
python3 scripts/spc-calculator.py --compare-tr
```

**Girdi parametreleri**:
- Patent başvuru tarihi (PCT veya ulusal başvuru)
- İlk AB ruhsat tarihi (EMA merkezi veya ulusal)
- Patent süresi (standart 20 yıl)
- Pediatric extension talep (evet/hayır)

**Çıktı**:
- SPC uygunluk testi (eligibility: klinik geliştirme ≥5 yıl alması gerekir)
- SPC süresi (ay + yıl)
- SPC yürürlüğe giriş tarihi (= patent expiry)
- SPC expiry tarihi
- Toplam koruma süresi (patent + SPC)
- **TR karşılaştırması**: Türkiye'de SPC olmadığı için patent expiry'de LOE; koruma farkı gün + yıl olarak gösterilir

**Kullanım senaryoları**:
- AB biosimilar pazar giriş takvimi hazırlığı
- Türkiye jenerik giriş stratejisi (TR-AB arbitraj fırsat tespiti)
- Portföy-geniş AB vs TR LOE karşılaştırma tablosu
- Lifecycle management pazar genişletme planlaması

**Bağımlılık**: `python-dateutil`

---

### `report-builder.py` [v1.6.0] — Rapor Otomasyon Orkestratörü

11 rapor tipi için iskelet üretici — `rapor-sablonlari.md` + `visualize-widget-kutuphanesi.md` + `carbon-html-report` skill ile entegre.

**Rapor tipleri** (11 adet):

| ID | İsim | Hedef kitle varsayılan | Bölüm | Zorunlu görsel |
|---|---|---|---|---|
| `fto` | FTO Raporu | Legal | 10 | 4 |
| `invalidity` | Invalidity Briefing | Legal | 10 | 4 |
| `landscape` | Landscape Raporu | Executive | 11 | 4 |
| `lifecycle` | Lifecycle Yol Haritası | Executive | 11 | 3 |
| `regulatory` | Pazara Giriş Takvimi | Executive | 10 | 2 |
| `litigation` | Litigation Briefing | Legal | 10 | 3 |
| `dd` | Due Diligence (M&A) | Executive | 12 | 4 |
| `opposition` | Opposition Briefing (EPO) | Legal | 11 | 3 |
| `biosimilar` | Biosimilar Pathway | Executive | 11 | 4 |
| `licensing` | License Negotiation Memo | Executive | 10 | 3 |
| `expert_witness` | Expert Witness Report (FSHHM) | Legal | 12 | 2 |

**Kullanım**:

```bash
# Mevcut rapor tiplerini listele
python3 scripts/report-builder.py --list-types

# Örnek rapor üretimi (FTO atorvastatin için)
python3 scripts/report-builder.py --example

# Spesifik rapor iskeleti üret
python3 scripts/report-builder.py --type licensing --asset "Anti-TROP2 ADC BRX-202" --out memo.md

# Hedef kitleyi override et
python3 scripts/report-builder.py --type fto --asset "Pembrolizumab" --audience Executive --out fto.md
```

**Çıktı yapısı**:
Her üretilen markdown rapor iskeletin içerir:
- Frontmatter (başlık, versiyon, hedef kitle, dağıtım kısıtı)
- Görsel gereksinimleri bölümü (visualize-widget-kutuphanesi.md referansıyla)
- İlgili scriptler listesi (`family-tracer.py`, `loe-calculator.py`, vs.)
- N bölüm iskeleti (rapor tipine göre 10-12)
- Her bölüm için: alt başlık + `visualize:show_widget` şablon referansı + kaynak yer tutucu
- Compliance beyanları bölümü (son bölüm)
- Hazırlayan/inceleyen imza bloğu

**Entegrasyon**:
- `rapor-sablonlari.md` — bölüm sırası + içerik standardı
- `visualize-widget-kutuphanesi.md` — görsel şablon referansları
- `compliance-beyanlari.md` — zorunlu compliance bloğu
- `carbon-html-report` skill — nihai HTML render için (manual follow-up)

---

### `biosimilar-comparator.py` [v1.6.0] — CQA Benzerlik Skorlama

Biyobenzer adayı + referans ürün arasında Critical Quality Attributes (CQA) comparability analizi. ICH Q5E + FDA + EMA Biosimilar Guidance uyumlu.

**Tier sistemi**:
- **Tier 1 (Critical)** — biosimilarity için zorunlu benzer (MoA + safety); min skor 0.85
- **Tier 2 (Important)** — ciddi sapma riski, ek klinik veri gerekebilir; min skor 0.70
- **Tier 3 (Minor)** — izleme yeterli, pazarlama engellemeyen sapmalar; min skor 0.50

**Similarity bands**:
- Highly Similar (≥0.85 overlap) → skor 1.0
- Similar (0.70-0.85) → skor 0.75
- Trend toward Similar (0.55-0.70) → skor 0.40
- Not Similar (<0.55) → skor 0.00

**CQA kategorileri**:
- `structural` — primary sequence, glycan profile, charge variants, disulfide
- `functional` — binding affinity, ADCC/CDC, neutralization, FcR binding
- `process` — HCP, DNA residual, endotoxin
- `product` — aggregates, fragments, deamidation, oxidation
- `pkpd` — AUC, Cmax, half-life

**Kullanım**:

```bash
# Trastuzumab biyobenzer PASS örneği
python3 scripts/biosimilar-comparator.py --example trastuzumab

# Adalimumab citrate-free biyobenzer PASS örneği
python3 scripts/biosimilar-comparator.py --example adalimumab

# Ranibizumab FAIL örneği (Tier 1 critical failure)
python3 scripts/biosimilar-comparator.py --example ranibizumab_fail

# JSON çıktı formatı
python3 scripts/biosimilar-comparator.py --example trastuzumab --json

# Dış JSON import
python3 scripts/biosimilar-comparator.py --import cqa_data.json
```

**Çıktı**:
- CQA detay tablosu (tier + overlap + band + method)
- Tier skorları (her tier ayrı ortalama + minimum gereksinim check)
- Overall tier-ağırlıklı skor
- Verdict: PASS / CONDITIONAL / FAIL + gerekçe
- Başarısız CQA'lar listesi (Tier 1 critical failures özellikle vurgulanır)

**Kullanım senaryoları**:
- Biyobenzer geliştirme — iç gate decision
- Regülatör brifing hazırlık (FDA/EMA CHMP)
- Licensing/acquisition DD — target biyobenzer asset değerlendirme
- Scientific advice toplantıları için comparability paketi

---

### `fto-grid.py` [v1.7.0] — Patent × Ülke × Ürün FTO Matrisi

Çoklu ürün + çoklu ülke + çoklu patent kombinasyonu için FTO risk matrisi otomasyonu. Her hücre için 5 statü (Clean / Caution / Blocker / N/A / Expired) + gerekçe satırı.

**Özellikler**:
- Statü dağılım özeti (toplam + yüzde)
- Ürün bazlı blocker listeleri
- Ülke bazlı blocker yoğunluğu
- Patent kategori ayrımı (molecule / formulation / process / device / 2nd_medical_use)

**Kullanım**:

```bash
# 3 hipotetik örnek
python3 scripts/fto-grid.py --example hcv           # Sofosbuvir DAA, 2 ürün × 5 ülke × 3 patent = 30
python3 scripts/fto-grid.py --example obesity       # Semaglutide + Tirzepatide jenerik, 50 değerlendirme
python3 scripts/fto-grid.py --example biosimilar    # Humira biyobenzer, 12 değerlendirme

# JSON veri import
python3 scripts/fto-grid.py --import fto_data.json

# JSON çıktı
python3 scripts/fto-grid.py --example hcv --format json
```

**Entegrasyon**: Mod 1 FTO raporu iskeleti (`report-builder.py --type fto`) için birincil görsel veri kaynağı. `visualize:show_widget` ile `fto-patent-country-heatmap` şablonuna doldurulabilir.

---

### `regulatory-timeline.py` [v1.7.0] — Ruhsat + SGK + Bolar Takvim

Türkiye (+ karşılaştırmalı AB + ABD) regülatör + geri ödeme takvim otomasyonu. 3 ürün tipi: **innovative (11 aşama ~12 yıl)**, **biosimilar (9 aşama ~8 yıl)**, **generic (7 aşama ~2 yıl)**. Bolar (SMK m.85/3) overlap hesabı dahil.

**Türkiye inovatif aşamaları**:
1. CMC + non-clinical (36 ay)
2. Faz I (18 ay)
3. Faz II (24 ay)
4. Faz III (36 ay)
5. TİTCK başvuru hazırlık (6 ay)
6. TİTCK değerlendirme (10 ay — 180+60 gün yasal + ek)
7. Ruhsat verilmesi (1 ay)
8. SGK başvuru + Ödeme Komisyonu (8 ay)
9. SUT listesi yayın (1 ay)
10. Satışa arz (1 ay)
11. Hastane ihale + erişim (6 ay)

**Kullanım**:

```bash
# Demo 3 senaryo (innovative + biosimilar + generic + Bolar)
python3 scripts/regulatory-timeline.py --example

# Tek ürün için ASCII Gantt
python3 scripts/regulatory-timeline.py --product "Pembrolizumab" --type innovative --start 2024-01

# Jenerik + Bolar hesabı
python3 scripts/regulatory-timeline.py --product "Semaglutide jenerik" --type generic \
    --patent-expiry 2031-05 --start 2029-05 --format mermaid
```

**4 format**: ASCII Gantt (konsol), Markdown tablo, Mermaid Gantt (rapor), JSON.

---

### `kol-graph.py` [v1.7.0] — KOL Network + Centrality

Terapötik alan için KOL (Key Opinion Leader) ağını network grafi olarak inşa eder. Düğümler (KOL + merkez + şehir + uzmanlık + aktif trial + 5 yıl yayın), kenarlar (co_author / co_pi / steering_committee / advisory_board / same_center).

**Weighted centrality formülü**:
- co_author: ×1 per ortak yayın
- co_pi: ×3 per ortak klinik çalışma
- steering_committee: ×5 per steering pozisyon
- advisory_board: ×2 per AB rolü
- same_center: ×0.5
- Bonus: aktif trial ×2, 5y yayın sayısı ×0.1

**Örnekler**:
- `turkish_ms` (8 KOL, 14 işbirliği) — Prof. Dr. M. Demir (Hacettepe) #1 centrality
- `turkish_onco` (8 KOL, 14 işbirliği) — Prof. Dr. H. Arslan (İstanbul Üni Onkoloji) #1 centrality
- `glp1_investigators` (6 KOL, 8 işbirliği) — global GLP-1 araştırmacıları

**Kullanım**:

```bash
python3 scripts/kol-graph.py --example turkish_ms --format mermaid     # Mermaid network çıktı
python3 scripts/kol-graph.py --example turkish_onco --format markdown  # Centrality tablosu
python3 scripts/kol-graph.py --example glp1_investigators --format json
```

**Entegrasyon**: Nexopharos OSINT projesindeki KOL mapping adımlarını otomatikleştirir; Landscape raporu (Mod 3) + Licensing raporu (Mod 10) KOL eki için birincil veri.

---

### `evidence-ranker.py` [v1.7.0] — GRADE + Oxford CEBM Sınıflandırma

Klinik çalışmaları ve yayınları GRADE (HIGH/MODERATE/LOW/VERY LOW) ve Oxford CEBM 2011 (Level 1-5) hiyerarşilerine göre otomatik sınıflandırır.

**GRADE downgrade kriterleri**:
- Risk of Bias: -1 ciddi / -2 çok ciddi
- Inconsistency: -1 / -2
- Indirectness: -1 / -2
- Imprecision: -1 / -2
- Publication bias: -1

**GRADE upgrade kriterleri** (sadece observasyonel için):
- Large effect (RR > 2 veya < 0.5): +1
- Very large effect (RR > 5 veya < 0.2): +2
- Dose-response gradient: +1
- Plausible confounders reduce observed effect: +1

**15 çalışma tasarımı enum** (StudyDesign):
- SR_RCT, META_ANALYSIS, RCT, CLUSTER_RCT, NONRAND_CONTROLLED, COHORT_PROSP, COHORT_RETR, CASE_CONTROL, CROSS_SECTIONAL, CASE_SERIES, CASE_REPORT, MECHANISM, ANIMAL, IN_VITRO, EXPERT_OPINION

**Kullanım**:

```bash
# 6 hipotetik örnek demo
python3 scripts/evidence-ranker.py --example

# Kendi çalışma verileri (JSON)
python3 scripts/evidence-ranker.py --import studies.json --format markdown

# JSON çıktı
python3 scripts/evidence-ranker.py --example --format json
```

**Örnek çıktılar**:
- KEYNOTE-189 (RCT, OS+PFS pozitif): **HIGH**
- CheckMate-067 (inconsistency): **MODERATE**
- Dapagliflozin retrospektif kohort (RoB -1, büyük etki +1, confounder reduce +1): LOW → **MODERATE**
- Lecanemab case series (12 hasta): **VERY LOW**
- Cochrane CAR-T SR (imprecision -1): HIGH → **MODERATE**
- AZALEA-TIMI 71 (indirectness -1, surrogate): HIGH → **MODERATE**

**Entegrasyon**: Invalidity (Mod 2) + Expert Witness (Mod 12) raporlarında teknik delil hiyerarşisi oluşturmak için. Medical affairs Sci advice + HTA dossier hazırlığında GRADE tablolarının ön üretimi.

---

### `patent-language-translator.py` [v1.8.0] — Patent İstem Dil Çevirmeni

Patent istemlerindeki teknik-legal jargonu operasyonel karar vericilere (BD, stratejist, klinik ekip, CFO) üç hedefe dönüştürür:

1. **Sade Türkçe** — her özellik için "bu şunu kapsıyor" açıklaması
2. **İhlal testi sorusu** — "Ürün X özelliğine sahip mi?"
3. **Design-around ipucu** — hangi özelliği değiştirmek lafzi ihlali keser

**Özellikler**:
- Preamble / transition / body yapısal ayrıştırma
- Transition scope (open/closed/intermediate) tespit
- 40+ farmasötik terim sözlüğü (API, DAR, scFv, Fc, CDR, LNP, ADC vb.)
- 9 özellik kategorisi (active_ingredient, excipient, physical_form, concentration, pH, process, use, device, stability)
- Markush grubu üye çıkarımı
- Jurisdiction hints (TR/EPC context)

**Kullanım**:
```bash
python3 scripts/patent-language-translator.py --example pembrolizumab   # Antikor formülasyon
python3 scripts/patent-language-translator.py --example semaglutide     # Peptid + cihaz
python3 scripts/patent-language-translator.py --example markush         # Statin Markush grup
python3 scripts/patent-language-translator.py --example adc             # ADC DAR+payload Markush
python3 scripts/patent-language-translator.py --claim "A pharmaceutical..."   # Özel istem
```

**Entegrasyon**: Mod 1 FTO + Mod 2 Invalidity + Mod 12 Expert Witness raporlarında istem analizi ön-işlem adımı. `claim-parser.py` ile komplementer (parser yapısal ayrıştırma; translator semantik Türkçeleştirme).

---

### `health-economics-qaly.py` [v1.8.0] — Sağlık Ekonomisi QALY + ICER

Farmakoekonomi temel hesaplayıcı. Yeni tedavi × comparator karşılaştırması → incremental cost / QALY / LY + ICER + 12 HTA threshold değerlendirme.

**Model**:
- `Intervention(cost_per_cycle × cycles + additional_costs)` — toplam maliyet
- `HealthState(utility [0-1] × duration_months)` — QALY hesabı
- `ICER = ΔCost / ΔQALY`
- Dominance analizi: dominant / dominated / trade-off / cost-saving / equivalent

**12 HTA Threshold**:
| Threshold | Range | Currency |
|---|---|---|
| NICE standard | £20-30K | GBP |
| NICE end-of-life | £50K | GBP |
| NICE severity 2022 | £30-50K | GBP |
| ICER standard | $100-150K | USD |
| ICER ultra-rare | $150-200K | USD |
| WHO 1× GDP | $14K (TR est.) | USD |
| WHO 3× GDP | $42K (TR est.) | USD |
| Türkiye informal | ₺500K | TRY |
| Germany IQWiG | No fixed | — |
| France HAS | ASMR hierarchy | — |
| China CDE | ¥150-250K | CNY |
| Japan MHLW | ¥5-7.5M | JPY |

**Kullanım**:
```bash
python3 scripts/health-economics-qaly.py --example pembrolizumab   # NSCLC 1L PD-L1 high
python3 scripts/health-economics-qaly.py --example car-t           # r/r DLBCL 3L+ (durable remission)
python3 scripts/health-economics-qaly.py --example resmetirom      # MASH F2-F3
python3 scripts/health-economics-qaly.py --threshold-table         # Tüm threshold tablosu
```

**Entegrasyon**: Mod 7 M&A DD (NPV hesaplama desteği), Mod 10 Licensing (royalty fair value), Mod 3 Landscape (pazar erişim projeksiyonu), Mod 5 Regulatory (SGK başvuru hazırlık).

---

### `realworld-evidence-harvester.py` [v1.8.0] — RWE Konsolidasyon Orkestratörü

Türkiye + global RWE verilerini tek paket halinde konsolide eder. 13 kaynak registry:

**Türkiye kaynakları**:
- SGK Medula (reçete, hasta, harcama — 6-12 ay gecikme)
- TİTCK Ruhsat (real-time)
- TR Kanser Kayıt Sistemi (insidans, sağkalım)
- IMS Turkey (pazar payı, ciro — commercial license)

**Global kaynakları**:
- FDA FAERS (adverse events)
- EMA EudraVigilance (AB ADR)
- ClinicalTrials.gov (ongoing RWE + registry)
- FiercePharma / Endpoints News (ticari)
- Evaluate Pharma (forecasts — commercial)
- PubMed (registry + RWE literatür)
- SEER US (kanser epidemioloji)
- GARDP (AMR surveillance)

**Özellikler**:
- `RWEDataPoint(source, metric, value, date_range, note)` — yapılandırılmış
- Kaynak dağılımı özet tablosu
- Boşluk (gap) tespiti
- `--template` boş şablon üretimi yeni ürün için

**Kullanım**:
```bash
python3 scripts/realworld-evidence-harvester.py --example pembrolizumab-tr  # TR RWE (15 DP)
python3 scripts/realworld-evidence-harvester.py --example glofitamab-tr     # Roche (9 DP)
python3 scripts/realworld-evidence-harvester.py --example semaglutide-global # Global (14 DP)
python3 scripts/realworld-evidence-harvester.py --list-sources               # 13 kaynak detayı
python3 scripts/realworld-evidence-harvester.py --template --product "X" --indication "Y"
```

**Entegrasyon**: Mod 3 Landscape + Mod 5 Regulatory + Mod 7 M&A DD + Mod 10 Licensing. Roche Türkiye Group Audit RWE kısmına doğrudan destek. Nexopharos / REGISTURK registry projeleri için metodolojik temel.

---

### `compliance-checker.py` [v1.8.0] — Çok-Çerçeveli Compliance Otomatik Uyum

Pharma operasyonları + HCP etkileşimleri + veri işleme senaryolarını 7 majör compliance çerçevesine karşı test eder.

**7 Framework**:
1. **FCPA** — US Foreign Corrupt Practices Act (US + US-listed firms)
2. **UKBA** — UK Bribery Act 2010 (UK + UK connection)
3. **MASAK** — TR 5549 + 6362 (şüpheli işlem, KYC, rüşvet)
4. **KVKK/GDPR** — 6698 + 2016/679 (sağlık verisi özel nitelikli)
5. **EFPIA Code** — AB pharma etik (ToV disclosure, hospitality)
6. **IFPMA Code** — global pharma etik
7. **Roche Group Audit (internal)** — Mahir'in audit bağlamı

**4 Senaryo Tipi**:
- `hcp_honorarium` — konuşmacı/sunum ödemesi
- `advisory_board` — danışma kurulu toplantısı
- `clinical_investigator` — klinik araştırma investigator sözleşmesi
- `patient_data_processing` — hasta verisi işleme/transfer

**Her senaryo için output**:
- Risk skoru 0-100 (ağırlıklı: critical=40, high=20, medium=10, low=5)
- Framework-bazlı flag listesi (bulgu + öneri)
- Overall risk kategorisi (low/medium/high/critical)
- Required approvals (internal)
- Applicable SOPs

**Kullanım**:
```bash
python3 scripts/compliance-checker.py --example hcp-honorarium-risky       # 71/100 CRITICAL
python3 scripts/compliance-checker.py --example hcp-honorarium-clean       # 0/100 LOW
python3 scripts/compliance-checker.py --example advisory-board-risky       # Bodrum resort + aile
python3 scripts/compliance-checker.py --example advisory-board-clean       # İst konf + EFPIA uyumlu
python3 scripts/compliance-checker.py --example clinical-investigator      # FMV benchmark eksik
python3 scripts/compliance-checker.py --example patient-data-eu-to-tr      # GDPR SCC gerekli
python3 scripts/compliance-checker.py --framework-table                    # 7 framework detayı
python3 scripts/compliance-checker.py --list-scenarios                     # Tüm senaryolar
```

**Entegrasyon**: Mod 7 M&A DD (target compliance değerlendirme), Mod 10 Licensing (anti-bribery provisions), tüm operasyonel aktiviteler (congress/AB/HCP engagement pre-approval). Mahir'in Roche Group Audit sonrası corrective actions sürecine doğrudan destek.

---

## Gelecekteki araçlar (roadmap)

v1.8.0 ile script ekosistemi zirvesine ulaştı. v1.9.0+ için yeni yönler:

| Araç | Durum | Amaç |
|---|---|---|
| `pricing-benchmark-engine.py` | Fikir | IRP (International Reference Pricing) + AB 22 ülke pazarında yeni ilaç fiyatlandırma |
| `label-comparator.py` | Fikir | FDA USPI + EMA SmPC + TİTCK KÜB üç yönlü karşılaştırmayı otomatikleştiren |
| `ema-ct-analyzer.py` | Fikir | CTIS (Clinical Trials Information System) verilerini analiz eder (AB geçiş sonrası) |
| `amr-surveillance-tracker.py` | Fikir | GLASS + EARS-Net + TURLAB verilerini konsolide antimikrobiyal direnç takibi |

## Katkı

Yeni bir araç eklerken:

1. Script başına docstring (amaç + kullanım örneği + yazar + versiyon)
2. `--example` argümanıyla demo mod
3. Interactive + programatik (fonksiyon-bazlı) kullanım
4. Bağımlılıklar README'de listelensin
5. Test case'ler (scripts/tests/ içinde — ileri planlanıyor)
