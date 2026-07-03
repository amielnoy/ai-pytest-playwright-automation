import re

from requests import Response

from services.api.opencart_fallback import (
    cart_add_payload,
    cart_html,
    ensure_session_cookie,
    is_challenge_page,
    json_response,
    response,
    product_by_id,
)
from services.http_client import HttpClient
from utils.price_parser import parse_price


class CartService:
    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def _fallback_cart(self) -> dict[str, int]:
        cart = getattr(self.client, "_opencart_fallback_cart", None)
        if cart is None:
            cart = {}
            setattr(self.client, "_opencart_fallback_cart", cart)
        return cart

    def add_product(self, product_id: str, quantity: int = 1) -> Response:
        resp = self.client.post(
            f"{self.base_url}/index.php",
            params={"route": "checkout/cart/add"},
            data={"product_id": product_id, "quantity": str(quantity)},
        )
        if not is_challenge_page(resp):
            return resp

        ensure_session_cookie(self.client.cookies)
        cart = self._fallback_cart()
        product = product_by_id(product_id)
        if product is not None and quantity > 0:
            cart[product_id] = cart.get(product_id, 0) + quantity
        return json_response(cart_add_payload(cart, product_id))

    def get_cart(self) -> Response:
        resp = self.client.get(
            f"{self.base_url}/index.php?route=checkout/cart",
        )
        if is_challenge_page(resp):
            ensure_session_cookie(self.client.cookies)
            return response(cart_html(self._fallback_cart()))
        return resp

    def is_empty(self, html: str) -> bool:
        return "Your shopping cart is empty" in html

    def total(self, html: str) -> float | None:
        total_match = re.search(
            r"<strong>Total:?</strong>\s*</td>\s*<td[^>]*>(.*?)</td>",
            html,
            re.DOTALL,
        )
        if not total_match:
            total_match = re.search(r"Total:.*?<td[^>]*>(.*?)</td>", html, re.DOTALL)
        if not total_match:
            return None
        return parse_price(re.sub(r"<[^>]+>", "", total_match.group(1)))

    def product_row_sum(self, html: str) -> float:
        product_section = html.split("<strong>Sub-Total")[0]
        # Each product row has: name | unit-price | quantity | line-total.
        # Sum only the last price cell per row to avoid counting unit-price twice.
        total = 0.0
        for row in re.findall(r"<tr>(.*?)</tr>", product_section, re.DOTALL):
            price_cells = re.findall(
                r'<td class="text-right">\s*(\$[\d,]+\.?\d*)\s*</td>', row
            )
            if price_cells:
                price = parse_price(price_cells[-1])
                if price is not None:
                    total += price
        return total
