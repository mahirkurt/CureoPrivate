# socius-vigil plugin — Uygulama Planı

> **Agentic çalışanlar için:** ZORUNLU ALT-SKILL: bu planı görev-görev uygulamak için `superpowers:subagent-driven-development` (önerilen) veya `superpowers:executing-plans` kullanın. Adımlar checkbox (`- [ ]`) sözdizimiyle izlenir.

**Hedef:** `socius-vigil.skill` v2.3.0 tek-dosya beceri paketini, 13 slash komutlu · hook-uygulamalı · üç alt-ajanlı bir Claude Code plugin'ine (`plugins/socius-vigil/`, v1.0.0) dönüştürmek.

**Mimari:** Flagship skill protokol gövdesini taşır (§0–§14, G1–G16, `references/`+`schemas/`+`scripts/`+`evals/` **tek kopya** — P1); 12 mod skill'i ≤120 satırlık ince kabuklar olarak flagship'e göreli yolla atıf verir; G7/G9/G10/G12/G13/G14/G16 kapıları düz yazıdan **fail-open Python hook'larına** taşınır; ağır fan-out üç izole alt-ajana verilir.

**Teknoloji yığını:** Claude Code plugin manifesti (`.claude-plugin/plugin.json`), Codex manifesti (`.codex-plugin/plugin.json`), HTTP MCP wire (`.mcp.json`), stdlib-yalnız Python 3.8+ hook script'leri, stdlib `unittest` (ağ yok).

**Spec:** [`docs/superpowers/specs/2026-08-06-socius-vigil-plugin-design.md`](../specs/2026-08-06-socius-vigil-plugin-design.md) — plan spec'ten argüman kurar; uygulayıcı ikisini birlikte okur.

## Global Kısıtlar

Spec'in P1–P4 değişmezleri her görevde geçerlidir:

- **P1 — Tek doğruluk kaynağı.** `references/`, `schemas/`, `scripts/`, `evals/` **yalnız** `skills/socius-vigil/` altında bulunur. Mod skill'leri kopyalamaz; `../socius-vigil/references/NN-*.md` göreli yoluyla atıf verir.
- **P2 — Hook'lar fail-open.** Hiçbir hook MCP çağrısını bloklamaz. `Stop` hook'ları `{"decision":"block","reason":…}` ile turu **tamamlatır**, iptal etmez. Her script `try/except: pass` ile sarılır; `stop_hook_active` görülünce derhal `return`.
- **P3 — Meta-tur baskılaması.** Plugin'in kendi kaynağı üzerinde çalışılan oturumlarda `stop_gates` ve `clean_copy_guard` ateşlenmez.
- **P4 — Degrade beyanı.** Connector yoksa katman atlanır **ve** manifestoda gerekçesiyle beyan edilir; sessiz atlama yasak.
- **Kanonik araç adları (18 — hiçbir yerde başka bir `sv_*` adı yazılmaz):**
  `sv_build_query_library` · `sv_source_inventory` · `sv_search` · `sv_search_fallback` · `sv_fetch` · `sv_retail_review_scan` · `sv_retail_filter` · `sv_extract_rating` · `sv_extract_reviews` · `sv_sentiment` · `sv_admiralty_score` · `sv_ach_matrix` · `sv_triangulate` · `sv_market_synthesis` · `sv_kol_stance` · `sv_icsr_check` · `sv_collect_pipeline` · `sv_quality_gate`
  (Sunucu ayrıca ChatGPT-uyumluluk alias'ları `search`/`fetch` yayınlar; **18'e dahil değildirler.**)
- **Worker URL:** `https://socius-vigil-mcp.cureonics.workers.dev/mcp` — Bearer `${SOCIUS_VIGIL_MCP_API_KEY}`.
- **Kanonik kaynak paket:** `/mnt/thunderbolt/workspaces/CureoHub/socius-vigil.skill` (zip, v2.3.0, 37 dosya: SKILL.md 456 satır + `skill-manifest.yaml` + 16 referans + 4 şema + 12 script + 2 eval dosyası).
- **Python:** stdlib yalnız, 3.8+ uyumlu. Hook'larda üçüncü-parti import **yasak**.
- **Dil:** kullanıcıya görünen tüm metin Türkçe; kod tanımlayıcıları İngilizce.
- **Yollar:** hepsi `/mnt/thunderbolt/workspaces/CureoPrivate` köküne göredir.

**Spec'ten iki ölçülmüş sapma** (uygulayıcı bunları aykırılık sanmasın):

1. Spec §3 `.codex-plugin/{plugin.json,openai.yaml}` diyor; repodaki iki emsal (`brand-ecosystem-core`, `lex-sanitas`) **yalnız `plugin.json`** taşıyor — `openai.yaml` hiç yok. Emsal izlenir → `openai.yaml` üretilmez.
2. Spec §9 "`brand-ecosystem-core/.mcp.optional.json`'daki socius-vigil girdisi kalır" diyor; ölçüm: o dosyanın adı `mcp.optional.json` (nokta yok) ve socius-vigil girdisi orada **değil**, `brand-ecosystem-core/.mcp.json` içinde wire'lı. `_role` güncellemesi gerçek dosyada yapılır (Görev 11).

---

