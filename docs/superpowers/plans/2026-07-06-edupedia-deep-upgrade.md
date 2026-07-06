# Edupedia 3.0.0 Derin Yükseltme — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `paideia` plugin'ini `edupedia`'ya taşımak ve flagship skill'i `carbon-edupedia` 3.0.0'a — üç araştırma eksenli zenginleştirme (içerik/Carbon-estetik/ADHD-oyunlaştırma), 5 yeni segment tipi, 2 yeni validator kapısı, bir QA agent ve iki hook ile — derinlemesine yükseltmek.

**Architecture:** Motor (`assets/module-template.html`, inline JS) `MODULE_DATA` veri-güdümlüdür; yeni segment tipleri `render()` dispatch tablosuna handler ekler (kod MODULE_DATA'da değil motorda). Validator (`scripts/validate_module.py`, saf-Python stdlib) gate fonksiyonları `gate_X(html, R)` deseniyle; testler bunları fixture HTML ile import-edip çağırır. Tüm yeni segment/alanlar opsiyonel + yeni kapılar koşullu → geriye uyumlu (major-bump marka+motor genişlemesi içindir).

**Tech Stack:** HTML5 + inline vanilla JS (motor), IBM Carbon v11 token'ları (`@carbon/*` otorite), Python 3.10+ stdlib (validator + testler, pytest), bash (hook script'leri), Claude plugin manifest/agent/hook formatı.

## Global Constraints

