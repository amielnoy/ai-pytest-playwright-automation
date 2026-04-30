from pages.cart_page import CartPage
from pages.models import ProductInfo
from pages.search_results_page import SearchResultsPage


class CartFlow:
    def __init__(
        self, search_results_page: SearchResultsPage, cart_page: CartPage
    ) -> None:
        self.results = search_results_page
        self.cart = cart_page

    def add_products_by_search(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        """Search for products under max_price, add them to the cart, and return their names."""
        products: list[ProductInfo] = self.results.get_products_under_price(
            query, max_price, limit
        )
        return self.results.add_items_to_cart(products)

    def open_cart(self) -> CartPage:
        self.cart.open()
        return self.cart
