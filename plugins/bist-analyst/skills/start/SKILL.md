---
name: start
description: >-
  BIST Analyst eklentisine giriş, bağlayıcı (Borsa MCP) sağlık kontrolü ve doğru
  moda yönlendirme. İlk kez eklentiyle çalışırken, "BIST Analyst nedir / nereden
  başlamalıyım / hangi modu kullanmalıyım", bağlayıcı bağlı mı, ya da analiz
  öncesi kurulum doğrulaması için kullanın. EN: Orientation and connector
  health-check for the BIST Analyst plugin; routes the request to the correct
  analysis mode of the bist-analist-kopilotu skill. Triggers — BIST Analyst
  başlat, eklenti oryantasyonu, "ne yapabilirsin", "nereden başlayayım",
  "Borsa bağlı mı", connector kontrolü, kurulum doğrulama.
---

# BIST Analyst — Başlangıç ve Yönlendirme (v1.0.0)

Bu beceri, **BIST Analyst** eklentisinin giriş kapısıdır. Üç işi yapar: (1) veri
omurgasının bağlı olduğunu doğrular, (2) eklentinin yeteneklerini ve sınırlarını
özetler, (3) kullanıcının niyetine göre asıl analiz becerisi olan
`bist-analist-kopilotu`'na yönlendirir. Kendisi brifing **üretmez**; üretim her
zaman `bist-analist-kopilotu` becerisinde gerçekleşir.

## 1. Kapsam ve sınır (Scope Guard)

- **Kapsam:** Yalnızca **BIST hisseleri** ve gerekli olduğunda BIST endeksleri /
  TCMB makro bağlamı.
- **Kapsam dışı:** ABD hisseleri, kripto varlıklar ve TEFAS fonları. Kullanıcı
  bunları sorarsa kapsam dışı olduğunu kibarca bildirin.
- **Kritik kural:** Tüm çıktılar **karar destek** niteliğindedir; **yatırım
  danışmanlığı/tavsiyesi değildir.** "Şunu al / sat / topla" gibi kişiye özel
  yönlendirme yapılmaz. Bu sınır, hem SPK yatırım danışmanlığı yetkisine saygı
  hem de kullanıcıya dürüstlük içindir.

## 2. Adım 0 — Bağlayıcı sağlık kontrolü (zorunlu)

Herhangi bir analize başlamadan önce **Borsa MCP** erişilebilir mi diye doğrulayın
(örn. `search_symbol` ile küçük bir prob). Bu eklenti, Borsa MCP'yi remote bir
bağlayıcı olarak **paket içinde** getirir; eklenti etkinleştirildiğinde otomatik
yapılandırılır.

- **Erişilebiliyorsa:** Hangi moda gidileceğini belirleyip `bist-analist-kopilotu`
  becerisine devredin.
- **Erişilemiyorsa:** Canlı veri varsaymadan durun. Kullanıcıya `/plugin` arayüzünden
  eklentinin **etkin** olduğunu ve `borsa` MCP sunucusunun onaylandığını kontrol
  etmesini önerin. Onay alınırsa, `bist-analist-kopilotu` içindeki **zarif düşüş**
  moduyla (yalnız `web_search`/`web_fetch`, kaynak ve kısıt açıkça belirtilerek)
  sınırlı analiz yapın. **Uydurma fiyat/rakam üretmeyin.**

> **Not (doğrulanmış):** TCMB EVDS makro katmanının API anahtarı Borsa MCP
> tarafında **sunucu-tarafında** ayarlıdır; kullanıcı kurulumu gerektirmez. EVDS
> probu başarısızsa makro çerçeve atlanır/uyarılır, ancak hisse analizi durmaz.

## 3. Mod yönlendirmesi

Niyeti belirleyip `bist-analist-kopilotu` becerisinin ilgili moduna yönlendirin.
Şüphede tek bir soruyla netleştirin.

| Kullanıcı niyeti | Tetik örnekleri | Yönlendirilecek mod |
| :--- | :--- | :--- |
| Tek hissede derinlemesine görünüm | "GARAN analiz et", "THYAO yorum", "ASELS teknik durum" | **Mod 1 — Tek hisse derin analizi** |
| Hafta için aday evreni | "bu hafta hangi hisseler", "yüksek momentumlu BIST", "haftalık tarama" | **Mod 2 — Haftalık tarama brifingi** |
| Tek bir KAP açıklaması/olayı | yeni KAP açıklaması, "şu haber ne anlama geliyor", sert fiyat/hacim | **Mod 3 — KAP / olay yorumu** |
| Verili bir sembol listesinin gözetimi | "izleme listemi gözden geçir", sembol listesi | **Mod 4 — İzleme listesi gözetimi** |

## 4. Eklentinin bileşenleri (kısa)

- **`bist-analist-kopilotu`** — asıl analist becerisi (4 mod, kanıt zinciri,
  karşıt senaryo, zorunlu feragat, brifing şablonları).
- **Borsa MCP (paketli bağlayıcı)** — KAP haberleri, gün sonu (EOD) fiyat/teknik,
  İş Yatırım/borsapy tabanlı tarayıcı + FX, TEFAS, TCMB EVDS + enflasyon.
- **İsteğe bağlı, dış bileşenler (paketli değil):** Brifingi IBM Carbon biçimli
  bir belgeye dökmek için `carbon-html-report` / `carbon-pptx`; tamamlayıcı borsa
  istatistikleri için Finmap MCP. Bunlar ayrı kurulur ve composable kullanılır.

## 5. Önemli veri sınırı

Borsa MCP fiyat verisi büyük ölçüde **gecikmeli/gün sonu (EOD)**'dur; **gün içi
emir defteri/derinlik/PİTE içermez**. Günlük ve haftalık ufuklu analiz için
yeterlidir; gün-içi mikro-yapı iddiası **üretilmez**.
