# references/visualize-widget-kutuphanesi.md — Visualize Widget Template Kütüphanesi

> `visualize:show_widget` tool'u ile kullanılmak üzere hazırlanmış, IBM Carbon Design System renk paleti + tipografi (Plex Sans/Plex Serif/Plex Mono) standartlarına uyumlu 30+ görsel şablonu. Tüm görseller rapor-sablonlari.md'deki 9 rapor tipinin zorunlu görsellerini kapsar. Claude, `visualize:read_me` modülünü yükledikten sonra bu kütüphaneden ilgili şablonu alıp spesifik vakaya uyarlayarak `visualize:show_widget` çağrısını yapar.

## İlişkili Protokoller

- **`gorsel-standartlari.md`** — Görsel standartların kaynak dökümantasyonu (renkler, fontlar, boyutlar, accessibility)
- **`rapor-sablonlari.md`** — 10 rapor tipi + her birinde hangi görsellerin zorunlu olduğu
- **`fto-invalidity-protokol.md`** — FTO + Invalidity spesifik görsel kuralları
- **`biyobenzer-yol.md`** — Biosimilar Gantt görselleri için rehber

## İçindekiler

1. Kullanım kuralları ve çağrı disiplini
2. Carbon renk sabitleri ve CSS değişkenleri
3. §1 FTO Raporu görselleri (4 şablon)
4. §2 Invalidity Briefing görselleri (4 şablon)
5. §3 Landscape Raporu görselleri (4 şablon)
6. §4 Lifecycle Yol Haritası görselleri (3 şablon)
7. §5 Pazara Giriş Takvimi görselleri (2 şablon)
8. §6 Litigation Briefing görselleri (3 şablon)
9. §7 Due Diligence görselleri (4 şablon)
10. §8 Opposition Briefing görselleri (3 şablon)
11. §9 Biosimilar Pathway görselleri (4 şablon)
12. §10 Expert Witness Report görselleri (2 şablon)

---

## 1. Kullanım Kuralları

### Çağrı disiplini

Claude, bir rapor üretirken görsel ekleme ihtiyacı olduğunda:

1. **Önce**: `visualize:read_me` modülünü yükler (`diagram` veya `chart` tipine göre)
2. **Sonra**: Bu kütüphaneden ilgili şablonu alır
3. **Sonra**: Şablondaki placeholder değerleri (`{{PLACEHOLDER}}`) vakaya özgü içerikle doldurur
4. **Sonra**: `visualize:show_widget` çağrısını yapar
5. **Kullanıcıya söylemez**: Hangi şablonu kullandığını, read_me çağrısını yaptığını — doğrudan görselin faydasını açıklar

### İçerik kuralları

- Her görsel IBM Carbon Gray 10 arka plan + Carbon Gray 100 text
- Status renkleri: green (support/pass) / red (blocker/fail) / yellow (caution) / blue (info)
- Font: IBM Plex Sans (başlık), IBM Plex Sans (body), IBM Plex Mono (kod/sayısal)
- Veri etiketleri mutlaka dahil (hover yetmez, statik görsel)
- Legend zorunlu
- Accessibility: `role="img"` + `aria-label` zorunlu

### Placeholder sözleşmesi

Tüm şablonlarda placeholder'lar `{{NAME}}` formatında:
- `{{TITLE}}` — görsel başlığı
- `{{DATA_*}}` — veri noktaları
- `{{COLOR_*}}` — özel renkler (varsayılanı override)
- `{{ASSET_NAME}}` — ürün/ilaç adı
- `{{YEAR_*}}` — yıllar

---

## 2. Carbon Renk Sabitleri

Tüm şablonlarda kullanılan CSS değişkenleri (visualize platformunca sağlanır; fallback olarak inline tanımlar):

```css
--cds-background: #f4f4f4;        /* Gray 10 */
--cds-layer: #ffffff;             /* White */
--cds-text-primary: #161616;      /* Gray 100 */
--cds-text-secondary: #525252;    /* Gray 70 */
--cds-support-error: #da1e28;     /* Red 60 — blocker/fail */
--cds-support-success: #24a148;   /* Green 60 — pass/clean */
--cds-support-warning: #f1c21b;   /* Yellow 30 — caution */
--cds-support-info: #0f62fe;      /* Blue 60 — info */
--cds-border-subtle: #c6c6c6;     /* Gray 30 */

/* Cool Gray (kategoriler için palette) */
--cds-cat-1: #0f62fe;  /* Blue */
--cds-cat-2: #8a3ffc;  /* Purple */
--cds-cat-3: #007d79;  /* Teal */
--cds-cat-4: #ff832b;  /* Orange */
--cds-cat-5: #fa4d56;  /* Red */
--cds-cat-6: #198038;  /* Green */

/* Typography */
--font-sans: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
--font-mono: 'IBM Plex Mono', 'Consolas', monospace;
--font-serif: 'IBM Plex Serif', 'Georgia', serif;
```

---

## 3. §1 FTO Raporu Görselleri

### 3.1. Patent × Ülke Heatmap (`fto-patent-country-heatmap`)

**Amaç**: Her patent için hangi ülkede FTO durumunun ne olduğunu gösteren matrix. Renk: yeşil (temiz) / sarı (dikkat) / kırmızı (blocker).

```svg
<svg viewBox="0 0 700 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans', sans-serif; fill: #161616; }
    .axis { font: 400 11px 'IBM Plex Sans', sans-serif; fill: #525252; }
    .cell-label { font: 500 10px 'IBM Plex Mono', monospace; fill: #ffffff; text-anchor: middle; }
    .legend { font: 400 11px 'IBM Plex Sans', sans-serif; fill: #161616; }
  </style>
  
  <rect width="700" height="400" fill="#f4f4f4"/>
  <text class="title" x="30" y="30">{{TITLE}}</text>
  
  <!-- Y-axis: Patent numaraları -->
  <text class="axis" x="25" y="80" text-anchor="end">{{PATENT_1}}</text>
  <text class="axis" x="25" y="120" text-anchor="end">{{PATENT_2}}</text>
  <text class="axis" x="25" y="160" text-anchor="end">{{PATENT_3}}</text>
  <text class="axis" x="25" y="200" text-anchor="end">{{PATENT_4}}</text>
  <text class="axis" x="25" y="240" text-anchor="end">{{PATENT_5}}</text>
  
  <!-- X-axis: Ülkeler -->
  <text class="axis" x="80" y="60" text-anchor="middle">TR</text>
  <text class="axis" x="180" y="60" text-anchor="middle">US</text>
  <text class="axis" x="280" y="60" text-anchor="middle">EP</text>
  <text class="axis" x="380" y="60" text-anchor="middle">JP</text>
  <text class="axis" x="480" y="60" text-anchor="middle">CN</text>
  <text class="axis" x="580" y="60" text-anchor="middle">BR</text>
  
  <!-- Heatmap grid — her satır bir patent, her sütun bir ülke -->
  <!-- Doldurma renkleri: #24a148 (temiz), #f1c21b (dikkat), #da1e28 (blocker), #c6c6c6 (yok) -->
  
  <!-- Patent 1 -->
  <rect x="30" y="65" width="100" height="35" fill="{{P1_TR_COLOR}}"/><text class="cell-label" x="80" y="87">{{P1_TR_LABEL}}</text>
  <rect x="130" y="65" width="100" height="35" fill="{{P1_US_COLOR}}"/><text class="cell-label" x="180" y="87">{{P1_US_LABEL}}</text>
  <rect x="230" y="65" width="100" height="35" fill="{{P1_EP_COLOR}}"/><text class="cell-label" x="280" y="87">{{P1_EP_LABEL}}</text>
  <rect x="330" y="65" width="100" height="35" fill="{{P1_JP_COLOR}}"/><text class="cell-label" x="380" y="87">{{P1_JP_LABEL}}</text>
  <rect x="430" y="65" width="100" height="35" fill="{{P1_CN_COLOR}}"/><text class="cell-label" x="480" y="87">{{P1_CN_LABEL}}</text>
  <rect x="530" y="65" width="100" height="35" fill="{{P1_BR_COLOR}}"/><text class="cell-label" x="580" y="87">{{P1_BR_LABEL}}</text>
  
  <!-- Patentler 2-5 için benzer yapı, 40px aralıklı y ofset -->
  
  <!-- Legend -->
  <g transform="translate(30, 320)">
    <rect x="0" y="0" width="18" height="18" fill="#24a148"/>
    <text class="legend" x="26" y="13">Temiz (FTO risk yok)</text>
    <rect x="170" y="0" width="18" height="18" fill="#f1c21b"/>
    <text class="legend" x="196" y="13">Dikkat (design-around)</text>
    <rect x="360" y="0" width="18" height="18" fill="#da1e28"/>
    <text class="legend" x="386" y="13">Blocker</text>
    <rect x="480" y="0" width="18" height="18" fill="#c6c6c6"/>
    <text class="legend" x="506" y="13">Ülkede patent yok</text>
  </g>
  
  <text class="axis" x="30" y="375" fill="#525252">Kaynak: EPAAT + USPTO + Espacenet · {{DATE}}</text>
</svg>
```

