"""
Session 6 — Advanced Playwright: POM + UI + API
CheckoutPage encapsulates the two-step checkout flow.
"""

from playwright.sync_api import Page, expect
from .base_page import BasePage
from .data_factory import CheckoutInfo


class CheckoutPage(BasePage):
    _FIRST_NAME_PLACEHOLDER = "First Name"
    _LAST_NAME_PLACEHOLDER = "Last Name"
    _POSTAL_CODE_PLACEHOLDER = "Zip/Postal Code"
    _CONTINUE_BUTTON = '[data-test="continue"]'
    _FINISH_BUTTON_ROLE = "button"
    _FINISH_BUTTON_NAME = "Finish"
    _ORDER_COMPLETE_TEXT = "Thank you for your order!"
    _ERROR_SELECTOR = '[data-test="error"]'

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def fill_info(self, info: CheckoutInfo) -> "CheckoutPage":
        self.page.get_by_placeholder(self._FIRST_NAME_PLACEHOLDER).fill(info.first_name)
        self.page.get_by_placeholder(self._LAST_NAME_PLACEHOLDER).fill(info.last_name)
        self.page.get_by_placeholder(self._POSTAL_CODE_PLACEHOLDER).fill(info.postal_code)
        return self

    def continue_to_overview(self) -> "CheckoutPage":
        self.page.locator(self._CONTINUE_BUTTON).click()
        return self

    def finish(self) -> "CheckoutPage":
        self.page.get_by_role(self._FINISH_BUTTON_ROLE, name=self._FINISH_BUTTON_NAME).click()
        return self

    def expect_order_complete(self) -> "CheckoutPage":
        expect(self.page.get_by_text(self._ORDER_COMPLETE_TEXT)).to_be_visible()
        return self

    def expect_info_error(self, message: str) -> "CheckoutPage":
        expect(self.page.locator(self._ERROR_SELECTOR)).to_contain_text(message)
        return self
