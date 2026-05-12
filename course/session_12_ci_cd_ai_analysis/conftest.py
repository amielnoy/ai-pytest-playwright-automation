"""
Session 12 conftest — what's NEW vs session 11
─────────────────────────────────────────────
Session 11 had:  browser_agent
Session 12 adds: failure_record  ← autouse fixture that writes failed test
                                   data to failures.jsonl for CI analysis.
                pytest_configure ← registers custom markers.

Run:  pytest course/session_12_ci_cd_ai_analysis/ -v
"""
import json
import os
import pathlib
import pathlib as _pl
import pytest
from playwright.sync_api import Page
from course.framework.pages import LoginPage, InventoryPage, CartPage
from course.framework.tools import HealTracker
from course.framework.agents import run_agent

BASE_URL = "https://www.saucedemo.com"
_USER = "standard_user"
_PASS = "secret_sauce"
_FAILURES_LOG = _pl.Path("ci-artifacts/failures.jsonl")


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: fast sanity checks run on every commit")
    config.addinivalue_line("markers", "regression: full regression suite")
    config.addinivalue_line("markers", "flaky_prone: known intermittent — monitored for flakiness")


# ── carried forward from session 11 ────────────────────────────────────────────

@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}


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


@pytest.fixture
def browser_agent(page: Page):
    def _run(goal: str, max_steps: int = 15) -> list[dict]:
        return run_agent(page, goal, max_steps)
    return _run


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


# ── NEW in session 12 — CI failure tracking ────────────────────────────────────

@pytest.fixture(autouse=True)
def failure_record(request):
    """NEW in session 12 — write failed test metadata to failures.jsonl in CI."""
    yield
    node = request.node
    if not os.environ.get("CI"):
        return
    if getattr(getattr(node, "rep_call", None), "failed", False):
        _FAILURES_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "test": node.nodeid,
            "message": str(getattr(node, "rep_call", "")).split("\n")[0],
        }
        with _FAILURES_LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")
