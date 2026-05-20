from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components import NavBarComponent
from pages.self_healing import healing_locator


class HomePage(BasePage):
    _FEATURED_PRODUCT_IMAGES = ".product-thumb img"
    _VISIBLE_IMAGES_MISSING_ALT_SCRIPT = """elements => elements
        .filter(el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length))
        .filter(el => !el.hasAttribute('alt') || !el.getAttribute('alt').trim())
        .map(el => el.outerHTML.slice(0, 160))"""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.nav = NavBarComponent(page)
        self.featured_product_images = healing_locator(
            page.locator(self._FEATURED_PRODUCT_IMAGES),
            name="featured product images",
            primary_label=self._FEATURED_PRODUCT_IMAGES,
            fallbacks=[
                (".product-thumb [role='img']", page.locator(".product-thumb [role='img']")),
                (".product-thumb img", page.locator(".product-thumb img")),
            ],
            events=self._self_heal_events,
        )

    def open(self) -> "HomePage":
        self.navigate()
        return self

    def search(self, query: str) -> None:
        self.nav.search(query)

    def has_currency_dropdown(self) -> bool:
        return self.nav.has_currency_dropdown()

    def has_search_input(self) -> bool:
        return self.nav.has_search_input()

    def has_empty_cart_summary(self) -> bool:
        return self.nav.has_empty_cart_summary()

    def has_header_accessible_controls(self) -> bool:
        return (
            self.nav.has_account_menu()
            and self.nav.has_currency_dropdown()
            and self.nav.has_search_input()
            and self.nav.has_empty_cart_summary()
        )

    def visible_featured_images_missing_alt(self) -> list[str]:
        return self.featured_product_images.evaluate_all(
            self._VISIBLE_IMAGES_MISSING_ALT_SCRIPT
        )

    def go_to_login(self) -> None:
        self.nav.go_to_login()

    def go_to_register(self) -> None:
        self.nav.go_to_register()

    def logout(self) -> None:
        self.nav.logout()

    def is_logged_in(self) -> bool:
        return self.nav.is_logged_in()