**Kullanım**: FTO raporu §3 için ana görsel. `family-tracer.py --example` çıktısındaki coverage matrix'ten türetilebilir.

### 3.2. İstem Özellik Matrisi (`fto-feature-matrix`)

**Amaç**: Bir patent istem özellikleri (F1, F2, F3...) vs müvekkil ürünün özellikleri karşılaştırma tablosu.

```html
<div style="background: #f4f4f4; padding: 24px; font-family: 'IBM Plex Sans', sans-serif;">
  <h3 style="font-weight: 600; color: #161616; margin: 0 0 16px 0;">{{TITLE}}</h3>
  <p style="color: #525252; margin: 0 0 16px 0; font-size: 12px;">Patent: {{PATENT_NO}} · İstem {{CLAIM_NO}}</p>
  
  <table style="width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #c6c6c6;">
    <thead>
      <tr style="background: #e0e0e0;">
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #161616; font-weight: 600; width: 60px;">F#</th>
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #161616; font-weight: 600;">İstem özelliği</th>
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #161616; font-weight: 600;">Müvekkil ürünü</th>
        <th style="padding: 12px; text-align: center; border-bottom: 2px solid #161616; font-weight: 600; width: 120px;">Eşleşme</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; font-family: 'IBM Plex Mono'; font-weight: 500;">F1</td>
        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{{F1_CLAIM}}</td>
        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{{F1_PRODUCT}}</td>
        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; background: {{F1_COLOR}}; color: #ffffff; font-weight: 600;">{{F1_MATCH}}</td>
      </tr>
      <!-- F2, F3, ... için tekrar -->
    </tbody>
  </table>
  
  <div style="margin-top: 16px; padding: 12px; background: {{VERDICT_BG}}; border-left: 4px solid {{VERDICT_BORDER}}; color: {{VERDICT_TEXT}};">
    <strong>Sonuç:</strong> {{VERDICT_TEXT_CONTENT}}
  </div>
</div>
```

**Renk kuralları**:
- Eşleşme = EVET → `background: #da1e28; color: #ffffff` (ihlal riski yüksek)
- Eşleşme = HAYIR → `background: #24a148; color: #ffffff`
- Eşleşme = KISMEN → `background: #f1c21b; color: #161616`

### 3.3. Design-Around Karar Ağacı (`fto-design-around-tree`)

**Amaç**: Risk tespit edilen patent için design-around alternatiflerinin karar ağacı.

```
Mermaid flowchart TD syntax:

flowchart TD
    A["{{TARGET_PATENT}}<br/>Risk tespit edildi"]:::risk
    A --> B{"{{CRITICAL_FEATURE}}<br/>etrafından dolaşılabilir mi?"}
    B -->|Evet| C["Option 1: {{ALT_1}}"]:::option
    B -->|Evet| D["Option 2: {{ALT_2}}"]:::option
    B -->|Hayır| E["Yalnızca lisans<br/>veya pazar beklenir"]:::risk
    C --> F["Klinik equivalence<br/>çalışması: {{COST_1}}"]:::detail
    D --> G["Formülasyon değişiklik<br/>maliyet: {{COST_2}}"]:::detail
    F --> H{Kabul?}
    G --> H
    H -->|Evet| I["Go: Lansman {{YEAR}}"]:::success
    H -->|Hayır| E
    
    classDef risk fill:#fff1f1,stroke:#da1e28,stroke-width:2px,color:#161616
    classDef option fill:#e5f6ff,stroke:#0f62fe,stroke-width:2px,color:#161616
    classDef detail fill:#f4f4f4,stroke:#525252,stroke-width:1px,color:#161616
    classDef success fill:#defbe6,stroke:#24a148,stroke-width:2px,color:#161616
```

**Çağrı**: `visualize:show_widget` için SVG bölümüne mermaid HTML render edilebilir; ya da doğrudan SVG.

### 3.4. LOE Gantt Zaman Çizelgesi (`fto-loe-gantt`)

**Amaç**: Patent expiry + veri imtiyazı + pazara giriş + SGK entegrasyonu paralel zamanlama.

```svg
<svg viewBox="0 0 900 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .year { font: 400 11px 'IBM Plex Mono'; fill: #525252; text-anchor: middle; }
    .milestone { font: 400 10px 'IBM Plex Sans'; fill: #161616; }
    .bar-label { font: 600 11px 'IBM Plex Sans'; fill: #ffffff; }
  </style>
  
  <rect width="900" height="350" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{TITLE}} — Loss of Exclusivity Zaman Çizelgesi</text>
  
  <!-- X-axis yılları — 10 yıl aralığı -->
  <line x1="180" y1="70" x2="860" y2="70" stroke="#c6c6c6"/>
  <text class="year" x="248" y="65">{{YEAR_0}}</text>
  <text class="year" x="316" y="65">{{YEAR_1}}</text>
  <text class="year" x="384" y="65">{{YEAR_2}}</text>
  <text class="year" x="452" y="65">{{YEAR_3}}</text>
  <text class="year" x="520" y="65">{{YEAR_4}}</text>
  <text class="year" x="588" y="65">{{YEAR_5}}</text>
  <text class="year" x="656" y="65">{{YEAR_6}}</text>
  <text class="year" x="724" y="65">{{YEAR_7}}</text>
  <text class="year" x="792" y="65">{{YEAR_8}}</text>
  <text class="year" x="860" y="65">{{YEAR_9}}</text>
  
  <!-- Bar 1: Temel patent -->
  <text class="label" x="170" y="108" text-anchor="end">Temel patent</text>
  <rect x="{{PATENT_START_X}}" y="92" width="{{PATENT_WIDTH}}" height="20" fill="#0f62fe"/>
  <text class="bar-label" x="{{PATENT_LABEL_X}}" y="107">{{PATENT_EXPIRY}}</text>
  
  <!-- Bar 2: Formülasyon patenti -->
  <text class="label" x="170" y="148" text-anchor="end">Formülasyon patenti</text>
  <rect x="{{FORM_START_X}}" y="132" width="{{FORM_WIDTH}}" height="20" fill="#8a3ffc"/>
  <text class="bar-label" x="{{FORM_LABEL_X}}" y="147">{{FORM_EXPIRY}}</text>
  
  <!-- Bar 3: Veri imtiyazı (6 yıl) -->
  <text class="label" x="170" y="188" text-anchor="end">Veri imtiyazı</text>
  <rect x="{{DATA_START_X}}" y="172" width="{{DATA_WIDTH}}" height="20" fill="#007d79"/>
  <text class="bar-label" x="{{DATA_LABEL_X}}" y="187">{{DATA_EXPIRY}}</text>
  
  <!-- Bar 4: Bolar dönemi (jenerik hazırlık) -->
  <text class="label" x="170" y="228" text-anchor="end">Bolar hazırlık</text>
  <rect x="{{BOLAR_START_X}}" y="212" width="{{BOLAR_WIDTH}}" height="20" fill="#f1c21b"/>
  <text class="bar-label" x="{{BOLAR_LABEL_X}}" y="227" fill="#161616">Biyoeşdeğerlik + dossier</text>
  
  <!-- Bar 5: Praktik pazara giriş -->
  <text class="label" x="170" y="268" text-anchor="end">Pazara giriş</text>
  <line x1="{{LAUNCH_X}}" y1="252" x2="{{LAUNCH_X}}" y2="278" stroke="#da1e28" stroke-width="3"/>
  <circle cx="{{LAUNCH_X}}" cy="265" r="8" fill="#da1e28"/>
  <text class="milestone" x="{{LAUNCH_X}}" y="293" text-anchor="middle">{{LAUNCH_DATE}}</text>
  
  <!-- Legend -->
  <g transform="translate(20, 310)">
    <rect x="0" y="0" width="14" height="14" fill="#0f62fe"/><text class="label" x="20" y="12">Patent</text>
    <rect x="100" y="0" width="14" height="14" fill="#8a3ffc"/><text class="label" x="120" y="12">Evergreening patent</text>
    <rect x="280" y="0" width="14" height="14" fill="#007d79"/><text class="label" x="300" y="12">Veri imtiyazı</text>
    <rect x="430" y="0" width="14" height="14" fill="#f1c21b"/><text class="label" x="450" y="12">Bolar</text>
    <circle cx="520" cy="7" r="6" fill="#da1e28"/><text class="label" x="532" y="12">Pazara giriş</text>
  </g>
</svg>
```

