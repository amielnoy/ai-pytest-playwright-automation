import allure
import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage


@allure.feature("Search")
@allure.story("Sort search results")
@pytest.mark.search
class TestSortByPrice:

    @allure.title("Test sort by price ascending")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sort_by_price_ascending(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
    ):
        with allure.step("Access eBay"):
            home_page.open()

        with allure.step("Verify the eBay header is visible"):
            assert home_page.has_currency_dropdown(), "eBay site header is not visible"

        with allure.step("Search for iPod"):
            home_page.search("iPod")

        with allure.step("Sort by price (lowest first)"):
            search_results_page.sort_by_name_ascending()

        with allure.step("Verify the results are sorted by price ascending"):
            names = search_results_page.product_names()
            allure.attach(
                "\n".join(names),
                name="Product names after price sort",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert names, "Expected search results for iPod"
            assert search_results_page.are_product_names_sorted_ascending(), (
                "Expected price-ascending order"
            )
