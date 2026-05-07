# Session 8 — Capstone: Production-Level Framework

## Framework Architecture Layers

A production test framework has five distinct layers, each with a single responsibility:

| Layer | Responsibility |
|---|---|
| **Tests** | Describe business behaviour — no Playwright calls inline |
| **Pages** | Encapsulate UI structure; one class per page or major component |
| **API clients** | Typed wrappers around backend endpoints |
| **AI utilities** | Test-gen CLI, self-healing wrapper, exploration agent |
| **Fixtures & data** | pytest fixtures, faker factories, test data files |

Tests should read like acceptance criteria. Any Playwright or HTTP detail belongs in the layer below.

---

## Architecture Decision Records (ADRs)

An ADR is a short document that captures a design decision, its context, and its consequences.
ADRs prevent the same debate from happening twice and help new team members understand why things are the way they are.

Format: **Status** (Proposed / Accepted / Deprecated) | **Context** | **Decision** | **Consequences**.

Key ADRs for this framework:
- **ADR-001**: Use sync Playwright API for readability.
- **ADR-002**: POM with Fluent API to keep tests linear.
- **ADR-003**: Self-healing must log every heal — flakiness must surface.
- **ADR-004**: Use Allure for test reporting.
- **ADR-005**: Isolate each test with a fresh browser context.

---

## Pre-Commit Hooks

Pre-commit hooks run automatically before every `git commit` and block the commit if they fail.
This enforces code quality without relying on developers to remember to run linters manually.

`.pre-commit-config.yaml` for this project runs:
- `ruff` — linting (import order, unused variables, style).
- `ruff-format` — formatting (replaces Black).
- `mypy --strict` — static type checking.

Run `pre-commit install` once after cloning to activate the hooks.

---

## Capstone Checklist

Before submitting the capstone project, verify all of the following:

- `pages/`, `services/`, `flows/`, `tests/` directories all present.
- All page classes extend `BasePage`; no raw selectors in test files.
- `@allure.feature` + `@allure.story` on every test class and method.
- `conftest` hook attaches a screenshot to Allure on test failure.
- Unique emails via `{ts}` placeholder; no shared state between tests.
- GitHub Actions pipeline: test → allure-generate → upload-artifact → gh-pages.
- `flaky_detector.py` wired to CI; issue opened when success rate < 95%.
- At least 10 AI-generated tests reviewed and committed.
- `ruff` + `mypy --strict` passing on all files.
- At least 5 ADRs in `docs/adrs/`.
