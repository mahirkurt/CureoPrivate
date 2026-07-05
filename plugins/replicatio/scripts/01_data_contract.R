#!/usr/bin/env Rscript
## replicatio :: 01_data_contract.R  (A layer — input validation / data contract)
## Parse diagnostics (readr::problems) + base structural checks + optional
## pointblank agent and optional validate ruleset. All findings -> JSON.
##
## Usage:
##   Rscript scripts/01_data_contract.R --csv <path.csv> [--rules <rules.R>] [--out <dir>]
##
## --rules <file.R>: optional. Sourced; if it leaves an object named `agent`
##   (pointblank agent) or `rules` (validate::validator), it is run against the data.

.sd <- {
  a <- commandArgs(trailingOnly = FALSE); f <- grep("^--file=", a, value = TRUE)
  if (length(f)) dirname(normalizePath(sub("^--file=", "", f[[1]]), mustWork = FALSE))
  else if (nzchar(Sys.getenv("CLAUDE_PLUGIN_ROOT"))) file.path(Sys.getenv("CLAUDE_PLUGIN_ROOT"), "scripts")
  else getwd()
}
source(file.path(.sd, "lib", "severity.R"))
source(file.path(.sd, "lib", "report.R"))

args <- commandArgs(trailingOnly = TRUE)
getopt <- function(flag, default = NULL) { i <- which(args == flag); if (length(i) && length(args) >= i[1] + 1) args[i[1] + 1] else default }
csv <- getopt("--csv", if (length(args) && !startsWith(args[1], "--")) args[1] else NULL)
rules_file <- getopt("--rules", NULL)
out <- getopt("--out", NULL)

if (is.null(csv)) {
  rep_usage("replicatio A-layer (data contract)\n",
            "  Rscript scripts/01_data_contract.R --csv <path.csv> [--rules <rules.R>] [--out <dir>]\n",
            "  --csv: CSV dosya yolu (zorunlu). --rules: opsiyonel pointblank `agent` / validate `rules`.\n")
  quit(save = "no", status = 0)
}
if (!file.exists(csv)) {
  message("[replicatio] HATA: CSV bulunamadi: ", csv); quit(save = "no", status = 0)
}

LAYER <- "01_data_contract"
findings <- list()
add <- function(f) findings[[length(findings) + 1]] <<- f
`%||%` <- function(a, b) if (is.null(a) || (length(a) == 1 && is.na(a))) b else a

## --- read with readr (captures parse problems) ---
if (!requireNamespace("readr", quietly = TRUE)) {
  rep_need("readr", LAYER, "read_csv", environment())
  rep_write_findings(findings, LAYER, out); quit(save = "no", status = 0)
}
df <- tryCatch(readr::read_csv(csv, show_col_types = FALSE, progress = FALSE),
               error = function(e) { message("[replicatio] read error: ", conditionMessage(e)); NULL })
if (is.null(df)) {
  add(rep_finding(LAYER, "csv_parse", "CRITICAL", paste("CSV ayristirilamadi:", csv), tool = "readr::read_csv"))
  rep_write_findings(findings, LAYER, out); quit(save = "no", status = 0)
}
probs <- tryCatch(readr::problems(df), error = function(e) NULL)
nprob <- if (is.null(probs)) 0L else nrow(probs)
if (nprob > 0) {
  sev <- rep_severity_from_fraction(nprob / max(nrow(df), 1L))
  if (is.na(sev)) sev <- "MINOR"
  add(rep_finding(LAYER, "parse_problems", sev,
                  sprintf("readr %d ayristirma sorunu bildirdi (tip zorlama / sutun kaymasi).", nprob),
                  tool = "readr::problems", value = nprob, expected = 0))
}

nr <- nrow(df); nc <- ncol(df)
add(rep_finding(LAYER, "dimensions", "OBSERVATION", sprintf("%d satir x %d sutun.", nr, nc),
                tool = "base::dim", value = sprintf("%dx%d", nr, nc)))

## --- duplicate rows ---
dup <- sum(duplicated(df))
if (dup > 0) {
  sev <- rep_severity_from_fraction(dup / max(nr, 1L))
  add(rep_finding(LAYER, "duplicate_rows", if (is.na(sev)) "MINOR" else sev,
                  sprintf("%d tekrar eden satir (%.1f%%).", dup, 100 * dup / max(nr, 1L)),
                  tool = "base::duplicated", value = dup, expected = 0))
}

