# BIST Analist Kopilotu — Brifing Yazım Stili (House Style)

Bu belge, `bist-analist-kopilotu` becerisinin ürettiği brifingin **yazım, biçim ve uyumluluk** kurallarını tanımlar. Bu kurallar, `assets/brief-template.md` şablonunu yönetir: aşağıda tanımlanan bölümler, şablonun içereceği bölümlerdir.

> **Sınır (değişmez):** Brifing **karar-destek notudur**, yatırım tavsiyesi değildir. Kişiselleştirilmiş al/sat, kişiye özel hedef fiyat veya tahsis önerisi içermez.

---

## 1. Genel ton ve dil

- **Bilimsel Türkçe:** Açık, ölçülü, savlardan kaçınan; iddia-kanıt-sınır disipliniyle yazılır.
- **Yayıma hazır, kendi kendine yeten belge:** Okuyucu, dış bağlam veya araç çıktısı görmeden brifingi tam anlayabilmelidir.
- **Makine dili sızıntısı yok:** Brifing metninde **ham JSON, araç/fonksiyon adı, "MCP", "tool", betik dosya adı veya kod** geçmez. Her şey düz nesre veya tabloya çevrilir. (Örn. "fiyat verisi" denir; veri kaynağının teknik adı yazılmaz.)
- **Sayı disiplini:** Her sayı **birimiyle** (TL, %, kat/x, adet) ve **geçerlilik tarihiyle** (*as-of*) verilir. Çıplak sayı kullanılmaz.
- **Kaynak gösterimi:** Her dış olgu, **resmî adı + tarihiyle** atıf alır (ör. "Kamuyu Aydınlatma Platformu (KAP) bildirimi, 12 Haziran 2026"; "şirketin 1. çeyrek finansal tablosu").
- **Her sonuç eşli:** Her bulgu, bir **güven düzeyi** (Yüksek/Orta/Düşük) ve bir **karşıt senaryo** ile birlikte sunulur.

---

## 2. Brifing iskeleti (emit edilen başlıklar)

Beceri, dört kipte de aynı iskeleti üretir; kapsam kipe göre derinleşir/sadeleşir. `brief-template.md` şu bölümleri içerir:

| # | Başlık | İçerik |
|---|---|---|
| 1 | **Özet / karar-destek notu** | Tek paragraf öz: ana gözlem, baskın güven düzeyi, kilit belirsizlik. Tavsiye dili yok. |
| 2 | **Teknik görünüm** | Çok-zaman-dilimli okuma (1W eğilim → 1d kurulum); teknik duruş etiketi (güçlü yukarı … güçlü aşağı); momentum/oynaklık/hacim; ayrışma/yanlış-sinyal notu. Her vargı güven düzeyiyle. |
| 3 | **Temel görünüm** | Sektör-normalize değerleme/kârlılık/sağlık/büyüme; kalite kompoziti bandı; TL-enflasyon uyarısı. |
| 4 | **KAP & haber akışı** | Önemli bildirimler ve haberler, resmî ad + tarihle; önemlilik (materiality) ve duyarlılık değerlendirmesi. |
| 5 | **Makro çerçeve** | Rejim (risk-açık/kapalı, faiz, kur), endeks/sektör bağlamı. |
| 6 | **Senaryo matrisi** | Baz / Boğa / Ayı; her biri tetikleyici + geçersizleşme seviyesiyle (EOD kapanış bazlı). |
| 7 | **İzlenecekler / seviyeler** | Takip edilecek seviyeler, tarihler (bilanço/temettü/KAP), tetikleyiciler. Bunlar gözlem listesidir, emir değil. |
| 8 | **Feragat (disclaimer)** | Zorunlu kapanış feragatnamesi. |

Kipe göre vurgu:

- **Tek-hisse derin analiz:** Tüm bölümler dolu, en derin işlenir.
- **Haftalık tarama:** Özet + bölümlerin özlü hâli, hisse başına kısa kart; matris sadeleşir.
- **KAP olay yorumu:** 4. bölüm (KAP) merkezdedir; diğerleri olay bağlamında okunur.
- **İzleme listesi gözetimi:** Önceki duruma göre **değişimler** öne çıkar; izlenecekler/seviyeler genişler.

