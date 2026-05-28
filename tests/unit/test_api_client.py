"""Unit tests for utils/api_client.py.

Tests _search_url, _parse_cards, ApiProduct, build_session, and create_cart
at the unit level — the RestClient is mocked so no real HTTP calls are made.
"""
from unittest.mock import MagicMock, patch

import allure
import pytest

from utils.api_client import (
    ApiProduct,
    _parse_cards,
    _search_url,
    build_session,
    create_cart,
)


# ---------------------------------------------------------------------------
# Minimal HTML helpers (mirrors the format _parse_cards expects)
# ---------------------------------------------------------------------------

def _product_card(pid: str, name: str, price: str) -> str:
    """Produce a minimal product-thumb HTML block matching OpenCart's format."""
    return (
        f'<div class="product-thumb">'
        f'<h4><a href="#">{name}</a></h4>'
        f'<p class="price">{price}</p>'
        f"<button onclick=\"cart.add('{pid}')\">Add</button>"
        f"</div>"
    )


def _search_page(*cards: str) -> str:
    return "<html><body>" + "".join(cards) + "</body></html>"


# ---------------------------------------------------------------------------
# _search_url
# ---------------------------------------------------------------------------

@allure.feature("API Client")
@allure.story("URL builder")
class TestSearchUrl:

    @allure.title("_search_url builds the correct OpenCart search endpoint")
    def test_basic_url(self):
        url = _search_url("https://example.com", "MacBook")
        assert url.startswith("https://example.com/index.php?")
        assert "route=product%2Fsearch" in url or "route=product/search" in url
        assert "search=MacBook" in url

    @allure.title("_search_url URL-encodes special characters in the query")
    def test_url_encodes_spaces(self):
        url = _search_url("https://example.com", "Mac Book")
        assert "Mac+Book" in url or "Mac%20Book" in url

    @allure.title("_search_url uses the supplied base_url as the prefix")
    def test_uses_base_url(self):
        url = _search_url("https://mystore.test/demo", "q")
        assert url.startswith("https://mystore.test/demo/")


# ---------------------------------------------------------------------------
# _parse_cards
# ---------------------------------------------------------------------------

@allure.feature("API Client")
@allure.story("HTML parser")
class TestParseCards:

    @allure.title("_parse_cards extracts product_id, name, and price from valid HTML")
    def test_extracts_fields(self):
        html = _search_page(_product_card("43", "MacBook", "$602.00"))
        results = _parse_cards(html, max_price=1000.0, limit=10)
        assert len(results) == 1
        pid, name, price = results[0]
        assert pid == "43"
        assert name == "MacBook"
        assert abs(price - 602.0) < 0.01

    @allure.title("_parse_cards filters out products above max_price")
    def test_filters_by_max_price(self):
        html = _search_page(
            _product_card("43", "MacBook", "$602.00"),
            _product_card("45", "MacBook Pro", "$2,000.00"),
        )
        results = _parse_cards(html, max_price=700.0, limit=10)
        assert len(results) == 1
        assert results[0][1] == "MacBook"

    @allure.title("_parse_cards respects the limit parameter")
    def test_respects_limit(self):
        html = _search_page(
            _product_card("1", "A", "$10.00"),
            _product_card("2", "B", "$20.00"),
            _product_card("3", "C", "$30.00"),
        )
        results = _parse_cards(html, max_price=100.0, limit=2)
        assert len(results) == 2

    @allure.title("_parse_cards returns empty list when no product-thumb blocks found")
    def test_no_products(self):
        html = "<html><body><p>No results</p></body></html>"
        assert _parse_cards(html, max_price=1000.0, limit=10) == []

    @allure.title("_parse_cards skips malformed cards missing a cart.add() call")
    def test_skips_card_without_cart_add(self):
        bad = (
            '<div class="product-thumb">'
            '<h4><a href="#">Broken</a></h4>'
            '<p class="price">$10.00</p>'
            "</div>"
        )
        html = _search_page(bad)
        assert _parse_cards(html, max_price=1000.0, limit=10) == []

    @allure.title("_parse_cards handles multiple products in the correct order")
    def test_order_preserved(self):
        html = _search_page(
            _product_card("1", "Alpha", "$10.00"),
            _product_card("2", "Beta", "$20.00"),
        )
        results = _parse_cards(html, max_price=100.0, limit=10)
        assert [r[1] for r in results] == ["Alpha", "Beta"]


