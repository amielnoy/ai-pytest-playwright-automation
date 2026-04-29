import allure
import pytest

from services.api.ebay_search_service import EbaySearchService
from services.api.http_response_constants import HTTP_OK
from services.rest_client import RestClient


@allure.feature("eBay API Integration Tests")
@allure.story("Multi-category search")
@pytest.mark.api
class TestEbayMultiCategorySearch:

    @pytest.mark.parametrize("query,min_items", [
        ("iPhone", 5), ("laptop", 5), ("book", 5),
    ])
    @allure.title("eBay search returns minimum item count for common categories")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_returns_minimum_items(
        self, ebay_search_service: EbaySearchService, query: str, min_items: int
    ):
        with allure.step(f"GET search results for {query!r}"):
            resp = ebay_search_service.search(query)

        with allure.step(f"Assert at least {min_items} item IDs returned"):
            assert resp.status_code == HTTP_OK
            ids = ebay_search_service.item_ids(resp.text)
            assert len(ids) >= min_items, (
                f"Expected >={min_items} items for {query!r}, got {len(ids)}"
            )

    @allure.title("eBay search prices are within a reasonable range for electronics")
    @allure.severity(allure.severity_level.NORMAL)
    def test_electronics_prices_in_reasonable_range(self, ebay_search_service: EbaySearchService):
        with allure.step("GET search results for 'iPhone'"):
            resp = ebay_search_service.search("iPhone")

        with allure.step("Assert prices are all between 0 and 10000"):
            assert resp.status_code == HTTP_OK
            prices = ebay_search_service.item_prices(resp.text)
            assert prices
            assert all(0 < p < 10000 for p in prices), f"Unexpected prices: {prices}"

    @allure.title("eBay item ID count matches or exceeds title count")
    @allure.severity(allure.severity_level.NORMAL)
    def test_item_id_count_not_less_than_title_count(self, ebay_search_service: EbaySearchService):
        with allure.step("GET search results for 'laptop'"):
            resp = ebay_search_service.search("laptop")

        with allure.step("Assert ID count >= title count"):
            assert resp.status_code == HTTP_OK
            ids = ebay_search_service.item_ids(resp.text)
            titles = ebay_search_service.item_titles(resp.text)
            assert len(ids) >= len(titles), (
                f"IDs ({len(ids)}) < titles ({len(titles)})"
            )


@allure.feature("eBay API Integration Tests")
@allure.story("Search session isolation")
@pytest.mark.api
class TestEbaySearchSessionIsolation:

    @allure.title("Two eBay search sessions are independent")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sessions_are_independent(self):
        headers = {"User-Agent": "Mozilla/5.0 (compatible; test/1.0)"}
        session_a = RestClient(headers=headers)
        session_b = RestClient(headers=headers)
        svc_a = EbaySearchService(session_a)
        svc_b = EbaySearchService(session_b)

        with allure.step("Search 'iPhone' with session A and 'laptop' with session B"):
            resp_a = svc_a.search("iPhone")
            resp_b = svc_b.search("laptop")

        with allure.step("Assert both responses are OK"):
            assert resp_a.status_code == HTTP_OK
            assert resp_b.status_code == HTTP_OK

        with allure.step("Assert iPhone and laptop searches return disjoint item IDs"):
            ids_a = set(svc_a.item_ids(resp_a.text))
            ids_b = set(svc_b.item_ids(resp_b.text))
            assert ids_a.isdisjoint(ids_b), (
                "iPhone and laptop searches returned overlapping item IDs"
            )

        session_a.close()
        session_b.close()
