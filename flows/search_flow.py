from pages.home_page import HomePage
from pages.models import ProductInfo
from pages.search_results_page import SearchResultsPage


class SearchFlow:
    def __init__(
        self, home_page: HomePage, search_results_page: SearchResultsPage
    ) -> None:
        self.home = home_page
        self.results = search_results_page

    def search(self, query: str) -> SearchResultsPage:
        """Open home page, submit a search, and return the results page."""
        self.home.open()
        self.home.search(query)
        return self.results

    def search_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[ProductInfo]:
        """Return products matching query priced at or below max_price."""
        return self.results.get_products_under_price(query, max_price, limit)
