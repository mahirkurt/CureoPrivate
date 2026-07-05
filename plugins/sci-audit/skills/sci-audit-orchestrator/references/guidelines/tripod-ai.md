# TRIPOD+AI (2024) — prediction-model studies using ML

Extends TRIPOD; check the base TRIPOD items PLUS these ML-specific ones. Full
statement: Collins GS et al. BMJ 2024;385:e078378.

- **Title/Abstract** — identifies development and/or validation of a prediction
  model using machine learning; the target population and outcome.
- **Data** — data sources, participants, and the split into development/tuning/
  evaluation sets (and how the split was made); sample-size rationale for ML.
- **Predictors & outcome** — definitions, timing, blinding; how predictors were
  processed/engineered; class imbalance handling.
- **Model development** — the ML method(s), hyperparameter tuning procedure and
  search space, internal validation (cross-validation/bootstrap), and feature
  selection — all pre-specified vs data-driven.
- **Performance** — discrimination (e.g. AUC/C-statistic) AND calibration, each
  with uncertainty (CIs); on an independent/held-out set; fairness/subgroup
  performance.
- **Explainability & reproducibility** — model availability (code/weights or a
  way to make predictions); interpretability methods and their limits.
- **Discussion** — limitations, generalisability, intended clinical use.

Red flags for LLM text: AUC with no calibration; no held-out/external
evaluation; hyperparameters with no tuning description; a "validated" ML model
with no way to reproduce a prediction; training performance shown as validation.
