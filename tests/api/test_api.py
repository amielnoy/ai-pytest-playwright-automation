import allure
import pytest

from services.api.ebay_search_service import EbaySearchService
from services.api.http_response_constants import HTTP_OK


@allure.feature("API Tests")
@allure.story("eBay search endpoint")
@pytest.mark.api
class TestEbaySearchApi:

    @allure.title("eBay search returns 200 and non-empty response for a known query")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_returns_200(self, ebay_search_service: EbaySearchService):
        with allure.step("GET search results for 'laptop'"):
            resp = ebay_search_service.search("laptop")

        with allure.step("Assert HTTP OK and item cards present"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            assert ebay_search_service.item_cards(resp.text), "No item cards in response"

    @allure.title("eBay search returns item IDs for known queries")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("query", ["iPhone", "laptop"])
    def test_search_returns_item_ids(self, ebay_search_service: EbaySearchService, query: str):
        with allure.step(f"GET search results for {query!r}"):
            resp = ebay_search_service.search(query)

        with allure.step("Assert HTTP OK and numeric item IDs present"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            ids = ebay_search_service.item_ids(resp.text)
            assert ids, f"No item IDs found for {query!r}"
            assert all(id_.isdigit() for id_ in ids), f"Non-numeric item IDs: {ids}"

    @allure.title("eBay search returns parseable positive prices for known queries")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["iPhone", "book"])
    def test_search_returns_positive_prices(self, ebay_search_service: EbaySearchService, query: str):
        with allure.step(f"GET search results for {query!r}"):
            resp = ebay_search_service.search(query)

        with allure.step("Assert all parsed prices are positive"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            prices = ebay_search_service.item_prices(resp.text)
            assert prices, f"No parseable prices for {query!r}"
            assert all(p > 0 for p in prices)

    @allure.title("eBay search returns non-empty item titles for known queries")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["iPhone", "laptop"])
    def test_search_returns_non_empty_titles(self, ebay_search_service: EbaySearchService, query: str):
        with allure.step(f"GET search results for {query!r}"):
            resp = ebay_search_service.search(query)

        with allure.step("Assert non-empty titles present"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            titles = ebay_search_service.item_titles(resp.text)
            assert titles, f"No titles for {query!r}"
            assert all(t.strip() for t in titles)
