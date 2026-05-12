"""
Test Automation Framework — accumulated across sessions 1–9.

Layer added per session
────────────────────────────────────────────────────────────
Session 1  manual test cases, QA theory           (no code)
Session 2  AI prompt templates                    (no code)
Session 3  first automated tests (raw Playwright) (tests only)
Session 6  pages/   Page Object Model             ← framework starts
Session 10  tools/   AI-powered CLI + self-healing
Session 11  agents/  browser exploration agent
Session 12  analysis/ CI failure analysis + flaky detector
Session 19  architecture, ADRs, pre-commit         (config layer)
Session 13  reporting/ Allure 3 integration
"""

BASE_URL = "https://www.saucedemo.com"
STANDARD_USER = "standard_user"
STANDARD_PASS = "secret_sauce"
