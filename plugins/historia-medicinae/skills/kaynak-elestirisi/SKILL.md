---
name: kaynak-elestirisi
description: "Quellenkritik skill'i — bir tarihsel kaynağın (özellikle sayısal olanın) ne söyleyip ne söyleyemeyeceğini belirler: ölüm nedeni serileri, ölüm cetvelleri, hastane ve tımarhane kayıtları, nüfus ve salgın istatistikleri, dönem raporları. Gözlemci zincirini yeniden kurar, kapsam dışı kalanı bulur, nicelleştirme için ICD10h çerçevesini dayatır. Kullanın: 'bu istatistik güvenilir mi', 'ölüm cetveli', 'mortalite serisi', 'hastane kaydı', 'kaynak eleştirisi', 'bu sayıyı kullanabilir miyim' sorularında — ve tarihsel bir sayı rapora girmeden ÖNCE."
argument-hint: "<kaynak veya veri serisi>"
allowed-tools: Read, Glob, Grep, WebFetch
disable-model-invocation: false
---

# Kaynak Eleştirisi (Quellenkritik)

Yükle: `../historia-medicinae/references/quellenkritik.md` ve
`../historia-medicinae/references/source-typology.md`.

## Beş soru — hiçbir veri bunlar sorulmadan kullanılmaz

1. **Kim üretti?** (hekim, kâtip, papaz, "searcher", memur, hasta)
2. **Hangi zorunlulukla?** (yasa, vergi, ücret, terfi, savunma)
3. **Hangi form dayattı?** (matbu form neyi sormaya zorluyor, neyi kaydettirmiyor)
4. **Kim kapsam dışı kaldı?** (yoksullar, köleler, kadınlar, kırsal, kayıt dışı ölümler)
5. **Nasıl korundu?** (hangi seri hayatta kaldı — **arşivin kendisi bir seçimdir**)

## Ölüm nedeni serileri — bağlayıcı bulgu

Tarihsel ölüm nedeni kaydı **patolojiyi değil, sertifikayı düzenleyenin bilgisini ve toplumsal
konvansiyonu** kodlar. İskoçya 1855–1949 ölçümünde "yaşlılık" (*old age*) bir hastalık değil,
**bilmemenin artık kategorisi** olarak işlev görmüştür (Reid et al. 2015,
DOI 10.1080/1081602X.2014.1001768).

> **Sonuç cümlesi (raporda geçmeli):** bir ölüm nedeni serisi *ölümlülüğün* değil, *tıbbî
> pratiğin* belgesidir.

## Nicelleştirme kuralı

Uzun serileri karşılaştırılabilir kılmak için **yayımlanmış bir kodlama çerçevesi** kullanılır —
modern ICD'ye *ad hoc* eşleme **değil**. Alanın standardı **ICD10h**'tır (İskoçya 1855–1973
üzerinde gösterildi, *Soc Hist Med* 2025, DOI 10.1093/shm/hkaf077). Çerçeve kullanılmıyorsa
sayı **karşılaştırmalı olarak sunulmaz**.

## Ölüm cetvelleri (bills of mortality)

Hem istatistiğin hem güvenilirlik sorununun başlangıcı. Graunt'un çıkarımları, veriyi üreten
**kilise kâtibi + "searcher"** zincirinden ayrılamaz (*J Med Biogr* 2022,
DOI 10.1177/09677720221079826). Gözlemci zinciri yeniden kurulmadan seri kullanılmaz.

## Kurumsal kayıtlar

Tımarhane/hastane defterleri büyük-N analize elverişlidir — **ama** kaydın kendi seçim mantığı
kurulduktan sonra: kim kabul edildi, kim yazdı, form neyi zorunlu kıldı (*Med Hist* 2017,
DOI 10.1017/mdh.2017.33).

> "Hastaların %40'ı X tanısı aldı" cümlesi, kabul kriteri ve form kodlaması açıklanmadan
> **anlamsızdır**.

## Dijital korpus çekincesi

Dijitalleştirilmiş metinde arama boş dönmesi yokluk kanıtı **değildir**: eski dijital *BMJ*'de
kelimelerin **%30'una varan** OCR hatası ölçülmüştür (Toon et al. 2016,
DOI 10.1017/mdh.2016.18). Anahtar-kelime frekansına dayalı her iddia bu çekinceyi taşır.

## Çıktı — kaynak künyesi bloğu

```
Kaynak: <ad, kurum, seri, tarih aralığı>
Üretici zinciri: <kim → kim → kim>
Zorunluluk: <yasa/ücret/...>
Form kısıtı: <ne sorulmuş, ne sorulmamış>
Kapsam dışı: <kim kayıtta yok>
Ne söyleyebilir: <...>
Ne SÖYLEYEMEZ: <...>
Nicelleştirilebilir mi: evet (ICD10h ile) / hayır (gerekçe)
```
