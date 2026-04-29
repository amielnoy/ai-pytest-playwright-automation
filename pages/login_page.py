from pages.base_page import BasePage


class LoginPage(BasePage):
    _EMAIL_INPUT = "input#userid"
    _CONTINUE_BUTTON = "button#signin-continue-btn"

    def login(self, email: str, password: str) -> None:  # noqa: ARG002
        self.navigate("signin/")
        self.page.locator(self._EMAIL_INPUT).fill(email)
        self.page.locator(self._CONTINUE_BUTTON).click()

    def is_login_successful(self) -> bool:
        # Not possible without real credentials
        return False
