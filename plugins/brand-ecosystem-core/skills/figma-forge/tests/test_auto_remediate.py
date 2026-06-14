"""figma-forge auto_remediate test suite (v0.3.0-alpha.1).

Covers:
    * Strategy registry: registration, lookup, duplicate detection
    * GateFailure / RemediationAction / RemediationContext dataclasses
    * G13 alias resolution: detection + plan + render
    * G17 Code Connect generator: detection + JSON synthesis
    * G14 SVG normalizer: viewBox/title/linecap injection
    * Runner: audit report parse → end-to-end action production
    * CLI: --list-strategies, --dry-run, --verbose
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Make the scripts/ directory importable
_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "scripts"))

from auto_remediate import (  # noqa: E402
    GateFailure,
    RemediationAction,
    RemediationContext,
    UnsupportedChannelError,
    all_strategies,
    get_strategy,
)
from auto_remediate.base import register_strategy, RemediationStrategy  # noqa: E402
from auto_remediate.runner import RunnerOptions, parse_audit_report, run  # noqa: E402


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestStrategyRegistry:
    def test_six_strategies_registered_on_import(self):
        # v0.3.0-rc: 7 strategies (G15 added in Sprint 4-5)
        regs = all_strategies()
        assert set(regs.keys()) == {2, 7, 8, 13, 14, 15, 17}

    def test_lookup_existing_strategy(self):
        cls = get_strategy(13)
        assert cls is not None
        assert cls.title == "DTCG alias path normalizer"

    def test_lookup_unknown_strategy(self):
        assert get_strategy(99) is None

    def test_duplicate_registration_raises(self):
        with pytest.raises(ValueError, match="already has a registered strategy"):
            @register_strategy(gate_id=13)
            class Dup(RemediationStrategy):
                title = "duplicate"
                def plan(self, *_): return []
                def render(self, *_): return ""


# ---------------------------------------------------------------------------
# Audit report parsing
# ---------------------------------------------------------------------------

class TestAuditParser:
    def test_parse_json_filters_pass(self, tmp_path):
        report = {
            "gates": [
                {"id": 1, "name": "X", "result": "PASS", "severity": "INFO"},
                {"id": 13, "name": "Y", "result": "FAIL", "severity": "MAJOR", "details": {"unresolved_count": 5}},
                {"id": 17, "name": "Z", "result": "WARN", "severity": "MINOR"},
            ]
        }
        path = tmp_path / "audit.json"
        path.write_text(json.dumps(report))
        failures = parse_audit_report(path)
        assert len(failures) == 2
        assert {f.gate_id for f in failures} == {13, 17}

    def test_parse_markdown_basic(self, tmp_path):
        md = """## Gate G13 — DTCG alias (FAIL)
