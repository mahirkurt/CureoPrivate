#!/usr/bin/env Rscript
## replicatio :: 02_assumptions.R  (B layer — method & assumption audit)
## Sources a user model script, retrieves the fitted model object, and runs the
## easystats `performance` assumption suite (+ DHARMa for non-Gaussian GLM/GLMM).
## p-values map to severity; anything that cannot be extracted numerically is an
## honest OBSERVATION carrying the textual result (no fabricated verdicts).
##
## Usage:
##   Rscript scripts/02_assumptions.R --model <model.R> [--object model] [--out <dir>]
##
## The model script must assign the fitted model to a variable (default name:
## `model`). It is sourced in an isolated environment.

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
model_file <- getopt("--model", if (length(args) && !startsWith(args[1], "--")) args[1] else NULL)
obj_name <- getopt("--object", "model")
out <- getopt("--out", NULL)

if (is.null(model_file)) {
  rep_usage("replicatio B-layer (assumption audit)\n",
            "  Rscript scripts/02_assumptions.R --model <model.R> [--object model] [--out <dir>]\n",
            "  Model betigi fitli modeli `model` (veya --object) degiskenine atamali.\n")
  quit(save = "no", status = 0)
}
if (!file.exists(model_file)) { message("[replicatio] HATA: model betigi yok: ", model_file); quit(save = "no", status = 0) }

LAYER <- "02_assumptions"
findings <- list()
add <- function(f) findings[[length(findings) + 1]] <<- f

## --- source model script, fetch object ---
menv <- new.env()
ok <- tryCatch({ sys.source(model_file, envir = menv); TRUE },
               error = function(e) { message("[replicatio] model source error: ", conditionMessage(e)); FALSE })
if (!ok || !exists(obj_name, envir = menv)) {
  add(rep_finding(LAYER, "model_object", "CRITICAL",
                  sprintf("Model betigi '%s' nesnesini uretmedi (kaynaklama/atama hatasi).", obj_name),
                  tool = "base::sys.source", expected = obj_name))
  rep_write_findings(findings, LAYER, out); quit(save = "no", status = 0)
}
model <- get(obj_name, envir = menv)
add(rep_finding(LAYER, "model_class", "OBSERVATION",
                sprintf("Model sinifi: %s", paste(class(model), collapse = "/")),
                tool = "base::class", value = paste(class(model), collapse = "/")))

if (!requireNamespace("performance", quietly = TRUE)) {
  rep_need("performance", LAYER, "assumption_suite", environment())
  rep_write_findings(findings, LAYER, out); quit(save = "no", status = 0)
}

## Pull a numeric p-value out of a performance check_* result, defensively.
extract_p <- function(res) {
  p <- tryCatch(attr(res, "p"), error = function(e) NULL)
  if (is.numeric(p) && length(p) >= 1) return(as.numeric(p[1]))
  if (is.numeric(res) && length(res) == 1) return(as.numeric(res))
  NA_real_
}

## Run one check_* function; map to a finding.
run_check <- function(fn_name, check_id, label, severity_hint = NULL) {
  fn <- tryCatch(get(fn_name, envir = asNamespace("performance")), error = function(e) NULL)
  if (is.null(fn)) return(invisible())
  res <- tryCatch(suppressWarnings(fn(model)), error = function(e) e)
  if (inherits(res, "error")) {
    add(rep_finding(LAYER, check_id, "OBSERVATION",
                    sprintf("%s calistirilamadi (model tipi destekleMiyor olabilir): %s", label, conditionMessage(res)),
                    tool = paste0("performance::", fn_name)))
    return(invisible())
  }
  p <- extract_p(res)
  sev <- rep_severity_from_p(p)
  if (!is.na(p) && !is.na(sev)) {
    add(rep_finding(LAYER, check_id, sev,
                    sprintf("%s ihlali (p = %.4g).", label, p),
                    tool = paste0("performance::", fn_name), value = signif(p, 4), expected = "p >= 0.05"))
  } else if (!is.na(p)) {
    add(rep_finding(LAYER, check_id, "OBSERVATION",
                    sprintf("%s: ihlal saptanmadi (p = %.4g).", label, p),
                    tool = paste0("performance::", fn_name), value = signif(p, 4)))
  } else {
    txt <- tryCatch(paste(utils::capture.output(print(res)), collapse = " "), error = function(e) "")
    add(rep_finding(LAYER, check_id, "OBSERVATION",
                    sprintf("%s: sayisal p cikartilamadi; metin sonuc: %s", label, substr(txt, 1, 240)),
                    tool = paste0("performance::", fn_name)))
  }
}

run_check("check_normality",        "normality",        "Artik normalligi")
run_check("check_heteroscedasticity","heteroscedasticity","Sabit varyans (homoskedastisite)")
run_check("check_autocorrelation",  "autocorrelation",  "Artik bagimsizligi (otokorelasyon)")

