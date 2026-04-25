import re
from playwright.sync_api import Page
from pages.base_page import BasePage


class CartPage(BasePage):
    _CART_TOTAL_ROW = "//strong[text()='Total:']/parent::td/following-sibling::td"
    _CART_ITEMS = "#content table tbody tr"
    _ITEM_NAME = "td.text-left a"
    _ITEM_PRICE = "td.text-right:last-child"
    _EMPTY_CART = "//p[contains(text(),'Your shopping cart is empty')]"
    _REMOVE_BTN = "//button[@data-original-title='Remove']"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self):
        self.navigate("index.php?route=checkout/cart")
        self.page.wait_for_load_state("networkidle")

    def get_cart_total(self) -> float:
        total_el = self.page.locator(self._CART_TOTAL_ROW).last
        raw = total_el.inner_text()
        return self._parse_price(raw)

    def is_empty(self) -> bool:
        return self.page.locator(self._EMPTY_CART).is_visible()

    def get_item_count(self) -> int:
        return self.page.locator(self._CART_ITEMS).count()

    def assert_total_not_exceeds(self, max_total: float) -> bool:
        total = self.get_cart_total()
        return total <= max_total

    @staticmethod
    def _parse_price(raw: str) -> float:
        numbers = re.findall(r"[\d,]+\.?\d*", raw.replace("$", ""))
        return float(numbers[0].replace(",", "")) if numbers else 0.0
