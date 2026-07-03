from playwright.sync_api import Page, expect

from pages.components.base_component import BaseComponent


class AlertComponent(BaseComponent):
    _SUCCESS = ".alert-success"
    _DANGER = ".alert-danger"
    _FIELD_ERROR = ".text-danger"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.success_alert = self._healed(
            self._SUCCESS, "success alert",
            ["[class*='alert'][class*='success']"],
        )
        self.danger_alert = self._healed(
            self._DANGER, "danger alert",
            ["[class*='alert'][class*='danger']", "[class*='alert'][class*='warning']"],
        )
        self.field_errors = self._healed(
            self._FIELD_ERROR, "field error",
            ["[class*='text-danger']", "[class*='error']"],
        )

    def get_error(self) -> str:
        """Return the first visible error text (banner or inline field error)."""
        if self.danger_alert.is_visible():
            return self.danger_alert.inner_text()
        first_field = self.field_errors.first
        if first_field.is_visible():
            return first_field.inner_text()
        return ""

    def get_success(self) -> str:
        if self.success_alert.is_visible():
            return self.success_alert.inner_text()
        return ""

    def wait_for_success(self, timeout: int = 8_000) -> None:
        # expect() requires a Playwright Locator, not SelfHealingLocator
        expect(self.success_alert.first).to_be_visible(timeout=timeout)

    def clear_success(self, timeout: int = 8_000) -> None:
        """Wait for add-to-cart success, then dismiss or hide before the next action."""
        self.wait_for_success(timeout=timeout)
        alert = self.success_alert.first
        close = alert.locator("button.close, [data-dismiss='alert']").first
        if close.is_visible():
            close.click()
        expect(alert).to_be_hidden(timeout=timeout)
