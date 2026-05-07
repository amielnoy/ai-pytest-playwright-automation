"""
Session 4 — Advanced Playwright: POM + UI + API
InventoryPage encapsulates product listing interactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect
from .base_page import BasePage

if TYPE_CHECKING:
    from .cart_page import CartPage


class InventoryPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.cart_badge = page.locator(".shopping_cart_badge")

    def add_first_item(self) -> "InventoryPage":
        self.page.get_by_role("button", name="Add to cart").first.click()
        return self

    def add_item_by_name(self, name: str) -> "InventoryPage":
        self.page.locator(".inventory_item").filter(has_text=name).get_by_role(
            "button", name="Add to cart"
        ).click()
        return self

    def remove_item_by_name(self, name: str) -> "InventoryPage":
        self.page.locator(".inventory_item").filter(has_text=name).get_by_role(
            "button", name="Remove"
        ).click()
        return self

    def sort_by(self, option: str) -> "InventoryPage":
        self.page.locator('[data-test="product_sort_container"]').select_option(option)
        return self

    def product_names(self) -> list[str]:
        return [el.inner_text() for el in self.page.locator(".inventory_item_name").all()]

    def product_prices(self) -> list[float]:
        return [
            float(el.inner_text().lstrip("$"))
            for el in self.page.locator(".inventory_item_price").all()
        ]

    def go_to_cart(self) -> CartPage:
        from .cart_page import CartPage
        self.page.locator(".shopping_cart_link").click()
        return CartPage(self.page, self.base_url)

    def expect_cart_count(self, count: int) -> "InventoryPage":
        expect(self.cart_badge).to_have_text(str(count))
        return self

    def expect_no_cart_badge(self) -> "InventoryPage":
        expect(self.cart_badge).not_to_be_visible()
        return self