*(Her görevin gereksinimleri örtük olarak bunları içerir — spec'ten birebir.)*
- **Emojisiz:** çıktıda emoji yok; görsel anlam yalnız ikon/piktogram/SVG (G-EMOJI FAIL).
- **WCAG 2.1 AA:** lang/title/reduced-motion/aria-live/odak/görsel-rolleri; her etkileşim klavye-erişilebilir (drag için click/keyboard fallback zorunlu).
- **Self-contained:** tek-dosya, offline; harici yerel dosya/CDN-veri/runtime-network yok. `localStorage` OK (feature-detect + degrade); IndexedDB KULLANMA (`file://`'da bloklu).
- **Token otoritesi:** `@carbon/themes@11.75.0` + `@carbon/*`; ham-hex yerine `--cds-*` token; G-TOKEN otorite haritası.
- **No-punitive / fixed-reward:** cezalandırıcı/süre-baskısı dili yok (G-WELLBEING FAIL); değişken-oran/loot-box/geri-sayım YOK; ödül fixed + deterministik + mastery-bağlı.
- **No-fabrication / kaynak-sadakati:** her olgu kazanım koduna/çekilen metne izlenebilir; `meta.sourceCitation` zorunlu.
- **MODULE_DATA veridir, kod değil:** segmentler keyfi render fonksiyonu taşımaz; motor handler sağlar (`sim` = preset kütüphanesi).
- **Sürüm:** flagship skill `carbon-edupedia` 3.0.0; plugin `edupedia` 0.2.0.
- **Yol kuralı:** `commands/` → `../CONNECTORS.md`; `skills/x/` → `../../CONNECTORS.md`; hook/agent → `${CLAUDE_PLUGIN_ROOT}`.
- **Mevcut 11 kapı ve 8 mod korunur;** yalnız eklenir.

---

## Dosya Yapısı Haritası

**Yeni:**
- `plugins/edupedia/skills/carbon-edupedia/references/content-enrichment.md` — entegre-edilebilir içerik + dürüst "yapılamaz" listesi
- `plugins/edupedia/skills/carbon-edupedia/references/carbon-excellence.md` — 15-madde uzman-Carbon checklist (G-CARBON-GRID normatif kaynağı)
- `plugins/edupedia/skills/carbon-edupedia/references/gamified-flows.md` — 4 akış şablonu + mekanikler + YAPMA listesi (G-FLOW normatif kaynağı)
- `plugins/edupedia/skills/carbon-edupedia/tests/test_gates.py` — validator gate testleri (pytest)
- `plugins/edupedia/skills/carbon-edupedia/tests/fixtures/` — pass/fail fixture modül HTML'leri
- `plugins/edupedia/skills/carbon-edupedia/tests/check_engine.sh` — motor script'i `node --check`
- `plugins/edupedia/agents/module-auditor.md` — QA denetçi agent
- `plugins/edupedia/hooks/hooks.json` — SessionStart + PostToolUse
- `plugins/edupedia/hooks/preflight.sh` — connector preflight script
- `plugins/edupedia/hooks/validate-module.sh` — modül otomatik doğrulama script

**Değişecek (git mv sonrası `plugins/edupedia/` altında):**
- `.claude-plugin/plugin.json` — name/displayName/version/description
- `.mcp.json`, `CONNECTORS.md`, `README.md`, `commands/*.md`, `skills/start/*` — prose markası
- `skills/carbon-edupedia/{SKILL.md, skill-manifest.yaml, CHANGELOG.md, docs/CHANGELOG.md}` — name/version 3.0.0 + read_when
- `skills/carbon-edupedia/assets/module-template.html` — 5 yeni render + streak/stepper/mathml/spaced-rep/pacingDisk
- `skills/carbon-edupedia/scripts/validate_module.py` — gate_flow + gate_carbon_grid + yeni-tip tanıma
- `skills/carbon-edupedia/references/{curriculum-integration.md, module-architecture.md, interaction-patterns.md}` — yeni segment şemaları
- `../../.claude-plugin/marketplace.json` (CureoPrivate kökü) — edupedia kaydı

---

## FAZ 0 — Yeniden Adlandırma

### Task 1: paideia → edupedia + carbon-paideia → carbon-edupedia rename

**Files:**
- Move: `plugins/paideia/` → `plugins/edupedia/` (git mv)
- Move: `plugins/edupedia/skills/carbon-paideia/` → `plugins/edupedia/skills/carbon-edupedia/` (git mv)
- Modify: `plugins/edupedia/.claude-plugin/plugin.json`, `.mcp.json`, `README.md`, `CONNECTORS.md`, `commands/*.md`, `skills/start/SKILL.md`, `skills/start/skill-manifest.yaml`
- Modify: `plugins/edupedia/skills/carbon-edupedia/{SKILL.md, skill-manifest.yaml, CHANGELOG.md, docs/CHANGELOG.md}`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Produces: plugin adı `edupedia`, skill adı `carbon-edupedia`, namespace `edupedia:carbon-edupedia`/`edupedia:start`, plugin version `0.2.0`, skill version `3.0.0`.

- [ ] **Step 1: git mv dizinleri**

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate
git mv plugins/paideia plugins/edupedia
git mv plugins/edupedia/skills/carbon-paideia plugins/edupedia/skills/carbon-edupedia
```

- [ ] **Step 2: Manifest + marketplace + prose rename (sed)**

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/edupedia
# skill adı referansları (namespace, prose): carbon-paideia -> carbon-edupedia
grep -rl "carbon-paideia" . | xargs sed -i 's/carbon-paideia/carbon-edupedia/g'
# plugin adı/namespace: paideia -> edupedia (skill zaten çözüldü)
grep -rl "paideia:" . | xargs sed -i 's/paideia:/edupedia:/g'
# marka prose (Paideia -> Edupedia, /paideia: -> /edupedia:, "paideia plugin" -> "edupedia")
grep -rl -i "paideia" . | xargs sed -i 's/\bPaideia\b/Edupedia/g; s#/paideia:#/edupedia:#g; s/\bpaideia\b/edupedia/g'
```
Manuel gözden geçir: `plugin.json` `name:"edupedia"`, `displayName:"Edupedia"`, `version:"0.2.0"`; skill `SKILL.md` `name: carbon-edupedia`, `metadata.version: 3.0.0`; `skill-manifest.yaml` `skill.name/version` + `build.version: 3.0.0`. marketplace.json kökte: `name:"edupedia"`, `source:"./plugins/edupedia"`, `displayName:"Edupedia"`.

- [ ] **Step 3: Yol-referansı bütünlüğü + JSON/YAML geçerliliği doğrula**

Run:
```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/edupedia
echo "stale 'paideia' kalıntısı (0 beklenir):"; grep -rn "paideia" . | grep -v "carbon-edupedia\|CHANGELOG" | wc -l
python3 -c "import json;[json.load(open(f)) for f in ['.claude-plugin/plugin.json','.mcp.json']];print('JSON ok')"
python3 -c "import json;json.load(open('../../.claude-plugin/marketplace.json'));print('marketplace ok')"
for c in commands/*.md; do grep -q '\.\./\.\./' "$c" && echo "HATA: $c overshoot ../../" || true; done
```
Expected: stale sayısı 0; "JSON ok"; "marketplace ok"; hiçbir command overshoot uyarısı yok.

- [ ] **Step 4: plugin-validator ile yapı doğrula**

Run: `plugin-validator` agent'ını `/mnt/thunderbolt/workspaces/CureoPrivate/plugins/edupedia` üzerinde çalıştır.
Expected: plugin.json geçerli, `edupedia:carbon-edupedia`+`edupedia:start` keşfedilir, 4 komut yüklenir, `.mcp.json` geçerli.

- [ ] **Step 5: Commit**

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate
git add -A plugins/edupedia .claude-plugin/marketplace.json
git commit -m "refactor(edupedia): rename paideia→edupedia, carbon-paideia→carbon-edupedia (0.2.0/3.0.0-wip)"
```

---

## FAZ 1 — Test Harness

### Task 2: Validator gate test harness (fixtures + pytest + node-check)

**Files:**
- Create: `plugins/edupedia/skills/carbon-edupedia/tests/test_gates.py`
- Create: `plugins/edupedia/skills/carbon-edupedia/tests/fixtures/minimal_pass.html`
- Create: `plugins/edupedia/skills/carbon-edupedia/tests/check_engine.sh`

**Interfaces:**
- Consumes: `scripts/validate_module.py` — `Result()` (`.rows` list of `(gate,status,msg)`, `.add()`, `.fail`), gate fns `gate_X(html, R)`.
- Produces: `run_gate(gate_fn, html) -> list[(status,msg)]` helper; `status_of(rows, gate_id) -> str`; convention: fixtures in `tests/fixtures/`.

- [ ] **Step 1: Write the failing test (harness self-test)**

```python
# tests/test_gates.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import validate_module as vm

def run_gate(gate_fn, html):
    R = vm.Result(); gate_fn(html, R); return R.rows

def status_of(rows, gate_id):
    for g, s, _ in rows:
        if g == gate_id: return s
    return None

def test_harness_imports_existing_gate():
    # mevcut gate_emoji importlanır ve emojisiz girdiye PASS verir
    rows = run_gate(vm.gate_emoji, "<html><body><p>merhaba</p></body></html>")
    assert status_of(rows, "G-EMOJI") == "PASS"
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'validate_module'` yoksa `AttributeError` (dosya henüz yok / gate imzası). İlk çalıştırmada `tests/` yoksa collection error.

- [ ] **Step 3: Fixture + check_engine.sh yaz**

```html
<!-- tests/fixtures/minimal_pass.html : validate_module'ün mevcut 11 kapısını geçen asgari modül -->
<!-- (module-template.html'in üst-yapısını mirror eder; MODULE_DATA tek teach+mcq) -->
```
`minimal_pass.html`: `assets/module-template.html`'i kopyala, `MODULE_DATA.segments`'i tek `teach` + tek `mcq`'ya indir (canlı doğrulanabilir asgari modül).
```bash
# tests/check_engine.sh — motor inline script'ini çıkarıp node --check
set -e
T="${1:-../assets/module-template.html}"
python3 - "$T" > /tmp/_engine.js <<'PY'
import sys,re
h=open(sys.argv[1],encoding='utf-8').read()
for m in re.finditer(r'<script>(.*?)</script>', h, re.S): sys.stdout.write(m.group(1)+"\n")
PY
node --check /tmp/_engine.js && echo "ENGINE SYNTAX OK"
```

- [ ] **Step 4: Run to verify pass**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -v && bash tests/check_engine.sh`
Expected: `test_harness_imports_existing_gate PASSED`; `ENGINE SYNTAX OK`.

- [ ] **Step 5: Commit**

```bash
git add plugins/edupedia/skills/carbon-edupedia/tests
git commit -m "test(edupedia): gate test harness (fixtures + pytest + node --check)"
```

---

## FAZ 2 — Reference Dosyaları (normatif kaynak)

### Task 3: content-enrichment.md

**Files:**
- Create: `plugins/edupedia/skills/carbon-edupedia/references/content-enrichment.md`
- Modify: `skills/carbon-edupedia/skill-manifest.yaml` (references[] + read_when), `SKILL.md` (progressive-disclosure işaretçisi)

**Interfaces:**
- Produces: normatif lisans/entegrasyon tablosu; §"yapılamaz" listesi (G-FLOW/G-CARBON-GRID değil ama auditor + yazar referansı).

- [ ] **Step 1: Dosyayı yaz** — bölümler: (1) Amaç + self-contained kısıtı; (2) **Entegre edilebilir** tablo — Wikidata CC0 olgu-çipleri (build-zamanı SPARQL → MODULE_DATA'ya dondur; QID+tarih provenansı; kazanım metnine uzlaştır; no-fabrication), Wikimedia PD/CC-BY (seyrek, Tier-1 korunur, atıf zorunlu, **CC BY-SA kaçın**), native MathML (sıfır yük), spaced-rep veri modeli; (3) **Yapılamaz** listesi (atıflı): PhET (phet.colorado.edu/en/licensing/html — kaynak OSS değil/iframe), GeoGebra/Desmos (NC/runtime), Khan (CC BY-NC-SA), EBA/MEB (FSEK), Açık Ders (CC BY-NC-ND); (4) Dyslexia-font miti (OpenDyslexic kanıt yok — PMC5629233) → ispatlı kaldıraçlar (satır-aralığı/ölçü/seçim); (5) lisans özet tablosu (spec §10.1). Her olgu doğrulanmış URL ile.

- [ ] **Step 2: manifest + SKILL wire**

`skill-manifest.yaml` `references:` altına ekle:
```yaml
  - path: references/content-enrichment.md
    read_when: 'İçerik zenginleştirme: build-zamanı entegre edilebilir kaynaklar (Wikidata CC0, Wikimedia PD/CC-BY, MathML, spaced-rep) + lisans/entegrasyon kısıtları + dürüst "yapılamaz" listesi.'
```
`SKILL.md` ilgili bölüme bir satır işaretçi ekle (mevcut referans-listeleme desenini izle).

- [ ] **Step 3: Doğrula** — Run: `python3 -c "import yaml;yaml.safe_load(open('plugins/edupedia/skills/carbon-edupedia/skill-manifest.yaml'));print('yaml ok')"` · Expected: `yaml ok`; dosya var.

- [ ] **Step 4: Commit** — `git add … && git commit -m "docs(edupedia): content-enrichment.md — entegre-edilebilir kaynaklar + yapılamaz listesi"`

### Task 4: carbon-excellence.md (G-CARBON-GRID normatif kaynağı)

**Files:**
- Create: `plugins/edupedia/skills/carbon-edupedia/references/carbon-excellence.md`
- Modify: `skill-manifest.yaml`, `SKILL.md`

- [ ] **Step 1: 15-madde checklist'i yaz** (her madde ikili-denetlenebilir, spec §4.2 + §10.2, carbondesignsystem.com atıflı):
  1. İçerik 16-sütun (Lg) grid'de; blok genişlikleri tam-sütun span (ad-hoc px/% değil).
  2. Her media/figür/tile/hero Carbon en-boy oranı (1:1/2:1/2:3/3:2/4:3/16:9).
  3. Derinlik layer adımlarıyla (layer-01/02/03), gölge değil.
  4. Drop-shadow yalnız floating/geçici yüzeyde (tooltip/menu/modal); statik kartta 0 gölge.
  5. Yeniden-kullanılır kartlar contextual layer/field/border token'ları (hardcoded -01/-02 değil).
  6. Gövde metni ölçü-sınırlı (sütun-alt-kümesi span, tam-genişlik değil); metin-yoğun alanda geniş gutter.
  7. Bölümler-arası nefes (iç-yoğun bölüm olsa da sayfa duvardan-duvara değil).
  8. Motion: entrance-ease görünme, exit-ease ayrılma, standard kalıcı-hareket (her yerde tek easing değil).
  9. Liste/dizi reveal ~20ms/öğe stagger, toplam <500ms; tek geçiş 100–300ms.
  10. Expressive (akışkan) tip yalnız hero/başlık; gövde/quiz productive; bir bileşen iki tip-set karıştırmaz.
  11. Aksan renk anlam taşır (kategori/wayfinding), yapı/dolgu üstünde; birincil eylem Blue 60; küçük metin düşük-kontrast aksanda değil.
  12. Çok-seri grafik sabit kategorik sıra (Purple70,Cyan50,Teal70,Magenta70,Red50…); sıralı veri sequential-mono; ±/orta-nokta diverging.
  13. Her grafikte içgörü-taşıyan (qualitative) başlık + eksen başlıkları/birimler + renk→anlam legend; renk tek-kodlayıcı değil.
  14. İkonlar bağlam başına tek boyut, tam-piksel, monokromatik ≥4.5:1; boyut komşu metinle eşleşir (16–20px ikon ↔ 14–16px metin).
  15. Expressive piktogramlar büyük+seyrek; varsayılan productive line stili.
  Ayrıca: "makine-denetlenebilir alt-küme" bölümü (G-CARBON-GRID hangi maddeleri regex/heuristik denetler: 1,2,3/4,9,10).

- [ ] **Step 2: manifest + SKILL wire** (read_when: 'Carbon estetik mükemmelliği: 15-madde uzman-vs-jenerik checklist (2x grid, en-boy oranı, layer-elevation, koreografi, expressive/productive, veri-viz palet); G-CARBON-GRID normatif kaynağı.')

- [ ] **Step 3: Doğrula** — yaml ok; dosya var; 15 madde mevcut (`grep -c "^[0-9]" ...`).

- [ ] **Step 4: Commit** — `git commit -m "docs(edupedia): carbon-excellence.md — 15-madde uzman-Carbon checklist"`

### Task 5: gamified-flows.md (G-FLOW normatif kaynağı)

**Files:**
- Create: `plugins/edupedia/skills/carbon-edupedia/references/gamified-flows.md`
- Modify: `skill-manifest.yaml`, `SKILL.md`

- [ ] **Step 1: Yaz** (spec §4.3 + §10.3, RCT atıflı): (A) 4 akış şablonu (Keşif Döngüsü hook→teach→interaction→micro-win; Sefer mission+avatar+mini-map+N-istasyon+kamp-molası+checkpoint+kapanış; Antrenman warm-up+uyarlanır-merdiven+gain-only-streak+öz-rekabet; Birlikte Odak co-play sarmalayıcı) segment-dizisi eşlemesiyle; (B) mekanikler + ADHD gerekçe + HTML tezahürü (merak-boşluğu segment-içinde-kapanır, hedef-gradyanı+bahşedilmiş-ilerleme, görünmez-taban-korumalı uyarlanır-zorluk, kaygısız tempo-diski); (C) **atıflı YAPMA listesi** (cross-session streak/loss-aversion — Hanus&Fox 2015; liderlik tablosu; değişken-oran/loot-box; geri-sayım; aşırı-juicing; overjustification — Deci 1999; hyperfocus-sömürüsü; açık merak-boşluğu); (D) "makine-denetlenebilir alt-küme" (G-FLOW ne denetler).

- [ ] **Step 2: manifest + SKILL wire** (read_when: '4 ADHD akış şablonu (Keşif/Sefer/Antrenman/Birlikte-Odak) + oyunlaştırma mekanikleri + atıflı YAPMA listesi; G-FLOW normatif kaynağı.')

- [ ] **Step 3: Doğrula** — yaml ok; 4 şablon + YAPMA listesi mevcut.

- [ ] **Step 4: Commit** — `git commit -m "docs(edupedia): gamified-flows.md — 4 akış şablonu + atıflı YAPMA listesi"`

---

## FAZ 3 — Validator Kapıları (TDD; motordan önce, fixture-tabanlı)

### Task 6: G-FLOW kapısı

**Files:**
- Modify: `skills/carbon-edupedia/scripts/validate_module.py` (yeni `gate_flow` + main'e ekle)
- Create: `tests/fixtures/flow_pass.html`, `tests/fixtures/flow_fail_openhook.html`, `tests/fixtures/flow_fail_lossstreak.html`
- Modify: `tests/test_gates.py`

**Interfaces:**
- Consumes: `Result` (Task 2).
- Produces: `gate_flow(html, R)` — koşullu (gamification imzası yoksa PASS/skip); FAIL koşulları: açık merak-boşluğu (`data-hook` var ama `data-hook-resolved` yok), loss/ceza streak dili, sayılı/kesintili pacingDisk, uyarlanır-zorluk etiketi.

- [ ] **Step 1: Failing testler**

```python
def test_gflow_skips_when_no_gamification():
    rows = run_gate(vm.gate_flow, open("tests/fixtures/minimal_pass.html").read())
    assert status_of(rows, "G-FLOW") == "PASS"  # imza yok → uygulanmaz/PASS

def test_gflow_fail_on_open_curiosity_gap():
    rows = run_gate(vm.gate_flow, open("tests/fixtures/flow_fail_openhook.html").read())
    assert status_of(rows, "G-FLOW") == "FAIL"

def test_gflow_fail_on_loss_streak_language():
    rows = run_gate(vm.gate_flow, open("tests/fixtures/flow_fail_lossstreak.html").read())
    assert status_of(rows, "G-FLOW") == "FAIL"

def test_gflow_pass_on_wellformed_flow():
    rows = run_gate(vm.gate_flow, open("tests/fixtures/flow_pass.html").read())
    assert status_of(rows, "G-FLOW") == "PASS"
```
Fixtures: `flow_fail_openhook.html` içinde `data-seg="hook"` bloğu var ama karşılık gelen `data-hook-resolved` işareti yok; `flow_fail_lossstreak.html` içinde "serini kaybettin" metni; `flow_pass.html` kapalı hook + gain-only streak.

- [ ] **Step 2: Run → fail** — Run: `python3 -m pytest tests/test_gates.py -k gflow -v` · Expected: FAIL — `AttributeError: module 'validate_module' has no attribute 'gate_flow'`.

- [ ] **Step 3: gate_flow implement**

```python
# validate_module.py — gate_curriculum'dan sonra ekle
FLOW_LOSS_RE = re.compile(r"(seri(n|ni)?\s*(kaybett|sıfırla|bozdu)|kaybettin|streak\s*lost|başarısız oldun)", re.I)
FLOW_LABEL_RE = re.compile(r"(zorlan[ıi]yorsun|çok kolay geliyor|seviyen düştü)", re.I)
def gate_flow(html, R):
    """Koşullu: gamification akış değişmezleri (merak-boşluğu kapanır, gain-only streak,
    kaygısız pacingDisk, uyarlanır-zorluk etiketlemez). İmza yoksa uygulanmaz."""
    has_hook = 'data-seg="hook"' in html or "data-hook" in html
    has_streak = "streakChip" in html or "streak-chip" in html
    has_disk = "pacingDisk" in html or "pacing-disk" in html
    if not (has_hook or has_streak or has_disk):
        R.add("G-FLOW","PASS","Gamification akış imzası yok (uygulanmaz)."); return
    issues=[]
    # açık merak-boşluğu: her hook 'data-hook-resolved' ile kapanmalı
    n_hook = html.count('data-seg="hook"')
    n_res  = html.count("data-hook-resolved")
    if n_hook and n_res < n_hook: issues.append(f"{n_hook - n_res} merak-boşluğu kapanmıyor (data-hook-resolved eksik)")
    if FLOW_LOSS_RE.search(html): issues.append("streak/kayıp cezalandırıcı dili (gain-only olmalı)")
    if FLOW_LABEL_RE.search(html): issues.append("uyarlanır-zorluk kullanıcıyı etiketliyor")
    if has_disk and re.search(r"pacing-disk[^>]*data-countdown", html): issues.append("tempo diski geri-sayım (kaygısız/kesintisiz olmalı)")
    if issues: R.add("G-FLOW","FAIL","; ".join(issues))
    else: R.add("G-FLOW","PASS","Akış değişmezleri: merak-boşluğu kapanıyor, gain-only streak, kaygısız disk.")
```
main'de gate listesine `gate_flow(html, R)` ekle (gate_curriculum'dan sonra).

- [ ] **Step 4: Run → pass** — Run: `python3 -m pytest tests/test_gates.py -k gflow -v` · Expected: 4 PASS.

- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): G-FLOW validator kapısı + fixtures (12→ kapı)"`

### Task 7: G-CARBON-GRID kapısı

**Files:**
- Modify: `scripts/validate_module.py` (`gate_carbon_grid` + main)
- Create: `tests/fixtures/grid_pass.html`, `tests/fixtures/grid_fail_shadow.html`
- Modify: `tests/test_gates.py`

**Interfaces:**
- Produces: `gate_carbon_grid(html, R)` — WARN→FAIL; makine-denetlenebilir alt-küme: statik kartta drop-shadow (FAIL), 2x-grid konteyner yokluğu (WARN), en-boy oranı (WARN), koreografi >500ms (WARN).

- [ ] **Step 1: Failing testler**

```python
def test_gcarbongrid_fail_on_static_card_shadow():
    rows = run_gate(vm.gate_carbon_grid, open("tests/fixtures/grid_fail_shadow.html").read())
    assert status_of(rows, "G-CARBON-GRID") == "FAIL"

def test_gcarbongrid_pass_on_layered_flat():
    rows = run_gate(vm.gate_carbon_grid, open("tests/fixtures/grid_pass.html").read())
    assert status_of(rows, "G-CARBON-GRID") in ("PASS","WARN")
```
`grid_fail_shadow.html`: `.card{box-shadow:0 2px 6px …}` statik kartta. `grid_pass.html`: layer token'ları + floating-only gölge.

- [ ] **Step 2: Run → fail** — Expected: `AttributeError … gate_carbon_grid`.

- [ ] **Step 3: gate_carbon_grid implement**

```python
STATIC_SHADOW_RE = re.compile(r"\.(card|seg|tile|teach)[^{]*\{[^}]*box-shadow\s*:\s*(?!none)", re.I|re.S)
def gate_carbon_grid(html, R):
    """WARN→FAIL: Carbon kompozisyon disiplini (carbon-excellence.md makine-alt-kümesi).
    Statik kart gölgesi = FAIL (layer-elevation ihlali); grid/aspect-ratio/koreografi = WARN."""
    fails=[]; warns=[]
    if STATIC_SHADOW_RE.search(html): fails.append("statik kartta drop-shadow (layer-elevation kullan; gölge yalnız floating)")
    if "cds--grid" not in html and "carbon-grid" not in html and "grid-template-columns" not in html:
        warns.append("2x grid konteyneri saptanmadı (ad-hoc genişlik riski)")
    if "aspect-ratio" not in html:
        warns.append("Carbon en-boy oranı (aspect-ratio) kullanılmıyor")
    for m in re.finditer(r"transition[^;]*?(\d+)ms", html):
        if int(m.group(1))>500: warns.append(f"koreografi {m.group(1)}ms >500ms"); break
    if fails: R.add("G-CARBON-GRID","FAIL","; ".join(fails))
    elif warns: R.add("G-CARBON-GRID","WARN","; ".join(warns[:3]))
    else: R.add("G-CARBON-GRID","PASS","Carbon kompozisyon: layer-elevation, grid, en-boy oranı, koreografi <500ms.")
```
main'e `gate_carbon_grid(html, R)` ekle.

- [ ] **Step 4: Run → pass** — Run: `python3 -m pytest tests/test_gates.py -k gcarbongrid -v` · Expected: 2 PASS.

- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): G-CARBON-GRID validator kapısı (→13 kapı)"`

---

## FAZ 4 — Motor Kümesi A: Oyunlaştırma Omurgası

> Not: `renderStreak`/`renderStepper`/TTS **zaten var** (module-template.html); bu görevler genişletir. `render()` dispatch tablosu satır ~1148'de `{teach:renderTeach,…}`; yeni tipler oraya eklenir.

### Task 8: `hook` segment tipi (merak-boşluğu)

**Files:**
- Modify: `assets/module-template.html` (renderHook + dispatch), `references/module-architecture.md` + `interaction-patterns.md` (şema), `references/curriculum-integration.md` (Keşif Döngüsü)
- Modify: `tests/test_gates.py` (+ hook fixture)

**Interfaces:**
- Consumes: mevcut `segHead(s,kicker)`, `instr(s)`, `ttsRow(text,lang)`, `setNav()`, `goNext()`.
- Produces: `renderHook(stage, s)`; MODULE_DATA `{type:"hook", id, title?, question, predict?:{options:[...], hintOnPick?}, resolvesIn}`; stage `data-hook-resolved` işareti hedef teach render edilince.

- [ ] **Step 1: Failing test (fixture render + G-FLOW kapanış)**

```python
def test_hook_segment_renders_and_closes():
    html = open("tests/fixtures/hook_pass.html").read()
    assert 'data-seg="hook"' in html and "data-hook-resolved" in html
    rows = run_gate(vm.gate_flow, html); assert status_of(rows,"G-FLOW")=="PASS"
```
`hook_pass.html`: template kopyası, MODULE_DATA'da bir `hook` + onu çözen `teach` (id `resolvesIn` ile); motor render sonrası her iki işaret DOM'da (statik fixture için elle işaretlenir).

- [ ] **Step 2: Run → fail** — Expected: fixture yok / işaret yok.

- [ ] **Step 3: renderHook implement + dispatch** (mevcut `renderTeach`/`renderFillblank` yapısını mirror et — segHead + gövde + setNav)

```javascript
/* ---- hook: merak-boşluğu (segment içinde kapanır) ---- */
function renderHook(stage, s){
  const predict = s.predict ? `<div class="hook-predict" role="group" aria-label="Tahmin">${
    (s.predict.options||[]).map((o,i)=>`<button class="hook-opt" data-i="${i}" type="button">${esc(o)}</button>`).join("")
  }</div>` : "";
  stage.innerHTML = segHead(s, "Merak")
    + `<div class="hook-card" data-resolves="${esc(s.resolvesIn||"")}">`
    + `<p class="hook-q">${icon("ic-idea")}<span>${esc(s.question)}</span></p>`
    + ttsRow(s.question) + predict
    + `<p class="hook-note">${s.predict?"Tahminini seç — az sonra öğreneceğiz.":"Az sonra çözeceğiz."}</p></div>`;
  stage.querySelectorAll(".hook-opt").forEach(b=>b.addEventListener("click",()=>{
    stage.querySelectorAll(".hook-opt").forEach(x=>x.classList.remove("hook-opt--pick"));
    b.classList.add("hook-opt--pick"); addXP(0,{silent:true}); // notsuz; merak açık, ceza yok
  }));
  // çözüm işareti: bu hook'un resolvesIn'i bir sonraki teach'te DOM'a data-hook-resolved yazar (Step 3b)
  setNav({nextLabel:"Öğren"});
}
```
dispatch tablosuna ekle: `hook:renderHook,`. **Step 3b:** `renderTeach` başına, eğer bu teach bir hook'un hedefiyse çözüm işaretini yaz:
```javascript
// renderTeach içinde, stage doldurulduktan sonra:
if (segs.some(x=>x.type==="hook" && x.resolvesIn===s.id)) stage.setAttribute("data-hook-resolved", s.id);
```
CSS: `.hook-card`, `.hook-opt` için mevcut token'ları kullan (accent-tint, layer-01; **gölge yok**).

- [ ] **Step 4: Run → pass + node --check** — Run: `bash tests/check_engine.sh && python3 -m pytest tests/test_gates.py -k "hook or gflow" -v` · Expected: ENGINE SYNTAX OK + PASS.

- [ ] **Step 5: Şema doc + commit** — module-architecture.md §2'ye `hook` şeması + interaction-patterns.md'ye mekaniği ekle. `git commit -m "feat(edupedia): hook segment (merak-boşluğu, segment-içi kapanır)"`

### Task 9: Progress sistemi — stepper milestones + goal-gradient + gain-only streak

**Files:**
- Modify: `assets/module-template.html` (`renderStepper` genişlet, `resetStreak` gain-only)
- Modify: `tests/test_gates.py`

**Interfaces:**
- Consumes: mevcut `renderStepper()`, `renderStreak()`, `resetStreak()`, `state.streak`, `updateRail()`.
- Produces: `meta.milestones?:[{atSegmentId, label}]` desteği; near-goal etiketi; `resetStreak()` → hold (0'a sıfırlamaz).

- [ ] **Step 1: Failing test**

```python
def test_gain_only_streak_no_reset_language():
    html = open("tests/fixtures/streak_gainonly.html").read()
    rows = run_gate(vm.gate_flow, html); assert status_of(rows,"G-FLOW")=="PASS"
    assert "streak=0" not in html.lower().replace(" ","")  # resetStreak artık 0'a set etmez
```

- [ ] **Step 2: Run → fail** — Expected: mevcut `resetStreak` `state.streak=0` içerir → assertion fail.

- [ ] **Step 3: Implement**
- `resetStreak()` → gain-only: streak'i **sıfırlama**; yalnız nötr "korundu" durumuna al (dots kalır). Mevcut gövdeyi değiştir:
```javascript
function resetStreak(){ /* gain-only: seri bozulmaz, nötr korunur */ const chip=$("#streakChip");
  if(chip) chip.setAttribute("data-held","true"); }
```
Çağıran yanlış-cevap yolları `resetStreak()`'i çağırmaya devam eder ama artık sıfırlamaz.
- `renderStepper()` sonuna near-goal etiketi + milestone işareti:
```javascript
// renderStepper() sonunda:
const left = segs.length - 1 - state.idx;
const gg=$("#railGoal"); if(gg){ gg.textContent = (left>0 && left<=2) ? "Son "+left+" durak" : ""; }
(D.meta.milestones||[]).forEach(m=>{ const i=segs.findIndex(x=>x.id===m.atSegmentId);
  if(i>=0){ const st=box.children[i]; if(st) st.classList.add("step--milestone"); } });
```
`#railGoal` öğesini üst-çubuk raya ekle (mevcut `#railText` yanına). CSS `.step--milestone` = accent nokta (gölgesiz).

- [ ] **Step 4: Run → pass + node --check** — Expected: ENGINE SYNTAX OK; G-FLOW PASS; "streak=0" yok.

- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): gain-only streak + stepper milestones/goal-gradient"`

### Task 10: Opt-in katmanlar — pacingDisk + Sefer mini-harita

**Files:**
- Modify: `assets/module-template.html` (`renderPacingDisk`, `renderQuestMap`; `learner.pacingDisk`, `meta.quest`)
- Modify: `tests/test_gates.py`

**Interfaces:**
- Produces: `learner.pacingDisk?:false` (varsayılan KAPALI); `meta.quest?:{stations:[{id,label}]}` → SVG mini-map; **sayısız/kesintisiz disk, hard-stop yok**.

- [ ] **Step 1: Failing test** — `test_pacingdisk_no_countdown`: `pacing_pass.html`'de `pacing-disk` var, `data-countdown` yok → G-FLOW PASS.

- [ ] **Step 2: Run → fail** — fixture/impl yok.

- [ ] **Step 3: Implement** — `renderPacingDisk()`: SVG daire, `estimatedMinutes` üstünden **tükenen** yay (requestAnimationFrame; `reduceMotion()` ise statik), numeric yok, alarm yok, dismiss butonu; yalnız `learner.pacingDisk===true` ise DOM'a girer. `renderQuestMap()`: `meta.quest.stations` → yatay SVG düğüm zinciri; tamamlanan istasyon `state.done`'a göre `--accent` dolgu (gölgesiz); üst-çubuk altına opsiyonel şerit. `render()` içinde çağır.

- [ ] **Step 4: Run → pass + node --check**

- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): opt-in tempo diski (kaygısız) + Sefer mini-harita"`

---

## FAZ 5 — Motor Kümesi B: Derin Öğretim

### Task 11: `worked` segment (soluk-çözümlü örnek)

**Files:** Modify `assets/module-template.html` (renderWorked + dispatch), `module-architecture.md`, `tests/test_gates.py`

**Interfaces:** `renderWorked(stage,s)`; `{type:"worked", id, title?, steps:[{text, html?}], fadeFrom:int}` — `fadeFrom` indeksinden itibaren adımlar boş input; öğrenci tamamlar; tümü doğru → XP + açıklama reveal.

- [ ] **Step 1: Failing test** — `worked_pass.html` G-INTERACT/G-A11Y PASS + `data-seg="worked"`.
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** (renderMCQ/renderFillblank yapısını mirror — segHead + adım listesi; `fadeFrom` öncesi adımlar salt-görünür, sonrası `<input aria-label>`; kontrol butonu; her input klavye-erişilebilir; anında geri bildirim + `addXP`).
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): worked segment (fade-scaffold çözümlü örnek)"`