**Kullanım**: `loe-calculator.py` çıktısından doğrudan doldurulabilir. §1 FTO + §5 Pazara Giriş Takvimi raporlarında ortak.

---

## 4. §2 Invalidity Briefing Görselleri

### 4.1. Mozaik Tablosu (`invalidity-mosaic`)

**Amaç**: Prior art × istem özellikleri matrisi — her hücre kapsama derecesi.

```html
<div style="background: #f4f4f4; padding: 24px; font-family: 'IBM Plex Sans';">
  <h3 style="font-weight: 600; margin: 0 0 8px 0;">{{TITLE}} — Yenilik Mozaiği</h3>
  <p style="color: #525252; margin: 0 0 16px 0; font-size: 12px;">Hedef: {{TARGET_PATENT}} İstem {{CLAIM_NO}}</p>
  
  <table style="width: 100%; border-collapse: collapse; background: #ffffff;">
    <thead>
      <tr style="background: #e0e0e0;">
        <th style="padding: 10px; border: 1px solid #c6c6c6; text-align: left; width: 180px;">Özellik</th>
        <th style="padding: 10px; border: 1px solid #c6c6c6; text-align: center;">{{PA1_ID}}</th>
        <th style="padding: 10px; border: 1px solid #c6c6c6; text-align: center;">{{PA2_ID}}</th>
        <th style="padding: 10px; border: 1px solid #c6c6c6; text-align: center;">{{PA3_ID}}</th>
        <th style="padding: 10px; border: 1px solid #c6c6c6; text-align: center;">{{PA4_ID}}</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding: 10px; border: 1px solid #c6c6c6; font-family: 'IBM Plex Mono'; font-weight: 500;">F1: {{F1_NAME}}</td>
        <td style="padding: 10px; border: 1px solid #c6c6c6; text-align: center; background: {{F1_PA1_BG}};">{{F1_PA1}}</td>
        <td style="padding: 10px; border: 1px solid #c6c6c6; text-align: center; background: {{F1_PA2_BG}};">{{F1_PA2}}</td>
        <td style="padding: 10px; border: 1px solid #c6c6c6; text-align: center; background: {{F1_PA3_BG}};">{{F1_PA3}}</td>
        <td style="padding: 10px; border: 1px solid #c6c6c6; text-align: center; background: {{F1_PA4_BG}};">{{F1_PA4}}</td>
      </tr>
      <!-- F2, F3, ... -->
      <tr style="background: #161616; color: #ffffff; font-weight: 600;">
        <td style="padding: 12px;">Tam kapsama?</td>
        <td style="padding: 12px; text-align: center;">{{PA1_COVERAGE}}</td>
        <td style="padding: 12px; text-align: center;">{{PA2_COVERAGE}}</td>
        <td style="padding: 12px; text-align: center;">{{PA3_COVERAGE}}</td>
        <td style="padding: 12px; text-align: center;">{{PA4_COVERAGE}}</td>
      </tr>
    </tbody>
  </table>
  
  <p style="font-size: 11px; color: #525252; margin-top: 12px;">
    ✓ Açıklanmış · ○ Kısmen · ✗ Açıklanmamış · Yeşil hücre: eşleşme var (yenilik tehdidi)
  </p>
</div>
```

### 4.2. Invalidity Radar Chart (`invalidity-radar`)

**Amaç**: 5 invalidity ekseninde (yenilik, buluş basamağı, yeterli açıklama, sanayi uygulanabilirlik, Markush coverage) saldırı kuvveti.

```svg
<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; text-anchor: middle; }
    .axis { font: 500 11px 'IBM Plex Sans'; fill: #161616; text-anchor: middle; }
    .grid { stroke: #c6c6c6; stroke-width: 0.5; fill: none; }
    .value-label { font: 600 11px 'IBM Plex Mono'; fill: #161616; }
  </style>
  
  <rect width="500" height="500" fill="#f4f4f4"/>
  <text class="title" x="250" y="25">{{TITLE}}</text>
  
  <!-- Grid polygons (10, 20, ..., 50 rating) -->
  <g transform="translate(250, 250)">
    <polygon class="grid" points="0,-160 152,-49 94,129 -94,129 -152,-49"/>
    <polygon class="grid" points="0,-120 114,-37 71,97 -71,97 -114,-37"/>
    <polygon class="grid" points="0,-80 76,-25 47,65 -47,65 -76,-25"/>
    <polygon class="grid" points="0,-40 38,-12 24,32 -24,32 -38,-12"/>
    
    <!-- Data polygon -->
    <polygon fill="#0f62fe" fill-opacity="0.35" stroke="#0f62fe" stroke-width="2"
             points="{{AX_NOVELTY}} {{AX_INVENTIVE}} {{AX_SUFFICIENCY}} {{AX_INDUSTRIAL}} {{AX_MARKUSH}}"/>
    
    <!-- Axis labels -->
    <text class="axis" x="0" y="-175">Yenilik ({{NOV_SCORE}})</text>
    <text class="axis" x="170" y="-49">Buluş basamağı ({{INV_SCORE}})</text>
    <text class="axis" x="100" y="150">Yeterli açıklama ({{SUF_SCORE}})</text>
    <text class="axis" x="-100" y="150">Sanayi uygulanabilirlik ({{IND_SCORE}})</text>
    <text class="axis" x="-170" y="-49">Markush ({{MKS_SCORE}})</text>
  </g>
  
  <text class="axis" x="250" y="480" fill="#525252">Skor 0-100 · Yüksek = güçlü saldırı vektörü</text>
</svg>
```

### 4.3. Citation Network (`invalidity-citation-network`)

**Amaç**: Hedef patent + prior art'lar + bağlantılar (backward + forward citations).

**Mermaid flowchart**:

```
flowchart LR
    PA1["{{PA1_ID}}<br/>{{PA1_YEAR}}"]:::prior
    PA2["{{PA2_ID}}<br/>{{PA2_YEAR}}"]:::prior
    PA3["{{PA3_ID}}<br/>{{PA3_YEAR}}"]:::prior
    NPL1["NPL: {{NPL1_AUTHOR}}<br/>{{NPL1_JOURNAL}} {{NPL1_YEAR}}"]:::npl
    NPL2["NPL: {{NPL2_AUTHOR}}<br/>{{NPL2_JOURNAL}} {{NPL2_YEAR}}"]:::npl
    TARGET(["{{TARGET_ID}}<br/>{{TARGET_YEAR}}<br/>HEDEF"]):::target
    
    PA1 -->|yenilik| TARGET
    PA2 -->|buluş basamağı| TARGET
    PA3 -->|buluş basamağı| TARGET
    NPL1 -->|tam sınıf bilgisi| TARGET
    NPL2 -->|motivation| TARGET
    PA1 -.-> PA2
    
    classDef target fill:#ffd7d9,stroke:#da1e28,stroke-width:3px,color:#161616
    classDef prior fill:#e5f6ff,stroke:#0f62fe,stroke-width:2px,color:#161616
    classDef npl fill:#d9fbfb,stroke:#007d79,stroke-width:1.5px,color:#161616
```

### 4.4. Forum Karar Ağacı (`invalidity-forum-tree`)

