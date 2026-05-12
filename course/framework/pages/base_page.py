"""
Session 6 — BasePage: navigate, wait, screenshot.
Every page class extends this. Tests never call it directly.
"""
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str = "") -> "BasePage":
        self.page.goto(f"{self.base_url}{path}")
        return self

    @property
    def title(self) -> str:
        return self.page.title()

    @property
    def url(self) -> str:
        return self.page.url