### Görev 1: Plugin iskeleti + P1 tek-kopya gövde taşıma

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/.claude-plugin/plugin.json`
- Oluştur: `plugins/socius-vigil/.codex-plugin/plugin.json`
- Oluştur: `plugins/socius-vigil/.mcp.json`
- Oluştur: `plugins/socius-vigil/.mcp.optional.json`
- Oluştur: `plugins/socius-vigil/skills/socius-vigil/**` (zip'ten çıkarılır)
- Test: `plugins/socius-vigil/tests/test_structure.py`

**Arayüzler:**
- Üretir: `plugins/socius-vigil/` kökü. Tüm hook'lar `PLUGIN_ROOT`'u `Path(__file__).resolve().parent.parent.parent` ile bulur. Flagship yolu `skills/socius-vigil/`; referanslar `skills/socius-vigil/references/NN-*.md`.

- [ ] **Adım 1: Yapı testini yaz**

`plugins/socius-vigil/tests/test_structure.py`:

```python
#!/usr/bin/env python3
"""Plugin yapısı + P1 tek-kopya değişmezi. stdlib unittest, ağ yok."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestManifest(unittest.TestCase):
    def test_plugin_json_gecerli(self):
        d = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(d["name"], "socius-vigil")
        self.assertEqual(d["version"], "1.0.0")
        self.assertEqual(d["mcpServers"], "./.mcp.json")
        self.assertFalse(d["defaultEnabled"])

    def test_userconfig_dort_anahtar_opsiyonel_ve_hassas(self):
        uc = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["userConfig"]
        for key in ("socius_vigil_api_key", "exa_api_key", "tavily_api_key", "anamnesis_api_key"):
            self.assertIn(key, uc)
            self.assertFalse(uc[key].get("required", False), key)
            self.assertTrue(uc[key].get("sensitive", False), key)

    def test_codex_manifesti_ayni_ad_ve_surum(self):
        cc = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        cx = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual((cc["name"], cc["version"]), (cx["name"], cx["version"]))


class TestMcpWire(unittest.TestCase):
    def _core(self):
        return json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]

    def test_cekirdek_filo_dort_server(self):
        self.assertEqual(set(self._core()), {"socius-vigil", "exa", "tavily", "anamnesis"})

    def test_core_server_worker_urlsi_ve_bearer(self):
        core = self._core()["socius-vigil"]
        self.assertEqual(core["url"], "https://socius-vigil-mcp.cureonics.workers.dev/mcp")
        self.assertEqual(core["headers"]["Authorization"], "Bearer ${SOCIUS_VIGIL_MCP_API_KEY}")

    def test_her_serverin_rol_aciklamasi_var(self):
        for name, cfg in self._core().items():
            self.assertTrue(cfg.get("_role", "").strip(), name)

    def test_opsiyonel_filo_alti_server(self):
        opt = json.loads((ROOT / ".mcp.optional.json").read_text(encoding="utf-8"))["mcpServers"]
        self.assertEqual(set(opt), {"tripadvisor", "pubmed-epmc", "consensus",
                                    "clinical-trials", "titck", "thoughtspot"})


class TestFlagshipGovde(unittest.TestCase):
    def test_kanonik_varliklar_tasindi(self):
        base = ROOT / "skills/socius-vigil"
        self.assertTrue((base / "SKILL.md").exists())
        self.assertTrue((base / "skill-manifest.yaml").exists())
        self.assertEqual(len(list((base / "references").glob("*.md"))), 16)
        self.assertEqual(len(list((base / "schemas").glob("*.json"))), 4)
        self.assertEqual(len(list((base / "scripts").glob("*.py"))), 12)
        self.assertTrue((base / "evals/bioderma_atoderm_creme_fr.md").exists())

    def test_p1_referanslar_tek_kopya(self):
        for d in (ROOT / "skills").iterdir():
            if not d.is_dir() or d.name == "socius-vigil":
                continue
            for forbidden in ("references", "schemas", "scripts"):
                self.assertFalse((d / forbidden).exists(), f"{d.name} {forbidden} kopyalamış")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate
python3 plugins/socius-vigil/tests/test_structure.py -v
```

Beklenen: `FileNotFoundError` — hepsi FAIL.

- [ ] **Adım 3: Kanonik gövdeyi zip'ten çıkar**

```bash
mkdir -p plugins/socius-vigil/skills
unzip -q /mnt/thunderbolt/workspaces/CureoHub/socius-vigil.skill -d plugins/socius-vigil/skills
ls plugins/socius-vigil/skills/socius-vigil
```

Zip kökü zaten `socius-vigil/` olduğu için doğrudan `skills/socius-vigil/` altına açılır. Çıkan `CHANGELOG.md` flagship'in kendi günlüğüdür; plugin kökündeki CHANGELOG (Görev 12) ondan ayrıdır.

- [ ] **Adım 4: `.claude-plugin/plugin.json` yaz**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
  "name": "socius-vigil",
  "displayName": "Socius-Vigil",
  "version": "1.0.0",
  "description": "Nitelikli pazar araştırması + sosyal dinleme/OSINT orkestrasyon süiti. 13 komut: pazar-raporu (uçtan uca §0–§14 rapor), rakip (SoV→ESOV + konumlandırma + beyaz alan), voc (VoC/Kano sürücü-bariyer), fiyat, trend, kol (profil×duruş + açıklama), perakende (yorum madenciliği + sahte-yorum sezgisi), vijilans (ICSR 4-kriter + Admiralty + ACH), hizli-tarama, yayin (temiz-kopya geçişi), start, durum. Toplama ve deterministik skorlama Social Listening MCP'sinin 18 sv_* aracıyla yapılır; yorum ve sentez skill katmanına aittir. G1–G16 kapıları hook'larla uygulanır: MCP araç-çağrı defteri (G7/G12), no-fabrication (G9), temiz-kopya jeton taraması (G16). WEB-RADR değişmezi: AE sinyali tespit-doğrula-yorumla-eskale edilir, resmî PV'de dosyalanmaz.",
  "author": { "name": "Cureonics", "url": "https://cureonics.com" },
  "homepage": "https://github.com/mahirkurt/CureoPrivate/tree/main/plugins/socius-vigil",
  "repository": "https://github.com/mahirkurt/CureoPrivate",
  "license": "UNLICENSED",
  "keywords": [
    "social-listening", "sosyal-dinleme", "market-intelligence", "pazar-arastirmasi",
    "share-of-voice", "ses-payi", "esov", "voice-of-customer", "musteri-sesi", "kano",
    "competitive-positioning", "rakip-konumlandirma", "beyaz-alan", "osint",
    "admiralty-code", "ach", "triangulation", "retail-review-mining", "yorum-analizi",
    "sahte-yorum", "kol-stance", "influencer", "cosmetovigilance", "kozmetovijilans",
    "icsr", "advers-etki", "web-radr", "pricing-perception", "trend-scan"
  ],
  "userConfig": {
    "socius_vigil_api_key": {
      "type": "string",
      "title": "Socius-Vigil MCP anahtarı",
      "description": "Social Listening worker'ının Bearer anahtarı (18 sv_* aracı). Yoksa toplama/skorlama scripts/*.py native düşüşüne iner ve her çıktı bunu G12 altında beyan eder. UYARI: bu alanı doldurmak TEK BAŞINA yetmez — .mcp.json header'ı ${SOCIUS_VIGIL_MCP_API_KEY} ortam değişkenini okur; userConfig→env fallback sözdizimi belgelenmemiştir. Değeri ayrıca ortam değişkeni olarak dışa aktarın: doppler run -p cureohub -c dev_personal -- claude",
      "required": false,
      "sensitive": true
    },
    "exa_api_key": {
      "type": "string",
      "title": "Exa anahtarı (opsiyonel)",
      "description": "sv_search/sv_fetch düşüşü + yorum keşfi. Yoksa keşif tavily/web_search'e iner; kapsama boşluğu §13'te beyan edilir.",
      "required": false,
      "sensitive": true
    },
    "tavily_api_key": {
      "type": "string",
      "title": "Tavily anahtarı (opsiyonel)",
      "description": "Geniş web tarama + extract. Yoksa kaynak keşfi yalnız Exa/web_search ile yapılır.",
      "required": false,
      "sensitive": true
    },
    "anamnesis_api_key": {
      "type": "string",
      "title": "Anamnesis anahtarı (opsiyonel)",
      "description": "Tier-2 bağlam ekonomisi substratı: >30 KB gövde ingest→bounded query. Yoksa bounded-chunk okumaya degrade edilir; arama asla bu yüzden başarısız olmaz.",
      "required": false,
      "sensitive": true
    }
  },
  "mcpServers": "./.mcp.json",
  "defaultEnabled": false
}
```

- [ ] **Adım 5: `.codex-plugin/plugin.json` yaz**

```json
{
  "name": "socius-vigil",
  "version": "1.0.0",
  "description": "Qualified market research + social listening/OSINT orchestration suite. 13 commands over the Social Listening MCP's 18 sv_* tools: collection and deterministic scoring belong to the MCP, interpretation and synthesis to the skill layer. Quality gates G1-G16 are hook-enforced (tool-call ledger, no-fabrication, clean-copy token scan). WEB-RADR invariant: adverse-event signals are detected, verified, interpreted and escalated - never filed as official pharmacovigilance cases.",
  "author": { "name": "Cureonics", "url": "https://cureonics.com" },
  "homepage": "https://cureonics.com",
  "license": "LicenseRef-Internal",
  "keywords": [
    "social-listening", "market-intelligence", "share-of-voice", "voice-of-customer",
    "competitive-positioning", "osint", "admiralty-code", "retail-review-mining",
    "kol-stance", "cosmetovigilance", "icsr", "web-radr"
  ]
}
```

- [ ] **Adım 6: `.mcp.json` (çekirdek filo) yaz**

```json
{
  "mcpServers": {
    "socius-vigil": {
      "type": "http",
      "url": "https://socius-vigil-mcp.cureonics.workers.dev/mcp",
      "headers": { "Authorization": "Bearer ${SOCIUS_VIGIL_MCP_API_KEY}" },
      "_tier": "core",
      "_role": "ÇEKİRDEK — 18 sv_* aracı: planlama (sv_build_query_library, sv_source_inventory), toplama (sv_search, sv_search_fallback, sv_fetch, sv_retail_review_scan, sv_collect_pipeline), skorlama (sv_sentiment, sv_admiralty_score, sv_ach_matrix, sv_triangulate, sv_icsr_check, sv_extract_rating, sv_extract_reviews, sv_retail_filter, sv_market_synthesis, sv_kol_stance) ve kapı denetimi (sv_quality_gate). Anahtar yoksa her araç için scripts/*.py native düşüşü devreye girer; skor kalitesi düşer, rapor durmaz — G12 altında beyan edilir. DİKKAT: sv_quality_gate rapor gövdesini kullanıcının kendi worker'ına gönderir."
    },
    "exa": {
      "type": "http",
      "url": "https://mcp.exa.ai/mcp",
      "_tier": "support",
      "_role": "DESTEK — yorum keşfi + temiz tam-içerik çıkarımı; sv_search/sv_fetch'in birincil düşüşü. Kanıt hiyerarşisinde MCP skorlamasının altındadır: buradan gelen içerik sv_admiralty_score ile notlanmadan eskale edilmez."
    },
    "tavily": {
      "type": "http",
      "url": "https://mcp.tavily.com/mcp",
      "headers": { "Authorization": "Bearer ${TAVILY_API_KEY}" },
      "_tier": "support",
      "_role": "DESTEK — geniş web tarama + extract; kaynak keşfi ve sektör kaynak matrisinin (references/12) doldurulması. Exa ile aynı kanıt basamağında."
    },
    "anamnesis": {
      "type": "http",
      "url": "https://anamnesis-mcp.cureonics.workers.dev/mcp",
      "headers": { "Authorization": "Bearer ${ANAMNESIS_MCP_API_KEY}" },
      "_tier": "substrate",
      "_role": "SUBSTRAT — kaynak değil, bağlam-ekonomisi altyapısı. >30 KB gövde (uzun forum başlığı, tam yorum korpusu, kurumsal PDF) ingest→bounded query ile ana pencereden uzak tutulur. Anahtar yoksa bounded-chunk okumaya degrade edilir."
    }
  }
}
```

- [ ] **Adım 7: `.mcp.optional.json` (sektör/sağlık genişletmesi) yaz**

```json
{
  "_comment": "OPSİYONEL genişletme — otomatik YÜKLENMEZ. Etkinleştirmek için ilgili girdiyi .mcp.json'a taşıyın veya claude.ai connector olarak bağlayın ve kendi kimliğinizi sağlayın. Bağlı değilse ne olduğu: CONNECTORS.md.",
  "mcpServers": {
    "tripadvisor": {
      "type": "http",
      "url": "https://mcp.tripadvisor.com/mcp",
      "_tier": "sector",
      "_role": "Otel/seyahat/F&B dikeyinde yorum kaynağı — G11'in bu sektördeki kanonik yüzeyi. Kullanıcı-bağlı claude.ai connector; bağlı değilse G11 'yorum yüzeyi erişilemedi' ile degrade beyan edilir."
    },
    "pubmed-epmc": {
      "type": "http",
      "url": "https://pubmed-mcp.cureonics.workers.dev/mcp",
      "headers": { "Authorization": "Bearer ${PUBMED_MCP_API_KEY}" },
      "_tier": "health",
      "_role": "AE klinik plausibility — bir yorum sinyalinin bilinen advers reaksiyon profiliyle uyumu. Bağlı değilse §10 sinyalleri klinik doğrulama olmadan, yalnız Admiralty+ACH ile raporlanır."
    },
    "consensus": {
      "type": "http",
      "url": "https://mcp.consensus.app/mcp",
      "_tier": "health",
      "_role": "İddia-kanıt taraması (bileşen etkinliği, KOL iddiası). Bağlı değilse iddia doğrulaması 'literatür kontrolü yapılmadı' olarak beyan edilir."
    },
    "clinical-trials": {
      "type": "http",
      "url": "https://clinicaltrials-mcp.cureonics.workers.dev/mcp",
      "_tier": "health",
      "_role": "Çalışma-temelli iddia doğrulaması. Bağlı değilse KOL/marka iddialarının çalışma dayanağı doğrulanmaz."
    },
    "titck": {
      "type": "http",
      "url": "https://titck.cureonics.com/mcp",
      "headers": { "Authorization": "Bearer ${TITCK_MCP_API_KEY}" },
      "_tier": "sector",
      "_role": "TR ruhsat/fiyat bağlamı — Türkiye pazarı raporlarında SKU kimliği ve ruhsat durumu. Bağlı değilse TR SKU doğrulaması manuel kalır; G10 riski artar ve beyan edilir."
    },
    "thoughtspot": {
      "type": "http",
      "url": "https://midas-mcp.cureonics.workers.dev/mcp",
      "headers": { "Authorization": "Bearer ${MIDAS_MCP_SHARED_SECRET}" },
      "_tier": "sector",
      "_role": "IQVIA MIDAS → pazar payı (SoM). ESOV hesabının TEK gerçek girdisi: ESOV = SoV − SoM. Bağlı değilse SoM 'not_provided' olur ve ESOV HESAPLANMAZ — uydurulmaz."
    }
  }
}
```

- [ ] **Adım 8: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/tests/test_structure.py -v
```

Beklenen: tüm testler PASS.

- [ ] **Adım 9: Commit**

```bash
git add plugins/socius-vigil
git commit -m "feat(socius-vigil): plugin iskeleti + kanonik v2.3.0 gövdesi (P1 tek kopya)"
```

---

### Görev 2: SKILL.md v2.3.0 → v2.4.0

**Dosyalar:**
- Değiştir: `plugins/socius-vigil/skills/socius-vigil/SKILL.md` (satır 6 başlık, §2 tablosu, §2.1, §12, §13, §14)
- Değiştir: `plugins/socius-vigil/skills/socius-vigil/skill-manifest.yaml`
- Test: `plugins/socius-vigil/tests/test_skill_body.py`

**Arayüzler:**
- Tüketir: Görev 1'in taşıdığı `skills/socius-vigil/SKILL.md`.
- Üretir: §12'de her kapı için `hook` · `sv_quality_gate` · `protokol-düzeyi` uygulama etiketi — Görev 7 ve 8 bu etiketlere dayanır.

- [ ] **Adım 1: Gövde testini yaz**

`plugins/socius-vigil/tests/test_skill_body.py`:

```python
#!/usr/bin/env python3
"""SKILL.md v2.4.0 gerçeklik denetimi. stdlib unittest, ağ yok."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = (ROOT / "skills/socius-vigil/SKILL.md").read_text(encoding="utf-8")
MANIFEST = (ROOT / "skills/socius-vigil/skill-manifest.yaml").read_text(encoding="utf-8")

TOOL_NAMES = [
    "sv_build_query_library", "sv_source_inventory", "sv_search",
    "sv_search_fallback", "sv_fetch", "sv_retail_review_scan",
    "sv_retail_filter", "sv_extract_rating", "sv_extract_reviews",
    "sv_sentiment", "sv_admiralty_score", "sv_ach_matrix", "sv_triangulate",
    "sv_market_synthesis", "sv_kol_stance", "sv_icsr_check",
    "sv_collect_pipeline", "sv_quality_gate",
]


class TestSurum(unittest.TestCase):
    def test_baslik_v240(self):
        self.assertIn("# Socius-Vigil v2.4.0", SKILL)

    def test_manifest_240(self):
        self.assertRegex(MANIFEST, r'version:\s*"2\.4\.0"')


class TestAracTablosu(unittest.TestCase):
    def test_on_sekiz_aracin_hepsi_gecer(self):
        for name in TOOL_NAMES:
            self.assertIn(name, SKILL, f"{name} SKILL.md'de yok")

    def test_uydurma_arac_adi_yok(self):
        """Metindeki her sv_* jetonu kanonik listede olmalı."""
        self.assertEqual(set(re.findall(r"\bsv_[a-z_]+\b", SKILL)) - set(TOOL_NAMES), set())

    def test_dort_yeni_aracin_native_dususu_yazili(self):
        for script in ("kol_stance.py", "market_synthesis.py",
                       "retail_filter.py", "quality_gate_check.py"):
            self.assertIn(script, SKILL, f"{script} native düşüş sütununda yok")


class TestArtikBulgularKaldirildi(unittest.TestCase):
    def test_sv_fix_blogu_yok(self):
        self.assertNotIn("SV-FIX-01b", SKILL)
        self.assertNotIn("SV-FIX-02b", SKILL)
        self.assertNotIn("Bilinen artık MCP bulguları", SKILL)

    def test_defense_in_depth_ilkesi_korundu(self):
        self.assertIn("defense-in-depth", SKILL)


class TestKapiTablosu(unittest.TestCase):
    def _gate_line(self, gate):
        return next(l for l in SKILL.splitlines() if l.startswith(f"| **{gate} "))

    def test_uygulama_sutunu_var(self):
        self.assertRegex(SKILL, r"\|\s*Kapı\s*\|\s*Kontrol\s*\|\s*Uygulama\s*\|")

    def test_hook_uygulanan_kapilar_etiketli(self):
        for gate in ("G7", "G9", "G10", "G12", "G13", "G14", "G16"):
            self.assertIn("hook", self._gate_line(gate), f"{gate} hook etiketi eksik")

    def test_g11_quality_gate_ile_uygulaniyor(self):
        self.assertIn("sv_quality_gate", self._gate_line("G11"))


class TestComposability(unittest.TestCase):
    def test_brand_market_signal_emekli_yazili(self):
        section = SKILL.split("## 13. Composability")[1].split("\n## ")[0]
        self.assertIn("Emekli", section)
        self.assertIn("brand-market-signal", section)

    def test_brand_audit_upstream_kaldi(self):
        section = SKILL.split("## 13. Composability")[1].split("\n## ")[0]
        self.assertIn("brand-audit", section.split("Downstream")[0])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/tests/test_skill_body.py -v
```

Beklenen: `test_baslik_v240`, `test_manifest_240`, dört yeni araç, kapı sütunu, SV-FIX ve composability testleri FAIL.

- [ ] **Adım 3: §2 araç tablosuna dört satır ekle**

`## 2. MCP ↔ Skill İş Bölümü` altındaki tabloya; `Skorla — çapraz onay` satırından **sonra** üç satır, `Orkestrasyon` satırından **sonra** bir satır:

```markdown
| Skorla — perakende eleme | `sv_retail_filter` | `scripts/retail_filter.py` | Off-SKU gürültüsünü ayıkla; eleme gerekçesini (precision_report) §3.5'e taşı |
| Sentez — pazar içgörüsü | `sv_market_synthesis` | `scripts/market_synthesis.py` | SoV/ESOV, Kano, huni eşlemesi → §3/§5/§7 yorumu |
| Skorla — KOL duruşu | `sv_kol_stance` | `scripts/kol_stance.py` | Profil×duruş matrisi; sponsorlu övgüyü organik tavsiyeden ayır (§8) |
| Kapı denetimi | `sv_quality_gate` | `scripts/quality_gate_check.py` | Heuristik çıktıyı **yorumla**; P2/P5 ihlallerini kendi okumanla ekle (§11.5) |
```

- [ ] **Adım 4: §2.1'deki "Bilinen artık MCP bulguları" bloğunu değiştir**

`**Bilinen artık MCP bulguları (12 Haziran 2026 …)**` paragrafını ve altındaki iki maddeyi (SV-FIX-01b, SV-FIX-02b) **sil**; yerine:

```markdown
**MCP kusur durumu (Faz-A denetimi, v0.3.1 — `test/core/sv_fixes.test.ts`):** SV-FIX-01…09 dizisinin tamamı ampirik olarak kapalıdır; çok-dilli morfoloji ve ICSR ürün-kriteri artık MCP tarafında doğru çalışır. Kalan P2 backlog'u sinyal kalitesini etkilemez (performans/telemetri kalemleri).

**Yine de defense-in-depth korunur — kusur telafisi olarak değil, ilke olarak:** skill, `ae_candidate` / `valid_icsr` bayraklarını birincil sinyal kabul eder **ve** yorum korpusunu `references/02` leksikonuyla bağımsız olarak yeniden tarar. İki bağımsız yol aynı sonucu vermiyorsa fark §13'te beyan edilir. Bu, bugünkü MCP doğruluğuna bağımlılığı ortadan kaldırır: gelecekteki bir regresyon sinyali sessizce düşüremez.
```

- [ ] **Adım 5: §12 kapı tablosuna "Uygulama" sütunu ekle**

Başlık `| Kapı | Kontrol |` → `| Kapı | Kontrol | Uygulama |`; ayraç `|---|---|` → `|---|---|---|`. Satır metinleri **değişmez**, yalnız sütun eklenir:

| Kapı | Eklenecek etiket |
|---|---|
| G1 · G2 · G3 · G4 · G5 · G6 · G15 | `protokol-düzeyi` |
| G7 | `hook (sv_ledger + stop_gates)` |
| G8 | `hook (sv_ledger hatırlatması) + protokol-düzeyi` |
| G9 · G10 · G13 · G14 | `hook (stop_gates)` |
| G11 | `sv_quality_gate` |
| G12 | `hook (sv_ledger + stop_gates)` |
| G16 | `hook (clean_copy_guard) + sv_quality_gate --profile clean` |

Tablodan hemen sonra:

```markdown
**Sütunun anlamı:** `hook` = plugin'in `hooks/` katmanı turu tamamlatarak uygular (modelin disiplinine bırakılmaz); `sv_quality_gate` = MCP aracı deterministik olarak denetler; `protokol-düzeyi` = bu skill'in okuma disiplinine bağlıdır, makineyle yakalanmaz. Bir kapının `protokol-düzeyi` olması onu opsiyonel yapmaz; yalnız yakalanmasının modele bağlı olduğunu dürüstçe söyler.
```

- [ ] **Adım 6: §13 Composability'ye emeklilik satırı ekle**

Bölümün sonuna:

```markdown
- **Emekli:** `brand-market-signal` — bu iş artık `/socius-vigil:rakip` (SoV + konumlandırma + beyaz alan) ve `/socius-vigil:pazar-raporu` (tam rapor) tarafından yapılır. `brand-ecosystem-core`'daki skill bir yönlendirme stub'ıdır; marka-özel handoff (beyaz alan → `brand-maker` naming brief'i) orada kalır.
```

- [ ] **Adım 7: §14 script kataloğunu güncelle**

`kol_stance.py`, `market_synthesis.py`, `retail_filter.py`, `quality_gate_check.py` satırlarının sonuna ekle: ` — **hem** MCP aracı (\`sv_*\`) **hem** native düşüş; MCP varken script koşturulmaz, yokken birebir aynı çıktıyı üretir.`

- [ ] **Adım 8: Başlık + manifest sürümünü yükselt**

`SKILL.md` satır 6: `# Socius-Vigil v2.3.0 — …` → `# Socius-Vigil v2.4.0 — …` (kalanı aynı).
`skill-manifest.yaml`: `version: "2.3.0"` → `"2.4.0"`; `runtime.mcp_servers` Social Listening satırında araç sayısı **18**; `build.release_name` → `socius-vigil-v2.4.0`. `verification.gates` **değişmez** (G1–G16 aynı).

- [ ] **Adım 9: Testleri koş**

```bash
python3 plugins/socius-vigil/tests/test_skill_body.py -v
python3 plugins/socius-vigil/tests/test_structure.py -v
```

Beklenen: ikisi de tamamen PASS.

- [ ] **Adım 10: Commit**

```bash
git add plugins/socius-vigil/skills/socius-vigil plugins/socius-vigil/tests/test_skill_body.py
git commit -m "feat(socius-vigil): SKILL.md v2.4.0 — 18 araç, SV-FIX artıkları kaldırıldı, kapı uygulama sütunu"
```

---

### Görev 3: `socius_doctor.py` — araç senkronu + tetikleyici ayrıklığı + SECTION_MAP

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/scripts/socius_doctor.py`
- Test: `plugins/socius-vigil/tests/test_doctor.py`

**Arayüzler:**
- Üretir: `TOOL_NAMES: list[str]` (18) — Görev 5 ve 7 hook'ları `from socius_doctor import TOOL_NAMES` ile import eder.
- Üretir: `skill_descriptions(root: Path) -> dict[str, str]` · `disjointness_report(descs: dict) -> list[tuple]`
- Üretir: CLI `--tools` · `--skills` · `--sections` · `--live`; hepsi 0 (temiz) veya 1 (bulgu) döner.

- [ ] **Adım 1: Doctor testini yaz**

`plugins/socius-vigil/tests/test_doctor.py`:

```python
#!/usr/bin/env python3
"""socius_doctor statik denetimleri. Ağ yok — --live test edilmez."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCTOR = ROOT / "scripts/socius_doctor.py"

sys.path.insert(0, str(ROOT / "scripts"))
from socius_doctor import TOOL_NAMES, disjointness_report, skill_descriptions  # noqa: E402


def run(*args):
    p = subprocess.run([sys.executable, str(DOCTOR), *args],
                       capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout


class TestAracListesi(unittest.TestCase):
    def test_on_sekiz_benzersiz_arac(self):
        self.assertEqual(len(TOOL_NAMES), 18)
        self.assertEqual(len(set(TOOL_NAMES)), 18)

    def test_chatgpt_aliaslari_listede_degil(self):
        self.assertNotIn("search", TOOL_NAMES)
        self.assertNotIn("fetch", TOOL_NAMES)

    def test_mcp_json_rolu_kanonik_listeyle_tutarli(self):
        rc, out = run("--tools")
        self.assertEqual(rc, 0, out)
        self.assertIn("TUTARLI", out)


class TestTetikleyiciAyrikligi(unittest.TestCase):
    def test_on_uc_skill_bulunur(self):
        self.assertEqual(len(skill_descriptions(ROOT)), 13)

    def test_beklenmeyen_cakisma_yok(self):
        rc, out = run("--skills")
        self.assertEqual(rc, 0, out)
        self.assertIn("ÇAKIŞMA YOK", out)

    def test_cakisma_raporu_yapay_veride_yakalar(self):
        """Mutasyon denetimi: rapor gerçekten ayrım yapıyor mu, yoksa hep boş mu?"""
        fake = {
            "voc": "müşteri sesi kano sürücü bariyer satın alma yolculuğu yorum",
            "fiyat": "müşteri sesi kano sürücü bariyer satın alma yolculuğu yorum",
        }
        self.assertTrue(disjointness_report(fake))

    def test_ayrik_aciklamalar_cakisma_uretmez(self):
        fake = {"voc": "müşteri sesi kano sürücü bariyer",
                "kol": "eczacı dermatolog duruş sponsorlu açıklama"}
        self.assertEqual(disjointness_report(fake), [])


class TestSectionMap(unittest.TestCase):
    def test_bolum_atiflari_tutarli(self):
        rc, out = run("--sections")
        self.assertEqual(rc, 0, out)
        self.assertIn("TUTARLI", out)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/tests/test_doctor.py -v
```

Beklenen: `ModuleNotFoundError: No module named 'socius_doctor'`.

- [ ] **Adım 3: `socius_doctor.py` yaz**

```python
#!/usr/bin/env python3
"""socius-vigil doctor — araç senkronu, skill ayrıklığı, SECTION_MAP, canlı prob.

    python3 scripts/socius_doctor.py            # üçü birden (ağ yok)
    python3 scripts/socius_doctor.py --tools    # araç adı senkronu
    python3 scripts/socius_doctor.py --skills   # tetikleyici ayrıklığı
    python3 scripts/socius_doctor.py --sections # SECTION_MAP tutarlılığı
    python3 scripts/socius_doctor.py --live     # canlı tools/list (anahtar gerekir)
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# TEK DOĞRULUK KAYNAĞI — hook'lar ve testler bunu import eder.
TOOL_NAMES = [
    "sv_build_query_library", "sv_source_inventory", "sv_search",
    "sv_search_fallback", "sv_fetch", "sv_retail_review_scan",
    "sv_retail_filter", "sv_extract_rating", "sv_extract_reviews",
    "sv_sentiment", "sv_admiralty_score", "sv_ach_matrix", "sv_triangulate",
    "sv_market_synthesis", "sv_kol_stance", "sv_icsr_check",
    "sv_collect_pipeline", "sv_quality_gate",
]

# ChatGPT-uyumluluk alias'ları: sunucu yayınlar, 18'e dahil DEĞİL.
ALIASES = {"search", "fetch"}

FLAGSHIP = "socius-vigil"
STOPWORDS = {
    "ve", "veya", "için", "ile", "bir", "bu", "the", "and", "for", "with",
    "kullanın", "use", "sorularında", "analizi", "raporu", "pazar", "socius",
    "vigil", "mcp", "araştırması", "modu", "when", "doubt",
}


def skill_descriptions(root):
    """skills/*/SKILL.md frontmatter description'larını topla."""
    out = {}
    for d in sorted((root / "skills").iterdir()):
        f = d / "SKILL.md"
        if not d.is_dir() or not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^description:\s*"?(.*?)"?\s*$', text, re.M | re.S)
        out[d.name] = (m.group(1) if m else "")[:2000]
    return out


def _terms(desc):
    toks = re.findall(r"[\wçğıöşüÇĞİÖŞÜ]{4,}", desc.lower())
    return {t for t in toks if t not in STOPWORDS}


def disjointness_report(descs):
    """Mod skill'leri arasında ≥6 ortak dar terim = çakışma adayı. Flagship muaf."""
    clashes = []
    names = [n for n in descs if n != FLAGSHIP]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            shared = _terms(descs[a]) & _terms(descs[b])
            if len(shared) >= 6:
                clashes.append((a, b, sorted(shared)[:8]))
    return clashes


