---
name: kronoloji
description: Hicrî/Rumî/Maliî ↔ Miladî tarih dönüşümü + ebced/kronogram çözümü yapar (CHRONOLOGY_CONVERSION modu).
---

`vekayinuvis` skill'ini **CHRONOLOGY_CONVERSION** modunda çalıştır.

Girdi: kullanıcının belirttiği tarih veya kronogram (örn. "15 Receb 1287"). ottoman-archives
hesaplama katmanını kullan: convert_date / parse_ottoman_date (takvim dönüşümü) ve calc_ebced /
tarih_dusur (kronogram-tarih düşürme).

Çıktı: **üç-takvim tablosu** + gün-isim doğrulaması + ek bağlam (o günün önemli
olayları, ilgili belgeler). Rumî sınır dönem (1839–1925) için doğrulamayı
zorunlu yap.