### Task 12: `selfExplain` segment (öz-açıklama)

**Files:** Modify `assets/module-template.html` (renderSelfExplain + dispatch), doc, tests

**Interfaces:** `renderSelfExplain(stage,s)`; `{type:"selfExplain", id, prompt, modelExplanation}` — istem + serbest `<textarea>` (notsuz/opsiyonel) + "Modeli gör" reveal butonu; ilerleme bloklamaz.

- [ ] **Step 1: Failing test** — `selfexplain_pass.html`: textarea + reveal, **puanlama yok** (G-WELLBEING PASS, no-punitive).
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** (segHead + prompt + ttsRow + textarea[aria-label] + reveal button → modelExplanation; `setNav` next hep etkin — düşük baskı).
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): selfExplain segment (öz-açıklama, notsuz)"`

### Task 13: Görünmez uyarlanır zorluk (mcq/fillblank tier)

**Files:** Modify `assets/module-template.html` (`renderMCQ`/`renderFillblank` tier mantığı), doc, tests

**Interfaces:** soru şemasına opsiyonel `tier?:1|2|3`; `state.perf` yuvarlanan pencere; 2 yanlış → ipucu-önce/kolay; 2 ilk-doğru → opsiyonel "meydan okuma" item; **taban hep kolay; asla etiketleme** (G-FLOW FLOW_LABEL_RE).

