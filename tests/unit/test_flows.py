"""Unit tests for flows/ — LoginFlow, RegistrationFlow, SearchFlow, CartFlow.

Each flow is pure delegation to page objects, so the tests use MagicMock to
verify the exact calls made and that return values are forwarded correctly.
No browser, network, or fixtures required.
"""
from unittest.mock import MagicMock, call

import allure
import pytest

from flows.cart_flow import CartFlow
from flows.login_flow import LoginFlow
from flows.registration_flow import RegistrationFlow
from flows.search_flow import SearchFlow
from pages.models import ProductInfo


# ---------------------------------------------------------------------------
# LoginFlow
# ---------------------------------------------------------------------------

@allure.feature("Flows")
@allure.story("LoginFlow")
class TestLoginFlow:

    def _make(self):
        home = MagicMock()
        login_page = MagicMock()
        return LoginFlow(home, login_page), home, login_page

    @allure.title("login() opens home → navigates to login → submits credentials")
    def test_login_call_sequence(self):
        flow, home, login_page = self._make()
        flow.login("user@example.com", "secret")
        home.open.assert_called_once()
        home.go_to_login.assert_called_once()
        login_page.login.assert_called_once_with("user@example.com", "secret")

    @allure.title("login() returns the result of is_login_successful()")
    def test_login_returns_success_flag(self):
        flow, home, login_page = self._make()
        login_page.is_login_successful.return_value = True
        assert flow.login("a@b.com", "pw") is True

        login_page.is_login_successful.return_value = False
        assert flow.login("a@b.com", "pw") is False

    @allure.title("logout() delegates to home.logout()")
    def test_logout_delegates(self):
        flow, home, _ = self._make()
        flow.logout()
        home.logout.assert_called_once()

    @allure.title("login() calls home.open() before go_to_login() (ordering check)")
    def test_login_ordering(self):
        manager = MagicMock()
        manager.attach_mock(MagicMock(), "open")
        manager.attach_mock(MagicMock(), "go_to_login")

        home = MagicMock()
        login_page = MagicMock()
        call_order = []
        home.open.side_effect = lambda: call_order.append("open")
        home.go_to_login.side_effect = lambda: call_order.append("go_to_login")
        login_page.login.side_effect = lambda e, p: call_order.append("login")

        LoginFlow(home, login_page).login("e@mail.com", "pw")
        assert call_order == ["open", "go_to_login", "login"]


# ---------------------------------------------------------------------------
# RegistrationFlow
# ---------------------------------------------------------------------------

@allure.feature("Flows")
@allure.story("RegistrationFlow")
class TestRegistrationFlow:

    def _make(self):
        home = MagicMock()
        register_page = MagicMock()
        return RegistrationFlow(home, register_page), home, register_page

    @allure.title("register() opens home → navigates to register → submits form fields")
    def test_register_call_sequence(self):
        flow, home, page = self._make()
        flow.register(
            first_name="Alice", last_name="Smith", email="a@b.com",
            telephone="0501234567", password="Secure1!", confirm_password="Secure1!",
        )
        home.open.assert_called_once()
        home.go_to_register.assert_called_once()
        page.register.assert_called_once_with(
            first_name="Alice", last_name="Smith", email="a@b.com",
            telephone="0501234567", password="Secure1!", confirm_password="Secure1!",
            newsletter=False,
        )

    @allure.title("register() passes newsletter=True when requested")
    def test_register_newsletter_forwarded(self):
        flow, _, page = self._make()
        flow.register(
            first_name="A", last_name="B", email="a@b.com",
            telephone="0500000000", password="pw", confirm_password="pw",
            newsletter=True,
        )
        _, kwargs = page.register.call_args
        assert kwargs["newsletter"] is True

    @allure.title("register() returns the result of is_registration_successful()")
    def test_register_returns_success_flag(self):
        flow, _, page = self._make()
        page.is_registration_successful.return_value = True
        assert flow.register(
            first_name="A", last_name="B", email="a@b.com",
            telephone="0500000000", password="pw", confirm_password="pw",
        ) is True

    @allure.title("get_error_message() delegates to register_page.get_error_message()")
    def test_get_error_message_delegates(self):
        flow, _, page = self._make()
        page.get_error_message.return_value = "Email already registered"
        assert flow.get_error_message() == "Email already registered"
        page.get_error_message.assert_called_once()


