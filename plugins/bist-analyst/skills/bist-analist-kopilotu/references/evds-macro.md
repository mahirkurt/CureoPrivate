# TCMB EVDS / Makro Katman ve Rejim Sınıflandırması — `bist-analist-kopilotu`

Bu belge, BIST hisse rejimini belirleyen makro katmanı tanımlar: hangi TCMB EVDS
serileri önemlidir, bunlar `borsa` MCP üzerinden nasıl alınır ve basit bir
**makro rejim sınıflandırması** (sıkılaştırma / gevşeme / belirsizlik) nasıl
yapılır. Belge, eşlik eden `scripts/macro_context.py` betiğiyle **aynı sinyalleri**
kullanır; tanımlar birbirini doğrular niteliktedir.

> **EVDS anahtarı sunucu tarafındadır.** Makro seriler `get_macro_data` /
> `get_evds_data` üzerinden alınır; kullanıcı kurulumu veya anahtar girişi
> gerekmez.

---

## 1. BIST rejimi için önemli seriler

| Sinyal | Seri | Araç | Hisse için anlamı |
|---|---|---|---|
| Politika faizi | 1 hafta repo / politika faizi | `get_macro_data` / `get_evds_data` | İskonto oranının çapası; yön rejimi belirler |
| Enflasyon (tüketici) | TÜFE (yıllık/aylık) | `get_evds_data` | Reel faizin paydası; faiz yönü beklentisi |
| Enflasyon (üretici) | ÜFE (yıllık) | `get_evds_data` | Maliyet baskısı; marj öncüsü |
| Kur | USDTRY ve sepet (USD+EUR) kur | `get_fx_data` | İthalatçı/ihracatçı ayrışması, geçişkenlik |
| Rezervler | TCMB brüt/net rezervler | `get_evds_data` | Kur istikrarı ve dış kırılganlık |
| Reel kur | REER (reel efektif döviz kuru) | `get_evds_data` | Rekabetçilik; ihracatçı konumu |
| Beklentiler | Piyasa katılımcıları beklenti anketi (enflasyon/faiz beklentisi) | `get_evds_data` | İleriye dönük rejim sezgisi |
| Tahvil faizi | TR gösterge tahvil faizi | `get_bond_yields` | Risk-free / iskonto oranı; değerleme baskısı |
| Olay takvimi | PPK/veri açıklama takvimi | `get_economic_calendar` | Yaklaşan rejim-değiştirici olaylar |

**Reel faiz** = politika faizi − (beklenen/cari TÜFE yıllık). Pozitif ve yükselen
reel faiz sıkılaştırıcı; negatif ve düşen reel faiz gevşeticidir.

---

## 2. Makro rejim sınıflandırması

`scripts/macro_context.py` rejimi dört sinyalin yönünden türetir:
**(a) politika faizi trendi, (b) reel faiz, (c) TÜFE trendi, (d) kur trendi.**
Aynı sinyaller burada da kullanılır.

| Rejim | Sinyal örüntüsü | Hisse iskonto oranı | Sektör eğilimi |
|---|---|---|---|
| **Sıkılaştırma** | Politika faizi yükseliyor; reel faiz pozitif/artıyor; TÜFE zirve/düşüş; kur stabilize | İskonto oranı **yükselir** → değerleme baskısı, uzun-vadeli/yüksek-büyüme isimler dezavantajlı | **Bankalar** net faiz marjı/mevduat-kredi makasıyla göreli avantajlı; faize-duyarlı (yüksek kaldıraçlı, uzun-vadeli temettü) isimler baskı altında |
| **Gevşeme** | Politika faizi düşüyor; reel faiz düşüyor; TÜFE düşüş trendinde; kur görece sakin | İskonto oranı **düşer** → değerleme desteği, büyüme/faize-duyarlı isimler avantajlı | **Faize-duyarlı** (inşaat, GYO, yüksek kaldıraçlı sanayi) ve büyüme isimleri öne çıkar; banka makası daralabilir |
| **Belirsizlik** | Sinyaller çelişkili (örn. faiz sabit ama kur hızlanıyor / TÜFE yapışkan); beklenti anketi dağınık | İskonto oranı **oynak / risk primi yüksek** | **İhracatçılar** (zayıf/oynak TL + döviz geliri) ve döviz-bazlı gelir/varlık taşıyanlar görece korunaklı; saf yerel-talep isimleri kırılgan |

### Sinyal okuma kuralları (betikle hizalı)

1. **Politika faizi trendi:** son birkaç PPK kararının yönü (artış / sabit / indirim).
2. **Reel faiz:** politika faizi − beklenen TÜFE; işaret ve yön birlikte okunur.
3. **TÜFE trendi:** yıllık enflasyonun yön türevi (hızlanıyor / yavaşlıyor).
4. **Kur trendi:** USDTRY ve sepet kurun momentum/oynaklığı; REER ile teyit.

Çelişki varsa rejim **belirsizlik** olarak işaretlenir; tek bir sinyale dayanarak
sıkılaştırma/gevşeme ilan edilmez.

---

## 3. Sektör çıkarımı özeti

- **Bankalar (XBANK):** sıkılaştırmada makas/marj lehine; gevşemede makas daralması
  riski. Faiz yönü birincil sürücü.
- **İhracatçılar:** zayıf/oynak TL ve döviz geliri belirsizlik ve TL değer kaybı
  rejimlerinde göreli korunak; güçlenen TL'de dezavantaj.
- **Faize-duyarlı (yüksek kaldıraç, GYO, inşaat, uzun-vadeli nakit akışı):**
  gevşemede avantajlı, sıkılaştırmada baskı altında.
- **Yerel-talep/savunmacı:** belirsizlikte göreli istikrar ama döviz korunağı zayıf.

Bu çıkarımlar **genel eğilimdir**, otomatik hisse seçimi değildir; her isim
şirket-özel temel ve teknik bağlamıyla birlikte değerlendirilir.

---

> Bu belgenin ürettiği makro çıkarımlar **karar-destek** amaçlıdır; **yatırım
> tavsiyesi değildir.**