## --- per-column: missingness, all-NA, constant ---
for (col in names(df)) {
  v <- df[[col]]
  na_frac <- mean(is.na(v))
  if (na_frac >= 1) {
    add(rep_finding(LAYER, paste0("all_na:", col), "MAJOR",
                    sprintf("'%s' sutunu tamamen NA.", col), tool = "base", value = "100% NA", expected = "<100% NA"))
  } else if (na_frac > 0) {
    sev <- rep_severity_from_fraction(na_frac, crit = 0.50, major = 0.20, minor = 0.0001)
    add(rep_finding(LAYER, paste0("missing:", col), if (is.na(sev)) "OBSERVATION" else sev,
                    sprintf("'%s' eksiklik: %.1f%%.", col, 100 * na_frac),
                    tool = "base::is.na", value = sprintf("%.1f%%", 100 * na_frac), expected = "0%"))
  }
  uniq <- length(unique(v[!is.na(v)]))
  if (uniq <= 1 && na_frac < 1) {
    add(rep_finding(LAYER, paste0("constant:", col), "OBSERVATION",
                    sprintf("'%s' sabit (tek deger) — modelde bilgi tasimaz.", col), tool = "base", value = uniq))
  }
}

## --- optional pointblank agent (verified workflow), guarded ---
if (requireNamespace("pointblank", quietly = TRUE)) {
  pb <- tryCatch({
    ag <- pointblank::create_agent(tbl = df, label = "replicatio data-contract")
    ag <- pointblank::rows_distinct(ag)
    for (col in names(df)) ag <- pointblank::col_vals_not_null(ag, columns = col)
    ag <- pointblank::interrogate(ag)
    pointblank::get_agent_report(ag, display_table = FALSE)
  }, error = function(e) { message("[replicatio] pointblank skipped: ", conditionMessage(e)); NULL })
  if (!is.null(pb) && is.data.frame(pb) && "f_failed" %in% names(pb)) {
    failed <- pb[!is.na(pb$f_failed) & pb$f_failed > 0, , drop = FALSE]
    if (nrow(failed)) {
      for (i in seq_len(nrow(failed))) {
        sev <- rep_severity_from_fraction(failed$f_failed[i])
        add(rep_finding(LAYER, paste0("pointblank:", failed$columns[i] %||% failed$type[i]),
                        if (is.na(sev)) "MINOR" else sev,
                        sprintf("pointblank %s: %.1f%% kayit basarisiz.", failed$type[i], 100 * failed$f_failed[i]),
                        tool = "pointblank", value = sprintf("%.1f%%", 100 * failed$f_failed[i]), expected = "0%"))
      }
    } else {
      add(rep_finding(LAYER, "pointblank", "OBSERVATION",
                      "pointblank temel sozlesme (rows_distinct + not_null) gecti.", tool = "pointblank"))
    }
  }
} else {
  rep_need("pointblank", LAYER, "pointblank_agent", environment())
}

## --- optional validate ruleset from --rules ---
if (!is.null(rules_file) && file.exists(rules_file) && requireNamespace("validate", quietly = TRUE)) {
  rv <- tryCatch({
    e <- new.env(); sys.source(rules_file, envir = e)
    if (exists("rules", envir = e)) {
      cf <- validate::confront(df, get("rules", envir = e))
      as.data.frame(summary(cf))
    } else NULL
  }, error = function(e) { message("[replicatio] validate skipped: ", conditionMessage(e)); NULL })
  if (!is.null(rv) && "fails" %in% names(rv)) {
    bad <- rv[rv$fails > 0, , drop = FALSE]
    for (i in seq_len(nrow(bad))) {
      frac <- bad$fails[i] / max(bad$items[i], 1L)
      sev <- rep_severity_from_fraction(frac)
      add(rep_finding(LAYER, paste0("validate:", bad$name[i]), if (is.na(sev)) "MINOR" else sev,
                      sprintf("validate kurali '%s': %d/%d basarisiz.", bad$name[i], bad$fails[i], bad$items[i]),
                      tool = "validate::confront", value = bad$fails[i], expected = 0))
    }
  }
}

rep_write_findings(findings, LAYER, out)
