"""Faker-backed test-data factories — SOLID-compliant dynamic test inputs.

SOLID mapping:
  S — each dataclass has one responsibility: describing one entity's fields.
      Serialisation (asdict) lives in callers, not in the class.
  O — every factory is extended via **overrides; no function body modification needed.
  L — not applicable (no inheritance hierarchy).
  I — FakerLike exposes only the methods each factory actually calls.
  D — factories depend on FakerLike (abstraction), not on Faker (concretion).
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from faker import Faker

_fake = Faker()

_KNOWN_PRODUCTS: tuple[str, ...] = (
    "MacBook", "iPhone", "Samsung", "iPod", "Canon", "HTC", "Palm", "Sony",
)


# ---------------------------------------------------------------------------
# I + D — thin protocol: factories depend only on the surface they actually use
# ---------------------------------------------------------------------------

@runtime_checkable
class FakerLike(Protocol):
    def first_name(self) -> str: ...
    def last_name(self) -> str: ...
    def password(
        self,
        length: int = ...,
        special_chars: bool = ...,
        digits: bool = ...,
        upper_case: bool = ...,
        lower_case: bool = ...,
    ) -> str: ...
    def numerify(self, text: str = ...) -> str: ...
    def uuid4(self) -> Any: ...
    def random_element(self, elements: Sequence) -> Any: ...
    def pyfloat(
        self,
        left_digits: int | None = ...,
        right_digits: int | None = ...,
        positive: bool | None = ...,
        min_value: float | int | None = ...,
        max_value: float | int | None = ...,
    ) -> float: ...
    def random_int(self, min: int = ..., max: int = ..., step: int = ...) -> int: ...  # noqa: A002


# ---------------------------------------------------------------------------
# S — plain data containers; no serialisation methods
# ---------------------------------------------------------------------------

@dataclass
class RegistrationData:
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    telephone: str
    newsletter: bool = False


@dataclass
class SearchData:
    query: str
    max_price: float
    limit: int


@dataclass
class CartScenario:
    query: str
    max_price: float
    limit: int
    max_total: float


@dataclass
class LoginCredentials:
    email: str
    password: str


# ---------------------------------------------------------------------------
# O + D — **overrides extends any field without modifying function bodies;
#          fake: FakerLike | None allows swapping the generator in tests
# ---------------------------------------------------------------------------

def make_registration(
    fake: FakerLike | None = None,
    **overrides,
) -> RegistrationData:
    """Return a RegistrationData with Faker values.

    Pass keyword overrides to set specific fields, e.g.::

        make_registration(first_name="")   # blank for validation tests
        make_registration(fake=mock_faker) # injected generator for unit tests
    """
    f = fake or _fake
    pw = f.password(
        length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
    )
    fields: dict = dict(
        first_name=f.first_name(),
        last_name=f.last_name(),
        email=f"auto+{f.uuid4()[:8]}@example.com",
        password=pw,
        confirm_password=pw,
        telephone=f.numerify("05########"),
        newsletter=False,
    )
    fields.update(overrides)
    return RegistrationData(**fields)


def make_search(
    fake: FakerLike | None = None,
    products: Sequence[str] | None = None,
    **overrides,
) -> SearchData:
    """Return a SearchData.

    Pass ``products`` to extend the pool of known queries without touching
    this function body (Open/Closed).
    """
    f = fake or _fake
    available = products or _KNOWN_PRODUCTS
    fields: dict = dict(
        query=f.random_element(available),
        max_price=round(
            f.pyfloat(min_value=200, max_value=2000, right_digits=2), 2
        ),
        limit=f.random_int(min=1, max=10),
    )
    fields.update(overrides)
    return SearchData(**fields)


def make_cart_scenario(
    fake: FakerLike | None = None,
    **overrides,
) -> CartScenario:
    f = fake or _fake
    query = overrides.pop("query", "MacBook")
    max_price = overrides.pop("max_price", 700.0)
    s = make_search(fake=f, query=query, max_price=max_price)
    fields: dict = dict(
        query=s.query,
        max_price=s.max_price,
        limit=s.limit,
        max_total=round(s.max_price * 5, 2),
    )
    fields.update(overrides)
    return CartScenario(**fields)


def make_invalid_credentials(
    fake: FakerLike | None = None,
    **overrides,
) -> LoginCredentials:
    """Return credentials guaranteed not to match any real account."""
    f = fake or _fake
    fields: dict = dict(
        email=f"invalid+{f.uuid4()[:8]}@nowhere.example",
        password=f.password(length=8),
    )
    fields.update(overrides)
    return LoginCredentials(**fields)
