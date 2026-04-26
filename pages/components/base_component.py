from playwright.sync_api import Page


class BaseComponent:
    """Root class for page-level components (interact with the full page)."""

    def __init__(self, page: Page) -> None:
        self.page = page
