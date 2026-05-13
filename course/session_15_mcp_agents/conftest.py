"""
Session 15 conftest — what's NEW vs session 10
─────────────────────────────────────────────
Session 14 had:  heal_tracker, screenshot_on_failure
Session 15 adds: browser_agent  ← wraps run_agent() as a callable fixture
                The agent can drive the browser with plain English goals.

Run:  pytest course/session_15_mcp_agents/ -v
Needs: ANTHROPIC_API_KEY
"""
import pathlib
import pytest
from playwright.sync_api import Page
from course.framework.pages import LoginPage, InventoryPage, CartPage
from course.framework.tools import HealTracker
from course.framework.agents import run_agent

BASE_URL = "https://www.saucedemo.com"
_USER = "standard_user"
_PASS = "secret_sauce"


@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}


# ── carried forward from session 10 ────────────────────────────────────────────

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


@pytest.fixture
def heal_tracker() -> HealTracker:
    tracker = HealTracker()
    yield tracker
    tracker.print_summary()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page: Page):
    yield
    node = request.node
    if getattr(getattr(node, "rep_call", None), "failed", False):
        pathlib.Path("screenshots").mkdir(exist_ok=True)
        path = f"screenshots/{node.name}.png"
        page.screenshot(path=path)
        print(f"\n[screenshot] {path}")


# ── NEW in session 11 — AI agent ───────────────────────────────────────────────

@pytest.fixture
def browser_agent(page: Page):
    """NEW in session 11 — call agent(goal) to let Claude drive the browser.

    Returns the step log: [{"step": n, "tool": …, "input": …}, …, {"final": …}]
    """
    def _run(goal: str, max_steps: int = 15) -> list[dict]:
        return run_agent(page, goal, max_steps)
    return _run
