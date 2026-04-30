import pytest

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.search_results_page import SearchResultsPage
from services.api.ebay_search_service import EbaySearchService
from services.api.http_response_constants import HTTP_FORBIDDEN, HTTP_OK
from services.api.public_service import EndpointCase
from services.api.search_service import SearchCase
from services.rest_client import RestClient
from tests.page_records import CartFlowPages, CartPages, RegistrationPages, SearchPages
from utils.data_loader import get_config, get_test_data, has_secret_file


_EBAY_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


PUBLIC_ENDPOINT_MAP = {
    "home": EndpointCase(path="", required_text="Electronics"),
    "search_laptop": EndpointCase(path="/sch/i.html?_nkw=laptop", required_text="s-item"),
    "search_iphone": EndpointCase(path="/sch/i.html?_nkw=iPhone", required_text="s-item"),
}

SEARCH_QUERY_MAP = {
    "iphone": SearchCase(query="iPhone", expected_names=("iPhone",), min_cards=1),
    "laptop": SearchCase(query="laptop", expected_names=("laptop",), min_cards=1),
}


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------

@pytest.fixture
def api_base_url() -> str:
    return get_config()["base_url"]


@pytest.fixture
def session(api_base_url: str) -> RestClient:
    """Fresh HTTP session per test, warming up with eBay."""
    client = RestClient(headers=_EBAY_HEADERS)
    client.get(api_base_url)
    yield client
    client.close()


# ---------------------------------------------------------------------------
# eBay API service fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ebay_search_service(page) -> EbaySearchService:
    service = EbaySearchService(page)
    probe = service.search("laptop")
    if probe.status_code == HTTP_FORBIDDEN:
        pytest.skip("eBay blocked automated search requests with HTTP 403")
    if probe.status_code != HTTP_OK:
        pytest.skip(f"eBay search probe returned HTTP {probe.status_code}")
    return service


# ---------------------------------------------------------------------------
# Page object fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def home_page(page, app_url: str) -> HomePage:
    return HomePage(page, app_url)


@pytest.fixture
def login_page(page, app_url: str) -> LoginPage:
    return LoginPage(page, app_url)


@pytest.fixture
def register_page(page, app_url: str) -> RegisterPage:
    return RegisterPage(page, app_url)


@pytest.fixture
def search_results_page(page, app_url: str) -> SearchResultsPage:
    return SearchResultsPage(page, app_url)


@pytest.fixture
def cart_page(page, app_url: str) -> CartPage:
    return CartPage(page, app_url)


@pytest.fixture
def search_pages(search_results_page: SearchResultsPage) -> SearchPages:
    return SearchPages(search_results=search_results_page)


@pytest.fixture
def cart_flow_pages(
    search_results_page: SearchResultsPage, cart_page: CartPage
) -> CartFlowPages:
    return CartFlowPages(search_results=search_results_page, cart=cart_page)


@pytest.fixture
def cart_pages(cart_page: CartPage) -> CartPages:
    return CartPages(cart=cart_page)


@pytest.fixture
def registration_pages(
    home_page: HomePage, register_page: RegisterPage
) -> RegistrationPages:
    return RegistrationPages(home=home_page, register=register_page)


# ---------------------------------------------------------------------------
# Data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def registration_data() -> dict:
    """
    Return registration test data, skipping if secrets or required fields are
    missing.  Centralises skip logic so tests stay free of guard conditions.
    """
    if not has_secret_file():
        pytest.skip("Registration secrets are not configured")
    data = get_test_data("registration")
    required_fields = ("email", "password", "confirm_password")
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        pytest.skip(f"Registration test data missing required fields: {missing}")
    return data


@pytest.fixture
def api_cart(ebay_search_service: EbaySearchService):
    """eBay equivalent: returns items found via search (no session cart)."""
    resp = ebay_search_service.search("iPhone")
    ids = ebay_search_service.item_ids(resp.text)
    prices = ebay_search_service.item_prices(resp.text)
    data = get_test_data()
    max_total = data.get("cart", {}).get("max_total", 5000.0)
    max_price = data.get("search", {}).get("max_price", 800.0)
    return ids[:5], prices[:5], max_total, max_price
