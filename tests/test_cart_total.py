import allure
import pytest
from playwright.sync_api import BrowserContext, Page

from pages.cart_page import CartPage


@allure.feature("Cart")
@allure.story("assertCartTotalNotExceeds")
@pytest.mark.cart
class TestCartTotalNotExceeds:

    @allure.title("Cart total does not exceed the configured maximum")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_total_not_exceeds(
        self, page: Page, context: BrowserContext, app_url: str, api_cart
    ):
        ocsessid, _, max_total, _ = api_cart

        # Inject the API session so the browser sees the pre-populated cart
        context.add_cookies([{"name": "OCSESSID", "value": ocsessid, "url": app_url}])

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
            assert total <= max_total, (
                f"Cart total ${total:.2f} exceeds the allowed maximum of ${max_total:.2f}"
            )

    @allure.title("Cart total stays under per-item max_price * item count")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_total_consistent_with_item_prices(
        self, page: Page, context: BrowserContext, app_url: str, api_cart
    ):
        ocsessid, products, _, max_price = api_cart

        context.add_cookies([{"name": "OCSESSID", "value": ocsessid, "url": app_url}])

        cart = CartPage(page, app_url)

        with allure.step("Open cart and verify total vs theoretical upper bound"):
            cart.open()
            total = cart.get_cart_total()
            upper_bound = max_price * len(products)
            assert total <= upper_bound, (
                f"Cart total ${total:.2f} exceeds upper bound "
                f"${max_price} x {len(products)} = ${upper_bound:.2f}"
            )
