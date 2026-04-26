from playwright.sync_api import Page
from pages.components.base_component import BaseComponent


class NavBarComponent(BaseComponent):
    _SEARCH_INPUT = "input[name='search']"
    _SEARCH_BUTTON = "button.btn-default[type='button']"
    _MY_ACCOUNT = "a[title='My Account']"
    _LOGIN_LINK = "//a[text()='Login']"
    _REGISTER_LINK = "//a[text()='Register']"
    _LOGOUT_LINK = "//a[text()='Logout']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def search(self, query: str) -> None:
        self.page.fill(self._SEARCH_INPUT, query)
        self.page.click(self._SEARCH_BUTTON)
        self.page.wait_for_load_state("networkidle")

    def go_to_login(self) -> None:
        self._open_account_menu_and_click(self._LOGIN_LINK)

    def go_to_register(self) -> None:
        self._open_account_menu_and_click(self._REGISTER_LINK)

    def logout(self) -> None:
        self._open_account_menu_and_click(self._LOGOUT_LINK)

    def is_logged_in(self) -> bool:
        self.page.click(self._MY_ACCOUNT)
        visible = self.page.locator(self._LOGOUT_LINK).is_visible()
        self.page.keyboard.press("Escape")
        return visible

    def _open_account_menu_and_click(self, link_selector: str) -> None:
        self.page.click(self._MY_ACCOUNT)
        self.page.click(link_selector)
        self.page.wait_for_load_state("networkidle")
