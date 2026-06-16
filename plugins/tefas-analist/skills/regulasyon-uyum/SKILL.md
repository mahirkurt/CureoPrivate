---
name: regulasyon-uyum
description: >-
  regulasyon-uyum — SPK uyum + KAP fon-duyuru katmanı. Her çıktının kanonik SPK feragatini
  (yatırım danışmanlığı değildir) BİREBİR içermesini zorunlu kılar; kişiselleştirilmiş al/sat
  dilini engeller; KAP fon duyurularını (kurucu/yönetici değişikliği, içtüzük tadili, fon
  dönüşümü, tasfiye) işler; scripts/rapor_lint.py ile yayım-öncesi denetim yapar (G7 zorunlu
  kapı). USE for — SPK uyumu, feragat, yatırım danışmanlığı sınırı, KAP fon duyurusu, içtüzük
  değişikliği, fon dönüşümü, uyum denetimi, rapor lint. EN — SPK compliance, disclaimer, fund
  disclosure, advisory boundary, report lint. When in doubt USE.
---

# regulasyon-uyum — SPK Uyum & KAP Duyuru Katmanı

**Süit:** tefas-analist · kaynak skill (her modda G7). > Connector için
**[../../CONNECTORS.md](../../CONNECTORS.md)** normatiftir.

## Ne Zaman Çağrılır
Her rapor yayımlanmadan önce (G7 zorunlu kapı) ve KAP fon duyurusu işlenirken.

## 0. Scope — SPK Sınırı
Çıktı **karar-destek**; SPK yatırım danışmanlığı/portföy yöneticiliği/al-sat tavsiyesi
**değildir**. Kişiselleştirilmiş "şu kadar al/sat" talebi → karar-destek diline çevrilir
(senaryo + tetikleyici + geçersizleşme; emir-kipi yok).

## Kanonik SPK Feragati (BİREBİR — değiştirilemez, kısaltılamaz)
`references/compliance.md` içindeki metin, `rapor_lint.py` tarafından **string-match** ile
denetlenir. Her raporun sonunda birebir bulunmalıdır:

> Bu içerik yalnızca bilgilendirme ve karar-destek amaçlıdır; SPK yatırım danışmanlığı,
> portföy yöneticiliği veya al/sat tavsiyesi niteliği taşımaz. Fon getirileri geçmişe dönük
> olup gelecekteki getirinin garantisi değildir; NAV verileri gün-sonu (EOD) ve gecikmeli
> olabilir. Yatırım kararları; kişinin kendi risk profili, bağımsız araştırması ve
> gerektiğinde SPK lisanslı bir yatırım kuruluşuna/danışmanına danışılarak alınmalıdır.

## KAP Fon Duyuruları
`Borsa get_news`/`get_regulations` (veya fon-mcp registry) ile kurucu/yönetici değişikliği,
içtüzük tadili, fon dönüşümü/birleşmesi, tasfiye, gider oranı değişikliği taranır. Önem
derecesi (`references/kap-fund-disclosures.md`): Yüksek/Orta/Düşük.

## G7 Uyum Kapısı (BLOKER, 8 kontrol — `scripts/rapor_lint.py`)
1. Kanonik SPK feragati birebir mevcut. 2. Emir-kipi yok ("al", "sat", "satın alın").
3. Sayısal iddialar tarihli (as-of). 4. Ham makine çıktısı/MCP adı yok (Katman A).
5. EOD/gecikme beyanı. 6. Üçüncü-taraf (kurucu/yönetici) etiketi. 7. Senaryo/karşıt-senaryo
mevcut. 8. Kesinlik iddiası yok ("kesin", "garanti"). **Geçmezse rapor yayımlanmaz.**

Kullanım: `python3 scripts/rapor_lint.py --file rapor.md` → `{passed, errors[], warnings[]}`.

## Referanslar
- `references/compliance.md` (kanonik feragat + SPK sınır doktrini)
- `references/report-style.md` (house style: bilimsel Türkçe, sayı disiplini, "tavsiye
  diline çevirme" rehberi)
- `references/kap-fund-disclosures.md` (duyuru taksonomisi + önem derecesi)
