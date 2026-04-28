from playwright.sync_api import Page, expect

from pages.components.base_component import BaseComponent


class AlertComponent(BaseComponent):
    """
    Flash messages and inline validation errors.
    Shared by Login, Register, and Search results pages.
    """

    _SUCCESS = ".alert-success"
    _DANGER = ".alert-danger"
    _FIELD_ERROR = ".text-danger"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def get_error(self) -> str:
        """Return the first visible error text (banner or inline field error)."""
        banner = self.page.locator(self._DANGER)
        if banner.is_visible():
            return banner.inner_text()
        first_field = self.page.locator(self._FIELD_ERROR).first
        if first_field.is_visible():
            return first_field.inner_text()
        return ""

    def get_success(self) -> str:
        el = self.page.locator(self._SUCCESS)
        return el.inner_text() if el.is_visible() else ""

    def wait_for_success(self, timeout: int = 8_000) -> None:
        expect(self.page.locator(self._SUCCESS)).to_be_visible(timeout=timeout)
