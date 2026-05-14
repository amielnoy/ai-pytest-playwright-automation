import allure
import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from pages.search_results_page import SearchResultsPage
from utils.data_loader import get_test_data


@allure.feature("Sanity")
@allure.story("Critical UI availability")
@pytest.mark.sanity
class TestSanity:

    @allure.title("Home page exposes the critical header controls")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_home_page_header_controls(self, home_page: HomePage):
        with allure.step("Open the TutorialsNinja demo store home page"):
            home_page.open()

        with allure.step("Verify page title and primary header controls are available"):
            assert home_page.title == "Your Store"
            assert home_page.has_currency_dropdown(), "Currency dropdown is not visible"
            assert home_page.has_search_input(), "Search input is not visible"
            assert home_page.has_empty_cart_summary(), "Empty cart summary is not visible"

    @allure.title("Invalid login keeps the user on login page with a warning")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("https://your-jira.atlassian.net/browse/TN-201", "TN-201")
    @allure.issue("https://your-jira.atlassian.net/browse/TN-BUG-8", "TN-BUG-8")
    def test_invalid_login_warning(self, login_page: LoginPage):
        with allure.step("Open account login page"):
            login_page.open()

        with allure.step("Submit invalid credentials"):
            sanity_data = get_test_data("sanity")
            login_page.login(
                email=sanity_data["invalid_email"],
                password=sanity_data["invalid_password"],
            )

        with allure.step("Verify login fails with the expected warning"):
            assert not login_page.is_login_successful()
            assert login_page.has_invalid_credentials_warning()

    @allure.title("Search result opens a product detail page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_detail_opens_from_search(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        product_detail_page: ProductDetailPage,
    ):
        with allure.step("Search for MacBook from the home page"):
            product = get_test_data("sanity")["search_product"]
            home_page.open()
            home_page.search(product)

        with allure.step("Open the MacBook product from search results"):
            search_results_page.open_product(product)

        with allure.step("Verify product detail essentials are visible"):
            assert product_detail_page.title == product
            assert product_detail_page.has_product_heading(product)
            assert product_detail_page.has_default_quantity()
            assert product_detail_page.has_add_to_cart_button()
