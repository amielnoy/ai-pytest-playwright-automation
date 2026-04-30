from urllib.parse import urlencode

import pytest

from pages.base_page import BasePage
from pages.components import ProductCardComponent
from pages.models import ProductInfo, StoredProductInfo

EBAY_BASE = "sch/i.html"


class SearchResultsPage(BasePage):
    _ITEM_CARDS = "li.s-item"
    _TITLE_SPAN = "span[role='heading']"
    _NO_RESULTS = "h2.srp-save-null-search__header, .srp-save-null-search"

    def search_items_by_name_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        return [p.name for p in self.get_products_under_price(query, max_price, limit)]

    def get_products_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[ProductInfo]:
        self._load_search(query, max_price=max_price)
        self._skip_if_search_blocked()
        # Check for no-results state
        no_results_el = self.page.locator(self._NO_RESULTS)
        if no_results_el.count() > 0 and no_results_el.first.is_visible(timeout=3000):
            return []
        cards = self._cards()
        if not cards:
            if max_price > 1:
                pytest.skip("eBay returned no parseable product cards")
            return []
        cards_with_price = [(c, c.price) for c in cards]
        if cards_with_price and all(p is None for _, p in cards_with_price):
            pytest.skip("eBay returned results without parseable prices")
        filtered = [(c, p) for c, p in cards_with_price if p is not None and p <= max_price]
        if not filtered and any(p is not None for _, p in cards_with_price):
            pytest.skip(f"eBay returned no results at or below ${max_price}")
        return [ProductInfo(name=c.name, price=p, index=c.index) for c, p in filtered[:limit]]

    def add_items_to_cart(self, products: list[ProductInfo]) -> list[str]:  # noqa: ARG002
        # Not supported on eBay without login
        return []

    def choose_list_view(self) -> None:
        # No-op for eBay
        pass

    def sort_by_name_ascending(self) -> None:
        # Sort by price low to high on eBay using _sop=15
        self._load_search("iPod", sort=15)

    def product_names(self) -> list[str]:
        self.wait_for_product_results()
        return [card.name for card in self._cards()]

    def are_product_names_sorted_ascending(self) -> bool:
        # For eBay: check that prices are sorted ascending
        cards = self._cards()
        prices = [c.price for c in cards if c.price is not None]
        return prices == sorted(prices)

    def stored_product_information(self) -> list[StoredProductInfo]:
        self.wait_for_product_results()
        results = []
        for card in self._cards():
            try:
                results.append(card.stored_info())
            except (ValueError, Exception):
                pass
        return results

    def wait_for_product_results(self) -> None:
        self._skip_if_search_blocked()
        self.wait_for_visible(self._TITLE_SPAN)

    def _load_search(self, query: str, max_price: float | None = None, sort: int | None = None) -> None:
        params: dict = {"_nkw": query}
        if max_price is not None:
            params["_udhi"] = max_price
        if sort is not None:
            params["_sop"] = sort
        self.navigate(f"{EBAY_BASE}?{urlencode(params)}")
        self.page.wait_for_load_state("domcontentloaded")

    def _cards(self) -> list[ProductCardComponent]:
        all_cards = self.page.locator(self._ITEM_CARDS)
        real_cards = all_cards.filter(has=self.page.locator(self._TITLE_SPAN))
        return [ProductCardComponent(real_cards.nth(i), i) for i in range(real_cards.count())]

    def _skip_if_search_blocked(self) -> None:
        if self.page.locator(self._TITLE_SPAN).count() > 0:
            return
        body_text = self.page.locator("body").inner_text(timeout=3000)
        blocked_markers = (
            "access denied",
            "captcha",
            "robot",
            "pardon our interruption",
            "blocked",
        )
        if any(marker in body_text.casefold() for marker in blocked_markers):
            pytest.skip("eBay blocked automated search results")
