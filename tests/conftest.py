import pytest

from flows.cart_flow import CartFlow
from flows.login_flow import LoginFlow
from flows.registration_flow import RegistrationFlow
from flows.search_flow import SearchFlow
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from pages.register_page import RegisterPage
from pages.search_results_page import SearchResultsPage
from services.api.account_service import AccountService
from services.api.cart_service import CartService
from services.api.public_service import EndpointCase, PublicService
from services.api.search_service import SearchCase, SearchService
from services.rest_client import RestClient
from tests.page_records import CartFlowPages, CartPages, RegistrationPages, SearchPages
from utils.api_client import build_session, create_cart
from utils.data_loader import get_config, get_test_data, has_secret_file


PUBLIC_ENDPOINT_MAP = {
    "home": EndpointCase(path="", required_text="Your Store"),
    "search": EndpointCase(
        path="/index.php?route=product/search&search=MacBook",
        required_text="MacBook",
    ),
    "cart": EndpointCase(
        path="/index.php?route=checkout/cart",
        required_text="Shopping Cart",
    ),
    "register": EndpointCase(
        path="/index.php?route=account/register",
        required_text="Register Account",
    ),
    "login": EndpointCase(
        path="/index.php?route=account/login",
        required_text="Returning Customer",
    ),
}

SEARCH_QUERY_MAP = {
    "macbook": SearchCase(
        query="MacBook",
        expected_names=("MacBook",),
        min_cards=1,
    ),
    "iphone": SearchCase(
        query="iPhone",
        expected_names=("iPhone",),
        min_cards=1,
    ),
}


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------

@pytest.fixture
def api_base_url() -> str:
    return get_config()["base_url"]


@pytest.fixture
def session(api_base_url: str) -> RestClient:
    """Fresh HTTP session per test: own OCSESSID, no shared cart state."""
    client = build_session()
    client.get(api_base_url)
    yield client
    client.close()


# ---------------------------------------------------------------------------
# API service fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def public_service(session: RestClient, api_base_url: str) -> PublicService:
    return PublicService(session, api_base_url)


@pytest.fixture
def search_service(session: RestClient, api_base_url: str) -> SearchService:
    return SearchService(session, api_base_url)


@pytest.fixture
def cart_service(session: RestClient, api_base_url: str) -> CartService:
    return CartService(session, api_base_url)


@pytest.fixture
def account_service(session: RestClient, api_base_url: str) -> AccountService:
    return AccountService(session, api_base_url)


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
def product_detail_page(page, app_url: str) -> ProductDetailPage:
    return ProductDetailPage(page, app_url)


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
# Flow fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def login_flow(home_page: HomePage, login_page: LoginPage) -> LoginFlow:
    return LoginFlow(home_page, login_page)


@pytest.fixture
def registration_flow(home_page: HomePage, register_page: RegisterPage) -> RegistrationFlow:
    return RegistrationFlow(home_page, register_page)


@pytest.fixture
def search_flow(home_page: HomePage, search_results_page: SearchResultsPage) -> SearchFlow:
    return SearchFlow(home_page, search_results_page)


@pytest.fixture
def cart_flow(search_results_page: SearchResultsPage, cart_page: CartPage) -> CartFlow:
    return CartFlow(search_results_page, cart_page)


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
def api_cart(app_url: str):
    """
    Populate a cart via the OpenCart REST API (no browser) and return the
    server session cookie plus the products that were added.

    Each call gets its own OCSESSID so parallel workers never share
    server-side cart state.  The caller must inject the cookie into the
    Playwright BrowserContext *before* navigating to the cart page:

        context.add_cookies([{"name": "OCSESSID", "value": ocsessid, "url": app_url}])
    """
    data = get_test_data()
    search = data["search"]
    # create_cart raises ValueError when no products match — no need to assert.
    ocsessid, products = create_cart(
        base_url=app_url,
        query=search["query"],
        max_price=search["max_price"],
        limit=search["limit"],
    )
    return ocsessid, products, data["cart"]["max_total"], search["max_price"]
