import json
import logging
import os
import pathlib
import socket
from collections.abc import Generator
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Route, Request, sync_playwright

import requests

from services.api.opencart_fallback import fallback_response_for_request, is_challenge_page
from requests.cookies import RequestsCookieJar
from utils.data_loader import get_config
from utils.logger import configure_logging, get_logger, AllureLogHandler

CONFIG = get_config()
LOGGER = get_logger("pytest")
_IN_CI = os.environ.get("CI", "").lower() in ("true", "1")


def _check_site_available(url: str, timeout: float = 5.0) -> bool:
    """The live demo store counts as available only if it is reachable *and*
    serving real store content. tutorialsninja.com is frequently bot-blocked
    (HTTP 415 / JS challenge), which is TCP-reachable but useless for the browser
    tests — so a plain socket connect is not enough. When the site is blocked we
    return False and the browser fallback route (offline OpenCart) is installed
    instead, exactly as it is when the host is unreachable.
    """
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        with socket.create_connection((host, port), timeout=timeout):
            pass
    except OSError:
        return False

    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
    except requests.RequestException:
        return False
    return resp.ok and not is_challenge_page(resp)


_SITE_AVAILABLE = _check_site_available(CONFIG["base_url"])


def _parse_cookies(cookie_header: str) -> RequestsCookieJar:
    jar = RequestsCookieJar()
    for part in cookie_header.split(";"):
        part = part.strip()
        if "=" in part:
            name, _, value = part.partition("=")
            jar.set(name.strip(), value.strip())
    return jar


def _make_fallback_route_handler(cart: dict[str, int]):
    def handle(route: Route, request: Request) -> None:
        # Only intercept navigation and AJAX; abort everything else (images, fonts, etc.)
        if request.resource_type not in ("document", "xhr", "fetch"):
            route.abort()
            return

        url = request.url
        method = request.method
        post_data: Any = None

        if method == "POST" and request.post_data:
            content_type = request.headers.get("content-type", "")
            try:
                if "application/json" in content_type:
                    post_data = json.loads(request.post_data)
                else:
                    parsed = parse_qs(request.post_data, keep_blank_values=True)
                    post_data = {k: v[0] for k, v in parsed.items()}
            except Exception:
                post_data = {}

        cookie_header = request.headers.get("cookie", "")
        jar = _parse_cookies(cookie_header)

        resp = fallback_response_for_request(
            method,
            url,
            params=None,
            data=post_data,
            cookies=jar,
            cart=cart,
        )

        ct = resp.headers.get("Content-Type", "text/html; charset=utf-8")
        route.fulfill(
            status=resp.status_code,
            headers={"Content-Type": ct},
            body=resp.content,
        )

    return handle
_ARTIFACTS_SETTING = os.environ.get("PW_RECORD_ARTIFACTS", "false").lower()
_RECORD_ARTIFACTS = _ARTIFACTS_SETTING in ("true", "1", "yes", "on")
_WEB_UI_TEST_ROOT = "tests/web-ui"
_IS_XDIST_CONTROLLER = False


def pytest_configure(config: pytest.Config) -> None:
    global _IS_XDIST_CONTROLLER
    worker_count = getattr(config.option, "numprocesses", None)
    _IS_XDIST_CONTROLLER = bool(worker_count) and not hasattr(config, "workerinput")
    configure_logging()
    LOGGER.info("pytest configured: %s", config.rootpath)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if item.path.as_posix().endswith(".py") and _WEB_UI_TEST_ROOT in item.path.as_posix():
            item.add_marker(pytest.mark.xdist_group("web-ui"))


