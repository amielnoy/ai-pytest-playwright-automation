"""
Session 23 — Capstone: every framework layer working together.

Each test here deliberately exercises a different layer combination:
  POM + data factory          → checkout flow
  POM + sorting               → sort assertion
  POM + multiple products     → cart management
  POM + negative scenario     → validation error
  Analysis helpers (unit)     → architecture self-check

Allure decorators are present on every test (session 19 requirement).
Screenshot is automatically attached to Allure on failure (conftest.py).

Run:  pytest course/session_23_capstone/ -v --alluredir=allure-results
"""
import allure
import pytest
from playwright.sync_api import Page, expect

from course.framework.pages import LoginPage, InventoryPage, CartPage
from course.framework.data import make_checkout_info, LOCKED_USER
from course.framework import BASE_URL, STANDARD_USER, STANDARD_PASS


@allure.feature("Authentication")
class TestAuthentication:

    @allure.story("Successful login")
    @allure.title("Standard user reaches inventory page")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_standard_user_login(self, inventory_page: InventoryPage):
        with allure.step("Verify URL is /inventory.html"):
            expect(inventory_page.page).to_have_url(f"{BASE_URL}/inventory.html")
        with allure.step("Verify at least one product is visible"):
            assert len(inventory_page.product_names()) > 0

    @allure.story("Login failure")
    @allure.title("Locked-out user sees error message")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_locked_out_user_error(self, login_page):
        with allure.step("Attempt login with locked-out user"):
            login_page.login(LOCKED_USER.username, LOCKED_USER.password)
        with allure.step("Verify error message is shown"):
            login_page.expect_error("locked out")

    @allure.story("Login failure")
    @allure.title("Empty password shows validation error")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_empty_password_validation(self, login_page):
        with allure.step("Submit with empty password"):
            login_page.login(STANDARD_USER, "")
        with allure.step("Verify password required error"):
            login_page.expect_error("Password is required")


@allure.feature("Cart")
class TestCart:

    @allure.story("Add to cart")
    @allure.title("Adding one item updates badge to 1")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_add_first_item(self, inventory_page: InventoryPage):
        with allure.step("Click Add to cart on the first product"):
            inventory_page.add_first_item()
        with allure.step("Verify cart badge shows 1"):
            inventory_page.expect_cart_count(1)

    @allure.story("Add to cart")
    @allure.title("Adding a product by name works correctly")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_add_specific_product(self, inventory_page: InventoryPage):
        with allure.step("Add Sauce Labs Backpack"):
            inventory_page.add_item_by_name("Sauce Labs Backpack")
        with allure.step("Verify cart count is 1"):
            inventory_page.expect_cart_count(1)

    @allure.story("Cart management")
    @allure.title("Removing an item clears the cart badge")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_remove_item_clears_badge(self, inventory_page: InventoryPage):
        with allure.step("Add then remove the first product"):
            inventory_page.add_first_item()
            inventory_page.expect_cart_count(1)
            inventory_page.remove_item_by_name("Sauce Labs Backpack")
        with allure.step("Verify badge is gone"):
            inventory_page.expect_no_cart_badge()


@allure.feature("Checkout")
class TestCheckout:

    @allure.story("Happy path")
    @allure.title("Complete purchase flow — add → checkout → order confirmed")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_complete_purchase(self, inventory_page: InventoryPage):
        info = make_checkout_info()
        with allure.step("Add first product to cart"):
            cart = inventory_page.add_first_item().go_to_cart()
        with allure.step("Verify cart has 1 item"):
            cart.expect_item_count(1)
        with allure.step("Fill checkout info and complete order"):
            (cart.proceed_to_checkout()
                 .fill_info(info.first_name, info.last_name, info.postal_code)
                 .continue_to_overview()
                 .finish()
                 .expect_order_complete())

    @allure.story("Validation")
    @allure.title("Checkout with missing first name shows error")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_checkout_missing_first_name(self, inventory_page: InventoryPage):
        info = make_checkout_info(missing="first_name")
        with allure.step("Proceed to checkout"):
            checkout = inventory_page.add_first_item().go_to_cart().proceed_to_checkout()
        with allure.step("Fill info with blank first name"):
            checkout.fill_info(info.first_name, info.last_name, info.postal_code)
            checkout.continue_to_overview()
        with allure.step("Verify validation error"):
            checkout.expect_error("First Name is required")


@allure.feature("Inventory")
class TestInventory:

    @allure.story("Sorting")
    @allure.title("Products sorted by price ascending are in correct order")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_sort_price_low_to_high(self, inventory_page: InventoryPage):
        with allure.step("Select Price (low to high)"):
            inventory_page.sort_by("lohi")
        with allure.step("Verify prices are ascending"):
            prices = inventory_page.product_prices()
            assert prices == sorted(prices), f"Prices not ascending: {prices}"

    @allure.story("Sorting")
    @allure.title("Products sorted by name A-Z are in correct order")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_sort_name_a_to_z(self, inventory_page: InventoryPage):
        with allure.step("Select Name (A to Z)"):
            inventory_page.sort_by("az")
        with allure.step("Verify names are sorted A→Z"):
            names = inventory_page.product_names()
            assert names == sorted(names), f"Names not A→Z: {names}"
