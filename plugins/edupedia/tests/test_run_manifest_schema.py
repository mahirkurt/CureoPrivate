import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator


SCHEMA_PATH = Path(__file__).parents[1] / "shared" / "run-manifest-schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft7Validator(SCHEMA)

GATE_IDS = {
    "G-EMOJI",
    "G-CARBON",
    "G-A11Y",
    "G-INTERACT",
    "G-SELFCONTAINED",
    "G-CONTRAST",
    "G-SVG",
    "G-WELLBEING",
    "G-VOICE",
    "G-AUDIO",
    "G-CURRICULUM",
    "G-VERIFY",
    "G-TOKEN",
    "G-FLOW",
    "G-CARBON-GRID",
    "G-EXAM",
}


def valid_manifest():
    return {
        "run_id": "Edupedia-20260817-fen5-hucre-v1",
        "ts": "2026-08-17T12:00:00+03:00",
        "plugin_version": "0.10.0",
        "requested_scope": {
            "command": "modul",
            "mode": "CURRICULUM",
            "outcome_codes": ["FB.5.3.1.1"],
            "subject_slug": "fen-bilimleri-dersi",
            "grade": "5.Sınıf",
            "topic": "hücre",
        },
        "connector_call_ledger": [
            {
                "tool": "search_learning_outcomes",
                "args_summary": "hücre|5.Sınıf|distinct",
                "cache": "miss",
            }
        ],
        "single_shot_enforced": True,
        "canonical_artifacts": {
            "outcomes_extract": {
                "scope_hash": "outcomes_extract:0123456789ab",
                "status": "ok",
            }
        },
        "tier2_status": "unavailable",
        "tier2_note": "tier2_unavailable: tool_absent",
        "quality_gates": {
            gate: {"status": "PASS", "detail": "validator fixture"} for gate in GATE_IDS
        },
        "deliverable_path": "outputs/hucre-fen5.html",
        "caveats": [],
        "metadata": {
            "fixture": "current-valid-manifest",
            "extension": {"producer": "test"},
        },
    }


def assert_valid(manifest):
    errors = sorted(VALIDATOR.iter_errors(manifest), key=lambda error: list(error.path))
    assert not errors, "\n".join(error.message for error in errors)


def assert_invalid(manifest):
    errors = sorted(VALIDATOR.iter_errors(manifest), key=lambda error: list(error.path))
    assert errors, "negative fixture unexpectedly validated"
    return errors


def test_schema_is_well_formed_and_versioned():
    Draft7Validator.check_schema(SCHEMA)
    assert SCHEMA["$id"].endswith("/run-manifest-schema-v2.json")
    assert SCHEMA["x-schema-version"] == "2.0.0"
    assert SCHEMA["x-revised"] == "2026-08-17"


def test_current_manifest_fixture_is_valid():
    assert_valid(valid_manifest())


def test_soru_exam_manifest_is_valid():
    manifest = valid_manifest()
    manifest["requested_scope"]["command"] = "soru"
    manifest["requested_scope"]["mode"] = "EXAM"
    manifest["deliverable_path"] = "outputs/kesir-sorulari.html"
    assert_valid(manifest)


def test_direct_skill_may_select_exam_mode():
    manifest = valid_manifest()
    manifest["requested_scope"]["command"] = "direct-skill"
    manifest["requested_scope"]["mode"] = "EXAM"
    assert_valid(manifest)


@pytest.mark.parametrize("field", ["single_shot_enforced", "deliverable_path"])
def test_missing_new_top_level_required_fields_are_invalid(field):
    manifest = valid_manifest()
    del manifest[field]
    assert_invalid(manifest)


def test_false_single_shot_is_invalid():
    manifest = valid_manifest()
    manifest["single_shot_enforced"] = False
    assert_invalid(manifest)


@pytest.mark.parametrize(
    "path",
    [
        "/tmp/module.html",
        "../module.html",
        "outputs/../../module.html",
        "C:/tmp/module.html",
        "https://example.org/module.html",
        "outputs/module.htm",
        "outputs/module.html\n",
        "outputs/module.html\r",
        "outputs/mod\tule.html",
    ],
)
def test_unsafe_or_non_html_deliverable_paths_are_invalid(path):
    manifest = valid_manifest()
    manifest["deliverable_path"] = path
    assert_invalid(manifest)


def test_missing_quality_gate_is_invalid_when_gate_record_is_present():
    manifest = valid_manifest()
    del manifest["quality_gates"]["G-VOICE"]
    assert_invalid(manifest)


def test_unknown_quality_gate_is_invalid():
    manifest = valid_manifest()
    manifest["quality_gates"]["G-TYPO"] = {"status": "PASS"}
    assert_invalid(manifest)


