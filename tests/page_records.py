from dataclasses import dataclass

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.register_page import RegisterPage
from pages.search_results_page import SearchResultsPage


@dataclass(frozen=True)
class SearchPages:
    search_results: SearchResultsPage


@dataclass(frozen=True)
class CartFlowPages:
    search_results: SearchResultsPage
    cart: CartPage


@dataclass(frozen=True)
class CartPages:
    cart: CartPage


@dataclass(frozen=True)
class RegistrationPages:
    home: HomePage
    register: RegisterPage
