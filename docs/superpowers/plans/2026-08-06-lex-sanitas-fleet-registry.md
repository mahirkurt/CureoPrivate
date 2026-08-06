# lex-sanitas v3.5.0 — Türetilmiş Filo (Fleet Registry) Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** lex-sanitas'ın MCP filosunu tek bir `fleet.yaml` kaynağından türetilir hâle getirmek; canlı prob'lu preflight ekleyerek titck sınıfı sessiz arızaları imkânsız kılmak; filoyu 15→19 server'a genişletmek.

**Architecture:** `fleet.yaml` (elle yazılan tek kaynak) → `tools/gen_fleet.py` → `.mcp.json` + `.codex-plugin/plugin.json` + `fleet.lock.json` + `⟨GEN⟩` işaretli belge blokları. `tools/check_drift.py` CI kapısı olarak türetilmiş≠commit'li ve düzyazı-sayı≠gerçek hâllerini yakalar. Hook'lar `fleet.lock.json` (stdlib json) okur, PyYAML'a bağımlı değildir. `hooks/scripts/fleet_probe.py` gerçek MCP `initialize` prob'u yapar ve `auth_missing` ile `unauthorized`'ı ayırır.

**Tech Stack:** Python 3.12 stdlib (json, urllib.request, concurrent.futures, argparse, re, pathlib) + PyYAML (yalnız üretici/checker; hook'lar için değil). Test: `python3` ile doğrudan koşulan `hooks/test_hooks.py`; davranışsal testler YAML senaryosu.

## Global Constraints

- **Dil:** tüm kod yorumları, docstring'ler, üretilen düzyazı ve commit mesajları **Türkçe**.
- **Hook bağımlılığı:** `hooks/scripts/*.py` **yalnız stdlib** kullanır. PyYAML import edilmez.
- **Fail-open:** hiçbir hook oturumu bloklamaz, hiçbir MCP çağrısı engellenmez. Her istisna → exit 0.
- **No-fabrication korunur:** erişilemeyen katman veri boşluğu olarak işaretlenir; asla doldurulmaz.
- **Üretilmiş dosyalara elle dokunulmaz:** `.mcp.json`, `fleet.lock.json` ve `⟨GEN⟩` blokları yalnız `gen_fleet.py` tarafından yazılır. Her üretilmiş dosya başında `"_generated"` uyarısı taşır.
- **`⟨GEN⟩` işaret sözdizimi:** markdown'da `<!-- GEN:<ad> BEGIN -->` … `<!-- GEN:<ad> END -->`.
- **Filo sayıları:** 19 server (16 gated + 3 public), 5 companion, 2 delegasyon. Hiçbir yere elle yazılmaz; `counts`'tan gelir veya `check_drift.py` doğrular.
- **Sürüm:** 3.4.0 → **3.5.0** (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `SKILL.md` frontmatter, `marketplace.json`).
- **Çalışma dizini:** tüm yollar `/mnt/thunderbolt/workspaces/CureoPrivate` köküne görelidir. Plugin kökü: `plugins/lex-sanitas/`.
- **Commit:** main üzerinde, mantıksal ayrık, **push edilmez**.

---

## Dosya Yapısı

| Dosya | Sorumluluk | Durum |
|---|---|---|
| `plugins/lex-sanitas/fleet.yaml` | Filonun tek gerçek kaynağı: 19 server + 5 companion + 2 delegasyon | **Yeni** |
| `plugins/lex-sanitas/fleet.lock.json` | Hook'ların okuduğu stdlib-türev; `role`/`tools_used` içermez | **Yeni (üretilir)** |
| `plugins/lex-sanitas/tools/gen_fleet.py` | Üretici: lock + `.mcp.json` + codex bloğu + `⟨GEN⟩` blokları | **Yeni** |
| `plugins/lex-sanitas/tools/check_drift.py` | CI kapısı: yeniden-üret+diff, düzyazı sayı taraması, şema denetimi | **Yeni** |
| `plugins/lex-sanitas/hooks/scripts/fleet_probe.py` | Canlı MCP prob'u + 24s cache; kütüphane ve CLI | **Yeni** |
| `plugins/lex-sanitas/.mcp.json` | 19 server wiring | Üretilir (titck auth fix burada) |
| `plugins/lex-sanitas/.codex-plugin/plugin.json` | `mcpServers` bloğu üretilir; gerisi elle | Değiştirilir |
| `plugins/lex-sanitas/hooks/scripts/session_start.py` | Lock + prob tüketen preflight | Yeniden yazılır |
| `plugins/lex-sanitas/hooks/scripts/stop_coverage.py` | `MANDATORY_ROWS` lock'tan türer (7 satır) | Değiştirilir |
| `plugins/lex-sanitas/hooks/test_hooks.py` | Birim testler (mevcut + fleet_probe + türetim) | Genişletilir |
| `plugins/lex-sanitas/agents/*.md` | `tools:` satırı `⟨GEN⟩` bloğu | Değiştirilir (4 dosya) |
| `plugins/lex-sanitas/commands/lex-connectors.md` | Canlı prob raporu + `⟨GEN⟩` anahtar tablosu | Yeniden yazılır |
| `plugins/lex-sanitas/hooks.json` (kök) | — | **Silinir** |
| `plugins/lex-sanitas/tests/fleet_registry_tests.yaml` | Davranışsal filo testleri | **Yeni** |
| `plugins/lex-sanitas/skills/lex-sanitas/SKILL.md` | §3/§4 filo düzyazısı + sürüm | Değiştirilir |
| `plugins/lex-sanitas/README.md` | Filo tablosu + mimari ağacı | Değiştirilir |
| `plugins/lex-sanitas/skills/lex-sanitas/references/00-mod-pipelines.md` | `⟨GEN⟩` mod×server bloğu | Değiştirilir |
| `plugins/lex-sanitas/tests/*.yaml` (mevcut 6) | 14→19, companion 6→5 | Değiştirilir |
| `.claude-plugin/marketplace.json` | lex-sanitas 3.5.0 | Değiştirilir |

---

## Task 1: Fleet registry + üretici

**Files:**
- Create: `plugins/lex-sanitas/fleet.yaml`
- Create: `plugins/lex-sanitas/tools/gen_fleet.py`
- Create: `plugins/lex-sanitas/fleet.lock.json` (üretilir)
- Test: `plugins/lex-sanitas/tools/test_gen_fleet.py`

**Interfaces:**
- Produces: `gen_fleet.load_fleet(root: Path) -> dict` — `fleet.yaml`'ı okur ve şema-doğrular.
- Produces: `gen_fleet.build_lock(fleet: dict) -> dict` — lock gövdesi (`counts`, `servers`, `companions`, `delegations`).
- Produces: `gen_fleet.build_mcp_servers(fleet: dict) -> dict` — `.mcp.json`'ın `mcpServers` bloğu.
- Produces: `gen_fleet.main(argv) -> int` — CLI; `--check` yazmadan diff döndürür.

- [ ] **Step 1: `fleet.yaml`'ı yaz**

19 server. `role` metinleri mevcut `.mcp.json`'dan **birebir taşınır** (titck ve health-policy'ninki düzeltilir), 4 yeni server için yeni yazılır.

```yaml
# lex-sanitas MCP filosunun TEK GERÇEK KAYNAĞI.
# .mcp.json · .codex-plugin/plugin.json · fleet.lock.json · commands/lex-connectors.md
# · agents/*.md tools: satırı · references/00-mod-pipelines.md ⟨GEN⟩ blokları
# BU DOSYADAN ÜRETİLİR. Onları elle düzenleme — burayı düzenle, sonra:
#   python3 tools/gen_fleet.py
version: 1
plugin: lex-sanitas
plugin_version: "3.5.0"

servers:
  - name: mevzuat
    url: https://mevzuat.cureonics.com/mcp
    tier: primary
    auth_env: MEVZUAT_MCP_API_KEY
    shard: S1
    modes: [ALL]
    gate: null
    tools_used: [search_mevzuat, get_mevzuat_madde_tree, get_mevzuat_madde_diff,
                 get_mevzuat_timeline, get_mevzuat_relations, get_mevzuat_gerekce,
                 get_anayasa, get_onceki_metinler, search_mulga_mevzuat,
                 build_mevzuat_semantic_context, resolve_resmi_gazete]
    role: >-
      PRİMER TR mevzuat — in-house HP self-host (v0.14.x, SQLite/FTS5 cache).
      Yapısal yasama-grafı: get_mevzuat_madde_tree/madde_diff (as_of tarihli) +
      get_mevzuat_timeline + ilga_zinciri/get_mevzuat_relations (NLP dayanak/atıf
      kenarları) + get_mevzuat_gerekce (LOCATOR) + semantik-bağlam recall-boost.
      Tüm modların TR-mevzuat omurgası. Arama KEYWORD tabanlı ('katma değer
      vergisi', '3065' DEĞİL).
    degrade: >-
      Anahtar yoksa TR-mevzuat omurgası düşer; mevzuat-bilgisi ikincil korpusuna
      degrade + manifestoda 'skipped: anahtar yok'. Üst-norm zinciri kurulamazsa
      G2 CONDITIONAL.
```

