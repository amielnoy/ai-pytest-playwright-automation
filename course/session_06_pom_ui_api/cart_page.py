"""
Session 6 — Advanced Playwright: POM + UI + API
CartPage encapsulates shopping cart interactions.
"""

from playwright.sync_api import Page, expect
from .base_page import BasePage


class CartPage(BasePage):
    _CART_ITEM = ".cart_item"
    _ITEM_NAME = ".cart_item_label .inventory_item_name"
    _REMOVE_BUTTON_ROLE = "button"
    _REMOVE_BUTTON_NAME = "Remove"
    _CHECKOUT_BUTTON_ROLE = "button"
    _CHECKOUT_BUTTON_NAME = "Checkout"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self) -> "CartPage":
        self.navigate("/cart.html")
        return self

    def item_names(self) -> list[str]:
        return [el.inner_text() for el in self.page.locator(self._ITEM_NAME).all()]

    def item_count(self) -> int:
        return self.page.locator(self._CART_ITEM).count()

    def remove_item_by_name(self, name: str) -> "CartPage":
        self.page.locator(self._CART_ITEM).filter(has_text=name).get_by_role(
            self._REMOVE_BUTTON_ROLE, name=self._REMOVE_BUTTON_NAME
        ).click()
        return self

    def proceed_to_checkout(self):
        from .checkout_page import CheckoutPage
        self.page.get_by_role(self._CHECKOUT_BUTTON_ROLE, name=self._CHECKOUT_BUTTON_NAME).click()
        return CheckoutPage(self.page, self.base_url)

    def expect_item_count(self, count: int) -> "CartPage":
        expect(self.page.locator(self._CART_ITEM)).to_have_count(count)
        return self

    def expect_empty(self) -> "CartPage":
        expect(self.page.locator(self._CART_ITEM)).to_have_count(0)
        return self
