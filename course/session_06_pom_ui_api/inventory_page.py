"""
Session 6 — Advanced Playwright: POM + UI + API
InventoryPage encapsulates product listing interactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect
from .base_page import BasePage

if TYPE_CHECKING:
    from .cart_page import CartPage


class InventoryPage(BasePage):
    _CART_BADGE = ".shopping_cart_badge"
    _CART_LINK = ".shopping_cart_link"
    _INVENTORY_ITEM = ".inventory_item"
    _ITEM_NAME = ".inventory_item_name"
    _ITEM_PRICE = ".inventory_item_price"
    _SORT_CONTAINER = '[data-test="product_sort_container"]'
    _ADD_TO_CART_ROLE = "button"
    _ADD_TO_CART_NAME = "Add to cart"
    _REMOVE_BUTTON_NAME = "Remove"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.cart_badge = page.locator(self._CART_BADGE)

    def add_first_item(self) -> "InventoryPage":
        self.page.get_by_role(self._ADD_TO_CART_ROLE, name=self._ADD_TO_CART_NAME).first.click()
        return self

    def add_item_by_name(self, name: str) -> "InventoryPage":
        self.page.locator(self._INVENTORY_ITEM).filter(has_text=name).get_by_role(
            self._ADD_TO_CART_ROLE, name=self._ADD_TO_CART_NAME
        ).click()
        return self

    def remove_item_by_name(self, name: str) -> "InventoryPage":
        self.page.locator(self._INVENTORY_ITEM).filter(has_text=name).get_by_role(
            self._ADD_TO_CART_ROLE, name=self._REMOVE_BUTTON_NAME
        ).click()
        return self

    def sort_by(self, option: str) -> "InventoryPage":
        self.page.locator(self._SORT_CONTAINER).select_option(option)
        return self

    def product_names(self) -> list[str]:
        return [el.inner_text() for el in self.page.locator(self._ITEM_NAME).all()]

    def product_prices(self) -> list[float]:
        return [
            float(el.inner_text().lstrip("$"))
            for el in self.page.locator(self._ITEM_PRICE).all()
        ]

    def go_to_cart(self) -> CartPage:
        from .cart_page import CartPage
        self.page.locator(self._CART_LINK).click()
        return CartPage(self.page, self.base_url)

    def expect_cart_count(self, count: int) -> "InventoryPage":
        expect(self.cart_badge).to_have_text(str(count))
        return self

    def expect_no_cart_badge(self) -> "InventoryPage":
        expect(self.cart_badge).not_to_be_visible()
        return self
