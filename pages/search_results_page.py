from urllib.parse import urlencode

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.components import ProductCardComponent
from pages.models import ProductInfo, StoredProductInfo


class SearchResultsPage(BasePage):
    _PRODUCT_THUMBS = ".product-thumb"
    _NO_RESULTS_TEXT = "There is no product that matches the search criteria."
    _PRODUCT_TITLE_SELECTOR = "h4"
    _PRODUCT_LINK_ROLE = "link"
    _LIST_VIEW_BUTTON = "#list-view"
    _SORT_SELECT_ROLE = "combobox"
    _SORT_SELECT_NAME = "Sort By"
    _SORT_NAME_ASCENDING_LABEL = "Name (A - Z)"
    _SEARCH_ROUTE = "product/search"
    _SEARCH_PATH_PREFIX = "index.php?"

    def search_items_by_name_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        return [p.name for p in self.get_products_under_price(query, max_price, limit)]

    def get_products_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[ProductInfo]:
        self._load_search(query)
        if self.page.get_by_text(self._NO_RESULTS_TEXT).is_visible():
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

    def open_product(self, product_name: str) -> None:
        product_link = self.page.get_by_role(
            self._PRODUCT_LINK_ROLE, name=product_name, exact=True
        )
        self.page.locator(self._PRODUCT_THUMBS).filter(
            has=product_link
        ).first.locator(self._PRODUCT_TITLE_SELECTOR).get_by_role(
            self._PRODUCT_LINK_ROLE, name=product_name, exact=True
        ).click()
        self.page.wait_for_load_state("domcontentloaded")

    def choose_list_view(self) -> None:
        self.wait_for_product_results()
        list_view = self.page.locator(self._LIST_VIEW_BUTTON)
        expect(list_view).to_be_visible()
        list_view.click()

    def sort_by_name_ascending(self) -> None:
        self.wait_for_product_results()
        sort_select = self.page.get_by_role(
            self._SORT_SELECT_ROLE, name=self._SORT_SELECT_NAME
        )
        expect(sort_select).to_be_visible()
        sort_select.select_option(label=self._SORT_NAME_ASCENDING_LABEL)
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
        params = urlencode({"route": self._SEARCH_ROUTE, "search": query})
        self.navigate(f"{self._SEARCH_PATH_PREFIX}{params}")

    def _cards(self) -> list[ProductCardComponent]:
        thumbs = self.page.locator(self._PRODUCT_THUMBS)
        return [ProductCardComponent(thumbs.nth(i), i) for i in range(thumbs.count())]
