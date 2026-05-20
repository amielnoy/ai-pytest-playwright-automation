from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

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
    _INVALID_LOGIN_WARNING_PREFIX = "Warning:"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.email_input = page.get_by_role(self._EMAIL_ROLE, name=self._EMAIL_NAME)
        self.password_input = page.get_by_label(self._PASSWORD_LABEL)
        self.login_button = page.get_by_role(
            self._LOGIN_BUTTON_ROLE, name=self._LOGIN_BUTTON_NAME
        )
        self.my_account_heading = page.get_by_role(
            self._MY_ACCOUNT_HEADING_ROLE,
            name=self._MY_ACCOUNT_HEADING_NAME,
            level=self._MY_ACCOUNT_HEADING_LEVEL,
        )
        self.invalid_credentials_warning = page.locator(
            self._INVALID_CREDENTIALS_WARNING
        )

    def open(self) -> None:
        self.navigate(self._PATH)

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

    def is_login_successful(self) -> bool:
        return self.my_account_heading.is_visible()

    def has_accessible_login_controls(self) -> bool:
        return (
            self.email_input.is_visible()
            and self.password_input.is_visible()
            and self.login_button.is_visible()
        )

    def has_invalid_credentials_warning(self) -> bool:
        return self.invalid_credentials_warning.is_visible()

    def has_invalid_credentials_warning_text(self, timeout: int = 5000) -> bool:
        try:
            self.invalid_credentials_warning.wait_for(state="visible", timeout=timeout)
        except PlaywrightTimeoutError:
            return False
        return (
            self._INVALID_LOGIN_WARNING_PREFIX
            in self.invalid_credentials_warning.inner_text()
        )
