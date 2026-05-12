Audit and fix brittle selectors in: $ARGUMENTS

If no argument is given, scan all page object files under `pages/`.

## What counts as brittle

Rank from most to least stable (1 = keep, 7 = replace):

1. `get_by_role(...)` with `name=` — semantic, screen-reader safe ✅
2. `get_by_label(...)` — tied to visible label text ✅
3. `get_by_placeholder(...)` — tied to placeholder attribute ✅
4. `get_by_text(...)` — tied to visible text (fragile if text is translated) ⚠️
5. `get_by_test_id(...)` / `locator('[data-test="..."]')` — explicit test hook ✅
6. `locator('[data-testid="..."]')` — common test hook ✅
7. `locator('.css-class')` — breaks on style refactors ❌
8. `locator('xpath=...')` — avoid entirely ❌
9. `locator('nth=...')` or `:nth-child(...)` — position-based, breaks on DOM reorder ❌

## Steps

1. **For each page object file**, list every locator with its current rank.
2. **For brittle locators (rank 7–9)**:
   - Use the Playwright MCP browser tools to navigate to the page and inspect the element.
   - Find the best stable locator (rank 1–5) for the same element.
   - Propose the replacement, showing `old → new`.
3. **Apply fixes** — edit the page object files directly.
4. **Run the tests** — run `pytest --collect-only -q` to confirm collection, then run the affected test files.
5. **Report** — output a table:

| File | Locator | Old (rank) | New (rank) | Status |
|---|---|---|---|---|
| pages/login_page.py | self.username | `.form-control` (7) | `get_by_label("Username")` (2) | Fixed |

If a brittle locator cannot be improved without a `data-test` attribute being added by a developer, flag it as `NEEDS_DEV_HOOK` and do not change it.