- [ ] **Step 1: Failing test** — `adaptive_pass.html`: tier'lı sorular + G-FLOW PASS (etiket yok).
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** — `state.perf=[]` (son N doğru/yanlış); soru seçiminde tier-filtre; yanlış→ipucu göster (mevcut explanation erken); "meydan okuma" opsiyonel buton (atlanabilir). Kullanıcıya görünür zorluk-etiketi YAZMA.
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): görünmez taban-korumalı uyarlanır zorluk"`

---

## FAZ 6 — Motor Kümesi D: Erişilebilirlik + Tekrar

### Task 14: TTS'i yeni segmentlere yay (D1 — küçük; TTS altyapısı zaten var)

**Files:** Modify `assets/module-template.html` (renderHook/renderWorked/renderSelfExplain/renderSim'e `ttsRow` ekle), tests

**Interfaces:** Consumes mevcut `ttsRow(text,lang)`/`TTS_OK`. Yeni segment render'larında birincil metin için `ttsRow`.

- [ ] **Step 1: Failing test** — `test_new_segments_have_tts`: hook/worked/selfExplain fixture'larında `class="tts-oku"` (TTS_OK true iken) veya `ttsRow` çağrısı motor kaynağında mevcut.
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** — Task 8/11/12/16 render'larına `ttsRow(...)` çağrısı ekle (zaten Task 8/12'de var; worked/sim'e ekle). Doğrula tümü tutarlı.
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): TTS'i yeni segment tiplerine yay"`