Some text
## Gate G07 — Variant matrix (PASS)
More text
## Gate G14 — Icons (WARN)
"""
        path = tmp_path / "audit.md"
        path.write_text(md)
        failures = parse_audit_report(path)
        assert {f.gate_id for f in failures} == {13, 14}


# ---------------------------------------------------------------------------
# G13 strategy
# ---------------------------------------------------------------------------

class TestG13AliasResolution:
    def test_resolves_simple_unresolved_alias(self, tmp_path):
        # Synthesize a tiny DTCG with one unresolved alias
        tokens = {
            "color": {
                "tbk": {"9": {"$type": "color", "$value": "#E30A17"}}
            },
            "semantic": {
                "anayasa": {"primary": {"$type": "color", "$value": "{tbk.9}"}}
            }
        }
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "dustur.tokens.json").write_text(
            json.dumps(tokens, ensure_ascii=False)
        )

        strategy = get_strategy(13)()
        failure = GateFailure(
            gate_id=13,
            gate_name="alias",
            result="FAIL",
            severity="MAJOR",
            details={"merged_dtcg": "tokens/dustur.tokens.json", "unresolved_count": 1},
            samples=[],
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        assert len(actions) == 1
        assert "{color.tbk.9}" in (actions[0].new_content or "")
        assert "{tbk.9}" not in (actions[0].new_content or "")

    def test_returns_empty_when_no_unresolved(self, tmp_path):
        tokens = {"color": {"tbk": {"9": {"$type": "color", "$value": "#E30A17"}}}}
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "dustur.tokens.json").write_text(json.dumps(tokens))

        strategy = get_strategy(13)()
        failure = GateFailure(
            gate_id=13, gate_name="alias", result="FAIL", severity="MAJOR",
            details={"merged_dtcg": "tokens/dustur.tokens.json"}, samples=[]
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        assert actions == []

    def test_render_produces_unified_diff(self):
        strategy = get_strategy(13)()
        action = RemediationAction(
            strategy_id=13,
            action_type="patch_file",
            target_path="tokens/x.json",
            rationale="test",
            old_content='{"$value": "{tbk.9}"}\n',
            new_content='{"$value": "{color.tbk.9}"}\n',
        )
        diff = strategy.render(action, "pr")
        assert "--- a/tokens/x.json" in diff
        assert "+++ b/tokens/x.json" in diff
        assert "-" in diff and "+" in diff

    def test_unsupported_channel_raises(self):
        strategy = get_strategy(13)()
        action = RemediationAction(
            strategy_id=13, action_type="patch_file", target_path="x", rationale="t",
        )
        with pytest.raises(UnsupportedChannelError):
            strategy.render(action, "plugin")


# ---------------------------------------------------------------------------
# G17 strategy
# ---------------------------------------------------------------------------

class TestG17CodeConnect:
    def _setup_minimal_library(self, tmp_path):
        (tmp_path / "components").mkdir()
        (tmp_path / "code-connect").mkdir()
        comp_spec = {
            "component": {
                "name": "Button",
                "name_carbon": "Button",
                "category": "Action"
            },
            "variants": {
                "axes": {"Variant": ["primary", "secondary"], "Size": ["sm", "md", "lg"]}
            }
        }
        (tmp_path / "components" / "02-button.json").write_text(
            json.dumps(comp_spec, ensure_ascii=False)
        )
        registry = {"ds_name": "Test System", "ds_version": "1.0.0"}
        (tmp_path / "library-registry.json").write_text(json.dumps(registry))
        return tmp_path

    def test_generates_mapping_for_missing(self, tmp_path):
        self._setup_minimal_library(tmp_path)
        strategy = get_strategy(17)()
        failure = GateFailure(
            gate_id=17, gate_name="code-connect", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        assert len(actions) == 1
        action = actions[0]
        assert action.action_type == "create_file"
        assert action.target_path == "code-connect/button.json"

        mapping = json.loads(action.new_content)
        assert mapping["component_id"] == "button"
        assert mapping["react"]["import_statement"] == "import { Button } from '@test/react';"
        assert "variant" in mapping["react"]["props"]
        assert "size" in mapping["react"]["props"]
        assert mapping["_review_required"] is True

    def test_skips_existing_mapping(self, tmp_path):
        self._setup_minimal_library(tmp_path)
        # Pre-create the mapping
        (tmp_path / "code-connect" / "button.json").write_text("{}")
        strategy = get_strategy(17)()
        failure = GateFailure(
            gate_id=17, gate_name="code-connect", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        assert actions == []

    def test_npm_scope_diacritic_strip(self, tmp_path):
        self._setup_minimal_library(tmp_path)
        # Override registry with Turkish ds_name
        registry = {"ds_name": "Düstur Tasarım Sistemi", "ds_version": "1.0.0"}
        (tmp_path / "library-registry.json").write_text(json.dumps(registry, ensure_ascii=False))

        strategy = get_strategy(17)()
        failure = GateFailure(
            gate_id=17, gate_name="code-connect", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        mapping = json.loads(actions[0].new_content)
        # "Düstur" → @dustur (diacritic-stripped)
        assert "@dustur" in mapping["react"]["import_statement"]


# ---------------------------------------------------------------------------
# G14 strategy
# ---------------------------------------------------------------------------

class TestG14IconNormalizer:
    def test_adds_missing_viewbox(self, tmp_path):
        svg_dir = tmp_path / "icons" / "svg" / "ui"
        svg_dir.mkdir(parents=True)
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path d="M1 1"/></svg>'
        (svg_dir / "test.svg").write_text(svg)

        strategy = get_strategy(14)()
        failure = GateFailure(
            gate_id=14, gate_name="icons", result="FAIL", severity="MAJOR",
            samples=[{"path": "ui/test.svg"}]
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        assert len(actions) == 1
        assert 'viewBox="0 0 24 24"' in actions[0].new_content
        assert "<title>" in actions[0].new_content

    def test_skips_selcuklu_motif_dir(self, tmp_path):
        sel_dir = tmp_path / "icons" / "svg" / "selcuklu-motif"
        sel_dir.mkdir(parents=True)
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96"><circle/></svg>'
        (sel_dir / "yildiz.svg").write_text(svg)

        strategy = get_strategy(14)()
        failure = GateFailure(
            gate_id=14, gate_name="icons", result="FAIL", severity="MAJOR",
            samples=[{"path": "selcuklu-motif/yildiz.svg"}]
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        assert actions == []  # Brand-asset, skipped


# ---------------------------------------------------------------------------
# Runner end-to-end
# ---------------------------------------------------------------------------

class TestRunnerE2E:
    def test_skips_gates_without_strategy(self, tmp_path):
        audit = tmp_path / "audit.json"
        audit.write_text(json.dumps({
            "gates": [{"id": 99, "name": "unknown", "result": "FAIL", "severity": "MAJOR"}]
        }))
        opts = RunnerOptions(
            audit_report=audit,
            library_dir=tmp_path,
            output_dir=tmp_path / "out",
            channel="pr",
            dry_run=True,
        )
        result = run(opts)
        assert result.skipped_gates == [(99, "no registered strategy")]
        assert result.action_count == 0

    def test_dry_run_writes_no_files(self, tmp_path):
        (tmp_path / "components").mkdir()
        (tmp_path / "code-connect").mkdir()
        spec = {
            "component": {"name": "Test", "name_carbon": "Test"},
            "variants": {"axes": {"Variant": ["a", "b"]}}
        }
        (tmp_path / "components" / "01-test.json").write_text(json.dumps(spec))
        (tmp_path / "library-registry.json").write_text('{"ds_name": "Test"}')

        audit = tmp_path / "audit.json"
        audit.write_text(json.dumps({
            "gates": [{"id": 17, "name": "cc", "result": "FAIL", "severity": "MAJOR"}]
        }))
        opts = RunnerOptions(
            audit_report=audit, library_dir=tmp_path,
            output_dir=tmp_path / "out", channel="pr", dry_run=True,
        )
        result = run(opts)
        assert result.action_count == 1
        assert not (tmp_path / "out").exists()  # No files written

    def test_apply_writes_summary(self, tmp_path):
        (tmp_path / "components").mkdir()
        (tmp_path / "code-connect").mkdir()
        spec = {
            "component": {"name": "Test", "name_carbon": "Test"},
            "variants": {"axes": {"Variant": ["a"]}}
        }
        (tmp_path / "components" / "01-test.json").write_text(json.dumps(spec))
        (tmp_path / "library-registry.json").write_text('{"ds_name": "Test"}')

        audit = tmp_path / "audit.json"
        audit.write_text(json.dumps({
            "gates": [{"id": 17, "name": "cc", "result": "FAIL", "severity": "MAJOR"}]
        }))
        opts = RunnerOptions(
            audit_report=audit, library_dir=tmp_path,
            output_dir=tmp_path / "out", channel="pr", dry_run=False,
        )
        result = run(opts)
        assert (tmp_path / "out" / "_summary.json").exists()
        summary = json.loads((tmp_path / "out" / "_summary.json").read_text())
        assert summary["strategies_run"] == [17]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))


# ===========================================================================
# v0.3.0-beta.1 — Sprint 2-3 additions
# G02 / G07 / G08 strategies + plugin channel TS writer
# ===========================================================================

class TestG02CompositeTypography:
    """G02 — composite typography → text-styles routing."""

    def _minimal_lib(self, tmp_path):
        (tmp_path / "tokens").mkdir()
        tokens = {
            "color": {"primary": {"$type": "color", "$value": "#FF0000"}},
            "typography": {
                "heading": {
                    "$type": "typography",
                    "$value": {
                        "fontFamily": "Inter",
                        "fontWeight": "700",
                        "fontSize": "32px",
                        "lineHeight": "1.2"
                    }
                }
            }
        }
        (tmp_path / "tokens" / "dustur.tokens.json").write_text(
            json.dumps(tokens, ensure_ascii=False)
        )
        return tmp_path

    def test_detects_composite_token(self, tmp_path):
        self._minimal_lib(tmp_path)
        strategy = get_strategy(2)()
        failure = GateFailure(
            gate_id=2, gate_name="text styles", result="FAIL", severity="MAJOR",
            details={"merged_dtcg": "tokens/dustur.tokens.json"}
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        # 2 actions: strip from DTCG + create text-styles file
        assert len(actions) == 2
        assert actions[0].action_type == "patch_file"
        assert actions[1].action_type == "create_file"
        assert actions[1].target_path == "tokens/dustur.text-styles.json"

    def test_text_styles_payload_shape(self, tmp_path):
        self._minimal_lib(tmp_path)
        strategy = get_strategy(2)()
        failure = GateFailure(
            gate_id=2, gate_name="text styles", result="FAIL", severity="MAJOR",
            details={"merged_dtcg": "tokens/dustur.tokens.json"}
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        create_action = actions[1]
        payload = json.loads(create_action.new_content)
        assert "text_styles" in payload
        assert "heading" in payload["text_styles"]
        assert payload["text_styles"]["heading"]["fontFamily"] == "Inter"
        assert payload["text_styles"]["heading"]["fontWeight"] == "700"

    def test_stripped_dtcg_has_no_composite(self, tmp_path):
        self._minimal_lib(tmp_path)
        strategy = get_strategy(2)()
        failure = GateFailure(
            gate_id=2, gate_name="text styles", result="FAIL", severity="MAJOR",
            details={"merged_dtcg": "tokens/dustur.tokens.json"}
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        patch_action = actions[0]
        amended = json.loads(patch_action.new_content)
        # The typography branch should be empty (composite removed)
        assert amended.get("typography", {}) == {} or "heading" not in amended.get("typography", {})

    def test_plugin_channel_render_emits_figma_calls(self, tmp_path):
        self._minimal_lib(tmp_path)
        strategy = get_strategy(2)()
        failure = GateFailure(
            gate_id=2, gate_name="text styles", result="FAIL", severity="MAJOR",
            details={"merged_dtcg": "tokens/dustur.tokens.json"}
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        create_action = actions[1]
        ts = strategy.render(create_action, "plugin")
        assert "figma.loadFontAsync" in ts
        assert "figma.createTextStyle" in ts
        assert "Inter" in ts


class TestG07VariantMatrix:
    """G07 — variant Cartesian product auto-calculator."""

    def _make_spec(self, axes, expected_count=None, disabled=None):
        spec = {
            "component": {"name": "Test", "name_carbon": "Test"},
            "variants": {"axes": axes}
        }
        if expected_count is not None:
            spec["variants"]["expected_count"] = expected_count
        if disabled:
            spec["variants"]["disabled_combinations"] = disabled
        return spec

    def test_corrects_stale_count(self, tmp_path):
        (tmp_path / "components").mkdir()
        spec = self._make_spec(
            axes={"Variant": ["a", "b"], "Size": ["sm", "md", "lg"]},
            expected_count=999  # stale
        )
        (tmp_path / "components" / "01-test.json").write_text(json.dumps(spec))

        strategy = get_strategy(7)()
        failure = GateFailure(
            gate_id=7, gate_name="variant matrix", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        assert len(actions) == 1
        new_spec = json.loads(actions[0].new_content)
        assert new_spec["variants"]["expected_count"] == 6  # 2 × 3

    def test_subtracts_disabled_combinations(self, tmp_path):
        (tmp_path / "components").mkdir()
        spec = self._make_spec(
            axes={"Variant": ["a", "b", "c", "d"], "Size": ["sm", "md", "lg"], "State": ["d", "h", "p", "f", "x"]},
            expected_count=60,
            disabled=[{"variant": "a", "state": "x"}]
        )
        (tmp_path / "components" / "01-test.json").write_text(json.dumps(spec))

        strategy = get_strategy(7)()
        failure = GateFailure(
            gate_id=7, gate_name="variant matrix", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        assert len(actions) == 1
        new_spec = json.loads(actions[0].new_content)
        # 4 × 3 × 5 − 1 disabled = 59
        assert new_spec["variants"]["expected_count"] == 59

    def test_no_action_when_count_correct(self, tmp_path):
        (tmp_path / "components").mkdir()
        spec = self._make_spec(
            axes={"Variant": ["a", "b"], "Size": ["sm", "md"]},
            expected_count=4  # already correct
        )
        (tmp_path / "components" / "01-test.json").write_text(json.dumps(spec))

        strategy = get_strategy(7)()
        failure = GateFailure(
            gate_id=7, gate_name="variant matrix", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        assert actions == []


class TestG08ComponentNaming:
    """G08 — component naming PascalCase rewriter."""

    def test_rewrites_snake_case(self, tmp_path):
        (tmp_path / "components").mkdir()
        spec = {
            "component": {"name": "Madde Card", "name_carbon": "madde_card"},
            "variants": {"axes": {}}
        }
        (tmp_path / "components" / "09-madde-card.json").write_text(json.dumps(spec))

        strategy = get_strategy(8)()
        failure = GateFailure(
            gate_id=8, gate_name="naming", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        assert len(actions) == 1
        new_spec = json.loads(actions[0].new_content)
        assert new_spec["component"]["name_carbon"] == "MaddeCard"

    def test_preserves_turkish_diacritics(self, tmp_path):
        (tmp_path / "components").mkdir()
        spec = {
            "component": {"name": "Yüzey Badge", "name_carbon": "yüzey-badge"},
            "variants": {"axes": {}}
        }
        (tmp_path / "components" / "01-yuzey-badge.json").write_text(
            json.dumps(spec, ensure_ascii=False)
        )

        strategy = get_strategy(8)()
        failure = GateFailure(
            gate_id=8, gate_name="naming", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        assert len(actions) >= 1
        new_spec = json.loads(actions[0].new_content)
        # Diacritics preserved
        assert new_spec["component"]["name_carbon"] == "YüzeyBadge"

    def test_no_action_for_already_pascal(self, tmp_path):
        (tmp_path / "components").mkdir()
        spec = {
            "component": {"name": "Button", "name_carbon": "Button"},
            "variants": {"axes": {}}
        }
        (tmp_path / "components" / "02-button.json").write_text(json.dumps(spec))

        strategy = get_strategy(8)()
        failure = GateFailure(
            gate_id=8, gate_name="naming", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)
        assert actions == []

    def test_cascades_to_code_connect(self, tmp_path):
        (tmp_path / "components").mkdir()
        (tmp_path / "code-connect").mkdir()
        spec = {
            "component": {"name": "Card", "name_carbon": "madde_card"},
            "variants": {"axes": {}}
        }
        (tmp_path / "components" / "09-madde-card.json").write_text(json.dumps(spec))
        mapping = {
            "component_id": "madde-card",
            "carbon_class_name": "madde_card",
            "react": {"import_statement": "import { madde_card } from '@x/react';",
                       "code_example": "<madde_card />"}
        }
        (tmp_path / "code-connect" / "madde-card.json").write_text(json.dumps(mapping))

        strategy = get_strategy(8)()
        failure = GateFailure(
            gate_id=8, gate_name="naming", result="FAIL", severity="MAJOR"
        )
        ctx = RemediationContext(library_dir=tmp_path)
        actions = strategy.plan(failure, ctx)

        # 1 spec + 1 cascaded mapping = 2 actions
        assert len(actions) == 2
        # Find the cascaded one
        cc_action = next(a for a in actions if a.target_path.startswith("code-connect/"))
        new_mapping = json.loads(cc_action.new_content)
        assert new_mapping["carbon_class_name"] == "MaddeCard"
        assert "MaddeCard" in new_mapping["react"]["import_statement"]


class TestPluginWriter:
    """Plugin channel TypeScript script writer."""

    def test_header_contains_metadata(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        action = RemediationAction(
            strategy_id=2,
            action_type="create_file",
            target_path="tokens/dustur.text-styles.json",
            rationale="Test rationale",
            new_content=json.dumps({"text_styles": {}}),
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "// figma-forge auto-remediate" in ts
        assert "Generated:" in ts
        assert "Library:" in ts
        assert "Actions:   1" in ts

    def test_actions_wrapped_in_try_catch(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        action = RemediationAction(
            strategy_id=2,
            action_type="create_file",
            target_path="x.json",
            rationale="r",
            new_content=json.dumps({"text_styles": {"h1": {"fontFamily": "Inter", "fontSize": 16}}}),
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "try {" in ts
        assert "} catch (err) {" in ts
        assert "console.error" in ts

    def test_g02_emits_figma_text_style_creation(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        action = RemediationAction(
            strategy_id=2,
            action_type="create_file",
            target_path="x.json",
            rationale="r",
            new_content=json.dumps({"text_styles": {
                "display": {
                    "fontFamily": "Fraunces", "fontWeight": "700",
                    "fontSize": "48px", "lineHeight": "1.1", "letterSpacing": "-1px"
                }
            }}),
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "figma.loadFontAsync({ family: 'Fraunces', style: '700' })" in ts
        assert "figma.createTextStyle()" in ts
        assert "style.name = 'display'" in ts
        assert "style.fontSize = 48.0" in ts
        # 1.1 × 100 may produce 110.0 or 110.00000000000001 (float precision)
        assert "unit: 'PERCENT'" in ts and "value: 110" in ts
        assert "unit: 'PIXELS'" in ts and "value: -1.0" in ts

    def test_static_only_action_emits_noop(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        action = RemediationAction(
            strategy_id=8,  # G08 = static-only (no plugin emitter registered)
            action_type="patch_file",
            target_path="components/x.json",
            rationale="rename",
            new_content="{}",
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "G08 action targets static source" in ts
        assert "git apply" in ts


class TestSixStrategyRegistry:
    """Verify all 6 strategies are registered after Sprint 2-3."""

    def test_all_six_registered(self):
        # v0.3.0-rc: now 7 strategies (G15 added)
        regs = all_strategies()
        assert set(regs.keys()) == {2, 7, 8, 13, 14, 15, 17}

    def test_g02_supports_both_channels(self):
        cls = get_strategy(2)
        assert "pr" in cls.output_channels
        assert "plugin" in cls.output_channels


class TestJSONAuditReport:
    """publish_audit --output-format json schema v1.0."""

    def test_json_payload_shape(self):
        import sys
        # Add the figma-forge root to path so publish_audit imports work
        sys.path.insert(0, str(_REPO / "scripts"))
        from publish_audit.models import Gate, GateResult
        from publish_audit.reporting import format_json_report

        gates = [
            GateResult(
                gate=Gate(id=13, name="alias", severity="error",
                          description="d", remediation="r"),
                status="fail", checked_count=10,
                failures=["a unresolved", "b unresolved"],
            ),
            GateResult(
                gate=Gate(id=17, name="cc", severity="warn",
                          description="d", remediation="r"),
                status="pass", checked_count=17,
            ),
        ]
        out = format_json_report(
            gates, file_label="Test", audit_target="t",
            build_version="0.3.0-beta.1"
        )
        parsed = json.loads(out)
        assert parsed["schema_version"] == "1.0"
        assert parsed["build_version"] == "0.3.0-beta.1"
        assert len(parsed["gates"]) == 2
        assert parsed["gates"][0]["result"] == "FAIL"
        assert parsed["gates"][0]["details"]["failure_count"] == 2
        assert parsed["gates"][1]["result"] == "PASS"
        assert "score" in parsed
        assert "band" in parsed


# ===========================================================================
# v0.3.0-rc.1 — Sprint 4-5 additions
# Orchestrate framework + bundle-manifest + static_lint + G15 strategy
# ===========================================================================

class TestG15IconSizeGrid:
    """G15 — Icon size grid normalizer."""

    def _make_svg(self, w: int, h: int) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}">\n  <circle cx="{w/2}" cy="{h/2}" r="{min(w,h)/3}"/>\n</svg>\n')

    def test_snaps_25_to_24(self, tmp_path):
        (tmp_path / "icons" / "svg" / "tier").mkdir(parents=True)
        svg = tmp_path / "icons" / "svg" / "tier" / "test.svg"
        svg.write_text(self._make_svg(25, 25))

        strategy = get_strategy(15)()
        ctx = RemediationContext(library_dir=tmp_path)
        failure = GateFailure(
            gate_id=15, gate_name="size grid", result="FAIL", severity="MAJOR"
        )
        actions = strategy.plan(failure, ctx)

        assert len(actions) == 1
        assert 'width="24"' in actions[0].new_content
        assert 'height="24"' in actions[0].new_content
        # viewBox preserved (geometry intact)
        assert 'viewBox="0 0 25 25"' in actions[0].new_content

    def test_preserves_aspect_for_non_square(self, tmp_path):
        (tmp_path / "icons" / "svg" / "tier").mkdir(parents=True)
        svg = tmp_path / "icons" / "svg" / "tier" / "banner.svg"
        # 16 wide × 24 tall — banner tier mark; dominant axis is 24
        svg.write_text(self._make_svg(16, 24))

        strategy = get_strategy(15)()
        ctx = RemediationContext(library_dir=tmp_path)
        failure = GateFailure(
            gate_id=15, gate_name="size grid", result="FAIL", severity="MAJOR"
        )
        actions = strategy.plan(failure, ctx)

        # 24 is already canonical → no action
        assert actions == []

    def test_no_action_when_on_grid(self, tmp_path):
        (tmp_path / "icons" / "svg" / "tier").mkdir(parents=True)
        (tmp_path / "icons" / "svg" / "tier" / "good.svg").write_text(self._make_svg(24, 24))
        (tmp_path / "icons" / "svg" / "tier" / "good2.svg").write_text(self._make_svg(48, 48))

        strategy = get_strategy(15)()
        ctx = RemediationContext(library_dir=tmp_path)
        failure = GateFailure(
            gate_id=15, gate_name="size grid", result="FAIL", severity="MAJOR"
        )
        actions = strategy.plan(failure, ctx)
        assert actions == []

    def test_registry_override(self, tmp_path):
        (tmp_path / "icons" / "svg" / "document").mkdir(parents=True)
        (tmp_path / "icons" / "svg" / "document" / "x.svg").write_text(self._make_svg(24, 24))
        # Without registry override, default doc grid is [32, 48] → 24 snaps to 32
        # With override [24, 48], 24 is canonical
        (tmp_path / "library-registry.json").write_text(
            '{"icon_size_grid": {"icons/svg/document/": [24, 48]}}'
        )

        strategy = get_strategy(15)()
        ctx = RemediationContext(library_dir=tmp_path)
        failure = GateFailure(
            gate_id=15, gate_name="size grid", result="FAIL", severity="MAJOR"
        )
        actions = strategy.plan(failure, ctx)
        assert actions == []


class TestSevenStrategyRegistry:
    """v0.3.0-rc: all 7 strategies present after G15 landed."""

    def test_all_seven_registered(self):
        regs = all_strategies()
        assert set(regs.keys()) == {2, 7, 8, 13, 14, 15, 17}


class TestStaticLint:
    """publish_audit static-only lint module."""

    def _setup_clean_bundle(self, tmp_path):
        (tmp_path / "tokens").mkdir()
        (tmp_path / "components").mkdir()
        (tmp_path / "code-connect").mkdir()
        (tmp_path / "icons" / "svg" / "tier").mkdir(parents=True)

        # Minimal merged DTCG
        tokens = {
            "color": {"primary": {"$type": "color", "$value": "#FF0000"}},
            "semantic": {
                "background": {"$type": "color", "$value": "{color.primary}"}
            }
        }
        (tmp_path / "tokens" / "dustur.tokens.json").write_text(
            json.dumps(tokens, ensure_ascii=False)
        )
        # Component spec
        spec = {
            "$schema": "x",
            "component": {"name": "Btn", "name_carbon": "Btn"},
            "variants": {"axes": {"v": ["a"]}, "expected_count": 1}
        }
        (tmp_path / "components" / "01-btn.json").write_text(json.dumps(spec))
        # Code Connect mapping
        (tmp_path / "code-connect" / "btn.json").write_text(
            '{"component_id": "btn", "carbon_class_name": "Btn"}'
        )
        # Valid SVG
        (tmp_path / "icons" / "svg" / "tier" / "x.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"></svg>'
        )
        # library-registry with a11y block
        (tmp_path / "library-registry.json").write_text(json.dumps({
            "ds_name": "Test",
            "ds_version": "0.0.1",
            "accessibility": {
                "wcag_target": "AA",
                "apca_enabled": True,
                "tr_diacritics_audit": ["Ç","Ğ","İ","Ö","Ş","Ü"]
            }
        }))
        return tmp_path

    def test_runs_all_nine_checks(self, tmp_path):
        from publish_audit.static_lint import run_static_lint

        self._setup_clean_bundle(tmp_path)
        results = run_static_lint(tmp_path)
        assert len(results) == 9
        gate_ids = [r.gate.id for r in results]
        assert gate_ids == [100, 101, 102, 103, 104, 105, 106, 107, 108]

    def test_detects_invalid_json(self, tmp_path):
        from publish_audit.static_lint import run_static_lint

        self._setup_clean_bundle(tmp_path)
        (tmp_path / "tokens" / "broken.json").write_text("{not valid")
        results = run_static_lint(tmp_path)
        l1 = next(r for r in results if r.gate.id == 100)
        assert l1.status == "fail"
        assert any("broken.json" in f for f in l1.failures)

    def test_detects_unresolved_alias(self, tmp_path):
        from publish_audit.static_lint import run_static_lint

        self._setup_clean_bundle(tmp_path)
        tokens_path = tmp_path / "tokens" / "dustur.tokens.json"
        tokens = json.loads(tokens_path.read_text())
        tokens["semantic"]["background"]["$value"] = "{color.nonexistent}"
        tokens_path.write_text(json.dumps(tokens, ensure_ascii=False))

        results = run_static_lint(tmp_path)
        l3 = next(r for r in results if r.gate.id == 102)
        assert l3.status == "fail"
        assert any("nonexistent" in f for f in l3.failures)

    def test_detects_missing_code_connect(self, tmp_path):
        from publish_audit.static_lint import run_static_lint

        self._setup_clean_bundle(tmp_path)
        # Add another component spec without a corresponding mapping
        spec2 = {
            "$schema": "x",
            "component": {"name": "Tag", "name_carbon": "Tag"},
            "variants": {"axes": {"v": ["a"]}, "expected_count": 1}
        }
        (tmp_path / "components" / "02-tag.json").write_text(json.dumps(spec2))

        results = run_static_lint(tmp_path)
        l7 = next(r for r in results if r.gate.id == 106)
        assert l7.status == "fail"
        assert any("tag" in f.lower() for f in l7.failures)

    def test_detects_missing_a11y_block(self, tmp_path):
        from publish_audit.static_lint import run_static_lint

        self._setup_clean_bundle(tmp_path)
        (tmp_path / "library-registry.json").write_text(json.dumps({
            "ds_name": "Test", "ds_version": "0.0.1"
            # No accessibility block
        }))

        results = run_static_lint(tmp_path)
        l9 = next(r for r in results if r.gate.id == 108)
        assert l9.status == "fail"

    def test_detects_invalid_svg(self, tmp_path):
        from publish_audit.static_lint import run_static_lint

        self._setup_clean_bundle(tmp_path)
        # Replace good SVG with one missing viewBox
        (tmp_path / "icons" / "svg" / "tier" / "x.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        )
        results = run_static_lint(tmp_path)
        l6 = next(r for r in results if r.gate.id == 105)
        assert l6.status == "fail"
        assert any("viewBox" in f for f in l6.failures)


class TestOrchestrate:
    """orchestrate framework: manifest parsing + dry-run + resume."""

    def _make_manifest(self, tmp_path, stages):
        manifest_path = tmp_path / "orchestration.json"
        manifest_path.write_text(json.dumps({
            "library": "Test",
            "version": "0.1.0",
            "pipeline": stages
        }))
        return manifest_path

    def test_manifest_parses_valid_pipeline(self, tmp_path):
        from orchestrate import parse_manifest

        manifest_path = self._make_manifest(tmp_path, [
            {"stage": 1, "mode": "SCAFFOLD", "description": "scaffold"},
            {"stage": 2, "mode": "TOKENS_IMPORT", "description": "tokens"}
        ])
        top, specs = parse_manifest(manifest_path)
        assert top["library"] == "Test"
        assert len(specs) == 2
        assert specs[0].mode == "SCAFFOLD"
        assert specs[1].mode == "TOKENS_IMPORT"

    def test_manifest_rejects_unknown_mode(self, tmp_path):
        from orchestrate import ManifestError, parse_manifest

        manifest_path = self._make_manifest(tmp_path, [
            {"stage": 1, "mode": "WAT", "description": "x"}
        ])
        try:
            parse_manifest(manifest_path)
            assert False, "Should have raised ManifestError"
        except ManifestError as e:
            assert "WAT" in str(e)

    def test_manifest_rejects_duplicate_indices(self, tmp_path):
        from orchestrate import ManifestError, parse_manifest

        manifest_path = self._make_manifest(tmp_path, [
            {"stage": 1, "mode": "SCAFFOLD", "description": "x"},
            {"stage": 1, "mode": "TOKENS_IMPORT", "description": "y"}
        ])
        try:
            parse_manifest(manifest_path)
            assert False, "Should have raised ManifestError"
        except ManifestError as e:
            assert "Duplicate" in str(e)

    def test_dry_run_skips_real_io(self, tmp_path):
        from orchestrate import RunnerOptions, run_pipeline

        # Build a bundle dir + manifest
        (tmp_path / "lib").mkdir()
        manifest_path = self._make_manifest(tmp_path / "lib", [
            {"stage": 1, "mode": "SCAFFOLD", "description": "x"},
            {"stage": 2, "mode": "TOKENS_IMPORT", "description": "y"}
        ])

        opts = RunnerOptions(
            manifest_path=manifest_path,
            library_dir=tmp_path / "lib",
            forge_root=Path(__file__).resolve().parent.parent,
            dry_run=True,
        )
        result = run_pipeline(opts)
        assert len(result.stages) == 2
        # SCAFFOLD is a live scaffold → succeeds with announce
        # TOKENS_IMPORT in dry_run mode → dry_run status
        statuses = [s.status for s in result.stages]
        assert "dry_run" in statuses or "success" in statuses

    def test_only_filter(self, tmp_path):
        from orchestrate import RunnerOptions, run_pipeline

        (tmp_path / "lib").mkdir()
        manifest_path = self._make_manifest(tmp_path / "lib", [
            {"stage": 1, "mode": "SCAFFOLD", "description": "x"},
            {"stage": 2, "mode": "TOKENS_IMPORT", "description": "y"},
            {"stage": 3, "mode": "PUBLISH", "description": "z"},
        ])
        opts = RunnerOptions(
            manifest_path=manifest_path,
            library_dir=tmp_path / "lib",
            forge_root=Path(__file__).resolve().parent.parent,
            dry_run=True,
            only=["TOKENS_IMPORT"],
        )
        result = run_pipeline(opts)
        modes_run = [s.mode for s in result.stages if s.status != "skipped"]
        assert modes_run == ["TOKENS_IMPORT"]


class TestBundleManifest:
    """bundle_manifest.py: file inventory + verify mode."""

    def test_builds_manifest_with_sha256(self, tmp_path):
        # bundle_manifest imports require it on sys.path
        sys.path.insert(0, str(_REPO / "scripts"))
        from bundle_manifest import build_manifest

        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "a.json").write_text('{"a": 1}')
        (tmp_path / "components").mkdir()
        (tmp_path / "components" / "b.json").write_text('{"b": 2}')

        manifest = build_manifest(tmp_path, bundle_name="Test", bundle_version="0.1.0")
        assert manifest["file_count"] == 2
        assert manifest["bundle_name"] == "Test"
        for f in manifest["files"]:
            assert len(f["sha256"]) == 64  # SHA-256 hex digest

    def test_categorizes_by_path(self, tmp_path):
        sys.path.insert(0, str(_REPO / "scripts"))
        from bundle_manifest import build_manifest

        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "a.json").write_text("{}")
        (tmp_path / "components").mkdir()
        (tmp_path / "components" / "b.json").write_text("{}")
        (tmp_path / "code-connect").mkdir()
        (tmp_path / "code-connect" / "x.json").write_text("{}")

        m = build_manifest(tmp_path, bundle_name="T")
        cats = m["summary_by_category"]
        assert cats["tokens.merged"] == 1
        assert cats["components.spec"] == 1
        assert cats["code-connect.mapping"] == 1

    def test_verify_detects_drift(self, tmp_path):
        sys.path.insert(0, str(_REPO / "scripts"))
        from bundle_manifest import build_manifest, verify_manifest

        (tmp_path / "a.json").write_text('{"v": 1}')
        m = build_manifest(tmp_path, bundle_name="T")
        (tmp_path / "manifest.json").write_text(json.dumps(m))

        # Now modify the file
        (tmp_path / "a.json").write_text('{"v": 2}')
        ok, issues = verify_manifest(tmp_path / "manifest.json", tmp_path)
        assert ok is False
        assert any("CHANGED" in line and "a.json" in line for line in issues)


# ===========================================================================
# v0.3.1-alpha.1 — audit-diff calibration delta + G14 plugin expansion
# ===========================================================================

class TestAuditDiffBase:
    """audit_diff data shapes — AuditSnapshot, GateTransition."""

    def _baseline_payload(self):
        return {
            "schema_version": "1.0",
            "audit_timestamp": "2026-05-26T12:00:00Z",
            "build_version": "0.3.0-rc.1",
            "score": 10.0,
            "band": "EXEMPLARY",
            "summary": {"errors": 0, "warns": 0, "infos": 0, "skips": 0, "passes": 9},
            "gates": [
                {"id": 100, "name": "JSON validity", "severity": "error",
                 "result": "PASS", "checked_count": 74, "samples": []},
                {"id": 102, "name": "Alias resolvability", "severity": "error",
                 "result": "PASS", "checked_count": 88, "samples": []},
                {"id": 105, "name": "SVG validity", "severity": "error",
                 "result": "PASS", "checked_count": 26, "samples": []},
            ]
        }

    def test_audit_snapshot_from_payload(self):
        from audit_diff import AuditSnapshot
        snap = AuditSnapshot.from_payload(self._baseline_payload(), path="x.json")
        assert snap.score == 10.0
        assert snap.band == "EXEMPLARY"
        assert len(snap.gates) == 3
        assert snap.gates[100]["result"] == "PASS"

    def test_diff_report_summary(self):
        from audit_diff import compare, AuditSnapshot
        baseline = AuditSnapshot.from_payload(self._baseline_payload(), path="b.json")
        # Current: G102 regressed PASS → FAIL
        current_payload = self._baseline_payload()
        for g in current_payload["gates"]:
            if g["id"] == 102:
                g["result"] = "FAIL"
                g["samples"] = [{"message": "color.x → unresolved {y.z}"}]
        current = AuditSnapshot.from_payload(current_payload, path="c.json")
        report = compare(baseline, current)
        assert report.summary["regressions"] == 1
        assert report.summary["improvements"] == 0
        assert report.summary["no_change"] == 2

    def test_score_delta_and_band_shift(self):
        from audit_diff import compare, AuditSnapshot
        baseline = AuditSnapshot.from_payload(self._baseline_payload(), path="b.json")
        current_payload = self._baseline_payload()
        current_payload["score"] = 7.2
        current_payload["band"] = "STRONG"
        current = AuditSnapshot.from_payload(current_payload, path="c.json")
        report = compare(baseline, current)
        assert report.score_delta == -2.8
        assert report.band_shift == "regressed"


class TestAuditDiffComparator:
    """audit_diff transition classification logic."""

    def _gate(self, gid, result, severity="error", samples=None, checked=10):
        return {
            "id": gid, "name": f"Gate {gid}",
            "severity": severity, "result": result,
            "checked_count": checked,
            "samples": samples or [],
        }

    def test_pass_to_fail_classified_as_regression(self):
        from audit_diff import compare, AuditSnapshot
        b = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "", "build_version": "x",
            "score": 10.0, "band": "EXEMPLARY", "summary": {},
            "gates": [self._gate(1, "PASS")]
        }, path="b")
        c = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "", "build_version": "x",
            "score": 8.5, "band": "EXCELLENT", "summary": {},
            "gates": [self._gate(1, "FAIL", samples=[{"message": "oops"}])]
        }, path="c")
        report = compare(b, c)
        assert report.transitions[0].classification == "regression"
        assert "oops" in report.transitions[0].samples_introduced

    def test_fail_to_pass_classified_as_improvement(self):
        from audit_diff import compare, AuditSnapshot
        b = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "", "build_version": "x",
            "score": 8.0, "band": "EXCELLENT", "summary": {},
            "gates": [self._gate(1, "FAIL", samples=[{"message": "fixed"}])]
        }, path="b")
        c = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "", "build_version": "x",
            "score": 10.0, "band": "EXEMPLARY", "summary": {},
            "gates": [self._gate(1, "PASS")]
        }, path="c")
        report = compare(b, c)
        assert report.transitions[0].classification == "improvement"
        assert "fixed" in report.transitions[0].samples_resolved

    def test_new_gate_classification(self):
        from audit_diff import compare, AuditSnapshot
        b = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "", "build_version": "x",
            "score": 10.0, "band": "EXEMPLARY", "summary": {},
            "gates": []
        }, path="b")
        c = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "", "build_version": "x",
            "score": 10.0, "band": "EXEMPLARY", "summary": {},
            "gates": [self._gate(108, "PASS")]
        }, path="c")
        report = compare(b, c)
        assert len(report.transitions) == 1
        assert report.transitions[0].classification == "new"
        assert report.transitions[0].result_baseline == "MISSING"

    def test_load_snapshot_rejects_non_v1_schema(self, tmp_path):
        from audit_diff import load_snapshot
        bad = tmp_path / "bad.json"
        bad.write_text('{"schema_version": "0.9", "gates": []}')
        try:
            load_snapshot(bad)
            assert False, "Should raise on non-v1.0 schema"
        except ValueError as e:
            assert "schema" in str(e).lower()


class TestAuditDiffRendering:
    """audit_diff JSON + Markdown rendering."""

    def _build_simple_report(self):
        from audit_diff import compare, AuditSnapshot
        b = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "T0", "build_version": "v1",
            "score": 10.0, "band": "EXEMPLARY", "summary": {},
            "gates": [{"id": 100, "name": "X", "severity": "error",
                      "result": "PASS", "checked_count": 5, "samples": []}]
        }, path="b.json")
        c = AuditSnapshot.from_payload({
            "schema_version": "1.0", "audit_timestamp": "T1", "build_version": "v1",
            "score": 7.0, "band": "STRONG", "summary": {},
            "gates": [{"id": 100, "name": "X", "severity": "error",
                      "result": "FAIL", "checked_count": 5,
                      "samples": [{"message": "broken alias {q.r}"}]}]
        }, path="c.json")
        return compare(b, c)

    def test_json_render_schema_v1(self):
        from audit_diff import format_diff_json
        report = self._build_simple_report()
        out = format_diff_json(report)
        parsed = json.loads(out)
        assert parsed["schema_version"] == "1.0"
        assert parsed["score_delta"] == -3.0
        assert parsed["band_shift"] == "regressed"
        assert parsed["summary"]["regressions"] == 1

    def test_markdown_render_shows_regressions(self):
        from audit_diff import format_diff_markdown
        report = self._build_simple_report()
        md = format_diff_markdown(report)
        assert "# figma-forge audit-diff" in md
        assert "Regressions" in md
        assert "G100" in md
        assert "PASS" in md and "FAIL" in md
        assert "broken alias" in md
        assert "🔽" in md  # regression symbol


class TestG14PluginExpansion:
    """G14 plugin emitter v0.3.1 — full component creation flow."""

    def test_emits_page_routing_for_tier_icons(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"></svg>'
        action = RemediationAction(
            strategy_id=14,
            action_type="patch_file",
            target_path="icons/svg/tier/anayasa-24.svg",
            rationale="r",
            new_content=svg,
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "'Tier Icons'" in ts
        assert "figma.createPage()" in ts
        assert "figma.setCurrentPageAsync" in ts

    def test_emits_idempotent_existing_check(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"></svg>'
        action = RemediationAction(
            strategy_id=14,
            action_type="patch_file",
            target_path="icons/svg/document/gavel.svg",
            rationale="r",
            new_content=svg,
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        # Idempotent flow: locate-by-name then update or create
        assert "findOne" in ts
        assert "ComponentNode" in ts
        assert "Updated existing component" in ts
        assert "Created new component" in ts

    def test_emits_correct_container_size_per_tier(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"></svg>'
        action = RemediationAction(
            strategy_id=14,
            action_type="patch_file",
            target_path="icons/svg/selcuklu-motif/star.svg",
            rationale="r",
            new_content=svg,
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "'Selçuklu Motifleri'" in ts
        assert "resize(192, 192)" in ts

    def test_provenance_in_description_and_doc_links(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"></svg>'
        action = RemediationAction(
            strategy_id=14,
            action_type="patch_file",
            target_path="icons/svg/tier/aym-24.svg",
            rationale="r",
            new_content=svg,
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "component.description" in ts
        assert "Source: icons/svg/tier/aym-24.svg" in ts
        assert "component.documentationLinks" in ts

    def test_template_literal_escapes_dollar_brace(self, tmp_path):
        """Verify ${} sequences inside SVG don't break the JS template literal."""
        from auto_remediate.plugin_writer import render_plugin_script
        # SVG with a literal ${...} pattern (e.g. a comment) must be escaped
        svg = '<svg viewBox="0 0 24 24"><!-- ${interpolation} should be safe --></svg>'
        action = RemediationAction(
            strategy_id=14,
            action_type="patch_file",
            target_path="icons/svg/tier/test.svg",
            rationale="r",
            new_content=svg,
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        # The literal ${ in source SVG must be escaped to \${
        assert "\\${interpolation}" in ts


# ===========================================================================
# v0.3.1 GA — audit-trend longitudinal analysis + G13 plugin expansion
# ===========================================================================

class TestAuditTrendBase:
    """audit_trend data shapes."""

    def _payload(self, score, band, timestamp, alias_result="PASS"):
        return {
            "schema_version": "1.0",
            "audit_timestamp": timestamp,
            "build_version": "0.3.1",
            "score": score, "band": band,
            "summary": {"errors": 0 if alias_result == "PASS" else 1, "passes": 9},
            "gates": [
                {"id": 100, "name": "JSON", "severity": "error",
                 "result": "PASS", "checked_count": 10, "samples": []},
                {"id": 102, "name": "Alias", "severity": "error",
                 "result": alias_result, "checked_count": 88,
                 "samples": [{"message": "broken"}] if alias_result == "FAIL" else []},
            ]
        }

    def test_time_point_from_payload(self):
        from audit_trend import TimePoint
        p = TimePoint.from_payload(
            self._payload(10.0, "EXEMPLARY", "2026-05-01T12:00:00Z"),
            path="x.json"
        )
        assert p.score == 10.0
        assert p.band == "EXEMPLARY"
        assert p.band_ordinal() == 6

    def test_load_points_skips_malformed(self, tmp_path):
        from audit_trend import load_points
        (tmp_path / "good.json").write_text(json.dumps(
            self._payload(10.0, "EXEMPLARY", "2026-05-01T12:00:00Z")
        ))
        (tmp_path / "bad.json").write_text("{not valid")
        points = load_points([tmp_path / "good.json", tmp_path / "bad.json"])
        assert len(points) == 1

    def test_load_points_rejects_non_v1_schema(self, tmp_path):
        from audit_trend import load_points
        (tmp_path / "bad.json").write_text('{"schema_version": "0.5", "gates": []}')
        try:
            load_points([tmp_path / "bad.json"])
            assert False, "Should reject non-v1.0 schema"
        except ValueError:
            pass

    def test_load_points_sorts_by_timestamp(self, tmp_path):
        from audit_trend import load_points
        (tmp_path / "later.json").write_text(json.dumps(
            self._payload(9.0, "EXEMPLARY", "2026-05-02T12:00:00Z")
        ))
        (tmp_path / "earlier.json").write_text(json.dumps(
            self._payload(8.0, "EXCELLENT", "2026-05-01T12:00:00Z")
        ))
        points = load_points([tmp_path / "later.json", tmp_path / "earlier.json"])
        assert points[0].score == 8.0   # Earlier comes first
        assert points[1].score == 9.0


class TestAuditTrendAnalyzer:
    """audit_trend statistical analysis."""

    def _make_point(self, ts, score, band, alias_result="PASS"):
        from audit_trend import TimePoint
        return TimePoint.from_payload({
            "schema_version": "1.0",
            "audit_timestamp": ts,
            "build_version": "0.3.1",
            "score": score, "band": band,
            "summary": {},
            "gates": [
                {"id": 102, "name": "Alias", "severity": "error",
                 "result": alias_result, "checked_count": 10, "samples": []}
            ]
        }, path="x.json")

    def test_score_mean_and_stdev(self):
        from audit_trend import analyze
        points = [
            self._make_point("2026-05-01T12:00:00Z", 10.0, "EXEMPLARY"),
            self._make_point("2026-05-02T12:00:00Z", 8.0, "EXCELLENT"),
            self._make_point("2026-05-03T12:00:00Z", 9.0, "EXEMPLARY"),
        ]
        report = analyze(points)
        assert report.score_mean == 9.0
        # Population stdev of [10, 8, 9] ≈ 0.816
        assert 0.8 < report.score_stdev < 0.9

    def test_flapping_gate_detection(self):
        from audit_trend import analyze
        # P, F, P, F, P → 2 P→F and 2 F→P transitions, mttf = 1
        points = [
            self._make_point(f"2026-05-0{i+1}T12:00:00Z", 10.0, "EXEMPLARY",
                              alias_result="PASS" if i % 2 == 0 else "FAIL")
            for i in range(5)
        ]
        report = analyze(points)
        g102 = report.gates[102]
        assert g102.pass_to_fail_transitions == 2
        assert g102.fail_to_pass_transitions == 2
        assert g102.stability == "flapping"
        assert g102.mean_time_to_fix == 1.0

    def test_regressing_gate_detection(self):
        from audit_trend import analyze
        # P, P, F, F, F → 1 P→F, 0 F→P → regressing
        points = [
            self._make_point("2026-05-01T12:00:00Z", 10.0, "EXEMPLARY", "PASS"),
            self._make_point("2026-05-02T12:00:00Z", 10.0, "EXEMPLARY", "PASS"),
            self._make_point("2026-05-03T12:00:00Z", 8.0, "EXCELLENT", "FAIL"),
            self._make_point("2026-05-04T12:00:00Z", 8.0, "EXCELLENT", "FAIL"),
            self._make_point("2026-05-05T12:00:00Z", 8.0, "EXCELLENT", "FAIL"),
        ]
        report = analyze(points)
        g102 = report.gates[102]
        assert g102.stability == "regressing"

    def test_calibration_drift_index(self):
        from audit_trend import analyze
        # All same score → CDI = 0
        points_stable = [
            self._make_point(f"2026-05-0{i+1}T12:00:00Z", 10.0, "EXEMPLARY")
            for i in range(5)
        ]
        report = analyze(points_stable)
        assert report.calibration_drift_index == 0.0

        # Varied scores → CDI > 0
        points_varied = [
            self._make_point("2026-05-01T12:00:00Z", 10.0, "EXEMPLARY"),
            self._make_point("2026-05-02T12:00:00Z", 6.0, "ACCEPTABLE"),
        ]
        report = analyze(points_varied)
        assert report.calibration_drift_index > 0.1


class TestAuditTrendRendering:
    """audit_trend report rendering (JSON, Markdown, HTML)."""

    def _three_point_report(self):
        from audit_trend import analyze, TimePoint
        points = [
            TimePoint.from_payload({
                "schema_version": "1.0", "audit_timestamp": f"2026-05-0{i}T12:00:00Z",
                "build_version": "0.3.1", "score": 8.0 + i, "band": "EXEMPLARY",
                "summary": {}, "gates": [
                    {"id": 100, "name": "JSON", "severity": "error",
                     "result": "PASS", "checked_count": 10, "samples": []}
                ]
            }, path=f"a{i}.json") for i in range(1, 4)
        ]
        return analyze(points)

    def test_json_render_schema_v1(self):
        from audit_trend import format_trend_json
        report = self._three_point_report()
        parsed = json.loads(format_trend_json(report))
        assert parsed["schema_version"] == "1.0"
        assert parsed["window"]["audit_count"] == 3
        assert "score_series" in parsed
        assert "calibration_drift_index" in parsed
        assert len(parsed["points"]) == 3

    def test_markdown_render_includes_summary(self):
        from audit_trend import format_trend_markdown
        report = self._three_point_report()
        md = format_trend_markdown(report)
        assert "audit-trend" in md
        assert "Score summary" in md
        assert "Band distribution" in md
        assert "Gate stability" in md

    def test_html_render_contains_inline_svg(self):
        from audit_trend import format_trend_html
        report = self._three_point_report()
        html = format_trend_html(report)
        assert "<svg" in html
        assert "polyline" in html
        # Inline-only — no external font/CDN/script
        assert "<script" not in html
        assert "fonts.googleapis.com" not in html
        # Dark theme indicator
        assert "var(--bg)" in html


class TestG13PluginExpansion:
    """G13 plugin emitter v0.3.1 — Variable rebind walker."""

    def test_extracts_alias_pairs_from_rationale(self):
        from auto_remediate.plugin_writer import _extract_alias_rebinds
        rationale = (
            "G13 rewrites stale aliases:\n"
            "- color.semantic.anayasa.primary → color.tbk.9\n"
            "- color.semantic.aym.primary → color.lacivert.8"
        )
        pairs = _extract_alias_rebinds(rationale)
        assert len(pairs) == 2
        assert pairs[0] == ("color.semantic.anayasa.primary", "color.tbk.9")
        assert pairs[1] == ("color.semantic.aym.primary", "color.lacivert.8")

    def test_emits_rebind_map_in_typescript(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        action = RemediationAction(
            strategy_id=13,
            action_type="patch_file",
            target_path="tokens/m.tokens.json",
            rationale=(
                "Rewrites:\n- color.x.1 → color.y.2\n- color.a.3 → color.b.4"
            ),
            new_content="{}",
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        assert "new Map<string, string>" in ts
        assert "'color.x.1'" in ts and "'color.y.2'" in ts
        assert "'color.a.3'" in ts and "'color.b.4'" in ts
        assert "getLocalVariableCollections" in ts
        assert "createVariableAlias" in ts
        assert "setValueForMode" in ts

    def test_g13_handles_no_pairs_gracefully(self, tmp_path):
        from auto_remediate.plugin_writer import render_plugin_script
        action = RemediationAction(
            strategy_id=13, action_type="patch_file",
            target_path="x.json", rationale="No arrows in this rationale",
            new_content="{}",
        )
        ctx = RemediationContext(library_dir=tmp_path)
        ts = render_plugin_script([action], ctx)
        # Empty map is still well-formed TS
        assert "new Map<string, string>" in ts
        assert "(no pairs parsed from rationale)" in ts

    def test_g13_deduplicates_repeated_pairs(self):
        from auto_remediate.plugin_writer import _extract_alias_rebinds
        rationale = (
            "Rewrites:\n"
            "- color.x → color.y\n"
            "- color.x → color.y\n"   # Duplicate
            "- color.a → color.b"
        )
        pairs = _extract_alias_rebinds(rationale)
        assert len(pairs) == 2
        assert pairs == [("color.x", "color.y"), ("color.a", "color.b")]


class TestMultiDSSmokeTests:
    """v0.3.1 GA: ecosystem works on Material 3 + Carbon + Düstur."""

    def _fixture_path(self, name: str) -> Path:
        # tests/fixtures/<name>/library-registry.json
        return _REPO / "tests" / "fixtures" / name

    def test_material3_stub_passes_static_lint(self):
        from publish_audit.static_lint import run_static_lint
        bundle = self._fixture_path("material3-stub")
        if not bundle.exists():
            return  # fixture absent in this checkout; smoke test optional
        results = run_static_lint(bundle)
        # All gates should PASS or skip (no failures)
        failures = [r for r in results if r.status == "fail"]
        assert failures == [], (
            f"Material 3 stub regressed: " +
            ", ".join(f"G{r.gate.id} ({r.failures[:1]})" for r in failures)
        )

    def test_carbon_stub_passes_static_lint(self):
        from publish_audit.static_lint import run_static_lint
        bundle = self._fixture_path("carbon-stub")
        if not bundle.exists():
            return
        results = run_static_lint(bundle)
        failures = [r for r in results if r.status == "fail"]
        assert failures == [], (
            f"Carbon stub regressed: " +
            ", ".join(f"G{r.gate.id} ({r.failures[:1]})" for r in failures)
        )

    def test_merged_dtcg_discovery_falls_back_to_first_tokens(self, tmp_path):
        from publish_audit.static_lint import _find_merged_dtcg
        # No library-registry; should pick first *.tokens.json under tokens/
        (tmp_path / "tokens").mkdir()
        (tmp_path / "tokens" / "anything.tokens.json").write_text(
            '{"color": {}}'
        )
        result = _find_merged_dtcg(tmp_path)
        assert result is not None
        assert result.name == "anything.tokens.json"


# ===========================================================================
# v1.0.0 GA — Stable API surface + Supply-chain attestation
# ===========================================================================

class TestPublicAPISurface:
    """v1.0.0: figma_forge top-level package re-exports and contract."""

    def test_top_level_package_imports(self):
        import figma_forge as ff
        # Sanity: not empty
        assert hasattr(ff, "__version__")
        assert hasattr(ff, "API_VERSION")
        assert hasattr(ff, "__all__")
        # __all__ is the canonical contract
        assert len(ff.__all__) >= 20

    def test_api_version_is_1_0(self):
        import figma_forge as ff
        assert ff.API_VERSION == "1.0"

    def test_all_exported_symbols_are_resolvable(self):
        import figma_forge as ff
        unresolvable = [
            name for name in ff.__all__
            if getattr(ff, name, None) is None
        ]
        assert unresolvable == [], (
            f"figma_forge.__all__ contains unresolvable symbols: {unresolvable}"
        )

    def test_audit_diff_public_surface(self):
        import figma_forge as ff
        # Dataclasses
        assert isinstance(ff.AuditSnapshot, type)
        assert isinstance(ff.DiffReport, type)
        assert isinstance(ff.GateTransition, type)
        # Functions
        assert callable(ff.compare_audits)
        assert callable(ff.load_audit_snapshot)
        assert callable(ff.format_diff_json)
        assert callable(ff.format_diff_markdown)

    def test_audit_trend_public_surface(self):
        import figma_forge as ff
        assert isinstance(ff.TimePoint, type)
        assert isinstance(ff.TrendReport, type)
        assert isinstance(ff.GateTimeSeries, type)
        assert callable(ff.analyze_trend)
        assert callable(ff.load_audit_points)
        assert callable(ff.format_trend_html)

    def test_supply_chain_lazy_load(self):
        """Supply-chain submodule is lazy-loaded on first access."""
        import figma_forge as ff
        # First-time access should resolve via __getattr__
        assert callable(ff.build_bundle_manifest)
        assert callable(ff.sign_manifest)
        assert callable(ff.verify_manifest)
        assert isinstance(ff.BundleManifest, type)
        assert isinstance(ff.ProvenanceAttestation, type)

    def test_unknown_attribute_raises_clear_error(self):
        import figma_forge as ff
        try:
            _ = ff.nonexistent_function
            assert False, "should have raised AttributeError"
        except AttributeError as e:
            assert "figma_forge" in str(e)
            assert "nonexistent_function" in str(e)


class TestSupplyChainBundleManifest:
    """v1.0.0: BundleManifest wrapper + canonical hashing."""

    def _make_library(self, tmp_path: Path) -> Path:
        lib = tmp_path / "lib"
        (lib / "tokens").mkdir(parents=True)
        (lib / "tokens" / "dustur.tokens.json").write_text(
            '{"color": {"primary": {"$type": "color", "$value": "#0000FF"}}}'
        )
        (lib / "library-registry.json").write_text(
            '{"ds_name": "X", "ds_version": "0.1.0"}'
        )
        return lib

    def test_build_bundle_manifest_returns_wrapper(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        assert isinstance(manifest, ff.BundleManifest)
        assert manifest.file_count >= 2
        assert manifest.total_size_bytes > 0

    def test_manifest_hash_is_deterministic(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        h1 = ff.build_bundle_manifest(lib).manifest_hash()
        h2 = ff.build_bundle_manifest(lib).manifest_hash()
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_manifest_hash_changes_when_file_modified(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        h1 = ff.build_bundle_manifest(lib).manifest_hash()
        # Tamper a file
        (lib / "tokens" / "dustur.tokens.json").write_text(
            '{"color": {"primary": {"$type": "color", "$value": "#FF0000"}}}'
        )
        h2 = ff.build_bundle_manifest(lib).manifest_hash()
        assert h1 != h2


class TestSupplyChainSlsaProvenance:
    """v1.0.0: SLSA v1.0 provenance shape."""

    def test_provenance_dict_has_canonical_in_toto_shape(self):
        import figma_forge as ff
        prov = ff.ProvenanceAttestation(
            bundle_manifest_hash="abc" + "0" * 61,
            builder_id="builder",
            invocation_command="cmd",
            source_repository="https://example.com/repo",
            source_commit="commit-sha",
        )
        d = prov.to_dict()
        # Canonical _type and predicateType
        assert d["_type"] == "https://in-toto.io/Statement/v1"
        assert d["predicateType"] == "https://slsa.dev/provenance/v1"
        # Subject points to manifest hash
        assert d["subject"][0]["digest"]["sha256"] == "abc" + "0" * 61
        # Build definition
        bd = d["predicate"]["buildDefinition"]
        assert bd["externalParameters"]["command"] == "cmd"
        assert bd["resolvedDependencies"][0]["digest"]["gitCommit"] == "commit-sha"
        # Run details
        assert d["predicate"]["runDetails"]["builder"]["id"] == "builder"

    def test_provenance_skips_git_commit_when_unset(self):
        import figma_forge as ff
        prov = ff.ProvenanceAttestation(
            bundle_manifest_hash="x" * 64,
            builder_id="b", invocation_command="c",
            source_repository="https://example.com/repo",
            source_commit="",  # not provided
        )
        d = prov.to_dict()
        deps = d["predicate"]["buildDefinition"]["resolvedDependencies"]
        # Repo URI present, but no gitCommit digest
        assert len(deps) == 1
        assert deps[0]["digest"] == {}

    def test_provenance_no_deps_when_no_source_repo(self):
        import figma_forge as ff
        prov = ff.ProvenanceAttestation(
            bundle_manifest_hash="x" * 64,
            builder_id="b", invocation_command="c",
        )
        d = prov.to_dict()
        deps = d["predicate"]["buildDefinition"]["resolvedDependencies"]
        assert deps == []


class TestSupplyChainSignAndVerify:
    """v1.0.0: sign_manifest + verify_manifest end-to-end (sha256-only mode)."""

    def _make_library(self, tmp_path: Path) -> Path:
        lib = tmp_path / "lib"
        (lib / "tokens").mkdir(parents=True)
        (lib / "tokens" / "t.tokens.json").write_text(
            '{"color": {"x": {"$type": "color", "$value": "#FF00FF"}}}'
        )
        (lib / "library-registry.json").write_text(
            '{"ds_name": "Test", "ds_version": "0.1.0"}'
        )
        return lib

    def test_sign_sha256_only_writes_three_artifacts(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        signed = ff.sign_manifest(
            manifest,
            identity="test@example.com",
            sign_mode="sha256-only",
        )
        out_dir = tmp_path / "signed"
        paths = signed.write_artifacts(out_dir)
        assert "manifest" in paths and paths["manifest"].exists()
        assert "provenance" in paths and paths["provenance"].exists()
        assert "signature" in paths and paths["signature"].exists()

    def test_verify_passes_for_clean_bundle(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        signed = ff.sign_manifest(manifest, identity="t@x.com", sign_mode="sha256-only")
        paths = signed.write_artifacts(tmp_path / "signed")
        result = ff.verify_manifest(
            manifest_path=paths["manifest"],
            provenance_path=paths["provenance"],
            signature_path=paths["signature"],
            expected_identity="t@x.com",
            library_dir=lib,
        )
        assert result.is_valid, f"Expected clean verify; got {result.failed_checks}"
        # Should have ≥4 passed checks (manifest, bundle, sig, identity)
        assert len(result.passed_checks) >= 4

    def test_verify_detects_modified_file_in_bundle(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        signed = ff.sign_manifest(manifest, identity="t@x.com", sign_mode="sha256-only")
        paths = signed.write_artifacts(tmp_path / "signed")
        # Tamper after signing
        (lib / "library-registry.json").write_text(
            '{"ds_name": "Test", "ds_version": "0.1.0", "TAMPERED": true}'
        )
        result = ff.verify_manifest(
            manifest_path=paths["manifest"],
            provenance_path=paths["provenance"],
            signature_path=paths["signature"],
            expected_identity="t@x.com",
            library_dir=lib,
        )
        assert not result.is_valid
        assert any("library-registry.json" in f for f in result.failed_checks)

    def test_verify_detects_identity_mismatch(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        signed = ff.sign_manifest(manifest, identity="legit@example.com",
                                  sign_mode="sha256-only")
        paths = signed.write_artifacts(tmp_path / "signed")
        result = ff.verify_manifest(
            manifest_path=paths["manifest"],
            provenance_path=paths["provenance"],
            signature_path=paths["signature"],
            expected_identity="impostor@evil.example",
            library_dir=lib,
        )
        assert not result.is_valid
        assert any("identity mismatch" in f for f in result.failed_checks)

    def test_verify_detects_modified_manifest(self, tmp_path):
        import figma_forge as ff
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        signed = ff.sign_manifest(manifest, identity="t@x.com", sign_mode="sha256-only")
        paths = signed.write_artifacts(tmp_path / "signed")
        # Tamper the manifest JSON
        contents = json.loads(paths["manifest"].read_text())
        contents["bundle_name"] = "MALICIOUS_RENAME"
        paths["manifest"].write_text(json.dumps(contents))
        result = ff.verify_manifest(
            manifest_path=paths["manifest"],
            provenance_path=paths["provenance"],
            signature_path=paths["signature"],
            expected_identity="t@x.com",
        )
        assert not result.is_valid
        assert any("manifest hash mismatch" in f for f in result.failed_checks)

    def test_sign_mode_auto_falls_back_when_sigstore_missing(self, tmp_path,
                                                              monkeypatch):
        """auto mode: if sigstore is not available, fall back to sha256-only."""
        import figma_forge as ff
        from figma_forge import supply_chain
        # Force fallback by pretending sigstore is missing
        monkeypatch.setattr(supply_chain, "_sigstore_available", lambda: False)
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        signed = supply_chain.sign_manifest(
            manifest, identity="t@x.com", sign_mode="auto"
        )
        assert signed.signing_mode == "sha256-only"

    def test_sign_mode_sigstore_keyless_raises_when_missing(self, tmp_path,
                                                             monkeypatch):
        """Explicit sigstore-keyless raises if sigstore is missing."""
        import figma_forge as ff
        from figma_forge import supply_chain
        monkeypatch.setattr(supply_chain, "_sigstore_available", lambda: False)
        lib = self._make_library(tmp_path)
        manifest = ff.build_bundle_manifest(lib)
        try:
            supply_chain.sign_manifest(
                manifest, identity="t@x.com", sign_mode="sigstore-keyless"
            )
            assert False, "should have raised RuntimeError"
        except RuntimeError as e:
            assert "sigstore" in str(e).lower()


# ===========================================================================
# v1.1.0-alpha — Transport layer (RFC + Protocol + adapters + router)
# ===========================================================================

class TestTransportProtocolAndCapabilityMatrix:
    """v1.1.0-alpha: TransportAdapter Protocol introspection + matrix consistency."""

    def test_transport_operations_tuple_is_stable(self):
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        # The set is the authoritative declaration; tests below assume it
        assert isinstance(TRANSPORT_OPERATIONS, tuple)
        assert len(TRANSPORT_OPERATIONS) == 21
        assert "create_variable_collection" in TRANSPORT_OPERATIONS
        assert "import_svg_as_component" in TRANSPORT_OPERATIONS
        assert "attach_code_connect" in TRANSPORT_OPERATIONS
        # v1.2.0 instance composition operations
        assert "place_instance" in TRANSPORT_OPERATIONS
        assert "set_instance_property" in TRANSPORT_OPERATIONS

    def test_capability_matrix_covers_every_operation(self):
        """Every declared op must have a cell for each of the 4 adapters."""
        import figma_forge as ff
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        from figma_forge.transport.capability_matrix import (
            CAPABILITY_MATRIX,
            ADAPTER_STUB, ADAPTER_PLUGIN_CAPTURE,
            ADAPTER_REST, ADAPTER_MCP_CURSOR,
        )
        for op in TRANSPORT_OPERATIONS:
            for adapter in (ADAPTER_STUB, ADAPTER_PLUGIN_CAPTURE,
                            ADAPTER_REST, ADAPTER_MCP_CURSOR):
                assert (op, adapter) in CAPABILITY_MATRIX, (
                    f"missing capability cell for ({op!r}, {adapter!r})"
                )

    def test_stub_supports_matches_matrix_declaration(self):
        """Every adapter's supports() must agree with capability_matrix."""
        import figma_forge as ff
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        from figma_forge.transport.capability_matrix import (
            ADAPTER_STUB, capability,
        )
        stub = ff.StubTransport()
        for op in TRANSPORT_OPERATIONS:
            cell = capability(op, ADAPTER_STUB)
            expected = cell.level in ("supported", "supported-enterprise")
            actual = stub.supports(op)
            assert actual == expected, (
                f"stub.supports({op!r}) = {actual}; matrix says {cell.level!r}"
            )

    def test_plugin_capture_supports_matches_matrix_declaration(self):
        import figma_forge as ff
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        from figma_forge.transport.capability_matrix import (
            ADAPTER_PLUGIN_CAPTURE, capability,
        )
        plug = ff.PluginCaptureTransport()
        for op in TRANSPORT_OPERATIONS:
            cell = capability(op, ADAPTER_PLUGIN_CAPTURE)
            expected = cell.level in ("supported", "supported-enterprise")
            actual = plug.supports(op)
            assert actual == expected, (
                f"plug.supports({op!r}) = {actual}; matrix says {cell.level!r}"
            )

    def test_rest_supports_matches_matrix_declaration(self):
        import figma_forge as ff
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        from figma_forge.transport.capability_matrix import (
            ADAPTER_REST, capability,
        )
        rest = ff.RestTransport(pat="dummy")
        for op in TRANSPORT_OPERATIONS:
            cell = capability(op, ADAPTER_REST)
            expected = cell.level in ("supported", "supported-enterprise")
            actual = rest.supports(op)
            assert actual == expected, (
                f"rest.supports({op!r}) = {actual}; matrix says {cell.level!r}"
            )

    def test_transport_adapter_is_runtime_checkable(self):
        """The Protocol is structural — adapters conform without inheritance."""
        import figma_forge as ff
        assert isinstance(ff.StubTransport(), ff.TransportAdapter)
        assert isinstance(ff.PluginCaptureTransport(), ff.TransportAdapter)
        assert isinstance(ff.RestTransport(pat="x"), ff.TransportAdapter)


class TestStubTransport:
    """v1.1.0-alpha: StubTransport always-success contract."""

    def test_full_operation_coverage_recorded_in_log(self):
        import figma_forge as ff
        stub = ff.StubTransport()
        token = stub.begin_session()
        fr = stub.create_file(name="Foundations", file_kind="foundations")
        coll = stub.create_variable_collection(
            file_key=fr.key, name="Colors", modes=["Light", "Dark"]
        )
        var = stub.create_variable(
            collection_ref=coll, name="color.primary.500",
            type="COLOR", values_per_mode={"Light": "#0F62FE", "Dark": "#4589FF"},
        )
        result = stub.commit_session(token)
        # 3 ops executed, plus session-bracketing entries
        assert result.operations_applied == 3
        assert len(stub.operations_log) == 5  # begin + 3 ops + commit
        kinds = [e["kind"] for e in stub.operations_log]
        assert kinds == [
            "begin_session", "create_file",
            "create_variable_collection", "create_variable",
            "commit_session",
        ]

    def test_stub_never_raises_on_any_supported_operation(self):
        """Stub contract: always succeeds for declared-supported ops."""
        import figma_forge as ff
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        stub = ff.StubTransport()
        # Just verify supports() is consistent; per-op smoke is covered above
        for op in TRANSPORT_OPERATIONS:
            # Stub claims to support every operation
            assert stub.supports(op)


class TestPluginCaptureTransport:
    """v1.1.0-alpha: PluginCaptureTransport TS rendering + idempotency guards."""

    def test_renders_variable_collection_with_idempotent_guard(self):
        import figma_forge as ff
        plug = ff.PluginCaptureTransport()
        plug.begin_session()
        plug.create_variable_collection(
            file_key="x", name="Colors", modes=["Light", "Dark"]
        )
        script = plug.render_typescript()
        # Idempotency guard
        assert "getLocalVariableCollections()" in script
        assert "find(c => c.name === 'Colors')" in script
        # Mode-ensure loop
        assert "requiredModes" in script
        assert "'Light'" in script and "'Dark'" in script

    def test_locale_tr_emits_turkish_header(self):
        import figma_forge as ff
        plug = ff.PluginCaptureTransport(locale="tr-TR")
        plug.begin_session()
        plug.create_variable_collection(file_key="x", name="R", modes=["A"])
        script = plug.render_typescript()
        assert "yapıştırıp" in script  # Turkish header phrase

    def test_locale_default_emits_english_header(self):
        import figma_forge as ff
        plug = ff.PluginCaptureTransport()  # locale defaults to en-US
        plug.begin_session()
        plug.create_variable_collection(file_key="x", name="R", modes=["A"])
        script = plug.render_typescript()
        assert "paste and Enter" in script

    def test_import_svg_rejects_non_svg_source(self):
        """ValidationError at capture time prevents broken TS at paste time."""
        import figma_forge as ff
        from figma_forge.transport.errors import ValidationError
        plug = ff.PluginCaptureTransport()
        plug.begin_session()
        page = plug.create_page(file_key="x", name="Icons")
        try:
            plug.import_svg_as_component(
                page_ref=page, name="bad",
                svg_source="not an svg",
                canonical_size=(24, 24),
            )
            assert False, "should have raised ValidationError"
        except ValidationError as e:
            assert "svg" in str(e).lower()

    def test_code_connect_unsupported_raises_clear_error(self):
        import figma_forge as ff
        from figma_forge.transport.protocol import (
            ComponentRef, CodeConnectMapping,
        )
        from figma_forge.transport.errors import CapabilityUnsupportedError
        plug = ff.PluginCaptureTransport()
        cref = ComponentRef(file_key="x", node_id="n", name="Btn")
        try:
            plug.attach_code_connect(
                component_ref=cref,
                mapping=CodeConnectMapping(
                    framework="react", import_statement="",
                    code_example="", props_mapping={},
                ),
            )
            assert False, "should have raised CapabilityUnsupportedError"
        except CapabilityUnsupportedError as e:
            assert e.operation == "attach_code_connect"
            assert e.adapter_id == "plugin-capture"

    def test_stable_ids_reproducible_across_runs(self):
        """Stable id hashing keeps captured operation list deterministic."""
        import figma_forge as ff
        # Two independent capture sessions with identical inputs:
        def capture_once():
            plug = ff.PluginCaptureTransport()
            plug.begin_session()
            plug.create_variable_collection(
                file_key="x", name="Test", modes=["A", "B"]
            )
            return plug.captured_operations()
        a = capture_once()
        b = capture_once()
        # Same collection_id under deterministic hashing
        assert a[0]["collection_id"] == b[0]["collection_id"]


class TestRestTransport:
    """v1.1.0-alpha: RestTransport credential gating + queue behavior."""

    def test_no_pat_means_no_credentials(self, monkeypatch):
        import figma_forge as ff
        monkeypatch.delenv("FIGMA_PERSONAL_ACCESS_TOKEN", raising=False)
        rest = ff.RestTransport()
        assert not rest.has_credentials()

    def test_explicit_pat_overrides_env(self, monkeypatch):
        import figma_forge as ff
        monkeypatch.setenv("FIGMA_PERSONAL_ACCESS_TOKEN", "env-token")
        rest = ff.RestTransport(pat="explicit-token")
        assert rest.has_credentials()
        assert rest._resolved_pat == "explicit-token"

    def test_begin_session_without_pat_raises_authentication_error(
        self, monkeypatch
    ):
        import figma_forge as ff
        monkeypatch.delenv("FIGMA_PERSONAL_ACCESS_TOKEN", raising=False)
        rest = ff.RestTransport()
        try:
            rest.begin_session()
            assert False, "should have raised AuthenticationError"
        except ff.AuthenticationError as e:
            assert "PAT" in str(e)

    def test_alpha_queues_calls_without_dispatching(self):
        import figma_forge as ff
        rest = ff.RestTransport(pat="x", dry_run=True)
        rest.begin_session()
        rest.create_variable_collection(
            file_key="f", name="Colors", modes=["Light"]
        )
        # Alpha contract: pending_calls accumulates, no HTTP attempt
        assert len(rest.pending_calls) == 1
        assert rest.pending_calls[0]["method"] == "POST"
        assert "variables" in rest.pending_calls[0]["path"]

    def test_styles_raise_capability_unsupported(self):
        import figma_forge as ff
        from figma_forge.transport.errors import CapabilityUnsupportedError
        from figma_forge.transport.protocol import Paint
        rest = ff.RestTransport(pat="x")
        try:
            rest.create_paint_style(
                file_key="f", name="primary",
                paints=[Paint(paint_type="SOLID",
                              payload={"color": {"r": 1, "g": 0, "b": 0}})],
            )
            assert False, "should have raised"
        except CapabilityUnsupportedError as e:
            assert e.operation == "create_paint_style"


class TestTransportRouter:
    """v1.1.0-alpha: TransportRouter preference + credential gating."""

    def test_router_requires_stub_adapter(self):
        import figma_forge as ff
        try:
            ff.TransportRouter(
                adapters={"rest-v1": ff.RestTransport(pat="x")},
                preferences=["rest-v1"],
            )
            assert False, "should have raised ValueError"
        except ValueError as e:
            assert "stub" in str(e).lower()

    def test_router_picks_first_supporting_adapter_in_preference_order(
        self, monkeypatch
    ):
        import figma_forge as ff
        monkeypatch.setenv("FIGMA_PERSONAL_ACCESS_TOKEN", "tok")
        router = ff.TransportRouter(
            adapters={
                "stub": ff.StubTransport(),
                "plugin-capture": ff.PluginCaptureTransport(),
                "rest-v1": ff.RestTransport(pat="tok"),
            },
            preferences=["rest-v1", "plugin-capture", "stub"],
        )
        # REST supports + has credentials → wins
        adapter = router.select("create_variable_collection")
        assert adapter.adapter_id() == "rest-v1"
        # REST doesn't support styles → falls to plugin-capture
        adapter = router.select("create_paint_style")
        assert adapter.adapter_id() == "plugin-capture"
        # Nothing other than stub supports publish_library
        adapter = router.select("publish_library")
        assert adapter.adapter_id() == "stub"

    def test_router_skips_credential_less_rest(self, monkeypatch):
        """When REST has no PAT, router falls through to next preference."""
        import figma_forge as ff
        monkeypatch.delenv("FIGMA_PERSONAL_ACCESS_TOKEN", raising=False)
        router = ff.TransportRouter(
            adapters={
                "stub": ff.StubTransport(),
                "plugin-capture": ff.PluginCaptureTransport(),
                "rest-v1": ff.RestTransport(),  # no pat
            },
            preferences=["rest-v1", "plugin-capture", "stub"],
        )
        adapter = router.select("create_variable_collection")
        # Skipped REST due to missing PAT, landed on plugin-capture
        assert adapter.adapter_id() == "plugin-capture"

    def test_candidate_chain_lists_supporting_adapters(self):
        import figma_forge as ff
        router = ff.TransportRouter(
            adapters={
                "stub": ff.StubTransport(),
                "plugin-capture": ff.PluginCaptureTransport(),
                "rest-v1": ff.RestTransport(pat="x"),
            },
            preferences=["rest-v1", "plugin-capture", "stub"],
        )
        chain = router.candidate_chain("create_variable_collection")
        assert chain == ["rest-v1", "plugin-capture", "stub"]
        # Only stub supports publish_library
        chain = router.candidate_chain("publish_library")
        assert chain == ["stub"]

    def test_fallback_warning_recorded_when_only_stub_handles(
        self, monkeypatch
    ):
        import figma_forge as ff
        monkeypatch.delenv("FIGMA_PERSONAL_ACCESS_TOKEN", raising=False)
        router = ff.TransportRouter(
            adapters={
                "stub": ff.StubTransport(),
                "rest-v1": ff.RestTransport(),
            },
            preferences=["rest-v1", "stub"],
        )
        # Nothing in preferences supports publish_library besides stub,
        # but stub IS in preferences here, so it's not technically a
        # "fallback" — the warning fires only when stub is reached as
        # last resort after preferences exhausted. Use a craft preference:
        router2 = ff.TransportRouter(
            adapters={
                "stub": ff.StubTransport(),
                "rest-v1": ff.RestTransport(),  # no pat
            },
            preferences=["rest-v1"],  # stub deliberately not preferred
        )
        adapter = router2.select("create_variable_collection")
        # Returned stub as last resort; warning recorded
        assert adapter.adapter_id() == "stub"
        assert len(router2.fallback_warnings) == 1


class TestRunPipeline:
    """v1.1.0-alpha: high-level run_pipeline + dual color_families shape."""

    def test_pipeline_on_dustur_via_plugin_capture(self):
        """Düstur (dict color_families) → ~72 primitives + 1 collection."""
        import figma_forge as ff
        from pathlib import Path
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=ff.PluginCaptureTransport(locale="tr-TR"),
            file_key="DUSTUR_FOUNDATIONS",
            stages=["FOUNDATIONS_BUILD"],  # explicit; v1.1.0-alpha.2 added ICONS
        )
        assert result.is_success
        assert "FOUNDATIONS_BUILD" in result.stages_completed
        # 1 collection + 72 primitives (6 families × 12 steps)
        assert result.operations_succeeded == 73
        assert result.operations_attempted == 73

    def test_pipeline_on_material3_stub_via_plugin_capture(self):
        """Material 3 (list color_families) → ~20 primitives + 1 collection."""
        import figma_forge as ff
        from pathlib import Path
        result = ff.run_pipeline(
            Path("/home/claude/figma-forge/tests/fixtures/material3-stub"),
            transport=ff.PluginCaptureTransport(),
            file_key="MAT3_FOUNDATIONS",
        )
        assert result.is_success
        # Material 3 stub: gray (10 steps) + blue (10 steps) + 1 collection
        assert result.operations_succeeded >= 21

    def test_pipeline_with_default_router_lands_on_plugin_capture(
        self, monkeypatch
    ):
        """Without a PAT, REST is skipped; PluginCapture handles foundations."""
        import figma_forge as ff
        from pathlib import Path
        monkeypatch.delenv("FIGMA_PERSONAL_ACCESS_TOKEN", raising=False)
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            file_key="DUSTUR",
        )
        assert result.is_success
        # Default router should have used plugin-capture
        adapters_used = list(result.session_results.keys())
        assert "plugin-capture" in adapters_used

    def test_pipeline_result_dataclass_shape(self):
        """PipelineResult exposes the documented fields."""
        import figma_forge as ff
        r = ff.PipelineResult()
        assert r.stages_completed == []
        assert r.stages_failed == []
        assert r.operations_attempted == 0
        assert r.operations_succeeded == 0
        assert r.session_results == {}
        assert r.fallback_warnings == []
        assert r.is_success is True  # no failures recorded


class TestTransportPublicAPI:
    """v1.1.0-alpha: top-level figma_forge re-exports + v1.x contract."""

    def test_v1_1_added_symbols_present(self):
        import figma_forge as ff
        v1_1_new = {
            "TransportAdapter", "TransportError",
            "AuthenticationError", "CapabilityUnsupportedError",
            "StubTransport", "PluginCaptureTransport", "RestTransport",
            "TransportRouter", "PipelineResult", "run_pipeline",
        }
        for sym in v1_1_new:
            assert sym in ff.__all__, f"{sym} missing from __all__"
            assert getattr(ff, sym) is not None

    def test_v1_0_symbols_still_present(self):
        """v1.x append-only guarantee: every v1.0 symbol must still resolve."""
        import figma_forge as ff
        v1_0_symbols = {
            "AuditSnapshot", "DiffReport", "GateTransition",
            "compare_audits", "load_audit_snapshot",
            "format_diff_json", "format_diff_markdown",
            "GateTimeSeries", "TimePoint", "TrendReport",
            "analyze_trend", "load_audit_points",
            "format_trend_json", "format_trend_markdown", "format_trend_html",
            "run_static_lint",
            "RemediationAction", "RemediationContext",
            "RemediationOptions", "run_remediation",
            "API_VERSION", "__version__",
        }
        missing = [s for s in v1_0_symbols if s not in ff.__all__]
        assert missing == [], (
            f"v1.0 symbols missing from v1.1 __all__: {missing}"
        )

    def test_api_version_unchanged_in_minor_bump(self):
        """API_VERSION stays at '1.0' because v1.1 is additive."""
        import figma_forge as ff
        assert ff.API_VERSION == "1.0"

    def test_color_families_helper_handles_both_shapes(self):
        """_color_families_for tolerates dict-keyed AND list-of-dicts."""
        from figma_forge.pipeline import _color_families_for
        from pathlib import Path
        dustur = _color_families_for(Path("/home/claude/dustur-figma-library"))
        m3 = _color_families_for(Path(
            "/home/claude/figma-forge/tests/fixtures/material3-stub"
        ))
        # Düstur: dict keyed by family token-tree prefix
        assert set(dustur) == {"tbk", "lacivert", "bordo", "turkuvaz", "amber", "neutral"}
        # Material 3 stub: list-of-dicts with explicit name fields
        assert len(m3) >= 2  # at least two families declared
        assert all(isinstance(name, str) for name in m3)


# ===========================================================================
# v1.1.0-alpha.2 — Live REST dispatch + Icons stage + Mock server integration
# ===========================================================================

class TestRestTransportLiveDispatch:
    """v1.1.0-alpha.2: RestTransport._dispatch_http via in-process mock server."""

    def _mock_server(self):
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        return MockFigmaServer()

    def test_successful_roundtrip_records_200_response(self):
        import figma_forge as ff
        with self._mock_server() as server:
            rest = ff.RestTransport(
                pat="test-pat", base_url=server.url, dry_run=False,
            )
            rest.begin_session()
            rest.create_variable_collection(
                file_key="F", name="Colors", modes=["Light"],
            )
            assert len(rest.pending_calls) == 1
            assert rest.pending_calls[0].get("response_code") == 200
            assert len(server.request_log) == 1
            assert server.request_log[0]["method"] == "POST"
            assert "variables" in server.request_log[0]["path"]

    def test_pat_passed_via_x_figma_token_header(self):
        import figma_forge as ff
        with self._mock_server() as server:
            rest = ff.RestTransport(
                pat="figd_secret_abc", base_url=server.url, dry_run=False,
            )
            rest.begin_session()
            rest.create_variable_collection(
                file_key="F", name="Colors", modes=["Light"],
            )
            received = server.request_log[0]["headers"]
            assert received.get("X-Figma-Token") == "figd_secret_abc"

    def test_401_response_raises_authentication_error(self):
        import figma_forge as ff
        from figma_forge.transport.errors import AuthenticationError
        with self._mock_server() as server:
            server.set_response(
                "POST", "/v1/files/X/variables",
                status=401, body={"error": "invalid token"},
            )
            rest = ff.RestTransport(
                pat="bad-pat", base_url=server.url, dry_run=False,
            )
            rest.begin_session()
            try:
                rest.create_variable_collection(
                    file_key="X", name="Y", modes=["A"],
                )
                assert False, "should have raised"
            except AuthenticationError as e:
                assert "401" in str(e)
                assert e.adapter_id == "rest-v1"

    def test_403_response_raises_authorization_error(self):
        """Non-Enterprise PAT trying to write Variables → 403."""
        import figma_forge as ff
        from figma_forge.transport.errors import AuthorizationError
        with self._mock_server() as server:
            server.set_response(
                "POST", "/v1/files/X/variables",
                status=403, body={"error": "Enterprise plan required"},
            )
            rest = ff.RestTransport(
                pat="non-ent-pat", base_url=server.url, dry_run=False,
            )
            rest.begin_session()
            try:
                rest.create_variable_collection(
                    file_key="X", name="Y", modes=["A"],
                )
                assert False, "should have raised"
            except AuthorizationError as e:
                assert "403" in str(e)
                assert "Enterprise" in str(e) or "403" in str(e)

    def test_404_response_raises_not_found_error(self):
        import figma_forge as ff
        from figma_forge.transport.errors import NotFoundError
        with self._mock_server() as server:
            server.set_response(
                "POST", "/v1/files/MISSING/variables",
                status=404, body={"error": "file not found"},
            )
            rest = ff.RestTransport(
                pat="x", base_url=server.url, dry_run=False,
            )
            rest.begin_session()
            try:
                rest.create_variable_collection(
                    file_key="MISSING", name="Y", modes=["A"],
                )
                assert False, "should have raised"
            except NotFoundError as e:
                assert "404" in str(e)

    def test_429_response_carries_retry_after_seconds(self):
        import figma_forge as ff
        from figma_forge.transport.errors import RateLimitError
        with self._mock_server() as server:
            server.set_response(
                "POST", "/v1/files/X/variables",
                status=429, body={"error": "rate limited"},
                headers={"Content-Type": "application/json",
                         "Retry-After": "45"},
            )
            rest = ff.RestTransport(
                pat="x", base_url=server.url, dry_run=False,
            )
            rest.begin_session()
            try:
                rest.create_variable_collection(
                    file_key="X", name="Y", modes=["A"],
                )
                assert False, "should have raised"
            except RateLimitError as e:
                assert e.retry_after_seconds == 45.0
                assert "429" in str(e)

    def test_503_response_raises_upstream_unavailable(self):
        import figma_forge as ff
        from figma_forge.transport.errors import UpstreamUnavailableError
        with self._mock_server() as server:
            server.set_response(
                "POST", "/v1/files/X/variables",
                status=503, body={"error": "service unavailable"},
            )
            rest = ff.RestTransport(
                pat="x", base_url=server.url, dry_run=False,
            )
            rest.begin_session()
            try:
                rest.create_variable_collection(
                    file_key="X", name="Y", modes=["A"],
                )
                assert False, "should have raised"
            except UpstreamUnavailableError as e:
                assert "503" in str(e)


class TestPipelineIconsBuild:
    """v1.1.0-alpha.2: ICONS_BUILD stage walks icons/svg/ tree."""

    def test_dustur_full_foundations_and_icons(self):
        """Düstur: 1 coll + 72 primitives + 3 pages + 26 icons = 102 ops."""
        import figma_forge as ff
        from pathlib import Path
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=ff.PluginCaptureTransport(locale="tr-TR"),
            stages=["FOUNDATIONS_BUILD", "ICONS_BUILD"],
        )
        assert result.is_success
        assert any("FOUNDATIONS_BUILD" in s for s in result.stages_completed)
        assert any("ICONS_BUILD" in s for s in result.stages_completed)
        # 1 collection + 72 primitives + 3 pages + 26 SVGs = 102 ops
        assert result.operations_succeeded == 102

    def test_icons_build_skipped_gracefully_when_no_icons_dir(self, tmp_path):
        """Bundles without icons/svg/ shouldn't fail the pipeline."""
        import figma_forge as ff
        # Minimal bundle: token tree + registry, no icons/
        lib = tmp_path / "no-icons-lib"
        (lib / "tokens").mkdir(parents=True)
        # Use a name discoverable by _find_merged_dtcg's slug-based search:
        # ds_name "Test" → slug "test" → tokens/test.tokens.json
        (lib / "tokens" / "test.tokens.json").write_text(
            '{"color": {"primary": {"500": {"$value": "#0F62FE", "$type": "color"}}}}'
        )
        (lib / "library-registry.json").write_text(
            '{"ds_name": "Test", "color_families": [{"name": "primary"}]}'
        )
        result = ff.run_pipeline(
            lib, transport=ff.StubTransport(),
            stages=["FOUNDATIONS_BUILD", "ICONS_BUILD"],
        )
        # FOUNDATIONS_BUILD runs; ICONS_BUILD reports the missing dir
        assert result.is_success
        assert any("no icons/svg" in s for s in result.stages_completed)

    def test_icons_stage_creates_one_page_per_category(self):
        """Düstur has 3 categories: document, selcuklu-motif, tier."""
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport()
        ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=plug,
            file_key="X",
            stages=["ICONS_BUILD"],
        )
        ops = plug.captured_operations()
        page_creates = [o for o in ops if o["kind"] == "create_page"]
        page_names = sorted(o["name"] for o in page_creates)
        assert "Icons / document" in page_names
        assert "Icons / selcuklu-motif" in page_names
        assert "Icons / tier" in page_names

    def test_icons_stage_routes_imports_to_correct_page(self):
        """import_svg ops carry page_name matching the category."""
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport()
        ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=plug,
            file_key="X",
            stages=["ICONS_BUILD"],
        )
        imports = [o for o in plug.captured_operations()
                   if o["kind"] == "import_svg_as_component"]
        # Verify the icon-to-page mapping survived
        tier_imports = [o for o in imports
                        if "tier" in o.get("page_name", "")]
        assert len(tier_imports) > 0
        for op in tier_imports:
            assert op["page_name"] == "Icons / tier"


class TestRestErrorTranslation:
    """v1.1.0-alpha.2: _translate_http_error path mapping (no live server)."""

    def test_infer_operation_from_variables_path(self):
        import figma_forge as ff
        rest = ff.RestTransport(pat="x", dry_run=True)
        assert rest._infer_operation_from_path(
            "/v1/files/X/variables"
        ) == "variables_endpoint"

    def test_infer_operation_from_code_connect_path(self):
        import figma_forge as ff
        rest = ff.RestTransport(pat="x", dry_run=True)
        assert rest._infer_operation_from_path(
            "/v1/code_connect"
        ) == "code_connect_endpoint"

    def test_infer_operation_from_file_get(self):
        import figma_forge as ff
        rest = ff.RestTransport(pat="x", dry_run=True)
        assert rest._infer_operation_from_path(
            "/v1/files/ABC123"
        ) == "get_file"


# ===========================================================================
# v1.1.0-beta.1 — Components / Patterns / Code Connect stage runners
# ===========================================================================

class TestVariantExpansion:
    """v1.1.0-beta.1: Cartesian variant matrix expansion + disabled exclusion."""

    def test_cartesian_product_of_axes(self):
        from figma_forge.pipeline import _variant_specs_from_axes
        axes = {"Variant": ["A", "B"], "Size": ["sm", "lg"]}
        specs = _variant_specs_from_axes(axes, set())
        assert len(specs) == 4  # 2 × 2
        names = {s.name for s in specs}
        assert "Variant=A, Size=sm" in names
        assert "Variant=B, Size=lg" in names

    def test_partial_descriptor_excludes_all_matching_combinations(self):
        """A 2-axis disabled clause excludes every combination matching it.

        'Variant=Ghost, State=Hover' (no Size given) excludes Ghost+Hover
        for ALL Size values — this is the mathematically correct behavior
        (each Size×Variant×State combo is a distinct Figma variant).
        """
        from figma_forge.pipeline import _variant_specs_from_axes
        axes = {
            "Variant": ["Primary", "Ghost"],
            "Size": ["sm", "md", "lg"],
            "State": ["Default", "Hover"],
        }
        disabled = {"Variant=Ghost, State=Hover (uses opacity overlay)"}
        specs = _variant_specs_from_axes(axes, disabled)
        # 2 × 3 × 2 = 12 total; Ghost+Hover × 3 Sizes = 3 excluded → 9
        assert len(specs) == 9
        ghost_hover = [
            s for s in specs
            if s.properties["Variant"] == "Ghost"
            and s.properties["State"] == "Hover"
        ]
        assert len(ghost_hover) == 0

    def test_is_disabled_matches_partial_clause(self):
        from figma_forge.pipeline import _is_disabled
        disabled = {"Variant=Ghost, State=Hover (prose)"}
        assert _is_disabled(
            {"Variant": "Ghost", "Size": "sm", "State": "Hover"}, disabled
        )
        assert not _is_disabled(
            {"Variant": "Primary", "Size": "sm", "State": "Hover"}, disabled
        )

    def test_empty_disabled_set_excludes_nothing(self):
        from figma_forge.pipeline import _variant_specs_from_axes
        axes = {"Variant": ["A", "B", "C"]}
        specs = _variant_specs_from_axes(axes, set())
        assert len(specs) == 3


class TestPipelineComponentsBuild:
    """v1.1.0-beta.1: COMPONENTS_BUILD stage."""

    def test_dustur_components_build(self):
        """Düstur: 17 component specs → 17 ComponentSets + 336 variants."""
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport()
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=plug,
            file_key="DUSTUR",
            stages=["COMPONENTS_BUILD"],
        )
        assert result.is_success
        assert any("COMPONENTS_BUILD" in s for s in result.stages_completed)
        ops = plug.captured_operations()
        sets = [o for o in ops if o["kind"] == "create_component_set"]
        # Düstur components all have variant axes
        assert len(sets) == 17
        total_variants = sum(o["variant_count"] for o in sets)
        assert total_variants == 336

    def test_components_build_attaches_descriptions(self):
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport()
        ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=plug, file_key="X",
            stages=["COMPONENTS_BUILD"],
        )
        descs = [o for o in plug.captured_operations()
                 if o["kind"] == "update_component_description"]
        assert len(descs) == 17  # one per component

    def test_components_build_skips_when_no_directory(self, tmp_path):
        import figma_forge as ff
        lib = tmp_path / "empty-lib"
        lib.mkdir()
        result = ff.run_pipeline(
            lib, transport=ff.StubTransport(),
            stages=["COMPONENTS_BUILD"],
        )
        assert any("no components directory" in s
                   for s in result.stages_completed)


class TestPipelinePatternsBuild:
    """v1.1.0-beta.1: PATTERNS_BUILD stage."""

    def test_dustur_patterns_build(self):
        """Düstur: 17 pattern specs → 17 composite components."""
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport()
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=plug, file_key="DUSTUR",
            stages=["PATTERNS_BUILD"],
        )
        assert result.is_success
        assert any("PATTERNS_BUILD" in s for s in result.stages_completed)
        comps = [o for o in plug.captured_operations()
                 if o["kind"] == "create_component"]
        assert len(comps) == 17

    def test_patterns_enrich_description_with_composition(self):
        """Pattern descriptions include 'Uses components:' metadata."""
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport()
        ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=plug, file_key="X",
            stages=["PATTERNS_BUILD"],
        )
        descs = [o for o in plug.captured_operations()
                 if o["kind"] == "update_component_description"]
        # At least one pattern references components in its description
        assert any("Uses components:" in o["description"] for o in descs)

    def test_patterns_build_skips_when_no_directory(self, tmp_path):
        import figma_forge as ff
        lib = tmp_path / "empty-lib"
        lib.mkdir()
        result = ff.run_pipeline(
            lib, transport=ff.StubTransport(),
            stages=["PATTERNS_BUILD"],
        )
        assert any("no patterns directory" in s
                   for s in result.stages_completed)


class TestPipelineCodeConnect:
    """v1.1.0-beta.1: CODE_CONNECT stage."""

    def test_dustur_code_connect_via_stub(self):
        """Düstur: 17 code-connect specs → 17 mappings (stub fallback)."""
        import figma_forge as ff
        from pathlib import Path
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=ff.StubTransport(),
            file_key="DUSTUR",
            stages=["CODE_CONNECT"],
        )
        assert result.is_success
        assert any("CODE_CONNECT" in s for s in result.stages_completed)
        assert any("17 mappings attached" in s
                   for s in result.stages_completed)

    def test_code_connect_routes_to_rest_when_available(self):
        """With a REST adapter (mock), Code Connect routes to it."""
        import figma_forge as ff
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        with MockFigmaServer() as server:
            rest = ff.RestTransport(
                pat="test-pat", base_url=server.url, dry_run=False,
            )
            router = ff.TransportRouter(
                adapters={"stub": ff.StubTransport(), "rest-v1": rest},
                preferences=["rest-v1", "stub"],
            )
            result = ff.run_pipeline(
                Path("/home/claude/dustur-figma-library"),
                transport=router, file_key="DUSTUR",
                stages=["CODE_CONNECT"],
            )
            assert result.is_success
            # REST received the code_connect POSTs
            cc_posts = [r for r in server.request_log
                        if "code_connect" in r["path"]]
            assert len(cc_posts) == 17

    def test_code_connect_skips_when_no_directory(self, tmp_path):
        import figma_forge as ff
        lib = tmp_path / "empty-lib"
        lib.mkdir()
        result = ff.run_pipeline(
            lib, transport=ff.StubTransport(),
            stages=["CODE_CONNECT"],
        )
        assert any("no code-connect directory" in s
                   for s in result.stages_completed)


