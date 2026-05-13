"""
Session 9 - API Testing
Key concepts: HTTP status codes, response contracts, JSON assertions,
session isolation, negative testing, and service-layer clients.

The reusable API helpers live in course.framework.api so this session continues
evolving the teaching framework instead of keeping logic in examples.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.api import (
    API_TEST_TYPES,
    PUBLIC_ENDPOINT_CASES,
    ApiCase,
    assert_product_contract,
    assert_required_fields,
    assert_status,
    build_search_path,
    normalize_query,
)

__all__ = [
    "API_TEST_TYPES",
    "PUBLIC_ENDPOINT_CASES",
    "ApiCase",
    "assert_product_contract",
    "assert_required_fields",
    "assert_status",
    "build_search_path",
    "normalize_query",
]


def demo() -> None:
    print("API test types:")
    for key, description in API_TEST_TYPES.items():
        print(f"- {key}: {description}")

    print("\nExample endpoint cases:")
    for case in PUBLIC_ENDPOINT_CASES:
        print(f"- {case.method} {case.path} -> {case.expected_status}")

    print("\nSearch path:", build_search_path("Apple Cinema"))


if __name__ == "__main__":
    demo()
