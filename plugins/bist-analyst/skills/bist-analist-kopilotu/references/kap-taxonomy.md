# KAP Açıklama Taksonomisi ve Önemlilik Skorlaması — `bist-analist-kopilotu`

Bu belge, Kamuyu Aydınlatma Platformu (**KAP**) açıklama türlerinin yapısal bir
taksonomisini ve deterministik bir **önemlilik (materiality) skorlama rubriğini**
tanımlar. Belge, `scripts/kap_materiality.py` betiğinin uygulayacağı **spesifikasyon**
olarak tasarlanmıştır: kategori etiketleri, varsayılan önemlilik kademeleri ve
yönsel önyargılar (directional prior) burada **numaralandırılmış ve sabittir**.

> KAP açıklamaları `borsa` MCP'sinin `get_news` aracı üzerinden alınır;
> `scripts/kap_fetch.py` bu çıktıyı normalize eder. Bu belge **karar-destek**
> amaçlıdır; **yatırım tavsiyesi değildir**. Tüm fiyat verileri gün sonu (EOD) /
> gecikmelidir.

---

## 1. Tasarım ilkeleri

1. **Kategori = sabit anahtar.** Her açıklama, aşağıdaki tabloda tanımlı bir
   `category_id` (snake_case, ASCII) değerine sınıflandırılır. Sınıflandırılamayan
   açıklama `diger` kategorisine düşer ve düşük önemlilik tabanıyla işlenir.
2. **İki ayrı çıktı.** Sınıflandırma iki bağımsız şey üretir:
   (a) **varsayılan önemlilik kademesi** (kategori tabanlı ön kabul),
   (b) **hesaplanmış önemlilik skoru** (0–100, Bölüm 3 rubriği ile).
   Skor, kademeyi nihai olarak belirler; kategori tabanı yalnızca veri eksikse
   geri-düşüş (fallback) değeridir.
3. **Yönsel önyargı bir hipotezdir.** `directional_prior` alanı bir tahmin
   değil, tarihsel taban eğilimdir; nihai yön çağrısı `kap-reaction.md`
   prosedürüyle, sentiment ve teknik duruş birleştirilerek kurulur.
4. **Belirsizlik onurlu kodlanır.** Yön kestirilemiyorsa `belirsiz` kullanılır;
   sahte kesinlik üretilmez.

### 1.1 Kademe (tier) eşikleri

| Kademe | Skor aralığı | Anlam |
|---|---:|---|
| **Yüksek** | ≥ 67 | Fiyat/hacim üzerinde anlamlı etki beklenir; brifingde öncelikli |
| **Orta** | 34–66 | İzlenmeli; bağlama göre etki |
| **Düşük** | ≤ 33 | Rutin/işlemsel; düşük fiyat etkisi |

### 1.2 Yönsel önyargı kodları

| Kod | Anlam |
|---|---|
| `pozitif` | Tarihsel olarak fiyat-destekleyici eğilim |
| `negatif` | Tarihsel olarak fiyat-baskılayıcı eğilim |
| `notr` | Sistematik yön yok |
| `belirsiz` | Yön açıklamanın içeriğine/detayına bağlı, tek başına kestirilemez |

---

## 2. Açıklama taksonomisi

Aşağıdaki tablo `kap_materiality.py` için kanonik kategori sözlüğüdür. Sütunlar:
**Türkçe etiket**, kısa açıklama, varsayılan önemlilik kademesi tabanı, tipik
yönsel önyargı.

