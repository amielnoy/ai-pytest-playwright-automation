import allure
import pytest

from tests.page_records import SearchPages
from utils.data_loader import get_test_data


@allure.feature("Shopping")
@allure.story("eBay item price integrity")
@pytest.mark.cart
class TestCartTotalNotExceeds:

    @allure.title("Sum of item prices does not exceed configured max total")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_item_price_sum_not_exceeds_max(self, search_pages: SearchPages, api_cart):
        item_ids, prices, max_total, max_price = api_cart

        allure.attach(
            f"Items: {len(item_ids)}\nPrices: {prices}\nSum: ${sum(prices):.2f}\nMax: ${max_total:.2f}",
            name="Price sum check",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step(f"Assert sum of prices <= ${max_total:.2f}"):
            total = sum(prices)
            assert total <= max_total, f"Sum ${total:.2f} exceeds max ${max_total:.2f}"

    @allure.title("Item prices from search are all within per-item max_price")
    @allure.severity(allure.severity_level.NORMAL)
    def test_item_prices_within_per_item_max(self, search_pages: SearchPages):
        data = get_test_data("search")

        with allure.step(f"Search '{data['query']}' under ${data['max_price']}"):
            products = search_pages.search_results.get_products_under_price(
                query=data["query"], max_price=data["max_price"], limit=data["limit"]
            )

        with allure.step("Verify each item price is within per-item max"):
            for p in products:
                assert p.price <= data["max_price"], (
                    f"Price ${p.price} exceeds max ${data['max_price']} for {p.name!r}"
                )
