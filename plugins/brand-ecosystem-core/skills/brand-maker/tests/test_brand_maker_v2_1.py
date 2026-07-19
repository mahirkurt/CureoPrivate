#!/usr/bin/env python3
"""
Regression tests for brand-maker v2.1 — expert-audit remediation.

Every one of the FIVE concrete failure cases the independent brand auditor found
is encoded here as a fixture. These tests are DETERMINISTIC and OFFLINE (domain
checks use --offline so no network is required); the point is that the SCRIPTS
themselves can never re-emit the audited defects.

Run standalone (CI-friendly, exits non-zero on any failure):
    python3 tests/test_brand_maker_v2_1.py

Or with pytest:
    pytest tests/test_brand_maker_v2_1.py -q

Pure Python 3.8+ stdlib. No third-party deps.
"""

import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(mod_name):
    path = SCRIPTS / f"{mod_name}.py"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

domain_recon = _load("domain_recon")
shortlist_diversity_check = _load("shortlist_diversity_check")
pharma_brand_collision = _load("pharma_brand_collision")
phonetic_analyzer = _load("phonetic_analyzer")
turkish_semantic_check = _load("turkish_semantic_check")


# The audited 14-finalist shortlist — every name in a single -anza/-anta/-onta
# morpheme family (one algorithm's variations, not distinct territories).
AUDITED_SHORTLIST = [
    "Auronza", "Nortanza", "Ortanza", "Selvanza", "Claranta", "Sanventa",
    "Faronta", "Fidonta", "Ortanta", "Valanza", "Merventa", "Toronta",
    "Cavanza", "Rovonta",
]


# ---------------------------------------------------------------------------
# Fixture 1 — DOMAIN FALSE-POSITIVE (auronza.com / nortanza.com were reported
# "available (standard)" but are REGISTERED). No single signal may report
# "available"; offline must degrade to "unverified", never "available".
# ---------------------------------------------------------------------------

def test_domain_auronza_nortanza_never_available_offline():
    for name in ("Auronza", "Nortanza"):
        r = domain_recon.verify_domain(name, ".com", offline=True)
        assert r["available"] is not True, f"{name}.com must not be 'available'"
        assert r["verification_status"] == "unverified", \
            f"{name}.com offline must be 'unverified', got {r['verification_status']}"
        assert "MÜSAİT" not in r["verdict"], \
            f"{name}.com verdict must not claim MÜSAİT: {r['verdict']}"


def test_domain_single_source_free_is_only_provisional():
    # One live source says free, the other unreachable → provisional, NOT available.
    r = domain_recon.verify_domain(
        "Zzxqvmkp", ".com", offline=False,
        rdap_fn=lambda d, t: {"status": "available", "detail": "stub"},
        whois_fn=lambda d, t: {"status": "unreachable", "detail": "stub"},
    )
    assert r["verification_status"] == "provisional_available"
    assert r["available"] is None, "single-source free must NOT be True"


def test_domain_two_sources_free_is_confirmed_available():
    r = domain_recon.verify_domain(
        "Zzxqvmkp", ".com", offline=False,
        rdap_fn=lambda d, t: {"status": "available", "detail": "stub"},
        whois_fn=lambda d, t: {"status": "available", "detail": "stub"},
    )
    assert r["verification_status"] == "confirmed_available"
    assert r["available"] is True


def test_domain_any_registered_source_is_taken():
    r = domain_recon.verify_domain(
        "Auronza", ".com", offline=False,
        rdap_fn=lambda d, t: {"status": "registered", "detail": "stub"},
        whois_fn=lambda d, t: {"status": "unreachable", "detail": "stub"},
    )
    assert r["verification_status"] == "confirmed_taken"
    assert r["available"] is False


# ---------------------------------------------------------------------------
# Fixture 2 — PHARMA BRAND FALSE-NEGATIVE (Claranta passed the web pre-scan but
# collides with the clarithromycin/Claritin brand family and is a registered
# Class-5 mark). Must be flagged; single-source "clean" must be impossible.
# ---------------------------------------------------------------------------

def test_claranta_flagged_as_pharma_brand_collision():
    data = pharma_brand_collision.load_data(None)
    r = pharma_brand_collision.scan("Claranta", data)
    assert r["collision_found"] is True, "Claranta must be flagged"
    assert r["score"] <= 1, f"Claranta must not score clean (got {r['score']})"
    matches = " ".join(
        (f.get("inn") or "") + " " + (f.get("match") or "") for f in r["findings"]
    ).lower()
    assert "clarithromycin" in matches or "clari" in matches, \
        "Claranta collision must reference the clarithromycin/clari family"


