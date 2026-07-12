---
name: satinalma
description: eSatış sepet + noVNC satın-alma akışı — karar matrisi, metin-onay kapısı, ödeme daima insan.
disable-model-invocation: true
---

`vekayinuvis` skill'ini **SEPET/SATIN-ALMA** akışında, **`devlet-arsivleri`** connector'ı
odağıyla çalıştır. Referans: `references/devlet-arsivleri-katalog.md` §8.1.

Hedef: `devarsiv_get_belge` çağrısının `access=="purchasable"` döndürdüğü ve kullanıcının
belgenin **tüm** sayfalarına ihtiyaç duyduğu bir belgeyi, resmî eSatış sepeti üzerinden
satın alınabilir hâle getirmek. Bu skill **açık kullanıcı isteği olmadan tetiklenmez**
(`disable-model-invocation: true`) — para harcayan bir akıştır; ödeme adımı daima insan
tarafından tamamlanır, asistan hiçbir aşamada otonom ödeme yapmaz.

Akış üç fazdan oluşur: ücretsiz karar aşaması, ödemesiz-ama-durum-değiştiren sepet
aşaması ve insan-tamamlamalı ödeme-sonrası aşaması. Faz 2'nin sonunda **metin-onay
kapısı** zorunludur — kullanıcının açık onayı olmadan ödeme adımına geçilmez.

## Faz 1 — KARAR (ücretsiz)

1. `devarsiv_get_belge` → künye + `goruntu_sayisi` + `access` (`"purchased"` ise DUR:
   `/vekayinuvis:arsiv-oku`)
2. `devarsiv_get_belge_image` → önizlemeyi GÖRÜyle değerlendir (içerik gerçekten
   hedefle ilgili mi?)
3. Karar matrisi (4 eksen): ilgi (görü teyidi) × derinlik (`goruntu_sayisi`) ×
   kaynak-değeri (özet+fon) × bütçe (~0,50 TL/sayfa TAHMİN; bağlayıcı tutar
   `list_cart` Tutar sütunu)
4. Karar tablosunu kullanıcıya sun: aday belgeler | sayfa | tahmini maliyet | gerekçe

Bu faz **tamamen ücretsizdir** ve devlet-değiştirici (state-changing) hiçbir araç
çağırmaz. Adım 1-2'de toplanan kanıt adım 3'teki 4-eksenli karar matrisine girdi
olur: "ilgi" ekseni salt görü değerlendirmesine dayanır (K6 madde 2 — katalog arama
token'i doğrulanmış içerik değildir, "görüntü teyidi bekliyor" etiketi görüyle
kaldırılır); "derinlik" ekseni `goruntu_sayisi` alanından gelir; "kaynak-değeri"
ekseni özet/fon bağlamının hedef konuya yakınlığını ölçer; "bütçe" ekseni yalnız
TAHMİNİ fiyatlandırma taşır. Adım 4'te karar tablosu kullanıcıya şeffaf biçimde
sunulur; hangi adayların sepete ekleneceğine kullanıcı karar verir.

## Faz 2 — SEPET (yumuşak kapı)

5. Onaylanan adaylar: `devarsiv_add_to_cart(item_id, hash, arsiv, pages)` — sayfa
   alt-kümesi destekli ("1,3-5")
6. `devarsiv_list_cart` → kalemleri + BAĞLAYICI toplamı doğrula
7. METİN-ONAY KAPISI: "Sepette N kalem, toplam X TL. Ödemeye geçilsin mi?" — açık
   onay olmadan `checkout_cart` ÇAĞRILMAZ; `remove_from_cart(clear=true)` da açık
   onay ister
8. `devarsiv_checkout_cart` → YALNIZ noVNC URL döner: https://devarsiv-vnc.cureonics.com/vnc.html
   + uyarı: "Kendi cihazınızdan kataloğa GİRMEYİN — tek-cihaz kilidi HP oturumunu düşürür."
   Ödeme (kart+3DS) DAİMA insan; Access girişi @cureonics.com OTP.

`add_to_cart` `[_RW]` ve `remove_from_cart` `[_DESTRUCTIVE]` devlet-değiştirici
araçlardır ama **para harcamazlar** — yalnız eSatış sepetinin içeriğini değiştirirler.
`checkout_cart` de **ödeme YAPMAZ**; yalnızca noVNC URL'sini ve güncel sepeti döner.
Adım 7'deki metin-onay kapısı bu akışın en kritik güvenlik kontrolüdür: sepet özeti
ve `devarsiv_list_cart` çıktısındaki bağlayıcı Tutar kullanıcıya gösterilip açık
onay alınmadan ne `checkout_cart` ne de sepeti boşaltan `remove_from_cart(clear=true)`
çağrılır.
Fiyat dili daima: "~0,50 TL/sayfa TAHMİNDİR; bağlayıcı tutar `devarsiv_list_cart` çıktısındaki Tutar sütunudur."
Tek-cihaz uyarısı adım 8'de
**daima verbatim** aktarılır — kullanıcının kendi cihazından kataloğa paralel giriş
yapması HP'deki kalıcı oturumu düşürür ve tüm filoyu `session_required`'a sokar.

## Faz 3 — ÖDEME SONRASI (operatör adımı)

9. Kullanıcı ödemeyi bitirdiğinde: HP'de `scripts/build_archive.py` koşulmalı —
   Claude Code host: `ssh hp-ai-node '~/devarsiv/.venv-arc/bin/python ~/devarsiv/build-archive.py'`
   (yol yoksa: CureoHub `mcp-servers/devlet-arsivleri-mcp/scripts/build_archive.py`
   kopyası)
   claude.ai host: komutu kullanıcıya kutu içinde ver (operatör adımı)
10. `devarsiv_list_archive` ile yeni code'u doğrula → `/vekayinuvis:arsiv-oku`

Faz 3 asistanın kendi başına tamamlayamadığı bir **operatör adımıdır**: satın
alınan sayfaların yerel BOA-kodlu PDF arşivine düşmesi için HP'de arşiv-derleme
script'inin çalıştırılması gerekir. Çalışma ortamı Claude Code ise (SSH erişimi
var) komut doğrudan koşulur; claude.ai bağlamında (SSH yok) komut kod-bloğu
içinde kullanıcıya verilir ve kullanıcı kendi tamamlar. Script tamamlandıktan
sonra `devarsiv_list_archive` ile yeni `code`'un göründüğü doğrulanır — bu
doğrulama `/vekayinuvis:arsiv-oku` akışına geçişin ön koşuludur.

**No-fabrication:** ödeme hiçbir koşulda otonom yapılmaz; sepet mutasyonu
yalnızca ana orkestratör turunda, kullanıcı onayıyla gerçekleşir;
`arsiv-tarama-distilleri` alt-ajanı sepete dokunmaz.
