---
description: Connector preflight + roster tazeleme + canlı G-PROBE. Bağlı connector'ları yüzey-bilinçli raporlar (claude.ai vs Claude Code), .mcp.json roster'ını CONNECTORS.md ile çapraz-doğrular (G-BUNDLE), Tier-K/Tier-O URL'lerinde canlı initialize handshake çalıştırır, mcp-scout ile roster bakımı önerir.
argument-hint: "[opsiyonel: yenile | probe | grup-adı]"
allowed-tools: Bash(python:*), Bash(curl:*)
---

# /evidentia-connectors — Preflight & Roster Doğrulama

İstek kipi (opsiyonel): **$ARGUMENTS** — boşsa tam preflight raporu.

## 1. Yüzey-Bilinçli Bağlanırlık Raporu

[`CONNECTORS.md`](../CONNECTORS.md) §1'deki katmanlamaya göre raporla: **§1.1 Bibliyografik Çekirdek**
(her PRISMA taramasında her-zaman-açık) bağlı mı; **§1.2–§1.6 opsiyonel zenginleştirme modülleri**
(alan/ilaç/regülatuar/HTA/KOL/Türkiye) hangileri bağlı, hangileri manuel ekleme gerektiriyor.
**Kritik yüzey ayrımı (CONNECTORS.md §6):**
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

## 2b. G-IDENTITY — Self-host Worker Kimlik Tutarlılığı

Her self-host Worker'ın kendini DÖRT yerde birden aynı adla tanıtması gerekir (`auth.ts` REALM,
başlık yorumu, `package.json` name, `wrangler.jsonc` name):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/g_identity.py
```
REALM kozmetik DEĞİLDİR: RFC 9728 `resource_name`'i, OAuth `client_id`'sini, 401 `WWW-Authenticate`
realm'ini ve kullanıcının connector eklerken okuduğu **onay sayfasının başlığını** besler. 2026-08-07
denetimi üç Worker'ın (`ema`/`globocan`/`who-gho`) canlıda kendini `openfda-mcp` diye tanıttığını
buldu — `auth.ts` kopyalanırken REALM yerelleştirilmemişti. Her Worker'ın kendi testleri bunu
göremez (hepsi kendi yanlış sabitini doğrular); yalnız bu ÇAPRAZ karşılaştırma görür.

## 3. G-PROBE — Canlı initialize Handshake

`probe`/`yenile` istendiğinde (veya periyodik) Tier-K + Tier-O remote URL'lerinde canlı MCP
`initialize` çalıştır (no-fabrication: durum **canlı** doğrulanır, hatırlanmaz):
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/g_probe.py
```
Beklenen (**2026-06-28 canlı re-probe**, `connector-registry.md §8` Probe Log): med-terminologies
(200; ⚠️ `icd11_search` AUTH-kırık → ICD-11 = `openfda`), nih-clinicaltables/nlm-rxnorm/iuphar-gtopdb
(200, pipeworx-gateway; ⚠️ nlm-rxnorm `interactions`=404 / `related`=400, nih `icd10cm` isim→0),
**drugddx (200, CANLI, Tier-O)**, **openfda (Bearer; openFDA + WHO ICD-11)**, **PopHIVE (200, ABD epi;
US-only)**, **Mevzuat Bilgisi (200, ikincil)**. Bir URL 4xx/5xx → raporla. **Yalnız §2.6 whitelist
araçları** çağrılır (pipeworx jenerikleri DEĞİL — G-WHITELIST); hasta-etkili çıktı otoriter kaynakla
çapraz-doğrulanır (G-XVAL). Elicit: OAuth-gated (claude.ai-bağlı) → tools/list canlı OAuth probe bekliyor.

## 4. Roster Bakımı (mcp-scout devri)

Yeni kaynak/connector keşfi veya bir bundled connector'ın kalıcı düşmesi → **`mcp-scout`** ile
yeniden keşif/yargı; verified sonuç `.mcp.json` + `CONNECTORS.md`'ye **birlikte** işlenir
(G-BUNDLE tekrar). Tier-K topluluk-yayıncı eklemelerinde least-privilege/sandbox-first notu korunur.

## 5. Güven Hatırlatması

Tier-K genişletme (×4) topluluk-yayıncıdır; hasta-etkili çıktı otoriter kaynakla çapraz-doğrulanır
(CONNECTORS.md §5). Doğrulanamayan canlılık/güvenlik **dürüstçe** raporlanır.
