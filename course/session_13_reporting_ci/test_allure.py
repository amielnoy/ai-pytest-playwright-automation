"""
Session 13 — Allure 3 reporting: the final, fully-decorated test suite.

Every test has:
  @allure.feature / @allure.story / @allure.title / @allure.severity
  with allure.step(...)  wraps each logical action

The conftest.py (session 13) also writes categories.json + environment.properties
before the run, so the Allure 3 Overview tab is fully populated.

Run:  pytest course/session_13_reporting_ci/ -v --alluredir=allure-results
Then: npx allure generate allure-results && npx allure open
"""
import allure
import pytest
from playwright.sync_api import Page, expect

from course.framework.pages import LoginPage, InventoryPage, CartPage
from course.framework.data import make_checkout_info, LOCKED_USER
from course.framework.reporting import summarise_results, validate_decorators
from course.framework import BASE_URL, STANDARD_USER, STANDARD_PASS


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

@allure.feature("Authentication")
@allure.story("Successful login")
@allure.title("Standard user reaches the inventory page")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_login_happy_path(inventory_page: InventoryPage):
    with allure.step("Assert URL is /inventory.html"):
        expect(inventory_page.page).to_have_url(f"{BASE_URL}/inventory.html")
    with allure.step("Assert at least one product is present"):
        assert len(inventory_page.product_names()) > 0


@allure.feature("Authentication")
@allure.story("Login failure")
@allure.title("Wrong password returns 'do not match' error")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_wrong_password_error(login_page):
    with allure.step("Attempt login with wrong password"):
        login_page.login(STANDARD_USER, "wrong_password")
    with allure.step("Assert error message contains 'do not match'"):
        login_page.expect_error("do not match")


@allure.feature("Authentication")
@allure.story("Login failure")
@allure.title("Locked-out user sees locked-out error")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_locked_out_user(login_page):
    with allure.step("Attempt login with locked_out_user"):
        login_page.login(LOCKED_USER.username, LOCKED_USER.password)
    with allure.step("Assert locked-out error shown"):
        login_page.expect_error("locked out")


# ─────────────────────────────────────────────────────────────────────────────
# Inventory + Cart
# ─────────────────────────────────────────────────────────────────────────────

@allure.feature("Cart")
@allure.story("Add to cart")
@allure.title("Badge updates to 1 after adding one item")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_add_one_item(inventory_page: InventoryPage):
    with allure.step("Click Add to cart on the first product"):
        inventory_page.add_first_item()
    with allure.step("Assert badge shows '1'"):
        inventory_page.expect_cart_count(1)


@allure.feature("Cart")
@allure.story("Cart contents")
@allure.title("Cart page shows correct item after navigating from inventory")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_cart_shows_added_item(inventory_page: InventoryPage):
    with allure.step("Add Sauce Labs Backpack"):
        cart = inventory_page.add_item_by_name("Sauce Labs Backpack").go_to_cart()
    with allure.step("Assert one item in cart"):
        cart.expect_item_count(1)
    with allure.step("Assert item name in cart"):
        assert "Sauce Labs Backpack" in cart.item_names()


# ─────────────────────────────────────────────────────────────────────────────
# Checkout
# ─────────────────────────────────────────────────────────────────────────────

@allure.feature("Checkout")
@allure.story("Happy path")
@allure.title("Full purchase flow completes with order confirmation")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_full_purchase(inventory_page: InventoryPage):
    info = make_checkout_info()
    with allure.step("Add first item and navigate to cart"):
        cart = inventory_page.add_first_item().go_to_cart()
    with allure.step("Proceed through checkout with valid info"):
        (cart.proceed_to_checkout()
             .fill_info(info.first_name, info.last_name, info.postal_code)
             .continue_to_overview()
             .finish()
             .expect_order_complete())


@allure.feature("Checkout")
@allure.story("Validation")
@allure.title("Missing postal code shows 'Postal Code is required'")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_checkout_missing_postal(inventory_page: InventoryPage):
    info = make_checkout_info(missing="postal_code")
    with allure.step("Proceed to checkout info step"):
        checkout = inventory_page.add_first_item().go_to_cart().proceed_to_checkout()
    with allure.step("Fill info with blank postal code and continue"):
        checkout.fill_info(info.first_name, info.last_name, info.postal_code)
        checkout.continue_to_overview()
    with allure.step("Assert postal code error is shown"):
        checkout.expect_error("Postal Code is required")


# ─────────────────────────────────────────────────────────────────────────────
# Reporting helpers (unit-style — no browser needed)
# ─────────────────────────────────────────────────────────────────────────────

@allure.feature("Reporting")
@allure.story("Result summary")
@allure.title("summarise_results returns empty dict when no results directory exists")
@allure.severity(allure.severity_level.MINOR)
def test_summarise_results_empty(tmp_path):
    """summarise_results gracefully returns {} for an empty directory."""
    from pathlib import Path
    from course.framework.reporting import summarise_results
    result = summarise_results(tmp_path)
    assert result == {}


@allure.feature("Reporting")
@allure.story("Decorator validation")
@allure.title("validate_decorators returns no findings for a well-decorated test file")
@allure.severity(allure.severity_level.MINOR)
def test_validate_decorators_on_this_file(tmp_path):
    """The session 13 test file itself should pass decorator validation."""
    from pathlib import Path
    from course.framework.reporting import validate_decorators
    import shutil
    shutil.copy(__file__, tmp_path / "test_allure.py")
    findings = validate_decorators(tests_dir=tmp_path)
    assert findings == [], f"Unexpected decorator violations: {findings}"
