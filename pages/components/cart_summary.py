from pages.components.base_component import BaseComponent
from utils.price_parser import parse_price


class CartSummaryComponent(BaseComponent):
    _TOTAL_ROW = "tfoot tr:has(strong:has-text('Total:')) td:last-child"
    _ITEMS = "#content table tbody tr"
    _CONTENT = "#content"
    _EMPTY_CART_TEXT = "Your shopping cart is empty!"

    def get_total(self) -> float:
        total_cell = self.page.locator(self._TOTAL_ROW).last
        if not total_cell.is_visible():
            return 0.0
        return parse_price(total_cell.inner_text()) or 0.0

    def get_item_count(self) -> int:
        return self.page.locator(self._ITEMS).count()

    def get_item_subtotals(self) -> list[float]:
        rows = self.page.locator(self._ITEMS).all()
        return [
            parse_price(row.locator("td:last-child").inner_text()) or 0.0
            for row in rows
        ]

    def is_empty(self) -> bool:
        return self.page.locator(self._CONTENT).get_by_text(
            self._EMPTY_CART_TEXT
        ).is_visible()
