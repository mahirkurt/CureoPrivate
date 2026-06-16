# KAP Açıklama–Fiyat Tepkisi ve Olası-Yön Çağrısı — `bist-analist-kopilotu`

Bu belge, KAP açıklamalarının **gün sonu (EOD) veri rejiminde** fiyat ve hacim
tepkisine nasıl haritalandığını, tepki pencerelerini, "haber alımı/satışı"
uyarısını, hacim teyidi gereğini ve `sentiment_score` + önemlilik + teknik duruşun
birleştirilerek nasıl **açık güven seviyeli ve karşı-senaryolu bir olası-yön
çağrısına** dönüştürüleceğini tanımlar. Çıktı **karar-desteğidir**; **al/sat
talimatı değildir**.

> Tüm veriler gün sonu (EOD) / gecikmelidir. **Hiçbir gün-içi (intraday) iddia
> üretilmez**: ilk-dakika tepkisi, açılış sıçraması, seans-içi seviye, emir
> defteri/derinlik bu belgenin kapsamı dışındadır.

---

## 1. Tepki pencereleri (EOD rejiminde)

EOD veriyle yalnızca **kapanıştan kapanışa** tepki gözlenebilir. Tanımlı
pencereler:

| Pencere | Tanım | EOD ile gözlemlenebilir mi? |
|---|---|---|
| **Açıklama günü (T0)** | Açıklamanın yayımlandığı seansın kapanışı | Kısmen — yalnızca o günün kapanış değişimi; gün-içi tepki **değil** |
| **T+1** | Bir sonraki işlem günü kapanışı | Evet — ilk "temiz" EOD tepki penceresi |
| **T+1..T+5** | Açıklamayı izleyen ilk hafta | Evet — kalıcılık/teyit penceresi |

### 1.1 Yorum kuralları

- **T0 dikkati:** Açıklama seans içinde geldiyse, T0 kapanışı tepkiyi yalnızca
  kısmen yansıtır (haber öncesi işlemlerle karışır). Açıklama kapanıştan sonra
  geldiyse, **asıl tepki T+1'dedir**. Brifing bu ayrımı belirtmelidir.
- **T+1 = birincil okuma.** Tek bir temiz EOD sinyali için T+1 kapanış değişimi
  esas alınır.
- **T+1..T+5 = teyit/kalıcılık.** Tek günlük tepkinin sürüp sürmediği (devam mı,
  geri-dönüş mü) bu pencerede okunur. Tek günlük sıçramanın bir hafta içinde
  silinmesi, "haber satışı" davranışının işaretidir.

---

## 2. "Haber alımı / satışı" (buy-the-rumor / sell-the-news) uyarısı

Beklenen bir gelişme (örn. uzun süredir konuşulan temettü, beklenen ihale)
açıklandığında fiyat, **açıklama öncesinde** önyüklenmiş olabilir. Bu durumda:

- Pozitif bir açıklama bile T0/T+1'de **negatif** tepki verebilir (kâr realizasyonu).
- Bu nedenle olası-yön çağrısı her zaman **"beklenti zaten fiyatlanmış olabilir"**
  karşı-senaryosunu içermelidir.
- Sinyaller: açıklama öncesi anormal yükseliş + hacim artışı; açıklama sonrası
  yön tersine dönerse `haber_satisi_riski = yüksek` etiketlenir.

> Sürpriz/beklenti sapması (`kap-taxonomy.md` `surprise` faktörü) düşükse, fiyat
> tepkisi de zayıf olma eğilimindedir — "yeni bilgi" yoktur.

---

## 3. Hacim teyidi gereği

Bir fiyat hareketi, **hacim teyidi olmadan** zayıf sinyaldir.

| Durum | Yorum |
|---|---|
| Fiyat hareketi **+** ortalama-üstü hacim | Teyitli tepki — sinyal güçlenir |
| Fiyat hareketi **+** düşük hacim | Teyitsiz — temkinli; gürültü olabilir |
| Hacim sıçraması **+** yatay fiyat | İlgi arttı, yön belirsiz — izleme |

`get_historical_data` EOD hacmi, açıklama öncesi N-gün ortalamasıyla
karşılaştırılır. Teyit yoksa güven seviyesi bir kademe düşürülür.

---

## 4. Olası-yön çağrısının kurulması

Olası-yön çağrısı **üç girdinin** birleşimidir; bir al/sat emri değildir.

### 4.1 Girdiler

1. **Sentiment** — `scripts/sentiment_score.py` (sözlük tabanlı), açıklama
   metninden `[-1, +1]` skor.
2. **Önemlilik + yönsel önyargı** — `kap-taxonomy.md` / `kap_materiality.py`
   (`materiality_score` 0–100, `directional_prior`).
3. **Teknik duruş** — `get_technical_analysis` EOD göstergeleri (trend yönü,
   RSI aşırı alım/satım, hareketli ortalama dizilimi).

### 4.2 Birleştirme mantığı (deterministik iskelet)

