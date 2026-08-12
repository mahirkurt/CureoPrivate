---
name: kavram
description: "CONCEPTUS modu — tıbbî fikir ve kavramların tarihi: humoralizm, miyazma–kontenjyonizm tartışması, mikrop teorisine geçiş, hücresel patoloji, klinik bakışın doğuşu, normal/patolojik ayrımı, kanıta dayalı tıbbın kuruluşu, tanı kategorilerinin tarihselliği. Kullanın: 'germ teorisi ne zaman kabul edildi', 'humoral teori', 'miyazma', 'hastalık kavramı', 'X tanısının tarihi', 'tıbbileşme', 'klinik bakış', 'kavram tarihi' sorularında."
argument-hint: "<kavram/teori> [dönem] [coğrafya]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# CONCEPTUS — Fikir ve Kavram Tarihi

Flagship protokolü `CONCEPTUS` moduyla çalıştır.

## Zorunlu yüklemeler

```
view ../historia-medicinae/references/historiography-schools.md
view ../historia-medicinae/references/quellenkritik.md
view ../historia-medicinae/references/historical-nosology.md
view ../historia-medicinae/references/kuresel-cerceve.md
```

## Yöntem: kavramın kendisi araştırma nesnesidir

Soru "bu kavram doğru muydu" değil, **"bu kavram ne yaptı"**dır: neyi görünür kıldı, neyi
görünmez, hangi pratiği mümkün kıldı, kimin otoritesini kurdu.

Güçlü çerçeve — Hacking'in **döngü etkileri**: bir tanı kategorisi adlandırdığı insanları da
dönüştürür; kategori ile insanlar birbirini yeniden şekillendirir (*Soc Hist Med* 2016,
DOI 10.1093/shm/hkw083). Bu çerçeve aynı zamanda retrospektif tanıya **yapıcı alternatiftir**.

## Dört adımlı kavram tarihi

1. **Terim tarihi** — kelime ne zaman, hangi dilde, hangi anlamda görünüyor? Anlam kayması
   izlenir (`historical-nosology.md`).
2. **Tartışma haritası** — kavram kime karşı savunuldu? Bir kavram çoğu kez bir **polemiğin**
   ürünüdür (kontenjyonizm ↔ antikontenjyonizm; hümoral ↔ solidist; laboratuvar ↔ klinik).
3. **Kurumsal taşıyıcı** — kavramı hangi kurum taşıdı (üniversite kürsüsü, laboratuvar, dergi,
   meslek örgütü, devlet dairesi)? Fikirler kurumsuz yayılmaz.
4. **Pratik sonuç** — kavram hangi müdahaleyi meşru kıldı? (kan alma, karantina, dezenfeksiyon,
   asepsi, zorunlu bildirim).

## İki yasak

- **Teleoloji.** "Nihayet mikrop teorisine ulaştılar" yazılmaz. Geçiş tarihlendirilirken
  **kimin, nerede, ne zaman** kabul ettiği ayrı ayrı gösterilir; kabul her yerde aynı anda
  olmamıştır.
- **Difüzyonizm.** Avrupa-dışı kavramsal gelenekler "henüz oraya varmamış" olarak sunulmaz
  (`kuresel-cerceve.md`).

## Getirim planı

- **Diyakronik bibliyometri:** `openalex_analyze_trends` (terim/konu yayılımı) +
  `openalex_get_citation_graph` (ekol haritası). ⚠️ Yalnız DOI'li literatürü görür; alanın
  kurucu monografları grafta **yoktur**.
- **Birincil metin:** IIIF (dönem risaleleri, ders kitapları) — Wellcome'da sayfa-içi arama ile
  terimin **metin içindeki** geçişleri bulunabilir; bu, terim tarihi için filodaki en güçlü araç.
- **Tam metin:** openathens → annas-reader.
- **Tarihyazımı:** consensus + scholar-gateway (pasaj-düzeyi tez doğrulama).

## Çıktı

G0 manifestosu · terim tarihi ayrı bölüm · tartışma haritası · kavramın pratik sonucu ·
tarihyazımsal konum (hangi ekol).
