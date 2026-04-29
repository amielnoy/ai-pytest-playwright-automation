from playwright.sync_api import expect

from pages.components.base_component import BaseComponent


class AlertComponent(BaseComponent):
    _FIELD_ERROR = "span.error, div.field__error--display"
    _SUCCESS = ".s-item__title"

    def get_error(self) -> str:
        """Return the first visible error text (inline field error)."""
        for sel in self._FIELD_ERROR.split(", "):
            el = self.page.locator(sel.strip()).first
            try:
                if el.is_visible(timeout=2000):
                    return el.inner_text()
            except Exception:
                pass
        return ""

    def get_success(self) -> str:
        el = self.page.locator(self._SUCCESS).first
        try:
            return el.inner_text() if el.is_visible(timeout=2000) else ""
        except Exception:
            return ""

    def wait_for_success(self, timeout: int = 8_000) -> None:
        expect(self.page.locator(self._SUCCESS).first).to_be_visible(timeout=timeout)
