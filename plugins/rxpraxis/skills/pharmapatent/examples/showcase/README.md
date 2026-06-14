# pharmapatent-showcase.jsx

Interactive React demo artifact for the pharmapatent skill ecosystem.

## Özellikler

IBM Carbon Design System + IBM Plex tipografi ile tasarlanmış, 6 sekmeli etkileşimli gösterge paneli:

1. **Genel Bakış** — 8 stat kartı + 4-katmanlı ekosistem mimari diyagramı
2. **Operasyonel Modlar** — 12 modun kart grid'i + modül detay paneli (bölüm sayısı, zorunlu görsel, hedef kitle)
3. **Terapötik Alanlar** — 9 domain derinlik dosyası + IP odak açıklaması
4. **Scriptler** — 10 Python script'in çalıştırma bilgisiyle tablosu
5. **Görsel Kütüphane** — 33 visualize widget şablonunun rapor tipine göre gruplaması
6. **Bilgi Grafiği** — Centrality bar chart + graph istatistikleri

## Kullanım

### Claude artifact olarak
```
React component olarak doğrudan bir Claude artifact'i içinde render edilebilir.
Default export: <PharmapatentShowcase />
```

### Standalone React projesi
```bash
# Vite + React + TypeScript veya JavaScript projesinde
npm install lucide-react
# Font için:
#   index.html'e IBM Plex Sans + IBM Plex Mono CDN link ekle
```

## Bağımlılıklar

- `react` (≥18)
- `lucide-react` (icon kütüphanesi — 20+ icon kullanılıyor)

## Stil

- IBM Carbon Design System v11 renkleri
- IBM Plex Sans / Mono font ailesi (sistem fallback dahil)
- Carbon'ın 4px grid + 16px padding standartları
- Tüm renk tokenleri `carbon` object'inde tanımlı

## Veri

`ECOSYSTEM` object'i pharmapatent v1.6.0 snapshot'unu içerir:
- 12 modes
- 9 domains
- 10 scripts
- 12 references
- 9 stats (files, edges, vs.)

Skill güncellendiğinde bu object güncellenmeli.

## Lisans

Internal use. pharmapatent skill v1.6.0 ile birlikte dağıtılmakta.
