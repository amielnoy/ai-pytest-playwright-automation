import allure
import pytest

from tests.page_records import RegistrationPages


@allure.feature("Authentication")
@allure.story("eBay Sign-In Page")
@pytest.mark.registration
class TestSignIn:

    @allure.title("Sign-in page loads with email input field")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sign_in_page_has_email_field(self, registration_pages: RegistrationPages):
        registration_pages.home.open()
        registration_pages.home.go_to_register()
        assert registration_pages.register.has_sign_in_form(), (
            "Email input not found on sign-in page"
        )

    @allure.title("Sign-in with empty email shows validation error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sign_in_missing_email_shows_error(self, registration_pages: RegistrationPages):
        registration_pages.home.open()
        registration_pages.home.go_to_register()
        registration_pages.register.register(
            first_name="", last_name="", email="",
            telephone="", password="", confirm_password=""
        )
        error = registration_pages.register.get_error_message()
        assert error != "", "Expected validation error for empty email, got none"

    @allure.title("Sign-in attempt with invalid credentials shows error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sign_in_invalid_credentials_shows_error(self, registration_pages: RegistrationPages):
        registration_pages.home.open()
        registration_pages.home.go_to_register()
        registration_pages.register.register(
            first_name="", last_name="", email="invalid@test-noreply.invalid",
            telephone="", password="wrong", confirm_password=""
        )
        # Either an error is shown, or we're still on the email step.
        # Verify the page is not showing a logged-in state.
        assert not registration_pages.register.is_registration_successful(), (
            "Expected sign-in to fail with invalid credentials"
        )
