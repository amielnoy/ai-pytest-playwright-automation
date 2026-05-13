"""
Session 14 — Building AI Tools for QA
CLI that takes a feature description and generates a ready-to-run pytest file.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-xxx
    python cli.py test --feature "user can reset password via email link" --out tests/test_reset.py
"""

import os
import typer
import anthropic
from pathlib import Path

app = typer.Typer()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def _text(msg) -> str:  # type: ignore[return]
    """Extract text from the first text block in a Claude response."""
    return next((b.text for b in msg.content if hasattr(b, "text")), "")

PROMPT_TEMPLATE = """You are a senior test automation engineer.
Generate a complete pytest + Playwright (sync API) test file for this feature.

REQUIREMENTS:
- Use modern locators: get_by_role, get_by_label, get_by_text
- Use expect() for assertions, never bare assert on DOM
- Include 1 positive test, 1 negative test, 1 edge case
- Output ONLY Python code, no markdown fences, no explanations

FEATURE:
{feature}

BASE URL:
{base_url}
"""


REVIEW_PROMPT = """You are a senior QA engineer reviewing a pytest + Playwright test file.

Check for these issues and report each one with file:line, severity (HIGH/MED/LOW), and a one-line fix:
1. Selectors written inline in tests instead of page objects
2. time.sleep() calls instead of Playwright auto-wait
3. Missing expect() — bare assert on DOM values
4. Hardcoded credentials or URLs
5. Tests that share mutable state across functions
6. Missing teardown for resources (browser contexts, API sessions)

FILE CONTENT:
{code}
"""


@app.command()
def test(
    feature: str = typer.Option(..., help="Feature description"),
    base_url: str = typer.Option("https://www.saucedemo.com"),
    out: Path = typer.Option("tests/test_generated.py"),
):
    """Generate a pytest + Playwright test file from a feature description."""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(feature=feature, base_url=base_url),
            }
        ],
    )
    code = _text(msg).strip()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(code)
    typer.echo(f"Test written to {out}")


@app.command()
def review(
    file: Path = typer.Argument(..., help="Path to a pytest file to review"),
    out: Path = typer.Option(Path("review_report.md"), help="Where to write the Markdown report"),
):
    """Review an existing test file for common QA automation anti-patterns."""
    if not file.exists():
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(1)
    code = file.read_text()
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": REVIEW_PROMPT.format(code=code)}],
    )
    report = f"# Review: {file}\n\n{_text(msg).strip()}\n"
    out.write_text(report)
    typer.echo(f"Review written to {out}")


@app.command()
def batch(
    features_file: Path = typer.Argument(..., help="Text file with one feature per line"),
    base_url: str = typer.Option("https://www.saucedemo.com"),
    out_dir: Path = typer.Option(Path("tests/generated")),
):
    """Generate test files for every feature listed in a text file."""
    features = [line.strip() for line in features_file.read_text().splitlines() if line.strip()]
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, feature in enumerate(features, 1):
        slug = feature[:40].lower().replace(" ", "_").replace("/", "_")
        out = out_dir / f"test_{slug}.py"
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(feature=feature, base_url=base_url)}],
        )
        out.write_text(_text(msg).strip())
        typer.echo(f"[{i}/{len(features)}] {out}")


if __name__ == "__main__":
    app()
