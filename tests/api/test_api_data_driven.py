"""
Data-driven API tests — two parametrization strategies side-by-side.

Inline params  → @pytest.mark.parametrize with values defined in this file.
JSON params    → cases loaded from data/api_test_cases.json so QA can extend
                 the matrix without touching Python.

Both strategies exercise the same assertions; the difference is only in where
the test inputs live.
"""

import allure
import pytest

from services.api.cart_service import CartService
from services.api.http_response_constants import HTTP_OK
from services.api.search_service import SearchService
from utils.data_loader import get_data_file
from utils.logger import get_logger

LOGGER = get_logger("api.data_driven")

# ---------------------------------------------------------------------------
# Load JSON-based cases once at module import time
# ---------------------------------------------------------------------------

_CASES = get_data_file("api_test_cases.json")

_JSON_SEARCH_CASES = [
    pytest.param(c["query"], c["expected_product"], c["min_cards"], id=c["query"])
    for c in _CASES.get("search_cases", [])
]

_JSON_PRICE_CASES = [
    pytest.param(c["query"], c["max_price"], id=f"{c['query']}_max{int(c['max_price'])}")
    for c in _CASES.get("price_filter_cases", [])
]

_JSON_CART_CASES = [
    pytest.param(c["query"], id=c["query"])
    for c in _CASES.get("cart_add_cases", [])
]

_JSON_EMPTY_CASES = [
    pytest.param(c["query"], id=f"empty_{i}")
    for i, c in enumerate(_CASES.get("empty_search_cases", []))
]


# =========================================================================== #
# INLINE PARAMS — Search                                                       #
# =========================================================================== #

@allure.feature("API Tests – Data Driven")
@allure.story("Search – inline params")
@pytest.mark.api
class TestSearchApiInline:

    @allure.title("Search [{query}] returns 200 and finds [{expected_product}]")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        ("query", "expected_product"),
        [
            ("MacBook", "MacBook"),
            ("iPhone",  "iPhone"),
            ("Canon",   "Canon"),
            ("Samsung", "Samsung"),
        ],
    )
    def test_search_returns_expected_product_inline(
        self,
        search_service: SearchService,
        query: str,
        expected_product: str,
    ):
        with allure.step(f"GET search for {query!r}"):
            LOGGER.info("Step: search for %r", query)
            resp = search_service.search(query)

        with allure.step("Assert HTTP 200"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )

        with allure.step(f"Assert {expected_product!r} appears in product names"):
            names = search_service.product_names(resp.text)
            LOGGER.info("Found product names: %s", names)
            assert any(expected_product in name for name in names), (
                f"Expected {expected_product!r} in results for {query!r}; got {names}"
            )

    @allure.title("Search [{query}] returns parseable positive prices – inline")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["MacBook", "iPhone", "Canon"])
    def test_search_returns_positive_prices_inline(
        self, search_service: SearchService, query: str
    ):
        with allure.step(f"GET search for {query!r}"):
            LOGGER.info("Step: search for %r", query)
            resp = search_service.search(query)

        with allure.step("Assert all returned prices are positive"):
            assert resp.status_code == HTTP_OK
            prices = search_service.prices(resp.text)
            LOGGER.info("Prices for %r: %s", query, prices)
            assert prices, f"No prices parsed for {query!r}"
            assert all(p > 0 for p in prices), (
                f"Non-positive price found for {query!r}: {prices}"
            )

    @allure.title("Search [{query}] with max_price {max_price} — all results within budget – inline")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        ("query", "max_price"),
        [
            ("MacBook", 2000.0),
            ("iPhone",  1000.0),
            ("Canon",    500.0),
        ],
    )
    def test_search_prices_within_budget_inline(
        self,
        search_service: SearchService,
        query: str,
        max_price: float,
    ):
        with allure.step(f"GET search for {query!r}"):
            LOGGER.info("Step: search for %r, max_price=%s", query, max_price)
            resp = search_service.search(query)

        with allure.step(f"Assert all prices ≤ {max_price}"):
            assert resp.status_code == HTTP_OK
            prices = search_service.prices(resp.text)
            over_budget = [p for p in prices if p > max_price]
            assert not over_budget, (
                f"Prices above {max_price} found for {query!r}: {over_budget}"
            )

    @allure.title("Search for unknown product [{query}] returns 200 with no product cards – inline")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "query",
        ["__nonexistent_product_xyz_999__", "zzz_no_such_item_abc"],
    )
    def test_empty_search_returns_200_no_cards_inline(
        self, search_service: SearchService, query: str
    ):
        with allure.step(f"GET search for unknown query {query!r}"):
            LOGGER.info("Step: empty-result search for %r", query)
            resp = search_service.search(query)

        with allure.step("Assert 200 and zero product cards"):
            assert resp.status_code == HTTP_OK
            cards = search_service.product_cards(resp.text)
            assert not cards, (
                f"Expected no cards for {query!r} but found {len(cards)}"
            )

    @allure.title("Search [{query}] returns numeric product IDs – inline")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["MacBook", "iPhone"])
    def test_search_returns_numeric_ids_inline(
        self, search_service: SearchService, query: str
    ):
        with allure.step(f"GET search for {query!r}"):
            LOGGER.info("Step: search ids for %r", query)
            resp = search_service.search(query)

        with allure.step("Assert all product IDs are numeric strings"):
            assert resp.status_code == HTTP_OK
            ids = search_service.product_ids(resp.text)
            assert ids, f"No product IDs found for {query!r}"
            assert all(pid.isdigit() for pid in ids), (
                f"Non-numeric product IDs for {query!r}: {ids}"
            )


