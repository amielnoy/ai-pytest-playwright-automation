"""Session 10 — LoginPage."""
from __future__ import annotations
from typing import TYPE_CHECKING
from playwright.sync_api import Page, expect
from .base_page import BasePage

if TYPE_CHECKING:
    from .inventory_page import InventoryPage


class LoginPage(BasePage):
    _USERNAME_PLACEHOLDER = "Username"
    _PASSWORD_PLACEHOLDER = "Password"
    _LOGIN_BUTTON_ROLE = "button"
    _LOGIN_BUTTON_NAME = "Login"
    _ERROR_SELECTOR = '[data-test="error"]'

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self._username = page.get_by_placeholder(self._USERNAME_PLACEHOLDER)
        self._password = page.get_by_placeholder(self._PASSWORD_PLACEHOLDER)
        self._login_btn = page.get_by_role(self._LOGIN_BUTTON_ROLE, name=self._LOGIN_BUTTON_NAME)
        self._error = page.locator(self._ERROR_SELECTOR)

    def open(self) -> "LoginPage":
        self.navigate("/")
        return self

    def login(self, username: str, password: str) -> InventoryPage:
        from .inventory_page import InventoryPage
        self._username.fill(username)
        self._password.fill(password)
        self._login_btn.click()
        return InventoryPage(self.page, self.base_url)

    def expect_error(self, text: str) -> "LoginPage":
        expect(self._error).to_contain_text(text)
        return self
