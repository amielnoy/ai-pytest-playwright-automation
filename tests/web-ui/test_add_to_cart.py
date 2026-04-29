import allure
import pytest

from tests.page_records import SearchPages
from utils.data_loader import get_test_data


@allure.feature("Shopping")
@allure.story("eBay buyable items")
@pytest.mark.cart
class TestAddItemsToCart:

    @allure.title("Search returns items with prices")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_returns_priced_items(self, search_pages: SearchPages):
        data = get_test_data("search")

        with allure.step(f"Find products matching '{data['query']}' under ${data['max_price']}"):
            products = search_pages.search_results.get_products_under_price(
                query=data["query"], max_price=data["max_price"], limit=data["limit"]
            )

        allure.attach(
            "\n".join(f"{p.name} — ${p.price}" for p in products),
            name="Products found",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Verify products were found with positive prices and names"):
            assert products, f"No products found under ${data['max_price']}"
            for p in products:
                assert p.price > 0, f"Expected positive price, got {p.price}"
                assert p.name, "Expected non-empty product name"

    @allure.title("No items returned when price cap is below all listings")
    @allure.severity(allure.severity_level.NORMAL)
    def test_no_items_when_price_cap_unreachable(self, search_pages: SearchPages):
        with allure.step("Search 'laptop' with price cap of $0.01 to get no matches"):
            products = search_pages.search_results.get_products_under_price(
                query="laptop", max_price=0.01, limit=5
            )

        with allure.step("Verify product list is empty"):
            assert products == [], f"Expected no products, got {products}"
