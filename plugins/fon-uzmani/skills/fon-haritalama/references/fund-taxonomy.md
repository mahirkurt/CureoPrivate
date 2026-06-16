# fund-taxonomy.md — YAT + EMK Fon Taksonomisi (SPK)

## YAT — Yatırım Fonları (başlıca kategoriler)
| Kategori | Tanım | Tipik benchmark |
|---|---|---|
| Hisse Senedi Fonu | Portföyün ≥%80 hisse (Hisse Senedi Yoğun Fon) | XU100 / XUTUM |
| Borçlanma Araçları Fonu | Kamu/özel sektör tahvil-bono | KYD tahvil endeksleri |
| Para Piyasası Fonu | Kısa vadeli, düşük risk (repo/mevduat) | KYD O/N repo |
| Değişken Fon | Esnek tahsis (sınıf serbest) | karma |
| Karma Fon | Hisse+borçlanma karışık | karma |
| Katılım Fonu | Faizsiz/katılım esaslı | katılım endeksleri |
| Kıymetli Madenler Fonu | Altın/gümüş ağırlıklı | altın |
| Fon Sepeti Fonu (FSF) | Diğer fonlara yatırım | — |
| Serbest Fon | Nitelikli yatırımcı, esnek/kaldıraçlı | — (genelde kapsam dışı) |
| Gayrimenkul / Girişim Sermayesi (GYF/GSYF) | Likidite düşük | — |

## EMK — Emeklilik Yatırım Fonları
Standart / Katkı / Agresif / Dengeli / Muhafazakâr / Katılım / Altın / Hisse / Borçlanma /
Para Piyasası alt-tipleri. OKS (otomatik katılım) ve devlet katkısı uygunluğu ek özniteliktir.
FİGO (fon işletim gider oranı) ve FTGK (fon toplam gider kesintisi) EMK'ye özgü maliyet alanları.

## Kategori seçim mantığı
- Benchmark eşlemesi `piyasa-makro/references/benchmark-selection.md`'ye girdi olur.
- Risk profili → uygun kategori (allocation-doctrine.md).
- Kaldıraçlı/serbest fonlar varsayılan dışlanır (brief.exclusion).
