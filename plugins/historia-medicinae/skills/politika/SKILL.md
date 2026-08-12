---
name: politika
description: "SANITAS_PUBLICA modu — kamu sağlığı politikası ve sağlık hukukunun tarihi: karantina ve tahaffuzhane rejimleri, uluslararası sanitary konvansiyonlar → IHR, sağlık bakanlıklarının kuruluşu, zorunlu aşı yasaları, WHO'nun kuruluşu, çiçek eradikasyon programı, Alma-Ata, sosyal sigorta ve ulusal sağlık sistemleri (Bismarck 1883, NHS 1946). Kullanın: 'karantina tarihi', 'sağlık yasası tarihi', 'WHO kuruluşu', 'NHS tarihi', 'zorunlu aşı yasası', 'sağlık politikası tarihi', 'sanitary conference' sorularında."
argument-hint: "<politika/yasa/kurum> [dönem] [ülke]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# SANITAS_PUBLICA — Kamu Sağlığı Politikası ve Hukuk Tarihi

Flagship protokolü `SANITAS_PUBLICA` moduyla çalıştır.
Yükle: `quellenkritik.md` · `kuresel-cerceve.md` · `source-typology.md` · `periodization.md`.

## Bu modun ayırt edici yanı: yasama bandı ZORUNLU

Politika tarihi ikincil literatürün özetiyle yazılmaz. Müzakerenin kendisi okunur:

| Kaynak | Ne verir |
|---|---|
| **Hansard** (`uk-legal`, 1803+) | Vaccination Acts, Contagious Diseases Acts, Public Health Acts, NHS 1946 — **zabıttan** tartışma |
| **GovInfo / Congress** (`health-policy`) | ABD federal sağlık mevzuatı ve komisyon raporları |
| **intl-treaty** | Sanitary konvansiyon geleneğinin mirasçı belgeleri, Oviedo, MEDICRIME ⚠️ küratörlü snapshot |
| **mevzuat / tbmm / resmigazete** | TR: 1593 Umumi Hıfzıssıhha Kanunu (1930), 1219 (1928) — gerekçe + zabıt + yayın kaydı |
| **health-policy** JP/AU/ES/IE/CN/MX/CA | Karşılaştırmalı ulusal katman |

## Üç katman ayrımı

**Niyet** (yasa metni) ≠ **Kabul süreci** (müzakere, muhalefet, uzlaşma) ≠ **Uygulama**
(denetim raporu, istatistik, direniş). Üçü ayrı kaynak ister; yalnız yasa metnine dayanan
politika tarihi eksiktir.

## Direniş ekseni

Zorunlu aşı, karantina ve bildirim rejimleri **daima** direnişle karşılaşmıştır (anti-vaccination
league'ler, ticaret çevrelerinin karantina karşıtlığı, mahremiyet itirazları). Direniş
"cehalet" olarak açıklanmaz; kendi gerekçeleriyle yeniden kurulur.

## Küresel çerçeve

Uluslararası sağlık rejimi Avrupa'nın ticaret çıkarlarıyla iç içe doğdu; "küresel sağlık"
anlatısı bu kökeni silmeden yazılır (`kuresel-cerceve.md`).

## Nicel destek

`who-gho` yalnız ≈1948 sonrası için geçerlidir; öncesine **projeksiyon yapılmaz**.
Tarihsel mortalite serileri için `kaynak-elestirisi` skill'i zorunlu.

## Çıktı

G0 manifestosu · yasa künyeleri tam (numara, tarih, yayın kaydı) · müzakere alıntıları
konuşmacı + tarih + sütun/sayfa ile · niyet/uygulama ayrımı görünür.

⚠️ Yürürlükteki TR normu sorulursa → `lex-sanitas` delegasyonu.
