"""tests/conftest.py — shared constants and fixture registration.

All fixtures live in tests/fixtures/; pytest discovers them via pytest_plugins.
"""
from services.api.public_service import EndpointCase
from services.api.search_service import SearchCase

pytest_plugins = [
    "tests.fixtures.services",
    "tests.fixtures.pages",
    "tests.fixtures.flows",
    "tests.fixtures.data",
    "tests.fixtures.chat",
]

# ---------------------------------------------------------------------------
# Shared test-case maps (used by contract tests and data-driven API tests)
# ---------------------------------------------------------------------------

PUBLIC_ENDPOINT_MAP = {
    "home": EndpointCase(path="", required_text="Your Store"),
    "search": EndpointCase(
        path="/index.php?route=product/search&search=MacBook",
        required_text="MacBook",
    ),
    "cart": EndpointCase(
        path="/index.php?route=checkout/cart",
        required_text="Shopping Cart",
    ),
    "register": EndpointCase(
        path="/index.php?route=account/register",
        required_text="Register Account",
    ),
    "login": EndpointCase(
        path="/index.php?route=account/login",
        required_text="Returning Customer",
    ),
}

SEARCH_QUERY_MAP = {
    "macbook": SearchCase(
        query="MacBook",
        expected_names=("MacBook",),
        min_cards=1,
    ),
    "iphone": SearchCase(
        query="iPhone",
        expected_names=("iPhone",),
        min_cards=1,
    ),
}