### Task 15: Çapraz-oturum aralıklı tekrar (flashcards Leitner)

**Files:** Modify `assets/module-template.html` (`renderFlashcards` + Leitner + localStorage), doc, tests

**Interfaces:** `flashcards` → kart durumu `localStorage["edupedia:"+moduleId+":leitner"]`; feature-detect; yoksa in-session degrade. `state.leitner={box:{}, due:[]}`.

- [ ] **Step 1: Failing test** — `test_spacedrep_degrades_without_storage`: motor kaynağı `try{localStorage…}catch` ile sarılı + `IndexedDB` KULLANMAZ (`grep -c IndexedDB == 0`).
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** — `lsGet/lsSet` güvenli sarmalayıcılar (try/catch → null); `renderFlashcards`'a Leitner kutu mantığı (doğru→üst kutu, yanlış→kutu 1; `due` sıralaması); modül anahtarı `D.meta.title` hash'i; `localStorage` yoksa mevcut in-session davranışa düşer.
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): flashcards çapraz-oturum Leitner (localStorage, degrade-safe)"`

### Task 16: MathML desteği

**Files:** Modify `assets/module-template.html` (`mathml` helper + body render), `interaction-patterns.md`, tests

**Interfaces:** `body`/`mathExpr` içinde inline `<math>…</math>` geçişi (motor sanitize'i `<math>` izin verir); `mathExpr` varsayılan kalır, MathML ileri notasyon için.

- [ ] **Step 1: Failing test** — `mathml_pass.html`: `<math>` içeren teach body, G-A11Y/G-SELFCONTAINED PASS (sıfır harici).
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** — body render'ında `<math>` etiketine izin (mevcut esc/sanitize whitelist'ine `math,mrow,mi,mo,mn,msup,msub,mfrac,msqrt,mtable,mtr,mtd` ekle); `mathExpr` fallback korunur.
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): native MathML (ileri notasyon, sıfır yük)"`

