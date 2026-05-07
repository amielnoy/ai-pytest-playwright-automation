"""
Session 8 — Capstone Project: Production-Level Framework
Helper to generate .pre-commit-config.yaml for the capstone project.

Run:
    python pre_commit_setup.py
"""

PRE_COMMIT_CONFIG = """\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        args: [--strict, --ignore-missing-imports]
"""

ADR_TEMPLATE = """\
# {title}

## Status: {status}

## Context
{context}

## Decision
{decision}

## Consequences
{consequences}
"""

ADR_003 = ADR_TEMPLATE.format(
    title="ADR-003: Self-healing must log every heal",
    status="Accepted",
    context=(
        "Self-healing selectors mask DOM changes from the test suite. "
        "If we don't log, the team silently relies on AI guesses and never updates Page Objects."
    ),
    decision=(
        "Every heal writes a line `[self-heal] <old> → <new>` to stdout. "
        "The CI runs qa-gen heal-report after every regression run and uploads the markdown "
        "to GitHub artifacts. A weekly Issue is opened listing top-healed selectors."
    ),
    consequences=(
        "+ DOM drift becomes visible.\n"
        "+ Engineers update selectors instead of accumulating heals.\n"
        "- ~5% noise in logs; mitigated by --quiet flag for local runs."
    ),
)


def write_pre_commit_config(path: str = ".pre-commit-config.yaml") -> None:
    with open(path, "w") as f:
        f.write(PRE_COMMIT_CONFIG)
    print(f"Written: {path}")


def write_adr(adr_text: str, path: str = "docs/adrs/adr-003.md") -> None:
    import os

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(adr_text)
    print(f"Written: {path}")


if __name__ == "__main__":
    write_pre_commit_config()
    write_adr(ADR_003)
