import re

from playwright.sync_api import Locator

from pages.models import StoredProductInfo
from pages.self_healing import healing_locator
from utils.price_parser import parse_price


class ProductCardComponent:
    """Scoped to a single .product-thumb locator, not the full page."""

    _NAME_HEADING_ROLE = "heading"
    _NAME_HEADING_LEVEL = 4
    _NAME_LINK_ROLE = "link"
    _IMAGE_ROLE = "img"
    _IMAGE_SRC_ATTRIBUTE = "src"
    # Product card text nodes have no stable ARIA labels, so these remain scoped CSS.
    _DESCRIPTION = ".caption > p:not(.price)"
    _PRICE = ".price"
    _ADD_TO_CART_BUTTON_ROLE = "button"
    _ADD_TO_CART_BUTTON_NAME = "Add to Cart"

    def __init__(self, root: Locator, index: int) -> None:
        self.root = root
        self.index = index
        self.name_heading = root.get_by_role(
            self._NAME_HEADING_ROLE, level=self._NAME_HEADING_LEVEL
        )
        self.name_link = self.name_heading.get_by_role(self._NAME_LINK_ROLE)
        self.image = root.get_by_role(self._IMAGE_ROLE)
        self.description_text = healing_locator(
            root.locator(self._DESCRIPTION),
            name=f"product card {index} description",
            primary_label=self._DESCRIPTION,
            fallbacks=[
                (".caption p", root.locator(".caption p")),
                ("p", root.locator("p")),
            ],
        ).first
        self.price_text = healing_locator(
            root.locator(self._PRICE),
            name=f"product card {index} price",
            primary_label=self._PRICE,
            fallbacks=[
                ("[class*='price']", root.locator("[class*='price']")),
                (".caption", root.locator(".caption")),
            ],
        )
        self.add_to_cart_button = root.get_by_role(
            self._ADD_TO_CART_BUTTON_ROLE, name=self._ADD_TO_CART_BUTTON_NAME
        )

    @property
    def name(self) -> str:
        return self.name_link.inner_text().strip()

    @property
    def cleaned_name(self) -> str:
        return re.sub(r"\bipod\b", "", self.name, flags=re.IGNORECASE).strip()

    @property
    def picture_url(self) -> str:
        return self.image.get_attribute(self._IMAGE_SRC_ATTRIBUTE) or ""

    @property
    def description(self) -> str:
        description = self.description_text.inner_text()
        return " ".join(description.split())

    @property
    def price(self) -> float | None:
        return parse_price(self.price_text.inner_text())

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
        self.add_to_cart_button.click()
