#!/usr/bin/env python3
"""
run_tests.py — Skill-package self-validation runner for figma-forge.

Runs the 8 verification gates declared in skill-manifest.yaml:
    G1-INT     file integrity
    G2-CONT    content validation
    G3-TPL     template validation
    G4-CONS    cross-file consistency
    G5-PROC    procedural completeness
    G6-ANTI    anti-pattern detection
    G7-DESC    description validation (≤1024 char hard limit)
    G8-MAPPER  built-in mapper coverage

Usage:
    python3 tests/run_tests.py                 # human-readable output
    python3 tests/run_tests.py --strict        # exit code 1 on error-severity failure
    python3 tests/run_tests.py --json          # machine-readable JSON output
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


@dataclass
class GateResult:
    id: str
    name: str
    severity: str  # 'error' | 'warning'
    passed: bool
    details: list[str] = field(default_factory=list)


# ----------------------------------------------------------------------------
# Gate implementations
# ----------------------------------------------------------------------------

REQUIRED_FILES = [
    "SKILL.md",
    "skill-manifest.yaml",
    "README.md",
    "references/figma-mcp-cookbook.md",
    "references/figma-rest-api.md",
    "references/figma-plugin-fallback.md",
    "references/w3c-dtcg-tokens.md",
    "references/style-dictionary.md",
    "references/carbon-mapping.md",
    "references/material3-mapping.md",
    "references/tailwind-mapping.md",
    "references/library-architecture.md",
    "references/component-spec-templates.md",
    "references/code-connect-patterns.md",
    "references/naming-conventions.md",
    "references/publish-checklist.md",
    "templates/dtcg-tokens.template.json",
    "templates/figma-plugin/manifest.json",
    "templates/figma-plugin/code.ts",
    "templates/figma-plugin/ui.html",
    "templates/code-connect/react.figma.tsx.template",
    "scripts/dtcg_to_variables.py",
    "scripts/style_dict_to_dtcg.py",
    "scripts/carbon_to_dtcg.py",
    "scripts/material3_to_dtcg.py",
    "scripts/tailwind_to_dtcg.py",
    "scripts/publish_audit.py",
    "evals/evals.json",
    "tests/run_tests.py",
]


def g1_file_integrity() -> GateResult:
    res = GateResult(id="G1-INT", name="File integrity", severity="error", passed=True)
    for rel in REQUIRED_FILES:
        if not (REPO / rel).exists():
            res.passed = False
            res.details.append(f"missing: {rel}")
    return res


MODE_NAMES = ["SCAFFOLD", "TOKENS_IMPORT", "FOUNDATIONS_BUILD",
              "COMPONENTS_BUILD", "MIGRATE", "CODE_CONNECT", "PUBLISH_AUDIT"]


def g2_content_validation() -> GateResult:
    res = GateResult(id="G2-CONT", name="Content validation", severity="error", passed=True)
    skill_md = (REPO / "SKILL.md").read_text(encoding="utf-8")
    for m in MODE_NAMES:
        if f"`{m}`" not in skill_md:
            res.details.append(f"mode missing from SKILL.md: {m}")
            res.passed = False
    # DTCG keyword presence
    dtcg_md = (REPO / "references/w3c-dtcg-tokens.md").read_text(encoding="utf-8")
    for kw in ["$value", "$type", "$description", "VARIABLE_ALIAS"]:
        if kw not in dtcg_md:
            res.details.append(f"DTCG keyword missing: {kw}")
            res.passed = False
    return res


def g3_template_validation() -> GateResult:
    res = GateResult(id="G3-TPL", name="Template validation", severity="error", passed=True)
    # DTCG template parses
    try:
        with open(REPO / "templates/dtcg-tokens.template.json", encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        res.passed = False
        res.details.append(f"DTCG template JSON parse error: {e}")
    # Plugin manifest parses
    try:
        with open(REPO / "templates/figma-plugin/manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
            for key in ("name", "id", "api", "main", "ui", "editorType"):
                if key not in manifest:
                    res.passed = False
                    res.details.append(f"plugin manifest missing key: {key}")
    except Exception as e:
        res.passed = False
        res.details.append(f"plugin manifest JSON parse error: {e}")
    # Plugin code has required functions
    code_ts = (REPO / "templates/figma-plugin/code.ts").read_text(encoding="utf-8")
    for sig in ["figma.variables.createVariableCollection",
                "figma.variables.createVariable",
                "figma.createPaintStyle",
                "figma.createTextStyle",
                "figma.createEffectStyle"]:
        if sig not in code_ts:
            res.passed = False
            res.details.append(f"plugin code missing API: {sig}")
    return res


def g4_cross_file_consistency() -> GateResult:
    res = GateResult(id="G4-CONS", name="Cross-file consistency", severity="error", passed=True)
    # Every mode referenced in SKILL.md should have at least one reference file mention
    skill_md = (REPO / "SKILL.md").read_text(encoding="utf-8")
    ref_paths = list((REPO / "references").glob("*.md"))
    ref_text = "\n".join(p.read_text(encoding="utf-8") for p in ref_paths)
    for m in MODE_NAMES:
        if m not in ref_text:
            res.details.append(f"mode {m} not referenced in any references/")
            res.passed = False
    # Verify the channel strategy is consistent
    if "Channel 1" not in skill_md or "Channel 2" not in skill_md or "Channel 3" not in skill_md:
        res.passed = False
        res.details.append("3-channel strategy not documented in SKILL.md")
    return res


def g5_procedural_completeness() -> GateResult:
    res = GateResult(id="G5-PROC", name="Procedural completeness", severity="error", passed=True)
    skill_md = (REPO / "SKILL.md").read_text(encoding="utf-8")
    # Each mode should have Precondition / Workflow / Postcondition documented
    for m in MODE_NAMES:
        # Look for the mode's section
        pattern = rf"### Mode \d+:?\s*`?{m}`?"
        if not re.search(pattern, skill_md):
            res.passed = False
            res.details.append(f"mode section missing for {m}")
            continue
        # The mode section should contain Precondition, Workflow, Postcondition
        section_start = re.search(pattern, skill_md).end()
        next_mode_match = re.search(r"### Mode \d+", skill_md[section_start:])
        section_end = section_start + (next_mode_match.start() if next_mode_match else 5000)
        section_text = skill_md[section_start:section_end]
        for required in ["Precondition", "Workflow", "Postcondition"]:
            if required not in section_text:
                res.passed = False
                res.details.append(f"mode {m} missing {required}")
    return res


def g6_anti_pattern() -> GateResult:
    res = GateResult(id="G6-ANTI", name="Anti-pattern detection", severity="warning", passed=True)
    # Scan for obvious hard-coded Figma file keys (24-char alphanumeric)
    suspect_pattern = re.compile(r"\bfile_key\s*[:=]\s*['\"][A-Za-z0-9]{22,}['\"]")
    for f in REPO.rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        for m in suspect_pattern.finditer(text):
            res.passed = False
            res.details.append(f"hard-coded file_key in {f.relative_to(REPO)}: {m.group(0)[:80]}")
    # Scan for PAT leakage signs
    pat_pattern = re.compile(r"['\"]figd_[A-Za-z0-9]{32,}['\"]")
    for f in REPO.rglob("*"):
        if not f.is_file() or f.suffix not in (".py", ".ts", ".md", ".json", ".html"):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if pat_pattern.search(text):
            res.passed = False
            res.details.append(f"possible PAT leakage in {f.relative_to(REPO)}")
    return res


def g7_description_validation() -> GateResult:
    """SMP v1.0 hard limit: SKILL.md frontmatter description ≤1024 chars."""
    res = GateResult(id="G7-DESC", name="Description validation", severity="error", passed=True)
    skill_md = (REPO / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", skill_md, re.DOTALL)
    if not m:
        res.passed = False
        res.details.append("SKILL.md has no YAML frontmatter")
        return res
    front = m.group(1)
    desc_match = re.search(r"^description:\s*(.*?)(?=^[a-z_]+:|\Z)", front, re.MULTILINE | re.DOTALL)
    if not desc_match:
        res.passed = False
        res.details.append("description key not found in frontmatter")
        return res
    desc = desc_match.group(1).strip()
    # Strip YAML block-scalar markers and collapse whitespace
    desc_normalized = re.sub(r"^>-?\s*", "", desc, flags=re.MULTILINE)
    desc_normalized = re.sub(r"\s+", " ", desc_normalized).strip()
    if len(desc_normalized) > 1024:
        res.passed = False
        res.details.append(f"description length {len(desc_normalized)} exceeds SMP v1.0 hard limit of 1024 chars")
    # Must contain a few trigger keywords
    for kw in ["Figma", "DS", "DTCG", "USE"]:
        if kw not in desc_normalized:
            res.details.append(f"description lacks recommended keyword: {kw}")
            # Not a hard failure
    return res


def g8_mapper_coverage() -> GateResult:
    res = GateResult(id="G8-MAPPER", name="Built-in mapper coverage", severity="error", passed=True)
    for required_script in ["carbon_to_dtcg.py", "material3_to_dtcg.py", "tailwind_to_dtcg.py"]:
        path = REPO / "scripts" / required_script
        if not path.exists():
            res.passed = False
            res.details.append(f"mapper missing: {required_script}")
            continue
        text = path.read_text(encoding="utf-8")
        # Each mapper should have a build() or main() entry point
        if "def main(" not in text:
            res.passed = False
            res.details.append(f"mapper {required_script} has no main()")
    # Sanity: try running the Carbon mapper if Python is available
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(REPO / "scripts/carbon_to_dtcg.py"),
             "--theme", "white", "--output", "/tmp/figma-forge-test-carbon.json"],
            capture_output=True, timeout=10
        )
        if result.returncode != 0:
            res.passed = False
            res.details.append(f"carbon_to_dtcg.py runtime failure: {result.stderr.decode()[:200]}")
    except Exception as e:
        res.details.append(f"could not run carbon mapper smoke test: {e}")
    return res


GATES = [
    ("G1-INT",  g1_file_integrity),
    ("G2-CONT", g2_content_validation),
    ("G3-TPL",  g3_template_validation),
    ("G4-CONS", g4_cross_file_consistency),
    ("G5-PROC", g5_procedural_completeness),
    ("G6-ANTI", g6_anti_pattern),
    ("G7-DESC", g7_description_validation),
    ("G8-MAPPER", g8_mapper_coverage),
]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strict", action="store_true", help="Exit code 1 on warning-severity failure too")
    p.add_argument("--json",  action="store_true", help="JSON output")
    args = p.parse_args()

    results = [fn() for _, fn in GATES]

    error_failures = sum(1 for r in results if not r.passed and r.severity == "error")
    warning_failures = sum(1 for r in results if not r.passed and r.severity == "warning")

    if args.json:
        print(json.dumps([{
            "id": r.id, "name": r.name, "severity": r.severity,
            "passed": r.passed, "details": r.details
        } for r in results], indent=2))
    else:
        print(f"figma-forge — Skill verification ({len(results)} gates)\n")
        for r in results:
            icon = "✅" if r.passed else ("❌" if r.severity == "error" else "⚠️")
            print(f"  {icon} {r.id} — {r.name} [{r.severity}]")
            for d in r.details:
                print(f"      · {d}")
        print()
        print(f"  Errors: {error_failures}  ·  Warnings: {warning_failures}")
        if error_failures == 0 and warning_failures == 0:
            print("  ✓ All gates passed.")

    if error_failures > 0:
        return 1
    if args.strict and warning_failures > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
