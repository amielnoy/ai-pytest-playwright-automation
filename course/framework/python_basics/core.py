"""
Session 3 - Python foundations for automation testing.

These helpers keep the examples close to real test-automation work: parsing
test data, filtering records, validating required fields, and formatting clear
failure messages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Product:
    name: str
    price: float
    in_stock: bool = True


def normalize_text(value: str) -> str:
    """Trim extra whitespace and normalize repeated spaces."""

    return " ".join(value.strip().split())


def parse_price(raw_price: str) -> float:
    """Convert UI price text such as '$1,202.00' into a float."""

    cleaned = raw_price.replace("$", "").replace(",", "").strip()
    return float(cleaned)


def product_names(products: list[Product]) -> list[str]:
    return [product.name for product in products]


def affordable_products(products: list[Product], max_price: float) -> list[Product]:
    return [
        product
        for product in products
        if product.in_stock and product.price <= max_price
    ]


def assert_required_fields(payload: dict[str, Any], required_fields: list[str]) -> None:
    missing = [
        field
        for field in required_fields
        if field not in payload or payload[field] in {None, ""}
    ]
    if missing:
        raise AssertionError(f"Missing required fields: {', '.join(missing)}")


def format_test_id(feature: str, behavior: str) -> str:
    clean_feature = normalize_text(feature).lower().replace(" ", "_")
    clean_behavior = normalize_text(behavior).lower().replace(" ", "_")
    return f"{clean_feature}__{clean_behavior}"
