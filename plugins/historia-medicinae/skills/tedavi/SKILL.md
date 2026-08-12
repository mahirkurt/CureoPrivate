---
name: tedavi
description: "THERAPEUTICA modu — tedavi, ilaç, cerrahi teknik ve tıbbî teknolojinin tarihi: materia medica, kan alma, çiçek aşısı ve variolasyon, anestezi, antisepsi, aspirin/salvarsan/insülin/penisilin, stetoskop, röntgen, diyaliz, transplantasyon. Kullanın: 'X ilacının tarihi', 'anestezinin keşfi', 'aşının tarihi', 'materia medica', 'cerrahi tarihi', 'tıbbî alet tarihi', 'ilaç geliştirme tarihi' sorularında."
argument-hint: "<tedavi/ilaç/teknoloji> [dönem] [coğrafya]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# THERAPEUTICA — Tedavi, İlaç ve Teknoloji Tarihi

Flagship protokolü `THERAPEUTICA` moduyla çalıştır.
Yükle: `historical-nosology.md` · `quellenkritik.md` · `kuresel-cerceve.md` · `source-typology.md`.

## Dört soru

1. **Nereden geldi?** Bitkisel/mineral kaynak, yerli bilgi, tesadüf, sistematik arama.
   ⚠️ Yerli bilginin kaynak olduğu vakalarda (kinin, kürar, birçok materia medica) **kim
   biliyordu, kim kredi aldı** sorusu sorulur — postkolonyal kontrol.
2. **Nasıl meşrulaştı?** Hangi kanıt standardı? (otorite, vaka serisi, sayısal yöntem,
   kontrollü deneme). Kanıt standardının kendisi tarihseldir.
3. **Nasıl yayıldı?** Kurum, ticaret, ordu, misyon, patent, reklam, ruhsat rejimi.
4. **Neden terk edildi (varsa)?** Terk ediliş çoğu kez "yanlış olduğu anlaşıldı"dan daha
   karmaşıktır — piyasa, ikame, regülasyon.

## Ruhsat/regülasyon ekseni

20. yüzyıl için yasama bandı birincil kaynaktır: `health-policy` (GovInfo/Congress — 1906 Pure
Food and Drugs Act, 1938 FD&C, 1962 Kefauver-Harris), `uk-legal` (Hansard), TR için
`mevzuat`/`tbmm`/`resmigazete`.

⚠️ **Çağdaş klinik etkililik sorulursa** (bu tedavi bugün işe yarıyor mu) → `evidentia`
delegasyonu. Bu plugin tarih yazar, klinik kanıt derlemez.

## Terminoloji

Tarihsel ilaç/bitki adları modern karşılığa **otomatik çevrilmez**; `historical-nosology.md`
kuralları ve `med-terminologies`'in ölçülmüş güvenilmezliği geçerlidir (`match_score`
kullanılmaz).

## Getirim

openalex + pubmed-epmc (`Historical Article`) · IIIF (herbal, farmakope, alet katalogları —
⚠️ **BHL anahtarı yok**, herbal/materia medica katmanı bu yüzden dar: manifestoda `gap`) ·
paper-search · openathens → annas-reader · yasama bandı.

## Çıktı

G0 manifestosu · kanıt standardının tarihselliği görünür · yerli bilgi kredisi sorusu yanıtlı.
