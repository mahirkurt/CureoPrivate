# Figma ↔ Carbon İnterop — Görsel QA Doğrulama Protokolü

> Bu referans, `carbon-edupedia` token otorite zincirinin **üçüncü (opsiyonel)
> katmanını** tanımlar: IBM'in resmî **Carbon Design System v11 Figma
> kütüphaneleri** üzerinden Figma MCP araçlarıyla görsel doğrulama. Birincil
> otorite daima `npm @carbon/*` paketleridir (bkz.
> `carbon-child-system.md` §1); Figma katmanı **bileşen anatomisi, durum
> görselleri ve değişken adlandırması** için ek bir doğrulama yüzeyidir —
> token değerinin kaynağı değildir.

## İçindekiler
1. Ne zaman kullanılır (ve kullanılmaz)
2. Ön koşul: kütüphane erişimi
3. Doğrulama akışı (araç sırası)
4. Figma değişken adı ↔ `--cds-*` eşleme tablosu
5. Sapma triyajı kuralı
6. `figma-forge` composability — edupedia ekranlarını Figma'ya itmek
7. Bilinen sınırlamalar

---

## 1. Ne zaman kullanılır (ve kullanılmaz)

**Kullanın:**
- Bir Carbon bileşeninin **anatomisini/durumlarını** görsel olarak doğrulamak
  gerektiğinde (ör. selectable tile'ın seçili durumunda kenar kalınlığı,
  notification'ın durum çubuğu konumu).
- Kullanıcı bir **Figma dosya URL'si** paylaştığında ve edupedia çıktısının o
  dosyadaki Carbon kullanımıyla hizalanması istendiğinde.
- Yeni bir Carbon bileşen deseni şablona eklenmeden önce **ikinci-kaynak
  teyidi** istendiğinde.

**Kullanmayın:**
- Rutin modül üretiminde — şablon zaten otorite-hizalıdır; Figma çağrısı
  gereksiz gecikme ekler.
- Token **hex değeri** sorusunda — değerin kaynağı npm'dir;
  `assets/carbon-v11-authority.json` çevrimdışı yanıt verir.
- `G-TOKEN` kapısı veya `sync_carbon_tokens.py` yerine — bunlar deterministik
  ve çevrimdışıdır.

## 2. Ön koşul: kütüphane erişimi

IBM'in resmî v11 kütüphaneleri Figma Community'de yayımlanır:

| Kütüphane | İçerik |
|---|---|
| **(v11) Carbon Design System — All themes** | 4 tema (White, G10, G90, G100) değişkenleri + çekirdek bileşenler |
| **(v11) Carbon — Text styles** | Tip ölçeği stilleri (heading, body, label, code) |
| **(v11) Carbon — Icons** | 16/20/24/32px ikon bileşenleri |
| **(v11) Carbon — Pictograms** | 48px+ piktogram bileşenleri |

**Kritik kısıt:** Community dosyaları MCP araçlarıyla **doğrudan
erişilemez** — kullanıcının dosyayı **kendi Figma hesabına kopyalaması**
(Community → "Open in Figma") ve oluşan **kopyanın URL'sini** paylaşması
gerekir. Topluluk anahtarıyla (`1157761560874207208` vb.) yapılan doğrudan
çağrılar erişim hatası döndürür. Kullanıcıdan istenmesi gereken format:
`https://www.figma.com/design/<fileKey>/<fileName>?node-id=<id>`

## 3. Doğrulama akışı (araç sırası)

Kullanıcı bir dosya URL'si verdiğinde:

```
1. get_libraries(fileKey)
   → dosyaya bağlı kütüphaneleri listele; Carbon v11 kütüphane anahtarlarını al.

2. search_design_system(fileKey, query, includeLibraryKeys=[...])
   → hedef bileşeni/değişkeni bul (ör. "notification", "tag teal",
     "support-info"). Anahtar kapsamı verilirse sonuç gürültüsü azalır.

3. get_variable_defs(fileKey, nodeId)
   → seçili düğüme bağlı değişken tanımlarını al (ör.
     'support/support-info': #0043ce). Node-spesifik URL gerekir.

4. get_design_context(fileKey, nodeId)  [gerekirse]
   → bileşenin ekran görüntüsü + referans kodu; anatomi doğrulaması için.

5. Karşılaştır: Figma değeri ↔ assets/carbon-v11-authority.json
   → §5 triyaj kuralını uygula.
```

İkon/piktogram doğrulaması için aynı akış Icons/Pictograms kütüphanesine
uygulanır; SVG path'leri `icon-pictogram-svg.md` §2–3'teki gömülü sprite ile
karşılaştırılır.

## 4. Figma değişken adı ↔ `--cds-*` eşleme tablosu

Carbon Figma kütüphanesi değişkenleri **grup/ad** hiyerarşisi kullanır; CSS
özel değişkeni karşılıkları:

| Figma değişkeni | CSS değişkeni |
|---|---|
| `background/background` | `--cds-background` |
| `layer/layer-01` … `layer-03` | `--cds-layer-01..03` |
| `layer/layer-hover-01` / `layer-active-01` / `layer-selected-01` | `--cds-layer-hover-01` vb. |
| `layer-accent/layer-accent-01` / `-hover-01` | `--cds-layer-accent-*` |
| `field/field-01` / `field-hover-01` | `--cds-field-*` |
| `background/background-hover` / `-active` | `--cds-background-hover/active` |
| `border/border-subtle-00` / `-01` | `--cds-border-subtle-00/01` |
| `border/border-strong-01` | `--cds-border-strong` |
| `border/border-tile-01` | `--cds-border-tile` |
| `border/border-interactive` | `--cds-border-interactive` |
| `text/text-primary` / `-secondary` / `-helper` / `-placeholder` / `-on-color` | `--cds-text-*` |
| `icon/icon-primary` / `-secondary` / `-on-color` | `--cds-icon-*` |
| `link/link-primary` / `-hover` | `--cds-link-primary(-hover)` |
| `button/button-primary` / `-hover` / `-active` | `--cds-button-primary-*` |
| `focus/focus` / `focus-inset` | `--cds-focus(-inset)` |
| `support/support-success` / `-error` / `-warning` / `-info` | `--cds-support-*` |
| `notification/notification-background-*` | `--cds-notif-*-bg` |
| `misc/highlight` / `overlay` / `skeleton-*` | `--cds-highlight` vb. |
| `tag/tag-background-X` / `tag-color-X` | motor `ACCENT_STRONG` çiftleri |

Tip stilleri (`Heading 04`, `Body 02`, `Label 01`, `Code 02`) `@carbon/type`
adlarıyla aynıdır; spacing değişkenleri (`spacing/spacing-01..13`)
`--cds-spacing-*` ile birebirdir.

## 5. Sapma triyajı kuralı

Figma değeri ile npm otoritesi çelişirse:

1. **npm kazanır.** Şablon ve `authority.json` npm değerini korur.
2. Figma sapması **rapor edilir** (kullanıcıya: "Figma kütüphane kopyanız
   muhtemelen eski bir yayın; All-themes kütüphanesini güncelleyin").
3. Sapma `@carbon/themes` sürüm farkından kaynaklanıyorsa (ör. kullanıcının
   kopyası v11.x-eski), `sync_carbon_tokens.py --refresh` ile npm tarafı
   tazelenir ve karşılaştırma yinelenir.
4. Yalnız **anatomi** farkı varsa (değer aynı, görsel yapı farklı), şablonun
   bileşen deseni `get_design_context` ekran görüntüsüne göre gözden geçirilir
   — bu, token değil **desen** güncellemesidir.

## 6. `figma-forge` composability — edupedia ekranlarını Figma'ya itmek

Ters yön (edupedia → Figma) bu skill'in kapsamı dışındadır; **`figma-forge`**
skill'i ile yapılır:

- `figma-forge`'un **Carbon v11 yerleşik mapper'ı** `--cds-*` token'larını
  Figma Variables'a, edupedia bileşen desenlerini (stepper, tile, notification,
  tag) variant ComponentSet'lere dönüştürür.
- Akış: edupedia modülü üret → `figma-forge` `TOKENS_IMPORT` modu ile
  `carbon-v11-authority.json`'u (W3C DTCG-benzeri yapı) Variables olarak içe
  aktar → `COMPONENTS_BUILD` ile ekran iskeletini kur.
- Bu yol, öğretmen/veli paydaşlarına modül tasarımını Figma üzerinde gözden
  geçirtmek istendiğinde kullanılır.

## 7. Bilinen sınırlamalar

- Community dosyalarına kopyasız erişim yok (bkz. §2) — akış kullanıcı
  URL'sine bağımlıdır.
- `get_variable_defs` **node-spesifik** çalışır; dosya-geneli değişken dökümü
  için kullanıcının değişkenleri kullanan bir frame URL'si gerekir.
- Figma kütüphanesindeki tema modları (White/G10/G90/G100) 4'lüdür; edupedia
  yalnız White + G100 kullanır — G10/G90 değerleri karşılaştırma dışıdır.
- Figma tarafındaki `light`/`dark` mod adlandırması kütüphane sürümüne göre
  değişebilir; eşlemeyi ada değil **değere** göre yapın.
