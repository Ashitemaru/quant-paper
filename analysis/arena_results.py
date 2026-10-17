#!/usr/bin/env python3
"""Pull Quant-Arena E1 results and render the paper's tables and figures.

Two stages, so that only the first one needs database access:

  fetch   Run on lj-gpu1. Reads the Arena DB inside a read-only transaction
          and writes a sanitized snapshot (default analysis/data/v9_runs.json).
          The snapshot never contains episodes.sealed_score: sealed-window
          score components stay out of everything this script produces.
  render  Run anywhere with Python 3.8+. Reads the snapshot and writes
          Tables/generated/*.tex and Figures/generated/*.tex (pgfplots).

Typical use:
  ssh lj-gpu1 'python3.12 - fetch --out -' < analysis/arena_results.py > analysis/data/v9_runs.json
  python3 analysis/arena_results.py render
"""
import argparse
import datetime as dt
import json
import math
import os
import statistics
import subprocess
import sys

SUITE = "sandbox_2022_2023_research_2024_final_v9"
CONTAINER = "postgres-bfaygxvetwckqrfwi1xtwluq"
DATABASE = "quant_arena_bench"
REPLICATES_PER_CELL = 3

# Display order and names; refs are the registered v9 model_refs.
MODELS = [
    ("astra6_v3_total_budget_r3", r"GPT-6 Astra"),
    ("opus55_v3_total_budget_r3", r"Claude Opus 5.5"),
    ("gemini38_v3_total_budget_r3", r"Gemini 3.8 Flash"),
    ("deepseek41_v3_total_budget_r3", r"DeepSeek V4.1 Flash"),
    ("glm53_shuzirensheng_v1", r"GLM-5.3"),
    ("kimik3_shuzirensheng_v1", r"Kimi K3"),
]
MODES = [("one_shot", "One-shot"), ("vanilla_iterative", "Vanilla")]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SNAPSHOT = os.path.join(ROOT, "analysis", "data", "v9_runs.json")

# Only public fields are selected. sealed_score is deliberately absent.
QUERY = """
SELECT coalesce(json_agg(row_to_json(x) ORDER BY x.created_at), '[]'::json)
FROM (
  SELECT e.id AS episode_id, e.status AS episode_status,
         e.publication_status, e.created_at, e.started_at, e.finished_at,
         s.manifest->>'model_ref' AS model_ref,
         s.manifest->>'research_mode' AS research_mode,
         s.manifest->>'track' AS track,
         s.manifest->>'environment_ref' AS environment_ref,
         r.id AS replicate_id, r.status AS replicate_status, r.phase,
         r.error, r.usage_complete, r.agent_restarts,
         e.result->'model' AS model,
         e.result->'research_score' AS research_score,
         e.result->'final_score'->'score' AS final_score,
         e.result->'overall_score' AS total_score,
         e.result->'research_finance' AS research_finance,
         e.result->'finance' AS final_finance,
         e.result->'diversity' AS diversity,
         e.result->'efficiency' AS efficiency,
         e.result->'eligibility' AS eligibility
  FROM arena_episodes e
  JOIN arena_submissions s ON s.id = e.submission_id
  JOIN arena_replicates r ON r.episode_id = e.id
  WHERE e.suite_ref = '{suite}'
) x
"""


# ── fetch ────────────────────────────────────────────────────────────────────

def fetch(args):
    cmd = ["docker", "exec", "-e", "PGOPTIONS=-c default_transaction_read_only=on",
           CONTAINER, "psql", "-U", "postgres", "-d", DATABASE, "-X", "-A", "-t",
           "-v", "ON_ERROR_STOP=1", "-c", QUERY.format(suite=SUITE)]
    out = subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout.decode()
    runs = json.loads(out)
    snapshot = {
        "suite_ref": SUITE,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "runs": runs,
    }
    text = json.dumps(snapshot, indent=1, sort_keys=True)
    if args.out == "-":
        sys.stdout.write(text + "\n")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
        print("wrote %d runs to %s" % (len(runs), args.out), file=sys.stderr)


# ── helpers ──────────────────────────────────────────────────────────────────

PENDING = r"\ph{pending}"
NA = "--"


def metric(block, name):
    """Value of a metric from an episode finance block (aggregate or scalar)."""
    if not isinstance(block, dict):
        return None
    m = block.get(name)
    if isinstance(m, dict):
        for key in ("mean", "value"):
            if m.get(key) is not None:
                return m[key]
        return None
    return m


def num(x):
    return x if isinstance(x, (int, float)) and math.isfinite(x) else None