# =========================================================================== #
# INLINE PARAMS — Cart                                                         #
# =========================================================================== #

@allure.feature("API Tests – Data Driven")
@allure.story("Cart – inline params")
@pytest.mark.api
class TestCartApiInline:

    @allure.title("Cart accepts product from search [{query}] – inline")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("query", ["MacBook", "iPhone", "Canon"])
    def test_cart_add_from_search_inline(
        self,
        search_service: SearchService,
        cart_service: CartService,
        query: str,
    ):
        with allure.step(f"Find first product ID for {query!r}"):
            LOGGER.info("Step: find product for %r", query)
            pid = search_service.first_product_id(query)

        with allure.step(f"POST product_id={pid} to cart"):
            LOGGER.info("Step: add product %s to cart", pid)
            resp = cart_service.add_product(pid)

        with allure.step("Assert 200 and cart is not empty"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            cart_resp = cart_service.get_cart()
            assert not cart_service.is_empty(cart_resp.text), (
                f"Cart empty after adding product {pid!r} from query {query!r}"
            )

    @allure.title("Cart total is positive after adding [{query}] – inline")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["MacBook", "iPhone"])
    def test_cart_total_positive_after_add_inline(
        self,
        search_service: SearchService,
        cart_service: CartService,
        query: str,
    ):
        with allure.step(f"Add first result of {query!r} to cart"):
            LOGGER.info("Step: add %r product to cart", query)
            pid = search_service.first_product_id(query)
            cart_service.add_product(pid)

        with allure.step("Assert cart total is parseable and positive"):
            cart_resp = cart_service.get_cart()
            total = cart_service.total(cart_resp.text)
            LOGGER.info("Cart total after adding %r: %s", query, total)
            assert total is not None and total > 0, (
                f"Cart total not positive after adding {query!r} (pid={pid}): {total}"
            )


# =========================================================================== #
# JSON PARAMS — Search                                                         #
# =========================================================================== #

@allure.feature("API Tests – Data Driven")
@allure.story("Search – JSON params")
@pytest.mark.api
class TestSearchApiJson:

    @allure.title("Search [{query}] returns [{expected_product}] – JSON")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        ("query", "expected_product", "min_cards"),
        _JSON_SEARCH_CASES,
    )
    def test_search_returns_expected_product_json(
        self,
        search_service: SearchService,
        query: str,
        expected_product: str,
        min_cards: int,
    ):
        with allure.step(f"GET search for {query!r}"):
            LOGGER.info("Step: JSON-driven search for %r (min_cards=%d)", query, min_cards)
            resp = search_service.search(query)

        with allure.step(f"Assert ≥{min_cards} product cards and {expected_product!r} in names"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            cards = search_service.product_cards(resp.text)
            names = search_service.product_names(resp.text)
            LOGGER.info("Cards: %d, names: %s", len(cards), names)
            assert len(cards) >= min_cards, (
                f"Expected ≥{min_cards} cards for {query!r}; got {len(cards)}"
            )
            assert any(expected_product in name for name in names), (
                f"{expected_product!r} not in product names for {query!r}: {names}"
            )

    @allure.title("Search [{query}] prices within max {max_price} – JSON")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        ("query", "max_price"),
        _JSON_PRICE_CASES,
    )
    def test_search_prices_within_budget_json(
        self,
        search_service: SearchService,
        query: str,
        max_price: float,
    ):
        with allure.step(f"GET search for {query!r}"):
            LOGGER.info("Step: JSON price-filter search for %r (max=%s)", query, max_price)
            resp = search_service.search(query)

        with allure.step(f"Assert all prices ≤ {max_price}"):
            assert resp.status_code == HTTP_OK
            prices = search_service.prices(resp.text)
            over_budget = [p for p in prices if p > max_price]
            assert not over_budget, (
                f"Prices above {max_price} for {query!r}: {over_budget}"
            )

    @allure.title("Unknown search [{query}] returns 200 with no product cards – JSON")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", _JSON_EMPTY_CASES)
    def test_empty_search_returns_200_no_cards_json(
        self, search_service: SearchService, query: str
    ):
        with allure.step(f"GET search for unknown query {query!r}"):
            LOGGER.info("Step: JSON empty-result search for %r", query)
            resp = search_service.search(query)

        with allure.step("Assert 200 and zero product cards"):
            assert resp.status_code == HTTP_OK
            cards = search_service.product_cards(resp.text)
            assert not cards, (
                f"Expected no cards for {query!r}; found {len(cards)}"
            )


# =========================================================================== #
# JSON PARAMS — Cart                                                           #
# =========================================================================== #

@allure.feature("API Tests – Data Driven")
@allure.story("Cart – JSON params")
@pytest.mark.api
class TestCartApiJson:

    @allure.title("Cart accepts product from [{query}] – JSON")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("query", _JSON_CART_CASES)
    def test_cart_add_from_search_json(
        self,
        search_service: SearchService,
        cart_service: CartService,
        query: str,
    ):
        with allure.step(f"Find first product for {query!r}"):
            LOGGER.info("Step: JSON cart add for %r", query)
            pid = search_service.first_product_id(query)

        with allure.step(f"POST product_id={pid} to cart"):
            LOGGER.info("Step: add product %s from query %r", pid, query)
            resp = cart_service.add_product(pid)

        with allure.step("Assert 200 and cart not empty"):
            assert resp.status_code == HTTP_OK, (
                f"Expected {HTTP_OK}, got {resp.status_code}"
            )
            cart_resp = cart_service.get_cart()
            assert not cart_service.is_empty(cart_resp.text), (
                f"Cart empty after adding {pid!r} from {query!r}"
            )
