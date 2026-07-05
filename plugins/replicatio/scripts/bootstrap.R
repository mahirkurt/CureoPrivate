#!/usr/bin/env Rscript
## replicatio :: bootstrap.R
## Installs the audit toolchain (optionally under renv). Idempotent; honest about
## anything that fails to install (no fabrication of a "ready" state).
##
## Usage:
##   Rscript scripts/bootstrap.R                 # install into the active library
##   Rscript scripts/bootstrap.R --renv          # init/snapshot a project-local renv
##   Rscript scripts/bootstrap.R --repos <URL>   # override CRAN mirror

args <- commandArgs(trailingOnly = TRUE)
use_renv <- "--renv" %in% args
repos <- "https://cloud.r-project.org"
ri <- which(args == "--repos")
if (length(ri) && length(args) >= ri[1] + 1) repos <- args[ri[1] + 1]
options(repos = c(CRAN = repos), warn = 1)

## Package -> layer it powers (documentation only).
pkgs <- c(
  ## A — data contract
  "readr", "pointblank", "validate", "assertr", "skimr",
  ## B — method & assumption audit
  "performance", "see", "DHARMa", "parameters", "effectsize", "gtsummary",
  ## C — reporting consistency / metascience
  "statcheck", "scrutiny", "rsprite2",
  ## D — reproducibility & version pinning
  "renv", "targets", "testthat", "covr", "sessioninfo",
  ## F — independent re-implementation / robustness
  "waldo", "specr",
  ## R-MCP backends (P0/P1 live introspection)
  "mcptools", "btw",
  ## plumbing (findings JSON)
  "jsonlite"
)

install_missing <- function(p) {
  have <- rownames(installed.packages())
  todo <- setdiff(p, have)
  if (!length(todo)) {
    message("[replicatio] bootstrap: all ", length(p), " packages already present.")
    return(invisible())
  }
  message("[replicatio] bootstrap: installing ", length(todo), " package(s): ",
          paste(todo, collapse = ", "))
  install.packages(todo)
}

if (use_renv) {
  if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv")
  if (!file.exists("renv.lock")) {
    message("[replicatio] renv::init() — project-local library + lockfile")
    tryCatch(renv::init(bare = TRUE, restart = FALSE),
             error = function(e) message("[replicatio] renv::init skipped: ", conditionMessage(e)))
  }
  install_missing(pkgs)
  tryCatch(renv::snapshot(prompt = FALSE),
           error = function(e) message("[replicatio] renv::snapshot skipped: ", conditionMessage(e)))
} else {
  install_missing(pkgs)
}

## Honest post-check.
have <- rownames(installed.packages())
missing <- setdiff(pkgs, have)
if (length(missing)) {
  message("[replicatio] WARNING: still missing: ", paste(missing, collapse = ", "))
  if (any(c("mcptools", "btw") %in% missing)) {
    message("[replicatio] TODO: mcptools/btw may need GitHub: ",
            "Rscript -e \"pak::pak(c('posit-dev/mcptools','posit-dev/btw'))\"")
  }
  quit(save = "no", status = 0)  # graceful: never crash the host
}
message("[replicatio] bootstrap complete — toolchain ready.")
