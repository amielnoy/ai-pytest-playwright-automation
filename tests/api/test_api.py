import allure
import pytest

from services.api.cart_service import CartService
from services.api.http_response_constants import HTTP_OK
from services.api.search_service import SearchService
from utils.api_client import build_session


@allure.feature("API Tests")
@allure.story("Search endpoint")
@pytest.mark.api
class TestSearchApi:

    @allure.title("Search returns 200 and non-empty HTML for a known query")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_returns_200(self, search_service: SearchService):
        with allure.step("GET search results for 'MacBook'"):
            resp = search_service.search("MacBook")

        with allure.step("Assert HTTP OK"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )

        with allure.step("Assert response contains product cards"):
            assert search_service.product_cards(resp.text), (
                "Search response contains no product cards"
            )

    @allure.title("Search returns expected products for known queries")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        ("query", "expected_product"),
        [
            ("MacBook", "MacBook"),
            ("iPhone", "iPhone"),
        ],
    )
    def test_search_returns_expected_product_names(
        self, search_service: SearchService, query: str, expected_product: str
    ):
        with allure.step(f"GET search results for {query!r}"):
            resp = search_service.search(query)

        with allure.step("Assert HTTP OK and expected product name"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            names = search_service.product_names(resp.text)
            assert expected_product in names, (
                f"Expected {expected_product!r} in search results, got {names}"
            )

    @allure.title("Search returns parseable positive prices for known queries")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["MacBook", "iPhone"])
    def test_search_returns_positive_prices(
        self, search_service: SearchService, query: str
    ):
        with allure.step(f"GET search results for {query!r}"):
            resp = search_service.search(query)

        with allure.step("Assert all parsed prices are positive"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            prices = search_service.prices(resp.text)
            assert prices, f"No parseable prices found for query {query!r}"
            assert all(price > 0 for price in prices), (
                f"Expected positive prices for {query!r}, got {prices}"
            )

    @allure.title("Search returns numeric product IDs for known queries")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["MacBook", "iPhone"])
    def test_search_returns_numeric_product_ids(
        self, search_service: SearchService, query: str
    ):
        with allure.step(f"GET search results for {query!r}"):
            resp = search_service.search(query)

        with allure.step("Assert all parsed product IDs are numeric"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            product_ids = search_service.product_ids(resp.text)
            assert product_ids, f"No product IDs found for query {query!r}"
            assert all(product_id.isdigit() for product_id in product_ids), (
                f"Expected numeric product IDs for {query!r}, got {product_ids}"
            )


@allure.feature("API Tests")
@allure.story("Cart endpoint")
@pytest.mark.api
class TestCartApi:

    @allure.title("POST to cart/add returns OK and issues an OCSESSID cookie")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_add_returns_ok_and_sets_session(
        self,
        session,
        search_service: SearchService,
        cart_service: CartService,
    ):
        pid = search_service.first_product_id("MacBook")

        with allure.step(f"POST product_id={pid} to cart"):
            resp = cart_service.add_product(pid)

        with allure.step("Assert HTTP OK"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )

        with allure.step("Assert OCSESSID cookie is present"):
            assert "OCSESSID" in session.cookies, "No OCSESSID cookie after cart add"

    @allure.title("Cart page reflects the product added via API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_page_reflects_api_add(
        self, search_service: SearchService, cart_service: CartService
    ):
        pid = search_service.first_product_id("MacBook")

        with allure.step(f"Add product {pid} via API"):
            cart_service.add_product(pid)

        with allure.step("Fetch cart page with the same session"):
            cart_resp = cart_service.get_cart()

        with allure.step("Assert cart is not empty"):
            assert not cart_service.is_empty(cart_resp.text), (
                "Cart page shows empty after API add"
            )

        with allure.step("Assert cart page contains a parseable total"):
            total = cart_service.total(cart_resp.text)
            assert total is not None and total > 0, (
                "Cart total could not be parsed or is zero"
            )

    @allure.title("Cart accepts products found from known search queries")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["MacBook", "iPhone"])
    def test_cart_accepts_products_from_search_results(
        self, search_service: SearchService, cart_service: CartService, query: str
    ):
        with allure.step(f"Find first product ID for {query!r}"):
            pid = search_service.first_product_id(query)

        with allure.step(f"POST product_id={pid} to cart"):
            resp = cart_service.add_product(pid)

        with allure.step("Assert cart add succeeds and cart page is not empty"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            cart_resp = cart_service.get_cart()
            assert not cart_service.is_empty(cart_resp.text), (
                f"Cart is empty after adding product {pid} from query {query!r}"
            )

    @allure.title("Two concurrent sessions have independent carts")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sessions_are_isolated(self, api_base_url: str):
        session_a = build_session()
        session_b = build_session()
        search_a = SearchService(session_a, api_base_url)
        cart_a = CartService(session_a, api_base_url)
        cart_b_service = CartService(session_b, api_base_url)

        pid = search_a.first_product_id("MacBook")

        with allure.step("Add product to session A only"):
            cart_a.add_product(pid)

        with allure.step("Check session B cart is still empty"):
            session_b.get(api_base_url)
            cart_b = cart_b_service.get_cart()
            assert cart_b_service.is_empty(cart_b.text), (
                "Session B cart is not empty: sessions are leaking state"
            )

        with allure.step("Assert session A and B have different OCSESSID values"):
            sid_a = session_a.cookies.get("OCSESSID")
            sid_b = session_b.cookies.get("OCSESSID")
            assert sid_a and sid_b, "One or both sessions have no OCSESSID"
            assert sid_a != sid_b, (
                f"Sessions share the same OCSESSID ({sid_a}): no isolation"
            )