# ---------------------------------------------------------------------------
# SearchFlow
# ---------------------------------------------------------------------------

@allure.feature("Flows")
@allure.story("SearchFlow")
class TestSearchFlow:

    def _make(self):
        home = MagicMock()
        results = MagicMock()
        return SearchFlow(home, results), home, results

    @allure.title("search() opens home → submits query → returns results page")
    def test_search_call_sequence(self):
        flow, home, results = self._make()
        returned = flow.search("MacBook")
        home.open.assert_called_once()
        home.search.assert_called_once_with("MacBook")
        assert returned is results

    @allure.title("search_under_price() delegates to results.get_products_under_price()")
    def test_search_under_price_delegates(self):
        flow, _, results = self._make()
        fake_products = [MagicMock(spec=ProductInfo)]
        results.get_products_under_price.return_value = fake_products
        out = flow.search_under_price("iPhone", 200.0, limit=3)
        results.get_products_under_price.assert_called_once_with("iPhone", 200.0, 3)
        assert out is fake_products

    @allure.title("search_under_price() uses default limit=5 when omitted")
    def test_search_under_price_default_limit(self):
        flow, _, results = self._make()
        results.get_products_under_price.return_value = []
        flow.search_under_price("Samsung", 500.0)
        results.get_products_under_price.assert_called_once_with("Samsung", 500.0, 5)

    @allure.title("search() does not call results.get_products_under_price()")
    def test_search_does_not_call_filter(self):
        flow, _, results = self._make()
        flow.search("Canon")
        results.get_products_under_price.assert_not_called()


# ---------------------------------------------------------------------------
# CartFlow
# ---------------------------------------------------------------------------

@allure.feature("Flows")
@allure.story("CartFlow")
class TestCartFlow:

    def _make(self):
        results = MagicMock()
        cart = MagicMock()
        return CartFlow(results, cart), results, cart

    @allure.title("add_products_by_search() searches under price then adds items to cart")
    def test_add_products_call_sequence(self):
        flow, results, _ = self._make()
        fake_products = [MagicMock(spec=ProductInfo), MagicMock(spec=ProductInfo)]
        results.get_products_under_price.return_value = fake_products
        results.add_items_to_cart.return_value = ["MacBook", "iPhone"]

        names = flow.add_products_by_search("MacBook", max_price=700.0, limit=2)

        results.get_products_under_price.assert_called_once_with("MacBook", 700.0, 2)
        results.add_items_to_cart.assert_called_once_with(fake_products)
        assert names == ["MacBook", "iPhone"]

    @allure.title("add_products_by_search() uses default limit=5 when omitted")
    def test_add_products_default_limit(self):
        flow, results, _ = self._make()
        results.get_products_under_price.return_value = []
        results.add_items_to_cart.return_value = []
        flow.add_products_by_search("iPhone", max_price=200.0)
        results.get_products_under_price.assert_called_once_with("iPhone", 200.0, 5)

    @allure.title("open_cart() opens cart with min_items=1 and returns the cart page")
    def test_open_cart_delegates(self):
        flow, _, cart = self._make()
        result = flow.open_cart()
        cart.open.assert_called_once_with(min_items=1)
        assert result is cart

    @allure.title("open_cart() forwards min_items override to cart.open()")
    def test_open_cart_custom_min_items(self):
        flow, _, cart = self._make()
        flow.open_cart(min_items=3)
        cart.open.assert_called_once_with(min_items=3)