```
yon_skoru = w1*sentiment_signed
          + w2*prior_signed*(materiality/100)
          + w3*teknik_signed

# sentiment_signed ∈ [-1,1]
# prior_signed: pozitif=+1, negatif=-1, notr/belirsiz=0
# teknik_signed ∈ [-1,1] (trend + momentum bileşimi)
# öneri: w1=0.35, w2=0.40, w3=0.25

likely_direction = "yukarı yönlü"  if yon_skoru >  esik_pos
                 = "aşağı yönlü"   if yon_skoru < -esik_neg
                 = "yön belirsiz"  aksi halde
```

### 4.3 Güven (confidence) seviyesi

Güven, sinyallerin **hizalanmasından** ve **veri kalitesinden** türetilir:

| Güven | Koşul |
|---|---|
| **Yüksek** | Üç girdi aynı yönde **ve** önemlilik Yüksek **ve** hacim teyitli |
| **Orta** | İki girdi hizalı veya önemlilik Orta; teyit kısmi |
| **Düşük** | Çelişen girdiler, düşük önemlilik, hacim teyidi yok, "haber satışı" riski |

> Güven asla "Yüksek"i geçemez; kesinlik iddiası (`%X kesin yükselir`) **yasaktır**.

### 4.4 Karşı-senaryo zorunluluğu

Her olası-yön çağrısı, **açıkça yazılmış bir karşı-senaryo** içermelidir:
çağrının yanlış çıkacağı en olası mekanizma (örn. "beklenti fiyatlanmış",
"seyreltme baskısı tepkiyi tersine çevirebilir", "hacim teyidi yok"). Karşı-senaryo
olmadan çağrı eksik kabul edilir ve `brief_lint.py` tarafından işaretlenir.

---

## 5. İşlenmiş örnek — güçlü bedelsiz vs. seyreltici bedelli

Aşağıdaki örnekler **karar-destek çerçevesindedir**; al/sat talimatı değildir.
Sayılar yöntem gösterimi içindir.

### 5.1 Güçlü bedelsiz sermaye artırımı

- **Açıklama:** Yüksek oranlı bedelsiz; sürpriz bileşeni var (beklenmiyordu).
- **Önemlilik:** `bedelsiz_artirim`, varsayılan Orta; sürpriz faktörü skoru
  ~60–66'ya çeker.
- **Yönsel önyargı:** `pozitif`.
- **Sentiment:** metin pozitif (~+0.4).
- **Teknik:** yükselen trend, RSI aşırı alımda değil → teknik_signed ~+0.5.
- **Hacim:** T+1'de ortalama-üstü → teyitli.
- **Çağrı:** *"T+1..T+5 penceresinde yukarı yönlü eğilim; güven: Orta–Yüksek."*
- **Karşı-senaryo:** Bedelsiz ekonomik değer yaratmaz; yükseliş davranışsal/
  likidite kaynaklıdır ve hızla geri verilebilir. Beklenti önceden fiyatlandıysa
  "haber satışı" görülebilir.

### 5.2 Seyreltici bedelli sermaye artırımı

- **Açıklama:** Büyük tutarlı, yüksek rüçhan iskontolu bedelli; nakit ihtiyacı sinyali.
- **Önemlilik:** `bedelli_artirim`, varsayılan Yüksek; `size_ratio` ve `cashflow`
  yüksek → skor ~78.
- **Yönsel önyargı:** `negatif`.
- **Sentiment:** metin nötr/negatif (~-0.2).
- **Teknik:** zayıf/yatay trend → teknik_signed ~-0.3.
- **Hacim:** T+1'de satış hacmiyle teyit.
- **Çağrı:** *"T+1'de aşağı yönlü baskı olasılığı; güven: Orta."*
- **Karşı-senaryo:** Bedelli **büyüme finansmanı** içinse (yüksek-getirili yatırım),
  seyreltme uzun vadede telafi edilebilir; güçlü ana ortak taahhüdü baskıyı
  sınırlayabilir. Bu durumda negatif önyargı yumuşar.

---

## 6. EOD sınırlarının açıkça beyanı

- Çıktıda fiyat geçtiği her yerde **"son kapanış (EOD)"** ifadesi kullanılır.
- "Açıklama anında fiyat şöyle hareket etti" türü **gün-içi anlatı yazılmaz**;
  yalnızca T0/T+1/T+1..T+5 kapanış pencereleri konuşulur.
- Emir defteri, derinlik, spread, seans-içi seviye iddiaları **üretilmez**.
- Tepki gözlemi her zaman geçmişe dönüktür; **gelecekteki tepki garanti edilmez**
  ("Geçmiş performans gelecekteki getirinin garantisi değildir").

---

> Bu belgenin tanımladığı tepki okuması ve olası-yön çağrısı **karar-destek**
> amaçlıdır; **yatırım danışmanlığı, aracılık veya al/sat tavsiyesi değildir**.
