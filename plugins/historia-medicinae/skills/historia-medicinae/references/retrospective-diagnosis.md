# Retrospektif Tanı — karar prosedürü

**MORBUS ve EDITIO modlarında yüklenmesi ZORUNLUDUR.**
İlgili skill: `skills/retrodiagnoz/SKILL.md`.

---

## 0. Neden bu dosya var

Geçmişteki bir hastalığa modern tanı etiketi yapıştırmak (*retrodiagnosis*) tıp tarihinin imza
tartışmasıdır — ve bir dil modelinin **en güçlü varsayılan hatasıdır**. Model, "1348'de Floransa'da
şişlikler ve ateş" tarifini görünce eğitimi gereği sessizce "veba (*Y. pestis*)" der. Bu, bir
sonuç gibi görünen ama aslında **kaynakta olmayan** bir iddiadır.

---

## 1. Tartışmanın iki yakası — ikisi de öğretilir

| Yaka | Tez | Kaynak |
|---|---|---|
| **Eleştiri** | Retrodiagnoz veri kalitesi sorunu değil **kategori karışıklığıdır**: modern hastalık ontolojisi, o ontolojiye göre kurulmamış kaynaklara ithal edilir | Karenberg 2009, *Prague Med Rep* (PMID 19591388) |
| **Eleştiri (ontolojik formülasyon)** | Asıl soru "zaman içinde *aynı hastalık* ne demektir" sorusudur; daha iyi kaynakla çözülmez | Arrizabalaga 2002, *Asclepio* (PMID 17191369, DOI 10.3989/asclepio.2002.v54.i1.135) |
| **Savunma** | Aynı sayıda yayımlanan karşı makale: geçmişte hastalık **teşhis edilebilir**, düğüm kesilebilir | *Asclepio* 2002, DOI 10.3989/asclepio.2002.v54.i1.133 ("Identifying disease in the past: cutting the gordian knot") |
| **Disiplinli uygulama** | Paleopatoloji, tarihsel metin temelli retrodiagnozu **açık kısıtlarla kabul eder** — toptan reddetmez | Mitchell 2011, *Int J Paleopathol* (PMID 29539322, DOI 10.1016/j.ijpp.2011.04.002) |

> **Bu plugin taraf tutmaz.** Retrodiagnozu yasaklamaz; **koşullu, işaretli ve gerekçeli** kılar.
> Toptan yasak koymak kullanıcıyı prosedürün etrafından dolaşmaya iter; asıl amaç etiketin
> **görünür ve tartışılabilir** olmasıdır.

---

## 2. Karar prosedürü — dört kapı

Bir modern tanı etiketi ancak **dört kapıdan da geçerse** kullanılabilir.

### K1 — Gereklilik
*Bu etiket olmadan sorunun cevabı verilebiliyor mu?*
Verilebiliyorsa **etiket kullanılmaz**. Çoğu tarihsel soru (nasıl deneyimlendi, nasıl yönetildi,
nasıl adlandırıldı) modern tanı olmadan cevaplanır.

### K2 — Kanıt türü
| Kanıt | Güç | Not |
|---|---|---|
| aDNA / paleogenomik | **Yüksek** | Yalnız **örneklenen bireyler ve mezarlar** için; bütün bir salgına genellenemez |
| İskelet lezyon (paleopatoloji) | Orta | Lezyon özgüllüğü sınırlı; ayırıcı tanı yazılır |
| Klinik tarif (dönem metni) | **Düşük** | Metnin kendi kategorisi modern kategoriye eşlenmez |
| Epidemiyolojik örüntü (yayılım/mevsimsellik/ölümlülük) | Düşük-orta | Destekleyici; tek başına yeterli değil |

**Kural:** yalnız klinik tarife dayanan etiket **hipotezdir**, bulgu değildir.

### K3 — Ayırıcı tanı yazıldı mı
Tek bir etiket verilemez; **en az iki alternatif** ve neden elendikleri yazılır. Alternatifsiz
etiket reddedilir.

### K4 — İşaretleme
Geçen etiket şu biçimde yazılır:

