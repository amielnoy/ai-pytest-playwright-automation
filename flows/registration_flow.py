from pages.home_page import HomePage
from pages.register_page import RegisterPage


class RegistrationFlow:
    def __init__(self, home_page: HomePage, register_page: RegisterPage) -> None:
        self.home = home_page
        self.register_page = register_page

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        telephone: str,
        password: str,
        confirm_password: str,
        newsletter: bool = False,
    ) -> bool:
        """Navigate to register from home, fill form, and submit. Returns True on success."""
        self.home.open()
        self.home.go_to_register()
        self.register_page.register(
            first_name=first_name,
            last_name=last_name,
            email=email,
            telephone=telephone,
            password=password,
            confirm_password=confirm_password,
            newsletter=newsletter,
        )
        return self.register_page.is_registration_successful()

    def get_error_message(self) -> str:
        return self.register_page.get_error_message()