def test_quality_gate_set_matches_validator_exactly():
    schema_gates = set(SCHEMA["properties"]["quality_gates"]["properties"])
    assert schema_gates == GATE_IDS
    assert set(SCHEMA["properties"]["quality_gates"]["required"]) == GATE_IDS


@pytest.mark.parametrize("status", ["OK", "BLOCK", "", None])
def test_unknown_gate_status_is_invalid(status):
    manifest = valid_manifest()
    manifest["quality_gates"]["G-VERIFY"]["status"] = status
    assert_invalid(manifest)


def test_typo_property_is_invalid_but_extension_metadata_is_allowed():
    manifest = valid_manifest()
    manifest["delivarable_path"] = "outputs/typo.html"
    assert_invalid(manifest)


def test_requested_scope_typo_property_is_invalid():
    manifest = valid_manifest()
    manifest["requested_scope"]["commmand"] = "modul"
    assert_invalid(manifest)


def test_soru_with_non_exam_mode_is_invalid():
    manifest = valid_manifest()
    manifest["requested_scope"]["command"] = "soru"
    manifest["requested_scope"]["mode"] = "MODULE"
    assert_invalid(manifest)


def test_gate_detail_typo_is_invalid():
    manifest = copy.deepcopy(valid_manifest())
    manifest["quality_gates"]["G-VERIFY"]["detial"] = "typo"
    assert_invalid(manifest)


@pytest.mark.parametrize("value", [None, "", "   ", "\n"])
def test_ledger_args_summary_is_required_and_nonempty(value):
    manifest = valid_manifest()
    entry = manifest["connector_call_ledger"][0]
    if value is None:
        del entry["args_summary"]
    else:
        entry["args_summary"] = value
    assert_invalid(manifest)


@pytest.mark.parametrize(
    "scope_hash",
    [
        "",
        "   ",
        "0123456789ab",
        "outcomes_extract:",
        "outcomes_extract:0123456789",
        "unknown_artifact:0123456789ab",
        "outcomes_extract:0123456789aZ",
    ],
)
def test_artifact_scope_hash_is_nonempty_and_patterned(scope_hash):
    manifest = valid_manifest()
    manifest["canonical_artifacts"]["outcomes_extract"]["scope_hash"] = scope_hash
    assert_invalid(manifest)


def test_artifact_scope_hash_prefix_matches_artifact_type():
    manifest = valid_manifest()
    manifest["canonical_artifacts"]["outcomes_extract"]["scope_hash"] = (
        "figure_probe:0123456789ab"
    )
    assert_invalid(manifest)


@pytest.mark.parametrize("caveat", [None, "", "   ", "\n"])
def test_degraded_artifact_requires_nonempty_caveat(caveat):
    manifest = valid_manifest()
    artifact = manifest["canonical_artifacts"]["outcomes_extract"]
    artifact["status"] = "degraded"
    if caveat is not None:
        artifact["caveat"] = caveat
    assert_invalid(manifest)


def test_degraded_artifact_with_caveat_is_valid():
    manifest = valid_manifest()
    artifact = manifest["canonical_artifacts"]["outcomes_extract"]
    artifact["status"] = "degraded"
    artifact["caveat"] = "Maarif connector erişilemedi; kayıtlı kapsam kullanıldı."
    assert_valid(manifest)


@pytest.mark.parametrize("status", ["unavailable", "degraded"])
@pytest.mark.parametrize("note", [None, "", "   ", "\n"])
def test_nonembedded_tier2_states_require_nonempty_note(status, note):
    manifest = valid_manifest()
    manifest["tier2_status"] = status
    if note is None:
        manifest.pop("tier2_note", None)
    else:
        manifest["tier2_note"] = note
    assert_invalid(manifest)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("plugin_version",), "   "),
        (("requested_scope", "outcome_codes", 0), ""),
        (("requested_scope", "subject_slug"), "\n"),
        (("requested_scope", "grade"), " "),
        (("requested_scope", "topic"), "\t"),
        (("quality_gates", "G-VERIFY", "detail"), "   "),
        (("caveats", 0), "\n"),
    ],
)
def test_evidence_strings_cannot_be_blank(path, value):
    manifest = valid_manifest()
    if path[0] == "caveats":
        manifest["caveats"] = [value]
    elif path[0] == "plugin_version":
        manifest["plugin_version"] = value
    elif path[0] == "requested_scope" and path[1] == "outcome_codes":
        manifest["requested_scope"]["outcome_codes"][path[2]] = value
    else:
        target = manifest
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    assert_invalid(manifest)


def test_timestamp_evidence_cannot_be_blank():
    manifest = valid_manifest()
    manifest["ts"] = "   "
    assert_invalid(manifest)
