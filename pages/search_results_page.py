from urllib.parse import urlencode

from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components import AlertComponent, ProductCardComponent
from pages.models import ProductInfo


class SearchResultsPage(BasePage):
    _PRODUCT_THUMBS = ".product-thumb"
    _NO_RESULTS = "//p[contains(text(),'There is no product that matches')]"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.alert = AlertComponent(page)

    def search_items_by_name_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        return [p.name for p in self.get_products_under_price(query, max_price, limit)]

    def get_products_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[ProductInfo]:
        self._load_search(query)
        if self.page.locator(self._NO_RESULTS).is_visible():
            return []
        # Snapshot price once per card to avoid a second DOM round-trip during list construction
        cards_with_price = [(c, c.price) for c in self._cards()]
        filtered = [(c, p) for c, p in cards_with_price if p is not None and p <= max_price]
        return [ProductInfo(name=c.name, price=p, index=c.index) for c, p in filtered[:limit]]

    def add_items_to_cart(self, products: list[ProductInfo]) -> list[str]:
        thumbs = self.page.locator(self._PRODUCT_THUMBS)
        added = []
        for product in products:
            card = ProductCardComponent(thumbs.nth(product.index), product.index)
            card.add_to_cart()
            self.alert.wait_for_success()
            added.append(product.name)
        return added

    def _load_search(self, query: str) -> None:
        params = urlencode({"route": "product/search", "search": query})
        self.navigate(f"index.php?{params}")

    def _cards(self) -> list[ProductCardComponent]:
        thumbs = self.page.locator(self._PRODUCT_THUMBS)
        return [ProductCardComponent(thumbs.nth(i), i) for i in range(thumbs.count())]
