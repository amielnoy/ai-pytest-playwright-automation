import allure
import pytest

from tests.page_records import SearchPages
from utils.data_loader import get_test_data


@allure.feature("Search")
@allure.story("Search with price filter")
@pytest.mark.search
class TestSearchUnderPrice:

    @allure.title("searchItemsByNameUnderPrice returns items at or below max_price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_items_under_price(self, search_pages: SearchPages):
        data = get_test_data("search")
        query = data["query"]
        max_price = data["max_price"]
        limit = data["limit"]

        with allure.step(f"Search '{query}' and filter items under ${max_price}"):
            names = search_pages.search_results.search_items_by_name_under_price(
                query=query, max_price=max_price, limit=limit
            )

        allure.attach(
            "\n".join(names) if names else "No items found",
            name="Filtered products",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Verify result count does not exceed the limit"):
            assert len(names) <= limit, (
                f"Expected at most {limit} results, got {len(names)}"
            )

        with allure.step("Verify all returned names are non-empty strings"):
            for name in names:
                assert isinstance(name, str) and name, f"Invalid product name: {name!r}"

    @allure.title("Search for non-existent product returns empty list")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_no_results(self, search_pages: SearchPages):
        with allure.step("Search with a query and price cap that yields no results"):
            names = search_pages.search_results.search_items_by_name_under_price(
                query="xyznonexistentproduct999", max_price=0.01, limit=5
            )

        with allure.step("Verify empty list returned"):
            assert names == [], f"Expected [], got {names}"

    @allure.title("Items with price above max_price are excluded")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_price_filter_excludes_expensive(self, search_pages: SearchPages):
        with allure.step("Search 'laptop' with max_price = $1 (should return nothing)"):
            names = search_pages.search_results.search_items_by_name_under_price(
                query="laptop", max_price=1.0, limit=5
            )

        with allure.step("Verify no items returned for unreachable price cap"):
            assert names == [], f"Expected no items under $1, got {names}"

    @allure.title("Result list is capped at limit even when more matches exist")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_respects_limit(self, search_pages: SearchPages):
        with allure.step("Search 'iPhone' with high max_price and limit=2"):
            names = search_pages.search_results.search_items_by_name_under_price(
                query="iPhone", max_price=9999.0, limit=2
            )

        with allure.step("Verify at most 2 items returned"):
            assert len(names) <= 2, f"Limit=2 violated, got {len(names)} items"
