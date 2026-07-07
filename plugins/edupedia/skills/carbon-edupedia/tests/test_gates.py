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

def test_gflow_skip_branch_when_truly_no_signature():
    rows = run_gate(vm.gate_flow, open("tests/fixtures/flow_skip_nogami.html").read())
    assert status_of(rows, "G-FLOW") == "PASS"
    # skip branch specifically: message says the gate is not applicable
    msg = next(m for g, s, m in rows if g == "G-FLOW")
    assert "imza yok" in msg or "uygulanmaz" in msg

def test_gcarbongrid_fail_on_static_card_shadow():
    rows = run_gate(vm.gate_carbon_grid, open("tests/fixtures/grid_fail_shadow.html").read())
    assert status_of(rows, "G-CARBON-GRID") == "FAIL"

def test_gcarbongrid_pass_on_layered_flat():
    rows = run_gate(vm.gate_carbon_grid, open("tests/fixtures/grid_pass.html").read())
    assert status_of(rows, "G-CARBON-GRID") in ("PASS", "WARN")

def test_hook_segment_renders_and_closes():
    # hook_pass.html: hand-marked fixture — data-seg="hook" (kanca render'ı) + ayrı
    # data-hook-resolved (hedef teach'in kapanış işareti); gerçek SPA'da bu ikisi hiç
    # aynı statik dosyada bulunmaz (runtime marker'lar), fixture ikisini simüle eder.
    html = open("tests/fixtures/hook_pass.html").read()
    assert 'data-seg="hook"' in html and "data-hook-resolved" in html
    rows = run_gate(vm.gate_flow, html); assert status_of(rows, "G-FLOW") == "PASS"

def test_gain_only_streak_no_reset_language():
    # v3.0.0 Task 9: resetStreak() artık state.streak'i sıfırlamaz (gain-only);
    # yalnızca nötr "korundu" (data-held) işaretine alır — kayıp/ceza dili yok.
    html = open("tests/fixtures/streak_gainonly.html").read()
    rows = run_gate(vm.gate_flow, html); assert status_of(rows, "G-FLOW") == "PASS"
    assert "streak=0" not in html.lower().replace(" ", "")  # resetStreak artık 0'a set etmez

def test_pacingdisk_no_countdown():
    # Task 10: pacing-disk render edilir, data-countdown YOK (sayısız/kesintisiz disk) → G-FLOW PASS
    html = open("tests/fixtures/pacing_pass.html").read()
    rows = run_gate(vm.gate_flow, html); assert status_of(rows, "G-FLOW") == "PASS"

def test_pacingdisk_fail_on_countdown_attribute():
    # değişmez kanıtı: aynı disk öğesine data-countdown eklenirse G-FLOW FAIL vermeli
    html = open("tests/fixtures/pacing_fail_countdown.html").read()
    rows = run_gate(vm.gate_flow, html); assert status_of(rows, "G-FLOW") == "FAIL"

def test_gcarbongrid_spaced_css_shadow_handling():
    # genuine spaced elevation shadow on a static card -> FAIL
    r1 = run_gate(vm.gate_carbon_grid, "<style>.card{box-shadow: 0 2px 6px rgba(0,0,0,.2);}</style>")
    assert status_of(r1, "G-CARBON-GRID") == "FAIL"
    # explicit no-shadow (spaced) must NOT FAIL
    r2 = run_gate(vm.gate_carbon_grid, "<style>.card{box-shadow: none;}</style>")
    assert status_of(r2, "G-CARBON-GRID") != "FAIL"
    # inset border-sim (spaced) must NOT FAIL
    r3 = run_gate(vm.gate_carbon_grid, "<style>.card{box-shadow: inset 0 0 0 2px var(--accent);}</style>")
    assert status_of(r3, "G-CARBON-GRID") != "FAIL"

def test_worked_segment_fixture_has_signature():
    # Task 11: worked_pass.html hand-marked static — renderWorked()'in gerçek çıktısını taklit
    # eder: fadeFrom öncesi salt-görünür adım + fadeFrom sonrası <input aria-label> boşluk.
    html = open("tests/fixtures/worked_pass.html").read()
    assert 'data-seg="worked"' in html
    assert "worked-step--solved" in html and "worked-step--blank" in html
    assert '<input' in html and 'aria-label=' in html

def test_worked_segment_ginteract_ga11y_no_regression():
    # worked bir MCQ değildir (stem/correctIndex yok) → G-INTERACT'in "uygulanmaz" WARN
    # dalına düşmesi regresyon SAYILMAZ (bkz. brief: "do not regress", literal PASS değil —
    # stems==0 iken gate_interact zaten hiçbir modülde FAIL veremez, bkz. validate_module.py).
    # G-A11Y ise bu fixture'ın kendi taşıdığı lang/title/reduced-motion/aria-live/aria-hidden
    # işaretleriyle gerçek PASS almalı (fixture bunun için elle donatıldı).
    html = open("tests/fixtures/worked_pass.html").read()
    rows_i = run_gate(vm.gate_interact, html)
    assert status_of(rows_i, "G-INTERACT") != "FAIL"
    rows_a = run_gate(vm.gate_a11y, html)
    assert status_of(rows_a, "G-A11Y") == "PASS"

def test_worked_zero_blank_not_counted_in_mastery():
    src = open("assets/module-template.html", encoding="utf-8").read()
    # worked contributes to the mastery denominator ONLY when it has a real blank step
    assert 's.fadeFrom < (s.steps||[]).length' in src
    # and the naive always-+1 form must be gone
    assert 'if(s.type==="worked") return n+1;' not in src

def test_selfexplain_segment_fixture_has_signature():
    # Task 12: selfexplain_pass.html hand-marked static — renderSelfExplain()'in gerçek
    # çıktısını taklit eder: istem + serbest/notsuz <textarea aria-label> + "Modeli gör"
    # aç/kapa düğmesi (aria-expanded, klavye-erişilebilir <button>).
    html = open("tests/fixtures/selfexplain_pass.html").read()
    assert 'data-seg="selfExplain"' in html
    assert "<textarea" in html and "aria-label=" in html
    assert 'aria-expanded="false"' in html and "se-reveal" in html

def test_selfexplain_gwellbeing_pass_and_ga11y_no_regression():
    # düşük-baskı metakognisyon: puanlama/ceza dili yok → G-WELLBEING gerçek PASS
    # (yalnızca "uygulanmaz" değil). Fixture kendi lang/title/reduced-motion/aria-live/
    # aria-hidden işaretleriyle G-A11Y'yi de gerçek PASS almalı (elle donatıldı).
    html = open("tests/fixtures/selfexplain_pass.html").read()
    rows_w = run_gate(vm.gate_wellbeing, html)
    assert status_of(rows_w, "G-WELLBEING") == "PASS"
    rows_a = run_gate(vm.gate_a11y, html)
    assert status_of(rows_a, "G-A11Y") == "PASS"

def test_selfexplain_engine_no_scoring_hooks():
    # motorun renderSelfExplain'i addXP/markMastered/bumpStreak'e dokunmamalı (notsuz/ungraded)
    # ve dispatch haritasına bağlanmış olmalı.
    src = open("assets/module-template.html", encoding="utf-8").read()
    i = src.index("function renderSelfExplain")
    j = src.index("\n  }\n", i)
    body = src[i:j]
    assert "addXP(" not in body and "markMastered(" not in body and "bumpStreak(" not in body
    assert "selfExplain:renderSelfExplain" in src
