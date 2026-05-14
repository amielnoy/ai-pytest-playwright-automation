import allure
import pytest

from tests.page_records import RegistrationPages


@allure.feature("Registration")
@allure.story("User Account Creation")
@pytest.mark.registration
class TestRegistration:

    @allure.title("Successful new-user registration")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("https://your-jira.atlassian.net/browse/TN-101", "TN-101")
    def test_register_new_user(
        self, registration_pages: RegistrationPages, registration_data: dict
    ):
        registration_pages.home.open()

        with allure.step("Navigate to Register page"):
            registration_pages.home.go_to_register()

        with allure.step(f"Fill registration form for {registration_data['email']}"):
            registration_pages.register.register(
                first_name=registration_data["first_name"],
                last_name=registration_data["last_name"],
                email=registration_data["email"],
                telephone=registration_data["telephone"],
                password=registration_data["password"],
                confirm_password=registration_data["confirm_password"],
                newsletter=registration_data["newsletter"],
            )

        with allure.step("Verify account created successfully"):
            assert registration_pages.register.is_registration_successful(), (
                f"Registration failed. Error: {registration_pages.register.get_error_message()}"
            )

    @allure.title("Registration fails with missing required fields")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.testcase("https://your-jira.atlassian.net/browse/TN-102", "TN-102")
    @allure.issue("https://your-jira.atlassian.net/browse/TN-BUG-12", "TN-BUG-12")
    def test_register_missing_fields(self, registration_pages: RegistrationPages):
        registration_pages.home.open()
        registration_pages.home.go_to_register()

        with allure.step("Submit empty form"):
            registration_pages.register.register(
                first_name="",
                last_name="",
                email="",
                telephone="",
                password="",
                confirm_password="",
            )

        with allure.step("Verify validation errors appear"):
            error = registration_pages.register.get_error_message()
            assert "First Name must be between 1 and 32 characters!" in error, (
                f"Expected first-name validation error, got: {error!r}"
            )
