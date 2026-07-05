# Lex-Sanitas Test Harness (plugin v3.0.0)

Bu dizin, lex-sanitas protokolünün **davranış sözleşmelerini** YAML-deklaratif senaryolar olarak içerir. Lex-sanitas bir Python paketi değil, bir Claude Code plugin protokolü olduğundan bu testler bir `pytest` koşucusuyla otomatik *assert* edilmez; bunun yerine üç yolla yürütülür:

> **v3.0.0 notu:** `routing_tests.yaml`, `scope_boundary_tests.yaml`, `citation_hallucination_tests.yaml`, `mod9_medical_research_tests.yaml` orijinal skill (v2.x) davranış sözleşmeleridir; mod sınıflandırma, kapsam sınırı, no-fabrication ve Mod 9 disiplini plugin'de aynen geçerlidir (yalnız `medical-research` çağrı yüzeyi artık **evidentia** plugin'i). Yeni **`full_fleet_coverage_tests.yaml`**, v3.0.0'ın tam-filo aktivasyonu + G0 kapsam manifestosu invaryantını kapsar.

1. **Manuel inceleme** — bir test mühendisi `given` istemini lex-sanitas'a verir, çıktıyı `expect` ve `assertions` ile karşılaştırır.
2. **`smp-orchestrator` / `skill-censor`** — `TRIGGER_AUDIT`, `COMPOSABILITY_AUDIT`, `SCOPE_BOUNDARY` modları bu süitleri girdi olarak okuyabilir.
3. **Şema doğrulaması** — `mod9_medical_research_tests.yaml` ve `citation_hallucination_tests.yaml` içindeki `sidecar_fixture` blokları `schemas/medical_sidecar.schema.json`'a karşı bir JSON Schema doğrulayıcı (Python `jsonschema`, Node `ajv` vb.) ile makine-doğrulanabilir.

## Süit biçimi

```yaml
suite:
  id: <kısa_kimlik>
  title: <başlık>
  version: "1.0"
  target_skill: lex-sanitas
  target_version: ">= 2.6.0"
  evaluator: [manual, smp-orchestrator, skill-censor, json_schema]
  description: <amaç>

cases:
  - id: <PREFIX-NNN>
    title: <vaka başlığı>
    given: <kullanıcı istemi VEYA sidecar_fixture referansı>
    expect:
      <beklenen davranış alanları — mod, tetikleme, kapsam, kapı sonucu>
    assertions:
      - <doğal dilde doğrulanabilir önerme>
    rationale: <neden bu beklenti — hangi SKILL.md/R14 bölümü>
```

## Sözleşme alanları

| Alan | Anlam |
|------|-------|
| `expect.mode` | Beklenen lex-sanitas modu (9 moddan biri) veya `out_of_scope` |
| `expect.medical_research` | `mandatory` / `conditional` / `none` (R14 §1.2) |
| `expect.routed_to` | `lex-sanitas` veya `out_of_scope` |
| `expect.redirect` | Kapsam-dışıysa hedef skill(ler): `saglik-sigorta` / `onko-erisim` / `promo-censor` |
| `expect.must_not_produce` | Üretilmemesi gereken çıktı türleri (Scope Guard) |
| `expect.gates` | İlgili kapıların beklenen sonucu: `PASS` / `FAIL` / `CONDITIONAL` |
| `expect.required_sections` | Modun zorunlu kıldığı medical-research bölümleri |
| `expect.schema_error` | Beklenen şema hatası (örn. `SchemaIncompatibilityError`) |

## Kapsam

| Süit | Kapsanan |
|------|----------|
| `routing_tests.yaml` | 9 mod sınıflandırma + medical-research tetikleme seviyesi |
| `scope_boundary_tests.yaml` | 5 kapsam-dışı kalemin negatif testi + reform pozitif karşılıkları |
| `mod9_medical_research_tests.yaml` | Mod 9 otomatik tetikleme + `ex_post_metrics` + G9 + şema-2.3.1 zorunluluğu |
| `citation_hallucination_tests.yaml` | G7 epistemik dürüstlük — uydurma CELEX/AYM/Yargıtay + `mcp_verified` etiketleme |

## Şema-doğrulama örneği (referans)

```bash
# sidecar_fixture'ları medical_sidecar şemasına karşı doğrula
python3 - <<'PY'
import json, yaml, sys
from jsonschema import Draft202012Validator
schema = json.load(open("schemas/medical_sidecar.schema.json"))
v = Draft202012Validator(schema)
suite = yaml.safe_load(open("tests/mod9_medical_research_tests.yaml"))
for c in suite["cases"]:
    fx = c.get("sidecar_fixture")
    if not fx: continue
    errs = sorted(v.iter_errors(fx), key=lambda e: e.path)
    exp = c["expect"].get("schema_valid", True)
    ok = (len(errs) == 0)
    print(f"{c['id']}: schema_valid={ok} (expected {exp}) "
          + ("" if ok == exp else "  <-- MISMATCH"))
PY
```

> **Not — v2.6.0:** Bu harness, lex-sanitas v2.5.7'ye kadar ertelenen üretim-standardı test/şema altyapısının ilk sürümüdür. Senaryolar kanıt-temelli ve kapsam-bilinçlidir; ileride `pytest`-tabanlı bir koşucu eklenebilir (v2.7+ olası).
