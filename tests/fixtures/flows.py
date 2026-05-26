"""Flow fixtures — high-level UI flow objects composed from page objects."""
import pytest

from flows.cart_flow import CartFlow
from flows.login_flow import LoginFlow
from flows.registration_flow import RegistrationFlow
from flows.search_flow import SearchFlow
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.search_results_page import SearchResultsPage


@pytest.fixture
def login_flow(home_page: HomePage, login_page: LoginPage) -> LoginFlow:
    return LoginFlow(home_page, login_page)


@pytest.fixture
def registration_flow(
    home_page: HomePage, register_page: RegisterPage
) -> RegistrationFlow:
    return RegistrationFlow(home_page, register_page)


@pytest.fixture
def search_flow(
    home_page: HomePage, search_results_page: SearchResultsPage
) -> SearchFlow:
    return SearchFlow(home_page, search_results_page)


@pytest.fixture
def cart_flow(
    search_results_page: SearchResultsPage, cart_page: CartPage
) -> CartFlow:
    return CartFlow(search_results_page, cart_page)