def pytest_runtest_logstart(nodeid: str, location: tuple[str, int | None, str]) -> None:
    del location
    if _IS_XDIST_CONTROLLER:
        return
    LOGGER.info("test started: %s", nodeid)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if _IS_XDIST_CONTROLLER:
        return

    if report.outcome == "rerun":
        rerun_num = getattr(report, "rerun", 0)
        LOGGER.warning(
            "test rerun #%d: %s phase=%s duration=%.3fs",
            rerun_num,
            report.nodeid,
            report.when,
            report.duration,
        )
        return

    if report.when != "call" and report.outcome not in {"failed", "skipped"}:
        return

    LOGGER.info(
        "test %s: %s phase=%s duration=%.3fs",
        report.outcome,
        report.nodeid,
        report.when,
        report.duration,
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: object) -> None:
    """Mark tests that passed after a retry as flaky in the allure results.

    allure-pytest writes a separate result file per attempt (same historyId).
    Allure 3 reads statusDetails.flaky from the JSON, so we set it here on the
    passing attempt whenever a failed attempt exists for the same test.
    """
    del session, exitstatus
    results_dir = pathlib.Path("allure-results")
    if not results_dir.exists():
        return

    by_history: dict[str, list[tuple[pathlib.Path, dict]]] = {}
    for path in results_dir.glob("*-result.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            hid = data.get("historyId")
            if hid:
                by_history.setdefault(hid, []).append((path, data))
        except Exception:
            pass

    for entries in by_history.values():
        if len(entries) < 2:
            continue
        statuses = {d["status"] for _, d in entries}
        if "failed" not in statuses or "passed" not in statuses:
            continue
        for path, data in entries:
            if data["status"] == "passed":
                data.setdefault("statusDetails", {})["flaky"] = True
                path.write_text(json.dumps(data), encoding="utf-8")
                LOGGER.info("flaky marker written: %s", data.get("fullName", path.name))


def _node_failed(node) -> bool:
    return any(
        getattr(node, f"rep_{when}", None) is not None and getattr(node, f"rep_{when}").failed
        for when in ("setup", "call", "teardown")
    )


def _attach_pw_artifacts(node) -> None:
    """Attach trace + video saved on the node. Must be called from a pytest hook
    (not a fixture teardown) so allure writes into the test result, not a fixture container."""
    if getattr(node, "_pw_artifacts_attached", False) or not _node_failed(node):
        return

    trace_file = getattr(node, "_pw_trace_file", None)
    if trace_file and trace_file.exists():
        allure.attach.file(
            str(trace_file),
            name="trace_on_failure",
            attachment_type=allure.attachment_type.ZIP,
        )

    for index, video_path in enumerate(getattr(node, "_pw_video_files", []), start=1):
        if video_path.exists():
            allure.attach.file(
                str(video_path),
                name=f"video_on_failure_{index}",
                attachment_type=allure.attachment_type.WEBM,
            )

    node._pw_artifacts_attached = True


def _stop_tracing(node, context: BrowserContext) -> None:
    trace_file = getattr(node, "_pw_trace_file", None)
    if (
        getattr(node, "_pw_should_record_artifacts", False)
        and trace_file
        and not getattr(node, "_pw_trace_stopped", False)
    ):
        context.tracing.stop(path=str(trace_file))
        node._pw_trace_stopped = True


@pytest.fixture(scope="session")
def browser_instance() -> Generator[Browser, None, None]:
    with sync_playwright() as pw:
        browser: Browser = getattr(pw, CONFIG["browser"]).launch(
            headless=_IN_CI or CONFIG["headless"],
            slow_mo=0 if _IN_CI else CONFIG["slow_mo"],
        )
        yield browser
        browser.close()


@pytest.fixture
def context(
    request: pytest.FixtureRequest,
    browser_instance: Browser,
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[BrowserContext, None, None]:
    should_record_artifacts = _IN_CI or _RECORD_ARTIFACTS
    video_dir = (
        tmp_path_factory.mktemp(request.node.name.replace("/", "_"))
        if should_record_artifacts
        else None
    )
    trace_file = video_dir / "trace.zip" if video_dir else None
    request.node._pw_should_record_artifacts = should_record_artifacts
    request.node._pw_video_dir = video_dir
    request.node._pw_trace_file = trace_file
    request.node._pw_trace_stopped = False
    request.node._pw_artifacts_attached = False
    context_options = {
        "viewport": CONFIG["viewport"],
        "base_url": CONFIG["base_url"],
    }
    if video_dir:
        context_options.update(
            {
                "record_video_dir": video_dir,
                "record_video_size": CONFIG["viewport"],
            }
        )

    ctx: BrowserContext = browser_instance.new_context(**context_options)
    ctx.set_default_timeout(CONFIG["timeout"])
    if not _SITE_AVAILABLE:
        per_context_cart: dict[str, int] = {}
        ctx.route("**/tutorialsninja.com/**", _make_fallback_route_handler(per_context_cart))
    if should_record_artifacts:
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield ctx
    _stop_tracing(request.node, ctx)
    ctx.close()
    # Save video files on the node — actual attachment happens in makereport(teardown)
    # so allure writes into the test result scope, not the fixture container scope.
    if should_record_artifacts and video_dir:
        request.node._pw_video_files = sorted(video_dir.rglob("*.webm"))


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    p = context.new_page()
    yield p
    p.close()


@pytest.fixture
def app_url() -> str:
    return CONFIG["base_url"]


@pytest.fixture(autouse=True)
def log(request: pytest.FixtureRequest) -> Generator[logging.Logger, None, None]:
    logger = get_logger(request.node.name)
    handler = AllureLogHandler()
    logging.getLogger().addHandler(handler)
    logger.info("START %s", request.node.nodeid)
    yield logger
    logger.info("END   %s", request.node.nodeid)
    handler.flush_to_allure(attachment_name="Logs")
    logging.getLogger().removeHandler(handler)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: pytest.CallInfo[Any]) -> Generator[None, Any, None]:
    del call
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    if rep.skipped:
        reason = rep.longrepr[2] if isinstance(rep.longrepr, tuple) else str(rep.longrepr)
        allure.dynamic.description(reason)

    if rep.when == "call" and rep.failed:
        page_fixture = cast(Page | None, item.funcargs.get("page"))
        if page_fixture:
            try:
                screenshot = page_fixture.screenshot()
                allure.attach(
                    screenshot,
                    name="screenshot_on_failure",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass

    if rep.when == "teardown":
        # Attach trace + video here, after all fixture teardowns have run and written
        # their files, but while the allure test lifecycle is still open.
        _attach_pw_artifacts(item)
