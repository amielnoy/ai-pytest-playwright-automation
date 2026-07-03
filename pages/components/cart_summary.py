from playwright.sync_api import Page, expect

from pages.components.base_component import BaseComponent
from utils.price_parser import parse_price


class CartSummaryComponent(BaseComponent):
    _TOTAL_LABEL = "Total:"
    _TOTAL_ROWS = "#content table tbody tr"
    _ITEMS = "#content .table-responsive table tbody tr"
    _CONTENT = "#content"
    _EMPTY_CART_TEXT = "Your shopping cart is empty!"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.total_rows = self._healed(
            self._TOTAL_ROWS, "cart total rows",
            ["#content table tr", ".table-responsive table tr"],
        )
        self.item_rows = self._healed(
            self._ITEMS, "cart item rows",
            ["#content table tbody tr", ".table-responsive tbody tr"],
        )
        self.content = self._healed(
            self._CONTENT, "cart content",
            ["main", "body"],
        )

    def get_total(self) -> float:
        total_cell = (
            self.total_rows.filter(has_text=self._TOTAL_LABEL)
            .locator("td")
            .last
        )
        if not total_cell.is_visible():
            return 0.0
        return parse_price(total_cell.inner_text()) or 0.0

    def get_item_count(self) -> int:
        return self.item_rows.count()

    def get_item_subtotals(self) -> list[float]:
        rows = self.item_rows.all()
        return [
            parse_price(row.locator("td:last-child").inner_text()) or 0.0
            for row in rows
        ]

    def is_empty(self) -> bool:
        return self.content.get_by_text(self._EMPTY_CART_TEXT).is_visible()

    def wait_for_item_count(self, count: int, timeout: int | None = None) -> None:
        """Wait until the cart table shows the expected number of line items."""
        kw = {} if timeout is None else {"timeout": timeout}
        expect(self.item_rows.resolved).to_have_count(count, **kw)
