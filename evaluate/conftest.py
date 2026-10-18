"""
evaluate/conftest.py · The scoreboard. You never edit this file.

WHAT IT DOES
    Every time you run pytest in Part 2 (steps 6-9), it writes one web page:

        evaluate/report.html

    Open it in your browser (double-click it, or Ctrl+click the link pytest prints at the end).
    It refreshes itself while the tests run: one row per test, green / red / skipped,
    and for AI-judge tests every metric's score, pass mark and the judge's reason.
    No account, no server, no internet: it's a plain file on your laptop.

HOW THE TESTS FEED IT
    - Pass / fail / skip and the failure message: automatic, for every test.
    - Judge scores: a test asks for the `scoreboard` fixture and calls scoreboard.add(metrics)
      after the judge has measured them (see step7_judge/test_judge.py).
"""

import html
import time
from datetime import datetime
from pathlib import Path

import pytest

REPORT = Path(__file__).resolve().parent / "report.html"
RESULTS = []  # one dict per finished test
STATE = {
    "started": None,
    "running": True,
    "total": 0,
}


# ---------------------------------------------------------------------------
# 1. Collect: what happened in each test
# ---------------------------------------------------------------------------
class Scoreboard:
    def __init__(self, item):
        self.item = item

    def add(self, metrics):
        """Put the judge's scores for this test on the scoreboard (call it after metric.measure())."""
        rows = []
        for metric in metrics:
            has_score = metric.score is not None
            rows.append(
                {
                    "name": getattr(metric, "__name__", type(metric).__name__),
                    "score": metric.score,
                    "threshold": metric.threshold,
                    "passed": bool(has_score and metric.is_successful()),
                    "reason": metric.reason or "",
                }
            )
        self.item.user_properties.append(("metrics", rows))


@pytest.fixture
def scoreboard(request):
    return Scoreboard(request.node)


def pytest_collection_modifyitems(items):
    STATE["total"] = len(items)


def pytest_sessionstart(session):
    STATE["started"] = time.time()
    RESULTS.clear()
    _write()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Runs after every test phase. Records one result row per finished test."""
    outcome = yield
    report = outcome.get_result()

    # A passing setup or teardown is not a result worth showing.
    if report.when == "setup" and report.outcome == "passed":
        return
    if report.when == "teardown" and report.outcome == "passed":
        return

    if report.when == "call" or report.outcome != "passed":
        message = ""
        if report.skipped and isinstance(report.longrepr, tuple):
            message = report.longrepr[2].replace("Skipped: ", "")
        elif report.failed and call.excinfo is not None:
            # Keep our own assert message, not pytest's re-run of the expression.
            message = str(call.excinfo.value).split("\nassert ")[0]

        # Judge scores added by the test through the scoreboard fixture (the last call wins).
        metrics = []

        for key, rows in item.user_properties:
            if key == "metrics":
                metrics.append(rows)

        latest_metrics = []
        if metrics:
            latest_metrics = metrics[-1]

        test_file = Path(str(item.fspath))
        RESULTS.append(
            {
                "file": test_file.parent.name + " / " + test_file.name,
                "name": item.name,
                "outcome": report.outcome,
                "message": message[:1500],
                "metrics": latest_metrics,
                "seconds": round(getattr(report, "duration", 0), 1),
            }
        )
        _write()


def pytest_sessionfinish(session):
    STATE["running"] = False
    _write()


def pytest_terminal_summary(terminalreporter):
    terminalreporter.write_sep("-", "scoreboard")
    terminalreporter.write_line(f"Open in your browser: {REPORT.as_uri()}")


# ---------------------------------------------------------------------------
# 2. Draw: one plain HTML page
# ---------------------------------------------------------------------------
CSS = """
/* Colours (light theme; the dark theme overrides them below) */
:root {
  --bg: #f7f8fb; --card: #fff; --ink: #141b4d; --muted: #5b6382; --line: #e3e6ef;
  --pass: #00968f; --fail: #e21147; --skip: #8a90a8; --bar: #eef0f6;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #10142e; --card: #181d3d; --ink: #eef0fb; --muted: #a9afcc; --line: #2a3060; --bar: #252b55; }
}

/* Page layout */
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.45 system-ui, -apple-system, Segoe UI, sans-serif;
}
main { max-width: 980px; margin: 0 auto; padding: 24px 16px 60px; }
h1 { font-size: 22px; margin: 0 0 4px; }
.sub { color: var(--muted); margin: 0 0 18px; }
h2 { font-size: 15px; margin: 22px 0 8px; color: var(--muted); font-weight: 600; }
footer { margin-top: 24px; color: var(--muted); font-size: 12px; }

