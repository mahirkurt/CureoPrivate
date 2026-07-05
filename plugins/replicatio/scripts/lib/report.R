## replicatio :: lib/report.R
## IBM Carbon v11 + IBM Plex single-file HTML report generator.
## Reads every <findings_dir>/*.json (the canonical findings schema written by
## lib/severity.R::rep_write_findings) and renders one self-contained HTML file:
## summary table + per-layer sections + severity badges + provenance (tool) stamps.
## EMOJI-FREE by house convention; icons/SVG allowed.
##
## Dual mode:
##   - sourced for its functions (render_report) by other scripts; OR
##   - run directly:  Rscript scripts/lib/report.R [--out <findings_dir>] [--html <path>]

if (!exists("rep_findings_dir")) {
  .rep_self <- {
    a <- commandArgs(trailingOnly = FALSE)
    f <- grep("^--file=", a, value = TRUE)
    if (length(f)) dirname(normalizePath(sub("^--file=", "", f[[1]]), mustWork = FALSE)) else getwd()
  }
  source(file.path(.rep_self, "severity.R"))
}

.REP_PALETTE <- c(
  CRITICAL    = "#da1e28",  # Carbon red 60
  MAJOR       = "#ff832b",  # Carbon orange 40
  MINOR       = "#f1c21b",  # Carbon yellow 30
  OBSERVATION = "#6f6f6f"   # Carbon gray 60
)
.REP_TEXT_ON <- c(CRITICAL = "#ffffff", MAJOR = "#161616", MINOR = "#161616", OBSERVATION = "#ffffff")

.REP_LAYER_TITLES <- c(
  "00_session"            = "Oturum & Ortam (D)",
  "01_data_contract"      = "A — Veri Sozlesmesi (Data Contract)",
  "02_assumptions"        = "B — Yontem & Varsayim Denetimi",
  "03_numeric_consistency"= "C — Raporlama Tutarliligi (Metabilim)",
  "04_crossvalidate"      = "F — Bagimsiz Yeniden-Uygulama"
)

.rep_esc <- function(x) {
  x <- as.character(x)
  x[is.na(x)] <- ""
  x <- gsub("&", "&amp;", x, fixed = TRUE)
  x <- gsub("<", "&lt;", x, fixed = TRUE)
  x <- gsub(">", "&gt;", x, fixed = TRUE)
  x <- gsub('"', "&quot;", x, fixed = TRUE)
  x
}

.rep_badge <- function(sev) {
  sev <- toupper(sev)
  bg <- .REP_PALETTE[[sev]]; fg <- .REP_TEXT_ON[[sev]]
  if (is.null(bg)) { bg <- "#6f6f6f"; fg <- "#ffffff" }
  sprintf('<span class="badge" style="background:%s;color:%s">%s</span>', bg, fg, .rep_esc(sev))
}

.rep_fmt_cell <- function(x) {
  if (is.null(x) || (length(x) == 1L && is.na(x))) return("")
  if (length(x) > 1L) x <- paste(x, collapse = ", ")
  .rep_esc(x)
}

## Read all findings JSON files in a directory; returns a named list keyed by layer.
.rep_read_all <- function(dir) {
  files <- list.files(dir, pattern = "\\.json$", full.names = TRUE)
  if (!length(files)) return(list())
  out <- list()
  for (fp in files) {
    obj <- tryCatch(jsonlite::read_json(fp, simplifyVector = FALSE),
                    error = function(e) NULL)
    if (is.null(obj) || is.null(obj$layer)) next
    out[[obj$layer]] <- obj
  }
  out[order(names(out))]
}

