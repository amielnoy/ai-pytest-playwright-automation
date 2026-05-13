"""
Session 4 — Playwright Basics + First Browser Tests
Key concepts: locator strategy, auto-wait, expect assertions, and pytest fixtures.
"""

# ── Locator priority (most → least preferred) ──────────────────────────────────
LOCATOR_PRIORITY = [
    "page.get_by_role('button', name='Login')   # accessible, stable",
    "page.get_by_label('Email address')         # form fields",
    "page.get_by_placeholder('Search…')         # inputs with hints",
    "page.get_by_text('Submit')                 # static text",
    "page.get_by_test_id('submit-btn')          # data-testid attribute",
    "page.locator('[data-test=\"error\"]')      # attribute fallback",
    "page.locator('.css-class')                 # last resort — fragile",
]

# ── Auto-wait: Playwright waits automatically — never use time.sleep() ─────────
# expect(locator).to_be_visible()    waits up to timeout (default 30 s)
# expect(locator).to_have_text(…)    waits for text to match
# expect(page).to_have_url(…)        waits for navigation to complete

# ── Assertion cheat-sheet ─────────────────────────────────────────────────────
ASSERTIONS = {
    "to_be_visible()":         "element is in DOM and visible",
    "to_be_hidden()":          "element is hidden or absent",
    "to_have_text('…')":       "exact or regex text match",
    "to_contain_text('…')":    "partial text match",
    "to_have_value('…')":      "input field value",
    "to_have_count(n)":        "locator matches exactly n elements",
    "not_to_be_visible()":     "negative — element gone or hidden",
}

# ── Fixture scopes ─────────────────────────────────────────────────────────────
FIXTURE_SCOPES = {
    "session":  "One browser for the whole run — fastest; no isolation",
    "module":   "New context per file — good for API tests",
    "function": "New page per test — default; full isolation",
}

# ── Parametrize pattern ────────────────────────────────────────────────────────
# @pytest.mark.parametrize("user,pwd,msg", [("", "x", "required"), …])
# def test_login_error(page, user, pwd, msg):
#     …  # one test function → N test cases

if __name__ == "__main__":
    print("Locator strategy (best → worst):")
    for i, loc in enumerate(LOCATOR_PRIORITY, 1):
        print(f"  {i}. {loc}")
