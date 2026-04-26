"""
Lightweight REST API client for creating test fixtures without a browser.

Uses OpenCart's standard AJAX endpoints:
  GET  /index.php?route=product/search&search=<query>  -> HTML with product cards
  POST /index.php?route=checkout/cart/add              -> adds product to session cart

Each call creates an independent requests.Session (own OCSESSID), so parallel
workers never share server-side cart state.
"""
import re
from dataclasses import dataclass

import requests

from utils.price_parser import parse_price

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; test-fixture-client/1.0)",
    "X-Requested-With": "XMLHttpRequest",
}


@dataclass
class ApiProduct:
    product_id: str
    name: str
    price: float


def _fetch(session: requests.Session, url: str) -> str:
    resp = session.get(url, headers=_HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def _parse_cards(html: str, max_price: float, limit: int) -> list[tuple[str, str, float]]:
    """
    Extract (product_id, name, price) from search-results HTML.
    Chunks the page by .product-thumb blocks so each field stays correlated.
    """
    results: list[tuple[str, str, float]] = []
    for chunk in re.split(r'class="product-thumb"', html)[1:]:
        pid = re.search(r"cart\.add\('(\d+)'", chunk)
        name = re.search(r"<h4>\s*<a[^>]*>([^<]+)</a>", chunk)
        price_block = re.search(r'class="price">(.*?)</p>', chunk, re.DOTALL)

        if not (pid and name and price_block):
            continue

        price = parse_price(re.sub(r"<[^>]+>", "", price_block.group(1)))
        if price is None or price > max_price:
            continue

        results.append((pid.group(1), name.group(1).strip(), price))
        if len(results) >= limit:
            break

    return results


def create_cart(
    base_url: str, query: str, max_price: float, limit: int
) -> tuple[str, list[ApiProduct]]:
    """
    Search for products matching *query* under *max_price* and add up to
    *limit* of them to a fresh cart session.

    Returns (ocsessid, products_added).  Each invocation gets its own
    OCSESSID so parallel calls never collide on the server.
    """
    session = requests.Session()

    html = _fetch(session, f"{base_url}/index.php?route=product/search&search={query}")
    candidates = _parse_cards(html, max_price, limit)

    if not candidates:
        raise ValueError(f"No products found for query='{query}' under ${max_price}")

    added: list[ApiProduct] = []
    for pid, name, price in candidates:
        resp = session.post(
            f"{base_url}/index.php?route=checkout/cart/add",
            data={"product_id": pid, "quantity": "1"},
            headers=_HEADERS,
            timeout=15,
        )
        if resp.ok:
            added.append(ApiProduct(product_id=pid, name=name, price=price))

    ocsessid = session.cookies.get("OCSESSID", "")
    return ocsessid, added
