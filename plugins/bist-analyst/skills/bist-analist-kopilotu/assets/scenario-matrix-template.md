<!--
  scenario-matrix-template.md — yeniden kullanılabilir senaryo matrisi bloğu.
  Her brifingde (özellikle Mod 1) doldurulur. Karar-destek çerçevesi: hedef
  fiyatlar tavsiye olarak değil, senaryo koşulu/geçersizlik seviyesi olarak verilir.
  "AL/SAT" etiketi kullanılmaz; yön "yukarı/aşağı/yatay" olarak ifade edilir.
-->

## Senaryo matrisi — {{SEMBOL}} ({{GG.AA.YYYY}} kapanışı, gün sonu/EOD)

| Senaryo | Tetikleyici | Teknik teyit | Temel / Makro koşul | Geçersizlik seviyesi | Güven |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **Baz** | {{en olası gidişat}} | {{ör. fiyat 20 günlük ort. üzerinde tutunur}} | {{ör. marjlar korunur; makro rejim yatay}} | {{S/R seviyesi}} | {{Orta}} |
| **Boğa (yukarı)** | {{olumlu katalizör}} | {{ör. direnç {{R1}} TL üzeri kapanış + hacim teyidi}} | {{ör. güçlü bilanço / gevşeme rejimi}} | {{ör. {{S1}} TL altına dönüş senaryoyu bozar}} | {{Düşük/Orta}} |
| **Ayı (aşağı)** | {{olumsuz katalizör}} | {{ör. destek {{S1}} TL altı kapanış}} | {{ör. marj baskısı / sıkılaştırma-stres}} | {{ör. {{R1}} TL üzeri geri kazanım senaryoyu bozar}} | {{Düşük/Orta}} |

**Doldurma kuralları**
- Her senaryo için en az bir **geçersizlik (invalidation) seviyesi** zorunludur — senaryo hangi koşulda çürür?
- Seviyeler gün sonu (EOD) kapanışına göre tanımlanır; gün-içi kırılım iddiası üretilmez.
- Güven; teknik + temel + makro + KAP katmanlarının uyumu ve veri tazeliğiyle orantılıdır (bkz. methodology.md).
- Senaryolar olasılık sırasına göre değil, **Baz → Boğa → Ayı** düzeninde sunulur; baz senaryo en olası gidişattır.
- Hiçbir hücre kişiye özel al/sat yönlendirmesi içermez; yalnızca koşul–sonuç ilişkisi kurar.

> Bu matris karar-destek amaçlıdır; yatırım tavsiyesi değildir.
