import allure
import pytest
from playwright.sync_api import Page

from pages.search_results_page import SearchResultsPage
from pages.cart_page import CartPage
from utils.data_loader import get_test_data


@allure.feature("Cart")
@allure.story("assertCartTotalNotExceeds")
@pytest.mark.cart
class TestCartTotalNotExceeds:

    @allure.title("Cart total does not exceed the configured maximum")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_total_not_exceeds(self, page: Page, app_url: str):
        search_data = get_test_data("search")
        cart_data = get_test_data("cart")
        query = search_data["query"]
        max_price = search_data["max_price"]
        limit = search_data["limit"]
        max_total = cart_data["max_total"]

        results_page = SearchResultsPage(page, app_url)

        with allure.step(f"Search '{query}' and collect products under ${max_price}"):
            products = results_page.get_products_under_price(
                query=query, max_price=max_price, limit=limit
            )

        assert products, f"No products found for query='{query}' under ${max_price}"

        with allure.step("Add products to cart"):
            results_page.add_items_to_cart(products)

        cart = CartPage(page, app_url)

        with allure.step("Open cart and read total"):
            cart.open()
            total = cart.get_cart_total()

        allure.attach(
            f"Cart total: ${total:.2f}\nMax allowed: ${max_total:.2f}",
            name="Cart total check",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step(f"Assert cart total ${total:.2f} <= ${max_total:.2f}"):
            assert cart.assert_total_not_exceeds(max_total), (
                f"Cart total ${total:.2f} exceeds the allowed maximum of ${max_total:.2f}"
            )

    @allure.title("Cart total stays under per-item max_price * item count")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_total_consistent_with_item_prices(self, page: Page, app_url: str):
        search_data = get_test_data("search")
        query = search_data["query"]
        max_price = search_data["max_price"]
        limit = search_data["limit"]

        results_page = SearchResultsPage(page, app_url)

        with allure.step("Collect and add products"):
            products = results_page.get_products_under_price(
                query=query, max_price=max_price, limit=limit
            )
            assert products, "No products found"
            results_page.add_items_to_cart(products)

        cart = CartPage(page, app_url)

        with allure.step("Verify theoretical upper bound (max_price * count)"):
            cart.open()
            total = cart.get_cart_total()
            upper_bound = max_price * len(products)
            # Each added item is <= max_price so the sum must be <= upper_bound
            assert total <= upper_bound, (
                f"Cart total ${total:.2f} exceeds upper bound "
                f"${max_price} × {len(products)} = ${upper_bound:.2f}"
            )
