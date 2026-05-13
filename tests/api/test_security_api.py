import allure
import pytest

from services.api.cart_service import CartService
from services.api.http_response_constants import HTTP_OK
from services.api.search_service import SearchService
from utils.api_client import build_session
from utils.logger import get_logger

LOGGER = get_logger("security.api")

_SQL_INJECTION = "' OR '1'='1'--"
_XSS_SCRIPT = "<script>alert(1)</script>"
_XSS_IMG = "<img src=x onerror=alert(1)>"
_NULL_BYTE_QUERY = "MacBook\x00evil"
_OVERSIZED_QUERY = "A" * 4096
_PATH_TRAVERSAL = "../../etc/passwd"
_SQL_PRODUCT_ID = "' OR 1=1 --"
_XSS_PRODUCT_ID = "<script>alert(1)</script>"

_DB_ERROR_MARKERS = ("Fatal error", "mysql_fetch", "SQL syntax", "You have an error in your SQL")
_FILE_MARKERS = ("root:x:", "/bin/bash", "/bin/sh")


def _assert_no_markers(html: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        assert marker not in html, f"{label}: {marker!r} found in response"


@allure.feature("Security Tests")
@allure.story("Search input security")
@pytest.mark.api
@pytest.mark.security
class TestSearchSecurity:

    @allure.title("SQL injection in search query returns 200 without DB error")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection_in_search_returns_200_without_db_error(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search with SQL injection payload: {_SQL_INJECTION!r}"):
            LOGGER.info("Step: GET search with SQL injection payload: %r", _SQL_INJECTION)
            resp = search_service.search(_SQL_INJECTION)

        with allure.step("Assert HTTP 200 and no DB error traceback in response"):
            LOGGER.info("Step: Assert 200 and no DB error markers")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            _assert_no_markers(resp.text, _DB_ERROR_MARKERS, "DB error on SQL injection")

    @allure.title("XSS <script> in search query is not reflected verbatim in response")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_script_tag_in_search_is_encoded_in_response(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search with XSS script payload: {_XSS_SCRIPT!r}"):
            LOGGER.info("Step: GET search with XSS payload: %r", _XSS_SCRIPT)
            resp = search_service.search(_XSS_SCRIPT)

        with allure.step("Assert HTTP 200 and raw <script> tag is not reflected unencoded"):
            LOGGER.info("Step: Assert raw <script>alert(1)</script> absent from response body")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            assert "<script>alert(1)</script>" not in resp.text, (
                "XSS payload reflected verbatim - potential reflected XSS vulnerability"
            )

    @allure.title("HTML injection <img onerror> in search is not reflected as an executable tag")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_html_injection_img_tag_in_search_is_encoded(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search with HTML injection payload: {_XSS_IMG!r}"):
            LOGGER.info("Step: GET search with HTML injection payload: %r", _XSS_IMG)
            resp = search_service.search(_XSS_IMG)

        with allure.step("Assert HTTP 200 and the full unencoded <img> tag is absent from the response"):
            LOGGER.info("Step: Assert raw <img src=x onerror=alert(1)> absent as executable tag")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            # Angle brackets encoded to &lt;/&gt; means the img tag cannot execute;
            # checking the full unencoded form catches a real injection while allowing encoded reflections.
            assert "<img src=x onerror=alert(1)>" not in resp.text, (
                "HTML injection <img> tag reflected unencoded - executable XSS payload present"
            )

    @allure.title("Null byte embedded in search query is handled gracefully")
    @allure.severity(allure.severity_level.NORMAL)
    def test_null_byte_in_search_is_handled_gracefully(
        self, search_service: SearchService
    ):
        with allure.step("GET search with null byte embedded in query string"):
            LOGGER.info("Step: GET search with null byte query: %r", _NULL_BYTE_QUERY)
            resp = search_service.search(_NULL_BYTE_QUERY)

        with allure.step("Assert HTTP 200 and no server error in response"):
            LOGGER.info("Step: Assert 200 and no Fatal error on null byte input")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            assert "Fatal error" not in resp.text, "Server error triggered by null byte input"

    @allure.title("Oversized search query (4 KB) is handled gracefully")
    @allure.severity(allure.severity_level.NORMAL)
    def test_oversized_search_query_is_handled_gracefully(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search with {len(_OVERSIZED_QUERY)}-char oversized query"):
            LOGGER.info("Step: GET search with %d-char oversized query", len(_OVERSIZED_QUERY))
            resp = search_service.search(_OVERSIZED_QUERY)

        with allure.step("Assert HTTP 200 and no server crash on oversized input"):
            LOGGER.info("Step: Assert 200 and no Fatal error for oversized input")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            assert "Fatal error" not in resp.text, "Server error on oversized query input"

    @allure.title("Path traversal in search query does not expose file-system content")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_path_traversal_in_search_does_not_expose_file_content(
        self, search_service: SearchService
    ):
        with allure.step(f"GET search with path traversal payload: {_PATH_TRAVERSAL!r}"):
            LOGGER.info("Step: GET search with path traversal: %r", _PATH_TRAVERSAL)
            resp = search_service.search(_PATH_TRAVERSAL)

        with allure.step("Assert HTTP 200 and no /etc/passwd content in response"):
            LOGGER.info("Step: Assert no filesystem markers in response body")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            _assert_no_markers(resp.text, _FILE_MARKERS, "File content leaked via path traversal")


@allure.feature("Security Tests")
@allure.story("Cart input security")
@pytest.mark.api
@pytest.mark.security
class TestCartSecurity:

    @allure.title("Cart add with SQL injection product_id is handled safely")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_add_with_sql_injection_product_id(
        self, cart_service: CartService
    ):
        with allure.step(f"POST cart/add with SQL injection product_id: {_SQL_PRODUCT_ID!r}"):
            LOGGER.info("Step: POST cart/add with SQL injection product_id: %r", _SQL_PRODUCT_ID)
            resp = cart_service.add_product(_SQL_PRODUCT_ID)

        with allure.step("Assert HTTP 200 and no DB error markers in response"):
            LOGGER.info("Step: Assert 200 and no DB error markers")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            _assert_no_markers(resp.text, _DB_ERROR_MARKERS, "DB error on SQL injection product_id")

    @allure.title("Cart add with XSS product_id is handled safely")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_add_with_xss_product_id(
        self, cart_service: CartService
    ):
        with allure.step(f"POST cart/add with XSS product_id: {_XSS_PRODUCT_ID!r}"):
            LOGGER.info("Step: POST cart/add with XSS product_id: %r", _XSS_PRODUCT_ID)
            resp = cart_service.add_product(_XSS_PRODUCT_ID)

        with allure.step("Assert HTTP 200 and raw <script> not echoed unencoded"):
            LOGGER.info("Step: Assert 200 and no unencoded <script> in response")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            assert "<script>alert(1)</script>" not in resp.text, (
                "XSS product_id reflected unencoded in cart add response"
            )

    @allure.title("HTTP GET to cart/add endpoint does not mutate cart state")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_to_cart_add_endpoint_does_not_add_item(
        self,
        search_service: SearchService,
        cart_service: CartService,
        session,
        api_base_url: str,
    ):
        pid = search_service.first_product_id("MacBook")

        with allure.step(f"Send GET (not POST) to cart/add with product_id={pid}"):
            LOGGER.info("Step: GET to cart/add with product_id=%s - verb tampering attempt", pid)
            resp = session.get(
                f"{api_base_url}/index.php",
                params={"route": "checkout/cart/add", "product_id": pid},
            )

        with allure.step("Assert HTTP 200 and cart remains empty after GET request"):
            LOGGER.info("Step: Assert cart is still empty - GET must not add items")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            cart_resp = cart_service.get_cart()
            assert cart_service.is_empty(cart_resp.text), (
                "Cart is not empty after GET to cart/add - HTTP verb tampering succeeds"
            )


@allure.feature("Security Tests")
@allure.story("Session and cookie security")
@pytest.mark.api
@pytest.mark.security
class TestSessionSecurity:

    @allure.title("OCSESSID session cookie is issued with path=/ scope on first visit")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ocsessid_cookie_is_set_with_root_path_scope(self, api_base_url: str):
        with allure.step("Send a fresh GET to the site root and capture Set-Cookie header"):
            LOGGER.info("Step: GET %s with fresh session, capture Set-Cookie", api_base_url)
            client = build_session()
            resp = client.get(api_base_url)
            client.close()

        with allure.step("Assert OCSESSID is issued and scoped to path=/"):
            LOGGER.info("Step: Assert OCSESSID present and path=/ in Set-Cookie value")
            set_cookie = resp.headers.get("Set-Cookie", "")
            assert "OCSESSID" in set_cookie, (
                f"No OCSESSID in Set-Cookie header: {set_cookie!r}"
            )
            ocsessid_part = set_cookie.split(",")[0]
            assert "path=/" in ocsessid_part, (
                f"OCSESSID cookie not scoped to path=/: {ocsessid_part!r}"
            )

    @allure.title("Two independent sessions receive distinct OCSESSID values")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_independent_sessions_receive_distinct_ocsessid(self, api_base_url: str):
        with allure.step("Create two independent sessions and visit the site root"):
            LOGGER.info("Step: Create session_a and session_b, GET %s with each", api_base_url)
            session_a = build_session()
            session_b = build_session()
            session_a.get(api_base_url)
            session_b.get(api_base_url)

        with allure.step("Assert each session holds a different OCSESSID value"):
            LOGGER.info("Step: Compare OCSESSID values across sessions")
            sid_a = session_a.cookies.get("OCSESSID")
            sid_b = session_b.cookies.get("OCSESSID")
            assert sid_a, "Session A received no OCSESSID cookie"
            assert sid_b, "Session B received no OCSESSID cookie"
            assert sid_a != sid_b, (
                f"Sessions share the same OCSESSID ({sid_a}) - session fixation risk"
            )
            session_a.close()
            session_b.close()

    @allure.title("Unauthenticated access to account page does not expose private sections")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_unauthenticated_account_page_does_not_expose_account_data(
        self, session, api_base_url: str
    ):
        with allure.step("GET /account/account without prior authentication"):
            LOGGER.info("Step: GET account/account with no credentials")
            resp = session.get(
                f"{api_base_url}/index.php",
                params={"route": "account/account"},
            )

        with allure.step("Assert account dashboard content is absent from response"):
            LOGGER.info("Step: Assert account-dashboard-only markers absent from response")
            assert resp.status_code == HTTP_OK, f"Expected {HTTP_OK}, got {resp.status_code}"
            # These markers only appear inside the account dashboard, not in footer nav links
            for private_marker in ("route=account/edit", "route=account/password", "Your Personal Details"):
                assert private_marker not in resp.text, (
                    f"Account dashboard marker {private_marker!r} visible without authentication"
                )

        with allure.step("Assert login page content is present confirming redirect to login"):
            LOGGER.info("Step: Assert login page markers present in response")
            assert "Returning Customer" in resp.text or "E-Mail Address" in resp.text, (
                "Expected login page after unauthenticated account access, but login form absent"
            )
