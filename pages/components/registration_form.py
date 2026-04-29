from pages.components.base_component import BaseComponent


class RegistrationFormComponent(BaseComponent):
    # Password inputs are excluded from the ARIA "textbox" role — kept as CSS selectors.
    _PASSWORD = "input#input-password"
    _CONFIRM = "input#input-confirm"
    _PRIVACY_POLICY = "input[name='agree']"

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
        self.page.get_by_role("textbox", name="First Name").fill(first_name)
        self.page.get_by_role("textbox", name="Last Name").fill(last_name)
        self.page.get_by_role("textbox", name="E-Mail").fill(email)
        self.page.get_by_role("textbox", name="Telephone").fill(telephone)
        self.page.locator(self._PASSWORD).fill(password)
        self.page.locator(self._CONFIRM).fill(confirm_password)
        self.page.get_by_role("radio", name="Yes" if newsletter else "No").check()

    def accept_privacy_policy(self) -> None:
        self.page.locator(self._PRIVACY_POLICY).check()

    def submit(self) -> None:
        self.page.get_by_role("button", name="Continue").click()

    def is_submitted_successfully(self) -> bool:
        return self.page.get_by_role(
            "heading", name="Your Account Has Been Created!", level=1
        ).is_visible()
