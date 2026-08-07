# fleetkit — plugin MCP filosu tek-kaynak altyapısı

Her plugin'in MCP filosu **tek bir `plugins/<ad>/fleet.yaml`** dosyasında tanımlanır; `.mcp.json`, `.codex-plugin/plugin.json` `mcpServers` bloğu, `fleet.lock.json` ve `⟨GEN⟩` işaretli belge blokları **ondan üretilir**.

## Neden var

2026-08-06 filo denetimi, filo tanımının plugin başına 3-8 yerde elle tutulmasının üç somut arıza sınıfı ürettiğini ölçtü:

**1. Ölü katmanlar (3).** Anahtarsız wire edilmiş ama Bearer isteyen uçlar — her çağrıda 401, hiçbir yerde görünmüyor:

| Plugin · server | Kök neden |
|---|---|
| `edupedia · maarif-mufredat` | Plugin'in OTORİTE kaynağı (105 MEB ders kitabı); preflight onu *"authless"* ilan ettiği için arızayı bildiremiyordu |
| `evidentia · titck-cache` | 2026-08-02 TİTCK kapılanması bu plugin'de kaçırıldı (`rxpraxis` düzeltilmiş, `lex-sanitas` + `evidentia` atlanmış) |
| `vekayinuvis · tavily` | `TAVILY_API_KEY` Doppler'da vardı, wire'a hiç girmemişti |

**2. Sapmış codex blokları (2).** `brand-ecosystem-core`'un `.codex-plugin` bloğu 7 gerçek server'ın **hiçbirini** taşımıyordu; buna karşılık var olmayan `exa`/`figma`/`godaddy`'yi ilan ediyordu. `evidentia`'nın `openathens` rol metni 11 gün eskiydi.

**3. Sürüm sürüklenmesi (5).** `marketplace.json` — yani **dağıtım yüzeyi** — `edupedia`'yı 0.6.5, `rxpraxis`'i 1.2.1 gösteriyordu; gerçek sürümler 0.7.0 ve 1.2.2 idi.

Hiçbiri bir teste takılmıyordu, çünkü hiçbiri türetilmiyordu.

## Bileşenler

| Dosya | Ne zaman koşar | İş |
|---|---|---|
| `gen_fleet.py` | geliştirme | `fleet.yaml` → türev artefaktlar |
| `check_drift.py` | **CI kapısı** (ağ gerektirmez) | 5 denetim: türev güncelliği · sürüm tutarlılığı · vendor bayt-özdeşliği · çift `hooks.json` · düzyazı sayıları |
| `fleet_probe.py` | **runtime** (hook'lar) | canlı MCP `initialize`; `auth_missing` ≠ `unauthorized` |
| `vendor.py` | geliştirme | kanonik prob'u hook'lu plugin'lere birebir kopyalar |
| `audit_plugins.py` | elle / periyodik | 5 eksenli **canlı** filo denetimi (ağ + Doppler ister) |
| `check_tools.py` | elle / periyodik | **araç-düzeyi** canlı denetim: `tools_used` beyanı ↔ sunucunun gerçek `tools/list`'i (+ `--call` ile salt-okunur duman testi). Ağ + Doppler ister |
| `check_sources.py` | **CI (bilgilendirici)** | `programmatic_source_healthcheck.yaml` sözleşmesini koşar (ağ, secret YOK) |
| `bootstrap_fleet.py` | tek seferlik | mevcut `.mcp.json`'dan `fleet.yaml` üretir |

### `check_tools.py` neden ayrı bir kapı

`audit_plugins.py` her uca yalnız `initialize` gönderir. 200 dönen sunucu "sağlıklı" sayılır — ama **sağlık ≠ işlevsellik**. 2026-08-07 ölçümünde dokuz plugin'in tamamı `initialize` düzeyinde temizken `lex-sanitas` üç FANTOM araç beyan ediyordu: `titck.search_medical_devices` (TİTCK'in 66 aracının hiçbiri cihaz aracı değil — kategori hatası), `eudamed_search_actors` ve `eudamed_probe` (canlı yüzeyde yok). Beyan `.mcp.json`'daki `_role` alanına aktığı için bu, modelin gördüğü canlı wiring'de duruyordu.

