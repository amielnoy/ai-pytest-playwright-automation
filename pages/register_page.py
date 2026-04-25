from playwright.sync_api import Page
from pages.base_page import BasePage


class RegisterPage(BasePage):
    # Locators
    _FIRST_NAME = "input#input-firstname"
    _LAST_NAME = "input#input-lastname"
    _EMAIL = "input#input-email"
    _TELEPHONE = "input#input-telephone"
    _PASSWORD = "input#input-password"
    _CONFIRM = "input#input-confirm"
    _NEWSLETTER_YES = "input[name='newsletter'][value='1']"
    _NEWSLETTER_NO = "input[name='newsletter'][value='0']"
    _PRIVACY_POLICY = "input[name='agree']"
    _SUBMIT = "input[type='submit'][value='Continue']"
    _SUCCESS_HEADING = "//h1[contains(text(),'Your Account Has Been Created')]"
    _ERROR_ALERT = ".alert-danger"
    _FIELD_ERROR = ".text-danger"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        telephone: str,
        password: str,
        confirm_password: str,
        newsletter: bool = False,
    ):
        self.page.fill(self._FIRST_NAME, first_name)
        self.page.fill(self._LAST_NAME, last_name)
        self.page.fill(self._EMAIL, email)
        self.page.fill(self._TELEPHONE, telephone)
        self.page.fill(self._PASSWORD, password)
        self.page.fill(self._CONFIRM, confirm_password)

        if newsletter:
            self.page.click(self._NEWSLETTER_YES)
        else:
            self.page.click(self._NEWSLETTER_NO)

        self.page.check(self._PRIVACY_POLICY)
        self.page.click(self._SUBMIT)
        self.page.wait_for_load_state("networkidle")

    def is_registration_successful(self) -> bool:
        return self.page.locator(self._SUCCESS_HEADING).is_visible()

    def get_error_message(self) -> str:
        banner = self.page.locator(self._ERROR_ALERT)
        if banner.is_visible():
            return banner.inner_text()
        # Fallback: inline per-field validation errors
        first_field_error = self.page.locator(self._FIELD_ERROR).first
        if first_field_error.is_visible():
            return first_field_error.inner_text()
        return ""
