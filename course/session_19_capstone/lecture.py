"""
Session 19 — Capstone: Production-Level Framework
Key concepts: architecture review, ADRs, quality gates, self-evaluation.
"""

# ── Framework layers (final state) ────────────────────────────────────────────
LAYERS = {
    "Tests":     "Describe WHAT — business behaviour, no Playwright calls inline.",
    "Pages":     "Describe HOW — one class per page, all selectors as class constants.",
    "Data":      "Typed factories (Faker) for realistic, isolated test inputs.",
    "Tools":     "AI-powered: CLI generator, self-healing, review command.",
    "Agents":    "Claude drives Playwright to explore and diff UI behaviour.",
    "Analysis":  "JUnit XML → Claude → PR comment; flaky detector → GitHub Issue.",
    "Reporting": "Allure 3: categories, environment, trend history, GitHub Pages.",
    "CI/CD":     "GitHub Actions: test → upload → report → pages → flaky cron.",
}

# ── Architecture Decision Records (ADRs) ──────────────────────────────────────
# ADR-001: Sync Playwright API (readability > async complexity for a course)
# ADR-002: Fluent POM returns next page object on navigation, self on same page
# ADR-003: Self-healing must log every heal — engineers MUST update selectors
# ADR-004: Allure for reporting — non-engineers can read results in browser
# ADR-005: Fresh browser context per test (request scope) for full isolation

ADR_TITLES = {
    "ADR-001": "Use synchronous Playwright API",
    "ADR-002": "Fluent Page Object Model with method chaining",
    "ADR-003": "Self-healing selectors must be logged, never silent",
    "ADR-004": "Allure 3 as the single reporting layer",
    "ADR-005": "Fresh browser context per test (request-scoped fixture)",
}

# ── Quality gates before shipping the framework ───────────────────────────────
QUALITY_GATES = [
    "ruff + ruff-format pass on all files (zero warnings)",
    "mypy --strict passes on all files",
    "pytest --collect-only -q shows no import errors",
    "All smoke tests green on 3 consecutive CI runs",
    "allure validate_decorators() returns no findings",
    "heal_tracker.summary() stays empty on stable selectors",
    "5+ ADRs committed in docs/adrs/",
]

# ── Self-evaluation rubric ────────────────────────────────────────────────────
RUBRIC = {
    "Code quality (30%)": {
        "excellent":   "ruff + mypy --strict pass; small focused modules; no dead code",
        "acceptable":  "Linting passes; some module bloat",
    },
    "Coverage (25%)": {
        "excellent":   "30+ tests across all layers; all green 5 runs in a row",
        "acceptable":  "20+ tests; occasional flakiness",
    },
    "AI integration (20%)": {
        "excellent":   "CLI used; self-heal logged + reviewed; at least 5 agent tests",
        "acceptable":  "CLI present but rarely used",
    },
    "CI/CD (15%)": {
        "excellent":   "smoke + regression split; Allure on Pages; flaky detector wired",
        "acceptable":  "Single CI job; no report",
    },
    "Docs (10%)": {
        "excellent":   "README + architecture + 5 ADRs",
        "acceptable":  "README only",
    },
}

if __name__ == "__main__":
    print("Framework layers:")
    for layer, desc in LAYERS.items():
        print(f"  {layer:<12} {desc}")
    print("\nADRs:")
    for adr, title in ADR_TITLES.items():
        print(f"  {adr}: {title}")
    print("\nQuality gates:")
    for gate in QUALITY_GATES:
        print(f"  [ ] {gate}")