```
flowchart TD
    START{Invalidity forum seçimi}
    START -->|AB geniş etki gerekli| EPO["EPO Opposition<br/>9 ay pencere"]:::primary
    START -->|Sadece TR| TR["TÜRKPATENT YİDK<br/>+ FSHHM"]:::secondary
    START -->|Sadece US| US["USPTO PTAB IPR<br/>+ CAFC"]:::secondary
    START -->|Çoklu jurisdiksiyon| MULTI["Çoklu ulusal<br/>hükümsüzlük"]:::warning
    
    EPO -->|temyiz| BOA["Board of Appeal"]:::detail
    TR -->|karar itirazı| FSHHM["FSHHM inceleme"]:::detail
    US -->|temyiz| CAFC["CAFC inceleme"]:::detail
    
    BOA --> DONE(["Karar"]):::done
    FSHHM --> DONE
    CAFC --> DONE
    MULTI --> DONE
    
    classDef primary fill:#edf5ff,stroke:#0f62fe,stroke-width:3px
    classDef secondary fill:#f4f4f4,stroke:#525252,stroke-width:2px
    classDef warning fill:#fff8e1,stroke:#f1c21b,stroke-width:2px
    classDef detail fill:#ffffff,stroke:#c6c6c6,stroke-width:1px
    classDef done fill:#defbe6,stroke:#24a148,stroke-width:2px
```

---

## 5. §3 Landscape Raporu Görselleri

### 5.1. Yıllık Başvuru Trendi (`landscape-filing-trend`)

**Amaç**: Hedef teknoloji alanında yıllık patent başvuru hacmi.

```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .axis-label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .tick { font: 400 10px 'IBM Plex Mono'; fill: #525252; }
    .bar-value { font: 600 10px 'IBM Plex Mono'; fill: #0f62fe; text-anchor: middle; }
  </style>
  
  <rect width="800" height="400" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{TITLE}} — Yıllık Patent Başvuru Trendi</text>
  
  <!-- Y-axis -->
  <line x1="70" y1="60" x2="70" y2="340" stroke="#161616" stroke-width="1.5"/>
  <text class="tick" x="60" y="65" text-anchor="end">{{Y_MAX}}</text>
  <text class="tick" x="60" y="145" text-anchor="end">{{Y_75}}</text>
  <text class="tick" x="60" y="225" text-anchor="end">{{Y_50}}</text>
  <text class="tick" x="60" y="305" text-anchor="end">{{Y_25}}</text>
  <text class="tick" x="60" y="340" text-anchor="end">0</text>
  <text class="axis-label" x="15" y="200" transform="rotate(-90 15 200)">Başvuru sayısı</text>
  
  <!-- X-axis -->
  <line x1="70" y1="340" x2="770" y2="340" stroke="#161616" stroke-width="1.5"/>
  
  <!-- 10 yıl bar — her yıl için 70px genişlik -->
  <!-- Yıl 1 -->
  <rect x="90" y="{{Y1_Y}}" width="50" height="{{Y1_H}}" fill="#0f62fe"/>
  <text class="bar-value" x="115" y="{{Y1_Y_LABEL}}">{{Y1_COUNT}}</text>
  <text class="tick" x="115" y="355" text-anchor="middle">{{Y1_YEAR}}</text>
  <!-- Yıl 2-10 için aynı yapı, x ofset 70px -->
  
  <!-- Trend line overlay (opsiyonel) -->
  <polyline points="{{TREND_POINTS}}" stroke="#da1e28" stroke-width="2" fill="none" stroke-dasharray="4 2"/>
  
  <text class="tick" x="20" y="388" fill="#525252">Kaynak: Espacenet + USPTO + PATENTSCOPE · CAGR: {{CAGR}}</text>
</svg>
```

### 5.2. Assignee Bar Chart (`landscape-assignee-bar`)

**Amaç**: Hedef alanda top 10 assignee (başvuru sahibi) payı.

```svg
<svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .value { font: 600 11px 'IBM Plex Mono'; fill: #ffffff; }
    .tick { font: 400 10px 'IBM Plex Mono'; fill: #525252; }
  </style>
  
  <rect width="800" height="500" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{TITLE}} — Top 10 Assignee</text>
  
  <!-- 10 assignee, her biri 40px yükseklik -->
  <text class="label" x="200" y="72" text-anchor="end">{{A1_NAME}}</text>
  <rect x="210" y="55" width="{{A1_WIDTH}}" height="26" fill="#0f62fe"/>
  <text class="value" x="{{A1_LABEL_X}}" y="72">{{A1_COUNT}}</text>
  
  <text class="label" x="200" y="112" text-anchor="end">{{A2_NAME}}</text>
  <rect x="210" y="95" width="{{A2_WIDTH}}" height="26" fill="#8a3ffc"/>
  <text class="value" x="{{A2_LABEL_X}}" y="112">{{A2_COUNT}}</text>
  
  <text class="label" x="200" y="152" text-anchor="end">{{A3_NAME}}</text>
  <rect x="210" y="135" width="{{A3_WIDTH}}" height="26" fill="#007d79"/>
  <text class="value" x="{{A3_LABEL_X}}" y="152">{{A3_COUNT}}</text>
  
  <!-- ... A4-A10 için benzer yapı, y +40px -->
  
  <!-- X-axis scale -->
  <line x1="210" y1="470" x2="770" y2="470" stroke="#161616"/>
  <text class="tick" x="210" y="485" text-anchor="middle">0</text>
  <text class="tick" x="350" y="485" text-anchor="middle">{{X_25}}</text>
  <text class="tick" x="490" y="485" text-anchor="middle">{{X_50}}</text>
  <text class="tick" x="630" y="485" text-anchor="middle">{{X_75}}</text>
  <text class="tick" x="770" y="485" text-anchor="middle">{{X_MAX}}</text>
</svg>
```

### 5.3. Coğrafi Choropleth Haritası (`landscape-geo-choropleth`)

**Amaç**: Dünya haritası üzerinde ülke bazlı patent başvuru yoğunluğu.

```
{{SIMPLE_BAR_FALLBACK}} — Gerçek choropleth için coordinat-yoğun SVG gerekir.
Pratik alternatif: bar chart ülke bazlı. Çok basit bölgesel harita için 
basit dünya haritası SVG path'lerinden sub-set kullanılabilir.
Önerilen: ülke bar chart (landscape-assignee-bar pattern ile ülke adı).
```

### 5.4. Evergreening Timeline (`landscape-evergreening-timeline`)

**Amaç**: Bir orijinatörün birincil + formülasyon + kullanım + dozaj + cihaz patentlerinin zaman çizelgesi.

```svg
<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 11px 'IBM Plex Sans'; fill: #161616; }
    .year { font: 400 10px 'IBM Plex Mono'; fill: #525252; text-anchor: middle; }
  </style>
  
  <rect width="900" height="300" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{ASSET_NAME}} — Evergreening Patent Zaman Çizelgesi</text>
  
  <!-- Yıl ekseni (15 yıl) -->
  <line x1="180" y1="60" x2="880" y2="60" stroke="#c6c6c6" stroke-width="1.5"/>
  <!-- Her 3 yılda tick -->
  <text class="year" x="180" y="52">{{Y0}}</text>
  <text class="year" x="320" y="52">{{Y3}}</text>
  <text class="year" x="460" y="52">{{Y6}}</text>
  <text class="year" x="600" y="52">{{Y9}}</text>
  <text class="year" x="740" y="52">{{Y12}}</text>
  <text class="year" x="880" y="52">{{Y15}}</text>
  
  <!-- Patent katmanları (her biri 30px yükseklik + gap) -->
  <text class="label" x="170" y="98" text-anchor="end">Temel molekül</text>
  <rect x="{{P1_X}}" y="85" width="{{P1_W}}" height="20" fill="#0f62fe"/>
  <text class="year" x="{{P1_END_X}}" y="100" fill="#0f62fe">{{P1_END}}</text>
  
  <text class="label" x="170" y="128" text-anchor="end">Polimorf</text>
  <rect x="{{P2_X}}" y="115" width="{{P2_W}}" height="20" fill="#8a3ffc"/>
  <text class="year" x="{{P2_END_X}}" y="130" fill="#8a3ffc">{{P2_END}}</text>
  
  <text class="label" x="170" y="158" text-anchor="end">Formülasyon</text>
  <rect x="{{P3_X}}" y="145" width="{{P3_W}}" height="20" fill="#007d79"/>
  <text class="year" x="{{P3_END_X}}" y="160" fill="#007d79">{{P3_END}}</text>
  
  <text class="label" x="170" y="188" text-anchor="end">İkinci tıbbi kullanım</text>
  <rect x="{{P4_X}}" y="175" width="{{P4_W}}" height="20" fill="#ff832b"/>
  <text class="year" x="{{P4_END_X}}" y="190" fill="#ff832b">{{P4_END}}</text>
  
  <text class="label" x="170" y="218" text-anchor="end">Cihaz (combo)</text>
  <rect x="{{P5_X}}" y="205" width="{{P5_W}}" height="20" fill="#fa4d56"/>
  <text class="year" x="{{P5_END_X}}" y="220" fill="#fa4d56">{{P5_END}}</text>
  
  <!-- LOE dikey çizgi (pratik pazara giriş) -->
  <line x1="{{LOE_X}}" y1="75" x2="{{LOE_X}}" y2="240" stroke="#da1e28" stroke-width="2" stroke-dasharray="4 2"/>
  <text class="label" x="{{LOE_X}}" y="260" text-anchor="middle" fill="#da1e28" font-weight="600">LOE: {{LOE_DATE}}</text>
</svg>
```

