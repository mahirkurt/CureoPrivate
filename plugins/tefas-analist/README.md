# TEFAS Uzmanı (tefas-analist)

Türkiye yatırım (YAT) ve emeklilik (EMK) fonları için **çok-skill orkestratör** karar-destek
süiti. Risk/getiri analizi, fon tarama, çoklu-fon karşılaştırma, **portföy inşası** ve
**sürekli izleme** — gerekçeli, kaynakça'lı, SPK-feragatli tek raporda.

> **Karar destek niteliğindedir; SPK yatırım danışmanlığı / portföy yöneticiliği /
> al-sat tavsiyesi değildir.**

## Ne yapar (5 mod)

| Mod | Komut | Açıklama |
|---|---|---|
| 1 Tek-fon derin analiz | `/fon-analiz` | Kimlik+dağılım+TER + risk/getiri (Sharpe/Sortino/maxDD/beta/VaR) + akran konumu |
| 2 Kategori/tarama | `/fon-tara` | Kategori/kriter taraması (düşük TER, yüksek Sharpe, …) |
| 3 Çoklu-fon karşılaştırma | `/fon-karsilastir` | 2-5 fon yan yana + korelasyon |
| 4 Portföy inşası (öneri) | `/fon-portfoy` | MVO/risk-parity/HRP tahsis + Baz/İyimser/Kötümser senaryo |
| 5 Sürekli izleme | `/fon-izle` | Rejim değişimi · stil sapması · drawdown alarmı · "ne değişti" |

## Mimari

SMP v1.0 capability-cluster: **fon-analiz-orkestratoru** (8-aşamalı G0-G7 boru hattı) +
6 kaynak skill (fon-haritalama, quant-analiz, piyasa-makro, regulasyon-uyum, portfoy-insa,
izleme) + `start` router. Paylaşılan sözleşmeler: [CONNECTORS.md](./CONNECTORS.md),
[shared/](./shared/).

**İki MCP omurgası:**
- **Borsa MCP** (mevcut) — getiri/NAV serisi/AUM/tarama/benchmark/risksiz oran/makro.
- **fon-mcp** (yeni; `mcp-servers/fon-mcp/`) — portföy dağılımı (zaman-serili)/holdings/
  TER/fon akışı/kurucu-yönetici/EMK.

**Kuant motoru:** `skills/quant-analiz/scripts/` — 12 saf-Python (stdlib) modül; Sharpe,
Sortino, Calmar, maxDD, VaR/CVaR, Monte Carlo, RBSA stil analizi, MVO/HRP optimizasyonu,
yoğunlaşma, maliyet, kalite kompoziti, izleme. Her biri bağımsız CLI + self-test.

## Kurulum

```bash
/plugin marketplace add mahirkurt/marketplace   # veya cureonics-marketplace
/plugin install tefas-analist@cureonics-marketplace
```

Connector'lar (Borsa MCP + fon-mcp) kullanıcının Claude.ai bağlantıları üzerinden tüketilir;
plugin canlı MCP paketlemez. fon-mcp dağıtımı için `mcp-servers/fon-mcp/CLAUDE-AI-BAGLANTI.md`.

## Veri ve sınırlar

- Fiyat/NAV **gün-sonu (EOD)**; gün-içi modellenmez.
- Geçmiş getiri gelecek garantisi değildir.
- Holdings/TER fon-mcp'ye (TEFAS/KAP) bağlıdır; erişilemezse degrade + caveat.
- Portföy optimizasyonu (`portfolio_opt.py`) varsayılan saf-stdlib; numpy opsiyonel.

## Lisans

İç skill varlığı; harici yeniden dağıtım için değildir. Bkz. [LICENSE](./LICENSE).
