"""
generate_summary.py

Builds benchmark-summary.html for the ANZ Performance Testing Agents
benchmark, in the same visual format as the reference test-generation
benchmark report (stat cards, category breakdown with legend, per-case
detail table).

Usage:
    python generate_summary.py
    python generate_summary.py --results benchmark_results.json --config benchmark_config.json --out benchmark-summary.html
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pct(numerator, denominator):
    if not denominator:
        return 0.0
    return round(numerator / denominator * 100, 1)


def rate_class(value, good=80, warn=50, lower_is_better=False):
    """Return 'good' / 'warn' / 'bad' CSS class for a percentage value."""
    if lower_is_better:
        if value <= (100 - good):
            return "good"
        if value <= (100 - warn):
            return "warn"
        return "bad"
    if value >= good:
        return "good"
    if value >= warn:
        return "warn"
    return "bad"


def final_attempt(case):
    attempts = case.get("attempts", [])
    return attempts[-1] if attempts else {}


def checks_of(case):
    fa = final_attempt(case)
    return fa.get("evaluation", {}).get("checks", {}) or {}


def used_retry(case):
    return case.get("total_attempts", 0) > case.get("iterations_requested", 0)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def build_category_rows(cases):
    by_cat = {}
    for c in cases:
        by_cat.setdefault(c.get("category", "uncategorized"), []).append(c)

    rows = []
    for cat in sorted(by_cat):
        group = by_cat[cat]
        executed = [c for c in group if c.get("final_status") in ("PASS", "FAIL")]
        passed = [c for c in executed if c.get("final_status") == "PASS"]
        pass_at_k = [c for c in executed if c.get("pass_at_k")]
        retried = [c for c in executed if used_retry(c)]

        agent_ok = [c for c in executed if checks_of(c).get("agent") or checks_of(c).get("response_present")]
        tool_ok = [c for c in executed if checks_of(c).get("tool") or checks_of(c).get("missing_data_handled")]
        mock_ok = [c for c in executed if checks_of(c).get("mock_status", checks_of(c).get("no_hallucination", True))]

        scores = [c.get("final_score", 0) for c in executed]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        total_attempts = sum(c.get("total_attempts", 0) for c in group)

        rows.append({
            "category": cat,
            "cases": len(group),
            "attempts": total_attempts,
            "pass_rate": pct(len(passed), len(executed)),
            "pass_at_k": pct(len(pass_at_k), len(executed)),
            "retry_rate": pct(len(retried), len(executed)),
            "agent_match": pct(len(agent_ok), len(executed)),
            "tool_match": pct(len(tool_ok), len(executed)),
            "mock_compliance": pct(len(mock_ok), len(executed)),
            "avg_score": avg_score,
        })

    # "all" totals row
    executed = [c for c in cases if c.get("final_status") in ("PASS", "FAIL")]
    passed = [c for c in executed if c.get("final_status") == "PASS"]
    pass_at_k = [c for c in executed if c.get("pass_at_k")]
    retried = [c for c in executed if used_retry(c)]
    agent_ok = [c for c in executed if checks_of(c).get("agent") or checks_of(c).get("response_present")]
    tool_ok = [c for c in executed if checks_of(c).get("tool") or checks_of(c).get("missing_data_handled")]
    mock_ok = [c for c in executed if checks_of(c).get("mock_status", checks_of(c).get("no_hallucination", True))]
    scores = [c.get("final_score", 0) for c in executed]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    total_attempts = sum(c.get("total_attempts", 0) for c in cases)

    total_row = {
        "category": "all",
        "cases": len(cases),
        "attempts": total_attempts,
        "pass_rate": pct(len(passed), len(executed)),
        "pass_at_k": pct(len(pass_at_k), len(executed)),
        "retry_rate": pct(len(retried), len(executed)),
        "agent_match": pct(len(agent_ok), len(executed)),
        "tool_match": pct(len(tool_ok), len(executed)),
        "mock_compliance": pct(len(mock_ok), len(executed)),
        "avg_score": avg_score,
    }

    return rows, total_row


def html_escape(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

CSS = """
:root {
  color-scheme: light dark;
  --bg: #ffffff; --fg: #1a1a1a; --muted: #666666; --border: #e2e2e2;
  --card-bg: #f7f7f8; --good: #1a7f37; --warn: #9a6700; --bad: #cf222e;
  --total-bg: #f0f4ff;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121212; --fg: #eaeaea; --muted: #a0a0a0; --border: #333333;
    --card-bg: #1c1c1e; --total-bg: #1b2436;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  padding: 32px 40px 64px;
}
header h1 { margin: 0 0 4px; font-size: 22px; }
.meta { color: var(--muted); margin: 0 0 24px; font-size: 13px; }
.stats { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 36px; }
.card {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 16px; min-width: 130px;
}
.card-value { font-size: 20px; font-weight: 600; }
.card-label { font-size: 12px; color: var(--muted); margin-top: 2px; }
h2 { font-size: 16px; margin: 32px 0 8px; }
.note { color: var(--muted); font-size: 13px; margin: 0 0 12px; max-width: 780px; }
.legend {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px 32px; margin: 4px 0 20px; padding: 14px 18px; background: var(--card-bg);
  border: 1px solid var(--border); border-radius: 10px;
}
.legend-group h3 {
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em;
  color: var(--muted); margin: 0 0 8px;
}
.legend dl { margin: 0; display: grid; grid-template-columns: max-content 1fr; column-gap: 14px; row-gap: 7px; }
.legend dt { font-weight: 600; font-size: 12.5px; white-space: nowrap; }
.legend dd { margin: 0; font-size: 12.5px; color: var(--muted); }
.table-wrap { overflow-x: auto; max-width: 100%; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { border-bottom: 1px solid var(--border); padding: 8px 10px; text-align: left; white-space: nowrap; }
th {
  color: var(--muted); font-weight: 600; font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.02em;
}
td.num { text-align: right; font-variant-numeric: tabular-nums; }
tr.total-row { background: var(--total-bg); font-weight: 600; }
.good { color: var(--good); }
.warn { color: var(--warn); }
.bad { color: var(--bad); }
"""


def cell(value, cls=None, num=True):
    classes = "num" if num else ""
    if cls:
        classes = f"{classes} {cls}".strip()
    attr = f' class="{classes}"' if classes else ""
    return f"<td{attr}>{value}</td>"


def category_table_html(rows, total_row):
    thead = (
        "<tr><th>Category</th><th>Cases</th><th>Attempts</th>"
        "<th>Pass Rate</th><th>Pass@k</th><th>Retry Rate</th>"
        "<th>Agent Match</th><th>Tool Match</th><th>Mock Compliance</th>"
        "<th>Avg Score</th></tr>"
    )

    def row_html(r, is_total=False):
        tr_open = '<tr class="total-row">' if is_total else "<tr>"

        pass_rate_txt = f"{r['pass_rate']:.1f}%"
        pass_at_k_txt = f"{r['pass_at_k']:.1f}%"
        retry_rate_txt = f"{r['retry_rate']:.1f}%"
        agent_match_txt = f"{r['agent_match']:.1f}%"
        tool_match_txt = f"{r['tool_match']:.1f}%"
        mock_compliance_txt = f"{r['mock_compliance']:.1f}%"
        avg_score_txt = f"{r['avg_score']:.1f}"

        return (
            f"{tr_open}"
            f"<td>{html_escape(r['category'])}</td>"
            f"{cell(r['cases'])}"
            f"{cell(r['attempts'])}"
            f"{cell(pass_rate_txt, rate_class(r['pass_rate']))}"
            f"{cell(pass_at_k_txt, rate_class(r['pass_at_k']))}"
            f"{cell(retry_rate_txt, rate_class(r['retry_rate'], lower_is_better=True))}"
            f"{cell(agent_match_txt, rate_class(r['agent_match']))}"
            f"{cell(tool_match_txt, rate_class(r['tool_match']))}"
            f"{cell(mock_compliance_txt, rate_class(r['mock_compliance']))}"
            f"{cell(avg_score_txt, rate_class(r['avg_score']))}"
            f"</tr>"
        )

    body = "".join(row_html(r) for r in rows) + row_html(total_row, is_total=True)
    return f"<table><thead>{thead}</thead><tbody>{body}</tbody></table>"


def per_case_table_html(cases):
    thead = (
        "<tr><th>Case</th><th>Category</th><th>Scenario</th>"
        "<th>Attempts</th><th>Final Status</th><th>Pass@k</th><th>Final Score</th></tr>"
    )

    def status_class(status):
        return "good" if status == "PASS" else "bad"

    rows_html = []
    for c in cases:
        status = c.get("final_status", "NOT_RUN")
        score = c.get("final_score", 0)
        score_num = score if isinstance(score, (int, float)) else 0
        score_txt = f"{score_num:.1f}"
        pass_at_k_txt = "100%" if c.get("pass_at_k") else "0%"
        pass_at_k_cls = "good" if c.get("pass_at_k") else "bad"

        rows_html.append(
            "<tr>"
            f"<td>{html_escape(c.get('id',''))}</td>"
            f"<td>{html_escape(c.get('category',''))}</td>"
            f"<td>{html_escape(c.get('scenario',''))}</td>"
            f"{cell(c.get('total_attempts','-'))}"
            f"{cell(status, status_class(status), num=False)}"
            f"{cell(pass_at_k_txt, pass_at_k_cls)}"
            f"{cell(score_txt, rate_class(score_num))}"
            "</tr>"
        )
    return f"<table><thead>{thead}</thead><tbody>{''.join(rows_html)}</tbody></table>"


LEGEND_HTML = """
<div class="legend">
  <div class="legend-group">
    <h3>Category</h3>
    <dl>
      <dt>test_execution</dt><dd>Runs performance load tests via JMeter or k6 and returns execution metrics.</dd>
      <dt>monitoring</dt><dd>Collects and interprets performance telemetry such as CPU and latency.</dd>
      <dt>security</dt><dd>Runs configured security checks covering authentication and authorization.</dd>
      <dt>analysis</dt><dd>Analyzes current and historical metrics using RAG-grounded context.</dd>
      <dt>reporting</dt><dd>Generates technical or executive performance reports.</dd>
      <dt>orchestration</dt><dd>Root agent routes the query to the correct specialist sub-agent.</dd>
    </dl>
  </div>
  <div class="legend-group">
    <h3>Metric</h3>
    <dl>
      <dt>Pass rate</dt><dd>The proportion of executed cases whose final attempt was marked PASS by evaluator.py.</dd>
      <dt>Pass@k</dt><dd>The proportion of cases for which at least one of the k iterations (plus retries) passed.</dd>
      <dt>Retry rate</dt><dd>The proportion of cases that required retry attempts beyond the configured iterations.</dd>
      <dt>Agent match</dt><dd>The proportion of cases where the response indicated the correct agent handled the query.</dd>
      <dt>Tool match</dt><dd>The proportion of cases where the response indicated the correct tool was invoked.</dd>
      <dt>Mock compliance</dt><dd>The proportion of cases where the mock/hallucination check in evaluator.py passed.</dd>
      <dt>Avg score</dt><dd>The mean 0-100 evaluator score across executed cases in the group.</dd>
    </dl>
  </div>
</div>
"""


def render_html(summary, rows, total_row, cases, generated_at, config):
    cards = [
        (summary.get("cases", 0), "Cases"),
        (summary.get("total_attempts", 0), "Attempts"),
        (config.get("iterations", "-"), "Iterations / case (k)"),
        (f"{total_row['agent_match']:.1f}%", "Agent match rate"),
        (f"{summary.get('pass_rate', 0):.1f}%", "Pass rate"),
        (f"{total_row['retry_rate']:.1f}%", "Retry rate"),
        (f"{summary.get('pass_at_k', 0):.1f}%", "Pass@k"),
    ]
    cards_html = "".join(
        f'<div class="card"><div class="card-value">{v}</div><div class="card-label">{l}</div></div>'
        for v, l in cards
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>ANZ Performance Testing Benchmark Report</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>ANZ Performance Testing Agent &mdash; Benchmark Report</h1>
  <p class="meta">
    Generated {generated_at} &middot;
    agent stack Google ADK 2.7.1 / GPT-4.1 &middot;
    evaluator evaluator.py (rule-based)
  </p>
</header>

<section class="stats">
{cards_html}
</section>

<section>
  <h2>Category breakdown</h2>
  <p class="note">Grouped by each test case's own category. The <strong>all</strong> row aggregates every case.</p>
  {LEGEND_HTML}
  <div class="table-wrap">{category_table_html(rows, total_row)}</div>
</section>

<section>
  <h2>Per-case detail</h2>
  <div class="table-wrap">{per_case_table_html(cases)}</div>
</section>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate benchmark-summary.html")
    parser.add_argument("--results", default="benchmark_results.json")
    parser.add_argument("--config", default="benchmark_config.json")
    parser.add_argument("--out", default="benchmark-summary.html")
    args = parser.parse_args()

    results_path = ROOT / args.results
    config_path = ROOT / args.config
    out_path = ROOT / args.out

    data = json.loads(results_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}

    cases = data.get("cases", [])
    summary = data.get("summary", {})
    generated_at = data.get("generated_at", datetime.now(timezone.utc).isoformat())

    rows, total_row = build_category_rows(cases)
    html = render_html(summary, rows, total_row, cases, generated_at, config)

    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
