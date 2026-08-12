---
name: retrodiagnoz
description: "Geçmişteki bir hastalığa modern tanı etiketi yapıştırma (retrospektif tanı) kararını yürüten disiplin skill'i — yasak değil, dört kapılı karar prosedürü. Devralınan retro-etiketler için atıf soyağacı kontrolü, adlandırılmış birey için ayrı etik rejim, ve 'bunun yerine ne yapmalı' (Hacking döngü etkileri) dalı. Kullanın: 'bu hastalık aslında neydi', 'Kara Ölüm veba mıydı', 'X kişisinin hastalığı neydi', 'consumption tüberküloz mu', 'retrospektif tanı', 'aDNA', 'paleopatoloji' sorularında — ve bir tıp tarihi çıktısında modern tanı etiketi kullanmadan önce DAİMA."
argument-hint: "<tarihsel hastalık tarifi veya devralınan etiket>"
allowed-tools: Read, Glob, Grep, WebFetch
disable-model-invocation: false
---

# Retrodiagnoz — karar prosedürü

Yükle: `../historia-medicinae/references/retrospective-diagnosis.md` ve
`../historia-medicinae/references/historical-nosology.md`.

## Neden bu skill var

Bu, alanın imza tartışması **ve** bir dil modelinin en güçlü varsayılan hatasıdır: model,
"1348 Floransa'da şişlik ve ateş" tarifini görünce eğitimi gereği sessizce "veba" der. Bu bir
sonuç gibi görünür ama **kaynakta yoktur**.

Eleştiri, veri kalitesi sorunu değil **kategori karışıklığı** olduğunu söyler: modern hastalık
ontolojisi, o ontolojiye göre kurulmamış kaynaklara ithal edilir (Karenberg 2009,
PMID 19591388; Arrizabalaga 2002, PMID 17191369). Karşı taraf da yayımlanmıştır ve
paleopatoloji disiplinli biçimde uygular (Mitchell 2011, PMID 29539322).

> **Bu skill taraf tutmaz.** Yasaklamaz — **koşullu, işaretli, gerekçeli** kılar. Toptan yasak,
> kullanıcıyı prosedürün etrafından dolaştırır; amaç etiketin **görünür ve tartışılabilir**
> olmasıdır.

## Dört kapı

**K1 — Gereklilik.** Bu etiket olmadan soru cevaplanabiliyor mu? Cevaplanabiliyorsa **etiket
kullanılmaz.** Tarihsel soruların çoğu (nasıl deneyimlendi, adlandırıldı, yönetildi) modern tanı
gerektirmez.

**K2 — Kanıt türü.**

| Kanıt | Güç | Kısıt |
|---|---|---|
| aDNA / paleogenomik | Yüksek | Yalnız **örneklenen bireyler ve mezarlar**; salgına genellenmez |
| İskelet lezyon | Orta | Lezyon özgüllüğü sınırlı; ayırıcı tanı yazılır |
| Dönem klinik tarifi | **Düşük** | Metnin kendi kategorisi modern kategoriye eşlenmez |
| Epidemiyolojik örüntü | Düşük-orta | Destekleyici; tek başına yetmez |

Yalnız klinik tarife dayanan etiket **hipotezdir**.

**K3 — Ayırıcı tanı.** En az iki alternatif ve elenme gerekçesi yazılır. Alternatifsiz etiket
reddedilir.

**K4 — İşaretleme.** Geçen etiket iç kayıtta şu biçimde tutulur:

```
[RETRO-HİPOTEZ: <etiket> | kanıt: <tür> | alternatifler: <A, B> | güven: düşük/orta/yüksek]
```

Görünür metinde düzyazıya çevrilir: *"…bugünkü sınıflandırmayla X ile uyumlu okunabilir; ancak
bu bir hipotezdir — kanıt yalnız klinik tarifedir ve Y ile Z elenmiş değildir."*

## Devralınan etiket — atıf soyağacı

Bir retro-tanı literatürde dolaşıyorsa tekrarlamadan **önce izlenir**: ilk kim, hangi kanıtla?
Bu ölçülmüş bir olgudur — Hildegard von Bingen'in "migren"i özgün kanıt temelinden bağımsız
olarak bir yüzyıl atıfla çoğaldı (Foxhall 2014, DOI 10.1017/mdh.2014.28).

Prosedür: `openalex_get_citation_graph` / `scholar-gateway:semanticSearch` ile en erken savunuya
in → kanıtı K2'ye göre değerlendir → raporda yaz ("bu tanı ilk kez … tarafından … temelinde
önerilmiştir").

## Adlandırılmış birey — ek iki kapı

Ölmüş, adı bilinen bir bireye tanı koymak epistemik olduğu kadar etiktir: ölüm sonrası
mahremiyet, yanlışlanamazlık, torunlara/topluluğa itibar zararı (Muramoto 2014, PMID 24884777).

- **K5 — Amaç:** tarihsel bir soruyu mu çözüyor, yoksa merak mı gideriyor? İkincisiyse yapılmaz.
- **K6 — Yaşayan bağlam:** yaşayan akraba veya kimliklenmiş topluluk etkileniyorsa ETHICA
  modu devreye girer.

## Bunun yerine ne yapmalı

Etiket reddedildiğinde boşluk bırakılmaz. Hacking'in **döngü etkileri** çerçevesi kategoriyi
tarihsel nesne yapar (*Soc Hist Med* 2016, DOI 10.1093/shm/hkw083):

> "Bu neydi?" → **"Bu nasıl adlandırıldı, kim tarafından, hangi çıkarla, ve adlandırma neyi
> değiştirdi?"**

## Terminoloji aracı uyarısı (ölçülmüş)

`med-terminologies:find_equivalent` bu iş için **otomatik kullanılamaz**: doğru ICD-11
isabetleri `match_score: 0` alırken yanlış sözlüksel isabetler `0.833` alır;
**`consumption` → tüberküloz hiç dönmez** ("Oxygen Consumption" döner). Skor sıralamada
**kullanılmaz**; araç yalnız doğrulama için çağrılır. Küratörlü sözlük:
`historical-nosology.md`.

## Çıktı

Karar (etiket kullanıldı / kullanılmadı) · geçilen kapılar · kanıt türü · alternatifler ·
devralınmışsa soyağacı · güven düzeyi.
