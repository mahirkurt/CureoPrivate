#!/usr/bin/env Rscript
## replicatio :: 00_session.R  (D layer — session & environment capture)
## Captures sessioninfo::session_info() and renv::status() so a run is anchored to
## an exact R + package state. Emits findings + a human-readable session-info.txt.
##
## Usage: Rscript scripts/00_session.R [--project <dir>] [--out <findings_dir>]

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
project <- getopt("--project", getwd())
out <- getopt("--out", NULL)

LAYER <- "00_session"
findings <- list()
add <- function(f) findings[[length(findings) + 1]] <<- f

## --- R + platform baseline (always an OBSERVATION anchor) ---
add(rep_finding(LAYER, "r_version", "OBSERVATION",
                sprintf("R %s on %s", getRversion(), R.version$platform),
                tool = "base::R.version", value = as.character(getRversion())))

## --- sessioninfo (preferred) or base fallback ---
if (requireNamespace("sessioninfo", quietly = TRUE)) {
  si <- tryCatch(sessioninfo::session_info(), error = function(e) NULL)
  if (!is.null(si)) {
    txt <- tryCatch(paste(utils::capture.output(print(si)), collapse = "\n"),
                    error = function(e) "")
    if (nzchar(txt)) {
      writeLines(txt, file.path(rep_findings_dir(out), "session-info.txt"))
      add(rep_finding(LAYER, "session_info", "OBSERVATION",
                      "Tam oturum/ortam yakalandi -> session-info.txt", tool = "sessioninfo::session_info"))
    }
  }
} else {
  rep_need("sessioninfo", LAYER, "session_info", environment())
}

## --- renv lockfile / sync status ---
if (requireNamespace("renv", quietly = TRUE)) {
  has_lock <- file.exists(file.path(project, "renv.lock"))
  if (!has_lock) {
    add(rep_finding(LAYER, "renv_lockfile", "MAJOR",
                    "Projede renv.lock yok: paket surumleri sabitlenmemis -> bagimsiz yeniden-uretim kirilgan.",
                    tool = "renv::status", expected = "renv.lock present"))
  } else {
    st <- tryCatch(utils::capture.output(renv::status(project = project)),
                   error = function(e) paste("renv::status error:", conditionMessage(e)))
    synced <- any(grepl("synchronized|up.to.date|consistent", st, ignore.case = TRUE)) &&
              !any(grepl("out of sync|not installed|recorded.*not installed|installed.*not recorded", st, ignore.case = TRUE))
    if (synced) {
      add(rep_finding(LAYER, "renv_sync", "OBSERVATION",
                      "renv kutuphanesi lockfile ile senkron.", tool = "renv::status"))
    } else {
      add(rep_finding(LAYER, "renv_sync", "MAJOR",
                      paste0("renv kutuphanesi lockfile ile senkron DEGIL: ",
                             paste(utils::head(st, 6), collapse = " | ")),
                      tool = "renv::status", expected = "library == lockfile"))
    }
  }
} else {
  rep_need("renv", LAYER, "renv_sync", environment())
}

## --- RNG discipline note (parallel-safe reproducibility) ---
add(rep_finding(LAYER, "rng_kind", "OBSERVATION",
                sprintf("Aktif RNGkind: %s. Paralel/tekrarli koda L'Ecuyer-CMRG + set.seed disiplini onerilir.",
                        paste(RNGkind(), collapse = "/")),
                tool = "base::RNGkind", value = paste(RNGkind(), collapse = "/")))

rep_write_findings(findings, LAYER, out)
