---
name: lex-reliance
description: "Mod 12 RELIANCE_FRAMEWORK — ulusal düzenleyici otoritenin referans otorite değerlendirmesine dayanabilmesi için mevzuat hükmü taslağı + gerekçe + risk tablosu. Reliance (karar ulusal otoritede kalır) ile tanıma (karar yerine geçer; andlaşma ister) ayrımı her bölümde korunur; önce yetki analizi (G2). Referans otorite listesi uydurulmaz. Argüman = ev bölgesi + işlev kapsamı."
argument-hint: '<ev bölgesi + işlev — örn. "TR: ruhsat değişiklik başvurularında kısaltılmış inceleme">'
---

# /lex-reliance — Mod 12 RELIANCE_FRAMEWORK (reliance çerçevesi taslağı)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 12 RELIANCE_FRAMEWORK** olarak çalıştır. Template: [`templates/reliance-framework.md`](../skills/cureolex/templates/reliance-framework.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Paketi yükle (§1.5)** — ev yargı bölgesi; norm hiyerarşisi ve legistik profil paketten.
3. **Yetki analizi (G2) ÖNCE:** karar yetkisini veren norm reliance'a izin veriyor mu → gereken norm düzeyi. Tanıma öneriliyorsa andlaşma usulü (`mcp__intl-treaty__*`).
4. **Tam-filo (G0):** paket S1 + karşılaştırmalı emsal (uk-legal, fedlex, eurlex, health-policy) — her emsal kendi paket koduyla ve `comparative_benchmark` rolüyle (G11). Erişim/kamu sağlığı kanıtı → evidentia.
5. **Taslak:** 9 maddelik iskelet (template §2); "ulusal karar yetkisinin korunması" maddesi atlanamaz.
6. **Kapılar:** G0, G1, G2, G5, G6, G7, G10, G11. `evidence_ledger` + `home_jurisdiction`.
7. **sci-audit'e delege et** · **kapsam manifestosu + confidence_label** ile bitir.
