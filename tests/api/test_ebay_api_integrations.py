import uuid

import allure
import pytest

from services.api.ebay_search_service import EbaySearchService
from services.api.http_response_constants import HTTP_OK


@allure.feature("eBay API Integration Tests")
@allure.story("Search endpoint integration")
@pytest.mark.api
class TestEbaySearchApiIntegration:

    @allure.title("eBay search returns OK for a known brand query")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_returns_ok_for_known_brand(
        self, ebay_search_service: EbaySearchService
    ):
        with allure.step("GET eBay search results for 'iPhone'"):
            resp = ebay_search_service.search("iPhone")

        with allure.step("Assert response is OK and contains item cards"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            assert ebay_search_service.item_cards(resp.text), (
                "Expected item cards for 'iPhone' search"
            )

    @allure.title("eBay search result item titles are non-empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_item_titles_are_non_empty(
        self, ebay_search_service: EbaySearchService
    ):
        with allure.step("GET eBay search results for 'iPhone'"):
            resp = ebay_search_service.search("iPhone")

        with allure.step("Assert every parsed item title has text"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            titles = ebay_search_service.item_titles(resp.text)
            assert titles, "No item titles found for iPhone search"
            assert all(title.strip() for title in titles), (
                f"Expected non-empty item titles, got {titles}"
            )

    @allure.title("eBay search item cards have matching IDs and titles")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_item_cards_have_ids_and_titles(
        self, ebay_search_service: EbaySearchService
    ):
        with allure.step("GET eBay search results for 'laptop'"):
            resp = ebay_search_service.search("laptop")

        with allure.step("Assert parsed item IDs and titles align to cards"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            cards = ebay_search_service.item_cards(resp.text)
            titles = ebay_search_service.item_titles(resp.text)
            item_ids = ebay_search_service.item_ids(resp.text)
            assert cards, "No item cards found for laptop search"
            assert titles, "No item titles found for laptop search"
            assert item_ids, "No item IDs found for laptop search"
            assert len(item_ids) >= len(titles), (
                f"Expected at least one ID per title, got "
                f"{len(item_ids)} IDs and {len(titles)} titles"
            )


@allure.feature("eBay API Integration Tests")
@allure.story("Search endpoint negative scenarios")
@pytest.mark.api
class TestEbaySearchApiNegative:

    @allure.title("eBay search with empty query returns OK")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_empty_query_returns_ok(
        self, ebay_search_service: EbaySearchService
    ):
        with allure.step("GET eBay search with empty query"):
            resp = ebay_search_service.search("")

        with allure.step("Assert response is OK"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )

    @allure.title("eBay search item prices are positive when results exist")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_item_prices_are_positive(
        self, ebay_search_service: EbaySearchService
    ):
        with allure.step("GET eBay search results for 'book'"):
            resp = ebay_search_service.search("book")

        with allure.step("Assert all parsed prices are positive"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            prices = ebay_search_service.item_prices(resp.text)
            assert prices, "Expected parseable prices from book search"
            assert all(p > 0 for p in prices), (
                f"Expected all prices to be positive, got {prices}"
            )

    @allure.title("eBay search with unknown query returns OK")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", [
        f"xyzzy-no-results-{uuid.uuid4().hex[:8]}",
        "!@#$%^&*()",
    ])
    def test_search_edge_case_queries_return_ok(
        self, ebay_search_service: EbaySearchService, query: str
    ):
        with allure.step(f"GET eBay search for edge-case query {query!r}"):
            resp = ebay_search_service.search(query)

        with allure.step("Assert request is handled gracefully"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK} for query {query!r}, got {resp.status_code}"
            )
