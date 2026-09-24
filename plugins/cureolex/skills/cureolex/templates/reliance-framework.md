# Reliance Çerçevesi — düzenleyici kararlarda referans otoriteye dayanma

**Mod:** RELIANCE_FRAMEWORK · **Kapılar:** G0, G1, G2, G5, G6, G7, G10, G11 · **Paket:** ev yargı bölgesi paketi

> **Ne üretir:** ulusal düzenleyici otoritenin, başka bir otoritenin değerlendirmesini veya
> kararını **kendi kararına dayanak olarak kullanabilmesi** için gereken mevzuat hükümlerinin
> taslağını ve gerekçesini.
>
> **Temel ayrım (her bölümde korunur):**
> - **Reliance** — başka otoritenin çıktısı dikkate alınır, **karar ulusal otoritede kalır**.
> - **Tanıma (recognition)** — başka otoritenin kararı ulusal karar yerine geçer; genellikle
>   andlaşma veya karşılıklı tanıma anlaşması gerektirir.
>
> Bu iki kurum karıştırılırsa taslak, ulusal otoritenin yetkisini fiilen devreden ama bunu
> söylemeyen bir metne dönüşür — G2 (üst norm / yetki) ihlali.
>
> **Referans otorite listesi uydurulmaz.** Hangi otoritelerin referans alınacağı politika
> tercihidir; taslakta liste ya kullanıcıdan gelir ya da mevcut bir ulusal/uluslararası
> belgeden künyeyle alınır. WHO listeleri (ör. WHO Listed Authorities) anılacaksa güncel
> hâli birincil kaynaktan doğrulanır.

---

## 0. Künye

| Alan | Değer |
|---|---|
| Ev yargı bölgesi | {{paket kodu + durum}} |
| Kapsam | {{hangi işlevler: kayıt/pazarlama izni, değişiklik başvuruları, GMP denetimi, seri serbest bırakma, klinik araştırma …}} |
| Reliance türü | kısaltılmış inceleme · doğrulama incelemesi · ortak değerlendirme · iş paylaşımı · tanıma (ayrı yasal dayanak gerekir) |
| Mevcut yasal dayanak | {{var: künye · yok · belirsiz}} — kanıt defteri ile |

## 1. Yetki analizi (G2 — önce)

- Ulusal otoritenin karar yetkisini veren norm (paketin norm hiyerarşisinden) ve bu normun reliance'a **izin verip vermediği**.
- Reliance için gereken norm düzeyi: yetki veren norm reliance'ı zaten kapsıyorsa alt düzey düzenleme yeter; kapsamıyorsa üst düzey değişiklik gerekir — bu tespit taslaktan ÖNCE yapılır.
- Tanıma öneriliyorsa: andlaşma/anlaşma gerekliliği ve anayasal andlaşma usulü (paketin `constitutional_health_rights` / `gate_params.G2`).

## 2. Taslak hükümler (iskelet)

Madde biçimi paketin legistik profiline göre kurulur. İskelet:

1. **Amaç ve kapsam** — hangi işlevler, hangi ürün sınıfları.
2. **Tanımlar** — reliance, referans otorite, referans karar, kısaltılmış inceleme.
3. **Referans otoritelerin belirlenmesi** — ölçütler (liste değil) + listenin hangi usulle, hangi norm düzeyinde yayımlanacağı.
4. **Başvuru koşulları** — aynı ürün ilkesi (formülasyon, üretim yeri, endikasyon eşdeğerliği), referans kararın belgeleri, beyan yükümlülüğü.
5. **Ulusal karar yetkisinin korunması** — ulusal otoritenin reddetme, ek bilgi isteme ve kararı yeniden değerlendirme yetkisi açıkça yazılır.
6. **Süreler** — kısaltılmış inceleme süresi.
7. **Karar sonrası yükümlülükler** — referans otoritedeki değişikliklerin (askıya alma, iptal, güvenlik güncellemesi) bildirilmesi.
8. **Şeffaflık** — reliance ile verilen kararların yayımlanması.
9. **Geçiş ve yürürlük** — paketin `gecis_hukumleri` ailesi (paket bu aileyi `coverage_gap` ile işaretlediyse rubrikte kontrol yoktur — raporda beyan edilir).

## 3. Gerekçe

- Kamu sağlığı gerekçesi: erişim süresi, düzenleyici kapasitenin yoğunlaştırılması — **kanıtla** (klinik/erişim verisi evidentia delegasyonu).
- Egemenlik gerekçesi: karar yetkisinin nerede kaldığı (Bölüm 1).
- Karşılaştırmalı emsal: başka yargı bölgelerinin reliance hükümleri — her biri kendi paket koduyla ve `comparative_benchmark` rolüyle (G11).

## 4. Riskler

| Risk | Açıklama | Hafifletme hükmü |
|---|---|---|
| Referans kararın ev bölgesine uymaması | epidemiyoloji, sağlık sistemi, ürün tedarik zinciri farkı | Md. 4 aynı-ürün ilkesi + Md. 5 ek bilgi yetkisi |
| Referans otoritede kararın değişmesi | askıya alma / iptal | Md. 7 bildirim yükümlülüğü |
| Fiilî yetki devri | reliance'ın tanımaya dönüşmesi | Md. 5 |

## 5. Sınırlar

- Referans otorite adlandırmak politika kararıdır; bu şablon öneri yapabilir ama karar vermez.
- Kapsam manifestosu + `confidence_label` (paket + tavan) zorunlu; insan denetimi zorunlu.
