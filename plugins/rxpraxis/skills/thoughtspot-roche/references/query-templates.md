# thoughtspot-roche — Validated Query Templates

## 1. Amaç

Sage NLU katmanının üzerinde stabil tetiklendiği prompt kalıplarının kataloğu. Üretim ortamında doğrulanmış pattern'ler "✅ validated", henüz test edilmemişler "🟡 unvalidated", başarısız olanlar "❌ anti-pattern" olarak işaretlenir.

---

## 2. Validated Patterns

### 2.1 Single-Attribute Breakdown ✅

```
What is the breakdown of [METRIC] by [ATTRIBUTE]?
```

**Çalışma örnekleri:**
- *"What is the breakdown of Swiss Franc sales by ATC1 Description (category)?"* (MIDAS Monthly · 2026-05-02)
- *"What are the top 15 diseases by Swiss Franc sales?"* (MIDAS Disease Monthly · 2026-05-02)

**Notlar:**
- `[ATTRIBUTE]` parantez içi açıklama (e.g., "(category)") tanınıyor; gerekli değil ama zarar vermiyor
- `[METRIC]` doğrudan cube column ismi olmalı; "sales" generic terim çoğunlukla "Swiss Franc" veya "Standard Units"'a otomatik map oluyor

### 2.2 Top-N Ranking ✅

```
What are the top [N] [ENTITY_TYPE] by [METRIC]?
```

**Çalışma örnekleri:**
- *"What are the top 15 diseases by Swiss Franc sales?"* — MIDAS Disease Monthly
- *"What are the top 10 manufacturers by Swiss Franc sales?"* (beklenen davranış — 2026-05-02 itibarıyla validated değil)

**Notlar:**
- `[N]` integer; 5–50 aralığında stabil
- `[ENTITY_TYPE]` cube'un karakteristik attribute'larından biri olmalı (diseases, manufacturers, products, molecules, countries, ATC classes)

### 2.3 Monthly Trend 🟡

```
Show monthly trend of [METRIC] for [ATTRIBUTE_VALUE] over the last [N] months
```

**Beklenen davranış:**
- Time-series döner; her ay bir satır
- "last N months" zaman pencere ifadesi muhtemelen tanınır ama davranış henüz haritalanmadı

**Test öncesi öneri:**
- İlk denemede explicit tarih aralığı kullan: *"between 2024-01 and 2025-12"*
- Yanıt geldiğinde davranışı bu dosyaya kaydet, status'u 🟡 → ✅ yap

### 2.4 Pairwise Comparison 🟡

```
Compare [METRIC] for [ENTITY_A] versus [ENTITY_B] in [TIME_WINDOW]
```

**Beklenen davranış:**
- İki sütunlu karşılaştırma tablosu veya yan-yana time series

**Test öncesi öneri:**
- Sage'in compare semantiğini desteklediği belgelenmemiş; ilk testte iki ayrı top-N sorgusu çalıştırıp manuel karşılaştırma daha güvenli

---

## 3. Anti-Patterns (Tetiklemeyen Sorgular)

### 3.1 Soyut Keşif Sorguları ❌

```
"Bu veri kaynağında hangi temel analizleri yapabilirim?"
"What kind of insights can I get from this data?"
"Tell me about this dataset"
```

**Neden başarısız:** Soyut, intent yok. Sage NLG ne tür bir analitik query bekleneceğini anlayamaz.

**Düzeltme:** Generic analytic kalıbı kullan: *"top performers by metric, trend over time, breakdown by category"*

### 3.2 Anahtar-Kelime Tarzı, Fiilsiz Prompt'lar ❌

```
"disease level breakdown, top diseases by volume"
"top manufacturers, monthly trend"
```

**Neden başarısız:** Sage NLU WH-soru fiili veya imperative fiil bekliyor. Bu kalıp Sage NLG için bile zayıf trigger.

**Düzeltme:** Tam cümle kur: *"What are the top diseases by volume?"*

### 3.3 Türkçe Sorgu (EMEA Tenant) ❌ / 🟡

```
"İlk 10 hastalığı CHF satışına göre listele"
"Manufacturer kırılımı göster"
```

**Neden riskli:** EMEA tenant metadata İngilizce eğitilmiş; Türkçe sorgu davranışı doğrulanmadı (2026-05-02 itibarıyla).

**Düzeltme:** Tüm sorgular İngilizce yazılır. Türkçe → İngilizce çeviri skill içinde otomatik uygulanır; kullanıcıya çıktı Türkçe sunulur.

---

## 4. Time Window Expressions — Henüz Haritalanmadı

Aşağıdaki ifadeler MIDAS standart zaman terimleridir ve **muhtemelen** ThoughtSpot Sage tarafından tanınır, ama davranış doğrulanmadı:

| Term | Anlam | Davranış |
|---|---|---|
| `MAT` | Moving Annual Total (son 12 ayın toplamı, yuvarlanan) | 🟡 Test edilecek |
| `YTD` | Year-To-Date | 🟡 Test edilecek |
| `last 12 months` | Son 12 takvim ayı | ✅ Doğrulandı (2026-06; molekül + ATC2 sorgularında çalışır) |
| `Q4 2025` | Spesifik takvim çeyreği | 🟡 Test edilecek |
| `2024` (yıl olarak tek) | Tüm 2024 takvim yılı | 🟡 Test edilecek |
| `between 2024-01 and 2025-12` | Explicit tarih aralığı | 🟡 İlk önerilen test formu |

**Test sıralaması önerisi:**
1. Önce explicit aralık (`between X and Y`) — en güvenli
2. Sonra `last N months` — Sage'lerde standart
3. En son `MAT` / `YTD` — pharma-spesifik, riskli

---

## 5. Filter / Where-Clause Behavior — Kısmen Doğrulandı

**✅ Doğrulanmış (2026-06):** Tek-attribute kategorik filtre — ATC2 koduyla — çalışır:

```
[Swiss Franc] [Molecule List] [ATC2] = 'l1' [Date] = 'last 12 months' sort by [Swiss Franc] descending top 10
```

> **ATC kod kuralı (kritik):** ATC kodları **küçük harf** literal'dir. Antineoplastik ajanlar `'l1'` (değil `'L01'`); dermatolojik `'d3'`; genitoüriner `'g2'` vb. Büyük harf veya `L01` formatı eşleşmeyebilir.

**🟡 Henüz denenmemiş:** Çoklu filter, coğrafi filtre (`in Türkiye`), indikasyon filtresi.

ThoughtSpot Sage'in WHERE-clause semantiği MCP üzerinden henüz tam haritalanmadı. İlk denemede tek attribute filter; sonra çoklu denenir.

---

## 6. Multi-Cube Queries — Desteklenmiyor

`getAnswer` tek seferde tek `datasourceId` parametresi alır. İki küpten join sorgu **tek call'da** mümkün değil. Pratik çözüm:

1. Sıralı `getAnswer` çağrıları (her biri tek cube)
2. Manuel/programmatik triangulation (skill output synthesis adımında)
3. G7 gate triangulation tutarlılığını doğrular

---

## 7. Yeni Pattern Eklenmesi

Yeni bir prompt kalıbı production'da test edildiğinde:

1. Bu dosyaya pattern + örnek + status eklenir
2. Status: 🟡 unvalidated → ✅ validated → ❌ anti-pattern
3. Validation tarihi ve hangi cube'da çalıştığı not edilir
4. Eğer bir pattern bir cube'da çalışıp başkasında çalışmıyorsa, "✅ MIDAS Monthly · 🟡 MIDAS Disease Monthly" gibi cube-spesifik annotation kullanılır
