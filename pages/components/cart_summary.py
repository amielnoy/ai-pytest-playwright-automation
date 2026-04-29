from pages.components.base_component import BaseComponent
from utils.price_parser import parse_price


class CartSummaryComponent(BaseComponent):
    _TOTAL_ROW = "//strong[text()='Total:']/parent::td/following-sibling::td"
    _ITEMS = "#content table tbody tr"
    _EMPTY = "//p[contains(text(),'Your shopping cart is empty')]"

    def get_total(self) -> float:
        total_cell = self.page.locator(self._TOTAL_ROW).last
        if not total_cell.is_visible():
            return 0.0
        return parse_price(total_cell.inner_text()) or 0.0

    def get_item_count(self) -> int:
        return self.page.locator(self._ITEMS).count()

    def is_empty(self) -> bool:
        return self.page.locator(self._EMPTY).is_visible()
