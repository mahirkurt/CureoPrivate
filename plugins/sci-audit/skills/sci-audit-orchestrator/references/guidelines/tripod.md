# TRIPOD — prediction-model studies (development / validation)

Check each item; report present / missing / partial with locating text. Full
statement: Collins GS et al. BMJ 2015;350:g7594 (TRIPOD); see also TRIPOD+AI 2024
for machine-learning models.

- **Title/Abstract** — identifies the study as developing and/or validating a
  prediction model, the target population, and the outcome.
- **Introduction** — rationale; objectives (development, validation, or both).
- **Methods** — source of data + study design; participants + eligibility, setting,
  dates; outcome definition + how/when assessed, blinded to predictors; predictors
  + how/when measured, blinded to outcome; sample size rationale; missing-data
  handling; how predictors were handled in analysis; model-building procedure
  (selection, internal validation); measures of model performance (discrimination
  e.g. C-statistic, calibration).
- **Results** — participant flow + characteristics; number of outcome events;
  full model (all coefficients + intercept, or a way to make predictions);
  performance with confidence intervals; validation results.
- **Discussion** — limitations; interpretation vs prior models; clinical use and
  implications.
- **Other** — supplementary material; funding.

Red flags for LLM text: a "validated model" with no external validation and no
calibration reported; a C-statistic with no CI; a model presented with no way to
reproduce a prediction (missing coefficients/intercept); training performance
reported as if it were validation.
