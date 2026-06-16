# kap-fund-disclosures.md — KAP Fon Duyuru Taksonomisi

KAP fon duyuruları `Borsa get_news`/`get_regulations` veya fon-mcp registry üzerinden taranır.

## Duyuru türleri & önem derecesi
| Tür | Önem | Etki |
|---|---|---|
| Kurucu / portföy yönetim şirketi değişikliği | Yüksek | Yönetim devamlılığı, strateji riski |
| İçtüzük / izahname tadili | Yüksek | Strateji/risk profili/gider değişebilir |
| Fon dönüşümü / birleşmesi | Yüksek | Kategori/risk profili kayması |
| Tasfiye / fona kapanma | Yüksek | Likidite/çıkış riski |
| Gider oranı (TER) değişikliği | Orta | Net getiri etkisi |
| Eşik/strateji parametre değişikliği | Orta | Davranış kayması |
| Periyodik raporlama | Düşük | Bilgilendirme |

## İşleme kuralı
- Açık/yeni duyurular `fund_state.open_kap[]`'a (izleme) ve rapor §İzlenecekler'e taşınır.
- Üçüncü-taraf (kurucu/yönetici) hakkında değer yargısı yapılmaz; olgu + kaynak damgası verilir.
- Yüksek önem → karar-destek notunda öne çıkarılır; karşıt-senaryo tetikleyicisi olabilir.
