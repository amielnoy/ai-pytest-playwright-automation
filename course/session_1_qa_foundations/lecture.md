# Session 1 — QA Foundations & Environment Setup

## What Is a Test Case?

A test case is a documented procedure to verify one specific behaviour.
Every test case contains six parts: **ID**, **title**, **priority**, **type**, **precondition**, **steps**, and **expected result**.
Steps must be atomic — one action per step. The expected result must be concrete and verifiable, not "it works".

Priorities: **High** (blocks release), **Medium** (degrades experience), **Low** (cosmetic or edge).
Types: Smoke, Functional, Negative, Edge Case, Security, Performance.

---

## The Test Pyramid

The test pyramid describes the ideal distribution of tests by layer:

- **Unit** — fast, cheap, many. Test logic in isolation, no browser or network.
- **Integration** — medium speed. Test how components talk to each other.
- **E2E / UI** — slow, expensive, few. Validate full user journeys through the real UI.

Invert the pyramid (more E2E than unit) and your suite becomes slow, fragile, and hard to maintain.

---

## Equivalence Partitioning & Boundary Analysis

Instead of testing every possible input, group inputs into **equivalence classes** that behave the same way.
Test one value from each class — valid and invalid.

**Boundary value analysis** adds tests at the edges of each class: minimum, maximum, just above, and just below.

Example — password length (8–72 chars):
Valid: `"password"` (8) and `"a" * 72`. Invalid: `""` (0), `"a" * 73` (73).

---

## Defect Lifecycle

New → Assigned → In Progress → Fixed → Verified → Closed (or Reopened).

A defect report needs: title, steps to reproduce, actual result, expected result, severity, and environment.
Severity ≠ Priority. A cosmetic bug on the CEO dashboard may be Low severity but High priority.

---

## Environment Setup Checklist

1. Python 3.12+ with a virtual environment.
2. `pip install -r requirements.txt` — installs pytest, Playwright, Allure, Faker.
3. `playwright install chromium` — downloads the browser binary.
4. Copy `data/secrets.json.example` → `data/secrets.json` and fill credentials.
5. Run `pytest --collect-only -q` to verify collection succeeds before the first full run.
