from playwright.sync_api import Page
from pages.base_page import BasePage


class HomePage(BasePage):
    # Locators
    _SEARCH_INPUT = "input[name='search']"
    _SEARCH_BUTTON = "button.btn-default[type='button']"
    _MY_ACCOUNT_MENU = "a[title='My Account']"
    _LOGIN_LINK = "//a[text()='Login']"
    _REGISTER_LINK = "//a[text()='Register']"
    _LOGOUT_LINK = "//a[text()='Logout']"
    _CART_BUTTON = "#cart > button"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self):
        self.navigate()
        self.page.wait_for_load_state("networkidle")
        return self

    def search(self, query: str):
        self.page.fill(self._SEARCH_INPUT, query)
        self.page.click(self._SEARCH_BUTTON)
        self.page.wait_for_load_state("networkidle")

    def go_to_login(self):
        self.page.click(self._MY_ACCOUNT_MENU)
        self.page.click(self._LOGIN_LINK)
        self.page.wait_for_load_state("networkidle")

    def go_to_register(self):
        self.page.click(self._MY_ACCOUNT_MENU)
        self.page.click(self._REGISTER_LINK)
        self.page.wait_for_load_state("networkidle")

    def logout(self):
        self.page.click(self._MY_ACCOUNT_MENU)
        self.page.click(self._LOGOUT_LINK)
        self.page.wait_for_load_state("networkidle")

    def is_logged_in(self) -> bool:
        self.page.click(self._MY_ACCOUNT_MENU)
        visible = self.page.locator(self._LOGOUT_LINK).is_visible()
        self.page.keyboard.press("Escape")
        return visible
