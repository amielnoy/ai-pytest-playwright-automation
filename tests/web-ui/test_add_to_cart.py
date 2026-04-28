import allure
import pytest

from tests.page_records import CartFlowPages
from utils.data_loader import get_test_data


@allure.feature("Cart")
@allure.story("addItemsToCart")
@pytest.mark.cart
class TestAddItemsToCart:

    @allure.title("Add items under max_price to cart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_items_to_cart(self, cart_flow_pages: CartFlowPages):
        search_data = get_test_data("search")
        query = search_data["query"]
        max_price = search_data["max_price"]
        limit = search_data["limit"]

        with allure.step(f"Find products matching '{query}' under ${max_price}"):
            products = cart_flow_pages.search_results.get_products_under_price(
                query=query, max_price=max_price, limit=limit
            )

        allure.attach(
            "\n".join(f"{p.name} — ${p.price}" for p in products),
            name="Products to add",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert products, (
            f"No products found for query='{query}' under ${max_price}. "
            "Cannot add to cart."
        )

        with allure.step(f"Add {len(products)} product(s) to cart"):
            added = cart_flow_pages.search_results.add_items_to_cart(products)

        with allure.step("Verify all selected products were added"):
            assert len(added) == len(products), (
                f"Expected {len(products)} items added, got {len(added)}"
            )

        with allure.step("Open cart and verify item count"):
            cart_flow_pages.cart.open()
            assert not cart_flow_pages.cart.is_empty(), "Cart is empty after adding items"

    @allure.title("No items added when no products match the price filter")
    @allure.severity(allure.severity_level.NORMAL)
    def test_no_items_added_when_nothing_matches(self, cart_flow_pages: CartFlowPages):
        with allure.step("Search with price cap of $0.01 to get no matches"):
            products = cart_flow_pages.search_results.get_products_under_price(
                query="MacBook", max_price=0.01, limit=5
            )

        with allure.step("Verify product list is empty — nothing to add"):
            assert products == [], f"Expected no products, got {products}"
