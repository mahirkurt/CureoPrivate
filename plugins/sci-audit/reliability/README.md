# reliability/ — CI-only evaluation & red-team layer

This directory is NOT part of the runtime plugin surface. It holds the optional
CI harnesses that regression-test the deterministic cores and the optional
providers. Nothing here runs in the claude.ai-web path.

## Contents

- `requirements-core.txt` — asserts the stdlib-only core (nothing to install).
- `requirements-optional.txt` — Zemberek / RAGAS / OTel / NLI pins for the
  optional layer (local venv or CI only).
- `evals/` — golden-set regression for the deterministic axes, plus the
  optional Grok/xAI reasoning gate (`GROK_API_KEY` required; sends no text
  without it).
- `redteam/` — adversarial prompts that try to make the plugin fabricate a
  citation, confirm a fake DOI, or pass an inconsistent statistic. The plugin
  must degrade to `manual_required`/`unverified`, never fabricate.

## Running the deterministic golden set

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/sci-audit/tests
```

## Optional Grok CI-eval judge (privacy contract)

The external Grok/xAI judge lives ONLY here, as an optional reasoning gate. It
is never invoked from the deterministic core. It sends text to xAI only when
`GROK_API_KEY` (or `XAI_API_KEY`) is present in the CI environment; with no key
it returns `unavailable` and sends nothing. This preserves the source repo's
privacy contract: the default, always-available path is fully local.
