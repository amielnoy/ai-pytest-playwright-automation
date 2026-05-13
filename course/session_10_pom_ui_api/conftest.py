"""
Session 10 conftest — what's NEW vs session 4
─────────────────────────────────────────────
Session 4 had:  browser_context_args, logged_in_page (raw Playwright)
Session 10 adds: login_page, inventory_page, cart_page  ← POM fixtures
                Every fixture returns a typed Page Object, not a raw page.

Run:  pytest course/session_10_pom_ui_api/ -v
"""
import pytest
from playwright.sync_api import Page
from course.framework.pages import LoginPage, InventoryPage, CartPage

BASE_URL = "https://www.saucedemo.com"
_USER = "standard_user"
_PASS = "secret_sauce"


@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}


# ── NEW in session 6 — POM fixtures ──────────────────────────────────────────

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Opened LoginPage — ready for credentials."""
    return LoginPage(page, BASE_URL).open()


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    """InventoryPage — standard_user already logged in."""
    return LoginPage(page, BASE_URL).open().login(_USER, _PASS)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    """CartPage — one item already added."""
    inventory = LoginPage(page, BASE_URL).open().login(_USER, _PASS)
    inventory.add_first_item()
    return inventory.go_to_cart()
