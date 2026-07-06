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
