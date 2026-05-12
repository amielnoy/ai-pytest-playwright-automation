"""
Session 3 — Playwright Basics + Your First Python Framework
Parametrized negative login tests for saucedemo.com.
"""

import pytest
from playwright.sync_api import Page, expect

BASE = "https://www.saucedemo.com"


@pytest.mark.parametrize(
    "user, pwd, msg",
    [
        ("locked_out_user", "secret_sauce", "locked out"),
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("standard_user", "wrong", "do not match"),
    ],
)
def test_login_negative(page: Page, user: str, pwd: str, msg: str):
    page.goto(BASE)
    page.get_by_placeholder("Username").fill(user)
    page.get_by_placeholder("Password").fill(pwd)
    page.get_by_role("button", name="Login").click()

    error = page.locator('[data-test="error"]')
    expect(error).to_contain_text(msg)
    expect(page).not_to_have_url(f"{BASE}/inventory.html")


def test_successful_login_redirects_to_inventory(page: Page):
    page.goto(BASE)
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(f"{BASE}/inventory.html")
    expect(page.get_by_role("button", name="Add to cart").first).to_be_visible()


def test_failed_login_does_not_set_session_cookie(page: Page, context):
    page.goto(BASE)
    page.get_by_placeholder("Username").fill("wrong_user")
    page.get_by_placeholder("Password").fill("wrong_pass")
    page.get_by_role("button", name="Login").click()

    cookies = context.cookies()
    session_cookies = [c for c in cookies if "session" in c["name"].lower()]
    assert session_cookies == [], f"Unexpected session cookie set on failed login: {session_cookies}"


def test_logout_clears_session(page: Page):
    page.goto(BASE)
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(f"{BASE}/inventory.html")

    page.get_by_role("button", name="Open Menu").click()
    page.get_by_role("link", name="Logout").click()

    expect(page).to_have_url(BASE + "/")
    page.goto(f"{BASE}/inventory.html")
    expect(page).to_have_url(BASE + "/")
