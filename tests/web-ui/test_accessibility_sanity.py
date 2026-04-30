import allure
import pytest


@allure.feature("Accessibility")
@allure.story("Sanity accessibility checks")
@pytest.mark.sanity
@pytest.mark.accessibility
class TestAccessibilitySanity:

    @allure.title("Home page declares English document language")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_home_page_declares_language(self, home_page):
        home_page.open()

        assert home_page.document_language() == "en"

    @allure.title("Home page critical header controls have accessible names")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_home_header_controls_have_accessible_names(self, home_page):
        home_page.open()

        assert home_page.has_header_accessible_controls()

    @allure.title("Home featured product images expose alt text")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_home_featured_product_images_have_alt_text(self, home_page):
        home_page.open()

        missing_alt = home_page.visible_featured_images_missing_alt()

        assert missing_alt == []

    @allure.title("Login form fields have programmatic labels")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_form_fields_have_programmatic_labels(self, login_page):
        login_page.open()

        assert login_page.has_accessible_login_controls()

    @allure.title("Invalid login warning is exposed as visible text")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_login_warning_is_visible_text(self, login_page):
        login_page.open()

        login_page.login("accessibility_invalid@example.com", "bad-password")

        assert login_page.has_invalid_credentials_warning_text()

    @allure.title("Registration required fields have programmatic labels")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_required_fields_have_programmatic_labels(
        self, home_page, register_page
    ):
        home_page.open()
        home_page.go_to_register()

        assert register_page.has_required_field_labels()

    @allure.title("Registration newsletter radios have accessible names")
    @allure.severity(allure.severity_level.NORMAL)
    def test_registration_newsletter_radios_have_accessible_names(
        self, home_page, register_page
    ):
        home_page.open()
        home_page.go_to_register()

        assert register_page.has_newsletter_options()

    @allure.title("Search page filter controls have labels")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_page_filter_controls_have_labels(
        self, home_page, search_results_page
    ):
        home_page.open()
        home_page.search("MacBook")

        assert search_results_page.has_filter_controls()

    @allure.title("Search results product title links have accessible names")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_result_product_links_have_accessible_names(
        self, home_page, search_results_page
    ):
        home_page.open()
        home_page.search("MacBook")

        product_names = search_results_page.product_title_link_names()

        assert product_names
        assert all(name.strip() for name in product_names)

    @allure.title("Product detail form fields have labels")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_detail_fields_have_labels(
        self, home_page, search_results_page, product_detail_page
    ):
        home_page.open()
        home_page.search("MacBook")
        search_results_page.open_product("MacBook")
        product_detail_page.open_reviews_tab()

        assert product_detail_page.has_review_form_fields()
        assert product_detail_page.duplicate_ids() == []
