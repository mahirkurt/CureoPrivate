---
name: prosopografi
description: Bir Osmanlı şahsiyetinin biyografisini ve hizmet kaydını derler (PROSOPOGRAPHY modu).
---

`vekayinuvis` skill'ini **PROSOPOGRAPHY** modunda çalıştır.

Hedef: kullanıcının belirttiği şahıs adı (örn. "Mustafa Behçet Efendi") için yaşam çizelgesi
(Hicrî + Miladî), atama-azil zinciri, eser listesi ve ikincil literatür. ottoman-archives
(get_islam_ansiklopedisi) + yoktez + web_fetch (Sicill-i Osmânî / İSAM e-baskı) kullan;
Sicill-i Ahval defterleri (BOA DH.SAİD) için yol haritası ekle.

**Kurumsal/teşkilat prosopografisi (`detsis`, v3.0 — modern/Cumhuriyet dönemi kurum sorgusunda):**
bir bakanlık/kurum/teşkilatın soyağacı gerektiğinde şu zinciri paralel çalıştır:

```
detsis_resolve_birim(ad/numara)  →  birimId
   ↓
detsis_get_gecmis_birim(birimId) →  teşkilatın önceki adları/bağlı olduğu üst birim
   ↓
detsis_list_milestones(birimId)  →  kuruluş/yeniden-yapılanma/kapanış kilometre taşları
   ↓
detsis_get_mevzuatlar(birimId)   →  kuruluş/değişiklik mevzuatı (kanun/KHK/CBK referansı)
```

**Cumhuriyet-sınırlı: Osmanlı teşkilatına inmez** — DETSİS yalnız Cumhuriyet dönemi merkezi
teşkilat kaydını tutar; Osmanlı dönemi kurumsal tarihçesi için `ottoman_get_islam_ansiklopedisi`
+ devarsiv katalog kaydı birincil kalır. Anahtar yoksa/kayıt yoksa şeffaf `skipped`/`degraded`
beyan edilir (G0); yokluk kanıt değildir.

Belirsizlik işaretlerini ([doğrulanmış]/[muhtemel]/[tartışmalı]/[bilinmiyor])
zorunlu uygula.
