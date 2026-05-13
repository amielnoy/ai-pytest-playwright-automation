from __future__ import annotations

import pytest

from course.framework.python_basics import (
    Product,
    affordable_products,
    assert_required_fields,
    format_test_id,
    normalize_text,
    parse_price,
    product_names,
)


def test_normalize_text_removes_extra_spaces() -> None:
    assert normalize_text("  Add   to   Cart  ") == "Add to Cart"


def test_parse_price_converts_currency_text() -> None:
    assert parse_price("$1,202.00") == 1202.0


def test_product_names_returns_names_in_order() -> None:
    products = [Product("MacBook", 602.0), Product("iPhone", 123.2)]

    assert product_names(products) == ["MacBook", "iPhone"]


def test_affordable_products_filters_by_stock_and_price() -> None:
    products = [
        Product("MacBook", 602.0),
        Product("iPhone", 123.2),
        Product("Apple Cinema 30", 110.0, in_stock=False),
    ]

    assert affordable_products(products, max_price=200) == [
        Product("iPhone", 123.2)
    ]


def test_assert_required_fields_accepts_complete_payload() -> None:
    assert_required_fields({"email": "user@example.com", "password": "secret"}, ["email"])


def test_assert_required_fields_reports_missing_values() -> None:
    with pytest.raises(AssertionError, match="email, password"):
        assert_required_fields({"email": "", "name": "Student"}, ["email", "password"])


def test_format_test_id_creates_readable_identifier() -> None:
    assert format_test_id("Search Results", "Sort A to Z") == "search_results__sort_a_to_z"
