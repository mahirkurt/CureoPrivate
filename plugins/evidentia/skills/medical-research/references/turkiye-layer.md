# Türkiye Native Layer (v8.0 — NEW)

**Loaded when:** Any query with Turkey context (Türkiye, TR, SGK, SUT, TİTCK, geri ödeme, ruhsat, eczane, yerli, biyobenzer) — and **by default on every query** (the "Türkiye Dörtlüsü" is mandatory in SKILL.md Adım 1.D).

**Purpose:** Replace the v7.1 Türkiye Dörtlüsü's `Exa site:titck.gov.tr` web-scraping with **native, structured MCP queries.** This is the single largest capability upgrade in v8.0 and directly serves TR pharma / oncology / regulatory / market-access work and the `onko-erisim` / `saglik-sigorta` / `pharmaintel` / `rxos` skill compositions.

**Primary connectors:** TİTCK (`1a49b1bb…`), Türk Mevzuat (`fbf16a1a…`), YÖK Tez (`b2d46b46…`), TÜRKPATENT (`ded65854…`), EuropePMC `AFF:"Turkey"`.

---

## 1. The v8.0 Türkiye Stack (replaces Dörtlüsü web-scraping)

| # | Source | Native tool | Replaces (v7.1) |
|---|---|---|---|
| 1 | **TİTCK** drug master | `search_drugs`, `get_drug`, `get_atc_class_summary`, `find_*` | `Exa site:titck.gov.tr` |
| 2 | **Mevzuat** (SUT, yönetmelik) | `search_mevzuat`, `get_mevzuat_text` | `Exa site:sgk.gov.tr OR resmigazete.gov.tr` |
| 3 | **YÖK Tez** | `search_yok_tez_detailed`, `get_yok_tez_document_markdown` | (retained) |
| 4 | **EuropePMC** Turkish affiliation | `search_articles("(konu) AND AFF:\"Turkey\"")` | (retained) |
| 5 | **TÜRKPATENT** | `search_patents`, `search_trademarks` | `Exa` patent scraping |

Exa Turkish scraping is now a **fallback only** (e.g., TOD/THD congress books, kanser.gov.tr pages without an API).

---

## 2. TİTCK — Structured Drug Queries (verified)

### 2.1 Core lookup chain
```
TİTCK: search_drugs(query="<INN or brand>", limit=20,
        atc_prefix=<optional>, reimbursement_status=<optional>,
        lifecycle_status=<optional "active">, in_market=<optional true>)
   → returns: barcode, product_name, active_ingredients, atc_code+atc_name,
     marketing_authorization_holder, reimbursement_status (GERİ ÖDEMELİ/GERİ ÖDEMESİZ),
     reference_status, lifecycle_status, manufacture_origin (imported/manufactured),
     in_market, prescription_code, authorization_date,
     price{firm_sale/depot/pharmacy/retail_price_try, source_country, source_price_eur, valid_from},
     essential_drugs{adult/child/newborn_list}, snomed_ingredients[{concept_id, fsn}]
TİTCK: get_drug(record_id="<barcode>")   # full master record
```

**Verified example (`search_drugs("trastuzumab")`):** Herceptin (Roche, reference, GERİ ÖDEMELİ, retail 12.668,50 TRY, source İsviçre 335,87 €), Trazimera (Pfizer biosimilar), Herzuma (Celltrion biosimilar), Kadcyla (T-DM1 ADC, L01FD03), Teruvia (Yerlika, manufactured). → instant biosimilar landscape + reimbursement + price, no scraping.

