import allure
import pytest
import pytest_check as check

from flows.cart_flow import CartFlow
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from pages.register_page import RegisterPage
from pages.search_results_page import SearchResultsPage


@allure.feature("Search")
@allure.story("Search result data integrity")
@pytest.mark.search
class TestSearchDataIntegrity:

    @allure.title("All MacBook search results have positive prices")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_results_have_positive_prices(
        self, search_results_page: SearchResultsPage
    ):
        with allure.step("Fetch MacBook products with high price ceiling"):
            products = search_results_page.get_products_under_price(
                query="MacBook", max_price=9999.0, limit=10
            )

        allure.attach(
            "\n".join(f"{p.name} — ${p.price}" for p in products),
            name="MacBook products",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Verify at least one result and all prices are positive"):
            assert products, "Expected MacBook search results"  # hard: prerequisite
            for product in products:
                check.greater(product.price, 0,
                    f"Non-positive price ${product.price} for '{product.name}'")

    @allure.title("Sort by Name Z-A produces results in descending order")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sort_name_descending(
        self, home_page: HomePage, search_results_page: SearchResultsPage
    ):
        with allure.step("Search for iPod from the home page"):
            home_page.open()
            home_page.search("iPod")

        with allure.step("Switch to list view and sort Name (Z - A)"):
            search_results_page.choose_list_view()
            search_results_page.sort_by_name_descending()

        with allure.step("Verify product names are in descending alphabetical order"):
            names = search_results_page.product_names()
            allure.attach(
                "\n".join(names),
                name="Sorted product names (Z-A)",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert names, "Expected iPod search results"
            assert search_results_page.are_product_names_sorted_descending(), (
                f"Expected descending order, got: {names}"
            )


@allure.feature("Cart")
@allure.story("Cart flow coverage")
@pytest.mark.cart
class TestCartFlowCoverage:

    @allure.title("Cart total is positive after adding items via CartFlow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_total_positive_after_adding_items(self, cart_flow: CartFlow):
        with allure.step("Add MacBook items under $700 to cart"):
            added = cart_flow.add_products_by_search(
                query="MacBook", max_price=700.0, limit=3
            )
            assert added, "No products were added to the cart"

        with allure.step("Open cart and verify total is greater than zero"):
            cart = cart_flow.open_cart()
            total = cart.get_cart_total()
            allure.attach(
                f"Cart total: ${total:.2f}",
                name="Cart total",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert total > 0, f"Expected positive cart total, got ${total:.2f}"

    @allure.title("Adding exactly one product results in one cart item")
    @allure.severity(allure.severity_level.NORMAL)
    def test_single_product_limit_yields_one_cart_item(self, cart_flow: CartFlow):
        with allure.step("Add at most 1 MacBook item to cart"):
            added = cart_flow.add_products_by_search(
                query="MacBook", max_price=9999.0, limit=1
            )
            assert len(added) == 1, f"Expected 1 product added, got {len(added)}"

        with allure.step("Open cart and verify item count is 1"):
            cart = cart_flow.open_cart()
            assert not cart.is_empty(), "Cart is unexpectedly empty"
            assert cart.get_item_count() == 1, (
                f"Expected 1 cart item, got {cart.get_item_count()}"
            )


@allure.feature("Navigation")
@allure.story("Page routing and form controls")
@pytest.mark.sanity
class TestNavigationCoverage:

    @allure.title("Home nav leads to register page at the correct URL")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_page_accessible_via_home_nav(
        self, home_page: HomePage, register_page: RegisterPage
    ):
        with allure.step("Open home page and navigate to Register via the account menu"):
            home_page.open()
            home_page.go_to_register()

        with allure.step("Verify the register page URL is correct"):
            assert "route=account/register" in register_page.url, (
                f"Unexpected register URL: {register_page.url}"
            )

    @allure.title("Submitting empty login credentials shows a danger warning")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_empty_credentials_shows_warning(self, login_page: LoginPage):
        with allure.step("Open the login page"):
            login_page.open()

        with allure.step("Submit form with empty email and password"):
            login_page.login(email="", password="")

        with allure.step("Verify login fails with a danger warning"):
            assert not login_page.is_login_successful(), (
                "Login should not succeed with empty credentials"
            )
            assert login_page.has_invalid_credentials_warning(), (
                "Expected danger warning for empty credentials"
            )


@allure.feature("Product Detail")
@allure.story("Product detail page essentials")
@pytest.mark.sanity
class TestProductDetailCoverage:

    @allure.title("iPhone product detail page shows heading and add-to-cart button")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_iphone_product_detail_has_essentials(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        product_detail_page: ProductDetailPage,
    ):
        with allure.step("Search for iPhone from the home page"):
            home_page.open()
            home_page.search("iPhone")

        with allure.step("Open the iPhone product from search results"):
            search_results_page.open_product("iPhone")

        with allure.step("Verify product detail essentials are present"):
            assert product_detail_page.has_product_heading("iPhone"), (
                "iPhone product heading not visible"
            )
            assert product_detail_page.has_add_to_cart_button(), (
                "Add to Cart button not visible on iPhone detail page"
            )

    @allure.title("MacBook reviews tab exposes the review form fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_reviews_tab_exposes_form_fields(
        self,
        home_page: HomePage,
        search_results_page: SearchResultsPage,
        product_detail_page: ProductDetailPage,
    ):
        with allure.step("Search for MacBook and open the product detail page"):
            home_page.open()
            home_page.search("MacBook")
            search_results_page.open_product("MacBook")

        with allure.step("Click the Reviews tab"):
            product_detail_page.open_reviews_tab()

        with allure.step("Verify review form fields are visible"):
            assert product_detail_page.has_review_form_fields(), (
                "Expected review form fields (Name, Review, Qty) to be visible"
            )


@allure.feature("Search")
@allure.story("Stored product data completeness")
@pytest.mark.search
class TestStoredProductData:

    @allure.title("Stored iPod products all have non-empty picture URLs")
    @allure.severity(allure.severity_level.NORMAL)
    def test_stored_products_have_picture_urls(
        self, home_page: HomePage, search_results_page: SearchResultsPage
    ):
        with allure.step("Search for iPod and switch to list view"):
            home_page.open()
            home_page.search("iPod")
            search_results_page.choose_list_view()

        with allure.step("Read stored product information"):
            products = search_results_page.stored_product_information()
            assert products, "Expected iPod search results"

        allure.attach(
            "\n".join(p.picture_url for p in products),
            name="Product picture URLs",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("Verify every product has a non-empty picture URL"):
            for product in products:
                check.is_true(product.picture_url,
                    f"Empty picture URL for '{product.name}'")

    @allure.title("Stored iPod products all have non-empty descriptions")
    @allure.severity(allure.severity_level.NORMAL)
    def test_stored_products_have_descriptions(
        self, home_page: HomePage, search_results_page: SearchResultsPage
    ):
        with allure.step("Search for iPod and switch to list view"):
            home_page.open()
            home_page.search("iPod")
            search_results_page.choose_list_view()

        with allure.step("Read stored product information"):
            products = search_results_page.stored_product_information()
            assert products, "Expected iPod search results"

        with allure.step("Verify every product has a non-empty description"):
            for product in products:
                check.is_true(product.description.strip(),
                    f"Empty description for '{product.name}'")
