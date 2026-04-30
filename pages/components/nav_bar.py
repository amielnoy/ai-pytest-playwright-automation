from playwright.sync_api import Locator, expect

from pages.components.base_component import BaseComponent


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

    def search(self, query: str) -> None:
        self.page.get_by_placeholder(self._SEARCH_PLACEHOLDER).fill(query)
        self.page.locator(self._SEARCH_CONTAINER).get_by_role(
            self._SEARCH_BUTTON_ROLE
        ).click()
        self.page.wait_for_load_state("domcontentloaded")

    def has_currency_dropdown(self) -> bool:
        return self.page.get_by_role(
            self._CURRENCY_BUTTON_ROLE, name=self._CURRENCY_BUTTON_NAME
        ).is_visible()

    def has_search_input(self) -> bool:
        return self.page.get_by_placeholder(self._SEARCH_PLACEHOLDER).is_visible()

    def has_empty_cart_summary(self) -> bool:
        return self.page.get_by_role(
            self._EMPTY_CART_BUTTON_ROLE, name=self._EMPTY_CART_BUTTON_NAME
        ).is_visible()

    def has_account_menu(self) -> bool:
        return (
            self.page.get_by_role(
                self._ACCOUNT_LINK_ROLE, name=self._ACCOUNT_LINK_NAME
            ).first.is_visible()
        )

    def go_to_login(self) -> None:
        self._open_account_menu_and_click(
            self.page.get_by_role(self._ACCOUNT_LINK_ROLE, name=self._LOGIN_LINK_NAME)
        )

    def go_to_register(self) -> None:
        self._open_account_menu_and_click(
            self.page.get_by_role(
                self._ACCOUNT_LINK_ROLE, name=self._REGISTER_LINK_NAME
            )
        )

    def logout(self) -> None:
        self._open_account_menu_and_click(
            self.page.get_by_role(self._ACCOUNT_LINK_ROLE, name=self._LOGOUT_LINK_NAME)
        )

    def is_logged_in(self) -> bool:
        return (
            self.page.get_by_role(
                self._ACCOUNT_LINK_ROLE, name=self._LOGOUT_LINK_NAME
            ).count()
            > 0
        )

    def _open_account_menu_and_click(self, link: Locator) -> None:
        self.page.get_by_role(
            self._ACCOUNT_LINK_ROLE, name=self._ACCOUNT_LINK_NAME
        ).first.click()
        expect(link).to_be_visible()
        link.click()
        self.page.wait_for_load_state("domcontentloaded")
