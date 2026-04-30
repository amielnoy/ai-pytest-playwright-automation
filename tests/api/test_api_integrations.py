import uuid

import allure
import pytest

from services.api.cart_service import CartService
from services.api.http_response_constants import HTTP_OK
from services.api.search_service import SearchService
from utils.price_parser import parse_price


MACBOOK = "MacBook"
MACBOOK_PRO = "MacBook Pro"
IPHONE = "iPhone"
IPOD = "iPod"
REFINE_SEARCH_MARKERS = (
    ('id="input-search"', "Search criteria input missing"),
    ('name="category_id"', "Category select missing"),
    ('id="button-search"', "Refine search button missing"),
)


def assert_ok(resp, expected_status: int = HTTP_OK) -> None:
    assert resp.status_code == expected_status, (
        f"Expected {expected_status}, got {resp.status_code}"
    )


def assert_cart_page_empty(cart_service: CartService) -> None:
    cart_resp = cart_service.get_cart()
    assert_ok(cart_resp)
    assert cart_service.is_empty(cart_resp.text), "Expected cart to stay empty"


def cart_add_payload(resp) -> dict:
    assert_ok(resp)
    payload = resp.json()
    assert isinstance(payload, dict), f"Expected JSON object, got {payload!r}"
    return payload


@allure.feature("API Integration Tests")
@allure.story("Search endpoint integration")
@pytest.mark.api
class TestSearchApiIntegration:

    @allure.title("Search returns OK with no product cards for an unknown query")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_unknown_query_returns_no_product_cards(
        self, search_service: SearchService
    ):
        query = f"unknown-product-{uuid.uuid4().hex[:8]}"

        with allure.step(f"GET search results for {query!r}"):
            resp = search_service.search(query)

        with allure.step("Assert response is OK and contains no product cards"):
            assert_ok(resp)
            assert not search_service.product_cards(resp.text), (
                f"Expected no product cards for unknown query {query!r}"
            )

    @allure.title("Search result product names are non-empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_product_names_are_non_empty(self, search_service: SearchService):
        with allure.step(f"GET search results for {IPOD!r}"):
            resp = search_service.search(IPOD)

        with allure.step("Assert every parsed product name has text"):
            assert_ok(resp)
            names = search_service.product_names(resp.text)
            assert names, f"No product names found for {IPOD} search"
            assert all(name.strip() for name in names), (
                f"Expected non-empty product names, got {names}"
            )

    @allure.title("Search product cards have matching IDs and names")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_product_cards_have_ids_and_names(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search results for {MACBOOK!r}"):
            resp = search_service.search(MACBOOK)

        with allure.step("Assert parsed product IDs and names align to cards"):
            assert_ok(resp)
            cards = search_service.product_cards(resp.text)
            names = search_service.product_names(resp.text)
            product_ids = search_service.product_ids(resp.text)
            assert cards, f"No product cards found for {MACBOOK} search"
            assert len(names) == len(cards), (
                f"Expected one name per card, got {len(names)} names and "
                f"{len(cards)} cards"
            )
            assert len(product_ids) >= len(cards), (
                f"Expected at least one product ID per card, got "
                f"{len(product_ids)} IDs and {len(cards)} cards"
            )

    @allure.title("Search supports multi-word product queries")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_multi_word_query_returns_expected_product(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search results for {MACBOOK_PRO!r}"):
            resp = search_service.search(MACBOOK_PRO)

        with allure.step("Assert exact multi-word product name is returned"):
            assert_ok(resp)
            names = search_service.product_names(resp.text)
            assert MACBOOK_PRO in names, (
                f"Expected {MACBOOK_PRO!r} in multi-word search results, got {names}"
            )

    @allure.title("Search page exposes refine-search controls")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_page_exposes_refine_search_controls(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search results page for {MACBOOK!r}"):
            resp = search_service.search(MACBOOK)

        with allure.step("Assert refine-search form controls exist in HTML"):
            assert_ok(resp)
            for marker, message in REFINE_SEARCH_MARKERS:
                assert marker in resp.text, message


@allure.feature("API Integration Tests")
@allure.story("Cart endpoint integration")
@pytest.mark.api
class TestCartApiIntegration:

    @allure.title("New API session starts with an empty cart")
    @allure.severity(allure.severity_level.NORMAL)
    def test_new_session_cart_starts_empty(self, cart_service: CartService):
        with allure.step("Fetch cart page before adding products"):
            cart_resp = cart_service.get_cart()

        with allure.step("Assert cart page is empty"):
            assert_ok(cart_resp)
            assert cart_service.is_empty(cart_resp.text), (
                "Expected a fresh API session to start with an empty cart"
            )

    @allure.title("Cart total is positive after adding quantity greater than one")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_total_positive_after_adding_quantity_two(
        self, search_service: SearchService, cart_service: CartService
    ):
        pid = search_service.first_product_id(MACBOOK)

        with allure.step(f"Add quantity=2 for product_id={pid}"):
            resp = cart_service.add_product(pid, quantity=2)

        with allure.step("Assert cart total is positive"):
            assert_ok(resp)
            cart_resp = cart_service.get_cart()
            total = cart_service.total(cart_resp.text)
            assert total is not None and total > 0, (
                f"Expected positive cart total after adding quantity=2, got {total}"
            )

    @allure.title("Cart keeps multiple products in the same API session")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_keeps_multiple_products_in_same_session(
        self, search_service: SearchService, cart_service: CartService
    ):
        macbook_pid = search_service.first_product_id(MACBOOK)
        iphone_pid = search_service.first_product_id(IPHONE)

        with allure.step("Add two different products to the same cart session"):
            macbook_resp = cart_service.add_product(macbook_pid)
            iphone_resp = cart_service.add_product(iphone_pid)

        with allure.step("Assert cart has a parseable positive row sum and total"):
            assert_ok(macbook_resp)
            assert_ok(iphone_resp)
            cart_resp = cart_service.get_cart()
            row_sum = cart_service.product_row_sum(cart_resp.text)
            total = cart_service.total(cart_resp.text)
            assert row_sum > 0, f"Expected positive cart row sum, got {row_sum}"
            assert total is not None and total > 0, (
                f"Expected positive cart total, got {total}"
            )

    @allure.title("Cart add response exposes success message and cart summary")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_add_response_contains_success_and_total(
        self, search_service: SearchService, cart_service: CartService
    ):
        pid = search_service.first_product_id(MACBOOK)

        with allure.step(f"POST product_id={pid} to cart"):
            resp = cart_service.add_product(pid)

        with allure.step("Assert cart/add JSON contains success and total fields"):
            payload = cart_add_payload(resp)
            assert "success" in payload, f"Missing success field in {payload!r}"
            assert "total" in payload, f"Missing total field in {payload!r}"
            assert MACBOOK in payload["success"], payload["success"]
            assert "item(s)" in payload["total"], payload["total"]

    @allure.title("Cart add response total matches the cart page total")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_add_response_total_matches_cart_page_total(
        self, search_service: SearchService, cart_service: CartService
    ):
        pid = search_service.first_product_id(MACBOOK)

        with allure.step(f"POST product_id={pid} with quantity=2"):
            resp = cart_service.add_product(pid, quantity=2)
            response_total = parse_price(cart_add_payload(resp).get("total", ""))

        with allure.step("Fetch cart page and compare grand total"):
            cart_resp = cart_service.get_cart()
            assert_ok(cart_resp)
            page_total = cart_service.total(cart_resp.text)
            assert response_total is not None, (
                f"Could not parse total from cart/add response: {resp.text}"
            )
            assert page_total == response_total, (
                f"Expected cart page total {page_total} to match response total "
                f"{response_total}"
            )


@allure.feature("API Integration Tests")
@allure.story("Cart endpoint negative scenarios")
@pytest.mark.api
class TestCartApiNegative:

    @allure.title("Cart add ignores missing or unknown product IDs")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("product_id", ["", "999999"])
    def test_cart_add_ignores_invalid_product_id(
        self, cart_service: CartService, product_id: str
    ):
        with allure.step(f"POST invalid product_id={product_id!r} to cart"):
            resp = cart_service.add_product(product_id)

        with allure.step("Assert request is handled and no product is added"):
            assert_ok(resp)
            assert resp.json() == [], (
                f"Expected empty response for invalid product_id={product_id!r}, "
                f"got {resp.text}"
            )
            assert_cart_page_empty(cart_service)

    @allure.title("Cart add with non-positive quantity does not add items")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("quantity", [0, -1])
    def test_cart_add_non_positive_quantity_does_not_add_items(
        self,
        search_service: SearchService,
        cart_service: CartService,
        quantity: int,
    ):
        pid = search_service.first_product_id(MACBOOK)

        with allure.step(f"POST product_id={pid} with quantity={quantity}"):
            resp = cart_service.add_product(pid, quantity=quantity)

        with allure.step("Assert cart remains empty"):
            assert_ok(resp)
            assert "0 item(s)" in resp.text, (
                f"Expected zero-item cart summary for quantity={quantity}, got {resp.text}"
            )
            assert_cart_page_empty(cart_service)
