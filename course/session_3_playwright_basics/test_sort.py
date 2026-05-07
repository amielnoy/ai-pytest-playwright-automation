"""
Session 3 — Playwright Basics + Your First Python Framework
Product sort tests for saucedemo.com.
"""

import pytest
from playwright.sync_api import Page, expect

SORT_CONTAINER = '[data-test="product_sort_container"]'
ITEM_PRICE = ".inventory_item_price"
ITEM_NAME = ".inventory_item_name"


def test_sort_price_low_to_high(logged_in_page: Page):
    logged_in_page.locator(SORT_CONTAINER).select_option("lohi")

    prices = [
        float(p.inner_text().lstrip("$"))
        for p in logged_in_page.locator(ITEM_PRICE).all()
    ]
    assert prices == sorted(prices), f"Prices not ascending: {prices}"


def test_sort_price_high_to_low(logged_in_page: Page):
    logged_in_page.locator(SORT_CONTAINER).select_option("hilo")

    prices = [
        float(p.inner_text().lstrip("$"))
        for p in logged_in_page.locator(ITEM_PRICE).all()
    ]
    assert prices == sorted(prices, reverse=True), f"Prices not descending: {prices}"


def test_sort_name_a_to_z(logged_in_page: Page):
    logged_in_page.locator(SORT_CONTAINER).select_option("az")

    names = [n.inner_text() for n in logged_in_page.locator(ITEM_NAME).all()]
    assert names == sorted(names), f"Names not A→Z: {names}"


def test_sort_name_z_to_a(logged_in_page: Page):
    logged_in_page.locator(SORT_CONTAINER).select_option("za")

    names = [n.inner_text() for n in logged_in_page.locator(ITEM_NAME).all()]
    assert names == sorted(names, reverse=True), f"Names not Z→A: {names}"


@pytest.mark.parametrize("option,label", [
    ("az", "Name (A to Z)"),
    ("za", "Name (Z to A)"),
    ("lohi", "Price (low to high)"),
    ("hilo", "Price (high to low)"),
])
def test_sort_dropdown_shows_correct_selected_label(logged_in_page: Page, option: str, label: str):
    sort = logged_in_page.locator(SORT_CONTAINER)
    sort.select_option(option)
    expect(sort.locator("option:checked")).to_have_text(label)
