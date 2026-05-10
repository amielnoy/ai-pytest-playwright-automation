"""
Session 7 — tests that demonstrate CI-aware patterns.

New in this session:
  • @pytest.mark.smoke / @pytest.mark.regression tags control what CI runs
  • @pytest.mark.flaky_prone marks tests known to be intermittent
  • failure_record autouse fixture writes JSONL in CI for AI analysis
  • group_by_cause() shows how failures are bucketed for the PR comment

Run:  pytest course/session_7_ci_cd_ai_analysis/ -v -m smoke
      pytest course/session_7_ci_cd_ai_analysis/ -v -m regression
"""
import pytest
from playwright.sync_api import Page, expect
from course.framework.pages import LoginPage, InventoryPage, CartPage
from course.framework.analysis import group_by_cause

BASE_URL = "https://www.saucedemo.com"


# ── smoke tests — must pass on every commit ───────────────────────────────────

@pytest.mark.smoke
def test_login_page_loads(page: Page):
    """Fastest possible smoke check: can we reach the login page?"""
    page.goto(BASE_URL)
    expect(page.get_by_placeholder("Username")).to_be_visible()
    expect(page.get_by_placeholder("Password")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()


@pytest.mark.smoke
def test_standard_user_can_login(inventory_page: InventoryPage):
    """Core happy path: standard_user reaches /inventory.html."""
    expect(inventory_page.page).to_have_url(f"{BASE_URL}/inventory.html")
    names = inventory_page.product_names()
    assert len(names) > 0


@pytest.mark.smoke
def test_add_to_cart_smoke(inventory_page: InventoryPage):
    """Smoke: adding one item updates the badge."""
    inventory_page.add_first_item().expect_cart_count(1)


# ── regression tests — full suite, run on PR ─────────────────────────────────

@pytest.mark.regression
def test_locked_out_user_cannot_login(login_page):
    """Regression: locked_out_user sees the correct error."""
    login_page.login("locked_out_user", "secret_sauce").expect_error("locked out")


@pytest.mark.regression
def test_sort_price_ascending(inventory_page: InventoryPage):
    """Regression: price sort low→high is correct."""
    inventory_page.sort_by("lohi")
    prices = inventory_page.product_prices()
    assert prices == sorted(prices), f"Prices not ascending: {prices}"


@pytest.mark.regression
def test_cart_persists_after_navigate(inventory_page: InventoryPage):
    """Regression: cart badge survives navigating away and back."""
    inventory_page.add_first_item()
    inventory_page.page.get_by_role("link", name="About").click()
    inventory_page.page.go_back()
    inventory_page.expect_cart_count(1)


@pytest.mark.regression
def test_full_checkout_flow(inventory_page: InventoryPage):
    """Regression: happy-path checkout from add-to-cart to order complete."""
    from course.framework.data import make_checkout_info
    info = make_checkout_info()
    cart = inventory_page.add_first_item().go_to_cart()
    cart.expect_item_count(1)
    (cart.proceed_to_checkout()
         .fill_info(info.first_name, info.last_name, info.postal_code)
         .continue_to_overview()
         .finish()
         .expect_order_complete())


# ── flaky_prone — monitored by flaky_detector ─────────────────────────────────

@pytest.mark.flaky_prone
@pytest.mark.regression
def test_performance_glitch_user_can_login(page: Page):
    """
    Marked flaky_prone: performance_glitch_user intentionally introduces a
    slow login. On slow CI runners this occasionally races with the timeout.
    The flaky_detector tracks the pass/fail rate across the last 30 runs.
    """
    inventory = LoginPage(page, BASE_URL).open().login(
        "performance_glitch_user", "secret_sauce"
    )
    expect(inventory.page).to_have_url(f"{BASE_URL}/inventory.html")


# ── unit-style: testing the analysis helpers themselves ───────────────────────

def test_group_by_cause_buckets_timeout_failures():
    failures = [
        {"test": "test_a", "message": "TimeoutError: waiting for selector"},
        {"test": "test_b", "message": "AssertionError: expected 'foo' to equal 'bar'"},
        {"test": "test_c", "message": "TimeoutError: element not visible"},
        {"test": "test_d", "message": "ConnectionError: dns lookup failed"},
    ]
    groups = group_by_cause(failures)
    assert len(groups["timeout"]) == 2
    assert len(groups["assertion"]) == 1
    assert len(groups["network"]) == 1


def test_group_by_cause_puts_unknown_into_other():
    failures = [{"test": "test_x", "message": "some random error we have not seen"}]
    groups = group_by_cause(failures)
    assert "other" in groups
    assert groups["other"][0]["test"] == "test_x"
