from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}/{path}")

    def get_title(self) -> str:
        return self.page.title()

    def wait_for_url_contains(self, fragment: str):
        self.page.wait_for_url(f"**{fragment}**")

    def take_screenshot(self, name: str):
        self.page.screenshot(path=f"allure-results/{name}.png")
