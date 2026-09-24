---
name: lex-maturity
description: "Mod 10 REGULATORY_MATURITY — ulusal düzenleyici sistemin mevzuat tabanını WHO GBT işlev yapısına (RS + MA/VL/MC/LI/RI/LT/CT/LR; olgunluk 1–4, hedef düzey 3) göre haritalar ve mevzuattan okunabilen açıkları gösterir. Resmî GBT değerlendirmesi DEĞİLDİR; olgunluk düzeyi atamaz, gösterge kimliği uydurmaz. Argüman = yargı bölgesi + ürün sınıfı."
argument-hint: '<yargı bölgesi + kapsam — örn. "TR ilaç: VL ve CT işlevlerinin yasal dayanağı">'
---

# /lex-maturity — Mod 10 REGULATORY_MATURITY (WHO GBT açık analizi)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 10 REGULATORY_MATURITY** olarak çalıştır. Template: [`templates/regulatory-maturity-gbt.md`](../skills/cureolex/templates/regulatory-maturity-gbt.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Paketi yükle (§1.5).** Yargı bölgesini argümandan çöz → `jurisdictions/<kod>/jurisdiction_pack.yaml`. Paket yoksa: `manual_required` + mevcut paketler listesi; paket `draft` ise çıktı en fazla LOW (CC-6) ve başlıkta taslak uyarısı.
3. **Tam-filo (G0)** — paketin S1 bağlayıcısı + `intl-treaty` + `oecd` + `openathens` (GBT yöntem literatürü). İşlev başına dayanak normu S1'de ara; boş sonuç yokluk kanıtı değildir.
4. **GBT çerçevesi** yalnız doğrulanmış yapıyla: RS + 8 işlev, düzey 1–4, düzey 3 asgari hedef. **Gösterge kimliği/metni modelin belleğinden YAZILMAZ** — WHO'nun güncel GBT belgesinden alıntılanamıyorsa satır `manual_required`.
5. **Kapılar:** G0, G2, G5, G6, G7, G10 (norm yürürlükte mi, as-of), G11 (yabancı reliance kaynakları doğru rolde mi). `evidence_ledger` + `home_jurisdiction`.
6. **sci-audit'e delege et.**
7. **Kapsam manifestosu + confidence_label** (`jurisdiction_pack` + `confidence_ceiling` alanları) ile bitir.
