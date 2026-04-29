from urllib.parse import urlencode

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.components import ProductCardComponent
from pages.models import ProductInfo, StoredProductInfo


class SearchResultsPage(BasePage):
    _PRODUCT_THUMBS = ".product-thumb"
    _NO_RESULTS = "//p[contains(text(),'There is no product that matches')]"

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

    def choose_list_view(self) -> None:
        self.wait_for_product_results()
        list_view = self.page.get_by_role("link", name="List")
        expect(list_view).to_be_visible()
        list_view.click()

    def sort_by_name_ascending(self) -> None:
        self.wait_for_product_results()
        sort_select = self.page.get_by_role("combobox", name="Sort By")
        expect(sort_select).to_be_visible()
        sort_select.select_option(label="Name (A - Z)")
        self.page.wait_for_load_state("domcontentloaded")
        self.wait_for_product_results()

    def product_names(self) -> list[str]:
        self.wait_for_product_results()
        return [card.name for card in self._cards()]

    def are_product_names_sorted_ascending(self) -> bool:
        names = self.product_names()
        return names == sorted(names, key=str.casefold)

    def stored_product_information(self) -> list[StoredProductInfo]:
        self.wait_for_product_results()
        return [card.stored_info() for card in self._cards()]

    def wait_for_product_results(self) -> None:
        self.wait_for_visible(self._PRODUCT_THUMBS)

    def _load_search(self, query: str) -> None:
        params = urlencode({"route": "product/search", "search": query})
        self.navigate(f"index.php?{params}")

    def _cards(self) -> list[ProductCardComponent]:
        thumbs = self.page.locator(self._PRODUCT_THUMBS)
        return [ProductCardComponent(thumbs.nth(i), i) for i in range(thumbs.count())]