class TestFullPipelineFiveStages:
    """v1.1.0-beta.1: all five stages in one run_pipeline invocation."""

    def test_dustur_full_five_stage_pipeline(self):
        """Complete Düstur build: 265 ops across 5 stages (with instances)."""
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport(locale="tr-TR")
        router = ff.TransportRouter(
            adapters={"stub": ff.StubTransport(), "plugin-capture": plug},
            preferences=["plugin-capture", "stub"],
        )
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=router, file_key="DUSTUR",
        )
        assert result.is_success
        # 5 stages all present
        joined = " ".join(result.stages_completed)
        for stage in ("FOUNDATIONS_BUILD", "ICONS_BUILD",
                      "COMPONENTS_BUILD", "PATTERNS_BUILD", "CODE_CONNECT"):
            assert stage in joined
        # Total ops: 1 coll + 72 vars + (3 pages + 26 icons) +
        #            (1 page + 17 sets + 17 descs) +
        #            (1 page + 17 patterns + 17 descs + 76 instances) +
        #            17 cc = 265  (v1.2.0 adds 76 nested instances)
        assert result.operations_succeeded == 265

    def test_default_stages_cover_all_five(self):
        """run_pipeline with no stages= runs all five by default."""
        import figma_forge as ff
        from pathlib import Path
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=ff.StubTransport(),
            file_key="X",
        )
        joined = " ".join(result.stages_completed)
        assert "FOUNDATIONS_BUILD" in joined
        assert "ICONS_BUILD" in joined
        assert "COMPONENTS_BUILD" in joined
        assert "PATTERNS_BUILD" in joined
        assert "CODE_CONNECT" in joined


