#!/usr/bin/env Rscript
## replicatio :: 04_crossvalidate.R  (F layer — independent re-implementation)
## Compares a reported result against an independent re-computation with
## waldo::compare(); optional specr specification-curve robustness pass.
##
## Usage:
##   Rscript scripts/04_crossvalidate.R --a <fileA> --b <fileB> [--tol <num>] [--out <dir>]
##     --a/--b accept .rds (readRDS) OR .R (sourced; must leave a `result` object).
##   Optional robustness:
##   Rscript scripts/04_crossvalidate.R --specs <specs.R> [--out <dir>]
##     --specs: an .R file that leaves a `spec_setup` object (from specr::setup()).

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
fa <- getopt("--a", NULL); fb <- getopt("--b", NULL)
specs_file <- getopt("--specs", NULL)
tol <- suppressWarnings(as.numeric(getopt("--tol", "0")))
out <- getopt("--out", NULL)

if (is.null(fa) && is.null(specs_file)) {
  rep_usage("replicatio F-layer (cross-validate / independent re-implementation)\n",
            "  Rscript scripts/04_crossvalidate.R --a <fileA> --b <fileB> [--tol <num>] [--out <dir>]\n",
            "  Rscript scripts/04_crossvalidate.R --specs <specs.R> [--out <dir>]\n",
            "  --a/--b: .rds VEYA .R (kaynaklaninca `result` birakmali). --specs: specr::setup() ciktisi `spec_setup`.\n")
  quit(save = "no", status = 0)
}

LAYER <- "04_crossvalidate"
findings <- list()
add <- function(f) findings[[length(findings) + 1]] <<- f

## Load an object from .rds or .R-leaving-`result`.
load_obj <- function(path) {
  if (is.null(path) || !file.exists(path)) stop(sprintf("dosya yok: %s", path))
  ext <- tolower(tools::file_ext(path))
  if (ext == "rds") return(readRDS(path))
  e <- new.env(); sys.source(path, envir = e)
  if (!exists("result", envir = e)) stop(sprintf("'%s' bir `result` nesnesi birakmadi", path))
  get("result", envir = e)
}

## --- pairwise comparison ---
if (!is.null(fa) && !is.null(fb)) {
  if (!requireNamespace("waldo", quietly = TRUE)) {
    rep_need("waldo", LAYER, "compare", environment())
  } else {
    objs <- tryCatch(list(a = load_obj(fa), b = load_obj(fb)), error = function(e) e)
    if (inherits(objs, "error")) {
      add(rep_finding(LAYER, "load", "CRITICAL",
                      paste("Karsilastirma girdisi yuklenemedi:", conditionMessage(objs)),
                      tool = "base::readRDS/sys.source"))
    } else {
      diff <- tryCatch(waldo::compare(objs$a, objs$b, tolerance = if (is.na(tol) || tol <= 0) NULL else tol,
                                      x_arg = "reported", y_arg = "recomputed"),
                       error = function(e) e)
      if (inherits(diff, "error")) {
        add(rep_finding(LAYER, "compare", "OBSERVATION",
                        paste("waldo::compare hata:", conditionMessage(diff)), tool = "waldo::compare"))
      } else if (length(diff) == 0) {
        add(rep_finding(LAYER, "compare", "OBSERVATION",
                        "Rapor edilen ve bagimsiz yeniden-hesaplanan sonuc OZDES (tol dahilinde).",
                        tool = "waldo::compare", value = "identical", expected = "identical"))
      } else {
        txt <- paste(utils::head(as.character(diff), 12), collapse = " | ")
        add(rep_finding(LAYER, "compare", "MAJOR",
                        sprintf("Rapor edilen ve yeniden-hesaplanan sonuc FARKLI (%d fark blogu). Ozet: %s",
                                length(diff), substr(txt, 1, 400)),
                        tool = "waldo::compare", value = length(diff), expected = "identical"))
      }
    }
  }
}

## --- optional specr robustness ---
if (!is.null(specs_file)) {
  if (!file.exists(specs_file)) {
    add(rep_finding(LAYER, "specs_input", "OBSERVATION", paste("specs betigi yok:", specs_file), tool = "specr"))
  } else if (!requireNamespace("specr", quietly = TRUE)) {
    rep_need("specr", LAYER, "specr", environment())
  } else {
    res <- tryCatch({
      e <- new.env(); sys.source(specs_file, envir = e)
      if (!exists("spec_setup", envir = e)) stop("specs betigi `spec_setup` (specr::setup() ciktisi) birakmali")
      specr::specr(get("spec_setup", envir = e))
    }, error = function(e) e)
    if (inherits(res, "error")) {
      add(rep_finding(LAYER, "specr", "OBSERVATION",
                      paste("specr::specr calistirilamadi:", conditionMessage(res)), tool = "specr::specr"))
    } else {
      rdf <- tryCatch(as.data.frame(res), error = function(e) NULL)
      nspec <- if (!is.null(rdf)) nrow(rdf) else NA_integer_
      if (!is.null(rdf) && "estimate" %in% names(rdf)) {
        sign_split <- range(sign(rdf$estimate), na.rm = TRUE)
        flips <- sign_split[1] != sign_split[2]
        add(rep_finding(LAYER, "spec_curve", if (flips) "MAJOR" else "OBSERVATION",
                        sprintf("Spesifikasyon-egrisi: %d spesifikasyon%s.", nspec,
                                if (flips) " — tahmin ISARETI spesifikasyonlar arasi DEGISIYOR (sonuc kirilgan)" else " — tahmin isareti tutarli"),
                        tool = "specr::specr", value = nspec))
      } else {
        add(rep_finding(LAYER, "specr", "OBSERVATION",
                        sprintf("specr calisti (%s spesifikasyon); ozet cikartilamadi.", nspec), tool = "specr::specr"))
      }
    }
  }
}

rep_write_findings(findings, LAYER, out)