---

## 6. §4 Lifecycle Yol Haritası Görselleri

### 6.1. Lifecycle Gantt (`lifecycle-gantt`)

**Amaç**: Onay sonrası pazar genişletme stratejisi — yeni endikasyon, yeni formülasyon, kombinasyon.

**Yapı**: §3.4 LOE Gantt'a benzer ama bar'ları stratejik aksiyon olarak yeniden etiketle (new indication Phase III, combination trial, device SC formülasyon, vb.).

### 6.2. Revenue Erosion Curve (`lifecycle-erosion`)

**Amaç**: LOE sonrası fiyat + volume erozyonu projeksyonu.

```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .tick { font: 400 10px 'IBM Plex Mono'; fill: #525252; }
    .line { stroke-width: 2.5; fill: none; }
  </style>
  
  <rect width="800" height="400" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{ASSET_NAME}} — Gelir Erozyonu Tahmini</text>
  
  <!-- Axes -->
  <line x1="70" y1="60" x2="70" y2="340" stroke="#161616"/>
  <line x1="70" y1="340" x2="770" y2="340" stroke="#161616"/>
  
  <!-- Y-axis labels ($) -->
  <text class="tick" x="60" y="65" text-anchor="end">$2B</text>
  <text class="tick" x="60" y="145" text-anchor="end">$1.5B</text>
  <text class="tick" x="60" y="225" text-anchor="end">$1B</text>
  <text class="tick" x="60" y="305" text-anchor="end">$500M</text>
  
  <!-- X-axis (yıllar) -->
  <text class="tick" x="70" y="360" text-anchor="middle">{{Y0}}</text>
  <text class="tick" x="200" y="360" text-anchor="middle">{{Y1}}</text>
  <text class="tick" x="330" y="360" text-anchor="middle">{{Y2}}</text>
  <text class="tick" x="460" y="360" text-anchor="middle">{{Y3}}</text>
  <text class="tick" x="590" y="360" text-anchor="middle">{{Y4}}</text>
  <text class="tick" x="720" y="360" text-anchor="middle">{{Y5}}</text>
  
  <!-- LOE dikey çizgi -->
  <line x1="{{LOE_X}}" y1="60" x2="{{LOE_X}}" y2="340" stroke="#da1e28" stroke-dasharray="4 2"/>
  <text class="label" x="{{LOE_X}}" y="50" text-anchor="middle" fill="#da1e28">LOE</text>
  
  <!-- Baseline (no intervention) -->
  <polyline class="line" stroke="#fa4d56" points="{{BASELINE_POINTS}}"/>
  <text class="label" x="790" y="300" text-anchor="end" fill="#fa4d56">Müdahalesiz</text>
  
  <!-- Lifecycle strategy line -->
  <polyline class="line" stroke="#24a148" points="{{LCM_POINTS}}"/>
  <text class="label" x="790" y="200" text-anchor="end" fill="#24a148">LCM + yeni formülasyon</text>
</svg>
```

### 6.3. Strategic Quadrant (`lifecycle-quadrant`)

**Amaç**: Lifecycle stratejileri × etki-zorluk matrisi. 2x2 quadrant.

```svg
<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; text-anchor: middle; }
    .axis { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .quadrant { font: 500 11px 'IBM Plex Sans'; fill: #525252; text-anchor: middle; }
    .strategy { font: 400 10px 'IBM Plex Sans'; fill: #161616; text-anchor: middle; }
  </style>
  
  <rect width="500" height="500" fill="#f4f4f4"/>
  <text class="title" x="250" y="30">{{TITLE}} — Strateji Matrisi</text>
  
  <!-- Quadrant arka planları -->
  <rect x="70" y="70" width="180" height="180" fill="#defbe6" opacity="0.5"/>
  <rect x="250" y="70" width="180" height="180" fill="#fff1f1" opacity="0.5"/>
  <rect x="70" y="250" width="180" height="180" fill="#f4f4f4" opacity="0.5"/>
  <rect x="250" y="250" width="180" height="180" fill="#fff8e1" opacity="0.5"/>
  
  <!-- Axes -->
  <line x1="70" y1="430" x2="430" y2="430" stroke="#161616" stroke-width="1.5"/>
  <line x1="250" y1="70" x2="250" y2="430" stroke="#161616" stroke-width="1.5"/>
  
  <!-- Axis labels -->
  <text class="axis" x="250" y="465" text-anchor="middle">Zorluk / Maliyet →</text>
  <text class="axis" x="30" y="250" transform="rotate(-90 30 250)" text-anchor="middle">Stratejik etki →</text>
  
  <!-- Quadrant labels -->
  <text class="quadrant" x="160" y="100" font-weight="600">Hızlı kazanımlar</text>
  <text class="quadrant" x="340" y="100" font-weight="600">Büyük bahisler</text>
  <text class="quadrant" x="160" y="290" font-weight="600">Rutin süreç</text>
  <text class="quadrant" x="340" y="290" font-weight="600">Değer az, riskli</text>
  
  <!-- Stratejiler nokta olarak -->
  <circle cx="{{S1_X}}" cy="{{S1_Y}}" r="8" fill="#0f62fe"/>
  <text class="strategy" x="{{S1_X}}" y="{{S1_LY}}">{{S1_NAME}}</text>
  <!-- S2-S6 için aynı -->
</svg>
```

---

## 7. §5 Pazara Giriş Takvimi Görselleri

### 7.1. LOE Gantt (§3.4 şablonunu kullan)

### 7.2. MAX Formülü Görselleştirme (`launch-max-formula`)

**Amaç**: `max(patent expiry, veri imtiyazı bitimi + ruhsat gecikmesi)` formülünün görsel açıklaması.

```svg
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .formula { font: 500 13px 'IBM Plex Mono'; fill: #0f62fe; }
    .value { font: 600 11px 'IBM Plex Mono'; fill: #ffffff; text-anchor: middle; }
    .year { font: 400 10px 'IBM Plex Mono'; fill: #525252; text-anchor: middle; }
  </style>
  
  <rect width="700" height="300" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{ASSET_NAME}} — LOE MAX Formülü</text>
  <text class="formula" x="20" y="54">LOE = MAX(Patent expiry, Veri imtiyazı + ruhsat süresi)</text>
  
  <!-- Option A: Patent -->
  <text class="label" x="170" y="108" text-anchor="end">A) Patent expiry</text>
  <rect x="180" y="92" width="{{A_WIDTH}}" height="22" fill="#0f62fe"/>
  <text class="value" x="{{A_LABEL_X}}" y="108">{{A_DATE}}</text>
  
  <!-- Option B: Data exclusivity + ruhsat -->
  <text class="label" x="170" y="158" text-anchor="end">B) Veri imtiyazı + ruhsat</text>
  <rect x="180" y="142" width="{{B_WIDTH}}" height="22" fill="#007d79"/>
  <text class="value" x="{{B_LABEL_X}}" y="158">{{B_DATE}}</text>
  
  <!-- Max (sonuç) -->
  <text class="label" x="170" y="208" text-anchor="end" font-weight="600">Praktik LOE (MAX)</text>
  <rect x="180" y="192" width="{{MAX_WIDTH}}" height="22" fill="#da1e28"/>
  <text class="value" x="{{MAX_LABEL_X}}" y="208">{{MAX_DATE}}</text>
  
  <!-- Zaman ekseni -->
  <line x1="180" y1="250" x2="680" y2="250" stroke="#161616"/>
  <text class="year" x="180" y="265">{{Y_START}}</text>
  <text class="year" x="430" y="265">{{Y_MID}}</text>
  <text class="year" x="680" y="265">{{Y_END}}</text>
  
  <text class="label" x="20" y="290" fill="#525252">Not: Türkiye için SPC yok — sadece 20 yıl patent + 6 yıl veri imtiyazı kuralı.</text>
</svg>
```