| `category_id` | Türkçe etiket | Açıklama | Varsayılan kademe | Yönsel önyargı |
|---|---|---|---|---|
| `finansal_rapor` | Finansal rapor / bilanço açıklaması | Çeyreklik/yıllık finansal tablo ve dipnotların kamuya açıklanması | Yüksek | `belirsiz` |
| `kar_payi` | Kâr payı (temettü) kararı | Yönetim kurulu/genel kurul temettü dağıtım kararı, oran ve takvim | Orta | `pozitif` |
| `bedelli_artirim` | Bedelli sermaye artırımı | Rüçhan hakkı kullandırılarak ücretli sermaye artırımı (nakit girişi, seyreltme) | Yüksek | `negatif` |
| `bedelsiz_artirim` | Bedelsiz sermaye artırımı | İç kaynaklardan bedelsiz pay dağıtımı (nominal seyreltme, nakit etkisi yok) | Orta | `pozitif` |
| `geri_alim` | Geri alım (pay-back) programı | Şirketin kendi paylarını geri alım programı başlatması/uygulaması | Orta | `pozitif` |
| `sozlesme_ihale` | Önemli sözleşme / ihale kazanımı | Maddi tutarlı sözleşme imzalanması veya ihale kazanılması | Yüksek | `pozitif` |
| `yatirim_tesvik` | Yatırım / kapasite / teşvik | Yeni yatırım, kapasite artışı, teşvik belgesi / yatırım teşviki | Orta | `pozitif` |
| `birlesme_devralma` | Satın alma–birleşme (M&A) | Şirket/varlık satın alma, birleşme, devralma işlemleri | Yüksek | `belirsiz` |
| `pay_devri` | Ortaklık / pay devri | Önemli pay sahipliği değişimi, ortaklık yapısı/pay devri bildirimi | Orta | `belirsiz` |
| `yonetim_degisikligi` | Yönetim değişikliği (CEO/CFO/YK) | Üst düzey yönetici veya yönetim kurulu üyeliği değişiklikleri | Orta | `belirsiz` |
| `denetim_gorusu` | Denetim görüşü / olumsuz görüş | Bağımsız denetçi görüşü; şartlı/olumsuz görüş veya görüş bildirmekten kaçınma | Yüksek | `negatif` |
| `dava_ceza_yaptirim` | Dava / idari para cezası / yaptırım | Maddi dava, idari para cezası, düzenleyici yaptırım | Orta | `negatif` |
| `uretim_durdurma` | Üretim durdurma / kapatma | Tesis/üretim hattı durdurma, faaliyet askıya alma, kapatma | Yüksek | `negatif` |
| `kredi_derecelendirme` | Kredi derecelendirme değişikliği | Derecelendirme kuruluşu not/görünüm güncellemesi | Orta | `belirsiz` |
| `yeni_urun_ruhsat` | Yeni ürün / ruhsat | Yeni ürün lansmanı, ruhsat/onay/patent alınması | Orta | `pozitif` |
| `faaliyet_raporu` | Faaliyet raporu | Dönemsel faaliyet raporu yayımı (çoğunlukla rutin) | Düşük | `notr` |
| `esas_sozlesme` | Esas sözleşme değişikliği | Esas sözleşme tadili (amaç-konu, sermaye tavanı, organ yapısı) | Düşük | `belirsiz` |
| `islem_sirasi_durdurma` | Payların işlem sırası durdurma | Borsa İstanbul tarafından pay işlem sırasının geçici durdurulması | Yüksek | `belirsiz` |
| `icsel_bilgi_erteleme` | İçsel bilgi ertelemesi | İçsel bilginin kamuya açıklanmasının ertelendiğinin/erteleme bitiminin bildirimi | Yüksek | `belirsiz` |
| `diger` | Diğer / sınıflandırılamayan | Yukarıdaki türlere atanamayan açıklamalar (geri-düşüş kategorisi) | Düşük | `notr` |

### 2.1 Yorum notları

- **`finansal_rapor` → `belirsiz`:** Yön, açıklanan sonucun beklentiye göre
  sapmasına bağlıdır; raporun varlığı tek başına yön taşımaz. Sürpriz sapma
  Bölüm 3'teki `surprise` faktörüyle yakalanır.
- **`bedelli_artirim` → `negatif`:** Seyreltme ve nakit ihtiyacı sinyali nedeniyle
  taban negatiftir; ancak yüksek-getirili bir yatırım için yapılan bedelli, niteliğe
  göre bu önyargıyı yumuşatabilir (bkz. `kap-reaction.md` işlenmiş örnek).
- **`bedelsiz_artirim` → `pozitif`:** Ekonomik değer yaratmaz (nominal seyreltme),
  fakat tarihsel olarak likidite/algı etkisiyle pozitif taban taşır; bu bir
  davranışsal eğilimdir, değer iddiası değildir.
- **`icsel_bilgi_erteleme` / `islem_sirasi_durdurma`:** Yön belirsiz; ancak
  **önemlilik tabanı yüksektir** çünkü bunlar genellikle maddi bir gelişmenin
  habercisidir.

---

## 3. Önemlilik skorlama rubriği (0–100)

`kap_materiality.py`, her açıklama için beş faktörlü ağırlıklı bir skor üretir.
Skor 0–100 aralığına ölçeklenir ve Bölüm 1.1 eşikleriyle kademelenir.

### 3.1 Faktörler ve ağırlıklar

Her faktör 0–100 arası bir alt-skor alır; ağırlıklı toplam nihai skordur.

| Faktör | `factor_id` | Ağırlık | Tanım |
|---|---|---:|---|
| İşletme büyüklüğüne oranı | `size_ratio` | 0.30 | İşlem/etki tutarının piyasa değeri, ciro veya özkaynağa oranı |
| Sürpriz / beklenti sapması | `surprise` | 0.25 | Açıklanan sonucun konsensüs/önceki döneme göre sapması |
| Kalıcılık | `persistence` | 0.20 | Etkinin tek seferlik mi yoksa sürdürülebilir/yapısal mı olduğu |
| Nakit-akışı etkisi | `cashflow` | 0.15 | Serbest nakit akışına doğrudan (giriş/çıkış) etki yönü ve büyüklüğü |
| Yönetişim sinyali | `governance` | 0.10 | Yönetim kalitesi, şeffaflık, kontrol/ortaklık yapısı üzerindeki sinyal |

> Ağırlıklar toplamı = 1.00. Bir faktör için veri yoksa o faktör **nötr (50)**
> kabul edilir ve `score_notes` alanında "veri yok → nötr" olarak işaretlenir
> (sahte yüksek/düşük skor üretilmez).

### 3.2 Alt-skor skalası (her faktör için)

