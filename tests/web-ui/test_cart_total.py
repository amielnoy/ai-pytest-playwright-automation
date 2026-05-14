import allure
import pytest
from playwright.sync_api import BrowserContext

from tests.page_records import CartPages


@allure.feature("Cart")
@allure.story("Cart Total Validation")
@pytest.mark.cart
class TestCartTotalNotExceeds:

    @allure.title("Cart total does not exceed the configured maximum")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("https://your-jira.atlassian.net/browse/TN-302", "TN-302")
    @allure.issue("https://your-jira.atlassian.net/browse/TN-BUG-19", "TN-BUG-19")
    def test_cart_total_not_exceeds(
        self, cart_pages: CartPages, context: BrowserContext, app_url: str, api_cart
    ):
        ocsessid, _, max_total, _ = api_cart

        # Must inject before cart_pages.cart.open() — the page fixture has not
        # navigated yet, so add_cookies takes effect on the first request.
        context.add_cookies([{"name": "OCSESSID", "value": ocsessid, "url": app_url}])

        with allure.step("Open cart and read total"):
            cart_pages.cart.open()
            total = cart_pages.cart.get_cart_total()

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
        self, cart_pages: CartPages, context: BrowserContext, app_url: str, api_cart
    ):
        ocsessid, products, _, max_price = api_cart

        # Must inject before cart_pages.cart.open() — same ordering contract as above.
        context.add_cookies([{"name": "OCSESSID", "value": ocsessid, "url": app_url}])

        with allure.step("Open cart and verify total matches sum of item subtotals"):
            cart_pages.cart.open()
            total = cart_pages.cart.get_cart_total()
            item_subtotals = cart_pages.cart.get_item_subtotals()
            assert item_subtotals, "Cart has no line items"
            expected = sum(item_subtotals)
            assert abs(total - expected) < 0.01, (
                f"Cart total ${total:.2f} does not match sum of item subtotals ${expected:.2f} "
                f"(items: {item_subtotals})"
            )