def check_tools():
    role = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["socius-vigil"]["_role"]
    print(f"Kanonik araç sayısı: {len(TOOL_NAMES)}")
    missing = [t for t in TOOL_NAMES if t not in role]
    if missing:
        print("UYARI — _role metninde geçmeyen araçlar:", ", ".join(missing))
    ghosts = set(re.findall(r"\bsv_[a-z_]+\b", role)) - set(TOOL_NAMES)
    if ghosts:
        print("İHLAL — kanonik olmayan araç adı:", ", ".join(sorted(ghosts)))
        return 1
    print("Araç adı senkronu: TUTARLI (18)")
    return 0


def check_skills():
    descs = skill_descriptions(ROOT)
    print(f"Skill sayısı: {len(descs)} (beklenen 13)")
    clashes = disjointness_report(descs)
    if clashes:
        for a, b, shared in clashes:
            print(f"ÇAKIŞMA — {a} ↔ {b}: {', '.join(shared)}")
        return 1
    print("Tetikleyici ayrıklığı: ÇAKIŞMA YOK")
    return 0


def check_sections():
    """Mod skill'lerinin §N atıfları references/13-section-map.md ile uyumlu mu."""
    smap = (ROOT / "skills/socius-vigil/references/13-section-map.md").read_text(encoding="utf-8")
    known = set(re.findall(r"§\s*(\d+(?:\.\d+)?)", smap)) | {str(i) for i in range(0, 15)}
    bad = []
    for d in (ROOT / "skills").iterdir():
        if not d.is_dir() or d.name == FLAGSHIP or not (d / "SKILL.md").exists():
            continue
        for ref in re.findall(r"§\s*(\d+(?:\.\d+)?)", (d / "SKILL.md").read_text(encoding="utf-8")):
            if ref not in known:
                bad.append((d.name, ref))
    if bad:
        for name, ref in bad:
            print(f"TUTARSIZ — {name}: §{ref} section-map'te yok")
        return 1
    print("SECTION_MAP: TUTARLI")
    return 0


def check_live():
    key = os.environ.get("SOCIUS_VIGIL_MCP_API_KEY", "").strip()
    if not key:
        print("--live atlandı: SOCIUS_VIGIL_MCP_API_KEY yok (degrade, hata değil)")
        return 0
    url = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["socius-vigil"]["url"]
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {key}",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        print(f"CANLI PROB BAŞARISIZ: {exc} — degrade beyan edin, uydurmayın")
        return 1
    live = set(re.findall(r'"name"\s*:\s*"([a-z_]+)"', raw)) - ALIASES
    extra, missing = live - set(TOOL_NAMES), set(TOOL_NAMES) - live
    if extra or missing:
        print(f"AYRIŞMA — fazla: {sorted(extra)} · eksik: {sorted(missing)}")
        return 1
    print(f"Canlı yüzey: {len(live)} araç, kanonik listeyle BİREBİR")
    return 0


def main():
    ap = argparse.ArgumentParser()
    for flag in ("tools", "skills", "sections", "live"):
        ap.add_argument(f"--{flag}", action="store_true")
    a = ap.parse_args()
    if not any((a.tools, a.skills, a.sections, a.live)):
        return check_tools() | check_skills() | check_sections()
    rc = 0
    if a.tools:
        rc |= check_tools()
    if a.skills:
        rc |= check_skills()
    if a.sections:
        rc |= check_sections()
    if a.live:
        rc |= check_live()
    return rc


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Adım 4: Testi koş — skill'ler henüz yok, iki testi Görev 9'a ertele**

```bash
python3 plugins/socius-vigil/tests/test_doctor.py -v
```

Beklenen: `test_on_uc_skill_bulunur` ve `test_beklenmeyen_cakisma_yok` FAIL (yalnız flagship var). İkisine `@unittest.skip("Görev 9'da etkinleşir")` ekle — **`test_cakisma_raporu_yapay_veride_yakalar` ve `test_ayrik_aciklamalar_cakisma_uretmez` skip EDİLMEZ**; ayrıklık mantığının doğruluğu yapay veriyle şimdi kanıtlanır.

- [ ] **Adım 5: Testi tekrar koş**

```bash
python3 plugins/socius-vigil/tests/test_doctor.py -v
```

Beklenen: iki skip, kalan hepsi PASS.

- [ ] **Adım 6: Commit**

```bash
git add plugins/socius-vigil/scripts/socius_doctor.py plugins/socius-vigil/tests/test_doctor.py
git commit -m "feat(socius-vigil): socius_doctor — 18 araç tek kaynağı + ayrıklık/section denetimi"
```

---

### Görev 4: Hook yardımcıları + `hooks.json` + `session_start.py`

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/hooks/hooks.json`
- Oluştur: `plugins/socius-vigil/hooks/scripts/_signals.py`
- Oluştur: `plugins/socius-vigil/hooks/scripts/_turn_tools.py`
- Oluştur: `plugins/socius-vigil/hooks/scripts/session_start.py`
- Test: `plugins/socius-vigil/hooks/tests/test_signals.py`

**Arayüzler:**
- Üretir (`_signals.py`): `PLUGIN_ROOT: Path` · `read_payload() -> dict` · `emit_context(text)` · `emit_block(reason)` · `env_present(name) -> bool` · `transcript_text(payload, limit=200_000) -> str` · `report_signature(text) -> bool` · `meta_turn(text) -> bool`
- Üretir (`_turn_tools.py`): `tools_since_last_prompt(payload) -> list[str]` · `sv_tool_invoked(payload) -> bool` · `transcript_available(payload) -> bool` · `ledger_path(payload) -> Path` · `read_ledger(payload) -> list[dict]` · `append_ledger(payload, record: dict)`
- Görev 5–8 hook'ları bu iki modülü `sys.path.insert(0, str(Path(__file__).resolve().parent))` sonrası import eder.

- [ ] **Adım 1: Sinyal testini yaz (mutasyon denetimli)**

`plugins/socius-vigil/hooks/tests/test_signals.py`:

```python
#!/usr/bin/env python3
"""Rapor imzası + meta-tur baskılaması (P3). stdlib unittest, ağ yok."""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
from _signals import meta_turn, report_signature  # noqa: E402

GERCEK_RAPOR = """# Pazar Zekâsı Raporu — Atoderm Crème

## 0. Yönetici Özeti (BLUF)
Ürün Fransa pazarında güçlü organik savunuculuk taşıyor.

## 3. Talep ve Ses Payı
Ses payı %18 [1].

## 5. Müşteri Sesi — Satın Alma Sürücüleri ve Bariyerleri
Nemlendirme sürücü, koku bariyer [2].
"""

META_TUR = """Plugin'in hooks/ dizinini inceledim. clean_copy_guard.py ve stop_gates.py
script'lerini yazdım; SKILL.md'deki pazar-raporu ve hizli-tarama modlarının imzalarını
karşılaştırdım.

# Pazar Zekâsı Raporu — örnek başlık (test fixture'ı)

## 1. Bir
## 2. İki
## 3. Üç
"""


class TestRaporImzasi(unittest.TestCase):
    def test_gercek_rapor_yakalanir(self):
        self.assertTrue(report_signature(GERCEK_RAPOR))

    def test_baslik_tek_basina_yetmez(self):
        self.assertFalse(report_signature("# Pazar Zekâsı Raporu — X\n\nKısa not."))

    def test_numarasiz_basliklar_yetmez(self):
        self.assertFalse(report_signature(
            "# Pazar Zekâsı Raporu\n\n## Giriş\n## Gelişme\n## Sonuç"))

    def test_bos_metin(self):
        self.assertFalse(report_signature(""))


class TestMetaTurBaskilamasi(unittest.TestCase):
    def test_plugin_ici_dosya_adi_baskilar(self):
        self.assertTrue(meta_turn(META_TUR))

    def test_gercek_rapor_baskilanmaz(self):
        self.assertFalse(meta_turn(GERCEK_RAPOR))

    def test_kaynak_kunyesi_baskilamayi_ezer(self):
        """Rapor SKILL.md'den söz etse bile kaynak künyesi taşıyorsa GERÇEKtir."""
        text = META_TUR + "\n[1] Doctissimo forum, erişim 2026-08-01, https://x.example\n"
        self.assertFalse(meta_turn(text))

    def test_iki_mod_adi_kaynaksiz_baskilar(self):
        self.assertTrue(meta_turn("pazar-raporu ve vijilans modlarını karşılaştırdım."))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_signals.py -v
```

Beklenen: `ModuleNotFoundError: No module named '_signals'`.

- [ ] **Adım 3: `_signals.py` yaz**

```python
"""socius-vigil hook ortak yardımcıları — stdlib yalnız, fail-open."""
import json
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent

# §7.1 güçlü imza: kanonik rapor başlığı + ≥3 numaralı bölüm
REPORT_TITLE_RX = re.compile(r"^#\s*Pazar Zekâsı Raporu", re.M)
NUMBERED_SECTION_RX = re.compile(r"^##\s*\d+(?:\.\d+)?\.", re.M)

# §7.1 baskılayıcı: plugin-iç dosya/dizin adı
INTERNAL_RX = re.compile(
    r"(hooks/|SKILL\.md|skill-manifest\.yaml|\.tool\.ts|socius_doctor|hooks\.json|"
    r"clean_copy_guard|stop_gates|sv_ledger|retrieve_dont_dump)")

MODE_NAMES = ("pazar-raporu", "hizli-tarama", "voc", "rakip", "fiyat", "trend",
              "kol", "perakende", "vijilans", "yayin", "durum", "start")

# Kaynak künyesi: numaralı atıf + URL veya erişim tarihi
SOURCE_RX = re.compile(r"\[\d+\]\s*.{0,120}?(https?://|erişim\s*\d{4}-\d{2}-\d{2})", re.S)


def read_payload():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def emit_context(text):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": text}}, ensure_ascii=False))


def emit_block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def env_present(name):
    return bool(name and os.environ.get(name, "").strip())


def transcript_text(payload, limit=200_000):
    path = payload.get("transcript_path")
    if not path:
        return ""
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    out = []
    for line in reversed(lines[-400:]):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        msg = rec.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    out.append(block.get("text", ""))
        elif isinstance(content, str):
            out.append(content)
        if sum(len(x) for x in out) > limit:
            break
    return "\n".join(reversed(out))


def report_signature(text):
    """Güçlü imza: kanonik başlık VE ≥3 numaralı bölüm başlığı."""
    if not text:
        return False
    return bool(REPORT_TITLE_RX.search(text)) and len(NUMBERED_SECTION_RX.findall(text)) >= 3


def meta_turn(text):
    """P3 — plugin'in KENDİ kodu üzerinde çalışılan tur mu?

    Baskılar: plugin-iç dosya adı VEYA ≥2 mod adı geçiyor VE hiç kaynak künyesi yok.
    Kaynak künyesi varsa tur gerçektir — metin plugin dosyalarından söz etse bile.
    """
    if not text:
        return False
    if SOURCE_RX.search(text):
        return False
    return bool(INTERNAL_RX.search(text)) or sum(1 for m in MODE_NAMES if m in text) >= 2
```

- [ ] **Adım 4: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_signals.py -v
```

Beklenen: 8 test PASS.

- [ ] **Adım 5: `_turn_tools.py` yaz**

```python
"""Tur-yerel araç izleme + MCP çağrı defteri I/O. stdlib yalnız, fail-open."""
import json
import os
import re
import tempfile
from pathlib import Path

# Hem yerel stdio (mcp__socius-vigil__sv_x) hem claude.ai connector
# (mcp__claude_ai_Social_Listening__sv_x) adlandırmasını yakalar.
SV_TOOL_RX = re.compile(r"mcp__.*__(sv_[a-z_]+)$")


def _records(path, tail=600):
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    out = []
    for line in lines[-tail:]:
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _is_user_prompt(rec):
    msg = rec.get("message") or {}
    return msg.get("role") == "user" and not rec.get("isMeta")


def _tool_uses(rec):
    content = (rec.get("message") or {}).get("content")
    if not isinstance(content, list):
        return []
    return [b.get("name", "") for b in content
            if isinstance(b, dict) and b.get("type") == "tool_use"]


def tools_since_last_prompt(payload):
    path = payload.get("transcript_path")
    if not path:
        return []
    recs = _records(path)
    start = 0
    for i, rec in enumerate(recs):
        if _is_user_prompt(rec):
            start = i
    names = []
    for rec in recs[start:]:
        names.extend(_tool_uses(rec))
    return [n for n in names if n]


def sv_tool_invoked(payload):
    return any(SV_TOOL_RX.search(n) for n in tools_since_last_prompt(payload))


def transcript_available(payload):
    path = payload.get("transcript_path")
    return bool(path and os.path.exists(path) and _records(path))


def ledger_path(payload):
    """Tur-yerel defter — oturum kimliğine anahtarlı, geçici dizinde."""
    sid = str(payload.get("session_id") or "anon")[:64]
    return Path(tempfile.gettempdir()) / f"socius_ledger_{re.sub(r'[^A-Za-z0-9_.-]', '_', sid)}.jsonl"


def read_ledger(payload):
    p = ledger_path(payload)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def append_ledger(payload, record):
    try:
        with ledger_path(payload).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass
```

- [ ] **Adım 6: `session_start.py` yaz**

```python
#!/usr/bin/env python3
"""SessionStart — connector preflight + doktrin enjeksiyonu. Fail-open."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _signals import emit_context, env_present, read_payload  # noqa: E402

KEYS = [
    ("SOCIUS_VIGIL_MCP_API_KEY", "socius-vigil (ÇEKİRDEK, 18 sv_* aracı)",
     "toplama/skorlama scripts/*.py native düşüşüne iner — rapor durmaz, G12 altında beyan edilir"),
    ("TAVILY_API_KEY", "tavily (destek)", "geniş web tarama kapalı; keşif Exa/web_search ile"),
    ("ANAMNESIS_MCP_API_KEY", "anamnesis (substrat)",
     ">30 KB gövde için bounded-chunk okumaya degrade"),
]

DOKTRIN = """[socius-vigil] Nitelikli pazar araştırması + sosyal dinleme protokolü aktif.
SINIR: MCP TOPLAR ve SKORLAR (18 sv_* aracı), SKILL YORUMLAR. Bir sv_sentiment yüzdesi,
bir sv_admiralty_score kodu, bir sv_ach_matrix kazananı HAM GİRDİdir — sonuç değil; ne
anlama geldiği, satışta neyi tetiklediği, hangi rakip aksiyonunu ima ettiği yazılmadan
rapor tamamlanmış sayılmaz.
WEB-RADR DEĞİŞMEZİ (I3): AE/ICSR çıktıları HER ZAMAN requires_human_review:true taşır.
Sinyal tespit-doğrula-yorumla-eskale edilir; resmî farmakovijilansta DOSYALANMAZ.
Eşikler: >=C3 / >=B2; MDR <=15 gün; kozmetovijilans SUE <=20 takvim günü.
NO-FABRICATION (G9): her kantitatif puan ya "alındı (kaynaklı)" ya "JS/API-kapılı —
alınamadı"dır. Uydurulmuş rakam, uydurulmuş araç adı (18 kanonik ad dışı sv_*) ve
uydurulmuş kaynak yasaktır. Boş sonuç yokluk kanıtı DEĞİLDİR.
İKİ ARTEFAKT (§11.5): teslim = Okuyucu Raporu (teknik jargon SIFIR) + Teknik Süreç Eki
(MCP defteri, kapı sonuçları, ham matrisler). İkisi KARIŞTIRILMAZ.
BAĞLAM EKONOMİSİ: ham gövde >6 KB → pazar-tarama-distilleri alt-ajanı; >30 KB → anamnesis
ingest→bounded query. Ham JSON ana pencereye dökülmez.
MOD SEÇİMİ: ürün/marka → /socius-vigil:pazar-raporu · AE/güvenlik → :vijilans · rakip
kıyas → :rakip · fiyat → :fiyat · e-ticaret yorumu → :perakende · KOL/uzman görüşü → :kol
· hızlı enstantane → :hizli-tarama · teslim öncesi → :yayin · tanı → :durum"""


def main():
    read_payload()  # akışı değiştirmez; stdin'i tüketmek için okunur
    eksik = [f"  · {label}: anahtar YOK → {degrade}"
             for env, label, degrade in KEYS if not env_present(env)]
    preflight = ""
    if eksik:
        preflight = ("\nPREFLIGHT — eksik anahtarlar (oturum DURMAZ, degrade beyan edilir):\n"
                     + "\n".join(eksik)
                     + "\n  Çözüm: oturumu `doppler run -p cureohub -c dev_personal -- claude` ile başlatın."
                     + "\n  Her eksik katman çıktıda `skipped: anahtar yok` olarak BEYAN EDİLİR (P4).")
    emit_context(DOKTRIN + preflight)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
```

- [ ] **Adım 7: `hooks.json` yaz**

