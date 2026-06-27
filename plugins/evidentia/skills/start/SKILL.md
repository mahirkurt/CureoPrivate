---
name: start
description: >-
  evidentia süitine giriş ve yönlendirme. Bağlı MCP connector'larını (akademik çekirdek,
  Türkiye Dörtlüsü, regülatuar/epidemiyoloji, mcp-scout genişletme, self-host drugddx)
  kontrol eder, flagship medical-research v8.2.0 skill'ini ve dört komutu tanıtır, kullanıcının
  niyetine göre doğru komuta/eksene yönlendirir. İlk kez süitle çalışırken, hangi connector'ların
  bağlı olduğunu görmek için, ya da "evidentia nedir / nereden başlamalıyım / hangi komutu
  kullanmalıyım / connector'larım bağlı mı" türü oryantasyon sorularında kullanın. Tetikleyiciler —
  evidentia başlat, süit oryantasyonu, connector kontrolü, "ne yapabilirsin", "nereden başlayayım",
  "hangi eksen", araştırma motoru kurulumu, kanıt sentezi nereden.
---

# evidentia — Başlangıç & Yönlendirme

Bu skill, `evidentia` araştırma süitine **giriş kapısıdır**. Beş adımı sırayla yürütün; ağır
işi flagship `medical-research` skill'i ve dört komut yapar.

---

## Adım 1 — Karşılama

Kullanıcıya kısaca: evidentia, **çok-kaynaklı bilimsel kanıt sentezi + Türkiye-pazarı**
araştırma motorudur. `medical-research` v8.2.0 flagship'ini, 20+ doğrulanmış connector'ı ve
mcp-scout ile canlı-doğrulanmış klinik genişletme MCP'lerini tek pakette toplar. 10 uzmanlık
ekseni vardır: Onko · Heme · Regülatuar · HTA · MedAffairs · İmmün · Nöro · Nadir · DrugIntel ·
Epidemiyoloji.

---

## Adım 2 — Connector Preflight (yüzey-bilinçli)

Araştırmaya başlamadan **bağlanırlığı raporlayın**. Bu, çift connector sorgusunu ve "neden veri
yok" şaşkınlığını önler. [`CONNECTORS.md`](../../CONNECTORS.md) ve
[`shared/canonical-cache-contract.md`](../../shared/canonical-cache-contract.md) **normatiftir**.

Kontrol listesi (gruba göre):
1. **Akademik çekirdek** — PubMed/EPMC, Clinical Trials, Consensus, Scholar Gateway, bioRxiv,
   YÖK Tez, Exa, Tavily (kota?).
2. **Curated + mekanizma** — AdisInsight, ChEMBL (+ Synapse/OpenTargets/Wiley koşullu).
3. **Türkiye Dörtlüsü + IP** — TİTCK (+ Cache), Mevzuat, Türk Patent, RegulatoryMCP (latency!),
   NPI, annas-mcp.
4. **mcp-scout genişletme (Tier-K)** — med-terminologies, NIH Clinical Tables, NLM RxNorm,
   IUPHAR GtoPdb → **topluluk-yayıncı: least-privilege, sandbox-first**.
5. **Self-host** — drugddx (deploy edildi mi? `/health` ok mu?).

> **Yüzey ayrımı (kritik):** **Claude Code**'da plugin `.mcp.json` roster'ını otomatik bağlar.
> **claude.ai web**'de Tier-K/Tier-O remote URL'leri **Settings → Connectors → Add custom
> connector** ile, Tier-A OAuth'u Advanced settings ile **manuel** eklenir. "Her şey otomatik
> bağlı" varsaymayın; eksikse kullanıcıya hangi connector'ı nereden ekleyeceğini söyleyin.

Eksik connector → graceful: o eksenin **fallback merdivenini** (CONNECTORS.md §2) belirtin,
araştırmayı durdurmayın.

---

## Adım 3 — Flagship Skill Tanıtımı

`medical-research` v8.2.0 ağır işi yapar: native-MCP-first çözümleme, probe-verified-only,
Adım 0–5 protokolü (kapsam → kaynak seçimi → çoklu-kaynak getirme → çapraz-doğrulama → sentez →
temiz-kopya). Kullanıcı doğrudan bir araştırma sorusu sorduğunda bu skill devreye girer; `start`
yalnızca yönlendirir.

---

## Adım 4 — Komut Tanıtımı

| Komut | Ne yapar |
|---|---|
| `/evidentia <soru>` | **Tam kanıt sentezi koşumu** — kapsam, çoklu-kaynak, çapraz-doğrulama, sentez |
| `/evidentia-connectors` | **Preflight + roster tazeleme** (mcp-scout) + G-PROBE canlı doğrulama |
| `/evidentia-fulltext <ref>` | **Tam-metin kademe** — EPMC→Paper Search→annas→Wiley (copyright-kapılı) |
| `/evidentia-kol <alan/molekül>` | **KOL haritası** — OpenAlex→S2→EPMC→NPI→YÖK Akademik |

Ağır/geniş fan-out koşumlar için `evidence-synthesizer` alt-ajanı bağlamı izole eder.

---

## Adım 5 — Niyet Yönlendirme + Scope Guard

| Kullanıcı niyeti | Yönlendir |
|---|---|
| "Şu molekül/hastalık için kanıt + pazar" | `/evidentia` |
| "Connector'larım bağlı mı / roster güncel mi" | `/evidentia-connectors` |
| "Şu makalenin tam metni" | `/evidentia-fulltext` (copyright kapısı) |
| "Bu alanda KOL kim" | `/evidentia-kol` |
| Belirsiz / çok-eksenli | `/evidentia` (medical-research kapsam-belirleme yapar) |

**Scope Guard (devir):**
- Bireysel SGK reddi / dava dilekçesi / mütalaa → **`ius-salutis`** veya **`onko-erisim`**.
- Promosyonel materyal MLR denetimi → **`promo-censor`**.
- Ticari strateji / asset profili / catalyst → **`pharmaintel`** (evidentia kanıt katmanını besler).
- Patent FTO / hükümsüzlük → **`pharmapatent`**.
- Yeni connector keşfi / self-host talimatnamesi → **`mcp-scout`**.
- Yayın-kalite render → **`carbon-html-report`** / **`carbon-pptx`**.

Şüphede: medical-research evrenseldir → `/evidentia` ile başlayın; kapsam-belirleme adımı doğru
ekseni seçer.
