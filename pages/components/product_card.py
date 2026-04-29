import re

from playwright.sync_api import Locator

from pages.models import StoredProductInfo
from utils.price_parser import parse_price


class ProductCardComponent:
    """Scoped to a single li.s-item locator, not the full page."""

    _TITLE = "span[role='heading']"
    _PRICE = ".s-item__price"
    _IMAGE = ".s-item__image-img"

    def __init__(self, root: Locator, index: int) -> None:
        self.root = root
        self.index = index

    @property
    def name(self) -> str:
        return self.root.locator(self._TITLE).inner_text().strip()

    @property
    def cleaned_name(self) -> str:
        return re.sub(r"\bipod\b", "", self.name, flags=re.IGNORECASE).strip()

    @property
    def picture_url(self) -> str:
        img = self.root.locator(self._IMAGE)
        if img.count() == 0:
            return ""
        return img.get_attribute("src") or ""

    @property
    def description(self) -> str:
        return ""

    @property
    def price(self) -> float | None:
        price_el = self.root.locator(self._PRICE)
        if price_el.count() == 0:
            return None
        return parse_price(price_el.inner_text())

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
