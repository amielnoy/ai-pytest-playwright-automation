"""
Session 8 - Database Testing
Key concepts: isolated test databases, schema checks, data integrity,
transactions, migrations, and API-to-database assertions.

The reusable database helpers live in course.framework.database so this session
continues evolving the teaching framework instead of keeping logic in examples.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.database import (
    SEED_PRODUCTS,
    SCHEMA_SQL,
    ProductRow,
    add_cart_item,
    cart_total,
    connect_database,
    create_cart,
    create_schema,
    product_names,
    seed_products,
)

__all__ = [
    "SEED_PRODUCTS",
    "SCHEMA_SQL",
    "ProductRow",
    "add_cart_item",
    "cart_total",
    "connect_database",
    "create_cart",
    "create_schema",
    "product_names",
    "seed_products",
]


def demo() -> None:
    connection = connect_database()
    create_schema(connection)
    seed_products(connection)
    cart_id = create_cart(connection)
    add_cart_item(connection, cart_id, product_id=43, quantity=1)
    add_cart_item(connection, cart_id, product_id=40, quantity=2)

    print("Products:", product_names(connection))
    print("Cart ID:", cart_id)
    print("Cart total:", cart_total(connection, cart_id))


if __name__ == "__main__":
    demo()
