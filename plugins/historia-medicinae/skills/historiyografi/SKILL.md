---
name: historiyografi
description: "HISTORIOGRAPHIA modu — bir tıp tarihi konusunun nasıl yazıldığını inceler: hangi ekoller, hangi tartışmalar, hangi pozisyon canlı hangisi aşıldı. Sosyal tıp tarihi, Foucault/biyopolitika, hastanın bakışı (heteroglossia), postkolonyal tıp, küresel sağlık tarihi, inşacı kategori tarihi, cinsiyet ve engellilik tarihi. Kullanın: 'bu konu nasıl yazıldı', 'literatür tartışması', 'hangi ekol', 'tarihyazımı', 'historiography', 'alanın durumu' sorularında."
argument-hint: "<konu veya ekol>"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# HISTORIOGRAPHIA — Tarihyazımı İncelemesi

Flagship protokolü `HISTORIOGRAPHIA` moduyla çalıştır.

## Zorunlu yükleme

```
view ../historia-medicinae/references/historiography-schools.md   # ZORUNLU
view ../historia-medicinae/references/kuresel-cerceve.md
```

## Konumlandırma prosedürü (dört soru)

1. **Fail kim?** Anlatının öznesi hekim mi, kurum mu, hasta mı, devlet mi?
2. **Hastalık nasıl ele alınıyor?** Değişmez biyolojik varlık mı, tarihsel çerçevelenmiş
   kategori mi?
3. **Değişim nasıl açıklanıyor?** Keşif/dâhi · toplumsal talep · kurumsal çıkar · iktidar
   ilişkisi.
4. **Kim kapsam dışı?** Hangi coğrafya, sınıf, cinsiyet, ırk anlatıya girmiyor?

## Güncellik yargısı — bu modun asıl katkısı

Ekolleri listelemek yetmez; hangisinin **bugün canlı**, hangisinin **yeniden formüle edilmiş**,
hangisinin **çekişmeli** olduğu söylenir. `historiography-schools.md` tablosu bunu taşır:

- "Hastanın bakışı" → **canlı ama yeniden formüle edilmiş** (hermeneutikten heteroglossia'ya).
  1985 formülasyonunu güncel diye aktarmak hatadır.
- Postkolonyal tıp tarihi → **canlı** (Anderson 1998 hâlâ ölçüt).
- Küresel sağlık tarihi → **canlı ve programatik** (BHM 2015 tüzüğü).
- Foucaultcu eksen → **çekişmeli**, ne kanonik ne ölü.
- Whig/ilerlemeci → **aşıldı** (ama LLM çıktısında sürekli geri sızar — çıktıyı buna karşı tara).

## İki ölçülmüş boşluk

**Cinsiyet tarihi** ve **engellilik tarihi** için kurulum turunda metodolojik derleme düzeyinde
kaynak bulunamadı. Bu eksenler çalışılıyorsa **hedefli yeniden tarama zorunludur** ve sonuç
`historiography-schools.md`'ye işlenir. Boşluk dürüstçe beyan edilir.

## Araçlar

`openalex_get_citation_graph` (ekol kümeleri) + `openalex_analyze_trends` (terim yayılımı) +
`consensus` (tartışmalı iddia sentezi) + `scholar-gateway` (pasaj-düzeyi tez doğrulama) +
`paper-search` (monograf katmanı).

⚠️ Atıf grafı yalnız DOI'li literatürü görür; alanın kurucu monografları (Rosenberg 1992,
Arnold 1993, Porter 1985) grafta **yoktur** — ekol haritası yalnız grafa dayandırılamaz.

## Çıktı

G0 manifestosu · ekol tablosu + güncellik yargısı · tartışmanın bugünkü düğümü · boşluk beyanı.
