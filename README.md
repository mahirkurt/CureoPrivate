# cureonics-pharma-marketplace — `rxpraxis` Kurulum Paketi

Bu dizin, **kurulabilir bir Claude Code plugin marketplace'idir**. `rxpraxis` süitini
(`rxos` orkestratörü + 4 kaynak skill + 6 komut + paylaşılan connector sözleşmeleri) tek
komutla kurulabilir biçimde paketler.

```
rxpraxis-marketplace/                     ← marketplace kökü (Claude Code'a EKLENECEK dizin)
├── .claude-plugin/
│   └── marketplace.json                  ← katalog (rxpraxis → ./plugins/rxpraxis)
└── plugins/
    └── rxpraxis/                         ← plugin
        ├── .claude-plugin/plugin.json    ← plugin manifest (v1.1.0)
        ├── commands/   (6 slash komut)
        ├── skills/     (rxos, start, medical-research, pharmaintel, pharmapatent, thoughtspot-roche)
        ├── shared/     (canonical-cache · provenance · run-manifest)
        ├── evals/      (entegrasyon eval'leri)
        ├── CONNECTORS.md · BUILD.md · README.md
        └── titck-cache-mcp-build-playbook.md
```

---

## Ön koşullar

1. **Claude Code** (terminal, VS Code veya JetBrains eklentisi) güncel sürüm.
2. **Connector'lar** — rxpraxis canlı MCP **paketlemez**; connector'ları Claude.ai/Claude Code
   bağlantılarınız üzerinden tüketir. Aşağıdakiler bağlı olmalı (siz zaten bağladınız):
   - **TİTCK Cache** (`titck-cache-mcp.cureonics.workers.dev`) — *birincil, kanonik TİTCK yolu*
   - **TİTCK** (ham upstream / fallback), **Mevzuat**, **Türk Patent**, **ThoughtSpot Spotter**,
     **MIDAS** (`midas-mcp`), **AdisInsight**, **PubMed**, **Clinical Trials**, **Consensus**,
     **Exa** — connector-skill eşlemesi `plugins/rxpraxis/CONNECTORS.md §1`'de.

> Eksik connector tarama-zamanı **degrade mod** ile bildirilir (taramayı durdurmaz); `start`
> skill'i pre-flight'ta bağlı connector'ları raporlar.

---

## Kurulum (yerel dizinden — bu paket)

Claude Code oturumunda:

```
/plugin marketplace add /mutlak/yol/rxpraxis-marketplace
/plugin install rxpraxis@cureonics-pharma-marketplace
```

`/mutlak/yol/rxpraxis-marketplace`, `.claude-plugin/marketplace.json` içeren **bu dizinin**
tam yoludur (ZIP'i açtığınız konum). Kurulumdan sonra Claude Code'u yeniden başlatın veya
oturumu yenileyin.

### Alternatif: Git deposundan

Paketi bir Git deposuna (ör. cureonics.com Gitea) iterseniz:

```
/plugin marketplace add <git-url-veya-owner/repo>
/plugin install rxpraxis@cureonics-pharma-marketplace
```

### Alternatif: kalıcı yapılandırma (settings.json)

Takım/kalıcı kurulum için Claude Code `settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "cureonics-pharma-marketplace": {
      "source": { "source": "directory", "path": "/mutlak/yol/rxpraxis-marketplace" }
    }
  },
  "enabledPlugins": { "rxpraxis@cureonics-pharma-marketplace": true }
}
```

---

## Kurulum doğrulaması

```
/plugin                       # yönetim arayüzü — rxpraxis "installed" görünmeli
/help                         # komut listesinde rxpraxis komutları görünmeli
```

Beklenen **6 komut**: `/rxpraxis-scan` · `/rxpraxis-validate` · `/rxpraxis-regulatory` ·
`/rxpraxis-patent` · `/rxpraxis-midas` · `/rxpraxis-evidence`.

Beklenen **skill'ler** (niyet-tetiklemeli, otomatik yüklenir): `rxos` (orkestratör), `start`
(oryantasyon/router), `medical-research`, `pharmaintel`, `pharmapatent`, `thoughtspot-roche`.

**Hızlı duman testi:** Yeni bir sohbet açıp `rxpraxis nedir, nereden başlayayım?` yazın →
`start` skill'i devreye girip bağlı connector'ları ve komutları raporlamalı.

---

## Tek-asset doğrulama / tam tarama

- **Tek molekül fizibilitesi (hızlı):** `/rxpraxis-validate dapagliflozin 10 mg film tablet`
- **TA / portföy taraması (tam):** `/rxpraxis-scan oftalmoloji topikal jenerik fırsatları`

Tam tarama sırasında, **TİTCK Cache** sayesinde aynı molekül birden çok skill tarafından
sorgulansa da upstream **bir kez** vurulur; `single_shot_enforced` kanıtı
`titck-cache-mcp.cureonics.workers.dev/ledger?session=<Mcp-Session-Id>` ucundan ölçülebilir
(bkz. `plugins/rxpraxis/BUILD.md §4-R1` + `titck-cache-mcp-build-playbook.md`).

---

## Güncelleme / kaldırma

```
/plugin marketplace update cureonics-pharma-marketplace   # katalog yenile
/plugin uninstall rxpraxis@cureonics-pharma-marketplace   # kaldır
```

---

## Kapsam ve sınırlar

- **Kapsam içi:** retail/topluluk-eczanesi kanalı, oral + topikal küçük molekül, tüm terapötik
  alanlar. **Kapsam dışı:** hospital/IV (G0 scope guard reddeder). Bireysel SGK/dava →
  `onko-erisim`; promosyonel denetim → `promo-censor`.
- Bu paket **SMP v1.0** konvansiyonlarına uyar (`plugins/rxpraxis/.claude-plugin/plugin.json`
  → `smp` bloğu). QA için ekosisteminizde `skill-censor` FULL_AUDIT + `smp-orchestrator`
  composability-graph çalıştırılabilir (bkz. `plugins/rxpraxis/BUILD.md §6/§8b`).
