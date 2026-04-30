from pages.base_page import BasePage


class LoginPage(BasePage):
    _PATH = "index.php?route=account/login"
    _EMAIL_ROLE = "textbox"
    _EMAIL_NAME = "E-Mail Address"
    _PASSWORD_LABEL = "Password"
    _LOGIN_BUTTON_ROLE = "button"
    _LOGIN_BUTTON_NAME = "Login"
    _MY_ACCOUNT_HEADING_ROLE = "heading"
    _MY_ACCOUNT_HEADING_NAME = "My Account"
    _MY_ACCOUNT_HEADING_LEVEL = 2
    _INVALID_CREDENTIALS_WARNING = ".alert-danger"

    def open(self) -> None:
        self.navigate(self._PATH)

    def login(self, email: str, password: str) -> None:
        self.page.get_by_role(self._EMAIL_ROLE, name=self._EMAIL_NAME).fill(email)
        self.page.get_by_label(self._PASSWORD_LABEL).fill(password)
        self.page.get_by_role(
            self._LOGIN_BUTTON_ROLE, name=self._LOGIN_BUTTON_NAME
        ).click()

    def is_login_successful(self) -> bool:
        return self.page.get_by_role(
            self._MY_ACCOUNT_HEADING_ROLE,
            name=self._MY_ACCOUNT_HEADING_NAME,
            level=self._MY_ACCOUNT_HEADING_LEVEL,
        ).is_visible()

    def has_invalid_credentials_warning(self) -> bool:
        return self.page.locator(self._INVALID_CREDENTIALS_WARNING).is_visible()
