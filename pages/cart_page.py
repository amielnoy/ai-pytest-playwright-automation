from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components import CartSummaryComponent


class CartPage(BasePage):
    _PATH = "index.php?route=checkout/cart"
    _CHECKOUT_LINK_ROLE = "link"
    _CHECKOUT_LINK_NAME = "Checkout"
    _CONTINUE_LINK_NAME = "Continue Shopping"
    _EMPTY_CART_TEXT = "Your shopping cart is empty!"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.summary = CartSummaryComponent(page)
        self.checkout_button = page.get_by_role(
            self._CHECKOUT_LINK_ROLE, name=self._CHECKOUT_LINK_NAME
        )
        self.continue_shopping_button = page.get_by_role(
            self._CHECKOUT_LINK_ROLE, name=self._CONTINUE_LINK_NAME
        )
        self.empty_message = page.get_by_text(self._EMPTY_CART_TEXT)

    def open(self, min_items: int | None = None) -> None:
        self.navigate(self._PATH)
        if min_items is not None:
            self.summary.wait_for_item_count(min_items)

    def get_cart_total(self) -> float:
        return self.summary.get_total()

    def is_empty(self) -> bool:
        return self.summary.is_empty()

    def get_item_count(self) -> int:
        return self.summary.get_item_count()

    def get_item_subtotals(self) -> list[float]:
        return self.summary.get_item_subtotals()
