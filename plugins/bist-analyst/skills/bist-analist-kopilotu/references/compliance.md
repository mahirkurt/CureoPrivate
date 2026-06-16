# Uyum ve Sınırlar (Compliance) — `bist-analist-kopilotu`

Bu belge, BIST analist ko-pilotunun **yönetişim ve uyum** çerçevesidir. Skilin
ürettiği her brifing bu belgeye tabidir. Temel sınır tektir ve müzakere edilemez:

> **KARAR-DESTEK, yatırım tavsiyesi DEĞİLDİR.**

Belge; SPK yatırım danışmanlığı sınırını, üçüncü-taraf hedef/öneri ele alımını,
uydurma sayı/intraday iddia yasaklarını, KVKK ve kaynak kullanım koşullarına
saygıyı, "tavsiye diline çevirme" rehberini ve `brief_lint.py` tarafından zorunlu
kılınan denetim listesini tanımlar.

---

## 1. Kanonik feragat (disclaimer) bloğu

Her brifing, **aşağıdaki metni birebir (verbatim)** içeren bir feragat bloğuyla
**sona ermelidir**. `brief_lint.py` bu metni dize-eşlemesiyle (string-match)
denetler; metin değiştirilemez, kısaltılamaz veya yeniden ifade edilemez.

```
Bu içerik yalnızca bilgilendirme ve karar-destek amaçlıdır; yatırım danışmanlığı, aracılık veya al/sat tavsiyesi niteliği taşımaz. Veriler büyük ölçüde gün sonu (EOD) ve gecikmeli olabilir; gün içi emir defteri/derinlik bilgisi içermez. Yatırım kararları; kişinin kendi risk profili, bağımsız araştırması ve gerektiğinde SPK lisanslı bir yatırım danışmanına danışılarak alınmalıdır. Geçmiş performans gelecekteki getirinin garantisi değildir.
```

---

## 2. SPK yatırım danışmanlığı sınırı

Türkiye'de yatırım danışmanlığı, Sermaye Piyasası Kurulu (SPK) tarafından lisansa
ve yetkiye bağlı, **kişiye özel** bir faaliyettir. Bu skil yetkili bir yatırım
kuruluşu değildir; dolayısıyla:

- **Kişiselleştirilmiş çağrı üretilmez.** "Sizin için X al / Y sat", "şu fiyattan
  gir", "portföyünüzü şöyle kurun" türü ifadeler **yasaktır**.
- **Genel, kaynaklı, koşullu bağlam** sunulur; karar kullanıcıya bırakılır.
- Kişiye özel karar gereken her noktada **SPK lisanslı bir yatırım danışmanına
  yönlendirme** yapılır (feragat bloğunda yer alır).

---

## 3. Üçüncü-taraf hedef ve öneriler

`get_analyst_data` ve benzeri kaynaklardan gelen analist hedef fiyatları, "al/tut/sat"
önerileri ve kurum tavsiyeleri:

- Yalnızca **"doğrulanmamış / üçüncü-taraf"** nötr bağlam olarak yüzeye çıkarılır.
- **Asla** skilin yönlendirmesi, onayı veya hedefi olarak sunulmaz.
- Daima kaynak ve (varsa) tarih etiketiyle aktarılır.
- "Analistler X diyor" cümlesi bir **gözlem** olarak verilir; "öyleyse X yapın"
  çıkarımına **dönüştürülmez**.

> Bkz. `data-sources.md` Bölüm 3 — Veri Güveni Merdiveni, Seviye 4
> (Doğrulanmamış / üçüncü-taraf).

---

## 4. Yasaklar

