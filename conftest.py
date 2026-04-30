import os

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from utils.data_loader import get_config

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
def context(request, browser_instance: Browser, tmp_path_factory):
    video_dir = tmp_path_factory.mktemp(request.node.name.replace("/", "_"))
    trace_file = video_dir / "trace.zip"
    ctx: BrowserContext = browser_instance.new_context(
        viewport=CONFIG["viewport"],
        base_url=CONFIG["base_url"],
        record_video={"dir": str(video_dir), "size": CONFIG["viewport"]},
    )
    ctx.set_default_timeout(CONFIG["timeout"])
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield ctx
    ctx.tracing.stop(path=str(trace_file))
    ctx.close()

    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        if trace_file.exists():
            allure.attach.file(
                str(trace_file),
                name="trace_on_failure",
                attachment_type=allure.attachment_type.ZIP,
            )

        video_files = sorted(video_dir.rglob("*.webm"))
        for index, video_path in enumerate(video_files, start=1):
            allure.attach.file(
                str(video_path),
                name=f"video_on_failure_{index}",
                attachment_type=allure.attachment_type.WEBM,
            )


@pytest.fixture
def page(context: BrowserContext) -> Page:
    p = context.new_page()
    yield p
    p.close()


@pytest.fixture
def app_url() -> str:
    return CONFIG["base_url"]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    if rep.when == "call" and rep.failed:
        page_fixture = item.funcargs.get("page")
        if page_fixture:
            screenshot = page_fixture.screenshot()
            allure.attach(
                screenshot,
                name="screenshot_on_failure",
                attachment_type=allure.attachment_type.PNG,
            )
