#!/usr/bin/env python3
"""Domain-agnostic Turkish scientific writing audit (sci-audit axis G).

Ported from the doktoratezi repo's `tr_sciaudit.py` with two structural
changes for the claude.ai-web / plugin environment:

  1. STDLIB-ONLY NETWORKING. All `requests` usage is replaced with
     `urllib.request`. The deterministic G1-G6 core needs no network at all;
     the optional TDK and GECTurk providers use urllib and degrade safely.
  2. LLM JUDGE REMOVED FROM THE DETERMINISTIC CORE. The original Grok/xAI
     adapter is gone from this file. The web-native replacement is the
     `style-judge` Claude subagent (see agents/style-judge.md). The
     `--enable-grok`/`--enable-llm` flags are preserved for CLI muscle memory
     but return an 'unavailable' provider result that points to the subagent
     and the CI reliability layer — NO text is ever sent from here.

Domain-specific whitelists (project abbreviations, project English-term leaks)
are NOT hardcoded. Extend them at runtime via `--abbreviations` and `--terms`.

Scope note: this checks Turkish scientific-writing SIGNALS only. It does not
certify scientific truth, citation validity, plagiarism, or clinical validity —
those are other sci-audit axes (A-F).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Literal


Severity = Literal["error", "warning", "info"]
ProviderStatus = Literal["ok", "skipped", "unavailable", "error"]

TURKISH_VOWELS = "aeiouAEIOUıİöÖüÜâÂîÎûÛ"
WORD_RE = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû]+(?:['’][A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû]+)?")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ0-9])")

# Generic scientific / statistical / file-format abbreviations that are common
# enough across domains to skip the "expand at first use" heuristic. Project-
# specific abbreviations are supplied via --abbreviations, never hardcoded.
COMMON_ABBREVIATIONS = {
    "AI", "ANOVA", "ANCOVA", "API", "APA", "BMI", "CI", "CONSORT", "COREQ",
    "CSV", "DNA", "DOCX", "DOI", "FDA", "GRIM", "HR", "HTML", "ICMJE", "IQR",
    "JARS", "JSON", "KVKK", "LLM", "MCP", "MRI", "OR", "PDF", "PII", "PMCID",
    "PMID", "PRISMA", "RCT", "RNA", "ROC", "RR", "SD", "SE", "SEM", "SPSS",
    "SRQR", "STROBE", "TDK", "TRIPOD", "URL", "WHO", "XML", "YÖK",
}

DIACRITIC_CANDIDATES = {
    "Turkce": "Turkish diacritic likely missing: Turkce -> Türkçe.",
    "calisma": "Turkish diacritic likely missing: calisma -> çalışma.",
    "yontem": "Turkish diacritic likely missing: yontem -> yöntem.",
    "cocuk": "Turkish diacritic likely missing: cocuk -> çocuk.",
    "olcek": "Turkish diacritic likely missing: olcek -> ölçek.",
    "giris": "Turkish diacritic likely missing: giris -> giriş.",
    "amac": "Turkish diacritic likely missing: amac -> amaç.",
    "arastirma": "Turkish diacritic likely missing: arastirma -> araştırma.",
    "olcum": "Turkish diacritic likely missing: olcum -> ölçüm.",
}

COLLOQUIAL_PATTERNS = {
    r"\bbir sürü\b": "Colloquial expression; prefer a precise academic quantity or remove.",
    r"\bşey\b": "Vague word; replace with a specific academic noun.",
    r"\bçok fazla\b": "Vague intensifier; prefer a measurable or restrained expression.",
    r"\bgayet\b": "Informal intensifier; prefer academic phrasing.",
    r"\bbayağı\b": "Informal intensifier; prefer academic phrasing.",
}

FIRST_PERSON_PATTERNS = {
    r"\bben\b": "First-person singular is not appropriate for scientific prose.",
    r"\bbiz\b": "First-person plural is usually not appropriate for scientific prose.",
    r"\bçalışmamız\b": "Prefer impersonal phrasing such as 'bu çalışma'.",
    r"\baraştırmamız\b": "Prefer impersonal phrasing such as 'bu araştırma'.",
    r"\binceledik\b": "Prefer passive or impersonal academic phrasing.",
    r"\bdeğerlendirdik\b": "Prefer passive or impersonal academic phrasing.",
    r"\bbulduk\b": "Prefer passive or impersonal academic phrasing.",
}

CAUSAL_OVERCLAIM_PATTERNS = {
    r"\bkanıtlamaktadır\b": "Strong proof language; verify that the design supports this claim.",
    r"\bkanıtlar\b": "Strong proof language; consider 'göstermektedir' if appropriate.",
    r"\bneden olur\b": "Causal wording; verify causal design or soften.",
    r"\bneden olmaktadır\b": "Causal wording; verify causal design or soften.",
    r"\bsebep olur\b": "Causal wording; verify causal design or soften.",
    r"\byol açar\b": "Causal wording; verify causal design or soften.",
    r"\bsağlar\b": "Possible causal overclaim; verify the design supports it.",
}

# Generic English-term leaks common in Turkish scientific prose. Extend with
# --terms for domain-specific terms; nothing here is disease/topic-specific.
ENGLISH_LEAK_PATTERNS = {
    r"\boutcome\b": "Use a Turkish term such as 'sonuç' or 'çıktı' unless a technical definition requires English.",
    r"\bbaseline\b": "Use 'başlangıç' / 'temel düzey' unless quoting.",
    r"\bfollow[- ]?up\b": "Use 'izlem' / 'takip' unless quoting.",
    r"\bsample size\b": "Use 'örneklem büyüklüğü' unless quoting.",
    r"\bframework\b": "Use 'çerçeve' unless explicitly defining an English construct.",
    r"\bsignificant\b": "Use 'anlamlı' unless quoting.",
}

DEFAULT_TERMS = ["yöntem", "bulgu", "örneklem", "değişken", "ölçek", "anlamlı"]
DEFAULT_TDK_URL = "https://sozluk.gov.tr/gts"
USER_AGENT = "sci-audit-tr/0.1"


@dataclass
class Issue:
    severity: Severity
    code: str
    line: int
    message: str
    evidence: str


@dataclass
class Metrics:
    paragraphs: int
    sentences: int
    words: int
    syllables: int
    average_words_per_sentence: float
    average_syllables_per_word: float
    atesman_score: float | None
    atesman_label: str


@dataclass
class ProviderResult:
    provider: str
    enabled: bool
    status: ProviderStatus
    summary: str
    findings: list[dict[str, Any]]


@dataclass
class ExternalConfig:
    enable_zemberek: bool = False
    enable_gecturk: bool = False
    enable_tdk: bool = False
    enable_grok: bool = False
    gecturk_url: str | None = None
    tdk_url: str = DEFAULT_TDK_URL
    terms: list[str] | None = None


@dataclass
class AuditReport:
    path: str
    strictness: str
    metrics: Metrics
    issues: list[Issue]
    providers: list[ProviderResult]
    human_review_required: bool = True
    scope_note: str = (
        "This audit checks Turkish scientific writing signals only (sci-audit "
        "axis G); it does not certify scientific truth, citation validity, "
        "plagiarism, or clinical validity (see axes A-F)."
    )


# --- Text extraction -------------------------------------------------------

def strip_qmd_noise(text: str) -> list[tuple[int, str]]:
    """Return prose-ish lines with original line numbers (YAML/fences dropped)."""
    kept: list[tuple[int, str]] = []
    in_yaml = False
    in_fence = False
    first_nonempty_seen = False

    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        if not first_nonempty_seen and not stripped:
            continue
        if not first_nonempty_seen and stripped == "---":
            in_yaml = True
            first_nonempty_seen = True
            continue
        first_nonempty_seen = True

        if in_yaml:
            if stripped == "---":
                in_yaml = False
            continue

        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            continue

        kept.append((lineno, line.rstrip("\n")))
    return kept


def normalize_prose(line: str) -> str:
    line = re.sub(r"`[^`]*`", " ", line)
    line = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", line)
    line = re.sub(r"\[@[^\]]+\]", " ", line)
    line = re.sub(r"@[-A-Za-z0-9_:.]+", " ", line)
    line = re.sub(r"\{#[-A-Za-z0-9_:.]+\}", " ", line)
    line = re.sub(r"^#+\s*", "", line.strip())
    return re.sub(r"\s+", " ", line).strip()


def build_paragraphs(lines: Iterable[tuple[int, str]]) -> list[tuple[int, str]]:
    paragraphs: list[tuple[int, str]] = []
    current: list[str] = []
    start_line = 0

    for lineno, raw in lines:
        if not raw.strip():
            if current:
                paragraphs.append((start_line, " ".join(current)))
                current = []
            continue
        if raw.lstrip().startswith("#"):
            if current:
                paragraphs.append((start_line, " ".join(current)))
                current = []
            continue
        text = normalize_prose(raw)
        if not text:
            continue
        if not current:
            start_line = lineno
        current.append(text)

    if current:
        paragraphs.append((start_line, " ".join(current)))
    return paragraphs


def split_sentences(paragraph: str) -> list[str]:
    protected = paragraph
    protected = re.sub(r"\bDr\.", "Dr<DOT>", protected)
    protected = re.sub(r"\bProf\.", "Prof<DOT>", protected)
    protected = re.sub(r"\bDoç\.", "Doç<DOT>", protected)
    protected = re.sub(r"\börn\.", "örn<DOT>", protected, flags=re.IGNORECASE)
    protected = re.sub(r"\bvb\.", "vb<DOT>", protected, flags=re.IGNORECASE)
    parts = [p.replace("<DOT>", ".").strip() for p in SENTENCE_SPLIT_RE.split(protected)]
    return [p for p in parts if p]


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def syllable_count(word: str) -> int:
    count = sum(1 for char in word if char in TURKISH_VOWELS)
    return max(1, count)


def atesman_label(score: float | None) -> str:
    if score is None:
        return "not-available"
    if score >= 90:
        return "very-easy"
    if score >= 70:
        return "easy"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "hard"
    return "very-hard"


def calculate_metrics(paragraphs: list[tuple[int, str]]) -> Metrics:
    sentence_count = 0
    word_count = 0
    syllable_total = 0

    for _, paragraph in paragraphs:
        sentence_count += len(split_sentences(paragraph))
        paragraph_words = words(paragraph)
        word_count += len(paragraph_words)
        syllable_total += sum(syllable_count(word) for word in paragraph_words)

    avg_wps = word_count / sentence_count if sentence_count else 0.0
    avg_spw = syllable_total / word_count if word_count else 0.0
    score = None
    if sentence_count and word_count:
        # Ateşman (1997) Turkish readability formula.
        score = 198.825 - 40.175 * avg_spw - 2.610 * avg_wps

    return Metrics(
        paragraphs=len(paragraphs),
        sentences=sentence_count,
        words=word_count,
        syllables=syllable_total,
        average_words_per_sentence=round(avg_wps, 2),
        average_syllables_per_word=round(avg_spw, 2),
        atesman_score=round(score, 2) if score is not None else None,
        atesman_label=atesman_label(score),
    )


# --- Deterministic issue detection (G1-G6) --------------------------------

def trim_evidence(text: str, limit: int = 140) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def add_regex_issues(
    issues: list[Issue],
    paragraph: str,
    line: int,
    patterns: dict[str, str],
    code: str,
    severity: Severity,
    flags: int = re.IGNORECASE,
) -> None:
    for pattern, message in patterns.items():
        for match in re.finditer(pattern, paragraph, flags=flags):
            issues.append(
                Issue(
                    severity=severity,
                    code=code,
                    line=line,
                    message=message,
                    evidence=trim_evidence(match.group(0)),
                )
            )


def detect_abbreviations(paragraph: str, line: int, whitelist: set[str]) -> list[Issue]:
    issues: list[Issue] = []
    candidates = set(re.findall(r"\b[A-ZÇĞİÖŞÜ]{2,}(?:-[A-ZÇĞİÖŞÜ0-9]+)*\b", paragraph))
    for candidate in sorted(candidates):
        if re.fullmatch(r"[IVXLCDM]+", candidate):
            continue
        if candidate.endswith("-"):
            continue
        if candidate in whitelist:
            continue
        if any(part in whitelist for part in candidate.split("-")):
            continue
        if re.search(rf"\({re.escape(candidate)}\)", paragraph):
            continue
        issues.append(
            Issue(
                severity="info",
                code="abbreviation-review",
                line=line,
                message="Check whether this abbreviation is expanded at first use and used consistently.",
                evidence=candidate,
            )
        )
    return issues


def detect_issues(
    lines: list[tuple[int, str]],
    paragraphs: list[tuple[int, str]],
    strictness: str,
    abbreviations: set[str],
) -> list[Issue]:
    issues: list[Issue] = []

    for lineno, raw in lines:
        # G1: encoding artefacts / mojibake / replacement chars.
        if "�" in raw or "Ä" in raw or "Å" in raw:
            issues.append(
                Issue("error", "encoding-artifact", lineno,
                      "Possible mojibake or replacement character in Turkish text.",
                      trim_evidence(raw))
            )
        if re.search(r"[ \t]+[,.!?;:]", raw):
            issues.append(
                Issue("warning", "space-before-punctuation", lineno,
                      "Remove whitespace before punctuation.", trim_evidence(raw))
            )
        if re.search(r"\S {2,}\S", raw):
            issues.append(
                Issue("warning", "multiple-spaces", lineno,
                      "Collapse repeated spaces in prose.", trim_evidence(raw))
            )

    for line, paragraph in paragraphs:
        paragraph_words = words(paragraph)
        word_count = len(paragraph_words)
        # G2: readability / paragraph length.
        if word_count > 260:
            issues.append(
                Issue("warning", "paragraph-too-long", line,
                      "Paragraph is too long for scientific readability.", trim_evidence(paragraph))
            )
        elif word_count > 180:
            issues.append(
                Issue("warning", "paragraph-long", line,
                      "Consider splitting this long paragraph.", trim_evidence(paragraph))
            )

        for sentence in split_sentences(paragraph):
            sentence_words = len(words(sentence))
            if sentence_words > 55:
                issues.append(
                    Issue("warning", "sentence-too-long", line,
                          "Sentence exceeds 55 words; split or simplify.", trim_evidence(sentence))
                )
            elif sentence_words > 38:
                issues.append(
                    Issue("warning", "sentence-long", line,
                          "Sentence is long; check readability and ambiguity.", trim_evidence(sentence))
                )

        repeated = re.search(r"\b([A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû]{2,})\s+\1\b", paragraph, flags=re.IGNORECASE)
        if repeated:
            issues.append(
                Issue("warning", "repeated-word", line, "Repeated adjacent word.", trim_evidence(repeated.group(0)))
            )

        # G1: missing-diacritic signals.
        for candidate, message in DIACRITIC_CANDIDATES.items():
            if message and re.search(rf"\b{re.escape(candidate)}\b", paragraph):
                issues.append(Issue("warning", "missing-diacritic", line, message, candidate))

        # G3: academic register + G4: causal/generalisation overclaim.
        add_regex_issues(issues, paragraph, line, COLLOQUIAL_PATTERNS, "colloquial-register", "warning")
        add_regex_issues(issues, paragraph, line, FIRST_PERSON_PATTERNS, "first-person-register", "warning")
        add_regex_issues(issues, paragraph, line, CAUSAL_OVERCLAIM_PATTERNS, "causal-overclaim", "warning")
        add_regex_issues(issues, paragraph, line, ENGLISH_LEAK_PATTERNS, "english-term-leak", "warning")

        # G5: decimal comma + APA-TR p-value form. English decimal-dot p-value
        # is an ERROR (hard blocker per stop hook); other decimal dots warn.
        for match in re.finditer(r"\bp\s*[<=>]\s*0?\.\d+", paragraph):
            issues.append(
                Issue("error", "decimal-dot-p-value", line,
                      "Use the Turkish decimal comma in p values, e.g. p<0,001.",
                      trim_evidence(match.group(0)))
            )
        for match in re.finditer(r"(?<![\w@])\d+\.\d+(?![\w])", paragraph):
            issues.append(
                Issue("warning", "decimal-dot", line,
                      "Use the decimal comma in Turkish scientific prose unless this is a version number or identifier.",
                      trim_evidence(match.group(0)))
            )

        # G6: abbreviation consistency (certification strictness only).
        if strictness == "certification":
            issues.extend(detect_abbreviations(paragraph, line, abbreviations))

    return issues


# --- Optional provider layers (stdlib urllib; safe degrade) ---------------

def provider_skipped(provider: str, reason: str) -> ProviderResult:
    return ProviderResult(provider, False, "skipped", reason, [])


def run_zemberek_layer(paragraphs: list[tuple[int, str]], enabled: bool) -> ProviderResult:
    if not enabled:
        return provider_skipped("zemberek", "Not requested. Use --enable-zemberek.")
    try:
        from zemberek import TurkishMorphology  # type: ignore
    except Exception as exc:
        return ProviderResult(
            "zemberek", True, "unavailable",
            "Python zemberek package is not installed/importable; provider is unavailable (report not blocked).",
            [{"error": type(exc).__name__}],
        )
    try:
        morphology = TurkishMorphology.create_with_defaults()
        sample_words: list[str] = []
        seen: set[str] = set()
        for _, paragraph in paragraphs:
            for word in words(paragraph):
                normalized = word.strip("’'").lower()
                if len(normalized) < 3 or normalized in seen:
                    continue
                seen.add(normalized)
                sample_words.append(normalized)
                if len(sample_words) >= 80:
                    break
            if len(sample_words) >= 80:
                break
        unknown: list[str] = []
        analyzed = 0
        for word in sample_words:
            analyses = morphology.analyze(word)
            try:
                analysis_count = len(list(analyses))
            except TypeError:
                analysis_count = len(analyses) if hasattr(analyses, "__len__") else 1
            if analysis_count == 0:
                unknown.append(word)
            else:
                analyzed += 1
        return ProviderResult(
            "zemberek", True, "ok",
            f"Zemberek morphology ran on {len(sample_words)} unique words; {analyzed} had at least one analysis.",
            [{"unknown_words_sample": unknown[:20]}] if unknown else [],
        )
    except Exception as exc:
        return ProviderResult(
            "zemberek", True, "error", "Zemberek adapter failed while running morphology.",
            [{"error": type(exc).__name__, "message": str(exc)[:300]}],
        )


def _http_post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (trusted self-host URL)
        body = resp.read().decode("utf-8", errors="replace")
        status = resp.getcode()
    try:
        return status, json.loads(body)
    except ValueError:
        return status, {"text_excerpt": body[:1000]}


def _http_get_json(url: str, params: dict[str, str], timeout: int = 10) -> Any:
    query = urllib.parse.urlencode(params)
    full = f"{url}?{query}"
    req = urllib.request.Request(full, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body)


def run_gecturk_layer(text: str, enabled: bool, url: str | None) -> ProviderResult:
    if not enabled:
        return provider_skipped("gecturk", "Not requested. Use --enable-gecturk.")
    if not url:
        return ProviderResult(
            "gecturk", True, "unavailable",
            "No self-hosted GECTurk endpoint configured. Provide --gecturk-url; no public programmatic API is assumed.",
            [],
        )
    try:
        status, payload = _http_post_json(url, {"text": text[:5000]})
        return ProviderResult(
            "gecturk", True, "ok",
            f"GECTurk endpoint responded with HTTP {status}.",
            [{"response": payload}],
        )
    except Exception as exc:
        return ProviderResult(
            "gecturk", True, "error", "GECTurk endpoint call failed.",
            [{"error": type(exc).__name__, "message": str(exc)[:300]}],
        )


def run_tdk_layer(enabled: bool, terms: list[str], tdk_url: str) -> ProviderResult:
    if not enabled:
        return provider_skipped("tdk", "Not requested. Use --enable-tdk.")
    findings: list[dict[str, Any]] = []
    try:
        for term in terms[:12]:
            payload = _http_get_json(tdk_url, {"ara": term})
            if isinstance(payload, list) and payload:
                first = payload[0]
                meanings = first.get("anlamlarListe") or []
                first_meaning = meanings[0].get("anlam") if meanings and isinstance(meanings[0], dict) else None
                findings.append({
                    "term": term, "found": True,
                    "headword": first.get("madde"), "first_meaning": first_meaning,
                })
            else:
                findings.append({"term": term, "found": False})
        return ProviderResult("tdk", True, "ok", f"TDK lookup completed for {min(len(terms), 12)} terms.", findings)
    except Exception as exc:
        # Safe-fallback contract: TDK error is a provider status, not a report
        # blocker; the deterministic G1-G6 audit still stands.
        return ProviderResult(
            "tdk", True, "error", "TDK lookup failed; deterministic audit is unaffected.",
            [{"error": type(exc).__name__, "message": str(exc)[:300]}],
        )


def run_llm_judge_stub(enabled: bool) -> ProviderResult:
    """The deterministic core does NOT send text to any LLM.

    The web-native register/fluency/terminology judge is the `style-judge`
    Claude subagent (agents/style-judge.md). An external Grok/xAI judge is only
    an optional CI-eval layer (reliability/), never invoked from here.
    """
    if not enabled:
        return provider_skipped("llm-judge", "Not requested. Use the style-judge subagent, or --enable-grok in CI.")
    return ProviderResult(
        "llm-judge", True, "unavailable",
        "No text is sent from this deterministic script. Use the 'style-judge' Claude "
        "subagent for the register/fluency/terminology rubric, or run the optional "
        "Grok CI-eval layer under reliability/ (GROK_API_KEY required there).",
        [],
    )


def run_external_layers(paragraphs: list[tuple[int, str]], config: ExternalConfig) -> list[ProviderResult]:
    text = "\n\n".join(paragraph for _, paragraph in paragraphs)
    terms = config.terms or DEFAULT_TERMS
    return [
        run_zemberek_layer(paragraphs, config.enable_zemberek),
        run_gecturk_layer(text, config.enable_gecturk, config.gecturk_url),
        run_tdk_layer(config.enable_tdk, terms, config.tdk_url),
        run_llm_judge_stub(config.enable_grok),
    ]


# --- Audit orchestration + rendering --------------------------------------

def audit_path(
    path: Path,
    strictness: str,
    external_config: ExternalConfig | None = None,
    extra_abbreviations: set[str] | None = None,
) -> AuditReport:
    raw = path.read_text(encoding="utf-8")
    return audit_text(raw, strictness, str(path), external_config, extra_abbreviations)


def audit_text(
    raw: str,
    strictness: str,
    label: str = "<text>",
    external_config: ExternalConfig | None = None,
    extra_abbreviations: set[str] | None = None,
) -> AuditReport:
    lines = strip_qmd_noise(raw)
    paragraphs = build_paragraphs(lines)
    metrics = calculate_metrics(paragraphs)
    whitelist = set(COMMON_ABBREVIATIONS) | (extra_abbreviations or set())
    issues = detect_issues(lines, paragraphs, strictness, whitelist)
    if strictness == "certification" and metrics.atesman_score is not None and metrics.atesman_score < 25:
        issues.append(
            Issue("warning", "readability-very-hard", 1,
                  "Ateşman score is very low; verify the difficulty is justified by scientific content.",
                  str(metrics.atesman_score))
        )
    providers = run_external_layers(paragraphs, external_config or ExternalConfig())
    return AuditReport(label, strictness, metrics, issues, providers)


def issue_counts(issues: list[Issue]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "info": 0}
    for issue in issues:
        counts[issue.severity] += 1
    return counts


def render_markdown(report: AuditReport) -> str:
    counts = issue_counts(report.issues)
    m = report.metrics
    lines = [
        "# Turkish Scientific Writing Audit (sci-audit axis G)",
        "",
        f"- Path: `{report.path}`",
        f"- Strictness: `{report.strictness}`",
        f"- Human review required: `{str(report.human_review_required).lower()}`",
        f"- Scope note: {report.scope_note}",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Paragraphs | {m.paragraphs} |",
        f"| Sentences | {m.sentences} |",
        f"| Words | {m.words} |",
        f"| Syllables | {m.syllables} |",
        f"| Avg. words/sentence | {m.average_words_per_sentence} |",
        f"| Avg. syllables/word | {m.average_syllables_per_word} |",
        f"| Ateşman score | {m.atesman_score if m.atesman_score is not None else 'NA'} |",
        f"| Ateşman label | {m.atesman_label} |",
        "",
        "## Issue Summary",
        "",
        f"- Errors (blocker): {counts['error']}",
        f"- Warnings (major): {counts['warning']}",
        f"- Info (minor): {counts['info']}",
        "",
        "## Issues",
        "",
    ]
    if not report.issues:
        lines.append("No issues detected by deterministic checks.")
    else:
        lines.extend(["| Severity | Code | Line | Message | Evidence |", "|---|---|---:|---|---|"])
        for issue in report.issues:
            evidence = issue.evidence.replace("|", "\\|")
            message = issue.message.replace("|", "\\|")
            lines.append(f"| {issue.severity} | `{issue.code}` | {issue.line} | {message} | {evidence} |")
    lines.extend(["", "## Provider Layers", "", "| Provider | Enabled | Status | Summary |", "|---|---:|---|---|"])
    for provider in report.providers:
        summary = provider.summary.replace("|", "\\|")
        lines.append(f"| `{provider.provider}` | {str(provider.enabled).lower()} | `{provider.status}` | {summary} |")
    provider_findings = [provider for provider in report.providers if provider.findings]
    if provider_findings:
        lines.extend(["", "## Provider Findings", ""])
        for provider in provider_findings:
            lines.extend([f"### {provider.provider}", "", "```json",
                          json.dumps(provider.findings, ensure_ascii=False, indent=2), "```", ""])
    lines.append("")
    return "\n".join(lines)


def to_json(report: AuditReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def exit_code(report: AuditReport, fail_on: str) -> int:
    counts = issue_counts(report.issues)
    if fail_on == "none":
        return 0
    if fail_on == "warning" and (counts["warning"] or counts["error"]):
        return 1
    if fail_on == "error" and counts["error"]:
        return 1
    return 0


def _read_terms_arg(value: str | None) -> list[str] | None:
    if not value:
        return None
    # Accept a comma list or a file path.
    p = Path(value)
    if p.exists():
        raw = p.read_text(encoding="utf-8")
        return [t.strip() for t in re.split(r"[,\n]", raw) if t.strip()]
    return [t.strip() for t in value.split(",") if t.strip()]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Turkish scientific prose in QMD/Markdown/text files (sci-audit axis G).")
    parser.add_argument("path", type=Path, help="QMD/Markdown/text file to audit.")
    # draft is the plugin-facing name; quick is the legacy alias. Both map to
    # the light pass. certification runs the full pass incl. G6 abbreviations.
    parser.add_argument("--strictness", choices=["draft", "quick", "certification"], default="draft")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    parser.add_argument("--out", type=Path, help="Optional report output path.")
    parser.add_argument("--fail-on", choices=["error", "warning", "none"], default="error")
    parser.add_argument("--enable-zemberek", action="store_true", help="Run optional Zemberek morphology provider.")
    parser.add_argument("--enable-gecturk", action="store_true", help="Run optional self-host GECTurk provider.")
    parser.add_argument("--gecturk-url", help="Self-hosted GECTurk HTTP endpoint URL.")
    parser.add_argument("--enable-tdk", action="store_true", help="Run limited TDK dictionary lookups.")
    parser.add_argument("--tdk-url", default=DEFAULT_TDK_URL, help="TDK lookup endpoint.")
    parser.add_argument("--terms", help="Comma list or file path of terms for terminology providers / English-leak extension.")
    parser.add_argument("--abbreviations", help="Comma list or file path of project abbreviations to add to the whitelist.")
    parser.add_argument("--enable-grok", action="store_true", help="Legacy flag; the deterministic core never sends text. Use the style-judge subagent.")
    parser.add_argument("--enable-llm", action="store_true", help="Alias for --enable-grok (no text is sent from here).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.path.exists():
        print(f"File not found: {args.path}", file=sys.stderr)
        return 2

    strictness = "quick" if args.strictness in ("draft", "quick") else "certification"
    # Report label keeps the user-facing name (draft), internal pass is quick.
    report_strictness = args.strictness if args.strictness != "quick" else "draft"

    terms = _read_terms_arg(args.terms)
    extra_abbr = set(_read_terms_arg(args.abbreviations) or [])
    external_config = ExternalConfig(
        enable_zemberek=args.enable_zemberek,
        enable_gecturk=args.enable_gecturk,
        enable_tdk=args.enable_tdk,
        enable_grok=args.enable_grok or args.enable_llm,
        gecturk_url=args.gecturk_url,
        tdk_url=args.tdk_url,
        terms=terms,
    )
    report = audit_path(args.path, strictness, external_config, extra_abbr)
    report.strictness = report_strictness
    rendered = to_json(report) if args.format == "json" else render_markdown(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return exit_code(report, args.fail_on)


if __name__ == "__main__":
    raise SystemExit(main())
