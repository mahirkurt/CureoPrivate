# rxpraxis

**Türkiye-merkezli farmasötik pazar zekâsı ve jenerik/biyobenzer fırsat tarama süiti.**

rxpraxis, dağınık **ticari + regülatuar + bilimsel + patent** zekâsını tek bir savunulabilir
"jenerik/biyobenzer fırsat" kararına dönüştüren bir Claude plugin'idir. Mahir'in mevcut beş
skill'ini (rxos · medical-research · pharmaintel · pharmapatent · thoughtspot-roche) tek bir
**paylaşılan connector sözleşmesi** ve **kanonik-artefakt önbelleği** altında birleştirir.

## Konumlanış

| Özellik | Değer |
|---|---|
| **Kapsam** | Retail/topluluk-eczanesi · oral + topikal küçük molekül · TÜM terapötik alanlar |
| **Kapsam dışı** | Hastane kanalı (IV/infüzyon) — her TA'da |
| **Orkestratör** | `rxos` — 7-aşamalı deterministik boru hattı (G0-G6) |
| **Kaynak skill'ler** | medical-research (Aşama 1) · pharmaintel (Aşama 2,5) · pharmapatent (Aşama 2,4) · thoughtspot-roche (Aşama 5b) |
| **SMP rolü** | capability-cluster (SMP v1.0) |

## Mimari Çekirdek — İki Entegrasyon Sözleşmesi

Süitin tekil skill'lerin toplamından **fazlası** olmasını sağlayan iki dosya:

1. **[CONNECTORS.md](./CONNECTORS.md)** — paylaşılan connector sözleşmesi. Beş skill'e dağılmış
   connector envanterini tek noktaya çeker; connector→skill sorumluluk sınırını, fallback
   zincirlerini ve **tek-sefer TİTCK kuralını** formalize eder.

2. **[shared/canonical-cache-contract.md](./shared/canonical-cache-contract.md)** — kanonik
   artefakt önbelleği. rxos'un "tek-sefer TİTCK" desenini **üç pahalı artefakta** genelleştirir
   (`titck_canonical` · `midas_extract` · `adis_pipeline`): aynı veri boru hattı boyunca **bir
   kez** çıkarılır, içerik-adresli anahtarla önbelleğe alınır, sonraki aşamalar **okur**.

## Dizin Yapısı

```
rxpraxis/
├── .claude-plugin/plugin.json        # plugin manifesti (SMP v1.0-uyumlu)
├── CONNECTORS.md                     # ★ paylaşılan connector sözleşmesi
├── README.md · BUILD.md              # genel bakış + vendor/entegrasyon yol haritası
├── commands/                         # 6 slash komutu
│   ├── rxpraxis-scan.md              # tam 7-aşamalı tarama (flagship)
│   ├── rxpraxis-validate.md · -regulatory.md · -patent.md · -midas.md · -evidence.md
├── shared/                           # ★ plugin-düzeyi paylaşılan katman
│   ├── canonical-cache-contract.md   # tek-sefer artefakt önbelleği
│   ├── provenance-standard.md        # birleşik kaynak damgalama
│   └── run-manifest-schema.json      # orkestrasyon kaydı + connector ledger
├── skills/
│   ├── start/                        # oryantasyon + yönlendirme
│   ├── rxos/                         # orkestratör (plugin-uyumlu)
│   ├── medical-research/             # vendored (BUILD.md §2)
│   ├── pharmaintel/                  # vendored
│   ├── pharmapatent/                 # vendored
│   └── thoughtspot-roche/            # vendored
└── evals/evals.json                  # plugin-düzeyi entegrasyon eval'leri
```

## Hızlı Başlangıç

1. `rxpraxis:start` ile süiti tanıyın ve bağlı connector'ları kontrol edin.
2. Tam fırsat taraması: `/rxpraxis-scan [terapötik alan / molekül briefi]`.
3. Tekil yetenekler: `/rxpraxis-regulatory` · `/rxpraxis-patent` · `/rxpraxis-midas` · `/rxpraxis-evidence`.

## Kurulum

Bu plugin canlı MCP sunucusu paketlemez; tüm connector'lar Claude.ai bağlantıları üzerinden
tüketilir (bkz. CONNECTORS.md). Süitin tam çalışması için CONNECTORS.md §1'deki connector'ların
bağlı olması beklenir; eksikler `start` skill'i tarafından raporlanır ve ilgili aşamalar
degrade modda çalışır.

Vendor + entegrasyon prosedürü ve QA stratejisi için **[BUILD.md](./BUILD.md)**.