## collinearity: VIF-based, not a p-value
vif <- tryCatch(suppressWarnings(performance::check_collinearity(model)), error = function(e) e)
if (!inherits(vif, "error")) {
  vdf <- tryCatch(as.data.frame(vif), error = function(e) NULL)
  if (!is.null(vdf) && "VIF" %in% names(vdf)) {
    mx <- suppressWarnings(max(vdf$VIF, na.rm = TRUE))
    sev <- if (is.finite(mx) && mx >= 10) "MAJOR" else if (is.finite(mx) && mx >= 5) "MINOR" else NA_character_
    if (!is.na(sev)) {
      add(rep_finding(LAYER, "collinearity", sev,
                      sprintf("Coklu baglanti: en yuksek VIF = %.2f.", mx),
                      tool = "performance::check_collinearity", value = round(mx, 2), expected = "VIF < 5"))
    } else {
      add(rep_finding(LAYER, "collinearity", "OBSERVATION",
                      sprintf("Coklu baglanti dusuk (max VIF = %.2f).", mx),
                      tool = "performance::check_collinearity", value = round(mx, 2)))
    }
  }
} else {
  add(rep_finding(LAYER, "collinearity", "OBSERVATION",
                  "check_collinearity calistirilamadi (tek terim / desteklenmeyen model).",
                  tool = "performance::check_collinearity"))
}

## outliers: count flagged
outl <- tryCatch(suppressWarnings(performance::check_outliers(model)), error = function(e) e)
if (!inherits(outl, "error")) {
  n_out <- tryCatch(sum(as.logical(outl), na.rm = TRUE), error = function(e) NA_integer_)
  if (!is.na(n_out) && n_out > 0) {
    add(rep_finding(LAYER, "outliers", "MINOR",
                    sprintf("%d etkili/aykiri gozlem isaretlendi.", n_out),
                    tool = "performance::check_outliers", value = n_out))
  } else if (!is.na(n_out)) {
    add(rep_finding(LAYER, "outliers", "OBSERVATION", "Aykiri gozlem isaretlenmedi.",
                    tool = "performance::check_outliers", value = 0))
  }
}

## non-Gaussian GLM/GLMM: overdispersion + DHARMa simulated residuals
fam <- tryCatch(stats::family(model)$family, error = function(e) NA_character_)
is_count_like <- !is.na(fam) && grepl("poisson|nbinom|binomial|Negative Binomial", fam, ignore.case = TRUE)
if (is_count_like) {
  od <- tryCatch(suppressWarnings(performance::check_overdispersion(model)), error = function(e) e)
  if (!inherits(od, "error")) {
    p <- extract_p(od); ratio <- tryCatch(attr(od, "ratio"), error = function(e) NA)
    sev <- rep_severity_from_p(p)
    if (!is.na(p) && !is.na(sev)) {
      add(rep_finding(LAYER, "overdispersion", sev,
                      sprintf("Asiri yayilim (p = %.4g%s).", p,
                              if (is.numeric(ratio)) sprintf(", oran = %.2f", ratio) else ""),
                      tool = "performance::check_overdispersion", value = if (is.numeric(ratio)) round(ratio, 2) else signif(p, 4),
                      expected = "ratio ~ 1"))
    }
  }
  if (requireNamespace("DHARMa", quietly = TRUE)) {
    sr <- tryCatch(performance::simulate_residuals(model), error = function(e) e)
    if (!inherits(sr, "error")) {
       td <- tryCatch(DHARMa::testResiduals(sr, plot = FALSE), error = function(e) NULL)
      pvals <- tryCatch(c(uniformity = td$uniformity$p.value, dispersion = td$dispersion$p.value,
                          outliers = td$outliers$p.value), error = function(e) NULL)
      if (!is.null(pvals)) {
        for (nm in names(pvals)) {
          sev <- rep_severity_from_p(pvals[[nm]])
          if (!is.na(sev)) add(rep_finding(LAYER, paste0("dharma_", nm), sev,
                              sprintf("DHARMa %s testi ihlali (p = %.4g).", nm, pvals[[nm]]),
                              tool = "DHARMa::testResiduals", value = signif(pvals[[nm]], 4), expected = "p >= 0.05"))
        }
      }
    }
  } else {
    rep_need("DHARMa", LAYER, "dharma_residuals", environment())
  }
}

## optional diagnostic plot (needs 'see')
if (requireNamespace("see", quietly = TRUE)) {
  png_path <- file.path(rep_findings_dir(out), "assumptions-check_model.png")
  ok_plot <- tryCatch({
    grDevices::png(png_path, width = 1400, height = 1000, res = 110)
    print(performance::check_model(model))
    grDevices::dev.off(); TRUE
  }, error = function(e) { try(grDevices::dev.off(), silent = TRUE); FALSE })
  if (ok_plot) add(rep_finding(LAYER, "check_model_plot", "OBSERVATION",
                               "Tani grafigi uretildi -> assumptions-check_model.png",
                               tool = "performance::check_model"))
}

rep_write_findings(findings, LAYER, out)