---

## 8. §6 Litigation Briefing Görselleri

### 8.1. Karar Ağacı — Dava Stratejisi (`litigation-decision-tree`)

**Mermaid flowchart**: §3.3 pattern gibi; dallar: ihtiyati tedbir → asıl dava → temyiz → icra.

### 8.2. Dava Maliyet Eğrisi (`litigation-cost-curve`)

```svg
<svg viewBox="0 0 700 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .tick { font: 400 10px 'IBM Plex Mono'; fill: #525252; }
  </style>
  
  <rect width="700" height="350" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{CASE_NAME}} — Dava Aşaması × Kümülatif Maliyet</text>
  
  <!-- Aşamalar: İlk dava dilekçesi → Bilirkişi → Delil → Duruşma → Karar → Temyiz -->
  <line x1="70" y1="280" x2="670" y2="280" stroke="#161616"/>
  
  <!-- Maliyet bar + kümülatif -->
  <rect x="80" y="{{S1_Y}}" width="80" height="{{S1_H}}" fill="#0f62fe"/>
  <text class="tick" x="120" y="295" text-anchor="middle">Dilekçe</text>
  <text class="tick" x="120" y="{{S1_Y_LABEL}}" text-anchor="middle">{{S1_COST}}</text>
  
  <rect x="180" y="{{S2_Y}}" width="80" height="{{S2_H}}" fill="#8a3ffc"/>
  <text class="tick" x="220" y="295" text-anchor="middle">Bilirkişi</text>
  <text class="tick" x="220" y="{{S2_Y_LABEL}}" text-anchor="middle">{{S2_COST}}</text>
  
  <!-- ... S3, S4, S5, S6 için aynı yapı -->
  
  <!-- Cumulative line overlay -->
  <polyline points="{{CUMULATIVE_POINTS}}" stroke="#da1e28" stroke-width="2" fill="none"/>
</svg>
```

### 8.3. Forum Matrisi (`litigation-forum-matrix`)

**Tablo** — forum × kriter (süre, maliyet, kazanma oranı, etki):

```html
<table style="width: 100%; border-collapse: collapse; background: #ffffff; font-family: 'IBM Plex Sans';">
  <thead>
    <tr style="background: #e0e0e0;">
      <th style="padding: 12px; border: 1px solid #c6c6c6;">Forum</th>
      <th style="padding: 12px; border: 1px solid #c6c6c6;">Ortalama süre</th>
      <th style="padding: 12px; border: 1px solid #c6c6c6;">Tahmini maliyet</th>
      <th style="padding: 12px; border: 1px solid #c6c6c6;">Davacı kazanma oranı</th>
      <th style="padding: 12px; border: 1px solid #c6c6c6;">Coğrafi etki</th>
      <th style="padding: 12px; border: 1px solid #c6c6c6;">Öneri</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>FSHHM İstanbul</td><td>18-30 ay</td><td>₺500K-2M</td><td>%35-55</td><td>TR</td><td style="background: {{C1}};">{{R1}}</td></tr>
    <tr><td>FSHHM Ankara</td><td>20-32 ay</td><td>₺500K-2M</td><td>%35-50</td><td>TR</td><td style="background: {{C2}};">{{R2}}</td></tr>
    <tr><td>EPO Opposition</td><td>24-36 ay</td><td>€75-180K</td><td>%60-70 (revoke/amend)</td><td>AB + EP üyeler</td><td style="background: {{C3}};">{{R3}}</td></tr>
    <tr><td>UPC (Unified Patent Court)</td><td>12-18 ay</td><td>€200K-500K</td><td>n/a (yeni)</td><td>AB</td><td style="background: {{C4}};">{{R4}}</td></tr>
  </tbody>
</table>
```

---

## 9. §7 Due Diligence Görselleri

### 9.1. Coverage Heatmap (§3.1 pattern) — Aile × Ülke

### 9.2. DD Radar Chart (`dd-radar`)

```svg
<!-- §4.2 invalidity-radar pattern. 5-6 eksen: Patent kuvveti, Klinik veri, Pazar potansiyeli, Regulatory path, IP portföy çeşitliliği, Bilanço -->
```

### 9.3. Monte Carlo NPV Distribution (`dd-montecarlo`)

```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .tick { font: 400 10px 'IBM Plex Mono'; fill: #525252; }
  </style>
  
  <rect width="800" height="400" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{ASSET}} NPV Dağılımı — 10,000 Monte Carlo Sim.</text>
  
  <!-- Histogram bar'ları — 20 bin -->
  <line x1="70" y1="340" x2="770" y2="340" stroke="#161616"/>
  
  <!-- Bin bar'ları — x-axis NPV değeri -->
  <!-- Her bar 35px genişlik -->
  <rect x="80" y="{{B1_Y}}" width="30" height="{{B1_H}}" fill="#0f62fe" opacity="0.8"/>
  <rect x="115" y="{{B2_Y}}" width="30" height="{{B2_H}}" fill="#0f62fe" opacity="0.8"/>
  <!-- ... B3-B20 -->
  
  <!-- P10, P50, P90 çizgileri -->
  <line x1="{{P10_X}}" y1="60" x2="{{P10_X}}" y2="340" stroke="#fa4d56" stroke-dasharray="3 2"/>
  <text class="label" x="{{P10_X}}" y="55" text-anchor="middle" fill="#fa4d56">P10: {{P10_VALUE}}</text>
  <line x1="{{P50_X}}" y1="60" x2="{{P50_X}}" y2="340" stroke="#24a148" stroke-width="2"/>
  <text class="label" x="{{P50_X}}" y="55" text-anchor="middle" fill="#24a148">P50: {{P50_VALUE}}</text>
  <line x1="{{P90_X}}" y1="60" x2="{{P90_X}}" y2="340" stroke="#fa4d56" stroke-dasharray="3 2"/>
  <text class="label" x="{{P90_X}}" y="55" text-anchor="middle" fill="#fa4d56">P90: {{P90_VALUE}}</text>
  
  <text class="label" x="400" y="380" text-anchor="middle">NPV ($M) →</text>
</svg>
```

### 9.4. Tornado Chart — Sensitivity (`dd-tornado`)

```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .value { font: 600 10px 'IBM Plex Mono'; fill: #161616; }
  </style>
  
  <rect width="800" height="400" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{ASSET}} — Duyarlılık Analizi (Tornado)</text>
  
  <!-- Central axis — baseline NPV -->
  <line x1="400" y1="60" x2="400" y2="360" stroke="#161616" stroke-width="2"/>
  <text class="label" x="400" y="55" text-anchor="middle" font-weight="600">Baseline NPV</text>
  
  <!-- 6 parameters, top to bottom: büyük etkiden küçüğe -->
  <!-- Parameter 1: Peak Sales -->
  <text class="label" x="390" y="98" text-anchor="end">Peak Sales (-50%/+50%)</text>
  <rect x="{{P1_NEG_X}}" y="80" width="{{P1_NEG_W}}" height="30" fill="#fa4d56" opacity="0.7"/>
  <rect x="400" y="80" width="{{P1_POS_W}}" height="30" fill="#24a148" opacity="0.7"/>
  <text class="value" x="{{P1_NEG_CENTER_X}}" y="100">{{P1_NEG_VAL}}</text>
  <text class="value" x="{{P1_POS_CENTER_X}}" y="100">{{P1_POS_VAL}}</text>
  
  <!-- Parameter 2-6 için benzer yapı, y +40px offset -->
  
  <!-- X-axis (NPV değişim) -->
  <line x1="100" y1="360" x2="700" y2="360" stroke="#c6c6c6"/>
  <text class="label" x="100" y="380" text-anchor="middle">-50%</text>
  <text class="label" x="400" y="380" text-anchor="middle">0</text>
  <text class="label" x="700" y="380" text-anchor="middle">+50%</text>
</svg>
```

---

## 10. §8 Opposition Briefing Görselleri

### 10.1. EPC Art. 100 Haritası (`opposition-art100-map`)

