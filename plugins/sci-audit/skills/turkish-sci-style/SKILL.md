---
name: turkish-sci-style
description: Use when auditing Turkish scientific text for writing quality and orthography (axis G) — auto-triggers when the text is Turkish or the user passes --lang tr. Trigger on "Türkçe imla denetimi", "bilimsel Türkçe kontrol", "ondalık virgül", "akademik dil denetimi", "check Turkish scientific writing", "APA-TR sayı biçimi". Runs the deterministic G1–G6 core (tr_sciaudit.py), optional TDK/Zemberek/GECTurk providers with safe degrade, and the style-judge subagent for register/fluency.
---

# Turkish Scientific Writing & Orthography (axis G)

Deterministic Turkish scientific-writing audit. The core runs everywhere
(claude.ai-web included) with zero network; providers degrade safely.

## Run it

```bash
# draft (light) or certification (full; adds G6 abbreviation consistency)
python3 "${CLAUDE_PLUGIN_ROOT}/skills/turkish-sci-style/scripts/tr_sciaudit.py" <file> \
  --strictness certification --format md --fail-on error

# project abbreviations & domain terms are parameters, never hardcoded:
python3 "${CLAUDE_PLUGIN_ROOT}/skills/turkish-sci-style/scripts/tr_sciaudit.py" <file> \
  --strictness certification --abbreviations project-abbr.txt --terms "terim1,terim2" \
  --enable-tdk

# optional local/CI providers:
python3 "${CLAUDE_PLUGIN_ROOT}/skills/turkish-sci-style/scripts/gecturk_endpoint.py" --port 8765 &
python3 "${CLAUDE_PLUGIN_ROOT}/skills/turkish-sci-style/scripts/tr_sciaudit.py" <file> \
  --enable-gecturk --gecturk-url http://127.0.0.1:8765/check --enable-zemberek
```

The CLI contract (`--strictness`, `--format`, `--out`, `--fail-on`,
`--enable-*`, `--terms`) is preserved for muscle memory and CI scripts.
`draft` is the plugin name for the light pass; `quick` is accepted as a legacy
alias.

## Layer mapping (G1–G7)

| Sub-axis | What it checks | Where |
|---|---|---|
| G1 formal orthography | encoding artefacts/mojibake, space-before-punctuation, repeated words, missing Turkish diacritics (ı/i, ş/s, ç/c signals) | deterministic core |
| G2 readability/style | sentence & paragraph length; **Ateşman** readability score | deterministic core |
| G3 academic register | first person, colloquialisms, English-term leakage | deterministic core |
| G4 causal/generalisation overreach | causal wording on non-causal designs ("kanıtlar", "neden olur") | deterministic core |
| G5 number format | **decimal comma** rule; APA-TR **p-value** form (`p<0,001` not `p<0.05`) | deterministic core (p-dot = error/blocker) |
| G6 abbreviation/term consistency | first-use expansion, whitelist, TDK validation | core (certification) + TDK provider |
| G7 morphology (optional) | Zemberek analysis | provider (pip pkg) |

## Provider-degrade matrix

| Provider | Available | Unavailable |
|---|---|---|
| Deterministic G1–G6 | always (no network) | n/a |
| TDK (`sozluk.gov.tr/gts`, direct HTTP) | term-validity findings | status `error`; core audit stands |
| GECTurk self-host | grammar findings (local/CI) | status `unavailable`; never assumed on web |
| Zemberek (`zemberek-python==0.2.3`, needs `setuptools<81`) | morphology sample | status `unavailable`; report not blocked |
| LLM judge | `style-judge` Claude subagent | deterministic G-axis stands alone |

The Grok/xAI adapter is NOT in the deterministic core — no text is sent from
`tr_sciaudit.py`. Register/fluency/terminology judging is the `style-judge`
subagent; a Grok judge exists only as an optional CI-eval layer under
`reliability/`.

## Key formulas & rules

- **Ateşman readability** = 198.825 − 40.175 × (syllables/word) − 2.610 ×
  (words/sentence). Higher = easier. Labels: ≥90 very-easy, ≥70 easy, ≥50
  medium, ≥30 hard, else very-hard.
- **APA-TR numbers.** Turkish scientific prose uses the decimal **comma**
  (3,14 not 3.14). p-values follow APA-TR: `p<0,001`, `p=0,03`. An English
  decimal-dot p-value in Turkish text is a **blocker** (error) — the Stop hook
  also catches this at end-of-turn (gate G5).

## Precedence

If the `style-judge` subagent disagrees with the deterministic core, the
**deterministic finding wins**. The judge adds register/fluency nuance; it never
overturns an orthography or number-format rule.

See `references/denetim-doktrini.md` for the full doctrine, security/privacy
contract, and the safe-fallback provider behaviour.
