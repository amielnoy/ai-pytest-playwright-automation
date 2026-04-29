from pages.components.base_component import BaseComponent


class NavBarComponent(BaseComponent):
    _SEARCH_INPUT = "input[name='_nkw']"
    _SEARCH_BUTTON = "#gh-btn"
    _SITE_HEADER = "#gh"
    _SIGN_IN_LINK = "a[href*='signin.ebay.com']"

    def search(self, query: str) -> None:
        self.page.locator(self._SEARCH_INPUT).fill(query)
        self.page.locator(self._SEARCH_BUTTON).click()
        self.page.wait_for_load_state("domcontentloaded")

    def has_site_header(self) -> bool:
        return self.page.locator(self._SITE_HEADER).is_visible()

    def go_to_login(self) -> None:
        self.page.locator(self._SIGN_IN_LINK).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    def go_to_register(self) -> None:
        self.page.locator(self._SIGN_IN_LINK).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    def logout(self) -> None:
        # No-op: eBay logout requires session management not needed here
        pass

    def is_logged_in(self) -> bool:
        return "Hi, " in (self.page.locator("#gh-ug").inner_text() if self.page.locator("#gh-ug").is_visible() else "")
