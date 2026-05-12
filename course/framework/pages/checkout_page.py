"""Session 6 — CheckoutPage (two-step checkout flow)."""
from playwright.sync_api import Page, expect
from .base_page import BasePage


class CheckoutPage(BasePage):
    _FIRST_NAME = "First Name"
    _LAST_NAME = "Last Name"
    _POSTAL_CODE = "Zip/Postal Code"
    _CONTINUE_BTN = '[data-test="continue"]'
    _FINISH_BTN_ROLE = "button"
    _FINISH_BTN_NAME = "Finish"
    _COMPLETE_TEXT = "Thank you for your order!"
    _ERROR_SELECTOR = '[data-test="error"]'

    def fill_info(self, first: str, last: str, postal: str) -> "CheckoutPage":
        self.page.get_by_placeholder(self._FIRST_NAME).fill(first)
        self.page.get_by_placeholder(self._LAST_NAME).fill(last)
        self.page.get_by_placeholder(self._POSTAL_CODE).fill(postal)
        return self

    def continue_to_overview(self) -> "CheckoutPage":
        self.page.locator(self._CONTINUE_BTN).click()
        return self

    def finish(self) -> "CheckoutPage":
        self.page.get_by_role(self._FINISH_BTN_ROLE, name=self._FINISH_BTN_NAME).click()
        return self

    def expect_order_complete(self) -> "CheckoutPage":
        expect(self.page.get_by_text(self._COMPLETE_TEXT)).to_be_visible()
        return self

    def expect_error(self, message: str) -> "CheckoutPage":
        expect(self.page.locator(self._ERROR_SELECTOR)).to_contain_text(message)
        return self