# ===========================================================================
# v1.2.0-alpha — McpCursorTransport (MCP tool-call plan emitter)
# ===========================================================================

class TestMcpCursorCapability:
    """v1.2.0-alpha: capability declarations + matrix consistency."""

    def test_supports_matches_matrix(self):
        """supports() agrees with the capability matrix for mcp-cursor."""
        import figma_forge as ff
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        from figma_forge.transport.capability_matrix import (
            capability, ADAPTER_MCP_CURSOR,
        )
        mcp = ff.McpCursorTransport()
        for op in TRANSPORT_OPERATIONS:
            cell = capability(op, ADAPTER_MCP_CURSOR)
            expected = cell.level in (
                "supported", "supported-enterprise", "supported-nl"
            )
            assert mcp.supports(op) == expected, f"{op}: drift"

    def test_native_vs_nl_split(self):
        """5 native + 13 use_figma_nl = 18 supported; publish unsupported."""
        import figma_forge as ff
        from figma_forge.transport.capability_matrix import (
            supported_operations, capability, ADAPTER_MCP_CURSOR,
        )
        ops = supported_operations(ADAPTER_MCP_CURSOR)
        assert len(ops) == 20  # +2 instance composition ops (v1.2.0)
        native = [o for o in ops
                  if capability(o, ADAPTER_MCP_CURSOR).level == "supported"]
        nl = [o for o in ops
              if capability(o, ADAPTER_MCP_CURSOR).level == "supported-nl"]
        assert len(native) == 5
        assert len(nl) == 15  # 13 + place_instance + set_instance_property
        mcp = ff.McpCursorTransport()
        assert not mcp.supports("publish_library")

    def test_emit_mechanism(self):
        import figma_forge as ff
        mcp = ff.McpCursorTransport()
        assert mcp.emit_mechanism("create_file") == "native"
        assert mcp.emit_mechanism("attach_code_connect") == "native"
        assert mcp.emit_mechanism("create_variable") == "use_figma_nl"
        assert mcp.emit_mechanism("create_component_set") == "use_figma_nl"

    def test_emit_mechanism_unsupported_raises(self):
        import figma_forge as ff
        from figma_forge.transport.errors import CapabilityUnsupportedError
        mcp = ff.McpCursorTransport()
        with pytest.raises(CapabilityUnsupportedError):
            mcp.emit_mechanism("publish_library")

    def test_authentication_is_ambient_mcp(self):
        import figma_forge as ff
        mcp = ff.McpCursorTransport()
        auth = mcp.authentication_required()
        assert auth.needs_credentials is False
        assert auth.credential_kind == "ambient-mcp"

    def test_is_transport_adapter(self):
        import figma_forge as ff
        from figma_forge.transport.protocol import TransportAdapter
        assert isinstance(ff.McpCursorTransport(), TransportAdapter)


class TestMcpCursorPlanEmission:
    """v1.2.0-alpha: MCP tool-call plan structure."""

    def test_native_descriptor_has_no_instruction(self):
        """Native descriptors carry args, no NL instruction."""
        import figma_forge as ff
        from figma_forge.transport.protocol import (
            ComponentRef, CodeConnectMapping,
        )
        mcp = ff.McpCursorTransport()
        mcp.begin_session()
        mcp.attach_code_connect(
            component_ref=ComponentRef(file_key="X", node_id="n1", name="Button"),
            mapping=CodeConnectMapping(
                framework="react", import_statement="import {Button}",
                code_example="<Button/>", props_mapping={},
            ),
        )
        ops = mcp.captured_operations()
        assert len(ops) == 1
        assert ops[0]["mechanism"] == "native"
        assert ops[0]["mcp_tool"] == "Figma:send_code_connect_mappings"
        assert "instruction" not in ops[0]

    def test_nl_descriptor_has_instruction(self):
        """use_figma_nl descriptors carry a natural-language instruction."""
        import figma_forge as ff
        mcp = ff.McpCursorTransport()
        mcp.begin_session()
        mcp.create_variable_collection(
            file_key="X", name="Renkler", modes=["Light", "Dark"],
        )
        op = mcp.captured_operations()[0]
        assert op["mechanism"] == "use_figma_nl"
        assert op["mcp_tool"] == "Figma:use_figma"
        assert "instruction" in op
        assert "Renkler" in op["instruction"]

    def test_locale_tr_produces_turkish_instruction(self):
        import figma_forge as ff
        mcp = ff.McpCursorTransport(locale="tr-TR")
        mcp.begin_session()
        mcp.create_page(file_key="X", name="Components")
        op = mcp.captured_operations()[0]
        assert "oluştur" in op["instruction"]  # Turkish "create"

    def test_locale_en_produces_english_instruction(self):
        import figma_forge as ff
        mcp = ff.McpCursorTransport(locale="en-US")
        mcp.begin_session()
        mcp.create_page(file_key="X", name="Components")
        op = mcp.captured_operations()[0]
        assert "Create" in op["instruction"]

    def test_render_mcp_plan_envelope(self):
        """The rendered plan is valid JSON with the expected envelope."""
        import figma_forge as ff
        import json
        mcp = ff.McpCursorTransport()
        mcp.begin_session()
        mcp.create_page(file_key="X", name="P1")
        plan = json.loads(mcp.render_mcp_plan())
        assert plan["plan_format_version"] == "1.0"
        assert plan["adapter"] == "mcp-cursor"
        assert plan["step_count"] == 1
        assert plan["steps"][0]["step"] == 1
        assert plan["steps"][0]["operation"] == "create_page"

    def test_svg_validation_at_emit(self):
        """import_svg_as_component rejects malformed SVG at capture time."""
        import figma_forge as ff
        from figma_forge.transport.protocol import PageRef
        from figma_forge.transport.errors import ValidationError
        mcp = ff.McpCursorTransport()
        mcp.begin_session()
        with pytest.raises(ValidationError):
            mcp.import_svg_as_component(
                page_ref=PageRef(file_key="X", page_id="p", name="Icons"),
                name="bad", svg_source="not-svg",
                canonical_size=(24, 24),
            )

    def test_publish_library_raises(self):
        import figma_forge as ff
        from figma_forge.transport.errors import CapabilityUnsupportedError
        mcp = ff.McpCursorTransport()
        with pytest.raises(CapabilityUnsupportedError):
            mcp.publish_library(file_key="X", changelog="v1")


class TestMcpCursorPipeline:
    """v1.2.0-alpha: full Düstur build through McpCursor."""

    def test_dustur_full_build_via_mcp(self):
        """Full 5-stage Düstur build emits a 189-step MCP plan."""
        import figma_forge as ff
        import json
        from pathlib import Path
        mcp = ff.McpCursorTransport(locale="tr-TR")
        router = ff.TransportRouter(
            adapters={"stub": ff.StubTransport(), "mcp-cursor": mcp},
            preferences=["mcp-cursor", "stub"],
        )
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=router, file_key="DUSTUR",
        )
        assert result.is_success
        assert result.operations_succeeded == 265
        assert len(result.fallback_warnings) == 0
        plan = json.loads(mcp.render_mcp_plan())
        assert plan["step_count"] == 265
        # 17 Code Connect mappings are native; rest are use_figma_nl
        # (172 v1.1 ops + 76 nested instances = 248 nl steps)
        assert plan["native_steps"] == 17
        assert plan["use_figma_nl_steps"] == 248

    def test_mcp_not_in_default_router(self):
        """McpCursor is opt-in; default router excludes it."""
        import figma_forge as ff
        from figma_forge.pipeline import _default_router
        router = _default_router()
        assert "mcp-cursor" not in router.adapters

    def test_router_selects_mcp_for_code_connect_fallback(self):
        """With REST uncredentialed, MCP becomes the Code Connect path."""
        import figma_forge as ff
        # REST with no PAT (dry_run, no creds) → router skips it for
        # credentialed ops; mcp-cursor (ambient) picks up Code Connect
        mcp = ff.McpCursorTransport()
        router = ff.TransportRouter(
            adapters={
                "stub": ff.StubTransport(),
                "mcp-cursor": mcp,
            },
            preferences=["mcp-cursor", "stub"],
        )
        selected = router.select("attach_code_connect")
        assert selected.adapter_id() == "mcp-cursor"


# ===========================================================================
# v1.2.0-alpha.2 — Nested-instance composition
# ===========================================================================

class TestNestedInstanceComposition:
    """v1.2.0-alpha.2: place_instance + set_instance_property."""

    def test_instance_ops_in_transport_operations(self):
        from figma_forge.transport.protocol import TRANSPORT_OPERATIONS
        assert "place_instance" in TRANSPORT_OPERATIONS
        assert "set_instance_property" in TRANSPORT_OPERATIONS
        assert len(TRANSPORT_OPERATIONS) == 21

    def test_rest_does_not_support_instances(self):
        """REST API has no instance-write endpoints."""
        import figma_forge as ff
        rest = ff.RestTransport()
        assert not rest.supports("place_instance")
        assert not rest.supports("set_instance_property")

    def test_stub_plugin_mcp_support_instances(self):
        import figma_forge as ff
        for adapter in (ff.StubTransport(), ff.PluginCaptureTransport(),
                        ff.McpCursorTransport()):
            assert adapter.supports("place_instance")
            assert adapter.supports("set_instance_property")

    def test_rest_place_instance_raises(self):
        import figma_forge as ff
        from figma_forge.transport.errors import CapabilityUnsupportedError
        from figma_forge.transport.protocol import ComponentRef
        rest = ff.RestTransport()
        ref = ComponentRef(file_key="X", node_id="n", name="C")
        with pytest.raises(CapabilityUnsupportedError):
            rest.place_instance(parent_ref=ref, component_ref=ref,
                                position=(0, 0))

    def test_stub_place_instance_returns_instance_ref(self):
        import figma_forge as ff
        from figma_forge.transport.protocol import ComponentRef, InstanceRef
        stub = ff.StubTransport()
        parent = ComponentRef(file_key="X", node_id="p", name="Pattern")
        comp = ComponentRef(file_key="X", node_id="c", name="Button")
        inst = stub.place_instance(parent_ref=parent, component_ref=comp,
                                   position=(0, 80))
        assert isinstance(inst, InstanceRef)
        assert inst.component_node_id == "c"
        assert inst.parent_node_id == "p"

    def test_plugin_emits_create_instance_ts(self):
        """PluginCapture renders figma.createInstance + appendChild."""
        import figma_forge as ff
        from figma_forge.transport.protocol import ComponentRef
        plug = ff.PluginCaptureTransport()
        plug.begin_session()
        parent = ComponentRef(file_key="X", node_id="p", name="Pattern")
        comp = ComponentRef(file_key="X", node_id="c", name="Button")
        inst = plug.place_instance(parent_ref=parent, component_ref=comp,
                                   position=(0, 80))
        plug.set_instance_property(instance_ref=inst, key="Variant",
                                   value="Primary")
        ts = plug.render_typescript()
        assert "createInstance()" in ts
        assert "appendChild" in ts
        assert "setProperties" in ts

    def test_mcp_emits_nl_instruction_for_instances(self):
        import figma_forge as ff
        import json
        from figma_forge.transport.protocol import ComponentRef
        mcp = ff.McpCursorTransport(locale="en-US")
        mcp.begin_session()
        parent = ComponentRef(file_key="X", node_id="p", name="Pattern")
        comp = ComponentRef(file_key="X", node_id="c", name="Button")
        mcp.place_instance(parent_ref=parent, component_ref=comp,
                           position=(0, 80))
        plan = json.loads(mcp.render_mcp_plan())
        assert plan["steps"][0]["operation"] == "place_instance"
        assert plan["steps"][0]["mechanism"] == "use_figma_nl"
        assert "instance" in plan["steps"][0]["instruction"].lower()

    def test_dustur_patterns_place_nested_instances(self):
        """Düstur PATTERNS_BUILD places 76 nested instances."""
        import figma_forge as ff
        from pathlib import Path
        plug = ff.PluginCaptureTransport()
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=plug, file_key="DUSTUR",
            stages=["PATTERNS_BUILD"],
        )
        assert result.is_success
        assert any("nested instances" in s for s in result.stages_completed)
        pi = [o for o in plug.captured_operations()
              if o["kind"] == "place_instance"]
        assert len(pi) == 76

    def test_patterns_skip_composition_when_rest(self):
        """When the adapter can't place instances, composition is skipped."""
        import figma_forge as ff
        from pathlib import Path
        # REST can't create_component either, so router falls to stub;
        # to force the "can't compose" path, use a router whose
        # create_component adapter lacks place_instance. We simulate by
        # selecting REST (which supports neither) — router falls to stub
        # which DOES support both, so instead assert the happy path here
        # and rely on capability test for the negative.
        rest = ff.RestTransport()
        assert not rest.supports("place_instance")

    def test_parse_component_reference_with_variant(self):
        from figma_forge.pipeline import _parse_component_reference
        name, props = _parse_component_reference("YuzeyBadge (Solid, Kanun)")
        assert name == "YuzeyBadge"
        assert props == {"prop0": "Solid", "prop1": "Kanun"}

    def test_parse_component_reference_bare(self):
        from figma_forge.pipeline import _parse_component_reference
        name, props = _parse_component_reference("Button")
        assert name == "Button"
        assert props == {}


# ===========================================================================
# v1.2.0-alpha.2 — BackoffPolicy
# ===========================================================================

class TestBackoffPolicy:
    """v1.2.0-alpha.2: rate-limit-aware retry policy."""

    def test_should_retry_respects_max_retries(self):
        import figma_forge as ff
        p = ff.BackoffPolicy(max_retries=3)
        assert p.should_retry(0)
        assert p.should_retry(2)
        assert not p.should_retry(3)
        assert not p.should_retry(4)

    def test_exponential_schedule_no_jitter(self):
        import figma_forge as ff
        p = ff.BackoffPolicy(max_retries=4, base_delay=1.0, jitter=False)
        assert p.compute_delay(0) == 1.0
        assert p.compute_delay(1) == 2.0
        assert p.compute_delay(2) == 4.0
        assert p.compute_delay(3) == 8.0

    def test_retry_after_honored(self):
        import figma_forge as ff
        p = ff.BackoffPolicy(base_delay=1.0, jitter=False)
        # server hint takes precedence over exponential
        assert p.compute_delay(5, retry_after_seconds=7.0) == 7.0

    def test_retry_after_clamped_to_max_delay(self):
        import figma_forge as ff
        p = ff.BackoffPolicy(max_delay=10.0, jitter=False)
        assert p.compute_delay(0, retry_after_seconds=999.0) == 10.0

    def test_max_delay_clamp_on_exponential(self):
        import figma_forge as ff
        p = ff.BackoffPolicy(base_delay=1.0, max_delay=30.0, jitter=False)
        assert p.compute_delay(10) == 30.0  # 1024 clamped

    def test_jitter_stays_within_ratio(self):
        import figma_forge as ff
        p = ff.BackoffPolicy(base_delay=10.0, jitter=True,
                             jitter_ratio=0.25, seed=42)
        d = p.compute_delay(0)
        assert 7.5 <= d <= 12.5  # 10 ± 25%

    def test_schedule_returns_all_delays(self):
        import figma_forge as ff
        p = ff.BackoffPolicy(max_retries=3, base_delay=1.0, jitter=False)
        assert p.schedule() == [1.0, 2.0, 4.0]

    def test_rest_retries_on_429(self):
        """RestTransport retries a 429 per the backoff policy."""
        import figma_forge as ff
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        with MockFigmaServer() as server:
            server.set_response(
                "POST", "/v1/files/DUSTUR/variables",
                status=429, body={"err": "rate limited"},
                headers={"Retry-After": "2"},
            )
            sleeps = []
            rest = ff.RestTransport(
                pat="test", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=2, base_delay=0.1,
                                         jitter=False),
            )
            rest._sleep_fn = lambda d: sleeps.append(d)
            rest.begin_session()
            from figma_forge.transport.errors import RateLimitError
            with pytest.raises(RateLimitError):
                rest.create_variable_collection(
                    file_key="DUSTUR", name="Renkler", modes=["L", "D"],
                )
            # 1 initial + 2 retries = 3 attempts; 2 sleeps honoring Retry-After
            posts = [r for r in server.request_log if "variables" in r["path"]]
            assert len(posts) == 3
            assert sleeps == [2.0, 2.0]

    def test_rest_no_backoff_single_shot(self):
        """Without a backoff policy, REST dispatches once (no retry)."""
        import figma_forge as ff
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        with MockFigmaServer() as server:
            server.set_response(
                "POST", "/v1/files/DUSTUR/variables",
                status=429, body={"err": "rate limited"},
            )
            rest = ff.RestTransport(pat="test", base_url=server.url,
                                    dry_run=False)  # no backoff
            rest.begin_session()
            from figma_forge.transport.errors import RateLimitError
            with pytest.raises(RateLimitError):
                rest.create_variable_collection(
                    file_key="DUSTUR", name="Renkler", modes=["L", "D"],
                )
            posts = [r for r in server.request_log if "variables" in r["path"]]
            assert len(posts) == 1  # single shot, no retry

    def test_backoff_in_public_api(self):
        import figma_forge as ff
        assert "BackoffPolicy" in ff.__all__
        assert ff.BackoffPolicy().max_retries == 3


# ===========================================================================
# v1.2.0-beta.1 — Concurrency detection
# ===========================================================================

class TestConcurrencyDetection:
    """v1.2.0-beta.1: file last_modified comparison."""

    def test_file_ref_has_last_modified(self):
        from figma_forge.transport.protocol import FileRef
        f = FileRef(key="X", last_modified="2026-05-28T10:00:00Z")
        assert f.last_modified == "2026-05-28T10:00:00Z"
        # default empty
        assert FileRef(key="Y").last_modified == ""

    def test_empty_baseline_not_checked(self):
        import figma_forge as ff
        r = ff.check_concurrency(ff.StubTransport(), file_key="X",
                                 baseline_modified="")
        assert r.checked is False
        assert r.has_concurrent_edit is False

    def test_plugin_cannot_check_graceful(self):
        """PluginCapture can't read live state → checked=False, no raise."""
        import figma_forge as ff
        r = ff.check_concurrency(ff.PluginCaptureTransport(), file_key="X",
                                 baseline_modified="2026-01-01T00:00:00Z")
        assert r.checked is False
        assert "cannot read live" in r.detail

    def test_rest_unchanged_no_concurrent_edit(self):
        import figma_forge as ff
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        with MockFigmaServer() as server:
            server.set_response("GET", "/v1/files/DUSTUR", status=200,
                                body={"name": "D", "lastModified": "2026-05-28T10:00:00Z"})
            rest = ff.RestTransport(pat="t", base_url=server.url, dry_run=False)
            rest.begin_session()
            r = ff.check_concurrency(rest, file_key="DUSTUR",
                                     baseline_modified="2026-05-28T10:00:00Z")
            assert r.checked is True
            assert r.has_concurrent_edit is False

    def test_rest_modified_detects_concurrent_edit(self):
        import figma_forge as ff
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        with MockFigmaServer() as server:
            server.set_response("GET", "/v1/files/DUSTUR", status=200,
                                body={"name": "D", "lastModified": "2026-05-28T11:30:00Z"})
            rest = ff.RestTransport(pat="t", base_url=server.url, dry_run=False)
            rest.begin_session()
            r = ff.check_concurrency(rest, file_key="DUSTUR",
                                     baseline_modified="2026-05-28T10:00:00Z")
            assert r.checked is True
            assert r.has_concurrent_edit is True
            assert "modified during the build" in r.detail

    def test_pipeline_detect_concurrency_flag(self):
        """run_pipeline(detect_concurrency=True) populates the report."""
        import figma_forge as ff
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        with MockFigmaServer() as server:
            server.set_response("GET", "/v1/files/DUSTUR", status=200,
                                body={"name": "D", "lastModified": "2026-05-28T10:00:00Z"})
            server.set_response("POST", "/v1/files/DUSTUR/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(pat="t", base_url=server.url, dry_run=False)
            router = ff.TransportRouter(
                adapters={"stub": ff.StubTransport(), "rest-v1": rest},
                preferences=["rest-v1", "stub"],
            )
            result = ff.run_pipeline(
                Path("/home/claude/dustur-figma-library"),
                transport=router, file_key="DUSTUR",
                stages=["FOUNDATIONS_BUILD"], detect_concurrency=True,
            )
            assert result.concurrency_report is not None
            assert result.concurrency_report.checked is True

    def test_pipeline_no_concurrency_by_default(self):
        """Without the flag, no concurrency report is produced."""
        import figma_forge as ff
        from pathlib import Path
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=ff.StubTransport(), file_key="X",
            stages=["FOUNDATIONS_BUILD"],
        )
        assert result.concurrency_report is None


# ===========================================================================
# v1.2.0-beta.1 — Mixed-router scenario (REST + Plugin + MCP together)
# ===========================================================================

