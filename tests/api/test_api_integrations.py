import uuid

import allure
import pytest

from services.api.cart_service import CartService
from services.api.http_response_constants import HTTP_OK
from services.api.search_service import SearchService


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
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            assert not search_service.product_cards(resp.text), (
                f"Expected no product cards for unknown query {query!r}"
            )

    @allure.title("Search result product names are non-empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_product_names_are_non_empty(self, search_service: SearchService):
        with allure.step("GET search results for 'iPod'"):
            resp = search_service.search("iPod")

        with allure.step("Assert every parsed product name has text"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            names = search_service.product_names(resp.text)
            assert names, "No product names found for iPod search"
            assert all(name.strip() for name in names), (
                f"Expected non-empty product names, got {names}"
            )

    @allure.title("Search product cards have matching IDs and names")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_product_cards_have_ids_and_names(
        self, search_service: SearchService
    ):
        with allure.step("GET search results for 'MacBook'"):
            resp = search_service.search("MacBook")

        with allure.step("Assert parsed product IDs and names align to cards"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            cards = search_service.product_cards(resp.text)
            names = search_service.product_names(resp.text)
            product_ids = search_service.product_ids(resp.text)
            assert cards, "No product cards found for MacBook search"
            assert len(names) == len(cards), (
                f"Expected one name per card, got {len(names)} names and "
                f"{len(cards)} cards"
            )
            assert len(product_ids) >= len(cards), (
                f"Expected at least one product ID per card, got "
                f"{len(product_ids)} IDs and {len(cards)} cards"
            )


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
            assert cart_resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {cart_resp.status_code}"
            )
            assert cart_service.is_empty(cart_resp.text), (
                "Expected a fresh API session to start with an empty cart"
            )

    @allure.title("Cart total is positive after adding quantity greater than one")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_total_positive_after_adding_quantity_two(
        self, search_service: SearchService, cart_service: CartService
    ):
        pid = search_service.first_product_id("MacBook")

        with allure.step(f"Add quantity=2 for product_id={pid}"):
            resp = cart_service.add_product(pid, quantity=2)

        with allure.step("Assert cart total is positive"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
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
        macbook_pid = search_service.first_product_id("MacBook")
        iphone_pid = search_service.first_product_id("iPhone")

        with allure.step("Add two different products to the same cart session"):
            macbook_resp = cart_service.add_product(macbook_pid)
            iphone_resp = cart_service.add_product(iphone_pid)

        with allure.step("Assert cart has a parseable positive row sum and total"):
            assert macbook_resp.status_code == HTTP_OK
            assert iphone_resp.status_code == HTTP_OK
            cart_resp = cart_service.get_cart()
            row_sum = cart_service.product_row_sum(cart_resp.text)
            total = cart_service.total(cart_resp.text)
            assert row_sum > 0, f"Expected positive cart row sum, got {row_sum}"
            assert total is not None and total > 0, (
                f"Expected positive cart total, got {total}"
            )
