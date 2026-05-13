"""
Session 3 - Python Foundations

Runnable examples for the Python syntax and data structures used throughout
the automation framework.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.python_basics import (  # noqa: E402
    Product,
    affordable_products,
    assert_required_fields,
    format_test_id,
    normalize_text,
    parse_price,
    product_names,
)


def build_demo_products() -> list[Product]:
    return [
        Product(name="MacBook", price=parse_price("$602.00")),
        Product(name="iPhone", price=parse_price("$123.20")),
        Product(name="Apple Cinema 30", price=parse_price("$110.00"), in_stock=False),
    ]


def demo() -> None:
    products = build_demo_products()
    print("Normalized text:", normalize_text("  Add   to   Cart  "))
    print("Product names:", product_names(products))
    print("Affordable:", product_names(affordable_products(products, max_price=200)))
    print("Test ID:", format_test_id("Search Results", "Sort A to Z"))

    user = {"email": "student@example.com", "password": "secret"}
    assert_required_fields(user, ["email", "password"])
    print("Required fields: ok")


if __name__ == "__main__":
    demo()


__all__ = [
    "Product",
    "affordable_products",
    "assert_required_fields",
    "build_demo_products",
    "format_test_id",
    "normalize_text",
    "parse_price",
    "product_names",
]
