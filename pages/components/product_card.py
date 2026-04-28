from playwright.sync_api import Locator

from utils.price_parser import parse_price


class ProductCardComponent:
    """Scoped to a single .product-thumb locator, not the full page."""

    _NAME = "h4 a"
    _PRICE = ".price"
    _ADD_TO_CART = "button[onclick*='cart.add']"

    def __init__(self, root: Locator, index: int) -> None:
        self.root = root
        self.index = index

    @property
    def name(self) -> str:
        return self.root.locator(self._NAME).inner_text().strip()

    @property
    def price(self) -> float | None:
        return parse_price(self.root.locator(self._PRICE).inner_text())

    def add_to_cart(self) -> None:
        self.root.locator(self._ADD_TO_CART).click()
