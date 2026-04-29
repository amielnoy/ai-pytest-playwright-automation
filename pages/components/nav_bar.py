from playwright.sync_api import Locator, expect

from pages.components.base_component import BaseComponent


class NavBarComponent(BaseComponent):
    _CURRENCY_DROPDOWN = "button.btn-link.dropdown-toggle:has(strong)"
    _SEARCH_INPUT = "input[name='search']"
    _SEARCH_BUTTON = "button.btn-default[type='button']"

    def search(self, query: str) -> None:
        self.page.locator(self._SEARCH_INPUT).fill(query)
        self.page.locator(self._SEARCH_BUTTON).click()
        self.page.wait_for_load_state("domcontentloaded")

    def has_currency_dropdown(self) -> bool:
        return self.page.locator(self._CURRENCY_DROPDOWN).is_visible()

    def go_to_login(self) -> None:
        self._open_account_menu_and_click(self.page.get_by_role("link", name="Login"))

    def go_to_register(self) -> None:
        self._open_account_menu_and_click(self.page.get_by_role("link", name="Register"))

    def logout(self) -> None:
        self._open_account_menu_and_click(self.page.get_by_role("link", name="Logout"))

    def is_logged_in(self) -> bool:
        return self.page.get_by_role("link", name="Logout").count() > 0

    def _open_account_menu_and_click(self, link: Locator) -> None:
        self.page.get_by_role("link", name="My Account").click()
        expect(link).to_be_visible()
        link.click()
