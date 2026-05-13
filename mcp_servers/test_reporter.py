"""
MCP server: test status reporter.

Reads allure-results/ JSON files and produces:
  - A colour-coded terminal summary (returned as tool output)
  - A standalone HTML file at <project-root>/test-status-report.html
  - An Allure result entry (JSON + attachments) written back into allure-results/
    so the summary appears inside the Allure HTML report on next generation

Status colour mapping
---------------------
passed  -> green  ✅
failed  -> red    ❌  (assertion failure)
broken  -> yellow ⚠️  (exception / setup error, not an assertion)
skipped -> yellow ⏭️
flaky   -> red    🔁  (same historyId has both passing and failing results)
unknown -> yellow ❓
"""

from __future__ import annotations

import json
import re
import textwrap
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("test-reporter")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_ALLURE_DIR = _PROJECT_ROOT / "allure-results"
_DEFAULT_HTML_OUT = _PROJECT_ROOT / "test-status-report.html"

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")

# --------------------------------------------------------------------------- #
# Colour / icon tables                                                          #
# --------------------------------------------------------------------------- #
_ANSI = {
    "green":  "\033[32m",
    "red":    "\033[31m",
    "yellow": "\033[33m",
    "reset":  "\033[0m",
    "bold":   "\033[1m",
}

_STATUS_COLOUR = {
    "passed":  "green",
    "failed":  "red",
    "broken":  "yellow",
    "skipped": "yellow",
    "flaky":   "red",
    "unknown": "yellow",
}

_STATUS_ICON = {
    "passed":  "✅",
    "failed":  "❌",
    "broken":  "⚠️ ",
    "skipped": "⏭️ ",
    "flaky":   "🔁",
    "unknown": "❓",
}

_HTML_BADGE = {
    "passed":  "#28a745",
    "failed":  "#dc3545",
    "broken":  "#ffc107",
    "skipped": "#ffc107",
    "flaky":   "#dc3545",
    "unknown": "#ffc107",
}

# Allure step status for each logical status
_ALLURE_STEP_STATUS = {
    "passed":  "passed",
    "skipped": "passed",
    "unknown": "passed",
    "broken":  "broken",
    "failed":  "failed",
    "flaky":   "failed",
}


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _overall_status(counts: dict[str, int]) -> str:
    if counts.get("failed", 0) or counts.get("flaky", 0):
        return "failed"
    if counts.get("broken", 0):
        return "broken"
    return "passed"


# --------------------------------------------------------------------------- #
# Result parsing                                                                #
# --------------------------------------------------------------------------- #

