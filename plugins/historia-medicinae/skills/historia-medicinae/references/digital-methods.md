# Dijital Yöntemler — ve zorunlu çekince

Dijital korpus kullanıldığında yüklenir.

---

## 1. Yöntem gerçektir, spekülatif değil

Tarihsel tıp korpuslarında metin madenciliği **yayımlanmış ve uygulanmış** bir yöntemdir:
*BMJ* (1840–) ve Londra Sağlık Memuru raporları üzerinde amaca özel bir anlamsal etiketleme
hattı kurulmuştur (Thompson et al. 2016, *PLoS ONE*, DOI 10.1371/journal.pone.0144717).

---

## 2. Bağlayıcı çekince — OCR ve varlık tipleme

Aynı proje ekibinin metodolojik değerlendirmesi iki sert kısıt ölçmüştür (Toon et al. 2016,
*Medical History*, DOI 10.1017/mdh.2016.18):

1. **OCR hatası:** eski dijitalleştirilmiş *BMJ*'de kelimelerin **%30'una varan** kısmı hatalı.
2. **Varlık tipleme direnci:** hastalık terimleri istikrarlı biçimde tiplenemez — çünkü
   kategoriye üyeliğin **kendisi** tarihsel olarak değişen şeydir.

> **Bundan çıkan tek kural:** dijitalleştirilmiş bir korpusta bir terimin bulunamaması
> **yokluk kanıtı değildir**. Anahtar-kelime frekansına dayalı her iddia bu çekinceyi taşır.

---

## 3. Uygulanabilir dijital hamleler (bu filoda)

| Hamle | Araç | Kısıt |
|---|---|---|
| Diyakronik bibliyometri (terim/konu yayılımı) | `openalex_analyze_trends` | Yalnız DOI'li literatür; monograflar yok |
| Ekol/etki haritası | `openalex_get_citation_graph` | Aynı kısıt |
| Sayfa-düzeyi tam-metin arama | `ottoman_search_within_manifest` (**yalnız Wellcome**) | Diğer kaynaklarda yok |
| Prosopografi grafiği | `anamnesis:upsert_triples` + `graph_neighbors` | Girdi kalitesi kadar iyi |
| Yapılandırılmış prosopografi sorgusu | Wikidata SPARQL (authless, ölçüldü) | Wikidata **P3**'tür — yönlendirme, kanıt değil |
| Belge-içi BM25 | `annas-reader:search_in_document` | Telif kapısı; yalnız analiz |

---

## 4. Nicel iddia yazım kuralı

Dijital yöntemle üretilmiş her sayı şu üçlüyle yazılır:
**(a)** korpusun kapsamı ve tarihi, **(b)** arama terimlerinin tam listesi, **(c)** OCR/kapsam
çekincesi. Üçü olmadan sayı raporda yer almaz.
