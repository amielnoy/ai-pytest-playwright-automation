import os

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from utils.data_loader import get_config

CONFIG = get_config()
# GitHub Actions (and most CI systems) set CI=true; force headless there
_IN_CI = os.environ.get("CI", "").lower() in ("true", "1")


@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as pw:
        browser: Browser = getattr(pw, CONFIG["browser"]).launch(
            headless=_IN_CI or CONFIG["headless"],
            slow_mo=0 if _IN_CI else CONFIG["slow_mo"],
        )
        yield browser
        browser.close()


@pytest.fixture
def context(browser_instance: Browser):
    ctx: BrowserContext = browser_instance.new_context(
        viewport=CONFIG["viewport"],
        base_url=CONFIG["base_url"],
    )
    ctx.set_default_timeout(CONFIG["timeout"])
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    p = context.new_page()
    yield p
    p.close()


@pytest.fixture
def app_url() -> str:
    return CONFIG["base_url"]


# Attach a screenshot to Allure on test failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ARG001
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page_fixture = item.funcargs.get("page")
        if page_fixture:
            screenshot = page_fixture.screenshot()
            allure.attach(
                screenshot,
                name="screenshot_on_failure",
                attachment_type=allure.attachment_type.PNG,
            )