```
flowchart TD
    TARGET["{{PATENT}}<br/>Granted {{GRANT_DATE}}"]:::target
    TARGET --> A["Art 100(a)(i)<br/>Yenilik"]:::vector
    TARGET --> B["Art 100(a)(ii)<br/>Buluş basamağı"]:::vector
    TARGET --> C["Art 100(b)<br/>Yeterli açıklama"]:::vector
    TARGET --> D["Art 100(c)<br/>Added matter"]:::vector
    
    A --> A1{"Prior art mozaik<br/>tam kapsama?"}:::decision
    B --> B1{"Problem-solution<br/>aşikâr çözüm?"}:::decision
    C --> C1{"Ortalama uzman<br/>reproduce edebilir?"}:::decision
    D --> D1{"İstemdeki özellik<br/>başvuruda var mı?"}:::decision
    
    A1 -->|Evet| RESULT1["YENİLİK YOKSUNLUĞU<br/>{{CONFIDENCE_1}}"]:::result
    B1 -->|Hayır| RESULT2["BULUŞ BASAMAĞI YOKSUN<br/>{{CONFIDENCE_2}}"]:::result
    C1 -->|Hayır| RESULT3["YETERSİZ AÇIKLAMA<br/>{{CONFIDENCE_3}}"]:::result
    D1 -->|Hayır| RESULT4["ADDED MATTER<br/>{{CONFIDENCE_4}}"]:::result
    
    classDef target fill:#ffd7d9,stroke:#da1e28,stroke-width:3px
    classDef vector fill:#edf5ff,stroke:#0f62fe,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f1c21b,stroke-width:2px
    classDef result fill:#defbe6,stroke:#24a148,stroke-width:2px
```

### 10.2. Problem-Solution Akışı (`opposition-problem-solution`)

```
flowchart LR
    A["En yakın prior art<br/>{{CPA_ID}}"] --> B["Teknik farklılık<br/>{{TECH_DIFF}}"]
    B --> C["Objektif teknik problem<br/>{{OBJ_PROBLEM}}"]
    C --> D{"Ortalama uzman<br/>aşikâr çözüm bulur mu?"}
    D -->|Evet + kombinasyon motivasyon| E["AŞİKAR<br/>(buluş basamağı yok)"]:::fail
    D -->|Hayır veya motivasyon yok| F["AŞIKAR DEĞİL<br/>(patent geçerli)"]:::pass
    
    classDef fail fill:#fff1f1,stroke:#da1e28,stroke-width:2px
    classDef pass fill:#defbe6,stroke:#24a148,stroke-width:2px
```

### 10.3. Opposition Takvim Gantt (`opposition-timeline`)

```svg
<!-- §3.4 LOE Gantt pattern ile benzer — bu sefer aşamalar:
     Notice drafting → Filing deadline → Opposition Division review →
     Patent sahibi cevabı → Opponent reply → Oral Proceedings → Karar → Temyiz -->
```

---

## 11. §9 Biosimilar Pathway Görselleri

### 11.1. Çok-Katmanlı Gantt (`biosimilar-multi-gantt`)

**Amaç**: Biosimilar geliştirme + onay + pazar girişi Gantt'ı 3 paralel swim-lane (Analytical comparability, Clinical comparability, Regulatory filings).

```svg
<svg viewBox="0 0 900 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .lane-title { font: 600 13px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 11px 'IBM Plex Sans'; fill: #161616; }
    .year { font: 400 10px 'IBM Plex Mono'; fill: #525252; text-anchor: middle; }
  </style>
  
  <rect width="900" height="420" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{REFERENCE_PRODUCT}} Biosimilar — Geliştirme Yol Haritası</text>
  
  <!-- Yıl ekseni -->
  <line x1="180" y1="60" x2="880" y2="60" stroke="#c6c6c6"/>
  <text class="year" x="180" y="52">{{Y0}}</text>
  <text class="year" x="320" y="52">{{Y2}}</text>
  <text class="year" x="460" y="52">{{Y4}}</text>
  <text class="year" x="600" y="52">{{Y6}}</text>
  <text class="year" x="740" y="52">{{Y8}}</text>
  <text class="year" x="880" y="52">{{Y10}}</text>
  
  <!-- Lane 1: Analytical -->
  <text class="lane-title" x="20" y="90">Analytical Comparability</text>
  <rect x="180" y="100" width="140" height="24" fill="#0f62fe"/>
  <text class="label" x="250" y="116" fill="#ffffff" text-anchor="middle">CQA profilleme</text>
  <rect x="320" y="100" width="100" height="24" fill="#0f62fe" opacity="0.7"/>
  <text class="label" x="370" y="116" fill="#ffffff" text-anchor="middle">Biobenzerliik</text>
  
  <!-- Lane 2: Clinical -->
  <text class="lane-title" x="20" y="180">Clinical Comparability</text>
  <rect x="350" y="190" width="80" height="24" fill="#8a3ffc"/>
  <text class="label" x="390" y="206" fill="#ffffff" text-anchor="middle">Faz I PK/PD</text>
  <rect x="430" y="190" width="180" height="24" fill="#8a3ffc" opacity="0.7"/>
  <text class="label" x="520" y="206" fill="#ffffff" text-anchor="middle">Faz III confirmatory</text>
  
  <!-- Lane 3: Regulatory -->
  <text class="lane-title" x="20" y="270">Regulatory Filings</text>
  <rect x="610" y="280" width="60" height="24" fill="#007d79"/>
  <text class="label" x="640" y="296" fill="#ffffff" text-anchor="middle">FDA BLA</text>
  <rect x="610" y="310" width="80" height="24" fill="#007d79" opacity="0.9"/>
  <text class="label" x="650" y="326" fill="#ffffff" text-anchor="middle">EMA MAA</text>
  <rect x="670" y="340" width="100" height="24" fill="#007d79" opacity="0.8"/>
  <text class="label" x="720" y="356" fill="#ffffff" text-anchor="middle">TİTCK başvuru</text>
  
  <!-- Milestone: Launch -->
  <circle cx="{{LAUNCH_X}}" cy="385" r="8" fill="#da1e28"/>
  <text class="label" x="{{LAUNCH_X}}" y="405" text-anchor="middle" fill="#da1e28" font-weight="600">Launch {{LAUNCH_YEAR}}</text>
</svg>
```

### 11.2. Comparability Sankey (`biosimilar-sankey`)

**Amaç**: CQA test kategorilerinin (structural, functional, PK) sonuçlara akışı. Kompleks — fallback:

```
{{BASIT_TABLO_FALLBACK}}
CQA kategorisi | Test sayısı | Benzer | Yüksek-benzer | Aynı
Structural     | 25          | 3      | 12            | 10
Functional     | 12          | 1      | 6             | 5
PK profile     | 8           | 0      | 2             | 6
```

### 11.3. Pazar Payı Stacked Area (`biosimilar-market-share`)

```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .tick { font: 400 10px 'IBM Plex Mono'; fill: #525252; }
  </style>
  
  <rect width="800" height="400" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{MOLECULE_NAME}} — Pazar Payı Evolüsyonu</text>
  
  <!-- Stacked area — her biosimilar için farklı renk -->
  <polygon points="{{REF_POLYGON}}" fill="#161616" opacity="0.8"/>
  <polygon points="{{BIO1_POLYGON}}" fill="#0f62fe" opacity="0.85"/>
  <polygon points="{{BIO2_POLYGON}}" fill="#8a3ffc" opacity="0.85"/>
  <polygon points="{{BIO3_POLYGON}}" fill="#007d79" opacity="0.85"/>
  <polygon points="{{BIO4_POLYGON}}" fill="#ff832b" opacity="0.85"/>
  
  <!-- Legend -->
  <g transform="translate(20, 360)">
    <rect x="0" y="0" width="14" height="14" fill="#161616"/><text class="label" x="20" y="12">Referans</text>
    <rect x="120" y="0" width="14" height="14" fill="#0f62fe"/><text class="label" x="140" y="12">{{BIO1_NAME}}</text>
    <rect x="260" y="0" width="14" height="14" fill="#8a3ffc"/><text class="label" x="280" y="12">{{BIO2_NAME}}</text>
    <rect x="400" y="0" width="14" height="14" fill="#007d79"/><text class="label" x="420" y="12">{{BIO3_NAME}}</text>
    <rect x="540" y="0" width="14" height="14" fill="#ff832b"/><text class="label" x="560" y="12">{{BIO4_NAME}}</text>
  </g>
</svg>
```

### 11.4. 3-Jurisdiction Launch Calendar (`biosimilar-launch-calendar`)

