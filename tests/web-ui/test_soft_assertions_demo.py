"""
Soft vs Hard Assertions — Teaching Demo
========================================

Hard assertion  → plain ``assert``
  Stops the test immediately at the first failure.
  Everything after the failing assert is SKIPPED.
  Use when a later step DEPENDS on this condition (prerequisite).

Soft assertion  → ``pytest_check``
  Collects ALL failures and reports them together at the end.
  Every check always runs, even if earlier ones failed.
  Use when conditions are INDEPENDENT and you want the full failure
  picture in one run — e.g. accessibility audits, data-integrity loops,
  multi-property UI checks.

Rule of thumb
-------------
  1. Hard assert to confirm you have something to work with (prerequisite).
  2. Soft check to evaluate every independent property of that thing.
"""

import allure
import pytest
import pytest_check as check

from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
from pages.search_results_page import SearchResultsPage


@allure.feature("Teaching")
@allure.story("Soft vs Hard Assertions")
@pytest.mark.sanity
class TestSoftAssertionsDemo:

    # ------------------------------------------------------------------
    # 1. Side-by-side: hard vs soft on the same multi-property check
    # ------------------------------------------------------------------

    @allure.title("[HARD] Home header controls — stops at the first missing control")
    @allure.severity(allure.severity_level.NORMAL)
    def test_home_header_hard(self, home_page: HomePage):
        """
        If currency_dropdown is absent the test fails here and NEVER checks
        search_input or cart_summary.  You only learn about one broken control
        per run, even if three are missing.
        """
        home_page.open()

        with allure.step("Assert each header control (stops at first failure)"):
            assert home_page.has_currency_dropdown(), "Currency dropdown missing"
            assert home_page.has_search_input(), "Search input missing"        # skipped if above fails
            assert home_page.has_empty_cart_summary(), "Cart summary missing"  # skipped if either above fails

    @allure.title("[SOFT] Home header controls — all failures collected in one run")
    @allure.severity(allure.severity_level.NORMAL)
    def test_home_header_soft(self, home_page: HomePage):
        """
        All three checks always run.  If two controls are missing you see both
        failures immediately — no need to re-run after fixing the first one.
        """
        home_page.open()

        with allure.step("Soft-check every header control (all failures collected)"):
            check.is_true(home_page.has_currency_dropdown(), "Currency dropdown missing")
            check.is_true(home_page.has_search_input(), "Search input missing")
            check.is_true(home_page.has_empty_cart_summary(), "Cart summary missing")

    # ------------------------------------------------------------------
    # 2. Multi-property product detail check
    # ------------------------------------------------------------------

    @allure.title("[SOFT] MacBook detail — heading, quantity, and cart button all checked")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_detail_soft(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        product_detail_page: ProductDetailPage,
    ):
        """
        Three independent properties of the same page.  A hard assert on the
        heading would hide whether the quantity or button is also broken.
        Soft assertions give the full picture in one shot.
        """
        with allure.step("Navigate to MacBook product detail page"):
            # Hard assert — we cannot check detail properties without landing on the page.
            home_page.open()
            home_page.search("MacBook")
            search_results_page.open_product("MacBook")

        with allure.step("Soft-check all detail page properties"):
            check.is_true(
                product_detail_page.has_product_heading("MacBook"),
                "Product heading 'MacBook' not visible",
            )
            check.is_true(
                product_detail_page.has_default_quantity(),
                "Default quantity is not '1'",
            )
            check.is_true(
                product_detail_page.has_add_to_cart_button(),
                "Add to Cart button not visible",
            )

    # ------------------------------------------------------------------
    # 3. Data-integrity loop — the killer use case for soft assertions
    # ------------------------------------------------------------------

    @allure.title("[SOFT] Search result prices — every failing product reported")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_prices_soft_loop(self, search_results_page: SearchResultsPage):
        """
        Without pytest-check a loop stops at the FIRST bad product.
        With soft assertions every product is inspected and ALL violations
        are listed together — essential for a data-integrity sweep.

        Notice the hard assert before the loop: if there are no products
        at all, the loop body is vacuously true and would pass silently.
        A hard prerequisite assert catches that case explicitly.
        """
        with allure.step("Fetch MacBook products (hard assert: must have results)"):
            products = search_results_page.get_products_under_price(
                query="MacBook", max_price=9999.0, limit=10
            )
            # Hard assert — prerequisite: nothing to validate without results.
            assert products, "No MacBook products returned — cannot validate prices"

        allure.attach(
            "\n".join(f"{p.name} — ${p.price}" for p in products),
            name="Products under inspection",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Soft-check every product has a positive price"):
            for product in products:
                # check.greater(a, b) passes when a > b
                check.greater(
                    product.price,
                    0,
                    f"Non-positive price ${product.price} for '{product.name}'",
                )
