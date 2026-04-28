from playwright.sync_api import Page

from pages.components.base_component import BaseComponent


class RegistrationFormComponent(BaseComponent):
    """All fields, controls, and post-submit state on the Register page."""

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
    _SUCCESS_HEADING = "h1:text-is('Your Account Has Been Created!')"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def fill(
        self,
        first_name: str,
        last_name: str,
        email: str,
        telephone: str,
        password: str,
        confirm_password: str,
        newsletter: bool = False,
    ) -> None:
        self.page.fill(self._FIRST_NAME, first_name)
        self.page.fill(self._LAST_NAME, last_name)
        self.page.fill(self._EMAIL, email)
        self.page.fill(self._TELEPHONE, telephone)
        self.page.fill(self._PASSWORD, password)
        self.page.fill(self._CONFIRM, confirm_password)
        radio = self._NEWSLETTER_YES if newsletter else self._NEWSLETTER_NO
        self.page.click(radio)

    def accept_privacy_policy(self) -> None:
        self.page.check(self._PRIVACY_POLICY)

    def submit(self) -> None:
        self.page.locator(self._SUBMIT).click()

    def is_submitted_successfully(self) -> bool:
        return self.page.locator(self._SUCCESS_HEADING).is_visible()
