import json
from dataclasses import asdict

import allure
import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage


@allure.feature("Search")
@allure.story("iPod product storage")
@pytest.mark.search
class TestIpoDStorage:

    @allure.title("ipodStorage")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ipod_storage(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
    ):
        with allure.step("Search for all iPod products"):
            home_page.open()
            home_page.search("iPod")
            search_results_page.choose_list_view()

        with allure.step("Store iPod name, picture URL, description, and price"):
            products = search_results_page.stored_product_information()
            product_records = [asdict(product) for product in products]
            allure.attach(
                json.dumps(product_records, indent=2),
                name="Stored iPod products",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Verify iPod was removed from stored product names"):
            assert products, "Expected iPod search results"
            for product in products:
                assert "ipod" not in product.name.casefold(), (
                    f"Stored product name still contains iPod: {product.name!r}"
                )

        with allure.step("Find and print maximum iPod price information"):
            max_product = max(products, key=lambda product: product.price)
            max_info = json.dumps(asdict(max_product), indent=2)
            print(f"Maximum iPod price product:\n{max_info}")
            allure.attach(
                max_info,
                name="Maximum iPod price product",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Find and print minimum iPod price information"):
            min_product = min(products, key=lambda product: product.price)
            min_info = json.dumps(asdict(min_product), indent=2)
            print(f"Minimum iPod price product:\n{min_info}")
            allure.attach(
                min_info,
                name="Minimum iPod price product",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Verify maximum and minimum prices are valid"):
            prices = [product.price for product in products]
            assert max_product.price == max(prices)
            assert min_product.price == min(prices)
