---
description: Connector preflight + roster tazeleme + canlı G-PROBE. Bağlı connector'ları yüzey-bilinçli raporlar (claude.ai vs Claude Code), .mcp.json roster'ını CONNECTORS.md ile çapraz-doğrular (G-BUNDLE), Tier-K/Tier-O URL'lerinde canlı initialize handshake çalıştırır, mcp-scout ile roster bakımı önerir.
argument-hint: "[opsiyonel: yenile | probe | grup-adı]"
allowed-tools: Bash(python:*), Bash(curl:*)
---

# /evidentia-connectors — Preflight & Roster Doğrulama

İstek kipi (opsiyonel): **$ARGUMENTS** — boşsa tam preflight raporu.

## 1. Yüzey-Bilinçli Bağlanırlık Raporu

[`CONNECTORS.md`](../CONNECTORS.md) §1'deki beş gruba göre **hangi connector'ın bağlı, hangisinin
manuel ekleme gerektirdiğini** raporla. **Kritik yüzey ayrımı (CONNECTORS.md §6):**
- **Claude Code** → `.mcp.json` roster'ı otomatik bağlar.
- **claude.ai web** → Tier-K/Tier-O remote URL'leri **Settings → Connectors → Add custom
  connector**; Tier-A OAuth Advanced settings. "Otomatik bağlı" varsayma.

Her grup için durum: ✅ bağlı / ⚠️ manuel-gerekli / 🔴 eksik → fallback merdiveni (§2).

## 2. G-BUNDLE — Roster ↔ SSOT Tutarlılığı

`.mcp.json` bundled roster ile `CONNECTORS.md` envanterini çapraz-doğrula (her bundled URL
CONNECTORS.md'de belgeli mi; her Tier-K/O girdisi roster'da mı):
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/g_bundle.py
```
Tutarsızlık → düzeltilecek delta'yı raporla.

## 3. G-PROBE — Canlı initialize Handshake

`probe`/`yenile` istendiğinde (veya periyodik) Tier-K + Tier-O remote URL'lerinde canlı MCP
`initialize` çalıştır (no-fabrication: durum **canlı** doğrulanır, hatırlanmaz):
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/g_probe.py
```
Beklenen: med-terminologies (200, v1.5.7), nih-clinicaltables/nlm-rxnorm/iuphar-gtopdb (200,
pipeworx-gateway). Bir URL 4xx/5xx → raporla; **drug-interaction-mcp HTTP 500 ise** → self-host
`drugddx` deploy durumunu hatırlat (`self-host/drugddx-mcp/BUILD-BRIEF.md`).

## 4. Roster Bakımı (mcp-scout devri)

Yeni kaynak/connector keşfi veya bir bundled connector'ın kalıcı düşmesi → **`mcp-scout`** ile
yeniden keşif/yargı; verified sonuç `.mcp.json` + `CONNECTORS.md`'ye **birlikte** işlenir
(G-BUNDLE tekrar). Tier-K topluluk-yayıncı eklemelerinde least-privilege/sandbox-first notu korunur.

## 5. Güven Hatırlatması

Tier-K genişletme (×4) topluluk-yayıncıdır; hasta-etkili çıktı otoriter kaynakla çapraz-doğrulanır
(CONNECTORS.md §5). Doğrulanamayan canlılık/güvenlik **dürüstçe** raporlanır.