# ---------------------------------------------------------------------------
# ApiProduct dataclass
# ---------------------------------------------------------------------------

@allure.feature("API Client")
@allure.story("ApiProduct dataclass")
class TestApiProduct:

    @allure.title("ApiProduct stores product_id, name, and price")
    def test_fields(self):
        p = ApiProduct(product_id="43", name="MacBook", price=602.0)
        assert p.product_id == "43"
        assert p.name == "MacBook"
        assert p.price == 602.0

    @allure.title("ApiProduct equality is field-based")
    def test_equality(self):
        a = ApiProduct("43", "MacBook", 602.0)
        b = ApiProduct("43", "MacBook", 602.0)
        assert a == b


# ---------------------------------------------------------------------------
# build_session
# ---------------------------------------------------------------------------

@allure.feature("API Client")
@allure.story("Session builder")
class TestBuildSession:

    @allure.title("build_session() returns a RestClient with User-Agent header set")
    def test_has_user_agent(self):
        client = build_session()
        try:
            ua = client.session.headers.get("User-Agent", "")
            assert ua, "User-Agent should not be empty"
        finally:
            client.close()


# ---------------------------------------------------------------------------
# create_cart (mocked RestClient)
# ---------------------------------------------------------------------------

@allure.feature("API Client")
@allure.story("create_cart")
class TestCreateCart:

    def _mock_client(self, search_html: str) -> MagicMock:
        client = MagicMock()
        search_resp = MagicMock()
        search_resp.text = search_html
        search_resp.raise_for_status.return_value = None
        client.get.return_value = search_resp

        add_resp = MagicMock()
        add_resp.raise_for_status.return_value = None
        client.post.return_value = add_resp

        client.cookies = MagicMock()
        client.cookies.get.return_value = "test-session-id"
        return client

    @allure.title("create_cart raises ValueError when no products match")
    def test_raises_when_no_products(self):
        html = "<html><body><p>No results</p></body></html>"
        client = self._mock_client(html)
        with patch("utils.api_client.build_session", return_value=client):
            with patch("utils.api_client.RestClient"):
                with pytest.raises(ValueError, match="No products found"):
                    create_cart("https://example.com", "xyz", max_price=100.0, limit=1)

    @allure.title("create_cart raises ValueError when all products exceed max_price")
    def test_raises_when_all_above_max_price(self):
        html = _search_page(_product_card("43", "MacBook", "$602.00"))
        client = self._mock_client(html)
        with patch("utils.api_client.build_session", return_value=client):
            with pytest.raises(ValueError, match="No products found"):
                create_cart("https://example.com", "MacBook", max_price=100.0, limit=5)

    @allure.title("create_cart returns (ocsessid, products) on success")
    def test_returns_ocsessid_and_products(self):
        html = _search_page(_product_card("43", "MacBook", "$602.00"))
        client = self._mock_client(html)
        with patch("utils.api_client.build_session", return_value=client):
            ocsessid, products = create_cart(
                "https://example.com", "MacBook", max_price=1000.0, limit=5
            )
        assert ocsessid == "test-session-id"
        assert len(products) == 1
        assert products[0].name == "MacBook"
        assert products[0].product_id == "43"

    @allure.title("create_cart calls GET search URL then POST cart/add for each product")
    def test_calls_search_then_cart_add(self):
        html = _search_page(
            _product_card("43", "MacBook", "$602.00"),
            _product_card("40", "iPhone", "$123.20"),
        )
        client = self._mock_client(html)
        with patch("utils.api_client.build_session", return_value=client):
            create_cart("https://example.com", "Mac", max_price=1000.0, limit=5)

        client.get.assert_called_once()
        assert client.post.call_count == 2
        post_urls = [c.args[0] for c in client.post.call_args_list]
        assert all("checkout/cart/add" in u for u in post_urls)

    @allure.title("create_cart respects the limit — adds at most limit products")
    def test_limit_respected(self):
        html = _search_page(
            _product_card("1", "A", "$10.00"),
            _product_card("2", "B", "$20.00"),
            _product_card("3", "C", "$30.00"),
        )
        client = self._mock_client(html)
        with patch("utils.api_client.build_session", return_value=client):
            _, products = create_cart(
                "https://example.com", "x", max_price=100.0, limit=2
            )
        assert len(products) == 2
        assert client.post.call_count == 2
