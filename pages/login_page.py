from pages.base_page import BasePage


class LoginPage(BasePage):
    # Password inputs are excluded from the ARIA "textbox" role — kept as CSS selector.
    _PASSWORD = "input#input-password"

    def login(self, email: str, password: str) -> None:
        self.page.get_by_role("textbox", name="E-Mail Address").fill(email)
        self.page.locator(self._PASSWORD).fill(password)
        self.page.get_by_role("button", name="Login").click()

    def is_login_successful(self) -> bool:
        return self.page.get_by_role("heading", name="My Account", level=2).is_visible()