| Yasak | Açıklama |
|---|---|
| **Uydurma sayı** | Kaynaktan teyit edilemeyen fiyat, oran, hedef veya metrik üretilemez. Veri yoksa "veri alınamadı" denir. |
| **Kaynaksız iddia** | Her maddi iddia izlenebilir bir kaynağa (KAP/TCMB/MCP aracı + tarih) bağlanır. |
| **Intraday mikroyapı iddiası** | Emir defteri, derinlik, bid/ask spread, seans-içi seviye, ilk-dakika tepkisi iddiaları yasaktır (veri EOD'dir). |
| **Kesinlik iddiası** | "%X kesin yükselir", "garanti getiri" türü ifadeler yasaktır. |
| **Kişiselleştirilmiş emir** | Bölüm 2 — kişiye özel al/sat talimatı yasaktır. |

---

## 5. KVKK ve kaynak kullanım koşulları

- **KVKK:** Kişisel veri toplanmaz, profillenmez, saklanmaz. Kullanıcının portföy/
  finansal durumu kişisel veri olarak işlenmez; analiz anonim ve genel kalır.
- **Kaynak kullanım koşulları:** `borsa` MCP, KAP, TCMB/EVDS ve üçüncü-taraf
  kaynakların kullanım koşullarına ve atıf gereklerine uyulur. İçerik, kaynağın
  izin verdiği ölçüde ve atıfla aktarılır; toplu kazıma/yeniden yayım yapılmaz.

---

## 6. "Tavsiye diline çevirme" rehberi

Kullanıcının doğrudan tavsiye isteyen ifadeleri, **karar-destek çerçevesine**
yeniden yazılır. Niyet reddedilmez; biçim dönüştürülür.

| Kullanıcı ifadesi | Karar-destek yeniden çerçevelemesi |
|---|---|
| "Ne alayım?" | "Hangi BIST hisselerini/sektörünü **inceleyelim**? Seçtiğiniz sembol(ler) için kaynaklı bir karar-destek özeti çıkarırım." |
| "X'i alayım mı?" | "X için **karar-destek görünümü** sunabilirim: son EOD durum, son KAP açıklamaları, temel/teknik bağlam ve karşı-senaryolar. Kararı siz verirsiniz." |
| "Hedef fiyat kaç?" | "Üçüncü-taraf analist hedefleri **doğrulanmamış bağlam** olarak mevcutsa onları, ayrıca destek/direnç seviyelerini (EOD) gösterebilirim; bunlar tavsiye değildir." |
| "Yükselir mi?" | "Olası-yön okuması verebilirim: sentiment + önemlilik + teknik duruş bileşimi, **açık güven seviyesi ve karşı-senaryoyla**; kesinlik içermez." |

İlke: **bilgilendir, çerçevele, kullanıcıya bırak** — asla emir verme.

---

## 7. `brief_lint.py` denetim listesi

Her brifing yayımlanmadan önce `brief_lint.py` aşağıdakileri zorunlu kılar:

| # | Kontrol | Geçme koşulu |
|---:|---|---|
| 1 | **Feragat mevcut** | Bölüm 1'deki kanonik metin birebir, brifing sonunda yer alır |
| 2 | **Emir-kipi yok** | Buyrum kipinde "al / sat / gir / topla" gibi al/sat talimatı bulunmaz |
| 3 | **Kaynaklar tarihli** | Her maddi iddia kaynak + tarih taşır |
| 4 | **Ham makine çıktısı yok** | İşlenmemiş JSON/araç dökümü brifinge konmaz; insan-okur özet kullanılır |
| 5 | **EOD sınırı beyanı** | Fiyat geçen her yerde "son kapanış (EOD)" / EOD-gecikme sınırı belirtilmiştir |
| 6 | **Üçüncü-taraf etiketi** | Analist hedef/öneri "doğrulanmamış / üçüncü-taraf" notuyla verilmiştir |
| 7 | **Karşı-senaryo** | Olası-yön çağrısı içeren brifingde açık karşı-senaryo bulunur |
| 8 | **Kesinlik yok** | "garanti", "%X kesin" türü kesinlik iddiası bulunmaz |

> Herhangi bir kontrolün başarısız olması, brifingin yayımdan önce düzeltilmesini
> gerektirir.

---

> Bu belge ve denetlediği tüm çıktılar **karar-destek** amaçlıdır; **yatırım
> danışmanlığı, aracılık veya al/sat tavsiyesi niteliği taşımaz.**
