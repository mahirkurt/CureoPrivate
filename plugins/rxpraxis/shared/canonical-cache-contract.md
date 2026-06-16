# rxpraxis — Kanonik Artefakt Önbellek Sözleşmesi

**Belge sınıfı:** Normatif orkestrasyon sözleşmesi — plugin-düzeyi
**Sürüm:** 1.1.0 *(v1.1 — §8 sub-agent izolasyonu + §9 extract-then-evict bağlam disiplini)*
**Birlikte normatif:** `../CONNECTORS.md` §3 (tek-sefer TİTCK) + §5 (MIDAS annualizasyon) + §9 (devre-kesici) · `./scan-ledger-schema.json`

> **Sözleşmenin amacı.** rxos'un §0.B.3 "tek-sefer TİTCK kuralı" tek bir connector için
> tanımlanmıştı. Bu sözleşme, deseni **üç pahalı kanonik artefakta** genelleştirir ve
> süitin verimliliğinin çekirdeğini oluşturur: aynı veri, boru hattı boyunca **bir kez**
> çıkarılır, içerik-adresli bir anahtarla önbelleğe alınır ve sonraki tüm aşamalar bu
> artefaktı **okur** — yeniden sorgulamaz. Bu, hiçbir tekil skill'in tek başına
> sağlayamayacağı bir kazanımdır; çünkü tekil skill'ler birbirlerinin çağrılarından
> habersizdir.

---

## 1. Kanonik Artefakt Kümesi

| Artefakt | Sahip skill / modül | Üretildiği aşama | Tüketen aşamalar | Connector maliyeti |
|---|---|---|---|---|
| **`titck_canonical`** | pharmapatent Mod 13 | Aşama 2 | 2, 4, 5 | TİTCK MCP ~6-9 çağrı |
| **`midas_extract`** | thoughtspot-roche | Aşama 5b | 5a, 5c | ThoughtSpot oturum + REST `searchdata` ~6 dalga |
| **`adis_pipeline`** | medical-research (0.5.I) | Aşama 1 | 1, 2, 4 | AdisInsight `search_drugs`/`get_drug` |

Her artefakt `run_manifest.json` `cached_artifacts[]` dizinine kaydedilir ve içerik-adresli
bir anahtarla işaretlenir.

---

## 2. İçerik-Adresli Anahtar Şeması

```
<artifact_type>:<scope_hash>
```

- `artifact_type` ∈ {`titck_canonical`, `midas_extract`, `adis_pipeline`}
- `scope_hash` = SHA-256(normalize edilmiş sorgu kapsamı)[:12]
  - **titck_canonical:** `sha256(inn + "|" + atc_code + "|" + holder_norm)`
  - **midas_extract:** `sha256(product + "|" + cube + "|" + window_start + "|" + window_end)`
  - **adis_pipeline:** `sha256(inn + "|" + indication_snomed)`

Aynı `scope_hash` için ikinci bir çağrı **yapılmaz**; önbellekteki artefakt döndürülür.
Farklı kapsam (örn. farklı pencere) farklı hash → yeni çıkarım (meşru).

---

## 3. TİTCK Kanonik Dosya Sözleşmesi (`titck_canonical`)

### 3.1 Çıkarım protokolü (Aşama 2, pharmapatent Mod 13 — BİR KEZ)

```yaml
titck_canonical:
  master_record:        # search_drugs (FTS5 smart) + get_drug
    barcode: ...
    inn: ...
    atc_code: ...
    form: ...
    strength: ...
  snomed_profile:       # get_drug_snomed_profile
    substance_concept: ...
    icd10_maps: [...]
  holder_portfolio:     # get_holder_portfolio (alias normalize)
    canonical_holder: ...
    aliases: [...]
    portfolio_size: ...
  atc_landscape:        # get_atc_class_summary + find_first_in_class
    class_size: ...
    first_in_class: {inn: ..., authorization_date: ...}
  price_chain:          # get_price_history (opsiyonel, Mod 13 derin mod)
    fsf: ...
    depot: ...
    pharmacy: ...
    public: ...
  equivalent_group:     # find_equivalent_products_by_substance (pharmaintel M4 paylaşır)
    members: [...]
    saturation_score: ...
  provenance: "[TİTCK MCP / <tool> / <ISO>]"
  scope_hash: "titck_canonical:<hash>"
```

