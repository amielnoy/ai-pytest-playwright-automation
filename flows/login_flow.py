from pages.home_page import HomePage
from pages.login_page import LoginPage


class LoginFlow:
    def __init__(self, home_page: HomePage, login_page: LoginPage) -> None:
        self.home = home_page
        self.login_page = login_page

    def login(self, email: str, password: str) -> bool:
        """Navigate to login from home and submit credentials. Returns True on success."""
        self.home.open()
        self.home.go_to_login()
        self.login_page.login(email, password)
        return self.login_page.is_login_successful()

    def logout(self) -> None:
        self.home.logout()
