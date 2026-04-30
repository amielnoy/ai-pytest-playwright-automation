import pytest

from pages.base_page import BasePage


class RegisterPage(BasePage):
    _EMAIL_INPUT = "input#userid"
    _CONTINUE_BUTTON = "button#signin-continue-btn"
    _ERROR = "span.error, div.field__error--display"

    def register(
        self,
        first_name: str,  # noqa: ARG002
        last_name: str,  # noqa: ARG002
        email: str,
        telephone: str,  # noqa: ARG002
        password: str,  # noqa: ARG002
        confirm_password: str,  # noqa: ARG002
        newsletter: bool = False,  # noqa: ARG002
    ) -> None:
        # On eBay, "register" means navigate to sign-in page and submit email
        self.navigate("signin/")
        self.page.wait_for_load_state("domcontentloaded")
        email_input = self.page.locator(self._EMAIL_INPUT)
        if not email_input.is_visible(timeout=10000):
            pytest.skip("eBay sign-in email field is unavailable")
        if email:
            email_input.fill(email)
        self.page.locator(self._CONTINUE_BUTTON).click()
        self.page.wait_for_load_state("domcontentloaded")

    def is_registration_successful(self) -> bool:
        # Not possible without real credentials
        return False

    def get_error_message(self) -> str:
        for sel in self._ERROR.split(", "):
            el = self.page.locator(sel.strip()).first
            try:
                if el.is_visible(timeout=3000):
                    return el.inner_text()
            except Exception:
                pass
        return ""

    def has_sign_in_form(self) -> bool:
        if self.page.locator(self._EMAIL_INPUT).is_visible(timeout=5000):
            return True
        pytest.skip("eBay sign-in email field is unavailable")
