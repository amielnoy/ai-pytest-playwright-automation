"""
Session 10 — Advanced Playwright: POM + UI + API
Test data factory using faker for generating realistic test inputs.
"""

from dataclasses import dataclass
from faker import Faker

fake = Faker()


@dataclass
class CheckoutInfo:
    first_name: str
    last_name: str
    postal_code: str


@dataclass
class UserCredentials:
    username: str
    password: str


@dataclass
class ProductOrder:
    product_name: str
    quantity: int


VALID_USERS = [
    UserCredentials("standard_user", "secret_sauce"),
    UserCredentials("performance_glitch_user", "secret_sauce"),
    UserCredentials("error_user", "secret_sauce"),
]

LOCKED_USER = UserCredentials("locked_out_user", "secret_sauce")


def make_checkout_info() -> CheckoutInfo:
    return CheckoutInfo(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        postal_code=fake.postcode(),
    )


def make_incomplete_checkout_info(missing: str = "first_name") -> CheckoutInfo:
    info = make_checkout_info()
    return CheckoutInfo(
        first_name="" if missing == "first_name" else info.first_name,
        last_name="" if missing == "last_name" else info.last_name,
        postal_code="" if missing == "postal_code" else info.postal_code,
    )


def make_product_order(product_name: str = "Sauce Labs Backpack", quantity: int = 1) -> ProductOrder:
    return ProductOrder(product_name=product_name, quantity=quantity)


if __name__ == "__main__":
    print(f"Checkout info:            {make_checkout_info()}")
    print(f"Missing first name:       {make_incomplete_checkout_info('first_name')}")
    print(f"Missing postal code:      {make_incomplete_checkout_info('postal_code')}")
    print(f"Product order:            {make_product_order()}")
    print(f"Valid users: {VALID_USERS}")
