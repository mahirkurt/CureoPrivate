# Tarihsel Nozoloji — terim sözlüğü ve terminoloji tuzağı

MORBUS, EDITIO ve CONCEPTUS modlarında yüklenir.

---

## 1. Ölçülmüş tuzak — `find_equivalent` skorlaması TERS çalışır

`med-terminologies:find_equivalent` tarihsel hastalık adlarını modern kodlara eşlemek için
kullanılabilir görünür. **Ölçüm (2026-08-11) bunu çürüttü:**

| Sorgu | Dönen | Doğru mu | `match_score` |
|---|---|---|---|
| `dropsy` | MG29.Z Oedema + ME04.Z Ascites | ✅ doğru | **0** |
| `apoplexy` | 8B20 Stroke | ✅ doğru | **0** |
| `apoplexy` | "Pituitary Apoplexy" | ❌ yanlış | **yüksek** |
| `consumption` | 3B20 DIC, 5A00.2Y hipotiroidi, MeSH "Oxygen Consumption" | ❌ **tüberküloz HİÇ dönmedi** | 0.833 |

> **Kural:** `match_score` sıralamada veya eşikte **KULLANILMAZ**. Skor, doğruluğun tersi yönde
> çalışmaktadır — sözlüksel benzerliği ödüllendirir, kavramsal doğruluğu değil.
>
> Araç yalnız **doğrulama** için çağrılır ("bu modern kodun karşılığı gerçekten bu mu"),
> **öneri üretmek** için değil. Her eşleme insan denetimine tabidir.
>
> SNOMED CT lisanssızdır → `snomed_*` araçları devre dışıdır.

Bu yüzden aşağıdaki **küratörlü sözlük** birincil kaynaktır.

---

## 2. Küratörlü sözlük — terim, dönem, dikkat

Aşağıdaki eşlemeler **hipotezdir**, tanı değildir (bkz. `retrospective-diagnosis.md` K4).

| Tarihsel terim | Dil/dönem | Yaygın modern okuma | ⚠️ Dikkat |
|---|---|---|---|
| *consumption*, *phthisis* | İng./Yun., erken modern–19. yy | Tüberküloz | Ölçülen boşluk: araç bunu **bulamıyor**. Ayrıca kilo kaybıyla giden her kronik hastalığı kapsayabilir |
| *dropsy*, *hydrops* | İng./Lat. | Ödem/asit — **bir semptom, hastalık değil** | Kalp/böbrek/karaciğer yetmezliği ayrımı kaynakta yoktur |
| *apoplexy* | Yun./Lat. | İnme | Ani ölümlerin genel kategorisi olarak da kullanılmıştır |
| *ague* | İng., ortaçağ–18. yy | Sıtma (aralıklı ateş) | Her aralıklı ateş sıtma değildir |
| *bloody flux* | İng. | Dizanteri | Etken ayrımı (amip/basil) kaynakta yok |
| *quinsy* | İng. | Peritonsiller apse | — |
| *falling sickness*, *morbus sacer* | İng./Lat. | Epilepsi | Dinî-kültürel yükü ayrı analiz nesnesidir |
| *green sickness*, *chlorosis* | 16.–19. yy | Demir eksikliği anemisi (?) | **Tartışmalı**; toplumsal cinsiyet tarihinin klasik vakası — kategori tarihi olarak okunmalı |
| *hysteria* | Yun.–20. yy | — | **Eşlemeye çalışılmaz**; kategorinin kendisi tarihsel nesnedir (Hacking çerçevesi) |
| *neurasthenia* | 19.–20. yy | — | Aynı; kültürel olarak yerel |
| *sweating sickness* | İng., 1485–1551 | **Bilinmiyor** | Etken belirlenememiştir; "muhtemelen hanta virüs" iddiası hipotezdir |
| *plague*, *pestis*, *tâ'ûn*, *vebâ* | çok dilli | *Y. pestis* | Terimler dönemde **her büyük salgın** için de kullanıldı; bkz. Kara Ölüm örneği |
| *cholera morbus* | 18.–19. yy | — | 19. yy öncesi "cholera" **asiyatik kolera değildir**; genel ishalli hastalık |
| *lues*, *pox*, *frengi* | 16. yy+ | Sifiliz | Adlandırma milliyetçi ("Fransız hastalığı") — adın kendisi kanıttır |
| *marasmus*, *tabes* | Lat. | Zayıflama sendromları | Semptomatik kategori |
| *childbed fever* | 18.–19. yy | Puerperal sepsis | Semmelweis tartışmasının nesnesi |
| *sıtma*, *humma*, *ishal-i müzmin* | Osm. Türkçesi | — | Osmanlı tıp terminolojisi → `turkiye-layer.md` ve `vekayinuvis` |

**Sözlük tamam değildir ve olamaz.** Yeni bir terimle karşılaşıldığında prosedür: (1) terimin
dönem içi kullanımını birincil/ikincil kaynaktan belirle, (2) modern okuma **ancak** dört kapıdan
geçerse ekle, (3) bu tabloya bir satır olarak öner.

---

## 3. Terminoloji kayması ve arama

Bir terim dönemde kullanılmıyorsa arama onu bulamaz — ve **boş sonuç yokluk kanıtı değildir**.
Pratik: modern terimle **birlikte** dönem terimleri ve yerel dildeki karşılıkları da aranır
("tuberculosis" **ve** "phthisis" **ve** "consumption" **ve** "verem").

---

## 4. Nicelleştirme

Tarihsel hastalık kategorilerini sayısal olarak karşılaştırmak gerekiyorsa **ICD10h** gibi
yayımlanmış bir çerçeve kullanılır, modern ICD'ye *ad hoc* eşleme değil
(bkz. `quellenkritik.md` §2).
