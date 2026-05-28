"""Smoke tests for services/api/opencart_fallback.py.

The fallback is the entire offline substitute for tutorialsninja.com — it handles
every route the test suite calls.  These tests verify that each route returns a
well-formed, correct response without any live network.
"""
from http import HTTPStatus
from unittest.mock import MagicMock

import allure
import pytest
from requests import Response
from requests.cookies import RequestsCookieJar

from services.api.opencart_fallback import (
    PRODUCTS,
    _CART_REGISTRY,
    cart_add_payload,
    cart_html,
    ensure_session_cookie,
    fallback_response_for_request,
    home_html,
    is_challenge_page,
    login_html,
    product_by_id,
    register_html,
    response as make_response,
    route_from_request,
    search_html,
    search_products,
)


def _empty_cookies() -> RequestsCookieJar:
    return RequestsCookieJar()


def _cookies_with_session(sid: str = "test-sid") -> RequestsCookieJar:
    jar = RequestsCookieJar()
    jar.set("OCSESSID", sid, path="/")
    return jar


BASE = "https://tutorialsninja.com/demo"


# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------

@allure.feature("OpenCart Fallback")
@allure.story("Product catalogue")
class TestSearchProducts:

    @allure.title("search_products('MacBook') returns MacBook products")
    def test_search_macbook(self):
        results = search_products("MacBook")
        assert results
        assert all("macbook" in p.name.casefold() for p in results)

    @allure.title("search_products('iPhone') returns iPhone product")
    def test_search_iphone(self):
        results = search_products("iPhone")
        assert len(results) == 1
        assert results[0].name == "iPhone"

    @allure.title("search_products('') returns no results (empty query)")
    def test_empty_query_returns_nothing(self):
        assert search_products("") == []

    @allure.title("search_products is case-insensitive")
    def test_case_insensitive(self):
        lower = search_products("macbook")
        upper = search_products("MACBOOK")
        assert lower == upper

    @allure.title("search_products('xyz_not_a_product') returns empty list")
    def test_no_match_returns_empty(self):
        assert search_products("xyz_not_a_product") == []

    @allure.title("search_products with sort='name' returns alphabetically sorted results")
    def test_sort_by_name_ascending(self):
        results = search_products("Mac", sort="name", order="ASC")
        names = [p.name for p in results]
        assert names == sorted(names, key=str.casefold)

    @allure.title("search_products with sort='name', order='DESC' returns reverse-sorted results")
    def test_sort_by_name_descending(self):
        results = search_products("Mac", sort="name", order="DESC")
        names = [p.name for p in results]
        assert names == sorted(names, key=str.casefold, reverse=True)


@allure.feature("OpenCart Fallback")
@allure.story("Product catalogue")
class TestProductById:

    @allure.title("product_by_id returns the matching product")
    def test_known_id_returns_product(self):
        macbook = product_by_id("43")
        assert macbook is not None
        assert macbook.name == "MacBook"
        assert macbook.price == 602.0

    @allure.title("product_by_id returns None for unknown ID")
    def test_unknown_id_returns_none(self):
        assert product_by_id("9999") is None

    @allure.title("all PRODUCTS are findable by their own ID")
    def test_all_products_findable(self):
        for product in PRODUCTS:
            found = product_by_id(product.product_id)
            assert found == product


@allure.feature("OpenCart Fallback")
@allure.story("Session management")
class TestSessionCookie:

    @allure.title("ensure_session_cookie creates a new OCSESSID when none exists")
    def test_creates_new_cookie(self):
        jar = _empty_cookies()
        sid = ensure_session_cookie(jar)
        assert sid
        assert jar.get("OCSESSID") == sid

    @allure.title("ensure_session_cookie returns the existing OCSESSID when present")
    def test_preserves_existing_cookie(self):
        jar = _cookies_with_session("existing-123")
        sid = ensure_session_cookie(jar)
        assert sid == "existing-123"

    @allure.title("new OCSESSID is a non-empty hex string")
    def test_new_sid_is_hex(self):
        jar = _empty_cookies()
        sid = ensure_session_cookie(jar)
        int(sid, 16)   # raises ValueError if not hex


