import re
from dataclasses import dataclass
from playwright.sync_api import Page
from pages.base_page import BasePage


@dataclass
class ProductInfo:
    name: str
    price: float
    index: int  # position in the result list (0-based)


class SearchResultsPage(BasePage):
    # Locators
    _PRODUCT_THUMBS = ".product-thumb"
    _PRODUCT_NAME = "h4 a"
    _PRODUCT_PRICE = ".price"
    _ADD_TO_CART_BTN = "//button[@onclick and contains(@onclick,'cart.add')]"
    _CART_SUCCESS_ALERT = ".alert-success"
    _NO_RESULTS = "//p[contains(text(),'There is no product that matches')]"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    # ------------------------------------------------------------------
    # Core: searchItemsByNameUnderPrice
    # Returns up to `limit` product names whose price <= max_price.
    # Mirrors the TypeScript signature from the exercise spec.
    # ------------------------------------------------------------------
    def search_items_by_name_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        self.navigate(f"index.php?route=product/search&search={query}")
        self.page.wait_for_load_state("networkidle")

        if self.page.locator(self._NO_RESULTS).is_visible():
            return []

        products = self._parse_products()
        filtered = [p for p in products if p.price <= max_price]
        return [p.name for p in filtered[:limit]]

    # ------------------------------------------------------------------
    # Returns full ProductInfo list filtered by price (used by cart tests)
    # ------------------------------------------------------------------
    def get_products_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[ProductInfo]:
        self.navigate(f"index.php?route=product/search&search={query}")
        self.page.wait_for_load_state("networkidle")

        if self.page.locator(self._NO_RESULTS).is_visible():
            return []

        products = self._parse_products()
        filtered = [p for p in products if p.price <= max_price]
        return filtered[:limit]

    # ------------------------------------------------------------------
    # Add items to cart by their product index on the results page.
    # Returns the list of names actually added.
    # ------------------------------------------------------------------
    def add_items_to_cart(self, products: list[ProductInfo]) -> list[str]:
        added = []
        thumbs = self.page.locator(self._PRODUCT_THUMBS)

        for product in products:
            thumb = thumbs.nth(product.index)
            add_btn = thumb.locator(self._ADD_TO_CART_BTN)
            add_btn.click()
            # Wait for success toast
            self.page.wait_for_selector(self._CART_SUCCESS_ALERT, timeout=8000)
            added.append(product.name)

        return added

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _parse_products(self) -> list[ProductInfo]:
        thumbs = self.page.locator(self._PRODUCT_THUMBS)
        count = thumbs.count()
        result: list[ProductInfo] = []

        for i in range(count):
            thumb = thumbs.nth(i)
            name = thumb.locator(self._PRODUCT_NAME).inner_text().strip()
            raw_price = thumb.locator(self._PRODUCT_PRICE).inner_text()
            price = self._extract_price(raw_price)
            if price is not None:
                result.append(ProductInfo(name=name, price=price, index=i))

        return result

    @staticmethod
    def _extract_price(raw: str) -> float | None:
        # Handle "Ex Tax:" lines — take the first dollar amount
        numbers = re.findall(r"\$[\d,]+\.?\d*", raw)
        if not numbers:
            return None
        # Strip $ and commas, convert to float
        return float(numbers[0].replace("$", "").replace(",", ""))
