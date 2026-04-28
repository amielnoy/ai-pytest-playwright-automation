import uuid

import allure
import pytest

from services.api.account_service import AccountService
from services.api.cart_service import CartService
from services.api.http_response_constants import HTTP_OK
from services.api.public_service import EndpointCase, PublicService
from services.api.search_service import SearchCase, SearchService
from tests.conftest import PUBLIC_ENDPOINT_MAP, SEARCH_QUERY_MAP
from utils.data_loader import get_test_data


@allure.feature("Contract Tests")
@allure.story("Public endpoint map")
@pytest.mark.contract
class TestPublicEndpointContract:

    @allure.title("Mapped public endpoints return OK and expected page markers")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case",
        PUBLIC_ENDPOINT_MAP.values(),
        ids=PUBLIC_ENDPOINT_MAP.keys(),
    )
    def test_public_endpoint_map_returns_expected_marker(
        self, public_service: PublicService, api_base_url: str, case: EndpointCase
    ):
        url = f"{api_base_url}{case.path}"

        with allure.step(f"GET {url}"):
            resp = public_service.get_path(case.path)

        with allure.step("Assert response status and HTML marker"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK} for {url}, got {resp.status_code}"
            )
            assert case.required_text in resp.text, (
                f"Expected marker {case.required_text!r} in {url}"
            )


@allure.feature("Contract Tests")
@allure.story("Search response contract")
@pytest.mark.contract
class TestSearchContract:

    @allure.title("Mapped search queries return expected product cards")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case",
        SEARCH_QUERY_MAP.values(),
        ids=SEARCH_QUERY_MAP.keys(),
    )
    def test_search_query_map_returns_expected_products(
        self, search_service: SearchService, case: SearchCase
    ):
        with allure.step(f"GET search results for {case.query!r}"):
            resp = search_service.search(case.query)

        with allure.step("Assert response contains enough product cards"):
            assert resp.status_code == HTTP_OK
            cards = search_service.product_cards(resp.text)
            assert len(cards) >= case.min_cards, (
                f"Expected at least {case.min_cards} product cards for "
                f"{case.query!r}, got {len(cards)}"
            )

        with allure.step("Assert expected product names are present"):
            missing_names = [
                name for name in case.expected_names if name not in resp.text
            ]
            assert not missing_names, (
                f"Missing expected product names for {case.query!r}: {missing_names}"
            )

    @allure.title("Search results contain product names and prices")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_response_has_names_and_prices(
        self, search_service: SearchService
    ):
        resp = search_service.search("MacBook")
        html = resp.text

        with allure.step("Assert at least one product name is present"):
            names = search_service.product_names(html)
            assert names, "No product names found in search response"

        with allure.step("Assert at least one parseable price is present"):
            prices = search_service.prices(html)
            assert prices, "No parseable prices found in search response"

    @allure.title("Search for non-existent product returns no product cards")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_no_results_contract(self, search_service: SearchService):
        resp = search_service.search(f"xyznonexistent{uuid.uuid4().hex[:6]}")
        assert resp.status_code == HTTP_OK
        assert not search_service.product_cards(resp.text), (
            "Expected no product cards for a nonsense query"
        )

    @allure.title("Search result product IDs are parseable integers")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_product_ids_are_integers(
        self, search_service: SearchService
    ):
        resp = search_service.search("Apple")
        pids = search_service.product_ids(resp.text)
        assert pids, "No product IDs found via cart.add() pattern"
        for pid in pids:
            assert pid.isdigit(), f"Product ID '{pid}' is not a digit string"


@allure.feature("Contract Tests")
@allure.story("Registration page structure")
@pytest.mark.contract
class TestRegistrationPageContract:

    @allure.title("Registration page returns OK and contains all required fields")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_page_has_required_fields(
        self, account_service: AccountService
    ):
        resp = account_service.get_register_page()

        with allure.step("Assert HTTP OK"):
            assert resp.status_code == HTTP_OK

        required_fields = [
            "input-firstname",
            "input-lastname",
            "input-email",
            "input-telephone",
            "input-password",
            "input-confirm",
        ]
        with allure.step("Assert all required input IDs are present in the HTML"):
            missing = [field for field in required_fields if field not in resp.text]
            assert not missing, f"Registration page missing fields: {missing}"

    @allure.title("Registration page contains privacy policy checkbox")
    @allure.severity(allure.severity_level.NORMAL)
    def test_registration_page_has_privacy_checkbox(
        self, account_service: AccountService
    ):
        resp = account_service.get_register_page()
        assert 'name="agree"' in resp.text, (
            "Privacy policy checkbox not found on registration page"
        )


@allure.feature("Contract Tests")
@allure.story("Price data integrity")
@pytest.mark.contract
class TestPriceContract:

    @allure.title("All prices in search results are positive numbers")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_search_prices_are_positive(
        self, search_service: SearchService
    ):
        resp = search_service.search("MacBook")
        prices = search_service.prices(resp.text)

        with allure.step(f"Assert all {len(prices)} prices are > 0"):
            non_positive = [price for price in prices if price <= 0]
            assert not non_positive, f"Non-positive prices found: {non_positive}"

    @allure.title("Cart total matches sum of individual item prices")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_total_matches_item_sum(
        self, search_service: SearchService, cart_service: CartService
    ):
        data = get_test_data("search")
        pid = search_service.first_product_id(data["query"])

        cart_service.add_product(pid)

        with allure.step("Fetch cart page and parse individual row prices and total"):
            cart_resp = cart_service.get_cart()
            html = cart_resp.text

        row_sum = cart_service.product_row_sum(html)
        grand_total = cart_service.total(html)
        assert grand_total is not None and grand_total > 0

        with allure.step(
            f"Assert row sum ${row_sum:.2f} approximately equals grand total ${grand_total:.2f}"
        ):
            assert abs(row_sum - grand_total) < 1.0, (
                f"Row sum ${row_sum:.2f} diverges from grand total ${grand_total:.2f}"
            )
