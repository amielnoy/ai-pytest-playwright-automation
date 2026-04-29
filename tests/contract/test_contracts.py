import uuid

import allure
import pytest

from services.api.ebay_search_service import EbaySearchService
from services.api.http_response_constants import HTTP_OK
from services.api.public_service import EndpointCase
from services.api.search_service import SearchCase
from tests.conftest import PUBLIC_ENDPOINT_MAP, SEARCH_QUERY_MAP


@allure.feature("Contract Tests")
@allure.story("eBay public endpoint map")
@pytest.mark.contract
class TestEbayPublicEndpointContract:

    @allure.title("Mapped public endpoints return OK and expected page markers")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case",
        PUBLIC_ENDPOINT_MAP.values(),
        ids=PUBLIC_ENDPOINT_MAP.keys(),
    )
    def test_public_endpoint_returns_ok_and_marker(
        self, ebay_search_service: EbaySearchService, case: EndpointCase
    ):
        url = f"https://www.ebay.com{case.path}"

        with allure.step(f"GET {url}"):
            resp = ebay_search_service.get(url)

        with allure.step("Assert response status and HTML marker"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK} for {url}, got {resp.status_code}"
            )
            assert case.required_text in resp.text, (
                f"Expected marker {case.required_text!r} in {url}"
            )


@allure.feature("Contract Tests")
@allure.story("eBay search response contract")
@pytest.mark.contract
class TestEbaySearchContract:

    @allure.title("Mapped search queries return expected item cards")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case",
        SEARCH_QUERY_MAP.values(),
        ids=SEARCH_QUERY_MAP.keys(),
    )
    def test_search_query_returns_expected_items(
        self, ebay_search_service: EbaySearchService, case: SearchCase
    ):
        with allure.step(f"GET search results for {case.query!r}"):
            resp = ebay_search_service.search(case.query)

        with allure.step("Assert response contains enough item cards"):
            assert resp.status_code == HTTP_OK
            cards = ebay_search_service.item_cards(resp.text)
            assert len(cards) >= case.min_cards, (
                f"Expected at least {case.min_cards} item cards for "
                f"{case.query!r}, got {len(cards)}"
            )

    @allure.title("Search response has titles and prices")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_response_has_titles_and_prices(self, ebay_search_service: EbaySearchService):
        with allure.step("GET search results for 'laptop'"):
            resp = ebay_search_service.search("laptop")

        with allure.step("Assert HTTP OK, titles and prices present"):
            assert resp.status_code == HTTP_OK
            assert ebay_search_service.item_titles(resp.text)
            assert ebay_search_service.item_prices(resp.text)

    @allure.title("Search returns no item IDs for nonsense query")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_no_results_for_nonsense_query(self, ebay_search_service: EbaySearchService):
        query = f"xyznonexistent{uuid.uuid4().hex[:6]}"

        with allure.step(f"GET search results for {query!r}"):
            resp = ebay_search_service.search(query)

        with allure.step("Assert no item IDs in response"):
            assert resp.status_code == HTTP_OK
            ids = ebay_search_service.item_ids(resp.text)
            assert not ids, f"Expected no item IDs for nonsense query, got {ids}"

    @allure.title("Search item IDs are numeric")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_item_ids_are_numeric(self, ebay_search_service: EbaySearchService):
        with allure.step("GET search results for 'iPhone'"):
            resp = ebay_search_service.search("iPhone")

        with allure.step("Assert all item IDs are digit strings"):
            assert resp.status_code == HTTP_OK
            ids = ebay_search_service.item_ids(resp.text)
            assert ids
            for id_ in ids:
                assert id_.isdigit(), f"Non-numeric item ID: {id_!r}"


@allure.feature("Contract Tests")
@allure.story("eBay price data integrity")
@pytest.mark.contract
class TestEbayPriceContract:

    @allure.title("All prices in search results are positive numbers")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_search_prices_are_positive(self, ebay_search_service: EbaySearchService):
        with allure.step("GET search results for 'laptop'"):
            resp = ebay_search_service.search("laptop")

        with allure.step("Assert all parsed prices are > 0"):
            assert resp.status_code == HTTP_OK
            prices = ebay_search_service.item_prices(resp.text)
            non_pos = [p for p in prices if p <= 0]
            assert not non_pos, f"Non-positive prices: {non_pos}"