/* The three tiles at the top: passed / failed / skipped */
.tiles { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
.tile { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 10px 14px; min-width: 110px; }
.tile b { display: block; font-size: 24px; }
.tile span { color: var(--muted); font-size: 13px; }

/* One row per test; the left border shows the result */
.row {
  background: var(--card); border: 1px solid var(--line); border-left: 5px solid var(--skip);
  border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
}
.row.passed { border-left-color: var(--pass); }
.row.failed { border-left-color: var(--fail); }
.head { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
.name { font-family: ui-monospace, Consolas, monospace; font-size: 13.5px; word-break: break-all; }
.chip { font-size: 12px; font-weight: 700; padding: 2px 9px; border-radius: 99px; color: #fff; background: var(--skip); white-space: nowrap; }
.passed .chip { background: var(--pass); }
.failed .chip { background: var(--fail); }
.msg { margin: 6px 0 0; color: var(--muted); font-size: 13px; white-space: pre-wrap; word-break: break-word; }

/* The judge's score bars; the dark mark on each bar is the pass mark */
.metric { display: grid; grid-template-columns: 150px 1fr 92px; gap: 10px; align-items: center; margin-top: 8px; font-size: 13px; }
.track { position: relative; height: 10px; background: var(--bar); border-radius: 99px; }
.fill { position: absolute; inset: 0 auto 0 0; border-radius: 99px; background: var(--pass); }
.fill.bad { background: var(--fail); }
.mark { position: absolute; top: -4px; bottom: -4px; width: 2px; background: var(--ink); opacity: .6; }
details { grid-column: 1 / -1; color: var(--muted); }
summary { cursor: pointer; }
.scores { margin-top: 6px; }
.scores > summary { font-size: 13px; }
"""


def _metric_html(metric):
    """One judge score: its name, a bar with the pass mark, the score, and the judge's reason."""
    score = metric["score"]

    if score is None:
        pct = 0
        label = "error"
    else:
        # Keep the score bar within its track, even for an out-of-range score.
        pct = score * 100
        pct = min(100, pct)
        pct = max(0, pct)
        label = f"{score:.2f} / {metric['threshold']}"

    if metric["passed"]:
        bar_class = "fill"
        reason_open = ""
    else:
        bar_class = "fill bad"
        reason_open = " open"  # Failed metrics show the reason right away.

    pass_mark = float(metric["threshold"]) * 100

    return (
        f'<div class="metric"><span>{html.escape(metric["name"])}</span>'
        f'<div class="track"><div class="{bar_class}" style="width:{pct:.0f}%"></div>'
        f'<div class="mark" style="left:{pass_mark:.0f}%" title="pass mark"></div></div>'
        f"<span>{label}</span>"
        f'<details{reason_open}><summary>judge\'s reason</summary>{html.escape(metric["reason"])}</details></div>'
    )


def _row_html(row):
    """One test row: name, result chip, failure message, and (for judge tests) the score bars."""
    message_html = ""
    if row["message"] and not row["metrics"]:
        message_html = f'<p class="msg">{html.escape(row["message"])}</p>'

    metric_blocks = []
    metric_scores = []

    for metric in row["metrics"]:
        metric_blocks.append(_metric_html(metric))

        score = metric["score"]
        if not score:
            score = 0
        metric_scores.append(score)

    metrics_html = "".join(metric_blocks)

    if metrics_html:
        # Judge scores: open for red tests, folded for green ones.
        worst = min(metric_scores)

        if row["outcome"] == "failed":
            open_attr = " open"
        else:
            open_attr = ""

        metrics_html = (
            f'<details class="scores"{open_attr}>'
            f'<summary>{len(row["metrics"])} judge scores · lowest {worst:.2f}</summary>{metrics_html}</details>'
        )

    return (
        f'<div class="row {row["outcome"]}"><div class="head">'
        f'<span class="name">{html.escape(row["name"])}</span>'
        f'<span class="chip">{row["outcome"]}</span></div>{message_html}{metrics_html}</div>'
    )


def _write():
    """Rebuild the whole report page from RESULTS and write it to disk."""
    counts = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
    }

    for result in RESULTS:
        outcome = result["outcome"]
        if outcome in counts:
            counts[outcome] += 1

    done = len(RESULTS)
    if STATE["running"]:
        refresh = '<meta http-equiv="refresh" content="2">'  # the page reloads itself while tests run
        status = f"running… {done} of {STATE['total']} tests done"
    else:
        refresh = ""
        status = f"finished · {done} tests"

    # Group the rows by test file.
    groups = {}
    for result in RESULTS:
        file = result["file"]

        if file not in groups:
            groups[file] = []

        groups[file].append(result)

    body = []
    for file, rows in groups.items():
        body.append(f"<h2>{html.escape(file)}</h2>")
        for row in rows:
            body.append(_row_html(row))
    if not RESULTS:
        body.append('<p class="sub">Waiting for the first test to finish…</p>')

    body_html = "".join(body)

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">{refresh}
<title>ShopKart Scoreboard</title><style>{CSS}</style></head><body><main>
<h1>ShopKart scoreboard</h1><p class="sub">{status} · updated {datetime.now():%H:%M:%S} · the line on each bar is the pass mark</p>
<div class="tiles"><div class="tile"><b>{counts['passed']}</b><span>passed</span></div>
<div class="tile"><b>{counts['failed']}</b><span>failed</span></div>
<div class="tile"><b>{counts['skipped']}</b><span>skipped (TODO)</span></div></div>
{body_html}
<footer>Written by evaluate/conftest.py every time you run pytest in Part 2. A plain file: nothing leaves your laptop.</footer>
</main></body></html>"""
    try:
        REPORT.write_text(page, encoding="utf-8")
    except OSError:
        pass  # the scoreboard is a bonus: never fail a test run because of it
