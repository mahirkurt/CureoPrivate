# Kanonik Artefakt Önbellek Sözleşmesi (canonical-cache-contract.md)

**Sürüm:** 1.0.0 · **Kapsam:** tefas-analist süiti orkestrasyonu.

Amaç: pahalı connector/hesap sonuçlarının bir run içinde **bir kez** üretilip sonraki
aşamalarca **okunması**; çift sorgu/çift-hesabın engellenmesi (CONNECTORS.md §3).

---

## 1. Kanonik Artefakt Kümesi

| Artefakt | Sahip skill | Üretildiği aşama | Tüketen aşamalar | Connector/hesap maliyeti |
|---|---|---|---|---|
| `fund_registry` | fon-haritalama | 1 | 1,2,3,5,6 | fon-mcp resolve+registry + Borsa get_fund_data |
| `holdings` | fon-haritalama | 1 | 3,5 | fon-mcp get_fund_holdings/allocation |
| `nav_series` | fon-haritalama | 1 | 4,5,6 | Borsa get_fund_data (NAV) |
| `market_context` | piyasa-makro | 2 | 4,6 | Borsa index/bond/fx/evds |
| `peer_metrics` | quant-analiz | 3 | 5,6 | kategori akran kuant (toplu) |
| `quant_metrics` | quant-analiz | 4 | 5,6 | kuant betikleri (fon başına) |
| `optimized_portfolio` | portfoy-insa | 5 | 6 | portfolio_opt betiği |

---

## 2. İçerik-Adresli Anahtar Şeması

```
<artifact_type>:<scope_hash>
scope_hash = SHA-256(normalize(scope))[:12]
```

| Artefakt | scope bileşenleri |
|---|---|
| `fund_registry` | `fund_id` |
| `holdings` | `fund_id + "|" + as_of_date` |
| `nav_series` | `fund_id + "|" + window_start + "|" + window_end` |
| `market_context` | `benchmark + "|" + window` |
| `peer_metrics` | `category + "|" + window` |
| `quant_metrics` | `fund_id + "|" + window + "|" + risk_free_id` |
| `optimized_portfolio` | `sorted(fund_ids) + "|" + risk_profile + "|" + constraints_hash` |

Aynı run + aynı `scope_hash` için ikinci çağrı yapılmaz; önbellekteki artefakt döner.
Cross-run paylaşım yapılmaz (provenance bütünlüğü; her run kendi as-of'unu taşır).

---

## 3. Yaşam Döngüsü

1. Aşama N artefaktı üretmeden önce `cached_artifacts[]`'a `scope_hash` ile bakar.
2. Yoksa connector/betik çağrılır, sonuç `cached_artifacts[]`'a yazılır + `provenance`
   damgası eklenir.
3. Sonraki aşamalar yalnız okur. `connector_call_ledger` her connector için çağrı
   sayısını ve `single_shot_enforced` bayrağını tutar.

---

## 4. Determinizm

Kuant betikleri (quant-analiz scripts/) saf-deterministiktir: aynı girdi → aynı çıktı.
`monte_carlo.py` sabit `seed` ile çalışır (seed `quant_metrics` artefaktına yazılır).
`run_manifest.connector_call_ledger.quant_engine.deterministic = true` ile denetlenir.
