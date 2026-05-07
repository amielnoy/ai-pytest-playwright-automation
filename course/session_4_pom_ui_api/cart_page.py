"""
Session 4 — Advanced Playwright: POM + UI + API
CartPage encapsulates shopping cart interactions.
"""

from playwright.sync_api import Page, expect
from .base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self) -> "CartPage":
        self.navigate("/cart.html")
        return self

    def item_names(self) -> list[str]:
        return [el.inner_text() for el in self.page.locator(".cart_item_label .inventory_item_name").all()]

    def item_count(self) -> int:
        return self.page.locator(".cart_item").count()

    def remove_item_by_name(self, name: str) -> "CartPage":
        self.page.locator(".cart_item").filter(has_text=name).get_by_role(
            "button", name="Remove"
        ).click()
        return self

    def proceed_to_checkout(self):
        from .checkout_page import CheckoutPage
        self.page.get_by_role("button", name="Checkout").click()
        return CheckoutPage(self.page, self.base_url)

    def expect_item_count(self, count: int) -> "CartPage":
        expect(self.page.locator(".cart_item")).to_have_count(count)
        return self

    def expect_empty(self) -> "CartPage":
        expect(self.page.locator(".cart_item")).to_have_count(0)
        return self