```json
{
  "description": "socius-vigil runtime enforcement — G7/G9/G10/G12/G13/G14/G16 kapılarını düz yazıdan uygulanan davranışa çevirir: (1) SessionStart connector-preflight + MCP-toplar/skill-yorumlar sınırı, WEB-RADR I3 değişmezi, no-fabrication, iki-artefakt doktrini, bağlam ekonomisi ve mod seçim ağacı enjeksiyonu; (2) PostToolUse sv_ledger, her sv_* çağrısından tool/provider/degraded/gaps/enriched_by/timestamp çekip tur-yerel deftere yazar ve AE sinyalinde I3 + eskalasyon eşiklerini hatırlatır; (3) PostToolUse retrieve-don't-dump, >6KB gövdede pazar-tarama-distilleri'ne, >30KB'de anamnesis'e yönlendirir (advisory); (4) Stop stop_gates, substantif rapor imzası varsa defteri denetler (G12 uydurma araç adı, G9 beyan, G13 minimum eksen, G14 RACI, G10 SKU) ve eksikse turu TAMAMLATIR; (5) Stop clean_copy_guard, Okuyucu Raporu'nda yasaklı teknik jeton taraması yapar (G16). Hiçbir hook MCP çağrısını bloklamaz; tümü fail-open ve meta-tur baskılamalıdır (P3).",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/env python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/session_start.py\"",
            "timeout": 15,
            "statusMessage": "socius-vigil: connector preflight + protokol doktrini"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__.*__sv_.*",
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/env python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/sv_ledger.py\"",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "/usr/bin/env python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/retrieve_dont_dump.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/env python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/stop_gates.py\"",
            "timeout": 15
          },
          {
            "type": "command",
            "command": "/usr/bin/env python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/clean_copy_guard.py\"",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

- [ ] **Adım 8: Fail-open davranışını elle doğrula**

```bash
echo '{}' | python3 plugins/socius-vigil/hooks/scripts/session_start.py | head -3
echo 'BOZUK JSON' | python3 plugins/socius-vigil/hooks/scripts/session_start.py; echo "çıkış kodu=$?"
python3 -c "import json;json.load(open('plugins/socius-vigil/hooks/hooks.json'));print('hooks.json geçerli')"
```

Beklenen: ilki `hookSpecificOutput` JSON'u basar; ikincisi sessizce çıkar, `çıkış kodu=0`; üçüncüsü `hooks.json geçerli`.

- [ ] **Adım 9: Commit**

```bash
git add plugins/socius-vigil/hooks
git commit -m "feat(socius-vigil): hook yardımcıları + hooks.json + SessionStart doktrini"
```

---

### Görev 5: `sv_ledger.py` — MCP çağrı defteri (G7/G12'yi uygulanabilir kılan parça)

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/hooks/scripts/sv_ledger.py`
- Değiştir: `plugins/socius-vigil/skills/socius-vigil/schemas/mcp_tool_ledger.schema.json` (enum 14 → 18)
- Test: `plugins/socius-vigil/hooks/tests/test_ledger.py`

**Arayüzler:**
- Tüketir: `_turn_tools.append_ledger(payload, record)`, `_signals.read_payload()`, `socius_doctor.TOOL_NAMES`.
- Üretir: her `sv_*` çağrısı için `{tool, provider, degraded, gaps, enriched_by, enrichment_note, access_gated, provenance:{timestamp,url?}}` kaydı — Görev 7 `stop_gates.py` bu defteri okur.

**Ölçülmüş sürüklenme (bu görev düzeltir):** `schemas/mcp_tool_ledger.schema.json`'un `tool` enum'u **14 sv_\* adı** taşıyor; `sv_retail_filter`, `sv_market_synthesis`, `sv_kol_stance`, `sv_quality_gate` eksik. Şema v0.4.0 yüzeyinin gerisinde kalmış — enum 18'e çıkarılır (native düşüş adları `web_search`/`web_fetch`/`Exa`/`Tripadvisor` korunur).

- [ ] **Adım 1: Defter testini yaz**

`plugins/socius-vigil/hooks/tests/test_ledger.py`:

```python
#!/usr/bin/env python3
"""sv_ledger — kayıt çıkarımı, AE hatırlatması, fail-open. Ağ yok."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent
SCRIPTS = HOOKS / "scripts"
ROOT = HOOKS.parent
sys.path.insert(0, str(SCRIPTS))
from _turn_tools import ledger_path, read_ledger  # noqa: E402


def run(payload):
    p = subprocess.run([sys.executable, str(SCRIPTS / "sv_ledger.py")],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout


def payload(tool, response, sid="test-ledger"):
    return {
        "session_id": sid,
        "tool_name": f"mcp__socius-vigil__{tool}",
        "tool_response": {"content": [{"type": "text", "text": json.dumps(response, ensure_ascii=False)}]},
    }


class TestKayit(unittest.TestCase):
    def setUp(self):
        p = ledger_path({"session_id": "test-ledger"})
        if p.exists():
            p.unlink()

    def test_saglayici_ve_degrade_yazilir(self):
        run(payload("sv_search", {"provider": "brave", "degraded": True, "gaps": ["searxng down"]}))
        rec = read_ledger({"session_id": "test-ledger"})[-1]
        self.assertEqual(rec["tool"], "sv_search")
        self.assertEqual(rec["provider"], "brave")
        self.assertTrue(rec["degraded"])
        self.assertEqual(rec["gaps"], ["searxng down"])
        self.assertIn("timestamp", rec["provenance"])

    def test_saglayici_yoksa_unknown_yazilir_kayit_atlanmaz(self):
        run(payload("sv_sentiment", {"net_sentiment": -0.2}))
        rec = read_ledger({"session_id": "test-ledger"})[-1]
        self.assertEqual(rec["provider"], "unknown")

    def test_zenginlestirme_alanlari_tasinir(self):
        run(payload("sv_search", {"provider": "searxng", "enriched_by": ["perplexity"],
                                  "enrichment_note": "tavily 432 quota"}))
        rec = read_ledger({"session_id": "test-ledger"})[-1]
        self.assertEqual(rec["enriched_by"], "perplexity")
        self.assertIn("quota", rec["enrichment_note"])


class TestAeHatirlatmasi(unittest.TestCase):
    def test_ae_adayi_i3_hatirlatir(self):
        rc, out = run(payload("sv_extract_reviews", {"provider": "exa", "reviews": [
            {"ae_candidate": True, "text": "cilt kızardı"}]}))
        self.assertEqual(rc, 0)
        self.assertIn("requires_human_review", out)
        self.assertIn("15 gün", out)

    def test_ae_yoksa_sessiz(self):
        rc, out = run(payload("sv_sentiment", {"provider": "searxng", "net_sentiment": 0.4}))
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "")


class TestFailOpen(unittest.TestCase):
    def test_bozuk_stdin_cikis_kodu_sifir(self):
        p = subprocess.run([sys.executable, str(SCRIPTS / "sv_ledger.py")],
                           input="BOZUK", capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0)

    def test_bilinmeyen_arac_defter_kirletmez(self):
        run({"session_id": "test-ledger", "tool_name": "Bash", "tool_response": {}})
        recs = [r for r in read_ledger({"session_id": "test-ledger"}) if r["tool"] == "Bash"]
        self.assertEqual(recs, [])


class TestSema(unittest.TestCase):
    def test_enum_on_sekiz_sv_araci_tasir(self):
        schema = json.loads((ROOT / "skills/socius-vigil/schemas/mcp_tool_ledger.schema.json")
                            .read_text(encoding="utf-8"))
        enum = schema["properties"]["tool"]["enum"]
        sv = [t for t in enum if t.startswith("sv_")]
        self.assertEqual(len(sv), 18, f"eksik: {sv}")
        for yeni in ("sv_retail_filter", "sv_market_synthesis", "sv_kol_stance", "sv_quality_gate"):
            self.assertIn(yeni, enum)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_ledger.py -v
```

Beklenen: script yok → hepsi FAIL; `TestSema` de FAIL (enum 14).

- [ ] **Adım 3: `sv_ledger.py` yaz**

```python
#!/usr/bin/env python3
"""PostToolUse — her sv_* çağrısını tur-yerel deftere yaz (G7/G12). Fail-open."""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from _signals import read_payload  # noqa: E402
from _turn_tools import append_ledger  # noqa: E402
from socius_doctor import TOOL_NAMES  # noqa: E402

AE_RX = re.compile(r'"(ae_candidate|valid_icsr|is_ae_candidate)"\s*:\s*true', re.I)

I3_UYARI = """[socius-vigil · I3 · WEB-RADR] Bu çağrı AE/ICSR sinyali taşıyor.
DEĞİŞMEZ: her satır requires_human_review:true ile raporlanır; sinyal tespit-doğrula-
yorumla-eskale edilir, resmî farmakovijilansta DOSYALANMAZ. Nedensellik iddia edilmez.
ESKALASYON EŞİKLERİ: Admiralty >=C3 veya >=B2 → eskalasyon triyajı (references/05);
MDR bildirimi <=15 gün; kozmetovijilans SUE <=20 takvim günü.
Aday sayısı yüksekse (>15) vijilans-triyaj alt-ajanına devret — ana pencereye dökme."""


def _response_text(payload):
    resp = payload.get("tool_response")
    if isinstance(resp, str):
        return resp
    if isinstance(resp, dict):
        content = resp.get("content")
        if isinstance(content, list):
            return "\n".join(b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text")
        return json.dumps(resp, ensure_ascii=False)
    return ""


def _short_tool(payload):
    """mcp__<server>__sv_x → sv_x; kanonik listede yoksa None."""
    m = re.search(r"__(sv_[a-z_]+)$", payload.get("tool_name", "") or "")
    name = m.group(1) if m else None
    return name if name in TOOL_NAMES else None


def _first(obj, *keys):
    for k in keys:
        if isinstance(obj, dict) and obj.get(k) not in (None, "", []):
            return obj[k]
    return None


def main():
    payload = read_payload()
    tool = _short_tool(payload)
    if not tool:
        return  # sv_* değil — defteri kirletme

    text = _response_text(payload)
    try:
        body = json.loads(text)
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}

    enriched = _first(body, "enriched_by")
    if isinstance(enriched, list):
        enriched = ", ".join(str(x) for x in enriched) or None

    record = {
        "tool": tool,
        "provider": str(_first(body, "provider", "source") or "unknown"),
        "degraded": bool(body.get("degraded", False)),
        "gaps": [str(g) for g in (body.get("gaps") or [])],
        "enriched_by": enriched,
        "enrichment_note": _first(body, "enrichment_note"),
        "access_gated": bool(body.get("access_gated", False)),
        "provenance": {"timestamp": datetime.now(timezone.utc).isoformat()},
    }
    url = _first(body, "url")
    if isinstance(url, str):
        record["provenance"]["url"] = url

    append_ledger(payload, record)

    if AE_RX.search(text):
        print(I3_UYARI)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
```

- [ ] **Adım 4: Şema enum'unu 18'e çıkar**

`skills/socius-vigil/schemas/mcp_tool_ledger.schema.json` → `properties.tool.enum` listesine dört ad ekle (mevcut 14 sv_* + native düşüş adları korunur):

```json
"sv_retail_filter",
"sv_market_synthesis",
"sv_kol_stance",
"sv_quality_gate",
```

Aynı dosyadaki `properties.tool.description` metnindeki **"14 sv_*"** ifadesini **"18 sv_*"** yap.

- [ ] **Adım 5: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_ledger.py -v
```

Beklenen: hepsi PASS.

- [ ] **Adım 6: Commit**

```bash
git add plugins/socius-vigil/hooks/scripts/sv_ledger.py \
        plugins/socius-vigil/hooks/tests/test_ledger.py \
        plugins/socius-vigil/skills/socius-vigil/schemas/mcp_tool_ledger.schema.json
git commit -m "feat(socius-vigil): sv_ledger hook + defter şeması 14→18 araç"
```

---

### Görev 6: `retrieve_dont_dump.py` — bağlam ekonomisi yönlendirmesi

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/hooks/scripts/retrieve_dont_dump.py`
- Oluştur: `plugins/socius-vigil/shared/context-economy-contract.md`
- Oluştur: `plugins/socius-vigil/shared/coverage-manifest.md`
- Test: `plugins/socius-vigil/hooks/tests/test_retrieve.py`

**Arayüzler:**
- Tüketir: `_signals.read_payload()`, `_signals.env_present()`.
- Üretir: Tier eşikleri — **>6 KB** → `pazar-tarama-distilleri` (Görev 10), **>30 KB** → `anamnesis` ingest. Görev 9'daki mod skill'leri bu eşiklere `shared/context-economy-contract.md` üzerinden atıf verir.

- [ ] **Adım 1: Testi yaz**

`plugins/socius-vigil/hooks/tests/test_retrieve.py`:

```python
#!/usr/bin/env python3
"""retrieve_dont_dump — eşikler + advisory (asla bloklamaz). Ağ yok."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(payload, env=None):
    e = dict(os.environ)
    e.update(env or {})
    p = subprocess.run([sys.executable, str(SCRIPTS / "retrieve_dont_dump.py")],
                       input=json.dumps(payload), capture_output=True, text=True,
                       timeout=30, env=e)
    return p.returncode, p.stdout


def payload(size, tool="sv_search"):
    return {
        "tool_name": f"mcp__socius-vigil__{tool}",
        "tool_response": {"content": [{"type": "text", "text": "x" * size}]},
    }


class TestEsikler(unittest.TestCase):
    def test_kucuk_govde_sessiz(self):
        rc, out = run(payload(2_000))
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "")

    def test_orta_govde_distiller_onerir(self):
        rc, out = run(payload(8_000))
        self.assertIn("pazar-tarama-distilleri", out)
        self.assertNotIn("anamnesis", out)

    def test_buyuk_govde_anamnesis_onerir(self):
        rc, out = run(payload(40_000), env={"ANAMNESIS_MCP_API_KEY": "x"})
        self.assertIn("anamnesis", out)

    def test_anahtarsiz_anamnesis_bounded_chunka_duser(self):
        rc, out = run(payload(40_000), env={"ANAMNESIS_MCP_API_KEY": ""})
        self.assertIn("bounded-chunk", out)


class TestAdvisory(unittest.TestCase):
    def test_asla_block_dondurmez(self):
        for size in (2_000, 8_000, 40_000):
            rc, out = run(payload(size))
            self.assertEqual(rc, 0)
            self.assertNotIn('"decision"', out)

    def test_sv_disi_arac_yok_sayilir(self):
        rc, out = run({"tool_name": "Bash",
                       "tool_response": {"content": [{"type": "text", "text": "x" * 40_000}]}})
        self.assertEqual(out.strip(), "")

    def test_bozuk_stdin_fail_open(self):
        p = subprocess.run([sys.executable, str(SCRIPTS / "retrieve_dont_dump.py")],
                           input="BOZUK", capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_retrieve.py -v
```

Beklenen: script yok → hepsi FAIL.

- [ ] **Adım 3: `retrieve_dont_dump.py` yaz**

```python
#!/usr/bin/env python3
"""PostToolUse — büyük gövdeyi ana pencereden uzak tut. Advisory, asla bloklamaz."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _signals import env_present, read_payload  # noqa: E402

TIER1 = 6 * 1024
TIER2 = 30 * 1024


def _response_text(payload):
    resp = payload.get("tool_response")
    if isinstance(resp, str):
        return resp
    if isinstance(resp, dict):
        content = resp.get("content")
        if isinstance(content, list):
            return "\n".join(b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text")
        return json.dumps(resp, ensure_ascii=False)
    return ""


def main():
    payload = read_payload()
    if not re.search(r"__sv_[a-z_]+$", payload.get("tool_name", "") or ""):
        return
    size = len(_response_text(payload).encode("utf-8", "replace"))
    if size <= TIER1:
        return

    kb = size // 1024
    if size <= TIER2:
        print(f"[socius-vigil · bağlam ekonomisi] Bu gövde ~{kb} KB (>6 KB eşiği). "
              "Ham JSON'u ana pencerede akıl yürütme: pazar × dil ekseninde <=4 paralel "
              "shard ile `pazar-tarama-distilleri` alt-ajanına devret; geri yalnız tek bir "
              "sv_distillate zarfı gelsin (<=20 bulgu + coverage). Ham JSON, tam-metin blok "
              "ve tam URL listesi ana pencereye SIZMAZ.")
        return

    if env_present("ANAMNESIS_MCP_API_KEY"):
        print(f"[socius-vigil · bağlam ekonomisi] Bu gövde ~{kb} KB (>30 KB eşiği). "
              "Tier-2: `anamnesis` ile ingest→bounded query yap; belge kimliğini "
              "`socius:` ön ekiyle yaz. Tam gövdeyi ana pencereye ALMA.")
    else:
        print(f"[socius-vigil · bağlam ekonomisi] Bu gövde ~{kb} KB (>30 KB eşiği) ve "
              "ANAMNESIS_MCP_API_KEY yok. Tier-2 substrat kapalı → bounded-chunk okumaya "
              "düş: yapısal navigasyonla hedef pasajı seç, kalanı okuma; bulguları "
              "evidence_ledger'a yaz. Bu degrade §13'te BEYAN EDİLİR (P4).")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
```

- [ ] **Adım 4: `shared/context-economy-contract.md` yaz**

```markdown
# Bağlam ekonomisi sözleşmesi — socius-vigil

Üç kademe. Eşikler `hooks/scripts/retrieve_dont_dump.py` tarafından **ölçülür**; bu belge
onların anlamını sabitler.

| Tier | Eşik | Ne yapılır | Bağlı değilse |
|---|---|---|---|
| **Tier 0** | <=6 KB | Doğrudan ana pencerede oku ve yorumla. | — |
| **Tier 1** | >6 KB | `pazar-tarama-distilleri` alt-ajanına devret. Sharding ekseni **pazar × dil** — platform DEĞİL (aynı platformun farklı dilleri farklı sinyal taşır; aynı dilin farklı platformları örtüşür). <=4 paralel çağrı. | Alt-ajan yoksa gövdeyi kendin özetle; ham JSON'u yine dökme. |
| **Tier 2** | >30 KB | `anamnesis` ingest → bounded query. Belge kimliği `socius:` ön ekli. | `ANAMNESIS_MCP_API_KEY` yoksa bounded-chunk okumaya düş + §13'te beyan et. |

**Değişmez:** ham JSON, tam-metin blok ve tam URL listesi ana pencereye sızmaz. Distiller
zarfı (`sv_distillate`) <=20 bulgu taşır; her bulgu: kaynak · dil · platform · URL · tarih ·
<=2 cümle özet · Admiralty ön-notu. Zarfın yanında `coverage` bloğu gelir.

**Neden kör getirme yok:** büyük bir belgeyi "önce çekip sonra bakayım" diye almak bağlamın
yarısını yakar ve sentez kalitesini düşürür. Önce yapısal navigasyon (başlık/bölüm/sayfa),
sonra hedef chunk, gerekirse Tier-2.
```

- [ ] **Adım 5: `shared/coverage-manifest.md` yaz**

