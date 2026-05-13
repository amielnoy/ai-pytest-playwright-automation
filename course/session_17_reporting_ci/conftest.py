"""
Session 17 conftest — what's NEW vs session 16
─────────────────────────────────────────────
Session 16 had:  failure_record, CI markers
Session 17 adds: pytest_configure writes categories.json + environment.properties
                into allure-results/ BEFORE any test runs, so the generated
                Allure 3 report shows categories and build context on the
                Overview tab.
                allure_screenshot attaches PNG evidence to failed tests.

This is the reporting-ready conftest used before the final capstone.

Run:  pytest course/session_17_reporting_ci/ -v --alluredir=allure-results
Then: npx allure generate allure-results && npx allure open
"""
import json
import os
import pathlib
import pytest
import allure
from playwright.sync_api import Page
from course.framework.pages import LoginPage, InventoryPage, CartPage
from course.framework.tools import HealTracker
from course.framework.agents import run_agent
from course.framework.reporting import write_categories, write_environment

BASE_URL = "https://www.saucedemo.com"
_USER = "standard_user"
_PASS = "secret_sauce"
_FAILURES_LOG = pathlib.Path("ci-artifacts/failures.jsonl")


# ── NEW in session 16 — Allure categories + environment ────────────────────────

def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: fast sanity checks")
    config.addinivalue_line("markers", "regression: full regression suite")
    config.addinivalue_line("markers", "flaky_prone: known intermittent — monitored")
    write_categories()
    write_environment()


# ── carried forward from session 15 ────────────────────────────────────────────

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
def failure_record(request):
    yield
    node = request.node
    if not os.environ.get("CI"):
        return
    if getattr(getattr(node, "rep_call", None), "failed", False):
        _FAILURES_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {"test": node.nodeid, "message": str(getattr(node, "rep_call", "")).split("\n")[0]}
        with _FAILURES_LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")


@pytest.fixture(autouse=True)
def allure_screenshot(request, page: Page):
    yield
    node = request.node
    if getattr(getattr(node, "rep_call", None), "failed", False):
        allure.attach(
            page.screenshot(),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