---

## 3. Her sonucu eşleme: güven + karşıt senaryo

Her önemli bulgu şu kalıpla sunulur:

> [Gözlem, sayı + birim + tarih ile]. **Güven: [Yüksek/Orta/Düşük].** **Karşıt senaryo:** [bu gözlemi geçersiz kılacak koşul/seviye].

Örnek (biçim örneği, gerçek veri değil):

> Haftalık eğilim yukarı dizilişte; günlük momentum sağlıklı bölgede (kapanış bazlı, 13 Haziran 2026). **Güven: Orta.** **Karşıt senaryo:** Günlük kapanış SMA50 altına sarkarsa eğilim zayıflar ve duruş nötrleşir.

---

## 4. Senaryo matrisi sunumu

Senaryo matrisi tablo olarak verilir:

| Senaryo | Tez | Tetikleyici | Geçersizleşme |
|---|---|---|---|
| Baz | … | … | … |
| Boğa | … | … | … |
| Ayı | … | … | … |

- Seviyeler **EOD kapanış bazlıdır**; gün-içi seviye iddiası yapılmaz.
- Olasılık **nitel** verilir ("baz daha olası, ayı kuyruk riski"); kesin yüzde atfı yok.

---

## 5. Üçüncü-taraf ve makine sızıntısı kuralları

- **Analist hedefleri/tavsiyeleri:** Yalnızca "doğrulanmamış piyasa beklentisi" çerçevesiyle, kaynak + tarihle. Becerinin vargısı gibi sunulamaz; hedef fiyat türetilemez.
- **Çeviri zorunluluğu:** Tüm teknik çıktı düz Türkçeye çevrilir; ham veri yapısı, araç adı, betik adı brifinge girmez.
- **Boşluk dürüstlüğü:** Alınamayan/eksik veri gizlenmez; "veri mevcut değil / doğrulanamadı" diye belirtilir.

---

## 6. "Yapma" listesi

Brifingte **asla** yapılmayacaklar:

- ❌ **Yatırım tavsiyesi dili:** "al", "sat", "topla", "gir/çık", "şu fiyattan alınmalı", kişiye özel hedef fiyat veya tahsis.
- ❌ **Uydurma rakam:** Kanıtla desteklenmeyen, kaynaksız üretilmiş sayı.
- ❌ **Kaynaksız iddia:** Resmî ad + tarih ile atıflanmamış olgu.
- ❌ **Gün-içi mikro-yapı iddiası:** Emir defteri, tik akışı, seans-içi anlık hareket; veri EOD/gecikmelidir.
- ❌ **Körlemesine ortalama:** Çelişen katmanları (güçlü teknik vs zayıf temel) gizleyip "orta" demek.
- ❌ **Güven/karşıt-senaryo eksik bulgu:** Her bulgu bu ikisini taşımalıdır.

> Nihai brifing, yayımdan önce uyumluluk denetiminden geçer (yardımcı denetleyici: `scripts/brief_lint.py`). Tavsiye dili, kaynaksız sayı, eksik güven düzeyi veya eksik karşıt senaryo işaretlenir.

---

## 7. Zorunlu kapanış feragatnamesi

Her brifing aşağıdaki feragatname ile (veya eşdeğer içerikle) kapanır:

> **Feragat:** Bu belge yalnızca **karar-destek** amaçlıdır ve **yatırım tavsiyesi değildir.** Kişiye özel al/sat yönlendirmesi, hedef fiyat veya portföy tahsisi içermez. Fiyat verileri **gün-sonu/gecikmeli** olup gün-içi hareketleri yansıtmaz. Üçüncü-taraf analist beklentileri doğrulanmamış bağlamdır. Yatırım kararları kişinin kendi sorumluluğundadır; profesyonel danışmanlık yerine geçmez.

---

*Karar-destek hatırlatması: Brifing gözlem ve senaryo sunar; tavsiye vermez. Her bulgu güven düzeyi ve karşıt senaryo ile, her sayı birim ve tarih ile yazılır.*
