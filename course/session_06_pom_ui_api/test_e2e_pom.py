"""
Session 6 — Advanced Playwright: POM + UI + API
E2E tests using the Page Object Model with Fluent API.
"""

from playwright.sync_api import Page, APIRequestContext
from .login_page import LoginPage

BASE_URL = "https://www.saucedemo.com"


def test_add_to_cart_via_pom(page: Page):
    inventory = LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")
    inventory.add_first_item().expect_cart_count(1)


def test_locked_out_user_shows_error(page: Page):
    login = LoginPage(page, BASE_URL).open()
    login.login("locked_out_user", "secret_sauce")
    login.expect_error("locked out")


def test_create_user_via_api_then_verify(playwright):
    api: APIRequestContext = playwright.request.new_context(base_url="https://reqres.in")
    response = api.post("/api/users", data={"name": "Amiel", "job": "QA"})
    assert response.status == 201
    body = response.json()
    assert body["name"] == "Amiel"
    assert body["job"] == "QA"
    api.dispose()


def test_full_checkout_flow(page: Page):
    from .data_factory import make_checkout_info

    inventory = LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")
    cart = inventory.add_first_item().go_to_cart()
    cart.expect_item_count(1)

    info = make_checkout_info()
    cart.proceed_to_checkout().fill_info(info).continue_to_overview().finish().expect_order_complete()


def test_checkout_missing_first_name_shows_error(page: Page):
    from .data_factory import make_incomplete_checkout_info

    inventory = LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")
    cart = inventory.add_first_item().go_to_cart()

    info = make_incomplete_checkout_info("first_name")
    cart.proceed_to_checkout().fill_info(info).continue_to_overview().expect_info_error("First Name is required")


def test_sort_products_name_ascending(page: Page):
    inventory = LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")
    inventory.sort_by("az")
    names = inventory.product_names()
    assert names == sorted(names), f"Names not sorted A→Z: {names}"


def test_add_specific_product_by_name(page: Page):
    inventory = LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")
    inventory.add_item_by_name("Sauce Labs Backpack").expect_cart_count(1)


def test_get_list_users_via_api(playwright):
    api: APIRequestContext = playwright.request.new_context(base_url="https://reqres.in")
    response = api.get("/api/users?page=1")
    assert response.status == 200
    body = response.json()
    assert "data" in body
    assert len(body["data"]) > 0
    for user in body["data"]:
        assert "id" in user
        assert "email" in user
    api.dispose()
