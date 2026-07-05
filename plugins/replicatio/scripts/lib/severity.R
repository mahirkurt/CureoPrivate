## replicatio :: lib/severity.R
## Severity model + structured-findings I/O. Sourced by every audit script.
## Defines functions/constants only; sourcing has no side effects.
## House convention: CRITICAL > MAJOR > MINOR > OBSERVATION. No fabrication: a
## check that cannot run records an OBSERVATION explaining why, never a fake pass/fail.

suppressWarnings(suppressMessages({
  .REP_HAVE_JSONLITE <- requireNamespace("jsonlite", quietly = TRUE)
}))

SEVERITY_LEVELS <- c("CRITICAL", "MAJOR", "MINOR", "OBSERVATION")

## Directory the currently running R script lives in. Works both under a bare
## `Rscript path/to/x.R` call and inside the Claude Code plugin runtime (which
## exports CLAUDE_PLUGIN_ROOT to the subprocess).
rep_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg)) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg[[1]]), mustWork = FALSE)))
  }
  root <- Sys.getenv("CLAUDE_PLUGIN_ROOT", "")
  if (nzchar(root)) return(file.path(root, "scripts"))
  getwd()
}

## Where findings JSON is written. Precedence: explicit `out` arg ->
## $REPLICATIO_FINDINGS_DIR -> ./.replicatio/findings under the CURRENT working
## directory (the analysis project). Never the installed plugin cache.
rep_findings_dir <- function(out = NULL) {
  d <- out
  if (is.null(d) || !nzchar(d)) d <- Sys.getenv("REPLICATIO_FINDINGS_DIR", "")
  if (!nzchar(d)) d <- file.path(getwd(), ".replicatio", "findings")
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  normalizePath(d, mustWork = FALSE)
}

## One finding in the canonical schema:
##   {layer, check, severity, message, tool, value, expected}
rep_finding <- function(layer, check, severity, message,
                        tool = NA_character_, value = NA, expected = NA) {
  severity <- toupper(as.character(severity))
  if (length(severity) != 1L || is.na(severity) || !severity %in% SEVERITY_LEVELS) {
    severity <- "OBSERVATION"
  }
  list(
    layer    = as.character(layer),
    check    = as.character(check),
    severity = severity,
    message  = as.character(message),
    tool     = if (is.null(tool)) NA_character_ else as.character(tool),
    value    = if (is.null(value)) NA else value,
    expected = if (is.null(expected)) NA else expected
  )
}

## Map a hypothesis-test p-value (SMALL p = assumption VIOLATED) to a severity.
## Returns NA_character_ when the test indicates NO violation (caller skips it).
rep_severity_from_p <- function(p, crit = NA_real_, major = 0.001,
                                minor = 0.01, obs = 0.05) {
  p <- suppressWarnings(as.numeric(p))
  if (length(p) != 1L || is.na(p)) return(NA_character_)
  if (!is.na(crit) && p < crit) return("CRITICAL")
  if (p < major) return("MAJOR")
  if (p < minor) return("MINOR")
  if (p < obs)   return("OBSERVATION")
  NA_character_
}

## Map a failing fraction (0..1) of validation units to a severity.
## Returns NA_character_ when nothing failed.
rep_severity_from_fraction <- function(frac, crit = 0.20, major = 0.05,
                                       minor = 0.001) {
  frac <- suppressWarnings(as.numeric(frac))
  if (length(frac) != 1L || is.na(frac) || frac <= 0) return(NA_character_)
  if (frac >= crit)  return("CRITICAL")
  if (frac >= major) return("MAJOR")
  if (frac >= minor) return("MINOR")
  "OBSERVATION"
}

## Count findings by severity (named integer vector over all SEVERITY_LEVELS).
rep_severity_counts <- function(findings) {
  sev <- vapply(findings, function(f) f$severity, character(1))
  counts <- table(factor(sev, levels = SEVERITY_LEVELS))
  stats::setNames(as.integer(counts), SEVERITY_LEVELS)
}

## Write a list of findings to <dir>/<layer>.json with a run stamp.
rep_write_findings <- function(findings, layer, out = NULL) {
  dir <- rep_findings_dir(out)
  path <- file.path(dir, paste0(layer, ".json"))
  payload <- list(
    layer        = layer,
    generated_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
    n_findings   = length(findings),
    counts       = as.list(rep_severity_counts(findings)),
    findings     = findings
  )
  if (.REP_HAVE_JSONLITE) {
    jsonlite::write_json(payload, path, auto_unbox = TRUE, pretty = TRUE,
                         null = "null", na = "null", digits = NA)
  } else {
    writeLines(sprintf(
      '{"layer":"%s","n_findings":%d,"error":"install jsonlite to serialize findings"}',
      layer, length(findings)), path)
  }
  message(sprintf("[replicatio] %-18s %d finding(s) -> %s",
                  paste0(layer, ":"), length(findings), path))
  invisible(path)
}

## Print a usage banner (callers decide whether to quit afterwards).
rep_usage <- function(...) {
  msg <- paste0(..., collapse = "")
  message(msg)
  invisible(NULL)
}

## requireNamespace with a single honest OBSERVATION finding if absent.
rep_need <- function(pkg, layer, check, findings_env) {
  if (requireNamespace(pkg, quietly = TRUE)) return(TRUE)
  f <- rep_finding(layer, check, "OBSERVATION",
                   sprintf("'%s' paketi kurulu degil; bu denetim atlandi. Once scripts/bootstrap.R calistirin.", pkg),
                   tool = pkg)
  assign("findings", c(get("findings", envir = findings_env), list(f)), envir = findings_env)
  FALSE
}
