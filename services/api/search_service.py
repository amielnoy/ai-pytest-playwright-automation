import re
from dataclasses import dataclass

from requests import Response

from services.rest_client import RestClient
from utils.price_parser import parse_price


@dataclass(frozen=True)
class SearchCase:
    query: str
    expected_names: tuple[str, ...]
    min_cards: int


class SearchService:
    def __init__(self, client: RestClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def search(self, query: str) -> Response:
        return self.client.get(
            f"{self.base_url}/index.php",
            params={"route": "product/search", "search": query},
        )

    def product_cards(self, html: str) -> list[str]:
        return re.findall(r'class="product-thumb"', html)

    def product_names(self, html: str) -> list[str]:
        return re.findall(r"<h4>\s*<a[^>]*>([^<]+)</a>", html)

    def product_ids(self, html: str) -> list[str]:
        return re.findall(r"cart\.add\('(\d+)'", html)

    def prices(self, html: str) -> list[float]:
        raw_blocks = re.findall(r'class="price">(.*?)</p>', html, re.DOTALL)
        parsed = [
            parse_price(re.sub(r"<[^>]+>", "", block)) for block in raw_blocks
        ]
        return [price for price in parsed if price is not None]

    def first_product_id(self, query: str) -> str:
        resp = self.search(query)
        pids = self.product_ids(resp.text)
        assert pids, f"No products found for query '{query}'"
        return pids[0]
