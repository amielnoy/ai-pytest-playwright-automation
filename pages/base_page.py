from playwright.sync_api import Page, expect

from pages.components.alert import AlertComponent


class BasePage:
    _HTML_SELECTOR = "html"
    _ANY_ID_SELECTOR = "[id]"
    _DUPLICATE_IDS_SCRIPT = """elements => {
        const ids = elements.map(el => el.id).filter(Boolean);
        return [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))];
    }"""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.alert = AlertComponent(page)

    def navigate(self, path: str = "", wait_until: str = "domcontentloaded") -> None:
        route = path.lstrip("/")
        target = f"{self.base_url}/{route}" if route else self.base_url
        self.page.goto(target, wait_until=wait_until)

    @property
    def title(self) -> str:
        return self.page.title()

    @property
    def url(self) -> str:
        return self.page.url

    def wait_for_visible(self, selector: str, timeout: int | None = None) -> None:
        kw = {} if timeout is None else {"timeout": timeout}
        expect(self.page.locator(selector).first).to_be_visible(**kw)

    def document_language(self) -> str | None:
        return self.page.locator(self._HTML_SELECTOR).get_attribute("lang")

    def duplicate_ids(self) -> list[str]:
        return self.page.locator(self._ANY_ID_SELECTOR).evaluate_all(
            self._DUPLICATE_IDS_SCRIPT
        )

    def take_screenshot(self) -> bytes:
        return self.page.screenshot()

    def get_error_message(self) -> str:
        return self.alert.get_error()
