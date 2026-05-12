# Session 3 — Playwright Basics & Your First Python Framework

## Learning Objectives

By the end of this session you will be able to:

- Explain how Playwright auto-wait eliminates `time.sleep()`.
- Choose the correct locator strategy for a given element and justify the choice.
- Write assertions with `expect()` instead of bare `assert` on DOM values.
- Set up pytest fixtures at the right scope (`session`, `module`, `function`).
- Use `@pytest.mark.parametrize` to drive negative tests with multiple inputs.
- Debug a failing test using the Playwright Trace Viewer.
- Run tests in parallel with `pytest-xdist` and understand scope-based distribution.

---

## How Playwright Works

Playwright controls a real browser (Chromium, Firefox, WebKit) over the DevTools Protocol.
Every action — `click`, `fill`, `goto` — automatically waits for the element to be ready.
This built-in **auto-wait** eliminates the need for `time.sleep()` calls.

The Python sync API (`from playwright.sync_api import sync_playwright`) runs sequentially and is easier to read and debug than the async variant. Use the sync API for UI automation unless you have a specific async requirement.

---

## Locator Strategy

Choose locators in this order (most stable → most fragile):

1. `get_by_role('button', name='Login')` — semantic, matches what screen readers see.
2. `get_by_label('Email address')` — best for form inputs.
3. `get_by_placeholder('Search…')` — inputs with placeholder text.
4. `get_by_text('Submit')` — static visible text.
5. `get_by_test_id('submit-btn')` — `data-testid` attribute added by developers.
6. `locator('[data-test="error"]')` — attribute fallback.
7. `locator('.css-class')` — last resort; breaks on style refactors.

Never use XPath in new code. Avoid nth-child selectors.

---

## Assertions with `expect()`

Always use `expect()` — it retries until the condition is true or the timeout expires:

- `expect(locator).to_be_visible()` — element present and visible.
- `expect(locator).to_have_text('…')` — exact or regex text.
- `expect(locator).to_contain_text('…')` — partial match.
- `expect(locator).to_have_value('…')` — input field value.
- `expect(locator).to_have_count(n)` — exactly n matching elements.
- `expect(page).to_have_url('…')` — navigation completed.

Never use bare `assert locator.inner_text() == '…'` — it reads the DOM once with no retry.

---

## pytest Fixtures

Fixtures provide setup and teardown for tests. Scope controls sharing:

- `session` — one browser instance for the whole run (fastest, no isolation).
- `module` — new context per file.
- `function` — new page per test (default; full isolation).

A `logged_in_page` fixture logs in once and yields the page, so login steps are not repeated in every test that needs an authenticated state.

---

## Parametrize for Negative Tests

`@pytest.mark.parametrize` turns one test function into N test cases — ideal for covering multiple invalid inputs with a single block of assertion logic.

```python
@pytest.mark.parametrize("user,pwd,msg", [
    ("locked_out_user", "secret_sauce", "locked out"),
    ("",                "secret_sauce", "Username is required"),
    ("standard_user",   "",             "Password is required"),
])
def test_login_negative(page, user, pwd, msg):
    …
```

---

## Debugging with the Playwright Trace Viewer

When a test fails in CI you have no browser to observe. The Trace Viewer captures every action, network request, and screenshot so you can replay the failure locally.

**Enable traces in `conftest.py`:**

```python
@pytest.fixture
def context(browser):
    ctx = browser.new_context()
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield ctx
    ctx.tracing.stop(path="trace.zip")
    ctx.close()
```

**Open the trace:**

```bash
playwright show-trace trace.zip
```

The viewer shows a timeline of every action, a DOM snapshot at each step, and the network log.

**Other debugging options:**

| Technique | Command | When to use |
|---|---|---|
| Headed mode | `pytest --headed` | Watch the browser live during a local run |
| Slow motion | `pytest --slowmo=500` | Slow each action by 500 ms to spot timing issues |
| Last-failed | `pytest --lf` | Re-run only the tests that failed in the previous run |
| Single test | `pytest -k "test_name"` | Isolate one case during debugging |
| Verbose | `pytest -v` | See individual test names and pass/fail inline |

**Trace Viewer workflow for CI failures:**

1. Add the tracing fixture above to `conftest.py`.
2. Upload `trace.zip` as a CI artifact (see Session 10 for the GitHub Actions step).
3. Download the artifact, run `playwright show-trace trace.zip`.
4. Step through actions until you see where the DOM diverged from your assertion.

---

## Parallel Test Execution with pytest-xdist

Running tests serially is slow. `pytest-xdist` distributes tests across worker processes.

**Install:**

```bash
pip install pytest-xdist
```

**Run with auto-detected CPU count:**

```bash
pytest -n auto
```

**Distribution modes:**

| Flag | Behaviour |
|---|---|
| `-n auto` | One worker per CPU core |
| `-n 4` | Exactly four workers |
| `--dist loadscope` | Tests in the same module run on the same worker (safe for module-scoped fixtures) |
| `--dist loadfile` | Tests in the same file run together |
| `-n 0` | Disable xdist — run serially (useful for debugging) |

**Rule:** use `--dist loadscope` when tests in the same file share a `module`-scoped fixture. Without it, two workers may create conflicting browser contexts.

The main project already has `pytest.ini` configured with `-n auto --dist loadscope` — you can override it locally with `-n 0` when debugging.

---

## Quick Allure Setup

Allure gives tests a persistent HTML report. Full setup is covered in Session 10, but you can start collecting results immediately:

```bash
pip install allure-pytest
pytest --alluredir=allure-results
npx allure generate allure-results
npx allure open
```

Decorate your tests with `@allure.feature`, `@allure.story`, and `@allure.title` — the report groups them by feature and shows step-level detail.

---

## Session Completion Checklist

Before moving to Session 4, verify you can answer yes to each item:

- [ ] I ran `test_login.py`, `test_add_to_cart.py`, and `test_sort.py` successfully.
- [ ] I can explain auto-wait and why `time.sleep()` is wrong in Playwright tests.
- [ ] I chose a locator for a real element without defaulting to CSS class or XPath.
- [ ] I wrote at least one `expect()` assertion and understand why bare `assert` is unreliable.
- [ ] I debugged a failing test using `--headed` or the Trace Viewer.
- [ ] I ran the suite with `-n auto` and again with `-n 0` and noticed the difference.
- [ ] I completed the exercises in `EXERCISES.md`.