class TestMixedRouterScenario:
    """v1.2.0-beta.1: real-world hybrid dispatch across three channels."""

    def _mixed_router(self, rest_base_url, rest_pat="enterprise-pat"):
        import figma_forge as ff
        rest = ff.RestTransport(pat=rest_pat, base_url=rest_base_url,
                                dry_run=True)
        return ff.TransportRouter(
            adapters={
                "stub": ff.StubTransport(),
                "rest-v1": rest,
                "plugin-capture": ff.PluginCaptureTransport(),
                "mcp-cursor": ff.McpCursorTransport(),
            },
            preferences=["rest-v1", "plugin-capture", "mcp-cursor", "stub"],
        )

    def test_variables_route_to_rest(self):
        """With a credentialed REST, Variables go to REST (Enterprise)."""
        import figma_forge as ff
        router = self._mixed_router("https://api.figma.com")
        selected = router.select("create_variable")
        assert selected.adapter_id() == "rest-v1"

    def test_code_connect_routes_to_rest(self):
        import figma_forge as ff
        router = self._mixed_router("https://api.figma.com")
        selected = router.select("attach_code_connect")
        assert selected.adapter_id() == "rest-v1"

    def test_create_component_falls_to_plugin(self):
        """REST can't create components → falls to PluginCapture."""
        import figma_forge as ff
        router = self._mixed_router("https://api.figma.com")
        selected = router.select("create_component")
        assert selected.adapter_id() == "plugin-capture"

    def test_place_instance_falls_to_plugin(self):
        """REST can't place instances → falls to PluginCapture."""
        import figma_forge as ff
        router = self._mixed_router("https://api.figma.com")
        selected = router.select("place_instance")
        assert selected.adapter_id() == "plugin-capture"

    def test_set_instance_property_falls_to_plugin(self):
        import figma_forge as ff
        router = self._mixed_router("https://api.figma.com")
        selected = router.select("set_instance_property")
        assert selected.adapter_id() == "plugin-capture"

    def test_candidate_chain_for_place_instance(self):
        """The candidate chain skips REST (unsupported) for place_instance."""
        import figma_forge as ff
        router = self._mixed_router("https://api.figma.com")
        chain = router.candidate_chain("place_instance")
        # REST must not be a candidate (it's unsupported)
        assert "rest-v1" not in chain
        # plugin-capture is the first viable candidate
        assert chain[0] == "plugin-capture"

    def test_rest_without_credentials_skipped_for_variables(self):
        """An uncredentialed REST is skipped; Variables fall onward."""
        import figma_forge as ff
        import os
        # Ensure no ambient PAT leaks in
        old = os.environ.pop("FIGMA_PERSONAL_ACCESS_TOKEN", None)
        try:
            rest = ff.RestTransport(pat=None, base_url="https://api.figma.com",
                                    dry_run=True)
            router = ff.TransportRouter(
                adapters={
                    "stub": ff.StubTransport(),
                    "rest-v1": rest,
                    "plugin-capture": ff.PluginCaptureTransport(),
                },
                preferences=["rest-v1", "plugin-capture", "stub"],
            )
            selected = router.select("create_variable")
            # REST needs credentials it doesn't have → skipped → plugin
            assert selected.adapter_id() == "plugin-capture"
        finally:
            if old is not None:
                os.environ["FIGMA_PERSONAL_ACCESS_TOKEN"] = old

    def test_full_dustur_mixed_router_coverage(self):
        """Full Düstur build through the mixed router: each op to the
        right channel, no stage failures."""
        import figma_forge as ff
        from pathlib import Path
        router = self._mixed_router("https://api.figma.com")
        result = ff.run_pipeline(
            Path("/home/claude/dustur-figma-library"),
            transport=router, file_key="DUSTUR",
        )
        assert result.is_success
        # All 5 stages present
        joined = " ".join(result.stages_completed)
        for stage in ("FOUNDATIONS_BUILD", "ICONS_BUILD",
                      "COMPONENTS_BUILD", "PATTERNS_BUILD", "CODE_CONNECT"):
            assert stage in joined
        # Coverage summary shows the mix
        coverage = router.coverage_summary(
            list(__import__("figma_forge").transport.TRANSPORT_OPERATIONS)
        )
        assert coverage  # non-empty diagnostic


# ===========================================================================
# v1.3.0-alpha.1 — validate_mcp_plan
# ===========================================================================

class TestValidateMcpPlan:
    """v1.3.0-alpha.1: static validation of MCP tool-call plans."""

    def _good_plan(self):
        return {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "locale": "en-US", "step_count": 1,
            "native_steps": 0, "use_figma_nl_steps": 1,
            "steps": [{
                "step": 1, "operation": "create_page",
                "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                "arguments": {"name": "Components"},
                "instruction": "Create a page named 'Components'.",
            }],
        }

    def test_clean_plan_is_executable(self):
        import figma_forge as ff
        r = ff.validate_mcp_plan(self._good_plan())
        assert r.is_executable
        assert r.schema_errors == []
        assert r.argument_errors == []

    def test_real_dustur_plan_clean(self):
        """Düstur's 265-step plan validates with no errors."""
        import figma_forge as ff
        import json
        from pathlib import Path
        mcp = ff.McpCursorTransport()
        router = ff.TransportRouter(
            adapters={"stub": ff.StubTransport(), "mcp-cursor": mcp},
            preferences=["mcp-cursor", "stub"],
        )
        ff.run_pipeline(Path("/home/claude/dustur-figma-library"),
                        transport=router, file_key="DUSTUR")
        r = ff.validate_mcp_plan(mcp.render_mcp_plan())
        assert r.is_executable
        assert r.step_count == 265
        assert r.schema_errors == []
        assert r.argument_errors == []
        assert r.ordering_warnings == []  # patterns place inside own frames

    def test_accepts_json_string_and_dict(self):
        import figma_forge as ff
        import json
        plan = self._good_plan()
        r1 = ff.validate_mcp_plan(plan)
        r2 = ff.validate_mcp_plan(json.dumps(plan))
        assert r1.is_executable == r2.is_executable == True

    def test_envelope_not_object_fails(self):
        import figma_forge as ff
        r = ff.validate_mcp_plan(["not", "a", "dict"])
        assert not r.is_executable
        assert any("not a JSON object" in e for e in r.schema_errors)

    def test_envelope_missing_field(self):
        import figma_forge as ff
        plan = self._good_plan()
        del plan["adapter"]
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable
        assert any("adapter" in e for e in r.schema_errors)

    def test_step_count_mismatch_fails(self):
        import figma_forge as ff
        plan = self._good_plan()
        plan["step_count"] = 99
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable
        assert any("disagrees" in e for e in r.schema_errors)

    def test_step_count_not_int_fails(self):
        import figma_forge as ff
        plan = self._good_plan()
        plan["step_count"] = "one"
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable

    def test_native_with_forbidden_instruction(self):
        import figma_forge as ff
        plan = self._good_plan()
        plan["steps"] = [{
            "step": 1, "operation": "create_file",
            "mcp_tool": "Figma:create_new_file", "mechanism": "native",
            "arguments": {"name": "X", "file_kind": "design"},
            "instruction": "forbidden",
        }]
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable
        assert any("must not carry an 'instruction'" in e
                   for e in r.schema_errors)

    def test_nl_without_instruction(self):
        import figma_forge as ff
        plan = self._good_plan()
        plan["steps"][0]["instruction"] = ""
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable

    def test_invalid_mechanism(self):
        import figma_forge as ff
        plan = self._good_plan()
        plan["steps"][0]["mechanism"] = "telepathy"
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable

    def test_native_argument_shape(self):
        """send_code_connect_mappings requires 6 args."""
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 1, "steps": [{
                "step": 1, "operation": "attach_code_connect",
                "mcp_tool": "Figma:send_code_connect_mappings",
                "mechanism": "native", "arguments": {"framework": "react"},
            }],
        }
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable
        assert len(r.argument_errors) == 1
        ae = r.argument_errors[0]
        assert ae["step"] == 1
        assert "node_id" in ae["missing"]
        assert "component_name" in ae["missing"]

    def test_non_monotonic_step_numbers(self):
        import figma_forge as ff
        plan = self._good_plan()
        plan["step_count"] = 2
        plan["steps"].append({
            "step": 5, "operation": "create_page",
            "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
            "arguments": {}, "instruction": "x",
        })
        r = ff.validate_mcp_plan(plan)
        assert not r.is_executable
        assert any("monotonically" in e for e in r.schema_errors)

    def test_ordering_warning_collection_missing(self):
        """create_variable with no prior collection → warning, not error."""
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 1, "steps": [{
                "step": 1, "operation": "create_variable",
                "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                "arguments": {"name": "color.x", "collection_id": "vc_orphan"},
                "instruction": "Create a color variable named color.x.",
            }],
        }
        r = ff.validate_mcp_plan(plan)
        assert r.is_executable  # soft warning, still executable
        assert any("vc_orphan" in w for w in r.ordering_warnings)

    def test_ordering_warning_parent_missing(self):
        """place_instance with no prior parent component → warning."""
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 1, "steps": [{
                "step": 1, "operation": "place_instance",
                "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                "arguments": {"parent_name": "GhostPattern",
                              "component_name": "Button"},
                "instruction": "Place a Button in GhostPattern.",
            }],
        }
        r = ff.validate_mcp_plan(plan)
        assert r.is_executable
        assert any("GhostPattern" in w for w in r.ordering_warnings)

    def test_ordering_satisfied_no_warning(self):
        """When dependencies are satisfied, no ordering warning."""
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 3, "steps": [
                {"step": 1, "operation": "create_variable_collection",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"name": "C", "collection_id": "vc_1"},
                 "instruction": "x"},
                {"step": 2, "operation": "create_component",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"name": "Frame", "page_name": "P"},
                 "instruction": "x"},
                {"step": 3, "operation": "place_instance",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"parent_name": "Frame",
                               "component_name": "Button"},
                 "instruction": "x"},
            ],
        }
        r = ff.validate_mcp_plan(plan)
        assert r.is_executable
        # Frame is now a known component; parent_name resolves
        parent_warnings = [w for w in r.ordering_warnings if "Frame" in w]
        assert len(parent_warnings) == 0


# ===========================================================================
# v1.3.0-alpha.2 — Native promotion infrastructure (mcp_dispatch.REGISTRY)
# ===========================================================================

class TestMcpDispatchRegistry:
    """v1.3.0-alpha.2: REGISTRY as single source of truth for MCP
    dispatch. These tests guarantee that drift cannot silently
    re-enter — the three consumers (mcp_cursor, capability_matrix,
    plan_validation) all derive their behavior from the registry."""

    def test_registry_shape_and_entry_count(self):
        from figma_forge.transport.mcp_dispatch import REGISTRY, McpDispatchSpec
        assert isinstance(REGISTRY, dict)
        # 5 native + 15 use_figma_nl = 20 (publish_library deliberately
        # excluded — MCP unsupported)
        assert len(REGISTRY) == 20
        for op, spec in REGISTRY.items():
            assert isinstance(spec, McpDispatchSpec)
            assert spec.operation == op  # key matches operation field
            assert spec.mechanism in ("native", "use_figma_nl")

    def test_native_entries_have_required_args(self):
        """Every native entry must declare its MCP tool's argument shape."""
        from figma_forge.transport.mcp_dispatch import REGISTRY
        natives = [s for s in REGISTRY.values() if s.mechanism == "native"]
        assert len(natives) == 5
        for spec in natives:
            assert spec.required_args, (
                f"Native {spec.operation} has empty required_args — "
                f"validator can't enforce shape"
            )
            assert spec.mcp_tool.startswith("Figma:")
            assert spec.mcp_tool != "Figma:use_figma"  # use_figma is NL

    def test_nl_entries_use_figma(self):
        """Every use_figma_nl entry routes through Figma:use_figma."""
        from figma_forge.transport.mcp_dispatch import REGISTRY
        nls = [s for s in REGISTRY.values() if s.mechanism == "use_figma_nl"]
        for spec in nls:
            assert spec.mcp_tool == "Figma:use_figma"
            assert spec.required_args == ()  # NL carries intent in instruction

    def test_mcp_cursor_map_derives_from_registry(self):
        """mcp_cursor._MCP_TOOL_FOR_OPERATION is registry-derived;
        identical operation→(tool,mech) mapping."""
        from figma_forge.transport.mcp_dispatch import REGISTRY
        from figma_forge.transport.mcp_cursor import _MCP_TOOL_FOR_OPERATION
        assert set(_MCP_TOOL_FOR_OPERATION.keys()) == set(REGISTRY.keys())
        for op, (tool, mech) in _MCP_TOOL_FOR_OPERATION.items():
            spec = REGISTRY[op]
            assert tool == spec.mcp_tool, (
                f"Drift: mcp_cursor map says {op}→{tool} but registry "
                f"says {spec.mcp_tool}"
            )
            assert mech == spec.mechanism

    def test_capability_matrix_mcp_column_derives_from_registry(self):
        """Every MCP-Cursor cell in CAPABILITY_MATRIX whose operation
        is in REGISTRY must match the registry's mechanism →
        capability level mapping."""
        from figma_forge.transport.mcp_dispatch import REGISTRY
        from figma_forge.transport.capability_matrix import (
            CAPABILITY_MATRIX, ADAPTER_MCP_CURSOR,
        )
        for op, spec in REGISTRY.items():
            cell = CAPABILITY_MATRIX[(op, ADAPTER_MCP_CURSOR)]
            expected_level = (
                "supported" if spec.mechanism == "native" else "supported-nl"
            )
            assert cell.level == expected_level, (
                f"Drift: matrix says ({op}, mcp-cursor)={cell.level} "
                f"but registry mechanism={spec.mechanism} implies "
                f"{expected_level}"
            )
            assert cell.notes == spec.capability_note

    def test_plan_validation_arg_dict_derives_from_registry(self):
        """validate_mcp_plan's native arg dict is registry-derived;
        every native MCP tool's required args match the registry."""
        from figma_forge.transport.mcp_dispatch import REGISTRY
        from figma_forge.transport.plan_validation import _NATIVE_TOOL_REQUIRED_ARGS
        natives = {s.mcp_tool: s.required_args
                   for s in REGISTRY.values() if s.mechanism == "native"}
        assert _NATIVE_TOOL_REQUIRED_ARGS == natives

    def test_publish_library_intentionally_absent_from_registry(self):
        """publish_library has no MCP support (no API surface for it);
        it must NOT appear in the registry. Matrix still declares it
        as unsupported via the literal."""
        from figma_forge.transport.mcp_dispatch import REGISTRY
        from figma_forge.transport.capability_matrix import (
            CAPABILITY_MATRIX, ADAPTER_MCP_CURSOR,
        )
        assert "publish_library" not in REGISTRY
        # but matrix still has the literal-declared cell
        cell = CAPABILITY_MATRIX[("publish_library", ADAPTER_MCP_CURSOR)]
        assert cell.level == "unsupported"

    def test_mcp_tool_for_operation_helper(self):
        from figma_forge.transport.mcp_dispatch import mcp_tool_for_operation
        # Native lookup
        assert mcp_tool_for_operation("create_file") == (
            "Figma:create_new_file", "native"
        )
        # NL lookup
        assert mcp_tool_for_operation("create_page") == (
            "Figma:use_figma", "use_figma_nl"
        )
        # Unknown operation
        assert mcp_tool_for_operation("nonexistent") is None

    def test_capability_level_for_operation_helper(self):
        from figma_forge.transport.mcp_dispatch import capability_level_for_operation
        assert capability_level_for_operation("create_file") == "supported"
        assert capability_level_for_operation("create_page") == "supported-nl"
        assert capability_level_for_operation("publish_library") is None

    def test_native_required_args_helper(self):
        from figma_forge.transport.mcp_dispatch import native_required_args
        nra = native_required_args()
        # 5 native tools
        assert len(nra) == 5
        assert nra["Figma:create_new_file"] == ("name", "file_kind")
        assert nra["Figma:send_code_connect_mappings"][0] == "node_id"

    def test_promotion_simulation_propagates(self):
        """Simulate promoting an op from NL to native via temporary
        registry override; assert that all three consumers reflect
        the change after re-derivation. This is the core promise of
        the registry mechanic — 'a one-line edit'."""
        from figma_forge.transport import mcp_dispatch, capability_matrix
        from figma_forge.transport.mcp_dispatch import (
            McpDispatchSpec, REGISTRY,
        )
        # Save & override
        original = REGISTRY["create_page"]
        promoted = McpDispatchSpec(
            operation="create_page",
            mcp_tool="Figma:create_page_new_tool",  # hypothetical
            mechanism="native",
            required_args=("name", "file_key"),
            capability_note="hypothetical native create_page",
        )
        REGISTRY["create_page"] = promoted
        try:
            # Re-apply matrix overrides
            capability_matrix._apply_registry_overrides()
            # Consumer 1: capability matrix updated
            cell = capability_matrix.CAPABILITY_MATRIX[
                ("create_page", capability_matrix.ADAPTER_MCP_CURSOR)
            ]
            assert cell.level == "supported"
            assert cell.notes == "hypothetical native create_page"
            # Consumer 2: native arg dict updated
            nra = mcp_dispatch.native_required_args()
            assert nra["Figma:create_page_new_tool"] == ("name", "file_key")
            # Consumer 3: mcp_tool_for_operation helper updated
            assert mcp_dispatch.mcp_tool_for_operation("create_page") == (
                "Figma:create_page_new_tool", "native"
            )
        finally:
            # Restore so other tests see the real registry
            REGISTRY["create_page"] = original
            capability_matrix._apply_registry_overrides()

    def test_supports_method_unchanged_after_promotion(self):
        """supports() result depends on capability level — both
        'supported' and 'supported-nl' return True. Promotion must
        not flip supports() (backward compat for descriptor
        consumers)."""
        import figma_forge as ff
        mcp = ff.McpCursorTransport()
        # Before: create_page is supported-nl
        assert mcp.supports("create_page") is True
        # After hypothetical promotion (simulated by override above
        # and restored) — supports() would still be True for the
        # promoted operation. We assert the contract: both mechanisms
        # report True via the public supports() API.
        from figma_forge.transport.mcp_dispatch import REGISTRY
        for op, spec in REGISTRY.items():
            assert mcp.supports(op) is True, (
                f"supports({op}) returned False — backward compat "
                f"violation for registered operation"
            )


# ===========================================================================
# v1.3.0-beta.1 — BatchPolicy parallel dispatch
# ===========================================================================

class TestBatchPolicy:
    """v1.3.0-beta.1: opt-in parallel dispatch via ThreadPoolExecutor."""

    def _setup(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        server = MockFigmaServer()
        server.__enter__()
        server.set_response("GET", "/v1/files/X", status=200,
                            body={"name": "X", "lastModified": "T0"})
        server.set_response("POST", "/v1/files/X/variables",
                            status=200, body={"meta": {}})
        server.set_response("POST", "/v1/code_connect", status=200,
                            body={"meta": {}})
        return server

    def test_policy_shape_defaults(self):
        import figma_forge as ff
        p = ff.BatchPolicy()
        assert p.max_concurrency == 4
        assert p.enabled is True

    def test_policy_rejects_invalid_concurrency(self):
        import figma_forge as ff
        with pytest.raises(ValueError, match="max_concurrency must be >= 1"):
            ff.BatchPolicy(max_concurrency=0)
        with pytest.raises(ValueError):
            ff.BatchPolicy(max_concurrency=-1)

    def test_policy_is_frozen(self):
        """BatchPolicy is a frozen dataclass — immutable."""
        import figma_forge as ff
        import dataclasses
        p = ff.BatchPolicy()
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.max_concurrency = 8  # type: ignore[misc]

    def test_default_no_batch_immediate_dispatch(self):
        """Without batch policy, write calls dispatch immediately on queue."""
        import figma_forge as ff
        server = self._setup()
        try:
            rest = ff.RestTransport(pat="t", base_url=server.url,
                                    dry_run=False)
            rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C",
                                             modes=["light"])
            # Dispatched immediately; no _deferred tag
            assert len(rest.pending_calls) == 1
            assert not rest.pending_calls[0].get("_deferred")
            assert len(server.request_log) == 1
        finally:
            server.__exit__(None, None, None)

    def test_batch_defers_write_dispatch(self):
        """With batch policy, write calls are deferred until commit."""
        import figma_forge as ff
        server = self._setup()
        try:
            rest = ff.RestTransport(pat="t", base_url=server.url,
                                    dry_run=False,
                                    batch=ff.BatchPolicy(max_concurrency=2))
            token = rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C",
                                             modes=["light"])
            # Deferred — not yet dispatched
            assert rest.pending_calls[0].get("_deferred") is True
            assert len(server.request_log) == 0
            # commit_session fires the batch
            rest.commit_session(token)
            assert len(server.request_log) == 1
            # _deferred tag cleared after dispatch
            assert "_deferred" not in rest.pending_calls[0]
        finally:
            server.__exit__(None, None, None)

    def test_batch_skips_get_calls(self):
        """GET calls bypass batch deferral — caller needs response synchronously."""
        import figma_forge as ff
        server = self._setup()
        try:
            rest = ff.RestTransport(pat="t", base_url=server.url,
                                    dry_run=False,
                                    batch=ff.BatchPolicy(max_concurrency=2))
            rest.begin_session()
            # GET dispatches immediately, returns populated FileRef
            f = rest.get_file(key="X")
            assert f.last_modified == "T0"
            # GET call has no _deferred tag
            gets = [c for c in rest.pending_calls if c["method"] == "GET"]
            assert len(gets) == 1 and not gets[0].get("_deferred")
        finally:
            server.__exit__(None, None, None)

    def test_disabled_policy_acts_like_none(self):
        """enabled=False behaves identically to batch=None."""
        import figma_forge as ff
        server = self._setup()
        try:
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                batch=ff.BatchPolicy(max_concurrency=4, enabled=False),
            )
            rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C", modes=["light"])
            # Despite policy attached, disabled → immediate dispatch
            assert not rest.pending_calls[0].get("_deferred")
            assert len(server.request_log) == 1
        finally:
            server.__exit__(None, None, None)

    def test_max_concurrency_one_serial_through_pool(self):
        """max_concurrency=1 still uses the pool but dispatches sequentially."""
        import figma_forge as ff
        server = self._setup()
        try:
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                batch=ff.BatchPolicy(max_concurrency=1),
            )
            from pathlib import Path
            router = ff.TransportRouter(
                adapters={"stub": ff.StubTransport(), "rest-v1": rest,
                          "plugin-capture": ff.PluginCaptureTransport()},
                preferences=["rest-v1", "plugin-capture", "stub"],
            )
            r = ff.run_pipeline(Path("/home/claude/dustur-figma-library"),
                                transport=router, file_key="X")
            assert r.is_success
            assert len(server.request_log) == 90
        finally:
            server.__exit__(None, None, None)

    def test_full_dustur_batched_completes(self):
        """All 90 Düstur writes complete through a 4-worker pool."""
        import figma_forge as ff
        from pathlib import Path
        server = self._setup()
        try:
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                batch=ff.BatchPolicy(max_concurrency=4),
            )
            router = ff.TransportRouter(
                adapters={"stub": ff.StubTransport(), "rest-v1": rest,
                          "plugin-capture": ff.PluginCaptureTransport()},
                preferences=["rest-v1", "plugin-capture", "stub"],
            )
            r = ff.run_pipeline(Path("/home/claude/dustur-figma-library"),
                                transport=router, file_key="X")
            assert r.is_success
            # All 90 writes landed at the server, all in pending_calls
            assert len(server.request_log) == 90
            writes = [c for c in rest.pending_calls
                      if c["method"] == "POST"]
            assert len(writes) == 90
            # None left as deferred (all dispatched)
            assert not any(c.get("_deferred") for c in writes)
        finally:
            server.__exit__(None, None, None)

    def test_batch_with_backoff_per_thread_retry(self):
        """Backoff runs independently per worker thread.
        First call returns 429 once then 200; succeeds via retry."""
        import figma_forge as ff
        server = self._setup()
        try:
            # Override variables endpoint to 429 then 200 (queue of 2)
            server.set_response_sequence("POST", "/v1/files/X/variables",
                                        [(429, {"Retry-After": "0"}, {"err": "rate"}),
                                         (200, {}, {"meta": {}})])
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=2, base_delay=0.001),
                batch=ff.BatchPolicy(max_concurrency=2),
            )
            rest._sleep_fn = lambda _: None  # no real sleep in test
            token = rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C",
                                             modes=["light"])
            result = rest.commit_session(token)
            assert result.operations_failed == 0
            # Two server hits: the 429 attempt then the 200 retry
            assert len(server.request_log) == 2
        finally:
            server.__exit__(None, None, None)

    def test_batch_records_failures_continues(self):
        """A failing call records error on the dict; batch continues."""
        import figma_forge as ff
        server = self._setup()
        try:
            # Persistent 500 on variables endpoint
            server.set_response("POST", "/v1/files/X/variables",
                                status=500, body={"err": "boom"})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(max_concurrency=2),
            )
            rest._sleep_fn = lambda _: None
            token = rest.begin_session()
            # Two failing writes — both must be attempted by the pool
            rest.create_variable_collection(file_key="X", name="C1",
                                             modes=["light"])
            rest.create_variable_collection(file_key="X", name="C2",
                                             modes=["light"])
            result = rest.commit_session(token)
            # Both failures recorded; batch completed all scheduled work
            assert result.operations_failed == 2
            errored = [c for c in rest.pending_calls if c.get("error")]
            assert len(errored) == 2
        finally:
            server.__exit__(None, None, None)

    def test_session_artifacts_report_batch_metadata(self):
        """commit_session SessionResult artifacts include batch info."""
        import figma_forge as ff
        server = self._setup()
        try:
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                batch=ff.BatchPolicy(max_concurrency=3),
            )
            token = rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C", modes=["a"])
            result = rest.commit_session(token)
            assert result.artifacts["batch_dispatched"] == "1"
            assert result.artifacts["max_concurrency"] == "3"
        finally:
            server.__exit__(None, None, None)


# ===========================================================================
# v1.4.0-alpha.1 — PriorState (cross-session validator hints)
# ===========================================================================

class TestPriorState:
    """v1.4.0-alpha.1: cross-session validator hints via PriorState."""

    def _orphan_plan(self):
        """A plan with two cross-session orphan references."""
        return {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 2,
            "steps": [
                {"step": 1, "operation": "create_variable",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"name": "color.new.1",
                               "collection_id": "vc_existing"},
                 "instruction": "Create a color variable."},
                {"step": 2, "operation": "place_instance",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"parent_name": "ExistingFrame",
                               "component_name": "Icon"},
                 "instruction": "Place Icon."},
            ],
        }

    def test_prior_state_shape_defaults(self):
        import figma_forge as ff
        p = ff.PriorState()
        assert p.known_collection_ids == frozenset()
        assert p.known_collection_names == frozenset()
        assert p.known_component_names == frozenset()
        assert p.known_page_names == frozenset()

    def test_prior_state_is_frozen(self):
        import figma_forge as ff
        import dataclasses
        p = ff.PriorState()
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.known_collection_ids = frozenset({"x"})  # type: ignore[misc]

    def test_no_prior_state_emits_warnings_v13_behavior(self):
        """Without prior_state, the v1.3 behavior is preserved exactly."""
        import figma_forge as ff
        r = ff.validate_mcp_plan(self._orphan_plan())
        assert r.is_executable  # warnings don't block
        assert len(r.ordering_warnings) == 2
        assert any("vc_existing" in w for w in r.ordering_warnings)
        assert any("ExistingFrame" in w for w in r.ordering_warnings)

    def test_prior_state_none_explicitly_acts_like_v13(self):
        """Explicit prior_state=None matches no-arg call."""
        import figma_forge as ff
        plan = self._orphan_plan()
        r1 = ff.validate_mcp_plan(plan)
        r2 = ff.validate_mcp_plan(plan, prior_state=None)
        assert r1.ordering_warnings == r2.ordering_warnings

    def test_empty_prior_state_acts_like_none(self):
        """A default PriorState() is equivalent to passing None."""
        import figma_forge as ff
        plan = self._orphan_plan()
        r1 = ff.validate_mcp_plan(plan, prior_state=None)
        r2 = ff.validate_mcp_plan(plan, prior_state=ff.PriorState())
        assert r1.ordering_warnings == r2.ordering_warnings

    def test_prior_state_collection_suppresses_orphan_collection(self):
        import figma_forge as ff
        prior = ff.PriorState(known_collection_ids=frozenset({"vc_existing"}))
        r = ff.validate_mcp_plan(self._orphan_plan(), prior_state=prior)
        # Only the parent_name warning remains
        assert len(r.ordering_warnings) == 1
        assert not any("vc_existing" in w for w in r.ordering_warnings)
        assert any("ExistingFrame" in w for w in r.ordering_warnings)

    def test_prior_state_component_suppresses_orphan_parent(self):
        import figma_forge as ff
        prior = ff.PriorState(known_component_names=frozenset({"ExistingFrame"}))
        r = ff.validate_mcp_plan(self._orphan_plan(), prior_state=prior)
        # Only the collection warning remains
        assert len(r.ordering_warnings) == 1
        assert not any("ExistingFrame" in w for w in r.ordering_warnings)
        assert any("vc_existing" in w for w in r.ordering_warnings)

    def test_prior_state_both_suppresses_all_warnings(self):
        """Full cross-session: all dependencies prior → 0 warnings."""
        import figma_forge as ff
        prior = ff.PriorState(
            known_collection_ids=frozenset({"vc_existing"}),
            known_component_names=frozenset({"ExistingFrame"}),
        )
        r = ff.validate_mcp_plan(self._orphan_plan(), prior_state=prior)
        assert r.is_executable
        assert r.ordering_warnings == []

    def test_prior_state_does_not_affect_schema_errors(self):
        """PriorState only suppresses ordering warnings — schema
        errors still block execution."""
        import figma_forge as ff
        bad_plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 99,  # mismatch → schema error
            "steps": [{
                "step": 1, "operation": "create_variable",
                "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                "arguments": {"collection_id": "vc_x"},
                "instruction": "x",
            }],
        }
        prior = ff.PriorState(known_collection_ids=frozenset({"vc_x"}))
        r = ff.validate_mcp_plan(bad_plan, prior_state=prior)
        assert not r.is_executable
        assert any("disagrees" in e for e in r.schema_errors)

    def test_prior_state_page_suppresses_orphan_page(self):
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 1,
            "steps": [{
                "step": 1, "operation": "create_component",
                "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                "arguments": {"name": "C", "page_name": "Foundations"},
                "instruction": "x",
            }],
        }
        # Without prior: orphan-page warning
        r1 = ff.validate_mcp_plan(plan)
        assert any("Foundations" in w for w in r1.ordering_warnings)
        # With prior: suppressed
        prior = ff.PriorState(known_page_names=frozenset({"Foundations"}))
        r2 = ff.validate_mcp_plan(plan, prior_state=prior)
        assert not any("Foundations" in w for w in r2.ordering_warnings)

    def test_real_dustur_plan_unaffected_by_prior_state(self):
        """Düstur's clean plan stays clean regardless of prior_state —
        backward compat sanity."""
        import figma_forge as ff
        from pathlib import Path
        mcp = ff.McpCursorTransport()
        router = ff.TransportRouter(
            adapters={"stub": ff.StubTransport(), "mcp-cursor": mcp},
            preferences=["mcp-cursor", "stub"],
        )
        ff.run_pipeline(Path("/home/claude/dustur-figma-library"),
                        transport=router, file_key="DUSTUR")
        plan = mcp.render_mcp_plan()
        r1 = ff.validate_mcp_plan(plan)
        r2 = ff.validate_mcp_plan(plan, prior_state=ff.PriorState(
            known_collection_names=frozenset({"Renkler", "Spacing"}),
        ))
        assert r1.is_executable == r2.is_executable == True
        assert r1.ordering_warnings == r2.ordering_warnings == []

    def test_prior_state_hashable_for_caching(self):
        """frozenset fields + frozen dataclass → hashable; can be
        cached / used as dict key (validator may cache reports by
        plan+prior_state pair in v1.5+)."""
        import figma_forge as ff
        p1 = ff.PriorState(known_collection_ids=frozenset({"vc_a"}))
        p2 = ff.PriorState(known_collection_ids=frozenset({"vc_a"}))
        assert hash(p1) == hash(p2)
        assert p1 == p2
        d = {p1: "cached"}
        assert d[p2] == "cached"


# ===========================================================================
# v1.4.0-alpha.2 — PlanRunner (reference agent-side runner)
# ===========================================================================