```markdown
# G0 kapsam manifestosu grameri — socius-vigil

Her substantif çıktı, **Teknik Süreç Eki** içinde bir kapsam manifestosu taşır. Manifesto
okuyucu kopyasına GİRMEZ (§11.5 iki-artefakt kuralı); TSE'de `<!-- OPS: ... -->` bloğunda
yaşar.

**Bir satır = bir server.** Durum sözlüğü:

| Durum | Anlamı |
|---|---|
| `hit N` | Çağrıldı, N kullanılabilir sonuç döndü. |
| `empty` | Çağrıldı, sonuç yok. **Yokluk kanıtı DEĞİLDİR** — sorgu/kapsam sınırı olabilir. |
| `degraded: <gerekçe>` | Çağrıldı, birincil olmayan sağlayıcıya düşüldü veya kısmi sonuç geldi. Gerekçe zorunlu. |
| `skipped: <gerekçe>` | Çağrılmadı. Gerekçe **zorunlu** — "anahtar yok", "mod için N/A", "kapsam dışı". Gerekçesiz skip yasaktır. |

**Çekirdek filo (4):** socius-vigil · exa · tavily · anamnesis
**Opsiyonel filo (6, yalnız etkinleştirilmişse):** tripadvisor · pubmed-epmc · consensus ·
clinical-trials · titck · thoughtspot
**Delegasyon satırları (3):** pazar-tarama-distilleri · vijilans-triyaj · rapor-denetcisi

**Sessiz atlama = G0 ihlali.** Bağlı bir connector'ın tetiklenmiş bağlamda çağrılmaması,
manifestoda gerekçesiyle yazılmadıkça ihlaldir. Bir katmanın yokluğu raporu durdurmaz —
gizlenmesi durdurur.
```

- [ ] **Adım 6: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_retrieve.py -v
```

Beklenen: hepsi PASS.

- [ ] **Adım 7: Commit**

```bash
git add plugins/socius-vigil/hooks/scripts/retrieve_dont_dump.py \
        plugins/socius-vigil/hooks/tests/test_retrieve.py \
        plugins/socius-vigil/shared
git commit -m "feat(socius-vigil): retrieve-don't-dump + bağlam ekonomisi ve kapsam manifestosu sözleşmeleri"
```

---

### Görev 7: `stop_gates.py` — G9/G10/G12/G13/G14 turu tamamlatarak uygular

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/hooks/scripts/stop_gates.py`
- Test: `plugins/socius-vigil/hooks/tests/test_stop_gates.py`

**Arayüzler:**
- Tüketir: `_signals.{read_payload, transcript_text, report_signature, meta_turn, emit_block}`, `_turn_tools.{read_ledger, sv_tool_invoked, transcript_available}`, `socius_doctor.TOOL_NAMES`.
- Üretir: eksik kapı varsa tek `emit_block(reason)`; reason her eksik kapıyı ayrı satırda sayar.

- [ ] **Adım 1: Testi yaz (mutasyon denetimli)**

`plugins/socius-vigil/hooks/tests/test_stop_gates.py`:

```python
#!/usr/bin/env python3
"""stop_gates — G9/G10/G12/G13/G14 + P2 fail-open + P3 meta-tur. Ağ yok."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent
SCRIPTS = HOOKS / "scripts"
sys.path.insert(0, str(SCRIPTS))
from _turn_tools import ledger_path  # noqa: E402

TAM_RAPOR = """# Pazar Zekâsı Raporu — Atoderm Crème

## 0. Yönetici Özeti (BLUF)
Fransa'da güçlü organik savunuculuk; koku ana bariyer.

## 3. Talep ve Ses Payı
Ses payı %18, kategori talebi yatay [1].

## 4. Sentiment Peyzajı ve Ticari Sonuçları
Net sentiment +0,32 [1].

## 5. Müşteri Sesi — Satın Alma Sürücüleri ve Bariyerleri
Sürücü: nemlendirme. Bariyer: koku [2].

## 7. Rakip Konumlandırma ve Algı Haritası
Cetaphil fiyatta, Avène hassasiyette konumlanıyor [3].

## 12. Satış ve Pazarlama Önerileri
1. Koku varyantı testi — Sorumlu (R): ürün; Onaylayan (A): pazarlama direktörü. Dayanak §5.

## 13. Sınırlılıklar, Kapsama Boşlukları ve Kaynak Oynaklığı
Instagram API-kapılı, yıldız dağılımı alınamadı. Rakamlar kaynaklıdır; uydurulmuş veri yok.
Tek SKU (Atoderm Crème 500 ml) hedeflendi; gama-içi diğer formlar ayrı tutuldu.

## 14. Kaynakça
[1] Doctissimo, erişim 2026-08-01, https://a.example
[2] Amazon.fr, erişim 2026-08-01, https://b.example
[3] Beaute-test, erişim 2026-08-01, https://c.example
"""

DEFTER = [
    {"tool": "sv_search", "provider": "searxng", "degraded": False,
     "provenance": {"timestamp": "2026-08-12T10:00:00+00:00"}},
    {"tool": "sv_sentiment", "provider": "native", "degraded": False,
     "provenance": {"timestamp": "2026-08-12T10:01:00+00:00"}},
]


def transcript(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    f.write(json.dumps({"message": {"role": "user", "content": "rapor"}}) + "\n")
    f.write(json.dumps({"message": {"role": "assistant",
                                    "content": [{"type": "text", "text": text}]}}) + "\n")
    f.close()
    return f.name


def seed_ledger(sid, records):
    p = ledger_path({"session_id": sid})
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
                 encoding="utf-8")


def run(text, sid="test-gates", records=DEFTER, stop_active=False):
    seed_ledger(sid, records)
    payload = {"session_id": sid, "transcript_path": transcript(text),
               "stop_hook_active": stop_active}
    p = subprocess.run([sys.executable, str(SCRIPTS / "stop_gates.py")],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout


class TestTemizRapor(unittest.TestCase):
    def test_tam_rapor_gecer(self):
        rc, out = run(TAM_RAPOR)
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "", f"beklenmeyen blok: {out}")


class TestKapilar(unittest.TestCase):
    def test_g12_bos_defter_yakalanir(self):
        rc, out = run(TAM_RAPOR, records=[])
        self.assertIn("G12", out)

    def test_g12_uydurma_arac_adi_yakalanir(self):
        kirli = DEFTER + [{"tool": "sv_magic_insight", "provider": "x",
                           "provenance": {"timestamp": "2026-08-12T10:02:00+00:00"}}]
        rc, out = run(TAM_RAPOR, records=kirli)
        self.assertIn("G12", out)
        self.assertIn("sv_magic_insight", out)

    def test_g9_beyan_eksikse_yakalanir(self):
        rc, out = run(TAM_RAPOR.replace(
            "Rakamlar kaynaklıdır; uydurulmuş veri yok.", ""))
        self.assertIn("G9", out)

    def test_g13_tek_eksenli_rapor_yakalanir(self):
        tek_eksen = "\n\n".join(
            b for b in TAM_RAPOR.split("\n\n")
            if not b.startswith(("## 5.", "## 7.")))
        rc, out = run(tek_eksen)
        self.assertIn("G13", out)

    def test_g14_raci_yoksa_yakalanir(self):
        rc, out = run(TAM_RAPOR.replace(
            "Sorumlu (R): ürün; Onaylayan (A): pazarlama direktörü. Dayanak §5.", "Yapılmalı."))
        self.assertIn("G14", out)

    def test_g10_sku_etiketi_yoksa_yakalanir(self):
        rc, out = run(TAM_RAPOR.replace(
            "Tek SKU (Atoderm Crème 500 ml) hedeflendi; gama-içi diğer formlar ayrı tutuldu.", ""))
        self.assertIn("G10", out)


class TestP2FailOpen(unittest.TestCase):
    def test_stop_hook_active_dongu_kirar(self):
        rc, out = run(TAM_RAPOR, records=[], stop_active=True)
        self.assertEqual(out.strip(), "")

    def test_block_kararidir_iptal_degil(self):
        rc, out = run(TAM_RAPOR, records=[])
        self.assertEqual(json.loads(out)["decision"], "block")
        self.assertEqual(rc, 0)

    def test_bozuk_stdin_fail_open(self):
        p = subprocess.run([sys.executable, str(SCRIPTS / "stop_gates.py")],
                           input="BOZUK", capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0)


class TestP3MetaTur(unittest.TestCase):
    def test_plugin_gelistirme_turu_ateslenmez(self):
        meta = ("stop_gates.py ve clean_copy_guard.py script'lerini yazdım.\n\n"
                "# Pazar Zekâsı Raporu — fixture\n\n## 1. Bir\n## 2. İki\n## 3. Üç\n")
        rc, out = run(meta, records=[])
        self.assertEqual(out.strip(), "")

    def test_kisa_yanit_ateslenmez(self):
        rc, out = run("Evet, ses payı yaklaşık %18.", records=[])
        self.assertEqual(out.strip(), "")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_stop_gates.py -v
```

Beklenen: script yok → hepsi FAIL.

- [ ] **Adım 3: `stop_gates.py` yaz**

```python
#!/usr/bin/env python3
"""Stop — substantif rapor çıktısında G9/G10/G12/G13/G14 denetimi. Fail-open, P3 korumalı."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from _signals import emit_block, meta_turn, read_payload, report_signature, transcript_text  # noqa: E402
from _turn_tools import read_ledger, sv_tool_invoked, transcript_available  # noqa: E402
from socius_doctor import TOOL_NAMES  # noqa: E402

# G13 minimum eksen: talep/SoV + sentiment + VoC + konumlandırma
EKSENLER = {
    "talep/SoV": re.compile(r"ses payı|share of voice|\bSoV\b|talep", re.I),
    "sentiment": re.compile(r"sentiment|duygu (analizi|peyzajı)", re.I),
    "VoC": re.compile(r"müşteri sesi|sürücü|bariyer|\bVoC\b|Kano", re.I),
    "konumlandırma": re.compile(r"konumlandırma|algı haritası|beyaz alan|rakip", re.I),
}
G9_RX = re.compile(r"uydurul(muş|mamış)|kaynaklıdır|alınamadı|API-kapılı|JS-kapılı", re.I)
G14_RX = re.compile(r"\bRACI\b|Sorumlu \(R\)|Onaylayan \(A\)", re.I)
G10_RX = re.compile(r"\bSKU\b", re.I)
SECTION_12_RX = re.compile(r"^##\s*12\.", re.M)
SECTION_13_RX = re.compile(r"^##\s*13\.", re.M)


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return  # P2 döngü koruması

    text = transcript_text(payload)
    if not report_signature(text):
        return  # substantif rapor değil
    if meta_turn(text):
        return  # P3 — plugin'in kendi kodu üzerinde çalışılıyor

    # Transkript varsa kesin sinyal: gerçekten sv_* çağrıldı mı?
    if transcript_available(payload) and not sv_tool_invoked(payload):
        # MCP hiç kullanılmadıysa rapor native düşüşle üretilmiş olabilir —
        # bu meşrudur ama G12 beyanı zorunludur; defter denetimine devam et.
        pass

    ledger = read_ledger(payload)
    eksik = []

    # G12 — defter dolu mu, uydurma araç adı var mı
    if not ledger:
        eksik.append(
            "G12 — MCP araç-çağrı defteri BOŞ. Teknik Süreç Eki T1'e her çağrıyı yaz "
            "(tool · provider · degraded · gaps · enriched_by · provenance.timestamp). "
            "MCP hiç kullanılmadıysa bunu native düşüş olarak açıkça beyan et.")
    else:
        hayalet = sorted({r.get("tool", "") for r in ledger} - set(TOOL_NAMES))
        if hayalet:
            eksik.append(
                f"G12 İHLALİ — kanonik olmayan araç adı defterde: {', '.join(hayalet)}. "
                f"Yalnız 18 kanonik sv_* adı ve bildirilmiş native düşüşler yazılabilir; "
                "uydurulmuş araç adı yasaktır.")

    # G9 — no-fabrication / gap beyanı
    if not SECTION_13_RX.search(text) or not G9_RX.search(text):
        eksik.append(
            "G9 — §13 sınırlılık beyanı eksik. Her kantitatif puan 'alındı (kaynaklı)' ya da "
            "'JS/API-kapılı — alınamadı' olarak işaretlenmeli; uydurulmuş rakam yok cümlesi "
            "ve kapsama boşlukları yazılmalı.")

    # G13 — çok eksenli içgörü
    bulunan = [ad for ad, rx in EKSENLER.items() if rx.search(text)]
    if len(bulunan) < 3:
        eksik.append(
            f"G13 — içgörü tek-eksenli. Bulunan eksenler: {', '.join(bulunan) or 'yok'}. "
            "En az üçü gerekir: talep/SoV · sentiment · VoC (sürücü-bariyer) · konumlandırma "
            "(references/11).")

    # G14 — aksiyonellik
    if not SECTION_12_RX.search(text) or not G14_RX.search(text):
        eksik.append(
            "G14 — §12 önerileri RACI taşımıyor veya yok. Her öneri önceliklendirilmiş, "
            "sorumlusu belli ve bir §3–§10 bulgusuna çapalı olmalı; genel tavsiye sayılmaz.")

    # G10 — SKU disambiguasyonu
    if not G10_RX.search(text):
        eksik.append(
            "G10 — SKU etiketlemesi görünmüyor. Çok-SKU markada hedef SKU kilitlenmeli, her "
            "bulgu tek SKU'ya etiketlenmeli, gama-içi formlar birleştirilmemeli.")

    if eksik:
        emit_block("[socius-vigil · kapı denetimi] Bu rapor eksik kapılarla kapanıyor. "
                   "Turu tamamla:\n\n" + "\n\n".join(f"• {e}" for e in eksik))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
```

- [ ] **Adım 4: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_stop_gates.py -v
```

Beklenen: hepsi PASS. `test_tam_rapor_gecer` FAIL ederse yanlış-pozitif var — kapı regex'ini gevşet, testi değiştirme.

- [ ] **Adım 5: Commit**

```bash
git add plugins/socius-vigil/hooks/scripts/stop_gates.py plugins/socius-vigil/hooks/tests/test_stop_gates.py
git commit -m "feat(socius-vigil): stop_gates — G9/G10/G12/G13/G14 hook uygulaması"
```

---

### Görev 8: `clean_copy_guard.py` — G16, doktrinin dişleri

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/hooks/scripts/clean_copy_guard.py`
- Test: `plugins/socius-vigil/hooks/tests/test_clean_copy.py`

**Arayüzler:**
- Tüketir: `_signals.{read_payload, transcript_text, report_signature, meta_turn, emit_block}`.
- Üretir: yasaklı jeton bulunursa `emit_block(reason)`; reason her sızıntıyı **konumuyla** (satır numarası + jeton) listeler.

**Neden bu kapı hook olmak zorunda:** G16, bir modelin kendi çıktısında en kötü yakaladığı ihlal türüdür — kendi ürettiği teknik jargonu "okuyucu için doğal" sanır. Rapor uzadıkça atlanma olasılığı artar. Deterministik jeton taraması bunu ucuz ve kesin yapar.

- [ ] **Adım 1: Testi yaz**

`plugins/socius-vigil/hooks/tests/test_clean_copy.py`:

```python
#!/usr/bin/env python3
"""clean_copy_guard — G16 yasaklı jeton taraması. Ağ yok."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

TEMIZ = """# Pazar Zekâsı Raporu — Atoderm Crème

## 0. Yönetici Özeti (BLUF)
Ürün Fransa'da güçlü organik savunuculuk taşıyor; koku ana bariyer.

## 3. Talep ve Ses Payı
Ses payı %18 [1]. Ses payı, bir markanın kategori konuşmasındaki payıdır.

## 5. Müşteri Sesi
Nemlendirme sürücü, koku bariyer [2].

<!-- VIZ: sürücü-bariyer yatay çubuk grafiği -->

## 14. Kaynakça
[1] Doctissimo, erişim 2026-08-01, https://a.example
[2] Amazon.fr, erişim 2026-08-01, https://b.example
"""


def transcript(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    f.write(json.dumps({"message": {"role": "user", "content": "rapor"}}) + "\n")
    f.write(json.dumps({"message": {"role": "assistant",
                                    "content": [{"type": "text", "text": text}]}}) + "\n")
    f.close()
    return f.name


def run(text, stop_active=False):
    payload = {"session_id": "test-clean", "transcript_path": transcript(text),
               "stop_hook_active": stop_active}
    p = subprocess.run([sys.executable, str(SCRIPTS / "clean_copy_guard.py")],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout


class TestTemizKopya(unittest.TestCase):
    def test_temiz_rapor_gecer(self):
        rc, out = run(TEMIZ)
        self.assertEqual(out.strip(), "", f"yanlış pozitif: {out}")

    def test_html_yorumundaki_viz_sizinti_degil(self):
        self.assertIn("<!-- VIZ", TEMIZ)
        rc, out = run(TEMIZ)
        self.assertEqual(out.strip(), "")


class TestSizintilar(unittest.TestCase):
    def test_sv_arac_adi_yakalanir(self):
        rc, out = run(TEMIZ.replace("Ses payı %18 [1].", "sv_sentiment %18 verdi [1]."))
        self.assertIn("sv_sentiment", out)

    def test_mcp_kelimesi_yakalanir(self):
        rc, out = run(TEMIZ.replace("Ses payı %18 [1].", "MCP'den alınan veriye göre %18 [1]."))
        self.assertIn("MCP", out)

    def test_parantezli_kapi_kodu_yakalanir(self):
        rc, out = run(TEMIZ.replace("koku bariyer [2].", "koku bariyer (G11) [2]."))
        self.assertIn("G11", out)

    def test_sv_fix_yakalanir(self):
        rc, out = run(TEMIZ.replace("koku bariyer [2].", "koku bariyer (SV-FIX-03) [2]."))
        self.assertIn("SV-FIX", out)

    def test_script_dosya_adi_yakalanir(self):
        rc, out = run(TEMIZ.replace("Ses payı %18 [1].", "market_synthesis.py çıktısı %18 [1]."))
        self.assertIn("market_synthesis.py", out)

    def test_gorunur_viz_yakalanir(self):
        rc, out = run(TEMIZ.replace("<!-- VIZ: sürücü-bariyer yatay çubuk grafiği -->",
                                    "VIZ: sürücü-bariyer yatay çubuk grafiği"))
        self.assertIn("VIZ", out)

    def test_doldurulmamis_koseli_parantez_yakalanir(self):
        rc, out = run(TEMIZ.replace("Ses payı %18 [1].", "Ses payı [ORAN GİRİLECEK] [1]."))
        self.assertIn("ORAN GİRİLECEK", out)

    def test_sizinti_satir_numarasi_bildirir(self):
        rc, out = run(TEMIZ.replace("Ses payı %18 [1].", "sv_sentiment %18 [1]."))
        self.assertRegex(out, r"satır\s*\d+")


class TestP2P3(unittest.TestCase):
    def test_stop_hook_active_dongu_kirar(self):
        rc, out = run(TEMIZ.replace("Ses payı %18 [1].", "sv_sentiment %18 [1]."), stop_active=True)
        self.assertEqual(out.strip(), "")

    def test_meta_tur_ateslenmez(self):
        meta = ("clean_copy_guard.py yazdım; sv_sentiment jetonunu tarıyor.\n\n"
                "# Pazar Zekâsı Raporu — fixture\n\n## 1. Bir\n## 2. İki\n## 3. Üç\n")
        rc, out = run(meta)
        self.assertEqual(out.strip(), "")

    def test_bozuk_stdin_fail_open(self):
        p = subprocess.run([sys.executable, str(SCRIPTS / "clean_copy_guard.py")],
                           input="BOZUK", capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_clean_copy.py -v
```