```
[RETRO-HİPOTEZ: <modern etiket> | kanıt: <tür> | alternatifler: <A, B> | güven: düşük/orta/yüksek]
```

Görünür rapor gövdesinde bu, düzyazı olarak ifade edilir:
> "Tarif, bugünkü sınıflandırmayla X ile uyumlu okunabilir; ancak bu bir **hipotezdir** —
> kanıt yalnız klinik tarife dayanır ve Y ile Z elenmiş değildir."

---

## 3. Devralınan etiket — atıf soyağacı kontrolü

Bir retro-tanı literatürde zaten dolaşıyorsa, **tekrarlamadan önce izlenir**: ilk kim, hangi
kanıtla ileri sürdü?

Bu boş bir titizlik değil, ölçülmüş bir olgudur: Hildegard von Bingen'in "migren"i, özgün
kanıt temelinden bağımsız olarak bir yüzyıl boyunca atıfla çoğalmıştır (Foxhall 2014,
*Medical History*, DOI 10.1017/mdh.2014.28).

**Prosedür:** `openalex_get_citation_graph` veya `scholar-gateway:semanticSearch` ile etiketin
en erken savunusuna in → o çalışmanın kanıtını K2 tablosuna göre değerlendir → sonuç raporda
yazılır ("bu tanı ilk kez … tarafından … temelinde önerilmiştir").

---

## 4. Adlandırılmış birey — ayrı ve daha katı rejim

Ölmüş, **adı bilinen** bir bireye tanı koymak epistemik olduğu kadar etik bir sorundur: ölüm
sonrası mahremiyet, yanlışlanamazlık ve torunlara/topluluğa itibar zararı (Muramoto 2014,
*Philos Ethics Humanit Med*, PMID 24884777, DOI 10.1186/1747-5341-9-10).

Ek kapılar:
- **K5 — Amaç:** tanı, tarihsel bir soruyu mu çözüyor yoksa yalnız merak mı gideriyor?
  İkincisiyse yapılmaz.
- **K6 — Yaşayan bağlam:** yaşayan akrabalar veya kimliklenmiş bir topluluk etkileniyorsa
  ETHICA modu devreye girer (`ethics-of-atrocity.md`).

---

## 5. Yapıcı alternatif — "bunun yerine ne yapmalı"

Retrodiagnoz reddedildiğinde boşluk bırakılmaz. Alanın önerdiği güçlü seçenek Hacking'in
**"döngü etkileri" / "insan yapmak"** çerçevesidir: tanı kategorileri betimledikleri insanları
da dönüştürür; kategorinin **kendisi** tarihsel nesnedir (*Social History of Medicine* 2016,
DOI 10.1093/shm/hkw083 — Münchhausen sendromu üzerinden tarihselleştirme).

Pratikte:
- "Bu neydi?" sorusu → **"Bu nasıl adlandırıldı, kimin tarafından, hangi çıkarla, ve
  adlandırma neyi değiştirdi?"**
- Kaynağın terimi analiz nesnesi olur, çeviri hedefi değil.

---

## 6. Kaba örnek — Kara Ölüm

- aDNA, belirli mezarlarda *Y. pestis* varlığını **doğrular** (K2 yüksek, ama örneklenen
  bireyler için).
- Buradan "1347–1351'in **her yerinde ve her dalgasında** veba" sonucu **çıkmaz** (K2 → K3).
- Küresel çerçeveye taşındığında yöntem maliyetleri açıkça tartışılmıştır
  (*The Medieval Globe* 2015, DOI 10.17302/tmg.1-1.3).
- Doğru yazım: örneklenen bölgeler için etiket + diğer bölgeler için "belirsiz, aday etkenler…"

---

## 7. Terminoloji köprüsünün güvenilmezliği

`med-terminologies:find_equivalent` bu iş için **otomatik olarak kullanılamaz** (ölçülmüş):
doğru ICD-11 isabetleri `match_score: 0` alırken yanlış sözlüksel isabetler `0.833` alır;
`consumption` → tüberküloz **hiç dönmez**. Ayrıntı ve küratörlü sözlük:
`historical-nosology.md`. Araç yalnız **doğrulama** için çağrılır, öneri üretmek için değil.
