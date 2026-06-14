# thoughtspot-roche — CSV Normalization Guide

## 1. Amaç

ThoughtSpot `getAnswer` araçlarının döndürdüğü CSV payload'ının kullanıcıya sunulmadan önce uygulanması zorunlu olan normalization adımlarının teknik referansıdır. SKILL.md §4.6 (Step 6) ile birlikte okunmalıdır.

---

## 2. Standart `getAnswer` Çıktı Yapısı

Her `getAnswer` yanıtının `data` alanı şu yapıdadır:

```
"Data extract produced by Mahir Kurt (kurtm1) on MM/DD/YYYY HH:MM UTC"
"You are downloading Roche confidential material"
""
"<column_1_name>","<column_2_name>",...
"<row_1_col_1>","<row_1_col_2>",...
"<row_2_col_1>","<row_2_col_2>",...
...
```

İlk **üç satır** her zaman aynı yapıdadır:

| Satır | İçerik | İşlem |
|---|---|---|
| 1 | Extract notu (kullanıcı + timestamp) | `parsing` → atla; `provenance metadata` → sakla |
| 2 | Confidential etiket | `parsing` → atla; `user output` → yansıt (G6) |
| 3 | Boş satır | Atla |
| 4 | Gerçek header satırı | İlk veri başlığı olarak kullan |
| 5+ | Veri satırları | İşle |

---

## 3. Bilimsel Notasyon → Türkçe Sayı Format Dönüşümü

ThoughtSpot büyük sayıları Python `repr` benzeri scientific notation ile döndürür:

```
2.8204218045255586E12
```

### 3.1 Mertebe Sınıflandırması

| Üs aralığı | Türkçe terim | Format örneği |
|---|---|---|
| `E0` – `E2` (1–999) | Birim | `847` |
| `E3` – `E5` (1.000–999.999) | Bin | `847.000` |
| `E6` – `E8` (1.000.000–999.999.999) | Milyon | `847 milyon` veya `847.000.000` |
| `E9` – `E11` (1×10⁹–9.99×10¹¹) | Milyar | `847 milyar` veya `847.5 milyar` |
| `E12` – `E14` (1×10¹²–9.99×10¹⁴) | Trilyon | `2.82 trilyon` |
| `E15+` | Katrilyon | (Beklenmiyor; pharma sales scale dışı) |

### 3.2 Türkçe Sayı Format Kuralları

- **Binlik ayraç:** Nokta (`.`)
- **Ondalık ayraç:** Virgül (`,`)
- **Milyar/trilyon ifadesi:** İki ondalık basamak yeterli; üçüncü basamak isteğe bağlı

**Örnekler:**

| Bilimsel | Tam basamak | Okunaklı format |
|---|---|---|
| `2.8204218045255586E12` | `2.820.421.804.525,56` | `2,82 trilyon CHF` |
| `1.5432691542370734E11` | `154.326.915.423,71` | `154 milyar CHF` |
| `9.190270016700407E10` | `91.902.700.167,00` | `91,9 milyar CHF` |
| `1.942506110973979E10` | `19.425.061.109,74` | `19,4 milyar CHF` |

### 3.3 Programmatik Conversion

`scripts/normalize_csv.py` aşağıdaki Python helper'ını sağlar:

```python
def format_chf(value_str: str, precision: int = 2) -> str:
    """
    Convert ThoughtSpot scientific notation CHF figure to Turkish-formatted string.

    >>> format_chf("2.8204218045255586E12")
    '2,82 trilyon CHF'
    >>> format_chf("1.5432691542370734E11")
    '154 milyar CHF'
    """
    val = float(value_str)
    if val >= 1e12:
        return f"{val/1e12:.{precision}f} trilyon CHF".replace(".", ",")
    elif val >= 1e9:
        return f"{val/1e9:.{precision}f} milyar CHF".replace(".", ",")
    elif val >= 1e6:
        return f"{val/1e6:.{precision}f} milyon CHF".replace(".", ",")
    else:
        return f"{val:,.0f} CHF".replace(",", ".")
```

---

## 4. Top-N Tablolarına Yüzde Pay Sütunu

Top-N sonuçlarına analitik bağlam için `Pay (%)` sütunu eklenir. İki tip vardır:

### 4.1 Top-N Toplamına Göre (Default)

```
Pay (%) = (row_value / sum_of_top_N_values) × 100
```

Bu cube'un tam toplamını yansıtmaz; sadece dönen N satır içindeki dağılımı gösterir. **Tablo başlığında "Top-N içi pay" notu zorunlu**, yanıltıcı yorum riskini azaltmak için.

### 4.2 Cube Toplamına Göre (Eğer Tam Toplam İstenmişse)

```
Pay (%) = (row_value / cube_grand_total) × 100
```

Bu yalnızca grand-total ayrı bir sorguda elde edilmişse uygulanır. Aksi durumda 4.1 kullanılır.

---

## 5. `Unclassified` / `Various` / `Other` Bucket Handling

Bazı küplerde (özellikle MIDAS Disease Monthly) anlamlı paylar tutar:

| Bucket | Tipik Anlam |
|---|---|
| `Unclassified` | Indikasyon-mapping yapılmamış SKU'lar veya çoklu-indikasyon ürünlerin atanmamış payı |
| `Various` | Heterojen küçük kategorilerin toplamı (genellikle ATC kayıt katmanında) |
| `Other` | Top-N dışına düşen tail birikimi |

**Output disiplini:**
- Bu bucket'lar tabloda yer alır ama görsel olarak işaretlenir (örn. italik veya †-dipnot)
- Yorum bloğunda açıkça not edilir: *"`Unclassified` kategorisi top-15'in %17,4'ünü tutuyor; bu MIDAS Disease küpünde indikasyon-mapping kapsamı dışında kalan ürünlerin payını yansıtır ve veri taksonomisi hassasiyeti için bilinmesi gereken bir olgudur."*

---

## 6. Currency Mertebesi Sanity Check (G8)

Roche'un yıllık global cirosu ~65 milyar CHF'dir. Bir tek küp sorgusunda gelen toplam mertebenin yorumu:

| Toplam mertebesi | Plauzibl yorum |
|---|---|
| < 100 milyar CHF | Tek yıl + tek manufacturer veya alt-segment |
| 100 milyar – 1 trilyon CHF | Çok yıl tek manufacturer veya tek yıl çok manufacturer |
| 1 – 20 trilyon CHF | Çok yıl + çok manufacturer (tüm-pazar audited sales kümülasyonu) |
| > 20 trilyon CHF | Olağandışı; veri çıkarma hatası şüphesi |

**Output disiplini:**
- Mertebe yorumu yanıt blogu içinde mutlaka belirtilir
- Eğer mertebe `> 20 trilyon` veya `< 1 milyar` (tek-cube grand total için) ise, kullanıcıya doğrulama sorusu sorulur

---

## 7. Provenance Block

Her yanıtın sonunda aşağıdaki provenance footer yer alır:

```markdown
---

**Provenance**

- **Datasource:** [Cube Name] (`[GUID]`)
- **Extract:** Mahir Kurt (kurtm1) · YYYY-MM-DD HH:MM UTC
- **Session:** `[analytical_session_id]` · answer `[answer_id]`
- **Frame URL:** [authenticated-only]
- **Classification:** Roche confidential — internal use only
```

Bu blok hem audit-trail hem downstream `create_dashboard` workflow'u için zorunludur.