| Bant | Alt-skor | Yorum |
|---|---:|---|
| Çok yüksek | 85–100 | Faktör güçlü ve net şekilde önemli |
| Yüksek | 67–84 | Belirgin etki |
| Orta | 34–66 | Ölçülü / belirsiz etki (50 = bilgi yok / nötr) |
| Düşük | 16–33 | Zayıf etki |
| İhmal edilebilir | 0–15 | Rutin / işlemsel |

### 3.3 Hesaplama

```
score = 100 * (
    0.30 * sub(size_ratio)/100 +
    0.25 * sub(surprise)/100 +
    0.20 * sub(persistence)/100 +
    0.15 * sub(cashflow)/100 +
    0.10 * sub(governance)/100
)

tier = "Yüksek"  if score >= 67
       "Orta"    if 34 <= score <= 66
       "Düşük"   if score <= 33
```

### 3.4 Kategori tabanlı ön-yükleme (priming)

Veri zayıf olduğunda (örn. tutar açıklanmamış), faktör alt-skorları Bölüm 2'deki
**varsayılan kademe** ile ön-yüklenir:

| Varsayılan kademe | Eksik faktör ön-skoru |
|---|---:|
| Yüksek | 70 |
| Orta | 50 |
| Düşük | 30 |

Böylece tutarı belirsiz ama doğası gereği yüksek-önemli bir açıklama (örn.
`islem_sirasi_durdurma`) düşük skora çakılmaz; aksine eksik veri nedeniyle
şişirilmiş bir kesinlik de iddia edilmez (`score_notes`'ta belirtilir).

### 3.5 Çıktı şeması (kap_materiality.py)

```json
{
  "category_id": "bedelli_artirim",
  "category_label": "Bedelli sermaye artırımı",
  "directional_prior": "negatif",
  "materiality_score": 78,
  "tier": "Yüksek",
  "factor_subscores": {
    "size_ratio": 90, "surprise": 70, "persistence": 60,
    "cashflow": 85, "governance": 55
  },
  "score_notes": ["size_ratio: artırım tutarı/PD ~ %40", "surprise: rüçhan iskontosu yüksek"]
}
```

---

## 4. Sınıflandırma anahtar kelimeleri (deterministik eşleme rehberi)

`kap_materiality.py` kategori atamasını metin üzerinde anahtar-kelime eşlemesiyle
yapar. Aşağıdaki liste başlangıç sözlüğüdür (genişletilebilir; çakışmada **en
yüksek varsayılan kademeli** kategori kazanır).

| `category_id` | Tetikleyici ifadeler (örnek) |
|---|---|
| `finansal_rapor` | "finansal rapor", "bilanço", "gelir tablosu", "konsolide", "çeyrek sonuç" |
| `kar_payi` | "kâr payı", "temettü", "dağıtım kararı", "nakit temettü" |
| `bedelli_artirim` | "bedelli", "rüçhan", "nakden artırım", "sermaye artırımı (bedelli)" |
| `bedelsiz_artirim` | "bedelsiz", "iç kaynaklardan", "geçmiş yıl kârları... sermayeye" |
| `geri_alim` | "geri alım", "pay geri alım", "back program" |
| `sozlesme_ihale` | "sözleşme imzal", "ihale", "kazanılmıştır", "sipariş alınmıştır" |
| `yatirim_tesvik` | "yatırım teşvik", "kapasite artış", "yeni tesis", "teşvik belgesi" |
| `birlesme_devralma` | "devralma", "satın alma", "birleşme", "hisse devralınması" |
| `pay_devri` | "pay devri", "ortaklık yapısı", "pay sahipliği değişikliği" |
| `yonetim_degisikligi` | "genel müdür", "CEO", "CFO", "yönetim kurulu üyeliği", "istifa", "atama" |
| `denetim_gorusu` | "bağımsız denetim", "denetçi görüşü", "olumsuz görüş", "şartlı görüş" |
| `dava_ceza_yaptirim` | "dava", "idari para cezası", "yaptırım", "soruşturma" |
| `uretim_durdurma` | "üretim durduruldu", "faaliyet askıya", "tesis kapat" |
| `kredi_derecelendirme` | "kredi derecelendirme", "rating", "not görünümü", "Moody's/Fitch/S&P/JCR" |
| `yeni_urun_ruhsat` | "yeni ürün", "ruhsat", "onay alındı", "patent", "lansman" |
| `faaliyet_raporu` | "faaliyet raporu" |
| `esas_sozlesme` | "esas sözleşme", "tadil", "sermaye tavanı değişikliği" |
| `islem_sirasi_durdurma` | "işlem sırası durdur", "sıra kapat", "Borsa İstanbul... durdurulmuştur" |
| `icsel_bilgi_erteleme` | "içsel bilgi", "erteleme", "açıklamanın ertelenmesi" |

> Eşleşme yoksa `diger`. Çoklu eşleşmede önceliklendirme: önce yüksek-kademe
> kategoriler değerlendirilir.

---

> Bu belgenin tanımladığı kategoriler, kademeler ve skor rubriği **karar-destek**
> içindir; **yatırım tavsiyesi, aracılık veya al/sat tavsiyesi değildir**.
