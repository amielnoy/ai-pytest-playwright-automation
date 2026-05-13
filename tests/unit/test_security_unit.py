import allure
import pytest

from services.api.cart_service import CartService
from services.api.search_service import SearchService
from services.rest_client import RestClient
from utils.logger import get_logger

LOGGER = get_logger("security.unit")


class _FakeSession:
    def __init__(self):
        self.calls: list[tuple] = []
        self.headers: dict = {}
        self.cookies: dict = {}

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))

    def close(self):
        pass


@pytest.mark.security
def test_rest_client_sends_no_authorization_header_by_default():
    with allure.step("Create a default RestClient with no custom headers"):
        LOGGER.info("Step: Instantiate RestClient() with no arguments")
        client = RestClient()

    with allure.step("Assert Authorization header is absent from the session"):
        LOGGER.info("Step: Assert 'Authorization' not in client.session.headers")
        assert "Authorization" not in client.session.headers, (
            "Default RestClient must not set an Authorization header"
        )


@pytest.mark.security
def test_rest_client_custom_headers_do_not_inject_credential_headers():
    with allure.step("Create RestClient with a safe custom header (X-Requested-With)"):
        LOGGER.info("Step: Instantiate RestClient with X-Requested-With only")
        client = RestClient(headers={"X-Requested-With": "XMLHttpRequest"})

    with allure.step("Assert Authorization and Cookie are not injected into session headers"):
        LOGGER.info("Step: Assert Authorization and Cookie absent from session.headers")
        assert "Authorization" not in client.session.headers, (
            "RestClient must not inject Authorization when only safe headers are provided"
        )
        assert "Cookie" not in client.session.headers, (
            "RestClient must not inject Cookie via session-level headers"
        )


@pytest.mark.security
def test_rest_client_timeout_is_forwarded_on_every_request():
    with allure.step("Create RestClient(timeout=5) and attach a fake session"):
        LOGGER.info("Step: Build RestClient(timeout=5) and swap in FakeSession")
        client = RestClient(timeout=5)
        fake = _FakeSession()
        client.session = fake

    with allure.step("Call GET and POST through the client"):
        LOGGER.info("Step: Invoke client.get and client.post")
        client.get("https://example.test/resource")
        client.post("https://example.test/action", data={"k": "v"})

    with allure.step("Assert timeout=5 is present in both recorded calls"):
        LOGGER.info("Step: Assert timeout forwarded in GET and POST kwargs")
        assert fake.calls[0][2].get("timeout") == 5, (
            "GET call missing the configured timeout - no timeout means potential hang"
        )
        assert fake.calls[1][2].get("timeout") == 5, (
            "POST call missing the configured timeout - no timeout means potential hang"
        )


@pytest.mark.security
def test_search_service_product_names_does_not_raise_on_xss_html():
    xss_html = (
        '<div class="product-thumb">'
        '<h4><a href="#">&lt;script&gt;alert(1)&lt;/script&gt;</a></h4>'
        "</div>"
    )

    with allure.step("Instantiate SearchService backed by a real (offline) RestClient"):
        LOGGER.info("Step: Build SearchService with RestClient, base_url=https://example.test")
        service = SearchService(RestClient(), "https://example.test")

    with allure.step("Call product_names with XSS-containing HTML"):
        LOGGER.info("Step: Call service.product_names on XSS HTML; expect list, no exception")
        names = service.product_names(xss_html)

    with allure.step("Assert result is a list without raising an exception"):
        LOGGER.info("Step: Assert isinstance(names, list)")
        assert isinstance(names, list), (
            f"product_names must return a list on XSS input, got {type(names)}"
        )


@pytest.mark.security
def test_search_service_product_ids_does_not_raise_on_malformed_html():
    malformed_html = "cart.add('<<unclosed>') ; RANDOM >< GARBAGE ><<<"

    with allure.step("Instantiate SearchService backed by a real (offline) RestClient"):
        LOGGER.info("Step: Build SearchService with RestClient, base_url=https://example.test")
        service = SearchService(RestClient(), "https://example.test")

    with allure.step("Call product_ids with malformed HTML"):
        LOGGER.info("Step: Call service.product_ids on malformed HTML; expect list, no exception")
        ids = service.product_ids(malformed_html)

    with allure.step("Assert result is a list (possibly empty) without raising"):
        LOGGER.info("Step: Assert isinstance(ids, list)")
        assert isinstance(ids, list), (
            f"product_ids must return a list on malformed input, got {type(ids)}"
        )


@pytest.mark.security
def test_cart_service_is_empty_returns_false_when_html_has_product_rows():
    html_with_products = (
        '<td class="text-left">MacBook</td>'
        '<td class="text-right">$200.00</td>'
    )

    with allure.step("Instantiate CartService backed by a real (offline) RestClient"):
        LOGGER.info("Step: Build CartService with RestClient, base_url=https://example.test")
        service = CartService(RestClient(), "https://example.test")

    with allure.step("Call is_empty on HTML that contains product rows but no empty marker"):
        LOGGER.info("Step: Call service.is_empty on HTML with product row content")
        result = service.is_empty(html_with_products)

    with allure.step("Assert is_empty returns False - product rows must not trigger empty state"):
        LOGGER.info("Step: Assert result is False")
        assert result is False, (
            "is_empty must return False when the empty-cart marker is absent from the HTML"
        )


@pytest.mark.security
def test_cart_service_total_returns_none_on_truncated_html():
    truncated_html = "<table><tr><td><strong>Total:</strong></td><td>$"

    with allure.step("Instantiate CartService backed by a real (offline) RestClient"):
        LOGGER.info("Step: Build CartService with RestClient, base_url=https://example.test")
        service = CartService(RestClient(), "https://example.test")

    with allure.step("Call total on truncated HTML with no closing tag for the price cell"):
        LOGGER.info("Step: Call service.total on truncated HTML; expect None, no exception")
        result = service.total(truncated_html)

    with allure.step("Assert total returns None gracefully without raising an exception"):
        LOGGER.info("Step: Assert result is None for unparseable/truncated HTML")
        assert result is None, (
            f"total must return None on truncated HTML, got {result!r}"
        )


@pytest.mark.security
def test_rest_client_post_is_excluded_from_default_retry_methods():
    with allure.step("Create a default RestClient and read the HTTPS adapter retry config"):
        LOGGER.info("Step: Build RestClient() and inspect HTTPS adapter max_retries")
        client = RestClient()
        retry_config = client.session.adapters["https://"].max_retries

    with allure.step("Assert POST is not in the allowed retry methods"):
        LOGGER.info(
            "Step: Assert POST not in allowed_methods=%s", retry_config.allowed_methods
        )
        assert "POST" not in retry_config.allowed_methods, (
            "POST must not be retried automatically - retrying mutations risks duplicate "
            "cart adds or order submissions"
        )
