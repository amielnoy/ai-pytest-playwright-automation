"""
Session 4 — Advanced Playwright: POM + UI + API
Base page class providing shared navigation helpers.
"""

from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> "BasePage":
        self.page.goto(f"{self.base_url}{path}")
        return self
