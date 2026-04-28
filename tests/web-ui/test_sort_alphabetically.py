import allure
import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage


@allure.feature("Search")
@allure.story("Sort search results")
@pytest.mark.search
class TestSortAlphabetically:

    @allure.title("Test sort alphabetically ascending")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sort_alphabetically_ascending(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
    ):
        with allure.step("Access TutorialsNinja demo store"):
            home_page.open()

        with allure.step("Verify the currency drop-down exists"):
            assert home_page.has_currency_dropdown(), "Currency drop-down is not visible"

        with allure.step("Search for iPod"):
            home_page.search("iPod")

        with allure.step("Choose list view"):
            search_results_page.choose_list_view()

        with allure.step("Sort by Name (A - Z)"):
            search_results_page.sort_by_name_ascending()

        with allure.step("Verify the results are sorted alphabetically"):
            names = search_results_page.product_names()
            allure.attach(
                "\n".join(names),
                name="Sorted product names",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert names, "Expected search results for iPod"
            assert search_results_page.are_product_names_sorted_ascending(), (
                f"Expected alphabetical order, got: {names}"
            )
