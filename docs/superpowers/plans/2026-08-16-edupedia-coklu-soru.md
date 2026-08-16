# edupedia çoklu sınav sorusu — uygulama planı

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan.

**Goal:** `/edupedia:soru` bir veya birden fazla soruyu tek HTML'de konu kümeleyerek öğretsin ve her soruyu kendi `worked`/`fadeFrom` ile çözsün. G-EXAM `exams[]` + `topics[]` biçimini ölçsün; eski `exam:{}` yeşil kalsın.

**Architecture:** Motor/`module-template.html` değişmez. Provenans blokları + G-EXAM regex. Çokluda zincir konu başına (`topics[].chain`); her `exams[]` öğesi kendi `workedId` üzerinde fadeFrom şart. Boş `exams: []` yok hükmünde → legacy `exam:{}`. n>4 WARN, FAIL değil. G-INTERACT `exams[].stem` saymaz.

**Tech Stack:** Python 3 `validate_module.py` (salt regex), pytest `test_gates.py`, Markdown komut/skill, plugin 0.8.0→0.9.0, carbon-edupedia 3.9.0→3.10.0. Vendor lockstep: CureoHub `services/edupedia_site/app/gates/validate_module.py`.

**Spec:** `docs/superpowers/specs/2026-08-16-edupedia-coklu-soru-design.md`

---

## File map

| Path | Change |
|---|---|
| `plugins/edupedia/skills/carbon-edupedia/tests/test_gates.py` | Spec §9 vakaları + G-INTERACT `exams[]` |
| `plugins/edupedia/skills/carbon-edupedia/scripts/validate_module.py` | `exams[]` dolaşımı, öğe başı `workedId`, `topics`+`topicId`, n>4 WARN, `gate_interact` strip |
| `plugins/edupedia/skills/carbon-edupedia/references/exam-solving.md` | Şema + çoklu kurgu; §7.2 tek-soru sınırı kalkar |
| `plugins/edupedia/commands/soru.md` | Çoklu girdi; “hangisini istiyorsun?” kalkar |
| `plugins/edupedia/skills/carbon-edupedia/SKILL.md` + `skill-manifest.yaml` | EXAM + G-EXAM; 3.10.0 |
| `plugins/edupedia/skills/start/SKILL.md`, README, plugin.json, marketplace, fleet | Komut metni; plugin 0.9.0 |
| CureoHub vendor kopya + `check_gates_drift.py` | Byte-aynı |

Commit/PR yok (kullanıcı istemedi). Worktree yok — mevcut dirty `main`, açık “uygula”.

---

### Task 1: Kırmızı testler

`test_gates.py` G-EXAM bölümünün sonuna:

- `EXAM_MULTI` — iki konu, üç `exams[]`, her birinde fadeFrom worked → PASS
- Bir `workedId` fadeFrom’suz → FAIL, mesajda o öğe id’si
- Kırık `topicId` → FAIL
- Beş sağlam `exams[]` → WARN `> 4`, FAIL değil
- `exams: []` + `exam:{}` → legacy PASS
- `exams: []` + exam yok + mode EXAM → FAIL
- G-INTERACT `EXAM_MULTI` → PASS (exams stem sayılmaz)
- Mevcut `EXAM_OK` dokunulmaz

**Verify:** `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -k gexam -q` — yeni testler FAIL, eskiler PASS.

---

### Task 2: Kapı

- `_iter_balanced_objects`, `_exam_worked_ok_id`
- `exams` yalnız `length ≥ 1` ise çoklu yol
- Çokluda `_exam_worked_ok(html)` YASAK
- `gate_interact`: `exams[]` içini de scope’tan düş
- Mode EXAM + ne exam ne dolu exams → FAIL

**Verify:** aynı pytest yeşil; `python3 -m pytest tests/ -q`

---

### Task 3: Doküman + sürüm

exam-solving §2–§7, soru.md, SKILL, manifest, CHANGELOG 3.10.0, plugin 0.9.0.

---

### Task 4: Vendor

```
cp <kaynak> services/edupedia_site/app/gates/validate_module.py
python3 services/edupedia_site/tools/check_gates_drift.py
```
