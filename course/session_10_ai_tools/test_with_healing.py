"""
Session 10 — tests that demonstrate self-healing selectors.

The heal_tracker fixture is injected via conftest.py.
Tests that use find_or_heal() will attempt the primary selector; if it
times out (because the selector is intentionally wrong here), Claude
generates a replacement and the heal is logged.

Run:  pytest course/session_10_ai_tools/test_with_healing.py -v -s
      ANTHROPIC_API_KEY must be set; tests skip otherwise.
"""
import os
import pytest
from playwright.sync_api import Page, expect

from course.framework.pages import LoginPage, InventoryPage
from course.framework.tools import HealTracker

BASE_URL = "https://www.saucedemo.com"
pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping self-healing tests",
)


def test_login_with_correct_selectors(inventory_page: InventoryPage):
    """Session 6 test still works — good selectors never trigger healing."""
    names = inventory_page.product_names()
    assert len(names) > 0, "Expected at least one product on the inventory page"


def test_heal_tracker_records_nothing_on_clean_run(
    inventory_page: InventoryPage, heal_tracker: HealTracker
):
    """When correct selectors are used, the heal log stays empty."""
    _ = inventory_page.product_names()
    assert heal_tracker.summary() == [], "No heals expected on a clean run"


def test_self_heal_stale_price_selector(page: Page, heal_tracker: HealTracker):
    """
    Demonstrate healing: deliberately use a wrong CSS class for the price.
    The tracker tries the stale selector, times out, asks Claude, and returns
    a working locator — the test still passes.
    """
    LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")

    # Correct selector: ".inventory_item_price"
    # Intentionally stale selector — simulates a CSS class rename after a redesign
    price_locator = heal_tracker.find_or_heal(
        page,
        selector=".item_price_amount",   # ← stale (does not exist)
        description="price label on each product card in the inventory list",
    )

    prices_text = price_locator.all_inner_texts()
    assert len(prices_text) > 0, "Healed locator should find price elements"
    heals = heal_tracker.summary()
    assert len(heals) == 1, f"Expected exactly 1 heal, got: {heals}"
    print(f"\n[demo] healed '{heals[0]['original']}' → '{heals[0]['healed']}'")


def test_heal_tracker_handles_multiple_stale_selectors(page: Page, heal_tracker: HealTracker):
    """Two stale selectors healed in one test — both logged independently."""
    LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")

    heal_tracker.find_or_heal(page, ".item_price_amount", "product price")
    heal_tracker.find_or_heal(page, ".product_title_text", "product name heading")

    assert len(heal_tracker.summary()) == 2
    heal_tracker.print_summary()
