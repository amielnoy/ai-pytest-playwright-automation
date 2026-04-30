from pages.components.base_component import BaseComponent


class RegistrationFormComponent(BaseComponent):
    _TEXTBOX_ROLE = "textbox"
    _FIRST_NAME_TEXTBOX_NAME = "First Name"
    _LAST_NAME_TEXTBOX_NAME = "Last Name"
    _EMAIL_TEXTBOX_NAME = "E-Mail"
    _TELEPHONE_TEXTBOX_NAME = "Telephone"
    _PASSWORD_LABEL = "Password"
    _CONFIRM_PASSWORD_LABEL = "Password Confirm"
    _REQUIRED_FIELD_LABELS = (
        _FIRST_NAME_TEXTBOX_NAME,
        _LAST_NAME_TEXTBOX_NAME,
        _EMAIL_TEXTBOX_NAME,
        _TELEPHONE_TEXTBOX_NAME,
        _PASSWORD_LABEL,
        _CONFIRM_PASSWORD_LABEL,
    )
    _NEWSLETTER_RADIO_ROLE = "radio"
    _NEWSLETTER_YES_NAME = "Yes"
    _NEWSLETTER_NO_NAME = "No"
    # The privacy checkbox is not wrapped by a label in TutorialNinja markup.
    _PRIVACY_POLICY = "input[name='agree']"
    _SUBMIT_BUTTON_ROLE = "button"
    _SUBMIT_BUTTON_NAME = "Continue"
    _SUCCESS_HEADING_ROLE = "heading"
    _SUCCESS_HEADING_NAME = "Your Account Has Been Created!"
    _SUCCESS_HEADING_LEVEL = 1

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
        self.page.get_by_role(
            self._TEXTBOX_ROLE, name=self._FIRST_NAME_TEXTBOX_NAME
        ).fill(first_name)
        self.page.get_by_role(
            self._TEXTBOX_ROLE, name=self._LAST_NAME_TEXTBOX_NAME
        ).fill(last_name)
        self.page.get_by_role(self._TEXTBOX_ROLE, name=self._EMAIL_TEXTBOX_NAME).fill(
            email
        )
        self.page.get_by_role(
            self._TEXTBOX_ROLE, name=self._TELEPHONE_TEXTBOX_NAME
        ).fill(telephone)
        self.page.get_by_label(self._PASSWORD_LABEL, exact=True).fill(password)
        self.page.get_by_label(self._CONFIRM_PASSWORD_LABEL).fill(confirm_password)
        newsletter_name = (
            self._NEWSLETTER_YES_NAME if newsletter else self._NEWSLETTER_NO_NAME
        )
        self.page.get_by_role(self._NEWSLETTER_RADIO_ROLE, name=newsletter_name).check()

    def accept_privacy_policy(self) -> None:
        self.page.locator(self._PRIVACY_POLICY).check()

    def submit(self) -> None:
        self.page.get_by_role(
            self._SUBMIT_BUTTON_ROLE, name=self._SUBMIT_BUTTON_NAME
        ).click()

    def is_submitted_successfully(self) -> bool:
        return self.page.get_by_role(
            self._SUCCESS_HEADING_ROLE,
            name=self._SUCCESS_HEADING_NAME,
            level=self._SUCCESS_HEADING_LEVEL,
        ).is_visible()

    def has_required_field_labels(self) -> bool:
        return all(
            self.page.get_by_label(label, exact=True).is_visible()
            for label in self._REQUIRED_FIELD_LABELS
        )

    def has_newsletter_options(self) -> bool:
        return (
            self.page.get_by_role(
                self._NEWSLETTER_RADIO_ROLE, name=self._NEWSLETTER_YES_NAME
            ).is_visible()
            and self.page.get_by_role(
                self._NEWSLETTER_RADIO_ROLE, name=self._NEWSLETTER_NO_NAME
            ).is_visible()
        )