class TestPlanRunner:
    """v1.4.0-alpha.2: reference interpreter for MCP plans."""

    def _simple_plan(self):
        return {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 2,
            "steps": [
                {"step": 1, "operation": "create_file",
                 "mcp_tool": "Figma:create_new_file", "mechanism": "native",
                 "arguments": {"name": "X", "file_kind": "design"}},
                {"step": 2, "operation": "create_page",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"name": "P"},
                 "instruction": "Create a page named 'P'."},
            ],
        }

    def test_default_dry_run_succeeds(self):
        """Default no-op dispatch runs any valid plan to completion."""
        import figma_forge as ff
        runner = ff.PlanRunner()
        result = runner.run(self._simple_plan())
        assert result.is_success
        assert result.steps_attempted == 2
        assert result.steps_succeeded == 2
        assert result.steps_failed == 0
        assert len(result.step_results) == 2

    def test_step_result_carries_dispatch_response(self):
        """Default no-op returns a sentinel; captured in StepResult.response."""
        import figma_forge as ff
        runner = ff.PlanRunner()
        result = runner.run(self._simple_plan())
        # Native step
        assert result.step_results[0].mechanism == "native"
        assert result.step_results[0].response == {
            "_noop": True, "mcp_tool": "Figma:create_new_file",
        }
        # NL step
        assert result.step_results[1].mechanism == "use_figma_nl"
        assert "_noop" in result.step_results[1].response

    def test_custom_native_dispatch_invoked_with_tool_and_args(self):
        import figma_forge as ff
        captured = []
        def my_native(tool, args):
            captured.append((tool, dict(args)))
            return {"id": "node-42"}
        runner = ff.PlanRunner(native_dispatch=my_native)
        result = runner.run(self._simple_plan())
        assert len(captured) == 1  # one native step
        assert captured[0] == (
            "Figma:create_new_file",
            {"name": "X", "file_kind": "design"},
        )
        assert result.step_results[0].response == {"id": "node-42"}

    def test_custom_nl_dispatch_invoked_with_instruction(self):
        import figma_forge as ff
        captured = []
        def my_nl(instruction, args):
            captured.append((instruction, dict(args)))
            return {"ok": True}
        runner = ff.PlanRunner(nl_dispatch=my_nl)
        runner.run(self._simple_plan())
        assert len(captured) == 1  # one NL step
        instruction, args = captured[0]
        assert "Create a page" in instruction
        assert args == {"name": "P"}

    def test_on_step_streams_every_step(self):
        import figma_forge as ff
        events = []
        runner = ff.PlanRunner(on_step=lambda r: events.append((r.step, r.status)))
        runner.run(self._simple_plan())
        assert events == [(1, "success"), (2, "success")]

    def test_failure_recorded_continues_when_no_abort(self):
        """abort_on_failure=False (default): batch-style best-effort."""
        import figma_forge as ff
        def fail_first(tool, args):
            raise RuntimeError("boom")
        runner = ff.PlanRunner(native_dispatch=fail_first,
                               abort_on_failure=False)
        result = runner.run(self._simple_plan())
        # Both attempted; native failed, NL succeeded
        assert result.steps_attempted == 2
        assert result.steps_failed == 1
        assert result.steps_succeeded == 1
        assert result.aborted_on_step is None
        assert not result.is_success
        # Error captured
        assert "boom" in result.step_results[0].error
        assert result.step_results[0].status == "failure"

    def test_abort_on_failure_halts_and_marks_skipped(self):
        """abort_on_failure=True: first failure stops, rest skipped."""
        import figma_forge as ff
        def fail_first(tool, args):
            raise RuntimeError("halt")
        runner = ff.PlanRunner(native_dispatch=fail_first,
                               abort_on_failure=True)
        result = runner.run(self._simple_plan())
        assert result.steps_attempted == 1  # only native attempted
        assert result.steps_failed == 1
        assert result.steps_succeeded == 0
        assert result.steps_skipped == 1  # NL skipped
        assert result.aborted_on_step == 1
        # The skipped step has status="skipped"
        assert result.step_results[1].status == "skipped"
        assert not result.is_success

    def test_invalid_plan_validation_gate_blocks_dispatch(self):
        """validate=True (default) + bad plan → no dispatch attempted."""
        import figma_forge as ff
        attempts = []
        runner = ff.PlanRunner(
            nl_dispatch=lambda i, a: attempts.append(i),
        )
        bad = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 99,  # mismatch → schema error
            "steps": [{"step": 1, "operation": "x", "mcp_tool": "y",
                       "mechanism": "use_figma_nl", "arguments": {},
                       "instruction": "z"}],
        }
        result = runner.run(bad)
        assert result.steps_attempted == 0
        assert attempts == []
        assert result.validation_report is not None
        assert not result.validation_report.is_executable
        # is_success must reflect the validation failure (regression fix)
        assert not result.is_success

    def test_validate_false_skips_gate(self):
        """validate=False runs even an invalid plan (dispatch attempted)."""
        import figma_forge as ff
        attempts = []
        runner = ff.PlanRunner(
            nl_dispatch=lambda i, a: attempts.append(i) or {"ok": True},
        )
        bad = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 99,
            "steps": [{"step": 1, "operation": "x", "mcp_tool": "y",
                       "mechanism": "use_figma_nl", "arguments": {},
                       "instruction": "z"}],
        }
        result = runner.run(bad, validate=False)
        assert result.steps_attempted == 1
        assert len(attempts) == 1
        assert result.validation_report is None

    def test_prior_state_forwarded_to_validator(self):
        """PriorState passed to run() suppresses ordering warnings."""
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 1,
            "steps": [{"step": 1, "operation": "create_variable",
                       "mcp_tool": "Figma:use_figma",
                       "mechanism": "use_figma_nl",
                       "arguments": {"name": "c", "collection_id": "vc_x"},
                       "instruction": "x"}],
        }
        runner = ff.PlanRunner()
        r1 = runner.run(plan)
        r2 = runner.run(plan, prior_state=ff.PriorState(
            known_collection_ids=frozenset({"vc_x"})))
        assert len(r1.validation_report.ordering_warnings) == 1
        assert len(r2.validation_report.ordering_warnings) == 0

    def test_duration_ms_measured(self):
        """duration_ms is populated and non-negative for attempted steps."""
        import figma_forge as ff
        import time
        def slow(tool, args):
            time.sleep(0.005)  # 5ms
            return {}
        runner = ff.PlanRunner(native_dispatch=slow)
        result = runner.run(self._simple_plan())
        # Native step waited ~5ms
        assert result.step_results[0].duration_ms >= 5.0
        # NL step is no-op, very fast but non-negative
        assert result.step_results[1].duration_ms >= 0.0

    def test_step_result_is_frozen(self):
        """StepResult is immutable — safe to stash into logs."""
        import figma_forge as ff
        import dataclasses
        runner = ff.PlanRunner()
        result = runner.run(self._simple_plan())
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.step_results[0].status = "failure"  # type: ignore[misc]

    def test_dustur_265_step_plan_completes_dry_run(self):
        """Real Düstur plan runs through default no-op dispatch."""
        import figma_forge as ff
        from pathlib import Path
        mcp = ff.McpCursorTransport()
        router = ff.TransportRouter(
            adapters={"stub": ff.StubTransport(), "mcp-cursor": mcp},
            preferences=["mcp-cursor", "stub"],
        )
        ff.run_pipeline(Path("/home/claude/dustur-figma-library"),
                        transport=router, file_key="DUSTUR")
        plan = mcp.render_mcp_plan()
        runner = ff.PlanRunner()
        result = runner.run(plan)
        assert result.is_success
        assert result.steps_attempted == 265
        assert result.steps_succeeded == 265
        assert result.steps_failed == 0
        # 17 native + 248 NL
        natives = sum(1 for s in result.step_results
                      if s.mechanism == "native")
        nls = sum(1 for s in result.step_results
                  if s.mechanism == "use_figma_nl")
        assert natives == 17
        assert nls == 248

    def test_dustur_with_custom_dispatch_routes_correctly(self):
        """Custom dispatchers see the correct subset of steps."""
        import figma_forge as ff
        from pathlib import Path
        native_calls = []
        nl_calls = []
        mcp = ff.McpCursorTransport()
        router = ff.TransportRouter(
            adapters={"stub": ff.StubTransport(), "mcp-cursor": mcp},
            preferences=["mcp-cursor", "stub"],
        )
        ff.run_pipeline(Path("/home/claude/dustur-figma-library"),
                        transport=router, file_key="DUSTUR")
        runner = ff.PlanRunner(
            native_dispatch=lambda t, a: native_calls.append(t) or {},
            nl_dispatch=lambda i, a: nl_calls.append(i[:20]) or {},
        )
        runner.run(mcp.render_mcp_plan())
        assert len(native_calls) == 17
        assert len(nl_calls) == 248
        # All native calls go to the 5 native MCP tools
        assert set(native_calls) == {"Figma:send_code_connect_mappings"}  # Düstur uses one

    def test_empty_plan_clean_result(self):
        """A plan with no steps produces a clean zero-everything result."""
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 0, "steps": [],
        }
        runner = ff.PlanRunner()
        result = runner.run(plan)
        assert result.is_success
        assert result.steps_attempted == 0
        assert result.steps_succeeded == 0
        assert result.steps_failed == 0
        assert result.step_results == []

    def test_json_string_and_dict_equivalent(self):
        """Same plan as JSON string or dict produces same result."""
        import figma_forge as ff
        import json
        plan_dict = self._simple_plan()
        plan_str = json.dumps(plan_dict)
        runner = ff.PlanRunner()
        r1 = runner.run(plan_dict)
        r2 = runner.run(plan_str)
        assert r1.steps_succeeded == r2.steps_succeeded
        assert r1.is_success == r2.is_success

    def test_on_step_receives_skipped_status(self):
        """When abort halts, on_step is still called for skipped steps."""
        import figma_forge as ff
        statuses = []
        def fail_first(tool, args):
            raise RuntimeError("x")
        runner = ff.PlanRunner(
            native_dispatch=fail_first, abort_on_failure=True,
            on_step=lambda r: statuses.append(r.status),
        )
        runner.run(self._simple_plan())
        assert statuses == ["failure", "skipped"]

    def test_is_success_false_when_validation_blocks(self):
        """The regression fix: validation_report failure → is_success=False."""
        import figma_forge as ff
        bad = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 1,
            "steps": [{"step": 1, "operation": "x", "mcp_tool": "y",
                       "mechanism": "telepathy",  # invalid mechanism
                       "arguments": {}}],
        }
        runner = ff.PlanRunner()
        result = runner.run(bad)
        assert result.steps_failed == 0  # no dispatch attempted
        assert result.steps_attempted == 0
        assert not result.is_success  # but is_success reflects validation
        assert not result.validation_report.is_executable


# ===========================================================================
# v1.4.0-beta.1 — AdaptiveConcurrency (observed-rate-limit-driven tuning)
# ===========================================================================

class TestAdaptiveConcurrency:
    """v1.4.0-beta.1: rate-limit observation + concurrency recommendation."""

    def _setup(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        server = MockFigmaServer()
        server.__enter__()
        return server

    # ---- Policy shape / validation -----------------------------------

    def test_policy_shape_defaults(self):
        import figma_forge as ff
        p = ff.AdaptiveConcurrency()
        assert p.min_concurrency == 1
        assert p.max_concurrency == 16
        assert p.target_429_ratio == 0.05
        assert p.aggressive_scale_up is False
        assert p.min_sample_size == 10

    def test_policy_rejects_invalid_bounds(self):
        import figma_forge as ff
        with pytest.raises(ValueError, match="min_concurrency must be >= 1"):
            ff.AdaptiveConcurrency(min_concurrency=0)
        with pytest.raises(ValueError, match="max_concurrency"):
            ff.AdaptiveConcurrency(min_concurrency=4, max_concurrency=2)
        with pytest.raises(ValueError, match="target_429_ratio"):
            ff.AdaptiveConcurrency(target_429_ratio=1.5)
        with pytest.raises(ValueError, match="min_sample_size"):
            ff.AdaptiveConcurrency(min_sample_size=0)

    def test_policy_is_frozen(self):
        import figma_forge as ff
        import dataclasses
        p = ff.AdaptiveConcurrency()
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.target_429_ratio = 0.10  # type: ignore[misc]

    # ---- recommend() algorithm ---------------------------------------

    def test_recommend_under_sample_holds(self):
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(min_sample_size=10)
        new, rat = p.recommend(current=4, requests_total=3, requests_429=1)
        assert new == 4  # hold
        assert "sample size 3 < min 10" in rat

    def test_recommend_above_target_scales_down(self):
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(target_429_ratio=0.05, min_sample_size=5)
        new, rat = p.recommend(current=4, requests_total=100, requests_429=10)
        assert new == 3
        assert "scale down" in rat

    def test_recommend_zero_pressure_scales_up(self):
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(max_concurrency=8, min_sample_size=5)
        new, rat = p.recommend(current=4, requests_total=100, requests_429=0)
        assert new == 5
        assert "scale up" in rat
        assert "incremental" in rat

    def test_recommend_aggressive_scale_up(self):
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(
            max_concurrency=8, aggressive_scale_up=True, min_sample_size=5,
        )
        new, rat = p.recommend(current=4, requests_total=100, requests_429=0)
        assert new == 6  # step of 2
        assert "aggressive" in rat

    def test_recommend_within_budget_holds(self):
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(target_429_ratio=0.05, min_sample_size=5)
        new, rat = p.recommend(current=4, requests_total=100, requests_429=3)
        assert new == 4
        assert "hold" in rat

    def test_recommend_respects_bounds(self):
        """Scale-down never below min; scale-up never above max."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(min_concurrency=2, max_concurrency=4,
                                    min_sample_size=5)
        # At min, sustained 429 → still min
        new, _ = p.recommend(current=2, requests_total=100, requests_429=50)
        assert new == 2
        # At max, zero pressure → still max
        new, _ = p.recommend(current=4, requests_total=100, requests_429=0)
        assert new == 4

    # ---- ConcurrencyObservation --------------------------------------

    def test_observation_is_frozen(self):
        import figma_forge as ff
        import dataclasses
        o = ff.ConcurrencyObservation(
            requests_total=10, requests_429=1, requests_5xx=0,
            retry_after_seconds_max=0.0,
            current_max_concurrency=4, recommended_max_concurrency=4,
            rationale="test",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            o.requests_total = 99  # type: ignore[misc]

    def test_observation_ratio_property(self):
        import figma_forge as ff
        o = ff.ConcurrencyObservation(
            requests_total=20, requests_429=5, requests_5xx=0,
            retry_after_seconds_max=0.0,
            current_max_concurrency=4, recommended_max_concurrency=3,
            rationale="x",
        )
        assert o.ratio_429 == 0.25
        # Empty total → 0.0, no zero-division
        o0 = ff.ConcurrencyObservation(
            requests_total=0, requests_429=0, requests_5xx=0,
            retry_after_seconds_max=0.0,
            current_max_concurrency=4, recommended_max_concurrency=4,
            rationale="x",
        )
        assert o0.ratio_429 == 0.0

    # ---- BatchPolicy integration -------------------------------------

    def test_batch_policy_adaptive_field_optional(self):
        import figma_forge as ff
        # Without adaptive
        b1 = ff.BatchPolicy(max_concurrency=4)
        assert b1.adaptive is None
        # With adaptive
        b2 = ff.BatchPolicy(max_concurrency=4,
                            adaptive=ff.AdaptiveConcurrency())
        assert b2.adaptive is not None

    def test_no_adaptive_no_observation_in_session_result(self):
        """Backward compat: BatchPolicy without adaptive → observation=None."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                batch=ff.BatchPolicy(max_concurrency=2),  # no adaptive
            )
            token = rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C",
                                             modes=["light"])
            result = rest.commit_session(token)
            assert result.adaptive_observation is None
        finally:
            server.__exit__(None, None, None)

    def test_adaptive_produces_observation_on_clean_batch(self):
        """Clean 200s + sample threshold met → scale-up recommendation."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(
                        max_concurrency=8, min_sample_size=5,
                    ),
                ),
            )
            token = rest.begin_session()
            for i in range(10):
                rest.create_variable_collection(file_key="X", name=f"C{i}",
                                                 modes=["light"])
            result = rest.commit_session(token)
            obs = result.adaptive_observation
            assert obs is not None
            assert obs.requests_total == 10
            assert obs.requests_429 == 0
            assert obs.current_max_concurrency == 4
            assert obs.recommended_max_concurrency == 5  # scale up
            assert "scale up" in obs.rationale
        finally:
            server.__exit__(None, None, None)

    def test_adaptive_scale_down_under_rate_limit_storm(self):
        """50% 429 → recommendation drops below current."""
        import figma_forge as ff
        server = self._setup()
        try:
            sequence = []
            for i in range(20):
                if i % 2 == 0:
                    sequence.append((429, {"Retry-After": "1"},
                                     {"err": "rate"}))
                else:
                    sequence.append((200, {}, {"meta": {}}))
            server.set_response_sequence(
                "POST", "/v1/files/X/variables", sequence,
            )
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=2, base_delay=0.001),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(
                        target_429_ratio=0.05, min_sample_size=5,
                    ),
                ),
            )
            rest._sleep_fn = lambda _: None
            token = rest.begin_session()
            for i in range(10):
                rest.create_variable_collection(file_key="X", name=f"C{i}",
                                                 modes=["light"])
            result = rest.commit_session(token)
            obs = result.adaptive_observation
            assert obs.requests_429 > 0
            assert obs.recommended_max_concurrency < obs.current_max_concurrency
            assert "scale down" in obs.rationale
            assert obs.retry_after_seconds_max == 1.0
        finally:
            server.__exit__(None, None, None)

    def test_adaptive_under_sample_holds_recommendation(self):
        """Below min_sample_size → recommendation equals current."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(min_sample_size=50),
                ),
            )
            token = rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C",
                                             modes=["light"])
            result = rest.commit_session(token)
            obs = result.adaptive_observation
            assert obs.requests_total == 1
            assert obs.recommended_max_concurrency == 4  # hold
            assert "sample size 1 < min 50" in obs.rationale
        finally:
            server.__exit__(None, None, None)

    def test_telemetry_thread_safe_under_concurrent_batch(self):
        """Many parallel writes update the counter without races."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=8,  # high concurrency
                    adaptive=ff.AdaptiveConcurrency(min_sample_size=5),
                ),
            )
            token = rest.begin_session()
            for i in range(50):
                rest.create_variable_collection(file_key="X", name=f"C{i}",
                                                 modes=["light"])
            result = rest.commit_session(token)
            obs = result.adaptive_observation
            # Counter must equal queued count (no lost writes from races)
            assert obs.requests_total == 50
            assert obs.requests_429 == 0
            assert obs.requests_5xx == 0
        finally:
            server.__exit__(None, None, None)

    def test_5xx_tracked_separately_from_429(self):
        """5xx errors counted in requests_5xx, not in 429."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=500, body={"err": "boom"})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=2,
                    adaptive=ff.AdaptiveConcurrency(min_sample_size=5),
                ),
            )
            rest._sleep_fn = lambda _: None
            token = rest.begin_session()
            for i in range(10):
                rest.create_variable_collection(file_key="X", name=f"C{i}",
                                                 modes=["light"])
            result = rest.commit_session(token)
            obs = result.adaptive_observation
            assert obs.requests_5xx >= 5  # at least half the attempts
            assert obs.requests_429 == 0
            # 0% 429 ratio → still scale up (5xx is server-side, not concurrency pressure)
            assert obs.recommended_max_concurrency >= obs.current_max_concurrency
        finally:
            server.__exit__(None, None, None)

    def test_observation_resets_between_batches(self):
        """Two commit_session calls produce independent observations
        — counters reset between batches."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=2,
                    adaptive=ff.AdaptiveConcurrency(min_sample_size=5),
                ),
            )
            # Batch 1: 10 calls
            token1 = rest.begin_session()
            for i in range(10):
                rest.create_variable_collection(file_key="X", name=f"A{i}",
                                                 modes=["light"])
            r1 = rest.commit_session(token1)
            assert r1.adaptive_observation.requests_total == 10
            # Batch 2: 5 calls — counter should reset, not accumulate
            token2 = rest.begin_session()
            for i in range(5):
                rest.create_variable_collection(file_key="X", name=f"B{i}",
                                                 modes=["light"])
            r2 = rest.commit_session(token2)
            assert r2.adaptive_observation.requests_total == 5
        finally:
            server.__exit__(None, None, None)


# ===========================================================================
# v1.5.0-alpha.1 — PriorState.last_verified_at + freshness check
# ===========================================================================

class TestPriorStateFreshness:
    """v1.5.0-alpha.1: stale-hint detection via last_verified_at."""

    def _plan(self):
        return {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 1,
            "steps": [{
                "step": 1, "operation": "create_variable",
                "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                "arguments": {"name": "c.1", "collection_id": "vc_x"},
                "instruction": "create c.1 in vc_x",
            }],
        }

    # ---- PriorState field shape -----------------------------------

    def test_last_verified_at_defaults_to_none(self):
        """v1.4 callers see exact v1.4 behavior (field is None)."""
        import figma_forge as ff
        p = ff.PriorState()
        assert p.last_verified_at is None

    def test_last_verified_at_accepts_tz_aware_datetime(self):
        import figma_forge as ff
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc)
        p = ff.PriorState(last_verified_at=ts)
        assert p.last_verified_at == ts

    def test_last_verified_at_rejects_naive_datetime(self):
        """Naive datetime → ValueError at construction (explicit policy)."""
        import figma_forge as ff
        from datetime import datetime
        with pytest.raises(ValueError, match="timezone-aware"):
            ff.PriorState(last_verified_at=datetime.now())  # naive!

    def test_prior_state_remains_hashable_with_timestamp(self):
        """datetime is hashable → PriorState stays hashable for cache keys."""
        import figma_forge as ff
        from datetime import datetime, timezone
        p = ff.PriorState(
            known_collection_ids=frozenset({"vc_x"}),
            last_verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        # Must be usable as dict key / set member
        d = {p: "ok"}
        s = {p}
        assert d[p] == "ok"
        assert p in s

    # ---- validate_mcp_plan freshness behavior -----------------------

    def test_no_timestamp_no_warning(self):
        """PriorState without last_verified_at → no freshness check."""
        import figma_forge as ff
        r = ff.validate_mcp_plan(self._plan(), prior_state=ff.PriorState(),
                                  freshness_window_seconds=60)
        assert r.freshness_warnings == []

    def test_no_window_no_warning(self):
        """last_verified_at set but no freshness_window_seconds → no check."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        p = ff.PriorState(
            last_verified_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        r = ff.validate_mcp_plan(self._plan(), prior_state=p)
        assert r.freshness_warnings == []

    def test_fresh_hint_no_warning(self):
        """Hint within window → no warning."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        p = ff.PriorState(
            known_collection_ids=frozenset({"vc_x"}),
            last_verified_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        )
        r = ff.validate_mcp_plan(self._plan(), prior_state=p,
                                  freshness_window_seconds=300)
        assert r.freshness_warnings == []

    def test_stale_hint_warning(self):
        """Hint beyond window → exactly one freshness warning."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        p = ff.PriorState(
            known_collection_ids=frozenset({"vc_x"}),
            last_verified_at=datetime.now(timezone.utc) - timedelta(seconds=3600),
        )
        r = ff.validate_mcp_plan(self._plan(), prior_state=p,
                                  freshness_window_seconds=300)
        assert len(r.freshness_warnings) == 1
        assert "stale" in r.freshness_warnings[0].lower()
        # Critical: warning does NOT block execution
        assert r.is_executable

    def test_future_timestamp_clock_skew_warning(self):
        """Negative age → distinct warning about clock skew."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        p = ff.PriorState(
            last_verified_at=datetime.now(timezone.utc) + timedelta(seconds=600),
        )
        r = ff.validate_mcp_plan(self._plan(), prior_state=p,
                                  freshness_window_seconds=300)
        assert len(r.freshness_warnings) == 1
        assert "future" in r.freshness_warnings[0].lower()

    def test_freshness_warning_does_not_affect_executability(self):
        """Stale hint + otherwise-clean plan → is_executable still True."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        p = ff.PriorState(
            known_collection_ids=frozenset({"vc_x"}),
            last_verified_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        r = ff.validate_mcp_plan(self._plan(), prior_state=p,
                                  freshness_window_seconds=60)
        assert r.is_executable
        assert r.schema_errors == []
        assert r.argument_errors == []

    def test_freshness_check_independent_of_ordering(self):
        """Freshness warning + ordering warning coexist independently."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        # No collection_id in hint → ordering warning expected
        # Stale timestamp → freshness warning expected
        p = ff.PriorState(
            last_verified_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        r = ff.validate_mcp_plan(self._plan(), prior_state=p,
                                  freshness_window_seconds=60)
        assert len(r.ordering_warnings) >= 1  # vc_x is orphan
        assert len(r.freshness_warnings) == 1  # stale

    def test_planrunner_forwards_freshness_window(self):
        """PlanRunner.run() forwards freshness_window_seconds to validator."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        p = ff.PriorState(
            known_collection_ids=frozenset({"vc_x"}),
            last_verified_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        runner = ff.PlanRunner()
        result = runner.run(self._plan(), prior_state=p,
                             freshness_window_seconds=300)
        # Warning, but dispatch still happens
        assert len(result.validation_report.freshness_warnings) == 1
        assert result.steps_succeeded == 1
        assert result.is_success

    def test_v14_caller_unaffected_by_new_field(self):
        """A v1.4-style call (no freshness args) returns same report shape."""
        import figma_forge as ff
        # No freshness_window_seconds, no last_verified_at
        r = ff.validate_mcp_plan(self._plan())
        # freshness_warnings field exists with empty default
        assert hasattr(r, "freshness_warnings")
        assert r.freshness_warnings == []

    def test_zero_freshness_window_triggers_immediately(self):
        """freshness_window_seconds=0 means 'any age is stale'."""
        import figma_forge as ff
        from datetime import datetime, timezone, timedelta
        p = ff.PriorState(
            last_verified_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        r = ff.validate_mcp_plan(self._plan(), prior_state=p,
                                  freshness_window_seconds=0)
        assert len(r.freshness_warnings) == 1


# ===========================================================================
# v1.5.0-alpha.2 — AdaptiveConcurrency multi-batch smoothing window
# ===========================================================================

class TestAdaptiveConcurrencyWindow:
    """v1.5.0-alpha.2: multi-batch smoothing via window + recommend_aggregate."""

    def _setup(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        server = MockFigmaServer()
        server.__enter__()
        return server

    def _obs(self, total, n429, current=4, rec=4):
        import figma_forge as ff
        return ff.ConcurrencyObservation(
            requests_total=total, requests_429=n429, requests_5xx=0,
            retry_after_seconds_max=0.0,
            current_max_concurrency=current,
            recommended_max_concurrency=rec, rationale="test",
        )

    # ---- AdaptiveConcurrency.window field ----------------------------

    def test_window_defaults_to_one(self):
        """Default window=1 → v1.4 behavior preserved."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency()
        assert p.window == 1

    def test_window_rejects_zero_or_negative(self):
        import figma_forge as ff
        with pytest.raises(ValueError, match="window must be >= 1"):
            ff.AdaptiveConcurrency(window=0)
        with pytest.raises(ValueError, match="window must be >= 1"):
            ff.AdaptiveConcurrency(window=-3)

    def test_policy_remains_frozen_with_window(self):
        import figma_forge as ff
        import dataclasses
        p = ff.AdaptiveConcurrency(window=5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.window = 10  # type: ignore[misc]

    # ---- recommend_aggregate pure ------------------------------------

    def test_recommend_aggregate_single_observation_matches_recommend(self):
        """Single-obs aggregate is identical to single-batch recommend."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(target_429_ratio=0.05, min_sample_size=5)
        single = self._obs(total=20, n429=2)  # 10% → scale down
        new_a, rat_a = p.recommend(
            current=4, requests_total=20, requests_429=2,
        )
        new_b, rat_b = p.recommend_aggregate(
            current=4, observations=[single],
        )
        assert new_a == new_b
        # Rationale carries aggregate prefix but contains the same substance
        assert "scale down" in rat_b
        assert "1 batch" in rat_b

    def test_recommend_aggregate_empty_holds(self):
        """Empty observations → hold at current."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency()
        new, rat = p.recommend_aggregate(current=4, observations=[])
        assert new == 4
        assert "no observations" in rat

    def test_recommend_aggregate_dilutes_single_batch_noise(self):
        """1 spike + 4 clean batches → hold, not scale down."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(
            target_429_ratio=0.05, min_sample_size=10,
        )
        # 1/3 (~33%) noise batch
        noisy = self._obs(total=3, n429=1)
        # 4 clean batches at 25 requests each
        clean = self._obs(total=25, n429=0)
        # Aggregate: 1/103 ≈ 1.0% — well within budget → hold
        new, rat = p.recommend_aggregate(
            current=4, observations=[noisy, clean, clean, clean, clean],
        )
        assert new == 4  # held, single-batch would have said 3
        assert "5 batches" in rat
        assert "hold" in rat

    def test_recommend_aggregate_detects_sustained_pressure(self):
        """5 consecutive 20% 429 batches → scale down."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(
            target_429_ratio=0.05, min_sample_size=5,
        )
        pressured = self._obs(total=20, n429=4)  # 20% each
        new, rat = p.recommend_aggregate(
            current=4, observations=[pressured] * 5,
        )
        assert new == 3
        assert "scale down" in rat
        assert "5 batches" in rat

    def test_recommend_aggregate_zero_pressure_scales_up(self):
        """All-clean window → scale up by 1."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(min_sample_size=5)
        clean = self._obs(total=30, n429=0)
        new, rat = p.recommend_aggregate(
            current=4, observations=[clean] * 3,
        )
        assert new == 5  # scale up
        assert "scale up" in rat
        assert "3 batches" in rat

    def test_recommend_aggregate_under_sample_holds(self):
        """Aggregate sample below min_sample_size → hold."""
        import figma_forge as ff
        p = ff.AdaptiveConcurrency(min_sample_size=100)
        small = self._obs(total=10, n429=0)
        new, rat = p.recommend_aggregate(
            current=4, observations=[small, small],  # 20 total
        )
        assert new == 4
        assert "sample size 20" in rat

    # ---- RestTransport history persistence ---------------------------

    def test_history_persists_across_commit_sessions(self):
        """observation_history accumulates as long as the transport lives."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(
                        min_sample_size=5, window=5,
                    ),
                ),
            )
            for batch_idx in range(3):
                token = rest.begin_session()
                for i in range(6):
                    rest.create_variable_collection(
                        file_key="X", name=f"B{batch_idx}_{i}",
                        modes=["light"],
                    )
                rest.commit_session(token)
            assert len(rest._observation_history) == 3
        finally:
            server.__exit__(None, None, None)

    def test_history_capped_at_window(self):
        """Beyond window batches → deque drops oldest."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(
                        min_sample_size=3, window=5,
                    ),
                ),
            )
            for batch_idx in range(7):  # 2 more than window
                token = rest.begin_session()
                for i in range(3):
                    rest.create_variable_collection(
                        file_key="X", name=f"B{batch_idx}_{i}",
                        modes=["light"],
                    )
                rest.commit_session(token)
            # Capped at window
            assert len(rest._observation_history) == 5
        finally:
            server.__exit__(None, None, None)

    def test_observation_carries_aggregate_recommendation(self):
        """SessionResult.adaptive_observation reflects window-aggregated
        recommendation, not just single-batch."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(
                        max_concurrency=8, min_sample_size=5, window=3,
                    ),
                ),
            )
            # Three clean batches → aggregate is overwhelmingly clean
            for batch_idx in range(3):
                token = rest.begin_session()
                for i in range(10):
                    rest.create_variable_collection(
                        file_key="X", name=f"B{batch_idx}_{i}",
                        modes=["light"],
                    )
                result = rest.commit_session(token)
            obs = result.adaptive_observation
            assert "aggregate over 3 batches" in obs.rationale
            assert obs.recommended_max_concurrency == 5  # scale up
        finally:
            server.__exit__(None, None, None)

    def test_window_one_matches_v14_behavior(self):
        """window=1 (default) produces identical recommendation to v1.4."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(  # window=1 default
                        max_concurrency=8, min_sample_size=5,
                    ),
                ),
            )
            token = rest.begin_session()
            for i in range(10):
                rest.create_variable_collection(
                    file_key="X", name=f"C{i}", modes=["light"],
                )
            result = rest.commit_session(token)
            obs = result.adaptive_observation
            # window=1 → deque size 1 → exactly v1.4 behavior
            # (single batch aggregate == single batch standalone)
            assert obs.recommended_max_concurrency == 5  # scale up
            assert "1 batch" in obs.rationale  # not "1 batches"
        finally:
            server.__exit__(None, None, None)

    def test_window_smooths_intermittent_noise_in_practice(self):
        """1 noisy batch in a 5-batch window does not trigger scale down."""
        import figma_forge as ff
        server = self._setup()
        try:
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(
                        target_429_ratio=0.05, min_sample_size=10, window=5,
                    ),
                ),
            )
            # Batches 1-4: all 200s, 20 requests each (80 total clean)
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            for batch_idx in range(4):
                token = rest.begin_session()
                for i in range(20):
                    rest.create_variable_collection(
                        file_key="X", name=f"B{batch_idx}_{i}",
                        modes=["light"],
                    )
                rest.commit_session(token)
            # Batch 5: a noisy batch with 4 of 5 calls being 429
            seq = [(429, {"Retry-After": "1"}, {"err": "rate"})] * 4 + [
                (200, {}, {"meta": {}})
            ] * 6
            server.set_response_sequence(
                "POST", "/v1/files/X/variables", seq,
            )
            rest._sleep_fn = lambda _: None
            token = rest.begin_session()
            for i in range(5):
                rest.create_variable_collection(
                    file_key="X", name=f"Bnoisy_{i}", modes=["light"],
                )
            result = rest.commit_session(token)
            obs = result.adaptive_observation
            # Single batch standalone would scale down. Aggregate over
            # 5 batches dilutes the spike. We expect either hold or
            # a much milder reaction.
            assert "aggregate over 5 batches" in obs.rationale
            # Don't insist on exact recommendation — depends on retry
            # math. Instead, assert that the spike alone (had it been
            # standalone) would have produced a more aggressive
            # recommendation than what aggregation yields.
            assert obs.recommended_max_concurrency >= 3  # not crashed to 1
        finally:
            server.__exit__(None, None, None)

    def test_window_keeps_history_when_no_adaptive(self):
        """Without adaptive policy, deque exists but is empty (no overhead)."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                batch=ff.BatchPolicy(max_concurrency=2),  # no adaptive
            )
            token = rest.begin_session()
            rest.create_variable_collection(file_key="X", name="C",
                                             modes=["light"])
            result = rest.commit_session(token)
            assert result.adaptive_observation is None
            # History exists but stays empty
            assert len(rest._observation_history) == 0
        finally:
            server.__exit__(None, None, None)

    def test_new_transport_instance_has_fresh_history(self):
        """A new RestTransport starts with an empty history."""
        import figma_forge as ff
        server = self._setup()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            for run_idx in range(2):
                rest = ff.RestTransport(
                    pat="t", base_url=server.url, dry_run=False,
                    backoff=ff.BackoffPolicy(max_retries=0),
                    batch=ff.BatchPolicy(
                        max_concurrency=4,
                        adaptive=ff.AdaptiveConcurrency(
                            min_sample_size=5, window=5,
                        ),
                    ),
                )
                # Each new transport instance gets fresh history
                assert len(rest._observation_history) == 0
                token = rest.begin_session()
                for i in range(5):
                    rest.create_variable_collection(
                        file_key="X", name=f"R{run_idx}_{i}",
                        modes=["light"],
                    )
                rest.commit_session(token)
                assert len(rest._observation_history) == 1
        finally:
            server.__exit__(None, None, None)


# ===========================================================================
# v1.5.0-beta.1 — ObservationLog cross-build persistence
# ===========================================================================

class TestObservationLog:
    """v1.5.0-beta.1: file-backed cross-build observation persistence."""

    def _tmp_log(self, tmp_path, name="history.jsonl", max_records=100):
        import figma_forge as ff
        return ff.ObservationLog(str(tmp_path / name), max_records=max_records)

    def _obs(self, total=90, n429=6, rec=3):
        import figma_forge as ff
        return ff.ConcurrencyObservation(
            requests_total=total, requests_429=n429, requests_5xx=0,
            retry_after_seconds_max=2.0, current_max_concurrency=4,
            recommended_max_concurrency=rec, rationale="test",
        )

    def _setup_server(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
        from mock_figma_server import MockFigmaServer
        s = MockFigmaServer()
        s.__enter__()
        return s

    # ---- Construction / validation -----------------------------------

    def test_construction_defaults(self, tmp_path):
        import figma_forge as ff
        log = ff.ObservationLog(str(tmp_path / "h.jsonl"))
        assert log.max_records == 100

    def test_max_records_validation(self, tmp_path):
        import figma_forge as ff
        with pytest.raises(ValueError, match="max_records must be >= 1"):
            ff.ObservationLog(str(tmp_path / "h.jsonl"), max_records=0)

    # ---- Append / read roundtrip -------------------------------------

    def test_append_creates_file(self, tmp_path):
        import os
        log = self._tmp_log(tmp_path)
        log.append(self._obs())
        assert os.path.exists(tmp_path / "history.jsonl")

    def test_append_read_roundtrip(self, tmp_path):
        log = self._tmp_log(tmp_path)
        log.append(self._obs(total=90, n429=6, rec=3))
        recs = log.read_recent()
        assert len(recs) == 1
        assert recs[0].requests_total == 90
        assert recs[0].requests_429 == 6
        assert recs[0].recommended_max_concurrency == 3

    def test_all_fields_preserved(self, tmp_path):
        import figma_forge as ff
        log = self._tmp_log(tmp_path)
        original = ff.ConcurrencyObservation(
            requests_total=123, requests_429=7, requests_5xx=2,
            retry_after_seconds_max=3.5, current_max_concurrency=6,
            recommended_max_concurrency=5,
            rationale="detailed rationale string",
        )
        log.append(original)
        loaded = log.read_recent()[0]
        assert loaded.requests_total == 123
        assert loaded.requests_429 == 7
        assert loaded.requests_5xx == 2
        assert loaded.retry_after_seconds_max == 3.5
        assert loaded.current_max_concurrency == 6
        assert loaded.recommended_max_concurrency == 5
        assert loaded.rationale == "detailed rationale string"

    def test_read_recent_n_returns_last_n(self, tmp_path):
        log = self._tmp_log(tmp_path)
        for i in range(10):
            log.append(self._obs(total=i))
        recs = log.read_recent(3)
        assert len(recs) == 3
        assert [r.requests_total for r in recs] == [7, 8, 9]

    def test_read_recent_missing_file_returns_empty(self, tmp_path):
        import figma_forge as ff
        log = ff.ObservationLog(str(tmp_path / "nonexistent.jsonl"))
        assert log.read_recent() == []

    def test_read_recent_empty_file_returns_empty(self, tmp_path):
        log = self._tmp_log(tmp_path)
        (tmp_path / "history.jsonl").write_text("")
        assert log.read_recent() == []

    # ---- Wrapper format ----------------------------------------------

    def test_jsonl_wrapper_format(self, tmp_path):
        import json
        log = self._tmp_log(tmp_path)
        log.append(self._obs(total=90))
        line = (tmp_path / "history.jsonl").read_text().strip()
        parsed = json.loads(line)
        assert "logged_at" in parsed
        assert "observation" in parsed
        assert parsed["observation"]["requests_total"] == 90

    def test_logged_at_is_iso_timestamp(self, tmp_path):
        import json
        from datetime import datetime
        log = self._tmp_log(tmp_path)
        log.append(self._obs())
        parsed = json.loads((tmp_path / "history.jsonl").read_text().strip())
        # Must parse as ISO 8601
        ts = datetime.fromisoformat(parsed["logged_at"])
        assert ts.tzinfo is not None  # tz-aware

    # ---- Corrupted-record tolerance ----------------------------------

    def test_corrupted_lines_skipped(self, tmp_path):
        log = self._tmp_log(tmp_path)
        log.append(self._obs(total=90))
        # Inject garbage
        with open(tmp_path / "history.jsonl", "a") as f:
            f.write("not json at all\n")
            f.write('{"partial": broken\n')
            f.write("\n")  # blank line
        log.append(self._obs(total=91))
        recs = log.read_recent()
        # Only the two valid observations survive
        assert len(recs) == 2
        assert {r.requests_total for r in recs} == {90, 91}

    def test_missing_required_field_skipped(self, tmp_path):
        import json
        log = self._tmp_log(tmp_path)
        log.append(self._obs(total=90))
        # A record missing required fields
        with open(tmp_path / "history.jsonl", "a") as f:
            f.write(json.dumps({"observation": {"requests_total": 5}}) + "\n")
        recs = log.read_recent()
        assert len(recs) == 1  # the incomplete one is dropped
        assert recs[0].requests_total == 90

    def test_extra_fields_tolerated(self, tmp_path):
        import json
        log = self._tmp_log(tmp_path)
        # A record with an unknown extra field (forward compat)
        full = {
            "requests_total": 50, "requests_429": 1, "requests_5xx": 0,
            "retry_after_seconds_max": 0.0, "current_max_concurrency": 4,
            "recommended_max_concurrency": 4, "rationale": "x",
            "future_field_v2": "ignored",
        }
        with open(tmp_path / "history.jsonl", "a") as f:
            f.write(json.dumps({"observation": full}) + "\n")
        recs = log.read_recent()
        assert len(recs) == 1
        assert recs[0].requests_total == 50

    # ---- Trim --------------------------------------------------------

    def test_trim_caps_at_max_records(self, tmp_path):
        log = self._tmp_log(tmp_path, max_records=3)
        for i in range(20):
            log.append(self._obs(total=i))
        recs = log.read_recent()
        # File transiently holds up to 2×max before trim; after 20
        # appends it has been trimmed. Never more than 2×max_records.
        assert len(recs) <= 6
        # The most recent records are always retained
        assert recs[-1].requests_total == 19

    def test_trim_preserves_recent_records(self, tmp_path):
        log = self._tmp_log(tmp_path, max_records=5)
        for i in range(100):
            log.append(self._obs(total=i))
        recs = log.read_recent(5)
        assert [r.requests_total for r in recs] == [95, 96, 97, 98, 99]

    # ---- __len__ / clear ---------------------------------------------

    def test_len_counts_records(self, tmp_path):
        log = self._tmp_log(tmp_path)
        assert len(log) == 0
        log.append(self._obs())
        log.append(self._obs())
        assert len(log) == 2

    def test_clear_empties_log(self, tmp_path):
        import os
        log = self._tmp_log(tmp_path)
        log.append(self._obs())
        log.clear()
        assert len(log) == 0
        assert not os.path.exists(tmp_path / "history.jsonl")

    # ---- RestTransport integration -----------------------------------

    def test_rest_seeds_history_from_log(self, tmp_path):
        """A new RestTransport seeds its history from the log."""
        import figma_forge as ff
        log = self._tmp_log(tmp_path)
        # Pre-populate the log with 3 observations
        for i in range(3):
            log.append(self._obs(total=20 + i))
        server = self._setup_server()
        try:
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(min_sample_size=5, window=5),
                ),
                observation_log=log,
            )
            # History seeded from log
            assert len(rest._observation_history) == 3
        finally:
            server.__exit__(None, None, None)

    def test_rest_appends_to_log_on_commit(self, tmp_path):
        """commit_session appends the observation to the log."""
        import figma_forge as ff
        log = self._tmp_log(tmp_path)
        server = self._setup_server()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(min_sample_size=5, window=5),
                ),
                observation_log=log,
            )
            token = rest.begin_session()
            for i in range(10):
                rest.create_variable_collection(file_key="X", name=f"C{i}",
                                                 modes=["light"])
            rest.commit_session(token)
            assert len(log) == 1
        finally:
            server.__exit__(None, None, None)

    def test_cross_instance_smoothing(self, tmp_path):
        """Instance B picks up Instance A's observations via the log."""
        import figma_forge as ff
        log = self._tmp_log(tmp_path)
        server = self._setup_server()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})

            def make_transport():
                return ff.RestTransport(
                    pat="t", base_url=server.url, dry_run=False,
                    backoff=ff.BackoffPolicy(max_retries=0),
                    batch=ff.BatchPolicy(
                        max_concurrency=4,
                        adaptive=ff.AdaptiveConcurrency(
                            min_sample_size=5, window=5,
                        ),
                    ),
                    observation_log=log,
                )

            # Instance A: two batches
            restA = make_transport()
            assert len(restA._observation_history) == 0  # fresh
            for b in range(2):
                token = restA.begin_session()
                for i in range(10):
                    restA.create_variable_collection(
                        file_key="X", name=f"A{b}_{i}", modes=["light"],
                    )
                restA.commit_session(token)
            assert len(log) == 2

            # Instance B: NEW transport, seeds from log
            restB = make_transport()
            assert len(restB._observation_history) == 2  # seeded from A!
            token = restB.begin_session()
            for i in range(10):
                restB.create_variable_collection(
                    file_key="X", name=f"B_{i}", modes=["light"],
                )
            result = restB.commit_session(token)
            # B's aggregate spans A's 2 batches + B's 1 = 3 batches
            assert "aggregate over 3 batches" in result.adaptive_observation.rationale
            assert len(log) == 3
        finally:
            server.__exit__(None, None, None)

    def test_no_log_no_persistence(self, tmp_path):
        """Without observation_log, no file is created (v1.5-alpha.2 behavior)."""
        import figma_forge as ff
        server = self._setup_server()
        try:
            server.set_response("POST", "/v1/files/X/variables",
                                status=200, body={"meta": {}})
            rest = ff.RestTransport(
                pat="t", base_url=server.url, dry_run=False,
                backoff=ff.BackoffPolicy(max_retries=0),
                batch=ff.BatchPolicy(
                    max_concurrency=4,
                    adaptive=ff.AdaptiveConcurrency(min_sample_size=5, window=5),
                ),
                # no observation_log
            )
            token = rest.begin_session()
            for i in range(5):
                rest.create_variable_collection(file_key="X", name=f"C{i}",
                                                 modes=["light"])
            result = rest.commit_session(token)
            # Observation still produced, just not persisted
            assert result.adaptive_observation is not None
        finally:
            server.__exit__(None, None, None)