---

## FAZ 7 — Motor Kümesi C: Etkileşimli Manipülatifler (en yüksek risk, en son)

### Task 17: `sim` segment + preset kütüphanesi

**Files:** Modify `assets/module-template.html` (renderSim + SIM_PRESETS + dispatch), `module-architecture.md`, tests

**Interfaces:** `renderSim(stage,s)`; `{type:"sim", id, simType:"pendulum|projectile|wave|numberScale|functionPlot", params:[{key,min,max,step,default,label}], labels}`; `SIM_PRESETS[simType](svgEl, values)` motor-içi render fn (MODULE_DATA kod taşımaz); slider `<input type=range aria-label>` + klavye; `reduceMotion()` → anlık redraw (animasyon yok).

- [ ] **Step 1: Failing test** — `sim_pass.html`: `data-seg="sim"` + range input[aria-label] + G-A11Y/G-SVG PASS (SVG role+title).
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** — `SIM_PRESETS` sabiti (5 preset, her biri `(svg, v)=>{…}` token-renkli SVG çizer); `renderSim` slider'ları `params`'tan kurar, `oninput`→preset redraw; `role="img"`+`<title>`; klavye slider yerleşik. Bilinmeyen `simType` → nazik "preset yok" notu (uydurma yok).
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): sim segment + 5-preset parametrik SVG kütüphanesi"`

