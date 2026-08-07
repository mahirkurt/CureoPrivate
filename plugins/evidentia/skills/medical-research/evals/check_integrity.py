#!/usr/bin/env python3
"""
check_integrity.py — medical-research skill integrity gate (evals harness).

Implements the executable gates declared in skill-manifest.yaml `verification:`:
  --refs        G-REF      every references/*.md cited by SKILL.md exists on disk;
                           mount-tolerant — out-of-tree plugin-root links
                           (../../CONNECTORS.md, ../../shared/…) WARN-skip when the
                           full plugin is not mounted                                   (blocking)
  --connectors  G-CONN     every connector in connector-registry resolves to a
                           runtime.mcp_servers entry in the manifest                    (blocking)
  --always-load G-ALWAYS   the 6 Adim-0 always-load files all present                  (blocking)
  --version     G-VERSION  version stamp agreement: manifest <-> SKILL.md frontmatter
                           <-> SKILL.md H1/changelog                                     (non-blocking)
  --coverage    G-COVERAGE knowledge-map.md exhaustive & consistent vs corpus           (blocking)
  --probe       G-PROBE    every first-class Extended Tier-K/O connector has a WIRE row
                           in the connector-registry §8 Probe Log (probe-verified-only)  (blocking)
  --xval        G-XVAL     each Extended-Tier recipe (SKILL.md Adım 1/B) carries a
                           cross-validation gate                                          (blocking)
  --whitelist   G-WHITELIST no pipeworx-generic tool appears in the §2.6 tool whitelist   (blocking)
  --strict      re-elevate out-of-tree plugin-root ref misses (G-REF) to FAIL, for
                full-plugin-mount CI where the root MUST resolve                        (modifier)
  --agents      G-AGENT    sub-agent `tools:` allowlists cover the MCP fleet and
                           exclude the removed web tier                            (blocking)
  (no flag)     run all gates

Stdlib only (no PyYAML dependency) — the manifest is parsed with lightweight,
structure-aware line scanning. Exit code 0 = all run gates passed; 1 = a blocking
gate failed; 2 = harness/setup error.

This harness ships with the `evidentia` plugin packaging (the source skill cited
evals/check_integrity.py in its manifest but did not ship it). G-REF is now
mount-aware: in a skill-only / flattened / CI / claude.ai-cache checkout the plugin
root is absent, so out-of-tree references (../../CONNECTORS.md,
../../shared/canonical-cache-contract.md) resolve only in a full mount — they are
reported as WARN and skipped (not FAIL) by default, and re-elevated to FAIL under
--strict. In-tree references keep a hard FAIL when missing. Behaviour is faithful to
the manifest spec; the skill's research logic is untouched (ADR-05).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent          # .../skills/medical-research
SKILL_MD = SKILL_DIR / "SKILL.md"
MANIFEST = SKILL_DIR / "skill-manifest.yaml"
REFS_DIR = SKILL_DIR / "references"
CONNECTOR_REGISTRY = REFS_DIR / "connector-registry.md"

ALWAYS_LOAD = [
    "knowledge-map.md", "connector-registry.md", "evidence-grading.md",
    "output-templates.md", "report-presentation.md", "prisma-reporting.md",
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
def gate_refs(strict: bool = False) -> bool:
    """G-REF: every references/*.md cited by SKILL.md exists on disk (mount-tolerant).

    Path-aware: (a) bare `references/<name>.md` paths must exist in references/;
    (b) markdown links `[..](path.md)` are resolved relative to SKILL.md and checked
    at the resolved location.

    Mount-awareness: a (b) link whose resolved target escapes the skill tree
    (e.g. ../../CONNECTORS.md, ../../shared/canonical-cache-contract.md) is a
    *plugin-root* reference — normative, but only resolvable in a FULL plugin mount.
    In a skill-only / flattened / CI / claude.ai-cache checkout the root is absent:
      - target exists  -> PASS (full mount)
      - target absent  -> WARN + skipped from `missing` (mount-tolerant default),
                          unless --strict, which re-elevates it to FAIL (full-mount CI).
    In-tree links keep a hard FAIL when missing (a genuinely deleted ref stays red).
    Plain prose mentions of removed files (e.g. "replaces connector-api.md") are NOT
    citations and are ignored.
    """
    print("G-REF  reference integrity (path-aware, mount-tolerant)")
    skill = _read(SKILL_MD)
    base = SKILL_MD.parent
    missing: list[str] = []
    checked = 0
    skipped = 0

    # (a) references/<name>.md  -> must exist in references/ (always in-tree)
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
        # in-tree vs out-of-tree (plugin-root) classification — stdlib-universal and
        # backward-safe: relative_to()+except, not is_relative_to() (Py3.9+ only).
        try:
            target.relative_to(SKILL_DIR)
            in_tree = True
        except ValueError:
            in_tree = False
        if target.exists():
            _ok(f"link {rel}")
        elif not in_tree:
            # plugin-root ref: resolves only in a full plugin mount
            if strict:
                _fail(f"link {rel}  -> {target} (out-of-tree; --strict)")
                missing.append(rel)
            else:
                _warn(f"link {rel} — plugin-root ref; resolves only in full plugin mount")
                skipped += 1
        else:
            _fail(f"link {rel}  -> {target}")
            missing.append(rel)

    if checked == 0:
        _warn("no references/ citations or .md links found in SKILL.md (unexpected)")
    if missing:
        _fail(f"{len(missing)} cited reference(s) missing: {', '.join(missing)}")
        return False
    resolved = checked - skipped
    msg = f"all {resolved} in-tree/resolved reference(s)/link(s) OK"
    if skipped:
        msg += f"; {skipped} plugin-root ref(s) WARN-skipped (full-mount only)"
    _ok(msg)
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
    core = ["PubMed", "Clinical Trials", "TİTCK", "Mevzuat", "openfda", "AdisInsight", "ChEMBL"]   # v8.5 D-α: Regulatory MCP → openfda
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
      (2) Every PRISMA phase marker (P0 .. P7) found in SKILL.md appears in the map.
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

    # (2) every PRISMA phase marker P0..P7 in SKILL.md appears in the map as a literal token.
    # (P2 Retrieval/Dedup and P6 GRADE have no dedicated phase-file, but the module-index
    # carries explicit P2/P6 phase notes, so a literal-token check suffices.)
    skill_text = _read(SKILL_MD)
    phases = sorted(set(re.findall(r"\bP[0-7]\b", skill_text)))
    for ph in phases:
        if ph in map_text:
            _ok(f"map covers phase {ph}")
        else:
            _fail(f"map omits phase {ph}")
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
        _ok(f"map consistent with corpus ({len(ref_files)} files, {len(phases)} phases, 0 dangling)")
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


# ----------------------------------------------------------------------------- v8.5 gates
def _md_section(text: str, heading_substr: str) -> str:
    """Return the markdown section whose heading contains heading_substr, up to the next
    same-or-higher-level heading (or EOF)."""
    out: list[str] = []
    capturing = False
    level = 0
    for ln in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m and not capturing and heading_substr.lower() in m.group(2).lower():
            capturing, level = True, len(m.group(1))
            out.append(ln)
            continue
        if capturing and m and len(m.group(1)) <= level:
            break
        if capturing:
            out.append(ln)
    return "\n".join(out)


# Extended Tier-K/O connectors that MUST be first-class + probe-evidenced (v8.5)
EXTENDED_TIER = ["med-terminologies", "nih-clinicaltables", "nlm-rxnorm", "iuphar-gtopdb", "drugddx"]

# pipeworx generic tools that must NEVER appear in the §2.6 tool whitelist (least-privilege)
PIPEWORX_GENERIC = {
    "ask_pipeworx", "ask_pipeworx_grounded", "discover_tools", "remember", "recall",
    "forget", "subscribe", "unsubscribe", "list_subscriptions", "validate_claim",
    "suggest_questions", "deep_research", "bet_research", "compare_entities",
    "entity_profile", "resolve_entity", "recent_alerts", "recent_changes",
    "pipeworx_feedback", "pipeworx_trending", "ai_visibility_check", "generate_llms_txt",
    "scan_competitor_ai_presence", "scan_dependency", "search_within",
    "polymarket_arbitrage", "polymarket_edges", "polymarket_edge_tracker",
    "polymarket_fill_risk", "polymarket_kalshi_spread",
}


def gate_probe() -> bool:
    """G-PROBE: every first-class Extended Tier-K/O connector has a WIRE row in the
    connector-registry §8 Probe Log — probe-verified-only (DEĞİŞMEZ 2: no remembered
    liveness without on-disk probe evidence)."""
    print("G-PROBE  Extended-Tier connectors ⇄ §8 Probe Log evidence")
    if not CONNECTOR_REGISTRY.exists():
        _fail("connector-registry.md absent")
        return False
    probe = _md_section(_read(CONNECTOR_REGISTRY), "Probe Log")
    if not probe.strip():
        _fail("no 'Probe Log' section in connector-registry.md (FAZ 0.3)")
        return False
    if not re.search(r"20\d\d-\d\d-\d\d", probe):
        _warn("Probe Log has no ISO date stamp")
    # Only TABLE ROWS count as probe evidence — a prose legend ("classified WIRE / DEGRADE /
    # DECLINE") must NOT satisfy the gate. A row is a line starting with '|'.
    rows = [l for l in probe.splitlines() if l.strip().startswith("|")]
    ok = True
    for c in EXTENDED_TIER + ["PopHIVE"]:
        row = next((l for l in rows if c in l and re.search(r"\bWIRE", l)), None)
        if row:
            _ok(f"{c} — WIRE table-row in Probe Log")
        else:
            _fail(f"{c} — no WIRE table-row in Probe Log (probe-verified-only)")
            ok = False
    return ok


def gate_xval() -> bool:
    """G-XVAL: each Extended-Tier recipe in SKILL.md Adım 1/B carries an explicit
    cross-validation gate (patient-impacting output confirmed against an authoritative
    source, DEĞİŞMEZ 4)."""
    print("G-XVAL  Extended-Tier recipes carry a cross-validation gate")
    skill = _read(SKILL_MD)
    if "Extended Tier-K" not in skill:
        _fail("SKILL.md has no 'Extended Tier-K' recipe block (Adım 1/B)")
        return False
    block = skill.split("Extended Tier-K", 1)[1].split("\n## ", 1)[0]
    recipes = ["Terminology", "normalization", "Clinical DDI", "Mechanism"]
    cues = ["cross-validate", "cross-validation", "çapraz-doğrula", "authoritative", "licensed source"]
    ok = True
    for r in recipes:
        idx = block.lower().find(r.lower())
        if idx < 0:
            _fail(f"recipe '{r}' missing from Extended-Tier block")
            ok = False
            continue
        # Bound the scan to THIS recipe bullet only (up to the next "- " bullet) so a
        # neighbouring recipe's cross-validation cue cannot bleed in and mask a stripped gate.
        nxt = block.find("\n- ", idx + 1)
        seg = (block[idx:nxt] if nxt > idx else block[idx: idx + 600]).lower()
        if any(c in seg for c in cues):
            _ok(f"recipe '{r}' → cross-validation gate present")
        else:
            _fail(f"recipe '{r}' → no cross-validation gate")
            ok = False
    return ok


def gate_whitelist() -> bool:
    """G-WHITELIST: no pipeworx-generic tool name appears in the connector-registry §2.6
    tool whitelist column (tool-level least-privilege, DEĞİŞMEZ 5)."""
    print("G-WHITELIST  no pipeworx-generic tool in the §2.6 whitelist")
    if not CONNECTOR_REGISTRY.exists():
        _fail("connector-registry.md absent")
        return False
    sec = _md_section(_read(CONNECTOR_REGISTRY), "Extended Terminology")
    if not sec.strip():
        _fail("no §2.6 'Extended Terminology / Pharmacology Tier' section")
        return False
    whitelist_cells: list[str] = []
    for ln in sec.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith("**"):   # data row (connector bolded)
            whitelist_cells.append(cells[2])
    if not whitelist_cells:
        _fail("could not parse §2.6 whitelist column")
        return False
    blob = " ".join(whitelist_cells).lower()
    leaked = sorted({g for g in PIPEWORX_GENERIC if re.search(r"\b" + re.escape(g) + r"\b", blob)})
    _ok(f"parsed {len(whitelist_cells)} §2.6 whitelist cell(s)")
    if leaked:
        _fail(f"pipeworx-generic tool(s) leaked into whitelist: {', '.join(leaked)}")
        return False
    _ok("no pipeworx-generic tool in the §2.6 whitelist")
    return True


PHASE_FILES = {
    "P0": "prisma-protocol.md", "P1": "search-strategy.md", "P3": "screening.md",
    "P4": "data-extraction.md", "P5": "risk-of-bias.md", "P7": "prisma-reporting.md",
}
DOMAIN_LAYERS = [
    "oncology-layer.md", "hematology-layer.md", "immunology-layer.md",
    "neurology-layer.md", "rare-disease-layer.md", "drug-intelligence-layer.md",
    "regulatory-intelligence.md", "regulatory-science-layer.md", "hta-layer.md",
    "medaffairs-ops-layer.md", "turkiye-layer.md",
]


def gate_phases() -> bool:
    """G-PHASES: SKILL.md declares P0..P7 and points each defined phase at its reference file."""
    print("G-PHASES  PRISMA pipeline phases present")
    skill = _read(SKILL_MD)
    ok = True
    for ph in ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"]:
        if re.search(r"\b" + ph + r"\b", skill):
            _ok(f"phase {ph} declared")
        else:
            _fail(f"phase {ph} missing from SKILL.md")
            ok = False
    for ph, fname in PHASE_FILES.items():
        if fname in skill:
            _ok(f"{ph} points at {fname}")
        else:
            _fail(f"{ph} does not point at {fname}")
            ok = False
    return ok


def gate_deskew() -> bool:
    """G-DESKEW: no domain layer is mandatorily loaded in the default path. Every domain
    layer reference in SKILL.md sits under the optional/enrichment framing, never an
    'always'/'mandatorily loaded' directive."""
    print("G-DESKEW  domain layers are optional (de-skew invariant)")
    skill = _read(SKILL_MD)
    ok = True
    # A bare "mandator" substring check collides with its own negation ("non-mandatory",
    # "not mandatory") — the same class of false-positive as G-DESC's SMA/PRISMA collision.
    # Only flag an un-negated "mandator" mention.
    mandator_re = re.compile(r"(?<!non-)(?<!non )(?<!not )mandator")
    for layer in DOMAIN_LAYERS:
        for m in re.finditer(re.escape(layer), skill):
            # inspect the line containing this mention
            line_start = skill.rfind("\n", 0, m.start()) + 1
            line_end = skill.find("\n", m.start())
            line = skill[line_start: line_end if line_end > 0 else len(skill)].lower()
            if mandator_re.search(line) or "always-load" in line or "always load" in line or "zorunlu" in line:
                _fail(f"{layer} referenced as mandatory/always: '{line.strip()[:80]}'")
                ok = False
    if ok:
        _ok(f"all {len(DOMAIN_LAYERS)} domain layers referenced as optional/enrichment")
    return ok


SKILL_MAX_LINES = 500
DESC_MAX_CHARS = 1024
# therapeutic-area / commercial triggers that must NOT dominate the general description
FORBIDDEN_DESC_TRIGGERS = [
    "CAR-T", "bispecific", "myeloma", "JAK", " MS,", "SMA", "Alzheimer", "ADC",
    "BTK", "MRD", "PDUFA", "biosimilar", "SGK", "SUT", "biyobenzer",
]
# general systematic-review triggers that MUST appear
REQUIRED_DESC_TRIGGERS = ["systematic", "PRISMA", "PICO"]


def _skill_description() -> str:
    """Extract the YAML frontmatter `description:` block value from SKILL.md."""
    text = _read(SKILL_MD)
    m = re.search(r"^description:\s*>?\s*\n((?:[ \t]+.*\n)+)", text, re.MULTILINE)
    if m:
        return " ".join(l.strip() for l in m.group(1).splitlines())
    m2 = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    return m2.group(1).strip() if m2 else ""


def gate_size() -> bool:
    """G-SIZE: SKILL.md body < 500 lines (Talimatname §3.2.1)."""
    print("G-SIZE  SKILL.md line budget")
    n = len(_read(SKILL_MD).splitlines())
    if n < SKILL_MAX_LINES:
        _ok(f"SKILL.md {n} lines (< {SKILL_MAX_LINES})")
        return True
    _fail(f"SKILL.md {n} lines (>= {SKILL_MAX_LINES}) — split into references/")
    return False


def gate_desc() -> bool:
    """G-DESC: description <=1024 chars, general PRISMA triggers present, no
    therapeutic-area/commercial trigger domination (de-skew invariant)."""
    print("G-DESC  skill description hygiene (de-skew)")
    desc = _skill_description()
    ok = True
    if not desc:
        _fail("no description: block parsed from SKILL.md frontmatter")
        return False
    if len(desc) <= DESC_MAX_CHARS:
        _ok(f"description {len(desc)} chars (<= {DESC_MAX_CHARS})")
    else:
        _fail(f"description {len(desc)} chars (> {DESC_MAX_CHARS})")
        ok = False
    missing = [t for t in REQUIRED_DESC_TRIGGERS if t.lower() not in desc.lower()]
    if missing:
        _fail(f"description missing required general trigger(s): {', '.join(missing)}")
        ok = False
    else:
        _ok(f"required general triggers present: {', '.join(REQUIRED_DESC_TRIGGERS)}")
    # Word-boundary match: a bare substring check makes "SMA" collide with the mandatory
    # required trigger "PRISMA" (PRI-SMA), which would make G-DESC unsatisfiable. The
    # author's " MS," spacing hack shows boundary intent; enforce it uniformly.
    def _forbidden_hit(t: str, hay: str) -> bool:
        return re.search(r"(?<![a-z])" + re.escape(t.lower().strip()) + r"(?![a-z])", hay) is not None
    leaked = [t for t in FORBIDDEN_DESC_TRIGGERS if _forbidden_hit(t, desc.lower())]
    if leaked:
        _fail(f"therapeutic-area/commercial trigger(s) dominate description: {', '.join(leaked)}")
        ok = False
    else:
        _ok("no therapeutic-area/commercial trigger domination")
    return ok



def gate_agents() -> bool:
    """G-AGENT: every plugin sub-agent that is told to orchestrate the MCP fleet actually has
    MCP tools in its `tools:` allowlist, and none of them carries the removed web tier.

    Why this gate exists (2026-08-07). `agents/evidence-synthesizer.md` shipped with
    `tools: Read, Bash, Glob, Grep, WebFetch, WebSearch` — not one MCP entry. Because `tools:`
    is an ALLOWLIST, the plugin's flagship isolation agent could not reach any of the 20
    evidence connectors its own body instructs it to drive, while it COULD reach `WebSearch`,
    the tier the skill removed in v1.4.0 and forbids in eight places. Provisioned exactly
    inverse to its contract, a run would either come back empty or fall back to web search —
    the worst possible failure mode for a no-fabrication plugin. Nothing caught it, because
    every existing gate reads the skill and the connectors, never the agents.

    Mount-tolerant: skips with a WARN when the plugin root is not mounted (skill-only checkout).
    """
    print("G-AGENT   sub-agent tool allowlists cover the fleet, and exclude the removed web tier")
    agents_dir = SKILL_DIR.parent.parent / "agents"
    lock = SKILL_DIR.parent.parent / "fleet.lock.json"
    if not agents_dir.is_dir() or not lock.exists():
        _warn("plugin root not mounted (agents/ or fleet.lock.json absent) — skipped")
        return True
    fleet = [s["name"] for s in json.loads(lock.read_text(encoding="utf-8"))["servers"]]
    ok = True
    for md in sorted(agents_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        m = re.search(r"^tools:\s*(.+)$", text, re.M)
        if not m:
            _warn(f"{md.name}: no `tools:` line — inherits the default set, not gated here")
            continue
        tools = [x.strip() for x in m.group(1).split(",")]
        if "WebSearch" in tools:
            _fail(f"{md.name}: grants WebSearch — the web/OSINT tier was removed in v1.4.0 "
                  f"and discovery-by-web is forbidden (fetching a URL an authoritative "
                  f"connector RETURNED is what WebFetch is for)")
            ok = False
        # An agent that never mentions a connector is not an orchestrator; only gate the ones
        # whose body actually names fleet servers.
        drives_fleet = sum(1 for s in fleet if s in text) >= 3
        if not drives_fleet:
            _ok(f"{md.name}: not a fleet orchestrator — MCP allowlist not required")
            continue
        missing = [s for s in fleet if f"mcp__{s}__*" not in m.group(1)]
        if missing:
            _fail(f"{md.name}: drives the fleet but its allowlist omits "
                  f"{len(missing)}/{len(fleet)} server(s): {', '.join(missing[:6])}"
                  + (" …" if len(missing) > 6 else ""))
            ok = False
        else:
            _ok(f"{md.name}: allowlist covers all {len(fleet)} fleet servers")
    return ok


GATES = {
    "refs": ("G-REF", gate_refs, True),
    "always-load": ("G-ALWAYS", gate_always_load, True),
    "connectors": ("G-CONN", gate_connectors, True),
    "version": ("G-VERSION", gate_version, False),
    "coverage": ("G-COVERAGE", gate_coverage, True),
    "probe": ("G-PROBE", gate_probe, True),
    "xval": ("G-XVAL", gate_xval, True),
    "whitelist": ("G-WHITELIST", gate_whitelist, True),
    "size": ("G-SIZE", gate_size, True),
    "desc": ("G-DESC", gate_desc, True),
    "phases": ("G-PHASES", gate_phases, True),
    "deskew": ("G-DESKEW", gate_deskew, True),
    "agents": ("G-AGENT", gate_agents, True),
}


def main() -> int:
    ap = argparse.ArgumentParser(description="medical-research integrity gate")
    for flag in GATES:
        ap.add_argument(f"--{flag}", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="G-REF: re-elevate out-of-tree plugin-root ref misses to FAIL (full-mount CI)")
    args = ap.parse_args()
    selected = [k for k in GATES if getattr(args, k.replace("-", "_"))]
    if not selected:
        selected = list(GATES)

    print(f"medical-research integrity gate — {SKILL_DIR.name}\n")
    failed_blocking = []
    try:
        for key in selected:
            gid, fn, blocking = GATES[key]
            passed = fn(strict=args.strict) if key == "refs" else fn()
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
