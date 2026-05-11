"""Session 4 — typed test-data factories using Faker."""
from dataclasses import dataclass
from faker import Faker

_fake = Faker()


@dataclass
class CheckoutInfo:
    first_name: str
    last_name: str
    postal_code: str


@dataclass
class UserCredentials:
    username: str
    password: str


# Known saucedemo users
VALID_USERS = [
    UserCredentials("standard_user", "secret_sauce"),
    UserCredentials("performance_glitch_user", "secret_sauce"),
    UserCredentials("error_user", "secret_sauce"),
]
LOCKED_USER = UserCredentials("locked_out_user", "secret_sauce")


def make_checkout_info(missing: str | None = None) -> CheckoutInfo:
    """Return random checkout info; pass missing='first_name'|'last_name'|'postal_code'
    to leave that field blank (for validation-error tests)."""
    return CheckoutInfo(
        first_name="" if missing == "first_name" else _fake.first_name(),
        last_name="" if missing == "last_name" else _fake.last_name(),
        postal_code="" if missing == "postal_code" else _fake.postcode(),
    )


def make_user(name: str | None = None, job: str = "QA") -> dict:
    """Return a random user payload for reqres.in-style API tests."""
    return {"name": name or _fake.name(), "job": job}
