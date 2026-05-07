"""
Session 4 — Advanced Playwright: POM + UI + API
LoginPage encapsulates all login-screen interactions.
"""

from playwright.sync_api import Page, expect
from .base_page import BasePage
from .inventory_page import InventoryPage


class LoginPage(BasePage):
    _USERNAME_PLACEHOLDER = "Username"
    _PASSWORD_PLACEHOLDER = "Password"
    _LOGIN_BUTTON_ROLE = "button"
    _LOGIN_BUTTON_NAME = "Login"
    _ERROR_SELECTOR = '[data-test="error"]'

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.username = page.get_by_placeholder(self._USERNAME_PLACEHOLDER)
        self.password = page.get_by_placeholder(self._PASSWORD_PLACEHOLDER)
        self.login_btn = page.get_by_role(self._LOGIN_BUTTON_ROLE, name=self._LOGIN_BUTTON_NAME)
        self.error = page.locator(self._ERROR_SELECTOR)

    def open(self) -> "LoginPage":
        self.navigate("/")
        return self

    def login(self, username: str, password: str) -> InventoryPage:
        self.username.fill(username)
        self.password.fill(password)
        self.login_btn.click()
        return InventoryPage(self.page, self.base_url)

    def expect_error(self, text: str) -> "LoginPage":
        expect(self.error).to_contain_text(text)
        return self