def _load_results(allure_dir: Path) -> list[dict]:
    results = []
    for path in allure_dir.glob("*-result.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            results.append(data)
        except (json.JSONDecodeError, OSError):
            pass
    return results


def _classify(results: list[dict]) -> list[dict]:
    """
    Group by historyId.  A test is 'flaky' when the same historyId has both a
    passing and a non-passing result in the same run (e.g. via retries).
    """
    by_history: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        hid = r.get("historyId") or r.get("uuid", "?")
        by_history[hid].append(r)

    classified = []
    for _hid, entries in by_history.items():
        statuses = {e.get("status", "unknown") for e in entries}
        canonical = max(entries, key=lambda e: e.get("stop", 0))

        if len(statuses) > 1 and "passed" in statuses:
            final_status = "flaky"
        else:
            final_status = canonical.get("status", "unknown")

        feature = next(
            (lb["value"] for lb in canonical.get("labels", []) if lb["name"] == "feature"),
            "",
        )
        suite = next(
            (lb["value"] for lb in canonical.get("labels", []) if lb["name"] == "suite"),
            "",
        )

        classified.append(
            {
                "name": canonical.get("name", "?"),
                "full_name": canonical.get("fullName", ""),
                "status": final_status,
                "feature": feature,
                "suite": suite,
                "duration_ms": canonical.get("stop", 0) - canonical.get("start", 0),
                "message": (canonical.get("statusDetails") or {}).get("message", ""),
            }
        )

    return sorted(classified, key=lambda r: (r["suite"], r["name"]))


# --------------------------------------------------------------------------- #
# Terminal report                                                               #
# --------------------------------------------------------------------------- #

def _terminal_report(classified: list[dict]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for r in classified:
        counts[r["status"]] += 1

    sep = "─" * 90
    lines: list[str] = [
        f"\n{_ANSI['bold']}TEST STATUS REPORT{_ANSI['reset']}  "
        f"({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})",
        sep,
        f"{'STATUS':<10}  {'TEST NAME':<55}  {'SUITE':<22}  {'MS':>6}",
        sep,
    ]

    for r in classified:
        colour = _ANSI[_STATUS_COLOUR.get(r["status"], "yellow")]
        icon = _STATUS_ICON.get(r["status"], "❓")
        label = f"{icon} {r['status'].upper():<8}"
        name = (r["name"][:53] + "..") if len(r["name"]) > 55 else r["name"]
        suite = (r["suite"][:20] + "..") if len(r["suite"]) > 22 else r["suite"]
        lines.append(
            f"{colour}{label}{_ANSI['reset']}  {name:<55}  {suite:<22}  {r['duration_ms']:>6}"
        )

    lines.append(sep)
    summary_parts = [
        f"{_ANSI[_STATUS_COLOUR.get(s, 'yellow')]}"
        f"{_STATUS_ICON.get(s, '❓')} {counts[s]} {s}"
        f"{_ANSI['reset']}"
        for s in ("passed", "failed", "broken", "skipped", "flaky", "unknown")
        if counts[s]
    ]
    lines.append("  ".join(summary_parts))
    lines.append(sep + "\n")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Standalone HTML report                                                        #
# --------------------------------------------------------------------------- #

def _html_report(classified: list[dict], out_path: Path) -> None:
    counts: dict[str, int] = defaultdict(int)
    for r in classified:
        counts[r["status"]] += 1

    def badge(status: str) -> str:
        colour = _HTML_BADGE.get(status, "#6c757d")
        icon = _STATUS_ICON.get(status, "❓")
        return (
            f'<span style="background:{colour};color:#fff;padding:2px 8px;'
            f'border-radius:4px;font-size:0.8em;font-weight:bold">'
            f'{icon} {status.upper()}</span>'
        )

    rows = [
        f"<tr>"
        f"<td style='padding:6px 10px'>{badge(r['status'])}</td>"
        f"<td style='padding:6px 10px'>{r['suite']}</td>"
        f"<td style='padding:6px 10px'>{r['name']}"
        + (f'<br><small style="color:#666">{r["message"][:120]}</small>' if r["message"] else "")
        + f"</td>"
        f"<td style='padding:6px 10px;text-align:right'>{r['duration_ms']} ms</td>"
        f"</tr>"
        for r in classified
    ]

    summary_badges = "  ".join(
        f'{badge(s)} <strong>{counts[s]}</strong>'
        for s in ("passed", "failed", "broken", "skipped", "flaky")
        if counts[s]
    )

    html = textwrap.dedent(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>Test Status Report</title>
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    margin: 32px; color: #333; }}
            h1 {{ font-size: 1.4em; margin-bottom: 4px; }}
            .ts {{ color: #888; font-size: 0.85em; margin-bottom: 20px; }}
            .summary {{ margin-bottom: 16px; }}
            table {{ border-collapse: collapse; width: 100%; font-size: 0.9em; }}
            th {{ background: #f4f4f4; text-align: left; padding: 8px 10px;
                  border-bottom: 2px solid #ddd; }}
            tr:nth-child(even) {{ background: #fafafa; }}
            tr:hover {{ background: #f0f4ff; }}
            td {{ border-bottom: 1px solid #eee; vertical-align: top; }}
          </style>
        </head>
        <body>
          <h1>Test Status Report</h1>
          <div class="ts">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div>
          <div class="summary">{summary_badges}</div>
          <table>
            <thead><tr>
              <th>Status</th><th>Suite</th><th>Test</th><th>Duration</th>
            </tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </body>
        </html>
    """).strip()

    out_path.write_text(html, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Allure result entry                                                           #
# --------------------------------------------------------------------------- #

def _write_allure_entry(
    classified: list[dict],
    terminal: str,
    html_path: Path,
    allure_dir: Path,
) -> None:
    """
    Write a summary Allure result entry so the status report appears as a
    distinct item inside the generated Allure HTML report.

    Written files (all inside allure_dir):
      <uuid>-txt-attachment.txt   — plain-text terminal report (ANSI stripped)
      <uuid>-html-attachment.html — full HTML report
      <uuid>-result.json          — Allure result referencing both attachments
    """
    counts: dict[str, int] = defaultdict(int)
    for r in classified:
        counts[r["status"]] += 1

    overall = _overall_status(counts)
    now_ms = int(time.time() * 1000)
    entry_uuid = str(uuid.uuid4())

    # Text attachment
    txt_source = f"{entry_uuid}-txt-attachment.txt"
    (allure_dir / txt_source).write_text(_strip_ansi(terminal), encoding="utf-8")

    # HTML attachment
    html_source = f"{entry_uuid}-html-attachment.html"
    html_content = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    (allure_dir / html_source).write_text(html_content, encoding="utf-8")

    # One step per non-zero status category
    steps = [
        {
            "name": f"{_STATUS_ICON.get(s, '❓')} {s.capitalize()}: {counts[s]}",
            "status": _ALLURE_STEP_STATUS.get(s, "passed"),
            "start": now_ms,
            "stop": now_ms,
        }
        for s in ("passed", "failed", "broken", "skipped", "flaky", "unknown")
        if counts[s]
    ]

    result = {
        "name": "Test Status Report",
        "status": overall,
        "steps": steps,
        "attachments": [
            {"name": "Terminal Report", "source": txt_source, "type": "text/plain"},
            {"name": "HTML Report",     "source": html_source, "type": "text/html"},
        ],
        "start": now_ms,
        "stop": now_ms + 1,
        "uuid": entry_uuid,
        "historyId": "mcp-test-reporter-summary",
        "testCaseId": "mcp-test-reporter-summary",
        "fullName": "mcp.test_reporter#report_test_status",
        "labels": [
            {"name": "feature",     "value": "Test Reporting"},
            {"name": "story",       "value": "MCP Status Report"},
            {"name": "severity",    "value": "normal"},
            {"name": "suite",       "value": "mcp_agent"},
            {"name": "parentSuite", "value": "mcp"},
            {"name": "subSuite",    "value": "test_reporter"},
        ],
    }

    (allure_dir / f"{entry_uuid}-result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# --------------------------------------------------------------------------- #
# MCP tool                                                                      #
# --------------------------------------------------------------------------- #

@mcp.tool()
def report_test_status(
    allure_dir: str = "",
    html_out: str = "",
    write_allure_entry: bool = True,
) -> str:
    """
    Read Allure result JSON files and return a colour-coded test status report.

    By default also:
      - Writes a standalone HTML file (test-status-report.html)
      - Writes an Allure result entry back into allure-results/ so the summary
        appears in the Allure HTML report on next `allure generate`

    Status classification:
      passed  -> green  ✅
      failed  -> red    ❌  (assertion failure)
      broken  -> yellow ⚠️  (exception / error, not assertion)
      skipped -> yellow ⏭️
      flaky   -> red    🔁  (mixed pass/fail results for the same test)

    Args:
        allure_dir:         Path to the allure-results directory.
                            Defaults to <project-root>/allure-results.
        html_out:           Path where the standalone HTML report is written.
                            Defaults to <project-root>/test-status-report.html.
        write_allure_entry: When True (default) a result JSON + attachments are
                            written into allure_dir so the report appears in
                            the generated Allure HTML.
    """
    resolved_dir = Path(allure_dir) if allure_dir else _DEFAULT_ALLURE_DIR
    resolved_html = Path(html_out) if html_out else _DEFAULT_HTML_OUT

    if not resolved_dir.exists():
        return (
            f"❌  allure-results directory not found: {resolved_dir}\n"
            "Run pytest with --alluredir first."
        )

    raw = _load_results(resolved_dir)
    if not raw:
        return f"No *-result.json files found in {resolved_dir}."

    classified = _classify(raw)
    terminal = _terminal_report(classified)
    _html_report(classified, resolved_html)

    if write_allure_entry:
        _write_allure_entry(classified, terminal, resolved_html, resolved_dir)
        allure_note = f"📊  Allure entry written to: {resolved_dir}\n"
    else:
        allure_note = ""

    return terminal + f"📄  HTML report written to: {resolved_html}\n" + allure_note


if __name__ == "__main__":
    mcp.run()
