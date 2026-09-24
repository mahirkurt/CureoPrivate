---
name: cureolex-start
description: >-
  Cureolex süiti için YALNIZCA oryantasyon ve yönlendirme skill'i — mevzuat üretim işini KENDİSİ yapmaz,
  onu flagship `cureolex` skill'ine/komutlarına yönlendirir. Kullan — "cureolex nedir / nereden başlamalıyım /
  hangi modu kullanmalıyım / hangi komut", "connector'larım bağlı mı / hepsi çalışıyor mu / tam-filo durumu", ya da
  kullanıcı sağlık mevzuatı reformu istiyor ama hangi modun (DRAFT/AMEND/ANALYZE/COMPLY/OPINE/RIA/COMPARATIVE/TBMM/
  EX_POST/MATURITY/TRANSPOSITION/RELIANCE) uygun olduğu belirsizse, ya da "hangi ülkeler destekleniyor". 21
  hukuk/regülasyon MCP + evidentia/sci-audit tam-filo durumunu kontrol eder, 12 modu, 13 komutu ve yargı bölgesi
  paketlerini tanıtır, niyet→komut yönlendirmesi yapar. Somut bir drafting talebi (ör. "yönetmelik taslağı
  hazırla") NET ise doğrudan flagship `cureolex` skill'i devreye girer — bu router araya girmez.
version: 4.0.0
---

# Cureolex — Başlangıç ve Yönlendirme

Bu skill, Cureolex süitinin giriş kapısıdır: **tam-filo durumunu kontrol eder**, **12 modu tanıtır** ve kullanıcıyı **doğru moda/komuta yönlendirir**.

## 1. Önce tam-filo durumunu göster

Kullanıcı süitle ilk kez çalışıyorsa veya "connector'larım bağlı mı / hepsi çalışıyor mu" diye sorduysa, **`/lex-connectors`** komutunu çalıştır — 21 wire'lı MCP + companion + evidentia/sci-audit'in canlı erişilebilirliğini raporlar (SessionStart preflight çıktısıyla tutarlı). **Web yüzeyinde** (`claude.ai`, ChatGPT) Python hook ve `fleet_probe.py` **yoktur**: `CONNECTORS.md` yüzey matrisini göster, kullanıcının elle eklediği connector'ları sor, canlı `ok` iddia etme.

## 2. Niyet → mod/komut yönlendirmesi

| Kullanıcı ne diyorsa | Mod | Komut |
|---|---|---|
| "yönetmelik/tebliğ taslağı hazırla", "yeni mevzuat", "ATMP düzenlemesi" | DRAFT | `/lex-draft` |
| "şu maddeyi değiştir", "ek/geçici madde", "ibare değişikliği" | AMEND | `/lex-amend` |
| "bu mevzuatı incele", "hukuka uygun mu", "sorun var mı" | ANALYZE | `/lex-analyze` |
| "5210 uyumu", "drafting kalite kontrolü", "metni denetle" | COMPLY | `/lex-comply` |
| "kurum görüşü", "Md.6 görüşü", "komisyon görüşü", "bilirkişi mütalaası" | OPINE | `/lex-opine` |
| "DEA hazırla", "düzenleyici etki analizi", "BEF" | RIA | `/lex-ria` |
| "karşılaştırmalı analiz", "AB karşılığı", "reliance benchmark" | COMPARATIVE_LAW | `/lex-comparative` |
| "TBMM kanun teklifi", "1219 SK reform", "Anayasa Md.88" | TBMM_KANUN_TEKLIFI | `/lex-bill` |
| "ex post değerlendirme", "geriye dönük etki", "sunset clause" | EX_POST_EVALUATION | `/lex-expost` |
| "WHO GBT", "düzenleyici olgunluk", "ML3 açığı" | REGULATORY_MATURITY | `/lex-maturity` |
| "direktif aktarımı", "uyum tablosu", "transposition" | TRANSPOSITION | `/lex-transpose` |
| "reliance", "referans otorite", "kısaltılmış inceleme" | RELIANCE_FRAMEWORK | `/lex-reliance` |
| "cureolex nedir / bağlantı durumu" | — | `/lex-connectors` |

**Yargı bölgesi (4.0):** belirtilmezse **TR** paketi (3.x davranışı). Başka bölge istenirse `jurisdictions/` altındaki paket yüklenir: **TR active · GB/DE/CH draft** — taslak pakette çıktı en fazla LOW güvenlidir ve bunu kullanıcıya baştan söyle. Paketi olmayan bölge için mod çalıştırılmaz; `manual_required` + mevcut paketler. TR'deki `TBMM_KANUN_TEKLIFI` genel `PARLIAMENTARY_BILL` modunun takma adıdır.

Mod belirsizse, kullanıcıya kısa bir netleştirme sorusu sor (ör. "Mevcut bir mevzuatı mı değiştireceğiz [AMEND], yoksa sıfırdan mı yazacağız [DRAFT]?"). Belirsizlik reform-dışı bir talebe işaret ediyorsa **Scope Guard** uygula (aşağı).

## 3. Scope Guard (her yönlendirmeden önce)

Cureolex yalnız **mevzuat reformu/üretimi** içindir. Şu talepler **kapsam dışıdır → yönlendir, çıktı üretme**:

- Bireysel SGK ödeme reddi davası · AYM bireysel başvuru (sağlık) · kompasyonel kullanım · malpraktis savunması → `saglik-sigorta` / `onko-erisim`.
- Promosyonel materyal denetimi (detail aid, MLR, speaker bureau, CME) → `promo-censor`.

## 4. Çekirdek doktrini hatırlat (yeni kullanıcıya)

- **Tam-filo:** wire edilmiş tüm araçlar her sorguda çalışır; çıktı **kapsam manifestosu** (G0) taşır.
- **No-fabrication:** kanun/CELEX/AYM/Yargıtay/PMID asla uydurulmaz; her atıf MCP-doğrulanmış (`evidence_ledger`).
- **Yumuşak delegasyon:** klinik kanıt → evidentia; atıf-adli + Türkçe dil → sci-audit (varsa; yoksa graceful degrade).
- **İnsan denetimi** her çıktıda zorunludur.

Detay: flagship skill **`cureolex`** — adıyla çağrılır (Skill aracı ya da kendi tetikleyicileri); paket içindeki yeri `skills/cureolex/SKILL.md` + `references/`. **Yol bir dağıtım ayrıntısıdır, bağ değildir:** bazı yüzeylerde flagship kullanıcı katmanına kurulur ve bu göreli yol çözülmez — o hâlde de flagship ADIYLA erişilebilir olduğu için yönlendirme geçerlidir.
