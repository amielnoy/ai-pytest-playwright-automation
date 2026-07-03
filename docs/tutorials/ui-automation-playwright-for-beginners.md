# UI Automation with Playwright — A Beginner's Step-by-Step Tutorial

This tutorial takes you from zero to running and understanding a real UI test in this repository, then writing one of your own. Everything here references actual files in the project — open them as you read. No prior automation experience needed.

**What you'll do:** run a real registration test in a visible browser, understand every layer it touches (test → fixtures → page objects → data), then write your own test.

**Time:** 60–90 minutes.

---

## Part 1 — Setup (10 min)

You need Python 3.11+ and Node.js installed. Then, in the project folder:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install the Chromium browser Playwright drives
playwright install chromium

# 3. Sanity check — unit tests need no browser or network
pytest tests/unit -q
```

If step 3 ends with something like `84 passed`, your setup works. If not, see Troubleshooting at the bottom.

**One config tweak so you can watch:** open `config/config.json` and confirm:

```json
"headless": false,
"slow_mo": 1000
```

`headless: false` shows the browser window; `slow_mo: 1000` slows every action to 1 second so your eyes can follow. (In CI these are `true` and `0`.)

---

## Part 2 — Run your first test and watch it (5 min)

```bash
pytest tests/web-ui/test_registration.py::TestRegistration::test_register_new_user
```

A Chromium window opens, navigates to https://tutorialsninja.com/demo, clicks "My Account → Register", fills the registration form field by field, submits, and verifies the success page. Then it closes and pytest prints `1 passed`.

That long command is pytest's addressing scheme: `file::class::test`. You can also run the whole file (`pytest tests/web-ui/test_registration.py`) or everything with a marker (`pytest -m registration`).

---

## Part 3 — What just happened: the test file (15 min)

Open `tests/web-ui/test_registration.py`. The core of what you just ran:

```python
@allure.feature("Registration")
@pytest.mark.registration
class TestRegistration:

    @allure.title("Successful new-user registration")
    def test_register_new_user(
        self, registration_pages: RegistrationPages, registration_data: dict
    ):
        registration_pages.home.open()

        with allure.step("Navigate to Register page"):
            registration_pages.home.go_to_register()

        with allure.step(f"Fill registration form for {registration_data['email']}"):
            registration_pages.register.register(
                first_name=registration_data["first_name"],
                ...
            )
```

Read it top to bottom and notice what's **missing**: there are no CSS selectors, no URLs, no `page.click(...)`. The test reads like a description of user behavior. Three mechanisms make that possible:

1. **Decorators** — `@pytest.mark.registration` tags the test (markers live in `pytest.ini`); the `@allure.*` decorators and `with allure.step(...)` blocks structure the report you'll see in Part 6.
2. **Parameters are fixtures** — `registration_pages` and `registration_data` are not variables you created; pytest *injects* them. That's the fixture system (Part 5).
3. **Actions live in page objects** — `registration_pages.register.register(...)` hides all browser mechanics (Part 4).

---

## Part 4 — Page Objects: where selectors live (15 min)

The rule of this repo: **selectors never appear in tests.** Every page of the site is a Python class under `pages/`.

### The base: `pages/base_page.py`

Every page class extends `BasePage`, which holds what all pages share:

```python
class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        ...

    def navigate(self, path: str = "", wait_until: str = "domcontentloaded") -> None:
        ...

    @property
    def title(self) -> str:
        return self.page.title()
```

So every page object knows how to navigate, read the title/URL, and take a screenshot — written once.

### A concrete page: `pages/register_page.py`

```python
class RegisterPage(BasePage):
    _ERROR_WARNING_SELECTOR = ".alert-danger"

    def register(self, first_name, last_name, email, telephone,
                 password, confirm_password, newsletter=False) -> None:
        self.form.fill(first_name, last_name, email, telephone,
                       password, confirm_password, newsletter)
        self.form.accept_privacy_policy()
        self.form.submit()

    def is_registration_successful(self) -> bool:
        return self.form.is_submitted_successfully()
```

Two things to notice:

- Selectors are **class constants** (`_ERROR_WARNING_SELECTOR = ".alert-danger"`), each defined exactly once. When the site's HTML changes, you fix one line here — not twenty tests.
- The form details are delegated to a **component** (`RegistrationFormComponent` in `pages/components/`). Pieces of UI that appear in a page get their own class, same idea one level down.

**Why this matters:** imagine the site renames the "Continue" button. Without POM, you'd hunt through every test. With POM, one constant changes and every test is fixed.

*Bonus for later:* `pages/self_healing.py` gives locators an approved fallback list — if the primary selector breaks, a fallback is used and the event is recorded so you can fix the selector. Deterministic, no AI guessing.

---

## Part 5 — Fixtures: how tests get what they need (15 min)

Fixtures are pytest's dependency injection: a test names a parameter, pytest builds and passes it. This repo defines them in two places.

### The browser chain — root `conftest.py`

```
browser_instance (scope: session)  →  one Chromium for the entire run
        └── context (per test)     →  a fresh, isolated browser profile
                └── page (per test) →  the tab your test drives
