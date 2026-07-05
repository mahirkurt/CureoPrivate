#!/usr/bin/env Rscript
## replicatio :: 03_numeric_consistency.R  (C layer — reporting consistency / metascience)
## statcheck (reported stat <-> p-value) + scrutiny GRIM/GRIMMER (integer mean/SD
## possibility) + rsprite2 SPRITE (plausible distributions). These are TRIGGER
## SIGNALS, not final arbiters — every run records that caveat.
##
## Usage (any subset):
##   Rscript scripts/03_numeric_consistency.R [--text <file.txt|.md|.pdf|.html>] \
##           [--stats <stats.csv with columns mean,sd,n[,min,max]>] [--out <dir>]

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
text_file <- getopt("--text", NULL)
stats_csv <- getopt("--stats", NULL)
out <- getopt("--out", NULL)

if (is.null(text_file) && is.null(stats_csv)) {
  rep_usage("replicatio C-layer (numeric / reporting consistency)\n",
            "  Rscript scripts/03_numeric_consistency.R [--text <file>] [--stats <stats.csv>] [--out <dir>]\n",
            "  --text: APA-stili istatistik metni (.txt/.md/.pdf/.html) -> statcheck.\n",
            "  --stats: sutunlari mean,sd,n[,min,max] olan CSV -> GRIM/GRIMMER/SPRITE.\n")
  quit(save = "no", status = 0)
}

LAYER <- "03_numeric_consistency"
findings <- list()
add <- function(f) findings[[length(findings) + 1]] <<- f

## mandatory methodological caveat
add(rep_finding(LAYER, "_caveat", "OBSERVATION",
                "statcheck/GRIM/GRIMMER/SPRITE TETIKLEYICI sinyallerdir, nihai hakem degildir. statcheck yalniz APA-stili rapor eder ve coklu-karsilastirma duzeltmesini TANIMAZ; isaretlenen her tutarsizlik elle dogrulanmalidir.",
                tool = "replicatio"))

## --- statcheck on text/PDF/HTML ---
if (!is.null(text_file)) {
  if (!file.exists(text_file)) {
    add(rep_finding(LAYER, "statcheck_input", "OBSERVATION", paste("Metin dosyasi yok:", text_file), tool = "statcheck"))
  } else if (!requireNamespace("statcheck", quietly = TRUE)) {
    rep_need("statcheck", LAYER, "statcheck", environment())
  } else {
    ext <- tolower(tools::file_ext(text_file))
    res <- tryCatch({
      if (ext == "pdf") statcheck::checkPDF(text_file)
      else if (ext %in% c("html", "htm")) statcheck::checkHTML(text_file)
      else statcheck::statcheck(paste(readLines(text_file, warn = FALSE), collapse = "\n"))
    }, error = function(e) e)
    if (inherits(res, "error")) {
      add(rep_finding(LAYER, "statcheck", "OBSERVATION",
                      paste("statcheck calistirilamadi:", conditionMessage(res)), tool = "statcheck"))
    } else if (is.null(res) || nrow(res) == 0) {
      add(rep_finding(LAYER, "statcheck", "OBSERVATION",
                      "statcheck APA-stili test istatistigi bulamadi (girdi APA formatinda olmayabilir).", tool = "statcheck::statcheck"))
    } else {
      n_tests <- nrow(res)
      n_err <- if ("error" %in% tolower(names(res))) sum(res[[which(tolower(names(res)) == "error")]], na.rm = TRUE) else NA_integer_
      n_dec <- if ("decisionerror" %in% tolower(names(res))) sum(res[[which(tolower(names(res)) == "decisionerror")]], na.rm = TRUE) else NA_integer_
      add(rep_finding(LAYER, "statcheck_scanned", "OBSERVATION",
                      sprintf("%d APA-stili test tarandi.", n_tests), tool = "statcheck", value = n_tests))
      if (!is.na(n_dec) && n_dec > 0)
        add(rep_finding(LAYER, "statcheck_decision_errors", "CRITICAL",
                        sprintf("%d KARAR hatasi: rapor edilen p, anlamlilik esigini test istatistigine gore yanlis tarafa dusuruyor.", n_dec),
                        tool = "statcheck", value = n_dec, expected = 0))
      if (!is.na(n_err) && n_err > 0)
        add(rep_finding(LAYER, "statcheck_inconsistencies", "MAJOR",
                        sprintf("%d tutarsizlik: rapor edilen p, test istatistigi+df'den yeniden-hesaplanan p ile uyusmuyor.", n_err),
                        tool = "statcheck", value = n_err, expected = 0))
      if ((is.na(n_err) || n_err == 0) && (is.na(n_dec) || n_dec == 0))
        add(rep_finding(LAYER, "statcheck_clean", "OBSERVATION",
                        "Taranan testlerde tutarsizlik saptanmadi.", tool = "statcheck"))
    }
  }
}

