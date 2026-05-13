"""
Session 4 — Playwright Basics + First Browser Tests
E2E test: log in, add a product to the cart, verify cart shows one item.
"""

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"
CART_BADGE = ".shopping_cart_badge"
CART_LINK = ".shopping_cart_link"
CART_ITEM = ".cart_item"


def test_add_single_item_to_cart(logged_in_page: Page):
    logged_in_page.get_by_role("button", name="Add to cart").first.click()

    expect(logged_in_page.locator(CART_BADGE)).to_have_text("1")

    logged_in_page.locator(CART_LINK).click()
    expect(logged_in_page).to_have_url(f"{BASE_URL}/cart.html")
    expect(logged_in_page.locator(CART_ITEM)).to_have_count(1)


def test_add_multiple_items_updates_badge(logged_in_page: Page):
    buttons = logged_in_page.get_by_role("button", name="Add to cart").all()
    for btn in buttons[:3]:
        btn.click()

    expect(logged_in_page.locator(CART_BADGE)).to_have_text("3")


def test_remove_item_from_cart_updates_badge(logged_in_page: Page):
    logged_in_page.get_by_role("button", name="Add to cart").first.click()
    expect(logged_in_page.locator(CART_BADGE)).to_have_text("1")

    logged_in_page.get_by_role("button", name="Remove").first.click()

    expect(logged_in_page.locator(CART_BADGE)).not_to_be_visible()


def test_cart_contents_survive_navigation(logged_in_page: Page):
    logged_in_page.get_by_role("button", name="Add to cart").first.click()

    logged_in_page.get_by_role("link", name="About").click()
    logged_in_page.go_back()

    expect(logged_in_page.locator(CART_BADGE)).to_have_text("1")


def test_empty_cart_has_no_badge(logged_in_page: Page):
    expect(logged_in_page.locator(CART_BADGE)).not_to_be_visible()
