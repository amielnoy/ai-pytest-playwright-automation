"""In-memory product catalogue for the OpenCart offline fallback.

The demo store's data is small and stable, so the fallback serves it from this
fixed catalogue instead of the live site. Kept separate from response building,
HTML templating, and request routing so each concern can change independently.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    price: float


PRODUCTS = (
    Product("43", "MacBook", 602.0),
    Product("45", "MacBook Pro", 2000.0),
    Product("40", "iPhone", 123.2),
    Product("36", "iPod Nano", 122.0),
    Product("30", "Canon EOS 5D", 98.0),
    Product("28", "Samsung SyncMaster 941BW", 242.0),
)


def search_products(query: str, sort: str = "", order: str = "ASC") -> list[Product]:
    normalized = query.casefold()
    results = [p for p in PRODUCTS if normalized and normalized in p.name.casefold()]
    if sort == "name":
        results = sorted(results, key=lambda p: p.name.casefold(), reverse=(order.upper() == "DESC"))
    return results


def product_by_id(product_id: str) -> Product | None:
    return next((p for p in PRODUCTS if p.product_id == product_id), None)
