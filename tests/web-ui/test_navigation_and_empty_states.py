import allure
import pytest

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage


@allure.feature("Navigation")
@allure.story("Header navigation and empty states")
@pytest.mark.sanity
class TestNavigationAndEmptyStates:

    @allure.title("Header search submits the query and shows matching results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_header_search_submits_query_and_shows_matching_results(
        self, home_page: HomePage, search_results_page: SearchResultsPage
    ):
        with allure.step("Open home page and search for iPhone from the header"):
            home_page.open()
            home_page.search("iPhone")

        with allure.step("Verify search route, query, and matching product result"):
            assert "route=product/search" in search_results_page.url
            assert "search=iPhone" in search_results_page.url
            assert "iPhone" in search_results_page.product_names()

    @allure.title("Empty cart page exposes empty state without item rows")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_cart_page_shows_empty_state(self, cart_page: CartPage):
        with allure.step("Open cart with a fresh browser session"):
            cart_page.open()

        with allure.step("Verify empty-cart state, row count, and total"):
            assert cart_page.is_empty()
            assert cart_page.get_item_count() == 0
            assert cart_page.get_cart_total() == 0.0

    @allure.title("Account menu opens the login page from the home page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_account_menu_opens_login_page(
        self, home_page: HomePage, login_page: LoginPage
    ):
        with allure.step("Open home page and choose Login from My Account"):
            home_page.open()
            home_page.go_to_login()

        with allure.step("Verify login page route and accessible controls"):
            assert "route=account/login" in login_page.url
            assert login_page.has_accessible_login_controls()

    @allure.title("Switching search results to list view keeps products available")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_view_keeps_search_results_available(
        self, home_page: HomePage, search_results_page: SearchResultsPage
    ):
        with allure.step("Search for MacBook and capture product names"):
            home_page.open()
            home_page.search("MacBook")
            names_before = search_results_page.product_names()

        with allure.step("Switch to list view and verify products remain available"):
            search_results_page.choose_list_view()
            names_after = search_results_page.product_names()
            assert names_before
            assert names_after == names_before