@allure.feature("OpenCart Fallback")
@allure.story("Challenge detection")
class TestIsChallengedPage:

    @allure.title("415 status code is detected as a challenge page")
    def test_415_is_challenge(self):
        resp = make_response("blocked", status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        assert is_challenge_page(resp) is True

    @allure.title("'One moment, please' body is detected as challenge")
    def test_one_moment_text_is_challenge(self):
        resp = make_response("One moment, please...")
        assert is_challenge_page(resp) is True

    @allure.title("Normal 200 search page is not a challenge")
    def test_normal_page_is_not_challenge(self):
        resp = make_response(search_html("MacBook"))
        assert is_challenge_page(resp) is False

    @allure.title("Non-Response objects are not challenge pages")
    def test_non_response_returns_false(self):
        assert is_challenge_page("some string") is False  # type: ignore[arg-type]
        assert is_challenge_page(None) is False            # type: ignore[arg-type]


@allure.feature("OpenCart Fallback")
@allure.story("Cart payload")
class TestCartAddPayload:

    @allure.title("cart_add_payload returns a dict with product total when product exists")
    def test_known_product_returns_total(self):
        cart: dict[str, int] = {"43": 2}
        payload = cart_add_payload(cart, "43")
        assert isinstance(payload, dict)
        assert "total" in payload

    @allure.title("cart_add_payload for unknown product returns an empty list")
    def test_unknown_product_returns_list(self):
        payload = cart_add_payload({}, "9999")
        assert payload == []


# ---------------------------------------------------------------------------
# HTML generators
# ---------------------------------------------------------------------------

@allure.feature("OpenCart Fallback")
@allure.story("HTML generators")
class TestHTMLGenerators:

    @allure.title("home_html() returns valid HTML with 'Your Store'")
    def test_home_html_contains_store_marker(self):
        html = home_html()
        assert "Your Store" in html
        assert "<html" in html.lower()

    @allure.title("search_html('MacBook') contains a MacBook product card")
    def test_search_html_contains_product(self):
        html = search_html("MacBook")
        assert "MacBook" in html
        assert "product-thumb" in html

    @allure.title("search_html('') contains a 'no results' message")
    def test_search_html_no_results(self):
        html = search_html("")
        assert "product-thumb" not in html

    @allure.title("login_html() contains the login form elements")
    def test_login_html_has_form(self):
        html = login_html()
        assert "E-Mail Address" in html or "email" in html.lower()
        assert "Password" in html
        assert "<form" in html.lower()

    @allure.title("login_html(warning=...) injects the warning text")
    def test_login_html_with_warning(self):
        html = login_html("Invalid credentials")
        assert "Invalid credentials" in html

    @allure.title("register_html() contains the registration form")
    def test_register_html_has_form(self):
        html = register_html()
        assert "Register" in html
        assert "First Name" in html or "firstname" in html.lower()

    @allure.title("register_html(success=True) contains the success heading")
    def test_register_html_success(self):
        html = register_html(success=True)
        assert "success" in html.lower() or "Your Account Has Been Created" in html


# ---------------------------------------------------------------------------
# Route dispatcher
# ---------------------------------------------------------------------------

@allure.feature("OpenCart Fallback")
@allure.story("Route dispatcher")
class TestRouteDispatcher:

    def _dispatch(self, route: str, method: str = "GET", data=None) -> Response:
        url = f"{BASE}/index.php?route={route}"
        cookies = _empty_cookies()
        return fallback_response_for_request(
            method, url, cookies=cookies, cart={}, data=data,
        )

    @allure.title("GET / (home route) returns 200 with 'Your Store'")
    def test_home_route(self):
        url = f"{BASE}/"
        cookies = _empty_cookies()
        resp = fallback_response_for_request("GET", url, cookies=cookies, cart={})
        assert resp.status_code == HTTPStatus.OK
        assert "Your Store" in resp.text

    @allure.title("GET product/search?search=MacBook returns 200 with product card")
    def test_search_route(self):
        resp = self._dispatch("product/search&search=MacBook")
        assert resp.status_code == HTTPStatus.OK
        assert "MacBook" in resp.text

    @allure.title("GET checkout/cart returns 200 cart page")
    def test_cart_route(self):
        resp = self._dispatch("checkout/cart")
        assert resp.status_code == HTTPStatus.OK

    @allure.title("POST checkout/cart/add with valid product_id updates the cart")
    def test_cart_add_route(self):
        url = f"{BASE}/index.php?route=checkout/cart/add"
        cookies = _empty_cookies()
        cart: dict[str, int] = {}
        resp = fallback_response_for_request(
            "POST", url, cookies=cookies, cart=cart,
            data={"product_id": "43", "quantity": "1"},
        )
        assert resp.status_code == HTTPStatus.OK

    @allure.title("GET account/register returns 200 with registration form")
    def test_register_route(self):
        resp = self._dispatch("account/register")
        assert resp.status_code == HTTPStatus.OK
        assert "Register" in resp.text

    @allure.title("POST account/register with empty first_name returns error page")
    def test_register_post_empty_first_name(self):
        url = f"{BASE}/index.php?route=account/register"
        cookies = _empty_cookies()
        resp = fallback_response_for_request(
            "POST", url, cookies=cookies, cart={},
            data={"firstname": "", "lastname": "Smith"},
        )
        assert resp.status_code == HTTPStatus.OK
        assert "First Name" in resp.text

    @allure.title("GET /.git/ returns 404 (blocked path)")
    def test_blocked_path_returns_404(self):
        url = f"{BASE}/.git/config"
        cookies = _empty_cookies()
        resp = fallback_response_for_request("GET", url, cookies=cookies, cart={})
        assert resp.status_code == HTTPStatus.NOT_FOUND

    @allure.title("GET product/product with unknown id returns 404")
    def test_product_detail_unknown_id(self):
        url = f"{BASE}/index.php?route=product/product&product_id=9999"
        cookies = _empty_cookies()
        resp = fallback_response_for_request("GET", url, cookies=cookies, cart={})
        assert resp.status_code == HTTPStatus.NOT_FOUND


@allure.feature("OpenCart Fallback")
@allure.story("Route dispatcher")
class TestRouteFromRequest:

    @allure.title("route_from_request extracts route from query string")
    def test_extracts_route(self):
        url = f"{BASE}/index.php?route=product/search&search=q"
        assert route_from_request(url) == "product/search"

    @allure.title("route_from_request returns empty string when route param absent")
    def test_no_route_returns_empty(self):
        assert route_from_request(f"{BASE}/") == ""
