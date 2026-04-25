import allure
import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage
from pages.register_page import RegisterPage
from utils.data_loader import get_test_data


@allure.feature("Registration")
@allure.story("User Account Creation")
@pytest.mark.registration
class TestRegistration:

    @allure.title("Successful new-user registration")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_new_user(self, page: Page, app_url: str):
        data = get_test_data("registration")

        home = HomePage(page, app_url)
        home.open()

        with allure.step("Navigate to Register page"):
            home.go_to_register()

        register = RegisterPage(page, app_url)

        with allure.step(f"Fill registration form for {data['email']}"):
            register.register(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                telephone=data["telephone"],
                password=data["password"],
                confirm_password=data["confirm_password"],
                newsletter=data["newsletter"],
            )

        with allure.step("Verify account created successfully"):
            assert register.is_registration_successful(), (
                f"Registration failed. Error: {register.get_error_message()}"
            )

    @allure.title("Registration fails with missing required fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_missing_fields(self, page: Page, app_url: str):
        home = HomePage(page, app_url)
        home.open()
        home.go_to_register()

        register = RegisterPage(page, app_url)

        with allure.step("Submit empty form"):
            register.register(
                first_name="",
                last_name="",
                email="",
                telephone="",
                password="",
                confirm_password="",
            )

        with allure.step("Verify validation errors appear"):
            error = register.get_error_message()
            assert error != "", "Expected validation error but got none"