```svg
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{TITLE}}">
  <style>
    .title { font: 600 16px 'IBM Plex Sans'; fill: #161616; }
    .label { font: 500 12px 'IBM Plex Sans'; fill: #161616; }
    .year { font: 400 10px 'IBM Plex Mono'; fill: #525252; text-anchor: middle; }
    .milestone { font: 600 10px 'IBM Plex Mono'; fill: #ffffff; text-anchor: middle; }
  </style>
  
  <rect width="800" height="300" fill="#f4f4f4"/>
  <text class="title" x="20" y="28">{{REFERENCE_NAME}} Biosimilar — 3 Jurisdiksiyon Launch Takvimi</text>
  
  <!-- Yıl ekseni -->
  <line x1="100" y1="60" x2="780" y2="60" stroke="#c6c6c6"/>
  <text class="year" x="100" y="52">{{Y0}}</text>
  <text class="year" x="270" y="52">{{Y2}}</text>
  <text class="year" x="440" y="52">{{Y4}}</text>
  <text class="year" x="610" y="52">{{Y6}}</text>
  <text class="year" x="780" y="52">{{Y8}}</text>
  
  <!-- Lane US -->
  <text class="label" x="90" y="108" text-anchor="end">🇺🇸 ABD</text>
  <rect x="{{US_PAT_START}}" y="92" width="{{US_PAT_W}}" height="22" fill="#0f62fe"/>
  <circle cx="{{US_LAUNCH_X}}" cy="103" r="10" fill="#24a148"/>
  <text class="milestone" x="{{US_LAUNCH_X}}" y="107">🚀</text>
  
  <!-- Lane EU -->
  <text class="label" x="90" y="158" text-anchor="end">🇪🇺 AB</text>
  <rect x="{{EU_PAT_START}}" y="142" width="{{EU_PAT_W}}" height="22" fill="#8a3ffc"/>
  <circle cx="{{EU_LAUNCH_X}}" cy="153" r="10" fill="#24a148"/>
  <text class="milestone" x="{{EU_LAUNCH_X}}" y="157">🚀</text>
  
  <!-- Lane TR -->
  <text class="label" x="90" y="208" text-anchor="end">🇹🇷 TR</text>
  <rect x="{{TR_PAT_START}}" y="192" width="{{TR_PAT_W}}" height="22" fill="#007d79"/>
  <circle cx="{{TR_LAUNCH_X}}" cy="203" r="10" fill="#24a148"/>
  <text class="milestone" x="{{TR_LAUNCH_X}}" y="207">🚀</text>
  
  <!-- Legend -->
  <g transform="translate(20, 260)">
    <rect x="0" y="0" width="14" height="14" fill="#0f62fe"/><text class="label" x="20" y="12">Patent koruması</text>
    <circle cx="160" cy="7" r="7" fill="#24a148"/><text class="label" x="175" y="12">Launch</text>
  </g>
</svg>
```

---

## 12. §10 Expert Witness Report Görselleri

### 12.1. İstem Ayrıştırma Matrisi (§3.2 pattern)

Bilirkişi raporunda her bağımsız istem için. Başlık: "İstem {{N}} — Özellik Analizi".

### 12.2. Tecavüz/Hükümsüzlük Sonuç Özeti (`expert-verdict-summary`)

```html
<div style="background: #f4f4f4; padding: 24px; font-family: 'IBM Plex Sans'; border-left: 6px solid {{VERDICT_COLOR}};">
  <h3 style="margin: 0 0 8px 0; color: #161616;">Bilirkişi Raporu — Sonuç Özeti</h3>
  <p style="color: #525252; margin: 0 0 16px 0; font-size: 12px;">Dosya No: {{CASE_NO}} · Patent: {{PATENT_NO}}</p>
  
  <table style="width: 100%; background: #ffffff; border-collapse: collapse;">
    <tr style="background: #e0e0e0;">
      <th style="padding: 12px; border: 1px solid #c6c6c6; text-align: left;">Mahkeme sorusu</th>
      <th style="padding: 12px; border: 1px solid #c6c6c6; text-align: center; width: 120px;">Cevap</th>
      <th style="padding: 12px; border: 1px solid #c6c6c6; text-align: left;">Temel gerekçe</th>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #c6c6c6;">1. Tecavüz var mı?</td>
      <td style="padding: 12px; border: 1px solid #c6c6c6; text-align: center; background: {{Q1_BG}}; color: #ffffff; font-weight: 700;">{{Q1_ANSWER}}</td>
      <td style="padding: 12px; border: 1px solid #c6c6c6;">{{Q1_REASONING}}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #c6c6c6;">2. Yenilik şartı karşılanıyor mu?</td>
      <td style="padding: 12px; border: 1px solid #c6c6c6; text-align: center; background: {{Q2_BG}}; color: #ffffff; font-weight: 700;">{{Q2_ANSWER}}</td>
      <td style="padding: 12px; border: 1px solid #c6c6c6;">{{Q2_REASONING}}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #c6c6c6;">3. Buluş basamağı var mı?</td>
      <td style="padding: 12px; border: 1px solid #c6c6c6; text-align: center; background: {{Q3_BG}}; color: #ffffff; font-weight: 700;">{{Q3_ANSWER}}</td>
      <td style="padding: 12px; border: 1px solid #c6c6c6;">{{Q3_REASONING}}</td>
    </tr>
  </table>
  
  <p style="margin-top: 16px; font-size: 11px; color: #525252;">
    Bilirkişi: {{EXPERT_NAME}} · {{EXPERT_TITLE}} · Tarih: {{DATE}}<br/>
    HMK m.266 bağımsızlık beyanı: {{INDEPENDENCE_STATEMENT}}
  </p>
</div>
```

**Renk kuralları**:
- Cevap EVET (tecavüz var / hükümsüz) → `#da1e28`
- Cevap HAYIR (tecavüz yok / geçerli) → `#24a148`
- Cevap KISMEN → `#f1c21b`

---

## Kütüphane Özeti

| Rapor | Şablon sayısı |
|---|---|
| §1 FTO | 4 (heatmap + feature matrix + design-around tree + LOE Gantt) |
| §2 Invalidity | 4 (mozaik + radar + citation network + forum tree) |
| §3 Landscape | 4 (filing trend + assignee bar + geo + evergreening timeline) |
| §4 Lifecycle | 3 (Gantt + erosion + quadrant) |
| §5 Pazara Giriş | 2 (LOE Gantt reuse + MAX formula) |
| §6 Litigation | 3 (decision tree + cost curve + forum matrix) |
| §7 Due Diligence | 4 (coverage heatmap reuse + radar + Monte Carlo + tornado) |
| §8 Opposition | 3 (Art.100 map + problem-solution + timeline) |
| §9 Biosimilar | 4 (multi-Gantt + sankey + market share + launch calendar) |
| §10 Expert Witness | 2 (feature matrix reuse + verdict summary) |
| **TOPLAM** | **33** (bazıları shared pattern) |

---

## Kullanım Örnekleri

### Örnek 1 — FTO raporunda patent × ülke heatmap

Claude akışı:
1. `visualize:read_me(modules=["chart"])` — CSS değişkenleri + best practices yükle
2. Kütüphaneden §3.1 şablonunu al
3. Placeholder'ları vakaya özgü doldur (patent numaraları, ülke renk kodları, tarih)
4. `visualize:show_widget(title="fto_patent_coverage_hepatitis_c", widget_code=SVG_COMPLETED, loading_messages=["Patent matrisi yükleniyor", "Ülke renkleri atanıyor"])`
5. Kullanıcıya metinle: "İşte FTO tarama sonuçları. 14 patent × 6 ülke matrisinde 3 kritik blocker tespit edildi..."

### Örnek 2 — Invalidity radar chart

Claude akışı:
1. `visualize:read_me(modules=["chart"])`
2. Kütüphaneden §4.2 radar şablonunu al
3. 5 eksen skorunu vakaya göre doldur — öz skor değerleri 0-100 (ör. Yenilik=75, Buluş basamağı=60, vs.)
4. Polygon noktalarını trigonometrik olarak hesapla — yenilik (0°, yukarı), buluş basamağı (72°), vs.
5. `visualize:show_widget(...)` 

---

*Bu kütüphane yaşayan bir dokümandır. Yeni rapor tipleri veya yeni görsel istekleri için şablonlar eklenir. Tüm şablonlar IBM Carbon v11 tasarım sistemine uyumludur; fontlar için IBM Plex ailesi varsayılandır.*