```

Why a chain? Launching a browser is slow, so it's shared. But each test gets a **fresh context** — clean cookies, clean storage — so no test can leak state into another. That's test isolation, and it's why you can run tests in any order.

Two more things `conftest.py` does automatically for every test:

- The autouse `log` fixture buffers all log lines and attaches them to the Allure report.
- The `pytest_runtest_makereport` hook attaches a **screenshot on every failure**.

You wrote zero code for either — they come with the framework.

### Page and data fixtures — `tests/fixtures/`

`tests/fixtures/pages.py` builds page objects from the chain:

```python
@pytest.fixture
def register_page(page, app_url: str) -> RegisterPage:
    return RegisterPage(page, app_url)
```

`tests/fixtures/data.py` loads inputs. The registration data comes from `data/test_data.json`:

```json
{
  "first_name": "Amiel",
  "email": "automation+{ts}@example.com",
  "password": "TestPass123!"
}
```

Notice `{ts}` — `utils/data_loader.py` replaces it with the current Unix timestamp when loading. That's why the test can register a "new" user on every run: each run gets a unique email. A tiny trick that kills an entire class of "user already exists" flaky failures.

**The full journey, once more:** test asks for `registration_pages` → pytest builds `page` (via context, via browser) and `app_url` (from `config/config.json` via `data_loader`) → builds the page objects → the test calls `register(...)` → the page object's component fills the real form.

---

## Part 6 — See your test in a report (5 min)

```bash
pytest tests/web-ui/test_registration.py --alluredir=allure-results
npm run allure:generate
npm run allure:open
```

A browser opens the Allure report. Find your test and click it: you'll see the named steps (`Navigate to Register page`, `Fill registration form for ...`), the attached logs, and — for failed tests — a screenshot from the exact moment of failure.

Want to see a failure on purpose? Run `pytest tests/web-ui/test_intentional_failure.py --alluredir=allure-results` and regenerate the report. Failure debugging here is: read the step it died on → look at the screenshot → read the logs. That workflow is 80% of real automation work.

---

## Part 7 — Write your own test, step by step (20 min)

Goal: verify that registering with a **mismatched password confirmation** shows an error. A realistic negative test.

**Step 1.** Create `tests/web-ui/test_password_mismatch.py`:

```python
import allure
import pytest

from tests.page_records import RegistrationPages


@allure.feature("Registration")
@allure.story("Validation errors")
@pytest.mark.registration
class TestPasswordMismatch:

    @allure.title("Mismatched password confirmation is rejected")
    def test_password_mismatch_shows_error(
        self, registration_pages: RegistrationPages, registration_data: dict
    ):
        registration_pages.home.open()

        with allure.step("Navigate to Register page"):
            registration_pages.home.go_to_register()

        with allure.step("Submit form with mismatched passwords"):
            registration_pages.register.register(
                first_name=registration_data["first_name"],
                last_name=registration_data["last_name"],
                email=registration_data["email"],
                telephone=registration_data["telephone"],
                password=registration_data["password"],
                confirm_password="DifferentPass999!",   # the deliberate mismatch
            )

        with allure.step("Verify registration did NOT succeed"):
            assert not registration_pages.register.is_registration_successful()
```

**Step 2.** Check pytest can find it, without running the browser:

```bash
pytest --collect-only -q tests/web-ui/test_password_mismatch.py
```

**Step 3.** Run it and watch: `pytest tests/web-ui/test_password_mismatch.py`

**Step 4.** Review your own work against the repo's rules:

- No selectors in the test ✅ (only page-object methods)
- Marker present ✅ (`@pytest.mark.registration`)
- Allure decorators + steps ✅
- Data from the fixture, not hard-coded ✅ (only the mismatch is literal — it *is* the test case)

That checklist is exactly what `/review-tests` (a Claude Code slash command in this repo) audits automatically.

**Stretch exercise:** the site shows a specific error text on mismatch. Add a method to `RegisterPage` that returns the confirmation-error text (put the selector in the page class!), then assert on it in your test. You've now made your first page-object change — the real skill.

---

## Part 8 — Troubleshooting

| Symptom | Cause & fix |
|---|---|
| `playwright: command not found` | Run `pip install -r requirements.txt` first, then `playwright install chromium`. |
| `Executable doesn't exist` on run | Browser not installed — `playwright install chromium`. |
| Test hangs then times out | The demo site is slow/down. Check https://tutorialsninja.com/demo in your own browser; raise `timeout` in `config/config.json`. |
| Browser doesn't appear | `headless` is `true` in `config/config.json`. |
| "Email already registered" errors | You hard-coded an email. Use `registration_data` — the `{ts}` placeholder guarantees uniqueness. |
| Test passes alone, fails in a batch | State leaking between tests — you probably bypassed the `context`/`page` fixtures. Always take `page` from the fixture. |
| `fixture 'X' not found` | Fixture name typo, or it lives in `tests/fixtures/` but isn't registered — check root `conftest.py` imports. |

---

## What's next

1. Read `tests/web-ui/test_search_under_price.py` and `pages/search_results_page.py` — same pattern, with data parsing.
2. Move down the pyramid: `tests/api/` shows the same discipline without a browser (service classes instead of page objects).
3. Then the fun part: section 05 of the academy site — testing AI systems and letting AI agents analyze your failures.

Questions? Join the Telegram community linked on the academy site.
