"""
Session 3 — Playwright Basics + Your First Python Framework
Product sort tests for saucedemo.com.
"""

import pytest
from playwright.sync_api import Page


def test_sort_price_low_to_high(logged_in_page: Page):
    logged_in_page.locator('[data-test="product_sort_container"]').select_option("lohi")

    prices = [
        float(p.inner_text().lstrip("$"))
        for p in logged_in_page.locator(".inventory_item_price").all()
    ]
    assert prices == sorted(prices), f"Prices not ascending: {prices}"


def test_sort_price_high_to_low(logged_in_page: Page):
    logged_in_page.locator('[data-test="product_sort_container"]').select_option("hilo")

    prices = [
        float(p.inner_text().lstrip("$"))
        for p in logged_in_page.locator(".inventory_item_price").all()
    ]
    assert prices == sorted(prices, reverse=True), f"Prices not descending: {prices}"


def test_sort_name_a_to_z(logged_in_page: Page):
    logged_in_page.locator('[data-test="product_sort_container"]').select_option("az")

    names = [
        n.inner_text()
        for n in logged_in_page.locator(".inventory_item_name").all()
    ]
    assert names == sorted(names), f"Names not A→Z: {names}"


def test_sort_name_z_to_a(logged_in_page: Page):
    logged_in_page.locator('[data-test="product_sort_container"]').select_option("za")

    names = [
        n.inner_text()
        for n in logged_in_page.locator(".inventory_item_name").all()
    ]
    assert names == sorted(names, reverse=True), f"Names not Z→A: {names}"


@pytest.mark.parametrize("option,label", [
    ("az", "Name (A to Z)"),
    ("za", "Name (Z to A)"),
    ("lohi", "Price (low to high)"),
    ("hilo", "Price (high to low)"),
])
def test_sort_dropdown_shows_correct_selected_label(logged_in_page: Page, option: str, label: str):
    sort = logged_in_page.locator('[data-test="product_sort_container"]')
    sort.select_option(option)
    assert sort.evaluate("el => el.options[el.selectedIndex].text") == label
