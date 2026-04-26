from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.components import NavBarComponent


class HomePage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.nav = NavBarComponent(page)

    def open(self) -> "HomePage":
        self.navigate()
        self.page.wait_for_load_state("networkidle")
        return self

    def search(self, query: str) -> None:
        self.nav.search(query)

    def go_to_login(self) -> None:
        self.nav.go_to_login()

    def go_to_register(self) -> None:
        self.nav.go_to_register()

    def logout(self) -> None:
        self.nav.logout()

    def is_logged_in(self) -> bool:
        return self.nav.is_logged_in()
