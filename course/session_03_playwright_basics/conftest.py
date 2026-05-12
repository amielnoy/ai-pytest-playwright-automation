"""
Session 3 — Playwright Basics + Your First Python Framework
Shared pytest fixtures for saucedemo.com tests.
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    page.goto(BASE_URL)
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(f"{BASE_URL}/inventory.html")
    return page
