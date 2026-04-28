import re

from playwright.sync_api import Locator

from pages.models import StoredProductInfo
from utils.price_parser import parse_price


class ProductCardComponent:
    """Scoped to a single .product-thumb locator, not the full page."""

    _NAME = "h4 a"
    _IMAGE = ".image img"
    _DESCRIPTION = ".caption > p:not(.price)"
    _PRICE = ".price"
    _ADD_TO_CART = "button[onclick*='cart.add']"

    def __init__(self, root: Locator, index: int) -> None:
        self.root = root
        self.index = index

    @property
    def name(self) -> str:
        return self.root.locator(self._NAME).inner_text().strip()

    @property
    def cleaned_name(self) -> str:
        return re.sub(r"\bipod\b", "", self.name, flags=re.IGNORECASE).strip()

    @property
    def picture_url(self) -> str:
        return self.root.locator(self._IMAGE).get_attribute("src") or ""

    @property
    def description(self) -> str:
        description = self.root.locator(self._DESCRIPTION).first.inner_text()
        return " ".join(description.split())

    @property
    def price(self) -> float | None:
        return parse_price(self.root.locator(self._PRICE).inner_text())

    def stored_info(self) -> StoredProductInfo:
        price = self.price
        if price is None:
            raise ValueError(f"Product price could not be parsed for {self.name!r}")
        return StoredProductInfo(
            name=self.cleaned_name,
            picture_url=self.picture_url,
            description=self.description,
            price=price,
        )

    def add_to_cart(self) -> None:
        self.root.locator(self._ADD_TO_CART).click()
