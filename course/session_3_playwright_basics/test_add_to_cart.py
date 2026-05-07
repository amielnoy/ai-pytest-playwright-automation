"""
Session 3 — Playwright Basics + Your First Python Framework
E2E test: log in, add a product to the cart, verify cart shows one item.
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_add_single_item_to_cart(logged_in_page: Page):
    logged_in_page.get_by_role("button", name="Add to cart").first.click()

    cart_badge = logged_in_page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("1")

    logged_in_page.locator(".shopping_cart_link").click()
    expect(logged_in_page).to_have_url(f"{BASE_URL}/cart.html")

    cart_items = logged_in_page.locator(".cart_item")
    expect(cart_items).to_have_count(1)


def test_add_multiple_items_updates_badge(logged_in_page: Page):
    buttons = logged_in_page.get_by_role("button", name="Add to cart").all()
    for btn in buttons[:3]:
        btn.click()

    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_text("3")


def test_remove_item_from_cart_updates_badge(logged_in_page: Page):
    logged_in_page.get_by_role("button", name="Add to cart").first.click()
    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_text("1")

    logged_in_page.get_by_role("button", name="Remove").first.click()

    expect(logged_in_page.locator(".shopping_cart_badge")).not_to_be_visible()


def test_cart_contents_survive_navigation(logged_in_page: Page):
    logged_in_page.get_by_role("button", name="Add to cart").first.click()

    logged_in_page.get_by_role("link", name="About").click()
    logged_in_page.go_back()

    expect(logged_in_page.locator(".shopping_cart_badge")).to_have_text("1")


def test_empty_cart_has_no_badge(logged_in_page: Page):
    expect(logged_in_page.locator(".shopping_cart_badge")).not_to_be_visible()
