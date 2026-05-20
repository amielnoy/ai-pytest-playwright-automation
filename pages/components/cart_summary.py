from playwright.sync_api import Page

from pages.components.base_component import BaseComponent
from pages.self_healing import healing_locator
from utils.price_parser import parse_price


class CartSummaryComponent(BaseComponent):
    _TOTAL_LABEL = "Total:"
    _TOTAL_ROWS = "#content table tbody tr"
    _ITEMS = "#content .table-responsive table tbody tr"
    _CONTENT = "#content"
    _EMPTY_CART_TEXT = "Your shopping cart is empty!"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.total_rows = healing_locator(
            page.locator(self._TOTAL_ROWS),
            name="cart total rows",
            primary_label=self._TOTAL_ROWS,
            fallbacks=[
                ("#content table tr", page.locator("#content table tr")),
                (".table-responsive table tr", page.locator(".table-responsive table tr")),
            ],
            events=self._self_heal_events,
        )
        self.item_rows = healing_locator(
            page.locator(self._ITEMS),
            name="cart item rows",
            primary_label=self._ITEMS,
            fallbacks=[
                ("#content table tbody tr", page.locator("#content table tbody tr")),
                (".table-responsive tbody tr", page.locator(".table-responsive tbody tr")),
            ],
            events=self._self_heal_events,
        )
        self.content = healing_locator(
            page.locator(self._CONTENT),
            name="cart content",
            primary_label=self._CONTENT,
            fallbacks=[
                ("main", page.locator("main")),
                ("body", page.locator("body")),
            ],
            events=self._self_heal_events,
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
