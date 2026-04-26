from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.components import AlertComponent, RegistrationFormComponent


class RegisterPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.form = RegistrationFormComponent(page)
        self.alert = AlertComponent(page)

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

    def get_error_message(self) -> str:
        return self.alert.get_error()