def fmt(x, digits=2, pct=False):
    x = num(x)
    if x is None:
        return NA
    if pct:
        return ("%." + str(digits) + "f") % (100 * x)
    return ("%." + str(digits) + "f") % x


def mean_sd(values, digits=2, pct=False):
    vals = [v for v in (num(v) for v in values) if v is not None]
    if not vals:
        return NA
    m = statistics.mean(vals)
    if len(vals) == 1:
        return fmt(m, digits, pct)
    sd = statistics.stdev(vals)
    return r"%s{\scriptsize$\pm$%s}" % (fmt(m, digits, pct), fmt(sd, digits, pct))


def tokens_k(x):
    x = num(x)
    return NA if x is None else "%.0f" % (x / 1000.0)


def esc(s):
    return str(s).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def run_state(run):
    """Collapse episode and replicate status into one reporting state."""
    st = run.get("episode_status")
    if st in ("completed", "failed", "cancelled"):
        return st
    return "blocked" if run.get("replicate_status") == "blocked" else "running"


def cells(snapshot):
    """Group runs by (model_ref, mode) in submission order."""
    out = {}
    for run in snapshot["runs"]:
        out.setdefault((run["model_ref"], run["research_mode"]), []).append(run)
    return out


def research_score(run, key):
    rs = run.get("research_score") or {}
    return rs.get(key)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


HEADER = "%% Generated by analysis/arena_results.py from %s (suite %s, fetched %s). Do not edit.\n"


# ── render ───────────────────────────────────────────────────────────────────

