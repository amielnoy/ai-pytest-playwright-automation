from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.components import RegistrationFormComponent


class RegisterPage(BasePage):
    _ERROR_WARNING_SELECTOR = ".alert-danger"
    _CONTINUE_AFTER_SUCCESS_ROLE = "link"
    _CONTINUE_AFTER_SUCCESS_NAME = "Continue"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.form = RegistrationFormComponent(page)
        # Promote the success heading to the page level for direct assertion.
        self.success_heading = self.form.success_heading
        self.error_warning = page.locator(self._ERROR_WARNING_SELECTOR)
        self.continue_button = page.get_by_role(
            self._CONTINUE_AFTER_SUCCESS_ROLE, name=self._CONTINUE_AFTER_SUCCESS_NAME
        )

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        telephone: str,
        password: str,
        confirm_password: str,
        newsletter: bool = False,
    ) -> None:
        self.form.fill(
            first_name, last_name, email, telephone, password, confirm_password, newsletter
        )
        self.form.accept_privacy_policy()
        self.form.submit()

    def is_registration_successful(self) -> bool:
        return self.form.is_submitted_successfully()

    def has_required_field_labels(self) -> bool:
        return self.form.has_required_field_labels()

    def has_newsletter_options(self) -> bool:
        return self.form.has_newsletter_options()
