# rxpraxis — Birleşik Provenance Damgası Standardı

**Belge sınıfı:** Normatif — plugin-düzeyi
**Sürüm:** 1.0.0

Süitin beş skill'i farklı provenance gelenekleri kullanıyordu (pharmapatent
`[MCP/tool/tarih]`, thoughtspot-roche `(guid, session, generation, frame)`, medical-research
Vancouver, pharmaintel 4-parçalı). Bu dosya hepsini tek bir damgalama gramerinde birleştirir;
her skill, kaynak tipine göre uygun damgayı uygular.

---

## 1. Kaynak Tipine Göre Damga Grameri

### 1.1 MCP connector verisi
```
[<MCP adı> / <tool_name> / <erişim_ISO>]
```
Örnek: `[TİTCK MCP / get_price_history / 2026-06-14]`

### 1.2 Mevzuat MCP (mevzuat kimliği zorunlu)
```
[Mevzuat MCP / <tool> / <mevzuat_id> / <erişim_ISO>]
```
Örnek: `[Mevzuat MCP / search_mevzuat / SMK 6769 / 2026-06-14]`

### 1.3 IQVIA MIDAS (yapısal provenance — alıntılanmaz, alana gömülür)
```yaml
provenance:
  datasource_guid: "..."
  session_identifier: "..."
  generation_number: ...
  frame_url: "..."
  extract_timestamp_utc: "..."
roche_confidential: true
```
> MIDAS provenance **rapor gövdesinde görünmez** (Roche confidential); yalnız sidecar/JSON
> artefaktında + İç Denetim Kaydında taşınır.

### 1.4 Akademik (Vancouver)
```
PMID/DOI/NCT + erişim tarihi
```
Örnek: `(PMID 38… , erişim 2026-06-14)` · `(NCT0…, ClinicalTrials.gov)`

### 1.5 Birincil web (yalnız URL keşfi sonrası doğrulama)
```
<kaynak adı>, <URL>, erişim <ISO>
```
web_search/Exa/Tavily **doğrulanabilir olgunun birincil alıntısı olamaz**; yalnız URL keşfi
için kullanılır, ardından birincil kaynak web_fetch ile teyit edilir.

---

## 2. Güven Derecelendirmesi (pharmaintel mirası)

Her maddi iddia için: **High / Medium / Low / Unknown**. İki-kaynak triangülasyonu maddi
iddialarda zorunlu. Tek-kaynak iddialar Low/Unknown işaretlenir.

---

## 3. İki Katmanlı Çıktı (medical-research v8.1 + pharmaintel v8.1 mirası)

- **Katman A (okuyucu-yüzlü):** dergi kalitesinde temiz kopya; connector adı, gate ID,
  axis kodu, çağrı telemetrisi **görünmez**.
- **Katman B (render-dışı):** İç Denetim ve Sağlama Kaydı — tüm provenance damgaları,
  güven dağılım tablosu, MIDAS yapısal provenance, connector call ledger. `<!-- RENDER:EXCLUDE-FROM-HERE -->`
  … `<!-- RENDER:EXCLUDE-TO-HERE -->` sentinel çifti ile sarılır.

---

## 4. Roche Confidential İşaretleme

MIDAS-türevi her alan `roche_confidential: true` taşır. Bu alanlar:
- Rapor gövdesinde **ham GUID/session göstermez**.
- Downstream render skill'leri (carbon-html-report/carbon-pptx) bu işareti tanır ve confidential
  bloğu uygun şekilde işler.
- Plugin dışına (external redistribution) çıkmaz.
