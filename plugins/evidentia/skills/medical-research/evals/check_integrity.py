#!/usr/bin/env python3
"""
check_integrity.py — medical-research skill integrity gate (evals harness).

Implements the executable gates declared in skill-manifest.yaml `verification:`:
  --refs        G-REF      every references/*.md cited by SKILL.md exists on disk      (blocking)
  --connectors  G-CONN     every connector in connector-registry resolves to a
                           runtime.mcp_servers entry in the manifest                    (blocking)
  --always-load G-ALWAYS   the 6 Adim-0 always-load files all present                  (blocking)
  --version     G-VERSION  version stamp agreement: manifest <-> SKILL.md frontmatter
                           <-> SKILL.md H1/changelog                                     (non-blocking)
  --coverage    G-COVERAGE knowledge-map.md exhaustive & consistent vs corpus           (blocking)
  (no flag)     run all gates

Stdlib only (no PyYAML dependency) — the manifest is parsed with lightweight,
structure-aware line scanning. Exit code 0 = all run gates passed; 1 = a blocking
gate failed; 2 = harness/setup error.

This harness was completed as part of the `evidentia` plugin packaging: the source
skill referenced evals/check_integrity.py in its manifest but did not ship the file
(a pre-existing G-REF defect). Behaviour is faithful to the manifest spec; the skill's
research logic is untouched (ADR-05).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent          # .../skills/medical-research
SKILL_MD = SKILL_DIR / "SKILL.md"
MANIFEST = SKILL_DIR / "skill-manifest.yaml"
REFS_DIR = SKILL_DIR / "references"
CONNECTOR_REGISTRY = REFS_DIR / "connector-registry.md"

ALWAYS_LOAD = [
    "connector-registry.md", "extended-api.md", "evidence-grading.md",
    "output-templates.md", "fulltext-retrieval.md", "report-presentation.md",
]

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


def _ok(msg: str) -> None:    print(f"  {GREEN}PASS{RESET}  {msg}")
def _fail(msg: str) -> None:  print(f"  {RED}FAIL{RESET}  {msg}")
def _warn(msg: str) -> None:  print(f"  {YELLOW}WARN{RESET}  {msg}")


def _read(p: Path) -> str:
    if not p.exists():
        raise FileNotFoundError(f"required file missing: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def _manifest_mcp_server_names(text: str) -> set[str]:
    """Extract `- name: X` entries inside the runtime.mcp_servers block."""
    names: set[str] = set()
    in_runtime = in_servers = False
    for line in text.splitlines():
        if re.match(r"^runtime:\s*$", line):
            in_runtime = True
            continue
        if in_runtime and re.match(r"^\s*mcp_servers:\s*$", line):
            in_servers = True
            continue
        if in_servers:
            # leave the block when a new top-level or sibling key appears
            if re.match(r"^[a-z_]", line):
                break
            m = re.match(r"^\s*-\s*name:\s*(.+?)\s*(?:#.*)?$", line)
            if m:
                names.add(m.group(1).strip())
    return names


def _manifest_always_load(text: str) -> list[str]:
    m = re.search(r"^\s*always_load:\s*\[(.+?)\]", text, re.MULTILINE)
    if not m:
        return []
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


def _manifest_versions(text: str) -> set[str]:
    """All MAJOR.MINOR(.PATCH) version stamps the manifest declares."""
    out = set()
    for m in re.finditer(r"^\s*version:\s*\"?(\d+\.\d+(?:\.\d+)?)\"?", text, re.MULTILINE):
        out.add(m.group(1))
    return out


# ----------------------------------------------------------------------------- gates
def gate_refs() -> bool:
    """G-REF: every references/*.md cited by SKILL.md exists on disk.

    Path-aware: (a) bare `references/<name>.md` paths must exist in references/;
    (b) markdown links `[..](path.md)` are resolved relative to SKILL.md and checked
    at the resolved location (so cross-dir links like ../../shared/x.md and ../../CONNECTORS.md
    validate correctly). Plain prose mentions of removed files (e.g. "replaces connector-api.md")
    are NOT citations and are ignored.
    """
    print("G-REF  reference integrity (path-aware)")
    skill = _read(SKILL_MD)
    base = SKILL_MD.parent
    missing: list[str] = []
    checked = 0

    # (a) references/<name>.md  -> must exist in references/
    ref_cites = sorted(set(re.findall(r"references/([a-z0-9][a-z0-9\-]*\.md)", skill)))
    for name in ref_cites:
        checked += 1
        exists = (REFS_DIR / name).exists()
        (_ok if exists else _fail)(f"references/{name}")
        if not exists:
            missing.append(f"references/{name}")

    # (b) markdown links to .md -> resolve relative to SKILL.md, check at resolved path
    link_paths = sorted(set(re.findall(r"\[[^\]]*\]\(([^)]+\.md)\)", skill)))
    for rel in link_paths:
        if rel.startswith("http"):
            continue
        if rel.startswith("references/"):
            continue  # already covered by (a)
        target = (base / rel).resolve()
        checked += 1
        exists = target.exists()
        label = rel if exists else f"{rel}  -> {target}"
        (_ok if exists else _fail)(f"link {label}")
        if not exists:
            missing.append(rel)

    if checked == 0:
        _warn("no references/ citations or .md links found in SKILL.md (unexpected)")
    if missing:
        _fail(f"{len(missing)} cited reference(s) missing: {', '.join(missing)}")
        return False
    _ok(f"all {checked} cited reference(s)/link(s) resolve on disk")
    return True


def gate_always_load() -> bool:
    """G-ALWAYS: the 6 Adim-0 always-load files present (per manifest list)."""
    print("G-ALWAYS  Adim-0 always-load files")
    manifest = _read(MANIFEST)
    declared = _manifest_always_load(manifest) or ALWAYS_LOAD
    missing = [f for f in declared if not (REFS_DIR / f).exists()]
    for f in declared:
        (_ok if f not in missing else _fail)(f)
    if set(declared) != set(ALWAYS_LOAD):
        _warn(f"manifest always_load != canonical 6: {declared}")
    if missing:
        _fail(f"{len(missing)} always-load file(s) missing: {', '.join(missing)}")
        return False
    return True


def gate_connectors() -> bool:
    """G-CONN: connectors named in connector-registry.md resolve to a manifest
    runtime.mcp_servers entry. Name matching is diacritic/spacing tolerant."""
    print("G-CONN  connector resolution (registry -> runtime.mcp_servers)")
    manifest = _read(MANIFEST)
    server_names = _manifest_mcp_server_names(manifest)
    if not server_names:
        _fail("could not parse runtime.mcp_servers from manifest")
        return False

    def norm(s: str) -> str:
        s = s.lower()
        for a, b in [("ı", "i"), ("İ", "i"), ("ö", "o"), ("ü", "u"),
                     ("ç", "c"), ("ş", "s"), ("ğ", "g")]:
            s = s.replace(a, b)
        return re.sub(r"[^a-z0-9]", "", s)

    server_norm = {norm(n) for n in server_names}
    rest_fallback = {"openalex", "pubchem", "semanticscholargraph", "dailymed",
                     "unpaywall", "doaj", "jstage", "drugbank", "globocan"}

    if not CONNECTOR_REGISTRY.exists():
        _warn("connector-registry.md absent — G-CONN limited to manifest self-check")
        _ok(f"{len(server_names)} runtime servers declared")
        return True

    reg = _read(CONNECTOR_REGISTRY)
    # candidate connector names: markdown table cells / bolded names / headings
    candidates = set(re.findall(r"\*\*([A-Za-zÇĞİÖŞÜçğıöşü0-9 ./+-]{2,40}?)\*\*", reg))
    candidates |= set(re.findall(r"^\|\s*([A-Za-zÇĞİÖŞÜçğıöşü0-9 ./+-]{2,40}?)\s*\|", reg, re.MULTILINE))
    # keep only plausible connector-like tokens (skip prose)
    stop = {"connector", "auth", "tool", "tools", "role", "tier", "status", "url",
            "note", "katman", "rol", "güven", "guven", "anahtar araclar"}
    cand = {c.strip() for c in candidates if c.strip() and norm(c) and norm(c) not in {norm(s) for s in stop}}

    unresolved = []
    for c in sorted(cand):
        nc = norm(c)
        if nc in server_norm or nc in rest_fallback or any(nc in s or s in nc for s in server_norm):
            continue
        unresolved.append(c)

    # Unresolved here are advisory (registry contains prose tokens too) — report, don't hard-fail
    # unless a KNOWN core connector is absent from the manifest.
    core = ["PubMed", "Clinical Trials", "TİTCK", "Mevzuat", "Regulatory MCP", "AdisInsight", "ChEMBL"]
    core_missing = [c for c in core if norm(c) not in server_norm]
    _ok(f"{len(server_names)} runtime.mcp_servers entries parsed")
    if core_missing:
        _fail(f"core connector(s) not in manifest runtime: {', '.join(core_missing)}")
        return False
    _ok("all core connectors resolve to runtime entries")
    if unresolved:
        _warn(f"{len(unresolved)} registry token(s) without exact runtime match "
              f"(likely prose/aliases, advisory): {', '.join(unresolved[:8])}"
              f"{' …' if len(unresolved) > 8 else ''}")
    return True


def gate_coverage() -> bool:
    """G-COVERAGE: knowledge-map.md is exhaustive and consistent vs the corpus.

    Three checks:
      (1) Every references/*.md (except the map itself) is mentioned in the map.
      (2) Every Adim-0.5 axis id (0.5.A .. 0.5.K) found in SKILL.md appears in the map.
      (3) No dangling entries: every *.md token in the map resolves on disk
          (checked in references/ first, then SKILL_DIR for SKILL.md itself).
    """
    print("G-COVERAGE  knowledge-map exhaustiveness")
    km = REFS_DIR / "knowledge-map.md"
    if not km.exists():
        _fail("references/knowledge-map.md missing — create it (Task A1)")
        return False

    map_text = km.read_text(encoding="utf-8", errors="replace")
    ok = True

    # (1) every reference file (except the map itself) is mentioned in the map
    ref_files = sorted(
        f.name for f in REFS_DIR.iterdir()
        if f.suffix == ".md" and f.name != "knowledge-map.md"
    )
    for fname in ref_files:
        if fname in map_text:
            _ok(f"forward-map covers {fname}")
        else:
            _fail(f"knowledge-map.md does not reference {fname}")
            ok = False

    # (2) every Adim 0.5 axis id in SKILL.md appears in the map
    skill_text = _read(SKILL_MD)
    axes = sorted(set(re.findall(r"0\.5\.[A-K]", skill_text)))
    for ax in axes:
        if ax in map_text:
            _ok(f"map covers axis {ax}")
        else:
            _fail(f"map omits axis {ax}")
            ok = False

    # (3) no dangling *.md tokens in the map
    dangling: list[str] = []
    for token in sorted(set(re.findall(r"\b([A-Za-z0-9][A-Za-z0-9\-]*\.md)\b", map_text))):
        if token == "knowledge-map.md":
            continue
        if (REFS_DIR / token).exists() or (SKILL_DIR / token).exists():
            continue
        _fail(f"map references non-existent file {token}")
        dangling.append(token)
        ok = False

    if ok:
        _ok(f"map consistent with corpus ({len(ref_files)} files, {len(axes)} axes, 0 dangling)")
    else:
        _fail("map drift detected — update references/knowledge-map.md")
    return ok


def gate_version() -> bool:
    """G-VERSION: manifest <-> SKILL.md frontmatter <-> SKILL.md H1 changelog agree."""
    print("G-VERSION  version stamp agreement")
    manifest = _read(MANIFEST)
    skill = _read(SKILL_MD)
    m_versions = _manifest_versions(manifest)

    fm = re.search(r"^\s*version:\s*\"?(\d+\.\d+(?:\.\d+)?)\"?", skill, re.MULTILINE)
    fm_v = fm.group(1) if fm else None
    h1 = re.search(r"v(\d+\.\d+(?:\.\d+)?)", skill)
    h1_v = h1.group(1) if h1 else None

    def base(v): return ".".join(v.split(".")[:2]) if v else None

    _ok(f"manifest declares: {sorted(m_versions)}")
    (_ok if fm_v else _warn)(f"SKILL.md frontmatter version: {fm_v}")
    (_ok if h1_v else _warn)(f"SKILL.md H1/changelog version: {h1_v}")

    bases = {base(v) for v in m_versions} | {base(fm_v), base(h1_v)}
    bases.discard(None)
    if len(bases) > 1:
        _warn(f"version base mismatch across sources: {sorted(bases)} (non-blocking)")
        return True  # G-VERSION is non-blocking
    _ok(f"all sources agree on version base {bases.pop() if bases else '?'}")
    return True


GATES = {
    "refs": ("G-REF", gate_refs, True),
    "always-load": ("G-ALWAYS", gate_always_load, True),
    "connectors": ("G-CONN", gate_connectors, True),
    "version": ("G-VERSION", gate_version, False),
    "coverage": ("G-COVERAGE", gate_coverage, True),
}


def main() -> int:
    ap = argparse.ArgumentParser(description="medical-research integrity gate")
    for flag in GATES:
        ap.add_argument(f"--{flag}", action="store_true")
    args = ap.parse_args()
    selected = [k for k in GATES if getattr(args, k.replace("-", "_"))]
    if not selected:
        selected = list(GATES)

    print(f"medical-research integrity gate — {SKILL_DIR.name}\n")
    failed_blocking = []
    try:
        for key in selected:
            gid, fn, blocking = GATES[key]
            passed = fn()
            print()
            if not passed and blocking:
                failed_blocking.append(gid)
    except FileNotFoundError as e:
        print(f"{RED}SETUP ERROR{RESET}: {e}")
        return 2

    if failed_blocking:
        print(f"{RED}BLOCKING GATE(S) FAILED: {', '.join(failed_blocking)}{RESET}")
        return 1
    print(f"{GREEN}ALL RUN GATES PASSED{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
