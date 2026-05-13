import sqlite3

import pytest

from course.framework.database import (
    add_cart_item,
    cart_total,
    connect_database,
    create_cart,
    create_schema,
    seed_products,
)


@pytest.fixture
def db():
    connection = connect_database()
    create_schema(connection)
    seed_products(connection)
    yield connection
    connection.close()


def test_cart_total_sums_price_times_quantity(db):
    cart_id = create_cart(db)

    add_cart_item(db, cart_id, product_id=43, quantity=1)
    add_cart_item(db, cart_id, product_id=40, quantity=2)

    assert cart_total(db, cart_id) == 848.4


def test_duplicate_cart_item_updates_quantity_instead_of_inserting_row(db):
    cart_id = create_cart(db)

    add_cart_item(db, cart_id, product_id=43, quantity=1)
    add_cart_item(db, cart_id, product_id=43, quantity=2)

    rows = db.execute(
        "SELECT product_id, quantity FROM cart_items WHERE cart_id = ?",
        (cart_id,),
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["product_id"] == 43
    assert rows[0]["quantity"] == 3


def test_product_price_constraint_rejects_negative_values(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO products(product_id, name, price, stock) VALUES (?, ?, ?, ?)",
            (999, "Broken Product", -1.0, 1),
        )


def test_cart_item_foreign_key_rejects_unknown_product(db):
    cart_id = create_cart(db)

    with pytest.raises(sqlite3.IntegrityError):
        add_cart_item(db, cart_id, product_id=999999, quantity=1)
