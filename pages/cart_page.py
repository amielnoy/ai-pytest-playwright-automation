from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components import CartSummaryComponent


class CartPage(BasePage):
    _PATH = "index.php?route=checkout/cart"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.summary = CartSummaryComponent(page)

    def open(self) -> None:
        self.navigate(self._PATH)

    def get_cart_total(self) -> float:
        return self.summary.get_total()

    def is_empty(self) -> bool:
        return self.summary.is_empty()

    def get_item_count(self) -> int:
        return self.summary.get_item_count()
