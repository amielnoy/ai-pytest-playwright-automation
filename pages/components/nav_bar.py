from playwright.sync_api import Page, expect

from pages.components.base_component import BaseComponent


class NavBarComponent(BaseComponent):
    _CURRENCY_DROPDOWN = "button.btn-link.dropdown-toggle:has(strong)"
    _SEARCH_INPUT = "input[name='search']"
    _SEARCH_BUTTON = "button.btn-default[type='button']"
    _MY_ACCOUNT = "a[title='My Account']"
    _LOGIN_LINK = "a:text-is('Login')"
    _REGISTER_LINK = "a:text-is('Register')"
    _LOGOUT_LINK = "a:text-is('Logout')"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def search(self, query: str) -> None:
        self.page.locator(self._SEARCH_INPUT).fill(query)
        self.page.locator(self._SEARCH_BUTTON).click()
        self.page.wait_for_load_state("domcontentloaded")

    def has_currency_dropdown(self) -> bool:
        return self.page.locator(self._CURRENCY_DROPDOWN).is_visible()

    def go_to_login(self) -> None:
        self._open_account_menu_and_click(self._LOGIN_LINK)

    def go_to_register(self) -> None:
        self._open_account_menu_and_click(self._REGISTER_LINK)

    def logout(self) -> None:
        self._open_account_menu_and_click(self._LOGOUT_LINK)

    def is_logged_in(self) -> bool:
        # The dropdown items are always in the DOM; no click needed to check state.
        return self.page.locator(self._LOGOUT_LINK).count() > 0

    def _open_account_menu_and_click(self, link_selector: str) -> None:
        self.page.locator(self._MY_ACCOUNT).click()
        link = self.page.locator(link_selector)
        expect(link).to_be_visible()
        link.click()