### 3.2 Paylaşım kuralı

- **Aşama 2 (pharmaintel Channel A + M4/M6):** `equivalent_group` + `withdrawal_trend`
  alanlarını bu artefakta **yazar**, ayrı TİTCK çağrısı yapmaz.
- **Aşama 4 (pharmapatent Mod 13→1→5→9):** `titck_canonical` referansını **okur**;
  yalnız Türk Patent MCP katmanını (patent + marka + tasarım) ayrıca çalıştırır.
- **medical-research Türkiye Dörtlüsü:** Aşama 1'de `TİTCK search_drugs` çağrısı zaten
  yapılmışsa, sonucu `titck_canonical.master_record`'a besler; çift `search_drugs` yasak.

### 3.3 Fallback degradasyonu

TİTCK MCP timeout → `CONNECTORS.md §6` fallback zinciri; artefakta caveat:
`"caveat": "TİTCK MCP timeout; cached registry/manual fetch", "status": "degraded"`.
G2.7 WARN gate'i bu durumda `TR_MCP_FALLBACK` ile geçer.

---

## 4. MIDAS Extract Sözleşmesi (`midas_extract`)

### 4.1 Annualizasyon (zorunlu — CONNECTORS.md §5)

Ham kümülatif-CHF **asla** penetrasyon hesabına sokulmaz. Her `by_country` değeri
`annualized_chf` taşır:

```
annualized_chf = raw_chf × (12 / time_span_months)
```

### 4.2 Artefakt şeması

```yaml
midas_extract:
  time_basis:           # sabit explicit pencere — tüm dalgalar paylaşır
    window_start: "2024-01"
    window_end: "2025-12"
    span_months: 24
  annualization: "raw_chf × (12/24)"
  tr_baseline:          # W1 — ATC1 üst-kırılım
    value_chf_annualized: ...
  by_country:           # W2 — 36 ülke (raw + annualized)
    - country: "..."
      raw_chf: ...
      annualized_chf: ...
      standard_units: ...
      status: "ok|data-redacted"
  per_capita: [...]     # W3 — istemci-tarafı (÷ nüfus, ÷ sağlık harcaması)
  structural_peer:      # W4 — ES/IT/GR/PT/PL/MX/BR medyanı
    peer_median: ...
    tr_gap_pct: ...
  erosion_curve: {...}  # W5 — LOE ±12ay, orijinatör/jenerik
  price_corridor: {...} # W6 — istemci-tarafı chf/su
  tr_rank:
    absolute: "N/36"
    per_capita: "N/36"
  provenance:           # her MIDAS alanında zorunlu
    datasource_guid: ...
    session_identifier: ...
    generation_number: ...
    frame_url: ...
    extract_timestamp_utc: ...
  roche_confidential: true
  scope_hash: "midas_extract:<hash>"
```

### 4.3 Ham-hücre asimetrisi (CONNECTORS.md §4)

`get_session_updates` ham hücre döndürmez. `by_country` rakamları **Path B** (REST
`searchdata` / midas-mcp) veya native export ile alınır. **G9 no-fabrication** her
hücreye uygulanır.

### 4.4 Paylaşım kuralı

- **Aşama 5a (pharmaintel M1 scorecard):** pazar boyutu girdisi olarak `tr_baseline`
  + `by_country` **annualized** değerlerini okur; ham CHF kullanmaz.
- **Aşama 5c (pharmaintel M2 fiyat tavanı):** `price_corridor` (istemci-tarafı `chf/su`)
  okur.
- **Aşama 5 revenue model:** penetrasyon sensitivity = year-5 peak / **annualize edilmiş**
  TR pazar tabanı (asla ham kümülatif).