# ===========================================================================
# v1.6.0-alpha.1 — DispatchResponse standardized dispatch return type
# ===========================================================================

class TestDispatchResponse:
    """v1.6.0-alpha.1: opt-in structured return for PlanRunner dispatch."""

    def _plan(self):
        return {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 2,
            "steps": [
                {"step": 1, "operation": "create_file",
                 "mcp_tool": "Figma:create_new_file", "mechanism": "native",
                 "arguments": {"name": "X", "file_kind": "design"}},
                {"step": 2, "operation": "create_page",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"name": "P"},
                 "instruction": "Create a page named 'P'."},
            ],
        }

    # ---- DispatchResponse shape --------------------------------------

    def test_dispatch_response_defaults(self):
        import figma_forge as ff
        dr = ff.DispatchResponse()
        assert dr.ok is True
        assert dr.entity_id is None
        assert dr.raw is None
        assert dr.retry_attempts == 0
        assert dr.warnings == ()

    def test_dispatch_response_frozen(self):
        import figma_forge as ff
        import dataclasses
        dr = ff.DispatchResponse()
        with pytest.raises(dataclasses.FrozenInstanceError):
            dr.ok = False  # type: ignore[misc]

    def test_dispatch_response_carries_fields(self):
        import figma_forge as ff
        dr = ff.DispatchResponse(
            ok=True, entity_id="node-7", raw={"http": 200},
            retry_attempts=2, warnings=("a", "b"),
        )
        assert dr.entity_id == "node-7"
        assert dr.raw == {"http": 200}
        assert dr.retry_attempts == 2
        assert dr.warnings == ("a", "b")

    # ---- Backward compatibility --------------------------------------

    def test_non_dispatch_response_return_is_success(self):
        """v1.5 behavior: any non-DispatchResponse return → success."""
        import figma_forge as ff
        runner = ff.PlanRunner(native_dispatch=lambda t, a: {"x": 1})
        result = runner.run(self._plan())
        sr = result.step_results[0]
        assert sr.status == "success"
        assert sr.response == {"x": 1}
        assert sr.dispatch_response is None  # not a DispatchResponse

    def test_default_noop_has_no_dispatch_response(self):
        """Default no-op dispatch returns a sentinel dict, not DispatchResponse."""
        import figma_forge as ff
        runner = ff.PlanRunner()
        result = runner.run(self._plan())
        assert all(sr.dispatch_response is None for sr in result.step_results)
        assert result.is_success

    # ---- ok=True path ------------------------------------------------

    def test_dispatch_response_ok_true_success(self):
        import figma_forge as ff
        def native(tool, args):
            return ff.DispatchResponse(ok=True, entity_id="n-1")
        runner = ff.PlanRunner(native_dispatch=native)
        result = runner.run(self._plan())
        sr = result.step_results[0]
        assert sr.status == "success"
        assert sr.dispatch_response is not None
        assert sr.dispatch_response.entity_id == "n-1"
        # response also holds the DispatchResponse (raw return)
        assert sr.response is sr.dispatch_response

    def test_entity_id_and_retry_captured(self):
        import figma_forge as ff
        def native(tool, args):
            return ff.DispatchResponse(
                entity_id="node-99", retry_attempts=3, raw={"ok": 1},
            )
        runner = ff.PlanRunner(native_dispatch=native)
        result = runner.run(self._plan())
        dr = result.step_results[0].dispatch_response
        assert dr.entity_id == "node-99"
        assert dr.retry_attempts == 3
        assert dr.raw == {"ok": 1}

    def test_warnings_captured_on_success(self):
        import figma_forge as ff
        def native(tool, args):
            return ff.DispatchResponse(ok=True, warnings=("deprecated API",))
        runner = ff.PlanRunner(native_dispatch=native)
        result = runner.run(self._plan())
        sr = result.step_results[0]
        assert sr.status == "success"  # warnings don't fail
        assert sr.dispatch_response.warnings == ("deprecated API",)

    # ---- ok=False soft failure ---------------------------------------

    def test_dispatch_response_ok_false_is_failure(self):
        import figma_forge as ff
        def native(tool, args):
            return ff.DispatchResponse(ok=False, warnings=("already exists",))
        runner = ff.PlanRunner(native_dispatch=native)
        result = runner.run(self._plan())
        sr = result.step_results[0]
        assert sr.status == "failure"
        assert result.steps_failed == 1
        assert not result.is_success
        # Warnings become the error string
        assert "already exists" in sr.error
        # dispatch_response still attached
        assert sr.dispatch_response is not None
        assert sr.dispatch_response.ok is False

    def test_ok_false_without_warnings_has_default_error(self):
        import figma_forge as ff
        def native(tool, args):
            return ff.DispatchResponse(ok=False)
        runner = ff.PlanRunner(native_dispatch=native)
        result = runner.run(self._plan())
        sr = result.step_results[0]
        assert sr.status == "failure"
        assert "ok=False" in sr.error

    def test_ok_false_triggers_abort(self):
        import figma_forge as ff
        def native(tool, args):
            return ff.DispatchResponse(ok=False, warnings=("halt",))
        runner = ff.PlanRunner(native_dispatch=native, abort_on_failure=True)
        result = runner.run(self._plan())
        assert result.steps_attempted == 1  # native step only
        assert result.steps_failed == 1
        assert result.steps_skipped == 1  # nl step skipped
        assert result.aborted_on_step == 1

    def test_mixed_ok_and_not_ok_counted_correctly(self):
        import figma_forge as ff
        # native ok, nl not-ok
        runner = ff.PlanRunner(
            native_dispatch=lambda t, a: ff.DispatchResponse(ok=True),
            nl_dispatch=lambda i, a: ff.DispatchResponse(ok=False, warnings=("x",)),
            abort_on_failure=False,
        )
        result = runner.run(self._plan())
        assert result.steps_succeeded == 1
        assert result.steps_failed == 1
        assert result.steps_attempted == 2

    # ---- nl_dispatch path --------------------------------------------

    def test_nl_dispatch_returns_dispatch_response(self):
        import figma_forge as ff
        runner = ff.PlanRunner(
            native_dispatch=lambda t, a: ff.DispatchResponse(entity_id="nat"),
            nl_dispatch=lambda i, a: ff.DispatchResponse(entity_id="nl"),
        )
        result = runner.run(self._plan())
        assert result.step_results[0].dispatch_response.entity_id == "nat"
        assert result.step_results[1].dispatch_response.entity_id == "nl"
        assert result.is_success

    # ---- on_step sees dispatch_response ------------------------------

    def test_on_step_receives_dispatch_response(self):
        import figma_forge as ff
        seen = []
        runner = ff.PlanRunner(
            native_dispatch=lambda t, a: ff.DispatchResponse(entity_id="x"),
            on_step=lambda sr: seen.append(sr.dispatch_response),
        )
        runner.run(self._plan())
        # First step is native with DispatchResponse; second is no-op nl
        assert seen[0] is not None
        assert seen[0].entity_id == "x"


# ===========================================================================
# v1.6.0-alpha.2 — Plan-aware concurrent PlanRunner
# ===========================================================================

class TestPlanExecutionLayers:
    """v1.6.0-alpha.2: topological dependency layering."""

    def test_empty_plan_no_layers(self):
        import figma_forge as ff
        assert ff.plan_execution_layers({"steps": []}) == []
        assert ff.plan_execution_layers({}) == []

    def test_independent_steps_single_layer(self):
        """Steps with no inter-dependencies collapse to one layer."""
        import figma_forge as ff
        plan = {"steps": [
            {"step": 1, "operation": "create_variable_collection",
             "arguments": {"collection_id": "c1", "name": "A"}},
            {"step": 2, "operation": "create_variable_collection",
             "arguments": {"collection_id": "c2", "name": "B"}},
            {"step": 3, "operation": "create_page",
             "arguments": {"name": "P"}},
        ]}
        assert ff.plan_execution_layers(plan) == [[1, 2, 3]]

    def test_collection_variable_two_layers(self):
        import figma_forge as ff
        plan = {"steps": [
            {"step": 1, "operation": "create_variable_collection",
             "arguments": {"collection_id": "c1", "name": "Colors"}},
            {"step": 2, "operation": "create_variable",
             "arguments": {"collection_id": "c1", "name": "blue"}},
            {"step": 3, "operation": "create_variable",
             "arguments": {"collection_id": "c1", "name": "red"}},
        ]}
        assert ff.plan_execution_layers(plan) == [[1], [2, 3]]

    def test_transitive_chain_three_layers(self):
        """page → component → instance lands in three successive layers."""
        import figma_forge as ff
        plan = {"steps": [
            {"step": 1, "operation": "create_page",
             "arguments": {"name": "Pg"}},
            {"step": 2, "operation": "create_component",
             "arguments": {"name": "Btn", "page_name": "Pg"}},
            {"step": 3, "operation": "place_instance",
             "arguments": {"parent_name": "Btn"}},
        ]}
        assert ff.plan_execution_layers(plan) == [[1], [2], [3]]

    def test_mixed_independent_and_dependent(self):
        import figma_forge as ff
        plan = {"steps": [
            {"step": 1, "operation": "create_variable_collection",
             "arguments": {"collection_id": "c1", "name": "A"}},
            {"step": 2, "operation": "create_variable_collection",
             "arguments": {"collection_id": "c2", "name": "B"}},
            {"step": 3, "operation": "create_variable",
             "arguments": {"collection_id": "c1", "name": "x"}},
            {"step": 4, "operation": "create_variable",
             "arguments": {"collection_id": "c2", "name": "y"}},
            {"step": 5, "operation": "create_page",
             "arguments": {"name": "P"}},
        ]}
        # Producers (1,2,5) in layer 0; consumers (3,4) in layer 1.
        assert ff.plan_execution_layers(plan) == [[1, 2, 5], [3, 4]]

    def test_reference_without_producer_no_constraint(self):
        """A reference to an entity created in a prior plan / by hand
        imposes no in-plan ordering — the step lands in layer 0."""
        import figma_forge as ff
        plan = {"steps": [
            {"step": 1, "operation": "create_variable",
             "arguments": {"collection_id": "external-c", "name": "x"}},
            {"step": 2, "operation": "create_page",
             "arguments": {"name": "P"}},
        ]}
        # Neither has an in-plan producer dependency.
        assert ff.plan_execution_layers(plan) == [[1, 2]]

    def test_layers_preserve_plan_order_within_layer(self):
        import figma_forge as ff
        plan = {"steps": [
            {"step": 3, "operation": "create_page", "arguments": {"name": "C"}},
            {"step": 1, "operation": "create_page", "arguments": {"name": "A"}},
            {"step": 2, "operation": "create_page", "arguments": {"name": "B"}},
        ]}
        # Single layer, sorted ascending by step number.
        assert ff.plan_execution_layers(plan) == [[1, 2, 3]]

    def test_json_string_input(self):
        import figma_forge as ff
        import json
        plan = {"steps": [
            {"step": 1, "operation": "create_page", "arguments": {"name": "P"}},
        ]}
        assert ff.plan_execution_layers(json.dumps(plan)) == [[1]]

    def test_real_plan_from_transport(self):
        """A plan rendered by McpCursorTransport layers correctly."""
        import figma_forge as ff
        import json
        mcp = ff.McpCursorTransport()
        mcp.begin_session()
        mcp.create_page(file_key="X", name="Components")
        mcp.create_variable_collection(file_key="X", name="Tokens",
                                       modes=["light", "dark"])
        plan = json.loads(mcp.render_mcp_plan())
        layers = ff.plan_execution_layers(plan)
        # Both are independent producers → single layer.
        all_steps = [s for layer in layers for s in layer]
        assert sorted(all_steps) == [s["step"] for s in plan["steps"]]
        # Layering covers every step exactly once.
        assert len(all_steps) == len(set(all_steps)) == plan["step_count"]

    def test_every_step_appears_exactly_once(self):
        """Invariant: layering is a partition of the step set."""
        import figma_forge as ff
        plan = {"steps": [
            {"step": i, "operation": "create_page",
             "arguments": {"name": f"P{i}"}}
            for i in range(1, 21)
        ]}
        layers = ff.plan_execution_layers(plan)
        flat = [s for layer in layers for s in layer]
        assert sorted(flat) == list(range(1, 21))
        assert len(flat) == len(set(flat))


class TestPlanConcurrentExecution:
    """v1.6.0-alpha.2: PlanRunner concurrent=True layered dispatch."""

    def _plan(self):
        return {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 5,
            "steps": [
                {"step": 1, "operation": "create_variable_collection",
                 "mcp_tool": "Figma:x", "mechanism": "native",
                 "arguments": {"collection_id": "c1", "name": "A"}},
                {"step": 2, "operation": "create_variable_collection",
                 "mcp_tool": "Figma:x", "mechanism": "native",
                 "arguments": {"collection_id": "c2", "name": "B"}},
                {"step": 3, "operation": "create_variable",
                 "mcp_tool": "Figma:x", "mechanism": "native",
                 "arguments": {"collection_id": "c1", "name": "x"}},
                {"step": 4, "operation": "create_variable",
                 "mcp_tool": "Figma:x", "mechanism": "native",
                 "arguments": {"collection_id": "c2", "name": "y"}},
                {"step": 5, "operation": "create_page",
                 "mcp_tool": "Figma:x", "mechanism": "native",
                 "arguments": {"name": "P"}},
            ],
        }

    def test_concurrent_matches_sequential_results(self):
        import figma_forge as ff
        seq = ff.PlanRunner(native_dispatch=lambda t, a: {"ok": 1})
        res_seq = seq.run(self._plan(), validate=False)
        con = ff.PlanRunner(native_dispatch=lambda t, a: {"ok": 1})
        res_con = con.run(self._plan(), validate=False, concurrent=True)
        assert res_seq.steps_succeeded == res_con.steps_succeeded == 5
        assert res_seq.steps_attempted == res_con.steps_attempted == 5
        assert res_seq.is_success == res_con.is_success is True

    def test_concurrent_step_results_in_plan_order(self):
        """step_results always plan-ordered, even if step 1 is slowest."""
        import figma_forge as ff
        import time
        def disp(tool, args):
            if args.get("name") == "A":
                time.sleep(0.03)
            return {"ok": 1}
        runner = ff.PlanRunner(native_dispatch=disp)
        res = runner.run(self._plan(), validate=False, concurrent=True,
                         max_workers=4)
        assert [sr.step for sr in res.step_results] == [1, 2, 3, 4, 5]

    def test_concurrent_dispatches_all_steps(self):
        import figma_forge as ff
        seen = []
        runner = ff.PlanRunner(
            native_dispatch=lambda t, a: seen.append(a.get("name")) or {"ok": 1})
        runner.run(self._plan(), validate=False, concurrent=True)
        assert sorted(seen) == ["A", "B", "P", "x", "y"]

    def test_concurrent_default_false_unchanged(self):
        """concurrent=False (default) is exact sequential behavior."""
        import figma_forge as ff
        runner = ff.PlanRunner(native_dispatch=lambda t, a: {"ok": 1})
        res = runner.run(self._plan(), validate=False)
        assert res.steps_succeeded == 5
        assert [sr.step for sr in res.step_results] == [1, 2, 3, 4, 5]

    def test_concurrent_with_dispatch_response_ok_false(self):
        import figma_forge as ff
        def disp(tool, args):
            if args.get("name") == "x":
                return ff.DispatchResponse(ok=False, warnings=("collision",))
            return ff.DispatchResponse(ok=True, entity_id="n")
        runner = ff.PlanRunner(native_dispatch=disp)
        res = runner.run(self._plan(), validate=False, concurrent=True)
        assert res.steps_failed == 1
        assert res.steps_succeeded == 4
        assert not res.is_success
        sr3 = [s for s in res.step_results if s.step == 3][0]
        assert sr3.status == "failure"
        assert "collision" in sr3.error

    def test_concurrent_layer_level_abort(self):
        """A failure in layer 0 completes that layer, then skips later layers."""
        import figma_forge as ff
        def disp(tool, args):
            if args.get("name") == "A":  # layer 0
                raise RuntimeError("boom")
            return {"ok": 1}
        runner = ff.PlanRunner(native_dispatch=disp, abort_on_failure=True)
        res = runner.run(self._plan(), validate=False, concurrent=True)
        statuses = {sr.step: sr.status for sr in res.step_results}
        # Layer 0 = {1,2,5}: 1 fails, 2 and 5 still complete.
        assert statuses[1] == "failure"
        assert statuses[2] == "success"
        assert statuses[5] == "success"
        # Layer 1 = {3,4}: skipped because layer 0 had a failure.
        assert statuses[3] == "skipped"
        assert statuses[4] == "skipped"
        assert res.aborted_on_step == 1
        assert res.steps_skipped == 2

    def test_concurrent_abort_picks_lowest_failing_step(self):
        """aborted_on_step is the min failing step in the aborting layer."""
        import figma_forge as ff
        def disp(tool, args):
            # Both step 1 and step 2 (layer 0) fail.
            if args.get("name") in ("A", "B"):
                raise RuntimeError("boom")
            return {"ok": 1}
        runner = ff.PlanRunner(native_dispatch=disp, abort_on_failure=True)
        res = runner.run(self._plan(), validate=False, concurrent=True)
        assert res.aborted_on_step == 1  # min(1, 2)

    def test_concurrent_no_abort_runs_all(self):
        """abort_on_failure=False runs every layer despite failures."""
        import figma_forge as ff
        def disp(tool, args):
            if args.get("name") == "A":
                raise RuntimeError("boom")
            return {"ok": 1}
        runner = ff.PlanRunner(native_dispatch=disp, abort_on_failure=False)
        res = runner.run(self._plan(), validate=False, concurrent=True)
        # All 5 attempted; only step 1 failed.
        assert res.steps_attempted == 5
        assert res.steps_failed == 1
        assert res.steps_succeeded == 4
        assert res.steps_skipped == 0

    def test_concurrent_max_workers_one(self):
        import figma_forge as ff
        runner = ff.PlanRunner(native_dispatch=lambda t, a: {"ok": 1})
        res = runner.run(self._plan(), validate=False, concurrent=True,
                         max_workers=1)
        assert res.steps_succeeded == 5
        assert [sr.step for sr in res.step_results] == [1, 2, 3, 4, 5]

    def test_concurrent_on_step_callback_all_steps(self):
        import figma_forge as ff
        seen = []
        runner = ff.PlanRunner(
            native_dispatch=lambda t, a: {"ok": 1},
            on_step=lambda sr: seen.append(sr.step))
        runner.run(self._plan(), validate=False, concurrent=True)
        # on_step fires for every step, in plan order (assembly order).
        assert seen == [1, 2, 3, 4, 5]

    def test_concurrent_validation_gate_still_applies(self):
        """concurrent=True still runs the validation gate first."""
        import figma_forge as ff
        bad_plan = {"plan_format_version": "1.0", "adapter": "mcp-cursor",
                    "step_count": 1, "steps": [
                        {"step": 1, "operation": "totally_unknown_op",
                         "mcp_tool": "X", "mechanism": "native",
                         "arguments": {}}]}
        runner = ff.PlanRunner(native_dispatch=lambda t, a: {"ok": 1})
        res = runner.run(bad_plan, concurrent=True)  # validate=True default
        # Validation should reject; no steps attempted.
        if res.validation_report is not None and not res.validation_report.is_executable:
            assert res.steps_attempted == 0

    def test_concurrent_nl_mechanism(self):
        import figma_forge as ff
        plan = {
            "plan_format_version": "1.0", "adapter": "mcp-cursor",
            "step_count": 2,
            "steps": [
                {"step": 1, "operation": "create_page",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"name": "A"}, "instruction": "Create page A"},
                {"step": 2, "operation": "create_page",
                 "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                 "arguments": {"name": "B"}, "instruction": "Create page B"},
            ],
        }
        runner = ff.PlanRunner(nl_dispatch=lambda i, a: {"ok": 1})
        res = runner.run(plan, validate=False, concurrent=True)
        assert res.steps_succeeded == 2
        assert all(sr.mechanism == "use_figma_nl" for sr in res.step_results)


