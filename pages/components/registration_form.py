from playwright.sync_api import Page

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

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name_input = page.get_by_role(
            self._TEXTBOX_ROLE, name=self._FIRST_NAME_TEXTBOX_NAME
        )
        self.last_name_input = page.get_by_role(
            self._TEXTBOX_ROLE, name=self._LAST_NAME_TEXTBOX_NAME
        )
        self.email_input = page.get_by_role(
            self._TEXTBOX_ROLE, name=self._EMAIL_TEXTBOX_NAME
        )
        self.telephone_input = page.get_by_role(
            self._TEXTBOX_ROLE, name=self._TELEPHONE_TEXTBOX_NAME
        )
        self.password_input = page.get_by_label(self._PASSWORD_LABEL, exact=True)
        self.confirm_password_input = page.get_by_label(
            self._CONFIRM_PASSWORD_LABEL
        )
        self.newsletter_yes = page.get_by_role(
            self._NEWSLETTER_RADIO_ROLE, name=self._NEWSLETTER_YES_NAME
        )
        self.newsletter_no = page.get_by_role(
            self._NEWSLETTER_RADIO_ROLE, name=self._NEWSLETTER_NO_NAME
        )
        self.privacy_policy = self._healed(
            self._PRIVACY_POLICY, "privacy policy checkbox",
            ["input[type='checkbox'][name='agree']", "input[type='checkbox']"],
        )
        self.submit_button = page.get_by_role(
            self._SUBMIT_BUTTON_ROLE, name=self._SUBMIT_BUTTON_NAME
        )
        self.success_heading = page.get_by_role(
            self._SUCCESS_HEADING_ROLE,
            name=self._SUCCESS_HEADING_NAME,
            level=self._SUCCESS_HEADING_LEVEL,
        )
        self.required_field_inputs = tuple(
            page.get_by_label(label, exact=True)
            for label in self._REQUIRED_FIELD_LABELS
        )

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
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.telephone_input.fill(telephone)
        self.password_input.fill(password)
        self.confirm_password_input.fill(confirm_password)
        newsletter_option = self.newsletter_yes if newsletter else self.newsletter_no
        newsletter_option.check()

    def accept_privacy_policy(self) -> None:
        self.privacy_policy.check()

    def submit(self) -> None:
        self.submit_button.click()

    def is_submitted_successfully(self) -> bool:
        return self.success_heading.is_visible()

    def has_required_field_labels(self) -> bool:
        return all(field.is_visible() for field in self.required_field_inputs)

    def has_newsletter_options(self) -> bool:
        return self.newsletter_yes.is_visible() and self.newsletter_no.is_visible()
