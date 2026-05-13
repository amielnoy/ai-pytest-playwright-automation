"""
Session 14 conftest — what's NEW vs session 9
─────────────────────────────────────────────
Session 9 had:  login_page, inventory_page, cart_page
Session 14 adds: heal_tracker          ← self-healing selector wrapper
                screenshot_on_failure ← auto-attach PNG on failure (autouse)

Run:  pytest course/session_14_ai_tools/ -v
Needs: ANTHROPIC_API_KEY (heal_tracker uses Claude; tests skip if missing)
"""
import pathlib
import pytest
from playwright.sync_api import Page
from course.framework.pages import LoginPage, InventoryPage, CartPage
from course.framework.tools import HealTracker

BASE_URL = "https://www.saucedemo.com"
_USER = "standard_user"
_PASS = "secret_sauce"


@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}


# ── carried forward from session 9 ────────────────────────────────────────────

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page, BASE_URL).open()


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    return LoginPage(page, BASE_URL).open().login(_USER, _PASS)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    inventory = LoginPage(page, BASE_URL).open().login(_USER, _PASS)
    inventory.add_first_item()
    return inventory.go_to_cart()


# ── NEW in session 13 — AI tools ──────────────────────────────────────────────

@pytest.fixture
def heal_tracker() -> HealTracker:
    """Accumulate self-heal events; print a summary after the test."""
    tracker = HealTracker()
    yield tracker
    tracker.print_summary()


# Screenshot on failure — autouse so it applies to every test in this session
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page: Page):
    """NEW in session 13 — save a PNG whenever a test fails."""
    yield
    node = request.node
    if getattr(getattr(node, "rep_call", None), "failed", False):
        pathlib.Path("screenshots").mkdir(exist_ok=True)
        path = f"screenshots/{node.name}.png"
        page.screenshot(path=path)
        print(f"\n[screenshot] {path}")
