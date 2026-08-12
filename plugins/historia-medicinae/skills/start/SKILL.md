---
name: start
description: "historia-medicinae süitine giriş ve yönlendirme. Bağlı connector'ları kontrol eder, 11 araştırma modunu ve üç metodoloji skill'ini tanıtır, kullanıcının niyetine göre doğru komuta yönlendirir. Kullanın: süitle ilk kez çalışırken, 'historia-medicinae nedir', 'nereden başlamalıyım', 'hangi komutu kullanmalıyım', 'connector'larım bağlı mı', 'tıp tarihi araştırmasına nasıl başlarım' türü oryantasyon sorularında."
argument-hint: "[opsiyonel: araştırmak istediğiniz konu]"
allowed-tools: Read, Glob, Bash
disable-model-invocation: false
---

# Historia Medicinae — Başlangıç

Kullanıcıyı karşıla, filoyu kontrol et, doğru moda yönlendir.

## 1. Karşılama

Kısa tut. Şunu söyle: bu süit **küresel** tıp tarihi araştırması yapar — Mezopotamya ve
Greko-Romen dünyadan İslâm geleneğine, Latin Batı'dan Doğu Asya ve Güney Asya'ya, sömürge
tıbbından çağdaş küresel sağlığa; Türkiye bu kapsamın **bir bölgesi**dir, dışında değil.

## 2. Filo kontrolü

`historia-medicinae:durum` skill'ini çağır (veya kullanıcı isterse atla). Özet ver:
kaç server bağlı, hangi bantlar eksik, hangi degrade devrede. **Ölçülmüş bloklar** (LoC 403,
NLM bot kapısı) burada bir kez hatırlatılır — sonra tekrarlanmaz.

## 3. Mod yönlendirme

Kullanıcının niyetini anla ve **tek bir komut öner** (liste dökme):

| Niyet | Komut |
|---|---|
| "Bu konuda hangi kaynaklar var?" | `/historia-medicinae:kaynak-avi` |
| Salgın, hastalık, epidemi | `/historia-medicinae:salgin` |
| Hastane, tıp okulu, cemiyet, lisanslama | `/historia-medicinae:kurum` |
| Fikir, kavram, teori (miyazma, germ teorisi, humoralizm) | `/historia-medicinae:kavram` |
| İnsan deneyleri, öjeni, sömürge tıbbı, tıp etiği tarihi | `/historia-medicinae:etik` |
| Hekim biyografisi, kuşak, ağ | `/historia-medicinae:hekim` |
| İlaç, tedavi, cerrahi teknik, tıbbî alet | `/historia-medicinae:tedavi` |
| Kamu sağlığı politikası, karantina, sağlık yasası | `/historia-medicinae:politika` |
| "Bu konu nasıl yazıldı, hangi ekoller?" | `/historia-medicinae:historiyografi` |
| Tarihsel bir tıp metnini okumak | `/historia-medicinae:metin` |
| Bulguları makaleye dönüştürmek | `/historia-medicinae:rapor` |

Metodoloji skill'leri (mod bağımsız çağrılabilir):
`retrodiagnoz` (modern tanı etiketi tartışması) · `kaynak-elestirisi` (kaynak güvenilirliği,
ölüm cetvelleri, kurumsal kayıtlar) · `iiif-tarama` (dijitalleştirilmiş yazma/erken basma avı).

## 4. Üç uyarı — bir kez söylenir

1. **Retrospektif tanı** varsayılan olarak yapılmaz; yapılırsa hipotez olarak işaretlenir.
2. **Yokluk kanıt değildir** — dijital korpuslarda arama boş dönebilir.
3. **Osmanlıca el yazması okuma** `vekayinuvis`'e delege edilir; kurulu değilse katalog
   düzeyinde kalınır.

## 5. Konu verildiyse

Argümanla bir konu geldiyse karşılamayı kısa kes, modu **kendin seç** ve doğrudan ilgili
skill'e geç.