### 2.2 Specialized TİTCK tools
| Tool | Use | Output |
|---|---|---|
| `get_atc_class_summary(atc_prefix="L01FD")` | ATC-class market snapshot | product count, in-market/passive split, price spread (min/avg/median/max TRY), top-5 holders, prescription breakdown, origin split, top-5 SNOMED substances |
| `find_off_label_uses_for_drug(barcode)` | **Oncology off-label** indication list (TİTCK's resmi list) | linked off-label rows by ingredient/SNOMED |
| `find_biosimilar_group(barcode)` | Originator vs biosimilar | same-SNOMED peers oldest-first; `is_likely_originator` flag (heuristic — verify vs EMA/FDA) |
| `find_reference_prices_for_drug(barcode)` | Reference price list (EUR) | linked reference-price rows |
| `compare_drug_to_alternatives(barcode)` | Substitution analysis | alternatives + price delta + origin + holder + reimbursement |
| `find_equivalent_products_by_substance(barcode)` | Same-substance equivalents | active-ingredient equivalents (not therapeutic equivalence) |
| `search_regulation_article23` | Madde-23 application history | regulatory exemption/supply records |
| `find_authorization_cancellations_for_drug(barcode)` | Ruhsat iptali | cancellation rows |
| `get_price_history(...)` / `get_withdrawal_trend(...)` | Time series | price/withdrawal trends |
| `search_off_label_uses(...)` | Browse oncology off-label list | direct off-label query |

### 2.3 Data caveats (from probe)
- **ATC duality:** master `atc_code` is current (e.g., `L01FD01`); `detailed_price_list` sub-field may carry legacy ATC (`L01XC03`). **Master record is authoritative.**
- `find_drug_drug_interactions` = **deprecated alias** for substance-overlap (NOT clinical DDI). Use `find_shared_substance_peers`; never present as interaction data.
- `find_biosimilar_group` originator flag is a **heuristic** (earliest authorization_date) — verify against EMA/FDA for clinical-grade claims.
- `search_active_ingredients` = the **registration pipeline** (in-process licensing), NOT approved-on-market list. Distinct from `search_drugs`.

---

## 3. Mevzuat — Native Legislation (SUT, yönetmelik, kararname)

```
Mevzuat: search_mevzuat(query="Sağlık Uygulama Tebliği <konu>", tur=<type code>, page_size=10)
   # ⚠️ aranacak_yer="baslik" REQUIRES a tur code (anti-scraping); else auto-downgrades to "tumu"
Mevzuat: get_mevzuat_text(...) / get_mevzuat_content(...)   # full text / HTML-parsed article
Mevzuat: get_mevzuat_madde_tree(...) / get_mevzuat_madde_diff(...)  # article tree / change history
Mevzuat: get_anayasa(...)   # Constitution articles (e.g., Md. 17/56 for onko-erisim)
```

Use for: SUT (Sağlık Uygulama Tebliği) coverage rules, Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği, fiyat kararnameleri (Resmî Gazete), Madde-22/23 framework. Replaces `Exa site:sgk.gov.tr/resmigazete.gov.tr` scraping with authoritative full-text.

---

## 4. TÜRKPATENT — Turkey IP (jenerik/biyobenzer)

```
TÜRKPATENT: search_patents(title="<molecule/formulation>", applicant="<holder>", ipc_class="A61K", cpc_class=...)
TÜRKPATENT: get_patent_details(...) ; search_trademarks(...) ; search_designs(...)
```
Feeds `pharmapatent` / `rxos` skills for generic feasibility, biosimilar entry, formulation patents, brand/design protection in TR. Complements (does not replace) Google Patents / Espacenet for global FTO.

---

## 5. Türkiye Output Block (for §5 / §13.f / turkey_access_summary sidecar)

Populate the sidecar `turkey_access_summary` from native sources:
```json
"turkey_access_summary": {
  "titck_status": "<from TİTCK lifecycle_status>",
  "titck_products": [{"brand":"...","holder":"...","barcode":"...","atc":"...","authorization_date":"..."}],
  "reimbursement": "<reimbursement_status>",
  "reference_status": "<reference_status>",
  "price_try": {"retail":0,"pharmacy":0,"depot":0,"firm":0,"source_country":"...","source_price_eur":0,"valid_from":"..."},
  "biosimilar_landscape": [{"brand":"...","holder":"...","is_likely_originator":false}],
  "off_label_oncology": ["<TİTCK off-label rows>"],
  "sut_rule": "<Mevzuat SUT reference>",
  "essential_drug_list": {"adult":1,"child":0,"newborn":0},
  "import_pathway": "<Madde-23 / şahsi kullanım if applicable>"
}
```

---

## 6. Composition

- **onko-erisim** — TİTCK reimbursement + off-label + Mevzuat SUT + `get_anayasa` (Md.17/56) → SGK ödeme reddi petition / ihtiyati tedbir (HMK 389).
- **saglik-sigorta** — TİTCK price + reference status + reimbursement → özel sağlık sigortası tıbbi gereklilik / fark ücreti analysis.
- **rxos / pharmaintel** — `get_atc_class_summary` + `compare_drug_to_alternatives` + `find_biosimilar_group` + TÜRKPATENT → jenerik/biyobenzer fizibilite, fiyat tavanı, eşdeğer grup.
- **pharmapatent** — TÜRKPATENT + Mevzuat (SMK 6769) → TR patent landscape, FTO, biyobenzer entry.

---

## 7. Mandatory Türkiye Dörtlüsü (every query — SKILL.md Adım 1.D, v8.0)
1. **TİTCK `search_drugs`** (native) — INN + brand.
2. **Mevzuat `search_mevzuat`** (native) — SUT/yönetmelik when clinical/reimbursement context.
3. **YÖK Tez `search_yok_tez_detailed`** — Türkçe + İngilizce.
4. **EuropePMC `AFF:"Turkey"`** — Turkish-authored studies.
Null-reporting: if all return empty, emit a **Türkiye Veri Boşluğu** block (do not silently omit).

---

*v8.0 — TİTCK shape verified via `search_drugs("trastuzumab")`; tool inventory verified via schema load, 9 June 2026.*
