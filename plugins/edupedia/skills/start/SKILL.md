---
name: start
description: edupedia ince istemcisine giriş ve yönlendirme. tedy orkestratörü bağlantısını kontrol eder, edupedia skill'ini ve beş komutu tanıtır, kullanıcının niyetine göre doğru komuta yönlendirir. edupedia nedir, nereden başlamalıyım, hangi komutu kullanmalıyım, tedy bağlı mı, kazanımdan modül nasıl üretilir türü oryantasyon sorularında kullanın.
version: 2.1.0
---

# edupedia — başlangıç

edupedia (1.0.0'dan beri) bir **ince istemcidir**: Maarif Modeli'ne hizalı etkileşimli modüllerin derlenmesi, 18 kalite kapısı ve tedy.online aile kataloğuna yayın `tedy` MCP orkestratöründe (https://mcp.tedy.online/mcp) yapılır. Kurallar `edupedia` skill'indedir.

## 1. Bağlantıyı kontrol et

`edupedia_durum` çağır. Yanıt geliyorsa bağlısın. Araç yoksa ya da yetki hatası dönüyorsa: `/mcp` → `tedy` → Authenticate; TEDY aile listesindeki tam yetkili Google hesabıyla giriş yap, onay sayfasında geri-çağırma adresini kontrol edip "Onayla"ya bas. Yalnız okuma rolündeki hesaplar bağlanamaz.

## 2. Niyete göre yönlendir

| Kullanıcı ne istiyor? | Komut |
|---|---|
| Kazanım kodundan modül | `/edupedia:modul <kod>` |
| Ders + sınıf + konudan modül | `/edupedia:mufredat <ders> <sınıf> <konu>` |
| Yalnız kazanım listesi | `/edupedia:kazanim-bul <konu> [sınıf] [ders]` |
| Sınav sorusunu öğreterek çöz (yayınlanmaz) | `/edupedia:soru <fotoğraf veya metin>` |
| Bağlantı ve sağlık | `/edupedia:durum` |

Yayınlanmış modüller ve ilerleme için `edupedia_katalog` ve `edupedia_ilerleme` kullanılır.

## 3. Sınırlar

- HTML'i model yazmaz; orkestratör derler ve kapılardan geçirir.
- Görünüm de orkestratördedir: modüller tedy.online panosuyla aynı Tedy tasarım dilinde (Carbon g10/g100, lacivert Tedy bandı) çıkar. MODULE_DATA'ya renk, tema, CSS ya da `meta.accent` yazılmaz.
- `maarif-mufredat` ve `egitim-kaynak` isteğe bağlı doğrudan bağlayıcılardır; derleme yine `edupedia_kapsam` çalıştırması ister.
- claude.ai, Codex, Grok ve Gemini Spark aynı akışı `surfaces/` paketleriyle kullanır; kurulum `KURULUM.md`.