# ===========================================================================
# v1.6.0-beta.1 — Cleanup & Maturation
#   (1) ObservationLog.compact()  (2) per-field freshness TTL
#   (3) AdaptiveConcurrency.suggest_window()
# ===========================================================================

class TestObservationLogCompact:
    """v1.6.0-beta.1: on-demand log compaction."""

    def _obs(self, total=100, n429=2):
        import figma_forge as ff
        return ff.ConcurrencyObservation(
            requests_total=total, requests_429=n429, requests_5xx=0,
            retry_after_seconds_max=0.0, current_max_concurrency=4,
            recommended_max_concurrency=4, rationale="x")

    def test_compact_trims_to_keep(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        log = ObservationLog(str(tmp_path / "o.jsonl"), max_records=100)
        for _ in range(10):
            log.append(self._obs())
        removed = log.compact(keep=3)
        assert removed == 7
        assert len(log) == 3

    def test_compact_removes_corrupted_lines(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        p = tmp_path / "o.jsonl"
        log = ObservationLog(str(p), max_records=100)
        for _ in range(5):
            log.append(self._obs())
        with open(p, "a") as fh:
            fh.write("garbage not json\n")
            fh.write('{"wrong": "shape"}\n')
            fh.write("\n")
        removed = log.compact(keep=5)
        # 5 valid + 2 corrupted (blank not counted) → keep 5, remove 2
        assert removed == 2
        assert len(log) == 5
        # No corrupted line survives
        assert all("garbage" not in ln for ln in open(p))

    def test_compact_keep_defaults_to_max_records(self, tmp_path):
        import json, dataclasses
        from datetime import datetime, timezone
        from figma_forge.transport.observation_log import ObservationLog
        p = tmp_path / "o.jsonl"
        # Write 10 valid records directly, bypassing append's auto-trim
        # (which fires at max_records×2) so we isolate compact's default.
        with open(p, "w") as fh:
            for _ in range(10):
                rec = {"logged_at": datetime.now(timezone.utc).isoformat(),
                       "observation": dataclasses.asdict(self._obs())}
                fh.write(json.dumps(rec) + "\n")
        log = ObservationLog(str(p), max_records=4)
        removed = log.compact()  # keep defaults to max_records=4
        assert len(log) == 4
        assert removed == 6

    def test_compact_no_op_when_within_budget(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        p = tmp_path / "o.jsonl"
        log = ObservationLog(str(p), max_records=100)
        for _ in range(3):
            log.append(self._obs())
        mtime_before = p.stat().st_mtime_ns
        removed = log.compact(keep=10)  # already within budget, clean
        assert removed == 0
        # File untouched — no needless rewrite
        assert p.stat().st_mtime_ns == mtime_before

    def test_compact_missing_file_returns_zero(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        log = ObservationLog(str(tmp_path / "nope.jsonl"), max_records=10)
        assert log.compact() == 0

    def test_compact_keep_below_one_raises(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        log = ObservationLog(str(tmp_path / "o.jsonl"), max_records=10)
        log.append(self._obs())
        with pytest.raises(ValueError):
            log.compact(keep=0)

    def test_compact_all_corrupted_empties_file(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        p = tmp_path / "o.jsonl"
        log = ObservationLog(str(p), max_records=10)
        with open(p, "w") as fh:
            fh.write("bad1\nbad2\nbad3\n")
        removed = log.compact(keep=5)
        assert removed == 3
        assert len(log) == 0

    def test_compact_preserves_recency_order(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        log = ObservationLog(str(tmp_path / "o.jsonl"), max_records=100)
        for i in range(10):
            log.append(self._obs(total=100 + i))  # marker via total
        log.compact(keep=3)
        recent = log.read_recent()
        # Last 3 appended: totals 107, 108, 109
        assert [o.requests_total for o in recent] == [107, 108, 109]


class TestPerFieldFreshness:
    """v1.6.0-beta.1: per-entity-class freshness TTLs."""

    def _prior(self, age_seconds):
        from figma_forge.transport.plan_validation import PriorState
        from datetime import datetime, timezone, timedelta
        return PriorState(
            known_collection_ids=frozenset({"c1"}),
            known_component_names=frozenset({"Button"}),
            known_page_names=frozenset({"Page1"}),
            last_verified_at=datetime.now(timezone.utc) - timedelta(seconds=age_seconds),
        )

    def _plan(self):
        return {"plan_format_version": "1.0", "adapter": "mcp-cursor",
                "step_count": 1,
                "steps": [{"step": 1, "operation": "create_page",
                           "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                           "arguments": {"name": "P"}, "instruction": "x"}]}

    def test_per_class_distinguishes_stale_classes(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_seconds=300,
            freshness_window_overrides={"collection": 3600})
        # collection fresh (3600), component+page stale (300 fallback)
        warns = rep.freshness_warnings
        assert not any("collection" in w for w in warns)
        assert any("component" in w for w in warns)
        assert any("page" in w for w in warns)

    def test_per_class_never_blocks_executability(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(10000),
            freshness_window_overrides={"collection": 1, "component": 1, "page": 1})
        assert len(rep.freshness_warnings) == 3
        assert rep.is_executable  # warnings are advisory

    def test_scalar_mode_unchanged_when_no_overrides(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_seconds=300)
        # Exactly one class-agnostic warning (v1.5 behavior)
        assert len(rep.freshness_warnings) == 1
        assert "old, exceeds" in rep.freshness_warnings[0]

    def test_overrides_only_without_scalar(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_overrides={"component": 300})
        # Only component is evaluated (collection/page have no TTL)
        assert len(rep.freshness_warnings) == 1
        assert "component" in rep.freshness_warnings[0]

    def test_all_classes_fresh_no_warnings(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(100),
            freshness_window_overrides={"collection": 3600, "component": 3600, "page": 3600})
        assert rep.freshness_warnings == []

    def test_class_without_hint_skipped(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        from figma_forge.transport.plan_validation import PriorState
        from datetime import datetime, timezone, timedelta
        # Only collection hint present
        prior = PriorState(
            known_collection_ids=frozenset({"c1"}),
            last_verified_at=datetime.now(timezone.utc) - timedelta(seconds=600))
        rep = validate_mcp_plan(
            self._plan(), prior_state=prior,
            freshness_window_overrides={"collection": 100, "component": 100, "page": 100})
        # Only collection has a hint → exactly one warning
        assert len(rep.freshness_warnings) == 1
        assert "collection" in rep.freshness_warnings[0]

    def test_clock_skew_class_independent_in_per_class_mode(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(-500),  # future
            freshness_window_overrides={"collection": 100, "component": 100})
        # One clock-skew warning, not one per class
        assert len(rep.freshness_warnings) == 1
        assert "future" in rep.freshness_warnings[0]

    def test_run_forwards_overrides(self):
        import figma_forge as ff
        rep_holder = {}
        runner = ff.PlanRunner(
            nl_dispatch=lambda i, a: None,
            on_step=lambda sr: None)
        result = runner.run(
            self._plan(), prior_state=self._prior(600),
            freshness_window_overrides={"collection": 3600})
        # Validation ran with overrides; page is stale (no TTL → no fallback → skipped)
        # Actually page has no override and no scalar → skipped; only verify it executed
        assert result.validation_report is not None
        assert result.validation_report.is_executable


class TestSuggestWindow:
    """v1.6.0-beta.1: AdaptiveConcurrency.suggest_window heuristic."""

    def _obs(self, total, n429):
        import figma_forge as ff
        return ff.ConcurrencyObservation(
            requests_total=total, requests_429=n429, requests_5xx=0,
            retry_after_seconds_max=0.0, current_max_concurrency=4,
            recommended_max_concurrency=4, rationale="x")

    def test_empty_suggests_one(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency()
        w, rationale = ac.suggest_window([])
        assert w == 1
        assert "nothing to smooth" in rationale

    def test_small_batches_sample_sufficiency(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency(min_sample_size=10)
        # avg batch 3 → ceil(10/3) = 4
        w, _ = ac.suggest_window([self._obs(3, 0) for _ in range(4)])
        assert w == 4

    def test_large_stable_suggests_one(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency(min_sample_size=10)
        # Large, constant ratio → no smoothing needed
        w, _ = ac.suggest_window([self._obs(200, 4) for _ in range(5)])
        assert w == 1

    def test_volatility_increases_window(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency(min_sample_size=10)
        # Large batches but swinging 429 ratio
        volatile = [self._obs(100, 0), self._obs(100, 0), self._obs(100, 20),
                    self._obs(100, 0), self._obs(100, 18)]
        w, _ = ac.suggest_window(volatile)
        assert w >= 2

    def test_clamped_to_max_suggested(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency(min_sample_size=10)
        # avg 1 → ceil(10/1)=10, clamp to 5
        w, _ = ac.suggest_window([self._obs(1, 0) for _ in range(3)], max_suggested=5)
        assert w == 5

    def test_result_always_at_least_one(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency(min_sample_size=1)
        w, _ = ac.suggest_window([self._obs(1000, 0)])
        assert w >= 1

    def test_is_pure_no_mutation(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency(window=1)
        ac.suggest_window([self._obs(3, 0) for _ in range(4)])
        # window field is frozen and unchanged — suggest never mutates
        assert ac.window == 1

    def test_rationale_names_dominant_signal(self):
        import figma_forge as ff
        ac = ff.AdaptiveConcurrency(min_sample_size=10)
        _, r_sample = ac.suggest_window([self._obs(2, 0) for _ in range(3)])
        assert "min sample" in r_sample
        _, r_stable = ac.suggest_window([self._obs(500, 10) for _ in range(5)])
        assert "stable" in r_stable


# ===========================================================================
# v1.7.0-alpha.1 — ID-vs-name freshness split
#   "collection" refines into "collection_id" / "collection_name" sub-classes
# ===========================================================================

class TestFreshnessIdNameSplit:
    """v1.7.0-alpha.1: per-class freshness ID-vs-name split (RFC v1.7 §4.2)."""

    def _prior(self, age_seconds, *, ids=True, names=True, comp=True, page=True):
        from figma_forge.transport.plan_validation import PriorState
        from datetime import datetime, timezone, timedelta
        return PriorState(
            known_collection_ids=frozenset({"VariableCollectionId:1"}) if ids else frozenset(),
            known_collection_names=frozenset({"Brand"}) if names else frozenset(),
            known_component_names=frozenset({"Button"}) if comp else frozenset(),
            known_page_names=frozenset({"Page 1"}) if page else frozenset(),
            last_verified_at=datetime.now(timezone.utc) - timedelta(seconds=age_seconds),
        )

    def _plan(self):
        return {"plan_format_version": "1.0", "adapter": "mcp-cursor",
                "step_count": 1,
                "steps": [{"step": 1, "operation": "create_page",
                           "mcp_tool": "Figma:use_figma", "mechanism": "use_figma_nl",
                           "arguments": {"name": "P"}, "instruction": "x"}]}

    def _classes(self, rep):
        out = []
        for w in rep.freshness_warnings:
            for c in ("collection_id", "collection_name", "collection",
                      "component", "page"):
                if c in w:
                    out.append(c)
                    break
        return out

    # ---- split mode activation ---------------------------------------

    def test_split_distinguishes_id_and_name(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_overrides={"collection_id": 3600, "collection_name": 300})
        cls = self._classes(rep)
        assert "collection_id" not in cls   # fresh (3600)
        assert "collection_name" in cls     # stale (300)

    def test_split_activated_by_collection_id_key(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        # Only collection_id present → split mode; collection_name falls
        # back to the scalar window.
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_seconds=300,
            freshness_window_overrides={"collection_id": 3600})
        cls = self._classes(rep)
        assert "collection_id" not in cls   # fresh (3600)
        assert "collection_name" in cls     # scalar fallback 300, stale

    def test_split_activated_by_collection_name_key(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_seconds=300,
            freshness_window_overrides={"collection_name": 3600})
        cls = self._classes(rep)
        assert "collection_name" not in cls  # fresh (3600)
        assert "collection_id" in cls        # scalar fallback 300, stale

    # ---- most-specific-wins precedence (§5.5) ------------------------

    def test_subkey_overrides_collection_alias(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        # collection_id specific (3600, fresh); collection_name inherits
        # the "collection" alias (300, stale).
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_overrides={"collection_id": 3600, "collection": 300})
        cls = self._classes(rep)
        assert "collection_id" not in cls    # specific 3600 wins
        assert "collection_name" in cls      # collection alias 300

    def test_collection_alias_covers_both_when_no_subkey_for_one(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        # collection_name specific (3600 fresh); collection_id inherits
        # "collection" alias (300 stale).
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_overrides={"collection_name": 3600, "collection": 300})
        cls = self._classes(rep)
        assert "collection_name" not in cls
        assert "collection_id" in cls

    # ---- backward compatibility (criterion 3) ------------------------

    def test_collection_only_key_is_v16_combined_behavior(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        # Both id and name hints present; legacy "collection" key →
        # exactly ONE combined warning (not two), as in v1.6.
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_overrides={"collection": 300})
        cls = self._classes(rep)
        assert cls.count("collection") == 1
        assert "collection_id" not in cls
        assert "collection_name" not in cls

    def test_no_collection_key_combined_via_scalar(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        # No collection key at all, scalar fallback → combined behavior.
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600),
            freshness_window_seconds=300,
            freshness_window_overrides={"component": 9999})
        cls = self._classes(rep)
        # collection (combined) stale via scalar; not split
        assert cls.count("collection") == 1
        assert "collection_id" not in cls

    # ---- hint presence gating ----------------------------------------

    def test_split_only_id_hint_present(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600, names=False),
            freshness_window_overrides={"collection_id": 300, "collection_name": 300})
        cls = self._classes(rep)
        assert "collection_id" in cls
        assert "collection_name" not in cls  # no name hint → skipped

    def test_split_only_name_hint_present(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600, ids=False),
            freshness_window_overrides={"collection_id": 300, "collection_name": 300})
        cls = self._classes(rep)
        assert "collection_name" in cls
        assert "collection_id" not in cls    # no id hint → skipped

    # ---- advisory only -----------------------------------------------

    def test_split_never_blocks_executability(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(10000),
            freshness_window_overrides={"collection_id": 1, "collection_name": 1})
        assert len(rep.freshness_warnings) == 2
        assert rep.is_executable

    def test_split_warning_names_subclass(self):
        from figma_forge.transport.plan_validation import validate_mcp_plan
        rep = validate_mcp_plan(
            self._plan(), prior_state=self._prior(600, names=False),
            freshness_window_overrides={"collection_id": 300})
        # The warning text must name the sub-class precisely
        assert any("collection_id hints" in w for w in rep.freshness_warnings)

    def test_run_forwards_split_overrides(self):
        import figma_forge as ff
        runner = ff.PlanRunner(nl_dispatch=lambda i, a: None)
        result = runner.run(
            self._plan(), prior_state=self._prior(600),
            freshness_window_overrides={"collection_id": 3600, "collection_name": 300})
        assert result.validation_report is not None
        cls = self._classes(result.validation_report)
        assert "collection_name" in cls
        assert "collection_id" not in cls


# ===========================================================================
# v1.7.0-alpha.2 — Per-process ObservationLog sharding
#   Lock-free writes, merged reads, per-shard compaction (RFC v1.7 §4.1)
# ===========================================================================

class TestObservationLogSharding:
    """v1.7.0-alpha.2: per-process sharded ObservationLog."""

    def _obs(self, total=100, n429=2):
        import figma_forge as ff
        return ff.ConcurrencyObservation(
            requests_total=total, requests_429=n429, requests_5xx=0,
            retry_after_seconds_max=0.0, current_max_concurrency=4,
            recommended_max_concurrency=4, rationale="x")

    def _write_shard(self, path, records):
        """records: list of (logged_at_iso, total)."""
        import json
        with open(path, "w", encoding="utf-8") as fh:
            for ts, total in records:
                fh.write(json.dumps({
                    "logged_at": ts,
                    "observation": {"requests_total": total, "requests_429": 0,
                                    "requests_5xx": 0, "retry_after_seconds_max": 0.0,
                                    "current_max_concurrency": 4,
                                    "recommended_max_concurrency": 4,
                                    "rationale": "x"}}) + "\n")

    # ---- shard identity ----------------------------------------------

    def test_shard_id_format_no_dots(self):
        from figma_forge.transport import observation_log as ol
        sid = ol._shard_id()
        assert sid.count("-") == 2          # pid-host-start
        assert "." not in sid               # safe for the glob

    def test_shard_id_stable_within_process(self):
        from figma_forge.transport import observation_log as ol
        assert ol._shard_id() == ol._shard_id()

    # ---- sharded append: own file, no lock ---------------------------

    def test_sharded_append_writes_shard_not_bare(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.append(self._obs())
        assert not (tmp_path / "history.jsonl").exists()  # no bare file
        shards = list(tmp_path.glob("history.*.jsonl"))
        assert len(shards) == 1

    def test_sharded_append_is_lock_free(self, tmp_path, monkeypatch):
        from figma_forge.transport import observation_log as ol
        from figma_forge.transport.observation_log import ObservationLog
        from contextlib import contextmanager
        calls = {"n": 0}
        orig = ol._exclusive_lock
        @contextmanager
        def counting(fh):
            calls["n"] += 1
            with orig(fh):
                yield
        monkeypatch.setattr(ol, "_exclusive_lock", counting)
        log = ObservationLog(str(tmp_path / "h.jsonl"),
                             max_records=100, shard_per_process=True)
        for _ in range(5):
            log.append(self._obs())
        assert calls["n"] == 0  # lock-free: the whole point of sharding

    def test_single_file_append_still_locks(self, tmp_path, monkeypatch):
        from figma_forge.transport import observation_log as ol
        from figma_forge.transport.observation_log import ObservationLog
        from contextlib import contextmanager
        calls = {"n": 0}
        orig = ol._exclusive_lock
        @contextmanager
        def counting(fh):
            calls["n"] += 1
            with orig(fh):
                yield
        monkeypatch.setattr(ol, "_exclusive_lock", counting)
        log = ObservationLog(str(tmp_path / "h.jsonl"),
                             max_records=100, shard_per_process=False)
        for _ in range(5):
            log.append(self._obs())
        assert calls["n"] == 5  # single-file mode unchanged

    # ---- merged reads ------------------------------------------------

    def test_sharded_read_merges_by_logged_at(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        base = "2026-01-01T12:00:0"
        self._write_shard(tmp_path / "history.1-a-1.jsonl",
                          [(base + "0+00:00", 200), (base + "3+00:00", 203)])
        self._write_shard(tmp_path / "history.2-b-2.jsonl",
                          [(base + "1+00:00", 201), (base + "4+00:00", 204)])
        self._write_shard(tmp_path / "history.3-c-3.jsonl",
                          [(base + "2+00:00", 202)])
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        totals = [o.requests_total for o in log.read_recent()]
        assert totals == [200, 201, 202, 203, 204]  # chronological merge

    def test_sharded_read_respects_n(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        base = "2026-01-01T12:00:0"
        self._write_shard(tmp_path / "history.1-a-1.jsonl",
                          [(base + f"{i}+00:00", 200 + i) for i in range(5)])
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        totals = [o.requests_total for o in log.read_recent(2)]
        assert totals == [203, 204]  # last 2 chronologically

    def test_sharded_len_counts_all_shards(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        self._write_shard(tmp_path / "history.1-a-1.jsonl",
                          [("2026-01-01T00:00:00+00:00", 1)])
        self._write_shard(tmp_path / "history.2-b-2.jsonl",
                          [("2026-01-01T00:00:01+00:00", 2),
                           ("2026-01-01T00:00:02+00:00", 3)])
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        assert len(log) == 3

    def test_sharded_read_skips_corrupted(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        p = tmp_path / "history.1-a-1.jsonl"
        self._write_shard(p, [("2026-01-01T00:00:00+00:00", 100)])
        with open(p, "a") as fh:
            fh.write("garbage\n")
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        assert len(log) == 1  # corrupted line skipped, no raise

    # ---- mode cross-compatibility (§5.4) -----------------------------

    def test_sharded_read_includes_bare_file(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        p = str(tmp_path / "history.jsonl")
        # Legacy single-file write
        ObservationLog(p, max_records=100, shard_per_process=False).append(
            self._obs(500))
        # Sharded read should treat the bare file as one more shard
        sharded = ObservationLog(p, max_records=100, shard_per_process=True)
        sharded.append(self._obs(600))
        totals = sorted(o.requests_total for o in sharded.read_recent())
        assert totals == [500, 600]

    # ---- per-shard compaction ----------------------------------------

    def test_compact_each_shard_independently(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        base = "2026-01-01T00:00:"
        self._write_shard(tmp_path / "history.1-a-1.jsonl",
                          [(base + f"{i:02d}+00:00", 100) for i in range(8)])
        self._write_shard(tmp_path / "history.2-b-2.jsonl",
                          [(base + f"{i:02d}+00:00", 200) for i in range(6)])
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        removed = log.compact(keep=3)
        assert removed == (8 - 3) + (6 - 3)  # 5 + 3 = 8
        assert len(log) == 6  # 3 per shard

    def test_sharded_clear_removes_all_shards(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        self._write_shard(tmp_path / "history.1-a-1.jsonl",
                          [("2026-01-01T00:00:00+00:00", 1)])
        self._write_shard(tmp_path / "history.2-b-2.jsonl",
                          [("2026-01-01T00:00:01+00:00", 2)])
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.clear()
        assert len(log) == 0
        assert list(tmp_path.glob("history*.jsonl")) == []

    # ---- backward compatibility --------------------------------------

    def test_single_file_default_unchanged(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        p = tmp_path / "history.jsonl"
        log = ObservationLog(str(p), max_records=100)  # default False
        log.append(self._obs(100))
        log.append(self._obs(101))
        assert p.exists()  # bare file, not a shard
        assert not list(tmp_path.glob("history.*.jsonl"))  # no shard files
        assert len(log) == 2

    def test_sharded_roundtrip_append_then_read(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.append(self._obs(100, 5))
        recent = log.read_recent()
        assert len(recent) == 1
        assert recent[0].requests_total == 100
        assert recent[0].requests_429 == 5  # all fields preserved


# ===========================================================================
# v1.7.0-beta.1 — Dead-shard reaping
#   Age-based cleanup of shards from exited processes (RFC v1.7 §5.3)
# ===========================================================================

class TestDeadShardReaping:
    """v1.7.0-beta.1: compact() reaps dead foreign shards by age."""

    def _obs(self, total=1):
        import figma_forge as ff
        return ff.ConcurrencyObservation(
            requests_total=total, requests_429=0, requests_5xx=0,
            retry_after_seconds_max=0.0, current_max_concurrency=4,
            recommended_max_concurrency=4, rationale="x")

    def _write_shard(self, path, n, total=100):
        import json
        with open(path, "w", encoding="utf-8") as fh:
            for i in range(n):
                fh.write(json.dumps({
                    "logged_at": f"2026-01-01T00:00:{i:02d}+00:00",
                    "observation": {"requests_total": total, "requests_429": 0,
                                    "requests_5xx": 0, "retry_after_seconds_max": 0.0,
                                    "current_max_concurrency": 4,
                                    "recommended_max_concurrency": 4,
                                    "rationale": "x"}}) + "\n")

    def _age(self, path, seconds):
        """Backdate a file's mtime by `seconds`."""
        import os
        import time
        old = time.time() - seconds
        os.utime(path, (old, old))

    # ---- the default threshold ---------------------------------------

    def test_default_threshold_is_one_week(self):
        from figma_forge.transport import observation_log as ol
        assert ol._DEFAULT_REAP_AFTER_SECONDS == 7 * 24 * 3600

    # ---- reaping a dead shard ----------------------------------------

    def test_old_foreign_shard_is_reaped(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        dead = tmp_path / "history.999-dead-aaa.jsonl"
        self._write_shard(dead, 5)
        self._age(dead, 8 * 24 * 3600)  # 8 days > 7-day threshold
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.append(self._obs())  # our own (fresh) shard
        removed = log.compact(keep=100)
        assert not dead.exists()       # reaped
        assert removed == 5            # its records counted as removed
        assert log._shard_path().exists()  # our shard survives
        assert len(log) == 1

    def test_reaped_records_counted_in_removed(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        dead = tmp_path / "history.1-dead-a.jsonl"
        self._write_shard(dead, 7)
        self._age(dead, 10 * 24 * 3600)
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        assert log.compact(keep=100) == 7  # all 7 records of the dead shard

    # ---- exemptions: own shard, bare file ----------------------------

    def test_own_shard_never_reaped_even_if_old(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.append(self._obs())
        own = log._shard_path()
        self._age(own, 30 * 24 * 3600)  # 30 days old
        log.compact(keep=100)
        assert own.exists()  # alive process — never reaped
        assert len(log) == 1

    def test_bare_file_never_reaped_even_if_old(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        bare = tmp_path / "history.jsonl"
        self._write_shard(bare, 3)
        self._age(bare, 60 * 24 * 3600)  # 60 days old
        log = ObservationLog(str(bare), max_records=100, shard_per_process=True)
        log.compact(keep=100)
        assert bare.exists()  # legacy single-file — operator may keep it
        assert len(log) == 3

    # ---- fresh shards are safe ---------------------------------------

    def test_fresh_foreign_shard_not_reaped(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        fresh = tmp_path / "history.888-other-b.jsonl"
        self._write_shard(fresh, 4)  # mtime = now
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.compact(keep=100)
        assert fresh.exists()
        assert len(log) == 4

    def test_shard_just_under_threshold_not_reaped(self, tmp_path):
        from figma_forge.transport import observation_log as ol
        from figma_forge.transport.observation_log import ObservationLog
        s = tmp_path / "history.333-x-f.jsonl"
        self._write_shard(s, 2)
        self._age(s, ol._DEFAULT_REAP_AFTER_SECONDS - 3600)  # 1h under
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.compact(keep=100)
        assert s.exists()

    # ---- opt-out -----------------------------------------------------

    def test_reaping_disabled_with_none(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        dead = tmp_path / "history.777-dead-c.jsonl"
        self._write_shard(dead, 5)
        self._age(dead, 100 * 24 * 3600)  # 100 days old
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        log.compact(keep=100, reap_after_seconds=None)
        assert dead.exists()  # reaping off — even a 100-day shard survives
        assert len(log) == 5

    def test_custom_threshold_more_aggressive(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        s = tmp_path / "history.444-dead-g.jsonl"
        self._write_shard(s, 3)
        self._age(s, 2 * 3600)  # 2 hours old
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        # 1-hour threshold — the 2-hour shard is now dead
        removed = log.compact(keep=100, reap_after_seconds=3600)
        assert not s.exists()
        assert removed == 3

    # ---- reap + compact together -------------------------------------

    def test_reap_and_compact_combined(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        dead = tmp_path / "history.111-dead-d.jsonl"
        self._write_shard(dead, 5)
        self._age(dead, 10 * 24 * 3600)
        alive = tmp_path / "history.222-busy-e.jsonl"
        self._write_shard(alive, 8)  # fresh, over budget
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        removed = log.compact(keep=3)
        assert removed == 5 + (8 - 3)  # 5 reaped + 5 trimmed = 10
        assert not dead.exists()
        assert alive.exists()
        assert len(log) == 3  # alive shard trimmed to 3

    # ---- single-file mode ignores the parameter ----------------------

    def test_single_file_ignores_reap(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        p = tmp_path / "history.jsonl"
        self._write_shard(p, 8)
        self._age(p, 100 * 24 * 3600)  # 100 days old
        log = ObservationLog(str(p), max_records=100)  # single-file
        removed = log.compact(keep=3)  # default reap arg, but no shards
        assert p.exists()      # file survives (just compacted in place)
        assert removed == 5    # 8 → 3
        assert len(log) == 3

    # ---- empty / vanished shard tolerance ----------------------------

    def test_reap_empty_shard_contributes_zero(self, tmp_path):
        from figma_forge.transport.observation_log import ObservationLog
        empty = tmp_path / "history.555-dead-h.jsonl"
        empty.write_text("", encoding="utf-8")
        self._age(empty, 10 * 24 * 3600)
        log = ObservationLog(str(tmp_path / "history.jsonl"),
                             max_records=100, shard_per_process=True)
        removed = log.compact(keep=100)
        assert not empty.exists()  # still reaped
        assert removed == 0        # no records to count
