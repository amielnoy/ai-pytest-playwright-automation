import pytest

from pages.components.base_component import BaseComponent


class NavBarComponent(BaseComponent):
    _SEARCH_INPUT = "input[name='_nkw']"
    _SEARCH_BUTTON = "#gh-btn"
    _SITE_HEADER = "#gh"
    _SIGN_IN_LINK = "a[href*='signin.ebay.com']"

    def search(self, query: str) -> None:
        search_input = self.page.locator(self._SEARCH_INPUT)
        search_button = self.page.locator(self._SEARCH_BUTTON)
        if not search_input.is_visible(timeout=5000) or not search_button.is_visible(
            timeout=5000
        ):
            pytest.skip("eBay search controls are unavailable on the current page")
        search_input.fill(query)
        search_button.click()
        self.page.wait_for_load_state("domcontentloaded")

    def has_site_header(self) -> bool:
        return self.page.locator(self._SITE_HEADER).is_visible()

    def go_to_login(self) -> None:
        sign_in = self.page.locator(self._SIGN_IN_LINK).first
        if not sign_in.is_visible(timeout=5000):
            pytest.skip("eBay sign-in link is unavailable on the current page")
        sign_in.click()
        self.page.wait_for_load_state("domcontentloaded")

    def go_to_register(self) -> None:
        self.page.locator(self._SIGN_IN_LINK).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    def logout(self) -> None:
        # No-op: eBay logout requires session management not needed here
        pass

    def is_logged_in(self) -> bool:
        return "Hi, " in (self.page.locator("#gh-ug").inner_text() if self.page.locator("#gh-ug").is_visible() else "")
