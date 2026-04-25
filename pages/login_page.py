from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    _EMAIL = "input#input-email"
    _PASSWORD = "input#input-password"
    _SUBMIT = "input[type='submit'][value='Login']"
    _ERROR_ALERT = ".alert-danger"
    _ACCOUNT_HEADING = "//h2[text()='My Account']"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def login(self, email: str, password: str):
        self.page.fill(self._EMAIL, email)
        self.page.fill(self._PASSWORD, password)
        self.page.click(self._SUBMIT)
        self.page.wait_for_load_state("networkidle")

    def is_login_successful(self) -> bool:
        return self.page.locator(self._ACCOUNT_HEADING).is_visible()

    def get_error_message(self) -> str:
        el = self.page.locator(self._ERROR_ALERT)
        return el.inner_text() if el.is_visible() else ""
