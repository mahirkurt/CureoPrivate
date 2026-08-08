---
name: lex-sanitas-start
description: >-
  Lex Sanitas süiti için YALNIZCA oryantasyon ve yönlendirme skill'i — mevzuat üretim işini KENDİSİ yapmaz,
  onu flagship `lex-sanitas` skill'ine/komutlarına yönlendirir. Kullan — "lex-sanitas nedir / nereden başlamalıyım /
  hangi modu kullanmalıyım / hangi komut", "connector'larım bağlı mı / hepsi çalışıyor mu / tam-filo durumu", ya da
  kullanıcı sağlık mevzuatı reformu istiyor ama hangi modun (DRAFT/AMEND/ANALYZE/COMPLY/OPINE/RIA/COMPARATIVE/TBMM/
  EX_POST) uygun olduğu belirsizse. 21 hukuk/regülasyon MCP + evidentia/sci-audit tam-filo durumunu kontrol eder,
  9 modu ve 10 komutu tanıtır, niyet→komut yönlendirmesi yapar. Somut bir drafting talebi (ör. "yönetmelik taslağı
  hazırla") NET ise doğrudan flagship `lex-sanitas` skill'i devreye girer — bu router araya girmez.
version: 3.4.0
---

# Lex Sanitas — Başlangıç ve Yönlendirme

Bu skill, Lex Sanitas süitinin giriş kapısıdır: **tam-filo durumunu kontrol eder**, **9 modu tanıtır** ve kullanıcıyı **doğru moda/komuta yönlendirir**.

## 1. Önce tam-filo durumunu göster

Kullanıcı süitle ilk kez çalışıyorsa veya "connector'larım bağlı mı / hepsi çalışıyor mu" diye sorduysa, **`/lex-connectors`** komutunu çalıştır — 21 wire'lı MCP + companion + evidentia/sci-audit'in canlı erişilebilirliğini raporlar (SessionStart preflight çıktısıyla tutarlı).

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
| "lex-sanitas nedir / bağlantı durumu" | — | `/lex-connectors` |

Mod belirsizse, kullanıcıya kısa bir netleştirme sorusu sor (ör. "Mevcut bir mevzuatı mı değiştireceğiz [AMEND], yoksa sıfırdan mı yazacağız [DRAFT]?"). Belirsizlik reform-dışı bir talebe işaret ediyorsa **Scope Guard** uygula (aşağı).

## 3. Scope Guard (her yönlendirmeden önce)

Lex Sanitas yalnız **mevzuat reformu/üretimi** içindir. Şu talepler **kapsam dışıdır → yönlendir, çıktı üretme**:

- Bireysel SGK ödeme reddi davası · AYM bireysel başvuru (sağlık) · kompasyonel kullanım · malpraktis savunması → `saglik-sigorta` / `onko-erisim`.
- Promosyonel materyal denetimi (detail aid, MLR, speaker bureau, CME) → `promo-censor`.

## 4. Çekirdek doktrini hatırlat (yeni kullanıcıya)

- **Tam-filo:** wire edilmiş tüm araçlar her sorguda çalışır; çıktı **kapsam manifestosu** (G0) taşır.
- **No-fabrication:** kanun/CELEX/AYM/Yargıtay/PMID asla uydurulmaz; her atıf MCP-doğrulanmış (`evidence_ledger`).
- **Yumuşak delegasyon:** klinik kanıt → evidentia; atıf-adli + Türkçe dil → sci-audit (varsa; yoksa graceful degrade).
- **İnsan denetimi** her çıktıda zorunludur.

Detay: flagship skill **`lex-sanitas`** — adıyla çağrılır (Skill aracı ya da kendi tetikleyicileri); paket içindeki yeri `skills/lex-sanitas/SKILL.md` + `references/`. **Yol bir dağıtım ayrıntısıdır, bağ değildir:** bazı yüzeylerde flagship kullanıcı katmanına kurulur ve bu göreli yol çözülmez — o hâlde de flagship ADIYLA erişilebilir olduğu için yönlendirme geçerlidir.
