# edupedia Sınav Sorusu Asistanı (EXAM modu) — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** edupedia plugin'ine, fotoğrafı çekilen veya yapıştırılan bir sınav sorusunu pedagojik ilkelerle çözen ve sorunun gerektirdiği kavram zincirini öğreten bir `EXAM` modu eklemek.

**Architecture:** Yeni bir çıktı türü yok — mevcut tek-dosya etkileşimli HTML modül üretilir. Soru transkribe edilip yeniden inşa edilir (fotoğraf gömülmez), böylece `assets/module-template.html` motoru **hiç değişmez**. Yeni yüzeyler: bir koşullu kalite kapısı (`G-EXAM`), bir referans dokümanı, bir komut ve `MODULE_DATA`'ya opsiyonel bir `exam` bloğu.

**Tech Stack:** Python 3.10+ (yalnız standart kütüphane) · pytest · Markdown · YAML · JSON

**Spec:** `docs/superpowers/specs/2026-07-31-edupedia-sinav-asistani-design.md`

**Çalışma dizini:** Tüm yollar `plugins/edupedia/` köküne görelidir (repo: `CureoPrivate`).
Testler `plugins/edupedia/skills/carbon-edupedia/` içinden çalıştırılır.

**Dal:** `feat/edupedia-sinav-asistani` (zaten açık; spec commit'i `ad33bf1` üzerinde)

## Global Constraints

- **Motor dokunulmaz.** `skills/carbon-edupedia/assets/module-template.html` bu planda **hiçbir adımda değiştirilmez**. Bir adım motor değişikliği gerektiriyorsa plan yanlıştır — dur ve bildir.
- **`agents/module-auditor.md` değişmez.** Mevcut dört denetim ekseni EXAM modülünde de geçerlidir.
- **Validator salt-metindir.** `scripts/validate_module.py` çevrimdışı çalışır, MCP erişimi yoktur ve `MODULE_DATA` JS nesnesini **parse etmez** — regex/heuristik denetim yapar. `G-EXAM` bu sınıra tabidir.
- **Python bağımlılığı yok.** `validate_module.py` yalnız standart kütüphane kullanır (`skill-manifest.yaml` → `runtime.required_packages: []`). Yeni paket eklenmez.
- **Emoji yok.** Üretilen hiçbir dosya (kod, doküman, test fixture) emoji içermez — `G-EMOJI` kapısının kendisi de bu kurala tabidir.
- **Dil: Türkçe.** Tüm doküman, docstring, kapı mesajı ve commit gövdesi Türkçedir.
- **Tek kaynak ilkesi.** Normatif kural **yalnız** `references/exam-solving.md`'de tanımlanır; `commands/soru.md` ve `SKILL.md` ona referans verir, kuralı **tekrarlamaz**. (Gerekçe: `commands/modul.md` içindeki uyarı — kural çoğaltması iki kopyanın sapmasına yol açtı ve claude.ai yalnız referansı gördüğü için orada yanlış kural geçerliydi.)
- **Kapı otoritesi yayın sunucusudur.** `validate_module.py` yerel ön-kontroldür. Bu plan sunucu tarafını (`CureoHub/services/edupedia_site/app/gates/`) **değiştirmez** — `G-EXAM` yayın sunucusuna ayrı bir iş olarak taşınır (bkz. Task 6 notu).

---

## Dosya Yapısı

| Dosya | Sorumluluk | Durum |
|---|---|---|
| `skills/carbon-edupedia/scripts/validate_module.py` | `G-EXAM` kapısı: `exam` bloğunun yapısal bütünlüğü | Değiştirilir (Task 1) |
| `skills/carbon-edupedia/tests/test_gates.py` | `G-EXAM` davranış testleri | Değiştirilir (Task 1) |
| `skills/carbon-edupedia/references/exam-solving.md` | **Normatif davranış**: soru anatomisi, geriye çözümleme, çeldirici pedagojisi, degrade protokolleri | **Oluşturulur** (Task 2) |
| `skills/carbon-edupedia/SKILL.md` | EXAM modunu, referansı ve `G-EXAM`'ı skill sözleşmesine bağlar | Değiştirilir (Task 3) |
| `skills/carbon-edupedia/skill-manifest.yaml` | SMP makine-okunur graf: mod, referans, kapı, tetikleyici | Değiştirilir (Task 3) |
| `commands/soru.md` | `/edupedia:soru` giriş noktası — referansa delege eder | **Oluşturulur** (Task 4) |
| `plugin.json` | Komut sayısı ve açıklama | Değiştirilir (Task 4) |
| `skills/start/SKILL.md` | Komut tablosu + niyet yönlendirme | Değiştirilir (Task 4) |
| `skills/carbon-edupedia/assets/module-template.html` | — | **DEĞİŞMEZ** |
| `agents/module-auditor.md` | — | **DEĞİŞMEZ** |

**Task sırası spec §11'den neden sapıyor:** Spec önce referansı, sonra kapıyı önerir.
Plan kapıyı (Task 1) referanstan (Task 2) önce koyar, çünkü kapı **bağımsız test
edilebilir bir teslimattır** ve TDD döngüsü onunla başlar; referans dokümanı tek başına
test edilemez. Normatif içerik ikisinde de aynıdır — sıra farkı davranışı değiştirmez.

**Neden `G-EXAM` testleri fixture dosyası kullanmıyor:** `G-FLOW`/`G-CARBON-GRID` testleri render edilmiş HTML işaretleri aradığı için tam şablon fixture'ı (1819 satır) gerektirir. `G-EXAM` yalnız `MODULE_DATA` metnini okur — `test_harness_imports_existing_gate` testindeki gibi satır içi string yeterlidir. Yeni fixture dosyası eklenmez.

---

### Task 1: `G-EXAM` kalite kapısı

**Files:**
- Modify: `skills/carbon-edupedia/scripts/validate_module.py` (modül docstring'i ~satır 20-40; yeni fonksiyonlar `gate_verify` sonrasına; `main()` ~satır 705-718)
- Test: `skills/carbon-edupedia/tests/test_gates.py` (dosya sonuna eklenir)

**Interfaces:**
- Consumes: `vm.Result` (mevcut — `add(gate, status, msg, applicable=True)`), `run_gate(gate_fn, html)` ve `status_of(rows, gate_id)` test yardımcıları (mevcut, `test_gates.py` başında tanımlı)
- Produces:
  - `_slice_bracketed(text, start_idx, open_ch="[", close_ch="]") -> str`
  - `_exam_collect(block, html) -> dict` (anahtarlar: `stem_ok`, `integrity`, `has_note`, `tcheck`, `all_ids`, `n_chain`, `n_mapped`, `missing_ids`, `has_source`, `has_options`, `has_distractor`, `worked_ok`)
  - `_exam_worked_ok(html) -> bool`
  - `_exam_eval(sig) -> tuple[list[str], list[str]]` (issues, warns)
  - `gate_exam(html, R) -> None`
  - `EXAM_INTEGRITY_VALUES: set[str]`

---

- [ ] **Step 1: Test sabitlerini ve ilk üç testi yaz**

`tests/test_gates.py` dosyasının **sonuna** ekle:

```python
# ---------------------------------------------------------------------------
# G-EXAM (v3.7.0) — sınav sorusu asistanı (EXAM modu) yapısal denetimi
# Fixture dosyası YOK: G-EXAM yalnız MODULE_DATA metnini okur, render edilmiş
# HTML işareti aramaz — satır içi string yeterli (bkz. plan "Dosya Yapısı").
# ---------------------------------------------------------------------------

EXAM_OK = '''<html lang="tr"><body><script>
const MODULE_DATA = {
  meta: { mode: "EXAM", title: "Kesir Problemi", sourceCitation: "MEB Matematik 6" },
  exam: {
    stem: "3/4 kg elma 24 TL ise 2/3 kg elma kac TL'dir?",
    options: ["12 TL", "14 TL", "16 TL", "18 TL"],
    source: "ogrenci fotografi - okul yazilisi",
    integrity: "sound",
    integrityNote: "",
    transcriptionCheck: "tc1",
    distractorAnalysis: "d1",
    chain: [
      { concept: "birim fiyat", outcomeCode: "MAT.6.1.4.1", mappedTo: ["t1"] },
      { concept: "kesirle bolme", outcomeCode: "MAT.6.1.4.2", mappedTo: ["w1"] }
    ]
  },
  segments: [
    { type: "teach", id: "s1", title: "Soruyu okuyalim" },
    { type: "selfExplain", id: "tc1", prompt: "Bir yeri farkliysa yaz." },
    { type: "teach", id: "t1", title: "Birim fiyat" },
    { type: "worked", id: "w1", title: "Cozum",
      steps: [ { text: "24 : 3/4 = 32" }, { text: "32 x 2/3 = ?", answer: ["21,33"] } ],
      fadeFrom: 1 },
    { type: "mcq", id: "d1",
      questions: [ { stem: "B sikki neden cazip ama yanlis?", correctIndex: 1 } ] }
  ]
};
</script></body></html>'''


def test_gexam_skips_when_not_exam_module():
    rows = run_gate(vm.gate_exam, "<html><body><p>merhaba</p></body></html>")
    assert status_of(rows, "G-EXAM") == "PASS"
    msg = next(m for g, s, m in rows if g == "G-EXAM")
    assert "uygulanmaz" in msg


def test_gexam_fail_when_mode_exam_without_block():
    html = '<html><body><script>const MODULE_DATA = { meta: { mode: "EXAM" } };</script></body></html>'
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"


def test_gexam_pass_on_wellformed():
    rows = run_gate(vm.gate_exam, EXAM_OK)
    assert status_of(rows, "G-EXAM") == "PASS"
```

- [ ] **Step 2: Testleri çalıştır, başarısız olduklarını doğrula**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -k gexam -v`

Expected: 3 test de FAIL — `AttributeError: module 'validate_module' has no attribute 'gate_exam'`

- [ ] **Step 3: `_slice_bracketed` yardımcısını ekle**

`scripts/validate_module.py` içinde, `gate_verify` fonksiyonunun **sonrasına** (yani `FLOW_LOSS_RE` tanımından **önce**) ekle:

```python
def _slice_bracketed(text, start_idx, open_ch="[", close_ch="]"):
    """text[start_idx] konumundaki açılış karakterinden EŞLEŞEN kapanışa kadar
    olan iç dilimi döndürür (açılış/kapanış hariç). Eşleşme yoksa "" döner.

    Neden: mevcut kapılar `\\{(.*?)\\n\\s*\\}` gibi girinti-bağımlı desenler kullanır;
    bunlar iç içe dizi/nesne içeren bloklarda (exam.chain[] içinde mappedTo[]) erken
    kapanır. Bu yardımcı sayarak eşleştirir.

    SINIR: string literali içindeki parantezleri saymaz (ör. concept: "a[b]" bloğu
    erken kapatır). Bu, kapının genel salt-metin/heuristik sınırıyla aynı düzeydedir
    (bkz. gate_curriculum notu) ve bilinçlidir.
    """
    depth = 0
    for i in range(start_idx, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return text[start_idx + 1:i]
    return ""
```

- [ ] **Step 4: `_exam_worked_ok` yardımcısını ekle**

`_slice_bracketed`'in hemen ardına ekle:

```python
def _exam_worked_ok(html):
    """En az bir `worked` segmentinde fadeFrom, adım sayısından KÜÇÜK mü?

    Bu, G-EXAM'ın çekirdek denetimidir: fadeFrom < adım sayısı ise son adım(lar)
    öğrenciye boş bırakılmış demektir — yani cevap doğrudan verilmemiştir.
    fadeFrom == adım sayısı ise tüm çözüm görünür (kopya), fadeFrom yoksa motor
    zaten segmenti kuramaz.

    HEURİSTİK: `type:"worked"` işaretinden geriye en yakın `{` bulunur ve o segment
    dilimlenir; dilim içindeki `steps` dizisinde `text:` sayılır. İç içe olağandışı
    biçimlendirme yanıltabilir — kapı beyanın BİÇİMİNİ ölçer, içeriğini değil.
    """
    for m in re.finditer(r'\btype\s*:\s*["\']worked["\']', html):
        brace = html.rfind("{", 0, m.start())
        if brace < 0:
            continue
        seg = _slice_bracketed(html, brace, "{", "}")
        fade_m = re.search(r'\bfadeFrom\s*:\s*(\d+)', seg)
        if not fade_m:
            continue
        steps_i = seg.find("steps")
        if steps_i < 0:
            continue
        arr_i = seg.find("[", steps_i)
        if arr_i < 0:
            continue
        n_steps = len(re.findall(r'\btext\s*:', _slice_bracketed(seg, arr_i)))
        if n_steps and int(fade_m.group(1)) < n_steps:
            return True
    return False
```

- [ ] **Step 5: `_exam_collect` ve `_exam_eval`'i ekle**

`_exam_worked_ok`'in hemen ardına ekle:

```python
EXAM_INTEGRITY_VALUES = {"sound", "flawed", "out_of_frame"}


def _exam_collect(block, html):
    """exam bloğundan G-EXAM sinyallerini toplar (saf veri çıkarımı)."""
    stem_m = re.search(r'\bstem\s*:\s*["\'](.*?)["\']\s*,', block, re.S)
    integ_m = re.search(r'\bintegrity\s*:\s*["\']([^"\']*)["\']', block)
    note_m = re.search(r'\bintegrityNote\s*:\s*["\'](.*?)["\']', block, re.S)
    tcheck_m = re.search(r'\btranscriptionCheck\s*:\s*["\']([^"\']*)["\']', block)
    source_m = re.search(r'\bsource\s*:\s*["\'](.*?)["\']', block, re.S)
    distr_m = re.search(r'\bdistractorAnalysis\s*:\s*["\']([^"\']*)["\']', block)

    chain_i = block.find("chain")
    chain_slice = ""
    if chain_i >= 0:
        arr_i = block.find("[", chain_i)
        if arr_i >= 0:
            chain_slice = _slice_bracketed(block, arr_i)

    mapped_ids = set()
    for arr in re.findall(r'mappedTo\s*:\s*\[([^\]]*)\]', chain_slice):
        mapped_ids |= set(re.findall(r'["\']([^"\']+)["\']', arr))
    all_ids = set(re.findall(r'\bid\s*:\s*["\']([^"\']+)["\']', html))

    return {
        "stem_ok": bool(stem_m and stem_m.group(1).strip()),
        "integrity": integ_m.group(1) if integ_m else "",
        "has_note": bool(note_m and note_m.group(1).strip()),
        "tcheck": tcheck_m.group(1) if tcheck_m else "",
        "all_ids": all_ids,
        "n_chain": len(re.findall(r'\bconcept\s*:', chain_slice)),
        "n_mapped": len(re.findall(r'\bmappedTo\s*:', chain_slice)),
        "missing_ids": [i for i in sorted(mapped_ids) if i not in all_ids],
        "has_source": bool(source_m and source_m.group(1).strip()),
        "has_options": bool(re.search(r'\boptions\s*:\s*\[', block)),
        "has_distractor": bool(distr_m and distr_m.group(1).strip()),
        "worked_ok": _exam_worked_ok(html),
    }


def _exam_eval(sig):
    """Toplanan sinyallerden (issues, warns) üretir. Saf karar mantığı."""
    issues = []; warns = []
    if not sig["stem_ok"]:
        issues.append("exam.stem boş veya yok; transkribe edilmiş soru metni zorunlu")
    if sig["integrity"] not in EXAM_INTEGRITY_VALUES:
        issues.append('exam.integrity "sound" | "flawed" | "out_of_frame" olmalı '
                      f'(bulunan: "{sig["integrity"]}")')
    elif sig["integrity"] != "sound" and not sig["has_note"]:
        issues.append(f'exam.integrity "{sig["integrity"]}" ama integrityNote boş; '
                      "sorunun nesinin bozuk/çerçeve dışı olduğu yazılmalı")
    if not sig["tcheck"]:
        issues.append("exam.transcriptionCheck yok; transkripsiyon doğrulama segmenti "
                      "atlanamaz (soru yanlış okunmuşsa her şey yanlış)")
    elif sig["tcheck"] not in sig["all_ids"]:
        issues.append(f'exam.transcriptionCheck "{sig["tcheck"]}" segments[] içinde yok')
    if not sig["worked_ok"]:
        issues.append("fadeFrom < adım sayısı olan bir `worked` segmenti yok; cevap "
                      "doğrudan verilemez — son adım(lar) öğrenciye bırakılmalı")
    if not sig["n_chain"]:
        issues.append("exam.chain[] boş veya `concept` içermiyor; geriye çözümleme "
                      "zinciri zorunlu")
    elif sig["n_mapped"] < sig["n_chain"]:
        issues.append(f'{sig["n_chain"]} zincir halkasından {sig["n_mapped"]} tanesinde '
                      "mappedTo var; her halka bir segmente bağlanmalı")
    if sig["missing_ids"]:
        issues.append("exam.chain mappedTo id'si segments[] içinde yok: "
                      + ", ".join(sig["missing_ids"][:5]))
    if not sig["has_source"]:
        warns.append("exam.source beyanı yok (sorunun kaynağı belirsiz)")
    if sig["has_options"] and not sig["has_distractor"]:
        warns.append("exam.options var ama exam.distractorAnalysis yok; çeldirici "
                     "analizi segmenti önerilir (yeni nesil çeldirici doğru ama ilgisizdir)")
    return issues, warns
```

- [ ] **Step 6: `gate_exam` fonksiyonunu ekle**

`_exam_eval`'in hemen ardına ekle:

```python
def gate_exam(html, R):
    """G-EXAM (koşullu): sınav-sorusu modülünün yapısal bütünlüğü.

    Yalnız mod EXAM ise veya bir `exam` bloğu varsa tetiklenir; aksi halde atlanır
    (geriye dönük uyum — mevcut modüller etkilenmez).

    ÇEKİRDEK DEĞER: `worked` segmentinde fadeFrom < adım sayısı ZORUNLUDUR. Böylece
    cevap hiçbir zaman doğrudan verilmez, öğrenci son adımı kendisi tamamlar —
    ödev-çözme makinesi olmak iyi niyete değil YAPIYA bağlanır.

    DENETLEYEMEZ (fazla güvenmeyin): transkripsiyonun fotoğrafa sadık olduğunu,
    çözümün DOĞRU olduğunu, zincirin eksiksiz olduğunu, outcomeCode'un gerçek bir
    kazanım olduğunu — hiçbiri çevrimdışı ölçülemez (MCP erişimi yok, G-CURRICULUM
    ve G-VERIFY ile aynı salt-metin sınırı). Kapı beyanın BİÇİMİNİ ölçer.
    Tam kural: references/exam-solving.md.
    """
    is_exam_mode = bool(re.search(r'\bmode\s*:\s*["\']EXAM["\']', html))
    exam_m = re.search(r'\bexam\s*:\s*\{', html)
    if not is_exam_mode and not exam_m:
        R.add("G-EXAM", "PASS", "Sınav-sorusu modülü değil (uygulanmaz).", applicable=False)
        return
    if not exam_m:
        R.add("G-EXAM", "FAIL",
              "mode EXAM ama `exam` bloğu yok; soru provenansı ve çözüm disiplini zorunlu "
              "(references/exam-solving.md).")
        return
    block = _slice_bracketed(html, exam_m.end() - 1, "{", "}")
    issues, warns = _exam_eval(_exam_collect(block, html))
    if issues:
        R.add("G-EXAM", "FAIL", "; ".join(issues))
    elif warns:
        R.add("G-EXAM", "WARN", "; ".join(warns))
    else:
        R.add("G-EXAM", "PASS",
              "Soru transkribe + doğrulama segmentine bağlı; zincir segmentlere "
              "izlenebilir; cevap fadeFrom ile öğrenciye bırakılmış. "
              "(Kapı yapıyı ölçer, çözümün doğruluğunu değil.)")
```

- [ ] **Step 7: `main()`'e kapıyı bağla**

`main()` içinde `gate_carbon_grid(html,R)` satırının **hemen ardına** ekle:

```python
    gate_exam(html,R)
```

- [ ] **Step 8: İlk üç testi çalıştır**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -k gexam -v`

Expected: 3 test de PASS

- [ ] **Step 9: FAIL dallarının testlerini yaz**

`tests/test_gates.py` sonuna ekle:

```python
def test_gexam_fail_on_empty_stem():
    html = EXAM_OK.replace(
        'stem: "3/4 kg elma 24 TL ise 2/3 kg elma kac TL\'dir?"', 'stem: ""')
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"
    assert "exam.stem" in next(m for g, s, m in rows if g == "G-EXAM")


def test_gexam_fail_when_worked_reveals_full_answer():
    # fadeFrom 1 -> 2: iki adimin ikisi de gorunur, ogrenciye bos birakilan adim yok
    html = EXAM_OK.replace("fadeFrom: 1", "fadeFrom: 2")
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"
    assert "fadeFrom" in next(m for g, s, m in rows if g == "G-EXAM")


def test_gexam_fail_on_missing_transcription_check():
    html = EXAM_OK.replace('transcriptionCheck: "tc1",', "")
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"
    assert "transcriptionCheck" in next(m for g, s, m in rows if g == "G-EXAM")


def test_gexam_fail_on_dangling_transcription_check_id():
    html = EXAM_OK.replace('transcriptionCheck: "tc1"', 'transcriptionCheck: "yok99"')
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"


def test_gexam_fail_on_dangling_chain_mapped_id():
    html = EXAM_OK.replace('mappedTo: ["w1"]', 'mappedTo: ["olmayan-segment"]')
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"
    assert "olmayan-segment" in next(m for g, s, m in rows if g == "G-EXAM")


def test_gexam_fail_on_empty_chain():
    html = EXAM_OK.replace('chain: [', 'chain: [] , unusedChain: [')
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"
    assert "chain" in next(m for g, s, m in rows if g == "G-EXAM")


def test_gexam_fail_on_invalid_integrity_value():
    html = EXAM_OK.replace('integrity: "sound"', 'integrity: "belki"')
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"


def test_gexam_fail_on_flawed_without_note():
    html = EXAM_OK.replace('integrity: "sound"', 'integrity: "flawed"')
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "FAIL"
    assert "integrityNote" in next(m for g, s, m in rows if g == "G-EXAM")


def test_gexam_pass_on_flawed_with_note():
    html = (EXAM_OK
            .replace('integrity: "sound"', 'integrity: "flawed"')
            .replace('integrityNote: ""',
                     'integrityNote: "B ve C siklarinin ikisi de dogru; tek cevap yok."'))
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "PASS"


def test_gexam_warn_on_missing_source():
    html = EXAM_OK.replace('source: "ogrenci fotografi - okul yazilisi",', "")
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "WARN"


def test_gexam_warn_on_options_without_distractor_analysis():
    html = EXAM_OK.replace('distractorAnalysis: "d1",', "")
    rows = run_gate(vm.gate_exam, html)
    assert status_of(rows, "G-EXAM") == "WARN"
    assert "distractorAnalysis" in next(m for g, s, m in rows if g == "G-EXAM")
```

- [ ] **Step 10: Tüm G-EXAM testlerini çalıştır**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -k gexam -v`

Expected: 14 test de PASS. Bir test düşerse `_exam_eval`'deki ilgili dalı düzelt — testi gevşetme.

- [ ] **Step 11: Regresyon — tüm test paketini çalıştır**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -v`

Expected: Tüm testler PASS (mevcut testler dahil). `G-EXAM` koşullu olduğu için mevcut fixture'larda `SKIPPED`/`PASS` dalına düşer ve hiçbir eski testi bozmaz.

- [ ] **Step 12: Mevcut fixture'da uçtan uca duman testi**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 scripts/validate_module.py tests/fixtures/minimal_pass.html --json | python3 -c "import sys,json; d=json.load(sys.stdin); print('G-EXAM:', d['G-EXAM'])"`

Expected: `G-EXAM: {'status': 'SKIPPED', 'detail': 'Sınav-sorusu modülü değil (uygulanmaz).'}`

Bu, `applicable=False` sözleşmesini doğrular: koşturulmayan kapı `--json` çıktısında **asla `PASS`** yazmaz.

- [ ] **Step 13: Modül docstring'ine kapı satırını ekle**

`scripts/validate_module.py` başındaki kapı listesinde, `G-CARBON-GRID` satırının **ardına** ekle (mevcut hizalamayı koru):

```
    G-EXAM          (FAIL) — koşullu: mode EXAM/exam bloğu varsa sınav-sorusu yapısı —
                    soru transkribe + doğrulama segmentine bağlı, zincir segmentlere
                    izlenebilir, cevap fadeFrom ile öğrenciye bırakılmış. Yargı modelin;
                    kapı transkripsiyonun sadakatini/çözümün doğruluğunu ÖLÇEMEZ
```

- [ ] **Step 14: Commit**

```bash
git add plugins/edupedia/skills/carbon-edupedia/scripts/validate_module.py \
        plugins/edupedia/skills/carbon-edupedia/tests/test_gates.py
git commit -m "feat(edupedia): G-EXAM koşullu kalite kapısı + 14 test

Sınav-sorusu modüllerinin yapısal bütünlüğünü denetler: exam.stem dolu,
transcriptionCheck var olan bir segmente bağlı, chain[] halkaları segmentlere
izlenebilir, integrity geçerli (sound değilse integrityNote zorunlu).

Çekirdek denetim worked.fadeFrom < adım sayısı: cevap doğrudan verilemez,
son adım öğrenciye bırakılır. Ödev-çözme makinesi olmak iyi niyete değil
yapıya bağlanır.

Yeni yardımcı _slice_bracketed: mevcut girinti-bağımlı blok desenleri iç içe
dizilerde (chain[] içinde mappedTo[]) erken kapanıyordu; sayarak eşleştirir.

Kapı koşulludur — exam bloğu yoksa SKIPPED, mevcut modüller etkilenmez."
```

---

### Task 2: `references/exam-solving.md` — normatif davranış

**Files:**
- Create: `skills/carbon-edupedia/references/exam-solving.md`

**Interfaces:**
- Consumes: `references/curriculum-integration.md` §3 Adım 0 (sınıf+ders kapısı), §6.1 (`verification` bloğu), `references/newgen-question-design.md` §3 (çeldirici mantığı), `references/module-architecture.md` §2 (`worked`/`selfExplain` şemaları)
- Produces: Bu dosya, EXAM modunun **tek normatif kaynağıdır**. `commands/soru.md` ve `SKILL.md` buraya referans verir.

- [ ] **Step 1: Dosyayı oluştur**

Aşağıdaki **tam** içerikle `skills/carbon-edupedia/references/exam-solving.md` dosyasını yaz:

````markdown
# Sınav Sorusu Çözme (EXAM modu) — Anatomi, Zincir ve Degrade Protokolleri

> **Ne zaman okunur:** `/edupedia:soru` çağrıldığında veya `mode:"EXAM"` bir modül
> üretilirken — **ZORUNLU, akışın tamamı**.
>
> **Ön koşul:** `references/adhd-pedagogy.md` (her modülden önce zorunlu) +
> `references/module-architecture.md` (`worked` ve `selfExplain` şemaları).
>
> **Tasarım kaynağı:** `docs/superpowers/specs/2026-07-31-edupedia-sinav-asistani-design.md`

EXAM modu, öğrencinin önüne gelmiş **bir** sınav sorusunu (fotoğraf veya yapıştırılmış
metin) girdi alır ve onu edupedia'nın pedagojik ilkeleriyle çözen + gerektirdiği kavram
zincirini öğreten tek-dosya etkileşimli bir modüle çevirir.

Bu mod, `CURRICULUM` modunun **tersine çalışır**: orada çerçeveyi ders kitabı çizer ve
model neyi üreteceğini seçer; burada **soru verilidir** ve çerçeveye sonradan bağlanır.

---

## 1. Dört karar (değiştirilemez)

| # | Karar | Gerekçe |
|---|---|---|
| K1 | Çıktı = etkileşimli tek-dosya HTML modül | Motor, 14 kapı ve `worked`/`selfExplain` yeniden kullanılır; yeni çıktı türü yok |
| K2 | Soru **içerikçe birebir** yer alır; modül **varsayılan yayınlanmaz** | Öğrenci kendi sorusunu tanımalı; telif riski yayın teklifi kaldırılarak kapatılır |
| K3 | Anlatım = **geriye doğru kavram zinciri** (kazanımın tamamı değil) | ~10-12 dk, DEHB kısa-oturum ilkesi; her segment soruya bağlı olduğu için "neden bunu öğreniyorum" hep açık |
| K4 | Soru **transkribe + yeniden inşa** edilir; **fotoğraf gömülmez** | Motorda raster taşıyıcı yok; yeniden inşa tema-duyarlı, ekran-okuyucu erişilebilir ve Tier-1 yazar-SVG doktriniyle tutarlı |

---

## 2. Akış

**Adım 0 — Girdi.** Fotoğrafı oku veya yapıştırılmış metni al.

**Adım 1 — TRANSKRİPSİYON.** Soruyu **birebir** metne çevir: aynı sayılar, aynı ifade,
aynı şıklar. Şekil/grafik varsa `references/svg-authoring.md` kurallarıyla **yazar-SVG
olarak yeniden çiz** (token renk, `role="img"` + `<title>`, 2px stroke, gradyansız).

> **Belirsizlik varsa SOR, tahmin etme.** Silik rakam, kesik kenar, okunmayan üs →
> neyin belirsiz olduğunu **tam olarak** söyle: "üçüncü şıkkın son rakamı okunmuyor —
> 6 mı 8 mi?" Yanlış okunan bir soru, sonraki her adımı sessizce yanlış yapar.

**Adım 2 — KAPI: ders + sınıf.** Kesinleşmeden üretim başlamaz. Fotoğrafta yazmıyorsa
`AskUserQuestion` ile **SOR**.

> Kural ve gerekçesi **tek yerde**: `curriculum-integration.md` §3 Adım 0. Burada
> tekrarlanmaz — çoğaltma iki kopyanın sapmasına yol açar.

**Adım 3 — TEŞHİS (geriye çözümleme).** Soruyu tersine çöz: *"bunu çözmek için önce
neyi bilmek gerekiyor?"* Tipik olarak 2-4 halka. Her halka bir kavram veya beceridir,
bir konu başlığı değil.

Örnek — *"3/4 kg elma 24 TL ise 2/3 kg kaç TL?"*:
1. birim fiyat kavramı
2. kesirle bölme
3. kesirle çarpma

**Adım 4 — KAZANIM.** Zincirin her halkasını `search_learning_outcomes` ile bir MEB
kazanımına **bağla — doğrula, uydurma**. Bağlanamayan halka için **D2** (§5).

**Adım 5 — ÇERÇEVE.** `list_textbooks` → `get_document_text` ile zincirin ders
kitabındaki yerini aç. **Çözümün ve anlatımın dayanağı burasıdır.** Kitap yoksa **D3**.

**Adım 6 — ÇÖZ.** Kendi çözümünü üret; her adımın dayanağı kitap sayfası olmalı.
Soru bozuksa **D1**, çerçeve üstüyse **D4**.

**Adım 7 — KURGU.** `exam` bloğu (§3) + segment dizisi (§4).

**Adım 8 — TESLİM.** `scripts/validate_module.py` (G-EXAM dahil) → `/mnt/user-data/outputs/`
+ yan yana `.manifest.json`.

> **Yayın TEKLİF EDİLMEZ (K2).** `/edupedia:modul` ve `/edupedia:mufredat`'ın aksine
> bu modda "yayınlamamı ister misin?" sorusu **sorulmaz**. Kullanıcı açıkça isterse
> telif uyarısı verilir ("bu soru size ait değilse yayınlamak telif ihlali olabilir")
> ve karar kullanıcınındır — engellenmez.

---

## 3. `exam` veri bloğu

`curriculum` bloğuyla aynı desende: motoru değiştirmez, izlenebilirlik taşır,
`G-EXAM` tarafından okunur.

```js
exam: {
  stem: "3/4 kg elma 24 TL ise 2/3 kg elma kaç TL'dir?",  // ZORUNLU — transkribe soru
  options: ["12 TL", "14 TL", "16 TL", "18 TL"],           // opsiyonel — şıklıysa
  figure: { kind: "svg", ref: "<svg …>" },                 // opsiyonel — yeniden çizilen şekil
  source: "öğrenci fotoğrafı — okul yazılısı",             // opsiyonel (yoksa WARN)
  integrity: "sound",                     // ZORUNLU: "sound" | "flawed" | "out_of_frame"
  integrityNote: "",                      // "sound" değilse ZORUNLU
  transcriptionCheck: "tc1",              // ZORUNLU — selfExplain segmentinin id'si
  distractorAnalysis: "d1",               // opsiyonel (options varsa yokluğu WARN)
  chain: [                                // ZORUNLU, boş olamaz
    { concept: "birim fiyat",
      outcomeCode: "MAT.6.1.4.1",         // opsiyonel (D2'de düşer)
      mappedTo: ["t1"] },                 // ZORUNLU — segments[]'te var olmalı
    { concept: "kesirle bölme",
      outcomeCode: "MAT.6.1.4.2",
      mappedTo: ["w1"] }
  ]
}
```

**Doğru cevap `exam` bloğunda tutulmaz.** İki yerde yaşar: `worked` segmentinin son
adımındaki `answer` ve çeldirici analizi `mcq`'sünün `correctIndex`'i. Tek kaynak.

> **Bilinen sızıntı (yeni değil):** `MODULE_DATA` HTML kaynağındadır; kaynağı açan
> öğrenci `answer`/`correctIndex` görebilir. Bu mevcut tüm `mcq` modülleri için de
> geçerlidir, EXAM modunun getirdiği bir gerileme değildir. Çözülmeyecek.

---

## 4. Segment kurgusu

```
 1  teach        "Soruyu birlikte okuyalım"
                  → exam.stem + exam.options + exam.figure (yazar-SVG)
 2  selfExplain  "Soruyu böyle okudum. Bir yeri farklıysa aşağıya yaz."
                  ← TRANSKRİPSİYON KAPISI — exam.transcriptionCheck bu id'yi gösterir
 3  hook         "Sence bunu çözmek için hangi bilgi gerekli?"   resolvesIn → 4
 4  teach + etkileşim   zincir halkası 1  (kitaptan; KB2.x becerisine eşlenmiş)
 5  teach + etkileşim   zincir halkası 2
 6  brainbreak   (≥6 segment ise — module-architecture.md §3 kuralı)
 7  worked       SORUNUN KENDİSİ, adım adım — fadeFrom ile son adım(lar) öğrenciye
 8  selfExplain  "Neden bu adımda böyle yaptık?"  (notsuz, cezasız)
 9  mcq          ÇELDİRİCİ ANALİZİ — exam.distractorAnalysis bu id'yi gösterir
10  mcq          TRANSFER — aynı zincirle 2 izomorfik soru
11  checkpoint
```

### 4.1 Neden 2. adım `mcq` değil `selfExplain`

`G-INTERACT` her `stem:` için bir `correctIndex:` şart koşar. "Soruyu doğru mu okudum?"
sorusunun doğru cevabı **yoktur** — `mcq` yapılırsa ya kapı düşer ya da *"Hayır, şurası
farklı"* diyen öğrenci **yanlış** sayılır (G-WELLBEING ihlali).

`selfExplain` notsuz ve cezasızdır; motor "Devam"ı koşulsuz etkin bırakır. Öğrenci
farkı yazabilir de yazmayabilir de. `modelExplanation` alanına düzeltme yönergesi konur:
*"Bir yeri farklıysa doğrusunu yazıp bana tekrar sor — düzeltilmiş soruyla yeni bir
modül üretirim."*

### 4.2 Neden 7. adımda `fadeFrom` zorunlu

Bu, EXAM modunun **varlık sebebidir**. `worked` segmenti `fadeFrom` ile kapatılır;
cevap hiçbir zaman doğrudan verilmez, öğrenci son adımı kendisi tamamlar.

`G-EXAM` bunu **zorunlu kılar** (`fadeFrom < steps.length`, yoksa FAIL). Ödev-çözme
makinesi olmamak bir üslup tercihi değil, **yapısal bir kısıttır** — modelin iyi
niyetine bırakılmaz.

### 4.3 Neden 9. adım (çeldirici analizi)

Yeni nesil sorularda çeldirici genellikle **doğru ama ilgisiz** bilgidir ve DEHB'li
öğrenci için en zorlayıcı noktadır. Geri bildirim "yanlış" demekle yetinmemeli,
**neden ilgisiz olduğunu** açıklamalıdır (`newgen-question-design.md` §3;
`adhd-pedagogy.md` Ö4).

---

## 5. Degrade protokolleri

| # | Durum | Davranış |
|---|---|---|
| **D1** | **Soru bozuk** — iki doğru şık, eksik veri, çelişkili öncül | `integrity:"flawed"` + `integrityNote`. `worked` yerine **tanı segmenti**: sorunun nesinin bozuk olduğu açıklanır. Zincir anlatımı **yine yapılır** (konu öğrenilir), ama **uydurma cevap üretilmez**. Öğrenci "ben anlamadım" sanmasın diye bu açıkça söylenir. |
| **D2** | **Kazanım bulunamıyor** | `chain[].outcomeCode` düşer; `curriculum` bloğu EXAM modunda **opsiyoneldir** → G-CURRICULUM tetiklenmez. Kullanıcıya bildirilir: "Bu soruyu bir MEB kazanımına bağlayamadım; konuyu genel bilgiyle anlattım." |
| **D3** | **Ders kitabı yok** (3·4·7·8·11·12. sınıf — TYMM kademeli yürürlüğü) | `verification.frame_source.kind:"program"` + `verdict:"supported_by_source"` (egitim-kaynak; `license` **zorunlu**). Yeni kural yok — `curriculum-integration.md` §6.1 dalı aynen geçerli. |
| **D4** | **Soru çerçeve üstü** — olimpiyat, ileri yayınevi sorusu | `integrity:"out_of_frame"` + `integrityNote`. Soru **yine çözülür**, açık not eklenir: "Bu soru 7. sınıf çerçevesinin üstünde; çözümü 9. sınıfta gelen X kavramını gerektiriyor." |
| **D5** | **Fotoğraf okunamıyor** | SOR, tahmin etme. Kısmi okunuyorsa neyin belirsiz olduğu tam olarak söylenir. |

### 5.1 EXAM ile CURRICULUM farkları (normatif)

| Kural | CURRICULUM | EXAM |
|---|---|---|
| `curriculum` bloğu | **zorunlu** | **opsiyonel** (D2) |
| `verification.scope.in_frame:false` | **üretimi durdurur** | **durdurmaz** (D4) |
| Yayın teklifi | üretim sonrası sorulur | **teklif edilmez** (K2) |
| `exam` bloğu | yok | **zorunlu** |

**D4 istisnasının gerekçesi:** CURRICULUM modunda `in_frame:false` üretimi durdurur,
çünkü orada model *neyi üreteceğini kendi seçer* ve çerçeve dışına taşması bir hatadır.
EXAM modunda soru **verilidir** — seçim yoktur. Öğrencinin önüne gelmiş bir soruyu
"çerçeve dışı" diye reddetmek işe yaramaz. Doğru davranış reddetmek değil, **dürüstçe
etiketleyip çözmektir**.

---

## 6. G-EXAM kapısı

Koşullu: yalnız `mode:"EXAM"` **veya** `exam` bloğu varsa tetiklenir.

**FAIL:** `exam` bloğu yok · `stem` boş · `transcriptionCheck` yok veya var olmayan bir
id'yi gösteriyor · `fadeFrom < adım sayısı` olan `worked` yok · `chain[]` boş veya
halkalarda `mappedTo` eksik · `mappedTo` id'si `segments[]`'te yok · `integrity` geçersiz
· `integrity` "sound" değilken `integrityNote` boş

**WARN:** `source` beyanı yok · `options` var ama `distractorAnalysis` yok

**DENETLEYEMEZ — dürüst sınır.** Validator çevrimdışıdır, MCP erişimi yoktur ve
`MODULE_DATA`'yı parse etmez (salt regex — G-CURRICULUM/G-VERIFY ile aynı sınır):
transkripsiyonun fotoğrafa sadık olduğunu, çözümün **doğru** olduğunu, zincirin
eksiksiz olduğunu, `outcomeCode`'un gerçek bir kazanım olduğunu **ölçemez**.

**Kapı beyanın BİÇİMİNİ ölçer, içeriğini değil.** Doğruluk yargısı modelindir ve insan
denetimine tabidir. Değeri şudur: zinciri iddia etmek, her halkayı bir segmente
bağlamayı zorunlu kılar.

---

## 7. Sınırlar

1. **Sınav/ödev sırasında kullanım için değildir.** Öğrenme sonrası araçtır; modül
   kapanışında wellbeing dilinde (suçlayıcı olmayan) bir not bulunur.
2. **Tek soru.** Fotoğrafta birden çok soru varsa hangisi olduğu **sorulur**. Çoklu-soru
   hata örüntüsü analizi bilinçli olarak kapsam dışıdır.
3. **MEB dışı müfredat kapsam dışıdır.** IB/Cambridge sorusunda çerçeve kurulamaz;
   dürüstçe söylenir.
4. **Transkripsiyon insan denetimine tabidir** — 2. segment tam da bunun içindir.
5. **Fotoğraf gömülmez** (K4). Motorda raster taşıyıcı yoktur.
````

- [ ] **Step 2: Emoji denetimi**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -c "
import re,sys
h=open('references/exam-solving.md',encoding='utf-8').read()
sys.path.insert(0,'scripts'); import validate_module as vm
m=vm.CORE_EMOJI_RE.findall(h)
print('emoji bulundu:', m if m else 'YOK')
sys.exit(1 if m else 0)"`

Expected: `emoji bulundu: YOK` ve çıkış kodu 0

- [ ] **Step 3: Commit**

```bash
git add plugins/edupedia/skills/carbon-edupedia/references/exam-solving.md
git commit -m "docs(edupedia): exam-solving.md — EXAM modunun normatif kaynağı

Dört karar, 8 adımlı akış, exam blok şeması, 11 segmentlik kurgu, beş degrade
protokolü (D1-D5) ve EXAM/CURRICULUM fark tablosu.

Tek kaynak ilkesi: komut ve SKILL.md buraya referans verir, kuralı tekrarlamaz.
Sınıf+ders kapısı curriculum-integration.md §3 Adım 0'a delege edilir."
```

---

### Task 3: `SKILL.md` + `skill-manifest.yaml` bağlantısı

**Files:**
- Modify: `skills/carbon-edupedia/SKILL.md` (§2 tetikleyiciler, §5 referans tablosu, §6 mod tablosu, §12 kapı listesi, metadata sürümü)
- Modify: `skills/carbon-edupedia/skill-manifest.yaml` (`skill.version`, `classification.triggers`, `references`, `inputs`, `verification.gates`, `build.version`)

**Interfaces:**
- Consumes: Task 1'in `G-EXAM` kapısı, Task 2'nin `references/exam-solving.md` dosyası
- Produces: `mode: "EXAM"` skill sözleşmesinde tanımlı hale gelir; Task 4'ün komutu buna dayanır

- [ ] **Step 1: `SKILL.md` §6 mod tablosuna EXAM satırını ekle**

`| **CURRICULUM** | …` satırının **ardına** ekle:

```markdown
| **EXAM** | **Sınav sorusu çözme modülü**: fotoğrafı çekilen veya yapıştırılan BİR soru transkribe edilip yeniden inşa edilir; geriye çözümlemeyle kavram zinciri öğretilir; çözüm `worked` + `fadeFrom` ile verilir (cevap asla doğrudan değil); `exam` bloğu doldurulur, G-EXAM ile doğrulanır | "bu soruyu çöz", "sınav sorusu", soru fotoğrafı yüklendi |
```

- [ ] **Step 2: `SKILL.md` §5 referans tablosuna satır ekle**

`| references/newgen-question-design.md | …` satırının **ardına** ekle:

```markdown
| `references/exam-solving.md` | **EXAM modunda ZORUNLU — akışın TAMAMI.** Fotoğrafı çekilen/yapıştırılan bir sınav sorusunu çözen modül: dört karar (K1-K4), 8 adımlı akış (transkripsiyon → sınıf/ders kapısı → geriye çözümleme → kazanım → çerçeve → çöz → kurgu → teslim), `exam` blok şeması, 11 segmentlik kurgu, beş degrade protokolü (D1-D5) ve EXAM/CURRICULUM fark tablosu. Yayın bu modda **teklif edilmez** (telif). |
```

- [ ] **Step 3: `SKILL.md` §2'ye tetikleyicileri ekle**

`**Müfredat MCP tetikleyicileri (Türkiye MEB / Maarif Modeli):**` bloğunun **öncesine** ekle:

```markdown
**Sınav sorusu tetikleyicileri (EXAM modu):**
- bir sınav sorusunun **fotoğrafı** yüklendi veya soru metni yapıştırıldı
- "bu soruyu çöz", "bu soruyu açıkla", "bunu nasıl yaparım"
- "sınav sorusu", "test sorusu", "deneme sorusu", "yazılı sorusu"
- "bu soruyu anlamadım", "bu soru neden B değil"
- Bu sinyallerde **`references/exam-solving.md` okunur ve akışın tamamı uygulanır**.
```

- [ ] **Step 4: `SKILL.md` §12 kapı listesine `G-EXAM`'ı ekle**

`- **G-CARBON-GRID (v3.0.0):** …` maddesinin **ardına** ekle:

```markdown
- **G-EXAM (v3.7.0, koşullu):** Yalnız `mode:"EXAM"` ise veya `exam` bloğu varsa
  tetiklenir (yoksa atlanır — geriye dönük uyum). Denetler: `exam.stem` dolu;
  `exam.transcriptionCheck` var olan bir segment id'sini gösteriyor (transkripsiyon
  doğrulaması atlanamaz); **`fadeFrom < adım sayısı` olan bir `worked` segmenti var**
  (cevap doğrudan verilemez — bu kapının çekirdek değeri); `exam.chain[]` dolu ve her
  halka `concept` + `segments[]`'te var olan bir `mappedTo` taşıyor;
  `exam.integrity` ∈ {`sound`, `flawed`, `out_of_frame`} ve `sound` değilse
  `integrityNote` dolu. WARN: `source` beyanı yok; `options` var ama
  `distractorAnalysis` yok. **DENETLEYEMEZ:** transkripsiyonun sadakatini, çözümün
  doğruluğunu, zincirin eksiksizliğini — hiçbiri çevrimdışı ölçülemez. Tam kural:
  `references/exam-solving.md` §6.
```

- [ ] **Step 5: `SKILL.md` metadata sürümünü yükselt**

Dosya başındaki frontmatter'da:

```yaml
metadata:
  version: 3.7.0
  last_updated: 2026-07-31
```

- [ ] **Step 6: `skill-manifest.yaml` — sürüm ve mod açıklaması**

`skill.version` alanını `3.7.0` yap. `inputs` içindeki `mode` girdisinin `description`
alanını şununla değiştir:

```yaml
    description: 'MODULE | QUIZ | FLASHCARDS | GAME | EXPLAINER | ASSESSMENT | SERIES | CURRICULUM | EXAM (varsayılan MODULE). CURRICULUM: MEB kazanımından üretim. EXAM: fotoğrafı çekilen/yapıştırılan bir sınav sorusundan üretim (references/exam-solving.md). Müfredat-duyarlılık tüm modlarda opsiyonel.'
```

- [ ] **Step 7: `skill-manifest.yaml` — tetikleyiciler**

`classification.triggers` listesinin **sonuna** ekle:

```yaml
    - 'bu soruyu çöz'
    - 'sınav sorusu'
    - 'test sorusu'
    - 'yazılı sorusu'
    - 'bu soruyu anlamadım'
    - 'soru fotoğrafı'
```

- [ ] **Step 8: `skill-manifest.yaml` — referans kaydı**

`references` listesinin **sonuna** ekle:

```yaml
  - path: references/exam-solving.md
    read_when: 'EXAM modunda ZORUNLU — akışın TAMAMI. Fotoğrafı çekilen veya yapıştırılan BİR sınav sorusunu çözen + gerektirdiği kavram zincirini öğreten modül: dört karar (K1-K4), 8 adımlı akış (transkripsiyon → sınıf/ders kapısı → geriye çözümleme → kazanım → çerçeve → çöz → kurgu → teslim), exam blok şeması, 11 segmentlik kurgu, beş degrade protokolü (D1 bozuk soru · D2 kazanım yok · D3 kitap yok · D4 çerçeve üstü · D5 okunmayan fotoğraf) ve EXAM/CURRICULUM fark tablosu. Soru transkribe + yeniden inşa edilir, fotoğraf GÖMÜLMEZ; yayın bu modda TEKLİF EDİLMEZ (telif). G-EXAM normatif kaynağı.'
```

- [ ] **Step 9a: Mevcut drift'i düzelt — `G-VERIFY` kaydı manifest'te yok**

`scripts/validate_module.py` `main()` içinde **14** kapı çalıştırır ama
`skill-manifest.yaml` `verification.gates` yalnız **13** tanesini beyan eder:
`G-VERIFY` kaydı hiç eklenmemiş. Bu, üzerinde çalıştığımız dosyadaki gerçek bir
sapmadır; `G-EXAM`'ı eklerken düzeltilir.

`verification.gates` listesinde `- id: G-CURRICULUM` girdisinin **ardına** ekle:

```yaml
    - id: G-VERIFY
      severity: FAIL
      description: 'v3.6.0. Koşullu (müfredat-temelli modülde): kapsam + doğruluk denetiminin KAYDI. verification bloğu zorunlu; frame_source document_id + kind taşır; scope.in_frame true (false ise FAIL, yayınlanmaz); claims[] boş değil ve her öğede claim + grounding + verdict var. verdict general_knowledge = WARN (çoğunluksa FAIL); supported_by_source grounding''i license taşımalı. Yargıyı MODEL yapar, kapı YAPIYI denetler — iddianın doğruluğunu, belgenin varlığını, sayfayı DOĞRULAYAMAZ (MCP erişimi yok). Normatif kaynak: references/curriculum-integration.md §6.1.'
```

- [ ] **Step 9b: `skill-manifest.yaml` — `G-EXAM` kapı kaydı**

`verification.gates` listesinin **sonuna** ekle:

```yaml
    - id: G-EXAM
      severity: FAIL
      description: 'v3.7.0. Koşullu (yalnız mode EXAM veya exam bloğu varsa; aksi halde atlanır). exam.stem dolu; exam.transcriptionCheck var olan bir segment id''sini gösteriyor; fadeFrom < adım sayısı olan bir worked segmenti var (cevap doğrudan verilemez — çekirdek denetim); exam.chain[] dolu ve her halka concept + segments[]''te var olan mappedTo taşıyor; exam.integrity sound|flawed|out_of_frame ve sound değilse integrityNote dolu. WARN: source beyanı yok; options var ama distractorAnalysis yok. Salt-metin denetim — transkripsiyonun sadakatini/çözümün doğruluğunu ÖLÇEMEZ. Normatif kaynak: references/exam-solving.md.'
```

- [ ] **Step 10: `skill-manifest.yaml` — build sürümü**

`build.version` alanını `3.7.0`, `build.release_date` alanını `'2026-07-31'` yap.

- [ ] **Step 11: YAML geçerliliğini doğrula**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -c "
import yaml
d = yaml.safe_load(open('skill-manifest.yaml', encoding='utf-8'))
gates = [g['id'] for g in d['verification']['gates']]
refs = [r['path'] for r in d['references']]
assert 'G-EXAM' in gates, gates
assert 'references/exam-solving.md' in refs, refs
assert 'G-VERIFY' in gates, 'G-VERIFY drift duzeltilmedi'
assert d['skill']['version'] == '3.7.0'
assert d['build']['version'] == '3.7.0'
print('YAML gecerli; kapi sayisi:', len(gates), '| referans sayisi:', len(refs))"`

Expected: `YAML gecerli; kapi sayisi: 15 | referans sayisi: 17`

(Başlangıç: 13 kapı beyanlı + `G-VERIFY` drift düzeltmesi + `G-EXAM` = 15; bu artık
`main()`'in çalıştırdığı 15 kapıyla birebir örtüşür. Referans: 16 + `exam-solving.md` = 17.)

> `PyYAML` kurulu değilse: `python3 -m pip install --user pyyaml`. Bu yalnız bir
> doğrulama aracıdır — `validate_module.py` YAML okumaz, çalışma zamanı bağımlılığı
> eklenmez (Global Constraints).

- [ ] **Step 12: Referans dosyasının gerçekten var olduğunu doğrula**

Run: `cd plugins/edupedia/skills/carbon-edupedia && test -f references/exam-solving.md && grep -c "^## " references/exam-solving.md`

Expected: `7` (yedi üst düzey bölüm)

- [ ] **Step 13: Commit**

```bash
git add plugins/edupedia/skills/carbon-edupedia/SKILL.md \
        plugins/edupedia/skills/carbon-edupedia/skill-manifest.yaml
git commit -m "feat(edupedia): carbon-edupedia 3.7.0 — EXAM modu skill sözleşmesine bağlandı

SKILL.md: 9. mod (EXAM), §2 tetikleyiciler, §5 referans satırı, §12 G-EXAM kapısı.
skill-manifest.yaml: sürüm 3.7.0, 6 yeni tetikleyici, exam-solving.md referansı,
G-EXAM kapı kaydı.

Ayrıca mevcut bir drift düzeltildi: G-VERIFY kaydı manifest'te hiç yoktu —
main() 14 kapı çalıştırırken manifest 13 tanesini beyan ediyordu. Artık
G-EXAM ile birlikte 15 kapı beyanlı ve çalışan kapı setiyle birebir örtüşüyor.

Kural çoğaltması yok: her iki dosya da exam-solving.md'ye referans verir."
```

---

### Task 4: `/edupedia:soru` komutu ve plugin yüzeyleme

**Files:**
- Create: `commands/soru.md`
- Modify: `plugin.json` (`description` alanı — komut listesi)
- Modify: `skills/start/SKILL.md` (Adım 4 komut tablosu, Adım 5 niyet yönlendirme)

**Interfaces:**
- Consumes: Task 2'nin `references/exam-solving.md` dosyası, Task 3'ün `EXAM` modu
- Produces: Kullanıcıya görünen `/edupedia:soru` giriş noktası

- [ ] **Step 1: `commands/soru.md` dosyasını oluştur**

```markdown
---
description: Fotoğrafı çekilen veya yapıştırılan bir sınav sorusunu pedagojik ilkelerle çözen + gerektirdiği kavram zincirini öğreten etkileşimli modül üretir
argument-hint: "<soru fotoğrafı veya soru metni> [+ opsiyonel ders/sınıf]"
---

`edupedia:carbon-edupedia` skill'ini **EXAM modunda** çağır. Mantığı burada tekrarlama —
skill'in modları, kalite kapıları ve pedagojik davranışı olduğu gibi geçerlidir; bu komut
yalnız soru → modül giriş noktasını kanonikleştirir.

**Girdi:** $ARGUMENTS *(soru fotoğrafı veya yapıştırılmış soru metni)*

## Yürütme protokolü

**Normatif kaynak: skill `references/exam-solving.md` — akışın TAMAMI oradadır.**
Bu komut kuralı **tekrarlamaz**; aşağıdaki liste yalnız bir haritadır.

1. **Referansı oku:** `references/exam-solving.md` (EXAM modunda zorunlu) +
   `references/adhd-pedagogy.md` (her modülden önce zorunlu).
2. **Transkripsiyon** (§2 Adım 1): soruyu birebir metne çevir; şekil varsa yazar-SVG
   olarak yeniden çiz. **Belirsizlik varsa SOR** — neyin okunmadığını tam söyle.
3. **KAPI** (§2 Adım 2): ders + sınıf kesinleşmeden üretim başlamaz. Kural tek yerde:
   `references/curriculum-integration.md` §3 Adım 0. Yoksa `AskUserQuestion` ile sor.
4. **Geriye çözümleme** (§2 Adım 3): "bunu çözmek için önce neyi bilmek gerekiyor?"
   → 2-4 halkalı kavram zinciri.
5. **Kazanım + çerçeve** (§2 Adım 4-5): her halkayı `search_learning_outcomes` ile
   kazanıma bağla; `list_textbooks` → `get_document_text` ile ders kitabını aç.
   Bağlanamıyorsa **D2**, kitap yoksa **D3** (§5).
6. **Çöz** (§2 Adım 6): her adımın dayanağı kitap sayfası. Soru bozuksa **D1**,
   çerçeve üstüyse **D4**.
7. **Kur + doğrula** (§2 Adım 7-8): `exam` bloğu (§3) + 11 segmentlik kurgu (§4);
   `scripts/validate_module.py` ile G-EXAM dahil kapıları geçir;
   `/mnt/user-data/outputs/` altına kebab-case adla kaydet + yan yana `.manifest.json`.

## Yayın

**Bu modda yayın TEKLİF EDİLMEZ** (`exam-solving.md` K2 — telif). `/edupedia:modul` ve
`/edupedia:mufredat`'ın aksine "yayınlamamı ister misin?" sorusu **sorulmaz**.

Kullanıcı kendisi isterse: telif uyarısını ver ("bu soru size ait değilse
edupedia.cureonics.com'da yayınlamak telif ihlali olabilir"), sonra karar kullanıcınındır —
engelleme.

## Sınırlılık

- Fotoğrafta **birden çok soru** varsa hangisini istediğini **sor** — bu komut tek soru
  işler (§7).
- Kazanım kodundan modül isteniyorsa → `/edupedia:modul`; ders+sınıf+konudan →
  `/edupedia:mufredat`; yalnız "hangi kazanımlar" keşfi → `/edupedia:kazanim-bul`.
- MEB dışı müfredat (IB/Cambridge) kapsam dışıdır; çerçeve kurulamaz, dürüstçe söylenir.
```

- [ ] **Step 2: `plugin.json` — komut listesini güncelle**

`description` alanı içinde geçen şu metni bul:

```
Beş komut: /edupedia:modul (kazanım kodundan), /edupedia:mufredat (ders+sınıf+konudan), /edupedia:kazanim-bul (kazanım keşfi), /edupedia:yayinla
```

Şununla değiştir:

```
Altı komut: /edupedia:modul (kazanım kodundan), /edupedia:mufredat (ders+sınıf+konudan), /edupedia:soru (fotoğrafı çekilen/yapıştırılan sınav sorusunu çözen + kavram zincirini öğreten EXAM modülü; soru transkribe edilir, fotoğraf gömülmez; cevap worked+fadeFrom ile asla doğrudan verilmez; yayın teklif edilmez — telif), /edupedia:kazanim-bul (kazanım keşfi), /edupedia:yayinla
```

Ayrıca `version` alanını `0.7.0` yap.

- [ ] **Step 3: `plugin.json` geçerliliğini doğrula**

Run: `cd plugins/edupedia && python3 -c "
import json
d = json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))
assert d['version'] == '0.7.0', d['version']
assert '/edupedia:soru' in d['description']
assert 'Altı komut' in d['description']
print('plugin.json gecerli; surum', d['version'])"`

Expected: `plugin.json gecerli; surum 0.7.0`

- [ ] **Step 4: `skills/start/SKILL.md` — Adım 4 komut tablosuna satır ekle**

`| /edupedia:mufredat | …` satırının **ardına** ekle:

```markdown
| `/edupedia:soru` | Sınav sorusundan modül üretir (fotoğraf veya metin) — çözer + kavram zincirini öğretir | `<soru fotoğrafı veya metni>` |
```

- [ ] **Step 5: `skills/start/SKILL.md` — Adım 5 niyet yönlendirmesine madde ekle**

`3. **"Bu konuya hangi kazanımlar denk geliyor?"** …` maddesinin **öncesine** ekle
(numaralandırmayı kaydır — sonraki maddeler 4, 5, 6, 7 olur):

```markdown
3. **Sınav sorusu fotoğrafı veya metni verildi** ("bu soruyu çöz", "bunu anlamadım") →
   `/edupedia:soru`. Yayın bu modda teklif edilmez (telif).
```

- [ ] **Step 6: Komut dosyasının frontmatter'ını doğrula**

Run: `cd plugins/edupedia && python3 -c "
import re
h = open('commands/soru.md', encoding='utf-8').read()
m = re.match(r'^---\n(.*?)\n---\n', h, re.S)
assert m, 'frontmatter yok'
fm = m.group(1)
assert 'description:' in fm and 'argument-hint:' in fm, fm
assert 'exam-solving.md' in h, 'normatif referansa delege edilmemis'
print('commands/soru.md gecerli')"`

Expected: `commands/soru.md gecerli`

- [ ] **Step 7: Emoji denetimi (yeni/değişen dosyalar)**

Run: `cd plugins/edupedia && python3 -c "
import sys
sys.path.insert(0,'skills/carbon-edupedia/scripts'); import validate_module as vm
bad = []
for p in ['commands/soru.md','.claude-plugin/plugin.json','skills/start/SKILL.md',
          'skills/carbon-edupedia/SKILL.md','skills/carbon-edupedia/skill-manifest.yaml']:
    m = vm.CORE_EMOJI_RE.findall(open(p, encoding='utf-8').read())
    if m: bad.append((p, m[:3]))
print('emoji ihlali:', bad if bad else 'YOK')
sys.exit(1 if bad else 0)"`

Expected: `emoji ihlali: YOK` ve çıkış kodu 0

- [ ] **Step 8: Commit**

```bash
git add plugins/edupedia/commands/soru.md \
        plugins/edupedia/.claude-plugin/plugin.json \
        plugins/edupedia/skills/start/SKILL.md
git commit -m "feat(edupedia): /edupedia:soru komutu + plugin 0.7.0 yüzeyleme

Altıncı komut: sınav sorusu fotoğrafı/metni → EXAM modülü. Komut kuralı
tekrarlamaz, exam-solving.md'ye delege eder (tek kaynak ilkesi).

start/SKILL.md komut tablosuna ve niyet yönlendirmesine eklendi.
Yayın bu modda teklif edilmez (telif)."
```

---

### Task 5: Uçtan uca doğrulama

**Files:**
- Test: geçici dosya `/tmp/exam-smoke.html` (commit edilmez)
- Doğrulanır: `skills/carbon-edupedia/scripts/validate_module.py`, `assets/module-template.html` (salt-okunur)

**Interfaces:**
- Consumes: Task 1-4'ün tamamı
- Produces: Yok (doğrulama görevi)

- [ ] **Step 1: Motorun değişmediğini kanıtla**

Run: `cd /mnt/thunderbolt/workspaces/CureoPrivate && git diff --stat main -- plugins/edupedia/skills/carbon-edupedia/assets/module-template.html plugins/edupedia/agents/module-auditor.md`

Expected: **boş çıktı** (hiç değişiklik yok). Çıktı boş değilse Global Constraints ihlali — dur ve bildir.

- [ ] **Step 2: Gerçek şablondan bir EXAM modülü türet**

Mevcut fixture'ı kopyalayıp `MODULE_DATA`'sını Task 1'deki `EXAM_OK` gövdesiyle değiştir:

```bash
cd /mnt/thunderbolt/workspaces/CureoPrivate/plugins/edupedia/skills/carbon-edupedia
python3 - <<'PY'
import re
src = open('tests/fixtures/minimal_pass.html', encoding='utf-8').read()
exam_block = '''  exam: {
    stem: "3/4 kg elma 24 TL ise 2/3 kg elma kac TL'dir?",
    options: ["12 TL", "14 TL", "16 TL", "18 TL"],
    source: "ogrenci fotografi - okul yazilisi",
    integrity: "sound",
    integrityNote: "",
    transcriptionCheck: "tc1",
    distractorAnalysis: "d1",
    chain: [
      { concept: "birim fiyat", outcomeCode: "MAT.6.1.4.1", mappedTo: ["t1"] },
      { concept: "kesirle bolme", outcomeCode: "MAT.6.1.4.2", mappedTo: ["w1"] }
    ]
  },
'''
extra_segments = '''    { type: "selfExplain", id: "tc1", prompt: "Soruyu boyle okudum. Bir yeri farkliysa yaz.",
      modelExplanation: "<p>Farkliysa dogrusunu yazip tekrar sor.</p>" },
    { type: "teach", id: "t1", title: "Birim fiyat", body: ["<p>Birim fiyat, bir birim urunun fiyatidir.</p>"] },
    { type: "worked", id: "w1", title: "Cozum",
      steps: [ { text: "24 : 3/4 = 32" }, { text: "32 x 2/3 = ?", answer: ["21,33"] } ],
      fadeFrom: 1 },
    { type: "mcq", id: "d1", title: "Celdirici analizi",
      questions: [ { stem: "B sikki neden cazip ama yanlis?",
                     options: ["Birim fiyati atliyor", "Dogru", "Ilgisiz"],
                     correctIndex: 0, explanation: "B, birim fiyat adimini atlar." } ] },
'''
# mode'u EXAM yap ve exam blogunu meta'nin ardina ekle
src = re.sub(r'(mode\s*:\s*)["\'][A-Z]+["\']', r'\1"EXAM"', src, count=1)
src = src.replace('  segments: [', exam_block + '  segments: [\n' + extra_segments, 1)
open('/tmp/exam-smoke.html', 'w', encoding='utf-8').write(src)
print('yazildi: /tmp/exam-smoke.html')
PY`

Expected: `yazildi: /tmp/exam-smoke.html`

> Bu betiğin `mode:` veya `segments: [` desenini bulamaması mümkündür (fixture
> güncellenmişse). O durumda dosyayı elle düzenle — amaç, **gerçek motor şablonu**
> üzerinde `exam` bloğunun kapıdan geçtiğini görmektir.

- [ ] **Step 3: Tam kapı setini çalıştır**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 scripts/validate_module.py /tmp/exam-smoke.html --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('G-EXAM :', d['G-EXAM'])
fails = {g: v for g, v in d.items() if v['status'] == 'FAIL'}
print('FAIL kapilar:', fails if fails else 'YOK')"`

Expected: `G-EXAM` durumu `PASS`. Başka bir kapı FAIL veriyorsa **o kapı bu planın kapsamı dışındadır** — fixture'dan gelen bir sorun olabilir; not al ama G-EXAM'ı gevşetme.

- [ ] **Step 4: Negatif duman testi — cevap doğrudan verilirse kapı düşmeli**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -c "
import sys, json, subprocess
h = open('/tmp/exam-smoke.html', encoding='utf-8').read().replace('fadeFrom: 1', 'fadeFrom: 2')
open('/tmp/exam-smoke-bad.html','w',encoding='utf-8').write(h)
" && python3 scripts/validate_module.py /tmp/exam-smoke-bad.html --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('G-EXAM :', d['G-EXAM']['status'])
assert d['G-EXAM']['status'] == 'FAIL', 'cevap dogrudan verilirken kapi gecti!'
print('DOGRULANDI: cevap dogrudan verilince G-EXAM dusuyor')"`

Expected: `G-EXAM : FAIL` ve `DOGRULANDI: ...`

Bu adım, planın **çekirdek iddiasını** kanıtlar: ödev-çözme makinesi olmak yapısal
olarak engellenmiştir.

- [ ] **Step 5: Geçici dosyaları temizle**

```bash
rm -f /tmp/exam-smoke.html /tmp/exam-smoke-bad.html
```

- [ ] **Step 6: Tüm test paketini son kez çalıştır**

Run: `cd plugins/edupedia/skills/carbon-edupedia && python3 -m pytest tests/test_gates.py -v`

Expected: Tüm testler PASS

- [ ] **Step 7: Dal özetini çıkar**

Run: `cd /mnt/thunderbolt/workspaces/CureoPrivate && git log --oneline main..HEAD && git diff --stat main..HEAD`

Expected: 5 commit (spec + Task 1-4); `module-template.html` ve `module-auditor.md`
**diff'te görünmemeli**.

---

## Kapsam dışı (bilinçli olarak yapılmayanlar)

Bu maddeler spec'te kayıtlıdır ve **bu planda uygulanmaz**:

1. **Yayın sunucusuna `G-EXAM` taşıma.** `CureoHub/services/edupedia_site/app/gates/`
   plugin validator'ın vendored kopyasıdır ve `tools/check_gates_drift.py` ile
   drift-denetlenir. `G-EXAM` eklendiğinde bu kopya **sapacaktır**. Bu ayrı bir iştir
   (ayrı repo, ayrı deploy) — ama EXAM modülleri varsayılan olarak yayınlanmadığı için
   (K2) acil değildir. **Drift denetimi kırmızıya dönerse beklenen davranıştır.**
2. **Tier-2 raster gömme dalı.** Spec §10'daki bağımsız bulgu: `visual.kind:"image"`
   motorda yok, ama dokümante edilmiş. Ayrı iş.
3. **Çoklu soru / hata örüntüsü analizi.** Spec §9.3 — ayrı yetenek, ayrı spec.
4. **`module-auditor`'a beşinci eksen.** Mevcut dört eksen EXAM modülünde de geçerli;
   yeni eksen YAGNI.

---

## Doğrulama özeti

Plan tamamlandığında şunlar doğrulanmış olur:

| İddia | Kanıt |
|---|---|
| `G-EXAM` çalışıyor ve koşullu | Task 1 Step 10-11 (14 test + regresyon) |
| Koşturulmayan kapı `PASS` demiyor | Task 1 Step 12 (`SKIPPED` çıktısı) |
| Cevap doğrudan verilirse kapı düşüyor | Task 5 Step 4 (negatif duman testi) |
| Motor değişmedi | Task 5 Step 1 (boş `git diff --stat`) |
| Emoji yok | Task 2 Step 2, Task 4 Step 7 |
| Manifest tutarlı | Task 3 Step 11 (YAML + kapı/referans varlığı) |
| Mevcut `G-VERIFY` drift'i kapandı | Task 3 Step 9a + Step 11 (15 kapı = `main()` seti) |
| Komut normatif kaynağa delege ediyor | Task 4 Step 6 (`exam-solving.md` referansı) |
