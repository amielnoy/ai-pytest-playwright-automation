# Session 5 — Building AI Tools for QA

## The Three Tools

This session builds three CLI tools that use the Claude API to automate QA work:

1. **`cli.py test`** — given a feature description, generates a complete pytest + Playwright file.
2. **`cli.py review`** — given an existing test file, audits it for anti-patterns and writes a Markdown report.
3. **`cli.py batch`** — reads a list of features from a text file and generates a test file for each line.

All three call `claude-sonnet-4-6` via `anthropic.Anthropic().messages.create()`.

---

## Test Generation Prompt Design

The generation prompt must specify:

- **Role**: "You are a senior test automation engineer."
- **Locator rule**: "Use `get_by_role`, `get_by_label`, `get_by_text` — no CSS or XPath."
- **Assertion rule**: "Use `expect()` for all assertions, never bare `assert` on DOM values."
- **Coverage minimum**: "Include 1 positive test, 1 negative test, 1 edge case."
- **Output format**: "Output ONLY Python code — no markdown fences, no explanations."

Without the output format constraint, Claude wraps code in ` ```python ``` ` blocks, which break `out.write_text(code)`.

---

## Self-Healing Selectors

`self_healing.py` wraps any locator with a fallback:

1. Try `page.locator(selector).wait_for(state="visible", timeout=2000)`.
2. On `PlaywrightTimeout` → send the page HTML and selector description to Claude.
3. Claude returns a new selector string to use for this test run.
4. Log every heal: `[self-heal] .old-class → [data-test="submit"]`.

**Golden rule**: heals are always logged and never silent. Engineers must update the Page Object — otherwise the suite accumulates AI guesses that silently drift from the real DOM.

---

## Heal Report

`heal_report.py` runs pytest, filters stdout for `[self-heal]` lines, counts each stale selector, and writes a Markdown table ranking selectors by how often they needed healing.

The report is uploaded as a CI artifact so the team can review which Page Objects need updating after a DOM change.

---

## Review Prompt: Anti-Patterns to Catch

The review tool asks Claude to scan for six issues:

1. Selectors written inline in tests instead of page objects.
2. `time.sleep()` calls instead of Playwright auto-wait.
3. Missing `expect()` — bare `assert` on DOM values.
4. Hardcoded credentials or URLs.
5. Tests that share mutable state across functions.
6. Missing teardown for browser contexts or API sessions.

Each finding must include file:line, severity (HIGH / MED / LOW), and a one-line fix suggestion.
