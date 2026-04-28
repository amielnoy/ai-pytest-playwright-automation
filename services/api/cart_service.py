import re

from services.rest_client import RestClient
from utils.price_parser import parse_price


class CartService:
    def __init__(self, client: RestClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def add_product(self, product_id: str, quantity: int = 1):
        return self.client.post(
            f"{self.base_url}/index.php",
            params={"route": "checkout/cart/add"},
            data={"product_id": product_id, "quantity": str(quantity)},
        )

    def get_cart(self):
        return self.client.get(
            f"{self.base_url}/index.php?route=checkout/cart",
        )

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
        row_price_strs = re.findall(
            r'<td class="text-right">\s*(\$[\d,]+\.?\d*)\s*</td>',
            product_section,
        )
        row_prices = [parse_price(price) for price in row_price_strs]
        return sum(price for price in row_prices if price is not None)
