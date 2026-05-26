"""Page object fixtures — one fixture per page class and page record bundle."""
import pytest

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from pages.register_page import RegisterPage
from pages.search_results_page import SearchResultsPage
from tests.page_records import CartFlowPages, CartPages, RegistrationPages, SearchPages


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