### 4.5 Pre-flight degradasyonu

ThoughtSpot `check_connectivity` `Pong` vermezse → Bölüm B atlanır; Aşama 5 TR-iç katman +
caveat ile **degrade** çalışır. G5.12-G5.16 WARN gate'leri sığ-mod fallback'e izin verir.

---

## 5. AdisInsight Pipeline Sözleşmesi (`adis_pipeline`)

### 5.1 Çıkarım protokolü (Aşama 1, medical-research 0.5.I — BİR KEZ)

```yaml
adis_pipeline:
  drug_record:          # search_drugs + get_drug (HyDE)
    inn: ...
    dev_phase: ...
    originator: ...
    licensees: [...]
  development_status:   # per-indication faz
    - indication: ...
      phase: ...
      status: ...
  competitive_set:      # search_drug_companies
    - company: ...
      portfolio_overlap: ...
  provenance: "[AdisInsight / <tool> / <ISO>]"
  scope_hash: "adis_pipeline:<hash>"
```

### 5.2 Paylaşım kuralı

- **Aşama 1 (treatment_landscape):** originatör + pipeline çapasını besler.
- **Aşama 2 (pharmaintel regulatory):** originatör MAH + ex-US licensee bilgisini
  `regulatory_matrix`'e taşır; ayrı AdisInsight çağrısı yapmaz.
- **Aşama 4 (pharmapatent landscape):** originatör portföyünü FTO compound patent çapası
  için okur.

---

## 6. Önbellek Yaşam Döngüsü ve Geçerlilik

| Durum | Davranış |
|---|---|
| Aynı run içinde aynı `scope_hash` | Önbellekten döndür; çağrı yapma |
| Aynı run içinde farklı `scope_hash` | Yeni çıkarım (meşru kapsam farkı) |
| Run sonu | Artefaktlar `<RUN_ID>/` dizininde kalıcı; cross-run paylaşım **yapılmaz** (provenance bütünlüğü) |
| Connector fallback kullanıldı | Artefakt `status: degraded` + caveat; downstream WARN gate |