Beklenen: script yok → hepsi FAIL.

- [ ] **Adım 3: `clean_copy_guard.py` yaz**

```python
#!/usr/bin/env python3
"""Stop — G16 temiz-kopya jeton taraması. Fail-open, P3 korumalı."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _signals import emit_block, meta_turn, read_payload, report_signature, transcript_text  # noqa: E402

HTML_COMMENT_RX = re.compile(r"<!--.*?-->", re.S)

YASAKLI = [
    ("sv_* araç adı", re.compile(r"\bsv_[a-z_]+\b")),
    ("MCP jetonu", re.compile(r"\bMCP\b")),
    ("parantezli kapı kodu", re.compile(r"[(（]\s*G\d{1,2}\s*[)）]")),
    ("SV-FIX kodu", re.compile(r"\bSV-FIX[-\w]*")),
    ("script/şema dosya adı", re.compile(r"\b\w+\.(py|json|ts|yaml)\b")),
    ("görünür VIZ yönergesi", re.compile(r"(?<!<!--\s)\bVIZ\b")),
    ("doldurulmamış köşeli parantez", re.compile(r"\[[A-ZÇĞİÖŞÜ][^\]]{3,}\]")),
]

# Kaynakça atıfları [1] [12] meşrudur — doldurulmamış parantez taramasından muaftır.
CITE_RX = re.compile(r"^\[\d+\]$")


def _mask_comments(text):
    """HTML yorumlarını aynı satır sayısını koruyarak boşluğa çevir."""
    def repl(m):
        return "\n" * m.group(0).count("\n")
    return HTML_COMMENT_RX.sub(repl, text)


def _reader_copy(text):
    """Okuyucu Raporu = TSE başlamadan önceki kısım."""
    for marker in ("# Teknik Süreç Eki", "## T1.", "Teknik Süreç Eki —"):
        idx = text.find(marker)
        if idx > 0:
            return text[:idx]
    return text


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return
    text = transcript_text(payload)
    if not report_signature(text) or meta_turn(text):
        return

    body = _mask_comments(_reader_copy(text))
    bulgular = []
    for lineno, line in enumerate(body.splitlines(), start=1):
        for etiket, rx in YASAKLI:
            for m in rx.finditer(line):
                jeton = m.group(0)
                if etiket == "doldurulmamış köşeli parantez" and CITE_RX.match(jeton):
                    continue
                bulgular.append(f"satır {lineno} · {etiket}: {jeton}")
    if not bulgular:
        return

    ilk = bulgular[:12]
    kalan = len(bulgular) - len(ilk)
    kuyruk = f"\n… ve {kalan} sızıntı daha." if kalan > 0 else ""
    emit_block(
        "[socius-vigil · G16 temiz kopya] Okuyucu Raporu teknik jargon sızıntısı taşıyor. "
        "§11.5 doktrini: okuyucu kopyasında sv_* araç adı, 'MCP', parantezli kapı kodu, "
        "SV-FIX, script/şema dosya adı, görünür VIZ ve doldurulmamış köşeli parantez "
        "BULUNAMAZ — bunların yeri Teknik Süreç Eki'dir. Turu tamamla ve şunları temizle:\n\n"
        + "\n".join(f"• {b}" for b in ilk) + kuyruk)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
```