def render(args):
    with open(args.snapshot) as fh:
        snap = json.load(fh)
    head = HEADER % (os.path.relpath(args.snapshot, ROOT), snap["suite_ref"], snap["fetched_at"])
    by_cell = cells(snap)
    tdir = os.path.join(ROOT, "Tables", "generated")
    fdir = os.path.join(ROOT, "Figures", "generated")

    known = {ref for ref, _ in MODELS}
    unknown = sorted({k[0] for k in by_cell} - known)
    if unknown:
        print("warning: runs from unlisted models ignored: %s" % unknown, file=sys.stderr)

    # Status table ------------------------------------------------------------
    rows = []
    totals = dict(sub=0, done=0, scored=0, fail=0, live=0, todo=0)
    for ref, name in MODELS:
        for mode, mname in MODES:
            runs = by_cell.get((ref, mode), [])
            states = [run_state(r) for r in runs]
            done = states.count("completed")
            scored = sum(1 for r in runs if run_state(r) == "completed" and num(r.get("total_score")) is not None)
            fail = states.count("failed") + states.count("cancelled")
            live = states.count("running") + states.count("blocked")
            todo = max(0, REPLICATES_PER_CELL - done - live)
            for k, v in (("sub", len(runs)), ("done", done), ("scored", scored), ("fail", fail), ("live", live), ("todo", todo)):
                totals[k] += v
            rows.append("%s & %s & %d & %d & %d & %d & %d & %d \\\\" % (
                name, mname, len(runs), done, scored, fail, live, todo))
    rows.append(r"\midrule")
    rows.append(r"\multicolumn{2}{@{}l}{Total} & %(sub)d & %(done)d & %(scored)d & %(fail)d & %(live)d & %(todo)d \\" % totals)
    write(os.path.join(tdir, "TabE1Status.tex"), head + r"""\begin{table}[t]
    \centering
    \footnotesize
    \caption{E1 run registry at the data snapshot (%s). Each cell prescribes %d independent replicates. \emph{Submitted} counts every episode, including failures and replacements; \emph{Scored} counts completed runs with an available total score; \emph{Live} counts runs still in research or final evaluation; \emph{To run} counts replicates not yet started that are needed to complete the cell. Failed runs stay in the registry and in every denominator.}
    \label{tab:e1_status}
    \begin{tabular}{@{}llrrrrrr@{}}
        \toprule
        Model & Mode & Submitted & Completed & Scored & Failed & Live & To run \\
        \midrule
%s
        \bottomrule
    \end{tabular}
\end{table}
""" % (snap["fetched_at"][:16].replace("T", " ") + " UTC", REPLICATES_PER_CELL, "\n".join("        " + r for r in rows)))

    # Main results table -------------------------------------------------------
    rows = []
    for ref, name in MODELS:
        for mode, mname in MODES:
            runs = by_cell.get((ref, mode), [])
            done = [r for r in runs if run_state(r) == "completed"]
            n = "%d/%d" % (len(done), max(REPLICATES_PER_CELL, len(runs)))
            if not done:
                rows.append("%s & %s & %s & %s \\\\" % (name, mname, n, " & ".join([PENDING] + [NA] * 7)))
                continue
            fin = [r.get("final_finance") for r in done]
            rows.append("%s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s \\\\" % (
                name, mname, n,
                mean_sd([research_score(r, "score") for r in done], 1),
                mean_sd([r.get("final_score") for r in done], 1),
                mean_sd([r.get("total_score") for r in done], 1),
                mean_sd([metric(f, "arr") for f in fin], 1, pct=True),
                mean_sd([metric(f, "delta_arr") for f in fin], 1, pct=True),
                mean_sd([metric(f, "rank_ic") for f in fin], 3),
                mean_sd([metric(f, "sharpe") for f in fin], 2),
                mean_sd([(num((r.get("efficiency") or {}).get("tokens_charged")) or 0) / 1000.0
                         if num((r.get("efficiency") or {}).get("tokens_charged")) is not None else None
                         for r in done], 1),
            ))
    write(os.path.join(tdir, "TabE1Main.tex"), head + r"""\begin{table*}[t]
    \centering
    \footnotesize
    \caption{E1 main results on the 2024 sealed window. Entries are means over completed replicates with the sample standard deviation in small type; $n$ is completed over prescribed (or submitted, if larger) runs, and failed runs count in the denominator. $S_{\mathrm{in}}$ and $S_{\mathrm{out}}$ are window scores on a 0--100 scale and Total $=0.3S_{\mathrm{in}}+0.7S_{\mathrm{out}}$. ARR and $\Delta$ARR are Top75 research-cohort annualized returns, in percent. Tokens are provider-reported totals per run, in thousands. A dash in a completed cell means the value is unavailable for every completed run (Table~\ref{tab:e1_runs} lists reasons). \ph{pending} marks cells without a completed replicate at the snapshot.}
    \label{tab:e1_main}
    \setlength{\tabcolsep}{3.5pt}
    \begin{tabular}{@{}llcrrrrrrrr@{}}
        \toprule
        Model & Mode & $n$ & $S_{\mathrm{in}}$ & $S_{\mathrm{out}}$ & Total & ARR & $\Delta$ARR & RankIC & Sharpe & Tokens \\
        \midrule
%s
        \bottomrule
    \end{tabular}
\end{table*}
""" % "\n".join("        " + r for r in rows))

    # In-sample (public formula) decomposition ---------------------------------
    rows = []
    for ref, name in MODELS:
        for mode, mname in MODES:
            done = [r for r in by_cell.get((ref, mode), []) if run_state(r) == "completed"]
            if not done:
                rows.append("%s & %s & %s \\\\" % (name, mname, " & ".join([PENDING] + [NA] * 7)))
                continue
            fin = [r.get("research_finance") for r in done]
            rows.append("%s & %s & %s & %s & %s & %s & %s & %s & %s & %s \\\\" % (
                name, mname,
                mean_sd([research_score(r, "Q") for r in done], 3),
                mean_sd([research_score(r, "efficiency_component") for r in done], 3),
                mean_sd([research_score(r, "diversity_component") for r in done], 3),
                mean_sd([metric(f, "rank_ic") for f in fin], 3),
                mean_sd([metric(f, "sharpe") for f in fin], 2),
                mean_sd([metric(f, "long_short_sharpe") for f in fin], 2),
                mean_sd([metric(f, "selection_turnover") for f in fin], 2),
                mean_sd([(r.get("diversity") or {}).get("independent_cluster_count") for r in done], 1),
            ))
    write(os.path.join(tdir, "TabE1InSample.tex"), head + r"""\begin{table*}[t]
    \centering
    \footnotesize
    \caption{Research-window (2022--2023) score decomposition under the published formula of Section~\ref{sec:scoring}. $Q$, $E$, and $D$ are the window components; RankIC, long-only Sharpe ($\mathrm{SR}_L$), long--short Sharpe ($\mathrm{SR}_{LS}$), and turnover (TO) are the inputs to $Q$; $K$ is the number of qualified, used, and mutually independent feature clusters. Means with standard deviations over completed replicates.}
    \label{tab:e1_insample}
    \setlength{\tabcolsep}{3.5pt}
    \begin{tabular}{@{}llrrrrrrrr@{}}
        \toprule
        Model & Mode & $Q$ & $E$ & $D$ & RankIC & $\mathrm{SR}_L$ & $\mathrm{SR}_{LS}$ & TO & $K$ \\
        \midrule
%s
        \bottomrule
    \end{tabular}
\end{table*}
""" % "\n".join("        " + r for r in rows))

    # Per-run registry (appendix) ---------------------------------------------
    rows = []
    for ref, name in MODELS:
        for mode, mname in MODES:
            for i, r in enumerate(by_cell.get((ref, mode), []), 1):
                err = (r.get("error") or {}).get("code") if isinstance(r.get("error"), dict) else None
                if not err and run_state(r) == "completed" and num(r.get("total_score")) is None:
                    err = ",".join(research_score(r, "reason_codes") or []) or None
                eff = r.get("efficiency") or {}
                rows.append("%s & %s & %d & \\texttt{%s} & %s & %s & %s & %s & %s & %s & %s \\\\" % (
                    name, mname, i, esc(r["episode_id"][3:11]), esc(run_state(r)),
                    esc(err) if err else NA,
                    tokens_k(eff.get("tokens_charged")),
                    eff.get("evaluation_count", NA) if eff else NA,
                    fmt(research_score(r, "score"), 1),
                    fmt(r.get("final_score"), 1),
                    fmt(r.get("total_score"), 1),
                ))
    if not rows:
        rows.append(r"\multicolumn{11}{c}{\ph{no runs at snapshot}} \\")
    write(os.path.join(tdir, "TabE1Runs.tex"), head + r"""\begin{table*}[t]
    \centering
    \scriptsize
    \caption{Every E1 run at the data snapshot, in submission order within each cell, including failed and replacement runs. Run identifiers are episode-ID prefixes. Tokens are provider-reported, in thousands; Evals counts admitted research evaluations.}
    \label{tab:e1_runs}
    \setlength{\tabcolsep}{3pt}
    \begin{tabular}{@{}llrlllrrrrr@{}}
        \toprule
        Model & Mode & \# & Run & State & Error & Tok.\,(k) & Evals & $S_{\mathrm{in}}$ & $S_{\mathrm{out}}$ & Total \\
        \midrule
%s
        \bottomrule
    \end{tabular}
\end{table*}
""" % "\n".join("        " + r for r in rows))

    # Token vs. total score figure (pgfplots) --------------------------------
    pts = {m: [] for m, _ in MODES}
    for (ref, mode), runs in by_cell.items():
        for r in runs:
            t = num((r.get("efficiency") or {}).get("tokens_charged"))
            s = num(r.get("total_score"))
            if run_state(r) == "completed" and t is not None and s is not None and mode in pts:
                pts[mode].append((t / 1000.0, s))
    if any(pts.values()):
        plots = []
        for (mode, mname), mark in zip(MODES, ("*", "triangle*")):
            coords = " ".join("(%.1f,%.3f)" % p for p in pts[mode])
            plots.append(r"\addplot[only marks, mark=%s] coordinates {%s}; \addlegendentry{%s}" % (mark, coords, mname))
        body = r"""\begin{tikzpicture}
\begin{axis}[width=0.9\linewidth, height=5.2cm, xmin=0, xmax=500,
  xlabel={Provider-reported tokens per run (thousands)}, ylabel={Total score},
  legend pos=north east, legend style={font=\footnotesize}, tick label style={font=\footnotesize}]
%s
\end{axis}
\end{tikzpicture}""" % "\n".join(plots)
    else:
        body = r"\fbox{\parbox[c][4cm][c]{0.85\linewidth}{\centering\ph{Pending: no completed E1 run at the data snapshot.}}}"
    write(os.path.join(fdir, "FigTokenScore.tex"), head + body + "\n")

    # Macros for prose ---------------------------------------------------------
    write(os.path.join(tdir, "e1_macros.tex"), head + "\n".join([
        r"\newcommand{\EOneSnapshot}{%s}" % (snap["fetched_at"][:16].replace("T", " ") + " UTC"),
        r"\newcommand{\EOnePrescribed}{%d}" % (len(MODELS) * len(MODES) * REPLICATES_PER_CELL),
        r"\newcommand{\EOneSubmitted}{%d}" % totals["sub"],
        r"\newcommand{\EOneCompleted}{%d}" % totals["done"],
        r"\newcommand{\EOneScored}{%d}" % totals["scored"],
        r"\newcommand{\EOneFailed}{%d}" % totals["fail"],
        r"\newcommand{\EOneLive}{%d}" % totals["live"],
    ]) + "\n")
    print("rendered tables and figures from %d runs" % len(snap["runs"]), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="read-only DB pull (run on lj-gpu1)")
    f.add_argument("--out", default=DEFAULT_SNAPSHOT, help="snapshot path, or - for stdout")
    r = sub.add_parser("render", help="write LaTeX tables and figures")
    r.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    args = ap.parse_args()
    fetch(args) if args.cmd == "fetch" else render(args)


if __name__ == "__main__":
    main()