> **Cross-run paylaşım yasağı:** İki ayrı run arasında artefakt paylaşılmaz; her run kendi
> provenance damgasını taşır. Bunun istisnası `datasource-registry.yaml` cached snapshot'ıdır
> (yalnız TİTCK timeout fallback'i, açık tarih damgasıyla).

---

## 7. run_manifest.json Entegrasyonu

```json
{
  "run_id": "RxOS-YYYYMMDD-<TA>-<SUB>-v<N>",
  "cached_artifacts": [
    {"type": "adis_pipeline",   "scope_hash": "...", "produced_stage": 1, "consumed_by": [1,2,4], "status": "ok"},
    {"type": "titck_canonical", "scope_hash": "...", "produced_stage": 2, "consumed_by": [2,4,5], "status": "ok"},
    {"type": "midas_extract",   "scope_hash": "...", "produced_stage": 5, "consumed_by": [5],     "status": "degraded", "caveat": "ThoughtSpot Pong yok; TR-iç degrade"}
  ],
  "connector_call_ledger": {
    "titck_mcp": {"calls": 7, "single_shot_enforced": true},
    "thoughtspot": {"waves": 6, "path_b_rest": true},
    "adisinsight": {"calls": 3}
  }
}
```

`connector_call_ledger.titck_mcp.single_shot_enforced: true` — tek-sefer kuralının
denetlenebilir kanıtı. `false` ise G2 kalite kapısı uyarı verir.

---

## 8. Sub-Agent İzolasyonu (bağlam koruma sözleşmesi)

Bazı aşamalar — özellikle **kanıt sentezi** (medical-research / `rxpraxis-evidence`) ve
**MIDAS ham çıkarım** — büyük ham yük (akademik tam-metin dump'ları, dizi-içinde-dizi MIDAS
satırları) üretir. Bu yük orkestratörün ana bağlamına taşınırsa boru hattı ortasında bağlam
eviction'ı ve token taşması olur. Sözleşme:

- **İzole context:** Yüksek-yük aşamalar bir **sub-agent** (izole context) içinde koşar; ham
  geri çağırmalar orada kalır.
- **Yalnız distilat döner:** Sub-agent orkestratöre **≤1-sayfa sentez** + **Vancouver atıf
  listesi** (PMID/DOI/NCT) döndürür — ham tam-metin DEĞİL. MIDAS için: distile `midas_extract`
  artefaktı (annualized değerler + provenance), ham hücre dizileri değil.
- **Kanonik artefakt köprüsü:** Sub-agent çıktısı bir kanonik artefakta (`adis_pipeline`,
  `midas_extract`) yazılır; downstream aşamalar artefaktı okur (§1-§5), sub-agent'ı yeniden
  çağırmaz.

| Aşama / komut | Sub-agent? | Orkestratöre dönen |
|---|---|---|
| `rxpraxis-evidence` / medical-research kanıt | **Evet** (en yüksek bağlam-riski) | ≤1-sayfa sentez + Vancouver atıflar |
| `rxpraxis-midas` / thoughtspot-roche ham | **Evet** (dizi-içinde-dizi yük) | `midas_extract` (annualized) + provenance |
| `rxpraxis-validate` / fast-path | Hayır (tek-aday, dar yük) | doğrudan karar kartı |

> **Kural:** Bir aşama ham tam-metni orkestratöre taşırsa bu bir **bağlam-disiplini ihlalidir**;
> distilat + atıf döndür, ham yükü §9 ile evict et.

---

## 9. Extract-Then-Evict (ham yük yaşam döngüsü)

Her ham connector geri çağırması (TİTCK raw kayıtları, AdisInsight tam kaydı, MIDAS satırları,
akademik tam-metin) **çıkar → düşür → diske yaz** döngüsünden geçer:

1. **Extract (distile):** Karar için gerekli alanları çıkar (ör. TİTCK: barcode/INN/ATC/holder;
   MIDAS: annualized_chf/standard_units; akademik: özet + atıf). Kanonik artefakt şemasına yaz
   (§3/§4/§5).
2. **Evict (düşür):** Ham yükü **bağlamdan düşür** — tam JSON kayıt, dizi-içinde-dizi satırlar,
   tam-metin gövdesi context'te **tutulmaz**.
3. **Persist (diske yaz):** Ham yük denetim/provenance için `<RUN_ID>/raw/` altına yazılır
   (context'e değil, diske). Distilat artefakt context'te kalır.
4. **Checkpoint:** `scan-ledger` checkpoint güncellenir (hangi artefakt üretildi, hangi ham
   evict edildi, hangi devre açık) — kesinti/eviction sonrası **yeniden yükleme** için.

```yaml
# scan-ledger checkpoint örneği (shared/scan-ledger-schema.json)
checkpoint:
  stage: 2
  produced: ["titck_canonical:ab12cd34ef56"]
  evicted_raw: ["titck_raw_search_drugs", "titck_raw_get_drug"]
  persisted_to: "<RUN_ID>/raw/titck/"
  next: "stage_4_patent"
```

**MIDAS özel akışı:** `midas_searchdata` FULL satırları **dizi-içinde-dizi** (positional)
gelir → `skills/thoughtspot-roche/scripts/ts_getanswer_extractor.py` (Top-N) /
`ts_getanswer_country_extractor.py` (ülke kırılımı) ile çıkar → distile → ham satırları düşür →
diske yaz. `record_size`'ı sınırla (asla `-1`); `meta` bloğunu (`returned/total/truncated/
exact/sampling`) oku ve bilinçli sayfala.

> **Neden:** En pahalı bağlam sızıntısı, distilattan sonra ham yükün context'te kalmasıdır.
> Extract-then-evict, uzun (7-aşamalı) koşumun bağlam bütçesi içinde tamamlanmasını sağlar ve
> §8 sub-agent izolasyonunu tamamlar.
