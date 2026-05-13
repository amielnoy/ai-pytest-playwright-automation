"""
Session 14 — Building AI Tools for QA
Heal report: runs pytest, parses self-heal log lines, and builds a Markdown summary.

Usage:
    python heal_report.py --out reports/heal.md
"""

import subprocess
import typer
from collections import Counter

app = typer.Typer()


@app.command()
def heal_report(out: str = "heal-report.md"):
    """Run pytest, parse self-heal log lines, build a Markdown report."""
    proc = subprocess.run(["pytest", "--tb=no", "-q"], capture_output=True, text=True)

    heals = [line for line in proc.stdout.splitlines() if line.startswith("[self-heal]")]
    by_selector = Counter(line.split("→")[0].strip() for line in heals)

    md = ["# Self-Heal Report", "", f"Total heals: {len(heals)}", ""]
    md.append("| Original selector | Times healed |")
    md.append("|---|---|")
    for sel, n in by_selector.most_common():
        md.append(f"| `{sel}` | {n} |")

    with open(out, "w") as f:
        f.write("\n".join(md))

    typer.echo(f"Report written to {out}")


if __name__ == "__main__":
    app()
