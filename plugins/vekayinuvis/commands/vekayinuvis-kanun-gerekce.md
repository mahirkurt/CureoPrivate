---
description: Bir kanunun TBMM-uyumlu, 5-katmanlı tarihî gerekçe bölümünü hazırlar (KANUN_GEREKÇESİ modu).
argument-hint: <kanun no/konusu, örn. "1219 sayılı Kanun reform teklifi">
---

`vekayinuvis` skill'ini **KANUN_GEREKÇESİ** modunda çalıştır.

Hedef: "$ARGUMENTS" için beş-katmanlı yasama tarihçesi (L1 klasik dönem → L2
Tanzimat-Islahat → L3 II. Meşrutiyet → L4 erken Cumhuriyet → L5 modern Türkiye)
kur. Düstûr I/II/III. Tertib + TBMM Zabıt Ceridesi + DergiPark/YÖKtez/TDV İA
triangülasyonu uygula.

references/kanun-gerekcesi-workflow.md **zorunlu** yükle. Sağlık mevzuatı
alanındaysa (1219, 6023, Hıfzıssıhha…) references/medical-history.md de yükle.
Bir katmanda kanıt boşluğu varsa şeffaf belirt; varsayım üretme. Çıktı,
TBMM İçtüzüğü m. 73-74 "Genel Gerekçe – Tarihî Çerçeve" formatına yerleşir ve
lex-sanitas ile composable'dır.