### Task 18: `conceptMap` segment (klavye-erişilebilir kurucu)

**Files:** Modify `assets/module-template.html` (renderConceptMap + dispatch), doc, tests

**Interfaces:** `renderConceptMap(stage,s)`; `{type:"conceptMap", id, nodes:[{id,label}], targetEdges:[[a,b]], instructions?}`; sürükle-bağla **VE klavye fallback** (kaynak-seç→hedef-seç→bağla); `targetEdges`'e karşı doğrula; anında geri bildirim + XP.

- [ ] **Step 1: Failing test** — `conceptmap_pass.html`: `data-seg="conceptMap"` + klavye-seç butonları (`aria-label`) + G-A11Y PASS (drag'e bağımlı değil).
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** — düğümleri SVG/DOM'a yerleştir; her düğüm `<button aria-label>` (klavye kaynak-seç→hedef-seç bağlar; pointer sürükle opsiyonel zenginleştirme); "Bağla" → `targetEdges` ile karşılaştır; doğru kenar accent, eksik/yanlış nötr geri bildirim (cezasız); tümü doğru → `addXP`+`markMastered`. Klavye yol ZORUNLU (mevcut `match`/`order` deseni).
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): conceptMap kurucu segment (klavye-erişilebilir)"`

### Task 19: Etkileşimli sayı-doğrusu/geometri

**Files:** Modify `assets/module-template.html` (`renderNumberline` genişlet), doc, tests

**Interfaces:** `numberline`/geometri şemasına `interactive?:true`; sürüklenebilir/klavye-adımlı nokta + canlı ölçüm.

- [ ] **Step 1: Failing test** — `numberline_interactive_pass.html`: `interactive` işaret + klavye-adım (`tabindex`/`aria-valuenow`) + G-A11Y/G-SVG PASS.
- [ ] **Step 2: Run → fail**
- [ ] **Step 3: Implement** — `renderNumberline` içine `s.interactive` dalı: nokta `role="slider"` + `aria-valuemin/max/now` + ok-tuşu adım + pointer sürükle; canlı değer metni; `reduceMotion` uyumlu.
- [ ] **Step 4: Run → pass + node --check**
- [ ] **Step 5: Commit** — `git commit -m "feat(edupedia): etkileşimli sayı-doğrusu/geometri (klavye-adımlı)"`

---

## FAZ 8 — Agent + Hook'lar

### Task 20: module-auditor agent

**Files:** Create `plugins/edupedia/agents/module-auditor.md`

**Interfaces:** Consumes `scripts/validate_module.py`, `references/{carbon-excellence,gamified-flows}.md`. Produces izole-bağlam denetim → öncelikli fix listesi (ana bağlama ≤1-sayfa).

