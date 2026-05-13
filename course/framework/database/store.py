"""
Session 8 - database layer for the teaching framework.

This module is intentionally small, but it follows the same direction as the
production framework: reusable setup and domain operations live outside tests.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProductRow:
    product_id: int
    name: str
    price: float
    stock: int


SCHEMA_SQL = """
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL CHECK (stock >= 0)
);

CREATE TABLE carts (
    cart_id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    cart_id INTEGER NOT NULL REFERENCES carts(cart_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (cart_id, product_id)
);
"""


SEED_PRODUCTS = [
    ProductRow(40, "iPhone", 123.20, 10),
    ProductRow(43, "MacBook", 602.00, 5),
    ProductRow(42, "Apple Cinema 30", 110.00, 2),
]


def connect_database(path: str | Path = ":memory:") -> sqlite3.Connection:
    """Create a SQLite connection configured like a test database."""
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_SQL)


def seed_products(connection: sqlite3.Connection) -> None:
    connection.executemany(
        "INSERT INTO products(product_id, name, price, stock) VALUES (?, ?, ?, ?)",
        [(p.product_id, p.name, p.price, p.stock) for p in SEED_PRODUCTS],
    )


def create_cart(connection: sqlite3.Connection) -> int:
    cursor = connection.execute("INSERT INTO carts DEFAULT VALUES")
    return int(cursor.lastrowid)


def add_cart_item(
    connection: sqlite3.Connection,
    cart_id: int,
    product_id: int,
    quantity: int,
) -> None:
    connection.execute(
        """
        INSERT INTO cart_items(cart_id, product_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(cart_id, product_id)
        DO UPDATE SET quantity = quantity + excluded.quantity
        """,
        (cart_id, product_id, quantity),
    )


def cart_total(connection: sqlite3.Connection, cart_id: int) -> float:
    row = connection.execute(
        """
        SELECT COALESCE(SUM(products.price * cart_items.quantity), 0) AS total
        FROM cart_items
        JOIN products USING(product_id)
        WHERE cart_items.cart_id = ?
        """,
        (cart_id,),
    ).fetchone()
    return float(row["total"])


def product_names(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT name FROM products ORDER BY name ASC"
    ).fetchall()
    return [str(row["name"]) for row in rows]