- [ ] **Adım 4: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/hooks/tests/test_clean_copy.py -v
```

Beklenen: hepsi PASS. `test_temiz_rapor_gecer` FAIL ederse yanlış-pozitif var (muhtemelen `\w+\.(py|json)` kaynakça URL'sinde eşleşiyor) — regex'i daralt, testi değiştirme.

- [ ] **Adım 5: Tüm hook testlerini birlikte koş**

```bash
for t in plugins/socius-vigil/hooks/tests/test_*.py; do echo "== $t"; python3 "$t" 2>&1 | tail -3; done
```

Beklenen: dört dosyanın hepsi OK.

- [ ] **Adım 6: Commit**

```bash
git add plugins/socius-vigil/hooks/scripts/clean_copy_guard.py plugins/socius-vigil/hooks/tests/test_clean_copy.py
git commit -m "feat(socius-vigil): clean_copy_guard — G16 temiz-kopya jeton taraması"
```

---

### Görev 9: 12 mod skill'i (13. = flagship)

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/skills/{start,durum,pazar-raporu,hizli-tarama,voc,rakip,fiyat,trend,kol,perakende,vijilans,yayin}/SKILL.md`
- Değiştir: `plugins/socius-vigil/tests/test_doctor.py` (Görev 3'te eklenen iki `@unittest.skip` kaldırılır)
- Test: `plugins/socius-vigil/tests/test_skills.py`

**Arayüzler:**
- Tüketir: flagship gövdesi — her mod skill'i `../socius-vigil/references/NN-*.md` göreli yoluyla atıf verir, **kopyalamaz** (P1).
- Üretir: 13 slash komut (`/socius-vigil:<ad>`); `socius_doctor.py --skills` ve `--sections` bunları denetler.

**Ortak kalıp — her mod skill'i altı başlıktan oluşur ve ≤120 satırdır:**
`## Ne zaman tetiklenir` · `## Zorunlu yüklemeler` · `## Araç sırası` · `## Çerçeve → rapor bölümü` · `## Kapılar` · `## Degrade yolu`

- [ ] **Adım 1: Skill testini yaz**

`plugins/socius-vigil/tests/test_skills.py`:

```python
#!/usr/bin/env python3
"""13 skill: yapı, uzunluk, P1 atıf disiplini, kapı bildirimi. Ağ yok."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
MODLAR = ["start", "durum", "pazar-raporu", "hizli-tarama", "voc", "rakip",
          "fiyat", "trend", "kol", "perakende", "vijilans", "yayin"]
BASLIKLAR = ["Ne zaman tetiklenir", "Zorunlu yüklemeler", "Araç sırası",
             "Çerçeve → rapor bölümü", "Kapılar", "Degrade yolu"]
TOOL_NAMES = set((ROOT / "scripts/socius_doctor.py").read_text(encoding="utf-8")
                 .split("TOOL_NAMES = [")[1].split("]")[0].replace('"', "").replace(",", " ").split())


def body(name):
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


class TestVarlik(unittest.TestCase):
    def test_on_uc_skill_var(self):
        found = {d.name for d in SKILLS.iterdir() if d.is_dir()}
        self.assertEqual(found, set(MODLAR) | {"socius-vigil"})


class TestYapi(unittest.TestCase):
    def test_frontmatter_alanlari(self):
        for m in MODLAR:
            t = body(m)
            self.assertRegex(t, r"^---\nname: " + re.escape(m) + r"\n", msg=m)
            self.assertIn("description:", t, m)
            self.assertIn("allowed-tools:", t, m)

    def test_uzunluk_120_satiri_asmaz(self):
        for m in MODLAR:
            n = len(body(m).splitlines())
            self.assertLessEqual(n, 120, f"{m}: {n} satır")

    def test_alti_baslik_tam(self):
        for m in MODLAR:
            if m in ("start", "durum"):
                continue  # oryantasyon/teşhis skill'leri bu iskeleti taşımaz
            for h in BASLIKLAR:
                self.assertIn(f"## {h}", body(m), f"{m}: '{h}' başlığı yok")


class TestP1AtifDisiplini(unittest.TestCase):
    def test_referanslar_goreli_yolla_cagrilir(self):
        for m in MODLAR:
            for ref in re.findall(r"references/(\d\d)-", body(m)):
                self.assertTrue((SKILLS / "socius-vigil/references").glob(f"{ref}-*"),
                                f"{m}: references/{ref} yok")

    def test_mod_skilli_kendi_referansini_tasimaz(self):
        for m in MODLAR:
            self.assertFalse((SKILLS / m / "references").exists(), m)


class TestAracAdlari(unittest.TestCase):
    def test_yalniz_kanonik_arac_adlari(self):
        for m in MODLAR:
            ghosts = set(re.findall(r"\bsv_[a-z_]+\b", body(m))) - TOOL_NAMES
            self.assertEqual(ghosts, set(), f"{m}: uydurma araç {ghosts}")


class TestKapiBildirimi(unittest.TestCase):
    BEKLENEN = {
        "pazar-raporu": ["G1", "G16"], "hizli-tarama": ["G2", "G9", "G12"],
        "voc": ["G9", "G11", "G13"], "rakip": ["G2", "G3", "G13", "G14"],
        "fiyat": ["G9", "G11"], "trend": ["G2", "G3", "G9"],
        "kol": ["G15", "G3", "G4"], "perakende": ["G11", "G9", "G10"],
        "vijilans": ["G4", "G5", "G8"], "yayin": ["G16", "G7", "G12"],
    }

    def test_her_mod_kendi_kapilarini_sayar(self):
        for m, gates in self.BEKLENEN.items():
            t = body(m).split("## Kapılar")[1].split("\n## ")[0]
            for g in gates:
                self.assertIn(g, t, f"{m}: {g} bildirilmemiş")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/tests/test_skills.py -v
```

Beklenen: `test_on_uc_skill_var` FAIL (yalnız flagship var).

- [ ] **Adım 3: `pazar-raporu` skill'ini yaz (kanonik örnek — kalan modlar bunu izler)**

`plugins/socius-vigil/skills/pazar-raporu/SKILL.md`:

```markdown
---
name: pazar-raporu
description: "MARKET_INTELLIGENCE_REPORT — bir ürün/hizmet/marka hakkında uçtan uca nitelikli pazar araştırması: talep, ses payı, sentiment peyzajı, müşteri sesi, perakende yorum analizi, trendler, rakip konumlandırma, fikir liderleri, risk sinyalleri ve RACI'li satış-pazarlama önerileri. §0–§14 tam rapor üretir. Kullanın: 'X ürünü için pazar araştırması', 'kapsamlı pazar zekâsı raporu', 'bu markayı pazarda analiz et', 'uçtan uca sosyal dinleme raporu' taleplerinde."
argument-hint: "<ürün/hizmet/marka> [pazar(lar)] [sektör]"
allowed-tools: Read, Glob, Grep, WebFetch, WebSearch, Task
disable-model-invocation: false
---

# MARKET_INTELLIGENCE_REPORT — amiral gemisi

Flagship protokolü `MARKET_INTELLIGENCE_REPORT` moduyla çalıştır.

## Ne zaman tetiklenir

Kullanıcı bir ürün/hizmet/marka verip kapsamlı pazar görünümü istediğinde. Tek bir eksen
isteniyorsa (yalnız fiyat, yalnız rakip, yalnız yorum) dar moda yönlendir — bu mod tam
raporu üretir ve pahalıdır.

## Zorunlu yüklemeler

```
view ../socius-vigil/SKILL.md                                  # protokol gövdesi §0–§14
view ../socius-vigil/references/11-market-research-frameworks.md
view ../socius-vigil/references/13-section-map.md
view ../socius-vigil/references/16-clean-copy-presentation.md   # teslim öncesi
```

## Araç sırası

1. `sv_build_query_library` — çok dilli sorgu kütüphanesi (G2'nin girdisi)
2. `sv_source_inventory` — pazar/sektör kaynak haritası (`references/12`)
3. `sv_search` → boşta `sv_search_fallback` → tam içerik için `sv_fetch`
4. `sv_retail_review_scan` → `sv_retail_filter` → `sv_extract_reviews` (+ `sv_extract_rating`)
5. `sv_sentiment` — net sentiment + tema
6. `sv_market_synthesis` — SoV/ESOV, Kano, huni eşlemesi
7. `sv_admiralty_score` + `sv_triangulate` — eskale edilen her bulgu için
8. Sağlık rejimi açıksa: `sv_icsr_check` → `sv_ach_matrix` (ambigü sinyaller)
9. Teslimden önce `/socius-vigil:yayin`

Adım 3–4 onlarca çağrı üretir → **`pazar-tarama-distilleri` alt-ajanına devret**
(pazar × dil ekseninde ≤4 shard). Ham JSON ana pencereye girmez.

## Çerçeve → rapor bölümü

| Çerçeve | Bölüm |
|---|---|
| IR/PIR + EEI | §1 |
| Kapsam + yöntem | §2 |
| Talep + SoV→ESOV | §3 |
| Perakende yorum analitiği | §3.5 |
| Sentiment → ticari sonuç | §4 |
| VoC / Kano sürücü-bariyer | §5 |
| Trend + inovasyon sinyali | §6 |
| STP + algı haritası + beyaz alan | §7 |
| KOL peyzajı + duruş + değerleme | §8 |
| Marka değeri sinyalleri | §9 |
| Vijilans / risk | §10 |
| Sentez + doğrulama | §11 |
| RACI'li öneriler | §12 |
| Sınırlılıklar + boşluklar | §13 |
| Kaynakça | §14 |

## Kapılar

**G1–G16 tamamı.** Bu modda hiçbiri N/A değildir; uygulanamayan kapı (ör. ürün online
satılmıyorsa G11) açıkça "N/A — gerekçe" yazılır, sessizce atlanmaz.
Kapıların hangisinin makineyle uygulandığı: flagship §12 "Uygulama" sütunu.

## Degrade yolu

| Eksik | Sonuç |
|---|---|
| `SOCIUS_VIGIL_MCP_API_KEY` yok | Toplama/skorlama `scripts/*.py` native düşüşüne iner; rapor üretilir, G12 altında beyan edilir |
| `thoughtspot` bağlı değil | SoM `not_provided` → **ESOV hesaplanmaz**, uydurulmaz; §3'te belirtilir |
| Yorum yüzeyi API-kapılı | Yıldız dağılımı "JS/API-kapılı — alınamadı" olarak işaretlenir (G9) |
| `anamnesis` yok | >30 KB gövdeler bounded-chunk okunur; §13'te beyan edilir |
```

- [ ] **Adım 4: Kalan 11 skill'i aynı kalıpla yaz**

Her biri için frontmatter `description` **ayrık** anahtar kelime kümesi taşır (flagship en genel; modlar dar). Tablo bağlayıcıdır:

| Skill | `description` dar anahtar kelimeleri | Araç sırası | Bölüm | Kapılar | Degrade |
|---|---|---|---|---|---|
| `start` | "socius-vigil nedir", "nereden başlayayım", "hangi mod", "connector'larım bağlı mı" | `sv_source_inventory` (opsiyonel) | — (kadro + mod seçim ağacı) | — | Anahtarsız çalışır; eksikleri listeler |
| `durum` | "socius tanı", "araç yüzeyi", "18 araç canlı mı", "skill çakışması" | `tools/list` + `scripts/socius_doctor.py --live` | — | — | Anahtar yoksa statik denetim koşar, canlı prob atlanır |
| `hizli-tarama` | "hızlı enstantane", "quick scan", "kabaca ne konuşuluyor" | `sv_collect_pipeline` → `sv_sentiment` | §0 + §3–§4 özet | G2, G9, G12 | Pipeline yoksa `sv_search`+`sv_sentiment` zincirini elle kur |
| `voc` | "müşteri sesi", "satın alma sürücüsü", "bariyer", "Kano", "ağrı noktası" | `sv_retail_review_scan` → `sv_retail_filter` → `sv_extract_reviews` | §5 (+§3.5) | G9, G11, G13 | Yorum yüzeyi kapalıysa forum/blog VoC'ye düş, §13'te beyan et |
| `rakip` | "ses payı", "share of voice", "ESOV", "konumlandırma", "algı haritası", "beyaz alan" | `sv_build_query_library` (rakip seti) → `sv_search` → `sv_sentiment` → `sv_market_synthesis` | §3, §7 | G2, G3, G13, G14 | `thoughtspot` yoksa SoM `not_provided`, ESOV yazılmaz |
| `fiyat` | "fiyat algısı", "değer-fiyat", "pahalı mı", "ödeme isteği", "fiyat şikâyeti" | `sv_extract_rating` → `sv_extract_reviews` (fiyat faseti) | §3.5, §5 fiyat kesiti | G9, G11 | Puan API-kapılıysa "alınamadı" işaretle, metinden fiyat teması çıkar |
| `trend` | "trend taraması", "ortaya çıkan tema", "kategori yörüngesi", "talep eğrisi" | `sv_search` (zaman pencereli) → `sv_extract_reviews` (hız/burst) | §6 (+§3 talep) | G2, G3, G9 | Zaman serisi alınamazsa yön beyanı "gözlemsel/directional" etiketiyle |
| `kol` | "fikir lideri", "influencer", "eczacı ne diyor", "dermatolog tavrı", "sponsorlu içerik" | `sv_search` (KOL keşfi) → `sv_kol_stance` → `sv_admiralty_score`/`sv_triangulate` | §8 | **G15**, G3, G4 | `sv_kol_stance` yoksa `scripts/kol_stance.py`; açıklama etiketi belirsizse "belirsiz" yaz, tahmin etme |
| `perakende` | "e-ticaret yorumu", "yıldız dağılımı", "doğrulanmış satın alma", "sahte yorum" | `sv_retail_review_scan` → `sv_retail_filter` → `sv_extract_reviews` → `sv_extract_rating` | §3.5 | **G11**, G9, G10 | Platform JS-kapılıysa Exa düşüşü; alınamayan puan uydurulmaz |
| `vijilans` | "advers etki", "istenmeyen etki", "kozmetovijilans", "ICSR", "güvenlik sinyali", "eskalasyon" | `sv_extract_reviews` → `sv_icsr_check` → `sv_admiralty_score` → `sv_ach_matrix` | §10 + eskalasyon triyajı | **G4, G5, G8**, I3 | Aday >15 ise `vijilans-triyaj` alt-ajanına devret; pediatrik bağlamda `references/14` bindir |
| `yayin` | "temiz kopya", "teslim öncesi", "okuyucu raporu", "yayına hazır mı" | `sv_quality_gate --profile clean --annex <TSE>` | İki artefakt ayrıştırma | **G16**, G7, G12 | Araç yoksa `scripts/quality_gate_check.py`; sonrasında `rapor-denetcisi` alt-ajanı |

**`vijilans` skill'ine zorunlu blok** (I3 — pazarlığa kapalı):

```markdown
## Değişmez — WEB-RADR (I3)

Her satır `requires_human_review:true` taşır. Bu skill sinyali **tespit-doğrula-yorumla-
eskale eder**; resmî farmakovijilansta **dosyalamaz** ve nedensellik iddia etmez.
WEB-RADR ölçümü: ürün terimiyle eşleşen gönderilerin <%2'si kişisel AE; aday AE'lerin
~%40'ı gerçek. Bu yüzden aday listesi ham hâlde rapora girmez — elenenlerin **sayısı ve
gerekçe dağılımı** yazılır (eleme şeffaflığı).
Eşikler: Admiralty ≥C3 veya ≥B2 → eskalasyon triyajı; MDR ≤15 gün; kozmetovijilans SUE
≤20 takvim günü (`references/05`).
```

- [ ] **Adım 5: Görev 3'teki iki skip'i kaldır**

`tests/test_doctor.py` içindeki `@unittest.skip("Görev 9'da etkinleşir")` satırlarını sil.

- [ ] **Adım 6: Testleri koş**

```bash
python3 plugins/socius-vigil/tests/test_skills.py -v
python3 plugins/socius-vigil/tests/test_doctor.py -v
python3 plugins/socius-vigil/scripts/socius_doctor.py --skills --sections
```

Beklenen: hepsi PASS; doctor `ÇAKIŞMA YOK` + `TUTARLI` basar. Çakışma raporlanırsa **testi değil, çakışan iki `description`'ı** daralt.

- [ ] **Adım 7: Commit**

```bash
git add plugins/socius-vigil/skills plugins/socius-vigil/tests
git commit -m "feat(socius-vigil): 12 mod skill'i — ayrık tetikleyiciler, P1 atıf disiplini"
```

---

### Görev 10: Üç alt-ajan

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/agents/pazar-tarama-distilleri.md`
- Oluştur: `plugins/socius-vigil/agents/vijilans-triyaj.md`
- Oluştur: `plugins/socius-vigil/agents/rapor-denetcisi.md`
- Test: `plugins/socius-vigil/tests/test_agents.py`

**Arayüzler:**
- Tüketir: Görev 6'nın Tier eşikleri (`retrieve_dont_dump.py` bu ajanlara yönlendirir), Görev 9'un mod skill'leri (devir noktalarını yazar).
- Üretir: `sv_distillate` zarfı (≤20 bulgu + `coverage`) · §10 tablosuna doğrudan giren triyaj satırları · ≤1 sayfa öncelikli düzeltme listesi.

- [ ] **Adım 1: Testi yaz**

`plugins/socius-vigil/tests/test_agents.py`:

```python
#!/usr/bin/env python3
"""Üç alt-ajan: frontmatter, yazma yasağı, çıktı sözleşmesi. Ağ yok."""
import re
import unittest
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agents"
ADLAR = ["pazar-tarama-distilleri", "vijilans-triyaj", "rapor-denetcisi"]


def body(name):
    return (AGENTS / f"{name}.md").read_text(encoding="utf-8")


class TestVarlikVeFrontmatter(unittest.TestCase):
    def test_uc_ajan_var(self):
        self.assertEqual({p.stem for p in AGENTS.glob("*.md")}, set(ADLAR))

    def test_frontmatter_alanlari(self):
        for a in ADLAR:
            t = body(a)
            self.assertRegex(t, r"^---\nname: " + re.escape(a) + r"\n", msg=a)
            self.assertIn("description:", t, a)
            self.assertIn("tools:", t, a)


class TestYazmaYasagi(unittest.TestCase):
    def test_hicbiri_write_edit_kullanamaz(self):
        for a in ADLAR:
            t = body(a)
            self.assertIn("disallowedTools", t, a)
            self.assertIn("Write", t.split("disallowedTools")[1][:120], a)
            self.assertIn("Edit", t.split("disallowedTools")[1][:120], a)


class TestCiktiSozlesmesi(unittest.TestCase):
    def test_distiller_zarf_ve_tavan_bildirir(self):
        t = body("pazar-tarama-distilleri")
        self.assertIn("sv_distillate", t)
        self.assertIn("20", t)          # ≤20 bulgu tavanı
        self.assertIn("coverage", t)
        self.assertIn("pazar × dil", t)  # sharding ekseni platform DEĞİL

    def test_triyaj_i3_ve_eleme_seffafligi(self):
        t = body("vijilans-triyaj")
        self.assertIn("requires_human_review", t)
        self.assertIn("elenen", t.lower())
        self.assertNotIn("dosyala", t.lower().replace("dosyalamaz", ""))

    def test_denetci_duzeltmeyi_kendisi_yapmaz(self):
        t = body("rapor-denetcisi")
        self.assertIn("Kritik", t)
        self.assertIn("Önemli", t)
        self.assertIn("Küçük", t)
        self.assertRegex(t, r"düzeltmeyi\s+kendisi\s+yapmaz|kendisi\s+düzeltmez")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/tests/test_agents.py -v
```

Beklenen: `agents/` yok → hepsi FAIL.

- [ ] **Adım 3: `pazar-tarama-distilleri.md` yaz**

```markdown
---
name: pazar-tarama-distilleri
description: "Ağır, çok-çağrılı pazar taramasını ana bağlamdan izole eden Tier-1 alt-ajan. pazar-raporu · rakip · trend gibi onlarca sv_* çağrısı gereken modlarda çağrılır; ham gürültüyü kendi bağlam penceresinde tüketir ve ana pencereye YALNIZ tek bir sv_distillate zarfı (≤20 bulgu + coverage) döndürür. Tek-çağrılık hızlı sorgular için ÇAĞIRMA — bu ajan yalnız bağlam ekonomisi gerektiğinde devreye girer."
tools: Read, Grep, Glob, WebFetch, WebSearch, Task
disallowedTools: Write, Edit, NotebookEdit
---

# pazar-tarama-distilleri — Tier-1 getirim izolasyonu

Sana bir **aktif konu** (ürün/marka/kategori + pazarlar) verilir. Görevin: ilgili `sv_*`
çağrılarını yapmak, ham çıktıyı **kendi** bağlamında tüketmek ve tek bir damıtılmış zarf
döndürmek.

## Sharding

Bölme ekseni **pazar × dil** — platform DEĞİL. Gerekçe: aynı platformun farklı dilleri
farklı sinyal taşır; aynı dilin farklı platformları büyük ölçüde örtüşür. En fazla **4
paralel** çağrı.

## Döndürdüğün zarf

```
sv_distillate:
  bulgular:            # ≤20; alaka filtresi KATIdır, konuyla ilgisiz olan girmez
    - kaynak: <site/platform>
      dil: <ISO kodu>
      platform: <forum | e-ticaret | sosyal | haber | blog>
      url: <tam URL>
      tarih: <YYYY-MM-DD veya "tarihsiz">
      ozet: <≤2 cümle>
      admiralty_on_not: <A–F/1–6 önerisi + tek cümle gerekçe>
  coverage:            # her server için BİR satır
    - <server>: hit N | empty | degraded: <gerekçe> | skipped: <gerekçe>
```

## Yasaklar

- Ham JSON, tam-metin blok ve tam URL listesi ana pencereye **sızmaz**.
- Bulgu sayısı 20'yi aşarsa **en yüksek Admiralty ön-notlu** 20'yi seç ve elenen sayısını
  `coverage` altında bildir — sessizce kırpma.
- Uydurma yok: bulunamayan alan `null`, boş sonuç `empty`. Boş sonuç yokluk kanıtı değildir.
- Dosya yazmazsın (`disallowedTools`).
```

- [ ] **Adım 4: `vijilans-triyaj.md` yaz**

```markdown
---
name: vijilans-triyaj
description: "Sağlık rejimi açıkken yorum korpusundaki AE adaylarını izole bağlamda triyaj eden alt-ajan. Her aday için sv_icsr_check + sv_admiralty_score koşar, ambigü olanlara sv_ach_matrix uygular; ana pencereye §10 tablosuna doğrudan girecek satırları + elenenlerin sayı ve gerekçe dağılımını döndürür. Aday sayısı azsa (<15) ÇAĞIRMA — doğrudan vijilans modu yeterlidir."
tools: Read, Grep, Glob, WebFetch, Task
disallowedTools: Write, Edit, NotebookEdit
---

# vijilans-triyaj — AE adayı triyajı

## Neden izole

WEB-RADR ölçümü: ürün terimiyle eşleşen gönderilerin **<%2'si** kişisel advers etkidir ve
aday AE'lerin yalnız **~%40'ı** gerçektir. Yüzlerce adayı ana pencereye dökmek hem bağlamı
taşırır hem yanlış-pozitifle sentezi bozar.

## Yaptığın

1. Her aday için `sv_icsr_check` (4 kriter: reporter · patient · product · reaction)
2. Her aday için `sv_admiralty_score` (A–F/1–6)
3. Ambigü adaylar için `sv_ach_matrix` — varsayılan 4 hipotez:
   gerçek UE · yanlış kullanım · astroturfing · ilgisiz-eşzamanlı

## Döndürdüğün

§10 tablosuna **doğrudan** girecek satırlar:

```
| SKU | Sinyal | ICSR 4-kriter | Admiralty | ACH kazananı | requires_human_review |
```

Ayrıca **eleme şeffaflığı** (§13'e girer): elenen aday **sayısı** + gerekçe dağılımı
(ör. "ürün bağlamı yok: 41 · olumsuzlama: 12 · beklenen reaksiyon: 8").

## Değişmezler (pazarlığa kapalı)

- Her satır `requires_human_review:true`.
- **Vaka dosyalama önerisi yazmazsın**; nedensellik iddia etmezsin.
- `valid_icsr:false` bir adayı otomatik elemez: adı-geçen SKU + uygulama bağlamı varsa
  "şüpheli-ürün taşıyan vaka" olarak taşınır.
- Eşikler: ≥C3 / ≥B2 → eskalasyon triyajı; MDR ≤15 gün; kozmetovijilans SUE ≤20 takvim günü.
- Dosya yazmazsın (`disallowedTools`).
```

- [ ] **Adım 5: `rapor-denetcisi.md` yaz**

```markdown
---
name: rapor-denetcisi
description: "Temiz-kopya geçişinden SONRA, teslimden ÖNCE çağrılan yayın-kalitesi denetçisi. sv_quality_gate --profile clean çıktısını yorumlar ve heuristiğin yakalayamadığı ihlalleri (eksik cümle, kopuk anlatım akışı, çerçevelenmemiş tablo) kendi okumasıyla ekler; ≤1 sayfa öncelikli düzeltme listesi döndürür. Düzeltmeyi KENDİSİ YAPMAZ."
tools: Read, Grep, Glob, Task
disallowedTools: Write, Edit, NotebookEdit
---

# rapor-denetcisi — yayın öncesi ikinci göz

## Ne zaman

`/socius-vigil:yayin` geçişinden **sonra**, teslimden **önce**.

## Yaptığın

1. `sv_quality_gate --profile clean --annex <TSE>` koş (yoksa
   `scripts/quality_gate_check.py --profile clean`).
2. Çıktısını **yorumla** — bir `blocking_failure` listesi tek başına rapor değildir.
3. Heuristiğin göremediğini ekle: P2 (eksiksiz cümle) ve P5 (anlatım akışı, çerçeveleyici
   metinle sarılmamış tablo/şekil) ihlalleri kendi okumanla bulunur.

## Döndürdüğün

**≤1 sayfa**, üç öncelikte:

```
Kritik — <konum> · <tek cümle gerekçe>
Önemli — <konum> · <tek cümle gerekçe>
Küçük  — <konum> · <tek cümle gerekçe>
```

Konum = bölüm numarası + satır/paragraf işareti. Gerekçe **tek cümle**; uzun açıklama yazma.

## Yasaklar

- **Düzeltmeyi kendisi yapmaz** — liste döner, metni değiştirmez (`disallowedTools`).
- Kapı sonucunu "yorumsuz kopyalamak" denetim sayılmaz.
- Temiz görünen rapora "sorun yok" demeden önce §11.5'in yedi ilkesini tek tek tara;
  bulgu yoksa hangi ilkelerin denetlendiğini yaz (denetlenmemiş ≠ temiz).
```

- [ ] **Adım 6: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/tests/test_agents.py -v
```

Beklenen: hepsi PASS.

- [ ] **Adım 7: Commit**

```bash
git add plugins/socius-vigil/agents plugins/socius-vigil/tests/test_agents.py
git commit -m "feat(socius-vigil): üç izole alt-ajan — distiller, vijilans triyajı, rapor denetçisi"
```

---

### Görev 11: `brand-market-signal` stub'a indirgeme

**Dosyalar:**
- Değiştir: `plugins/brand-ecosystem-core/skills/brand-market-signal/SKILL.md` (86 satır → ≤30 satır)
- Değiştir: `plugins/brand-ecosystem-core/.mcp.json` (`socius-vigil._role` metni)
- Değiştir: `plugins/brand-ecosystem-core/.claude-plugin/plugin.json` (sürüm yükselt) + `CHANGELOG.md`
- Test: `plugins/socius-vigil/tests/test_stub.py`

**Arayüzler:**
- Korunur (kırılmasın diye): `name: brand-market-signal` ve frontmatter'daki **tüm tetikleyici anahtar kelimeler** — mevcut kullanıcı alışkanlığı ve `brand-audit`'in iç atıfları çalışmaya devam eder.
- Korunur: **marka-özel handoff sözleşmesi** — beyaz alan → `brand-maker` naming brief'i. Bu bilgi socius-vigil'de **yoktur**, stub'da kalır.

- [ ] **Adım 1: Testi yaz**

`plugins/socius-vigil/tests/test_stub.py`:

```python
#!/usr/bin/env python3
"""brand-market-signal stub'ı: kırılmadan yönlendiriyor mu. Ağ yok."""
import json
import re
import unittest
from pathlib import Path

BEC = Path(__file__).resolve().parent.parent.parent / "brand-ecosystem-core"
STUB = BEC / "skills/brand-market-signal/SKILL.md"
BODY = STUB.read_text(encoding="utf-8")


class TestKorunanlar(unittest.TestCase):
    def test_isim_degismedi(self):
        self.assertRegex(BODY, r"^---\nname: brand-market-signal\n")

    def test_tetikleyici_kelimeler_korundu(self):
        for kw in ("share-of-voice", "sentiment", "positioning", "white-space"):
            self.assertIn(kw, BODY.lower(), kw)

    def test_brand_maker_handoffu_stubda_kaldi(self):
        self.assertIn("brand-maker", BODY)
        self.assertRegex(BODY, r"(white[- ]space|beyaz alan)")

    def test_fabrikasyon_yasagi_cumlesi_korundu(self):
        self.assertRegex(BODY, r"(uydur|fabricat|no-fabrication)")


class TestStubOlmus(unittest.TestCase):
    def test_otuz_satiri_asmaz(self):
        n = len(BODY.splitlines())
        self.assertLessEqual(n, 30, f"{n} satır — stub değil")

    def test_socius_komutlarina_yonlendiriyor(self):
        self.assertIn("/socius-vigil:rakip", BODY)
        self.assertIn("/socius-vigil:pazar-raporu", BODY)

    def test_kurulu_degilse_ne_yapilacagi_yazili(self):
        self.assertRegex(BODY, r"(kurulu değilse|not installed|kurulum)")


class TestMcpRolu(unittest.TestCase):
    def test_socius_girdisi_kaldi_ve_rol_guncellendi(self):
        srv = json.loads((BEC / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        self.assertIn("socius-vigil", srv)
        role = srv["socius-vigil"]["_role"]
        self.assertNotIn("brand-market-signal skill'inin veri katmanı", role)
        self.assertIn("socius-vigil plugin", role)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/tests/test_stub.py -v
```

Beklenen: `test_otuz_satiri_asmaz` (86 satır), `test_socius_komutlarina_yonlendiriyor` ve `TestMcpRolu` FAIL.

- [ ] **Adım 3: Mevcut frontmatter'ı oku ve anahtar kelimeleri çıkar**

```bash
sed -n '1,20p' plugins/brand-ecosystem-core/skills/brand-market-signal/SKILL.md
```

Frontmatter `description` bloğunu **birebir koru** — yalnız gövdeyi değiştir. Tetikleyici kelime kaybı, kullanıcının alışkın olduğu çağrının sessizce ölmesi demektir.

- [ ] **Adım 4: Gövdeyi stub'a indir**

Frontmatter'ın **altındaki** her şeyi şununla değiştir (frontmatter'a dokunma):

```markdown
# brand-market-signal — yönlendirme

Bu iş artık **socius-vigil plugin'i** tarafından yapılır:

- **Ses payı + konumlandırma + beyaz alan** → `/socius-vigil:rakip`
- **Uçtan uca pazar zekâsı raporu** → `/socius-vigil:pazar-raporu`
- **Yorum/VoC derinleşmesi** → `/socius-vigil:voc`

socius-vigil, aynı `socius-vigil` connector'ını kullanır; bu skill'in yaptığı işi 18 araçlık
yüzey, G1–G16 kapıları ve hook uygulamasıyla yapar.

## socius-vigil kurulu değilse

`brand-audit`'in rakip adımını **gerçek sinyalle** beslemek için plugin'i kur:
`/plugin install socius-vigil@cureonics-marketplace` → sonra `enabledPlugins` doğrula
(kurulum sessizce düşebilir). Kurulmadan bu skill veri **üretmez** — varsayım üretmez de:
sinyal yoksa "sinyal toplanmadı" yazılır, **uydurulmaz**.

## Burada kalan tek şey: marka handoff'u

Beyaz alan bulgusu → `brand-maker` naming brief'i. Eşleme: her beyaz alan, brief'in
"kategori boşluğu" alanına; her karşıt-konumlandırma, "kaçınılacak çağrışım" alanına girer.
Bu sözleşme socius-vigil'de **yoktur** — marka katmanına özgüdür ve burada yaşar.
```

- [ ] **Adım 5: `.mcp.json` `_role` metnini güncelle**

`plugins/brand-ecosystem-core/.mcp.json` → `mcpServers["socius-vigil"]._role` yeni değeri:

```
DESTEK — sosyal dinleme / OSINT sinyal kaynağı. brand-audit'in rakip/kategori adımı bunu opportunistik kullanır. Tam pazar araştırması artık ayrı socius-vigil plugin'inin işidir (/socius-vigil:rakip · :pazar-raporu); buradaki girdi, o plugin kurulu olmasa bile brand-audit'in sinyal çekebilmesi için KALIR.
```

Girdi **silinmez** — stub yokken bile `brand-audit` bu connector'ı kullanabilir.

- [ ] **Adım 6: Sürüm + CHANGELOG**

`plugins/brand-ecosystem-core/.claude-plugin/plugin.json` ve `.codex-plugin/plugin.json` sürümünü bir minör artır (ör. `1.1.3` → `1.2.0`); `CHANGELOG.md` başına:

```markdown
## 1.2.0 — 2026-08-12
- `brand-market-signal` yönlendirme stub'ına indirildi; pazar araştırması işi socius-vigil
  plugin'ine taşındı. Tetikleyici anahtar kelimeler ve brand-maker handoff sözleşmesi korundu.
- `.mcp.json` socius-vigil `_role` metni yeni sınırı anlatacak şekilde güncellendi (girdi kaldı).
```

- [ ] **Adım 7: Testi koş, geçtiğini doğrula**

```bash
python3 plugins/socius-vigil/tests/test_stub.py -v
```

Beklenen: hepsi PASS.

- [ ] **Adım 8: Commit**

```bash
git add plugins/brand-ecosystem-core plugins/socius-vigil/tests/test_stub.py
git commit -m "refactor(brand-ecosystem-core): brand-market-signal → socius-vigil yönlendirme stub'ı (v1.2.0)"
```

---

### Görev 12: Belgeler + marketplace kaydı + kurulum ve uçtan uca doğrulama

**Dosyalar:**
- Oluştur: `plugins/socius-vigil/README.md` · `CONNECTORS.md` · `CHANGELOG.md`
- Değiştir: `.claude-plugin/marketplace.json` (11. plugin kaydı)
- Sil: `~/.claude/skills/socius-vigil/` (bayat v1.2.0 kopya)
- Test: `plugins/socius-vigil/tests/test_marketplace.py`

**Arayüzler:**
- Tüketir: Görev 1–11'in tamamı.
- Üretir: kurulabilir plugin — `/plugin install socius-vigil@cureonics-marketplace`.

- [ ] **Adım 1: Testi yaz**

`plugins/socius-vigil/tests/test_marketplace.py`:

```python
#!/usr/bin/env python3
"""Marketplace kaydı + belge sözleşmesi. Ağ yok."""
import json
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
REPO = PLUGIN.parent.parent
MARKET = json.loads((REPO / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))


def entry():
    return next(p for p in MARKET["plugins"] if p["name"] == "socius-vigil")


class TestMarketplace(unittest.TestCase):
    def test_kayit_var(self):
        self.assertEqual(entry()["source"], "./plugins/socius-vigil")

    def test_surum_manifestle_ayni(self):
        manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(entry()["version"], manifest["version"])

    def test_kategori_ve_anahtar_kelimeler(self):
        e = entry()
        self.assertIn("category", e)
        self.assertGreaterEqual(len(e["keywords"]), 10)


class TestBelgeler(unittest.TestCase):
    def test_uc_belge_var(self):
        for f in ("README.md", "CONNECTORS.md", "CHANGELOG.md"):
            self.assertTrue((PLUGIN / f).exists(), f)

    def test_connectors_her_server_icin_degrade_yazar(self):
        t = (PLUGIN / "CONNECTORS.md").read_text(encoding="utf-8")
        for s in ("socius-vigil", "exa", "tavily", "anamnesis", "tripadvisor",
                  "pubmed-epmc", "consensus", "clinical-trials", "titck", "thoughtspot"):
            self.assertIn(s, t, s)
        self.assertIn("Bağlı değilse", t)

    def test_connectors_quality_gate_veri_akisini_uyarir(self):
        t = (PLUGIN / "CONNECTORS.md").read_text(encoding="utf-8")
        self.assertIn("sv_quality_gate", t)
        self.assertRegex(t, r"(rapor gövdesini|kendi worker)")

    def test_readme_userconfig_tuzagini_yazar(self):
        t = (PLUGIN / "README.md").read_text(encoding="utf-8")
        self.assertIn("ortam değişkeni", t)
        self.assertIn("doppler run", t)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu doğrula**

```bash
python3 plugins/socius-vigil/tests/test_marketplace.py -v
```

Beklenen: `StopIteration` / dosya yok → hepsi FAIL.

- [ ] **Adım 3: `CONNECTORS.md` yaz**

Her satır: **rol · gerekli anahtar · bağlı değilse ne olur** (hangi kapı N/A'ya düşer, hangi metrik `not_provided` olur).

```markdown
# socius-vigil — connector kadrosu

## Çekirdek (otomatik yüklenir — `.mcp.json`)

| Server | Rol | Anahtar | Bağlı değilse |
|---|---|---|---|
| `socius-vigil` | 18 `sv_*` aracı: toplama + deterministik skorlama | `SOCIUS_VIGIL_MCP_API_KEY` | `scripts/*.py` native düşüşü koşar; skor kalitesi düşer, rapor durmaz. **G12** "native düşüş yapıldı" beyanı ZORUNLU olur |
| `exa` | Yorum keşfi + temiz tam-içerik | (opsiyonel) | `sv_fetch` düşüşü daralır; JS-ağır yorum sayfaları alınamaz → ilgili puanlar "JS-kapılı — alınamadı" (G9) |
| `tavily` | Geniş web tarama + extract | `TAVILY_API_KEY` | Kaynak keşfi Exa/web_search ile sınırlı; `references/12` matrisi kısmi doldurulur, §13'te beyan edilir |
| `anamnesis` | Tier-2 bağlam substratı | `ANAMNESIS_MCP_API_KEY` | >30 KB gövdeler bounded-chunk okunur; kapı etkilenmez, bağlam kalitesi düşer |

## Opsiyonel (elle etkinleştirilir — `.mcp.optional.json`)

| Server | Rol | Bağlı değilse |
|---|---|---|
| `tripadvisor` | Otel/seyahat/F&B yorum yüzeyi | **G11** o dikeyde "yorum yüzeyi erişilemedi" ile degrade |
| `pubmed-epmc` | AE klinik plausibility | §10 sinyalleri klinik doğrulamasız; yalnız Admiralty+ACH |
| `consensus` | İddia-kanıt taraması | KOL/marka iddiası "literatür kontrolü yapılmadı" etiketiyle |
| `clinical-trials` | Çalışma-temelli iddia doğrulaması | İddianın çalışma dayanağı doğrulanmaz |
| `titck` | TR ruhsat/fiyat bağlamı | TR SKU doğrulaması manuel; **G10** riski artar ve beyan edilir |
| `thoughtspot` | IQVIA MIDAS → pazar payı (SoM) | **SoM `not_provided` → ESOV HESAPLANMAZ.** Uydurulmaz; §3'te açıkça yazılır |

## Veri akışı uyarısı

`sv_quality_gate` **rapor gövdesini** kullanıcının kendi Cloudflare worker'ına gönderir.
Gizli/müşteri-özel bir rapor denetlenecekse bunu bilerek yapın; alternatif olarak yerel
`scripts/quality_gate_check.py` aynı denetimi ağ olmadan koşar.

## Anahtar sağlama

`.mcp.json` header'ları `${ENV_VAR}` okur. `plugin.json` `userConfig` alanını doldurmak
**tek başına yetmez** — userConfig→env fallback sözdizimi belgelenmemiştir. Kanonik yol:

    doppler run -p cureohub -c dev_personal -- claude
```

- [ ] **Adım 4: `README.md` yaz**

```markdown
# Socius-Vigil — nitelikli pazar araştırması + sosyal dinleme süiti

13 komut · 18 araçlık MCP yüzeyi · G1–G16 kapıları (yedisi hook-uygulamalı) · 3 izole alt-ajan.

## Kurulum

    /plugin marketplace add mahirkurt/CureoPrivate
    /plugin install socius-vigil@cureonics-marketplace

**Kurulumdan sonra MUTLAKA doğrula** — plugin kurulumu sessizce düşebilir:

    /plugin              → socius-vigil "enabled" görünmeli
    /socius-vigil:durum

## Anahtarlar

Değerleri **ortam değişkeni** olarak sağlayın; `userConfig` alanını doldurmak tek başına
`.mcp.json` header'ını beslemez:

    doppler run -p cureohub -c dev_personal -- claude

Anahtarsız da çalışır: her eksik katman native düşüşe iner ve **beyan edilir** (P4).

## Komutlar

| Komut | Ne yapar |
|---|---|
| `/socius-vigil:start` | Oryantasyon: connector kadrosu + mod seçim ağacı |
| `/socius-vigil:durum` | Teşhis: connector canlılığı, 18 araç, skill ayrıklığı |
| `/socius-vigil:pazar-raporu` | Uçtan uca §0–§14 pazar zekâsı raporu |
| `/socius-vigil:hizli-tarama` | Tek çağrılık hacim/sentiment/tema enstantanesi |
| `/socius-vigil:voc` | Müşteri sesi: satın alma sürücüleri ve bariyerleri, Kano |
| `/socius-vigil:rakip` | Ses payı → ESOV, konumlandırma, beyaz alan |
| `/socius-vigil:fiyat` | Değer-fiyat algısı, fiyat şikâyeti madenciliği |
| `/socius-vigil:trend` | Ortaya çıkan temalar, kategori yörüngesi |
| `/socius-vigil:kol` | Profil×duruş matrisi, açıklama etiketi, değerleme |
| `/socius-vigil:perakende` | Yorum madenciliği, puan dağılımı, sahte-yorum sezgisi |
| `/socius-vigil:vijilans` | AE/ICSR triyajı + eskalasyon (WEB-RADR I3) |
| `/socius-vigil:yayin` | Temiz-kopya geçişi: Okuyucu Raporu + Teknik Süreç Eki |

## Neyi vaat etmez

- Resmî farmakovijilans dosyalaması yapmaz (I3 — insan denetimi zorunlu).
- SoM verisi olmadan ESOV hesaplamaz; alınamayan puanı uydurmaz.
- Boş sonucu "yok" diye raporlamaz.

## Geliştirme

    for t in tests/test_*.py hooks/tests/test_*.py; do python3 "$t"; done
    python3 scripts/socius_doctor.py --tools --skills --sections
```

- [ ] **Adım 5: `CHANGELOG.md` yaz**

```markdown
# Değişim günlüğü — socius-vigil plugin

## 1.0.0 — 2026-08-12
İlk sürüm. `socius-vigil.skill` v2.3.0 tek-dosya paketinden plugin'e dönüşüm.

- Flagship protokol **v2.4.0**: araç tablosu 14 → 18; SV-FIX artık-bulgu bloğu kaldırıldı
  (v0.3.1'de ampirik kapandı; defense-in-depth ilke olarak korundu); §12 kapı tablosuna
  "Uygulama" sütunu eklendi.
- **12 mod skill'i** = 12 slash komut; her biri ≤120 satır ve referansları göreli yolla
  çağırır (P1 tek kopya).
- **Hook katmanı:** SessionStart doktrini · `sv_ledger` (G7/G12) · `retrieve_dont_dump`
  (Tier 1/2) · `stop_gates` (G9/G10/G12/G13/G14) · `clean_copy_guard` (G16). Tümü fail-open
  ve meta-tur baskılamalı (P2/P3).
- **Üç izole alt-ajan:** `pazar-tarama-distilleri` · `vijilans-triyaj` · `rapor-denetcisi`.
- `mcp_tool_ledger.schema.json` enum'u 14 → 18 araç (v0.4.0 yüzeyiyle senkronlandı).
- `brand-market-signal` yönlendirme stub'ına indirildi (brand-ecosystem-core v1.2.0).
```

- [ ] **Adım 6: Marketplace kaydını ekle**

`.claude-plugin/marketplace.json` → `plugins` dizisine 11. giriş:

```json
{
  "name": "socius-vigil",
  "displayName": "Socius-Vigil",
  "source": "./plugins/socius-vigil",
  "version": "1.0.0",
  "description": "Nitelikli pazar araştırması + sosyal dinleme/OSINT orkestrasyon süiti — 13 komut, 18 araçlık MCP yüzeyi, hook-uygulamalı G1–G16 kapıları, üç izole alt-ajan.",
  "author": { "name": "Cureonics", "url": "https://cureonics.com" },
  "category": "research",
  "keywords": [
    "social-listening", "sosyal-dinleme", "market-intelligence", "pazar-arastirmasi",
    "share-of-voice", "voice-of-customer", "competitive-positioning", "osint",
    "admiralty-code", "retail-review-mining", "kol-stance", "cosmetovigilance",
    "icsr", "web-radr"
  ],
  "strict": false
}
```

- [ ] **Adım 7: Tüm test paketini koş**

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate
for t in plugins/socius-vigil/tests/test_*.py plugins/socius-vigil/hooks/tests/test_*.py; do
  echo "== $t"; python3 "$t" 2>&1 | tail -2
done
python3 plugins/socius-vigil/scripts/socius_doctor.py
```

Beklenen: sekiz test dosyasının hepsi OK; doctor üç denetimde de temiz.

- [ ] **Adım 8: Plugin doğrulayıcıyı koş**

`plugin-dev:plugin-validator` alt-ajanını `plugins/socius-vigil` üzerinde çalıştır.
Beklenen: temiz. Bulgu varsa düzelt ve tekrar koş.

- [ ] **Adım 9: Belgeleri commit'le**

```bash
git add plugins/socius-vigil/README.md plugins/socius-vigil/CONNECTORS.md \
        plugins/socius-vigil/CHANGELOG.md plugins/socius-vigil/tests/test_marketplace.py \
        .claude-plugin/marketplace.json
git commit -m "docs(socius-vigil): README + CONNECTORS + CHANGELOG + marketplace kaydı"
```

- [ ] **Adım 10: Kur ve kurulumu DOĞRULA (sessiz düşme tuzağı)**

Claude Code'da:

    /plugin marketplace update cureonics-marketplace
    /plugin install socius-vigil@cureonics-marketplace
    /plugin                      → "enabled" teyidi ZORUNLU

Kurulum sessizce düşebilir — `enabledPlugins` listesinde görmeden "kuruldu" deme.

- [ ] **Adım 11: Bayat kopyayı kaldır**

```bash
ls ~/.claude/skills/socius-vigil     # v1.2.0 (11 Haziran) — plugin bunu ikame eder
rm -rf ~/.claude/skills/socius-vigil
```

İki kopya aynı anda yüklüyse tetikleyiciler çakışır ve model eski protokolü okuyabilir.

- [ ] **Adım 12: Canlı oryantasyon + uçtan uca eval**

    /socius-vigil:durum

Beklenen: 4 çekirdek connector, **18 araç**, skill ayrıklığı temiz, degrade yolları doğru.

Sonra referans vaka (`skills/socius-vigil/evals/bioderma_atoderm_creme_fr.md`):

    /socius-vigil:pazar-raporu Bioderma Atoderm Crème (FR pazarı)
    /socius-vigil:yayin

Ardından `rapor-denetcisi` alt-ajanını çağır. **Geçme ölçütü:** Okuyucu Raporu ile Teknik
Süreç Eki ayrık üretiliyor; `sv_quality_gate --profile clean` `blocking_failures` **boş**;
`clean_copy_guard` sızıntı bildirmiyor; `stop_gates` kapı eksiği bildirmiyor.

- [ ] **Adım 13: Kapanış commit'i**

```bash
git add plugins/socius-vigil plugins/brand-ecosystem-core .claude-plugin/marketplace.json
git commit -m "chore(socius-vigil): v1.0.0 kurulum doğrulaması + bayat skill kopyası emekli"
```

---

## Kendi kendine denetim (planı yazan yaptı)

**Spec kapsaması.** §3 dizin yapısı → Görev 1; §4 skill dekompozisyonu → Görev 9; §5
SKILL.md değişiklikleri → Görev 2; §6 alt-ajanlar → Görev 10; §7 hook katmanı → Görev 4–8;
§7.1 tetikleme imzaları → Görev 4 (`_signals.meta_turn`, mutasyon-denetimli testler) +
Görev 7/8'in `TestP3MetaTur` sınıfları; §8 MCP kablolaması → Görev 1; §9 brand-market-signal
→ Görev 11; §10 doğrulama kapıları → Görev 3 (doctor), Görev 12 (validator, kurulum, eval,
bayat kopya); §11 riskler → ilgili görevlerin degrade/test adımlarına dağıtıldı; §12 kapsam
dışı → plana **alınmadı** (MCP sunucu kodu, yeni çerçeve icadı, carbon render entegrasyonu,
Firecrawl connector'ı, public marketplace yayını).

**Spec'te olup planda karşılığı olmayan tek kalem:** `.codex-plugin/openai.yaml` — repo
emsalinde böyle bir dosya yok; Global Kısıtlar'da sapma olarak beyan edildi.

**Planın spec'e eklediği iki ölçülmüş düzeltme:** (1) `mcp_tool_ledger.schema.json` enum'u
14 araçta donmuş — Görev 5 Adım 4 onu 18'e çıkarır; (2) spec'in verdiği
`brand-ecosystem-core/.mcp.optional.json` yolu yanlış — Görev 11 gerçek dosyayı (`.mcp.json`)
hedefler.

**Tip tutarlılığı.** `TOOL_NAMES` tek yerde tanımlı (`scripts/socius_doctor.py`) ve üç
yerden import ediliyor (`sv_ledger.py`, `stop_gates.py`, testler). Görev 4'te ilan edilen
yardımcı imzalar Görev 5–8'de birebir aynı adlarla çağrılıyor: `read_payload` ·
`transcript_text` · `report_signature` · `meta_turn` · `emit_block` · `emit_context` ·
`env_present` · `ledger_path` · `read_ledger` · `append_ledger` · `sv_tool_invoked` ·
`transcript_available`.

**Bilinen sıra bağımlılığı.** Görev 3'ün iki testi Görev 9'a kadar `skip` işaretlidir
(13 skill henüz yok). Görev 9 Adım 5 bu işaretleri kaldırır — atlanırsa ayrıklık denetimi
sessizce koşmaz.
