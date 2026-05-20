from playwright.sync_api import Locator, Page, expect

from pages.components.base_component import BaseComponent
from pages.self_healing import healing_locator


class NavBarComponent(BaseComponent):
    _SEARCH_PLACEHOLDER = "Search"
    _SEARCH_CONTAINER = "#search"
    _SEARCH_BUTTON_ROLE = "button"
    _CURRENCY_BUTTON_ROLE = "button"
    _CURRENCY_BUTTON_NAME = "Currency"
    _EMPTY_CART_BUTTON_ROLE = "button"
    _EMPTY_CART_BUTTON_NAME = "0 item(s) - $0.00"
    _ACCOUNT_LINK_ROLE = "link"
    _ACCOUNT_LINK_NAME = "My Account"
    _LOGIN_LINK_NAME = "Login"
    _REGISTER_LINK_NAME = "Register"
    _LOGOUT_LINK_NAME = "Logout"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_input = page.get_by_placeholder(self._SEARCH_PLACEHOLDER)
        self.search_container = healing_locator(
            page.locator(self._SEARCH_CONTAINER),
            name="header search container",
            primary_label=self._SEARCH_CONTAINER,
            fallbacks=[
                ("[class*='search']", page.locator("[class*='search']")),
            ],
            events=self._self_heal_events,
        )
        self.currency_dropdown = page.get_by_role(
            self._CURRENCY_BUTTON_ROLE, name=self._CURRENCY_BUTTON_NAME
        )
        self.empty_cart_summary = page.get_by_role(
            self._EMPTY_CART_BUTTON_ROLE, name=self._EMPTY_CART_BUTTON_NAME
        )
        self.account_menu = page.get_by_role(
            self._ACCOUNT_LINK_ROLE, name=self._ACCOUNT_LINK_NAME
        )
        self.login_link = page.get_by_role(
            self._ACCOUNT_LINK_ROLE, name=self._LOGIN_LINK_NAME
        )
        self.register_link = page.get_by_role(
            self._ACCOUNT_LINK_ROLE, name=self._REGISTER_LINK_NAME
        )
        self.logout_link = page.get_by_role(
            self._ACCOUNT_LINK_ROLE, name=self._LOGOUT_LINK_NAME
        )

    def search(self, query: str) -> None:
        self.search_input.fill(query)
        self.search_container.get_by_role(self._SEARCH_BUTTON_ROLE).click()
        self.page.wait_for_load_state("domcontentloaded")

    def has_currency_dropdown(self) -> bool:
        return self.currency_dropdown.is_visible()

    def has_search_input(self) -> bool:
        return self.search_input.is_visible()

    def has_empty_cart_summary(self) -> bool:
        return self.empty_cart_summary.is_visible()

    def has_account_menu(self) -> bool:
        return self.account_menu.first.is_visible()

    def go_to_login(self) -> None:
        self._open_account_menu_and_click(self.login_link)

    def go_to_register(self) -> None:
        self._open_account_menu_and_click(self.register_link)

    def logout(self) -> None:
        self._open_account_menu_and_click(self.logout_link)

    def is_logged_in(self) -> bool:
        return self.logout_link.count() > 0

    def _open_account_menu_and_click(self, link: Locator) -> None:
        self.account_menu.first.click()
        expect(link).to_be_visible()
        link.click()
        self.page.wait_for_load_state("domcontentloaded")
