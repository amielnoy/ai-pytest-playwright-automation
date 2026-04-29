from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components import NavBarComponent


class HomePage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.nav = NavBarComponent(page)

    def open(self) -> "HomePage":
        self.navigate()
        return self

    def search(self, query: str) -> None:
        self.nav.search(query)

    def has_currency_dropdown(self) -> bool:
        # Repurposed for eBay: checks that the site header is visible
        return self.nav.has_site_header()

    def go_to_login(self) -> None:
        self.nav.go_to_login()

    def go_to_register(self) -> None:
        self.nav.go_to_register()

    def logout(self) -> None:
        self.nav.logout()

    def is_logged_in(self) -> bool:
        return self.nav.is_logged_in()