```bash
# envanter karşılaştırması
doppler run -- python3 tools/fleetkit/check_tools.py lex-sanitas
# + argümansız salt-okunur araçları GERÇEKTEN çağır
doppler run -- python3 tools/fleetkit/check_tools.py lex-sanitas --call
```

`--call` katı bir allowlist kullanır (yalnız envanter/kimlik uçları) — yazan, indiren veya ücret doğuran hiçbir araç çağrılmaz.

## Günlük kullanım

```bash
# fleet.yaml düzenledikten sonra
python3 tools/fleetkit/gen_fleet.py

# commit öncesi (ağsız, deterministik)
python3 tools/fleetkit/check_drift.py --all

# canlı sağlık (Doppler ister)
doppler run -p cureohub -c dev_personal -- python3 tools/fleetkit/audit_plugins.py

# kanonik prob'u değiştirdiysen
python3 tools/fleetkit/vendor.py
```

## İki tasarım kararı

**Vendor, paylaşım değil.** Plugin'ler marketplace'ten **tek dizin** olarak kurulur; repo kökündeki paylaşılan kod kurulu kopyaya gitmez. Bu yüzden runtime bileşeni (`fleet_probe.py`) her plugin'in içine **birebir kopyalanır** ve `check_drift [3]` bayt-özdeşliği denetler — `edupedia`'nın `app/gates/` vendor'lı validator deseninin aynısı. Geliştirme araçları (`gen_fleet`, `check_drift`) plugin'e girmez.

**Hook'lar PyYAML görmez.** `fleet.yaml` insan içindir; hook'lar `fleet.lock.json`'u **stdlib `json`** ile okur. Kullanıcı sisteminde PyYAML kurulu olmasa da preflight çalışır.

## Prob istemcisinin üç sertleştirmesi

Üçü de **sağlıklı** server'ları sahte arızalı gösteriyordu — yani prob, teşhis etmek için var olduğu hatanın aynısını üretiyordu. Hepsi regresyon testinde:

| Sertleştirme | Olmazsa |
|---|---|
| Açık `User-Agent` | urllib varsayılanı Cloudflare bot kuralına takılır → **tüm** cureonics uçları sahte 403/1010 |
| 256 KB okuma sınırı | `oecd`'nin 32 KB `initialize` gövdesi ortasından kesilir → sahte `error` |
| 12 sn eşik | `anamnesis` kalıcı olarak ~11 sn sürer (soğuk başlangıç değil) → sahte `unreachable` |
| 307/308 takibi | FastMCP `/mcp` → `/mcp/` yönlendirmesi (`edupedia · modul-yayin`) → sahte `error` |

## `fleet.yaml` şeması (v2)

```yaml
version: 2
plugin: <ad>
plugin_version: "x.y.z"
prose_count_check: true        # ops. — düzyazıdaki "N MCP" iddialarını denetle

servers:
  - name: mevzuat
    url: https://mevzuat.cureonics.com/mcp
    tier: primary              # serbest metin — her plugin kendi taksonomisini kullanır
    auth_env: MEVZUAT_MCP_API_KEY   # null ⇒ public (anahtarsız 200 BEKLENİR)
    role: >-                   # ops. — .mcp.json _role notu
      …
    shard: S1                  # ops. — alt-ajan araç kısıtı için
    modes: [ALL]               # ops. — mod×server matrisi için
    gate: G7                   # ops. — bağlı kalite kapısı
    extra:                     # ops. — ek _* alanları .mcp.json'a aynen geçer
      _probe: "…"

companions: []                 # ops. — wire EDİLEMEZ dış connector'lar
delegations: []                # ops. — zorunlu plugin delegasyonları
generated_blocks: []           # ops. — ⟨GEN⟩ hedefleri (dosya + üretici + config)
mcp_comment: >-                # ops. — .mcp.json _comment'ine eklenir
```

`tier` **serbest metindir**: `lex-sanitas` `primary`/`comparative`/`doctrine`, `evidentia` `K`/`K-epi`/`O` kullanır. Sabit bir liste dayatmak mevcut sözlükleri yeniden yazmak olurdu.

## Uyarı

`bootstrap_fleet.py --all --force` **reddedilir** — elle yazılmış bir `fleet.yaml`'i sessizce ezer (`lex-sanitas`'ta bir kez oldu; `companions`/`delegations`/`generated_blocks` kayboldu). Ezmek istediğiniz plugin'i **adıyla** verin.
