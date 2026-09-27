#!/usr/bin/env python3
"""cureolex paket denetimleri — run_suites.py [8] tarafından çağrılır (AĞ ERİŞİMİ YOK).

Her denetim `(root, fleet) -> (errors, warnings)` imzasını taşır; her öğe
`(bağlam, mesaj)` ikilisidir. Yeni denetim CHECKS listesine eklenir.
"""
import json
import re
from pathlib import Path

SNAKE = r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+"
_MCP_PREFIX = re.compile(r"mcp__[A-Za-z0-9_-]+?__")
_CALL = re.compile(r"(?<![\w.])(" + SNAKE + r")\(")
_CHAIN_LEFT = re.compile(r"(?<![\w.])`?(" + SNAKE + r")(?:\([^)\n]*\))?`?\s*(?:→|->)")
_CHAIN_RIGHT = re.compile(r"(?:→|->)\s*`?(" + SNAKE + r")(?![\w.])")
# YAML/pseudo-call anahtarı: `mcp_call: <ad>` — bir çağrı biçimidir (spec §1.3
# başarı ölçütü 2: "çağrı biçiminde anılan her araç adı"). Yalnız bu anahtarla
# dar tutulur; genel `<kelime>: <kelime>` biçimini yakalamaz.
_MCP_CALL_KEY = re.compile(r"(?<![\w.])mcp_call:\s*`?(" + SNAKE + r")")

TOOL_SCAN_GLOBS = ("skills/**/*.md", "agents/*.md", "commands/*.md", "tests/*.yaml")
SCHEMA_GLOBS = ("skills/*/schemas/*.json", "jurisdictions/_schema/*.json")

# Araç olmayan ama çağrı/zincir biçiminde yazılan tanımlayıcılar. Her girdi bir
# gerekçe yorumu taşır; boş başlar, denetim bulgularına göre dolar.
NON_TOOL_IDENTIFIERS: set = {
    # Durum/etiket sentinelleri (fleet.yaml ve dokümantasyon genelinde dönüş
    # değeri olarak kullanılır — araç değil):
    "manual_required",                    # degrade fallback etiketi
    "illustrative_placeholder_not_verified",  # doğrulanamayan atıf etiketi
    "auth_missing",                       # anahtar-yok durumu etiketi
    "sira_no",                            # tbmm_get_kanun_teklifi PARAMETRESİ
    "excluded_sources",                   # health-policy semantic_search çıktı alanı
    "out_of_scope_flags",                 # evidentia sidecar reverse_signals alanı
    "retry_triggers",                     # evidentia sidecar reverse_signals alanı
    "open_primary_source",                # kaynak-stratejisi registry etiketi (eu.eurovoc)
    "rest_api",                           # yönlendirme stratejisi etiketi (AM-2)
    "web_primary",                        # yönlendirme stratejisi etiketi (AM-2)
    # references/14b — Python pseudocode işlev adları (def ...), MCP aracı değil:
    "consume_medical_research_output", "check_version_compatibility",
    "handle_reverse_signals", "get_current_cureolex_mode",
    "validate_vancouver_format", "flag_unverified_reference",
    "validate_judicial_citations", "compute_combined_confidence",
    "validate_ex_post_completeness", "assemble_cureolex_output",
    "add_footnote_to_section", "add_user_recommendation",
    "is_critical_missing_layer", "inject_keywords", "retry_medical_research",
    "add_to_executive_summary",
    # references/15 — health-policy rescope'unda (2026-06-29) KALDIRILAN eski
    # araç adları; artık hiçbir sunucu tarafından sarılmıyor, yalnız tarihsel
    # emeklilik notunda anılır (çağrılamaz):
    "dataeuropa_dataset_search", "fedlex_fetch_document", "uk_legislation_fetch",
}


def tool_references(text: str) -> set:
    """Metindeki araç atıfları: çağrı biçimi `ad(`, `→`/`->` zinciri halkası ya da
    `mcp_call: ad` YAML/pseudo-call anahtarı."""
    text = _MCP_PREFIX.sub(" ", text)
    return (set(_CALL.findall(text)) | set(_CHAIN_LEFT.findall(text))
            | set(_CHAIN_RIGHT.findall(text)) | set(_MCP_CALL_KEY.findall(text)))


def known_tools(fleet: dict) -> set:
    names = set()
    for s in fleet.get("servers", []):
        names |= set(s.get("tools_used", [])) | set(s.get("tools_fallback", []))
    for c in fleet.get("companions", []):
        names |= set(c.get("tools", []))
    return names


def _schema_keys(obj, out: set) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "properties" and isinstance(v, dict):
                out |= set(v)
            _schema_keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _schema_keys(v, out)


def schema_field_names(root: Path) -> set:
    """Şema özellik adları + şema dosya kökleri: zincirde yazılsalar da araç değildir."""
    out = set()
    for g in SCHEMA_GLOBS:
        for p in root.glob(g):
            out.add(p.name.split(".")[0])
            try:
                _schema_keys(json.loads(p.read_text(encoding="utf-8")), out)
            except json.JSONDecodeError:
                continue
    return out


def check_tool_names(root: Path, fleet: dict):
    known = known_tools(fleet) | schema_field_names(root) | NON_TOOL_IDENTIFIERS
    errors = []
    for g in TOOL_SCAN_GLOBS:
        for p in sorted(root.glob(g)):
            rel = str(p.relative_to(root))
            for ref in sorted(tool_references(p.read_text(encoding="utf-8")) - known):
                errors.append((rel, f"araç listelerinde OLMAYAN araç adı '{ref}' (hayalet?)"))
    return errors, []


CHECKS = [check_tool_names]


def run_all(root: Path, fleet: dict):
    errors, warnings = [], []
    for chk in CHECKS:
        e, w = chk(root, fleet)
        errors += e
        warnings += w
    return errors, warnings