## --- scrutiny GRIM / GRIMMER + rsprite2 SPRITE on a stats table ---
if (!is.null(stats_csv)) {
  if (!file.exists(stats_csv)) {
    add(rep_finding(LAYER, "stats_input", "OBSERVATION", paste("Stats CSV yok:", stats_csv), tool = "scrutiny"))
  } else {
    sdf <- tryCatch(utils::read.csv(stats_csv, stringsAsFactors = FALSE, colClasses = "character"),
                    error = function(e) NULL)
    nm <- tolower(names(sdf))
    has <- function(x) x %in% nm
    col <- function(x) sdf[[which(nm == x)[1]]]
    if (is.null(sdf) || !has("mean") || !has("n")) {
      add(rep_finding(LAYER, "stats_columns", "OBSERVATION",
                      "Stats CSV en az 'mean' ve 'n' sutunlarini icermeli (GRIMMER/SPRITE icin 'sd', SPRITE icin 'min'+'max').",
                      tool = "scrutiny"))
    } else if (!requireNamespace("scrutiny", quietly = TRUE)) {
      rep_need("scrutiny", LAYER, "grim", environment())
    } else {
      ## GRIM: needs x (mean as string) + n
      grim_df <- data.frame(x = col("mean"), n = col("n"), stringsAsFactors = FALSE)
      gm <- tryCatch(scrutiny::grim_map(grim_df), error = function(e) e)
      if (!inherits(gm, "error") && "consistency" %in% names(gm)) {
        ninc <- sum(!gm$consistency, na.rm = TRUE)
        add(rep_finding(LAYER, "grim", if (ninc > 0) "MAJOR" else "OBSERVATION",
                        sprintf("GRIM: %d/%d rapor edilen ortalama, N ile matematiksel olarak MUMKUN DEGIL.", ninc, nrow(gm)),
                        tool = "scrutiny::grim_map", value = ninc, expected = 0))
      } else {
        add(rep_finding(LAYER, "grim", "OBSERVATION",
                        paste("grim_map calistirilamadi:", if (inherits(gm, "error")) conditionMessage(gm) else "beklenmeyen cikti"),
                        tool = "scrutiny::grim_map"))
      }
      ## GRIMMER: needs x, sd, n
      if (has("sd")) {
        grimmer_df <- data.frame(x = col("mean"), sd = col("sd"), n = col("n"), stringsAsFactors = FALSE)
        gr <- tryCatch(scrutiny::grimmer_map(grimmer_df), error = function(e) e)
        if (!inherits(gr, "error") && "consistency" %in% names(gr)) {
          ninc <- sum(!gr$consistency, na.rm = TRUE)
          add(rep_finding(LAYER, "grimmer", if (ninc > 0) "MAJOR" else "OBSERVATION",
                          sprintf("GRIMMER: %d/%d ortalama+SD cifti, N ile matematiksel olarak MUMKUN DEGIL.", ninc, nrow(gr)),
                          tool = "scrutiny::grimmer_map", value = ninc, expected = 0))
        }
      }
      ## SPRITE via rsprite2 (needs sd + min + max)
      if (has("sd") && has("min") && has("max")) {
        if (!requireNamespace("rsprite2", quietly = TRUE)) {
          rep_need("rsprite2", LAYER, "sprite", environment())
        } else {
          for (i in seq_len(nrow(sdf))) {
            res <- tryCatch({
              p <- rsprite2::set_parameters(
                mean = as.numeric(col("mean")[i]), sd = as.numeric(col("sd")[i]),
                n_obs = as.integer(col("n")[i]),
                min_val = as.numeric(col("min")[i]), max_val = as.numeric(col("max")[i]))
              rsprite2::find_possible_distributions(p, n_distributions = 1)
            }, error = function(e) e)
            if (inherits(res, "error")) {
              add(rep_finding(LAYER, paste0("sprite_row", i), "MAJOR",
                              sprintf("SPRITE satir %d: parametrelerle uyumlu HICBIR dagitim bulunamadi/gecersiz (%s).",
                                      i, conditionMessage(res)),
                              tool = "rsprite2::find_possible_distributions"))
            }
          }
          add(rep_finding(LAYER, "sprite", "OBSERVATION",
                          "SPRITE calistirildi (ozet); ihlaller sprite_row* olarak isaretlendi.",
                          tool = "rsprite2"))
        }
      }
    }
  }
}

rep_write_findings(findings, LAYER, out)