def test_pharma_clean_result_still_carries_mandatory_caveat():
    # Even a no-hit result must never be reported as "clean" without caveat.
    data = pharma_brand_collision.load_data(None)
    r = pharma_brand_collision.scan("Vexoryn", data)
    assert r["provenance"]["live_tm_checked"] is False
    assert r["mandatory_caveat"], "a caveat is mandatory on every result"
    # score 2 verdict must still say formal research is required, never a bare "clean"
    assert "gerekli" in r["verdict"].lower() or r["score"] <= 1


# ---------------------------------------------------------------------------
# Fixture 3 — HOMOGENEITY (all 14 finalists share the -anza/-anta/-onta family).
# The set-level diversity gate must FAIL and trigger a second round.
# ---------------------------------------------------------------------------

def test_audited_shortlist_fails_diversity_gate():
    result = shortlist_diversity_check.analyze(AUDITED_SHORTLIST)
    assert result["passed"] is False, "the 14-name family must FAIL the gate"
    assert result["trigger_second_round"] is True
    assert result["metrics"]["saturated_family_share"] >= 0.9, \
        "family share should be ~1.0 for this set"
    assert result["missing_territories"], "gate must suggest complementary territories"


def test_diverse_shortlist_passes_diversity_gate():
    diverse = ["Arc", "Veridya", "Kodak", "Atlas", "Granola"]
    result = shortlist_diversity_check.analyze(diverse)
    assert result["passed"] is True, "a genuinely diverse shortlist must PASS"


# ---------------------------------------------------------------------------
# Fixture 4 — NAIVE PERCEPTION (intended etymology ≠ perceived root):
# Ortanza/Ortanta → "orta" (mediocre); Selvanza → "selva".
# ---------------------------------------------------------------------------

def test_ortanza_naive_reads_orta_negative():
    a = turkish_semantic_check.analyze("Ortanza", intended_root="ortus")
    l6 = a["layer6_naive_perception"]
    assert l6["dominant_perceived"] is not None
    assert l6["dominant_perceived"]["token"] == "orta"
    assert l6["dominant_perceived"]["polarity"] == "negative"
    assert l6["has_negative_perception"] is True
    # first-class: it must be in the verdict flags, not buried
    assert any("orta" in f for f in a["turkish_market_verdict"]["naive_perception_flags"])


def test_ortanta_naive_reads_orta():
    a = turkish_semantic_check.analyze("Ortanta")
    assert a["layer6_naive_perception"]["dominant_perceived"]["token"] == "orta"


def test_selvanza_naive_reads_selva_with_intent_deviation():
    a = turkish_semantic_check.analyze("Selvanza", intended_root="salv")
    l6 = a["layer6_naive_perception"]
    assert l6["dominant_perceived"]["token"] == "selva"
    assert l6["intent_perception_deviation"] is True


# ---------------------------------------------------------------------------
# Fixture 5 — SCORE CEILING (phonetic + Turkish scores piled at 95-100 and did
# not discriminate). Recalibrated scores must spread meaningfully.
# ---------------------------------------------------------------------------

def test_phonetic_scores_no_longer_pile_at_95_100():
    mixed = ["Kodak", "Xerox", "Groq", "Ortanza", "Selvanza", "Veridya",
             "Lumina", "Zenith", "Apex", "Granola", "Stripe", "Ozempic"]
    comps = [phonetic_analyzer.analyze(n)["readiness_score"] for n in mixed]
    assert not all(c >= 95 for c in comps), "scores must not all pile at 95-100"
    assert max(comps) - min(comps) >= 20, \
        f"composite must show a spread ≥20 (got {max(comps)-min(comps)})"
    assert len(set(comps)) >= 6, "composite must show meaningful distinct values"


def test_phonetic_axes_are_separate():
    # A smooth -anza name: high ease, LOW brand strength (that's the whole point).
    a = phonetic_analyzer.analyze("Ortanza")
    assert a["pronunciation_ease"] >= 80, "ease legitimately high for smooth name"
    assert a["brand_strength"]["score"] <= 55, \
        "brand strength must be low for a template -anza name"
    assert a["pronunciation_ease"] - a["brand_strength"]["score"] >= 20, \
        "the two axes must genuinely diverge"


def test_turkish_verdict_discriminates():
    # -anza family with a negative naive reading must sit well below the old
    # 85-100 pile.
    v_ortanza = turkish_semantic_check.analyze("Ortanza")["turkish_market_verdict"]
    assert v_ortanza["score"] < 68, \
        f"Ortanza TR verdict must be discriminated downward (got {v_ortanza['score']})"


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

def _run():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failures = []
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failures.append((t.__name__, str(e)))
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:  # pragma: no cover
            failures.append((t.__name__, f"ERROR: {e}"))
            print(f"  ERROR {t.__name__}: {e}")
    print("─" * 60)
    print(f"{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    print("brand-maker v2.1 — regression suite (5 audited failure fixtures)")
    print("─" * 60)
    sys.exit(_run())
