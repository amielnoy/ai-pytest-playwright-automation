import allure

from pages.home_page import HomePage


@allure.feature("Intentional Failure")
@allure.story("Failing web UI script")
class TestIntentionalFailure:

    @allure.title("Home page title intentionally fails")
    @allure.severity(allure.severity_level.NORMAL)
    def test_home_page_title_intentional_failure(self, home_page: HomePage):
        with allure.step("Open the TutorialsNinja demo store home page"):
            home_page.open()

        with allure.step("Verify an intentionally incorrect page title"):
            assert home_page.title == "This title is expected to fail"
