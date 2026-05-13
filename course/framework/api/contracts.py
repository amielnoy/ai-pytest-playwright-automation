"""
Session 9 - API layer for the teaching framework.

The helpers here model the same idea used in production API tests: keep
contract and request-shaping logic reusable instead of copying it into tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApiCase:
    name: str
    method: str
    path: str
    expected_status: int
    expected_field: str | None = None


API_TEST_TYPES = {
    "smoke": "Endpoint is reachable and returns the expected status code.",
    "contract": "Response shape contains required fields and compatible types.",
    "negative": "Invalid input is rejected with a clear status and error message.",
    "state": "A write operation changes only the expected server-side state.",
    "integration": "Multiple API calls work together in one realistic flow.",
}


PUBLIC_ENDPOINT_CASES = [
    ApiCase("home page", "GET", "/", 200),
    ApiCase("search macbook", "GET", "/index.php?route=product/search&search=MacBook", 200),
    ApiCase("cart page", "GET", "/index.php?route=checkout/cart", 200),
]


def assert_status(actual_status: int, expected_status: int) -> None:
    assert actual_status == expected_status, (
        f"Expected HTTP {expected_status}, got HTTP {actual_status}"
    )


def assert_required_fields(payload: dict[str, Any], required_fields: dict[str, type]) -> None:
    missing = [field for field in required_fields if field not in payload]
    assert not missing, f"Missing required fields: {missing}"

    wrong_types = {
        field: type(payload[field]).__name__
        for field, expected_type in required_fields.items()
        if not isinstance(payload[field], expected_type)
    }
    assert not wrong_types, f"Fields with wrong types: {wrong_types}"


def assert_product_contract(product: dict[str, Any]) -> None:
    assert_required_fields(
        product,
        {
            "product_id": int,
            "name": str,
            "price": float,
        },
    )
    assert product["product_id"] > 0
    assert product["name"].strip()
    assert product["price"] >= 0


def normalize_query(value: str) -> str:
    """Small example of deterministic request-data preparation."""
    return value.strip().replace(" ", "+")


def build_search_path(query: str) -> str:
    return f"/index.php?route=product/search&search={normalize_query(query)}"