Kalan 18 server aynı şemayla. Özet tablo (tam `role`/`degrade` metinleri Step 1'de yazılır):

| name | url | tier | auth_env | shard | modes | gate |
|---|---|---|---|---|---|---|
| mevzuat | mevzuat.cureonics.com | primary | `MEVZUAT_MCP_API_KEY` | S1 | ALL | — |
| mevzuat-bilgisi | mevzuat.surucu.dev | secondary | `null` | S1 | ALL | — |
| resmi-gazete | resmi-gazete-mcp.cureonics.workers.dev | primary | `RESMI_GAZETE_MCP_API_KEY` | S1 | ALL | — |
| titck | titck.cureonics.com | primary | `TITCK_MCP_API_KEY` | S1 | ALL | — |
| tbmm | tbmm.cureonics.com | primary | `TBMM_MCP_API_KEY` | S1 | ALL | — |
| saglikbakanligi | saglik-mcp.cureonics.com | primary | `SAGLIK_BAKANLIGI_MCP_API_KEY` | S1 | ALL | — |
| detsis | detsis.cureonics.com | support | `DETSIS_MCP_API_KEY` | S1 | ALL | — |
| health-policy | health-policy-mcp.cureonics.workers.dev | comparative | `HEALTH_POLICY_MCP_API_KEY` | S2 | ALL | — |
| german-law | german-law.cureonics.com | comparative | `GERMAN_LAW_MCP_API_KEY` | S2 | ALL | G6 |
| ich-guidelines | ich.cureonics.com | comparative | `ICH_MCP_API_KEY` | S2 | ALL | G6 |
| intl-treaty | intl-treaty-mcp.cureonics.workers.dev | comparative | `INTL_TREATY_MCP_API_KEY` | S2 | ALL | G6 |
| eudamed | eudamed-mcp.cureonics.workers.dev | comparative | `EUDAMED_MCP_MCP_API_KEY` | S2 | ALL | — |
| oecd | oecd.cureonics.com | support | `OECD_MCP_API_KEY` | S2 | ALL | — |
| yok-akademik | yok-akademik.cureonics.com | doctrine | `YOK_AKADEMIK_MCP_API_KEY` | S3 | ALL | G5 |
| **yoktez** | yoktezmcp.fastmcp.app | doctrine | `null` | S3 | ALL | **G7** |
| **literatur** | literatur-mcp.surucu.dev | doctrine | `null` | S3 | ALL | G5 |
| **openathens** | openathens.cureonics.com | fulltext | `OPENATHENS_MCP_API_KEY` | S4 | ALL | G6 |
| **annas-reader** | annas.cureonics.com | fulltext | `ANNAS_MCP_API_KEY` | S4 | ALL | G6 |
| anamnesis | anamnesis-mcp.cureonics.workers.dev | substrate | `ANAMNESIS_MCP_API_KEY` | ALL | ALL | — |

Yeni dört server'ın `role`/`degrade` metinleri:

```yaml
  - name: yoktez
    url: https://yoktezmcp.fastmcp.app/mcp
    tier: doctrine
    auth_env: null
    shard: S3
    modes: [ALL]
    gate: G7
    tools_used: [search_yok_tez_detailed, get_yok_tez_thesis_details,
                 get_yok_tez_document_markdown, search_yok_tez_by_anabilim_dali]
    role: >-
      YÖK Ulusal Tez Merkezi tam-metin — tez-düzeyi Türk hukuk/tıp doktrini
      (gerekçe akademik dayanağı, ANALYZE doktrin taraması) + G7 YÖK-Tez ATIF
      DOĞRULAMASI (tez no/başlık/yazar teyidi → uydurma tez atfı deterministik
      yakalanır). yok-akademik profil-metadata'sının tam-metin tamamlayıcısı.
      Authless (FastMCP remote). v3.5.0'da companion'dan first-class'a terfi etti.
    degrade: >-
      Erişilemezse tez-doktrin yok-akademik metadata'sına degrade eder ve G7'deki
      YÖK-Tez atıf doğrulaması yapılamaz → bu tip atıflar
      'illustrative_placeholder_not_verified' etiketlenir, KULLANILMAZ.

  - name: literatur
    url: https://literatur-mcp.surucu.dev/mcp
    tier: doctrine
    auth_env: null
    shard: S3
    modes: [ALL]
    gate: G5
    tools_used: [search_articles, pdf_to_html, get_article_references]
    role: >-
      DergiPark Türk akademik dergi makaleleri — arama (yıl/tür/dizin/sıralama) +
      PDF→HTML TAM METİN + referans çekme. Doktrin katmanının tek OKUNABİLİR TR
      kaynağı: yok-akademik yalnız metadata verir, bu tam metin verir. Gerekçe
      akademik dayanağı + ANALYZE doktrin taraması. Authless (surucu.dev).
    degrade: >-
      Erişilemezse doktrin katmanı metadata-only'ye (yok-akademik) düşer;
      gerekçede doktrin atfı yapılabilir ama içerik alıntılanamaz → manifestoda
      'degraded: tam metin yok'.

  - name: openathens
    url: https://openathens.cureonics.com/mcp
    tier: fulltext
    auth_env: OPENATHENS_MCP_API_KEY
    shard: S4
    modes: [COMPARATIVE_LAW, ANALYZE, RIA, EX_POST_EVALUATION, OPINE]
    gate: G6
    tools_used: [oa_session_status, oa_resolve, oa_fetch_fulltext, oa_list_databases]
    role: >-
      LİSANSLI kurumsal tam-metin kapısı (Tier 3) — Millet Kütüphanesi/OpenAthens
      SAML üzerinden 309 lisanslı veritabanı. Yabancı hukuk doktrini (monograf,
      hakemli makale) için paywall'lı kaynaklara YASAL erişim. Mod 7 karşılaştırmalı
      analizin ve G6 uluslararası kaynak teyidinin doktrin desteği (birincil norm
      metni DEĞİL — o health-policy/german-law/Open Law'dadır).
    degrade: >-
      Oturum düşük/anahtar yoksa manifestoda 'degraded: lisanslı band kapalı'.
      ŞELALE DİSİPLİNİ: openathens'in yokluğu annas-reader'ı OTOMATİK AÇMAZ —
      son çare yalnız openathens denendikten sonra ve açık gerekçeyle kullanılır.

  - name: annas-reader
    url: https://annas.cureonics.com/mcp
    tier: fulltext
    auth_env: ANNAS_MCP_API_KEY
    shard: S4
    modes: [COMPARATIVE_LAW, ANALYZE]
    gate: G6
    tools_used: [book_search, article_search, get_document_info, read_document,
                 search_in_document]
    role: >-
      SON-ÇARE tam-metin (Tier 4, efemer-RAG reader) — lisanslı band (openathens
      Tier 3) getiremeyince. Out-of-print hukuk monografı, erişilemeyen yabancı
      doktrin. YALNIZ ANALİZ İÇİN: getirilen tam metin yeniden yayımlanmaz,
      çıktıya gövde olarak kopyalanmaz; yalnız atıf + damıtılmış bulgu üretir.
    degrade: >-
      Erişilemezse ilgili doktrin satırı 'manual_required' (kaynak künyesi +
      erişim yolu) yazılır — asla uydurma içerik.
```

Companion ve delegasyon blokları:

```yaml
companions:
  - name: Yargı
    tool_prefixes: ["mcp__Yarg__", "mcp__claude_ai_Yarg__"]
    gate: G5
    modes: [ALL]
    manifest_row: "Yargı (companion — G5 içtihat)"
    degrade: "G5 en fazla CONDITIONAL — AYM/Danıştay/Yargıtay zinciri doğrulanamaz"
  - name: Open Law
    tool_prefixes: ["mcp__Open_Law__", "mcp__claude_ai_Open_Law__"]
    gate: G6
    modes: [ALL]
    manifest_row: "Open Law (companion — G6 CELEX)"
    degrade: "CELEX doğrulaması german-law get_eu_basis→WebFetch'e degrade; G6 CONDITIONAL"
  - name: Ansvar
    tool_prefixes: ["mcp__Ansvar__", "mcp__claude_ai_Ansvar__"]
    gate: null
    modes: [COMPARATIVE_LAW, ANALYZE, RIA]
    manifest_row: "Ansvar (companion — Mod7 58-yargı)"
    degrade: "CH/FR/IT/NL/SE/DK/FI/AT/PL satırları manual_required + kapsam boşluğu beyanı"
  - name: Fedlex Swiss
    tool_prefixes: ["mcp__Fedlex_Swiss__", "mcp__claude_ai_Fedlex_Swiss__"]
    gate: null
    modes: [COMPARATIVE_LAW]
    manifest_row: "Fedlex Swiss (companion — Mod7 CH birincil metin)"
    degrade: "CH birincil-metin satırı Ansvar çerçeve-taramasına degrade + manual_required"
  - name: Türk Patent
    tool_prefixes: ["mcp__T_rk_Patent__", "mcp__claude_ai_T_rk_Patent__"]
    gate: null
    modes: [DRAFT, RIA, COMPARATIVE_LAW]
    manifest_row: "Türk Patent (companion — IP/SPC/veri imtiyazı)"
    degrade: "IP-boyutlu satır manual_required (TÜRKPATENT portal deep-link)"

delegations:
  - name: evidentia
    plugin_id_prefix: "evidentia@"
    trigger: "klinik boyut (ilaç/cihaz/hastalık/tedavi/klinik-çalışma/geri-ödeme)"
    manifest_row: "evidentia (klinik delegasyon)"
    degrade: "Kurulu değilse klinik iddialar unverified; manifestoda 'skipped: plugin kurulu değil'"
  - name: sci-audit
    plugin_id_prefix: "sci-audit@"
    trigger: "her reform-modu çıktısı"
    manifest_row: "sci-audit (çıktı-QA delegasyonu)"
    degrade: "Kurulu değilse çıktı-QA manuel; atıf-adli + TR imla taraması yapılmaz"
```

- [ ] **Step 2: `tools/test_gen_fleet.py`'yi yaz (başarısız test)**

```python
#!/usr/bin/env python3
"""gen_fleet üretici birim testleri — stdlib unittest, ağ erişimi YOK."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_fleet  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class TestFleetRegistry(unittest.TestCase):
    def setUp(self):
        self.fleet = gen_fleet.load_fleet(ROOT)

    def test_fleet_sunucu_sayisi(self):
        self.assertEqual(len(self.fleet["servers"]), 19)
        self.assertEqual(len(self.fleet["companions"]), 5)
        self.assertEqual(len(self.fleet["delegations"]), 2)

    def test_titck_auth_zorunlu(self):
        """2026-08-02 kapılanması: titck ARTIK public değil."""
        titck = next(s for s in self.fleet["servers"] if s["name"] == "titck")
        self.assertEqual(titck["auth_env"], "TITCK_MCP_API_KEY")

    def test_health_policy_kanonik_env(self):
        hp = next(s for s in self.fleet["servers"] if s["name"] == "health-policy")
        self.assertEqual(hp["auth_env"], "HEALTH_POLICY_MCP_API_KEY")

    def test_yoktez_companion_degil(self):
        """yoktez v3.5.0'da first-class wire; companion listesinde OLMAMALI."""
        names = {s["name"] for s in self.fleet["servers"]}
        comp = {c["name"] for c in self.fleet["companions"]}
        self.assertIn("yoktez", names)
        self.assertFalse(names & comp, "wire'lı server companion olamaz")

    def test_lock_sayilari(self):
        lock = gen_fleet.build_lock(self.fleet)
        self.assertEqual(lock["counts"]["servers"], 19)
        self.assertEqual(lock["counts"]["gated"], 16)
        self.assertEqual(lock["counts"]["public"], 3)
        self.assertEqual(lock["counts"]["companions"], 5)

    def test_lock_role_metnini_tasimaz(self):
        """Lock hook'lar içindir; düzyazı şişirmez."""
        lock = gen_fleet.build_lock(self.fleet)
        for s in lock["servers"]:
            self.assertNotIn("role", s)
            self.assertNotIn("tools_used", s)

    def test_mcp_json_auth_header_uretimi(self):
        mcp = gen_fleet.build_mcp_servers(self.fleet)
        self.assertEqual(
            mcp["titck"]["headers"]["Authorization"], "Bearer ${TITCK_MCP_API_KEY}"
        )
        self.assertNotIn("headers", mcp["yoktez"], "public server header taşımaz")

    def test_sema_dogrulama_bozuk_tier_reddeder(self):
        bad = {"version": 1, "plugin": "x", "plugin_version": "1",
               "servers": [{"name": "a", "url": "https://a/mcp", "tier": "UYDURMA",
                            "auth_env": None, "shard": "S1", "modes": ["ALL"],
                            "gate": None, "tools_used": [], "role": "r", "degrade": "d"}],
               "companions": [], "delegations": []}
        with self.assertRaises(ValueError):
            gen_fleet.validate_fleet(bad)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Testi koştur, başarısız olduğunu doğrula**

Run: `cd plugins/lex-sanitas && python3 tools/test_gen_fleet.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'gen_fleet'`

- [ ] **Step 4: `tools/gen_fleet.py`'yi yaz**

```python
#!/usr/bin/env python3
"""lex-sanitas filo üreticisi — fleet.yaml'dan tüm türev artefaktları üretir.

Üretilenler:
  fleet.lock.json                      hook'ların okuduğu stdlib-türev
  .mcp.json                            Claude Code MCP wiring
  .codex-plugin/plugin.json            mcpServers bloğu (yerinde değiştirilir)
  commands/lex-connectors.md           ⟨GEN⟩ anahtar tablosu
  agents/*.md                          ⟨GEN⟩ tools: satırı
  skills/.../references/00-mod-pipelines.md  ⟨GEN⟩ mod×server bloğu

Kullanım:
  python3 tools/gen_fleet.py            üret ve yaz
  python3 tools/gen_fleet.py --check    yazma; fark varsa exit 1 (CI kapısı)
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

TIERS = {"primary", "secondary", "comparative", "support",
         "doctrine", "fulltext", "substrate"}
SHARDS = {"S1", "S2", "S3", "S4", "ALL"}
MODES = {"ALL", "DRAFT", "AMEND", "ANALYZE", "COMPLY", "OPINE", "RIA",
         "COMPARATIVE_LAW", "TBMM_KANUN_TEKLIFI", "EX_POST_EVALUATION"}
GATES = {None, "G5", "G6", "G7"}

SERVER_KEYS = {"name", "url", "tier", "auth_env", "shard", "modes",
               "gate", "tools_used", "role", "degrade"}

GEN_WARNING = ("ÜRETİLMİŞ DOSYA — elle düzenlemeyin. Kaynak: fleet.yaml → "
               "python3 tools/gen_fleet.py")


def load_fleet(root: Path) -> dict:
    """fleet.yaml'ı okur ve şema-doğrular."""
    fleet = yaml.safe_load((root / "fleet.yaml").read_text(encoding="utf-8"))
    validate_fleet(fleet)
    return fleet


def validate_fleet(fleet: dict) -> None:
    """Şema ihlallerinde ValueError fırlatır — sessiz bozuk üretim olmaz."""
    for key in ("version", "plugin", "plugin_version", "servers",
                "companions", "delegations"):
        if key not in fleet:
            raise ValueError(f"fleet.yaml: '{key}' alanı eksik")

    seen = set()
    for s in fleet["servers"]:
        missing = SERVER_KEYS - set(s)
        if missing:
            raise ValueError(f"server {s.get('name')!r}: eksik alan(lar) {sorted(missing)}")
        if s["name"] in seen:
            raise ValueError(f"server adı tekrarlı: {s['name']}")
        seen.add(s["name"])
        if s["tier"] not in TIERS:
            raise ValueError(f"{s['name']}: geçersiz tier {s['tier']!r}")
        if s["shard"] not in SHARDS:
            raise ValueError(f"{s['name']}: geçersiz shard {s['shard']!r}")
        if s["gate"] not in GATES:
            raise ValueError(f"{s['name']}: geçersiz gate {s['gate']!r}")
        if not set(s["modes"]) <= MODES:
            raise ValueError(f"{s['name']}: geçersiz mod(lar) {set(s['modes']) - MODES}")
        if not s["url"].endswith("/mcp"):
            raise ValueError(f"{s['name']}: url '/mcp' ile bitmeli")

    comp = {c["name"] for c in fleet["companions"]}
    if seen & comp:
        raise ValueError(f"wire'lı server companion olamaz: {sorted(seen & comp)}")


def build_lock(fleet: dict) -> dict:
    """Hook'ların okuduğu stdlib-türev — role/tools_used/degrade taşımaz."""
    servers = [
        {k: s[k] for k in ("name", "url", "tier", "auth_env", "shard", "modes", "gate")}
        for s in fleet["servers"]
    ]
    gated = sum(1 for s in servers if s["auth_env"])
    return {
        "_generated": GEN_WARNING,
        "plugin_version": fleet["plugin_version"],
        "counts": {
            "servers": len(servers),
            "gated": gated,
            "public": len(servers) - gated,
            "companions": len(fleet["companions"]),
            "delegations": len(fleet["delegations"]),
        },
        "servers": servers,
        "companions": fleet["companions"],
        "delegations": fleet["delegations"],
    }


def _squash(text: str) -> str:
    """YAML katlanmış blokların satır sonlarını tek boşluğa indirger."""
    return " ".join(text.split())


def build_mcp_servers(fleet: dict) -> dict:
    """`.mcp.json`/codex için mcpServers bloğu."""
    out = {}
    for s in fleet["servers"]:
        entry = {"type": "http", "url": s["url"]}
        if s["auth_env"]:
            entry["headers"] = {"Authorization": "Bearer ${%s}" % s["auth_env"]}
        entry["_tier"] = s["tier"]
        entry["_role"] = _squash(s["role"])
        out[s["name"]] = entry
    return out
```

Devamı (üretim yardımcıları) aynı dosyada:

```python
def build_mcp_json(fleet: dict) -> dict:
    lock_counts = build_lock(fleet)["counts"]
    comment = (
        f"{GEN_WARNING} — lex-sanitas MCP wiring. TAM-FİLO İLKESİ: "
        f"{lock_counts['servers']} server'ın TAMAMI her sorguda devreye alınır (G0 kapsam "
        f"kapısı). PRİMER/İKİNCİL etiketi aktivasyon kapısı DEĞİL, sentezde otorite "
        f"önceliğidir. Ağır getirim distiller alt-ajanlarında toplanır "
        f"(retrieve-don't-dump). {lock_counts['gated']} server Bearer-gated, "
        f"{lock_counts['public']} public. Anahtar yoksa SessionStart preflight uyarır ve "
        f"o katman graceful degrade eder. {lock_counts['companions']} companion "
        f"(Yargı/Open Law/Ansvar/Fedlex Swiss/Türk Patent) claude.ai connector'ıdır — "
        f"wire edilemez; bkz. commands/lex-connectors.md."
    )
    return {"_comment": comment, "mcpServers": build_mcp_servers(fleet)}


def replace_gen_block(text: str, name: str, body: str) -> str:
    """<!-- GEN:name BEGIN --> … <!-- GEN:name END --> arasını değiştirir."""
    begin, end = f"<!-- GEN:{name} BEGIN -->", f"<!-- GEN:{name} END -->"
    pattern = re.compile(
        re.escape(begin) + r".*?" + re.escape(end), re.DOTALL
    )
    if not pattern.search(text):
        raise ValueError(f"⟨GEN⟩ bloğu bulunamadı: {name}")
    return pattern.sub(f"{begin}\n{body}\n{end}", text)


def env_table(fleet: dict) -> str:
    rows = ["| Server | Tier | Env-var (Doppler → Bearer) |", "|---|---|---|"]
    for s in fleet["servers"]:
        env = f"`{s['auth_env']}`" if s["auth_env"] else "_(public — anahtar yok)_"
        rows.append(f"| `{s['name']}` | {s['tier']} | {env} |")
    for c in fleet["companions"]:
        rows.append(f"| {c['name']} | companion | _(claude.ai connector — env anahtarı yok)_ |")
    return "\n".join(rows)


def agent_tools_line(fleet: dict, shards: list[str], extra: list[str],
                     companions: bool) -> str:
    names = [s["name"] for s in fleet["servers"]
             if s["shard"] in shards or s["shard"] == "ALL"]
    tools = [f"mcp__{n}__*" for n in names]
    if companions:
        tools += [f"{p}*" for c in fleet["companions"] for p in c["tool_prefixes"]]
    return "tools: " + ", ".join(extra + tools)
```

- [ ] **Step 5: Testi koştur, geçtiğini doğrula**

Run: `cd plugins/lex-sanitas && python3 tools/test_gen_fleet.py -v`
Expected: 8 test PASS

- [ ] **Step 6: Üreticiyi koştur, lock'u üret**

Run: `cd plugins/lex-sanitas && python3 tools/gen_fleet.py`
Expected: `fleet.lock.json` yazıldı; `counts.servers=19, gated=16, public=3`

Doğrula: `python3 -c "import json;d=json.load(open('fleet.lock.json'));print(d['counts'])"`

- [ ] **Step 7: Commit**

```bash
git add plugins/lex-sanitas/fleet.yaml plugins/lex-sanitas/fleet.lock.json \
        plugins/lex-sanitas/tools/gen_fleet.py plugins/lex-sanitas/tools/test_gen_fleet.py
git commit -m "feat(lex-sanitas): fleet.yaml tek kaynak + üretici (19 server)"
```

---

## Task 2: `.mcp.json` + codex bloğu üretimi (titck arızası burada kapanır)

**Files:**
- Modify: `plugins/lex-sanitas/tools/gen_fleet.py` (yazma yolları + `main`)
- Modify: `plugins/lex-sanitas/.mcp.json` (üretilir)
- Modify: `plugins/lex-sanitas/.codex-plugin/plugin.json` (`mcpServers` bloğu)
- Test: `plugins/lex-sanitas/tools/test_gen_fleet.py` (genişletilir)

**Interfaces:**
- Consumes: Task 1'in `load_fleet`, `build_mcp_json`, `build_mcp_servers`.
- Produces: `gen_fleet.write_all(root, fleet, check=False) -> list[str]` — değişen dosya yollarının listesi.

- [ ] **Step 1: Başarısız testi ekle**

```python
    def test_mcp_json_uretilen_ile_commitli_ayni(self):
        """CI kapısının çekirdeği: diskteki .mcp.json üretilenle birebir olmalı."""
        expected = gen_fleet.build_mcp_json(self.fleet)
        actual = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_codex_mcpservers_ayni(self):
        codex = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(codex["mcpServers"], gen_fleet.build_mcp_servers(self.fleet))

    def test_codex_diger_alanlar_korunur(self):
        codex = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertIn("interface", codex)
        self.assertEqual(codex["interface"]["displayName"], "Lex Sanitas")
```

- [ ] **Step 2: Testi koştur, başarısız olduğunu doğrula**

Run: `python3 tools/test_gen_fleet.py -v -k mcp_json`
Expected: FAIL — mevcut `.mcp.json` 15 server ve titck header'sız

- [ ] **Step 3: `write_all` + `main`'i ekle**

```python
def _write(path: Path, content: str, check: bool, changed: list) -> None:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return
    changed.append(str(path))
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _json_text(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def write_all(root: Path, fleet: dict, check: bool = False) -> list:
    """Tüm türev artefaktları yazar (veya check modunda yalnız farkı toplar)."""
    changed = []
    _write(root / "fleet.lock.json", _json_text(build_lock(fleet)), check, changed)
    _write(root / ".mcp.json", _json_text(build_mcp_json(fleet)), check, changed)

    codex_path = root / ".codex-plugin" / "plugin.json"
    codex = json.loads(codex_path.read_text(encoding="utf-8"))
    codex["version"] = fleet["plugin_version"]
    codex["mcpServers"] = build_mcp_servers(fleet)
    _write(codex_path, _json_text(codex), check, changed)

    conn = root / "commands" / "lex-connectors.md"
    _write(conn, replace_gen_block(conn.read_text(encoding="utf-8"),
                                   "fleet-env-table", env_table(fleet)),
           check, changed)

    for agent, shards, extra, comps in AGENT_SHARDS:
        path = root / "agents" / agent
        _write(path, replace_gen_block(path.read_text(encoding="utf-8"), "agent-tools",
                                       agent_tools_line(fleet, shards, extra, comps)),
               check, changed)

    pipe = root / "skills" / "lex-sanitas" / "references" / "00-mod-pipelines.md"
    _write(pipe, replace_gen_block(pipe.read_text(encoding="utf-8"),
                                   "mode-server-matrix", mode_matrix(fleet)),
           check, changed)
    return changed


AGENT_SHARDS = [
    ("legal-distiller.md", ["S1", "S3"], ["Read", "Grep", "WebFetch"], True),
    ("comparative-law-researcher.md", ["S2", "S4"], ["Read", "Grep", "WebFetch"], True),
    ("compliance-auditor.md", ["S1"], ["Read", "Grep"], True),
    ("gerekce-drafter.md", ["S1", "S3"], ["Read", "Grep"], True),
]


def mode_matrix(fleet: dict) -> str:
    modes = ["DRAFT", "AMEND", "ANALYZE", "COMPLY", "OPINE", "RIA",
             "COMPARATIVE_LAW", "TBMM_KANUN_TEKLIFI", "EX_POST_EVALUATION"]
    head = "| Server | " + " | ".join(m[:6] for m in modes) + " |"
    sep = "|---|" + "---|" * len(modes)
    rows = [head, sep]
    for s in fleet["servers"] + fleet["companions"]:
        active = s.get("modes", ["ALL"])
        cells = ["✓" if ("ALL" in active or m in active) else "·" for m in modes]
        rows.append(f"| `{s['name']}` | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lex-sanitas filo üreticisi")
    ap.add_argument("--check", action="store_true",
                    help="yazma; fark varsa exit 1 (CI kapısı)")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    fleet = load_fleet(root)
    changed = write_all(root, fleet, check=args.check)
    if args.check and changed:
        print("SÜRÜKLENME — türetilmiş dosyalar güncel değil:", file=sys.stderr)
        for c in changed:
            print(f"  · {c}", file=sys.stderr)
        print("Çözüm: python3 tools/gen_fleet.py", file=sys.stderr)
        return 1
    for c in changed:
        print(f"yazıldı: {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: `⟨GEN⟩` işaretlerini hedef dosyalara ekle**

`commands/lex-connectors.md` içindeki mevcut "Anahtar env-var haritası" tablosunu şu blokla değiştir:

```markdown
<!-- GEN:fleet-env-table BEGIN -->
<!-- GEN:fleet-env-table END -->
```

`references/00-mod-pipelines.md` sonuna:

```markdown
## Mod × server matrisi (üretilmiş)

<!-- GEN:mode-server-matrix BEGIN -->
<!-- GEN:mode-server-matrix END -->
```

Her `agents/*.md` frontmatter'ında `description:` bloğundan sonra:

```markdown
<!-- GEN:agent-tools BEGIN -->
<!-- GEN:agent-tools END -->
```

> **Not:** `tools:` satırı YAML frontmatter içinde olmalı. `⟨GEN⟩` HTML yorumları YAML'da geçerli değildir — bu yüzden ajan dosyalarında işaret **frontmatter'ın son satırından hemen önce**, `#` YAML yorumu biçiminde kullanılır: `# GEN:agent-tools BEGIN` / `# GEN:agent-tools END`. `replace_gen_block`'a `comment_style` parametresi eklenerek her iki biçim desteklenir.

- [ ] **Step 5: Üreticiyi koştur**

Run: `python3 tools/gen_fleet.py`
Expected: `.mcp.json`, `.codex-plugin/plugin.json`, `commands/lex-connectors.md`, 4 ajan, `00-mod-pipelines.md` yazıldı

- [ ] **Step 6: titck düzeltmesini canlı doğrula**

```bash
python3 -c "
import json; d=json.load(open('plugins/lex-sanitas/.mcp.json'))
t=d['mcpServers']['titck']; print(t['headers'])
assert t['headers']['Authorization']=='Bearer \${TITCK_MCP_API_KEY}'
print('titck auth OK; toplam server:', len(d['mcpServers']))"
```
Expected: `{'Authorization': 'Bearer ${TITCK_MCP_API_KEY}'}` · `toplam server: 19`

- [ ] **Step 7: Testleri koştur**

Run: `python3 tools/test_gen_fleet.py -v`
Expected: 11 test PASS

- [ ] **Step 8: Commit**

```bash
git add plugins/lex-sanitas/
git commit -m "fix(lex-sanitas): titck Bearer gate + health-policy kanonik env; .mcp.json üretilir"
```

---

## Task 3: Drift kapısı

**Files:**
- Create: `plugins/lex-sanitas/tools/check_drift.py`
- Test: `plugins/lex-sanitas/tools/test_check_drift.py`

**Interfaces:**
- Consumes: `gen_fleet.load_fleet`, `gen_fleet.write_all(check=True)`.
- Produces: `check_drift.scan_prose_counts(root, expected) -> list[tuple[str,int,str]]` — (dosya, satır, bulunan metin).
- Produces: `check_drift.main(argv) -> int` — 0 temiz, 1 sürüklenme.

- [ ] **Step 1: Başarısız testi yaz**

```python
#!/usr/bin/env python3
"""check_drift birim testleri."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_drift  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class TestDriftGate(unittest.TestCase):
    def test_yanlis_sayiyi_yakalar(self):
        hits = check_drift.scan_text(
            "wire edilmiş 14 hukuk/regülasyon MCP her sorguda çalışır", expected=19
        )
        self.assertTrue(hits, "'14 … MCP' ifadesi yakalanmalıydı")

    def test_dogru_sayiyi_gecirir(self):
        self.assertFalse(
            check_drift.scan_text("wire edilmiş 19 hukuk/regülasyon MCP", expected=19)
        )

    def test_alakasiz_sayiyi_yakalamaz(self):
        """5210 sayılı Yönetmelik, Md.90/5, 21-nokta rubrik → false positive olmamalı."""
        for s in ("5210 sayılı Yönetmelik", "Anayasa Md.90/5",
                  "R6b 21-nokta yürütülebilir rubrik", "G0-G9 kalite kapıları"):
            self.assertFalse(check_drift.scan_text(s, expected=19), s)

    def test_companion_sayisini_dogrular(self):
        self.assertTrue(
            check_drift.scan_text("6 companion tam-filonun zorunlu üyesi",
                                  expected=19, companions=5)
        )

    def test_repo_temiz(self):
        """Bütünleşik: plan tamamlandığında repo sürüklenmesiz olmalı."""
        self.assertEqual(check_drift.main(["--quiet"]), 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Testi koştur, başarısız olduğunu doğrula**

Run: `python3 tools/test_check_drift.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'check_drift'`

- [ ] **Step 3: `check_drift.py`'yi yaz**

```python
#!/usr/bin/env python3
"""lex-sanitas sürüklenme kapısı — ağ erişimi GEREKTİRMEZ, CI'da güvenle koşar.

Üç denetim:
  1. Türetilmiş dosyalar güncel mi (gen_fleet --check)
  2. Düzyazıda elle yazılmış filo sayısı gerçekle uyuşuyor mu
  3. auth_env'li her server lock'ta görünüyor mu (hook kapsamı)

Çıkış: 0 temiz · 1 sürüklenme.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_fleet

# Filo sayısı iddiası kalıpları — YALNIZ 'MCP/server/companion' bağlamında sayı arar,
# böylece 5210/21-nokta/G0-G9 gibi alakasız sayılar false positive üretmez.
SERVER_CLAIM = re.compile(
    r"(?<![\d.])(\d{1,3})\s*(?:hukuk/regülasyon\s+)?(?:kaynak\s+)?"
    r"(?:MCP|server|sunucu)\b(?!\s*[-–]\s*\d)",
    re.IGNORECASE,
)
COMPANION_CLAIM = re.compile(r"(?<![\d.])(\d{1,3})\s*companion\b", re.IGNORECASE)

SCAN_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".json"}
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = {"fleet.lock.json", ".mcp.json", "fleet.yaml"}  # üretilmiş/kaynak


def scan_text(text: str, expected: int, companions: int | None = None) -> list:
    """Metindeki yanlış filo-sayısı iddialarını döndürür."""
    hits = []
    for m in SERVER_CLAIM.finditer(text):
        if int(m.group(1)) != expected:
            hits.append(m.group(0).strip())
    if companions is not None:
        for m in COMPANION_CLAIM.finditer(text):
            if int(m.group(1)) != companions:
                hits.append(m.group(0).strip())
    return hits


def scan_prose_counts(root: Path, expected: int, companions: int) -> list:
    """Plugin ağacındaki düzyazıyı tarar; (dosya, satır_no, bulgu) listesi döner."""
    findings = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if path.name in SKIP_FILES or SKIP_DIRS & set(path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            for hit in scan_text(line, expected, companions):
                findings.append((str(path.relative_to(root)), i, hit))
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lex-sanitas sürüklenme kapısı")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    fleet = gen_fleet.load_fleet(root)
    lock = gen_fleet.build_lock(fleet)
    failed = False

    stale = gen_fleet.write_all(root, fleet, check=True)
    if stale:
        failed = True
        if not args.quiet:
            print("[1/3] TÜRETİLMİŞ DOSYA SÜRÜKLENMESİ:", file=sys.stderr)
            for s in stale:
                print(f"      · {s}", file=sys.stderr)
            print("      Çözüm: python3 tools/gen_fleet.py", file=sys.stderr)

    prose = scan_prose_counts(root, lock["counts"]["servers"],
                              lock["counts"]["companions"])
    if prose:
        failed = True
        if not args.quiet:
            print("[2/3] DÜZYAZI SAYI SÜRÜKLENMESİ "
                  f"(gerçek: {lock['counts']['servers']} server / "
                  f"{lock['counts']['companions']} companion):", file=sys.stderr)
            for f, line, hit in prose:
                print(f"      · {f}:{line}  →  {hit!r}", file=sys.stderr)

    hook_gap = _hook_coverage_gap(root, lock)
    if hook_gap:
        failed = True
        if not args.quiet:
            print(f"[3/3] HOOK KAPSAM AÇIĞI: {hook_gap}", file=sys.stderr)

    if not failed and not args.quiet:
        print(f"filo temiz — {lock['counts']['servers']} server "
              f"({lock['counts']['gated']} gated / {lock['counts']['public']} public), "
              f"{lock['counts']['companions']} companion")
    return 1 if failed else 0


def _hook_coverage_gap(root: Path, lock: dict) -> str:
    """Hook'lar lock'u okumalı; hardcoded GATED sözlüğü kalmışsa yakala."""
    src = (root / "hooks" / "scripts" / "session_start.py").read_text(encoding="utf-8")
    if re.search(r"^GATED\s*=\s*\{", src, re.MULTILINE):
        return ("session_start.py hâlâ hardcoded GATED sözlüğü taşıyor — "
                "fleet.lock.json okumalı")
    if "fleet.lock.json" not in src:
        return "session_start.py fleet.lock.json okumuyor"
    return ""


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Testi koştur — regex testleri geçmeli, `test_repo_temiz` başarısız olmalı**

Run: `python3 tools/test_check_drift.py -v`
Expected: 4 PASS, `test_repo_temiz` FAIL (düzyazı hâlâ "14" diyor, hook lock okumuyor) — bu **beklenen**; Task 5 ve 8'de kapanır.

- [ ] **Step 5: Commit**

```bash
git add plugins/lex-sanitas/tools/check_drift.py plugins/lex-sanitas/tools/test_check_drift.py
git commit -m "feat(lex-sanitas): sürüklenme kapısı — türetim + düzyazı sayı + hook kapsam denetimi"
```

---

## Task 4: Canlı MCP prob'u

**Files:**
- Create: `plugins/lex-sanitas/hooks/scripts/fleet_probe.py`
- Test: `plugins/lex-sanitas/hooks/test_hooks.py` (genişletilir)

**Interfaces:**
- Produces: `fleet_probe.load_lock(root: Path) -> dict | None` — lock okunamazsa `None` (fail-open).
- Produces: `fleet_probe.probe_server(server: dict, env: dict, timeout: float) -> dict` — `{"name", "status", "http", "detail"}`; `status` ∈ `{ok, auth_missing, unauthorized, unreachable, error}`.
- Produces: `fleet_probe.probe_fleet(lock, env, deadline=8.0) -> dict[str, dict]`.
- Produces: `fleet_probe.cached_probe(root, env, ttl=86400, fresh=False) -> dict[str, dict]`.

- [ ] **Step 1: Başarısız testleri yaz** (`hooks/test_hooks.py` sonuna)

```python
# ── fleet_probe ───────────────────────────────────────────────────────────
import fleet_probe  # noqa: E402  (hooks/scripts sys.path'te)


class TestFleetProbe(unittest.TestCase):
    def test_anahtar_yoksa_istek_atilmaz(self):
        """auth_missing: ağa hiç çıkılmaz — bu bir degrade, arıza değil."""
        srv = {"name": "x", "url": "https://ornek.invalid/mcp",
               "auth_env": "YOK_BOYLE_BIR_ANAHTAR"}
        r = fleet_probe.probe_server(srv, env={}, timeout=0.1)
        self.assertEqual(r["status"], "auth_missing")
        self.assertIsNone(r["http"])

    def test_401_unauthorized_olarak_siniflanir(self):
        """titck sınıfı arıza: anahtar VAR ama sunucu reddetti → yapılandırma hatası."""
        r = fleet_probe.classify(http=401, body="")
        self.assertEqual(r, "unauthorized")

    def test_403_de_unauthorized(self):
        self.assertEqual(fleet_probe.classify(http=403, body=""), "unauthorized")

    def test_200_gecerli_jsonrpc_ok(self):
        body = '{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18"}}'
        self.assertEqual(fleet_probe.classify(http=200, body=body), "ok")

    def test_200_sse_govdesi_de_ok(self):
        body = 'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"x":1}}\n'
        self.assertEqual(fleet_probe.classify(http=200, body=body), "ok")

    def test_200_jsonrpc_hatasi_error(self):
        body = '{"jsonrpc":"2.0","id":1,"error":{"code":-32600,"message":"bad"}}'
        self.assertEqual(fleet_probe.classify(http=200, body=body), "error")

    def test_5xx_unreachable(self):
        self.assertEqual(fleet_probe.classify(http=503, body=""), "unreachable")

    def test_cache_ttl_dolmamissa_yeniden_prob_etmez(self):
        import tempfile, json as _j, time
        with tempfile.TemporaryDirectory() as d:
            cache = pathlib.Path(d) / "fleet_probe.json"
            cache.write_text(_j.dumps({"ts": time.time(),
                                       "results": {"a": {"status": "ok"}}}))
            got = fleet_probe.read_cache(cache, ttl=86400)
            self.assertEqual(got, {"a": {"status": "ok"}})

    def test_cache_ttl_dolmussa_none(self):
        import tempfile, json as _j, time
        with tempfile.TemporaryDirectory() as d:
            cache = pathlib.Path(d) / "fleet_probe.json"
            cache.write_text(_j.dumps({"ts": time.time() - 90000, "results": {}}))
            self.assertIsNone(fleet_probe.read_cache(cache, ttl=86400))

    def test_bozuk_cache_fail_open(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            cache = pathlib.Path(d) / "fleet_probe.json"
            cache.write_text("bu json değil {{{")
            self.assertIsNone(fleet_probe.read_cache(cache, ttl=86400))

    def test_lock_yoksa_none(self):
        self.assertIsNone(fleet_probe.load_lock(pathlib.Path("/olmayan/yol")))

    def test_yalniz_stdlib(self):
        """Hook'lar kullanıcı sisteminde PyYAML olmadan çalışmalı."""
        src = (HOOKS / "scripts" / "fleet_probe.py").read_text(encoding="utf-8")
        self.assertNotIn("import yaml", src)
        self.assertNotIn("import requests", src)
```

- [ ] **Step 2: Testi koştur, başarısız olduğunu doğrula**

Run: `cd plugins/lex-sanitas && python3 hooks/test_hooks.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'fleet_probe'`

- [ ] **Step 3: `fleet_probe.py`'yi yaz**

```python
#!/usr/bin/env python3
"""lex-sanitas canlı filo prob'u — yalnız stdlib, fail-open, 24 saat cache'li.

Neden var: env-var varlığına bakmak YETMEZ. 2026-08-02'de titck kapılandı;
lex-sanitas onu 'public' saymaya devam etti ve her çağrıda 401 aldı — preflight
yapısal olarak göremedi çünkü yalnız os.environ'a bakıyordu. Bu modül gerçek
bir MCP `initialize` isteği atar ve iki hâli AYIRIR:

  auth_missing  → anahtar beklenen ama ortamda yok (meşru degrade; ağa çıkılmaz)
  unauthorized  → anahtar var/yok ama sunucu 401/403 verdi (YAPILANDIRMA ARIZASI)

Kullanım (CLI):  python3 fleet_probe.py [--fresh] [--json] [--quiet]
Kullanım (kütüphane):  cached_probe(root, os.environ)
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

INIT_PAYLOAD = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "lex-sanitas-preflight", "version": "3.5.0"}},
}).encode("utf-8")

PER_ENDPOINT_TIMEOUT = 4.0
TOTAL_DEADLINE = 8.0
CACHE_TTL = 86400


def load_lock(root: Path):
    """fleet.lock.json'u okur; okunamazsa None (fail-open)."""
    try:
        return json.loads((root / "fleet.lock.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def classify(http, body: str) -> str:
    """HTTP kodu + gövdeden durum türetir."""
    if http in (401, 403):
        return "unauthorized"
    if http is None or http >= 500:
        return "unreachable"
    if http != 200:
        return "error"
    payload = _extract_json(body)
    if payload is None:
        return "error"
    return "error" if "error" in payload else ("ok" if "result" in payload else "error")


def _extract_json(body: str):
    """Düz JSON veya SSE (`data: {...}`) gövdesinden ilk JSON nesnesini çıkarır."""
    for raw in (body, *[ln[5:].strip() for ln in body.splitlines()
                        if ln.startswith("data:")]):
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                return json.loads(raw)
            except ValueError:
                continue
    return None


def probe_server(server: dict, env, timeout: float = PER_ENDPOINT_TIMEOUT) -> dict:
    """Tek sunucuyu prob eder. Ağ hatası dâhil hiçbir istisna sızmaz."""
    name, auth_env = server["name"], server.get("auth_env")
    key = env.get(auth_env) if auth_env else None
    if auth_env and not key:
        return {"name": name, "status": "auth_missing", "http": None,
                "detail": f"${auth_env} süreç ortamında yok"}

    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(server["url"], data=INIT_PAYLOAD,
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(8192).decode("utf-8", "replace")
            return {"name": name, "status": classify(resp.status, body),
                    "http": resp.status, "detail": ""}
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(2048).decode("utf-8", "replace")
        except Exception:
            body = ""
        return {"name": name, "status": classify(exc.code, body),
                "http": exc.code, "detail": body[:120]}
    except Exception as exc:
        return {"name": name, "status": "unreachable", "http": None,
                "detail": type(exc).__name__}


def probe_fleet(lock: dict, env, deadline: float = TOTAL_DEADLINE) -> dict:
    """Tüm filoyu paralel prob eder; bütçe dolarsa kalanlar 'unknown'."""
    servers = lock.get("servers", [])
    results = {s["name"]: {"name": s["name"], "status": "unknown",
                           "http": None, "detail": "bütçe doldu"} for s in servers}
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(probe_server, s, env): s["name"] for s in servers}
        for fut in as_completed(futures, timeout=deadline):
            try:
                r = fut.result()
                results[r["name"]] = r
            except Exception:
                pass
            if time.monotonic() - started > deadline:
                break
    return results


def _cache_path() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return Path(base) / "lex-sanitas" / "fleet_probe.json"


def read_cache(path: Path, ttl: int = CACHE_TTL):
    """Taze cache'i döner; bayat/bozuk/eksikse None."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - float(data["ts"]) > ttl:
            return None
        return data["results"]
    except Exception:
        return None


def write_cache(path: Path, results: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"ts": time.time(), "results": results}),
                        encoding="utf-8")
    except Exception:
        pass  # cache yazılamaması asla akışı bozmaz


def cached_probe(root: Path, env, ttl: int = CACHE_TTL, fresh: bool = False):
    """Cache'li prob. Lock yoksa veya her şey çökerse boş dict (fail-open)."""
    try:
        lock = load_lock(root)
        if not lock:
            return {}
        path = _cache_path()
        if not fresh:
            cached = read_cache(path, ttl)
            if cached is not None:
                return cached
        results = probe_fleet(lock, env)
        write_cache(path, results)
        return results
    except Exception:
        return {}


SYMBOL = {"ok": "✓", "auth_missing": "○", "unauthorized": "✗",
          "unreachable": "✗", "error": "!", "unknown": "?"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lex-sanitas filo prob'u")
    ap.add_argument("--fresh", action="store_true", help="cache'i atla")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parent.parent.parent
    results = cached_probe(root, os.environ, fresh=args.fresh)
    if args.as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif not args.quiet:
        for name in sorted(results):
            r = results[name]
            http = r.get("http") or "-"
            print(f"{SYMBOL.get(r['status'], '?')} {name:18s} {r['status']:14s} "
                  f"{http:>4} {r.get('detail', '')[:60]}")
    return 0  # her zaman 0 — fail-open


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Testleri koştur**

Run: `python3 hooks/test_hooks.py -v`
Expected: tüm `TestFleetProbe` testleri PASS

- [ ] **Step 5: Canlı prob'u koştur (bütünleşik doğrulama)**

Run: `doppler run -p cureohub -c dev_personal -- python3 hooks/scripts/fleet_probe.py --fresh`
Expected: 19 satır; **titck `✓ ok 200`** (arıza kapandı), tümü `ok` veya açık gerekçeli.

- [ ] **Step 6: Commit**

```bash
git add plugins/lex-sanitas/hooks/scripts/fleet_probe.py plugins/lex-sanitas/hooks/test_hooks.py
git commit -m "feat(lex-sanitas): canlı MCP prob'u — auth_missing vs unauthorized ayrımı"
```

---

## Task 5: Preflight'ı lock + prob'a bağla

**Files:**
- Modify: `plugins/lex-sanitas/hooks/scripts/session_start.py` (tamamı)
- Modify: `plugins/lex-sanitas/hooks/test_hooks.py`

**Interfaces:**
- Consumes: `fleet_probe.cached_probe`, `fleet_probe.load_lock`.
- Produces: `session_start.build_context(lock, probe, plugins) -> str`.

- [ ] **Step 1: Başarısız testleri ekle**

```python
class TestSessionStartPreflight(unittest.TestCase):
    LOCK = {"counts": {"servers": 19, "gated": 16, "public": 3,
                       "companions": 5, "delegations": 2},
            "servers": [{"name": "titck", "auth_env": "TITCK_MCP_API_KEY"}],
            "companions": [{"name": "Yargı", "gate": "G5",
                            "manifest_row": "Yargı (companion — G5 içtihat)",
                            "degrade": "G5 CONDITIONAL"}],
            "delegations": [{"name": "evidentia", "plugin_id_prefix": "evidentia@",
                             "manifest_row": "evidentia (klinik delegasyon)"}]}

    def test_saglikli_filoda_preflight_sessiz(self):
        ctx = session_start.build_context(
            self.LOCK, {"titck": {"name": "titck", "status": "ok", "http": 200}}, {})
        self.assertNotIn("[preflight]", ctx)

    def test_unauthorized_yapilandirma_arizasi_olarak_bildirilir(self):
        ctx = session_start.build_context(
            self.LOCK,
            {"titck": {"name": "titck", "status": "unauthorized", "http": 401,
                       "detail": ""}}, {})
        self.assertIn("titck", ctx)
        self.assertIn("YAPILANDIRMA ARIZASI", ctx)
        self.assertNotIn("graceful degrade", ctx.split("titck")[1][:200])

    def test_auth_missing_degrade_olarak_bildirilir(self):
        ctx = session_start.build_context(
            self.LOCK,
            {"titck": {"name": "titck", "status": "auth_missing", "http": None,
                       "detail": "$TITCK_MCP_API_KEY süreç ortamında yok"}}, {})
        self.assertIn("doppler run", ctx)

    def test_sayilar_lock_tan_gelir(self):
        ctx = session_start.build_context(self.LOCK, {}, {})
        self.assertIn("19", ctx)
        self.assertNotIn("wire'lı 14", ctx)

    def test_hardcoded_gated_sozlugu_kalmadi(self):
        src = (HOOKS / "scripts" / "session_start.py").read_text(encoding="utf-8")
        self.assertNotRegex(src, r"(?m)^GATED\s*=\s*\{")
        self.assertIn("fleet.lock.json", src)

    def test_titck_public_yalani_kalmadi(self):
        src = (HOOKS / "scripts" / "session_start.py").read_text(encoding="utf-8")
        self.assertNotIn("Public server'lar — titck", src)

    def test_prob_cokerse_fail_open(self):
        """cached_probe boş dönerse hook yine bağlam üretir, çökmez."""
        ctx = session_start.build_context(self.LOCK, {}, {})
        self.assertTrue(ctx.startswith("[lex-sanitas]"))
```

- [ ] **Step 2: Testi koştur, başarısız olduğunu doğrula**

Run: `python3 hooks/test_hooks.py -v -k SessionStart`
Expected: FAIL — `build_context` yok; `GATED` sözlüğü hâlâ var

- [ ] **Step 3: `session_start.py`'yi yeniden yaz**

`GATED` sözlüğü silinir. Yeni yapı:

```python
#!/usr/bin/env python3
"""lex-sanitas SessionStart preflight — canlı filo prob'u + konvansiyon enjeksiyonu.

v3.5.0: anahtar haritası artık hardcoded DEĞİL — fleet.lock.json'dan gelir
(tools/gen_fleet.py üretir). Preflight gerçek MCP `initialize` prob'u yapar ve
'anahtar yok' (meşru degrade) ile 'sunucu reddetti' (yapılandırma arızası)
hâllerini AYIRIR. Prob 24 saat cache'lenir; sağlıklı filoda preflight sessizdir.
Fail-open: prob/lock çökerse yalnız konvansiyonlar enjekte edilir.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import fleet_probe
except Exception:
    fleet_probe = None

ROOT = Path(__file__).resolve().parent.parent.parent
DELEGATION_FALLBACK = {"evidentia": "evidentia@", "sci-audit": "sci-audit@"}


def conventions(lock) -> str:
    """Çekirdek invaryantlar — sayılar lock'tan enterpole edilir."""
    c = (lock or {}).get("counts", {})
    n_srv = c.get("servers", "?")
    comps = (lock or {}).get("companions", [])
    comp_desc = " / ".join(
        f"{x['name']} {x['tool_prefixes'][0]}*" for x in comps
    ) or "companion listesi okunamadı"
    return (
        f"[lex-sanitas] Türkiye sağlık mevzuatı reform protokolü aktif. "
        f"Çekirdek invaryantlar: (1) TAM-FİLO — wire'lı {n_srv} hukuk MCP + "
        f"{len(comps)} companion ({comp_desc}) her sorguda çalışır; companion'lar "
        f"tam-filonun ZORUNLU üyeleridir — bağlıyken tetiklenmiş bağlamda atlanmaları "
        f"G0 ihlalidir; bağlı değillerse ilgili kapı CONDITIONAL + manifesto beyanı; "
        f"bağlam-dışı companion satırı dürüstçe 'skipped: mod için N/A' yazılır "
        f"(satır hiç yazılmamazlık edilemez). Connector önekleri yüzeye göre "
        f"mcp__<Ad>__* veya mcp__claude_ai_<Ad>__* görünebilir — ada göre eşleştir. "
        f"Çıktı G0 kapsam manifestosu taşır (server → hit/empty/degraded/"
        f"skipped-with-reason; sessiz atlama = FAIL). "
        f"(2) NO-FABRICATION — kanun/CELEX/AYM/Yargıtay/PMID/YÖK-Tez asla uydurulmaz; "
        f"her atıf MCP-doğrulanmış (evidence_ledger). YÖK-Tez atıfları artık wire'lı "
        f"yoktez connector'ıyla doğrulanır (G7 hard PASS). "
        f"(3) SCOPE GUARD — yalnız mevzuat reformu; bireysel dava (SGK red/AYM başvuru), "
        f"malpraktis → saglik-sigorta/onko-erisim; promosyon denetimi → promo-censor. "
        f"(4) ZORUNLU DELEGASYON — klinik kanıt → evidentia (her klinik-boyutlu sorguda); "
        f"atıf-adli + TR dil → sci-audit (her çıktıda). Bu plugin'ler KURULUYKEN "
        f"atlanmaları G0 ihlalidir. (5) İNSAN DENETİMİ her çıktıda zorunlu. "
        f"(6) BAĞLAM EKONOMİSİ — ham veri ana pencereye girmez: ≤4 paralel distiller "
        f"alt-ajanı (Tier 1) + anamnesis RAG substratı (Tier 2) + kanonik cache + "
        f"kör-getirme-yok chunking. (7) TAM-METİN ŞELALESİ — lisanslı band "
        f"(openathens Tier 3) önce; annas-reader (Tier 4) yalnız o denendikten sonra ve "
        f"YALNIZ ANALİZ için. shared/context-economy-contract.md."
    )
```

`build_context` ve `main`:

```python
def build_context(lock, probe: dict, plugins: dict) -> str:
    ctx = conventions(lock)

    if plugins:
        installed = [n for n, ok in plugins.items() if ok]
        absent = [n for n, ok in plugins.items() if not ok]
        if installed:
            ctx += ("\n[preflight/delegasyon] KURULU: " + ", ".join(installed)
                    + " → bağlam tetiklendiğinde çağrılmaları ZORUNLU. Atlanmaları "
                    "G0 ihlalidir; 'skipped: plugin kurulu değil' YAZILAMAZ.")
        if absent:
            ctx += ("\n[preflight/delegasyon] KURULU DEĞİL: " + ", ".join(absent)
                    + " → graceful degrade meşru; manifestoda beyan et, uydurma.")

    broken = [r for r in probe.values() if r.get("status") == "unauthorized"]
    missing = [r for r in probe.values() if r.get("status") == "auth_missing"]
    down = [r for r in probe.values()
            if r.get("status") in ("unreachable", "error")]

    if broken:
        ctx += ("\n[preflight] ⚠ YAPILANDIRMA ARIZASI — şu server(lar) canlı prob'da "
                "401/403 verdi: "
                + ", ".join(f"{r['name']} (HTTP {r['http']})" for r in broken)
                + ". Bu bir degrade DEĞİL, düzeltilebilir bir wiring hatasıdır: ya "
                ".mcp.json'daki Authorization header'ı eksik/yanlış, ya anahtar "
                "geçersiz. fleet.yaml'i düzeltip `python3 tools/gen_fleet.py` koş. "
                "Bu tur bu katman manifestoda 'degraded: 401' olarak beyan edilir.")
    if missing:
        ctx += ("\n[preflight] Şu connector anahtar(lar)ı süreç ortamında YOK: "
                + ", ".join(f"{r['name']} ({r['detail']})" for r in missing)
                + ". Manifestoda 'skipped: anahtar yok' beyan edilir (tam-filo "
                "degrade — çıktı durmaz). Çözüm: oturumu "
                "`doppler run -p cureohub -c dev_personal -- claude` ile başlat.")
    if down:
        ctx += ("\n[preflight] Şu server(lar) erişilemedi: "
                + ", ".join(f"{r['name']} ({r.get('detail') or r.get('http')})"
                            for r in down)
                + ". Manifestoda 'degraded: erişilemedi'; asla uydurma.")
    return ctx


def detect_installed_plugins():
    """~/.claude/settings.json enabledPlugins'ten delegasyon plugin'lerini algılar."""
    try:
        lock = fleet_probe.load_lock(ROOT) if fleet_probe else None
        prefixes = ({d["name"]: d["plugin_id_prefix"] for d in lock["delegations"]}
                    if lock else DELEGATION_FALLBACK)
        with open(os.path.expanduser("~/.claude/settings.json"), encoding="utf-8") as fh:
            enabled = json.load(fh).get("enabledPlugins", {})
        return {name: any(k.startswith(p) and v for k, v in enabled.items())
                for name, p in prefixes.items()}
    except Exception:
        return {}


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass
    lock, probe = None, {}
    try:
        if fleet_probe:
            lock = fleet_probe.load_lock(ROOT)
            probe = fleet_probe.cached_probe(ROOT, os.environ)
    except Exception:
        pass
    ctx = build_context(lock, probe, detect_installed_plugins())
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart",
                               "additionalContext": ctx}}))
    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Testleri koştur**

Run: `python3 hooks/test_hooks.py -v`
Expected: tüm testler PASS

- [ ] **Step 5: Hook'u uçtan uca koştur**

Run: `echo '{}' | doppler run -p cureohub -c dev_personal -- python3 hooks/scripts/session_start.py | python3 -m json.tool`
Expected: geçerli JSON; `additionalContext` "19 hukuk MCP + 5 companion" içeriyor; `[preflight] ⚠` **yok** (filo sağlıklı)

- [ ] **Step 6: Commit**

```bash
git add plugins/lex-sanitas/hooks/
git commit -m "feat(lex-sanitas): preflight lock+prob'a bağlandı; hardcoded GATED sözlüğü kaldırıldı"
```

---

## Task 6: Stop hook + hooks.json tekilleştirme

**Files:**
- Modify: `plugins/lex-sanitas/hooks/scripts/stop_coverage.py`
- Delete: `plugins/lex-sanitas/hooks.json` (kök kopya)
- Modify: `plugins/lex-sanitas/hooks/test_hooks.py`

**Interfaces:**
- Consumes: `fleet_probe.load_lock`.
- Produces: `stop_coverage.mandatory_rows(lock) -> dict[str, re.Pattern]` — 7 satır (5 companion + 2 delegasyon).

- [ ] **Step 1: Başarısız testleri ekle**

```python
class TestStopMandatoryRows(unittest.TestCase):
    def test_yedi_zorunlu_satir(self):
        lock = fleet_probe.load_lock(ROOT)
        rows = stop_coverage.mandatory_rows(lock)
        self.assertEqual(len(rows), 7, "5 companion + 2 delegasyon")

    def test_yoktez_artik_zorunlu_companion_satiri_degil(self):
        """v3.5.0: yoktez wire'landı → companion satırı olmaktan çıktı."""
        lock = fleet_probe.load_lock(ROOT)
        rows = stop_coverage.mandatory_rows(lock)
        self.assertFalse([k for k in rows if "YokTez" in k or "YÖK-Tez" in k])

    def test_lock_yoksa_gomulu_listeye_duser(self):
        rows = stop_coverage.mandatory_rows(None)
        self.assertGreaterEqual(len(rows), 5)

    def test_kok_hooks_json_silindi(self):
        self.assertFalse((ROOT / "hooks.json").exists(),
                         "kök hooks.json kaldırılmalı — hooks/hooks.json kanonik")
```

- [ ] **Step 2: Testi koştur, başarısız olduğunu doğrula**

Run: `python3 hooks/test_hooks.py -v -k Mandatory`
Expected: FAIL — `mandatory_rows` yok; kök `hooks.json` duruyor

- [ ] **Step 3: `stop_coverage.py`'de `MANDATORY_ROWS` sabitini fonksiyonla değiştir**

```python
def mandatory_rows(lock):
    """Manifestoda BULUNMASI ZORUNLU satırlar — lock'tan türetilir.

    Companion'lar (wire edilemez dış connector) + delegasyon plugin'leri. Wire'lı
    server'lar için satır-satır regex denetimi YAPILMAZ (kırılgan olur); G0
    manifestosunun varlığı ve bu satırlar denetlenir.
    """
    if not lock:
        return dict(_FALLBACK_ROWS)
    rows = {}
    for c in lock.get("companions", []):
        token = re.escape(c["name"].split()[0])
        rows[c["manifest_row"]] = re.compile(token.replace(r"\ ", r"[_ ]?"),
                                             re.IGNORECASE)
    for d in lock.get("delegations", []):
        rows[d["manifest_row"]] = re.compile(
            re.escape(d["name"]).replace(r"\-", "[- ]?"), re.IGNORECASE)
    return rows


_FALLBACK_ROWS = {
    "Yargı (companion — G5 içtihat)": re.compile(r"\bYarg", re.IGNORECASE),
    "Open Law (companion — G6 CELEX)": re.compile(r"Open[_ ]?Law", re.IGNORECASE),
    "Ansvar (companion — Mod7 58-yargı)": re.compile(r"\bAnsvar", re.IGNORECASE),
    "Fedlex Swiss (companion — Mod7 CH)": re.compile(r"Fedlex", re.IGNORECASE),
    "Türk Patent (companion — IP/SPC)": re.compile(r"T[üu]rk[_ ]?Patent", re.IGNORECASE),
    "evidentia (klinik delegasyon)": re.compile(r"\bevidentia", re.IGNORECASE),
    "sci-audit (çıktı-QA delegasyonu)": re.compile(r"\bsci[- ]?audit", re.IGNORECASE),
}
```

`main()` içinde `MANDATORY_ROWS.items()` → `mandatory_rows(_lock()).items()`; `_lock()` `fleet_probe.load_lock(ROOT)`'u try/except ile sarar.

- [ ] **Step 4: Kök `hooks.json`'u sil**

```bash
git rm plugins/lex-sanitas/hooks.json
```

- [ ] **Step 5: Testleri koştur**

Run: `python3 hooks/test_hooks.py -v`
Expected: tüm testler PASS

- [ ] **Step 6: Commit**

```bash
git add plugins/lex-sanitas/hooks/
git commit -m "refactor(lex-sanitas): Stop zorunlu satırları lock'tan türer (7); kök hooks.json kaldırıldı"
```

---

## Task 7: Ajan shard kısıtları

**Files:**
- Modify: `plugins/lex-sanitas/agents/legal-distiller.md`
- Modify: `plugins/lex-sanitas/agents/comparative-law-researcher.md`
- Modify: `plugins/lex-sanitas/agents/compliance-auditor.md`
- Modify: `plugins/lex-sanitas/agents/gerekce-drafter.md`
- Test: `plugins/lex-sanitas/tools/test_gen_fleet.py`

**Interfaces:**
- Consumes: `gen_fleet.agent_tools_line`, `gen_fleet.AGENT_SHARDS`.

- [ ] **Step 1: Başarısız testi ekle**

```python
    def test_legal_distiller_S2_gormez(self):
        """S1+S3 ajanı karşılaştırmalı server'ları görmemeli."""
        line = gen_fleet.agent_tools_line(
            self.fleet, ["S1", "S3"], ["Read"], companions=True)
        self.assertIn("mcp__mevzuat__*", line)
        self.assertIn("mcp__yoktez__*", line)
        self.assertNotIn("mcp__health-policy__*", line)
        self.assertNotIn("mcp__eudamed__*", line)

    def test_comparative_S1_gormez(self):
        line = gen_fleet.agent_tools_line(
            self.fleet, ["S2", "S4"], ["Read"], companions=True)
        self.assertIn("mcp__health-policy__*", line)
        self.assertIn("mcp__openathens__*", line)
        self.assertNotIn("mcp__tbmm__*", line)

    def test_anamnesis_her_ajanda(self):
        """shard=ALL olan substrat her shard'a girer."""
        for shards in (["S1", "S3"], ["S2", "S4"]):
            self.assertIn("mcp__anamnesis__*",
                          gen_fleet.agent_tools_line(self.fleet, shards, [], False))

    def test_ajan_dosyalari_gen_blogu_tasiyor(self):
        for agent, *_ in gen_fleet.AGENT_SHARDS:
            text = (ROOT / "agents" / agent).read_text(encoding="utf-8")
            self.assertIn("# GEN:agent-tools BEGIN", text, agent)
            self.assertIn("tools:", text, agent)
```

- [ ] **Step 2: Testi koştur, başarısız olduğunu doğrula**

Run: `python3 tools/test_gen_fleet.py -v -k distiller`
Expected: FAIL — ajan dosyalarında `⟨GEN⟩` bloğu yok

- [ ] **Step 3: `replace_gen_block`'a YAML yorum biçimi desteği ekle**

```python
def replace_gen_block(text: str, name: str, body: str,
                      comment_style: str = "html") -> str:
    """⟨GEN⟩ bloğunun içini değiştirir.

    comment_style='html'  → <!-- GEN:name BEGIN --> … <!-- GEN:name END -->
    comment_style='yaml'  → # GEN:name BEGIN … # GEN:name END
    (YAML frontmatter'da HTML yorumu geçersizdir; ajan dosyaları 'yaml' kullanır.)
    """
    if comment_style == "yaml":
        begin, end = f"# GEN:{name} BEGIN", f"# GEN:{name} END"
    else:
        begin, end = f"<!-- GEN:{name} BEGIN -->", f"<!-- GEN:{name} END -->"
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"⟨GEN⟩ bloğu bulunamadı: {name} ({comment_style})")
    return pattern.sub(f"{begin}\n{body}\n{end}", text)
```

`write_all`'daki ajan döngüsü `comment_style="yaml"` geçirir.

- [ ] **Step 4: Her ajan dosyasının frontmatter'ına işaret ekle**

`description:` bloğundan sonra, kapanış `---`'ından önce:

```yaml
# GEN:agent-tools BEGIN
tools: Read, Grep, WebFetch, mcp__mevzuat__*
# GEN:agent-tools END
```

(İçerik üretici tarafından değiştirilecek — yer tutucu satır bilinçli olarak geçerli bir `tools:` satırıdır ki dosya ara durumda da parse edilebilsin.)

- [ ] **Step 5: Üreticiyi koştur ve doğrula**

Run: `python3 tools/gen_fleet.py && grep -A1 "GEN:agent-tools BEGIN" agents/legal-distiller.md`
Expected: `tools:` satırı 11 S1/S3 server + companion önekleri içeriyor, `health-policy` **yok**

- [ ] **Step 6: Testleri koştur**

Run: `python3 tools/test_gen_fleet.py -v`
Expected: tüm testler PASS

- [ ] **Step 7: Commit**

```bash
git add plugins/lex-sanitas/agents/ plugins/lex-sanitas/tools/
git commit -m "feat(lex-sanitas): distiller ajanlarına shard-tabanlı araç kısıtı"
```

---

## Task 8: `/lex-connectors` canlı prob raporu + düzyazı senkronu

**Files:**
- Modify: `plugins/lex-sanitas/commands/lex-connectors.md`
- Modify: `plugins/lex-sanitas/skills/lex-sanitas/SKILL.md`
- Modify: `plugins/lex-sanitas/README.md`
- Modify: `plugins/lex-sanitas/skills/lex-sanitas/references/00-mod-pipelines.md`
- Modify: `plugins/lex-sanitas/shared/context-economy-contract.md`
- Modify: `plugins/lex-sanitas/tests/{full_fleet_coverage,context_economy,routing,scope_boundary,citation_hallucination,mod9_medical_research}_tests.yaml`
- Modify: `plugins/lex-sanitas/commands/lex-draft.md` (ve "14" geçen diğer komutlar)

- [ ] **Step 1: `check_drift` ile tüm sürüklenme noktalarını listele**

Run: `python3 tools/check_drift.py`
Expected: `[2/3] DÜZYAZI SAYI SÜRÜKLENMESİ` altında dosya:satır listesi

- [ ] **Step 2: `/lex-connectors`'ı canlı prob'a bağla**

`## Yürütme` bölümünün 2-3. adımlarını değiştir:

```markdown
2. **Canlı prob'u koştur.** `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/fleet_probe.py`
   — kullanıcı "güncel/taze durum" istediyse `--fresh` ekle (aksi hâlde 24 saatlik
   cache kullanılır, ağ trafiği yok):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/fleet_probe.py" --json
   ```

3. **Her satırı durumuyla raporla.** Prob'un beş durumunu **ayırt ederek** yaz —
   bu ayrım kritiktir:

   | Durum | Anlamı | Aksiyon |
   |---|---|---|
   | `ok` | hazır | — |
   | `auth_missing` | anahtar süreç ortamında yok | `doppler run -p cureohub -c dev_personal -- claude` |
   | `unauthorized` | **anahtar var/yok ama sunucu 401/403 verdi — YAPILANDIRMA ARIZASI** | `fleet.yaml` düzelt → `python3 tools/gen_fleet.py` |
   | `unreachable` | timeout/5xx | upstream sorunu; manifestoda `degraded` |
   | `error` | 200 ama geçersiz JSON-RPC | sunucu sürümü uyumsuz olabilir |
```

- [ ] **Step 3: Düzyazı sayılarını düzelt**

Her bulguda `14` → `19`, `6 companion` → `5 companion`. Ayrıca:

- `SKILL.md` §3 ilk cümlesi: *"Wire edilmiş 19 server `.mcp.json`'da rol notlarıyla tanımlıdır (16'sı Bearer-anahtar-gated; `mevzuat-bilgisi`, `yoktez`, `literatur` public)."*
- `SKILL.md` §3 doktrin maddesi: yoktez/literatur first-class olarak yeniden yazılır, companion listesinden çıkarılır.
- `SKILL.md` §3'e **yeni tam-metin şelalesi** maddesi eklenir (openathens Tier 3 → annas-reader Tier 4, şelale disiplini).
- `SKILL.md` §4 G7 satırı: *"YÖK-Tez atıfları **wire'lı `mcp__yoktez__*`** ile doğrulanır (tez no/başlık/yazar) → companion'a bağlı değil, hard PASS."*
- `README.md` filo tablosu ve mimari ağacı güncellenir.

- [ ] **Step 4: Testleri güncelle**

6 YAML test dosyasında `14` → `19`, companion `6` → `5`. `full_fleet_coverage_tests.yaml`'a iki yeni senaryo ekle:

```yaml
  - id: FF-08-yoktez-wire-g7-hard-pass
    given: >-
      Bir DRAFT çıktısı YÖK-Tez atfı içeriyor ve yoktez connector'ı wire'lı (public).
    expect:
      - "G7 CONDITIONAL DEĞİL — atıf mcp__yoktez__get_yok_tez_thesis_details ile doğrulanmalı."
      - "Manifestoda 'yoktez → hit N kayıt' satırı bulunmalı."
      - "yoktez companion satırı olarak YAZILMAMALI (v3.5.0'da first-class)."

  - id: FF-09-tam-metin-selale-disiplini
    given: >-
      Mod 7 karşılaştırmalı analizde yabancı doktrin tam metni gerekiyor;
      openathens oturumu düşük.
    expect:
      - "annas-reader OTOMATİK açılmamalı — şelale sırası korunur."
      - "openathens satırı 'degraded: lisanslı band kapalı' yazılmalı."
      - "annas-reader kullanılacaksa açık gerekçe + yalnız-analiz notu taşımalı."
```

- [ ] **Step 5: Üretici + drift kapısını koştur**

Run: `python3 tools/gen_fleet.py && python3 tools/check_drift.py`
Expected: `filo temiz — 19 server (16 gated / 3 public), 5 companion`

- [ ] **Step 6: Tüm testleri koştur**

Run: `python3 tools/test_gen_fleet.py && python3 tools/test_check_drift.py && python3 hooks/test_hooks.py`
Expected: hepsi PASS (`test_repo_temiz` dâhil)

- [ ] **Step 7: Commit**

```bash
git add plugins/lex-sanitas/
git commit -m "docs(lex-sanitas): filo düzyazısı 19/5'e senkronlandı; /lex-connectors canlı prob raporu"
```

---

## Task 9: Davranışsal filo testleri + sürüm teslimi

**Files:**
- Create: `plugins/lex-sanitas/tests/fleet_registry_tests.yaml`
- Modify: `plugins/lex-sanitas/tests/README.md`
- Modify: `plugins/lex-sanitas/.claude-plugin/plugin.json` (3.5.0 + açıklama)
- Modify: `plugins/lex-sanitas/skills/lex-sanitas/SKILL.md` (frontmatter `version: 3.5.0`)
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: `tests/fleet_registry_tests.yaml`'ı yaz**

```yaml
suite: fleet_registry
version: "3.5.0"
description: >-
  Filo kayıt defterinin (fleet.yaml → türev artefaktlar) davranışsal invaryantları.
  Bu testler AĞ ERİŞİMİ gerektirir (canlı prob) — deterministik CI kapısı için
  tools/check_drift.py kullanın.

cases:
  - id: FR-01-titck-gated
    given: "titck.cureonics.com'a anahtarsız MCP initialize isteği atılır."
    expect:
      - "HTTP 401 dönmeli — TİTCK 2026-08-02'de kapılandı."
      - "fleet.yaml'de titck.auth_env == TITCK_MCP_API_KEY olmalı."
      - "Anahtarla aynı istek 200 dönmeli."

  - id: FR-02-public-server-anahtarsiz-200
    given: "fleet.yaml'de auth_env: null işaretli her server prob edilir."
    expect:
      - "mevzuat-bilgisi, yoktez, literatur anahtarsız 200 dönmeli."
      - "Herhangi biri 401 dönerse upstream kapılanmış demektir → fleet.yaml güncellenmeli."

  - id: FR-03-env-adlari-doppler-da-var
    given: "fleet.yaml'deki her auth_env adı Doppler cureohub/dev_personal'da aranır."
    expect:
      - "16 gated server'ın env adının tamamı Doppler'da bulunmalı."
      - "Bulunmayan ad = yanlış yazım veya emekli secret."

  - id: FR-04-companion-wire-kesisimi-bos
    given: "fleet.yaml servers[] ve companions[] adları karşılaştırılır."
    expect:
      - "Kesişim BOŞ olmalı — bir server hem wire'lı hem companion olamaz."
      - "yoktez yalnız servers[] içinde olmalı (v3.5.0 terfisi)."

  - id: FR-05-preflight-401-i-arıza-olarak-bildirir
    given: "Bir gated server'ın anahtarı bilinçli olarak bozulur ve preflight koşulur."
    expect:
      - "additionalContext 'YAPILANDIRMA ARIZASI' ifadesi taşımalı."
      - "'graceful degrade' olarak sunulmamalı — bu düzeltilebilir bir wiring hatasıdır."
```

- [ ] **Step 2: FR-01…FR-04'ü canlı doğrula**

```bash
doppler run -p cureohub -c dev_personal -- python3 hooks/scripts/fleet_probe.py --fresh
```
Expected: 19 satır, hepsi `ok`; titck `✓ ok 200`

Env adları denetimi:
```bash
doppler secrets -p cureohub -c dev_personal --only-names > /tmp/dop.txt
python3 -c "
import yaml
f=yaml.safe_load(open('fleet.yaml'))
names={l.strip(' │') for l in open('/tmp/dop.txt')}
missing=[s['auth_env'] for s in f['servers'] if s['auth_env'] and s['auth_env'] not in names]
print('eksik env adı:', missing or 'yok')"
```
Expected: `eksik env adı: yok`

- [ ] **Step 3: Sürümü 3.5.0'a çek**

`fleet.yaml` `plugin_version: "3.5.0"` (zaten), sonra:
- `.claude-plugin/plugin.json` → `"version": "3.5.0"` + açıklamada `14 hukuk/regülasyon MCP` → `19 hukuk/regülasyon MCP`, companion listesinden YokTez çıkar
- `skills/lex-sanitas/SKILL.md` frontmatter → `version: 3.5.0`
- `.codex-plugin/plugin.json` → üretici zaten `plugin_version`'dan yazıyor; `description`/`longDescription` elle güncellenir
- `.claude-plugin/marketplace.json` → lex-sanitas `"version": "3.5.0"`

- [ ] **Step 4: `README.md` sürüm notunu ekle**

```markdown
Sürüm 3.5.0 = **türetilmiş filo**: `fleet.yaml` tek kaynak → `.mcp.json`/codex/
lock/komut/ajan türetilir + `tools/check_drift.py` sürüklenme kapısı; **canlı MCP
prob'lu preflight** (`auth_missing` ≠ `unauthorized`); **titck Bearer gate onarımı**
(2026-08-02 kapılanması kaçırılmıştı → katman 401 alıyordu); filo **15→19**
(yoktez + literatur + openathens + annas-reader wire), companion **6→5** (yoktez
first-class'a terfi → **G7 hard PASS**); distiller ajanlarına shard-tabanlı araç
kısıtı; kök `hooks.json` kopyası kaldırıldı.
```

- [ ] **Step 5: Tam doğrulama koşusu**

```bash
cd plugins/lex-sanitas
python3 tools/gen_fleet.py --check   # exit 0 = türev güncel
python3 tools/check_drift.py         # exit 0 = sürüklenme yok
python3 tools/test_gen_fleet.py
python3 tools/test_check_drift.py
python3 hooks/test_hooks.py
doppler run -p cureohub -c dev_personal -- python3 hooks/scripts/fleet_probe.py --fresh
```
Expected: tüm komutlar exit 0; prob'da 19/19 `ok`

- [ ] **Step 6: Commit**

```bash
git add plugins/lex-sanitas/ .claude-plugin/marketplace.json
git commit -m "release(lex-sanitas): v3.5.0 — türetilmiş filo, canlı prob, 19 server"
```

---

## Self-Review Notları

**Spec kapsamı:** §2 mimari → Task 1-3; §3 filo bileşimi → Task 1-2; §4 prob'lu preflight → Task 4-5; §5 ajan kısıtı → Task 7; §6 temizlik → Task 2, 6, 8; §7 degrade → `fleet.yaml` `degrade` alanları + Task 5 sınıflandırma; §8 test → Task 1,3,4,6,7,9; §9 sürüm → Task 9. Tümü karşılandı.

**Bilinen kırılganlık:** `check_drift.SERVER_CLAIM` regex'i düzyazıda "N MCP/server" kalıbını arar. `references/` altındaki uzun hukuk metinlerinde yanlış eşleşme çıkarsa `SKIP_FILES`'a eklemek yerine regex daraltılmalı — testte üç false-positive vakası (`5210 sayılı`, `Md.90/5`, `21-nokta`) zaten koruma altında.

**Kullanıcı aksiyonu (kod dışı):** `lex-sanitas@cureonics-marketplace` kurulu değil; `/plugin` ile kurulması gerekiyor.
