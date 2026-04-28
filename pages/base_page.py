from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str = "", wait_until: str = "domcontentloaded") -> None:
        route = path.lstrip("/")
        target = f"{self.base_url}/{route}" if route else self.base_url
        self.page.goto(target, wait_until=wait_until)