- [ ] **Step 1: Agent frontmatter + gövde yaz** (plugin-dev agent-development deseni; sibling agent'larla uyumlu `description` + "when to use" örnekleri; `tools: Read, Bash, Grep, Glob`; `${CLAUDE_PLUGIN_ROOT}` yolları). Gövde: 4 denetim ekseni (13-kapı validate_module + carbon-excellence 15-madde + gamified-flows A/B/C/D + wellbeing/kaynak-sadakati); girdi=modül HTML yolu; çıktı=öncelikli fix listesi.
- [ ] **Step 2: Doğrula** — Run: `python3 -c "import re;t=open('plugins/edupedia/agents/module-auditor.md').read();assert t.startswith('---') and 'description:' in t;print('frontmatter ok')"` · Expected: `frontmatter ok`.
- [ ] **Step 3: plugin-validator** — agent keşfedilir.
- [ ] **Step 4: Commit** — `git commit -m "feat(edupedia): module-auditor QA agent (izole 13-kapı denetim)"`

### Task 21: hooks.json + preflight + validate script'leri

**Files:** Create `plugins/edupedia/hooks/hooks.json`, `hooks/preflight.sh`, `hooks/validate-module.sh`

**Interfaces:** SessionStart→preflight (connector notu, fail-open); PostToolUse Write|Edit→modül ise validate_module.py, değilse no-op.

- [ ] **Step 1: hooks.json yaz**

```json
{
  "SessionStart": [{ "hooks": [{ "type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/preflight.sh\"", "timeout": 10 }] }],
  "PostToolUse": [{ "matcher": "Write|Edit", "hooks": [{ "type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/validate-module.sh\"", "timeout": 30 }] }]
}
```

- [ ] **Step 2: preflight.sh (fail-open) + validate-module.sh (gate) yaz**

```bash
# preflight.sh — connector bilgilendirmesi (fail-open, deterministik)
echo "Edupedia: maarif-mufredat connector'ı için /edupedia:durum ile canlılık+Tier-2 (get_figure) kontrol edebilirsiniz. MCP olmadan da offline üretim çalışır."
exit 0
```
```bash
# validate-module.sh — PostToolUse: yazılan dosya modül ise doğrula
set -e
# hook stdin JSON'undan dosya yolunu çek (tool_input.file_path)
FILE=$(cat | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || true)
[ -z "$FILE" ] && exit 0
case "$FILE" in *.html) ;; *) exit 0;; esac
grep -q "MODULE_DATA" "$FILE" 2>/dev/null || exit 0   # modül imzası yoksa no-op
V="${CLAUDE_PLUGIN_ROOT}/skills/carbon-edupedia/scripts/validate_module.py"
python3 "$V" "$FILE" || echo "Edupedia doğrulama: yukarıdaki kapı ihlallerini gözden geçirin (bloke etmez)."
exit 0
```

- [ ] **Step 3: Kuru-çalıştırma testi**

Run:
```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/edupedia
python3 -c "import json;json.load(open('hooks/hooks.json'));print('hooks.json ok')"
CLAUDE_PLUGIN_ROOT=$(pwd) bash hooks/preflight.sh
# modül-olmayan → no-op
echo '{"tool_input":{"file_path":"/tmp/x.txt"}}' | CLAUDE_PLUGIN_ROOT=$(pwd) bash hooks/validate-module.sh; echo "exit=$?"
# modül → doğrula
echo "{\"tool_input\":{\"file_path\":\"$(pwd)/skills/carbon-edupedia/tests/fixtures/minimal_pass.html\"}}" | CLAUDE_PLUGIN_ROOT=$(pwd) bash hooks/validate-module.sh
```
Expected: `hooks.json ok`; preflight notu; txt→exit=0 no-op; minimal_pass→13-kapı raporu.

- [ ] **Step 4: Commit** — `git commit -m "feat(edupedia): hooks — SessionStart preflight + PostToolUse otomatik doğrulama"`

---

## FAZ 9 — Sürüm + Entegrasyon Doğrulama

### Task 22: Şablona canlı örnekler + 13/13 entegrasyon + sürüm/CHANGELOG

**Files:** Modify `assets/module-template.html` (örnek MODULE_DATA'ya yeni segment örnekleri), `CHANGELOG.md`+`docs/CHANGELOG.md` (3.0.0), `SKILL.md`+`skill-manifest.yaml` (3.0.0 teyit), `shared/run-manifest-schema.json` (G-FLOW/G-CARBON-GRID quality_gates)

**Interfaces:** Consumes tüm önceki task'ler. Produces: 13/13 geçen referans modül + 3.0.0 sürüm damgası.

- [ ] **Step 1: Failing test (tam entegrasyon)**

```python
def test_full_template_passes_13_gates():
    import subprocess
    r = subprocess.run(["python3","scripts/validate_module.py","assets/module-template.html"],
                       capture_output=True, text=True)
    assert r.returncode == 0                       # hiç FAIL yok
    for g in ["G-FLOW","G-CARBON-GRID"]: assert g in r.stdout   # yeni kapılar raporlanıyor
```

- [ ] **Step 2: Run → fail** — Expected: yeni kapılar raporda yoksa / bir örnek FAIL ederse.

- [ ] **Step 3: Şablon örnekleri + sürüm** — module-template.html örnek MODULE_DATA'sına birer `hook`/`worked`/`selfExplain`/`sim`/`conceptMap` örneği ekle (canlı render + 13/13). CHANGELOG'a 3.0.0 girişi (spec özeti; geriye-uyum notu; "8 mod/mevcut 11 kapı korundu, 2 kapı+5 segment eklendi"). run-manifest-schema.json `quality_gates` bloğuna `G-FLOW`+`G-CARBON-GRID`. SKILL.md/manifest 3.0.0 teyit.

- [ ] **Step 4: Run → pass (tam suite)**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/ -v && bash tests/check_engine.sh && python3 scripts/validate_module.py assets/module-template.html`
Expected: tüm testler PASS; ENGINE SYNTAX OK; 13/13 (0 İHLAL).

- [ ] **Step 5: plugin-validator + Commit**

Run: plugin-validator `plugins/edupedia`; sonra:
```bash
git add -A plugins/edupedia
git commit -m "feat(edupedia): carbon-edupedia 3.0.0 — 13-kapı entegrasyon + canlı segment örnekleri + CHANGELOG"
```

### Task 23: Kabul kriterleri (E1–E10) + push

- [ ] **Step 1: E1–E10 kontrol listesini koştur**

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/edupedia
# E1/E2: keşif + stale-ref
grep -rn "\bpaideia\b" . | grep -v CHANGELOG | wc -l   # 0 beklenir
# E5: 13 kapı
python3 skills/carbon-edupedia/scripts/validate_module.py skills/carbon-edupedia/assets/module-template.html | grep -c "GEÇTİ\|UYARI\|İHLAL"  # 13
# E4/E9: node --check + degrade grepleri
bash skills/carbon-edupedia/tests/check_engine.sh
grep -c "IndexedDB" skills/carbon-edupedia/assets/module-template.html   # 0
# E7: agent, E8: hooks
python3 -c "import json;json.load(open('hooks/hooks.json'))"
test -f agents/module-auditor.md && echo "agent ok"
```
Expected: stale 0; 13 kapı; ENGINE OK; IndexedDB 0; agent ok. Her E-kriterini spec §9'a göre işaretle.

- [ ] **Step 2: Nihai commit + push**

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate
git add -A && git commit -m "chore(edupedia): 3.0.0 kabul kriterleri E1-E10 doğrulandı" --allow-empty
git push origin main
```
Expected: push başarılı; `## main...origin/main` senkron.

---

## Self-Review Notları

- **Spec kapsamı:** §3 rename→Task1; §4.1-4.3 reference→Task3-5; §5 küme A→Task8-10, B→Task11-13, C→Task17-19, D→Task14-16; §6 kapılar→Task6-7; §7 agent→Task20; §8 hook→Task21; §9 kabul→Task22-23; §10 araştırma→reference içeriği. Tüm spec bölümleri kapsanıyor.
- **TTS gerçeği:** Task14 küçültüldü (altyapı zaten var — module-template.html `ttsBtn`/`speakText`/`TTS_OK`); yalnız yeni segmentlere yayılır.
- **Streak gerçeği:** Task9 mevcut `resetStreak`'i gain-only'ye çeker (sıfırdan kurmaz).
- **Tip tutarlılığı:** `run_gate`/`status_of` (Task2) tüm gate testlerinde; `gate_flow`/`gate_carbon_grid` imzaları (html,R) mevcut desenle aynı; segment render fn'leri `render(stage,s)` imzası + dispatch tablosu tutarlı.
- **No-placeholder:** validator gate'leri, hook script'leri, test harness'ı tam kod; reference dosyaları normatif içerik (checklist maddeleri, şablonlar, lisans tablosu) taşır; motor JS görevleri kesin dispatch entegrasyon-noktası + mirror-edilecek mevcut fn + temsili kod + fixture/node-check testi verir.
