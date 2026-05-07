"""
Session 4 — Advanced Playwright: POM + UI + API
CheckoutPage encapsulates the two-step checkout flow.
"""

from playwright.sync_api import Page, expect
from .base_page import BasePage
from .data_factory import CheckoutInfo


class CheckoutPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def fill_info(self, info: CheckoutInfo) -> "CheckoutPage":
        self.page.get_by_placeholder("First Name").fill(info.first_name)
        self.page.get_by_placeholder("Last Name").fill(info.last_name)
        self.page.get_by_placeholder("Zip/Postal Code").fill(info.postal_code)
        return self

    def continue_to_overview(self) -> "CheckoutPage":
        self.page.get_by_role("input", name="Continue").click()
        return self

    def finish(self) -> "CheckoutPage":
        self.page.get_by_role("button", name="Finish").click()
        return self

    def expect_order_complete(self) -> "CheckoutPage":
        expect(self.page.get_by_text("Thank you for your order!")).to_be_visible()
        return self

    def expect_info_error(self, message: str) -> "CheckoutPage":
        expect(self.page.locator('[data-test="error"]')).to_contain_text(message)
        return self
