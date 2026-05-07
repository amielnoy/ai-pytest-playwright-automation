"""
Session 4 — Advanced Playwright: POM + UI + API
LoginPage encapsulates all login-screen interactions.
"""

from playwright.sync_api import Page, expect
from .base_page import BasePage
from .inventory_page import InventoryPage


class LoginPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.login_btn = page.get_by_role("button", name="Login")
        self.error = page.locator('[data-test="error"]')

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
