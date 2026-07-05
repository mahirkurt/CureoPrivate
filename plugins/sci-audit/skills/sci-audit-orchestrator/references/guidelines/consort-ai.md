# CONSORT-AI (2020) — RCTs of AI/ML interventions

An extension to CONSORT 2010; check the base CONSORT items PLUS these AI-specific
items. Full statement: Liu X, Cruz Rivera S et al. Nat Med 2020;26:1364.

- **Intervention (AI) description** — state the AI intervention and its
  intended role in the care pathway; the intended user (clinician, patient,
  autonomous); the setting of integration.
- **Inputs & outputs** — the input data required by the AI (and how acquired/
  selected), and how the AI's output is presented and acted upon.
- **Model identification** — the version of the AI algorithm evaluated; how/when
  it was updated (if at all) during the trial.
- **Human–AI interaction** — the degree of human oversight; how AI outputs were
  used in decisions; handling of cases where humans and AI disagreed.
- **Error analysis** — analysis of performance errors, failure modes, and the
  approach to identifying/handling poor-quality or unavailable input data.
- **Continuous learning** — whether the algorithm changed during the study.

Red flags for LLM text: an "AI-driven RCT" with no algorithm version; no
input/output specification; no human-oversight description; no error/failure
analysis; performance reported with no external/prospective validation.
