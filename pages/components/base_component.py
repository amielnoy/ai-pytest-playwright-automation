from playwright.sync_api import Page

from pages.self_healing import SelfHealEvent


class BaseComponent:
    """Root class for page-level components (interact with the full page)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self._self_heal_events: list[SelfHealEvent] = []

    def self_heal_events(self) -> list[SelfHealEvent]:
        return list(self._self_heal_events)
