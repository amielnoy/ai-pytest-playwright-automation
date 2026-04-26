import os

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from utils.api_client import create_cart
from utils.data_loader import get_config, get_test_data

CONFIG = get_config()
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


@pytest.fixture
def api_cart(app_url: str):
    """
    Populate a cart via the OpenCart REST API (no browser) and return the
    server session cookie plus the products that were added.

    Each call gets its own OCSESSID so parallel workers never share
    server-side cart state.  The caller must inject the cookie into the
    Playwright BrowserContext before navigating to the cart page:

        context.add_cookies([{"name": "OCSESSID", "value": ocsessid, "url": app_url}])
    """
    data = get_test_data()
    search = data["search"]
    ocsessid, products = create_cart(
        base_url=app_url,
        query=search["query"],
        max_price=search["max_price"],
        limit=search["limit"],
    )
    assert products, (
        f"api_cart fixture: no products added for query='{search['query']}' "
        f"under ${search['max_price']}"
    )
    return ocsessid, products, data["cart"]["max_total"], search["max_price"]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
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
