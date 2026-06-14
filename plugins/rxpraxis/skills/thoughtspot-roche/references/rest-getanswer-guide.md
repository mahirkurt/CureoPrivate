# thoughtspot-roche — REST getAnswer-First Extraction Guide

## 1. Amaç

MCP (Spotter) **ham hücre değeri döndürmez** (`get_session_updates` yalnız NLG özeti + `answer` meta nesnesi verir; SKILL.md §2.4). Niceliksel rapor için gerçek rakamlar ThoughtSpot **REST API v2.0** ile çekilir. Bu dosya, doğrulanmış istek gövdelerini, yanıt zarfını ve `n_countries` türev hesaplarını belgeler.

Kaynak: ThoughtSpot Developer dokümanı (`developers.thoughtspot.com`), 2026-06 doğrulaması. Endpoint'ler: `auth/token/full`, `metadata/search`, `searchdata`.

---

## 2. Üç Adımlı Akış

### Adım 0 — Kimlik

```
POST https://<TS_HOST>/api/rest/2.0/auth/token/full
Content-Type: application/json
{
  "username": "<TS_USER>",
  "secret_key": "<TS_SECRET_KEY>",
  "validity_time_in_sec": 3600
}
→ { "token": "<ACCESS_TOKEN>", ... }
```

- SSO-only tenant'ta trusted authentication etkin olmalı.
- Satır-düzeyi filtre/entitlement gerekiyorsa `auth/token/custom` (filter_rules + objects) kullanılır.
- v1 token'ları da v2 isteklerinde geçerlidir.

### Adım 1 — Veri Kaynağı GUID Çözümü

```
POST https://<TS_HOST>/api/rest/2.0/metadata/search
Authorization: Bearer <ACCESS_TOKEN>
{
  "metadata": [{ "type": "LOGICAL_TABLE", "name_pattern": "Midas Monthly" }],
  "record_size": 10
}
→ yanıttan metadata_id (GUID)
```

GUID UI'dan da alınabilir: Data → ilgili Worksheet/Model → adres çubuğundaki GUID.

### Adım 2 — searchdata (Ham Hücre)

```
POST https://<TS_HOST>/api/rest/2.0/searchdata
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
Accept: application/json
User-Agent: market-intel/2.0
{
  "query_string": "[Swiss Franc] [Molecule List] [ATC2] = 'l1' [Date] = 'last 12 months' sort by [Swiss Franc] descending top 10",
  "logical_table_identifier": "<WORKSHEET_GUID>",
  "data_format": "COMPACT",
  "record_offset": 0,
  "record_size": -1
}
```

| Parametre | Not |
|---|---|
| `data_format` | `COMPACT` (varsayılan) veya `FULL` |
| `record_offset` | Varsayılan 0 |
| `record_size` | Varsayılan 10; tam set için `-1` |
| Satır tavanı | Çağrı başına ≤100.000 satır |
| `User-Agent` | Kod tabanlı çağrıda zorunlu |

**Yanıt zarfı:**
```json
{ "contents": [ {
    "column_names": ["Molecule List", "Total Swiss Franc"],
    "data_rows": [ ["<molecule>", 123456789], ... ]
} ] }
```

---

## 3. ThoughtSpot Sorgu Dili (query_string) Kuralları

- Sütunlar köşeli parantez: `[Swiss Franc]`, `[Molecule List]`, `[Country]`.
- Literal değer tek tırnak: `[ATC2] = 'l1'`. **ATC kodları küçük harf** (`l1`, `d3`, `g2`).
- Sıralama: `sort by [Swiss Franc] descending`.
- Top-N: `top 10`.
- Zaman: `[Date] = 'last 12 months'` (doğrulandı). `MAT`/`YTD`/explicit aralık → `references/query-templates.md`.
- Disambiguasyon UI seçimiyle değil, açık token'larla yapılır.

---

## 4. v1 Fallback (tenant v2 kapalıysa)

```
POST https://<TS_HOST>/callosum/v1/tspublic/v1/searchdata
  ?query_string=[Swiss Franc] [Molecule List]&data_source_guid=<GUID>
  &batchsize=-1&pagenumber=-1&offset=-1&formattype=COMPACT
Header: X-Requested-By: ThoughtSpot
```

v1 yanıtı: `columnNames` + `data` (alt-dizi satırlar) + sampling ratio.

---

## 5. `n_countries` ve Coğrafi Yoğunlaşma Türevleri

Top-N molekül liderboard'u alındıktan sonra, **molekül başına** ülke-düzeyi sorgu çalıştırılır:

```
[Country] [Swiss Franc] [Molecule List] = '<molekül>' [Date] = 'last 12 months'
sort by [Swiss Franc] descending
```

Dönen ülke satırlarından (pozitif satış = varlık) türetilir:

| Türev | Formül / Tanım |
|---|---|
| `n_countries` | `count(country where chf > 0)` — coğrafi ayak izi |
| `top_country` | En yüksek cirolu ülke |
| `top_country_share_pct` | `100 × top_chf / molecule_total` |
| `hhi_country` | `Σ (share_i)²`, share_i = ülke_i / molekül_toplamı; 0 = tam dağınık, 1 = tek ülke |

Çıktı şemaları:
- Özet: `rank,molecule,total_chf,share_of_class_pct,n_countries,top_country,top_country_share_pct,hhi_country`
- Uzun-format: `molecule,country,chf,pct_of_molecule_total`

`share_of_class_pct` paydası, ATC2='l1' **tüm-molekül** toplamından (ayrı bir `searchdata` çağrısı) gelir — top-10 toplamı değil.

Programmatik uygulama: `scripts/ts_getanswer_country_extractor.py` (env-driven, vendor-neutral). Top-N-only varyantı: `scripts/ts_getanswer_extractor.py`.

---

## 6. No-Fabrication Disiplini (G9)

- Tüm rakamlar canlı API yanıtından gelir. API erişilemezse script hata verip durur; **rakam uydurulmaz**.
- MCP `answer` meta verisi yalnız yapı/şema/sıralama doğrulaması içindir; sayı için bu REST yolu zorunludur (G10).
- Eşik kuralı: `n_countries` için "varlık" `> 0` satış olarak tanımlanır; iade/düzeltme kaynaklı negatif/sıfır satırlar sayılmaz.

---

## 7. Çağrı Bütçesi ve Performans

| İş | Çağrı sayısı |
|---|---|
| Top-N + sınıf toplamı | 2 |
| + molekül başına ülke kırılımı (N=10) | +10 |
| **Toplam** | ~12 |

`TS_CALL_DELAY` (script env) ile rate-limit'e karşı yumuşatma yapılabilir. Cross-country agregasyonlar yavaş olabilir → `TIMEOUT` ≥120 sn önerilir.