render_report <- function(findings_dir = NULL, output = NULL, title = "Replicatio Denetim Raporu") {
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    stop("[replicatio] report: 'jsonlite' gerekli. Once scripts/bootstrap.R calistirin.")
  }
  dir <- rep_findings_dir(findings_dir)
  if (is.null(output) || !nzchar(output)) output <- file.path(dir, "replicatio-report.html")
  layers <- .rep_read_all(dir)

  ## ---- aggregate ----
  all_findings <- list()
  for (L in layers) all_findings <- c(all_findings, L$findings)
  totals <- rep_severity_counts(all_findings)
  generated <- format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")

  ## ---- head / css ----
  css <- sprintf('
    @import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap");
    :root { --bg:#f4f4f4; --surface:#ffffff; --text:#161616; --line:#e0e0e0; --muted:#6f6f6f; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text);
      font-family:"IBM Plex Sans","Segoe UI",system-ui,-apple-system,sans-serif; font-size:14px; line-height:1.5; }
    .wrap { max-width:1080px; margin:0 auto; padding:48px 24px 80px; }
    header.app { border-left:6px solid #0f62fe; padding:8px 0 8px 16px; margin-bottom:8px; }
    header.app h1 { font-size:28px; font-weight:600; margin:0; letter-spacing:-0.01em; }
    .meta { color:var(--muted); font-size:13px; margin:4px 0 28px 16px;
      font-family:"IBM Plex Mono",ui-monospace,monospace; }
    h2 { font-size:18px; font-weight:600; margin:40px 0 12px; padding-bottom:8px; border-bottom:1px solid var(--line); }
    table { width:100%%; border-collapse:collapse; background:var(--surface); margin:8px 0 20px; }
    th { text-align:left; font-weight:600; font-size:12px; letter-spacing:0.02em; text-transform:uppercase;
      color:var(--muted); padding:12px 14px; border-bottom:1px solid var(--line); background:#fafafa; }
    td { padding:12px 14px; border-bottom:1px solid var(--line); vertical-align:top; }
    tr:last-child td { border-bottom:none; }
    .badge { display:inline-block; padding:2px 10px; border-radius:2px; font-size:11px; font-weight:600;
      letter-spacing:0.04em; white-space:nowrap; }
    .tool { font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12px; color:var(--muted); }
    code,.mono { font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12.5px; }
    .summary td.n { font-family:"IBM Plex Mono",ui-monospace,monospace; font-weight:600; text-align:right; width:96px; }
    .swatch { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:8px; vertical-align:middle; }
    .empty { color:var(--muted); font-style:italic; padding:12px 0; }
    .clean { border-left:6px solid #24a148; background:#defbe6; padding:14px 16px; margin:16px 0; }
    footer { color:var(--muted); font-size:12px; margin-top:48px; padding-top:16px; border-top:1px solid var(--line);
      font-family:"IBM Plex Mono",ui-monospace,monospace; }')

  ## ---- summary table ----
  sum_rows <- paste(vapply(SEVERITY_LEVELS, function(s) sprintf(
    '<tr><td><span class="swatch" style="background:%s"></span>%s</td><td class="n">%d</td></tr>',
    .REP_PALETTE[[s]], s, totals[[s]]), character(1)), collapse = "\n")
  summary_tbl <- sprintf(
    '<table class="summary"><thead><tr><th>Siddet</th><th class="n">Adet</th></tr></thead><tbody>%s
     <tr><td><strong>Toplam</strong></td><td class="n"><strong>%d</strong></td></tr></tbody></table>',
    sum_rows, length(all_findings))

  ## ---- per-layer sections ----
  section_html <- function(layer_key, obj) {
    title <- .REP_LAYER_TITLES[[layer_key]]
    if (is.null(title)) title <- layer_key
    fnds <- obj$findings
    head <- sprintf("<h2>%s</h2>", .rep_esc(title))
    if (!length(fnds)) {
      return(paste0(head, '<div class="clean">Bu katmanda bulgu yok (denetim calisti, ihlal saptanmadi).</div>'))
    }
    ## sort by severity rank then check
    rank <- match(vapply(fnds, function(f) f$severity, character(1)), SEVERITY_LEVELS)
    fnds <- fnds[order(rank)]
    rows <- vapply(fnds, function(f) sprintf(
      '<tr><td>%s</td><td><code>%s</code></td><td>%s</td><td class="mono">%s</td><td class="mono">%s</td><td class="tool">%s</td></tr>',
      .rep_badge(f$severity), .rep_esc(f$check), .rep_esc(f$message),
      .rep_fmt_cell(f$value), .rep_fmt_cell(f$expected), .rep_fmt_cell(f$tool)),
      character(1))
    paste0(head,
      '<table><thead><tr><th>Siddet</th><th>Denetim</th><th>Mesaj</th><th>Deger</th><th>Beklenen</th><th>Kaynak</th></tr></thead><tbody>',
      paste(rows, collapse = "\n"), "</tbody></table>")
  }

  sections <- if (!length(layers)) {
    '<div class="empty">Hic bulgu dosyasi bulunamadi. Once bir denetim komutu calistirin (orn. /replicatio:audit-data).</div>'
  } else {
    paste(mapply(section_html, names(layers), layers, SIMPLIFY = TRUE), collapse = "\n")
  }

  html <- sprintf('<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title><style>%s</style></head>
<body><div class="wrap">
<header class="app"><h1>%s</h1></header>
<div class="meta">olusturulma: %s &nbsp;|&nbsp; kaynak dizin: %s &nbsp;|&nbsp; severity-graded &middot; provenance-stamped &middot; no-fabrication</div>
<h2>Ozet</h2>%s
%s
<footer>replicatio &mdash; R + CSV dogruluk &amp; yeniden-uretilebilirlik denetimi. Bulgular karar-destek niteligindedir; otomatik tetikleyici sinyaller (statcheck/GRIM/GRIMMER/SPRITE) nihai hakem degildir, dogrulama gerektirir.</footer>
</div></body></html>',
    .rep_esc(title), css, .rep_esc(title), .rep_esc(generated), .rep_esc(dir), summary_tbl, sections)

  writeLines(html, output)
  message(sprintf("[replicatio] report -> %s  (%d finding(s): %d CRITICAL / %d MAJOR / %d MINOR / %d OBSERVATION)",
                  output, length(all_findings), totals[["CRITICAL"]], totals[["MAJOR"]],
                  totals[["MINOR"]], totals[["OBSERVATION"]]))
  invisible(output)
}

## ---- standalone CLI (only when report.R itself is the invoked --file) ----
.rep_is_main <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  fa <- grep("^--file=", a, value = TRUE)
  length(fa) && identical(basename(sub("^--file=", "", fa[[1]])), "report.R")
}
if (.rep_is_main()) {
  a <- commandArgs(trailingOnly = TRUE)
  getopt <- function(flag) { i <- which(a == flag); if (length(i) && length(a) >= i[1] + 1) a[i[1] + 1] else NULL }
  render_report(findings_dir = getopt("--out"), output = getopt("--html"))
}
